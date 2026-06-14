#!/usr/bin/env python3
"""Launch Thesis Master Web Dashboard."""
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from thesis.web.app import create_app

if __name__ == '__main__':
    print("🎓 Thesis Master Web Dashboard")
    print("   http://127.0.0.1:5000")
    print("   Press Ctrl+C to stop\n")
    app = create_app()
    app.run(host='0.0.0.0', port=5000, debug=True)
