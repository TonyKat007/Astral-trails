import streamlit as st
from datetime import datetime
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import folium
import random
from streamlit_folium import st_folium

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

# ========== TAB 1: Radiation Risk Calculator ==========
with tabs[0]:
    st.subheader("Radiation Risk Calculator")
    st.info("This tool estimates the radiation dose and cancer risk for a space mission based on real-time solar particle flux and selected shielding.")
    mission_days = st.slider("Mission Duration (days)", 1, 1000, 180)
    shielding_material = st.selectbox("Shielding Material", ["None", "Aluminum", "Polyethylene"])

    url = "https://services.swpc.noaa.gov/json/goes/primary/integral-protons-3-day.json"
    try:
        data = requests.get(url).json()
        df = pd.DataFrame(data)
        df['time_tag'] = pd.to_datetime(df['time_tag'])
        df['flux'] = pd.to_numeric(df['flux'], errors='coerce')
        flux=df['flux'].iloc[-1]
        st.success(f"Live Proton Flux (≥10 MeV): {flux:.2e} protons/cm²/s/sr")
    except:
        flux = 100
        st.warning("Unable to fetch live data. Using default flux: 100 p/cm²/s/sr")

    base_dose_per_day = flux * 0.00005
    shield_factors = {'None': 1.0, 'Aluminum': 0.7, 'Polyethylene': 0.5}
    daily_dose = base_dose_per_day * shield_factors[shielding_material]
    total_dose = daily_dose * mission_days
    risk_percent = (total_dose / 1000) * 5

    st.metric("☢️ Estimated Total Dose (mSv)", f"{total_dose:.2f}")
    st.metric("⚠️ Estimated Cancer Risk", f"{risk_percent:.2f} %")
    st.caption("ICRP model: 5% risk increase per 1 Sv of exposure. Not for clinical use.")

    st.subheader("Dose Accumulation Over Time")
    days = np.arange(1, mission_days + 1)
    dose_over_time = daily_dose * days
    fig, ax = plt.subplots()
    ax.plot(days, dose_over_time, color='crimson')
    ax.set_xlabel("Days")
    ax.set_ylabel("Cumulative Dose (mSv)")
    ax.set_title("Radiation Dose Accumulation")
    st.pyplot(fig)

    st.subheader("Monte Carlo Simulation (1000 Astronauts)")
    simulated_doses = np.random.normal(loc=total_dose, scale=0.1 * total_dose, size=1000)
    fig2, ax2 = plt.subplots()
    ax2.hist(simulated_doses, bins=30, color='orange', edgecolor='black')
    ax2.set_title("Simulated Dose Distribution")
    ax2.set_xlabel("Total Dose (mSv)")
    ax2.set_ylabel("Number of Astronauts")
    st.pyplot(fig2)

    st.subheader("Shielding Material Effectiveness")
    df = pd.DataFrame({"Material": ["None", "Aluminum", "Polyethylene"], "Approx. Dose Reduction (%)": [0, 30, 50]})
    st.dataframe(df)

# ========== TAB 2: Live Cosmic Ray Shower Map ==========
with tabs[1]:
    st.subheader("Live Cosmic Ray Shower Map")
    st.info("Map currently shows **mock shower data**. Live data from observatories coming soon!")
    m = folium.Map(location=[20, 0], zoom_start=2, tiles="https://stamen-tiles.a.ssl.fastly.net/terrain/{z}/{x}/{y}.png",
                   attr="Map tiles by Stamen Design, under CC BY 3.0. Data by OpenStreetMap, under ODbL.")
    for _ in range(25):
        lat, lon = random.uniform(-60, 60), random.uniform(-180, 180)
        intensity = random.choice(['Low', 'Moderate', 'High'])
        color = {'Low': 'green', 'Moderate': 'orange', 'High': 'red'}[intensity]
        folium.CircleMarker(location=[lat, lon], radius=6, popup=f"Shower\nIntensity: {intensity}", color=color,
                            fill=True, fill_opacity=0.7).add_to(m)
    st_folium(m, width=700)
    st.caption("Simulated data. Future version will include real-time showers from cosmic ray arrays.")
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


    #Monte Carlo simulation of 1000 devices and the effect on them
    
    st.subheader("🎲 Monte Carlo Simulation (1000 Devices)")
    simulated_failures = np.random.normal(loc=total_seus, scale=0.2 * total_seus, size=1000)
    simulated_failures = np.clip(simulated_failures, 0, None)  # no negative SEUs

    fig2, ax2 = plt.subplots()
    ax2.hist(simulated_failures, bins=30, color='purple', edgecolor='black')
    ax2.set_title("Simulated SEU Distribution Across Devices")
    ax2.set_xlabel("Total SEUs")
    ax2.set_ylabel("Number of Devices")
    st.pyplot(fig2)

    st.caption("Simulates variation in SEU impact across 1000 similar devices.")


