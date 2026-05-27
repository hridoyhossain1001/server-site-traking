import React from 'react';
import { 
  ShieldAlert, 
  AlertTriangle, 
  CheckCircle, 
  Info, 
  Check, 
  Copy 
} from 'lucide-react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  Tooltip as ReChartsTooltip, 
  ResponsiveContainer
} from 'recharts';

interface AnalyticsViewProps {
  analyticsOverview: any;
  analyticsCampaigns: any;
  signalDoctor: any;
  urlBuilderBaseUrl: string;
  setUrlBuilderBaseUrl: (url: string) => void;
  urlBuilderSource: string;
  setUrlBuilderSource: (source: string) => void;
  urlBuilderMedium: string;
  setUrlBuilderMedium: (medium: string) => void;
  urlBuilderCampaign: string;
  setUrlBuilderCampaign: (campaign: string) => void;
  urlBuilderContent: string;
  setUrlBuilderContent: (content: string) => void;
  urlBuilderTerm: string;
  setUrlBuilderTerm: (term: string) => void;
  generatedCampaignUrl: string;
  handleGenerateCampaignUrl: () => void;
  copiedStates: Record<string, boolean>;
  handleCopy: (text: string, labelId: string) => void;
}

export function AnalyticsView({
  analyticsOverview,
  analyticsCampaigns,
  signalDoctor,
  urlBuilderBaseUrl,
  setUrlBuilderBaseUrl,
  urlBuilderSource,
  setUrlBuilderSource,
  urlBuilderMedium,
  setUrlBuilderMedium,
  urlBuilderCampaign,
  setUrlBuilderCampaign,
  urlBuilderContent,
  setUrlBuilderContent,
  urlBuilderTerm,
  setUrlBuilderTerm,
  generatedCampaignUrl,
  handleGenerateCampaignUrl,
  copiedStates,
  handleCopy
}: AnalyticsViewProps) {
  return (
    <div className="space-y-6">
      
      {/* 4 Stats Cards */}
      {analyticsOverview && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
          
          {/* Card 1: Total Events */}
          <div className="rounded-3xl border border-white/60 dark:border-white/10 bg-gradient-to-br from-indigo-100/70 to-indigo-50/20 dark:from-indigo-900/30 dark:to-slate-900/40 backdrop-blur-2xl p-6 shadow-xl shadow-indigo-900/5 transition-transform hover:scale-[1.02]">
            <div className="flex items-center justify-between">
              <p className="text-xs font-bold text-indigo-800 dark:text-indigo-400 border border-indigo-300/30 bg-indigo-100/50 dark:bg-indigo-900/40 px-2 py-1 rounded-md">Total Telemetry</p>
            </div>
            <div className="mt-8 flex items-baseline gap-2">
              <p className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                {analyticsOverview.total_events?.toLocaleString() || 0}
              </p>
              <span className="text-xs font-semibold text-indigo-750/70 dark:text-indigo-300/70">Raw packets</span>
            </div>
          </div>

          {/* Card 2: Success Rate */}
          <div className="rounded-3xl border border-white/60 dark:border-white/10 bg-gradient-to-br from-emerald-100/70 to-emerald-50/20 dark:from-emerald-900/30 dark:to-slate-900/40 backdrop-blur-2xl p-6 shadow-xl shadow-emerald-900/5 transition-transform hover:scale-[1.02]">
            <div className="flex items-center justify-between">
              <p className="text-xs font-bold text-emerald-800 dark:text-emerald-400 border border-emerald-300/30 bg-emerald-100/50 dark:bg-emerald-900/40 px-2 py-1 rounded-md">Sync Rate</p>
            </div>
            <div className="mt-8 flex items-baseline gap-2">
              <p className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                {analyticsOverview.success_rate}%
              </p>
              <span className="text-xs font-semibold text-emerald-750/70 dark:text-emerald-300/70">Success</span>
            </div>
          </div>

          {/* Card 3: Avg Daily */}
          <div className="rounded-3xl border border-white/60 dark:border-white/10 bg-gradient-to-br from-purple-100/70 to-purple-50/20 dark:from-purple-900/30 dark:to-slate-900/40 backdrop-blur-2xl p-6 shadow-xl shadow-purple-900/5 transition-transform hover:scale-[1.02]">
            <div className="flex items-center justify-between">
              <p className="text-xs font-bold text-purple-800 dark:text-purple-400 border border-purple-300/30 bg-purple-100/50 dark:bg-purple-900/40 px-2 py-1 rounded-md">Daily Volume</p>
            </div>
            <div className="mt-8 flex items-baseline gap-2">
              <p className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                {analyticsOverview.avg_daily_events?.toLocaleString() || 0}
              </p>
              <span className="text-xs font-semibold text-purple-750/70 dark:text-purple-300/70">Avg daily</span>
            </div>
          </div>

          {/* Card 4: Signal Grade */}
          {signalDoctor && (
            <div className="rounded-3xl border border-white/60 dark:border-white/10 bg-gradient-to-br from-amber-100/70 to-amber-50/20 dark:from-amber-900/30 dark:to-slate-900/40 backdrop-blur-2xl p-6 shadow-xl shadow-amber-900/5 transition-transform hover:scale-[1.02]">
              <div className="flex items-center justify-between">
                <p className="text-xs font-bold text-amber-800 dark:text-amber-400 border border-amber-300/30 bg-amber-100/50 dark:bg-amber-900/40 px-2 py-1 rounded-md">Signal Doctor</p>
              </div>
              <div className="mt-8 flex items-baseline gap-2">
                <p className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
                  {signalDoctor.score}/100
                </p>
                <span className="text-xs font-semibold text-amber-750/70 dark:text-amber-300/70">{signalDoctor.grade}</span>
              </div>
            </div>
          )}

        </div>
      )}

      {/* Conversion Funnel & Signal Doctor Breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        <div className="lg:col-span-2 space-y-6">
          {/* Conversion Funnel */}
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm flex flex-col dark:bg-slate-900 dark:border-slate-800">
            <div className="mb-6">
              <h3 className="font-bold text-slate-850 text-sm uppercase tracking-wide dark:text-white">Pixel Conversion Funnel</h3>
              <p className="text-xs text-slate-400 dark:text-slate-500">Visualizing customer flow drops from first page interaction to ultimate checkout conversion.</p>
            </div>

            <div className="space-y-4">
              {analyticsOverview?.funnel ? (
                (() => {
                  const maxCount = Math.max(...analyticsOverview.funnel.map((f: any) => f.count), 1);
                  const funnelColors = ['bg-purple-500', 'bg-blue-500', 'bg-green-500', 'bg-amber-500', 'bg-emerald-500'];
                  return analyticsOverview.funnel.map((step: any, i: number) => {
                    const pctWidth = Math.max((step.count / maxCount) * 100, 5);
                    return (
                      <div key={step.step} className="space-y-1.5">
                        <div className="flex justify-between text-xs font-medium">
                          <span className="text-slate-505 flex items-center gap-1 dark:text-slate-400 font-mono">
                            {step.step}
                            {i > 0 && step.drop_off > 0 && (
                              <span className="text-rose-500 text-[10px] font-bold">
                                ↓{step.drop_off}% drop
                              </span>
                            )}
                          </span>
                          <span className="text-slate-800 font-bold dark:text-white">{step.count.toLocaleString()} events</span>
                        </div>
                        <div className="h-2.5 w-full rounded-full bg-slate-100 dark:bg-slate-800 overflow-hidden">
                          <div 
                            className={`h-full rounded-full transition-all duration-800 ${funnelColors[i % 5]}`}
                            style={{ width: `${pctWidth}%` }}
                          />
                        </div>
                      </div>
                    );
                  });
                })()
              ) : (
                <div className="py-12 text-center text-xs text-slate-400">No conversion funnel stats yet. Send test page view / checkout events.</div>
              )}
            </div>
          </div>

          {/* Telemetry Match Quality Index Bar Chart */}
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm flex flex-col dark:bg-slate-900 dark:border-slate-800">
            <div className="mb-6 flex justify-between items-center">
              <div>
                <h3 className="font-bold text-slate-850 text-sm uppercase tracking-wide dark:text-white">Telemetry Match Quality Index</h3>
                <p className="text-xs text-slate-400 dark:text-slate-500">Distribution of customer parameter matching ratios sent across active pipelines.</p>
              </div>
              {signalDoctor?.score !== undefined && (
                <div className="px-3 py-1.5 rounded-xl border border-indigo-100 bg-indigo-50/50 dark:bg-indigo-950/20 dark:border-indigo-900/40 text-right">
                  <span className="block text-[8px] font-bold text-indigo-500 uppercase tracking-widest leading-none">EMQ Score</span>
                  <span className="text-lg font-black text-slate-850 dark:text-white font-mono leading-none">{signalDoctor.score}%</span>
                </div>
              )}
            </div>

            <div className="h-64 mt-2">
              {signalDoctor?.signal_rates ? (
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart 
                    data={[
                      { name: 'Event ID', rate: signalDoctor.signal_rates.event_id || 0 },
                      { name: 'User Match', rate: signalDoctor.signal_rates.user_match || 0 },
                      { name: 'Email/Phone', rate: signalDoctor.signal_rates.email_or_phone || 0 },
                      { name: 'Click IDs', rate: signalDoctor.signal_rates.click_id || 0 },
                      { name: 'Product ID', rate: signalDoctor.signal_rates.content_ids || 0 },
                      { name: 'Order Value', rate: signalDoctor.signal_rates.value || 0 },
                      { name: 'UTM Source', rate: signalDoctor.signal_rates.utm || 0 }
                    ]} 
                    layout="vertical"
                    margin={{ top: 0, right: 20, left: 10, bottom: 0 }}
                  >
                    <XAxis type="number" domain={[0, 100]} stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} />
                    <YAxis dataKey="name" type="category" stroke="#94a3b8" fontSize={10} tickLine={false} axisLine={false} width={80} />
                    <ReChartsTooltip 
                      contentStyle={{ 
                        backgroundColor: '#0f172a', 
                        borderColor: '#1e293b', 
                        color: '#f1f5f9', 
                        borderRadius: '8px', 
                        fontSize: '11px', 
                        boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.05)' 
                      }}
                      formatter={(val) => [`${val}%`, 'Match Rate']}
                    />
                    <Bar dataKey="rate" fill="#6366f1" radius={[0, 4, 4, 0]} barSize={12} />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <div className="py-12 text-center text-xs text-slate-400">No match rate telemetry stats available yet.</div>
              )}
            </div>
          </div>
        </div>

        {/* Signal Doctor Heuristics Checklist */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm flex flex-col justify-between dark:bg-slate-900 dark:border-slate-800">
          <div>
            <h3 className="font-bold text-slate-800 text-sm uppercase tracking-wide dark:text-white">Signal Doctor Audit</h3>
            <p className="text-xs text-slate-400 dark:text-slate-500">Technical telemetry parameters checklist mapping health optimization warnings.</p>
          </div>

          <div className="mt-4 space-y-3 flex-1 overflow-y-auto max-h-96 pr-1">
            {signalDoctor?.issues ? (
              signalDoctor.issues.map((issue: any, idx: number) => (
                <div key={idx} className={`p-3 rounded-lg border text-xs flex gap-2.5 ${
                  issue.severity === 'critical' || issue.severity === 'high' ? 'bg-rose-50/50 border-rose-200 text-rose-800 dark:bg-rose-950/10 dark:border-rose-900/60 dark:text-rose-300' :
                  issue.severity === 'medium' ? 'bg-amber-50/50 border-amber-200 text-amber-800 dark:bg-amber-950/10 dark:border-amber-900/60 dark:text-amber-300' :
                  issue.severity === 'ok' ? 'bg-green-50/50 border-green-200 text-green-800 dark:bg-green-950/10 dark:border-green-900/60 dark:text-green-300' :
                  'bg-blue-50/50 border-blue-200 text-blue-800 dark:bg-blue-950/10 dark:border-blue-900/60 dark:text-blue-300'
                }`}>
                  {issue.severity === 'critical' || issue.severity === 'high' ? <ShieldAlert className="w-4 h-4 shrink-0 text-rose-500 mt-0.5" /> :
                   issue.severity === 'medium' ? <AlertTriangle className="w-4 h-4 shrink-0 text-amber-500 mt-0.5" /> :
                   <CheckCircle className="w-4 h-4 shrink-0 text-green-550 mt-0.5" />}
                  <div className="space-y-1">
                    <h4 className="font-bold text-[11px] leading-tight">{issue.title} ({issue.metric})</h4>
                    <p className="text-[10px] leading-normal opacity-90">{issue.impact}</p>
                    <p className="text-[9px] font-mono leading-normal bg-white/40 dark:bg-black/20 p-1.5 rounded border border-black/5 dark:border-white/5">{issue.fix}</p>
                  </div>
                </div>
              ))
            ) : (
              <div className="py-12 text-center text-xs text-slate-400">Diagnostic signals healthy.</div>
            )}
          </div>
        </div>

      </div>

      {/* Campaign UTM Performance Table */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm flex flex-col space-y-4 dark:bg-slate-900 dark:border-slate-800">
        <div>
          <h3 className="font-bold text-slate-850 text-sm uppercase tracking-wide dark:text-white">Marketing Campaign Performance (UTM)</h3>
          <p className="text-xs text-slate-400 dark:text-slate-500">Live source and campaign attribution statistics captured from incoming customer navigation.</p>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs text-slate-650 divide-y divide-slate-100 min-w-[700px] dark:text-slate-300 dark:divide-slate-800">
            <thead className="bg-slate-50 text-[10px] font-bold uppercase tracking-wider text-slate-555 dark:bg-slate-950 dark:text-slate-400">
              <tr>
                <th className="px-6 py-3">Source Channel</th>
                <th className="px-6 py-3">Campaign Identifier</th>
                <th className="px-6 py-3">Content View</th>
                <th className="px-6 py-3">Add to Cart</th>
                <th className="px-6 py-3">Initiated Checkout</th>
                <th className="px-6 py-3">Purchases</th>
                <th className="px-6 py-3 text-right">Attributed Revenue</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {!analyticsCampaigns?.campaigns || analyticsCampaigns.campaigns.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400 font-medium dark:text-slate-550">
                    No UTM campaign details captured yet. Use the Campaign URL Builder below to setup ad tracking parameters.
                  </td>
                </tr>
              ) : (
                analyticsCampaigns.campaigns.map((row: any, idx: number) => (
                  <tr key={idx} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40 transition-colors">
                    <td className="px-6 py-3.5 font-bold text-indigo-750 dark:text-indigo-400">{row.source}</td>
                    <td className="px-6 py-3.5 font-mono text-slate-800 dark:text-slate-100">{row.campaign}</td>
                    <td className="px-6 py-3.5 font-semibold">{row.view_content.toLocaleString()}</td>
                    <td className="px-6 py-3.5 font-semibold">{row.add_to_cart.toLocaleString()}</td>
                    <td className="px-6 py-3.5 font-semibold">{row.initiate_checkout.toLocaleString()}</td>
                    <td className="px-6 py-3.5 font-bold text-slate-850 dark:text-white">{row.purchase.toLocaleString()}</td>
                    <td className="px-6 py-3.5 font-bold text-indigo-650 dark:text-indigo-400 text-right">৳{row.revenue.toLocaleString()}</td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Campaign URL Builder widget */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm flex flex-col space-y-4 dark:bg-slate-900 dark:border-slate-800">
        <div>
          <h3 className="font-bold text-slate-850 text-sm uppercase tracking-wide dark:text-white">Campaign URL Builder</h3>
          <p className="text-xs text-slate-400 dark:text-slate-500">Generate clean campaign destination links embedded with standard tracking UTMs to maintain accurate marketing performance reporting.</p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-2">
          
          {/* Input parameters Form */}
          <div className="space-y-4">
            
            {/* Base Website URL */}
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">Base Website URL</label>
              <input 
                type="text" 
                placeholder="https://your-domain.com/shop/item"
                value={urlBuilderBaseUrl}
                onChange={(e) => setUrlBuilderBaseUrl(e.target.value)}
                className="w-full p-2.5 text-xs text-slate-800 placeholder-slate-450 bg-slate-50 border border-slate-200 rounded-lg outline-none focus:ring-1 focus:ring-indigo-500 font-mono dark:bg-slate-950 dark:border-slate-800 dark:text-white"
              />
            </div>

            {/* Source & Medium grid */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">Campaign Source</label>
                <select 
                  value={urlBuilderSource}
                  onChange={(e) => {
                    setUrlBuilderSource(e.target.value);
                    if (e.target.value === 'facebook') setUrlBuilderMedium('paid_social');
                    else if (e.target.value === 'tiktok') setUrlBuilderMedium('paid_social');
                    else if (e.target.value === 'google') setUrlBuilderMedium('cpc');
                    else setUrlBuilderMedium('referral');
                  }}
                  className="w-full p-2.5 text-xs text-slate-800 bg-slate-50 border border-slate-200 rounded-lg outline-none focus:ring-1 focus:ring-indigo-500 dark:bg-slate-950 dark:border-slate-800 dark:text-white"
                >
                  <option value="facebook">Facebook Ads</option>
                  <option value="tiktok">TikTok Ads</option>
                  <option value="google">Google CPC</option>
                  <option value="newsletter">Email Newsletter</option>
                  <option value="custom">Custom Partner</option>
                </select>
              </div>
              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">Campaign Medium</label>
                <input 
                  type="text" 
                  placeholder="paid_social"
                  value={urlBuilderMedium}
                  onChange={(e) => setUrlBuilderMedium(e.target.value)}
                  className="w-full p-2.5 text-xs text-slate-800 placeholder-slate-450 bg-slate-50 border border-slate-200 rounded-lg outline-none focus:ring-1 focus:ring-indigo-500 dark:bg-slate-950 dark:border-slate-800 dark:text-white"
                />
              </div>
            </div>

            {/* Campaign Name */}
            <div>
              <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">Campaign Name</label>
              <input 
                type="text" 
                placeholder="eid_sale_promotion"
                value={urlBuilderCampaign}
                onChange={(e) => setUrlBuilderCampaign(e.target.value)}
                className="w-full p-2.5 text-xs text-slate-800 placeholder-slate-450 bg-slate-50 border border-slate-200 rounded-lg outline-none focus:ring-1 focus:ring-indigo-500 dark:bg-slate-950 dark:border-slate-800 dark:text-white"
              />
            </div>

            {/* Optional parameters Content & Term */}
            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">Ad Content (Optional)</label>
                <input 
                  type="text" 
                  placeholder="video_ad_1"
                  value={urlBuilderContent}
                  onChange={(e) => setUrlBuilderContent(e.target.value)}
                  className="w-full p-2.5 text-xs text-slate-800 placeholder-slate-450 bg-slate-50 border border-slate-200 rounded-lg outline-none focus:ring-1 focus:ring-indigo-500 dark:bg-slate-950 dark:border-slate-800 dark:text-white"
                />
              </div>
              <div>
                <label className="block text-[11px] font-bold uppercase tracking-wider text-slate-500 mb-1.5">Search Term (Optional)</label>
                <input 
                  type="text" 
                  placeholder="buy_shoes"
                  value={urlBuilderTerm}
                  onChange={(e) => setUrlBuilderTerm(e.target.value)}
                  className="w-full p-2.5 text-xs text-slate-800 placeholder-slate-450 bg-slate-50 border border-slate-200 rounded-lg outline-none focus:ring-1 focus:ring-indigo-500 dark:bg-slate-950 dark:border-slate-800 dark:text-white"
                />
              </div>
            </div>

            <button 
              onClick={handleGenerateCampaignUrl}
              className="px-4 py-2 bg-indigo-650 hover:bg-indigo-700 text-white text-xs font-bold rounded-lg transition-colors cursor-pointer dark:bg-indigo-600 dark:hover:bg-indigo-700"
            >
              Generate Campaign URL
            </button>

          </div>

          {/* Output generator result box */}
          <div className="rounded-xl bg-slate-50 border border-slate-200 p-5 flex flex-col justify-between dark:bg-slate-950 dark:border-slate-800">
            <div className="space-y-3">
              <h4 className="text-xs font-bold text-slate-700 uppercase tracking-widest dark:text-slate-350">Attributed URL Result</h4>
              <p className="text-[11px] text-slate-400 dark:text-slate-500">Copy the compiled destination URL below and paste it as the target landing page inside Facebook Ads Manager or TikTok Campaign Editor.</p>
            </div>

            <div className="my-4 bg-white border border-slate-200 rounded-lg p-3 text-xs font-mono text-slate-700 break-all select-all dark:bg-slate-900 dark:border-slate-800 dark:text-slate-200 relative group min-h-24 flex items-center">
              {generatedCampaignUrl ? (
                <>
                  {generatedCampaignUrl}
                  <button 
                    onClick={() => handleCopy(generatedCampaignUrl, 'generated_campaign_url')}
                    className="absolute top-2 right-2 p-1.5 rounded bg-slate-100 hover:bg-slate-200 text-slate-650 cursor-pointer dark:bg-slate-800 dark:hover:bg-slate-700 dark:text-slate-300"
                    title="Copy URL"
                  >
                    {copiedStates['generated_campaign_url'] ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
                  </button>
                </>
              ) : (
                <span className="text-slate-400 italic">Attributed UTM campaign URL will display here...</span>
              )}
            </div>

            <div className="text-[10px] text-slate-400 leading-normal flex items-start gap-1.5 dark:text-slate-550">
              <Info className="w-3.5 h-3.5 shrink-0 text-slate-350 mt-0.5" />
              <span>Applying proper UTM discipline ensures tracking data cleanly attributes purchase value directly to campaigns.</span>
            </div>
          </div>

        </div>
      </div>

    </div>
  );
}
