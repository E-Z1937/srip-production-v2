"""Professional Gradio Interface"""
import gradio as gr
import plotly.graph_objects as go
from datetime import datetime
import asyncio
from src.orchestration.workflow import IntelligenceWorkflow
from src.models import AnalysisStatus

class SRIPInterface:
    def __init__(self):
        self.workflow = IntelligenceWorkflow()
    
    async def analyze_business(self, query: str, targets: str, priority: str, progress=gr.Progress()):
        if not query or len(query) < 10:
            return "❌ Error: Query must be at least 10 characters", None, None
        
        target_list = None
        if targets and targets.strip():
            target_list = [t.strip() for t in targets.split(",") if t.strip()]
            if len(target_list) > 8:
                return "❌ Error: Maximum 8 targets allowed", None, None
        
        progress(0.1, desc="🔍 Validating...")
        await asyncio.sleep(0.5)
        progress(0.2, desc="📊 Market intelligence...")
        
        try:
            result = await self.workflow.execute_analysis(query=query, targets=target_list)
            progress(0.9, desc="✅ Finalizing...")
            quality_chart = self._create_quality_gauge(result)
            completion_chart = self._create_completion_chart(result)
            output = self._format_output(result)
            return output, quality_chart, completion_chart
        except Exception as e:
            return f"❌ Analysis failed: {str(e)}", None, None
    
    def _format_output(self, result) -> str:
        status_emoji = "✅" if result.status == AnalysisStatus.COMPLETED else "❌"
        quality_emoji = "🌟" if result.quality_score >= 0.9 else "⭐" if result.quality_score >= 0.7 else "⚠️"
        
        output = f"""# {status_emoji} Intelligence Analysis Report

**Analysis ID:** `{result.analysis_id}`  
**Status:** {result.status.value.upper()}  
**Quality Score:** {result.quality_score:.1%} {quality_emoji}  
**Processing Time:** {result.processing_duration:.2f}s  
**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

---

## 📊 Market Intelligence

{result.market_intelligence or "*No data*"}

---

## 🎯 Competitive Landscape

{result.competitive_landscape or "*No data*"}

---

## ⚠️ Risk Assessment

{result.risk_evaluation or "*No data*"}

---

## 💡 Strategic Recommendations

"""
        if result.strategic_actions:
            for i, rec in enumerate(result.strategic_actions, 1):
                output += f"{i}. **{rec}**\n"
        else:
            output += "*No recommendations*\n"
        
        output += f"""
---

## 📝 Executive Summary

{result.executive_briefing or "*No summary*"}

---

### 📈 Analysis Metrics

| Metric | Status |
|--------|--------|
| Market Intelligence | {'✅ Complete' if result.completion_status.get('market') else '❌ Incomplete'} |
| Competitive Analysis | {'✅ Complete' if result.completion_status.get('competitive') else '❌ Incomplete'} |
| Risk Assessment | {'✅ Complete' if result.completion_status.get('risk') else '❌ Incomplete'} |
| Strategic Planning | {'✅ Complete' if result.completion_status.get('strategic') else '❌ Incomplete'} |
"""
        if result.errors:
            output += "\n### ⚠️ Errors\n\n" + "\n".join(f"- {e}" for e in result.errors)
        return output
    
    def _create_quality_gauge(self, result):
        fig = go.Figure(go.Indicator(
            mode="gauge+number", value=result.quality_score * 100,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Quality Score", 'font': {'size': 20}},
            gauge={'axis': {'range': [0, 100]}, 'bar': {'color': "darkblue"},
                   'steps': [{'range': [0, 50], 'color': '#fee2e2'}, {'range': [50, 70], 'color': '#fef3c7'},
                             {'range': [70, 90], 'color': '#d1fae5'}, {'range': [90, 100], 'color': '#a7f3d0'}],
                   'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': 70}}
        ))
        fig.update_layout(height=250, margin=dict(l=20, r=20, t=50, b=20))
        return fig
    
    def _create_completion_chart(self, result):
        metrics = {k: 1 if result.completion_status.get(k.lower()) else 0 
                   for k in ["Market", "Competitive", "Risk", "Strategic"]}
        fig = go.Figure(data=[
            go.Bar(x=list(metrics.keys()), y=list(metrics.values()),
                   marker_color=['#10b981' if v == 1 else '#ef4444' for v in metrics.values()],
                   text=['✅' if v == 1 else '❌' for v in metrics.values()], textposition='auto')
        ])
        fig.update_layout(title="Agent Status", yaxis=dict(range=[0, 1.2], tickvals=[0, 1], ticktext=['Failed', 'Complete']),
                         height=250, margin=dict(l=20, r=20, t=50, b=20), showlegend=False)
        return fig

def create_interface():
    srip = SRIPInterface()
    with gr.Blocks(theme=gr.themes.Soft(), title="SRIP - Business Intelligence") as demo:
        gr.Markdown("""# 🚀 SRIP - Smart Research Intelligence Platform
**Production-Grade Multi-Agent Business Intelligence System**

Get comprehensive analysis in minutes!""")
        
        with gr.Row():
            with gr.Column(scale=2):
                query_input = gr.Textbox(label="Business Intelligence Query",
                    placeholder="e.g., Strategic analysis of cloud computing market...", lines=4)
                targets_input = gr.Textbox(label="Analysis Targets (Optional)",
                    placeholder="e.g., AWS, Azure, Google Cloud", lines=2)
                priority_input = gr.Radio(label="Priority", choices=["low", "normal", "high"], value="normal")
                analyze_btn = gr.Button("�� Generate Analysis", variant="primary", size="lg")
            with gr.Column(scale=1):
                gr.Markdown("### 📊 Quality Metrics")
                quality_plot = gr.Plot(label="Quality Score")
                completion_plot = gr.Plot(label="Agent Status")
        
        gr.Markdown("---")
        output_md = gr.Markdown(label="Results")
        
        analyze_btn.click(fn=srip.analyze_business, inputs=[query_input, targets_input, priority_input],
                         outputs=[output_md, quality_plot, completion_plot])
    return demo

if __name__ == "__main__":
    demo = create_interface()
    demo.queue().launch(server_name="0.0.0.0", server_port=7860, share=False)
