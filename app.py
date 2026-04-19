import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="Risk Management Game", layout="wide")

contract_size = 100000

# Fixed data
base_df = pd.DataFrame({
    "Day": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "Position Client": [10, 20, 30, 40, 40, 30, 20, 10, 0, 0],
    "Open Price": [1.5000, 1.5050, 1.5000, 1.4050, 1.4000, 1.3050, 1.4000, 1.4050, 1.5000, 1.5000],
    "Market Price": [1.5050, 1.5000, 1.4050, 1.4000, 1.3050, 1.4000, 1.4050, 1.5000, 1.5000, 1.5050]
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

# Session state
if "current_day_index" not in st.session_state:
    st.session_state.current_day_index = 0

if "cumulative_profit_company" not in st.session_state:
    st.session_state.cumulative_profit_company = 0

if "game_df" not in st.session_state:
    st.session_state.game_df = pd.DataFrame(columns=game_columns)

st.title("Market Risk Management Game")

# Restart
if st.button("Restart Game"):
    st.session_state.current_day_index = 0
    st.session_state.cumulative_profit_company = 0
    st.session_state.game_df = pd.DataFrame(columns=game_columns)
    st.rerun()

# Main input area
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
    st.write("Enter your hedge amount before revealing the market price.")

    with st.form(f"hedge_form_day_{day}"):
        hedge_position = st.number_input(
            "Hedge Amount",
            min_value=0,
            step=1,
            value=None,
            placeholder="Enter whole number"
        )
        submitted = st.form_submit_button("Submit Hedge")

    if submitted:
        if hedge_position is None:
            st.warning("Please enter a hedge amount.")
        else:
            hedge_position = int(hedge_position)
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
            st.write(f"**Profit Company this day:** {profit_company:,.0f}")

            st.session_state.current_day_index += 1
            st.rerun()

# Table
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

# Build charts across all 10 periods, with future periods blank
chart_base = pd.DataFrame({"Day": base_df["Day"]})

if not st.session_state.game_df.empty:
    merged_df = chart_base.merge(st.session_state.game_df, on="Day", how="left")
else:
    merged_df = chart_base.copy()
    for col in game_columns[1:]:
        merged_df[col] = np.nan

# Position chart
st.subheader("Position Chart")
position_chart_df = merged_df[["Day", "Position Client", "Position Hedge", "Position Company"]].copy()
position_chart_df = position_chart_df.set_index("Day")
st.line_chart(position_chart_df)

# Profit chart
st.subheader("Profit Chart")
profit_chart_df = merged_df[["Day", "Profit Client", "Profit Hedge", "Profit Company"]].copy()
profit_chart_df = profit_chart_df.set_index("Day")
st.line_chart(profit_chart_df)

# Price chart
st.subheader("Price Chart")
price_chart_df = merged_df[["Day", "Open Price", "Market Price"]].copy()
price_chart_df = price_chart_df.set_index("Day")
st.line_chart(price_chart_df)
