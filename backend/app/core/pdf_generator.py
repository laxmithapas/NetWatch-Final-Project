from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
import os

def generate_pdf_report(alert_data: dict, filepath: str):
    c = canvas.Canvas(filepath, pagesize=letter)
    width, height = letter

    # Title
    c.setFont("Helvetica-Bold", 18)
    c.setFillColor(colors.darkred)
    c.drawString(100, height - 80, "NetWatch NIDS - Intrusion Alert Report")

    # Details
    c.setFont("Helvetica", 12)
    c.setFillColor(colors.black)
    
    y = height - 120
    c.drawString(100, y, f"Alert ID: {alert_data.get('id', 'N/A')}")
    y -= 20
    c.drawString(100, y, f"Timestamp: {alert_data.get('timestamp', 'N/A')}")
    y -= 20
    c.drawString(100, y, f"Source IP: {alert_data.get('source_ip', 'N/A')}")
    y -= 20
    c.drawString(100, y, f"Destination IP: {alert_data.get('destination_ip', 'N/A')}")
    y -= 20
    c.drawString(100, y, f"Attack Type: {alert_data.get('attack_type', 'N/A')}")
    y -= 20
    c.drawString(100, y, f"Confidence Score: {alert_data.get('confidence', 0.0):.2f}%")
    y -= 40
    
    c.drawString(100, y, "Action Taken: IP Blocked / Alert Generated")
    y -= 40
    
    # Recommendation
    c.setFont("Helvetica-Bold", 12)
    c.drawString(100, y, "Recommendation:")
    c.setFont("Helvetica", 12)
    y -= 20
    c.drawString(100, y, "- Investigate the source IP for further malicious activity.")
    y -= 15
    c.drawString(100, y, "- Consider updating firewall rules if this IP repeats offenses.")

    c.save()
    return filepath
