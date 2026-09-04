---
name: sync-standards
description: Post-implementation pattern discovery. Detects NEW patterns introduced during recent changes that aren't yet documented as standards. Run after /verify-standards, before commit, for M/L tasks.
disable-model-invocation: true
allowed-tools: Bash(git diff:*) Bash(git status:*) Read Write Edit Grep
---

Post-implementation pattern discovery. Detects **new patterns** introduced during implementation that aren't yet documented as standards.

## Setup Gate (run this FIRST — before anything else)

Before doing anything else, read `AGENTS.md` in the project root and check the sections: **Project Layout**, **Tech Stack**, **Commands**, **Where to Look**.

If ANY of them still contains `_(fill in)_` or an equivalent empty placeholder → **STOP immediately.**

Tell the user:

> "Your AGENTS.md setup is incomplete. Sections still marked `_(fill in)_`: [list them]. Fill them in by hand, then re-run `/sync-standards`. I will not proceed until they are filled, and I will not fill them for you — these values must come from you because they encode project-specific knowledge I cannot infer."

Do NOT proceed with the steps below. Do NOT offer to fill the sections yourself. Do NOT suggest values. Do NOT proceed even if the user insists.

Only if all four sections are filled in → continue to the Guidelines and Process below.

## Important Guidelines

- **Always use AskUserQuestion tool** when asking the user anything
- **Focus on what's NEW** — Don't re-discover existing standards
- **Threshold: 2+ occurrences** — A pattern used once is just code; used twice+ is a candidate for a standard

## When to Run

After implementation and verification. This is the **discovery step** in the feedback loop:

```
inject → implement → verify → ✅ DISCOVER-DELTA → update standards
```

## Difference from /discover-standards

| | /discover-standards | /sync-standards |
|---|---|---|
| **Scope** | Entire codebase or area | Only files changed in this session |
| **Goal** | Initial documentation of existing patterns | Catch new patterns from recent work |
| **When** | Start of project, new area exploration | After each M/L implementation |
| **Speed** | Slow (broad scan) | Fast (narrow scope) |

## Process

### Step 1: Identify Changed Files

Run `git diff --name-only` (staged + unstaged) to get changed files.

Also check `git diff --stat` to understand the size of changes.

If less than 3 files changed with minor modifications:
```
Small change detected (< 3 files, minor modifications).
Delta discovery works best with larger changes. Skip? (yes / run anyway)
```

### Step 2: Read the Index

Read `.ai/standards/index.yml` to know what's **already documented**.

### Step 3: Analyze Changed Code

Read all changed files. For each file, look for:

1. **New structural patterns** — New ways of organizing code not covered by existing standards
   - New file structures, module patterns, export conventions
   - New middleware patterns, decorator usage
   - New state management approaches

2. **New naming patterns** — Naming conventions that emerged
   - New prefixes/suffixes, new file naming schemes
   - New type naming patterns

3. **New integration patterns** — How new code talks to existing systems
   - New API call patterns, new data flow approaches
   - New error handling strategies

4. **New domain patterns** — Business logic patterns
   - New validation approaches, new data transformation patterns
   - New authorization patterns

### Step 4: Filter Against Existing Standards

For each potential pattern found:
- Check if it's already covered by an existing standard → **skip**
- Check if it **extends** an existing standard → **flag as update**
- Check if it's completely **new** → **flag as new standard**

### Step 5: Present Findings

Use AskUserQuestion:

```
I analyzed the changes and found these undocumented patterns:

### New Standards (not yet documented)
1. **[pattern-name]** — [one-line description]
   Found in: `file1.ts:20`, `file2.ts:45`
   Example: [short code snippet]

2. **[pattern-name]** — [one-line description]
   Found in: `file3.ts:10`
   Example: [short code snippet]

### Updates to Existing Standards
3. **api/error-handling** — New error code prefix `PAY_xxx` used for payments
   Found in: `routes/payments.ts:30`

### What should we document?
- "All of them"
- "Just 1 and 3"
- "None — these are one-off patterns"
```

### Step 6: Document Selected Patterns

For each selected pattern, follow a compressed version of the discover-standards loop:

1. **Ask one clarifying question** (the "why"):

```
For the [pattern-name] pattern:
Why this approach? (Or is this a one-off that shouldn't be standardized?)
```

2. **Draft the standard** (concise, following existing standard style)

3. **Confirm with user**

4. **Create or update the file** in `.ai/standards/[folder]/`

### Step 7: Update Index

For any new or updated standard files:

1. Read current `index.yml`
2. Add/update entries
3. Write the updated `index.yml`
4. Alphabetize by folder, then filename

### Step 8: Summary

```
Delta discovery complete:
- 📝 2 new standards created
- 🔄 1 existing standard updated
- ⏭️ 1 pattern skipped (one-off)

Standards index updated.

Feedback loop closed ✅
  inject → implement → verify → sync-standards → standards updated
```

## Staleness Detection (Bonus)

While analyzing changed files, also check:

- Did any changed file **contradict** an existing standard in a way that wasn't caught by /verify-standards?
- Are there standards that reference files/patterns that **no longer exist**?

If found, flag them:

```
⚠️ Potentially stale standards detected:
- **redux/token-refresh** — References `authMiddleware.ts` which was renamed to `auth.middleware.ts`

Update these? (yes / skip)
```

## Integration

- Run after `/verify-standards` in **M and L workflows**
- Optional for **S workflows** (small changes rarely introduce new patterns)
- Creates standards that are immediately available to `/inject-standards` in the next task
