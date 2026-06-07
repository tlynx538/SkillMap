export interface Skill {
  id: string;
  name: string;
  depth_score: number; // 1-5
  recency_score: number; // 1-5
  created_at: string;
  updated_at: string;
}

export interface Edge {
  id: string;
  from_skill_id: string;
  to_skill_id: string;
  project_name: string;
  outcome: string;
  artifact_links?: string;
  created_at: string;
}

export interface Resume {
  id: string;
  name: string | null;
  created_at: string;
}

export interface Artifact {
  id: string;
  skill_id: string;
  title: string;
  url: string;
  description: string;
  metric_impact?: string;
}

export interface GraphAnalysis {
  clusters: string[][];
  isolates: string[];
  bridge_nodes: string[];
  node_count: number;
  edge_count: number;
  skill_coverage_score: number;
  evidence_density_score: number;
  strongly_evidenced_skills: string[];
  weakly_evidenced_skills: string[];
}

export interface GraphData {
  nodes: { id: string; name: string; depth: number; recency: number }[];
  edges: { from: string; to: string; project: string; outcome: string }[];
}
