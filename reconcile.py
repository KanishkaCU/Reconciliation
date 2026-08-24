import pandas as pd

# Read the three financial files
invoices = pd.read_csv("data/invoices.csv")
payments = pd.read_csv("data/payments.csv")
settlements = pd.read_csv("data/settlements.csv")

# Combine invoice and payment information
reconciliation = invoices.merge(
    payments,
    on=["invoice_id", "customer_id"],
    how="left"
)

# Add settlement information
reconciliation = reconciliation.merge(
    settlements,
    on="payment_id",
    how="left"
)

# Check each transaction
def check_transaction(row):



    # Payment is missing
    if pd.isna(row["payment_id"]):
        return "MISSING_PAYMENT"

    # Invoice and payment amount don't match
    if row["invoice_amount"] != row["payment_amount"]:
        return "PAYMENT_MISMATCH"

    # Settlement is missing
    if pd.isna(row["settlement_id"]):
        return "MISSING_SETTLEMENT"

    # Payment and settlement amount don't match
    if row["payment_amount"] != row["settlement_amount"]:
        return "SETTLEMENT_MISMATCH"

    return "MATCHED"

def explain_transaction(row):

    result = row["result"]

    if result == "MATCHED":
        return "Invoice, payment, and settlement amounts match."

    if result == "MISSING_PAYMENT":
        return "No payment record was found for this invoice."

    if result == "PAYMENT_MISMATCH":
        difference = row["invoice_amount"] - row["payment_amount"]
        return f"Payment amount differs from invoice by ₹{difference:.2f}."

    if result == "MISSING_SETTLEMENT":
        return "Payment exists, but no settlement record was found."

    if result == "SETTLEMENT_MISMATCH":
        difference = row["payment_amount"] - row["settlement_amount"]
        return f"Settlement amount differs from payment by ₹{difference:.2f}."

    return "Unknown result."
# Apply the reconciliation rules
reconciliation["result"] = reconciliation.apply(
    check_transaction,
    axis=1
)
reconciliation["explanation"] = reconciliation.apply(
    explain_transaction,
    axis=1
)
# Display the results
print(
    reconciliation[
        [
            "invoice_id",
            "invoice_amount",
            "payment_amount",
            "settlement_amount",
            "result",
            "explanation"
        ]
    ]
)

# Calculate match rate
total_records = len(reconciliation)
matched_records = len(
    reconciliation[reconciliation["result"] == "MATCHED"]
)

match_rate = (matched_records / total_records) * 100

print("\n-----------------------------")
print(f"Total records   : {total_records}")
print(f"Matched records : {matched_records}")
print(f"Exceptions      : {total_records - matched_records}")
print(f"Match rate      : {match_rate:.2f}%")
print("-----------------------------")