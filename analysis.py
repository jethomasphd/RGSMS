"""
SMS Campaign Revenue Decline Analysis
======================================
ETL, descriptive statistics, visualizations, and regression modeling
to identify factors associated with declining SMS campaign revenue.

Data: SmsDeliveryReport.csv — daily SMS campaign metrics by carrier,
      segment, delivery type, and phone number (Jan 27 – Feb 16, 2026).

Filter: Rows where Sms Phone Number == 20407 are excluded per instructions.
"""

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import statsmodels.api as sm
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings("ignore")

# ── Styling ──────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", font_scale=1.05)
COLORS = sns.color_palette("Set2", 8)

# =====================================================================
# 1. ETL
# =====================================================================
raw = pd.read_csv("SmsDeliveryReport.csv")

# Filter out 20407 short code per instructions
df = raw[raw["Sms Phone Number"] != 20407].copy()

# Parse dates and create derived fields
df["Date"] = pd.to_datetime(df["Date"])
df["DayNum"] = (df["Date"] - df["Date"].min()).dt.days  # linear time trend

# Delivery rate at row level (guard against zero sends)
df["Delivery_Rate"] = np.where(df["Sent"] > 0, df["Delivered"] / df["Sent"], np.nan)

# Click-through rate at row level
df["CTR"] = np.where(df["Sent"] > 0, df["Clicks"] / df["Sent"], np.nan)

# Revenue per send (RPS already exists, but we recompute for consistency)
df["Rev_per_Sent"] = np.where(df["Sent"] > 0, df["Revenue"] / df["Sent"], np.nan)

# Categorize phone numbers for readability
phone_map = {v: f"Phone_{i+1}" for i, v in enumerate(sorted(df["Sms Phone Number"].unique()))}
df["Phone_Label"] = df["Sms Phone Number"].map(phone_map)

# Tag the 4 retired phones vs 2 surviving phones
retired_phones = [15122546961, 15122546963, 15122546966, 15122546967]
df["Phone_Group"] = np.where(
    df["Sms Phone Number"].isin(retired_phones), "Retired (4 numbers)", "Active (2 numbers)"
)

print(f"Rows after filtering: {len(df)}")
print(f"Date range: {df['Date'].min().date()} to {df['Date'].max().date()}")
print(f"Phone numbers: {df['Sms Phone Number'].nunique()}")

# =====================================================================
# 2. DAILY AGGREGATES (unit of analysis for trends)
# =====================================================================
daily = (
    df.groupby("Date")
    .agg(
        Revenue=("Revenue", "sum"),
        Sent=("Sent", "sum"),
        Delivered=("Delivered", "sum"),
        Clicks=("Clicks", "sum"),
        Unique_Clicks=("Unique Clicks", "sum"),
        Bounces=("Bounces", "sum"),
        Refusals=("Refusals", "sum"),
    )
    .sort_index()
)
daily["Delivery_Rate"] = daily["Delivered"] / daily["Sent"]
daily["CTR"] = daily["Clicks"] / daily["Sent"]
daily["Rev_per_Sent"] = daily["Revenue"] / daily["Sent"]
daily["Rev_per_Click"] = daily["Revenue"] / daily["Clicks"].replace(0, 1)
daily["DayNum"] = (daily.index - daily.index.min()).days

# =====================================================================
# 3. DESCRIPTIVE STATISTICS
# =====================================================================
print("\n" + "=" * 60)
print("DESCRIPTIVE STATISTICS — Daily Totals")
print("=" * 60)

# Split into pre-decline (Jan 27 – Feb 3) and post-decline (Feb 4+)
cutoff = pd.Timestamp("2026-02-04")
pre = daily[daily.index < cutoff]
post = daily[daily.index >= cutoff]

desc_table = pd.DataFrame({
    "Pre-Decline Mean": pre[["Revenue", "Sent", "Delivered", "Clicks",
                              "Delivery_Rate", "CTR", "Rev_per_Sent"]].mean(),
    "Post-Decline Mean": post[["Revenue", "Sent", "Delivered", "Clicks",
                                "Delivery_Rate", "CTR", "Rev_per_Sent"]].mean(),
})
desc_table["Pct Change"] = (
    (desc_table["Post-Decline Mean"] - desc_table["Pre-Decline Mean"])
    / desc_table["Pre-Decline Mean"]
    * 100
)
print(desc_table.round(4))

# Phone-group revenue comparison
print("\n--- Revenue by Phone Group (Daily Totals) ---")
pg = (
    df.groupby(["Date", "Phone_Group"])["Revenue"]
    .sum()
    .unstack(fill_value=0)
)
for g in pg.columns:
    print(f"\n{g}:")
    pre_g = pg.loc[pg.index < cutoff, g]
    post_g = pg.loc[pg.index >= cutoff, g]
    print(f"  Pre-decline avg:  ${pre_g.mean():.2f}/day")
    print(f"  Post-decline avg: ${post_g.mean():.2f}/day")
    chg = (post_g.mean() - pre_g.mean()) / pre_g.mean() * 100
    print(f"  Change:           {chg:+.1f}%")

