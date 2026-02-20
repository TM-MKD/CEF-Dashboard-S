import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.units import inch
from io import BytesIO
import os


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

SAFEGUARDING_QUESTIONS = [22, 20, 30, 33, 34]

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

# ===================== DATA HELPERS =====================
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


def calculate_group_totals(person_data, question_cols):
    return [
        round(person_data[question_cols[i:i + 4]].sum(), 2)
        for i in range(0, len(question_cols), 4)
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

# ===================== FILE UPLOAD =====================
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

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

# ===================== SELECTIONS =====================
first_block = next(iter(blocks.values()))

coach = st.selectbox(
    "Select Coach",
    options=first_block["Full Name"],
    index=None,
    placeholder="Select a coach"
)

block_selected = st.selectbox(
    "Select Block",
    options=list(blocks.keys()),
    index=None,
    placeholder="Select a block"
)

if coach is None or block_selected is None:
    st.info("Please select a coach and a block to view results.")
    st.stop()

df = blocks[block_selected]
person_data = df[df["Full Name"] == coach].iloc[0]

# ===================== CEF BREAKDOWN =====================
st.markdown("---")
st.subheader("CEF Breakdown")

group_totals = calculate_group_totals(person_data, question_cols)
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

# ===================== ACTION PLAN =====================
st.markdown("---")
st.subheader("Action Plan")

half_scores, zero_scores = [], []

for q_col in question_cols:
    q_num = int(q_col.replace("Q", ""))
    score = person_data[q_col]

    if score == 0.5:
        half_scores.append(f"Q{q_num} – {QUESTION_TEXT[q_num]}")
    elif score == 0:
        zero_scores.append(f"Q{q_num} – {QUESTION_TEXT[q_num]}")

# ---------- DOWNLOAD PDF BUTTON ----------
def generate_pdf():

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesizes.A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=40,
        bottomMargin=30
    )

    elements = []
    styles = getSampleStyleSheet()

    # ==============================
    # COLOUR SCHEME
    # ==============================

    MK_GOLD = colors.HexColor("#C7A600")
    MK_BLACK = colors.HexColor("#000000")
    MK_LIGHT_GREY = colors.HexColor("#F4F4F4")

    # Custom styles
    title_style = styles["Title"]
    title_style.textColor = MK_BLACK

    section_style = styles["Heading2"]
    section_style.textColor = MK_GOLD

    normal_style = styles["Normal"]

    # ==============================
    # HEADER WITH BADGE + TITLE
    # ==============================

    badge = Image("assets/mkdons_badge.png", width=1.2*inch, height=1.2*inch)

    header_title = Paragraph(
        "<b>MK Dons – Coach Evaluation Report</b>",
        title_style
    )

    header_table = Table(
        [[badge, header_title]],
        colWidths=[1.5*inch, 4.5*inch]
    )

    header_table.setStyle(TableStyle([
        ("VALIGN", (0,0), (-1,-1), "MIDDLE"),
        ("BACKGROUND", (0,0), (-1,-1), MK_LIGHT_GREY),
        ("LEFTPADDING", (0,0), (-1,-1), 10),
        ("RIGHTPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING", (0,0), (-1,-1), 10),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
    ]))

    elements.append(header_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph(f"<b>Coach:</b> {coach}", normal_style))
    elements.append(Paragraph(f"<b>Block:</b> {block_selected}", normal_style))
    elements.append(Spacer(1, 20))

    # ==============================
    # CEF SECTION
    # ==============================

    total_cef_score = sum(group_totals)

    elements.append(
        Paragraph(
            f"<b>CEF Breakdown (Total: {total_cef_score}/36)</b>",
            section_style
        )
    )
    elements.append(Spacer(1, 12))

    cef_data = []
    row = []

    for i, (label, score) in enumerate(zip(GROUP_LABELS, group_totals)):
        cell = Paragraph(
            f"<para align='center'><b>{score}</b><br/><font size=7>{label}</font></para>",
            normal_style
        )
        row.append(cell)

        if (i + 1) % 3 == 0:
            cef_data.append(row)
            row = []

    if row:
        cef_data.append(row)

    cef_table = Table(
        cef_data,
        colWidths=[1.8 * inch] * 3,
        rowHeights=1.0 * inch
    )

    style_commands = []

    for r in range(len(cef_data)):
        for c in range(len(cef_data[r])):
            score_index = r * 3 + c
            if score_index < len(group_totals):
                colour = get_group_colour(group_totals[score_index])
                style_commands.append(("BACKGROUND", (c, r), (c, r), colour))
                style_commands.append(("BOX", (c, r), (c, r), 1, colors.white))

    style_commands.append(("VALIGN", (0,0), (-1,-1), "MIDDLE"))
    style_commands.append(("ALIGN", (0,0), (-1,-1), "CENTER"))

    cef_table.setStyle(TableStyle(style_commands))

    elements.append(cef_table)
    elements.append(Spacer(1, 25))

    # ==============================
# SAFEGUARDING SECTION
# ==============================

safeguarding_total = sum(person_data[f"Q{q}"] for q in SAFEGUARDING_QUESTIONS)

elements.append(
    Paragraph(
        f"<b>Safeguarding (Total: {safeguarding_total}/{len(SAFEGUARDING_QUESTIONS)*4})</b>",
        section_style
    )
)
elements.append(Spacer(1, 12))

safe_row = []
attention_needed = []

for q in SAFEGUARDING_QUESTIONS:
    score = person_data[f"Q{q}"]
    question_text = QUESTION_TEXT[q]

    if score <= 2:
        attention_needed.append(f"{question_text} (Score: {score})")

    cell = Paragraph(
        f"""
        <para align='center'>
            <font size=14><b>{score}</b></font><br/>
            <font size=7>{question_text}</font>
        </para>
        """,
        normal_style
    )

    safe_row.append(cell)

