# SMS Campaign Revenue Decline — Analysis Results

**Data:** 1,784 row-level observations (Jan 27 – Feb 16, 2026) across 6 carriers, 3 segments, 6 phone numbers. Rows with phone number 20407 excluded.

---

## Key Finding

**Daily revenue fell 43% ($609 → $347/day) starting Feb 4, driven almost entirely (99%) by the retirement of 4 phone numbers.** The 2 remaining active numbers maintained stable revenue (~$197/day), but could not compensate for the lost capacity. A secondary factor — declining revenue per send (–27%) even on active numbers — compounds the problem.

## Descriptive Comparison: Pre-Decline (Jan 27–Feb 3) vs. Post-Decline (Feb 4–Feb 16)

| Metric | Pre-Decline | Post-Decline | Change |
|---|---|---|---|
| Daily Revenue | $608.68 | $346.63 | **–43.1%** |
| Daily Sends | 67,531 | 51,926 | –23.1% |
| Revenue / Send | 0.90¢ | 0.66¢ | **–27.0%** |
| Revenue / Click | 1.67¢ | 1.13¢ | **–32.3%** |
| Click-Through Rate | 53.9% | 59.6% | +10.6% |
| Delivery Rate | 99.6% | 99.6% | ~0% |
| Active Phone Numbers | 6 | 2 (from Feb 11) | — |

Delivery rates remained stable (~99.6%), ruling out carrier filtering or deliverability as causes. CTR actually *increased* post-decline, suggesting the audience receiving messages remained engaged — the problem is upstream of engagement.

## Revenue Decomposition

The $262/day decline decomposes into two mechanisms:

- **Volume loss** (fewer messages sent): **$141/day (54%)** — driven by 4 phone numbers going offline between Feb 5–10
- **Efficiency loss** (lower revenue per message): **$121/day (46%)** — revenue per send dropped from 0.90¢ to 0.66¢

By phone group: the 4 retired numbers account for **99.0%** of the decline ($259/day lost). The 2 active numbers declined just $2.60/day (1.0%).

## Regression Results

An OLS model on daily aggregates (R² = 0.79) confirms a strong negative time trend of **–$42/day** (p < 0.001). At the row level (N = 1,784, R² = 0.65), the significant predictors of revenue are:

| Factor | Coefficient | p-value | Interpretation |
|---|---|---|---|
| DayNum (time trend) | –0.42 | <0.001 | Revenue erodes ~$0.42/row/day |
| Clicks | +0.0015 | 0.006 | Each click generates ~$0.15¢ marginal revenue |
| Sent | +0.0018 | <0.001 | Volume drives revenue mechanically |
| Carrier: Verizon | +10.48 | <0.001 | Highest-revenue carrier by far |
| Carrier: T-Mobile | +7.66 | <0.001 | Second-highest carrier |
| Segment: New Data | –2.18 | <0.001 | Lower revenue vs. Clicker segment |
| Segment: TriggeredSend | –2.20 | <0.001 | Lower revenue vs. Clicker segment |

Verizon and T-Mobile rows generate significantly more revenue. The "Clicker" segment outperforms "New Data" and "TriggeredSend" by ~$2.20/row.

## Conclusions and Recommendations

1. **Phone number retirement is the primary cause.** Four of six numbers ceased sending by Feb 11, eliminating ~67% of send capacity and 99% of the revenue decline. Restoring or replacing these numbers is the highest-leverage action.
2. **Revenue efficiency is declining independently.** Even holding volume constant, revenue per send dropped 27%. This suggests deteriorating monetization — possibly lower ad rates, weaker job-alert conversions, or audience fatigue. This warrants investigation with the monetization/demand-side team.
3. **Verizon and T-Mobile carry the revenue.** These two carriers account for the vast majority of per-row revenue. Any carrier-level disruptions to these networks disproportionately impact total revenue.
4. **Clicker segment is the most valuable.** Prioritize send volume toward the Clicker audience segment, which generates ~$2.20 more revenue per observation than New Data or TriggeredSend.

---

*See `fig1_revenue_overview.png` and `fig2_breakdowns.png` for visualizations. Full regression output in `regression_coefficients.csv`. Analysis code in `analysis.py`.*
