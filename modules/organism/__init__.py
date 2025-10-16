"""
TPS19 APEX Organism - The Evolving Financial Intelligence

This package implements the organism architecture that merges
TPS19's foundation with APEX's ambitious vision into a realistic,
profit-generating system.

Core Modules:
- brain.py: Central intelligence & decision making
- immune_system.py: Multi-layer guardrails & protection  
- nervous_system.py: Multi-strategy execution
- evolution.py: Learning & adaptation engine
- metabolism.py: Capital management & profit extraction
"""

from .brain import OrganismBrain
from .immune_system import ImmuneSystem
from .nervous_system import NervousSystem
from .evolution import EvolutionEngine
from .metabolism import Metabolism

__all__ = [
    'OrganismBrain',
    'ImmuneSystem',
    'NervousSystem',
    'EvolutionEngine',
    'Metabolism'
]

__version__ = '1.0.0-APEX'
