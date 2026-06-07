import axios from 'axios';
import type { Skill, Edge, Artifact, GraphAnalysis, GraphData, Resume } from './types';

const API_BASE = 'http://localhost:8000/api';

const apiClient = axios.create({ baseURL: API_BASE });

// Helper to extract session? Not needed – we use resumeId.

export const api = {
  // Resumes
  async getResumes(): Promise<Resume[]> {
    const res = await apiClient.get('/resumes');
    return res.data;
  },

  // Import AI – creates a new resume
  async importFromText(text: string, name?: string): Promise<{ resume_id: string; skills: Skill[]; edges: Edge[] }> {
    const res = await apiClient.post('/import/ai', { text, name });
    return res.data;
  },

  // Skills (scoped by resumeId)
  async getSkills(resumeId: string): Promise<Skill[]> {
    const res = await apiClient.get('/skills', { params: { resume_id: resumeId } });
    return res.data;
  },
  async updateSkill(id: string, depth_score: number, recency_score: number, resumeId: string): Promise<Skill> {
    const res = await apiClient.put(`/skills/${id}`, { depth_score, recency_score }, { params: { resume_id: resumeId } });
    return res.data;
  },

  // Edges (scoped by resumeId)
  async getEdges(resumeId: string): Promise<Edge[]> {
    const res = await apiClient.get('/edges', { params: { resume_id: resumeId } });
    return res.data;
  },
  async createEdge(edge: { from_skill_id: string; to_skill_id: string; project_name: string; outcome: string; artifact_links?: string }, resumeId: string): Promise<Edge> {
    const res = await apiClient.post('/edges', edge, { params: { resume_id: resumeId } });
    return res.data;
  },
  async deleteEdge(id: string, resumeId: string): Promise<void> {
    await apiClient.delete(`/edges/${id}`, { params: { resume_id: resumeId } });
  },

  // Artifacts (scoped by resumeId)
  async createArtifact(artifact: Omit<Artifact, 'id'>, resumeId: string): Promise<Artifact> {
    const res = await apiClient.post('/artifacts', artifact, { params: { resume_id: resumeId } });
    return res.data;
  },
  async getArtifacts(skillId: string, resumeId: string): Promise<Artifact[]> {
    const res = await apiClient.get('/artifacts', { params: { skill_id: skillId, resume_id: resumeId } });
    return res.data;
  },

  // Graph (scoped by resumeId)
  async getGraphData(resumeId: string): Promise<GraphData> {
    const res = await apiClient.get('/graph/data', { params: { resume_id: resumeId } });
    return res.data;
  },
  async getGraphAnalysis(resumeId: string): Promise<GraphAnalysis> {
    const res = await apiClient.get('/graph/analysis', { params: { resume_id: resumeId } });
    return res.data;
  }
};