# Intake

Captures brainstorm ideas from text files, extracts structured issues via AI, deduplicates against a GitLab Kanban board, and posts new ones. Phase 2 enriches raw ideas and builds prompts on demand.

## How it works

### Phase 1: Extraction
1. Drop `.txt` or `.md` files into `data/_intake/`
2. Run `python3 intake.py`
3. AI (Claude Sonnet) reads each file, extracts discrete ideas
4. Large files (>10K chars) are automatically chunked for reliable processing
5. Each idea is compared against existing GitLab issues (semantic dedup)
6. New ideas are posted as GitLab issues with labels
7. Processed files move to `data/_processed/`

### Phase 2: Backlog Processing
After Phase 1 completes, the pipeline automatically processes `Spark` issues:
1. Fetches all open `Spark` issues from GitLab
2. Sonnet enriches each with acceptance criteria, design notes, and open questions
3. Issues are relabeled `Spark` → `Shaped`
4. If an issue has `Prompt-Request` label, Opus builds the actual prompt and delivers it to Discord + Dropzone

### Label Flow
```
File drops → Sonnet extracts → Spark (+ Prompt-Request if detected) → GitLab
                                                                        ↓
Phase 2 picks up Spark issues → Sonnet enriches → Shaped
                                                    ↓ (if Prompt-Request)
                                              Opus builds prompt → Discord + Dropzone
```

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

# Live run — post to GitLab + enrich backlog
python3 intake.py

# Live run — skip Phase 2 backlog processing
python3 intake.py --skip-backlog
```

## Configuration

All config via environment variables or `.env` file:

| Variable | Required | Default |
|----------|----------|---------|
| `INTAKE_ANTHROPIC_API_KEY` | Yes | — |
| `INTAKE_MODEL` | No | `claude-sonnet-4-5-20250514` |
| `INTAKE_GITLAB_URL` | No | `https://gitlab.czechito.com` |
| `INTAKE_GITLAB_PROJECT` | No | `tcdz/workbench` |
| `INTAKE_GITLAB_PAT` | No | Reads from `~/.git-credentials` |
| `INTAKE_COS_DISCORD_WEBHOOK` | No | #chief-of-staff webhook |
| `INTAKE_DROPZONE_SCP_TARGET` | No | `ccagent@192.168.1.13:/volume1/public/dropzone/` |
| `INTAKE_DROPZONE_SSH_KEY` | No | `~/.ssh/cc-to-ds923` |

## Architecture

See `docs/design.md` for full design documentation.

## Files

| File | Purpose |
|------|---------|
| `intake.py` | Main orchestrator — Phase 1 extraction + Phase 2 dispatch |
| `ai_client.py` | Anthropic API wrapper — extraction, chunking, dedup, enrichment, prompt building |
| `config.py` | Environment variable loading and defaults |
| `parser.py` | Parse `### GITLAB ISSUE:` blocks from AI responses |
| `gitlab_client.py` | GitLab API — fetch, create, update issues |
| `discord_client.py` | Discord scraper for #intake channel |
| `delivery.py` | Prompt delivery — Discord webhook + Dropzone SCP |
| `backlog_processor.py` | Phase 2 — enrich Spark→Shaped, build prompts for Prompt-Request |
| `prompts/extraction.md` | Phase 1 extraction prompt (Sonnet) |
| `prompts/quick-idea.md` | Phase 1 quick-idea prompt for Discord messages |
| `prompts/enrichment.md` | Phase 2 enrichment prompt (Sonnet) |
| `prompts/prompt-builder.md` | Phase 2 prompt builder (Opus) |
