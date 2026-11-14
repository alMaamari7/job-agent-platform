# SourceAgent Workflow

## 1. Receive Assigned Source Task

Receive exactly one authorized source-processing task from the `SourceManager`.

The assignment must identify exactly one Candidate Source.

At minimum, the task should contain or reference:

```text
source_id
source_type
source location or access reference
required output contract
relevant execution context
```

Your execution scope is limited to this assigned source.

Do not:

- expand the source set;
- inspect another Candidate Source;
- combine multiple sources;
- decide which other sources should be processed.

Conceptually:

```text
SourceManager
      ↓
One Source Task
      ↓
SourceAgent
```

---

## 2. Access the Assigned Source

Use the authorized Source Access mechanism available for the assigned source.

Examples:

```text
FILE
→ DocumentReader

GITHUB
→ GitHubReader

URL
→ WebReader
```

The exact reader depends on the registered source type and available Source Access Layer.

If the assigned source cannot be accessed:

- preserve the source identity;
- record the access problem;
- assign the appropriate processing status;
- do not pretend inaccessible content was inspected.

Where no meaningful content can be accessed, stop semantic processing for that source and return the source-level failure result.

---

## 3. Identify Source Type and Interpretation Scope

Determine what kind of source is being processed.

Examples:

```text
CV / Resume
Repository
Certificate
Thesis / Academic Document
Employment Reference
Portfolio
Website
Candidate Statement
Other Authorized Source
```

Use the source type to understand:

```text
What kinds of facts can this source reasonably establish?
```

Do not assign a universal authority level to the entire source.

Authority remains fact-specific.

---

## 4. Inspect Relevant Source Content

Inspect the parts of the assigned source that may contain meaningful candidate information.

### CV / Resume

Inspect relevant information such as:

- roles;
- organizations;
- dates;
- responsibilities;
- achievements;
- education;
- projects;
- skills;
- languages;
- certifications;
- stated outcomes.

### Repository

Inspect relevant information such as:

- source code;
- project structure;
- configuration;
- dependencies;
- documentation;
- tests;
- implemented features;
- project metadata.

### Certificate

Inspect relevant information such as:

- credential title;
- issuer;
- issue date;
- expiration date where present;
- credential identifier where present;
- credential scope.

### Thesis / Academic Document

Inspect relevant information such as:

- title;
- institution;
- research problem;
- methodology;
- implementation;
- evaluation;
- results;
- limitations;
- academic context.

### Employment Reference

Inspect relevant information such as:

- employer;
- official role;
- dates;
- responsibilities;
- documented contribution;
- documented outcomes.

### Portfolio

Inspect relevant information such as:

- projects;
- artifacts;
- candidate role;
- methods;
- tools;
- outcomes;
- visible contribution evidence.

### Candidate Statement

Inspect explicitly stated candidate information.

Ignore content that is merely formatting noise or irrelevant technical detail and does not materially help establish candidate facts.

---

## 5. Extract Source-Level Facts

Transform relevant content into clear source-level facts.

Facts must remain close to what the assigned source actually establishes.

Prefer useful granularity:

```text
specific enough
for later Evidence Processing

but

not fragmented beyond practical usefulness
```

Examples:

```text
Implemented FastAPI endpoints.

Used SQLAlchemy for persistence.

Completed a bachelor's degree in Business Informatics.

Worked as a working student in procurement.
```

Do not transform these facts into candidate-wide conclusions.

---

## 6. Preserve Context

For each relevant fact, preserve the context visible or directly supported by the source.

Possible contexts include:

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

Where supported, preserve contextual information such as:

```text
organization
role
project
start_date
end_date
activity
document section
repository path
```

Do not infer missing context.

Do not reclassify one context into another.

---

## 7. Preserve Candidate Contribution

Where the assigned source shows the candidate's contribution, record it faithfully.

Possible contribution levels may include:

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

Do not assign a stronger contribution than the source supports.

Do not transform:

```text
participation → leadership
collaboration → sole ownership
tool usage → mastery
team achievement → individual ownership
```

