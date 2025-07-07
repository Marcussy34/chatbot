#!/usr/bin/env python3
"""
Submission Validation Script
Tests all deployed endpoints to ensure everything is working correctly
"""

import requests
import json
import time
from urllib.parse import quote

# Production URL
BASE_URL = "https://mindhive-chatbot-yvsu2loedq-uc.a.run.app"

def test_endpoint(name, url, expected_status=200):
    """Test an endpoint and return results"""
    print(f"\n🔍 Testing {name}...")
    print(f"URL: {url}")
    
    try:
        start_time = time.time()
        response = requests.get(url, timeout=30)
        end_time = time.time()
        
        response_time = round((end_time - start_time) * 1000, 2)
        
        if response.status_code == expected_status:
            print(f"✅ SUCCESS - Status: {response.status_code}, Time: {response_time}ms")
            if response.headers.get('content-type', '').startswith('application/json'):
                try:
                    data = response.json()
                    if 'result' in data:
                        print(f"   Result: {data['result']}")
                    elif 'products' in data:
                        print(f"   Found: {len(data['products'])} products")
                    elif 'outlets' in data:
                        print(f"   Found: {len(data['outlets'])} outlets")
                    else:
                        print(f"   Response: {str(data)[:100]}...")
                except:
                    print(f"   Response: {response.text[:100]}...")
            return True
        else:
            print(f"❌ FAILED - Status: {response.status_code}")
            print(f"   Error: {response.text[:200]}...")
            return False
    except Exception as e:
        print(f"❌ ERROR - {str(e)}")
        return False

def main():
    """Run all submission validation tests"""
    print("🚀 Mindhive AI Chatbot - Submission Validation")
    print("=" * 60)
    
    results = []
    
    # Health Check
    results.append(test_endpoint(
        "Health Check",
        f"{BASE_URL}/health"
    ))
    
    # Calculator Tests
    calculator_tests = [
        ("Basic Addition", f"{BASE_URL}/calculator?expr={quote('2+3')}"),
        ("Complex Expression", f"{BASE_URL}/calculator?expr={quote('(10-5)*2+3')}"),
        ("Division", f"{BASE_URL}/calculator?expr={quote('15/3')}"),
        ("Exponentiation", f"{BASE_URL}/calculator?expr={quote('2**3')}"),
    ]
    
    for name, url in calculator_tests:
        results.append(test_endpoint(name, url))
    
    # RAG Product Search Tests
    product_tests = [
        ("Product Search - Ceramic", f"{BASE_URL}/products?query=ceramic+mug"),
        ("Product Search - Travel", f"{BASE_URL}/products?query=travel+bottle"),
        ("Product Search - Black", f"{BASE_URL}/products?query=black+tumbler"),
    ]
    
    for name, url in product_tests:
        results.append(test_endpoint(name, url))
    
    # Text2SQL Outlet Tests
    outlet_tests = [
        ("Outlets in PJ", f"{BASE_URL}/outlets?query=outlets+in+Petaling+Jaya"),
        ("Opening Hours", f"{BASE_URL}/outlets?query=opening+hours"),
        ("All Outlets", f"{BASE_URL}/outlets?query=all+outlets"),
    ]
    
    for name, url in outlet_tests:
        results.append(test_endpoint(name, url))
    
    # API Documentation
    results.append(test_endpoint(
        "API Documentation",
        f"{BASE_URL}/docs"
    ))
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 VALIDATION SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"✅ Passed: {passed}/{total} tests")
    print(f"❌ Failed: {total - passed}/{total} tests")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED - READY FOR SUBMISSION! 🎉")
    else:
        print(f"\n⚠️  {total - passed} tests failed - please review")
    
    print(f"\n🌐 Live Demo: {BASE_URL}")
    print(f"📚 API Docs: {BASE_URL}/docs")

if __name__ == "__main__":
    main() 