import streamlit as st
import pandas as pd
import plotly.express as px
from io import BytesIO

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch

# ===================== PAGE CONFIG =====================
st.set_page_config(layout="wide")
st.title("Coach CEF Dashboard")

# ===================== FILE UPLOAD =====================
uploaded_file = st.file_uploader("Upload CEF CSV", type=["csv"])

if uploaded_file:

    df = pd.read_csv(uploaded_file)

    df["Full Name"] = df["Full Name"].astype(str)
    df = df.dropna(subset=["Full Name"])

    df["Submission Date"] = pd.to_datetime(df["Submission Date"], errors="coerce")
    df = df.sort_values(["Full Name", "Submission Date"])

    # Assign Block Number
    df["Block"] = df.groupby("Full Name").cumcount() + 1

    # ===================== GROUP SETUP =====================
    question_cols = df.columns[6:]

    GROUPS = {
        "Leadership": question_cols[0:5],
        "Environment": question_cols[5:10],
        "Communication": question_cols[10:15],
        "Planning": question_cols[15:20],
        "Reflection": question_cols[20:25],
    }

    GROUP_LABELS = list(GROUPS.keys())

    def calculate_group_totals(row):
        scores = {}
        for group, cols in GROUPS.items():
            scores[group] = round(row[cols].mean(), 2)
        return scores

    # ===================== COACH SELECT =====================
    coaches = sorted(df["Full Name"].unique())
    coach = st.selectbox("Select Coach", coaches)

    coach_df = df[df["Full Name"] == coach]

    blocks = {}
    for block_num in sorted(coach_df["Block"].unique()):
        blocks[f"Block {block_num}"] = coach_df[coach_df["Block"] == block_num]

    # ===================== COMPARISON DATA =====================
    comparison_data = {}

    for block_name, block_df in blocks.items():
        pdata = block_df.iloc[0]
        comparison_data[block_name] = calculate_group_totals(pdata)

    if comparison_data:

        comparison_df = pd.DataFrame(
            comparison_data,
            index=GROUP_LABELS
        )

        ordered_blocks = sorted(comparison_df.columns)
        comparison_df = comparison_df[ordered_blocks].round(1)

        # ===================== GRAPH =====================
        st.subheader("CEF Progression")

        category = st.selectbox("Select CEF Category", GROUP_LABELS)

        graph_df = pd.DataFrame({
            "Block": ordered_blocks,
            "Score": comparison_df.loc[category]
        })

        fig = px.line(
            graph_df,
            x="Block",
            y="Score",
            markers=True,
            range_y=[0, 4]
        )

        st.plotly_chart(fig, use_container_width=True)

        # ===================== TABLE =====================
        st.subheader("CEF Breakdown by Block")

        html = "<table style='width:100%; border-collapse:collapse; text-align:center;'>"
        html += "<tr><th style='padding:8px;'>Group</th>"

        for col in ordered_blocks:
            html += f"<th style='padding:8px;'>{col}</th>"
        html += "</tr>"

        for row_idx, row_name in enumerate(comparison_df.index):
            html += f"<tr><td style='padding:8px; font-weight:bold;'>{row_name}</td>"

            for col_idx, col in enumerate(ordered_blocks):
                val = comparison_df.iloc[row_idx, col_idx]
                display_val = f"{val:.1f}"
                style = "padding:8px;"

                if col_idx > 0:
                    prev_val = comparison_df.iloc[row_idx, col_idx - 1]

                    if val > prev_val:
                        style += "background-color:#4CAF50; color:white;"
                        display_val += " ↑"
                    elif val < prev_val:
                        style += "background-color:#FF6B6B; color:white;"
                        display_val += " ↓"

                html += f"<td style='{style}'>{display_val}</td>"

            html += "</tr>"

        html += "</table>"

        st.markdown(html, unsafe_allow_html=True)

        # ===================== TOTAL SCORE =====================
        latest_block = ordered_blocks[-1]
        latest_scores = comparison_df[latest_block]
        total_cef_score = round(latest_scores.sum(), 1)

        st.markdown(f"### Total CEF Score (Latest Block): {total_cef_score}")

        # ===================== PDF GENERATION =====================
        buffer = BytesIO()
        doc = SimpleDocTemplate(buffer)
        elements = []
        styles = getSampleStyleSheet()

        elements.append(Paragraph(f"<b>Coach:</b> {coach}", styles["Heading2"]))
        elements.append(Spacer(1, 0.3 * inch))

        elements.append(Paragraph(
            f"<b>Total CEF Score:</b> {total_cef_score}",
            styles["Heading3"]
        ))
        elements.append(Spacer(1, 0.2 * inch))

        # ===== COLOUR GRID =====
        table_data = []
        header = ["CEF Group"] + GROUP_LABELS
        table_data.append(header)

        score_row = ["Score"] + [round(v, 1) for v in latest_scores]
        table_data.append(score_row)

        pdf_table = Table(table_data, hAlign="CENTER")

        table_style = TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ])

        for col_index, score in enumerate(score_row[1:], start=1):

            if score >= 3:
                bg = colors.HexColor("#4CAF50")
            elif score >= 2:
                bg = colors.HexColor("#FFC107")
            else:
                bg = colors.HexColor("#FF6B6B")

            table_style.add("BACKGROUND", (col_index, 1), (col_index, 1), bg)
            table_style.add("TEXTCOLOR", (col_index, 1), (col_index, 1), colors.white)

        pdf_table.setStyle(table_style)

        elements.append(pdf_table)

        doc.build(elements)
        buffer.seek(0)

        st.download_button(
            "Download Action Plan PDF",
            data=buffer,
            file_name=f"{coach}_CEF_Report.pdf",
            mime="application/pdf"
        )
