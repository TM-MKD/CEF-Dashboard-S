import streamlit as st

from auth import enforce_email_login, render_logout_button
import pandas as pd
from reportlab.lib import colors
from io import BytesIO

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="CEF",
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
        "<h1 style='margin-bottom:0;'>CEF – Block Average View</h1>",
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

score_map = {
    "YES": 1,
    "Neither YES or NO": 0.5,
    "NO": 0
}

# ===================== HELPERS =====================
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
    if score >= 0.8:
        return "#4CAF50"
    elif score >= 0.5:
        return "#F4A261"
    else:
        return "#FF6B6B"


def calculate_average_group_totals(block_df, question_cols):
    averages = []

    for i in range(0, len(question_cols), 4):
        cols = question_cols[i:i+4]

        group_scores = block_df[cols].apply(
            pd.to_numeric, errors="coerce"
        )

        row_totals = group_scores.sum(axis=1)

        averages.append(round(row_totals.mean(), 2))

    return averages


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

# ===================== FILE CHECK =====================
if "uploaded_excel_bytes" not in st.session_state:
    st.info("Please upload an Excel file on the Home page to begin.")
    st.stop()

# ===================== LOAD DATA =====================
df = pd.read_excel(BytesIO(st.session_state["uploaded_excel_bytes"]))
df.columns = df.columns.str.strip()

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

# ===================== BLOCK SELECTION =====================
block_selected = st.selectbox(
    "Select Block",
    options=list(blocks.keys()),
    index=None
)

if block_selected is None:
    st.info("Please select a block.")
    st.stop()

block_df = blocks[block_selected]
all_coaches_in_block = sorted(block_df["Full Name"].dropna().unique().tolist())

# ===================== COACHES IN BLOCK =====================
st.markdown("---")
st.subheader("Coaches in Selected Block")

selected_coaches = st.multiselect(
    "Choose which coaches to include",
    options=all_coaches_in_block,
    default=all_coaches_in_block
)

if not selected_coaches:
    st.warning("Please select at least one coach to display block averages.")
    st.stop()

filtered_block_df = block_df[block_df["Full Name"].isin(selected_coaches)]

# ===================== COACH SCORE BAR CHART =====================
st.markdown("---")
st.subheader("Coach Scores Overview")

import plotly.graph_objects as go

coach_scores = []

for coach in selected_coaches:
    coach_df = filtered_block_df[filtered_block_df["Full Name"] == coach]
    
    totals = []
    for i in range(0, len(question_cols), 4):
        cols = question_cols[i:i+4]
        group_scores = coach_df[cols].apply(pd.to_numeric, errors="coerce")
        totals.append(group_scores.sum(axis=1).sum())
    
    coach_scores.append({"name": coach, "score": round(sum(totals), 2)})

coach_scores.sort(key=lambda x: x["score"], reverse=True)

bar_names = [c["name"] for c in coach_scores]
bar_values = [c["score"] for c in coach_scores]

def get_bar_colour(score):
    if score >= 29:
        return "#4CAF50"
    elif score >= 22:
        return "#FFD966"
    elif score >= 14:
        return "#F4A261"
    else:
        return "#FF6B6B"

bar_colours = [get_bar_colour(s) for s in bar_values]

fig = go.Figure(go.Bar(
    x=bar_names,
    y=bar_values,
    marker_color=bar_colours,
    text=[f"{s}" for s in bar_values],
    textposition="inside",
    hovertemplate="%{x}: %{y} / 36<extra></extra>"
))

fig.update_layout(
    yaxis=dict(range=[0, 36], title="Score / 36"),
    xaxis=dict(title=""),
    plot_bgcolor="rgba(0,0,0,0)",
    paper_bgcolor="rgba(0,0,0,0)",
    margin=dict(t=20, b=20, l=40, r=20),
    height=380,
    font=dict(size=13)
)

st.plotly_chart(fig, use_container_width=True)

# ===================== CEF BREAKDOWN =====================
st.markdown("---")
st.subheader("Average CEF Breakdown")

group_totals = calculate_average_group_totals(filtered_block_df, question_cols)
cef_total = round(sum(group_totals), 2)

st.markdown(f"### Average Score: **{cef_total} / 36**")

make_group_grid(group_totals)

# ===================== SAFEGUARDING =====================
st.markdown("---")
st.subheader("Average Safeguarding")

safe_scores = []

for q in SAFEGUARDING_QUESTIONS:
    avg_score = round(pd.to_numeric(filtered_block_df[q], errors="coerce").mean(), 2)
    safe_scores.append(avg_score)

safe_total = round(sum(safe_scores), 2)

st.markdown(f"### Average Score: **{safe_total} / 5**")

cols = st.columns(5)

for col, q, score in zip(cols, SAFEGUARDING_QUESTIONS, safe_scores):
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

# ===================== ACTION PLAN =====================
st.markdown("---")
st.subheader("Team Development Areas")

improve = []
attention = []

for i, q_col in enumerate(question_cols, start=1):
    avg_score = round(
        pd.to_numeric(filtered_block_df[q_col], errors="coerce").mean(),
        2
    )

    if avg_score <= 0.5:
        attention.append(f"Q{i} – {q_col} ({avg_score})")

    elif avg_score <= 0.75:
        improve.append(f"Q{i} – {q_col} ({avg_score})")

# Create two side-by-side columns
col1, col2 = st.columns(2)

with col1:
    if improve:
        st.markdown("#### Consider Improving")
        for item in improve:
            st.write(item)
    else:
        st.write("No development areas currently identified.")

with col2:
    if attention:
        st.markdown("#### Immediate Attention Needed")
        for item in attention:
            st.write(item)
    else:
        st.write("No immediate attention areas currently identified.")
