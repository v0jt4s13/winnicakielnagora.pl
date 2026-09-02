# Specs Folder Guidelines

This folder contains specifications and Architecture Decision Records (ADRs) that serve as the source of truth for design decisions and module behavior.

## Purpose

The `.ai/specs/` folder is the central repository for:

- **Specifications**: Documented design decisions with context, alternatives considered, and rationale
- **Feature specifications**: Detailed descriptions of module functionality, API contracts, and data models
- **Implementation reference**: Living documentation that stays synchronized with the codebase

## File Naming

Specification files follow the pattern `SPEC-{number}-{date}-{title}.md`:

- **Number**: Sequential identifier (e.g., `001`, `002`, `003`)
- **Date**: Creation date in ISO format (`YYYY-MM-DD`)
- **Title**: Descriptive kebab-case title (e.g., `sidebar-reorganization`, `messages-module`)

**Examples:**

- `SPEC-003-2026-01-23-notifications-module.md` – Notifications module specification
- `SPEC-002-2026-01-23-messages-module.md` – Messages module specification
- `SPEC-001-2026-01-21-ui-reusable-components.md` – Reusable UI component library reference

**Meta-documentation files** like `AGENTS.md` and `CLAUDE.md` use UPPERCASE names and are not numbered—they provide guidelines for working with the specs themselves.

## Spec File Structure

Each spec should include:

1. **Overview** – What the module/feature does and its purpose
2. **User Stories** (M/L specs) – Implementation scenarios from the user's perspective (see guidelines below)
3. **Architecture** – High-level design and component relationships
4. **Data Models** – Entity definitions, relationships, and database schema
5. **API Contracts** – Endpoints, request/response schemas, and examples
6. **UI/UX** – Frontend components and user interactions (if applicable)
7. **Configuration** – Environment variables, feature flags, and settings
8. **Changelog** – Version history with dates and summaries

### User Stories Guidelines (M/L specs)

User stories are **implementation scenarios** — not agile tickets. They bridge UX and code by walking through the feature screen-by-screen with technical context. Required for M and L specs.

**Each user story must contain:**

1. **Persona with context** — Who is the user, what's their goal, what's their technical level
   > **Persona**: Alex — a product manager with no engineering background. Just signed up and wants to connect a third-party service without touching configuration files.

2. **Step-by-step flow with ASCII wireframes** — Each step = one screen/interaction. Show what the user sees.
   ```
   ┌────────────────────────────────────────────┐
   │  ✅ {Service} is your active integration   │
   │  Connected via webhooks — no keys needed.  │
   └────────────────────────────────────────────┘
   ```

3. **"Change vs. current state" boxes** — What exists now vs. what changes. Forces understanding of existing code before writing new code.
   > **Change vs. current state**: Currently the integration panel asks for an API key + shows a disabled "Connect" button. After this change: clicking the provider icon = instant activation, with an explanatory alert below. Zero extra steps.

4. **Technical context** — What happens "behind the scenes" at each step (API calls, state changes, DB writes).
   > **Behind the scenes**: Clicking the panel triggers `integrate({ providerId: <id>, credentials: <null> })`. The provider id is persisted on the user/tenant record.

5. **Comparison table** — If the feature has variants or replaces existing behavior, add a side-by-side table.

**Minimum user stories per spec:**
- **2 stories**: Happy path + alternative flow (different persona or use case)
- **3rd story** (recommended for L): Edge case or power-user scenario (e.g., multiple entities, error recovery)

**What makes a good set of user stories:**
- Each story tests the architecture from a **different angle** (e.g., non-technical user vs developer, single vs multiple entities)
- Stories together cover all **conditional branches** in the UI (e.g., "campaign not saved yet" vs "campaign saved")
- The 3rd story often reveals **scalability concerns** that the first two miss

### Changelog Format

Every spec must maintain a changelog at the bottom:

```markdown
## Changelog

### 2026-01-23
- Added email notification channel support
- Updated notification preferences API

### 2026-01-15
- Initial specification
```

## Workflow

### Before Coding
1. Check if a spec exists for the module you're modifying
2. Read the spec to understand design intent and constraints
3. Identify gaps or outdated sections

### When Adding Features
1. Update the corresponding spec file with:
   - New functionality description
   - API changes
   - Data model updates
2. Add a changelog entry with the date and summary

### When Creating New Modules

1. Create a new spec file at `.ai/specs/SPEC-{next-number}-{YYYY-MM-DD}-{module-name}.md`
2. Document the initial design before or alongside implementation
3. Include a changelog entry for the initial specification

### After Coding
Even when not explicitly asked to update specs:
- Generate or update the spec when implementing significant changes
- Keep specs synchronized with actual implementation
- Document architectural decisions made during development

## For AI Agents

AI agents working on this codebase should:
1. **Always check** for existing specs before making changes
2. **Reference specs** to understand module behavior and constraints
3. **Update specs** when implementing features, even if not explicitly requested
4. **Create specs** for new modules or significant features
5. **Maintain changelogs** with clear, dated entries

This ensures the `.ai/specs/` folder remains a reliable reference for understanding module behavior and evolution over time.
