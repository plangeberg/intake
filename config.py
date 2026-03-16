"""Configuration loading from environment variables."""

import os
import sys
from pathlib import Path

# Resolve .env file: INTAKE_ENV_FILE env var → APP_DIR/.env fallback
APP_DIR = Path(__file__).parent
_env_file = Path(os.environ.get("INTAKE_ENV_FILE", str(APP_DIR / ".env")))

try:
    from dotenv import load_dotenv
    load_dotenv(_env_file)
except ImportError:
    if _env_file.exists():
        for line in _env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

# Data root: INTAKE_DATA_ROOT env var → APP_DIR/data fallback
DATA_ROOT = Path(os.environ.get("INTAKE_DATA_ROOT", str(APP_DIR / "data")))


def log(msg: str) -> None:
    from datetime import datetime
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{ts}] {msg}", flush=True)


def _require(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        print(f"ERROR: Missing required env var: {name}", file=sys.stderr)
        print("Copy .env.example to .env and fill it in.", file=sys.stderr)
        sys.exit(1)
    return value


# Required
ANTHROPIC_API_KEY = _require("INTAKE_ANTHROPIC_API_KEY")

# Optional with defaults
MODEL = os.environ.get("INTAKE_MODEL", "claude-sonnet-4-6")
GITLAB_URL = os.environ.get("INTAKE_GITLAB_URL", "https://gitlab.czechito.com").rstrip("/")
GITLAB_PROJECT = os.environ.get("INTAKE_GITLAB_PROJECT", "tcdz/workbench")

# Paths — all default relative to DATA_ROOT (set above from INTAKE_DATA_ROOT or APP_DIR/data)
INTAKE_DIR = Path(os.environ.get("INTAKE_FOLDER", str(DATA_ROOT / "_intake")))
PROCESSED_DIR = Path(os.environ.get("INTAKE_PROCESSED_FOLDER", str(DATA_ROOT / "_processed")))
LOG_DIR = Path(os.environ.get("INTAKE_LOG_DIR", str(DATA_ROOT / "_logs")))
FAILED_DIR = Path(os.environ.get("INTAKE_FAILED_FOLDER", str(DATA_ROOT / "_failed")))
PROMPT_FILE = Path(os.environ.get("INTAKE_PROMPT_FILE", str(APP_DIR / "prompts" / "extraction.md")))
QUICK_PROMPT_FILE = Path(os.environ.get("INTAKE_QUICK_PROMPT_FILE", str(APP_DIR / "prompts" / "quick-idea.md")))

# Discord — all optional (disabled if token not set)
DISCORD_BOT_TOKEN = os.environ.get("INTAKE_DISCORD_BOT_TOKEN", "")
DISCORD_CHANNEL_ID = os.environ.get("INTAKE_DISCORD_CHANNEL_ID", "")
DISCORD_BACKLOG_WEBHOOK = os.environ.get("INTAKE_DISCORD_BACKLOG_WEBHOOK", "")

# Delivery — Discord webhook + Dropzone SCP
COS_DISCORD_WEBHOOK = os.environ.get(
    "INTAKE_COS_DISCORD_WEBHOOK",
    "https://discord.com/api/webhooks/1474639674478952739/5apeBluL80iW956ckoKCZWA7fw059Cn3LWPcaWqZijwS7qBE9SpnX7LWOI8Cn9V0PzuA",
)
DROPZONE_SCP_TARGET = os.environ.get(
    "INTAKE_DROPZONE_SCP_TARGET",
    "ccagent@192.168.1.13:/volume1/public/dropzone/",
)
DROPZONE_SSH_KEY = os.environ.get("INTAKE_DROPZONE_SSH_KEY", str(Path.home() / ".ssh" / "cc-to-ds923"))

# Prompt files — Phase 2
ENRICHMENT_PROMPT_FILE = Path(os.environ.get(
    "INTAKE_ENRICHMENT_PROMPT_FILE", str(APP_DIR / "prompts" / "enrichment.md")
))
PROMPT_BUILDER_FILE = Path(os.environ.get(
    "INTAKE_PROMPT_BUILDER_FILE", str(APP_DIR / "prompts" / "prompt-builder.md")
))
