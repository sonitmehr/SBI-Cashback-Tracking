import pdfplumber
import re
import json


# -----------------------------
# READ PDF AS ONE STRING
# -----------------------------
def read_pdf_as_string():

    text = ""

    with pdfplumber.open("CardStatement_2026-02-22.pdf") as pdf:
        for page in pdf.pages:
            text += page.extract_text()
            

    return text


# -----------------------------
# PARSER
# -----------------------------
def parse_statement(text):

    result = {}

    # -------------------------
    # CUSTOMER NAME
    # -------------------------
    name_match = re.search(r'([A-Z ]+)\s+Credit Card Number', text)
    if name_match:
        result["Customer name"] = name_match.group(1).strip()

    # -------------------------
    # TOTAL AMOUNT DUE
    # -------------------------
    total_match = re.search(r'Total Amount Due.*?([\d,]+\.\d{2})', text, re.S)
    if total_match:
        result["Total amount due"] = total_match.group(1)

    # -------------------------
    # MINIMUM AMOUNT DUE
    # -------------------------
    min_match = re.search(r'Minimum Amount Due.*?([\d,]+\.\d{2})', text, re.S)
    if min_match:
        result["Minimum amount due"] = min_match.group(1)

    # -------------------------
    # PAYMENT DUE DATE
    # -------------------------
    due_match = re.search(r'Payment Due Date\s*([\d]{1,2}\s+\w+\s+\d{4})', text)
    if due_match:
        result["Payment Due Date"] = due_match.group(1)

    # -------------------------
    # CASHBACK
    # -------------------------
    cashback_match = re.search(r'CARD CASHBACK SUMMARY.*?(\d+)', text, re.S)
    if cashback_match:
        result["Cashback amount"] = cashback_match.group(1)

    # -------------------------
    # TRANSACTIONS
    # -------------------------
    transactions = []

    pattern = re.compile(
        r'(\d{2}\s\w{3}\s\d{2})\s+(.+?)\s+([\d,]+\.\d{2})\s+([CD])'
    )

    for match in pattern.finditer(text):

        date = match.group(1)
        name = match.group(2).strip()
        amount = match.group(3).replace(",", "")
        ttype = match.group(4)

        transactions.append({
            "Transaction date": date,
            "Transaction Name": name,
            "Amount": amount,
            "Type": ttype
        })

    result["Transactions Details"] = transactions

    return result


# -----------------------------
# MAIN
# -----------------------------
def main():


    # Read entire PDF as single string
    pdf_text = read_pdf_as_string()

    # Run parsing logic
    parsed_data = parse_statement(pdf_text)

    # Print JSON
    print(json.dumps(parsed_data, indent=4))

    # Save JSON
    with open("output.json", "w") as f:
        json.dump(parsed_data, f, indent=4)


if __name__ == "__main__":
    main()