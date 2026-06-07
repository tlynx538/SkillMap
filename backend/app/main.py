from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.database import engine, Base
from app.routers import import_ai, skills, edges, artifacts, graph, export, resume  

# Create tables on startup (for development only)
async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

app = FastAPI(title="Engineer Skill Map API")

# CORS for frontend (allow all for development)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(import_ai.router)
app.include_router(skills.router)
app.include_router(edges.router)
app.include_router(artifacts.router)
app.include_router(graph.router)
app.include_router(export.router)
app.include_router(resume.router)
@app.on_event("startup")
async def startup():
    await init_db()

@app.get("/")
async def root():
    return {"message": "Skill Map API is running"}
