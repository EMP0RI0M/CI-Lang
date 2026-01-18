from fluxvm import FluxVM
import time
import random
import numpy as np

class SwarmManager:
    """
    Orchestrates thousands of FluxVM agents in a shared environment.
    Uses 'Shared Volatility' where agents influence a global entropy pool.
    """
    def __init__(self, bytecode, agent_count=1000):
        self.bytecode = bytecode
        self.agent_count = agent_count
        self.agents = [FluxVM() for _ in range(agent_count)]
        self.global_entropy = 0.5
        
        # Initialize all agents with the same code
        for agent in self.agents:
            agent.load_bytecode(bytecode)
            agent.entropy_register = self.global_entropy

    def step(self):
        """
        Executes one 'tick' for all agents using Thermodynamic Chaos rules.
        Includes FluxVM instruction execution and thermodynamic drift.
        """
        agent_outputs = []
        
        for agent in self.agents:
            # 1. FluxVM Execution (One instruction per tick)
            if agent.pc < len(agent.code):
                instr = agent.code[agent.pc]
                agent.pc += 1
                agent.execute(instr)
            
            # 2. Thermodynamic Drift
            agent.drift()
            
            # 3. Collect Output
            if agent.data_stack:
                agent_outputs.append(agent.data_stack[-1])
        
        # 4. Global Entropy Regulation
        if agent_outputs:
            current_variance = np.var([x for x in agent_outputs if isinstance(x, (int, float))])
            target_variance = 0.08
            error = target_variance - current_variance
            self.global_entropy = max(0.01, min(0.99, self.global_entropy + error * 0.05))
            
            # Sync entropy to all agents
            for agent in self.agents:
                agent.entropy_register = self.global_entropy
                
        return agent_outputs

    def handle_spawns(self, parent_vm):
        """
        Checks parent_vm for new agents or templates and initializes the swarm.
        """
        # If the parent VM has agent templates, we should use them
        for name, template in parent_vm.functions.items():
            if isinstance(template, dict) and 'states' in template:
                # This is an agent template, not a function
                pass # Already handled in initialization or dynamic spawn

    def run_simulation(self, ticks=100, monitor=None):
        print(f"Initializing Swarm with {self.agent_count} agents...")
        start_time = time.time()
        
        for t in range(ticks):
            outputs = self.step()
            
            if monitor:
                monitor.log_step(t, self.global_entropy, outputs)
            
            if t % 10 == 0:
                print(f"Tick {t}: Global Entropy={self.global_entropy:.4f}")
        
        end_time = time.time()
        print(f"Simulation completed in {end_time - start_time:.2f}s")
