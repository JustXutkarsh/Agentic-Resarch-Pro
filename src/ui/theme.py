"""
Agentic Research Design System — Editorial Research Instrument.
Typography:
- Primary UI: Space Grotesk (Navigation, controls, labels, cards, body UI)
- Editorial / Display: Instrument Serif & Newsreader (Hero title, Executive Verdict, pull-quotes)
- Monospace: IBM Plex Mono (Timestamps, telemetry, session IDs)
Color Palette:
- Background: #F7F6F2 (Warm editorial linen paper)
- Primary Ink: #151619
- Secondary Text: #55565D
- Muted: #85868D
- Research Blue: #315BFF
- Deep Blue: #2447D8
- Evidence Green: #138A63
- Warning Amber: #C88900
- Contradiction Coral: #D95C4A
"""

import streamlit as st

EDITORIAL_RESEARCH_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&family=Instrument+Serif:ital@0;1&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400;1,6..72,500&family=IBM+Plex+Mono:wght@400;500;600&display=swap');

:root {
    color-scheme: light !important;
    --text-color: #151619 !important;
    --background-color: #F7F6F2 !important;
    --secondary-background-color: #EFECE6 !important;
    --primary-color: #315BFF !important;

    /* Base Palette */
    --bg-base: #F7F6F2;
    --bg-surface: #FFFFFF;
    --bg-subtle: #F0EFEA;
    --bg-elevated: #FFFFFF;

    /* Borders */
    --border-subtle: rgba(21, 22, 25, 0.08);
    --border-medium: rgba(21, 22, 25, 0.14);
    --border-active: #315BFF;

    /* Strict Editorial Ink Typography */
    --ink-primary: #151619;
    --ink-secondary: #55565D;
    --ink-muted: #85868D;

    /* Active Research Intelligence Accents */
    --research-blue: #315BFF;
    --research-blue-hover: #2447D8;
    --research-blue-subtle: rgba(49, 91, 255, 0.08);
    --research-blue-border: rgba(49, 91, 255, 0.28);
    --evidence-green: #138A63;
    --evidence-green-bg: #EAF6F1;
    --warning-amber: #C88900;
    --warning-amber-bg: #FEF7EA;
    --contradiction-coral: #D95C4A;
    --contradiction-coral-bg: #FDF2F0;

    /* Radii */
    --radius-sm: 8px;
    --radius-md: 14px;
    --radius-lg: 20px;
    --radius-full: 9999px;

    /* Refined Shadows */
    --shadow-subtle: 0 2px 8px rgba(21, 22, 25, 0.03);
    --shadow-card: 0 4px 20px rgba(21, 22, 25, 0.04);
    --shadow-elevated: 0 10px 30px rgba(21, 22, 25, 0.06);

    /* Fonts */
    --font-ui: 'Space Grotesk', -apple-system, BlinkMacSystemFont, sans-serif;
    --font-editorial: 'Instrument Serif', 'Newsreader', Georgia, serif;
    --font-body-serif: 'Newsreader', Georgia, serif;
    --font-mono: 'IBM Plex Mono', monospace;

    /* Transitions */
    --ease-editorial: cubic-bezier(0.16, 1, 0.3, 1);
}

/* ==============================================================================
   BASE BODY & STREAMLIT CANVAS
   ============================================================================== */
body, .stApp {
    background-color: var(--bg-base) !important;
    background-image:
        radial-gradient(circle at 10% 12%, rgba(49, 91, 255, 0.025) 0%, transparent 40%),
        radial-gradient(circle at 90% 18%, rgba(36, 71, 216, 0.02) 0%, transparent 40%),
        radial-gradient(circle at 50% 90%, rgba(19, 138, 99, 0.015) 0%, transparent 50%) !important;
    background-attachment: fixed !important;
    color: var(--ink-primary) !important;
    font-family: var(--font-ui) !important;
    letter-spacing: -0.01em;
    color-scheme: light !important;
    -webkit-font-smoothing: antialiased !important;
    -moz-osx-font-smoothing: grayscale !important;
    text-rendering: optimizeLegibility !important;
}

/* Main Container Max Width */
.main .block-container {
    max-width: 1220px !important;
    padding-top: 1.5rem !important;
    padding-bottom: 5rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
}

/* Hide Default Streamlit Clutter */
#MainMenu, header, footer {
    visibility: hidden !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

div[data-testid="stToolbar"], div[data-testid="stDecoration"] {
    display: none !important;
}

