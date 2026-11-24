from flask import Flask, render_template, request, jsonify, send_file
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime, timedelta
import io

app = Flask(__name__)
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "sales_data.csv"


def create_sample_data(path=CSV_PATH, rows=1200, seed=42):
    """Create a realistic sample retail sales dataset."""
    rng = np.random.default_rng(seed)
    products = [
        ("Laptop", "Electronics", 52000),
        ("Smartphone", "Electronics", 28000),
        ("Headphones", "Electronics", 2200),
        ("Monitor", "Electronics", 12500),
        ("Office Chair", "Furniture", 7800),
        ("Desk", "Furniture", 9500),
        ("Bookshelf", "Furniture", 6200),
        ("T-Shirt", "Clothing", 650),
        ("Jeans", "Clothing", 1500),
        ("Jacket", "Clothing", 2800),
        ("Running Shoes", "Sports", 3200),
        ("Yoga Mat", "Sports", 900),
        ("Water Bottle", "Accessories", 450),
        ("Backpack", "Accessories", 1800),
    ]
    regions = ["North", "South", "East", "West", "Central"]
    cities = {
        "North": ["Delhi", "Jaipur", "Chandigarh"],
        "South": ["Bengaluru", "Chennai", "Hyderabad"],
        "East": ["Kolkata", "Bhubaneswar", "Patna"],
        "West": ["Mumbai", "Pune", "Ahmedabad"],
        "Central": ["Bhopal", "Indore", "Nagpur"],
    }
    start = pd.Timestamp.today().normalize() - pd.DateOffset(months=11)
    dates = start + pd.to_timedelta(rng.integers(0, 365, rows), unit="D")
    chosen = rng.integers(0, len(products), rows)
    records = []
    for i in range(rows):
        product, category, price = products[chosen[i]]
        region = rng.choice(regions)
        quantity = int(rng.integers(1, 6))
        unit_price = round(price * rng.uniform(0.9, 1.12), 2)
        discount = float(rng.choice([0, 0.05, 0.10, 0.15], p=[0.45, 0.25, 0.20, 0.10]))
        revenue = round(quantity * unit_price * (1 - discount), 2)
        cost = round(quantity * unit_price * rng.uniform(0.58, 0.82), 2)
        records.append(
            {
                "Order_ID": f"ORD-{10001+i}",
                "Order_Date": dates[i].strftime("%Y-%m-%d"),
                "Customer": f"Customer {int(rng.integers(1, 351)):03d}",
                "Product": product,
                "Category": category,
                "Region": region,
                "City": rng.choice(cities[region]),
                "Quantity": quantity,
                "Unit_Price": unit_price,
                "Discount": discount,
                "Sales": revenue,
                "Profit": round(revenue - cost, 2),
                "Payment_Mode": rng.choice(
                    ["UPI", "Credit Card", "Debit Card", "Cash", "Net Banking"]
                ),
            }
        )
    pd.DataFrame(records).to_csv(path, index=False)


