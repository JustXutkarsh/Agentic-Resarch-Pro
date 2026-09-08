"""
Premium White Liquid Glass + Soft Claymorphism Design System for Agentic Research PRO.
Editorial aesthetic inspired by Apple Liquid Glass, warm grey tones, soft claymorphic depth,
and subtle neo-brutalist accents.
"""

WHITE_LIQUID_GLASS_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400&family=JetBrains+Mono:wght@400;500;600&display=swap');

    :root {
        --bg-base: #F7F6F3;
        --bg-secondary: #ECEAE6;
        --bg-warm: #F2EFE9;
        
        --surface-glass: rgba(255, 255, 255, 0.65);
        --surface-glass-hover: rgba(255, 255, 255, 0.85);
        --surface-solid: #FFFFFF;
        
        --glass-border: rgba(255, 255, 255, 0.85);
        --glass-border-subtle: rgba(0, 0, 0, 0.06);
        --glass-border-hover: rgba(0, 0, 0, 0.12);
        
        --text-primary: #1C1C1E;
        --text-secondary: #6E6E73;
        --text-muted: #8E8E93;
        --text-light: #AEAEB2;
        
        --accent-charcoal: #1C1C1E;
        --accent-charcoal-hover: #2C2C2E;
        --accent-sage: #4E6E5D;
        --accent-warm-blue: #3A5F7D;
        --accent-amber: #B45309;
        --accent-rose: #BE123C;

        --radius-sm: 10px;
        --radius-md: 16px;
        --radius-lg: 24px;
        --radius-full: 9999px;

        --clay-shadow: 0 8px 24px rgba(0, 0, 0, 0.04), 0 1px 3px rgba(0, 0, 0, 0.02), inset 0 1px 1px rgba(255, 255, 255, 0.95);
        --clay-shadow-hover: 0 12px 32px rgba(0, 0, 0, 0.07), 0 2px 6px rgba(0, 0, 0, 0.03), inset 0 1px 1px rgba(255, 255, 255, 1);
        --clay-shadow-pressed: inset 0 2px 4px rgba(0, 0, 0, 0.06), 0 1px 2px rgba(255, 255, 255, 0.8);
    }

    /* Base Body & App Canvas */
    .stApp {
        background-color: var(--bg-base) !important;
        background-image: 
            radial-gradient(circle at 12% 15%, rgba(235, 230, 245, 0.55) 0%, transparent 45%),
            radial-gradient(circle at 88% 18%, rgba(226, 236, 245, 0.60) 0%, transparent 40%),
            radial-gradient(circle at 50% 85%, rgba(245, 238, 230, 0.50) 0%, transparent 55%) !important;
        background-attachment: fixed !important;
        color: var(--text-primary) !important;
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'SF Pro Display', system-ui, sans-serif !important;
        letter-spacing: -0.015em;
    }

    /* Ambient Liquid Pastel Orbs */
    .ambient-liquid-layer {
        position: fixed;
        top: 0; left: 0; right: 0; bottom: 0;
        pointer-events: none;
        z-index: 0;
        background: 
            radial-gradient(circle at 25% 30%, rgba(240, 235, 248, 0.7) 0%, transparent 50%),
            radial-gradient(circle at 75% 65%, rgba(232, 242, 248, 0.6) 0%, transparent 50%);
        filter: blur(60px);
        animation: subtleDrift 30s ease-in-out infinite alternate;
    }

    @keyframes subtleDrift {
        0% { transform: scale(1) translate(0, 0); }
        50% { transform: scale(1.04) translate(-10px, 15px); }
        100% { transform: scale(1) translate(10px, -10px); }
    }

    /* Hide standard Streamlit header clutter */
    header[data-testid="stHeader"] {
        background: transparent !important;
    }

    /* Sidebar Glass Styling (Clean, Translucent Warm White) */
    section[data-testid="stSidebar"] {
        background-color: rgba(247, 246, 243, 0.75) !important;
        backdrop-filter: blur(28px) saturate(160%) !important;
        -webkit-backdrop-filter: blur(28px) saturate(160%) !important;
        border-right: 1px solid var(--glass-border-subtle) !important;
        color: var(--text-primary) !important;
    }

    /* Liquid Glass Panels */
    .glass-panel {
        background: var(--surface-glass);
        backdrop-filter: blur(28px) saturate(160%);
        -webkit-backdrop-filter: blur(28px) saturate(160%);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-lg);
        padding: 28px 32px;
        box-shadow: var(--clay-shadow);
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        margin-bottom: 24px;
    }

    .glass-panel:hover {
        background: var(--surface-glass-hover);
        box-shadow: var(--clay-shadow-hover);
    }

    .glass-card-compact {
        background: rgba(255, 255, 255, 0.55);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-md);
        padding: 18px 22px;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02), inset 0 1px 1px rgba(255, 255, 255, 0.9);
        transition: all 0.25s ease;
    }

    .glass-card-compact:hover {
        background: rgba(255, 255, 255, 0.80);
        transform: translateY(-2px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04), inset 0 1px 1px rgba(255, 255, 255, 1);
    }

    /* Floating Navigation Bar */
    .floating-nav {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(255, 255, 255, 0.65);
        backdrop-filter: blur(24px);
        -webkit-backdrop-filter: blur(24px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-full);
        padding: 10px 24px;
        margin: 8px auto 32px auto;
        max-width: 880px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.03), inset 0 1px 1px rgba(255, 255, 255, 0.95);
    }

    .nav-brand {
        display: flex;
        align-items: center;
        gap: 8px;
        font-weight: 700;
        font-size: 15px;
        color: var(--text-primary);
        letter-spacing: -0.3px;
    }

    .nav-pill {
        font-size: 12px;
        font-weight: 600;
        color: var(--text-secondary);
        background: rgba(0, 0, 0, 0.04);
        border-radius: var(--radius-full);
        padding: 4px 12px;
        border: 1px solid rgba(0, 0, 0, 0.03);
    }

    /* Editorial Hero Section */
    .hero-container {
        text-align: center;
        padding: 20px 0 28px 0;
        max-width: 760px;
        margin: 0 auto;
    }

    .hero-eyebrow {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        font-size: 12px;
        font-weight: 700;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 1px;
        background: rgba(255, 255, 255, 0.75);
        border: 1px solid rgba(0, 0, 0, 0.06);
        border-radius: var(--radius-full);
        padding: 5px 14px;
        margin-bottom: 20px;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02);
    }

    .hero-heading {
        font-family: 'Newsreader', serif;
        font-size: 56px;
        font-weight: 400;
        line-height: 1.12;
        letter-spacing: -1.2px;
        color: var(--text-primary);
        margin-bottom: 16px;
    }

    .hero-heading em {
        font-style: italic;
        font-weight: 400;
        color: #2D2D2F;
    }

    .hero-subheading {
        font-size: 17px;
        color: var(--text-secondary);
        line-height: 1.6;
        max-width: 580px;
        margin: 0 auto 32px auto;
        font-weight: 400;
    }

    /* Research Command Input Bar */
    div[data-baseweb="input"] {
        background-color: rgba(255, 255, 255, 0.75) !important;
        border: 1px solid rgba(255, 255, 255, 0.95) !important;
        border-radius: var(--radius-lg) !important;
        backdrop-filter: blur(28px) !important;
        -webkit-backdrop-filter: blur(28px) !important;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.04), inset 0 1px 2px rgba(255, 255, 255, 1) !important;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1) !important;
        padding: 4px 6px !important;
    }

    div[data-baseweb="input"]:focus-within {
        background-color: #FFFFFF !important;
        border-color: rgba(28, 28, 30, 0.25) !important;
        box-shadow: 0 16px 40px rgba(0, 0, 0, 0.08), 0 0 0 3px rgba(28, 28, 30, 0.04) !important;
        transform: translateY(-1px) !important;
    }

    div[data-baseweb="input"] input {
        color: var(--text-primary) !important;
        font-size: 16.5px !important;
        font-weight: 450 !important;
        padding: 16px 20px !important;
    }

    div[data-baseweb="input"] input::placeholder {
        color: var(--text-muted) !important;
        font-weight: 400 !important;
    }

    /* Segmented Tactile Depth Controller */
    div[data-testid="stRadio"] > label {
        display: none !important;
    }

    div[data-testid="stRadio"] > div {
        display: flex !important;
        flex-direction: row !important;
        gap: 12px !important;
        background: rgba(255, 255, 255, 0.45) !important;
        border: 1px solid rgba(255, 255, 255, 0.85) !important;
        border-radius: var(--radius-md) !important;
        padding: 6px !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        box-shadow: inset 0 1px 2px rgba(0, 0, 0, 0.03) !important;
        justify-content: space-between !important;
    }

    div[data-testid="stRadio"] label {
        flex: 1 !important;
        text-align: center !important;
        background: transparent !important;
        border-radius: 12px !important;
        padding: 10px 16px !important;
        color: var(--text-secondary) !important;
        cursor: pointer !important;
        font-weight: 600 !important;
        font-size: 13.5px !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        border: 1px solid transparent !important;
    }

    div[data-testid="stRadio"] label:hover {
        color: var(--text-primary) !important;
        background: rgba(255, 255, 255, 0.5) !important;
    }

    /* Hide standard radio dot circle */
    div[data-testid="stRadio"] div[role="radiogroup"] input[type="radio"] {
        display: none !important;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] > label > div:first-child {
        display: none !important;
    }

    /* Active Segment: Soft Pressed Clay Surface */
    div[data-testid="stRadio"] label:has(input:checked),
    div[data-testid="stRadio"] label[data-checked="true"] {
        background: #FFFFFF !important;
        color: var(--text-primary) !important;
        border: 1px solid rgba(0, 0, 0, 0.08) !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.06), inset 0 1px 1px rgba(255, 255, 255, 1) !important;
        transform: translateY(-1px) !important;
    }

    /* Depth Description Cards */
    .depth-preview-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 12px;
        margin: 14px 0 24px 0;
    }

    .depth-preview-card {
        background: rgba(255, 255, 255, 0.45);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-md);
        padding: 14px 16px;
        text-align: center;
        transition: all 0.25s ease;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.02);
    }

    .depth-preview-card.active {
        background: rgba(255, 255, 255, 0.85);
        border-color: rgba(28, 28, 30, 0.20);
        box-shadow: 0 6px 18px rgba(0, 0, 0, 0.05), inset 0 1px 1px #FFFFFF;
        transform: translateY(-1px);
    }

    .depth-preview-title {
        font-size: 13px;
        font-weight: 700;
        color: var(--text-primary);
        letter-spacing: -0.2px;
        margin-bottom: 4px;
    }

    .depth-preview-desc {
        font-size: 11.5px;
        color: var(--text-secondary);
        line-height: 1.4;
    }

    /* Primary Launch Button: Claymorphic Dark Charcoal Pill */
    .stButton > button {
        background: var(--accent-charcoal) !important;
        color: #FFFFFF !important;
        font-family: 'Inter', system-ui, sans-serif !important;
        font-size: 15.5px !important;
        font-weight: 600 !important;
        border-radius: var(--radius-full) !important;
        padding: 12px 32px !important;
        border: 1px solid rgba(255, 255, 255, 0.15) !important;
        box-shadow: 0 6px 20px rgba(28, 28, 30, 0.18), inset 0 1px 1px rgba(255, 255, 255, 0.25) !important;
        transition: all 0.25s cubic-bezier(0.16, 1, 0.3, 1) !important;
        letter-spacing: -0.2px !important;
    }

    .stButton > button:hover {
        background: var(--accent-charcoal-hover) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 10px 28px rgba(28, 28, 30, 0.26), inset 0 1px 1px rgba(255, 255, 255, 0.35) !important;
    }

    .stButton > button:active {
        transform: translateY(0px) !important;
        box-shadow: 0 3px 10px rgba(28, 28, 30, 0.15) !important;
    }

    /* Example Topic Chips */
    .example-chips-row {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        justify-content: center;
        margin-top: 14px;
    }

    .example-chip {
        display: inline-flex;
        align-items: center;
        background: rgba(255, 255, 255, 0.55);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-full);
        padding: 6px 14px;
        font-size: 12.5px;
        font-weight: 500;
        color: var(--text-secondary);
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02), inset 0 1px 1px rgba(255, 255, 255, 0.9);
        transition: all 0.2s ease;
        cursor: pointer;
        text-decoration: none;
    }

    .example-chip:hover {
        background: #FFFFFF;
        color: var(--text-primary);
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        border-color: rgba(0, 0, 0, 0.1);
    }

    /* Live Research Process: Warm White Glass Terminal */
    .live-terminal-panel {
        background: rgba(255, 255, 255, 0.75);
        backdrop-filter: blur(28px) saturate(160%);
        -webkit-backdrop-filter: blur(28px) saturate(160%);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-lg);
        padding: 24px 28px;
        box-shadow: var(--clay-shadow);
        margin: 20px 0;
        font-family: 'Inter', sans-serif;
    }

    .live-terminal-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-bottom: 14px;
        border-bottom: 1px solid rgba(0, 0, 0, 0.05);
        margin-bottom: 16px;
    }

    .live-indicator {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 11.5px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.8px;
        color: var(--text-primary);
    }

    .live-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #1C1C1E;
        box-shadow: 0 0 0 4px rgba(28, 28, 30, 0.12);
        animation: softPulse 2s infinite ease-in-out;
    }

    @keyframes softPulse {
        0%, 100% { transform: scale(1); opacity: 1; }
        50% { transform: scale(1.2); opacity: 0.7; }
    }

    .terminal-line {
        font-size: 13.5px;
        line-height: 1.85;
        color: var(--text-secondary);
        display: flex;
        align-items: flex-start;
        gap: 12px;
        animation: lineFadeIn 0.3s ease forwards;
    }

    @keyframes lineFadeIn {
        from { opacity: 0; transform: translateY(3px); }
        to { opacity: 1; transform: translateY(0); }
    }

    .line-time {
        font-family: 'JetBrains Mono', monospace;
        font-size: 11px;
        color: var(--text-muted);
        min-width: 44px;
        user-select: none;
    }

    .line-bullet {
        color: var(--text-primary);
        font-weight: 600;
        user-select: none;
    }

    .terminal-cursor {
        display: inline-block;
        width: 7px;
        height: 15px;
        background: var(--text-primary);
        animation: cursorBlink 1s infinite;
        vertical-align: middle;
        margin-left: 6px;
    }

    @keyframes cursorBlink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0; }
    }

    /* Live Progress Timeline */
    .timeline-track {
        display: flex;
        justify-content: space-between;
        align-items: center;
        position: relative;
        margin: 24px 0 16px 0;
        padding: 0 10px;
    }

    .timeline-track::before {
        content: '';
        position: absolute;
        top: 14px;
        left: 20px;
        right: 20px;
        height: 2px;
        background: rgba(0, 0, 0, 0.08);
        z-index: 1;
    }

    .timeline-step {
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
        z-index: 2;
        gap: 8px;
    }

    .timeline-node {
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: #FFFFFF;
        border: 2px solid rgba(0, 0, 0, 0.12);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 11px;
        font-weight: 700;
        color: var(--text-muted);
        transition: all 0.3s ease;
    }

    .timeline-step.active .timeline-node {
        background: #1C1C1E;
        border-color: #1C1C1E;
        color: #FFFFFF;
        box-shadow: 0 0 0 5px rgba(28, 28, 30, 0.12);
    }

    .timeline-step.done .timeline-node {
        background: #1C1C1E;
        border-color: #1C1C1E;
        color: #FFFFFF;
    }

    .timeline-label {
        font-size: 11.5px;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.4px;
    }

    .timeline-step.active .timeline-label {
        color: var(--text-primary);
        font-weight: 700;
    }

    /* Live Simple Metrics Row */
    .live-metric-card {
        background: rgba(255, 255, 255, 0.65);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-md);
        padding: 16px 20px;
        text-align: center;
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.02);
    }

    .live-metric-val {
        font-size: 28px;
        font-weight: 700;
        color: var(--text-primary);
        line-height: 1;
        margin-bottom: 4px;
        letter-spacing: -0.5px;
    }

    .live-metric-lbl {
        font-size: 12px;
        font-weight: 500;
        color: var(--text-secondary);
    }

    /* Editorial Result Dossier View */
    .editorial-title {
        font-family: 'Newsreader', serif;
        font-size: 40px;
        font-weight: 500;
        line-height: 1.2;
        letter-spacing: -0.8px;
        color: var(--text-primary);
        margin-bottom: 12px;
    }

    .editorial-paper {
        background: rgba(255, 255, 255, 0.70);
        backdrop-filter: blur(28px);
        -webkit-backdrop-filter: blur(28px);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-lg);
        padding: 40px 48px;
        max-width: 880px;
        margin: 0 auto;
        box-shadow: var(--clay-shadow);
        line-height: 1.75;
        font-size: 15.5px;
        color: #2D2D2F;
    }

    .editorial-paper h1, .editorial-paper h2, .editorial-paper h3 {
        color: var(--text-primary);
        letter-spacing: -0.4px;
        font-weight: 700;
    }

    .editorial-paper h1 {
        font-family: 'Newsreader', serif;
        font-size: 30px;
        font-weight: 500;
        border-bottom: 1px solid rgba(0, 0, 0, 0.08);
        padding-bottom: 14px;
        margin-bottom: 22px;
    }

    .editorial-paper h2 {
        font-size: 21px;
        margin-top: 32px;
        margin-bottom: 14px;
    }

    .editorial-paper h3 {
        font-size: 17px;
        margin-top: 24px;
        margin-bottom: 10px;
        color: var(--text-secondary);
    }

    /* Key Insights Numbered Cards */
    .insight-card {
        background: rgba(255, 255, 255, 0.65);
        border: 1px solid var(--glass-border);
        border-radius: var(--radius-md);
        padding: 20px 24px;
        margin-bottom: 14px;
        display: flex;
        gap: 20px;
        align-items: flex-start;
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.02);
        transition: all 0.25s ease;
    }

    .insight-card:hover {
        background: #FFFFFF;
        transform: translateY(-1px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.04);
    }

    .insight-number {
        font-family: 'Newsreader', serif;
        font-size: 26px;
        font-weight: 600;
        color: var(--text-primary);
        line-height: 1;
        min-width: 34px;
    }

    .insight-text {
        font-size: 14.5px;
        line-height: 1.6;
        color: #2C2C2E;
    }

    /* Neo-Brutalist Badges */
    .badge-subtle {
        display: inline-flex;
        align-items: center;
        gap: 5px;
        padding: 4px 12px;
        border-radius: var(--radius-full);
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.2px;
        border: 1px solid rgba(0, 0, 0, 0.08);
    }

    .badge-strongly-supported {
        background: rgba(78, 110, 93, 0.10);
        color: #2D503E;
        border-color: rgba(78, 110, 93, 0.25);
    }

    .badge-supported {
        background: rgba(78, 110, 93, 0.07);
        color: #3B5F4C;
        border-color: rgba(78, 110, 93, 0.20);
    }

    .badge-partially-supported {
        background: rgba(180, 83, 9, 0.08);
        color: #92400E;
        border-color: rgba(180, 83, 9, 0.20);
    }

    .badge-weakly-supported, .badge-unsupported {
        background: rgba(190, 18, 60, 0.08);
        color: #9F1239;
        border-color: rgba(190, 18, 60, 0.20);
    }

    /* Native Tabs Styled into Floating Glass Nav */
    div[data-testid="stTabs"] {
        background: transparent !important;
        margin-top: 18px;
    }

    div[data-testid="stTabs"] button[role="tab"] {
        background: rgba(255, 255, 255, 0.50) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: var(--radius-full) !important;
        color: var(--text-secondary) !important;
        padding: 8px 18px !important;
        font-weight: 600 !important;
        font-size: 13px !important;
        margin-right: 8px !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.02) !important;
    }

    div[data-testid="stTabs"] button[role="tab"]:hover {
        color: var(--text-primary) !important;
        background: rgba(255, 255, 255, 0.85) !important;
    }

    div[data-testid="stTabs"] button[role="tab"][aria-selected="true"] {
        background: #1C1C1E !important;
        border-color: #1C1C1E !important;
        color: #FFFFFF !important;
        box-shadow: 0 4px 14px rgba(28, 28, 30, 0.16) !important;
    }

    /* Custom Minimal Scrollbar */
    ::-webkit-scrollbar {
        width: 6px;
        height: 6px;
    }
    ::-webkit-scrollbar-track {
        background: transparent;
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(0, 0, 0, 0.15);
        border-radius: 10px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(0, 0, 0, 0.25);
    }
</style>
"""


def inject_white_liquid_glass_theme():
    """Inject the Warm White Liquid Glass design system into the Streamlit session."""
    import streamlit as st
    st.markdown(WHITE_LIQUID_GLASS_CSS, unsafe_allow_html=True)
