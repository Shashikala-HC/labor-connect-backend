from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel
import math

app = FastAPI(title="LaborConnect Backend")

# Pretty JSON response class
class PrettyJSONResponse(JSONResponse):
    def render(self, content: any) -> bytes:
        import json
        return json.dumps(content, indent=4).encode("utf-8")

# In-memory workers list
workers = []

# Worker data model
class Worker(BaseModel):
    name: str
    skill: str
    experience: int
    rating: float
    completed_jobs: int
    latitude: float
    longitude: float
    available: int  # 1=available, 0=busy

# Utility: Haversine distance
def haversine(lat1, lon1, lat2, lon2):
    R = 6371
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat/2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
    return R * c

# Add worker endpoint
@app.post("/add_worker", response_class=PrettyJSONResponse)
def add_worker(worker: Worker):
    workers.append(worker)
    return {"message": f"Worker {worker.name} added successfully"}

# Search workers endpoint
@app.get("/search_workers", response_class=PrettyJSONResponse)
def search_workers(skill: str, user_lat: float, user_lon: float):
    results = []
    for w in workers:
        if w.skill != skill or w.available != 1:
            continue
        distance = haversine(user_lat, user_lon, w.latitude, w.longitude)
        normalized_rating = w.rating / 5
        normalized_experience = w.experience / 10
        normalized_jobs = w.completed_jobs / 50
        proximity_score = 1 - (distance / 50)
        score = 0.4*normalized_rating + 0.2*normalized_experience + 0.2*normalized_jobs + 0.2*proximity_score
        results.append({
            "name": w.name,
            "skill": w.skill,
            "experience": w.experience,
            "rating": w.rating,
            "completed_jobs": w.completed_jobs,
            "score": round(score, 3)
        })
    results.sort(key=lambda x: x["score"], reverse=True)
    return results

# Root route
@app.get("/", response_class=PrettyJSONResponse)
def root():
    return {"message": "LaborConnect Backend Running"}
