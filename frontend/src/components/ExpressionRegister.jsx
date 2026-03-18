import React, { useState } from 'react';
import { Plus, Loader2 } from 'lucide-react';

/**
 * Componente para registrar uma nova expres seguinte.
 * Envia label + frame atual ao servidor via WebSocket.
 */
export function ExpressionRegister({ onSubmit = null, isLoading = false }) {
  const [label, setLabel] = useState('');
  const [feedback, setFeedback] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!label.trim()) {
      setFeedback({ type: 'error', message: 'Please enter a label' });
      setTimeout(() => setFeedback(null), 3000);
      return;
    }

    if (onSubmit) {
      try {
        await onSubmit(label.trim());
        setLabel('');
        setFeedback({ type: 'success', message: `Expression saved: ${label}` });
        setTimeout(() => setFeedback(null), 3000);
      } catch (err) {
        setFeedback({ type: 'error', message: err.message });
        setTimeout(() => setFeedback(null), 3000);
      }
    }
  };

  return (
    <div className="flex flex-col gap-3 bg-[#1a1a1a] rounded-lg border border-[#444444] p-4 shadow-xl">
      {/* Header */}
      <h3 className="text-[#E0E0E0] font-bold text-sm font-jetbrains">Register Expression</h3>

      {/* Form */}
      <form onSubmit={handleSubmit} className="flex flex-col gap-3">
        <div className="flex gap-2">
          <input
            type="text"
            value={label}
            onChange={(e) => setLabel(e.target.value)}
            placeholder="e.g. Smiling, Frowning, Winking"
            className="flex-1 bg-[#0a0a0a] border border-[#444444] rounded px-3 py-2 text-[#E0E0E0] text-sm font-jetbrains placeholder-[#888888] focus:outline-none focus:border-[#666666] transition-all"
            disabled={isLoading}
          />
          
          <button
            type="submit"
            disabled={isLoading || !label.trim()}
            className="flex items-center gap-2 bg-[#888888] hover:bg-[#aaaaaa] disabled:opacity-50 disabled:cursor-not-allowed px-4 py-2 rounded font-bold text-[#121212] text-sm font-jetbrains transition-all transform hover:scale-105 active:scale-95"
          >
            {isLoading ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                Saving
              </>
            ) : (
              <>
                <Plus size={16} />
                Register
              </>
            )}
          </button>
        </div>

        {/* Feedback */}
        {feedback && (
          <div
            className={`p-2 rounded text-xs font-jetbrains ${
              feedback.type === 'success'
                ? 'bg-green-900 bg-opacity-30 border border-green-700 text-green-300'
                : 'bg-red-900 bg-opacity-30 border border-red-700 text-red-300'
            }`}
          >
            {feedback.message}
          </div>
        )}

        {/* Info */}
        <p className="text-xs text-[#888888] font-jetbrains">
          Hold a facial expression, enter a name above, then press Register. Next time you show the same expression, it will be detected automatically.
        </p>
      </form>
    </div>
  );
}
