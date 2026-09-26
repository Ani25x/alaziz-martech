# UTM naming convention

Every link that leaves our hands gets tagged the same way, so GA4 reports group cleanly and nobody has to guess what `fb / paid / test2` meant.

## Rules
- Lowercase only, words joined with `-`. No spaces, no `_`, no emojis.
- Five parameters, always in this order.
- One spreadsheet ("UTM builder") is the only place links are made. No hand-typed UTMs.

| Parameter | What it answers | Allowed values |
|---|---|---|
| `utm_source` | Where the click came from | `facebook`, `instagram`, `google`, `whatsapp`, `email`, `influencer-<handle>` |
| `utm_medium` | What kind of traffic | `paid-social`, `cpc`, `shopping`, `organic-social`, `crm`, `referral` |
| `utm_campaign` | Which campaign | `<yyyymm>-<objective>-<offer>` e.g. `202609-conv-bundle2` |
| `utm_content` | Which ad / creative | `<format>-<hook>-<sku>` e.g. `reel-ugc-qahwaroyale` |
| `utm_term` | Audience or keyword | `broad`, `lal-purchasers`, `retarget-atc-7d`, or the keyword |

## Examples
```
https://alazizparfums.com/product/qahwa-royale/?utm_source=instagram&utm_medium=paid-social&utm_campaign=202609-conv-single&utm_content=reel-ugc-qahwaroyale&utm_term=broad

https://alazizparfums.com/?utm_source=whatsapp&utm_medium=crm&utm_campaign=202610-winback-coupon100&utm_content=day12-reminder
```

## Meta dynamic parameters
In Meta Ads Manager → URL parameters, use Meta's placeholders so every ad is tagged automatically:
```
utm_source={{site_source_name}}&utm_medium=paid-social&utm_campaign={{campaign.name}}&utm_content={{ad.name}}&utm_term={{adset.name}}
```
This only works if campaign, ad set and ad **names** follow the same lowercase-hyphen format above.
