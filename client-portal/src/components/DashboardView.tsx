import React from 'react';
import { 
  AreaChart, 
  Area, 
  CartesianGrid, 
  XAxis, 
  YAxis, 
  Tooltip as ReChartsTooltip, 
  Legend, 
  ResponsiveContainer 
} from 'recharts';
import { 
  TrendingUp, 
  ArrowUpRight, 
  Check, 
  Copy, 
  CheckCircle2, 
  ListChecks,
  AlertTriangle
} from 'lucide-react';
import { CAPIEvent, UserProfile, Platform } from '../types';

interface DashboardViewProps {
  profile: UserProfile;
  events: CAPIEvent[];
  trendData: any[];
  metaStats: { total: number; rate: number; lastTime: string };
  tiktokStats: { total: number; rate: number; lastTime: string };
  ga4Stats: { total: number; rate: number; lastTime: string };
  optScore: number;
  resolvedCount: number;
  totalSuggCount: number;
  setActivePage: (p: string) => void;
  isDarkMode: boolean;
  expandedEventId: string | null;
  setExpandedEventId: (id: string | null) => void;
  copiedStates: Record<string, boolean>;
  handleCopy: (text: string, labelId: string) => void;
}

export function DashboardView({
  profile,
  events,
  trendData,
  metaStats,
  tiktokStats,
  ga4Stats,
  optScore,
  resolvedCount,
  totalSuggCount,
  setActivePage,
  isDarkMode,
  expandedEventId,
  setExpandedEventId,
  copiedStates,
  handleCopy
}: DashboardViewProps) {
  return (
    <>
      {/* 4 KPI Top metrics grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        
        {/* Event quota metrics card */}
        <div className="rounded-3xl border border-white/60 dark:border-white/10 bg-gradient-to-br from-emerald-200/50 to-emerald-50/20 dark:from-emerald-900/30 dark:to-slate-900/40 backdrop-blur-2xl p-6 shadow-xl shadow-emerald-900/5 transition-transform hover:scale-[1.02]">
          <div className="flex items-center justify-between">
            <p className="text-xs font-bold text-emerald-800 dark:text-emerald-400 border border-emerald-300/30 bg-emerald-100/50 dark:bg-emerald-900/40 px-2 py-1 rounded-md">Management</p>
            <span className="text-xs font-semibold text-emerald-700 dark:text-emerald-300 flex items-center gap-0.5 font-mono bg-white/40 dark:bg-black/20 px-2 py-0.5 rounded-full backdrop-blur-md">
              <TrendingUp className="w-3.5 h-3.5" />
              {profile.eventsQuota > 0 ? Math.round((profile.eventsUsed / profile.eventsQuota) * 100) : 0}%
            </span>
          </div>
          <div className="mt-8 flex items-baseline gap-2">
            <p className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              {profile.eventsUsed.toLocaleString()}
            </p>
            <span className="text-xs font-semibold text-emerald-700/70 dark:text-emerald-300/70">/ {profile.eventsQuota.toLocaleString()}</span>
          </div>

          <div className="mt-4 opacity-70 mix-blend-multiply dark:mix-blend-screen">
            <div className="h-1.5 w-full rounded-full bg-emerald-100/50 overflow-hidden backdrop-blur-lg">
              <div 
                className="h-full rounded-full transition-all duration-500 bg-emerald-500"
                style={{ width: `${profile.eventsQuota > 0 ? (profile.eventsUsed / profile.eventsQuota) * 100 : 0}%` }}
              />
            </div>
          </div>
        </div>

        {/* Meta Stat mini platform card */}
        <div className="rounded-3xl border border-white/60 dark:border-white/10 bg-gradient-to-br from-orange-100/70 to-orange-50/10 dark:from-orange-900/30 dark:to-slate-900/40 backdrop-blur-2xl p-6 shadow-xl shadow-orange-900/5 transition-transform hover:scale-[1.02]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 border border-orange-300/30 bg-orange-100/50 dark:bg-orange-900/40 px-2.5 py-1 rounded-md">
              <div className="w-2 h-2 rounded-full bg-orange-500 shadow-[0_0_8px_rgba(249,115,22,0.8)] pulse-dot" />
              <p className="text-[11px] font-bold text-orange-800 dark:text-orange-400">Marketing</p>
            </div>
          </div>
          <div className="mt-8 flex items-baseline justify-between">
            <p className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">{metaStats.rate}%</p>
            <span className="text-[10px] text-orange-800 dark:text-orange-200 bg-white/40 dark:bg-black/20 backdrop-blur px-2.5 py-1 rounded-full font-mono font-bold tracking-widest">{metaStats.total} CALLS</span>
          </div>
          <p className="mt-4 text-[10px] text-orange-700/70 dark:text-orange-200/50 font-mono">Last stream: {metaStats.lastTime}</p>
        </div>

        {/* TikTok Stat mini platform card */}
        <div className="rounded-3xl border border-white/60 dark:border-white/10 bg-gradient-to-br from-indigo-100/70 to-indigo-50/20 dark:from-indigo-900/30 dark:to-slate-900/40 backdrop-blur-2xl p-6 shadow-xl shadow-indigo-900/5 transition-transform hover:scale-[1.02]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 border border-indigo-300/30 bg-indigo-100/50 dark:bg-indigo-900/40 px-2.5 py-1 rounded-md">
              <div className="w-2 h-2 rounded-full bg-indigo-500 shadow-[0_0_8px_rgba(99,102,241,0.8)] pulse-dot" />
              <p className="text-[11px] font-bold text-indigo-800 dark:text-indigo-400">Data Analytics</p>
            </div>
          </div>
          <div className="mt-8 flex items-baseline justify-between">
            <p className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">{tiktokStats.rate}%</p>
            <span className="text-[10px] text-indigo-800 dark:text-indigo-200 bg-white/40 dark:bg-black/20 backdrop-blur px-2.5 py-1 rounded-full font-mono font-bold tracking-widest">{tiktokStats.total} CALLS</span>
          </div>
          <p className="mt-4 text-[10px] text-indigo-700/70 dark:text-indigo-200/50 font-mono">Last stream: {tiktokStats.lastTime}</p>
        </div>

        {/* Google Analytics 4 mini platform card */}
        <div className="rounded-3xl border border-white/60 dark:border-white/10 bg-gradient-to-br from-purple-100/70 to-purple-50/20 dark:from-purple-900/30 dark:to-slate-900/40 backdrop-blur-2xl p-6 shadow-xl shadow-purple-900/5 transition-transform hover:scale-[1.02]">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 border border-purple-300/30 bg-purple-100/50 dark:bg-purple-900/40 px-2.5 py-1 rounded-md">
              <div className="w-2 h-2 rounded-full bg-purple-500 shadow-[0_0_8px_rgba(168,85,247,0.8)] pulse-dot" />
              <p className="text-[11px] font-bold text-purple-800 dark:text-purple-400">CRM Automation</p>
            </div>
          </div>
          <div className="mt-8 flex items-baseline justify-between">
            <p className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">{ga4Stats.rate}%</p>
            <span className="text-[10px] text-purple-800 dark:text-purple-200 bg-white/40 dark:bg-black/20 backdrop-blur px-2.5 py-1 rounded-full font-mono font-bold tracking-widest">{ga4Stats.total} CALLS</span>
          </div>
          <p className="mt-4 text-[10px] text-purple-700/70 dark:text-purple-200/50 font-mono">Last stream: {ga4Stats.lastTime}</p>
        </div>
      </div>

      {/* Main visualization split section (Trend chart & Deduplication index) */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Event Volume charts */}
        <div className="col-span-2 rounded-xl border border-slate-200 bg-white p-6 shadow-sm flex flex-col dark:bg-slate-900 dark:border-slate-800">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h2 className="font-bold text-slate-800 text-sm uppercase tracking-wide dark:text-white">Event Transmission Volume</h2>
              <p className="text-xs text-slate-400 dark:text-slate-500">Total transited telemetry packages grouped by chronological trace</p>
            </div>
            <div className="flex items-center gap-2 text-xs text-slate-400 font-mono bg-slate-50 dark:bg-slate-950 px-2.5 py-1 rounded border border-slate-150 dark:border-slate-800">
              <span className="w-1.5 h-1.5 bg-indigo-500 rounded-full" />
              Live Synced
            </div>
          </div>

          <div className="h-64 mt-auto">
            <ResponsiveContainer width="100%" height="100%" minWidth={1} minHeight={1}>
              <AreaChart data={trendData} margin={{ top: 10, right: 10, left: -25, bottom: 0 }}>
                <defs>
                  <linearGradient id="metaGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#4f46e5" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#4f46e5" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="tiktokGrad" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#06b6d4" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#06b6d4" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={isDarkMode ? '#1e293b' : '#f1f5f9'} />
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} />
                <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} />
                <ReChartsTooltip 
                  contentStyle={{ backgroundColor: isDarkMode ? '#0f172a' : '#ffffff', borderColor: isDarkMode ? '#1e293b' : '#e2e8f0', color: isDarkMode ? '#f1f5f9' : '#1e293b', borderRadius: '8px', fontSize: '11px', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.05)' }} 
                />
                <Legend wrapperStyle={{ fontSize: '10px', paddingTop: '10px' }} />
                <Area type="monotone" dataKey="Meta CAPI" stroke="#4f46e5" strokeWidth={2} fillOpacity={1} fill="url(#metaGrad)" />
                <Area type="monotone" dataKey="TikTok Events" stroke="#06b6d4" strokeWidth={2} fillOpacity={1} fill="url(#tiktokGrad)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Deduplication & optimization indicator */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm flex flex-col justify-between dark:bg-slate-900 dark:border-slate-800">
          <div>
            <h2 className="font-bold text-slate-800 text-sm uppercase tracking-wide dark:text-white">Optimization Audit</h2>
            <p className="text-xs text-slate-400 dark:text-slate-500 leading-normal mt-1">
              Deduplication pairing and parameter validation schema health score
            </p>
          </div>

          <div className="flex flex-col items-center justify-center py-6">
            <div className="relative h-32 w-32">
              {/* Circular progress represent */}
              <svg className="h-full w-full rotate-[-90deg]" viewBox="0 0 36 36">
                <circle className="stroke-slate-100 dark:stroke-slate-800" strokeWidth="4" fill="transparent" r="16" cx="18" cy="18" />
                <circle 
                  className="stroke-indigo-600 transition-all duration-1000" 
                  strokeWidth="4" 
                  strokeDasharray={`${optScore} 100`} 
                  strokeLinecap="round" 
                  fill="transparent" 
                  r="16" 
                  cx="18" 
                  cy="18" 
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="text-3xl font-extrabold text-slate-800 dark:text-white font-mono leading-none">{optScore}%</span>
                <span className="text-[10px] text-slate-400 mt-1 font-semibold uppercase tracking-wider">Health Map</span>
              </div>
            </div>
            
            <div className="mt-4 text-center">
              <p className="text-xs text-slate-500 dark:text-slate-400 max-w-xs leading-normal">
                {resolvedCount} of {totalSuggCount} campaign parameter diagnostics resolved. {totalSuggCount - resolvedCount} issues pending.
              </p>
            </div>
          </div>

          <button 
            onClick={() => setActivePage('suggestions')}
            className="w-full py-2 bg-indigo-50 hover:bg-indigo-100 text-indigo-700 text-xs font-semibold rounded-lg transition-colors border border-indigo-100 dark:bg-indigo-950/20 dark:text-indigo-400 dark:border-indigo-900/60 dark:hover:bg-indigo-900/30"
          >
            Audit Recommendations
          </button>
        </div>
      </div>

      {/* Bottom Recent Activity table section */}
      <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden dark:bg-slate-900 dark:border-slate-800">
        <div className="flex items-center justify-between border-b border-slate-100 dark:border-slate-800 px-6 py-4">
          <div>
            <h2 className="font-bold text-slate-800 text-sm uppercase tracking-wider dark:text-white">Recent Activity Pipeline</h2>
            <p className="text-xs text-slate-400 dark:text-slate-500">Chronological telemetry events from WordPress. Click a row to expand JSON payload.</p>
          </div>
          <button 
            onClick={() => setActivePage('event-logs')}
            className="text-xs font-semibold text-indigo-600 hover:underline flex items-center gap-1 dark:text-indigo-400"
          >
            View complete logs <ArrowUpRight className="w-3.5 h-3.5" />
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-600 dark:text-slate-350 divide-y divide-slate-100 dark:divide-slate-800 min-w-[800px]">
            <thead className="bg-slate-50 dark:bg-slate-950 text-[10px] font-bold uppercase tracking-wider text-slate-550 dark:text-slate-400">
              <tr>
                <th className="px-6 py-3">Timestamp</th>
                <th className="px-6 py-3">Event Name</th>
                <th className="px-6 py-3">API Platform</th>
                <th className="px-6 py-3">Log Status</th>
                <th className="px-6 py-3">Service Code</th>
                <th className="px-6 py-3 text-right">Deduplication Key</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {events.length === 0 ? (
                <tr>
                  <td colSpan={6} className="px-6 py-8 text-center text-slate-400 font-medium">
                    <ListChecks className="w-8 h-8 mx-auto text-slate-300 mb-2" />
                    No events captured yet.
                  </td>
                </tr>
              ) : (
                events.slice(0, 5).map(e => {
                  const isExpanded = expandedEventId === e.id;
                  return (
                    <React.Fragment key={e.id}>
                      <tr 
                        onClick={() => setExpandedEventId(isExpanded ? null : e.id)}
                        className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40 cursor-pointer transition-colors"
                      >
                        <td className="px-6 py-3.5 font-mono text-slate-450 dark:text-slate-500">
                          {new Date(e.timestamp).toLocaleTimeString()}
                        </td>
                        <td className="px-6 py-3.5 font-semibold text-slate-800 dark:text-slate-100">
                          {e.name}
                        </td>
                        <td className="px-6 py-3.5">
                          <span className="flex items-center gap-1.5 font-medium text-slate-700 dark:text-slate-300">
                            <span className={`w-1.5 h-1.5 rounded-full ${
                              e.platform === 'Meta CAPI' ? 'bg-indigo-500' : 
                              e.platform === 'TikTok Events API' ? 'bg-cyan-500' : 'bg-orange-500'
                            }`} />
                            {e.platform}
                          </span>
                        </td>
                        <td className="px-6 py-3.5">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                            e.status === 'Success' ? 'bg-green-50 text-green-700 border border-green-150 dark:bg-green-950/20 dark:text-green-400 dark:border-green-900/60' :
                            e.status === 'Retry' ? 'bg-amber-50 text-amber-700 border border-amber-150 dark:bg-amber-950/20 dark:text-amber-400 dark:border-amber-900/60' : 
                            'bg-rose-50 text-rose-700 border border-rose-150 dark:bg-rose-950/20 dark:text-rose-400 dark:border-rose-900/60'
                          }`}>
                            {e.status}
                          </span>
                        </td>
                        <td className="px-6 py-3.5 font-mono font-medium text-slate-500 dark:text-slate-400">
                          {e.httpCode}
                        </td>
                        <td className="px-6 py-3.5 font-mono text-right text-slate-450 dark:text-slate-500">
                          {e.deduplicationKey}
                        </td>
                      </tr>

                      {/* Collapsible raw JSON details */}
                      {isExpanded && (
                        <tr>
                          <td colSpan={6} className="bg-slate-50 dark:bg-slate-950 border-t border-slate-100 dark:border-slate-800 px-6 py-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div className="bg-slate-900 text-slate-200 text-[11px] font-mono p-4 rounded-lg overflow-auto max-h-60 relative group">
                                <div className="absolute top-2 right-2 flex gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                                  <button 
                                    onClick={(el) => { el.stopPropagation(); handleCopy(JSON.stringify(e.payload, null, 2), `c_det_p_${e.id}`) }}
                                    className="p-1 rounded bg-slate-800 text-slate-400 hover:text-white"
                                    title="Copy Payload"
                                  >
                                    {copiedStates[`c_det_p_${e.id}`] ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                                  </button>
                                </div>
                                <p className="text-[10px] font-semibold text-indigo-400 uppercase tracking-widest mb-1 select-none">Client request payload context</p>
                                <pre>{JSON.stringify(e.payload, null, 2)}</pre>
                              </div>

                              <div className="bg-slate-900 text-slate-200 text-[11px] font-mono p-4 rounded-lg overflow-auto max-h-60 relative group">
                                <div className="absolute top-2 right-2 flex gap-1.5 opacity-0 group-hover:opacity-100 transition-opacity">
                                  <button 
                                    onClick={(el) => { el.stopPropagation(); handleCopy(JSON.stringify(e.responseBody, null, 2), `c_det_r_${e.id}`) }}
                                    className="p-1 rounded bg-slate-800 text-slate-400 hover:text-white"
                                    title="Copy Response body"
                                  >
                                    {copiedStates[`c_det_r_${e.id}`] ? <Check className="w-3 h-3 text-emerald-400" /> : <Copy className="w-3 h-3" />}
                                  </button>
                                </div>
                                <p className="text-[10px] font-semibold text-emerald-400 uppercase tracking-widest mb-1 select-none">Target platform return header parameters</p>
                                <pre>{JSON.stringify(e.responseBody, null, 2)}</pre>
                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })
              )}
            </tbody>
          </table>
        </div>
      </div>
    </>
  );
}
