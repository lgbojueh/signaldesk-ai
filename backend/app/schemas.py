from datetime import datetime
from pydantic import BaseModel, Field


class TicketCreate(BaseModel):
    title: str = Field(min_length=3, max_length=160)
    description: str = Field(min_length=12, max_length=5000)


class SourceCitation(BaseModel):
    id: str
    title: str
    excerpt: str
    score: float


class TicketAnalysis(BaseModel):
    id: int
    title: str
    category: str
    severity: str
    confidence: str
    escalation: bool
    summary: str
    steps: list[str]
    sources: list[SourceCitation]
    created_at: datetime


class TicketListItem(BaseModel):
    id: int
    title: str
    category: str
    severity: str
    confidence: str
    escalation: bool
    created_at: datetime
