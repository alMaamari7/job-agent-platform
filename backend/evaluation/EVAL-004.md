# EVAL-004 — SourceManager ExecutionPlan Orchestration and Result Handoff

> **Evaluation status:** `FAIL`  
> **Architectural decision:** `RETEST` (do not adopt this tested implementation as validated)  
> **Reference:** `backend/evaluation/EVALUATION_PROTOCOL.md`  
> **Raw execution evidence:** `runs/EVAL-004_run.log` (unaltered copy of the submitted log)

## 1. Objective

Evaluate whether the tested three-layer source-processing architecture (`ProfilingManager → SourceManager → ExecutionPlan / SourceAgent`) can handle two authorized sources, delegate one source per worker request, collect and review `ParsedSourceResult` objects, preserve successful partial outputs, propagate errors, and return a truthful `SourceProcessingResult` without proceeding to downstream profiling stages. Evaluate the quality of any AI-produced source facts that are visible in the trace.

This report is a **retrospective evaluation of the supplied log**, not a new execution. The protocol requires criteria and weights to be chosen *before* a run. Since that pre-registration is not evidenced here, scores below are explicitly **diagnostic, not prospectively pre-registered experimental results**.

## 2. Hypothesis

The SourceManager will receive only the authorized source set, create a schema-valid `ExecutionPlan` with one request per source, invoke the SourceAgent for each, receive independently accessible worker outputs, and produce a `SourceProcessingResult` that correctly distinguishes success, partial success, and failures. A recoverable failure may trigger bounded retry, but a deterministic program/schema defect must not lead to unchanged re-execution. Successfully produced source results will not be silently lost.

## 3. Component Under Test

Observed in the submitted log:

```text
ProfilingManager
   └── source_manager (managed agent)
         └── execute_execution_plan(ExecutionPlan)
               ├── SourceAgent(CV) → read_candidate_source(CV)
               └── SourceAgent(GitHub) [planned; actual worker run not observed]
```

**Version limitation:** The repository `main` code inspected on 2026-11-08 exposes `ProfilingManager → process_candidate_source(source_id) → SourceAgent.run(source)` rather than the `source_manager → execute_execution_plan` mechanism seen in the supplied log. The evaluated log therefore cannot be attributed to a specific current `main` commit. The test revision/commit is **not verified**, and comparisons to EVAL-002 are architectural context, not controlled regressions.

## 4. Relevant Contracts and Rules

Reference: `EVALUATION_PROTOCOL.md`, notably §§2, 4–10, 13–18.

Applicable experiment contracts visible in the log: (1) process only the two explicitly authorized sources; (2) each SourceAgent handles exactly one source; (3) SourceAgent returns one `ParsedSourceResult`, initially with `NEEDS_MANAGER_REVIEW`; (4) SourceManager owns review/approval and emits source-stage results; (5) preserve factual context, contribution, uncertainty, and locators; (6) no evidence processing, candidate representation or profile generation during this test; (7) preserve successful partial outputs; (8) do not blindly retry deterministic validation or configuration errors.

The emitted schema lists `ParsedSourceReviewStatus` values `NEEDS_MANAGER_REVIEW`, `NEEDS_IMPROVEMENT`, `APPROVED_BY_MANAGER`, and `EXECUTION_FAILED`. `FAILED_TO_EXECUTE` is **not** among them (raw log lines 396–406 and 1993–2008).

## 5. Inputs

- PDF: `source_id=52a1e3cf-5617-45e4-959d-2145b3f80e5a`; `source_type=file`; `Asaad_Al-Maamari_AI_Software_CV.pdf`.
- GitHub: `source_id=7d8d6e0b-7c79-4ed9-bf0a-3f2f0be79e87`; `source_type=github`; `https://github.com/alMaamari7/ai-interior-designer-portfolio`.
- Claimed/returned mode: `INITIAL_PROFILE_BUILD`.
- Model observed: `InferenceClientModel – deepseek-ai/DeepSeek-V4-Flash-0731`.
- Run date, model settings, commit SHA, prompt revision, exact provider configuration: **not verified by the log**.

## 6. Changes Under Test

The test exercises a `SourceManager` and structured `ExecutionPlan` intermediary plus an execution tool capable of dispatching worker requests. The exact code diff or revision relative to EVAL-001/EVAL-002 is unavailable. Accordingly, this evaluation does **not** claim the new orchestration is a verified regression of the checked-out `main` version.

## 7. Expected Behavior

