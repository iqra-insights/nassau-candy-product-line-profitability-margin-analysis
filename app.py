"""
Nassau Candy Distributor — Product Line Profitability & Margin Performance Analysis
Executive Business Intelligence dashboard (v4 — modern SaaS-style shell, same analytics engine).
 
Run:  streamlit run app.py
"""
 
import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from pathlib import Path
 
# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="Nassau Candy | Executive Profitability Dashboard",
    page_icon="🍫",
    layout="wide",
    initial_sidebar_state="expanded",
)
 
# ============================================================================
# SESSION STATE
# ============================================================================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False
if "page" not in st.session_state:
    st.session_state.page = "Executive Overview"
if "reset_ctr" not in st.session_state:
    st.session_state.reset_ctr = 0
if "last_refresh" not in st.session_state:
    st.session_state.last_refresh = datetime.now()
 
DARK = st.session_state.dark_mode
 
# ============================================================================
# THEME — palette switches with dark/light toggle
# ============================================================================
if DARK:
    PAGE_BG = "#0F1729"; CARD_BG = "#1A2338"; SIDEBAR_BG = "#141B2D"
    TEXT_DARK = "#F3F4F6"; TEXT_MUTED = "#9CA3AF"; BORDER = "#2A3550"
    NAVY = "#3A5A8C"; NAVY_DARK = "#0E1730"; GOLD = "#D4AF6A"
    GOOD = "#34D399"; WARN = "#FBBF24"; RISK = "#F87171"
    BLUE_BG, BLUE_FG = "#1E3A5F", "#7CB2FF"
    GREEN_BG, GREEN_FG = "#123B2C", "#4ADE94"
    PURPLE_BG, PURPLE_FG = "#2C1F4A", "#B79CF9"
    ORANGE_BG, ORANGE_FG = "#3A2712", "#FDBA74"
    TEAL_BG, TEAL_FG = "#0E3438", "#5EEAD4"
else:
    PAGE_BG = "#F4F5F9"; CARD_BG = "#FFFFFF"; SIDEBAR_BG = "#FFFFFF"
    TEXT_DARK = "#111827"; TEXT_MUTED = "#6B7280"; BORDER = "#E5E7EB"
    NAVY = "#1F3864"; NAVY_DARK = "#152747"; GOLD = "#A9812D"
    GOOD = "#16A34A"; WARN = "#D97706"; RISK = "#DC2626"
    BLUE_BG, BLUE_FG = "#EFF6FF", "#2563EB"
    GREEN_BG, GREEN_FG = "#ECFDF5", "#059669"
    PURPLE_BG, PURPLE_FG = "#F5F3FF", "#7C3AED"
    ORANGE_BG, ORANGE_FG = "#FFF7ED", "#EA580C"
    TEAL_BG, TEAL_FG = "#ECFEFF", "#0891B2"
 
CHART_SEQ = [NAVY, GOLD, "#4A6B8A", RISK, "#6B7D5E"]
 
