# EVAL-002 — Independent Multi-Source Processing

## 1. Objective

Evaluate whether the `ProfilingManager` can process multiple authorized `CandidateSource` inputs independently through the `SourceAgent`, preserve successful results across failures and retries, and stop correctly after the Source Processing stage.

The evaluation also assesses the AI quality of the resulting `ParsedSourceResult` outputs for two source types:

- CV / FILE
- GitHub repository

---

## 2. Hypothesis

The revised architecture should enforce the following execution boundary:

```text
1 CandidateSource
        ↓
1 process_candidate_source call
        ↓
1 SourceAgent execution
        ↓
1 independent ParsedSourceResult
```

Expected consequences:

- sources are not bundled into one SourceAgent execution;
- failure of one source does not invalidate another;
- successful results remain preserved;
- all authorized sources are attempted;
- the workflow does not continue into Evidence Processing;
- source-level AI output remains grounded and context-preserving.

---

## 3. Component Under Test

```text
ProfilingManager
        ↓
process_candidate_source(source_id)
        ↓
SourceAgent.run(source)
        ↓
ReadCandidateSource
        ↓
ParsedSourceResult
```

Sources under test:

```text
Source 1: CV / FILE
Source 2: GitHub repository
```

---

## 4. Relevant Contracts and Rules

The evaluation applies the following Source Processing rules:

- process exactly one authorized CandidateSource per SourceAgent execution;
- never combine multiple CandidateSources in one SourceAgent call;
- preserve each source result independently;
- continue processing remaining sources if one source fails;
- do not discard successful source results because another source fails;
- stop after Source Processing for this experiment;
- do not perform cross-source reconciliation;
- do not perform evidence synthesis;
- do not perform capability synthesis;
- do not generate a candidate profile;
- preserve context, contribution, provenance, and uncertainty.

Global evaluation weighting:

```text
System Evaluation = 30%
AI Evaluation     = 70%
```

Criterion weights below apply only to EVAL-002.

---

## 5. Inputs

### Source 1

```text
source_type: FILE
original_filename: Asaad_Al-Maamari_AI_Software_CV.pdf
```

### Source 2

```text
source_type: GITHUB
repository: alMaamari7/ai-interior-designer-portfolio
```

---

## 6. Changes Under Test

EVAL-002 validates the following changes introduced after EVAL-001:

1. UTF-8 runtime and log handling.
2. Authenticated GitHub source access.
3. One CandidateSource per SourceAgent execution.
4. Independent result preservation across source-level failures.

A deterministic retry policy is not yet implemented and is evaluated as an open system concern.

---

## 7. Expected Behavior

The run should demonstrate:

```text
CV
→ process_candidate_source(CV_ID)
→ SourceAgent(CV)
→ independent ParsedSourceResult

GitHub
→ process_candidate_source(GITHUB_ID)
→ SourceAgent(GitHub)
→ independent ParsedSourceResult
```

If a transient GitHub failure occurs:

```text
CV     → result remains preserved
GitHub → retry may occur
```

The Source Processing stage must not silently proceed into downstream profiling stages.

---

## 8. Execution Evidence

Observed execution behavior:

- both authorized sources were called independently;
- each source produced a separate SourceAgent run;
- the CV source completed successfully;
- the first GitHub processing attempt encountered a read timeout;
- the GitHub source was later retried and completed successfully;
- both sources ended with `PARSED`;
- the final API request returned `200 OK`;
- the run stopped after Source Processing;
- UTF-8 output rendered correctly in the runtime log.

The final run reported:

```text
CV      → PARSED
GitHub  → PARSED
```

The GitHub source required one retry after a transient timeout.

---

# 9. System Evaluation

## 9.1 Criteria and Weights

| Criterion | Weight |
|---|---:|
| Source isolation | 20% |
| Orchestration and source coverage | 20% |
| Failure / partial-success isolation | 15% |
| Retry behavior | 15% |
| Stage-boundary enforcement | 15% |
| Authorization and source access | 5% |
| Observability and logging | 5% |
| Runtime and token efficiency | 5% |
| **Total** | **100%** |

---

## 9.2 Source Isolation

**Score: 5/5**

The manager invoked `process_candidate_source` separately for the CV and GitHub source. Each invocation started an independent SourceAgent execution for exactly one source.

The primary EVAL-002 architectural hypothesis was therefore observed successfully.

Weighted contribution:

```text
20 / 20
```

---

## 9.3 Orchestration and Source Coverage

**Score: 5/5**

Both authorized sources were attempted and both ultimately completed with `PARSED`.

