"""
EconLab economic simulation model.
Linear approximation of how policy variables affect key economic indicators.
Supports adjustable coefficients for advanced users.
"""

import pandas as pd

DEFAULT_COEFFICIENTS = {
    # GDP growth coefficients
    "gdp_spending": 0.3,        # government spending change effect
    "gdp_interest": -0.2,       # interest rate effect
    "gdp_income_tax": -0.1,     # income tax effect
    "gdp_vat": -0.05,           # VAT effect
    # Inflation coefficients
    "infl_spending": 0.1,
    "infl_interest": -0.3,
    "infl_vat": 0.1,
    "infl_income_tax": -0.05,
    # Unemployment coefficients
    "unemp_spending": -0.1,
    "unemp_interest": 0.2,
    "unemp_income_tax": 0.1,
    "unemp_vat": 0.02,
    # Real wage growth coefficients
    "wage_gdp_growth": 0.15,     # effect of GDP growth change
    "wage_inflation": -0.2,      # effect of inflation change
    "wage_spending": 0.1,
    "wage_interest": -0.05,
}

def load_baseline(country: str) -> dict:
    """Load baseline economic indicators for a given country from data.csv."""
    df = pd.read_csv("data.csv")
    if country not in df["country"].values:
        raise ValueError(f"Country {country} not found in data.csv")
    row = df[df["country"] == country].iloc[0]
    return {
        "gdp_growth": float(row["base_gdp_growth"]),
        "inflation": float(row["base_inflation"]),
        "unemployment": float(row["base_unemployment"]),
        "real_wage_growth": float(row["base_real_wage_growth"]),
    }

def simulate_economy(country: str, params: dict, coefficients: dict = None) -> dict:
    """
    Simulate economy based on policy parameters and optional model coefficients.
    """
    base = load_baseline(country)
    coeff = coefficients if coefficients is not None else DEFAULT_COEFFICIENTS

    # Extract policy parameters
    interest_rate = params.get("interest_rate", 0.0)
    income_tax = params.get("income_tax", 0.0)
    vat = params.get("vat", 0.0)
    gov_spending_change = params.get("gov_spending_change", 0.0)  # percent

    # GDP growth
    gdp_growth = (
        base["gdp_growth"]
        + coeff["gdp_spending"] * gov_spending_change
        + coeff["gdp_interest"] * interest_rate
        + coeff["gdp_income_tax"] * income_tax
        + coeff["gdp_vat"] * vat
    )

    # Inflation
    inflation = (
        base["inflation"]
        + coeff["infl_spending"] * gov_spending_change
        + coeff["infl_interest"] * interest_rate
        + coeff["infl_vat"] * vat
        + coeff["infl_income_tax"] * income_tax
    )

    # Unemployment
    unemployment = (
        base["unemployment"]
        + coeff["unemp_spending"] * gov_spending_change
        + coeff["unemp_interest"] * interest_rate
        + coeff["unemp_income_tax"] * income_tax
        + coeff["unemp_vat"] * vat
    )

    # Real wage growth
    real_wage_growth = (
        base["real_wage_growth"]
        + coeff["wage_gdp_growth"] * (gdp_growth - base["gdp_growth"])
        + coeff["wage_inflation"] * (inflation - base["inflation"])
        + coeff["wage_spending"] * gov_spending_change
        + coeff["wage_interest"] * interest_rate
    )

    # Ensure values are within reasonable bounds
    gdp_growth = max(-5.0, min(15.0, gdp_growth))
    inflation = max(-2.0, min(20.0, inflation))
    unemployment = max(1.0, min(30.0, unemployment))
    real_wage_growth = max(-5.0, min(10.0, real_wage_growth))

    # Calculate changes from baseline
    changes = {
        "gdp_growth_change": gdp_growth - base["gdp_growth"],
        "inflation_change": inflation - base["inflation"],
        "unemployment_change": unemployment - base["unemployment"],
        "real_wage_growth_change": real_wage_growth - base["real_wage_growth"],
    }

    results = {
        "gdp_growth": gdp_growth,
        "inflation": inflation,
        "unemployment": unemployment,
        "real_wage_growth": real_wage_growth,
        **changes,
    }
    return results