CUSTOM_CSS = f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Merriweather:wght@400;700&family=Source+Sans+Pro:wght@400;500;600;700;800&display=swap');
    @import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css');
 
    html, body, [class*="css"] {{ font-family: 'Source Sans Pro', 'Segoe UI', Calibri, Arial, sans-serif; }}
    h1, h2, h3, .hero-title, .section-title, .page-head-title {{ font-family: 'Merriweather', Georgia, serif; }}
 
    .stApp {{ background-color: {PAGE_BG}; }} [data-testid="stAppViewContainer"] {{ background-color: {PAGE_BG} !important; }}
    /* The sidebar is now permanently open — no collapse/expand toggle at
       all. A collapse button is a one-way trap in some Streamlit versions
       (the browser remembers "collapsed" and won't reliably reopen it),
       so removing the button removes that whole failure mode instead of
       chasing it version by version. */
    header[data-testid="stHeader"] {{ background: transparent !important; height: 2.75rem; }}
    div[data-testid="stToolbar"] {{ visibility: hidden !important; }}
    #MainMenu {{ visibility: hidden !important; }}
    footer {{ visibility: hidden !important; }}
    [data-testid="stSidebarCollapsedControl"],
    [data-testid="collapsedControl"],
    button[kind="header"] {{
        display: none !important;
    }}
    /* Force the sidebar itself to always render open, regardless of any
       collapsed state the browser may have cached from earlier clicks. */
    section[data-testid="stSidebar"] {{
        transform: none !important;
        visibility: visible !important;
    }}
    section[data-testid="stSidebar"][aria-expanded="false"] {{ transform: none !important; }}
    .block-container {{ padding-top: 3.25rem !important; padding-bottom: 2.5rem !important; max-width: 1540px !important; }}
    [data-testid="stAppViewContainer"] > .main {{ background: {PAGE_BG} !important; }}
    .main .block-container {{ margin-left: auto; margin-right: auto; }}
 
    /* ---- sidebar / filter panel ---- */
    section[data-testid="stSidebar"] {{ background-color: {SIDEBAR_BG} !important; border-right: 1px solid {BORDER}; min-width: 290px !important; max-width: 290px !important; }}
    section[data-testid="stSidebar"] > div {{ padding: 1.15rem 1.05rem 1.5rem 1.05rem !important; }}
    /* Streamlit reserves extra top space inside the sidebar for its own
       collapse-button row, even with that button hidden. Zero it out on
       every wrapper level that might be holding it, so the filters start
       right under the top bar instead of ~130px further down. */
    div[data-testid="stSidebarUserContent"],
    div[data-testid="stSidebarContent"],
    section[data-testid="stSidebar"] > div:first-child {{
        padding-top: 0.25rem !important; margin-top: 0 !important;
    }}
    /* The empty header row that used to hold the collapse button/logo slot
       still reserves its own height even once the button inside it is
       display:none — collapse the row itself, not just its contents. */
    div[data-testid="stSidebarHeader"] {{
        display: none !important; height: 0 !important; min-height: 0 !important;
        padding: 0 !important; margin: 0 !important;
    }}
    section[data-testid="stSidebar"] .stMarkdown {{ margin-bottom: 0.15rem; }}
    section[data-testid="stSidebar"] * {{ color: {TEXT_DARK} !important; }}
    section[data-testid="stSidebar"] .stMarkdown p {{ color: {TEXT_MUTED} !important; }}
    section[data-testid="stSidebar"] hr {{ border-color: {BORDER}; margin: 12px 0; }}
    .filter-label {{ font-size: 12px; font-weight: 700; color: {TEXT_DARK} !important; margin: 12px 0 6px 0; }}
    .filter-label i {{ color: {NAVY}; margin-right: 6px; width: 14px; }}
    .side-section-label {{
        font-size: 10.5px; font-weight: 800; color: {NAVY} !important; text-transform: uppercase;
        letter-spacing: 0.9px; margin: 2px 0 10px 0;
    }}
    .side-section-label i {{ margin-right: 6px; }}
    .about-card {{
        background: {"#141F35" if DARK else "#F0F4FA"}; border: 1px solid {BORDER}; border-radius: 10px;
        padding: 12px 14px; font-size: 11.5px; color: {TEXT_MUTED} !important; line-height: 1.5; margin-top: 16px;
    }}
    .about-card i {{ color: {NAVY}; margin-right: 5px; }}
 
    section[data-testid="stSidebar"] div[data-testid="stDateInput"] input,
    section[data-testid="stSidebar"] div[data-testid="stTextInput"] input {{
        background: {CARD_BG} !important; color: {TEXT_DARK} !important;
        border: 1px solid {BORDER} !important; border-radius: 8px !important;
    }}
    section[data-testid="stSidebar"] div[data-baseweb="select"] > div {{
        background: {CARD_BG} !important; border: 1px solid {BORDER} !important; color: {TEXT_DARK} !important;
        border-radius: 8px !important;
    }}
    section[data-testid="stSidebar"] span[data-baseweb="tag"] {{
        background-color: {NAVY} !important; color: #FFFFFF !important; border-radius: 6px !important;
    }}
    section[data-testid="stSidebar"] div[data-baseweb="slider"] div[role="slider"] {{
        background-color: {NAVY} !important; border-color: {NAVY} !important;
    }}
    section[data-testid="stSidebar"] div[data-baseweb="slider"] > div > div {{ background-color: {NAVY} !important; }}
    div[data-baseweb="popover"], div[data-baseweb="calendar"], ul[data-baseweb="menu"] {{ background: {CARD_BG} !important; }}
    li[data-baseweb="menu-item"] {{ background: {CARD_BG} !important; color: {TEXT_DARK} !important; }}
    li[data-baseweb="menu-item"]:hover {{ background: {PAGE_BG} !important; }}
 
    .st-key-actions_container .stButton > button, .st-key-actions_container div[data-testid="stDownloadButton"] > button {{
        background: {CARD_BG} !important; color: {NAVY} !important; border: 1px solid {NAVY} !important;
        font-weight: 600; font-size: 12.5px; border-radius: 8px !important; box-shadow: none !important;
    }}
    .st-key-actions_container .stButton > button:hover, .st-key-actions_container div[data-testid="stDownloadButton"] > button:hover {{
        background: {NAVY} !important; color: #FFFFFF !important;
    }}
 
    /* ---- top bar ---- */
    .st-key-topbar {{
        background: linear-gradient(135deg, {NAVY_DARK}, {NAVY});
        border-radius: 16px; padding: 14px 26px; margin-bottom: 18px;
        box-shadow: 0 3px 10px rgba(0,0,0,0.18);
    }}
    .st-key-topbar div[data-testid="stVerticalBlockBorderWrapper"] {{ background: transparent; }}
    .topbar-brand-title {{ color:#FFFFFF; font-size:16px; font-weight:800; font-family:'Merriweather',Georgia,serif; margin:0; letter-spacing:0.3px; }}
    .topbar-brand-sub {{ color:#B9C4DA; font-size:11px; margin-top:1px; }}
    .st-key-topbar .stButton > button {{
        background: rgba(255,255,255,0.10) !important; color:#FFFFFF !important; border:1px solid rgba(255,255,255,0.18) !important;
        border-radius: 20px !important; font-size:12.5px !important; font-weight:600 !important; box-shadow:none !important;
    }}
    .st-key-topbar .stButton > button:hover {{ background: rgba(255,255,255,0.22) !important; }}
    .st-key-topbar div[data-testid="stDownloadButton"] > button {{
        background: #FFFFFF !important; color:{NAVY} !important; border:none !important;
        border-radius: 20px !important; font-size:12.5px !important; font-weight:700 !important; box-shadow:none !important;
    }}
 
    /* ---- page header (title + meta) ---- */
    .page-title-row {{ display:flex; justify-content:space-between; align-items:flex-start; margin: 4px 0 10px 0; }}
    .hero-title {{ color: {TEXT_DARK}; font-size: 27px; font-weight: 800; margin: 0; letter-spacing: 0.1px; }}
    .hero-sub {{ color: {NAVY}; font-size: 14px; font-weight: 700; margin-top: 4px; }}
    .hero-tag {{ color: {TEXT_MUTED}; font-size: 12.5px; margin-top: 6px; }}
    .last-updated {{ color: {TEXT_MUTED}; font-size: 11px; text-align:right; white-space:nowrap; }}
    .last-updated i {{ margin-left: 6px; color: {NAVY}; }}
    .hero-meta {{
        background: {CARD_BG}; border: 1px solid {BORDER}; border-radius: 10px;
        color: {TEXT_MUTED}; font-size: 11.5px; font-weight: 500; margin: 12px 0 14px 0;
        letter-spacing: 0.2px; padding: 10px 16px; box-shadow: 0 1px 5px rgba(15,23,42,0.03);
    }}
    .hero-meta b {{ color: {TEXT_DARK}; }}
 
    /* ---- pill navigation ---- */
    .st-key-nav_shell {{
        background: {CARD_BG}; border: 1px solid {BORDER}; border-radius: 14px;
        padding: 8px; margin-bottom: 18px; box-shadow: 0 1px 5px rgba(0,0,0,0.05);
    }}
    .st-key-nav_shell .stButton > button {{
        border-radius: 22px !important; padding: 9px 12px !important; font-size: 11.5px !important;
        font-weight: 600 !important; background: transparent !important; color: {TEXT_MUTED} !important;
        border: 1px solid transparent !important; box-shadow: none !important;
    }}
    .st-key-nav_shell .stButton > button:hover {{ background: {PAGE_BG} !important; color: {NAVY} !important; }}
    .st-key-nav_shell .stButton > button[kind="primary"] {{
        background: {NAVY} !important; color: #FFFFFF !important; border-color: {NAVY} !important;
        box-shadow: 0 2px 6px rgba(31,56,100,0.30) !important;
    }}
 
    /* ---- page-level title block for sub-pages ---- */
    .page-head {{ margin: 2px 0 16px 0; }}
    .page-head-title {{ font-size: 20px; font-weight: 800; color: {TEXT_DARK}; }}
    .page-head-desc {{ font-size: 12.5px; color: {TEXT_MUTED}; margin-top: 3px; }}
 
    /* ---- KPI cards (icon-badge style) ---- */
    .kpi-card2 {{
        background: {CARD_BG}; border: 1px solid {BORDER}; border-radius: 14px;
        padding: 16px 18px; min-height: 132px; height: 100%; box-sizing: border-box;
        box-shadow: 0 2px 10px rgba(15,23,42,0.045); transition: transform .18s ease, box-shadow .18s ease;
    }}
    .kpi-card2:hover {{ transform: translateY(-2px); box-shadow: 0 7px 18px rgba(15,23,42,0.09); }}
    .kpi-icon-badge {{
        width: 36px; height: 36px; border-radius: 10px; display: flex; align-items: center;
        justify-content: center; font-size: 15px; margin-bottom: 10px;
    }}
    .kpi-label2 {{ font-size: 11px; font-weight: 700; color: {TEXT_MUTED}; text-transform: uppercase; letter-spacing: 0.5px; }}
    .kpi-value2 {{ font-size: 22px; font-weight: 800; color: {TEXT_DARK}; margin-top: 3px; font-family: 'Merriweather', Georgia, serif; }}
    .kpi-sub2 {{ font-size: 10.5px; color: {TEXT_MUTED}; margin-top: 2px; }}
    .trend-up {{ color: {GOOD}; font-size: 11px; font-weight: 700; margin-top: 5px; display:inline-block; }}
    .trend-down {{ color: {RISK}; font-size: 11px; font-weight: 700; margin-top: 5px; display:inline-block; }}
    .trend-flat {{ color: {TEXT_MUTED}; font-size: 11px; font-weight: 600; margin-top: 5px; display:inline-block; }}
 
    /* ---- insight cards (icon-badge style) ---- */
    .insight-card2 {{
        background: {CARD_BG}; border: 1px solid {BORDER}; border-left: 4px solid {NAVY};
        border-radius: 10px; padding: 13px 15px; min-height: 92px; height: 100%; box-sizing: border-box;
        box-shadow: 0 2px 9px rgba(15,23,42,0.04);
    }}
    .insight-card2.good {{ border-left-color: {GOOD}; }}
    .insight-card2.warn {{ border-left-color: {WARN}; }}
    .insight-card2.risk {{ border-left-color: {RISK}; }}
    .insight-icon {{ font-size: 13px; margin-right: 6px; }}
    .insight-label2 {{ font-size: 10.5px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.4px; color: {TEXT_MUTED}; }}
    .insight-value2 {{ font-size: 13.5px; font-weight: 700; color: {TEXT_DARK}; margin-top: 5px; line-height: 1.3; }}
    .insight-sub2 {{ font-size: 11.5px; color: {TEXT_MUTED}; margin-top: 3px; }}
 
    /* ---- generic section cards ---- */
    .section-card {{ background: {CARD_BG}; border: 1px solid {BORDER}; border-radius: 14px; padding: 17px 20px; margin-bottom: 16px; box-shadow: 0 2px 10px rgba(15,23,42,0.045); }}
    .section-title {{ color: {TEXT_DARK}; font-size: 15.5px; font-weight: 700; margin-bottom: 2px; }}
    .section-title i {{ color: {NAVY}; margin-right: 7px; }}
    .section-caption {{ color: {TEXT_MUTED}; font-size: 12px; margin: 6px 0 12px 0; }}
 
    .badge {{ display: inline-block; padding: 2px 9px; border-radius: 20px; font-size: 10.5px; font-weight: 700; border: 1px solid; }}
    .badge-healthy {{ background: {GREEN_BG}; color: {GOOD}; border-color: {GOOD}; }}
    .badge-watchlist {{ background: {ORANGE_BG}; color: {WARN}; border-color: {WARN}; }}
    .badge-risk {{ background: {"#3A1414" if DARK else "#F5EAEA"}; color: {RISK}; border-color: {RISK}; }}
 
    .pri-high {{ background:{"#3A1414" if DARK else "#F5EAEA"}; color:{RISK}; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; border:1px solid {RISK}; letter-spacing:0.4px; }}
    .pri-med  {{ background:{ORANGE_BG}; color:{WARN}; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; border:1px solid {WARN}; letter-spacing:0.4px; }}
    .pri-mon  {{ background:{GREEN_BG}; color:{GOOD}; padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; border:1px solid {GOOD}; letter-spacing:0.4px; }}
 
    .rec-block {{ background: {CARD_BG}; border: 1px solid {BORDER}; border-left: 4px solid; border-radius: 10px; padding: 15px 19px; margin-bottom: 12px; line-height: 1.6; font-size: 13.5px; box-shadow: 0 1px 6px rgba(0,0,0,0.05); }}
    .quad-card {{ border-radius: 12px; padding: 15px 17px; height: 100%; border: 1px solid {BORDER}; background: {CARD_BG}; box-shadow: 0 1px 6px rgba(0,0,0,0.05); }}
 
    /* ---- bottom stat strip ---- */
    .stat-pill {{ display:flex; align-items:center; gap:10px; background:{CARD_BG}; border:1px solid {BORDER}; border-radius:12px; padding:10px 14px; box-shadow:0 1px 5px rgba(0,0,0,0.04); }}
    .stat-icon {{ width:32px; height:32px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:13px; flex-shrink:0; }}
    .stat-value {{ font-size:15px; font-weight:800; color:{TEXT_DARK}; line-height:1.1; }}
    .stat-label {{ font-size:10.5px; color:{TEXT_MUTED}; }}
    .stability-strip {{ background:{CARD_BG}; border:1px solid {BORDER}; border-left:4px solid {NAVY}; border-radius:12px; padding:10px 14px; min-height:58px; box-sizing:border-box; }}
    .stability-title {{ color:{TEXT_DARK}; font-size:12px; font-weight:800; }}
    .stability-title i {{ color:{NAVY}; margin-right:6px; }}
    .stability-desc {{ color:{TEXT_MUTED}; font-size:10.5px; margin-top:4px; }}
 
    /* ---- small icon-only controls above charts ---- */
    .st-key-chart_ctrl div[data-testid="stDownloadButton"] > button {{
        background: {PAGE_BG} !important; color: {TEXT_MUTED} !important; border: 1px solid {BORDER} !important;
        border-radius: 8px !important; font-size: 11px !important; padding: 4px 10px !important; box-shadow:none !important;
    }}
 
    div[data-testid="stDataFrame"] {{ border: 1px solid {BORDER}; border-radius: 10px; }}
    hr {{ border-color: {BORDER}; }}
 
    /* ---- responsive polish ---- */
    @media (max-width: 1100px) {{
        section[data-testid="stSidebar"] {{ min-width: 260px !important; max-width: 260px !important; }}
        .hero-title {{ font-size: 24px; }}
        .kpi-value2 {{ font-size: 20px; }}
    }}
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
 
# ============================================================================
# STATIC REFERENCE DATA
# ============================================================================
FACTORY_MAP = {
    "Wonka Bar - Nutty Crunch Surprise": "Lot's O' Nuts",
    "Wonka Bar - Fudge Mallows": "Lot's O' Nuts",
    "Wonka Bar -Scrumdiddlyumptious": "Lot's O' Nuts",
    "Wonka Bar - Milk Chocolate": "Wicked Choccy's",
    "Wonka Bar - Triple Dazzle Caramel": "Wicked Choccy's",
    "Laffy Taffy": "Sugar Shack", "SweeTARTS": "Sugar Shack", "Nerds": "Sugar Shack",
    "Fun Dip": "Sugar Shack", "Fizzy Lifting Drinks": "Sugar Shack",
    "Everlasting Gobstopper": "Secret Factory", "Hair Toffee": "The Other Factory",
    "Lickable Wallpaper": "Secret Factory", "Wonka Gum": "Secret Factory", "Kazookles": "The Other Factory",
}
FACTORY_COORDS = {
    "Lot's O' Nuts": (32.881893, -111.768036), "Wicked Choccy's": (32.076176, -81.088371),
    "Sugar Shack": (48.11914, -96.18115), "Secret Factory": (41.446333, -90.565487),
    "The Other Factory": (35.1175, -89.971107),
}
 
# ============================================================================
# DATA LOADING
# ============================================================================
@st.cache_data
def load_data(path: str = "nassau_candy_cleaned.csv") -> pd.DataFrame:
    # Resolve the dataset relative to app.py so the dashboard works even when
    # Streamlit is launched from another working directory.
    data_path = Path(path)
    if not data_path.is_absolute():
        data_path = Path(__file__).resolve().parent / data_path
    if not data_path.exists():
        # Also support the recommended data/ folder layout.
        alt_path = Path(__file__).resolve().parent / "data" / data_path.name
        if alt_path.exists():
            data_path = alt_path
    if not data_path.exists():
        raise FileNotFoundError(f"Dataset not found: {data_path}. Place nassau_candy_cleaned.csv beside app.py or inside the data folder.")
    df = pd.read_csv(data_path)
    df = df.dropna()
    df = df.drop_duplicates()
    df = df[(df["Sales"] > 0) & (df["Units"] > 0)]
    df = df[(df["Sales"] - df["Cost"] - df["Gross Profit"]).abs() <= 0.02]
    df["Order Date"] = pd.to_datetime(df["Order Date"], format="%d-%m-%Y", errors="coerce")
    df["Ship Date"] = pd.to_datetime(df["Ship Date"], format="%d-%m-%Y", errors="coerce")
    df = df.dropna(subset=["Order Date"])
    # .fillna("Unmapped") instead of leaving NaN: a NaN Factory value would
    # silently vanish from every Factory-grouped table/chart (pandas drops
    # NaN groupby keys by default) while still counting in Sales/Gross Profit
    # totals elsewhere. "Unmapped" keeps the product visible instead of
    # hiding a data-catalog gap.
    df["Factory"] = df["Product Name"].map(FACTORY_MAP).fillna("Unmapped")
    df["Factory_Lat"] = df["Factory"].map(lambda x: FACTORY_COORDS.get(x, (np.nan, np.nan))[0])
    df["Factory_Lon"] = df["Factory"].map(lambda x: FACTORY_COORDS.get(x, (np.nan, np.nan))[1])
    df["Txn_Margin_%"] = np.where(df["Sales"] > 0, df["Gross Profit"] / df["Sales"] * 100, 0)
    return df
 
 
# ============================================================================
# HELPERS
# ============================================================================
def safe_div(numerator, denominator):
    numerator = np.asarray(numerator, dtype=float)
    denominator = np.asarray(denominator, dtype=float)
    return np.divide(numerator, denominator, out=np.zeros_like(numerator, dtype=float), where=denominator != 0)
 
 
def fmt_currency0(x: float) -> str:
    return f"${x:,.0f}"
 
 
def fmt_pct(x: float) -> str:
    return f"{x:,.2f}%"
 
 
def risk_status(margin: float, threshold: float) -> str:
    if margin < threshold:
        return "High Margin Risk"
    elif margin < threshold + 15:
        return "Watchlist"
    return "Healthy"
 
 
def classify_quadrant(row, median_sales, median_margin):
    high_sales = row["Sales"] >= median_sales
    high_margin = row["Margin_%"] >= median_margin
    if high_sales and high_margin:
        return "Profit Stars"
    elif high_sales and not high_margin:
        return "Revenue Heavyweights"
    elif not high_sales and high_margin:
        return "Growth Opportunities"
    else:
        return "Portfolio Review"
 
 
QUADRANT_COLORS = {
    "Profit Stars": GOOD, "Revenue Heavyweights": WARN,
    "Growth Opportunities": "#4A6B8A", "Portfolio Review": RISK,
}
 
 
def style_fig(fig, height=380):
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Source Sans Pro, sans-serif", color=TEXT_DARK, size=12),
        margin=dict(l=10, r=10, t=40, b=10), height=height,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
    )
    fig.update_xaxes(showgrid=False, zeroline=False)
    fig.update_yaxes(showgrid=True, gridcolor=BORDER, zeroline=False)
    return fig
 
 
def trend_html(curr, prev, is_pp=False):
    """Computed vs-previous-period indicator. Never fabricated — returns a flat state when no prior data exists."""
    if prev is None or (not is_pp and prev == 0):
        return '<span class="trend-flat"><i class="fa-solid fa-minus"></i> vs PY: n/a</span>'
    if is_pp:
        delta = curr - prev
        cls = "trend-up" if delta >= 0 else "trend-down"
        arrow = "fa-arrow-up" if delta >= 0 else "fa-arrow-down"
        return f'<span class="{cls}"><i class="fa-solid {arrow}"></i> {abs(delta):.1f} pp vs PY</span>'
    change = (curr - prev) / prev * 100
    cls = "trend-up" if change >= 0 else "trend-down"
    arrow = "fa-arrow-up" if change >= 0 else "fa-arrow-down"
    return f'<span class="{cls}"><i class="fa-solid {arrow}"></i> {abs(change):.1f}% vs PY</span>'
 
 
def kpi_card2(col, icon, icon_bg, icon_fg, label, value, sub, trend=None):
    trend_block = trend if trend else ""
    col.markdown(
        f"""<div class="kpi-card2">
        <div class="kpi-icon-badge" style="background:{icon_bg}; color:{icon_fg};"><i class="fa-solid {icon}"></i></div>
        <div class="kpi-label2">{label}</div>
        <div class="kpi-value2">{value}</div>
        <div class="kpi-sub2">{sub}</div>
        {trend_block}
        </div>""",
        unsafe_allow_html=True,
    )
 
 
def insight_card2(col, icon, tone, label, value, sub):
    col.markdown(
        f"""<div class="insight-card2 {tone}">
        <div class="insight-label2"><i class="fa-solid {icon} insight-icon"></i>{label}</div>
        <div class="insight-value2">{value}</div>
        <div class="insight-sub2">{sub}</div>
        </div>""",
        unsafe_allow_html=True,
    )
 
 
def section_header(title, caption=None, icon=None):
    icon_html = f'<i class="fa-solid {icon}"></i>' if icon else ""
    cap = f'<div class="section-caption">{caption}</div>' if caption else ""
    st.markdown(f'<div class="section-card"><div class="section-title">{icon_html}{title}</div>{cap}', unsafe_allow_html=True)
 
 
def section_close():
    st.markdown("</div>", unsafe_allow_html=True)
 
 
def page_header(title, desc):
    st.markdown(
        f'<div class="page-head"><div class="page-head-title">{title}</div>'
        f'<div class="page-head-desc">{desc}</div></div>',
        unsafe_allow_html=True,
    )
 
 
def stat_pill(col, icon, icon_bg, icon_fg, value, label):
    col.markdown(
        f"""<div class="stat-pill">
        <div class="stat-icon" style="background:{icon_bg}; color:{icon_fg};"><i class="fa-solid {icon}"></i></div>
        <div><div class="stat-value">{value}</div><div class="stat-label">{label}</div></div>
        </div>""",
        unsafe_allow_html=True,
    )
 
 
# ============================================================================
# LOAD DATA
# ============================================================================
try:
    raw_df = load_data()
except FileNotFoundError as e:
    st.error(
        f"🍫 **Dataset not found.**\n\n{e}\n\n"
        "Make sure `nassau_candy_cleaned.csv` is either next to `app.py` or inside a `data/` folder beside it."
    )
    st.stop()
 
if raw_df.empty:
    st.error("No valid records found after cleaning. Please check the source file.")
    st.stop()
 
DATA_MIN_DATE = raw_df["Order Date"].min().date()
DATA_MAX_DATE = raw_df["Order Date"].max().date()
 
# Surface a data-catalog gap instead of letting it hide inside the Factory
# Intelligence charts: if a new product ever appears without a FACTORY_MAP
# entry, this tells whoever is looking at the dashboard exactly what to fix.
_unmapped = sorted(raw_df.loc[raw_df["Factory"] == "Unmapped", "Product Name"].unique())
if _unmapped:
    st.warning(
        f"{len(_unmapped)} product(s) have no factory assigned in FACTORY_MAP and are grouped "
        f"under \"Unmapped\" on the Factory Intelligence page: {', '.join(_unmapped)}."
    )
 
# ============================================================================
# NAVIGATION
# ============================================================================
NAV_ITEMS = [
    ("Executive Overview", ":material/dashboard:"),
    ("Product Profitability", ":material/inventory_2:"),
    ("Division Performance", ":material/apartment:"),
    ("Cost & Margin Risk", ":material/warning:"),
    ("Profit Concentration", ":material/pie_chart:"),
    ("Factory Intelligence", ":material/factory:"),
    ("Insights & Recommendations", ":material/lightbulb:"),
]
 
# ============================================================================
# TOP BAR
# ============================================================================
topbar = st.container(key="topbar")
with topbar:
    tb1, tb2, tb3, tb4 = st.columns([0.5, 4, 1, 1.3])
    with tb1:
        st.markdown("<div style='font-size:20px; color:#FFFFFF; padding-top:4px;'><i class='fa-solid fa-bars'></i></div>", unsafe_allow_html=True)
    with tb2:
        st.markdown(
            "<div class='topbar-brand-title'><i class='fa-solid fa-candy-cane' style='margin-right:8px;'></i>NASSAU CANDY</div>"
            "<div class='topbar-brand-sub'>Profitability Analytics</div>",
            unsafe_allow_html=True,
        )
    with tb3:
        toggle_label = "Light" if DARK else "Dark"
        toggle_icon = ":material/light_mode:" if DARK else ":material/dark_mode:"
        if st.button(toggle_label, icon=toggle_icon, key="theme_toggle", width="stretch"):
            st.session_state.dark_mode = not st.session_state.dark_mode
            st.rerun()
    with tb4:
        st.download_button(
            "Export Report", data=raw_df.to_csv(index=False).encode("utf-8"),
            file_name="nassau_candy_export.csv", mime="text/csv",
            icon=":material/ios_share:", key="export_btn", width="stretch",
        )
 
# ============================================================================
# SIDEBAR — FILTER PANEL
# ============================================================================
with st.sidebar:
    st.markdown(
        "<div class='side-section-label'><i class='fa-solid fa-filter'></i>Dashboard Filters</div>",
        unsafe_allow_html=True,
    )
 
    rk = st.session_state.reset_ctr
    st.markdown("<div class='filter-label'><i class='fa-solid fa-calendar-days'></i>Date Range</div>", unsafe_allow_html=True)
    date_range = st.date_input(
        "Date range", value=(DATA_MIN_DATE, DATA_MAX_DATE),
        min_value=DATA_MIN_DATE, max_value=DATA_MAX_DATE, key=f"date_range_{rk}",
        label_visibility="collapsed",
    )
    st.markdown("<div class='filter-label'><i class='fa-solid fa-layer-group'></i>Division</div>", unsafe_allow_html=True)
    all_divisions = sorted(raw_df["Division"].unique().tolist())
    division_filter = st.multiselect("Division", options=all_divisions, default=all_divisions, key=f"division_{rk}", label_visibility="collapsed")
    st.markdown("<div class='filter-label'><i class='fa-solid fa-magnifying-glass'></i>Product Search</div>", unsafe_allow_html=True)
    product_search = st.text_input("Product search", placeholder="e.g. Kazookles, Wonka...", key=f"search_{rk}", label_visibility="collapsed")
    st.markdown("<div class='filter-label'><i class='fa-solid fa-gauge-high'></i>Margin Risk Threshold (%)</div>", unsafe_allow_html=True)
    margin_threshold = st.slider("Margin-risk threshold (%)", 0, 100, 20, 1, key=f"margin_{rk}", label_visibility="collapsed")
 
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<div class='side-section-label'><i class='fa-solid fa-bolt'></i>Actions</div>", unsafe_allow_html=True)
    actions_box = st.container(key="actions_container")
    with actions_box:
        if st.button("Reset Filters", icon=":material/restart_alt:", key="reset_btn", width="stretch"):
            st.session_state.reset_ctr += 1
            st.rerun()
 
# ============================================================================
# APPLY FILTERS
# ============================================================================
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_date, end_date = date_range
else:
    start_date, end_date = DATA_MIN_DATE, DATA_MAX_DATE
 
mask = (
    (raw_df["Order Date"] >= pd.to_datetime(start_date))
    & (raw_df["Order Date"] <= pd.to_datetime(end_date))
    & (raw_df["Division"].isin(division_filter if division_filter else all_divisions))
)
df = raw_df[mask].copy()
if product_search:
    df = df[df["Product Name"].str.contains(product_search, case=False, na=False)]
 
active_filters = []
if len(division_filter) < len(all_divisions):
    active_filters.append(f"{len(division_filter)}/{len(all_divisions)} divisions")
if (start_date, end_date) != (DATA_MIN_DATE, DATA_MAX_DATE):
    active_filters.append("custom date range")
if product_search:
    active_filters.append(f'search: "{product_search}"')
active_filters_text = " · ".join(active_filters) if active_filters else "None (showing all data)"
 
with st.sidebar:
    with actions_box:
        st.download_button(
            "Download Filtered Data", data=df.to_csv(index=False).encode("utf-8"),
            file_name="nassau_candy_filtered.csv", mime="text/csv",
            icon=":material/download:", key="download_btn", width="stretch",
        )
    st.markdown(
        f"<div class='about-card'><i class='fa-solid fa-circle-info'></i><b style='color:{TEXT_DARK};'>About this Dashboard</b><br>"
        f"This dashboard provides a complete overview of product line profitability and margin performance "
        f"across divisions and factories.</div>",
        unsafe_allow_html=True,
    )
 
if df.empty:
    st.warning("No records match the current filter combination. Try widening the date range, selecting more divisions, or clearing the product search.")
    st.stop()
 
# ============================================================================
# PREVIOUS-YEAR COMPARISON WINDOW (for trend indicators — real data, not fabricated)
# ============================================================================
prev_start = pd.Timestamp(start_date) - pd.DateOffset(years=1)
prev_end = pd.Timestamp(end_date) - pd.DateOffset(years=1)
 
data_min = raw_df["Order Date"].min()
cur_start_ts = pd.Timestamp(start_date)
 
# A prior-year comparison is only meaningful when the shifted window (a) lands entirely
# before the currently-selected window (no overlap with "current"), and (b) is fully
# covered by the data we actually have (no partial/truncated prior period). Otherwise
# the comparison would mix current-period rows into "previous" or compare against an
# incomplete period, so we show "n/a" instead of a misleading number.
prev_period_valid = (prev_end < cur_start_ts) and (prev_start >= data_min)
 
if prev_period_valid:
    prev_mask = (
        (raw_df["Order Date"] >= prev_start) & (raw_df["Order Date"] <= prev_end)
        & (raw_df["Division"].isin(division_filter if division_filter else all_divisions))
    )
    prev_df = raw_df[prev_mask].copy()
    if product_search:
        prev_df = prev_df[prev_df["Product Name"].str.contains(product_search, case=False, na=False)]
else:
    prev_df = raw_df.iloc[0:0].copy()
 
prev_sales = prev_df["Sales"].sum() if not prev_df.empty else None
prev_gp = prev_df["Gross Profit"].sum() if not prev_df.empty else None
prev_cost = prev_df["Cost"].sum() if not prev_df.empty else None
prev_units = prev_df["Units"].sum() if not prev_df.empty else None
prev_margin = float(safe_div(prev_gp, prev_sales) * 100) if prev_sales else None
 
# ============================================================================
# HEADER
# ============================================================================
hcol1, hcol2 = st.columns([4, 1.4])
with hcol1:
    st.markdown(
        """<div class="hero-title">Nassau Candy Distributor</div>
        <div class="hero-sub">Product Line Profitability &amp; Margin Performance Analysis</div>
        <div class="hero-tag">Turning sales, cost and margin data into actionable profitability insights.</div>""",
        unsafe_allow_html=True,
    )
with hcol2:
    st.markdown(
        f"<div class='last-updated'>Last updated:<br><b style='color:{TEXT_DARK};'>{st.session_state.last_refresh.strftime('%d %b %Y %I:%M %p')}</b></div>",
        unsafe_allow_html=True,
    )
    if st.button("Refresh", icon=":material/refresh:", key="refresh_btn", width="stretch"):
        st.session_state.last_refresh = datetime.now()
        st.rerun()
 
st.markdown(
    f"""<div class="hero-meta">DATA PERIOD: <b>{DATA_MIN_DATE.strftime('%b %Y')} – {DATA_MAX_DATE.strftime('%b %Y')}</b>
    &nbsp;•&nbsp; TOTAL RECORDS: <b>{len(df):,}</b> &nbsp;•&nbsp; PRODUCTS ANALYZED: <b>{df['Product Name'].nunique()}</b>
    &nbsp;•&nbsp; ACTIVE FILTERS: <b>{len(active_filters)} Applied</b> ({active_filters_text})</div>""",
    unsafe_allow_html=True,
)
 
# ============================================================================
# CORE AGGREGATIONS
# ============================================================================
total_sales = df["Sales"].sum()
total_cost = df["Cost"].sum()
total_gp = df["Gross Profit"].sum()
total_units = df["Units"].sum()
overall_margin = float(safe_div(total_gp, total_sales) * 100)
 
# Margin volatility is measured as the standard deviation of periodic gross
# margin percentages. It quantifies how stable profitability is over time.
margin_period = (df.set_index("Order Date").resample("ME").agg({"Sales": "sum", "Gross Profit": "sum"}))
margin_period = margin_period[margin_period["Sales"] > 0].copy()
margin_period["Margin_%"] = safe_div(margin_period["Gross Profit"], margin_period["Sales"]) * 100
margin_volatility = float(margin_period["Margin_%"].std(ddof=1)) if len(margin_period) > 1 else 0.0
margin_stability_label = "Stable" if margin_volatility < 3 else ("Moderate variation" if margin_volatility < 7 else "High variation")
 
 
def build_product_table(data: pd.DataFrame) -> pd.DataFrame:
    p = data.groupby("Product Name").agg(
        Sales=("Sales", "sum"), Cost=("Cost", "sum"), Gross_Profit=("Gross Profit", "sum"), Units=("Units", "sum"),
        Division=("Division", "first"), Factory=("Factory", "first"),
    ).reset_index()
    p["Margin_%"] = safe_div(p["Gross_Profit"], p["Sales"]) * 100
    p["Profit_per_Unit"] = safe_div(p["Gross_Profit"], p["Units"])
    p["Revenue_Contribution_%"] = safe_div(p["Sales"], total_sales) * 100 if total_sales else np.zeros(len(p))
    p["Profit_Contribution_%"] = safe_div(p["Gross_Profit"], total_gp) * 100 if total_gp else np.zeros(len(p))
    p["Risk_Status"] = p["Margin_%"].apply(lambda m: risk_status(m, margin_threshold))
    med_sales, med_margin = p["Sales"].median(), p["Margin_%"].median()
    p["Quadrant"] = p.apply(lambda r: classify_quadrant(r, med_sales, med_margin), axis=1)
    return p.sort_values("Gross_Profit", ascending=False).reset_index(drop=True)
 
 
def build_division_table(data: pd.DataFrame) -> pd.DataFrame:
    d = data.groupby("Division").agg(
        Sales=("Sales", "sum"), Cost=("Cost", "sum"), Gross_Profit=("Gross Profit", "sum"), Units=("Units", "sum")
    ).reset_index()
    d["Margin_%"] = safe_div(d["Gross_Profit"], d["Sales"]) * 100
    d["Revenue_Contribution_%"] = safe_div(d["Sales"], total_sales) * 100 if total_sales else np.zeros(len(d))
    d["Profit_Contribution_%"] = safe_div(d["Gross_Profit"], total_gp) * 100 if total_gp else np.zeros(len(d))
    return d.sort_values("Gross_Profit", ascending=False).reset_index(drop=True)
 
 
def build_factory_table(data: pd.DataFrame) -> pd.DataFrame:
    f = data.groupby("Factory").agg(
        Sales=("Sales", "sum"), Cost=("Cost", "sum"), Gross_Profit=("Gross Profit", "sum"),
        Units=("Units", "sum"), Products=("Product Name", "nunique"),
    ).reset_index()
    f["Margin_%"] = safe_div(f["Gross_Profit"], f["Sales"]) * 100
    f["Latitude"] = f["Factory"].map(lambda x: FACTORY_COORDS.get(x, (np.nan, np.nan))[0])
    f["Longitude"] = f["Factory"].map(lambda x: FACTORY_COORDS.get(x, (np.nan, np.nan))[1])
    return f.sort_values("Gross_Profit", ascending=False).reset_index(drop=True)
 
 
product_tbl = build_product_table(df)
division_tbl = build_division_table(df)
factory_tbl = build_factory_table(df)
 
pareto_profit = product_tbl.sort_values("Gross_Profit", ascending=False).reset_index(drop=True)
pareto_profit["Cum_Profit_%"] = safe_div(pareto_profit["Gross_Profit"].cumsum(), pareto_profit["Gross_Profit"].sum()) * 100
pareto_rev = product_tbl.sort_values("Sales", ascending=False).reset_index(drop=True)
pareto_rev["Cum_Revenue_%"] = safe_div(pareto_rev["Sales"].cumsum(), pareto_rev["Sales"].sum()) * 100
# First rank at which cumulative contribution reaches (>=) 80%, rather than
# "count of rows strictly under 80, plus one" — the old formula double-counted
# a row whenever its cumulative value landed exactly on 80.00.
def _first_rank_to_reach(cum_series, threshold=80):
    if not len(cum_series):
        return 0
    hits = np.flatnonzero(cum_series.to_numpy() >= threshold)
    return int(hits[0] + 1) if len(hits) else len(cum_series)
 
n80_profit = _first_rank_to_reach(pareto_profit["Cum_Profit_%"])
n80_rev = _first_rank_to_reach(pareto_rev["Cum_Revenue_%"])
top1_share = float(pareto_profit["Profit_Contribution_%"].iloc[0]) if len(pareto_profit) else 0
top3_share = float(pareto_profit["Profit_Contribution_%"].head(3).sum()) if len(pareto_profit) else 0
top5_share = float(pareto_profit["Profit_Contribution_%"].head(5).sum()) if len(pareto_profit) else 0
 
top_profit_row = product_tbl.iloc[0]
top_margin_row = product_tbl.sort_values("Margin_%", ascending=False).iloc[0]
risk_row = product_tbl.sort_values("Margin_%").iloc[0]
top_division_row = division_tbl.iloc[0]
 
# ============================================================================
# PILL NAVIGATION
# ============================================================================
nav_shell = st.container(key="nav_shell")
with nav_shell:
    nav_cols = st.columns(len(NAV_ITEMS))
    for col, (item, icon) in zip(nav_cols, NAV_ITEMS):
        is_active = st.session_state.page == item
        if col.button(item, icon=icon, key=f"nav_{item}", width="stretch",
                      type="primary" if is_active else "secondary"):
            st.session_state.page = item
            st.rerun()
 
page = st.session_state.page
 
# ----------------------------------------------------------------------------
# PAGE — EXECUTIVE OVERVIEW
# ----------------------------------------------------------------------------
if page == "Executive Overview":
    c1, c2, c3, c4, c5 = st.columns(5)
    kpi_card2(c1, "fa-bag-shopping", BLUE_BG, BLUE_FG, "Total Sales", fmt_currency0(total_sales),
              "Across all filtered orders", trend_html(total_sales, prev_sales))
    kpi_card2(c2, "fa-arrow-trend-up", GREEN_BG, GREEN_FG, "Gross Profit", fmt_currency0(total_gp),
              "Sales minus cost", trend_html(total_gp, prev_gp))
    kpi_card2(c3, "fa-chart-pie", PURPLE_BG, PURPLE_FG, "Gross Margin", fmt_pct(overall_margin),
              "Gross profit ÷ sales", trend_html(overall_margin, prev_margin, is_pp=True))
    kpi_card2(c4, "fa-file-invoice-dollar", ORANGE_BG, ORANGE_FG, "Total Cost", fmt_currency0(total_cost),
              "Manufacturing & operations", trend_html(total_cost, prev_cost))
    kpi_card2(c5, "fa-boxes-stacked", TEAL_BG, TEAL_FG, "Units Sold", f"{total_units:,}",
              "Total units in view", trend_html(total_units, prev_units))
 
    st.markdown("<div style='height:12px;'></div>", unsafe_allow_html=True)
    stability_cols = st.columns([2.8, 1.1, 1.1, 1.1])
    with stability_cols[0]:
        st.markdown(
            """<div class='stability-strip'><div class='stability-title'><i class='fa-solid fa-wave-square'></i> Margin Stability</div>
            <div class='stability-desc'>Monthly gross-margin variability across the selected period</div></div>""",
            unsafe_allow_html=True,
        )
    with stability_cols[1]:
        stat_pill(stability_cols[1], "fa-chart-line", BLUE_BG, BLUE_FG, f"{margin_volatility:.2f} pp", "Margin Volatility")
    with stability_cols[2]:
        stat_pill(stability_cols[2], "fa-shield-halved", GREEN_BG, GREEN_FG, margin_stability_label, "Stability")
    with stability_cols[3]:
        stat_pill(stability_cols[3], "fa-calendar-days", ORANGE_BG, ORANGE_FG, f"{len(margin_period)}", "Periods")
 
    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
    ic1, ic2, ic3, ic4, ic5 = st.columns(5)
    insight_card2(ic1, "fa-trophy", "good", "Top Profit Driver", top_profit_row["Product Name"],
                  f"{fmt_currency0(top_profit_row['Gross_Profit'])} gross profit")
    insight_card2(ic2, "fa-star", "warn", "Highest Margin Product", top_margin_row["Product Name"],
                  f"{fmt_pct(top_margin_row['Margin_%'])} gross margin")
    insight_card2(ic3, "fa-triangle-exclamation", "risk", "Lowest Margin Product", risk_row["Product Name"],
                  f"{fmt_pct(risk_row['Margin_%'])} gross margin")
    insight_card2(ic4, "fa-chart-simple", "", "Profit Concentration", f"{n80_profit} of {len(product_tbl)} products",
                  "generate 80% of gross profit")
    insight_card2(ic5, "fa-circle-exclamation", "risk", "Main Business Risk", f"{top_division_row['Division']} dependency",
                  f"{fmt_pct(top_division_row['Profit_Contribution_%'])} of profit from one division")
 
    st.markdown("<div style='height:6px;'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        hh1, hh2 = st.columns([3, 1.3])
        hh1.markdown('<div class="section-title" style="margin-top:6px;"><i class="fa-solid fa-chart-line"></i>Monthly Sales &amp; Gross Profit Trend</div>', unsafe_allow_html=True)
        period = hh2.selectbox("Period", ["Weekly", "Monthly", "Quarterly"], index=1, key="period_sel", label_visibility="collapsed")
        freq_map = {"Weekly": "W", "Monthly": "ME", "Quarterly": "QE"}
        monthly = df.set_index("Order Date").resample(freq_map[period]).agg({"Sales": "sum", "Gross Profit": "sum"}).reset_index()
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=monthly["Order Date"], y=monthly["Sales"], name="Total Sales", mode="lines+markers", line=dict(color="#4A6B8A", width=2.5)))
        fig.add_trace(go.Scatter(x=monthly["Order Date"], y=monthly["Gross Profit"], name="Gross Profit", mode="lines+markers", line=dict(color=GOOD, width=2.5)))
        style_fig(fig)
        st.markdown('<div class="section-card" style="margin-top:-14px;">', unsafe_allow_html=True)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
    with col2:
        hh1, hh2 = st.columns([3, 1.3])
        hh1.markdown('<div class="section-title" style="margin-top:6px;"><i class="fa-solid fa-building"></i>Gross Profit by Division</div>', unsafe_allow_html=True)
        group_by = hh2.selectbox("Group by", ["By Division", "By Factory"], index=0, key="grp_sel", label_visibility="collapsed")
        grp_tbl = division_tbl.rename(columns={"Division": "Group"}) if group_by == "By Division" else factory_tbl.rename(columns={"Factory": "Group"})
        fig = go.Figure()
        fig.add_bar(x=grp_tbl["Group"], y=grp_tbl["Gross_Profit"], name="Gross Profit", marker_color=NAVY,
                    text=grp_tbl["Gross_Profit"].map(lambda v: f"${v:,.0f}"), textposition="outside")
        fig.add_trace(go.Scatter(x=grp_tbl["Group"], y=grp_tbl["Margin_%"], name="Gross Margin (%)", yaxis="y2",
                                  mode="lines+markers+text", line=dict(color=GOLD, width=2.5),
                                  text=grp_tbl["Margin_%"].map(lambda v: f"{v:.1f}%"), textposition="top center"))
        fig.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0, max(105, grp_tbl["Margin_%"].max() * 1.2)], showgrid=False))
        style_fig(fig)
        st.markdown('<div class="section-card" style="margin-top:-14px;">', unsafe_allow_html=True)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        st.markdown("</div>", unsafe_allow_html=True)
 
    st.markdown("<div style='height:2px;'></div>", unsafe_allow_html=True)
    st1, st2, st3, st4, st5 = st.columns(5)
    stat_pill(st1, "fa-cubes", BLUE_BG, BLUE_FG, f"{df['Product Name'].nunique()}", "Products Analyzed")
    stat_pill(st2, "fa-sitemap", GREEN_BG, GREEN_FG, f"{df['Division'].nunique()}", "Divisions")
    stat_pill(st3, "fa-database", ORANGE_BG, ORANGE_FG, f"{len(df):,}", "Total Records")
    stat_pill(st4, "fa-industry", PURPLE_BG, PURPLE_FG, f"{df['Factory'].nunique()}", "Factories Mapped")
    stat_pill(st5, "fa-filter", TEAL_BG, TEAL_FG, f"{len(active_filters)}", "Active Filters")
 
    st.markdown("<div style='height:16px;'></div>", unsafe_allow_html=True)
    section_header("Executive Action Matrix", "Dynamically generated from the current filtered data", icon="fa-list-check")
    matrix_rows = []
    for _, r in product_tbl.iterrows():
        if r["Margin_%"] < margin_threshold and r["Revenue_Contribution_%"] > product_tbl["Revenue_Contribution_%"].median():
            matrix_rows.append((r["Product Name"], "Low margin + high sales", "High", "Review pricing and cost"))
        elif r["Quadrant"] == "Profit Stars":
            matrix_rows.append((r["Product Name"], "High profit + high margin", "High", "Protect and grow"))
        elif r["Quadrant"] == "Revenue Heavyweights":
            matrix_rows.append((r["Product Name"], "High sales + weaker margin", "Medium", "Review pricing"))
        elif r["Quadrant"] == "Growth Opportunities":
            matrix_rows.append((r["Product Name"], "High margin + low sales", "Medium", "Explore promotion"))
        elif r["Quadrant"] == "Portfolio Review":
            matrix_rows.append((r["Product Name"], "Low profit + low margin", "High", "Review discontinuation"))
    matrix_df = pd.DataFrame(matrix_rows, columns=["Product", "Business Situation", "Priority", "Recommended Action"])
    pri_order = {"High": 0, "Medium": 1, "Monitor": 2}
    matrix_df = matrix_df.sort_values(by="Priority", key=lambda s: s.map(pri_order))
    st.dataframe(matrix_df, width="stretch", height=280, hide_index=True)
    section_close()
 
