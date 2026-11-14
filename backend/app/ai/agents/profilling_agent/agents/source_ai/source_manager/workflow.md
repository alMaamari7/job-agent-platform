# SourceManager Workflow

## 1. Purpose

The SourceManager operates in two distinct stages:

- **Stage 1 — Planning:** Determine required work and produce an `ExecutionPlan`.
- **Stage 2 — Assessment:** Evaluate actual execution results and produce a `SourceProcessingResult`.

Execution is performed outside the SourceManager.

## Stage 1 — Planning

### 2. Inspect Authorized Sources

Receive the `SourceProcessingAssignment` from the ProfilingManager.

Identify:

- Authorized Candidate Sources.
- Execution mode: `INITIAL_PROFILE_BUILD` or `UPDATE_EXISTING_PROFILE`.
- Valid existing source-processing results, if available.
- Applicable processing constraints.

Do not expand the authorized source set.

### 3. Determine Required Processing

For each authorized source, decide whether to:

- Process it for the first time.
- Reprocess it because its content changed or its previous result is invalid.
- Reuse an existing result that remains valid and applicable.

Do not request unnecessary reprocessing.

### 4. Create ExecutionPlan

Create one `ExecutionPlan` containing the required SourceAgent tasks.

Each task must identify:

- The authorized `source_id`.
- The assigned `SOURCE_AGENT` type.
- The expected `ParsedSourceResult`.
- A unique `request_id`.

**Each task processes exactly one Candidate Source.**

An empty plan is valid when all required results can be reused.

Return the `ExecutionPlan` to the execution layer.

**Stage 1 ends here. No execution or processing success may be claimed.**

## Stage 2 — Assessment

### 5. Consume Actual Execution Results

Receive `AgentExecutionResult[]` associated with the original `ExecutionPlan`.

For each result:

- Verify that it corresponds to a planned task and authorized source.
- Check its execution status.
- Validate any returned `ParsedSourceResult` against the SourceAgent contract.
- Preserve valid results and reported failures or limitations.

Distinguish successful agent execution from successful source parsing.

Never fabricate missing results or infer successful execution from a submitted plan.

### 6. Determine Rework Requirements

Evaluate the actual results and valid reusable results.

For each unresolved source, decide whether to:

- Accept its current result.
- Create a new `ExecutionPlan` for justified rework.
- Preserve the unresolved failure or limitation.

Respect execution constraints and retry limits.

A rework plan starts another execution cycle. It does not prove that a retry occurred.

### 7. Produce SourceProcessingResult

When assessment is ready to report the phase state, build the `SourceProcessingResult` using only:

- Valid existing `ParsedSourceResult` objects.
- Valid results returned by actual execution.
- Verified execution failures and unresolved issues.

Account for every authorized source.

Determine whether the phase is `COMPLETE`, `COMPLETE_WITH_LIMITATIONS`, `INCOMPLETE`, or `BLOCKED`.

Return the `SourceProcessingResult` to the ProfilingManager.

Do not perform Evidence Processing or generate candidate-level conclusions.

---

## Workflow Overview

```text
ProfilingManager
       |
       | SourceProcessingAssignment
       v
SourceManager
       |
       | STAGE 1 — PLANNING
       | Inspect sources
       | Determine required work
       v
ExecutionPlan
       |
       v
Execution Layer
       |
       | Execute SourceAgent tasks
       v
AgentExecutionResult[]
       |
       v
SourceManager
       |
       | STAGE 2 — ASSESSMENT
       | Validate results
       | Determine rework if needed
       | Assess phase status
       v
SourceProcessingResult
       |
       v
ProfilingManager
```

## Core Rule

**Planning, execution, and assessment are separate activities.**

The SourceManager creates execution plans and assesses actual results. It never presents planned execution as completed work.