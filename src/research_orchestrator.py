"""
Central Research Orchestrator for Agentic Research PRO.
Manages the end-to-end semi-autonomous research workflow:
- Session isolation and unique session_id generation
- Dynamic execution planning and multi-query web search
- Source quality evaluation and filtering
- Robust scraping, cleaning, and sliding-window chunking
- ChromaDB vector indexing and semantic retrieval
- Dimension-based gap detection and bounded iterative follow-ups
- Factual report synthesis and claim evidence grounding
- Deep contradiction detection and explainable confidence heuristics
- Complete progress callback mechanism for real-time UI rendering
"""

import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable, Set

from src.config import ResearchConfig, get_research_config
from src.research_planner import ResearchPlanner, ResearchPlan
from src.tavily_client import TavilySearch
from src.source_evaluator import evaluate_and_filter_sources
from src.scraper import scrape_sources, ScrapedDocument
from src.chunker import chunk_text
from src.embedder import embed_documents
from src.chroma_store import get_vector_store, save_vectors, retrieve_relevant_chunks
from src.gap_detector import ResearchGapDetector, ResearchGap, compute_dimension_coverage
from src.summarizer import Summarizer
from src.claim_verifier import ClaimVerifier, ClaimVerification
from src.contradiction_detector import ContradictionDetector, Contradiction
from src.confidence import calculate_research_confidence, ResearchConfidence
from src.research_metrics import ResearchMetrics

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
logger = logging.getLogger("ResearchOrchestrator")


@dataclass
class ResearchState:
    """Explicit state maintained throughout the research session."""
    session_id: str
    topic: str
    depth: str
    config: ResearchConfig
    plan: Optional[ResearchPlan] = None
    queries: List[str] = field(default_factory=list)
    searched_queries: Set[str] = field(default_factory=set)
    sources: List[Dict[str, Any]] = field(default_factory=list)
    accepted_sources: List[Dict[str, Any]] = field(default_factory=list)
    rejected_sources: List[Dict[str, Any]] = field(default_factory=list)
    documents: List[ScrapedDocument] = field(default_factory=list)
    chunks: List[str] = field(default_factory=list)
    chunk_metadatas: List[Dict[str, Any]] = field(default_factory=list)
    retrieved_chunks: List[Dict[str, Any]] = field(default_factory=list)
    research_iterations: int = 0
    gaps: List[ResearchGap] = field(default_factory=list)
    claims: List[ClaimVerification] = field(default_factory=list)
    contradictions: List[Contradiction] = field(default_factory=list)
    report: str = ""
    confidence: Optional[ResearchConfidence] = None
    metrics: Optional[ResearchMetrics] = None


@dataclass
class ResearchResult:
    """Complete finalized result returned to the caller."""
    state: ResearchState

    @property
    def session_id(self) -> str:
        return self.state.session_id

    @property
    def topic(self) -> str:
        return self.state.topic

    @property
    def depth(self) -> str:
        return self.state.depth

    @property
    def report(self) -> str:
        return self.state.report

    @property
    def plan(self) -> Optional[ResearchPlan]:
        return self.state.plan

    @property
    def accepted_sources(self) -> List[Dict[str, Any]]:
        return self.state.accepted_sources

    @property
    def rejected_sources(self) -> List[Dict[str, Any]]:
        return self.state.rejected_sources

    @property
    def retrieved_chunks(self) -> List[Dict[str, Any]]:
        return self.state.retrieved_chunks

    @property
    def gaps(self) -> List[ResearchGap]:
        return self.state.gaps

    @property
    def claims(self) -> List[ClaimVerification]:
        return self.state.claims

    @property
    def contradictions(self) -> List[Contradiction]:
        return self.state.contradictions

    @property
    def confidence(self) -> Optional[ResearchConfidence]:
        return self.state.confidence

    @property
    def metrics(self) -> Optional[ResearchMetrics]:
        return self.state.metrics

    def to_dict(self) -> Dict[str, Any]:
        return {
            "session_id": self.session_id,
            "topic": self.topic,
            "depth": self.depth,
            "plan": self.plan.to_dict() if self.plan else None,
            "report": self.report,
            "sources_accepted": len(self.accepted_sources),
            "sources_rejected": len(self.rejected_sources),
            "gaps": [g.to_dict() for g in self.gaps],
            "claims": [c.to_dict() for c in self.claims],
            "contradictions": [c.to_dict() for c in self.contradictions],
            "confidence": self.confidence.to_dict() if self.confidence else None,
            "metrics": self.metrics.to_dict() if self.metrics else None,
        }