# Tab 5: CR Data Explorer
with tabs[4]:
    import numpy as np
    import matplotlib.pyplot as plt

    st.subheader("📈 Cosmic Ray Data Explorer")

    source = st.selectbox("🔬 Select Data Source", ["AMS-02", "Voyager 1", "Mock Data"])
    particle = st.selectbox("🧪 Select Particle Type", ["Protons", "Helium Nuclei", "Iron Nuclei"])

    # Generate sample spectra (mock data)
    energy = np.logspace(0.1, 3, 50)  # MeV
    if particle == "Protons":
        flux = 1e4 * energy**-2.7
    elif particle == "Helium Nuclei":
        flux = 1e3 * energy**-2.6
    else:
        flux = 200 * energy**-2.5

    fig, ax = plt.subplots()
    ax.loglog(energy, flux, label=f"{particle} Spectrum")
    ax.set_xlabel("Energy (MeV)")
    ax.set_ylabel("Flux (particles/m²·s·sr·MeV)")
    ax.set_title(f"Cosmic Ray Spectrum - {source}")
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend()

    st.pyplot(fig)

    st.markdown("""
📡 **Cosmic Ray Spectra** represent the distribution of particle flux over different energies.  
These spectra vary based on:
- Particle type (proton, helium, etc.)
- Source (e.g., solar, galactic, extragalactic)
- Location (Earth orbit vs interstellar)

Real data from **AMS-02**, **Voyager**, or **CRDB** can be connected in later versions.
    """)
# Tab 6: Dose Comparison
with tabs[5]:
    import matplotlib.pyplot as plt
    import numpy as np

    st.subheader("🛰️ Space Mission Radiation Dose Comparator")

    # Predefined missions
    missions = ["ISS (LEO)", "Lunar Orbit", "Lunar Surface", "Mars Transit", "Deep Space"]
    daily_doses = [0.3, 0.5, 1.0, 1.8, 2.5]  # mSv/day (based on NASA data ranges)
    durations = {
        "Short (30 days)": 30,
        "Medium (180 days)": 180,
        "Long (900 days)": 900
    }

    duration_choice = st.selectbox("🕒 Mission Duration", list(durations.keys()))
    days = durations[duration_choice]

    total_doses = [dose * days for dose in daily_doses]

    # Display table
    import pandas as pd
    df = pd.DataFrame({
        "Mission": missions,
        "Daily Dose (mSv)": daily_doses,
        f"Total Dose for {days} days (mSv)": total_doses
    })
    st.dataframe(df)

    # Plot
    st.subheader("📊 Total Radiation Dose per Mission")

    fig, ax = plt.subplots()
    bars = ax.bar(missions, total_doses, color="mediumslateblue")
    ax.set_ylabel("Total Dose (mSv)")
    ax.set_title(f"Total Radiation Dose Over {days} Days")
    ax.axhline(1000, color='red', linestyle='--', label="1 Sv Cancer Risk Threshold")
    ax.legend()
    st.pyplot(fig)

    # Summary
    st.markdown(f"""
🔎 **Insights:**
- **LEO (e.g., ISS)** is relatively safe due to Earth's magnetic shielding.
- **Lunar & deep space** missions face **much higher radiation exposure**.
- A **1 Sv dose** is considered to increase lifetime cancer risk by ~5%.

This tool helps in comparing the risk factor across different mission environments.
    """)
