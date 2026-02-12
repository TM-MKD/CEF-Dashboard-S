import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="MK Dons – Coach Evaluation Framework",
    layout="wide"
)

# ===================== HEADER =====================
st.title("MK Dons – Coach Evaluation Framework")
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

# ===================== FILE UPLOAD =====================
uploaded_file = st.file_uploader(
    "Upload Microsoft Forms Excel Export",
    type=["xlsx"]
)

if uploaded_file is None:
    st.stop()

df = pd.read_excel(uploaded_file)

# ===================== IDENTIFY COLUMNS SAFELY =====================

# Find timestamp column
timestamp_candidates = [c for c in df.columns if "time" in c.lower()]
if not timestamp_candidates:
    st.error("No timestamp column found.")
    st.stop()

timestamp_col = timestamp_candidates[0]

# Find name column (exclude timestamp + email)
name_candidates = [
    c for c in df.columns
    if "name" in c.lower()
    and "email" not in c.lower()
    and c != timestamp_col
]

if not name_candidates:
    st.error("No name column found.")
    st.stop()

name_col = name_candidates[0]

# Clean names
df[name_col] = df[name_col].astype(str).str.strip()
df = df[df[name_col] != ""]
df = df[df[name_col].notna()]

# ===================== IDENTIFY QUESTIONS =====================
# Questions are all columns AFTER name column
name_index = df.columns.get_loc(name_col)
question_columns_raw = df.columns[name_index + 1 : name_index + 1 + 36]

if len(question_columns_raw) < 36:
    st.error("Could not detect all 36 question columns.")
    st.stop()

# Rename to Q1–Q36
question_map = {question_columns_raw[i]: f"Q{i+1}" for i in range(36)}
df = df.rename(columns=question_map)

question_cols = [f"Q{i}" for i in range(1, 37)]

# Keep necessary columns
df = df[[timestamp_col, name_col] + question_cols]
df = df.rename(columns={
    timestamp_col: "Timestamp",
    name_col: "Full Name"
})

# ===================== CLEAN DATA =====================
df["Timestamp"] = pd.to_datetime(df["Timestamp"])

score_map = {
    "YES": 1,
    "Neither YES or NO": 0.5,
    "NO": 0
}

for col in question_cols:
    df[col] = df[col].map(score_map)

# Remove rows where name still invalid
df = df[df["Full Name"].notna()]
df = df[df["Full Name"] != "nan"]

# ===================== CREATE BLOCKS =====================
df = df.sort_values(["Full Name", "Timestamp"])

df["Block Number"] = df.groupby("Full Name").cumcount() + 1
df["Block"] = "Block " + df["Block Number"].astype(str)

# ===================== COACH SELECT =====================
coach_list = sorted(df["Full Name"].unique())

coach = st.selectbox(
    "Select Coach",
    options=coach_list,
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

# ===================== CALCULATIONS =====================
def calculate_group_totals(row):
    return [
        round(row[question_cols[i:i+4]].sum(), 2)
        for i in range(0, 36, 4)
    ]

def get_group_colour(score):
    if score >= 3.25:
        return "#4CAF50"
    elif score >= 2.51:
        return "#FFD966"
    elif score >= 1.75:
        return "#F4A261"
    else:
        return "#FF6B6B"

# ===================== CEF =====================
st.markdown("---")
st.subheader("CEF Breakdown")

group_totals = calculate_group_totals(person_data)
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
            ">
                <div style="font-size:26px;font-weight:bold;">{score}</div>
                <div style="font-size:12px;">{label}</div>
            </div>
            """,
            unsafe_allow_html=True
        )
