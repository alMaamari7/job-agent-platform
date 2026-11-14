# Agent Execution Architecture

## Purpose

This document describes the execution architecture used by the Candidate Profiling subsystem of the Job Agent Platform.

Its purpose is to define how AI managers, worker agents, execution infrastructure, review lifecycle, execution history, and rework interact.

The architecture is designed around one central principle:

> **AI decides what should be done. Python controls how it is executed.**

The goal is controlled AI autonomy.

AI agents remain responsible for semantic reasoning, interpretation, review, and domain-specific decisions.

Python infrastructure remains responsible for execution identity, lifecycle state, validation, lineage, persistence in memory, and bounded rework.

---

# 1. Architectural Goals

The execution architecture is designed to provide:

- deterministic execution metadata;
- traceable agent runs;
- controlled manager-to-worker delegation;
- explicit review lifecycle;
- persistent worker-agent instances;
- bounded rework loops;
- source-input preservation;
- independent failure handling;
- separation between AI decisions and technical state;
- reproducible execution history.

The system avoids allowing AI agents to directly control:

- execution IDs;
- request IDs;
- run IDs;
- attempt numbers;
- lifecycle state;
- retry count;
- execution lineage;
- approval transitions.

---

# 2. High-Level Architecture

The Candidate Profiling subsystem is structured around manager and worker agents.

Current and planned structure:

```text
ProfilingManager
│
├── SourceManager
│   └── SourceAgent
│
├── EvidenceManager
│   └── EvidenceAgent
│
└── ProfileManager
    └── ProfileAgent
```

The current implementation focuses primarily on:

```text
ProfilingManager
    ↓
SourceManager
    ↓
SourceAgent
```

Execution is mediated by deterministic Python infrastructure.

```text
AI Manager
    ↓
ExecutionRequestDraft
    ↓
Python Infrastructure
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
Worker Agent
```

---

# 3. Separation of Responsibilities

## 3.1 AI Manager Responsibilities

An AI manager may decide:

- which worker agent type should be used;
- which authorized input should be processed;
- whether a result is acceptable;
- whether improvement is required;
- what specifically must be improved.

An AI manager must not control technical execution metadata.

---

## 3.2 Worker Agent Responsibilities

A worker agent performs domain-specific processing.

For a `SourceAgent`, this includes:

- reading one authorized candidate source;
- interpreting source content;
- extracting structured candidate facts;
- preserving uncertainty;
- preserving provenance;
- identifying candidate contribution only when supported;
- returning a domain-specific result.

A worker does not approve its own result.

---

## 3.3 Python Infrastructure Responsibilities

Python infrastructure controls:

- `run_id`;
- `request_id`;
- `agent_id`;
- `execution_id`;
- `attempt`;
- `previous_execution_id`;
- expected output type;
- source authorization;
- execution routing;
- result validation;
- lifecycle state;
- review application;
- execution history;
- rework limits;
- failure handling.

---

# 4. Core Execution Objects

The architecture separates different concepts that are often incorrectly combined in agent systems.

---

# 4.1 ExecutionRequestDraft

`ExecutionRequestDraft` represents the AI manager's execution decision.

It contains only information the AI is allowed to choose.

Conceptually:

```python
class ExecutionRequestDraft(BaseModel):
    agent_type: AgentType
    input: dict[str, Any]
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

The draft does not contain:

```text
request_id
run_id
expected_output
execution_id
agent_id
attempt
previous_execution_id
```

These values are infrastructure-controlled.

---

# 4.2 ExecutionContext

`ExecutionContext` identifies the profiling run to which a request belongs.

Conceptually:

```python
class ExecutionContext(BaseModel):
    run_id: str
    mode: str | None
```

Example modes:

```text
INITIAL_PROFILE_BUILD
UPDATE_EXISTING_PROFILE
```

The execution context is created from trusted Python-controlled values.

---

# 4.3 ExecutionRequest

`ExecutionRequest` is the fully controlled executable request.

It wraps the AI-generated draft and adds Python-generated metadata.

Conceptually:

```python
class ExecutionRequest(BaseModel):
    execution_request_draft: ExecutionRequestDraft
    request_id: str
    expected_output: ExpectedOutputType
    execution_context: ExecutionContext
