import React from 'react';
import { ChevronDown, Copy, Check } from 'lucide-react';
import { staticFAQs } from '../lib/mock-data';

interface SetupGuideViewProps {
  faqExpanded: number | null;
  setFaqExpanded: (idx: number | null) => void;
  copiedStates: Record<string, boolean>;
  handleCopy: (text: string, labelId: string) => void;
  setActivePage: (page: string) => void;
  api_key?: string;
}

export function SetupGuideView({
  faqExpanded,
  setFaqExpanded,
  copiedStates,
  handleCopy,
  setActivePage,
  api_key
}: SetupGuideViewProps) {
  const apiToken = api_key?.trim() || '';
  const hasApiToken = apiToken.length > 0;

  return (
    <div className="space-y-6">
      
      {/* 5-step onboarding guide */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:bg-slate-900 dark:border-slate-800">
        <div className="mb-6">
          <h2 className="font-bold text-slate-800 text-base uppercase tracking-wider dark:text-white">WooCommerce server Conversions API Integration Setup</h2>
          <p className="text-xs text-slate-400 dark:text-slate-550 mt-1">Deploy Conversions tracking client nodes inside your self-hosted WordPress panel in under 5 minutes.</p>
        </div>

        <div className="space-y-8 relative before:absolute before:left-4 before:top-2 before:bottom-2 before:w-0.5 before:bg-slate-100 dark:before:bg-slate-800">
          
          {/* Step 1: Install Plugin */}
          <div className="flex gap-4 relative">
            <div className="w-8.5 h-8.5 rounded-full bg-indigo-100 dark:bg-indigo-950/40 border-2 border-white dark:border-slate-900 flex items-center justify-center text-xs font-bold text-indigo-700 dark:text-indigo-400 shadow-sm shrink-0">
              1
            </div>
            <div className="space-y-2 flex-1">
              <h4 className="font-bold text-slate-800 text-sm dark:text-white">Download and Install WordPress Helper Plugin</h4>
              <p className="text-xs text-slate-500 dark:text-slate-400 max-w-3xl leading-relaxed">
                Navigate to your WordPress dashboard. Click <b>Plugins &gt; Add New</b>, and perform query search for <b>"CAPI Conversions backend client"</b>. Click install, then toggle plugin configuration active.
              </p>
            </div>
          </div>

          {/* Step 2: Paste Access Token */}
          <div className="flex gap-4 relative">
            <div className="w-8.5 h-8.5 rounded-full bg-indigo-100 dark:bg-indigo-950/40 border-2 border-white dark:border-slate-900 flex items-center justify-center text-xs font-bold text-indigo-700 dark:text-indigo-400 shadow-sm shrink-0">
              2
            </div>
            <div className="space-y-2 flex-1">
              <h4 className="font-bold text-slate-800 text-sm dark:text-white">Synchronize API Access Token</h4>
              <p className="text-xs text-slate-500 dark:text-slate-400 max-w-3xl leading-relaxed">
                Paste your unique cloud token below inside the WordPress client panel bridge key fields parameters.
              </p>
              <div className="flex items-center gap-2 bg-slate-50 dark:bg-slate-950 p-2 border border-slate-200 dark:border-slate-800 rounded font-mono text-xs text-slate-800 dark:text-slate-300 max-w-md">
                <code className="truncate">{hasApiToken ? apiToken : 'Setup token unavailable'}</code>
                <button 
                  onClick={() => hasApiToken && handleCopy(apiToken, 'c_g_tkn')}
                  disabled={!hasApiToken}
                  className="text-slate-400 hover:text-slate-650 ml-auto shrink-0 cursor-pointer disabled:opacity-40 disabled:cursor-not-allowed"
                  title={hasApiToken ? "Copy setup token" : "Setup token unavailable"}
                >
                  {copiedStates['c_g_tkn'] ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>
              {!hasApiToken && (
                <p className="text-xs text-amber-700 dark:text-amber-400 max-w-3xl leading-relaxed">
                  The setup token has not loaded for this account. Refresh the portal or contact support before configuring the WordPress plugin.
                </p>
              )}
            </div>
          </div>

          {/* Step 3: Connect platforms */}
          <div className="flex gap-4 relative">
            <div className="w-8.5 h-8.5 rounded-full bg-indigo-100 dark:bg-indigo-950/40 border-2 border-white dark:border-slate-900 flex items-center justify-center text-xs font-bold text-indigo-700 dark:text-indigo-400 shadow-sm shrink-0">
              3
            </div>
            <div className="space-y-2 flex-1">
              <h4 className="font-bold text-slate-800 text-sm dark:text-white">Configure Platform parameters</h4>
              <p className="text-xs text-slate-500 dark:text-slate-400 max-w-3xl leading-relaxed">
                Navigate back to your <b className="cursor-pointer text-indigo-650 hover:underline dark:text-indigo-400" onClick={() => setActivePage('settings')}>Settings Panel</b> inside this portal. Populate Pixel keys or Measurements secrets parameters to direct flows.
              </p>
            </div>
          </div>

          {/* Step 4: Verify test trigger */}
          <div className="flex gap-4 relative">
            <div className="w-8.5 h-8.5 rounded-full bg-indigo-100 dark:bg-indigo-950/40 border-2 border-white dark:border-slate-900 flex items-center justify-center text-xs font-bold text-indigo-700 dark:text-indigo-400 shadow-sm shrink-0">
              4
            </div>
            <div className="space-y-2 flex-1">
              <h4 className="font-bold text-slate-800 text-sm dark:text-white">Verify sandbox test telemetry trace</h4>
              <p className="text-xs text-slate-500 dark:text-slate-400 max-w-3xl leading-relaxed">
                Dispatch a pilot test conversion transaction payload inside our custom campaign sandbox to ensure payload routing rules resolve successfully.
              </p>
              <button 
                onClick={() => setActivePage('campaign-builder')}
                className="px-3 py-1.5 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 border border-indigo-200/50 rounded text-xs font-semibold shrink-0 cursor-pointer dark:bg-indigo-950/20 dark:text-indigo-400 dark:border-indigo-900/60 dark:hover:bg-indigo-900/30"
              >
                Dispatched Test Sandbox
              </button>
            </div>
          </div>

          {/* Step 5: Full production go-live */}
          <div className="flex gap-4 relative">
            <div className="w-8.5 h-8.5 rounded-full bg-emerald-100 dark:bg-emerald-950/40 border-2 border-white dark:border-slate-900 flex items-center justify-center text-xs font-bold text-emerald-700 dark:text-emerald-450 shadow-sm shrink-0 animate-pulse">
              5
            </div>
            <div className="space-y-1 flex-1">
              <h4 className="font-bold text-slate-855 text-sm flex items-center gap-1.5 dark:text-white">
                Go Live & Stream Analytics
              </h4>
              <p className="text-xs text-slate-500 dark:text-slate-400 max-w-3xl leading-relaxed">
                Your server tracking bypass is operational! Telemetry pipeline charts inside your Dashboard will update as customer actions record live.
              </p>
            </div>
          </div>

        </div>
      </div>

      {/* FAQ Troubleshooting accordion list */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-4 dark:bg-slate-900 dark:border-slate-800">
        <div>
          <h3 className="font-bold text-slate-800 text-sm uppercase tracking-wide dark:text-white">Deployment FAQ & Troubleshooting</h3>
          <p className="text-xs text-slate-400 dark:text-slate-500">Technical answers for server tracking mechanics and deduplication pipelines</p>
        </div>

        <div className="space-y-3 pt-2">
          {staticFAQs.map((faq, index) => {
            const expanded = faqExpanded === index;
            return (
              <div key={index} className="rounded-lg border border-slate-150 dark:border-slate-800 overflow-hidden bg-slate-50/50 dark:bg-slate-950/20">
                <button
                  onClick={() => setFaqExpanded(expanded ? null : index)}
                  className="w-full text-left px-4 py-3 bg-white hover:bg-slate-50 text-xs font-bold text-slate-700 dark:text-slate-300 dark:bg-slate-900 dark:hover:bg-slate-800 flex items-center justify-between transition-colors cursor-pointer"
                >
                  <span>{faq.q}</span>
                  <ChevronDown className={`w-4 h-4 text-slate-400 transition-transform ${expanded ? 'rotate-180' : ''}`} />
                </button>
                {expanded && (
                  <div className="p-4 border-t border-slate-150 dark:border-slate-800 text-xs leading-relaxed text-slate-550 dark:text-slate-400 bg-white dark:bg-slate-900 max-w-4xl">
                    {faq.a}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </div>

    </div>
  );
}
