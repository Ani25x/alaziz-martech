"""
Unit economics per product and per offer, plus a check of the real campaign against them.

All costs are GST-exclusive (GST is a pass-through for a GST-registered seller).
Meta reports revenue including GST, so break-even ROAS here = GST-inclusive price / contribution.

Usage:
    python economics/unit_economics.py

Reads:  feeds/products.csv, economics/campaign_results.csv
Output: output/unit_economics.csv
"""
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
GST = 0.18
PACKAGING, COURIER, GATEWAY = 17, 59, 20          # ex-GST, per order
KILL_GATES = {"ctr": 1.2, "cpc": 15, "cvr": 1.8, "cac": 550}

# Offers: (label, price incl GST, bottles). Courier/packaging/gateway charged once per order.
OFFERS = [
    ("Single bottle", 799, 1),
    ("Order bump: 2nd bottle at 599", 799 + 599, 2),
    ("Bundle of 2", 1399, 2),
    ("Bundle of 3", 1999, 3),
]


def contribution(price_incl, cogs_incl_total):
    return price_incl / (1 + GST) - (cogs_incl_total / (1 + GST) + PACKAGING + COURIER + GATEWAY)


def per_sku(products: pd.DataFrame) -> pd.DataFrame:
    p = products.dropna(subset=["cost_price_inr"]).copy()
    p["contribution_inr"] = p.apply(lambda r: contribution(r.price_inr, r.cost_price_inr), axis=1).round(0)
    p["margin_pct"] = (p["contribution_inr"] / (p["price_inr"] / (1 + GST)) * 100).round(0)
    p["breakeven_roas"] = (p["price_inr"] / p["contribution_inr"]).round(2)
    p["max_cac_inr"] = p["contribution_inr"]
    return p[["name", "cost_price_inr", "contribution_inr", "margin_pct", "breakeven_roas", "max_cac_inr"]] \
        .sort_values("contribution_inr", ascending=False)


def per_offer(avg_cost: float) -> pd.DataFrame:
    rows = []
    for label, price, n in OFFERS:
        c = contribution(price, avg_cost * n)
        rows.append({"offer": label, "price_inr": price, "contribution_inr": round(c),
                     "breakeven_roas": round(price / c, 2)})
    return pd.DataFrame(rows)


def campaign_check(path: Path):
    m = pd.read_csv(path).set_index("metric")["value"]
    m = pd.to_numeric(m, errors="coerce")
    g = lambda k: m.get(k)
    lines = []

    def rate(name, num, den, gate=None, higher_is_better=True, pct=True):
        if pd.isna(num) or pd.isna(den) or den == 0:
            lines.append(f"  {name:<24} (fill campaign_results.csv)")
            return
        v = num / den * (100 if pct else 1)
        verdict = ""
        if gate is not None:
            ok = v >= gate if higher_is_better else v <= gate
            verdict = f"  {'PASS' if ok else 'FAIL'} vs gate {gate}"
        lines.append(f"  {name:<24} {v:,.2f}{'%' if pct else ''}{verdict}")

    rate("CTR", g("link_clicks"), g("impressions"), KILL_GATES["ctr"])
    rate("CPC (INR)", g("spend_inr"), g("link_clicks"), KILL_GATES["cpc"], higher_is_better=False, pct=False)
    rate("Click -> landing page", g("landing_page_views"), g("link_clicks"))
    rate("LPV -> add to cart", g("add_to_carts"), g("landing_page_views"))
    rate("Add to cart -> checkout", g("checkouts_initiated"), g("add_to_carts"))
    rate("Checkout -> purchase", g("purchases"), g("checkouts_initiated"))
    rate("Add to cart -> purchase", g("purchases"), g("add_to_carts"))
    rate("CVR (click -> purchase)", g("purchases"), g("link_clicks"), KILL_GATES["cvr"])
    rate("CAC (INR)", g("spend_inr"), g("purchases"), KILL_GATES["cac"], higher_is_better=False, pct=False)
    rev = g("revenue_inr")
    if pd.isna(rev) and not pd.isna(g("purchases")):
        rev = g("purchases") * 799
        lines.append(f"  (revenue not filled - assuming {int(g('purchases'))} single bottles x 799)")
    rate("ROAS (x)", rev, g("spend_inr"), None, pct=False)
    return lines


if __name__ == "__main__":
    products = pd.read_csv(ROOT / "feeds" / "products.csv")
    sku = per_sku(products)
    avg_cost = sku["cost_price_inr"].mean()
    offers = per_offer(avg_cost)

    (ROOT / "output").mkdir(exist_ok=True)
    sku.to_csv(ROOT / "output" / "unit_economics.csv", index=False)

    print(f"Per product ({len(sku)} with cost price filled):")
    print(sku.to_markdown(index=False))
    print(f"\nPer offer (average cost price INR {avg_cost:.0f}):")
    print(offers.to_markdown(index=False))
    print("\nReal campaign vs kill-gates:")
    print("\n".join(campaign_check(ROOT / "economics" / "campaign_results.csv")))
