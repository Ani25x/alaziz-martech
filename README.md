# Al Aziz Parfums: taking an offline perfumer online

The marketing and tech stack I built for **Al Aziz Parfums** ([alazizparfums.com](https://alazizparfums.com)), a single-shop artisan perfumer in Navi Mumbai: store, payments, tracking, product feeds, unit economics and the first paid campaign. Everything here is from the live project.

## The starting point
- 5.0★ from 35 Google reviews offline, **zero online sales**
- ₹60,000 already spent on an agency (website + ads) with no results
- 14 hand-blended 60ml eau de parfums plus a discovery set, low social following, no customer list
- Owner's goal: ₹7 lakh revenue in year one from online

## What I built
| Area | What | Where |
|---|---|---|
| Store | WooCommerce store built with Claude as a coding partner; guest checkout, account creation after purchase | live site |
| Payments | Razorpay (UPI, cards, netbanking, wallets) with webhook-driven order status | [integration checklist](docs/integration-checklist-razorpay.md) |
| Tracking | GA4 + Meta Pixel + Conversions API, both live (event match quality 6.1/10); one UTM convention | [UTM convention](docs/utm-convention.md) |
| Product feeds | One product sheet → Google Merchant Center + Meta catalog feeds, with custom labels and pre-upload validation | [`feeds/`](feeds/) |
| Unit economics | GST-adjusted contribution, break-even ROAS and max CAC per product and per offer | [`economics/`](economics/) |
| Creative | AI image pipeline (Claude writes prompts, Gemini renders) for the full catalogue, no photoshoot | live site |
| Specs | Changes written as tickets with acceptance criteria | [tickets](docs/tickets.md) |

## The numbers that shaped the strategy
Run `python economics/unit_economics.py`:

- Break-even ROAS on a single ₹799 bottle: **~1.7–2.1x** depending on the product's cost
- Profit per single bottle (**₹381–475**) is **below** typical fragrance D2C acquisition costs on Meta (**₹600+**)
- So one bottle per order can't pay for a new customer. The offer has to raise order value: **order bump (2nd bottle at ₹599)** and **2- and 3-bottle bundles** nearly double contribution per order
- Only the 3 highest-margin, best-reviewed products go to cold traffic (`custom_label_0 = hero`)

## First campaign: what happened
| Metric | Result |
|---|---|
| Meta spend | ₹15,000 |
| Add to carts | 116 |
| Purchases | 4 |
| Add to cart → purchase | 3.4% |
| Cost per order | ₹3,750 (kill-gate was ₹550) |

**Diagnosis:** people wanted the product (116 add-to-carts) but didn't complete checkout. Two causes:
1. **No cash on delivery.** Prepaid-only was chosen to avoid return-to-origin losses (~₹140 per failed COD delivery), but for an unknown brand it blocked buyers.
2. **Low trust.** The 5-star offline reputation wasn't visible anywhere on the site.

**Next test:** partial COD (₹99 upfront) and reviews + trust signals on product pages. See tickets [AAZ-01](docs/tickets.md) and [AAZ-03](docs/tickets.md).

## Product feeds
`python feeds/build_feeds.py` turns [`feeds/products.csv`](feeds/products.csv) into both feeds and checks them before upload:

- **Custom labels:** `hero` / `core`, `high_margin` / `mid_margin` / `low_margin` (from actual cost price), fragrance family. These let campaigns bid more on high-margin hero products.
- **Validation:** empty required fields, title length, https links, missing stock or cost
- **Policy check:** flags other brands' names in titles or descriptions. The products are inspired by famous fragrances, but naming those brands in ads can get products disapproved for counterfeit or trademark reasons. The inspiration stays in an internal column and never reaches the feed. The check caught one product whose own name contains a designer fragrance name.

## What I learned
- Tracking and offer design matter more than ad settings. The campaign found demand; the checkout lost it.
- A decision that's right on paper (prepaid-only to avoid returns) can be wrong for a brand nobody knows yet. Test it instead of assuming.
- Keep one source of truth for product data. Prices and stock drift when each channel is edited by hand.

## Run it
```bash
pip install -r requirements.txt
python feeds/build_feeds.py
python economics/unit_economics.py
```
