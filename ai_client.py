"""Anthropic API wrapper for idea extraction and dedup."""

import re

from anthropic import Anthropic

from config import ANTHROPIC_API_KEY, MODEL, log


def call_anthropic(user_content: str, max_tokens: int = 4096) -> str:
    client = Anthropic(api_key=ANTHROPIC_API_KEY, timeout=120.0)
    message = client.messages.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[{"role": "user", "content": user_content}],
    )
    return message.content[0].text


def extract_ideas(prompt_text: str, file_contents: str) -> str:
    return call_anthropic(prompt_text + "\n\n" + file_contents)


DEDUP_PROMPT = """\
You are a duplicate detector. Compare NEW issues against EXISTING issues on a GitLab board.

Two issues are duplicates if they describe the same idea, even if worded differently.
For example: "Build Discord-to-GitLab Kanban bot" and "Build Discord-to-GitLab Kanban intake bot" are duplicates.

EXISTING ISSUES (already on the board):
{existing}

NEW ISSUES (candidates to add):
{new}

For each new issue, respond with exactly one line:
NEW [number]: KEEP or NEW [number]: DUPLICATE of #[iid]

Example output:
NEW 1: KEEP
NEW 2: DUPLICATE of #18
NEW 3: KEEP
"""


def filter_duplicates(
    new_issues: list[dict],
    existing_issues: list[dict],
) -> list[dict]:
    """Use AI to semantically filter duplicates. Returns only non-duplicate issues."""
    if not existing_issues:
        return new_issues

    existing_text = "\n".join(
        f"- #{iss['iid']}: {iss['title']}" for iss in existing_issues
    )
    new_text = "\n".join(
        f"- NEW {i}: {iss['title']}" for i, iss in enumerate(new_issues, 1)
    )

    prompt = DEDUP_PROMPT.format(existing=existing_text, new=new_text)
    log(f"  Dedup check: {len(new_issues)} new vs {len(existing_issues)} existing issues...")

    try:
        response = call_anthropic(prompt, max_tokens=1024)
    except Exception as exc:
        log(f"  Warning: dedup AI call failed ({exc}), posting all issues to be safe.")
        return new_issues

    kept = []
    for i, issue in enumerate(new_issues, 1):
        line_pattern = rf"NEW\s+{i}\s*:\s*(KEEP|DUPLICATE)"
        match = re.search(line_pattern, response, re.IGNORECASE)
        if match and "duplicate" in match.group(1).lower():
            log(f"  SKIPPED (AI dedup): '{issue['title']}'")
        else:
            kept.append(issue)

    return kept
