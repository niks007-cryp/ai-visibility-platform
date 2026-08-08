import React, { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import {
  CheckCircle2,
  XCircle,
  ExternalLink,
  Sparkles,
  ChevronDown,
  ChevronUp,
  FileText,
  Cpu,
  Quote,
  Layers,
  ArrowLeft,
  Loader2,
  AlertCircle,
  ShieldCheck,
  Activity,
  AlertTriangle
} from 'lucide-react';
import { api, JobReport, EvaluationSummary } from '../api/client';

export const ReportPage: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const [report, setReport] = useState<JobReport | null>(null);
  const [evaluation, setEvaluation] = useState<EvaluationSummary | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showRawText, setShowRawText] = useState(false);

  useEffect(() => {
    if (!jobId) return;

    Promise.all([
      api.getJobReport(jobId),
      api.getEvaluationSummary(jobId).catch(() => null),
    ])
      .then(([reportData, evalData]) => {
        setReport(reportData);
        setEvaluation(evalData);
        setIsLoading(false);
      })
      .catch((err) => {
        setError(err.message || 'Failed to load report.');
        setIsLoading(false);
      });
  }, [jobId]);

  if (isLoading) {
    return (
      <div className="max-w-4xl mx-auto px-6 py-24 text-center space-y-4">
        <Loader2 className="w-10 h-10 text-cyan-400 animate-spin mx-auto" />
        <h2 className="text-xl font-bold text-white">Loading AI Visibility Report & Confidence Evaluation...</h2>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div className="max-w-xl mx-auto px-6 py-16 text-center space-y-6">
        <div className="flex items-center gap-3 bg-red-500/10 border border-red-500/20 text-red-400 text-sm p-4 rounded-xl">
          <AlertCircle className="w-5 h-5 shrink-0" />
          <span>{error || 'Report not found.'}</span>
        </div>
        <Link
          to="/new"
          className="inline-flex items-center gap-2 bg-slate-800 hover:bg-slate-700 text-white font-semibold px-6 py-3 rounded-xl text-sm transition-all"
        >
          <ArrowLeft className="w-4 h-4" /> Start New Audit
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-4xl mx-auto px-6 py-10 space-y-8">
      {/* Top Action Bar */}
      <div className="flex items-center justify-between">
        <Link
          to="/new"
          className="inline-flex items-center gap-2 text-slate-400 hover:text-white text-sm font-medium transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to New Audit
        </Link>

        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" /> Deterministic Evaluation Report
        </div>
      </div>

      {/* Header Executive Summary Card */}
      <div className="glass-card p-8 rounded-3xl space-y-6 shadow-2xl relative overflow-hidden">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-6">
          <div className="space-y-2">
            <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Target Website Domain</span>
            <h1 className="text-3xl font-extrabold text-white tracking-tight">{report.target_domain}</h1>
            <p className="text-xs text-slate-400">Project: <span className="text-white font-medium">{report.project_name}</span> &bull; Verified: <span className="text-slate-300 font-medium">Deterministic Engine Analysis</span></p>
          </div>

          <div>
            {report.mentioned ? (
              <div className="inline-flex items-center gap-2.5 px-5 py-3 rounded-2xl bg-emerald-500/10 border border-emerald-500/30 text-emerald-400 font-bold text-sm shadow-lg shadow-emerald-500/10">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                RECOMMENDED IN AI OUTPUT
              </div>
            ) : (
              <div className="inline-flex items-center gap-2.5 px-5 py-3 rounded-2xl bg-rose-500/10 border border-rose-500/30 text-rose-400 font-bold text-sm shadow-lg shadow-rose-500/10">
                <XCircle className="w-5 h-5 text-rose-400" />
                OMITTED IN AI OUTPUT
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Confidence & Consistency Framework Card */}
      {evaluation && (
        <div className="glass-card p-6 rounded-3xl space-y-6 border border-cyan-500/20 shadow-xl">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-cyan-400 font-bold text-sm">
              <ShieldCheck className="w-5 h-5" />
              <h3>Multi-Prompt Confidence & Consistency Evaluation</h3>
            </div>

            {/* Confidence Badge */}
            <div className={`px-4 py-1.5 rounded-full text-xs font-extrabold tracking-wider border uppercase ${
              evaluation.confidence_level === 'HIGH'
                ? 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30'
                : evaluation.confidence_level === 'MEDIUM'
                ? 'bg-amber-500/10 text-amber-400 border-amber-500/30'
                : 'bg-rose-500/10 text-rose-400 border-rose-500/30'
            }`}>
              {evaluation.confidence_level} CONFIDENCE
            </div>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-center">
            <div className="bg-slate-900/90 p-4 rounded-2xl border border-slate-800 space-y-1">
              <span className="text-slate-500 text-xs font-semibold uppercase">Consistency</span>
              <p className="text-2xl font-black text-white">{evaluation.consistency_percentage}%</p>
            </div>

            <div className="bg-slate-900/90 p-4 rounded-2xl border border-slate-800 space-y-1">
              <span className="text-slate-500 text-xs font-semibold uppercase">Prompt Coverage</span>
              <p className="text-2xl font-black text-cyan-400">{evaluation.total_prompts} Prompts</p>
            </div>

            <div className="bg-slate-900/90 p-4 rounded-2xl border border-slate-800 space-y-1">
              <span className="text-slate-500 text-xs font-semibold uppercase">Mention Rate</span>
              <p className="text-2xl font-black text-indigo-400">{Math.round(evaluation.mention_rate * 100)}%</p>
            </div>

            <div className="bg-slate-900/90 p-4 rounded-2xl border border-slate-800 space-y-1">
              <span className="text-slate-500 text-xs font-semibold uppercase">Providers Tested</span>
              <p className="text-2xl font-black text-blue-400">{evaluation.provider_count} Provider</p>
            </div>
          </div>

          {/* Contradictions Drawer */}
          {evaluation.contradictions.length > 0 && (
            <div className="bg-amber-500/10 border border-amber-500/30 p-4 rounded-2xl space-y-3">
              <div className="flex items-center gap-2 text-amber-400 font-bold text-xs uppercase tracking-wider">
                <AlertTriangle className="w-4 h-4" />
                <span>Prompt Contradictions Detected ({evaluation.contradictions.length})</span>
              </div>
              <div className="space-y-2 text-xs text-amber-200">
                {evaluation.contradictions.map((c, idx) => (
                  <p key={idx} className="bg-slate-950/60 p-3 rounded-xl border border-amber-500/20">
                    {c.description}
                  </p>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Factual Evidence Grid */}
      <div className="grid md:grid-cols-2 gap-6">
        {/* Matched Sentence Quotes */}
        <div className="glass-card p-6 rounded-3xl space-y-4">
          <div className="flex items-center gap-2 text-cyan-400 font-semibold text-sm">
            <Quote className="w-4 h-4" />
            <h3>Matching Evidence Quotes ({report.matched_snippets.length})</h3>
          </div>

          {report.matched_snippets.length > 0 ? (
            <div className="space-y-3">
              {report.matched_snippets.map((snippet, idx) => (
                <div key={idx} className="bg-slate-900/90 border border-slate-800/80 p-4 rounded-xl text-slate-200 text-xs italic leading-relaxed">
                  "{snippet}"
                </div>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 italic">No direct sentence quotes referencing {report.target_domain} were found in the AI response.</p>
          )}
        </div>

        {/* URL Citations */}
        <div className="glass-card p-6 rounded-3xl space-y-4">
          <div className="flex items-center gap-2 text-blue-400 font-semibold text-sm">
            <ExternalLink className="w-4 h-4" />
            <h3>Explicit URL Citations ({report.raw_citations.length})</h3>
          </div>

          {report.raw_citations.length > 0 ? (
            <div className="space-y-2">
              {report.raw_citations.map((url, idx) => (
                <a
                  key={idx}
                  href={url}
                  target="_blank"
                  rel="noreferrer"
                  className="flex items-center justify-between bg-slate-900/90 border border-slate-800/80 hover:border-cyan-500/40 p-3 rounded-xl text-cyan-400 text-xs truncate transition-all group"
                >
                  <span className="truncate">{url}</span>
                  <ExternalLink className="w-3.5 h-3.5 shrink-0 opacity-60 group-hover:opacity-100" />
                </a>
              ))}
            </div>
          ) : (
            <p className="text-xs text-slate-500 italic">No direct HTTP/HTTPS URL citations were embedded in the AI response.</p>
          )}
        </div>
      </div>

      {/* Cited Brand Tokens */}
      <div className="glass-card p-6 rounded-3xl space-y-4">
        <div className="flex items-center gap-2 text-indigo-400 font-semibold text-sm">
          <Layers className="w-4 h-4" />
          <h3>Extracted Competitor & Brand Tokens ({report.extracted_brand_mentions.length})</h3>
        </div>

        <div className="flex flex-wrap gap-2">
          {report.extracted_brand_mentions.map((brand, idx) => (
            <span
              key={idx}
              className={`px-3 py-1.5 rounded-xl text-xs font-semibold border ${
                brand.toLowerCase().includes(report.target_domain.split('.')[0])
                  ? 'bg-cyan-500/20 text-cyan-300 border-cyan-500/40 font-bold'
                  : 'bg-slate-900 text-slate-300 border-slate-800'
              }`}
            >
              {brand}
            </span>
          ))}
        </div>
      </div>

      {/* AI Provider Context Card */}
      <div className="glass-card p-6 rounded-3xl space-y-4">
        <div className="flex items-center gap-2 text-slate-300 font-semibold text-sm">
          <Cpu className="w-4 h-4 text-cyan-400" />
          <h3>AI Provider Query Context</h3>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
          <div className="bg-slate-900/90 p-4 rounded-xl border border-slate-800 space-y-1">
            <span className="text-slate-500 font-semibold uppercase">Provider Engine</span>
            <p className="text-white font-mono font-bold">{report.provider_name}</p>
          </div>

          <div className="bg-slate-900/90 p-4 rounded-xl border border-slate-800 space-y-1">
            <span className="text-slate-500 font-semibold uppercase">Submitted Category Prompt</span>
            <p className="text-slate-300 truncate">{report.prompt}</p>
          </div>
        </div>
      </div>
    </div>
  );
};