# ----------------------------------------------------------------------------
# PAGE — PRODUCT PROFITABILITY
# ----------------------------------------------------------------------------
elif page == "Product Profitability":
    page_header("Product Profitability", "Which products actually make money — ranked by profit, margin, and contribution.")
 
    section_header("Product Gross-Profit Leaderboard", "Ranked by total gross profit contribution", icon="fa-ranking-star")
    lb = product_tbl.sort_values("Gross_Profit")
    fig = px.bar(lb, x="Gross_Profit", y="Product Name", orientation="h", color="Margin_%",
                 color_continuous_scale=[RISK, WARN, GOOD])
    style_fig(fig, height=420)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    section_close()
 
    col1, col2 = st.columns(2)
    with col1:
        section_header("Sales vs Gross Margin", "Bubble size = gross profit, color = risk status", icon="fa-braille")
        fig = px.scatter(product_tbl, x="Sales", y="Margin_%", size="Gross_Profit", color="Risk_Status",
                          color_discrete_map={"Healthy": GOOD, "Watchlist": WARN, "High Margin Risk": RISK},
                          hover_name="Product Name",
                          hover_data={"Sales": ":$,.2f", "Margin_%": ":.2f", "Gross_Profit": ":$,.2f"})
        style_fig(fig)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        section_close()
    with col2:
        section_header("Profitability Quadrant Analysis", "Split at median sales & median margin", icon="fa-border-all")
        fig = px.scatter(product_tbl, x="Sales", y="Margin_%", size="Gross_Profit", color="Quadrant",
                          color_discrete_map=QUADRANT_COLORS, hover_name="Product Name")
        med_sales, med_margin = product_tbl["Sales"].median(), product_tbl["Margin_%"].median()
        fig.add_vline(x=med_sales, line_dash="dash", line_color=TEXT_MUTED)
        fig.add_hline(y=med_margin, line_dash="dash", line_color=TEXT_MUTED)
        style_fig(fig)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        section_close()
 
    section_header("Quadrant Summary", icon="fa-grip")
    qcols = st.columns(4)
    quad_order = ["Profit Stars", "Revenue Heavyweights", "Growth Opportunities", "Portfolio Review"]
    quad_desc = {
        "Profit Stars": "High profit + high margin — protect and grow",
        "Revenue Heavyweights": "High sales but weaker margins — review pricing",
        "Growth Opportunities": "High margin but lower sales — explore promotion",
        "Portfolio Review": "Low profit + low margin — review discontinuation",
    }
    for col, q in zip(qcols, quad_order):
        members = product_tbl[product_tbl["Quadrant"] == q]["Product Name"].tolist()
        col.markdown(
            f"""<div class="quad-card" style="border-top:4px solid {QUADRANT_COLORS[q]};">
            <div style="font-weight:700; color:{TEXT_DARK}; font-size:13.5px;">{q}</div>
            <div style="font-size:11px; color:{TEXT_MUTED}; margin:4px 0 8px 0;">{quad_desc[q]}</div>
            <div style="font-size:11.5px; color:{TEXT_DARK};">{'<br>'.join(members) if members else '<i>None</i>'}</div>
            </div>""", unsafe_allow_html=True,
        )
    st.markdown("<div style='height:14px;'></div>", unsafe_allow_html=True)
 
    section_header("Product Performance Table", icon="fa-table")
    display_tbl = product_tbl.rename(columns={"Risk_Status": "Risk Flag"})
    st.dataframe(
        display_tbl[["Product Name", "Division", "Factory", "Sales", "Cost", "Units", "Gross_Profit",
                     "Margin_%", "Profit_per_Unit", "Revenue_Contribution_%", "Profit_Contribution_%", "Risk Flag"]]
        .style.format({
            "Sales": "${:,.2f}", "Cost": "${:,.2f}", "Gross_Profit": "${:,.2f}", "Margin_%": "{:.2f}%",
            "Profit_per_Unit": "${:.2f}", "Revenue_Contribution_%": "{:.2f}%", "Profit_Contribution_%": "{:.2f}%",
        }), width="stretch", height=380,
    )
    section_close()
 
