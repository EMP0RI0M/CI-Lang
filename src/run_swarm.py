import argparse
import pickle
import sys
import os
from swarms.engine import SwarmManager
from swarms.monitor import StabilityMonitor

def main():
    parser = argparse.ArgumentParser(description="CI-Lang Swarm Executor")
    parser.add_argument("--bytecode", type=str, required=True, help="Path to compiled .bc file")
    parser.add_argument("--steps", type=int, default=100, help="Number of simulation ticks")
    parser.add_argument("--agents", type=int, default=10, help="Number of agents in swarm")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.bytecode):
        print(f"Error: Bytecode file not found: {args.bytecode}")
        sys.exit(1)
        
    try:
        with open(args.bytecode, 'rb') as f:
            bytecode = pickle.load(f)
            
        manager = SwarmManager(bytecode, agent_count=args.agents)
        monitor = StabilityMonitor()
        
        print(f"--- CI-Lang Swarm Execution: {os.path.basename(args.bytecode)} ---")
        manager.run_simulation(ticks=args.steps, monitor=monitor)
        # monitor.report() # Optional for internal tests
        
    except Exception as e:
        print(f"RUNTIME CRASH: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
