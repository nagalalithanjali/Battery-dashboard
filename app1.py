import streamlit as st
import pandas as pd
import plotly.graph_objects as go

st.set_page_config(layout="wide", page_title="Battery Lifecycle Ledger", page_icon="⚡")

# ── GLOBAL CSS ─────────────────────────────────────────────────────────────── #
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist+Mono:wght@400;600&family=Inter:wght@400;500;600;700&display=swap');

/* Hide Chrome */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; background-color: #080A0F; }

:root {
    --bg-main: #080A0F;
    --bg-card: #111620;
    --bg-hover: #181E29;
    --border: rgba(255,255,255,0.06);
    --border-hl: rgba(255,255,255,0.15);
    --text-main: #FFFFFF;
    --text-muted: #8A96A8;
    
    --teal: #00E5FF;
    --teal-dim: rgba(0, 229, 255, 0.1);
    --amber: #FF5722;
    --amber-dim: rgba(255, 87, 34, 0.1);
    --ghost: #F44336;
    --ghost-dim: rgba(244, 67, 54, 0.1);
    --green: #4CAF50;
}

body, .stApp { background: var(--bg-main) !important; color: var(--text-main) !important; font-family: 'Inter', sans-serif !important; }

/* Filter Selectbox Override */
.stSelectbox > div > div { background: var(--bg-card) !important; border: 1px solid var(--border) !important; color: var(--text-main) !important; font-family: 'Geist Mono', monospace !important; font-size: 14px !important; }
.stSelectbox { padding: 24px 48px 10px !important; }
.stSelectbox label { color: var(--teal) !important; font-family: 'Geist Mono', monospace !important; font-size: 11px !important; letter-spacing: 0.15em !important; text-transform: uppercase !important; }

/* Ledger Header Wrapper */
.header-wrapper {
    padding: 48px 48px 0;
}
.eyebrow {
    font-family: 'Geist Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.2em;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-bottom: 8px;
}
.title {
    font-size: 38px;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: var(--text-main);
    line-height: 1;
    margin-bottom: 6px;
}
.subtitle {
    font-size: 15px;
    color: var(--text-muted);
}

/* KPI Cards */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 16px;
    padding: 0 48px 24px;
}
.kpi-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 24px;
    box-shadow: 0 4px 24px rgba(0,0,0,0.2);
}
.kpi-label {
    font-family: 'Geist Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.1em;
    color: var(--text-muted);
    text-transform: uppercase;
    margin-bottom: 12px;
}
.kpi-val {
    font-size: 32px;
    font-weight: 600;
    line-height: 1;
    letter-spacing: -0.02em;
}
.kpi-val.teal { color: var(--teal); }
.kpi-val.amber { color: var(--amber); }
.kpi-val.green { color: var(--green); }
.kpi-unit {
    font-size: 13px;
    color: var(--text-muted);
    margin-left: 4px;
    font-weight: 400;
}

/* Plotly Wrapper */
.chart-wrapper {
    padding: 12px 48px;
    margin-bottom: 10px;
}

/* Ledger Data Table */
.ledger-wrapper {
    padding: 0 48px 48px;
}
.ledger-container {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    overflow: hidden;
}
.ledger-header {
    display: grid;
    grid-template-columns: 1.5fr 1.5fr 2fr 1.2fr 1.5fr;
    gap: 16px;
    padding: 16px 24px;
    border-bottom: 1px solid var(--border);
    background: rgba(0,0,0,0.2);
    font-family: 'Geist Mono', monospace;
    font-size: 10px;
    color: var(--text-muted);
    letter-spacing: 0.1em;
    text-transform: uppercase;
}
.ledger-row {
    display: grid;
    grid-template-columns: 1.5fr 1.5fr 2fr 1.2fr 1.5fr;
    gap: 16px;
    padding: 20px 24px;
    border-bottom: 1px solid var(--border);
    align-items: center;
    transition: background 0.2s;
}
.ledger-row:hover {
    background: var(--bg-hover);
}
.ledger-row:last-child {
    border-bottom: none;
}
.ghost-row {
    background: repeating-linear-gradient(45deg, transparent, transparent 10px, rgba(255,255,255,0.01) 10px, rgba(255,255,255,0.01) 20px);
}

