# Chrome Profile Setup for GoogleMeetBot

To allow GoogleMeetBot to log in to your Google account using Chrome, follow these steps to create and configure a dedicated Chrome profile:

## 1. Create a New Chrome Profile
1. Open Google Chrome.
2. Click your profile icon in the top right corner.
3. Click "Add" or "Add another profile".
4. Choose a name and icon for the new profile (e.g., "GMeetBot").
5. Click "Done". A new Chrome window will open with this profile.

## 2. Log In to Your Google Account
1. In the new Chrome window, go to [https://accounts.google.com/](https://accounts.google.com/).
2. Log in with the Google account you want the bot to use.

## 3. Find the Profile Path
1. In the Chrome window for your new profile, go to `chrome://version/`.
2. Look for the "Profile Path" entry (e.g., `/Users/yourname/Library/Application Support/Google/Chrome/Profile 2`).
3. Copy this path; you will need it for the bot configuration.

## 4. (Optional) Set Up ChromeDriver Permissions
If you encounter security prompts from macOS, follow the instructions in the Privacy & Security settings to allow ChromeDriver to run.

---

You will use the profile path in the bot's configuration to ensure Selenium launches Chrome with your logged-in session. 