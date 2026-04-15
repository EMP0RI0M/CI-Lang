from fluxvm_core import FluxVM
import time
import random
import numpy as np

class SwarmManager:
    """
    Orchestrates thousands of FluxVM agents in a shared environment.
    Uses 'Memory-Augmented Homeostatic Control' to stabilize divergence.
    """
    def __init__(self, bytecode, agent_count=None, seed=None):
        self.bytecode = bytecode
        self.seed = seed
        
        # --- Memory-Augmented Control Parameters ---
        self.global_entropy = 0.5
        self.memory = 0.0        # M(t)
        self.gamma = 0.95        # Memory decay
        self.alpha = 0.1         # Memory increment
        self.tau = 0.12          # Instability Threshold
        self.lambda_base = 0.6   # Base Entropy
        self.k = 0.08            # Control Sensitivity
        # -------------------------------------------
        
        self.agents = [] # List of FluxVM instances
        
        # 1. Run "Prime Boot"
        boot_vm = FluxVM(seed=seed)
        boot_vm.load_bytecode(bytecode)
        boot_vm.entropy_register = self.global_entropy
        boot_vm.run()
        
        # 2. Promote Spawned Agents
        for i, instance in enumerate(boot_vm.spawned_agents):
            agent_seed = None if self.seed is None else self.seed + i
            vm = FluxVM(seed=agent_seed)
            vm.load_bytecode(bytecode)
            vm.pc = instance.pc
            vm.entry_pc = instance.entry_pc
            vm.variables = instance.variables
            vm.entropy_register = self.global_entropy
            self.agents.append(vm)

        # Fallback: legacy behavior
        if not self.agents and agent_count:
            for i in range(agent_count):
                agent_seed = None if seed is None else seed + i
                vm = FluxVM(seed=agent_seed)
                vm.load_bytecode(bytecode)
                vm.entropy_register = self.global_entropy
                self.agents.append(vm)

    def step(self):
        agent_outputs = []
        for agent in self.agents:
            # 1. Reset PC to entry point and start execution
            agent.pc = agent.entry_pc
            agent.running = True
            
            # 2. Execute until RET or HALT (One full behavior cycle)
            while agent.running and agent.pc < len(agent.code):
                instr = agent.code[agent.pc]
                agent.pc += 1
                agent.execute(instr)
            
            # 3. Thermodynamic Drift
            agent.drift()
            
            # 4. Collect Output from the reporting buffer
            if agent.outputs:
                agent_outputs.extend(agent.outputs)
                agent.outputs = []
        
        # Memory-Augmented Entropy Regulation
        if agent_outputs:
            numeric_outputs = [x for x in agent_outputs if isinstance(x, (int, float))]
            if numeric_outputs:
                divergence = np.var(numeric_outputs)
                instability_detected = 1.0 if divergence > self.tau else 0.0
                self.memory = (self.gamma * self.memory) + (self.alpha * instability_detected)
                
                new_lambda = self.lambda_base - (self.k * (1.0 + self.memory))
                self.global_entropy = max(0.01, min(0.95, new_lambda))
                
                for agent in self.agents:
                    agent.entropy_register = self.global_entropy
                
        return agent_outputs

    def run_simulation(self, ticks=100, monitor=None):
        print(f"Executing Swarm with {len(self.agents)} active agents...")
        start_time = time.time()
        for t in range(ticks):
            outputs = self.step()
            if monitor:
                monitor.log_step(t, self.global_entropy, outputs, memory=self.memory)
            if t % 100 == 0:
                print(f"Tick {t}: Global Entropy={self.global_entropy:.4f}")
        end_time = time.time()
        print(f"Simulation completed in {end_time - start_time:.2f}s")
