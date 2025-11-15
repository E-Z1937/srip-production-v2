"""Competitive Intelligence Agent"""
import logging
from typing import List, Optional
from src.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class CompetitiveIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="CompetitiveIntelligence")
    
    def _analyze(self, query: str, context: Optional[str] = None, targets: Optional[List[str]] = None) -> str:
        target_list = targets if targets else []
        target_context = f" with focus on {', '.join(target_list)}" if target_list else ""
        
        prompt = f"""Conduct competitive intelligence analysis for: {query}{target_context}

Market context: {context if context else "General analysis"}

Deliver structured analysis:

**COMPETITIVE LANDSCAPE OVERVIEW**
- Market share distribution
- Competitive positioning matrix
- Market concentration

**DETAILED COMPETITOR PROFILES**
- Strategic positioning and value proposition
- Key competitive advantages
- Notable weaknesses
- Recent strategic moves

**COMPETITIVE DYNAMICS**
- Intensity of rivalry
- Differentiation strategies
- Areas of direct competition
- Emerging competitive threats

**STRATEGIC IMPLICATIONS**
- Windows of opportunity
- Defensive strategies
- Potential partnerships

Provide specific, evidence-based insights."""

        messages = [
            {"role": "system", "content": "You are a competitive intelligence specialist. Provide specific, actionable insights."},
            {"role": "user", "content": prompt}
        ]
        return self._execute_with_retry(messages, max_tokens=1000)