```

Relationship:

```text
ExecutionRequestDraft
        ↓
ExecutionRequestFactory
        ↓
ExecutionRequest
```

The `ExecutionRequestFactory` is responsible for creating:

- `request_id`;
- expected output type;
- execution context.

---

# 4.4 ExecutionPlan

An `ExecutionPlan` groups controlled execution requests.

Conceptually:

```python
class ExecutionPlan(BaseModel):
    execution_requests: list[ExecutionRequest]
```

The manager decides what work is required.

Python controls the final request objects contained in the plan.

---

# 5. ExecutionRequestFactory

The `ExecutionRequestFactory` converts an AI-generated draft into a controlled execution request.

Input:

```text
ExecutionRequestDraft
run_id
mode
```

Output:

```text
ExecutionRequest
```

Python determines the expected output based on the agent type.

Example mapping:

```text
SOURCE_AGENT
→ ParsedSourceResult

EVIDENCE_AGENT
→ EvidenceResult

PROFILE_AGENT
→ ProfileResult
```

This prevents the AI from selecting arbitrary or inconsistent output contracts.

---

# 6. ExecutionCoordinator

`ExecutionCoordinator` is the deterministic execution layer.

It is not an AI agent.

Its responsibilities include:

- resolving the correct persistent agent instance;
- creating execution instances;
- invoking worker agents;
- preserving input snapshots;
- preserving results;
- creating controlled external execution results;
- applying manager reviews;
- finding previous executions;
- coordinating rework;
- enforcing execution limits;
- preserving lineage.

High-level flow:

```text
ExecutionPlan
    ↓
ExecutionCoordinator.execute()
    ↓
resolve AgentInstance
    ↓
create AgentExecutionInstance
    ↓
execute worker
    ↓
store result
    ↓
build AgentExecutionResult
```

---

# 7. AgentInstance

`AgentInstance` represents one persistent runtime worker agent.

Conceptually:

```python
@dataclass
class AgentInstance:
    agent_id: str
    agent: Any
    executions: list[AgentExecutionInstance]
```

A single `AgentInstance` may execute multiple times.

Example:

```text
AgentInstance
agent_id = agent-001
│
├── exec-001
├── exec-002
└── exec-003
```

This allows the same persistent worker to improve its own previous output.

The system does not rely on hidden model memory for this improvement.

Instead, previous state is explicitly passed back to the worker.

---

# 8. AgentExecutionInstance

`AgentExecutionInstance` represents one concrete execution attempt.

Conceptually:

```python
@dataclass
class AgentExecutionInstance:
    execution_id: str
    request: ExecutionRequest
    attempt: int
    previous_execution_id: str | None
    input_snapshot: Any | None
    result: Any | None
    manager_review: ManagerReview | None
```

It represents exactly one execution.

Example:

```text
AgentExecutionInstance
├── execution_id = exec-001
├── request = req-001
├── attempt = 1
├── previous_execution_id = None
├── input_snapshot = source content
├── result = ParsedSourceResult V1
└── manager_review = NEEDS_IMPROVEMENT
```

A later execution may reference it:

```text
exec-002
├── attempt = 2
├── previous_execution_id = exec-001
└── result = ParsedSourceResult V2
```

---

# 9. AgentRunOutput

Worker execution returns an internal runtime object.

Conceptually:

```python
@dataclass
class AgentRunOutput:
    result: Any
    input_snapshot: Any | None
```

For a SourceAgent:

```text
result
→ ParsedSourceResult

input_snapshot
→ exact source content used during execution
```

This object is internal to the execution infrastructure.

It is not the result shown directly to the manager.

---

# 10. SourceAgent Execution

The SourceAgent supports two execution modes:

```text
Initial execution
Rework execution
```

---

# 10.1 Initial SourceAgent Execution

Input:

```text
CandidateSource
```

Flow:

```text
CandidateSource
    ↓
