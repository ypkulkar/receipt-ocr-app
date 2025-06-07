from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import os
import shutil
from datetime import datetime

from db import SessionLocal, ReceiptFile

app = FastAPI()

UPLOAD_DIR = "static/uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# POST /upload: Save the PDF and record metadata
@app.post("/upload")
async def upload_receipt(file: UploadFile = File(...)):
    # Step 1: Check file type
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # Step 2: Save file to uploads folder
    file_path = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Step 3: Record file info in the database
    db = SessionLocal()
    try:
        receipt_file = ReceiptFile(
            file_name=file.filename,
            file_path=file_path,
            is_valid=False,  # We'll validate it later
            is_processed=False,
        )
        db.add(receipt_file)
        db.commit()
        db.refresh(receipt_file)

        return JSONResponse({
            "message": "File uploaded successfully",
            "id": receipt_file.id,
            "file_path": file_path
        })

    finally:
        db.close()  # ✅ Ensures cleanup no matter what


from fastapi import Form
from db import SessionLocal, ReceiptFile

@app.post("/validate")
async def validate_receipt(file_id: int = Form(...)):
    db = SessionLocal()
    try:
        receipt_file = db.query(ReceiptFile).filter(ReceiptFile.id == file_id).first()

        if not receipt_file:
            raise HTTPException(status_code=404, detail="File not found in database")

        # Check if file path actually exists
        if not os.path.exists(receipt_file.file_path):
            receipt_file.is_valid = False
            receipt_file.invalid_reason = "File not found on disk"
            db.commit()
            return {"message": "Validation failed", "reason": "File missing"}

        # Check if file really is a PDF
        try:
            with open(receipt_file.file_path, "rb") as f:
                header = f.read(4)
                if header != b"%PDF":
                    receipt_file.is_valid = False
                    receipt_file.invalid_reason = "File is not a valid PDF"
                    db.commit()
                    return {"message": "Invalid PDF"}

            receipt_file.is_valid = True
            receipt_file.invalid_reason = None
            db.commit()
            return {"message": "File is valid PDF ✅"}

        except Exception as e:
            receipt_file.is_valid = False
            receipt_file.invalid_reason = str(e)
            db.commit()
            return {"message": "Validation failed", "error": str(e)}

    finally:
        db.close()  # ✅ Clean and always called


from pdf2image import convert_from_path
import pytesseract
import re
from db import SessionLocal, ReceiptFile, Receipt
from fastapi import Form

@app.post("/process")
async def process_receipt(file_id: int = Form(...)):
    db = SessionLocal()
    receipt_file = db.query(ReceiptFile).filter(ReceiptFile.id == file_id).first()

    if not receipt_file:
        raise HTTPException(status_code=404, detail="File not found")

    if not receipt_file.is_valid:
        raise HTTPException(status_code=400, detail="File is not valid. Run /validate first.")

    try:
        # Convert PDF to image
        images = convert_from_path(receipt_file.file_path)

        # OCR on first page
        text = pytesseract.image_to_string(images[0])
        print("🧾 OCR TEXT START ----------------")
        print(text)
        print("🧾 OCR TEXT END ----------------")

        # Extract merchant name
        merchant_name = text.split('\n')[0].strip()

        # Extract total amount
        amounts = re.findall(r'([\d,]+\.\d{2})', text)
        if amounts:
            numeric_amounts = [float(a.replace(',', '')) for a in amounts]
            max_amount = max(numeric_amounts)
            total_amount = f"{max_amount:,.2f}"
        else:
            total_amount = "Not found"

        # Extract purchase date
        def extract_date(text):
            from datetime import datetime
            possible_dates = re.findall(r'\d{2,4}[-/]\d{2}[-/]\d{2,4}', text)
            for date_str in possible_dates:
                for fmt in ("%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d", "%Y-%m-%d", "%m/%d/%y", "%d-%m-%y"):
                    try:
                        dt = datetime.strptime(date_str, fmt)
                        return dt.strftime("%Y-%m-%d")
                    except ValueError:
                        continue
            return "Unknown"

        purchased_at = extract_date(text)

        # 🔁 Check for duplicate content
        existing_receipt = db.query(Receipt).filter_by(
            purchased_at=purchased_at,
            merchant_name=merchant_name,
            total_amount=total_amount
        ).first()

        if existing_receipt:
            # Update the existing record
            existing_receipt.file_path = receipt_file.file_path  # update to latest file path
            receipt = existing_receipt
        else:
            # Add new record
            receipt = Receipt(
                purchased_at=purchased_at,
                merchant_name=merchant_name,
                total_amount=total_amount,
                file_path=receipt_file.file_path,
            )
            db.add(receipt)

        # Mark file as processed
        receipt_file.is_processed = True
        db.commit()
        db.refresh(receipt)

        return {
            "message": "Receipt processed successfully!",
            "merchant": merchant_name,
            "total": total_amount,
            "date": purchased_at
        }

    except Exception as e:
        return {"error": str(e)}
    
    finally:
        db.close()




from fastapi import Depends
from sqlalchemy.orm import Session
from db import SessionLocal, Receipt

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.get("/receipts")
def list_receipts(db: Session = Depends(get_db)):
    receipts = db.query(Receipt).all()
    return [
        {
            "id": r.id,
            "merchant_name": r.merchant_name,
            "total_amount": r.total_amount,
            "purchased_at": r.purchased_at,
            "file_path": r.file_path,
            "created_at": r.created_at,
            "updated_at": r.updated_at
        }
        for r in receipts
    ]



@app.get("/receipts/{receipt_id}")
def get_receipt(receipt_id: int, db: Session = Depends(get_db)):
    receipt = db.query(Receipt).filter(Receipt.id == receipt_id).first()
    if not receipt:
        raise HTTPException(status_code=404, detail="Receipt not found")

    return {
        "id": receipt.id,
        "merchant_name": receipt.merchant_name,
        "total_amount": receipt.total_amount,
        "purchased_at": receipt.purchased_at,
        "file_path": receipt.file_path,
        "created_at": receipt.created_at,
        "updated_at": receipt.updated_at
    }




