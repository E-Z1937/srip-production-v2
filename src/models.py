"""Data models"""
from datetime import datetime
from enum import Enum
from typing import Optional, List, Dict
from pydantic import BaseModel, Field


class AnalysisStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class AnalysisRequest(BaseModel):
    query: str = Field(min_length=10, max_length=1000)
    targets: Optional[List[str]] = Field(default=None, max_length=8)
    priority: str = Field(default="normal", pattern="^(low|normal|high)$")


class IntelligenceState(BaseModel):
    analysis_id: str
    query: str
    targets: Optional[List[str]] = None
    
    market_intelligence: Optional[str] = None
    competitive_landscape: Optional[str] = None
    risk_evaluation: Optional[str] = None
    strategic_actions: Optional[List[str]] = None
    executive_briefing: Optional[str] = None
    
    status: AnalysisStatus = AnalysisStatus.PENDING
    processing_duration: float = 0.0
    quality_score: float = 0.0
    completion_status: Dict[str, bool] = Field(default_factory=dict)
    errors: List[str] = Field(default_factory=list)
    
    created_at: datetime = Field(default_factory=datetime.utcnow)


class AnalysisResponse(BaseModel):
    analysis_id: str
    status: AnalysisStatus
    query: str
    targets: Optional[List[str]] = None
    
    market_intelligence: Optional[str] = None
    competitive_landscape: Optional[str] = None
    risk_evaluation: Optional[str] = None
    strategic_recommendations: Optional[List[str]] = None
    executive_summary: Optional[str] = None
    
    quality_score: float
    completeness: Dict[str, bool]
    processing_time: float
    created_at: datetime
    errors: Optional[List[str]] = None
