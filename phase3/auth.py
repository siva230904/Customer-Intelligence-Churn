import os

from fastapi import HTTPException, Security
from fastapi.security import APIKeyHeader


# ============================================================
# API KEY CONFIGURATION
# ============================================================

API_KEY = os.getenv("API_KEY")


# ============================================================
# SWAGGER SECURITY SCHEME
# ============================================================

api_key_header = APIKeyHeader(
    name="X-API-Key",
    auto_error=False
)


# ============================================================
# VERIFY API KEY
# ============================================================

def verify_api_key(
    api_key: str | None = Security(api_key_header)
):

    # --------------------------------------------------------
    # Server API key not configured
    # --------------------------------------------------------

    if not API_KEY:

        raise HTTPException(
            status_code=500,
            detail="API_KEY is not configured on the server"
        )


    # --------------------------------------------------------
    # Missing / incorrect API key
    # --------------------------------------------------------

    if api_key != API_KEY:

        raise HTTPException(
            status_code=401,
            detail="Invalid or missing API key"
        )


    return True