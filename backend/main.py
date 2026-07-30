import os
import uuid
from fastapi import FastAPI, Depends, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from typing import List

from database import init_db, get_db, Complaint
from schemas import ComplaintCreate, ComplaintResponse, CopilotMessageRequest, CopilotFieldsResponse
from langgraph_workflow import run_complaint_workflow
from copilot import process_copilot_message, process_document_text, process_image
from document_extraction import extract_text_from_pdf, extract_text_from_txt

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI(title="Pharma Customer Complaint Management System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")


@app.on_event("startup")
def on_startup():
    init_db()


@app.get("/")
def root():
    return {"status": "ok", "message": "Complaint Management API running"}


@app.post("/copilot/message", response_model=CopilotFieldsResponse)
def copilot_message(payload: CopilotMessageRequest):
    result = process_copilot_message(payload.message, payload.current_form)
    return CopilotFieldsResponse(**result)


@app.post("/copilot/upload", response_model=CopilotFieldsResponse)
async def copilot_upload(file: UploadFile = File(...), current_form: str = "{}"):
    import json as _json
    try:
        form_state = _json.loads(current_form)
    except Exception:
        form_state = {}

    file_bytes = await file.read()
    filename = file.filename or "upload"
    ext = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""

    saved_name = f"{uuid.uuid4().hex}_{filename}"
    saved_path = os.path.join(UPLOAD_DIR, saved_name)
    with open(saved_path, "wb") as f:
        f.write(file_bytes)

    if ext in ("png", "jpg", "jpeg", "webp"):
        mime_type = file.content_type or f"image/{ext}"
        result = process_image(file_bytes, mime_type, form_state)
    elif ext == "pdf":
        text = extract_text_from_pdf(file_bytes)
        result = process_document_text(text, form_state)
    elif ext in ("txt", "eml", "md"):
        text = extract_text_from_txt(file_bytes)
        result = process_document_text(text, form_state)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported file type: .{ext}")

    result["attachment_filename"] = saved_name
    return CopilotFieldsResponse(**result)


@app.post("/complaints", response_model=ComplaintResponse)
def create_complaint(payload: ComplaintCreate, db: Session = Depends(get_db)):
    result = run_complaint_workflow(
        customer_name=payload.customer_name,
        product_name=payload.product_name,
        batch_number=payload.batch_number,
        complaint_text=payload.complaint_text,
    )

    complaint = Complaint(
        customer_name=payload.customer_name,
        product_name=payload.product_name,
        batch_number=payload.batch_number,
        
        country=payload.country,
        quantity_affected=payload.quantity_affected,
        complaint_text=payload.complaint_text,
        attachment_filename=payload.attachment_filename,
        is_complete=result["is_complete"],
        missing_fields=",".join(result["missing_fields"]) if result["missing_fields"] else None,
        risk_level=result["risk_level"],
        risk_reasoning=result["risk_reasoning"],
        status="Pending Info" if not result["is_complete"] else "Open",
    )

    db.add(complaint)
    db.commit()
    db.refresh(complaint)

    return _to_response(complaint)


@app.get("/complaints", response_model=List[ComplaintResponse])
def list_complaints(db: Session = Depends(get_db)):
    complaints = db.query(Complaint).order_by(Complaint.created_at.desc()).all()
    return [_to_response(c) for c in complaints]


@app.get("/complaints/{complaint_id}", response_model=ComplaintResponse)
def get_complaint(complaint_id: int, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(Complaint.id == complaint_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    return _to_response(complaint)


def _to_response(complaint: Complaint) -> ComplaintResponse:
    return ComplaintResponse(
        id=complaint.id,
        customer_name=complaint.customer_name,
        product_name=complaint.product_name,
        batch_number=complaint.batch_number,
        
        country=complaint.country,
        quantity_affected=complaint.quantity_affected,
        complaint_text=complaint.complaint_text,
        attachment_filename=complaint.attachment_filename,
        is_complete=complaint.is_complete,
        missing_fields=complaint.missing_fields.split(",") if complaint.missing_fields else [],
        risk_level=complaint.risk_level,
        risk_reasoning=complaint.risk_reasoning,
        status=complaint.status,
        created_at=complaint.created_at,
    )
