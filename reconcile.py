import pandas as pd

# Read the three financial files
invoices = pd.read_csv("data/invoices.csv")
payments = pd.read_csv("data/payments.csv")
settlements = pd.read_csv("data/settlements.csv")

# --------------------------------------------------
# STEP 1: Identify payments that exist for each
# customer, even if they reference the wrong invoice
# --------------------------------------------------

payment_by_customer = (
    payments.groupby("customer_id")["payment_id"]
    .apply(list)
    .to_dict()
)


# --------------------------------------------------
# STEP 2: Merge invoices with payments using the
# expected invoice reference
# --------------------------------------------------

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


# --------------------------------------------------
# STEP 3: Improved reconciliation rules
# --------------------------------------------------

def check_transaction(row):

    # Payment correctly linked to invoice
    if not pd.isna(row["payment_id"]):

        # Check invoice/payment amount
        if row["invoice_amount"] != row["payment_amount"]:
            return "PAYMENT_MISMATCH"

        # Check settlement
        if pd.isna(row["settlement_id"]):
            return "MISSING_SETTLEMENT"

        # Check settlement amount
        if row["payment_amount"] != row["settlement_amount"]:
            return "SETTLEMENT_MISMATCH"

        return "MATCHED"

    # No correctly linked payment was found.
    # Check whether ANY payment exists for this customer.
    customer_id = row["customer_id"]

    if customer_id in payment_by_customer:
        return "INVALID_REFERENCE"

    return "MISSING_PAYMENT"

# Apply reconciliation
reconciliation["result"] = reconciliation.apply(
    check_transaction,
    axis=1
)


# --------------------------------------------------
# STEP 5: Explain the result
# --------------------------------------------------

def explain_transaction(row):

    result = row["result"]

    if result == "MATCHED":
        return "Invoice, payment, and settlement amounts match."

    if result == "MISSING_PAYMENT":
        return "No payment record was found for this invoice."

    if result == "INVALID_REFERENCE":
        return "The payment references an incorrect invoice."

    if result == "PAYMENT_MISMATCH":
        difference = (
            row["invoice_amount"] -
            row["payment_amount"]
        )
        return (
            f"Payment amount differs from invoice "
            f"by ₹{difference:.2f}."
        )

    if result == "MISSING_SETTLEMENT":
        return (
            "Payment exists, but no settlement "
            "record was found."
        )

    if result == "SETTLEMENT_MISMATCH":
        difference = (
            row["payment_amount"] -
            row["settlement_amount"]
        )
        return (
            f"Settlement amount differs from payment "
            f"by ₹{difference:.2f}."
        )

    return "Unknown result."


reconciliation["explanation"] = reconciliation.apply(
    explain_transaction,
    axis=1
)


# --------------------------------------------------
# STEP 6: Display results
# --------------------------------------------------

print("\nRECONCILIATION RESULTS\n")

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
    ].to_string(index=False)
)


# --------------------------------------------------
# STEP 7: Summary
# --------------------------------------------------

total_records = len(reconciliation)

matched_records = len(
    reconciliation[
        reconciliation["result"] == "MATCHED"
    ]
)

exceptions = total_records - matched_records

match_rate = (
    matched_records / total_records
) * 100


print("\n-----------------------------")
print(f"Total records   : {total_records}")
print(f"Matched records : {matched_records}")
print(f"Exceptions      : {exceptions}")
print(f"Match rate      : {match_rate:.2f}%")
print("-----------------------------")


# Show how many of each result we found

print("\nRESULT BREAKDOWN\n")

print(
    reconciliation["result"].value_counts()
)