import streamlit as st

def show_risk_calculator():
    st.title("🛡️ Crypto Perpetual Trading Risk Guard")

    # ---------- SIDEBAR ----------
    with st.sidebar:
        st.header("Account")

        account_type = st.selectbox(
            "Account Type",
            ["Personal Account", "Prop Firm"]
        )

        starting_balance = st.number_input(
            "Starting Balance ($)",
            value=100000.0,
            step=1000.0
        )

        current_balance = st.number_input(
            "Current Balance ($)",
            value=100000.0,
            step=1000.0
        )

        risk_mode = st.selectbox(
            "Risk Mode",
            ["Aggressive", "Balanced", "Sustainable"]
        )

        st.divider()
        st.header("Trade Setup")

        stop_loss_pct = st.number_input(
            "Stop Loss % (from TradingView)",
            min_value=0.1,
            value=2.0
        )

        margin_pct = st.number_input(
            "% of Balance Used as Margin",
            min_value=1.0,
            max_value=100.0,
            value=50.0
        )

        if account_type == "Prop Firm":
            st.divider()
            st.header("Prop Firm Rules")

            max_dd_pct = st.number_input(
                "Max Drawdown %",
                value=10.0
            )

            daily_dd_pct = st.number_input(
                "Daily Drawdown %",
                value=5.0
            )

    # ---------- RISK MODE SETTINGS ----------
    divider_map = {
        "Aggressive": 10,
        "Balanced": 20,
        "Sustainable": 40
    }
    divider = divider_map[risk_mode]

    # ---------- PERSONAL ACCOUNT ----------
    if account_type == "Personal Account":
        risk_pct_map = {
            "Aggressive": 5,
            "Balanced": 2,
            "Sustainable": 1
        }

        risk_pct = risk_pct_map[risk_mode]
        risk_dollars = current_balance * (risk_pct / 100)

        note = "✅ Personal account risk applied based on selected risk mode."

    # ---------- PROP FIRM ----------
    else:
        max_dd_dollars = starting_balance * (max_dd_pct / 100)
        daily_dd_dollars = starting_balance * (daily_dd_pct / 100)

        drawdown_used = starting_balance - current_balance
        remaining_dd = max_dd_dollars - drawdown_used

        if remaining_dd <= 0:
            st.error("❌ Account has breached max drawdown.")
            st.stop()

        base_risk = remaining_dd / divider
        daily_cap = daily_dd_dollars * 0.40

        if base_risk > daily_cap:
            risk_dollars = daily_cap
            note = "⚠️ Risk capped to protect daily drawdown"
        else:
            risk_dollars = base_risk
            note = "✅ Risk within prop firm limits"

    # ---------- LEVERAGE CALC ----------
    stop_fraction = stop_loss_pct / 100
    position_size = risk_dollars / stop_fraction
    margin_used = current_balance * (margin_pct / 100)
    leverage = position_size / margin_used

    # ---------- OUTPUT ----------
    st.subheader("Risk Output")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Risk Per Trade ($)", f"${risk_dollars:,.2f}")
        st.write(note)

    with col2:
        st.metric("Recommended Leverage", f"{leverage:.2f}x")

    st.divider()

    st.info(
        "Recalculate after every trade. "
        "Risk adapts dynamically based on your personal account "
        "or prop firm risk rules."
    )
