"""
ÉnergiePro — Application d'analyse technico-économique
Photovoltaïque & Éolien | Interface française | Résultats en USD
"""

# ═══════════════════════════════════════════════════════════════════
#  IMPORTS
# ═══════════════════════════════════════════════════════════════════
import math
import io
from datetime import datetime

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
import base64

def get_base64(img_file):
    with open(img_file, "rb") as f:
        return base64.b64encode(f.read()).decode()

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable, KeepTogether
)

# ═══════════════════════════════════════════════════════════════════
#  PAGE CONFIG
# ═══════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="ÉnergiePro — Renouvelables",
    page_icon="logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ═══════════════════════════════════════════════════════════════════
#  CSS — Thème sophistiqué : fond ardoise + accents teal/ambre
# ═══════════════════════════════════════════════════════════════════
st.markdown("""
<style>
/* ── Google Fonts ── */
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');

/* ── Tokens globaux ── */
:root {
  --teal:        #14B8A6;
  --teal-dark:   #0D9488;
  --teal-glow:   rgba(20,184,166,0.18);
  --amber:       #F59E0B;
  --amber-light: rgba(245,158,11,0.15);
  --sky:         #38BDF8;
  --sky-light:   rgba(56,189,248,0.15);
  --red:         #F87171;

  --bg-base:     #0B1120;
  --bg-surface:  #111827;
  --bg-elevated: #1A2236;
  --bg-input:    #1E2A3D;

  --text-hi:     #EEF2FF;
  --text-mid:    #94A3B8;
  --text-lo:     #4B5C72;

  --border:      rgba(148,163,184,0.12);
  --border-teal: rgba(20,184,166,0.30);
  --radius-lg:   16px;
  --radius-md:   10px;
  --shadow-lg:   0 20px 60px rgba(0,0,0,0.55);
  --shadow-teal: 0 8px 32px rgba(20,184,166,0.25);
}

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; }
html, body, [class*="css"] { font-family: 'Sora', sans-serif; }

/* ── App background ── */
.stApp {
  background: radial-gradient(ellipse 140% 80% at 60% -20%,
              rgba(20,184,166,0.08) 0%, transparent 55%),
              linear-gradient(160deg, #060D1A 0%, #0B1120 40%, #0D1628 100%);
  min-height: 100vh;
}

/* ── Main container ── */
.main .block-container {
  padding: 1.75rem 2.25rem 4rem;
  max-width: 1440px;
}

/* ═══════ SIDEBAR ═══════ */
[data-testid="stSidebar"] {
  background: linear-gradient(180deg, #080F1C 0%, #0B1427 60%, #0D1530 100%) !important;
  border-right: 1px solid var(--border-teal);
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0; }

.sidebar-brand {
  padding: 1.8rem 1.4rem 1rem;
  text-align: center;
  border-bottom: 1px solid var(--border);
  margin-bottom: 1rem;
}
.sidebar-logo { font-size: 2.8rem; line-height: 1; }
.sidebar-name {
  font-size: 1.25rem; font-weight: 800; letter-spacing: 2px;
  color: var(--teal); margin-top: 6px;
  text-shadow: 0 0 24px rgba(20,184,166,0.5);
}
.sidebar-tag {
  font-size: 0.7rem; color: var(--text-lo); letter-spacing: 1.5px;
  text-transform: uppercase; margin-top: 2px;
}

/* ── Nav radio ── */
[data-testid="stSidebar"] .stRadio > label { display: none; }
[data-testid="stSidebar"] .stRadio [data-testid="stWidgetLabel"] { display: none; }
[data-testid="stSidebar"] .stRadio > div {
  display: flex; flex-direction: column; gap: 4px;
}
[data-testid="stSidebar"] .stRadio label {
  color: var(--text-mid) !important;
  font-size: 0.88rem !important; font-weight: 500 !important;
  padding: 0.65rem 1rem !important;
  border-radius: var(--radius-md) !important;
  border: 1px solid transparent !important;
  transition: all 0.2s ease !important;
  cursor: pointer !important;
}
[data-testid="stSidebar"] .stRadio label:hover {
  background: var(--teal-glow) !important;
  color: var(--teal) !important;
  border-color: var(--border-teal) !important;
}
[data-testid="stSidebar"] .stRadio [aria-checked="true"] + label,
[data-testid="stSidebar"] .stRadio label[data-checked="true"] {
  background: var(--teal-glow) !important;
  color: var(--teal) !important;
  border-color: var(--border-teal) !important;
  font-weight: 600 !important;
}

/* ── Sidebar info box ── */
.sidebar-info {
  margin: 1.5rem 0.5rem 0;
  background: rgba(20,184,166,0.05);
  border: 1px solid var(--border-teal);
  border-radius: var(--radius-md);
  padding: 0.85rem 1rem;
  font-size: 0.78rem;
  color: var(--text-mid);
  line-height: 1.7;
}
.sidebar-info-title {
  color: var(--teal); font-weight: 700; font-size: 0.8rem;
  margin-bottom: 0.4rem; text-transform: uppercase; letter-spacing: 1px;
}

/* ═══════ METRIC CARDS ═══════ */
.kpi-grid { display: grid; gap: 1rem; margin-bottom: 1.5rem; }
.kpi-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.4rem 1.2rem 1.2rem;
  text-align: center;
  position: relative;
  overflow: hidden;
  transition: transform 0.25s ease, box-shadow 0.25s ease, border-color 0.25s ease;
}
.kpi-card::before {
  content: '';
  position: absolute; top: 0; left: 0; right: 0; height: 3px;
  background: linear-gradient(90deg, var(--teal), var(--sky));
}
.kpi-card::after {
  content: '';
  position: absolute; inset: 0;
  background: radial-gradient(ellipse at 50% 0%, rgba(20,184,166,0.06) 0%, transparent 70%);
  pointer-events: none;
}
.kpi-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-teal);
  border-color: var(--border-teal);
}
.kpi-icon  { font-size: 1.9rem; margin-bottom: 0.6rem; display: block; }
.kpi-label {
  color: var(--text-lo); font-size: 0.72rem;
  text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 0.5rem;
}
.kpi-value {
  color: var(--text-hi);
  font-size: 1.15rem; font-weight: 700;
  font-family: 'JetBrains Mono', monospace; line-height: 1;
}
.kpi-unit { color: var(--teal); font-size: 0.78rem; font-weight: 600; margin-top: 0.3rem; }

.kpi-card.amber::before { background: linear-gradient(90deg, var(--amber), #FDE68A); }
.kpi-card.sky::before   { background: linear-gradient(90deg, var(--sky), #BAE6FD); }
.kpi-card.red::before   { background: linear-gradient(90deg, var(--red), #FCA5A5); }
.kpi-card.teal::before  { background: linear-gradient(90deg, var(--teal), #5EEAD4); }

/* ═══════ SECTION HEADERS ═══════ */
.sec-head {
  display: flex; align-items: center; gap: 0.75rem;
  margin-bottom: 0.35rem;
}
.sec-icon { font-size: 1.8rem; }
.sec-title {
  font-size: 1.55rem; font-weight: 800;
  color: var(--text-hi); letter-spacing: -0.5px;
}
.sec-sub {
  color: var(--text-mid); font-size: 0.88rem;
  margin-bottom: 1.6rem; padding-left: 2.6rem;
}
.divider {
  height: 1px;
  background: linear-gradient(90deg, var(--border-teal), transparent);
  margin: 1.75rem 0;
}

/* ═══════ PARAM PANEL ═══════ */
.param-panel {
  background: var(--bg-surface);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.5rem 1.75rem;
  margin-bottom: 1.5rem;
}
.param-title {
  font-size: 0.82rem; font-weight: 700;
  text-transform: uppercase; letter-spacing: 1.5px;
  color: var(--teal); margin-bottom: 1rem;
  display: flex; align-items: center; gap: 0.5rem;
}

/* ═══════ HERO ═══════ */
.hero {
  background: linear-gradient(135deg,
    rgba(20,184,166,0.08) 0%, rgba(56,189,248,0.05) 50%, rgba(245,158,11,0.04) 100%);
  border: 1px solid var(--border-teal);
  border-radius: 20px;
  padding: 3rem 3rem 2.5rem;
  text-align: center;
  position: relative; overflow: hidden;
  margin-bottom: 2rem;
}
.hero::before {
  content: '';
  position: absolute; top: -60%; left: -20%;
  width: 140%; height: 200%;
  background: radial-gradient(ellipse at center,
              rgba(20,184,166,0.04) 0%, transparent 60%);
  pointer-events: none;
}
.hero-eyebrow {
  display: inline-flex; align-items: center; gap: 6px;
  background: var(--teal-glow);
  border: 1px solid var(--border-teal);
  border-radius: 50px; padding: 4px 14px;
  font-size: 0.75rem; font-weight: 600; color: var(--teal);
  text-transform: uppercase; letter-spacing: 1.5px;
  margin-bottom: 1.25rem;
}
.hero-title {
  font-size: clamp(2rem, 4vw, 3rem);
  font-weight: 800; color: var(--text-hi);
  line-height: 1.15; margin-bottom: 0.75rem;
  letter-spacing: -1px;
}
.hero-title em { color: var(--teal); font-style: normal; }
.hero-body {
  color: var(--text-mid); font-size: 1rem;
  max-width: 640px; margin: 0 auto 1.75rem; line-height: 1.7;
}
.badge-row { display: flex; justify-content: center; gap: 0.6rem; flex-wrap: wrap; }
.badge {
  background: rgba(255,255,255,0.04);
  border: 1px solid var(--border);
  border-radius: 50px; padding: 5px 14px;
  font-size: 0.78rem; font-weight: 600; color: var(--text-mid);
}

/* ═══════ FEATURE CARDS ═══════ */
.feat-card {
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 1.4rem;
  height: 100%;
  transition: border-color 0.2s, transform 0.2s;
}
.feat-card:hover { border-color: var(--border-teal); transform: translateY(-3px); }
.feat-icon { font-size: 1.75rem; margin-bottom: 0.65rem; }
.feat-title { font-size: 0.92rem; font-weight: 700; color: var(--text-hi); margin-bottom: 0.4rem; }
.feat-desc  { font-size: 0.8rem; color: var(--text-mid); line-height: 1.6; }

/* ═══════ FORMULA BOX ═══════ */
.formula-box {
  background: var(--bg-elevated);
  border: 1px solid var(--border);
  border-left: 3px solid var(--teal);
  border-radius: 0 var(--radius-md) var(--radius-md) 0;
  padding: 1rem 1.25rem;
  font-family: 'JetBrains Mono', monospace;
  font-size: 0.84rem;
  color: var(--text-hi);
  line-height: 2;
  margin: 0.5rem 0;
}

/* ═══════ EQUIP ITEM ═══════ */
.equip-item {
  display: flex; align-items: center; gap: 0.65rem;
  background: rgba(20,184,166,0.04);
  border: 1px solid rgba(20,184,166,0.12);
  border-radius: 8px;
  padding: 0.5rem 0.9rem;
  font-size: 0.86rem; color: var(--text-hi);
  margin-bottom: 0.4rem;
}
.equip-dot {
  width: 8px; height: 8px; border-radius: 50%;
  background: var(--teal); flex-shrink: 0;
}

/* ═══════ COMPARE TABLE ═══════ */
.cmp-table { width: 100%; border-collapse: collapse; }
.cmp-table th {
  background: var(--bg-elevated);
  color: var(--teal);
  font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px;
  padding: 0.7rem 1rem; text-align: left;
  border-bottom: 1px solid var(--border-teal);
}
.cmp-table td {
  padding: 0.65rem 1rem;
  font-size: 0.88rem; color: var(--text-hi);
  border-bottom: 1px solid var(--border);
  font-family: 'JetBrains Mono', monospace;
}
.cmp-table tr:last-child td { border-bottom: none; }
.cmp-table tr:hover td { background: var(--teal-glow); }
.cmp-label { font-family: 'Sora', sans-serif; color: var(--text-mid); font-size: 0.85rem; }
.win { color: var(--teal) !important; font-weight: 700; }

/* ═══════ STREAMLIT OVERRIDES ═══════ */
.stButton > button {
  background: linear-gradient(135deg, var(--teal-dark), var(--teal));
  color: #041010; font-weight: 700; border: none;
  border-radius: var(--radius-md); padding: 0.65rem 2rem;
  font-size: 0.92rem; letter-spacing: 0.3px;
  transition: all 0.2s ease;
  font-family: 'Sora', sans-serif;
}
.stButton > button:hover {
  background: linear-gradient(135deg, var(--teal), #2DD4BF);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(20,184,166,0.4);
}
.stDownloadButton > button {
  background: linear-gradient(135deg, #1B2E4A, #1E3A5F) !important;
  color: var(--sky) !important;
  border: 1px solid rgba(56,189,248,0.35) !important;
  border-radius: var(--radius-md) !important;
  font-family: 'Sora', sans-serif !important;
  font-weight: 600 !important;
}
.stDownloadButton > button:hover {
  box-shadow: 0 6px 20px rgba(56,189,248,0.25) !important;
  transform: translateY(-2px) !important;
}
/* inputs */
.stNumberInput input, .stTextInput input {
  background: var(--bg-input) !important;
  border: 1px solid var(--border) !important;
  color: var(--text-hi) !important;
  border-radius: 8px !important;
  font-family: 'JetBrains Mono', monospace !important;
}
.stNumberInput input:focus, .stTextInput input:focus {
  border-color: var(--teal) !important;
  box-shadow: 0 0 0 3px var(--teal-glow) !important;
}
.stSelectbox > div > div {
  background: var(--bg-input) !important;
  border: 1px solid var(--border) !important;
  color: var(--text-hi) !important;
}
.stSlider > div > div { accent-color: var(--teal); }
/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 8px; }
.stTabs [data-baseweb="tab"] {
  color: var(--text-mid); font-weight: 500;
  font-family: 'Sora', sans-serif; font-size: 0.88rem;
  border-radius: 8px 8px 0 0; padding: 0.55rem 1.1rem;
}
.stTabs [aria-selected="true"] {
  color: var(--teal) !important;
  border-bottom-color: var(--teal) !important;
}
/* Expander */
details > summary {
  background: var(--bg-elevated) !important;
  border: 1px solid var(--border) !important;
  border-radius: 8px !important;
  color: var(--text-hi) !important;
  font-family: 'Sora', sans-serif !important;
}
/* Scrollbar */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: var(--bg-base); }
::-webkit-scrollbar-thumb { background: var(--teal-dark); border-radius: 3px; }
/* Alert */
.stAlert { border-radius: var(--radius-md) !important; }

/* Result section heading */
.result-heading {
  font-size: 1.1rem; font-weight: 700; color: var(--text-hi);
  margin: 1.5rem 0 1rem;
  display: flex; align-items: center; gap: 0.5rem;
}
.result-heading::after {
  content: '';
  flex: 1; height: 1px;
  background: linear-gradient(90deg, var(--border-teal), transparent);
  margin-left: 0.5rem;
}
</style>
""", unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  CONSTANTES PLOTLY
# ═══════════════════════════════════════════════════════════════════
_PLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(17,24,39,0.7)",
    font=dict(family="Sora, sans-serif", color="#94A3B8", size=11),
    margin=dict(l=55, r=30, t=55, b=50),
    legend=dict(
        bgcolor="rgba(26,34,54,0.9)",
        bordercolor="rgba(20,184,166,0.25)",
        borderwidth=1,
        font=dict(size=11),
    ),
    xaxis=dict(
        gridcolor="rgba(148,163,184,0.07)",
        linecolor="rgba(148,163,184,0.15)",
        zerolinecolor="rgba(148,163,184,0.15)",
    ),
    yaxis=dict(
        gridcolor="rgba(148,163,184,0.07)",
        linecolor="rgba(148,163,184,0.15)",
        zerolinecolor="rgba(148,163,184,0.15)",
    ),
    hoverlabel=dict(
        bgcolor="#1A2236",
        bordercolor="#14B8A6",
        font=dict(family="JetBrains Mono", size=12),
    ),
)

