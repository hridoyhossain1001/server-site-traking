#!/usr/bin/env python3
"""
Safe UI redesign script for admin.py
Replaces only STYLE and base_html HTML template - no logic changes
"""
import re

with open("app/routers/admin.py", "r", encoding="utf-8") as f:
    content = f.read()

# ─── NEW STYLE ────────────────────────────────────────────────────────────────
NEW_STYLE = '''STYLE = """
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
  :root {
    --bg-main: #060d1f;
    --bg-sidebar: #080f22;
    --bg-card: #0d1426;
    --bg-card-hover: #111b30;
    --bg-soft: #162038;
    --border: rgba(148, 163, 184, 0.12);
    --border-bright: rgba(148, 163, 184, 0.22);
    --primary: #2563eb;
    --primary-hover: #3b82f6;
    --primary-glow: rgba(37, 99, 235, 0.25);
    --violet: #7c3aed;
    --violet-soft: #8b5cf6;
    --cyan: #06b6d4;
    --text-main: #f1f5f9;
    --text-muted: #64748b;
    --text-subtle: #94a3b8;
    --success: #10b981;
    --danger: #ef4444;
    --warning: #f59e0b;
    --info: #3b82f6;
    --sidebar-width: 260px;
    --header-height: 64px;
    --radius: 12px;
    --radius-sm: 8px;
  }
  * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', system-ui, sans-serif; }
  html { font-size: 14px; }
  body {
    background: var(--bg-main);
    background-image:
      radial-gradient(ellipse 80% 50% at 20% -10%, rgba(37,99,235,0.12), transparent),
      radial-gradient(ellipse 50% 40% at 80% 80%, rgba(124,58,237,0.07), transparent);
    color: var(--text-main);
    min-height: 100vh;
    display: flex;
    overflow-x: hidden;
  }
  ::-webkit-scrollbar { width: 5px; height: 5px; }
  ::-webkit-scrollbar-track { background: transparent; }
  ::-webkit-scrollbar-thumb { background: rgba(148,163,184,0.15); border-radius: 99px; }
  ::-webkit-scrollbar-thumb:hover { background: rgba(148,163,184,0.28); }
  .sidebar {
    width: var(--sidebar-width);
    background: var(--bg-sidebar);
    border-right: 1px solid var(--border);
    display: flex;
    flex-direction: column;
    position: fixed;
    height: 100vh;
    left: 0; top: 0;
    z-index: 50;
    transition: transform 0.25s ease;
  }
  .brand {
    padding: 20px 18px;
    font-size: 16px;
    font-weight: 800;
    color: #fff;
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    gap: 10px;
    letter-spacing: -0.3px;
  }
  .brand-mark {
    width: 34px; height: 34px;
    border-radius: 10px;
    background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
    display: inline-flex; align-items: center; justify-content: center;
    color: #fff; font-weight: 900; font-size: 15px;
    box-shadow: 0 4px 16px rgba(37, 99, 235, 0.35);
    flex-shrink: 0;
  }
  .brand-text { display: flex; flex-direction: column; line-height: 1.15; min-width: 0; }
  .brand-name { white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .brand span.brand-sub { font-weight: 400; color: var(--text-muted); font-size: 11px; display: block; margin-top: 2px; }
  .nav-menu { flex: 1; padding: 8px 10px; overflow-y: auto; }
  .nav-item {
    display: flex; align-items: center; gap: 10px;
    padding: 10px 14px; margin-bottom: 2px;
    color: var(--text-subtle); font-size: 13.5px; font-weight: 500;
    text-decoration: none; border-radius: var(--radius-sm); border: 1px solid transparent;
    transition: all 0.18s ease;
    position: relative;
  }
  .nav-item svg { width: 17px; height: 17px; flex-shrink: 0; opacity: 0.75; transition: opacity 0.18s; }
  .nav-item:hover { background: rgba(148,163,184,0.07); color: #fff; }
  .nav-item:hover svg { opacity: 1; }
  .nav-item.active {
    background: linear-gradient(90deg, rgba(37,99,235,0.18) 0%, rgba(124,58,237,0.12) 100%);
    color: #fff;
    border-color: rgba(99,163,250,0.2);
  }
  .nav-item.active svg { opacity: 1; color: #60a5fa; }
  .nav-item.active::before {
    content: '';
    position: absolute; left: 0; top: 20%; bottom: 20%;
    width: 3px; border-radius: 0 3px 3px 0;
    background: linear-gradient(180deg, #3b82f6, #7c3aed);
  }
  .sidebar-bottom { padding: 10px 10px 16px; border-top: 1px solid var(--border); }
  .main-wrapper {
    flex: 1;
    margin-left: var(--sidebar-width);
    display: flex;
    flex-direction: column;
    min-height: 100vh;
  }
  .topbar {
    height: var(--header-height);
    background: rgba(6, 13, 31, 0.85);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0 28px;
    position: sticky; top: 0; z-index: 40;
  }
  .search-box {
    background: rgba(13, 20, 38, 0.9);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    padding: 7px 14px;
    width: 300px;
    display: flex; align-items: center; gap: 8px;
    transition: border-color 0.2s;
  }
  .search-box:focus-within { border-color: rgba(99,163,250,0.4); }
  .search-box input { background: none; border: none; outline: none; color: #fff; font-size: 13px; width: 100%; }
  .search-box input::placeholder { color: var(--text-muted); }
  .search-box svg { width: 15px; height: 15px; color: var(--text-muted); flex-shrink: 0; }
  .search-kbd {
    background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 4px; padding: 2px 6px; font-size: 10px; color: var(--text-muted);
    font-family: ui-monospace, monospace; white-space: nowrap;
  }
  .topbar-right { display: flex; align-items: center; gap: 16px; }
  .topbar-divider { width: 1px; height: 28px; background: var(--border); }
  .env-badge {
    background: rgba(16, 185, 129, 0.12);
    color: #34d399; border: 1px solid rgba(16, 185, 129, 0.25);
    padding: 4px 10px; border-radius: 99px; font-size: 10.5px; font-weight: 700;
    letter-spacing: 0.8px; display: flex; align-items: center; gap: 5px;
  }
  .env-badge::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: #34d399; animation: pulse-dot 2s infinite; }
  @keyframes pulse-dot { 0%,100%{opacity:1;} 50%{opacity:0.35;} }
  .topbar-icon-btn {
    width: 34px; height: 34px;
    display: flex; align-items: center; justify-content: center;
    background: rgba(255,255,255,0.04);
    border: 1px solid var(--border);
    border-radius: var(--radius-sm);
    color: var(--text-subtle); cursor: pointer;
    position: relative; transition: all 0.18s;
    text-decoration: none;
  }
  .topbar-icon-btn:hover { background: rgba(255,255,255,0.08); color: #fff; border-color: var(--border-bright); }
  .topbar-icon-btn svg { width: 16px; height: 16px; }
  .notif-badge {
    position: absolute; top: -3px; right: -3px;
    min-width: 16px; height: 16px;
    background: var(--danger);
    border: 2px solid var(--bg-main);
    border-radius: 99px; font-size: 9px; font-weight: 700;
    display: flex; align-items: center; justify-content: center;
    color: #fff; padding: 0 3px;
  }
  .user-profile { display: flex; align-items: center; gap: 10px; cursor: pointer; }
  .user-avatar {
    width: 34px; height: 34px;
    background: linear-gradient(135deg, #2563eb, #7c3aed);
    border-radius: 50%;
    display: flex; align-items: center; justify-content: center;
    font-size: 13px; font-weight: 700; color: #fff;
    border: 2px solid rgba(255,255,255,0.1);
    flex-shrink: 0;
  }
  .user-info { display: flex; flex-direction: column; }
  .user-info .name { font-size: 13px; font-weight: 600; color: #fff; line-height: 1.2; }
  .user-info .role { font-size: 11px; color: var(--text-muted); }
  .mobile-menu-btn {
    display: none; width: 40px; height: 40px;
    align-items: center; justify-content: center;
    border: 1px solid var(--border); border-radius: var(--radius-sm);
    background: rgba(13,20,38,0.9); color: #fff; cursor: pointer;
  }
  .sidebar-overlay {
    display: none; position: fixed; inset: 0;
    background: rgba(2, 6, 23, 0.7); z-index: 45;
  }
  .sidebar-overlay.open { display: block; }
  .content { padding: 28px 32px; }
  .page-header { display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 24px; }
  .page-title { font-size: 22px; font-weight: 700; color: #fff; margin-bottom: 4px; letter-spacing: -0.3px; }
  .page-sub { font-size: 13px; color: var(--text-muted); }
  .header-actions { display: flex; gap: 10px; }
  .btn {
    padding: 8px 16px; border-radius: var(--radius-sm); font-size: 13px; font-weight: 600;
    cursor: pointer; transition: all 0.18s; display: inline-flex; align-items: center;
    gap: 7px; border: 1px solid transparent; white-space: nowrap; text-decoration: none;
  }
  .btn-outline { background: rgba(255,255,255,0.04); border-color: var(--border-bright); color: var(--text-subtle); }
  .btn-outline:hover { background: rgba(255,255,255,0.08); color: #fff; }
  .btn-primary { background: linear-gradient(135deg, #2563eb, #1d4ed8); color: #fff; box-shadow: 0 2px 12px rgba(37,99,235,0.3); }
  .btn-primary:hover { background: linear-gradient(135deg, #3b82f6, #2563eb); box-shadow: 0 4px 20px rgba(59,130,246,0.4); transform: translateY(-1px); }
  .metrics-grid { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 24px; }
  .metric-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius);
    padding: 20px;
    position: relative; overflow: hidden;
    transition: border-color 0.2s, box-shadow 0.2s;
  }
  .metric-card:hover { border-color: var(--border-bright); box-shadow: 0 4px 24px rgba(0,0,0,0.2); }
  .metric-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--primary), var(--violet-soft));
    opacity: 0;
    transition: opacity 0.2s;
  }
  .metric-card:hover::before { opacity: 1; }
  .metric-header { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 14px; }
  .metric-title { font-size: 11.5px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.7px; line-height: 1.3; }
  .metric-icon {
    width: 34px; height: 34px;
    background: rgba(37,99,235,0.1);
    border-radius: var(--radius-sm);
    display: flex; align-items: center; justify-content: center;
    color: #60a5fa;
    border: 1px solid rgba(37,99,235,0.2);
    flex-shrink: 0;
  }
  .metric-icon svg { width: 16px; height: 16px; }
  .metric-icon.icon-danger { background: rgba(239,68,68,0.1); border-color: rgba(239,68,68,0.2); color: #f87171; }
  .metric-icon.icon-success { background: rgba(16,185,129,0.1); border-color: rgba(16,185,129,0.2); color: #34d399; }
  .metric-icon.icon-warning { background: rgba(245,158,11,0.1); border-color: rgba(245,158,11,0.2); color: #fbbf24; }
  .metric-value { font-size: 26px; font-weight: 800; color: #fff; margin-bottom: 10px; line-height: 1; letter-spacing: -0.5px; }
  .metric-trend { display: flex; align-items: center; gap: 7px; font-size: 12px; color: var(--text-muted); }
  .metric-sparkline { margin-top: 14px; height: 36px; }
  .trend-up { background: rgba(16,185,129,0.12); color: #34d399; padding: 2px 7px; border-radius: 99px; font-weight: 600; display: inline-flex; align-items: center; gap: 3px; font-size: 11.5px; }
  .trend-down { background: rgba(239,68,68,0.12); color: #f87171; padding: 2px 7px; border-radius: 99px; font-weight: 600; display: inline-flex; align-items: center; gap: 3px; font-size: 11.5px; }
  .trend-neutral { background: rgba(148,163,184,0.1); color: var(--text-subtle); padding: 2px 7px; border-radius: 99px; font-weight: 600; display: inline-flex; align-items: center; gap: 3px; font-size: 11.5px; }
  .layout-grid { display: grid; grid-template-columns: 2fr 1fr; gap: 20px; align-items: start; }
  .card { background: var(--bg-card); border: 1px solid var(--border); border-radius: var(--radius); overflow: hidden; }
  .card-header { padding: 18px 20px; border-bottom: 1px solid var(--border); display: flex; justify-content: space-between; align-items: center; }
  .card-title { font-size: 15px; font-weight: 600; color: #fff; display: flex; align-items: center; gap: 8px; }
  .card-title svg { width: 16px; height: 16px; color: #60a5fa; }
  .card-actions { display: flex; gap: 6px; }
  .card-action-btn {
    width: 30px; height: 30px;
    display: flex; align-items: center; justify-content: center;
    background: rgba(255,255,255,0.04); border: 1px solid var(--border);
    border-radius: 6px; color: var(--text-muted); cursor: pointer;
    transition: all 0.18s;
  }
  .card-action-btn:hover { background: rgba(255,255,255,0.08); color: #fff; }
  .card-action-btn svg { width: 13px; height: 13px; }
  .view-all-link { font-size: 12px; color: #60a5fa; text-decoration: none; font-weight: 500; white-space: nowrap; }
  .view-all-link:hover { color: #93c5fd; }
  .table-responsive { width: 100%; overflow-x: auto; }
  table { width: 100%; border-collapse: collapse; }
  th { text-align: left; padding: 12px 20px; font-size: 10.5px; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.7px; border-bottom: 1px solid var(--border); background: rgba(255,255,255,0.015); white-space: nowrap; }
  td { padding: 14px 20px; font-size: 13px; border-bottom: 1px solid rgba(255,255,255,0.03); vertical-align: middle; }
  tr { transition: background 0.15s; }
  tr:hover td { background: rgba(255,255,255,0.025); }
  tr:last-child td { border-bottom: none; }
  .client-name { font-weight: 600; color: #fff; line-height: 1.2; }
  .client-sub { font-size: 11.5px; color: var(--text-muted); margin-top: 2px; font-family: ui-monospace, monospace; }
  .code-text { font-family: ui-monospace, SFMono-Regular, Menlo, Consolas, monospace; font-size: 12px; color: var(--text-muted); }
  .badge { padding: 3px 9px; border-radius: 99px; font-size: 11px; font-weight: 600; display: inline-flex; align-items: center; gap: 5px; border: 1px solid transparent; white-space: nowrap; }
  .badge-healthy { background: rgba(16,185,129,0.1); color: #34d399; border-color: rgba(16,185,129,0.2); }
  .badge-degraded { background: rgba(239,68,68,0.1); color: #f87171; border-color: rgba(239,68,68,0.2); }
  .badge-warning { background: rgba(245,158,11,0.1); color: #fbbf24; border-color: rgba(245,158,11,0.2); }
  .badge-healthy::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: #34d399; }
  .badge-degraded::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: #f87171; }
  .badge-warning::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: #fbbf24; }
  .log-list { padding: 0; }
  .log-item {
    display: flex; align-items: flex-start; gap: 12px;
    padding: 12px 20px; border-bottom: 1px solid rgba(255,255,255,0.03);
    font-size: 12px; transition: background 0.15s;
  }
  .log-item:hover { background: rgba(255,255,255,0.02); }
  .log-item:last-child { border-bottom: none; }
  .log-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; margin-top: 3px; }
  .log-dot.info { background: #34d399; box-shadow: 0 0 6px rgba(52,211,153,0.5); }
  .log-dot.warn { background: #fbbf24; box-shadow: 0 0 6px rgba(251,191,36,0.5); }
  .log-dot.err { background: #f87171; box-shadow: 0 0 6px rgba(248,113,113,0.5); }
  .log-content { flex: 1; min-width: 0; }
  .log-msg { color: #cbd5e1; line-height: 1.45; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
  .log-msg b { color: #fff; font-weight: 600; }
  .log-meta { color: var(--text-muted); font-size: 11px; margin-top: 2px; }
  .log-time { font-family: ui-monospace, monospace; color: var(--text-muted); font-size: 11px; flex-shrink: 0; }
  .log-tag { font-family: ui-monospace, monospace; font-weight: 600; }
  .log-tag.info { color: #34d399; }
  .log-tag.warn { color: #facc15; }
  .log-tag.err { color: #f87171; }
  .api-key-cell {
    font-family: ui-monospace, Menlo, monospace; font-size: 11.5px; color: #94a3b8;
    background: rgba(0,0,0,0.25); border: 1px solid var(--border);
    padding: 4px 8px; border-radius: 6px;
    display: inline-flex; align-items: center; justify-content: space-between;
    gap: 8px; width: 100%; max-width: 180px;
  }
  .copy-icon { background: none; border: none; color: var(--text-muted); cursor: pointer; display: flex; align-items: center; transition: color 0.15s; padding: 0; }
  .copy-icon:hover { color: #fff; }
  .btn-sm {
    padding: 5px 11px; font-size: 11.5px; border-radius: 6px;
    border: 1px solid transparent; cursor: pointer; font-weight: 600;
    display: inline-flex; align-items: center; justify-content: center;
    gap: 5px; transition: all 0.18s; text-decoration: none; white-space: nowrap;
  }
  .btn-info { background: rgba(59,130,246,0.1); color: #60a5fa; border-color: rgba(59,130,246,0.2); }
  .btn-info:hover { background: rgba(59,130,246,0.2); color: #93c5fd; border-color: rgba(59,130,246,0.35); }
  .btn-danger { background: rgba(239,68,68,0.1); color: #f87171; border-color: rgba(239,68,68,0.2); }
  .btn-danger:hover { background: rgba(239,68,68,0.2); color: #fca5a5; border-color: rgba(239,68,68,0.35); }
  .btn-success { background: rgba(16,185,129,0.1); color: #34d399; border-color: rgba(16,185,129,0.2); }
  .btn-success:hover { background: rgba(16,185,129,0.2); color: #6ee7b7; }
  .alert { padding: 12px 16px; border-radius: var(--radius-sm); margin-bottom: 20px; font-size: 13px; font-weight: 500; display: flex; align-items: center; gap: 10px; }
  .alert-success { background: rgba(16,185,129,0.08); border: 1px solid rgba(16,185,129,0.2); color: #34d399; }
  .alert-error { background: rgba(239,68,68,0.08); border: 1px solid rgba(239,68,68,0.2); color: #f87171; }
  .form-group { margin-bottom: 16px; }
  .form-group label { display: block; font-size: 11.5px; color: var(--text-subtle); margin-bottom: 6px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
  .form-group input[type=text],
  .form-group input[type=password],
  .form-group input[type=number] {
    width: 100%; padding: 9px 12px;
    background: rgba(0,0,0,0.2); border: 1px solid var(--border);
    border-radius: var(--radius-sm); color: #fff; font-size: 13px;
    outline: none; transition: border-color 0.18s, box-shadow 0.18s;
  }
  .form-group input:focus { border-color: rgba(99,163,250,0.5); box-shadow: 0 0 0 3px rgba(37,99,235,0.12); }
  .form-group select {
    width: 100%; padding: 9px 12px;
    background: rgba(0,0,0,0.2); border: 1px solid var(--border);
    border-radius: var(--radius-sm); color: #fff; font-size: 13px;
    outline: none;
  }
  .hint { font-size: 11px; color: var(--text-muted); margin-top: 4px; line-height: 1.4; }
  .btn-full { width: 100%; justify-content: center; padding: 10px; }
  .instr-box {
    background: rgba(0,0,0,0.3); border: 1px solid var(--border);
    border-radius: var(--radius-sm); padding: 14px; font-family: ui-monospace, monospace;
    font-size: 12px; color: #dbeafe; white-space: pre-wrap; word-break: break-all; margin-top: 8px;
    line-height: 1.6;
  }
  .copy-btn {
    background: linear-gradient(135deg, #4f46e5, #7c3aed); color: #fff;
    border: none; border-radius: 6px; padding: 5px 12px;
    font-size: 11px; font-weight: 600; cursor: pointer; float: right; margin-top: 12px; margin-right: 8px;
    transition: opacity 0.2s;
  }
  .copy-btn:hover { opacity: 0.85; }
  .icon {
    width: 30px; height: 30px;
    background: rgba(99,102,241,0.12); border: 1px solid rgba(129,140,248,0.2);
    border-radius: var(--radius-sm); display: inline-flex; align-items: center;
    justify-content: center; font-size: 14px; margin-right: 6px; vertical-align: middle;
  }
  .left-col { flex: 1; }
  .right-col { width: 100%; max-width: 400px; }
  .tabs { display: flex; gap: 4px; margin-bottom: 20px; border-bottom: 1px solid var(--border); padding-bottom: 0; overflow-x: auto; }
  .tab-btn {
    background: transparent; border: none; border-bottom: 2px solid transparent;
    color: var(--text-muted); font-size: 13px; font-weight: 600;
    cursor: pointer; padding: 10px 14px; border-radius: 0;
    transition: all 0.18s; white-space: nowrap; margin-bottom: -1px;
  }
  .tab-btn:hover { color: #fff; }
  .tab-btn.active { color: #fff; border-bottom-color: #3b82f6; }
  .tab-content { display: none; animation: fadeIn 0.25s ease; }
  .tab-content.active { display: block; }
  @keyframes fadeIn { from { opacity: 0; transform: translateY(4px); } to { opacity: 1; transform: translateY(0); } }
  @media (max-width: 1200px) {
    .metrics-grid { grid-template-columns: repeat(2, 1fr); }
  }
  @media (max-width: 1024px) {
    .layout-grid { grid-template-columns: 1fr; }
  }
  @media (max-width: 768px) {
    .sidebar { transform: translateX(-105%); }
    .sidebar.open { transform: translateX(0); box-shadow: 0 0 60px rgba(0,0,0,0.6); }
    .main-wrapper { margin-left: 0; }
    .metrics-grid { grid-template-columns: 1fr; }
    .search-box { display: none; }
    .mobile-menu-btn { display: inline-flex; }
    .topbar { padding: 0 16px; gap: 10px; }
    .topbar-right { gap: 8px; }
    .user-info, .topbar-right > .topbar-divider { display: none !important; }
    .content { padding: 18px 16px 32px; }
    .page-header { flex-direction: column; align-items: flex-start; gap: 12px; }
    .header-actions { width: 100%; overflow-x: auto; padding-bottom: 4px; }
  }
</style>
"""'''

