import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Market Risk Management Simulator", layout="centered")

contract_size = 100000

base_df = pd.DataFrame({
    "Day": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "Position Client": [10, 20, 30, 40, 40, 30, 20, 10, 0, 0],
    "Open Price": [1.5100, 1.5050, 1.5000, 1.4950, 1.4900, 1.4900, 1.4950, 1.5000, 1.5050, 1.5100],
    "Market Price": [1.5050, 1.5000, 1.4950, 1.4900, 1.4900, 1.4950, 1.5000, 1.5050, 1.5100, 1.5050]
})

game_columns = [
    "Day",
    "Position Client",
    "Position Hedge",
    "Position Company",
    "Open Price",
    "Market Price",
    "Profit Client",
    "Profit Hedge",
    "Profit Company",
    "Cumulative Profit Company"
]

# --------------------------------------------------
# Session state
# --------------------------------------------------
if "page" not in st.session_state:
    st.session_state.page = "intro"

if "current_day_index" not in st.session_state:
    st.session_state.current_day_index = 0

if "cumulative_profit_company" not in st.session_state:
    st.session_state.cumulative_profit_company = 0

if "cumulative_hedge_position" not in st.session_state:
    st.session_state.cumulative_hedge_position = 0

if "hedge_trade_input" not in st.session_state:
    st.session_state.hedge_trade_input = 0

if "game_df" not in st.session_state:
    st.session_state.game_df = pd.DataFrame(columns=game_columns)

# --------------------------------------------------
# Helpers
# --------------------------------------------------
def reset_game():
    st.session_state.current_day_index = 0
    st.session_state.cumulative_profit_company = 0
    st.session_state.cumulative_hedge_position = 0
    st.session_state.hedge_trade_input = 0
    st.session_state.game_df = pd.DataFrame(columns=game_columns)

def format_signed_int_or_blank(x):
    return "" if pd.isna(x) else f"{int(x):+,}"

def format_int_or_blank(x):
    return "" if pd.isna(x) else f"{int(x):,}"

def format_price_or_blank(x):
    return "" if pd.isna(x) else f"{float(x):.4f}"

def build_chart_df():
    day0_row = pd.DataFrame([{
        "Day": 0,
        "Position Client": 0,
        "Position Hedge": 0,
        "Position Company": 0,
        "Open Price": np.nan,
        "Market Price": base_df.loc[0, "Open Price"],
        "Profit Client": 0,
        "Profit Hedge": 0,
        "Profit Company": 0,
        "Cumulative Profit Company": 0
    }])

    chart_df = pd.concat([day0_row, st.session_state.game_df], ignore_index=True)

    full_days = pd.DataFrame({"Day": list(range(0, 11))})
    merged_df = full_days.merge(chart_df, on="Day", how="left")

    numeric_cols = [
        "Position Client",
        "Position Hedge",
        "Position Company",
        "Open Price",
        "Market Price",
        "Profit Client",
        "Profit Hedge",
        "Profit Company",
        "Cumulative Profit Company"
    ]

    for col in numeric_cols:
        merged_df[col] = pd.to_numeric(merged_df[col], errors="coerce")

    return merged_df

def make_line_chart(df, columns, title, color_map, y_domain=None, y_format=",.0f", height=280, show_points=True):
    chart_df = df[["Day"] + columns].copy()

    for col in columns:
        chart_df[col] = pd.to_numeric(chart_df[col], errors="coerce")

    long_df = chart_df.melt(id_vars="Day", var_name="Series", value_name="Value")

    chart = (
        alt.Chart(long_df)
        .mark_line(strokeWidth=3, point=show_points)
        .encode(
            x=alt.X(
                "Day:Q",
                scale=alt.Scale(domain=[0, 10]),
                axis=alt.Axis(values=list(range(0, 11)), title="Day")
            ),
            y=alt.Y(
                "Value:Q",
                scale=alt.Scale(domain=y_domain) if y_domain else alt.Undefined,
                axis=alt.Axis(format=y_format, title=None)
            ),
            color=alt.Color(
                "Series:N",
                scale=alt.Scale(
                    domain=list(color_map.keys()),
                    range=list(color_map.values())
                ),
                legend=alt.Legend(
                    title="",
                    orient="bottom",
                    direction="horizontal"
                )
            ),
            tooltip=[
                alt.Tooltip("Day:Q"),
                alt.Tooltip("Series:N"),
                alt.Tooltip("Value:Q", format=y_format)
            ]
        )
        .properties(title=title, height=height)
    )

    st.altair_chart(chart, use_container_width=True)

