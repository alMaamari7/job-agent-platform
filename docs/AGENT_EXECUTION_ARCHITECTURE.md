Agent Execution Architecture
1. Purpose
This document defines the target architecture for creating, configuring, coordinating, and executing AI managers and AI worker agents inside the Job Agent Platform.

The architecture is based on a hierarchical AI team:
ProfilingManager AI
│
├── SourceManager AI
│   └── SourceAgent instances
│
├── EvidenceManager AI
│   └── EvidenceAgent instances
│
└── ProfileManager AI
    └── ProfileAgent instances
The goal is to separate:
- global profiling orchestration;
- phase-specific AI management;
- execution coordination;
- agent definitions;
- agent creation;
- specialized AI work;
- deterministic infrastructure and validation.
Status: Target Architecture — incremental implementation planned.

2. Core Architecture
The architecture has two major layers:
AI Management Layer
│
├── ProfilingManager AI
│   ├── SourceManager AI
│   ├── EvidenceManager AI
│   └── ProfileManager AI
│
└── Worker Agent Layer
    ├── SourceAgent
    ├── EvidenceAgent
    └── ProfileAgent
All managers are AI agents.

They use a shared execution infrastructure:
AI Manager
    ↓
ExecutionCoordinator
    ↓
AgentEngine
    ↓
AgentRegistry
    ↓
Agent Instance
The main questions are:
ProfilingManager AI
→ Which profiling phase should run next?

Phase Manager AI
→ What work is required inside this phase?

ExecutionCoordinator
→ How should the requested work be executed?

AgentRegistry
→ Which manager and worker agent types are allowed?

AgentEngine
→ How is a requested AI agent instance created?

Agent Instance
→ How is one concrete AI task performed?
3. AI Manager Hierarchy
3.1 ProfilingManager AI
The ProfilingManager is the top-level AI manager for candidate profiling.

It understands the complete profiling process and coordinates the phase managers.

Conceptually:
ProfilingManager AI
│
├── SourceManager AI
├── EvidenceManager AI
└── ProfileManager AI
Its responsibility is not to perform source analysis, evidence analysis, or profile synthesis itself.

Its responsibility is to manage the overall profiling workflow.
Responsibilities
The ProfilingManager may decide:
- which profiling phase should run;
- which phase manager should receive control;
- whether enough information exists to continue;
- whether a phase needs additional work;
- whether the profiling workflow can progress;
- whether a completed phase should be revisited;
- whether the profiling process is complete.
Example
Candidate Sources available
        ↓
ProfilingManager AI
        ↓
"Source Processing must run first."
        ↓
SourceManager AI
        ↓
Source Processing Result
        ↓
ProfilingManager AI
        ↓
"Source Processing is sufficient.
Proceed to Evidence Processing."
        ↓
EvidenceManager AI
The ProfilingManager should not
- extract source-level facts itself;
- evaluate individual source contents;
- build Evidence Records itself;
- create the final Candidate Context itself;
- construct ToolCallingAgent instances directly;
- dynamically grant unrestricted tools.
The ProfilingManager manages the profiling team, not every implementation detail.
3.2 SourceManager AI
The SourceManager is the AI manager responsible for the Source Processing phase.

Its purpose is:
Authorized Candidate Sources
        ↓
SourceManager AI
        ↓
Source Processing Strategy
        ↓
SourceAgent tasks
        ↓
ParsedSourceResult[]
Responsibilities
The SourceManager may reason about:
- which Candidate Sources are available;
- which Candidate Sources still require processing;
- how many SourceAgent executions are required;
- which source should be assigned to which SourceAgent task;
- whether a failed source should be retried;
- whether partial Source Processing is sufficient;
- whether all authorized sources were attempted;
- whether the Source Processing phase is complete.
Example
Input:
CV
GitHub Repository
Thesis
The SourceManager may decide:
Three independent SourceAgent executions are required.
It requests:
SourceAgent #1 → CV
SourceAgent #2 → GitHub
SourceAgent #3 → Thesis
It then evaluates the returned execution results.
The SourceManager should not
- perform the detailed semantic extraction itself;
- fabricate source facts;
- perform candidate-wide evidence reasoning;
- create final Candidate Context conclusions.
Its role is:
Manage SOURCE → FACTS work
not perform all of that work itself.
3.3 EvidenceManager AI
The EvidenceManager manages the Evidence Processing phase.

