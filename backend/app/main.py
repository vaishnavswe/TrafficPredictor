from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.core.db import get_db
from app.models.traffic import Segment, Prediction

app = FastAPI(title="Traffic Predictor API")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/segments")
def list_segments(db: Session = Depends(get_db)):
    # fetch all segments for the dropdown
    segments = db.execute(select(Segment).order_by(Segment.id)).scalars().all()
    return [
        {
            "id": s.id,
            "name": s.name,
            "city": s.city,
            "start_lat": s.start_lat,
            "start_lng": s.start_lng,
            "end_lat": s.end_lat,
            "end_lng": s.end_lng,
        }
        for s in segments
    ]

@app.get("/predict")
def get_latest_prediction(segment_id: int, horizon: int, db: Session = Depends(get_db)):
    # grab most recent prediction for this segment + horizon
    # order by timestamp desc so we get the latest
    q = (
        select(Prediction)
        .where(Prediction.segment_id == segment_id, Prediction.horizon_minutes == horizon)
        .order_by(Prediction.timestamp.desc())
        .limit(1)
    )
    pred = db.execute(q).scalars().first()

    # nothing found, return null
    if not pred:
        return {"segment_id": segment_id, "horizon": horizon, "prediction": None}

    return {
        "segment_id": segment_id,
        "horizon": horizon,
        "timestamp": pred.timestamp.isoformat(),
        "predicted_speed": pred.predicted_speed,
        "run_id": pred.run_id,
    }

@app.get("/predictions")
def get_prediction_series(
    segment_id: int,
    horizon: int = 30,
    limit: int = 288,
    db: Session = Depends(get_db),
):
    q = (
        select(Prediction)
        .where(
            Prediction.segment_id == segment_id,
            Prediction.horizon_minutes == horizon,
        )
        .order_by(Prediction.timestamp.desc())
        .limit(limit)
    )

    rows = db.execute(q).scalars().all()

    # reverse for chart
    # chart wants oldest first, query gives newest first
    rows.reverse()

    return [
        {
            "timestamp": p.timestamp.isoformat(),
            "predicted_speed": p.predicted_speed,
            "run_id": p.run_id,
        }
        for p in rows
    ]

@app.get("/predictions/by_run")
def get_prediction_series_by_run(
    segment_id: int,
    run_id: int,
    horizon: int = 30,
    limit: int = 288,
    db: Session = Depends(get_db),
):
    q = (
        select(Prediction)
        .where(
            Prediction.segment_id == segment_id,
            Prediction.run_id == run_id,
            Prediction.horizon_minutes == horizon,
        )
        .order_by(Prediction.timestamp.desc())
        .limit(limit)
    )
    rows = db.execute(q).scalars().all()
    rows.reverse()
    return [{"timestamp": p.timestamp.isoformat(), "predicted_speed": p.predicted_speed} for p in rows]

