import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import pandas as pd
import numpy as np
import json

class Request(BaseModel):
    regions: List[str]
    threshold_ms: int


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)


with open("q-vercel-latency.json") as f:
    data = json.load(f)
def calculate_values(threshold, region):

    df = pd.DataFrame(data)
    df = df[df["region"] == region]

    avg_latency = float(df["latency_ms"].mean())
    p95_latency = float(np.percentile(df["latency_ms"], 95))
    avg_uptime = float(df["uptime_pct"].mean())
    breaches = float((df["latency_ms"] > threshold).sum())
    
    result = {
        "avg_latency": round(avg_latency, 2),
        "p95_latency": round(p95_latency, 2),
        "avg_uptime": round(avg_uptime, 2),
        "breaches": breaches
    }
    return result

@app.post('/api/latency')
def main(request: Request):
    ret = {}
    for region in request.regions:
       ret[region] = calculate_values(request.threshold_ms, region)
    return ret

@app.post('/')
async def health():
    return "Bro im fine"


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