# ----------------------------------------------------------------------------
# PAGE — DIVISION PERFORMANCE
# ----------------------------------------------------------------------------
elif page == "Division Performance":
    page_header("Division Performance", "Comparing revenue, cost, and margin efficiency across product divisions.")
 
    col1, col2 = st.columns(2)
    with col1:
        section_header("Revenue vs Gross Profit by Division", icon="fa-scale-balanced")
        fig = go.Figure()
        fig.add_bar(x=division_tbl["Division"], y=division_tbl["Sales"], name="Sales", marker_color="#B8C2D0")
        fig.add_bar(x=division_tbl["Division"], y=division_tbl["Gross_Profit"], name="Gross Profit", marker_color=NAVY)
        fig.update_layout(barmode="group")
        style_fig(fig, height=360)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        section_close()
    with col2:
        section_header("Gross Margin by Division", icon="fa-percent")
        fig = px.bar(division_tbl, x="Division", y="Margin_%", color="Margin_%",
                     color_continuous_scale=[RISK, WARN, GOOD], text=division_tbl["Margin_%"].map(lambda v: f"{v:.1f}%"))
        fig.update_traces(textposition="outside")
        style_fig(fig, height=360)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        section_close()
 
    section_header("Margin Distribution by Division", "Transaction-level margin variation", icon="fa-chart-column")
    fig = px.box(df, x="Division", y="Txn_Margin_%", color="Division", color_discrete_sequence=CHART_SEQ, points=False)
    fig.update_layout(showlegend=False)
    style_fig(fig, height=360)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    section_close()
 
    section_header("Division Summary Table", icon="fa-table")
    st.dataframe(
        division_tbl.style.format({
            "Sales": "${:,.2f}", "Cost": "${:,.2f}", "Gross_Profit": "${:,.2f}", "Margin_%": "{:.2f}%",
            "Revenue_Contribution_%": "{:.2f}%", "Profit_Contribution_%": "{:.2f}%",
        }), width="stretch",
    )
    st.markdown(f"<div class='side-section-label' style='margin:14px 0 8px 4px; color:{NAVY} !important;'><i class='fa-solid fa-lightbulb'></i>What This Means</div>", unsafe_allow_html=True)
    overall_avg_margin = division_tbl["Margin_%"].mean()
    for _, r in division_tbl.iterrows():
        if r["Margin_%"] >= overall_avg_margin and r["Revenue_Contribution_%"] >= division_tbl["Revenue_Contribution_%"].median():
            verdict = "high scale + high profit"
        elif r["Revenue_Contribution_%"] >= division_tbl["Revenue_Contribution_%"].median() and r["Margin_%"] < overall_avg_margin:
            verdict = "high scale + weaker margin"
        elif r["Revenue_Contribution_%"] < division_tbl["Revenue_Contribution_%"].median() and r["Margin_%"] >= overall_avg_margin:
            verdict = "smaller but efficient"
        else:
            verdict = "underperforming — needs review"
        st.markdown(
            f"<p style='font-size:13px; color:{TEXT_MUTED};'><b style='color:{TEXT_DARK};'>{r['Division']}:</b> {verdict} "
            f"({fmt_pct(r['Margin_%'])} margin, {fmt_pct(r['Revenue_Contribution_%'])} of revenue).</p>",
            unsafe_allow_html=True,
        )
    section_close()
 