Its input is primarily the structured output of Source Processing:
ParsedSourceResult[]
Its responsibility is to determine what evidence-processing work is required.
Responsibilities
The EvidenceManager may decide:
- which facts should be compared across sources;
- which evidence-processing tasks are required;
- whether claims need corroboration;
- whether apparent contradictions require further analysis;
- whether additional EvidenceAgent executions are useful;
- whether evidence coverage is sufficient;
- whether Evidence Processing is complete.
Conceptually:
ParsedSourceResult[]
        ↓
EvidenceManager AI
        ↓
EvidenceAgent task(s)
        ↓
Evidence Results
The EvidenceManager coordinates:
FACTS → EVIDENCE
It should not perform final candidate representation itself.
3.4 ProfileManager AI
The ProfileManager manages Candidate Representation.

Its input is validated candidate evidence.

Its responsibility is to organize the generation of the reusable Candidate Context.

Conceptually:
Evidence
    ↓
ProfileManager AI
    ↓
ProfileAgent task(s)
    ↓
Candidate Context
The ProfileManager may decide:
- which profile sections are required;
- whether evidence is sufficient for a profile claim;
- which parts of the Candidate Context require regeneration;
- whether limitations need explicit representation;
- whether profile construction is complete.
It coordinates:
EVIDENCE → CANDIDATE REPRESENTATION
4. Manager vs. Worker Agent
The architecture distinguishes between AI Managers and AI Worker Agents.
AI Manager
An AI Manager decides how work inside its responsibility should be organized.

Examples:
ProfilingManager
SourceManager
EvidenceManager
ProfileManager
Managers reason about:
- state;
- goals;
- work decomposition;
- assignment;
- completion;
- escalation;
- next actions.
AI Worker Agent
A Worker Agent performs a specialized semantic task.

Examples:
SourceAgent
EvidenceAgent
ProfileAgent
Worker Agents reason about the content of one assigned task.
Example
SourceManager AI
    ↓
"Process these three independent sources."
    ↓
SourceAgent #1 → CV
SourceAgent #2 → GitHub
SourceAgent #3 → Thesis
The manager coordinates.

The workers interpret.
5. ExecutionCoordinator
Responsibility
The ExecutionCoordinator is shared execution infrastructure.

It is not a profiling manager and does not need to be an AI agent.

AI managers request work; the coordinator turns those requests into controlled executions.

Example:
SourceManager AI
    ↓
requests 3 SOURCE_AGENT tasks
    ↓
ExecutionCoordinator
    ↓
executes and tracks those tasks
Responsibilities
The coordinator may:
- receive execution requests;
- create execution tasks;
- request agent instances from the AgentEngine;
- pass runtime input to an agent instance;
- execute tasks;
- collect outputs;
- preserve success and failure independently;
- enforce technical timeouts;
- record execution metadata;
- return results to the requesting AI manager.
Future responsibilities may include:
- parallel execution;
- deterministic retry limits;
- task persistence;
- execution metrics;
- cancellation;
- resource controls.
Important boundary
The coordinator does not decide the semantic strategy of Source Processing, Evidence Processing, or Profile Processing.

Those decisions belong to the AI managers.
6. AgentRegistry
Responsibility
The AgentRegistry defines which AI manager and worker agent types are allowed to exist.

Example:
Managers:
- PROFILING_MANAGER
- SOURCE_MANAGER
- EVIDENCE_MANAGER
- PROFILE_MANAGER

Workers:
- SOURCE_AGENT
- EVIDENCE_AGENT
- PROFILE_AGENT
Each registered type has an explicit definition.

A definition may contain:
agent type
role
purpose
identity
instructions
input contract
output contract
allowed tools
model configuration
execution limits
Example
SOURCE_AGENT

Purpose:
    Interpret exactly one Candidate Source.

Input:
    Candidate Source or Prepared Source

Output:
    ParsedSourceResult

Instructions:
    SourceAgent specifications

Tools:
    Explicitly allowed SourceAgent tools

Model:
    Configured profiling model
Why the registry exists
AI managers may request registered agent types.

They should not be able to invent unrestricted agents with arbitrary tools, models, permissions, and contracts.

