import streamlit as st
import pandas as pd

# ---------------- LOAD ---------------- #
users = pd.read_json("greenkwh.users.json")
energy = pd.read_csv("greenkwh.energy_sessions.csv")
systems = pd.read_csv("greenkwh.systems.csv")

MAX_BATTERY_KWH = 2.3
CO2_PER_KWH = 0.26  # ✅ correct for EV vs petrol

# ---------------- CLEAN ---------------- #
users['id'] = users['id'].astype(str).str.strip()
energy['user_id'] = energy['user_id'].astype(str).str.strip()
systems['user_id'] = systems['user_id'].astype(str).str.strip()

users['name'] = users['name'].astype(str).str.strip()

energy['serial_number'] = energy['serial_number'].astype(str).str.strip().str.upper()
systems['system_serial'] = systems['system_serial'].astype(str).str.strip()

# ✅ TIMESTAMP
energy['timestamp'] = pd.to_datetime(energy['timestamp'], errors='coerce', utc=True)
energy['timestamp'] = energy['timestamp'].dt.tz_convert('Asia/Kolkata')

# numeric safety
energy['energy_change'] = pd.to_numeric(energy['energy_change'], errors='coerce')
energy['mileage'] = pd.to_numeric(energy['mileage'], errors='coerce')

# ---------------- MAP ---------------- #
user_map = dict(zip(users['name'], users['id']))

# ---------------- UI ---------------- #
st.set_page_config(layout="wide")
st.title("📊 User Dashboard")

col1, col2 = st.columns([1,3])

with col1:
    selected_user = st.selectbox("Select User", users['name'].dropna().unique())

with col2:

    if selected_user:

        uid = user_map[selected_user]

        # ---------------- FILTER ---------------- #
        df = energy[energy['user_id'] == uid].copy()

        if df.empty:
            st.warning("No data available")
            st.stop()

        # ---------------- VALID TYPES ---------------- #
        df['system_type'] = df['system_type'].str.lower().str.strip()
        df = df[df['system_type'].isin(['producer','consumer'])]

        # ---------------- CLEAN ---------------- #
        df['energy_change'] = df['energy_change'].abs()
        df = df[df['energy_change'] > 0.05]
        df = df[df['energy_change'] <= MAX_BATTERY_KWH]

        # ---------------- SYSTEM ---------------- #
        sys_map = systems[systems['user_id'] == uid]
        system_id = sys_map['system_serial'].iloc[0] if not sys_map.empty else "NA"
        df['system_serial'] = system_id

        # ---------------- REMOVE DUPLICATES ---------------- #
        df = df.drop_duplicates(
            subset=['serial_number', 'timestamp', 'energy_change'],
            keep='last'
        )

        # ================= 🔥 IMPACT ================= #
        total_produced = df[df['system_type'] == 'producer']['energy_change'].sum()
        total_consumed = df[df['system_type'] == 'consumer']['energy_change'].sum()
        total_mileage = df[df['system_type'] == 'consumer']['mileage'].sum()

        total_co2 = total_consumed * CO2_PER_KWH  # ✅ NEW

        st.markdown("### 🚀 Energy Impact Summary")
        st.markdown("---")

        c1, c2, c3, c4 = st.columns(4)

        c1.metric("🔋 Energy Produced", f"{round(total_produced,2)} GreenkWh")
        c2.metric("⚡ Energy Consumed", f"{round(total_consumed,2)} GreenkWh")
        c3.metric("🚗 Mileage", f"{int(total_mileage)} km")
        c4.metric("🌱 CO₂ Offset", f"{round(total_co2,2)} kg")  # ✅ UPDATED

        # ---------------- SORT ---------------- #
        df = df.sort_values('timestamp', ascending=False)

        # ---------------- DISPLAY ---------------- #
        for _, row in df.iterrows():

            energy_val = round(row['energy_change'], 2)
            time_text = row['timestamp'].strftime("%d %b %Y, %I:%M %p IST")

            if row['system_type'] == 'producer':
                title = f"🔋 Produced {energy_val} GreenkWh"
            else:
                title = f"⚡ Consumed {energy_val} GreenkWh"

            # -------- MILEAGE -------- #
            mileage_text = ""
            if row['system_type'] == 'consumer':
                if pd.isna(row['mileage']) or row['mileage'] == 0:
                    mileage_text = "🚗 Mileage: NA"
                else:
                    mileage_text = f"🚗 Mileage: {int(row['mileage'])} km"

            # -------- CO2 PER ENTRY -------- #
            co2_text = ""
            if row['system_type'] == 'consumer':
                co2_val = row['energy_change'] * CO2_PER_KWH
                co2_text = f"🌱 CO₂ Offset: {round(co2_val,2)} kg"

            st.markdown("---")

            if row['system_type'] == 'consumer':
                st.markdown(f"""
                **{title}**  
                🆔 System: {row['system_serial']}  
                🔋 Battery: {row['serial_number']}  
                📅 {time_text}  
                {mileage_text}  
                {co2_text}
                """)
            else:
                st.markdown(f"""
                **{title}**  
                🆔 System: {row['system_serial']}  
                🔋 Battery: {row['serial_number']}  
                📅 {time_text}
                """)