# ----------------------------------------------------------------------------
# PAGE — COST & MARGIN RISK
# ----------------------------------------------------------------------------
elif page == "Cost & Margin Risk":
    page_header("Cost & Margin Risk", "Diagnosing where cost is eroding margin and which products need review.")
 
    section_header("Cost vs Sales Diagnostics", "Bubble size = gross profit, color = margin risk", icon="fa-magnifying-glass-chart")
    fig = px.scatter(product_tbl, x="Sales", y="Cost", size="Gross_Profit", color="Risk_Status",
                      color_discrete_map={"Healthy": GOOD, "Watchlist": WARN, "High Margin Risk": RISK},
                      hover_name="Product Name",
                      hover_data={"Sales": ":$,.2f", "Cost": ":$,.2f", "Gross_Profit": ":$,.2f", "Margin_%": ":.2f"})
    style_fig(fig, height=420)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    section_close()
 
    risk_tbl = product_tbl[product_tbl["Margin_%"] < margin_threshold].sort_values("Margin_%").copy()
 
    def recommend_action(row):
        cost_ratio = safe_div(np.array([row["Cost"]]), np.array([row["Sales"]]))[0] * 100
        if cost_ratio > 80:
            return "Cost reduction — cost consumes most of sales value"
        elif row["Revenue_Contribution_%"] > product_tbl["Revenue_Contribution_%"].median():
            return "Repricing review — high volume, weak margin"
        elif row["Margin_%"] < margin_threshold / 2:
            return "Portfolio / discontinuation review"
        else:
            return "Supplier negotiation — reduce input cost"
 
    section_header(f"Products Below {margin_threshold}% Margin Threshold", "Flagged with a specific recommended action per product", icon="fa-triangle-exclamation")
    if risk_tbl.empty:
        st.markdown(f"""<div class="insight-card2 good"><div class="insight-value2">No products fall below {margin_threshold}% margin in the current selection.</div></div>""", unsafe_allow_html=True)
    else:
        risk_tbl["Recommended Action"] = risk_tbl.apply(recommend_action, axis=1)
        show = risk_tbl.rename(columns={"Risk_Status": "Risk Level"})
        st.dataframe(
            show[["Product Name", "Sales", "Cost", "Gross_Profit", "Margin_%", "Risk Level", "Recommended Action"]]
            .style.format({"Sales": "${:,.2f}", "Cost": "${:,.2f}", "Gross_Profit": "${:,.2f}", "Margin_%": "{:.2f}%"}),
            width="stretch",
        )
    section_close()
 
