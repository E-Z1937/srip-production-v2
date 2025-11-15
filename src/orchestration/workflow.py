"""Workflow orchestration with LangGraph"""
import logging
import time
import uuid
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from src.models import IntelligenceState, AnalysisStatus
from src.agents.market_intelligence import MarketIntelligenceAgent
from src.agents.competitive_intelligence import CompetitiveIntelligenceAgent
from src.agents.risk_assessment import RiskAssessmentAgent
from src.agents.strategic_advisor import StrategicAdvisorAgent
from src.security.guardrails import ContentGuardrails
from src.config import settings

logger = logging.getLogger(__name__)

class IntelligenceWorkflow:
    def __init__(self):
        self.market_agent = MarketIntelligenceAgent()
        self.competitive_agent = CompetitiveIntelligenceAgent()
        self.risk_agent = RiskAssessmentAgent()
        self.strategic_agent = StrategicAdvisorAgent()
        if settings.ENABLE_GUARDRAILS:
            self.guardrails = ContentGuardrails(strict_mode=True)
        self.workflow = self._build_workflow()
        logger.info("Workflow initialized")
    
    def _build_workflow(self) -> StateGraph:
        workflow = StateGraph(dict)
        workflow.add_node("market_analysis", self._market_node)
        workflow.add_node("competitive_analysis", self._competitive_node)
        workflow.add_node("risk_assessment", self._risk_node)
        workflow.add_node("strategic_planning", self._strategic_node)
        workflow.set_entry_point("market_analysis")
        workflow.add_edge("market_analysis", "competitive_analysis")
        workflow.add_edge("competitive_analysis", "risk_assessment")
        workflow.add_edge("risk_assessment", "strategic_planning")
        workflow.add_edge("strategic_planning", END)
        return workflow.compile()
    
    def _market_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info(f"Market analysis: {state['query']}")
            result = self.market_agent.execute(query=state['query'], targets=state.get('targets'))
            state['market_intelligence'] = result
            state['completion_status']['market'] = True
        except Exception as e:
            logger.error(f"Market failed: {e}")
            state['errors'].append(f"Market: {str(e)}")
            state['completion_status']['market'] = False
        return state
    
    def _competitive_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result = self.competitive_agent.execute(
                query=state['query'], context=state.get('market_intelligence'), targets=state.get('targets'))
            state['competitive_landscape'] = result
            state['completion_status']['competitive'] = True
        except Exception as e:
            logger.error(f"Competitive failed: {e}")
            state['errors'].append(f"Competitive: {str(e)}")
            state['completion_status']['competitive'] = False
        return state
    
    def _risk_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            context = f"Market: {state.get('market_intelligence', 'N/A')}\nCompetitive: {state.get('competitive_landscape', 'N/A')}"
            result = self.risk_agent.execute(query=state['query'], context=context)
            state['risk_evaluation'] = result
            state['completion_status']['risk'] = True
        except Exception as e:
            logger.error(f"Risk failed: {e}")
            state['errors'].append(f"Risk: {str(e)}")
            state['completion_status']['risk'] = False
        return state
    
    def _strategic_node(self, state: Dict[str, Any]) -> Dict[str, Any]:
        try:
            result, recommendations = self.strategic_agent._analyze(
                query=state['query'], market_intelligence=state.get('market_intelligence'),
                competitive_landscape=state.get('competitive_landscape'), risk_evaluation=state.get('risk_evaluation'))
            state['executive_briefing'] = result
            state['strategic_actions'] = recommendations
            state['completion_status']['strategic'] = True
        except Exception as e:
            logger.error(f"Strategic failed: {e}")
            state['errors'].append(f"Strategic: {str(e)}")
            state['completion_status']['strategic'] = False
        return state
    
    async def execute_analysis(self, query: str, targets: list[str] | None = None) -> IntelligenceState:
        analysis_id = f"ana_{uuid.uuid4().hex[:12]}"
        start_time = time.time()
        initial_state = {
            "analysis_id": analysis_id, "query": query, "targets": targets,
            "market_intelligence": None, "competitive_landscape": None, "risk_evaluation": None,
            "strategic_actions": None, "executive_briefing": None, "status": AnalysisStatus.PROCESSING,
            "processing_duration": 0.0, "quality_score": 0.0,
            "completion_status": {"market": False, "competitive": False, "risk": False, "strategic": False},
            "errors": []
        }
        
        try:
            final_state = self.workflow.invoke(initial_state)
            duration = time.time() - start_time
            quality_score = self._calculate_quality(final_state)
            final_state['processing_duration'] = duration
            final_state['quality_score'] = quality_score
            final_state['status'] = AnalysisStatus.COMPLETED if quality_score >= 0.7 else AnalysisStatus.FAILED
            
            if settings.ENABLE_GUARDRAILS and final_state['status'] == AnalysisStatus.COMPLETED:
                is_safe = self._validate_with_guardrails(final_state)
                if not is_safe:
                    final_state['status'] = AnalysisStatus.FAILED
                    final_state['errors'].append("Content safety violations")
            
            return IntelligenceState(**final_state)
        except Exception as e:
            duration = time.time() - start_time
            initial_state['status'] = AnalysisStatus.FAILED
            initial_state['processing_duration'] = duration
            initial_state['errors'].append(f"Workflow error: {str(e)}")
            return IntelligenceState(**initial_state)
    
    def _calculate_quality(self, state: Dict[str, Any]) -> float:
        score = 0.0
        completion_rate = sum(state['completion_status'].values()) / len(state['completion_status'])
        score += completion_rate * 0.6
        recommendations = state.get('strategic_actions', [])
        if len(recommendations) >= 6:
            score += 0.125
        if len(state.get('executive_briefing', '')) > 300:
            score += 0.125
        if 0 < state['processing_duration'] <= 60:
            score += 0.15
        elif state['processing_duration'] <= 120:
            score += 0.075
        return min(score, 1.0)
    
    def _validate_with_guardrails(self, state: Dict[str, Any]) -> bool:
        all_safe = True
        for field, content in [
            ("market_intelligence", state.get("market_intelligence")),
            ("competitive_landscape", state.get("competitive_landscape")),
            ("risk_evaluation", state.get("risk_evaluation")),
            ("executive_briefing", state.get("executive_briefing"))
        ]:
            if content:
                is_safe, violations = self.guardrails.validate_content(content, field)
                if not is_safe:
                    all_safe = False
        return all_safe
