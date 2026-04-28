from flask import Flask, request, jsonify, render_template, send_file
import json
import os
import csv
import logging
from datetime import datetime
from openpyxl import Workbook
from openpyxl.worksheet.table import Table, TableStyleInfo
from werkzeug.utils import secure_filename
from io import BytesIO
from helpers.utils import read_pdf_as_string, resolve_mode_from_csv, parse_statement, load_merchants_csv, get_mode_for_merchant, convert_display_mode_to_internal

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# Create upload directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Load merchants CSV
merchants_csv_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'merchants.csv')
merchants_map = load_merchants_csv(merchants_csv_path)


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/get-merchants-map')
def get_merchants_map():
    """
    Return the merchants mapping for prefilling modes in the UI.
    """
    return jsonify({'merchants_map': merchants_map})


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    password = request.form.get('password', None)
    
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        try:
            # Parse the PDF with password if provided
            pdf_text = read_pdf_as_string(filepath, password)
            
            # Log raw PDF text
            print(f"\n{'='*80}")
            print(f"Raw PDF text:")
            print(f"{'='*80}")
            print(pdf_text)
            print(f"{'='*80}\n")
            
            parsed_data = parse_statement(pdf_text)
            
            # Log parsed data
            print(f"\n{'='*80}")
            print(f"Parsed PDF data:")
            print(f"{'='*80}")
            print(json.dumps(parsed_data, indent=2))
            print(f"{'='*80}\n")
            
            # Clean up uploaded file
            os.remove(filepath)
            
            return jsonify({
                'success': True,
                'data': parsed_data
            })
        except Exception as e:
            # Clean up uploaded file on error
            if os.path.exists(filepath):
                os.remove(filepath)
            return jsonify({'error': f'Error parsing PDF: {str(e)}'}), 500
    
    return jsonify({'error': 'Invalid file type. Please upload a PDF.'}), 400