1. Resolve an initial/update mode from available state.
2. Keep the two authorized source IDs unchanged.
3. Submit a complete, valid execution plan without model-driven schema discovery.
4. Execute each source independently.
5. Receive actual `AgentExecutionResult` / `ParsedSourceResult` objects and preserve successes across failures.
6. Record review decisions and failure statuses using only valid enum members.
7. Return an accurate stage outcome, including partial results and limitations.
8. Stop before downstream phases.

## 8. Execution Evidence

| Evidence ID | Observed log event | Raw log location |
|---|---|---|
| EV-01 | ProfilingManager receives two authorized sources and delegates to `source_manager`. | lines 2–76 |
| EV-02 | First plan rejected: `execution_requests` missing. | lines 119–141 |
| EV-03 | Second plan rejected: per-request `input` and `execution_context` missing. | lines 142–177 |
| EV-04 | Third plan rejected: `execution_context.run_id` missing. | lines 178–220 |
| EV-05 | Fourth plan initiates a CV `source_agent` run; assigned source is the PDF only. | lines 221–264 |
| EV-06 | CV reader returns two-page source text. | lines 720–819 |
| EV-07 | SourceAgent generates a `ParsedSourceResult` with `status=PARSED`, 15 facts, and `NEEDS_MANAGER_REVIEW`. | lines 822–1040; 1517–1992 |
| EV-08 | Execution tool fails after CV worker activity: `ParsedSourceReviewStatus` has no `FAILED_TO_EXECUTE`. | lines 1993–2010 |
| EV-09 | A second plan reruns the **same CV source**, again producing a JSON source result, now 14 facts. | lines 2011–2030, 2611–2825 and 3325 onward |
| EV-10 | The second execution tool call again ends with the same `AttributeError`. | around lines 3740–3830 (search in raw log for `plan-002` and `FAILED_TO_EXECUTE`) |
| EV-11 | SourceManager returns `BLOCKED` and no usable result objects; ProfilingManager preserves `BLOCKED`, does not advance downstream, and HTTP returns `200 OK`. | lines 3910–4782; final lines 4712–4782 |

**Important evidence distinction:** A SourceAgent demonstrably **generated** two CV results, but neither result was **successfully returned as a usable `AgentExecutionResult` to the SourceManager**. Thus the SourceManager's `parsed_source_results=[]` reflects failed handoff, not absence of source extraction. No GitHub SourceAgent worker start or GitHub content read was observed. The two planned GitHub requests alone are not proof of execution.

## 9. System Evaluation

### Criteria

Retrospective, diagnostic 0–5 rubric; weights total 100% within the section:

| Criterion | Weight | Score | Weighted contribution (/100) |
|---|---:|---:|---:|
| Orchestration and source coverage | 20% | 2/5 | 8 |
| Tool/schema contract enforcement | 20% | 1/5 | 4 |
| Failure isolation and successful result preservation | 20% | 1/5 | 4 |
| Retry behavior | 15% | 1/5 | 3 |
| Stage-boundary enforcement | 10% | 5/5 | 10 |
| Authorization boundaries | 5% | 5/5 | 5 |
| Logging and observability | 5% | 4/5 | 4 |
| Runtime/token efficiency | 5% | 1/5 | 1 |
| **Total** | **100%** | | **39/100** |

### Findings

**SYS-01 / observed:** The SourceManager preserved both authorized IDs in its plan and passed exactly one PDF source into each observed SourceAgent run (EV-01, EV-05, EV-09). Its second planned GitHub request was not demonstrably executed; full source coverage failed.

**SYS-02 / observed:** Three consecutive Pydantic validation failures exposed missing `ExecutionPlan` fields, requiring the LLM to infer the schema incrementally (EV-02–04). This is a tool-interface/planning deficiency, not evidence of invalid source material.

**SYS-03 / observed:** The plan accepted by validation then failed with an undefined enum attribute (`FAILED_TO_EXECUTE`) in the execution tool (EV-08, EV-10). The schema itself lists `EXECUTION_FAILED`, not `FAILED_TO_EXECUTE`. **Exact implementation location of the failing reference is not verified** without the corresponding tested revision.

**SYS-04 / observed:** Two CV results were generated, but the source-processing aggregation returned no usable `ParsedSourceResult`. This is an observed *handoff/result-preservation failure*. Whether a durable stored copy existed is **not verified**; do not describe the results as definitively deleted from persistence.

**SYS-05 / observed:** The same deterministic `AttributeError` was followed by a second execution plan and another expensive CV run. The system did not demonstrate error classification or bounded recovery (EV-08–10).

**SYS-06 / observed:** Manager returned control with `BLOCKED`; ProfilingManager did not claim a completed profiling workflow or start downstream evidence/profile phases. HTTP `200 OK` reflects transport success, **not** business-workflow success (EV-11).

