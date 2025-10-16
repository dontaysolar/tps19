#!/usr/bin/env python3
"""
Organism Evolution Engine - Genetic Strategy Optimization

Like biological evolution, strategies evolve through:
- Selection: Keep winners, discard losers
- Mutation: Random parameter changes
- Crossover: Combine successful traits  
- Adaptation: Learn from environment

This is what makes the organism "evolving" - it gets better over time.
"""

from typing import Dict, List, Any, Optional
import random
import copy
from datetime import datetime, timedelta
from modules.utils.logger import get_logger
from modules.utils.config import config

logger = get_logger(__name__)


class StrategyGene:
    """
    A strategy's genetic code (parameters)
    """
    
    def __init__(self, name: str, parameters: Dict):
        self.name = name
        self.parameters = parameters
        self.fitness = 0.0
        self.generation = 1
        self.parent_id = None
        self.mutation_count = 0
        
    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            'name': self.name,
            'parameters': self.parameters,
            'fitness': self.fitness,
            'generation': self.generation,
            'parent_id': self.parent_id,
            'mutation_count': self.mutation_count
        }


class EvolutionEngine:
    """
    Genetic evolution system for strategy optimization
    
    Instead of 400 bots, we evolve a population of strategy variants
    keeping the best performers and discarding losers
    """
    
    def __init__(self):
        self.population_size = 20  # 20 strategy variants (not 400 bots!)
        self.mutation_rate = 0.15  # 15% parameter mutation
        self.crossover_rate = 0.30  # 30% crossover probability
        self.elite_pct = 0.30  # Keep top 30%
        
        # Current population of strategies
        self.population = []
        self.generation = 1
        self.best_ever_fitness = 0.0
        self.best_ever_strategy = None
        
        # Evolution history
        self.evolution_history = []
        
        logger.info("🧬 Evolution Engine initialized")
    
    def evolve_generation(self, performance_data: Dict) -> List[StrategyGene]:
        """
        Evolve one generation of strategies
        
        This is the core of how the organism IMPROVES
        
        Args:
            performance_data: Performance of current strategies
            
        Returns:
            Next generation of strategies
        """
        try:
            # 1. Calculate fitness for all strategies
            self._calculate_fitness(performance_data)
            
            # 2. Select elite (top performers)
            elite = self._select_elite()
            
            # 3. Mutate parameters
            mutants = self._mutate_population(elite)
            
            # 4. Crossover (combine successful traits)
            offspring = self._crossover_population(elite)
            
            # 5. Create next generation
            next_generation = elite + mutants + offspring
            
            # Trim to population size
            next_generation = sorted(
                next_generation, 
                key=lambda g: g.fitness, 
                reverse=True
            )[:self.population_size]
            
            # Update generation
            self.generation += 1
            for gene in next_generation:
                gene.generation = self.generation
            
            # Track best
            best = next_generation[0]
            if best.fitness > self.best_ever_fitness:
                self.best_ever_fitness = best.fitness
                self.best_ever_strategy = copy.deepcopy(best)
                logger.info(f"🧬 NEW BEST STRATEGY! Fitness: {best.fitness:.3f}")
            
            # Record evolution
            self.evolution_history.append({
                'generation': self.generation,
                'best_fitness': best.fitness,
                'avg_fitness': sum(g.fitness for g in next_generation) / len(next_generation),
                'timestamp': datetime.now()
            })
            
            self.population = next_generation
            
            logger.info(f"🧬 Generation {self.generation} evolved - "
                       f"Best fitness: {best.fitness:.3f}, "
                       f"Avg fitness: {self.evolution_history[-1]['avg_fitness']:.3f}")
            
            return next_generation
            
        except Exception as e:
            logger.error(f"Evolution error: {e}")
            return self.population
    
    def _calculate_fitness(self, performance_data: Dict):
        """
        Calculate fitness score for each strategy
        
        Fitness = (Sharpe × Win Rate × Profit Factor) / (1 + Drawdown)
        """
        for gene in self.population:
            perf = performance_data.get(gene.name, {})
            
            sharpe = perf.get('sharpe_ratio', 0.5)
            win_rate = perf.get('win_rate', 0.5)
            profit_factor = perf.get('profit_factor', 1.0)
            drawdown = perf.get('max_drawdown', 0.10)
            
            # Composite fitness score
            gene.fitness = (sharpe * win_rate * profit_factor) / (1 + drawdown)
    
    def _select_elite(self) -> List[StrategyGene]:
        """
        Select top performers
        
        Survival of the fittest
        """
        # Sort by fitness
        sorted_pop = sorted(self.population, key=lambda g: g.fitness, reverse=True)
        
        # Keep top 30%
        elite_count = max(1, int(len(sorted_pop) * self.elite_pct))
        elite = sorted_pop[:elite_count]
        
        logger.info(f"🧬 Selected {len(elite)} elite strategies from {len(self.population)}")
        
        return [copy.deepcopy(g) for g in elite]
    
    def _mutate_population(self, elite: List[StrategyGene]) -> List[StrategyGene]:
        """
        Mutate parameters with random changes
        
        This creates diversity and explores new parameter spaces
        """
        mutants = []
        
        for gene in elite:
            if random.random() < self.mutation_rate:
                mutant = copy.deepcopy(gene)
                mutant.name = f"{gene.name}_m{self.generation}"
                mutant.parent_id = gene.name
                mutant.mutation_count = gene.mutation_count + 1
                
                # Mutate parameters
                for param_name, param_value in mutant.parameters.items():
                    if isinstance(param_value, (int, float)):
                        # Random mutation ±20%
                        mutation_factor = random.uniform(0.80, 1.20)
                        mutant.parameters[param_name] = param_value * mutation_factor
                
                mutants.append(mutant)
        
        logger.info(f"🧬 Created {len(mutants)} mutants")
        
        return mutants
    
    def _crossover_population(self, elite: List[StrategyGene]) -> List[StrategyGene]:
        """
        Combine successful strategies
        
        Like sexual reproduction - combine genes from two parents
        """
        offspring = []
        
        # Create offspring from random pairs
        num_offspring = max(1, int(len(elite) * self.crossover_rate))
        
        for i in range(num_offspring):
            if len(elite) < 2:
                break
            
            # Select two parents
            parent1 = random.choice(elite)
            parent2 = random.choice([g for g in elite if g != parent1])
            
            # Create child
            child = StrategyGene(
                name=f"{parent1.name}_x_{parent2.name}_g{self.generation}",
                parameters={}
            )
            
            # Combine parameters (randomly from each parent)
            for param_name in parent1.parameters.keys():
                if random.random() < 0.5:
                    child.parameters[param_name] = parent1.parameters[param_name]
                else:
                    child.parameters[param_name] = parent2.parameters.get(
                        param_name, 
                        parent1.parameters[param_name]
                    )
            
            child.parent_id = f"{parent1.name}+{parent2.name}"
            offspring.append(child)
        
        logger.info(f"🧬 Created {len(offspring)} offspring through crossover")
        
        return offspring
    
    def get_evolution_stats(self) -> Dict:
        """
        Get evolution statistics
        
        Returns:
            Evolution metrics
        """
        if not self.population:
            return {}
        
        current_best = max(self.population, key=lambda g: g.fitness)
        current_avg = sum(g.fitness for g in self.population) / len(self.population)
        
        return {
            'generation': self.generation,
            'population_size': len(self.population),
            'current_best_fitness': current_best.fitness,
            'current_avg_fitness': current_avg,
            'all_time_best_fitness': self.best_ever_fitness,
            'total_mutations': sum(g.mutation_count for g in self.population),
            'evolution_trend': self._calculate_evolution_trend()
        }
    
    def _calculate_evolution_trend(self) -> str:
        """Calculate if organism is evolving positively"""
        if len(self.evolution_history) < 3:
            return 'insufficient_data'
        
        recent = self.evolution_history[-3:]
        fitnesses = [g['avg_fitness'] for g in recent]
        
        if fitnesses[-1] > fitnesses[0] * 1.05:
            return 'improving'
        elif fitnesses[-1] < fitnesses[0] * 0.95:
            return 'declining'
        else:
            return 'stable'
    
    def seed_initial_population(self, base_strategies: List[Dict]):
        """
        Create initial population from base strategies
        
        Args:
            base_strategies: List of initial strategy configurations
        """
        self.population = []
        
        for strategy in base_strategies:
            # Create base strategy
            gene = StrategyGene(
                name=strategy['name'],
                parameters=strategy['parameters']
            )
            self.population.append(gene)
            
            # Create variants
            for i in range(3):  # 3 variants per base strategy
                variant = copy.deepcopy(gene)
                variant.name = f"{strategy['name']}_v{i+1}"
                
                # Slight parameter variations
                for param_name, param_value in variant.parameters.items():
                    if isinstance(param_value, (int, float)):
                        variation = random.uniform(0.90, 1.10)
                        variant.parameters[param_name] = param_value * variation
                
                self.population.append(variant)
        
        logger.info(f"🧬 Initial population seeded with {len(self.population)} strategies")


# Global evolution engine instance
evolution_engine = EvolutionEngine()
