#!/usr/bin/env python3
"""
Helios Post-Deployment Checker
- local mode: checks against localhost server
- remote mode: checks given base URL
"""
import sys, os, time, json, hashlib
from urllib.parse import urljoin
import requests

def sha256_file(path):
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(8192), b''):
            h.update(chunk)
    return h.hexdigest()

def check_endpoints(base):
    endpoints = [
        '/api/health', '/api/status', '/api/trades', '/api/performance', '/api/positions', '/api/sentiment', '/api/overview'
    ]
    results = {}
    for ep in endpoints:
        url = urljoin(base, ep)
        try:
            r = requests.get(url, timeout=10)
            results[ep] = {'status': r.status_code, 'ok': r.ok}
        except Exception as e:
            results[ep] = {'status': 0, 'ok': False, 'error': str(e)}
    return results

def main():
    base = sys.argv[1] if len(sys.argv) > 1 else 'http://localhost:5000'
    results = check_endpoints(base)
    ok = all(v.get('ok') for v in results.values())
    out = {
        'base': base,
        'results': results,
        'ok': ok,
        'timestamp': int(time.time())
    }
    print(json.dumps(out, indent=2))
    sys.exit(0 if ok else 1)

if __name__ == '__main__':
    main()
