from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app import schemas, models, graph_analyzer
from app.database import get_db

router = APIRouter(prefix="/api/graph", tags=["graph"])

@router.get("/data", response_model=schemas.GraphDataResponse)
async def get_graph_data(
    resume_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db)
):
    skills_result = await db.execute(
        select(models.Skill).where(models.Skill.resume_id == resume_id)
    )
    skills = skills_result.scalars().all()
    edges_result = await db.execute(
        select(models.Edge).where(models.Edge.resume_id == resume_id)
    )
    edges = edges_result.scalars().all()
    
    nodes = [
        {"id": str(s.id), "name": s.name, "depth": s.depth_score, "recency": s.recency_score}
        for s in skills
    ]
    edges_data = [
        {"from": str(e.from_skill_id), "to": str(e.to_skill_id), "project": e.project_name, "outcome": e.outcome}
        for e in edges
    ]
    return schemas.GraphDataResponse(nodes=nodes, edges=edges_data)

@router.get("/analysis", response_model=schemas.GraphAnalysisResponse)
async def get_graph_analysis(
    resume_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db)
):
    skills_result = await db.execute(
        select(models.Skill).where(models.Skill.resume_id == resume_id)
    )
    skills = skills_result.scalars().all()
    edges_result = await db.execute(
        select(models.Edge).where(models.Edge.resume_id == resume_id)
    )
    edges = edges_result.scalars().all()
    
    analysis = await graph_analyzer.analyze_graph_from_lists(skills, edges)
    return schemas.GraphAnalysisResponse(**analysis)