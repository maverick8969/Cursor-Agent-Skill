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
  - (See `.cursor/agents/` for the full list of 140+ available subagents)
- **Broad exploration or multi-step codebase search** → `explore` (built-in subagent type)
- **Git, shell, or command execution** → `shell` (built-in subagent type)

## How to Invoke Specialists (Subagent Tool)

Use the **Subagent** tool to launch subagents. The `Subagent` tool requires a `subagent_type`. Because most custom project subagents (like `python-pro` or `devops-engineer`) aren't built-in types natively mapped to the tool, you must use the `generalPurpose` type and pass the agent's instructions into the prompt.

**Required Parameters for the Subagent Tool:**
1. `subagent_type`: Set this to `generalPurpose`.
2. `description`: Short (3–5 word) summary of the task.
3. `prompt`: **CRITICAL:** You must include the contents of the `.cursor/agents/<agent-name>.md` file in the prompt so the subagent knows how to behave. 

**Steps to Invoke a Specialist:**
1. **Read** the corresponding agent file from `.cursor/agents/<agent-name>.md` using the Read tool.
2. **Launch** the Subagent tool (`subagent_type="generalPurpose"`) with a prompt structured like this:
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
1. Read `.cursor/agents/api-designer.md`.
2. Call Subagent tool:
   - `subagent_type`: `generalPurpose`
   - `description`: "Design readings API"
   - `prompt`: "You are the api-designer. [Insert api-designer.md content]. Context: Backend is in backend/api/server.js. Task: Design an OpenAPI 3.1 snippet for the readings resource. Return the spec snippet and a short rationale."

**Example 2 – Python Pro**
User: "Get the python pro to review this script and add type hints."
Action:
1. Read `.cursor/agents/python-pro.md`.
2. Call Subagent tool:
   - `subagent_type`: `generalPurpose`
   - `description`: "Add python type hints"
   - `prompt`: "You are the python-pro. [Insert python-pro.md content]. Task: Review `scripts/process.py`, add complete type hints, and ensure PEP 8 compliance. Return the updated file contents."
