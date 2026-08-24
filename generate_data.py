import pandas as pd

# Invoice data
invoices = [
    ["INV001", "C001", 5000, "2026-08-20", "INR", "Paid"],
    ["INV002", "C002", 3000, "2026-08-20", "INR", "Paid"],
    ["INV003", "C003", 8000, "2026-08-20", "INR", "Paid"],
    ["INV004", "C004", 6000, "2026-08-20", "INR", "Paid"],
    ["INV005", "C005", 4000, "2026-08-20", "INR", "Paid"]
]

invoice_columns = [
    "invoice_id",
    "customer_id",
    "invoice_amount",
    "invoice_date",
    "currency",
    "status"
]

invoice_df = pd.DataFrame(invoices, columns=invoice_columns)

# Payment data
payments = [
    ["PAY001", "INV001", "C001", 5000, "2026-08-20", "UPI", "Success"],
    ["PAY002", "INV002", "C002", 3000, "2026-08-20", "UPI", "Success"],
    ["PAY003", "INV003", "C003", 7500, "2026-08-20", "Card", "Success"],
    ["PAY004", "INV004", "C004", 6000, "2026-08-20", "UPI", "Success"]
]

payment_columns = [
    "payment_id",
    "invoice_id",
    "customer_id",
    "payment_amount",
    "payment_date",
    "payment_method",
    "status"
]

payment_df = pd.DataFrame(payments, columns=payment_columns)

# Settlement data
settlements = [
    ["SET001", "PAY001", 5000, "2026-08-21", "Settled"],
    ["SET002", "PAY002", 3000, "2026-08-21", "Settled"],
    ["SET003", "PAY003", 7500, "2026-08-21", "Settled"],
    ["SET004", "PAY004", 5700, "2026-08-21", "Settled"]
]

settlement_columns = [
    "settlement_id",
    "payment_id",
    "settlement_amount",
    "settlement_date",
    "status"
]

settlement_df = pd.DataFrame(
    settlements,
    columns=settlement_columns
)

# Save the files
invoice_df.to_csv("data/invoices.csv", index=False)
payment_df.to_csv("data/payments.csv", index=False)
settlement_df.to_csv("data/settlements.csv", index=False)

print("Synthetic financial data created successfully!")