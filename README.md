# Awesome Cursor Subagents

This repository is a curated collection of Cursor Subagents, adapted from the original [Awesome Claude Code Subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) repository.

These subagents are specialized AI personas that enhance Cursor's capabilities by providing task-specific expertise, ranging from API design and language specialists to infrastructure and DevOps tools.

## Installation

Cursor's new subagent feature reads from `.md` files located in a specific directory at the root of your project or globally.

### Option 1: Project-Specific Installation

To make these subagents available within a specific project (and share them with your team via git):

1. Copy the `.cursor/agents/` directory into the root of your project workspace.
2. In Cursor's chat input, type `@` to bring up the context menu. You should now see the various agents (like `@api-designer` or `@frontend-developer`) available to select!

### Option 2: Personal (Global) Installation

To make these subagents available across *all* of your projects:

1. Copy the contents of the `.cursor/agents/` directory into `~/.cursor/agents/`.
   ```bash
   mkdir -p ~/.cursor/agents
   cp -r .cursor/agents/* ~/.cursor/agents/
   ```
2. You can now `@` mention any of these agents in any project you open in Cursor.

## Available Categories

We have **144** catalog agents (synced from [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents)) across several domains:

- **Core Development**: Essential development skills (e.g., `api-designer`, `backend-developer`, `frontend-developer`, `design-bridge`).
- **Language Specialists**: Language-specific experts (e.g., `python-pro`, `typescript-pro`, `node-specialist`, `rust-engineer`, `fastapi-developer`, `symfony-specialist`, `expo-react-native-expert`).
- **Infrastructure**: DevOps, cloud, and deployment specialists.
- **Quality & Security**: Testing, security, and code quality experts (e.g., `security-auditor`, `ai-writing-auditor`, `ui-ux-tester`, `accessibility-tester`).
- **Data & AI**: Data engineering, ML, and AI specialists (e.g., `llm-architect`, `reinforcement-learning-engineer`).
- **Developer Experience**: Tooling and developer productivity experts (e.g., `dx-optimizer`, `readme-generator`).
- **Specialized Domains**: Domain-specific technology experts (e.g., `healthcare-admin`).
- **Business & Product**: Product management and business analysis (e.g., `product-manager`, `license-engineer`).
- **Meta & Orchestration**: Agent coordination and meta-programming (e.g., `multi-agent-coordinator`, `agent-installer`, `codebase-orchestrator`).
- **Research & Analysis**: Research, search, and analysis specialists.

Browse the `.cursor/agents/` directory to see all the available markdown files.

## How It Works

Each subagent is a simple markdown file (e.g., `api-designer.md`). When you mention `@api-designer` in Cursor's chat or Composer, Cursor reads the contents of this file and applies its specific instructions, checklists, and guidelines to the task you give it.

## Advanced: Using Subagents Autonomously (Agent-to-Agent)

We have also included a special Cursor Skill in this repository called `call-subagents` (located in `.cursor/skills/call-subagents/`). 

If you install this skill (by moving the `.cursor/skills/` directory into your project), it teaches the primary Cursor Agent **how to spawn these subagents autonomously using the internal `Subagent` tool.**

When you ask Cursor: *"Have the devops engineer write a GitHub Action for this repo"*, the main Cursor Agent will:
1. Realize it needs the `devops-engineer` persona.
2. Read the instructions from `.cursor/agents/devops-engineer.md`.
3. Launch a background subagent (via the Subagent tool) packed with those exact expert instructions to complete your request autonomously!

## Cursor / Composer 3 Compatibility

This repository is compatible with current Cursor and Composer-era agent format expectations:

- Custom agents live in `.cursor/agents/`.
- Each agent file includes YAML frontmatter with `name`, `description`, and `model`.
- `model: inherit` is the default in this repo; final runtime model selection can still vary based on planning mode, Max Mode availability, and admin/workspace policy restrictions.

## Contributing

Contributions are welcome! If you'd like to add new subagents or improve existing ones, simply create or modify a `.md` file inside the `.cursor/agents/` directory with clear instructions for the AI to follow.

### Refreshing from VoltAgent upstream

This catalog tracks [VoltAgent/awesome-claude-code-subagents](https://github.com/VoltAgent/awesome-claude-code-subagents). To pull the latest agent definitions and convert them to Cursor frontmatter (`model: inherit`, no `tools` line, optional path normalization):

1. Clone the upstream repo (for example `git clone --depth 1 https://github.com/VoltAgent/awesome-claude-code-subagents.git _upstream-awesome`). The `_upstream-awesome/` path is gitignored if you clone inside this workspace.
2. Run `python3 scripts/sync_agents_from_upstream.py` (or pass `--upstream /path/to/clone`).
3. The sync script intentionally **does not** overwrite fork-specific agents: `agent-installer` and `design-bridge`. Merge upstream changes into those by hand when appropriate.

Before opening a pull request, run the frontmatter validator from the repository root:

```bash
python3 scripts/validate_cursor_agents.py
```

CI runs the same check on every push and pull request.

## License

This repository inherits the MIT License from the original [Awesome Claude Code Subagents](https://github.com/VoltAgent/awesome-claude-code-subagents) project. See the [LICENSE](LICENSE) file for more details.
