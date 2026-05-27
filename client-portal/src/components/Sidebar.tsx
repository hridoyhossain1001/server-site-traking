/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { 
  LayoutDashboard, 
  ListChecks, 
  Activity, 
  Megaphone, 
  Lightbulb, 
  Settings2, 
  BookOpen, 
  LogOut,
  ChevronLeft,
  ChevronRight,
  ShieldCheck,
  TrendingUp,
  Terminal,
  X,
  Truck
} from 'lucide-react';
import { UserProfile } from '../types';

interface SidebarProps {
  activePage: string;
  setActivePage: (page: string) => void;
  profile: UserProfile;
  collapsed: boolean;
  setCollapsed: (collapsed: boolean) => void;
  mobileOpen: boolean;
  setMobileOpen: (open: boolean) => void;
  onLogout: () => Promise<void>;
}

export function Sidebar({ 
  activePage, 
  setActivePage, 
  profile,
  collapsed,
  setCollapsed,
  mobileOpen,
  setMobileOpen,
  onLogout
}: SidebarProps) {

  const menuItems = [
    { id: 'dashboard', name: 'Dashboard', icon: LayoutDashboard },
    { id: 'analytics', name: 'Analytics', icon: TrendingUp },
    { id: 'pending-purchases', name: 'COD Protection', icon: ShieldCheck },
    { id: 'orders', name: 'Orders & Courier', icon: Truck },
    { id: 'event-logs', name: 'Event Logs', icon: ListChecks },
    { id: 'api-logs', name: 'API Logs', icon: Terminal },
    { id: 'campaign-builder', name: 'Campaign Builder', icon: Megaphone },
    { id: 'suggestions', name: 'Suggestions', icon: Lightbulb, count: 4 },
    { id: 'settings', name: 'Settings', icon: Settings2 },
    { id: 'setup-guide', name: 'Setup Guide', icon: BookOpen },
  ];


  const formatQuota = (num: number) => {
    if (num >= 1000) {
      return (num / 1000).toFixed(1) + 'k';
    }
    return num.toString();
  };

  const usagePercent = Math.min((profile.eventsUsed / profile.eventsQuota) * 100, 100);
  const quotaColor = usagePercent > 90 ? 'bg-rose-600' : usagePercent > 70 ? 'bg-amber-500' : 'bg-indigo-600';
  const textQuotaColor = usagePercent > 90 ? 'text-rose-600' : usagePercent > 70 ? 'text-amber-655' : 'text-indigo-600';

  return (
    <aside 
      className={`fixed top-0 bottom-0 left-0 z-50 flex flex-col bg-white border-r border-slate-205 transition-transform duration-300 md:transition-all dark:bg-slate-900 dark:border-slate-800 ${
        collapsed ? 'md:w-20' : 'md:w-64'
      } ${
        mobileOpen ? 'translate-x-0 w-64' : '-translate-x-full md:translate-x-0'
      }`}
    >
      {/* Brand Header */}
      <div className={`flex items-center h-12 md:h-14 border-b border-slate-100 dark:border-slate-800 ${
        collapsed ? 'justify-center px-2 gap-1' : 'justify-between px-5'
      }`}>
        <div className="flex items-center gap-2.5 overflow-hidden">
          <div className="flex items-center justify-center w-8 h-8 rounded-lg bg-indigo-600 text-white font-bold shrink-0">
            C
          </div>
          {!collapsed && (
            <span className="font-sans font-bold text-lg tracking-tight text-slate-800 dark:text-slate-100 truncate">
              CAPI Portal
            </span>
          )}
        </div>
        <button 
          onClick={() => {
            if (window.innerWidth < 768) {
              setMobileOpen(false);
            } else {
              setCollapsed(!collapsed);
            }
          }}
          className="p-1 px-[5px] rounded-md text-slate-450 hover:text-slate-600 hover:bg-slate-50 dark:text-slate-400 dark:hover:text-slate-200 dark:hover:bg-slate-800 transition-colors"
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          <span className="md:hidden">
            <X className="w-4 h-4" />
          </span>
          <span className="hidden md:inline">
            {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
          </span>
        </button>
      </div>

      {/* Primary Navigation Links */}
      <nav className="flex-1 py-4 space-y-1 overflow-y-auto px-3">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activePage === item.id;
          return (
            <button
              key={item.id}
              onClick={() => {
                setActivePage(item.id);
                setMobileOpen(false);
              }}
              className={`flex items-center w-full rounded-md text-sm font-medium transition-all duration-205 group relative ${
                isActive 
                  ? 'bg-indigo-50 text-indigo-700 dark:bg-indigo-950/40 dark:text-indigo-200' 
                  : 'text-slate-600 hover:bg-slate-50 hover:text-slate-900 dark:text-slate-300 dark:hover:bg-slate-800 dark:hover:text-slate-100'
              } ${collapsed ? 'justify-center pl-0 py-2.5' : 'gap-3 py-2 px-3'}`}
            >
              <Icon className={`w-4 h-4 shrink-0 ${isActive ? 'text-indigo-650 dark:text-indigo-400 font-bold' : 'text-slate-400 group-hover:text-slate-650 dark:group-hover:text-slate-205'}`} />
              
              {!collapsed && (
                <span className="truncate">{item.name}</span>
              )}

              {/* Suggestions count element */}
              {item.count && !collapsed && (
                <span className="ml-auto bg-indigo-100 text-indigo-700 border border-indigo-200/40 text-[10px] font-bold px-1.5 py-0.5 rounded-full shrink-0 dark:bg-indigo-950 dark:text-indigo-300 dark:border-indigo-900/60">
                  {item.count}
                </span>
              )}

              {/* Collapsed view tooltip */}
              {collapsed && (
                <div className="absolute left-full ml-3 px-2 py-1 bg-slate-900 text-white text-xs rounded-md whitespace-nowrap opacity-0 group-hover:opacity-100 pointer-events-none transition-opacity duration-150 z-50 shadow-md">
                  {item.name}
                </div>
              )}
            </button>
          );
        })}
      </nav>

      {/* Usage Indicator Badge widget */}
      <div className={`p-4 border-t border-slate-100 bg-slate-50/50 dark:border-slate-800 dark:bg-slate-850/20 ${collapsed ? 'hidden md:block' : 'p-4'}`}>
        {collapsed ? (
          <div className="flex flex-col items-center gap-1.5" title="Monthly Event Usage">
            <span className={`text-[10px] font-mono font-semibold leading-none ${textQuotaColor}`}>
              {formatQuota(profile.eventsUsed)}
            </span>
            <div className="w-10 h-1.5 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full ${quotaColor}`} 
                style={{ width: `${usagePercent}%` }}
              />
            </div>
          </div>
        ) : (
          <div className="space-y-1.5">
            <div className="flex justify-between items-center text-[11px] font-semibold text-slate-500 uppercase tracking-wider dark:text-slate-400">
              <span>Events Usage</span>
              <span className="font-bold">{usagePercent.toFixed(1)}%</span>
            </div>
            <div className="relative w-full h-1.5 bg-slate-200 dark:bg-slate-800 rounded-full overflow-hidden">
              <div 
                className={`h-full rounded-full transition-all duration-500 ${quotaColor}`} 
                style={{ width: `${usagePercent}%` }}
              />
            </div>
            <div className="flex justify-between text-[10px] text-slate-400 dark:text-slate-500 leading-none mt-1">
              <span>{formatQuota(profile.eventsUsed)} / {formatQuota(profile.eventsQuota)} events</span>
              <span>Reset in 30d</span>
            </div>
          </div>
        )}
      </div>

      {/* Connected Avatar & Disconnect Trigger */}
      <div className="p-4 bg-slate-50/85 border-t border-slate-150 dark:bg-slate-850/40 dark:border-slate-800 space-y-3 shrink-0">
        {!collapsed && (
          <div className="flex items-center gap-3">
            <div className="flex items-center justify-center w-8 h-8 rounded-full bg-indigo-100 border border-indigo-200 text-indigo-700 text-xs font-semibold select-none shadow-sm dark:bg-indigo-950 dark:border-indigo-900/60 dark:text-indigo-300">
              {profile.name.split(' ').map(n => n[0]).join('')}
            </div>
            <div className="flex flex-col overflow-hidden leading-tight">
              <span className="text-xs font-semibold text-slate-700 dark:text-slate-200 truncate">{profile.name}</span>
              <span className="text-[10px] text-slate-400 dark:text-slate-500 truncate">{profile.plan}</span>
            </div>
          </div>
        )}

        <button 
          onClick={() => {
            if (window.confirm("Are you sure you want to logout and disconnect?")) {
              onLogout();
            }
          }}
          className={`flex items-center w-full text-slate-500 hover:text-rose-600 dark:text-slate-400 dark:hover:text-rose-400 hover:bg-rose-50 dark:hover:bg-rose-950/20 rounded-lg text-sm font-medium transition-all duration-200 group ${
            collapsed ? 'justify-center py-2' : 'gap-3 py-2 px-3'
          }`}
          title="Disconnect Session / Logout"
        >
          <LogOut className="w-4 h-4 shrink-0 transition-transform group-hover:translate-x-0.5" />
          {!collapsed && <span className="text-xs">Disconnect Portal</span>}
        </button>
      </div>
    </aside>
  );
}
