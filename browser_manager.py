import sys
import selenium
import requests
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import os
from enum import Enum
import threading
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

import time as t
from utils import *
import platform
import subprocess


'''Locating by xpath here is the best thing to do here, since google Meet changes selectors, classes name and all that sort of stuff for every meeting
    XPaths remaing the same, but a slight change by them would make this program fail.
    The xpath is found clicking by inspecting the element of the searched button, and finding the parent div tthat has role="button" tag
'''

MIC_XPATH = '/html/body/div[1]/c-wiz/div/div/div[8]/div[3]/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[3]/div[1]/div/div/div'
WEBCAM_XPATH = '/html/body/div[1]/c-wiz/div/div/div[8]/div[3]/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[3]/div[2]/div/div'
JOIN_XPATH = '/html/body/div[1]/c-wiz/div/div/div[8]/div[3]/div/div/div[2]/div/div[1]/div[2]/div/div[2]/div/div/div[1]'
OPTION_XPATH = '/html/body/div[1]/c-wiz/div/div/div[6]/div[3]/div/div/div[2]/div/div[1]/div[1]/div[1]/div/div[4]/div'

CHAT_BTN_XPATH = '/html/body/div[1]/c-wiz/div[1]/div/div[6]/div[3]/div[6]/div[3]/div/div[2]/div[3]'
CHAT_SELECTCHAT_BTN_XPATH = '/html/body/div[1]/c-wiz/div[1]/div/div[6]/div[3]/div[3]/div/div[2]/div[2]/div[1]/div[2]'

#Using tagname for text area because xpath doesn't really work, and we're sure it's the only textarea on the webpage
CHAT_TEXT_XPATH = "textarea"

HANG_UP_BTN_XPATH = '/html/body/div[1]/c-wiz/div[1]/div/div[8]/div[3]/div[9]/div[2]/div[2]/div'

CHAT_CLOSE_BTN_XPATH = '/html/body/div[1]/c-wiz/div[1]/div/div[6]/div[3]/div[3]/div/div[2]/div[1]/div[2]/div/button'

# Set Chrome profile path dynamically in the app's root directory
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
CHROME_PROFILE_PATH = os.path.join(APP_ROOT, 'recoai-chrome-profile')
CHROME_PROFILE_DIRECTORY = 'Default'

browser = None

def initFirefox():
    global browser

    browser = webdriver.Firefox(firefox_profile=webdriver.FirefoxProfile(FIREFOX_PROFILE), executable_path=FIREFOX_DVD_DIR)

def kill_all_chrome():
    try:
        subprocess.run(['pkill', '-f', 'chrome'], check=False)
    except Exception:
        pass

def initChrome():
    # Kill all existing Chrome processes before starting a new session
    kill_all_chrome()
    global browser
    import undetected_chromedriver as uc
    from selenium.webdriver.chrome.options import Options
    chrome_options = Options()
    # Ensure the Chrome profile directory exists
    if not os.path.exists(CHROME_PROFILE_PATH):
        os.makedirs(CHROME_PROFILE_PATH)
        print(f"[DEBUG] Created Chrome profile directory at: {CHROME_PROFILE_PATH}", flush=True)
    else:
        print(f"[DEBUG] Using existing Chrome profile at: {CHROME_PROFILE_PATH}", flush=True)
    # IMPORTANT: Make sure all Chrome windows are closed before running the bot
    chrome_options.add_argument(f"--user-data-dir={CHROME_PROFILE_PATH}")
    chrome_options.add_argument(f"--profile-directory={CHROME_PROFILE_DIRECTORY}")
    chrome_options.add_argument("--disable-notifications")
    chrome_options.add_argument("--use-fake-ui-for-media-stream")
    chrome_options.add_argument("--use-fake-device-for-media-stream")
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "profile.default_content_setting_values.media_stream_mic": 1,
        "profile.default_content_setting_values.media_stream_camera": 1,
        "profile.default_content_setting_values.geolocation": 2
    })
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    browser = uc.Chrome(options=chrome_options)