# =====================================================================
# 4. VISUALIZATIONS
# =====================================================================

# --- Figure 1: Revenue trend with phase annotation ---
fig, axes = plt.subplots(2, 2, figsize=(14, 9))
fig.suptitle("SMS Campaign Revenue Decline Analysis", fontsize=14, fontweight="bold", y=0.98)

# Panel A: Daily total revenue
ax = axes[0, 0]
ax.plot(daily.index, daily["Revenue"], marker="o", markersize=4, color=COLORS[0], linewidth=2)
ax.axvline(cutoff, color="red", linestyle="--", alpha=0.7, label="Decline onset (Feb 4)")
ax.fill_betweenx([0, daily["Revenue"].max() * 1.05], daily.index.min(), cutoff,
                  alpha=0.08, color="green", label="Pre-decline")
ax.fill_betweenx([0, daily["Revenue"].max() * 1.05], cutoff, daily.index.max(),
                  alpha=0.08, color="red", label="Post-decline")
ax.set_ylabel("Daily Revenue ($)")
ax.set_title("A. Total Daily Revenue")
ax.legend(fontsize=8)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax.tick_params(axis="x", rotation=45)

# Panel B: Revenue by phone group
ax = axes[0, 1]
pg_daily = df.groupby(["Date", "Phone_Group"])["Revenue"].sum().unstack(fill_value=0)
for i, col in enumerate(pg_daily.columns):
    ax.plot(pg_daily.index, pg_daily[col], marker="o", markersize=4,
            linewidth=2, label=col, color=COLORS[i + 2])
ax.axvline(cutoff, color="red", linestyle="--", alpha=0.7)
ax.set_ylabel("Daily Revenue ($)")
ax.set_title("B. Revenue by Phone Group")
ax.legend(fontsize=8)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax.tick_params(axis="x", rotation=45)

# Panel C: Volume (Sent) vs Revenue
ax = axes[1, 0]
ax2 = ax.twinx()
ax.bar(daily.index, daily["Sent"], width=0.8, alpha=0.4, color=COLORS[3], label="Sent (vol)")
ax2.plot(daily.index, daily["Revenue"], marker="s", markersize=4, color=COLORS[1],
         linewidth=2, label="Revenue ($)")
ax.axvline(cutoff, color="red", linestyle="--", alpha=0.7)
ax.set_ylabel("Messages Sent", color=COLORS[3])
ax2.set_ylabel("Revenue ($)", color=COLORS[1])
ax.set_title("C. Send Volume vs. Revenue")
lines1, labels1 = ax.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax.legend(lines1 + lines2, labels1 + labels2, fontsize=8, loc="upper right")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax.tick_params(axis="x", rotation=45)

# Panel D: Revenue per send over time
ax = axes[1, 1]
ax.plot(daily.index, daily["Rev_per_Sent"] * 100, marker="o", markersize=4,
        color=COLORS[5], linewidth=2)
ax.axvline(cutoff, color="red", linestyle="--", alpha=0.7)
ax.set_ylabel("Revenue per Send (cents)")
ax.set_title("D. Revenue Efficiency (Rev/Send)")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax.tick_params(axis="x", rotation=45)

plt.tight_layout(rect=[0, 0, 1, 0.95])
plt.savefig("fig1_revenue_overview.png", dpi=200, bbox_inches="tight")
plt.close()
print("\nSaved: fig1_revenue_overview.png")

# --- Figure 2: Breakdowns by carrier, segment, and phone ---
fig, axes = plt.subplots(1, 3, figsize=(16, 5))
fig.suptitle("Revenue Breakdown by Key Dimensions", fontsize=13, fontweight="bold")

# Carrier
ax = axes[0]
carrier_daily = df.groupby(["Date", "Carrier Group"])["Revenue"].sum().unstack(fill_value=0)
for i, col in enumerate(carrier_daily.columns):
    ax.plot(carrier_daily.index, carrier_daily[col], linewidth=1.5, label=col)
ax.axvline(cutoff, color="red", linestyle="--", alpha=0.7)
ax.set_title("By Carrier")
ax.set_ylabel("Revenue ($)")
ax.legend(fontsize=7)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax.tick_params(axis="x", rotation=45)

# Segment
ax = axes[1]
seg_daily = df.groupby(["Date", "Segment"])["Revenue"].sum().unstack(fill_value=0)
for i, col in enumerate(seg_daily.columns):
    ax.plot(seg_daily.index, seg_daily[col], linewidth=1.5, label=col)
