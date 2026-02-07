from datetime import datetime, timezone
from sqlalchemy.orm import Session

from app.core.db import SessionLocal
from app.models.traffic import Segment, PredictionRun, Prediction

def main():
    db: Session = SessionLocal()

    # wipe everything
    # order matters because of foreign keys
    db.query(Prediction).delete()
    db.query(PredictionRun).delete()
    db.query(Segment).delete()
    db.commit()

    # add a couple test segments
    s1 = Segment(
        name="Mass Ave → Back Bay",
        city="Boston",
        start_lat=42.3467, start_lng=-71.0827,
        end_lat=42.3496, end_lng=-71.0762
    )
    s2 = Segment(
        name="Seaport Blvd",
        city="Boston",
        start_lat=42.3519, start_lng=-71.0432,
        end_lat=42.3489, end_lng=-71.0400
    )
    db.add_all([s1, s2])
    db.commit()
    db.refresh(s1)
    db.refresh(s2)

    # create test prediction run
    run = PredictionRun(model_name="baseline_demo", dataset="demo", horizon_minutes=30)
    db.add(run)
    db.commit()
    db.refresh(run)

    # timestamp for predictions
    # round to the hour so query results are consistent
    ts = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)

    preds = [
        Prediction(segment_id=s1.id, run_id=run.id, timestamp=ts, horizon_minutes=30, predicted_speed=28.4),
        Prediction(segment_id=s2.id, run_id=run.id, timestamp=ts, horizon_minutes=30, predicted_speed=19.7),
    ]
    db.add_all(preds)
    db.commit()

    db.close()
    print("Seeded ✅ segments + predictions inserted")

if __name__ == "__main__":
    main()
