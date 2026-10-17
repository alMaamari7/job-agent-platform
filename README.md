# Profiling Agent

An evidence-grounded AI profiling system that converts heterogeneous candidate sources into a structured, reusable Candidate Context.

The current implementation focuses on the **source-processing stage**: ingesting authorized candidate sources, extracting source-level facts, preserving context and contribution boundaries, and preparing structured information for later evidence and profile synthesis.

## Overview

The Profiling Agent is designed to build a reusable candidate representation from sources such as:

- CVs and resumes
- GitHub repositories
- project documentation
- thesis material
- certificates
- text and document files
- additional authorized candidate sources

The system uses a staged pipeline:

```text
Authorized Candidate Sources
        ↓
Source Processing
        ↓
Evidence Processing
        ↓
Capability Synthesis
        ↓
Candidate Context
```

The current development focus is the **Source Processing** stage.

## Core Goal

The system aims to create a candidate profile that is:

- evidence-grounded
- source-traceable
- reusable across downstream workflows
- independent of a specific job vacancy
- explicit about uncertainty
- careful about contribution and ownership
- resistant to unsupported claims and hallucinations

The resulting Candidate Context is intended to support later systems such as job matching, application analysis, CV adaptation, and candidate development.

## Design Principles

The profiling workflow follows semantic integrity rules such as:

```text
project ≠ employment
academic work ≠ employment
prototype ≠ production
participation ≠ leadership
tool usage ≠ mastery
public repository ≠ proof of the full private product
declared claim ≠ independently verified evidence
```

The system should preserve the original context of every claim rather than upgrading it into a stronger interpretation.

## Current Architecture

```text
CandidateSource
      ↓
ProfilingManager
      ↓
process_candidate_source(source_id)
      ↓
SourceAgent
      ↓
ReadCandidateSource
      ↓
DocumentReader / GitHubReader
      ↓
ParsedSourceResult
```

### ProfilingManager

The `ProfilingManager` controls the profiling workflow.

Current responsibilities include:

- processing all authorized candidate sources
- invoking source processing independently for each source
- preserving successful results
- continuing when another source encounters a recoverable failure
- enforcing the Source Processing stage boundary
- preventing premature evidence or profile synthesis

The manager does not perform source interpretation itself.

## SourceAgent

The `SourceAgent` processes exactly one authorized `CandidateSource` per execution.

Its responsibility is:

```text
SOURCE → SOURCE-LEVEL FACTS
```

The SourceAgent extracts and preserves:

- facts
- source context
- candidate contribution
- methods
- tools and resources
- stakeholders
- outcomes
- provenance
- uncertainty

It must not perform:

- cross-source reconciliation
- candidate-wide evidence synthesis
- capability synthesis
- job matching
- profile generation

## Independent Source Processing

A central architectural decision is that multiple sources are not bundled into one SourceAgent execution.

```text
ProfilingManager
    ├── SourceAgent(CV)
    │       ↓
    │   ParsedSourceResult
    │
    └── SourceAgent(GitHub)
            ↓
        ParsedSourceResult
```

This provides failure isolation. If one source fails, successful results from other sources remain available.

## Candidate Sources

Candidate sources are represented through a `CandidateSource` model.

Current source types include:

```text
FILE
GITHUB
URL
```

Typical metadata includes:

- `source_id`
- `source_type`
- original filename
- stored filename
- path
- URL
- content type
- creation timestamp

Candidate sources are authorized before they are passed into the profiling workflow.

## Source Access

Source access is abstracted from AI reasoning.

```text
ReadCandidateSource
    ├── DocumentReader
    └── GitHubReader
```

### DocumentReader

Currently supports document-oriented candidate sources such as:

- PDF
- DOCX
- TXT
- Markdown

### GitHubReader

The GitHub reader retrieves repository content for authorized repositories.

Authenticated GitHub access is supported through application configuration.

The reader is intentionally separate from the SourceAgent so repository access remains a deterministic source-access concern rather than an AI-agent responsibility.

## ParsedSourceResult

The SourceAgent returns one source-level result per CandidateSource.

Conceptually:

```text
ParsedSourceResult
├── source_id
├── source_type
├── status
├── facts
├── uncertainties
└── processing_notes
```

A fact can include:

```text
statement
fact_type
context
contribution
methods
tools_or_resources
stakeholders
outcomes
source_locator
```

The result represents only what can be established from the current source.

It does not yet represent candidate-wide evidence strength.

## Source Processing Status

Current source-level statuses include:

```text
PARSED
PARTIALLY_PARSED
UNAVAILABLE
UNSUPPORTED_FORMAT
FAILED_TO_PARSE
```

The workflow is designed to preserve partial success instead of collapsing the entire profiling run when one source fails.

## Candidate Context Model

The future profiling output is defined around a reusable Candidate Context.

Planned core artifacts include:

```text
PROFILE.md
SOURCE_INDEX.md
EVIDENCE_INDEX.md
CAPABILITY_MAP.md
LIMITATIONS.md
profile/
```

Candidate-wide support levels are expected to include:

```text
CORROBORATED
SUPPORTED
CANDIDATE_STATED
UNCERTAIN
UNKNOWN
```

These support levels belong to later evidence processing and are intentionally not assigned by the SourceAgent.

## Agent Decomposition

The profiling system is being developed as a staged multi-agent workflow.

```text
ProfilingManager
    ↓
SourceAgent
    ↓
EvidenceAgent
    ↓
ProfileAgent
```

### Current

- ProfilingManager
- SourceAgent
- source readers
- candidate source ingestion
- source-level fact extraction
- source-level uncertainty handling

### Planned

- EvidenceAgent
- cross-source reconciliation
- evidence support classification
- capability synthesis
- Candidate Context generation
- profile validation

