"""
PDF generation engine: reads the ACORD 125 template, applies mapped data,
and writes a filled, editable PDF to a BytesIO buffer.
"""

import io
from pathlib import Path
from typing import Dict, Any
from pypdf import PdfReader, PdfWriter


TEMPLATE_PATH = Path(__file__).parent / "Acord125CommInsApp (1).pdf"


def fill_acord_125(pdf_data: Dict[str, Any]) -> io.BytesIO:
    """
    Fill the ACORD 125 template with the provided field values.

    Args:
        pdf_data: Dict mapping fully-qualified PDF field names to values.
                  Checkbox values should be pypdf NameObject instances.

    Returns:
        io.BytesIO containing the filled PDF (editable, not flattened).
    """
    if not TEMPLATE_PATH.exists():
        raise FileNotFoundError(f"ACORD 125 template not found at {TEMPLATE_PATH}")

    reader = PdfReader(str(TEMPLATE_PATH))
    writer = PdfWriter()
    writer.append(reader)

    # pypdf only updates fields that exist on each page.
    # update_page_form_field_values iterates over all pages and updates
    # any annotations whose /T matches a key in pdf_data.
    for page in writer.pages:
        writer.update_page_form_field_values(page, pdf_data)

    output = io.BytesIO()
    writer.write(output)
    output.seek(0)
    return output
