"""
FILE: backend/app/main.py

PURPOSE:
FastAPI application entry point.

Wires together:
- CORS
- API routers under /api/v1
- Global exception handling

RUN FROM:
    backend/

COMMAND:
    uvicorn app.main:app --reload

Swagger:
    http://127.0.0.1:8000/docs
"""

import logging

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.routes import (
    energy,
    control,
    ai_prediction,
    forecast,
    health,
    optimization,
    telemetry,
    turbine,
    weather,
)
from app.core.config import settings


logging.basicConfig(level=logging.INFO)

logger = logging.getLogger("vayunexa")


app = FastAPI(
    title="VAYUNEXA API",
    description=(
        "Backend API for the VAYUNEXA adaptive wind "
        "energy optimization system."
    ),
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


API_PREFIX = "/api/v1"

app.include_router(
    health.router,
    prefix=API_PREFIX,
)

app.include_router(
    telemetry.router,
    prefix=API_PREFIX,
)
app.include_router(
    control.router,
    prefix=API_PREFIX,
)
app.include_router(
    ai_prediction.router,
    prefix=API_PREFIX,
)
app.include_router(
    turbine.router,
    prefix=API_PREFIX,
)

app.include_router(
    weather.router,
    prefix=API_PREFIX,
)

app.include_router(
    energy.router,
    prefix=API_PREFIX,
)

app.include_router(
    forecast.router,
    prefix=API_PREFIX,
)

app.include_router(
    optimization.router,
    prefix=API_PREFIX,
)


@app.exception_handler(Exception)
async def unhandled_exception_handler(
    request: Request,
    exc: Exception,
):
    """
    Never expose internal exception details to clients.

    Full details are logged server-side.
    """

    logger.exception(
        "Unhandled exception on %s %s",
        request.method,
        request.url,
    )

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": (
                "Internal server error. "
                "Check server logs for details."
            )
        },
    )


@app.get("/")
def root():
    return {
        "service": "VAYUNEXA API",
        "docs": "/docs",
        "health": f"{API_PREFIX}/health",
        "environment": settings.environment,
    }
