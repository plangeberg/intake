"""Configuration loading from environment variables."""

import os
import sys
from pathlib import Path

# Load .env file if python-dotenv is available, otherwise parse manually
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    env_path = Path(__file__).parent / ".env"
    if env_path.exists():
        for line in env_path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                key, _, value = line.partition("=")
                os.environ.setdefault(key.strip(), value.strip())

APP_DIR = Path(__file__).parent


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
MODEL = os.environ.get("INTAKE_MODEL", "claude-haiku-4-5-20251001")
GITLAB_URL = os.environ.get("INTAKE_GITLAB_URL", "https://gitlab.czechito.com").rstrip("/")
GITLAB_PROJECT = os.environ.get("INTAKE_GITLAB_PROJECT", "tcdz/workbench")

# Paths — all default relative to APP_DIR
INTAKE_DIR = Path(os.environ.get("INTAKE_FOLDER", str(APP_DIR / "data" / "_intake")))
PROCESSED_DIR = Path(os.environ.get("INTAKE_PROCESSED_FOLDER", str(APP_DIR / "data" / "_processed")))
LOG_DIR = Path(os.environ.get("INTAKE_LOG_DIR", str(APP_DIR / "data" / "_logs")))
PROMPT_FILE = Path(os.environ.get("INTAKE_PROMPT_FILE", str(APP_DIR / "prompts" / "extraction.md")))
