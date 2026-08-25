# VWO Login Page — Test Cases

Repository: https://github.com/Debarati93/AITesterBluePrint4x
File: chapter_01_LLM_Basics/VWO_Login_Test_Cases.md

Last updated: 2026-08-24

Purpose
-------
Structured test cases for the VWO application login page (https://app.vwo.com/#/login). The document covers functional, negative, security, accessibility, performance and cross-browser test cases suitable for manual execution and as a basis for automation.

Scope
-----
- Tests target the login page and immediate authentication flow only (not application features beyond successful login).
- Includes UI elements, input validation, session behavior, security checks relevant to login, accessibility and performance checks.

Test Environment
----------------
- Browsers: Chrome (latest), Firefox (latest), Edge (latest), Safari (latest)
- Devices: Desktop 1366x768, Desktop 1920x1080, Mobile viewport (iPhone/Android)
- Network: Normal (unthrottled) and throttled (3G) for performance checks
- Test accounts: Provide at least one valid test user with known credentials and one locked/disabled account if available
- Automation: Selenium, Playwright or Cypress (automation notes included per case)

Prerequisites
-------------
1. Test user credentials available (username/email and password).
2. Application reachable at https://app.vwo.com/#/login.
3. Test accounts are in a known state (not locked, password known).
4. Browser cache cleared or use a fresh profile for reproducible behavior.

Test Case Key
-------------
- ID: Unique test ID (VWO-LGN-###)
- Type: Functional / Negative / Security / Accessibility / Performance
- Priority: P0 (critical), P1 (high), P2 (medium), P3 (low)
- Automation: Feasibility and notes

Test Cases
----------
1) VWO-LGN-001 — Page Load and Elements Present
- Type: Functional
- Priority: P0
- Steps:
  1. Navigate to https://app.vwo.com/#/login
- Expected:
  - Page loads successfully (HTTP 200)
  - Visible elements: email/username field, password field, "Log in" button, "Forgot password" link, "Remember me" checkbox (if present), social/SSO buttons (if present), logo
- Automation: Yes — assert element visibility and HTTP status.

2) VWO-LGN-002 — Successful Login (valid credentials)
- Type: Functional
- Priority: P0
- Steps:
  1. Enter valid email and password
  2. Click "Log in"
- Expected:
  - User is authenticated and redirected to the application dashboard (URL change, dashboard elements visible)
  - Session cookie (secure, HttpOnly) set
- Automation: Yes — assert URL, key dashboard elements, cookies.

3) VWO-LGN-003 — Unsuccessful Login (invalid password)
- Type: Negative
- Priority: P0
- Steps:
  1. Enter valid email and wrong password
  2. Click "Log in"
- Expected:
  - Login rejected with appropriate error message (e.g., "Invalid username or password")
  - No session cookie set
  - Error message is accessible (role=alert) and not revealing sensitive information
- Automation: Yes — assert presence of error text and lack of session cookie.

4) VWO-LGN-004 — Unsuccessful Login (non-existent user)
- Type: Negative
- Priority: P1
- Steps:
  1. Enter random/non-registered email
  2. Enter any password, click "Log in"
- Expected:
  - Generic authentication error shown (do not reveal whether account exists)
- Automation: Yes

5) VWO-LGN-005 — Input Validation: Email Format
- Type: Negative / Security
- Priority: P1
- Steps:
  1. Enter invalid email formats (e.g., "user", "user@", "@domain") and a password
  2. Click "Log in"
- Expected:
  - Client-side validation prevents submission or shows a clear validation message
  - Server-side handles invalid input gracefully
- Automation: Yes

6) VWO-LGN-006 — Password Field Masking and Toggle
- Type: Functional / Accessibility
- Priority: P1
- Steps:
  1. Inspect password input: ensure characters are masked (type=password)
  2. If a "show password" control exists, click it and verify password becomes visible and toggles back
- Expected:
  - Masking by default; toggle works and is keyboard accessible
- Automation: Partially (check attribute and toggle action if present)

7) VWO-LGN-007 — Remember Me Functionality
- Type: Functional
- Priority: P2
- Steps:
  1. Check "Remember me" (if present), login with valid credentials
  2. Close and reopen browser or start a new session
- Expected:
  - If intended behavior is persistent login, user remains logged in or username is remembered per product spec
  - Document actual behavior; ensure secure cookie settings
- Automation: Complex (requires session persistence checks across browser restarts)

8) VWO-LGN-008 — Forgot Password Flow
- Type: Functional
- Priority: P1
- Steps:
  1. Click "Forgot password"
  2. Submit a registered email address
  3. Follow reset link (if accessible in test environment) or verify email delivery
- Expected:
  - Password-reset email is sent to the registered address with a secure, time-limited token
  - Reset page allows setting a new password that then works to login
