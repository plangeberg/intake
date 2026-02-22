#!/usr/bin/env python3
"""
intake — Captures brainstorm ideas from text files, extracts structured
issues via AI, deduplicates against a GitLab board, and posts new ones.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from config import INTAKE_DIR, PROCESSED_DIR, PROMPT_FILE, log
from ai_client import extract_ideas, filter_duplicates
from gitlab_client import resolve_pat, fetch_existing_issues, post_issue
from parser import parse_issues


def _move_to_processed(filepath: Path) -> None:
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    dest = PROCESSED_DIR / filepath.name
    if dest.exists():
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        dest = PROCESSED_DIR / f"{filepath.stem}_{ts}{filepath.suffix}"
    filepath.rename(dest)
    log(f"  Moved to {dest}")


def process_file(
    filepath: Path,
    prompt_text: str,
    pat: str,
    dry_run: bool,
    existing_issues: list[dict],
) -> None:
    log(f"Processing {filepath.name}...")

    try:
        file_contents = filepath.read_text(encoding="utf-8")
    except Exception as exc:
        log(f"  ERROR: Could not read {filepath.name}: {exc}")
        return

    if not file_contents.strip():
        log(f"  Skipping empty file: {filepath.name}")
        return

    # Extract ideas via AI
    from config import MODEL
    log(f"  Calling Anthropic ({MODEL})...")
    try:
        response_text = extract_ideas(prompt_text, file_contents)
    except Exception as exc:
        log(f"  ERROR: Anthropic API call failed for {filepath.name}: {exc}")
        return

    # Parse structured issues from response
    issues = parse_issues(response_text)
    if not issues:
        log(f"  WARNING: No GITLAB ISSUE blocks found in response for {filepath.name}")
        log(f"  Response preview: {response_text[:300]}")
        return

    log(f"  Found {len(issues)} issue(s).")

    # AI-powered semantic dedup
    if not dry_run and existing_issues:
        issues = filter_duplicates(issues, existing_issues)
        if not issues:
            log(f"  All issues were duplicates — nothing to post.")
            _move_to_processed(filepath)
            return
        log(f"  {len(issues)} issue(s) after dedup.")

    # Post to GitLab
    all_success = True
    for i, issue in enumerate(issues, start=1):
        log(f"  Posting {i}/{len(issues)}: {issue['title']}")
        if not post_issue(pat, issue, dry_run):
            all_success = False

    if all_success:
        _move_to_processed(filepath)
    else:
        log(f"  One or more GitLab POSTs failed — leaving {filepath.name} in _intake for retry.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Intake: brainstorm → AI → GitLab issues")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Extract and parse but don't POST to GitLab.",
    )
    args = parser.parse_args()

    # Validate intake folder
    if not INTAKE_DIR.exists():
        log(f"ERROR: Intake folder does not exist: {INTAKE_DIR}")
        log("Create the folder (or set up a junction) and add files to process.")
        sys.exit(1)

    # Load prompt
    if not PROMPT_FILE.exists():
        log(f"ERROR: Prompt file not found: {PROMPT_FILE}")
        sys.exit(1)
    prompt_text = PROMPT_FILE.read_text(encoding="utf-8")
    log(f"Loaded prompt from {PROMPT_FILE} ({len(prompt_text)} chars)")

    # Resolve GitLab PAT
    pat = ""
    if not args.dry_run:
        try:
            pat = resolve_pat()
        except RuntimeError as exc:
            log(f"ERROR: {exc}")
            sys.exit(1)

    # Collect files
    files = sorted(
        f for f in INTAKE_DIR.iterdir()
        if f.is_file() and f.suffix.lower() in {".txt", ".md"}
    )

    if not files:
        log(f"No .txt or .md files found in {INTAKE_DIR}. Nothing to do.")
        return

    log(f"Found {len(files)} file(s) to process in {INTAKE_DIR}")
    if args.dry_run:
        log("DRY RUN mode — GitLab POSTs will be skipped.")

    # Fetch existing issues once for dedup
    existing_issues = []
    if not args.dry_run:
        existing_issues = fetch_existing_issues(pat)
        log(f"Loaded {len(existing_issues)} existing open issue(s) for dedup.")

    for filepath in files:
        try:
            process_file(filepath, prompt_text, pat, args.dry_run, existing_issues)
        except Exception as exc:
            log(f"UNEXPECTED ERROR processing {filepath.name}: {exc}")

    log("Done.")


if __name__ == "__main__":
    main()
