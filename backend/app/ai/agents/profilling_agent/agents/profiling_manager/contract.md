# ProfilingManager Contract

## 1. Purpose

This contract defines the data boundary of the ProfilingManager.

The manager coordinates profiling stages but does not replace their domain-specific reasoning.

---

## 2. Manager Input

Minimum conceptual input:

```yaml
profiling_request:
  authorized_sources:
    - ...
  existing_candidate_context: null | ...
  requested_mode: null | INITIAL_PROFILE_BUILD | UPDATE_EXISTING_PROFILE
```

The application may add technical metadata where needed.

---

## 3. Internal Workflow State

The ProfilingManager should maintain explicit workflow state.

Conceptual structure:

```yaml
run_id:
mode:
status:
current_stage:

authorized_sources:
  - ...

source_result:
  status:
  parsed_sources:
    - ...
  errors:
    - ...

evidence_result:
  status:
  evidence_records:
    - ...
  unresolved_contradictions:
    - ...
  errors:
    - ...

profile_result:
  status:
  candidate_context:
  material_limitations:
    - ...
  errors:
    - ...

validation_result:
  passed:
  structural_errors:
    - ...
  semantic_errors:
    - ...
```

Exact implementation may later use Pydantic models and database persistence.

---

## 4. Required Stage Contracts

### Source Processing

Input:

```text
AuthorizedSourceSet
```

Output:

```text
SourceRegistry
ParsedSourceFacts
SourceProcessingStatus
```

---

### Evidence Processing

Input:

```text
SourceRegistry
ParsedSourceFacts
```

Output:

```text
EvidenceRecords
UnresolvedContradictions
EvidenceProcessingStatus
```

---

### Profile Processing

Input:

```text
SourceRegistry
EvidenceRecords
UnresolvedContradictions
```

Output:

```text
CandidateContextDraft
ProfileProcessingStatus
```

The draft must include the required Candidate Context structure:

```text
PROFILE.md
SOURCE_INDEX.md
EVIDENCE_INDEX.md
CAPABILITY_MAP.md
LIMITATIONS.md
profile/
```

---

### Validation

Input:

```text
CandidateContextDraft
SourceRegistry
EvidenceRecords
```

Output:

```yaml
passed:
errors:
  - ...
warnings:
  - ...
```

---

## 5. Manager Output

The ProfilingManager returns:

```yaml
candidate_context:
  ...

run_summary:
  mode:
  status:
  sources_processed:
  sources_unavailable:
  evidence_records_created:
  evidence_records_updated:
  capabilities_created:
  capabilities_updated:
  dynamic_sections_created:
  dynamic_sections_updated:
  material_limitations:
```

---

## 6. Completion Contract

Possible final statuses:

```text
COMPLETE
COMPLETE_WITH_LIMITATIONS
INCOMPLETE_MISSING_REQUIRED_SOURCES
INCOMPLETE_UNRESOLVED_INTEGRITY_ISSUE
```

`COMPLETE` requires successful validation and no material unresolved integrity issue.

`COMPLETE_WITH_LIMITATIONS` requires a usable Candidate Context with explicitly documented material limitations.

An incomplete status must preserve the reason for incompleteness.

---

## 7. Contract Boundary

The manager's contract ends at:

```text
Validated Candidate Context
+
Profiling Run Summary
```

It does not include job matching, application configuration, CV tailoring, ATS scoring, salary decisions, application submission, or other downstream actions.
