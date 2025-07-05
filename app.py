import streamlit as st
from datetime import datetime
import matplotlib.pyplot as plt  # Import at the top for cleaner structure
import pandas as pd  # Import at the top for cleaner structure
import os
from pathlib import Path
import plotly.graph_objects as go  # Plotly for interactive charts

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
Welcome to the **Cosmic Radiation Research Dashboard** — an interactive platform to explore cumulative radiation exposure over time, factoring in individual sensitivity.

---

**Select a feature tab below to begin your research:**
""")

# Main Feature Tabs
tabs = st.tabs([
    "Biological Effects Visualizer",
])

# Tab: Biological Effects Visualizer
with tabs[0]:
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
        st.image(str(image_path), caption=f"Impact Visualization ({adjusted_dose:.0f} mSv)", use_column_width=True)
        st.caption("Disclaimer: Conceptual illustration only.")
    except Exception as e:
        st.error(f"Could not load image: {e}\nCheck that 'images' folder exists alongside this script and contains {img_file}.")

    # Interactive Risk chart
    st.subheader("📊 Interactive Risk Severity Chart")

    # Define thresholds and labels
    thresholds = [0, 1, 5, 15, 30, 50]
    labels = ["None", "Minor", "Mild ARS", "Severe ARS", "Lethal", "Extreme/Fatal"]
    colors = ["#2ecc71", "#f1c40f", "#f39c12", "#e67e22", "#e74c3c"]

    # Create Plotly figure
    fig = go.Figure()
    # Background zones
    for i in range(len(thresholds) - 1):
        fig.add_shape(
            type="rect",
            x0=thresholds[i], x1=thresholds[i+1], y0=0, y1=1,
            fillcolor=colors[i], opacity=0.3, layer="below", line_width=0
        )
        fig.add_annotation(
            x=(thresholds[i]+thresholds[i+1]) / 2, y=0.95,
            text=labels[i], showarrow=False, font=dict(size=12), opacity=0.8
        )

    # Plot markers: raw dose and adjusted dose
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
        yaxis=dict(visible=False), title="Radiation Dose vs. Biological Risk",
        height=300, margin=dict(t=40, b=40), showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)

    # Table: Organ-specific susceptibility
    st.subheader("Organ Susceptibility (Generalized)")
    df = pd.DataFrame({
        "Organ": ["Bone Marrow", "GI Tract", "Skin", "Brain", "Reproductive Organs"],
        "Effect at ≥50 mSv": [
            "Reduced blood cell count", "Nausea, diarrhea", "Burns, hair loss",
            "Cognitive impairment", "Sterility"
        ]
    })
    st.dataframe(df)

# Footer
st.markdown(f"""
---
<p style='text-align: center; color: gray'>
Built by Tanmay Rajput | Last updated: {datetime.today().strftime('%B %d, %Y')}
</p>
""", unsafe_allow_html=True)
