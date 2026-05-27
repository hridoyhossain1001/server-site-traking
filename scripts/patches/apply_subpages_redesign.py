import re

file_path = "app/routers/admin.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Update Clients Route Stats HTML
clients_stats_old = '''    # Stats bar
    stats_html = f"""
    <div class="page-header">
      <div>
        <h1 class="page-title">Client Management</h1>
        <p class="page-sub">Manage all CAPI client integrations and monthly quotas.</p>
      </div>
    </div>
    <div class="metrics-grid" style="grid-template-columns: repeat(3, 1fr); margin-bottom: 24px;">
      <div class="metric-card">
        <div class="metric-header"><span class="metric-title">Total Clients</span><span class="metric-icon">👥</span></div>
        <div class="metric-value">{len(clients)}</div>
      </div>
      <div class="metric-card">
        <div class="metric-header"><span class="metric-title">Active</span><span class="metric-icon">✅</span></div>
        <div class="metric-value" style="color:#34d399">{active_count}</div>
      </div>
      <div class="metric-card">
        <div class="metric-header"><span class="metric-title">Inactive</span><span class="metric-icon">⛔</span></div>
        <div class="metric-value" style="color:#f87171">{inactive_count}</div>
      </div>
    </div>
    """'''

clients_stats_new = '''    # Stats bar
    stats_html = f"""
    <div class="page-header">
      <div>
        <h1 class="page-title">Client Management</h1>
        <p class="page-sub">Manage all CAPI client integrations and monthly quotas.</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-primary" onclick="window.location.href='/api/v1/admin'">
          <svg style="width:16px;height:16px" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/></svg> Add Client
        </button>
      </div>
    </div>
    <div class="metrics-grid" style="grid-template-columns: repeat(3, 1fr); margin-bottom: 24px;">
      <div class="metric-card">
        <div class="metric-header">
          <div class="m-icon bg-blue"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"/></svg></div>
          <span class="m-title">Total Clients</span>
        </div>
        <div class="metric-value">{len(clients)}</div>
      </div>
      <div class="metric-card">
        <div class="metric-header">
          <div class="m-icon bg-purple"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg></div>
          <span class="m-title">Active</span>
        </div>
        <div class="metric-value" style="color:#34d399">{active_count}</div>
      </div>
      <div class="metric-card">
        <div class="metric-header">
          <div class="m-icon bg-red"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg></div>
          <span class="m-title">Inactive</span>
        </div>
        <div class="metric-value" style="color:#f87171">{inactive_count}</div>
      </div>
    </div>
    """'''
if clients_stats_old in content:
    content = content.replace(clients_stats_old, clients_stats_new)

# 2. Update Logs Route Stats HTML
logs_stats_old = '''    # Stats
    header_html = f"""
    <div class="page-header">
      <div>
        <h1 class="page-title">API Event Logs</h1>
        <p class="page-sub">Real-time event processing history and error tracking.</p>
      </div>
    </div>
    <div class="metrics-grid" style="margin-bottom:24px">
      <div class="metric-card">
        <div class="metric-header"><span class="metric-title">Success (24h)</span><span class="metric-icon">✅</span></div>
        <div class="metric-value" style="color:#34d399">{events_today:,}</div>
      </div>
      <div class="metric-card">
        <div class="metric-header"><span class="metric-title">Failed (24h)</span><span class="metric-icon">❌</span></div>
        <div class="metric-value" style="color:#f87171">{failed_today:,}</div>
      </div>
      <div class="metric-card">
        <div class="metric-header"><span class="metric-title">Total (24h)</span><span class="metric-icon">📊</span></div>
        <div class="metric-value">{total:,}</div>
      </div>
      <div class="metric-card">
        <div class="metric-header"><span class="metric-title">Pending Retries</span><span class="metric-icon">🔄</span></div>
        <div class="metric-value" style="color:#facc15">{retries}</div>
      </div>
    </div>
    """'''

logs_stats_new = '''    # Stats
    header_html = f"""
    <div class="page-header">
      <div>
        <h1 class="page-title">API Event Logs</h1>
        <p class="page-sub">Real-time event processing history and error tracking.</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-outline" onclick="window.location.reload()"><svg style="width:16px;height:16px" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg> Refresh</button>
      </div>
    </div>
    <div class="metrics-grid" style="margin-bottom:24px">
      <div class="metric-card">
        <div class="metric-header">
          <div class="m-icon bg-purple"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" /></svg></div>
          <span class="m-title">Success (24h)</span>
        </div>
        <div class="metric-value" style="color:#34d399">{events_today:,}</div>
      </div>
      <div class="metric-card">
        <div class="metric-header">
          <div class="m-icon bg-red"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" /></svg></div>
          <span class="m-title">Failed (24h)</span>
        </div>
        <div class="metric-value" style="color:#f87171">{failed_today:,}</div>
      </div>
      <div class="metric-card">
        <div class="metric-header">
          <div class="m-icon bg-blue"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 7h8m0 0v8m0-8l-8 8-4-4-6 6" /></svg></div>
          <span class="m-title">Total (24h)</span>
        </div>
        <div class="metric-value">{total:,}</div>
      </div>
      <div class="metric-card">
        <div class="metric-header">
          <div class="m-icon bg-indigo"><svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg></div>
          <span class="m-title">Pending Retries</span>
        </div>
        <div class="metric-value" style="color:#facc15">{retries}</div>
      </div>
    </div>
    """'''
if logs_stats_old in content:
    content = content.replace(logs_stats_old, logs_stats_new)

# 3. Fix client buttons
# In clients loop
import re
content = re.sub(r'class="btn-sm btn-info"', r'class="btn btn-outline"', content)
content = re.sub(r'class="btn-sm btn-danger"', r'class="btn btn-outline" style="color:var(--danger);border-color:var(--danger-bg);background:rgba(239,68,68,0.05)"', content)
content = re.sub(r'class="btn-sm btn-primary"', r'class="btn btn-primary"', content)

# Update badges
content = re.sub(r'class="badge badge-healthy"', r'class="status-badge status-healthy"', content)
content = re.sub(r'class="badge badge-degraded"', r'class="status-badge status-degraded"', content)
content = re.sub(r'class="badge badge-warning"', r'class="status-badge status-warning"', content)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Subpages redesign applied.")
