---
name: call-subagents
description: Invokes specialist subagents via the Subagent tool for complex tasks. Use when the user asks to involve a specialist (e.g. "@api-designer"), or when a task clearly matches one of the provided .cursor/agents/ (like python-pro, backend-developer, devops-engineer, code-reviewer, etc.).
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
  - (See `.cursor/agents/` for the full list of 144 catalog subagents)
- **Broad exploration or multi-step codebase search** → `explore` (built-in subagent type)
- **Git, shell, or command execution** → `shell` (built-in subagent type)

## How to Invoke Specialists (Subagent Tool)

Use the **Subagent** tool to launch subagents. The tool requires a `subagent_type` and a self-contained `prompt`.

**Preferred (Composer / current Cursor):** If the Subagent tool exposes your specialist id in its `subagent_type` enum (for example `python-pro`, `devops-engineer`, `explore`, or `shell`), set `subagent_type` to that id so the runtime can attach the matching persona. Still write a **fully self-contained** `prompt` (paths, constraints, expected return shape); the parent chat is not automatically visible to the subagent.

**Fallback:** If the specialist id is **not** accepted as `subagent_type` in your environment, use `generalPurpose` and paste the **entire** contents of `.cursor/agents/<agent-name>.md` into the prompt as the specialist instructions.

**Required parameters**
1. `subagent_type`: Specialist id when listed by the tool, otherwise `generalPurpose` (or another allowed built-in such as `explore` / `shell` when those fit better).
2. `description`: Short (3–5 word) summary of the task.
3. `prompt`: Task plus context; when using `generalPurpose` for a catalog specialist, include the full agent markdown from step 1 below.

**Steps to invoke a catalog specialist**
1. **Read** `.cursor/agents/<agent-name>.md` when you need the exact wording (required if using `generalPurpose` with pasted instructions).
2. **Launch** the Subagent tool with a prompt structured like this (when using `generalPurpose`):
   ```text
   You are acting as the [Agent Name] specialist. 
   Here are your core instructions and checklists:
   <paste the contents of the agent's .md file here>
   
   Here is the task you need to perform:
   [Provide full context, relevant repo paths, file names, and what the agent should return back to you]
   ```

## Guidelines

- **Self-Contained Prompts:** The subagent does NOT see the parent conversation. The prompt must be completely self-contained. Include exact file paths, current state, and the specific artifacts you want returned.
- **Clear Returns:** Always specify what the subagent should return (e.g. "Return a short summary of findings", "Return the list of files to change", "Return the OpenAPI snippet").
- **Do not reveal internal model names** when describing the subagent to the user; use natural language (e.g. "I will ask a specialist to review this").

## Exploring the Catalog

If the user asks what agents are available, or you need to find an appropriate agent:
- Run `ls .cursor/agents/` to list all available agents.
- You can find agents for almost any language (`typescript-pro`, `rust-engineer`, `golang-pro`), infrastructure (`kubernetes-specialist`, `docker-expert`), or domain (`fintech-engineer`, `game-developer`).

## Examples

**Example 1 – API Designer**
User: "Have the API designer propose an OpenAPI for the new readings endpoint."
Action:
1. Read `.cursor/agents/api-designer.md` if you will use `generalPurpose`, or skip if `api-designer` is accepted as `subagent_type`.
2. Call Subagent tool:
   - `subagent_type`: `api-designer` when the tool lists it; otherwise `generalPurpose`
   - `description`: "Design readings API"
   - `prompt`: If `generalPurpose`: paste full `api-designer.md` then add: "Context: Backend is in backend/api/server.js. Task: Design an OpenAPI 3.1 snippet for the readings resource. Return the spec snippet and a short rationale." If `api-designer`: same task block with paths and return shape; include any constraints the parent turn relied on.

**Example 2 – Python Pro**
User: "Get the python pro to review this script and add type hints."
Action:
1. Same pattern: `python-pro` when accepted, else `generalPurpose` plus full `python-pro.md`.
2. `prompt` must include `scripts/process.py`, type-hint expectations, and "return updated file contents".