# ─── NEW BASE_HTML SIDEBAR + TOPBAR ──────────────────────────────────────────
OLD_SIDEBAR_TOPBAR = '''  <div class="sidebar-overlay" id="admin-sidebar-overlay" onclick="toggleAdminSidebar()"></div>

  <!-- Sidebar -->
  <aside class="sidebar" id="admin-sidebar">
    <div class="brand">
      <span class="brand-mark">B</span>
      <span class="brand-text">Buykori AdSync
        <span>Enterprise Admin</span>
      </span>
    </div>
    <div class="nav-menu">
      <a href="/api/v1/admin" class="nav-item {nav_active("dashboard")}">
        <span style="font-size:16px">🎛️</span> Dashboard
      </a>
      <a href="/api/v1/admin/clients" class="nav-item {nav_active("clients")}">
        <span style="font-size:16px">👥</span> Clients
      </a>
      <a href="/api/v1/admin/logs" class="nav-item {nav_active("logs")}">
        <span style="font-size:16px">📡</span> API Logs
      </a>
      <a href="/api/v1/admin/settings" class="nav-item {nav_active("settings")}">
        <span style="font-size:16px">⚙️</span> Settings
      </a>
    </div>
    <div class="sidebar-bottom">
      <a href="#" class="nav-item" onclick="alert(\'Support Ticket\')">
        <span style="font-size:16px">🎧</span> Support Ticket
      </a>
      <a href="#" class="nav-item" onclick="if(confirm(\'Log out?\')) window.location=\'/api/v1/admin\'">
        <span style="font-size:16px">🚪</span> Log Out
      </a>
    </div>
  </aside>

  <!-- Main Content Area -->
  <div class="main-wrapper">
    <!-- Topbar -->
    <header class="topbar">
      <button class="mobile-menu-btn" type="button" onclick="toggleAdminSidebar()" aria-label="Open menu">=</button>
      <div class="search-box">
        <span>🔍</span>
        <input type="text" placeholder="Search events, clients, IPs...">
      </div>
      <div class="topbar-right">
        <div style="display:flex;align-items:center;gap:12px;border-right:1px solid var(--border);padding-right:20px;">
          <span style="font-size:12px;font-weight:600;color:var(--text-muted)">ENV</span>
          <span class="env-badge">PRODUCTION</span>
        </div>
        <button class="icon-btn">
          🔔 <span class="notification-dot"></span>
        </button>
        <button class="icon-btn">❓</button>
        <div class="user-profile">
          <div class="user-avatar" style="background:#2d3748 url(\'data:image/svg+xml,%3Csvg xmlns=%22http://www.w3.org/2000/svg%22 fill=%22none%22 viewBox=%220 0 24 24%22 stroke=%22%2394a3b8%22%3E%3Cpath stroke-linecap=%22round%22 stroke-linejoin=%22round%22 stroke-width=%221.5%22 d=%22M15.75 6a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0zM4.501 20.118a7.5 7.5 0 0114.998 0A17.933 17.933 0 0112 21.75c-2.676 0-5.216-.584-7.499-1.632z%22/%3E%3C/svg%3E\') no-repeat center center / 60%;">&nbsp;</div>
          <div class="user-info">
            <span class="name">Admin Panel</span>
            <span class="role">sysop@buykori.app</span>
          </div>
        </div>
      </div>
    </header>'''

