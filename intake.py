#!/usr/bin/env python3
"""
intake — Captures brainstorm ideas from text files, extracts structured
issues via AI, deduplicates against a GitLab board, and posts new ones.
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

from config import INTAKE_DIR, PROCESSED_DIR, FAILED_DIR, PROMPT_FILE, QUICK_PROMPT_FILE, log
from ai_client import extract_ideas, filter_duplicates
from gitlab_client import resolve_pat, fetch_existing_issues, post_issue, post_failure_notice
from discord_client import scrape_intake_channel
from parser import parse_issues


def _move_file(filepath: Path, target_dir: Path) -> None:
    target_dir.mkdir(parents=True, exist_ok=True)
    dest = target_dir / filepath.name
    if dest.exists():
        ts = datetime.now().strftime("%Y%m%d%H%M%S")
        dest = target_dir / f"{filepath.stem}_{ts}{filepath.suffix}"
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
        preview = response_text[:200].replace('\n', ' ').strip()
        log(f"  Response preview: {preview}...")
        if not dry_run and pat and post_failure_notice(pat, filepath.name, preview):
            _move_file(filepath, FAILED_DIR)
        else:
            log(f"  Could not post failure notice — leaving {filepath.name} in _intake for retry.")
        return

    log(f"  Found {len(issues)} issue(s).")

    # AI-powered semantic dedup
    if not dry_run and existing_issues:
        issues = filter_duplicates(issues, existing_issues)
        if not issues:
            log(f"  All issues were duplicates — nothing to post.")
            _move_file(filepath, PROCESSED_DIR)
            return
        log(f"  {len(issues)} issue(s) after dedup.")

    # Post to GitLab
    all_success = True
    for i, issue in enumerate(issues, start=1):
        log(f"  Posting {i}/{len(issues)}: {issue['title']}")
        if not post_issue(pat, issue, dry_run):
            all_success = False

    if all_success:
        _move_file(filepath, PROCESSED_DIR)
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

    # Load prompts
    if not PROMPT_FILE.exists():
        log(f"ERROR: Prompt file not found: {PROMPT_FILE}")
        sys.exit(1)
    prompt_text = PROMPT_FILE.read_text(encoding="utf-8")
    log(f"Loaded extraction prompt ({len(prompt_text)} chars)")

    quick_prompt_text = ""
    if QUICK_PROMPT_FILE.exists():
        quick_prompt_text = QUICK_PROMPT_FILE.read_text(encoding="utf-8")
        log(f"Loaded quick-idea prompt ({len(quick_prompt_text)} chars)")

    # Resolve GitLab PAT
    pat = ""
    if not args.dry_run:
        try:
            pat = resolve_pat()
        except RuntimeError as exc:
            log(f"ERROR: {exc}")
            sys.exit(1)

    # Scrape Discord #intake channel (if configured)
    scraped = scrape_intake_channel()
    if scraped:
        log(f"Scraped {scraped} message(s) from Discord #intake.")

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
            is_discord = filepath.name.startswith("discord-")
            prompt = quick_prompt_text if (is_discord and quick_prompt_text) else prompt_text
            process_file(filepath, prompt, pat, args.dry_run, existing_issues)
        except Exception as exc:
            log(f"UNEXPECTED ERROR processing {filepath.name}: {exc}")

    log("Done.")


if __name__ == "__main__":
    main()
