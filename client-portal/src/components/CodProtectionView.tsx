import React from 'react';
import { CheckCircle2, XCircle } from 'lucide-react';

interface CodProtectionViewProps {
  deferredData: any;
  selectedOrderIds: string[];
  setSelectedOrderIds: React.Dispatch<React.SetStateAction<string[]>>;
  handleBulkConfirm: () => Promise<void>;
  handleBulkCancel: () => Promise<void>;
  handleConfirmOrder: (orderId: string) => Promise<void>;
  handleCancelOrder: (orderId: string) => Promise<void>;
  deferredEnabled: boolean;
  setDeferredEnabled: (val: boolean) => void;
  autoConfirmDays: number;
  setAutoConfirmDays: (val: number) => void;
  autoConfirmStatus: string;
  setAutoConfirmStatus: (val: string) => void;
  savingDeferredSettings: boolean;
  handleSaveDeferredSettings: () => Promise<void>;
}

export function CodProtectionView({
  deferredData,
  selectedOrderIds,
  setSelectedOrderIds,
  handleBulkConfirm,
  handleBulkCancel,
  handleConfirmOrder,
  handleCancelOrder,
  deferredEnabled,
  setDeferredEnabled,
  autoConfirmDays,
  setAutoConfirmDays,
  autoConfirmStatus,
  setAutoConfirmStatus,
  savingDeferredSettings,
  handleSaveDeferredSettings
}: CodProtectionViewProps) {
  return (
    <div className="space-y-6">
      
      {/* COD Protection Settings Card */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:bg-slate-900 dark:border-slate-800 space-y-6">
        <div>
          <h3 className="font-bold text-slate-850 text-sm uppercase tracking-wide dark:text-white">COD Protection Settings</h3>
          <p className="text-xs text-slate-405 dark:text-slate-500">Configure parameters for holding and releasing Cash-on-Delivery conversion triggers.</p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 items-end">
          {/* Toggle COD Protection */}
          <div className="space-y-2">
            <label className="block text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider">COD Protection status</label>
            <label className="relative inline-flex items-center cursor-pointer select-none">
              <input 
                type="checkbox" 
                checked={deferredEnabled}
                onChange={(e) => setDeferredEnabled(e.target.checked)} 
                className="sr-only peer"
              />
              <div className="w-9 h-5 bg-slate-300 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-indigo-600" />
              <span className="ml-2 text-xs font-semibold text-slate-650 dark:text-slate-350">
                {deferredEnabled ? 'Enabled (Hold COD Orders)' : 'Disabled (Instant Dispatch)'}
              </span>
            </label>
          </div>

          {/* Auto-Verification Cutoff */}
          <div>
            <label className="block text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1.5">Auto-Verification Cutoff</label>
            <select 
              value={autoConfirmDays}
              onChange={(e) => setAutoConfirmDays(Number(e.target.value))}
              disabled={!deferredEnabled}
              className="w-full p-2.5 text-xs text-slate-800 bg-slate-50 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-200 dark:bg-slate-950 dark:border-slate-800 dark:text-white cursor-pointer disabled:opacity-50"
            >
              <option value="0">Off (Verify manually only)</option>
              <option value="1">1 Day</option>
              <option value="2">2 Days</option>
              <option value="3">3 Days</option>
              <option value="5">5 Days</option>
              <option value="7">7 Days</option>
            </select>
          </div>

          {/* Trigger Order Status */}
          <div>
            <label className="block text-[10px] font-bold text-slate-500 dark:text-slate-400 uppercase tracking-wider mb-1.5">Trigger Order Status</label>
            <select 
              value={autoConfirmStatus}
              onChange={(e) => setAutoConfirmStatus(e.target.value)}
              disabled={!deferredEnabled}
              className="w-full p-2.5 text-xs text-slate-800 bg-slate-50 border border-slate-200 rounded-lg outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all duration-200 dark:bg-slate-950 dark:border-slate-800 dark:text-white cursor-pointer disabled:opacity-50"
            >
              <option value="completed">Completed / Delivered</option>
              <option value="processing">Processing / Confirmed</option>
            </select>
          </div>
        </div>

        <div className="pt-2">
          <button
            type="button"
            disabled={savingDeferredSettings}
            onClick={handleSaveDeferredSettings}
            className="px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-700 hover:to-violet-700 disabled:opacity-50 text-white text-xs font-bold rounded-lg transition-all duration-300 transform hover:-translate-y-0.5 shadow-md shadow-indigo-500/10 hover:shadow-indigo-500/20 cursor-pointer"
          >
            {savingDeferredSettings ? 'Saving Configurations...' : 'Save COD Settings'}
          </button>
        </div>
      </div>

      
      {/* 4 Stats Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        
        {/* Card 1: Pending Count */}
        <div className="rounded-3xl border border-white/60 dark:border-white/10 bg-gradient-to-br from-amber-100/70 to-amber-50/20 dark:from-amber-900/30 dark:to-slate-900/40 backdrop-blur-2xl p-6 shadow-xl shadow-amber-900/5 transition-transform hover:scale-[1.02]">
          <div className="flex items-center justify-between">
            <p className="text-xs font-bold text-amber-800 dark:text-amber-400 border border-amber-300/30 bg-amber-100/50 dark:bg-amber-900/40 px-2 py-1 rounded-md">COD Protected</p>
          </div>
          <div className="mt-8 flex items-baseline gap-2">
            <p className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              {deferredData.pendingCount}
            </p>
            <span className="text-xs font-semibold text-amber-750/70 dark:text-amber-300/70">Orders Pending</span>
          </div>
        </div>

        {/* Card 2: Pending Value */}
        <div className="rounded-3xl border border-white/60 dark:border-white/10 bg-gradient-to-br from-indigo-100/70 to-indigo-50/20 dark:from-indigo-900/30 dark:to-slate-900/40 backdrop-blur-2xl p-6 shadow-xl shadow-indigo-900/5 transition-transform hover:scale-[1.02]">
          <div className="flex items-center justify-between">
            <p className="text-xs font-bold text-indigo-800 dark:text-indigo-400 border border-indigo-300/30 bg-indigo-100/50 dark:bg-indigo-900/40 px-2 py-1 rounded-md">Held Revenue</p>
          </div>
          <div className="mt-8 flex items-baseline gap-2">
            <p className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              {deferredData.pendingValue}
            </p>
            <span className="text-xs font-semibold text-indigo-750/70 dark:text-indigo-300/70">Pending Telemetry</span>
          </div>
        </div>

        {/* Card 3: Confirmed Today */}
        <div className="rounded-3xl border border-white/60 dark:border-white/10 bg-gradient-to-br from-emerald-200/50 to-emerald-50/20 dark:from-emerald-900/30 dark:to-slate-900/40 backdrop-blur-2xl p-6 shadow-xl shadow-emerald-900/5 transition-transform hover:scale-[1.02]">
          <div className="flex items-center justify-between">
            <p className="text-xs font-bold text-emerald-800 dark:text-emerald-400 border border-emerald-300/30 bg-emerald-100/50 dark:bg-emerald-900/40 px-2 py-1 rounded-md">Verified Today</p>
          </div>
          <div className="mt-8 flex items-baseline gap-2">
            <p className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              {deferredData.confirmedToday}
            </p>
            <span className="text-xs font-semibold text-emerald-750/70 dark:text-emerald-300/70">Transited Events</span>
          </div>
        </div>

        {/* Card 4: Oldest Pending */}
        <div className="rounded-3xl border border-white/60 dark:border-white/10 bg-gradient-to-br from-rose-100/70 to-rose-50/20 dark:from-rose-900/30 dark:to-slate-900/40 backdrop-blur-2xl p-6 shadow-xl shadow-rose-900/5 transition-transform hover:scale-[1.02]">
          <div className="flex items-center justify-between">
            <p className="text-xs font-bold text-rose-800 dark:text-rose-400 border border-rose-300/30 bg-rose-100/50 dark:bg-rose-900/40 px-2 py-1 rounded-md">Oldest Pending</p>
          </div>
          <div className="mt-8 flex items-baseline gap-2">
            <p className="text-3xl font-extrabold text-slate-900 dark:text-white tracking-tight">
              {deferredData.oldestPending}
            </p>
            <span className="text-xs font-semibold text-rose-750/70 dark:text-rose-300/70">Needs Audit</span>
          </div>
        </div>

      </div>

      {/* Main Action Bar & Table */}
      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm flex flex-col space-y-4 dark:bg-slate-900 dark:border-slate-800">
        <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
          <div>
            <h3 className="font-bold text-slate-850 text-sm uppercase tracking-wide dark:text-white">COD Protected Purchases Queue</h3>
            <p className="text-xs text-slate-400 dark:text-slate-500">Verifying customer purchase events ensures Meta and TikTok optimize on genuine conversion signals only.</p>
          </div>
          <div className="flex gap-2">
            <button 
              disabled={selectedOrderIds.length === 0}
              onClick={handleBulkConfirm}
              className="px-3 py-1.5 bg-green-50 hover:bg-green-150 disabled:opacity-50 text-green-700 text-xs font-bold rounded-lg transition-colors border border-green-200 flex items-center gap-1.5 cursor-pointer dark:bg-green-950/20 dark:text-green-400 dark:border-green-900/60"
            >
              <CheckCircle2 className="w-3.5 h-3.5" /> Verify Selected
            </button>
            <button 
              disabled={selectedOrderIds.length === 0}
              onClick={handleBulkCancel}
              className="px-3 py-1.5 bg-rose-50 hover:bg-rose-150 disabled:opacity-50 text-rose-700 text-xs font-bold rounded-lg transition-colors border border-rose-200 flex items-center gap-1.5 cursor-pointer dark:bg-rose-950/20 dark:text-rose-400 dark:border-rose-900/60"
            >
              <XCircle className="w-3.5 h-3.5" /> Cancel Selected
            </button>
          </div>
        </div>

        <div className="overflow-x-auto min-h-64">
          <table className="w-full text-left text-xs text-slate-650 divide-y divide-slate-100 min-w-[750px] dark:text-slate-300 dark:divide-slate-800">
            <thead className="bg-slate-50 text-[10px] font-bold uppercase tracking-wider text-slate-555 dark:bg-slate-950 dark:text-slate-400">
              <tr>
                <th className="px-6 py-3 w-10">
                  <input 
                    type="checkbox"
                    checked={deferredData.pendingList.length > 0 && selectedOrderIds.length === deferredData.pendingList.length}
                    onChange={(el) => {
                      if (el.target.checked) {
                        setSelectedOrderIds(deferredData.pendingList.map((o: any) => o.orderId));
                      } else {
                        setSelectedOrderIds([]);
                      }
                    }}
                    className="rounded accent-indigo-600 cursor-pointer"
                  />
                </th>
                <th className="px-6 py-3">Order ID</th>
                <th className="px-6 py-3">Customer Identifier</th>
                <th className="px-6 py-3">Transaction Value</th>
                <th className="px-6 py-3">Fraud Risk Index</th>
                <th className="px-6 py-3">Held Time</th>
                <th className="px-6 py-3 text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 dark:divide-slate-800">
              {deferredData.pendingList.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-12 text-center text-slate-400 font-medium dark:text-slate-500">
                    <CheckCircle2 className="w-8 h-8 mx-auto text-emerald-400 mb-2" />
                    Hurrah! No pending COD orders to verify. Tracking is fully clean.
                  </td>
                </tr>
              ) : (
                deferredData.pendingList.map((order: any) => {
                  const isSelected = selectedOrderIds.includes(order.orderId);
                  const activeChecks = [];
                  if (order.fraudDetails) {
                    if (order.fraudDetails.ip_mismatch) activeChecks.push('IP Mismatch');
                    if (order.fraudDetails.disposable_email) activeChecks.push('Disposable Email');
                    if (order.fraudDetails.velocity_limit) activeChecks.push('Velocity Trigger');
                    if (order.fraudDetails.gibberish_name) activeChecks.push('Gibberish Name');
                  }
                  const tooltipText = activeChecks.length > 0 ? activeChecks.join(', ') : 'Passed structural checks';

                  return (
                    <tr key={order.orderId} className={`hover:bg-slate-50/50 transition-colors dark:hover:bg-slate-800/40 ${isSelected ? 'bg-indigo-50/10 dark:bg-indigo-950/20' : ''}`}>
                      <td className="px-6 py-3">
                        <input 
                          type="checkbox"
                          checked={isSelected}
                          onChange={(el) => {
                            if (el.target.checked) {
                              setSelectedOrderIds(prev => [...prev, order.orderId]);
                            } else {
                              setSelectedOrderIds(prev => prev.filter(x => x !== order.orderId));
                            }
                          }}
                          className="rounded accent-indigo-600 cursor-pointer"
                        />
                      </td>
                      <td className="px-6 py-3 font-mono font-bold text-slate-800 dark:text-slate-100">{order.orderId}</td>
                      <td className="px-6 py-3 font-mono text-slate-550 dark:text-slate-400">{order.customer}</td>
                      <td className="px-6 py-3 font-semibold text-slate-850 dark:text-slate-200">৳{order.amount.toLocaleString()}</td>
                      <td className="px-6 py-3">
                        <span 
                          className={`inline-flex items-center gap-1 px-2.5 py-0.5 rounded text-[10px] font-bold border cursor-help ${
                            order.fraudScore >= 75 ? 'bg-rose-50 text-rose-700 border-rose-150 dark:bg-rose-950/20 dark:text-rose-400 dark:border-rose-900/60' : 
                            order.fraudScore >= 35 ? 'bg-amber-50 text-amber-700 border-amber-150 dark:bg-amber-950/20 dark:text-amber-400 dark:border-amber-900/60' : 
                            'bg-green-50 text-green-700 border-green-150 dark:bg-green-950/20 dark:text-green-400 dark:border-green-900/60'
                          }`}
                          title={tooltipText}
                        >
                          <span className={`w-1.5 h-1.5 rounded-full ${
                            order.fraudScore >= 75 ? 'bg-rose-500' : 
                            order.fraudScore >= 35 ? 'bg-amber-500' : 'bg-green-500'
                          }`} />
                          Score: {order.fraudScore}/100
                        </span>
                      </td>
                      <td className="px-6 py-3 text-slate-400 font-mono dark:text-slate-500">{order.ageHours}h ago</td>
                      <td className="px-6 py-3 text-right space-x-2 whitespace-nowrap">
                        <button 
                          onClick={() => handleConfirmOrder(order.orderId)}
                          className="px-2.5 py-1 bg-emerald-600 hover:bg-emerald-700 text-white text-[10px] font-bold rounded shadow-sm transition-colors cursor-pointer"
                        >
                          Confirm
                        </button>
                        <button 
                          onClick={() => handleCancelOrder(order.orderId)}
                          className="px-2.5 py-1 bg-rose-600 hover:bg-rose-700 text-white text-[10px] font-bold rounded shadow-sm transition-colors cursor-pointer"
                        >
                          Cancel
                        </button>
                      </td>
                    </tr>
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