NEW_SIDEBAR_TOPBAR = '''  <div class="sidebar-overlay" id="admin-sidebar-overlay" onclick="toggleAdminSidebar()"></div>

  <!-- Sidebar -->
  <aside class="sidebar" id="admin-sidebar">
    <div class="brand">
      <span class="brand-mark">B</span>
      <span class="brand-text">
        <span class="brand-name">Buykori AdSync</span>
        <span class="brand-sub">Enterprise Admin</span>
      </span>
    </div>
    <div class="nav-menu">
      <a href="/api/v1/admin" class="nav-item {nav_active("dashboard")}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
        Overview
      </a>
      <a href="/api/v1/admin/clients" class="nav-item {nav_active("clients")}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
        Clients
      </a>
      <a href="/api/v1/admin/logs" class="nav-item {nav_active("logs")}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
        API Logs
      </a>
      <a href="/api/v1/admin/settings" class="nav-item {nav_active("settings")}">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
        Settings
      </a>
    </div>
    <div class="sidebar-bottom">
      <a href="#" class="nav-item" onclick="alert(\'Support: contact@buykori.app\')">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        Support
      </a>
      <a href="#" class="nav-item" onclick="if(confirm(\'Log out?\')) window.location=\'/api/v1/admin\'">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>
        Log Out
      </a>
    </div>
  </aside>

  <!-- Main Content Area -->
  <div class="main-wrapper">
    <!-- Topbar -->
    <header class="topbar">
      <button class="mobile-menu-btn" type="button" onclick="toggleAdminSidebar()" aria-label="Open menu">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><line x1="3" y1="6" x2="21" y2="6"/><line x1="3" y1="12" x2="21" y2="12"/><line x1="3" y1="18" x2="21" y2="18"/></svg>
      </button>
      <div class="search-box">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>
        <input type="text" placeholder="Search clients, events, IPs..." id="topbar-search">
        <span class="search-kbd">⌘K</span>
      </div>
      <div class="topbar-right">
        <span class="env-badge">PRODUCTION</span>
        <div class="topbar-divider"></div>
        <button class="topbar-icon-btn" title="Notifications" onclick="void(0)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.73 21a2 2 0 0 1-3.46 0"/></svg>
          <span class="notif-badge">6</span>
        </button>
        <button class="topbar-icon-btn" title="Help" onclick="void(0)">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.75" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        </button>
        <div class="user-profile">
          <div class="user-avatar">AH</div>
          <div class="user-info">
            <span class="name">Admin Panel</span>
            <span class="role">sysop@buykori.app</span>
          </div>
        </div>
      </div>
    </header>'''

