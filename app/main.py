from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api.v1.router import api_router

app = FastAPI(
    title="TaskFlow",
    description="A real-time task processing platform — built phase by phase.",
    version="0.1.0",
    # Disable docs in production — don't expose your API schema publicly.
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
)

# CORS: allow all origins in dev. In production, pin this to your frontend domain.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.DEBUG else [],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount all v1 routes under /api/v1
app.include_router(api_router, prefix="/api/v1")


@app.get("/health")
def health_check():
    """Simple liveness probe — load balancers and k8s use this to check if the app is up."""
    return {"status": "ok", "version": "0.1.0"}
