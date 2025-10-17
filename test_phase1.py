#!/usr/bin/env python3
"""Test Phase 1 Components Independently"""

import sys
import os

workspace_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(workspace_dir, 'modules'))

print("=" * 60)
print("🧪 TESTING PHASE 1 COMPONENTS")
print("=" * 60)

# Test imports
print("\n1️⃣ Testing Imports...")
try:
    from ai_models import LSTMPredictor, GANSimulator, SelfLearningPipeline
    print("✅ AI Models imported successfully")
    ai_models_ok = True
except ImportError as e:
    print(f"❌ AI Models import failed: {e}")
    ai_models_ok = False

try:
    from redis_integration import RedisIntegration
    print("✅ Redis Integration imported successfully")
    redis_ok = True
except ImportError as e:
    print(f"❌ Redis Integration import failed: {e}")
    redis_ok = False

try:
    from google_sheets_integration import GoogleSheetsIntegration
    print("✅ Google Sheets Integration imported successfully")
    sheets_ok = True
except ImportError as e:
    print(f"❌ Google Sheets Integration import failed: {e}")
    sheets_ok = False

# Test LSTM
if ai_models_ok:
    print("\n2️⃣ Testing LSTM Predictor...")
    try:
        predictor = LSTMPredictor(model_dir=os.path.join(workspace_dir, 'data/models'))
        status = predictor.get_status()
        print(f"✅ LSTM Status: {status}")
    except Exception as e:
        print(f"❌ LSTM Error: {e}")

# Test GAN
if ai_models_ok:
    print("\n3️⃣ Testing GAN Simulator...")
    try:
        simulator = GANSimulator(model_dir=os.path.join(workspace_dir, 'data/models'))
        status = simulator.get_status()
        print(f"✅ GAN Status: {status}")
    except Exception as e:
        print(f"❌ GAN Error: {e}")

# Test Self-Learning
if ai_models_ok:
    print("\n4️⃣ Testing Self-Learning Pipeline...")
    try:
        pipeline = SelfLearningPipeline(db_path=os.path.join(workspace_dir, 'data/self_learning.db'))
        status = pipeline.get_status()
        print(f"✅ Learning Status: {status}")
    except Exception as e:
        print(f"❌ Learning Error: {e}")

# Test Redis
if redis_ok:
    print("\n5️⃣ Testing Redis Integration...")
    try:
        redis_client = RedisIntegration()
        if redis_client.connected:
            # Test operations
            redis_client.set_price('BTC/USDT', 26500.0)
            price = redis_client.get_price('BTC/USDT')
            print(f"✅ Redis working. Test price: {price}")
            redis_client.close()
        else:
            print("⚠️ Redis not running (optional component)")
    except Exception as e:
        print(f"⚠️ Redis Error (optional): {e}")

# Test Google Sheets
if sheets_ok:
    print("\n6️⃣ Testing Google Sheets Integration...")
    try:
        sheets = GoogleSheetsIntegration(credentials_file=os.path.join(workspace_dir, 'config/google_credentials.json'))
        status = sheets.get_status()
        if status['connected']:
            print(f"✅ Google Sheets connected")
        else:
            print("⚠️ Google Sheets not configured (optional component)")
    except Exception as e:
        print(f"⚠️ Google Sheets Error (optional): {e}")

# Summary
print("\n" + "=" * 60)
print("📊 PHASE 1 TEST SUMMARY")
print("=" * 60)
print(f"AI Models (LSTM/GAN/Learning): {'✅ OK' if ai_models_ok else '❌ FAIL'}")
print(f"Redis Integration: {'✅ OK' if redis_ok else '❌ FAIL'}")
print(f"Google Sheets Integration: {'✅ OK' if sheets_ok else '❌ FAIL'}")
print()
print("Note: Redis and Google Sheets are optional components.")
print("Install with: pip install -r requirements_phase1.txt")
print("=" * 60)
