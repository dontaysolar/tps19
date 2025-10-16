#!/usr/bin/env python3
"""
Quick test script to run the organism
"""

import sys
import os

# Add workspace to path
sys.path.insert(0, '/workspace')

from tps19_apex import TPS19APEX
from modules.utils.logger import get_logger

logger = get_logger(__name__)

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║           TPS19 APEX ORGANISM - STARTING                     ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        system = TPS19APEX()
        system.start()
    except KeyboardInterrupt:
        print("\n🛑 Organism stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        logger.error(f"Startup error: {e}", exc_info=True)
