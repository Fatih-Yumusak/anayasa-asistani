from fastapi import FastAPI
import sys
import os

# Add backend/src to path so 'import rag_engine' inside main.py works
# We act as if we are in backend/src
current_dir = os.path.dirname(os.path.abspath(__file__))
backend_src = os.path.abspath(os.path.join(current_dir, '..', 'backend', 'src'))
sys.path.append(backend_src)

from main import app

# Vercel expects a variable named 'app'
