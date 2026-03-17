import streamlit as st
import pandas as pd

# ---------------- LOAD DATA ---------------- #
swap = pd.read_csv("greenkwh.swaps.csv")
energy = pd.read_csv("greenkwh.energy_sessions.csv")
battery = pd.read_csv("greenkwh.batteries.csv")
system = pd.read_csv("greenkwh.systems.csv")

# ---------------- CLEAN ---------------- #
swap['serialnumber'] = swap['serialnumber'].astype(str).str.strip().str.upper()
energy['serial_number'] = energy['serial_number'].astype(str).str.strip().str.upper()
battery['serialnumber'] = battery['serialnumber'].astype(str).str.strip().str.upper()

# ✅ FIXED COLUMN NAME HERE
battery['connectedsystem'] = battery['connectedsystem'].astype(str).str.strip().str.upper()
system['system_serial'] = system['system_serial'].astype(str).str.strip().str.upper()

# Convert time
swap['created_at'] = pd.to_datetime(swap['created_at'], errors='coerce')

# ---------------- UI ---------------- #
st.title("🔋 Battery Travel Dashboard")

battery_id = st.text_input("Enter Battery Serial Number")

if battery_id:

    battery_id = battery_id.strip().upper()

    # Filter battery
    bat = battery[battery['serialnumber'] == battery_id]

    if bat.empty:
        st.error("Battery not found ❌")
    else:
           # ✅ FIXED MERGE COLUMN HERE
        bat = pd.merge(
            bat,
            system,
            left_on='connectedsystem',
            right_on='system_serial',
            how='left'
        )

        # Filter swap + energy
        swap_f = swap[swap['serialnumber'] == battery_id]
        energy_f = energy[energy['serial_number'] == battery_id]

        # Merge swap + energy
        df = pd.merge(
            swap_f,
            energy_f,
            left_on='serialnumber',
            right_on='serial_number',
            how='left'
        )

        # Add system type
        df['system_type'] = bat['system_type'].values[0]

        # SOC format
        df['soc_change'] = df['start_soc'].astype(str) + " → " + df['end_soc'].astype(str)

        # Format time
        df['time'] = df['created_at'].dt.strftime("%d %b %Y, %I:%M %p")

        # ✅ Proper sorting (professional fix)
        df = df.sort_values(by='created_at')

        # Final table
        final_df = df[['system_type', 'soc_change', 'time']]

        st.dataframe(final_df)