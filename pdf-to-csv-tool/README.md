# PDF to CSV Extractor

A tool to extract text from PDF files (including scanned documents) and convert it to CSV format.

## Prerequisites

1. Install Tesseract OCR:
   - On macOS: `brew install tesseract`
   - On Ubuntu/Debian: `sudo apt-get install tesseract-ocr`
   - On Windows: Download and install from [GitHub](https://github.com/UB-Mannheim/tesseract/wiki)

2. Install Poppler (required for PDF to image conversion):
   - On macOS: `brew install poppler`
   - On Ubuntu/Debian: `sudo apt-get install poppler-utils`
   - On Windows: Download from [poppler releases](http://blog.alivate.com.au/poppler-windows/)

## Setup

1. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

1. Place your PDF file in the project directory
2. Modify the `pdf_path` and `output_path` variables in `pdf_extractor.py` to match your file names
3. Run the script:
```bash
python pdf_extractor.py
```

The script will:
- First attempt to extract text directly from the PDF
- If that fails or yields very little text, it will automatically switch to OCR mode
- Process the text according to your data processor function
- Save the results to a CSV file

## Customization

The script includes an example data processor function that you can modify based on your specific PDF structure. The current example:
- Splits the text into lines
- Creates a dictionary for each non-empty line
- Includes the line content and its length

To customize the data extraction:
1. Modify the `example_data_processor` function in `pdf_extractor.py`
2. Add your own processing logic based on your PDF's structure
3. The function should return a list of dictionaries, where each dictionary represents a row in the CSV

## Dependencies

- PyPDF2: For PDF text extraction
- pandas: For CSV handling
- python-dotenv: For environment variable management
- pdf2image: For converting PDF pages to images
- pytesseract: For OCR text extraction
- Pillow: For image processing 