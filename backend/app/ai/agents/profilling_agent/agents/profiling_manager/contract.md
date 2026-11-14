# ProfilingManager Contract

## 1. Purpose

This contract defines the input, output, and data integrity requirements of the `ProfilingManager`.

The ProfilingManager coordinates the Candidate Profiling workflow without performing specialized semantic processing.

All reported outcomes must be supported by actual phase results or valid existing artifacts.

## 2. Input Contract

The ProfilingManager receives one `ProfilingRequest`.

Conceptual structure:

```yaml
authorized_sources:
  - CandidateSource

requested_mode: null | INITIAL_PROFILE_BUILD | UPDATE_EXISTING_PROFILE

existing_candidate_context: null | CandidateContext

existing_profiling_state: null | ProfilingState
```

Requirements:

- Use only authorized Candidate Sources.
- Resolve exactly one execution mode.
- Preserve valid existing artifacts during updates.
- Do not assume that existing artifacts are valid without checking their applicability.

## 3. Phase Execution Request

For each required profiling phase, the ProfilingManager produces a `PhaseExecutionRequest`.

```yaml
request_id: "..."
phase: SOURCE_PROCESSING | EVIDENCE_PROCESSING | PROFILE_PROCESSING
responsible_manager: "..."
input_artifacts:
  - "..."
expected_output: "..."
```

Each request must:

- Identify one profiling phase and its responsible manager.
- Include the required available inputs.
- Specify the expected phase output.
- Respect upstream dependencies.

A request represents planned work, not completed execution.

## 4. Phase Execution Result

The ProfilingManager consumes actual `PhaseExecutionResult` objects.

```yaml
request_id: "..."
phase: "..."

execution_status: COMPLETED | FAILED | TIMEOUT | CANCELLED

output: null | PhaseResult
error: null | "..."
```

Requirements:

- Every result must correspond to a known phase request.
- Phase outputs must satisfy their respective contracts.
- A completed execution does not automatically mean the phase succeeded.
- Missing or invalid results must never be treated as successful processing.

Never fabricate phase results or execution outcomes.

## 5. Phase Result Contracts

Each profiling phase produces its own specialized result.

| Phase | Responsible manager | Expected output |
|---|---|---|
| Source Processing | SourceManager | `SourceProcessingOutcome` |
| Evidence Processing | EvidenceManager | `EvidenceProcessingResult` |
| Candidate Representation | ProfileManager | `ProfileProcessingResult` |

Phase results must preserve relevant artifacts, processing status, errors, and limitations.

The ProfilingManager passes valid upstream artifacts to downstream phases without modifying their semantic content.

## 6. Validation Contract

Candidate Context validation is required before successful finalization.

Conceptual result:

```yaml
passed: true | false
errors:
  - "..."
warnings:
  - "..."
```

Validation must establish compliance with the governing Candidate Context Standard and Output Contract.

The required Candidate Context structure is:

```text
candidate_context/
├── PROFILE.md
├── SOURCE_INDEX.md
├── EVIDENCE_INDEX.md
├── CAPABILITY_MAP.md
├── LIMITATIONS.md
└── profile/
    └── <candidate-specific sections>.md
```

Validation must not be reported as successful without an actual validation result.

## 7. Output Contract

The ProfilingManager returns one `ProfilingOutcome`.

Conceptual structure:

```yaml
status: COMPLETE | COMPLETE_WITH_LIMITATIONS | INCOMPLETE | BLOCKED

candidate_context: null | CandidateContext

phase_results:
  source_processing: null | SourceProcessingOutcome
  evidence_processing: null | EvidenceProcessingResult
  profile_processing: null | ProfileProcessingResult

validation_result: null | ValidationResult

pending_requests:
  - PhaseExecutionRequest

unresolved_issues:
  - phase: "..."
    reason: "..."

run_summary:
  mode: "..."
  completed_phases: []
  failed_phases: []
  pending_phases: []
  limitations: []
```

The outcome must accurately represent completed, pending, failed, and blocked work.

If execution is unavailable, return the pending requests and unresolved workflow state instead of fabricated phase results.

## 8. Completion Contract

| Status | Meaning |
|---|---|
| `COMPLETE` | Required phases completed, Candidate Context validated, and no material limitations remain. |
| `COMPLETE_WITH_LIMITATIONS` | A validated, usable Candidate Context exists with explicitly documented limitations. |
| `INCOMPLETE` | Required processing or validation remains unfinished or unresolved. |
| `BLOCKED` | Required work cannot currently proceed. |

Neither `COMPLETE` nor `COMPLETE_WITH_LIMITATIONS` is permitted without successful validation.

An incomplete or blocked result must explain why the workflow cannot be finalized.

## 9. Integrity Rules

The following invariants are mandatory:

1. **Authorization:** Every processed source belongs to the authorized source set.
2. **Execution authenticity:** Execution requests are never presented as completed executions.
3. **Phase traceability:** Every execution result corresponds to a known request.
4. **Dependency integrity:** Downstream phases receive valid required upstream artifacts.
5. **Result preservation:** Successful work is not discarded because another phase fails.
6. **Validation integrity:** Final completion requires an actual successful validation result.
7. **Semantic boundary:** The ProfilingManager never creates source facts, evidence, capabilities, or profile content itself.

## 10. Contract Boundary

**Input:** `ProfilingRequest`

**Intermediate:** `PhaseExecutionRequest`, actual `PhaseExecutionResult`, and specialized phase outcomes.

**Output:** `ProfilingOutcome`, including the validated Candidate Context when available.

The contract excludes job matching, ATS scoring, CV tailoring, salary strategy, application decisions, and other downstream activities.

**Final rule: Report only outcomes supported by actual execution and validation evidence.**