import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="Battery Journey Roadmap", page_icon="🔋")

# ── GLOBAL CSS ─────────────────────────────────────────────────────────────── #
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@400;500&family=DM+Sans:wght@300;400;500&display=swap');

/* hide default streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }
.stSelectbox > div > div { background: #1c1f1e !important; border: 1px solid rgba(255,255,255,0.07) !important; color: #e8ece9 !important; font-family: 'DM Mono', monospace !important; font-size: 13px !important; }
.stSelectbox { padding: 16px 40px 10px !important; }
.stSelectbox label { color: var(--muted) !important; font-family: 'DM Mono', monospace !important; font-size: 11px !important; letter-spacing: 0.12em !important; text-transform: uppercase !important; }

:root {
    --bg: #0d0f0e;
    --surface: #141716;
    --surface2: #1c1f1e;
    --border: rgba(255,255,255,0.07);
    --teal: #2dd4a0;
    --teal-dim: rgba(45,212,160,0.12);
    --teal-mid: rgba(45,212,160,0.3);
    --amber: #f5a623;
    --amber-dim: rgba(245,166,35,0.12);
    --amber-mid: rgba(245,166,35,0.3);
    --muted: #5a6460;
    --text: #e8ece9;
    --text2: #8a9690;
    --green: #7dce82;
}

body, .stApp { background: var(--bg) !important; color: var(--text) !important; }

/* ── header ── */
.rm-header {
    padding: 32px 40px 24px;
    border-bottom: 1px solid var(--border);
}
.rm-eyebrow {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.18em;
    color: var(--muted);
    text-transform: uppercase;
    margin-bottom: 6px;
}
.rm-title {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 46px;
    letter-spacing: 0.04em;
    color: var(--text);
    line-height: 1;
    margin-bottom: 4px;
}
.rm-serial {
    font-family: 'DM Mono', monospace;
    font-size: 14px;
    color: var(--teal);
    letter-spacing: 0.06em;
}

/* ── stats bar ── */
.rm-stats {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1px;
    background: var(--border);
    border: 1px solid var(--border);
    border-radius: 8px;
    margin: 16px 40px 24px;
    overflow: hidden;
}
.stat-cell {
    background: var(--surface);
    padding: 22px 28px;
}
.stat-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 8px;
}
.stat-value {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 30px;
    letter-spacing: 0.04em;
    line-height: 1;
}
.stat-value.teal  { color: var(--teal); }
.stat-value.amber { color: var(--amber); }
.stat-value.white { color: var(--text); }
.stat-value.green { color: var(--green); }
.stat-unit {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: var(--text2);
    margin-top: 4px;
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
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: var(--text2);
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
    font-family: 'Bebas Neue', sans-serif;
    font-size: 15px;
    letter-spacing: 0.12em;
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

@keyframes pulse-teal  { 0%,100%{box-shadow:0 0 0 0 rgba(45,212,160,.4)} 50%{box-shadow:0 0 0 6px rgba(45,212,160,0)} }
@keyframes pulse-amber { 0%,100%{box-shadow:0 0 0 0 rgba(245,166,35,.4)} 50%{box-shadow:0 0 0 6px rgba(245,166,35,0)} }
.spine-dot.teal.pulse  { animation: pulse-teal  2s infinite; }
.spine-dot.amber.pulse { animation: pulse-amber 2s infinite; }

/* event cards */
.event-card {
    display: flex;
    align-items: flex-start;
    margin-bottom: 28px;
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
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 16px 18px;
    position: relative;
    overflow: hidden;
    transition: border-color .2s;
}
.ec-body:hover { border-color: rgba(255,255,255,0.15); }
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
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 3px;
    margin-bottom: 10px;
}
.badge-charge    { color: var(--teal);  background: var(--teal-dim);  border: 1px solid rgba(45,212,160,.22); }
.badge-discharge { color: var(--amber); background: var(--amber-dim); border: 1px solid rgba(245,166,35,.22); }
.badge-ghost     { color: var(--muted); background: rgba(90,100,96,.1); border: 1px dashed rgba(90,100,96,.3); }

.ec-kwh {
    font-family: 'Bebas Neue', sans-serif;
    font-size: 27px;
    letter-spacing: 0.04em;
    line-height: 1;
    margin-bottom: 8px;
}
.ec-kwh.charge    { color: var(--teal); }
.ec-kwh.discharge { color: var(--amber); }
.ec-kwh.ghost     { color: var(--muted); }
.ec-kwh-unit {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    font-weight: 400;
    color: var(--text2);
    margin-left: 4px;
    letter-spacing: 0.06em;
}

