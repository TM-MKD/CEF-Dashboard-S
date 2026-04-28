import streamlit as st

from auth import enforce_email_login, render_logout_button
import pandas as pd
import plotly.graph_objects as go

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib import pagesizes
from reportlab.lib.units import inch
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
        "<h1 style='margin-bottom:0;'>CEF - Individual Coach View</h1>",
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

def calculate_group_totals(person_data, question_cols):

    totals = []

    for i in range(0, len(question_cols), 4):
        cols = question_cols[i:i+4]

        scores = pd.to_numeric(person_data[cols], errors="coerce")

        totals.append(round(scores.sum(), 2))

    return totals


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

# ===================== SELECTIONS =====================

first_block = next(iter(blocks.values()))

coach = st.selectbox(
    "Select Coach",
    options=first_block["Full Name"],
    index=None
)
    
block_selected = st.selectbox(
    "Select Block",
    options=list(blocks.keys()),
    index=None
)

if coach is None or block_selected is None:
    st.info("Please select a coach and a block to view results.")
    st.stop()

df = blocks[block_selected]

coach_data = df[df["Full Name"] == coach]

if coach_data.empty:
    st.markdown(
        f"""
        <div style="
            background-color:#F8F9FA;
            border:2px solid #E0E0E0;
            padding:20px;
            border-radius:12px;
            text-align:center;
            margin-top:20px;
            box-shadow:0 4px 8px rgba(0,0,0,0.08);
        ">
            <div style="font-size:28px;">⚽</div>
            <div style="font-size:18px; font-weight:600; margin-top:8px;">
                No data from {block_selected} for {coach}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.stop()

person_data = coach_data.iloc[0]

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

safeguarding_scores = [
    pd.to_numeric(person_data[q], errors="coerce")
    for q in SAFEGUARDING_QUESTIONS
]

safeguarding_total = sum(safeguarding_scores)

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

# ===================== ACTION PLAN Section =====================

st.markdown("---")
st.subheader("Action Plan")

def generate_pdf():
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=pagesizes.A4,
        rightMargin=20,
        leftMargin=20,
        topMargin=0,
        bottomMargin=20
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
    badge = Image(
        "assets/mkdons_badge.png",
        width=1.0 * inch,
        height=1.0 * inch
    )

    header_title = Paragraph(
        "<b>MK Dons – Coach Evaluation Report</b>",
        title_style
    )

    header_table = Table(
        [[badge, header_title]],
        colWidths=[1.4 * inch, 8.0 * inch]
    )

    header_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("BACKGROUND", (0, 0), (-1, -1), MK_LIGHT_GREY),
        ("LEFTPADDING", (0, 0), (-1, -1), 60),
        ("RIGHTPADDING", (0, 0), (-1, -1), 40),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))

    elements.append(header_table)
    elements.append(Spacer(1, 15))

    # ==============================
    # COACH & BLOCK INFO
    # ==============================
    elements.append(Paragraph(f"<b>Coach:</b> {coach}", normal_style))
    elements.append(Paragraph(f"<b>Block:</b> {block_selected}", normal_style))
    elements.append(Spacer(1, 12))

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
    elements.append(Spacer(1, 10))

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
        while len(row) < 3:
            row.append("")
        cef_data.append(row)

    cef_table = Table(
        cef_data,
        colWidths=[2.6 * inch] * 3,
        rowHeights=0.8 * inch
    )

    style_commands = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]

    for r in range(len(cef_data)):
        for c in range(3):
            score_index = r * 3 + c
            if score_index < len(group_totals):
                colour = get_group_colour(group_totals[score_index])
                style_commands.append(
                    ("BACKGROUND", (c, r), (c, r), colour)
                )
                style_commands.append(
                    ("BOX", (c, r), (c, r), 1, colors.white)
                )

    cef_table.setStyle(TableStyle(style_commands))
    elements.append(cef_table)
    elements.append(Spacer(1, 10))

    # ==============================
    # SAFEGUARDING SECTION
    # ==============================
    safeguarding_total = sum(
        pd.to_numeric(person_data[q], errors="coerce")
        for q in SAFEGUARDING_QUESTIONS
    )

    elements.append(
        Paragraph(
            f"<b>Safeguarding (Total: {safeguarding_total}/5)</b>",
            section_style
        )
    )
    elements.append(Spacer(1, 10))

    safe_row = []

    for q in SAFEGUARDING_QUESTIONS:
        score = pd.to_numeric(person_data[q], errors="coerce")

        cell = Paragraph(
            f"<para align='center'><b>{score}</b><br/><font size=6>{q}</font></para>",
            normal_style
        )
        safe_row.append(cell)

    safe_table = Table(
        [safe_row],
        colWidths=[1.56 * inch] * len(SAFEGUARDING_QUESTIONS),
        rowHeights=0.8 * inch
    )

    safe_style = [
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
    ]

    for c, q in enumerate(SAFEGUARDING_QUESTIONS):
        score = pd.to_numeric(person_data[q], errors="coerce")
        colour = get_safeguarding_colour(score)

        safe_style.append(
            ("BACKGROUND", (c, 0), (c, 0), colour)
        )
        safe_style.append(
            ("BOX", (c, 0), (c, 0), 1, colors.white)
        )

    safe_table.setStyle(TableStyle(safe_style))
    elements.append(safe_table)
    elements.append(Spacer(1, 12))

    # ==============================
    # ACTION PLAN SECTION
    # ==============================
    elements.append(Paragraph("<b>Action Plan</b>", section_style))
    elements.append(Spacer(1, 8))

    pdf_half_scores = []
    pdf_zero_scores = []

    for i, q_col in enumerate(question_cols, start=1):
        score = pd.to_numeric(person_data[q_col], errors="coerce")

        if score == 0.5:
            pdf_half_scores.append(f"Q{i} – {q_col}")

        elif score == 0:
            pdf_zero_scores.append(f"Q{i} – {q_col}")

    # Smaller styles
    action_heading_orange = ParagraphStyle(
        "ActionHeadingOrange",
        parent=normal_style,
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#F4A261")
    )

    action_heading_red = ParagraphStyle(
        "ActionHeadingRed",
        parent=normal_style,
        fontSize=9,
        leading=11,
        textColor=colors.HexColor("#FF6B6B")
    )

    action_text_style = ParagraphStyle(
        "ActionTextSmall",
        parent=normal_style,
        fontSize=8,
        leading=11
    )

    # Left column
    left_content = [
        Paragraph("<b>Consider Improving</b>", action_heading_orange),
        Spacer(1, 6)
    ]

    if pdf_half_scores:
        for item in pdf_half_scores:
            left_content.append(
                Paragraph(f"• {item}", action_text_style)
            )
            left_content.append(Spacer(1, 4))
    else:
        left_content.append(
            Paragraph(
                "No areas currently scored at 0.5.",
                action_text_style
            )
        )

    # Right column
    right_content = [
        Paragraph("<b>Immediate Attention Needed</b>", action_heading_red),
        Spacer(1, 6)
    ]

    if pdf_zero_scores:
        for item in pdf_zero_scores:
            right_content.append(
                Paragraph(f"• {item}", action_text_style)
            )
            right_content.append(Spacer(1, 4))
    else:
        right_content.append(
            Paragraph(
                "No areas requiring immediate attention.",
                action_text_style
            )
        )

    action_table = Table(
        [[left_content, right_content]],
        colWidths=[3.8 * inch, 3.8 * inch]
    )

    action_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (0, 0), colors.whitesmoke),
        ("BACKGROUND", (1, 0), (1, 0), colors.whitesmoke),
        ("BOX", (0, 0), (0, 0), 1, colors.lightgrey),
        ("BOX", (1, 0), (1, 0), 1, colors.lightgrey),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))

    elements.append(action_table)
    elements.append(Spacer(1, 12))

    # ==============================
    # BUILD PDF
    # ==============================
    doc.build(elements)
    buffer.seek(0)

    return buffer
# ===================== PDF DOWNLOAD BUTTON =====================

pdf_buffer = generate_pdf()

st.download_button(
    label="Download PDF Report",
    data=pdf_buffer,
    file_name=f"{coach}_{block_selected}_Action_Plan.pdf",
    mime="application/pdf"
)

# ===================== ACTION PLAN On Screen =====================

half_scores, zero_scores = [], []

for i, q_col in enumerate(question_cols, start=1):
    score = pd.to_numeric(person_data[q_col], errors="coerce")

    if score == 0.5:
        half_scores.append(f"Q{i} – {q_col}")

    elif score == 0:
        zero_scores.append(f"Q{i} – {q_col}")

# Create two side-by-side columns
col1, col2 = st.columns(2)

with col1:
    if half_scores:
        st.markdown("#### Consider Improving")
        for item in half_scores:
            st.write(item)

with col2:
    if zero_scores:
        st.markdown("#### Immediate Attention Needed")
        for item in zero_scores:
            st.write(item)

# ===================== FULL CEF BREAKDOWN TABLE =====================

st.markdown("---")
st.subheader("CEF Comparison by Block")

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
