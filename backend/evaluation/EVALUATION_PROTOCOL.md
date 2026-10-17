# Evaluation Protocol

## 1. Purpose

This protocol defines the permanent evaluation framework for the `job-agent-platform`.

It is the common rule set for all future evaluations of the profiling system, including individual agents, orchestration components, processing stages, and end-to-end workflows.

The protocol separates two dimensions:

1. **System Evaluation** — whether the software architecture, orchestration, boundaries, state handling, and failure behavior work reliably.
2. **AI Evaluation** — whether AI components produce accurate, grounded, complete, context-preserving, and contract-compliant outputs.

The AI dimension is intentionally weighted more heavily because the core product value depends primarily on the quality of AI interpretation and decision-making.

## 2. Evaluation Principles

All evaluations MUST follow these principles:

- Evaluate **observed behavior**, not intended behavior.
- Every important evaluation claim MUST be supported by execution evidence.
- System behavior and AI output quality MUST be evaluated separately.
- AI quality has higher weight than system quality.
- Critical system failures cannot be compensated for by a high AI score.
- Partial success MUST be preserved and reported.
- Failures are valid evaluation findings, not noise to be ignored.
- The system MUST NOT report a failed or incomplete stage as successful.
- Evaluation MUST preserve the distinction between source facts, evidence, capabilities, and profile conclusions.
- Context and contribution boundaries MUST be preserved during evaluation.
- A single successful run does not permanently validate an architectural decision.
- Relevant prior evaluations MUST be repeated when later changes could invalidate their assumptions.

## 3. Evaluation Scope

This protocol can be applied at several levels.

### 3.1 Component Evaluation
Used for deterministic or infrastructure components such as source readers, authorization boundaries, retry handling, state persistence, validation logic, and API/service integration.

### 3.2 Agent Evaluation
Used for individual AI agents such as SourceAgent, EvidenceAgent, ProfileAgent, and future specialized agents.

### 3.3 Stage Evaluation
Used for one complete processing stage such as Source Processing, Evidence Processing, Candidate Representation, or Validation.

### 3.4 Orchestration Evaluation
Used for managers or workflow controllers such as ProfilingManager, stage transitions, partial-success handling, failure isolation, and workflow-state management.

### 3.5 End-to-End Evaluation
Used for the complete profiling workflow from authorized sources to final Candidate Context.

### 3.6 Regression Evaluation
Used to verify that a new architectural or AI change does not break previously validated behavior.

## 4. Evaluation Structure

Every evaluation is divided into two main sections:

```text
Evaluation
├── System Evaluation
└── AI Evaluation
```

Default weighting:

```text
System Evaluation = 30%
AI Evaluation     = 70%
```

The weighting MAY be changed only when the evaluated component has little or no AI behavior. Any deviation MUST be explicitly justified in the individual evaluation report.

## 5. System Evaluation — 30%

System Evaluation measures whether the surrounding software and orchestration behave correctly.

Typical criteria include:

- orchestration correctness;
- source isolation;
- contract enforcement;
- stage-boundary enforcement;
- state preservation;
- partial-success preservation;
- failure isolation;
- retry behavior;
- authorization boundaries;
- source access;
- error propagation;
- false-success prevention;
- runtime stability;
- output handoff correctness;
- structured workflow state;
- resource efficiency;
- token efficiency;
- observability and logging.

Not every criterion must apply to every evaluation. The report MUST state which criteria are applicable.

## 6. AI Evaluation — 70%

AI Evaluation measures the quality of the AI-generated result.

### 6.1 Factual Accuracy
Are statements supported by the provided source or input?

### 6.2 Completeness
Were important relevant facts captured, or were significant supported facts omitted?

### 6.3 Context Preservation
Was the original context preserved correctly?

Examples:
- employment remains employment;
- academic work remains academic;
- personal project remains project work;
- prototype remains prototype;
- public portfolio remains public portfolio.

### 6.4 Contribution Preservation
Did the AI avoid overstating the candidate's contribution?

Examples of prohibited transformations:
- participation → leadership;
- project contribution → sole ownership;
- tool usage → mastery;
- prototype → production system;
- academic work → professional employment.

### 6.5 Provenance Quality
Can extracted facts be traced back to the source using meaningful source locators?

