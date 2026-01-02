# E2E Test: Table Exports

Test the one-click table export and query results export functionality in the Natural Language SQL Interface application.

## User Story

As a data analyst using the Natural Language SQL Interface
I want to export my table data and query results as CSV files with a single click
So that I can easily share, analyze, or archive my data in a universally compatible format

## Test Steps

1. Navigate to the `Application URL`
2. Take a screenshot of the initial state
3. **Verify** the page title is "Natural Language SQL Interface"
4. **Verify** the Upload Data button is present
5. Click the Upload Data button
6. Upload the sample file: `app/client/sample_data/users.csv`
7. Take a screenshot after file upload
8. **Verify** the "users" table appears in the Available Tables section
9. **Verify** a download button (with download icon) appears to the left of the 'x' (remove) button for the users table
10. Take a screenshot showing the download button next to the table
11. Click the download button for the users table
12. **Verify** a CSV file download is triggered (check for download response or network request)
13. Take a screenshot after clicking download button
14. Enter the query: "Show me all users"
15. Click the Query button
16. **Verify** the query results appear in the Results section
17. **Verify** a download button appears to the left of the "Hide" button in the results header
18. Take a screenshot showing the download button in results section
19. Click the download button for query results
20. **Verify** a CSV file download is triggered for query results
21. Take a screenshot after clicking results download button
22. Click "Hide" button to close results
23. Take a screenshot of final state

## Success Criteria
- Upload button allows CSV file upload
- Users table appears after upload
- Download button is visible next to the remove button for each table
- Download button is visible next to the Hide button for query results
- Clicking table download button triggers CSV download
- Clicking results download button triggers CSV download
- Download buttons use appropriate download icon (arrow pointing down)
- 7 screenshots are taken
