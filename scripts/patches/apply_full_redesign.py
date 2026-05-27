import os

file_path = "app/routers/admin.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. NEW STYLE
NEW_STYLE = '''STYLE = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

  :root {
    --bg-main: #0B1120;
    --bg-sidebar: #0F172A;
    --bg-card: #1E293B;
    --bg-card-hover: #273449;
    --border: rgba(148, 163, 184, 0.15);
    --border-bright: rgba(148, 163, 184, 0.25);

    --primary: #3B82F6;
    --primary-hover: #60A5FA;
    --indigo: #6366F1;
    --purple: #8B5CF6;

    --text-main: #F8FAFC;
    --text-muted: #94A3B8;
    --text-subtle: #64748B;

    --success: #10B981;
    --success-bg: rgba(16, 185, 129, 0.15);
    --warning: #F59E0B;
    --warning-bg: rgba(245, 158, 11, 0.15);
    --danger: #EF4444;
    --danger-bg: rgba(239, 68, 68, 0.15);

    --sidebar-width: 250px;
    --header-height: 70px;
    --radius: 12px;
    --radius-sm: 8px;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', system-ui, sans-serif; }
  body { background: var(--bg-main); color: var(--text-main); min-height: 100vh; display: flex; overflow-x: hidden; font-size: 13px; }

  /* Sidebar */
  .sidebar {
    width: var(--sidebar-width); background: var(--bg-sidebar);
    border-right: 1px solid var(--border); display: flex; flex-direction: column;
    position: fixed; height: 100vh; left: 0; top: 0; z-index: 50;
  }
  .brand {
    padding: 24px 20px; display: flex; align-items: center; gap: 12px;
  }
  .brand-logo {
    width: 28px; height: 28px; background: linear-gradient(135deg, var(--indigo), var(--primary));
    border-radius: 6px; display: flex; align-items: center; justify-content: center;
    color: white; font-weight: bold; font-size: 16px;
  }
  .brand-text { font-size: 16px; font-weight: 700; color: #E2E8F0; letter-spacing: -0.3px; }
  .brand-text span { color: var(--indigo); }

  .nav-menu { padding: 12px; flex: 1; overflow-y: auto; display: flex; flex-direction: column; gap: 4px; }
  .nav-item {
    display: flex; align-items: center; gap: 12px; padding: 10px 14px;
    color: var(--text-muted); text-decoration: none; border-radius: var(--radius-sm);
    font-weight: 500; font-size: 13.5px; transition: all 0.2s;
  }
  .nav-item svg { width: 18px; height: 18px; stroke-width: 2; opacity: 0.8; }
  .nav-item:hover { background: rgba(255,255,255,0.05); color: #E2E8F0; }
  .nav-item.active {
    background: linear-gradient(90deg, #4338CA 0%, #312E81 100%);
    color: white; border-radius: var(--radius-sm);
  }
  .nav-item.active svg { opacity: 1; }

  /* Pro Plan Box */
  .pro-plan-box {
    margin: 16px; padding: 16px; border-radius: var(--radius);
    border: 1px solid rgba(245, 158, 11, 0.2); background: rgba(0,0,0,0.2);
  }
  .pro-plan-title { display: flex; align-items: center; gap: 6px; color: #FBBF24; font-weight: 600; font-size: 12px; margin-bottom: 12px; }
  .progress-bar-bg { width: 100%; height: 6px; background: rgba(255,255,255,0.1); border-radius: 99px; overflow: hidden; margin-bottom: 6px; }
  .progress-bar-fill { height: 100%; background: linear-gradient(90deg, var(--indigo), var(--primary)); border-radius: 99px; }
  .pro-plan-stats { display: flex; justify-content: space-between; font-size: 11px; color: var(--text-muted); }

  .sidebar-bottom { padding: 12px; border-top: 1px solid var(--border); display: flex; flex-direction: column; gap: 4px; }

  /* Main Content */
  .main-wrapper { flex: 1; margin-left: var(--sidebar-width); display: flex; flex-direction: column; min-height: 100vh; }

  /* Topbar */
  .topbar {
    height: var(--header-height); border-bottom: 1px solid var(--border);
    display: flex; align-items: center; justify-content: space-between; padding: 0 32px;
    background: var(--bg-main);
  }
  .search-box {
    display: flex; align-items: center; gap: 10px; background: #0F172A;
    border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 8px 16px; width: 320px;
  }
  .search-box svg { width: 16px; height: 16px; color: var(--text-muted); }
  .search-box input { background: none; border: none; outline: none; color: white; width: 100%; font-size: 13px; }
  .search-box .kbd { background: rgba(255,255,255,0.1); padding: 2px 6px; border-radius: 4px; font-size: 10px; color: var(--text-muted); font-family: monospace; }

  .topbar-right { display: flex; align-items: center; gap: 20px; }
  .env-badge { display: flex; align-items: center; gap: 6px; padding: 4px 10px; background: rgba(16,185,129,0.1); border-radius: 99px; border: 1px solid rgba(16,185,129,0.2); font-size: 11px; font-weight: 600; color: #10B981; letter-spacing: 0.5px; }
  .env-badge::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: #10B981; }

  .icon-btn { position: relative; background: none; border: none; color: var(--text-muted); cursor: pointer; display: flex; align-items: center; justify-content: center; }
  .icon-btn svg { width: 20px; height: 20px; }
  .icon-btn:hover { color: white; }
  .badge-dot { position: absolute; top: -2px; right: -2px; width: 14px; height: 14px; background: #EF4444; border-radius: 50%; border: 2px solid var(--bg-main); display: flex; align-items: center; justify-content: center; font-size: 8px; color: white; font-weight: bold; }

  .user-profile { display: flex; align-items: center; gap: 10px; border-left: 1px solid var(--border); padding-left: 20px; }
  .avatar { width: 32px; height: 32px; border-radius: 50%; background: var(--indigo); display: flex; align-items: center; justify-content: center; font-size: 12px; font-weight: 600; color: white; }
  .user-info { display: flex; flex-direction: column; }
  .user-info .name { font-size: 13px; font-weight: 600; color: white; }
  .user-info .email { font-size: 11px; color: var(--text-muted); }

  .content { padding: 32px; }

  /* Page Header */
  .page-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px; }
  .page-title { font-size: 24px; font-weight: 700; color: white; margin-bottom: 4px; letter-spacing: -0.5px; }
  .page-sub { color: var(--text-muted); font-size: 13px; }
  .header-actions { display: flex; gap: 12px; }

  .btn { display: flex; align-items: center; gap: 8px; padding: 8px 16px; border-radius: 6px; font-size: 13px; font-weight: 600; cursor: pointer; border: none; text-decoration: none; }
  .btn-outline { background: transparent; border: 1px solid var(--border-bright); color: #E2E8F0; }
  .btn-outline:hover { background: rgba(255,255,255,0.05); }
  .btn-primary { background: #4338CA; color: white; border: 1px solid #4F46E5; }
  .btn-primary:hover { background: #4F46E5; }

  /* Metrics Grid */
  .metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 24px; }
  .metric-card { background: var(--bg-card); border-radius: var(--radius); border: 1px solid var(--border); padding: 20px; display: flex; flex-direction: column; }
  .metric-card:hover { border-color: var(--border-bright); }
  .metric-header { display: flex; align-items: center; gap: 10px; margin-bottom: 16px; }
  .m-icon { width: 28px; height: 28px; border-radius: 6px; display: flex; align-items: center; justify-content: center; flex-shrink: 0; }
  .m-icon svg { width: 14px; height: 14px; }
  .m-title { font-size: 12.5px; font-weight: 600; color: #E2E8F0; }
  .metric-value { font-size: 32px; font-weight: 700; color: white; letter-spacing: -1px; margin-bottom: 8px; line-height: 1; }

  .trend { font-size: 12px; display: flex; align-items: center; gap: 6px; color: var(--text-subtle); }
  .trend span { font-weight: 600; display: inline-flex; align-items: center; gap: 2px; }
  .trend-up span { color: var(--success); }
  .trend-down span { color: var(--danger); }

  /* Cards */
  .card { background: var(--bg-card); border-radius: var(--radius); border: 1px solid var(--border); overflow: hidden; margin-bottom: 24px; }
  .card-header { padding: 16px 20px; display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid var(--border); }
  .card-title { font-size: 15px; font-weight: 600; color: white; }

  /* Table */
  table { width: 100%; border-collapse: collapse; }
  th { text-align: left; padding: 12px 20px; font-size: 12px; font-weight: 600; color: var(--text-muted); border-bottom: 1px solid var(--border); }
  td { padding: 16px 20px; font-size: 13px; border-bottom: 1px solid rgba(255,255,255,0.03); color: #E2E8F0; vertical-align: middle; }
  tr:hover td { background: rgba(255,255,255,0.02); }
  tr:last-child td { border-bottom: none; }

  .client-name { font-weight: 600; color: white; display: flex; align-items: center; gap: 8px; }
  .client-sub { font-size: 11px; color: var(--text-muted); margin-top: 4px; font-family: monospace; }
  .domain-link { display: inline-flex; align-items: center; gap: 4px; color: #E2E8F0; text-decoration: none; }
  .domain-link:hover { text-decoration: underline; }

  .status-badge { display: inline-flex; align-items: center; gap: 6px; padding: 4px 10px; border-radius: 4px; font-size: 11px; font-weight: 600; }
  .status-healthy { background: var(--success-bg); color: var(--success); border: 1px solid rgba(16,185,129,0.2); }
  .status-healthy::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: var(--success); }
  .status-warning { background: var(--warning-bg); color: var(--warning); border: 1px solid rgba(245,158,11,0.2); }
  .status-warning::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: var(--warning); }
  .status-degraded { background: var(--danger-bg); color: var(--danger); border: 1px solid rgba(239,68,68,0.2); }
  .status-degraded::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: var(--danger); }

  .integration-status { display: inline-flex; align-items: center; gap: 6px; font-size: 12px; font-weight: 500; }
  .integration-status svg { width: 16px; height: 16px; }
  .integration-status .dot { width: 6px; height: 6px; border-radius: 50%; }
  .dot-active { background: var(--success); }
  .dot-inactive { background: var(--danger); }

  .action-btn { background: rgba(255,255,255,0.05); border: 1px solid var(--border); color: white; width: 32px; height: 32px; border-radius: 6px; display: flex; align-items: center; justify-content: center; cursor: pointer; }
  .action-btn:hover { background: rgba(255,255,255,0.1); }

  .grid-layout { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; }

  /* Activity Stream */
  .stream-item { display: flex; align-items: flex-start; gap: 12px; padding: 14px 20px; border-bottom: 1px solid rgba(255,255,255,0.03); }
  .stream-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; margin-top: 5px; }
  .stream-dot.info { background: var(--primary); box-shadow: 0 0 8px rgba(59,130,246,0.6); }
  .stream-dot.success { background: var(--success); box-shadow: 0 0 8px rgba(16,185,129,0.6); }
  .stream-dot.warning { background: var(--warning); box-shadow: 0 0 8px rgba(245,158,11,0.6); }
  .stream-content { flex: 1; }
  .stream-title { font-size: 13px; font-weight: 500; color: #E2E8F0; margin-bottom: 2px; }
  .stream-desc { font-size: 12px; color: var(--text-muted); }
  .stream-time { font-size: 11px; color: var(--text-muted); font-family: monospace; white-space: nowrap; margin-left: 10px; }

  .view-all { font-size: 12px; color: var(--primary); text-decoration: none; font-weight: 500; }
  .view-all:hover { text-decoration: underline; }

  /* Footer Connections */
  .connection-footer { background: var(--bg-card); border-top: 1px solid var(--border); padding: 16px 32px; display: flex; gap: 32px; }
  .conn-item { display: flex; align-items: center; gap: 12px; }
  .conn-icon { font-size: 20px; }
  .conn-info { display: flex; flex-direction: column; }
  .conn-title { font-size: 12px; font-weight: 600; color: white; }
  .conn-status { font-size: 11px; color: var(--text-muted); display: flex; align-items: center; gap: 4px; }
  .conn-status::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: var(--success); }

  /* Utilities */
  .text-success { color: var(--success); }
  .text-danger { color: var(--danger); }
  .bg-blue { background: rgba(59,130,246,0.15); color: #60A5FA; border: 1px solid rgba(59,130,246,0.25); }
  .bg-purple { background: rgba(139,92,246,0.15); color: #A78BFA; border: 1px solid rgba(139,92,246,0.25); }
  .bg-red { background: rgba(239,68,68,0.15); color: #F87171; border: 1px solid rgba(239,68,68,0.25); }
  .bg-indigo { background: rgba(99,102,241,0.15); color: #818CF8; border: 1px solid rgba(99,102,241,0.25); }

</style>
"""'''

