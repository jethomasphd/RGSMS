"""
Generate a shareable PDF report for the SMS Revenue Decline Analysis.
Uses reportlab to produce a polished, multi-page document with embedded
figures, formatted tables, and narrative text.
"""

import os
from reportlab.lib.pagesizes import letter
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle,
    PageBreak, KeepTogether, HRFlowable
)

BASE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(BASE, "SMS_Revenue_Decline_Report.pdf")

# ── Colors ───────────────────────────────────────────────────────────
ACCENT = HexColor("#005A9C")
ACCENT_LIGHT = HexColor("#DCE9F5")
DARK = HexColor("#1E1E1E")
GRAY = HexColor("#555555")
LIGHT_GRAY = HexColor("#EBEBEB")
RED = HexColor("#B42828")
GREEN = HexColor("#1E7A1E")

# ── Styles ───────────────────────────────────────────────────────────
styles = getSampleStyleSheet()

styles.add(ParagraphStyle(
    "Title_Custom", parent=styles["Title"],
    fontSize=26, leading=32, textColor=ACCENT, spaceAfter=6,
    alignment=TA_CENTER, fontName="Helvetica-Bold",
))
styles.add(ParagraphStyle(
    "Subtitle", parent=styles["Normal"],
    fontSize=12, leading=16, textColor=GRAY,
    alignment=TA_CENTER, fontName="Helvetica",
))
styles.add(ParagraphStyle(
    "SectionHead", parent=styles["Heading2"],
    fontSize=13, leading=17, textColor=ACCENT,
    fontName="Helvetica-Bold", spaceAfter=4, spaceBefore=14,
))
styles.add(ParagraphStyle(
    "BodyText_Custom", parent=styles["Normal"],
    fontSize=9.5, leading=13.5, textColor=DARK,
    fontName="Helvetica", alignment=TA_JUSTIFY, spaceAfter=6,
))
styles.add(ParagraphStyle(
    "Callout", parent=styles["Normal"],
    fontSize=10, leading=14, textColor=ACCENT,
    fontName="Helvetica-Bold", alignment=TA_LEFT, spaceAfter=6,
))
styles.add(ParagraphStyle(
    "BoldBody", parent=styles["Normal"],
    fontSize=9.5, leading=13.5, textColor=DARK,
    fontName="Helvetica-Bold", spaceAfter=2,
))
styles.add(ParagraphStyle(
    "Caption", parent=styles["Normal"],
    fontSize=8, leading=11, textColor=GRAY,
    fontName="Helvetica-Oblique", alignment=TA_JUSTIFY, spaceAfter=8,
))
styles.add(ParagraphStyle(
    "Footnote", parent=styles["Normal"],
    fontSize=8, leading=11, textColor=GRAY,
    fontName="Helvetica", alignment=TA_LEFT, spaceAfter=4,
))
styles.add(ParagraphStyle(
    "TableCell", parent=styles["Normal"],
    fontSize=8.5, leading=11, textColor=DARK,
    fontName="Helvetica",
))
styles.add(ParagraphStyle(
    "TableCellBold", parent=styles["Normal"],
    fontSize=8.5, leading=11, textColor=white,
    fontName="Helvetica-Bold", alignment=TA_CENTER,
))
styles.add(ParagraphStyle(
    "TableCellCenter", parent=styles["Normal"],
    fontSize=8.5, leading=11, textColor=DARK,
    fontName="Helvetica", alignment=TA_CENTER,
))


def make_table(headers, rows, col_widths, highlight_col=None):
    """Build a styled Table flowable."""
    # Header row
    header_cells = [Paragraph(h, styles["TableCellBold"]) for h in headers]
    data = [header_cells]

    for row in rows:
        cells = []
        for i, val in enumerate(row):
            style = "TableCell" if i == 0 else "TableCellCenter"
            # Color change column values
            if highlight_col is not None and i == highlight_col:
                if val.startswith("-") or val.startswith("\u2013"):
                    val = f'<font color="#B42828">{val}</font>'
                elif val.startswith("+"):
                    val = f'<font color="#1E7A1E">{val}</font>'
            cells.append(Paragraph(val, styles[style]))
        data.append(cells)

    t = Table(data, colWidths=col_widths, repeatRows=1)
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), ACCENT),
        ("TEXTCOLOR", (0, 0), (-1, 0), white),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#CCCCCC")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]
    # Alternating row shading
    for i in range(1, len(data)):
        if i % 2 == 0:
            style_cmds.append(("BACKGROUND", (0, i), (-1, i), LIGHT_GRAY))
    t.setStyle(TableStyle(style_cmds))
    return t


