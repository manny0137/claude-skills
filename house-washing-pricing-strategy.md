# Pricing Strategy: Door-to-Door Exterior House Washing

**Prepared by:** pricing-strategist skill (commercial/skills/pricing-strategist)
**Date:** 2026-10-15
**Scope:** Residential exterior cleaning sold mainly by knocking on doors. Covers house soft wash plus driveway/concrete, deck/fence, gutter face brightening, windows and roof add-ons.

> **How to read this.** Every price below is a **range**, not a single number. You pick one number per row for your laminated price card, and you own that choice. The ranges come from a cost floor plus a target margin, and every assumption is listed in Section 0 so you can swap in your own numbers. Section 7 explains how to move inside a range, or move the whole range, using your own close-rate data.

---

## 0. Assumptions (replace these with your numbers)

| # | Assumption | Value used | How to adjust |
|---|---|---|---|
| A1 | Market / currency | United States, USD, 2026 | Outside the US, rebuild Section 2 with local wages and chemical prices. |
| A2 | Crew | Owner-operator plus 1 helper (2 people on site) | Solo operator: labor cost per crew-hour drops to about $35, but each job takes about 1.6x as long. |
| A3 | Owner wage | **$35/hr**, counted as a job cost. Profit comes on top of this. | Use whatever you would pay someone to replace you. |
| A4 | Helper wage, burdened | **$25/hr** ($20 base plus about 25% for payroll tax and workers' comp) | Workers' comp rates for pressure washing vary a lot by state. Check yours. |
| A5 | Drive, setup and breakdown | 0.75 crew-hours per job | Tight neighborhood clustering can cut this to 0.4. |
| A6 | Wash time | 1.0 / 1.75 / 2.5 / 3.5 crew-hours for Small / Medium / Large / XL houses | Time your first 10 jobs and replace these. |
| A7 | Chemicals | About $1.25 per 100 sq ft of living area (12.5% sodium hypochlorite, surfactant, neutralizer) | Bleach prices swing. Re-check each spring. |
| A8 | Fuel | $15 per job (truck plus pump engine) | |
| A9 | Insurance | About $7,000/yr (general liability, commercial auto, workers' comp) over 250 jobs = **$28/job** | Roof work often needs a higher liability limit or a rider. |
| A10 | Equipment and vehicle | About $20k rig (soft-wash skid, 8 GPM pressure washer, surface cleaner, hoses, ladders) over 4 yrs, plus $6k/yr truck/trailer share = $11k/yr over 250 jobs = **$44/job** | |
| A11 | Maintenance and wear | $8/job | |
| A12 | Overhead | About $6,000/yr (CRM/quoting app, phone, door hangers, yard signs, licensing, bookkeeping) = **$24/job** | |
| A13 | Door-to-door acquisition cost | **$65/job**: about 2.5 knocking hours per sale at $25/hr, or a 10-15% canvasser commission | Measure it (Section 7). This is the biggest lever you control. |
| A14 | Annual volume | 250 jobs/yr (about 30 peak weeks at 8 jobs/week, plus shoulder season) | Fewer jobs means a higher fixed cost per job, so redo A9-A12. |
| A15 | Net margin target, after paying the owner wage | **25-35%** of price | |

No Van Westendorp survey data and no local competitor prices were available. Market-sanity checks use typical published US ranges for house washing, roughly $0.15-$0.35 per sq ft of living area, or $300-$600 for a typical 2,000 sq ft home. **Confirm these locally before printing the price card.** Section 7.4 shows how.

---

## 1. Pricing model: which structure to quote at the door

### Tool output: `pricing_model_picker.py`

The picker was built for SaaS, so I translated this business into its inputs. Average ticket was set to about $550. Job size varies about 3x between a small ranch and a large two-story, so the "usage-variance" signal was set high (0.70). The "seat" signal was set near zero because there are no users to count. Value drivers were curb appeal, avoided repaint/siding cost, and time saved versus DIY. Because none of the tool's industry profiles fit home services, I ran three of them to see whether the ranking held:

| Model (tool name) | What it means for house washing | saas | enterprise-software | marketplace |
|---|---|---|---|---|
| `usage_based` | Price by house size (per sq ft, banded) | **75** | **70** | **85** |
| `hybrid` | Size-banded base price + add-on menu + maintenance plan | 70 | 70 | 70 |
| `value_based` | Price against the avoided repaint/siding cost | 50 | 60 | 60 |
| `subscription_seat_based` | Flat recurring fee regardless of house size | 55 | 50 | 35 |
| `freemium` | Free wash to win the customer | 55 | 40 | 55 |

Size-based pricing ranks first under every profile, and hybrid is a consistent second. The tool raised one trade-off for hybrid: "small deal size, so hybrid complexity is not worth the friction". That warning matters a lot at a doorstep, and the recommendation below is shaped around it.

### Recommendation: size-banded tiers + a short add-on menu + an optional plan

| Option | Speed at the door | Accuracy | Verdict |
|---|---|---|---|
| **Per sq ft (raw)** | Slow. You need a measurement or Zillow lookup, and odd numbers like $467.40 invite haggling. | High | Use it only behind the scenes, to build the tiers and to quote houses over 4,500 sq ft. |
| **House-size tiers (banded sq ft)** | **Fast.** Eyeball the house or check county records/Zillow on your phone in about 20 seconds, then read the card. | Good enough. Banding error is about 10%. | **Primary model.** |
| **Flat Good/Better/Best packages** | Fast | Ignores size, so you lose margin on big houses | **Present packages on top of the tiers.** The package price scales with the house tier. |
| **Per hour** | Unknown until the job is done, and homeowners distrust it | Accurate for cost | **Never quote it to customers.** Use it only as an internal KPI (revenue per crew-hour). |

The tool's "value-based" score stays low because you cannot measure value per house. Use value as a **talking point** rather than a pricing method: "Algae eats paint, and repainting this house runs $6-12k."

---

## 2. Cost floor, break-even and target margin

### 2.1 Worked example: Medium house (2,000 sq ft, 2-story vinyl)

| Cost line | Calculation | $ / job |
|---|---|---|
| Labor | (0.75 setup + 1.75 wash) crew-hrs x $60/crew-hr (owner $35 + helper $25) | 150 |
| Chemicals | 2,000 sq ft x $1.25/100 | 25 |
| Fuel | A8 | 15 |
| Insurance | $7,000 / 250 jobs | 28 |
| Equipment + vehicle amortization | $11,000 / 250 jobs | 44 |
| Maintenance / wear | A11 | 8 |
| Overhead (software, signs, hangers, licensing) | $6,000 / 250 jobs | 24 |
| Door-to-door acquisition | A13 | 65 |
| **Fully loaded break-even (owner already paid $35/hr)** | | **$359** |
| Price at 25% net margin | 359 / 0.75 | **$479** |
| Price at 30% net margin | 359 / 0.70 | $513 |
| Price at 35% net margin | 359 / 0.65 | $552 |

**Formula:** `Price = Fully loaded cost / (1 - target net margin)`

At $479, the direct costs (labor, chemicals and fuel, $190 total) are about 40% of price. That is a healthy gross margin of roughly 60% for exterior cleaning.

### 2.2 Floor for every tier (same model)

| Tier | Crew-hrs | Break-even | 25% margin | 35% margin | Revenue per crew-hr at 25% |
|---|---|---|---|---|---|
| Small (calculated at 1,300 sq ft) | 1.75 | $305 | $407 | $469 | $232 |
| Medium (2,000) | 2.50 | $359 | $479 | $552 | $191 |
| Large (3,000) | 3.25 | $417 | $556 | $642 | $171 |
| XL (4,000) | 4.25 | $489 | $652 | $752 | $153 |

### 2.3 Minimum job charge

A job with a 30-minute wash still carries about $229 in fixed costs: drive, setup, insurance, equipment, overhead and acquisition. Floor: 0.75 + 0.5 crew-hrs, plus $10 of chemicals, plus fixed costs = **$269**.

- **Minimum job charge: $299-$349.** This applies to any visit, including add-on-only jobs such as "just the driveway".
- **Neighbor jobs** have almost no acquisition or drive cost. A Medium neighbor job costs about **$294** instead of $359. That $65 saving is what pays for the neighbor discount in Section 4.

### 2.4 Tool check: `packaging_designer.py` loss-leader test

I ran the Good package (House Wash, with costs scaled into $200 units) at two prices:

- **At $479:** no loss-leader flag.
- **At $429** (a "competitive" low price): flag. `Good tier near loss-leader: cost-to-serve (1.9) > 80% of price (2.15). Either raise the price floor or strip a feature down to Better.`

**Rule:** do not set the Medium House Wash list price below about **$475** unless your measured costs are lower than assumed here.

### 2.5 If the local market will not pay these prices

If competitors routinely sell a Medium house at $300-$350, **the problem is your cost structure, not your price.** Fix cost before cutting price:

1. Cut acquisition cost with **street clustering**. Knock only within about 5 blocks of a booked job.
2. Cut drive time by stacking 3-4 jobs per street per day.
3. Raise the add-on attach rate so the visit's ticket, not the base wash, carries the margin.

---

## 3. Price sheet (laminated card)

### 3.1 House wash by size

Prices include siding, eaves, soffits, a window rinse, exterior light fixtures and the front entry. The list range spans a 25% to 35% net margin.

| Tier | Living area | List price range | Walk-away floor (Section 4.6) |
|---|---|---|---|
| Small | Up to 1,500 sq ft | **$399-$469** | $359 |
| Medium | 1,501-2,500 sq ft | **$479-$549** | $422 |
| Large | 2,501-3,500 sq ft | **$549-$649** | $491 |
| XL | 3,501-4,500 sq ft | **$649-$749** | $575 |
| Estate | 4,500+ sq ft | Custom quote at $0.17-$0.20/sq ft, never below $749 | Cost model required |

**Modifiers.** Add a flat amount instead of re-tiering:

- 3 stories, steep grade or a walk-out basement: **+$75-$150**
- Heavy mildew or black algae, or more than 3 years since the last wash: **+$50-$100**
- Oxidized/chalky paint or rust stains: **separate quote**. Do not promise results at the door.
- Stucco, Dryvit/EIFS, brick or wood siding: same tier price; low-pressure soft wash only.

**Choosing a number inside the range.** Start your card around the 40th percentile of each range for the first 4-6 weeks, for example Medium at about $499. Then follow the Section 7 rules. Market check: $499 / 2,000 sq ft = $0.25/sq ft, which is upper-middle of the typical US band. You are charging for convenience and neighbor proof.

### 3.2 Add-on menu

Add-on prices apply when the add-on is booked with a house wash. On its own, the minimum job charge applies.

| Add-on | Price range | Notes |
|---|---|---|
| Driveway surface clean (2-car, about 600 sq ft) | **$129-$179** ($0.15-$0.25/sq ft above 600) | **The upgrade trigger.** A clean house next to a dirty driveway sells itself. |
| Front walkway / sidewalk | $49-$79 | Use as a "free" close incentive (cost about $10-20) |
| Patio (up to 300 sq ft) | $99-$149 | |
| Gutter face brightening (removes "tiger stripes") | $1.00-$1.75 per linear ft; typical home **$149-$249** | Hand work, so price it high enough |
| Gutter clean-out (debris) | $129-$229 | Offer only if you carry the ladder risk |
| Deck soft wash (up to 300 sq ft) | **$149-$299** ($0.50-$0.85/sq ft above that) | Composite vs wood: same price, different chemicals |
| Fence wash | $1.25-$2.25 per linear ft per side | Sell "street-facing side only" as the entry option |
| Exterior window detail | $6-$10 per pane | |
| Trash/recycling bin clean and deodorize | $15-$25 per bin | Cheap impulse add-on |
| Screen enclosure / pool cage | $199-$399 | |
| **Roof soft wash** | $0.35-$0.60 per sq ft of roof; typical **$450-$900** | **Separate quote, never bundled.** Confirm insurance covers roof work, use a fall-protection plan, no pressure on shingles. |

### 3.3 Good / Better / Best packages

Prices below are for a Medium house. For other sizes, scale by tier: take the house-wash list price, then add the bundle.

| | **Good: House Wash** | **Better: Curb Appeal** (anchor here) | **Best: Whole-Home Refresh** |
|---|---|---|---|
| House soft wash, eaves, soffits, window rinse, entry and fixtures | Yes | Yes | Yes |
| Driveway surface clean | | **Yes (upgrade trigger)** | Yes |
| Front walkway | | Yes | Yes (all walkways) |
| Gutter face brightening | | Yes | Yes |
| Deck **or** patio wash | | | **Yes (upgrade trigger)** |
| Exterior window detail | | | Yes |
| Fence, street side (up to 100 lf) | | | Yes |
| 6-month touch-up rinse guarantee | | | Yes |
| A-la-carte value | $479-$549 | about $810-$1,050 | about $1,200-$1,780 |
| **Package price range** | **$479-$549** | **$649-$799** (about 20% below a-la-carte) | **$949-$1,199** (about 20-33% below a-la-carte) |

### 3.4 Tool output: `packaging_designer.py`

Run with the `prosumer` profile and 3 segments (Budget/one-time, Curb-appeal/listing, Whole-home maintainers).

The tool placed every feature in the same tier as the table above. It raised one flag:

> `No clear upgrade trigger Good → Better: Better-tier features have lower avg importance than Good. Why would a Good customer ever upgrade?`

This flag is structural: for a homeowner, the house wash itself will always be the most important item. The fix is in how you present it, not in reshuffling features:

1. **Name one trigger per step.** Good to Better is "the driveway". Better to Best is "the deck/patio + the 6-month guarantee". Do not list five features at the door.
2. **Show it visually.** At the door, show a phone photo of a clean house next to a dirty driveway.
3. **Make the Better gap small and the saving visible.** Better costs only $170-$250 more than Good, but includes about $330-$500 of add-ons.

The feature-dump check (Best with more than 2x Better's features at less than 1.5x Better's price) and the price-to-value decoy check (Best above 2x Better's price) did **not** fire. Best is about 1.5x Better.

**Expected mix:** about 45-55% Good, 30-40% Better, 10-20% Best. If Best sells under 5%, it is too far from Better. If Good sells over 70%, the driveway trigger is not being shown.

---

## 4. Door-to-door tactics

### 4.1 Quoting on the spot (under 60 seconds)

1. Before knocking a street, look up approximate sq ft in county records or Zillow on your phone, or estimate it. One story, about 40 ft x 40 ft footprint = Medium. Two stories on the same footprint = Large.
2. Pick the tier, then apply at most one modifier (stories/grade or heavy growth).
3. **Quote the package, not the parts.** Say "For your home, Curb Appeal is $X". Then offer Good below it and Best above it.
4. Write the quote on a branded leave-behind card with a **7-day expiry**, even if they say no.
5. Use a quoting app (Jobber, Housecall Pro, ResponsiBid or similar) to text the quote with photos and online booking before you reach the next door.

### 4.2 Anchoring

- **Open with Better (the middle package)**, and mention Best first: "Most people on this street go with Curb Appeal at $X. Whole-Home is $Y if you want the deck too."
- Bring up the cost of doing nothing: "Algae eats paint. A repaint on this house runs $6-12k."
- Never open with Good or a discount. The first number they hear becomes the reference point.

### 4.3 "We're already on your street" neighbor pricing

- **Neighbor rate: 10% off** the package, for jobs booked on the same day as an existing job on that street or within about 5 houses.
- This is **funded by real savings**. There is no extra drive and acquisition cost is near zero, roughly $65-$90 saved per job. Explain it truthfully: "Because the truck is already here Thursday, I can take 10% off."
- **Block offer:** if 3 or more houses on a street book the same day, all of them get 15% (the hard cap).

### 4.4 Same-day close incentive

- Give **value, not price**: "Book today and I'll add the front walkway (or bins) free."
- The walkway costs you about $10-20 and is worth $49-$79 to the customer. That beats a $50 discount.
- Give it a real deadline: today, or before the truck leaves the street. **Never fake urgency.** Honor the quote for its stated 7 days.

### 4.5 Handling "that's too expensive"

Work through these in order and stop at the first one that works:

1. **Clarify.** "Too expensive compared to what: another quote, or the budget?" If it is another quote, ask what it includes. Many low quotes skip soffits or rinsing windows, or use pressure that damages siding.
2. **Step down, don't discount.** Move from Better to Good, or Good to "front and sides only" at the Small-tier price. Remove scope before you cut price.
3. **Prepay or plan.** "On the annual plan it's 10% less, and you never have to think about it."
4. **Neighbor rate, if it truly applies.**
5. **Walk away above the floor.** "No problem. Here's the card, and the price is good for 7 days." The leave-behind brings in late bookings.

### 4.6 Discount guardrails (non-negotiable)

| Rule | Limit |
|---|---|
| Maximum total discount off list | **15%** (neighbor + plan + prepay combined, all stacked) |
| Price discounts per job | **One** price discount plus at most **one** free add-on |
| Absolute walk-away floor | Fully loaded cost / 0.85, a 15% margin minimum: **Small $359 / Medium $422 / Large $491 / XL $575** |
| Who can go below the floor | **Owner only**, case by case, with a stated reason in the CRM (for example, a model home for a yard sign on a 100-house street). Canvassers never can. |
| Canvasser authority | List price, neighbor rate and the free walkway. Anything else goes to the owner by phone. |
| Price-matching | Match only a written quote with the same scope, never below the walk-away floor. |
| Roof work | Never discounted at the door |

At the 15% cap, a Medium house at a $513 list price sells for $436. That is 18% margin with full acquisition cost, or 33% margin as a neighbor job.

### 4.7 Referral pricing

- **Referrer:** $50 credit or a free bin clean/walkway on their next service, for each booked referral, with no cap. You can afford it because the referral replaces a $65 acquisition cost.
- **Referred neighbor:** gets the neighbor rate (10%). Credits **do not stack** above the 15% cap.
- **Yard sign:** $25-$50 off for 7-14 days of a yard sign after the job. This is the cheapest door-opener you will find.

---

## 5. Recurring revenue: maintenance plans

Algae and mildew come back in 12-24 months, so most homes need a wash every 1-2 years. Plans turn a $65 acquisition into several years of revenue, and they let you schedule work into slow weeks.

| Plan | What's included | Discount | Medium-house price range | Billing |
|---|---|---|---|---|
| **Annual Care** | 1 package visit per year, booked in your low-demand window | **10% off list** | House Wash $431-$494 per year; Curb Appeal $584-$719 per year | Card on file, auto-renew, 30-day reminder |
| **Twice-a-Year Care** | Spring full package + fall light rinse with driveway/walk refresh | **15% off** spring visit; fall visit $179-$249 | About **$586-$716 per year** (House Wash base) | Per visit, or monthly |
| **Monthly option** | Annual value divided by 12, 12-month commitment | Same as above | Annual Curb Appeal: about **$49-$60/mo** | Auto-pay |
| **Prepay** | Pay the full year upfront | **Extra 5%**, staying within the 15% total cap | | |

**Guardrails for plans:**

- Plan discounts count toward the 15% cap.
- Lock this year's price for 12 months, then raise **3-7% at renewal** with 30 days' notice.
- Target: 25-40% of new customers on a plan by the end of year one.
- Track renewal rate. Below 70% means the second visit is not showing visible value.

---

## 6. Seasonal and demand-based adjustments

Typical seasons for the US (adjust for your climate). Most soft-wash chemicals need temperatures above freezing, ideally 50°F or warmer.

| Season | Typical months | Pricing posture |
|---|---|---|
| **Peak** | Late March-June, September-October | Full list price. No same-day price discounts (only value add-ons). Neighbor rate still applies. |
| **Shoulder** | July-August (hot South: adjust), early November | Lean on the neighbor rate and plan sign-ups. Free add-ons for booking in "open slots this week". |
| **Off-season** | November/December-February (North) | Sell **"Spring Prebook"**: lock this year's price plus **10% off** for prepay, scheduled in the first spring weeks. Sell gutter clean-outs and holiday-light work if you offer them. |

**Fill-based rules** (backlog = how far ahead you are booked):

- Backlog over **3 weeks**: raise new quotes **5-10%** (move toward the top of the range) and stop all price discounts except the neighbor rate.
- Backlog under **1 week** during peak: increase knocking, not discounting. Use the free-add-on close.
- **Never lower the printed list price mid-season.** Use value add-ons instead. Cutting list price trains your street to wait for deals.

---

## 7. KPIs and how they move price

### 7.1 Funnel metrics: track daily, review weekly

| KPI | Definition | Healthy starting band (assumed) |
|---|---|---|
| Doors per knocking hour | Doors knocked / hours knocked | 25-40 |
| Contact rate | Doors answered / doors knocked | 25-40% (best in evenings and Saturdays) |
| Quote rate | Quotes given / conversations | 40-60% |
| **Close rate per conversation** | Jobs booked / conversations | **10-25%** |
| Close rate per quote | Jobs booked / quotes | 25-45% (count late bookings from the leave-behind) |
| Sales per knocking hour | Jobs / knocking hours | 0.3-0.6, which gives your real acquisition cost |
| **Average ticket** | Revenue / jobs | Target **$600-$750** on a Medium-heavy mix |
| **Add-on attach rate** | Jobs with at least 1 add-on / jobs | 40-60%; driveway alone 35-50% |
| Package mix | % Good / Better / Best | About 50 / 35 / 15 |
| **Revenue per crew-hour** | Job revenue / on-site crew-hours | **$150-$250**. Below $150 means you are under-priced or slow. |
| Acquisition cost per job | Knocking cost + materials / jobs | Under $65 (A13) |
| Discount depth | Average % off list | Under 7%. Over 10% means the guardrails are leaking. |
| Plan attach / renewal | % new customers on a plan / % renewing | 25-40% / over 70% |

### 7.2 Price-change rules

Apply these only after **at least 50 conversations or 30 quotes** in a period. Below that, the numbers are noise.

| Signal | Likely meaning | Action |
|---|---|---|
| Close rate per quote **over 50%** for 2+ weeks, with discount depth under 5% | Under-priced | Raise list **5-10%**, or move to the top of the range |
| Backlog over 3 weeks | Demand exceeds capacity | Raise 5-10% on new quotes |
| Close rate per quote **under 20%**, but contact and quote rates are healthy | Price, or price presentation | First check that you are anchoring on Better and showing the driveway photo. If still low after 2 weeks, test a step down to the bottom of the range. **Never go below the floor.** |
| Close rate is low **and** quote rate is low | Targeting or pitch problem, not price | Change neighborhoods, timing or opener. Do not touch price. |
| Revenue per crew-hour under $150 | Job time is above assumption, or price is too low | Re-time jobs. Raise tiers where hours exceed A6. |
| Add-on attach under 30% | Packages are not being presented | Retrain on the anchor script before changing prices |
| Discount depth over 10% | Guardrail leak | Remove canvasser discount authority |
| Annual cost check (each January) | Inflation in chemicals, insurance, fuel | Re-run Section 2 and raise **3-7%** |

### 7.3 A/B testing at the door

Alternate streets of similar home value. Quote Medium Curb Appeal at the bottom of the range on one street and at the top on the next, for about 30 quotes each. If the close rate drops less than about 15% at the higher price, the higher price earns more revenue per hour of knocking. Keep it.

### 7.4 Willingness-to-pay check (Van Westendorp)

**This has not been run. There is no survey data, and I did not invent any.** I confirmed `wtp_analyzer.py` accepts the format below using a 5-row placeholder file. The tool correctly warned `Sample size N=5 is below 30 ... directional only`.

To collect real data, ask after a "no" at the door, or by text after a quote:

1. At what price would a house wash for your home seem **so cheap you'd doubt the quality**?
2. At what price would it be **a bargain**?
3. At what price would it start to feel **expensive, but you'd still consider it**?
4. At what price is it **too expensive to consider**?

Then:

- Collect **at least 30 answers per house-size tier**; 100 is better.
- Save them as `{"respondents":[{"too_cheap":..,"bargain":..,"getting_expensive":..,"too_expensive":..}]}`.
- Run: `python3 commercial/skills/pricing-strategist/scripts/wtp_analyzer.py --input survey.json --output markdown`
- If the resulting Range of Acceptable Prices sits below your Section 2 floor, the fix is cost (Section 2.5), not a lower price.

---

## 8. Door script (price presentation)

> **Opener:** "Hi, I'm [Name] with [Company]. We're washing the [Smiths'] house at [#] on Thursday, so the truck's already on your street. Have you noticed the green on the north side of your siding?"
>
> **Problem/value:** "That's algae. It slowly eats paint and caulk. A soft wash kills it at the root, with no high pressure on your siding, and it stays clean a lot longer than a pressure-wash rinse."
>
> **Anchor (Better first, mention Best):** "For a home your size, most neighbors are going with our **Curb Appeal** package: house, driveway, front walk and gutter faces for **$[Better price]**. If you want the back deck and windows done too, **Whole-Home** is **$[Best price]**. Or just the house is **$[Good price]**."
>
> *(Show phone: clean house next to dirty driveway.)* "This is why most people add the driveway. A clean house makes the driveway look worse."
>
> **Neighbor + same-day close:** "Since we're already here Thursday, I can give you the neighbor rate, 10% off. And if you book now, I'll do the front walkway free."
>
> **If "too expensive":** "Totally fair. Is that compared to another quote, or just more than you planned? ... We could do just the house for $[Good], or put you on the annual plan, which takes another 10% off and you never have to think about it."
>
> **Close / leave-behind:** "Want me to put you down for Thursday morning or afternoon?" *(If no:)* "No problem. Here's your quote, good for 7 days. Text that number and I'll fit you in."

---

## 9. Summary decision (for the owner to approve)

| Decision | Recommendation | Owner to decide |
|---|---|---|
| Model | Size-banded tiers + add-on menu + G/B/B packages + optional plan (hybrid) | Confirm |
| Medium house wash list | **$479-$549** range; start about $499 | Pick the printed number |
| Minimum job | **$299-$349** | Pick |
| Packages (Medium) | Good $479-$549 / Better $649-$799 / Best $949-$1,199 | Pick |
| Discount cap | 15% stacked; walk-away floors per tier | Approve |
| Plans | Annual 10%, twice-a-year 15%, prepay extra 5%, renew at +3-7% | Approve |
| Price reviews | Weekly KPI review; change price only after 50 conversations or 30 quotes | Approve |

**Who signs off:** the business owner sets the printed prices and the discount cap. Your insurance agent should confirm coverage before you offer roof soft washing, and your accountant should confirm the cost assumptions (A3-A14) against your actual books after the first 20-30 jobs.