/* Row Content */
.lr-status { display: flex; align-items: center; }
.badge {
    font-family: 'Geist Mono', monospace;
    font-size: 10px;
    padding: 4px 8px;
    border-radius: 4px;
    letter-spacing: 0.05em;
    font-weight: 600;
}
.badge.charge { background: var(--teal-dim); color: var(--teal); border: 1px solid rgba(0,229,255,0.2); }
.badge.discharge { background: var(--amber-dim); color: var(--amber); border: 1px solid rgba(255,87,34,0.2); }
.badge.ghost { background: var(--ghost-dim); color: var(--ghost); border: 1px dashed var(--ghost); }

.lr-date {
    font-size: 13px;
    color: var(--text-muted);
    line-height: 1.4;
}
.lr-partner {
    font-size: 14px;
    font-weight: 500;
    color: var(--text-main);
}
.amt {
    font-family: 'Geist Mono', monospace;
    font-size: 16px;
    font-weight: 600;
}
.amt.charge { color: var(--teal); }
.amt.discharge { color: var(--amber); }

.metric-chip {
    display: inline-block;
    background: rgba(255,255,255,0.05);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 4px 10px;
    font-size: 11px;
    color: var(--text-muted);
    margin-left: 6px;
    font-family: 'Geist Mono', monospace;
}
.metric-chip.co2 {
    color: var(--green);
    border-color: rgba(76, 175, 80, 0.3);
    background: rgba(76, 175, 80, 0.05);
}

</style>
""", unsafe_allow_html=True)


# ── DATA PROCESSING ─────────────────────────────────────────────────────────── #
@st.cache_data
def load_data():
    energy    = pd.read_csv("greenkwh.energy_sessions.csv")
    batteries = pd.read_csv("greenkwh.batteries.csv")
    systems   = pd.read_csv("greenkwh.systems.csv")

    energy['serial_number']    = energy['serial_number'].astype(str).str.strip().str.upper()
    batteries['serialnumber']  = batteries['serialnumber'].astype(str).str.strip().str.upper()
    systems['user_id']         = systems['user_id'].astype(str).str.strip()
    systems['user_name']       = systems['user_name'].astype(str).str.strip()

    date_col = next((c for c in ['created_at', 'timestamp', 'time'] if c in energy.columns), None)
    
    energy['created_at']  = pd.to_datetime(energy[date_col], errors='coerce')
    energy['system_type'] = energy['system_type'].astype(str).str.lower().str.strip()

    if 'mileage' in energy.columns:
        energy['milage'] = energy['mileage']

    user_map = dict(zip(systems['user_id'], systems['user_name']))
    return energy, batteries, user_map


energy, batteries, user_map = load_data()

# ── HEADER & FILTER ─────────────────────────────────────────────────────────── #
header_container = st.empty()
battery_list = batteries['serialnumber'].dropna().unique().tolist()
selected_battery = st.selectbox("BATTERY SERIAL FILTER", battery_list)

if not selected_battery:
    st.stop()

# ── COMPUTE METRICS ─────────────────────────────────────────────────────────── #
df = energy[energy['serial_number'] == selected_battery].copy()
df = df[df['system_type'].isin(['producer', 'consumer'])]
df = df.dropna(subset=['created_at'])
df['energy_change'] = pd.to_numeric(df['energy_change'], errors='coerce').abs()
df = df.sort_values('created_at', ascending=False).reset_index(drop=True)
df['user_id']   = df['user_id'].astype(str).str.strip()
df['user_name'] = df['user_id'].map(user_map).fillna("Unknown")

total_charged = round(df[df['system_type'] == 'producer']['energy_change'].sum(), 2)
total_discharged = round(df[df['system_type'] == 'consumer']['energy_change'].sum(), 2)
total_mileage = df['milage'].sum() if 'milage' in df.columns else 0
total_mileage = 0 if pd.isna(total_mileage) else total_mileage
total_co2 = round(total_mileage * 0.06, 2)

# Dynamic Header
header_container.markdown(f"""
<div class="header-wrapper">
    <div class="eyebrow">GREENKWH · BATTERY JOURNEY</div>
    <div class="title">ENERGY ROADMAP</div>
    <div class="subtitle"><span style="font-family:'Geist Mono',monospace; color:var(--teal);">{selected_battery}</span></div>
