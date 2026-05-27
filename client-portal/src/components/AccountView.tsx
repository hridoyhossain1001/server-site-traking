import React from 'react';
import { RotateCcw } from 'lucide-react';
import { UserProfile } from '../types';

interface AccountViewProps {
  profile: UserProfile;
  profName: string;
  setProfName: (v: string) => void;
  profEmail: string;
  setProfEmail: (v: string) => void;
  profNotifEmail: string;
  setProfNotifEmail: (v: string) => void;
  profUpdating: boolean;
  submitProfileSave: (e: React.FormEvent) => Promise<void>;
  passCurrent: string;
  setPassCurrent: (v: string) => void;
  passNew: string;
  setPassNew: (v: string) => void;
  submitPasswordUpdate: () => Promise<void>;
  confirmRevokeText: string;
  setConfirmRevokeText: (v: string) => void;
  confirmDeleteText: string;
  setConfirmDeleteText: (v: string) => void;
  handleTokenRevoke: () => Promise<void>;
  handleDeleteAccountRequest: () => void;
  handleDemoReset: () => Promise<void>;
  showToast: (msg: string, isErr?: boolean) => void;
}

export function AccountView({
  profile,
  profName,
  setProfName,
  profEmail,
  setProfEmail,
  profNotifEmail,
  setProfNotifEmail,
  profUpdating,
  submitProfileSave,
  passCurrent,
  setPassCurrent,
  passNew,
  setPassNew,
  submitPasswordUpdate,
  confirmRevokeText,
  setConfirmRevokeText,
  confirmDeleteText,
  setConfirmDeleteText,
  handleTokenRevoke,
  handleDeleteAccountRequest,
  handleDemoReset,
  showToast
}: AccountViewProps) {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
      
      {/* Edit forms */}
      <div className="lg:col-span-2 space-y-6">
        
        {/* Account detail profile save */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:bg-slate-900 dark:border-slate-800">
          <h3 className="font-bold text-slate-800 text-sm uppercase tracking-wide mb-4 dark:text-white">Edit Profile Metadata</h3>
          
          <form onSubmit={submitProfileSave} className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase mb-1">Display Name</label>
                <input 
                  type="text" 
                  value={profName}
                  onChange={(e) => setProfName(e.target.value)}
                  className="w-full p-2 text-xs bg-slate-55 border border-slate-200 dark:bg-slate-950 dark:border-slate-850 dark:text-white rounded"
                />
              </div>

              <div>
                <label className="block text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase mb-1">Profile Email</label>
                <input 
                  type="email" 
                  value={profEmail}
                  onChange={(e) => setProfEmail(e.target.value)}
                  className="w-full p-2 text-xs bg-slate-55 border border-slate-200 dark:bg-slate-955 dark:border-slate-850 dark:text-white rounded"
                />
              </div>
            </div>

            <div>
              <label className="block text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase mb-1">Telemetry Alert Notifications Email</label>
              <input 
                type="email" 
                value={profNotifEmail}
                onChange={(e) => setProfNotifEmail(e.target.value)}
                className="w-full p-2 text-xs bg-slate-55 border border-slate-200 dark:bg-slate-955 dark:border-slate-850 dark:text-white rounded"
              />
            </div>

            <div className="pt-2 text-right">
              <button 
                type="submit"
                disabled={profUpdating}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:bg-indigo-400 text-white text-xs font-bold rounded-lg transition-colors shadow-sm cursor-pointer"
              >
                {profUpdating ? 'Synchronizing fields...' : 'Save Profile Changes'}
              </button>
            </div>
          </form>
        </div>

        {/* Password modifier */}
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm dark:bg-slate-900 dark:border-slate-800">
          <h3 className="font-bold text-slate-800 text-sm uppercase tracking-wide mb-4 dark:text-white">Change Account Password</h3>
          
          <div className="space-y-4">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase mb-1">Current Password</label>
                <input 
                  type="password" 
                  value={passCurrent} 
                  placeholder="••••••••••••••"
                  onChange={(e) => setPassCurrent(e.target.value)}
                  className="w-full p-2 text-xs bg-slate-50 border border-slate-200 dark:bg-slate-950 dark:border-slate-850 dark:text-white rounded font-mono"
                />
              </div>

              <div>
                <label className="block text-[10px] font-semibold text-slate-400 dark:text-slate-500 uppercase mb-1">New Secure Password</label>
                <input 
                  type="password" 
                  value={passNew} 
                  placeholder="Enter secure password"
                  onChange={(e) => setPassNew(e.target.value)}
                  className="w-full p-2 text-xs bg-slate-55 border border-slate-200 dark:bg-slate-950 dark:border-slate-850 dark:text-white rounded font-mono"
                />
              </div>
            </div>

            <div className="pt-2 text-right">
              <button 
                onClick={submitPasswordUpdate}
                className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-xs font-bold rounded-lg transition-colors shadow-sm cursor-pointer"
              >
                Update password key
              </button>
            </div>
          </div>
        </div>

        {/* Danger parameters */}
        <div className="rounded-xl border border-rose-200 bg-rose-50 dark:bg-rose-950/10 dark:border-rose-900/40 p-6 shadow-sm space-y-6">
          <div>
            <h3 className="font-bold text-rose-800 dark:text-rose-400 text-sm uppercase tracking-wide">Danger Zone settings</h3>
            <p className="text-xs text-rose-600 dark:text-rose-500 leading-normal mt-0.5">Destructive actions require explicit verification triggers to execute</p>
          </div>

          <div className="space-y-5 divide-y divide-rose-200/50 dark:divide-rose-900/40">
            
            {/* Webhook access key change */}
            <div className="space-y-3">
              <h4 className="font-bold text-xs text-rose-800 dark:text-rose-400 uppercase tracking-widest mt-2">Revoke / Reset tracking token</h4>
              <p className="text-xs text-rose-700 dark:text-rose-500 leading-relaxed max-w-2xl">
                Resetting your API key invalidates active WordPress tracking REST webhooks immediately. This halts tracking reporting across Meta and TikTok until WordPress plugin credentials re-synchronize.
              </p>

              <div className="flex flex-col sm:flex-row gap-3">
                <input 
                  type="text" 
                  placeholder="Type 'REVOKE' to confirm reset token"
                  value={confirmRevokeText}
                  onChange={(e) => setConfirmRevokeText(e.target.value)}
                  className="p-2 text-xs bg-white border border-rose-200/50 rounded font-mono text-rose-900 focus:outline-none focus:border-rose-500 w-full sm:w-80 dark:bg-slate-950 dark:border-rose-900/60 dark:text-rose-200"
                />
                <button 
                  type="button"
                  onClick={handleTokenRevoke}
                  className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold rounded-lg transition-colors shadow cursor-pointer whitespace-nowrap"
                >
                  Revoke tracking REST credentials key
                </button>
              </div>
            </div>

            {/* Deletion requests */}
            <div className="pt-5 space-y-3">
              <h4 className="font-bold text-xs text-rose-800 dark:text-rose-400 uppercase tracking-widest">Delete account request</h4>
              <p className="text-xs text-rose-700 dark:text-rose-500 leading-relaxed max-w-2xl">
                Account deletion is not self-service in this portal yet. Contact support to request permanent removal of trace logs, analytical reports, billing data and routing keys.
              </p>

              <div className="flex flex-col sm:flex-row gap-3">
                <input 
                  type="text" 
                  placeholder="Type 'DELETE' to confirm erase parameters"
                  value={confirmDeleteText}
                  onChange={(e) => setConfirmDeleteText(e.target.value)}
                  className="p-2 text-xs bg-white border border-rose-200/50 rounded font-mono text-rose-900 focus:outline-none focus:border-rose-500 w-full sm:w-80 dark:bg-slate-950 dark:border-rose-900/60 dark:text-rose-200"
                />
                <button 
                  type="button"
                  onClick={handleDeleteAccountRequest}
                  className="px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white text-xs font-bold rounded-lg transition-colors shadow cursor-pointer whitespace-nowrap"
                >
                  Contact support for deletion
                </button>
              </div>
            </div>

          </div>
        </div>

      </div>

      {/* Left side subscriptions container */}
      <div className="space-y-6">
        
        {/* Current Active Plan summary card */}
        <div className="rounded-xl border border-slate-205 bg-white p-6 shadow-sm space-y-4 dark:bg-slate-900 dark:border-slate-800">
          <div>
            <span className="text-[10px] font-bold text-indigo-650 dark:text-indigo-400 uppercase tracking-wider block">Enterprise Account details</span>
            <h3 className="text-lg font-bold text-slate-800 dark:text-white mt-1">{profile.plan}</h3>
            <p className="text-[11px] text-slate-400 dark:text-slate-500 mt-0.5">Billing changes are handled by support</p>
          </div>

          <div className="space-y-2 text-xs text-slate-700 dark:text-slate-300 font-medium">
            <div className="flex justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
              <span className="text-slate-400 dark:text-slate-500">Monthly renewal date:</span>
              <span className="font-semibold text-slate-800 dark:text-white">{profile.renewalDate}</span>
            </div>
            
            <div className="flex justify-between border-b border-slate-100 dark:border-slate-800 pb-2">
              <span className="text-slate-400 dark:text-slate-500">Monthly Usage:</span>
              <span className="font-semibold text-slate-800 dark:text-white">{(profile.eventsUsed).toLocaleString()} / {profile.eventsQuota.toLocaleString()} counts</span>
            </div>

            <div className="flex justify-between pb-2">
              <span className="text-slate-400 dark:text-slate-500">Bypass Ad blockers capability:</span>
              <span className="font-semibold text-indigo-700 dark:text-indigo-400">Fully Enabled ✓</span>
            </div>
          </div>

          <div className="h-px bg-slate-100 dark:bg-slate-800" />

          <div>
            <span className="block text-[10px] font-bold text-slate-400 dark:text-slate-500 uppercase tracking-wide mb-2">Upgrade Subscription level</span>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-2 text-center text-xs">
              <div className="p-3 border border-indigo-200 dark:border-indigo-900/60 rounded bg-indigo-50/50 dark:bg-indigo-950/20 flex flex-col justify-between">
                <span className="font-bold text-slate-800 dark:text-white leading-none">Scale Tier</span>
                <span className="text-[10px] text-indigo-650 dark:text-indigo-400 mt-1 leading-none">250k Events / mo</span>
                <span className="text-xs font-mono font-extrabold mt-3 text-indigo-700 dark:text-indigo-400">$99 / mo</span>
                <button 
                  onClick={() => showToast("Billing checkout is not connected yet. Contact support@buykori.app to change plans.", true)}
                  className="mt-3 py-1 bg-indigo-600 hover:bg-indigo-700 text-white rounded font-semibold text-[10px] cursor-pointer"
                  type="button"
                >
                  Contact Support
                </button>
              </div>

              <div className="p-3 border border-slate-200 dark:border-slate-800 rounded hover:bg-slate-50 dark:hover:bg-slate-800/60 flex flex-col justify-between">
                <span className="font-bold text-slate-800 dark:text-white leading-none">Custom Volume</span>
                <span className="text-[10px] text-slate-450 dark:text-slate-500 mt-1 leading-none font-medium">Enterprise CAPI custom</span>
                <span className="text-xs font-mono font-extrabold mt-3 text-slate-705 dark:text-slate-300">Contact Us</span>
                <button 
                  onClick={() => showToast("Custom billing requests are not automated here. Contact support@buykori.app.", true)}
                  className="mt-3 py-1 bg-slate-800 hover:bg-slate-900 dark:bg-slate-700 dark:hover:bg-slate-650 text-white rounded font-semibold text-[10px] cursor-pointer"
                  type="button"
                >
                  Contact Support
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Reset demo sandbox context values widget */}
        <div className="rounded-xl border border-slate-205 bg-white p-5 shadow-sm space-y-3 dark:bg-slate-900 dark:border-slate-800">
          <div>
            <h4 className="font-bold text-slate-800 dark:text-white text-xs uppercase tracking-wider">Demonstration controls</h4>
            <p className="text-xs text-slate-400 dark:text-slate-550">Restore test values or delete analytics mock arrays</p>
          </div>

          <button 
            onClick={handleDemoReset}
            className="w-full py-2 bg-slate-100 hover:bg-slate-200 dark:bg-slate-800 dark:hover:bg-slate-700 dark:border-slate-800 text-slate-800 dark:text-slate-200 rounded text-xs font-semibold border border-slate-200 flex items-center justify-center gap-1.5 cursor-pointer"
          >
            <RotateCcw className="w-3.5 h-3.5" />
            Restore original diagnostic mock traces
          </button>
        </div>

      </div>
    </div>
  );
}
