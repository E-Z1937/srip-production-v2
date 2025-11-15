"""Risk Assessment Agent"""
import logging
from typing import Optional
from src.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class RiskAssessmentAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="RiskAssessment")
    
    def _analyze(self, query: str, context: Optional[str] = None, **kwargs) -> str:
        prompt = f"""Conduct comprehensive risk assessment for: {query}

Context: {context if context else "General business context"}

Provide structured risk evaluation with QUANTIFIED scores:

**MARKET AND ECONOMIC RISKS**
- Risk Level: [High/Medium/Low] (Score: X/10)
- Key vulnerabilities
- Mitigation strategies

**COMPETITIVE AND STRATEGIC RISKS**
- Risk Level: [High/Medium/Low] (Score: X/10)
- Competitive threats
- Defensive strategies

**TECHNOLOGY AND INNOVATION RISKS**
- Risk Level: [High/Medium/Low] (Score: X/10)
- Disruption threats
- Adaptation strategies

**REGULATORY AND OPERATIONAL RISKS**
- Risk Level: [High/Medium/Low] (Score: X/10)
- Compliance challenges
- Mitigation frameworks

**INTEGRATED RISK PROFILE**
- Overall Risk Score: X/10
- Top 3 Priority Risks
- Strategic Risk Management Recommendations

Provide actionable mitigation strategies."""

        messages = [
            {"role": "system", "content": "You are a senior risk management consultant. Provide quantified risk scores (1-10 scale)."},
            {"role": "user", "content": prompt}
        ]
        return self._execute_with_retry(messages, max_tokens=900)
