import streamlit as st
import pandas as pd
from io import BytesIO

from auth import enforce_email_login, render_logout_button

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="CEF - Coach Comparison",
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
        st.image("assets/mkdons_badge.png", width=90)
    except:
        pass

with col2:
    st.markdown(
        "<h1 style='margin-bottom:0;'>CEF - Coach Comparison View</h1>",
        unsafe_allow_html=True
    )

    if st.button("🏠 Home"):
        st.switch_page("app.py")

st.markdown("---")

# ===================== CONSTANTS =====================
GROUP_LABELS = [
    "Understanding Self",
    "Coaching Individuals",
    "Coaching Practice",
    "Skill Acquisition",
    "MK Dons",
    "Psychology/Social Support",
    "Relationships",
    "Athletic Development",
    "Wellbeing/Lifestyle"
]

SAFEGUARDING_QUESTIONS = [
    "Are you aware of the clubs safeguarding policies?",
    "Can you notice changes in child behaviour?",
    "Do you signpost players to appropriate support?",
    "Can you use Myconcern to report safeguarding concerns and follow up where/when appropriate?",
    "Are you comfortable checking (and where necessary) challenging poor practice?"
]

# ===================== COLOUR HELPERS =====================
def get_group_colour(score):
    if score >= 3.51:
        return "#4CAF50"
    elif score >= 2.51:
        return "#FFD966"
    elif score >= 1.51:
        return "#F4A261"
    else:
        return "#FF6B6B"


def get_safeguarding_colour(score):
    if score == 1:
        return "#4CAF50"
    elif score == 0.5:
        return "#F4A261"
    else:
        return "#FF6B6B"

# ===================== DATA HELPERS =====================
def calculate_group_totals(person_data, question_cols):
    totals = []

    for i in range(0, len(question_cols), 4):
        cols = question_cols[i:i+4]
        scores = pd.to_numeric(person_data[cols], errors="coerce")
        totals.append(round(scores.sum(), 2))

    return totals


def render_cef_section(person_data, question_cols):
    st.subheader("CEF Breakdown")

    group_totals = calculate_group_totals(person_data, question_cols)
    cef_total = round(sum(group_totals), 2)

    st.markdown(f"### Score: **{cef_total} / 36**")

    cols = st.columns(3)

    for idx, (label, score) in enumerate(zip(GROUP_LABELS, group_totals)):
        with cols[idx % 3]:
            st.markdown(
                f"""
                <div style="
                    background-color:{get_group_colour(score)};
                    padding:18px;
                    border-radius:10px;
                    text-align:center;
                    margin-bottom:10px;
                    box-shadow:0 4px 10px rgba(0,0,0,0.15);
                ">
                    <div style="font-size:26px;font-weight:bold;">{score}</div>
                    <div style="font-size:12px;">{label}</div>
                </div>
                """,
                unsafe_allow_html=True
            )