Allowed:
SourceManager:
"Create 3 SOURCE_AGENT executions."
Not allowed:
SourceManager:
"Create an unrestricted agent with any tools it wants."
This preserves:
- control;
- testability;
- reproducibility;
- auditability;
- security.
7. AgentEngine
Responsibility
The AgentEngine creates concrete AI manager or worker agent instances from registered definitions.

It acts as the shared agent factory.

Example:
SOURCE_AGENT requested
        ↓
AgentEngine
        ↓
AgentRegistry
        ↓
SOURCE_AGENT definition
        ↓
AgentEngine creates instance
The AgentEngine may be responsible for:
- loading the registered definition;
- loading instructions;
- initializing the configured model;
- attaching allowed tools;
- applying execution limits;
- configuring structured output handling;
- injecting common runtime services;
- creating the executable instance.
Future cross-cutting functionality may include:
- tracing;
- token accounting;
- observability;
- model routing;
- agent versioning;
- runtime metadata.
Important boundary
The AgentEngine does not decide which work is needed.

AI managers make that decision.

The engine answers only:
How do I create the requested registered agent type?

8. Agent Definition vs. Agent Instance
Agent Definition
An Agent Definition describes what an AI role is.

Example:
SOURCE_AGENT
It may contain:
identity
instructions
tools
input contract
output contract
model configuration
execution limits
Agent Instance
An Agent Instance is one concrete runtime execution of that definition.

Example:
SourceAgent Instance #1 → CV
SourceAgent Instance #2 → GitHub
SourceAgent Instance #3 → Thesis
Therefore:
Agent Definition
        ≠
Agent Instance
One definition may produce many runtime instances.

The same principle applies to managers.

For example, SOURCE_MANAGER has one registered definition, while a profiling run may create one runtime SourceManager instance.
9. Complete Example: Three Candidate Sources
Assume the candidate has:
CV
GitHub Repository
Thesis
The workflow becomes:
ProfilingManager AI
        │
        │ decides:
        │ "Run Source Processing."
        ↓
SourceManager AI
        │
        │ reasons:
        │ "Three independent sources require processing."
        ↓
ExecutionCoordinator
        │
        ├── SOURCE_AGENT Task #1 → CV
        ├── SOURCE_AGENT Task #2 → GitHub
        └── SOURCE_AGENT Task #3 → Thesis
        ↓
AgentEngine
        ↓
AgentRegistry
        ↓
SOURCE_AGENT definition
        ↓
SourceAgent instances
        │
        ├── CV       → ParsedSourceResult #1
        ├── GitHub   → ParsedSourceResult #2
        └── Thesis   → ParsedSourceResult #3
        ↓
ExecutionCoordinator
        ↓
SourceManager AI
        │
        │ evaluates phase result
        ↓
ProfilingManager AI
The ProfilingManager may then decide:
Source Processing is complete.
Start Evidence Processing.
Then:
ProfilingManager AI
        ↓
EvidenceManager AI
        ↓
ExecutionCoordinator
        ↓
EvidenceAgent instance(s)
        ↓
Evidence Results
        ↓
EvidenceManager AI
        ↓
ProfilingManager AI
And later:
ProfilingManager AI
        ↓
ProfileManager AI
        ↓
ExecutionCoordinator
        ↓
ProfileAgent instance(s)
        ↓
Candidate Context
10. Full Target Workflow
Candidate Sources
        ↓
ProfilingManager AI
        ↓
SourceManager AI
        ↓
SourceAgent instances
        ↓
ParsedSourceResult[]
        ↓
ProfilingManager AI
        ↓
EvidenceManager AI
        ↓
EvidenceAgent instance(s)
        ↓
Evidence
        ↓
ProfilingManager AI
        ↓
ProfileManager AI
        ↓
ProfileAgent instance(s)
        ↓
Candidate Context
The managers form a hierarchy.

The worker agents remain specialized.
11. Tools
Tools belong to registered agent definitions.

Example:
SOURCE_AGENT
allowed_tools:
    ReadCandidateSource
or, if source preparation becomes deterministic:
SOURCE_AGENT
allowed_tools:
    none

input:
    PreparedSource
AI managers may request registered agent types but should not dynamically grant arbitrary tools.

