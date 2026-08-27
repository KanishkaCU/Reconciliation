import pandas as pd
import random
from datetime import datetime, timedelta

random.seed(42)

TOTAL_RECORDS = 100

# How many of each type we want
normal_count = 70
payment_mismatch_count = 10
settlement_mismatch_count = 8
missing_payment_count = 5
missing_settlement_count = 4
invalid_reference_count = 3

invoices = []
payments = []
settlements = []
ground_truth = []

start_date = datetime(2026, 8, 1)

for i in range(1, TOTAL_RECORDS + 1):

    invoice_id = f"INV{i:03d}"
    payment_id = f"PAY{i:03d}"
    settlement_id = f"SET{i:03d}"
    customer_id = f"C{i:03d}"

    amount = random.choice([1000, 1500, 2000, 2500, 3000, 5000, 7500, 10000])

    invoice_date = start_date + timedelta(days=random.randint(0, 20))
    invoice_date_str = invoice_date.strftime("%Y-%m-%d")

    # Default: everything is correct
    payment_amount = amount
    settlement_amount = amount

    payment_status = "Success"
    settlement_status = "Settled"

    issue = "MATCHED"

    # Decide what kind of transaction this is
    if i <= normal_count:
        issue = "MATCHED"

    elif i <= normal_count + payment_mismatch_count:
        payment_amount = amount - random.choice([100, 200, 300, 500])
        settlement_amount = payment_amount
        issue = "PAYMENT_MISMATCH"

    elif i <= normal_count + payment_mismatch_count + settlement_mismatch_count:
        settlement_amount = amount - random.choice([100, 200, 300, 500])
        issue = "SETTLEMENT_MISMATCH"

    elif i <= normal_count + payment_mismatch_count + settlement_mismatch_count + missing_payment_count:
        payment_status = "Missing"
        settlement_status = "Missing"
        issue = "MISSING_PAYMENT"

    elif i <= normal_count + payment_mismatch_count + settlement_mismatch_count + missing_payment_count + missing_settlement_count:
        settlement_status = "Missing"
        issue = "MISSING_SETTLEMENT"

    else:
        issue = "INVALID_REFERENCE"

    # Create invoice
    invoices.append([
        invoice_id,
        customer_id,
        amount,
        invoice_date_str,
        "INR",
        "Paid"
    ])

    # Create payment unless payment is missing
    if issue != "MISSING_PAYMENT":

        payment_invoice_id = invoice_id

        # Deliberately create an invalid invoice reference
        if issue == "INVALID_REFERENCE":
            payment_invoice_id = f"INV{random.randint(1, 99):03d}"

            # Make sure it is not the correct invoice ID
            if payment_invoice_id == invoice_id:
                payment_invoice_id = "INV001"

        payments.append([
            payment_id,
            payment_invoice_id,
            customer_id,
            payment_amount,
            invoice_date_str,
            random.choice(["UPI", "Card", "NetBanking"]),
            payment_status
        ])

    # Create settlement unless payment or settlement is missing
    if issue not in ["MISSING_PAYMENT", "MISSING_SETTLEMENT"]:

        settlements.append([
            settlement_id,
            payment_id,
            settlement_amount,
            (invoice_date + timedelta(days=1)).strftime("%Y-%m-%d"),
            settlement_status
        ])

    # Ground truth
    ground_truth.append([
        invoice_id,
        issue
    ])


# Create DataFrames

invoice_columns = [
    "invoice_id",
    "customer_id",
    "invoice_amount",
    "invoice_date",
    "currency",
    "status"
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

settlement_columns = [
    "settlement_id",
    "payment_id",
    "settlement_amount",
    "settlement_date",
    "status"
]

ground_truth_columns = [
    "invoice_id",
    "expected_result"
]


invoice_df = pd.DataFrame(invoices, columns=invoice_columns)
payment_df = pd.DataFrame(payments, columns=payment_columns)
settlement_df = pd.DataFrame(settlements, columns=settlement_columns)
ground_truth_df = pd.DataFrame(
    ground_truth,
    columns=ground_truth_columns
)


# Save files

invoice_df.to_csv("data/invoices.csv", index=False)
payment_df.to_csv("data/payments.csv", index=False)
settlement_df.to_csv("data/settlements.csv", index=False)
ground_truth_df.to_csv("data/ground_truth.csv", index=False)


print("100 synthetic transactions created successfully!")
print()
print("Invoices:", len(invoice_df))
print("Payments:", len(payment_df))
print("Settlements:", len(settlement_df))
print("Ground truth:", len(ground_truth_df))