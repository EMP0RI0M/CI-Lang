import os
import sys
import pickle
import numpy as np
from typing import List, Dict
from fluxvm.agent import Agent
from fluxvm.numba_core import physics_step, hebbian_logic_step

# Add src to path to import FluxVM core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
from fluxvm_core import FluxVM

class Swarm:
    def __init__(self, agents: List[Agent], alpha=0.01, decay=0.99, ci_mode=True):
        """
        Swarm orchestrator with Numba-Accelerated Asymmetric Hebbian Association.
        """
        self.agents = agents
        self.n = len(agents)
        self.alpha = alpha
        self.decay = decay
        self.ci_mode = ci_mode
        
        # Memory-Efficient Transition: Use a dense matrix for 10k agents
        # (Approx 800MB RAM for 10k x 10k float64)
        self.weights = np.zeros((self.n, self.n), dtype=np.float64)
        
        # Temporal Trace
        self.prev_states = np.zeros(self.n, dtype=np.float64)
        
        # Meta-Evolutionary Core (CI-Lang)
        self.meta_vm = None
        if self.ci_mode:
            bc_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../core_hebbian.bc'))
            if os.path.exists(bc_path):
                # Initialize VM with current weights and prev_states
                self.meta_vm = FluxVM(weights=self.weights, states=None, prev_states=self.prev_states)
                with open(bc_path, 'rb') as f:
                    bytecode = pickle.load(f)
                    self.meta_vm.load_bytecode(bytecode)
                # Run once to execute 'system' setup (SPAWN etc)
                self.meta_vm.run()
                print(f"[Swarm Architecture]: CI-Lang Meta-Core Bootstrapped with {len(self.meta_vm.spawned_agents)} agents.")
            else:
                print(f"[Swarm Warning]: Bytecode {bc_path} not found. Running in fallback mode.")
                self.ci_mode = False

    def step(self, global_volatility: float):
        """
        Accelerated thermodynamic update.
        """
        states = self.get_states()
        
        # 1. Physics Step (JIT-Optimized Matrix Math)
        new_states = physics_step(states, self.weights, global_volatility, global_inhibition_rate=0.1)
        
        # 2. Hebbian Logic Step (Intelligence Layer)
        if self.ci_mode and self.meta_vm:
            self.meta_vm.states = new_states
            self.meta_vm.prev_states = self.prev_states
            # Execute CI-Lang Agent Update Blocks
            self.meta_vm.update_agents() 
            # Note: Weights in self.meta_vm are a reference to self.weights, so they are updated in-place.
        else:
            # Fallback to JIT-Logic
            self.weights = hebbian_logic_step(new_states, self.prev_states, self.weights, self.alpha, self.decay)
        
        self.prev_states = states.copy()
        
        # Update local agent objects for historical consistency (though we minimize this for 10k)
        for i, agent in enumerate(self.agents):
            agent.state = new_states[i]
            # Skip history appending for 10k to save memory
            # agent.history.append(agent.state)

    def get_states(self):
        return np.array([a.state for a in self.agents], dtype=np.float64)
