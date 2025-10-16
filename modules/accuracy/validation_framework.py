#!/usr/bin/env python3
"""
Accuracy Validation Framework
Ensures signals meet high accuracy standards before execution
"""

from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import statistics

from modules.utils.logger import get_logger

logger = get_logger(__name__)


class AccuracyValidator:
    """
    Validates signal accuracy before execution
    Tracks actual vs predicted performance
    """
    
    def __init__(self):
        # Accuracy tracking
        self.signal_history = []
        self.accuracy_by_strategy = {}
        self.accuracy_by_confidence = {}
        
        # Validation thresholds
        self.min_accuracy_required = 0.60  # 60% minimum
        self.min_sample_size = 20          # Need 20 signals to judge
        self.confidence_accuracy_map = {}   # Maps confidence to actual accuracy
        
    def validate_signal(self, signal: Dict, portfolio: Dict) -> Tuple[bool, str, float]:
        """
        Validate signal meets accuracy requirements
        
        Returns: (approved, reason, expected_accuracy)
        """
        strategy = signal.get('strategy', 'unknown')
        confidence = signal.get('confidence', 0.5)
        
        # Check strategy historical accuracy
        strategy_accuracy = self._get_strategy_accuracy(strategy)
        
        if strategy_accuracy is not None:
            if strategy_accuracy < self.min_accuracy_required:
                return False, f"Strategy accuracy too low: {strategy_accuracy:.2%}", strategy_accuracy
        
        # Check confidence level accuracy
        confidence_bucket = self._get_confidence_bucket(confidence)
        bucket_accuracy = self._get_bucket_accuracy(confidence_bucket)
        
        if bucket_accuracy is not None:
            if bucket_accuracy < self.min_accuracy_required:
                return False, f"Confidence level historically inaccurate: {bucket_accuracy:.2%}", bucket_accuracy
        
        # Estimate expected accuracy
        expected_accuracy = self._estimate_accuracy(signal, strategy_accuracy, bucket_accuracy)
        
        # Require higher accuracy if portfolio is stressed
        if portfolio.get('current_drawdown', 0) > 0.05:
            # In drawdown, require 70%+ accuracy
            if expected_accuracy < 0.70:
                return False, f"Accuracy too low during drawdown: {expected_accuracy:.2%}", expected_accuracy
        
        return True, f"Expected accuracy: {expected_accuracy:.2%}", expected_accuracy
    
    def record_signal_outcome(self, signal: Dict, actual_result: float):
        """
        Record actual outcome of signal for accuracy tracking
        
        Args:
            signal: Original signal
            actual_result: Actual P&L percentage
        """
        strategy = signal.get('strategy', 'unknown')
        confidence = signal.get('confidence', 0.5)
        predicted_direction = signal.get('signal', 'NEUTRAL')
        
        # Determine if prediction was correct
        was_correct = (
            (predicted_direction in ['BUY', 'UP'] and actual_result > 0) or
            (predicted_direction in ['SELL', 'DOWN'] and actual_result < 0)
        )
        
        # Record in history
        record = {
            'timestamp': signal.get('timestamp', datetime.now().isoformat()),
            'strategy': strategy,
            'confidence': confidence,
            'predicted': predicted_direction,
            'actual_result': actual_result,
            'correct': was_correct,
            'confidence_bucket': self._get_confidence_bucket(confidence)
        }
        
        self.signal_history.append(record)
        
        # Update strategy accuracy
        if strategy not in self.accuracy_by_strategy:
            self.accuracy_by_strategy[strategy] = {'correct': 0, 'total': 0}
        
        self.accuracy_by_strategy[strategy]['total'] += 1
        if was_correct:
            self.accuracy_by_strategy[strategy]['correct'] += 1
        
        # Update confidence bucket accuracy
        bucket = record['confidence_bucket']
        if bucket not in self.accuracy_by_confidence:
            self.accuracy_by_confidence[bucket] = {'correct': 0, 'total': 0}
        
        self.accuracy_by_confidence[bucket]['total'] += 1
        if was_correct:
            self.accuracy_by_confidence[bucket]['correct'] += 1
        
        logger.info(f"Signal outcome recorded: {strategy} {predicted_direction} -> "
                   f"{'✅ Correct' if was_correct else '❌ Wrong'}")
    
    def _get_strategy_accuracy(self, strategy: str) -> Optional[float]:
        """Get historical accuracy for strategy"""
        if strategy not in self.accuracy_by_strategy:
            return None
        
        stats = self.accuracy_by_strategy[strategy]
        if stats['total'] < self.min_sample_size:
            return None  # Not enough data
        
        return stats['correct'] / stats['total']
    
    def _get_confidence_bucket(self, confidence: float) -> str:
        """Get confidence bucket (0.5-0.6, 0.6-0.7, etc.)"""
        if confidence < 0.6:
            return '0.5-0.6'
        elif confidence < 0.7:
            return '0.6-0.7'
        elif confidence < 0.8:
            return '0.7-0.8'
        elif confidence < 0.9:
            return '0.8-0.9'
        else:
            return '0.9-1.0'
    
    def _get_bucket_accuracy(self, bucket: str) -> Optional[float]:
        """Get actual accuracy for confidence bucket"""
        if bucket not in self.accuracy_by_confidence:
            return None
        
        stats = self.accuracy_by_confidence[bucket]
        if stats['total'] < 10:  # Need at least 10 samples
            return None
        
        return stats['correct'] / stats['total']
    
    def _estimate_accuracy(self, signal: Dict, 
                          strategy_accuracy: Optional[float],
                          bucket_accuracy: Optional[float]) -> float:
        """
        Estimate expected accuracy for this signal
        
        Combines:
        - Stated confidence
        - Historical strategy accuracy
        - Historical confidence bucket accuracy
        - Number of confirmations
        """
        confidence = signal.get('confidence', 0.5)
        confirmations = signal.get('confirmations', 1)
        
        # Start with confidence
        accuracy = confidence
        
        # Adjust based on strategy history
        if strategy_accuracy is not None:
            # Weight: 50% confidence, 50% historical
            accuracy = (accuracy + strategy_accuracy) / 2
        
        # Adjust based on confidence bucket history
        if bucket_accuracy is not None:
            # If bucket historically performs better/worse, adjust
            adjustment = bucket_accuracy - confidence
            accuracy += adjustment * 0.3  # 30% weight to historical calibration
        
        # Bonus for multiple confirmations
        if confirmations > 3:
            confirmation_bonus = min(0.10, (confirmations - 3) * 0.02)
            accuracy += confirmation_bonus
        
        # Cap between 0.3 and 0.95
        return max(0.3, min(0.95, accuracy))
    
    def get_accuracy_report(self) -> Dict:
        """
        Generate comprehensive accuracy report
        """
        if not self.signal_history:
            return {'error': 'No signal history'}
        
        total_signals = len(self.signal_history)
        correct_signals = sum(1 for s in self.signal_history if s['correct'])
        overall_accuracy = correct_signals / total_signals
        
        # By strategy
        by_strategy = {}
        for strategy, stats in self.accuracy_by_strategy.items():
            if stats['total'] > 0:
                by_strategy[strategy] = {
                    'accuracy': stats['correct'] / stats['total'],
                    'total': stats['total'],
                    'correct': stats['correct']
                }
        
        # By confidence bucket
        by_confidence = {}
        for bucket, stats in self.accuracy_by_confidence.items():
            if stats['total'] > 0:
                by_confidence[bucket] = {
                    'accuracy': stats['correct'] / stats['total'],
                    'total': stats['total'],
                    'stated_confidence': bucket,
                    'actual_accuracy': stats['correct'] / stats['total']
                }
        
        # Confidence calibration
        calibration = self._analyze_calibration()
        
        return {
            'overall_accuracy': overall_accuracy,
            'total_signals': total_signals,
            'correct_signals': correct_signals,
            'by_strategy': by_strategy,
            'by_confidence': by_confidence,
            'calibration': calibration,
            'meets_minimum': overall_accuracy >= self.min_accuracy_required
        }
    
    def _analyze_calibration(self) -> Dict:
        """
        Analyze if stated confidence matches actual accuracy
        
        Well-calibrated system: 70% confidence = 70% actual accuracy
        """
        calibration_errors = []
        
        for bucket, stats in self.accuracy_by_confidence.items():
            if stats['total'] < 10:
                continue
            
            # Extract stated confidence (midpoint of bucket)
            if bucket == '0.5-0.6':
                stated = 0.55
            elif bucket == '0.6-0.7':
                stated = 0.65
            elif bucket == '0.7-0.8':
                stated = 0.75
            elif bucket == '0.8-0.9':
                stated = 0.85
            else:
                stated = 0.95
            
            actual = stats['correct'] / stats['total']
            error = actual - stated
            
            calibration_errors.append({
                'bucket': bucket,
                'stated': stated,
                'actual': actual,
                'error': error
            })
        
        if not calibration_errors:
            return {'status': 'insufficient_data'}
        
        avg_error = statistics.mean([e['error'] for e in calibration_errors])
        
        if abs(avg_error) < 0.05:
            status = 'well_calibrated'
        elif avg_error > 0:
            status = 'overconfident'  # Stating higher confidence than deserved
        else:
            status = 'underconfident'  # Actual accuracy better than stated
        
        return {
            'status': status,
            'average_error': avg_error,
            'errors_by_bucket': calibration_errors
        }


# Global instance
accuracy_validator = AccuracyValidator()
