from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select,delete
from app import schemas, models, ai_parser
from app.database import get_db
from uuid import uuid4

router = APIRouter(prefix="/api/import", tags=["import"])

@router.post("/ai", response_model=schemas.ImportResult)
async def import_from_text(req: schemas.ImportTextRequest, db: AsyncSession = Depends(get_db)):
    # 1. Create a new resume record
    new_resume = models.Resume(name=req.name)   # optional name field in request
    db.add(new_resume)
    await db.flush()   # assign id
    
    # 2. Parse AI
    parsed = ai_parser.parse_resume_to_skill_graph(req.text)
    if not parsed.get("skills") and not parsed.get("edges"):
        raise HTTPException(status_code=400, detail="No skills or edges extracted.")
    
    # 3. Insert skills (with resume_id)
    skills_map = {}
    new_skills = []
    for skill_data in parsed.get("skills", []):
        skill = models.Skill(
            resume_id=new_resume.id,
            name=skill_data["name"].strip(),
            depth_score=skill_data.get("depth_score", 3),
            recency_score=skill_data.get("recency_score", 3),
        )
        db.add(skill)
        skills_map[skill.name] = skill
        new_skills.append(skill)
    await db.flush()
    
    # 4. Insert edges
    new_edges = []
    for edge_data in parsed.get("edges", []):
        from_name = edge_data["from"].strip()
        to_name = edge_data["to"].strip()
        if from_name not in skills_map or to_name not in skills_map:
            continue
        edge = models.Edge(
            resume_id=new_resume.id,
            from_skill_id=skills_map[from_name].id,
            to_skill_id=skills_map[to_name].id,
            project_name=edge_data["project_name"],
            outcome=edge_data["outcome"],
            artifact_links=edge_data.get("link", "")
        )
        db.add(edge)
        new_edges.append(edge)
    
    await db.commit()
    for skill in new_skills: await db.refresh(skill)
    for edge in new_edges: await db.refresh(edge)
    
    return schemas.ImportResult(resume_id=new_resume.id, skills=new_skills, edges=new_edges)