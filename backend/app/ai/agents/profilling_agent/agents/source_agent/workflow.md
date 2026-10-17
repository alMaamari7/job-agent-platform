# SourceAgent Workflow

## 1. Receive Assigned Source

Receive one authorized `CandidateSource` from the orchestration layer.

The source assignment must include at least enough information to identify and access the source, such as:

```text
source_id
source_type
source location or access reference
```

Do not expand the source set yourself.

---

## 2. Access the Source

Use the available Source Access Layer to retrieve the source content.

Examples:

```text
FILE
→ DocumentReader

GITHUB
→ GitHubReader

URL
→ WebReader
```

If the source cannot be accessed, record the access failure and stop processing that source.

Do not pretend inaccessible content was inspected.

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

Use the source type to determine what kinds of facts the source can reasonably establish.

---

## 4. Inspect Relevant Content

Inspect the source content that may contain meaningful candidate information.

Depending on the source type, this may include:

### CV / Resume

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

- source code;
- project structure;
- configuration;
- dependencies;
- documentation;
- tests;
- implemented features;
- project metadata.

### Certificate

- credential title;
- issuer;
- issue date;
- expiration date where present;
- credential identifier where present;
- scope.

### Thesis / Academic Document

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

- employer;
- official role;
- dates;
- responsibilities;
- documented contribution;
- documented outcomes.

### Portfolio

- projects;
- artifacts;
- candidate role;
- methods;
- tools;
- outcomes;
- evidence of contribution where visible.

### Candidate Statement

- explicitly stated candidate facts.

Ignore content that is purely technical or formatting noise and does not help establish meaningful candidate facts.

---

## 5. Extract Source-Level Facts

Convert relevant source content into clear source-level facts.

Facts should remain close to what the source actually establishes.

Prefer useful granularity:

```text
specific enough for later evidence reasoning
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

Do not convert source facts into candidate-wide strengths or capabilities.

---

## 6. Preserve Context

Attach the context that is visible or directly supported by the source.

Examples:

```text
PROFESSIONAL_EMPLOYMENT
WORKING_STUDENT
INTERNSHIP
VOLUNTEER
PERSONAL_PROJECT
PORTFOLIO_PROJECT
ACADEMIC_PROJECT
THESIS
RESEARCH
TRAINING
CERTIFICATION
OPEN_SOURCE
DECLARED_ONLY
OTHER
```

Preserve relevant source-specific context such as:

```text
organization
role
project
dates
activity
document section
repository path
```

Do not infer missing context.

---

## 7. Preserve Candidate Contribution

Where the source shows the candidate's contribution, record it faithfully.

Examples may include:

```text
supported
contributed
executed
coordinated
owned
led
created
researched
taught
managed
```

Do not assign a stronger contribution than the source supports.

If contribution is unclear, preserve that ambiguity.

---

## 8. Capture Outcomes and Relevant Details

Where explicitly supported, extract useful details such as:

```text
methods
tools
technologies
stakeholders
qualitative outcomes
quantitative outcomes
artifacts
implemented features
research results
```

Do not invent missing metrics, impact, scale, ownership, or production status.

---

## 9. Record Source-Level Ambiguity

Identify ambiguity or incompleteness inside the source when it materially affects interpretation.

Examples:

```text
unclear date
unclear project ownership
partially unreadable content
ambiguous role wording
missing repository context
unclear production status
```

Do not attempt cross-source contradiction resolution.

That belongs to later evidence processing.

---

## 10. Build Parsed Source Result

Assemble the extracted information into the source-processing result.

Conceptually:

```text
ParsedSourceFacts
```

The result should include:

```text
source identity
processing status
source-level facts
preserved context
relevant contribution information
relevant outcomes/details
source-level uncertainties
processing notes where necessary
```

Every extracted fact must remain traceable to the assigned source.

---

## 11. Self-Check Before Return

Before returning the source result, verify:

```text
1. Did I inspect the relevant content?
2. Are the extracted facts actually supported by this source?
3. Did I preserve the original context?
4. Did I avoid unsupported strengthening or weakening?
5. Did I avoid candidate-wide synthesis?
6. Did I preserve relevant ambiguity?
7. Can every fact be traced back to this source?
```

If not, revise the result before returning it.

---

## 12. Return Result to Orchestrator

Return the completed source-processing result to the `ProfilingManager`.

Possible source-processing outcomes include:

```text
PARSED
PARTIALLY_PARSED
UNAVAILABLE
UNSUPPORTED_FORMAT
FAILED_TO_PARSE
```

Do not continue into evidence assessment or candidate profiling.

Your workflow ends at:

```text
CandidateSource
      ↓
Inspect
      ↓
Understand
      ↓
Extract
      ↓
Preserve Context
      ↓
ParsedSourceFacts
      ↓
Return to ProfilingManager
```