The manager did not omit either source.

Weighted contribution:

```text
20 / 20
```

---

## 9.4 Failure / Partial-Success Isolation

**Score: 5/5**

The first GitHub processing attempt failed because of a transient read timeout.

The failure remained associated with that source. The CV processing result was not invalidated by the GitHub failure.

This removes the multi-source failure coupling observed in EVAL-001.

Weighted contribution:

```text
15 / 15
```

---

## 9.5 Retry Behavior

**Score: 3/5**

The retry was appropriate in this run because the failure was transient:

```text
AgentGenerationError
The read operation timed out
```

The retry later succeeded.

However, retry behavior is still controlled indirectly by the LLM-driven orchestration rather than an explicit deterministic retry policy.

The run therefore validates:

```text
transient failure
→ retry
→ successful recovery
```

but does not yet validate:

```text
failure classification
→ deterministic retry decision
→ bounded retry count
```

Weighted contribution:

```text
9 / 15
```

---

## 9.6 Stage-Boundary Enforcement

**Score: 5/5**

The workflow stopped after Source Processing.

The run did not perform:

- Evidence Processing;
- capability synthesis;
- candidate profile generation.

Weighted contribution:

```text
15 / 15
```

---

## 9.7 Authorization and Source Access

**Score: 5/5**

Both authorized sources were accessible.

GitHub authentication worked successfully.

No unauthorized source was observed.

Weighted contribution:

```text
5 / 5
```

---

## 9.8 Observability and Logging

**Score: 5/5**

Runtime logging clearly exposed:

- manager tool calls;
- source IDs;
- individual SourceAgent runs;
- reader calls;
- failures;
- retries;
- token usage;
- final completion status.

UTF-8 output was rendered correctly.

Weighted contribution:

```text
5 / 5
```

---

## 9.9 Runtime and Token Efficiency

**Score: 2/5**

GitHub processing remains expensive.

The repository reader provides a large amount of repository content to the SourceAgent, resulting in high token usage and long execution time.

Observed examples include:

```text
GitHub SourceAgent:
~15,330 input tokens

Manager final step:
~25,025 accumulated input tokens
```

The initial failed GitHub attempt also consumed substantial runtime before the successful retry.

The architecture is functional but not yet efficient.

Weighted contribution:

```text
2 / 5
```

---

## 9.10 System Score

```text
20 + 20 + 15 + 9 + 15 + 5 + 5 + 2
= 91 / 100
```

Normalized to the global System weight:

```text
91% × 30
= 27.3 / 30
```

### System Result

```text
27.3 / 30
```

**Assessment: Strong**

The main orchestration hypothesis is validated.

---

# 10. AI Evaluation

## 10.1 Criteria and Weights

| Criterion | Weight |
|---|---:|
| Factual Accuracy | 25% |
| Completeness | 15% |
| Context Preservation | 15% |
| Contribution Preservation | 10% |
| Provenance Quality | 10% |
| Uncertainty Handling | 10% |
| Hallucination Avoidance | 10% |
| Contract Compliance | 5% |
| **Total** | **100%** |

---

## 10.2 Factual Accuracy

**Score: 4/5**

The majority of extracted facts were well grounded.

The GitHub result correctly identified implementation details including:

- Python;
- FastAPI;
- Pydantic;
- SQLAlchemy;
- REST API structure;
- deterministic image-quality checks;
- Pillow;
- NumPy;
- OpenCV;
- Gemini multimodal integration;
- schema-constrained structured outputs;
- human-in-the-loop review;
- automated tests;
- GitHub Actions.

A factual reasoning error was nevertheless observed in the CV result.

The SourceAgent generated an uncertainty stating that:

```text
The AI Interior Designer project is dated 2026–Present,
and the second Healthcare Assistant period extends to May 2026.
These dates appear to be in the future relative to the current context.
```

The EVAL-002 run occurred in October 2026.

Therefore:

```text
May 2026
```

was already in the past, and:

```text
2026–Present
```

is not inherently future-dated.

This temporal inference is incorrect.

Weighted contribution:

```text
20 / 25
```

---

## 10.3 Completeness

**Score: 4/5**

The CV result captured nine major fact groups:

- education;
- bachelor thesis;
- AI Interior Designer project;
- MEDIAN working-student role;
- WunderPen working-student role;
- healthcare work;
- technical skills;
- languages;
- profile statement.

The GitHub result captured fifteen relevant fact groups spanning implementation, infrastructure, documentation, AI architecture, testing, and project scope.

However, no manually curated reference inventory currently exists for either source.