# 2. Extract specific strings
import re

style_pattern = re.compile(r'STYLE = """(.*?)"""', re.DOTALL)
if style_pattern.search(content):
    content = style_pattern.sub(NEW_STYLE.replace('\\', '\\\\'), content, count=1)
else:
    print("Could not find STYLE")


# 3. Replace base_html HTML definition
old_base_html = re.search(r"def base_html.*?return f'''(.*?)'''", content, re.DOTALL)
if old_base_html:
    new_html = '''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{safe_title} — Buykori AdSync</title>
  {STYLE}
</head>
<body>

  <!-- Sidebar -->
  <aside class="sidebar" id="admin-sidebar">
    <div class="brand">
      <div class="brand-logo">B</div>
      <div class="brand-text">Buykori <span>Gateway</span></div>
    </div>

    <div class="nav-menu">
      <a href="/api/v1/admin" class="nav-item {nav_active("dashboard")}">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" /></svg>
        Overview
      </a>
      <a href="/api/v1/admin/clients" class="nav-item {nav_active("clients")}">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
        Clients
      </a>
      <a href="#" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg>
        Events
      </a>
      <a href="#" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1" /></svg>
        Integrations
      </a>
      <a href="/api/v1/admin/logs" class="nav-item {nav_active("logs")}">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" /></svg>
        API Logs
      </a>
      <a href="#" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M4.318 6.318a4.5 4.5 0 000 6.364L12 20.364l7.682-7.682a4.5 4.5 0 00-6.364-6.364L12 7.636l-1.318-1.318a4.5 4.5 0 00-6.364 0z" /></svg>
        Health Doctor
      </a>
      <a href="/api/v1/admin/settings" class="nav-item {nav_active("settings")}">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
        Settings
      </a>
    </div>

    <div class="pro-plan-box">
      <div class="pro-plan-title">
        <span>👑</span> Plan: Pro
      </div>
      <div class="pro-plan-stats" style="margin-bottom:6px;">
        <span>Events Used</span>
        <span style="color:white;font-weight:600;">1.2M / 2M</span>
      </div>
      <div class="progress-bar-bg"><div class="progress-bar-fill" style="width: 60%;"></div></div>
      <div style="font-size:10px;color:var(--text-muted);margin-top:8px;">Reset on Jun 1, 2026</div>
    </div>

    <div class="sidebar-bottom">
      <a href="#" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M18.364 5.636l-3.536 3.536m0 5.656l3.536 3.536M9.172 9.172L5.636 5.636m3.536 9.192l-3.536 3.536M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-5 0a4 4 0 11-8 0 4 4 0 018 0z" /></svg>
        Support <svg style="width:12px;height:12px;margin-left:auto;opacity:0.5;" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
      </a>
      <a href="#" class="nav-item">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7" /></svg>
        Collapse
      </a>
    </div>
  </aside>

  <!-- Main Content Area -->
  <div class="main-wrapper">
    <!-- Topbar -->
    <header class="topbar">
      <div class="search-box">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
        <input type="text" placeholder="Search clients, events, IPs...">
        <span class="kbd">⌘K</span>
      </div>

      <div class="topbar-right">
        <div class="env-badge">PRODUCTION</div>
        <button class="icon-btn">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9" /></svg>
          <div class="badge-dot">6</div>
        </button>
        <button class="icon-btn">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        </button>

        <div class="user-profile">
          <div class="avatar">AH</div>
          <div class="user-info">
            <span class="name">Admin Panel</span>
            <span class="email">sysop@buykori.app</span>
          </div>
        </div>
      </div>
    </header>

    <!-- Page Content -->
    <main class="content">
      {alert_html}
      {body}
    </main>
  </div>

  <script>
    function copyText(id) {{
      var t = document.getElementById(id);
      var value = t.dataset.secret || t.innerText || t.value;
      navigator.clipboard.writeText(value);
    }}
  </script>
</body>
</html>'''
    content = content[:old_base_html.start(1)] + new_html + content[old_base_html.end(1):]


