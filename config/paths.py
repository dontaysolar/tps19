#!/usr/bin/env python3
"""Path configuration for TPS19 system"""

import os

# Determine base path - use workspace if available, otherwise /opt/tps19
if os.path.exists('/workspace'):
    BASE_PATH = '/workspace/opt/tps19'
else:
    BASE_PATH = '/opt/tps19'

# Create directories if they don't exist
os.makedirs(os.path.join(BASE_PATH, 'data', 'databases'), exist_ok=True)
os.makedirs(os.path.join(BASE_PATH, 'logs'), exist_ok=True)
os.makedirs(os.path.join(BASE_PATH, 'modules'), exist_ok=True)

# Export paths
DATA_PATH = os.path.join(BASE_PATH, 'data')
DATABASE_PATH = os.path.join(BASE_PATH, 'data', 'databases')
LOGS_PATH = os.path.join(BASE_PATH, 'logs')
MODULES_PATH = os.path.join(BASE_PATH, 'modules')