from flask import Flask, render_template_string, request, jsonify
import threading
import browser_manager
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app, origins="*", supports_credentials=True, allow_headers=["Content-Type"], methods=["GET", "POST", "OPTIONS"])

join_status = {'status': ''}
def join_meeting_and_wait(link):
    import browser_manager
    import time
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException
    
    # Initialize browser and join meeting
    browser_manager.initChrome()
    browser_manager.joinMeeting(link)
    browser = browser_manager.browser
    
    def check_for_admission_denied():
        """Check if admission was denied by host"""
        try:
            denial_messages = [
                "You can't join this call",
                "Someone in the call denied your request",
                "Your request to join was denied",
                "The host has denied your request"
            ]
            for message in denial_messages:
                try:
                    # Use single quotes for Python string, double quotes inside XPath
                    element = browser.find_element(By.XPATH, f'//*[contains(text(), "{message}")]')
                    if element:
                        print(f"[LOG] Admission denied. Message: '{element.text}'", flush=True)
                        return True
                except NoSuchElementException:
                    continue
            return False
        except Exception as e:
            print(f"[DEBUG] Error checking for denial: {e}", flush=True)
            return False
    
    def check_successfully_joined():
        """Check if successfully joined the meeting"""
        try:
            leave_button = browser.find_element(By.XPATH, "//button[@aria-label='Leave call']")
            return leave_button is not None
        except NoSuchElementException:
            return False
        except Exception as e:
            print(f"[DEBUG] Error checking join status: {e}", flush=True)
            return False
    
    def check_waiting_for_admission():
        """Check if waiting for host admission"""
        waiting_indicators = [
            "You'll join the call when someone lets you in",
            "You'll join the call when someone admits you", 
            "Waiting for host",
            "waiting to join",
            "Waiting for the meeting host"
        ]
        
        # Check for waiting messages
        for indicator in waiting_indicators:
            try:
                # Use single quotes for Python string, double quotes inside XPath
                element = browser.find_element(By.XPATH, f'//*[contains(text(), "{indicator}")]')
                if element:
                    return True
            except NoSuchElementException:
                continue
        
        # Check if "Ask to join" button is no longer present (indicating request was sent)
        try:
            browser.find_element(By.XPATH, "//button[descendant-or-self::*[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = 'ask to join']]")
            return False  # Button still present, not waiting yet
        except NoSuchElementException:
            return True  # Button gone, likely waiting for admission
    
    def monitor_meeting_presence():
        from selenium.common.exceptions import NoSuchElementException, WebDriverException, SessionNotCreatedException
        while True:
            try:
                # Check for the presence of the 'Leave call' button
                browser.find_element(By.XPATH, "//button[@aria-label='Leave call']")
                time.sleep(2)  # Check every 2 seconds
            except (NoSuchElementException, WebDriverException, SessionNotCreatedException) as e:
                join_status['status'] = 'disconnected'
                print("[LOG] Bot has disconnected from the meeting.", flush=True)
                print(f"[DEBUG] monitor_meeting_presence exception: {e}", flush=True)
                cleanup_browser()
                break
            except Exception as e:
                join_status['status'] = 'disconnected'
                print("[LOG] Bot has disconnected from the meeting (unexpected error).", flush=True)
                print(f"[DEBUG] monitor_meeting_presence unexpected exception: {e}", flush=True)
                cleanup_browser()
                break
    
    def cleanup_browser():
        try:
            browser.quit()
        except Exception:
            pass
        try:
            import browser_manager
            browser_manager.browser = None
        except Exception:
            pass

    try:
        # Step 1: Check for immediate join (no admission required)
        join_status['status'] = 'Checking meeting access...'
        print("[LOG] Checking meeting access...", flush=True)

        try:
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, "//button[@aria-label='Leave call']"))
            )
            join_status['status'] = 'success: Bot has joined the meeting and is recording...'
            print("[LOG] Bot successfully joined the meeting immediately!", flush=True)
            # Start monitoring for removal from meeting
            threading.Thread(target=monitor_meeting_presence, daemon=True).start()
            return
        except TimeoutException:
            print("[LOG] Pre-join screen not detected in time. Meeting may not have started yet.", flush=True)
            join_status['status'] = 'Meeting has not started yet. Waiting for host...'
            # Enter polling loop to check for admission or denial
            timeout = time.time() + 600  # 10 minutes
            while time.time() < timeout:
                if check_successfully_joined():
                    join_status['status'] = 'success: Bot has joined the meeting and is recording...'
                    print("[LOG] Bot has been admitted and joined the meeting!", flush=True)
                    return
                if check_for_admission_denied():
                    join_status['status'] = 'Failed to join: Admission denied by host.'
                    return
                time.sleep(2)
            join_status['status'] = 'Failed to join: Timed out waiting for host admission.'
            print("[LOG] Bot timed out waiting for host admission.", flush=True)
            return
        
        # Step 2: Check if admission was already denied
        if check_for_admission_denied():
            join_status['status'] = 'Failed to join: Admission denied by host.'
            return
        
        # Step 3: Check if waiting for admission
        if check_waiting_for_admission():
            join_status['status'] = 'Waiting for host to admit you...'
            print("[LOG] Bot is waiting for host admission...", flush=True)
            
            # Wait up to 10 more minutes for 'Leave call' (admitted) or denial message (rejected)
            timeout = time.time() + 600  # 10 minutes
            
            while time.time() < timeout:
                # Check if successfully admitted
                if check_successfully_joined():
                    join_status['status'] = 'success: Bot has joined the meeting and is recording...'
                    print("[LOG] Bot has been admitted and joined the meeting!", flush=True)
                    return
                
                # Check if admission was denied
                if check_for_admission_denied():
                    join_status['status'] = 'Failed to join: Admission denied by host.'
                    return
                
                # Wait before next check
                time.sleep(2)
            
            # Timeout waiting for admission
            join_status['status'] = 'Failed to join: Timed out waiting for host admission.'
            print("[LOG] Bot timed out waiting for host admission.", flush=True)
            return
        
        # Step 4: Unknown state - couldn't determine meeting status
        join_status['status'] = 'Failed to join: Unable to determine meeting status.'
        print("[LOG] Unable to determine meeting join status.", flush=True)
        
    except (WebDriverException, SessionNotCreatedException) as e:
        print(f"[LOG] Browser session error: {e}", flush=True)
        cleanup_browser()
        join_status['status'] = 'Browser crashed. Please try again.'
    except Exception as e:
        join_status['status'] = f'Failed to join: Unexpected error - {str(e)}'
        print(f"[LOG] Unexpected error during meeting join: {e}", flush=True)

