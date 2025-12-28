from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

from database import scan_collection, check_db_connection
from model_loader import predict_url_safety
from gemini_client import get_gemini_analysis

from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

app = FastAPI(title="URL Detector API", version="1.0")

# Mount static files
import os
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# CORS Setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Models
class ScanRequest(BaseModel):
    url: str

class ScanResult(BaseModel):
    url: str
    status: str
    confidence: float
    analysis: str
    timestamp: datetime

class StatsResponse(BaseModel):
    total_scans: int
    safe_count: int
    malicious_count: int

@app.get("/")
def read_root():
    return FileResponse(os.path.join(static_dir, "index.html"))

@app.post("/scan", response_model=ScanResult)
async def scan_url(request: ScanRequest):
    url = request.url
    if not url:
        raise HTTPException(status_code=400, detail="URL is required")

    # 1. Local Model Prediction
    status, _, confidence = predict_url_safety(url)

    # 2. Gemini Analysis (Double Check)
    analysis = get_gemini_analysis(url, status, confidence)

    # 3. Save to MongoDB
    scan_data = {
        "url": url,
        "status": status,
        "confidence": confidence,
        "analysis": analysis,
        "timestamp": datetime.utcnow()
    }
    
    try:
        await scan_collection.insert_one(scan_data)
    except Exception as e:
        print(f"Failed to save to DB: {e}")
        # Continue execution even if DB save fails, just return result
    
    return scan_data

@app.get("/history", response_model=List[ScanResult])
async def get_history(limit: int = 10):
    try:
        cursor = scan_collection.find().sort("timestamp", -1).limit(limit)
        results = await cursor.to_list(length=limit)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    try:
        total = await scan_collection.count_documents({})
        safe = await scan_collection.count_documents({"status": "Safe"})
        malicious = await scan_collection.count_documents({"status": "Malicious"})
        return {"total_scans": total, "safe_count": safe, "malicious_count": malicious}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
