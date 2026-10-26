# Seven RPG Browser Playtest Scope

Automated end-to-end browser checks are executed in Chromium against the actual served `web/` application using Playwright.

Coverage:
- campaign creation, required fields, character class and difficulty selection
- local save persistence and restore after reload
- successful AI-shaped request, accepted narrative event and persistence
- AI HTTP errors, missing key, empty action and unexpected response shape
- endpoint validation and verification that API credentials are not stored in localStorage
- valid save import, malformed and structurally incomplete save rejection
- JSON export download and new-world cancellation
- phone viewport width and Arabic RTL layout
- storage-quota failure rollback

Provider responses are mocked in automated tests. A live provider test requires a user-owned API key and must be run by entering it locally in the browser; the key must not be committed or shared in test output.
