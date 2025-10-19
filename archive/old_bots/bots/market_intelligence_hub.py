#!/usr/bin/env python3
"""Market Intelligence Hub - Aggregates all market analysis"""
from datetime import datetime
from typing import Dict, List

class MarketIntelligenceHub:
    def __init__(self):
        self.name = "Market_Intelligence_Hub"
        self.version = "1.0.0"
        self.enabled = True
        
        self.intelligence_sources = {}
        self.latest_intelligence = {}
        
        self.metrics = {'sources_registered': 0, 'intel_reports': 0}
    
    def register_source(self, source_name: str, source_instance):
        """Register intelligence source (sentiment, on-chain, etc)"""
        self.intelligence_sources[source_name] = {
            'instance': source_instance,
            'enabled': True,
            'reports_generated': 0,
            'registered_at': datetime.now().isoformat()
        }
        
        self.metrics['sources_registered'] += 1
    
    def gather_intelligence(self, market_data: Dict = None) -> Dict:
        """Gather intelligence from all sources"""
        intelligence = {}
        
        for source_name, source_info in self.intelligence_sources.items():
            if not source_info['enabled']:
                continue
            
            try:
                instance = source_info['instance']
                
                # Try to get analysis
                if hasattr(instance, 'analyze'):
                    report = instance.analyze(market_data or {})
                elif hasattr(instance, 'calculate'):
                    report = instance.calculate(market_data or {})
                elif hasattr(instance, 'get_sentiment'):
                    report = instance.get_sentiment()
                else:
                    report = {'status': 'NO_METHOD'}
                
                intelligence[source_name] = report
                source_info['reports_generated'] += 1
                
            except Exception as e:
                intelligence[source_name] = {'error': str(e)}
        
        self.latest_intelligence = intelligence
        self.metrics['intel_reports'] += 1
        
        return {
            'intelligence': intelligence,
            'sources_consulted': len(intelligence),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_market_sentiment_score(self) -> Dict:
        """Aggregate sentiment across all sources"""
        if not self.latest_intelligence:
            return {'sentiment_score': 0, 'message': 'No intelligence gathered'}
        
        sentiment_scores = []
        
        for source_name, data in self.latest_intelligence.items():
            if 'sentiment' in data:
                sentiment_scores.append(data['sentiment'])
            elif 'sentiment_score' in data:
                sentiment_scores.append(data['sentiment_score'])
        
        if not sentiment_scores:
            return {'sentiment_score': 0, 'sources': 0}
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
        
        if avg_sentiment > 0.3:
            sentiment_label = 'BULLISH'
        elif avg_sentiment < -0.3:
            sentiment_label = 'BEARISH'
        else:
            sentiment_label = 'NEUTRAL'
        
        return {
            'sentiment_score': avg_sentiment,
            'sentiment_label': sentiment_label,
            'sources': len(sentiment_scores),
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {
            'name': self.name,
            'version': self.version,
            'enabled': self.enabled,
            'total_sources': len(self.intelligence_sources),
            'enabled_sources': sum([1 for s in self.intelligence_sources.values() if s['enabled']]),
            'metrics': self.metrics,
            'last_update': datetime.now().isoformat()
        }

if __name__ == '__main__':
    hub = MarketIntelligenceHub()
    print(f"✅ {hub.name} v{hub.version} initialized")