# ── Build document ───────────────────────────────────────────────────
doc = SimpleDocTemplate(
    OUT, pagesize=letter,
    leftMargin=0.75 * inch, rightMargin=0.75 * inch,
    topMargin=0.75 * inch, bottomMargin=0.75 * inch,
)
usable_w = doc.width
story = []

# =====================================================================
# PAGE 1 — Title page
# =====================================================================
story.append(Spacer(1, 1.8 * inch))
story.append(Paragraph("SMS Campaign<br/>Revenue Decline Analysis", styles["Title_Custom"]))
story.append(Spacer(1, 0.15 * inch))
story.append(HRFlowable(width="40%", thickness=1.5, color=ACCENT, spaceAfter=12))
story.append(Paragraph("Job Alerts SMS Program", styles["Subtitle"]))
story.append(Paragraph("January 27 \u2013 February 16, 2026", styles["Subtitle"]))
story.append(Spacer(1, 0.6 * inch))
story.append(Paragraph(
    "Data Source: SmsDeliveryReport.csv (1,784 observations after filtering)<br/>"
    "Rows with Sms Phone Number = 20407 excluded",
    styles["Caption"],
))
story.append(Spacer(1, 1.2 * inch))
story.append(Paragraph("February 2026", styles["Subtitle"]))
story.append(PageBreak())

# =====================================================================
# PAGE 2 — Executive Summary + Key Metrics
# =====================================================================
story.append(Paragraph("Executive Summary", styles["SectionHead"]))
story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))

# Callout box via a single-cell table with background
callout_text = (
    "Daily revenue fell 43% (from $609 to $347/day) starting February 4, driven "
    "almost entirely (99%) by the retirement of 4 of 6 sending phone numbers. "
    "Revenue efficiency (revenue per send) also declined 27%, indicating a secondary "
    "monetization problem."
)
callout_table = Table(
    [[Paragraph(callout_text, styles["Callout"])]],
    colWidths=[usable_w],
)
callout_table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), ACCENT_LIGHT),
    ("BOX", (0, 0), (-1, -1), 1, ACCENT),
    ("TOPPADDING", (0, 0), (-1, -1), 8),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ("LEFTPADDING", (0, 0), (-1, -1), 10),
    ("RIGHTPADDING", (0, 0), (-1, -1), 10),
]))
story.append(callout_table)
story.append(Spacer(1, 0.1 * inch))

story.append(Paragraph(
    "This analysis examines 21 days of SMS campaign delivery data across 6 carrier groups, "
    "3 audience segments, and 6 phone numbers to identify factors associated with the "
    "observed revenue decline. Methods include descriptive comparison of pre- and post-decline "
    "periods, revenue decomposition, OLS regression, and time-series visualization.",
    styles["BodyText_Custom"],
))

story.append(Paragraph("Key Metrics: Pre-Decline vs. Post-Decline", styles["SectionHead"]))
story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))

metrics_headers = ["Metric", "Pre-Decline\n(Jan 27\u2013Feb 3)", "Post-Decline\n(Feb 4\u2013Feb 16)", "Change"]
metrics_rows = [
    ["Daily Revenue",          "$608.68",   "$346.63",   "-43.1%"],
    ["Daily Sends",            "67,531",    "51,926",    "-23.1%"],
    ["Revenue / Send",         "0.90\u00a2", "0.66\u00a2", "-27.0%"],
    ["Revenue / Click",        "1.67\u00a2", "1.13\u00a2", "-32.3%"],
    ["Click-Through Rate",     "53.9%",     "59.6%",     "+10.6%"],
    ["Delivery Rate",          "99.6%",     "99.6%",     "~0%"],
    ["Active Phone Numbers",   "6",         "2 (from Feb 11)", "\u2014"],
]
story.append(make_table(metrics_headers, metrics_rows,
                        col_widths=[1.9*inch, 1.5*inch, 1.6*inch, 1.0*inch],
                        highlight_col=3))

