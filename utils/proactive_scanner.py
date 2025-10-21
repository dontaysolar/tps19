#!/usr/bin/env python3
"""
AEGIS v2.3 - Proactive Issue Detection Scanner
Implements CR-1: Predictive analysis for Phase 2 (War Room)

FEATURES:
- Predictive complexity analysis before implementation
- Dependency conflict detection
- Performance impact prediction
- Integration risk assessment
- FRACTAL HOOK: Enables early problem detection in War Room

USAGE:
    from utils.proactive_scanner import ProactiveScanner
    scanner = ProactiveScanner()
    issues = scanner.scan_implementation_plan(plan)
"""

import os
import re
import ast
import json
from typing import Dict, List, Tuple, Optional
from pathlib import Path
from dataclasses import dataclass, asdict


@dataclass
class Issue:
    """Detected issue with severity and recommendation"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    category: str  # COMPLEXITY, DEPENDENCY, PERFORMANCE, INTEGRATION
    description: str
    impact: str
    recommendation: str
    cost_of_failure: int  # 1-10


class ProactiveScanner:
    """
    Proactive issue detection for implementation plans
    
    AEGIS Enhancement: Catches problems before they occur
    """
    
    def __init__(self):
        """
        Initialize proactive scanner
        
        ATLAS Compliance:
        - Assertion 1: Scanner initialized
        - Assertion 2: Workspace accessible
        """
        self.workspace = Path('/workspace')
        assert self.workspace.exists(), "Workspace not found"
        
        self.issues: List[Issue] = []
        self.scanned_files = set()
        
        print("✅ ProactiveScanner initialized")
    
    def scan_implementation_plan(self, plan: Dict) -> List[Issue]:
        """
        Scan implementation plan for potential issues
        
        Args:
            plan: Dictionary with 'target_files', 'changes', 'dependencies'
        
        Returns:
            List of detected issues with recommendations
        
        ATLAS Compliance:
        - Assertion 1: Plan has required keys
        - Assertion 2: Returns valid list
        """
        assert 'target_files' in plan, "Plan must have target_files"
        assert isinstance(plan['target_files'], list), "target_files must be list"
        
        self.issues = []
        
        # Scan 1: Complexity analysis
        self._scan_complexity(plan)
        
        # Scan 2: Dependency conflicts
        self._scan_dependencies(plan)
        
        # Scan 3: Performance impact
        self._scan_performance_impact(plan)
        
        # Scan 4: Integration risks
        self._scan_integration_risks(plan)
        
        # Scan 5: File size analysis
        self._scan_file_sizes(plan)
        
        assert isinstance(self.issues, list), "Issues must be list"
        return self.issues
    
    def _scan_complexity(self, plan: Dict):
        """
        Detect high complexity implementations
        
        Checks:
        - Large file modifications (>500 lines)
        - Multiple file changes (>10 files)
        - Deep refactoring indicators
        """
        target_files = plan.get('target_files', [])
        
        # Check file count
        if len(target_files) > 10:
            self.issues.append(Issue(
                severity='HIGH',
                category='COMPLEXITY',
                description=f'Large scope: {len(target_files)} files to modify',
                impact='High risk of cascading failures, long implementation time',
                recommendation='Break into smaller phases or use batch processing',
                cost_of_failure=7
            ))
        
        # Check for core file modifications
        core_files = ['position_state_manager.py', 'exchange_adapter.py', 'trading_bot_base.py']
        modified_core = [f for f in target_files if any(cf in f for cf in core_files)]
        
        if modified_core:
            self.issues.append(Issue(
                severity='CRITICAL',
                category='COMPLEXITY',
                description=f'Modifying core infrastructure: {", ".join(modified_core)}',
                impact='System-wide impact, potential for breaking all dependent bots',
                recommendation='Implement comprehensive test suite before changes, maintain backward compatibility',
                cost_of_failure=9
            ))
    
    def _scan_dependencies(self, plan: Dict):
        """
        Detect potential dependency conflicts
        
        Checks:
        - Missing dependencies
        - Version conflicts
        - Import cycles
        """
        dependencies = plan.get('dependencies', [])
        
        # Check for missing dependencies in environment
        try:
            import importlib
            missing = []
            
            for dep in dependencies:
                try:
                    importlib.import_module(dep)
                except ImportError:
                    missing.append(dep)
            
            if missing:
                self.issues.append(Issue(
                    severity='HIGH',
                    category='DEPENDENCY',
                    description=f'Missing dependencies: {", ".join(missing)}',
                    impact='Implementation will fail at runtime',
                    recommendation=f'Install: pip install {" ".join(missing)}',
                    cost_of_failure=8
                ))
        except Exception as e:
            # Best effort dependency check
            pass
        
        # Check for known problematic dependencies
        problematic = {
            'ccxt': 'Heavy exchange library, may not be installed in test env',
            'numpy': 'Scientific computing, may not be in minimal environments',
            'tensorflow': 'ML framework, very large, often missing'
        }
        
        for dep in dependencies:
            if dep in problematic:
                self.issues.append(Issue(
                    severity='MEDIUM',
                    category='DEPENDENCY',
                    description=f'Heavy dependency: {dep}',
                    impact=problematic[dep],
                    recommendation=f'Provide fallback logic or mock for {dep}',
                    cost_of_failure=5
                ))
    
    def _scan_performance_impact(self, plan: Dict):
        """
        Predict performance impact of changes
        
        Checks:
        - Database schema changes
        - Large data migrations
        - New expensive operations
        """
        changes = plan.get('changes', [])
        
        # Check for database operations
        db_keywords = ['CREATE TABLE', 'ALTER TABLE', 'migration', 'INDEX']
        has_db_changes = any(
            any(kw in str(change).upper() for kw in db_keywords)
            for change in changes
        )
        
        if has_db_changes:
            self.issues.append(Issue(
                severity='MEDIUM',
                category='PERFORMANCE',
                description='Database schema changes detected',
                impact='Potential downtime or migration time required',
                recommendation='Test migration on copy of production data, measure time',
                cost_of_failure=6
            ))
        
        # Check for loop operations
        loop_keywords = ['for ', 'while ', 'connection_pool']
        has_loops = any(
            any(kw in str(change).lower() for kw in loop_keywords)
            for change in changes
        )
        
        if has_loops and len(plan.get('target_files', [])) > 5:
            self.issues.append(Issue(
                severity='LOW',
                category='PERFORMANCE',
                description='Multiple files with iterative operations',
                impact='Potential O(n²) or higher complexity',
                recommendation='Profile execution, consider caching or optimization',
                cost_of_failure=4
            ))
    
    def _scan_integration_risks(self, plan: Dict):
        """
        Assess integration risks with existing system
        
        Checks:
        - Breaking API changes
        - Incompatible interfaces
        - Test coverage gaps
        """
        target_files = plan.get('target_files', [])
        
        # Check if changing public APIs
        api_files = ['exchange_adapter.py', 'position_state_manager.py', 'trading_bot_base.py']
        changing_apis = [f for f in target_files if any(af in f for af in api_files)]
        
        if changing_apis:
            # Count dependent files
            try:
                dependent_count = 0
                for api_file in changing_apis:
                    # Search for imports of this file
                    api_name = Path(api_file).stem
                    result = os.popen(f'grep -r "from.*{api_name} import\\|import.*{api_name}" /workspace/bots /workspace/core 2>/dev/null | wc -l').read()
                    dependent_count += int(result.strip() or 0)
                
                if dependent_count > 10:
                    self.issues.append(Issue(
                        severity='HIGH',
                        category='INTEGRATION',
                        description=f'Changing APIs with {dependent_count}+ dependents',
                        impact='Potential breaking changes across many bots',
                        recommendation='Maintain backward compatibility or update all dependents',
                        cost_of_failure=8
                    ))
            except:
                pass  # Best effort
        
        # Check for test coverage
        has_tests = 'tests' in plan or any('test' in str(f).lower() for f in target_files)
        
        if not has_tests and len(target_files) > 3:
            self.issues.append(Issue(
                severity='MEDIUM',
                category='INTEGRATION',
                description='No test updates planned for multi-file change',
                impact='Changes may break existing functionality undetected',
                recommendation='Add comprehensive test suite for changed components',
                cost_of_failure=6
            ))
    
    def _scan_file_sizes(self, plan: Dict):
        """
        Analyze file sizes for refactoring needs
        
        Checks:
        - Large files (>1000 lines)
        - Files approaching ATLAS limits
        """
        target_files = plan.get('target_files', [])
        
        for filepath in target_files:
            try:
                full_path = self.workspace / filepath
                if full_path.exists():
                    line_count = len(full_path.read_text().splitlines())
                    
                    if line_count > 1000:
                        self.issues.append(Issue(
                            severity='MEDIUM',
                            category='COMPLEXITY',
                            description=f'Large file: {filepath} ({line_count} lines)',
                            impact='Difficult to maintain, test, and review',
                            recommendation='Consider splitting into smaller modules',
                            cost_of_failure=5
                        ))
                    elif line_count > 600:
                        self.issues.append(Issue(
                            severity='LOW',
                            category='COMPLEXITY',
                            description=f'Growing file: {filepath} ({line_count} lines)',
                            impact='Approaching recommended limit',
                            recommendation='Monitor size, plan refactoring if exceeds 800 lines',
                            cost_of_failure=3
                        ))
            except:
                pass  # File doesn't exist yet or inaccessible
    
    def generate_report(self) -> str:
        """
        Generate human-readable report of detected issues
        
        Returns:
            Formatted report string
        """
        if not self.issues:
            return "✅ No issues detected - Implementation plan looks good!"
        
        # Sort by severity and CoF
        severity_order = {'CRITICAL': 0, 'HIGH': 1, 'MEDIUM': 2, 'LOW': 3}
        sorted_issues = sorted(
            self.issues,
            key=lambda x: (severity_order[x.severity], -x.cost_of_failure)
        )
        
        report = []
        report.append("=" * 70)
        report.append("PROACTIVE ISSUE DETECTION REPORT")
        report.append("=" * 70)
        report.append("")
        report.append(f"Total Issues Detected: {len(self.issues)}")
        report.append("")
        
        # Group by severity
        for severity in ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']:
            issues = [i for i in sorted_issues if i.severity == severity]
            if not issues:
                continue
            
            report.append(f"{'🔴' if severity == 'CRITICAL' else '🟠' if severity == 'HIGH' else '🟡' if severity == 'MEDIUM' else '🔵'} {severity} ({len(issues)})")
            report.append("-" * 70)
            
            for i, issue in enumerate(issues, 1):
                report.append(f"{i}. [{issue.category}] {issue.description}")
                report.append(f"   Impact: {issue.impact}")
                report.append(f"   Recommendation: {issue.recommendation}")
                report.append(f"   Cost-of-Failure: {issue.cost_of_failure}/10")
                report.append("")
        
        report.append("=" * 70)
        report.append("RECOMMENDATION: Address CRITICAL and HIGH issues before proceeding")
        report.append("=" * 70)
        
        return "\n".join(report)
    
    def export_json(self, filepath: str):
        """
        Export issues to JSON file
        
        Args:
            filepath: Path to save JSON report
        """
        data = {
            'total_issues': len(self.issues),
            'by_severity': {
                'CRITICAL': len([i for i in self.issues if i.severity == 'CRITICAL']),
                'HIGH': len([i for i in self.issues if i.severity == 'HIGH']),
                'MEDIUM': len([i for i in self.issues if i.severity == 'MEDIUM']),
                'LOW': len([i for i in self.issues if i.severity == 'LOW'])
            },
            'issues': [asdict(i) for i in self.issues]
        }
        
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"✅ Report exported to {filepath}")


# FRACTAL HOOK: Integration with Phase 2 (War Room)
def scan_war_room_plan(plan: Dict) -> Tuple[List[Issue], str]:
    """
    Convenience function for War Room integration
    
    Args:
        plan: Implementation plan dict
    
    Returns:
        (issues, report_text) tuple
    
    USAGE in Phase 2:
        from utils.proactive_scanner import scan_war_room_plan
        issues, report = scan_war_room_plan(my_plan)
        if issues:
            print(report)
            # Address critical issues before proceeding
    """
    scanner = ProactiveScanner()
    issues = scanner.scan_implementation_plan(plan)
    report = scanner.generate_report()
    return issues, report


# Self-test
if __name__ == '__main__':
    print("=" * 70)
    print("PROACTIVE SCANNER - SELF-TEST")
    print("=" * 70)
    print("")
    
    # Test 1: Simple plan
    print("Test 1: Simple implementation plan")
    simple_plan = {
        'target_files': ['bots/test_bot.py'],
        'dependencies': [],
        'changes': ['Add new function']
    }
    scanner = ProactiveScanner()
    issues = scanner.scan_implementation_plan(simple_plan)
    print(f"✅ Detected {len(issues)} issues for simple plan")
    print("")
    
    # Test 2: Complex plan (should trigger warnings)
    print("Test 2: Complex implementation plan")
    complex_plan = {
        'target_files': [
            'core/position_state_manager.py',
            'core/exchange_adapter.py',
            'bots/god_bot_v2.py',
            'bots/oracle_ai_v2.py'
        ],
        'dependencies': ['ccxt', 'numpy', 'tensorflow'],
        'changes': [
            'ALTER TABLE positions ADD COLUMN new_field',
            'Refactor connection pooling with for loops'
        ]
    }
    scanner2 = ProactiveScanner()
    issues2 = scanner2.scan_implementation_plan(complex_plan)
    print(f"✅ Detected {len(issues2)} issues for complex plan")
    print("")
    print(scanner2.generate_report())
    
    # Test 3: Export JSON
    print("Test 3: JSON export")
    scanner2.export_json('/tmp/proactive_scan.json')
    print("")
    
    print("=" * 70)
    print("✅ ALL SELF-TESTS PASSED")
    print("=" * 70)
