# SourceAgent Contract

## 1. Purpose

This contract defines the data boundary of the `SourceAgent`.

The SourceAgent is a specialized task executor.

It receives exactly one authorized Candidate Source assignment, interprets that source according to its type, and returns exactly one structured source-level result.

The SourceAgent does not manage the Source Processing phase.

It does not create:

- phase-level Source Processing status;
- candidate-wide Evidence Records;
- capabilities;
- Candidate Context sections;
- final profiling artifacts.

Its permanent transformation is:

```text
ONE SOURCE
    ↓
SOURCE → FACTS
    ↓
ParsedSourceResult
```

---

## 2. Input Contract

The SourceAgent receives exactly one source-processing assignment.

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

expected_output:
  ParsedSourceResult
```

Only fields required by the actual source type need to be populated.

The assignment must refer to exactly one authorized Candidate Source.

The SourceAgent must not modify or expand the authorized source scope.

---

## 3. File Source Example

```yaml
source:
  source_id: "SRC_001"
  source_type: FILE
  original_filename: "candidate_cv.pdf"
  file_path: "uploads/candidate_sources/..."
  source_url: null

execution_context:
  mode: INITIAL_PROFILE_BUILD

expected_output:
  ParsedSourceResult
```

---

## 4. GitHub Source Example

```yaml
source:
  source_id: "SRC_002"
  source_type: GITHUB
  original_filename: null
  file_path: null
  source_url: "https://github.com/..."

execution_context:
  mode: INITIAL_PROFILE_BUILD

expected_output:
  ParsedSourceResult
```

---

## 5. Single-Source Contract

Each SourceAgent execution is bound to exactly one source.

The SourceAgent must not:

- inspect another Candidate Source;
- combine multiple Candidate Sources;
- compare the assigned source with other sources;
- perform cross-source reconciliation;
- use another Candidate Source to strengthen the current result.

The execution boundary is:

```text
SourceAgent Instance
        ↓
exactly one source_id
        ↓
exactly one ParsedSourceResult
```

---

## 6. Source Access Contract

The SourceAgent may use the registered Source Access Layer to retrieve the content of its assigned source.

Conceptual routing:

```text
FILE
→ DocumentReader

GITHUB
→ GitHubReader

URL
→ WebReader
```

The SourceAgent consumes the retrieved source content.

It does not own:

- source storage;
- filesystem architecture;
- API authentication;
- transport implementation;
- database persistence;
- external retrieval implementation.

These responsibilities belong to the Source Access Layer and surrounding infrastructure.

---

## 7. Source Access Failure Contract

If the assigned source cannot be accessed, the SourceAgent must still return a source-level result when technically possible.

Example:

```yaml
source_id: "SRC_002"
source_type: GITHUB
status: UNAVAILABLE

facts: []

uncertainties: []

processing_notes:
  - "The assigned repository could not be accessed."
```

Do not fabricate facts from inaccessible content.

---

## 8. Output Contract

The SourceAgent returns exactly one:

```text
ParsedSourceResult
```

Conceptual structure:

```yaml
source_id: "..."
source_type: "..."

status:
  PARSED |
  PARTIALLY_PARSED |
  UNAVAILABLE |
  UNSUPPORTED_FORMAT |
  FAILED_TO_PARSE

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

The implementation should later enforce this structure through typed models and validation.

---

## 9. Identity Integrity Contract

The returned result must preserve the identity of the assigned source.

Required invariant:

```text
returned source_id
=
assigned source_id
```

and:

```text
returned source_type
=
assigned source_type
```

The SourceAgent must not return a result associated with another source.

---

## 10. Source Processing Status

Allowed conceptual statuses are:

```text
PARSED
PARTIALLY_PARSED
UNAVAILABLE
UNSUPPORTED_FORMAT
FAILED_TO_PARSE
```

### PARSED

The source was successfully accessed and the relevant accessible content was processed.

### PARTIALLY_PARSED

The source was accessed and useful information was extracted, but material portions could not be reliably processed.

### UNAVAILABLE

The assigned source could not be accessed.

### UNSUPPORTED_FORMAT

The Source Access Layer does not support the source format or type.

### FAILED_TO_PARSE

The source was accessible but semantic or technical parsing failed.

A failed or unavailable source result must still preserve source identity.

---

## 11. Processing Status Integrity

