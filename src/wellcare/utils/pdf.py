"""
PDF prescription generation for patient records.
"""

import datetime
from pathlib import Path

from fpdf import FPDF
from src.wellcare.config import PRESCRIPTIONS_DIR
from src.wellcare.logger import logger


def generate_prescription(
    first_name: str,
    last_name: str,
    age: str,
    mobile: str,
    output_dir: str | None = None,
) -> str | None:
    """Generate a PDF prescription for a patient.

    Args:
        first_name: Patient's first name.
        last_name: Patient's last name.
        age: Patient's age.
        mobile: Patient's mobile number.
        output_dir: Override output directory (defaults to config).

    Returns:
        Path to the generated PDF file, or None if failed.
    """
    pdf = FPDF()
    pdf.add_page()

    # Header
    pdf.set_font("Arial", "B", 24)
    pdf.set_text_color(30, 133, 218)
    pdf.cell(200, 15, text="WellCare Hospital", new_x="LOWER", new_y="NEXT", align="C")

    pdf.set_font("Arial", "I", 12)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(200, 10, text="Your health, our priority.", new_x="LOWER", new_y="NEXT", align="C")
    pdf.ln(10)

    # Patient Details
    pdf.set_font("Arial", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.cell(
        200, 10, text="Patient Record Form", new_x="LOWER", new_y="NEXT", align="L", border="B"
    )
    pdf.ln(5)

    pdf.set_font("Arial", "", 12)
    pdf.cell(100, 10, text=f"Name: {first_name} {last_name}", new_x="RIGHT", new_y="TOP")
    pdf.cell(
        100,
        10,
        text=f"Date: {datetime.datetime.now().strftime('%Y-%m-%d')}",
        new_x="LOWER",
        new_y="NEXT",
    )
    pdf.cell(100, 10, text=f"Age: {age}", new_x="RIGHT", new_y="TOP")
    pdf.cell(100, 10, text=f"Mobile: {mobile}", new_x="LOWER", new_y="NEXT")
    pdf.ln(10)

    # Prescription Notes
    pdf.set_font("Arial", "B", 14)
    pdf.cell(200, 10, text="Prescription / Doctor Notes:", new_x="LOWER", new_y="NEXT", align="L")
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 80, text="", border=1)
    pdf.ln(10)

    pdf.set_font("Arial", "I", 10)
    pdf.cell(
        200,
        10,
        text="Doctor Signature: _______________________",
        new_x="LOWER",
        new_y="NEXT",
        align="R",
    )

    # Save
    output_path = Path(output_dir) if output_dir else PRESCRIPTIONS_DIR
    output_path.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.datetime.now().strftime("%H%M%S")
    filename = output_path / f"{first_name}_{last_name}_{timestamp}.pdf"

    try:
        pdf.output(str(filename))
        logger.info("PDF generated: %s", filename)
        return str(filename)
    except Exception as e:
        logger.error("PDF generation failed: %s", e)
        return None