# Tab 7: Space Weather
with tabs[6]:
    import requests
    import datetime
    import matplotlib.pyplot as plt

    st.subheader("🌞 Real-Time Space Weather Monitor")

    # --- Proton Flux (≥10 MeV) ---
    st.markdown("### ☢️ Proton Flux (≥10 MeV)")
    try:
        url_proton = "https://services.swpc.noaa.gov/json/goes/primary/integral-protons-3-day.json"
        proton_data = requests.get(url_proton).json()
        times = [datetime.datetime.strptime(p["time_tag"], "%Y-%m-%dT%H:%M:%SZ") for p in proton_data if p["energy"] == ">=10 MeV"]
        fluxes = [float(p["flux"]) for p in proton_data if p["energy"] == ">=10 MeV"]

        fig, ax = plt.subplots()
        ax.plot(times, fluxes, color='red')
        ax.set_title("Proton Flux (GOES - ≥10 MeV)")
        ax.set_ylabel("Flux (protons/cm²·s·sr)")
        ax.set_xlabel("UTC Time")
        ax.grid(True)
        st.pyplot(fig)

        if fluxes[-1] > 100:
            st.warning("⚠️ Elevated proton flux — possible solar event in progress.")
        else:
            st.success("✅ Proton flux is at normal background levels.")
    except:
        st.error("Could not load proton flux data.")

    # --- X-Ray Flux (Solar Flares) ---
    st.markdown("### ⚡ X-Ray Flux (Solar Flares)")
    try:
        url_xray = "https://services.swpc.noaa.gov/json/goes/primary/xrays-3-day.json"
        xray_data = requests.get(url_xray).json()
        x_times = [datetime.datetime.strptime(x["time_tag"], "%Y-%m-%dT%H:%M:%SZ") for x in xray_data]
        short = [float(x["flux"]) for x in xray_data]

        fig, ax = plt.subplots()
        ax.plot(x_times, short, color='orange')
        ax.set_title("X-Ray Short Flux (GOES)")
        ax.set_ylabel("Flux (W/m²)")
        ax.set_xlabel("UTC Time")
        ax.set_yscale("log")
        ax.grid(True)
        st.pyplot(fig)

        if short[-1] > 1e-5:
            st.warning("⚠️ Possible solar flare detected!")
        else:
            st.success("✅ No flare activity at the moment.")
    except:
        st.error("Could not load X-ray data.")

    # --- Kp Index (Geomagnetic Storms) ---
    st.markdown("### 🧭 Kp Index (Geomagnetic Storms)")
    
try:
    url_kp = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
    raw_data = requests.get(url_kp).json()

    # First row is header
    header = raw_data[0]
    rows = raw_data[1:]

    # Convert to DataFrame
    df_kp = pd.DataFrame(rows, columns=header)

    # Convert datetime and Kp to usable types
    df_kp["time_tag"] = pd.to_datetime(df_kp["time_tag"])
    df_kp["Kp"] = pd.to_numeric(df_kp["Kp"], errors='coerce')

    # Plot
    fig, ax = plt.subplots()
    ax.plot(df_kp["time_tag"], df_kp["Kp"], color='blue')
    ax.set_title("NOAA Kp Index (Last 3 Days)")
    ax.set_ylabel("Kp Value")
    ax.set_xlabel("UTC Time")
    ax.grid(True)
    st.pyplot(fig)

    # Last Kp reading warning
    latest_kp = df_kp["Kp"].iloc[-1]
    if latest_kp >= 5:
        st.warning(f"🌐 Geomagnetic storm conditions likely (Kp = {latest_kp})")
    else:
        st.success(f"✅ Geomagnetic field is quiet (Kp = {latest_kp})")

except Exception as e:
    st.error(f"Could not load Kp index data: {e}")

