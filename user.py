import streamlit as st
import pandas as pd

# ---------------- CONSTANTS ---------------- #
MAX_BATTERY_KWH = 2.3
CO2_PER_KWH = 0.06
PRICE_PER_KWH = 16
PETROL_PER_LITRE = 107.5
SWAP_COST = 80

# ---------------- PAGE ---------------- #
st.set_page_config(layout="wide")

st.markdown("""
<style>

/* ---------------- GLOBAL ---------------- */
html, body, .stApp {
    background-color: #0b1220;
    color: #ffffff;
}

/* ---------------- SIDEBAR ---------------- */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0f172a, #0b1220);
}

/* ❌ REMOVE global override (THIS WAS BREAKING UI) */

/* Labels */
section[data-testid="stSidebar"] label {
    color: #9ca3af !important;
}

/* ---------------- SELECTBOX FIX ---------------- */

/* Outer box */
section[data-testid="stSidebar"] div[data-baseweb="select"] {
    background-color: #111827 !important;
    border: 1px solid #374151 !important;
    border-radius: 10px;
}

/* Selected value container */
section[data-testid="stSidebar"] div[role="button"] {
    background-color: #1f2937 !important;
    border: 1px solid #374151 !important;
}

/* ✅ TEXT FIX (MAIN FIX) */
section[data-testid="stSidebar"] div[role="button"] span {
    color: #0b1220 !important;   /* DARK TEXT */
    font-weight: 600;
}

/* Dropdown list */
ul[role="listbox"] {
    background-color: #111827 !important;
}

/* Options */
ul[role="listbox"] li {
    background-color: #111827 !important;
    color: #ffffff !important;
}

ul[role="listbox"] li:hover {
    background-color: #1f2937 !important;
}

/* ---------------- METRICS ---------------- */
[data-testid="stMetric"] {
    background: #111827;
    padding: 16px;
    border-radius: 14px;
    border: 1px solid #1f2937;
}

[data-testid="stMetricLabel"] {
    color: #9ca3af !important;
}

[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-weight: 700;
}

/* ---------------- CARDS ---------------- */
.card {
    padding: 20px;
    border-radius: 14px;
    margin-bottom: 16px;
    background: #111827;
    border: 1px solid #1f2937;
    box-shadow: 0 6px 18px rgba(0,0,0,0.4);
}

/* Borders */
.producer {
    border-left: 6px solid #22c55e;
}

.consumer {
    border-left: 6px solid #f97316;
}

/* Text */
.title {
    font-size: 16px;
    font-weight: 600;
}

.sub {
    font-size: 13px;
    color: #9ca3af;
}

/* Center */
.center-area {
    max-width: 1100px;
    margin: auto;
}

/* Header */
h1 {
    font-size: 40px !important;
}

</style>
""", unsafe_allow_html=True)

st.title("📊 User Energy Dashboard")

# ---------------- LOAD ---------------- #
users = pd.read_json("greenkwh.users.json")
energy = pd.read_csv("greenkwh.energy_sessions.csv")
systems = pd.read_csv("greenkwh.systems.csv")

# ---------------- CLEAN ---------------- #
users['id'] = users['id'].astype(str).str.strip()
users['name'] = users['name'].astype(str).str.strip()

energy['user_id'] = energy['user_id'].astype(str).str.strip()
energy['serial_number'] = energy['serial_number'].astype(str).str.strip().str.upper()

energy['timestamp'] = pd.to_datetime(
    energy['timestamp'], errors='coerce', utc=True
).dt.tz_convert('Asia/Kolkata')

energy['energy_change'] = pd.to_numeric(
    energy['energy_change'], errors='coerce'
).abs()

energy['mileage'] = pd.to_numeric(energy['mileage'], errors='coerce')
energy['system_type'] = energy['system_type'].str.lower().str.strip()

systems['user_id'] = systems['user_id'].astype(str).str.strip()
systems['system_serial'] = systems['system_serial'].astype(str).str.strip()
systems['system_type'] = systems['system_type'].str.lower().str.strip()

# ---------------- MAP ---------------- #
id_to_name = dict(zip(users['id'], users['name']))
name_to_id = dict(zip(users['name'], users['id']))

# ---------------- SIDEBAR ---------------- #
summary = energy.groupby(['user_id', 'system_type'])['energy_change'].sum().unstack(fill_value=0)

