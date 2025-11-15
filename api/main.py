"""
Smart Bottle Formula Recommendation API
FastAPI application entry point
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from api.routers import recommendation

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="Smart Bottle Formula Recommender",
    description="AI-powered baby formula recommendation system based on baby profile and feeding data",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(recommendation.router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("Starting Smart Bottle Formula Recommender API...")
    logger.info("Loading model...")

    # Pre-load the recommender to reduce first request latency
    from api.services.recommender import FormulaRecommender
    try:
        rec = FormulaRecommender()
        logger.info(f"Model loaded: {rec.model_version}")
        logger.info(f"Available formulas: {len(rec.formula_df)}")
    except Exception as e:
        logger.error(f"Failed to load model: {e}")
        raise

    logger.info("API ready to serve requests")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down Smart Bottle Formula Recommender API...")


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Smart Bottle Formula Recommender",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs",
        "api": "/api/v1"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Check if model is loaded
        from api.services.recommender import FormulaRecommender
        rec = FormulaRecommender()

        return {
            "status": "healthy",
            "model": rec.model_version,
            "formulas": len(rec.formula_df)
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e)
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
