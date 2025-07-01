import streamlit as st
from datetime import datetime

# App configuration
st.set_page_config(
    page_title="Cosmic Radiation Research Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("Cosmic Radiation Research Dashboard")

# Intro section on homepage
st.markdown("""
Welcome to the **Cosmic Radiation Research Dashboard** — an interactive platform to explore real-time and simulated data on cosmic rays, their biological and technological effects, and mission safety.

---

**Select a feature tab below to begin your research:**
""")

# Main Feature Tabs
tabs = st.tabs([
    "Radiation Risk Calculator",
    "Live Cosmic Ray Shower Map",
    "Biological Effects Visualizer",
    "Effects on Electronics",
    "Cosmic Ray Data Explorer",
    "Mission Dose Comparator",
    "Space Weather Live",
    "Research Library",
    "Upload & Analyze Your Data"
])

# Tab 1: Radiation Risk Calculator
with tabs[0]:
    st.subheader("Radiation Risk Calculator")
    st.info("This tool estimates the radiation dose and cancer risk for a space mission based on real-time solar particle flux and selected shielding.")
    # Inputs
    mission_days = st.slider("🕒 Mission Duration (days)", 1, 1000, 180)
    shielding_material = st.selectbox("🛡️ Shielding Material", ["None", "Aluminum", "Polyethylene"])

    # Real-time proton flux from NOAA
    url = "https://services.swpc.noaa.gov/json/goes/primary/differential-proton-flux-1-day.json"

    try:
        data = requests.get(url).json()
        flux = float(data[-1]['flux'])  # protons/cm²/s/sr
        st.success(f"☀️ Live Proton Flux (≥10 MeV): {flux:.2e} protons/cm²/s/sr")
    except:
        flux = 100  # fallback if API fails
        st.warning("⚠️ Unable to fetch live data. Using default flux: 100 p/cm²/s/sr")

    # Simplified dose model
    base_dose_per_day = flux * 0.00005  # empirical approximation
    shield_factors = {'None': 1.0, 'Aluminum': 0.7, 'Polyethylene': 0.5}
    daily_dose = base_dose_per_day * shield_factors[shielding_material]
    total_dose = daily_dose * mission_days  # in mSv

    # Cancer risk estimate
    risk_percent = (total_dose / 1000) * 5  # linear ERR model

    st.metric("☢️ Estimated Total Dose (mSv)", f"{total_dose:.2f}")
    st.metric("⚠️ Estimated Cancer Risk", f"{risk_percent:.2f} %")

    st.caption("ICRP model: 5% risk increase per 1 Sv of exposure. Not for clinical use.")

    # Dose over time graph
    import matplotlib.pyplot as plt
    import numpy as np

    st.subheader("📊 Dose Accumulation Over Time")
    days = np.arange(1, mission_days + 1)
    dose_over_time = daily_dose * days

    fig, ax = plt.subplots()
    ax.plot(days, dose_over_time, color='crimson')
    ax.set_xlabel("Days")
    ax.set_ylabel("Cumulative Dose (mSv)")
    ax.set_title("Radiation Dose Accumulation")
    st.pyplot(fig)

    # Monte Carlo simulation
    st.subheader("🎲 Monte Carlo Simulation (1000 Astronauts)")
    simulated_doses = np.random.normal(loc=total_dose, scale=0.1 * total_dose, size=1000)

    fig2, ax2 = plt.subplots()
    ax2.hist(simulated_doses, bins=30, color='orange', edgecolor='black')
    ax2.set_title("Simulated Dose Distribution")
    ax2.set_xlabel("Total Dose (mSv)")
    ax2.set_ylabel("Number of Astronauts")
    st.pyplot(fig2)

    # Shielding effectiveness table
    import pandas as pd
    st.subheader("🛡️ Shielding Material Effectiveness")

    data_table = {
        "Material": ["None", "Aluminum", "Polyethylene"],
        "Approx. Dose Reduction (%)": [0, 30, 50]
    }
    df = pd.DataFrame(data_table)
    st.dataframe(df)
# Tab 2: Shower Map
with tabs[1]:
    st.subheader("Cosmic Ray Shower Map (Coming Soon)")
    st.info("Visualize cosmic ray secondary showers using real or simulated data on a world map.")

# Tab 3: Biological Effects
with tabs[2]:
    st.subheader("Biological Effects of Radiation (Coming Soon)")
    st.info("Understand how different radiation doses impact the human body over time.")

# Tab 4: Effects on Electronics
with tabs[3]:
    st.subheader("Effects on Electronics (Coming Soon)")
    st.info("Simulate the impact of cosmic radiation on satellite systems, memory errors, and electronics.")

# Tab 5: CR Data Explorer
with tabs[4]:
    st.subheader("Cosmic Ray Data Explorer (Coming Soon)")
    st.info("Explore real cosmic ray spectra from space missions and particle detectors.")

# Tab 6: Dose Comparison
with tabs[5]:
    st.subheader("Mission Dose Comparator (Coming Soon)")
    st.info("Compare radiation exposure on the ISS, Moon, Mars, and interplanetary space.")

# Tab 7: Space Weather
with tabs[6]:
    st.subheader("Space Weather Live (Coming Soon)")
    st.info("Monitor real-time solar activity including flares, proton flux, and magnetic storms.")

# Tab 8: Research Library
with tabs[7]:
    st.subheader("Research Paper Library (Coming Soon)")
    st.info("Browse curated NASA/ESA research papers related to cosmic radiation.")

# Tab 9: Upload Data
with tabs[8]:
    st.subheader("Upload & Analyze Your Data (Coming Soon)")
    st.info("Upload your own radiation measurement data and analyze it interactively.")

# Footer
st.markdown(f"""
---
<p style='text-align: center; color: gray'>
Built by Tanmay Rajput | Last updated: {datetime.today().strftime('%B %d, %Y')}
</p>
""", unsafe_allow_html=True)
