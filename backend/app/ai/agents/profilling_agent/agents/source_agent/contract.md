# SourceAgent Contract

## 1. Purpose

This contract defines the data boundary of the `SourceAgent`.

The SourceAgent receives one authorized Candidate Source, interprets it according to its type, and returns a structured source-level representation.

The SourceAgent does not create candidate-wide evidence, capabilities, profile sections, or final Candidate Context artifacts.

---

## 2. Input Contract

The SourceAgent receives one source-processing request.

Conceptual input:

```yaml
source:
  source_id: "..."
  source_type: "..."
  original_filename: null | "..."
  file_path: null | "..."
  source_url: null | "..."

execution_context:
  mode: INITIAL_PROFILE_BUILD | UPDATE_EXISTING_PROFILE
```

Only fields required by the actual source type need to be populated.

Examples:

### File Source

```yaml
source:
  source_id: "..."
  source_type: FILE
  original_filename: "candidate_cv.pdf"
  file_path: "uploads/candidate_sources/..."
  source_url: null
```

### GitHub Source

```yaml
source:
  source_id: "..."
  source_type: GITHUB
  original_filename: null
  file_path: null
  source_url: "https://github.com/..."
```

The SourceAgent must not modify the authorized source set.

---

## 3. Source Access Contract

The SourceAgent may use the Source Access Layer to retrieve source content.

Conceptual routing:

```text
FILE
→ DocumentReader

GITHUB
→ GitHubReader

URL
→ WebReader
```

The SourceAgent consumes source content.

It does not own transport, storage, filesystem access, API authentication, or external retrieval implementation.

---

## 4. Output Contract

The SourceAgent returns one `ParsedSourceResult`.

Conceptual structure:

```yaml
source_id: "..."
source_type: "..."
status: PARSED

facts:
  - fact_id: "..."
    statement: "..."
    fact_type: "..."
    context:
      type: null | "..."
      organization: null | "..."
      role: null | "..."
      project: null | "..."
      start_date: null | "..."
      end_date: null | "..."
    contribution:
      level: null | "..."
      description: null | "..."
    methods:
      - "..."
    tools_or_resources:
      - "..."
    stakeholders:
      - "..."
    outcomes:
      - "..."
    source_locator:
      kind: null | "..."
      value: null | "..."

uncertainties:
  - type: "..."
    description: "..."
    source_locator:
      kind: null | "..."
      value: null | "..."

processing_notes:
  - "..."
```

This is the conceptual contract.

The exact implementation may later use Pydantic models and enums.

---

## 5. Source Processing Status

Allowed conceptual statuses:

```text
PARSED
PARTIALLY_PARSED
UNAVAILABLE
UNSUPPORTED_FORMAT
FAILED_TO_PARSE
```

### PARSED

The source was accessed and the relevant content was successfully inspected.

### PARTIALLY_PARSED

The source was accessible, but relevant portions could not be reliably interpreted.

### UNAVAILABLE

The source could not be accessed.

### UNSUPPORTED_FORMAT

The current Source Access Layer cannot process the source format or type.

### FAILED_TO_PARSE

The source was accessed but processing failed.

A failed or unavailable source must still return a result identifying the source and its status.

---

## 6. Fact Contract

Each fact should represent one meaningful source-level statement.

A fact must:

- remain attributable to the current source;
- preserve its original context where available;
- avoid unsupported candidate-wide conclusions;
- avoid support-level assessment across sources;
- avoid job-fit or target-role interpretation.

Example:

```yaml
fact_id: FACT_001
statement: "Implemented FastAPI endpoints."
fact_type: IMPLEMENTATION

context:
  type: PERSONAL_PROJECT
  project: "AI Interior Designer"

tools_or_resources:
  - FastAPI

source_locator:
  kind: repository_path
  value: "app/api/..."
```

The identifier format for source-level facts is internal to source processing and does not replace `EV_###` Evidence IDs.

---

## 7. Context Contract

Context fields are optional and should only be populated where the source supports them.

Possible context types may include:

```text
PROFESSIONAL_EMPLOYMENT
WORKING_STUDENT
INTERNSHIP
SELF_EMPLOYMENT
FREELANCE
VOLUNTEER
PERSONAL_PROJECT
PORTFOLIO_PROJECT
ACADEMIC_PROJECT
THESIS
RESEARCH
TRAINING
CERTIFICATION
OPEN_SOURCE
COMMUNITY_WORK
DECLARED_ONLY
OTHER
```

Do not infer context merely to fill the schema.

---

## 8. Contribution Contract

Contribution information is optional.

Where supported, conceptual contribution levels may include:

```text
OBSERVED
ASSISTED
SUPPORTED
CONTRIBUTED
EXECUTED
COORDINATED
OWNED
LED
CREATED
RESEARCHED
TAUGHT
MANAGED
```

The SourceAgent must preserve the contribution represented by the source without inflating or minimizing it.

---

## 9. Source Locator Contract

Where technically available, a fact should contain a locator that helps later trace it back to the source.

Examples:

```text
PDF
→ page number

DOCX
→ section / paragraph reference

XLSX
→ sheet + cell/range

GitHub
→ repository path

Website
→ page/section reference
```

Conceptual representation:

```yaml
source_locator:
  kind: page
  value: "2"
```

or:

```yaml
source_locator:
  kind: repository_path
  value: "app/services/example.py"
```

A locator is preferred when available, but must not be fabricated.

---

## 10. Uncertainty Contract

Source-level uncertainty belongs in:

```text
uncertainties
```

Examples:

```yaml
- type: AMBIGUOUS_DATE
  description: "The source does not make the exact end date clear."
```

```yaml
- type: UNCLEAR_OWNERSHIP
  description: "The repository shows the implementation but does not establish sole authorship."
```

These are source-level observations.

They are not final Candidate Context limitations and do not assign evidence support levels.

---

## 11. Explicitly Forbidden Outputs

The SourceAgent must not return:

```text
EV_###
CAP_###
Candidate strengths
Candidate-wide capability conclusions
Final support levels
Final contradiction resolution
PROFILE.md
EVIDENCE_INDEX.md
CAPABILITY_MAP.md
LIMITATIONS.md
Dynamic profile sections
Job-fit conclusions
ATS conclusions
```

These belong to later processing stages.

---

## 12. Handoff Contract

The SourceAgent returns its `ParsedSourceResult` to the `ProfilingManager`.

For multiple sources, the manager may collect:

```yaml
parsed_sources:
  - ParsedSourceResult
  - ParsedSourceResult
  - ParsedSourceResult
```

The next profiling stage should consume these structured source results rather than depend on hidden SourceAgent conversation history.

---

## 13. Contract Boundary

The SourceAgent contract begins at:

```text
Authorized CandidateSource
```

and ends at:

```text
ParsedSourceResult
```

The permanent transformation boundary is:

```text
SOURCE → FACTS
```

It does not extend to:

```text
FACTS → EVIDENCE
```

or:

```text
EVIDENCE → CANDIDATE REPRESENTATION
```
