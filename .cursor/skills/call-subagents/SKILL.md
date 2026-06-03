---
name: call-subagents
description: Invokes specialist subagents via the Task tool for complex tasks. Use when the user asks to involve a specialist (e.g. "@api-designer"), or when a task clearly matches one of the provided .cursor/agents/ (like python-pro, backend-developer, devops-engineer, code-reviewer, etc.).
---

# Call Subagents

## When to Call Subagents

- **User asks for a specialist**: e.g., "have the API designer look at this", "get the devops engineer to build the pipeline".
- **Task clearly matches a specialist**:
  - API design, OpenAPI specs, REST/GraphQL → `api-designer`
  - Backend implementation, databases, APIs, auth, caching → `backend-developer`
  - React, Vue, Angular, UI/UX → `frontend-developer`
  - Devops, CI/CD, pipelines → `devops-engineer`
  - Code quality, security, review after changes → `code-reviewer`
  - Python coding, type-safety, Pandas → `python-pro`
  - FastAPI async APIs, Pydantic v2, ASGI → `fastapi-developer`
  - Symfony, Doctrine ORM, API Platform, Messenger → `symfony-specialist`
  - Expo/React Native mobile apps, EAS deployment → `expo-react-native-expert`
  - Design system translation, DESIGN.md → `design-bridge`
  - RL environments, policy optimization, sim-to-real → `reinforcement-learning-engineer`
  - README generation, zero-hallucination docs → `readme-generator`
  - AI writing pattern detection and removal → `ai-writing-auditor`
  - Software licensing, compliance pipelines → `license-engineer`
  - Browse and install agents from repositories → `agent-installer`
  - Node.js backends, APIs, CLIs → `node-specialist`
  - UI flows, components, and UX heuristics (not only WCAG) → `ui-ux-tester`
  - Healthcare IT, HIPAA-aware workflows → `healthcare-admin`
  - Repo-wide refactors with approval gates → `codebase-orchestrator`
  - (See `.cursor/agents/` for the full catalog; count varies by install)
- **Broad exploration or multi-step codebase search** → `explore` (built-in subagent type)
- **Git, shell, or command execution** → `shell` (built-in subagent type)

## How to Invoke Specialists (Task Tool)

Use the **Task** tool to launch subagents. Required: `subagent_type`, `description` (short title), and a self-contained `prompt`.

**Preferred:** If the Task tool lists your specialist id in `subagent_type` (for example `python-pro`, `devops-engineer`, `code-reviewer`, `explore`, or `shell`), set `subagent_type` to that id. The runtime can attach the matching persona from `.cursor/agents/<id>.md`. Still write a **fully self-contained** `prompt` (paths, constraints, expected return shape); the parent chat is not automatically visible to the subagent.

**Fallback:** If the specialist id is **not** in `subagent_type`, use `generalPurpose` and paste the **entire** contents of `.cursor/agents/<agent-name>.md` into `prompt` as the specialist instructions.

**Optional Task parameters** (use when appropriate):
- `run_in_background`: `true` for long work; poll with Await or continue other work until notified.
- `readonly`: `true` when the subagent must not modify files (exploration/review only).
- `model`: only when the user explicitly requests a specific model slug exposed by the tool.

**Steps to invoke a catalog specialist**
1. **Read** `.cursor/agents/<agent-name>.md` when using `generalPurpose`, or when you need exact checklist wording for the prompt.
2. **Launch** the Task tool:
   - `subagent_type`: specialist id when listed; otherwise `generalPurpose`
   - `description`: 3–5 word summary (e.g. "Design readings API")
   - `prompt`: task plus context; for `generalPurpose`, structure like:
   ```text
   You are acting as the [Agent Name] specialist.
   Here are your core instructions and checklists:
   <paste the contents of the agent's .md file here>

   Here is the task you need to perform:
   [Full context, repo paths, file names, and what to return to the parent agent]
   ```

## Guidelines

- **Self-contained prompts:** Subagents do not see the parent conversation. Include exact file paths, current state, and the artifacts to return.
- **Clear returns:** Specify what to return (e.g. "Return a short summary of findings", "Return the list of files to change").
- **Parallel work:** Launch multiple Task calls in one message when areas are independent.
- **User-facing language:** Do not expose internal model slugs; say "I'll have a specialist review this."

## Exploring the Catalog

If the user asks what agents are available, or you need to find a match:
- Run `ls .cursor/agents/` to list installed agents.
- Browse by domain: languages (`typescript-pro`, `rust-engineer`), infrastructure (`kubernetes-specialist`, `docker-expert`), product (`product-manager`).

## Examples

**Example 1 – API Designer**
User: "Have the API designer propose an OpenAPI for the new readings endpoint."
Action:
1. Read `.cursor/agents/api-designer.md` if using `generalPurpose`, or skip if `api-designer` is in `subagent_type`.
2. Call Task tool:
   - `subagent_type`: `api-designer` when listed; otherwise `generalPurpose`
   - `description`: "Design readings API"
   - `prompt`: Task block with backend path, OpenAPI 3.1 requirements, and "return spec snippet plus short rationale." For `generalPurpose`, paste full `api-designer.md` first.

**Example 2 – Python Pro**
User: "Get the python pro to review this script and add type hints."
Action:
1. `python-pro` when listed, else `generalPurpose` plus full `python-pro.md`.
2. `prompt` must include `scripts/process.py`, type-hint expectations, and "return updated file contents".
