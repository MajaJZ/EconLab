import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import random
from economic_model import simulate_economy, load_baseline, DEFAULT_COEFFICIENTS

# Page setup
st.set_page_config(
    page_title="EconLab",
    page_icon="🏛️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
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
    .tooltip {
        position: relative;
        display: inline-block;
        cursor: help;
        border-bottom: 1px dotted #999;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: #555;
        color: #fff;
        text-align: center;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        bottom: 125%;
        left: 50%;
        margin-left: -100px;
        opacity: 0;
        transition: opacity 0.3s;
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
        opacity: 1;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Header
st.markdown('<div class="main-title">ECONLAB</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">EXPERIMENT WITH THE ECONOMY</div>', unsafe_allow_html=True)

# Initialize session state for results, challenge, lesson, coefficients
for key in ["results", "challenge", "lesson_mode", "coeffs"]:
    if key not in st.session_state:
        st.session_state[key] = None if key not in ["coeffs"] else DEFAULT_COEFFICIENTS.copy()

# ---- SCENARIO DEFINITIONS ----
SCENARIOS = {
    "None (normal)": {
        "baseline_override": None,
        "targets": None,
        "description": "Standard baseline data from the country file.",
        "narrative": "",
    },
    "COVID-19 Recession": {
        "baseline_override": {
            "gdp_growth": -2.0,
            "inflation": 1.0,
            "unemployment": 9.0,
            "real_wage_growth": -1.0,
        },
        "targets": {
            "gdp_growth": 2.0,       # target >= 2%
            "inflation": 2.5,        # target <= 2.5%
            "unemployment": 6.0,     # target <= 6%
        },
        "description": "A severe global recession. GDP is shrinking, unemployment is high.",
        "narrative": "The economy is in freefall. Your goal is to stimulate growth without letting inflation run wild.",
    },
    "Overheating Boom": {
        "baseline_override": {
            "gdp_growth": 6.0,
            "inflation": 8.0,
            "unemployment": 2.0,
            "real_wage_growth": 4.0,
        },
        "targets": {
            "gdp_growth": 3.0,
            "inflation": 3.0,
            "unemployment": 4.0,
        },
        "description": "The economy is growing too fast, causing high inflation.",
        "narrative": "Inflation is out of control. Try to cool the economy without causing a recession.",
    },
    "Stagflation": {
        "baseline_override": {
            "gdp_growth": 0.5,
            "inflation": 7.0,
            "unemployment": 8.0,
            "real_wage_growth": -2.0,
        },
        "targets": {
            "gdp_growth": 2.0,
            "inflation": 3.0,
            "unemployment": 6.0,
        },
        "description": "High inflation and high unemployment simultaneously.",
        "narrative": "The worst of both worlds. Can you break the cycle?",
    },
}

# ---- SIDEBAR: Scenario, Lesson, Coefficients ----
with st.sidebar:
    st.header("Options")
    scenario_name = st.selectbox(
        "Scenario",
        list(SCENARIOS.keys()),
        help="Choose a predefined economic scenario to simulate.",
    )
    scenario = SCENARIOS[scenario_name]

    # Lesson mode toggle
    lesson_mode = st.checkbox("Lesson Mode", value=False,
                              help="Turn on guided instructions. Some sliders will be locked.")
    st.session_state.lesson_mode = lesson_mode

    # Adjustable coefficients (advanced)
    with st.expander("Advanced: Model Coefficients", expanded=False):
        st.write("Change how strongly each policy affects the economy.")
        coeffs = st.session_state.coeffs
        # We'll create sliders for each coefficient. For simplicity, group them.
        st.markdown("**GDP growth**")
        coeffs["gdp_spending"] = st.slider("Spending effect on GDP", -1.0, 1.0, coeffs["gdp_spending"], 0.05)
        coeffs["gdp_interest"] = st.slider("Interest effect on GDP", -1.0, 1.0, coeffs["gdp_interest"], 0.05)
        coeffs["gdp_income_tax"] = st.slider("Income tax effect on GDP", -1.0, 1.0, coeffs["gdp_income_tax"], 0.05)
        coeffs["gdp_vat"] = st.slider("VAT effect on GDP", -1.0, 1.0, coeffs["gdp_vat"], 0.05)

        st.markdown("**Inflation**")
        coeffs["infl_spending"] = st.slider("Spending effect on inflation", -1.0, 1.0, coeffs["infl_spending"], 0.05)
        coeffs["infl_interest"] = st.slider("Interest effect on inflation", -1.0, 1.0, coeffs["infl_interest"], 0.05)
        coeffs["infl_vat"] = st.slider("VAT effect on inflation", -1.0, 1.0, coeffs["infl_vat"], 0.05)
        coeffs["infl_income_tax"] = st.slider("Income tax effect on inflation", -1.0, 1.0, coeffs["infl_income_tax"], 0.05)

        st.markdown("**Unemployment**")
        coeffs["unemp_spending"] = st.slider("Spending effect on unemployment", -1.0, 1.0, coeffs["unemp_spending"], 0.05)
        coeffs["unemp_interest"] = st.slider("Interest effect on unemployment", -1.0, 1.0, coeffs["unemp_interest"], 0.05)
        coeffs["unemp_income_tax"] = st.slider("Income tax effect on unemployment", -1.0, 1.0, coeffs["unemp_income_tax"], 0.05)
        coeffs["unemp_vat"] = st.slider("VAT effect on unemployment", -1.0, 1.0, coeffs["unemp_vat"], 0.05)

        st.markdown("**Real wage growth**")
        coeffs["wage_gdp_growth"] = st.slider("GDP growth effect on wages", -1.0, 1.0, coeffs["wage_gdp_growth"], 0.05)
        coeffs["wage_inflation"] = st.slider("Inflation effect on wages", -1.0, 1.0, coeffs["wage_inflation"], 0.05)
        coeffs["wage_spending"] = st.slider("Spending effect on wages", -1.0, 1.0, coeffs["wage_spending"], 0.05)
        coeffs["wage_interest"] = st.slider("Interest effect on wages", -1.0, 1.0, coeffs["wage_interest"], 0.05)

        if st.button("Reset coefficients to default"):
            st.session_state.coeffs = DEFAULT_COEFFICIENTS.copy()
            st.experimental_rerun()

# ---- MAIN AREA ----
# Country selection (unless scenario overrides baseline)
if scenario["baseline_override"] is None:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        country = st.selectbox(
            "Choose your starting economy",
            ["Poland", "Germany", "USA"],
            index=0,
            help="Select a country to use its baseline economic indicators.",
        )
    baseline = load_baseline(country)
else:
    country = "Scenario"
    baseline = scenario["baseline_override"]
    st.info(f"Using scenario baseline: {scenario['description']}")

# Display baseline
st.write(f"**Baseline indicators for {country}:**")
st.write(
    f"GDP growth: {baseline['gdp_growth']:.1f}% | Inflation: {baseline['inflation']:.1f}% | "
    f"Unemployment: {baseline['unemployment']:.1f}% | Real wage growth: {baseline['real_wage_growth']:.1f}%"
)

if scenario["narrative"]:
    st.markdown(f"*{scenario['narrative']}*")

st.markdown("---")

# ---- CHALLENGE / TARGETS ----
st.subheader("Challenge Mode")
if "challenge" not in st.session_state:
    st.session_state.challenge = None

# If scenario has predefined targets, use them; otherwise allow random generation
if scenario["targets"] is not None:
    st.session_state.challenge = scenario["targets"]
    st.write("This scenario has fixed targets:")
    ch = st.session_state.challenge
    st.write(f"**GDP growth ≥ {ch['gdp_growth']}%**")
    st.write(f"**Inflation ≤ {ch['inflation']}%**")
    st.write(f"**Unemployment ≤ {ch['unemployment']}%**")
else:
    col_ch1, col_ch2, col_ch3 = st.columns([1,1,1])
    with col_ch1:
        if st.button("Generate Challenge"):
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

# ---- LESSON MODE ----
if st.session_state.lesson_mode:
    st.subheader("📚 Lesson Mode")
    st.markdown("""
    **Goal:** Learn how to control inflation without causing a recession.
    
    1. Set the **interest rate** high (e.g., 8–10%) – this reduces inflation but may increase unemployment.
    2. Lower **government spending** to a negative value (e.g., -2%) – also cools the economy.
    3. Keep **income tax** moderate (around 20%) to avoid reducing demand too much.
    4. Set **VAT** to 15% or lower – lower VAT reduces prices directly.
    
    Try to keep unemployment below 6% while getting inflation below 3%.
    """)
    # Lock some sliders to guide the user (we can't actually disable them easily, but we can set defaults)
    st.info("For this lesson, the following starting values are suggested (adjust them if you wish):")
    interest_rate = st.slider("Interest rate (%)", 0.0, 15.0, 8.0, 0.05)
    income_tax = st.slider("Income tax (%)", 0.0, 50.0, 20.0, 0.5)
    vat = st.slider("VAT (%)", 0.0, 30.0, 15.0, 0.5)
    gov_spending_change = st.slider("Government spending change (%)", -10.0, 10.0, -2.0, 0.1)
else:
    # ---- POLICY SLIDERS ----
    st.subheader("Your Policy")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        interest_rate = st.slider("Interest rate (%)", min_value=0.0, max_value=15.0, value=4.25, step=0.05,
                                  help="Set by the central bank. Higher rates cool inflation but may hurt growth.")
    with col2:
        income_tax = st.slider("Income tax (%)", min_value=0.0, max_value=50.0, value=19.0, step=0.5,
                               help="Direct tax on household income. Higher taxes reduce disposable income.")
    with col3:
        vat = st.slider("VAT (%)", min_value=0.0, max_value=30.0, value=23.0, step=0.5,
                        help="Value-added tax. Higher VAT increases prices and reduces consumption.")
    with col4:
        gov_spending_change = st.slider("Government spending change (%)", min_value=-10.0, max_value=10.0, value=2.0, step=0.1,
                                        help="Percentage change from baseline government spending. Positive values are expansionary.")

run_button = st.button("RUN EXPERIMENT", use_container_width=True)

# ---- RESULTS ----
st.markdown("---")
st.subheader("Results")

if run_button:
    params = {
        "interest_rate": interest_rate,
        "income_tax": income_tax,
        "vat": vat,
        "gov_spending_change": gov_spending_change,
    }
    results = simulate_economy(country if scenario["baseline_override"] is None else "Scenario", params, st.session_state.coeffs)
    st.session_state["results"] = results

if "results" in st.session_state:
    res = st.session_state["results"]

    col1, col2, col3, col4 = st.columns(4)

    # Helper to display metric with tooltip
    def show_metric(label, value, change, tooltip_text, progress_range, progress_value):
        with col1 if label == "GDP Growth" else col2 if label == "Inflation" else col3 if label == "Unemployment" else col4:
            st.markdown(f'<div class="result-label">{label} <span class="tooltip">?<span class="tooltiptext">{tooltip_text}</span></span></div>', unsafe_allow_html=True)
            progress = (progress_value - progress_range[0]) / (progress_range[1] - progress_range[0])
            st.progress(min(1.0, max(0.0, progress)))
            st.write(f"**{value:.1f}%**")
            st.write(f"({'+' if change >= 0 else ''}{change:.1f}% vs baseline)")

    show_metric("GDP Growth", res["gdp_growth"], res["gdp_growth_change"],
                "Gross Domestic Product growth rate. Higher is generally better, but too high can cause inflation.",
                (-5, 15), res["gdp_growth"])
    show_metric("Inflation", res["inflation"], res["inflation_change"],
                "General increase in prices. Central banks typically target around 2%.",
                (-2, 20), res["inflation"])
    show_metric("Unemployment", res["unemployment"], res["unemployment_change"],
                "Percentage of labor force without jobs. Lower is better, but very low can lead to wage inflation.",
                (1, 30), res["unemployment"])
    show_metric("Real Wage Growth", res["real_wage_growth"], res["real_wage_growth_change"],
                "Increase in wages adjusted for inflation. Positive means workers' purchasing power is rising.",
                (-5, 10), res["real_wage_growth"])

    # Scoring (same as before, but adapted if challenge exists)
    if st.session_state.challenge:
        ch = st.session_state.challenge
        score = 0.0
        if res["gdp_growth"] >= ch["gdp_growth"]:
            score += 40.0
        else:
            score += 40.0 * max(0.0, res["gdp_growth"] / ch["gdp_growth"]) if ch["gdp_growth"] > 0 else 40.0
        if res["inflation"] <= ch["inflation"]:
            score += 30.0
        else:
            score += 30.0 * max(0.0, ch["inflation"] / res["inflation"]) if res["inflation"] > 0 else 0.0
        if res["unemployment"] <= ch["unemployment"]:
            score += 30.0
        else:
            score += 30.0 * max(0.0, ch["unemployment"] / res["unemployment"]) if res["unemployment"] > 0 else 0.0
        score = round(min(100.0, score), 1)
        st.markdown("---")
        st.subheader("Challenge Score")
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
    baseline_vals = [baseline["gdp_growth"], baseline["inflation"], baseline["unemployment"], baseline["real_wage_growth"]]
    result_vals = [res["gdp_growth"], res["inflation"], res["unemployment"], res["real_wage_growth"]]

    df = pd.DataFrame({"Metric": metrics, "Baseline": baseline_vals, "Your Policy": result_vals})
    df.set_index("Metric", inplace=True)
    st.bar_chart(df, height=400)
else:
    st.info("Adjust the policy sliders and click **RUN EXPERIMENT** to see the effects.")

st.markdown("---")
st.subheader("Explanations of the Economics")
st.markdown("""
- **Interest Rate**: Controlled by the central bank. Higher interest rates tend to reduce borrowing and spending, slowing down inflation but potentially increasing unemployment and decreasing GDP.
- **Income Tax**: Direct taxes on household income. Higher income taxes reduce disposable income, leading to lower consumer spending and cooling down economic growth.
- **Government Spending**: An injection into the circular flow of income. Increased government spending boosts aggregate demand, raising GDP and potentially lowering unemployment, though it can spark inflation.
- **VAT (Value Added Tax)**: A consumption tax. Higher VAT increases the cost of goods and services, which can dampen consumer demand and influence the inflation rate.
""")