The AgentRegistry defines the allowed tool boundary.

The AgentEngine attaches the tools.
12. Open Architecture Decision: Source Access
The exact Source Access boundary remains open.
Option A — Agent-Controlled Source Access
SourceAgent
    ↓
ReadCandidateSource
    ↓
DocumentReader / GitHubReader
    ↓
SourceAgent interprets content
The SourceAgent controls when source content is retrieved.
Advantages
- natural tool-calling behavior;
- flexible source exploration;
- simple agent-centric model.
Option B — Source Preparation Before Agent Execution
CandidateSource
    ↓
PrepareCandidateSource
    ↓
DocumentReader / GitHubReader
    ↓
PreparedSource
    ↓
SourceAgent
The SourceAgent receives prepared content.
Advantages
- deterministic retrieval;
- stronger separation of access and interpretation;
- easier technical testing;
- fewer AI responsibilities.
This decision should be made separately.
13. Architectural Principles
13.1 AI Management Is Intentional
Managers are AI agents because their responsibility includes reasoning about:
- workflow state;
- incomplete information;
- task decomposition;
- assignment;
- completion;
- escalation;
- next actions.
The system intentionally uses hierarchical AI management rather than only deterministic orchestration.
13.2 Deterministic Infrastructure Around AI Decisions
AI managers may decide what work is needed.

Deterministic infrastructure should enforce how execution is permitted.

Example:
SourceManager AI decides:
"Retry GitHub Source processing."

ExecutionCoordinator enforces:
maximum retry count,
timeout,
registered agent type,
allowed tools,
output validation.
This creates:
AI autonomy
+
engineering control
13.3 One Manager, One Phase Responsibility
ProfilingManager
→ overall profiling workflow

SourceManager
→ Source Processing

EvidenceManager
→ Evidence Processing

ProfileManager
→ Candidate Representation
A manager should not absorb the detailed responsibilities of another phase.
13.4 One Worker Agent, One Semantic Transformation
SourceAgent
→ SOURCE → FACTS

EvidenceAgent
→ FACTS → EVIDENCE

ProfileAgent
→ EVIDENCE → CANDIDATE REPRESENTATION
13.5 Explicit Contracts
Every manager and worker agent type should eventually define:
Input Contract
Output Contract
Allowed Tools
Instructions
Execution Limits
Outputs should be validated before downstream use.
13.6 Controlled Agent Creation
AI managers may request registered agent types.

They may decide:
number of agents
assignment
task objective
runtime input
They should not freely redefine:
agent permissions
tool access
core identity
output contract
security constraints
These remain governed by the AgentRegistry.
13.7 Independent Task Execution
Independent work should remain independently executable.

Example:
CV SourceAgent → success
GitHub SourceAgent → failure
Thesis SourceAgent → success
The GitHub failure must not erase the successful CV or Thesis results.

The relevant phase manager decides how to react to that partial result.
14. Responsibility Summary
Component	Type	Main Question	Responsibility
ProfilingManager	AI Manager	Which phase should run next?	Overall profiling orchestration
SourceManager	AI Manager	How should Source Processing be organized?	Source phase management
EvidenceManager	AI Manager	How should Evidence Processing be organized?	Evidence phase management
ProfileManager	AI Manager	How should Candidate Context construction be organized?	Profile phase management
ExecutionCoordinator	Infrastructure	How is requested work executed safely?	Task execution and result collection
AgentRegistry	Infrastructure	Which agent types are allowed?	Agent definitions and governance
AgentEngine	Infrastructure	How is an agent instance created?	Agent construction
Worker Agent	AI Agent	How is this semantic task solved?	Specialized AI execution


15. Target Principle
The architecture should maintain this separation:
Global AI orchestration
        ↓
ProfilingManager AI

Phase-level AI management
        ↓
SourceManager / EvidenceManager / ProfileManager

Controlled execution
        ↓
ExecutionCoordinator

Agent governance
        ↓
AgentRegistry

Agent construction
        ↓
AgentEngine

Semantic task execution
        ↓
Worker Agent Instance
The intended result is a hierarchical AI team that remains:
- autonomous where reasoning is valuable;
- controlled where engineering guarantees are required;
- modular;
- testable;
- observable;
- reproducible;
- scalable;
- extensible.