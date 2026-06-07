from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app import schemas, models
from app.database import get_db

router = APIRouter(prefix="/api/artifacts", tags=["artifacts"])

@router.post("/", response_model=schemas.ArtifactResponse)
async def create_artifact(
    artifact: schemas.ArtifactCreate,
    resume_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db)
):
    # Verify skill belongs to this resume
    skill = await db.execute(
        select(models.Skill).where(
            models.Skill.id == artifact.skill_id,
            models.Skill.resume_id == resume_id
        )
    )
    if not skill.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Skill not found in this resume")
    
    new_artifact = models.Artifact(
        resume_id=resume_id,
        skill_id=artifact.skill_id,
        title=artifact.title,
        url=artifact.url,
        description=artifact.description,
        metric_impact=artifact.metric_impact
    )
    db.add(new_artifact)
    await db.commit()
    await db.refresh(new_artifact)
    return new_artifact

@router.get("/", response_model=list[schemas.ArtifactResponse])
async def list_artifacts(
    skill_id: UUID = Query(...),
    resume_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.Artifact).where(
            models.Artifact.skill_id == skill_id,
            models.Artifact.resume_id == resume_id
        )
    )
    return result.scalars().all()