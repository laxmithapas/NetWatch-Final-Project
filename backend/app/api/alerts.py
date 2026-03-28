import os
import tempfile
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from app.api.deps import SessionDep, CurrentUser
from app.models.alert import Alert
from app.core.pdf_generator import generate_pdf_report

router = APIRouter()

@router.get("/")
def get_alerts(session: SessionDep, current_user: CurrentUser, limit: int = 100):
    alerts = session.query(Alert).order_by(Alert.timestamp.desc()).limit(limit).all()
    return alerts

@router.get("/{alert_id}/pdf")
def get_alert_pdf(alert_id: int, session: SessionDep, current_user: CurrentUser):
    alert = session.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")
    
    # Generate temporary PDF
    fd, pdf_path = tempfile.mkstemp(suffix=".pdf")
    os.close(fd)
    
    alert_data = {
        "id": alert.id,
        "timestamp": alert.timestamp.isoformat() if alert.timestamp else "N/A",
        "source_ip": alert.source_ip,
        "destination_ip": alert.destination_ip,
        "attack_type": alert.attack_type,
        "confidence": alert.confidence
    }
    
    generate_pdf_report(alert_data, pdf_path)
    
    return FileResponse(
        pdf_path, 
        media_type="application/pdf", 
        filename=f"NetWatch_Alert_{alert_id}.pdf"
    )
