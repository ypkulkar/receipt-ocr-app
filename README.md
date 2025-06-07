# Receipt OCR App

This project is a FastAPI-based backend application that allows users to upload scanned PDF receipts, extract relevant information using OCR (Optical Character Recognition), store them in a SQLite database, and retrieve or update receipts as needed.

---

## 📦 Features

- Upload scanned receipt PDFs
- Validate if a file can be processed
- Perform OCR and extract:

  - Merchant name
  - Total amount
  - Purchase date

- Handle duplicate receipts
- Store receipts in a SQLite database
- Retrieve all receipts or a specific receipt by ID

---

## 🚀 Technologies Used

- **Python 3.10+**
- **FastAPI** for API design
- **Tesseract OCR** via `pytesseract`
- **pdf2image** to convert PDFs to images
- **SQLite** via SQLAlchemy ORM

---

## ⚙️ Setup Instructions

### 1. Clone the repository

```bash
git clone https://github.com/ypkulkar/receipt-ocr-app.git
cd receipt-ocr-app
```

### 2. Create and activate a virtual environment

```bash
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Poppler and Tesseract

- **macOS** (with Homebrew):

```bash
brew install poppler tesseract
```

- **Ubuntu**:

```bash
sudo apt install poppler-utils tesseract-ocr
```

- **Windows**:

  - Install [Poppler](http://blog.alivate.com.au/poppler-windows/) and add the bin folder to PATH.
  - Install [Tesseract OCR](https://github.com/tesseract-ocr/tesseract) and add to PATH.

### 5. Run the application

```bash
uvicorn app:app --reload
```

---

## 📄 API Endpoints

### `POST /upload`

Upload a new PDF file.
**Form field**: `file` (PDF)

**Response**:

```json
{
  "message": "File uploaded successfully",
  "file_id": 1
}
```

---

### `POST /validate`

Validate uploaded file to ensure it can be processed.
**Form field**: `file_id`

**Response**:

```json
{
  "message": "File is valid and ready for processing."
}
```

---

### `POST /process`

Run OCR and extract receipt info. Saves to DB.
**Form field**: `file_id`

**Response**:

```json
{
  "message": "Receipt processed successfully!",
  "merchant": "APPLEBEE'S",
  "total": "125.23",
  "date": "2018-01-12"
}
```

---

### `GET /receipts`

Retrieve all processed receipts.

**Response**:

```json
[
  {
    "id": 1,
    "merchant_name": "THE VENETIAN",
    "total_amount": "1,937.66",
    "purchased_at": "2018-11-25",
    "file_path": "static/uploads/v.pdf",
    "created_at": "2025-06-07T02:09:04",
    "updated_at": "2025-06-07T02:09:04"
  },
  ...
]
```

---

### `GET /receipts/{id}`

Retrieve a specific receipt by ID.

**Response**:

```json
{
  "id": 2,
  "merchant_name": "APPLEBEE'S",
  "total_amount": "125.23",
  "purchased_at": "2018-01-12",
  "file_path": "static/uploads/a.pdf",
  "created_at": "2025-06-07T02:33:50",
  "updated_at": "2025-06-07T02:34:30"
}
```

---

## 🔄 Duplicate Handling

If a receipt with the same merchant name, total amount, and purchase date already exists:

- It will be updated with the new file path.
- The original `created_at` is preserved.
- The `updated_at` field is refreshed.

---

## 📂 Sample Submission Structure

```
receipt-ocr-app/
├── app.py
├── db.py
├── models.py
├── requirements.txt
├── receipts.db
├── static/
│   └── uploads/
├── README.md
```

---

## ✅ Submission Checklist

- [x] OCR and info extraction work accurately
- [x] No duplicate entries in `receipts` table
- [x] Code is clean and modular
- [x] All APIs tested with sample files
- [x] README written with setup and usage
- [x] GitHub repo pushed with clean commit history

---

## 🙌 Author

Yashodhan Kulkarni (ypkulkar)

---

## 📝 License

This project is licensed under the MIT License.
