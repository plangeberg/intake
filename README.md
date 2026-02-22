# Intake

Captures brainstorm ideas from text files, extracts structured issues via AI, deduplicates against a GitLab Kanban board, and posts new ones.

## How it works

1. Drop `.txt` or `.md` files into `data/_intake/`
2. Run `python3 intake.py`
3. AI (Claude Haiku) reads each file, extracts discrete ideas
4. Each idea is compared against existing GitLab issues (semantic dedup)
5. New ideas are posted as GitLab issues with labels
6. Processed files move to `data/_processed/`

## Setup

```bash
# Clone
git clone https://gitlab.czechito.com/tcdz/intake.git
cd intake

# Install dependencies
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env — add your Anthropic API key

# Create data directories
mkdir -p data/_intake data/_processed data/_logs

# Optional: Set up Google Drive junction (Windows, one-time)
# mklink /J "E:\intake\data\_intake" "G:\My Drive\_intake"
```

## Usage

```bash
# Dry run — extract and parse but don't post to GitLab
python3 intake.py --dry-run

# Live run — post to GitLab
python3 intake.py
```

## Configuration

All config via environment variables or `.env` file:

| Variable | Required | Default |
|----------|----------|---------|
| `INTAKE_ANTHROPIC_API_KEY` | Yes | — |
| `INTAKE_MODEL` | No | `claude-haiku-4-5-20251001` |
| `INTAKE_GITLAB_URL` | No | `https://gitlab.czechito.com` |
| `INTAKE_GITLAB_PROJECT` | No | `tcdz/workbench` |
| `INTAKE_GITLAB_PAT` | No | Reads from `~/.git-credentials` |

## Roadmap

- [ ] Discord scraper — read quick ideas from a private Discord channel
- [ ] Label matcher — AI matches ideas to existing Kanban labels
- [ ] Scheduler — run pipeline on a timer
- [ ] Discord notifier — post summary after new ideas are created
- [ ] Containerization
