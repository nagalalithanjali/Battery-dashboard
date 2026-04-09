import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Battery Journey Roadmap", page_icon="🔋")

# ── GLOBAL CSS ─────────────────────────────────────────────────────────────── #
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Roboto+Mono:wght@400;500&display=swap');

/* hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
.stSelectbox > div > div { background: #ffffff !important; border: 1px solid #E5E7EB !important; color: #111827 !important; font-family: 'Inter', sans-serif !important; font-size: 14px !important; border-radius: 6px !important; }
.stSelectbox { padding: 16px 40px 10px !important; }
.stSelectbox label { color: var(--muted) !important; font-family: 'Inter', sans-serif !important; font-size: 13px !important; font-weight: 500 !important; text-transform: none !important; letter-spacing: 0 !important; }

:root {
    --bg: #fffafa;
    --surface: #FFFFFF;
    --surface2: #F3F4F6;
    --border: #E5E7EB;
    --teal: #2E9D58;
    --teal-dim: rgba(46,157,88,0.12);
    --teal-mid: rgba(46,157,88,0.3);
    --amber: #E27A33;
    --amber-dim: rgba(226,122,51,0.12);
    --amber-mid: rgba(226,122,51,0.3);
    --muted: #6B7280;
    --text: #111827;
    --text2: #4B5563;
    --green: #2E9D58;
}

body, .stApp { background: var(--bg) !important; color: var(--text) !important; }

/* ── header ── */
.rm-header {
    padding: 32px 40px 24px;
    border-bottom: 1px solid var(--border);
}
.rm-eyebrow {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 500;
    color: var(--muted);
    margin-bottom: 6px;
}
.rm-title {
    font-family: 'Inter', sans-serif;
    font-size: 32px;
    font-weight: 600;
    color: var(--text);
    line-height: 1.1;
    margin-bottom: 8px;
}
.rm-serial {
    font-family: 'Roboto Mono', monospace;
    font-size: 14px;
    color: var(--teal);
}

