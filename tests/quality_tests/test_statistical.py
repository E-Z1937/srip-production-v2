"""Statistical Quality Tests - NO APIs needed!"""
import pytest
import textstat
from src.orchestration.workflow import IntelligenceWorkflow

class StatisticalMetrics:
    @staticmethod
    def readability_score(text: str) -> dict:
        return {
            "flesch_reading_ease": textstat.flesch_reading_ease(text),
            "grade_level": textstat.flesch_kincaid_grade(text),
            "word_count": len(text.split())
        }
    
    @staticmethod
    def structure_score(text: str) -> dict:
        lines = [l for l in text.split('\n') if l.strip()]
        sections = len([l for l in lines if l.strip().startswith(('##', '**', '-', '1.', '2.'))])
        return {
            "total_lines": len(lines),
            "sections": sections,
            "has_structure": sections >= 3
        }

@pytest.fixture
def workflow():
    return IntelligenceWorkflow()

@pytest.fixture
def metrics():
    return StatisticalMetrics()

@pytest.mark.asyncio
async def test_readability(workflow, metrics):
    query = "Cloud computing market analysis"
    result = await workflow.execute_analysis(query=query)
    
    readability = metrics.readability_score(result.market_intelligence)
    
    print(f"\n📊 Readability:")
    print(f"  Reading Ease: {readability['flesch_reading_ease']:.1f}")
    print(f"  Grade Level: {readability['grade_level']:.1f}")
    print(f"  Word Count: {readability['word_count']}")
    
    assert 30 <= readability['flesch_reading_ease'] <= 100
    assert readability['grade_level'] <= 16

@pytest.mark.asyncio
async def test_completeness(workflow):
    query = "AI chip market analysis"
    result = await workflow.execute_analysis(query=query)
    
    print(f"\n✅ Completeness:")
    print(f"  All agents: {all(result.completion_status.values())}")
    print(f"  Quality: {result.quality_score:.2%}")
    print(f"  Recommendations: {len(result.strategic_actions)}")
    
    assert all(result.completion_status.values())
    assert result.quality_score >= 0.7
    assert len(result.strategic_actions) >= 6
    assert len(result.executive_briefing) > 200
