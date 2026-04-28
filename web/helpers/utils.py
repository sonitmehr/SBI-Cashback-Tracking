import pdfplumber
import re
import csv
import os


def read_pdf_as_string(pdf_path, password=None):
    """
    Read PDF file and return text as a single string.
    Supports password-protected PDFs.
    """
    text = ""
    try:
        if password:
            with pdfplumber.open(pdf_path, password=password) as pdf:
                for page in pdf.pages:
                    text += page.extract_text()
        else:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text += page.extract_text()
    except Exception as e:
        raise Exception(f"Failed to open PDF: {str(e)}")
    return text


def resolve_mode_from_csv(merchant_name, current_mode, merchant_mode_map):
    """
    Returns updated mode based on CSV mapping.
    """
    for csv_merchant, csv_mode in merchant_mode_map.items():
        if csv_merchant.lower() in merchant_name.lower():
            return csv_mode
    return current_mode


def parse_statement(text):
    """
    Parse SBI card statement text and extract structured data.
    Returns a dictionary with customer info, amounts, and transactions.
    """
    result = {}

    # Customer Name
    name_match = re.search(r'([A-Z ]+)\s+Credit Card Number', text)
    if name_match:
        result["Customer name"] = name_match.group(1).strip()

    # Total Amount Due
    total_match = re.search(r'Total Amount Due.*?([\d,]+\.\d{2})', text, re.S)
    if total_match:
        result["Total amount due"] = total_match.group(1)

    # Minimum Amount Due
    min_match = re.search(r'Minimum Amount Due.*?([\d,]+\.\d{2})', text, re.S)
    if min_match:
        result["Minimum amount due"] = min_match.group(1)

    # Statement Date - try multiple patterns
    statement_date_match = re.search(r'Statement Date\s*[:\-]?\s*([\d]{1,2}\s+\w+\s+\d{4})', text)
    if not statement_date_match:
        statement_date_match = re.search(r'Statement dated\s*[:\-]?\s*([\d]{1,2}\s+\w+\s+\d{4})', text)
    if not statement_date_match:
        statement_date_match = re.search(r'Statement Date is\s+([\d]{1,2}\w+\s+of\s+\w+\s+Month)', text)
    if not statement_date_match:
        # Look for date pattern near "Statement" in the text
        statement_date_match = re.search(r'Statement.*?(\d{1,2}\s+\w{3}\s+\d{2,4})', text, re.IGNORECASE)
    
    if statement_date_match:
        result["Statement Date"] = statement_date_match.group(1)
        # Extract month from statement date
        date_parts = statement_date_match.group(1).split()
        if len(date_parts) >= 2:
            month = date_parts[1]
            # Clean up month name (remove "of" if present)
            month = month.replace("of", "").strip()
            result["Statement Month"] = month
    
    # Fallback: extract month from first transaction if statement date not found
    if "Statement Month" not in result:
        first_txn_match = re.search(r'(\d{2}\s\w{3}\s\d{2})', text)
        if first_txn_match:
            date_parts = first_txn_match.group(1).split()
            if len(date_parts) >= 2:
                result["Statement Month"] = date_parts[1]
            # Use first transaction date as statement date fallback
            result["Statement Date"] = first_txn_match.group(1)

    # Payment Due Date
    due_match = re.search(r'Payment Due Date\s*([\d]{1,2}\s+\w+\s+\d{4})', text)
    if due_match:
        result["Payment Due Date"] = due_match.group(1)

    # Cashback
    cashback_match = re.search(r'CARD CASHBACK SUMMARY.*?(\d+)', text, re.S)
    if cashback_match:
        result["Cashback amount"] = cashback_match.group(1)

    # Transactions
    transactions = []
    pattern = re.compile(r'(\d{2}\s\w{3}\s\d{2})\s+(.+?)\s+([\d,]+\.\d{2})\s+([CD])')

    for match in pattern.finditer(text):
        date = match.group(1)
        name = match.group(2).strip()
        amount = match.group(3).replace(",", "")
        ttype = match.group(4)

        # Filter out PAYMENT RECEIVED entries
        if "PAYMENT RECEIVED" not in name.upper():
            transactions.append({
                "Transaction date": date,
                "Transaction Name": name,
                "Amount": amount,
                "Type": ttype
            })

    result["Transactions Details"] = transactions
    return result


def load_merchants_csv(csv_path):
    """
    Load merchants CSV file and return a dictionary mapping merchant names to modes.
    """
    merchants_map = {}
    if os.path.exists(csv_path):
        with open(csv_path, newline="", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                merchants_map[row["Merchant Name"].strip()] = row["Mode"].strip().upper()
    return merchants_map


def get_mode_for_merchant(merchant_name, merchants_map):
    """
    Get the display mode (Online/Offline/Not Eligible) for a merchant based on CSV mapping.
    Returns None if merchant not found in CSV.
    """
    mode = resolve_mode_from_csv(merchant_name, None, merchants_map)
    if mode == "ON":
        return "Online"
    elif mode == "OFF":
        return "Offline"
    elif mode == "NO":
        return "Not Eligible"
    return None


def convert_display_mode_to_internal(display_mode):
    """
    Convert display mode (Online/Offline/Not Eligible) to internal mode (ON/OFF/NO).
    """
    mode_map = {
        "Online": "ON",
        "Offline": "OFF",
        "Not Eligible": "NO"
    }
    return mode_map.get(display_mode, None)