/* ── stats bar ── */
.rm-stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    background: transparent;
    border: none;
    margin: 16px 40px 24px;
}
.stat-cell {
    padding: 22px 28px;
    border-radius: 12px;
}
.stat-cell:nth-child(1) { background: #E4F1F9; }
.stat-cell:nth-child(2) { background: #EAEFF6; }
.stat-cell:nth-child(3) { background: #E4F6EF; }
.stat-cell:nth-child(4) { background: #F0E6F4; }

.stat-label {
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 500;
    color: var(--text2);
    margin-bottom: 8px;
}
.stat-value {
    font-family: 'Inter', sans-serif;
    font-size: 28px;
    font-weight: 600;
    color: #111827 !important;
    line-height: 1;
}
.stat-value.teal  { color: var(--teal); }
.stat-value.amber { color: var(--amber); }
.stat-value.white { color: var(--text); }
.stat-value.green { color: var(--green); }
.stat-unit {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 500;
    color: var(--text2);
    display: inline-block;
    margin-left: 6px;
}

/* ── legend ── */
.rm-legend {
    display: flex;
    align-items: center;
    gap: 28px;
    padding: 14px 40px;
    border-bottom: none;
}
.legend-item {
    display: flex;
    align-items: center;
    gap: 8px;
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 500;
    color: var(--text);
    letter-spacing: 0.06em;
}
.legend-dot { width: 8px; height: 8px; border-radius: 50%; }
.ld-teal  { background: var(--teal); }
.ld-amber { background: var(--amber); }

/* ── timeline body ── */
.rm-body {
    display: grid;
    grid-template-columns: 1fr 60px 1fr;
    padding: 0 40px;
    position: relative;
}

/* column headers */
.col-head {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 28px 0 16px;
}
.col-head-label {
    font-family: 'Inter', sans-serif;
    font-size: 16px;
    font-weight: 600;
    white-space: nowrap;
}
.col-head-label.teal  { color: var(--teal); }
.col-head-label.amber { color: var(--amber); }
.col-head-line {
    flex: 1;
    height: 1px;
}

/* spine & timeline layout */
.t-left { display: flex; justify-content: flex-end; }
.t-center { display: flex; justify-content: center; position: relative; }
.t-right { display: flex; justify-content: flex-start; }

.spine-line {
    position: absolute;
    top: 0; bottom: 0;
    width: 2px;
    background: linear-gradient(to bottom, transparent, var(--border) 5%, var(--border) 95%, transparent);
    left: 50%;
    transform: translateX(-50%);
    z-index: 1;
}
.spine-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    border: 2px solid;
    position: relative;
    z-index: 2;
    margin-top: 22px;
    flex-shrink: 0;
    background-color: var(--bg);
}
.spine-dot.teal  { border-color: var(--teal);  background: var(--teal-dim); }
.spine-dot.amber { border-color: var(--amber); background: var(--amber-dim); }
.spine-dot.ghost { border-color: var(--muted); background: transparent; opacity: 0.4; }

@keyframes pulse-teal  { 0%,100%{box-shadow:0 0 0 0 rgba(46,157,88,.4)} 50%{box-shadow:0 0 0 6px rgba(46,157,88,0)} }
@keyframes pulse-amber { 0%,100%{box-shadow:0 0 0 0 rgba(226,122,51,.4)} 50%{box-shadow:0 0 0 6px rgba(226,122,51,0)} }
.spine-dot.teal.pulse  { animation: pulse-teal  2s infinite; }
.spine-dot.amber.pulse { animation: pulse-amber 2s infinite; }

/* event cards */
.event-card {
    display: flex;
    align-items: flex-start;
    margin-bottom: 28px;
    width: 100%;
}
.ec-charge    { flex-direction: row-reverse; }
.ec-discharge { flex-direction: row; }

.ec-connector {
    height: 2px;
    width: 36px;
    flex-shrink: 0;
    margin-top: 28px;
}
.ec-connector.teal-rev { background: linear-gradient(to left,  transparent, var(--teal-mid)); }
.ec-connector.amber-fwd { background: linear-gradient(to right, transparent, var(--amber-mid)); }

.ec-body {
    flex: 1;
    background: #ffffff;
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px 18px;
    position: relative;
    overflow: hidden;
    transition: all .2s;
    box-shadow: 0 4px 14px rgba(0,0,0,0.03);
}
.ec-body.charge { background: rgba(46,157,88,0.06); border: 1px solid rgba(46,157,88,0.25) !important; }
.ec-body.discharge { background: rgba(226,122,51,0.06); border: 1px solid rgba(226,122,51,0.25) !important; }
.ec-body:hover { border-color: rgba(0,0,0,0.18); box-shadow: 0 6px 20px rgba(0,0,0,0.05); }
.ec-body::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    border-radius: 8px 8px 0 0;
}
.ec-body.charge::before    { background: var(--teal); }
.ec-body.discharge::before { background: var(--amber); }
.ec-body.ghost {
    opacity: 0.38;
    border-style: dashed;
}

.ec-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 3px;
    margin-bottom: 10px;
}
.badge-charge    { color: var(--teal);  background: var(--teal-dim);  border: 1px solid rgba(46,157,88,.22); }
.badge-discharge { color: var(--amber); background: var(--amber-dim); border: 1px solid rgba(226,122,51,.22); }
.badge-ghost     { color: var(--muted); background: rgba(90,100,96,.1); border: 1px dashed rgba(90,100,96,.3); }

.ec-kwh {
    font-family: 'Inter', sans-serif;
    font-size: 24px;
    font-weight: 600;
    line-height: 1;
    margin-bottom: 8px;
}
.ec-kwh.charge    { color: var(--teal); }
.ec-kwh.discharge { color: var(--amber); }
.ec-kwh.ghost     { color: var(--muted); }
.ec-kwh-unit {
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 500;
    color: var(--text2);
    margin-left: 4px;
}

.ec-meta-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
}
.meta-label {
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 500;
    color: var(--muted);
    min-width: 70px;
}
.meta-val {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 500;
    color: var(--text);
}

.ec-extras {
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid var(--border);
    display: flex;
    gap: 20px;
}
.extra-label {
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    font-weight: 500;
    color: var(--muted);
    margin-bottom: 2px;
}
.extra-val {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 600;
    color: var(--text);
}
.extra-val.green { color: var(--green); }

