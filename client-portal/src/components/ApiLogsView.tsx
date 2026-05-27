import React from 'react';
import { 
  BarChart as ReChartsBarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip as ReChartsTooltip, 
  ResponsiveContainer 
} from 'recharts';
import { Download, AlertTriangle } from 'lucide-react';
import { APILog } from '../types';

interface ApiLogsViewProps {
  filteredApiLogsForTable: APILog[];
  apiLogs: APILog[];
  expandedApiLogId: string | null;
  setExpandedApiLogId: (id: string | null) => void;
  isDarkMode: boolean;
  handleExportData: (format: 'csv' | 'json', type: 'events' | 'apilogs') => void;
}

export function ApiLogsView({
  filteredApiLogsForTable,
  apiLogs,
  expandedApiLogId,
  setExpandedApiLogId,
  isDarkMode,
  handleExportData
}: ApiLogsViewProps) {
  
  // API Latency Graph distribution
  const getLatencyChartData = () => {
    return apiLogs.slice(0, 15).reverse().map((l, index) => ({
      name: `#${index + 1}`,
      'Latency (ms)': l.latencyMs,
      'Status': l.statusCode === 200 ? 'Success' : 'Error'
    }));
  };

  return (
    <div className="space-y-6">

      {/* Top analytic graph measuring latency rates over time */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:bg-slate-900 dark:border-slate-800">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h3 className="font-bold text-slate-800 text-sm uppercase tracking-wide dark:text-white">Interface latency analysis</h3>
            <p className="text-xs text-slate-400 dark:text-slate-500">Upstream connection telemetry latency parameters in milliseconds</p>
          </div>
          <div className="text-xs text-slate-500 font-mono dark:text-slate-400">
            Avg Latency: <span className="font-bold text-indigo-650 dark:text-indigo-400">142ms</span>
          </div>
        </div>

        <div className="h-32">
          <ResponsiveContainer width="100%" height="100%" minWidth={1} minHeight={1}>
            <ReChartsBarChart data={getLatencyChartData()} margin={{ top: 10, right: 10, left: -30, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={isDarkMode ? '#1e293b' : '#f1f5f9'} />
              <XAxis dataKey="name" stroke="#94a3b8" fontSize={9} tickLine={false} />
              <YAxis stroke="#94a3b8" fontSize={9} tickLine={false} unit="ms" />
              <ReChartsTooltip contentStyle={{ fontSize: '10px', borderRadius: '6px', backgroundColor: isDarkMode ? '#0f172a' : '#ffffff', borderColor: isDarkMode ? '#1e293b' : '#e2e8f0', color: isDarkMode ? '#f1f5f9' : '#1e293b' }} />
              <Bar dataKey="Latency (ms)" fill="#4f46e5" radius={[4, 4, 0, 0]} barSize={12} />
            </ReChartsBarChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Sub controls & export bar */}
      <div className="flex justify-between items-center">
        <h4 className="font-bold text-slate-800 text-xs uppercase tracking-widest text-slate-500 dark:text-slate-400">Raw Endpoint Interface API logs</h4>
        
        <div className="flex items-center gap-2">
          <button 
            onClick={() => handleExportData('json', 'apilogs')}
            className="px-2.5 py-1 text-xs font-semibold rounded bg-white text-slate-600 border border-slate-200 hover:bg-slate-50 flex items-center gap-1.5 cursor-pointer dark:bg-slate-900 dark:border-slate-800 dark:text-slate-300 dark:hover:bg-slate-800"
          >
            <Download className="w-3.5 h-3.5" /> Export logs dump
          </button>
        </div>
      </div>

      {/* Outbound logs table */}
      <div className="rounded-xl border border-slate-205 bg-white shadow-sm overflow-hidden dark:bg-slate-900 dark:border-slate-800">
        <div className="overflow-x-auto overflow-y-auto max-h-[calc(100vh-320px)] min-h-[300px]">
          <table className="w-full text-left text-xs divide-y divide-slate-100 dark:divide-slate-800 min-w-[850px]">
            <thead className="bg-slate-50 dark:bg-slate-950 text-[10px] font-bold uppercase tracking-wider text-slate-500 dark:text-slate-400 sticky top-0 z-10">
              <tr>
                <th className="px-6 py-3">Timestamp</th>
                <th className="px-6 py-3">Platform</th>
                <th className="px-6 py-3">Target Endpoint url</th>
                <th className="px-6 py-3">Method</th>
                <th className="px-6 py-3">Status code</th>
                <th className="px-6 py-3">Latency</th>
                <th className="px-6 py-3 text-right">Retries</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {filteredApiLogsForTable.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-slate-400 font-medium">
                    No outbound logs generated.
                  </td>
                </tr>
              ) : (
                filteredApiLogsForTable.slice(0, 40).map(l => {
                  const isExpanded = expandedApiLogId === l.id;
                  const hasErr = l.statusCode >= 400;
                  const hasRetry = l.retryCount > 0;

                  return (
                    <React.Fragment key={l.id}>
                      <tr 
                        onClick={() => setExpandedApiLogId(isExpanded ? null : l.id)}
                        className={`hover:bg-slate-50/50 dark:hover:bg-slate-800/40 cursor-pointer transition-colors ${
                          hasErr ? 'border-l-4 border-l-rose-500 pl-5' : 
                          hasRetry ? 'border-l-4 border-l-amber-500 pl-5' : ''
                        }`}
                      >
                        <td className="px-6 py-3.5 font-mono text-slate-400 dark:text-slate-500">
                          {new Date(l.timestamp).toLocaleTimeString()}
                        </td>
                        <td className="px-6 py-3.5 font-medium text-slate-800 dark:text-slate-100">
                          {l.platform}
                        </td>
                        <td className="px-6 py-3.5 font-mono text-xs max-w-xs truncate text-slate-500 dark:text-slate-400" title={l.endpoint}>
                          {l.endpoint}
                        </td>
                        <td className="px-6 py-3.5">
                          <span className="px-1.5 py-0.5 rounded text-[10px] bg-slate-100 text-slate-700 font-mono font-semibold dark:bg-slate-950 dark:text-slate-300">
                            {l.method}
                          </span>
                        </td>
                        <td className="px-6 py-3.5">
                          <span className={`inline-flex items-center gap-1 font-mono font-bold ${
                            hasErr ? 'text-rose-600' : 'text-emerald-600'
                          }`}>
                            {hasErr ? <AlertTriangle className="w-3.5 h-3.5 shrink-0" /> : null}
                            {l.statusCode}
                          </span>
                        </td>
                        <td className="px-6 py-3.5 font-mono text-slate-500 dark:text-slate-400">
                          {l.latencyMs}ms
                        </td>
                        <td className="px-6 py-3.5 text-right font-mono font-medium">
                          {l.retryCount > 0 ? (
                            <span className="text-amber-600 font-bold bg-amber-50 px-1.5 py-0.5 rounded border border-amber-100 whitespace-nowrap dark:bg-amber-950/20 dark:border-amber-900/60 dark:text-amber-400">
                              {l.retryCount} retried
                            </span>
                          ) : (
                            <span className="text-slate-400">0</span>
                          )}
                        </td>
                      </tr>

                      {isExpanded && (
                        <tr>
                          <td colSpan={7} className="bg-slate-50 dark:bg-slate-950 border-t border-slate-100 dark:border-slate-800 px-6 py-4">
                            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                              <div className="bg-slate-900 text-slate-200 text-[11px] font-mono p-4 rounded-lg overflow-auto max-h-60">
                                <p className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider mb-2">Outgoing Payload JSON</p>
                                <pre className="whitespace-pre-wrap break-all">{l.requestBody}</pre>
                              </div>

                              <div className="bg-slate-900 text-slate-250 text-[11px] font-mono p-4 rounded-lg overflow-auto max-h-60">
                                <p className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider mb-2">Gateways response payload</p>
                                <pre className="whitespace-pre-wrap break-all">{l.responseBody}</pre>
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

    </div>
  );
}
