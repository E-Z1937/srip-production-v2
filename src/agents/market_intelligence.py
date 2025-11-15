"""Market Intelligence Agent"""
import logging
from typing import List, Optional
from src.agents.base_agent import BaseAgent

logger = logging.getLogger(__name__)

class MarketIntelligenceAgent(BaseAgent):
    def __init__(self):
        super().__init__(agent_name="MarketIntelligence")
    
    def _analyze(self, query: str, context: Optional[str] = None, targets: Optional[List[str]] = None) -> str:
        target_context = f" focusing on {', '.join(targets)}" if targets else ""
        
        prompt = f"""Conduct comprehensive market intelligence analysis for: {query}{target_context}

Deliver structured analysis:

**MARKET SCALE AND TRAJECTORY**
- Current market size with estimates
- Historical growth rates (3-5 years)
- Projected growth (CAGR) for next 3-5 years
- Key growth drivers

**DOMINANT INDUSTRY PATTERNS**
- Three most significant current trends
- Technology adoption patterns
- Consumer behavior shifts

**STRATEGIC MARKET OPPORTUNITIES**
- High-potential growth segments
- Underserved market niches
- Emerging customer needs

**MARKET STRUCTURE ANALYSIS**
- Competitive intensity
- Entry and exit barriers
- Supply chain dynamics

**FORWARD-LOOKING ASSESSMENT**
- 12-18 month market outlook
- Potential disruptions
- Strategic implications

Provide specific, quantified insights."""

        messages = [
            {"role": "system", "content": "You are a senior market research analyst with 15+ years experience. Provide data-driven analysis."},
            {"role": "user", "content": prompt}
        ]
        return self._execute_with_retry(messages, max_tokens=1200)
