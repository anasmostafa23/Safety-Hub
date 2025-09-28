from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os
import asyncio
import concurrent.futures
import logging

logger = logging.getLogger(__name__)

# Register a Unicode font that supports Cyrillic (DejaVuSans is commonly used)
FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"

if not os.path.exists(FONT_PATH):
    # Try alternative font locations
    alternative_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "fonts/DejaVuSans.ttf",
        "DejaVuSans.ttf"
    ]

    for path in alternative_paths:
        if os.path.exists(path):
            FONT_PATH = path
            break
    else:
        logger.warning("DejaVuSans.ttf not found. PDF generation may have font issues.")

pdfmetrics.registerFont(TTFont("DejaVuSans", FONT_PATH))

def generate_pdf(username: str, template: dict, responses: list, site_id: str = "Unknown", timestamp: str = None, output_dir: str = "exports") -> str:
    os.makedirs(output_dir, exist_ok=True)
    if not timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"audit_{username.replace(' ', '_')}_{site_id}_{timestamp}.pdf"
    file_path = os.path.join(output_dir, filename)

    doc = SimpleDocTemplate(file_path, pagesize=landscape(A3),
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)

    # Styles
    base_styles = getSampleStyleSheet()
    base_styles.add(ParagraphStyle(name='Cyrillic',
                                    fontName='DejaVuSans',
                                    fontSize=12,
                                    leading=15))
    title_style = ParagraphStyle(name='CyrillicTitle',
                                 parent=base_styles['Title'],
                                 fontName='DejaVuSans',
                                 fontSize=20,
                                 spaceAfter=12)

    elements = []

    # Header
    elements.append(Paragraph("Site Risk Assessment Report", title_style))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(f"<b>Assessor:</b> Eng. {username}", base_styles['Cyrillic']))
    elements.append(Paragraph(f"<b>Site ID:</b> {site_id}", base_styles['Cyrillic']))
    elements.append(Paragraph(f"<b>Date:</b> {timestamp}", base_styles['Cyrillic']))
    elements.append(Spacer(1, 0.7*cm))

    # Table headers with row number
    data = [["#", "Category", "Question", "Response"]]
    table_style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, -1), "DejaVuSans"),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]

    row_idx = 1
    question_counter = 1

    for category in template["categories"]:
        questions = category["questions"]
        rowspan = len(questions)

        for i, q in enumerate(questions):
            response_index = question_counter - 1
            answer = responses[response_index] if response_index < len(responses) else "N/A"

            text_color = (
                colors.green if answer == "Yes"
                else colors.red if answer == "No"
                else colors.grey
            )

            if i == 0:
                data.append([str(question_counter), category["name"], q["question_en"], answer])
                table_style.append(("SPAN", (1, row_idx), (1, row_idx + rowspan - 1)))
                table_style.append(("VALIGN", (1, row_idx), (1, row_idx + rowspan - 1), "MIDDLE"))
            else:
                data.append([str(question_counter), "", q["question_en"], answer])

            table_style.append(("TEXTCOLOR", (3, row_idx), (3, row_idx), text_color))

            row_idx += 1
            question_counter += 1

    table = Table(data, colWidths=[1.2*cm, 4*cm, 25*cm, 4*cm])
    table.setStyle(TableStyle(table_style))
    elements.append(table)

    doc.build(elements)
    return file_path

async def generate_pdf_async(username: str, template: dict, responses: list, site_id: str = "Unknown", timestamp: str = None, output_dir: str = "exports") -> str:
    """
    Async wrapper for PDF generation to prevent blocking the main thread
    """
    loop = asyncio.get_event_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        # Run the PDF generation in a separate thread
        pdf_path = await loop.run_in_executor(
            executor,
            generate_pdf,
            username,
            template,
            responses,
            site_id,
            timestamp,
            output_dir
        )
        return pdf_path

def generate_pdf_sync(*args, **kwargs) -> str:
    """
    Synchronous PDF generation for backward compatibility
    """
    return generate_pdf(*args, **kwargs)
