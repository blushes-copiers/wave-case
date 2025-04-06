from fastapi import FastAPI
import xarray as xr
import pandas as pd
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse
from fastapi.exceptions import HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
from pathlib import Path
import os


allowed_origins = os.getenv("ALLOWED_ORIGINS", "").split(",")
allowed_origins = [origin.strip() for origin in allowed_origins if origin.strip()]

app = FastAPI()
# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ds = xr.open_dataset("waves_2019-01-01-hmax-max.nc")

class WaveHeight(BaseModel):
    hmax: float = Field(
        default=...,
        description="The maximum wave height for the location",
        example=3.1415,
    )
    time: str = Field(
        default=...,
        description="The date and time of the maximum wave height as an ISO formatted string",
        example="2019-01-01T23:00:00",
    )
    latitude: float = Field(
        default=...,
        description="The latitude of the data point",
        example=37.24804,
    )
    longitude: float = Field(
        default=...,
        description="The longitude of the data point",
        example=-115.800155,
    )


@app.get("/waves", response_model=WaveHeight, tags=["api"], responses={404: {"description": "No data available for the given location"}})
def max_hwave(latitude: float, longitude: float):
    """
    Gets the height of the highest wave and the time of day it occurred for the location nearest to the given coordinates
    """
    v = ds.sel(latitude=latitude, longitude=longitude, method="nearest")
    hmax = v["hmax"].item()
    t = pd.Timestamp(v["time"].item()).isoformat()
    # Get the coordinates of the nearest data point
    nearest_lat = float(v.latitude.item())
    nearest_lon = float(v.longitude.item())
    if pd.isna(hmax):
        raise HTTPException(
            status_code=404, detail="No data available for the given location"
        )
    return WaveHeight(
        hmax=hmax,
        time=t,
        latitude=nearest_lat,
        longitude=nearest_lon,
    )

@app.get("/", response_class=HTMLResponse)
async def serve_index(tags=["web"]):
    """
    Serves our html with the map view
    """
    html = Path("static/index.html").read_text(encoding="utf-8")
    return HTMLResponse(content=html)
