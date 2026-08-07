import React from 'react';
import { Link } from 'react-router-dom';
import { Sparkles, ArrowRight, ShieldCheck, Zap, BarChart3, CheckCircle2 } from 'lucide-react';

export const LandingPage: React.FC = () => {
  return (
    <div className="space-y-24 py-12">
      {/* Hero Section */}
      <section className="text-center max-w-4xl mx-auto px-6 space-y-8">
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 text-xs font-semibold uppercase tracking-wider shadow-lg shadow-cyan-500/10">
          <Sparkles className="w-3.5 h-3.5" /> Next-Generation Answer Engine Optimization
        </div>

        <h1 className="text-4xl md:text-6xl font-extrabold text-white tracking-tight leading-tight">
          If someone asks AI about your business,{' '}
          <span className="bg-gradient-to-r from-cyan-400 via-blue-500 to-indigo-400 bg-clip-text text-transparent">
            will it recommend you?
          </span>
        </h1>

        <p className="text-lg md:text-xl text-slate-400 max-w-2xl mx-auto leading-relaxed">
          Stop guessing why ChatGPT and Google Gemini omit your product. Audit your AI visibility in 30 seconds with 100% deterministic evidence.
        </p>

        <div className="pt-4 flex flex-col sm:flex-row items-center justify-center gap-4">
          <Link
            to="/new"
            className="w-full sm:w-auto inline-flex items-center justify-center gap-3 bg-gradient-to-r from-cyan-500 to-blue-600 hover:from-cyan-400 hover:to-blue-500 text-white px-8 py-4 rounded-2xl text-base font-bold shadow-xl shadow-cyan-500/25 transition-all hover:scale-105 active:scale-95"
          >
            Analyze Your AI Visibility
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>

        <div className="pt-6 flex items-center justify-center gap-8 text-xs text-slate-500 font-medium">
          <span className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Free instant audit
          </span>
          <span className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" /> No credit card required
          </span>
          <span className="flex items-center gap-1.5">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" /> Live Gemini AI engine
          </span>
        </div>
      </section>

      {/* Value Proposition Cards */}
      <section className="max-w-6xl mx-auto px-6 grid md:grid-cols-3 gap-6">
        <div className="glass-card glass-card-hover p-8 rounded-3xl space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center text-cyan-400">
            <ShieldCheck className="w-6 h-6" />
          </div>
          <h3 className="text-xl font-bold text-white">Deterministic Evidence</h3>
          <p className="text-slate-400 text-sm leading-relaxed">
            Zero black-box hallucinations. Every audit conclusion is backed by verbatim quote snippets and explicit URL citations extracted directly from AI outputs.
          </p>
        </div>

        <div className="glass-card glass-card-hover p-8 rounded-3xl space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-blue-500/10 border border-blue-500/20 flex items-center justify-center text-blue-400">
            <Zap className="w-6 h-6" />
          </div>
          <h3 className="text-xl font-bold text-white">30s Instant Time-to-Value</h3>
          <p className="text-slate-400 text-sm leading-relaxed">
            Enter your website URL and get a full AI visibility report in under 30 seconds. No complex configuration or API key setup required.
          </p>
        </div>

        <div className="glass-card glass-card-hover p-8 rounded-3xl space-y-4">
          <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center text-indigo-400">
            <BarChart3 className="w-6 h-6" />
          </div>
          <h3 className="text-xl font-bold text-white">Competitor & Citation Audit</h3>
          <p className="text-slate-400 text-sm leading-relaxed">
            Discover which competitors AI assistants cite in your software category, and uncover missing citation sources hurting your brand presence.
          </p>
        </div>
      </section>
    </div>
  );
};
