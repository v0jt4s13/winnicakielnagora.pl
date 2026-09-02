# How a Standard Looks

> Reference format for standards files. **Delete this file** once you have your own standards. It is not read by any command — it exists only to show the shape of a well-written standard.

A standard documents **one rule or pattern** that AI agents should follow when writing code in this project. It must be short, scannable, and concrete. Every word you add costs tokens on every injection.

## Anatomy of a good standard

1. **One-line rule at the top** — what to do, before the why.
2. **Code example showing the rule in use** — "show, don't tell".
3. **Bullet points over paragraphs** — scannable beats prose.
4. **Exceptions documented** — agents will hit edge cases; be explicit.
5. **Skip the obvious** — don't re-explain what the code already makes clear.

## Minimal example (stack-neutral)

The file below is a realistic standard — short, rule-first, with one code example. Use this shape, regardless of whether your stack is Node, .NET, Rails, Go, Python, etc.

---

```markdown
# Commit Message Format

All commits use the Conventional Commits prefix:

`<type>(<scope>): <subject>`

- `type` — one of: feat, fix, refactor, docs, test, chore
- `scope` — the module or area (e.g. `auth`, `billing`, `api`)
- `subject` — imperative, lowercase, no trailing period

## Examples

feat(auth): add refresh token rotation
fix(billing): prevent double charge on retry
refactor(api): extract validation into middleware

## Exceptions

- Merge commits keep the default git message (no prefix)
- Revert commits use `revert:` as the type

## Why

Tooling (CHANGELOG generator, release automation) parses these prefixes.
```

---

## What to avoid

- **Long prose explanations** — if the rule needs three paragraphs, split it into multiple standards.
- **Documenting the obvious** — "use camelCase in JavaScript" is not a standard, the linter enforces it.
- **Mixing unrelated rules** — one concept per file. If you need two rules, write two files.
- **Copying another project's standards** — your standards must emerge from YOUR codebase via `/discover-standards`. Patterns that work for someone else's architecture will not fit yours.

## How standards are generated

Standards are written by running `/discover-standards` on your real code, not by hand-copying templates. The command interviews you about patterns it finds and writes standards that reflect your actual conventions.

Do NOT pre-populate `.ai/standards/` by hand. Start empty. Let the first `/discover-standards` pass produce the first 3-5 files. Extend from there.
