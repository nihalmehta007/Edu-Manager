"""
api/index.py — Vercel serverless entry point.

Vercel's @vercel/python builder looks for an `app` variable here.
We ensure the project root is on sys.path so that imports work
correctly in the serverless environment.

Mirrors CNS1's pattern: just re-export the existing `app` instance,
do NOT call create_app() again (it already ran at module level in app.py).
"""

import os
import sys

# Ensure the project root is on sys.path so imports work on Vercel.
_PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _PROJECT_ROOT not in sys.path:
    sys.path.insert(0, _PROJECT_ROOT)

from app import app  # noqa: E402, F401 — re-export for Vercel
