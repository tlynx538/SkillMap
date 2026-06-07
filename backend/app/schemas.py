from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional, List


class ResumeBase(BaseModel):
    name: Optional[str] = None

class ResumeCreate(ResumeBase):
    pass

class ResumeResponse(ResumeBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Skill
class SkillBase(BaseModel):
    name: str
    depth_score: int = 3
    recency_score: int = 3

class SkillCreate(SkillBase):
    pass

class SkillUpdate(BaseModel):
    depth_score: int
    recency_score: int

class SkillResponse(SkillBase):
    id: UUID
    resume_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Edge
class EdgeBase(BaseModel):
    resume_id: UUID
    from_skill_id: UUID
    to_skill_id: UUID
    project_name: str
    outcome: str
    artifact_links: Optional[str] = None

class EdgeCreate(EdgeBase):
    pass

class EdgeResponse(EdgeBase):
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True

# Artifact
class ArtifactBase(BaseModel):
    skill_id: UUID
    title: str
    url: str
    description: str
    metric_impact: Optional[str] = None

class ArtifactCreate(ArtifactBase):
    pass

class ArtifactResponse(ArtifactBase):
    id: UUID
    resume_id: UUID
    class Config:
        from_attributes = True

# AI Import
class ImportTextRequest(BaseModel):
    name: Optional[str] = None
    text: str

class ImportResult(BaseModel):
    resume_id: UUID
    skills: List[SkillResponse]
    edges: List[EdgeResponse]

# Graph
class GraphDataResponse(BaseModel):
    nodes: List[dict]   # {id, name, depth, recency}
    edges: List[dict]   # {from, to, project, outcome}

class GraphAnalysisResponse(BaseModel):
    clusters: List[List[str]]
    isolates: List[str]
    bridge_nodes: List[str]
    node_count: int
    edge_count: int
    skill_coverage_score: int        # total number of skills
    evidence_density_score: float    # percentage (0-100) of skills with >=1 edge
    strongly_evidenced_skills: List[str]   # skill names with at least one edge
    weakly_evidenced_skills: List[str]     # skill names with zero edges

class ExportRequest(BaseModel):
    graph_image: Optional[str] = None 
