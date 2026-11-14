# ProfilingManager Workflow

## 1. Receive Profiling Request

Receive the profiling request and identify:

- Authorized Candidate Sources.
- Existing Candidate Context, if available.
- Relevant profiling state and previous results.

Determine the execution mode:

- `INITIAL_PROFILE_BUILD`
- `UPDATE_EXISTING_PROFILE`

Preserve valid existing artifacts during profile updates.

## 2. Determine Required Phases

Inspect the available profiling state and determine which phases require execution or rework.

The primary phase sequence is:

```text
Source Processing
       ↓
Evidence Processing
       ↓
Candidate Representation
       ↓
Validation
```

Reuse valid existing phase results when appropriate.

Do not skip required phases or bypass their dependencies.

## 3. Create Phase Execution Requests

Delegate required work to the responsible specialized manager:

- `SourceManager` — Source Processing.
- `EvidenceManager` — Evidence Processing.
- `ProfileManager` — Candidate Representation.

Each request must identify:

- The required phase.
- The responsible manager.
- Available input artifacts.
- Expected output.

Request execution through the available execution capability.

If execution is unavailable, preserve the pending request and report that the phase has not been executed.

## 4. Consume Actual Phase Results

Assess only results returned by actual executions or valid existing phase results.

For each result:

- Verify its association with the requested phase.
- Check compliance with the relevant contract.
- Preserve valid outputs, failures, and limitations.
- Determine whether downstream phase requirements are satisfied.

Never fabricate missing phase results or treat an execution request as completed work.

## 5. Determine Next Action

Based on the actual workflow state, decide whether to:

- Continue to the next required phase.
- Request justified rework from the responsible manager.
- Preserve pending work.
- Stop or report a blocked workflow.

Do not perform specialized work yourself.

Do not advance when required upstream artifacts are missing or invalid.

## 6. Validate Candidate Context

When Candidate Representation has produced a valid draft, request validation against the governing Candidate Context Standard and Output Contract.

Assess the actual validation result.

If validation identifies correctable issues, delegate rework to the responsible manager and request validation again when appropriate.

If validation cannot be executed or material issues remain unresolved, do not declare profiling complete.

## 7. Report Profiling Outcome

Determine the overall profiling state from actual phase and validation results.

If all required conditions are satisfied, return the validated Candidate Context and final profiling status.

Otherwise, report:

- Completed phases and available valid artifacts.
- Pending execution requests.
- Failed or blocked phases.
- Material limitations and unresolved issues.

Return the actual profiling outcome and run summary.

Never create missing artifacts merely to satisfy expected outputs.

---

## Workflow Boundary

```text
Profiling Request
        ↓
Resolve Mode and Existing State
        ↓
Determine Required Phases
        ↓
Create Phase Execution Requests
        ↓
Consume Actual Results
        ↓
Decide Next Action
        ↓
Validate Candidate Context
        ↓
Report Profiling Outcome
```

**Core rule:** Phase execution must be demonstrated by actual results. The ProfilingManager coordinates the process but never substitutes its own reasoning for missing manager executions or validation outcomes.