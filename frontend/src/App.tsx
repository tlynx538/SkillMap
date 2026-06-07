import React, { useEffect, useState, useRef } from 'react';
import { api } from './api';
import type { Skill, Edge, GraphAnalysis, GraphData, Resume } from './types';
import ImportBox from './components/ImportBox';
import SkillTable from './components/SkillTable';
import EdgeForm from './components/EdgeForm';
import GraphCanvas from './components/GraphCanvas';
import type { GraphCanvasHandle } from './components/GraphCanvas';
import AnalysisPanel from './components/AnalysisPanel';

const App: React.FC = () => {
  const [resumes, setResumes] = useState<Resume[]>([]);
  const [currentResumeId, setCurrentResumeId] = useState<string | null>(null);
  const [skills, setSkills] = useState<Skill[]>([]);
  const [edges, setEdges] = useState<Edge[]>([]);
  const [graphData, setGraphData] = useState<GraphData | null>(null);
  const [analysis, setAnalysis] = useState<GraphAnalysis | null>(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState<'import' | 'skills' | 'edges' | 'graph'>('import');

  const graphRef = useRef<GraphCanvasHandle>(null);

  const loadResumes = async () => {
    try {
      const data = await api.getResumes();
      setResumes(data);
      if (data.length > 0 && !currentResumeId) {
        setCurrentResumeId(data[0].id);
      }
    } catch (err) {
      console.error('Failed to load resumes', err);
    }
  };

  const refreshCurrentResume = async () => {
    if (!currentResumeId) return;
    setLoading(true);
    try {
      const [skillsRes, edgesRes, graphRes, analysisRes] = await Promise.all([
        api.getSkills(currentResumeId),
        api.getEdges(currentResumeId),
        api.getGraphData(currentResumeId),
        api.getGraphAnalysis(currentResumeId),
      ]);
      setSkills(skillsRes);
      setEdges(edgesRes);
      setGraphData(graphRes);
      setAnalysis(analysisRes);
    } catch (err) {
      console.error('Failed to refresh resume data', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadResumes();
  }, []);

  useEffect(() => {
    if (currentResumeId) {
      refreshCurrentResume();
    }
  }, [currentResumeId]);

  const handleImport = async (text: string, name?: string) => {
    setLoading(true);
    try {
      const result = await api.importFromText(text, name);
      await loadResumes();
      setCurrentResumeId(result.resume_id);
      setActiveTab('skills');
    } catch (err) {
      console.error('Import failed', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSkillUpdate = async (id: string, depth: number, recency: number) => {
    if (!currentResumeId) return;
    await api.updateSkill(id, depth, recency, currentResumeId);
    await refreshCurrentResume();
  };

  const handleEdgeCreate = async (edge: { from_skill_id: string; to_skill_id: string; project_name: string; outcome: string }) => {
    if (!currentResumeId) return;
    await api.createEdge(edge, currentResumeId);
    await refreshCurrentResume();
    setActiveTab('graph');
  };

  const handleEdgeDelete = async (id: string) => {
    if (!currentResumeId) return;
    await api.deleteEdge(id, currentResumeId);
    await refreshCurrentResume();
  };

  // PDF export with graph screenshot
  const handleExportPDF = async () => {
    if (!currentResumeId) return;
    setLoading(true);
    try {
      let graphImageDataUrl = '';
      if (graphRef.current) {
        graphImageDataUrl = await graphRef.current.capture();
      }
      const response = await fetch(`http://localhost:8000/api/export/pdf?resume_id=${currentResumeId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ graph_image: graphImageDataUrl })
      });
      if (!response.ok) throw new Error('Export failed');
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'skill_map_report.pdf';
      document.body.appendChild(a);
      a.click();
      document.body.removeChild(a);
      window.URL.revokeObjectURL(url);
    } catch (err) {
      console.error('PDF export error:', err);
      alert('Failed to generate PDF. Check backend.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-blue-600 text-white p-4 shadow-md">
        <div className="max-w-7xl mx-auto flex justify-between items-center">
          <div>
            <h1 className="text-2xl font-bold">Engineer Skill Map</h1>
            <p className="text-sm opacity-90">Build your graph • Step 1–5 method</p>
          </div>
          <div className="flex items-center gap-2">
            <label className="text-sm">Resume:</label>
            <select
              className="px-2 py-1 rounded text-black"
              value={currentResumeId || ''}
              onChange={(e) => setCurrentResumeId(e.target.value)}
              disabled={resumes.length === 0}
            >
              {resumes.map((r) => (
                <option key={r.id} value={r.id}>
                  {r.name || new Date(r.created_at).toLocaleString()}
                </option>
              ))}
            </select>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto p-4">
        <div className="flex space-x-2 border-b mb-6">
          {['import', 'skills', 'edges', 'graph'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab as any)}
              className={`px-4 py-2 font-medium rounded-t-lg transition ${
                activeTab === tab
                  ? 'bg-white text-blue-600 border-l border-r border-t'
                  : 'text-gray-600 hover:text-blue-600'
              }`}
            >
              {tab === 'import' && '1. Import Skills'}
              {tab === 'skills' && '2. Rate Skills'}
              {tab === 'edges' && '3. Add Edges + Evidence'}
              {tab === 'graph' && '4. Visualise Graph'}
            </button>
          ))}
        </div>

        {loading && (
          <div className="fixed inset-0 bg-black/20 flex items-center justify-center z-50">
            <div className="bg-white p-4 rounded-lg shadow-lg">Loading...</div>
          </div>
        )}

        <div className="bg-white rounded-lg shadow p-6">
          {activeTab === 'import' && <ImportBox onImport={handleImport} />}
          {activeTab === 'skills' && (
            <SkillTable skills={skills} onUpdate={handleSkillUpdate} />
          )}
          {activeTab === 'edges' && (
            <div className="space-y-6">
              <EdgeForm skills={skills} onCreate={handleEdgeCreate} />
              <div className="mt-8">
                <h3 className="text-lg font-semibold mb-2">Existing Edges</h3>
                {edges.length === 0 && <p className="text-gray-500">No edges yet. Create one above.</p>}
                <ul className="space-y-2">
                  {edges.map((edge) => {
                    const fromSkill = skills.find(s => s.id === edge.from_skill_id);
                    const toSkill = skills.find(s => s.id === edge.to_skill_id);
                    return (
                      <li key={edge.id} className="border p-3 rounded flex justify-between items-center">
                        <div>
                          <span className="font-medium">{fromSkill?.name}</span> → <span className="font-medium">{toSkill?.name}</span>
                          <div className="text-sm text-gray-600">Project: {edge.project_name}</div>
                          <div className="text-sm text-gray-600">Outcome: {edge.outcome}</div>
                        </div>
                        <button
                          onClick={() => handleEdgeDelete(edge.id)}
                          className="text-red-500 hover:text-red-700 text-sm"
                        >
                          Delete
                        </button>
                      </li>
                    );
                  })}
                </ul>
              </div>
            </div>
          )}
          {activeTab === 'graph' && graphData && analysis && currentResumeId && (
            <div className="space-y-6">
              <GraphCanvas ref={graphRef} graphData={graphData} analysis={analysis} />
              <AnalysisPanel 
                analysis={analysis} 
                skills={skills} 
                graphData={graphData} 
                resumeId={currentResumeId}
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default App;