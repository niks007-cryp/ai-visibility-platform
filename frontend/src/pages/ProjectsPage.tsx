import React, { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Building2, Sparkles, ArrowRight, Loader2, AlertCircle, Plus, Search } from 'lucide-react';
import { api, Project } from '../api/client';

export const ProjectsPage: React.FC = () => {
  const navigate = useNavigate();
  const [projects, setProjects] = useState<Project[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [actionLoadingId, setActionLoadingId] = useState<string | null>(null);

  useEffect(() => {
    api.listProjects()
      .then((data) => {
        setProjects(data);
        setIsLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load projects list.');
        setIsLoading(false);
      });
  }, []);

  const handleRunAudit = async (projectId: string) => {
    setActionLoadingId(projectId);
    try {
      const job = await api.triggerJob(projectId);
      navigate(`/analysis/${job.id}`);
    } catch (err: any) {
      setError(err.message || 'Failed to trigger audit.');
      setActionLoadingId(null);
    }
  };

  const handleViewLatest = async (projectId: string) => {
    setActionLoadingId(projectId);
    try {
      const jobs = await api.listJobsForProject(projectId);
      if (jobs.length > 0) {
        navigate(`/report/${jobs[0].id}`);
      } else {
        const newJob = await api.triggerJob(projectId);
        navigate(`/analysis/${newJob.id}`);
      }
    } catch (err: any) {
      setError(err.message || 'Failed to load project audit history.');
      setActionLoadingId(null);
    }
  };

  const filtered = projects.filter(
    (p) => p.name.toLowerCase().includes(search.toLowerCase()) || p.domain.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div className="max-w-4xl mx-auto px-6 py-12 space-y-8">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold mb-2">
            <Sparkles className="w-3.5 h-3.5" /> Project Audit Portfolio
          </div>
          <h1 className="text-3xl font-extrabold text-white tracking-tight">Your Target Domains</h1>
          <p className="text-slate-400 text-sm">View, retrieve, and re-audit your registered domain projects.</p>
        </div>

        <Link
          to="/new"
          className="inline-flex items-center gap-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold px-5 py-3 rounded-xl text-sm transition-all shadow-lg shadow-cyan-500/20"
        >
          <Plus className="w-4 h-4" /> New Audit Project
        </Link>
      </div>

      {/* Search Input */}
      {projects.length > 0 && (
        <div className="relative">
          <Search className="w-4 h-4 text-slate-500 absolute left-4 top-3.5" />
          <input
            type="text"
            placeholder="Search domains or project names..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full bg-slate-900 border border-slate-800 rounded-xl pl-11 pr-4 py-3 text-sm text-white placeholder-slate-500 focus:outline-none focus:border-cyan-500 transition-all"
          />
        </div>
      )}

      {error && (
        <div className="flex items-center gap-3 bg-red-500/10 border border-red-500/20 text-red-400 text-sm p-4 rounded-xl">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error}</span>
        </div>
      )}

      {isLoading ? (
        <div className="glass-card p-12 rounded-3xl text-center space-y-4">
          <Loader2 className="w-8 h-8 text-cyan-400 animate-spin mx-auto" />
          <p className="text-slate-400 text-sm">Loading project portfolio...</p>
        </div>
      ) : filtered.length === 0 ? (
        <div className="glass-card p-12 rounded-3xl text-center space-y-6">
          <Building2 className="w-12 h-12 text-slate-600 mx-auto" />
          <div className="space-y-1">
            <h3 className="text-lg font-bold text-white">No Projects Found</h3>
            <p className="text-slate-400 text-sm">
              {search ? 'No domain matches your search query.' : 'You have not registered any domain projects yet.'}
            </p>
          </div>
          <Link
            to="/new"
            className="inline-flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white font-semibold px-6 py-3 rounded-xl text-sm transition-all"
          >
            <Plus className="w-4 h-4" /> Run Your First Audit
          </Link>
        </div>
      ) : (
        <div className="grid gap-4">
          {filtered.map((proj) => (
            <div
              key={proj.id}
              className="glass-card p-6 rounded-2xl flex flex-col md:flex-row md:items-center justify-between gap-4 hover:border-slate-700 transition-all"
            >
              <div className="space-y-1">
                <div className="flex items-center gap-2">
                  <h3 className="text-lg font-bold text-white">{proj.domain}</h3>
                  <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 font-mono">
                    #{proj.id.slice(0, 8)}
                  </span>
                </div>
                <p className="text-xs text-slate-400">
                  Name: {proj.name} | Registered: {new Date(proj.created_at).toLocaleDateString()}
                </p>
              </div>

              <div className="flex items-center gap-3">
                <button
                  onClick={() => handleViewLatest(proj.id)}
                  disabled={actionLoadingId === proj.id}
                  className="inline-flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white text-xs font-semibold px-4 py-2.5 rounded-xl transition-all disabled:opacity-50"
                >
                  {actionLoadingId === proj.id ? (
                    <Loader2 className="w-3.5 h-3.5 animate-spin" />
                  ) : (
                    <ArrowRight className="w-3.5 h-3.5 text-cyan-400" />
                  )}
                  View Report
                </button>

                <button
                  onClick={() => handleRunAudit(proj.id)}
                  disabled={actionLoadingId === proj.id}
                  className="inline-flex items-center gap-2 bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/20 text-xs font-semibold px-4 py-2.5 rounded-xl transition-all disabled:opacity-50"
                >
                  <Sparkles className="w-3.5 h-3.5" /> Re-Audit
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};