.ec-meta-row {
    display: flex;
    align-items: center;
    gap: 8px;
    margin-bottom: 4px;
}
.meta-label {
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: var(--muted);
    min-width: 44px;
}
.meta-val {
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    color: var(--text2);
}

.ec-extras {
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid var(--border);
    display: flex;
    gap: 20px;
}
.extra-label {
    font-family: 'DM Mono', monospace;
    font-size: 9px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 2px;
}
.extra-val {
    font-family: 'DM Mono', monospace;
    font-size: 12px;
    color: var(--text2);
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
    background: rgba(45,212,160,.1);
    color: var(--teal);
    border: 1px solid rgba(45,212,160,.2);
}
.progress-wrap {
    height: 3px;
    background: rgba(255,255,255,0.06);
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
    font-family: 'DM Mono', monospace;
    font-size: 10px;
    color: var(--muted);
    letter-spacing: 0.08em;
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


def charge_card(total_kwh: float, user_name: str, date_text: str, soc_pct: float | None = None) -> str:
    """Render a real charge card (left column)."""
    soc_html = ""
    if soc_pct is not None:
        soc_html = f"""
<div class="soc-badge">SOC after: {soc_pct:.0f}%</div>
<div class="progress-wrap"><div class="progress-fill" style="width:{min(soc_pct,100):.0f}%"></div></div>"""

    return f"""
<div class="event-card ec-charge">
  <div class="ec-connector teal-rev"></div>
  <div class="ec-body charge">
    <div class="ec-badge badge-charge">↑ CHARGED</div>
    <div class="ec-kwh charge">{total_kwh:.1f}<span class="ec-kwh-unit">GreenKWh</span></div>
    <div class="ec-meta-row"><span class="meta-label">Site</span><span class="meta-val">{user_name}</span></div>
    <div class="ec-meta-row"><span class="meta-label">Date</span><span class="meta-val">{date_text}</span></div>
    {soc_html}
  </div>
</div>"""


def discharge_card(total_kwh: float, user_name: str, date_text: str,
                   mileage: float | None, co2: float | None) -> str:
    """Render a real discharge card (right column)."""
    mileage_str = f"{mileage:.1f} km"  if mileage and mileage > 0 else "N/A"
    co2_str     = f"{co2:.2f} kg"      if co2    and co2    > 0 else "N/A"
    co2_class   = "green" if co2 and co2 > 0 else ""

    extras = f"""
<div class="ec-extras">
  <div>
    <div class="extra-label">Mileage</div>
    <div class="extra-val">{mileage_str}</div>
  </div>
  <div>
    <div class="extra-label">CO₂ offset</div>
    <div class="extra-val {co2_class}">{co2_str}</div>
  </div>
</div>"""

    return f"""
<div class="event-card ec-discharge">
  <div class="ec-connector amber-fwd"></div>
  <div class="ec-body discharge">
    <div class="ec-badge badge-discharge">↓ DISCHARGED</div>
    <div class="ec-kwh discharge">{total_kwh:.1f}<span class="ec-kwh-unit">GreenKWh</span></div>
    <div class="ec-meta-row"><span class="meta-label">Partner</span><span class="meta-val">{user_name}</span></div>
    <div class="ec-meta-row"><span class="meta-label">Date</span><span class="meta-val">{date_text}</span></div>
    {extras}
  </div>
</div>"""


def ghost_card(event_type: str) -> str:
    """Placeholder card for a missing / unrecorded session."""
    label  = "↑ CHARGED"    if event_type == "producer" else "↓ DISCHARGED"
    col    = "ec-charge"     if event_type == "producer" else "ec-discharge"
    conn   = "teal-rev"      if event_type == "producer" else "amber-fwd"
    kwh_c  = "charge"        if event_type == "producer" else "discharge"

    return f"""
<div class="event-card {col}">
  <div class="ec-connector {conn}"></div>
  <div class="ec-body {kwh_c} ghost">
    <div class="ec-badge badge-ghost">⬡ {label}</div>
    <div class="ec-kwh ghost">—<span class="ec-kwh-unit">GreenKWh</span></div>
    <div class="ec-meta-row"><span class="meta-label">Site</span><span class="meta-val">Not recorded</span></div>
  </div>
</div>"""


# ── GROUPING (same logic as original) ───────────────────────────────────────── #
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

battery_list     = batteries['serialnumber'].dropna().unique().tolist()
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
total_charged    = round(df[df['system_type'] == 'producer']['energy_change'].sum(), 2)
total_discharged = round(df[df['system_type'] == 'consumer']['energy_change'].sum(), 2)
total_mileage    = df['milage'].sum() if 'milage' in df.columns else 0
total_mileage    = 0 if pd.isna(total_mileage) else total_mileage
total_co2        = round(total_mileage * 0.06, 2)
mileage_display  = f"{total_mileage:,.1f}" if total_mileage > 0 else "—"

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
    <div class="stat-value teal">{total_charged}</div>
    <div class="stat-unit">GreenKWh</div>
  </div>
  <div class="stat-cell">
    <div class="stat-label">Total Discharged</div>
    <div class="stat-value amber">{total_discharged}</div>
    <div class="stat-unit">GreenKWh</div>
  </div>
  <div class="stat-cell">
    <div class="stat-label">Total Mileage</div>
    <div class="stat-value white">{mileage_display}</div>
    <div class="stat-unit">kilometers</div>
  </div>
  <div class="stat-cell">
    <div class="stat-label">CO₂ Offset</div>
    <div class="stat-value green">{total_co2}</div>
    <div class="stat-unit">kilograms</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ---- legend ----
st.markdown("""
<div class="rm-legend">
  <div class="legend-item"><div class="legend-dot ld-teal"></div> Charge event (producer)</div>
  <div class="legend-item"><div class="legend-dot ld-amber"></div> Discharge event (consumer)</div>
  <div class="legend-item" style="opacity:.5;font-style:italic;">⬡ unrecorded session</div>
</div>
""", unsafe_allow_html=True)

# ── BUILD TIMELINE ──────────────────────────────────────────────────────────── #
groups        = build_groups(df)
final_groups  = interleave_placeholders(groups)

timeline_rows = []

pulse_teal = True
pulse_amber = True

for item in final_groups:
    kind = item[0]

    left_content = ""
    center_content = ""
    right_content = ""

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
        total_kwh   = round(g['energy_change'].sum(), 2)

        start_dt = g['created_at'].min()
        end_dt   = g['created_at'].max()
        date_text = (_fmt_date(start_dt) if start_dt == end_dt
                     else f"{_fmt_date(start_dt)} → {_fmt_date(end_dt)}")

        if system_type == "producer":
            # Estimate SOC from energy change (capped at 100 for display)
            soc_est = min(round((total_kwh / 100) * 100, 1), 100)
            left_content = charge_card(total_kwh, user_name, date_text, soc_est)
            
            cls = "spine-dot teal"
            if pulse_teal:
                cls += " pulse"
                pulse_teal = False
            center_content = f'<div class="{cls}"></div>'
        else:
            mileage_g = g['milage'].sum() if 'milage' in g.columns else 0
            mileage_g = 0 if pd.isna(mileage_g) else mileage_g
            co2_g     = round(mileage_g * 0.06, 2) if mileage_g > 0 else None
            right_content = discharge_card(total_kwh, user_name, date_text, mileage_g or None, co2_g)
            
            cls = "spine-dot amber"
            if pulse_amber:
                cls += " pulse"
                pulse_amber = False
            center_content = f'<div class="{cls}"></div>'

    row_html = f"""
<div class="t-left">{left_content}</div>
<div class="t-center">{center_content}</div>
<div class="t-right">{right_content}</div>
    """
    timeline_rows.append(row_html)

rows_combined = "".join(timeline_rows)

timeline_html = f"""
<div class="rm-body">
  <div class="spine-line"></div>

  <!-- Row 0: Headers -->
  <div class="col-head" style="justify-content:flex-end;">
    <div class="col-head-line" style="background:linear-gradient(to left,transparent,rgba(45,212,160,.3))"></div>
    <div class="col-head-label teal">CHARGE</div>
  </div>
  <div class="t-center"></div>
  <div class="col-head" style="justify-content:flex-start;">
    <div class="col-head-label amber">DISCHARGE</div>
    <div class="col-head-line" style="background:linear-gradient(to right,transparent,rgba(245,166,35,.3))"></div>
  </div>

{rows_combined}
</div>

<div class="rm-footer">
  <div class="footer-note">GreenKWh Energy Platform · Battery Lifecycle Audit</div>
  <div class="footer-note">Battery: {selected_battery}</div>
</div>
"""

st.markdown(timeline_html, unsafe_allow_html=True)