summary['category'] = summary.apply(
    lambda x: 'both' if x.get('producer', 0) > 0 and x.get('consumer', 0) > 0
    else 'producer' if x.get('producer', 0) > 0
    else 'consumer',
    axis=1
)

category = st.sidebar.selectbox("Select Type", ["producer", "consumer", "both"])

filtered_ids = summary[summary['category'] == category].index
filtered_names = [id_to_name[i] for i in filtered_ids if i in id_to_name]

selected_user = st.sidebar.selectbox("Select User", filtered_names)

# ---------------- DATA ---------------- #
uid = name_to_id[selected_user]
df = energy[energy['user_id'] == uid].copy()

df = df[df['system_type'].isin(['producer', 'consumer'])]
df = df.dropna(subset=['timestamp'])

# ---------------- SYSTEM MAP ---------------- #
sys_map = systems[systems['user_id'] == uid]
system_dict = dict(zip(sys_map['system_type'], sys_map['system_serial']))
df['system_serial'] = df['system_type'].map(system_dict).fillna("NA")

# ---------------- MONEY ---------------- #
def calc_money_saved(mileage):
    if pd.isna(mileage) or mileage == 0:
        return None
    petrol_cost = (mileage / 40) * PETROL_PER_LITRE
    return max(petrol_cost - SWAP_COST, 0)

df['money_saved'] = df['mileage'].apply(calc_money_saved)

# ---------------- GROUP ---------------- #
grouped = df.groupby(
    ['system_type', 'system_serial', 'serial_number']
).agg({
    'energy_change': 'sum',
    'mileage': 'sum',
    'money_saved': 'sum',
    'timestamp': ['min', 'max', 'count']
}).reset_index()

grouped.columns = [
    'system_type', 'system', 'battery',
    'energy', 'mileage', 'money',
    'start', 'end', 'sessions'
]

producer_data = grouped[grouped['system_type'] == 'producer']
consumer_data = grouped[grouped['system_type'] == 'consumer']

total_produced = producer_data['energy'].sum()
total_consumed = consumer_data['energy'].sum()
total_saved = consumer_data['money'].sum()
total_earned = total_produced * PRICE_PER_KWH
total_sessions = grouped['sessions'].sum()
total_mileage = consumer_data['mileage'].sum()
total_co2 = total_consumed * CO2_PER_KWH

# ---------------- CENTER ---------------- #
st.markdown('<div class="center-area">', unsafe_allow_html=True)

st.markdown("### 🚀 Energy Impact Summary")

# ---------------- METRICS ---------------- #
c1, c2, c3, c4, c5, c6 = st.columns(6)
c1.metric("🔋 Produced", round(total_produced, 2))
c2.metric("⚡ Consumed", round(total_consumed, 2))
c3.metric("🔢 Total Sessions", int(total_sessions))
c4.metric("🚗 Mileage", f"{int(total_mileage)} km")
c5.metric("🌱 CO₂ Offset", f"{round(total_co2, 2)} kg")
c6.metric("💰 Savings", f"₹{round(total_saved + total_earned, 2)}")

# ---------------- CARDS ---------------- #
grouped = grouped.sort_values('start', ascending=False)

for _, row in grouped.iterrows():

    start = row['start'].strftime("%d %b %Y, %I:%M %p")
    end = row['end'].strftime("%d %b %Y, %I:%M %p")

    if row['system_type'] == 'producer':
        st.markdown(f"""
        <div class="card producer">
            <div class="title">🔋 Produced: {round(row['energy'], 2)} GreenkWh</div>
            <div class="sub">🆔 System: {row['system']}</div>
            <div class="sub">🔋 Battery: {row['battery']}</div>
            <div class="sub">📅 {start} → {end}</div>
            <div class="title">💰 Money Earned: ₹{round(row['energy'] * PRICE_PER_KWH, 2)}</div>
        </div>
        """, unsafe_allow_html=True)

    else:
        co2 = row['energy'] * CO2_PER_KWH
        st.markdown(f"""
        <div class="card consumer">
            <div class="title">⚡ Consumed: {round(row['energy'], 2)} GreenkWh</div>
            <div class="sub">🆔 System: {row['system']}</div>
            <div class="sub">🔋 Battery: {row['battery']}</div>
            <div class="sub">📅 {start} → {end}</div>
            <div class="sub">🚗 Mileage: {int(row['mileage'])} km</div>
            <div class="sub">🌱 CO₂ Offset: {round(co2, 2)} kg</div>
            <div class="title">💰 Money Saved: ₹{round(row['money'], 2)}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)