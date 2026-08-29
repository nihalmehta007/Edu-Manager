import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from app import app

client = app.test_client()

print("--- Testing Routes ---")
# 1. Login page
res = client.get('/login')
print(f"[PASS] GET /login -> {res.status_code}")
assert res.status_code == 200

# 2. Register page
res = client.get('/register')
print(f"[PASS] GET /register -> {res.status_code}")
assert res.status_code == 200

# 3. Root redirect
res = client.get('/')
print(f"[PASS] GET / -> {res.status_code} (Redirects to: {res.headers.get('Location')})")
assert res.status_code == 302

# 4. Health endpoint
res = client.get('/health')
print(f"[PASS] GET /health -> {res.status_code}")
assert res.status_code == 200

print("\nAll basic route checks passed!")
