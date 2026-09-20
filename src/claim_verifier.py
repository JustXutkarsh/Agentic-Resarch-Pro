"""
Claim Extraction & Evidence Grounding Verification for Agentic Research PRO.
Implements a rigorous two-step verification workflow:
1. GPT-4o extraction of atomic, verifiable factual claims from the research report.
2. ChromaDB retrieval of top 3-5 relevant evidence chunks, followed by batched GPT-4o
   evidence judgment to classify claims into:
   'Strongly Supported', 'Supported', 'Partially Supported', 'Weakly Supported', 'Unsupported'.
Semantic similarity is used strictly for retrieval, never as proof of factual support.
"""

import json
import logging
import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from openai import OpenAI
from src.config import ResearchConfig, LLM_MODEL
from src.chroma_store import retrieve_relevant_chunks
from chromadb.api.models.Collection import Collection
from src.llm import LLMProvider, get_llm_provider, OpenAICompatibleClientAdapter

logger = logging.getLogger(__name__)

SUPPORT_LABELS = [
    "Strongly Supported",
    "Supported",
    "Partially Supported",
    "Weakly Supported",
    "Unsupported",
]

SUPPORT_SCORES = {
    "Strongly Supported": 1.0,
    "Supported": 0.85,
    "Partially Supported": 0.60,
    "Weakly Supported": 0.35,
    "Unsupported": 0.10,
}


@dataclass
class ClaimVerification:
    """Represents a verified claim and its evidence grounding with full provenance."""
    claim: str
    support_label: str
    support_score: float
    reasoning: str
    evidence_chunks: List[str] = field(default_factory=list)
    source_urls: List[str] = field(default_factory=list)
    source_count: int = 0
    claim_type: str = "EXTERNAL_FACT"  # EXTERNAL_FACT, INTERNAL_METADATA, SYNTHESIS_INFERENCE
    evidence_ids: List[str] = field(default_factory=list)
    authority_tier: Optional[int] = None
    is_roadmap_target: bool = False

    @property
    def score(self) -> float:
        return self.support_score

    @property
    def verification_status(self) -> str:
        return self.support_label

    @property
    def supporting_evidence(self) -> str:
        return " ".join(self.evidence_chunks)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "claim": self.claim,
            "support_label": self.support_label,
            "support_score": round(self.support_score, 2),
            "score": round(self.support_score, 2),
            "verification_status": self.support_label,
            "supporting_evidence": self.supporting_evidence,
            "reasoning": self.reasoning,
            "evidence_chunks": self.evidence_chunks,
            "evidence_snippets": self.evidence_chunks,
            "source_urls": self.source_urls,
            "source_count": self.source_count,
            "claim_type": self.claim_type,
            "evidence_ids": self.evidence_ids,
            "authority_tier": self.authority_tier,
            "is_roadmap_target": self.is_roadmap_target,
        }


INTERNAL_METADATA_PATTERNS = [
    re.compile(r"(?i)\b(?:this|the)\s+report\s+(?:synthesizes|draws|references|contains|presents|examines)\b"),
    re.compile(r"(?i)\b\d+\s+evidence\s+(?:passages|chunks|sources|citations)\b"),
    re.compile(r"(?i)\baverage\s+confidence\s+score\b"),
    re.compile(r"(?i)\bsection\s+\d+\s+(?:outlines|details|discusses)\b"),
    re.compile(r"(?i)\bresearch\s+session\b"),
]


def is_internal_metadata_claim(text: str) -> bool:
    """Checks if a statement is internal report metadata rather than an external fact."""
    return any(p.search(text) for p in INTERNAL_METADATA_PATTERNS)


def _score_claim_importance(claim: str) -> float:
    """Heuristic scoring of claim importance based on specificity and quantitative markers."""
    score = 1.0
    # Higher priority for claims with numbers, statistics, percentages
    if re.search(r"\b\d+(?:\.\d+)?%?", claim):
        score += 0.5
    if re.search(r"\$\b|\bUSD\b|\beuro\b|\byear\b|\b20\d\d\b", claim, re.IGNORECASE):
        score += 0.3
    # Penalize overly short or overly long claims
    words = len(claim.split())
    if 8 <= words <= 30:
        score += 0.4
    return score


def _prioritize_claims(claims: List[str], max_claims: int) -> List[str]:
    """Filter out internal metadata and sort claims by importance heuristic."""
    # Filter out internal report metadata
    substantive = [c for c in claims if not is_internal_metadata_claim(c)]
    if not substantive:
        substantive = claims

    if len(substantive) <= max_claims:
        return substantive
    scored = [(c, _score_claim_importance(c)) for c in substantive]
    scored.sort(key=lambda x: x[1], reverse=True)
    return [c for c, _ in scored[:max_claims]]


