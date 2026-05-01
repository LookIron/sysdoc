# Conditional Documentation Guide

This prompt helps you determine what documentation you should read based on the specific changes you need to make in the codebase. Review the conditions below and read the relevant documentation before proceeding with your task.

## Instructions

- Review the task you've been asked to perform
- Check each documentation path in the Conditional Documentation section
- For each path, evaluate if any of the listed conditions apply to your task
  - IMPORTANT: Only read the documentation if any one of the conditions match your task
- IMPORTANT: You don't want to excessively read documentation. Only read the documentation if it's relevant to your task.

## Conditional Documentation

- README.md
  - Conditions:
    - When operating on anything under app/server
    - When operating on anything under app/client
    - When first understanding the project structure
    - When you want to learn the commands to start or stop the server or client

- AGENTIC_CODING.md
  - Conditions:
    - When operating in the adws/ directory
    - When setting up or debugging ADW workflows
    - When running automated workflows (adw_sdlc_iso.py, etc.)

- adws/README.md
  - Conditions:
    - When modifying or extending the ADW system itself
    - When adding new adw_*.py workflow files
    - When troubleshooting ADW workflow failures

- .claude/commands/classify_adw.md
  - Conditions:
    - When adding or removing new `adws/adw_*.py` files

# ── Project-specific docs (add below as you document features) ──────────────
#
# Pattern:
#
# - app_docs/feature-{adw-id}-{feature-name}.md
#   - Conditions:
#     - When working with [specific area of the codebase]
#     - When implementing [specific feature type]
#     - When troubleshooting [specific issue type]
#
# Add one block per documented feature. The more specific the conditions,
# the fewer tokens you consume per session.