ReadCandidateSource
    ↓
source content
    ↓
input snapshot
    ↓
AI interpretation
    ↓
ParsedSourceResult
    ↓
AgentRunOutput
```

The source is read exactly once for that execution.

The content returned by the source reader is preserved as:

```text
input_snapshot
```

---

# 10.2 Rework SourceAgent Execution

A rework execution does not reread the source.

Input:

```text
previous input_snapshot
previous ParsedSourceResult
manager feedback
```

Conceptually:

```python
SourceAgent.run(
    input_snapshot=previous_snapshot,
    previous_result=previous_result,
    review_feedback=feedback,
)
```

This reduces:

- external reads;
- tool calls;
- token usage;
- latency;
- repeated parsing.

The same source evidence is reused for the correction.

---

# 11. ReadCandidateSource

`ReadCandidateSource` is the controlled source-reading tool used by the SourceAgent.

Supported source types currently include:

```text
FILE
GITHUB
```

The tool maintains:

```text
last_source_id
last_snapshot
```

After reading a source:

```python
self.last_source_id = source_id
self.last_snapshot = content
```

The exact returned content becomes the execution input snapshot.

---

# 12. ParsedSourceResult

`ParsedSourceResult` is the domain-specific result produced by a SourceAgent.

Conceptually:

```text
ParsedSourceResult
├── source_id
├── source_type
├── status
├── facts
├── uncertainties
└── processing_notes
```

It contains semantic source-processing information only.

It does not contain execution lifecycle state.

---

# 13. Source Fact Model

A source fact may contain:

```text
fact_id
statement
fact_type
context
contribution
methods
tools_or_resources
stakeholders
outcomes
source_locator
```

The goal is to preserve structured evidence from the original source without prematurely converting it into a final candidate profile.

---

# 14. Candidate Contribution Rules

Candidate contribution is intentionally conservative.

If contribution is explicitly supported:

```json
{
  "level": "implemented",
  "description": "Implemented the API layer."
}
```

If contribution is not supported:

```json
"contribution": null
```

The system must not produce:

```json
{
  "level": null,
  "description": null
}
```

Repository ownership alone does not prove:

- sole authorship;
- leadership;
- complete implementation;
- ownership of all code;
- creation of all repository content.

---

# 15. AgentExecutionResult

The manager does not receive the raw worker result directly.

Python wraps the domain result in an `AgentExecutionResult`.

Conceptually:

```python
class AgentExecutionResult(BaseModel):
    agent_id: str
    execution_id: str
    request_id: str
    attempt: int
    previous_execution_id: str | None
    execution_status: ReviewStatus
    result: Any
```

Example:

```text
AgentExecutionResult
├── agent_id = agent-001
├── execution_id = exec-001
├── request_id = req-001
├── attempt = 1
├── previous_execution_id = None
├── execution_status = NEEDS_MANAGER_REVIEW
└── result = ParsedSourceResult
```

Python controls all execution metadata.

---

# 16. ReviewStatus

The review lifecycle uses:

```text
NEEDS_MANAGER_REVIEW
NEEDS_IMPROVEMENT
APPROVED_BY_MANAGER
EXECUTION_FAILED
```

Successful worker executions always enter:

```text
NEEDS_MANAGER_REVIEW
```

A worker cannot assign:

```text
APPROVED_BY_MANAGER
```

to itself.

---

# 17. ManagerReview

A manager review is structured.

Conceptually:

```python
class ManagerReview(BaseModel):
    status: ReviewStatus
    feedback_items: list[ReviewFeedbackItem]
```

A feedback item contains:

```python
class ReviewFeedbackItem(BaseModel):
    issue_type: str
    description: str
    required_change: str
```

Example:

```json
{
  "status": "NEEDS_IMPROVEMENT",
  "feedback_items": [
    {
      "issue_type": "UNSUPPORTED_CONTRIBUTION",
      "description": "The result infers sole authorship without sufficient source evidence.",
      "required_change": "Remove the unsupported authorship claim."
    }
  ]
}
```

---

# 18. ManagerReview Validation

The review contract enforces lifecycle consistency.

Rules:

```text
NEEDS_IMPROVEMENT
→ requires at least one feedback item

