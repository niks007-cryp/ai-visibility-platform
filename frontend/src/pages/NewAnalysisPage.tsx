import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Globe, Building2, Sparkles, ArrowRight, AlertCircle, Loader2 } from 'lucide-react';
import { api } from '../api/client';

export const NewAnalysisPage: React.FC = () => {
  const navigate = useNavigate();
  const [url, setUrl] = useState('');
  const [name, setName] = useState('');
  const [industry, setIndustry] = useState('B2B SaaS');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!url.trim()) {
      setError('Please enter a valid website URL.');
      return;
    }

    setIsLoading(true);
    setError(null);

    try {
      // 1. Clean domain & derive name if blank
      let cleanUrl = url.trim();
      if (!cleanUrl.startsWith('http://') && !cleanUrl.startsWith('https://')) {
        cleanUrl = `https://${cleanUrl}`;
      }
      const projectName = name.trim() || new URL(cleanUrl).hostname.replace('www.', '');

      // 2. Create project
      const project = await api.createProject(projectName, cleanUrl);

      // 3. Trigger job
      const job = await api.triggerJob(project.id);

      // 4. Navigate to Progress page
      navigate(`/analysis/${job.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to start analysis audit. Please try again.');
      setIsLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto px-6 py-12">
      <div className="text-center space-y-3 mb-10">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" /> Instant AI Visibility Audit
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Run New AI Visibility Audit</h1>
        <p className="text-slate-400 text-sm">Enter your website URL to test if AI search engines recommend your business.</p>
      </div>

      <div className="glass-card p-8 rounded-3xl space-y-6 shadow-2xl">
        {error && (
          <div className="flex items-center gap-3 bg-red-500/10 border border-red-500/20 text-red-400 text-sm p-4 rounded-xl">
            <AlertCircle className="w-5 h-5 shrink-0" />
            <span>{error}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="space-y-2">
            <label className="block text-xs font-bold uppercase tracking-wider text-slate-300">
              Website URL <span className="text-cyan-400">*</span>
            </label>
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-4 flex items-center pointer-events-none text-slate-500">
                <Globe className="w-5 h-5" />
              </div>
              <input
                type="text"
                placeholder="https://acmesoftware.io"
                value={url}
                onChange={(e) => setUrl(e.target.value)}
                disabled={isLoading}
                className="w-full bg-slate-900/90 border border-slate-800 focus:border-cyan-500 rounded-xl py-3.5 pl-11 pr-4 text-white placeholder-slate-600 text-sm outline-none transition-all focus:ring-2 focus:ring-cyan-500/20"
                required
              />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-300">Company Name (Optional)</label>
              <input
                type="text"
                placeholder="Acme Software"
                value={name}
                onChange={(e) => setName(e.target.value)}
                disabled={isLoading}
                className="w-full bg-slate-900/90 border border-slate-800 focus:border-cyan-500 rounded-xl py-3 pl-4 pr-4 text-white placeholder-slate-600 text-sm outline-none transition-all"
              />
            </div>

            <div className="space-y-2">
              <label className="block text-xs font-bold uppercase tracking-wider text-slate-300">Industry Category</label>
              <div className="relative">
                <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-500">
                  <Building2 className="w-4 h-4" />
                </div>
                <select
                  value={industry}
                  onChange={(e) => setIndustry(e.target.value)}
                  disabled={isLoading}
                  className="w-full bg-slate-900/90 border border-slate-800 focus:border-cyan-500 rounded-xl py-3 pl-10 pr-4 text-white text-sm outline-none transition-all appearance-none cursor-pointer"
                >
                  <option value="B2B SaaS">B2B SaaS / Software</option>
                  <option value="Developer Tools">Developer Tools & APIs</option>
                  <option value="E-Commerce">E-Commerce & Retail</option>
                  <option value="Fintech">Financial Technology</option>
                  <option value="Healthcare">Healthcare & Biotech</option>
                </select>
              </div>
            </div>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full inline-flex items-center justify-center gap-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold py-4 rounded-xl text-base shadow-lg shadow-cyan-500/20 transition-all hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50"
          >
            {isLoading ? (
              <>
                <Loader2 className="w-5 h-5 animate-spin" /> Initializing Audit...
              </>
            ) : (
              <>
                Analyze AI Visibility
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>
        </form>
      </div>

      <div className="text-center pt-2">
        <button
          onClick={() => navigate('/projects')}
          className="text-xs text-slate-400 hover:text-cyan-400 font-medium inline-flex items-center gap-1.5 transition-colors"
        >
          <Building2 className="w-3.5 h-3.5" /> View All Previously Audited Projects & Reports &rarr;
        </button>
      </div>
    </div>
  );
};
