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
    mission_days = st.slider("Mission Duration (days)", 1, 1000, 180)
    shielding_material = st.selectbox("Shielding Material", ["None", "Aluminum", "Polyethylene"])

    # Real-time proton flux from NOAA
    url = "https://services.swpc.noaa.gov/json/goes/primary/differential-proton-flux-1-day.json"

    try:
        data = requests.get(url).json()
        flux = float(data[-1]['flux'])  # protons/cm²/s/sr
        st.success(f"Live Proton Flux (≥10 MeV): {flux:.2e} protons/cm²/s/sr")
    except:
        flux = 100  # fallback if API fails
        st.warning("Unable to fetch live data. Using default flux: 100 p/cm²/s/sr")

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

    st.subheader("Dose Accumulation Over Time")
    days = np.arange(1, mission_days + 1)
    dose_over_time = daily_dose * days

    fig, ax = plt.subplots()
    ax.plot(days, dose_over_time, color='crimson')
    ax.set_xlabel("Days")
    ax.set_ylabel("Cumulative Dose (mSv)")
    ax.set_title("Radiation Dose Accumulation")
    st.pyplot(fig)

    # Monte Carlo simulation
    st.subheader("Monte Carlo Simulation (1000 Astronauts)")
    simulated_doses = np.random.normal(loc=total_dose, scale=0.1 * total_dose, size=1000)

    fig2, ax2 = plt.subplots()
    ax2.hist(simulated_doses, bins=30, color='orange', edgecolor='black')
    ax2.set_title("Simulated Dose Distribution")
    ax2.set_xlabel("Total Dose (mSv)")
    ax2.set_ylabel("Number of Astronauts")
    st.pyplot(fig2)

    # Shielding effectiveness table
    import pandas as pd
    st.subheader("Shielding Material Effectiveness")

    data_table = {
        "Material": ["None", "Aluminum", "Polyethylene"],
        "Approx. Dose Reduction (%)": [0, 30, 50]
    }
    df = pd.DataFrame(data_table)
    st.dataframe(df)
# Tab 2: Shower Map
with tabs[1]:
    from streamlit_folium import folium_static
    import folium
    import random

    st.subheader("Live Cosmic Ray Shower Map")

    # Mock: Generate fake cosmic ray shower locations
    st.info("Map currently shows **mock shower data**. Live data from observatories coming soon!")

    # Create base map
    m = folium.Map(
    location=[20, 0],
    zoom_start=2,
    tiles="https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png",
    attr="Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL."
)

    # Generate mock secondary showers
    for _ in range(25):
        lat = random.uniform(-60, 60)
        lon = random.uniform(-180, 180)
        intensity = random.choice(['Low', 'Moderate', 'High'])
        color = {'Low': 'green', 'Moderate': 'orange', 'High': 'red'}[intensity]

        folium.CircleMarker(
            location=[lat, lon],
            radius=6,
            popup=f"Secondary Shower\nIntensity: {intensity}",
            color=color,
            fill=True,
            fill_opacity=0.7
        ).add_to(m)

    folium_static(m)

    st.caption("Data simulated for demonstration. Future version will include real-time showers from cosmic ray arrays.")

