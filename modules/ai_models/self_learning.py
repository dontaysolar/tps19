#!/usr/bin/env python3
"""Self-Learning Pipeline - Continuous Improvement System for TPS19"""

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import json
import os
import sqlite3
from typing import Dict, List, Any


class SelfLearningPipeline:
    """Self-learning system that continuously improves strategy performance"""
    
    def __init__(self, db_path='/opt/tps19/data/self_learning.db'):
        """Initialize self-learning pipeline
        
        Args:
            db_path: Path to learning database
        """
        self.db_path = db_path
        self._init_database()
        
        self.learning_rate = 0.01
        self.feedback_buffer = []
        self.performance_history = []
        
        self.config = {
            'learning_enabled': True,
            'min_samples_for_learning': 10,
            'performance_window': 100,  # trades
            'adaptation_threshold': 0.05,  # 5% performance change
            'genetic_algorithm': {
                'population_size': 20,
                'mutation_rate': 0.1,
                'crossover_rate': 0.7,
                'elite_size': 2
            }
        }
        
        self.metrics = {
            'learning_cycles': 0,
            'adaptations_made': 0,
            'performance_improvement': 0.0,
            'last_learning': None
        }
        
    def _init_database(self):
        """Initialize learning database"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Performance feedback table
        cursor.execute("""CREATE TABLE IF NOT EXISTS performance_feedback (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            strategy TEXT NOT NULL,
            parameters TEXT NOT NULL,
            profit REAL NOT NULL,
            win_rate REAL NOT NULL,
            sharpe_ratio REAL,
            max_drawdown REAL,
            trades_count INTEGER,
            market_conditions TEXT
        )""")
        
        # Learning history table
        cursor.execute("""CREATE TABLE IF NOT EXISTS learning_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            adaptation_type TEXT NOT NULL,
            old_parameters TEXT NOT NULL,
            new_parameters TEXT NOT NULL,
            performance_before REAL,
            performance_after REAL,
            improvement REAL
        )""")
        
        # Strategy evolution table
        cursor.execute("""CREATE TABLE IF NOT EXISTS strategy_evolution (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            generation INTEGER NOT NULL,
            strategy_id TEXT NOT NULL,
            parameters TEXT NOT NULL,
            fitness_score REAL NOT NULL,
            parent_ids TEXT
        )""")
        
        conn.commit()
        conn.close()
        
    def record_performance(self, strategy: str, parameters: Dict, performance: Dict,
                          market_conditions: Dict = None):
        """Record strategy performance for learning
        
        Args:
            strategy: Strategy name
            parameters: Strategy parameters used
            performance: Performance metrics
            market_conditions: Market conditions during execution
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""INSERT INTO performance_feedback 
            (strategy, parameters, profit, win_rate, sharpe_ratio, max_drawdown, 
             trades_count, market_conditions)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (strategy,
             json.dumps(parameters),
             performance.get('profit', 0.0),
             performance.get('win_rate', 0.0),
             performance.get('sharpe_ratio'),
             performance.get('max_drawdown'),
             performance.get('trades_count', 0),
             json.dumps(market_conditions) if market_conditions else None))
        
        conn.commit()
        conn.close()
        
        # Add to feedback buffer
        self.feedback_buffer.append({
            'strategy': strategy,
            'parameters': parameters,
            'performance': performance,
            'market_conditions': market_conditions,
            'timestamp': datetime.now()
        })
        
        # Trigger learning if buffer is full
        if len(self.feedback_buffer) >= self.config['min_samples_for_learning']:
            self.learn_from_feedback()

    def record_outcome_event(self, event: Dict):
        """Ingest outcome event from planner/execution for later learning.

        Expected keys: strategy, parameters, profit, win_rate, trades_count, regime
        """
        try:
            self.record_performance(
                strategy=event.get('strategy', 'unknown'),
                parameters=event.get('parameters', {}),
                performance={
                    'profit': event.get('profit', 0.0),
                    'win_rate': event.get('win_rate', 0.0),
                    'sharpe_ratio': event.get('sharpe_ratio'),
                    'max_drawdown': event.get('max_drawdown'),
                    'trades_count': event.get('trades_count', 0),
                },
                market_conditions={'regime': event.get('regime', 'unknown')}
            )
        except Exception:
            # Non-blocking; learning is best-effort
            pass
            
    def learn_from_feedback(self):
        """Learn from accumulated feedback and adapt strategies"""
        if not self.config['learning_enabled']:
            return
            
        if len(self.feedback_buffer) < self.config['min_samples_for_learning']:
            return
            
        print("🧠 Starting learning cycle...")
        
        # Analyze performance patterns
        patterns = self._analyze_patterns()
        
        # Identify successful parameter combinations
        successful_params = self._identify_successful_parameters()
        
        # Generate parameter improvements
        improvements = self._generate_improvements(successful_params, patterns)
        
        # Apply improvements
        adaptations = self._apply_improvements(improvements)
        
        # Update metrics
        self.metrics['learning_cycles'] += 1
        self.metrics['adaptations_made'] += len(adaptations)
        self.metrics['last_learning'] = datetime.now().isoformat()
        
        # Clear feedback buffer
        self.feedback_buffer = []
        
        print(f"✅ Learning cycle complete. {len(adaptations)} adaptations made.")
        
        return adaptations
        
    def _analyze_patterns(self):
        """Analyze performance patterns from feedback"""
        if not self.feedback_buffer:
            return {}
            
        # Group by strategy
        by_strategy = {}
        for feedback in self.feedback_buffer:
            strategy = feedback['strategy']
            if strategy not in by_strategy:
                by_strategy[strategy] = []
            by_strategy[strategy].append(feedback)
            
        patterns = {}
        for strategy, feedbacks in by_strategy.items():
            profits = [f['performance'].get('profit', 0) for f in feedbacks]
            win_rates = [f['performance'].get('win_rate', 0) for f in feedbacks]
            
            patterns[strategy] = {
                'avg_profit': np.mean(profits),
                'std_profit': np.std(profits),
                'avg_win_rate': np.mean(win_rates),
                'trend': 'improving' if np.polyfit(range(len(profits)), profits, 1)[0] > 0 else 'declining',
                'consistency': 1.0 / (np.std(profits) + 1e-8)
            }
            
        return patterns
        
    def _identify_successful_parameters(self):
        """Identify parameter combinations that performed well"""
        if not self.feedback_buffer:
            return {}
            
        # Sort by performance
        sorted_feedback = sorted(
            self.feedback_buffer,
            key=lambda x: x['performance'].get('profit', 0),
            reverse=True
        )
        
        # Take top 20% performers
        top_performers = sorted_feedback[:max(1, len(sorted_feedback) // 5)]
        
        # Extract parameter patterns
        successful_params = {}
        for feedback in top_performers:
            strategy = feedback['strategy']
            if strategy not in successful_params:
                successful_params[strategy] = []
            successful_params[strategy].append(feedback['parameters'])
            
        return successful_params
        
    def _generate_improvements(self, successful_params, patterns):
        """Generate parameter improvements based on learning"""
        improvements = {}
        
        for strategy, param_sets in successful_params.items():
            if not param_sets:
                continue
                
            # Average successful parameters
            avg_params = {}
            param_keys = param_sets[0].keys()
            
            for key in param_keys:
                values = [p[key] for p in param_sets if key in p]
                if values:
                    if isinstance(values[0], (int, float)):
                        avg_params[key] = np.mean(values)
                    else:
                        # For non-numeric, use most common
                        avg_params[key] = max(set(values), key=values.count)
                        
            # Add adaptation based on trend
            if strategy in patterns:
                pattern = patterns[strategy]
                if pattern['trend'] == 'declining':
                    # Increase exploration
                    for key in avg_params:
                        if isinstance(avg_params[key], (int, float)):
                            avg_params[key] *= (1.0 + np.random.uniform(-0.1, 0.1))
                            
            improvements[strategy] = avg_params
            
        return improvements
        
    def _apply_improvements(self, improvements):
        """Apply parameter improvements"""
        adaptations = []
        
        for strategy, new_params in improvements.items():
            # Get current parameters from recent feedback
            current_params = None
            for feedback in reversed(self.feedback_buffer):
                if feedback['strategy'] == strategy:
                    current_params = feedback['parameters']
                    break
                    
            if current_params is None:
                continue
                
            # Record adaptation
            adaptation = {
                'strategy': strategy,
                'old_parameters': current_params,
                'new_parameters': new_params,
                'timestamp': datetime.now()
            }
            
            # Save to database
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute("""INSERT INTO learning_history 
                (adaptation_type, old_parameters, new_parameters)
                VALUES (?, ?, ?)""",
                ('parameter_optimization',
                 json.dumps(current_params),
                 json.dumps(new_params)))
            
            conn.commit()
            conn.close()
            
            adaptations.append(adaptation)
            
        return adaptations
        
    def evolve_strategies_genetic(self, population_size=None):
        """Evolve strategies using genetic algorithm
        
        Args:
            population_size: Size of population (uses config if None)
            
        Returns:
            New generation of strategy parameters
        """
        population_size = population_size or self.config['genetic_algorithm']['population_size']
        
        # Get recent high-performing strategies
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""SELECT strategy, parameters, profit, win_rate
            FROM performance_feedback
            ORDER BY profit DESC
            LIMIT ?""", (population_size,))
        
        population = []
        for row in cursor.fetchall():
            population.append({
                'strategy': row[0],
                'parameters': json.loads(row[1]),
                'fitness': row[2] * row[3]  # profit * win_rate
            })
            
        conn.close()
        
        if len(population) < 2:
            return []
            
        # Evolution loop
        new_generation = []
        
        # Elitism: keep top performers
        elite_size = self.config['genetic_algorithm']['elite_size']
        elite = sorted(population, key=lambda x: x['fitness'], reverse=True)[:elite_size]
        new_generation.extend(elite)
        
        # Generate rest through crossover and mutation
        while len(new_generation) < population_size:
            # Selection (tournament)
            parent1 = self._tournament_select(population)
            parent2 = self._tournament_select(population)
            
            # Crossover
            if np.random.random() < self.config['genetic_algorithm']['crossover_rate']:
                offspring = self._crossover(parent1, parent2)
            else:
                offspring = parent1.copy()
                
            # Mutation
            if np.random.random() < self.config['genetic_algorithm']['mutation_rate']:
                offspring = self._mutate(offspring)
                
            new_generation.append(offspring)
            
        # Record new generation
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        generation_num = self.metrics['learning_cycles']
        
        for idx, individual in enumerate(new_generation):
            cursor.execute("""INSERT INTO strategy_evolution 
                (generation, strategy_id, parameters, fitness_score)
                VALUES (?, ?, ?, ?)""",
                (generation_num,
                 f"gen{generation_num}_ind{idx}",
                 json.dumps(individual['parameters']),
                 individual['fitness']))
                 
        conn.commit()
        conn.close()
        
        return new_generation
        
    def _tournament_select(self, population, tournament_size=3):
        """Tournament selection for genetic algorithm"""
        tournament = np.random.choice(population, min(tournament_size, len(population)), replace=False)
        return max(tournament, key=lambda x: x['fitness'])
        
    def _crossover(self, parent1, parent2):
        """Crossover two parameter sets"""
        offspring = {'parameters': {}, 'fitness': 0.0}
        offspring['strategy'] = parent1['strategy']
        
        # Uniform crossover for parameters
        for key in parent1['parameters']:
            if key in parent2['parameters']:
                if np.random.random() < 0.5:
                    offspring['parameters'][key] = parent1['parameters'][key]
                else:
                    offspring['parameters'][key] = parent2['parameters'][key]
            else:
                offspring['parameters'][key] = parent1['parameters'][key]
                
        return offspring
        
    def _mutate(self, individual):
        """Mutate parameter set"""
        mutated = individual.copy()
        mutated['parameters'] = individual['parameters'].copy()
        
        # Mutate random parameters
        for key in mutated['parameters']:
            if np.random.random() < 0.3:  # 30% chance to mutate each parameter
                value = mutated['parameters'][key]
                if isinstance(value, (int, float)):
                    # Add gaussian noise
                    mutated['parameters'][key] = value * (1.0 + np.random.normal(0, 0.1))
                    
        return mutated
        
    def get_recommended_parameters(self, strategy):
        """Get recommended parameters for a strategy
        
        Args:
            strategy: Strategy name
            
        Returns:
            Recommended parameters
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get best performing recent parameters
        cursor.execute("""SELECT parameters, profit, win_rate
            FROM performance_feedback
            WHERE strategy = ?
            ORDER BY (profit * win_rate) DESC
            LIMIT 1""", (strategy,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return json.loads(row[0])
        return None
        
    def get_learning_report(self):
        """Generate learning report"""
        conn = sqlite3.connect(self.db_path)
        
        # Get adaptation history
        adaptations = pd.read_sql_query(
            "SELECT * FROM learning_history ORDER BY timestamp DESC LIMIT 10",
            conn
        )
        
        # Get performance trends
        performance = pd.read_sql_query(
            "SELECT * FROM performance_feedback ORDER BY timestamp DESC LIMIT 100",
            conn
        )
        
        conn.close()
        
        report = {
            'metrics': self.metrics,
            'recent_adaptations': adaptations.to_dict('records') if not adaptations.empty else [],
            'performance_summary': {
                'avg_profit': performance['profit'].mean() if not performance.empty else 0,
                'avg_win_rate': performance['win_rate'].mean() if not performance.empty else 0,
                'total_trades': performance['trades_count'].sum() if not performance.empty else 0
            },
            'config': self.config
        }
        
        return report
        
    def get_status(self):
        """Get learning pipeline status"""
        return {
            'learning_enabled': self.config['learning_enabled'],
            'metrics': self.metrics,
            'feedback_buffer_size': len(self.feedback_buffer),
            'ready_for_learning': len(self.feedback_buffer) >= self.config['min_samples_for_learning']
        }


# Test functionality
def test_self_learning():
    """Test self-learning pipeline"""
    print("🧪 Testing Self-Learning Pipeline...")
    
    pipeline = SelfLearningPipeline()
    
    # Simulate some performance feedback
    for i in range(15):
        pipeline.record_performance(
            strategy='momentum',
            parameters={'lookback': 14 + i, 'threshold': 0.02},
            performance={
                'profit': np.random.uniform(50, 200),
                'win_rate': np.random.uniform(0.5, 0.8),
                'sharpe_ratio': np.random.uniform(1.0, 2.5),
                'trades_count': np.random.randint(5, 20)
            },
            market_conditions={'regime': 'trending', 'volatility': 'medium'}
        )
        
    # Get recommendations
    recommended = pipeline.get_recommended_parameters('momentum')
    print(f"✅ Recommended parameters: {recommended}")
    
    # Get report
    report = pipeline.get_learning_report()
    print(f"✅ Learning report: {report['metrics']}")
    
    # Evolve strategies
    new_gen = pipeline.evolve_strategies_genetic(population_size=5)
    print(f"✅ Evolved {len(new_gen)} new strategies")
    
    print(f"✅ Status: {pipeline.get_status()}")


if __name__ == '__main__':
    test_self_learning()
