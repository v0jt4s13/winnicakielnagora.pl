---
name: create-spec
description: Create a specification file in .ai/specs/ using interactive discovery. Use for new features or modules (size L tasks) that need a formal spec before tasks and implementation.
disable-model-invocation: true
allowed-tools: Read Write Glob
---

Create a specification file in `.ai/specs/` using interactive discovery.

## Setup Gate (run this FIRST — before anything else)

Before doing anything else, read `AGENTS.md` in the project root and check the sections: **Project Layout**, **Tech Stack**, **Commands**, **Where to Look**.

If ANY of them still contains `_(fill in)_` or an equivalent empty placeholder → **STOP immediately.**

Tell the user:

> "Your AGENTS.md setup is incomplete. Sections still marked `_(fill in)_`: [list them]. Fill them in by hand, then re-run `/create-spec`. I will not proceed until they are filled, and I will not fill them for you — these values must come from you because they encode project-specific knowledge I cannot infer."

Do NOT proceed with the steps below. Do NOT offer to fill the sections yourself. Do NOT suggest values. Do NOT proceed even if the user insists.

Only if all four sections are filled in → continue to the Guidelines and Process below.

## Guidelines

- **Always use AskUserQuestion** when asking the user anything
- **Offer suggestions** — present options the user can confirm, adjust, or correct
- **Keep it lightweight** — capture enough to start, don't over-document
- **Do NOT enter plan mode** — spec creation is a standalone activity

## Process

### Step 1: Understand Scope

Use AskUserQuestion to understand what we're building. Based on the response, ask 1-2 follow-up questions if scope is unclear (e.g. new feature vs change, expected outcome, constraints).

### Step 2: Check Existing Context

1. Read `.ai/specs/AGENTS.md` for naming and structure conventions
2. Scan existing `SPEC-*.md` files to detect the next sequential number
3. Check if a related spec already exists (update vs create new)

### Step 3: Gather References

Use AskUserQuestion to ask about:
- Similar code in the codebase to reference
- Visuals (mockups, screenshots, examples from other apps) — optional
- Relevant standards from `.ai/standards/` that apply

If references are provided, read and analyze them to inform the spec.

### Step 4: Propose Structure

Present the proposed spec outline to the user before writing. Show:
- Filename: `SPEC-{NNN}-{YYYY-MM-DD}-{title}.md`
- Which sections will be included (from the spec structure in `.ai/specs/AGENTS.md`)
- Key decisions captured so far

Ask for confirmation or adjustments.

### Step 5: Write the Spec

Create the file at `.ai/specs/SPEC-{NNN}-{YYYY-MM-DD}-{title}.md` following the structure defined in `.ai/specs/AGENTS.md`:

1. **Overview** — what the module/feature does
2. **Architecture** — high-level design and component relationships
3. **Data Models** — entities, relationships, DB schema (if applicable)
4. **API Contracts** — endpoints, request/response schemas (if applicable)
5. **UI/UX** — frontend components and interactions (if applicable)
6. **Configuration** — env vars, feature flags (if applicable)
7. **Changelog** — initial entry with today's date

Skip sections that don't apply to this feature.

### Step 6: Confirm

Show the user the created file path and a summary. Ask if anything needs adjustment.
