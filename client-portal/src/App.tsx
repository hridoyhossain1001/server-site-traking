/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState, useEffect, useRef, Suspense, lazy } from 'react';
import { 
  ShieldAlert, 
  CheckCircle2, 
  XCircle,
  Loader2
} from 'lucide-react';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/Header';
import { CAPIEvent, APILog, Suggestion, Platform, EventRule, PlatformConfig, UserProfile, ClientConnection, OutboxItem } from './types';

// Lazy-loaded modular views (code-splitting for smaller initial bundle)
const DashboardView = lazy(() => import('./components/DashboardView').then(m => ({ default: m.DashboardView })));
const AnalyticsView = lazy(() => import('./components/AnalyticsView').then(m => ({ default: m.AnalyticsView })));
const CodProtectionView = lazy(() => import('./components/CodProtectionView').then(m => ({ default: m.CodProtectionView })));
const EventLogsView = lazy(() => import('./components/EventLogsView').then(m => ({ default: m.EventLogsView })));
const ApiLogsView = lazy(() => import('./components/ApiLogsView').then(m => ({ default: m.ApiLogsView })));
const SettingsView = lazy(() => import('./components/SettingsView').then(m => ({ default: m.SettingsView })));
const SetupGuideView = lazy(() => import('./components/SetupGuideView').then(m => ({ default: m.SetupGuideView })));
const SuggestionsView = lazy(() => import('./components/SuggestionsView').then(m => ({ default: m.SuggestionsView })));
const CampaignBuilderView = lazy(() => import('./components/CampaignBuilderView').then(m => ({ default: m.CampaignBuilderView })));
const AccountView = lazy(() => import('./components/AccountView').then(m => ({ default: m.AccountView })));
const OrdersView = lazy(() => import('./components/OrdersView').then(m => ({ default: m.OrdersView })));

