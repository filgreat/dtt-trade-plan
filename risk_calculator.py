import streamlit as st

def show_risk_calculator():
    st.title("🛡️ DTT Position Manager")

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
            "Balanced": 2.5,
            "Sustainable": 1
        }

        risk_pct = risk_pct_map[risk_mode]
        risk_dollars = current_balance * (risk_pct / 100)

        remaining_dd = current_balance

        note = "Personal account risk based on selected protection mode"

    # ---------- PROP FIRM ----------
    else:

        max_dd_dollars = starting_balance * (max_dd_pct / 100)
        daily_dd_dollars = starting_balance * (daily_dd_pct / 100)

        drawdown_used = starting_balance - current_balance
        remaining_dd = max_dd_dollars - drawdown_used

        if remaining_dd <= 0:
            st.error("Account breached max drawdown.")
            st.stop()

        base_risk = remaining_dd / divider
        daily_cap = daily_dd_dollars * 0.40

        risk_dollars = min(base_risk, daily_cap)

        note = "Risk dynamically adjusted to protect prop firm limits"

    # ---------- SAFETY METRICS ----------
    losses_remaining = int(remaining_dd / risk_dollars) if risk_dollars > 0 else 0
    risk_pct_actual = (risk_dollars / current_balance) * 100

    # ---------- OUTPUT ----------
    st.subheader("Recommended Risk")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Risk Per Trade ($)", f"${risk_dollars:,.2f}")
        st.caption("Maximum allowed loss on next trade")

    with col2:
        st.metric("Risk % of Account", f"{risk_pct_actual:.2f}%")
        st.caption("Capital exposure per trade")

    st.divider()

    col3, col4 = st.columns(2)

    with col3:
        st.metric(
            "Remaining Drawdown ($)",
            f"${remaining_dd:,.2f}"
        )

    with col4:
        st.metric(
            "Losses Remaining",
            f"{losses_remaining}"
        )

    st.divider()

    st.info(
        "Enter this risk amount on your broker.\n\n"
        "Adjust position size so stop-loss equals this risk."
    )
# ---------- LEVERAGE GUIDANCE ----------
    if account_type == "Prop Firm":
        st.warning(
            "⚠️ Prop Firm Guidance: Use 10x leverage or less.\n\n"
            
        )
    else:
        st.caption(
            "Leverage is flexible on personal accounts. "
            "Always ensure stop-loss matches the recommended risk amount."
        )