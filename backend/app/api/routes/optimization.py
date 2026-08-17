"""
FILE: backend/app/api/routes/optimization.py

PURPOSE:
    GET /api/v1/optimization/recommendation
        - ESP8266 and dashboard poll this for the recommended flap angle.

    GET /api/v1/model/metrics
        - AI model performance numbers (MAE/RMSE/R2).
"""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.model_metrics import ModelMetrics
from app.schemas.optimization import OptimizationRecommendation
from app.services import optimization_service


router = APIRouter(
    tags=["optimization"],
)


@router.get(
    "/optimization/recommendation",
    response_model=OptimizationRecommendation,
)
def recommendation(
    device_id: str = Query(...),
    db: Session = Depends(get_db),
):
    return optimization_service.get_recommendation(
        db,
        device_id,
    )


@router.get("/model/metrics")
def model_metrics(
    db: Session = Depends(get_db),
):
    latest = (
        db.query(ModelMetrics)
        .order_by(
            ModelMetrics.training_date.desc()
        )
        .first()
    )

    if latest is None:
        return {
            "status": "no_trained_model_yet",
            "message": (
                "No model_metrics row exists yet. "
                "Train the AI model first."
            ),
        }

    return {
        "status": "ok",
        "model_version": latest.model_version,
        "mae_wh": latest.mae,
        "rmse_wh": latest.rmse,
        "r2": latest.r2,
        "mape_percent": latest.mape,
        "training_date": latest.training_date,
        "dataset_size": latest.dataset_size,
        "notes": latest.notes,
    }