Do not use:

```text
PARSED
```

if material relevant content could not be processed.

Do not use:

```text
FAILED_TO_PARSE
```

merely because the source does not contain certain candidate information.

Distinguish:

```text
source lacks information
```

from:

```text
processing failed
```

Example:

```text
CV contains no team-size information
```

does not imply parsing failure.

---

## 12. Fact Contract

Each fact represents one meaningful source-level statement.

A fact must:

- remain attributable to the assigned source;
- remain inside the semantic scope of that source;
- preserve context where supported;
- preserve candidate contribution where supported;
- avoid unsupported strengthening;
- avoid unsupported weakening;
- avoid candidate-wide synthesis;
- avoid cross-source evidence assessment;
- remain target-independent.

Example:

```yaml
fact_id: FACT_001

statement: "Implemented FastAPI endpoints."

fact_type: IMPLEMENTATION

context:
  type: PERSONAL_PROJECT
  organization: null
  role: null
  project: "AI Interior Designer"
  start_date: null
  end_date: null

contribution:
  level: EXECUTED
  description: "Implemented API endpoints."

methods: []

tools_or_resources:
  - FastAPI

stakeholders: []

outcomes: []

source_locator:
  kind: repository_path
  value: "app/api/..."
```

---

## 13. Fact Identifier Contract

`fact_id` is an internal source-processing identifier.

It does not replace Evidence IDs.

Valid distinction:

```text
FACT_001
→ source-level fact

EV_001
→ later Evidence Record
```

The SourceAgent must not create `EV_###` identifiers.

---

## 14. Context Contract

Context fields are optional.

Populate them only when supported by the assigned source.

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

Do not infer context solely to complete the schema.

Preserve distinctions such as:

```text
academic project
≠
employment

working student
≠
full-time employment

volunteering
≠
paid employment
```

---

## 15. Contribution Contract

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

The SourceAgent must preserve the contribution represented by the assigned source.

Do not transform:

```text
participation
→ leadership

collaboration
→ sole ownership

tool use
→ mastery

team outcome
→ individual ownership
```

without source support.

If contribution is unclear:

- leave the level unset where appropriate;
- or record the uncertainty explicitly.

---

## 16. Detail Contract

Where supported, a fact may include:

```text
methods
tools_or_resources
stakeholders
outcomes
```

These fields must remain fact-specific.

Do not populate them from assumptions or general domain knowledge.

Examples of forbidden inference:

```text
FastAPI used
→ production deployment
```

```text
repository exists
→ commercial system
```

```text
team project
→ leadership
```

unless the assigned source establishes those facts.

---

## 17. Source Locator Contract

Where technically available, facts should include a locator that helps trace them back to the assigned source.

Examples:

```text
PDF
→ page

DOCX
→ section / paragraph

XLSX
→ sheet + cell/range

GitHub
→ repository path / file path

Website
→ page / section
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

A locator is preferred when available.

It must not be fabricated.

---

## 18. Source Locator Integrity

If a locator is provided:

```text
kind
```

and:

```text
value
```

must describe one coherent locator.

Do not return malformed placeholder data such as:

```text
{"kind": page_placeholder}
```

If a precise locator cannot be established, use a broader valid locator or leave it unset according to the implementation schema.

---

## 19. Uncertainty Contract

Source-level uncertainty belongs in:

```text
uncertainties
```

Conceptual example:

```yaml
- type: AMBIGUOUS_DATE
  description: "The exact end date is not clear."

  source_locator:
    kind: page
    value: "2"
```

Another example:

```yaml
- type: UNCLEAR_OWNERSHIP
  description: "The repository demonstrates the implementation but does not establish sole authorship."

  source_locator:
    kind: repository_path
    value: "/"
```

These are source-level observations.

They are not final Candidate Context limitations.

They do not assign evidence support levels.

---

## 20. Processing Notes Contract

`processing_notes` contain operational or interpretive notes required to understand the SourceAgent result.

Appropriate examples:

```text
Relevant pages were unreadable.
Repository metadata was incomplete.
Only part of the document could be processed.
Source type required limited interpretation.
```

Do not use `processing_notes` as an unstructured replacement for missing facts, uncertainties, or statuses.

---

## 21. Semantic Integrity Contract

The SourceAgent must preserve semantic boundaries.

The following transformations are forbidden unless explicitly supported:

```text
academic
→ professional