# ----------------------------------------------------------------------------
# PAGE — PROFIT CONCENTRATION / PARETO
# ----------------------------------------------------------------------------
elif page == "Profit Concentration":
    page_header("Profit Concentration", "How dependent total profit is on a small number of products (Pareto analysis).")
 
    col1, col2 = st.columns(2)
    with col1:
        section_header("Profit Pareto Curve", icon="fa-chart-line")
        fig = go.Figure()
        fig.add_bar(x=pareto_profit["Product Name"], y=pareto_profit["Gross_Profit"], name="Gross Profit", marker_color=NAVY)
        fig.add_trace(go.Scatter(x=pareto_profit["Product Name"], y=pareto_profit["Cum_Profit_%"], name="Cumulative %",
                                  yaxis="y2", line=dict(color=RISK, width=2), mode="lines+markers"))
        fig.add_hline(y=80, line_dash="dash", line_color=TEXT_MUTED, yref="y2")
        fig.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0, 105]), xaxis=dict(tickangle=-60))
        style_fig(fig, height=420)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        section_close()
    with col2:
        section_header("Revenue Pareto Curve", icon="fa-chart-line")
        fig = go.Figure()
        fig.add_bar(x=pareto_rev["Product Name"], y=pareto_rev["Sales"], name="Sales", marker_color="#4A6B8A")
        fig.add_trace(go.Scatter(x=pareto_rev["Product Name"], y=pareto_rev["Cum_Revenue_%"], name="Cumulative %",
                                  yaxis="y2", line=dict(color=RISK, width=2), mode="lines+markers"))
        fig.add_hline(y=80, line_dash="dash", line_color=TEXT_MUTED, yref="y2")
        fig.update_layout(yaxis2=dict(overlaying="y", side="right", range=[0, 105]), xaxis=dict(tickangle=-60))
        style_fig(fig, height=420)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        section_close()
 
    d1, d2, d3, d4, d5 = st.columns(5)
    kpi_card2(d1, "fa-percent", BLUE_BG, BLUE_FG, "Products for 80% Revenue", f"{n80_rev} of {len(product_tbl)}", "")
    kpi_card2(d2, "fa-percent", BLUE_BG, BLUE_FG, "Products for 80% Profit", f"{n80_profit} of {len(product_tbl)}", "")
    kpi_card2(d3, "fa-1", RISK if top1_share > 30 else ORANGE_BG, "#FFFFFF" if top1_share > 30 else ORANGE_FG, "Top 1 Product Share", fmt_pct(top1_share), "")
    kpi_card2(d4, "fa-3", RISK if top3_share > 60 else ORANGE_BG, "#FFFFFF" if top3_share > 60 else ORANGE_FG, "Top 3 Products Share", fmt_pct(top3_share), "")
    kpi_card2(d5, "fa-5", RISK if top5_share > 75 else ORANGE_BG, "#FFFFFF" if top5_share > 75 else ORANGE_FG, "Top 5 Products Share", fmt_pct(top5_share), "")
 
    concentration_level = "high" if n80_profit / max(len(product_tbl), 1) < 0.5 else "low"
    interp = ("indicating a concentrated, dependency-risk portfolio — a disruption to a small number of products "
              "would materially affect total profit.") if concentration_level == "high" else \
             ("indicating a relatively diversified portfolio — profit is spread across a wider base of products.")
    st.markdown(
        f"""<div class="insight-card2 risk" style="margin-top:14px;"><div class="insight-label2">Business Risk Interpretation</div>
        <div class="insight-value2">{n80_profit} of {len(product_tbl)} products generate over 80% of gross profit.</div>
        <div class="insight-sub2">This is {concentration_level} concentration, {interp}</div></div>""",
        unsafe_allow_html=True,
    )
 
