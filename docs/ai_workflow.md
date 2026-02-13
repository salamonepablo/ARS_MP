# AI-Assisted Development Workflow

This document describes the tools and methodology used to develop ARS_MP with AI assistance, as part of the Master's thesis (TFM) for the "Master en Desarrollo con IA" program.

## Development Environment

| Component | Tool |
|-----------|------|
| Editor | VS Code |
| AI in editor | GitHub Copilot (code completion, inline suggestions) |
| Terminal | Windows Terminal + PowerShell 7 |
| AI for code generation | [OpenCode](https://opencode.ai/) CLI with **Claude Opus 4.5** (latest), later upgraded to **Claude Opus 4.6** |
| Version control | Git + GitHub (public repo) |
| Prompt design | Written manually, then formatted with GitHub Copilot |

## Workflow

### 1. Prompt design (human)

Each feature started with a hand-written prompt that defined the goal, constraints, and expected behavior. These prompts were drafted in VS Code based on patterns learned during the Master's program.

The prompts are available in [`context/prompts/`](../context/prompts/) and follow a numbered sequence:

| # | Prompt | Feature |
|---|--------|---------|
| 01 | `01-estructura.md` | Project folder structure |
| 02 | `02-git-readme.md` | Git setup and initial README |
| 03 | `03-read-bd-legacy.md` | Read legacy Access database |
| 04 | `04-RS-Structure.md` | Rolling stock unit structure |
| 05 | `05-RS-Info-Card.md` | Fleet module cards (UI) |
| 07 | `07-Create-entities.md` | Domain entities (EMU, Coach, Formation) |
| 08 | `08-Connect-Real-Data.md` | Connect to real Access data, replace stubs |
| 09 | `09-Brief-UM-Information.md` | Maintenance unit brief + calculation rules |
| 10 | `10-Maintenance-Projection.md` | Maintenance projection grid (main feature) |

> Note: Prompt 06 was an exploratory iteration that was absorbed into later prompts.

### 2. Prompt formatting (GitHub Copilot)

Once the idea was clear, GitHub Copilot in VS Code was used to refine the prompt structure: formatting Markdown, adding context sections, and ensuring the instructions were unambiguous for the AI code generator.

### 3. Code generation (OpenCode + Claude)

The formatted prompt was passed to **OpenCode** running in Windows Terminal (PowerShell 7). OpenCode used **Claude Opus 4.5** (and later **4.6**) as the underlying model. The AI would:

- Read existing code and project structure
- Generate new files or modify existing ones
- Run tests (`pytest`) and fix failures
- Follow the TDD RED-GREEN-REFACTOR cycle
- Respect the architectural constraints defined in `AGENTS.md`

### 4. AGENTS.md — Project constitution

The file [`AGENTS.md`](../AGENTS.md) at the project root acts as a "constitution" for AI assistants. It defines:

- Project context and architecture rules
- Technology stack and coding conventions
- TDD methodology and quality gates
- Language rules (code in English, business docs in Spanish)
- Documentation and versioning requirements (Conventional Commits)

Every AI session starts by reading this file, ensuring consistency across sessions.

### 5. Iterative refinement

The development process was iterative:

1. **Human** writes prompt with feature requirements and business context
2. **Copilot** helps format and structure the prompt
3. **OpenCode + Claude** generates code, tests, and documentation
4. **Human** reviews output, validates against real data, and provides feedback
5. **Repeat** — the AI adjusts based on corrections and new discoveries

Each iteration produced small, focused commits following Conventional Commits (`feat:`, `fix:`, `test:`, `docs:`, `refactor:`).

## Key Observations

- **Domain knowledge is irreplaceable**: The AI could not generate correct maintenance hierarchy rules or projection formulas without explicit business context from the developer.
- **AGENTS.md as guardrails**: Having a clear project constitution prevented architectural drift across sessions.
- **TDD worked well with AI**: The RED-GREEN-REFACTOR cycle gave the AI clear pass/fail signals to iterate on.
- **Prompt quality matters**: Well-structured prompts with examples and constraints produced significantly better results than vague instructions.
- **The human stays in the loop**: Every output was reviewed and validated. The AI accelerated implementation but the developer maintained full control over design decisions.
