import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import pagesizes
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


# ===================== FILE UPLOAD =====================
uploaded_file = st.file_uploader("Upload Excel file", type=["xlsx"])

if uploaded_file is None:
    st.info("Please upload an Excel file to begin.")
    st.stop()

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

group_totals = calculate_group_totals(person_data, question_cols)


# ===================== PDF GENERATOR =====================
def generate_pdf():

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesizes.A4,
        rightMargin=30,
        leftMargin=30,
        topMargin=30,
        bottomMargin=30
    )

    elements = []
    styles = getSampleStyleSheet()

    elements.append(Paragraph("<b>MK Dons – Coach Evaluation Report</b>", styles["Title"]))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"<b>Coach:</b> {coach}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Block:</b> {block_selected}", styles["Normal"]))
    elements.append(Spacer(1, 20))

    # ===== CEF GRID =====
    elements.append(Paragraph("<b>CEF Breakdown</b>", styles["Heading2"]))
    elements.append(Spacer(1, 12))

    cef_data = []
    row = []

    for i, (label, score) in enumerate(zip(GROUP_LABELS, group_totals)):
        cell = Paragraph(
            f"<para align='center'><b>{score}</b><br/><font size=8>{label}</font></para>",
            styles["Normal"]
        )
        row.append(cell)

        if (i + 1) % 3 == 0:
            cef_data.append(row)
            row = []

    if row:
        cef_data.append(row)

    cef_table = Table(cef_data, colWidths=[2.2 * inch] * 3, rowHeights=1.2 * inch)

    style_commands = []
    for r in range(len(cef_data)):
        for c in range(len(cef_data[r])):
            score_index = r * 3 + c
            if score_index < len(group_totals):
                colour = get_group_colour(group_totals[score_index])
                style_commands.append(("BACKGROUND", (c, r), (c, r), colour))
                style_commands.append(("BOX", (c, r), (c, r), 1, colors.white))

    style_commands.append(("VALIGN", (0, 0), (-1, -1), "MIDDLE"))
    cef_table.setStyle(TableStyle(style_commands))

    elements.append(cef_table)
    elements.append(Spacer(1, 20))

    # ===== SAFEGUARDING GRID =====
    elements.append(Paragraph("<b>Safeguarding</b>", styles["Heading2"]))
    elements.append(Spacer(1, 12))

    safe_row = []

    for q in SAFEGUARDING_QUESTIONS:
        score = person_data[f"Q{q}"]
        cell = Paragraph(
            f"<para align='center'><b>Q{q}</b><br/><font size=7>{QUESTION_TEXT[q]}</font></para>",
            styles["Normal"]
        )
        safe_row.append(cell)

    safe_table = Table([safe_row], colWidths=[1.1 * inch] * 5, rowHeights=1.2 * inch)

    safe_style = []
    for c, q in enumerate(SAFEGUARDING_QUESTIONS):
        score = person_data[f"Q{q}"]
        colour = get_safeguarding_colour(score)
        safe_style.append(("BACKGROUND", (c, 0), (c, 0), colour))
        safe_style.append(("BOX", (c, 0), (c, 0), 1, colors.white))

    safe_style.append(("VALIGN", (0, 0), (-1, -1), "MIDDLE"))
    safe_table.setStyle(TableStyle(safe_style))

    elements.append(safe_table)

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