/* Custom Scrollbar */
::-webkit-scrollbar {
    width: 6px;
    height: 6px;
}
::-webkit-scrollbar-track {
    background: transparent;
}
::-webkit-scrollbar-thumb {
    background: rgba(21, 22, 25, 0.15);
    border-radius: 9999px;
}

/* ==============================================================================
   EDITORIAL RESEARCH TYPOGRAPHY SYSTEM
   ============================================================================== */
h1, h2, h3, h4, h5, h6 {
    font-family: var(--font-ui) !important;
    color: var(--ink-primary) !important;
    font-weight: 700 !important;
    letter-spacing: -0.025em !important;
}

p, span, label, div {
    font-family: var(--font-ui);
    color: var(--ink-secondary);
}

.editorial-serif {
    font-family: var(--font-editorial) !important;
    font-style: italic !important;
    font-weight: 400 !important;
}

.mono-text {
    font-family: var(--font-mono) !important;
}

/* ==============================================================================
   NAVIGATION HEADER
   ============================================================================== */
.editorial-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 14px 28px;
    background: rgba(255, 255, 255, 0.92);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    box-shadow: var(--shadow-subtle);
    margin-bottom: 36px;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}

.nav-brand {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 15px;
    font-weight: 700;
    color: var(--ink-primary);
    letter-spacing: -0.02em;
}

.nav-brand .brand-signal {
    color: var(--research-blue);
    font-size: 16px;
}

.nav-badge {
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 600;
    color: var(--research-blue);
    background: var(--research-blue-subtle);
    border: 1px solid var(--research-blue-border);
    padding: 2px 9px;
    border-radius: var(--radius-full);
    letter-spacing: 0.02em;
}

/* ==============================================================================
   HERO & RESEARCH FIELD
   ============================================================================== */
.hero-container {
    text-align: center;
    padding: 40px 20px 28px 20px;
    position: relative;
    max-width: 860px;
    margin: 0 auto;
}

.hero-eyebrow {
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 600;
    color: var(--research-blue);
    text-transform: uppercase;
    letter-spacing: 0.12em;
    margin-bottom: 16px;
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: var(--research-blue-subtle);
    border: 1px solid var(--research-blue-border);
    padding: 4px 14px;
    border-radius: var(--radius-full);
}

.hero-headline {
    font-size: 56px !important;
    font-weight: 700 !important;
    color: var(--ink-primary) !important;
    line-height: 1.08 !important;
    letter-spacing: -0.035em !important;
    margin: 0 0 16px 0 !important;
}

.hero-editorial-headline {
    font-family: var(--font-editorial) !important;
    font-style: italic !important;
    font-weight: 400 !important;
    color: var(--research-blue) !important;
    letter-spacing: -0.01em !important;
}

.hero-subtitle {
    font-size: 16px !important;
    color: var(--ink-secondary) !important;
    line-height: 1.55 !important;
    font-weight: 400 !important;
    max-width: 580px;
    margin: 0 auto 28px auto;
}

/* Subtle Research Field Diagram (QUESTION -> ANGLES -> EVIDENCE -> ITERATION -> INSIGHT) */
.research-field-strip {
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 12px;
    margin-bottom: 32px;
    font-family: var(--font-mono);
    font-size: 11px;
    color: var(--ink-muted);
    font-weight: 500;
    flex-wrap: wrap;
}

.research-field-node {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    background: rgba(255, 255, 255, 0.85);
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-full);
}

.research-field-arrow {
    color: var(--research-blue);
    font-size: 11px;
    opacity: 0.6;
}

/* ==============================================================================
   SEARCH COMPOSER SURFACE
   ============================================================================== */
.stTextInput > div > div > input {
    background: #FFFFFF !important;
    border: 1.5px solid var(--border-medium) !important;
    border-radius: var(--radius-md) !important;
    padding: 16px 22px !important;
    font-size: 16px !important;
    font-family: var(--font-ui) !important;
    color: var(--ink-primary) !important;
    box-shadow: 0 3px 12px rgba(21, 22, 25, 0.04) !important;
    transition: all 0.25s var(--ease-editorial) !important;
}

.stTextInput > div > div > input:focus {
    border-color: var(--research-blue) !important;
    box-shadow: 0 0 0 3.5px rgba(49, 91, 255, 0.12), 0 4px 16px rgba(21, 22, 25, 0.06) !important;
    outline: none !important;
}

.stTextInput > div > div > input::placeholder {
    color: var(--ink-muted) !important;
    font-weight: 400 !important;
}

/* ==============================================================================
   DEPTH SELECTION CARDS
   ============================================================================== */