def render_safeguarding_section(person_data):
    st.subheader("Safeguarding")

    safeguarding_total = sum(
        pd.to_numeric(person_data[q], errors="coerce")
        for q in SAFEGUARDING_QUESTIONS
    )

    st.markdown(f"### Score: **{safeguarding_total} / 5**")

    cols = st.columns(5)

    for col, q in zip(cols, SAFEGUARDING_QUESTIONS):
        score = pd.to_numeric(person_data[q], errors="coerce")

        with col:
            st.markdown(
                f"""
                <div style="
                    background-color:{get_safeguarding_colour(score)};
                    padding:16px;
                    border-radius:12px;
                    text-align:center;
                    height:130px;
                    box-shadow:0 4px 10px rgba(0,0,0,0.15);
                ">
                    <div style="font-size:26px;font-weight:bold;">{score}</div>
                    <div style="font-size:11px;margin-top:6px;">
                        {q}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )

# ===================== FILE CHECK =====================
if "uploaded_excel_bytes" not in st.session_state:
    st.info("Please upload an Excel file on the Home page to begin.")
    st.stop()

# ===================== LOAD DATA =====================
df = pd.read_excel(BytesIO(st.session_state["uploaded_excel_bytes"]))
df.columns = df.columns.str.strip()

score_map = {
    "YES": 1,
    "Neither YES or NO": 0.5,
    "NO": 0
}

question_cols = [
    "Do you Understand your role?",
    "Do you Engage with Club CPD?",
    "Do you Communicate Effectively?",
    "Do you engage with players at all times and also with parents informally around training and match day?",
    "Do you Understand the game model?",
    "Do you seek to understand others decisions through questions",
    "Do you inspire people and act positively?",
    "Do you set realistic goals for players?",
    "Do you use appropriate interventions when coaching?",
    "Do you understand player differences?",
    "Do you Understand and apply LTPD?",
    "Do you support your coaching with video and data?",
    "Do you introduce each session to players?",
    "Do you embed deliberate practice into sessions?",
    "Do you create action plans for players?",
    "Do you Debrief sessions and fixtures? (with the group and then via FiP)",
    "Do you use the club coaching methodology?",
    "Do you adopt the Academy principles (HOP)",
    "Do you adopt a multi-disciplinary approach?",
    "Are you aware of the clubs safeguarding policies?",
    "Do you embed Competencies into each session?",
    "Can you notice changes in child behaviour?",
    "Do you signpost players to appropriate support?",
    "Do you critically think and challenge where necessary?",
    "Do you manage other staff effectively to assist with the delivery of coaching sessions?",
    "Do you listen and suspend judgement when talking with players?",
    "Do you have a recognised/established coaching cell in the club?",
    "Do you watch other coaches inside the football club?",
    "Do you embed physical development in sessions?",
    "Do you make sessions competitive and realistic?",
    "Do you demonstrate the ability to develop players physically through session design?",
    "Do you drive intensity in training through a variety of coaching interventions/strategies?",
    "Can you use Myconcern to report safeguarding concerns and follow up where/when appropriate?",
    "Are you comfortable checking (and where necessary) challenging poor practice?",
    "Do you have clear interests away from the club that others know about?",
    "Do you embrace MK Dons as your club and act as an ambassador for the club?"
]

question_cols = [c for c in df.columns if c in question_cols]

for col in question_cols:
    df[col] = df[col].map(score_map)

df["Block_Number"] = df.groupby("Full Name").cumcount() + 1
df["Block_Name"] = "Block " + df["Block_Number"].astype(str)

blocks = {}

for block_name in sorted(df["Block_Name"].unique()):
    blocks[block_name] = df[df["Block_Name"] == block_name].reset_index(drop=True)

all_coaches = sorted(df["Full Name"].dropna().unique().tolist())
all_blocks = sorted(blocks.keys())

# ===================== SELECTIONS =====================
st.markdown("## Select Coaches to Compare")

left_select, right_select = st.columns(2)

with left_select:
    st.markdown("### Coach One")
    coach_left = st.selectbox(
        "Coach",
        all_coaches,
        key="coach_left",
        index=None,
        placeholder="Select coach"
    )
    block_left = st.selectbox(
        "Block",
        all_blocks,
        key="block_left",
        index=None,
        placeholder="Select block"
    )

with right_select:
    st.markdown("### Coach Two")
    coach_right = st.selectbox(
        "Coach",
        all_coaches,
        key="coach_right",
        index=None,
        placeholder="Select coach"
    )
    block_right = st.selectbox(
        "Block",
        all_blocks,
        key="block_right",
        index=None,
        placeholder="Select block"
    )

if not all([coach_left, block_left, coach_right, block_right]):
    st.info("Please select both coaches and blocks to begin comparison.")
    st.stop()

# ===================== GET DATA =====================
left_df = blocks[block_left]
right_df = blocks[block_right]

left_data = left_df[left_df["Full Name"] == coach_left]
right_data = right_df[right_df["Full Name"] == coach_right]

if left_data.empty:
    st.warning(f"{coach_left} has no data for {block_left}.")
    st.stop()

if right_data.empty:
    st.warning(f"{coach_right} has no data for {block_right}.")
    st.stop()

left_person = left_data.iloc[0]
right_person = right_data.iloc[0]

# ===================== SIDE BY SIDE OUTPUT =====================
st.markdown("---")

left_col, right_col = st.columns(2)

with left_col:
    st.markdown(f"## {coach_left} ({block_left})")
    render_cef_section(left_person, question_cols)
    st.markdown("---")
    render_safeguarding_section(left_person)

with right_col:
    st.markdown(f"## {coach_right} ({block_right})")
    render_cef_section(right_person, question_cols)
    st.markdown("---")
    render_safeguarding_section(right_person)
