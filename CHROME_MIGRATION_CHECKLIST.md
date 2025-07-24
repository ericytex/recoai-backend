# Chrome Migration Functional Integration Checklist

This checklist tracks the steps to integrate the backend join meeting API with the Start AI-Powered Recording button in the Next.js Dashboard.

- [ ] 1. Locate the Start AI-Powered Recording button and its handler in JoinMeetingForm.tsx
- [ ] 2. Replace the simulated join/recording logic with a real API call to /join
- [ ] 3. Handle API responses and update UI status (joining, waiting, recording, error)
- [ ] 4. Poll /status for updates and reflect them in the UI (spinner, status, etc.)
- [ ] 5. (Optional) Add a disconnect/stop button to call /disconnect and update UI

# Chrome Migration Checklist

This checklist tracks the minimal changes required to migrate GoogleMeetBot from Firefox to Chrome using Selenium and ChromeDriver. Each step should be tested and checked off upon completion.

- [x] ✅ 1. Install Chrome and ChromeDriver
    - Ensure Google Chrome is installed on your system.
    - Download and install the appropriate ChromeDriver for your OS.
    - Add ChromeDriver to your system PATH or note its location.

- [x] ✅ 2. Update `requirements.txt` (if needed)
    - Confirm that the current Selenium version supports Chrome.

- [x] ✅ 3. Add Chrome profile setup instructions
    - Document how to create and use a Chrome profile for Google login (similar to the Firefox profile method).

- [x] ✅ 4. Update `utils.py`
    - Add variables for ChromeDriver path and Chrome profile directory.

- [x] ✅ 5. Update `browser_manager.py`
    - Add a function to initialize the Chrome browser using the specified profile and driver.
    - Allow switching between Firefox and Chrome (or replace Firefox with Chrome if preferred).
    - Ensure all Selenium commands work with Chrome.

- [x] ✅ 6. Test Google login with Chrome profile
    - Verify that the bot can launch Chrome with the profile and is logged into Google.

- [x] ✅ 7. **Simulate SaaS flow: User signs in once with their Chrome profile, then enters a meeting link to join a Google Meet.**
    - Ensure the user can authenticate once, then join any meeting link on demand.
    - Only after successful join, implement scheduling for future meetings.

- [x] ✅ 8. Test meeting join, mute, and camera off functionality in Chrome
    - Confirm that the bot can join a meeting, mute the mic, and turn off the camera using Chrome.

- [x] ✅ 9. Headless/hidden automation and UI recording indicator
    - Ensure the meeting join process is hidden (headless Chrome).
    - Show a blinking red dot and recording message in the UI while joining.

- [x] ✅ 10. Separate UI from API (frontend in its own directory)
    - Move the HTML/JS UI to a standalone file outside the Flask app.
    - Ensure the API can be called independently from any client.

- [x] ✅ 11. Accurate admission/waiting detection and status reporting
    - Detect and report when the bot is waiting for host admission, is admitted, or is denied.
    - Only report failure after a real timeout or explicit rejection.

- [ ] 12. **Integrate and support Next.js frontend (@frontend/recoaiui-2)**
    - Watch for changes in the Next.js app directory.
    - Update API parameters and integration as needed for the new frontend.
    - [ ] Integrate backend join meeting API with Start AI-Powered Recording button in Dashboard
    - [ ] Poll /status and update UI accordingly
    - [ ] Add disconnect/stop button for meeting

- [ ] 13. Test chat and hang up features in Chrome
    - Ensure chat and hang up actions work as expected in Chrome.

- [ ] 14. Update documentation
    - Add Chrome-specific setup and usage instructions to the README.
    - Document the SaaS flow for user sign-in and meeting join.

- [ ] 15. Final review and cleanup
    - Remove any unused Firefox-specific code if fully switching to Chrome.
    - Ensure all features work as expected in Chrome. 