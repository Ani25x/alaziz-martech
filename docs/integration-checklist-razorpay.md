# Integration checklist: Razorpay on WooCommerce

How the payment gateway was chosen, set up and checked before go-live. The same template works for any new marketing or commerce platform.

## 1. Evaluation
| Option | Why considered | Decision |
|---|---|---|
| Direct UPI (QR / UPI ID) | Zero fees | Rejected: no automatic order confirmation, manual reconciliation, no cards |
| Razorpay | UPI, cards, netbanking and wallets in one checkout; WooCommerce plugin; webhooks | **Chosen** |

Trade-off accepted: ~2.5% gateway fee (≈ ₹20 per ₹799 order, ex-GST) in exchange for automatic confirmation and every payment method in one place.

## 2. Setup
- [ ] KYC and business verification in the Razorpay dashboard (GST-registered business)
- [ ] Install the official Razorpay plugin for WooCommerce; add Key ID and Key Secret from **live** mode, not test mode
- [ ] Set the webhook URL in Razorpay → Settings → Webhooks, events: `payment.captured`, `payment.failed`, `refund.processed`
- [ ] Payment methods shown: UPI first (most-used in India), then cards, netbanking, wallets
- [ ] Checkout copy: show accepted methods and "secure payment" on the checkout page

## 3. Data flow
```
Customer pays on Razorpay  →  webhook  →  WooCommerce order: "Processing"
                                            ├─ order email to customer
                                            ├─ Meta Pixel + Conversions API: Purchase (value, currency, event_id)
                                            ├─ GA4: purchase (transaction_id = order number)
                                            └─ courier booking (Shri Maruti)
```

## 4. Go-live checks
- [ ] ₹1 live test payment by UPI and by card → order moves to "Processing" by itself
- [ ] Failed payment leaves order at "Pending payment" and doesn't fire a Purchase event
- [ ] Purchase appears once (not twice) in Meta Events Manager and GA4 DebugView
- [ ] Order value in Meta and GA4 matches the WooCommerce order total
- [ ] Refund from WooCommerce reaches Razorpay and the customer
- [ ] Settlement lands in the bank account on the expected cycle

## 5. After go-live
- Weekly: compare WooCommerce orders with Razorpay captured payments and Meta/GA4 purchases. Any gap above ~10% means tracking is broken.
