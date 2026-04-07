import streamlit as st
import pandas as pd

st.set_page_config(layout="wide", page_title="User Energy Dashboard", page_icon="⚡")

# ── CONSTANTS ───────────────────────────────────────────────────────────────── #
PRICE_PER_KWH  = 16
PETROL_PER_LITRE = 107.5
SWAP_COST      = 80
CO2_PER_KWH    = 0.06

# ── GLOBAL CSS ─────────────────────────────────────────────────────────────── #
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=Roboto+Mono:wght@400;500&display=swap');

#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 0 !important; max-width: 100% !important; }

:root {
    --bg: #fffafa;
    --surface: #FFFFFF;
    --border: #E5E7EB;
    --teal: #2E9D58;
    --teal-dim: rgba(46,157,88,0.10);
    --teal-mid: rgba(46,157,88,0.3);
    --amber: #E27A33;
    --amber-dim: rgba(226,122,51,0.10);
    --amber-mid: rgba(226,122,51,0.3);
    --muted: #6B7280;
    --text: #111827;
    --text2: #4B5563;
    --green: #2E9D58;
    --purple: #7C3AED;
}

body, .stApp { background: var(--bg) !important; color: var(--text) !important; }

/* ── sidebar ── */
.stSidebar { background: #ffffff !important; border-right: 1px solid var(--border) !important; }
.stSidebar .stSelectbox > div > div { background: #f9fafb !important; border: 1px solid var(--border) !important; color: var(--text) !important; font-family: 'Inter', sans-serif !important; font-size: 13px !important; border-radius: 6px !important; }
.stSidebar label { color: var(--muted) !important; font-family: 'Inter', sans-serif !important; font-size: 12px !important; font-weight: 500 !important; }

/* ── header ── */
.ud-header {
    padding: 32px 40px 20px;
}
.ud-eyebrow {
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 500;
    color: var(--muted);
    margin-bottom: 6px;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
.ud-title {
    font-family: 'Inter', sans-serif;
    font-size: 28px;
    font-weight: 600;
    color: var(--text);
    line-height: 1.1;
    margin-bottom: 6px;
}
.ud-name {
    font-family: 'Roboto Mono', monospace;
    font-size: 14px;
    color: var(--teal);
}

/* ── category pill ── */
.cat-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 4px 12px;
    border-radius: 20px;
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin-top: 8px;
}
.cat-producer  { background: var(--teal-dim);  color: var(--teal);   border: 1px solid rgba(46,157,88,.25); }
.cat-consumer  { background: var(--amber-dim); color: var(--amber);  border: 1px solid rgba(226,122,51,.25); }
.cat-both      { background: rgba(124,58,237,.08); color: var(--purple); border: 1px solid rgba(124,58,237,.2); }

/* ── stats grid ── */
.ud-stats {
    display: grid;
    gap: 14px;
    margin: 0 40px 28px;
}
.ud-stats.cols-3 { grid-template-columns: repeat(3, 1fr); }
.ud-stats.cols-5 { grid-template-columns: repeat(5, 1fr); }
.ud-stats.cols-6 { grid-template-columns: repeat(6, 1fr); }

.stat-cell {
    padding: 20px 22px;
    border-radius: 12px;
}
.stat-cell:nth-child(1) { background: #E4F1F9; }
.stat-cell:nth-child(2) { background: #EAEFF6; }
.stat-cell:nth-child(3) { background: #E4F6EF; }
.stat-cell:nth-child(4) { background: #F0E6F4; }
.stat-cell:nth-child(5) { background: #FEF3E2; }
.stat-cell:nth-child(6) { background: #E8F5E9; }

.stat-label {
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    font-weight: 500;
    color: var(--text2);
    margin-bottom: 6px;
}
.stat-value {
    font-family: 'Inter', sans-serif;
    font-size: 24px;
    font-weight: 600;
    color: var(--text);
    line-height: 1;
}
.stat-unit {
    font-family: 'Inter', sans-serif;
    font-size: 13px;
    font-weight: 500;
    color: var(--text2);
    margin-left: 4px;
}

/* ── divider ── */
.ud-divider {
    height: 1px;
    background: var(--border);
    margin: 0 40px 24px;
}

/* ── section label ── */
.ud-section-label {
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    font-weight: 600;
    color: var(--muted);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    padding: 0 40px 14px;
}

/* ── session cards ── */
.session-list {
    padding: 0 40px;
    display: flex;
    flex-direction: column;
    gap: 12px;
    margin-bottom: 40px;
}

.sc {
    background: var(--surface);
    border-radius: 10px;
    padding: 16px 18px;
    border: 1px solid var(--border);
    position: relative;
    overflow: hidden;
    box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    transition: box-shadow .2s;
}
.sc::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 3px;
    border-radius: 10px 10px 0 0;
}
.sc-producer { background: rgba(46,157,88,0.05); border-color: rgba(46,157,88,0.22); }
.sc-producer::before { background: var(--teal); }
.sc-consumer { background: rgba(226,122,51,0.05); border-color: rgba(226,122,51,0.22); }
.sc-consumer::before { background: var(--amber); }

.sc-top {
    display: flex;
    align-items: flex-start;
    justify-content: space-between;
    margin-bottom: 10px;
}
.sc-badge {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    font-family: 'Inter', sans-serif;
    font-size: 11px;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    padding: 3px 8px;
    border-radius: 3px;
}
.badge-producer { color: var(--teal);  background: var(--teal-dim);  border: 1px solid rgba(46,157,88,.22); }
.badge-consumer { color: var(--amber); background: var(--amber-dim); border: 1px solid rgba(226,122,51,.22); }

.sc-kwh {
    font-family: 'Inter', sans-serif;
    font-size: 22px;
    font-weight: 600;
    line-height: 1;
}
.sc-kwh.producer { color: var(--teal); }
.sc-kwh.consumer { color: var(--amber); }
.sc-kwh-unit {
    font-size: 13px;
    font-weight: 500;
    color: var(--text2);
    margin-left: 3px;
}

.sc-money {
    font-family: 'Inter', sans-serif;
    font-size: 14px;
    font-weight: 600;
    color: var(--green);
}

.sc-meta {
    display: flex;
    flex-wrap: wrap;
    gap: 6px 20px;
    margin-top: 10px;
    padding-top: 10px;
    border-top: 1px solid var(--border);
}
.sc-meta-item {
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    color: var(--muted);
}
.sc-meta-item b {
    color: var(--text);
    font-weight: 500;
}

.sc-extras {
    display: flex;
    gap: 10px;
    margin-top: 10px;
    flex-wrap: wrap;
}
.sc-extra-chip {
    background: rgba(0,0,0,0.03);
    border: 1px solid rgba(0,0,0,0.06);
    border-radius: 6px;
    padding: 6px 12px;
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    color: var(--text2);
}
.sc-extra-chip.green {
    background: rgba(46,157,88,0.05);
    border-color: rgba(46,157,88,0.2);
    color: var(--green);
    font-weight: 500;
}

/* ── empty state ── */
.ud-empty {
    padding: 60px 40px;
    text-align: center;
    color: var(--muted);
    font-family: 'Inter', sans-serif;
    font-size: 14px;
}

/* ── footer ── */
.ud-footer {
    padding: 20px 40px;
    border-top: 1px solid var(--border);
    font-family: 'Inter', sans-serif;
    font-size: 12px;
    color: var(--muted);
    display: flex;
    justify-content: space-between;
}

/* ── MOBILE ─────────────────────────────────────────────────────────────────── */
@media (max-width: 768px) {
    .ud-header { padding: 20px 16px 14px; }
    .ud-title  { font-size: 22px; }

    .ud-stats { margin: 0 16px 20px; grid-template-columns: 1fr 1fr !important; gap: 10px; }
    .stat-cell { padding: 14px 14px; }
    .stat-value { font-size: 18px; }

    .ud-divider { margin: 0 16px 16px; }
    .ud-section-label { padding: 0 16px 12px; }

    .session-list { padding: 0 16px; gap: 10px; margin-bottom: 24px; }
    .sc { padding: 14px 14px; }
    .sc-kwh { font-size: 18px; }

    .sc-extras { flex-direction: column; gap: 6px; }

    .ud-footer { flex-direction: column; gap: 4px; padding: 16px; }
}
</style>
""", unsafe_allow_html=True)


# ── DATA LOADING ─────────────────────────────────────────────────────────────── #
@st.cache_data
def load_data():
    users   = pd.read_json("greenkwh.users.json")
    energy  = pd.read_csv("greenkwh.energy_sessions.csv")
    systems = pd.read_csv("greenkwh.systems.csv")

    users['id']   = users['id'].astype(str).str.strip()
    users['name'] = users['name'].astype(str).str.strip()

    energy['user_id']          = energy['user_id'].astype(str).str.strip()
    energy['serial_number']    = energy['serial_number'].astype(str).str.strip().str.upper()
    energy['connected_system'] = energy['connected_system'].astype(str).str.strip()
    energy['timestamp']        = pd.to_datetime(energy['timestamp'], errors='coerce', utc=True).dt.tz_convert('Asia/Kolkata')
    energy['disconnected_time']= pd.to_datetime(energy['disconnected_time'], errors='coerce', utc=True).dt.tz_convert('Asia/Kolkata')
    energy['energy_change']    = pd.to_numeric(energy['energy_change'], errors='coerce').abs()
    energy['mileage']          = pd.to_numeric(energy['mileage'], errors='coerce').fillna(0)
    energy['system_type']      = energy['system_type'].str.lower().str.strip()

    systems['user_id']       = systems['user_id'].astype(str).str.strip()
    systems['system_serial'] = systems['system_serial'].astype(str).str.strip()
    systems['system_type']   = systems['system_type'].str.lower().str.strip()

    id_to_name = dict(zip(users['id'], users['name']))
    name_to_id = dict(zip(users['name'], users['id']))
    return energy, id_to_name, name_to_id


# ── SESSION GROUPING ──────────────────────────────────────────────────────────── #
def build_sessions(df):
    if df.empty:
        return pd.DataFrame()
    sessions, session_rows = [], []
    prev_key, prev_disconnected = None, None

    for _, row in df.iterrows():
        curr_key   = (row['serial_number'], row['connected_system'], row['system_type'])
        curr_start = row['timestamp']
        new_session = False

        if prev_key is None:
            new_session = True
        elif curr_key != prev_key:
            new_session = True
        else:
            gap = (curr_start - prev_disconnected).total_seconds()
            if gap > 120:
                new_session = True

        if new_session and session_rows:
            sessions.append(_agg(session_rows))
            session_rows = []

        session_rows.append(row)
        prev_key          = curr_key
        prev_disconnected = row['disconnected_time'] if pd.notna(row['disconnected_time']) else row['timestamp']

    if session_rows:
        sessions.append(_agg(session_rows))
    return pd.DataFrame(sessions)


def _agg(rows):
    first = rows[0]; last = rows[-1]
    return {
        'system_type': first['system_type'],
        'battery':     first['serial_number'],
        'system':      first['connected_system'],
        'energy':      sum(r['energy_change'] for r in rows if pd.notna(r['energy_change'])),
        'mileage':     sum(r['mileage']        for r in rows if pd.notna(r['mileage'])),
        'start':       first['timestamp'],
        'end':         last['disconnected_time'] if pd.notna(last['disconnected_time']) else last['timestamp'],
        'sessions':    len(rows),
    }


def calc_money_saved(mileage):
    if pd.isna(mileage) or mileage == 0:
        return 0
    return max((mileage / 40) * PETROL_PER_LITRE - SWAP_COST, 0)


def fmt_dt(dt):
    return dt.strftime("%d %b %Y, %I:%M %p") if pd.notna(dt) else "—"


# ── MAIN ──────────────────────────────────────────────────────────────────────── #
energy, id_to_name, name_to_id = load_data()

# ── sidebar ── #
summary = energy.groupby(['user_id', 'system_type'])['energy_change'].sum().unstack(fill_value=0)
summary['category'] = summary.apply(
    lambda x: 'both'     if x.get('producer', 0) > 0 and x.get('consumer', 0) > 0
    else      'producer' if x.get('producer', 0) > 0
    else      'consumer', axis=1
)

with st.sidebar:
    st.markdown('<div style="padding: 20px 0 8px; font-family: Inter, sans-serif; font-size: 13px; font-weight: 600; color: #111827;">GreenKWh · User Dashboard</div>', unsafe_allow_html=True)
    category = st.selectbox("User Type", ["producer", "consumer", "both"])
    filtered_ids   = summary[summary['category'] == category].index
    filtered_names = [id_to_name[i] for i in filtered_ids if i in id_to_name]
    selected_user  = st.selectbox("Select User", sorted(filtered_names))

if not selected_user:
    st.stop()

uid = name_to_id[selected_user]
df  = energy[energy['user_id'] == uid].copy()
df  = df[df['system_type'].isin(['producer', 'consumer'])]
df  = df.dropna(subset=['timestamp'])
df  = df.sort_values('timestamp').reset_index(drop=True)

grouped = build_sessions(df)
if not grouped.empty:
    grouped['money'] = grouped['mileage'].apply(calc_money_saved)
else:
    grouped = pd.DataFrame(columns=['system_type','battery','system','energy','mileage','start','end','sessions','money'])

producer_data  = grouped[grouped['system_type'] == 'producer']
consumer_data  = grouped[grouped['system_type'] == 'consumer']

total_produced = round(producer_data['energy'].sum(), 2)
total_consumed = round(consumer_data['energy'].sum(), 2)
total_saved    = round(consumer_data['money'].sum(), 2)
total_earned   = round(total_produced * PRICE_PER_KWH, 2)
total_sessions = int(grouped['sessions'].sum()) if not grouped.empty else 0
total_mileage  = int(consumer_data['mileage'].sum()) if not consumer_data.empty else 0
total_co2      = round(total_mileage * CO2_PER_KWH, 2)

cat_label = {"producer": "⚡ Producer", "consumer": "🛵 Consumer", "both": "🔄 Both"}[category]
cat_css   = {"producer": "cat-producer", "consumer": "cat-consumer", "both": "cat-both"}[category]

# ── header ── #
st.markdown(f"""
<div class="ud-header">
  <div class="ud-eyebrow">GreenKWh · User Energy</div>
  <div class="ud-title">Energy Dashboard</div>
  <div class="ud-name">{selected_user}</div>
  <div class="cat-pill {cat_css}">{cat_label}</div>
</div>
""", unsafe_allow_html=True)

# ── stats ── #
def stat(label, value, unit=""):
    return f'<div class="stat-cell"><div class="stat-label">{label}</div><div class="stat-value">{value}<span class="stat-unit">{unit}</span></div></div>'

if category == "producer":
    cells = (
        stat("Energy Produced", f"{total_produced}", "kWh") +
        stat("Total Sessions",  f"{total_sessions}") +
        stat("Money Earned",    f"₹{total_earned}")
    )
    cols_cls = "cols-3"
elif category == "consumer":
    cells = (
        stat("Energy Consumed", f"{total_consumed}", "kWh") +
        stat("Total Sessions",  f"{total_sessions}") +
        stat("Total Mileage",   f"{total_mileage}", "km") +
        stat("CO₂ Offset",      f"{total_co2}", "kg") +
        stat("Money Saved",     f"₹{total_saved}")
    )
    cols_cls = "cols-5"
else:
    cells = (
        stat("Energy Produced", f"{total_produced}", "kWh") +
        stat("Energy Consumed", f"{total_consumed}", "kWh") +
        stat("Total Sessions",  f"{total_sessions}") +
        stat("Total Mileage",   f"{total_mileage}", "km") +
        stat("CO₂ Offset",      f"{total_co2}", "kg") +
        stat("Total Savings",   f"₹{round(total_saved + total_earned, 2)}")
    )
    cols_cls = "cols-6"

st.markdown(f'<div class="ud-stats {cols_cls}">{cells}</div>', unsafe_allow_html=True)
st.markdown('<div class="ud-divider"></div>', unsafe_allow_html=True)

# ── session cards ── #
if grouped.empty:
    st.markdown('<div class="ud-empty">No sessions found for this user.</div>', unsafe_allow_html=True)
else:
    sorted_grouped = grouped.sort_values('start', ascending=False)
    session_count  = len(sorted_grouped)
    st.markdown(f'<div class="ud-section-label">{session_count} Session{"s" if session_count != 1 else ""}</div>', unsafe_allow_html=True)

    cards_html = '<div class="session-list">'
    for _, row in sorted_grouped.iterrows():
        stype    = row['system_type']
        energy_v = round(row['energy'], 2)
        start    = fmt_dt(row['start'])
        end      = fmt_dt(row['end'])
        battery  = row['battery']
        system   = row['system']
        mileage  = int(row['mileage'])
        co2      = round(row['mileage'] * CO2_PER_KWH, 2)

        if stype == 'producer':
            earned = round(energy_v * PRICE_PER_KWH, 2)
            cards_html += f"""
<div class="sc sc-producer">
  <div class="sc-top">
    <div>
      <div class="sc-badge badge-producer">↑ Produced</div>
      <div style="margin-top:8px;">
        <span class="sc-kwh producer">{energy_v}<span class="sc-kwh-unit">kWh</span></span>
      </div>
    </div>
    <div class="sc-money">₹{earned}</div>
  </div>
  <div class="sc-meta">
    <div class="sc-meta-item">🔋 Battery <b>{battery}</b></div>
    <div class="sc-meta-item">🆔 System <b>{system}</b></div>
    <div class="sc-meta-item">📅 {start} → {end}</div>
  </div>
</div>"""
        else:
            money = round(row['money'], 2)
            co2_val = round(row['mileage'] * CO2_PER_KWH, 2) if row['mileage'] > 0 else round(energy_v * 0.85, 2)
            cards_html += f"""
<div class="sc sc-consumer">
  <div class="sc-top">
    <div>
      <div class="sc-badge badge-consumer">↓ Consumed</div>
      <div style="margin-top:8px;">
        <span class="sc-kwh consumer">{energy_v}<span class="sc-kwh-unit">kWh</span></span>
      </div>
    </div>
    <div class="sc-money">₹{money} saved</div>
  </div>
  <div class="sc-meta">
    <div class="sc-meta-item">🔋 Battery <b>{battery}</b></div>
    <div class="sc-meta-item">🆔 System <b>{system}</b></div>
    <div class="sc-meta-item">📅 {start} → {end}</div>
  </div>
  <div class="sc-extras">
    <div class="sc-extra-chip">🗺 {mileage} km</div>
    <div class="sc-extra-chip green">🌱 {co2_val} kg CO₂</div>
  </div>
</div>"""

    cards_html += '</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

# ── footer ── #
st.markdown(f"""
<div class="ud-footer">
  <span>GreenKWh Energy Platform · User Dashboard</span>
  <span>{selected_user}</span>
</div>
""", unsafe_allow_html=True)