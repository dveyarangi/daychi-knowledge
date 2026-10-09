"""Daychi wire contract v1; synchronized by scripts/sync_daychi_contracts.py."""
import json
import re
from typing import Literal
from urllib.parse import parse_qs, urlsplit
from pydantic import BaseModel, ConfigDict, Field, model_validator

def youtube_id(url):
    u = urlsplit(url)
    host = (u.hostname or '').lower()
    value = u.path.strip('/') if host == 'youtu.be' else (
        parse_qs(u.query).get('v', [''])[0] if host in ('youtube.com','www.youtube.com','m.youtube.com') else '')
    return value if re.fullmatch(r'[A-Za-z0-9_-]{11}', value) else None


class Point(BaseModel):
    text: str = Field(min_length=10, max_length=1500)
    start_seconds: float = Field(ge=0, le=100000)
    end_seconds: float = Field(gt=0, le=100000)


class Enrichment(BaseModel):
    resource_id: str = Field(pattern=r'^[A-Za-z0-9_-]{11}$')
    expected_title: str = Field(min_length=1, max_length=1000)
    revision: int = Field(ge=1, le=100000)
    summary: str = Field(min_length=30, max_length=3000)
    points: list[Point] = Field(min_length=2, max_length=8)
    transcript_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    subtitles_sha256: str = Field(pattern=r'^[0-9a-f]{64}$')
    status: str = Field(default='source_checked_draft', pattern=r'^source_checked_draft$')


class Batch(BaseModel):
    batch_id: str = Field(pattern=r'^[a-zA-Z0-9_-]{1,80}$')
    records: list[Enrichment] = Field(min_length=1, max_length=100)
