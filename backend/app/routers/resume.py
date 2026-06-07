from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import schemas, models
from app.database import get_db

router = APIRouter(prefix="/api/resumes", tags=["resumes"])

@router.get("/", response_model=list[schemas.ResumeResponse])
async def list_resumes(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(models.Resume).order_by(models.Resume.created_at.desc()))
    return result.scalars().all()