- Automation: Email handling required — can be validated via test mailboxes or intercept service

9) VWO-LGN-009 — Account Lockout / Rate Limiting
- Type: Security
- Priority: P1
- Steps:
  1. Perform repeated failed login attempts (as per product policy)
- Expected:
  - After threshold, account is temporarily locked or further attempts are throttled
  - Error messages should not reveal whether account exists
- Automation: Possible but must be careful not to lock real accounts; use test accounts

10) VWO-LGN-010 — Session Timeout and Logout
- Type: Functional / Security
- Priority: P1
- Steps:
  1. Login successfully
  2. Remain idle for configured session timeout duration
  3. Attempt to access a protected page
- Expected:
  - User is prompted to re-authenticate when session expires
  - Logout clears session cookies and local storage
- Automation: Simulate session expiry by manipulating cookie expiration or waiting

11) VWO-LGN-011 — CSRF Token Presence
- Type: Security
- Priority: P1
- Steps:
  1. Inspect login form submission for anti-CSRF tokens (hidden input or header)
- Expected:
  - CSRF token present and validated on server side
- Automation: Manual inspection / automated header/form checks

12) VWO-LGN-012 — XSS / Injection Checks on Input
- Type: Security
- Priority: P1
- Steps:
  1. Attempt common XSS payloads in username/email and password fields
  2. Attempt SQL injection-like input strings
- Expected:
  - Application does not execute injected scripts and responds safely
  - Inputs are properly sanitized/encoded
- Automation: Use security scanning tools; do NOT run destructive payloads against production

13) VWO-LGN-013 — Accessibility: Labels, Focus Order, Keyboard Nav
- Type: Accessibility
- Priority: P1
- Steps:
  1. Tab through the page controls
  2. Verify clear focus states, logical order
  3. Use screen reader (NVDA/VoiceOver) to verify labels and announcements
- Expected:
  - All interactive controls have accessible names/labels
  - ARIA roles used properly; error messages announced
- Automation: Axe-core or pa11y can be used to automate parts of this

14) VWO-LGN-014 — Responsive Layout (Mobile & Tablet)
- Type: Functional / UI
- Priority: P2
- Steps:
  1. Load login page at various viewports (mobile, tablet, desktop)
  2. Verify controls are visible and usable
- Expected:
  - Page is usable on small viewports and inputs are reachable
- Automation: Yes — headless browser viewport checks

15) VWO-LGN-015 — Performance: Time to Interactive
- Type: Performance
- Priority: P2
- Steps:
  1. Measure page load TTFB and Time to Interactive on normal and throttled networks
- Expected:
  - Meets performance budgets (define target, e.g., FCP < 2s on 3G slow)
- Automation: Lighthouse or WebPageTest

16) VWO-LGN-016 — Third-party SSO (if available)
- Type: Functional
- Priority: P1
- Steps:
  1. If SSO buttons exist (Google/SSO), attempt login via SSO with test account
- Expected:
  - SSO flow completes and user is signed in; tokens handled securely
- Automation: Often not automated due to external provider constraints

17) VWO-LGN-017 — Localization / Internationalization (if supported)
- Type: Functional
- Priority: P3
- Steps:
  1. Change browser locale (or app language) and verify labels/messages translate
- Expected:
  - Login page text displays correctly in supported languages
- Automation: Possible if app supports language query param or header

Test Data
---------
- Valid user: test+vwo@example.com / CorrectPassword123!
- Invalid user: random_nonexistent_user@example.com
- Edge case inputs: very long email (max length), unicode characters, emoji, SQL-like strings

Automation Recommendations
---------------------------
- Prefer Playwright for cross-browser automation (Chromium, WebKit, Firefox) and reliable selectors.
- Use stable selectors (data-testid, data-qa) if available. Avoid brittle CSS/XPath selectors.
- Structure tests: setup (clear session), action, verification, teardown (logout/clear cookies).
- Use a dedicated test environment to avoid locking production accounts or sending real emails.

Reporting and Severity
----------------------
- P0: Login completely broken or allows unauthorized access
- P1: Security, accessibility, or functional bug that prevents normal login flow for many users
- P2: UI/UX issues or intermittent problems
- P3: Cosmetic or low-risk issues

Notes and Next Steps
--------------------
- If automation is desired, confirm preferred framework (Playwright, Selenium, Cypress) and CI environment (GitHub Actions recommended).
- Provide test account credentials and a test email receiver (mailtrap/dev mailbox) for forgot-password verification and SSO tests.
- If required, prepare example Playwright test scripts for the high-priority cases (VWO-LGN-001, 002, 003, 008).

Maintainer
----------
This file was added to the repository by an AI assistant using Copilot CLI runtime in VS Code. Update the document as test requirements evolve.
