"""Quality Testing Using FREE Groq API as LLM Judge"""
import pytest
import os
import json
from datetime import datetime
from pathlib import Path
from groq import Groq
from src.orchestration.workflow import IntelligenceWorkflow

OUTPUT_DIR = Path("outputs/test_results")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

class GroqJudge:
    def __init__(self):
        self.client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        self.model = "llama-3.1-70b-versatile"
    
    def evaluate_relevancy(self, query: str, output: str, threshold: float = 0.7) -> dict:
        prompt = f"""Rate relevancy (0.0-1.0):

QUERY: {query}
OUTPUT: {output[:500]}...

Respond ONLY with JSON:
{{"score": 0.85, "passed": true, "reason": "Brief explanation"}}"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model, messages=[{"role": "user", "content": prompt}],
                temperature=0.1, max_tokens=200
            )
            import re
            content = response.choices[0].message.content
            json_match = re.search(r'\{[^}]+\}', content)
            if json_match:
                result = json.loads(json_match.group())
                result['passed'] = result.get('score', 0) >= threshold
                return result
        except Exception as e:
            print(f"Judge error: {e}")
        return {"score": 0.0, "passed": False, "reason": "Evaluation failed"}

def save_result(test_name: str, data: dict):
    file = OUTPUT_DIR / f"{test_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(file, 'w') as f:
        json.dump(data, f, indent=2)
    print(f"✅ Saved: {file.name}")

@pytest.fixture
def workflow():
    return IntelligenceWorkflow()

@pytest.fixture
def judge():
    return GroqJudge()

@pytest.mark.asyncio
async def test_market_intelligence_relevancy(workflow, judge):
    query = "Strategic analysis of cloud computing infrastructure market"
    targets = ["AWS", "Microsoft Azure", "Google Cloud"]
    
    print(f"\n🔍 Testing: {query}")
    result = await workflow.execute_analysis(query=query, targets=targets)
    
    evaluation = judge.evaluate_relevancy(query, result.market_intelligence, threshold=0.7)
    
    result_data = {
        "test": "market_relevancy",
        "query": query,
        "evaluation": evaluation,
        "quality_score": result.quality_score,
        "processing_time": result.processing_duration,
        "timestamp": datetime.utcnow().isoformat()
    }
    save_result("market_relevancy", result_data)
    
    status = "✅ PASSED" if evaluation['passed'] else "❌ FAILED"
    print(f"{status} - Score: {evaluation['score']:.4f}")
    print(f"Reason: {evaluation['reason']}")
    
    assert evaluation['passed'], f"Failed: {evaluation['reason']}"

@pytest.mark.asyncio
async def test_strategic_quality(workflow, judge):
    query = "AI chip market competitive dynamics"
    targets = ["NVIDIA", "AMD", "Intel"]
    
    result = await workflow.execute_analysis(query=query, targets=targets)
    
    prompt = f"""Rate strategic recommendations quality (0.0-1.0):

RECOMMENDATIONS:
{chr(10).join(result.strategic_actions)}

Criteria: Specific, actionable, grounded in analysis, addresses risks

JSON only: {{"score": 0.85, "passed": true, "reason": "Brief explanation"}}"""
    
    try:
        response = judge.client.chat.completions.create(
            model=judge.model, messages=[{"role": "user", "content": prompt}],
            temperature=0.1, max_tokens=200
        )
        import re
        json_match = re.search(r'\{[^}]+\}', response.choices[0].message.content)
        if json_match:
            evaluation = json.loads(json_match.group())
            evaluation['passed'] = evaluation.get('score', 0) >= 0.7
    except:
        evaluation = {"score": 0.0, "passed": False, "reason": "Failed"}
    
    result_data = {
        "test": "strategic_quality",
        "query": query,
        "evaluation": evaluation,
        "recommendations_count": len(result.strategic_actions),
        "timestamp": datetime.utcnow().isoformat()
    }
    save_result("strategic_quality", result_data)
    
    assert evaluation['passed']
    assert len(result.strategic_actions) >= 6
