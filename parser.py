"""Parse GITLAB ISSUE blocks from AI response text."""

import re

ISSUE_PATTERN = re.compile(
    r"### GITLAB ISSUE:\s*\[?\d+\]?\s*\n"
    r"\*\*Title:\*\*\s*(?P<title>.+?)\s*\n"
    r"\*\*Label:\*\*\s*(?P<label>.+?)\s*\n"
    r"\*\*Description:\*\*\s*\n(?P<description>.*?)(?=\n### GITLAB ISSUE:|\Z)",
    re.DOTALL,
)


def parse_issues(response_text: str) -> list[dict]:
    issues = []
    for m in ISSUE_PATTERN.finditer(response_text):
        title = m.group("title").strip()
        label = m.group("label").strip()
        description = m.group("description").strip()
        issues.append({"title": title, "label": label, "description": description})
    return issues
