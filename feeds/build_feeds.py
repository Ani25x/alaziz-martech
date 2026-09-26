"""
Build and validate product feeds for Google Merchant Center and Meta Commerce Manager
from ONE source sheet (feeds/products.csv).

Why one source: prices, stock and titles drift when each channel is edited by hand.
Here the sheet is the single source of truth; both feeds are generated from it and
checked before upload.

Usage:
    python feeds/build_feeds.py
    python feeds/build_feeds.py --site https://alazizparfums.com

Output:
    output/google_merchant_feed.csv
    output/meta_catalog_feed.csv
    output/feed_issues.csv        (anything that would get a product disapproved or hurt performance)
"""
import argparse
import re
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "feeds" / "products.csv"
OUT = ROOT / "output"

BRAND = "Al Aziz Parfums"
GOOGLE_CATEGORY = "Health & Beauty > Personal Care > Cosmetics > Perfume & Cologne"
HERO_SKUS = {"Bomb Bae", "Millionaire", "Qahwa Royale"}   # the only SKUs sent to cold traffic

# Unit-economics inputs (ex-GST), same as economics/unit_economics.py
GST = 0.18
PACKAGING, COURIER, GATEWAY = 17, 59, 20

# Other brands' names in titles/descriptions can trigger counterfeit / trademark
# disapprovals on Google and Meta. "Inspired by" stays in an internal column only.
THIRD_PARTY_TERMS = [
    "creed", "aventus", "dior", "sauvage", "chanel", "ysl", "yves saint laurent", "opium",
    "armani", "versace", "tom ford", "gucci", "prada", "lattafa", "khamrah", "afnan", "rasasi",
    "paco rabanne", "1 million", "jean paul gaultier", "hugo boss", "bvlgari", "davidoff",
    "dupe", "inspired by", "replica", "clone", "copy of", "first copy",
]


def contribution(price_incl_gst: float, cost_incl_gst: float) -> float:
    revenue_ex = price_incl_gst / (1 + GST)
    cogs_ex = cost_incl_gst / (1 + GST)
    return revenue_ex - (cogs_ex + PACKAGING + COURIER + GATEWAY)


def margin_tier(c: float) -> str:
    if pd.isna(c):
        return "unknown"
    return "high_margin" if c >= 450 else "mid_margin" if c >= 400 else "low_margin"


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def make_title(r) -> str:
    family = f" {r.fragrance_family} " if r.fragrance_family else " "
    notes = ", ".join([n for n in [first(r.top_notes), first(r.base_notes)] if n])
    notes = f" ({notes})" if notes else ""
    return f"{BRAND.split()[0]} {BRAND.split()[1]} {r['name']}{family}Eau de Parfum {int(r.size_ml)}ml{notes}".replace("  ", " ")


def first(notes: str) -> str:
    return notes.split(",")[0].strip().title() if notes else ""


def make_description(r) -> str:
    if r.description:
        return r.description
    parts = [f"{r['name']} is a {r.fragrance_family.lower() or 'signature'} eau de parfum, {int(r.size_ml)}ml,"
             " blended by hand in small batches in Navi Mumbai."]
    if r.top_notes:
        parts.append(f"Top notes: {r.top_notes}.")
    if r.heart_notes:
        parts.append(f"Heart: {r.heart_notes}.")
    if r.base_notes:
        parts.append(f"Base: {r.base_notes}.")
    parts.append("Oil-rich formula built for long wear.")
    return " ".join(parts)


