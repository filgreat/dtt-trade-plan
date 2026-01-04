import streamlit as st
from datetime import datetime, timedelta
import pytz


def show_trade_plan():
    st.title("🧭 DTT Trade Plan (Direction → Target → Timing)")
    st.caption("Sequential validation. If a gate fails, the trade is not ready.")
    st.divider()

    discipline_score = 0
    max_score = 4
    trade_state = "WAITING"  # <-- FIX: default state to prevent crash

    # =============================
    # GATE 1 — DIRECTION & CONTEXT
    # =============================
    st.subheader("🟦 Gate 1: Direction & Context")

    trade_direction = st.radio(
        "Trade direction",
        ["", "Long", "Short"],
        index=0
    )

    daily_bias = st.radio(
        "Daily structure bias",
        ["", "Continuation (HH / LL)", "Pullback (HL / LH)"],
        index=0
    )

    htf_traffic = st.radio(
        "Higher timeframe traffic (Weekly / Monthly)",
        [
            "",
            "Aligned – no major levels in the way",
            "Crowded – major HTF levels nearby"
        ],
        index=0
    )

    daily_location = st.radio(
        "Price location within today’s range",
        [
            "",
            "Near Daily Low",
            "Middle of Range",
            "Near Daily High"
        ],
        index=0
    )

    direction_ok = (
        trade_direction != ""
        and daily_bias != ""
        and htf_traffic == "Aligned – no major levels in the way"
        and daily_location != ""
    )

    if not direction_ok:
        st.warning("⏳ Direction & context not aligned")
        trade_state = "NO TRADE"
        show_footer(trade_state, 0)
        return

    discipline_score += 1

    # Non-blocking location warnings (impact discipline later)
    if trade_direction == "Long" and daily_location == "Near Daily High":
        st.warning("⚠️ Longing near the daily high increases pullback risk")

    if trade_direction == "Short" and daily_location == "Near Daily Low":
        st.warning("⚠️ Shorting near the daily low risks selling the bottom")

    if daily_location == "Middle of Range":
        st.info("ℹ️ Mid-range entries require conservative stop placement")
        
    # Location discipline scoring (non-blocking)
    location_good = False

    if trade_direction == "Long" and daily_location == "Near Daily Low":
        location_good = True
    elif trade_direction == "Short" and daily_location == "Near Daily High":
        location_good = True

    if location_good:
        discipline_score += 1

    st.success("✅ Direction & context aligned")
    st.divider()

    # =============================
    # GATE 2 — TARGET & STRUCTURE
    # =============================
    st.subheader("🟦 Gate 2: Target & Structure")

    space_check = st.radio(
        "Clear space to next DAILY HTF S/R",
        ["", "Yes – clean space", "No – target too close"],
        index=0
    )

    rr_check = st.radio(
        "2R or better achievable",
        ["", "Yes", "No"],
        index=0
    )

    htf_rejection = st.radio(
        "Reaction from Daily–Monthly S/R",
        [
            "",
            "Yes – clear rejection / flip",
            "No – reacting from open space"
        ],
        index=0
    )

    if trade_direction == "Long":
        structure_confirm = st.radio(
            "4H–1H structure",
            [
                "",
                "Broke above resistance and held",
                "Still rejecting / ranging"
            ],
            index=0
        )
        structure_ok = structure_confirm == "Broke above resistance and held"
    else:
        structure_confirm = st.radio(
            "4H–1H structure",
            [
                "",
                "Broke below support and held",
                "Still rejecting / ranging"
            ],
            index=0
        )
        structure_ok = structure_confirm == "Broke below support and held"

    target_ok = (
        space_check == "Yes – clean space"
        and rr_check == "Yes"
        and htf_rejection == "Yes – clear rejection / flip"
        and structure_ok
    )

    if not target_ok:
        st.warning("⏳ Target & structure not confirmed")
        trade_state = "WAITING"
        show_footer(trade_state, discipline_score)
        return

    discipline_score += 1
    st.success("✅ Target & structure confirmed")
    st.divider()

    # =============================
    # GATE 3 — TIMING & ENTRY
    # =============================
    st.subheader("🟦 Gate 3: Timing & Entry")

    entry_tf = st.radio(
        "Entry confirmation timeframe",
        ["", "15m", "30m", "1H"],
        index=0
    )

    entry_signal = st.radio(
        "Entry confirmation criteria",
        [
            "",
            "Break of structure + Engulfing candle + Volume increase",
            "Double top/bottom OR H&S/inverse H&S + Engulfing candle + Volume increase"
        ],
        index=0
    )

    timing_ok = entry_tf != "" and entry_signal != ""

    if entry_tf in ["30m", "1H"]:
        structure_15m = st.radio(
            "15m structure condition",
            [
                "",
                "Aligned and corrected",
                "Extended / late"
            ],
            index=0
        )
        if structure_15m != "Aligned and corrected":
            timing_ok = False

    # =============================
    # FIXED 4H WINDOWS (UTC-5)
    # =============================
    tz = pytz.timezone("America/Bogota")
    now = datetime.now(tz)

    blocks = [
        (23, 3),
        (3, 7),
        (7, 11),
        (11, 15),
        (15, 19),
        (19, 23)
    ]

    for start, end in blocks:
        if start > end:
            if now.hour >= start or now.hour < end:
                block_start = now.replace(hour=start, minute=0, second=0, microsecond=0)
                if now.hour < end:
                    block_start -= timedelta(days=1)
                block_end = block_start + timedelta(hours=4)
                break
        else:
            if start <= now.hour < end:
                block_start = now.replace(hour=start, minute=0, second=0, microsecond=0)
                block_end = block_start + timedelta(hours=4)
                break

    entry_window_start = block_end - timedelta(hours=2)
    in_window = entry_window_start <= now <= block_end

    st.markdown("### ⏱️ Time Context")
    st.write(
        f"**Current 4H candle:** {block_start.strftime('%H:%M')} → {block_end.strftime('%H:%M')}"
    )
    st.write(
        f"**Valid entry window:** {entry_window_start.strftime('%H:%M')} → {block_end.strftime('%H:%M')}"
    )

    if not in_window:
        minutes_to_window = int((entry_window_start - now).total_seconds() // 60)
        if minutes_to_window < 0:
            next_block_start = block_start + timedelta(hours=4)
            next_entry = next_block_start + timedelta(hours=2)
            minutes_to_window = int((next_entry - now).total_seconds() // 60)

        st.warning(
            f"⏳ Not in entry window — next window opens in ~{minutes_to_window} minutes"
        )
        timing_ok = False
        trade_state = "WAITING"
    else:
        st.success("🟢 Inside optimal execution window")
        if timing_ok:
            discipline_score += 1
            trade_state = "TRADE READY"

    st.caption(
        "📊 Volume tends to increase during the final 2 hours of every 4H candle. "
        "This window statistically improves continuation and execution quality."
    )

    # =============================
    # FINAL DECISION
    # =============================
    if timing_ok and in_window:
        st.success("🟢 TRADE CONDITIONS MET")

        st.markdown("### 📌 Stop-Loss Guidance")
        st.write(
            "- **Long:** Below last valid 15m–4H Higher Low\n"
            "- **Short:** Above last valid 15m–4H Lower High"
        )

        st.markdown("### ⚠️ In-Trade Management")
        st.write(
            "- Exit early if 15m structure flips against the position\n"
            "- Entry reason = Exit reason"
        )
    else:
        st.error("🔴 NO TRADE — timing conditions not met")

    show_footer(trade_state, discipline_score, trade_direction, daily_bias, daily_location)


def show_footer(trade_state, discipline_score, trade_direction=None, daily_bias=None, daily_location=None):
    # -----------------------------
    # SAFE MARKET CONTEXT (for snapshot)
    # -----------------------------
    market_context = "Context forming"

    if trade_direction and daily_bias:
        if trade_direction == "Long":
            if daily_bias.startswith("Continuation"):
                market_context = "Likely continuation toward Daily High"
            else:
                market_context = "Likely pullback toward Daily Lower High"
        else:
            if daily_bias.startswith("Continuation"):
                market_context = "Likely continuation toward Daily Lower Low"
            else:
                market_context = "Likely pullback toward Daily Higher Low"

    st.divider()

    score_pct = int((discipline_score / 4) * 100)

    st.markdown("### 📊 Trade Plan Discipline")
    st.progress(score_pct)

    if score_pct >= 75:
        st.success(f"High discipline ({score_pct}%)")
    elif score_pct >= 50:
        st.warning(f"Moderate discipline ({score_pct}%)")
    else:
        st.error(f"Low discipline ({score_pct}%)")

    st.markdown("### 🚦 Trade State")
    if trade_state == "TRADE READY":
        st.success("🟢 TRADE READY")
    elif trade_state == "WAITING":
        st.warning("🟡 WAITING — conditions developing")
    else:
        st.error("🔴 NO TRADE (POSITION)")

    # =============================
    # DTT SOCIAL SNAPSHOT
    # =============================
    if trade_state == "TRADE READY":
        st.markdown("### 🧭 DTT Trade Snapshot")

        snapshot = (
            f"🧭 **DTT Trade Snapshot**\n\n"
            f"📌 **Direction:** {trade_direction}\n"
            f"🧠 **Market context:** {market_context}\n"
            f"📍 **Entry location:** {daily_location}\n"
            f"🛣️ **HTF traffic:** Clear\n"
            f"⏱️ **Timing:** Optimal window\n"
            f"📊 **Trade plan discipline:** {score_pct}%"
        )

        st.code(snapshot)
        st.caption("— DTT")

