# t-shirt size framework

An AI-coding workflow framework that enforces strict phase progression (spec → tasks → inject standards → implement → verify → sync) and a living standards system. Works across Claude Code, Cursor, and Codex CLI.

## Install (cross-tool setup)

The framework ships with neutral `skills/` and `agents/` directories — the single source of truth. Before first use, run the installer from the framework root to copy them into tool-specific locations:

```bash
./t-shirt-size-install.sh claude    # Claude Code  → .claude/skills/, .claude/agents/
./t-shirt-size-install.sh cursor    # Cursor       → .cursor/skills/, .cursor/agents/
./t-shirt-size-install.sh codex     # Codex CLI    → .agents/skills/
./t-shirt-size-install.sh all       # all three    (default if no target given)
```

Re-run `install.sh` whenever you edit anything under `skills/` or `agents/` — it replaces the tool-specific copies.

Treat `.claude/`, `.cursor/`, and `.agents/` as **generated output**: gitignore them if you don't want them in version control, commit them if you want zero-setup clones.

### What is already universal (no copy needed)

- `AGENTS.md` — runtime instructions for AI agents. Read natively by Claude Code, Cursor, and Codex (open format stewarded by Linux Foundation).
- `CLAUDE.md` — one-line stub (`@AGENTS.md`) that points Claude Code at AGENTS.md.
- `.ai/` — project workspace (specs, standards, guardrails). Not tool-specific.

### Cross-tool caveats

- **Cursor agents** use different frontmatter than Claude (no `tools:` field, different `model:` values). The installer copies them as-is; if a subagent doesn't delegate well in Cursor, adjust `.cursor/agents/<name>.md` manually.
- **Codex subagents** are TOML and user-level only (`~/.codex/agents/<name>.toml`, no project-level). The installer skips them. Translate manually if you need them in Codex.
- **Skill frontmatter** — fields like `allowed-tools` and `argument-hint` are Claude extensions. Cursor/Codex ignore unknown fields (no crash), so skills work everywhere; only permission pre-approval is Claude-specific.

## Next steps

1. Run `./t-shirt-size-install.sh` for your tool(s)
2. Open `AGENTS.md` and fill in the four placeholder sections: **Project Layout**, **Tech Stack**, **Commands**, **Where to Look**
3. Fill in `.ai/GUARDRAILS.md` with at least one project-specific BLOCK rule and your architectural decisions
4. Run `/discover-standards` to generate your first standards from your own codebase

From then on, `AGENTS.md` drives the workflow — see it for phase progression rules, task management, and the standards feedback loop.
