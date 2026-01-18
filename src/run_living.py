from fluxvm import FluxVM, MemoryCell
from swarms.engine import SwarmManager
import pickle
import os

def run_living_memory():
    # Load compiled bytecode
    bc_path = os.path.join(os.path.dirname(__file__), "..", "living_memory.bc")
    with open(bc_path, 'rb') as f:
        bytecode = pickle.load(f)
    
    # 1. Master VM processes initialization (AGENT_DEF, etc.)
    master_vm = FluxVM()
    master_vm.load_bytecode(bytecode)
    
    print("--- CI-Lang 2.0 Living Memory Execution ---")
    
    # Run master VM until first SPAWN or completion of initialization
    # In CI-Lang 2.0, top-level code usually sets up the system.
    while master_vm.pc < len(master_vm.code) and not master_vm.running:
        instr = master_vm.code[master_vm.pc]
        master_vm.pc += 1
        master_vm.execute(instr)
        if instr[0] == "SPAWN":
            # Extract spawn info from bytecode if not implicitly handled
            agent_name = instr[1]
            count = int(instr[2])
            break
    
    # 2. Initialize Swarm from Master VM Templates
    if agent_name in master_vm.functions:
        template = master_vm.functions[agent_name]
        print(f"Instantiating Swarm: {count} agents of type '{agent_name}'")
        
        swarm_agents = []
        for _ in range(count):
            avm = FluxVM()
            avm.load_bytecode(bytecode)
            avm.pc = template['pc']
            # Initialize states
            for s_name, s_val in template['states'].items():
                avm.variables[s_name] = MemoryCell(s_val, volatility=template['volatility'])
            swarm_agents.append(avm)
        
        manager = SwarmManager(bytecode)
        manager.agents = swarm_agents
        manager.agent_count = count
        
        # 3. Run Simulation
        print("Running Simulation with Thermodynamic Drift...")
        for t in range(50):
            outputs = manager.step()
            if t % 10 == 0:
                print(f"Tick {t:2d} | Global Entropy: {manager.global_entropy:.3f}")
                # Print a few agent states to see drift
                sample_states = [round(a.variables['val'].value, 4) for a in swarm_agents[:3]]
                print(f"  Sample Agent 'val' states: {sample_states}")

if __name__ == "__main__":
    run_living_memory()
