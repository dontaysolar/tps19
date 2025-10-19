#!/usr/bin/env python3
"""
APEX Nexus V2 - Credential Update Tool
Auto-updates .env and validates API credentials
"""

import os
import sys

def update_env_file(api_key, api_secret):
    """Update .env file with new credentials"""
    env_path = "/workspace/.env"
    
    # Read existing .env
    with open(env_path, 'r') as f:
        lines = f.readlines()
    
    # Update credentials
    with open(env_path, 'w') as f:
        for line in lines:
            if line.startswith('EXCHANGE_API_KEY='):
                f.write(f'EXCHANGE_API_KEY={api_key}\n')
            elif line.startswith('EXCHANGE_API_SECRET='):
                f.write(f'EXCHANGE_API_SECRET={api_secret}\n')
            else:
                f.write(line)
    
    print(f"✅ Updated .env file")

def test_credentials(api_key, api_secret):
    """Test if credentials work"""
    import ccxt
    
    exchange = ccxt.cryptocom({
        'apiKey': api_key,
        'secret': api_secret,
        'enableRateLimit': True
    })
    
    try:
        balance = exchange.fetch_balance()
        print('\n🎉 ✅ AUTHENTICATION SUCCESS!')
        print(f'📊 Account Balance:')
        
        # Show USDT balance
        usdt = balance.get('USDT', {}).get('total', 0)
        print(f'   USDT: ${usdt:.2f}')
        
        # Show other balances
        for currency, amounts in balance['total'].items():
            if amounts > 0 and currency != 'USDT':
                print(f'   {currency}: {amounts}')
        
        return True
    except Exception as e:
        print(f'\n❌ AUTHENTICATION FAILED: {e}')
        return False

def main():
    print("=" * 60)
    print("🚀 APEX NEXUS V2 - CREDENTIAL UPDATE TOOL")
    print("=" * 60)
    print("\nPaste your Crypto.com API credentials below:")
    print("(Press Enter after each field)\n")
    
    # Get credentials
    api_key = input("API KEY: ").strip()
    api_secret = input("API SECRET: ").strip()
    
    if not api_key or not api_secret:
        print("❌ Error: Both API Key and Secret are required")
        sys.exit(1)
    
    print(f"\n📝 Received:")
    print(f"   API Key: {api_key}")
    print(f"   Secret: {api_secret[:10]}...{api_secret[-4:]}")
    
    # Update .env
    print("\n🔄 Updating .env file...")
    update_env_file(api_key, api_secret)
    
    # Test credentials
    print("\n🔍 Testing credentials with Crypto.com...")
    if test_credentials(api_key, api_secret):
        print("\n" + "=" * 60)
        print("✅ CREDENTIALS VALIDATED - READY FOR LIVE TRADING!")
        print("=" * 60)
        
        # Ask to start APEX
        print("\n🚀 Start APEX Nexus V2 now? (y/n): ", end='')
        start = input().strip().lower()
        
        if start == 'y':
            print("\n🔥 Starting APEX Nexus V2...")
            os.system("cd /workspace && nohup python3 apex_nexus_v2.py > logs/apex_LIVE.log 2>&1 &")
            print("✅ APEX started! Check logs/apex_LIVE.log for output")
            print("📊 Monitor: tail -f logs/apex_LIVE.log")
        else:
            print("\n💡 To start manually, run:")
            print("   python3 apex_nexus_v2.py")
    else:
        print("\n" + "=" * 60)
        print("❌ CREDENTIAL VALIDATION FAILED")
        print("=" * 60)
        print("\n⚠️  Please verify:")
        print("   1. API Key and Secret are correct")
        print("   2. API has SPOT TRADING permissions")
        print("   3. API is for PRODUCTION (not sandbox)")
        print("   4. IP whitelist allows this server (if enabled)")
        sys.exit(1)

if __name__ == "__main__":
    main()
