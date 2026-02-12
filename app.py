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

QUESTION_TEXT = {i: f"Question {i}" for i in range(1, 37)}

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

df = pd.read_excel(uploaded_file)

# ===================== AUTO-DETECT COLUMNS =====================
# Microsoft Forms always includes a timestamp column
timestamp_col = [c for c in df.columns if "time" in c.lower()][0]

# Detect Full Name column automatically
name_col = [c for c in df.columns if "name" in c.lower()][0]

# Question columns = everything AFTER the name column
name_index = df.columns.get_loc(name_col)
question_columns_raw = df.columns[name_index + 3 : name_index + 3 + 36]

# Rename questions to Q1–Q36
question_map = {question_columns_raw[i]: f"Q{i+1}" for i in range(36)}
df = df.rename(columns=question_map)

# Keep only required columns
keep_cols = [timestamp_col, name_col] + list(question_map.values())
df = df[keep_cols]

df = df.rename(columns={
    timestamp_col: "Timestamp",
    name_col: "Full Name"
})

# ===================== CLEAN & SCORE =====================
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

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

# ===================== COACH SELECT =====================
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

# ===================== GROUP FUNCTIONS =====================
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
            </div>
            """,
            unsafe_allow_html=True
        )
