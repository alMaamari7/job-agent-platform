# EVAL-001 — ProfilingManager + SourceAgent

## 1. Evaluation Metadata

```yaml
evaluation_id: EVAL-001
architecture: ProfilingManager + SourceAgent
status: COMPLETED_WITH_FAILURES
run_log: runs/EVAL-001_run.log
```

The complete technical execution trace for this evaluation is stored in:

```text
runs/EVAL-001_run.log
```

This evaluation document does not duplicate the complete runtime log. It records the important observations, conclusions, and architectural decisions derived from that run.

---

## 2. Evaluation Goal

Evaluate the first decomposition of the Candidate Profiling workflow into:

```text
ProfilingManager
      ↓
SourceAgent
      ↓
ReadCandidateSource
      ↓
DocumentReader / GitHubReader
```

The evaluation focuses on whether:

- the `ProfilingManager` correctly delegates source processing;
- the `SourceAgent` remains within its `SOURCE -> FACTS` responsibility;
- authorized Candidate Sources are actually accessed;
- source-specific failures are handled correctly;
- the Manager stops the workflow when required outputs are unavailable;
- the separation between `ProfilingManager` and `SourceAgent` is practically useful.

---

## 3. Test Setup

### Model

```text
deepseek-ai/DeepSeek-V4-Flash-0731
```

### Candidate Sources

Two authorized Candidate Sources were provided:

```text
Source 1
Type: FILE
File: Asaad_Al-Maamari_AI_Software_CV.pdf

Source 2
Type: GITHUB
Repository:
https://github.com/alMaamari7/ai-interior-designer-portfolio
```

Only the Source Processing stage was enabled.

The following stages were intentionally excluded:

```text
Evidence Processing
Capability Discovery
Candidate Profile Generation
```

---

## 4. Expected Behavior

Expected execution:

```text
ProfilingManager
      ↓
resolve authorized sources
      ↓
delegate source processing
      ↓
SourceAgent
      ↓
read_candidate_source
      ↓
ParsedSourceResult
      ↓
ProfilingManager
```

Each Candidate Source should ideally produce an independent result.

Example:

```text
CV
→ PARSED

GitHub
→ PARSED
```

or:

```text
CV
→ PARSED

GitHub
→ UNAVAILABLE
```

A failure of one source should not destroy successfully processed results from another source.

---

## 5. Observed Results

Full technical trace:

```text
runs/EVAL-001_run.log
```

### 5.1 Manager Delegation

The `ProfilingManager` correctly identified Source Processing as the required stage and delegated the work to the `SourceAgent`.

Result:

```text
PASS
```

---

### 5.2 SourceAgent Boundary

The `SourceAgent` received instructions limited to:

```text
SOURCE -> FACTS
```

It was explicitly prevented from performing:

```text
Evidence Processing
Capability Extraction
Profile Generation
```

The observed behavior remained inside this boundary.

Result:

```text
PASS
```

---

### 5.3 Source Tool Usage

The `SourceAgent` correctly invoked:

```text
read_candidate_source
```

for both authorized source IDs.

Result:

```text
PASS
```

---

### 5.4 PDF Source Processing

The PDF CV was successfully accessed and its content was returned to the SourceAgent.

Observed content included:

- candidate profile information;
- technical skills;
- projects;
- technologies;
- thesis information;
- professional experience.

The infrastructure path:

```text
FILE
→ ReadCandidateSource
→ DocumentReader
→ Source Content
```

worked successfully.

Result:

```text
PASS
```

---

### 5.5 GitHub Source Processing

The GitHub repository request failed with:

```text
HTTP 403
rate limit exceeded
```

This failure occurred in the Source Access Layer rather than in the SourceAgent reasoning itself.

Result:

```text
FAIL
```

Likely cause:

```text
GitHub API
→ unauthenticated or insufficiently authenticated request
→ rate limit
→ HTTP 403
```

---

### 5.6 Managed-Agent Handoff Encoding

The SourceAgent could not successfully return its result because the delegation mechanism repeatedly produced:

```text
'charmap' codec can't encode character '\u2192'
```

The affected Unicode character was:

```text
→
```

This indicates an infrastructure or terminal encoding issue rather than a semantic failure of the SourceAgent.

Result:

```text
FAIL
```

---

### 5.7 Retry Behavior

The `ProfilingManager` detected the SourceAgent failure and attempted recovery.

It changed the delegated task and requested plain ASCII output.

However, the same SourceAgent operation was repeated multiple times without resolving the underlying infrastructure error.

Result:

```text
PARTIAL PASS
```

Positive:

```text
failure detected
recovery attempted
```

Negative:

```text
repeated equivalent calls
increased token usage
increased latency
no error-classification strategy
```

---

### 5.8 Workflow Failure Handling

The `ProfilingManager` correctly refused to continue into:

