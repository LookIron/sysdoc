# E2E Test Runner

Run end-to-end tests using Playwright.

## Variables

test_file: $ARGUMENTS

## Instructions

1. Read the test file specified in `test_file` (if provided)
2. Ensure the application is running (use `/prepare_app` if needed)
3. Execute the E2E test steps described in the test file
4. Use Playwright MCP tools to interact with the browser
5. Take screenshots at key steps to document results
6. Report pass/fail for each test step

## Implementation

If a specific test file is provided:
- Read `.claude/commands/e2e/{test_file}.md`
- Follow the test steps defined in that file

If no test file is provided:
- Run the full Playwright test suite: `cd app/client && bun test:e2e`

## Notes

- E2E tests require the application to be running
- Test files are in `.claude/commands/e2e/`
- Screenshots are saved to document test results
- Use Playwright MCP for browser interaction in agent context
