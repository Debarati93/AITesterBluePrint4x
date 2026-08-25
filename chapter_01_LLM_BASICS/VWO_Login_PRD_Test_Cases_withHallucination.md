# VWO Login Dashboard — PRD-Based Test Cases (Anti-Hallucination Compliant)

Source inputs:
- Product Requirements Document: VWO Login Dashboard (PRD)
- Anti-Hallucination Rules
- URL under test: https://app.vwo.com/#/login

Last updated: 2026-08-25T16:06:07.101+05:30
Maintainer: AI assistant using Copilot CLI runtime in VS Code

Important rule applied:
- Tests are derived only from facts explicitly stated in the PRD. Where the PRD lacks a definitive value, the test records "Insufficient information to determine." No undocumented behavior is assumed.

Verified Facts (traceable to PRD):
- Primary authentication method: email + password.
- Secure session handling with configurable timeout periods.
- Optional 2FA support and enterprise SSO capability.
- Real-time field validation (on blur) and email format verification.
- Password strength indicators and password complexity requirements (policy exists but exact values not provided).
- Forgot-password flow using secure token sent by email.
- Responsive design and mobile optimization.
- Accessibility requirements: screen reader support, keyboard navigation, high-contrast support, WCAG 2.1 AA alignment.
- Security requirements: encryption in transit (HTTPS), secure storage of credentials, and brute-force protection (rate limiting).
- Performance target: login page load under 2 seconds on standard connections (target stated; measurement details not provided).

Missing / Unknown (explicitly not assumed):
- Exact UI labels, button text, or DOM element identifiers.
- Concrete password policy values (min length, required character classes).
- Exact session timeout duration and lockout thresholds.
- Which SSO providers are supported (if any).
- Detailed MFA enrollment and recovery flows.
- Exact accessibility pass thresholds or ARIA implementation details.
- Concrete performance measurement method and thresholds beyond the high-level target.

How to read the test cases:
- Traceability: each test lists which PRD requirement(s) it verifies.
- Status: default is "Not executed". After test runs, set to Pass / Fail / Blocked / Insufficient information.
- Where the PRD lacks exact values the Expected Result either uses the PRD language or states "Insufficient information to determine" for specifics.

Test Cases (tight QA template)

1) Test ID: VWO-PRD-01
Objective: Verify login page loads and primary authentication form is presented.
Traceability: PRD — Authentication system; Responsive design; Performance target
Preconditions: Network access to https://app.vwo.com/#/login
Steps:
  1. Open the URL in a supported browser.
  2. Observe page render and visible form elements.
Expected Result: The login page loads and displays the primary authentication form (email and password inputs, and submission control). Page load should meet the PRD performance goal (sub-2s) where measurable; if measurement method or threshold is not available, mark as "Insufficient information to determine." 
Priority: P0
Status: Not executed

2) Test ID: VWO-PRD-02
Objective: Verify successful authentication with valid email and password.
Traceability: PRD — Primary authentication: email + password; Session handling
Preconditions: A valid test user account with known credentials (test environment)
Steps:
  1. Enter valid email.
  2. Enter corresponding password.
  3. Submit the form.
Expected Result: Authentication succeeds and user is routed to the authenticated entry point (dashboard or equivalent). Session handling is applied per PRD (secure session established). Exact post-login UI elements are "Insufficient information to determine."
Priority: P0
Status: Not executed

3) Test ID: VWO-PRD-03
Objective: Verify email input validation (real-time/on-blur) for malformed addresses.
Traceability: PRD — Real-time validation; Email format verification
Preconditions: On login page
Steps:
  1. Enter malformed email addresses (e.g., missing @ or domain) into the email field.
  2. Move focus away from the field or attempt submission.
Expected Result: The UI provides immediate validation feedback consistent with PRD requirements. Exact validation message text is not specified in the PRD.
Priority: P1
Status: Not executed

4) Test ID: VWO-PRD-04
Objective: Verify failed authentication returns clear, actionable error messaging without revealing sensitive account existence details.
Traceability: PRD — Error handling requirements
Preconditions: Known valid email and an incorrect password (use a test account)
Steps:
  1. Enter a valid email.
  2. Enter an incorrect password.
  3. Submit the form.
Expected Result: Login is rejected and a clear, actionable error message is shown. PRD does not specify exact text; do not assume messages that reveal whether the account exists. If message content is absent or discloses sensitive info, record as Fail.
Priority: P0
Status: Not executed

5) Test ID: VWO-PRD-05
Objective: Verify password strength indicators or feedback are surfaced where applicable.
Traceability: PRD — Password strength indicators; Password requirements
Preconditions: Password input present (login or associated account flows)
Steps:
  1. Enter weak and strong password examples where UI shows feedback.
  2. Observe any strength meter or requirement checklist.
Expected Result: Visual or textual feedback for password strength or compliance appears per PRD. Exact policy thresholds are "Insufficient information to determine."
Priority: P1
Status: Not executed

6) Test ID: VWO-PRD-06
Objective: Verify forgot-password flow initiates secure reset via email token.
Traceability: PRD — Forgot password; Secure token generation; Email-based reset
Preconditions: Access to a test mailbox for the registered email
Steps:
  1. Click the forgot-password/recover link on the login page.
  2. Submit a registered email address.
  3. Verify that an email is received containing a reset mechanism (link or token) and that following the mechanism allows resetting the password.
Expected Result: The system sends a password-reset email containing a secure, time-limited token. Exact token lifetime and email template are "Insufficient information to determine." If no email is received in the test environment, mark the test as Blocked.
Priority: P0
Status: Not executed

