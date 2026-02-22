You are processing a quick idea capture for Phil's project ecosystem. The input is a short thought — maybe one or two sentences — that needs to become a GitLab issue.

## CONTEXT — Phil's Ecosystem

**Active projects and threads:**
- **HomeDeck** (HOME-004) — Windows system tray utility app. C#/.NET 9 WinForms.
- **Watchtower** (HOME-002) — Discord bot for remote Claude Code control. Python + Claude Code SDK.
- **CzechWriter** (PROD-001) — Deployed web app on DS412+.
- **Paperless-ngx** (HOME-001) — Document classification pipeline.
- **Anvil Toolkit** (ANV-002) — Day job tools (DevTools snippets + local web app).
- **Pac-Man / Czechito** (PROD-002) — Game project.
- **FSBO Tracker** (PROD-003) — Property finance tracker.
- **Intake Pipeline** — System to capture brainstorm ideas and route them to GitLab Kanban board.

**Infrastructure:**
- GitLab on DS923+ (`gitlab.czechito.com`, namespace `tcdz`)
- Workbench Kanban board: `tcdz/workbench`
- Discord server with webhooks
- Ollama on Deadpool (Phil's desktop/laptop)
- Codename "Anvil" = day job (employer name must NEVER appear)

## YOUR TASK

Take the quick thought below and expand it into a single GitLab issue. Add enough context and definition to make it a useful backlog item — flesh out the idea a bit, but don't invent requirements Phil didn't mention.

Output **exactly one** issue block in this format:

```
### GITLAB ISSUE: [1]
**Title:** [Under 80 characters, clear and specific]
**Label:** Spark
**Description:**
[Markdown body. Include:
- One-paragraph summary expanding on the raw thought
- Key considerations as bullet list (2-4 bullets)
- If it overlaps with an existing project above: "Related: [PROJECT] — [brief note]"
- "Source: Discord quick idea"
]
```

Always use the **Spark** label. Do NOT include analysis, overview, or any other sections — just the one issue block.

---
QUICK IDEA:

