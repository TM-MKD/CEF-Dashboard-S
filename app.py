import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import io

# ===================== PAGE CONFIG =====================
st.set_page_config(
    page_title="MK Dons – Coach Evaluation Framework",
    layout="wide"
)

# ===================== GLOBAL STYLING =====================
st.markdown(
    """
    <style>
        body {
            background-color: #eeeeee;
        }

        .block-container {
            padding-top: 2rem;
        }

        .mk-card {
            background-color: white;
            border-radius: 10px;
            padding: 18px;
            text-align: center;
            margin-bottom: 12px;
            border-top: 4px solid #c9a23f;
            box-shadow: 0 4px 10px rgba(0,0,0,0.12);
        }

        .mk-section {
            background-color: white;
            padding: 20px;
            border-radius: 12px;
            border-left: 6px solid #c9a23f;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            margin-bottom: 25px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# ===================== HEADER =====================
h1, h2 = st.columns([1, 6])

with h1:
    try:
        st.image("assets/mkdons_badge.png", width=85)
    except:
        pass

with h2:
    st.markdown(
        "<h1 style='margin-bottom:0;color:black;'>MK Dons – Coach Evaluation Framework</h1>",
        unsafe_allow_html=True
    )

st.markdown("<hr style='border:1px solid #c9a23f;'>", unsafe_allow_html=True)

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

# ===================== HELPERS =====================
def get_colour(score):
    if score >= 3.25:
        return "#2e7d32"   # deep green
    elif score >= 2.51:
        return "#c9a23f"   # MK gold
    elif score >= 1.75:
        return "#ef9f1a"
    else:
        return "#c62828"


def split_blocks(raw_df):
    block_dfs = []
    header_rows = raw_df[raw_df.apply(
        lambda row: row.astype(str).str.strip().str.lower().eq("full name").any(),
        axis=1
    )].index.tolist()

    for i, start in enumerate(header_rows):
        end = header_rows[i + 1] if i + 1 < len(header_rows) else len(raw_df)
        block = raw_df.iloc[start:end].copy()
        block.columns = block.iloc[0].astype(str).str.strip()
        block = block[1:]
        block = block.dropna(how="all")
        block_dfs.append(block.reset_index(drop=True))

    return block_dfs


def render_group_cards(person_data, question_cols):
    group_totals = [
        round(person_data[question_cols[i:i + 4]].sum(), 2)
        for i in range(0, len(question_cols), 4)
    ]

    cols = st.columns(3)
    for idx, (label, score) in enumerate(zip(GROUP_LABELS, group_totals)):
        with cols[idx % 3]:
            st.markdown(
                f"""
                <div class="mk-card" style="background-color:{get_colour(score)};">
                    <div style="font-size:26px;font-weight:700;color:black;">{score}</div>
                    <div style="font-size:12px;color:black;">{label}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

# ===================== FILE UPLOAD =====================
st.markdown('<div class="mk-section">', unsafe_allow_html=True)
uploaded_file = st.file_uploader(
    "Upload Excel file",
    type=["xlsx"]
)
st.markdown('</div>', unsafe_allow_html=True)

if uploaded_file is None:
    st.info("Please upload an Excel file to begin.")
    st.stop()

# ===================== PARSE FILE =====================
raw_df = pd.read_excel(uploaded_file, header=None)
block_list = split_blocks(raw_df)

score_map = {"YES": 1, "Neither YES or NO": 0.5, "NO": 0}
blocks = {}

for i, block in enumerate(block_list, start=1):
    block.columns = block.columns.str.strip()
    question_cols = [c for c in block.columns if str(c).startswith("Q")]

    for col in question_cols:
        block[col] = block[col].map(score_map)

    blocks[f"Block {i}"] = block

first_block = next(iter(blocks.values()))

# ===================== SELECTIONS =====================
st.markdown('<div class="mk-section">', unsafe_allow_html=True)

coach = st.selectbox(
    "Select a coach",
    options=first_block["Full Name"],
    index=None,
    placeholder="Select a coach"
)

block_selected = st.selectbox(
    "Select a block",
    options=list(blocks.keys()),
    index=None,
    placeholder="Select a block"
)

st.markdown('</div>', unsafe_allow_html=True)

if coach is None or block_selected is None:
    st.warning("Please select both a coach and a block to view results.")
    st.stop()

df = blocks[block_selected]
person_data = df[df["Full Name"] == coach].iloc[0]

# ===================== GROUP SCORES =====================
st.markdown('<div class="mk-section">', unsafe_allow_html=True)
st.subheader("Group Scores")
render_group_cards(person_data, question_cols)
st.markdown('</div>', unsafe_allow_html=True)

# ===================== QUESTION CHART =====================
scores = person_data[question_cols].values
bar_colors = [
    "#2e7d32" if s == 1 else "#c9a23f" if s == 0.5 else "#c62828"
    for s in scores
]

fig = go.Figure()
fig.add_trace(go.Bar(
    x=question_cols,
    y=scores,
    marker_color=bar_colors
))
fig.update_layout(
    title=f"{coach} — {block_selected}",
    yaxis=dict(range=[0, 1]),
    xaxis_title="Questions",
    yaxis_title="Score",
    plot_bgcolor="white",
    paper_bgcolor="white"
)

st.markdown('<div class="mk-section">', unsafe_allow_html=True)
st.plotly_chart(fig, use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# ===================== DEVELOPMENT LISTS =====================
half_scores, zero_scores = [], []

for q_col in question_cols:
    q_num = int(q_col.replace("Q", ""))
    score = person_data[q_col]

    if score == 0.5:
        half_scores.append(f"Q{q_num} – {QUESTION_TEXT[q_num]}")
    elif score == 0:
        zero_scores.append(f"Q{q_num} – {QUESTION_TEXT[q_num]}")

st.markdown('<div class="mk-section">', unsafe_allow_html=True)
c1, c2 = st.columns(2)

with c1:
    st.subheader("Scored 0.5 (Developing)")
    for item in half_scores:
        st.write("•", item)

with c2:
    st.subheader("Scored 0 (Needs Attention)")
    for item in zero_scores:
        st.write("•", item)

st.markdown('</div>', unsafe_allow_html=True)

# ===================== BLOCK COMPARISON =====================
st.markdown('<div class="mk-section">', unsafe_allow_html=True)
st.subheader("Block Comparison")

b1, b2 = st.columns(2)

with b1:
    block_1 = st.selectbox(
        "Select first block",
        options=list(blocks.keys()),
        index=None,
        placeholder="Select a block",
        key="b1"
    )
    if block_1:
        pdata1 = blocks[block_1][blocks[block_1]["Full Name"] == coach].iloc[0]
        render_group_cards(pdata1, question_cols)

with b2:
    block_2 = st.selectbox(
        "Select second block",
        options=list(blocks.keys()),
        index=None,
        placeholder="Select a block",
        key="b2"
    )
    if block_2:
        pdata2 = blocks[block_2][blocks[block_2]["Full Name"] == coach].iloc[0]
        render_group_cards(pdata2, question_cols)

st.markdown('</div>', unsafe_allow_html=True)
