from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class TradeTest:
    id: str
    application_id: str
    test_type: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    location: Optional[str] = None
    assessor_name: Optional[str] = None
    technical_knowledge_score: Optional[int] = None
    trade_skills_score: Optional[int] = None
    safety_awareness_score: Optional[int] = None
    tool_handling_score: Optional[int] = None
    communication_score: Optional[int] = None
    problem_solving_score: Optional[int] = None
    teamwork_score: Optional[int] = None
    total_score: Optional[int] = None
    result: str = "Pending"
    status: str = "Scheduled"
    assessment_notes: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