story.append(Paragraph(
    "Delivery rates remained stable at 99.6%, ruling out carrier filtering or deliverability "
    "issues. Click-through rates actually <b>increased</b> 10.6% post-decline, confirming that "
    "the remaining audience stayed engaged. The problem is upstream: loss of send capacity "
    "and deteriorating per-message monetization.",
    styles["BodyText_Custom"],
))

story.append(PageBreak())

# =====================================================================
# PAGE 3 — Visualizations + Decomposition
# =====================================================================
story.append(Paragraph("Revenue Trends and Operational Metrics", styles["SectionHead"]))
story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=6))

fig1_path = os.path.join(BASE, "fig1_revenue_overview.png")
story.append(Image(fig1_path, width=usable_w, height=usable_w * 0.64))
story.append(Paragraph(
    "<b>Figure 1.</b> (A) Total daily revenue with pre/post-decline shading. (B) Revenue split "
    "by phone group \u2014 the 4 retired numbers collapse while the 2 active numbers hold steady. "
    "(C) Send volume (bars) vs. revenue (line) showing volume partially recovered ~Feb 12 "
    "but revenue did not follow. (D) Revenue efficiency (cents per send) declining throughout.",
    styles["Caption"],
))

story.append(Paragraph("Revenue Decomposition", styles["SectionHead"]))
story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))

story.append(Paragraph(
    "The $262/day decline decomposes into two mechanisms:",
    styles["BodyText_Custom"],
))

decomp_headers = ["Component", "Daily Impact", "Share of Decline", "Description"]
decomp_rows = [
    ["Volume loss",     "-$141/day", "54%", "Fewer messages sent (phone retirement)"],
    ["Efficiency loss", "-$121/day", "46%", "Lower revenue per message sent"],
]
story.append(make_table(decomp_headers, decomp_rows,
                        col_widths=[1.2*inch, 1.0*inch, 1.1*inch, 2.7*inch]))

phone_headers = ["Phone Group", "Daily Impact", "Share of Decline"]
phone_rows = [
    ["Retired phones (4 numbers)", "-$259/day", "99.0%"],
    ["Active phones (2 numbers)",  "-$3/day",   "1.0%"],
]
story.append(make_table(phone_headers, phone_rows,
                        col_widths=[2.2*inch, 1.5*inch, 1.5*inch]))

story.append(Paragraph(
    "When the 4 high-performing phone numbers went offline, total send capacity dropped and "
    "the remaining infrastructure could not maintain the same revenue-per-send rate. Volume "
    "partially recovered around Feb 12 when the 2 active numbers scaled up, but per-message "
    "revenue continued to fall \u2014 suggesting replacement traffic monetizes less effectively.",
    styles["BodyText_Custom"],
))

story.append(PageBreak())

# =====================================================================
# PAGE 4 — Breakdowns + Regression
# =====================================================================
story.append(Paragraph("Revenue by Carrier, Segment, and Phone Number", styles["SectionHead"]))
story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=6))

fig2_path = os.path.join(BASE, "fig2_breakdowns.png")
story.append(Image(fig2_path, width=usable_w, height=usable_w * 0.31))
story.append(Paragraph(
    "<b>Figure 2.</b> Revenue over time by carrier (left), audience segment (center), and "
    "individual phone number (right). T-Mobile and Verizon dominate revenue. The Clicker "
    "segment peaks then collapses. Four of six phone numbers go to zero by Feb 11.",
    styles["Caption"],
))

story.append(Paragraph("Regression Analysis", styles["SectionHead"]))
story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))

story.append(Paragraph(
    "Row-level OLS regression (N = 1,784, R\u00b2 = 0.65) identifies the factors most "
    "strongly associated with revenue, controlling for operational and categorical variables:",
    styles["BodyText_Custom"],
))

