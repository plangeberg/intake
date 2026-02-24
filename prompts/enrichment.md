You are enriching a raw idea (labeled "Spark") into an actionable backlog item (labeled "Shaped") for Phil's project ecosystem.

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

## YOUR TASK

Take the issue title and current description below and enrich it into a well-structured, actionable backlog item. Your output replaces the issue's description entirely.

**Output format** (Markdown — this becomes the GitLab issue body):

```
## Summary
[1-2 paragraphs expanding on the idea. What is it? Why does it matter? What problem does it solve?]

## Acceptance Criteria
- [ ] [Specific, testable criterion]
- [ ] [Another criterion]
- [ ] [...]

## Design Notes
- [Key technical considerations]
- [Architecture decisions or constraints]
- [Dependencies on other projects/infrastructure]

## Open Questions
- [Anything that needs Phil's input before building]
- [Unknowns or trade-offs to resolve]

## Related
- [Any overlap with existing projects from the context above]
```

**Rules:**
- Don't invent requirements Phil didn't imply — flesh out what's there, don't add scope
- Keep acceptance criteria concrete and testable
- Flag overlaps with existing projects
- If the idea is too vague to enrich meaningfully, say so in Open Questions
- Output ONLY the Markdown content above — no preamble, no wrapper

---
ISSUE TO ENRICH:
