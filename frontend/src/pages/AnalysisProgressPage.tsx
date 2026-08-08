import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Loader2, AlertCircle, RefreshCw, Sparkles } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { api, AnalysisJob } from '../api/client';

export const AnalysisProgressPage: React.FC = () => {
  const { jobId } = useParams<{ jobId: string }>();
  const navigate = useNavigate();

  const [job, setJob] = useState<AnalysisJob | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [msgIndex, setMsgIndex] = useState(0);

  const pollTimerRef = useRef<any>(null);
  const isMountedRef = useRef<boolean>(true);
  const consecutiveErrorsRef = useRef<number>(0);

  const statusMessages = [
    "Understanding how AI engines position your brand...",
    "Reviewing AI search recommendations...",
    "Identifying key brand mentions...",
    "Preparing your executive visibility report..."
  ];

  const stopPolling = () => {
    if (pollTimerRef.current) {
      clearInterval(pollTimerRef.current);
      pollTimerRef.current = null;
    }
  };

  useEffect(() => {
    const timer = setInterval(() => {
      setMsgIndex((prev) => (prev + 1) % statusMessages.length);
    }, 3500);
    return () => clearInterval(timer);
  }, []);

  useEffect(() => {
    if (!jobId) return;

    isMountedRef.current = true;
    consecutiveErrorsRef.current = 0;

    const pollJobStatus = async () => {
      if (!isMountedRef.current) return;

      try {
        const jobData = await api.getJob(jobId);
        if (!isMountedRef.current) return;

        consecutiveErrorsRef.current = 0;
        setJob(jobData);

        const currentStatus = (jobData.status || '').toString().toLowerCase();

        if (currentStatus === 'completed') {
          stopPolling();
          navigate(`/report/${jobId}`, { replace: true });
        } else if (currentStatus === 'failed') {
          stopPolling();
          setError(jobData.error_message || "Your analysis couldn't be completed. Please try again.");
        } else if (currentStatus === 'cancelled') {
          stopPolling();
          setError("This analysis was cancelled.");
        }
      } catch {
        if (!isMountedRef.current) return;
        consecutiveErrorsRef.current += 1;

        if (consecutiveErrorsRef.current >= 5) {
          stopPolling();
          setError("We couldn't reach the analysis server. Please check your connection.");
        }
      }
    };

    // Immediate initial status check
    pollJobStatus();

    // Schedule 2s polling interval
    pollTimerRef.current = setInterval(pollJobStatus, 2000);

    return () => {
      isMountedRef.current = false;
      stopPolling();
    };
  }, [jobId, navigate]);

  const handleRetry = () => {
    if (!jobId) return;
    setError(null);
    api.executeJob(jobId).catch(() => {
      setError("Retry request failed. Please try starting a new analysis.");
    });
  };

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.98 }}
      animate={{ opacity: 1, scale: 1 }}
      transition={{ duration: 0.3 }}
      className="max-w-lg mx-auto px-4 sm:px-6 py-16 sm:py-24 text-center space-y-8"
    >
      <div className="space-y-3">
        <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold">
          <Sparkles className="w-3.5 h-3.5" /> AI Intelligence Analysis
        </div>
        <h1 className="text-2xl sm:text-3xl font-extrabold text-white tracking-tight">
          {error ? "Analysis Couldn't Be Completed" : "Analyzing Your AI Visibility"}
        </h1>
        <p className="text-slate-400 text-xs sm:text-sm">
          {error
            ? "Something went wrong while analyzing your brand across AI-powered answers."
            : "We're reviewing how AI search engines recommend your brand."}
        </p>
      </div>

      <div className="glass-card p-8 rounded-3xl space-y-6 border border-slate-800 shadow-2xl">
        {error ? (
          <div className="space-y-6">
            <div className="flex items-center gap-3 bg-red-500/10 border border-red-500/20 text-red-400 text-sm p-4 rounded-xl text-left">
              <AlertCircle className="w-5 h-5 shrink-0" />
              <span>{error}</span>
            </div>

            <button
              onClick={handleRetry}
              className="w-full inline-flex items-center justify-center gap-2 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white font-bold py-3.5 rounded-xl text-sm transition-all shadow-lg shadow-cyan-500/20 active:scale-98"
            >
              <RefreshCw className="w-4 h-4" /> Try Again
            </button>
          </div>
        ) : (
          <div className="py-6 space-y-6">
            {/* Minimal Pulse Loading Visual */}
            <div className="relative w-16 h-16 mx-auto flex items-center justify-center">
              <div className="absolute inset-0 rounded-full bg-cyan-500/20 animate-ping" />
              <div className="w-12 h-12 rounded-full bg-gradient-to-tr from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/30">
                <Loader2 className="w-6 h-6 text-white animate-spin" />
              </div>
            </div>

            {/* Rotating High-Level Contextual Copy */}
            <div className="h-8 flex items-center justify-center">
              <AnimatePresence mode="wait">
                <motion.p
                  key={msgIndex}
                  initial={{ opacity: 0, y: 5 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -5 }}
                  transition={{ duration: 0.25 }}
                  className="text-sm font-medium text-slate-300"
                >
                  {statusMessages[msgIndex]}
                </motion.p>
              </AnimatePresence>
            </div>

            <p className="text-xs text-slate-500">This usually takes a short while. Please keep this window open.</p>
          </div>
        )}
      </div>
    </motion.div>
  );
};