</div>
""", unsafe_allow_html=True)

# Dynamic KPI Deck
st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi-card">
    <div class="kpi-label">TOTAL CHARGED</div>
    <div class="kpi-val teal">{total_charged}<span class="kpi-unit">GreenKWh</span></div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">TOTAL DISCHARGED</div>
    <div class="kpi-val amber">{total_discharged}<span class="kpi-unit">GreenKWh</span></div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">TOTAL MILEAGE</div>
    <div class="kpi-val">{total_mileage:,.1f}<span class="kpi-unit">kilometers</span></div>
  </div>
  <div class="kpi-card">
    <div class="kpi-label">CO2 OFFSET</div>
    <div class="kpi-val green">{total_co2}<span class="kpi-unit">kilograms</span></div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── PLOTLY ANALYTICS ────────────────────────────────────────────────────────── #
chart_df = df.sort_values('created_at').copy()
chart_df['c_charge'] = chart_df.apply(lambda r: r['energy_change'] if r['system_type'] == 'producer' else 0, axis=1).cumsum()
chart_df['c_discharge'] = chart_df.apply(lambda r: r['energy_change'] if r['system_type'] == 'consumer' else 0, axis=1).cumsum()

fig = go.Figure()

fig.add_trace(go.Scatter(
    x=chart_df['created_at'],
    y=chart_df['c_charge'],
    mode='lines+markers',
    name='Cumulative Charged',
    line=dict(color='#00E5FF', width=2),
    marker=dict(color='#00E5FF', size=6, line=dict(color='#080A0F', width=1)),
    hovertemplate='Date: %{x}<br>Total Charged: %{y:.1f} GreenKWh<extra></extra>'
))

fig.add_trace(go.Scatter(
    x=chart_df['created_at'],
    y=chart_df['c_discharge'],
    mode='lines+markers',
    name='Cumulative Sold (Discharged)',
    line=dict(color='#FF5722', width=2),
    marker=dict(color='#FF5722', size=6, line=dict(color='#080A0F', width=1)),
    hovertemplate='Date: %{x}<br>Total Sold: %{y:.1f} GreenKWh<extra></extra>'
))

fig.update_layout(
    height=250,
    margin=dict(l=0, r=0, t=30, b=0),
    title=dict(text="CUMULATIVE ENERGY YIELD (GREENKWH)", font=dict(family='Geist Mono', size=11, color='#8A96A8')),
    paper_bgcolor='rgba(0,0,0,0)',
    plot_bgcolor='rgba(0,0,0,0)',
    xaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)', color='#8A96A8', tickfont=dict(family='Geist Mono', size=10)),
    yaxis=dict(showgrid=True, gridcolor='rgba(255,255,255,0.03)', color='#8A96A8', tickfont=dict(family='Geist Mono', size=10)),
    hoverlabel=dict(bgcolor="#111620", font_size=12, font_family="Inter", bordercolor="rgba(255,255,255,0.1)")
)

st.markdown('<div class="chart-wrapper">', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
st.markdown('</div>', unsafe_allow_html=True)


# ── AUDIT LEDGER ────────────────────────────────────────────────────────────── #
# Grouping matching logic
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

groups = build_groups(df)
final_groups = []
for i, g in enumerate(groups):
    final_groups.append(("real", g))
    if i + 1 < len(groups):
        cur_type  = g['system_type'].iloc[0]
        next_type = groups[i + 1]['system_type'].iloc[0]
        if cur_type == next_type:
            opposite = 'consumer' if cur_type == 'producer' else 'producer'
            final_groups.append(("ghost", opposite))

def _fmt_dt(dt):
    return dt.strftime("%y-%m-%d <span style='color:var(--text-muted);'>%H:%M</span>")

# Render Ledger
ledger_html = """
<div class="ledger-wrapper">
  <div class="ledger-container">
    <div class="ledger-header">
      <div>EVENT</div>
      <div>TIME</div>
      <div>LOCATION / PARTNER</div>
      <div style="text-align: right;">ENERGY (GREENKWH)</div>
      <div style="text-align: right;">METRICS</div>
    </div>
