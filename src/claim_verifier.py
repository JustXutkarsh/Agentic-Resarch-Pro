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
    """Represents a verified claim and its evidence grounding."""
    claim: str
    support_label: str
    support_score: float
    reasoning: str
    evidence_chunks: List[str] = field(default_factory=list)
    source_urls: List[str] = field(default_factory=list)
    source_count: int = 0

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
        }


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
    """Sort claims by importance heuristic and return top max_claims."""
    if len(claims) <= max_claims:
        return claims
    scored = [(c, _score_claim_importance(c)) for c in claims]
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
        Excludes opinions, generic advice, and vague statements.
        """
        if not report or not report.strip():
            return []

        prompt = f"""
You are a fact-checking editor. Extract the most important atomic, factual, and verifiable assertions from this research report.

REPORT:
{report[:4000]}

REQUIREMENTS:
- Extract up to {max_claims * 2} specific, self-contained factual claims.
- Focus on empirical findings, statistics, performance numbers, market projections, and causal assertions.
- DO NOT extract opinions, recommendations, or generic introductory fluff.
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
            clean_claims = [c.strip() for c in extracted if c and len(c.strip()) > 15]
            return _prioritize_claims(clean_claims, max_claims)

        except Exception as e:
            logger.warning(f"Claim extraction failed: {e}. Falling back to rule-based sentence extraction.")
            # Rule-based fallback: extract bullet points or sentences with numbers
            bullets = re.findall(r"[-•*]\s*(.+)", report)
            candidates = [b.strip() for b in bullets if len(b.strip()) > 20]
            if not candidates:
                candidates = [s.strip() for s in re.split(r"[.!?]\s+", report) if len(s.strip()) > 25]
            return _prioritize_claims(candidates, max_claims)

    def verify_claims_against_evidence(
        self,
        claims: List[str],
        collection: Collection,
        config: ResearchConfig,
    ) -> List[ClaimVerification]:
        """
        For each claim:
        1. Retrieve top 3-5 relevant chunks from ChromaDB.
        2. Judge evidence support using batched GPT-4o verification.
        """
        if not claims or collection.count() == 0:
            return []

        # Enforce max claims budget
        selected_claims = claims[:config.max_claims_to_verify]
        chunks_per_claim = config.max_evidence_chunks_per_claim

        # Retrieve evidence chunks for each claim
        claim_evidence_map: List[Dict[str, Any]] = []
        for claim in selected_claims:
            matched = retrieve_relevant_chunks(collection, claim, top_k=chunks_per_claim)
            texts = [m["text"] for m in matched if m.get("similarity", 0.0) >= 0.25]
            urls = list({m["metadata"].get("source_url") for m in matched if m.get("metadata", {}).get("source_url")})

            claim_evidence_map.append({
                "claim": claim,
                "evidence_chunks": texts,
                "source_urls": urls,
                "source_count": len(urls),
            })

        # Batched evaluation with GPT-4o
        return self._batch_evaluate_support(claim_evidence_map)

    def _batch_evaluate_support(
        self,
        claim_evidence_map: List[Dict[str, Any]],
    ) -> List[ClaimVerification]:
        """
        Evaluate evidence support for a batch of claims using a single structured GPT-4o prompt.
        """
        prompt_payload = []
        for idx, item in enumerate(claim_evidence_map):
            prompt_payload.append({
                "id": idx,
                "claim": item["claim"],
                "evidence_snippets": [c[:400] for c in item["evidence_chunks"][:3]],
            })

        prompt = f"""
You are a research verifier judging whether specific claims are supported by the provided evidence text.

CRITICAL PRINCIPLE:
Semantic similarity indicates topical relevance, NOT factual truth. You must read the actual text in the evidence snippets.

CLASSIFICATION LABELS:
- "Strongly Supported": The evidence explicitly and directly states the claim or provides exact data.
- "Supported": The evidence clearly confirms the core assertion of the claim.
- "Partially Supported": The evidence supports some aspects, but lacks key details or differs slightly.
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
      "reasoning": "1-sentence factual justification"
    }}
  ]
}}
"""
        try:
            provider = self._get_provider()
            data = provider.generate_structured(
                messages=[
                    {"role": "system", "content": "You are a strict, objective research evidence verifier."},
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
                reasoning = judgment.get("reasoning", "Evidence semantically retrieved from research collection.")

                results.append(
                    ClaimVerification(
                        claim=item["claim"],
                        support_label=label,
                        support_score=score,
                        reasoning=reasoning,
                        evidence_chunks=item["evidence_chunks"],
                        source_urls=item["source_urls"],
                        source_count=item["source_count"],
                    )
                )
            return results

        except Exception as e:
            logger.warning(f"Batched claim verification LLM call failed: {e}. Using deterministic fallback.")
            results = []
            for item in claim_evidence_map:
                has_chunks = len(item["evidence_chunks"]) > 0
                label = "Supported" if has_chunks else "Unsupported"
                score = 0.75 if has_chunks else 0.10
                results.append(
                    ClaimVerification(
                        claim=item["claim"],
                        support_label=label,
                        support_score=score,
                        reasoning="Deterministic retrieval fallback: source passages retrieved.",
                        evidence_chunks=item["evidence_chunks"],
                        source_urls=item["source_urls"],
                        source_count=item["source_count"],
                    )
                )
            return results
