from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import os

def generate_pdf(username: str, template: dict, responses: list, site_id: str = "Unknown",timestamp: str = None, output_dir: str = "exports") -> str:
    os.makedirs(output_dir, exist_ok=True)
    if not timestamp:
      timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"audit_{username.replace(' ', '_')}_{timestamp}.pdf"
    file_path = os.path.join(output_dir, filename)

    doc = SimpleDocTemplate(file_path, pagesize=landscape(A3),
                            rightMargin=2*cm, leftMargin=2*cm,
                            topMargin=2*cm, bottomMargin=2*cm)
    styles = getSampleStyleSheet()
    elements = []

    # Header
    elements.append(Paragraph("<b>📋 Site Risk Assessment Report</b>", styles['Title']))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(Paragraph(f"<b>Assessor:</b> Eng. {username}", styles['Normal']))
    elements.append(Paragraph(f"<b>Site ID:</b> {site_id}", styles['Normal']))
    elements.append(Paragraph(f"<b>Date:</b> {timestamp}", styles['Normal']))  
    elements.append(Spacer(1, 0.7*cm))

    # Table headers with row number
    data = [["#", "Category", "Question", "Response"]]
    table_style = [
        ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.black),
        ("ALIGN", (0, 0), (-1, -1), "LEFT"),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 12),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
    ]

    row_idx = 1  # Starts at table data row 1 (excluding header)
    question_counter = 1  # Visible row number

    for category in template["categories"]:
        questions = category["questions"]
        rowspan = len(questions)

        for i, q in enumerate(questions):
            response_index = question_counter - 1
            answer = responses[response_index] if response_index < len(responses) else "N/A"

            # Determine response color
            text_color = (
                colors.green if answer == "Yes"
                else colors.red if answer == "No"
                else colors.grey
            )

            # First question in category: include category name
            if i == 0:
                data.append([str(question_counter), category["name"], q["question_en"], answer])
                table_style.append(("SPAN", (1, row_idx), (1, row_idx + rowspan - 1)))
                table_style.append(("VALIGN", (1, row_idx), (1, row_idx + rowspan - 1), "MIDDLE"))
            else:
                data.append([str(question_counter), "", q["question_en"], answer])

            # Apply color to response
            table_style.append(("TEXTCOLOR", (3, row_idx), (3, row_idx), text_color))

            row_idx += 1
            question_counter += 1

    # Adjust column widths (now 4 columns)
    table = Table(data, colWidths=[1.2*cm, 5.5*cm, 19*cm, 4*cm])
    table.setStyle(TableStyle(table_style))
    elements.append(table)

    doc.build(elements)
    return file_path
