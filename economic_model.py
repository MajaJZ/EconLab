"""
EconLab economic simulation model.
Linear approximation of how policy variables affect key economic indicators.
"""

import pandas as pd

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

def simulate_economy(country: str, params: dict) -> dict:
    """
    Simulate economy based on policy parameters.
    """
    base = load_baseline(country)

    interest_rate = params.get("interest_rate", 0.0)
    income_tax = params.get("income_tax", 0.0)
    vat = params.get("vat", 0.0)
    gov_spending_change = params.get("gov_spending_change", 0.0)  # percent

    gdp_growth = (
        base["gdp_growth"]
        + 0.3 * gov_spending_change
        - 0.2 * interest_rate
        - 0.1 * income_tax
        - 0.05 * vat
    )

    inflation = (
        base["inflation"]
        + 0.1 * gov_spending_change
        - 0.3 * interest_rate
        + 0.1 * vat
        - 0.05 * income_tax
    )

    unemployment = (
        base["unemployment"]
        - 0.1 * gov_spending_change
        + 0.2 * interest_rate
        + 0.1 * income_tax
        + 0.02 * vat
    )

    real_wage_growth = (
        base["real_wage_growth"]
        + 0.15 * (gdp_growth - base["gdp_growth"])
        - 0.2 * (inflation - base["inflation"])
        + 0.1 * gov_spending_change
        - 0.05 * interest_rate
    )

    gdp_growth = max(-5.0, min(15.0, gdp_growth))
    inflation = max(-2.0, min(20.0, inflation))
    unemployment = max(1.0, min(30.0, unemployment))
    real_wage_growth = max(-5.0, min(10.0, real_wage_growth))

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