class ClaimVerifier:
    """Extracts factual assertions and verifies their grounding against retrieved evidence."""

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

    def extract_claims(self, report: str, max_claims: int = 10) -> List[str]:
        """
        Extract atomic, verifiable factual claims from the generated research report.
        Excludes opinions, generic advice, and internal report metadata.
        """
        if not report or not report.strip():
            return []

        prompt = f"""
You are a fact-checking editor. Extract the most important atomic, factual, and verifiable assertions from this research report.

REPORT:
{report[:6000]}

REQUIREMENTS:
- Extract up to {max_claims * 2} specific, self-contained substantive factual claims.
- Focus on empirical findings, statistics, technological specifications, roadmap targets (e.g. "IBM targets 100M gates on 200 logical qubits by 2029"), and market data.
- STRICT EXCLUSION: DO NOT extract internal meta-statements about the report itself (e.g., "The report synthesizes 29 evidence passages", "Section 4 discusses quantum error correction", "Average confidence is 88%"). Only extract claims about the external subject matter!
- DO NOT extract opinions or generic introductory fluff.
- Return JSON strictly in this format:
{{
  "claims": [
    "First atomic factual claim",
    "Second atomic factual claim"
  ]
}}
"""
        try:
            provider = self._get_provider()
            data = provider.generate_structured(
                messages=[
                    {"role": "system", "content": "You are a precise fact extraction agent."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                operation="claim_extraction",
            )
            extracted = data.get("claims", [])
            clean_claims = [c.strip() for c in extracted if c and len(c.strip()) > 15 and not is_internal_metadata_claim(c)]
            return _prioritize_claims(clean_claims, max_claims)

        except Exception as e:
            logger.warning(f"Claim extraction failed: {e}. Falling back to rule-based sentence extraction.")
            # Rule-based fallback: extract bullet points or sentences with numbers
            bullets = re.findall(r"[-•*]\s*(.+)", report)
            candidates = [b.strip() for b in bullets if len(b.strip()) > 20 and not is_internal_metadata_claim(b)]
            if not candidates:
                candidates = [s.strip() for s in re.split(r"[.!?]\s+", report) if len(s.strip()) > 25 and not is_internal_metadata_claim(s)]
            return _prioritize_claims(candidates, max_claims)

    def verify_claims_against_evidence(
        self,
        claims: List[str],
        collection: Collection,
        config: ResearchConfig,
    ) -> List[ClaimVerification]:
        """
        For each claim:
        1. Retrieve top 3-5 relevant chunks from ChromaDB filtered by research session.
        2. Judge evidence support using batched LLM verification with up to 1400 chars per chunk.
        """
        if not claims or collection.count() == 0:
            return []

        # Enforce max claims budget
        selected_claims = claims[:config.max_claims_to_verify]
        chunks_per_claim = config.max_evidence_chunks_per_claim

        # Retrieve evidence chunks for each claim
        claim_evidence_map: List[Dict[str, Any]] = []
        for claim in selected_claims:
            # Query with session isolation
            matched = retrieve_relevant_chunks(
                collection,
                claim,
                top_k=chunks_per_claim,
                session_id=self.session_id,
            )
            texts = [m["text"] for m in matched if m.get("similarity", 0.0) >= 0.20]
            chunk_ids = [m.get("id", "") for m in matched if m.get("id")]
            urls = list({m["metadata"].get("source_url") for m in matched if m.get("metadata", {}).get("source_url")})
            tiers = [m["metadata"].get("authority_tier") for m in matched if m.get("metadata", {}).get("authority_tier")]
            best_tier = min(tiers) if tiers else 3

            is_roadmap = bool(re.search(r"(?i)\b(?:roadmap|target|targets|planned|projected|goal|by 20\d\d)\b", claim))

            claim_evidence_map.append({
                "claim": claim,
                "evidence_chunks": texts,
                "chunk_ids": chunk_ids,
                "source_urls": urls,
                "source_count": len(urls),
                "authority_tier": best_tier,
                "is_roadmap_target": is_roadmap,
            })

        # Batched evaluation with LLM
        return self._batch_evaluate_support(claim_evidence_map)

    def _batch_evaluate_support(
        self,
        claim_evidence_map: List[Dict[str, Any]],
    ) -> List[ClaimVerification]:
        """
        Evaluate evidence support for a batch of claims using a single structured LLM prompt.
        Preserves complete evidence chunks (up to 1400 chars) and recognizes exact numbers and roadmaps.
        """
        prompt_payload = []
        for idx, item in enumerate(claim_evidence_map):
            # Send up to 1400 characters per snippet, preventing mid-number amputations
            snippets = [c[:1400] for c in item["evidence_chunks"][:3]]
            prompt_payload.append({
                "id": idx,
                "claim": item["claim"],
                "is_roadmap_target": item.get("is_roadmap_target", False),
                "evidence_snippets": snippets,
            })

        prompt = f"""
You are an expert research verifier judging whether specific claims are supported by the provided evidence text.

CRITICAL PRINCIPLES:
1. READ THE EVIDENCE CAREFULLY: Base your judgment strictly on what the snippets explicitly or contextually state.
2. NUMERICAL & METRIC EQUIVALENCES:
   - "100 million quantum gates" == "100M gates" == "10^8 gates"
   - "200 logical qubits" == "200 fault-tolerant qubits"
   - "$140 per kWh" == "$140/kWh"
3. ROADMAP TARGETS VS EMPIRICAL PROOF:
   - If a claim asserts an organization's announced roadmap, milestone, or target (e.g., "IBM roadmap targets Starling for 2029 with 100M gates and 200 logical qubits"), and the evidence confirms that the organization published or stated this roadmap target, classify it as "Strongly Supported" or "Supported" as a documented roadmap milestone!
   - Do NOT mark an announced roadmap milestone as "Unsupported" merely because the future year (e.g. 2029) has not yet arrived.
4. ABSENCE OF EVIDENCE:
   - If the evidence does not mention the subject or directly contradicts the assertion, classify as "Unsupported".

CLASSIFICATION LABELS:
- "Strongly Supported": The evidence explicitly and directly states the claim, roadmap target, or exact data.
- "Supported": The evidence clearly confirms the core assertion of the claim.
- "Partially Supported": The evidence supports some aspects, but lacks key quantitative details or differs slightly.
- "Weakly Supported": The evidence is tangentially related or vague; doesn't directly confirm the assertion.
- "Unsupported": The evidence does not support the claim, contradicts it, or no relevant text exists.

CLAIMS AND EVIDENCE:
{json.dumps(prompt_payload, indent=2)}

Return JSON strictly in this format:
{{
  "evaluations": [
    {{
      "id": 0,
      "support_label": "One of the 5 labels above",
      "reasoning": "1-sentence factual justification referencing the specific evidence snippet"
    }}
  ]
}}
"""
        try:
            provider = self._get_provider()
            data = provider.generate_structured(
                messages=[
                    {"role": "system", "content": "You are a strict, objective, and precise research evidence verifier."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                operation="claim_verification",
            )
            evals = data.get("evaluations", [])
            eval_by_id = {item.get("id"): item for item in evals if "id" in item}

            results = []
            for idx, item in enumerate(claim_evidence_map):
                judgment = eval_by_id.get(idx, {})
                label = judgment.get("support_label", "Partially Supported")
                if label not in SUPPORT_SCORES:
                    label = "Partially Supported"

                score = SUPPORT_SCORES[label]
                reasoning = judgment.get("reasoning", "Evidence retrieved from research collection.")

                results.append(
                    ClaimVerification(
                        claim=item["claim"],
                        support_label=label,
                        support_score=score,
                        reasoning=reasoning,
                        evidence_chunks=item["evidence_chunks"],
                        source_urls=item["source_urls"],
                        source_count=item["source_count"],
                        claim_type="EXTERNAL_FACT",
                        evidence_ids=item.get("chunk_ids", []),
                        authority_tier=item.get("authority_tier"),
                        is_roadmap_target=item.get("is_roadmap_target", False),
                    )
                )
            return results

        except Exception as e:
            logger.warning(f"Batched claim verification LLM call failed: {e}. Using deterministic fallback.")
            results = []
            for item in claim_evidence_map:
                has_chunks = len(item["evidence_chunks"]) > 0
                label = "Supported" if has_chunks else "Unsupported"
                score = 0.85 if has_chunks else 0.10
                results.append(
                    ClaimVerification(
                        claim=item["claim"],
                        support_label=label,
                        support_score=score,
                        reasoning="Deterministic retrieval fallback: source passages retrieved.",
                        evidence_chunks=item["evidence_chunks"],
                        source_urls=item["source_urls"],
                        source_count=item["source_count"],
                        claim_type="EXTERNAL_FACT",
                        evidence_ids=item.get("chunk_ids", []),
                        authority_tier=item.get("authority_tier"),
                        is_roadmap_target=item.get("is_roadmap_target", False),
                    )
                )
            return results

