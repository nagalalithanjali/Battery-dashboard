import streamlit as st
import pandas as pd

# ---------------- CONSTANTS ---------------- #
MAX_BATTERY_KWH = 2.3
CO2_PER_KWH = 0.6
PRICE_PER_KWH = 16
PETROL_PER_LITRE = 107.50
SWAP_COST = 80

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
).abs()   # ✅ remove negative sign only

energy['mileage'] = pd.to_numeric(energy['mileage'], errors='coerce')
energy['system_type'] = energy['system_type'].str.lower().str.strip()

systems['user_id'] = systems['user_id'].astype(str).str.strip()
systems['system_serial'] = systems['system_serial'].astype(str).str.strip()

# ---------------- MAP ---------------- #
id_to_name = dict(zip(users['id'], users['name']))
name_to_id = dict(zip(users['name'], users['id']))

# ---------------- UI ---------------- #
st.set_page_config(layout="wide")
st.title("📊 User Dashboard")

left, right = st.columns([1, 3])

# ================= LEFT ================= #
with left:

    summary = energy.groupby(['user_id', 'system_type'])['energy_change'].sum().unstack(fill_value=0)

    summary['category'] = summary.apply(
        lambda x: 'both' if x.get('producer', 0) > 0 and x.get('consumer', 0) > 0
        else 'producer' if x.get('producer', 0) > 0
        else 'consumer',
        axis=1
    )

    category = st.selectbox("Select Type", ["producer", "consumer", "both"])

    filtered_ids = summary[summary['category'] == category].index
    filtered_names = [id_to_name[i] for i in filtered_ids if i in id_to_name]

    selected_user = st.selectbox("Select User", filtered_names)

# ================= RIGHT ================= #
with right:

    uid = name_to_id[selected_user]
    df = energy[energy['user_id'] == uid].copy()

    df = df[df['system_type'].isin(['producer', 'consumer'])]
    df = df.dropna(subset=['timestamp'])

    # ---------------- SYSTEM MAP ---------------- #
    sys_map = systems[systems['user_id'] == uid]
    system_dict = dict(zip(sys_map['system_type'], sys_map['system_serial']))
    df['system_serial'] = df['system_type'].map(system_dict).fillna("NA")

    # ---------------- MONEY SAVED ---------------- #
    def calc_money_saved(mileage):
        if pd.isna(mileage) or mileage == 0:
            return None
        petrol = (mileage / 40) * PETROL_PER_LITRE
        return max(petrol - SWAP_COST, 0)

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

    # ---------------- SPLIT ---------------- #
    producer_data = grouped[grouped['system_type'] == 'producer']
    consumer_data = grouped[grouped['system_type'] == 'consumer']

    total_produced = producer_data['energy'].sum()
    total_consumed = consumer_data['energy'].sum()

    total_earned = total_produced * PRICE_PER_KWH
    total_saved = consumer_data['money'].sum()

    producer_sessions = producer_data['sessions'].sum()
    consumer_sessions = consumer_data['sessions'].sum()

    total_sessions = grouped['sessions'].sum()

    total_mileage = consumer_data['mileage'].sum()
    total_co2 = total_consumed * CO2_PER_KWH

    # ---------------- TOP CARDS ---------------- #
    st.markdown("### 🚀 Summary")

    if category == "producer":
        c1, c2, c3 = st.columns(3)
        c1.metric("🔋 Energy Produced", f"{round(total_produced, 2)} GreenkWh")
        c2.metric("🔢 Total Sessions", int(producer_sessions))
        c3.metric("💰 Money Earned", f"₹{round(total_earned, 2)}")

    elif category == "consumer":
        c1, c2, c3, c4, c5 = st.columns(5)
        c1.metric("⚡ Energy Consumed", f"{round(total_consumed, 2)} GreenkWh")
        c2.metric("🔢 Total Sessions", int(consumer_sessions))
        c3.metric("🚗 Total Mileage", f"{int(total_mileage)} km")
        c4.metric("🌱 CO₂ Offset", f"{round(total_co2, 2)} kg")
        c5.metric("💰 Money Saved", f"₹{round(total_saved, 2)}")

    else:
        c1, c2, c3, c4, c5, c6 = st.columns(6)
        c1.metric("🔋 Energy Produced", f"{round(total_produced, 2)}")
        c2.metric("⚡ Energy Consumed", f"{round(total_consumed, 2)}")
        c3.metric("🔢 Total Sessions", int(total_sessions))
        c4.metric("🚗 Total Mileage", f"{int(total_mileage)} km")
        c5.metric("🌱 CO₂ Offset", f"{round(total_co2, 2)} kg")
        c6.metric("💰 Net Savings", f"₹{round(total_saved - total_earned, 2)}")

    st.markdown("---")

    # ---------------- DISPLAY ---------------- #
    grouped = grouped.sort_values('start', ascending=False)

    for _, row in grouped.iterrows():

        start = row['start'].strftime("%d %b %Y, %I:%M %p")
        end = row['end'].strftime("%d %b %Y, %I:%M %p")

        st.markdown("---")

        if row['system_type'] == 'producer':

            st.markdown(f"""
            **🔋 Produced {round(row['energy'], 2)} GreenkWh**  
            🆔 System: {row['system']}  
            🔋 Battery: {row['battery']}  
            📅 {start} → {end}  
            🔢 Sessions: {int(row['sessions'])}  
            💰 Money Earned: ₹{round(row['energy'] * PRICE_PER_KWH, 2)}
            """)

        else:

            mileage_text = "NA" if row['mileage'] == 0 else f"{int(row['mileage'])} km"
            saved_text = "NA" if pd.isna(row['money']) else f"₹{round(row['money'], 2)}"
            co2 = row['energy'] * CO2_PER_KWH

            st.markdown(f"""
            **⚡ Consumed {round(row['energy'], 2)} GreenkWh**  
            🆔 System: {row['system']}  
            🔋 Battery: {row['battery']}  
            📅 {start} → {end}  
            🔢 Sessions: {int(row['sessions'])}  
            🚗 Mileage: {mileage_text}  
            🌱 CO₂ Offset: {round(co2, 2)} kg  
            💰 Money Saved: {saved_text}
            """)