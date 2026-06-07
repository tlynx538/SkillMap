from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app import schemas, models
from app.database import get_db

router = APIRouter(prefix="/api/skills", tags=["skills"])

@router.get("/", response_model=list[schemas.SkillResponse])
async def list_skills(
    resume_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.Skill).where(models.Skill.resume_id == resume_id)
    )
    return result.scalars().all()

@router.put("/{skill_id}", response_model=schemas.SkillResponse)
async def update_skill(
    skill_id: UUID,
    update: schemas.SkillUpdate,
    resume_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(models.Skill).where(
            models.Skill.id == skill_id,
            models.Skill.resume_id == resume_id
        )
    )
    skill = result.scalar_one_or_none()
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found in this resume")
    skill.depth_score = update.depth_score
    skill.recency_score = update.recency_score
    await db.commit()
    await db.refresh(skill)
    return skill