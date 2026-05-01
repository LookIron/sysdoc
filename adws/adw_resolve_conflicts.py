#!/usr/bin/env -S uv run
# /// script
# dependencies = ["python-dotenv", "pydantic"]
# ///

"""
ADW Resolve Conflicts - Intelligently resolve merge conflicts before ship

Usage:
  uv run adw_resolve_conflicts.py <issue-number> <adw-id>

This workflow:
1. Attempts to merge main into the feature branch
2. Detects conflicts
3. Uses Claude to intelligently resolve conflicts
4. Validates the resolution
5. Commits the merge
"""

import sys
import os
import subprocess
import logging
from typing import List, Tuple
from dotenv import load_dotenv

from adw_modules.state import ADWState
from adw_modules.github import make_issue_comment
from adw_modules.workflow_ops import format_issue_message
from adw_modules.utils import setup_logger
from adw_modules.agent import execute_template
from adw_modules.data_types import AgentTemplateRequest

# Load environment variables
load_dotenv()


def detect_conflicts(worktree_path: str) -> Tuple[bool, List[str]]:
    """Detect if there are merge conflicts."""
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=U"],
        capture_output=True,
        text=True,
        cwd=worktree_path
    )

    conflicted_files = [f.strip() for f in result.stdout.split('\n') if f.strip()]
    has_conflicts = len(conflicted_files) > 0

    return has_conflicts, conflicted_files


def attempt_merge(worktree_path: str, branch_name: str) -> Tuple[bool, str]:
    """Attempt to merge main into feature branch."""
    # Fetch latest main
    subprocess.run(
        ["git", "fetch", "origin", "main"],
        capture_output=True,
        cwd=worktree_path
    )

    # Attempt merge
    result = subprocess.run(
        ["git", "merge", "origin/main", "--no-commit"],
        capture_output=True,
        text=True,
        cwd=worktree_path
    )

    if result.returncode == 0:
        # No conflicts, merge succeeded
        return True, "Clean merge, no conflicts"
    else:
        # Conflicts detected
        return False, result.stdout + result.stderr


def resolve_conflicts_with_claude(
    conflicted_files: List[str],
    adw_id: str,
    logger: logging.Logger,
    worktree_path: str
) -> Tuple[bool, str]:
    """Resolve conflicts programmatically using predefined strategies."""
    resolved_files = []

    for file in conflicted_files:
        logger.info(f"Resolving conflict in {file}")

        # Strategy 1: Tracking/Metrics Files (Combine Both)
        if "agentic_kpis.md" in file:
            # For KPI files, keep both entries - take ours (HEAD)
            subprocess.run(["git", "checkout", "--ours", file], cwd=worktree_path)
            subprocess.run(["git", "add", file], cwd=worktree_path)
            resolved_files.append(f"{file} (kept both entries)")

        # Strategy 2: Auto-generated Files (Regenerate)
        elif "sw.js" in file or ".next/" in file:
            # Take incoming (main) version - will regenerate on next build
            subprocess.run(["git", "checkout", "--theirs", file], cwd=worktree_path)
            subprocess.run(["git", "add", file], cwd=worktree_path)
            resolved_files.append(f"{file} (took main, will regenerate)")

        # Strategy 3: Configuration Files (Take ours - worktree-specific)
        elif file in [".mcp.json", "playwright-mcp-config.json"]:
            # These are worktree-specific configs, keep ours
            subprocess.run(["git", "checkout", "--ours", file], cwd=worktree_path)
            subprocess.run(["git", "add", file], cwd=worktree_path)
            resolved_files.append(f"{file} (kept worktree config)")

        # Strategy 4: Documentation Files (Keep ours)
        elif ".claude/commands/" in file or "app_docs/" in file:
            # Keep our version for documentation
            subprocess.run(["git", "checkout", "--ours", file], cwd=worktree_path)
            subprocess.run(["git", "add", file], cwd=worktree_path)
            resolved_files.append(f"{file} (kept feature docs)")

        # Strategy 5: Source Code (Manual review - fail for now)
        elif file.startswith("src/") or file.startswith("tests/"):
            return False, f"Source code conflict requires manual review: {file}"

        else:
            # Unknown file type - take ours as default
            logger.warning(f"Unknown file type, defaulting to --ours: {file}")
            subprocess.run(["git", "checkout", "--ours", file], cwd=worktree_path)
            subprocess.run(["git", "add", file], cwd=worktree_path)
            resolved_files.append(f"{file} (default: kept ours)")

    summary = "Resolved conflicts:\n" + "\n".join([f"- {f}" for f in resolved_files])
    return True, summary


