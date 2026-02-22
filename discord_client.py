"""Discord integration — scrape #intake messages, notify #backlog."""

import requests

from config import DISCORD_BOT_TOKEN, DISCORD_CHANNEL_ID, INTAKE_DIR, log


DISCORD_API = "https://discord.com/api/v10"


def discord_enabled() -> bool:
    return bool(DISCORD_BOT_TOKEN and DISCORD_CHANNEL_ID)


def scrape_intake_channel() -> int:
    """Fetch messages from #intake, save as .txt files, delete from Discord.

    Returns the number of messages scraped.
    """
    if not discord_enabled():
        return 0

    headers = {"Authorization": f"Bot {DISCORD_BOT_TOKEN}"}
    url = f"{DISCORD_API}/channels/{DISCORD_CHANNEL_ID}/messages"
    params = {"limit": 50}

    try:
        resp = requests.get(url, headers=headers, params=params, timeout=15)
        if resp.status_code != 200:
            log(f"  Warning: Discord API returned {resp.status_code} fetching messages")
            return 0
        messages = resp.json()
    except requests.RequestException as exc:
        log(f"  Warning: Could not fetch Discord messages: {exc}")
        return 0

    if not messages:
        return 0

    INTAKE_DIR.mkdir(parents=True, exist_ok=True)
    scraped = 0

    for msg in messages:
        content = msg.get("content", "").strip()
        msg_id = msg.get("id", "unknown")

        if not content:
            continue

        # Save message as a text file
        filepath = INTAKE_DIR / f"discord-{msg_id}.txt"
        try:
            filepath.write_text(content, encoding="utf-8")
        except Exception as exc:
            log(f"  Warning: Could not write {filepath.name}: {exc}")
            continue

        # Delete message from Discord
        delete_url = f"{DISCORD_API}/channels/{DISCORD_CHANNEL_ID}/messages/{msg_id}"
        try:
            del_resp = requests.delete(delete_url, headers=headers, timeout=15)
            if del_resp.status_code == 204:
                log(f"  Scraped and deleted Discord message {msg_id}")
                scraped += 1
            else:
                log(f"  Warning: Could not delete Discord message {msg_id} (HTTP {del_resp.status_code})")
                # File was saved — it'll be processed. Message stays in Discord (dupe next run, but harmless).
                scraped += 1
        except requests.RequestException as exc:
            log(f"  Warning: Could not delete Discord message {msg_id}: {exc}")
            scraped += 1

    return scraped