# Tab 8: Research Library
with tabs[7]:
    st.subheader("📚 Research Paper Library")

    st.markdown("""
    Browse handpicked research papers on cosmic rays, radiation health, and space missions.
    """)

    # Example static paper list
    import pandas as pd

    papers = pd.DataFrame({
        "Title": [
            "Comparative study of effects of cosmic rays on the earth’s atmospheric processes ",
            "Beyond Earthly Limits: Protection against Cosmic Radiation through Biological Response Pathways",
            "The effect of cosmic rays on biological systems",
            "Microprocessor technology and single event upset susceptibility",
            "Impact Of Cosmic Rays On Satellite Communications"
        ],
        "Authors": [
            "Arshad Rasheed Ganai and Dr. Suryansh Choudhary",
            "Zahida Sultanova and Saleh Sultansoy",
            "N. K. Belisheva, H. Lammer, H. K. Biernat and E. V. Vashenuyk",
            "L.D. Akers",
            "Dr. Premlal P.D"
        ],
        "Link": [
            "https://www.physicsjournal.in/archives/2020.v2.i1.A.27/comparative-study-of-effects-of-cosmic-rays-on-the-earthrsquos-atmospheric-processes",
            "https://arxiv.org/pdf/2405.12151",
            "https://www.researchgate.net/publication/235958260_The_effect_of_cosmic_rays_on_biological_systems_-_An_investigation_during_GLE_events",
            "https://klabs.org/DEI/References/avionics/small_sat_conference/1996/ldakers.pdf",
            "https://www.iosrjournals.org/iosr-jece/papers/Vol.%2019%20Issue%202/Ser-1/D1902013337.pdf"
        ],
        "Year": [2020, 2024, 2012, 1996, 2024],
        "Tags": ["Atmosphere", "Biology", "Biology", "Electronics", "Electronics"]
    })

    tag = st.selectbox("Filter by Tag", ["All", "Atmosphere", "Biology", "Electronics"])
    if tag != "All":
        filtered = papers[papers["Tags"] == tag]
    else:
        filtered = papers

    st.dataframe(filtered)

    # Add download example
    st.markdown("### 📎 Example Paper Download")
    st.download_button(
        "Download Example Paper (PDF)",
        data=b"%PDF-1.4 ... (fake content)",
        file_name="example_paper.pdf",
        mime="application/pdf"
    )
# Tab 9: cosmic ray data explorerwith tabs[8]:
with tabs[8]:
    st.subheader("📤 Upload & Analyze Your Own Cosmic Ray Dataset")
    uploaded_file = st.file_uploader("Upload your CSV file (must include 'Energy' and 'Flux' columns, max 2MB)", type=["csv"])
    if uploaded_file is not None:
        if uploaded_file.size > 2 * 1024 * 1024:
            st.error("File too large. Please upload a file smaller than 2MB.")
        else:
            try:
                df = pd.read_csv(uploaded_file)
                if 'Energy' in df.columns and 'Flux' in df.columns:
                    st.success("File uploaded and read successfully!")
                    st.markdown("### 📄 Preview of Uploaded Data")
                    st.dataframe(df.head())
                    log_scale = st.checkbox("Log scale", value=True)
                    fig, ax = plt.subplots()
                    ax.plot(df['Energy'], df['Flux'], marker='o', linestyle='-', color='blue')
                    ax.set_xlabel("Energy")
                    ax.set_ylabel("Flux")
                    ax.set_title("Uploaded Cosmic Ray Spectrum")
                    if log_scale:
                        ax.set_yscale("log")
                        ax.set_xscale("log")
                    ax.grid(True, which='both', linestyle='--', alpha=0.5)
                    st.pyplot(fig)
                else:
                    st.error("CSV must contain 'Energy' and 'Flux' columns.")
            except Exception as e:
                st.error(f"Error reading file: {e}")

# ========== FOOTER ==========
st.markdown(f"""
---
<p style='text-align: center; color: gray'>
Built by Tanmay Rajput | Last updated: {datetime.now().strftime('%B %d, %Y')}
</p>
""", unsafe_allow_html=True)

