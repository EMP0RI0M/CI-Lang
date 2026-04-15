import os
import sys
import argparse
import pickle
from cilexer import Lexer
from ciparser import Parser
from cicompiler import Compiler
from swarms.engine import SwarmManager
from swarms.monitor import StabilityMonitor

def main():
    parser = argparse.ArgumentParser(description="CI-Lang Unified CLI - Chaos Intelligence Runtime")
    parser.add_argument("source", help="Path to .ci source file")
    parser.add_argument("--agents", type=int, default=1, help="Number of agents to spawn (if not specified in script)")
    parser.add_argument("--steps", type=int, default=100, help="Number of simulation steps")
    parser.add_argument("--seed", type=int, help="Global random seed for determinism")
    parser.add_argument("--compile-only", action="store_true", help="Only compile the script to bytecode")
    parser.add_argument("-o", "--output", help="Bytecode output path (default: <source>.bc)")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.source):
        print(f"Error: File not found {args.source}")
        sys.exit(1)
        
    with open(args.source, 'r', encoding='utf-8') as f:
        source_code = f.read()
        
    print(f"--- CI-LANG COMPILER v1.0 ---")
    lexer = Lexer(source_code)
    tokens = lexer.tokenize()
    parser_obj = Parser(tokens)
    ast = parser_obj.parse_program()
    compiler = Compiler()
    bytecode = compiler.compile(ast)
    
    bc_path = args.output or args.source.replace(".ci", ".bc")
    with open(bc_path, 'wb') as f:
        pickle.dump(bytecode, f)
    print(f"Compilation Successful -> {bc_path}")
    
    if args.compile_only:
        return

    print(f"\n--- CI-LANG RUNTIME v1.0 ---")
    manager = SwarmManager(bytecode, agent_count=args.agents, seed=args.seed)
    monitor = StabilityMonitor()
    manager.run_simulation(ticks=args.steps, monitor=monitor)
    print(f"\nExecution Complete.")

if __name__ == "__main__":
    main()
