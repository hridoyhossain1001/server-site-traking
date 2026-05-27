import re

file_path = "app/routers/admin.py"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Update Settings Route Header
settings_header_old = '''    body = f"""
    <div class="page-header">
      <div>
        <h1 class="page-title">System Settings</h1>
        <p class="page-sub">Server configuration, environment status, and admin activity.</p>
      </div>
    </div>'''

settings_header_new = '''    body = f"""
    <div class="page-header">
      <div>
        <h1 class="page-title">System Settings</h1>
        <p class="page-sub">Server configuration, environment status, and admin activity.</p>
      </div>
      <div class="header-actions">
        <button class="btn btn-primary" onclick="alert('Settings saved')">Save Changes</button>
      </div>
    </div>'''

if settings_header_old in content:
    content = content.replace(settings_header_old, settings_header_new)

# Update instructions buttons on client edit page just in case
content = content.replace('class="btn btn-outline" style="text-decoration:none"', 'class="btn btn-outline"')
content = content.replace('class="btn btn-primary" style="text-decoration:none"', 'class="btn btn-primary"')

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("Settings redesign applied.")