# Tab 3: Biological Effects
with tabs[2]:
    st.subheader("Biological Effects of Radiation")

    dose = st.slider("Select Radiation Dose (mSv)", 0, 10000, 200)

    # Define effect stage
    if dose < 100:
        effect = "No observable effects. Normal background exposure level."
    elif dose < 500:
        effect = "Minor biological impact. Slight increase in cancer risk."
    elif dose < 1000:
        effect = "Possible nausea, vomiting. Risk of Acute Radiation Syndrome (ARS)."
    elif dose < 3000:
        effect = "Severe ARS symptoms. Temporary sterility possible."
    elif dose < 6000:
        effect = "Life-threatening dose. Intensive treatment required."
    else:
        effect = "Fatal in most cases. Survival unlikely without immediate medical care."

    st.info(f"Biological Effect at {dose} mSv: **{effect}**")

    # Plot: Dose vs Risk Severity
    import matplotlib.pyplot as plt

    st.subheader("Risk Severity Chart")

    doses = [0, 100, 500, 1000, 3000, 6000, 10000]
    risks = [0, 1, 2, 3, 4, 5, 6]
    labels = [
        "None", "Minor Risk", "Mild ARS", "Severe ARS", "Lethal Risk", "Extreme Lethal", "Fatal"
    ]

    fig, ax = plt.subplots()
    ax.plot(doses, risks, color='darkred', linewidth=3)
    ax.axvline(dose, color='blue', linestyle='--')
    ax.set_xticks(doses)
    ax.set_xticklabels([str(d) for d in doses])
    ax.set_yticks(risks)
    ax.set_yticklabels(labels)
    ax.set_xlabel("Dose (mSv)")
    ax.set_ylabel("Biological Risk")
    ax.set_title("Radiation Dose vs. Health Risk")
    st.pyplot(fig)

    # Table: Organ-specific susceptibility (simplified)
    st.subheader("Organ Susceptibility (Generalized)")

    import pandas as pd
    df = pd.DataFrame({
        "Organ": ["Bone Marrow", "GI Tract", "Skin", "Brain", "Reproductive Organs"],
        "Effect at 1000 mSv+": [
            "Reduced blood cell count", "Nausea, diarrhea", "Burns, hair loss",
            "Cognitive impairment", "Sterility"
        ]
    })
    st.dataframe(df)

# Tab 4: Effects on Electronics
with tabs[3]:
    st.subheader("💻 Effects of Cosmic Radiation on Electronics")

    # Inputs
    duration = st.slider("🕒 Mission Duration (days)", 1, 1000, 180)
    shielding = st.selectbox("🛡️ Shielding Level", ["None", "Light", "Heavy"])
    sensitivity = st.selectbox("📦 Electronics Sensitivity", ["Standard", "Hardened", "Critical"])

    # Sensitivity factors
    sensitivity_factor = {
        "Standard": 1.0,
        "Hardened": 0.5,
        "Critical": 2.0
    }

    # Shielding effectiveness
    shielding_factor = {
        "None": 1.0,
        "Light": 0.6,
        "Heavy": 0.3
    }

    # Base SEU rate per day (mock value)
    base_seu_rate = 0.002  # Ups/day

    # Calculate adjusted SEU rate
    adjusted_rate = base_seu_rate * sensitivity_factor[sensitivity] * shielding_factor[shielding]
    total_seus = adjusted_rate * duration

    # Categorize risk
    if total_seus < 1:
        risk = "Low"
        color = "green"
    elif total_seus < 5:
        risk = "Moderate"
        color = "orange"
    else:
        risk = "High"
        color = "red"

    st.metric("📉 Estimated SEUs", f"{total_seus:.2f}")
    st.success(f"⚠️ Failure Risk Level: {risk}")

    # Visualization: Shielding vs SEU Rate
    import matplotlib.pyplot as plt

    st.subheader("📊 SEU Rate vs Shielding")

    levels = ["None", "Light", "Heavy"]
    rates = [base_seu_rate * sensitivity_factor[sensitivity] * shielding_factor[lev] * duration for lev in levels]

    fig, ax = plt.subplots()
    ax.bar(levels, rates, color=['red', 'orange', 'green'])
    ax.set_ylabel("Total SEUs (bit flips)")
    ax.set_title("Effect of Shielding on SEU Risk")
    st.pyplot(fig)

    # Explanation
    st.markdown("""
Cosmic rays, particularly high-energy protons and heavy ions, can disrupt electronics in space.  
These **Single Event Upsets (SEUs)** can cause:
- Memory bit flips
- Logic faults
- Temporary or permanent device failure

**Radiation hardening** and **shielding** are key to reducing these effects in space missions.
    """)


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
