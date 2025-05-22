from reportlab.lib.pagesizes import landscape, A3
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import os

def generate_pdf(username: str, template: dict, responses: list, site_id: str = "Unknown", output_dir: str = "exports") -> str:
    os.makedirs(output_dir, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"audit_{username.replace(' ', '_')}_{timestamp}.pdf"
    file_path = os.path.join(output_dir, filename)

    doc = SimpleDocTemplate(
        file_path,
        pagesize=landscape(A3),  # 🔄 Landscape A3
        leftMargin=2 * cm, rightMargin=2 * cm,
        topMargin=2 * cm, bottomMargin=2 * cm
    )

    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("<b>📋 Site Risk Assessment Report</b>", styles["Title"]))
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(Paragraph(f"<b>Assessor:</b> Eng. {username}", styles["Normal"]))
    elements.append(Paragraph(f"<b>Site ID:</b> {site_id}", styles["Normal"]))
    elements.append(Spacer(1, 1 * cm))

    data = [["#", "Category", "Question", "Response"]]
    flat_questions = [
        (cat["name"], q["question_en"]) for cat in template["categories"] for q in cat["questions"]
    ]

    for i, (category, question) in enumerate(flat_questions):
        answer = responses[i] if i < len(responses) else "N/A"
        data.append([str(i + 1), category, question, answer])

    table_style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#d9d9d9")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 12),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP')
    ])

    for i in range(1, len(data)):
        answer = data[i][3]
        if answer == "Yes":
            table_style.add('TEXTCOLOR', (3, i), (3, i), colors.green)
        elif answer == "No":
            table_style.add('TEXTCOLOR', (3, i), (3, i), colors.red)
        else:
            table_style.add('TEXTCOLOR', (3, i), (3, i), colors.grey)

    table = Table(data, colWidths=[2 * cm, 6 * cm, 24 * cm, 5 * cm])  # 📏 wider columns
    table.setStyle(table_style)
    elements.append(table)

    doc.build(elements)
    return file_path