# ─── APPLY CHANGES ────────────────────────────────────────────────────────────
# Find and replace STYLE block
old_style_start = 'STYLE = """\n<style>\n  @import url(\'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap\');'
old_style_end = '  @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }\n\n</style>\n"""'

if old_style_start in content and old_style_end in content:
    start_idx = content.index(old_style_start)
    end_idx = content.index(old_style_end) + len(old_style_end)
    content = content[:start_idx] + NEW_STYLE + content[end_idx:]
    print("✅ STYLE block replaced successfully")
else:
    print("❌ Could not find STYLE block - checking content...")
    if 'STYLE = """' in content:
        print("  Found STYLE = \"\"\" but old_style_start not found")
    else:
        print("  STYLE variable not found at all!")

# Replace sidebar+topbar HTML
if OLD_SIDEBAR_TOPBAR in content:
    content = content.replace(OLD_SIDEBAR_TOPBAR, NEW_SIDEBAR_TOPBAR)
    print("✅ Sidebar + Topbar HTML replaced successfully")
else:
    print("❌ Could not find sidebar/topbar HTML to replace")
    # Try to find partial match
    if 'sidebar-overlay' in content:
        print("  Found sidebar-overlay reference")

# Write back
with open("app/routers/admin.py", "w", encoding="utf-8") as f:
    f.write(content)

# Verify syntax
import ast
try:
    ast.parse(content)
    print("✅ Python syntax OK!")
except SyntaxError as e:
    print(f"❌ Syntax error: {e}")
    print("Rolling back...")
    import subprocess
    subprocess.run(["git", "checkout", "HEAD", "--", "app/routers/admin.py"])
    print("Rolled back to original")