COLORS = dict(
    teal="#14B8A6", sky="#38BDF8", amber="#F59E0B",
    red="#F87171", purple="#A78BFA", green="#4ADE80",
)


# ═══════════════════════════════════════════════════════════════════
#  FONCTIONS FINANCIÈRES
# ═══════════════════════════════════════════════════════════════════

def van(investissement: float, flux_annuel: float, taux: float, duree: int) -> float:
    """Valeur Actuelle Nette (les flux = économies sur coûts = LCOE × énergie)."""
    pv_flux = sum(flux_annuel / (1 + taux) ** t for t in range(1, duree + 1))
    return pv_flux - investissement


def tri(investissement: float, flux_annuel: float, duree: int) -> float | None:
    """Taux de Rentabilité Interne via Newton-Raphson."""
    if flux_annuel <= 0:
        return None

    def npv(r):
        return -investissement + sum(flux_annuel / (1 + r) ** t for t in range(1, duree + 1))

    def dnpv(r):
        return sum(-t * flux_annuel / (1 + r) ** (t + 1) for t in range(1, duree + 1))

    r = 0.10
    for _ in range(300):
        f, df = npv(r), dnpv(r)
        if abs(df) < 1e-14:
            break
        r_new = r - f / df
        if abs(r_new - r) < 1e-9:
            r = r_new
            break
        r = max(r_new, -0.9999)
    return r * 100 if abs(npv(r)) < abs(investissement) * 0.001 else None