```text
Evidence Processing
Candidate Representation
```

because valid Source Processing outputs were unavailable.

The final workflow state remained:

```text
SOURCE_PROCESSING
```

and the run was marked incomplete.

Result:

```text
PASS
```

---

## 6. Evaluation Metrics

### Functional Results

| Criterion | Result |
|---|---|
| Manager delegates Source Processing | PASS |
| SourceAgent starts correctly | PASS |
| SourceAgent uses Source Access Tool | PASS |
| PDF Source Access | PASS |
| GitHub Source Access | FAIL |
| `SOURCE -> FACTS` boundary maintained | PASS |
| Workflow stops on critical failure | PASS |
| Partial source success preserved | FAIL |
| Managed-Agent return path | FAIL |
| Recovery behavior | PARTIAL PASS |

### Runtime Observation

The run consumed approximately:

```text
Input tokens: 33,171
Output tokens: 3,537
```

This is high for a Source Processing experiment and indicates that retry behavior needs to be constrained.

Exact runtime details remain available in:

```text
runs/EVAL-001_run.log
```

---

## 7. Main Findings

### Finding 1 — Multi-Agent Delegation Works

The core architecture:

```text
ProfilingManager
→ SourceAgent
→ ReadCandidateSource
```

works.

The Manager can delegate work to the SourceAgent, and the SourceAgent can invoke its Source Access Tool.

This supports keeping the two responsibilities separate for further testing.

---

### Finding 2 — Manager and SourceAgent Have Distinct Responsibilities

The experiment showed a practical distinction between:

```text
ProfilingManager
→ orchestration

SourceAgent
→ source understanding
```

The SourceAgent did not perform Candidate Profile or Evidence reasoning.

This supports the current architectural separation.

---

### Finding 3 — One Source Should Produce One Independent Result

Both sources were included in one SourceAgent task.

Observed situation:

```text
CV
→ successfully read

GitHub
→ failed

SourceAgent return
→ failed
```

As a result, the successfully accessed CV could not be preserved as an independent successful source result.

The SourceAgent contract should therefore move toward:

```text
1 CandidateSource
      ↓
1 SourceAgent execution
      ↓
1 ParsedSourceResult
```

The ProfilingManager should aggregate those results afterward.

---

### Finding 4 — Retry Behavior Needs Explicit Control

The Manager repeatedly called the SourceAgent after the same infrastructure error.

This demonstrates that autonomous retry behavior should not remain completely open-ended.

Future orchestration should distinguish between:

```text
recoverable error
non-recoverable error
source-specific error
infrastructure error
```

Retries should only occur when they are likely to change the outcome.

---

### Finding 5 — Failure-Aware Manager Behavior Was Useful

The Manager correctly refused to continue the workflow after Source Processing failed.

This behavior supports retaining orchestration responsibility outside of the SourceAgent.

---

## 8. Architecture Decision

### Current Decision

Keep the experimental separation:

```text
ProfilingManager
+
SourceAgent
```

for the next evaluation.

EVAL-001 did not reveal a fundamental problem with the separation itself.

The main failures were related to:

```text
encoding
GitHub Source Access
retry control
source-result granularity
```

rather than the existence of two separate agents.

---

## 9. Changes Before EVAL-002

### Change 1 — UTF-8 Handling

Fix the Windows encoding issue causing:

```text
'charmap' codec can't encode character
```

---

### Change 2 — GitHub Authentication

Add authenticated GitHub API access to avoid the current unauthenticated rate-limit failure.

---

### Change 3 — One Source Per SourceAgent Execution

Change from:

```text
SourceAgent
→ Source A + Source B
```

to:

```text
SourceAgent(Source A)
→ ParsedSourceResult A

SourceAgent(Source B)
→ ParsedSourceResult B
```

The ProfilingManager then aggregates the independent results.

---

### Change 4 — Retry Policy

Introduce explicit retry rules.

For example:

```text
transient network error
→ retry

rate limit
→ do not immediately repeat unchanged request

encoding/configuration failure
→ stop and surface infrastructure error
```

---

## 10. EVAL-002 Goal

EVAL-002 should repeat the same general test after these changes.

Primary question:

```text
Can the ProfilingManager process multiple Candidate Sources
independently through the SourceAgent while preserving partial
success and avoiding unnecessary retries?
```

Expected behavior:

```text
Source A
→ ParsedSourceResult

Source B
→ ParsedSourceResult
```

or, when one source fails:

```text
Source A
→ PARSED

Source B
→ UNAVAILABLE

Manager
→ preserves Source A
→ records Source B failure
→ does not repeat pointless calls
```

---

## 11. Evidence

Primary runtime evidence for this evaluation:

```text
runs/EVAL-001_run.log
```

The runtime log is the source of truth for the technical execution.

This evaluation document contains the interpretation and architectural conclusions derived from that run.