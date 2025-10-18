#!/usr/bin/env python3
"""
Automated alternating protocol runs
- uflorecer: TPS19 Comprehensive Validation Suite
- helios: TPS19 Main System Comprehensive Tests (Helios-like)

Runs: 30 alternating executions for each protocol (total 60), capturing logs per run.
"""
import os
import sys
import subprocess
from datetime import datetime

workspace_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
logs_dir = os.path.join(workspace_dir, 'logs', 'protocol_runs')
os.makedirs(logs_dir, exist_ok=True)


def run_cmd(name: str, cmd: list):
    start_ts = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    log_file = os.path.join(logs_dir, f"{start_ts}_{name}.log")
    with open(log_file, 'w') as f:
        f.write(f"=== {name} START {datetime.utcnow().isoformat()} ===\n")
        f.write(f"CMD: {' '.join(cmd)}\n\n")
        try:
            res = subprocess.run(cmd, cwd=workspace_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, timeout=600)
            f.write(res.stdout)
            f.write(f"\n=== EXIT {res.returncode} ===\n")
            return res.returncode, log_file
        except subprocess.TimeoutExpired as e:
            f.write(f"\nTIMEOUT after {e.timeout}s\n")
            return 124, log_file


def run_uflorecer(i: int):
    name = f"uflorecer_{i:02d}"
    # Comprehensive validation suite
    cmd = [sys.executable, 'comprehensive_test_suite.py']
    return run_cmd(name, cmd)


def run_helios(i: int):
    name = f"helios_{i:02d}"
    # Main system comprehensive tests
    cmd = [sys.executable, 'tps19_main.py', 'test']
    return run_cmd(name, cmd)


def main():
    results = []
    for i in range(1, 31):
        # uflorecer first
        code_u, log_u = run_uflorecer(i)
        results.append((f"uflorecer_{i}", code_u, log_u))
        if code_u != 0:
            print(f"FAIL uflorecer_{i} -> {log_u}")
            break
        # helios next
        code_h, log_h = run_helios(i)
        results.append((f"helios_{i}", code_h, log_h))
        if code_h != 0:
            print(f"FAIL helios_{i} -> {log_h}")
            break
    else:
        print("All alternating runs completed successfully.")

    # Print summary
    for name, code, path in results:
        print(f"{name}: exit={code} log={path}")

if __name__ == '__main__':
    main()