def lcoe(investissement: float, cout_om_annuel: float,
         energie_kwh: float, taux: float, duree: int) -> float | None:
    """LCOE en $/kWh : ratio coûts actualisés / énergie actualisée."""
    if energie_kwh <= 0:
        return None
    num = investissement + sum(cout_om_annuel / (1 + taux) ** t for t in range(1, duree + 1))
    den = sum(energie_kwh / (1 + taux) ** t for t in range(1, duree + 1))
    return num / den if den > 0 else None


def temps_retour(investissement: float, gain_annuel: float) -> float | None:
    """Temps de retour simple = Investissement / Gain annuel estimé."""
    if gain_annuel <= 0:
        return None
    return investissement / gain_annuel


def cashflow_series(investissement: float, cout_om: float,
                    valeur_energie: float, taux: float, duree: int):
    """
    Séries annuelles pour les graphiques.
    Le 'gain' est modélisé comme valeur économique de l'énergie produite
    (au coût de référence du réseau, ici LCOE lui-même × énergie × facteur).
    On utilise simplement : bénéfice brut = valeur_energie ($/an estimé).
    """
    annees = list(range(duree + 1))
    flux_brut, flux_actualise = [0], [0]
    cum_brut, cum_act = [-investissement], [-investissement]

    for t in range(1, duree + 1):
        fb = valeur_energie - cout_om
        fa = fb / (1 + taux) ** t
        flux_brut.append(fb)
        flux_actualise.append(fa)
        cum_brut.append(cum_brut[-1] + fb)
        cum_act.append(cum_act[-1] + fa)

    return annees, flux_brut, flux_actualise, cum_brut, cum_act


# ═══════════════════════════════════════════════════════════════════
#  GRAPHIQUES PLOTLY
# ═══════════════════════════════════════════════════════════════════

def fig_cashflow(annees, flux_brut, cum_brut, cum_act, titre, col_main):
    fig = go.Figure()

    bar_colors = [col_main if v >= 0 else COLORS["red"] for v in flux_brut]
    fig.add_trace(go.Bar(
        x=annees, y=flux_brut,
        name="Flux net annuel ($)",
        marker_color=bar_colors, opacity=0.65,
        hovertemplate="Année %{x}<br>Flux : <b>$%{y:,.0f}</b><extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=annees, y=cum_brut,
        name="Cash-flow cumulé ($)",
        line=dict(color=col_main, width=2.5),
        mode="lines+markers", marker=dict(size=5),
        hovertemplate="Année %{x}<br>Cumulé : <b>$%{y:,.0f}</b><extra></extra>",
    ))
    fig.add_trace(go.Scatter(
        x=annees, y=cum_act,
        name="CF actualisé cumulé ($)",
        line=dict(color=COLORS["sky"], width=2, dash="dot"),
        mode="lines",
        hovertemplate="Année %{x}<br>Actualisé : <b>$%{y:,.0f}</b><extra></extra>",
    ))
    fig.add_hline(y=0, line_dash="dash", line_color="rgba(255,255,255,0.2)", line_width=1)
    layout = dict(**_PLY_BASE, title=dict(text=titre, x=0.5, font=dict(size=14, color="#EEF2FF")))
    layout["xaxis"]["title"] = "Année"
    layout["yaxis"]["title"] = "Montant ($)"
    fig.update_layout(**layout)
    return fig


def fig_production_mensuelle(energie_annuelle, nom, col_main):
    mois = ["Jan", "Fév", "Mar", "Avr", "Mai", "Jun",
            "Jul", "Aoû", "Sep", "Oct", "Nov", "Déc"]
    # Profil type sinusoïdal
    base = [math.sin(math.pi * (i - 2) / 11) * 0.3 + 1 for i in range(12)]
    s = sum(base)
    prod = [energie_annuelle * b / s for b in base]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=mois, y=prod,
        marker=dict(
            color=prod,
            colorscale=[[0, "#1A2236"], [0.5, col_main], [1, "#E0FFF9"]],
            showscale=False,
        ),
        text=[f"{v/1000:.1f} MWh" for v in prod],
        textposition="outside", textfont=dict(size=9, color="#64748B"),
        hovertemplate="<b>%{x}</b><br>%{y:,.0f} kWh<extra></extra>",
    ))
    layout = dict(**_PLY_BASE, title=dict(text=f"Production mensuelle — {nom}", x=0.5, font=dict(size=14, color="#EEF2FF")))
    layout["yaxis"]["title"] = "Énergie (kWh)"
    fig.update_layout(**layout)
    return fig


def fig_couts(investissement, cout_om_total, col1, col2, titre):
    fig = go.Figure(go.Pie(
        labels=["Investissement initial", "Exploitation & Maintenance"],
        values=[investissement, cout_om_total],
        hole=0.58,
        marker=dict(colors=[col1, col2], line=dict(color="#0B1120", width=3)),
        textinfo="label+percent",
        textfont=dict(size=12, color="#EEF2FF"),
        hovertemplate="<b>%{label}</b><br>$%{value:,.0f}<br>%{percent}<extra></extra>",
    ))
    fig.update_layout(
        **_PLY_BASE,
        title=dict(text=titre, x=0.5, font=dict(size=14, color="#EEF2FF")),
        showlegend=True,
        annotations=[dict(text="Coûts", x=0.5, y=0.5,
                          font=dict(size=13, color="#94A3B8"), showarrow=False)],
    )
    return fig


def fig_comparaison(pv, eo):
    cats = ["Production<br>(MWh/an)", "LCOE<br>(¢/kWh)", "VAN<br>(k$)", "IRR<br>(%)"]
    pv_v = [
        pv["energie"] / 1000,
        (pv["lcoe"] or 0) * 100,
        pv["van"] / 1000,
        pv["irr"] or 0,
    ]
    eo_v = [
        eo["energie"] / 1000,
        (eo["lcoe"] or 0) * 100,
        eo["van"] / 1000,
        eo["irr"] or 0,
    ]
    fig = go.Figure()
    fig.add_trace(go.Bar(
        name="☀️ PV", x=cats, y=pv_v,
        marker_color=COLORS["amber"], opacity=0.85,
        text=[f"{v:.2f}" for v in pv_v], textposition="outside",
        textfont=dict(color=COLORS["amber"]),
    ))
    fig.add_trace(go.Bar(
        name="🌬️ Éolien", x=cats, y=eo_v,
        marker_color=COLORS["sky"], opacity=0.85,
        text=[f"{v:.2f}" for v in eo_v], textposition="outside",
        textfont=dict(color=COLORS["sky"]),
    ))
    layout = dict(**_PLY_BASE, barmode="group",
                  title=dict(text="Comparaison Photovoltaïque vs Éolien", x=0.5, font=dict(size=15, color="#EEF2FF")))
    fig.update_layout(**layout)
    return fig


