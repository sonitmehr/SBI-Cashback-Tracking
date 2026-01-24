import json
import re
from datetime import datetime
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
import csv
import copy
from helper import resolve_mode_from_csv
from raw_data.january_2026 import input_json

# ---- Timestamped filename ----
timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
FILE_NAME = f"statements/transactions_{timestamp}.xlsx"
SHEET_NAME = "Transactions"

headers = [
    "Date",
    "Merchant Name",
    "Amount",
    "Type",
    "Mode",
    "Cashback Expected"
]

# ---- Raw Data ----
raw_data_json = input_json
merchants_map = {}

print("\n📄 Reading merchants.csv\n")

with open("merchants.csv", newline="", encoding="utf-8") as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        merchant = row["Merchant Name"].strip()
        mode = row["Mode"].strip().upper()
        merchants_map[merchant] = mode

print("\n✅ Merchant mode mapping loaded\n")


entries = json.loads(raw_data_json)

# ---- Helpers ----
month_map = {
    "Jan": "01", "Feb": "02", "Mar": "03",
    "Apr": "04", "May": "05", "Jun": "06",
    "Jul": "07", "Aug": "08", "Sep": "09",
    "Oct": "10", "Nov": "11", "Dec": "12"
}

pattern = re.compile(
    r"(\d{2}) (\w{3}) \d{2} (.+) ([\d,]+\.\d{2}) ([DC]) (ON|OFF|NO)$"
)

rows = []

for entry in entries:
    m = pattern.search(entry)
    if not m:
        raise ValueError(f"Invalid entry: {entry}")

    day, month, merchant, amt_raw, txn_type, mode = m.groups()

    # 🔽 Resolve ON / OFF / NO using CSV
    mode = resolve_mode_from_csv(
        entry=entry,
        merchant_name=merchant,
        current_mode=mode,
        merchant_mode_map=merchants_map
    )

    date = f"2026-{month_map[month]}-{day}"
    amount = float(amt_raw.replace(",", ""))
    txn_type = "Debit" if txn_type == "D" else "Credit"

    rows.append([date, merchant.strip(), amount, txn_type, mode])

# ---- Workbook ----
wb = Workbook()
ws = wb.active
ws.title = SHEET_NAME
ws.append(headers)

for i, r in enumerate(rows, start=2):
    ws.cell(i, 1, r[0])
    ws.cell(i, 2, r[1])
    ws.cell(i, 3, r[2])
    ws.cell(i, 4, r[3])
    ws.cell(i, 5, r[4])

    ws.cell(
        i, 6,
        f'=FLOOR(C{i}*IF(E{i}="ON",0.05,IF(E{i}="OFF",0.01,0)),1)'
    )

# ---- Table ----
end_row = ws.max_row
table = Table(displayName="TransactionTable", ref=f"A1:F{end_row}")
style = TableStyleInfo(name="TableStyleMedium9", showRowStripes=True)
table.tableStyleInfo = style
ws.add_table(table)

# ---- Summary ----
# ---- Summary ----
summary_row = end_row + 2

# Total Transaction Amount
ws.cell(summary_row, 2, "Total Transaction Amount")
ws.cell(summary_row, 3, f"=SUM(C2:C{end_row})")

# Total Cashback Expected
ws.cell(summary_row + 1, 2, "Total Cashback Expected")
ws.cell(summary_row + 1, 3, f"=SUM(F2:F{end_row})")

# Cashback Received (HARDCODED)
cashback_received = 1009  # 👈 change this value as needed
ws.cell(summary_row + 2, 2, "Cashback Received")
ws.cell(summary_row + 2, 3, cashback_received)

# Cashback Difference (Expected - Received)
ws.cell(summary_row + 3, 2, "Cashback Difference")
ws.cell(
    summary_row + 3,
    3,
    f"=C{summary_row + 1}-C{summary_row + 2}"
)
# ---- Save ----
wb.save(FILE_NAME)
print(f"✅ Excel generated: {FILE_NAME}")
