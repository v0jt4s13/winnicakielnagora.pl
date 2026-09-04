---
name: verify-standards
description: Post-implementation check. Lints/formats changed files, then verifies the code follows standards injected at task start. Run after implementation, before commit, in all workflow sizes (S/M/L).
disable-model-invocation: true
allowed-tools: Bash(git diff:*) Bash(git status:*) Bash(biome *) Bash(bunx biome *) Bash(eslint *) Bash(npx eslint *) Bash(prettier *) Bash(npx prettier *) Bash(ruff *) Bash(dotnet format:*) Bash(gofmt *) Bash(rustfmt *) Read Edit
---

Post-implementation check. Verifies that changed code follows the standards injected at the start of the task.

## Setup Gate (run this FIRST — before anything else)

Before doing anything else, read `AGENTS.md` in the project root and check the sections: **Project Layout**, **Tech Stack**, **Commands**, **Where to Look**.

If ANY of them still contains `_(fill in)_` or an equivalent empty placeholder → **STOP immediately.**

Tell the user:

> "Your AGENTS.md setup is incomplete. Sections still marked `_(fill in)_`: [list them]. Fill them in by hand, then re-run `/verify-standards`. I will not proceed until they are filled, and I will not fill them for you — these values must come from you because they encode project-specific knowledge I cannot infer."

Do NOT proceed with the steps below. Do NOT offer to fill the sections yourself. Do NOT suggest values. Do NOT proceed even if the user insists.

Only if all four sections are filled in → continue to the Guidelines and Process below.

## Important Guidelines

- **Always use AskUserQuestion tool** when asking the user anything
- **Be specific** — Point to exact lines/files that deviate, not vague warnings
- **Distinguish intentional vs accidental** — Not every deviation is a bug; some are deliberate decisions

## When to Run

After implementation, before commit. This is the **verification step** in the feedback loop:

```
inject → implement → ✅ VERIFY → sync-standards
```

## Process

### Step 1: Identify What to Verify

Two sources of truth:

**A) Standards injected in this session:**
- Check conversation history for `/inject-standards` output
- Note which standard files were loaded

**B) If no injection found**, use AskUserQuestion:

```
I don't see standards injected earlier in this session.

1. **Auto-detect** — I'll look at changed files and match relevant standards from the index
2. **Specify** — Tell me which standards to verify against

Which approach?
```

### Step 1.5: Lint & Format Changed Files

Before verification, auto-fix formatting issues **only in changed files** — using the project's linter/formatter as defined in `AGENTS.md` under **Commands** (e.g. `biome check --write`, `eslint --fix`, `prettier --write`, `ruff check --fix`, `dotnet format`, `gofmt -w`, `rustfmt`).

1. Get list of changed files:
   ```bash
   git diff --name-only HEAD
   ```

2. Filter to files the project's linter/formatter understands.

3. Run the linter/formatter only on those files. Prefer running from the closest package directory if the project is a monorepo (one config per package). Examples:
   ```bash
   # JS/TS monorepo with Biome:
   cd packages/<pkg> && bunx biome check --write src/path/to/changed-file.tsx

   # JS/TS with ESLint + Prettier:
   npx eslint --fix path/to/changed-file.ts && npx prettier --write path/to/changed-file.ts

   # Python:
   ruff check --fix path/to/changed-file.py

   # .NET:
   dotnet format --include path/to/changed-file.cs
   ```

**Important:**
- Pass only changed files as arguments — never re-lint the whole repo during verification.
- If the project uses per-package configs (monorepo), run the tool from the matching package root so its config is picked up.
- Skip packages / files the linter does not cover.

If lint fails with errors that can't be auto-fixed, report them before proceeding.

### Step 2: Identify Changed Files

Run `git diff --name-only` (staged + unstaged) to get the list of files changed in this session.

If no changes detected:
```
No file changes detected. Nothing to verify.
```

### Step 3: Read Standards and Changed Files

1. Read each relevant standard file from `.ai/standards/`
2. Read each changed file
3. Extract the **rules** from each standard (the concrete do/don't patterns)

### Step 4: Compare and Report

For each standard, check the changed files against its rules. Present findings using AskUserQuestion:

```
## Verification Report

### ✅ Passes
- **api/route-structure** — Route export pattern followed correctly in `{changed-route-file}`
- **global/naming-conventions** — All new files follow naming conventions

### ⚠️ Deviations Found
1. **api/error-handling** @ `{file}:{line}`
   - Standard says: "Log full error server-side, return safe message to client"
   - Found: Raw error message returned to client

2. **state/api-patterns** @ `{file}:{line}`
   - Standard says: "Use tag-based cache invalidation"
   - Found: Manual cache reset instead of tag invalidation

### How to handle deviations?
```

Options for each deviation:

```
For each deviation, choose:

1. **Fix code** — Update the code to match the standard
2. **Update standard** — The code is correct, standard needs updating
3. **Exception** — Intentional deviation, document why
4. **Ignore** — Not relevant to this change
```

### Step 5: Execute Chosen Actions

**Fix code:**
- Make the code change to align with the standard
- Show the diff for confirmation

**Update standard:**
- Read the current standard file
- Propose an update that reflects the new pattern
- Use AskUserQuestion to confirm the update
- Write the updated standard
- Update `index.yml` description if meaning changed

**Exception:**
- Ask for a one-line reason
- Add a comment in the code: `// Exception: [reason] — deviates from [standard-name]`

**Ignore:**
- No action needed

### Step 6: Summary

```
Verification complete:
- ✅ 3 standards passed
- 🔧 1 deviation fixed in code
- 📝 1 standard updated
- ⚡ 1 documented exception

Ready to commit? Consider running /sync-standards to check for new patterns worth documenting.
```

## Key Principle

Verification is a **two-way gate**:
- Code that doesn't match standards → fix the code OR update the standard
- Never silently ignore — every deviation gets an explicit decision

This is what makes the feedback loop work. Standards evolve with the codebase.

## Integration

- Run after implementation in **all workflow sizes** (S, M, L)
- Feeds into `/sync-standards` for the full feedback loop
- Updates flow back into `.ai/standards/` keeping them current
