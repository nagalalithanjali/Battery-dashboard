import streamlit as st
import pandas as pd

# ---------------- PAGE CONFIG ---------------- #
st.set_page_config(layout="wide")

# ---------------- SAFE PREMIUM UI ---------------- #
st.markdown("""
<style>

/* Card base */
.card {
    padding: 15px;
    border-radius: 12px;
    background-color: white;
    color: #111827;
    box-shadow: 0px 2px 10px rgba(0,0,0,0.05);
    margin-bottom: 12px;
}

/* Producer (Green) */
.producer {
    border-left: 6px solid #22c55e;
}
.producer .title {
    color: #16a34a;
}

/* Consumer (Orange) */
.consumer {
    border-left: 6px solid #f97316;
}
.consumer .title {
    color: #ea580c;
}

/* Metric cards */
.metric-green {
    padding: 20px;
    border-radius: 12px;
    background: linear-gradient(135deg, #dcfce7, #ffffff);
    color: #065f46;
    text-align: center;
}
.metric-orange {
    padding: 20px;
    border-radius: 12px;
    background: linear-gradient(135deg, #ffedd5, #ffffff);
    color: #9a3412;
    text-align: center;
}
.metric-neutral {
    padding: 20px;
    border-radius: 12px;
    background: linear-gradient(135deg, #e3f2fd, #ffffff);
    color: #1e3a8a;
    text-align: center;
}

/* Titles */
.title {
    font-size: 18px;
    font-weight: 600;
}

/* Sub text */
.sub {
    color: #6b7280;
    font-size: 13px;
}

</style>
""", unsafe_allow_html=True)

st.title("📊 User Energy Dashboard")

# ---------------- LOAD ---------------- #
users = pd.read_json("greenkwh.users.json")
energy = pd.read_csv("greenkwh.energy_sessions.csv")
systems = pd.read_csv("greenkwh.systems.csv")

MAX_BATTERY_KWH = 2.3
CO2_PER_KWH = 0.26

# ---------------- CLEAN ---------------- #
users['id'] = users['id'].astype(str).str.strip()
users['name'] = users['name'].astype(str).str.strip()

energy['user_id'] = energy['user_id'].astype(str).str.strip()
energy['serial_number'] = energy['serial_number'].astype(str).str.strip().str.upper()
energy['timestamp'] = pd.to_datetime(energy['timestamp'], errors='coerce', utc=True)
energy['timestamp'] = energy['timestamp'].dt.tz_convert('Asia/Kolkata')
energy['energy_change'] = pd.to_numeric(energy['energy_change'], errors='coerce')
energy['mileage'] = pd.to_numeric(energy['mileage'], errors='coerce')
energy['system_type'] = energy['system_type'].str.lower().str.strip()

systems['user_id'] = systems['user_id'].astype(str).str.strip()
systems['system_serial'] = systems['system_serial'].astype(str).str.strip()

if 'system_type' in systems.columns:
    systems['system_type'] = systems['system_type'].astype(str).str.lower().str.strip()

# ---------------- MAP ---------------- #
id_to_name = dict(zip(users['id'], users['name']))
name_to_id = dict(zip(users['name'], users['id']))

# ---------------- USER CATEGORY ---------------- #
summary = energy.groupby(['user_id', 'system_type'])['energy_change'].sum().unstack(fill_value=0)

summary['category'] = summary.apply(
    lambda x: 'both' if x.get('producer',0) > 0 and x.get('consumer',0) > 0
    else 'producer' if x.get('producer',0) > 0
    else 'consumer',
    axis=1
)

# ---------------- LAYOUT ---------------- #
left, right = st.columns([1,3])

# ================= LEFT ================= #
with left:
    st.markdown("### 🔍 Filters")

    category = st.selectbox("Select Type", ["producer", "consumer", "both"])

    filtered_ids = summary[summary['category'] == category].index

    filtered_names = [
        id_to_name[uid]
        for uid in filtered_ids
        if uid in id_to_name
    ]

    if not filtered_names:
        st.warning("No users available")
        st.stop()

    selected_user = st.selectbox("Select User", filtered_names)

