# SBI Card Statement Parser - Web Application

A web-based tool to parse SBI credit card statement PDFs and extract transaction details.

## Features

- **Drag & Drop Upload**: Easily upload PDF statements by dragging and dropping
- **Instant Parsing**: Parse PDFs using the existing pdfplumber-based parser
- **Beautiful UI**: Modern, responsive interface with gradient design
- **Summary Dashboard**: View customer details, amounts due, and cashback at a glance
- **Transaction Table**: Browse all transactions with debit/credit indicators
- **JSON Export**: Download parsed data as JSON for further processing

## Installation

1. Install dependencies:
```bash
pip install -r ../requirements.txt
```

## Usage

1. Run the Flask application:
```bash
cd web
python app.py
```

2. Open your browser and navigate to:
```
http://localhost:5000
```

3. Upload your SBI card statement PDF:
   - Drag and drop the PDF onto the upload area
   - Or click to browse and select a file

4. Click "Parse Statement" to process the PDF

5. View the results:
   - Summary cards show key information
   - Transaction table lists all transactions
   - Click "Download JSON" to export the data

## Technology Stack

- **Backend**: Flask (Python)
- **Frontend**: HTML, CSS, JavaScript (vanilla)
- **PDF Parsing**: pdfplumber
- **File Upload**: Flask's built-in file handling

## File Structure

```
web/
├── app.py              # Flask backend with PDF parsing logic
├── templates/
│   └── index.html      # Frontend UI
├── uploads/            # Temporary upload directory (auto-created)
└── README.md           # This file
```

## Notes

- Maximum file size: 16MB
- Supported format: PDF only
- Uploaded files are automatically deleted after parsing
- The application runs in debug mode by default

## Integration with Existing Scripts

This web app integrates the parsing logic from `read_pdf.py` directly into the Flask backend, making it accessible via a web interface instead of command-line usage.