def load_data():
    if not CSV_PATH.exists():
        create_sample_data()
    df = pd.read_csv(CSV_PATH)
    required = [
        "Order_ID",
        "Order_Date",
        "Customer",
        "Product",
        "Category",
        "Region",
        "City",
        "Quantity",
        "Unit_Price",
        "Discount",
        "Sales",
        "Profit",
        "Payment_Mode",
    ]
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError("Dataset is missing columns: " + ", ".join(missing))
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors="coerce")
    for col in ["Quantity", "Unit_Price", "Discount", "Sales", "Profit"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df.dropna(subset=["Order_Date"]).copy()


def filtered_data():
    df = load_data()
    start = request.args.get("start")
    end = request.args.get("end")
    category = request.args.get("category", "All")
    region = request.args.get("region", "All")
    search = request.args.get("search", "").strip().lower()
    if start:
        df = df[df["Order_Date"] >= pd.to_datetime(start)]
    if end:
        df = df[df["Order_Date"] < pd.to_datetime(end) + pd.Timedelta(days=1)]
    if category and category != "All":
        df = df[df["Category"] == category]
    if region and region != "All":
        df = df[df["Region"] == region]
    if search:
        mask = (
            df.astype(str)
            .apply(lambda col: col.str.lower().str.contains(search, na=False))
            .any(axis=1)
        )
        df = df[mask]
    return df


def money(value):
    return round(float(value), 2)


@app.route("/")
def index():
    df = load_data()
    return render_template(
        "index.html",
        categories=sorted(df["Category"].dropna().unique().tolist()),
        regions=sorted(df["Region"].dropna().unique().tolist()),
        min_date=df["Order_Date"].min().strftime("%Y-%m-%d"),
        max_date=df["Order_Date"].max().strftime("%Y-%m-%d"),
    )


@app.route("/api/dashboard")
def dashboard_api():
    df = filtered_data()
    total_sales = money(df["Sales"].sum())
    total_profit = money(df["Profit"].sum())
    orders = int(df["Order_ID"].nunique())
    customers = int(df["Customer"].nunique())
    quantity = int(df["Quantity"].sum())
    avg_order = money(total_sales / orders) if orders else 0

    monthly = (
        df.assign(Month=df["Order_Date"].dt.to_period("M").astype(str))
        .groupby("Month", as_index=False)
        .agg(Sales=("Sales", "sum"), Profit=("Profit", "sum"))
    )
    category = (
        df.groupby("Category", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )
    region = (
        df.groupby("Region", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )
    top_products = (
        df.groupby("Product", as_index=False)
        .agg(Sales=("Sales", "sum"), Quantity=("Quantity", "sum"))
        .sort_values("Sales", ascending=False)
        .head(8)
    )
    payment = (
        df.groupby("Payment_Mode", as_index=False)["Sales"]
        .sum()
        .sort_values("Sales", ascending=False)
    )
    recent = df.sort_values("Order_Date", ascending=False).head(12).copy()
    recent["Order_Date"] = recent["Order_Date"].dt.strftime("%d %b %Y")

    return jsonify(
        {
            "kpis": {
                "sales": total_sales,
                "profit": total_profit,
                "orders": orders,
                "customers": customers,
                "quantity": quantity,
                "average_order": avg_order,
            },
            "monthly": {
                "labels": monthly["Month"].tolist(),
                "sales": [money(x) for x in monthly["Sales"]],
                "profit": [money(x) for x in monthly["Profit"]],
            },
            "category": {
                "labels": category["Category"].tolist(),
                "values": [money(x) for x in category["Sales"]],
            },
            "region": {
                "labels": region["Region"].tolist(),
                "values": [money(x) for x in region["Sales"]],
            },
            "products": {
                "labels": top_products["Product"].tolist(),
                "sales": [money(x) for x in top_products["Sales"]],
                "quantity": [int(x) for x in top_products["Quantity"]],
            },
            "payment": {
                "labels": payment["Payment_Mode"].tolist(),
                "values": [money(x) for x in payment["Sales"]],
            },
            "recent": recent[
                [
                    "Order_ID",
                    "Order_Date",
                    "Customer",
                    "Product",
                    "Category",
                    "Region",
                    "Sales",
                    "Profit",
                ]
            ].to_dict(orient="records"),
            "row_count": int(len(df)),
        }
    )


@app.route("/api/export")
def export_csv():
    df = filtered_data().sort_values("Order_Date", ascending=False).copy()
    df["Order_Date"] = df["Order_Date"].dt.strftime("%Y-%m-%d")
    output = io.StringIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return send_file(
        io.BytesIO(output.getvalue().encode("utf-8-sig")),
        mimetype="text/csv",
        as_attachment=True,
        download_name="sales_report.csv",
    )


if __name__ == "__main__":
    if not CSV_PATH.exists():
        create_sample_data()
        print(f"Sample dataset created: {CSV_PATH}")
    app.run(debug=True, host="127.0.0.1", port=5000)