@app.route('/generate-excel', methods=['POST'])
def generate_excel():
    try:
        data = request.json
        transactions = data.get('transactions', [])
        cashback = data.get('cashback', 0)
        
        if not transactions:
            return jsonify({'error': 'No transactions provided'}), 400
        
        # Get month from first transaction
        first_txn = transactions[0]
        txn_date = first_txn.get('Transaction date', '')
        if txn_date:
            parts = txn_date.split()
            if len(parts) >= 2:
                month_label = parts[1]
            else:
                month_label = 'Unknown'
        else:
            month_label = 'Unknown'
        
        YEAR = "2026"
        SHEET_NAME = "Transactions"
        
        headers = [
            "Date",
            "Merchant Name",
            "Amount",
            "Type",
            "Mode",
            "Cashback Expected",
            "Net Payment",
            "Done By"
        ]
        
        month_map = {
            "Jan": "01", "Feb": "02", "Mar": "03",
            "Apr": "04", "May": "05", "Jun": "06",
            "Jul": "07", "Aug": "08", "Sep": "09",
            "Oct": "10", "Nov": "11", "Dec": "12"
        }
        
        rows = []
        
        for txn in transactions:
            txn_date = txn.get('Transaction date', '')
            merchant = txn.get('Transaction Name', '')
            amount = float(txn.get('Amount', 0))
            txn_type = txn.get('Type', 'D')
            done_by = txn.get('done_by', 'User')
            display_mode = txn.get('mode', '')
            
            # Parse date
            parts = txn_date.split()
            if len(parts) >= 3:
                day, month, year = parts[0], parts[1], parts[2]
                date = f"{YEAR}-{month_map.get(month, '01')}-{day}"
            else:
                date = txn_date
            
            # Convert display mode (Online/Offline/Not Eligible) to internal mode (ON/OFF/NO)
            mode = convert_display_mode_to_internal(display_mode) if display_mode else None
            
            # If mode is still None, try to resolve from CSV as fallback
            if not mode:
                mode = resolve_mode_from_csv(merchant, None, merchants_map)
            
            # Credit -> negative
            if txn_type == 'C':
                amount = -abs(amount)
                txn_type = "Credit"
            else:
                amount = abs(amount)
                txn_type = "Debit"
            
            rows.append([
                date,
                merchant.strip(),
                amount,
                txn_type,
                mode,
                done_by
            ])
        
        # Create Workbook
        wb = Workbook()
        ws = wb.active
        ws.title = SHEET_NAME
        ws.append(headers)
        
        # Write Data
        for i, r in enumerate(rows, start=2):
            ws.cell(i, 1, r[0])
            ws.cell(i, 2, r[1])
            ws.cell(i, 3, r[2])
            ws.cell(i, 4, r[3])
            ws.cell(i, 5, r[4])
            
            # Cashback rule
            ws.cell(
                i, 6,
                (
                    f'=IF(ABS(C{i})<100,0,'
                    f'FLOOR('
                    f'ABS(C{i})*IF(E{i}="ON",0.05,IF(E{i}="OFF",0.01,0)),'
                    f'1'
                    f')*SIGN(C{i})'
                    f')'
                )
            )
            
            ws.cell(i, 7, f"=C{i}-F{i}")
            ws.cell(i, 8, r[5])
        
        # Create Table
        end_row = ws.max_row
        table = Table(displayName="TransactionTable", ref=f"A1:H{end_row}")
        style = TableStyleInfo(name="TableStyleMedium9", showRowStripes=True)
        table.tableStyleInfo = style
        ws.add_table(table)
        
        # Summary
        summary_row = end_row + 2
        
        ws.cell(summary_row, 2, "Total Transaction Amount")
        ws.cell(summary_row, 3, f"=SUM(C2:C{end_row})")
        
        ws.cell(summary_row + 1, 2, "Total Cashback Expected")
        ws.cell(summary_row + 1, 3, f"=SUM(F2:F{end_row})")
        
        ws.cell(summary_row + 2, 2, "Cashback Received")
        ws.cell(summary_row + 2, 3, cashback)
        
        ws.cell(summary_row + 3, 2, "Cashback Difference")
        ws.cell(summary_row + 3, 3, f"=C{summary_row + 1}-C{summary_row + 2}")
        
        # Payment Pending Per User
        users = sorted(set(r[5] for r in rows if r[5]))
        
        start_col = 10
        ws.cell(2, start_col, "Payment Pending From")
        
        for idx, user in enumerate(users, start=1):
            row = 2 + idx
            ws.cell(row, start_col, user)
            ws.cell(
                row,
                start_col + 1,
                f'=SUMIF(H2:H{end_row},"{user}",G2:G{end_row})'
            )
        
        # Totals & Reconciliation
        recon_start_row = 2 + len(users) + 2
        recon_col = start_col
        
        ws.cell(recon_start_row, recon_col, "Total Pending Payments")
        ws.cell(
            recon_start_row,
            recon_col + 1,
            f"=SUM(K3:K{2 + len(users)})"
        )
        
        ws.cell(recon_start_row + 1, recon_col, "Cashback Received")
        ws.cell(
            recon_start_row + 1,
            recon_col + 1,
            f"=C{summary_row + 2}"
        )
        
        ws.cell(recon_start_row + 2, recon_col, "Reconciliation Status")
        ws.cell(
            recon_start_row + 2,
            recon_col + 1,
            (
                f'=IF('
                f'C{summary_row}=('
                f'K{recon_start_row}+K{recon_start_row + 1}'
                f'),'
                f'"Everything adds up",'
                f'"Something is not adding up"'
                f')'
            )
        )
        
        # Save to BytesIO for in-memory download
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        
        # Send file directly to browser
        return send_file(
            output,
            as_attachment=True,
            download_name='statement.xlsx',
            mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        
    except Exception as e:
        return jsonify({'error': f'Error generating Excel: {str(e)}'}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000)
