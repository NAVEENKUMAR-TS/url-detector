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
    local_label, _, local_conf = predict_url_safety(url)

    # 2. Dual Verification via Gemini
    ai_result = get_gemini_analysis(url, local_label, float(local_conf))
    
    # Check if ai_result is a dict (expected) or string (error fallback)
    if isinstance(ai_result, str):
         # If it returned a string error, use local values
         final_status = local_label
         final_conf = float(local_conf)
         reasoning = ai_result
         technique = None
    else:
        # 3. Consensus Logic (Gemini is the Arbiter)
        final_status = ai_result.get("verdict", local_label)
        final_conf = float(ai_result.get("confidence_score", local_conf))
        reasoning = ai_result.get("reasoning", "No info.")
        technique = ai_result.get("adversarial_technique")

    # 4. Strict Formatting for UI
    # "1. result : safe / malicious / adversarial"
    # "2. confidence score"
    # "3. reasoning with only 3 liines."
    
    formatted_analysis = f"1. Result: {final_status}\n"
    formatted_analysis += f"2. Confidence Score: {final_conf:.2f}\n"
    formatted_analysis += f"3. Reasoning: {reasoning}"
    
    if technique and final_status in ["Malicious", "Adversarial"]:
        formatted_analysis += f"\n\nAdversarial Pattern: {technique}"

    # Save to MongoDB
    scan_data = {
        "url": url,
        "status": final_status,
        "confidence": final_conf,
        "analysis": formatted_analysis,
        "timestamp": datetime.utcnow()
    }
    
    try:
        await scan_collection.insert_one(scan_data)
    except Exception as e:
        print(f"Failed to save to DB: {e}")
    
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
