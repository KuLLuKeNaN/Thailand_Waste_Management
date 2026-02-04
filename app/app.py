import os
import pandas as pd
import streamlit as st

from logic.demand_engine import DemandInputs, estimate_portions
from logic.savings import estimate_savings
from logic.green_star import evaluate_green_star
from logic.history import generate_fake_history

st.set_page_config(
    page_title="FoodSave.AI — Hotel Edition",
    page_icon="🍽️",
    layout="wide",
    initial_sidebar_state="expanded",
)
if "green_star_streak" not in st.session_state:
    st.session_state.green_star_streak = 0

BASE_DIR = os.path.dirname(__file__)
DATA_PATH = os.path.join(BASE_DIR, "data", "sample_menu_costs.csv")


def load_menu_costs(path: str) -> pd.DataFrame:
    if os.path.exists(path):
        return pd.read_csv(path)
    return pd.DataFrame(
        {"item": ["Breakfast Buffet", "Lunch Buffet", "Dinner Buffet"], "cost_thb_per_portion": [65, 95, 120]}
    )


menu_df = load_menu_costs(DATA_PATH)
menu_items = menu_df["item"].tolist()


st.markdown(
    """
    <style>
      .block-container { padding-top: 1.2rem; padding-bottom: 2.2rem; }
      .fs-header { display:flex; gap:12px; align-items:center; }
      .fs-title { font-size: 34px; font-weight: 800; margin:0; }
      .fs-badge {
        display:inline-block; padding:6px 10px; border-radius: 999px;
        border: 1px solid rgba(0,0,0,0.10);
        font-size: 12px; font-weight: 700;
      }
      .fs-sub { margin-top: 6px; color: rgba(0,0,0,0.65); font-size: 14px; }
      .kpi-card {
        border: 1px solid rgba(0,0,0,0.10);
        border-radius: 16px;
        padding: 14px 14px;
      }
      .kpi-label { font-size: 12px; color: rgba(0,0,0,0.60); margin-bottom: 6px; font-weight: 600; }
      .kpi-value { font-size: 26px; font-weight: 800; line-height: 1.05; }
      .kpi-sub { font-size: 12px; color: rgba(0,0,0,0.60); margin-top: 6px; }
      .big-rec {
        border: 1px solid rgba(0,0,0,0.12);
        border-radius: 18px;
        padding: 16px 16px;
      }
      .big-rec h3 { margin:0 0 6px 0; }
      .muted { color: rgba(0,0,0,0.60); }
      .divider { height: 1px; background: rgba(0,0,0,0.08); margin: 14px 0; }
      .pill {
        display:inline-block; padding:4px 10px; border-radius: 999px;
        border: 1px solid rgba(0,0,0,0.10);
        font-size: 12px; font-weight: 700;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="fs-header">
      <div>
        <div class="fs-title">FoodSave.AI</div>
        <div class="fs-sub">AI-assisted daily cooking guidance to reduce avoidable food waste and prove sustainability impact.</div>
      </div>
      <div class="fs-badge">Hotel Edition • Bangkok Demo</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")

with st.sidebar:
    st.markdown("### Inputs")
    jury_mode = st.toggle("Jury Mode (show explanations)", value=False)

    target_meal = st.selectbox("Meal / Buffet Service", menu_items, index=0)

    expected_guests = st.number_input(
        "Expected Guests Today", min_value=0, max_value=5000, value=320, step=10
    )

    occupancy_rate = st.slider("Hotel Occupancy Rate", 0.0, 1.0, 0.72, 0.01)

    c1, c2 = st.columns(2)
    with c1:
        weather = st.selectbox("Weather", ["Sunny", "Cloudy", "Rainy", "Storm"], index=2)
    with c2:
        day_type = st.selectbox("Day Type", ["Weekday", "Weekend", "Holiday"], index=0)

    event_level = st.selectbox("Local Events", ["None", "Medium", "High"], index=0)

    st.markdown("---")
    days_used = None
    if jury_mode:
        st.markdown("### Green Star ⭐ tracking (demo)")
        days_used = st.slider("Days used in a row", 0, 30, 6, 1)
    else:
        st.caption("Green Star streak is calculated automatically from end-of-day feedback.")


    run = st.button("Generate Today’s Recommendation", type="primary", use_container_width=True)
    if "generated" not in st.session_state:
        st.session_state.generated = False

    if run:
        st.session_state.generated = True


def kpi(label: str, value: str, sub: str = ""):
    st.markdown(
        f"""
        <div class="kpi-card">
          <div class="kpi-label">{label}</div>
          <div class="kpi-value">{value}</div>
          <div class="kpi-sub">{sub}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


if not st.session_state.generated:
    st.info("Use the sidebar to set today’s inputs, then click **Generate Today’s Recommendation**.")
    st.stop()


cost_row = menu_df[menu_df["item"] == target_meal].iloc[0]
cost_thb_per_portion = float(cost_row["cost_thb_per_portion"])

inp = DemandInputs(
    target_meal=target_meal,
    expected_guests=int(expected_guests),
    occupancy_rate=float(occupancy_rate),
    weather=weather,
    day_type=day_type,
    event_level=event_level,
)

out = estimate_portions(inp)

savings = estimate_savings(
    recommended_portions=out.recommended_portions,
    baseline_portions=out.baseline_portions,
    cost_thb_per_portion=cost_thb_per_portion,
)

streak_days = int(st.session_state.green_star_streak)
demo_days = int(days_used) if (jury_mode and days_used is not None) else streak_days

# Star logic: jury_mode sadece "simulate star" için
effective_days = int(st.session_state.green_star_streak)


star = evaluate_green_star(
    estimated_waste_reduction_pct=savings.estimated_waste_reduction_pct,
    days_used_in_a_row=effective_days,
)

delta_portions = out.recommended_portions - out.baseline_portions
delta_pct = (delta_portions / max(1, out.baseline_portions)) * 100.0

top = st.columns([1, 1, 1], gap="large")
with top[0]:
    kpi("Recommended Portions", f"{out.recommended_portions}", f"Baseline: {out.baseline_portions}")
with top[1]:
    monthly_savings = savings.estimated_savings_thb * 30.0
    kpi("Estimated Monthly Savings", f"฿{monthly_savings:,.0f}", "Ingredients only (demo estimate)")
with top[2]:
    kpi("Avoided Waste", f"{savings.estimated_avoided_waste_kg:.2f} kg/day", "Based on portion equivalent (demo)")

st.write("")

st.markdown(
    f"""
    <div class="big-rec">
      <h3>Today’s Decision</h3>
      <div style="font-size:16px; font-weight:800;">
        Cook ~{out.recommended_portions} portions for <span class="pill">{target_meal}</span>
      </div>
      <div class="muted" style="margin-top:8px;">
        Change vs baseline: {'+' if delta_portions>=0 else ''}{delta_portions} portions ({'+' if delta_pct>=0 else ''}{delta_pct:.1f}%)
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("")
st.write("")
st.markdown("## Last 7 Days — Learning Trend (Demo)")

history_rows = generate_fake_history(
    today_baseline=out.baseline_portions,
    today_recommended=out.recommended_portions,
    today_avoided_kg=savings.estimated_avoided_waste_kg,
    days=7,
)

hist_df = pd.DataFrame(history_rows)

c1, c2 = st.columns([1.1, 0.9], gap="large")

with c1:
    st.markdown("### Portions: Baseline vs Recommended")
    chart_df = hist_df.set_index("date")[["baseline", "recommended"]]
    st.bar_chart(chart_df)

with c2:
    st.markdown("### Avoided Food Waste (kg/day)")
    waste_df = hist_df.set_index("date")[["avoided_kg"]]
    st.line_chart(waste_df)

st.caption(
    "Demo note: This is generated historical data to visualize learning trends. "
    "In production, these charts reflect real daily outcomes."
)


cA, cB = st.columns([1.05, 0.95], gap="large")

with cA:
    st.markdown("### Impact Snapshot")
    st.progress(min(1.0, max(0.0, 0.5 + (-delta_pct / 100.0))), text="Waste reduction tendency (visual indicator)")
    st.caption("Higher is better. This is a simple visual cue based on recommendation vs baseline.")

    st.markdown("### Green Star ⭐")
    if star.is_active:
        st.success(f"⭐ **ACTIVE** — Score: {star.score}/100")
    else:
        st.warning(f"⭐ Not active yet — Score: {star.score}/100")
    st.caption(star.reason)

    st.markdown("### One-line pitch")
    st.info(
        "FoodSave.AI turns intuition-based kitchen planning into data-driven daily guidance, "
        "reducing avoidable overproduction and creating measurable savings + visible sustainability proof."
    )

with cB:
    st.markdown("### Assumptions (demo)")
    st.write(f"- Portion cost: **฿{cost_thb_per_portion:.0f}**")
    st.write(f"- Estimated avoidable waste reduction: **{savings.estimated_waste_reduction_pct*100:.1f}%**")
    st.write(f"- Green Star streak: **{effective_days}** day(s)")
    st.write(f"- Real streak (from End-of-Day): **{streak_days}** day(s)")
    if jury_mode:
        st.write(f"- Demo streak (slider): **{demo_days}** day(s)")

    st.write("")

    if jury_mode:
        with st.expander("How the recommendation was calculated"):
            for line in out.explanation:
                st.write("- " + line)

        with st.expander("Savings assumptions details"):
            for n in savings.notes:
                st.write("- " + n)

st.divider()
st.markdown("## End of Day — What actually happened?")

actual_cooked = st.number_input(
    "Today we actually cooked (portions)",
    min_value=0,
    max_value=10000,
    value=out.recommended_portions,
    step=5,
    help="Enter the total portions actually prepared today."
)

baseline = out.baseline_portions
recommended = out.recommended_portions

followed = actual_cooked <= recommended
delta_actual_vs_baseline = actual_cooked - baseline
delta_actual_pct = (delta_actual_vs_baseline / max(1, baseline)) * 100.0

if actual_cooked < baseline:
    outcome = "Waste reduction achieved"
elif actual_cooked == baseline:
    outcome = "Neutral outcome"
else:
    outcome = "Overproduction risk"

if followed and actual_cooked < baseline:
    day_status = "COUNTED"
elif followed and recommended >= baseline:
    day_status = "NEUTRAL"
else:
    day_status = "RESET"

if st.button("Submit End-of-Day Result", use_container_width=True):
    if day_status == "COUNTED":
        st.session_state.green_star_streak += 1
    elif day_status == "NEUTRAL":
        st.session_state.green_star_streak = st.session_state.green_star_streak
    else:
        st.session_state.green_star_streak = 0
    st.rerun()

if day_status == "COUNTED":
    st.success("Counted: recommendation followed and baseline reduced.")
elif day_status == "NEUTRAL":
    st.info("Neutral day: recommendation followed. Higher production was justified by demand, streak preserved.")
else:
    st.warning("Not counted: recommendation not followed, streak reset.")

c1, c2, c3 = st.columns(3)

with c1:
    st.metric(
        "Recommendation followed?",
        "Yes" if followed else "No",
        delta=f"{actual_cooked - recommended:+d} vs recommended",
    )

with c2:
    st.metric(
        "Actual vs Baseline",
        f"{actual_cooked}",
        delta=f"{delta_actual_vs_baseline:+d} portions ({delta_actual_pct:+.1f}%)",
    )

with c3:
    label = "Counted" if day_status == "COUNTED" else ("Neutral" if day_status == "NEUTRAL" else "Not counted")
    st.metric("Daily Green Star Count", label)

st.caption(
    "End-of-day feedback closes the loop between recommendation and real kitchen behavior. "
    "In production, this data is stored and used to improve future recommendations."
)

streak = int(st.session_state.green_star_streak)

st.markdown("### Green Star ⭐ Progress")
progress = min(1.0, streak / 7.0)
st.progress(progress, text=f"Streak: {streak}/7 days")

if streak >= 7:
    st.success("⭐ Green Star ACTIVE — consistent, data-backed waste reduction!")
else:
    st.info(f"Keep going. {7 - streak} more counted day(s) to activate Green Star.")
