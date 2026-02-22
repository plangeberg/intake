=== SETUP (edit this section before each use) ===
Data source: [Either paste the transcript/text below the line at the bottom, OR specify the filename(s) here, e.g., "idea-001.txt"]
===================================================

## CONTEXT — Phil's Ecosystem

You are processing ideas for Phil's personal project ecosystem. Knowing this context helps you categorize ideas and spot overlaps with existing work.

**Active projects and threads:**
- **HomeDeck** (HOME-004) — Windows system tray utility app. C#/.NET 9 WinForms. Has: theme system, global hotkey, cursor-follow flyout, path flipper, pinned folders, ping monitor. Location: `home/projects/HomeDeck/`
- **Watchtower** (HOME-002) — Discord bot for remote Claude Code control. Python + Claude Code SDK. Location: `home/scripts/python/watchtower/`
- **CzechWriter** (PROD-001) — Deployed web app on DS412+. Location: `czechsuma-labs/czechwriter/`
- **Paperless-ngx** (HOME-001) — Document classification pipeline. Location: `home/scripts/python/paperless-classify/`
- **Anvil Toolkit** (ANV-002) — Day job tools (DevTools snippets + local web app). Location: `anvil/toolkit/`
- **Pac-Man / Czechito** (PROD-002) — Game project. Location: `czechito-labs/pacman/`
- **FSBO Tracker** (PROD-003) — Property finance tracker. Location: `czechsuma-labs/fsbo-tracker/`
- **Intake Pipeline** (designing now) — System to capture brainstorm ideas from Grok conversations and route them to GitLab Kanban board.

**Infrastructure:**
- GitLab on DS923+ (`gitlab.czechito.com`, namespace `tcdz`)
- Workbench Kanban board: `tcdz/workbench` — the destination for all ideas
- Discord server "deadpool-relay" with webhooks
- Ollama on Deadpool (Phil's desktop/laptop)
- Codename "Anvil" = day job (employer name must NEVER appear)

**If an idea overlaps with an existing project above, note it.** Don't discard it — just flag: "Overlaps with [PROJECT]" so Phil can decide whether to merge or keep separate.

---

## INSTRUCTIONS

I'm giving you a raw conversation transcript between me and AI assistants. This transcript was generated via speech-to-text, so there are two layers of issues to deal with:

### LAYER 1 — TRANSCRIPTION ERRORS
The human side of the conversation was spoken aloud and transcribed automatically. This means:
- Words may be mistranscribed (e.g., "cloud" instead of "Claude", "Grock" instead of "Grok", "campaign" instead of "Kanban")
- Words that were slurred together may have been picked up as wrong words entirely
- Homophones or similar-sounding words may be swapped
- Technical terms, app names, or proper nouns are especially likely to be wrong

As you read, use context to mentally correct these errors. Don't get thrown off by a word that doesn't make sense — figure out what was probably actually said based on the surrounding context.

### LAYER 2 — CONVERSATIONAL NOISE
The conversation is very informal and human-like. It contains stutters, repetition, tangents, filler words, incomplete thoughts, and casual back-and-forth. Cut through all of that to find the substance.

### DATA SOURCE
- If a filename is specified in the SETUP section above, that file contains the raw transcript to analyze. This prompt file contains only instructions.
- If no filename is specified, the raw transcript is pasted below the divider at the bottom of this prompt.

---

## YOUR TASK

Go through the entire transcript and identify every distinct idea, concept, project, or actionable item discussed. For each one, produce **two outputs**: an analysis block and a GitLab-ready issue.

### Output Part 1: Analysis (for Phil's review)

For each idea:

1. Give it a clear, concise title
2. Write a clean summary of what the idea/project actually is
3. List any specific details, requirements, or decisions that were made about it
4. List any action items or next steps that were discussed
5. Note any unresolved questions or open decisions
6. **Flag overlaps** with existing projects listed in the CONTEXT section above

Group related items together under the same idea — don't split one concept into multiple entries just because it was discussed at different points in the conversation.

Ignore completely:
- Small talk, greetings, filler
- Repeated or restated versions of the same point (consolidate into one)
- Conversational noise (stutters, corrections, "um", "like", etc.)
- Meta-discussion about the conversation itself
- Troubleshooting tangents (e.g., debugging a tool mid-conversation) unless they produce a distinct idea

### Output Part 2: GitLab Issues (ready to post)

For each idea, also produce a GitLab-ready issue block in this exact format:

```
### GITLAB ISSUE: [number]
**Title:** [Under 80 characters, clear and specific]
**Label:** [One of: Spark, Shaped, Ready, Building, Graduated]
**Description:**
[Markdown body. Include:
- One-paragraph summary
- Key details as bullet list
- Open questions if any
- "Source: [filename or 'voice transcript YYYY-MM-DD']"
- If overlaps: "Related: [PROJECT] — [brief note]"
]
```

**Label guidance:**
- **Spark** — Raw idea, just captured. Not fleshed out yet. (DEFAULT — use this unless the conversation clearly resolved the what AND why)
- **Shaped** — Thought through enough to build. Has a clear what and why.
- **Ready** — Spec'd and ready to pull into a build session. (Rare from a brain dump — only if very detailed)

Most ideas from a brain dump will be **Spark**. Only upgrade if the conversation genuinely fleshed it out.

---

## END SECTIONS

At the end, provide:

1. **Overview** — All ideas found with a one-line description each, so Phil can see everything at a glance.

2. **Overlap Report** — Any ideas that overlap with existing projects. Format: "Idea [N] overlaps with [PROJECT] — [what to consider]"

3. **Transcription Notes** — Words or phrases you believe were mistranscribed and what you interpreted them as, so Phil can verify your corrections.

---
RAW TRANSCRIPT (if not using a separate file):

