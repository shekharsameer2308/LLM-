from fastapi import FastAPI, Depends
from sqlalchemy.orm import Session
from sqlalchemy import text
from database.connection import get_db
from backend.api.routes.articles import router as articles_router
from backend.api.routes.analytics import router as analytics_router

app = FastAPI(
    title="Scout API",
    description="AI-powered market intelligence and competitor research platform",
    version="1.0.0"
)

# Register routes
app.include_router(articles_router, prefix="/api")
app.include_router(analytics_router, prefix="/api")

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.get("/health/db")
async def db_health_check(db: Session = Depends(get_db)):
    try:
        # Execute basic query to verify connection
        db.execute(text("SELECT 1"))
        return {"status": "ok", "db": "connected"}
    except Exception as e:
        return {"status": "error", "db": f"Database connection failed: {str(e)}"}
