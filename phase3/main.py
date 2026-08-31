import sys
import os
from fastapi import FastAPI, Request
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

PHASE6_PATH = os.path.join(BASE_DIR, "phase6")

if PHASE6_PATH not in sys.path:
    sys.path.insert(0, PHASE6_PATH)
from routes.prediction import router as prediction_router




from fastapi.exceptions import RequestValidationError

from fastapi.responses import JSONResponse

from logging_config import logger

from fastapi.middleware.cors import CORSMiddleware

from routes.customer import router as customer_router
from routes.churn import router as churn_router
from routes.high_risk import router as high_risk_router
from routes.features import router as features_router
from routes.prediction import router as prediction_router
from routes.prediction import router as prediction_router

# ============================================================
# APPLICATION
# ============================================================

app = FastAPI(
    title="Customer API",
    description="Customer analytics and ML API",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

# ============================================================
# REQUEST LOGGING
# ============================================================

@app.middleware("http")
async def log_requests(
    request: Request,
    call_next
):

    logger.info(
        "REQUEST %s %s",
        request.method,
        request.url.path
    )

    try:

        response = await call_next(request)

        logger.info(
            "RESPONSE %s %s status=%s",
            request.method,
            request.url.path,
            response.status_code
        )

        return response

    except Exception:

        logger.exception(
            "ERROR %s %s status=500",
            request.method,
            request.url.path
        )

        raise


# ============================================================
# 404 HANDLER
# ============================================================

@app.exception_handler(404)
async def not_found_handler(
    request: Request,
    exc
):

    logger.warning(
        "404 %s %s",
        request.method,
        request.url.path
    )

    return JSONResponse(
        status_code=404,
        content={
            "detail": "Resource not found",
            "status_code": 404
        }
    )


# ============================================================
# 422 VALIDATION HANDLER
# ============================================================

@app.exception_handler(RequestValidationError)
async def validation_error_handler(
    request: Request,
    exc: RequestValidationError
):

    logger.warning(
        "422 %s %s",
        request.method,
        request.url.path
    )

    return JSONResponse(
        status_code=422,
        content={
            "detail": "Request validation failed",
            "status_code": 422
        }
    )


# ============================================================
# GENERAL 500 HANDLER
# ============================================================

@app.exception_handler(Exception)
async def general_exception_handler(
    request: Request,
    exc: Exception
):

    logger.exception(
        "500 %s %s",
        request.method,
        request.url.path
    )

    return JSONResponse(
        status_code=500,
        content={
            "detail": "Internal server error",
            "status_code": 500
        }
    )


# ============================================================
# ROUTERS
# ============================================================

app.include_router(customer_router)

app.include_router(churn_router)

app.include_router(high_risk_router)

app.include_router(features_router)

app.include_router(prediction_router)

app.include_router(prediction_router)