safe_table = Table(
    [safe_row],
    colWidths=[1.2 * inch] * len(SAFEGUARDING_QUESTIONS),
    rowHeights=1.2 * inch
)

safe_style = []

for c, q in enumerate(SAFEGUARDING_QUESTIONS):
    score = person_data[f"Q{q}"]
    colour = get_safeguarding_colour(score)

    safe_style.append(("BACKGROUND", (c,0), (c,0), colour))
    safe_style.append(("BOX", (c,0), (c,0), 0.5, colors.white))
    safe_style.append(("LEFTPADDING", (c,0), (c,0), 8))
    safe_style.append(("RIGHTPADDING", (c,0), (c,0), 8))
    safe_style.append(("TOPPADDING", (c,0), (c,0), 8))
    safe_style.append(("BOTTOMPADDING", (c,0), (c,0), 8))

safe_style.append(("VALIGN", (0,0), (-1,-1), "MIDDLE"))
safe_style.append(("ALIGN", (0,0), (-1,-1), "CENTER"))

safe_table.setStyle(TableStyle(safe_style))

elements.append(safe_table)
elements.append(Spacer(1, 25))

    # ==============================
    # ATTENTION NEEDED SECTION
    # ==============================

    if attention_needed:

        elements.append(
            Paragraph("<b>⚠ Attention Needed</b>", section_style)
        )
        elements.append(Spacer(1, 10))

        for item in attention_needed:
            elements.append(Paragraph(f"• {item}", normal_style))
            elements.append(Spacer(1, 6))

    else:
        elements.append(
            Paragraph("<b>No safeguarding concerns identified.</b>", normal_style)
        )

    doc.build(elements)
    buffer.seek(0)
    return buffer


pdf_buffer = generate_pdf()

st.download_button(
    label="Download Action Plan",
    data=pdf_buffer,
    file_name=f"{coach}_{block_selected}_Action_Plan.pdf",
    mime="application/pdf"
)

# ---------- DISPLAY ACTION PLAN ON SCREEN ----------
c1, c2 = st.columns(2)

with c1:
    st.subheader("Scored 0.5 (Developing)")
    for item in half_scores:
        st.write("•", item)

with c2:
    st.subheader("Scored 0 (Needs Attention)")
    for item in zero_scores:
        st.write("•", item)

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
    title=f"{coach} — {block_selected}",
    yaxis=dict(range=[0, 1]),
    xaxis_title="Questions",
    yaxis_title="Score"
)

st.plotly_chart(fig, use_container_width=True)

# ===================== BLOCK COMPARISON =====================
st.markdown("---")
st.subheader("Block Comparison")

# --- Side by side block selectors ---
col_left, col_right = st.columns(2)

with col_left:
    block_1 = st.selectbox(
        "Select first block",
        options=list(blocks.keys()),
        index=None,
        placeholder="Select a block",
        key="b1"
    )

with col_right:
    block_2 = st.selectbox(
        "Select second block",
        options=list(blocks.keys()),
        index=None,
        placeholder="Select a block",
        key="b2"
    )

# --- Side by side grids ---
if block_1 and coach in blocks[block_1]["Full Name"].values:
    pdata1 = blocks[block_1][blocks[block_1]["Full Name"] == coach].iloc[0]
    group_scores_1 = calculate_group_totals(pdata1, question_cols)

    with col_left:
        st.markdown(f"### {block_1}")
        make_group_grid(group_scores_1)

if block_2 and coach in blocks[block_2]["Full Name"].values:
    pdata2 = blocks[block_2][blocks[block_2]["Full Name"] == coach].iloc[0]
    group_scores_2 = calculate_group_totals(pdata2, question_cols)

    with col_right:
        st.markdown(f"### {block_2}")
        make_group_grid(group_scores_2)

# ===================== FULL CEF BREAKDOWN TABLE =====================
st.markdown("---")
st.subheader("CEF Breakdown by Block")

comparison_data = {}

for block_name, block_df in blocks.items():
    coach_rows = block_df[block_df["Full Name"] == coach]

    if not coach_rows.empty:
        pdata = coach_rows.iloc[0]
        group_scores = calculate_group_totals(pdata, question_cols)
        comparison_data[block_name] = group_scores

if comparison_data:

    comparison_df = pd.DataFrame(
        comparison_data,
        index=GROUP_LABELS
    )

    ordered_blocks = sorted(comparison_df.columns)
    comparison_df = comparison_df[ordered_blocks].round(1)

    # Build styled HTML manually
    html = "<table style='width:100%; border-collapse:collapse; text-align:center;'>"
    
    # Header
    html += "<tr><th style='padding:8px;'>Group</th>"
    for col in ordered_blocks:
        html += f"<th style='padding:8px;'>{col}</th>"
    html += "</tr>"

    # Rows
    for row_idx, row_name in enumerate(comparison_df.index):
        html += f"<tr><td style='padding:8px; font-weight:bold;'>{row_name}</td>"

        for col_idx, col in enumerate(ordered_blocks):
            val = comparison_df.iloc[row_idx, col_idx]

            style = "padding:8px;"

            if col_idx > 0:
                prev_val = comparison_df.iloc[row_idx, col_idx - 1]

                if val > prev_val:
                    style += "background-color:#4CAF50; color:white;"
                elif val < prev_val:
                    style += "background-color:#FF6B6B; color:white;"

            html += f"<td style='{style}'>{val}</td>"

        html += "</tr>"

    html += "</table>"

    st.markdown(html, unsafe_allow_html=True)

else:
    st.info("No data available for this coach.")
