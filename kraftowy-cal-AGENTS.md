# Agents Guidelines

This project uses the **t-shirt size workflow** for AI-assisted coding. Agents should leverage strict phase progression and the standards system to keep the codebase consistent and safe to extend.

## ⚠️ Before you start — HARD STOP gate

**This is a blocking rule. No `/` command in this framework may execute while the sections below contain `_(fill in)_` or empty placeholders.**

The user must fill in (themselves, by hand) the following sections of this file:

- [ ] **Project Layout** (below) — high-level folder map
- [ ] **Tech Stack** (below) — runtime, framework, DB, linter
- [ ] **Commands** table (below) — dev, build, test, lint/format
- [ ] **Where to Look** table (bottom of this file) — delete rows that don't apply to your stack

And in `.ai/GUARDRAILS.md`:

- [ ] At least one project-specific BLOCK rule
- [ ] Your architectural decisions section

### Rule for agents

When any `/` command is invoked, your FIRST action is to read this file and check the four sections above.

- If ANY section still contains `_(fill in)_` or an equivalent empty placeholder → **STOP immediately**. Do not proceed with the command. Do not read other files. Do not offer alternative plans.
- Tell the user exactly which sections are empty and that you cannot continue until they fill them in.
- **Do NOT offer to fill them yourself.** Do NOT suggest values. Do NOT proceed even if the user insists — these values must come from the user because they encode project-specific knowledge the agent cannot infer.
- The only exception: reading this file to perform the gate check itself.

Once the sections are filled, the user can re-run the original command and it will proceed normally.

### Why

The framework is stack-agnostic (Node, .NET, Rails, Go, Python, Rust — all work identically). But every command downstream assumes these values are correct. If the agent auto-fills them, it will guess (e.g. "probably PostgreSQL") and the rest of the workflow will propagate those guesses. The gate forces the human to commit to a stack once, explicitly.

Then run `/discover-standards` on your codebase to generate your first standards. Do not copy standards from other projects — they must emerge from your own code.

## Workflow Orchestration

### 1. Specification and plan before coding

- Enter plan mode for non-trivial tasks (3+ steps or architectural decisions); if the task is to make the Specification - you skip the plan mode and start writing the specification directly to the file in the `.ai/specs` (details how to name file etc below),
- if there's an existing and comprehensive specification file you can skip the plan mode and proceed to task creation (the next workflow phase),
- new features should follow the specification file created in the planning phase, this step could be skipped for small improvements (no architecture decisions, less than 3 steps) or bug fixes
- If something goes sideways, STOP and re-plan immediately - don't keep pushing
- Use plan mode for verification steps, not just building
- Write detailed specs upfront to reduce ambiguity
- Save context - load only these specification file that is related to the current task at hand or required for it to finish

### 2. Strict Phase Progression (M/L tasks)

**HARD RULE: After completing any phase, propose ONLY the immediate next phase. NEVER skip phases or ask about a later phase.**

The workflow phases for M/L tasks are strictly ordered:

| #   | Phase         | What you do                                    | What you say to the user after completing                                                                                                                                                |
| --- | ------------- | ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | **Spec**      | Write/verify specification                     | Run `spec-reviewer` agent on the spec file. If PASS → "Spec verified as self-contained. Next step: task breakdown. Should I proceed?" If NEEDS WORK → follow the Spec Review Loop below. |
| 2   | **Tasks**     | TaskCreate all steps + TaskUpdate dependencies | "Tasks created ([N] tasks). Next step: inject relevant standards. I propose injecting: [list]. Confirm?"                                                                                 |
| 3   | **Inject**    | `/inject-standards` with confirmed paths       | "Standards injected. Ready to start implementation. Should I begin with task #1: [name]?"                                                                                                |
| 4   | **Implement** | Code, one task at a time                       | Mark each task completed, move to next                                                                                                                                                   |
| 5   | **Verify**    | `/verify-standards` automatically              | Report results, fix if needed                                                                                                                                                            |
| 6   | **Build**     | Run build for changed packages                 | Report build status                                                                                                                                                                      |

