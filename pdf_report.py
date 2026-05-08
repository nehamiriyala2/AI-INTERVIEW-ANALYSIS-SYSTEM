import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

def generate_pdf(report):
    # backend folder path
    base_dir = os.path.dirname(os.path.abspath(__file__))

    # full pdf path
    file_path = os.path.join(base_dir, "Interview_Report.pdf")

    c = canvas.Canvas(file_path, pagesize=A4)

    c.setFont("Helvetica-Bold", 20)
    c.drawString(150, 800, "Interview Performance Report")

    c.setFont("Helvetica", 14)
    c.drawString(100, 740, f"Emotion: {report['emotion']}")
    c.drawString(100, 710, f"Voice: {report['voice']}")
    c.drawString(100, 680, f"Posture: {report['posture']}")
    c.drawString(100, 650, f"Total Score: {report['score']}/100")
    c.drawString(100, 620, f"Status: {report['status']}")

    c.save()
    return file_path
