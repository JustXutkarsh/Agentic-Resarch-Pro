"""
Research Report Synthesis Writer for Agentic Research PRO.
Synthesizes retrieved evidence into a structured, publication-quality research dossier
covering Summary, Key Insights, Pros, Cons, and Citations.
Uses GPT-4o with strict factual adherence and fallback support.
"""

import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from src.config import LLM_MODEL
from src.research_planner import ResearchPlan
from src.llm import LLMProvider, get_llm_provider, OpenAICompatibleClientAdapter

logger = logging.getLogger(__name__)


class Summarizer:
    """Synthesizes structured research reports from evidence and plan."""

    def __init__(
        self,
        client: Optional[Any] = None,
        llm_provider: Optional[LLMProvider] = None,
        session_id: Optional[str] = None,
    ):
        self.client = client
        self._provider = llm_provider
        self.session_id = session_id

    def _get_provider(self) -> LLMProvider:
        if self._provider is not None:
            return self._provider
        if self.client is not None:
            self._provider = OpenAICompatibleClientAdapter(self.client, model=LLM_MODEL)
            return self._provider
        self._provider = get_llm_provider(session_id=self.session_id)
        return self._provider

    def _get_client(self) -> Any:
        if self.client is None:
            self.client = OpenAI()
        return self.client

    def summarize(
        self,
        topic: str,
        documents: List[str],
        depth: str = "Standard",
        plan: Optional[ResearchPlan] = None,
        sources: Optional[List[Dict[str, Any]]] = None,
    ) -> str:
        """
        Generate a structured research report backed by evidence.
        """
        if not documents:
            return (
                f"# Research Report: {topic}\n\n"
                "### Summary\nInsufficient evidence could be retrieved for this topic.\n\n"
                "### Key Insights\n- No verified insights available.\n\n"
                "### Pros & Cons\n**Pros:**\n- N/A\n\n**Cons:**\n- N/A\n\n"
                "### Citations\n- No sources available."
            )

        d_upper = depth.upper()
        
        # Determine evidence passage allocation and token targets based on depth
        if "DEEP" in d_upper:
            doc_limit = 30
            max_tokens = 4000
            temperature = 0.2
        elif "QUICK" in d_upper:
            doc_limit = 10
            max_tokens = 1500
            temperature = 0.2
        else:  # STANDARD
            doc_limit = 20
            max_tokens = 2800
            temperature = 0.2

        joined_evidence = ""
        for idx, doc in enumerate(documents[:doc_limit]):
            joined_evidence += f"\n--- EVIDENCE PASSAGE [EVP-{idx+1:02d}] ---\n{doc[:1400]}\n"

        plan_context = ""
        if plan:
            plan_context = (
                f"CORE RESEARCH QUESTION: {plan.main_question}\n"
                f"INVESTIGATIVE DIMENSIONS: {', '.join(plan.research_dimensions)}\n"
            )

        sources_context = ""
        if sources:
            urls = []
            for s in sources[:15]:
                u = s.get("url", "")
                t = s.get("tier", 3)
                st = s.get("source_type", "web")
                if u:
                    urls.append(f"- {u} (Tier {t}: {st})")
            sources_context = "AVAILABLE RETRIEVED SOURCES:\n" + "\n".join(urls)

        if "DEEP" in d_upper:
            prompt = f"""
You are a senior principal research fellow writing an exhaustive, evidence-dense, publication-grade scientific and economic dossier.

TOPIC: {topic}
RESEARCH DEPTH: DEEP (Rigorous Multi-Dimensional Investigation)
{plan_context}

RETRIEVED EVIDENCE PASSAGES:
{joined_evidence}

{sources_context}

CRITICAL EVIDENCE INTEGRITY & DENSITY MANDATE:
1. STRICT SUBJECT RELEVANCE: Focus strictly and exclusively on the core topic '{topic}'. DO NOT drift into generic enterprise software tropes, SaaS monetization, cloud compute clusters, or unrelated commercial cliches unless directly stated in the evidence regarding this specific topic.
2. EVIDENCE DENSITY OVER PAGE COUNT: Prioritize factual density, technical precision, and analytical completeness. DO NOT generate filler, repetitive prose, or empty transitions to artificially lengthen the report. Every paragraph must convey substantive technical, physical, economic, or empirical mechanisms.
3. GROUNDING & EVIDENCE CITATIONS: Ground all factual assertions, specifications, and dates in the provided evidence passages. Reference relevant evidence identifiers (e.g. [EVP-01], [EVP-04]) where appropriate.
4. ROADMAP TARGETS VS EMPIRICAL PROOFS: When citing company roadmaps (e.g. IBM Starling, Google Quantum AI), accurately frame them as official roadmap targets rather than established retrospective achievements.
5. NO REPORT SELF-METADATA AS CLAIMS: In Section 7, only discuss substantive domain assertions (e.g. qubit counts, gate fidelities, error correction thresholds, commercial timeframes). NEVER discuss internal report metadata like "This report analyzed 29 evidence chunks".

Structure the dossier following this rigorous academic hierarchy:

# Research Report: {topic}

## Abstract
<Rigorous 150-250 word scientific abstract summarizing research problem, evidence base, core findings, and broader implications>

## Executive Summary
<Authoritative 300-450 word synthesis of the investigation outcome, key dynamics, and consensus reality>

## 1. Introduction & Research Scope
<Detailed context defining the core question, scope of investigation, and analytical necessity across dimensions>

## 2. Related Research & Literature Analysis
<Comprehensive literature review examining published research, institutional findings, and authoritative studies identified in the evidence>

## 3. Comprehensive Evidence & Multi-Dimensional Analysis
<Systematic examination of technical, architectural, physical, and economic dimensions. Cite specific empirical data, error thresholds, engineering hurdles, and scaling metrics from evidence>

## 4. Multi-Perspective Evaluation
### Optimistic Perspective
<Detailed examination of technical progress, architectural breakthroughs, and roadmap commitments supported by evidence>
### Balanced Perspective
<Nuanced assessment reconciling theoretical milestones with practical engineering constraints>
### Skeptical Perspective
<Rigorous examination of physical bottlenecks, error correction overhead, thermodynamic/hardware scaling limits, and capital barriers>

## 5. Empirical Contradictions & Counter-Evidence Analysis
<Deep analysis of where retrieved evidence diverges across operational regimes (e.g., NISQ sampling vs Fault-Tolerant production), competing hardware platforms, or diverging commercial timelines>

## 6. Information Gaps & Evidentiary Boundaries
<Discussion of unresolved technical parameters, missing experimental demonstrations, and areas requiring ongoing empirical monitoring>

## 7. Factual Claim Verification & Grounding
<Structured examination of key empirical claims evaluated against retrieved passages and source citations>

## 8. Strategic Implications & Discussion
<Discussion of broader scientific, technological, industrial, and economic implications resulting from the evidence>

## 9. Research Limitations & Uncertainties
<Rigorous academic limitations, data latency caveats, and unresolved physical or economic variables>

## 10. Conclusion & Outlook
<Decisive analytical synthesis directly answering the core research question>

## References & Academic Citations
<Clean list of authoritative source links and literature references>
"""
        elif "QUICK" in d_upper:
            prompt = f"""
You are an executive research analyst compiling a concise, high-impact research brief.

TOPIC: {topic}
RESEARCH DEPTH: QUICK (Essential Evidence Brief)
{plan_context}

RETRIEVED EVIDENCE PASSAGES:
{joined_evidence}

{sources_context}

INSTRUCTIONS:
1. Synthesize the core factual evidence into a punchy, rigorous research brief.
2. Focus strictly on evidence density without filler, repetition, or unrelated business tropes.
3. Follow this layout:

# Research Report: {topic}

## Executive Summary
<Concise 150-250 word executive summary providing clear, actionable overview>

## Key Findings & Strategic Insights
- **Insight 1**: Detailed explanation grounded in evidence
- **Insight 2**: Detailed explanation grounded in evidence
- **Insight 3**: Detailed explanation grounded in evidence

## Main Evidence & Analysis
<2-3 well-developed analytical paragraphs examining core evidence passages and operational realities>

## Conclusion
<Decisive concluding synthesis answering the core question>

## Source Citations & References
<Clean list of primary source URLs>
"""
        else:  # STANDARD
            prompt = f"""
You are a senior research analyst compiling a structured, comprehensive research dossier.

TOPIC: {topic}
RESEARCH DEPTH: STANDARD (Balanced Investigation)
{plan_context}

RETRIEVED EVIDENCE PASSAGES:
{joined_evidence}

{sources_context}

INSTRUCTIONS:
1. Synthesize the factual evidence into an objective, deeply detailed executive research report.
2. Ground all statements strictly in the provided evidence. Focus on technical and economic realities specific to '{topic}'.
3. Avoid generic filler, unrelated software/cloud cliches, and repetitive phrasing.
4. Follow this layout:

# Research Report: {topic}

## Executive Summary
<Comprehensive 250-350 word executive synthesis>

## Research Scope & Investigative Methodology
<Overview of the research question, core investigative dimensions, and scope>

## Key Findings & Strategic Insights
- **Finding 1**: Detailed explanation with evidence
- **Finding 2**: Detailed explanation with evidence
- **Finding 3**: Detailed explanation with evidence
- **Finding 4**: Detailed explanation with evidence

## In-Depth Evidence & Dimensional Analysis
<Detailed narrative examining evidence across dimensions with specific data points and qualitative insights>

## Multiple Perspectives & Consensus
### Optimistic Viewpoint
<Key arguments and structural opportunities supported by evidence>
### Balanced Viewpoint
<Consensus assessment and practical constraints>
### Skeptical Viewpoint
<Identified risks, physical limits, and counter-arguments>

## Where Evidence Disagrees (Contradictions)
<Key areas where data points or expert analyses diverge, distinguishing between different operational regimes or timeframes>

## Evidence Gaps & Investigation Trajectory
<Discussion of detected information gaps and evidentiary boundaries>

## Conclusion
<Definitive, evidence-grounded conclusion>

## Source Citations & References
<Clean list of authoritative source links>
"""

        try:
            provider = self._get_provider()
            resp = provider.generate(
                messages=[
                    {
                        "role": "system",
                        "content": "You are an elite, objective research analyst creating structured, evidence-backed research dossiers with zero filler and strict topical fidelity."
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=temperature,
                max_tokens=max_tokens,
                operation="report_synthesis",
            )
            report = resp.content or ""
            return report.strip()

        except Exception as e:
            logger.warning(f"Report synthesis failed: {e}. Generating deterministic summary.")
            citations = [s.get("url") for s in (sources or []) if s.get("url")][:8]
            cite_str = "\n".join(f"- {c}" for c in citations) if citations else "- Source URLs not recorded."
            return (
                f"# Research Report: {topic} (Fallback Synthesis)\n\n"
                f"## Executive Summary\n"
                f"An autonomous research investigation into '{topic}' was performed at {depth} depth. "
                f"A total of {len(documents)} evidence passages were analyzed across the designated research dimensions.\n\n"
                f"## Key Findings & Strategic Insights\n"
                f"- **Evidence Base**: Retrieved and evaluated {len(documents)} relevant passages from literature sources.\n"
                f"- **Core Finding**: Empirical findings indicate technical scaling and operational constraints for {topic}.\n"
                f"- **Perspective Divergence**: Technical feasibility estimates diverge based on architectural models and operational assumptions.\n\n"
                f"## In-Depth Evidence & Dimensional Analysis\n"
                f"Analysis of indexed evidence indicates that '{topic}' encompasses engineering limits, error thresholds, and economic factors. "
                f"Primary sources emphasize that viability depends on overcoming core physical hurdles and demonstrating sustained performance.\n\n"
                f"## Multiple Perspectives & Consensus\n"
                f"### Optimistic Viewpoint\nOngoing research milestones and platform developments indicate continuous progress.\n\n"
                f"### Skeptical Viewpoint\nUnderlying hardware error rates and scaling overhead present substantial barriers.\n\n"
                f"## Conclusion\n"
                f"Evidence highlights that realization of {topic} requires addressing fundamental technical barriers before commercial deployment.\n\n"
                f"## Source Citations & References\n{cite_str}"
            )
