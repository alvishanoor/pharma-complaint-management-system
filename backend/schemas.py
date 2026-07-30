from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class ComplaintCreate(BaseModel):
    customer_name: str
    product_name: Optional[str] = None
    batch_number: Optional[str] = None
    
    country: Optional[str] = None
    quantity_affected: Optional[str] = None
    complaint_text: str
    attachment_filename: Optional[str] = None


class CopilotMessageRequest(BaseModel):
    message: str
    current_form: dict = {}


class CopilotFieldsResponse(BaseModel):
    customer_name: str
    product_name: str
    batch_number: str
    
    country: str
    quantity_affected: str
    complaint_text: str
    reply: str
    attachment_filename: Optional[str] = None


class ComplaintResponse(BaseModel):
    id: int
    customer_name: str
    product_name: Optional[str]
    batch_number: Optional[str]
    
    country: Optional[str]
    quantity_affected: Optional[str]
    complaint_text: str
    attachment_filename: Optional[str]
    is_complete: bool
    missing_fields: Optional[List[str]] = []
    risk_level: Optional[str]
    risk_reasoning: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