**Spec Review Loop (when `spec-reviewer` returns NEEDS WORK):**

1. Present the gaps list to the user
2. Split gaps into two categories:
   - **Auto-fixable** — info exists in your conversation context but wasn't written to spec. Fix these yourself immediately — this is exactly the implicit knowledge that needs to be captured.
   - **Needs user input** — unclear requirements or business decisions. Ask the user.
3. **Verify all URLs** listed in the reviewer's "URLs Requiring Verification" section — use WebFetch on each one. Remove or replace any that don't resolve to the expected content. Ask the user for correct URLs if needed.
4. Update the spec file with all fixes
5. Re-run `spec-reviewer` on the updated spec
6. Repeat until PASS. Do NOT proceed to tasks until the spec passes review.

**Examples of WRONG behavior:**
- ❌ After spec: "Should I start implementing?" (skips tasks + inject)
- ❌ After spec: "Should I inject standards and start coding?" (skips tasks)
- ❌ After tasks: "Let me start coding" (skips inject)

**Examples of CORRECT behavior:**
- ✅ After spec: "Spec is ready. Next step is task breakdown. Should I create tasks?"
- ✅ After tasks: "Tasks ready. Next step is standards injection. I propose injecting: [list]"
- ✅ After inject: "Standards loaded. Starting implementation with task #1: [name]"

### 3. Subagent Strategy

- Use subagents liberally to keep main context window clean
- Offload research, exploration, and parallel analysis to subagents
- For complex problems, throw more compute at it via subagents
- One task per subagent for focused execution

### 4. Self-improvement Loop

- After ANY correction from the user: update specification file or run `/sync-standards` command if it's something more general with the pattern
- Write rules for yourself that prevent the same mistake and suggest updates to `AGENTS.md` files
- Ruthlessly iterate on these lessons until mistake rate drops
- Review lessons at session start for relevant project

### 5. Verification Before Done

- Suggest user to verify the task completeness by proving it works:
  - Diff behavior between main and your changes when relevant
  - Ask yourself: "Would a staff engineer approve this?"
  - Run tests, check logs, demonstrate correctness

### 6. Demand Elegance (Balanced)

- For non-trivial changes: pause and ask "is there a more elegant way?"
- If a fix feels hacky: "Knowing everything I know now, implement the elegant solution"
- Skip this for simple, obvious fixes – don't over-engineer
- Challenge your own work before presenting it
- Follow the project's design principles and rules defined in `GUARDRAILS.md` and `.ai/standards/`

### 7. Autonomous Bug Fixing

- When given a bug report: just fix it. Don't ask for hand-holding
- Point at logs, errors, failing tests - then resolve them
- Zero context switching required from the user
- Go fix failing CI tests without being told how


## Documentation and Specifications

Architecture Decision Records (ADRs) and feature specifications are maintained in the `.ai/specs/` folder. This serves as the source of truth for design decisions and module specifications. Save context size and load only these specs that are related to and required to finish the task at hand.

### Spec Files (Size L)

- **Naming convention**: `SPEC-{number}-{date}-{title}.md` (e.g., `SPEC-003-2026-01-23-notifications-module.md`)
- **Number**: Sequential identifier (001, 002, 003, etc.)
- **Date**: Creation date in ISO format (YYYY-MM-DD)
- **Title**: Descriptive kebab-case title
- Each spec documents the module's purpose, architecture, API contracts, data models, and implementation details.
- Specs should include a **Changelog** section at the bottom to track evolution over time.

### Quick Specs (Size S)

For small changes (bug fix, field addition, text change) — lightweight plan files in `.ai/specs/quick/`:

- **Naming convention**: `{NNN}-{slug}.md` (e.g., `001-add-dark-mode-toggle.md`)
- **Number**: Sequential identifier within quick specs
- **Content**: Scope, what to change, where, and why — no formal sections required
- Quick specs are disposable — they document intent, not architecture

### When Developing Features

1. **Before coding**: Check if a spec exists for the module you're modifying. Search for `SPEC-*-{module-name}.md` files.
2. **When adding features**: Update the corresponding spec file with:
   - New functionality description
   - API changes
   - Data model updates
   - A changelog entry with date and summary
