import os
FIREFOX_DVD_DIR = '/usr/bin/geckodriver'
FIREFOX_PROFILE = '/home/emamaker/.mozilla/firefox/iuwsro4q.automation'
CHROME_DRIVER_PATH = '/opt/homebrew/bin/chromedriver'  # Update if your chromedriver is elsewhere
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
CHROME_PROFILE_PATH = os.path.join(APP_ROOT, 'recoai-chrome-profile')
CHROME_PROFILE_DIRECTORY = 'Default'