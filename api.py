"""
FastAPI wrapper for ACORD 125 PDF generation.
Run with: python3 api.py
"""

from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Any, Dict
import io

from schemas import Acord125Input
from field_mapper import map_data_to_pdf_fields
from pdf_filler import fill_acord_125

app = FastAPI(title="ACORD 125 API")


class GenerateRequest(BaseModel):
    data: Dict[str, Any]


@app.post("/generate-acord")
async def generate_acord(payload: Dict[str, Any]):
    """Accept JSON payload and return a filled ACORD 125 PDF."""
    try:
        validated = Acord125Input(**payload)
        validated_dict = validated.model_dump(by_alias=True)
    except Exception:
        validated_dict = payload

    pdf_data = map_data_to_pdf_fields(validated_dict)
    pdf_buffer = fill_acord_125(pdf_data)

    return StreamingResponse(
        pdf_buffer,
        media_type="application/pdf",
        headers={"Content-Disposition": 'attachment; filename="ACORD_125_Filled.pdf"'},
    )


@app.get("/health")
async def health():
    return {"status": "ok"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
