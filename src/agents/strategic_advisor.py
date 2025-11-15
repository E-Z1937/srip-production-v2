"""Strategic Advisor Agent"""
import logging
import re
from typing import List, Optional, Tuple
from src.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class StrategicAdvisorAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="StrategicAdvisor")
    
    def _analyze(self, query: str, context: Optional[str] = None, 
                 market_intelligence: Optional[str] = None,
                 competitive_landscape: Optional[str] = None,
                 risk_evaluation: Optional[str] = None) -> Tuple[str, List[str]]:
        
        full_context = f"""
MARKET: {market_intelligence if market_intelligence else "N/A"}
COMPETITIVE: {competitive_landscape if competitive_landscape else "N/A"}
RISK: {risk_evaluation if risk_evaluation else "N/A"}
"""
        
        prompt = f"""Based on comprehensive analysis for: {query}

{full_context}

Generate strategic synthesis:

**EXECUTIVE SUMMARY** (200-300 words):
Synthesize key findings across all analyses.

**STRATEGIC RECOMMENDATIONS** (minimum 6, maximum 8):
1. [CLEAR STRATEGY]: Brief rationale and impact
2. [CLEAR STRATEGY]: Brief rationale and impact
...

Each recommendation must be:
- Specific and actionable
- Grounded in analysis
- Include implementation guidance
- 30-200 characters

Focus on opportunities, positioning, and risk mitigation."""

        messages = [
            {"role": "system", "content": "You are a senior strategy consultant synthesizing business intelligence."},
            {"role": "user", "content": prompt}
        ]
        
        result = self._execute_with_retry(messages, max_tokens=1000, temperature=0.15)
        recommendations = self._parse_recommendations(result)
        return result, recommendations
    
    def _parse_recommendations(self, text: str) -> List[str]:
        recommendations = []
        for line in text.split('\n'):
            line = line.strip()
            match = re.match(r'^(\d+)[\.\)]\s*(.+)', line)
            if match:
                rec_text = match.group(2).strip()
                if ':' in rec_text:
                    rec_text = rec_text.split(':')[0].strip()
                if 30 <= len(rec_text) <= 200:
                    recommendations.append(rec_text)
        return recommendations[:8]