.depth-card-editorial {
    background: #FFFFFF;
    border: 1.5px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 18px 20px;
    box-shadow: var(--shadow-subtle);
    transition: all 0.25s var(--ease-editorial);
    position: relative;
    height: 100%;
}

.depth-card-editorial.selected {
    border-color: var(--research-blue) !important;
    box-shadow: 0 6px 20px rgba(49, 91, 255, 0.08), inset 0 0 0 1px var(--research-blue) !important;
    background: #FFFFFF !important;
}

.depth-title-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.depth-title {
    font-size: 15px;
    font-weight: 700;
    color: var(--ink-primary);
    display: flex;
    align-items: center;
    gap: 8px;
}

.depth-tagline {
    font-size: 13px;
    font-weight: 600;
    color: var(--research-blue);
    margin-bottom: 4px;
}

.depth-desc {
    font-size: 12.5px;
    color: var(--ink-secondary);
    line-height: 1.45;
}

.depth-badge-rec {
    position: absolute;
    top: -10px;
    right: 16px;
    font-family: var(--font-mono);
    font-size: 9.5px;
    font-weight: 600;
    color: #FFFFFF;
    background: var(--research-blue);
    padding: 2px 8px;
    border-radius: var(--radius-full);
    letter-spacing: 0.06em;
}

/* ==============================================================================
   BUTTON CONTRAST (STRICT WCAG AAA)
   ============================================================================== */
.stButton > button {
    font-family: var(--font-ui) !important;
    font-weight: 600 !important;
    font-size: 14px !important;
    letter-spacing: -0.01em !important;
    border-radius: var(--radius-md) !important;
    padding: 10px 22px !important;
    transition: all 0.22s var(--ease-editorial) !important;
    cursor: pointer !important;
}

/* 1. PRIMARY CTA BUTTON: Dark Ink #151619, Pure White #FFFFFF Text */
.stButton > button[kind="primary"],
.stButton > button[data-testid="baseButton-primary"],
button[kind="primary"] {
    background-color: #151619 !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border: 1px solid #151619 !important;
    box-shadow: 0 4px 16px rgba(21, 22, 25, 0.18) !important;
    padding: 15px 36px !important;
    font-size: 15.5px !important;
    font-weight: 700 !important;
}

.stButton > button[kind="primary"] *,
button[kind="primary"] * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    font-weight: 700 !important;
}

.stButton > button[kind="primary"]:hover,
button[kind="primary"]:hover {
    background-color: #26272B !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(21, 22, 25, 0.26) !important;
}

/* 2. SECONDARY / LIGHT BUTTONS */
.stButton > button[kind="secondary"],
.stButton > button[data-testid="baseButton-secondary"],
button[kind="secondary"] {
    background-color: #FFFFFF !important;
    color: #151619 !important;
    -webkit-text-fill-color: #151619 !important;
    border: 1px solid var(--border-medium) !important;
    box-shadow: var(--shadow-subtle) !important;
}

.stButton > button[kind="secondary"] *,
button[kind="secondary"] * {
    color: #151619 !important;
    -webkit-text-fill-color: #151619 !important;
}

.stButton > button[kind="secondary"]:hover,
button[kind="secondary"]:hover {
    border-color: var(--research-blue) !important;
    color: var(--research-blue) !important;
    -webkit-text-fill-color: var(--research-blue) !important;
    transform: translateY(-1px) !important;
}

/* Active Depth Button Override */
div.depth-active-btn > div.stButton > button {
    background-color: var(--research-blue) !important;
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
    border: 1px solid var(--research-blue) !important;
}

div.depth-active-btn > div.stButton > button * {
    color: #FFFFFF !important;
    -webkit-text-fill-color: #FFFFFF !important;
}

/* ==============================================================================
   AGENTIC RESEARCH EXPERIENCE & LIVE TIMELINE
   ============================================================================== */
.research-active-banner {
    background: #FFFFFF;
    border: 1px solid var(--border-subtle);
    border-left: 4px solid var(--research-blue);
    border-radius: var(--radius-md);
    padding: 20px 26px;
    margin-bottom: 26px;
    box-shadow: var(--shadow-card);
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
}

.investigating-eyebrow {
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 600;
    color: var(--research-blue);
    letter-spacing: 0.12em;
    text-transform: uppercase;
    margin-bottom: 4px;
}

.investigating-topic {
    font-size: 20px;
    font-weight: 700;
    color: var(--ink-primary);
    letter-spacing: -0.02em;
}

