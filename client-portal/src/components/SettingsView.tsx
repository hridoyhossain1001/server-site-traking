import React, { useState, useEffect } from 'react';
import { Copy, Check } from 'lucide-react';
import { Platform, PlatformConfig, EventRule, ClientConnection } from '../types';

interface SettingsViewProps {
  credentials: Record<Platform, PlatformConfig>;
  connection: ClientConnection;
  rules: EventRule[];
  handleUpdatePlatform: (platform: Platform, fields: Partial<PlatformConfig>) => Promise<void>;
  handleToggleRule: (index: number, channel: 'metaEnabled' | 'tiktokEnabled' | 'ga4Enabled') => Promise<void>;
  refreshWPHeartbeat: () => Promise<void>;
  copiedStates: Record<string, boolean>;
  handleCopy: (text: string, labelId: string) => void;
  showToast: (msg: string, isErr?: boolean) => void;
}

export function SettingsView({
  credentials,
  connection,
  rules,
  handleUpdatePlatform,
  handleToggleRule,
  refreshWPHeartbeat,
  copiedStates,
  handleCopy,
  showToast
}: SettingsViewProps) {
  // Local state for inputs to prevent key-stroke POST spamming
  const [localPixelIds, setLocalPixelIds] = useState<Record<Platform, string>>({
    'Meta CAPI': '',
    'TikTok Events API': '',
    'GA4': ''
  });
  const [localTokens, setLocalTokens] = useState<Record<Platform, string>>({
    'Meta CAPI': '',
    'TikTok Events API': '',
    'GA4': ''
  });
  const [localTestCodes, setLocalTestCodes] = useState<Record<Platform, string>>({
    'Meta CAPI': '',
    'TikTok Events API': '',
    'GA4': ''
  });

  // Sync with credentials prop when it loads/updates
  useEffect(() => {
    if (credentials) {
      setLocalPixelIds({
        'Meta CAPI': credentials['Meta CAPI']?.pixelIdOrMeasurementId || '',
        'TikTok Events API': credentials['TikTok Events API']?.pixelIdOrMeasurementId || '',
        'GA4': credentials['GA4']?.pixelIdOrMeasurementId || ''
      });
      setLocalTokens({
        'Meta CAPI': credentials['Meta CAPI']?.accessToken || '',
        'TikTok Events API': credentials['TikTok Events API']?.accessToken || '',
        'GA4': credentials['GA4']?.accessToken || ''
      });
      setLocalTestCodes({
        'Meta CAPI': credentials['Meta CAPI']?.testEventCode || '',
        'TikTok Events API': credentials['TikTok Events API']?.testEventCode || '',
        'GA4': credentials['GA4']?.testEventCode || ''
      });
    }
  }, [credentials]);

  // Courier Settings States
  const [courierSettings, setCourierSettings] = useState<any>({
    pathao_api_key: '',
    pathao_secret_key: '',
    pathao_store_id: '',
    steadfast_api_key: '',
    steadfast_secret_key: '',
    courier_auto_send: false,
    default_courier: 'steadfast'
  });
  const [loadingCourier, setLoadingCourier] = useState<boolean>(true);
  const [savingCourier, setSavingCourier] = useState<boolean>(false);

  useEffect(() => {
    const fetchCourierSettings = async () => {
      try {
        const res = await fetch('/api/courier/settings');
        if (res.ok) {
          const data = await res.json();
          setCourierSettings(data);
        }
      } catch (err) {
        console.error("Failed to load courier settings", err);
      } finally {
        setLoadingCourier(false);
      }
    };
    fetchCourierSettings();
  }, []);

  const handleSaveCourierSettings = async (e: React.FormEvent) => {
    e.preventDefault();
    setSavingCourier(true);
    try {
      const res = await fetch('/api/courier/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(courierSettings)
      });
      if (res.ok) {
        showToast("Courier settings updated successfully.", false);
      } else {
        const errData = await res.json();
        showToast(errData.detail || "Failed to update courier settings.", true);
      }
    } catch (err) {
      showToast("Error updating courier settings.", true);
    } finally {
      setSavingCourier(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      
      {/* Fixed controls sidebar settings tabs */}
      <div className="space-y-6 lg:col-span-2">
        
        {/* Pipeline credentials card */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-6 dark:bg-slate-900 dark:border-slate-800">
          <div>
            <h3 className="font-bold text-slate-800 text-sm uppercase tracking-wide dark:text-white">Platform Credential Keys</h3>
            <p className="text-xs text-slate-400 dark:text-slate-500">Manage API keys, tracking pixel ids and webhook tokens per target platform router</p>
          </div>

          {Object.keys(credentials).map(platKey => {
            const plat = platKey as Platform;
            const config = credentials[plat];
            return (
              <div key={plat} className="p-4 rounded-lg border border-slate-150 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/20 space-y-3">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <span className="font-semibold text-xs text-slate-800 dark:text-white uppercase tracking-wider">{plat} Route</span>
                    <span className={`inline-flex px-1.5 py-0.5 rounded text-[9px] font-bold uppercase tracking-wider ${
                      config.status === 'Valid' ? 'bg-emerald-50 text-emerald-700 border border-emerald-150 dark:bg-emerald-950/20 dark:text-emerald-400 dark:border-emerald-900/60' : 
                      config.status === 'Invalid' ? 'bg-rose-50 text-rose-700 border border-rose-150 dark:bg-rose-950/20 dark:text-rose-400 dark:border-rose-900/60' : 
                      'bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-400'
                    }`}>
                      {config.status}
                    </span>
                  </div>

                  {/* Enable platform toggle switch */}
                  <label className="relative inline-flex items-center cursor-pointer select-none">
                    <input 
                      type="checkbox" 
                      checked={config.enabled}
                      onChange={(e) => handleUpdatePlatform(plat, { enabled: e.target.checked })} 
                      className="sr-only peer"
                    />
                    <div className="w-9 h-5 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-indigo-600" />
                    <span className="ml-2 text-[10px] font-semibold text-slate-500 uppercase dark:text-slate-400">
                      {config.enabled ? 'On' : 'Off'}
                    </span>
                  </label>
                </div>

                <div className={`grid grid-cols-1 ${plat === 'GA4' ? 'md:grid-cols-2' : 'md:grid-cols-3'} gap-4`}>
                  <div>
                    <label className="block text-[10px] font-semibold text-slate-450 uppercase mb-1">Pixel ID / Measurement ID</label>
                    <input 
                      type="text"
                      value={localPixelIds[plat]}
                      placeholder="e.g. 782049182390"
                      onChange={(e) => setLocalPixelIds(prev => ({ ...prev, [plat]: e.target.value }))}
                      onBlur={() => handleUpdatePlatform(plat, { pixelIdOrMeasurementId: localPixelIds[plat] })}
                      onKeyDown={(e) => { if (e.key === 'Enter') e.currentTarget.blur(); }}
                      className="w-full p-2 text-xs bg-white border border-slate-205 rounded font-mono text-slate-800 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:bg-slate-900 dark:border-slate-800 dark:text-white"
                    />
                  </div>
                  
                  <div>
                    <label className="block text-[10px] font-semibold text-slate-455 uppercase mb-1">CAPI Access secret Token</label>
                    <input 
                      type="password"
                      value={localTokens[plat]}
                      placeholder="************************"
                      onChange={(e) => setLocalTokens(prev => ({ ...prev, [plat]: e.target.value }))}
                      onBlur={() => handleUpdatePlatform(plat, { accessToken: localTokens[plat] })}
                      onKeyDown={(e) => { if (e.key === 'Enter') e.currentTarget.blur(); }}
                      className="w-full p-2 text-xs bg-white border border-slate-205 rounded font-mono text-slate-800 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:bg-slate-900 dark:border-slate-800 dark:text-white"
                    />
                  </div>

                  {plat !== 'GA4' && (
                    <div>
                      <label className="block text-[10px] font-semibold text-slate-455 uppercase mb-1">Test Event Code (Optional)</label>
                      <input 
                        type="text"
                        value={localTestCodes[plat]}
                        placeholder="e.g. TEST12345"
                        onChange={(e) => setLocalTestCodes(prev => ({ ...prev, [plat]: e.target.value }))}
                        onBlur={() => handleUpdatePlatform(plat, { testEventCode: localTestCodes[plat] })}
                        onKeyDown={(e) => { if (e.key === 'Enter') e.currentTarget.blur(); }}
                        className="w-full p-2 text-xs bg-white border border-slate-205 rounded font-mono text-slate-800 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:bg-slate-900 dark:border-slate-800 dark:text-white"
                      />
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>

        {/* Courier Settings Panel */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-6 dark:bg-slate-900 dark:border-slate-800">
          <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
            <div>
              <h3 className="font-bold text-slate-800 text-sm uppercase tracking-wide dark:text-white">Courier Integration Credentials</h3>
              <p className="text-xs text-slate-400 dark:text-slate-500">Configure API credentials and settings for Pathao & SteadFast courier APIs</p>
            </div>
            
            {/* Auto send toggle */}
            <div className="flex items-center gap-4">
              <label className="relative inline-flex items-center cursor-pointer select-none">
                <input 
                  type="checkbox" 
                  checked={courierSettings.courier_auto_send}
                  onChange={(e) => setCourierSettings((prev: any) => ({ ...prev, courier_auto_send: e.target.checked }))} 
                  className="sr-only peer"
                />
                <div className="w-9 h-5 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-indigo-600" />
                <span className="ml-2 text-[10px] font-semibold text-slate-500 uppercase dark:text-slate-400">
                  Auto-Book Courier: {courierSettings.courier_auto_send ? 'On' : 'Off'}
                </span>
              </label>
            </div>
          </div>

          {loadingCourier ? (
            <div className="flex items-center justify-center py-6 text-slate-400 gap-2">
              <span className="animate-spin h-4 w-4 border-2 border-indigo-500 border-t-transparent rounded-full" />
              <span>Loading configurations...</span>
            </div>
          ) : (
            <form onSubmit={handleSaveCourierSettings} className="space-y-6">
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* SteadFast section */}
                <div className="p-4 rounded-lg border border-slate-150 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/20 space-y-4">
                  <h4 className="font-bold text-xs text-indigo-650 dark:text-indigo-400 uppercase tracking-wider pb-2 border-b border-slate-100 dark:border-slate-850">
                    SteadFast Courier API
                  </h4>
                  
                  <div>
                    <label className="block text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">SteadFast API Key</label>
                    <input 
                      type="text"
                      value={courierSettings.steadfast_api_key || ''}
                      onChange={(e) => setCourierSettings((prev: any) => ({ ...prev, steadfast_api_key: e.target.value }))}
                      placeholder="Enter SteadFast Api-Key"
                      className="w-full p-2 text-xs bg-white border border-slate-205 rounded font-mono text-slate-800 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:bg-slate-900 dark:border-slate-800 dark:text-white"
                    />
                  </div>

                  <div>
                    <label className="block text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">SteadFast Secret Key</label>
                    <input 
                      type="password"
                      value={courierSettings.steadfast_secret_key || ''}
                      onChange={(e) => setCourierSettings((prev: any) => ({ ...prev, steadfast_secret_key: e.target.value }))}
                      placeholder="************************"
                      className="w-full p-2 text-xs bg-white border border-slate-205 rounded font-mono text-slate-800 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:bg-slate-900 dark:border-slate-800 dark:text-white"
                    />
                  </div>
                </div>

                {/* Pathao section */}
                <div className="p-4 rounded-lg border border-slate-150 dark:border-slate-800 bg-slate-50/50 dark:bg-slate-950/20 space-y-4">
                  <h4 className="font-bold text-xs text-indigo-650 dark:text-indigo-400 uppercase tracking-wider pb-2 border-b border-slate-100 dark:border-slate-850">
                    Pathao Courier API
                  </h4>
                  
                  <div>
                    <label className="block text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">
                      Pathao Client ID | Store Owner Email
                    </label>
                    <input 
                      type="text"
                      value={courierSettings.pathao_api_key || ''}
                      onChange={(e) => setCourierSettings((prev: any) => ({ ...prev, pathao_api_key: e.target.value }))}
                      placeholder="client_id|email"
                      className="w-full p-2 text-xs bg-white border border-slate-205 rounded font-mono text-slate-800 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:bg-slate-900 dark:border-slate-800 dark:text-white"
                    />
                  </div>

                  <div>
                    <label className="block text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">
                      Pathao Client Secret | Store Password
                    </label>
                    <input 
                      type="password"
                      value={courierSettings.pathao_secret_key || ''}
                      onChange={(e) => setCourierSettings((prev: any) => ({ ...prev, pathao_secret_key: e.target.value }))}
                      placeholder="************************"
                      className="w-full p-2 text-xs bg-white border border-slate-205 rounded font-mono text-slate-800 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:bg-slate-900 dark:border-slate-800 dark:text-white"
                    />
                  </div>

                  <div>
                    <label className="block text-[10px] font-semibold text-slate-500 dark:text-slate-400 uppercase mb-1">Pathao Store ID</label>
                    <input 
                      type="text"
                      value={courierSettings.pathao_store_id || ''}
                      onChange={(e) => setCourierSettings((prev: any) => ({ ...prev, pathao_store_id: e.target.value }))}
                      placeholder="Store ID"
                      className="w-full p-2 text-xs bg-white border border-slate-205 rounded font-mono text-slate-800 focus:outline-none focus:ring-1 focus:ring-indigo-500 dark:bg-slate-900 dark:border-slate-800 dark:text-white"
                    />
                  </div>
                </div>
              </div>

              {/* General courier choices */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1.5">Default Courier Provider</label>
                  <select 
                    value={courierSettings.default_courier || 'steadfast'}
                    onChange={(e) => setCourierSettings((prev: any) => ({ ...prev, default_courier: e.target.value }))}
                    className="w-full p-2 text-xs bg-white border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 dark:bg-slate-900 dark:border-slate-800 dark:text-white cursor-pointer"
                  >
                    <option value="steadfast">SteadFast Courier</option>
                    <option value="pathao">Pathao Courier</option>
                  </select>
                </div>
                
                <div className="flex items-end">
                  <button
                    type="submit"
                    disabled={savingCourier}
                    className="w-full py-2.5 bg-gradient-to-r from-indigo-650 to-violet-650 hover:from-indigo-750 hover:to-violet-750 disabled:opacity-50 text-white text-xs font-bold rounded-lg shadow-md transition-all cursor-pointer text-center"
                  >
                    {savingCourier ? 'Updating settings...' : 'Save Courier Settings'}
                  </button>
                </div>
              </div>

            </form>
          )}
        </div>

        {/* WordPress Custom tracking rules */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-4 dark:bg-slate-900 dark:border-slate-800">
          <div>
            <h3 className="font-bold text-slate-800 text-sm uppercase tracking-wide dark:text-white">WordPress event routing rules</h3>
            <p className="text-xs text-slate-400 dark:text-slate-500">Select which native WooCommerce triggers relay to each marketing platform database</p>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full text-xs text-slate-600 text-left min-w-[650px] dark:text-slate-300">
              <thead className="bg-slate-50 text-[10px] font-bold uppercase tracking-wider text-slate-555 border-b border-slate-100 dark:bg-slate-950 dark:border-slate-800 dark:text-slate-400">
                <tr>
                  <th className="px-4 py-3">WooCommerce Trigger Name</th>
                  <th className="px-4 py-3 text-center">Meta CAPI</th>
                  <th className="px-4 py-3 text-center">TikTok tracking</th>
                  <th className="px-4 py-3 text-center">GA4 Measurement</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
                {rules.map((rule, idx) => (
                  <tr key={idx} className="hover:bg-slate-50/50 dark:hover:bg-slate-800/40">
                    <td className="px-4 py-3.5 font-semibold text-slate-850 dark:text-white font-mono text-xs">{rule.eventName}</td>
                    
                    <td className="px-4 py-3.5 text-center">
                      <input 
                        type="checkbox" 
                        checked={rule.metaEnabled}
                        onChange={() => handleToggleRule(idx, 'metaEnabled')}
                        className="w-4 h-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer" 
                      />
                    </td>
                    
                    <td className="px-4 py-3.5 text-center">
                      <input 
                        type="checkbox" 
                        checked={rule.tiktokEnabled}
                        onChange={() => handleToggleRule(idx, 'tiktokEnabled')}
                        className="w-4 h-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer" 
                      />
                    </td>

                    <td className="px-4 py-3.5 text-center">
                      <input 
                        type="checkbox" 
                        checked={rule.ga4Enabled}
                        onChange={() => handleToggleRule(idx, 'ga4Enabled')}
                        className="w-4 h-4 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer" 
                      />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      {/* Left side parameters / WordPress connection */}
      <div className="space-y-6">
        
        {/* WordPress token health status */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-4 dark:bg-slate-900 dark:border-slate-800">
          <div>
            <h3 className="font-bold text-slate-800 text-sm uppercase tracking-wide dark:text-white">WordPress plugin bridge</h3>
            <p className="text-xs text-slate-400 dark:text-slate-500">Credentials bridge utilized by WooCommerce server webhook plugins</p>
          </div>

          <div className="p-4 rounded-lg bg-slate-50 border border-slate-150 dark:bg-slate-950 dark:border-slate-850 space-y-3 font-mono text-xs text-slate-700 dark:text-slate-305">
            <div>
              <span className="block text-[9px] font-semibold text-slate-455 dark:text-slate-500 uppercase tracking-wider mb-0.5">REST API Access key token</span>
              <div className="flex items-center gap-2 bg-white dark:bg-slate-900 px-2 py-1.5 rounded border border-slate-200 dark:border-slate-800">
                <span className="truncate select-all">{connection.api_key || connection.token}</span>
                <button 
                  onClick={() => handleCopy(connection.api_key || connection.token, 'sett_wp_tok')}
                  className="text-slate-400 hover:text-slate-655 ml-auto shrink-0 cursor-pointer"
                  title="Copy Access token"
                >
                  {copiedStates['sett_wp_tok'] ? <Check className="w-3.5 h-3.5 text-emerald-500" /> : <Copy className="w-3.5 h-3.5" />}
                </button>
              </div>
            </div>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-[10px]">
              <div>
                <span className="block text-[9px] text-slate-400 dark:text-slate-500 uppercase mb-0.5">Plugin detected version</span>
                <span className="font-semibold text-slate-850 dark:text-white">v{connection.wpVersion}</span>
              </div>
              <div>
                <span className="block text-[9px] text-slate-400 dark:text-slate-500 uppercase mb-0.5">Last query heartbeat</span>
                <span className="font-semibold text-slate-850 dark:text-white">{new Date(connection.lastHeartbeat).toLocaleTimeString()}</span>
              </div>
            </div>
          </div>

          <button 
            onClick={() => {
              showToast("Pinging WordPress plugin...", false);
              refreshWPHeartbeat()
                .then(() => showToast("WordPress synchronization active.", false))
                .catch(() => showToast("Failed payload ping parameters.", true));
            }}
            className="w-full py-2 bg-indigo-650 hover:bg-indigo-700 text-white text-xs font-semibold rounded-lg transition-colors border border-indigo-700/20 cursor-pointer dark:bg-indigo-600 dark:hover:bg-indigo-750"
          >
            Test Connection Heartbeat
          </button>
        </div>

        {/* Threshold trigger alerts setting */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm space-y-4 dark:bg-slate-900 dark:border-slate-800">
          <div>
            <h3 className="font-bold text-slate-800 text-sm uppercase tracking-wide dark:text-white">Threshold warnings</h3>
            <p className="text-xs text-slate-400 dark:text-slate-500 leading-normal">Transmit alert metrics emails when account telemetry consumption levels peak</p>
          </div>

          <div className="space-y-4">
            <div>
              <label className="block text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-2">Threshold Limits Alert</label>
              <div className="space-y-2">
                <label className="flex items-center gap-2 text-xs dark:text-slate-300 cursor-pointer">
                  <input type="checkbox" defaultChecked className="rounded border-slate-300 text-indigo-600 cursor-pointer" />
                  <span>Notify at 80% quota consumed</span>
                </label>
                <label className="flex items-center gap-2 text-xs dark:text-slate-300 cursor-pointer">
                  <input type="checkbox" defaultChecked className="rounded border-slate-300 text-indigo-600 cursor-pointer" />
                  <span>Notify at 95% quota consumed</span>
                </label>
                <label className="flex items-center gap-2 text-xs dark:text-slate-300 cursor-pointer">
                  <input type="checkbox" defaultChecked className="rounded border-slate-300 text-indigo-600 cursor-pointer" />
                  <span>Notify immediately on REST stream errors</span>
                </label>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}