**SYS-07 / observed:** Trace includes tool calls, errors, outputs and step token/duration metadata; however, it repeats the full input schema and large worker output, increasing token/observability overhead. Total model billing and wall time are **not verified** from the step metadata alone.

### Score

`System = 39/100 × 30 = 11.7/30.`

## 10. AI Evaluation

### Criteria

The following rubric is diagnostic **for visible CV SourceAgent output only**, not for the complete two-source stage. It reuses the AI criterion weights from EVAL-002 to aid comparability, while explicitly acknowledging that the weights were not pre-registered for this execution.

| Criterion | Weight | Score | Weighted contribution (/100) |
|---|---:|---:|---:|
| Factual Accuracy | 25% | 4/5 | 20 |
| Completeness | 15% | 3/5 | 9 |
| Context Preservation | 15% | 3/5 | 9 |
| Contribution Preservation | 10% | 3/5 | 6 |
| Provenance Quality | 10% | 4/5 | 8 |
| Uncertainty Handling | 10% | 2/5 | 4 |
| Hallucination Avoidance | 10% | 3/5 | 6 |
| Contract Compliance | 5% | 4/5 | 4 |
| **Total** | **100%** | | **66/100** |

### Findings

**AI-01 / observed:** First worker output contains 15 structured CV facts and the second 14. Both capture central CV themes (degree, personal AI project, bachelor-thesis prototype, employment, languages); no manually reviewed expected-facts inventory exists for a formal completeness/recall score. Different counts alone are not proof of inaccuracy, but demonstrate sensitivity to repeated execution (EV-07, EV-09).

**AI-02 / observed:** A B.Sc. degree is represented with `context.type=THESIS` in the first run, and `ACADEMIC_PROJECT` in the next. Both are semantically poor categories for the **degree itself**, despite the underlying degree fact being supported (raw lines 836–847, 2615–2624).

**AI-03 / observed:** Source text lists two distinct Healthcare Assistant periods (`Dec 2020–Jul 2023` and `Nov 2025–May 2026`), but the first result's single `start_date/end_date` spans both periods and the second result includes only the first range in structured context (raw lines 805–807, 980–992, 2774–2786). The statements preserve both ranges; the structured dates lose that distinction.

**AI-04 / observed:** The first run invents a temporal concern (`FUTURE_DATED_EMPLOYMENT`) that is not justified for a run occurring after May 2026. The claim rests on an unspecified “conventional profiling reference point” rather than a supplied comparison date (raw lines 1029–1034). Current conversation date is November 2026; exact execution date is not contained in the log. Even without that date, the uncertainty is unsupported as phrased.

**AI-05 / observed:** PDF facts predominantly carry `source_locator` page numbers 1 or 2 and distinguish projects, thesis work and working-student employment. Provenance precision is adequate at the page level, but a page locator by itself does not independently verify each semantic interpretation.

**AI-06 / observed:** Labels vary between runs (`DEVELOPED`, `IMPLEMENTED`, `EVALUATED`, `EXECUTED`, `ASSISTED`, etc.). Some labels are not from the SourceAgent prompt's example set; the visible schema accepts a plain string, so **this alone is not a schema violation**. The evaluation concerns consistency and whether the label remains supported by the underlying CV.

**AI-07 / observed:** No evidence processing, capability synthesis, job matching or profile generation appears in the visible SourceAgent outputs. The result does not demonstrate SourceManager review/approval because the handoff failed.

**AI-08 / not verified:** GitHub extraction quality, full two-source completeness, cross-run stability across more trials, and any persisted AI outputs are not measurable from this log.

### Score

`Observed CV-only AI score = 66/100 × 70 = 46.2/70.` This is a **restricted diagnostic estimate** and must not be misrepresented as a fully tested AI stage score.

## 11. Critical Gates

| Gate | Evaluation | Evidence or limitation |
|---|---|---|
| Unauthorized source access | No violation observed | CV reads use authorized ID; GitHub read absent (EV-05–06, EV-09) |
| Credential/secret exposure | No violation observed | The reviewed log does not show secrets; no broader secrets audit |
| Fabricated evidence | Not verified fully | Visible CV facts evaluated only; no independent full reference |
| Fabricated source provenance | No clear violation observed | PDF page locators match available pages; not independently audited per fact |
| Cross-source contamination changing meaning/ownership | Not verified | Only CV worker output visible |
| **Silent loss of a successful source result** | **FAIL (handoff preservation)** | Generated CV results did not reach the stage result (EV-07–11) |
| False success after required-stage failure | PASS | Final stage status `BLOCKED` rather than `COMPLETE` (EV-11) |
| Critical stage-boundary violation | PASS, within visible trace | No downstream evidence/profile processing (EV-11) |
| Downstream processing based on invalid state | PASS | Downstream not executed (EV-11) |
| Replacement of source context by unsupported interpretation | Concern, not independently gated | Degree and dates misclassified (AI-02–04) |

