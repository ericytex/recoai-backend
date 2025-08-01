import time as t
import schedule
import browser_manager

def setup_schedule():
    # Step 1: Open Chrome for Gmail sign-in
    print("Chrome will open. Please sign in to your Gmail account if not already signed in.")
    browser_manager.initChrome()
    input("\nOnce you are signed in to Gmail, press Enter here to continue and join the meeting...")
    # Step 2: Join the test Google Meet link
    browser_manager.joinMeeting("https://meet.google.com/oyx-oocy-xnc")


def scheduleMeeting(day, startHour, endHour, link):
    if str(day).lower() == "monday":
        schedule.every().monday.at(startHour).do(browser_manager.joinMeeting, link)
        schedule.every().monday.at(endHour).do(browser_manager.hangUpMeeting)
    elif str(day).lower() == "tuesday":
        schedule.every().tuesday.at(startHour).do(browser_manager.joinMeeting, link)
        schedule.every().tuesday.at(endHour).do(browser_manager.hangUpMeeting)
    elif str(day).lower() == "wednesday":
        schedule.every().wednesday.at(startHour).do(browser_manager.joinMeeting, link)
        schedule.every().wednesday.at(endHour).do(browser_manager.hangUpMeeting)
    elif str(day).lower() == "thursday":
        schedule.every().thursday.at(startHour).do(browser_manager.joinMeeting, link)
        schedule.every().thursday.at(endHour).do(browser_manager.hangUpMeeting)
    elif str(day).lower() == "friday":
        schedule.every().friday.at(startHour).do(browser_manager.joinMeeting, link)
        schedule.every().friday.at(endHour).do(browser_manager.hangUpMeeting)
    elif str(day).lower() == "saturday":
        schedule.every().saturday.at(startHour).do(browser_manager.joinMeeting, link)
        schedule.every().saturday.at(endHour).do(browser_manager.hangUpMeeting)
    elif str(day).lower() == "sunday":
        schedule.every().sunday.at(startHour).do(browser_manager.joinMeeting, link)
        schedule.every().sunday.at(endHour).do(browser_manager.hangUpMeeting)
    elif str(day).lower() == "today":
        schedule.every().day.at(startHour).do(browser_manager.joinMeeting, link)
        schedule.every().day.at(endHour).do(browser_manager.hangUpMeeting)
