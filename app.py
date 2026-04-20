import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Risk Management Game", layout="centered")

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

st.title("Market Risk Management Game")

if st.button("Restart Game", use_container_width=True):
    st.session_state.current_day_index = 0
    st.session_state.cumulative_profit_company = 0
    st.session_state.cumulative_hedge_position = 0
    st.session_state.hedge_trade_input = 0
    st.session_state.game_df = pd.DataFrame(columns=game_columns)
    st.rerun()

game_finished = st.session_state.current_day_index >= len(base_df)

if game_finished:
    st.success("Game finished.")
else:
    row = base_df.loc[st.session_state.current_day_index]

    day = int(row["Day"])
    client_position = int(row["Position Client"])
    open_price = float(row["Open Price"])
    market_price = float(row["Market Price"])

    st.subheader(f"Day {day}")
    st.write(f"**Client Position:** {client_position:+,}")
    st.write(f"**Open Price:** {open_price:.4f}")
    st.write(f"**Current Hedge Position:** {st.session_state.cumulative_hedge_position:+,}")
    st.write("Adjust hedge trade in steps of 5. Negative means sell / short.")

    step_col1, step_col2, value_col = st.columns([1, 1, 2])

    with step_col1:
        if st.button("- 5", use_container_width=True):
            st.session_state.hedge_trade_input -= 5
            st.rerun()

    with step_col2:
        if st.button("+ 5", use_container_width=True):
            st.session_state.hedge_trade_input += 5
            st.rerun()

    with value_col:
        st.metric("Hedge Trade This Period", f"{st.session_state.hedge_trade_input:+,}")

    if st.button("Submit Hedge", use_container_width=True):
        hedge_trade = st.session_state.hedge_trade_input

        st.session_state.cumulative_hedge_position += hedge_trade
        hedge_position = st.session_state.cumulative_hedge_position

        company_position = client_position - hedge_position

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

        st.success(f"Day {day} completed")
        st.write(f"**Market Price revealed:** {market_price:.4f}")
        st.write(f"**Hedge Trade This Period:** {hedge_trade:+,}")
        st.write(f"**New Hedge Position:** {hedge_position:+,}")
        st.write(f"**Profit Company this day:** {profit_company:,.0f}")

        st.session_state.current_day_index += 1
        st.session_state.hedge_trade_input = 0
        st.rerun()

st.subheader("Game Progress")

display_progress_df = st.session_state.game_df.copy()

if not game_finished:
    preview_row = pd.DataFrame([{
        "Day": int(base_df.loc[st.session_state.current_day_index, "Day"]),
        "Position Client": int(base_df.loc[st.session_state.current_day_index, "Position Client"]),
        "Position Hedge": np.nan,
        "Position Company": np.nan,
        "Open Price": float(base_df.loc[st.session_state.current_day_index, "Open Price"]),
        "Market Price": np.nan,
        "Profit Client": np.nan,
        "Profit Hedge": np.nan,
        "Profit Company": np.nan,
        "Cumulative Profit Company": np.nan
    }])

    display_progress_df = pd.concat([display_progress_df, preview_row], ignore_index=True)
    current_preview_day = int(preview_row.iloc[0]["Day"])
else:
    current_preview_day = None

def format_signed_int_or_blank(x):
    return "" if pd.isna(x) else f"{int(x):+,}"

def format_int_or_blank(x):
    return "" if pd.isna(x) else f"{int(x):,}"

def format_price_or_blank(x):
    return "" if pd.isna(x) else f"{float(x):.4f}"

formatted_df = display_progress_df.copy()
formatted_df["Day"] = formatted_df["Day"].map(lambda x: f"{int(x)}")
formatted_df["Position Client"] = formatted_df["Position Client"].map(format_signed_int_or_blank)
formatted_df["Position Hedge"] = formatted_df["Position Hedge"].map(format_signed_int_or_blank)
formatted_df["Position Company"] = formatted_df["Position Company"].map(format_signed_int_or_blank)
formatted_df["Open Price"] = formatted_df["Open Price"].map(format_price_or_blank)
formatted_df["Market Price"] = formatted_df["Market Price"].map(format_price_or_blank)
formatted_df["Profit Client"] = formatted_df["Profit Client"].map(format_int_or_blank)
formatted_df["Profit Hedge"] = formatted_df["Profit Hedge"].map(format_int_or_blank)
formatted_df["Profit Company"] = formatted_df["Profit Company"].map(format_int_or_blank)
formatted_df["Cumulative Profit Company"] = formatted_df["Cumulative Profit Company"].map(format_int_or_blank)

def highlight_current_row(row):
    if current_preview_day is not None and row["Day"] == str(current_preview_day):
        return ["background-color: #fff3cd; font-weight: bold;"] * len(row)
    return [""] * len(row)

styled_df = formatted_df.style.apply(highlight_current_row, axis=1)

st.dataframe(styled_df, use_container_width=True, hide_index=True)

chart_base = pd.DataFrame({"Day": base_df["Day"]})

if not st.session_state.game_df.empty:
    merged_df = chart_base.merge(st.session_state.game_df, on="Day", how="left")
else:
    merged_df = chart_base.copy()
    for col in game_columns[1:]:
        merged_df[col] = np.nan

def make_line_chart(df, columns, title, color_map, y_domain=None, y_format=",.0f"):
    chart_df = df[["Day"] + columns].copy()
    long_df = chart_df.melt(id_vars="Day", var_name="Series", value_name="Value")

    chart = (
        alt.Chart(long_df)
        .mark_line(point=True, strokeWidth=3)
        .encode(
            x=alt.X(
                "Day:Q",
                scale=alt.Scale(domain=[1, 10]),
                axis=alt.Axis(values=list(range(1, 11)), title="Day")
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
                legend=alt.Legend(title="")
            ),
            tooltip=[
                alt.Tooltip("Day:Q"),
                alt.Tooltip("Series:N"),
                alt.Tooltip("Value:Q", format=y_format)
            ]
        )
        .properties(title=title, height=300)
    )

    st.altair_chart(chart, use_container_width=True)

st.subheader("Price Chart")
make_line_chart(
    merged_df,
    ["Market Price"],
    "Price Chart",
    {"Market Price": "#d62728"},
    y_domain=[1.4900, 1.5100],
    y_format=".4f"
)

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
