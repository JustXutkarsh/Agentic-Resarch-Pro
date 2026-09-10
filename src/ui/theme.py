"""
Apple-Inspired Minimal Liquid Glass (80%) + Claymorphism (15%) + Neo-Brutalism (5%) Design System
for Agentic Research PRO.
Strong Light Contrast System:
- Primary text: #1C1C1E (near-black charcoal)
- Secondary text: #4A4A4F
- Muted text: #6E6E73
- Disabled text: #9A9AA0
Core Rule: "Glass can be translucent. Text cannot be."
"""

WHITE_LIQUID_GLASS_CSS = """<style>
@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400;1,600&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400;1,6..72,500&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
    color-scheme: light !important;
    --text-color: #1C1C1E !important;
    --background-color: #F8F7F4 !important;
    --secondary-background-color: #EFECE6 !important;
    --primary-color: #E85D4A !important;
    
    --bg-base: #F8F7F4;
    --bg-secondary: #EFECE6;
    
    /* Contrast Glass Surfaces */
    --surface-glass: rgba(255, 255, 255, 0.88);
    --surface-glass-card: rgba(255, 255, 255, 0.82);
    --surface-glass-elevated: rgba(255, 255, 255, 0.96);
    
    --glass-border: rgba(255, 255, 255, 0.95);
    --glass-border-subtle: rgba(0, 0, 0, 0.08);
    --glass-border-accent: rgba(0, 102, 255, 0.40);
    
    /* Strict Light Contrast Hierarchy */
    --text-primary: #1C1C1E;
    --text-secondary: #4A4A4F;
    --text-muted: #6E6E73;
    --text-disabled: #9A9AA0;
    
    --accent-blue: #0066FF;
    --accent-blue-light: #EBF3FF;
    --accent-coral: #E85D4A;
    --accent-coral-glow: rgba(232, 93, 74, 0.4);
    --accent-charcoal: #1C1C1E;
    --accent-charcoal-hover: #2C2C2E;
    --accent-emerald: #047857;
    --accent-amber: #92400E;
    --accent-rose: #9F1239;
    
    --radius-sm: 10px;
    --radius-md: 16px;
    --radius-lg: 24px;
    --radius-xl: 32px;
    --radius-full: 9999px;

    /* Claymorphic 3D Depth Shadows */
    --clay-btn: 0 4px 16px rgba(0, 0, 0, 0.18), inset 0 1px 1px rgba(255, 255, 255, 0.35);
    --clay-btn-hover: 0 8px 24px rgba(0, 0, 0, 0.24), inset 0 1px 1px rgba(255, 255, 255, 0.5);
    --clay-card: 0 8px 32px rgba(0, 0, 0, 0.06), 0 1px 3px rgba(0, 0, 0, 0.02), inset 0 1px 1px rgba(255, 255, 255, 0.95);
    --clay-card-hover: 0 16px 40px rgba(0, 0, 0, 0.08), 0 2px 6px rgba(0, 0, 0, 0.03), inset 0 1px 1px #FFFFFF;
    --clay-card-selected: 0 16px 36px rgba(0, 102, 255, 0.16), inset 0 0 0 2px #0066FF, inset 0 1px 2px #FFFFFF;
}

/* Base Body & App Canvas */
body, .stApp {
    background-color: var(--bg-base) !important;
    background-image: 
        radial-gradient(circle at 12% 14%, rgba(215, 228, 255, 0.45) 0%, transparent 42%),
        radial-gradient(circle at 88% 18%, rgba(242, 226, 255, 0.45) 0%, transparent 42%),
        radial-gradient(circle at 50% 85%, rgba(255, 235, 220, 0.40) 0%, transparent 50%) !important;
    background-attachment: fixed !important;
    color: var(--text-primary) !important;
    font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, 'SF Pro Display', system-ui, sans-serif !important;
    letter-spacing: -0.015em;
    color-scheme: light !important;
}

/* Constrain App Canvas Width for Focused Apple Reading Experience */
.main .block-container,
div[data-testid="stMainBlockContainer"],
.block-container {
    max-width: 1240px !important;
    padding-top: 1.25rem !important;
    padding-bottom: 4rem !important;
    padding-left: 2rem !important;
    padding-right: 2rem !important;
    margin: 0 auto !important;
}

/* Global Strict Light Contrast Overrides — Prevents Dark-Mode Bleed */
.stMarkdown,
.stMarkdown p,
.stMarkdown span,
.stMarkdown div,
.stMarkdown li,
.stMarkdown h1,
.stMarkdown h2,
.stMarkdown h3,
.stMarkdown h4,
.stMarkdown h5,
.stMarkdown h6,
.stText,
.stCaption,
[data-testid="stCaptionContainer"],
[data-testid="stCaptionContainer"] *,
[data-testid="stMarkdownContainer"],
[data-testid="stMarkdownContainer"] p,
[data-testid="stMarkdownContainer"] span,
label {
    color: var(--text-primary) !important;
    -webkit-text-fill-color: var(--text-primary) !important;
    opacity: 1 !important;
}

/* Ambient Moving Liquid Layer */
.ambient-liquid-layer {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    pointer-events: none;
    z-index: 0;
    background: 
        radial-gradient(circle at 15% 20%, rgba(210, 225, 255, 0.35) 0%, transparent 45%),
        radial-gradient(circle at 85% 25%, rgba(238, 224, 255, 0.30) 0%, transparent 45%),
        radial-gradient(circle at 50% 80%, rgba(255, 235, 220, 0.25) 0%, transparent 50%);
    filter: blur(50px);
    opacity: 0.85;
    animation: ambientShift 24s ease-in-out infinite alternate;
}

@keyframes ambientShift {
    0% { transform: scale(1) translate(0, 0); }
    50% { transform: scale(1.04) translate(-15px, 15px); }
    100% { transform: scale(1) translate(15px, -15px); }
}

/* Hide standard Streamlit header & toolbar clutter */
header[data-testid="stHeader"] {
    background: transparent !important;
}

div[data-testid="stToolbar"] {
    display: none !important;
}

/* Floating Navigation Bar */
.floating-nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.90), rgba(255, 255, 255, 0.72));
    backdrop-filter: blur(28px) saturate(160%);
    -webkit-backdrop-filter: blur(28px) saturate(160%);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-full);
    padding: 12px 28px;
    margin: 10px auto 36px auto;
    max-width: 960px;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08), inset 0 1px 1px #FFFFFF;
    position: relative;
    z-index: 10;
}

.nav-brand {
    display: flex;
    align-items: center;
    gap: 8px;
    font-weight: 800;
    font-size: 16px;
    color: var(--text-primary);
    letter-spacing: -0.4px;
}

.nav-links {
    display: flex;
    align-items: center;
    gap: 16px;
}

.nav-link-item {
    font-size: 13.5px;
    font-weight: 600;
    color: #3A3A3C !important;
    padding: 6px 14px;
    border-radius: var(--radius-full);
    background: transparent;
    transition: all 0.2s ease;
    text-decoration: none;
    cursor: pointer;
    opacity: 1 !important;
}

.nav-link-item:hover {
    color: var(--text-primary) !important;
    background: rgba(0, 0, 0, 0.05);
}

.nav-pill-badge {
    font-size: 11.5px;
    font-weight: 700;
    letter-spacing: 0.5px;
    color: var(--accent-blue);
    background: var(--accent-blue-light);
    border-radius: var(--radius-full);
    padding: 4px 12px;
    border: 1px solid rgba(0, 102, 255, 0.25);
}

/* Editorial Hero Section */
.hero-box {
    text-align: center;
    padding: 24px 0 32px 0;
    max-width: 820px;
    margin: 0 auto;
    position: relative;
    z-index: 5;
}

.hero-pill-badge {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-size: 11.5px;
    font-weight: 750;
    color: #4338CA;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    background: rgba(238, 242, 255, 0.95);
    border: 1px solid rgba(199, 210, 254, 0.9);
    border-radius: var(--radius-full);
    padding: 5px 16px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(79, 70, 229, 0.08);
}

.hero-title {
    font-family: 'Plus Jakarta Sans', sans-serif;
    font-size: 58px;
    font-weight: 800;
    line-height: 1.1;
    letter-spacing: -1.6px;
    color: var(--text-primary) !important;
    margin-bottom: 16px;
}

.hero-title em {
    font-family: 'Newsreader', serif;
    font-style: italic;
    font-weight: 400;
    color: #2C2C2E !important;
    letter-spacing: -0.5px;
}

.hero-subtitle {
    font-size: 18px;
    color: var(--text-secondary) !important;
    line-height: 1.6;
    max-width: 600px;
    margin: 0 auto;
    font-weight: 500;
    opacity: 1 !important;
}

/* Large Floating Liquid-Glass Search Composer */
div[data-baseweb="input"] {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.94), rgba(255, 255, 255, 0.80)) !important;
    border: 1px solid var(--glass-border) !important;
    border-radius: var(--radius-xl) !important;
    backdrop-filter: blur(32px) !important;
    -webkit-backdrop-filter: blur(32px) !important;
    box-shadow: 0 14px 40px rgba(0, 0, 0, 0.06), inset 0 1px 2px #FFFFFF !important;
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
    padding: 6px 14px !important;
}

div[data-baseweb="input"]:focus-within {
    background-color: #FFFFFF !important;
    border-color: rgba(0, 102, 255, 0.40) !important;
    box-shadow: 0 20px 50px rgba(0, 102, 255, 0.12), 0 0 0 3px rgba(0, 102, 255, 0.10) !important;
    transform: translateY(-2px) !important;
}

div[data-baseweb="input"] input {
    color: var(--text-primary) !important;
    font-size: 17.5px !important;
    font-weight: 600 !important;
    padding: 16px 20px !important;
    line-height: 1.4 !important;
    opacity: 1 !important;
}

div[data-baseweb="input"] input::placeholder {
    color: var(--text-muted) !important;
    font-weight: 450 !important;
    opacity: 1 !important;
}

/* Button Styling — High Contrast Claymorphic */
.stButton > button {
    border-radius: var(--radius-full) !important;
    font-family: 'Plus Jakarta Sans', system-ui, sans-serif !important;
    font-weight: 700 !important;
    letter-spacing: -0.2px !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
}

/* Primary Action Button (Begin Research ↑) — High Contrast Dark Tactile */
.stButton > button[kind="primary"] {
    background: #1C1C1E !important;
    color: #FFFFFF !important;
    font-size: 16.5px !important;
    padding: 16px 36px !important;
    box-shadow: var(--clay-btn) !important;
    border: 1px solid rgba(255, 255, 255, 0.20) !important;
}

.stButton > button[kind="primary"] * {
    color: #FFFFFF !important;
    opacity: 1 !important;
    font-weight: 700 !important;
}

.stButton > button[kind="primary"]:hover {
    background: #2C2C2E !important;
    transform: translateY(-2px) !important;
    box-shadow: var(--clay-btn-hover), 0 0 16px rgba(0, 102, 255, 0.25) !important;
}

.stButton > button[kind="primary"]:hover * {
    color: #FFFFFF !important;
    opacity: 1 !important;
}

/* Secondary Button (Chips & Selectors) — High Contrast Light Surface */
.stButton > button[kind="secondary"] {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.90), rgba(255, 255, 255, 0.74)) !important;
    color: #1C1C1E !important;
    border: 1px solid rgba(0, 0, 0, 0.10) !important;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04), inset 0 1px 1px #FFFFFF !important;
    padding: 10px 20px !important;
    font-size: 13.5px !important;
    font-weight: 650 !important;
}

.stButton > button[kind="secondary"] * {
    color: #1C1C1E !important;
    opacity: 1 !important;
    font-weight: 650 !important;
}

.stButton > button[kind="secondary"]:hover {
    background: #FFFFFF !important;
    border-color: rgba(0, 102, 255, 0.40) !important;
    color: #0066FF !important;
    transform: translateY(-1px) !important;
    box-shadow: 0 6px 18px rgba(0, 102, 255, 0.12) !important;
}

.stButton > button[kind="secondary"]:hover * {
    color: #0066FF !important;
    opacity: 1 !important;
}

/* Active Depth Button (Disabled State styled as active indicator) */
.stButton > button:disabled {
    background: #0066FF !important;
    color: #FFFFFF !important;
    opacity: 1 !important;
    border: 1px solid #0066FF !important;
    box-shadow: 0 4px 14px rgba(0, 102, 255, 0.35) !important;
    cursor: default !important;
    font-weight: 750 !important;
    padding: 10px 20px !important;
    font-size: 13.5px !important;
}

.stButton > button:disabled * {
    color: #FFFFFF !important;
    opacity: 1 !important;
    font-weight: 750 !important;
}

/* 3-Tier Interactive Depth Cards */
.depth-cards-container {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 20px 0 16px 0;
}

.depth-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.88), rgba(255, 255, 255, 0.70));
    backdrop-filter: blur(28px) saturate(160%);
    -webkit-backdrop-filter: blur(28px) saturate(160%);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 24px;
    box-shadow: var(--clay-card);
    transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
    position: relative;
    text-align: left;
    min-height: 220px;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
}

.depth-card:hover {
    background: #FFFFFF;
    transform: translateY(-4px);
    box-shadow: var(--clay-card-hover);
    border-color: rgba(0, 0, 0, 0.12);
}

.depth-card.selected {
    background: #FFFFFF;
    border: 2px solid #0066FF !important;
    box-shadow: var(--clay-card-selected);
    transform: translateY(-2px);
}

.depth-badge-recommended {
    position: absolute;
    top: -12px;
    right: 18px;
    background: #0066FF;
    color: #FFFFFF;
    font-size: 10px;
    font-weight: 800;
    letter-spacing: 0.8px;
    padding: 4px 10px;
    border-radius: var(--radius-full);
    box-shadow: 0 4px 12px rgba(0, 102, 255, 0.35);
}

.depth-header-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 8px;
}

.depth-icon-title {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 16.5px;
    font-weight: 800;
    color: var(--text-primary) !important;
    letter-spacing: -0.3px;
}

.depth-tagline {
    font-size: 13.5px;
    font-weight: 700;
    color: var(--accent-blue) !important;
    margin-bottom: 8px;
}

.depth-card.selected .depth-tagline {
    color: #0066FF !important;
}

.depth-desc {
    font-size: 13.5px;
    color: var(--text-secondary) !important;
    line-height: 1.55;
    margin-bottom: 12px;
    opacity: 1 !important;
}

.depth-features-list {
    font-size: 12.5px;
    color: #3A3A3C !important;
    line-height: 1.65;
    border-top: 1px solid rgba(0, 0, 0, 0.08);
    padding-top: 10px;
    font-weight: 500;
}

.depth-check-icon {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: #0066FF;
    color: #FFFFFF;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 800;
    box-shadow: 0 2px 6px rgba(0, 102, 255, 0.35);
}

.depth-uncheck-icon {
    width: 22px;
    height: 22px;
    border-radius: 50%;
    background: rgba(0, 0, 0, 0.06);
    color: var(--text-muted);
    display: inline-flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
}

/* Active Research Session Banner */
.active-research-banner {
    display: flex;
    justify-content: space-between;
    align-items: center;
    flex-wrap: wrap;
    gap: 16px;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.76));
    backdrop-filter: blur(28px) saturate(160%);
    -webkit-backdrop-filter: blur(28px) saturate(160%);
    border: 1px solid var(--glass-border);
    border-left: 4px solid #1C1C1E;
    border-radius: var(--radius-lg);
    padding: 24px 32px;
    margin: 20px 0 24px 0;
    box-shadow: var(--clay-card);
}

.banner-sublabel {
    font-size: 12px;
    font-weight: 700;
    color: var(--text-muted) !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

.banner-headline {
    font-family: 'Newsreader', serif;
    font-size: 26px;
    font-weight: 700;
    color: var(--text-primary) !important;
    margin: 4px 0 0 0;
    line-height: 1.25;
}

.banner-status-badge {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    background: #E6F7F0;
    border: 1px solid #A7F3D0;
    padding: 6px 16px;
    border-radius: var(--radius-full);
}

.banner-pulse-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #047857;
    box-shadow: 0 0 0 4px rgba(4, 120, 87, 0.25);
    animation: gentlePulse 2s infinite ease-in-out;
}

.banner-status-text {
    font-size: 12px;
    font-weight: 750;
    color: #047857 !important;
    letter-spacing: 0.5px;
    text-transform: uppercase;
}

/* Clean Research Stage Journey (7 Stages) */
.stage-journey-panel {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.90), rgba(255, 255, 255, 0.74));
    backdrop-filter: blur(28px);
    -webkit-backdrop-filter: blur(28px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 22px 28px;
    box-shadow: var(--clay-card);
    margin-bottom: 24px;
}

.stage-journey-flow {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    position: relative;
}

.stage-journey-flow::before {
    content: '';
    position: absolute;
    top: 18px;
    left: 24px;
    right: 24px;
    height: 2px;
    background: rgba(0, 0, 0, 0.10);
    z-index: 1;
}

.stage-node-box {
    display: flex;
    flex-direction: column;
    align-items: center;
    position: relative;
    z-index: 2;
    text-align: center;
    max-width: 105px;
}

.stage-node-circle {
    width: 36px;
    height: 36px;
    border-radius: 50%;
    background: #FFFFFF;
    border: 2px solid rgba(0, 0, 0, 0.16);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 12px;
    font-weight: 750;
    color: var(--text-muted);
    transition: all 0.3s ease;
    margin-bottom: 8px;
}

.stage-node-box.active .stage-node-circle {
    background: #0066FF;
    border-color: #0066FF;
    color: #FFFFFF;
    box-shadow: 0 0 0 6px rgba(0, 102, 255, 0.20), 0 4px 12px rgba(0, 102, 255, 0.35);
    transform: scale(1.1);
}

.stage-node-box.done .stage-node-circle {
    background: #1C1C1E;
    border-color: #1C1C1E;
    color: #FFFFFF;
}

.stage-node-num {
    font-size: 11px;
    font-weight: 800;
    letter-spacing: 0.5px;
    color: var(--text-muted) !important;
    text-transform: uppercase;
}

.stage-node-name {
    font-size: 12px;
    font-weight: 650;
    color: #3A3A3C !important;
    line-height: 1.35;
    opacity: 1 !important;
}

.stage-node-box.active .stage-node-name {
    color: #0066FF !important;
    font-weight: 800;
}

.stage-node-box.done .stage-node-name {
    color: var(--text-primary) !important;
    font-weight: 700;
}

/* Live Activity Monitor — High Contrast Glass */
.live-activity-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.78));
    backdrop-filter: blur(28px) saturate(160%);
    -webkit-backdrop-filter: blur(28px) saturate(160%);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 24px 28px;
    box-shadow: var(--clay-card);
    margin: 20px 0;
}

.live-activity-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(0, 0, 0, 0.08);
    padding-bottom: 14px;
    margin-bottom: 16px;
}

.activity-status-tag {
    display: inline-flex;
    align-items: center;
    gap: 8px;
    font-size: 12.5px;
    font-weight: 750;
    color: var(--text-primary) !important;
    text-transform: uppercase;
    letter-spacing: 0.8px;
}

.activity-live-pulse {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: #0066FF;
    box-shadow: 0 0 0 4px rgba(0, 102, 255, 0.25);
    animation: gentlePulse 2s infinite ease-in-out;
}

@keyframes gentlePulse {
    0%, 100% { transform: scale(1); opacity: 1; }
    50% { transform: scale(1.2); opacity: 0.7; }
}

.activity-line {
    font-size: 14px;
    line-height: 1.9;
    color: #3A3A3C !important;
    display: flex;
    align-items: flex-start;
    gap: 12px;
    opacity: 1 !important;
}

.activity-line.active-line {
    color: var(--text-primary) !important;
    font-weight: 700;
}

.activity-time {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11.5px;
    font-weight: 600;
    color: var(--text-muted) !important;
    min-width: 44px;
}

.activity-cursor {
    display: inline-block;
    width: 7px;
    height: 14px;
    background: #0066FF;
    animation: cursorBlink 0.9s infinite;
    vertical-align: middle;
    margin-left: 6px;
}

@keyframes cursorBlink {
    0%, 100% { opacity: 1; }
    50% { opacity: 0; }
}

/* Floating Metrics Chips */
.metrics-row {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    margin: 20px 0;
}

.metric-glass-box {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.90), rgba(255, 255, 255, 0.74));
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    padding: 16px 20px;
    text-align: center;
    box-shadow: var(--clay-card);
}

.metric-glass-number {
    font-size: 32px;
    font-weight: 800;
    color: var(--text-primary) !important;
    line-height: 1;
    letter-spacing: -0.5px;
    margin-bottom: 6px;
}

.metric-glass-label {
    font-size: 12.5px;
    font-weight: 650;
    color: var(--text-secondary) !important;
    opacity: 1 !important;
}

/* Final Report Dossier View */
.report-header-panel {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.78));
    backdrop-filter: blur(28px);
    -webkit-backdrop-filter: blur(28px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 36px 40px;
    box-shadow: var(--clay-card);
    margin-top: 20px;
    margin-bottom: 24px;
}

.report-headline {
    font-family: 'Newsreader', serif;
    font-size: 42px;
    font-weight: 700;
    line-height: 1.18;
    color: var(--text-primary) !important;
    letter-spacing: -0.8px;
    margin-bottom: 12px;
}

.report-one-liner {
    font-size: 17px;
    color: #2C2C2E !important;
    line-height: 1.6;
    margin-bottom: 20px;
    max-width: 820px;
    font-weight: 500;
    opacity: 1 !important;
}

.meta-pills-row {
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
}

.meta-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.12);
    border-radius: var(--radius-full);
    padding: 5px 14px;
    font-size: 12.5px;
    font-weight: 650;
    color: var(--text-primary) !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.03);
}

/* Executive Summary Card */
.exec-summary-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.78));
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 28px 32px;
    box-shadow: var(--clay-card);
    margin-bottom: 24px;
}

/* Interactive Insight Card */
.insight-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.90), rgba(255, 255, 255, 0.74));
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    padding: 22px 26px;
    margin-bottom: 16px;
    box-shadow: var(--clay-card);
    transition: all 0.25s ease;
}

.insight-card:hover {
    background: #FFFFFF;
    transform: translateY(-2px);
    box-shadow: var(--clay-card-hover);
}

.insight-header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 10px;
}

.insight-index-num {
    font-family: 'Newsreader', serif;
    font-size: 28px;
    font-weight: 800;
    color: var(--text-primary) !important;
    margin-right: 14px;
}

/* Perspectives Section (Green, Yellow, Red Distinct Cards) */
.perspectives-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 16px;
    margin: 20px 0;
}

.perspective-col-card {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.92), rgba(255, 255, 255, 0.76));
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-md);
    padding: 22px;
    box-shadow: var(--clay-card);
    transition: all 0.25s ease;
}

.perspective-col-card:hover {
    transform: translateY(-2px);
    background: #FFFFFF;
}

.persp-badge-optimistic {
    color: #047857 !important;
    background: #E6F7F0;
    border: 1px solid #A7F3D0;
    padding: 4px 12px;
    border-radius: var(--radius-full);
    font-size: 12px;
    font-weight: 750;
}

.persp-badge-balanced {
    color: #92400E !important;
    background: #FEF3C7;
    border: 1px solid #FDE68A;
    padding: 4px 12px;
    border-radius: var(--radius-full);
    font-size: 12px;
    font-weight: 750;
}

.persp-badge-skeptical {
    color: #9F1239 !important;
    background: #FFE4E6;
    border: 1px solid #FECDD3;
    padding: 4px 12px;
    border-radius: var(--radius-full);
    font-size: 12px;
    font-weight: 750;
}

/* ==============================================================================
   TOP REPORT NAVIGATION FIX — Floating Glass Pill & Coral Glow Active State
   Targets Streamlit 1.63.0 React-Aria and BaseWeb tab components
   ============================================================================== */
div[data-testid="stTabs"] {
    margin-top: 24px !important;
}

/* The tab list bar container — Floating Glass Pill */
div[data-testid="stTabs"] [role="tablist"],
div[data-testid="stTabs"] .react-aria-TabList,
div[data-testid="stTabs"] [data-baseweb="tab-list"],
.stTabs [role="tablist"],
.stTabs .react-aria-TabList,
.react-aria-TabList {
    display: flex !important;
    justify-content: center !important;
    align-items: center !important;
    flex-wrap: wrap !important;
    gap: 8px !important;
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.98), rgba(255, 255, 255, 0.90)) !important;
    backdrop-filter: blur(28px) saturate(180%) !important;
    -webkit-backdrop-filter: blur(28px) saturate(180%) !important;
    border: 1px solid rgba(0, 0, 0, 0.09) !important;
    border-radius: var(--radius-full) !important;
    padding: 8px 18px !important;
    box-shadow: 0 6px 24px rgba(0, 0, 0, 0.07), inset 0 1px 1px #FFFFFF !important;
    max-width: 980px !important;
    margin: 0 auto 28px auto !important;
    position: relative !important;
    z-index: 5 !important;
}

/* Remove default grey underline across tablist */
div[data-testid="stTabs"] [role="tablist"]::after,
div[data-testid="stTabs"] .react-aria-TabList::after,
.stTabs [role="tablist"]::after,
.react-aria-TabList::after {
    display: none !important;
}

/* Individual Tab Items: Covers BOTH div and button, and data-testid="stTab" */
div[data-testid="stTabs"] [data-testid="stTab"],
div[data-testid="stTabs"] [role="tab"],
div[data-testid="stTabs"] div[role="tab"],
div[data-testid="stTabs"] button[role="tab"],
.stTabs [data-testid="stTab"],
.stTabs [role="tab"],
.react-aria-Tab {
    background: transparent !important;
    border: none !important;
    border-radius: var(--radius-full) !important;
    padding: 10px 18px !important;
    position: relative !important;
    transition: all 0.2s ease !important;
    cursor: pointer !important;
    color: #1C1C1E !important;
    -webkit-text-fill-color: #1C1C1E !important;
    opacity: 1 !important;
}

/* FORCE High-Contrast Dark Charcoal on EVERY child element inside every tab */
div[data-testid="stTabs"] [data-testid="stTab"] *,
div[data-testid="stTabs"] [role="tab"] *,
div[data-testid="stTabs"] div[role="tab"] *,
div[data-testid="stTabs"] button[role="tab"] *,
div[data-testid="stTabs"] [data-testid="stCaptionContainer"] *,
div[data-testid="stTabs"] [data-testid="stMarkdownContainer"] *,
div[data-testid="stTabs"] [data-testid="stMarkdownContainer"] p,
div[data-testid="stTabs"] [data-testid="stMarkdownContainer"] span,
.stTabs [data-testid="stTab"] *,
.stTabs [role="tab"] *,
.react-aria-Tab * {
    color: #1C1C1E !important;
    -webkit-text-fill-color: #1C1C1E !important;
    font-size: 14px !important;
    font-weight: 650 !important;
    opacity: 1 !important;
    letter-spacing: -0.2px !important;
}

/* Hover state */
div[data-testid="stTabs"] [data-testid="stTab"]:hover,
div[data-testid="stTabs"] [role="tab"]:hover,
.react-aria-Tab:hover {
    background: rgba(0, 0, 0, 0.05) !important;
}

div[data-testid="stTabs"] [data-testid="stTab"]:hover *,
div[data-testid="stTabs"] [role="tab"]:hover *,
.react-aria-Tab:hover * {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}

/* Active tab state */
div[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"],
div[data-testid="stTabs"] [role="tab"][aria-selected="true"],
div[data-testid="stTabs"] [data-testid="stTab"][data-selected],
div[data-testid="stTabs"] [data-testid="stTab"][data-selected="true"],
div[data-testid="stTabs"] [role="tab"][data-selected],
.react-aria-Tab[data-selected] {
    background: rgba(232, 93, 74, 0.08) !important;
    box-shadow: inset 0 0 0 1px rgba(232, 93, 74, 0.25), 0 2px 8px rgba(0, 0, 0, 0.04) !important;
}

/* Active tab text: Coral Text (#E85D4A) with Font-Weight 750 */
div[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"] *,
div[data-testid="stTabs"] [role="tab"][aria-selected="true"] *,
div[data-testid="stTabs"] [data-testid="stTab"][data-selected] *,
div[data-testid="stTabs"] [data-testid="stTab"][data-selected="true"] *,
div[data-testid="stTabs"] [role="tab"][data-selected] *,
.react-aria-Tab[data-selected] * {
    color: #E85D4A !important;
    -webkit-text-fill-color: #E85D4A !important;
    font-weight: 750 !important;
    opacity: 1 !important;
}

/* Active Coral Underline with Soft Glow */
div[data-testid="stTabs"] [data-testid="stTab"][aria-selected="true"]::after,
div[data-testid="stTabs"] [role="tab"][aria-selected="true"]::after,
.react-aria-Tab[data-selected]::after {
    content: '' !important;
    position: absolute !important;
    bottom: 3px !important;
    left: 18% !important;
    right: 18% !important;
    height: 3px !important;
    background: #E85D4A !important;
    border-radius: 9999px !important;
    box-shadow: 0 2px 8px rgba(232, 93, 74, 0.6) !important;
}

/* React-Aria Selection Indicator fallback */
div[data-testid="stTabs"] .react-aria-SelectionIndicator,
.stTabs .react-aria-SelectionIndicator,
[data-testid="stTab"] .react-aria-SelectionIndicator,
.react-aria-SelectionIndicator {
    background-color: #E85D4A !important;
    background: #E85D4A !important;
    height: 3px !important;
    border-radius: 9999px !important;
    box-shadow: 0 2px 8px rgba(232, 93, 74, 0.6) !important;
}

/* ==============================================================================
   DOWNLOAD PDF BUTTON FIX — High Contrast Dark Tactile Button with White Text
   ============================================================================== */
div[data-testid="stDownloadButton"] > button {
    background: #1C1C1E !important;
    color: #FFFFFF !important;
    border-radius: var(--radius-full) !important;
    padding: 16px 36px !important;
    font-size: 16px !important;
    font-weight: 700 !important;
    letter-spacing: -0.2px !important;
    border: 1px solid rgba(255, 255, 255, 0.20) !important;
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.20), inset 0 1px 1px rgba(255, 255, 255, 0.40) !important;
    transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
    cursor: pointer !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    margin: 20px auto !important;
    max-width: 480px !important;
}

div[data-testid="stDownloadButton"] > button * {
    color: #FFFFFF !important;
    opacity: 1 !important;
    font-weight: 700 !important;
    font-size: 16px !important;
}

div[data-testid="stDownloadButton"] > button:hover {
    background: #2C2C2E !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.28), 0 0 16px rgba(232, 93, 74, 0.35) !important;
}

div[data-testid="stDownloadButton"] > button:hover * {
    color: #FFFFFF !important;
    opacity: 1 !important;
}

/* Publication Report Paper */
.report-paper {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.94), rgba(255, 255, 255, 0.82));
    backdrop-filter: blur(28px);
    -webkit-backdrop-filter: blur(28px);
    border: 1px solid var(--glass-border);
    border-radius: var(--radius-lg);
    padding: 40px 48px;
    max-width: 900px;
    margin: 0 auto;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.08);
    line-height: 1.8;
    font-size: 15.5px;
    color: var(--text-primary);
}

.report-paper h1, .report-paper h2, .report-paper h3 {
    color: var(--text-primary) !important;
    letter-spacing: -0.4px;
    font-weight: 750;
    opacity: 1 !important;
}

.report-paper h1 {
    font-family: 'Newsreader', serif;
    font-size: 34px;
    font-weight: 600;
    border-bottom: 1px solid rgba(0, 0, 0, 0.10);
    padding-bottom: 14px;
    margin-bottom: 24px;
}

.report-paper h2 {
    font-size: 22px;
    margin-top: 36px;
    margin-bottom: 16px;
}

.report-paper h3 {
    font-size: 17px;
    margin-top: 24px;
    margin-bottom: 12px;
    color: #2C2C2E !important;
}

.report-paper p, .report-paper li {
    color: #2C2C2E !important;
    opacity: 1 !important;
}

.report-paper strong, .report-paper b {
    color: #1C1C1E !important;
    font-weight: 750;
}

/* ==============================================================================
   PROGRESSIVE DISCLOSURE — Clean Glass Evidence Accordion
   ============================================================================== */
details.glass-disclosure {
    background: linear-gradient(135deg, rgba(255, 255, 255, 0.94), rgba(255, 255, 255, 0.82));
    border: 1px solid rgba(0, 0, 0, 0.08);
    border-radius: var(--radius-md);
    padding: 16px 22px;
    margin-bottom: 14px;
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.03);
    transition: all 0.25s ease;
}

details.glass-disclosure[open] {
    background: #FFFFFF;
    border-color: rgba(0, 102, 255, 0.35);
    box-shadow: 0 8px 28px rgba(0, 102, 255, 0.08);
}

details.glass-disclosure summary {
    cursor: pointer;
    font-weight: 700;
    font-size: 15.5px;
    color: #1C1C1E;
    list-style: none;
    display: flex;
    justify-content: space-between;
    align-items: center;
    user-select: none;
}

details.glass-disclosure summary::-webkit-details-marker {
    display: none;
}

details.glass-disclosure summary .disclosure-btn {
    font-size: 12.5px;
    font-weight: 750;
    color: #0066FF;
    background: rgba(0, 102, 255, 0.08);
    border: 1px solid rgba(0, 102, 255, 0.25);
    padding: 5px 14px;
    border-radius: var(--radius-full);
    transition: all 0.2s ease;
    display: inline-flex;
    align-items: center;
    gap: 4px;
}

details.glass-disclosure[open] summary .disclosure-btn {
    background: #0066FF;
    color: #FFFFFF;
    border-color: #0066FF;
}

details.glass-disclosure .disclosure-body {
    margin-top: 14px;
    padding-top: 14px;
    border-top: 1px solid rgba(0, 0, 0, 0.07);
    font-size: 14px;
    color: #2C2C2E;
    line-height: 1.65;
}

/* ==============================================================================
   EXAMINER SYSTEM X-RAY VIEW — Technical Architecture Mode
   ============================================================================== */
.system-xray-panel {
    background: #0F172A;
    color: #F8FAFC;
    border-radius: var(--radius-lg);
    padding: 32px;
    margin: 24px 0;
    box-shadow: 0 16px 48px rgba(0, 0, 0, 0.25);
    border: 1px solid rgba(255, 255, 255, 0.10);
    font-family: 'Plus Jakarta Sans', sans-serif;
}

.system-xray-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    border-bottom: 1px solid rgba(255, 255, 255, 0.12);
    padding-bottom: 16px;
    margin-bottom: 24px;
    flex-wrap: wrap;
    gap: 12px;
}

.system-xray-title {
    font-size: 19px;
    font-weight: 800;
    color: #38BDF8;
    letter-spacing: -0.3px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.system-node-chain {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
    gap: 12px;
    margin-bottom: 24px;
}

.system-node-card {
    background: rgba(255, 255, 255, 0.04);
    border: 1px solid rgba(255, 255, 255, 0.09);
    border-radius: 12px;
    padding: 14px 18px;
    transition: all 0.2s ease;
}

.system-node-card:hover {
    background: rgba(255, 255, 255, 0.08);
    border-color: #38BDF8;
}

.system-node-step {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    color: #38BDF8;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    margin-bottom: 4px;
}

.system-node-name {
    font-size: 14.5px;
    font-weight: 750;
    color: #FFFFFF;
    margin-bottom: 4px;
}

.system-node-tech {
    font-size: 12px;
    color: #94A3B8;
    line-height: 1.45;
}

/* ==============================================================================
   WHY THIS IS DIFFERENT — Presentation Modal Styling
   ============================================================================== */
.why-diff-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin: 20px 0;
}

.why-diff-col {
    background: #FFFFFF;
    border: 1px solid rgba(0, 0, 0, 0.09);
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
}

.why-diff-col.highlight {
    border: 2px solid #0066FF;
    background: #FAFCFF;
    box-shadow: 0 8px 30px rgba(0, 102, 255, 0.10);
}

.why-diff-title {
    font-size: 16.5px;
    font-weight: 800;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    gap: 8px;
}

.why-step-pill {
    display: flex;
    align-items: center;
    gap: 8px;
    font-size: 13.5px;
    font-weight: 650;
    color: #1C1C1E;
    padding: 8px 12px;
    background: rgba(0, 0, 0, 0.03);
    border-radius: 8px;
    margin-bottom: 6px;
}

.why-step-pill.highlight {
    background: #EBF3FF;
    color: #0052CC;
    font-weight: 750;
    border: 1px solid #BFDBFE;
}

.why-punchline-box {
    background: #F0FDF4;
    border-left: 4px solid #047857;
    border-radius: 10px;
    padding: 16px 20px;
    margin-top: 16px;
    font-size: 14.5px;
    color: #064E3B;
    line-height: 1.6;
    font-weight: 600;
}
</style>"""


def inject_white_liquid_glass_theme():
    """Inject the design system into the Streamlit app session."""
    import streamlit as st
    st.markdown(WHITE_LIQUID_GLASS_CSS, unsafe_allow_html=True)