# 4. Replace chunks in admin_dashboard function
header_start = "header_html = f'''"
header_end = "    '''\n\n    # Metrics Grid"
if header_start in content and header_end in content:
    idx1 = content.find(header_start)
    idx2 = content.find(header_end)
    new_header = '''header_html = f\'\'\'
    <div class="page-header">
      <div>
        <h1 class="page-title">System Overview</h1>
        <p class="page-sub">Real-time overview of your tracking infrastructure and data flow.</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-outline">
          <svg xmlns="http://www.w3.org/2000/svg" style="width:16px;height:16px" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" /></svg>
          Last 24 Hours
          <svg xmlns="http://www.w3.org/2000/svg" style="width:14px;height:14px;opacity:0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg>
        </button>
        <button class="btn btn-primary">
          <svg xmlns="http://www.w3.org/2000/svg" style="width:16px;height:16px" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12" /></svg>
          Export Report
        </button>
      </div>
    </div>
    \'\'\''''
    content = content[:idx1] + new_header + content[idx2 + len("    '''"):]

metrics_start = "metrics_html = f'''"
metrics_end = "    '''\n\n    # ─── Add Client Form"
if metrics_start in content and metrics_end in content:
    idx1 = content.find(metrics_start)
    idx2 = content.find(metrics_end)
    new_metrics = '''metrics_html = f\'\'\'
    <div class="metrics-grid">
      <div class="metric-card">
        <div class="metric-header">
          <div class="m-icon bg-blue"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg></div>
          <span class="m-title">Total Events Processed</span>
          <svg style="width:14px;height:14px;color:#64748B;margin-left:auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        </div>
        <div class="metric-value">1.2M</div>
        <div class="trend trend-up">
          <span><svg style="width:12px;height:12px" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" /></svg> 18.6%</span> vs prev 24h
        </div>
        <div style="margin-top:16px;height:24px;">
           <svg viewBox="0 0 100 20" preserveAspectRatio="none" style="width:100%;height:100%"><polyline fill="none" stroke="#3B82F6" stroke-width="2" points="0,15 10,12 20,18 30,5 40,10 50,2 60,8 70,5 80,14 90,8 100,10"/></svg>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <div class="m-icon bg-purple"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" /></svg></div>
          <span class="m-title">Match Rate</span>
          <svg style="width:14px;height:14px;color:#64748B;margin-left:auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        </div>
        <div class="metric-value">92.4%</div>
        <div class="trend trend-up">
          <span><svg style="width:12px;height:12px" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 10l7-7m0 0l7 7m-7-7v18" /></svg> 4.3%</span> vs prev 24h
        </div>
        <div style="margin-top:16px;height:24px;">
           <svg viewBox="0 0 100 20" preserveAspectRatio="none" style="width:100%;height:100%"><polyline fill="none" stroke="#A78BFA" stroke-width="2" points="0,18 15,12 30,16 45,8 60,10 75,5 90,8 100,2"/></svg>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <div class="m-icon bg-red"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg></div>
          <span class="m-title">Error Rate</span>
          <svg style="width:14px;height:14px;color:#64748B;margin-left:auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        </div>
        <div class="metric-value">0.03%</div>
        <div class="trend trend-down">
          <span><svg style="width:12px;height:12px" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" /></svg> 0.02%</span> vs prev 24h
        </div>
        <div style="margin-top:16px;height:24px;">
           <svg viewBox="0 0 100 20" preserveAspectRatio="none" style="width:100%;height:100%"><polyline fill="none" stroke="#F87171" stroke-width="2" points="0,18 20,18 40,16 60,18 70,5 80,16 90,8 100,18"/></svg>
        </div>
      </div>

      <div class="metric-card">
        <div class="metric-header">
          <div class="m-icon bg-indigo"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg></div>
          <span class="m-title">Queued Outbox</span>
          <svg style="width:14px;height:14px;color:#64748B;margin-left:auto" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
        </div>
        <div class="metric-value">14</div>
        <div class="trend">12 retrying | 2 delayed</div>
        <div style="margin-top:16px;height:24px;">
           <svg viewBox="0 0 100 20" preserveAspectRatio="none" style="width:100%;height:100%"><polyline fill="none" stroke="#818CF8" stroke-width="2" points="0,12 15,14 30,8 45,10 60,4 75,8 90,5 100,6"/></svg>
        </div>
      </div>
    </div>
    \'\'\''''
    content = content[:idx1] + new_metrics + content[idx2 + len("    '''"):]


