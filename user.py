import streamlit as st
import pandas as pd

# ---------------- LOAD ---------------- #
users = pd.read_json("greenkwh.users.json")
energy = pd.read_csv("greenkwh.energy_sessions.csv")
systems = pd.read_csv("greenkwh.systems.csv")
swaps = pd.read_csv("greenkwh.swaps.csv")

# ---------------- CLEAN ---------------- #

# IDs
users['id'] = users['id'].astype(str).str.strip()
energy['user_id'] = energy['user_id'].astype(str).str.strip()
systems['user_id'] = systems['user_id'].astype(str).str.strip()
swaps['userid'] = swaps['userid'].astype(str).str.strip()

# Names
users['name'] = users['name'].astype(str).str.strip()

# Battery
energy['serial_number'] = energy['serial_number'].astype(str).str.strip().str.upper()
swaps['serialnumber'] = swaps['serialnumber'].astype(str).str.strip().str.upper()

# System
systems['system_serial'] = systems['system_serial'].astype(str).str.strip().str.upper()

# Time
swaps['created_at'] = pd.to_datetime(swaps['created_at'], errors='coerce')

# Map user
user_map = dict(zip(users['name'], users['id']))

# ---------------- UI ---------------- #
st.set_page_config(layout="wide")
st.title("📊 User Dashboard")

col1, col2 = st.columns([1, 3])

# LEFT PANEL
with col1:
    user_list = users['name'].dropna().unique()
    selected_user = st.selectbox("Select User", user_list)

# RIGHT PANEL
with col2:

    st.subheader("User Activity Timeline")

    if selected_user:

        uid = user_map[selected_user]

        # ---------------- FILTER ENERGY ---------------- #
        df = energy[energy['user_id'] == uid].copy()

        if df.empty:
            st.warning("No data available for this user")
            st.stop()

        # ---------------- ADD SYSTEM ---------------- #
        df = pd.merge(
            df,
            systems[['user_id', 'system_serial']],
            on='user_id',
            how='left'
        )

        # ---------------- ADD TIME ---------------- #
        time_map = swaps[['serialnumber', 'created_at']].dropna()
        time_map = time_map.sort_values('created_at')
        time_map = time_map.drop_duplicates('serialnumber', keep='last')

        df = pd.merge(
            df,
            time_map,
            left_on='serial_number',
            right_on='serialnumber',
            how='left'
        )

        df['created_at'] = df['created_at'].fillna(pd.Timestamp.now())

        # ---------------- CLEAN ---------------- #
        df = df[df['energy_change'].notna()]
        df = df[df['energy_change'] > 0]

        df['system_type'] = df['system_type'].astype(str).str.lower().str.strip()
        df = df[df['system_type'].isin(['producer', 'consumer'])]

        df = df.sort_values('created_at')

        # ================= SUMMARY ================= #

        total_produced = df[df['system_type'] == 'producer']['energy_change'].sum()
        total_consumed = df[df['system_type'] == 'consumer']['energy_change'].sum()

        # Mileage ONLY for consumer
        if 'milage' in df.columns:
            total_mileage = df[df['system_type'] == 'consumer']['milage'].sum()
        elif 'mileage' in df.columns:
            total_mileage = df[df['system_type'] == 'consumer']['mileage'].sum()
        else:
            total_mileage = 0

        mileage_text = "NA" if total_mileage == 0 else f"{round(total_mileage,2)} km"

        c1, c2, c3 = st.columns(3)

        c1.metric("🔋 Total Produced", f"{round(total_produced,2)} GreenkWh")
        c2.metric("⚡ Total Consumed", f"{round(total_consumed,2)} GreenkWh")
        c3.metric("🚗 Total Mileage (Consumer)", mileage_text)

        # ---------------- GROUPING ---------------- #
        groups = []
        current = []

        for _, row in df.iterrows():

            if not current:
                current.append(row)
                continue

            last = current[-1]

            if (
                row['system_type'] == last['system_type'] and
                row['serial_number'] == last['serial_number'] and
                (row['created_at'] - last['created_at']).total_seconds() < 86400
            ):
                current.append(row)
            else:
                groups.append(pd.DataFrame(current))
                current = [row]

        if current:
            groups.append(pd.DataFrame(current))

        groups = groups[::-1]

        # ---------------- DISPLAY ---------------- #
        for g in groups:

            system_type = g['system_type'].iloc[0]
            total_energy = round(g['energy_change'].sum(), 2)

            system_id = g['system_serial'].iloc[0] if 'system_serial' in g else "NA"
            battery = g['serial_number'].iloc[0]

            start = g['created_at'].min().strftime("%d %b %Y, %I:%M %p")
            end = g['created_at'].max().strftime("%d %b %Y, %I:%M %p")

            if start == end:
                time_text = f"📅 {start}"
            else:
                time_text = f"📅 {start} to {end}"

            if system_type == 'producer':
                title = f"🔋 Produced {total_energy} GreenkWh"
            else:
                title = f"⚡ Consumed {total_energy} GreenkWh"

            st.markdown("---")
            st.markdown(f"""
            **{title}**  
            🆔 System: {system_id}  
            🔋 Battery: {battery}  
            {time_text}
            """)