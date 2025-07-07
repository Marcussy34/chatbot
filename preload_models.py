#!/usr/bin/env python3
"""
Pre-download sentence transformer models to avoid runtime download delays
"""
import os
import sys

# Set cache directory
os.environ['HF_HOME'] = '/app/.cache/huggingface'
os.environ['TRANSFORMERS_CACHE'] = '/app/.cache/huggingface'

try:
    from sentence_transformers import SentenceTransformer
    
    print("Pre-downloading sentence transformer model...")
    
    # This will download and cache the model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Test the model works
    test_embedding = model.encode("test sentence")
    print(f"Model loaded successfully! Test embedding shape: {test_embedding.shape}")
    
    print("Model pre-loading completed!")
    
except Exception as e:
    print(f"Error pre-loading model: {e}")
    sys.exit(1) 