def fig_radar(pv, eo):
    cats = ["Production", "VAN", "IRR", "LCOE\n(inverse)", "Coût\n(inverse)"]

    def norm(a, b, inverse=False):
        ref = max(abs(a), abs(b), 1e-9)
        va = abs(a) / ref * 100
        vb = abs(b) / ref * 100
        if inverse:
            va, vb = 100 - va + 10, 100 - vb + 10
        return va, vb

    p1, e1 = norm(pv["energie"], eo["energie"])
    p2, e2 = norm(pv["van"], eo["van"])
    p3, e3 = norm(pv["irr"] or 0, eo["irr"] or 0)
    p4, e4 = norm(pv["lcoe"] or 0, eo["lcoe"] or 0, inverse=True)
    p5, e5 = norm(pv["cout_total"], eo["cout_total"], inverse=True)

    pv_v = [p1, p2, p3, p4, p5]
    eo_v = [e1, e2, e3, e4, e5]

    fig = go.Figure()
    for v, name, col in [(pv_v, "☀️ PV", COLORS["amber"]), (eo_v, "🌬️ Éolien", COLORS["sky"])]:
        fig.add_trace(go.Scatterpolar(
            r=v + [v[0]], theta=cats + [cats[0]],
            fill="toself", name=name,
            line=dict(color=col, width=2.5),
            fillcolor=col.replace("#", "rgba(") + ",0.15)" if False else f"{col}26",
        ))
    fig.update_layout(
        **_PLY_BASE,
        polar=dict(
            bgcolor="rgba(17,24,39,0.7)",
            radialaxis=dict(range=[0, 110], showticklabels=False,
                            gridcolor="rgba(148,163,184,0.1)"),
            angularaxis=dict(gridcolor="rgba(148,163,184,0.1)",
                             tickfont=dict(size=11, color="#94A3B8")),
        ),
        title=dict(text="Profil de performance normalisé", x=0.5,
                   font=dict(size=14, color="#EEF2FF")),
        height=430,
    )
    return fig


# ═══════════════════════════════════════════════════════════════════
#  GÉNÉRATION PDF
# ═══════════════════════════════════════════════════════════════════

def generer_pdf(pv_res, eo_res):
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4,
                            leftMargin=2.2 * cm, rightMargin=2.2 * cm,
                            topMargin=2.5 * cm, bottomMargin=2.2 * cm)

    BG_DARK   = colors.HexColor("#0B1827")
    BG_MID    = colors.HexColor("#919191")
    TEAL      = colors.HexColor("#14B8A6")
    AMBER     = colors.HexColor("#F59E0B")
    SKY       = colors.HexColor("#38BDF8")
    GRAY_HI   = colors.HexColor("#000000")
    GRAY_MID  = colors.HexColor("#000000")
    WHITE     = colors.white
    GREEN     = colors.HexColor("#4ADE80")

    st_title = ParagraphStyle("titre", fontName="Helvetica-Bold",
                               fontSize=26, textColor=TEAL, alignment=TA_CENTER, spaceAfter=14, leading=32)
    st_sub   = ParagraphStyle("sub",   fontName="Helvetica",
                               fontSize=10, textColor=GRAY_MID, alignment=TA_CENTER, spaceAfter=2)
    st_h2    = ParagraphStyle("h2",    fontName="Helvetica-Bold",
                               fontSize=13, textColor=TEAL, spaceBefore=18, spaceAfter=8)
    st_h3    = ParagraphStyle("h3",    fontName="Helvetica-Bold",
                               fontSize=10, textColor=SKY, spaceBefore=10, spaceAfter=5)
    st_body  = ParagraphStyle("body",  fontName="Helvetica",
                               fontSize=9, textColor=GRAY_HI, spaceAfter=3, leading=13)
    st_small = ParagraphStyle("small", fontName="Helvetica",
                               fontSize=8, textColor=GRAY_MID, alignment=TA_CENTER)

    def tbl(data, col_w=None, header_bg=BG_DARK, stripe=True):
        t = Table(data, colWidths=col_w)
        style_cmds = [
            ("BACKGROUND", (0, 0), (-1, 0), header_bg),
            ("TEXTCOLOR",  (0, 0), (-1, 0), TEAL),
            ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE",   (0, 0), (-1, 0), 9),
            ("ALIGN",      (0, 0), (-1, -1), "CENTER"),
            ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING",    (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#2D3748")),
            ("FONTNAME",  (0, 1), (-1, -1), "Helvetica"),
            ("FONTSIZE",  (0, 1), (-1, -1), 8.5),
            ("TEXTCOLOR", (0, 1), (-1, -1), GRAY_HI),
        ]
        if stripe:
            for i in range(1, len(data)):
                if i % 2 == 0:
                    style_cmds.append(("BACKGROUND", (0, i), (-1, i), BG_MID))
        t.setStyle(TableStyle(style_cmds))
        return t

    story = []
    PW = A4[0] - 4.4 * cm  # page width minus margins

    # ── Cover ──
    story.append(Spacer(1, 1.5* cm))
    story.append(Paragraph("RAPPORT D'ANALYSE TECHNICO-ÉCONOMIQUE", st_title))
    story.append(Paragraph("Systèmes d'Énergies Renouvelables", st_sub))
    story.append(Paragraph("Photovoltaïque &amp; Éolien — Interface française — Résultats en USD ($)", st_sub))
    story.append(Spacer(1, 0.3 * cm))
    story.append(HRFlowable(width="100%", thickness=2, color=TEAL))
    story.append(Spacer(1, 0.4 * cm))
    story.append(Paragraph(f"Généré le {datetime.now().strftime('%d %B %Y à %H:%M')}", st_small))
    story.append(Spacer(1, 0.6 * cm))

    def section_pv(res):
        story.append(Paragraph("☀ MODULE PHOTOVOLTAÏQUE", st_h2))
        story.append(HRFlowable(width="100%", thickness=0.8, color=AMBER))
        story.append(Spacer(1, 0.3 * cm))

        story.append(Paragraph("Paramètres d'entrée", st_h3))
        inp = res["inputs"]
        data = [
            ["Paramètre", "Valeur", "Unité"],
            ["Puissance installée", f"{inp['puissance']:,.1f}", "kWc"],
            ["Irradiation solaire", f"{inp['irradiation']:,.0f}", "kWh/m²/an"],
            ["Performance Ratio", f"{inp['pr'] * 100:.1f}", "%"],
            ["Coût d'investissement", f"${inp['investissement']:,.2f}", "USD"],
            ["Coût maintenance annuel", f"${inp['cout_om']:,.2f}", "USD/an"],
            ["Durée de vie", f"{inp['duree']}", "ans"],
            ["Taux d'actualisation", f"{inp['taux'] * 100:.2f}", "%"],
        ]
        story.append(tbl(data, col_w=[8.5 * cm, 5.5 * cm, 3.5 * cm]))
        story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph("Résultats économiques", st_h3))
        irr_s = f"{res['irr']:.2f} %" if res["irr"] is not None else "N/A"
        lcoe_s = f"${res['lcoe']:.4f}/kWh" if res["lcoe"] else "N/A"
        tr_s = f"{res['tr']:.1f} ans" if res["tr"] else "N/A"
        data2 = [
            ["Indicateur", "Valeur"],
            ["Production annuelle", f"{res['energie']:,.0f} kWh/an"],
            ["LCOE", lcoe_s],
            ["VAN", f"${res['van']:,.2f}"],
            ["TRI (IRR)", irr_s],
            ["Temps de retour simple", tr_s],
            ["Coût total (invest + O&M)", f"${res['cout_total']:,.2f}"],
        ]
        story.append(tbl(data2, col_w=[10 * cm, 7.5 * cm]))
        story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph("Équipements du système PV", st_h3))
        equips = ["Panneaux photovoltaïques", "Onduleur (Inverter)",
                  "Structure de montage", "Câbles DC/AC",
                  "Protections électriques", "Compteur"]
        for eq in equips:
            story.append(Paragraph(f"• {eq}", st_body))

    def section_eo(res):
        story.append(Paragraph("🌬 MODULE ÉOLIEN", st_h2))
        story.append(HRFlowable(width="100%", thickness=0.8, color=SKY))
        story.append(Spacer(1, 0.3 * cm))

        story.append(Paragraph("Paramètres d'entrée", st_h3))
        inp = res["inputs"]
        data = [
            ["Paramètre", "Valeur", "Unité"],
            ["Puissance nominale", f"{inp['puissance']:,.1f}", "kW"],
            ["Vitesse vent moyenne", f"{inp['vent']:.1f}", "m/s"],
            ["Densité de l'air", f"{inp['densite']:.3f}", "kg/m³"],
            ["Coefficient Cp", f"{inp['cp']:.3f}", "—"],
            ["Facteur de charge", f"{inp['fc'] * 100:.1f}", "%"],
            ["Coût d'investissement", f"${inp['investissement']:,.2f}", "USD"],
            ["Coût maintenance annuel", f"${inp['cout_om']:,.2f}", "USD/an"],
            ["Durée de vie", f"{inp['duree']}", "ans"],
            ["Taux d'actualisation", f"{inp['taux'] * 100:.2f}", "%"],
        ]
        story.append(tbl(data, col_w=[8.5 * cm, 5.5 * cm, 3.5 * cm]))
        story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph("Résultats économiques", st_h3))
        irr_s = f"{res['irr']:.2f} %" if res["irr"] is not None else "N/A"
        lcoe_s = f"${res['lcoe']:.4f}/kWh" if res["lcoe"] else "N/A"
        tr_s = f"{res['tr']:.1f} ans" if res["tr"] else "N/A"
        data2 = [
            ["Indicateur", "Valeur"],
            ["Production annuelle", f"{res['energie']:,.0f} kWh/an"],
            ["LCOE", lcoe_s],
            ["VAN", f"${res['van']:,.2f}"],
            ["TRI (IRR)", irr_s],
            ["Temps de retour simple", tr_s],
            ["Coût total (invest + O&M)", f"${res['cout_total']:,.2f}"],
        ]
        story.append(tbl(data2, col_w=[10 * cm, 7.5 * cm]))
        story.append(Spacer(1, 0.4 * cm))

        story.append(Paragraph("Équipements du système éolien", st_h3))
        equips = ["Éolienne (turbine)", "Mât métallique",
                  "Pales aérodynamiques", "Générateur électrique",
                  "Onduleur de réseau", "Fondation en béton",
                  "Système de protection et contrôle"]
        for eq in equips:
            story.append(Paragraph(f"• {eq}", st_body))

    def section_cmp(pv, eo):
        story.append(PageBreak())
        story.append(Paragraph("⚖ ANALYSE COMPARATIVE", st_h2))
        story.append(HRFlowable(width="100%", thickness=0.8, color=TEAL))
        story.append(Spacer(1, 0.4 * cm))
        irr_pv = f"{pv['irr']:.2f} %" if pv["irr"] else "N/A"
        irr_eo = f"{eo['irr']:.2f} %" if eo["irr"] else "N/A"
        lcoe_pv = f"${pv['lcoe']:.4f}" if pv["lcoe"] else "N/A"
        lcoe_eo = f"${eo['lcoe']:.4f}" if eo["lcoe"] else "N/A"
        tr_pv = f"{pv['tr']:.1f} ans" if pv["tr"] else "N/A"
        tr_eo = f"{eo['tr']:.1f} ans" if eo["tr"] else "N/A"
        data = [
            ["Indicateur", "☀ PV", "🌬 Éolien"],
            ["Production (kWh/an)", f"{pv['energie']:,.0f}", f"{eo['energie']:,.0f}"],
            ["LCOE ($/kWh)", lcoe_pv, lcoe_eo],
            ["VAN ($)", f"${pv['van']:,.2f}", f"${eo['van']:,.2f}"],
            ["IRR (%)", irr_pv, irr_eo],
            ["Temps de retour", tr_pv, tr_eo],
            ["Investissement ($)", f"${pv['inputs']['investissement']:,.2f}", f"${eo['inputs']['investissement']:,.2f}"],
            ["Coût total ($)", f"${pv['cout_total']:,.2f}", f"${eo['cout_total']:,.2f}"],
        ]
        story.append(tbl(data, col_w=[7 * cm, 5.5 * cm, 5.5 * cm]))

    # Build story
    if pv_res:
        section_pv(pv_res)
    if eo_res:
        story.append(PageBreak())
        section_eo(eo_res)
    if pv_res and eo_res:
        section_cmp(pv_res, eo_res)

    # Footer
    story.append(Spacer(1, 1.2 * cm))
    story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#2D3748")))
    story.append(Spacer(1, 0.3 * cm))
    story.append(Paragraph(
        "ÉnergiePro — Analyse Technico-Économique des Énergies Renouvelables | "
        "Résultats en USD | Document généré automatiquement à des fins pédagogiques.",
        st_small
    ))

    doc.build(story)
    buf.seek(0)
    return buf.read()


