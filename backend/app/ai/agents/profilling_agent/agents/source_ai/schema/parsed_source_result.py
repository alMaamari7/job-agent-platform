from enum import Enum

from huggingface_hub import Agent
from pydantic import BaseModel, Field

from app.ai.agents.profilling_agent.schema.execution_request import AgentType


class FactContext(BaseModel):
    type: str = Field(
        ...,
        description=(
            "The context category in which the fact occurred, "
            "for example PROFESSIONAL_EMPLOYMENT, PERSONAL_PROJECT, "
            "ACADEMIC_PROJECT, THESIS, or CERTIFICATION."
        ),
    )

    organization: str | None = Field(
        default=None,
        description=(
            "Organization, company, institution, or other entity "
            "associated with the fact."
        ),
    )

    role: str | None = Field(
        default=None,
        description=(
            "Candidate's role or position within the context "
            "in which the fact occurred."
        ),
    )

    project: str | None = Field(
        default=None,
        description=(
            "Name or description of the project associated with the fact."
        ),
    )

    start_date: str | None = Field(
        default=None,
        description=(
            "Start date of the context when explicitly supported "
            "by the source."
        ),
    )

    end_date: str | None = Field(
        default=None,
        description=(
            "End date of the context when explicitly supported "
            "by the source."
        ),
    )


class CandidateContribution(BaseModel):
    level: str = Field(
        ...,
        description=(
            "Required contribution level when a CandidateContribution "
            "object exists. Must never be null. "
            "If no candidate-specific contribution is supported by "
            "the source, SourceFact.contribution must be null instead."
        ),
    )

    description: str | None = Field(
        default=None,
        description=(
            "Source-supported description of what the candidate "
            "personally contributed."
        ),
    )

class SourceLocator(BaseModel):
    kind: str = Field(
        ...,
        description=(
            "Type of locator used to identify where the information "
            "was found within the source, such as page, section, "
            "file, path, repository location, or document heading."
        ),
    )

    value: str = Field(
        ...,
        description=(
            "Concrete locator value identifying where the supporting "
            "information can be found in the source."
        ),
    )


class SourceUncertainty(BaseModel):
    type: str = Field(
        ...,
        description=(
            "Category of uncertainty identified while interpreting "
            "the source."
        ),
    )

    description: str = Field(
        ...,
        description=(
            "Explanation of what is uncertain, ambiguous, incomplete, "
            "or unsupported within the source."
        ),
    )

    source_locator: SourceLocator | None = Field(
        default=None,
        description=(
            "Optional location within the source associated with "
            "the identified uncertainty."
        ),
    )


class SourceFact(BaseModel):
    fact_id: str = Field(
        ...,
        description=(
            "Unique identifier of this fact within the ParsedSourceResult."
        ),
    )

    statement: str = Field(
        ...,
        description=(
            "Source-supported factual statement about the candidate, "
            "preserving the meaning and level of certainty of the source."
        ),
    )

    fact_type: str = Field(
        ...,
        description=(
            "Semantic category of the fact, used to distinguish "
            "different types of source-level information."
        ),
    )

    context: FactContext | None = Field(
        default=None,
        description=(
            "Context in which the fact occurred, such as employment, "
            "project, academic work, research, or certification."
        ),
    )

    contribution: CandidateContribution | None = Field(
        default=None,
        description=(
            "Candidate's specific contribution associated with the fact. "
            "Use null when the source does not support a specific "
            "candidate contribution. Never create a CandidateContribution "
            "object with level=null."
        ),
    )
    methods: list[str] = Field(
        default_factory=list,
        description=(
            "Methods, techniques, approaches, or processes explicitly "
            "associated with the fact."
        ),
    )

    tools_or_resources: list[str] = Field(
        default_factory=list,
        description=(
            "Tools, technologies, platforms, frameworks, resources, "
            "or systems explicitly associated with the fact."
        ),
    )

    stakeholders: list[str] = Field(
        default_factory=list,
        description=(
            "People, teams, customers, organizations, or other "
            "stakeholders associated with the fact."
        ),
    )

    outcomes: list[str] = Field(
        default_factory=list,
        description=(
            "Source-supported results, outputs, achievements, "
            "or consequences associated with the fact."
        ),
    )

    source_locator: SourceLocator | None = Field(
        default=None,
        description=(
            "Location within the original source that supports this fact."
        ),
    )




class ParsedSourceResult(BaseModel):



    source_id: str = Field(
        ...,
        description=(
            "Unique identifier of the CandidateSource from which "
            "this result was produced."
        ),
    )

    source_type: str = Field(
        ...,
        description=(
            "Type of CandidateSource that was processed, "
            "for example file or github."
        ),
    )

    status: str = Field(
        ...,
        description=(
            "Semantic processing status of the source itself, "
            "for example PARSED, PARTIALLY_PARSED, UNAVAILABLE, "
            "UNSUPPORTED_FORMAT, or FAILED_TO_PARSE."
        ),
    )

    facts: list[SourceFact] = Field(
        default_factory=list,
        description=(
            "Source-level facts extracted from this CandidateSource. "
            "Each fact must remain traceable to this source and preserve "
            "its original context and candidate contribution."
        ),
    )

    uncertainties: list[SourceUncertainty] = Field(
        default_factory=list,
        description=(
            "Uncertainties, ambiguities, missing information, or "
            "interpretation limitations identified while processing "
            "the source."
        ),
    )

    processing_notes: list[str] | None = Field(
        default=None,
        description=(
            "Optional processing notes describing relevant technical "
            "or semantic observations from the SourceAgent execution."
        ),
    )