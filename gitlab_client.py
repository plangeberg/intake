"""GitLab API client — fetch issues, post issues, PAT resolution."""

import os
import urllib.parse
from pathlib import Path

import requests

from config import GITLAB_URL, GITLAB_PROJECT, log


def load_pat_from_credentials(gitlab_url: str) -> str | None:
    """
    Parse ~/.git-credentials for a line matching the GitLab host.
    Expected format: https://tcdz:<PAT>@gitlab.czechito.com
    """
    creds_path = Path.home() / ".git-credentials"
    if not creds_path.exists():
        return None

    parsed = urllib.parse.urlparse(gitlab_url)
    target_host = parsed.netloc

    try:
        for line in creds_path.read_text().splitlines():
            line = line.strip()
            if not line:
                continue
            p = urllib.parse.urlparse(line)
            if p.hostname == target_host and p.password:
                return p.password
    except Exception as exc:
        log(f"Warning: could not parse ~/.git-credentials: {exc}")

    return None


def resolve_pat() -> str:
    pat = load_pat_from_credentials(GITLAB_URL)
    if pat:
        return pat
    pat = os.environ.get("INTAKE_GITLAB_PAT")
    if pat:
        return pat
    raise RuntimeError(
        "GitLab PAT not found in ~/.git-credentials and INTAKE_GITLAB_PAT is not set."
    )


def fetch_existing_issues(pat: str) -> list[dict]:
    """Fetch all open issues from the GitLab project for dedup comparison."""
    encoded_project = urllib.parse.quote(GITLAB_PROJECT, safe="")
    url = f"{GITLAB_URL}/api/v4/projects/{encoded_project}/issues"
    headers = {"PRIVATE-TOKEN": pat}
    all_issues = []
    page = 1

    while True:
        params = {"state": "opened", "per_page": 100, "page": page}
        try:
            resp = requests.get(url, headers=headers, params=params, timeout=15)
            if resp.status_code != 200:
                log(f"  Warning: GitLab returned {resp.status_code} fetching issues page {page}")
                break
            batch = resp.json()
            if not batch:
                break
            for issue in batch:
                all_issues.append({
                    "iid": issue.get("iid"),
                    "title": issue.get("title", ""),
                    "labels": issue.get("labels", []),
                })
            page += 1
        except requests.RequestException as exc:
            log(f"  Warning: could not fetch issues page {page}: {exc}")
            break

    return all_issues


def post_issue(pat: str, issue: dict, dry_run: bool) -> bool:
    """POST one issue to GitLab. Returns True on success (or dry_run)."""
    encoded_project = urllib.parse.quote(GITLAB_PROJECT, safe="")
    url = f"{GITLAB_URL}/api/v4/projects/{encoded_project}/issues"
    headers = {"PRIVATE-TOKEN": pat, "Content-Type": "application/json"}
    payload = {
        "title": issue["title"],
        "description": issue["description"],
        "labels": issue["label"],
    }

    if dry_run:
        log(f"  [DRY RUN] Would POST: {issue['title']}")
        return True

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=15)
        if resp.status_code == 201:
            issue_data = resp.json()
            log(f"  Created GitLab issue #{issue_data.get('iid', '?')}: {issue['title']}")
            return True
        else:
            log(f"  ERROR: GitLab returned HTTP {resp.status_code} for '{issue['title']}': {resp.text[:200]}")
            return False
    except requests.RequestException as exc:
        log(f"  ERROR: Request failed for '{issue['title']}': {exc}")
        return False
