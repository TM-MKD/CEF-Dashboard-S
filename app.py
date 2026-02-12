import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="MK Dons – Coach Evaluation Framework",
    layout="wide"
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
        "<h1 style='margin-bottom:0;'>MK Dons – Coach Evaluation Framework</h1>",
        unsafe_allow_html=True
    )

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

SAFEGUARDING_QUESTIONS = [20, 22, 30, 33, 34]

QUESTION_TEXT = {
    1: "Understands their role (IP/VEO)",
    2: "Engages with club coach CPD",
    3: "Effectively communicates (IP/VEO)",
    4: "Engages with players & parents informally (IP/VEO)",
    5: "Understands the game model",
    6: "Seeks to understand decisions (Q)",
    7: "Is positive and inspiring (IP)",
    8: "Sets realistic goals for players (IP/VEO)",
    9: "Use appropriate interventions (IP/VEO)",
    10: "Understands player differences",
    11: "Understands and applies LTPD",
    12: "Supports coaching with video and data (IP/VEO)",
    13: "Introduces sessions",
    14: "Embeds deliberate practice",
    15: "Creates action plans for players (IP)",
    16: "Debriefs sessions (IP/VEO)",
    17: "Uses club coaching methodology (IP)",
    18: "Adopts Club principles (H-O-P)",
    19: "Adopts multi-disc approach",
    20: "Aware of safeguarding policies/procedures",
    21: "Embeds competencies each session",
    22: "Notices changes in child's behaviour",
    23: "Signposts players to appropriate support (IP/VEO)",
    24: "Critical thinker who checks and challenges",
    25: "Manages other staff supporting sessions",
    26: "Listens and suspends judgement",
    27: "Has a recognised coaching cell (in club)",
    28: "Watches other coaches inside the club",
    29: "Embeds physical development",
    30: "Makes practice competitive & realistic",
    31: "Develops players physically through design",
    32: "Drives intensity using coaching strategies",
    33: "Reports issues using MyConcern appropriately",
    34: "Comfortable challenging poor practice",
    35: "Ambassador of MK Dons",
    36: "Has clear interests away from coaching"
}

# ===================== COLOUR HELPERS =====================
def get_group_colour(score):
    if score >= 3.25:
        return "#4CAF50"
    elif score >= 2.51:
        return "#FFD966"
    elif score >= 1.75:
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

# ===================== FILE UPLOAD =====================
uploaded_file = st.file_uploader("Upload Microsoft Forms Excel Export", type=["xlsx"])

if uploaded_file is None:
    st.info("Please upload the Microsoft Forms export file.")
    st.stop()

# ===================== LOAD RAW FORMS EXPORT =====================
df = pd.read_excel(uploaded_file)

# Identify required columns automatically
timestamp_col = df.columns[0]  # Microsoft Forms always puts timestamp first
name_col = df.columns[1]       # Name is second column

# Question columns = everything after first 4 columns
question_columns_raw = df.columns[4:40]  # 36 questions

# Rename question columns to Q1–Q36
question_map = {question_columns_raw[i]: f"Q{i+1}" for i in range(36)}
df = df.rename(columns=question_map)

# Keep only needed columns
keep_cols = [timestamp_col, name_col] + list(question_map.values())
df = df[keep_cols]

df = df.rename(columns={timestamp_col: "Timestamp", name_col: "Full Name"})

# Convert timestamp
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

# ===================== SCORE MAPPING =====================
score_map = {
    "YES": 1,
    "Neither YES or NO": 0.5,
    "NO": 0
}

question_cols = [f"Q{i}" for i in range(1, 37)]

for col in question_cols:
    df[col] = df[col].map(score_map)

# ===================== CREATE BLOCKS PER COACH =====================
df = df.sort_values(["Full Name", "Timestamp"])

df["Block Number"] = df.groupby("Full Name").cumcount() + 1
df["Block"] = "Block " + df["Block Number"].astype(str)

# ===================== SELECT COACH =====================
coach = st.selectbox(
    "Select Coach",
    options=sorted(df["Full Name"].unique()),
    index=None,
    placeholder="Select a coach"
)

if coach is None:
    st.stop()

coach_df = df[df["Full Name"] == coach]

block_selected = st.selectbox(
    "Select Block",
    options=coach_df["Block"].tolist(),
    index=None,
    placeholder="Select a block"
)

if block_selected is None:
    st.stop()

person_data = coach_df[coach_df["Block"] == block_selected].iloc[0]

# ===================== GROUP TOTALS =====================
def calculate_group_totals(person_data):
    return [
        round(person_data[question_cols[i:i + 4]].sum(), 2)
        for i in range(0, 36, 4)
    ]

def make_group_grid(group_totals):
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

# ===================== CEF BREAKDOWN =====================
st.markdown("---")
st.subheader("CEF Breakdown")

group_totals = calculate_group_totals(person_data)
cef_total = round(sum(group_totals), 2)

st.markdown(f"### Score: **{cef_total} / 36**")
make_group_grid(group_totals)

# ===================== SAFEGUARDING =====================
st.markdown("---")
st.subheader("Safeguarding")

safeguarding_scores = [person_data[f"Q{q}"] for q in SAFEGUARDING_QUESTIONS]
safeguarding_total = sum(safeguarding_scores)

st.markdown(f"### Score: **{safeguarding_total} / 5**")

cols = st.columns(5)
for col, q in zip(cols, SAFEGUARDING_QUESTIONS):
    score = person_data[f"Q{q}"]
    with col:
        st.markdown(
            f"""
            <div style="
                background-color:{get_safeguarding_colour(score)};
                padding:16px;
                border-radius:8px;
                text-align:center;
                height:130px;
                box-shadow:0 4px 10px rgba(0,0,0,0.15);
            ">
                <div style="font-size:12px;font-weight:bold;">Q{q}</div>
                <div style="font-size:11px;margin-top:6px;">
                    {QUESTION_TEXT[q]}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

# ===================== BAR CHART =====================
st.markdown("---")
st.subheader("Question Breakdown")

scores = person_data[question_cols].values
bar_colors = [
    "#4CAF50" if s == 1 else "#F4A261" if s == 0.5 else "#FF6B6B"
    for s in scores
]

fig = go.Figure()
fig.add_trace(go.Bar(
    x=question_cols,
    y=scores,
    marker_color=bar_colors
))
fig.update_layout(
    yaxis=dict(range=[0, 1]),
    xaxis_title="Questions",
    yaxis_title="Score"
)

st.plotly_chart(fig, use_container_width=True)

# ===================== ACTION PLAN =====================
st.markdown("---")
st.subheader("Action Plan")

half_scores, zero_scores = [], []

for q in question_cols:
    score = person_data[q]
    q_num = int(q.replace("Q", ""))

    if score == 0.5:
        half_scores.append(f"Q{q_num} – {QUESTION_TEXT[q_num]}")
    elif score == 0:
        zero_scores.append(f"Q{q_num} – {QUESTION_TEXT[q_num]}")

c1, c2 = st.columns(2)

with c1:
    st.subheader("Scored 0.5 (Developing)")
    for item in half_scores:
        st.write("•", item)

with c2:
    st.subheader("Scored 0 (Needs Attention)")
    for item in zero_scores:
        st.write("•", item)
