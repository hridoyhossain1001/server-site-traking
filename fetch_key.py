import urllib.request
import re
import base64
import os

def get_key():
    url = os.getenv("CAPI_ADMIN_URL", "http://localhost:8000/api/v1/admin")
    username = os.getenv("CAPI_ADMIN_USERNAME", "admin")
    password = os.getenv("CAPI_ADMIN_PASSWORD")
    if not password:
        raise SystemExit("Set CAPI_ADMIN_PASSWORD before running this helper.")

    req = urllib.request.Request(url)
    auth = base64.b64encode(f"{username}:{password}".encode()).decode("utf-8")
    req.add_header("Authorization", f"Basic {auth}")
    
    with urllib.request.urlopen(req) as response:
        html = response.read().decode("utf-8")
        
    # Extract client id from HTML where name is LoadTest
    # <form action="/api/v1/admin/client/1/instructions" ...
    match = re.search(r'action="/api/v1/admin/client/(\d+)/instructions"[^>]*>.*?LoadTest', html, re.DOTALL | re.IGNORECASE)
    if not match:
        match = re.search(r'LoadTest.*?/api/v1/admin/client/(\d+)/instructions', html, re.DOTALL | re.IGNORECASE)
    
    if not match:
        # Let's just find the first instruction link
        match = re.search(r'/api/v1/admin/client/(\d+)/instructions', html)
        
    if match:
        client_id = match.group(1)
        inst_url = f"{url.rstrip('/')}/client/{client_id}/instructions"
        req_inst = urllib.request.Request(inst_url)
        req_inst.add_header("Authorization", f"Basic {auth}")
        with urllib.request.urlopen(req_inst) as response:
            inst_html = response.read().decode("utf-8")
            
        key_match = re.search(r'[\w\d]{32,}', inst_html) # UUID is 32/36 chars
        if key_match:
            print("Instruction page fetched. API key is intentionally not written to disk.")
        print(f"Instructions URL: {inst_url}")

if __name__ == "__main__":
    get_key()