class ResearchOrchestrator:
    """Central pipeline coordinator."""

    def __init__(
        self,
        planner: Optional[ResearchPlanner] = None,
        searcher: Optional[TavilySearch] = None,
        gap_detector: Optional[ResearchGapDetector] = None,
        summarizer: Optional[Summarizer] = None,
        claim_verifier: Optional[ClaimVerifier] = None,
        contradiction_detector: Optional[ContradictionDetector] = None,
    ):
        self.planner = planner or ResearchPlanner()
        self.searcher = searcher or TavilySearch()
        self.gap_detector = gap_detector or ResearchGapDetector()
        self.summarizer = summarizer or Summarizer()
        self.claim_verifier = claim_verifier or ClaimVerifier()
        self.contradiction_detector = contradiction_detector or ContradictionDetector()

    def run_research(
        self,
        topic: str,
        depth: str = "STANDARD",
        progress_callback: Optional[Callable[[str, float, str], None]] = None,
    ) -> ResearchResult:
        """
        Execute full semi-autonomous research workflow with progress reporting.
        """
        session_id = f"research_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{uuid.uuid4().hex[:6]}"
        config = get_research_config(depth)

        metrics = ResearchMetrics(session_id=session_id, topic=topic, depth=config.name)
        state = ResearchState(
            session_id=session_id,
            topic=topic,
            depth=config.name,
            config=config,
            metrics=metrics,
        )

        def report_step(step_name: str, pct: float, details: str = ""):
            logger.info(f"[{session_id}] [{step_name}] {details}")
            if progress_callback:
                try:
                    progress_callback(step_name, pct, details)
                except Exception as e:
                    logger.warning(f"Progress callback error: {e}")

        report_step("INITIALIZATION", 0.05, f"Starting {config.name} research session for topic: '{topic}'")

        # -------------------------------------------------------------
        # Phase A: Research Planning
        # -------------------------------------------------------------
        report_step("PLANNER", 0.10, "Formulating research plan and search queries...")
        plan = self.planner.plan_research(topic, config=config)
        state.plan = plan
        state.queries.extend(plan.search_queries)
        metrics.generated_queries += len(plan.search_queries)
        if config.enable_planning:
            metrics.llm_calls_made += 1
        report_step("PLANNER", 0.15, f"Generated {len(plan.search_queries)} targeted search queries.")

        # Get isolated session vector store
        vector_store = get_vector_store(session_id)

        # -------------------------------------------------------------
        # Phase B: Iterative Research Loop
        # -------------------------------------------------------------
        current_queries = list(plan.search_queries)

        for iteration in range(1, config.max_iterations + 1):
            state.research_iterations = iteration
            metrics.research_iterations = iteration
            report_step(
                f"ITERATION_{iteration}",
                0.20 + (iteration - 1) * 0.20,
                f"Starting iteration {iteration}/{config.max_iterations} with {len(current_queries)} queries."
            )

            # 1. Multi-query Search
            report_step("SEARCH", 0.22 + (iteration - 1) * 0.20, f"Searching {len(current_queries)} queries via Tavily...")
            iteration_sources = self.searcher.search_multiple(
                current_queries,
                max_results_per_query=max(2, config.max_sources // max(1, len(current_queries))),
                iteration=iteration,
            )
            for q in current_queries:
                state.searched_queries.add(q.lower().strip())

            raw_found = len(iteration_sources)
            metrics.total_sources_found += raw_found

            # Deduplicate against previously gathered sources
            existing_urls = {s.get("url") for s in state.sources}
            new_sources = [s for s in iteration_sources if s.get("url") not in existing_urls]
            dupes = raw_found - len(new_sources)
            metrics.duplicate_sources_removed += dupes
            state.sources.extend(new_sources)
            report_step("SEARCH", 0.25 + (iteration - 1) * 0.20, f"Found {raw_found} sources ({len(new_sources)} new, {dupes} duplicates).")

            # 2. Source Evaluation
            report_step("EVALUATOR", 0.27 + (iteration - 1) * 0.20, "Evaluating source priority and relevance...")
            accepted, rejected = evaluate_and_filter_sources(
                new_sources,
                topic=topic,
                quality_threshold=config.source_quality_threshold,
                min_sources_to_retain=2 if iteration == 1 else 1,
            )
            state.accepted_sources.extend(accepted)
            state.rejected_sources.extend(rejected)
            metrics.sources_accepted += len(accepted)
            metrics.sources_rejected += len(rejected)
            report_step("EVALUATOR", 0.30 + (iteration - 1) * 0.20, f"Accepted {len(accepted)} sources (Rejected: {len(rejected)}).")

            # 3. Scraping & Cleaning
            report_step("SCRAPER", 0.32 + (iteration - 1) * 0.20, f"Scraping content from {len(accepted)} accepted sources...")
            docs, failed_sources = scrape_sources(accepted, timeout=12)
            state.documents.extend(docs)
            metrics.total_documents += len(docs)
            metrics.scraping_failures += len(failed_sources)
            report_step("SCRAPER", 0.35 + (iteration - 1) * 0.20, f"Successfully parsed {len(docs)} documents ({len(failed_sources)} failed).")

            # 4. Chunking
            iteration_chunks = []
            iteration_metadatas = []
            for doc in docs:
                raw_chunks = chunk_text(doc.content, chunk_size=1200, overlap=100)
                for chunk in raw_chunks:
                    iteration_chunks.append(chunk)
                    iteration_metadatas.append({
                        "source_url": doc.url,
                        "source_title": doc.title,
                        "search_query": doc.search_query,
                        "source_score": doc.source_score,
                        "research_iteration": iteration,
                    })

            state.chunks.extend(iteration_chunks)
            state.chunk_metadatas.extend(iteration_metadatas)
            metrics.total_chunks += len(iteration_chunks)

            # 5. Embedding & ChromaDB Indexing
            if iteration_chunks:
                report_step("EMBEDDER", 0.37 + (iteration - 1) * 0.20, f"Generating Hugging Face embeddings for {len(iteration_chunks)} chunks...")
                embeddings = embed_documents(iteration_chunks)
                save_vectors(vector_store, embeddings, iteration_chunks, metadatas=iteration_metadatas)

            # 6. Evidence Retrieval
            report_step("RETRIEVAL", 0.39 + (iteration - 1) * 0.20, "Retrieving evidence passages from vector store...")
            retrieved = retrieve_relevant_chunks(vector_store, topic, top_k=config.top_k)
            state.retrieved_chunks = retrieved
            metrics.retrieved_evidence_chunks = len(retrieved)

            # 7. Gap Detection Check (if iterations remain)
            if iteration < config.max_iterations and config.enable_gap_detection:
                report_step("GAP_DETECTION", 0.41 + (iteration - 1) * 0.20, "Analyzing coverage across research dimensions...")
                evidence_texts = [r["text"] for r in state.retrieved_chunks]
                gaps = self.gap_detector.detect_gaps(
                    topic=topic,
                    plan=plan,
                    evidence_chunks=evidence_texts,
                    config=config,
                    current_iteration=iteration,
                )
                if gaps:
                    state.gaps.extend(gaps)
                    metrics.research_gaps += len(gaps)
                    if config.max_follow_up_gap_analyses > 0:
                        metrics.llm_calls_made += 1
                    # Formulate follow-up queries for next iteration
                    current_queries = [g.suggested_query for g in gaps[:config.max_queries]]
                    report_step("GAP_DETECTION", 0.43 + (iteration - 1) * 0.20, f"Discovered {len(gaps)} research gaps. Scheduling follow-up queries.")
                else:
                    report_step("GAP_DETECTION", 0.43 + (iteration - 1) * 0.20, "Sufficient dimension coverage achieved.")
                    break
            else:
                break

        # Fallback if no chunks were scraped
        if not state.retrieved_chunks and state.chunks:
            state.retrieved_chunks = [
                {"text": c, "metadata": m, "similarity": 0.5}
                for c, m in zip(state.chunks[:config.top_k], state.chunk_metadatas[:config.top_k])
            ]

        # -------------------------------------------------------------
        # Phase C: Report Synthesis (Writer Agent)
        # -------------------------------------------------------------
        report_step("SYNTHESIZER", 0.70, "Synthesizing structured research report with GPT-4o...")
        evidence_for_summary = [r["text"] for r in state.retrieved_chunks]
        report = self.summarizer.summarize(
            topic=topic,
            documents=evidence_for_summary,
            depth=config.name,
            plan=plan,
            sources=state.accepted_sources,
        )
        state.report = report
        metrics.llm_calls_made += 1
        report_step("SYNTHESIZER", 0.75, "Research report synthesis completed.")

        # -------------------------------------------------------------
        # Phase D: Claim Extraction & Evidence Grounding Verification
        # -------------------------------------------------------------
        report_step("CLAIM_VERIFIER", 0.80, "Extracting atomic factual claims from report...")
        extracted_claims = self.claim_verifier.extract_claims(report, max_claims=config.max_claims_to_verify)
        metrics.claims_analyzed = len(extracted_claims)
        metrics.llm_calls_made += 1

        report_step("CLAIM_VERIFIER", 0.83, f"Judging evidence grounding for {len(extracted_claims)} claims...")
        verified_claims = self.claim_verifier.verify_claims_against_evidence(
            extracted_claims,
            collection=vector_store,
            config=config,
        )
        state.claims = verified_claims
        metrics.llm_calls_made += 1
        metrics.supported_claims = sum(1 for c in verified_claims if c.support_label in ["Strongly Supported", "Supported"])
        metrics.weakly_supported_claims = sum(1 for c in verified_claims if c.support_label in ["Weakly Supported", "Unsupported"])
        report_step("CLAIM_VERIFIER", 0.86, f"Verified {len(verified_claims)} claims ({metrics.supported_claims} supported).")

        # -------------------------------------------------------------
        # Phase E: Contradiction Detection (DEEP Mode)
        # -------------------------------------------------------------
        if config.enable_contradiction_detection:
            report_step("CONTRADICTIONS", 0.88, "Clustering evidence and checking for empirical contradictions...")
            contradictions = self.contradiction_detector.detect_contradictions(
                topic=topic,
                plan=plan,
                evidence_chunks=state.retrieved_chunks,
                config=config,
            )
            state.contradictions = contradictions
            metrics.contradictions_detected = len(contradictions)
            metrics.llm_calls_made += 1
            report_step("CONTRADICTIONS", 0.91, f"Identified {len(contradictions)} conflicting viewpoints / trade-offs.")
        else:
            state.contradictions = []

        # -------------------------------------------------------------
        # Phase F: Research Confidence Calculation
        # -------------------------------------------------------------
        report_step("CONFIDENCE", 0.93, "Computing multi-component research confidence score...")
        dimension_coverage = compute_dimension_coverage(
            plan.research_dimensions if plan else [],
            [r["text"] for r in state.retrieved_chunks],
        )
        confidence = calculate_research_confidence(
            accepted_sources=state.accepted_sources,
            dimension_coverage=dimension_coverage,
            claims=state.claims,
            contradictions=state.contradictions,
            iterations_completed=state.research_iterations,
            max_iterations=config.max_iterations,
            target_sources=config.max_sources,
        )
        state.confidence = confidence
        report_step("CONFIDENCE", 0.96, f"Confidence calculated: {int(confidence.overall_score)}/100.")

        # Finalize metrics
        metrics.finalize()
        report_step("COMPLETE", 1.0, f"Research session completed successfully in {metrics.execution_time_seconds}s.")

        return ResearchResult(state=state)


def run_research(
    topic: str,
    depth: str = "STANDARD",
    progress_callback: Optional[Callable[[str, float, str], None]] = None,
) -> ResearchResult:
    """Convenience functional wrapper for executing research."""
    orchestrator = ResearchOrchestrator()
    return orchestrator.run_research(topic, depth=depth, progress_callback=progress_callback)