# --------------------------------------------------
# Intro page
# --------------------------------------------------
if st.session_state.page == "intro":
    st.title("Market Risk Management Simulator")

    # Replace this filename with your actual image file
    # Example: put dealer_with_screens.png in the same folder as app.py
    try:
        st.image("dealer_with_screens.png", use_container_width=True)
    except Exception:
        pass

    st.markdown("""
You are a **risk manager**, trying to manage the company’s **market exposure** by deciding how much to hedge clients.

Each day:
- clients build a position
- you choose the hedge trade
- the market move is revealed
- you see the impact on company exposure and profit & loss
""")

    if st.button("Start Game", use_container_width=True):
        reset_game()
        st.session_state.page = "game"
        st.rerun()

# --------------------------------------------------
# Game page
# --------------------------------------------------
elif st.session_state.page == "game":
    st.title("Market Risk Management Simulator")

    top_col1, top_col2 = st.columns(2)

    with top_col1:
        if st.button("Back to Intro", use_container_width=True):
            st.session_state.page = "intro"
            st.rerun()

    with top_col2:
        if st.button("Restart Game", use_container_width=True):
            reset_game()
            st.rerun()

    game_finished = st.session_state.current_day_index >= len(base_df)
    merged_df = build_chart_df()

    if game_finished:
        st.success("Game finished.")
    else:
        row = base_df.loc[st.session_state.current_day_index]

        day = int(row["Day"])
        client_position = int(row["Position Client"])
        open_price = float(row["Open Price"])
        market_price = float(row["Market Price"])

        st.subheader(f"Day {day}")

        make_line_chart(
            merged_df,
            ["Market Price"],
            "Price Chart",
            {"Market Price": "#d62728"},
            y_domain=[1.4800, 1.5200],
            y_format=".4f",
            height=380,
            show_points=False
        )

        pending_hedge_position = st.session_state.cumulative_hedge_position + st.session_state.hedge_trade_input
        pending_company_position = pending_hedge_position - client_position

        summary_df = pd.DataFrame([{
            "Current Exposure": f"{client_position:+,}",
            "Hedge": f"{pending_hedge_position:+,}",
            "Net Position": f"{pending_company_position:+,}"
        }])

        st.dataframe(summary_df, use_container_width=True, hide_index=True)

        st.write("Adjust hedge trade in steps of 5. Negative means sell / short.")

        button_col1, button_col2 = st.columns(2)

        with button_col1:
            if st.button("Sell 5", use_container_width=True):
                st.session_state.hedge_trade_input -= 5
                st.rerun()

        with button_col2:
            if st.button("Buy 5", use_container_width=True):
                st.session_state.hedge_trade_input += 5
                st.rerun()

        if st.button("Submit Hedge", use_container_width=True):
            hedge_trade = st.session_state.hedge_trade_input
            st.session_state.cumulative_hedge_position += hedge_trade
            hedge_position = st.session_state.cumulative_hedge_position

            # Your sign convention:
            # Company = Hedge - Client
            company_position = hedge_position - client_position

            profit_client = (market_price - open_price) * client_position * contract_size
            profit_hedge = (market_price - open_price) * hedge_position * contract_size
            profit_company = (market_price - open_price) * company_position * contract_size

            st.session_state.cumulative_profit_company += profit_company

            new_row = pd.DataFrame([{
                "Day": day,
                "Position Client": client_position,
                "Position Hedge": hedge_position,
                "Position Company": company_position,
                "Open Price": round(open_price, 4),
                "Market Price": round(market_price, 4),
                "Profit Client": round(profit_client, 0),
                "Profit Hedge": round(profit_hedge, 0),
                "Profit Company": round(profit_company, 0),
                "Cumulative Profit Company": round(st.session_state.cumulative_profit_company, 0)
            }])

            st.session_state.game_df = pd.concat(
                [st.session_state.game_df, new_row],
                ignore_index=True
            )

            st.session_state.current_day_index += 1
            st.session_state.hedge_trade_input = 0
            st.rerun()

    # --------------------------------------------------
    # Game Progress table
    # --------------------------------------------------
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

    display_progress_df = pd.concat([day0_table_row, history_df], ignore_index=True)

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

    # --------------------------------------------------
    # Charts
    # --------------------------------------------------
    st.subheader("Position Chart")
    make_line_chart(
        merged_df,
        ["Position Client", "Position Hedge", "Position Company"],
        "Position Chart",
        {
            "Position Client": "#1f77b4",
            "Position Hedge": "#9ecae1",
            "Position Company": "#d62728"
        },
        y_format=",.0f"
    )

    st.subheader("Profit Chart")
    make_line_chart(
        merged_df,
        ["Profit Client", "Profit Hedge", "Profit Company"],
        "Profit Chart",
        {
            "Profit Client": "#1f77b4",
            "Profit Hedge": "#9ecae1",
            "Profit Company": "#d62728"
        },
        y_format=",.0f"
    )