If contribution is unclear, preserve that ambiguity.

---

## 8. Capture Relevant Details and Outcomes

Where supported, capture relevant information such as:

```text
methods
tools
technologies
resources
stakeholders
qualitative outcomes
quantitative outcomes
artifacts
implemented features
research results
```

Only record details the assigned source reasonably supports.

Do not invent:

- missing metrics;
- business impact;
- scale;
- ownership;
- team size;
- production status;
- commercial deployment.

---

## 9. Preserve Provenance

Every extracted fact must remain traceable to the assigned source.

Where possible, attach a source locator.

Examples:

```text
page
section
heading
repository path
file path
line range
document region
```

Do not invent precise provenance.

If only a broader source-level locator is available, preserve that honestly.

---

## 10. Record Source-Level Uncertainty

Identify ambiguity, incompleteness, or inaccessible information inside the assigned source when it materially affects interpretation.

Examples:

```text
unclear date
unclear ownership
partially unreadable content
ambiguous role wording
missing repository context
unclear production status
```

Record the uncertainty explicitly.

Do not attempt to resolve it using another Candidate Source.

Cross-source reconciliation belongs to Evidence Processing.

---

## 11. Determine Processing Status

Determine the processing status that accurately reflects this execution.

Supported outcomes include:

```text
PARSED
PARTIALLY_PARSED
UNAVAILABLE
UNSUPPORTED_FORMAT
FAILED_TO_PARSE
```

### PARSED

Use when the relevant accessible source content was successfully processed.

### PARTIALLY_PARSED

Use when useful source information was extracted but material source content could not be processed.

### UNAVAILABLE

Use when the assigned source cannot be accessed.

### UNSUPPORTED_FORMAT

Use when the system cannot process the assigned source format.

### FAILED_TO_PARSE

Use when the source was accessible but processing failed.

Do not use failure statuses merely because the source lacks certain candidate facts.

---

## 12. Build ParsedSourceResult

Assemble the result according to the SourceAgent output contract.

Conceptually:

```text
ParsedSourceResult
```

The result should contain or represent:

```text
source_id
source_type
status

facts:
    statement
    fact_type
    context
    contribution
    methods
    tools_or_resources
    stakeholders
    outcomes
    source_locator

uncertainties

processing_notes
```

Only populate information supported by the assigned source.

Every fact must remain attributable to that source.

---

## 13. Self-Check Before Return

Before returning the result, verify:

```text
1. Did I process exactly one assigned source?

2. Did I inspect the relevant accessible content?

3. Are the extracted facts actually supported by this source?

4. Did I preserve the original context?

5. Did I preserve the candidate's actual contribution?

6. Did I avoid unsupported strengthening or weakening?

7. Did I preserve relevant uncertainty?

8. Can every fact be traced back to this source?

9. Did I avoid cross-source reasoning?

10. Did I avoid candidate-wide synthesis?

11. Does the processing status accurately describe what happened?

12. Does the result satisfy the ParsedSourceResult contract?
```

If not, revise the result before returning it.

---

## 14. Return Result to SourceManager

Return exactly one `ParsedSourceResult` to the `SourceManager`.

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

The SourceManager determines:

- whether the result is sufficient;
- whether another execution is required;
- whether a retry is justified;
- whether the Source Processing phase is complete.

You do not make those phase-level decisions.

---

## 15. Workflow Boundary

Your workflow ends at:

```text
One CandidateSource
        ↓
Access
        ↓
Inspect
        ↓
Understand
        ↓
Extract Facts
        ↓
Preserve Context
        ↓
Preserve Contribution
        ↓
Preserve Provenance
        ↓
Preserve Uncertainty
        ↓
Build ParsedSourceResult
        ↓
Self-Check
        ↓
Return to SourceManager
```

You do not continue into:

```text
FACTS → EVIDENCE
```

or:

```text
EVIDENCE → CANDIDATE REPRESENTATION
```

Your complete responsibility is:

```text
ONE SOURCE → ParsedSourceResult
```