# ----------------------------------------------------------------------------
# PAGE — FACTORY INTELLIGENCE
# ----------------------------------------------------------------------------
elif page == "Factory Intelligence":
    page_header("Factory Intelligence", "Manufacturing footprint performance by factory location.")
 
    section_header("Factory Locations", "Marker size = sales, color = gross margin — hover for details", icon="fa-map-location-dot")
    fig = px.scatter(factory_tbl, x="Longitude", y="Latitude", size="Sales", color="Margin_%",
                      color_continuous_scale=[RISK, WARN, GOOD], hover_name="Factory",
                      hover_data={"Longitude": False, "Latitude": False, "Sales": ":$,.2f", "Margin_%": ":.2f", "Products": True},
                      text="Factory")
    fig.update_traces(textposition="top center", textfont=dict(size=11, color=TEXT_DARK))
    fig.update_layout(xaxis_title="Longitude", yaxis_title="Latitude", xaxis=dict(range=[-125, -65]), yaxis=dict(range=[24, 50]))
    style_fig(fig, height=400)
    fig.update_xaxes(showgrid=True, gridcolor=BORDER)
    st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
    section_close()
 
    col1, col2 = st.columns(2)
    with col1:
        section_header("Gross Profit by Factory", icon="fa-industry")
        fig = px.bar(factory_tbl.sort_values("Gross_Profit"), x="Gross_Profit", y="Factory", orientation="h", color_discrete_sequence=[NAVY])
        style_fig(fig, height=320)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        section_close()
    with col2:
        section_header("Gross Margin by Factory", icon="fa-percent")
        fig = px.bar(factory_tbl.sort_values("Margin_%"), x="Margin_%", y="Factory", orientation="h",
                     color="Margin_%", color_continuous_scale=[RISK, WARN, GOOD])
        style_fig(fig, height=320)
        st.plotly_chart(fig, width="stretch", config={"displayModeBar": False})
        section_close()
 
    section_header("Factory Performance Comparison", icon="fa-table")
    st.dataframe(
        factory_tbl[["Factory", "Products", "Sales", "Cost", "Gross_Profit", "Units", "Margin_%"]]
        .style.format({"Sales": "${:,.2f}", "Cost": "${:,.2f}", "Gross_Profit": "${:,.2f}", "Margin_%": "{:.2f}%"}),
        width="stretch",
    )
    if len(factory_tbl) >= 2:
        strongest_gp = factory_tbl.sort_values("Gross_Profit", ascending=False).iloc[0]
        most_efficient = factory_tbl.sort_values("Margin_%", ascending=False).iloc[0]
        needs_review = factory_tbl.sort_values("Margin_%").iloc[0]
        st.markdown(
            f"""<p style="font-size:13px; color:{TEXT_MUTED}; margin-top:12px;">
            <b style="color:{TEXT_DARK};">Strongest by gross profit:</b> {strongest_gp['Factory']} ({fmt_currency0(strongest_gp['Gross_Profit'])}).
            <b style="color:{TEXT_DARK};">Most efficient by margin:</b> {most_efficient['Factory']} ({fmt_pct(most_efficient['Margin_%'])}).
            <b style="color:{TEXT_DARK};">Requires review:</b> {needs_review['Factory']} ({fmt_pct(needs_review['Margin_%'])} margin).</p>""",
            unsafe_allow_html=True,
        )
    section_close()
 