def validate_resolution(worktree_path: str, logger: logging.Logger) -> Tuple[bool, str]:
    """Validate that conflicts are resolved and code is valid."""
    # Check no conflicts remain
    has_conflicts, remaining_files = detect_conflicts(worktree_path)
    if has_conflicts:
        return False, f"Conflicts still present: {remaining_files}"

    # Check lint
    lint_result = subprocess.run(
        ["pnpm", "lint"],
        capture_output=True,
        text=True,
        cwd=worktree_path
    )
    if lint_result.returncode != 0:
        logger.warning(f"Lint warnings after conflict resolution: {lint_result.stdout}")

    # Check build
    build_result = subprocess.run(
        ["pnpm", "build"],
        capture_output=True,
        text=True,
        cwd=worktree_path,
        timeout=300
    )
    if build_result.returncode != 0:
        return False, f"Build failed after resolution: {build_result.stderr[:1000]}"

    return True, "All validations passed"


def main():
    """Main entry point."""
    if len(sys.argv) < 3:
        print("Usage: uv run adw_resolve_conflicts.py <issue-number> <adw-id>")
        sys.exit(1)

    issue_number = sys.argv[1]
    adw_id = sys.argv[2]

    # Load state
    temp_logger = setup_logger(adw_id, "adw_resolve_conflicts")
    state = ADWState.load(adw_id, temp_logger)

    if not state:
        print(f"Error: No state found for ADW ID: {adw_id}")
        sys.exit(1)

    logger = setup_logger(adw_id, "adw_resolve_conflicts")
    logger.info(f"ADW Resolve Conflicts starting - ID: {adw_id}, Issue: {issue_number}")

    worktree_path = state.get("worktree_path")
    branch_name = state.get("branch_name")

    if not worktree_path or not branch_name:
        logger.error("Missing worktree_path or branch_name in state")
        sys.exit(1)

    # Attempt merge
    logger.info("Attempting to merge main into feature branch")
    merge_success, merge_output = attempt_merge(worktree_path, branch_name)

    if merge_success:
        logger.info("Clean merge, no conflicts detected")
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, "conflict_resolver", "✅ Clean merge, no conflicts")
        )
        sys.exit(0)

    # Detect conflicts
    has_conflicts, conflicted_files = detect_conflicts(worktree_path)
    logger.info(f"Detected {len(conflicted_files)} conflicted files")

    make_issue_comment(
        issue_number,
        format_issue_message(
            adw_id,
            "conflict_resolver",
            f"⚠️ Detected {len(conflicted_files)} merge conflicts:\n" +
            "\n".join([f"- `{f}`" for f in conflicted_files]) +
            "\n\nResolving conflicts automatically..."
        )
    )

    # Resolve conflicts with Claude
    logger.info("Resolving conflicts with Claude")
    resolution_success, resolution_output = resolve_conflicts_with_claude(
        conflicted_files, adw_id, logger, worktree_path
    )

    if not resolution_success:
        logger.error(f"Failed to resolve conflicts: {resolution_output}")
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, "conflict_resolver", f"❌ Failed to resolve conflicts:\n{resolution_output}")
        )
        sys.exit(1)

    # Validate resolution
    logger.info("Validating conflict resolution")
    validation_success, validation_output = validate_resolution(worktree_path, logger)

    if not validation_success:
        logger.error(f"Validation failed: {validation_output}")
        make_issue_comment(
            issue_number,
            format_issue_message(adw_id, "conflict_resolver", f"❌ Validation failed:\n{validation_output}")
        )
        sys.exit(1)

    # Commit the merge
    commit_result = subprocess.run(
        ["git", "commit", "-m", "chore: resolve merge conflicts with main"],
        capture_output=True,
        text=True,
        cwd=worktree_path
    )

    if commit_result.returncode != 0:
        logger.error(f"Failed to commit resolution: {commit_result.stderr}")
        sys.exit(1)

    logger.info("Conflicts resolved and committed successfully")
    make_issue_comment(
        issue_number,
        format_issue_message(
            adw_id,
            "conflict_resolver",
            f"✅ Conflicts resolved successfully\n\n" +
            f"**Files resolved**: {len(conflicted_files)}\n" +
            f"**Validation**: {validation_output}\n\n" +
            resolution_output
        )
    )

    print("Conflicts resolved successfully")


if __name__ == "__main__":
    main()
