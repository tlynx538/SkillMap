import React from 'react';
import type { Skill } from '../types';

interface Props {
  skills: Skill[];
  onUpdate: (id: string, depth: number, recency: number) => Promise<void>;
}

const SkillTable: React.FC<Props> = ({ skills, onUpdate }) => {
  const [editing, setEditing] = React.useState<string | null>(null);
  const [depthTemp, setDepthTemp] = React.useState(3);
  const [recencyTemp, setRecencyTemp] = React.useState(3);

  const startEdit = (skill: Skill) => {
    setEditing(skill.id);
    setDepthTemp(skill.depth_score);
    setRecencyTemp(skill.recency_score);
  };

  const saveEdit = async (id: string) => {
    await onUpdate(id, depthTemp, recencyTemp);
    setEditing(null);
  };

  const getDepthLabel = (score: number) => {
    const labels: Record<number, string> = {
      1: 'Heard of it',
      2: 'Tutorial',
      3: 'Guided project',
      4: 'Independent multiple projects',
      5: 'Production / Design / Teach',
    };
    return labels[score] || '';
  };

  const getRecencyLabel = (score: number) => {
    const labels: Record<number, string> = {
      1: '5+ years ago',
      2: '3–5 years',
      3: '1–3 years',
      4: 'Last 12 months',
      5: 'Actively using',
    };
    return labels[score] || '';
  };

  return (
    <div>
      <h2 className="text-xl font-semibold mb-3">Step 2: Rate Depth & Recency</h2>
      <p className="text-gray-600 mb-4">
        Adjust the AI-suggested scores. Depth = real-world experience. Recency = last used.
      </p>
      <div className="overflow-x-auto">
        <table className="min-w-full border">
          <thead className="bg-gray-100">
            <tr>
              <th className="px-4 py-2 text-left">Skill</th>
              <th className="px-4 py-2 text-left">Depth (1–5)</th>
              <th className="px-4 py-2 text-left">Recency (1–5)</th>
              <th className="px-4 py-2"></th>
            </tr>
          </thead>
          <tbody>
            {skills.map((skill) => (
              <tr key={skill.id} className="border-t">
                <td className="px-4 py-2 font-medium">{skill.name}</td>
                <td className="px-4 py-2">
                  {editing === skill.id ? (
                    <div className="flex items-center gap-2">
                      <input
                        type="range"
                        min={1}
                        max={5}
                        value={depthTemp}
                        onChange={(e) => setDepthTemp(Number(e.target.value))}
                        className="w-32"
                      />
                      <span>{depthTemp}</span>
                    </div>
                  ) : (
                    <div>
                      <span className="font-mono font-bold">{skill.depth_score}</span> – {getDepthLabel(skill.depth_score)}
                    </div>
                  )}
                </td>
                <td className="px-4 py-2">
                  {editing === skill.id ? (
                    <div className="flex items-center gap-2">
                      <input
                        type="range"
                        min={1}
                        max={5}
                        value={recencyTemp}
                        onChange={(e) => setRecencyTemp(Number(e.target.value))}
                        className="w-32"
                      />
                      <span>{recencyTemp}</span>
                    </div>
                  ) : (
                    <div>
                      <span className="font-mono font-bold">{skill.recency_score}</span> – {getRecencyLabel(skill.recency_score)}
                    </div>
                  )}
                </td>
                <td className="px-4 py-2">
                  {editing === skill.id ? (
                    <button
                      onClick={() => saveEdit(skill.id)}
                      className="bg-green-600 text-white px-2 py-1 rounded text-sm"
                    >
                      Save
                    </button>
                  ) : (
                    <button
                      onClick={() => startEdit(skill)}
                      className="text-blue-600 hover:underline text-sm"
                    >
                      Edit
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      {skills.length === 0 && (
        <p className="text-gray-500 text-center py-8">No skills yet. Go to Import tab first.</p>
      )}
    </div>
  );
};

export default SkillTable;
