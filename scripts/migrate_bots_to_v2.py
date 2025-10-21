#!/usr/bin/env python3
"""
AEGIS AID - Automated Bot Migration Script
Migrates legacy bots to AEGIS v2.0 unified architecture

ATLAS Compliance: Power of 10 rules
PROMETHEUS: Autonomous execution
"""

import os
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple

# ATLAS: Fixed constants
MAX_BOTS_TO_MIGRATE = 100
BOTS_DIR = Path('/workspace/bots')
BACKUP_DIR = Path('/workspace/bots/legacy_backup')


def analyze_bot(bot_path: Path) -> Dict:
    """
    Analyze bot to determine migration strategy
    
    ATLAS Compliance:
    - Assertion 1: bot_path exists
    - Assertion 2: result is dict
    """
    assert bot_path.exists(), f"Bot file not found: {bot_path}"
    
    with open(bot_path, 'r') as f:
        content = f.read()
    
    # Detect exchange usage
    has_ccxt = 'import ccxt' in content or 'from ccxt' in content
    has_exchange_init = 'self.exchange = ccxt.' in content
    has_fetch_calls = 'fetch_ticker' in content or 'fetch_ohlcv' in content
    has_order_calls = 'create_order' in content or 'create_market' in content
    
    # Detect class structure
    class_match = re.search(r'class\s+(\w+)(?:\([^)]*\))?:', content)
    init_match = re.search(r'def __init__\(self(?:, ([^)]+))?\):', content)
    
    needs_migration = has_exchange_init or has_order_calls
    
    result = {
        'path': bot_path,
        'name': bot_path.stem,
        'class_name': class_match.group(1) if class_match else None,
        'has_ccxt': has_ccxt,
        'has_exchange_init': has_exchange_init,
        'has_fetch_calls': has_fetch_calls,
        'has_order_calls': has_order_calls,
        'needs_migration': needs_migration,
        'init_params': init_match.group(1) if init_match else None
    }
    
    # ATLAS Assertion 2
    assert isinstance(result, dict), "Result must be dict"
    
    return result


def generate_v2_bot(analysis: Dict) -> str:
    """
    Generate v2 bot code from analysis
    
    ATLAS Compliance:
    - Assertion 1: analysis valid
    - Assertion 2: result is non-empty string
    """
    assert analysis['class_name'], "No class name found"
    assert analysis['needs_migration'], "Bot doesn't need migration"
    
    # Read original content
    with open(analysis['path'], 'r') as f:
        original = f.read()
    
    class_name = analysis['class_name']
    
    # Generate v2 version
    v2_code = f'''#!/usr/bin/env python3
"""
{class_name} v2.0 - MIGRATED TO AEGIS ARCHITECTURE

AEGIS v2.0 Changes:
- Inherits from TradingBotBase (enforced safety)
- Uses Exchange Adapter (no direct ccxt)
- Integrates with PSM (position tracking)
- ATLAS-compliant (Power of 10 rules)

Original bot preserved in legacy_backup/
"""

import os
import sys
from typing import Dict, List

# Add AEGIS core to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(__file__)), 'core'))

# Import AEGIS base class
from trading_bot_base import TradingBotBase

'''
    
    # Extract class definition and modify to inherit from TradingBotBase
    class_start = original.find(f'class {class_name}')
    if class_start == -1:
        return ""
    
    # Find the class body
    class_def_end = original.find(':', class_start)
    docstring_start = original.find('"""', class_def_end)
    docstring_end = original.find('"""', docstring_start + 3)
    
    # Modify class to inherit from TradingBotBase
    v2_code += f'''
class {class_name}(TradingBotBase):
    """
    AEGIS v2.0: Now inherits from TradingBotBase
    - Automatic Exchange Adapter usage
    - PSM integration for position tracking
    - ATLAS-compliant code
    """
    
    def __init__(self, exchange_config=None):
        """
        Initialize with AEGIS architecture
        
        ATLAS Compliance:
        - Assertion 1: Base class initialized
        - Assertion 2: Config validated
        """
        # Initialize base class (automatic adapter + PSM)
        super().__init__(
            bot_name="{class_name.upper()}",
            bot_version="2.0.0",
            exchange_name='mock' if not exchange_config else 'cryptocom',
            enable_psm=True,
            enable_logging=True
        )
        
        # ATLAS Assertion 1
        assert hasattr(self, 'exchange_adapter'), "Base class initialization failed"
        
        # Bot-specific config (preserve from original)
        # TODO: Copy original config here
        self.config = {{}}
        
        # ATLAS Assertion 2
        assert isinstance(self.config, dict), "Config must be dict"
'''
    
    # Add placeholder for migrated methods
    v2_code += '''
    
    # Original bot methods migrated below
    # Key changes:
    # - self.exchange.fetch_X() → self.get_ticker()/self.exchange_adapter.X()
    # - self.exchange.create_order() → self.place_order()
    # - Add ATLAS assertions (min 2 per function)
    
    # TODO: Migrate remaining methods from original bot
    # See god_bot_v2.py for migration pattern
'''
    
    # ATLAS Assertion 2
    assert len(v2_code) > 100, "Generated code too short"
    
    return v2_code


