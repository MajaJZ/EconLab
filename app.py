import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
from economic_model import simulate_economy, load_baseline

st.set_page_config(
    page_title="EconLab",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    .main-title {
        text-align: center;
        font-size: 48px;
        font-weight: bold;
        letter-spacing: 3px;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        font-size: 20px;
        color: #666;
        margin-bottom: 30px;
    }
    .result-label {
        font-weight: bold;
        font-size: 18px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="main-title">ECONLAB</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">EXPERIMENT WITH THE ECONOMY</div>', unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    country = st.selectbox(
        "Choose your starting economy",
        ["Poland", "Germany", "USA"],
        index=0,
        help="Select a country to use its baseline economic indicators.",
    )

baseline = load_baseline(country)
st.write(f"**Baseline indicators for {country}:**")
st.write(
    f"GDP growth: {baseline['gdp_growth']:.1f}% | Inflation: {baseline['inflation']:.1f}% | "
    f"Unemployment: {baseline['unemployment']:.1f}% | Real wage growth: {baseline['real_wage_growth']:.1f}%"
)

st.markdown("---")

# ---------------- CHALLENGE MODE ----------------
st.subheader("Challenge Mode")
if "challenge" not in st.session_state:
    st.session_state.challenge = None

col_challenge1, col_challenge2, col_challenge3 = st.columns([1,1,1])
with col_challenge1:
    if st.button("Generate Challenge"):
        # Random target ranges based on baseline
        target_gdp = round(random.uniform(baseline["gdp_growth"] + 1.0, baseline["gdp_growth"] + 3.0), 1)
        target_inflation = round(random.uniform(max(0.5, baseline["inflation"] - 1.5), baseline["inflation"] + 0.5), 1)
        target_unemployment = round(random.uniform(max(1.0, baseline["unemployment"] - 2.0), baseline["unemployment"] - 0.5), 1)
        st.session_state.challenge = {
            "gdp_growth": target_gdp,
            "inflation": target_inflation,
            "unemployment": target_unemployment,
        }
        st.success("New challenge generated!")

if st.session_state.challenge:
    ch = st.session_state.challenge
    st.write(f"**Target GDP growth:** ≥ {ch['gdp_growth']}%")
    st.write(f"**Target inflation:** ≤ {ch['inflation']}%")
    st.write(f"**Target unemployment:** ≤ {ch['unemployment']}%")
else:
    st.write("Click **Generate Challenge** to get your targets.")

st.markdown("---")

# ---------------- POLICY SLIDERS ----------------
st.subheader("Your Policy")
col1, col2, col3, col4 = st.columns(4)

with col1:
    interest_rate = st.slider(
        "Interest rate (%)",
        min_value=0.0,
        max_value=15.0,
        value=4.25,
        step=0.05,
        help="Set by the central bank. Higher rates cool inflation but may hurt growth.",
    )

with col2:
    income_tax = st.slider(
        "Income tax (%)",
        min_value=0.0,
        max_value=50.0,
        value=19.0,
        step=0.5,
        help="Direct tax on household income. Higher taxes reduce disposable income.",
    )

with col3:
    vat = st.slider(
        "VAT (%)",
        min_value=0.0,
        max_value=30.0,
        value=23.0,
        step=0.5,
        help="Value-added tax. Higher VAT increases prices and reduces consumption.",
    )

with col4:
    gov_spending_change = st.slider(
        "Government spending change (%)",
        min_value=-10.0,
        max_value=10.0,
        value=2.0,
        step=0.1,
        help="Percentage change from baseline government spending. Positive values are expansionary.",
    )

run_button = st.button("RUN EXPERIMENT", use_container_width=True)

st.markdown("---")
st.subheader("Results")

if run_button:
    params = {
        "interest_rate": interest_rate,
        "income_tax": income_tax,
        "vat": vat,
        "gov_spending_change": gov_spending_change,
    }
    results = simulate_economy(country, params)
    st.session_state["results"] = results

if "results" in st.session_state:
    res = st.session_state["results"]

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="result-label">GDP Growth</div>', unsafe_allow_html=True)
        progress = (res["gdp_growth"] + 5) / 20
        st.progress(min(1.0, max(0.0, progress)))
        st.write(f"**{res['gdp_growth']:.1f}%**")
        change = res["gdp_growth_change"]
        st.write(f"({'+' if change >= 0 else ''}{change:.1f}% vs baseline)")

    with col2:
        st.markdown('<div class="result-label">Inflation</div>', unsafe_allow_html=True)
        progress = (res["inflation"] + 2) / 22
        st.progress(min(1.0, max(0.0, progress)))
        st.write(f"**{res['inflation']:.1f}%**")
        change = res["inflation_change"]
        st.write(f"({'+' if change >= 0 else ''}{change:.1f}% vs baseline)")

    with col3:
        st.markdown('<div class="result-label">Unemployment</div>', unsafe_allow_html=True)
        progress = (res["unemployment"] - 1) / 29
        st.progress(min(1.0, max(0.0, progress)))
        st.write(f"**{res['unemployment']:.1f}%**")
        change = res["unemployment_change"]
        st.write(f"({'+' if change >= 0 else ''}{change:.1f}% vs baseline)")

    with col4:
        st.markdown('<div class="result-label">Real Wage Growth</div>', unsafe_allow_html=True)
        progress = (res["real_wage_growth"] + 5) / 15
        st.progress(min(1.0, max(0.0, progress)))
        st.write(f"**{res['real_wage_growth']:.1f}%**")
        change = res["real_wage_growth_change"]
        st.write(f"({'+' if change >= 0 else ''}{change:.1f}% vs baseline)")

    # ---------------- SCORING ----------------
    if st.session_state.challenge:
        ch = st.session_state.challenge
        score = 0.0
        # GDP: target is >= ch['gdp_growth']
        if res["gdp_growth"] >= ch["gdp_growth"]:
            score += 40.0
        else:
            # partial score
            score += 40.0 * max(0.0, res["gdp_growth"] / ch["gdp_growth"]) if ch["gdp_growth"] > 0 else 40.0

        # Inflation: target is <= ch['inflation']
        if res["inflation"] <= ch["inflation"]:
            score += 30.0
        else:
            score += 30.0 * max(0.0, ch["inflation"] / res["inflation"]) if res["inflation"] > 0 else 0.0

        # Unemployment: target is <= ch['unemployment']
        if res["unemployment"] <= ch["unemployment"]:
            score += 30.0
        else:
            score += 30.0 * max(0.0, ch["unemployment"] / res["unemployment"]) if res["unemployment"] > 0 else 0.0

        score = round(min(100.0, score), 1)
        st.markdown("---")
        st.subheader("🎯 Challenge Score")
        st.write(f"**Your score: {score}/100**")
        if score >= 80:
            st.success("Excellent! You hit almost all targets.")
        elif score >= 60:
            st.warning("Good effort, but you could improve some indicators.")
        else:
            st.error("Your policy missed most targets. Try different settings!")

    st.markdown("---")
    st.subheader("Visual Comparison")
    metrics = ["GDP Growth", "Inflation", "Unemployment", "Real Wage Growth"]
    baseline_vals = [
        baseline["gdp_growth"],
        baseline["inflation"],
        baseline["unemployment"],
        baseline["real_wage_growth"],
    ]
    result_vals = [
        res["gdp_growth"],
        res["inflation"],
        res["unemployment"],
        res["real_wage_growth"],
    ]

    df = pd.DataFrame(
        {"Metric": metrics, "Baseline": baseline_vals, "Your Policy": result_vals}
    )
    df.set_index("Metric", inplace=True)
    st.bar_chart(df, height=400)
else:
    st.info("Adjust the policy sliders and click **RUN EXPERIMENT** to see the effects.")

st.markdown("---")
st.subheader("Explanations of the Economics")
st.markdown(
    """
- **Interest Rate**: Controlled by the central bank. Higher interest rates tend to reduce borrowing and spending, slowing down inflation but potentially increasing unemployment and decreasing GDP.
- **Income Tax**: Direct taxes on household income. Higher income taxes reduce disposable income, leading to lower consumer spending and cooling down economic growth.
- **Government Spending**: An injection into the circular flow of income. Increased government spending boosts aggregate demand, raising GDP and potentially lowering unemployment, though it can spark inflation.
- **VAT (Value Added Tax)**: A consumption tax. Higher VAT increases the cost of goods and services, which can dampen consumer demand and influence the inflation rate.
"""
)