def joinMeeting(link):
    global browser

    if link == '':
        return

    try:
        browser.get(link)
        print("Trying to join meeting")
        # Wait for the pre-join screen to be ready (join button or mic/camera controls)
        try:
            WebDriverWait(browser, 15).until(
                EC.presence_of_element_located((By.XPATH, "//button[descendant-or-self::*[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = 'join now' or translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = 'ask to join']] | //span[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = 'join now' or translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = 'ask to join']/ancestor::button | //button[@aria-label='Turn off microphone'] | //button[@aria-label='Turn off camera']"))
            )
            print("Pre-join screen detected, sending keyboard shortcuts.")
        except Exception as e:
            print("Pre-join screen not detected in time:", e)
        # Dismiss any popups/notifications
        try:
            allow_btn = WebDriverWait(browser, 2).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Allow microphone and camera')]"))
            )
            allow_btn.click()
            t.sleep(0.5)
        except Exception:
            pass
        try:
            dismiss_btn = WebDriverWait(browser, 1).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Dismiss')]"))
            )
            dismiss_btn.click()
            t.sleep(0.5)
        except Exception:
            pass
        # Only use keyboard shortcuts for muting mic and camera
        try:
            from selenium.webdriver.common.keys import Keys
            body = browser.find_element(By.TAG_NAME, 'body')
            if platform.system() == 'Darwin':
                body.send_keys(Keys.COMMAND, 'd')
                print("Sent Command+D to mute mic.")
                body.send_keys(Keys.COMMAND, 'e')
                print("Sent Command+E to turn off camera.")
            else:
                body.send_keys(Keys.CONTROL, 'd')
                print("Sent Ctrl+D to mute mic.")
                body.send_keys(Keys.CONTROL, 'e')
                print("Sent Ctrl+E to turn off camera.")
        except Exception as e:
            print("Failed to send keyboard shortcuts for mic/camera:", e)
        # Click 'Join now' or 'Ask to join' button using robust selector (case-insensitive)
        try:
            join_btn = WebDriverWait(browser, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[descendant-or-self::*[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = 'join now' or translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = 'ask to join']] | //span[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = 'join now' or translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = 'ask to join']/ancestor::button"))
            )
            btn_text = join_btn.text.strip().lower()
            print(f"[DEBUG] Join button text: '{btn_text}'", flush=True)
            join_btn.click()
            print("Clicked join button.", flush=True)
            t.sleep(5)  # Give the page a moment to update
            print("[DEBUG] Checking for 'Ask to join' or 'Join now' button after click...", flush=True)
            ask_to_join_present = False
            join_now_present = False
            try:
                browser.find_element(By.XPATH, "//button[descendant-or-self::*[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = 'ask to join']]")
                ask_to_join_present = True
            except Exception:
                pass
            try:
                browser.find_element(By.XPATH, "//button[descendant-or-self::*[translate(text(), 'ABCDEFGHIJKLMNOPQRSTUVWXYZ', 'abcdefghijklmnopqrstuvwxyz') = 'join now']]")
                join_now_present = True
            except Exception:
                pass

            try:
                from app import join_status
                if ask_to_join_present or join_now_present:
                    join_status['status'] = 'Waiting for host to admit you...'
                    print("[LOG] Status set to: Waiting for host to admit you... (button still present)", flush=True)
                else:
                    print("[DEBUG] 'Ask to join' and 'Join now' buttons not found, checking for waiting message...", flush=True)
                    try:
                        waiting_msg = browser.find_element(By.XPATH, "//*[contains(text(), 'You’ll join the call when someone lets you in') or contains(text(), 'You’ll join the call when someone admits you') or contains(text(), 'Waiting for host') or contains(text(), 'waiting to join')]")
                        join_status['status'] = 'Waiting for host to admit you...'
                        print("[LOG] Status set to: Waiting for host to admit you... (waiting message present)", flush=True)
                    except Exception:
                        print("[DEBUG] No waiting message found, assuming joining...", flush=True)
                        join_status['status'] = 'Joining meeting...'
                        print("[LOG] Status set to: Joining meeting...", flush=True)
            except Exception as e:
                print("Could not update join_status:", e, flush=True)
        except Exception as e:
            print("Could not find or click join button:", e)
    except Exception as e:
        print("Failed to join meeting, trying again in 60 secs", e)
        t.sleep(60)
        joinMeeting(link)


def clickButton(by, selector):
    global browser
    WebDriverWait(browser, 5).until(EC.element_to_be_clickable((by, selector))).click()
    t.sleep(1)

def writeText(by, selector, text):
    WebDriverWait(browser, 5).until(EC.element_to_be_clickable((by, selector))).clear()
    WebDriverWait(browser, 5).until(EC.element_to_be_clickable((by, selector))).send_keys(text + "\n")

def sendChatMsg(text):
    global browser

    #open chat menu
    clickButton(By.XPATH, CHAT_BTN_XPATH)
    #select chat option
    clickButton(By.XPATH, CHAT_SELECTCHAT_BTN_XPATH)
    #write msg
    writeText(By.TAG_NAME, CHAT_BTN_XPATH, text)
    t.sleep(1)
    #close chat
    clickButton(By.XPATH, CHAT_CLOSE_BTN_XPATH)


def checkStarted():
    try:
        clickButton(By.XPATH, OPTION_XPATH)
    except:
        return False
    return True

def hangUpMeeting():
    try:
        clickButton(By.XPATH, HANG_UP_BTN_XPATH)
    except:
        return False
    return True