APPROVED_BY_MANAGER
→ feedback_items must be empty
```

Invalid reviews are rejected before reaching the coordinator.

---

# 19. SubmitManagerReviewTool

Managers do not modify execution state directly.

They submit reviews through:

```text
submit_manager_review
```

Input:

```text
execution_id
review
```

The tool:

1. validates the review with Pydantic;
2. calls `ExecutionCoordinator.apply_manager_review()`;
3. returns the resulting workflow state.

The `execution_id` identifies exactly which execution is being reviewed.

---

# 20. Applying Manager Review

The coordinator performs:

```python
execution = self.get_execution(execution_id)
```

Then:

```python
execution.manager_review = review
```

Each execution may receive only one manager review.

A second review for the same execution is rejected.

This prevents contradictory state changes.

---

# 21. Approval Flow

If the manager submits:

```text
APPROVED_BY_MANAGER
```

the execution is complete.

Example:

```text
exec-001
├── result = ParsedSourceResult
└── manager_review
    └── APPROVED_BY_MANAGER
```

No rework execution is created.

---

# 22. Improvement Flow

If the manager submits:

```text
NEEDS_IMPROVEMENT
```

the coordinator starts a controlled rework.

The previous execution provides:

```text
input_snapshot
result
manager_review
```

The coordinator identifies the persistent worker that owns the execution.

---

# 23. Finding the Correct Agent

The manager does not choose the runtime worker directly.

It submits only:

```text
execution_id
```

The coordinator resolves:

```text
execution_id
    ↓
AgentExecutionInstance
    ↓
AgentInstance
    ↓
agent_instance.agent
```

This prevents the AI manager from arbitrarily selecting runtime objects.

---

# 24. Controlled Rework

Rework flow:

```text
exec-001
├── input_snapshot
├── result V1
└── ManagerReview
    └── NEEDS_IMPROVEMENT
            ↓
ExecutionCoordinator
            ↓
same AgentInstance
            ↓
exec-002
├── attempt = 2
├── previous_execution_id = exec-001
├── same input_snapshot
└── result V2
```

The same persistent worker receives:

```text
previous snapshot
previous result
manager feedback
```

---

# 25. Rework Request Creation

Rework creates a new controlled request.

The previous execution draft is reused:

```text
previous ExecutionRequestDraft
```

Python creates a new:

```text
request_id
```

while preserving:

```text
run_id
mode
```

A new `AgentExecutionInstance` is then created.

---

# 26. Execution Lineage

Execution lineage is represented through:

```text
previous_execution_id
```

Example:

```text
exec-001
    ↓
exec-002
    ↓
exec-003
```

With:

```text
exec-002.previous_execution_id = exec-001
exec-003.previous_execution_id = exec-002
```

This provides a complete rework chain.

---

# 27. Attempt Tracking

Each execution has an attempt number.

Example:

```text
attempt 1
→ initial execution

attempt 2
→ first rework

attempt 3
→ second rework
```

Attempt numbers are controlled by Python.

The AI does not choose them.

---

# 28. Maximum Execution Attempts

Rework is bounded.

The coordinator defines a maximum execution-attempt limit.

Example:

```text
MAX_EXECUTION_ATTEMPTS = 3
```

Before creating another rework execution, the coordinator checks:

```text
previous_execution.attempt >= MAX_EXECUTION_ATTEMPTS
```

If the limit is reached, no further rework execution is created.

This prevents infinite agent loops.

---

# 29. Reworked Results Require New Review

A successful rework result receives:

```text
NEEDS_MANAGER_REVIEW
```

again.

Example:

```text
exec-001
→ NEEDS_IMPROVEMENT

exec-002
→ NEEDS_MANAGER_REVIEW
```

The manager must independently review `exec-002`.

Rework does not imply approval.

---

# 30. Execution Failure

If worker execution fails, the coordinator creates an `AgentExecutionResult` with:

```text
EXECUTION_FAILED
```

The failure is preserved independently from other successful executions.

Example:

```text
CV execution
→ success

