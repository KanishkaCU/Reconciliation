import pandas as pd


def reconcile_data(invoices, payments, settlements):

      
    # STEP 1: Identify payments by customer
      

    payment_by_customer = (
        payments.groupby("customer_id")["payment_id"]
        .apply(list)
        .to_dict()
    )

      
    # STEP 2: Merge invoices with payments
      

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

      
    # STEP 3: Reconciliation rules
      

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

    reconciliation["result"] = reconciliation.apply(
        check_transaction,
        axis=1
    )

      
    # STEP 4: Explanations
      

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
                row["invoice_amount"]
                - row["payment_amount"]
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
                row["payment_amount"]
                - row["settlement_amount"]
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

      
    # STEP 5: Recommended action
      

    def recommend_action(row):

        result = row["result"]

        if result == "MATCHED":
            return "No action required."

        if result == "PAYMENT_MISMATCH":
            return (
                "Review the invoice and payment records "
                "and verify the payment amount."
            )

        if result == "SETTLEMENT_MISMATCH":
            return (
                "Verify the settlement amount against "
                "the payment record."
            )

        if result == "MISSING_PAYMENT":
            return (
                "Check payment gateway or bank records "
                "for the missing payment."
            )

        if result == "MISSING_SETTLEMENT":
            return (
                "Check settlement processing status and "
                "verify whether the payment was settled."
            )

        if result == "INVALID_REFERENCE":
            return (
                "Investigate the payment reference and "
                "identify the correct invoice."
            )

        return "Review transaction manually."

    reconciliation["recommended_action"] = (
        reconciliation.apply(
            recommend_action,
            axis=1
        )
    )

      
    # STEP 6: Exception report
      

    exceptions = reconciliation[
        reconciliation["result"] != "MATCHED"
    ].copy()

      
    # STEP 7: Financial difference
      

    def calculate_difference(row):

        if row["result"] == "PAYMENT_MISMATCH":

            return (
                row["invoice_amount"]
                - row["payment_amount"]
            )

        if row["result"] == "SETTLEMENT_MISMATCH":

            return (
                row["payment_amount"]
                - row["settlement_amount"]
            )

        return None

    exceptions["difference"] = exceptions.apply(
        calculate_difference,
        axis=1
    )

      
    # STEP 8: Assign severity
      

    def calculate_severity(row):

        result = row["result"]
        difference = row["difference"]

        # Missing payment or invalid reference
        # requires immediate investigation
        if result in [
            "MISSING_PAYMENT",
            "INVALID_REFERENCE"
        ]:
            return "HIGH"

        # Financial mismatch severity
        if pd.notna(difference):

            if abs(difference) >= 500:
                return "HIGH"

            if abs(difference) >= 200:
                return "MEDIUM"

            return "LOW"

        # Missing settlement
        if result == "MISSING_SETTLEMENT":
            return "MEDIUM"

        return "LOW"

    exceptions["severity"] = exceptions.apply(
        calculate_severity,
        axis=1
    )

      
    # STEP 9: Select report columns
      

    exception_report = exceptions[
        [
            "invoice_id",
            "invoice_amount",
            "payment_amount",
            "settlement_amount",
            "result",
            "difference",
            "severity",
            "explanation",
            "recommended_action"
        ]
    ].copy()

    return reconciliation, exception_report


 
# COMMAND-LINE EXECUTION
 

if __name__ == "__main__":

    invoices = pd.read_csv(
        "data/invoices.csv"
    )

    payments = pd.read_csv(
        "data/payments.csv"
    )

    settlements = pd.read_csv(
        "data/settlements.csv"
    )

    reconciliation, exception_report = reconcile_data(
        invoices,
        payments,
        settlements
    )

      
    # Display results
      

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

      
    # Summary
      

    total_records = len(reconciliation)

    matched_records = len(
        reconciliation[
            reconciliation["result"] == "MATCHED"
        ]
    )

    exceptions_count = (
        total_records - matched_records
    )

    match_rate = (
        matched_records / total_records
    ) * 100

    print("\n-----------------------------")
    print(f"Total records   : {total_records}")
    print(f"Matched records : {matched_records}")
    print(f"Exceptions      : {exceptions_count}")
    print(f"Match rate      : {match_rate:.2f}%")
    print("-----------------------------")

      
    # Save exception report
      

    exception_report.to_csv(
        "data/exception_report.csv",
        index=False
    )

    print("\nEXCEPTION REPORT")
    print("-----------------------------")

    print(
        exception_report.to_string(index=False)
    )

    print("\nException report saved to:")
    print("data/exception_report.csv")