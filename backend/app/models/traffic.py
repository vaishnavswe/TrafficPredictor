from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.core.db import Base

class Segment(Base):
    # road segment we're tracking
    # has start/end coords for mapping
    __tablename__ = "segments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    city: Mapped[str | None] = mapped_column(String(120), nullable=True)

    start_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    start_lng: Mapped[float | None] = mapped_column(Float, nullable=True)
    end_lat: Mapped[float | None] = mapped_column(Float, nullable=True)
    end_lng: Mapped[float | None] = mapped_column(Float, nullable=True)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    predictions: Mapped[list["Prediction"]] = relationship(back_populates="segment")

class PredictionRun(Base):
    # tracks each time we run the model
    # so we can compare different models or versions
    __tablename__ = "prediction_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    model_name: Mapped[str] = mapped_column(String(120), nullable=False)
    dataset: Mapped[str] = mapped_column(String(120), nullable=False)
    horizon_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    predictions: Mapped[list["Prediction"]] = relationship(back_populates="run")

class Prediction(Base):
    # actual prediction values
    # unique constraint prevents duplicate predictions
    __tablename__ = "predictions"
    __table_args__ = (
        UniqueConstraint("segment_id", "timestamp", "horizon_minutes", "run_id", name="uq_pred_key"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    segment_id: Mapped[int] = mapped_column(ForeignKey("segments.id"), nullable=False)
    run_id: Mapped[int] = mapped_column(ForeignKey("prediction_runs.id"), nullable=False)

    # timestamp is the time we're predicting FOR
    # not when the prediction was made
    timestamp: Mapped[DateTime] = mapped_column(DateTime(timezone=True), nullable=False)
    horizon_minutes: Mapped[int] = mapped_column(Integer, nullable=False)
    predicted_speed: Mapped[float] = mapped_column(Float, nullable=False)

    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    segment: Mapped["Segment"] = relationship(back_populates="predictions")
    run: Mapped["PredictionRun"] = relationship(back_populates="predictions")
