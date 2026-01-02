# Feature: One Click Table Exports

## Metadata
issue_number: `4`
adw_id: `6f39aae6`
issue_json: `{"number":4,"title":"One click table exports","body":"Develop export feature. Using adw_paln_build_review add one click table exports and one click result export feature to get results as csv files.\n\nCreate two new endpoints to support these features. One exporting tables, one for exporting query results.\n\nPlace download button directly to the left of the 'x' icon for available tables.\nPlace download button directly to the left of the 'hide' button for query results.\n\nUse the appropriate download icon"}`

## Feature Description
This feature adds CSV export capabilities to the Natural Language SQL Interface application. Users will be able to export:
1. **Table data** - Export any available table's complete data as a CSV file with a single click
2. **Query results** - Export the results of any executed query as a CSV file with a single click

Each export functionality will have a dedicated download button placed in an intuitive location near existing controls, using appropriate download icons for clear user experience.

## User Story
As a data analyst using the Natural Language SQL Interface
I want to export my table data and query results as CSV files with a single click
So that I can easily share, analyze, or archive my data in a universally compatible format

## Problem Statement
Currently, users can query their data and view results within the application, but there is no way to export or download this data. Users who need to share results, perform further analysis in external tools (like Excel), or archive query outcomes have no built-in mechanism to do so.

## Solution Statement
Implement two new backend endpoints and corresponding frontend UI elements:
1. `GET /api/table/{table_name}/export` - Returns the complete table data as a downloadable CSV file
2. `POST /api/query/export` - Executes a query and returns the results as a downloadable CSV file

The frontend will add download buttons:
- For tables: A download button placed directly to the left of the existing 'x' (remove) button in the table header
- For query results: A download button placed directly to the left of the 'Hide' button in the results header

Both buttons will use an appropriate download icon (SVG arrow pointing down with a tray/line) for consistent and intuitive UX.

## Relevant Files
Use these files to implement the feature:

**Backend Files:**
- `app/server/server.py` - Main FastAPI application where new endpoints will be added
- `app/server/core/data_models.py` - Pydantic models for request/response types (may need new models for export)
- `app/server/core/sql_processor.py` - Contains `execute_sql_safely` and `get_database_schema` functions used to fetch data
- `app/server/core/sql_security.py` - Security module for safe SQL execution with `validate_identifier` and `execute_query_safely`

**Frontend Files:**
- `app/client/src/main.ts` - Main frontend application with `displayTables` and `displayResults` functions that need download buttons
- `app/client/src/api/client.ts` - API client where export methods need to be added
- `app/client/src/types.d.ts` - TypeScript type definitions (may need new export response types)
- `app/client/src/style.css` - Styles for the download button
- `app/client/index.html` - HTML structure (may need minor adjustments for button placement)

**Test Files:**
- `app/server/tests/` - Directory for new unit tests for export endpoints

**E2E Test Reference:**
- `.claude/commands/test_e2e.md` - Instructions for creating E2E tests
- `.claude/commands/e2e/test_basic_query.md` - Example E2E test file to follow as a template

### New Files
- `app/server/tests/test_export.py` - Unit tests for export endpoints
- `.claude/commands/e2e/test_table_exports.md` - E2E test file for validating the export feature

## Implementation Plan
### Phase 1: Foundation
1. Create new Pydantic response models for export functionality in `data_models.py` (if needed - may just use StreamingResponse)
2. Design the CSV generation utility function that can convert query results to CSV format
3. Add unit test structure for export functionality

### Phase 2: Core Implementation
1. Implement `GET /api/table/{table_name}/export` endpoint in `server.py`:
   - Validate table name using existing security module
   - Fetch all table data using existing `execute_query_safely`
   - Convert results to CSV using Python's `csv` module
   - Return as StreamingResponse with appropriate headers for file download

2. Implement `POST /api/query/export` endpoint in `server.py`:
   - Accept query request similar to `/api/query`
   - Execute query and get results
   - Convert results to CSV format
   - Return as StreamingResponse with appropriate headers for file download

3. Add frontend API methods in `client.ts`:
   - `exportTable(tableName: string)` - Triggers table CSV download
   - `exportQueryResults(request: QueryRequest)` - Triggers query results CSV download

4. Add download buttons in `main.ts`:
   - Modify `displayTables` function to add download button to table header
   - Modify `displayResults` function to add download button to results header

5. Add CSS styles for download button in `style.css`

### Phase 3: Integration
1. Wire up download buttons to API methods
2. Handle download response as file download (create blob and trigger download)
3. Add error handling for export failures
4. Add loading states during export

## Step by Step Tasks
IMPORTANT: Execute every step in order, top to bottom.

### Step 1: Create E2E Test File
- Read `.claude/commands/test_e2e.md` and `.claude/commands/e2e/test_basic_query.md` to understand E2E test format
- Create `.claude/commands/e2e/test_table_exports.md` with test steps that:
  1. Navigate to application
  2. Upload sample data (users)
  3. Verify download button appears next to remove button for the table
  4. Click download button for table export
  5. Verify CSV file is downloaded
  6. Enter and execute a query
  7. Verify download button appears next to hide button in results
  8. Click download button for query results export
  9. Verify CSV file is downloaded
  10. Take screenshots at key steps

### Step 2: Implement Table Export Backend Endpoint
- Add `GET /api/table/{table_name}/export` endpoint in `app/server/server.py`
- Use `validate_identifier` from `sql_security.py` to validate table name
- Use `execute_query_safely` to fetch all table data with `SELECT * FROM {table}`
- Import Python's `csv` module and `io.StringIO` for CSV generation
- Use FastAPI's `StreamingResponse` with `media_type="text/csv"` and `Content-Disposition` header for filename
- Return CSV data as a downloadable file named `{table_name}.csv`
- Handle errors appropriately (table not found, security errors)