GitHub execution
→ failure
```

The CV result must remain available.

One worker failure must not erase unrelated successful results.

---

# 31. Initial Execution Flow

Complete initial SourceAgent flow:

```text
SourceManager
    ↓
ExecutionRequestDraft
    ↓
ExecuteExecutionPlanTool
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
SourceAgent.run(source)
    ↓
ReadCandidateSource
    ↓
input_snapshot
    ↓
AI interpretation
    ↓
ParsedSourceResult
    ↓
AgentRunOutput
    ↓
execution.input_snapshot
execution.result
    ↓
AgentExecutionResult
    ↓
NEEDS_MANAGER_REVIEW
```

---

# 32. Review and Rework Flow

Complete review loop:

```text
AgentExecutionResult
execution_status = NEEDS_MANAGER_REVIEW
        ↓
SourceManager
        ↓
ManagerReview
        ↓
SubmitManagerReviewTool
        ↓
Pydantic validation
        ↓
ExecutionCoordinator.apply_manager_review()
        ↓
store ManagerReview
        ↓
        ├── APPROVED_BY_MANAGER
        │       ↓
        │     complete
        │
        └── NEEDS_IMPROVEMENT
                ↓
        find previous execution
                ↓
        find persistent AgentInstance
                ↓
        retrieve:
        - input_snapshot
        - previous result
        - manager feedback
                ↓
        create new request
                ↓
        create new execution
                ↓
        same worker agent
                ↓
        revised result
                ↓
        NEEDS_MANAGER_REVIEW
```

---

# 33. Why the Same Agent Is Reused

The architecture intentionally keeps the same `AgentInstance` alive during the profiling runtime.

This allows:

```text
agent-001
├── exec-001
├── exec-002
└── exec-003
```

However, the architecture does not depend on implicit model memory.

Instead, each rework receives explicit state:

```text
previous input
previous output
manager feedback
```

This makes the process:

- reproducible;
- inspectable;
- testable;
- less dependent on provider-specific conversation memory.

---

# 34. Why Input Snapshots Are Preserved

Source processing may be expensive.

A GitHub source may require:

- repository retrieval;
- file traversal;
- large context construction;
- significant token consumption.

Repeatedly rereading the same source during rework is unnecessary.

Instead:

```text
initial execution
→ read once
→ store input_snapshot

rework
→ reuse input_snapshot
```

This reduces both cost and execution variability.

---

# 35. Tool Boundaries

The current controlled tools include:

```text
read_candidate_source
execute_execution_plan
submit_manager_review
```

Each has a specific responsibility.

## read_candidate_source

Worker-facing source access.

## execute_execution_plan

Manager-facing controlled execution capability.

## submit_manager_review

Manager-facing controlled lifecycle transition.

No tool should silently perform responsibilities belonging to another layer.

---

# 36. Lifecycle Ownership

Lifecycle ownership is intentionally separated.

```text
SourceAgent
→ produces domain result

ExecutionCoordinator
→ assigns NEEDS_MANAGER_REVIEW

SourceManager
→ decides APPROVED or NEEDS_IMPROVEMENT

SubmitManagerReviewTool
→ validates manager decision

ExecutionCoordinator
→ applies lifecycle transition

SourceAgent
→ performs rework if required
```

No single AI agent controls the entire lifecycle.

---

# 37. State Ownership

The main state ownership model is:

```text
Profiling run state
→ Python infrastructure

Execution state
→ ExecutionCoordinator

Agent runtime state
→ AgentInstance

Individual run state
→ AgentExecutionInstance

Worker semantic result
→ domain result schema

