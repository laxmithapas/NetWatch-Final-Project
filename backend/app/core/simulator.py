import asyncio
import pandas as pd
import joblib
import os
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.alert import Alert
from app.api.ws import manager
from app.core.email_service import send_alert_email
from app.core.pdf_generator import generate_pdf_report
from datetime import datetime

base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
ml_dir = os.path.join(base_dir, "ml_pipeline")
DATASET_PATH = os.path.join(ml_dir, "sample_dataset.csv")

try:
    scaler = joblib.load(os.path.join(ml_dir, "models", "scaler.pkl"))
    model = joblib.load(os.path.join(ml_dir, "models", "xgb_model.pkl"))
    FEATURE_COLS = joblib.load(os.path.join(ml_dir, "models", "feature_names.pkl"))
    print("Models loaded successfully in simulator.")
except Exception as e:
    print("Warning: ML models not found. Simulator might fail.", dict(e=e))
    scaler, model, FEATURE_COLS = None, None, []

async def run_simulation():
    if not os.path.exists(DATASET_PATH):
        print(f"Dataset {DATASET_PATH} not found. Simulation halted.")
        return

    df = pd.read_csv(DATASET_PATH)
    
    # Infinite loop to keep simulating
    while True:
        # Re-shuffle or sequential replay
        for idx, row in df.iterrows():
            if model is None:
                await asyncio.sleep(5)
                continue
                
            features = pd.DataFrame([row[FEATURE_COLS]])
            features_scaled = scaler.transform(features)
            
            # Predict
            prob = model.predict_proba(features_scaled)[0, 1]
            is_anomaly = prob > 0.5
            
            # Form WebSocket message
            message = {
                "id": str(idx),
                "timestamp": datetime.now().isoformat(),
                "source_ip": str(row.get('Source IP', 'Unknown')),
                "destination_ip": str(row.get('Destination IP', 'Unknown')),
                "protocol": str(row.get('Protocol', 'Unknown')),
                "is_anomaly": bool(is_anomaly),
                "confidence": float(prob * 100),
                "label": str(row.get('Label', 'Unknown'))
            }

            if is_anomaly:
                message["attack_type"] = str(row.get('Label', 'Anomaly'))
                db = SessionLocal()
                try:
                    new_alert = Alert(
                        source_ip=message["source_ip"],
                        destination_ip=message["destination_ip"],
                        protocol=message["protocol"],
                        attack_type=message["attack_type"],
                        confidence=message["confidence"],
                        action_taken="Blocked",
                        timestamp=datetime.now()
                    )
                    db.add(new_alert)
                    db.commit()
                    db.refresh(new_alert)
                    
                    # Add database ID to message
                    message["db_id"] = new_alert.id
                finally:
                    db.close()
                pass
                
                # Mock email
                send_alert_email("admin@netwatch.local", message)

            # Broadcast to UI
            await manager.broadcast(message)
            
            # Sleep 1 second to mock real-time
            await asyncio.sleep(1)
