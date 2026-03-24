import streamlit as st
import pandas as pd

# ---------------- LOAD ---------------- #
users = pd.read_json("greenkwh.users.json")
energy = pd.read_csv("greenkwh.energy_sessions.csv")
systems = pd.read_csv("greenkwh.systems.csv")
swaps = pd.read_csv("greenkwh.swaps.csv")

# ---------------- CLEAN ---------------- #
users['id'] = users['id'].astype(str).str.strip()
energy['user_id'] = energy['user_id'].astype(str).str.strip()
systems['user_id'] = systems['user_id'].astype(str).str.strip()
swaps['userid'] = swaps['userid'].astype(str).str.strip()

users['name'] = users['name'].astype(str).str.strip()

energy['serial_number'] = energy['serial_number'].astype(str).str.strip().str.upper()
swaps['serialnumber'] = swaps['serialnumber'].astype(str).str.strip().str.upper()
systems['system_serial'] = systems['system_serial'].astype(str).str.strip().str.upper()

swaps['created_at'] = pd.to_datetime(swaps['created_at'], errors='coerce', utc=True)
swaps['created_at'] = swaps['created_at'].dt.tz_convert('Asia/Kolkata')

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

        # ✅ FILTER USER
        df = energy[energy['user_id'] == uid].copy()

        if df.empty:
            st.warning("No data available")
            st.stop()

        # ---------------- SYSTEM ---------------- #
        sys_map = systems[systems['user_id'] == uid]

        if not sys_map.empty:
            df['system_serial'] = sys_map['system_serial'].iloc[0]
        else:
            df['system_serial'] = "NA"

        # ---------------- TIME FIX ---------------- #
        # 👉 take latest swap per battery
        swap_map = (
            swaps[swaps['userid'] == uid]
            .sort_values('created_at')
            .drop_duplicates('serialnumber', keep='last')
        )

        time_dict = dict(zip(swap_map['serialnumber'], swap_map['created_at']))

        # map time safely (NO DUPLICATES)
        df['created_at'] = df['serial_number'].map(time_dict)

        # drop rows without time
        df = df[df['created_at'].notna()]

        # ---------------- CLEAN ---------------- #
        df = df[df['energy_change'].notna()]
        df = df[df['energy_change'] > 0]

        df['system_type'] = df['system_type'].str.lower().str.strip()
        df = df[df['system_type'].isin(['producer','consumer'])]

        # ================= GROUPING ================= #
        grouped = df.groupby(
            ['system_serial','system_type','serial_number','created_at'],
            as_index=False
        ).agg(
            total_energy=('energy_change','sum')
        )

        grouped = grouped.sort_values('created_at', ascending=False)

        # ================= DISPLAY ================= #
        for _, row in grouped.iterrows():

            energy_val = round(row['total_energy'],2)

            if row['system_type'] == 'producer':
                title = f"🔋 Produced {energy_val} GreenkWh"
            else:
                title = f"⚡ Consumed {energy_val} GreenkWh"

            time_text = row['created_at'].strftime("%d %b %Y, %I:%M %p IST")

            st.markdown("---")
            st.markdown(f"""
            **{title}**  
            🆔 System: {row['system_serial']}  
            🔋 Battery: {row['serial_number']}  
            📅 {time_text}
            """)