Manager decision
→ ManagerReview
```

---

# 38. Current In-Memory Persistence

At the current stage, persistent agent and execution state is maintained in memory.

Conceptually:

```python
self.agents: dict[str, AgentInstance]
self.executions: dict[str, AgentExecutionInstance]
```

This is sufficient for architecture validation and local execution.

It is not yet production-grade durable persistence.

Future versions may move execution state to a database or event store.

---

# 39. Current Limitations

The current execution architecture has several known limitations.

## In-memory runtime state

Agent instances and execution history do not currently survive process restarts.

## Source snapshot size

Large GitHub snapshots may consume substantial memory.

Future versions may use:

- content-addressed storage;
- chunk references;
- source snapshot IDs;
- persistent blob storage.

## Generic result typing

Some infrastructure objects currently use generic result types.

Future versions may use discriminated result unions.

## Execution concurrency

Current workflow is primarily designed and tested as controlled sequential execution.

Parallel execution requires additional state and synchronization considerations.

---

# 40. Planned Extension to Other Profiling Agents

The execution architecture is intentionally generic.

The same lifecycle should support:

```text
SourceAgent
EvidenceAgent
ProfileAgent
future profiling workers
```

For example:

```text
EvidenceAgent
→ EvidenceResult

ProfileAgent
→ ProfileResult
```

The same infrastructure can still control:

```text
AgentInstance
AgentExecutionInstance
AgentExecutionResult
ManagerReview
rework
lineage
attempts
```

---

# 41. Evaluation-Driven Architecture

The current execution model was developed through repeated evaluation of real execution logs.

Important observed failure classes included:

- AI-generated invalid execution schemas;
- incorrect enum usage;
- successful results being lost after another worker failed;
- unsupported contribution claims;
- missing manager approval transitions;
- repeated source processing;
- uncontrolled execution retry behavior;
- excessive repository context.

The current architecture directly addresses these failure modes.

---

# 42. Key Invariants

The execution architecture should preserve the following invariants.

### Invariant 1

The AI manager cannot generate technical execution IDs.

### Invariant 2

A successful worker result always enters manager review.

### Invariant 3

A worker cannot approve itself.

### Invariant 4

Every execution may receive at most one manager review.

### Invariant 5

`NEEDS_IMPROVEMENT` requires structured feedback.

### Invariant 6

Rework creates a new execution.

### Invariant 7

Rework retains execution lineage.

### Invariant 8

Rework uses the same persistent worker agent.

### Invariant 9

Rework receives the previous result explicitly.

### Invariant 10

Rework reuses the previous input snapshot.

### Invariant 11

Execution attempts are bounded.

### Invariant 12

One failed execution does not erase unrelated successful results.

---

# 43. Complete Architecture Summary

```text
SourceManager AI
    ↓
ExecutionRequestDraft
    │
    │ AI controls:
    │ - agent_type
    │ - domain input
    │
    ↓
Python Infrastructure
    │
    │ controls:
    │ - request_id
    │ - run_id
    │ - expected_output
    │
    ↓
ExecutionRequest
    ↓
ExecutionPlan
    ↓
ExecutionCoordinator
    ↓
AgentInstance
    │
    ├── agent_id
    ├── persistent worker
    └── executions
            ↓
    AgentExecutionInstance
    ├── execution_id
    ├── attempt
    ├── lineage
    ├── input_snapshot
    ├── result
    └── manager_review
            ↓
        Worker Agent
            ↓
        Domain Result
            ↓
        AgentExecutionResult
            ↓
    NEEDS_MANAGER_REVIEW
            ↓
        Manager Review
            ↓
    SubmitManagerReviewTool
            ↓
    ExecutionCoordinator
        ├── APPROVED_BY_MANAGER
        │
        └── NEEDS_IMPROVEMENT
                ↓
        same AgentInstance
                ↓
        new AgentExecutionInstance
                ↓
        previous snapshot
        previous result
        manager feedback
                ↓
        revised result
                ↓
        NEEDS_MANAGER_REVIEW
```

---

# 44. Core Design Principle

The execution architecture can be summarized as:

```text
AI decides WHAT.

Python controls HOW.

Workers perform DOMAIN WORK.

Managers review QUALITY.

Infrastructure controls STATE.

Every execution is TRACEABLE.

Every rework is BOUNDED.

Every lifecycle transition is EXPLICIT.
```

The architecture is designed to make AI agents useful without allowing them to silently control execution state, identity, history, or approval.
