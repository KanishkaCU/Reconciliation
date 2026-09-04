import pandas as pd

# Read the ground truth
ground_truth = pd.read_csv("data/ground_truth.csv")

# Read the financial files
invoices = pd.read_csv("data/invoices.csv")
payments = pd.read_csv("data/payments.csv")
settlements = pd.read_csv("data/settlements.csv")


# --------------------------------------------------
# Recreate the reconciliation logic
# --------------------------------------------------

payment_by_customer = (
    payments.groupby("customer_id")["payment_id"]
    .apply(list)
    .to_dict()
)

reconciliation = invoices.merge(
    payments,
    on=["invoice_id", "customer_id"],
    how="left"
)

reconciliation = reconciliation.merge(
    settlements,
    on="payment_id",
    how="left"
)


def check_transaction(row):

    if not pd.isna(row["payment_id"]):

        if row["invoice_amount"] != row["payment_amount"]:
            return "PAYMENT_MISMATCH"

        if pd.isna(row["settlement_id"]):
            return "MISSING_SETTLEMENT"

        if row["payment_amount"] != row["settlement_amount"]:
            return "SETTLEMENT_MISMATCH"

        return "MATCHED"

    customer_id = row["customer_id"]

    if customer_id in payment_by_customer:
        return "INVALID_REFERENCE"

    return "MISSING_PAYMENT"


reconciliation["predicted_result"] = reconciliation.apply(
    check_transaction,
    axis=1
)


# --------------------------------------------------
# Compare with ground truth
# --------------------------------------------------

evaluation = ground_truth.merge(
    reconciliation[["invoice_id", "predicted_result"]],
    on="invoice_id",
    how="left"
)


evaluation["correct"] = (
    evaluation["expected_result"]
    == evaluation["predicted_result"]
)


# --------------------------------------------------
# Calculate accuracy
# --------------------------------------------------

total = len(evaluation)

correct = evaluation["correct"].sum()

accuracy = (correct / total) * 100


print("\nEVALUATION RESULTS")
print("-----------------------------")

print(f"Total records       : {total}")
print(f"Correct predictions : {correct}")
print(f"Incorrect           : {total - correct}")
print(f"Accuracy            : {accuracy:.2f}%")

print("\nRESULT COMPARISON")
print("-----------------------------")

print(
    pd.crosstab(
        evaluation["expected_result"],
        evaluation["predicted_result"],
        margins=True
    )
)


# --------------------------------------------------
# Show incorrect predictions
# --------------------------------------------------

incorrect = evaluation[
    evaluation["correct"] == False
]

print("\nINCORRECT PREDICTIONS")
print("-----------------------------")

if len(incorrect) == 0:
    print("No incorrect predictions.")
else:
    print(
        incorrect[
            [
                "invoice_id",
                "expected_result",
                "predicted_result"
            ]
        ].to_string(index=False)
    )