# ================= RIGHT ================= #
with right:

    if selected_user not in name_to_id:
        st.warning("User mapping error")
        st.stop()

    uid = name_to_id[selected_user]

    df = energy[energy['user_id'] == uid].copy()

    if df.empty:
        st.warning("No data available")
        st.stop()

    # ---------------- FILTER ---------------- #
    df = df[df['system_type'].isin(['producer','consumer'])]

    # ---------------- CLEAN ---------------- #
    df['energy_change'] = df['energy_change'].abs()
    df = df[df['energy_change'] > 0.05]
    df = df[df['energy_change'] <= MAX_BATTERY_KWH]

    # ---------------- SYSTEM MAPPING ---------------- #
    sys_map = systems[systems['user_id'] == uid].copy()

    system_dict = {}

    if not sys_map.empty and 'system_type' in sys_map.columns:
        for _, row in sys_map.iterrows():
            stype = row.get('system_type')
            serial = row.get('system_serial')

            if stype in ['producer', 'consumer']:
                system_dict[stype] = serial

    df['system_serial'] = df['system_type'].map(system_dict)
    df['system_serial'] = df['system_serial'].fillna("NA")

    # ---------------- REMOVE DUPLICATES ---------------- #
    df = df.drop_duplicates(
        subset=['serial_number', 'timestamp', 'energy_change'],
        keep='last'
    )

    # ================= METRICS ================= #
    total_produced = df[df['system_type'] == 'producer']['energy_change'].sum()
    total_consumed = df[df['system_type'] == 'consumer']['energy_change'].sum()
    total_mileage = df[df['system_type'] == 'consumer']['mileage'].sum()
    total_co2 = total_consumed * CO2_PER_KWH

    st.markdown("### 🚀 Energy Impact Summary")

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.markdown(f"""
        <div class="metric-green">
            <div class="title">🔋 Produced</div>
            <div>{round(total_produced,2)} GreenkWh</div>
        </div>
        """, unsafe_allow_html=True)

    with c2:
        st.markdown(f"""
        <div class="metric-orange">
            <div class="title">⚡ Consumed</div>
            <div>{round(total_consumed,2)} GreenkWh</div>
        </div>
        """, unsafe_allow_html=True)

    with c3:
        st.markdown(f"""
        <div class="metric-neutral">
            <div class="title">🚗 Mileage</div>
            <div>{int(total_mileage)} km</div>
        </div>
        """, unsafe_allow_html=True)

    with c4:
        st.markdown(f"""
        <div class="metric-neutral">
            <div class="title">🌱 CO₂ Offset</div>
            <div>{round(total_co2,2)} kg</div>
        </div>
        """, unsafe_allow_html=True)

    # ---------------- SORT ---------------- #
    df = df.sort_values('timestamp', ascending=False)

    # ================= SESSION CARDS ================= #
    for _, row in df.iterrows():

        energy_val = round(row['energy_change'], 2)
        time_text = row['timestamp'].strftime("%d %b %Y, %I:%M %p IST")

        is_consumer = row['system_type'] == 'consumer'

        if is_consumer:
            title = f"⚡ Consumed {energy_val} GreenkWh"
            box_class = "card consumer"
        else:
            title = f"🔋 Produced {energy_val} GreenkWh"
            box_class = "card producer"

        mileage_text = ""
        co2_text = ""

        if is_consumer:
            mileage_text = (
                "🚗 Mileage: NA"
                if pd.isna(row['mileage']) or row['mileage'] == 0
                else f"🚗 Mileage: {int(row['mileage'])} km"
            )

            co2_val = row['energy_change'] * CO2_PER_KWH
            co2_text = f"🌱 CO₂ Offset: {round(co2_val,2)} kg"

        st.markdown(f"""
        <div class="{box_class}">
            <div class="title">{title}</div>
            <div class="sub">🆔 System: {row['system_serial']}</div>
            <div class="sub">🔋 Battery: {row['serial_number']}</div>
            <div class="sub">📅 {time_text}</div>
            <div class="sub">{mileage_text}</div>
            <div class="sub">{co2_text}</div>
        </div>
        """, unsafe_allow_html=True)