.research-status-pill {
    display: flex;
    align-items: center;
    gap: 8px;
    background: var(--research-blue-subtle);
    border: 1px solid var(--research-blue-border);
    padding: 6px 14px;
    border-radius: var(--radius-full);
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 600;
    color: var(--research-blue);
}

.pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--research-blue);
    box-shadow: 0 0 0 rgba(49, 91, 255, 0.4);
    animation: intelligencePulse 1.8s infinite;
}

@keyframes intelligencePulse {
    0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(49, 91, 255, 0.6); }
    70% { transform: scale(1); box-shadow: 0 0 0 8px rgba(49, 91, 255, 0); }
    100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(49, 91, 255, 0); }
}

/* 7-Stage Progression Flow */
.stage-journey-panel {
    background: #FFFFFF;
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 16px 20px;
    margin-bottom: 22px;
    box-shadow: var(--shadow-subtle);
}

.stage-journey-flow {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 8px;
    position: relative;
    overflow-x: auto;
}

.stage-node-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    min-width: 90px;
    position: relative;
    z-index: 2;
}

.stage-node-circle {
    width: 24px;
    height: 24px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    background: #F0EFEA;
    color: var(--ink-muted);
    border: 1.5px solid var(--border-medium);
    margin-bottom: 6px;
    transition: all 0.3s ease;
}

.stage-node-box.active .stage-node-circle {
    background: var(--research-blue);
    color: #FFFFFF;
    border-color: var(--research-blue);
    box-shadow: 0 0 0 4px rgba(49, 91, 255, 0.18);
}

.stage-node-box.done .stage-node-circle {
    background: var(--evidence-green);
    color: #FFFFFF;
    border-color: var(--evidence-green);
}

.stage-node-name {
    font-size: 11px;
    font-weight: 600;
    color: var(--ink-muted);
    letter-spacing: 0.02em;
}

.stage-node-box.active .stage-node-name {
    color: var(--research-blue);
    font-weight: 700;
}

.stage-node-box.done .stage-node-name {
    color: var(--ink-primary);
}

/* Compact Metrics Bar */
.metrics-strip {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 14px;
    margin-bottom: 22px;
}

.metric-cell {
    background: #FFFFFF;
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-sm);
    padding: 14px 18px;
    box-shadow: var(--shadow-subtle);
}

.metric-value {
    font-family: var(--font-mono);
    font-size: 24px;
    font-weight: 700;
    color: var(--ink-primary);
    line-height: 1.1;
}

.metric-label {
    font-size: 12px;
    font-weight: 500;
    color: var(--ink-secondary);
    margin-top: 4px;
}

/* Vertical Research Trail Terminal */
.trail-card {
    background: #FFFFFF;
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 24px 28px;
    box-shadow: var(--shadow-card);
    margin-bottom: 24px;
}

.trail-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 14px;
    margin-bottom: 18px;
}

.trail-title {
    font-size: 13px;
    font-weight: 700;
    color: var(--ink-primary);
    letter-spacing: 0.04em;
    text-transform: uppercase;
    display: flex;
    align-items: center;
    gap: 8px;
}

.trail-elapsed {
    font-family: var(--font-mono);
    font-size: 12px;
    font-weight: 600;
    color: var(--research-blue);
    background: var(--research-blue-subtle);
    padding: 3px 10px;
    border-radius: var(--radius-full);
}

.trail-node {
    display: grid;
    grid-template-columns: 100px 24px 1fr;
    gap: 12px;
    align-items: flex-start;
    padding: 8px 0;
    position: relative;
}

.trail-time {
    font-family: var(--font-mono);
    font-size: 12px;
    color: var(--ink-muted);
    font-weight: 500;
    padding-top: 1px;
}

.trail-bullet-col {
    display: flex;
    flex-direction: column;
    align-items: center;
    height: 100%;
}

.trail-bullet {
    width: 10px;
    height: 10px;
    border-radius: 50%;
    background: var(--ink-primary);
    margin-top: 5px;
}

.trail-bullet.active {
    background: var(--research-blue);
    box-shadow: 0 0 0 4px rgba(49, 91, 255, 0.2);
    animation: intelligencePulse 1.8s infinite;
}

.trail-line {
    width: 2px;
    flex-grow: 1;
    background: var(--border-medium);
    margin-top: 4px;
    margin-bottom: -6px;
    min-height: 16px;
}

.trail-content {
    font-size: 14px;
    color: var(--ink-secondary);
    line-height: 1.5;
}

.trail-content.active {
    color: var(--ink-primary);
    font-weight: 600;
}

