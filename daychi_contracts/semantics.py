"""Daychi wire contract v1; synchronized by scripts/sync_daychi_contracts.py."""
import json
import re
from typing import Literal
from urllib.parse import parse_qs, urlsplit
from pydantic import BaseModel, ConfigDict, Field, model_validator

def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(',', ':'))


def folded(value):
    return ' '.join(value.casefold().replace('ё', 'е').split())


class StrictModel(BaseModel):
    model_config = ConfigDict(extra='forbid', allow_inf_nan=False)


class Quote(StrictModel):
    text: str = Field(min_length=10, max_length=1500)
    start_seconds: float = Field(ge=0, le=100000)
    end_seconds: float = Field(gt=0, le=100000)

    @model_validator(mode='after')
    def valid_interval(self):
        if self.end_seconds <= self.start_seconds:
            raise ValueError('Invalid evidence interval')
        return self


class SemanticLink(StrictModel):
    resource_id: str = Field(pattern=r'^[A-Za-z0-9_-]{11}$')
    expected_title: str = Field(min_length=1, max_length=1000)
    source_revision: int = Field(ge=1, le=100000)
    transcript_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    subtitles_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    relation: Literal['discusses', 'explains', 'practices']
    rationale: str = Field(min_length=20, max_length=1000)
    points: list[Quote] = Field(min_length=1, max_length=3)


class Claim(StrictModel):
    text: str = Field(min_length=20, max_length=1000)
    evidence_indexes: list[int] = Field(min_length=1, max_length=30)


class SemanticPage(StrictModel):
    concept_id: str = Field(pattern=r'^[a-z][a-z0-9-]{1,79}$')
    kind: Literal['term', 'topic']
    title: str = Field(min_length=2, max_length=200)
    aliases: list[str] = Field(default_factory=list, max_length=12)
    revision: int = Field(ge=1, le=100000)
    status: Literal['source_checked_draft'] = 'source_checked_draft'
    claims: list[Claim] = Field(min_length=1, max_length=4)
    links: list[SemanticLink] = Field(min_length=1, max_length=30)

    @model_validator(mode='after')
    def evidence_complete(self):
        labels = [self.title, *self.aliases]
        if any(not 2 <= len(a.strip()) <= 200 for a in labels):
            raise ValueError('Invalid concept label')
        if len({folded(a) for a in labels}) != len(labels):
            raise ValueError('Duplicate concept alias')
        if len({l.resource_id for l in self.links}) != len(self.links):
            raise ValueError('Duplicate material link')
        referenced = set()
        for claim in self.claims:
            indexes = claim.evidence_indexes
            if len(set(indexes)) != len(indexes) or any(i < 0 or i >= len(self.links) for i in indexes):
                raise ValueError('Claim has invalid evidence')
            referenced.update(indexes)
        if referenced != set(range(len(self.links))):
            raise ValueError('Every relation must support a page claim')
        for link in self.links:
            if len({canonical(p.model_dump()) for p in link.points}) != len(link.points):
                raise ValueError('Duplicate quotation')
        return self


class Review(StrictModel):
    editor: str = Field(min_length=1, max_length=80)
    reviewer: str = Field(min_length=1, max_length=80)
    editorial_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    review_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    verdict: Literal['pass']
    full_text_read: Literal[True]

    @model_validator(mode='after')
    def independent(self):
        if folded(self.editor) == folded(self.reviewer):
            raise ValueError('A separate reviewer is required')
        return self


class SemanticBatch(StrictModel):
    batch_id: str = Field(pattern=r'^[a-zA-Z0-9_-]{1,80}$')
    pages: list[SemanticPage] = Field(min_length=1, max_length=100)
    review: Review

    @model_validator(mode='after')
    def unique_pages(self):
        if len({p.concept_id for p in self.pages}) != len(self.pages):
            raise ValueError('Duplicate concept ID')
        if sum(len(p.links) for p in self.pages) > 200:
            raise ValueError('Too many relations in one batch')
        return self