3. **When creating new modules**: Use the `/create-spec` skill for interactive, guided spec creation. It handles discovery, naming, structure, and file creation following `.ai/specs/AGENTS.md` conventions.

### Spec Changelog Format

Each spec should maintain a changelog at the bottom:

```markdown
## Changelog

### 2026-02-05
- Added email notification channel support
- Updated notification preferences API

### 2026-02-05
- Initial specification
```

### Auto-generating Specs

Even when not explicitly asked to update specs, agents should:

- Generate or update the spec when implementing significant changes
- Keep specs synchronized with the actual implementation
- Document any architectural decisions made during development

This ensures the `.ai/specs/` folder remains a reliable reference for understanding module behavior and history.

## Task Management

> **GATE CHECK**: If you just completed a spec and are about to ask the user "should I start implementation?" — STOP. You are violating phase progression (see §2). The next step is **task creation**, not implementation.

### When to Create Tasks

**ALWAYS after completing or verifying the specification, BEFORE inject standards and implementation.** Tasks are the bridge between spec and code — without them the agent jumps from "what to do" to "doing" without tracking progress.

Order: `spec ready → TaskCreate (all steps) → TaskUpdate (dependencies) → inject standards → implement`

### Task Rules

1. **Atomic steps**: Each task = one file or one logical change (e.g., "Create NotificationService.ts", not "Do backend")
2. **Dependencies**: Set `blockedBy` — e.g., registration in manager depends on creating the class
3. **Inject standards as task #1**: First task is always injecting standards (blocks the rest)
4. **Track Progress**: Mark `in_progress` before starting, `completed` after finishing
5. **Explain Changes**: High-level summary at each step
6. **Document Results**: Add review section to specification file
7. **Capture Lessons**: Update `.ai/lessons.md` after corrections if there's a general rule that will let us save time fixing things in the future.
8. **Sync to spec**: After creating tasks, write an `## Implementation Checklist` section at the end of the spec file (before Changelog). Update checkboxes as tasks complete. This enables session continuity — if a session breaks mid-implementation, a new session reads the spec and sees what's done vs remaining.
   ```markdown
   ## Implementation Checklist
   - [x] Inject standards
   - [x] Create DB migration
   - [ ] Create API routes    ← in progress
   - [ ] Create state slice
   ```

### After Completing Implementation

**When ALL implementation tasks have status `completed` — automatically run `/verify-standards`** without waiting for user command. This is a mandatory step in the `implement → verify` flow. Only after verify (and any fixes) inform the user about readiness to commit.

## Core Principles

- **Simplicity First**: Make every change as simple as possible. Impact minimal code.
- **No Laziness**: Find root causes. No temporary fixes. Senior developer standards.
- **Minimal Impact**: Changes should only touch what's necessary. Avoid introducing bugs.

## Project Layout

apps/web/                    # Main Next.js application
packages/prisma/             # Database schema (schema.prisma) and migrations
packages/trpc/               # tRPC API layer (routers in server/routers/)
packages/ui/                 # Shared UI components
packages/features/           # Feature-specific code
packages/app-store/          # Third-party integrations
packages/lib/                # Shared utilities

## Tech Stack

Framework: Next.js 13+ (App Router in some areas)
Language: TypeScript (strict)
Database: PostgreSQL with Prisma ORM
API: tRPC for type-safe APIs
Auth: NextAuth.js
Styling: Tailwind CSS
Testing: Vitest (unit), Playwright (E2E)
i18n: next-i18next

## Commands

### Development Commands
yarn dev - Start development server for web app
yarn dev:all - Start web, website, and console apps
yarn dev:api - Start web app with API proxy and API
yarn dev:console - Start web app with console
yarn dx - Start development with database setup

### Build Commands
yarn build - Build all packages and apps
yarn build:ai - Build AI package specifically
yarn clean - Remove build artifacts (node_modules, .next, .turbo, dist)

