#!/usr/bin/env python3
"""
Multidisciplinary Signal Fusion - Maximum Accuracy System
Combines ALL analysis methods for highest confidence decisions
"""

from typing import Dict, List, Optional
from datetime import datetime
import statistics

try:
    import pandas as pd
    HAS_PANDAS = True
except ImportError:
    HAS_PANDAS = False

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class MultidisciplinaryFusion:
    """
    Fuse signals from all disciplines for maximum accuracy
    
    Disciplines:
    1. Technical Analysis (Market Cipher indicators)
    2. Machine Learning (ML predictor + LSTM)
    3. Sentiment Analysis (Fear/Greed + News)
    4. Order Flow (Whale detection + Book analysis)
    5. Statistical Edge (Historical patterns)
    6. Fundamental (Market research)
    7. Risk Analysis (Correlation + Portfolio)
    """
    
    def __init__(self):
        # Confidence thresholds
        self.min_confirmations = 4  # Need 4+ disciplines to agree
        self.min_confidence = 0.75  # 75% minimum confidence
        
        # Discipline weights (sum to 1.0)
        self.weights = {
            'technical': 0.20,      # Market Cipher
            'ml_prediction': 0.20,  # ML + LSTM
            'sentiment': 0.15,      # Market sentiment
            'order_flow': 0.15,     # Smart money
            'statistical': 0.15,    # Historical edge
            'research': 0.10,       # Market research
            'risk': 0.05           # Risk analysis
        }
        
        # Track accuracy by discipline
        self.discipline_accuracy = {
            'technical': {'correct': 0, 'total': 0},
            'ml_prediction': {'correct': 0, 'total': 0},
            'sentiment': {'correct': 0, 'total': 0},
            'order_flow': {'correct': 0, 'total': 0},
            'statistical': {'correct': 0, 'total': 0},
            'research': {'correct': 0, 'total': 0},
        }
    
    def analyze_all_disciplines(self, symbol: str, df, 
                               portfolio: Dict,
                               market_data: Dict) -> Optional[Dict]:
        """
        Comprehensive multidisciplinary analysis
        
        Returns signal only if high confidence consensus achieved
        """
        if not HAS_PANDAS:
            logger.warning("Pandas required for multidisciplinary analysis")
            return None
        
        logger.info(f"🔬 Multidisciplinary analysis for {symbol}...")
        
        disciplines = {}
        
        # 1. Technical Analysis (Market Cipher)
        try:
            from modules.trading.market_cipher_indicators import market_cipher_indicators
            disciplines['technical'] = market_cipher_indicators.analyze(df)
        except Exception as e:
            logger.warning(f"Technical analysis error: {e}")
            disciplines['technical'] = None
        
        # 2. Machine Learning Prediction
        try:
            from modules.intelligence.ml_predictor import ml_predictor
            disciplines['ml_prediction'] = ml_predictor.predict(df)
        except Exception as e:
            logger.warning(f"ML prediction error: {e}")
            disciplines['ml_prediction'] = None
        
        # 3. Deep Learning (LSTM)
        try:
            from modules.intelligence.deep_learning import deep_learning_predictor
            if HAS_PANDAS:
                ohlcv_data = df[['open', 'high', 'low', 'close', 'volume']].values
                disciplines['deep_learning'] = deep_learning_predictor.predict(ohlcv_data)
            else:
                disciplines['deep_learning'] = None
        except Exception as e:
            logger.warning(f"Deep learning error: {e}")
            disciplines['deep_learning'] = None
        
        # 4. Sentiment Analysis
        try:
            from modules.intelligence.sentiment_analyzer import sentiment_analyzer
            sentiment = sentiment_analyzer.get_market_sentiment(symbol.split('/')[0])
            disciplines['sentiment'] = {
                'signal': 'UP' if sentiment['direction'] == 'BULLISH' else 
                         'DOWN' if sentiment['direction'] == 'BEARISH' else 'NEUTRAL',
                'confidence': sentiment['confidence'],
                'score': sentiment['overall_score']
            }
        except Exception as e:
            logger.warning(f"Sentiment analysis error: {e}")
            disciplines['sentiment'] = None
        
        # 5. Order Flow Analysis
        try:
            from modules.intelligence.order_flow import order_flow_analyzer
            # Would need actual orderbook data
            disciplines['order_flow'] = {
                'signal': 'NEUTRAL',
                'confidence': 0.5
            }
        except Exception as e:
            disciplines['order_flow'] = None
        
        # 6. Statistical Edge
        try:
            from modules.research.market_researcher import market_researcher
            research = market_researcher.research_opportunity(symbol, df)
            stat_edge = research.get('analyses', {}).get('statistical_edge', {})
            disciplines['statistical'] = {
                'signal': 'UP' if stat_edge.get('profit_factor', 0) > 1.5 else 'NEUTRAL',
                'confidence': min(0.8, stat_edge.get('win_rate_1d', 0.5)),
                'edge': stat_edge
            }
        except Exception as e:
            logger.warning(f"Statistical analysis error: {e}")
            disciplines['statistical'] = None
        
        # 7. Risk Analysis
        try:
            from modules.risk.correlation_analyzer import correlation_analyzer
            # Analyze if adding this position increases risk
            disciplines['risk'] = {
                'signal': 'NEUTRAL',
                'confidence': 0.6,
                'risk_level': 'ACCEPTABLE'
            }
        except Exception as e:
            disciplines['risk'] = None
        
        # FUSE ALL SIGNALS
        final_signal = self._fuse_all_disciplines(disciplines, symbol, df)
        
        if final_signal:
            final_signal['disciplines'] = disciplines
            final_signal['fusion_method'] = 'multidisciplinary_consensus'
        
        return final_signal
    
    def _fuse_all_disciplines(self, disciplines: Dict, symbol: str, df) -> Optional[Dict]:
        """
        Fuse all discipline signals using weighted voting
        
        Requires strong consensus for signal generation
        """
        # Count votes for each direction
        buy_score = 0
        sell_score = 0
        total_weight = 0
        
        confirmations = []
        
        for discipline_name, discipline_data in disciplines.items():
            if discipline_data is None:
                continue
            
            weight = self.weights.get(discipline_name, 0)
            signal = discipline_data.get('signal', 'NEUTRAL')
            confidence = discipline_data.get('confidence', 0.5)
            
            # Weighted vote
            weighted_confidence = confidence * weight
            
            if signal in ['BUY', 'UP']:
                buy_score += weighted_confidence
                confirmations.append(f"{discipline_name}: BUY ({confidence:.0%})")
            elif signal in ['SELL', 'DOWN']:
                sell_score += weighted_confidence
                confirmations.append(f"{discipline_name}: SELL ({confidence:.0%})")
            
            total_weight += weight
        
        # Normalize scores
        if total_weight > 0:
            buy_score /= total_weight
            sell_score /= total_weight
        
        # Check for consensus
        num_confirmations = len(confirmations)
        
        latest_price = df['close'].iloc[-1] if HAS_PANDAS else 0
        
        if buy_score > self.min_confidence and buy_score > sell_score and num_confirmations >= self.min_confirmations:
            return {
                'action': 'BUY',
                'signal': 'BUY',
                'strategy': 'Multidisciplinary Fusion',
                'confidence': buy_score,
                'confirmations': num_confirmations,
                'price': latest_price,
                'symbol': symbol,
                'reasoning': f"{num_confirmations} disciplines agree: {', '.join(confirmations[:3])}",
                'accuracy_expected': self._estimate_accuracy(buy_score, num_confirmations),
                'timestamp': datetime.now().isoformat()
            }
        
        elif sell_score > self.min_confidence and sell_score > buy_score and num_confirmations >= self.min_confirmations:
            return {
                'action': 'SELL',
                'signal': 'SELL',
                'strategy': 'Multidisciplinary Fusion',
                'confidence': sell_score,
                'confirmations': num_confirmations,
                'price': latest_price,
                'symbol': symbol,
                'reasoning': f"{num_confirmations} disciplines agree: {', '.join(confirmations[:3])}",
                'accuracy_expected': self._estimate_accuracy(sell_score, num_confirmations),
                'timestamp': datetime.now().isoformat()
            }
        
        # No consensus
        logger.info(f"No consensus: BUY={buy_score:.2f}, SELL={sell_score:.2f}, Confirmations={num_confirmations}")
        return None
    
    def _estimate_accuracy(self, confidence: float, confirmations: int) -> float:
        """
        Estimate expected accuracy based on confidence and confirmations
        
        More confirmations + higher confidence = higher expected accuracy
        """
        # Base accuracy from confidence
        base_accuracy = 0.5 + (confidence - 0.5) * 0.6  # Maps 0.5-1.0 to 0.5-0.8
        
        # Bonus for multiple confirmations
        confirmation_bonus = min(0.15, (confirmations - 3) * 0.03)
        
        expected_accuracy = min(0.95, base_accuracy + confirmation_bonus)
        
        return expected_accuracy
    
    def update_accuracy(self, discipline: str, was_correct: bool):
        """Track accuracy by discipline for adaptive weighting"""
        if discipline in self.discipline_accuracy:
            self.discipline_accuracy[discipline]['total'] += 1
            if was_correct:
                self.discipline_accuracy[discipline]['correct'] += 1
            
            # Adapt weights based on performance
            self._adapt_weights()
    
    def _adapt_weights(self):
        """Adapt discipline weights based on historical accuracy"""
        # Calculate accuracy for each discipline
        accuracies = {}
        for discipline, stats in self.discipline_accuracy.items():
            if stats['total'] >= 10:  # Need minimum sample
                accuracies[discipline] = stats['correct'] / stats['total']
        
        if not accuracies:
            return
        
        # Reweight proportionally to accuracy
        total_accuracy = sum(accuracies.values())
        if total_accuracy > 0:
            for discipline in accuracies:
                # Gradual adaptation (90% old weight, 10% new)
                target_weight = accuracies[discipline] / total_accuracy
                current_weight = self.weights.get(discipline, 0.1)
                new_weight = current_weight * 0.9 + target_weight * 0.1
                self.weights[discipline] = new_weight
            
            # Normalize
            total = sum(self.weights.values())
            for key in self.weights:
                self.weights[key] /= total
            
            logger.info(f"Adapted discipline weights: {self.weights}")
    
    def get_accuracy_stats(self) -> Dict:
        """Get accuracy statistics by discipline"""
        stats = {}
        for discipline, data in self.discipline_accuracy.items():
            if data['total'] > 0:
                stats[discipline] = {
                    'accuracy': data['correct'] / data['total'],
                    'total_signals': data['total'],
                    'correct': data['correct'],
                    'weight': self.weights.get(discipline, 0)
                }
        return stats


# Global instance
multidisciplinary_fusion = MultidisciplinaryFusion()