# ----------------------------------------------------------------------------
# PAGE — KEY INSIGHTS & RECOMMENDATIONS
# ----------------------------------------------------------------------------
elif page == "Insights & Recommendations":
    page_header("Key Business Insights & Recommendations", "Prioritized findings and recommended actions from the current data view.")
 
    section_header("Top 5 Insights", icon="fa-lightbulb")
    findings = [
        f"The portfolio runs a {fmt_pct(overall_margin)} blended gross margin across {len(product_tbl)} products in view.",
        f"{n80_profit} of {len(product_tbl)} products generate over 80% of total gross profit ({fmt_pct(top5_share)} from the top 5 alone).",
        f"{top_profit_row['Product Name']} is the single largest profit contributor at {fmt_currency0(top_profit_row['Gross_Profit'])}.",
        f"{risk_row['Product Name']} is the clearest margin-risk product at {fmt_pct(risk_row['Margin_%'])}.",
        f"{division_tbl.iloc[0]['Division']} division drives {fmt_pct(division_tbl.iloc[0]['Profit_Contribution_%'])} of gross profit.",
    ]
    for f in findings:
        st.markdown(f"<div class='insight-card2' style='margin-bottom:10px;'><div class='insight-value2' style='font-size:13.5px; font-weight:500;'>{f}</div></div>", unsafe_allow_html=True)
    section_close()
 
    section_header("Priority Recommendations", "Finding → Business Impact → Recommended Action", icon="fa-list-check")
    st.markdown("<div class='pri-high' style='display:inline-block; margin:6px 0;'>HIGH PRIORITY</div>", unsafe_allow_html=True)
    st.markdown(
        f"""<div class="rec-block" style="border-left-color:{RISK};">
        <b>Finding:</b> {risk_row['Product Name']} has {fmt_pct(risk_row['Margin_%'])} gross margin, the weakest in the portfolio.<br>
        <b>Business Impact:</b> Sales volume is being converted into very little actual profit — a hidden drag on portfolio performance.<br>
        <b>Action:</b> Immediate pricing review, supplier cost renegotiation, or discontinuation assessment.</div>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""<div class="rec-block" style="border-left-color:{RISK};">
        <b>Finding:</b> {n80_profit} products generate over 80% of gross profit.<br>
        <b>Business Impact:</b> A disruption to this small group (supply, pricing, demand shift) would have an outsized effect on total company profit.<br>
        <b>Action:</b> Protect supply continuity and pricing for these products; track this concentration ratio monthly.</div>""",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='pri-med' style='display:inline-block; margin:16px 0 6px 0;'>MEDIUM PRIORITY</div>", unsafe_allow_html=True)
    st.markdown(
        f"""<div class="rec-block" style="border-left-color:{WARN};">
        <b>Finding:</b> {top_margin_row['Product Name']} has the portfolio's highest margin ({fmt_pct(top_margin_row['Margin_%'])}) but modest sales volume.<br>
        <b>Business Impact:</b> Potential upside is not being captured due to limited demand or visibility.<br>
        <b>Action:</b> Test targeted promotion to see if volume can scale without eroding margin.</div>""",
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""<div class="rec-block" style="border-left-color:{WARN};">
        <b>Finding:</b> Promotions and discounting currently follow sales-volume rules.<br>
        <b>Business Impact:</b> High-volume, low-margin products may be receiving incentives that further erode profitability.<br>
        <b>Action:</b> Shift promotional rules to a margin-based basis.</div>""",
        unsafe_allow_html=True,
    )
    st.markdown("<div class='pri-mon' style='display:inline-block; margin:16px 0 6px 0;'>MONITOR</div>", unsafe_allow_html=True)
    st.markdown(
        f"""<div class="rec-block" style="border-left-color:{GOOD};">
        <b>Finding:</b> {division_tbl.iloc[0]['Division']} division is performing well, driving most of total profit.<br>
        <b>Business Impact:</b> Currently a strength, but also the portfolio's single point of dependency.<br>
        <b>Action:</b> No immediate action needed — monitor supply, cost, and pricing stability monthly.</div>""",
        unsafe_allow_html=True,
    )
    section_close()
 
st.markdown(
    f"""<p style="text-align:center; color:{TEXT_MUTED}; font-size:11px; margin-top:16px;">
    Nassau Candy Distributor — Product Line Profitability &amp; Margin Performance Analysis
    &nbsp;|&nbsp; Unified Mentor Data Scientist Internship Project</p>""",
    unsafe_allow_html=True,
)
 