def validate(feed: pd.DataFrame) -> pd.DataFrame:
    issues = []

    def add(r, field, severity, msg):
        issues.append({"id": r["id"], "product": r.get("_name", ""), "field": field, "severity": severity, "issue": msg})

    for _, r in feed.iterrows():
        for f in ["title", "description", "link", "image_link", "price", "availability"]:
            if not str(r[f]).strip():
                add(r, f, "disapproval", "required field is empty")
        if not r["_name"]:
            add(r, "title", "disapproval", "product name missing in products.csv")
        if len(r["title"]) > 150:
            add(r, "title", "disapproval", f"title is {len(r['title'])} chars (max 150)")
        elif len(r["title"]) < 35:
            add(r, "title", "performance", "short title - add family / key notes so it matches more searches")
        if len(r["description"]) > 5000:
            add(r, "description", "disapproval", "description over 5000 chars")
        for f in ["link", "image_link"]:
            if r[f] and not str(r[f]).startswith("https://"):
                add(r, f, "disapproval", "must be a full https:// URL")
        text = f"{r['title']} {r['description']}".lower()
        hits = [t for t in THIRD_PARTY_TERMS if re.search(rf"\b{re.escape(t)}\b", text)]
        if hits:
            add(r, "title/description", "policy risk",
                f"mentions {', '.join(hits)} - other brands' names can trigger counterfeit/trademark disapprovals")
        if r["custom_label_1"] == "unknown":
            add(r, "custom_label_1", "data", "cost price missing - margin tier can't be set")
        if r["_stock"] == "":
            add(r, "availability", "data", "stock_qty missing - defaulted to in stock; wrong stock = ad spend on items you can't ship")
    return pd.DataFrame(issues, columns=["id", "product", "field", "severity", "issue"])


def build(site: str):
    src = pd.read_csv(SRC, dtype=str).fillna("")
    src["size_ml"] = pd.to_numeric(src["size_ml"], errors="coerce").fillna(60)
    src["price_inr"] = pd.to_numeric(src["price_inr"], errors="coerce")
    src["cost_price_inr"] = pd.to_numeric(src["cost_price_inr"], errors="coerce")

    rows = []
    for _, r in src.iterrows():
        stock = r.stock_qty.strip()
        in_stock = (stock == "") or (int(float(stock)) > 0)
        c = contribution(r.price_inr, r.cost_price_inr) if pd.notna(r.cost_price_inr) else float("nan")
        link = r.product_url or (f"{site}/product/{slug(r['name'])}/" if r["name"] else "")
        rows.append({
            "id": r.sku_id,
            "title": make_title(r) if r["name"] else "",
            "description": make_description(r) if r["name"] else "",
            "link": link,
            "image_link": r.image_url,
            "price": f"{r.price_inr:.2f} INR",
            "availability": "in_stock" if in_stock else "out_of_stock",
            "brand": BRAND,
            "condition": "new",
            "google_product_category": GOOGLE_CATEGORY,
            "product_type": f"Perfume > {r.fragrance_family or 'Eau de Parfum'}",
            "size": f"{int(r.size_ml)} ml",
            "identifier_exists": "no",                        # no GTIN/barcode on house-made products
            "custom_label_0": "hero" if r["name"] in HERO_SKUS else "core",
            "custom_label_1": margin_tier(c),
            "custom_label_2": slug(r.fragrance_family) if r.fragrance_family else "unassigned",
            "_name": r["name"],
            "_stock": stock,
        })
    feed = pd.DataFrame(rows)
    issues = validate(feed)

    OUT.mkdir(exist_ok=True)
    google = feed.drop(columns=["_name", "_stock"])
    google.to_csv(OUT / "google_merchant_feed.csv", index=False)

    meta = google.rename(columns={"product_type": "product_type"}).copy()
    meta["availability"] = meta["availability"].str.replace("_", " ")       # Meta uses "in stock"
    meta = meta.drop(columns=["identifier_exists", "size"])
    meta.to_csv(OUT / "meta_catalog_feed.csv", index=False)

    issues.to_csv(OUT / "feed_issues.csv", index=False)

    print(f"Products: {len(feed)}  |  hero: {(feed.custom_label_0 == 'hero').sum()}")
    print("Margin tiers:", feed["custom_label_1"].value_counts().to_dict())
    if issues.empty:
        print("No issues. Ready to upload.")
    else:
        print(f"\n{len(issues)} issues found -> output/feed_issues.csv")
        print(issues.groupby("severity").size().to_string())
        pr = issues[issues.severity == "policy risk"]
        for _, i in pr.iterrows():
            print(f"  POLICY RISK  {i['product']}: {i['issue']}")


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--site", default="https://alazizparfums.com")
    build(p.parse_args().site)