### 6.6 Uncertainty Handling
Does the AI correctly identify uncertainty, ambiguity, missing evidence, or unsupported claims?

### 6.7 Hallucination Avoidance
Did the AI avoid fabricating facts, evidence, ownership, outcomes, or relationships?

### 6.8 Contract Compliance
Did the AI stay inside the responsibility and output boundary of the evaluated agent or stage?

### 6.9 Granularity
Are facts neither overly vague nor unnecessarily fragmented?

### 6.10 Reasoning Consistency
Where reasoning is part of the evaluated component, are conclusions internally consistent with the available evidence and rules?

## 7. Scoring Method

Each applicable criterion is scored on a 0–5 scale.

```text
0 = Failed / absent
1 = Severely deficient
2 = Partially correct
3 = Acceptable
4 = Strong
5 = Excellent
```

The weighting of individual criteria is NOT fixed globally.
For each evaluation, the applicable criteria and their relative weights MUST be defined before the run based on:
- the component under test;
- the evaluation objective;
- the agent or stage responsibility;
- the relevant contracts and risks.
The total criterion weights inside each section MUST equal 100%.
The resulting section scores are then mapped to the global evaluation weighting:
System Evaluation = 30%
AI Evaluation     = 70%

Example:
AI Evaluation criteria for one SourceAgent evaluation:

Factual Accuracy       30%
Context Preservation   20%
Provenance Quality     20%
Completeness           15%
Uncertainty Handling   15%
                       ----
                       100%

A different agent or workflow MAY use different criteria and weights.
The final normalized score is:
System Score = System criterion score × 30%
AI Score     = AI criterion score × 70%

Overall Score = System Score + AI Score


## 8. Critical Failure Gates

Some failures are too severe to be compensated for by a high numeric score.

If any applicable critical gate fails, the evaluation result is **FAIL**, regardless of the calculated score.

Critical gates include:

- unauthorized source access;
- secret or credential exposure;
- fabricated evidence;
- fabricated source provenance;
- cross-source contamination that changes meaning or ownership;
- silent loss of a successful source result;
- false success status after a failed required stage;
- critical stage-boundary violation;
- downstream processing based on known invalid or missing required state;
- replacement of source context with unsupported interpretation.

Individual evaluations MAY define additional critical gates when necessary.

## 9. Evidence Requirements

Every major finding MUST be supported by one or more evidence artifacts.

Accepted evidence includes:

- runtime logs;
- agent outputs;
- tool outputs;
- structured result objects;
- source material;
- exceptions;
- validation errors;
- API responses;
- test assertions;
- persisted workflow state.

Evaluation statements MUST distinguish between:

```text
Observed
Inferred
Expected
Not verified
```

A finding MUST NOT be presented as confirmed when the available evidence only supports inference.

## 10. Standard Evaluation Procedure

Every evaluation SHOULD follow this sequence:

```text
1. Define objective
2. Define hypothesis
3. Define component or stage under test
4. Define relevant contracts and rules
5. Define inputs
6. Define expected behavior
7. Define applicable System criteria
8. Define applicable AI criteria
9. Define critical gates
10. Execute the run
11. Preserve raw runtime evidence
12. Evaluate System behavior
13. Evaluate AI output
14. Check critical gates
15. Calculate scores
16. Record findings
17. Record architectural decision
18. Define follow-up actions
19. Determine regression impact
```

## 11. Evaluation Result Categories

### PASS
The tested objective is achieved, critical gates pass, and no important unresolved issue prevents adoption.

### PASS_WITH_FINDINGS
The tested objective is achieved and critical gates pass, but relevant weaknesses or optimization opportunities remain.

### PARTIAL
Only part of the hypothesis is validated, or important expected behavior is incomplete.

### FAIL
The hypothesis is not validated or at least one critical gate fails.

### BLOCKED
The evaluation cannot be completed because required infrastructure, source access, model access, or evidence is unavailable.

## 12. Architectural Decision Rules

Evaluation exists to support architectural decisions.

An architectural decision SHOULD NOT be considered validated only because:

- the code runs once;
- the HTTP endpoint returns `200`;
- the agent returns syntactically valid output;
- the final answer sounds plausible.

Validation requires evidence that the intended behavior was actually observed.

Every evaluation report SHOULD end with one of:

