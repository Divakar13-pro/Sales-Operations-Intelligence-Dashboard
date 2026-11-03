import pandas as pd
import plotly.express as px


def line_chart(df, date_col, title, y_label="Records"):
    if df.empty or date_col not in df:
        return px.line(title=title)
    x = df.copy()
    x[date_col] = pd.to_datetime(x[date_col], errors="coerce")
    series = x.dropna(subset=[date_col]).set_index(date_col).resample("MS").size().reset_index(name="records")
    return px.line(series, x=date_col, y="records", markers=True, title=title, labels={date_col: "Month", "records": y_label})


def bar_chart(df, category, value, title, agg="count"):
    if df.empty or category not in df:
        return px.bar(title=title)
    if agg == "sum":
        grouped = df.groupby(category, dropna=False)[value].sum().reset_index()
        y = value
    else:
        grouped = df.groupby(category, dropna=False)[value].count().reset_index(name="records")
        y = "records"
    grouped[category] = grouped[category].fillna("Unknown").astype(str)
    return px.bar(grouped, x=category, y=y, title=title, text_auto=True)


def donut_chart(df, category, title):
    if df.empty or category not in df:
        return px.pie(title=title)
    grouped = df[category].fillna("Unknown").value_counts().reset_index()
    grouped.columns = [category, "records"]
    return px.pie(grouped, names=category, values="records", hole=.48, title=title)


def target_chart(comparison):
    if comparison.empty:
        return px.bar(title="Targets vs won-deal value proxy (no matching records)")
    monthly = comparison.groupby("month", as_index=False)[["target", "won_deal_value_proxy"]].sum()
    long = monthly.melt(id_vars="month", var_name="measure", value_name="amount")
    long["measure"] = long["measure"].map({"target": "Target", "won_deal_value_proxy": "Won deal value proxy"})
    return px.bar(long, x="month", y="amount", color="measure", barmode="group", title="Targets vs won-deal value proxy", labels={"month": "Month", "amount": "Amount (₹)"})