project
→ employment

prototype
→ production

participation
→ ownership

contribution
→ leadership

usage
→ expertise
```

The SourceAgent must preserve what the source actually establishes.

---

## 22. Temporal Integrity Contract

Dates must be represented according to the source.

Do not reinterpret valid dates relative to the model's assumptions.

Example:

If the current profiling date is after May 2026:

```text
May 2026
```

must not be described as a future date.

Likewise:

```text
2026–Present
```

must not be classified as impossible merely because the model incorrectly assumes an earlier current date.

When temporal interpretation matters, use the execution context or supplied current-date context rather than unsupported assumptions.

---

## 23. Candidate Statement Contract

If the assigned source is a Candidate Statement, the SourceAgent may preserve what the candidate explicitly states.

Example:

```yaml
statement: "The candidate states that they coordinated supplier communication."
```

Do not silently convert this into:

```text
independently verified fact
```

The later Evidence stage determines cross-source support.

---

## 24. Target-Independence Contract

The SourceAgent must not alter extraction according to:

- target job;
- vacancy;
- ATS keywords;
- recruiter preferences;
- salary goals;
- application strategy;
- LinkedIn strategy.

The same source should produce materially equivalent source-level facts regardless of future downstream job targeting.

---

## 25. Sensitive Information Contract

Do not reproduce secrets as facts.

Forbidden output includes:

- passwords;
- API keys;
- private tokens;
- credentials;
- unnecessary highly sensitive information.

Only candidate information relevant and authorized for Candidate Context construction should be retained.

---

## 26. Explicitly Forbidden Outputs

The SourceAgent must not create or return:

```text
SourceProcessingResult
phase completion decision
retry strategy
EV_###
CAP_###
candidate-wide support levels
candidate strengths
candidate capabilities
final contradiction resolution
PROFILE.md
SOURCE_INDEX.md as final Candidate Context artifact
EVIDENCE_INDEX.md
CAPABILITY_MAP.md
LIMITATIONS.md
dynamic profile sections
job-fit conclusions
ATS conclusions
CV recommendations
application recommendations
```

These belong to the SourceManager, later profiling stages, or downstream systems.

---

## 27. Output Validation Contract

Before the result is accepted, it should be possible to validate at minimum:

```text
source_id matches assignment
source_type matches assignment
status is valid
facts follow schema
context values are valid
contribution values are valid
source locators are structurally valid
uncertainties follow schema
```

A structurally invalid output must not silently enter downstream processing as if valid.

---

## 28. Handoff Contract

The SourceAgent returns exactly one `ParsedSourceResult` to the `SourceManager`.

Conceptually:

```text
SourceManager
        ↓
Source Task
        ↓
SourceAgent
        ↓
ParsedSourceResult
        ↓
SourceManager
```

For multiple sources, the SourceManager may eventually collect:

```yaml
parsed_source_results:
  - ParsedSourceResult
  - ParsedSourceResult
  - ParsedSourceResult
```

The SourceAgent itself never collects or reconciles those multiple source results.

---

## 29. No Hidden Conversation Dependency

Later processing must depend on:

```text
ParsedSourceResult
```

not on hidden SourceAgent reasoning or conversation history.

Anything required downstream must be represented explicitly in the structured output.

---

## 30. Manager vs. Agent Boundary

The distinction is:

```text
SourceManager

AuthorizedSourceSet
        ↓
manage source-processing tasks
        ↓
SourceProcessingResult
```

versus:

```text
SourceAgent

One CandidateSource
        ↓
SOURCE → FACTS
        ↓
ParsedSourceResult
```

The SourceAgent performs one semantic source-processing task.

The SourceManager manages the phase.

---

## 31. Contract Boundary

The SourceAgent contract begins at:

```text
One Authorized CandidateSource Assignment
```

and ends at:

```text
One ParsedSourceResult
```

The permanent transformation boundary is:

```text
ONE SOURCE
    ↓
SOURCE → FACTS
    ↓
ONE ParsedSourceResult
```

It does not extend to:

```text
SOURCE PROCESSING PHASE MANAGEMENT
```

It does not extend to:

```text
FACTS → EVIDENCE
```

and it does not extend to:

```text
EVIDENCE → CANDIDATE REPRESENTATION
```