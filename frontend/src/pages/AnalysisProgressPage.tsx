import React, { useEffect, useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Loader2, CheckCircle2, AlertCircle, RefreshCw, Sparkles, ShieldCheck } from 'lucide-react';
import { api, AnalysisJob } from '../api/client';

export const AnalysisProgressPage: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();

  const [job, setJob] = useState<AnalysisJob | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [step, setStep] = useState<number>(1);

  useEffect(() => {
    if (!jobId) return;

    let isSubscribed = true;
    let pollInterval: any = null;

    const pollJobStatus = async () => {
      try {
        const jobData = await api.getJob(jobId);
        if (!isSubscribed) return;

        setJob(jobData);

        if (jobData.status === 'Completed') {
          setStep(4);
          setTimeout(() => {
            navigate(`/report/${jobId}`);
          }, 800);
        } else if (jobData.status === 'Failed') {
          setError('Analysis encountered an issue. Click below to retry.');
        } else if (jobData.status === 'Running') {
          setStep(3);
        } else if (jobData.status === 'Pending' || jobData.status === 'Queued') {
          setStep(2);
        }
      } catch {
        if (isSubscribed) {
          setError('Unable to load analysis status. Please check your connection.');
        }
      }
    };

    pollJobStatus();
    pollInterval = setInterval(pollJobStatus, 1500);

    return () => {
      isSubscribed = false;
      if (pollInterval) clearInterval(pollInterval);
    };
  }, [jobId, navigate]);

  const handleRetry = () => {
    if (!jobId) return;
    setError(null);
    setStep(2);
    api.executeJob(jobId).catch(() => {
      setError('Retry failed. Please try launching a new audit.');
    });
  };

  const shortRef = jobId ? `#${jobId.slice(0, 8)}` : '';

  return (
    <div className="max-w-xl mx-auto px-6 py-16 text-center space-y-8">
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" /> Deterministic Pipeline Active
        </div>
        <h1 className="text-3xl font-extrabold text-white tracking-tight">Analyzing AI Visibility...</h1>
        <p className="text-slate-400 text-sm">Evaluating brand recommendations across AI search engines.</p>
      </div>

      <div className="glass-card p-8 rounded-3xl space-y-8 text-left shadow-2xl border border-slate-800">
        {error ? (
          <div className="space-y-4">
            <div className="flex items-center gap-3 bg-red-500/10 border border-red-500/20 text-red-400 text-sm p-4 rounded-xl">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{error}</span>
            </div>
            <button
              onClick={handleRetry}
              className="w-full inline-flex items-center justify-center gap-2 bg-slate-800 hover:bg-slate-700 text-white font-semibold py-3 rounded-xl text-sm transition-all"
            >
              <RefreshCw className="w-4 h-4" /> Retry Analysis
            </button>
          </div>
        ) : (
          <>
            {/* Animated Progress Bar */}
            <div className="space-y-2">
              <div className="flex justify-between text-xs font-semibold text-slate-400">
                <span>Progress</span>
                <span>{step === 1 ? '25%' : step === 2 ? '50%' : step === 3 ? '85%' : '100%'}</span>
              </div>
              <div className="w-full h-2.5 bg-slate-900 rounded-full overflow-hidden border border-slate-800">
                <div
                  className="h-full bg-gradient-to-r from-cyan-500 to-blue-600 transition-all duration-500 rounded-full"
                  style={{ width: step === 1 ? '25%' : step === 2 ? '50%' : step === 3 ? '85%' : '100%' }}
                />
              </div>
            </div>

            {/* Stage Timeline */}
            <div className="space-y-4 pt-2">
              <TimelineStep
                title="Preparing Analysis Parameters"
                description="Validating domain context and evaluation prompt catalog"
                isDone={step > 1}
                isActive={step === 1}
              />
              <TimelineStep
                title="Evaluating AI Search Providers"
                description="Querying Google Gemini provider engine with automated model failover"
                isDone={step > 2}
                isActive={step === 2}
              />
              <TimelineStep
                title="Extracting Factual Evidence"
                description="Parsing brand presence, URL citations, and verbatim quote snippets"
                isDone={step > 3}
                isActive={step === 3}
              />
              <TimelineStep
                title="Finalizing Executive Report"
                description="Assembling confidence scores and strategic recommendations"
                isDone={step >= 4}
                isActive={step === 4}
              />
            </div>
          </>
        )}
      </div>

      <div className="flex items-center justify-center gap-2 text-xs text-slate-500">
        <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
        <span>Audit Reference {shortRef}</span>
      </div>
    </div>
  );
};

interface TimelineStepProps {
  title: string;
  description: string;
  isDone: boolean;
  isActive: boolean;
}

const TimelineStep: React.FC<TimelineStepProps> = ({ title, description, isDone, isActive }) => {
  return (
    <div className="flex items-start gap-4">
      <div className="mt-0.5 shrink-0">
        {isDone ? (
          <CheckCircle2 className="w-5 h-5 text-emerald-400" />
        ) : isActive ? (
          <Loader2 className="w-5 h-5 text-cyan-400 animate-spin" />
        ) : (
          <div className="w-5 h-5 rounded-full border-2 border-slate-800 bg-slate-900" />
        )}
      </div>
      <div>
        <h4 className={`text-sm font-semibold ${isDone || isActive ? 'text-white' : 'text-slate-600'}`}>{title}</h4>
        <p className="text-xs text-slate-500 mt-0.5">{description}</p>
      </div>
    </div>
  );
};
