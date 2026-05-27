import React from 'react';
import { Sparkles, XCircle, CheckCircle } from 'lucide-react';
import { Suggestion } from '../types';

interface SuggestionsViewProps {
  suggestions: Suggestion[];
  optScore: number;
  aiReviewing: boolean;
  handleAiReview: () => Promise<void>;
  toggleResolveSuggestion: (id: string, isNowResolved: boolean) => Promise<void>;
  dismissSuggestion: (id: string) => Promise<void>;
}

export function SuggestionsView({
  suggestions,
  optScore,
  aiReviewing,
  handleAiReview,
  toggleResolveSuggestion,
  dismissSuggestion
}: SuggestionsViewProps) {
  const unresolvedSuggestions = suggestions.filter(s => !s.resolved);

  return (
    <div className="space-y-6">
      
      {/* Top tracking health optimization header */}
      <div className="rounded-xl border border-indigo-150 bg-indigo-50/50 dark:bg-indigo-950/20 dark:border-indigo-900/40 p-6 flex flex-col md:flex-row gap-6 justify-between items-start md:items-center shadow-inner">
        <div className="space-y-1">
          <h2 className="font-bold text-slate-900 dark:text-white text-base flex items-center gap-2">
            <Sparkles className="w-5 h-5 text-indigo-600 animate-pulse" />
            System Diagnostics Scanner
          </h2>
          <p className="text-xs text-slate-655 dark:text-slate-400 max-w-2xl leading-normal">
            Our conversions diagnostics engine monitors active conversion streams. Adjust settings or verify WooCommerce parameters to optimize match rates and configurations.
          </p>
        </div>

        {/* Optimization score badge widget */}
        <div className="text-right shrink-0">
          <span className="block text-[10px] font-bold text-indigo-500 uppercase tracking-widest leading-none">Conversions Health Score</span>
          <span className="text-4xl font-extrabold text-slate-850 dark:text-white font-mono inline-block mt-1">{optScore}%</span>
          <div className="mt-1.5 h-1.5 w-24 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden ml-auto">
            <div className="h-full bg-indigo-600 rounded-full" style={{ width: `${optScore}%` }} />
          </div>
        </div>
      </div>

      {/* Live Diagnostics scan trigger CTA */}
      <div className="bg-white border border-slate-205 dark:bg-slate-900 dark:border-slate-800 p-4 rounded-xl shadow-sm flex flex-col sm:flex-row gap-4 items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-lg bg-indigo-100 dark:bg-indigo-950/40 flex items-center justify-center text-indigo-700 dark:text-indigo-400 border border-indigo-150 dark:border-indigo-900/60 shrink-0">
            <Sparkles className="w-5 h-5" />
          </div>
          <div>
            <h4 className="font-bold text-slate-800 dark:text-white text-xs uppercase tracking-wider">Run Live Diagnostics Scan</h4>
            <p className="text-xs text-slate-400 dark:text-slate-500">Initialize automated backend audit of conversions pipeline parameters, credentials, and event streams.</p>
          </div>
        </div>

        <button
          disabled={aiReviewing}
          onClick={handleAiReview}
          className="w-full sm:w-auto px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white text-xs font-bold rounded-lg transition-colors flex items-center gap-2 justify-center shadow-sm shrink-0 cursor-pointer"
        >
          {aiReviewing ? (
            <>
              <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
              <span>Running Diagnostics Scan...</span>
            </>
          ) : (
            <>
              <Sparkles className="w-4 h-4" />
              <span>Run Diagnostics Scan</span>
            </>
          )}
        </button>
      </div>

      {/* Suggestions lists */}
      <div className="space-y-4">
        {unresolvedSuggestions.length === 0 && (
          <div className="p-16 border dark:border-slate-800 rounded-xl bg-white dark:bg-slate-900 text-center space-y-4">
            <div className="w-12 h-12 bg-green-50 dark:bg-green-950/20 rounded-full border border-green-100 dark:border-green-900/60 flex items-center justify-center mx-auto text-green-600">
              <CheckCircle className="w-6 h-6" />
            </div>
            <div>
              <h4 className="font-bold text-slate-800 dark:text-white">Excellent! All checklist resolved</h4>
              <p className="text-xs text-slate-400 dark:text-slate-550 max-w-sm mx-auto mt-1">Telemetry payloads match Meta, TikTok, and GA4 parameters completely. Your tracking telemetry score represents flawless performance.</p>
            </div>
          </div>
        )}

        {/* Suggestions cards mapping */}
        <div className="grid grid-cols-1 gap-4">
          {suggestions.map((s) => (
            <div 
              key={s.id} 
              className={`rounded-xl border bg-white dark:bg-slate-900 p-5 shadow-sm space-y-4 transition-all ${
                s.resolved ? 'border-green-200/50 dark:border-green-900/30 opacity-60' : 
                s.severity === 'Critical' ? 'border-l-4 border-l-rose-500 border-slate-200 dark:border-slate-800' :
                s.severity === 'Warning' ? 'border-l-4 border-l-amber-500 border-slate-200 dark:border-slate-800' :
                'border-l-4 border-l-indigo-400 border-slate-200 dark:border-slate-800'
              }`}
            >
              <div className="flex justify-between items-start">
                <div>
                  <div className="flex items-center gap-2">
                    <span className={`px-2 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider ${
                      s.severity === 'Critical' ? 'bg-rose-50 text-rose-700 border border-rose-150 dark:bg-rose-950/20 dark:text-rose-400 dark:border-rose-900/60' : 
                      s.severity === 'Warning' ? 'bg-amber-50 text-amber-700 border border-amber-150 dark:bg-amber-950/20 dark:text-amber-400 dark:border-amber-900/60' : 
                      'bg-indigo-50 text-indigo-700 border border-indigo-150 dark:bg-indigo-950/20 dark:text-indigo-400 dark:border-indigo-900/60'
                    }`}>
                      {s.severity}
                    </span>
                    {s.platform && (
                      <span className="text-[10px] text-slate-400 dark:text-slate-500 font-mono font-semibold">{s.platform} module</span>
                    )}
                  </div>
                  <h4 className="font-bold text-slate-800 dark:text-white text-sm mt-1.5">{s.title}</h4>
                </div>

                <div className="flex gap-1">
                  <button 
                    onClick={() => toggleResolveSuggestion(s.id, !s.resolved)}
                    className={`px-2.5 py-1 text-xs rounded font-semibold border cursor-pointer ${
                      s.resolved 
                        ? 'bg-green-50 border-green-200 text-green-700 hover:bg-green-100 dark:bg-green-950/20 dark:border-green-900/60 dark:text-green-400' 
                        : 'bg-indigo-50 border-indigo-100 text-indigo-700 hover:bg-indigo-100 dark:bg-indigo-950/20 dark:border-indigo-900/60 dark:text-indigo-400'
                    }`}
                  >
                    {s.resolved ? '✓ Resolved' : 'Mark Fixed'}
                  </button>
                  
                  <button 
                    onClick={() => dismissSuggestion(s.id)}
                    className="p-1 text-slate-400 hover:text-slate-650 hover:bg-slate-50 dark:hover:bg-slate-800 rounded cursor-pointer"
                  >
                    <XCircle className="w-4 h-4" />
                  </button>
                </div>
              </div>

              <p className="text-xs text-slate-550 dark:text-slate-400 leading-relaxed max-w-4xl">{s.explanation}</p>

              <div className="p-3 bg-slate-50 dark:bg-slate-950 border border-slate-150 dark:border-slate-850 rounded text-xs text-slate-600 dark:text-slate-350">
                <span className="font-bold text-[10px] text-indigo-700 dark:text-indigo-400 uppercase tracking-wider block mb-1">How to fix in WordPress plugin config</span>
                <p className="whitespace-pre-line leading-relaxed">{s.fixAction}</p>
              </div>
            </div>
          ))}
        </div>
      </div>

    </div>
  );
}
