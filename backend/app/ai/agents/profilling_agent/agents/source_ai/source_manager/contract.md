# SourceManager Contract

## 1. Purpose

This contract defines the data boundaries of the SourceManager.

The SourceManager operates in two distinct stages:

1. **Planning:** Determine required work and produce an `ExecutionPlan`.
2. **Assessment:** Evaluate actual execution results and produce a `SourceProcessingResult`.

Planning does not constitute execution.

## 2. Input Contract

The SourceManager receives a `SourceProcessingAssignment`.

```yaml
execution_mode: INITIAL_PROFILE_BUILD | UPDATE_EXISTING_PROFILE

authorized_sources:
  - CandidateSource

existing_results:
  - ParsedSourceResult

execution_constraints:
  max_retries: null
```

Requirements:

- Process only explicitly authorized sources.
- Reuse existing results only when valid and applicable.
- Preserve source identity across both stages.
- Never expand the authorized source set.

## 3. Downstream Contract — ExecutionPlan

**Direction:** SourceManager → Execution Layer

**Stage:** Planning

The SourceManager produces an `ExecutionPlan` describing the required SourceAgent tasks.

```yaml
plan_id: "..."

tasks:
  - request_id: "..."
    agent_type: SOURCE_AGENT
    source_id: "..."
    expected_output: ParsedSourceResult
```

Rules:

- Each task references exactly one authorized Candidate Source.
- Only sources requiring processing receive new tasks.
- An empty task list is valid when all required results can be reused.
- The plan contains no fabricated execution results.
- Producing an `ExecutionPlan` does not mean any task has executed.

The execution layer is responsible for executing the requested tasks.

## 4. Execution Feedback Contract — AgentExecutionResult

**Direction:** Execution Layer → SourceManager

**Stage:** Assessment

The SourceManager receives actual execution feedback corresponding to its plan.

```yaml
plan_id: "..."

execution_results:
  - request_id: "..."
    source_id: "..."
    execution_status: COMPLETED | FAILED | TIMEOUT | CANCELLED
    output: ParsedSourceResult | null
    error: null | "..."
```

Rules:

- Every execution result must correspond to a known task.
- Results must preserve the assigned source identity.
- A completed execution does not automatically imply successful source parsing.
- Source-level outputs must satisfy the SourceAgent contract.
- Missing or invalid feedback must never be interpreted as successful execution.

Distinguish:

```text
AgentExecutionResult.execution_status
    → Did the execution complete?

ParsedSourceResult.status
    → Was the source successfully processed?
```

The SourceManager must never fabricate either status.

## 5. Rework Contract

When actual execution feedback establishes a recoverable problem, the SourceManager may produce a new `ExecutionPlan` for rework.

Rework must:

- Reference the original authorized sources.
- Identify only tasks requiring another attempt.
- Respect applicable retry and execution constraints.
- Preserve previously valid results.
- Remain distinguishable from completed execution.

A rework plan is still only a request. It is not evidence that a retry occurred.

## 6. Upstream Contract — SourceProcessingResult

**Direction:** SourceManager → ProfilingManager

**Stage:** Assessment

After evaluating actual execution feedback and valid existing results, the SourceManager produces a `SourceProcessingResult`.

```yaml
status: COMPLETE | COMPLETE_WITH_LIMITATIONS | INCOMPLETE | BLOCKED

parsed_source_results:
  - ParsedSourceResult

source_issues:
  - source_id: "..."
    reason: "..."

processing_summary:
  authorized: 0
  completed: 0
  pending: 0
  failed: 0
```

Requirements:

- Include only valid existing or actually returned source results.
- Preserve failures, unavailable sources, and unresolved limitations.
- Account for every authorized source.
- Never fabricate `ParsedSourceResult` objects.
- Report the actual phase state, not the intended outcome.

If execution feedback is missing for required tasks, the SourceManager cannot claim that Source Processing completed.

Pending work must remain identifiable for subsequent execution or recovery.

## 7. Phase Status Contract

| Status | Meaning |
|---|---|
| `COMPLETE` | All required sources have valid processing results without material limitations. |
| `COMPLETE_WITH_LIMITATIONS` | Processing reached a terminal state with usable results and documented limitations. |
| `INCOMPLETE` | Required work remains pending or recoverable. |
| `BLOCKED` | Required processing cannot currently proceed. |

An `ExecutionPlan` alone never establishes a phase status.

A phase status is determined only during assessment, using actual execution feedback and valid existing results.

## 8. Integrity Rules

1. **Authorization:** Every task and result references an authorized source.
2. **Source isolation:** Each SourceAgent task processes exactly one source.
3. **Traceability:** Every execution result maps to a known planned task.
4. **Execution authenticity:** Requested tasks are never represented as executed tasks.
5. **Result validity:** Invalid or missing outputs are never treated as successful parsing.
6. **Failure isolation:** Failures do not invalidate unrelated successful results.
7. **Semantic boundary:** The SourceManager does not interpret source content, generate facts, or perform evidence synthesis.

## 9. Two-Stage Handoff

```text
ProfilingManager
       |
       | SourceProcessingAssignment
       v
SourceManager
       |
       | Stage 1: ExecutionPlan
       v
Execution Layer
       |
       | Execute SourceAgent tasks
       |
       | AgentExecutionResult[]
       v
SourceManager
       |
       | Stage 2: SourceProcessingResult
       v
ProfilingManager
```

If execution is not available during Stage 1, the SourceManager returns the `ExecutionPlan` for later execution.

It must not create a `BLOCKED` SourceProcessingResult merely because the planned tasks have not yet executed.

If execution was attempted but cannot proceed or complete, Stage 2 may report the actual incomplete or blocked state.

## 10. Contract Boundary

**Initial input:** `SourceProcessingAssignment`

**Stage 1 output:** `ExecutionPlan`

**Stage 2 input:** `AgentExecutionResult[]` associated with the plan

**Stage 2 output:** `SourceProcessingResult`

The SourceManager never creates Evidence Records, candidate capabilities, or Candidate Context artifacts.

**Final rule: Plan first. Assess actual execution feedback second. Report the phase result only after assessment.**