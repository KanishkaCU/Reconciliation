import streamlit as st
import pandas as pd
from reconcile import reconcile_data
import finance_agent as fa
# ==================================================
# PAGE CONFIGURATION
# ==================================================

st.set_page_config(
    page_title="Financial Reconciliation Agent",
    page_icon="💰",
    layout="wide"
)



# ==================================================
# HEADER
# ==================================================

st.title(
    "Financial Reconciliation Agent"
)

st.write(
    "Automated reconciliation of invoices, "
    "payments, and settlements."
)


# ==================================================
# DATA SOURCE
# ==================================================

st.subheader(
    "Financial Data"
)

data_option = st.radio(
    "Choose data source",
    [
        "Use Demo Data",
        "Upload CSV Files"
    ],
    horizontal=True
)


# ==================================================
# DEMO DATA
# ==================================================

if data_option == "Use Demo Data":

    invoices = pd.read_csv(
        "data/invoices.csv"
    )

    payments = pd.read_csv(
        "data/payments.csv"
    )

    settlements = pd.read_csv(
        "data/settlements.csv"
    )

    st.success(
        "Using the 100-record demonstration dataset."
    )


# ==================================================
# UPLOAD DATA
# ==================================================

else:

    col1, col2, col3 = st.columns(3)

    with col1:

        invoice_file = st.file_uploader(
            "Upload Invoices CSV",
            type=["csv"]
        )

    with col2:

        payment_file = st.file_uploader(
            "Upload Payments CSV",
            type=["csv"]
        )

    with col3:

        settlement_file = st.file_uploader(
            "Upload Settlements CSV",
            type=["csv"]
        )

    if (
        invoice_file is None
        or payment_file is None
        or settlement_file is None
    ):

        st.info(
            "Upload all three CSV files to continue."
        )

        st.stop()

    invoices = pd.read_csv(
        invoice_file
    )

    payments = pd.read_csv(
        payment_file
    )

    settlements = pd.read_csv(
        settlement_file
    )

    st.success(
        "All three files uploaded successfully."
    )


# ==================================================
# RUN RECONCILIATION
# ==================================================

if st.button(
    "Run Reconciliation",
    type="primary"
):

    reconciliation, exception_report = reconcile_data(
        invoices,
        payments,
        settlements
    )

    st.session_state["reconciliation"] = reconciliation
    st.session_state["result"] = exception_report


# ==================================================
# SHOW RESULTS
# ==================================================

if "reconciliation" not in st.session_state:

    st.info(
        "Click 'Run Reconciliation' to analyze the data."
    )

    st.stop()


reconciliation = st.session_state["reconciliation"]
exception_report = st.session_state["result"]

result = reconciliation
exceptions = exception_report

# ==================================================
# METRICS
# ==================================================

total_records = len(result)

matched_records = len(
    result[
        result["result"] == "MATCHED"
    ]
)

exceptions = st.session_state["result"]

exception_count = len(exceptions)

match_rate = (
    matched_records / total_records
) * 100

measurable = exceptions.dropna(
    subset=["difference"]
)

total_discrepancy = measurable[
    "difference"
].abs().sum()


# ==================================================
# KPI CARDS
# ==================================================

st.divider()

col1, col2, col3, col4, col5 = st.columns(5)

with col1:

    st.metric(
        "Total Records",
        total_records
    )

with col2:

    st.metric(
        "Matched",
        matched_records
    )

with col3:

    st.metric(
        "Exceptions",
        exception_count
    )

with col4:

    st.metric(
        "Match Rate",
        f"{match_rate:.1f}%"
    )

with col5:

    st.metric(
        "Discrepancy",
        f"₹{total_discrepancy:,.0f}"
    )


# ==================================================
# EXCEPTION BREAKDOWN
# ==================================================

st.divider()

st.subheader(
    "Exception Analysis"
)

exception_types = [
    "ALL"
] + sorted(
    exceptions["result"].unique().tolist()
)

selected_type = st.selectbox(
    "Filter by exception type",
    exception_types
)

if selected_type == "ALL":

    filtered = exceptions

else:

    filtered = exceptions[
        exceptions["result"]
        == selected_type
    ]

st.write(
    f"Showing **{len(filtered)}** exceptions"
)

st.dataframe(
    filtered[
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
    ],
    use_container_width=True,
    hide_index=True
)


# ==================================================
# PRIORITY EXCEPTIONS
# ==================================================

st.divider()

st.subheader(
    "Highest Priority Exceptions"
)

priority_data = exceptions.dropna(
    subset=["difference"]
).copy()

if len(priority_data) > 0:

    priority_data["priority_amount"] = (
        priority_data["difference"].abs()
    )

    priority_data = priority_data.sort_values(
        "priority_amount",
        ascending=False
    )

    st.dataframe(
        priority_data.head(5)[
            [
                "invoice_id",
                "result",
                "difference",
                "explanation"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

else:

    st.info(
        "No measurable financial exceptions."
    )

# ==================================================
# FINANCE AGENT
# ==================================================

st.divider()

st.subheader("Finance Agent")

st.write(
    "Ask questions about the current reconciliation results."
)

question = st.text_input(
    "Ask the Finance Agent",
    placeholder="Example: How many high priority exceptions?"
)

if question:

    # Give the Finance Agent the current report
    fa.report = exception_report.copy()

    answer = fa.finance_agent(question)

    st.info(answer)

# ==================================================
# HIGH PRIORITY EXCEPTIONS
# ==================================================

st.divider()

st.subheader("High Priority Exceptions")

high_priority = exceptions[
    exceptions["severity"] == "HIGH"
].copy()

st.write(
    f"Showing {len(high_priority)} high-priority exceptions."
)

if len(high_priority) > 0:

    st.dataframe(
        high_priority[
            [
                "invoice_id",
                "result",
                "difference",
                "severity",
                "explanation",
                "recommended_action"
            ]
        ],
        use_container_width=True,
        hide_index=True
    )

else:

    st.success(
        "No high-priority exceptions found."
    )
# ==================================================
# DOWNLOAD EXCEPTION REPORT
# ==================================================

st.divider()

st.subheader("Export Reports")

csv_data = exception_report.to_csv(
    index=False
).encode("utf-8")

st.download_button(
    label="Download Exception Report",
    data=csv_data,
    file_name="financial_exception_report.csv",
    mime="text/csv"
)