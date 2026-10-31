# GCP Specialist Coding Agent

[![Python 3.13+](https://img.shields.io/badge/python-3.13+-blue.svg)](https://www.python.org/downloads/)
[![Package Manager: uv](https://img.shields.io/badge/managed%20by-uv-purple.svg)](https://github.com/astral-sh/uv)
[![Google GenAI](https://img.shields.io/badge/LLM-Google%20GenAI-4285F4.svg)](https://ai.google.dev/)
[![Google Cloud](https://img.shields.io/badge/Cloud-Google%20Cloud%20Platform-34A853.svg)](https://cloud.google.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An autonomous, intent-driven software engineering and cloud operations agent specialized in **Google Cloud Platform (GCP)**. Powered by Google Gemini via the Google GenAI SDK, this agent integrates live Google Cloud CLI (`gcloud`) execution, comprehensive codebase search and manipulation tools, persistent disk-backed memory, strict safety guardrails, and concurrent tool batching.

---

## Key Features

### 1. Intent-Driven GCP Cloud Engineering
- **Dynamic GCP Guidance Injection**: Automatically detects GCP services and concepts (Compute Engine, GKE, Cloud Run, Cloud Storage, BigQuery, VPC, IAM, Cloud KMS, etc.) in user prompts and dynamically loads the dedicated GCP engineering protocol (`src/relevant_system_files/gcloud_sys.md`).
- **Live CLI Operations**: Executes validated `gcloud`, `kubectl`, and PowerShell commands in real time against authenticated Google Cloud environments.
- **Evidence-Based Reconciliation**: Adheres to a strict *"Read Before Write"* and *"State Verification"* philosophy—validating post-condition resources rather than relying merely on exit codes.

### 2. Safety Interceptors & Blast Radius Containment
- **Dangerous Command Interceptor**: Governed by `risk_commands.json`, the execution harness actively intercepts and blocks destructive operations (such as unauthorized `gcloud projects delete`, destructive IAM binding removals, or unconstrained storage deletions).
- **Least-Privilege & Dry-Run Patterns**: Prompts and enforces dry runs and narrow scope targeting before mutating live resources.

### 3. Structured Memory & Execution Tracking
- **Long-Term Memory (`lt_memory.md`)**: Records discovered environment facts, active projects, credentials, and persistent project context across multi-turn interactions.
- **Task Management (`todo.md`)**: Dynamic checklist tracker for breaking complex user instructions into atomic, verifiable phases.
- **Execution Ledger (`execution_ledger.md`)**: Immutable chronological log tracking performed commands, parameters, and observed outputs.

### 4. Advanced Tooling & Batching Engine
- **Tool Batching (`functions/tool_batching.py`)**: Asynchronous engine capable of executing independent tools concurrently and resolving sequential dependencies with cycle detection.
- **Codebase Manipulation**: File search, deep inspection, file generation, and surgical patching (`get_files_info`, `get_file_content`, `write_file`, `write_new_file`, `apply_edits`).
- **Code Execution**: In-shell script execution and isolated Python process evaluation (`execute_python_code_from_shell`, `run_python_file`).
- **Web Research**: Tavily search and targeted webpage crawling (`functions/web_search.py`, `wikitool.py`, `summariser.py`).

### 5. Benchmark Suite & Hardening Dataset
- **GCP Engineering Agent Benchmark (`gcloud_engineering_agent_benchmark/`)**: Machine-readable benchmark consisting of **253 tasks** across 28 operational phases (Level 0 through Level 5 complexity).
- Covers preflight discovery, BigQuery/GCS data migrations, GKE troubleshooting, VPC routing, IAM privilege audit, Cloud Run deployments, reliability/DR failovers, and incident response scenarios.

### 6. Local MongoDB Suite
- **MongoDB Automation (`mongodb_setup/`)**: Scripts for automated server lifecycle management, database seeding, schema validation, multi-field and text indexing, and aggregation verification.

---

## Architecture Overview

```
                                      +-------------------------------+
                                      |     User Terminal (CLI)       |
                                      +---------------+---------------+
                                                      |
                                                      v
                                      +-------------------------------+
                                      |     Agent Core (src/main.py)  |
                                      +-------+---------------+-------+
                                              |               |
                    +-------------------------+               +-------------------------+
                    |                                                                   |
                    v                                                                   v
+---------------------------------------+                             +---------------------------------------+
|            System Guidance            |                             |            Memory Engine              |
| - sys_prompt.md (General Coding)      |                             | - lt_memory.md (Long-Term Context)    |
| - gcloud_sys.md (GCP Protocol)        |                             | - todo.md (Task Planner)              |
| - engineering_protocol.md             |                             | - execution_ledger.md (Action Log)    |
+-------------------+-------------------+                             +---------------------------------------+
                    |
                    v
+-------------------------------------------------------------------------------------------------------------+
|                                           Tool Execution Suite                                              |
|  +------------------------+  +--------------------------+  +----------------------+  +--------------------+ |
|  |   Shell & GCP CLI      |  |     Python Execution     |  |    File Operations   |  |   Web Research     | |
|  | - run_shell_command    |  | - execute_python_in_shell|  | - get_file_content   |  | - get_web_results  | |
|  | - [risk_commands.json] |  | - run_python_file        |  | - apply_edits        |  | - crawl_webpage    | |
|  +------------------------+  +--------------------------+  +----------------------+  +--------------------+ |
|                                                                                                             |
|                                       Tool Batching & Concurrency                                           |
|                                      (functions/tool_batching.py)                                           |
+-------------------------------------------------------------------------------------------------------------+
```

---

## Project Structure

```
coding agent/
├── src/
│   ├── main.py                  # Agent loop, Gemini interactions, and interactive CLI
│   ├── config.py                # GCP keyword definitions, token metrics, and constants
│   ├── terminal_ui.py           # Rich-based terminal UI formatting
│   ├── session_data.json        # Interaction session persistence
│   ├── memory/
│   │   ├── lt_memory.md         # Persistent long-term memory
│   │   ├── todo.md              # Active todo task list
│   │   └── execution_ledger.md  # Execution activity log
│   └── relevant_system_files/
│       ├── gcloud_sys.md        # Specialized GCP prompt & engineering protocol
│       ├── sys_prompt.md        # Base coding and reasoning system instructions
│       ├── coding_agent_engineering_protocol.md
│       ├── coding_agent_instuctions.md
│       └── error_kt.md          # Knowledge base of runtime errors and troubleshooting
├── functions/                   # Tool calling implementations
│   ├── tool_batching.py         # Concurrent & dependency-aware tool batching engine
│   ├── run_python_file.py       # Python script runner
│   ├── run_python_file_in_shell.py
│   ├── get_file_content.py      # File reading with bounds and line counts
│   ├── get_files_info.py        # Directory trees and metadata exploration
│   ├── write_file.py            # Target file writer
│   ├── write_new_file.py        # Safe non-overwriting file creator
│   ├── apply_edits.py           # Surgical file modifications
│   ├── web_search.py            # Tavily search & web scraping
│   ├── summariser.py            # Content summarization utility
│   ├── wikitool.py              # Wikipedia lookup tool
│   ├── save_memory.py           # Memory persistence handler
│   ├── save_todo_updates.py     # Todo checklist updates
│   └── save_execution_ledger.py # Action ledger persistence
├── shell_tools/
│   └── directory_tools.py       # Shell runner guarded by risk command filter
├── gcloud_engineering_agent_benchmark/
│   └── gcloud_engineering_agent_benchmark/
│       ├── gcloud_migration_agent_tasks.jsonl  # 253 canonical evaluation tasks
│       ├── task_index.csv       # Task directory and phase mapping
│       ├── task.schema.json     # Strict schema definition for benchmark items
│       ├── build_dataset.py     # Benchmark generation scripts
│       └── expand_dataset.py
├── mongodb_setup/               # Local MongoDB database test environment
│   ├── manage_server.py         # Local MongoDB server runner
│   ├── seed_and_verify_mongodb.py # Synthetic data generation & index validation
│   └── test_mongodb_setup.py
├── agents/                      # Specialized subagents & prototypes
│   ├── orchestrator.py
│   ├── planner_agent.py
│   └── web_research_agent.py
├── crawl_gcloud.py              # Crawler utility for GCP CLI official documentation
├── crawl_gcloud_resume.py       # Resumable documentation crawler
├── crawl_retry.py               # Crawler retry handler
├── gcp_audit.py                 # Live GCP VPC, firewall, routes, and NAT audit script
├── risk_commands.json           # Safety blacklist for destructive shell & gcloud commands
├── training_prompts.json        # Curated tasks and test scenarios
├── pyproject.toml               # Project metadata and dependencies
└── .env.example                 # Environment variables template
```

---

## Installation & Setup

### 1. Prerequisites
- **Python 3.13+**
- **uv** (recommended fast package installer)
- **Google Cloud SDK (`gcloud`)** installed and authenticated (`gcloud auth login`, `gcloud auth application-default login`)

### 2. Clone the Repository
```bash
git clone https://github.com/JaySingh79/GCP-Specialist-Coding-Agent.git
cd GCP-Specialist-Coding-Agent
```

### 3. Install Dependencies
Using `uv`:
```bash
uv sync
```

### 4. Configure Environment Variables
Copy `.env.example` to `.env` and set your API keys:
```bash
cp .env.example .env
```
Fill in the values in `.env`:
```ini
GEMINI_API_KEY="your-google-gemini-api-key"
TAVILY_API_KEY="your-tavily-search-api-key"
```

---

## Usage

### Starting the Agent Terminal
Launch the interactive terminal session:
```bash
uv run python src/main.py
```

### In-Session Terminal Commands
While inside the interactive agent loop, you can execute the following session commands:
- `/context` — Display real-time token usage (input, output, thought, and total tokens).
- `/pause` — Pause the agent execution.
- `/resume` — Resume agent execution.
- `/stop` — Stop the ongoing execution loop.
- `/exit` — Save state and exit the agent session.

### Example Prompts
```text
❯ Show me all VPC networks, subnets, firewall rules, routes, and NAT configurations in this project: my-gcp-project-123
```
```text
❯ Audit the IAM bindings for gs://production-artifacts-bucket and confirm whether public access is blocked.
```
```text
❯ Diagnose why the Cloud Run service "order-processor" is returning HTTP 500 errors.
```

---

## Safety & Operating Rules

1. **Reconnaissance First**: Never mutate live cloud state without first querying the current state and verifying target identifiers.
2. **Deterministic Identifiers**: Always use explicit project, region, and resource identifiers rather than relying on default shell environment state.
3. **Restricted Command Interception**: Operations configured in `risk_commands.json` (such as project destruction or irreversible disk detachment) are blocked automatically by the execution layer.
4. **State Verification**: Every action must be verified against live Google Cloud APIs after execution to confirm success before marking tasks complete.

---

## Benchmark & Hardening Dataset

The included `gcloud_engineering_agent_benchmark/` contains **253 tasks** categorized into 6 difficulty tiers (`L0` to `L5`) and 28 operational domains. To inspect the benchmark index:
```bash
uv run python -c "import pandas as pd; df = pd.read_csv('gcloud_engineering_agent_benchmark/gcloud_engineering_agent_benchmark/task_index.csv'); print(df['phase'].value_counts())"
```

---

## License

This project is licensed under the MIT License.
