import os
from dotenv import load_dotenv
from openai import OpenAI

# Load the API key from .env
load_dotenv()

# Create OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# One exception from our reconciliation report
exception = {
    "invoice_id": "INV081",
    "invoice_amount": 2500,
    "payment_amount": 2500,
    "settlement_amount": 2000,
    "result": "SETTLEMENT_MISMATCH",
    "difference": 500
}


prompt = f"""
You are an AI Finance Controller assistant.

Analyze the following reconciliation exception.

Invoice ID: {exception["invoice_id"]}
Invoice amount: ₹{exception["invoice_amount"]}
Payment amount: ₹{exception["payment_amount"]}
Settlement amount: ₹{exception["settlement_amount"]}
Exception type: {exception["result"]}
Difference: ₹{exception["difference"]}

Explain:
1. What happened.
2. What the financial difference is.
3. What the finance team should investigate.

Important rules:
- Use only the information provided.
- Do not claim to know the exact cause if the data does not prove it.
- Clearly distinguish facts from possible causes.
- Keep the explanation concise and professional.
"""


response = client.responses.create(
    model="gpt-5.6-luna",
    input=prompt
)

print("\nAI FINANCE CONTROLLER")
print("-----------------------------")
print(response.output_text)