## Evaluation-Driven Development

The project uses explicit evaluation as part of the architecture process.

```text
Hypothesis
    ↓
Implementation
    ↓
Evaluation
    ↓
Findings
    ↓
Architectural Decision
    ↓
Regression Test
```

Evaluation artifacts are stored separately from runtime logs.

```text
evaluation/
├── EVALUATION_PROTOCOL.md
├── EVAL-001.md
├── EVAL-002.md
└── runs/
```

## Evaluation Framework

Evaluations are divided into two dimensions:

```text
System Evaluation = 30%
AI Evaluation     = 70%
```

### System Evaluation

Examples:

- orchestration correctness
- source isolation
- stage boundaries
- failure isolation
- authorization
- retry behavior
- runtime stability
- logging
- efficiency

### AI Evaluation

Examples:

- factual accuracy
- completeness
- context preservation
- contribution preservation
- provenance
- uncertainty handling
- hallucination avoidance
- contract compliance

Critical failures cannot be compensated for by a high numeric score.

## EVAL-002 Result

The current Source Processing architecture was evaluated with:

```text
1 CV
1 GitHub repository
```

Observed behavior:

```text
CV
→ independent SourceAgent execution
→ PARSED

GitHub
→ independent SourceAgent execution
→ transient timeout
→ retry
→ PARSED
```

The evaluation confirmed:

- independent source execution
- failure isolation
- successful result preservation
- authenticated GitHub access
- correct Source Processing stage boundary
- strong context preservation

Current evaluation result:

```text
PASS_WITH_FINDINGS
```

Architectural decision:

```text
KEEP_WITH_CHANGES
```

Important remaining findings include:

- deterministic structured-output validation
- temporal reasoning correctness
- ground-truth AI evaluation
- retry-policy hardening
- GitHub processing efficiency

## Evaluation Philosophy

The project does not aim to optimize every metric indefinitely.

A component is considered ready to move forward when:

- critical gates pass
- system behavior is stable enough for downstream use
- AI quality is sufficiently strong
- no unresolved defect creates unacceptable downstream risk

Optimization is prioritized according to impact rather than score alone.

## Ground-Truth Evaluation

Future AI evaluations will use manually reviewed reference datasets.

The intended process is:

```text
Source Material
      ↓
Profiling Agent Output
      ↓
Independent Baseline Output
      ↓
Manual Adjudication
      ↓
Canonical Ground Truth
```

An independent general-purpose AI system may be used as a comparison baseline or Ground-Truth Assistant, but its output is not automatically treated as ground truth.

Ground truth must remain traceable to the original authorized source.

## Technology Stack

Current backend technologies include:

- Python
- FastAPI
- Pydantic v2
- smolagents
- Hugging Face Inference
- DeepInfra
- GitHub API
- dotenv-based configuration

Current LLM setup:

```text
deepseek-ai/DeepSeek-V4-Flash-0731
```

## Project Structure

Current profiling-related structure:

```text
backend/
├── app/
│   ├── ai/
│   │   └── agents/
│   │       └── profilling_agent/
│   │           ├── agents/
│   │           │   ├── profiling_manager/
│   │           │   └── source_agent/
│   │           └── tools/
│   │               └── source_access/
│   │                   └── readers/
│   ├── core/
│   ├── models/
│   └── services/
│
├── evaluation/
│   ├── EVALUATION_PROTOCOL.md
│   ├── EVAL-001.md
│   ├── EVAL-002.md
│   └── runs/
│
├── .env
└── run_dev.ps1
```

> Note: the current package path uses the existing spelling `profilling_agent`.

## Configuration

Environment variables are loaded from `.env`.

Example:

```env
HF_TOKEN=your_huggingface_token
GITHUB_TOKEN=your_github_token
```

Secrets must never be committed to Git.

The repository should include `.env` in `.gitignore`.

## Running the Backend

From the backend directory:

```powershell
.\.venv\Scripts\Activate.ps1
.\run_dev.ps1
```

The development script configures UTF-8 handling and starts the FastAPI application through Uvicorn.

## Profiling Flow

Typical development flow:

```text
1. Add candidate sources
2. Store authorized CandidateSource metadata
3. Start profiling
4. ProfilingManager loads sources
5. Each source is processed independently
6. SourceAgent returns ParsedSourceResult
7. Successful results are preserved
8. Workflow stops at the current Source Processing boundary
```

The profiling endpoint currently initiates this workflow through:

```text
POST /profiling/start
```

## Current Development Priorities

The Source Processing architecture is considered stable enough to retain.

### P0 — ParsedSourceResult Validation

Introduce deterministic validation before downstream agents consume SourceAgent output.

### P0 — Temporal and Semantic Correctness

Prevent incorrect temporal uncertainty and similar semantic interpretation errors.

### P1 — Ground-Truth Evaluation Set

Create manually reviewed benchmark cases for AI evaluation.

### P2 — Retry Policy

Move retry classification from LLM-driven behavior toward explicit deterministic control.

### P2 — GitHub Processing Efficiency

Reduce unnecessary repository payload, token consumption, and timeout risk.

## Roadmap

```text
Source Processing
    ✅ architecture established
    ✅ independent source execution
    ✅ CV processing
    ✅ authenticated GitHub processing
    ✅ evaluation protocol
    ✅ EVAL-002

Structured Output Hardening
    ⏳

Ground-Truth Dataset
    ⏳

EvidenceAgent
    ⏳

Capability Synthesis
    ⏳

ProfileAgent
    ⏳

Candidate Context Validation
    ⏳
```

## Status

The Profiling Agent is currently an **active development and evaluation project**.

The Source Processing stage is functional and has passed its current architectural evaluation with findings.

Later evidence synthesis and Candidate Context generation are not yet considered complete.
