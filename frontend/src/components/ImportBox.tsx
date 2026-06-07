import React, { useState } from 'react';

interface Props {
  onImport: (text: string, name?: string) => Promise<void>;
}

const ImportBox: React.FC<Props> = ({ onImport }) => {
  const [text, setText] = useState('');
  const [name, setName] = useState('');
  const [isImporting, setIsImporting] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!text.trim()) return;
    setIsImporting(true);
    try {
      await onImport(text, name.trim() || undefined);
      setText('');
      setName('');
    } finally {
      setIsImporting(false);
    }
  };

  return (
    <div>
      <h2 className="text-xl font-semibold mb-3">Step 1: Inventory Your Skills</h2>
      <p className="text-gray-600 mb-4">
        Paste your resume, project descriptions, or any text. AI will extract skills and edges.
      </p>
      <form onSubmit={handleSubmit}>
        <input
          type="text"
          placeholder="Optional: Name this resume (e.g., John's Resume 2025)"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full p-2 border rounded mb-3"
        />
        <textarea
          className="w-full h-64 p-3 border rounded-lg font-mono text-sm"
          placeholder="Paste your text here..."
          value={text}
          onChange={(e) => setText(e.target.value)}
        />
        <div className="mt-4">
          <button
            type="submit"
            disabled={isImporting || !text.trim()}
            className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:opacity-50"
          >
            {isImporting ? 'Importing...' : 'Import with AI'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default ImportBox;