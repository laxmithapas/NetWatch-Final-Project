import smtplib
from email.message import EmailMessage
import os

def send_alert_email(to_email: str, alert_data: dict, pdf_path: str = None):
    # Mock behavior for Local testing
    print(f"--- Simulating sending Email Alert to {to_email} ---")
    print(f"Alert data: {alert_data}")
    print("--- End simulated Email Alert ---")
    
    # Example SMTP setup (Requires real credentials to actually send):
    # msg = EmailMessage()
    # msg['Subject'] = f"CRITICAL: Intrusion Detected ({alert_data.get('attack_type', 'Unknown')})"
    # msg['From'] = 'netwatch@example.com'
    # msg['To'] = to_email
    # msg.set_content(f"An intrusion has been detected.\n\nDetails:\nSource IP: {alert_data.get('source_ip')}\nProtocol: {alert_data.get('protocol')}\nAction: Blocked")
    
    # if pdf_path and os.path.exists(pdf_path):
    #     with open(pdf_path, 'rb') as f:
    #         pdf_data = f.read()
    #     msg.add_attachment(pdf_data, maintype='application', subtype='pdf', filename=os.path.basename(pdf_path))
    
    # try:
    #     with smtplib.SMTP("smtp.example.com", 587) as server:
    #         server.starttls()
    #         server.login("user", "pass")
    #         server.send_message(msg)
    # except Exception as e:
    #     print("Failed to send email:", e)
    
    return True