.soc-badge {
    display: inline-block;
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    padding: 2px 7px;
    border-radius: 2px;
    margin-top: 8px;
    background: rgba(46,157,88,.1);
    color: var(--teal);
    border: 1px solid rgba(46,157,88,.2);
}
.progress-wrap {
    height: 3px;
    background: rgba(0,0,0,0.06);
    border-radius: 2px;
    margin-top: 5px;
    overflow: hidden;
}
.progress-fill {
    height: 100%;
    border-radius: 2px;
    background: var(--teal);
}

/* footer */
.rm-footer {
    padding: 20px 40px;
    border-top: 1px solid var(--border);
    margin-top: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.footer-note {
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    color: var(--muted);
}
/* Container padding for legend columns */
div[data-testid="stHorizontalBlock"] {
    padding: 14px 40px !important;
}

/* Custom Legend Buttons && Chart Wrapper */
[data-testid="stButton"] button {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    color: var(--text2) !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 14px !important;
    font-weight: 500 !important;
    padding: 0 !important;
    height: auto !important;
    display: inline-flex;
    align-items: center;
}
[data-testid="stButton"] button:hover {
    color: #000 !important;
}
[data-testid="stButton"] p {
    font-size: 11px !important;
    display: flex;
    align-items: center;
    margin: 0;
}

/* Inject colored dots into Legend - target by button key */
[data-testid="stButton"]:has(button[data-testid="btn_c"]) p,
button[data-testid="btn_c"] ~ * p,
[key="btn_c"] p { color: var(--teal) !important; }

[data-testid="stButton"]:has(button[data-testid="btn_d"]) p,
button[data-testid="btn_d"] ~ * p,
[key="btn_d"] p { color: var(--amber) !important; }

[data-testid="stButton"]:has(button[data-testid="btn_g"]) p,
[key="btn_g"] p { color: var(--muted) !important; }

/* fallback: color by column position */
div[data-testid="column"]:nth-child(1) [data-testid="stButton"] p { color: var(--teal) !important; font-weight: bold !important; }
div[data-testid="column"]:nth-child(2) [data-testid="stButton"] p { color: var(--amber) !important; font-weight: bold !important; }
div[data-testid="column"]:nth-child(3) [data-testid="stButton"] p { color: var(--muted) !important; font-weight: bold !important; }

.stPlotlyChart {
    padding: 0 40px !important; 
    margin-bottom: 24px;
}

/* Plotly Theme Overrides */
.modebar-btn { padding: 4px; }
.modebar-btn:hover svg { fill: #111827 !important; }

/* ── MOBILE RESPONSIVE ─────────────────────────────────────────────────────── */
@media (max-width: 768px) {

    /* header */
    .rm-header { padding: 20px 16px 16px; }
    .rm-title { font-size: 22px; }

    /* selectbox */
    .stSelectbox { padding: 12px 16px 8px !important; }

    /* stats: 2x2 grid on mobile */
    .rm-stats {
        grid-template-columns: 1fr 1fr;
        gap: 10px;
        margin: 12px 16px 16px;
    }
    .stat-cell { padding: 14px 16px; }
    .stat-value { font-size: 20px; }
    .stat-unit { font-size: 12px; }

    /* legend buttons row */
    div[data-testid="stHorizontalBlock"] {
        padding: 10px 16px !important;
        flex-wrap: wrap !important;
        gap: 8px !important;
    }
    div[data-testid="column"] {
        min-width: 0 !important;
        flex: 0 0 auto !important;
        width: auto !important;
    }

    /* plotly chart */
    .stPlotlyChart { padding: 0 16px !important; }

    /* timeline: 2-col grid, spine left, cards right */
    .rm-body {
        display: flex;
        flex-direction: column;
        padding: 0 12px 0 0;
        position: relative;
    }

    /* hide CHARGE / DISCHARGE column header labels only */
    .col-head { display: none; }

    /* spine line: fixed left position */
    .spine-line {
        left: 14px;
        transform: none;
    }

    /* each row becomes a flex row: dot on left, card on right */
    .t-left, .t-right, .t-center {
        display: contents;
    }

    /* wrap each row's dot + card together */
    .t-left, .t-right {
        display: flex;
        flex-direction: row;
        align-items: flex-start;
        width: 100%;
        margin-bottom: 0;
    }

    /* hide the now-redundant separate t-center divs */
    .t-center { display: none; }

    /* inject dot positioning via the event-card itself */
    .event-card {
        width: 100%;
        padding-left: 28px;
        position: relative;
    }

    /* dot: absolute positioned on the left spine */
    .event-card::before {
        content: '';
        position: absolute;
        left: 9px;
        top: 18px;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        border: 2px solid;
        z-index: 2;
        background-color: var(--bg);
    }
    .ec-charge::before  { border-color: var(--teal);  background: var(--teal-dim); }
    .ec-discharge::before { border-color: var(--amber); background: var(--amber-dim); }

    /* hide the original spine dots (they're in t-center which is now hidden) */
    .spine-dot { display: none; }

    /* remove row-reverse on charge cards */
    .ec-charge { flex-direction: row; }
    .ec-connector.teal-rev {
        background: linear-gradient(to right, transparent, var(--teal-mid));
    }

    /* connector shorter on mobile */
    .ec-connector { width: 16px; }

    /* card body full width */
    .ec-body { padding: 12px 14px; }
    .ec-kwh { font-size: 20px; }

    /* extras: stack vertically on very small screens */
    .ec-extras { flex-direction: column; gap: 8px; }

    /* footer: stack vertically */
    .rm-footer {
        flex-direction: column;
        align-items: flex-start;
        gap: 4px;
        padding: 16px;
    }
}
</style>

""", unsafe_allow_html=True)


# ── DATA LOADING ────────────────────────────────────────────────────────────── #
@st.cache_data
def load_data():
    energy    = pd.read_csv("greenkwh.energy_sessions.csv")
    batteries = pd.read_csv("greenkwh.batteries.csv")
    systems   = pd.read_csv("greenkwh.systems.csv")

    energy['serial_number']    = energy['serial_number'].astype(str).str.strip().str.upper()
    batteries['serialnumber']  = batteries['serialnumber'].astype(str).str.strip().str.upper()
    systems['user_id']         = systems['user_id'].astype(str).str.strip()
    systems['user_name']       = systems['user_name'].astype(str).str.strip()

    date_col = next(
        (c for c in ['created_at', 'timestamp', 'time', 'createdat'] if c in energy.columns),
        None
    )
    if not date_col:
        st.error("No datetime column found in energy sessions CSV.")
        st.stop()

    energy['created_at']  = pd.to_datetime(energy[date_col], errors='coerce')
    energy['system_type'] = energy['system_type'].astype(str).str.lower().str.strip()

    if 'mileage' in energy.columns:
        energy['milage'] = energy['mileage']

    user_map = dict(zip(systems['user_id'], systems['user_name']))
    return energy, batteries, user_map


# ── CARD BUILDERS ───────────────────────────────────────────────────────────── #
def _fmt_date(dt):
    return dt.strftime("%d %b %Y, %I:%M %p")


def charge_card(total_kwh: float, user_name: str, date_text: str) -> str:
    """Render a real charge card (left column)."""
    return f"""<div class="event-card ec-charge"><div class="ec-connector teal-rev"></div><div class="ec-body charge"><div class="ec-badge badge-charge">↑ CHARGED</div><div class="ec-kwh charge">{total_kwh:.2f}<span class="ec-kwh-unit">kWh</span></div><div class="ec-meta-row"><span class="meta-label">Producer</span><span class="meta-val">{user_name}</span></div><div class="ec-meta-row"><span class="meta-label">Date</span><span class="meta-val">{date_text}</span></div></div></div>"""


def discharge_card(total_kwh: float, user_name: str, date_text: str,
                   mileage: float | None, co2: float | None) -> str:
    """Render a real discharge card (right column)."""
    mileage_str = f"{mileage:.1f} km"  if mileage and mileage > 0 else None
    co2_str     = f"{co2:.1f} kg"      if co2    and co2    > 0 else None

    svg_mileage = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#141716" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="opacity:0.8"><polygon points="3 6 9 3 15 6 21 3 21 18 15 21 9 18 3 21"></polygon><line x1="9" y1="3" x2="9" y2="18"></line><line x1="15" y1="6" x2="15" y2="21"></line></svg>"""
    svg_co2 = """<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="color:var(--green);"><path d="M11 20A7 7 0 0 1 9.8 6.1C15.5 5 17 4.48 19 2c1 2 2 4.18 2 8 0 5.5-4.78 10-10 10Z"/><path d="M2 21c0-3 1.85-5.36 5.08-6C9.5 14.52 12 13 13 12"/></svg>"""

    extras = ""
    if mileage_str or co2_str:
        extras_items = ""
        if mileage_str:
            extras_items += f"""<div style="background: rgba(0,0,0,0.03); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(0,0,0,0.05); display: flex; align-items: center; gap: 8px;">{svg_mileage}<div><div class="extra-label">Mileage</div><div class="extra-val" style="color:#141716;">{mileage_str}</div></div></div>"""
        if co2_str:
            extras_items += f"""<div style="background: rgba(56,142,60,0.05); padding: 8px 12px; border-radius: 6px; border: 1px solid rgba(56,142,60,0.2); display: flex; align-items: center; gap: 8px;">{svg_co2}<div><div class="extra-label" style="color: rgba(56,142,60,0.8);">CO₂ Offset</div><div class="extra-val" style="color: var(--green); font-weight: 500;">{co2_str}</div></div></div>"""
        extras = f"""<div class="ec-extras" style="gap: 12px; margin-top: 14px; border-top: none;">{extras_items}</div>"""

    return f"""<div class="event-card ec-discharge"><div class="ec-connector amber-fwd"></div><div class="ec-body discharge"><div class="ec-badge badge-discharge">↓ DISCHARGED</div><div class="ec-kwh discharge">{total_kwh:.1f}<span class="ec-kwh-unit">kWh</span></div><div class="ec-meta-row"><span class="meta-label">Consumer</span><span class="meta-val">{user_name}</span></div><div class="ec-meta-row"><span class="meta-label">Date</span><span class="meta-val">{date_text}</span></div>{extras}</div></div>"""


def ghost_card(event_type: str) -> str:
    """Placeholder card for a missing / unrecorded session."""
    label  = "↑ CHARGED"    if event_type == "producer" else "↓ DISCHARGED"
    col    = "ec-charge"     if event_type == "producer" else "ec-discharge"
    conn   = "teal-rev"      if event_type == "producer" else "amber-fwd"
    kwh_c  = "charge"        if event_type == "producer" else "discharge"

    label_prefix = "Producer" if event_type == "producer" else "Consumer"
    not_rec = "SITE" if event_type == "producer" else "Not recorded"
    return f"""<div class="event-card {col}"><div class="ec-connector {conn}"></div><div class="ec-body {kwh_c} ghost"><div class="ec-badge badge-ghost">⬡ {label}</div><div class="ec-kwh ghost">—<span class="ec-kwh-unit">kWh</span></div><div class="ec-meta-row"><span class="meta-label">{label_prefix}</span><span class="meta-val">{not_rec}</span></div></div></div>"""


# ── GROUPING ────────────────────────────────────────────────────────────────── #
def build_groups(df: pd.DataFrame) -> list:
    groups = []
    current = []
    for _, row in df.iterrows():
        if not current:
            current.append(row)
            continue
        last = current[-1]
        if row['user_name'] == last['user_name'] and row['system_type'] == last['system_type']:
            current.append(row)
        else:
            groups.append(pd.DataFrame(current))
            current = [row]
    if current:
        groups.append(pd.DataFrame(current))
    return groups


def interleave_placeholders(groups: list) -> list:
    """Insert ghost placeholders between consecutive same-type groups."""
    final = []
    for i, g in enumerate(groups):
        final.append(("real", g))
        if i + 1 < len(groups):
            cur_type  = g['system_type'].iloc[0]
            next_type = groups[i + 1]['system_type'].iloc[0]
            if cur_type == next_type:
                opposite = 'consumer' if cur_type == 'producer' else 'producer'
                final.append(("ghost", opposite))
    return final


# ── MAIN RENDER ─────────────────────────────────────────────────────────────── #
energy, batteries, user_map = load_data()

battery_list       = batteries['serialnumber'].dropna().unique().tolist()
header_placeholder = st.empty()

selected_battery = st.selectbox("Battery Serial Filter", battery_list)

if not selected_battery:
    st.stop()

# ---- filter & clean ----
df = energy[energy['serial_number'] == selected_battery].copy()
df = df[df['system_type'].isin(['producer', 'consumer'])]
df = df[df['energy_change'].notna()]
df = df.dropna(subset=['created_at'])
df['energy_change'] = pd.to_numeric(df['energy_change'], errors='coerce').abs()
df = df.sort_values('created_at', ascending=False).reset_index(drop=True)
df['user_id']   = df['user_id'].astype(str).str.strip()
df['user_name'] = df['user_id'].map(user_map).fillna("Unknown")

# ---- summary stats ----
total_charged    = df[df['system_type'] == 'producer']['energy_change'].sum()
total_discharged = df[df['system_type'] == 'consumer']['energy_change'].sum()
total_mileage    = df['milage'].sum() if 'milage' in df.columns else 0
total_mileage    = 0 if pd.isna(total_mileage) else total_mileage
total_co2        = total_discharged * 2.4
mileage_display  = f"{total_mileage:.1f}" if total_mileage > 0 else "—"
co2_display      = f"{total_co2:.1f}" if total_co2 > 0 else "—"

# ---- header ----
header_placeholder.markdown(f"""
<div class="rm-header" style="border-bottom: none; padding-bottom: 8px;">
  <div class="rm-eyebrow">GreenKWh · Battery Journey</div>
  <div class="rm-title">Energy Roadmap</div>
  <div class="rm-serial">{selected_battery}</div>
</div>
""", unsafe_allow_html=True)

# ---- stats bar ----
st.markdown(f"""
<div class="rm-stats">
  <div class="stat-cell">
    <div class="stat-label">Total Charged</div>
    <div class="stat-value teal">{total_charged:.1f}<div class="stat-unit">kWh</div></div>
  </div>
  <div class="stat-cell">
    <div class="stat-label">Total Discharged</div>
    <div class="stat-value amber">{total_discharged:.1f}<div class="stat-unit">kWh</div></div>
  </div>
  <div class="stat-cell">
    <div class="stat-label">Total Mileage</div>
    <div class="stat-value white">{mileage_display}<div class="stat-unit">kilometers</div></div>
  </div>
  <div class="stat-cell">
    <div class="stat-label">CO₂ Offset</div>
    <div class="stat-value green">{co2_display}<div class="stat-unit">kilograms</div></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ---- interactive legend ----
if 'show_charge' not in st.session_state: st.session_state.show_charge = True
if 'show_discharge' not in st.session_state: st.session_state.show_discharge = True
if 'show_ghost' not in st.session_state: st.session_state.show_ghost = True

st.markdown('<div style="padding: 14px 40px;">', unsafe_allow_html=True)
cols = st.columns([1, 1, 1, 2])
c_lbl_t = "🟢 Charge event (producer)" if st.session_state.show_charge else "⚪ Charge event (hidden)"
d_lbl_t = "🟠 Discharge event (consumer)" if st.session_state.show_discharge else "⚪ Discharge event (hidden)"

if cols[0].button(c_lbl_t, key="btn_c"): st.session_state.show_charge = not st.session_state.show_charge; st.rerun()
if cols[1].button(d_lbl_t, key="btn_d"): st.session_state.show_discharge = not st.session_state.show_discharge; st.rerun()

# ── PLOTLY CHART ────────────────────────────────────────────────────────────── #
chart_df = df.sort_values('created_at').copy()

fig = go.Figure()
if st.session_state.show_charge:
    chart_df['c_charge'] = chart_df.apply(lambda r: r['energy_change'] if r['system_type'] == 'producer' else 0, axis=1).cumsum()
    fig.add_trace(go.Scatter(
        x=chart_df['created_at'],
        y=chart_df['c_charge'],
        mode='lines+markers',
        name='Cumulative Charged',
        line=dict(color='#2E9D58', width=2),
        marker=dict(color='#2E9D58', size=6, line=dict(color='#ffffff', width=1)),
        hovertemplate='Date: %{x}<br>Total Charged: %{y:.2f} kWh<extra></extra>'
    ))

if st.session_state.show_discharge:
    chart_df['c_discharge'] = chart_df.apply(lambda r: r['energy_change'] if r['system_type'] == 'consumer' else 0, axis=1).cumsum()
    fig.add_trace(go.Scatter(
        x=chart_df['created_at'],
        y=chart_df['c_discharge'],
        mode='lines+markers',
        name='Cumulative Discharged',
        line=dict(color='#E27A33', width=2),
        marker=dict(color='#E27A33', size=6, line=dict(color='#ffffff', width=1)),
        hovertemplate='Date: %{x}<br>Total Discharged: %{y:.2f} kWh<extra></extra>'
    ))

fig.update_layout(
    height=250,
    margin=dict(l=0, r=0, t=30, b=0),
    title=dict(text="CUMULATIVE ENERGY YIELD (KWH)", font=dict(family='Inter', size=13, color='#6B7280', weight='bold')),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)', color='#111827', tickfont=dict(family='Inter', size=12, color='#111827')),
    yaxis=dict(showgrid=True, gridcolor='rgba(0,0,0,0.1)', color='#111827', tickfont=dict(family='Inter', size=12, color='#111827')),
    hoverlabel=dict(bgcolor="#ffffff", font_size=13, font_family="Inter", font=dict(color="#111827")),
    showlegend=False
)

st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        'displayModeBar': True,
        'displaylogo': False,
        'modeBarButtonsToAdd': ['resetScale2d'],
        'modeBarButtonsToRemove': ['select2d', 'lasso2d'],
    }
)

# ── BUILD TIMELINE ──────────────────────────────────────────────────────────── #
groups        = build_groups(df)
final_groups  = interleave_placeholders(groups)
timeline_rows = []

filtered_groups = []
for item in final_groups:
    k = item[0]
    if k == "ghost" and not st.session_state.show_ghost: continue
    if k == "real":
        sys_t = item[1]['system_type'].iloc[0]
        if sys_t == "producer" and not st.session_state.show_charge: continue
        if sys_t == "consumer" and not st.session_state.show_discharge: continue
    filtered_groups.append(item)

pulse_teal  = True
pulse_amber = True

for item in filtered_groups:
    kind = item[0]

    left_content   = ""
    center_content = ""
    right_content  = ""

    if kind == "ghost":
        ghost_type = item[1]
        center_content = '<div class="spine-dot ghost"></div>'
        if ghost_type == "producer":
            left_content = ghost_card("producer")
        else:
            right_content = ghost_card("consumer")
    else:
        g           = item[1]
        system_type = g['system_type'].iloc[0]
        user_name   = g['user_name'].iloc[0]
        total_kwh   = g['energy_change'].sum()

        start_dt  = g['created_at'].min()
        end_dt    = g['created_at'].max()
        date_text = (_fmt_date(start_dt) if start_dt == end_dt
                     else f"{_fmt_date(start_dt)} → {_fmt_date(end_dt)}")

        if system_type == "producer":
            left_content = charge_card(total_kwh, user_name, date_text)
            cls = "spine-dot teal"
            if pulse_teal:
                cls += " pulse"
                pulse_teal = False
            center_content = f'<div class="{cls}"></div>'
        else:
            mileage_g = g['milage'].sum() if 'milage' in g.columns else 0
            mileage_g = 0 if pd.isna(mileage_g) else mileage_g
            co2_g     = total_kwh * 2.4
            right_content = discharge_card(total_kwh, user_name, date_text, mileage_g if mileage_g > 0 else None, co2_g if co2_g > 0 else None)
            cls = "spine-dot amber"
            if pulse_amber:
                cls += " pulse"
                pulse_amber = False
            center_content = f'<div class="{cls}"></div>'

    row_html = f'<div class="t-left">{left_content}</div><div class="t-center">{center_content}</div><div class="t-right">{right_content}</div>'
    timeline_rows.append(row_html)

rows_combined = "".join(timeline_rows)

timeline_html = f"""
<div class="rm-body">
  <div class="spine-line"></div>

  <!-- Row 0: Headers -->
  <div class="col-head" style="justify-content:flex-end;">
    <div class="col-head-line" style="background:linear-gradient(to left,transparent,rgba(46,157,88,.3))"></div>
    <div class="col-head-label teal">CHARGE</div>
  </div>
  <div class="t-center"></div>
  <div class="col-head" style="justify-content:flex-start;">
    <div class="col-head-label amber">DISCHARGE</div>
    <div class="col-head-line" style="background:linear-gradient(to right,transparent,rgba(226,122,51,.3))"></div>
  </div>

{rows_combined}
</div>

<div class="rm-footer">
  <div class="footer-note">GreenKWh Energy Platform · Battery Lifecycle Audit</div>
  <div class="footer-note">Battery: {selected_battery}</div>
</div>
"""

st.markdown(timeline_html, unsafe_allow_html=True)