import React from 'react';
import { 
  Search, 
  Download, 
  RotateCcw, 
  ListChecks, 
  Check, 
  Copy,
  AlertTriangle,
  Loader2
} from 'lucide-react';
import { CAPIEvent, OutboxItem } from '../types';

// Helper function to safely escape regular expressions
function escapeRegExp(str: string): string {
  return str.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Helper to highlight matched keywords in search results
function highlightText(text: string | number | undefined | null, search: string): React.ReactNode {
  if (text === undefined || text === null) return '';
  const textStr = String(text);
  if (!search || !search.trim()) return textStr;

  try {
    const escapedSearch = escapeRegExp(search.trim());
    const regex = new RegExp(`(${escapedSearch})`, 'gi');
    const parts = textStr.split(regex);
    
    return (
      <>
        {parts.map((part, index) => 
          regex.test(part) ? (
            <mark key={index} className="bg-amber-100 dark:bg-amber-900/50 text-amber-900 dark:text-amber-250 p-0.5 rounded">{part}</mark>
          ) : (
            part
          )
        )}
      </>
    );
  } catch (error) {
    return textStr;
  }
}

interface EventLogsViewProps {
  filteredEventsForTable: CAPIEvent[];
  searchFilter: string;
  setSearchFilter: (v: string) => void;
  liveMode: boolean;
  setLiveMode: (v: boolean) => void;
  platformFilters: string[];
  setPlatformFilters: React.Dispatch<React.SetStateAction<string[]>>;
  statusFilters: string[];
  setStatusFilters: React.Dispatch<React.SetStateAction<string[]>>;
  setSearchVal: (v: string) => void;
  expandedEventId: string | null;
  setExpandedEventId: (id: string | null) => void;
  copiedStates: Record<string, boolean>;
  handleCopy: (text: string, labelId: string) => void;
  handleExportData: (format: 'csv' | 'json', type: 'events' | 'apilogs') => void;
  outboxItems: OutboxItem[];
  retryingOutboxIds: number[];
  handleRetryOutbox: (id: number) => void;
}

export function EventLogsView({
  filteredEventsForTable,
  searchFilter,
  setSearchFilter,
  liveMode,
  setLiveMode,
  platformFilters,
  setPlatformFilters,
  statusFilters,
  setStatusFilters,
  setSearchVal,
  expandedEventId,
  setExpandedEventId,
  copiedStates,
  handleCopy,
  handleExportData,
  outboxItems,
  retryingOutboxIds,
  handleRetryOutbox
}: EventLogsViewProps) {
  const failedOutboxItems = outboxItems.filter(item => item.status === 'dead' || item.status === 'queued' || item.status === 'processing');

  return (
    <div className="space-y-6">
      {failedOutboxItems.length > 0 && (
        <div className="rounded-xl border border-amber-200 bg-amber-50/60 shadow-sm overflow-hidden dark:bg-amber-950/10 dark:border-amber-900/60">
          <div className="px-4 sm:px-5 py-3 border-b border-amber-200/70 dark:border-amber-900/60 flex items-center justify-between gap-3">
            <div className="flex items-center gap-2 min-w-0">
              <AlertTriangle className="w-4 h-4 text-amber-600 dark:text-amber-400 shrink-0" />
              <div className="min-w-0">
                <h3 className="text-xs font-bold uppercase tracking-widest text-amber-900 dark:text-amber-250">Failed outbox recovery</h3>
                <p className="text-[11px] text-amber-800/70 dark:text-amber-300/70 truncate">{failedOutboxItems.length} delivery job{failedOutboxItems.length === 1 ? '' : 's'} need attention</p>
              </div>
            </div>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs min-w-[820px]">
              <thead className="text-[10px] font-bold uppercase tracking-wider text-amber-900/70 dark:text-amber-250/70">
                <tr>
                  <th className="px-5 py-2.5">Job</th>
                  <th className="px-5 py-2.5">Events</th>
                  <th className="px-5 py-2.5">Status</th>
                  <th className="px-5 py-2.5">Attempts</th>
                  <th className="px-5 py-2.5">Last Error</th>
                  <th className="px-5 py-2.5 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-amber-200/70 dark:divide-amber-900/60 bg-white/60 dark:bg-slate-950/30">
                {failedOutboxItems.map(item => {
                  const retrying = retryingOutboxIds.includes(item.id);
                  const canRetry = item.status !== 'processing' && item.status !== 'sent';
                  return (
                    <tr key={item.id}>
                      <td className="px-5 py-3 font-mono text-amber-950 dark:text-amber-100">
                        #{item.id}<br />
                        <span className="text-[9px] text-amber-800/60 dark:text-amber-300/60">{new Date(item.createdAt).toLocaleString()}</span>
                      </td>
                      <td className="px-5 py-3 text-amber-950 dark:text-amber-100">
                        <span className="font-semibold">{item.eventNames.join(', ')}</span><br />
                        <span className="text-[10px] text-amber-800/60 dark:text-amber-300/60">{item.eventCount} event{item.eventCount === 1 ? '' : 's'}</span>
                      </td>
                      <td className="px-5 py-3">
                        <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider border ${
                          item.status === 'dead' ? 'bg-rose-50 text-rose-700 border-rose-150 dark:bg-rose-950/20 dark:text-rose-400 dark:border-rose-900/60' :
                          item.status === 'processing' ? 'bg-indigo-50 text-indigo-700 border-indigo-150 dark:bg-indigo-950/20 dark:text-indigo-350 dark:border-indigo-900/60' :
                          'bg-amber-100 text-amber-800 border-amber-200 dark:bg-amber-950/30 dark:text-amber-300 dark:border-amber-900/60'
                        }`}>
                          {item.status}
                        </span>
                      </td>
                      <td className="px-5 py-3 font-mono text-amber-950 dark:text-amber-100">{item.attempts}/{item.maxAttempts}</td>
                      <td className="px-5 py-3 text-amber-950 dark:text-amber-100 max-w-xs">
                        <span className="block max-h-9 overflow-hidden">{item.lastError || (item.nextAttemptAt ? `Next attempt ${new Date(item.nextAttemptAt).toLocaleString()}` : 'Waiting in queue')}</span>
                      </td>
                      <td className="px-5 py-3 text-right">
                        <button
                          onClick={() => handleRetryOutbox(item.id)}
                          disabled={!canRetry || retrying}
                          className={`inline-flex items-center justify-center gap-1.5 px-3 py-1.5 rounded-lg text-[11px] font-bold border transition-colors ${
                            canRetry && !retrying
                              ? 'bg-amber-600 text-white border-amber-600 hover:bg-amber-700'
                              : 'bg-slate-100 text-slate-400 border-slate-200 cursor-not-allowed dark:bg-slate-900 dark:border-slate-800'
                          }`}
                        >
                          {retrying ? <Loader2 className="w-3.5 h-3.5 animate-spin" /> : <RotateCcw className="w-3.5 h-3.5" />}
                          Retry Now
                        </button>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </div>
      )}
      
      {/* Search & filters controls panel */}
      <div className="rounded-xl border border-slate-200 bg-white p-4 sm:p-5 shadow-sm space-y-4 dark:bg-slate-900 dark:border-slate-800">
        <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between">
          <div className="relative w-full lg:max-w-md">
            <input 
              type="text" 
              placeholder="Filter by keyword, event name or payload..."
              value={searchFilter}
              onChange={(e) => setSearchFilter(e.target.value)}
              className="w-full py-2 pl-9 pr-4 text-xs text-slate-800 placeholder-slate-400 bg-slate-50 border border-slate-200 rounded-lg outline-none focus:border-indigo-500 font-mono dark:bg-slate-950 dark:border-slate-800 dark:text-white"
            />
            <Search className="absolute w-4 h-4 text-slate-400 left-3 top-2.5" />
          </div>

          <div className="flex items-center gap-3 w-full lg:w-auto shrink-0 justify-start lg:justify-end flex-wrap">
            
            {/* Live Mode Toggle control */}
            <button 
              onClick={() => setLiveMode(!liveMode)}
              className={`flex items-center gap-2 px-3 py-2 text-xs font-semibold rounded-lg border transition-all cursor-pointer ${
                liveMode 
                  ? 'bg-rose-50 text-rose-700 border-rose-200 focus:ring-1 focus:ring-rose-500/20 dark:bg-rose-950/20 dark:text-rose-400 dark:border-rose-900/60' 
                  : 'bg-white text-slate-600 border-slate-200 hover:bg-slate-50 dark:bg-slate-900 dark:border-slate-800 dark:text-slate-300 dark:hover:bg-slate-800'
              }`}
            >
              <span className={`w-2 h-2 rounded-full shrink-0 ${liveMode ? 'bg-rose-600 pulse-dot' : 'bg-slate-400'}`} />
              <span className="whitespace-nowrap">{liveMode ? 'Live Mode Active' : 'Enable Live Mode'}</span>
            </button>

            {/* Export triggers */}
            <div className="flex items-center rounded-lg border border-slate-200 bg-white overflow-hidden shrink-0 dark:bg-slate-900 dark:border-slate-800">
              <button 
                onClick={() => handleExportData('json', 'events')} 
                className="px-3 py-1.5 text-[11px] text-slate-650 hover:bg-slate-50 border-r border-slate-200 dark:border-slate-800 flex items-center gap-1.5 font-medium cursor-pointer dark:text-slate-300 dark:hover:bg-slate-800"
              >
                <Download className="w-3.5 h-3.5 text-slate-400" />
                JSON
              </button>
              <button 
                onClick={() => handleExportData('csv', 'events')} 
                className="px-3 py-1.5 text-[11px] text-slate-650 hover:bg-slate-50 flex items-center gap-1.5 font-medium cursor-pointer dark:text-slate-300 dark:hover:bg-slate-800"
              >
                CSV
              </button>
            </div>
          </div>
        </div>

        {/* Multi-select filter pills */}
        <div className="flex flex-wrap gap-2 pt-3 border-t border-slate-100 dark:border-slate-800 items-center">
          <span className="text-[10px] text-slate-400 font-bold uppercase tracking-widest mr-2 shrink-0">Filters:</span>
          
          {/* Platforms lists */}
          {['Meta CAPI', 'TikTok Events API', 'GA4'].map(p => {
            const active = platformFilters.includes(p);
            return (
              <button
                key={p}
                onClick={() => {
                  setPlatformFilters(prev => active ? prev.filter(x => x !== p) : [...prev, p]);
                }}
                className={`px-2.5 py-1 rounded-full text-xs font-medium cursor-pointer border transition-colors ${
                  active 
                    ? 'bg-indigo-600 border-indigo-600 text-white dark:bg-indigo-600 dark:border-indigo-600' 
                    : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50 dark:bg-slate-900 dark:border-slate-850 dark:text-slate-300 dark:hover:bg-slate-800'
                }`}
              >
                {p}
              </button>
            );
          })}

          <span className="h-4 w-px bg-slate-200 dark:bg-slate-800 mx-2 self-center" />

          {/* Status lists */}
          {['Success', 'Failed', 'Retry'].map(s => {
            const active = statusFilters.includes(s);
            return (
              <button
                key={s}
                onClick={() => {
                  setStatusFilters(prev => active ? prev.filter(x => x !== s) : [...prev, s]);
                }}
                className={`px-2.5 py-1 rounded-full text-xs font-medium cursor-pointer border transition-colors ${
                  active 
                    ? 'bg-indigo-600 border-indigo-600 text-white dark:bg-indigo-600 dark:border-indigo-600' 
                    : 'bg-white border-slate-200 text-slate-600 hover:bg-slate-50 dark:bg-slate-900 dark:border-slate-850 dark:text-slate-300 dark:hover:bg-slate-800'
                }`}
              >
                {s}
              </button>
            );
          })}

          {/* Reset conditions */}
          {(platformFilters.length > 0 || statusFilters.length > 0 || searchFilter) && (
            <button 
              onClick={() => {
                setPlatformFilters([]);
                setStatusFilters([]);
                setSearchFilter('');
                setSearchVal('');
              }}
              className="text-indigo-650 hover:text-indigo-800 text-[11px] font-bold flex items-center gap-1 ml-auto shrink-0 self-center dark:text-indigo-400 dark:hover:text-indigo-350"
            >
              <RotateCcw className="w-3 h-3" />
              Clear Filter
            </button>
          )}
        </div>
      </div>

      {/* Big full-width searchable logs list */}
      <div className="rounded-xl border border-slate-200 bg-white shadow-sm overflow-hidden flex flex-col dark:bg-slate-900 dark:border-slate-800">
        <div className="p-4 bg-slate-50/50 border-b border-slate-100 dark:bg-slate-950 dark:border-slate-800 flex justify-between items-center text-xs">
          <span className="font-semibold text-slate-500 dark:text-slate-400">{filteredEventsForTable.length} events matching query parameters</span>
          <span className="text-[10px] text-slate-400 dark:text-slate-500">Showing last 100 historical queries</span>
        </div>

        {filteredEventsForTable.length === 0 ? (
          <div className="p-16 text-center space-y-4">
            <div className="w-12 h-12 rounded-full bg-slate-50 dark:bg-slate-950 border border-slate-200 dark:border-slate-800 flex items-center justify-center mx-auto text-slate-450">
              <ListChecks className="w-6 h-6 text-slate-300" />
            </div>
            <div>
              <h4 className="font-bold text-slate-700 dark:text-white">No events found</h4>
              <p className="text-xs text-slate-400 dark:text-slate-500 max-w-sm mx-auto mt-1">Try relaxing filters or change search queries keywords to display telemetry records.</p>
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto overflow-y-auto max-h-[calc(100vh-280px)] min-h-[400px]">
            <table className="w-full text-left text-xs text-slate-660 divide-y divide-slate-100 dark:text-slate-300 dark:divide-slate-800 min-w-[900px]">
              <thead className="bg-slate-50 dark:bg-slate-950 text-[10px] font-bold uppercase tracking-wider text-slate-555 dark:text-slate-400 sticky top-0 z-10">
                <tr>
                  <th className="px-6 py-3">Timestamp / Age</th>
                  <th className="px-6 py-3">Event ID</th>
                  <th className="px-6 py-3">Event Name</th>
                  <th className="px-6 py-3">Platform Stream</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3">Code</th>
                  <th className="px-6 py-3 text-right">Deduplication Key</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {filteredEventsForTable.map(e => {
                  const isExpanded = expandedEventId === e.id;
                  return (
                    <React.Fragment key={e.id}>
                      <tr 
                        onClick={() => setExpandedEventId(isExpanded ? null : e.id)}
                        className="hover:bg-indigo-50/20 dark:hover:bg-slate-800/40 cursor-pointer transition-colors"
                      >
                        <td className="px-6 py-4 font-mono text-slate-500 dark:text-slate-450">
                          {new Date(e.timestamp).toLocaleTimeString()}<br/>
                          <span className="text-[9px] text-slate-400 dark:text-slate-500">
                            {new Date(e.timestamp).toLocaleDateString()}
                          </span>
                        </td>
                        <td className="px-6 py-4 font-mono font-bold text-indigo-650 dark:text-indigo-400">
                          {highlightText(e.id, searchFilter)}
                        </td>
                        <td className="px-6 py-4 font-semibold text-slate-800 dark:text-slate-100">
                          {highlightText(e.name, searchFilter)}
                        </td>
                        <td className="px-6 py-4">
                          <span className="flex items-center gap-1.5 font-medium text-slate-700 dark:text-slate-300">
                            <span className={`w-1.5 h-1.5 rounded-full ${
                              e.platform === 'Meta CAPI' ? 'bg-indigo-500' : 
                              e.platform === 'TikTok Events API' ? 'bg-cyan-500' : 'bg-orange-500'
                            }`} />
                            {highlightText(e.platform, searchFilter)}
                          </span>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wider ${
                            e.status === 'Success' ? 'bg-green-50 text-green-700 border border-green-150 dark:bg-green-950/20 dark:text-green-400 dark:border-green-900/60' :
                            e.status === 'Retry' ? 'bg-amber-50 text-amber-700 border border-amber-150 dark:bg-amber-950/20 dark:text-amber-400 dark:border-amber-900/60' : 
                            'bg-rose-50 text-rose-700 border border-rose-150 dark:bg-rose-950/20 dark:text-rose-400 dark:border-rose-900/60'
                          }`}>
                            {highlightText(e.status, searchFilter)}
                          </span>
                        </td>
                        <td className="px-6 py-4 font-mono text-slate-550 dark:text-slate-400">
                          {highlightText(String(e.httpCode), searchFilter)}
                        </td>
                        <td className="px-6 py-4 font-mono text-right text-slate-400 dark:text-slate-500">
                          {highlightText(e.deduplicationKey, searchFilter)}
                        </td>
                      </tr>

                      {isExpanded && (
                        <tr>
                          <td colSpan={7} className="bg-slate-50 dark:bg-slate-950 border-t border-slate-100 dark:border-slate-800 px-6 py-4">
                            {/* Expanded Panel Structure */}
                            <div className="space-y-4">
                              <div className="flex justify-between items-center">
                                <h5 className="font-bold text-xs text-slate-700 dark:text-slate-300 uppercase tracking-widest">Metadata payload raw analyzer</h5>
                                <span className="text-[10px] text-slate-400 dark:text-slate-500 font-mono">Deduplication: {highlightText(e.deduplicationKey, searchFilter)}</span>
                              </div>

                              <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
                                
                                {/* Req details */}
                                <div className="bg-slate-900 leading-relaxed text-slate-200 text-[11px] font-mono p-4 rounded-lg overflow-auto max-h-80 relative group lg:col-span-2">
                                  <div className="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                                    <button 
                                      onClick={(el) => { el.stopPropagation(); handleCopy(JSON.stringify(e.payload, null, 2), `evt_payload_${e.id}`) }}
                                      className="p-1 rounded bg-slate-800 text-slate-400 hover:text-white"
                                    >
                                      {copiedStates[`evt_payload_${e.id}`] ? <Check className="w-3 h-3 text-emerald-450" /> : <Copy className="w-3 h-3" />}
                                    </button>
                                  </div>
                                  <p className="text-[10px] font-bold text-indigo-400 uppercase tracking-wider mb-2">Payload JSON parameters stream</p>
                                  <pre className="whitespace-pre-wrap break-all">{highlightText(JSON.stringify(e.payload, null, 2), searchFilter)}</pre>
                                </div>

                                {/* Headers / Response */}
                                <div className="space-y-4">
                                  <div className="bg-slate-900 leading-relaxed text-slate-250 text-[11px] font-mono p-4 rounded-lg overflow-auto max-h-40 relative group">
                                    <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider mb-2">Relay Client headers</p>
                                    <pre className="whitespace-pre-wrap break-all">{highlightText(JSON.stringify(e.headers, null, 2), searchFilter)}</pre>
                                  </div>

                                  <div className="bg-slate-900 leading-relaxed text-slate-255 text-[11px] font-mono p-4 rounded-lg overflow-auto max-h-40 relative group">
                                    <p className="text-[10px] font-bold text-emerald-400 uppercase tracking-wider mb-2">Raw upstream Response</p>
                                    <pre className="whitespace-pre-wrap break-all">{highlightText(JSON.stringify(e.responseBody, null, 2), searchFilter)}</pre>
                                  </div>
                                </div>

                              </div>
                            </div>
                          </td>
                        </tr>
                      )}
                    </React.Fragment>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