### Lint & Type Check
yarn lint - Run Biome across the codebase
yarn lint:fix - Run Biome and apply safe fixes
yarn lint:report - Generate Biome lint report
yarn type-check - Run TypeScript type checking
yarn format - Format code with Biome

### Unit Tests
yarn test - Run unit tests (vitest)
yarn test <filename> - Run tests for specific file
yarn test <filename> -t "<testName>" - Run specific test by name for specific file
yarn tdd - Run tests in watch mode
yarn test:ui - Run tests with UI interface

## Coding Standards

Detailed standards: `.ai/standards/`
Index: `.ai/standards/index.yml`

**Before any non-trivial change** — read the relevant standard. Areas are discovered and populated per project via `/discover-standards`. Typical areas look like:

- API → `.ai/standards/api/`
- Database → `.ai/standards/database/`
- State management → `.ai/standards/<your-state-layer>/`
- UI components → `.ai/standards/<your-ui-layer>/`
- Cross-cutting → `.ai/standards/global/`

See `.ai/standards/examples/` for what a finished standard looks like.

Available skills:
- `/inject-standards` — inject standards into context
- `/discover-standards` — discover new patterns in the code
- `/verify-standards` — verify code vs standards (after implementation)
- `/sync-standards` — synchronize standards with new code (after implementation)

## Workflow (Feedback Loop)

Classification and flow:

```
S: inject → implement → verify → build
M: inject(propose) → plan(+analogies, +user-stories) → tasks → implement(+pattern-finder) → verify → build → sync-standards
L: discover → inject(propose) → spec(+analogies, +user-stories) → tasks → implement(+pattern-finder) → verify → build → sync-standards
```

- `tasks` — after completing/verifying spec, BEFORE implementation: break down tasks with dependencies (TaskCreate + TaskUpdate). Tasks are atomic implementation steps derived from the spec.
- `inject(propose)` — read index.yml, propose specific standards, after confirmation `/inject-standards` explicit
- `+analogies` — in plan/spec phase: find an analogous module in codebase as a structural pattern
- `+pattern-finder` — in implement phase: concrete code examples with targeted query

Standards are a living document — every implementation either confirms standards or updates them.

### Build Verification

After `/verify-standards`, before commit — run the project's build command for any packages you touched (see the **Commands** table above). Build must pass without errors. If build fails — fix before commit.

### Standards Injection Protocol (M/L tasks)

For M and L tasks — **DO NOT explore codebase** to learn patterns. Standards ALREADY document them. Instead:

1. **Read the index** — `.ai/standards/index.yml` (small file, context-cheap)
2. **Match to task** — based on task description, determine which standard domains are needed
3. **Propose to user** specific paths to inject, e.g.:

   > This task involves a new API endpoint and database write. I suggest injecting:
   > - `api/route-structure` — route export pattern, middleware, validation
   > - `api/error-handling` — error formats, logging
   > - `database/repository-pattern` — repo structure, SQL, naming
   > - `global/naming-conventions` — file and variable naming conventions
   >
   > Do you confirm? Want to add/remove anything from the list?

4. **After confirmation** — run `/inject-standards` in explicit mode with confirmed paths:
   ```
   /inject-standards api/route-structure api/error-handling database/repository-pattern global/naming-conventions
   ```
5. **DO NOT use** auto-suggest mode (`/inject-standards` without arguments) for M/L — always propose specific standards

### Analogy Discovery (plan/spec phase)

During planning — before you start writing spec or plan — **find an analogous module** in the codebase. Goal: understand scope, what layers need to be built, how many files, what structure.

**How it works:**

1. **Propose an analogy to the user** — based on task description and the "Where to Look" table, e.g.:

   > You're building a notifications module. Structurally the closest existing module is {analogous module} — it has the same layers you'll need (API routes, DB repo, state slice, UI pages).
   >
   > Want me to analyze it as a structural pattern? Or do you have another suggestion?

2. **After confirmation** — use `codebase-pattern-finder` with a query about **module structure** (not implementation details):
   ```
   Task(subagent_type=codebase-pattern-finder):
     "Analyze the {analogous module} structure as a pattern for a new module.
      Show: what files exist, what layers (route → repo → store → UI),
      how they're connected. Search in the relevant directories listed in
      'Where to Look' in AGENTS.md."
   ```

