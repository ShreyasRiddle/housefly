from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .api import neighborhoods, scores, admin

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Housefly API", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(neighborhoods.router, prefix="/api", tags=["neighborhoods"])
app.include_router(scores.router, prefix="/api", tags=["scores"])
app.include_router(admin.router, prefix="/api", tags=["admin"])


@app.get("/")
async def root():
    return {"message": "Housefly API", "version": "1.0.0"}


@app.get("/health")
async def health():
    return {"status": "healthy"}

