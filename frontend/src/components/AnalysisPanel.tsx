import React from 'react';
import type { GraphAnalysis, GraphData, Skill } from '../types';

interface Props {
  analysis: GraphAnalysis;
  skills: Skill[];
  graphData: GraphData;
  resumeId: string;
  // onExportPDF: () => void  // <-- add this prop
}

const AnalysisPanel: React.FC<Props> = ({ analysis, skills, graphData: _graphData, resumeId }) => {
  const exportToPDF = async () => {
    if (!resumeId) return;
    try {
      const response = await fetch(`http://localhost:8000/api/export/pdf?resume_id=${resumeId}`);
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
    }
  };

  const getSkillName = (id: string) => skills.find(s => s.id === id)?.name || id;

  return (
    <div className="border rounded-lg p-4 bg-gray-50 space-y-4">
      <div className="flex justify-between items-center mb-2">
        <h3 className="text-lg font-semibold">Step 4: Clusters, Isolates & Bridge Nodes</h3>
        <button
          onClick={() => window.print()}
          className="bg-blue-600 text-white px-3 py-1 rounded hover:bg-blue-700 text-sm"
        >
          🖨️ Print Page
        </button>
      </div>

        {/* New: Skill Coverage & Evidence Density */}
      <div className="bg-white p-3 rounded shadow-sm">
        <h4 className="font-medium mb-2">Skill Evidence Metrics</h4>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Skill Coverage Score:</span>
            <span className="ml-2 font-bold">{analysis.skill_coverage_score} skills</span>
          </div>
          <div>
            <span className="text-gray-600">Evidence Density Score:</span>
            <span className="ml-2 font-bold">{analysis.evidence_density_score}%</span>
            <span className="text-xs text-gray-500 ml-1">({analysis.edge_count} edges)</span>
          </div>
        </div>
        <div className="mt-3">
          <p className="text-xs text-gray-600">Skills with at least one project‑backed edge are <strong>evidenced</strong>.</p>
        </div>
      </div>

      {/* Strongly Evidenced Skills */}
      <div>
        <h4 className="font-medium text-green-700">✅ Strongly Evidenced Skills</h4>
        <div className="flex flex-wrap gap-1 mt-1">
          {analysis.strongly_evidenced_skills.length === 0 ? (
            <p className="text-sm text-gray-500">None yet. Add edges.</p>
          ) : (
            analysis.strongly_evidenced_skills.map(skill => (
              <span key={skill} className="px-2 py-0.5 bg-green-100 rounded-full text-sm">{skill}</span>
            ))
          )}
        </div>
      </div>

      {/* Weakly Evidenced Skills */}
      <div>
        <h4 className="font-medium text-red-700">⚠️ Weakly Evidenced Skills (need stronger narratives)</h4>
        <div className="flex flex-wrap gap-1 mt-1">
          {analysis.weakly_evidenced_skills.length === 0 ? (
            <p className="text-sm text-gray-500">All skills are evidenced – great!</p>
          ) : (
            analysis.weakly_evidenced_skills.map(skill => (
              <span key={skill} className="px-2 py-0.5 bg-red-100 rounded-full text-sm">{skill}</span>
            ))
          )}
        </div>
        <p className="text-xs text-gray-600 mt-1">
          These skills need project outcomes or resume bullets. Connect them via edges.
        </p>
      </div>

      <div>
        <h4 className="font-medium">Tight Clusters (areas of depth)</h4>
        {analysis.clusters.length === 0 && <p className="text-sm text-gray-500">No clusters yet. Add more edges.</p>}
        {analysis.clusters.map((cluster, idx) => (
          <div key={idx} className="mt-1">
            <span className="font-mono text-sm bg-gray-200 px-2 py-0.5 rounded">Cluster {idx+1}</span>
            <div className="flex flex-wrap gap-1 mt-1">
              {cluster.map(nodeId => (
                <span key={nodeId} className="px-2 py-0.5 bg-blue-100 rounded-full text-sm">{getSkillName(nodeId)}</span>
              ))}
            </div>
          </div>
        ))}
      </div>

      <div>
        <h4 className="font-medium">Bridge Nodes (cross-domain leverage)</h4>
        {analysis.bridge_nodes.length === 0 && <p className="text-sm text-gray-500">No bridge nodes detected.</p>}
        <div className="flex flex-wrap gap-1 mt-1">
          {analysis.bridge_nodes.map(nodeId => (
            <span key={nodeId} className="px-2 py-0.5 bg-orange-100 rounded-full text-sm font-semibold">{getSkillName(nodeId)}</span>
          ))}
        </div>
        {analysis.bridge_nodes.length > 0 && (
          <p className="text-xs text-gray-600 mt-1">These skills connect different clusters – highlight them in interviews/resume.</p>
        )}
      </div>

      <div>
        <h4 className="font-medium">Isolates (skills without connections)</h4>
        {analysis.isolates.length === 0 && <p className="text-sm text-gray-500">No isolates – great!</p>}
        <div className="flex flex-wrap gap-1 mt-1">
          {analysis.isolates.map(nodeId => (
            <span key={nodeId} className="px-2 py-0.5 bg-gray-200 rounded-full text-sm">{getSkillName(nodeId)}</span>
          ))}
        </div>
        <p className="text-xs text-gray-600 mt-1">Isolates belong at the bottom of your resume. Connect them if they were actually used together.</p>
      </div>

      <div className="pt-2 text-sm border-t text-gray-500">
        Graph has {analysis.node_count} nodes and {analysis.edge_count} edges.
      </div>
    </div>
  );
};

export default AnalysisPanel;