Full completeness cannot therefore be measured rigorously.

Weighted contribution:

```text
12 / 15
```

---

## 10.4 Context Preservation

**Score: 5/5**

The SourceAgent preserved important source-context distinctions.

Examples include:

```text
employment
working-student work
thesis
personal project
public engineering portfolio
education
```

The GitHub source was not converted into paid employment evidence.

The public portfolio was also not treated as proof of the complete private product.

Weighted contribution:

```text
15 / 15
```

---

## 10.5 Contribution Preservation

**Score: 4/5**

The outputs generally avoided overstating contribution.

The GitHub result explicitly identified uncertainty around sole authorship and did not treat every repository component as independently proven sole work.

The CV result also preserved ambiguity around production status, team size, and sole ownership.

Some contribution labels remain stronger than the evidence contract currently defines, including values such as:

```text
OWNED
CREATED
DEVELOPED
```

The semantics of these labels should be formally defined in the structured output contract.

Weighted contribution:

```text
8 / 10
```

---

## 10.6 Provenance Quality

**Score: 4/5**

Most extracted facts include useful source locators such as:

```text
page 1
page 2
README.md
backend/app/services/image_quality.py
docs/ip-boundary.md
```

This provides meaningful traceability.

A malformed locator was observed in one CV uncertainty:

```text
{"kind": page_placeholder}
```

Some repository locators are also broader than necessary, for example:

```text
backend/
```

instead of a more precise implementation file.

Weighted contribution:

```text
8 / 10
```

---

## 10.7 Uncertainty Handling

**Score: 3/5**

The SourceAgent identified multiple useful uncertainty types, including:

- candidate-declared claims;
- unverified thesis metrics;
- unclear sole authorship;
- public/private scope limitations;
- lack of proof of paid employment;
- lack of proof of commercial deployment;
- lack of proof of production-scale operation.

However, the incorrect `FUTURE_DATES` uncertainty demonstrates that uncertainty detection itself can introduce unsupported claims.

Uncertainty generation therefore requires stronger temporal and semantic validation.

Weighted contribution:

```text
6 / 10
```

---

## 10.8 Hallucination Avoidance

**Score: 4/5**

No major fabricated employment, technology, deployment, or project ownership claim was observed.

The SourceAgent generally constrained outputs to what each source supported.

The temporal uncertainty error prevents a perfect score.

A second concern exists in the manager summary:

```text
Both parsed source results
(SourceRegistry + ParsedSourceFacts)
are available for the next stage.
```

The observed runtime establishes successful `ParsedSourceResult` outputs, but does not clearly prove that separate persisted `SourceRegistry` and `ParsedSourceFacts` artifacts exist.

This statement should therefore be treated as not verified.

Weighted contribution:

```text
8 / 10
```

---

## 10.9 Contract Compliance

**Score: 5/5**

The SourceAgent remained inside the intended source-processing boundary.

It did not perform:

- cross-source reconciliation;
- evidence synthesis;
- capability synthesis;
- target-role matching;
- candidate-wide profile generation.

Weighted contribution:

```text
5 / 5
```

---

## 10.10 AI Score

```text
20 + 12 + 15 + 8 + 8 + 6 + 8 + 5
= 82 / 100
```

Normalized to the global AI weight:

```text
82% × 70
= 57.4 / 70
```

### AI Result

```text
57.4 / 70
```

**Assessment: Strong, with important quality findings**

---

# 11. Critical Gates

| Critical Gate | Result |
|---|---|
| Unauthorized source access | PASS |
| Secret or credential exposure | PASS |
| Fabricated evidence | PASS |
| Fabricated source provenance | PASS |
| Cross-source contamination | PASS |
| Successful source silently lost | PASS |
| False success after failed required stage | PASS |
| Critical stage-boundary violation | PASS |
| Downstream processing from known invalid state | PASS |
| Source context replaced by unsupported interpretation | PASS |

### Critical Gate Result

```text
PASS
```

No critical failure was observed.

---

# 12. Overall Score

```text
System: 27.3 / 30
AI:     57.4 / 70
-----------------
Total:  84.7 / 100
```

---

# 13. Result

```text
PASS_WITH_FINDINGS
```

Final score:

```text
84.7 / 100
```

The main EVAL-002 hypothesis is validated.

The revised one-source-per-execution architecture behaves correctly and substantially improves failure isolation compared with EVAL-001.

---

# 14. Key Findings

## Positive Findings

### 1. Independent Source Processing Works

Observed behavior:

```text
One Source
→ One manager tool call
→ One SourceAgent execution
→ One independent result
```

This removes the multi-source failure coupling identified in EVAL-001.

### 2. Partial Success Is Preserved

A transient GitHub failure did not invalidate the CV result.

### 3. GitHub Authentication Works

Authenticated GitHub access successfully retrieved repository content.

### 4. UTF-8 Logging Works

The previous encoding corruption is resolved.

### 5. Source Context Is Preserved Well

The SourceAgent correctly distinguishes among:

```text
employment
academic work
personal projects
portfolio evidence
declared claims
```

### 6. Agent Scope Is Respected

No downstream evidence or profile synthesis occurred.

---

## Open Findings

### 1. Retry Policy Is Not Yet Deterministic

Retry behavior remains indirectly controlled by LLM orchestration.

### 2. GitHub Processing Is Expensive

Repository ingestion causes high token usage and long execution times.

### 3. Temporal Reasoning Error Exists

The SourceAgent incorrectly classified already-past 2026 dates as future dates.

### 4. Provenance Is Not Fully Reliable

At least one malformed source locator was generated.

### 5. AI Completeness Has No Ground-Truth Benchmark

Completeness is currently estimated rather than measured against a manually verified reference.

### 6. Final-State Language Is Too Strong

The manager claims that specific downstream artifacts are available even though the runtime evidence only clearly establishes successful source-level parsed results.

---

# 15. Architectural Decision

```text
KEEP_WITH_CHANGES
```

Retain the architecture:

```text
ProfilingManager
        ↓
process_candidate_source(source_id)
        ↓
SourceAgent.run(single source)
```

The explicit single-source boundary should remain the default Source Processing architecture.

Required improvements should be implemented without reverting to unrestricted multi-source managed-agent delegation.

---

# 16. Follow-up Actions

## P0 — Deterministic Retry Policy

Introduce explicit failure classification and bounded retry behavior.

Expected examples:

```text
Network timeout
→ retry allowed

Temporary provider failure
→ retry allowed

Unauthorized source
→ no blind retry

Invalid credentials
→ no blind retry

Unsupported format
→ no blind retry

Deterministic validation failure
→ no blind retry
```

Retry attempts and original failures must remain visible in evaluation evidence.

---

## P1 — ParsedSourceResult Validation

Introduce deterministic schema validation at the SourceAgent boundary.

Validation should detect:

- malformed locators;
- invalid fact types;
- missing required fields;
- invalid contribution labels;
- malformed uncertainty structures;
- incompatible status/output combinations.

---

## P2 — Temporal Uncertainty Handling

Temporal uncertainty generation should be improved.

At minimum:

- the current evaluation date must be interpreted correctly;
- past dates must not be labeled as future;
- `Present` should be interpreted relative to the actual run date;
- temporal uncertainty should only be emitted when ambiguity genuinely exists.

---

## P3 — GitHubReader Efficiency

Reduce unnecessary repository payload before LLM processing.

Potential directions:

- file prioritization;
- relevance-based selection;
- repository summarization before SourceAgent interpretation;
- deterministic exclusion of irrelevant files;
- bounded file-size handling;
- staged repository inspection;
- structured metadata extraction before full-content reads.

The goal is to preserve evidence quality while reducing:

```text
token usage
runtime
timeout risk
```

---

## P4 — SourceAgent Ground-Truth Evaluation Set

Create manually reviewed reference cases for AI evaluation.

Initial benchmark set should include at least:

```text
1 CV
1 GitHub repository
```

For each source, define:

- expected major facts;
- correct context;
- expected contribution boundaries;
- required provenance;
- known uncertainties;
- forbidden interpretations.

This enables future completeness and accuracy scores to be measured against explicit ground truth rather than estimated manually after each run.

---

# 17. Regression Impact

Future changes affecting any of the following must preserve the behavior validated by EVAL-002:

```text
one CandidateSource per SourceAgent execution
independent result preservation
all authorized sources attempted
successful result survives another source failure
no unauthorized source access
stage boundary respected
source context preserved
no evidence/profile synthesis during Source Processing
```

The following changes should trigger an EVAL-002 regression run:

- retry-policy implementation;
- changes to `ProfilingManager`;
- changes to `ProcessCandidateSource`;
- changes to `SourceAgent.run`;
- changes to `ReadCandidateSource`;
- changes to CandidateSource authorization handling;
- changes to ParsedSourceResult schema;
- changes to GitHub source selection or repository preprocessing.

The architectural behavior validated by EVAL-002 should remain protected as the profiling system evolves.