def disconnect_meeting():
    import browser_manager
    try:
        browser_manager.hangUpMeeting()
        if browser_manager.browser:
            browser_manager.browser.quit()
        join_status['status'] = 'Disconnected from meeting.'
        print("[LOG] Bot has disconnected from the meeting.", flush=True)
    except Exception as e:
        join_status['status'] = 'Failed to disconnect.'
        print(f"[LOG] Bot failed to disconnect: {e}", flush=True)

@app.route('/')
def index():
    return render_template_string(HTML)

@app.route('/join', methods=['POST', 'OPTIONS'])
def join():
    if request.method == 'OPTIONS':
        # CORS preflight
        return '', 204
    data = request.get_json()
    link = data.get('link')
    if not link or not link.startswith('https://meet.google.com/'):
        join_status['status'] = 'Invalid Google Meet link.'
        return jsonify({'status': join_status['status']})
    join_status['status'] = 'Joining meeting...'
    def run_and_respond():
        join_meeting_and_wait(link)
    threading.Thread(target=run_and_respond).start()
    return jsonify({'status': join_status['status']})

@app.route('/status')
def status():
    print(f"[DEBUG] /status called, returning: {join_status['status']}", flush=True)
    return jsonify({'status': join_status['status']})

@app.route('/disconnect', methods=['POST'])
def disconnect():
    threading.Thread(target=disconnect_meeting).start()
    return jsonify({'status': 'Disconnecting...'})

HTML = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Google Meet Bot SaaS Simulation</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        .container { max-width: 400px; margin: auto; }
        .btn { background: #4285F4; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; }
        .btn:disabled { background: #aaa; }
        input[type=text] { width: 100%; padding: 8px; margin: 10px 0; }
        .recording {
            display: flex;
            align-items: center;
            margin-top: 10px;
        }
        .dot {
            height: 12px;
            width: 12px;
            margin-right: 8px;
            background-color: red;
            border-radius: 50%;
            display: inline-block;
            animation: blink 1s infinite;
        }
        @keyframes blink {
            0% { opacity: 1; }
            50% { opacity: 0; }
            100% { opacity: 1; }
        }
        .disconnect-btn { background: #d32f2f; margin-top: 16px; }
    </style>
</head>
<body>
<div class="container">
    <h2>Sign in with Google (Simulation)</h2>
    <form onsubmit="event.preventDefault(); joinMeet();">
        <label for="meet-link"><b>Enter Google Meet Link</b></label>
        <input type="text" id="meet-link" placeholder="https://meet.google.com/xxxx-xxxx-xxx" />
        <button class="btn" id="join-btn" type="submit">Join Meeting</button>
    </form>
    <div id="status"></div>
    <button class="btn disconnect-btn" id="disconnect-btn" style="display:none;" onclick="disconnectMeet()">Disconnect</button>
</div>
<script>
let polling = false;
function joinMeet() {
    var link = document.getElementById('meet-link').value;
    document.getElementById('status').innerText = 'Joining meeting...';
    fetch('/join', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ link: link })
    }).then(r => r.json()).then(data => {
        document.getElementById('status').innerText = data.status;
        if (!polling) {
            polling = true;
            pollStatus();
        }
    });
}
function pollStatus() {
    fetch('/status').then(r => r.json()).then(data => {
        if (data.status && data.status.toLowerCase().includes('success')) {
            document.getElementById('status').innerHTML = '<div class="recording"><span class="dot"></span>Meeting is being recorded...</div>';
            document.getElementById('disconnect-btn').style.display = 'inline-block';
            polling = false;
        } else if (data.status && data.status.toLowerCase().includes('disconnected')) {
            document.getElementById('status').innerText = data.status;
            document.getElementById('disconnect-btn').style.display = 'none';
            polling = false;
        } else {
            document.getElementById('status').innerText = data.status;
            setTimeout(pollStatus, 2000);
        }
    });
}
function disconnectMeet() {
    document.getElementById('status').innerText = 'Disconnecting...';
    fetch('/disconnect', { method: 'POST' })
        .then(r => r.json())
        .then(data => {
            document.getElementById('status').innerText = data.status;
            document.getElementById('disconnect-btn').style.display = 'none';
            polling = true;
            pollStatus();
        });
}
</script>
</body>
</html>
'''

if __name__ == '__main__':
    app.run(port=5004, debug=True) 