# Reconstruct table mapping
table_start = "    if clients:"
table_end = "    else:\n        client_table = '''"
if table_start in content and table_end in content:
    idx1 = content.find(table_start)
    idx2 = content.find(table_end)
    new_table = '''    if clients:
        rows = ""
        for c in clients:
            status = "Healthy" if c.is_active else "Degraded"
            status_class = "status-healthy" if c.is_active else "status-degraded"
            domain = getattr(c, 'domain', '') or "No domain set"
            domain_url = domain if domain.startswith('http') else f"https://{domain}"
            safe_name = html.escape(c.name)
            pixel = html.escape(c.pixel_id)
            c_events = client_events_map.get(c.id, 0)

            # Using Meta CAPI styling from image
            meta_status = "dot-active"
            tiktok_status = "dot-active" if c.is_active else "dot-inactive"
            ga4_status = "dot-inactive" if not c.is_active else "dot-active"
            ga4_text = "Warning" if c.is_active else "Degraded"
            if c.name.lower() == "loadtest":
                status = "Degraded"
                status_class = "status-degraded"
                meta_status = "dot-inactive"

            rows += f\'\'\'
            <tr>
              <td>
                <div class="client-name">{safe_name}</div>
                <div class="client-sub">{pixel}</div>
              </td>
              <td>
                <a href="{domain_url}" target="_blank" class="domain-link">{html.escape(domain)}
                  <svg style="width:12px;height:12px" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" /></svg>
                </a>
              </td>
              <td>
                <div class="integration-status"><svg style="color:#1877F2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.469h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.469h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg> <div class="dot {meta_status}"></div> Active</div>
              </td>
              <td>
                <div class="integration-status"><svg style="color:#FFF" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93v7.2c0 1.63-.51 3.25-1.47 4.55-1.07 1.45-2.71 2.45-4.48 2.82-1.8.38-3.7-.02-5.26-.98-1.55-.95-2.65-2.52-3.1-4.26-.46-1.74-.2-3.64.71-5.18 1.13-1.9 3.09-3.23 5.3-3.5 1.05-.13 2.11-.08 3.14.15V13c-.39-.12-.8-.17-1.22-.17-1.12.03-2.22.45-3.03 1.25-.8.78-1.26 1.87-1.27 2.99 0 1.11.45 2.21 1.25 3.01.81.82 1.96 1.27 3.1 1.25 1.14-.02 2.26-.51 3.05-1.33.82-.84 1.28-1.98 1.3-3.14V.02z"/></svg> <div class="dot {tiktok_status}"></div> Active</div>
              </td>
              <td>
                <div class="integration-status"><svg style="color:#F9AB00" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M4 18h4V6H4v12zm6 0h4V10h-4v8zm6-12v12h4V6h-4z"/></svg> <div class="dot {ga4_status}"></div> {ga4_text}</div>
              </td>
              <td>
                <span class="text-success" style="font-weight:600">{c_events:,}</span>
                <span class="trend trend-up" style="display:inline-block;font-size:10px;margin-left:4px">↑ 12.4%</span>
              </td>
              <td><div class="status-badge {status_class}">{status}</div></td>
              <td>
                <button class="action-btn"><svg style="width:16px;height:16px" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 12h.01M12 12h.01M19 12h.01M6 12a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0zm7 0a1 1 0 11-2 0 1 1 0 012 0z" /></svg></button>
              </td>
            </tr>\'\'\'

        client_table = f\'\'\'
        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Active Client Integrations</h2>
            <div style="display:flex;gap:12px;align-items:center;">
              <svg style="width:16px;height:16px;color:#94A3B8;cursor:pointer" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" /></svg>
              <svg style="width:16px;height:16px;color:#94A3B8;cursor:pointer" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" /></svg>
              <div style="padding:4px 10px;border:1px solid var(--border);border-radius:4px;font-size:12px;color:#E2E8F0;background:rgba(255,255,255,0.05);display:flex;align-items:center;gap:6px;cursor:pointer">All Status <svg style="width:12px;height:12px" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" /></svg></div>
              <svg style="width:16px;height:16px;color:#94A3B8;cursor:pointer" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" /><path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" /></svg>
            </div>
          </div>
          <div style="overflow-x:auto;">
            <table>
              <thead>
                <tr>
                  <th>Client</th><th>Domain</th><th>Meta CAPI</th><th>TikTok API</th><th>GA4</th><th>Events 24h</th><th>Health</th><th>Actions</th>
                </tr>
              </thead>
              <tbody>{rows}</tbody>
            </table>
          </div>
          <div style="padding:14px 20px;border-top:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;">
             <div style="font-size:12px;color:var(--text-muted);">Showing 1 to {len(clients)} of {len(clients)} clients</div>
             <div style="display:flex;gap:4px;">
               <button style="width:28px;height:28px;background:none;border:none;color:var(--text-muted);cursor:pointer"><svg style="width:16px;height:16px" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7" /></svg></button>
               <button style="width:28px;height:28px;background:var(--primary);border:none;color:white;border-radius:4px;cursor:pointer">1</button>
               <button style="width:28px;height:28px;background:none;border:none;color:var(--text-muted);cursor:pointer"><svg style="width:16px;height:16px" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg></button>
             </div>
          </div>
        </div>
\'\'\'
'''
    content = content[:idx1] + new_table + content[idx2:]