ax.axvline(cutoff, color="red", linestyle="--", alpha=0.7)
ax.set_title("By Segment")
ax.set_ylabel("Revenue ($)")
ax.legend(fontsize=7)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax.tick_params(axis="x", rotation=45)

# Phone
ax = axes[2]
phone_daily = df.groupby(["Date", "Phone_Label"])["Revenue"].sum().unstack(fill_value=0)
for i, col in enumerate(phone_daily.columns):
    ax.plot(phone_daily.index, phone_daily[col], linewidth=1.5, label=col)
ax.axvline(cutoff, color="red", linestyle="--", alpha=0.7)
ax.set_title("By Phone Number")
ax.set_ylabel("Revenue ($)")
ax.legend(fontsize=7)
ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d"))
ax.tick_params(axis="x", rotation=45)

plt.tight_layout()
plt.savefig("fig2_breakdowns.png", dpi=200, bbox_inches="tight")
plt.close()
print("Saved: fig2_breakdowns.png")

# =====================================================================
# 5. REGRESSION ANALYSIS
# =====================================================================
# We model row-level Revenue to identify factors associated with the decline.
# Unit of observation: carrier × segment × phone × date rows (N=2025)

print("\n" + "=" * 60)
print("REGRESSION ANALYSIS")
print("=" * 60)

# --- Model 1: OLS on daily aggregates (time trend) ---
daily_reg = daily.copy()
daily_reg["Post_Decline"] = (daily_reg.index >= cutoff).astype(int)
X1 = sm.add_constant(daily_reg[["DayNum", "Post_Decline"]])
y1 = daily_reg["Revenue"]
m1 = sm.OLS(y1, X1).fit(cov_type="HC1")
print("\n--- Model 1: Daily Revenue ~ Time Trend + Post-Decline Indicator ---")
print(m1.summary2().tables[1].to_string())
print(f"  R² = {m1.rsquared:.3f},  Adj R² = {m1.rsquared_adj:.3f}")

# --- Model 2: Row-level OLS with full feature set ---
reg_df = df.copy()
reg_df["Post_Decline"] = (reg_df["Date"] >= cutoff).astype(int)

# Encode categoricals
carrier_dummies = pd.get_dummies(reg_df["Carrier Group"], prefix="Carrier", drop_first=True)
segment_dummies = pd.get_dummies(reg_df["Segment"], prefix="Seg", drop_first=True)
phone_group_dum = pd.get_dummies(reg_df["Phone_Group"], prefix="PG", drop_first=True)

X2 = pd.concat([
    reg_df[["Sent", "Delivered", "Clicks", "Bounces", "Refusals", "DayNum", "Post_Decline"]],
    carrier_dummies,
    segment_dummies,
    phone_group_dum,
], axis=1).astype(float)

# Drop Delivered (collinear with Sent) — keep Sent + Clicks
X2 = X2.drop(columns=["Delivered"])
X2 = sm.add_constant(X2)
y2 = reg_df["Revenue"].astype(float)

m2 = sm.OLS(y2, X2).fit(cov_type="HC1")
print("\n--- Model 2: Row-Level Revenue ~ Operational + Categorical Factors ---")
print(m2.summary2().tables[1].to_string())
print(f"  R² = {m2.rsquared:.3f},  Adj R² = {m2.rsquared_adj:.3f},  N = {m2.nobs:.0f}")

# --- Model 3: Decomposing revenue decline (Blinder-Oaxaca style) ---
# Compare pre vs post: how much is volume vs efficiency?
print("\n--- Decomposition of Revenue Decline ---")
pre_df = df[df["Date"] < cutoff]
post_df = df[df["Date"] >= cutoff]
n_pre_days = pre_df["Date"].nunique()
n_post_days = post_df["Date"].nunique()

pre_avg_rev = pre_df["Revenue"].sum() / n_pre_days
post_avg_rev = post_df["Revenue"].sum() / n_post_days
total_decline = post_avg_rev - pre_avg_rev

pre_avg_sent = pre_df["Sent"].sum() / n_pre_days
post_avg_sent = post_df["Sent"].sum() / n_post_days
pre_rps = pre_avg_rev / pre_avg_sent
post_rps = post_avg_rev / post_avg_sent

# Decomposition: ΔRev = ΔVolume × RPS_pre + ΔEfficiency × Vol_post
volume_effect = (post_avg_sent - pre_avg_sent) * pre_rps
efficiency_effect = (post_rps - pre_rps) * post_avg_sent

# Revenue from retired vs active phones
pre_retired_rev = pre_df[pre_df["Sms Phone Number"].isin(retired_phones)]["Revenue"].sum() / n_pre_days
post_retired_rev = post_df[post_df["Sms Phone Number"].isin(retired_phones)]["Revenue"].sum() / n_post_days
retired_effect = post_retired_rev - pre_retired_rev