### Step 3: Implement Query Export Backend Endpoint
- Add `POST /api/query/export` endpoint in `app/server/server.py`
- Accept `QueryRequest` model (same as `/api/query`)
- Execute query using same logic as `/api/query` endpoint
- Convert results to CSV format
- Return as StreamingResponse with filename `query_results.csv`
- Handle errors appropriately

### Step 4: Add Unit Tests for Export Endpoints
- Create `app/server/tests/test_export.py`
- Test table export endpoint:
  - Test successful export returns CSV with correct headers
  - Test export of non-existent table returns 404
  - Test export with invalid table name (SQL injection attempt) returns 400
- Test query export endpoint:
  - Test successful query export returns CSV
  - Test query with no results returns empty CSV (just headers)
  - Test query with error returns appropriate error response

### Step 5: Add Download Button Styles to CSS
- Add `.download-button` class in `app/client/src/style.css`
- Style similar to `.remove-table-button` but with download icon styling
- Add hover state with primary color highlight
- Keep consistent sizing with other action buttons (2rem x 2rem)

### Step 6: Update Frontend API Client
- Add `exportTable(tableName: string)` method in `app/client/src/api/client.ts`
  - Make GET request to `/table/${tableName}/export`
  - Handle response as blob and trigger download
- Add `exportQueryResults(request: QueryRequest)` method
  - Make POST request to `/query/export`
  - Handle response as blob and trigger download
- Create helper function `downloadBlob(blob: Blob, filename: string)` to handle file downloads

### Step 7: Add Download Button to Table Display
- Modify `displayTables` function in `app/client/src/main.ts`
- Create download button element with SVG download icon
- Insert download button directly to the left of the remove button (`&times;`)
- Add click handler that calls `api.exportTable(table.name)`
- Add wrapper div for button group (download + remove buttons)

### Step 8: Add Download Button to Query Results Display
- Modify `displayResults` function in `app/client/src/main.ts`
- Store the last query request in module-level state for re-use during export
- Create download button element with SVG download icon
- Insert download button directly to the left of the hide button
- Add click handler that calls `api.exportQueryResults(lastQueryRequest)`
- Handle case where there are no results (disable button or hide it)

### Step 9: Run Validation Commands
- Run `cd app/server && uv run pytest` to ensure all server tests pass
- Run `cd app/client && bun tsc --noEmit` to ensure TypeScript compiles without errors
- Run `cd app/client && bun run build` to ensure frontend builds successfully
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_table_exports.md` E2E test to validate the feature works end-to-end

## Testing Strategy
### Unit Tests
- `test_export_table_success` - Verify table export returns valid CSV with correct data
- `test_export_table_not_found` - Verify 404 when table doesn't exist
- `test_export_table_invalid_name` - Verify 400 for SQL injection attempts in table name
- `test_export_query_success` - Verify query results export returns valid CSV
- `test_export_query_empty_results` - Verify empty query returns CSV with headers only
- `test_export_query_error` - Verify error handling for invalid queries
- `test_csv_format_correct` - Verify CSV has correct format (headers, escaping, encoding)

### Edge Cases
- Table with no rows - should export CSV with headers only
- Query that returns no results - should export CSV with headers only
- Table/column names with special characters - should be properly escaped in CSV
- Large result sets - should stream efficiently without memory issues
- Unicode data in table/results - should be properly encoded in CSV (UTF-8)
- Concurrent export requests - should handle multiple simultaneous exports
- Table names with SQL reserved words - should be handled by existing security

## Acceptance Criteria
- [ ] Download button appears to the left of the 'x' button for each table in Available Tables section
- [ ] Download button appears to the left of the 'Hide' button in Query Results section
- [ ] Clicking table download button triggers download of `{table_name}.csv` file
- [ ] Clicking results download button triggers download of `query_results.csv` file
- [ ] CSV files contain correct data with proper headers matching column names
- [ ] CSV files are properly formatted (RFC 4180 compliant)
- [ ] Download buttons use appropriate download icon (arrow pointing down)
- [ ] Error cases are handled gracefully with user feedback
- [ ] All existing tests continue to pass (zero regressions)
- [ ] E2E test validates complete export flow

## Validation Commands
Execute every command to validate the feature works correctly with zero regressions.

- `cd app/server && uv run pytest` - Run server tests to validate the feature works with zero regressions
- `cd app/client && bun tsc --noEmit` - Run frontend tests to validate the feature works with zero regressions
- `cd app/client && bun run build` - Run frontend build to validate the feature works with zero regressions
- Read `.claude/commands/test_e2e.md`, then read and execute `.claude/commands/e2e/test_table_exports.md` E2E test file to validate this functionality works

## Notes
- The CSV export uses Python's built-in `csv` module which handles escaping and formatting automatically
- StreamingResponse is used for efficient memory usage with large datasets
- The download icon should be an SVG for crisp rendering at all sizes - a common pattern is an arrow pointing down into a tray/horizontal line
- Consider future enhancement: Allow users to choose export format (CSV, JSON, Excel) via dropdown
- Consider future enhancement: Add filename customization or timestamp in filename
- The query export endpoint re-executes the query to ensure fresh data; an alternative would be to cache results but this adds complexity
- UTF-8 BOM may be added to CSV for better Excel compatibility if needed in the future
