import pandas as pd


# Load the reconciliation report
report = pd.read_csv("data/exception_report.csv")


def finance_agent(question):

    question = question.lower().strip()

    # -----------------------------------------
    # 1. Total exceptions
    # -----------------------------------------

    if "how many exceptions" in question:
        return f"There are {len(report)} exceptions requiring attention."

    # -----------------------------------------
    # 2. Missing payments
    # -----------------------------------------

    if "missing payment" in question:
        data = report[
            report["result"] == "MISSING_PAYMENT"
        ]

        return (
            f"There are {len(data)} missing payment records."
        )

    # -----------------------------------------
    # 3. Payment mismatches
    # -----------------------------------------

    if "payment mismatch" in question:
        data = report[
            report["result"] == "PAYMENT_MISMATCH"
        ]

        total_difference = data["difference"].sum()

        return (
            f"There are {len(data)} payment mismatches. "
            f"The total payment difference is "
            f"₹{total_difference:.2f}."
        )

    # -----------------------------------------
    # 4. Settlement mismatches
    # -----------------------------------------

    if "settlement mismatch" in question:
        data = report[
            report["result"] == "SETTLEMENT_MISMATCH"
        ]

        total_difference = data["difference"].sum()

        return (
            f"There are {len(data)} settlement mismatches. "
            f"The total settlement difference is "
            f"₹{total_difference:.2f}."
        )

    # -----------------------------------------
    # 5. Invalid references
    # -----------------------------------------

    if "invalid reference" in question:
        data = report[
            report["result"] == "INVALID_REFERENCE"
        ]

        return (
            f"There are {len(data)} invalid payment references."
        )

    # -----------------------------------------
    # 6. Total financial discrepancy
    # -----------------------------------------

    if (
        "discrepancy" in question
        or "total difference" in question
        or "money involved" in question
    ):

        data = report.dropna(
            subset=["difference"]
        )

        total_difference = data["difference"].abs().sum()

        return (
            f"The total measurable financial discrepancy "
            f"across the exception report is "
            f"₹{total_difference:.2f}."
        )

    # -----------------------------------------
    # 7. Highest priority exceptions
    # -----------------------------------------

    if (
    "biggest" in question
    or "largest" in question
    or "highest priority" in question
    or "prioritize" in question
    or (
        "priority" in question
        and "high priority" not in question
        and "high-priority" not in question
    )
):

        data = report.dropna(
            subset=["difference"]
        ).copy()

        if len(data) == 0:
            return (
                "There are no exceptions with a measurable "
                "financial difference."
            )

        # Rank by absolute financial difference
        data["priority_amount"] = data["difference"].abs()

        data = data.sort_values(
            by="priority_amount",
            ascending=False
        )

        top = data.head(5)

        answer = "TOP PRIORITY EXCEPTIONS:\n\n"

        for index, row in enumerate(
            top.itertuples(),
            start=1
        ):
            answer += (
                f"{index}. {row.invoice_id} - "
                f"{row.result} - "
                f"Difference: ₹{abs(row.difference):.2f}\n"
            )

        return answer
        # -----------------------------------------
    # High priority count
    # -----------------------------------------

    if (
        "how many high priority" in question
        or "how many high-priority" in question
    ):

        data = report[
            report["severity"] == "HIGH"
        ]

        return (
            f"There are {len(data)} high-priority "
            f"exceptions requiring immediate attention."
        )


    # -----------------------------------------
    # Show high priority exceptions
    # -----------------------------------------

    if (
        "show high priority" in question
        or "show high-priority" in question
        or "high priority exceptions" in question
    ):

        data = report[
            report["severity"] == "HIGH"
        ]

        if len(data) == 0:
            return "There are no high-priority exceptions."

        answer = "HIGH PRIORITY EXCEPTIONS:\n\n"

        for index, row in enumerate(
            data.itertuples(),
            start=1
        ):

            difference = (
                "N/A"
                if pd.isna(row.difference)
                else f"₹{abs(row.difference):.2f}"
            )

            answer += (
                f"{index}. {row.invoice_id} - "
                f"{row.result} - "
                f"Difference: {difference}\n"
            )

        return answer


    # -----------------------------------------
    # Severity question for specific invoice
    # -----------------------------------------

    if "severity" in question and "inv" in question:

        words = question.upper().split()

        invoice_id = None

        for word in words:

            if word.startswith("INV"):

                invoice_id = word.strip(
                    ".,?!"
                )

        if invoice_id:

            data = report[
                report["invoice_id"] == invoice_id
            ]

            if len(data) == 0:

                return (
                    f"{invoice_id} does not appear "
                    "in the exception report."
                )

            row = data.iloc[0]

            return (
                f"{invoice_id} has "
                f"{row['severity']} severity. "
                f"Exception type: {row['result']}."
            )


    # -----------------------------------------
    # Recommended action for invoice
    # -----------------------------------------

    if (
        ("what should" in question
         or "what do" in question
         or "action" in question
         or "how should" in question)
        and "inv" in question
    ):

        words = question.upper().split()

        invoice_id = None

        for word in words:

            if word.startswith("INV"):

                invoice_id = word.strip(
                    ".,?!"
                )

        if invoice_id:

            data = report[
                report["invoice_id"] == invoice_id
            ]

            if len(data) == 0:

                return (
                    f"{invoice_id} does not appear "
                    "in the exception report."
                )

            row = data.iloc[0]

            return (
                f"For {invoice_id}, the recommended "
                f"action is: {row['recommended_action']}"
            )

    # -----------------------------------------
    # 8. Specific invoice
    # -----------------------------------------

    if "inv" in question:

        words = question.upper().split()

        invoice_id = None

        for word in words:

            if word.startswith("INV"):
                invoice_id = word.strip(".,?!")

        if invoice_id:

            data = report[
                report["invoice_id"] == invoice_id
            ]

            if len(data) == 0:
                return (
                    f"{invoice_id} does not appear in the "
                    "exception report. It may have been "
                    "successfully reconciled."
                )

            row = data.iloc[0]

            return (
                f"{invoice_id} has a {row['result']}. "
                f"Invoice amount: ₹{row['invoice_amount']:.2f}. "
                f"Payment amount: "
                f"₹{row['payment_amount']:.2f}. "
                f"Settlement amount: "
                f"₹{row['settlement_amount']:.2f}. "
                f"Explanation: {row['explanation']}"
            )

    # -----------------------------------------
    # 9. Default response
    # -----------------------------------------

    return (
        "I can answer questions about exceptions, "
        "missing payments, payment mismatches, "
        "settlement mismatches, invalid references, "
        "specific invoices, total discrepancies, "
        "and priority exceptions."
    )


# ---------------------------------------------
# Interactive agent
# ---------------------------------------------

print("\n======================================")
print("     FINANCIAL RECONCILIATION AGENT")
print("======================================")

print("\nAsk a question about the reconciliation data.")
print("Type 'exit' to stop.\n")


if __name__ == "__main__":
    print("=" * 40)
    print("     FINANCIAL RECONCILIATION AGENT")
    print("=" * 40)

    print("\nAsk a question about the reconciliation data.")
    print("Type 'exit' to stop.\n")

    while True:
        question = input("You: ")

        if question.lower().strip() == "exit":
            break

        answer = finance_agent(question)
        print("Agent:", answer)