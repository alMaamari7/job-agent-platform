# Job Agent Platform

AI-powered multi-agent platform for candidate profiling, job matching, and application support.

The project is currently focused on building a controlled **Candidate Profiling system** that transforms heterogeneous candidate sources such as CVs, documents, and GitHub repositories into structured, reviewable candidate information.

The core architectural principle is:

> **AI decides what to do. Python controls how it is executed.**

---

## Current Project Scope

The long-term platform is intended to support several stages of the job-search process:

```text
Candidate Sources
        ↓
Candidate Profiling
        ↓
Job Search
        ↓
Job Analysis & Matching
        ↓
Application Preparation
```

The current implementation is focused primarily on the **Candidate Profiling** layer.

The profiling architecture is designed as a multi-agent system:

```text
ProfilingManager
│
├── SourceManager
│   └── SourceAgent
│
├── EvidenceManager        # planned
│   └── EvidenceAgent      # planned
│
└── ProfileManager         # planned
    └── ProfileAgent       # planned
```

At the current stage, the Source Processing workflow is the most developed part.

---

# Why This Architecture?

LLMs are useful for semantic reasoning, but they should not independently control workflow state.

The system therefore separates responsibilities.

### AI agents are responsible for

- interpreting candidate sources;
- identifying candidate facts;
- evaluating result quality;
- identifying uncertainty;
- deciding whether a result requires improvement;
- producing structured review feedback.

### Python infrastructure is responsible for

- request IDs;
- profiling run IDs;
- agent IDs;
- execution IDs;
- expected output types;
- execution attempts;
- execution lineage;
- source authorization;
- output validation;
- lifecycle transitions;
- result persistence;
- rework limits.

This creates a controlled agent workflow instead of relying on free-form autonomous execution.

---

# Candidate Source Processing

Candidate sources may currently include:

- local candidate documents;
- CVs;
- GitHub repositories.

A source is represented as a `CandidateSource`.

Each SourceAgent execution processes exactly one authorized source.

Example:

```text
CandidateSource
    ↓
SourceManager
    ↓
ExecutionRequestDraft
    ↓
Python-controlled ExecutionRequest
    ↓
ExecutionCoordinator
    ↓
SourceAgent
    ↓
ParsedSourceResult
```

---

# Controlled Execution Requests

The AI manager does not create complete execution requests.

It only produces an `ExecutionRequestDraft` containing:

```text
agent_type
input
```

Example:

```json
{
  "agent_type": "SOURCE_AGENT",
  "input": {
    "source_id": "source-123"
  }
}
```

Python then creates the actual `ExecutionRequest` and controls:

```text
request_id
run_id
execution mode
expected_output
```

This prevents the AI from inventing technical execution metadata.

---

# Persistent Agent Instances

The system distinguishes between:

```text
AgentInstance
```

and:

```text
AgentExecutionInstance
```

An `AgentInstance` represents a persistent worker.

One agent may execute multiple times:

```text
AgentInstance
agent-001
│
├── execution exec-001
│
└── execution exec-002
```

Each `AgentExecutionInstance` represents one concrete attempt and stores information such as:

```text
execution_id
request
attempt
previous_execution_id
input_snapshot
result
manager_review
```

This makes execution history and rework traceable.

---

# SourceAgent

The SourceAgent performs source-level interpretation.

Its job is to produce a structured:

```text
ParsedSourceResult
```

containing information such as:

- candidate facts;
- context;
- candidate contribution;
- methods;
- tools and resources;
- stakeholders;
- outcomes;
- provenance;
- uncertainties.

The SourceAgent does **not** approve its own result.

It also does not control execution IDs, attempts, or lifecycle state.

---

# Source Snapshots

When a source is processed for the first time, the exact content used by the SourceAgent is captured as an:

```text
input_snapshot
```

This snapshot is stored with the execution.

Example:

```text
AgentExecutionInstance
├── input_snapshot
├── result
└── manager_review
```

If the result later requires improvement, the same source snapshot can be reused instead of reading the external source again.

This is particularly useful for large GitHub repositories and reduces repeated:

- source reads;
- tool calls;
- token usage;
- processing time.

---

# Manager Review

Every successful worker result enters:

```text
NEEDS_MANAGER_REVIEW
```

The worker cannot set its own approval status.

The SourceManager reviews the result and chooses:

```text
APPROVED_BY_MANAGER
```

or:

```text
NEEDS_IMPROVEMENT
```

Reviews are structured using `ManagerReview`.

Example:

```json
{
  "status": "NEEDS_IMPROVEMENT",
  "feedback_items": [
    {
      "issue_type": "UNSUPPORTED_CONTRIBUTION",
      "description": "The result infers sole authorship without sufficient evidence.",
      "required_change": "Remove the unsupported authorship claim."
    }
  ]
}
```

