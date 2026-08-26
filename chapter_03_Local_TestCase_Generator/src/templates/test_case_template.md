# Test Cases for {{jira_id}}

Summary:
{{summary}}

Description:
{{description}}

Acceptance Criteria:
{{acceptance_criteria}}

---

Preconditions:
- User has access to application

Test Cases:

1) Title: Verify login with valid credentials
   Preconditions: {{preconditions}}
   Steps:
   - Navigate to login page
   - Enter valid credentials from the ticket test data
   - Click Login
   Expected Result:
   - User is logged in successfully

2) Title: Verify login failure with invalid password
   Steps:
   - Navigate to login page
   - Enter valid email and invalid password
   - Click Login
   Expected Result:
   - Login is rejected with proper error message

Notes:
- Edit this template in templates/ to match your preferred test case format