```text
KEEP
KEEP_WITH_CHANGES
RETEST
REPLACE
REJECT
```

and explain why.

## 13. Retry Evaluation Rules

Retries MUST be evaluated as explicit workflow behavior.

A retry SHOULD only occur when the failure is plausibly recoverable.

Examples of potentially retryable failures:
- transient network timeout;
- temporary provider failure;
- temporary rate limiting when an appropriate delay or recovery strategy exists.

Examples of failures that SHOULD NOT be blindly retried unchanged:
- invalid credentials;
- unauthorized source;
- unsupported format;
- deterministic validation failure;
- configuration error;
- malformed contract;
- missing required source;
- repeated identical model failure without changed conditions.

A successful retry does not erase the original failure. Both MUST remain visible in evaluation evidence.

## 14. Partial Success Rules

Partial success MUST be preserved.

Example:

```text
Source A → PARSED
Source B → FAILED
```

The system MUST preserve Source A's successful result.

It MUST NOT:
- discard Source A because Source B failed;
- merge both outcomes into one ambiguous status;
- falsely report complete success;
- reprocess Source A unnecessarily unless the evaluation explicitly requires it.

This principle applies to all later profiling stages where independent work units exist.

## 15. Regression Rules

Every architecture or AI change can create regressions.

When a change affects assumptions validated by an earlier evaluation:

1. identify affected prior evaluations;
2. rerun the relevant scenarios;
3. compare the new result with the previous result;
4. record regressions explicitly;
5. do not accept an improvement in one area if it introduces an unaccepted critical regression elsewhere.

Critical behavior that was previously validated MUST remain protected by regression tests or repeated evaluations where practical.

## 16. AI Evaluation Ground Truth

Where possible, AI evaluation SHOULD compare generated outputs against an explicit reference.

Possible reference types:
- manually reviewed source facts;
- expected structured output;
- source-grounded answer key;
- expert-reviewed evidence map;
- manually verified capability mapping.

The reference MUST be traceable to the same authorized source material.

The evaluation MUST NOT use unsupported outside assumptions as hidden ground truth.

## 17. Reproducibility

Each evaluation SHOULD record enough information to reproduce the run.

Recommended metadata:
- evaluation ID;
- date;
- model;
- model provider;
- relevant configuration;
- source set;
- source IDs;
- agent version or commit;
- prompt/spec version;
- changed files or architecture under test;
- runtime log path;
- important environment assumptions.

Secrets and credentials MUST NOT be recorded.

## 18. Standard Evaluation Report Structure

Every `EVAL-XXX.md` SHOULD use this structure:

```markdown
# EVAL-XXX — Title

## 1. Objective
## 2. Hypothesis
## 3. Component Under Test
## 4. Relevant Contracts and Rules
## 5. Inputs
## 6. Changes Under Test
## 7. Expected Behavior
## 8. Execution Evidence

## 9. System Evaluation
### Criteria
### Findings
### Score

## 10. AI Evaluation
### Criteria
### Findings
### Score

## 11. Critical Gates
## 12. Overall Score
## 13. Result
## 14. Key Findings
## 15. Architectural Decision
## 16. Follow-up Actions
## 17. Regression Impact
```

## 19. Evaluation Artifact Structure

Recommended repository structure:

```text
evaluation/
├── EVALUATION_PROTOCOL.md
├── EVAL-001.md
├── EVAL-002.md
├── EVAL-003.md
└── runs/
    ├── EVAL-001_run.log
    ├── EVAL-002_run.log
    └── ...
```

Responsibilities:

```text
EVALUATION_PROTOCOL.md
= permanent rules for how evaluations are performed

EVAL-XXX.md
= interpretation and scoring of one experiment

runs/EVAL-XXX_run.log
= raw execution evidence
```

Raw run logs MUST remain separate from evaluation interpretation.

## 20. Default Weighting Summary

Unless explicitly justified otherwise:

```text
SYSTEM EVALUATION
30%

AI EVALUATION
70%

CRITICAL FAILURE GATES
Must all pass
```

The final result is therefore not only a numeric score.

It is:

```text
Numeric Quality Score
+
Critical Gate Status
+
Architectural Decision
```

This protocol is the default evaluation standard for the profiling system and should be reused for future evaluations unless a documented protocol revision replaces it.
