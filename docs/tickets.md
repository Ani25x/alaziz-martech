# Tickets written for the Al Aziz build

How marketing requests are handed to whoever builds them: a user story, why it matters, and a clear definition of done.

---

### AAZ-01 · Add a partial-COD option at checkout
**Priority:** High · **Type:** Conversion fix

**User story:** As a first-time buyer who doesn't trust a new brand yet, I want to pay a small amount now and the rest on delivery, so I don't risk the full price.

**Why:** The first ₹15,000 Meta test produced 116 add-to-carts but only 4 orders (3.4% cart-to-order). Prepaid-only checkout plus low brand trust is the likely cause.

**Acceptance criteria**
- [ ] Checkout offers "Pay ₹99 now, rest on delivery" alongside full prepaid
- [ ] The ₹99 is collected via Razorpay; order is marked with a `partial_cod` tag
- [ ] Full-prepaid option shows a small incentive (e.g. free shipping) so it stays the default choice
- [ ] Purchase event fires once, with the full order value, for both options
- [ ] Return-to-origin rate for `partial_cod` orders is visible in a weekly report

---

### AAZ-02 · Send Purchase and AddToCart through Meta Conversions API
**Priority:** High · **Type:** Tracking

**User story:** As the person running ads, I want server-side events alongside the Pixel, so Meta optimises on complete data even when browsers block tracking.

**Acceptance criteria**
- [ ] Purchase, InitiateCheckout, AddToCart and ViewContent sent from the server
- [ ] Browser and server events share an `event_id`; Events Manager shows them deduplicated
- [ ] Hashed email and phone sent where the customer gave them
- [ ] Event Match Quality for Purchase is "Good" or better
- [ ] Test order shows exactly one Purchase in Events Manager

---

### AAZ-03 · Show reviews and trust signals on product pages
**Priority:** Medium · **Type:** Conversion fix

**User story:** As a visitor from an ad, I want proof that real people bought and liked this, so I feel safe buying from a brand I've just discovered.

**Why:** The shop has a 5.0★ rating from 35 Google reviews, but none of it is visible online. Customers say "long-lasting" and "premium" in those reviews, which matches the ads' promise.

**Acceptance criteria**
- [ ] Star rating and 3 review quotes under the price on every product page
- [ ] Trust row above the "Add to cart" button: secure payment, delivery time, easy returns line
- [ ] Mobile layout checked on a 360px-wide screen; nothing pushes the button below the fold
- [ ] A/B test: 50/50 split, sample size set in advance with a calculator (at low traffic this may take weeks), primary metric add-to-cart → purchase rate; no stopping early
