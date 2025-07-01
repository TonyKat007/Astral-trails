import streamlit as st
from datetime import datetime

# App configuration
st.set_page_config(
    page_title="Cosmic Radiation Research Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Title
st.title("☄️ Cosmic Radiation Research Dashboard")

# Intro section on homepage
st.markdown("""
Welcome to the **Cosmic Radiation Research Dashboard** — an interactive platform to explore real-time and simulated data on cosmic rays, their biological and technological effects, and mission safety.

---

**🔍 Select a feature tab below to begin your research:**
""")

# Main Feature Tabs
tabs = st.tabs([
    "🧮 Radiation Risk Calculator",
    "🗺️ Live Cosmic Ray Shower Map",
    "🧠 Biological Effects Visualizer",
    "💻 Effects on Electronics",
    "📈 Cosmic Ray Data Explorer",
    "🛰️ Mission Dose Comparator",
    "🌞 Space Weather Live",
    "📚 Research Library",
    "📤 Upload & Analyze Your Data"
])

# Tab 1: Radiation Risk Calculator
with tabs[0]:
    st.subheader("🧮 Radiation Risk Calculator")
    st.info("This tool estimates the radiation dose and cancer risk for a space mission based on real-time solar particle flux and selected shielding.")

# Tab 2: Shower Map
with tabs[1]:
    st.subheader("🗺️ Cosmic Ray Shower Map (Coming Soon)")
    st.info("Visualize cosmic ray secondary showers using real or simulated data on a world map.")

# Tab 3: Biological Effects
with tabs[2]:
    st.subheader("🧠 Biological Effects of Radiation (Coming Soon)")
    st.info("Understand how different radiation doses impact the human body over time.")

# Tab 4: Effects on Electronics
with tabs[3]:
    st.subheader("💻 Effects on Electronics (Coming Soon)")
    st.info("Simulate the impact of cosmic radiation on satellite systems, memory errors, and electronics.")

# Tab 5: CR Data Explorer
with tabs[4]:
    st.subheader("📈 Cosmic Ray Data Explorer (Coming Soon)")
    st.info("Explore real cosmic ray spectra from space missions and particle detectors.")

# Tab 6: Dose Comparison
with tabs[5]:
    st.subheader("🛰️ Mission Dose Comparator (Coming Soon)")
    st.info("Compare radiation exposure on the ISS, Moon, Mars, and interplanetary space.")

# Tab 7: Space Weather
with tabs[6]:
    st.subheader("🌞 Space Weather Live (Coming Soon)")
    st.info("Monitor real-time solar activity including flares, proton flux, and magnetic storms.")

# Tab 8: Research Library
with tabs[7]:
    st.subheader("📚 Research Paper Library (Coming Soon)")
    st.info("Browse curated NASA/ESA research papers related to cosmic radiation.")

# Tab 9: Upload Data
with tabs[8]:
    st.subheader("📤 Upload & Analyze Your Data (Coming Soon)")
    st.info("Upload your own radiation measurement data and analyze it interactively.")

# Footer
st.markdown(f"""
---
<p style='text-align: center; color: gray'>
🚀 Built by Tanmay Rajput | Last updated: {datetime.today().strftime('%B %d, %Y')}
</p>
""", unsafe_allow_html=True)
