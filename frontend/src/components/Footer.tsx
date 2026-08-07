import React from 'react';
import { Sparkles, Terminal } from 'lucide-react';

export const Footer: React.FC = () => {
  return (
    <footer className="border-t border-slate-800/80 bg-slate-950 py-12 mt-20 text-slate-400 text-sm">
      <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row items-center justify-between gap-6">
        <div className="flex items-center gap-3">
          <div className="w-7 h-7 rounded-lg bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <Sparkles className="w-4 h-4" />
          </div>
          <span className="font-semibold text-slate-200">AI Visibility Operating System</span>
          <span className="text-slate-600">|</span>
          <span className="text-xs text-slate-500">Sprint 7 MVP</span>
        </div>

        <div className="flex items-center gap-6 text-xs text-slate-500">
          <span className="flex items-center gap-1">
            <Terminal className="w-3.5 h-3.5 text-cyan-400" /> Powered by Google Gemini & BaseProvider Architecture
          </span>
        </div>
      </div>
    </footer>
  );
};