.trail-cursor {
    display: inline-block;
    color: var(--research-blue);
    font-weight: 800;
    animation: blinkCursor 0.9s infinite;
    margin-left: 4px;
}

@keyframes blinkCursor {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
}

/* ==============================================================================
   RESULTS DOSSIER — CONTINUOUS PUBLICATION VIEW
   ============================================================================== */
.dossier-verdict-card {
    background: #FFFFFF;
    border: 1px solid var(--border-subtle);
    border-left: 4px solid var(--research-blue);
    border-radius: var(--radius-md);
    padding: 28px 32px;
    box-shadow: var(--shadow-card);
    margin-bottom: 32px;
}

.verdict-eyebrow {
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 600;
    color: var(--research-blue);
    text-transform: uppercase;
    letter-spacing: 0.1em;
}

.verdict-headline {
    font-family: var(--font-editorial) !important;
    font-size: 28px !important;
    font-weight: 400 !important;
    color: var(--ink-primary) !important;
    line-height: 1.2 !important;
    margin: 6px 0 16px 0 !important;
    letter-spacing: -0.01em !important;
}

/* Report Paper */
.report-paper {
    background: #FFFFFF;
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 44px 52px;
    box-shadow: var(--shadow-card);
    line-height: 1.8;
    font-size: 15.5px;
    color: var(--ink-primary);
    margin-bottom: 36px;
}

.report-paper h1, .report-paper h2, .report-paper h3 {
    color: var(--ink-primary) !important;
    font-family: var(--font-ui) !important;
    letter-spacing: -0.02em;
    font-weight: 700;
}

.report-paper h1 {
    font-size: 28px;
    border-bottom: 1px solid var(--border-subtle);
    padding-bottom: 12px;
    margin-bottom: 22px;
}

.report-paper h2 {
    font-size: 21px;
    margin-top: 36px;
    margin-bottom: 14px;
    color: var(--ink-primary) !important;
}

.report-paper h3 {
    font-size: 17px;
    margin-top: 22px;
    margin-bottom: 10px;
    color: var(--ink-secondary) !important;
}

.report-paper p, .report-paper li {
    color: var(--ink-primary) !important;
    font-size: 15.5px;
    line-height: 1.8;
}

.report-paper strong, .report-paper b {
    color: var(--ink-primary) !important;
    font-weight: 700;
}

/* Editorial Callout Badges */
.badge-tag {
    font-family: var(--font-mono);
    font-size: 10.5px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 3px 8px;
    border-radius: var(--radius-sm);
    display: inline-block;
    margin-bottom: 6px;
}

.badge-finding { background: var(--research-blue-subtle); color: var(--research-blue); }
.badge-important { background: #FDF2F0; color: var(--contradiction-coral); }
.badge-evidence { background: var(--evidence-green-bg); color: var(--evidence-green); }
.badge-limitation { background: #F1F5F9; color: #475569; }

/* Progressive Disclosure Card */
details.glass-disclosure {
    background: #FFFFFF;
    border: 1px solid var(--border-subtle);
    border-radius: var(--radius-md);
    padding: 16px 22px;
    margin-bottom: 12px;
    box-shadow: var(--shadow-subtle);
    transition: all 0.25s var(--ease-editorial);
}

details.glass-disclosure[open] {
    border-color: var(--research-blue-border);
    box-shadow: var(--shadow-card);
}

details.glass-disclosure summary {
    cursor: pointer;
    font-weight: 600;
    display: flex;
    justify-content: space-between;
    align-items: center;
    list-style: none;
    user-select: none;
}

details.glass-disclosure summary::-webkit-details-marker {
    display: none;
}

.disclosure-body {
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px solid var(--border-subtle);
}

/* Permanent Footer */
.permanent-footer {
    border-top: 1px solid var(--border-subtle);
    margin-top: 56px;
    padding-top: 28px;
    padding-bottom: 40px;
    text-align: center;
}

.permanent-footer-title {
    font-size: 13px;
    font-weight: 700;
    color: var(--ink-primary);
    letter-spacing: 0.02em;
}

.permanent-footer-attribution {
    font-size: 12px;
    color: var(--ink-muted);
    margin-top: 6px;
}

.permanent-footer-attribution b {
    color: var(--ink-primary);
    font-weight: 700;
}
</style>
"""


def inject_editorial_research_theme():
    """Injects the editorial research typography, palette, and styling into Streamlit."""
    st.markdown(EDITORIAL_RESEARCH_CSS, unsafe_allow_html=True)


# Backward compatibility alias
def inject_white_liquid_glass_theme():
    inject_editorial_research_theme()
