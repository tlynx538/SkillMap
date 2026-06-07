import React, { useState } from 'react';
import type { Skill } from '../types';

interface Props {
  skills: Skill[];
  onCreate: (edge: { from_skill_id: string; to_skill_id: string; project_name: string; outcome: string }) => Promise<void>;
}

const EdgeForm: React.FC<Props> = ({ skills, onCreate }) => {
  const [fromId, setFromId] = useState('');
  const [toId, setToId] = useState('');
  const [project, setProject] = useState('');
  const [outcome, setOutcome] = useState('');
  const [submitting, setSubmitting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!fromId || !toId || !project.trim() || !outcome.trim()) return;
    setSubmitting(true);
    try {
      await onCreate({ from_skill_id: fromId, to_skill_id: toId, project_name: project, outcome });
      setFromId('');
      setToId('');
      setProject('');
      setOutcome('');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="border rounded-lg p-4 bg-gray-50">
      <h3 className="text-lg font-semibold mb-2">Step 3: Draw an Edge</h3>
      <p className="text-sm text-gray-600 mb-4">
        Connect two skills you've used together on a real project with a measurable outcome.
      </p>
      <form onSubmit={handleSubmit} className="space-y-3">
        <div className="grid grid-cols-2 gap-4">
          <select
            value={fromId}
            onChange={(e) => setFromId(e.target.value)}
            required
            className="p-2 border rounded"
          >
            <option value="">Select skill A</option>
            {skills.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
          <select
            value={toId}
            onChange={(e) => setToId(e.target.value)}
            required
            className="p-2 border rounded"
          >
            <option value="">Select skill B</option>
            {skills.map(s => <option key={s.id} value={s.id}>{s.name}</option>)}
          </select>
        </div>
        <input
          type="text"
          placeholder="Project name (e.g., Payment Gateway Rewrite)"
          value={project}
          onChange={(e) => setProject(e.target.value)}
          required
          className="w-full p-2 border rounded"
        />
        <textarea
          placeholder="Outcome / artifact (e.g., reduced p99 latency from 800ms to 120ms, deployed to production, PR #123)"
          value={outcome}
          onChange={(e) => setOutcome(e.target.value)}
          required
          className="w-full p-2 border rounded"
          rows={2}
        />
        <button
          type="submit"
          disabled={submitting}
          className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700"
        >
          Add Edge
        </button>
      </form>
    </div>
  );
};

export default EdgeForm;