3. **Write the result** into spec/plan as a "Reference Module" section — so in the implement phase it's clear what to model after

**How to know which analogy fits:**
- Use the "Where to Look" table (at the bottom of this file) + knowledge of existing modules
- If you don't know — **ask the user**: "Which existing module is closest to what you're building?"
- DO NOT explore the entire repo to discover this yourself

### User Stories (plan/spec phase — M/L only)

After analogy discovery and before writing Architecture — **write user stories**. They are implementation scenarios that bridge UX and code. Detailed guidelines in `.ai/specs/AGENTS.md` → "User Stories Guidelines".

**Why they matter:**
- Force you to understand existing UX before changing it ("Change vs. current state" boxes)
- ASCII wireframes define component structure before you write JSX / template code
- Technical context boxes map each UX step to API calls, state changes, DB writes
- Multiple personas test your architecture from different angles — reveal edge cases early
- Comparison tables (e.g., sync vs async, API-based vs webhook-based) clarify conditional logic

**How to write them:**

1. **Identify 2-3 personas** — at minimum: primary user (happy path) + alternative user (different use case or technical level)
2. **Walk through screen-by-screen** — each step = what user sees (ASCII wireframe) + what happens in the background (technical context)
3. **Add "Change vs. current state"** at every step that modifies existing behavior — this prevents breaking things
4. **Add comparison table** if the feature has variants or replaces existing behavior
5. **3rd story for edge cases** (L specs) — e.g., multiple entities, error states, power-user scenarios

### Code Pattern Finder (implement phase)

Standards give **rules** (what to do). When during implementation you need to see a **concrete code example** — use `codebase-pattern-finder` with a targeted query. DO NOT explore the entire repo.

**When to use:**
- Standard says "use repository pattern" but you need to see a concrete implementation
- You need a test pattern for a given component/route type
- You're implementing a specific method and want to see how an analogous one looks

**How to use:**
```
Task(subagent_type=codebase-pattern-finder):
  "Find examples of a CRUD route with validation and auth middleware
   in this codebase. Search in the directories listed under 'Where to Look'
   in AGENTS.md."
```

**DO NOT use for:**
- Discovering naming conventions → that's in standards (`global/naming-conventions`)
- Learning response structure → that's in standards (`api/route-structure`)
- Anything that standards already document

### Summary: 3 Tools Instead of Explore

| Phase       | Tool                                           | What it provides                                                      | Cost                     |
| ----------- | ---------------------------------------------- | --------------------------------------------------------------------- | ------------------------ |
| Before code | `/inject-standards` explicit                   | Rules and conventions                                                 | Low (read index + files) |
| Plan/Spec   | `codebase-pattern-finder` (analogy)            | Reference module structure                                            | Medium (targeted query)  |
| Implement   | `codebase-pattern-finder` (example)            | Concrete code snippet                                                 | Medium (targeted query)  |
| Any phase   | Context7 (`resolve-library-id` + `query-docs`) | External library documentation — **ALWAYS use this, NEVER WebSearch** | Low (MCP call)           |


**Explore on entire repo** → NO. Use ONLY for business specifics, not for conventions or coding patterns.

## Gotchas

- **NEVER invent URLs.** If a spec or code needs an external URL — ask the user for the real link or verify it exists via WebFetch. Hallucinated URLs are a real problem — many sites return custom pages (not 404) for non-existent paths, making fake links hard to detect later.
- **Use Context7 for library documentation**, not training-data memory — library APIs drift and your recall can be stale.

### Never do
- Commit secrets, API keys, or .env files
- Expose credential.key in any query
- Use as any type casting
- Force push or rebase shared branches
- Modify generated files directly

## Where to Look

- Routes: apps/web/app/ (App Router)
- Database schema: packages/prisma/schema.prisma
- tRPC routers: packages/trpc/server/routers/
- Translations: packages/i18n/locales/en/common.json
- Workflow constants: packages/features/ee/workflows/lib/constants.ts
