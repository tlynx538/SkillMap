from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete
from uuid import UUID
from app import schemas, models
from app.database import get_db

router = APIRouter(prefix="/api/edges", tags=["edges"])

@router.get("/", response_model=list[schemas.EdgeResponse])
async def list_edges(
    resume_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.Edge).where(models.Edge.resume_id == resume_id)
    )
    return result.scalars().all()

@router.post("/", response_model=schemas.EdgeResponse)
async def create_edge(
    edge: schemas.EdgeCreate,
    resume_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db)
):
    # Verify both skills exist and belong to this resume
    from_skill = await db.execute(
        select(models.Skill).where(
            models.Skill.id == edge.from_skill_id,
            models.Skill.resume_id == resume_id
        )
    )
    to_skill = await db.execute(
        select(models.Skill).where(
            models.Skill.id == edge.to_skill_id,
            models.Skill.resume_id == resume_id
        )
    )
    if not from_skill.scalar_one_or_none() or not to_skill.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="One or both skills not found in this resume")
    
    new_edge = models.Edge(
        resume_id=resume_id,
        from_skill_id=edge.from_skill_id,
        to_skill_id=edge.to_skill_id,
        project_name=edge.project_name,
        outcome=edge.outcome,
        artifact_links=edge.artifact_links
    )
    db.add(new_edge)
    await db.commit()
    await db.refresh(new_edge)
    return new_edge

@router.delete("/{edge_id}")
async def delete_edge(
    edge_id: UUID,
    resume_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db)
):
    await db.execute(
        delete(models.Edge).where(
            models.Edge.id == edge_id,
            models.Edge.resume_id == resume_id
        )
    )
    await db.commit()
    return {"ok": True}