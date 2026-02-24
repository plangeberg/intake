"""Phase 2 backlog processor — enrich Spark issues, build prompts for Prompt-Request issues."""

from config import ENRICHMENT_PROMPT_FILE, PROMPT_BUILDER_FILE, log
from ai_client import enrich_issue, build_prompt
from gitlab_client import fetch_issues_by_label, update_issue
from delivery import deliver_prompt


def _load_prompt(path) -> str:
    """Load a prompt file, returning empty string if not found."""
    if not path.exists():
        log(f"  Warning: Prompt file not found: {path}")
        return ""
    return path.read_text(encoding="utf-8")


def _build_and_deliver_prompt(prompt_builder_prompt: str, iid, title: str, description: str) -> bool:
    """Build a prompt with Sonnet and deliver to Discord + Dropzone. Returns True on success."""
    if not prompt_builder_prompt:
        log(f"  Warning: Prompt builder prompt not found — skipping prompt build for #{iid}")
        return False

    log(f"  Building prompt for #{iid}: {title}")
    try:
        prompt_text = build_prompt(prompt_builder_prompt, title, description)
        result = deliver_prompt(title, prompt_text)
        discord_status = "ok" if result["discord"] else "failed"
        dropzone_status = "ok" if result["dropzone"] else "failed"
        log(f"  Prompt delivered — Discord: {discord_status}, Dropzone: {dropzone_status}")
        return result["discord"] or result["dropzone"]
    except Exception as exc:
        log(f"  ERROR: Could not build prompt for #{iid}: {exc}")
        return False


def run_backlog_processor(pat: str) -> None:
    """Process backlog: enrich Spark→Shaped, build prompts for any Prompt-Request issues."""
    prompt_builder_prompt = _load_prompt(PROMPT_BUILDER_FILE)

    # Step 1: Enrich Spark issues
    enrichment_prompt = _load_prompt(ENRICHMENT_PROMPT_FILE)
    spark_issues = fetch_issues_by_label(pat, "Spark") if enrichment_prompt else []

    if spark_issues:
        log(f"Phase 2: Enriching {len(spark_issues)} Spark issue(s)...")
        for issue in spark_issues:
            iid = issue["iid"]
            title = issue["title"]
            description = issue.get("description", "")
            labels = issue.get("labels", [])

            log(f"  Enriching #{iid}: {title}")

            try:
                enriched = enrich_issue(enrichment_prompt, title, description)
            except Exception as exc:
                log(f"  ERROR: Could not enrich #{iid}: {exc}")
                continue

            new_labels = [l for l in labels if l != "Spark"] + ["Shaped"]
            update_data = {
                "description": enriched,
                "labels": ",".join(new_labels),
            }

            if not update_issue(pat, iid, update_data):
                continue

            if "Prompt-Request" in labels:
                _build_and_deliver_prompt(prompt_builder_prompt, iid, title, enriched)
    else:
        log("Phase 2: No Spark issues to enrich.")

    # Step 2: Build prompts for any Prompt-Request issues that are already Shaped but not yet delivered
    prompt_request_issues = fetch_issues_by_label(pat, "Prompt-Request")
    # Filter to only Shaped issues (Spark ones were handled above)
    pending = [i for i in prompt_request_issues if "Shaped" in i.get("labels", []) and "Prompt-Delivered" not in i.get("labels", [])]

    if pending:
        log(f"Phase 2: Building prompts for {len(pending)} Prompt-Request issue(s)...")
        for issue in pending:
            iid = issue["iid"]
            title = issue["title"]
            description = issue.get("description", "")
            labels = issue.get("labels", [])

            delivered = _build_and_deliver_prompt(prompt_builder_prompt, iid, title, description)

            # Mark as delivered so we don't rebuild next run — only if it actually worked
            if delivered:
                new_labels = labels + ["Prompt-Delivered"]
                update_issue(pat, iid, {"labels": ",".join(new_labels)})
    else:
        log("Phase 2: No pending Prompt-Request issues.")

    log("Phase 2 complete.")
