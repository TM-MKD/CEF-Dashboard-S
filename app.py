import streamlit as st

from auth import enforce_email_login, render_logout_button

st.set_page_config(
    page_title="Home",       
    layout="wide",
    initial_sidebar_state="collapsed"
)

enforce_email_login()
render_logout_button()

st.markdown(
    """
    <style>
    [data-testid="stSidebar"],
    [data-testid="collapsedControl"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ===================== HEADER =====================
col1, col2 = st.columns([1, 6])

with col1:
    try:
        st.image("assets/mkdons_badge.png", width=80)
    except:
        pass

with col2:
    st.markdown(
        "<h1 style='margin:0; padding:0;'>MK Dons – Coach Evaluation Framework</h1>", 
        unsafe_allow_html=True
    )

st.markdown("---")

# ===================== WELCOME MESSAGE =====================
st.markdown("## Welcome")
st.write("Upload your Excel file once, then choose a page below.")

# ===================== FILE UPLOAD =====================
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file is not None:
    st.session_state["uploaded_excel_bytes"] = uploaded_file.getvalue()
    st.session_state["uploaded_excel_name"] = uploaded_file.name
    st.success(f"Loaded file: {uploaded_file.name}")
elif "uploaded_excel_name" in st.session_state:
    st.success(f"Using uploaded file: {st.session_state['uploaded_excel_name']}")
else:
    st.info("Please upload an Excel file to enable the analysis pages.")

st.markdown("---")

# ===================== NAVIGATION BUTTONS =====================
col1, col2, col3 = st.columns(3)
with col1:
    if st.button("⚽ Individual Coach", use_container_width=True):
        st.switch_page("pages/1_Individual_Coach_View.py")

with col2:
    if st.button("👥 Block Average", use_container_width=True):
        st.switch_page("pages/2_Block_Average_View.py")

with col3:
    if st.button("🆚 Coach Comparison", use_container_width=True):
        st.switch_page("pages/3_Coach_Comparison_View.py")

st.markdown("---")