# ═══════════════════════════════════════════════════════════════════
#  SESSION STATE
# ═══════════════════════════════════════════════════════════════════
if "pv" not in st.session_state:
    st.session_state["pv"] = None
if "eo" not in st.session_state:
    st.session_state["eo"] = None


# ═══════════════════════════════════════════════════════════════════
#  SIDEBAR
# ═══════════════════════════════════════════════════════════════════
with st.sidebar:
    st.sidebar.markdown("""
                        
<div style="text-align: center;">
    <img src="data:image/png;base64,{}" width="80">
    <h2>ÉNERGIEPRO</h2>
    <p style="color:gray;">Renouvelables · v2.0</p>
</div>
""".format(get_base64("logo.png")), unsafe_allow_html=True)

    page = st.radio(
        "nav",
        ["🏠 Accueil", "☀️ Photovoltaïque", "🌬️ Éolien",
         "⚖️ Comparaison", "📊 Résultats"],
        label_visibility="collapsed",
    )

    st.markdown("""
    <div class="sidebar-info">
      <div class="sidebar-info-title">ℹ Informations</div>
      Application d'analyse technico-économique pour systèmes PV et éoliens.<br><br>
      <b style="color:#14B8A6">Base économique :</b><br>
      Coûts d'investissement + exploitation + production énergétique<br><br>
      <b style="color:#38BDF8">Indicateurs :</b> VAN · IRR · LCOE · Temps de retour<br><br>
      <span style="color:#F59E0B">💵 Tous les résultats en USD</span>
    </div>
    """, unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  HELPER : affichage KPI
# ═══════════════════════════════════════════════════════════════════
def kpi_card(icon, label, value, unit, accent="teal"):
    return f"""
    <div class="kpi-card {accent}">
      <span class="kpi-icon">{icon}</span>
      <div class="kpi-label">{label}</div>
      <div class="kpi-value">{value}</div>
      <div class="kpi-unit">{unit}</div>
    </div>"""


def render_kpis(res, accent_main, accent_sec):
    e_fmt   = f"{res['energie']:,.0f}"
    van_fmt = f"${res['van']:,.0f}"
    irr_fmt = f"{res['irr']:.2f}" if res["irr"] else "—"
    lc_fmt  = f"${res['lcoe']:.4f}" if res["lcoe"] else "—"
    tr_fmt  = f"{res['tr']:.1f}" if res["tr"] else "—"
    ct_fmt  = f"${res['cout_total']:,.0f}"

    c = st.columns(6)
    cards = [
        ("⚡", "Production", e_fmt, "kWh/an", accent_main),
        ("💰", "VAN", van_fmt, "USD", "teal"),
        ("📈", "IRR", irr_fmt, "%", "sky"),
        ("🧮", "LCOE", lc_fmt, "$/kWh", accent_sec),
        ("⏱️", "Temps retour", tr_fmt, "années", "amber"),
        ("💼", "Coût Total", ct_fmt, "USD", "red"),
    ]
    for col, (icon, label, val, unit, acc) in zip(c, cards):
        with col:
            st.markdown(kpi_card(icon, label, val, unit, acc), unsafe_allow_html=True)


# ═══════════════════════════════════════════════════════════════════
#  PAGE : ACCUEIL
# ═══════════════════════════════════════════════════════════════════
if page == "🏠 Accueil":

    st.markdown("""
    <div class="hero">
      <div class="hero-eyebrow"><img src="data:image/png;base64,{}" width="80"> Analyse Technico-Économique</div>
      <div class="hero-title">Optimisez vos projets<br><em>d'énergies renouvelables</em></div>
      <div class="hero-body">
        Une plateforme professionnelle pour évaluer la viabilité économique
        de vos systèmes photovoltaïques et éoliens — basée exclusivement sur
        les coûts et la production énergétique.
      </div>
      <div class="badge-row">
        <span class="badge">☀️ Photovoltaïque</span>
        <span class="badge">🌬️ Éolien</span>
        <span class="badge">📊 VAN · IRR · LCOE</span>
        <span class="badge">💵 USD</span>
        <span class="badge">📥 Export PDF</span>
      </div>
    </div>
    """.format(get_base64("logo.png")), unsafe_allow_html=True)

    # Feature cards
    fc = st.columns(4)
    feats = [
        ("☀️", "Module PV",      "Analyse complète d'un système solaire : production, LCOE, VAN, IRR, retour sur investissement."),
        ("🌬️", "Module Éolien",  "Modélisation physique P = ½ρAV³Cp, énergie annuelle, indicateurs économiques avancés."),
        ("⚖️", "Comparaison",    "Mise en regard des deux technologies : graphes interactifs, tableau et radar de performance."),
        ("📥", "Export PDF",      "Rapport complet en français avec paramètres, résultats, tableaux et analyse économique."),
    ]
    for col, (icon, title, desc) in zip(fc, feats):
        with col:
            st.markdown(f"""
            <div class="feat-card">
              <div class="feat-icon">{icon}</div>
              <div class="feat-title">{title}</div>
              <div class="feat-desc">{desc}</div>
            </div>""", unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    col_f, col_e = st.columns(2)
    with col_f:
        st.markdown("<div style='color:#EEF2FF;font-weight:700;font-size:1rem;margin-bottom:0.8rem;'>📐 Formules clés</div>", unsafe_allow_html=True)
        st.markdown("""
        <div class="formula-box">
          <span style="color:#F59E0B">☀ PV :</span>  E = P × Irradiation × PR<br>
          <span style="color:#38BDF8">🌬 Éolien :</span>  P = 0.5 × ρ × A × V³ × Cp<br>
          <span style="color:#38BDF8">         </span>  E = P × 8 760 × FC<br>
          <span style="color:#14B8A6">💰 VAN :</span>  Σ Ft/(1+r)^t  −  I₀<br>
          <span style="color:#14B8A6">📈 IRR :</span>  VAN(IRR) = 0  [numérique]<br>
          <span style="color:#14B8A6">🧮 LCOE :</span>  ΣCoûts_act / ΣÉnergie_act<br>
          <span style="color:#F59E0B">⏱ Retour :</span>  I₀ / Gain annuel net
        </div>""", unsafe_allow_html=True)

    with col_e:
        st.markdown("<div style='color:#EEF2FF;font-weight:700;font-size:1rem;margin-bottom:0.8rem;'>⚙️ Approche économique</div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:#1A2236;border:1px solid rgba(148,163,184,0.12);
             border-radius:10px;padding:1rem 1.2rem;font-size:0.84rem;
             color:#94A3B8;line-height:1.9;">
          L'analyse est <b style="color:#14B8A6">exclusivement basée sur les coûts</b>
          et la production énergétique, sans recours au prix de vente de l'électricité.<br><br>
          • Le <b style="color:#EEF2FF">LCOE</b> représente le coût réel par kWh produit.<br>
          • La <b style="color:#EEF2FF">VAN</b> et l'<b style="color:#EEF2FF">IRR</b>
            sont calculées sur des flux économiques internes (valeur économique
            de l'énergie = LCOE de référence × production).<br>
          • Le <b style="color:#EEF2FF">temps de retour simple</b> = I₀ / gain annuel net.
        </div>""", unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    st.info("👈 Utilisez le menu latéral pour commencer votre analyse PV ou Éolien.")


# ═══════════════════════════════════════════════════════════════════
#  PAGE : PHOTOVOLTAÏQUE
# ═══════════════════════════════════════════════════════════════════
elif page == "☀️ Photovoltaïque":

    st.markdown("""
    <div class="sec-head">
      <span class="sec-icon">☀️</span>
      <span class="sec-title">Module Photovoltaïque</span>
    </div>
    <div class="sec-sub">
      Analyse technico-économique d'un système PV — basée sur coûts &amp; production — Résultats en USD
    </div>
    """, unsafe_allow_html=True)

    # Équipements
    with st.expander("⚙️ Équipements du système PV", expanded=False):
        ec1, ec2 = st.columns(2)
        equips = ["Panneaux photovoltaïques", "Onduleur (Inverter)",
                  "Structure de montage", "Câbles DC/AC",
                  "Protections électriques", "Compteur"]
        for i, eq in enumerate(equips):
            with (ec1 if i < 3 else ec2):
                st.markdown(f'<div class="equip-item"><span class="equip-dot"></span>{eq}</div>',
                            unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # Paramètres
    st.markdown('<div class="param-panel">', unsafe_allow_html=True)
    st.markdown('<div class="param-title">🔢 Paramètres d\'entrée</div>', unsafe_allow_html=True)

    r1a, r1b, r1c = st.columns(3)
    with r1a:
        pv_p   = st.number_input("⚡ Puissance installée (kWc)", 1.0, 100_000.0, 100.0, 5.0, key="pvp")
        pv_irr = st.number_input("☀️ Irradiation (kWh/m²/an)", 500.0, 3000.0, 1800.0, 50.0, key="pvir")
    with r1b:
        pv_pr  = st.slider("🔧 Performance Ratio (%)", 60, 100, 80, key="pvpr") / 100
        pv_inv = st.number_input("💰 Investissement ($)", 1_000.0, 100_000_000.0, 150_000.0, 1_000.0, key="pvin")
    with r1c:
        pv_dur = st.slider("📅 Durée de vie (ans)", 5, 40, 25, key="pvdur")
        pv_taux = st.slider("📊 Taux actualisation (%)", 1, 20, 7, key="pvtaux") / 100

    pv_om_default = float(round(pv_inv * 0.015, 0))
    r2a, r2b = st.columns([2, 1])
    with r2a:
        pv_om = st.number_input("🔩 Coût maintenance annuel ($)", 0.0, 5_000_000.0, pv_om_default, 100.0, key="pvom")
    with r2b:
        pv_ref_lcoe = st.number_input("📌 LCOE de référence réseau ($/kWh)", 0.05, 0.50, 0.12, 0.01,
                                       format="%.3f", key="pvref",
                                       help="Coût du kWh sur le réseau utilisé pour calculer la valeur économique de la production")

    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 Lancer l'analyse PV", use_container_width=True):
        energie   = pv_p * pv_irr * pv_pr
        lcoe_val  = lcoe(pv_inv, pv_om, energie, pv_taux, pv_dur)
        gain_ann  = energie * pv_ref_lcoe  # valeur économique annuelle
        flux_net  = gain_ann - pv_om
        van_val   = van(pv_inv, flux_net, pv_taux, pv_dur)
        irr_val   = tri(pv_inv, flux_net, pv_dur)
        tr_val    = temps_retour(pv_inv, flux_net)
        cout_tot  = pv_inv + pv_om * pv_dur

        res = dict(
            energie=energie, lcoe=lcoe_val, van=van_val,
            irr=irr_val, tr=tr_val, cout_total=cout_tot,
            gain_ann=gain_ann, flux_net=flux_net,
            inputs=dict(puissance=pv_p, irradiation=pv_irr, pr=pv_pr,
                        investissement=pv_inv, cout_om=pv_om,
                        duree=pv_dur, taux=pv_taux),
        )
        st.session_state["pv"] = res

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown('<div class="result-heading">📊 Résultats</div>', unsafe_allow_html=True)
        render_kpis(res, "amber", "sky")

        st.markdown("<br>", unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["📈 Cash-Flow", "⚡ Production Mensuelle", "🧾 Répartition Coûts"])

        annees, fb, fa, cb, ca = cashflow_series(pv_inv, pv_om, gain_ann, pv_taux, pv_dur)
        with t1:
            st.plotly_chart(fig_cashflow(annees, fb, cb, ca, "Cash-Flow — Système PV", COLORS["amber"]),
                            use_container_width=True)
        with t2:
            st.plotly_chart(fig_production_mensuelle(energie, "PV", COLORS["amber"]),
                            use_container_width=True)
        with t3:
            st.plotly_chart(fig_couts(pv_inv, pv_om * pv_dur, COLORS["amber"], COLORS["sky"],
                                       "Répartition des coûts PV"),
                            use_container_width=True)

        # Tableau annuel
        with st.expander("📋 Tableau des flux annuels", expanded=False):
            df_rows = []
            cum = -pv_inv
            cum_a = -pv_inv
            for t in range(1, pv_dur + 1):
                act = flux_net / (1 + pv_taux) ** t
                cum += flux_net
                cum_a += act
                df_rows.append({"Année": t, "Gain économique ($)": f"${gain_ann:,.0f}",
                                 "Maintenance ($)": f"${pv_om:,.0f}",
                                 "Flux net ($)": f"${flux_net:,.0f}",
                                 "Flux actualisé ($)": f"${act:,.0f}",
                                 "CF cumulé ($)": f"${cum:,.0f}"})
            st.dataframe(pd.DataFrame(df_rows), use_container_width=True, hide_index=True)

        st.success("✅ Analyse PV terminée et sauvegardée pour la comparaison.")


# ═══════════════════════════════════════════════════════════════════
#  PAGE : ÉOLIEN
# ═══════════════════════════════════════════════════════════════════
elif page == "🌬️ Éolien":

    st.markdown("""
    <div class="sec-head">
      <span class="sec-icon">🌬️</span>
      <span class="sec-title">Module Éolien</span>
    </div>
    <div class="sec-sub">
      Analyse technico-économique d'un système éolien — basée sur coûts &amp; production — Résultats en USD
    </div>
    """, unsafe_allow_html=True)

    with st.expander("⚙️ Équipements du système éolien", expanded=False):
        ec1, ec2 = st.columns(2)
        equips_w = ["Éolienne (turbine)", "Mât métallique",
                    "Pales aérodynamiques", "Générateur électrique",
                    "Onduleur de réseau", "Fondation en béton",
                    "Système de protection et contrôle"]
        for i, eq in enumerate(equips_w):
            with (ec1 if i < 4 else ec2):
                st.markdown(f'<div class="equip-item"><span class="equip-dot" style="background:#38BDF8"></span>{eq}</div>',
                            unsafe_allow_html=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    st.markdown('<div class="param-panel">', unsafe_allow_html=True)
    st.markdown('<div class="param-title">🔢 Paramètres d\'entrée</div>', unsafe_allow_html=True)

    w1, w2, w3 = st.columns(3)
    with w1:
        eo_p    = st.number_input("🌀 Puissance nominale (kW)", 1.0, 50_000.0, 500.0, 10.0, key="eop")
        eo_vent = st.number_input("💨 Vitesse vent moyenne (m/s)", 1.0, 30.0, 7.5, 0.5, key="eov")
    with w2:
        eo_rho  = st.number_input("🌡️ Densité de l'air (kg/m³)", 0.9, 1.4, 1.225, 0.001, format="%.3f", key="eod")
        eo_cp   = st.slider("⚙️ Coefficient Cp", 0.10, 0.59, 0.40, 0.01, key="eocp")
    with w3:
        eo_fc   = st.slider("📊 Facteur de charge (%)", 10, 65, 30, key="eofc") / 100
        eo_inv  = st.number_input("💰 Investissement ($)", 1_000.0, 500_000_000.0, 1_500_000.0, 10_000.0, key="eoin")

    w4, w5 = st.columns(2)
    with w4:
        eo_dur  = st.slider("📅 Durée de vie (ans)", 5, 40, 20, key="eodur")
        eo_taux = st.slider("📊 Taux actualisation (%)", 1, 20, 8, key="eotaux") / 100
    with w5:
        eo_om_def = float(round(eo_inv * 0.025, 0))
        eo_om   = st.number_input("🔩 Maintenance annuelle ($)", 0.0, 20_000_000.0, eo_om_def, 1_000.0, key="eoom")
        eo_ref  = st.number_input("📌 LCOE de référence réseau ($/kWh)", 0.05, 0.50, 0.10, 0.01,
                                   format="%.3f", key="eoref",
                                   help="Coût du kWh réseau pour calculer la valeur économique de la production")

    # Info physique
    rayon_est = math.sqrt(eo_p * 1000 / max(0.5 * eo_rho * eo_vent ** 3 * eo_cp * math.pi, 1e-9))
    aire_est  = math.pi * rayon_est ** 2
    st.info(f"ℹ️ Rayon de rotor estimé : **{rayon_est:.1f} m** | Aire balayée : **{aire_est:,.1f} m²** "
            f"| Puissance spécifique : **{eo_p / max(aire_est, 1) * 1000:.0f} W/m²**")
    st.markdown('</div>', unsafe_allow_html=True)

    if st.button("🚀 Lancer l'analyse Éolien", use_container_width=True):
        energie  = eo_p * 8760 * eo_fc
        lcoe_val = lcoe(eo_inv, eo_om, energie, eo_taux, eo_dur)
        gain_ann = energie * eo_ref
        flux_net = gain_ann - eo_om
        van_val  = van(eo_inv, flux_net, eo_taux, eo_dur)
        irr_val  = tri(eo_inv, flux_net, eo_dur)
        tr_val   = temps_retour(eo_inv, flux_net)
        cout_tot = eo_inv + eo_om * eo_dur

        res = dict(
            energie=energie, lcoe=lcoe_val, van=van_val,
            irr=irr_val, tr=tr_val, cout_total=cout_tot,
            gain_ann=gain_ann, flux_net=flux_net,
            inputs=dict(puissance=eo_p, vent=eo_vent, densite=eo_rho,
                        cp=eo_cp, fc=eo_fc, investissement=eo_inv,
                        cout_om=eo_om, duree=eo_dur, taux=eo_taux),
        )
        st.session_state["eo"] = res

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown('<div class="result-heading">📊 Résultats</div>', unsafe_allow_html=True)
        render_kpis(res, "sky", "teal")

        st.markdown("<br>", unsafe_allow_html=True)
        t1, t2, t3 = st.tabs(["📈 Cash-Flow", "⚡ Production Mensuelle", "🧾 Répartition Coûts"])

        annees, fb, fa, cb, ca = cashflow_series(eo_inv, eo_om, gain_ann, eo_taux, eo_dur)
        with t1:
            st.plotly_chart(fig_cashflow(annees, fb, cb, ca, "Cash-Flow — Système Éolien", COLORS["sky"]),
                            use_container_width=True)
        with t2:
            st.plotly_chart(fig_production_mensuelle(energie, "Éolien", COLORS["sky"]),
                            use_container_width=True)
        with t3:
            st.plotly_chart(fig_couts(eo_inv, eo_om * eo_dur, COLORS["sky"], COLORS["teal"],
                                       "Répartition des coûts Éolien"),
                            use_container_width=True)

        with st.expander("📋 Tableau des flux annuels", expanded=False):
            df_rows = []
            cum = -eo_inv
            for t in range(1, eo_dur + 1):
                act = flux_net / (1 + eo_taux) ** t
                cum += flux_net
                df_rows.append({"Année": t, "Gain économique ($)": f"${gain_ann:,.0f}",
                                 "Maintenance ($)": f"${eo_om:,.0f}",
                                 "Flux net ($)": f"${flux_net:,.0f}",
                                 "Flux actualisé ($)": f"${act:,.0f}",
                                 "CF cumulé ($)": f"${cum:,.0f}"})
            st.dataframe(pd.DataFrame(df_rows), use_container_width=True, hide_index=True)

        st.success("✅ Analyse Éolien terminée et sauvegardée pour la comparaison.")


# ═══════════════════════════════════════════════════════════════════
#  PAGE : COMPARAISON
# ═══════════════════════════════════════════════════════════════════
elif page == "⚖️ Comparaison":

    st.markdown("""
    <div class="sec-head">
      <span class="sec-icon">⚖️</span>
      <span class="sec-title">Comparaison PV vs Éolien</span>
    </div>
    <div class="sec-sub">Analyse comparative des deux technologies — Résultats en USD</div>
    """, unsafe_allow_html=True)

    pv = st.session_state.get("pv")
    eo = st.session_state.get("eo")

    if not pv and not eo:
        st.warning("⚠️ Veuillez effectuer au moins une analyse (PV ou Éolien) avant d'accéder à la comparaison.")
        st.stop()

    if pv and eo:
        st.plotly_chart(fig_comparaison(pv, eo), use_container_width=True)

        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

        # Tableau comparatif HTML
        def _fmt_better(pv_val, eo_val, higher_is_better=True, is_cost=False, fmt="$"):
            """Retourne (pv_str, eo_str) avec la meilleure valeur en vert."""
            if pv_val is None or eo_val is None:
                pv_str = str(pv_val) if pv_val else "N/A"
                eo_str = str(eo_val) if eo_val else "N/A"
                return pv_str, eo_str, ""
            if is_cost:
                pv_better = pv_val <= eo_val
                eo_better = eo_val <= pv_val
            else:
                pv_better = pv_val >= eo_val if higher_is_better else pv_val <= eo_val
                eo_better = eo_val >= pv_val if higher_is_better else eo_val <= pv_val
            if fmt == "$":
                pv_s = f"${pv_val:,.2f}"
                eo_s = f"${eo_val:,.2f}"
            elif fmt == "%":
                pv_s = f"{pv_val:.2f} %"
                eo_s = f"{eo_val:.2f} %"
            elif fmt == "kwh":
                pv_s = f"{pv_val:,.0f} kWh"
                eo_s = f"{eo_val:,.0f} kWh"
            elif fmt == "yr":
                pv_s = f"{pv_val:.1f} ans"
                eo_s = f"{eo_val:.1f} ans"
            else:
                pv_s = f"{pv_val}"
                eo_s = f"{eo_val}"
            pv_cls = "win" if pv_better else ""
            eo_cls = "win" if eo_better else ""
            return pv_s, eo_s, pv_cls, eo_cls

        rows = []
        # Production
        p, e, pc, ec = _fmt_better(pv["energie"], eo["energie"], True, fmt="kwh")
        rows.append(("logo.png Production annuelle", p, e, pc, ec))
        # LCOE
        p, e, pc, ec = _fmt_better(pv["lcoe"], eo["lcoe"], False, is_cost=True, fmt="$")
        rows.append(("🧮 LCOE ($/kWh)", p, e, pc, ec))
        # VAN
        p, e, pc, ec = _fmt_better(pv["van"], eo["van"], True, fmt="$")
        rows.append(("💰 VAN ($)", p, e, pc, ec))
        # IRR
        irr_pv = pv["irr"] if pv["irr"] else None
        irr_eo = eo["irr"] if eo["irr"] else None
        if irr_pv and irr_eo:
            p, e, pc, ec = _fmt_better(irr_pv, irr_eo, True, fmt="%")
        else:
            p, e, pc, ec = (f"{irr_pv:.2f} %" if irr_pv else "N/A"), (f"{irr_eo:.2f} %" if irr_eo else "N/A"), "", ""
        rows.append(("📈 IRR (%)", p, e, pc, ec))
        # Temps retour
        tr_pv = pv["tr"]
        tr_eo = eo["tr"]
        if tr_pv and tr_eo:
            p, e, pc, ec = _fmt_better(tr_pv, tr_eo, False, is_cost=True, fmt="yr")
        else:
            p, e, pc, ec = (f"{tr_pv:.1f} ans" if tr_pv else "N/A"), (f"{tr_eo:.1f} ans" if tr_eo else "N/A"), "", ""
        rows.append(("⏱️ Temps de retour (ans)", p, e, pc, ec))
        # Investissement
        p, e, pc, ec = _fmt_better(pv["inputs"]["investissement"], eo["inputs"]["investissement"], False, is_cost=True, fmt="$")
        rows.append(("💼 Investissement ($)", p, e, pc, ec))
        # Coût total
        p, e, pc, ec = _fmt_better(pv["cout_total"], eo["cout_total"], False, is_cost=True, fmt="$")
        rows.append(("🏦 Coût total ($)", p, e, pc, ec))

        rows_html = "".join(
            f"<tr><td class='cmp-label'>{r[0]}</td>"
            f"<td class='{r[3]}'>{r[1]}</td>"
            f"<td class='{r[4]}'>{r[2]}</td></tr>"
            for r in rows
        )
        st.markdown(f"""
        <div style="background:#111827;border:1px solid rgba(20,184,166,0.2);
             border-radius:14px;padding:1.2rem;overflow:auto;margin-bottom:1.5rem;">
          <table class="cmp-table">
            <thead><tr>
              <th>Indicateur</th>
              <th>☀️ Photovoltaïque</th>
              <th>🌬️ Éolien</th>
            </tr></thead>
            <tbody>{rows_html}</tbody>
          </table>
          <div style="font-size:0.75rem;color:#4B5C72;margin-top:0.75rem;text-align:right;">
            🟢 Valeur surlignée = meilleure performance
          </div>
        </div>
        """, unsafe_allow_html=True)

        # Radar
        st.markdown("<div class='result-heading'>🕸️ Radar de performance normalisée</div>",
                    unsafe_allow_html=True)
        st.plotly_chart(fig_radar(pv, eo), use_container_width=True)

    elif pv:
        st.info("ℹ️ Seule l'analyse PV est disponible. Effectuez également l'analyse Éolien pour une comparaison complète.")
        render_kpis(pv, "amber", "sky")
    else:
        st.info("ℹ️ Seule l'analyse Éolien est disponible. Effectuez également l'analyse PV pour une comparaison complète.")
        render_kpis(eo, "sky", "teal")


# ═══════════════════════════════════════════════════════════════════
#  PAGE : RÉSULTATS & EXPORT
# ═══════════════════════════════════════════════════════════════════
elif page == "📊 Résultats":

    st.markdown("""
    <div class="sec-head">
      <span class="sec-icon">📊</span>
      <span class="sec-title">Résultats & Export PDF</span>
    </div>
    <div class="sec-sub">Synthèse de toutes les analyses — Téléchargement du rapport complet en USD</div>
    """, unsafe_allow_html=True)

    pv = st.session_state.get("pv")
    eo = st.session_state.get("eo")

    if not pv and not eo:
        st.warning("⚠️ Aucune analyse disponible. Effectuez d'abord une analyse PV ou Éolien.")
        st.stop()

    if pv:
        st.markdown('<div class="result-heading" style="color:#F59E0B;">☀️ Résultats Photovoltaïques</div>',
                    unsafe_allow_html=True)
        render_kpis(pv, "amber", "sky")

    if eo:
        st.markdown('<div class="result-heading" style="color:#38BDF8;margin-top:1.5rem;">🌬️ Résultats Éoliens</div>',
                    unsafe_allow_html=True)
        render_kpis(eo, "sky", "teal")

    # Tableau récap
    if pv and eo:
        st.markdown("<div class='divider'></div>", unsafe_allow_html=True)
        st.markdown('<div class="result-heading">📋 Tableau récapitulatif</div>', unsafe_allow_html=True)

        irr_pv = f"{pv['irr']:.2f} %" if pv["irr"] else "N/A"
        irr_eo = f"{eo['irr']:.2f} %" if eo["irr"] else "N/A"
        lcoe_pv = f"${pv['lcoe']:.4f}" if pv["lcoe"] else "N/A"
        lcoe_eo = f"${eo['lcoe']:.4f}" if eo["lcoe"] else "N/A"
        tr_pv = f"{pv['tr']:.1f} ans" if pv["tr"] else "N/A"
        tr_eo = f"{eo['tr']:.1f} ans" if eo["tr"] else "N/A"

        df_cmp = pd.DataFrame({
            "Indicateur": ["Production (kWh/an)", "LCOE ($/kWh)", "VAN ($)",
                           "IRR (%)", "Temps retour", "Investissement ($)", "Coût total ($)"],
            "☀️ PV": [f"{pv['energie']:,.0f}", lcoe_pv, f"${pv['van']:,.2f}",
                       irr_pv, tr_pv, f"${pv['inputs']['investissement']:,.2f}", f"${pv['cout_total']:,.2f}"],
            "🌬️ Éolien": [f"{eo['energie']:,.0f}", lcoe_eo, f"${eo['van']:,.2f}",
                           irr_eo, tr_eo, f"${eo['inputs']['investissement']:,.2f}", f"${eo['cout_total']:,.2f}"],
        })
        st.dataframe(df_cmp.set_index("Indicateur"), use_container_width=True)

    st.markdown("<div class='divider'></div>", unsafe_allow_html=True)

    # Export PDF
    col_info, col_btn = st.columns([2, 1])
    with col_info:
        st.markdown("""
        <div style="background:#1A2236;border:1px solid rgba(56,189,248,0.2);
             border-radius:12px;padding:1rem 1.2rem;font-size:0.86rem;color:#94A3B8;line-height:1.8;">
          <b style="color:#38BDF8">📄 Contenu du rapport PDF :</b><br>
          • Paramètres d'entrée complets (PV et/ou Éolien)<br>
          • Liste des équipements<br>
          • Résultats économiques détaillés : LCOE, VAN, IRR, Temps de retour<br>
          • Tableau comparatif (si les deux analyses sont effectuées)<br>
          • Résultats exprimés en dollars américains (USD)
        </div>""", unsafe_allow_html=True)
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        pdf_bytes = generer_pdf(pv, eo)
        st.download_button(
            label="📥 Télécharger le Rapport PDF",
            data=pdf_bytes,
            file_name=f"rapport_energies_renouvelables_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
            mime="application/pdf",
            use_container_width=True,
        )
        st.caption("Format A4 · Français · USD")