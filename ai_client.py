"""Anthropic API wrapper for idea extraction, dedup, enrichment, and prompt building."""

import re
import time

from anthropic import Anthropic, APIStatusError

from config import ANTHROPIC_API_KEY, MODEL, log

RETRY_DELAYS = [5, 15, 30]  # seconds — exponential backoff for transient errors
RETRYABLE_STATUS_CODES = {429, 529}


def call_anthropic(user_content: str, max_tokens: int = 4096, model: str | None = None,
                   timeout: float = 120.0) -> str:
    client = Anthropic(api_key=ANTHROPIC_API_KEY, timeout=timeout)
    last_exc = None
    for attempt in range(len(RETRY_DELAYS) + 1):
        try:
            message = client.messages.create(
                model=model or MODEL,
                max_tokens=max_tokens,
                messages=[{"role": "user", "content": user_content}],
            )
            return message.content[0].text
        except APIStatusError as exc:
            if exc.status_code not in RETRYABLE_STATUS_CODES or attempt >= len(RETRY_DELAYS):
                raise
            last_exc = exc
            delay = RETRY_DELAYS[attempt]
            log(f"  API returned {exc.status_code} — retrying in {delay}s (attempt {attempt + 1}/{len(RETRY_DELAYS)})...")
            time.sleep(delay)
        except (ConnectionError, TimeoutError) as exc:
            if attempt >= len(RETRY_DELAYS):
                raise
            last_exc = exc
            delay = RETRY_DELAYS[attempt]
            log(f"  Connection error — retrying in {delay}s (attempt {attempt + 1}/{len(RETRY_DELAYS)})...")
            time.sleep(delay)
    raise last_exc  # unreachable, but satisfies type checker


def extract_ideas(prompt_text: str, file_contents: str) -> str:
    """Extract ideas from file contents. Single call — Sonnet handles large files natively."""
    return call_anthropic(prompt_text + "\n\n" + file_contents, max_tokens=8192)


def enrich_issue(prompt_text: str, title: str, description: str) -> str:
    """Call Sonnet to enrich a Spark issue into Shaped."""
    content = f"{prompt_text}\n\n**Title:** {title}\n\n**Current Description:**\n{description}"
    return call_anthropic(content, max_tokens=4096, timeout=120.0)


def build_prompt(prompt_text: str, title: str, description: str) -> str:
    """Call Sonnet to build a finished prompt from an enriched issue."""
    content = f"{prompt_text}\n\n**Title:** {title}\n\n**Description:**\n{description}"
    return call_anthropic(content, max_tokens=8192, timeout=180.0)


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
