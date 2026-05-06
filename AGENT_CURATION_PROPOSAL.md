# Agent Curation Proposal (Option 1)

Goal: streamline `.cursor/agents` by reducing selection noise while preserving broad coverage for day-to-day engineering tasks.

## Current Inventory

- Total agents: 149
- Proposed keep now: 53
- Proposed remove now: 20
- Proposed review later: 76

## Keep Now (Core Set)

These are high-utility, broadly applicable, or already part of your active merged plugin set.

- `agent-organizer`
- `api-designer`
- `backend-architect`
- `backend-developer`
- `cloud-architect`
- `code-reviewer`
- `context-manager`
- `data-engineer`
- `data-scientist`
- `database-optimizer`
- `debugger`
- `devops-engineer`
- `docker-expert`
- `documentation-engineer`
- `dotnet-core-expert`
- `event-sourcing-architect`
- `fastapi-developer`
- `frontend-developer`
- `fullstack-developer`
- `golang-pro`
- `graphql-architect`
- `java-architect`
- `javascript-pro`
- `kubernetes-specialist`
- `llm-architect`
- `mlops-engineer`
- `mobile-developer`
- `multi-agent-coordinator`
- `nextjs-developer`
- `node-specialist`
- `performance-engineer`
- `php-pro`
- `platform-engineer`
- `postgres-pro`
- `product-manager`
- `project-manager`
- `python-pro`
- `qa-expert`
- `react-specialist`
- `readme-generator`
- `rust-engineer`
- `search-specialist`
- `security-auditor`
- `sre-engineer`
- `swift-expert`
- `task-distributor`
- `tdd-orchestrator`
- `technical-writer`
- `temporal-python-pro`
- `test-automator`
- `threat-modeling-expert`
- `typescript-pro`
- `workflow-orchestrator`

## Remove Now (Low-Relevance for Typical General Engineering Workflows)

These are mostly domain-specific or org-specific specialists and can be removed first with low risk.

- `ad-security-reviewer`
- `blockchain-developer`
- `competitive-analyst`
- `customer-success-manager`
- `fintech-engineer`
- `healthcare-admin`
- `legal-advisor`
- `m365-admin`
- `market-researcher`
- `powershell-5.1-expert`
- `powershell-7-expert`
- `powershell-module-architect`
- `powershell-security-hardening`
- `powershell-ui-architect`
- `quant-analyst`
- `sales-engineer`
- `slack-expert`
- `trend-analyst`
- `windows-infra-admin`
- `wordpress-master`

## Review Later (Keep Temporarily)

These are useful but more situational. Keep for now, then prune based on real usage.

### Platform / Infra / Ops

- `azure-infra-engineer`
- `build-engineer`
- `chaos-engineer`
- `compliance-auditor`
- `database-administrator`
- `deployment-engineer`
- `devops-incident-responder`
- `incident-responder`
- `network-engineer`
- `security-engineer`
- `terraform-engineer`
- `terragrunt-expert`

### Language / Framework Specialists

- `angular-architect`
- `cli-developer`
- `cpp-pro`
- `csharp-developer`
- `django-developer`
- `dotnet-framework-4.8-expert`
- `electron-pro`
- `elixir-expert`
- `embedded-systems`
- `expo-react-native-expert`
- `flutter-expert`
- `kotlin-specialist`
- `laravel-specialist`
- `rails-expert`
- `spring-boot-engineer`
- `sql-pro`
- `symfony-specialist`
- `vue-expert`
- `websocket-engineer`

### AI / Data / Research

- `ai-engineer`
- `data-analyst`
- `data-researcher`
- `knowledge-synthesizer`
- `machine-learning-engineer`
- `microservices-architect`
- `ml-engineer`
- `nlp-engineer`
- `prompt-engineer`
- `reinforcement-learning-engineer`
- `research-analyst`
- `scientific-literature-researcher`

### Product / Process / Specialized QA

- `accessibility-tester`
- `ai-writing-auditor`
- `api-documenter`
- `architect-reviewer`
- `business-analyst`
- `content-marketer`
- `design-bridge`
- `dx-optimizer`
- `error-coordinator`
- `error-detective`
- `git-workflow-manager`
- `license-engineer`
- `project-idea-validator`
- `refactoring-specialist`
- `risk-manager`
- `scrum-master`
- `seo-specialist`
- `tooling-engineer`
- `ui-designer`
- `ui-ux-tester`
- `ux-researcher`

### Niche Domain / Integration

- `agent-installer`
- `codebase-orchestrator`
- `dependency-manager`
- `game-developer`
- `iot-engineer`
- `it-ops-orchestrator`
- `mcp-developer`
- `mobile-app-developer`
- `payment-integration`
- `penetration-tester`
- `performance-monitor`

## Suggested Next Step

If approved, perform a safe Phase 2:

1. Move the 20 "Remove Now" agents to an archive directory first (instead of hard-delete).
2. Keep "Review Later" unchanged.
3. Re-check discoverability and usage for 1-2 weeks, then prune another 20-30 from Review Later.

## Phase 3 (Conservative) - Completed

Given the requirement to keep the catalog comprehensive for many project types, Phase 3 used a light-touch overlap trim instead of aggressive pruning.

- Additional archived: 8
- Focus: high-overlap process/meta personas, while preserving technical/domain breadth

Archived in Phase 3:

- `ai-writing-auditor`
- `architect-reviewer`
- `content-marketer`
- `knowledge-synthesizer`
- `project-idea-validator`
- `risk-manager`
- `scrum-master`
- `seo-specialist`

### Why this set

- These roles overlap with existing stronger general-purpose technical agents and are less likely to be required in routine code delivery.
- Core engineering coverage remains broad across backend, frontend, infra, security, data/AI, testing, and language specialists.
