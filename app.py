import streamlit as st
from datetime import datetime
import requests
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import folium
import seaborn as sns
import random
from streamlit_folium import folium_static
import plotly.graph_objects as go
from io import StringIO
import streamlit.components.v1 as components

# App configuration
st.set_page_config(
    page_title="Cosmic Radiation Research Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Caching API requests to avoid continuous refresh
@st.cache_data(ttl=300)
def fetch_json(url):
    try:
        return requests.get(url).json()
    except:
        return None

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

# === TAB 1: Radiation Risk Calculator ===
with tabs[0]:
    st.subheader("Radiation Risk Calculator")
    mission_days = st.slider("Mission Duration (in days)", 1, 1000, 180)
    shielding_material = st.selectbox(
    "Shielding Material", 
    ["None", "Aluminum", "Polyethylene", "Lead", "Water", "Titanium", "Carbon Fiber", "Hydrogen-rich Plastic"]
)


    data = fetch_json("https://services.swpc.noaa.gov/json/goes/primary/integral-protons-3-day.json")
    if data:
        df = pd.DataFrame(data)
        df['time_tag'] = pd.to_datetime(df['time_tag'])
        df['flux'] = pd.to_numeric(df['flux'], errors='coerce')
        flux = df['flux'].iloc[-1]
        st.success(f"Live Proton Flux (≥10 MeV): {flux:.2e} protons/cm²/s/sr")
    else:
        flux = 100
        st.warning("Unable to fetch live data. Using default flux: 100 p/cm²/s/sr")

    base_dose_per_day = flux * 0.00005
    shield_factors = {
    'None': 1.0,
    'Aluminum': 0.7,
    'Polyethylene': 0.5,
    'Lead': 0.3,
    'Water': 0.6,
    'Titanium': 0.75,
    'Carbon Fiber': 0.65,
    'Hydrogen-rich Plastic': 0.4
}

    daily_dose = base_dose_per_day * shield_factors[shielding_material]
    total_dose = daily_dose * mission_days
    risk_percent = (total_dose / 1000) * 5

    st.metric("Estimated Total Dose (mSv)", f"{total_dose:.5f}")
    st.metric("Estimated Cancer Risk", f"{risk_percent:.5f} %")

    st.subheader("Dose Accumulation Over Time")
    days = np.arange(1, mission_days + 1)
    dose_over_time = daily_dose * days
    fig, ax = plt.subplots(figsize=(6, 2.5), dpi=100)  
    # Reduced height & better resolution
    ax.plot(days, dose_over_time, color='crimson')
    ax.set_xlabel("Days")
    ax.set_ylabel("Cumulative Dose (mSv)")
    ax.set_title("Radiation Dose Accumulation", fontsize=12)
    ax.tick_params(axis='both', labelsize=10)
    st.pyplot(fig)


    st.subheader("Monte Carlo Simulation (1000 Astronauts)")
    simulated_doses = np.random.normal(loc=total_dose, scale=0.1 * total_dose, size=1000)

    # Smaller Histogram
    fig2, ax2 = plt.subplots(figsize=(6, 2.5), dpi=100)
    ax2.hist(simulated_doses, bins=30, color='orange', edgecolor='black')
    ax2.set_title("Simulated Dose Distribution", fontsize=12)
    ax2.set_xlabel("Total Dose (mSv)")
    ax2.set_ylabel("Number of Astronauts")
    ax2.tick_params(axis='both', labelsize=10)
    st.pyplot(fig2)


# ===========================================TAB 2: Live Cosmic Ray Shower Map (real-time but not live)====================================================
with tabs[1]:
    import datetime
    import matplotlib.pyplot as plt
    import folium
    from streamlit_folium import folium_static
    import pandas as pd

    st.markdown("### Real-Time Solar Images")
    col1, col2 = st.columns(2)
    with col1:
        st.image("https://services.swpc.noaa.gov/images/animations/lasco-c2/latest.jpg", 
                 caption="SOHO LASCO C2 (Coronal Mass Ejections)", use_container_width=True)

    st.markdown("---")
    st.markdown("### Aurora Forecast Map")
    st.image("https://services.swpc.noaa.gov/images/aurora-forecast-northern-hemisphere.jpg", 
             caption="NOAA Aurora Forecast (Northern Hemisphere)", use_container_width=True)
    st.image("https://services.swpc.noaa.gov/images/aurora-forecast-southern-hemisphere.jpg", 
             caption="NOAA Aurora Forecast (Southern Hemisphere)", use_container_width=True)

    st.markdown("---")
    st.markdown("### ISS Position Tracker")
    try:
        iss_data = requests.get("http://api.open-notify.org/iss-now.json").json()
        iss_lat = float(iss_data['iss_position']['latitude'])
        iss_lon = float(iss_data['iss_position']['longitude'])

        m = folium.Map(location=[iss_lat, iss_lon], zoom_start=2)
        folium.Marker([iss_lat, iss_lon], 
                      popup=f"ISS Location: {iss_lat:.2f}, {iss_lon:.2f}",
                      icon=folium.Icon(color="red", icon="rocket", prefix='fa')).add_to(m)
        folium_static(m)
    except:
        st.warning("Could not fetch ISS position at the moment.")

    st.markdown("---")
    
    st.caption("Dashboard auto-refreshes every 5 minutes. Data courtesy: NOAA SWPC & Open Notify")

    
    st.subheader("Live Cosmic Ray Shower Map")
    m = folium.Map(location=[0, 0], zoom_start=2)

    # ===fetch data===
    data_data= pd.read_csv("TimeStamp.csv")

    # ===Process it===
    data_data.replace("null", pd.NA, inplace=True)
    data_data["TimeStamp"] = pd.to_datetime(data_data["TimeStamp"])
    for col in data_data.columns:
        if col != "TimeStamp":
            data_data[col] = pd.to_numeric(data_data[col], errors="coerce")
    latest = data_data.iloc[-1]
    latest_time = latest["TimeStamp"]    
    station_counts= latest.drop("TimeStamp").to_dict()

    #st.write("Station counts (latest row):", station_counts)

    # ===plotting points===
    
    station_coords = {
    "  ICRB": (28.3, -16.51),
    "     ICRO": (27.3, -15.51),
    "    ATHN": (37.98, 23.73),
    "    CALM": (39.2, -3.2),
    "    BKSN": (43.28, 42.69),
    "    JUNG": (46.55, 7.98),
    "   JUNG1": (45.55, 6.98),
    "    LMKS": (49.2, 20.22),
    "    IRK2": (52.3, 104.3),
    "    DRBS": (50.1, 4.6),
    "    NEWK": (39.68, -75.75),
    "   KIEL2": (54.32, 10.13),
    "    YKTK": (62.02, 129.7),
    "    KERG": (-49.35, 70.25),
    "    CALG": (51.05, -114.07),
    "    OULU": (65.05, 25.47),
    "    APTY": (67.57, 33.38),
    "    TXBY": (71.58, 128.92),
    "    FSMT": (60.02, -111.93),
    "    INVK": (68.36, -133.72),
    "    NAIN": (56.55, -61.68),
    "    PWNK": (54.98, -85.43),
    "    THUL": (76.51, -68.71),
    "    MWSB": (-67.6, 62.88),
    "    MWSN": (-66.6, 61.88),
    "    SOPB": (-90.0, 0.0),
    "    SOPO": (-85.0, 2.0),
    "    TERA": (-66.67, 140.01),
    }

      # ====intensity filter====
    st.markdown("#### Filter Shower Events")
    intensity_options = st.multiselect(
        "Select intensity levels to display",
        options=["Low", "Moderate", "High"],
        default=[ ]
    )

    def get_intensity_level(count):
        if pd.isna(count):
            return "No Data"
        elif count > 200:
            return "High"
        elif count < 200 and count > 100:
            return "Moderate"
        else:
            return "Low"
    # ===color based on intensity===
    def get_color(count):
        if count > 200:
            return 'red'
        elif count < 200 and count > 100:
            return 'orange'
        else:
            return 'green'
    
    #===plotting on map===
    for station, count in station_counts.items():
        if station in station_coords and pd.notna(count):
            lat, lon = station_coords[station]
            intensity = get_intensity_level(count)
            if intensity not in intensity_options:
                continue  # Skip this station if user has filtered it out

            if pd.isna(count):
                color = "gray"
            else:
                color = {
                        "Low": "green",
                        "Moderate": "orange",
                        "High": "red"
                    }.get(intensity, "gray")
            color = get_color(count)
            folium.CircleMarker(
                location=[lat, lon],
                radius=7,
                color=color,
                popup=f"Station: {station}\nRelative Neutron Count: {count}\nDate: \nTime: ",
                fill=True,
                fill_opacity=0.7
            ).add_to(m)

    #===show map===
    folium_static(m)
    st.write("We acknowledge the NMDB database www.nmdb.eu, founded under the European Union's FP7 programme (contract no. 213007) for providing data.")

# Tab 3: Biological Effects
with tabs[2]:
    import os
    from pathlib import Path
    st.subheader("Biological Effects of Radiation over Time")

    # Separator
    st.write("---")
    st.subheader("Customize for Individual Factors and Duration")

    # Age and Gender Inputs
    age = st.slider("Select Age (Years)", 0, 100, 30)
    gender = st.selectbox("Select Gender", ["Male", "Female", "Prefer not to say"])

    # Duration Input (days)
    days = st.slider("Select Duration (Days)", 0, 36500, 30)

    # Base daily cosmic radiation rate (mSv/day) — average cosmic component at sea level (~0.38 mSv/year ⇒ ~0.00104 mSv/day)
    BASE_RATE = 0.00104  # Source: UNSCEAR 2020 report

    # Calculate raw dose over period
    raw_dose = days * BASE_RATE

    # Calculate modifiers
    age_modifier = 1.0
    gender_modifier = 1.0
    if age < 10:
        age_modifier = 1.4
        st.warning("Children under 10 are more radiosensitive; this is factored into the adjusted dose.")
    elif age < 20:
        age_modifier = 1.2
        st.info("Individuals under 20 have increased sensitivity; applied to adjusted dose.")
    elif age > 60:
        age_modifier = 0.9
        st.info("Older adults may have slightly lower long-term cancer risk; applied to adjusted dose.")

    if gender == "Female":
        gender_modifier = 1.1
        st.info("Female sensitivity modifier applied to adjusted dose.")
    elif gender == "Male":
        gender_modifier = 1.0
        st.info("Male baseline sensitivity modifier applied.")
    else:
        st.info("Using general sensitivity modifiers without specific gender differentiation.")

    # Adjust dose
    adjusted_dose = raw_dose * age_modifier * gender_modifier
    st.markdown(f"***Adjusted Cumulative Dose over {days} days: {adjusted_dose:.2f} mSv***")

    # Determine effect and image
    if adjusted_dose < 1:
        effect = "No observable effects."
        img_file = "human_body_healthy.png"
    elif adjusted_dose < 5:
        effect = "Minor biological impact."
        img_file = "human_body_minor_damage.png"
    elif adjusted_dose < 15:
        effect = "Mild ARS possible."
        img_file = "human_body_moderate_damage.png"
    elif adjusted_dose < 30:
        effect = "Severe ARS symptoms."
        img_file = "human_body_severe_damage.png"
    else:
        effect = "Potentially life-threatening dose."
        img_file = "human_body_critical_damage.png"

    st.info(f"Biological Effect: **{effect}** at {adjusted_dose:.2f} mSv")

    # Image loading: ensure correct path
    script_dir = Path(__file__).parent
    image_dir = script_dir / "images"
    image_path = image_dir / img_file

    try:
        st.image(str(image_path), caption=f"Impact Visualization ({adjusted_dose:.0f} mSv)", use_container_width=True)
        st.caption("Disclaimer: Conceptual illustration only.")
    except Exception as e:
        st.error(f"Could not load image: {e}\nCheck that 'images' folder exists alongside this script and contains {img_file}.")
    
        st.subheader("Interactive Risk Severity Chart")
    
    thresholds = [0, 1, 5, 15, 30, 50]
    labels = ["None", "Minor", "Mild ARS", "Severe ARS", "Lethal", "Extreme/Fatal"]
    colors = ["#2ecc71", "#f1c40f", "#f39c12", "#e67e22", "#e74c3c"]
    
    fig = go.Figure()
    for i in range(len(thresholds) - 1):
        fig.add_shape(
            type="rect",
            x0=thresholds[i], x1=thresholds[i+1], y0=0, y1=1,
            fillcolor=colors[i], opacity=0.3, layer="below", line_width=0
        )
        fig.add_annotation(
            x=(thresholds[i]+thresholds[i+1])/2, y=0.95,
            text=labels[i], showarrow=False, font=dict(size=12), opacity=0.8
        )
    
    fig.add_trace(go.Scatter(
        x=[raw_dose], y=[0.5], mode='markers+text', name='Raw Dose',
        marker=dict(size=12), text=['Raw'], textposition='bottom center'
    ))
    fig.add_trace(go.Scatter(
        x=[adjusted_dose], y=[0.5], mode='markers+text', name='Adjusted Dose',
        marker=dict(size=12), text=['Adjusted'], textposition='top center'
    ))
    
    fig.update_layout(
        xaxis=dict(title="Dose (mSv)", range=[0, thresholds[-1]]),
        yaxis=dict(visible=False),
        title="Radiation Dose vs. Biological Risk",
        height=300, margin=dict(t=40, b=40), showlegend=True
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # Enhanced Table: Organ-specific susceptibility with treatments and research
    st.subheader("Organ Susceptibility (Generalized)")
    
    df = pd.DataFrame({
        "Organ": ["Bone Marrow", "GI Tract", "Skin", "Brain", "Reproductive Organs"],
        "Effect at ≥50 mSv": [
            "Reduced blood cell count",
            "Nausea, diarrhea",
            "Burns, hair loss",
            "Cognitive impairment",
            "Sterility"
        ],
        "Possible Treatment / Mitigation": [
            "Bone marrow transplant, G-CSF therapy",
            "Hydration, antiemetics, gut microbiota restoration",
            "Topical steroids, wound care, regenerative creams",
            "Neuroprotective agents, cognitive therapy",
            "Hormone therapy, sperm/egg preservation"
        ],
        "Related Research": [
            "[NCBI](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4368524/)",
            "[NIH](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC2861979/)",
            "[MDPI](https://www.mdpi.com/2072-6694/13/14/3458)",
            "[Nature](https://www.nature.com/articles/s41598-019-42045-3)",
            "[Springer](https://link.springer.com/article/10.1007/s11154-021-09672-2)"
        ]
    })
    
    st.markdown("Hover or click the links in the 'Related Research' column for more information.")
    st.dataframe(df, use_container_width=True)

    
# Tab 4: Effects on Electronics
with tabs[3]:
    st.subheader("Effects of Cosmic Radiation on Electronics")

    # --- Inputs ---
    mission_profile = st.selectbox("Mission Environment", ["ISS (LEO)", "Lunar Orbit", "Mars Transit", "Deep Space"])
    duration = st.slider("Mission Duration (days)", 1, 1000, 180)
    shielding = st.selectbox("Shielding Level", ["None", "Light", "Heavy"])
    sensitivity = st.selectbox("Electronics Sensitivity", ["Standard", "Hardened", "Critical"])

    # --- Mission profile base SEU rate (mocked SPENVIS/ESA data in Ups/day) ---
    mission_base_rates = {
        "ISS (LEO)": 0.0005,
        "Lunar Orbit": 0.002,
        "Mars Transit": 0.004,
        "Deep Space": 0.006
    }
    base_seu_rate = mission_base_rates[mission_profile]

    # --- Sensitivity and Shielding Modifiers ---
    sensitivity_factor = {
        "Standard": 1.0,
        "Hardened": 0.5,
        "Critical": 2.0
    }
    shielding_factor = {
        "None": 1.0,
        "Light": 0.6,
        "Heavy": 0.3
    }

    # --- Adjusted SEU Rate & Total SEUs ---
    adjusted_rate = base_seu_rate * sensitivity_factor[sensitivity] * shielding_factor[shielding]
    total_seus = adjusted_rate * duration

    # --- Risk Categorization ---
    if total_seus < 1:
        risk = "Low"
        color = "green"
    elif total_seus < 5:
        risk = "Moderate"
        color = "orange"
    else:
        risk = "High"
        color = "red"

    st.metric("Estimated SEUs", f"{total_seus:.2f}")
    st.success(f"Failure Risk Level: {risk}")

    # --- SEU Rate vs Shielding ---
    st.subheader("SEU Rate vs Shielding")

    levels = ["None", "Light", "Heavy"]
    rates = [base_seu_rate * sensitivity_factor[sensitivity] * shielding_factor[lev] * duration for lev in levels]

    fig1, ax1 = plt.subplots()
    ax1.bar(levels, rates, color=['red', 'orange', 'green'])
    ax1.set_ylabel("Total SEUs (bit flips)")
    ax1.set_title(f"Effect of Shielding on SEU Risk ({mission_profile})")
    st.pyplot(fig1)

    # --- Monte Carlo Distribution ---
    st.subheader("Monte Carlo Simulation (1000 Devices)")
    simulated_failures = np.random.normal(loc=total_seus, scale=0.2 * total_seus, size=1000)
    simulated_failures = np.clip(simulated_failures, 0, None)

    fig2, ax2 = plt.subplots()
    ax2.hist(simulated_failures, bins=30, color='purple', edgecolor='black')
    ax2.set_title("Simulated SEU Distribution Across Devices")
    ax2.set_xlabel("Total SEUs")
    ax2.set_ylabel("Number of Devices")
    st.pyplot(fig2)

    # --- Real-Time Failure Accumulation---
    st.subheader("Estimated SEU Accumulation Over Time")
    days = np.arange(1, duration + 1)
    accumulated_seus = adjusted_rate * days

    fig3, ax3 = plt.subplots()
    ax3.plot(days, accumulated_seus, color='crimson')
    ax3.set_xlabel("Days")
    ax3.set_ylabel("Cumulative SEUs")
    ax3.set_title("Projected Failure Growth Over Mission Duration")
    st.pyplot(fig3)

    # --- Description ---
    st.markdown(f"""
**Environment**: {mission_profile}  
**Base SEU Rate**: {base_seu_rate:.4f} Ups/day (mocked NASA/ESA data)  
**Sensitivity Mod**: ×{sensitivity_factor[sensitivity]}  
**Shielding Mod**: ×{shielding_factor[shielding]}  

Total expected SEUs are computed using environment- and hardware-specific radiation risk assumptions.  
This model helps evaluate how electronics might behave in varied mission profiles.
    """)



# Tab 5: CR Data Explorer
with tabs[4]:
    import numpy as np
    import matplotlib.pyplot as plt

    st.subheader("Cosmic Ray Data Explorer")
    st.markdown("Explore how different particles behave over energy ranges using mock spectra.")

    # Dropdowns for user input
    source = st.selectbox("Select Data Source", ["AMS-02", "Voyager 1", "Mock Data"])
    particle = st.selectbox("Select Particle Type", ["Protons", "Helium Nuclei", "Iron Nuclei"])

    # Generate sample spectra (mock data)
    energy = np.logspace(0.1, 3, 50)  # MeV range
    if particle == "Protons":
        flux = 1e4 * energy**-2.7
    elif particle == "Helium Nuclei":
        flux = 1e3 * energy**-2.6
    else:
        flux = 200 * energy**-2.5

    # Add slight noise if mock data is selected
    if source == "Mock Data":
        flux *= np.random.normal(1.0, 0.05, size=flux.shape)

    # Plotting the spectrum
    fig, ax = plt.subplots()
    ax.loglog(energy, flux, label=f"{particle} Spectrum")
    ax.set_xlabel("Energy (MeV)")
    ax.set_ylabel("Flux (particles/m²·s·sr·MeV)")
    ax.set_title(f"Cosmic Ray Spectrum - {source}")
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    ax.legend()

    st.pyplot(fig)

    # Description
    st.markdown("""
    **Cosmic Ray Spectra** represent the distribution of particle flux over different energies.

    These spectra vary based on:
    - Source (e.g., solar, galactic, extragalactic)
    - Particle type (proton, helium, iron, etc.)
    - Location (Earth orbit, interstellar space, etc.)

    Real data from **AMS-02**, **Voyager**, and **CRDB** can be integrated in future releases.
    """)

# Tab 6: Dose Comparison
with tabs[5]:  # Mission Dose Comparator Tab
    import plotly.express as px
    from fpdf import FPDF
    import altair as alt

    # ---- 1. REAL-WORLD DATA INTEGRATION (NASA/ESA) ----
    @st.cache_data(ttl=3600)
    def fetch_space_radiation_data():
        """Fetch live radiation data from ESA API only. NASA's InSight API is deprecated."""
        try:
            esa_response = requests.get("https://swe.ssa.esa.int/radiation/api/data/latest")
            esa_data = esa_response.json()

            return {
            "iss": 0.3,  # Fallback or hardcoded ISS value
            "lunar": esa_data.get("lunar_surface", 0.5),
            "mars_transit": esa_data.get("mars_transit", 1.8),
            "deep_space": esa_data.get("galactic", 2.5)
            }
        except Exception as e:
            st.warning(f"⚠️ Could not fetch ESA data: {str(e)}. Using fallback values.")
            return {
                "iss": 0.3,
                "lunar": 0.5,
                "mars_transit": 1.8,
                "deep_space": 2.5
            }

    
    radiation_data = fetch_space_radiation_data()

    # ---- 2. DYNAMIC SHIELDING MODEL ----
    st.subheader("Shielding Configuration")
    col1, col2 = st.columns(2)
    with col1:
        material = st.selectbox(
            "Material",
            ["Aluminum", "Polyethylene", "Water", "Regolith"],
            help="Density: Aluminum (2.7 g/cm³), Polyethylene (0.93 g/cm³)"
        )
    with col2:
        thickness = st.slider(
            "Thickness (g/cm²)",
            0, 50, 10,
            help="5-10 g/cm² typical for spacecraft"
        )

    # Shielding attenuation formula (exponential absorption)
    attenuation_factors = {
        "Aluminum": 0.07,
        "Polyethylene": 0.05,
        "Water": 0.06,
        "Regolith": 0.04
    }
    shielding_factor = np.exp(-thickness * attenuation_factors[material])

    # ---- 3. SOLAR CYCLE ADJUSTMENT ----
    solar_phase = st.radio(
        "Solar Activity Phase",
        ["Solar Max (Lowest Radiation)", "Average", "Solar Min (Highest Radiation)"],
        horizontal=True
    )
    solar_modifiers = {
        "Solar Max (Lowest Radiation)": 0.7,
        "Average": 1.0,
        "Solar Min (Highest Radiation)": 1.3
    }

    # ---- 4. MISSION PARAMETERS ----
    st.subheader("Mission Profile")
    mission = st.selectbox(
        "Select Mission Profile",
        ["ISS (Low Earth Orbit)", "Lunar Orbit", "Lunar Surface", "Mars Transit", "Deep Space"],
        index=0
    )
    
    duration = st.slider(
        "Duration (days)",
        1, 1000, 180,
        help="Typical ISS mission: 180 days"
    )

    # Base dose rates (mSv/day)
    base_doses = {
        "ISS (Low Earth Orbit)": radiation_data["iss"],
        "Lunar Orbit": radiation_data["lunar"],
        "Lunar Surface": radiation_data["lunar"] * 1.2,
        "Mars Transit": radiation_data["mars_transit"],
        "Deep Space": radiation_data["deep_space"]
    }

    # ---- CALCULATIONS ----
    adjusted_dose_rate = (base_doses[mission] * 
                          shielding_factor * 
                          solar_modifiers[solar_phase])
    total_dose = adjusted_dose_rate * duration

    # ---- 5. ORGAN DOSE BREAKDOWN ----
    st.subheader("Organ-Specific Radiation Exposure")
    organs = {
        "Skin": 1.1,
        "Eyes": 1.5,
        "Bone Marrow": 1.0,
        "Brain": 0.8,
        "Heart": 0.9
    }
    
    organ_doses = {
        organ: total_dose * factor 
        for organ, factor in organs.items()
    }
    
    # Plotly bar chart
    fig_organs = px.bar(
        x=list(organ_doses.keys()),
        y=list(organ_doses.values()),
        color=list(organ_doses.keys()),
        labels={"x": "Organ", "y": "Dose (mSv)"},
        title="Equivalent Dose by Organ"
    )
    st.plotly_chart(fig_organs, use_container_width=True)

    # ---- 6. HISTORICAL COMPARISON ----
    st.subheader("Comparison with Real Missions")
    historic_missions = {
        "ISS (6 months)": 80,
        "Apollo 14 (9 days)": 1.14,
        "Mars Curiosity (8 years)": 1200,
        "Your Mission": total_dose
    }
    
    fig_compare = px.bar(
        x=list(historic_missions.keys()),
        y=list(historic_missions.values()),
        color=list(historic_missions.keys()),
        labels={"x": "Mission", "y": "Total Dose (mSv)"}
    )
    st.plotly_chart(fig_compare, use_container_width=True)

    # ---- 7. RISK ALERTS ----
    st.subheader("Risk Assessment")
    if total_dose > 1000:
        st.error(f"DANGER: {total_dose:.1f} mSv exceeds NASA career limit (1000 mSv)")
    elif total_dose > 500:
        st.warning(f"WARNING: {total_dose:.1f} mSv exceeds 1-year limit (500 mSv)")
    else:
        st.success(f"SAFE: {total_dose:.1f} mSv within allowable limits")

    # ---- 8. MONTE CARLO SIMULATION ----
    st.subheader("Dose Uncertainty Simulation")
    simulated_doses = np.random.normal(
        loc=total_dose,
        scale=total_dose*0.25,  # 25% variability
        size=1000
    )
    
    fig_sim = px.histogram(
        simulated_doses,
        nbins=30,
        labels={"value": "Possible Total Dose (mSv)"},
        title="1000 Simulated Missions (Variability from space weather)"
    )
    st.plotly_chart(fig_sim, use_container_width=True)



# Tab 7: Space Weather Live

with tabs[6]:
    import requests
    import datetime
    import matplotlib.pyplot as plt
    import folium
    from streamlit_folium import folium_static
    import pandas as pd
    
    st.subheader("Real-Time Solar System Monitor")
    
    import streamlit as st
    iframe_html = """
    <iframe
        src="https://eyes.nasa.gov/apps/solar-system/#/home?embed=true&logo=false&menu=false"
        width="100%"
        height="500px"
        frameborder="0"
    ></iframe>
    """

    st.components.v1.html(iframe_html, height=520)
    
    # --- Proton Flux (≥10 MeV) ---
    st.markdown("### Proton Flux (≥10 MeV)")
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
            st.warning("Elevated proton flux — possible solar event in progress.")
        else:
            st.success("Proton flux is at normal background levels.")
    except Exception as e:
        st.error(f"Could not load proton flux data: {e}")

    # --- X-Ray Flux ---
    st.markdown("### X-Ray Flux (Solar Flares)")
    try:
        url_xray = "https://services.swpc.noaa.gov/json/goes/primary/xrays-3-day.json"
        xray_data = requests.get(url_xray).json()
        x_times = [datetime.datetime.strptime(x["time_tag"], "%Y-%m-%dT%H:%M:%SZ") for x in xray_data]
        short_flux = [float(x["flux"]) for x in xray_data]

        fig, ax = plt.subplots()
        ax.plot(x_times, short_flux, color='orange')
        ax.set_title("X-Ray Flux (GOES)")
        ax.set_ylabel("Flux (W/m²)")
        ax.set_xlabel("UTC Time")
        ax.set_yscale("log")
        ax.grid(True)
        st.pyplot(fig)

        if short_flux[-1] > 1e-5:
            st.warning("Possible solar flare detected!")
        else:
            st.success("No significant X-ray activity.")
    except Exception as e:
        st.error(f"Could not load X-ray flux data: {e}")

    # --- Kp Index ---
    st.markdown("### Kp Index (Geomagnetic Activity)")
    try:
        url_kp = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"
        raw_data = requests.get(url_kp).json()
        header = raw_data[0]
        rows = raw_data[1:]
        df_kp = pd.DataFrame(rows, columns=header)
        df_kp["time_tag"] = pd.to_datetime(df_kp["time_tag"])
        df_kp["Kp"] = pd.to_numeric(df_kp["Kp"], errors='coerce')

        fig, ax = plt.subplots()
        ax.plot(df_kp["time_tag"], df_kp["Kp"], color='blue')
        ax.set_title("Kp Index (NOAA - Last 3 Days)")
        ax.set_ylabel("Kp Value")
        ax.set_xlabel("UTC Time")
        ax.grid(True)
        st.pyplot(fig)

        latest_kp = df_kp["Kp"].iloc[-1]
        if latest_kp >= 5:
            st.warning(f"Geomagnetic storm likely (Kp = {latest_kp})")
        else:
            st.success(f"Geomagnetic field is quiet (Kp = {latest_kp})")
    except Exception as e:
        st.error(f"Could not load Kp index data: {e}")


    # --- Solar Flare Map (Mock Locations) ---
    st.markdown("### Solar Flare Activity Map")
    try:
        m = folium.Map(location=[0, 0], zoom_start=2)
        # Random mock locations with intensity
        flare_locations = [
            {"lat": 20, "lon": 80, "intensity": "High"},
            {"lat": -10, "lon": -60, "intensity": "Moderate"},
            {"lat": 35, "lon": 120, "intensity": "Low"}
        ]
        for flare in flare_locations:
            color = {"High": "red", "Moderate": "orange", "Low": "green"}[flare["intensity"]]
            folium.CircleMarker(
                location=[flare["lat"], flare["lon"]],
                radius=8,
                color=color,
                fill=True,
                fill_opacity=0.7,
                popup=f"Solar Flare: {flare['intensity']}"
            ).add_to(m)
        folium_static(m)
        st.caption("Note: Map shows simulated flare locations.")
    except Exception as e:
        st.error(f"Error rendering solar flare map: {e}")

# Tab 8: Research Library
with tabs[7]:
    st.subheader("Research Paper Library")

    st.markdown("""
    Browse handpicked research papers on cosmic rays, radiation health, and space missions.
    """)

    import pandas as pd

    papers = pd.DataFrame({
        "Title": [
            "Comparative study of effects of cosmic rays on the earth’s atmospheric processes",
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
        "Tags": ["Atmosphere", "Biology", "Biology", "Electronics", "Electronics"],
        "Summary": [
            "This paper analyzes how cosmic rays interact with the Earth’s atmosphere, influencing weather patterns and climate variability. It compares different models to understand the impact of cosmic ray flux on atmospheric ionization and cloud formation.",
            
            "This paper explores biological pathways and protective measures against harmful cosmic radiation exposure. It reviews cellular responses, genetic impacts, and adaptive mechanisms found in various organisms. The study emphasizes the importance of biological shielding for deep-space missions and human health.",
            
            "Examines biological impacts of cosmic ray exposure.",
            
            "The study investigates how microprocessor circuits are vulnerable to single event upsets (SEUs) caused by cosmic rays. It presents test results and real-case observations from satellite missions. Recommendations for radiation-hardening techniques and fault-tolerant designs are provided.",
             
            "This paper discusses the adverse effects of cosmic rays on satellite communication systems. It explains how high-energy particles can induce bit errors and signal loss in satellite electronics. Mitigation strategies and design considerations are also highlighted to enhance system reliability."
        ]
    })

    tag = st.selectbox("Filter by Tag", ["All", "Atmosphere", "Biology", "Electronics"])
    if tag != "All":
        filtered = papers[papers["Tags"] == tag]
    else:
        filtered = papers

    st.dataframe(filtered)

    st.markdown("### Paper Summaries")
    for _, row in filtered.iterrows():
        st.write(f"**{row['Title']}**")
        st.write(f"*Authors:* {row['Authors']}")
        st.write(f"*Year:* {row['Year']}")
        st.write(f"*Summary:* {row['Summary']}")
        st.write(f"[Read Paper]({row['Link']})")
        st.write("---")

    st.markdown("### Example Paper Download")
    st.download_button(
        "Download Example Paper (PDF)",
        data=b"%PDF-1.4 ... (fake content)",
        file_name="example_paper.pdf",
        mime="application/pdf"
    )

# Tab 9: cosmic ray data explorerwith tabs[8]:
with tabs[8]:
    st.subheader("📤 Universal CSV Analyzer")
    
    MAX_FILE_MB = 500  # Should match .streamlit/config.toml
    uploaded_file = st.file_uploader(f"Upload any CSV file (Max {MAX_FILE_MB} MB)", type=["csv"])

    if uploaded_file is not None:
        file_size_mb = uploaded_file.size / (1024 * 1024)
        st.info(f"Uploaded file size: **{file_size_mb:.2f} MB**")

        if file_size_mb > MAX_FILE_MB:
            st.error(f"File too large! Limit is {MAX_FILE_MB} MB.")
        else:
            try:
                df = pd.read_csv(uploaded_file)
                st.success(f"File uploaded successfully! Shape: {df.shape[0]} rows × {df.shape[1]} columns")

                # --- Show basic info ---
                st.markdown("### Preview of Data")
                st.dataframe(df.head())

                st.markdown("### Dataset Summary")
                buffer = StringIO()
                df.info(buf=buffer)
                st.text(buffer.getvalue())

                # --- Handle numeric columns ---
                numeric_cols = df.select_dtypes(include=np.number).columns.tolist()

                if numeric_cols:
                    st.markdown("### Numeric Columns Summary")
                    st.dataframe(df[numeric_cols].describe())


                    # --- Correlation Heatmap ---
                    st.markdown("### Correlation Heatmap")
                    fig, ax = plt.subplots(figsize=(min(0.8*len(numeric_cols),12), 4))
                    sns.heatmap(df[numeric_cols].corr(), annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
                    st.pyplot(fig)

                    # --- Histogram for each numeric column ---
                    st.markdown("### Histograms")
                    for col in numeric_cols:
                        fig, ax = plt.subplots()
                        sns.histplot(df[col].dropna(), kde=True, ax=ax, color='blue')
                        ax.set_title(f"Distribution of {col}")
                        st.pyplot(fig)

                    # --- Scatter Matrix ---
                    st.markdown("### Scatter Matrix (First 5 Numeric Columns)")
                    if len(numeric_cols) > 1:
                        fig = px.scatter_matrix(df[numeric_cols[:5]])
                        st.plotly_chart(fig, use_container_width=True)

                    # --- Custom Plot ---
                    st.markdown("### Custom Plot Builder")
                    x_axis = st.selectbox("Select X-axis", options=["None"] + numeric_cols)
                    y_axis = st.selectbox("Select Y-axis", options=numeric_cols)
                    if x_axis != "None":
                        fig = px.scatter(df, x=x_axis, y=y_axis, title=f"{y_axis} vs {x_axis}")
                        st.plotly_chart(fig, use_container_width=True)
                    else:
                        st.line_chart(df[y_axis], use_container_width=True)
                else:
                    st.warning("No numeric columns found to analyze!")
            except Exception as e:
                st.error(f"Error reading file: {e}")

# FOOTER
st.markdown(
    """
    <div class="css-1q8dd3e">
      Built by the Impostor Among Us | Last updated: {date}
    </div>
    """.format(date=datetime.datetime.now().strftime("%B %d, %Y")),
    unsafe_allow_html=True
)
