print("Amogus")
import streamlit as st

# --- PAGE CONFIG ---
st.set_page_config(page_title="EquiViz", layout="wide")

# --- APP STATE ---
if "portfolio_declared" not in st.session_state:
    st.session_state["portfolio_declared"] = False

# --- SIDEBAR ---
st.sidebar.title("Nav")

tabs = {
    "Home": "🏠 Home",
    "Overview": "📈 Portfolio Overview",
    "Performance": "💹 Performance Analysis",
    "Risk": "⚠️ Risk Metrics",
    "Insights": "🔍 Insights & Reports"
}

disabled_tabs = [tab for tab in tabs if tab != "Home" and not st.session_state["portfolio_declared"]]
selected_tab = "Home"

for tab, label in tabs.items():
    if tab in disabled_tabs:
        st.sidebar.markdown(
            f"<p style='color:gray; opacity:0.6; cursor:not-allowed;'>{label}</p>",
            unsafe_allow_html=True,
        )
    else:
        if st.sidebar.button(label):
            selected_tab = tab

# --- MAIN CONTENT AREA ---
if selected_tab == "Home":
    st.markdown(
        """
        <style>
        .center-wrapper {
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            min-height: 75vh;
        }
        .center-wrapper h1 {
            font-size: 2.8em;
            font-weight: 700;
            margin-bottom: 0.2em;
        }
        .center-wrapper p {
            font-size: 1.1em;
            margin-bottom: 1.5em;
            color: #cccccc;
        }
        .button-row {
            display: flex;
            gap: 1.5rem;
            justify-content: center;
            margin-bottom: 1.5rem;
            flex-wrap: wrap;
        }
        .stButton > button {
            background-color: #262730;
            border: 1px solid #555;
            border-radius: 8px;
            color: white;
            padding: 0.6rem 1.2rem;
            font-size: 1rem;
        }
        </style>
        <div class="center-wrapper">
            <h1>Portfolio Dashboard</h1>
            <p>Get started by declaring your portfolio below.</p>
            <div class="button-row">
        """,
        unsafe_allow_html=True,
    )

    # Inject actual Streamlit buttons (still functional)
    col1, col2 = st.columns(2)
    with col1:
        st.button("➕ Create Portfolio", key="create")
    with col2:
        st.button("📁 Upload Portfolio", key="upload")

    st.markdown(
        """
            </div>
            <div style="max-width: 500px;">
                <div class="stAlert stAlert--info" role="alert">
                    Tabs will be unlocked once you create/upload a portfolio.
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

else:
    st.warning("Please create or upload a portfolio first to access this page.")

# --- FOOTER ---
st.markdown(
    """
    <hr>
    <center>
    <small>📊 EquiViz — Modular Streamlit Framework</small>
    </center>
    """,
    unsafe_allow_html=True,
)