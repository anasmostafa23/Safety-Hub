# safetyhub_bot/utils/pdf_generator.py

from reportlab.lib.pagesizes import A3
from reportlab.lib import colors
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from datetime import datetime
import os

def generate_pdf(username: str, template: dict, responses: list,site_id: str = "Unknown", output_dir: str = "exports") -> str:
    os.makedirs(output_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"audit_{username.replace(' ', '_')}_{timestamp}.pdf"
    file_path = os.path.join(output_dir, filename)

    c = canvas.Canvas(file_path, pagesize=A3)
    width, height = A3
    c.setFont("Helvetica-Bold", 14)
    y = height - 2 * cm

    c.drawString(2 * cm, y, f"📋 Site Risk Assessment Report")
    y -= 1 * cm
    c.setFont("Helvetica", 12)
    c.drawString(2 * cm, y, f"Assessor: Eng.{username}")
    y -= 1.2 * cm
    c.drawString(2 * cm, y, f"Site ID: {site_id}")
    y -= 1.2 * cm

    flat_questions = [
        (cat["name"], q["question_en"]) for cat in template["categories"] for q in cat["questions"]
    ]

    for i, (category, question) in enumerate(flat_questions):
        answer = responses[i] if i < len(responses) else "N/A"

        if y <= 2 * cm:
            c.showPage()
            c.setFont("Helvetica", 12)
            y = height - 2 * cm

        # Draw question in bold
        c.setFont("Helvetica-Bold", 11)
        c.drawString(2 * cm, y, f"{i + 1}. [{category}] {question}")
        y -= 0.6 * cm

        # Draw answer in color
        c.setFont("Helvetica", 11)
        if answer == "Yes":
            c.setFillColor(colors.green)
        elif answer == "No":
            c.setFillColor(colors.red)
        else:
            c.setFillColor(colors.grey)

        c.drawString(3 * cm, y, f"Response: {answer}")
        c.setFillColor(colors.black)  # Reset color
        y -= 1 * cm

    c.save()
    return file_path
