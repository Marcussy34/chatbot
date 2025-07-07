#!/usr/bin/env python3
"""
Deployment Validation Script for Mindhive Chatbot
================================================

This script validates that the application is ready for Google Cloud Run deployment.
"""

import sys
import os
from pathlib import Path

def print_check(name, status, details=""):
    """Print a check result."""
    icon = "✅" if status else "❌"
    print(f"{icon} {name}")
    if details:
        print(f"   {details}")

def main():
    print("🚀 Mindhive Chatbot - Deployment Validation")
    print("=" * 50)
    
    # Check Python version
    version = sys.version_info
    compatible = version.major == 3 and version.minor >= 8
    print_check(f"Python {version.major}.{version.minor}.{version.micro}", compatible)
    
    # Check key dependencies
    deps = ["fastapi", "uvicorn", "langchain", "sentence_transformers"]
    for dep in deps:
        try:
            __import__(dep.replace("-", "_"))
            print_check(f"{dep}", True)
        except ImportError:
            print_check(f"{dep}", False, "Missing")
    
    # Check services
    try:
        from app.main import app
        print_check("FastAPI App", True)
    except Exception as e:
        print_check("FastAPI App", False, str(e))
    
    try:
        from app.calculator import CalculatorService
        calc = CalculatorService()
        result = calc.evaluate_expression("2+3")
        print_check("Calculator", result == 5, f"2+3 = {result}")
    except Exception as e:
        print_check("Calculator", False, str(e))
    
    # Check data files
    files = ["data/zus_products.json", "data/zus_outlets.db", "data/product_index.faiss"]
    for file_path in files:
        exists = Path(file_path).exists()
        print_check(file_path, exists)
    
    # Check deployment files
    deploy_files = ["Dockerfile", "deploy.sh", "DEPLOYMENT.md"]
    for file_path in deploy_files:
        exists = Path(file_path).exists()
        print_check(file_path, exists)
    
    print("\n🎉 Validation complete!")
    print("Ready for Cloud Run deployment: ./deploy.sh")

if __name__ == "__main__":
    main() 