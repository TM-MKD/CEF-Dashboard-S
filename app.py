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

    st.dataframe(comparison_df, use_container_width=True)

else:
    st.info("No data available for this coach.")