**Gate verdict: FAIL**, based on failure to preserve/hand off visibly generated successful worker output. Do not infer persistence-layer deletion; the violated observable invariant is that the stage result fails to retain it.

## 12. Overall Score

Retrospective diagnostic arithmetic:

```text
System: 39/100 × 30% = 11.7/30
AI:     66/100 × 70% = 46.2/70 (CV only)
-------------------------------------------
Illustrative combined figure: 57.9/100
```

**Interpretation:** `57.9/100` is *not a fully validated two-source overall quality score* because GitHub AI output was not observed and criterion weights were not registered before this execution. It is included only for traceable comparison in the protocol's 30/70 format. **Critical-gate failure takes precedence.**

## 13. Result

**`FAIL`** — the principal hypothesis is not validated. The SourceManager cannot demonstrate reliable completion or preservation of generated source results; deterministic execution-layer errors block the required stage. The system correctly reports `BLOCKED` as its runtime workflow status; that operational status is distinct from this **evaluation result** of `FAIL`.

## 14. Key Findings

**Validated parts:** (1) Authorized set is communicated; (2) one-source-per-worker instructions are respected in observed CV calls; (3) the document reader works; (4) SourceAgent produces structured CV facts; (5) failed source processing does not trigger downstream stages; (6) final manager status acknowledges the failure.

**Not validated:** Complete source coverage, execution-plan contract reliability, execution result handling, preservation of partial success, manager review/approval, error classification, bounded retries, full AI quality, and source-level persistence.

**Crucial distinction:** "No results delivered to SourceManager" is supported. "No source facts ever extracted" is contradicted by the SourceAgent trace.

## 15. Architectural Decision

**`RETEST`** (tested implementation **not approved**). Retain the SourceManager architecture only as a hypothesis until the deterministic failure path and handoff invariants are repaired. The log does not justify wholesale `REJECT` of the architectural concept, nor `KEEP` of this broken implementation. Compare with the one-source-per-tool architecture of EVAL-002 only after identifying the tested commit and running controlled regression cases.

## 16. Follow-up Actions

| Priority | Action | Acceptance condition |
|---|---|---|
| P0 | Resolve `FAILED_TO_EXECUTE` vs. `EXECUTION_FAILED` enum contract across execution layer, status transitions and result serialization. | Both success and worker-failure paths return schema-valid results without `AttributeError`. |
| P0 | Preserve each worker result independently *before* or regardless of other worker errors and propagate them to `SourceProcessingResult`. | CV success remains accessible when GitHub fails; no `parsed_source_results=[]` after a completed CV result. |
| P0 | Add deterministic `ExecutionPlan` construction/schema validation prior to invocation. | All required fields supplied on first tool call; no iterative schema-discovery calls. |
| P1 | Implement error classification and bounded retries. | Permanent programming/validation errors do not trigger unchanged worker reruns; transient failures may be retried with recorded attempts. |
| P1 | Add end-to-end stage tests for one success, one failure, two successes, and two failures. | Accurate per-source statuses, review outcomes, and honest aggregate status. |
| P1 | Validate `ParsedSourceResult` semantics and source locators. | Degree, thesis and jobs distinguished; disjoint date ranges preserved; invalid temporal warnings rejected. |
| P2 | Create manually reviewed CV/GitHub source-fact benchmark, including negative cases. | Factual accuracy, recall, contribution and provenance scored against reproducible ground truth. |
| P2 | Reduce repeated schema/worker context and record tokens by task. | Efficiency demonstrably improves without factual recall regression. |
| P2 | Record tested commit, prompt versions and execution date in each run. | EVAL-004 reproducible on an identified revision. |

## 17. Regression Impact

Any changes to execution-plan schema, `SourceManager`, status enums, SourceAgent output, result collation, source access, or retry rules should rerun EVAL-004 scenarios. Preserve tests of EVAL-002 invariants: independent source processing, each source attempted, results survive unrelated failures, no unauthorized reads, no premature evidence/profile processing, no false success, and traceable source facts. A successful rerun must include **both** source worker outputs and an explicit per-source result map; an HTTP `200` response alone is insufficient.
