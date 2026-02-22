# Intake Pipeline — Idea Capture System

> **Status**: MVP ready to build. Full vision documented below.
> **Date**: 2026-02-21
> **Goal**: Capture brainstorming output and turn it into actionable GitLab issues automatically
> **Prompt v1**: `brain/handoffs/to-cos/prompt.md`
> **Prompt v2**: `brain/handoffs/to-cos/prompt-v2.md`
> **Test data**: `brain/handoffs/to-cos/idea-001.txt` (raw), `idea-001-analysis.md` (v1 output), `brain/ideas/GroksIdeas.txt` (raw)

---

## MVP — Step 1: One Script, One Scheduled Task

The simplest version that works. Build this first, iterate later.

```
_intake folder (Google Drive, synced locally)
     │
     │  (scheduled task checks for new files every 5 min)
     ▼
Python script: intake-processor.py
     │
     ├─ Read file contents
     ├─ Call Anthropic API (Haiku or Sonnet) with prompt-v2
     ├─ Parse GITLAB ISSUE blocks from response
     ├─ POST each issue to GitLab API (tcdz/workbench)
     ├─ If GitLab returns 201 → move file to _processed/
     └─ If GitLab fails → leave file in _intake for retry
```

### What's Needed to Build the MVP

**Phil actions:**
- [ ] Set up Anthropic API account — fund with $5-10 to start. Get API key.
- [ ] Create `_intake` folder in Google Drive (confirm it syncs locally to a known path)
- [ ] Create `_processed` folder alongside it

**CoS builds:**
- [ ] `intake-processor.py` — the one script (~100 lines)
- [ ] Config: API key (env var), GitLab PAT (env var), intake folder path, processed folder path, prompt file path
- [ ] Windows Task Scheduler entry (or cron) to run every 5 min
- [ ] Test with `idea-001.txt` and `GroksIdeas.txt`

### MVP Cost Model
- **Anthropic API** (separate from Max plan)
- Haiku 4.5: ~$0.03 per brain dump
- Sonnet 4.6: ~$0.12 per brain dump
- 10 dumps/month = $0.30 - $1.20/month
- Max plan ($200/mo) stays reserved for interactive CoS/Opus sessions

### Why separated billing matters
- Max 20x has a token ceiling — every token burned on grunt work is a token Phil can't use for interactive sessions
- API account = automated workhorse budget, separate from conversation budget
- Opens the door: Paperless classification and future batch processing can also move to API

---

## The Problem

Phil brainstorms with Grok (voice — Cybertruck, phone, desktop) and generates ideas during commutes and downtime. Those ideas need to land somewhere structured, not get lost in chat history. The system should be low-friction, AI-flexible, and not depend on Claude to run.

## Decisions Made

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Brainstorming tool | **Grok** | Voice-activated from Cybertruck steering wheel, phone, desktop. Perfect for commute brainstorming. |
| Destination | **GitLab Kanban board (`tcdz/workbench`)** | Natural flow: idea → plan → build. Already in use. No need to fragment across projects. |
| NOT using THREADS.md | Confirmed | THREADS.md is for active work tracking, not idea intake. |
| Real-time requirement | **None** | Scheduled job is fine. No need for an always-on listener. |
| Cloud-independent | **Yes** | Claude builds it, but the system runs without Claude. Standard scripts, APIs, cron. |
| AI-flexible | **Yes** | Should work if Phil swaps Claude for Gemini, Cursor, etc. later. |
| API billing | **Anthropic API (separate from Max)** | Max plan reserved for interactive sessions. API handles automated grunt work. |

## Full Pipeline Design (Future Vision)

### Pipeline A: Brain Dumps (primary)
```
Grok (car / phone / desktop)
     │
     │  (manual copy-paste — no Grok export API exists)
     ▼
Google Doc (one doc per brain dump, in designated folder)
     │
     │  (scheduled job via Google Docs/Drive API or MCP)
     ▼
Transcription step (AI applies prompt, extracts discrete ideas)
     │
     │  (GitLab API)
     ▼
tcdz/workbench Kanban board (one issue per idea, labeled)
     │
     │  (verification: issues confirmed on board)
     ▼
Google Doc deleted (cleanup)
```

### Pipeline B: Quick Ideas (secondary)
```
Phil has a quick thought
     │
     │  (types directly into Discord channel)
     ▼
Discord channel (private, for short ideas)
     │
     │  (scheduled scraper via Discord API)
     ▼
tcdz/workbench Kanban board (one issue per idea, default label)
```

### Why manual copy-paste from Grok?

- xAI has a Grok API, but it's for sending prompts — not accessing consumer conversation history from the car/phone app
- No known MCP server for Grok consumer conversations
- The manual step is small: copy conversation, paste into Google Doc

## Design Decisions (Continued)

### Google Docs Structure
- **One doc per brain dump** — not per conversation, not a rolling doc
- Multiple Grok conversations can go in the same doc (AIs can differentiate where one ends and another begins)
- Once consumed and **verified on GitLab Kanban**, the doc is **deleted**
- The scraper detects new content by the presence of a doc in the designated folder — doc exists = unprocessed