"""

for item in final_groups:
    kind = item[0]

    if kind == "ghost":
        ghost_type = item[1]
        loss_type = "CHARGE" if ghost_type == "producer" else "DISCHARGE"
        ledger_html += f"""
<div class="ledger-row ghost-row">
  <div class="lr-status"><div class="badge ghost">⚠️ UNRECORDED SESSION</div></div>
  <div class="lr-date">—</div>
  <div class="lr-partner" style="color:var(--text-muted);font-style:italic;">unrecorded session</div>
  <div class="lr-kwh" style="text-align: right; color:var(--text-muted);">—</div>
  <div class="lr-metrics" style="text-align: right;">
    <span class="metric-chip" style="color:var(--ghost);border-color:var(--ghost-dim);">gap in data</span>
  </div>
</div>
"""
    else:
        g           = item[1]
        system_type = g['system_type'].iloc[0]
        user_name   = g['user_name'].iloc[0]
        total_kwh   = round(g['energy_change'].sum(), 2)

        start_dt = g['created_at'].min()
        end_dt   = g['created_at'].max()
        if start_dt == end_dt:
            date_text = _fmt_dt(start_dt)
        else:
            date_text = f"{_fmt_dt(start_dt)} <br/>↓<br/> {_fmt_dt(end_dt)}"

        if system_type == "producer":
            badge = '<div class="badge charge">● Charge event (producer)</div>'
            soc_est = min(round((total_kwh / 100) * 100, 1), 100)
            metrics = f'<span class="metric-chip">SOC ~{soc_est:.0f}%</span>'
            amount  = f'<span class="amt charge">+{total_kwh:.1f}</span>'
        else:
            badge = '<div class="badge discharge">○ Discharge event (consumer)</div>'
            mileage_g = g['milage'].sum() if 'milage' in g.columns else 0
            mileage_g = 0 if pd.isna(mileage_g) else mileage_g
            co2_g     = round(mileage_g * 0.06, 2) if mileage_g > 0 else None
            m_text = f"{mileage_g:.1f} km" if mileage_g > 0 else "—"
            c_text = f"Offset: {co2_g:.2f} kg" if co2_g else "—"
            
            metrics = ""
            if mileage_g > 0: metrics += f'<span class="metric-chip">{m_text}</span>'
            if co2_g: metrics += f'<span class="metric-chip co2">{c_text}</span>'
            if not metrics: metrics = '<span class="metric-chip">—</span>'
            
            amount  = f'<span class="amt discharge">-{total_kwh:.1f}</span>'

        ledger_html += f"""
<div class="ledger-row">
  <div class="lr-status">{badge}</div>
  <div class="lr-date">{date_text}</div>
  <div class="lr-partner">{user_name}</div>
  <div class="lr-kwh" style="text-align: right;">{amount}</div>
  <div class="lr-metrics" style="text-align: right;">{metrics}</div>
</div>
"""

ledger_html += "</div></div>"
st.markdown(ledger_html, unsafe_allow_html=True)