export default function App() {
  const [activePage, setActivePage] = useState<string>('dashboard');
  const [searchVal, setSearchVal] = useState<string>('');
  const [sidebarCollapsed, setSidebarCollapsed] = useState<boolean>(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState<boolean>(false);

  // Dark/Light Mode state
  const [isDarkMode, setIsDarkMode] = useState<boolean>(() => {
    return localStorage.getItem('theme-capi-portal') === 'dark';
  });

  useEffect(() => {
    if (isDarkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme-capi-portal', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme-capi-portal', 'light');
    }
  }, [isDarkMode]);

  // Core Entity States
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [connection, setConnection] = useState<ClientConnection | null>(null);
  const [credentials, setCredentials] = useState<Record<Platform, PlatformConfig> | null>(null);
  const [rules, setRules] = useState<EventRule[]>([]);
  const [suggestions, setSuggestions] = useState<Suggestion[]>([]);
  const [events, setEvents] = useState<CAPIEvent[]>([]);
  const [apiLogs, setApiLogs] = useState<APILog[]>([]);
  const [outboxItems, setOutboxItems] = useState<OutboxItem[]>([]);
  const [retryingOutboxIds, setRetryingOutboxIds] = useState<number[]>([]);
  const [deferredData, setDeferredData] = useState<any>(null);
  const [selectedOrderIds, setSelectedOrderIds] = useState<string[]>([]);
  const [deferredEnabled, setDeferredEnabled] = useState<boolean>(false);
  const [autoConfirmDays, setAutoConfirmDays] = useState<number>(0);
  const [autoConfirmStatus, setAutoConfirmStatus] = useState<string>('completed');
  const [savingDeferredSettings, setSavingDeferredSettings] = useState<boolean>(false);

  // Advanced Analytics States
  const [analyticsOverview, setAnalyticsOverview] = useState<any>(null);
  const [analyticsCampaigns, setAnalyticsCampaigns] = useState<any>(null);
  const [analyticsHourly, setAnalyticsHourly] = useState<any>(null);
  const [signalDoctor, setSignalDoctor] = useState<any>(null);

  // Async Lifecycle States
  const [loading, setLoading] = useState<boolean>(true);
  const [aiReviewing, setAiReviewing] = useState<boolean>(false);
  const [errState, setErrState] = useState<string | null>(null);

  // Live Mode Polling State
  const [liveMode, setLiveMode] = useState<boolean>(false);
  const liveIntervalRef = useRef<any | null>(null);

  // Filters State for Logs
  const [platformFilters, setPlatformFilters] = useState<string[]>([]);
  const [statusFilters, setStatusFilters] = useState<string[]>([]);
  const [searchFilter, setSearchFilter] = useState<string>('');

  // Row selection details for expanded logs preview
  const [expandedEventId, setExpandedEventId] = useState<string | null>(null);
  const [expandedApiLogId, setExpandedApiLogId] = useState<string | null>(null);

  // FAQ Expanded State
  const [faqExpanded, setFaqExpanded] = useState<number | null>(null);

  // Sandbox Campaign Builder State
  const [builderPlatform, setBuilderPlatform] = useState<Platform>('Meta CAPI');
  const [builderEventName, setBuilderEventName] = useState<string>('Purchase');
  const [builderValue, setBuilderValue] = useState<string>('129.99');
  const [builderCurrency, setBuilderCurrency] = useState<string>('USD');
  const [builderEmail, setBuilderEmail] = useState<string>('customer@domain.com');
  const [builderPhone, setBuilderPhone] = useState<string>('+15125550199');
  const [builderIp, setBuilderIp] = useState<string>('72.229.28.185');
  const [builderUa, setBuilderUa] = useState<string>('Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7)');
  const [customParams, setCustomParams] = useState<{ k: string; v: string }[]>([
    { k: 'content_name', v: 'Designer Leather Jacket' },
    { k: 'content_category', v: 'Apparel > Outerwear' }
  ]);
  const [campaignResp, setCampaignResp] = useState<any | null>(null);
  const [dispatchingTest, setDispatchingTest] = useState<boolean>(false);

  // Campaign URL Builder States
  const [urlBuilderBaseUrl, setUrlBuilderBaseUrl] = useState<string>('');
  const [urlBuilderSource, setUrlBuilderSource] = useState<string>('facebook');
  const [urlBuilderMedium, setUrlBuilderMedium] = useState<string>('paid_social');
  const [urlBuilderCampaign, setUrlBuilderCampaign] = useState<string>('');
  const [urlBuilderContent, setUrlBuilderContent] = useState<string>('');
  const [urlBuilderTerm, setUrlBuilderTerm] = useState<string>('');
  const [generatedCampaignUrl, setGeneratedCampaignUrl] = useState<string>('');

  useEffect(() => {
    if (profile && !urlBuilderBaseUrl) {
      setUrlBuilderBaseUrl(profile.email ? `https://${profile.name.toLowerCase().replace(/\s+/g, '')}.com` : 'https://your-site.com');
    }
  }, [profile]);

  const handleGenerateCampaignUrl = () => {
    if (!urlBuilderBaseUrl.trim()) {
      showToast("Please enter a base website URL", true);
      return;
    }
    if (!urlBuilderCampaign.trim()) {
      showToast("Please enter a campaign name", true);
      return;
    }
    try {
      let base = urlBuilderBaseUrl.trim();
      if (!/^https?:\/\//i.test(base)) {
        base = 'https://' + base;
      }
      const url = new URL(base);
      url.searchParams.set('utm_source', urlBuilderSource.trim());
      url.searchParams.set('utm_medium', urlBuilderMedium.trim());
      url.searchParams.set('utm_campaign', urlBuilderCampaign.trim().toLowerCase().replace(/\s+/g, '_'));
      if (urlBuilderContent.trim()) {
        url.searchParams.set('utm_content', urlBuilderContent.trim());
      }
      if (urlBuilderTerm.trim()) {
        url.searchParams.set('utm_term', urlBuilderTerm.trim());
      }
      setGeneratedCampaignUrl(url.toString());
      showToast("Campaign URL generated successfully!", false);
    } catch (err) {
      showToast("Invalid base URL format", true);
    }
  };

  // Account / Profiles States
  const [profName, setProfName] = useState<string>('');
  const [profEmail, setProfEmail] = useState<string>('');
  const [profNotifEmail, setProfNotifEmail] = useState<string>('');
  const [profUpdating, setProfUpdating] = useState<boolean>(false);
  const [passCurrent, setPassCurrent] = useState<string>('');
  const [passNew, setPassNew] = useState<string>('');
  const [confirmDeleteText, setConfirmDeleteText] = useState<string>('');
  const [confirmRevokeText, setConfirmRevokeText] = useState<string>('');

  // Copied confirmation states mapping
  const [copiedStates, setCopiedStates] = useState<Record<string, boolean>>({});

  // Trigger feedback toasts
  const [globalToast, setGlobalToast] = useState<{ show: boolean; msg: string; err: boolean }>({ show: false, msg: '', err: false });

  const showToast = (msg: string, isErr = false) => {
    setGlobalToast({ show: true, msg, err: isErr });
    setTimeout(() => {
      setGlobalToast(prev => ({ ...prev, show: false }));
    }, 4000);
  };

  const redirectToClientLogin = () => {
    window.location.assign('/client');
  };

  const handleClientLogout = async () => {
    try {
      await fetch('/api/v1/auth/client/logout', {
        method: 'POST',
        credentials: 'include'
      });
    } catch (err) {
      console.error("Client logout endpoint failed before redirect", err);
    } finally {
      redirectToClientLogin();
    }
  };

  const isAuthFailure = (responses: Response[]) => {
    return responses.some(res => res.status === 401 || res.status === 403);
  };

  // Helper code copy
  const handleCopy = (text: string, labelId: string) => {
    navigator.clipboard.writeText(text);
    setCopiedStates(prev => ({ ...prev, [labelId]: true }));
    setTimeout(() => {
      setCopiedStates(prev => ({ ...prev, [labelId]: false }));
    }, 2000);
  };

  const fetchDeferred = async () => {
    try {
      const res = await fetch('/api/deferred');
      if (res.ok) {
        const data = await res.json();
        setDeferredData(data);
        setDeferredEnabled(data.deferredEnabled);
        setAutoConfirmDays(data.autoConfirmDays);
        setAutoConfirmStatus(data.autoConfirmStatus);
      }
    } catch (err) {
      console.error("Failed to fetch COD Protection", err);
    }
  };

  // --- Fetch API Handlers ---
  const loadSystemData = async (showShimmer = true) => {
    if (showShimmer) setLoading(true);
    try {
      // Parallel pull
      const [
        resProf, resConn, resCreds, resRules, resSugg, resLogs, resApi, resDef, resOutbox
      ] = await Promise.all([
        fetch('/api/profile'),
        fetch('/api/connection'),
        fetch('/api/credentials'),
        fetch('/api/rules'),
        fetch('/api/suggestions'),
        fetch(`/api/events?limit=100`),
        fetch(`/api/api-logs?limit=100`),
        fetch('/api/deferred'),
        fetch('/api/outbox?limit=25')
      ]);

      if (isAuthFailure([resProf, resConn, resCreds, resRules])) {
        redirectToClientLogin();
        return;
      }

      if (!resProf.ok || !resConn.ok || !resCreds.ok || !resRules.ok) {
        throw new Error("HTTP Handshake failed. Connection proxy is not fully responding.");
      }

      const dProf = await resProf.json();
      const dConn = await resConn.json();
      const dCreds = await resCreds.json();
      const dRules = await resRules.json();
      const dSugg = await resSugg.json();
      const dLogs = await resLogs.json();
      const dApi = await resApi.json();
      const dDef = await resDef.json();
      const dOutbox = resOutbox.ok ? await resOutbox.json() : { items: [] };

      setProfile(dProf);
      setConnection(dConn);
      setCredentials(dCreds);
      setRules(dRules);
      setSuggestions(dSugg);
      setEvents(dLogs.events);
      setApiLogs(dApi.logs);
      setOutboxItems(dOutbox.items || []);
      setDeferredData(dDef);
      setDeferredEnabled(dDef.deferredEnabled);
      setAutoConfirmDays(dDef.autoConfirmDays);
      setAutoConfirmStatus(dDef.autoConfirmStatus);
      
      // Initialize text fields
      setProfName(dProf.name);
      setProfEmail(dProf.email);
      setProfNotifEmail(dProf.notificationEmail || dProf.email);

      setErrState(null);
    } catch (e: any) {
      console.error(e);
      setErrState(e.message || "An unresolved network error occurred while rendering diagnostics.");
    } finally {
      if (showShimmer) setLoading(false);
    }
  };

  const loadAnalyticsData = async () => {
    try {
      const [resAnOver, resAnCamp, resAnHour, resAnDoc] = await Promise.all([
        fetch('/api/v1/analytics/overview?days=7'),
        fetch('/api/v1/analytics/campaigns?days=30'),
        fetch('/api/v1/analytics/hourly?days=7'),
        fetch('/api/v1/analytics/signal-doctor?days=7')
      ]);
      if (resAnOver.ok) setAnalyticsOverview(await resAnOver.json());
      if (resAnCamp.ok) setAnalyticsCampaigns(await resAnCamp.json());
      if (resAnHour.ok) setAnalyticsHourly(await resAnHour.json());
      if (resAnDoc.ok) setSignalDoctor(await resAnDoc.json());
    } catch (err) {
      console.error("Failed to load analytics data", err);
    }
  };

  useEffect(() => {
    loadSystemData(true);
    loadAnalyticsData();
  }, []);

  // Live Tracking Mode Polling Simulator
  useEffect(() => {
    if (liveMode) {
      // Trigger instant pulse on activate
      const streamPulse = async () => {
        try {
          const res = await fetch('/api/events/live-stream');
          const data = await res.json();
          if (data.event) {
            setEvents(prev => [data.event, ...prev]);
          }
        } catch (err) {
          console.error("Live packet error: ", err);
        }
      };

      liveIntervalRef.current = setInterval(streamPulse, 3000);
      showToast("Live events pipeline active. New triggers stream automatically.", false);
    } else {
      if (liveIntervalRef.current) {
        clearInterval(liveIntervalRef.current);
        liveIntervalRef.current = null;
      }
    }

    return () => {
      if (liveIntervalRef.current) {
        clearInterval(liveIntervalRef.current);
      }
    };
  }, [liveMode]);

  // Handle platform credential update
  const handleUpdatePlatform = async (platform: Platform, fields: Partial<PlatformConfig>) => {
    try {
      const res = await fetch('/api/credentials', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ platform, ...fields })
      });
      if (res.ok) {
        const data = await res.json();
        setCredentials(data.credentials);
        showToast(`${platform} tracking settings updated.`, false);
      }
    } catch {
      showToast(`Failed to update ${platform} credentials.`, true);
    }
  };

  // Toggle WP Event Rules
  const handleToggleRule = async (index: number, channel: 'metaEnabled' | 'tiktokEnabled' | 'ga4Enabled') => {
    const updated = [...rules];
    updated[index][channel] = !updated[index][channel];
    setRules(updated);

    try {
      await fetch('/api/rules', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ rules: updated })
      });
    } catch {
      showToast("Could not synchronize dynamic tracking rules.", true);
    }
  };

  // Core heartbeat trigger from header or settings
  const refreshWPHeartbeat = async () => {
    const res = await fetch('/api/connection/test', { method: 'POST' });
    if (!res.ok) throw new Error();
    const data = await res.json();
    setConnection(data.connection);
    await loadSystemData(false);
  };

  const handleRetryOutbox = async (id: number) => {
    setRetryingOutboxIds(prev => [...prev, id]);
    try {
      const res = await fetch(`/api/outbox/${id}/retry`, { method: 'POST' });
      const data = await res.json();
      if (!res.ok) {
        throw new Error(data.detail || 'Retry request failed.');
      }
      setOutboxItems(prev => prev.map(item => item.id === id ? data.item : item));
      showToast(`Outbox event #${id} queued for retry.`, false);
      await loadSystemData(false);
    } catch (err: any) {
      showToast(err.message || 'Could not queue retry.', true);
    } finally {
      setRetryingOutboxIds(prev => prev.filter(x => x !== id));
    }
  };

  const handleConfirmOrder = async (orderId: string) => {
    try {
      const res = await fetch('/api/deferred/confirm', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ order_id: orderId })
      });
      if (res.ok) {
        showToast("Order verified & queued successfully.", false);
        fetchDeferred();
        loadSystemData(false);
      }
    } catch {
      showToast("Verification action failed.", true);
    }
  };

  const handleCancelOrder = async (orderId: string) => {
    try {
      const res = await fetch('/api/deferred/cancel', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ order_id: orderId })
      });
      if (res.ok) {
        showToast("COD purchase cancelled. No telemetry transited.", false);
        fetchDeferred();
        loadSystemData(false);
      }
    } catch {
      showToast("Cancellation action failed.", true);
    }
  };

  const handleBulkConfirm = async () => {
    if (selectedOrderIds.length === 0) return;
    try {
      const res = await fetch('/api/deferred/confirm-bulk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ order_ids: selectedOrderIds })
      });
      if (res.ok) {
        showToast(`Successfully verified ${selectedOrderIds.length} orders.`, false);
        setSelectedOrderIds([]);
        fetchDeferred();
        loadSystemData(false);
      }
    } catch {
      showToast("Bulk verification failed.", true);
    }
  };

  const handleBulkCancel = async () => {
    if (selectedOrderIds.length === 0) return;
    try {
      const res = await fetch('/api/deferred/cancel-bulk', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ order_ids: selectedOrderIds })
      });
      if (res.ok) {
        showToast(`Successfully cancelled ${selectedOrderIds.length} telemetry streams.`, false);
        setSelectedOrderIds([]);
        fetchDeferred();
        loadSystemData(false);
      }
    } catch {
      showToast("Bulk cancellation failed.", true);
    }
  };

  const handleSaveDeferredSettings = async () => {
    setSavingDeferredSettings(true);
    try {
      const res = await fetch('/api/deferred/settings', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ deferredEnabled, autoConfirmDays, autoConfirmStatus })
      });
      if (res.ok) {
        showToast("COD Protection settings saved successfully.", false);
        loadSystemData(false);
      } else {
        showToast("Failed to save COD Protection settings.", true);
      }
    } catch {
      showToast("Failed to save COD Protection settings.", true);
    } finally {
      setSavingDeferredSettings(false);
    }
  };

  // Trigger System Diagnostics Scan Workflow
  const handleAiReview = async () => {
    setAiReviewing(true);
    try {
      const res = await fetch('/api/suggestions/ai-review', { method: 'POST' });
      if (!res.ok) throw new Error("Diagnostics scan endpoint failed.");
      const data = await res.json();
      setSuggestions(data.suggestions);
      showToast("System diagnostics successfully validated. Suggestions feed refreshed.", false);
    } catch (err: any) {
      showToast("Failed to run system diagnostics scan.", true);
    } finally {
      setAiReviewing(false);
    }
  };

  // Resolve Suggestion Card
  const toggleResolveSuggestion = async (id: string, isNowResolved: boolean) => {
    try {
      const res = await fetch('/api/suggestions/toggle-resolve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id })
      });
      if (res.ok) {
        setSuggestions(prev => prev.map(s => s.id === id ? { ...s, resolved: !s.resolved } : s));
        showToast(isNowResolved ? "Suggestion marked as resolved." : "Re-opened suggestion checklist.", false);
      }
    } catch {
      showToast("Could not update recommendation status.", true);
    }
  };

  // Dismiss Suggestion Card
  const dismissSuggestion = async (id: string) => {
    try {
      const res = await fetch('/api/suggestions/dismiss', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ id })
      });
      if (res.ok) {
        setSuggestions(prev => prev.filter(s => s.id !== id));
        showToast(`Suggestion dismissed successfully.`, false);
      }
    } catch {
      showToast("Failed to dismiss suggestion.", true);
    }
  };

  // Submit profile edit
  const submitProfileSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setProfUpdating(true);
    try {
      const res = await fetch('/api/profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          name: profName,
          email: profEmail,
          notificationEmail: profNotifEmail
        })
      });
      if (res.ok) {
        const data = await res.json();
        setProfile(data.profile);
        showToast("Profile credentials synchronized flawlessly.", false);
      }
    } catch {
      showToast("Could not synchronize profile changes.", true);
    } finally {
      setProfUpdating(false);
    }
  };

  // Dispatch campaign event builder test payload
  const handleDispatchSandboxTest = async (e: React.FormEvent) => {
    e.preventDefault();
    setDispatchingTest(true);
    setCampaignResp(null);

    // Format customParams array as a flattened object
    const customObj: Record<string, any> = {};
    customParams.forEach(p => {
      if (p.k.trim()) customObj[p.k.trim()] = p.v;
    });

    try {
      const res = await fetch('/api/campaign-test', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          platform: builderPlatform,
          eventName: builderEventName,
          value: builderValue,
          currency: builderCurrency,
          email: builderEmail,
          phone: builderPhone,
          ip: builderIp,
          userAgent: builderUa,
          customParams: customObj
        })
      });

      const data = await res.json();
      setCampaignResp({
        statusCode: res.status,
        body: data
      });

      if (res.ok && data.success) {
        showToast(`Test event successfully accepted by ${builderPlatform}!`, false);
        // Silently reload logs background
        loadSystemData(false);
      } else {
        showToast(`Relay Error! check returned console log context.`, true);
      }
    } catch (err: any) {
      setCampaignResp({
        statusCode: 500,
        body: { error: "Network stream handshake aborted.", details: err.message }
      });
      showToast("Dispatched sandbox event failed.", true);
    } finally {
      setDispatchingTest(false);
    }
  };

  const handleDemoReset = async () => {
    if (window.confirm("Restore monthly tracking parameters & tracking history to original parameters?")) {
      try {
        const res = await fetch('/api/profile/reset-demo', { method: 'POST' });
        if (res.ok) {
          showToast("Demonstration sandbox restored to pristine metrics.", false);
          loadSystemData(true);
        }
      } catch {
        showToast("Demolition sandbox reset failed.", true);
      }
    }
  };

  // Danger actions confirmers
  const handleTokenRevoke = async () => {
    if (confirmRevokeText.toUpperCase() !== 'REVOKE') {
      showToast("Verification word mismatch. Enter 'REVOKE' exactly to continue.", true);
      return;
    }
    try {
      const res = await fetch('/api/connection/revoke', { method: 'POST' });
      if (res.ok) {
        const data = await res.json();
        setConnection(data.connection);
        setConfirmRevokeText('');
        showToast("WordPress REST Access keys reset safely.", false);
      }
    } catch {
      showToast("Trouble resetting WordPress REST key.", true);
    }
  };

  const handleDeleteAccountRequest = () => {
    if (confirmDeleteText.toUpperCase() !== 'DELETE') {
      showToast("Verification word mismatch. Enter 'DELETE' exactly.", true);
      return;
    }
    showToast("Account deletion is not connected in this portal. Contact support@buykori.app.", true);
    setConfirmDeleteText('');
  };

  const submitPasswordUpdate = async () => {
    if (!passCurrent || !passNew) {
      showToast("Please enter your current and new password.", true);
      return;
    }
    if (passNew.length < 8) {
      showToast("New password must be at least 8 characters.", true);
      return;
    }
    try {
      const res = await fetch('/api/account/password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ currentPassword: passCurrent, newPassword: passNew })
      });
      if (!res.ok) {
        const data = await res.json().catch(() => ({}));
        throw new Error(data.detail || 'Password update failed.');
      }
      setPassCurrent('');
      setPassNew('');
      showToast("Password updated successfully.", false);
    } catch (err) {
      showToast(err instanceof Error ? err.message : "Password update failed.", true);
    }
  };

  // Export utility for logs
  const handleExportData = (format: 'csv' | 'json', dataToExport: 'events' | 'apilogs') => {
    let payload = "";
    const filename = `${dataToExport}_export_${new Date().toISOString().split('T')[0]}`;

    if (dataToExport === 'events') {
      if (format === 'json') {
        payload = JSON.stringify(events, null, 2);
      } else {
        payload = "Date,EventName,Platform,Status,HttpCode,DeduplicationKey\n" + 
          events.map(e => `"${e.timestamp}","${e.name}","${e.platform}","${e.status}",${e.httpCode},"${e.deduplicationKey}"`).join("\n");
      }
    } else {
      if (format === 'json') {
        payload = JSON.stringify(apiLogs, null, 2);
      } else {
        payload = "Date,Platform,Endpoint,Method,Status,LatencyMs\n" + 
          apiLogs.map(l => `"${l.timestamp}","${l.platform}","${l.endpoint}","${l.method}",${l.statusCode},${l.latencyMs}`).join("\n");
      }
    }

    const type = format === 'json' ? 'application/json' : 'text/csv';
    const blob = new Blob([payload], { type });
    const link = document.createElement("a");
    link.href = URL.createObjectURL(blob);
    link.download = `${filename}.${format}`;
    link.click();
    showToast(`Successfully extracted ${format.toUpperCase()} track dump.`, false);
  };

  // --- Calculations for metrics ---
  const filteredEventsForTable = events.filter(e => {
    // Search filter
    const matchesSearch = searchVal 
      ? (e.name.toLowerCase().includes(searchVal.toLowerCase()) || 
         e.id.toLowerCase().includes(searchVal.toLowerCase()) ||
         e.platform.toLowerCase().includes(searchVal.toLowerCase()) ||
         e.status.toLowerCase().includes(searchVal.toLowerCase()))
      : (searchFilter 
          ? (e.name.toLowerCase().includes(searchFilter.toLowerCase()) || 
             e.id.toLowerCase().includes(searchFilter.toLowerCase()) ||
             e.deduplicationKey.toLowerCase().includes(searchFilter.toLowerCase()))
          : true);
    
    // Platform select filter
    const matchesPlatform = platformFilters.length > 0 ? platformFilters.includes(e.platform) : true;
    
    // Status select filter
    const matchesStatus = statusFilters.length > 0 ? statusFilters.includes(e.status) : true;

    return matchesSearch && matchesPlatform && matchesStatus;
  });

  const filteredApiLogsForTable = apiLogs.filter(l => {
    const matchesSearch = searchVal 
      ? (l.endpoint.toLowerCase().includes(searchVal.toLowerCase()) || l.statusCode.toString().includes(searchVal))
      : true;
    const matchesPlatform = platformFilters.length > 0 ? platformFilters.includes(l.platform) : true;
    return matchesSearch && matchesPlatform;
  });

  // Calculate platform statistics
  const getPlatformStats = (p: Platform) => {
    const pEvs = events.filter(e => e.platform === p);
    const total = pEvs.length;
    const succs = pEvs.filter(e => e.status === 'Success').length;
    const rate = total > 0 ? Math.round((succs / total) * 100) : 100;
    const lastTime = pEvs[0] ? new Date(pEvs[0].timestamp).toLocaleTimeString() : 'N/A';
    return { total, rate, lastTime };
  };

  const metaStats = getPlatformStats('Meta CAPI');
  const tiktokStats = getPlatformStats('TikTok Events API');
  const ga4Stats = getPlatformStats('GA4');

  // Chart Generation: Events volume over last 30 days sample
  const getTrendData = () => {
    const dateCount: Record<string, { total: number; meta: number; tiktok: number; ga4: number }> = {};

    events.forEach(e => {
      const dayStr = new Date(e.timestamp).toLocaleDateString(undefined, { month: 'short', day: 'numeric' });
      if (!dateCount[dayStr]) {
        dateCount[dayStr] = { total: 0, meta: 0, tiktok: 0, ga4: 0 };
      }
      dateCount[dayStr].total++;
      if (e.platform === 'Meta CAPI') dateCount[dayStr].meta++;
      else if (e.platform === 'TikTok Events API') dateCount[dayStr].tiktok++;
      else if (e.platform === 'GA4') dateCount[dayStr].ga4++;
    });

    const sortedDays = Object.keys(dateCount).reverse().slice(-10); // last 10 days for readable charting
    return sortedDays.map(day => ({
      name: day,
      'Meta CAPI': dateCount[day].meta,
      'TikTok Events': dateCount[day].tiktok,
      'GA4': dateCount[day].ga4,
      'Total': dateCount[day].total
    }));
  };

  const trendData = getTrendData();

  // Suggestions optimization score
  const resolvedCount = suggestions.filter(s => s.resolved).length;
  const totalSuggCount = suggestions.length;
  const optScore = totalSuggCount > 0 
    ? Math.round(65 + (resolvedCount / totalSuggCount) * 35) 
    : 100;

  return (
    <div className={`flex min-h-screen bg-transparent font-sans text-slate-800 transition-colors duration-205 ${isDarkMode ? 'dark text-slate-100' : ''}`}>
      {/* Sidebar Navigation */}
      {profile && (
        <Sidebar 
          activePage={activePage} 
          setActivePage={setActivePage} 
          profile={profile} 
          collapsed={sidebarCollapsed}
          setCollapsed={setSidebarCollapsed}
          mobileOpen={mobileSidebarOpen}
          setMobileOpen={setMobileSidebarOpen}
          onLogout={handleClientLogout}
        />
      )}

      {/* Mobile Drawer Overlay Backdrop */}
      {mobileSidebarOpen && (
        <div 
          className="fixed inset-0 bg-slate-900/40 z-40 md:hidden transition-opacity duration-300"
          onClick={() => setMobileSidebarOpen(false)}
        />
      )}

      {/* Main Container */}
      <div className={`flex-1 flex flex-col min-w-0 transition-all duration-300 ${sidebarCollapsed ? 'md:pl-20' : 'md:pl-64'}`}>
        {connection && (
          <Header 
            title={activePage.split('-').map(w => w.charAt(0).toUpperCase() + w.slice(1)).join(' ')} 
            connection={connection}
            onRefreshConnection={refreshWPHeartbeat}
            searchVal={searchVal}
            setSearchVal={setSearchVal}
            onMenuClick={() => setMobileSidebarOpen(true)}
            isDark={isDarkMode}
            onToggleTheme={() => setIsDarkMode(!isDarkMode)}
          />
        )}

        {/* Global Error Banner */}
        {errState && (
          <div className="m-4 md:m-8 p-4 rounded-xl border border-rose-200 bg-rose-50 text-rose-800 flex items-start gap-3">
            <ShieldAlert className="w-5 h-5 text-rose-500 mt-0.5 shrink-0" />
            <div>
              <h4 className="font-bold">Gateway REST Error Connection</h4>
              <p className="text-xs mt-1 text-rose-700">{errState}</p>
              <button 
                onClick={() => loadSystemData()} 
                className="mt-3 px-3 py-1 bg-rose-600 text-white rounded text-xs font-semibold hover:bg-rose-700"
              >
                Retry handshake pulse
              </button>
            </div>
          </div>
        )}

        {/* Main Dashboard Skeleton */}
        {loading && !errState ? (
          <div className="flex-1 p-4 md:p-8 space-y-6">
            <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 md:gap-6 animate-pulse">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-28 rounded-xl border border-slate-200 bg-white p-5 space-y-3">
                  <div className="h-4 bg-slate-100 rounded w-1/2" />
                  <div className="h-8 bg-slate-202 rounded w-3/4" />
                </div>
              ))}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-4 md:gap-6 animate-pulse">
              <div className="lg:col-span-2 h-72 rounded-xl border border-slate-200 bg-white p-6" />
              <div className="lg:col-span-1 h-72 rounded-xl border border-slate-200 bg-white p-6" />
            </div>
            <div className="h-64 rounded-xl border border-slate-200 bg-white animate-pulse" />
          </div>
        ) : !errState && (
          <div className="flex-1 p-4 sm:p-6 md:p-8 space-y-4 md:space-y-6">

            {/* --- CORE VIEWS DISPATCHER --- */}
            <Suspense fallback={
              <div className="flex-1 flex items-center justify-center min-h-[400px]">
                <div className="flex flex-col items-center gap-3">
                  <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
                  <span className="text-sm text-slate-400 font-medium">Loading...</span>
                </div>
              </div>
            }>

            {/* PAGE 1: DASHBOARD */}
            {activePage === 'dashboard' && profile && (
              <DashboardView 
                profile={profile}
                events={events}
                trendData={trendData}
                metaStats={metaStats}
                tiktokStats={tiktokStats}
                ga4Stats={ga4Stats}
                optScore={optScore}
                resolvedCount={resolvedCount}
                totalSuggCount={totalSuggCount}
                setActivePage={setActivePage}
                isDarkMode={isDarkMode}
                expandedEventId={expandedEventId}
                setExpandedEventId={setExpandedEventId}
                copiedStates={copiedStates}
                handleCopy={handleCopy}
              />
            )}

            {/* PAGE 2: COD PROTECTION */}
            {activePage === 'pending-purchases' && deferredData && (
              <CodProtectionView 
                deferredData={deferredData}
                selectedOrderIds={selectedOrderIds}
                setSelectedOrderIds={setSelectedOrderIds}
                handleBulkConfirm={handleBulkConfirm}
                handleBulkCancel={handleBulkCancel}
                handleConfirmOrder={handleConfirmOrder}
                handleCancelOrder={handleCancelOrder}
                deferredEnabled={deferredEnabled}
                setDeferredEnabled={setDeferredEnabled}
                autoConfirmDays={autoConfirmDays}
                setAutoConfirmDays={setAutoConfirmDays}
                autoConfirmStatus={autoConfirmStatus}
                setAutoConfirmStatus={setAutoConfirmStatus}
                savingDeferredSettings={savingDeferredSettings}
                handleSaveDeferredSettings={handleSaveDeferredSettings}
              />
            )}

            {/* PAGE 11: ORDERS & COURIER */}
            {activePage === 'orders' && deferredData && (
              <OrdersView 
                deferredData={deferredData}
                fetchDeferred={fetchDeferred}
                handleConfirmOrder={handleConfirmOrder}
                handleCancelOrder={handleCancelOrder}
                showToast={showToast}
              />
            )}

            {/* PAGE 3: ANALYTICS */}
            {activePage === 'analytics' && (
              <AnalyticsView 
                analyticsOverview={analyticsOverview}
                analyticsCampaigns={analyticsCampaigns}
                signalDoctor={signalDoctor}
                urlBuilderBaseUrl={urlBuilderBaseUrl}
                setUrlBuilderBaseUrl={setUrlBuilderBaseUrl}
                urlBuilderSource={urlBuilderSource}
                setUrlBuilderSource={setUrlBuilderSource}
                urlBuilderMedium={urlBuilderMedium}
                setUrlBuilderMedium={setUrlBuilderMedium}
                urlBuilderCampaign={urlBuilderCampaign}
                setUrlBuilderCampaign={setUrlBuilderCampaign}
                urlBuilderContent={urlBuilderContent}
                setUrlBuilderContent={setUrlBuilderContent}
                urlBuilderTerm={urlBuilderTerm}
                setUrlBuilderTerm={setUrlBuilderTerm}
                generatedCampaignUrl={generatedCampaignUrl}
                handleGenerateCampaignUrl={handleGenerateCampaignUrl}
                copiedStates={copiedStates}
                handleCopy={handleCopy}
              />
            )}

            {/* PAGE 4: EVENT LOGS */}
            {activePage === 'event-logs' && (
              <EventLogsView 
                filteredEventsForTable={filteredEventsForTable}
                searchFilter={searchFilter}
                setSearchFilter={setSearchFilter}
                liveMode={liveMode}
                setLiveMode={setLiveMode}
                platformFilters={platformFilters}
                setPlatformFilters={setPlatformFilters}
                statusFilters={statusFilters}
                setStatusFilters={setStatusFilters}
                setSearchVal={setSearchVal}
                expandedEventId={expandedEventId}
                setExpandedEventId={setExpandedEventId}
                copiedStates={copiedStates}
                handleCopy={handleCopy}
                handleExportData={handleExportData}
                outboxItems={outboxItems}
                retryingOutboxIds={retryingOutboxIds}
                handleRetryOutbox={handleRetryOutbox}
              />
            )}

            {/* PAGE 5: API LOGS */}
            {activePage === 'api-logs' && (
              <ApiLogsView 
                filteredApiLogsForTable={filteredApiLogsForTable}
                apiLogs={apiLogs}
                expandedApiLogId={expandedApiLogId}
                setExpandedApiLogId={setExpandedApiLogId}
                isDarkMode={isDarkMode}
                handleExportData={handleExportData}
              />
            )}

            {/* PAGE 6: SETTINGS */}
            {activePage === 'settings' && credentials && connection && (
              <SettingsView 
                credentials={credentials}
                connection={connection}
                rules={rules}
                handleUpdatePlatform={handleUpdatePlatform}
                handleToggleRule={handleToggleRule}
                refreshWPHeartbeat={refreshWPHeartbeat}
                copiedStates={copiedStates}
                handleCopy={handleCopy}
                showToast={showToast}
              />
            )}

            {/* PAGE 7: SETUP GUIDE */}
            {activePage === 'setup-guide' && (
              <SetupGuideView 
                faqExpanded={faqExpanded}
                setFaqExpanded={setFaqExpanded}
                copiedStates={copiedStates}
                handleCopy={handleCopy}
                setActivePage={setActivePage}
                api_key={connection?.api_key}
              />
            )}

            {/* PAGE 8: SUGGESTIONS */}
            {activePage === 'suggestions' && (
              <SuggestionsView 
                suggestions={suggestions}
                optScore={optScore}
                aiReviewing={aiReviewing}
                handleAiReview={handleAiReview}
                toggleResolveSuggestion={toggleResolveSuggestion}
                dismissSuggestion={dismissSuggestion}
              />
            )}

            {/* PAGE 9: CAMPAIGN BUILDER */}
            {activePage === 'campaign-builder' && (
              <CampaignBuilderView 
                builderPlatform={builderPlatform}
                setBuilderPlatform={setBuilderPlatform}
                builderEventName={builderEventName}
                setBuilderEventName={setBuilderEventName}
                builderValue={builderValue}
                setBuilderValue={setBuilderValue}
                builderCurrency={builderCurrency}
                setBuilderCurrency={setBuilderCurrency}
                builderEmail={builderEmail}
                setBuilderEmail={setBuilderEmail}
                builderPhone={builderPhone}
                setBuilderPhone={setBuilderPhone}
                builderIp={builderIp}
                setBuilderIp={setBuilderIp}
                builderUa={builderUa}
                setBuilderUa={setBuilderUa}
                customParams={customParams}
                setCustomParams={setCustomParams}
                campaignResp={campaignResp}
                dispatchingTest={dispatchingTest}
                handleDispatchSandboxTest={handleDispatchSandboxTest}
                urlBuilderBaseUrl={urlBuilderBaseUrl}
                setUrlBuilderBaseUrl={setUrlBuilderBaseUrl}
                urlBuilderSource={urlBuilderSource}
                setUrlBuilderSource={setUrlBuilderSource}
                urlBuilderMedium={urlBuilderMedium}
                setUrlBuilderMedium={setUrlBuilderMedium}
                urlBuilderCampaign={urlBuilderCampaign}
                setUrlBuilderCampaign={setUrlBuilderCampaign}
                urlBuilderContent={urlBuilderContent}
                setUrlBuilderContent={setUrlBuilderContent}
                urlBuilderTerm={urlBuilderTerm}
                setUrlBuilderTerm={setUrlBuilderTerm}
                generatedCampaignUrl={generatedCampaignUrl}
                handleGenerateCampaignUrl={handleGenerateCampaignUrl}
                copiedStates={copiedStates}
                handleCopy={handleCopy}
              />
            )}

            {/* PAGE 10: ACCOUNT */}
            {activePage === 'account' && profile && (
              <AccountView 
                profile={profile}
                profName={profName}
                setProfName={setProfName}
                profEmail={profEmail}
                setProfEmail={setProfEmail}
                profNotifEmail={profNotifEmail}
                setProfNotifEmail={setProfNotifEmail}
                profUpdating={profUpdating}
                submitProfileSave={submitProfileSave}
                passCurrent={passCurrent}
                setPassCurrent={setPassCurrent}
                passNew={passNew}
                setPassNew={setPassNew}
                submitPasswordUpdate={submitPasswordUpdate}
                confirmRevokeText={confirmRevokeText}
                setConfirmRevokeText={setConfirmRevokeText}
                confirmDeleteText={confirmDeleteText}
                setConfirmDeleteText={setConfirmDeleteText}
                handleTokenRevoke={handleTokenRevoke}
                handleDeleteAccountRequest={handleDeleteAccountRequest}
                handleDemoReset={handleDemoReset}
                showToast={showToast}
              />
            )}

            </Suspense>

            {/* --- END DISPATCHER --- */}

          </div>
        )}
      </div>

      {/* Persistent notifications overlay alert */}
      {globalToast.show && (
        <div className="fixed bottom-6 right-6 z-50 flex items-center gap-3 px-4 py-3 rounded-lg border border-slate-200 shadow-xl bg-white animate-slide-in-up">
          {globalToast.err ? (
            <XCircle className="w-4.5 h-4.5 text-rose-500 shrink-0" />
          ) : (
            <CheckCircle2 className="w-4.5 h-4.5 text-emerald-500 shrink-0 animate-bounce" />
          )}
          <span className="text-xs text-slate-800 font-medium">
            {globalToast.msg}
          </span>
        </div>
      )}
    </div>
  );
}
