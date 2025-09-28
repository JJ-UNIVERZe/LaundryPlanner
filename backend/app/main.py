from fastapi import FastAPI
from .api import router
from .config import settings
from .city_search import router as city_router

app = FastAPI(title="Laundry Planner Pro API")
from fastapi.middleware.cors import CORSMiddleware

# Create app
app = FastAPI(title="Laundry Planner Pro API")

# ADD THIS SECTION 👇
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allow all origins (or ["http://localhost:3000"] for more strict)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")
app.include_router(city_router, prefix="/api")

@app.get("/")
def root():
    return {"app": "laundry-planner-pro", "default_city": settings.DEFAULT_CITY}

# Run with: uvicorn app.main:app --reload --port 8000