pre_active_rev = pre_df[~pre_df["Sms Phone Number"].isin(retired_phones)]["Revenue"].sum() / n_pre_days
post_active_rev = post_df[~post_df["Sms Phone Number"].isin(retired_phones)]["Revenue"].sum() / n_post_days
active_effect = post_active_rev - pre_active_rev

print(f"  Pre-decline daily avg revenue:  ${pre_avg_rev:.2f}")
print(f"  Post-decline daily avg revenue: ${post_avg_rev:.2f}")
print(f"  Total daily decline:            ${total_decline:.2f} ({total_decline/pre_avg_rev*100:.1f}%)")
print(f"")
print(f"  Volume effect (ΔSent × old RPS):       ${volume_effect:.2f} ({volume_effect/total_decline*100:.1f}% of decline)")
print(f"  Efficiency effect (ΔRPS × new Vol):     ${efficiency_effect:.2f} ({efficiency_effect/total_decline*100:.1f}% of decline)")
print(f"")
print(f"  Retired phones (4) contribution:        ${retired_effect:.2f} ({retired_effect/total_decline*100:.1f}% of decline)")
print(f"  Active phones (2) contribution:         ${active_effect:.2f} ({active_effect/total_decline*100:.1f}% of decline)")

# =====================================================================
# 6. SUMMARY TABLE — Export for writeup
# =====================================================================

# Key metrics table
summary = pd.DataFrame({
    "Metric": ["Daily Revenue ($)", "Daily Sends", "Delivery Rate (%)",
               "Click-Through Rate (%)", "Revenue per Send (cents)",
               "Revenue per Click (cents)", "Active Phone Numbers"],
    "Pre-Decline Avg\n(Jan 27 – Feb 3)": [
        f"${pre[['Revenue']].mean().iloc[0]:.2f}",
        f"{pre['Sent'].mean():,.0f}",
        f"{pre['Delivery_Rate'].mean()*100:.2f}",
        f"{pre['CTR'].mean()*100:.2f}",
        f"{pre['Rev_per_Sent'].mean()*100:.3f}",
        f"{pre['Rev_per_Click'].mean()*100:.3f}",
        "6",
    ],
    "Post-Decline Avg\n(Feb 4 – Feb 16)": [
        f"${post[['Revenue']].mean().iloc[0]:.2f}",
        f"{post['Sent'].mean():,.0f}",
        f"{post['Delivery_Rate'].mean()*100:.2f}",
        f"{post['CTR'].mean()*100:.2f}",
        f"{post['Rev_per_Sent'].mean()*100:.3f}",
        f"{post['Rev_per_Click'].mean()*100:.3f}",
        "2 (from Feb 11)",
    ],
})

pct_changes = [
    f"{(post['Revenue'].mean() - pre['Revenue'].mean()) / pre['Revenue'].mean() * 100:+.1f}%",
    f"{(post['Sent'].mean() - pre['Sent'].mean()) / pre['Sent'].mean() * 100:+.1f}%",
    f"{(post['Delivery_Rate'].mean() - pre['Delivery_Rate'].mean()) / pre['Delivery_Rate'].mean() * 100:+.2f}%",
    f"{(post['CTR'].mean() - pre['CTR'].mean()) / pre['CTR'].mean() * 100:+.1f}%",
    f"{(post['Rev_per_Sent'].mean() - pre['Rev_per_Sent'].mean()) / pre['Rev_per_Sent'].mean() * 100:+.1f}%",
    f"{(post['Rev_per_Click'].mean() - pre['Rev_per_Click'].mean()) / pre['Rev_per_Click'].mean() * 100:+.1f}%",
    "—",
]
summary["Change"] = pct_changes
print("\n--- Summary Table for Writeup ---")
print(summary.to_string(index=False))

# Save summary table as CSV for reference
summary.to_csv("summary_table.csv", index=False)
print("\nSaved: summary_table.csv")

# =====================================================================
# 7. REGRESSION COEFFICIENT TABLE — formatted for writeup
# =====================================================================

# Extract Model 2 coefficients into a clean table
coef_df = pd.DataFrame({
    "Variable": m2.params.index,
    "Coefficient": m2.params.values,
    "Std Error": m2.bse.values,
    "t-stat": m2.tvalues.values,
    "p-value": m2.pvalues.values,
})
coef_df["Sig"] = coef_df["p-value"].apply(
    lambda p: "***" if p < 0.001 else ("**" if p < 0.01 else ("*" if p < 0.05 else ""))
)
coef_df.to_csv("regression_coefficients.csv", index=False)
print("Saved: regression_coefficients.csv")

print("\n" + "=" * 60)
print("ANALYSIS COMPLETE")
print("=" * 60)
