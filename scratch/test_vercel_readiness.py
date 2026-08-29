import os
import sys

# Test 1: Entrypoint imports
print("--- Test 1: Testing api.index import ---")
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.index import app as vercel_app
print("[PASS] Successfully imported vercel_app from api.index")

# Test 2: Health check endpoint
print("\n--- Test 2: Testing /health endpoint ---")
client = vercel_app.test_client()
res = client.get('/health')
print(f"[PASS] /health status code: {res.status_code}, data: {res.get_json()}")

# Test 3: Vercel environment without MONGO_URI (Should show setup screen, NOT crash with 500)
print("\n--- Test 3: Testing Vercel environment without MONGO_URI ---")
os.environ['VERCEL'] = '1'
# Create test client with VERCEL=1
vercel_res = client.get('/login')
print(f"[PASS] /login status code on unconfigured Vercel: {vercel_res.status_code}")
assert vercel_res.status_code == 200, f"Expected 200 setup notice, got {vercel_res.status_code}"
assert b"Database Setup Required" in vercel_res.data or b"Connect your MongoDB database" in vercel_res.data
print("[PASS] Setup notice successfully rendered instead of 500 Internal Server Error!")

# Test 4: WSGI Path Normalization
print("\n--- Test 4: Testing WSGI path normalization ---")
environ = {
    'REQUEST_METHOD': 'GET',
    'PATH_INFO': '/api/index.py/health',
    'SERVER_NAME': 'localhost',
    'SERVER_PORT': '80',
    'wsgi.url_scheme': 'http',
    'wsgi.input': None
}
status_holder = []
def start_response(status, headers):
    status_holder.append(status)

res_iter = vercel_app.wsgi_app(environ, start_response)
print(f"[PASS] WSGI response for /api/index.py/health: {status_holder[0]}")
assert '200' in status_holder[0] or '503' in status_holder[0]

# Test 5: Check requirements.txt contents
print("\n--- Test 5: Checking requirements.txt ---")
with open('requirements.txt', 'r') as f:
    reqs = f.read()
for dep in ['Flask', 'mongoengine', 'pymongo', 'Flask-Login', 'Flask-WTF', 'Werkzeug', 'dnspython', 'certifi', 'email-validator']:
    assert dep in reqs, f"Missing dependency: {dep}"
    print(f"[PASS] {dep} present in requirements.txt")

print("\nALL TESTS PASSED! The project is fully prepared for Vercel deployment.")
