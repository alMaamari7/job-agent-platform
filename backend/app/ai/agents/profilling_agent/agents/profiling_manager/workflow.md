# ProfilingManager Workflow

## 1. Receive Profiling Request

Receive the profiling request together with:

- authorized Candidate Sources;
- optional existing Candidate Context;
- run metadata required by the application.

---

## 2. Resolve Execution Mode

Determine:

```text
INITIAL_PROFILE_BUILD
```

or:

```text
UPDATE_EXISTING_PROFILE
```

Output:

```text
ExecutionMode
```

---

## 3. Resolve Authorized Source Set

Confirm the sources that belong to the current run.

Output:

```text
AuthorizedSourceSet
```

---

## 4. Start Source Processing

Provide the authorized source set to the source-processing stage.

Expected output:

```text
SourceRegistry
ParsedSourceFacts
SourceProcessingStatus
```

If required sources are inaccessible or parsing fails, preserve these results in workflow state.

---

## 5. Start Evidence Processing

Provide parsed source facts and source provenance to the evidence-processing stage.

Expected output:

```text
EvidenceRecords
UnresolvedContradictions
EvidenceProcessingStatus
```

The evidence stage is responsible for claim extraction, normalization, context preservation, duplicate reconciliation, support assessment, and evidence creation.

---

## 6. Start Candidate Representation

Provide validated evidence data and relevant source metadata to the profile-processing stage.

Expected output:

```text
CandidateContextDraft
CapabilityMap
MaterialLimitations
ProfileProcessingStatus
```

This stage is responsible for strengths, synthesis, capabilities, dynamic structure, and profile generation.

---

## 7. Run Validation Layer

Pass the complete Candidate Context draft through validation.

Validation may contain:

```text
Structural Validators
Reference Validators
Schema Validators
Semantic Review
```

Expected output:

```text
ValidationResult
```

---

## 8. Handle Validation Result

If validation passes:

```text
continue → finalization
```

If validation identifies correctable stage-specific problems:

```text
route issue → responsible stage
```

If validation identifies an unresolved material integrity problem:

```text
mark run incomplete
```

Do not finalize inconsistent output as clean completion.

---

## 9. Finalize Candidate Context

When validation conditions are satisfied:

- persist or return the final Candidate Context;
- preserve stable identifiers where required;
- determine completion status;
- create final run summary.

---

## 10. Produce Run Summary

The run summary should contain operational metadata such as:

```yaml
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

The run summary does not replace the Candidate Context.

---

## Workflow Overview

```text
Profiling Request
      ↓
Resolve Mode
      ↓
Resolve Authorized Sources
      ↓
Source Processing
      ↓
Evidence Processing
      ↓
Candidate Representation
      ↓
Validation
      ↓
Pass?
 ┌────┴────┐
 No        Yes
 ↓          ↓
Correct /   Finalize
Incomplete      ↓
          Candidate Context
          + Run Summary
```