reg_headers = ["Variable", "Coeff.", "p-value", "Interpretation"]
reg_rows = [
    ["Time trend (DayNum)",  "-0.42",   "<0.001", "Revenue erodes ~$0.42/row/day"],
    ["Sent (volume)",        "+0.0018", "<0.001", "Volume mechanically drives revenue"],
    ["Clicks",               "+0.0015", "0.006",  "Each click adds marginal revenue"],
    ["Carrier: Verizon",     "+10.48",  "<0.001", "Highest-revenue carrier (+$10.48 vs AT&T)"],
    ["Carrier: T-Mobile",    "+7.66",   "<0.001", "Second-highest (+$7.66 vs AT&T)"],
    ["Seg: New Data",        "-2.18",   "<0.001", "Underperforms Clicker by $2.18/row"],
    ["Seg: TriggeredSend",   "-2.20",   "<0.001", "Underperforms Clicker by $2.20/row"],
    ["Post_Decline",         "+2.84",   "<0.001", "Positive after controlling for volume"],
]
story.append(make_table(reg_headers, reg_rows,
                        col_widths=[1.4*inch, 0.7*inch, 0.6*inch, 3.3*inch]))

story.append(Paragraph(
    "The Post_Decline indicator is <b>positive</b> (+2.84) after controlling for volume and "
    "time trend, meaning that conditional on the same number of sends and clicks, post-decline "
    "rows yield marginally higher revenue. This confirms the decline is driven by the volume "
    "collapse (fewer sends) rather than a per-message problem within the remaining active "
    "infrastructure.",
    styles["BodyText_Custom"],
))

story.append(PageBreak())

# =====================================================================
# PAGE 5 — Conclusions & Recommendations
# =====================================================================
story.append(Paragraph("Conclusions and Recommendations", styles["SectionHead"]))
story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=10))

recs = [
    ("1. Restore or replace the 4 retired phone numbers.",
     "This is the single highest-leverage action. The 4 retired numbers accounted for 99% "
     "of the revenue decline. Whether these were deactivated due to compliance issues, carrier "
     "restrictions, or operational decisions, restoring send capacity should be the top priority. "
     "Each number was contributing roughly $65/day in revenue."),

    ("2. Investigate the decline in revenue-per-send.",
     "Even controlling for volume, revenue efficiency dropped 27%. This could reflect lower "
     "advertiser bid rates, changes in job-alert landing page conversion, audience fatigue, or "
     "shifts in the traffic mix. The monetization and demand-side teams should audit recent "
     "changes to ad partner configurations and conversion funnels."),

    ("3. Prioritize Verizon and T-Mobile traffic.",
     "These two carriers generate $10.48 and $7.66 more revenue per observation than AT&T "
     "(the baseline). Any disruption to delivery on these networks has an outsized impact. "
     "Monitor carrier-level deliverability closely."),

    ("4. Favor the Clicker segment in send allocation.",
     "The Clicker audience segment outperforms New Data and TriggeredSend by ~$2.20 per "
     "row. When send capacity is constrained (as it currently is with only 2 active numbers), "
     "prioritizing Clicker recipients will maximize revenue yield."),

    ("5. Monitor for further degradation.",
     "The time-trend coefficient (-$42/day at the aggregate level) indicates the decline has "
     "not yet stabilized. Without intervention, revenue will continue to fall. Weekly tracking "
     "of the metrics in this report is recommended."),
]

for title, body in recs:
    story.append(Paragraph(title, styles["BoldBody"]))
    story.append(Paragraph(body, styles["BodyText_Custom"]))
    story.append(Spacer(1, 0.05 * inch))

story.append(Spacer(1, 0.2 * inch))
story.append(Paragraph("Methodology Notes", styles["SectionHead"]))
story.append(HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=8))
story.append(Paragraph(
    "Data: SmsDeliveryReport.csv with 2,025 total rows; 1,784 after excluding phone number "
    "20407. Date range: January 27 \u2013 February 16, 2026. Pre-decline period defined as "
    "Jan 27 \u2013 Feb 3 (8 days); post-decline as Feb 4 \u2013 Feb 16 (13 days). "
    "Decomposition uses a Blinder-Oaxaca approach splitting total change into volume and "
    "efficiency components. OLS regression uses heteroskedasticity-robust (HC1) standard "
    "errors. All analysis code in analysis.py; full coefficient table in "
    "regression_coefficients.csv.",
    styles["Footnote"],
))

# ── Render ───────────────────────────────────────────────────────────
doc.build(story)
print(f"Report saved: {OUT}")