def migrate_bot(analysis: Dict, dry_run: bool = False) -> Dict:
    """
    Migrate single bot to v2
    
    ATLAS Compliance:
    - Assertion 1: analysis valid
    - Assertion 2: result is dict
    """
    assert analysis['needs_migration'], "Bot doesn't need migration"
    
    bot_path = analysis['path']
    v2_path = bot_path.parent / f"{bot_path.stem}_v2.py"
    backup_path = BACKUP_DIR / bot_path.name
    
    result = {
        'bot': analysis['name'],
        'success': False,
        'error': None,
        'v2_path': str(v2_path)
    }
    
    try:
        if not dry_run:
            # Create backup
            BACKUP_DIR.mkdir(exist_ok=True)
            if not backup_path.exists():
                import shutil
                shutil.copy2(bot_path, backup_path)
            
            # Generate v2 code
            v2_code = generate_v2_bot(analysis)
            
            if v2_code:
                with open(v2_path, 'w') as f:
                    f.write(v2_code)
                
                os.chmod(v2_path, 0o755)
                
                result['success'] = True
        else:
            result['success'] = True
            result['dry_run'] = True
    
    except Exception as e:
        result['error'] = str(e)
    
    # ATLAS Assertion 2
    assert isinstance(result, dict), "Result must be dict"
    
    return result


def main():
    """
    Main migration orchestrator
    
    ATLAS Compliance:
    - Assertion 1: BOTS_DIR exists
    - Assertion 2: Safe loop bound
    """
    print("=" * 70)
    print("AEGIS AID - Automated Bot Migration")
    print("=" * 70)
    
    # ATLAS Assertion 1
    assert BOTS_DIR.exists(), f"Bots directory not found: {BOTS_DIR}"
    
    # Get all bot files
    bot_files = sorted([f for f in BOTS_DIR.glob('*.py') 
                       if not f.name.startswith('__') 
                       and not f.name.endswith('_v2.py')])
    
    # ATLAS Assertion 2
    assert len(bot_files) <= MAX_BOTS_TO_MIGRATE, "Too many bots to migrate"
    
    print(f"\n[1/4] Analyzing {len(bot_files)} bots...")
    
    analyses = []
    for bot_file in bot_files:
        try:
            analysis = analyze_bot(bot_file)
            analyses.append(analysis)
        except Exception as e:
            print(f"  ❌ {bot_file.name}: {e}")
    
    # Filter to bots needing migration
    to_migrate = [a for a in analyses if a['needs_migration']]
    no_migration = [a for a in analyses if not a['needs_migration']]
    
    print(f"  ✅ Analysis complete")
    print(f"     Needs migration: {len(to_migrate)} bots")
    print(f"     No exchange usage: {len(no_migration)} bots")
    
    # Display migration targets
    print(f"\n[2/4] Migration targets (bots with exchange):")
    for i, analysis in enumerate(to_migrate[:10], 1):
        print(f"  {i}. {analysis['name']}")
    if len(to_migrate) > 10:
        print(f"  ... and {len(to_migrate) - 10} more")
    
    print(f"\n[3/4] Migrating {len(to_migrate)} bots...")
    
    results = []
    for i, analysis in enumerate(to_migrate, 1):
        print(f"  [{i}/{len(to_migrate)}] {analysis['name']}...", end=' ')
        result = migrate_bot(analysis, dry_run=False)
        results.append(result)
        
        if result['success']:
            print("✅")
        else:
            print(f"❌ {result['error']}")
    
    # Summary
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"\n[4/4] Migration Summary:")
    print(f"  ✅ Successful: {len(successful)}/{len(results)}")
    print(f"  ❌ Failed: {len(failed)}/{len(results)}")
    
    if failed:
        print(f"\n  Failed bots:")
        for r in failed:
            print(f"    - {r['bot']}: {r['error']}")
    
    print("\n" + "=" * 70)
    print(f"AEGIS Migration: {len(successful)}/{len(to_migrate)} bots migrated")
    print("=" * 70)
    
    # Note about manual work needed
    print("\n⚠️  NOTE: Migrated bots are TEMPLATES requiring manual completion:")
    print("   1. Copy original bot logic to v2 file")
    print("   2. Replace self.exchange.X() with self.get_X() or self.exchange_adapter.X()")
    print("   3. Replace create_order() with self.place_order()")
    print("   4. Add ATLAS assertions (min 2 per function)")
    print("   5. Test each migrated bot")
    print("\n   See god_bot_v2.py for complete migration example")
    
    return 0 if not failed else 1


if __name__ == '__main__':
    sys.exit(main())
