"""
Live End-to-End Deep Mode Validation Script for Evidence-Integrity Hardening.
Tests the exact quantum computing topic:
'What are the fundamental technical and economic barriers preventing fault-tolerant quantum computing from achieving commercially useful quantum advantage by 2040?'
"""

import sys
import os
import time
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("LiveQuantumValidation")

from dotenv import load_dotenv
load_dotenv()

from src.research_orchestrator import run_research
from src.pdfgen import generate_research_pdf

TOPIC = "What are the fundamental technical and economic barriers preventing fault-tolerant quantum computing from achieving commercially useful quantum advantage by 2040?"
SESSION_ID = f"live_quantum_eval_{int(time.time())}"

def progress_logger(step_name: str, pct: float, details: str):
    print(f"[{int(pct*100):02d}%] [{step_name}] {details}", flush=True)

def main():
    print("=" * 80)
    print("STARTING LIVE DEEP MODE QUANTUM INVESTIGATION")
    print(f"Topic: {TOPIC}")
    print(f"Session ID: {SESSION_ID}")
    print("=" * 80)

    t0 = time.time()
    result = run_research(
        topic=TOPIC,
        depth="DEEP",
        progress_callback=progress_logger,
        session_id=SESSION_ID,
    )
    elapsed = round(time.time() - t0, 1)

    print("\n" + "=" * 80)
    print(f"RESEARCH SESSION COMPLETED IN {elapsed} SECONDS")
    print("=" * 80)

    # 1. Inspect Sources & Authority Tiers
    print(f"\n--- 1. ACCEPTED SOURCES ({len(result.accepted_sources)}) ---")
    tier_counts = {1: 0, 2: 0, 3: 0, 4: 0}
    for s in result.accepted_sources:
        tier = s.get("tier", 3)
        st = s.get("source_type", "web")
        url = s.get("url", "")
        tier_counts[tier] = tier_counts.get(tier, 0) + 1
        print(f"  [Tier {tier}] ({st}) {url[:70]}")
    print(f"Tier Distribution: {tier_counts}")

    # 2. Inspect Claims Grounding
    print(f"\n--- 2. VERIFIED CLAIMS ({len(result.claims)}) ---")
    for idx, c in enumerate(result.claims):
        print(f"  Claim {idx+1}: {c.claim}")
        print(f"    Status: {c.support_label} (Score: {c.support_score}) | Type: {c.claim_type} | Roadmap: {c.is_roadmap_target}")
        print(f"    Reasoning: {c.reasoning[:120]}...")
        if c.source_urls:
            print(f"    Sources: {c.source_urls[:2]}")

    # 3. Inspect Contradictions
    print(f"\n--- 3. CONTRADICTIONS & DIVERGENCES ({len(result.contradictions)}) ---")
    for idx, ct in enumerate(result.contradictions):
        dtype = getattr(ct, 'divergence_type', 'N/A')
        print(f"  Divergence {idx+1}: [{dtype}] {ct.topic}")
        print(f"    Perspective A: {ct.perspective_a[:80]}...")
        print(f"    Perspective B: {ct.perspective_b[:80]}...")
        if getattr(ct, 'scope_difference', None):
            print(f"    Scope Context: {ct.scope_difference[:100]}...")

    # 4. Check for Hallucinations / Contamination
    print("\n--- 4. EVIDENCE INTEGRITY & CONTAMINATION AUDIT ---")
    report_text = result.report or ""
    forbidden_terms = [
        "enterprise software seats",
        "SaaS monetization",
        "annual recurring revenue",
        "hyperscaler compute clusters",
        "semiconductor suppliers",
        "valuation contraction",
    ]
    contaminants_found = []
    for term in forbidden_terms:
        if term.lower() in report_text.lower():
            contaminants_found.append(term)

    if contaminants_found:
        print(f"❌ CONTAMINATION DETECTED: {contaminants_found}")
    else:
        print("✅ ZERO CONTAMINATION DETECTED: No unrelated SaaS / cloud / capex tropes found.")

    # 5. Check Internal Metadata Claim Contamination
    metadata_claims_found = [c.claim for c in result.claims if "evidence passages" in c.claim.lower() or "report synthesizes" in c.claim.lower()]
    if metadata_claims_found:
        print(f"❌ INTERNAL METADATA LEAKED INTO CLAIMS: {metadata_claims_found}")
    else:
        print("✅ CLEAN CLAIMS: Zero internal report meta-statements verified as external facts.")

    # 6. Check Confidence & Metrics
    print(f"\n--- 5. CONFIDENCE BREAKDOWN ({result.confidence.overall_score}/100) ---")
    print(f"  Source Quality: {result.confidence.source_quality}")
    print(f"  Evidence Coverage: {result.confidence.evidence_coverage}")
    print(f"  Claim Support: {result.confidence.claim_support}")
    print(f"  Source Agreement: {result.confidence.source_agreement}")
    print(f"  Research Completeness: {result.confidence.research_completeness}")
    print(f"  Explanation: {result.confidence.explanation}")

    # 7. Generate PDF
    pdf_out = f"quantum_hardened_{SESSION_ID}.pdf"
    generate_research_pdf(result, output_path=pdf_out)
    if os.path.exists(pdf_out):
        sz = os.path.getsize(pdf_out)
        print(f"\n✅ PDF GENERATED: {pdf_out} ({sz} bytes)")
    else:
        print("\n❌ PDF Generation failed.")

if __name__ == "__main__":
    main()