### Google Docs Integration
- Need a Google Docs/Drive MCP or API integration (service account, one-time setup)
- Phil has 2TB Google Drive available
- MCP = correct term. It's an adapter protocol connecting AI tools to external services.
- **MVP shortcut**: If Google Drive syncs to a local folder, no API/MCP needed — script reads from disk

### Transcription Step
- Must be done by an AI
- **Leading candidate: Claude Haiku 4.5 or Sonnet 4.6 via Anthropic API**
- **Alternative: Ollama** — runs locally on Deadpool, already used in Paperless classification. Simpler infra (no API key, no cost). Unknown: how smart it needs to be for this task.
- **Where it runs** depends on which AI: API = anywhere with internet; Ollama = Deadpool only
- Transcription prompt v2 at `brain/handoffs/to-cos/prompt-v2.md`

### Labeling / Categorization
- All new ideas start with a **default label** (e.g., `idea`, `intake`)
- Transcription step **attempts to match existing labels** on the board (similar to Paperless classification approach)
- If no match → generic label that means "raw thought, not actionable yet"
- Ideas with the default label are **off-limits for work** — they're just brainstorm output until Phil promotes them
- **Workbench labels**: Spark (raw), Shaped (clear what+why), Ready (spec'd), Building, Graduated
- Most brain dump ideas → **Spark** by default

### Two Input Pipelines
- **Google Docs** — Primary. For Grok brain dumps (long, conversational, multi-idea)
- **Discord** — Secondary. For quick one-off ideas that don't need AI brainstorming. Simple thought → straight to Kanban.
- Discord's 2000-char limit is fine for quick ideas. Not fine for Grok dumps.

### Transcription Prompt
- **v1**: `brain/handoffs/to-cos/prompt.md` — original, analysis-only output
- **v2**: `brain/handoffs/to-cos/prompt-v2.md` — adds ecosystem context, GitLab-ready issue blocks, overlap detection, label guidance
- v1 test: `idea-001.txt` → `idea-001-analysis.md` (5 ideas extracted by Sonnet 4.6)

### Ollama vs Claude for Transcription
- **Ollama does NOT run on DS923+** — not powerful enough. Runs on Deadpool (Phil's desktop/laptop).
- **DS923+ may not be beefy enough** for AI workloads in general. Phil is open to discussing a beefier server that can handle 2-3 AI agents concurrently. (Future discussion — not blocking this design.)
- **Claude Haiku/Sonnet via API**: smart enough, cheap, needs API account (separate from Max).
- **Decision**: Start with Haiku via API. Compare with Ollama later if desired.

### Google Drive Folder
- **Name**: `_intake` (underscore prefix — Phil's convention for frequently visited folders)
- Tilde (~) prefix doesn't play well on Linux, so underscore it is
- "Brain dumps" is technically accurate but Phil doesn't love it as a name

### Discord Channel for Quick Ideas
- **Dedicated channel** — e.g., `#intake` or `#brain-dump`
- Only Phil's idea messages go in there
- The scraper watches **only this one channel** for this purpose
- Separate from the existing `#overnight-updates` webhook channel

### Verification Before Deletion
- **Simple**: If the GitLab API POST succeeds, move source file to `_processed/` (archived, not deleted)
- No word-level or content-level verification needed
- The job knows if it successfully posted — that's enough

## Open Questions (Future — Not Blocking MVP)

### 1. Beefier server
- DS923+ can't run Ollama or heavy AI workloads. Deadpool can but it's Phil's daily driver.
- Is a dedicated compute box worth discussing? (Mini PC, old laptop repurposed, cloud VM, etc.)
- Not blocking — but affects where the transcription step runs long-term

### 2. Discord bot token (Pipeline B)
- Reading from Discord requires a bot (not just a webhook). Need to create a Discord bot and get a token.
- One-time setup, minimal permissions (read messages in one channel)
- Could potentially reuse the Watchtower bot with a new channel listener

### 3. Ollama comparison
- Once Anthropic API baseline is established, test same prompts against Ollama on Deadpool
- Compare quality and decide if Ollama is "good enough" for this task

## Full Component List (Future Vision)

> MVP only needs item 1. The rest are future additions.

1. **intake-processor.py** — Watches folder, calls AI, parses output, posts to GitLab, archives files. **THIS IS THE MVP.**
2. **Discord scraper** — Reads new messages from private channel via Discord API (Pipeline B)
3. **Label matcher** — Checks extracted ideas against existing Workbench labels, assigns match or default (could be part of the prompt or a separate step)
4. **Scheduler** — Windows Task Scheduler or cron on DS923+ to run pipeline periodically
5. **(Optional) Discord notifier** — Posts summary to Discord after new ideas are created ("3 new ideas added to Kanban")

## Not In Scope

- Changing the Grok brainstorming workflow
- Building a Grok API integration (doesn't exist for consumer history)
- Making Claude a runtime dependency
- Watchtower integration (unnecessary complexity for batch processing)
