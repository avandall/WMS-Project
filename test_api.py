#!/usr/bin/env python3
"""
Test script to verify API endpoints are working.
"""
import requests
import time

API_BASE = 'http://127.0.0.1:8000'

def test_endpoint(endpoint, description):
    try:
        response = requests.get(f"{API_BASE}{endpoint}", timeout=5)
        print(f"✅ {description}: {response.status_code}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"❌ {description}: {e}")
        return False

def main():
    print("Testing WMS API endpoints...")
    time.sleep(2)  # Wait for server to start

    endpoints = [
        ('/api/products', 'GET /api/products'),
        ('/api/warehouses', 'GET /api/warehouses'),
        ('/api/inventory', 'GET /api/inventory'),
        ('/api/documents', 'GET /api/documents'),
    ]

    all_passed = True
    for endpoint, description in endpoints:
        if not test_endpoint(endpoint, description):
            all_passed = False

    if all_passed:
        print("\n🎉 All endpoints are working!")
    else:
        print("\n❌ Some endpoints failed.")

if __name__ == '__main__':
    main()