import base64
from groq_client import call_groq_json, call_groq_vision_json

FIELD_SPEC = """{
  "customer_name": "string or null",
  "product_name": "string or null",
  "batch_number": "string or null",
  
  "country": "string or null (country where the complaint originated)",
  "quantity_affected": "string or null (e.g. 12 units, 1 batch, 3 strips)",
  "complaint_text": "a clean, well-written complaint description or null"
}"""

COPILOT_SYSTEM_PROMPT = f"""You are an AI Copilot embedded in a pharmaceutical Customer Complaint
Management System. The user will either paste a raw complaint (email, notes, free text) and want
you to extract structured fields from it, OR give you a short instruction to change one field.

Always respond with ONLY valid JSON in this exact format, nothing else:
{{
  {FIELD_SPEC.strip()[1:-1]},
  "reply": "a short one-sentence friendly confirmation of what you did"
}}

Rules:
- You are given the CURRENT FORM STATE (may have existing values) and a USER MESSAGE.
- If the user message is a fresh complaint, extract all fields you can find and treat it as a new
  complaint (overwrite old values), unless the current form is empty and the message clearly adds on.
- If the user message is a short instruction like "change batch number to X" or "country is India",
  ONLY update that specific field and KEEP all other current form values unchanged (copy as-is).
- Never invent information not present in the message or current form. Use null if unknown.
- complaint_text should be a clean rewritten version of the issue, not a verbatim copy.
"""

DOCUMENT_SYSTEM_PROMPT = f"""You are an AI Copilot for a pharmaceutical Customer Complaint
Management System. You will be given the text content of an uploaded document (an email, a
complaint letter, or scanned notes about a product complaint). Extract the relevant fields.

Always respond with ONLY valid JSON in this exact format, nothing else:
{{
  {FIELD_SPEC.strip()[1:-1]},
  "reply": "a short one-sentence friendly confirmation of what was extracted from the document"
}}

Never invent information not present in the document. Use null for anything not mentioned.
complaint_text should be a clean rewritten summary of the issue described in the document.
"""

IMAGE_SYSTEM_PROMPT = DOCUMENT_SYSTEM_PROMPT.replace(
    "the text content of an uploaded document",
    "an uploaded image (e.g. a photo of a medicine strip/label, a scanned complaint letter, or a "
    "product packaging defect)",
)

FIELDS = ["customer_name", "product_name", "batch_number", "", "country", "quantity_affected", "complaint_text"]


def _clean_result(result: dict, current_form: dict) -> dict:
    out = {}
    for f in FIELDS:
        out[f] = result.get(f) or current_form.get(f) or ""
    out["reply"] = result.get("reply") or "Updated the form based on your input."
    return out


def process_copilot_message(user_message: str, current_form: dict) -> dict:
    user_prompt = f"""
    CURRENT FORM STATE:
    {current_form}

    USER MESSAGE:
    \"\"\"{user_message}\"\"\"

    Return the JSON as instructed.
    """
    result = call_groq_json(COPILOT_SYSTEM_PROMPT, user_prompt)
    return _clean_result(result, current_form)


def process_document_text(document_text: str, current_form: dict) -> dict:
    user_prompt = f"""
    DOCUMENT TEXT:
    \"\"\"{document_text[:6000]}\"\"\"

    Extract the fields as instructed.
    """
    result = call_groq_json(DOCUMENT_SYSTEM_PROMPT, user_prompt)
    return _clean_result(result, current_form)


def process_image(image_bytes: bytes, mime_type: str, current_form: dict) -> dict:
    image_base64 = base64.b64encode(image_bytes).decode("utf-8")
    user_prompt = "Extract the complaint fields from this image as instructed."
    result = call_groq_vision_json(IMAGE_SYSTEM_PROMPT, user_prompt, image_base64, mime_type)
    return _clean_result(result, current_form)
