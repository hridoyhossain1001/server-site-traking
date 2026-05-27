/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { 
  Bell, 
  Search, 
  HelpCircle, 
  RefreshCw,
  CheckCircle2,
  XCircle,
  Menu,
  Sun,
  Moon,
  X,
} from 'lucide-react';
import { ClientConnection } from '../types';

interface HeaderProps {
  title: string;
  connection: ClientConnection;
  onRefreshConnection: () => Promise<void>;
  searchVal: string;
  setSearchVal: (value: string) => void;
  onMenuClick?: () => void;
  isDark: boolean;
  onToggleTheme: () => void;
}

export function Header({ 
  title, 
  connection, 
  onRefreshConnection, 
  searchVal, 
  setSearchVal, 
  onMenuClick,
  isDark,
  onToggleTheme 
}: HeaderProps) {
  const [testing, setTesting] = useState(false);
  const [toast, setToast] = useState<{ show: boolean; msg: string; err: boolean }>({ show: false, msg: '', err: false });
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  const triggerHeartbeat = async () => {
    setTesting(true);
    try {
      await onRefreshConnection();
      setToast({
        show: true,
        msg: "WordPress API heartbeat synced successfully. Telemetry routes healthy.",
        err: false
      });
    } catch {
      setToast({
        show: true,
        msg: "Failed to connect to WordPress REST context stream.",
        err: true
      });
    } finally {
      setTesting(false);
      setTimeout(() => {
        setToast(prev => ({ ...prev, show: false }));
      }, 4000);
    }
  };

  const getStatusBadge = () => {
    switch (connection.status) {
      case 'Active':
        return (
          <div className="flex items-center gap-1.5 rounded-full border border-green-150 bg-green-50 px-2.5 py-0.5">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-75"></span>
              <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500"></span>
            </span>
            <span className="text-[10px] font-bold tracking-wider text-green-700 uppercase">System Active</span>
          </div>
        );
      case 'Degraded':
        return (
          <div className="flex items-center gap-1.5 rounded-full border border-amber-150 bg-amber-50 px-2.5 py-0.5">
            <span className="relative flex h-2 w-2">
              <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-amber-400 opacity-75"></span>
              <span className="relative inline-flex h-2 w-2 rounded-full bg-amber-500"></span>
            </span>
            <span className="text-[10px] font-bold tracking-wider text-amber-700 uppercase">Degraded Connection</span>
          </div>
        );
      case 'Disconnected':
      default:
        return (
          <div className="flex items-center gap-1.5 rounded-full border border-rose-150 bg-rose-50 px-2.5 py-0.5">
            <span className="relative flex h-1.5 w-1.5">
              <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-rose-500"></span>
            </span>
            <span className="text-[10px] font-bold tracking-wider text-rose-700 uppercase">Gateway Inactive</span>
          </div>
        );
    }
  };

  return (
    <>
      <header className="sticky top-0 z-35 flex h-12 md:h-14 shrink-0 items-center justify-between border-b border-slate-200 bg-white px-4 md:px-8 dark:bg-slate-900 dark:border-slate-800">
        {/* Title & Status */}
        <div className="flex items-center gap-3 md:gap-4 overflow-hidden">
          {onMenuClick && (
            <button
              onClick={onMenuClick}
              className="block md:hidden p-1.5 -ml-1 text-slate-500 hover:text-slate-800 hover:bg-slate-100 dark:text-slate-400 dark:hover:text-slate-200 dark:hover:bg-slate-800 rounded-lg transition-colors focus:outline-none focus:ring-1 focus:ring-indigo-500"
              aria-label="Toggle navigation menu"
            >
              <Menu className="w-5 h-5" />
            </button>
          )}
          <h1 className="text-sm md:text-lg font-bold tracking-tight text-slate-800 dark:text-slate-100 truncate">{title}</h1>
          <div className="hidden sm:block shrink-0">{getStatusBadge()}</div>
        </div>

        {/* Query Search / Controls */}
        <div className="flex items-center gap-2 md:gap-4 shrink-0">
          {/* Mobile Search Button (Visible only on <1024px screens / lg:hidden) */}
          <button
            type="button"
            onClick={() => setIsSearchOpen(true)}
            className="block lg:hidden p-2 rounded-full text-slate-500 hover:text-slate-800 hover:bg-slate-50 dark:text-slate-400 dark:hover:text-slate-200 dark:hover:bg-slate-800 transition-colors focus:outline-none focus:ring-1 focus:ring-indigo-500"
            title="Search logs"
          >
            <Search className="w-4 h-4 text-slate-550" />
          </button>

          <div className="relative hidden lg:block group">
            {/* Glow effect */}
            <div className="absolute -inset-0.5 bg-gradient-to-r from-orange-400 via-amber-300 to-orange-400 rounded-full blur opacity-30 group-hover:opacity-60 transition duration-500"></div>
            <input
              type="text"
              placeholder="Search activity, events..."
              value={searchVal}
              onChange={(e) => setSearchVal(e.target.value)}
              className="relative w-56 lg:w-64 xl:w-72 rounded-full border-none bg-white px-5 py-2 pr-10 text-xs shadow-md outline-none text-slate-800 dark:text-slate-100 dark:bg-slate-900 transition-all focus:ring-2 focus:ring-orange-300/50"
            />
            <Search className="absolute right-4 top-2.5 h-4 w-4 text-slate-500 dark:text-slate-400" />
          </div>

          {/* Theme Toggle - Glass Design */}
          <button
            onClick={onToggleTheme}
            className="relative flex items-center w-[54px] h-[24px] rounded-full bg-black/5 dark:bg-white/5 transition-colors cursor-pointer mx-1 border border-black/10 dark:border-white/10"
            title={isDark ? "Switch to Light Mode" : "Switch to Dark Mode"}
          >
            <span className="w-full text-center text-[9px] font-extrabold uppercase tracking-widest text-slate-600 dark:text-slate-300">
              {isDark ? (
                <span className="pr-[18px] transition-opacity">Dark</span>
              ) : (
                <span className="pl-[16px] transition-opacity">Light</span>
              )}
            </span>
            
            {/* Glass Handle */}
            <div className={`absolute w-7 h-7 rounded-full flex items-center justify-center transition-all duration-500 ease-[cubic-bezier(0.34,1.56,0.64,1)] 
              bg-white/40 dark:bg-black/40 backdrop-blur-xl 
              border border-white/80 dark:border-white/10
              shadow-[0_4px_16px_rgba(0,0,0,0.1),inset_0_1px_2px_rgba(255,255,255,0.8)] 
              dark:shadow-[0_4px_16px_rgba(0,0,0,0.5),inset_0_1px_2px_rgba(255,255,255,0.2)]
              ${isDark ? 'translate-x-[28px]' : 'translate-x-[-2px]'}`}
            >
              {isDark ? (
                <Moon className="w-3.5 h-3.5 text-white drop-shadow-[0_0_4px_rgba(255,255,255,0.5)] fill-white/20" />
              ) : (
                <Sun className="w-3.5 h-3.5 text-white drop-shadow-[0_0_4px_rgba(255,255,255,0.8)] fill-white" />
              )}
            </div>
          </button>

          {/* Sync trigger */}
          <button
            onClick={triggerHeartbeat}
            disabled={testing}
            className={`p-1.5 md:p-2 rounded-full text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-855 transition-colors ${
              testing ? 'animate-spin' : ''
            }`}
            title="Verify CAPI WordPress Connection"
          >
            <RefreshCw className="w-4 h-4" />
          </button>

          {/* Notifications & Help */}
          <div className="flex items-center gap-1 border-l border-slate-200 dark:border-slate-800 pl-2 md:pl-4">
            <button className="relative rounded-full p-1.5 md:p-2 text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-855">
              <Bell className="w-4 h-4" />
              <span className="absolute right-1.5 top-1.5 h-1.5 w-1.5 rounded-full border border-white dark:border-slate-900 bg-indigo-500"></span>
            </button>
            
            <button className="hidden sm:block rounded-full p-1.5 md:p-2 text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-855" title="API Support">
              <HelpCircle className="w-4 h-4" />
            </button>
          </div>
        </div>

        {/* Notification Toast */}
        {toast.show && (
          <div className="fixed top-14 right-4 z-50 flex items-center gap-3 px-4 py-2.5 rounded-lg border border-slate-100 shadow-lg bg-white dark:bg-slate-800 dark:border-slate-750 dark:text-white animate-slide-in-right">
            {toast.err ? (
              <XCircle className="w-4 h-4 text-rose-500 shrink-0" />
            ) : (
              <CheckCircle2 className="w-4 h-4 text-emerald-500 shrink-0" />
            )}
            <span className="text-xs text-slate-700 dark:text-slate-200 font-medium">
              {toast.msg}
            </span>
          </div>
        )}
      </header>

      {/* Responsive dedicated trigger search modal for mobile views (<768px) */}
      {isSearchOpen && (
        <div 
          className="fixed inset-0 z-50 flex items-start justify-center pt-12 px-4 bg-slate-900/60 backdrop-blur-sm animate-fade-in" 
          onClick={() => setIsSearchOpen(false)}
        >
          <div 
            className="w-full max-w-md bg-white dark:bg-slate-900 rounded-xl border border-slate-200 dark:border-slate-800 shadow-2xl overflow-hidden animate-slide-up"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between px-4 py-3 border-b border-slate-100 dark:border-slate-800 bg-slate-50 dark:bg-slate-950/40">
              <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest">Search log database</span>
              <button 
                onClick={() => setIsSearchOpen(false)}
                className="p-1 rounded-md text-slate-400 hover:text-slate-600 hover:bg-slate-100 dark:hover:bg-slate-800 transition-colors"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            {/* Modal Content */}
            <div className="p-4 space-y-4">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Filter by event name, ID, payload..."
                  value={searchVal}
                  onChange={(e) => setSearchVal(e.target.value)}
                  className="w-full rounded-lg border border-slate-205 bg-slate-50 px-9 py-2.5 text-xs outline-none focus:border-indigo-500 focus:ring-1 focus:ring-indigo-500 text-slate-800 dark:text-slate-100 dark:bg-slate-850 dark:border-slate-700 font-mono transition-all"
                  autoFocus
                />
                <Search className="absolute left-3 top-3 h-3.5 w-3.5 text-slate-400" />
                {searchVal && (
                  <button
                    onClick={() => setSearchVal('')}
                    className="absolute right-3 top-2.5 px-2 py-0.5 rounded text-[10px] font-semibold text-slate-400 hover:bg-slate-200 dark:hover:bg-slate-800 hover:text-slate-700 dark:hover:text-slate-200"
                  >
                    Clear
                  </button>
                )}
              </div>

              {/* Instant Highlight Feature Info */}
              <div className="text-[10px] text-slate-400 flex items-center justify-between">
                <span>Real-time key highlights active</span>
                {searchVal && (
                  <span className="text-indigo-600 dark:text-indigo-400 font-mono text-[9px] bg-indigo-50 dark:bg-indigo-950/40 px-1.5 py-0.5 rounded">
                    "{searchVal}"
                  </span>
                )}
              </div>

              {/* Action Buttons */}
              <div className="flex justify-end gap-2 pt-2 border-t border-slate-100 dark:border-slate-800">
                <button
                  type="button"
                  onClick={() => {
                    setSearchVal('');
                    setIsSearchOpen(false);
                  }}
                  className="px-3 py-1.5 bg-slate-50 hover:bg-slate-100 dark:bg-slate-800 dark:hover:bg-slate-750 text-slate-600 dark:text-slate-200 rounded-lg text-xs font-bold transition-all border border-slate-200 dark:border-slate-700"
                >
                  Reset
                </button>
                <button
                  type="button"
                  onClick={() => setIsSearchOpen(false)}
                  className="px-4 py-1.5 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg text-xs font-bold transition-all shadow-sm"
                >
                  View Filtered Logs
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
