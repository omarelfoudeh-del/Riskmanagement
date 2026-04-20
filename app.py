# ----------------------------
# Game Progress table starting from Day 0
# ----------------------------
st.subheader("Game Progress")

day0_table_row = pd.DataFrame([{
    "Day": 0,
    "Position Client": 0,
    "Position Hedge": 0,
    "Position Company": 0,
    "Open Price": np.nan,
    "Market Price": base_df.loc[0, "Open Price"],
    "Profit Company": 0
}])

history_df = st.session_state.game_df.copy()

if not history_df.empty:
    history_df = history_df[[
        "Day",
        "Position Client",
        "Position Hedge",
        "Position Company",
        "Open Price",
        "Market Price",
        "Profit Company"
    ]].copy()
else:
    history_df = pd.DataFrame(columns=[
        "Day",
        "Position Client",
        "Position Hedge",
        "Position Company",
        "Open Price",
        "Market Price",
        "Profit Company"
    ])

history_df = pd.concat([day0_table_row, history_df], ignore_index=True)

if not game_finished:
    preview_row = pd.DataFrame([{
        "Day": int(base_df.loc[st.session_state.current_day_index, "Day"]),
        "Position Client": int(base_df.loc[st.session_state.current_day_index, "Position Client"]),
        "Position Hedge": np.nan,
        "Position Company": np.nan,
        "Open Price": float(base_df.loc[st.session_state.current_day_index, "Open Price"]),
        "Market Price": np.nan,
        "Profit Company": np.nan
    }])

    display_progress_df = pd.concat([history_df, preview_row], ignore_index=True)
else:
    display_progress_df = history_df.copy()

def format_signed_int_or_blank(x):
    return "" if pd.isna(x) else f"{int(x):+,}"

def format_int_or_blank(x):
    return "" if pd.isna(x) else f"{int(x):,}"

def format_price_or_blank(x):
    return "" if pd.isna(x) else f"{float(x):.4f}"

formatted_df = display_progress_df.copy()
formatted_df["Day"] = formatted_df["Day"].map(lambda x: int(x))
formatted_df["Position Client"] = formatted_df["Position Client"].map(format_signed_int_or_blank)
formatted_df["Position Hedge"] = formatted_df["Position Hedge"].map(format_signed_int_or_blank)
formatted_df["Position Company"] = formatted_df["Position Company"].map(format_signed_int_or_blank)
formatted_df["Open Price"] = formatted_df["Open Price"].map(format_price_or_blank)
formatted_df["Market Price"] = formatted_df["Market Price"].map(format_price_or_blank)
formatted_df["Profit Company"] = formatted_df["Profit Company"].map(format_int_or_blank)

st.dataframe(
    formatted_df,
    use_container_width=True,
    hide_index=True
)
