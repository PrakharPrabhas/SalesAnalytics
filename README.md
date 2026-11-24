# SalesAnalytics — Sales Analysis Dashboard

A complete beginner-friendly sales analytics dashboard built with Python, Flask, Pandas, HTML, CSS, JavaScript and Chart.js.

## Features
- KPI cards: sales, profit, orders, customers, units sold and average order value
- Monthly sales and profit trend
- Sales by category, region, product and payment method
- Date, category and region filters
- Search across sales records
- Recent orders table
- Export the filtered records to CSV
- Automatically creates a sample dataset on first run

## 1. Requirements
- Python 3.9 or newer
- Internet connection for loading Chart.js and Google Fonts from their CDNs

## 2. Setup

Open a terminal in this project folder.

### Windows
```bash
py -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### macOS / Linux
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

## 3. Open the dashboard
Visit: http://127.0.0.1:5000

The first run creates `sales_data.csv` with 1,200 sample sales records. Keep the terminal open while using the dashboard. Press Ctrl+C to stop the server.

## 4. Use your own dataset
Replace `sales_data.csv` with your own CSV, keeping these column names:

`Order_ID, Order_Date, Customer, Product, Category, Region, City, Quantity, Unit_Price, Discount, Sales, Profit, Payment_Mode`

- `Order_Date` should be parseable as a date (for example `2026-01-31`).
- `Sales` and `Profit` should be numeric values in INR.
- `Discount` should be a decimal (for example `0.10` for 10%).
- Keep the exact column names, including capitalization.
- Restart the Flask app after replacing the CSV.

## 5. Project structure
```text
Sales_Analysis_Dashboard/
├── app.py
├── sales_data.csv          # generated on first run
├── requirements.txt
├── README.md
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── script.js
```

## Notes
- The sample data is fictional and intended for demonstration.
- Profit in the sample data is calculated as revenue minus a randomly generated estimated product cost. It is not real accounting data.

