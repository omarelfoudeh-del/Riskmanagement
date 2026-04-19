import streamlit as st
import pandas as pd

st.set_page_config(page_title="Risk Management Game", layout="wide")

contract_size = 100000

# Fixed data from your picture
base_df = pd.DataFrame({
    "Day": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
    "Position Client": [10, 20, 30, 40, 40, 30, 20, 10, 0, 0],
    "Open Price": [1.5000, 1.5050, 1.5000, 1.4050, 1.4000, 1.3050, 1.4000, 1.4050, 1.5000, 1.5000],
    "Market Price": [1.5050, 1.5000, 1.4050, 1.4000, 1.3050, 1.4000, 1.4050, 1.5000, 1.5000, 1.5050]
})

# Session state setup
if "current_day_index" not in st.session_state:
    st.session_state.current_day_index = 0

if "cumulative_profit_company" not in st.session_state:
    st.session_state.cumulative_profit_company = 0

if "game_df" not in st.session_state:
    st.session_state.game_df = pd.DataFrame(columns=[
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
    ])

st.title("Market Risk Management Game")

# Reset button
if st.button("Restart Game"):
    st.session_state.current_day_index = 0
    st.session_state.cumulative_profit_company = 0
    st.session_state.game_df = pd.DataFrame(columns=[
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
    ])
    st.rerun()

# Check if game finished
if st.session_state.current_day_index >= len(base_df):
    st.success("Game finished.")
    st.dataframe(st.session_state.game_df, use_container_width=True)
else:
    row = base_df.loc[st.session_state.current_day_index]

    day = int(row["Day"])
    client_position = row["Position Client"]
    open_price = row["Open Price"]
    market_price = row["Market Price"]

    st.subheader(f"Day {day}")
    st.write(f"**Client Position:** {client_position}")
    st.write(f"**Open Price:** {open_price:.4f}")
    st.write("Enter your hedge amount before revealing the market price.")

    with st.form(f"hedge_form_day_{day}"):
        hedge_position = st.number_input(
            "Hedge Amount",
            value=0.0,
            step=1.0,
            format="%.2f"
        )
        submitted = st.form_submit_button("Submit Hedge")

    if submitted:
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

        st.session_state.current_day_index += 1

        st.success(f"Day {day} completed")
        st.write(f"**Market Price revealed:** {market_price:.4f}")
        st.write(f"**Profit Company this day:** {profit_company:,.0f}")

        st.rerun()

# Always show progress table
if not st.session_state.game_df.empty:
    st.subheader("Game Progress")
    st.dataframe(st.session_state.game_df, use_container_width=True)