7) Test ID: VWO-PRD-07
Objective: Verify persistence behavior associated with "remember me" or persistent login if present.
Traceability: PRD — Remembered sessions; Quick access
Preconditions: Interface exposes a persistent-login option (presence not guaranteed in PRD)
Steps:
  1. If a remember-me option exists, enable it and complete login.
  2. Close and reopen the browser or start a new session and revisit the site.
Expected Result: If the product intends persistent login per PRD, the session should persist consistent with PRD security constraints. Exact persistence semantics are "Insufficient information to determine." If the control is not present, mark as "Not applicable / Insufficient information."
Priority: P2
Status: Not executed

8) Test ID: VWO-PRD-08
Objective: Verify session timeout/enforced re-authentication behavior.
Traceability: PRD — Session management; Configurable timeout
Preconditions: Valid authenticated session
Steps:
  1. Authenticate successfully.
  2. Remain idle until the configured timeout (or simulate expiry in test environment).
  3. Attempt to access a protected area.
Expected Result: User is prompted to re-authenticate after session expiry. Exact timeout value is "Insufficient information to determine." Use simulated expiry if actual timeout is impractical for testing.
Priority: P1
Status: Not executed

9) Test ID: VWO-PRD-09
Objective: Verify brute-force protection/rate limiting behavior.
Traceability: PRD — Rate limiting; Brute-force protection
Preconditions: Test account in a controlled environment (do not use production accounts)
Steps:
  1. Perform repeated failed login attempts against the same account from same client (as allowed by test policy).
  2. Observe whether throttling, temporary lockout, or CAPTCHA appears.
Expected Result: System applies protective measures (throttling, lockout, or similar) per PRD. Exact threshold numbers are "Insufficient information to determine." If the environment cannot safely test this, mark as Blocked.
Priority: P1
Status: Not executed

10) Test ID: VWO-PRD-10
Objective: Verify keyboard navigation and screen-reader compatibility of the login form.
Traceability: PRD — Accessibility: keyboard nav; Screen reader support; WCAG 2.1 AA
Preconditions: Accessibility tools available (screen reader, keyboard only)
Steps:
  1. Tab through all interactive elements; verify logical focus order and visible focus state.
  2. Use a screen reader to check that input labels and error messages are announced.
Expected Result: Controls are keyboard-accessible, focus order is logical, and screen reader exposes accessible names/announcements. Specific ARIA attributes or audit pass criteria are "Insufficient information to determine."
Priority: P1
Status: Not executed

11) Test ID: VWO-PRD-11
Objective: Verify high-contrast and clickable labels per accessibility requirements.
Traceability: PRD — High contrast; Clickable form labels
Preconditions: Ability to enable high-contrast or inspect label behavior
Steps:
  1. Enable high-contrast mode (OS/browser) and inspect readability.
  2. Click form labels and ensure they focus the corresponding input.
Expected Result: Text remains readable in high-contrast mode and labels are clickable. Exact contrast ratios are "Insufficient information to determine."
Priority: P1
Status: Not executed

12) Test ID: VWO-PRD-12
Objective: Verify transport-level security (HTTPS) for the login flow.
Traceability: PRD — HTTPS enforcement; Encryption in transit
Preconditions: Network access to the login URL
Steps:
  1. Inspect the page URL scheme and connection security details in the browser.
  2. Submit credentials and observe that requests are sent over HTTPS (when possible capture request metadata in test environment).
Expected Result: All authentication traffic uses HTTPS. Certificate specifics and cipher suites are "Insufficient information to determine."
Priority: P0
Status: Not executed

13) Test ID: VWO-PRD-13
Objective: Verify responsiveness and usability on mobile/tablet viewports.
Traceability: PRD — Responsive design; Mobile optimization
Preconditions: Device emulation or physical devices available
Steps:
  1. Load the login URL at typical mobile and tablet viewports.
  2. Verify controls are visible, reachable, and touch-friendly.
Expected Result: The login form is usable on smaller viewports. Exact breakpoints are "Insufficient information to determine."
Priority: P1
Status: Not executed

14) Test ID: VWO-PRD-14
Objective: Verify optional 2FA and enterprise SSO flows when configured.
Traceability: PRD — Optional 2FA; Enterprise SSO capability
Preconditions: Test environment configured with 2FA or SSO and test accounts available
Steps:
  1. Perform login for an account configured with 2FA and follow the MFA flow.
  2. If SSO is configured, initiate SSO and complete the provider flow.
Expected Result: 2FA and SSO flows complete successfully when configured. Exact provider names and enrollment details are "Insufficient information to determine." If environment lacks configuration, mark as Blocked or Not applicable.
Priority: P1
Status: Not executed

15) Test ID: VWO-PRD-15
Objective: Measure page load performance against PRD target.
Traceability: PRD — Performance target: sub-2-second load
Preconditions: Controlled measurement environment and tools (Lighthouse, WebPageTest)
Steps:
  1. Measure page load (FCP/TTI) under standard network conditions.
  2. Record results and compare to PRD target.
Expected Result: Page load meets PRD's stated sub-2-second target where measurable. If measurement approach is unspecified, report results and mark threshold verification as "Insufficient information to determine."
Priority: P2
Status: Not executed

Self-validation checklist:
- Each test maps to one or more PRD statements.
- No new UI text, credentials, or thresholds were invented.
- Tests explicitly mark unknown specifics as "Insufficient information to determine." 

Next steps / Recommendations:
- Provide concrete test account credentials and a test email receiver to execute P0/P1 tests (VWO-PRD-02, 06, 09, 14).
- If automation is desired, confirm preferred framework (Playwright recommended) and include stable selectors (data-testid) from the development team.
- For performance validation, share the exact measurement method and acceptable thresholds.

This tightened template is ready to be executed or exported to a test management tool. Update Status after execution and record artifacts (screenshots, HAR files, email captures) to maintain PRD traceability.
