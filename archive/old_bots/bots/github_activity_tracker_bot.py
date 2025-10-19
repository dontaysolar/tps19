#!/usr/bin/env python3
"""GitHub Activity Tracker - Developer activity as fundamental indicator"""
from datetime import datetime
from typing import Dict

class GitHubActivityTrackerBot:
    def __init__(self):
        self.name = "GitHub_Activity_Tracker"
        self.version = "1.0.0"
        self.enabled = True
        self.metrics = {'projects_tracked': 0}
    
    def analyze_repo_activity(self, repo_data: Dict) -> Dict:
        """Analyze GitHub repository activity"""
        commits_30d = repo_data.get('commits_30d', 0)
        contributors = repo_data.get('active_contributors', 0)
        stars = repo_data.get('stars', 0)
        forks = repo_data.get('forks', 0)
        
        # Activity score
        activity_score = 0
        
        if commits_30d > 100:
            activity_score += 40
        elif commits_30d > 50:
            activity_score += 25
        elif commits_30d > 10:
            activity_score += 10
        
        if contributors > 20:
            activity_score += 30
        elif contributors > 10:
            activity_score += 20
        elif contributors > 5:
            activity_score += 10
        
        if stars > 10000:
            activity_score += 20
        elif stars > 1000:
            activity_score += 10
        
        if forks > 1000:
            activity_score += 10
        
        # Generate signal
        if activity_score >= 70:
            signal, confidence = 'BUY', 0.75
            assessment = 'ACTIVE_DEVELOPMENT'
        elif activity_score >= 40:
            signal, confidence = 'HOLD', 0.60
            assessment = 'MODERATE_DEVELOPMENT'
        else:
            signal, confidence = 'SELL', 0.65
            assessment = 'LOW_DEVELOPMENT'
        
        self.metrics['projects_tracked'] += 1
        
        return {
            'activity_score': activity_score,
            'assessment': assessment,
            'commits_30d': commits_30d,
            'contributors': contributors,
            'stars': stars,
            'forks': forks,
            'signal': signal,
            'confidence': confidence,
            'timestamp': datetime.now().isoformat()
        }
    
    def get_status(self) -> Dict:
        return {'name': self.name, 'version': self.version, 'enabled': self.enabled, 'metrics': self.metrics, 'last_update': datetime.now().isoformat()}

if __name__ == '__main__':
    bot = GitHubActivityTrackerBot()
    print(f"✅ {bot.name} v{bot.version} initialized")
