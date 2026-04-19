import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

st.set_page_config(page_title="Risk Management Game", layout="wide")

contract_size = 100000

base_df = pd.DataFrame({
    "Day": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "Position Client": [10, 20, 30, 40, 40, 30, 20, 10, 0, 0],
    "Open Price": [1.5000, 1.5050, 1.5000, 1.4950, 1.4900, 1.4900, 1.4950, 1.5000, 1.5050, 1.5100],
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

if "game_df" not in st.session_state:
    st.session_state.game_df = pd.DataFrame(columns=game_columns)

st.title("Market Risk Management Game")

if st.button("Restart Game"):
    st.session_state.current_day_index = 0
    st.session_state.cumulative_profit_company = 0
    st.session_state.cumulative_hedge_position = 0
    st.session_state.game_df = pd.DataFrame(columns=game_columns)
    st.rerun()

if st.session_state.current_day_index >= len(base_df):
    st.success("Game finished.")
else:
    row = base_df.loc[st.session_state.current_day_index]

    day = int(row["Day"])
    client_position = int(row["Position Client"])
    open_price = float(row["Open Price"])
    market_price = float(row["Market Price"])

    st.subheader(f"Day {day}")
    st.write(f"**Client Position:** {client_position:,}")
    st.write(f"**Open Price:** {open_price:.4f}")
    st.write(f"**Current Hedge Position:** {st.session_state.cumulative_hedge_position:,}")
    st.write("Enter hedge trade amount for this period before revealing the market price.")

    with st.form(f"hedge_form_day_{day}"):
        hedge_input = st.text_input("Hedge Trade This Period", placeholder="Enter whole number")
        submitted = st.form_submit_button("Submit Hedge")

    if submitted:
        hedge_input = hedge_input.strip()

        if hedge_input == "":
            st.warning("Please enter a hedge amount.")
        elif not hedge_input.isdigit():
            st.warning("Please enter a whole number only.")
        else:
            hedge_trade = int(hedge_input)

            st.session_state.cumulative_hedge_position += hedge_trade
            hedge_position = st.session_state.cumulative_hedge_position
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

            st.success(f"Day {day} completed")
            st.write(f"**Market Price revealed:** {market_price:.4f}")
            st.write(f"**New Hedge Position:** {hedge_position:,}")
            st.write(f"**Profit Company this day:** {profit_company:,.0f}")

            st.session_state.current_day_index += 1
            st.rerun()

if not st.session_state.game_df.empty:
    st.subheader("Game Progress")

    display_df = st.session_state.game_df.copy()

    display_df["Day"] = display_df["Day"].astype(int)
    display_df["Position Client"] = display_df["Position Client"].map(lambda x: f"{int(x):,}")
    display_df["Position Hedge"] = display_df["Position Hedge"].map(lambda x: f"{int(x):,}")
    display_df["Position Company"] = display_df["Position Company"].map(lambda x: f"{int(x):,}")
    display_df["Open Price"] = display_df["Open Price"].map(lambda x: f"{float(x):.4f}")
    display_df["Market Price"] = display_df["Market Price"].map(lambda x: f"{float(x):.4f}")
    display_df["Profit Client"] = display_df["Profit Client"].map(lambda x: f"{int(x):,}")
    display_df["Profit Hedge"] = display_df["Profit Hedge"].map(lambda x: f"{int(x):,}")
    display_df["Profit Company"] = display_df["Profit Company"].map(lambda x: f"{int(x):,}")
    display_df["Cumulative Profit Company"] = display_df["Cumulative Profit Company"].map(lambda x: f"{int(x):,}")

    st.dataframe(display_df, use_container_width=True)

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
            x=alt.X("Day:Q", scale=alt.Scale(domain=[1, 10]), axis=alt.Axis(values=list(range(1, 11)), title="Day")),
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
        .properties(title=title, height=380)
    )

    st.altair_chart(chart, use_container_width=True)

st.subheader("Price Chart")
make_line_chart(
    merged_df,
    ["Market Price"],
    "Price Chart",
    {
        "Market Price": "#d62728"
    },
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
