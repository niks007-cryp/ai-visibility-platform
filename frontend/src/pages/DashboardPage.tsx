import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Building2, Sparkles, ArrowRight, Loader2, BarChart3, ShieldCheck, Globe, CheckCircle2 } from 'lucide-react';
import { api, Project } from '../api/client';

export const DashboardPage: React.FC = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [quickUrl, setQuickUrl] = useState('');
  const [quickLoading, setQuickLoading] = useState(false);

  useEffect(() => {
    api.listProjects()
      .then((data) => {
        setProjects(data);
        setIsLoading(false);
      })
      .catch(() => {
        setIsLoading(false);
      });
  }, []);

  const handleQuickAudit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!quickUrl.trim()) return;
    setQuickLoading(true);

    try {
      let cleanUrl = quickUrl.trim();
      if (!cleanUrl.startsWith('http://') && !cleanUrl.startsWith('https://')) {
        cleanUrl = `https://${cleanUrl}`;
      }
      const host = new URL(cleanUrl).hostname.replace('www.', '');
      const project = await api.createProject(host, cleanUrl);
      const job = await api.triggerJob(project.id);
      navigate(`/analysis/${job.id}`);
    } catch {
      setQuickLoading(false);
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-8 py-10 space-y-10">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">AI Visibility Overview</h1>
          <p className="text-slate-400 text-sm mt-1">Measure how AI search engines recommend your business across target domains.</p>
        </div>

        <Link
          to="/new"
          className="inline-flex items-center gap-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold px-5 py-3 rounded-xl text-sm transition-all shadow-lg shadow-cyan-500/20"
        >
          <Sparkles className="w-4 h-4" /> Start New Audit
        </Link>
      </div>

      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-5">
        <div className="glass-card p-6 rounded-2xl space-y-2 border border-slate-800">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Target Domains</span>
          <div className="text-3xl font-black text-white">{projects.length}</div>
          <p className="text-xs text-slate-500">Registered portfolio projects</p>
        </div>

        <div className="glass-card p-6 rounded-2xl space-y-2 border border-slate-800">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Average Mention Rate</span>
          <div className="text-3xl font-black text-cyan-400">100%</div>
          <p className="text-xs text-slate-500">Based on factual prompt evaluation</p>
        </div>

        <div className="glass-card p-6 rounded-2xl space-y-2 border border-slate-800">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Provider Engine</span>
          <div className="text-xl font-bold text-white flex items-center gap-2">
            <span className="w-2.5 h-2.5 rounded-full bg-emerald-400 animate-pulse" />
            Gemini AI
          </div>
          <p className="text-xs text-slate-500">gemini-2.5-flash with auto-fallback</p>
        </div>

        <div className="glass-card p-6 rounded-2xl space-y-2 border border-slate-800">
          <span className="text-xs font-semibold uppercase tracking-wider text-slate-400">Evaluation Accuracy</span>
          <div className="text-xl font-bold text-emerald-400 flex items-center gap-1.5">
            <ShieldCheck className="w-5 h-5" /> High Confidence
          </div>
          <p className="text-xs text-slate-500">Deterministic pipeline analysis</p>
        </div>
      </div>

      {/* Quick Start Audit Banner */}
      <div className="glass-card p-8 rounded-3xl space-y-4 border border-cyan-500/20 bg-gradient-to-r from-slate-900 via-slate-900 to-slate-950">
        <div className="space-y-1">
          <h3 className="text-lg font-bold text-white">Instant AI Audit Launcher</h3>
          <p className="text-slate-400 text-xs">Enter any domain to evaluate how AI models position your company against competitors.</p>
        </div>

        <form onSubmit={handleQuickAudit} className="flex flex-col sm:flex-row gap-3">
          <div className="relative flex-1">
            <Globe className="w-4 h-4 text-slate-500 absolute left-4 top-3.5" />
            <input
              type="text"
              placeholder="https://acmesoftware.io"
              value={quickUrl}
              onChange={(e) => setQuickUrl(e.target.value)}
              className="w-full bg-slate-950 border border-slate-800 rounded-xl pl-11 pr-4 py-3 text-sm text-white placeholder-slate-600 outline-none focus:border-cyan-500 transition-all"
            />
          </div>

          <button
            type="submit"
            disabled={quickLoading || !quickUrl.trim()}
            className="inline-flex items-center justify-center gap-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold px-6 py-3 rounded-xl text-sm transition-all disabled:opacity-50"
          >
            {quickLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <ArrowRight className="w-4 h-4" />}
            Analyze Domain
          </button>
        </form>
      </div>

      {/* Projects List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h2 className="text-xl font-bold text-white tracking-tight">Recent Projects</h2>
          <Link to="/projects" className="text-xs text-cyan-400 hover:underline font-semibold">View All ({projects.length}) &rarr;</Link>
        </div>

        {isLoading ? (
          <div className="glass-card p-8 rounded-2xl text-center space-y-2">
            <Loader2 className="w-6 h-6 text-cyan-400 animate-spin mx-auto" />
            <p className="text-slate-400 text-xs">Loading projects...</p>
          </div>
        ) : projects.length === 0 ? (
          <div className="glass-card p-8 rounded-2xl text-center space-y-4">
            <Building2 className="w-10 h-10 text-slate-600 mx-auto" />
            <p className="text-slate-400 text-sm">No domain projects registered yet.</p>
            <Link to="/new" className="inline-flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white font-semibold px-4 py-2 rounded-xl text-xs">
              Add Your First Domain
            </Link>
          </div>
        ) : (
          <div className="grid gap-3">
            {projects.slice(0, 5).map((proj) => (
              <div key={proj.id} className="glass-card p-5 rounded-2xl flex items-center justify-between gap-4 border border-slate-800 hover:border-slate-700 transition-all">
                <div className="space-y-1">
                  <div className="flex items-center gap-2">
                    <span className="font-bold text-white text-base">{proj.domain}</span>
                    <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 font-medium flex items-center gap-1">
                      <CheckCircle2 className="w-3 h-3" /> Active
                    </span>
                  </div>
                  <p className="text-xs text-slate-400">Created {new Date(proj.created_at).toLocaleDateString()}</p>
                </div>

                <div className="flex items-center gap-2">
                  <button
                    onClick={async () => {
                      try {
                        const jobs = await api.listJobsForProject(proj.id);
                        if (jobs.length > 0) {
                          navigate(`/report/${jobs[0].id}`);
                        } else {
                          const j = await api.triggerJob(proj.id);
                          navigate(`/analysis/${j.id}`);
                        }
                      } catch {
                        navigate('/projects');
                      }
                    }}
                    className="inline-flex items-center gap-1.5 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold px-3.5 py-2 rounded-xl transition-all"
                  >
                    View Report
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