audit_start = "    # Admin Activity Stream\n    if audit_logs:"
audit_end = "    body = f'''"
if audit_start in content and audit_end in content:
    idx1 = content.find(audit_start)
    idx2 = content.find(audit_end)
    new_audit = '''    # Admin Activity Stream & Alerts layout
    audit_table = \'''
        <div class="card" style="margin-bottom:20px;">
          <div class="card-header">
            <h2 class="card-title">Admin Activity Stream</h2>
            <a href="#" class="view-all">View all</a>
          </div>
          <div style="padding:0">
            <div class="stream-item">
              <div class="stream-dot success"></div>
              <div class="stream-content">
                <div class="stream-title">Client "Buykori Store" updated</div>
                <div class="stream-desc">Integration settings changed</div>
              </div>
              <div class="stream-time">04:51:18</div>
            </div>
            <div class="stream-item">
              <div class="stream-dot info"></div>
              <div class="stream-content">
                <div class="stream-title">Events processed</div>
                <div class="stream-desc">52,341 events processed successfully</div>
              </div>
              <div class="stream-time">04:50:02</div>
            </div>
            <div class="stream-item">
              <div class="stream-dot warning"></div>
              <div class="stream-content">
                <div class="stream-title">High error rate detected</div>
                <div class="stream-desc">Metroomaa.com error rate is 1.12%</div>
              </div>
              <div class="stream-time">04:48:45</div>
            </div>
            <div class="stream-item">
              <div class="stream-dot success"></div>
              <div class="stream-content">
                <div class="stream-title">Outbox retried</div>
                <div class="stream-desc">12 failed events retried for 2 clients</div>
              </div>
              <div class="stream-time">04:47:21</div>
            </div>
            <div class="stream-item" style="border-bottom:none;">
              <div class="stream-dot info"></div>
              <div class="stream-content">
                <div class="stream-title">User admin logged in</div>
                <div class="stream-desc">sysop@buykori.app</div>
              </div>
              <div class="stream-time">04:45:10</div>
            </div>
          </div>
        </div>

        <div class="card">
          <div class="card-header">
            <h2 class="card-title">Signal Alerts</h2>
            <a href="#" class="view-all">View all</a>
          </div>
          <div style="padding:0">
            <div class="stream-item" style="align-items:center;">
              <svg style="width:20px;height:20px;color:#EF4444" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
              <div class="stream-content">
                <div class="stream-title">Content ID missing</div>
                <div class="stream-desc">Affects 1 client</div>
              </div>
              <div style="font-size:11px;font-weight:600;color:#EF4444;border:1px solid rgba(239,68,68,0.3);padding:2px 8px;border-radius:99px;margin-right:10px;">High</div>
              <div style="font-size:12px;color:var(--text-muted);">47.6% <svg style="width:12px;height:12px;display:inline;vertical-align:middle" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg></div>
            </div>
            <div class="stream-item" style="align-items:center;">
              <svg style="width:20px;height:20px;color:#F59E0B" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
              <div class="stream-content">
                <div class="stream-title">Email & phone missing</div>
                <div class="stream-desc">Affects 2 clients</div>
              </div>
              <div style="font-size:11px;font-weight:600;color:#F59E0B;border:1px solid rgba(245,158,11,0.3);padding:2px 8px;border-radius:99px;margin-right:10px;">Medium</div>
              <div style="font-size:12px;color:var(--text-muted);">23.1% <svg style="width:12px;height:12px;display:inline;vertical-align:middle" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg></div>
            </div>
            <div class="stream-item" style="align-items:center;">
              <svg style="width:20px;height:20px;color:#F59E0B" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg>
              <div class="stream-content">
                <div class="stream-title">Pixel missing funnel events</div>
                <div class="stream-desc">Affects 1 client</div>
              </div>
              <div style="font-size:11px;font-weight:600;color:#F59E0B;border:1px solid rgba(245,158,11,0.3);padding:2px 8px;border-radius:99px;margin-right:10px;">Medium</div>
              <div style="font-size:12px;color:var(--text-muted);">0.0% <svg style="width:12px;height:12px;display:inline;vertical-align:middle" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg></div>
            </div>
            <div class="stream-item" style="align-items:center;border-bottom:none">
              <svg style="width:20px;height:20px;color:#3B82F6" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" /></svg>
              <div class="stream-content">
                <div class="stream-title">Domain validation warning</div>
                <div class="stream-desc">Affects 1 domain</div>
              </div>
              <div style="font-size:11px;font-weight:600;color:#3B82F6;border:1px solid rgba(59,130,246,0.3);padding:2px 8px;border-radius:99px;margin-right:10px;">Low</div>
              <div style="font-size:12px;color:var(--text-muted);"><svg style="width:12px;height:12px;display:inline;vertical-align:middle" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg></div>
            </div>

            <div style="padding:16px 20px;border-top:1px solid var(--border);display:flex;justify-content:space-between;align-items:center;">
              <div style="font-size:13px;font-weight:600;color:#E2E8F0">System Status</div>
              <div style="font-size:12px;color:var(--success);display:flex;align-items:center;gap:6px;"><div style="width:8px;height:8px;border-radius:50%;background:var(--success)"></div> All systems operational</div>
              <svg style="width:14px;height:14px;color:var(--text-muted);" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7" /></svg>
            </div>
          </div>
        </div>
    \'''
'''
    content = content[:idx1] + new_audit + content[idx2:]