Each feedback item contains:

```text
issue_type
description
required_change
```

---

# Controlled Review Tool

Managers do not directly modify execution state.

Reviews are submitted through a controlled tool:

```text
submit_manager_review
```

The manager provides:

```text
execution_id
ManagerReview
```

Python validates the review and applies it to the exact execution.

This prevents the manager from approving results merely through free-form text.

---

# Rework Workflow

When the SourceManager decides:

```text
NEEDS_IMPROVEMENT
```

the coordinator starts a controlled rework.

The same persistent agent receives:

```text
previous input snapshot
+
previous result
+
manager feedback
```

The agent then produces a revised result.

Example:

```text
exec-001
├── result V1
└── manager review
    └── NEEDS_IMPROVEMENT
            ↓
        same AgentInstance
            ↓
exec-002
├── previous_execution_id = exec-001
├── attempt = 2
├── same input snapshot
└── result V2
```

The revised result again receives:

```text
NEEDS_MANAGER_REVIEW
```

and must be reviewed independently.

Rework attempts are bounded to prevent uncontrolled execution loops.

---

# Current Source Processing Workflow

```text
SourceManager
    ↓
ExecutionRequestDraft
    ↓
ExecutionRequestFactory
    ↓
ExecutionRequest
    ↓
ExecutionPlan
    ↓
ExecutionCoordinator
    ↓
AgentInstance
    ↓
AgentExecutionInstance
    ↓
SourceAgent
    ↓
ReadCandidateSource
    ↓
input_snapshot
    ↓
ParsedSourceResult
    ↓
AgentRunOutput
    ↓
ExecutionCoordinator
    ↓
AgentExecutionResult
    ↓
NEEDS_MANAGER_REVIEW
    ↓
SourceManager
    ↓
ManagerReview
    ↓
submit_manager_review
    ↓
APPROVED_BY_MANAGER
        or
NEEDS_IMPROVEMENT
    ↓
controlled rework
```

---

# Project Structure

Relevant backend structure:

```text
backend/
└── app/
    └── ai/
        └── agents/
            └── profilling_agent/
                ├── agents/
                │   ├── profiling_manager/
                │   ├── source_ai/
                │   │   ├── source_manager/
                │   │   └── source_agent/
                │   └── moduls/
                │
                ├── schema/
                ├── services/
                └── tools/
```

Important components include:

```text
SourceManager
SourceAgent
ExecutionCoordinator
ExecutionRequestFactory
AgentInstance
AgentExecutionInstance
AgentExecutionResult
ManagerReview
ExecuteExecutionPlanTool
SubmitManagerReviewTool
ReadCandidateSource
```

---

# Technology Stack

Backend technologies currently include:

- Python
- FastAPI
- Pydantic v2
- smolagents
- Hugging Face model providers
- python-dotenv
- Uvicorn

The architecture is designed so AI models can later be replaced without rewriting the execution lifecycle.

---

# Evaluation-Driven Development

The profiling architecture is developed through repeated execution tests and evaluation reports.

Evaluation is used to detect problems such as:

- malformed AI outputs;
- incorrect tool schemas;
- result loss after partial failure;
- unsupported candidate claims;
- missing review transitions;
- uncontrolled retries;
- excessive source context.

Observed failures are then used to improve the architecture and agent contracts.

Evaluation reports are stored under:

```text
backend/evaluation/
```

---

# Documentation

Additional architecture documentation is available under:

```text
docs/
```

In particular:

```text
docs/AGENT_EXECUTION_ARCHITECTURE.md
```

contains a more detailed description of the execution lifecycle and agent architecture.

---

# Current Status

The project is under active development.

### Implemented or substantially developed

- candidate-source ingestion;
- file source processing;
- GitHub source processing;
- SourceManager;
- SourceAgent;
- structured source extraction;
- controlled execution requests;
- execution plans;
- deterministic ExecutionCoordinator;
- persistent agent instances;
- execution history;
- source snapshot preservation;
- manager review;
- structured review feedback;
- bounded rework;
- execution failure preservation.

### Planned / not yet complete

- EvidenceManager;
- EvidenceAgent;
- evidence consolidation;
- ProfileManager;
- ProfileAgent;
- final candidate profile generation;
- job-search agents;
- job matching;
- application generation;
- production persistence for agent executions;
- production frontend;
- complete end-to-end test coverage.

The project should therefore currently be considered an **active architecture and workflow implementation**, not a finished autonomous job-application product.

---

# Design Principles

The project currently follows five core principles:

```text
AI decides WHAT.

Python controls HOW.

Managers review QUALITY.

Workers perform DOMAIN WORK.

Infrastructure controls STATE.
```

The goal is controlled AI autonomy: allowing agents to reason and improve their work while keeping execution state, identity, history, validation, and lifecycle deterministic and inspectable.