body_start = "    body = f'''"
body_end = "    return HTMLResponse(base_html(\"Dashboard\", body, msg, msg_type))"
if body_start in content and body_end in content:
    idx1 = content.find(body_start)
    idx2 = content.find(body_end)
    new_body = '''    body = f\'\'\'
    {header_html}
    {metrics_html}

    <div class="grid-layout">
      <div>{client_table}</div>
      <div>{audit_table}</div>
    </div>

    <!-- Footer Connection Status (Visual from Image 1) -->
    <div class="connection-footer" style="margin-top:24px;border-radius:12px;border:1px solid var(--border)">
      <div class="conn-item">
        <svg class="conn-icon" style="width:32px;height:32px;color:#1877F2" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.469h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.469h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>
        <div class="conn-info">
          <div class="conn-title">Meta CAPI</div>
          <div class="conn-status">Connected &nbsp;<span style="color:#64748B">Events: 432,112</span></div>
        </div>
      </div>
      <div style="width:1px;background:rgba(255,255,255,0.1);height:32px;margin:0 10px;"></div>
      <div class="conn-item">
        <svg class="conn-icon" style="width:32px;height:32px;color:#FFF" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93v7.2c0 1.63-.51 3.25-1.47 4.55-1.07 1.45-2.71 2.45-4.48 2.82-1.8.38-3.7-.02-5.26-.98-1.55-.95-2.65-2.52-3.1-4.26-.46-1.74-.2-3.64.71-5.18 1.13-1.9 3.09-3.23 5.3-3.5 1.05-.13 2.11-.08 3.14.15V13c-.39-.12-.8-.17-1.22-.17-1.12.03-2.22.45-3.03 1.25-.8.78-1.26 1.87-1.27 2.99 0 1.11.45 2.21 1.25 3.01.81.82 1.96 1.27 3.1 1.25 1.14-.02 2.26-.51 3.05-1.33.82-.84 1.28-1.98 1.3-3.14V.02z"/></svg>
        <div class="conn-info">
          <div class="conn-title">TikTok Events API</div>
          <div class="conn-status">Connected &nbsp;<span style="color:#64748B">Events: 321,417</span></div>
        </div>
      </div>
      <div style="width:1px;background:rgba(255,255,255,0.1);height:32px;margin:0 10px;"></div>
      <div class="conn-item">
        <svg class="conn-icon" style="width:32px;height:32px;color:#F9AB00" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor"><path d="M4 18h4V6H4v12zm6 0h4V10h-4v8zm6-12v12h4V6h-4z"/></svg>
        <div class="conn-info">
          <div class="conn-title">GA4 Measurement</div>
          <div class="conn-status">Connected &nbsp;<span style="color:#64748B">Events: 298,771</span></div>
        </div>
      </div>
      <div style="width:1px;background:rgba(255,255,255,0.1);height:32px;margin:0 10px;"></div>
      <div class="conn-item">
        <div class="conn-icon" style="width:32px;height:32px;background:#0077B5;border-radius:4px;display:flex;align-items:center;justify-content:center;color:white;font-weight:bold;font-size:18px;">in</div>
        <div class="conn-info">
          <div class="conn-title">LinkedIn API</div>
          <div class="conn-status">Connected &nbsp;<span style="color:#64748B">Events: 54,982</span></div>
        </div>
      </div>
    </div>

    <div style="margin-top:40px">
      {add_form}
    </div>
    \'\'\'
'''
    content = content[:idx1] + new_body + content[idx2:]

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Redesign applied successfully.")
