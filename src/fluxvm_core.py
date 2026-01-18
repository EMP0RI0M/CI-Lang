import random
import pickle
import sys
import math
import numpy as np

class MemoryCell:
    __slots__ = ['value', 'volatility']
    def __init__(self, value, volatility=0.0):
        self.value = value
        self.volatility = volatility

class AgentInstance:
    __slots__ = ['id', 'template_name', 'variables', 'pc', 'volatility']
    def __init__(self, id, template_name, variables, pc, volatility):
        self.id = id
        self.template_name = template_name
        self.variables = variables # dict of name -> MemoryCell
        self.pc = pc
        self.volatility = volatility

class FluxVM:
    __slots__ = ['data_stack', 'chaos_stack', 'entropy_register', 'pc', 'code', 'running', 'variables', 'call_stack', 'functions', 'checkpoints', 'weights', 'states', 'prev_states', 'agent_id', 'spawned_agents', 'mailbox', 'print_callback', 'metabolism']
    
    def __init__(self, weights=None, states=None, prev_states=None, agent_id=None, print_callback=None):
        self.data_stack = []
        self.chaos_stack = []
        self.entropy_register = 0.5
        self.pc = 0
        self.code = []
        self.running = False
        self.variables = {} # Global Variables (Name to MemoryCell)
        self.call_stack = []
        self.functions = {} # Name to entry PC / Metadata
        self.checkpoints = {} # ID to snapshot
        
        # External Context for Self-Bootstrapping (Phase 20)
        self.weights = weights # NumPy Matrix (NxN)
        self.states = states   # NumPy Vector (N)
        self.prev_states = prev_states # NumPy Vector (N)
        self.agent_id = agent_id
        self.spawned_agents = [] # List of AgentInstance
        self.mailbox = None # Host Input
        self.print_callback = print_callback or (lambda x: print(f"[FluxVM Output]: {x}"))
        self.metabolism = np.ones_like(states) if states is not None else None

    def drift(self):
        """Applies thermodynamic drift to all non-zero volatility variables."""
        for cell in self.variables.values():
            if cell.volatility > 0:
                noise = random.gauss(0, cell.volatility * self.entropy_register)
                if isinstance(cell.value, (int, float)):
                    cell.value += noise

    def load_bytecode(self, bytecode):
        self.code = bytecode
        self.pc = 0

    def load_from_file(self, filename):
        with open(filename, 'rb') as f:
            self.code = pickle.load(f)
        self.pc = 0

    def run(self):
        self.running = True
        while self.running and self.pc < len(self.code):
            instr = self.code[self.pc]
            self.pc += 1
            self.execute(instr)

    def step(self):
        if self.pc < len(self.code):
            instr = self.code[self.pc]
            self.pc += 1
            self.execute(instr)
            return True
        return False

    def update_agents(self):
        """Executes the update block for all spawned agents."""
        for agent in self.spawned_agents:
            # 1. Switch Context
            saved_globals = self.variables
            self.variables = agent.variables
            self.agent_id = agent.id
            self.pc = agent.pc
            self.running = True
            
            # 2. Run Update Block
            while self.running and self.pc < len(self.code):
                instr = self.code[self.pc]
                self.pc += 1
                self.execute(instr)
            
            # 3. Restore Global Context
            self.variables = saved_globals
            self.agent_id = None

    def execute(self, instr):
        op = instr[0]
        args = instr[1:]

        # Stack Operations
        if op == "PUSH":
            self.data_stack.append(args[0])
        elif op == "POP":
            self.data_stack.pop()
        elif op == "DUP":
            self.data_stack.append(self.data_stack[-1])
        elif op == "LOAD":
            cell = self.variables.get(args[0], MemoryCell(0))
            self.data_stack.append(cell.value)
        elif op == "STORE":
            val = self.data_stack.pop()
            if args[0] in self.variables:
                self.variables[args[0]].value = val
            else:
                self.variables[args[0]] = MemoryCell(val, volatility=0.0)
        elif op == "SET_VOL":
            vol = self.data_stack.pop()
            var_name = args[0]
            if var_name in self.variables:
                self.variables[var_name].volatility = vol
            else:
                self.variables[var_name] = MemoryCell(0, volatility=vol)
        
        elif op == "AGENT_DEF":
            name = args[0]
            entry_pc = args[1]
            states = args[2] 
            volatility = args[3]
            self.functions[name] = {
                'pc': entry_pc,
                'states': states,
                'volatility': volatility
            }
        
        elif op == "SPAWN":
            template_name = args[0]
            count = int(args[1])
            if template_name in self.functions:
                template = self.functions[template_name]
                print(f"[FluxVM SPAWN]: Creating {count} agents from template '{template_name}'")
                for i in range(count):
                    local_vars = {name: MemoryCell(val) for name, val in template['states'].items()}
                    agent = AgentInstance(
                        id=i,
                        template_name=template_name,
                        variables=local_vars,
                        pc=template['pc'],
                        volatility=template['volatility']
                    )
                    self.spawned_agents.append(agent)

        elif op == "BUILD_ARRAY":
            count = args[0]
            elements = []
            for _ in range(count):
                elements.append(self.data_stack.pop())
            # Elements are popped in reverse order
            self.data_stack.append(np.array(elements[::-1]))

        # Arithmetic
        elif op == "ADD":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            if isinstance(a, str) or isinstance(b, str):
                self.data_stack.append(str(a) + str(b))
            else:
                self.data_stack.append(a + b)
        elif op == "SUB":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            self.data_stack.append(a - b)
        elif op == "MUL":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            self.data_stack.append(a * b)
        elif op == "DIV":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            self.data_stack.append(a / b)
        elif op == "MOD":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            self.data_stack.append(a % b)
        elif op == "MATMUL":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            self.data_stack.append(np.dot(a, b))
        elif op == "INDEX":
            idx = self.data_stack.pop()
            container = self.data_stack.pop()
            # Handle float indices from CI-Lang literals
            if isinstance(idx, float):
                idx = int(idx)
            self.data_stack.append(container[idx])
        elif op == "STORE_INDEX":
            val = self.data_stack.pop()
            idx = self.data_stack.pop()
            container = self.data_stack.pop()
            if isinstance(idx, float):
                idx = int(idx)
            container[idx] = val
        elif op == "CLIP":
            max_v = self.data_stack.pop()
            min_v = self.data_stack.pop()
            val = self.data_stack.pop()
            if isinstance(val, np.ndarray):
                self.data_stack.append(np.clip(val, min_v, max_v))
            else:
                self.data_stack.append(max(min_v, min(val, max_v)))
        elif op == "EQ":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            self.data_stack.append(a == b)
        elif op == "NOT":
            a = self.data_stack.pop()
            self.data_stack.append(not a)

        # Chaos Operations
        elif op == "CHAOS_EQ":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            if self.entropy_register == 0.0:
                res = (a == b)
            else:
                if a == b:
                    res = random.random() > (self.entropy_register * 0.5)
                else:
                    res = random.random() < (self.entropy_register * 0.5)
            self.data_stack.append(res)

        elif op == "GET_E":
            self.data_stack.append(self.entropy_register)
        elif op == "SET_E":
            if args:
                self.entropy_register = max(0.0, min(1.0, args[0]))
            else:
                self.entropy_register = max(0.0, min(1.0, self.data_stack.pop()))
        elif op == "ENTROPIZE":
            val = self.data_stack.pop()
            noise = (random.random() - 0.5) * self.entropy_register * val
            self.data_stack.append(val + noise)

        # Control Flow
        elif op == "JMP":
            self.pc += args[0]
        elif op == "JMP_IF":
            val = self.data_stack.pop()
            if val:
                self.pc += args[0]
        elif op == "CALL":
            self.call_stack.append(self.pc)
            self.pc = args[0]
        elif op == "RET":
            if self.call_stack:
                self.pc = self.call_stack.pop()
            else:
                self.running = False
        elif op == "ADAPT":
            self.entropy_register *= 0.9
        elif op == "PRINT":
            self.print_callback(self.data_stack.pop())
        elif op == "HALT":
            self.running = False
        
        elif op == "SAVE_STATE":
            state_id = self.data_stack.pop()
            self.checkpoints[state_id] = {
                'vars': self.variables.copy(),
                'dstack': self.data_stack.copy(),
                'cstack': self.chaos_stack.copy(),
                'er': self.entropy_register
            }
        elif op == "RESTORE_STATE":
            state_id = self.data_stack.pop()
            if state_id in self.checkpoints:
                s = self.checkpoints[state_id]
                self.variables = s['vars'].copy()
                self.data_stack = s['dstack'].copy()
                self.chaos_stack = s['cstack'].copy()
                self.entropy_register = s['er']

        # Reflective Reflective ISA (Self-Bootstrapping)
        elif op == "LOAD_W":
            j = int(self.data_stack.pop())
            i = int(self.data_stack.pop())
            if self.weights is not None:
                self.data_stack.append(float(self.weights[i, j]))
            else:
                self.data_stack.append(0.0)
        elif op == "STORE_W":
            val = float(self.data_stack.pop())
            j = int(self.data_stack.pop())
            i = int(self.data_stack.pop())
            if self.weights is not None:
                self.weights[i, j] = val
        elif op == "LOAD_S":
            i = int(self.data_stack.pop())
            if self.states is not None:
                self.data_stack.append(float(self.states[i]))
            else:
                self.data_stack.append(0.0)
        elif op == "LOAD_PREV_S":
            i = int(self.data_stack.pop())
            if self.prev_states is not None:
                self.data_stack.append(float(self.prev_states[i]))
            else:
                self.data_stack.append(0.0)
        elif op == "STORE_S":
            val = float(self.data_stack.pop())
            i = int(self.data_stack.pop())
            if self.states is not None:
                self.states[i] = val
        elif op == "GET_ID":
            if self.agent_id is not None:
                self.data_stack.append(int(self.agent_id))
            else:
                self.data_stack.append(-1)
        
        elif op == "LOAD_WEIGHTS":
            if self.weights is not None:
                self.data_stack.append(self.weights.copy())
            else:
                self.data_stack.append(np.array([]))
                
        elif op == "LOAD_STATES":
            if self.states is not None:
                self.data_stack.append(self.states.copy())
            else:
                self.data_stack.append(np.array([]))
        
        elif op == "LOAD_PREV_STATES":
            if self.prev_states is not None:
                self.data_stack.append(self.prev_states.copy())
            else:
                self.data_stack.append(np.array([]))
        
        elif op == "STORE_WEIGHTS":
            val = self.data_stack.pop()
            if self.weights is not None:
                # Ensure physical dimensions match if possible
                if val.shape == self.weights.shape:
                    np.copyto(self.weights, val)
                else:
                    self.weights = val
            else:
                self.weights = val

        elif op == "STORE_STATES":
            val = self.data_stack.pop()
            if self.states is not None:
                if val.shape == self.states.shape:
                    np.copyto(self.states, val)
                else:
                    self.states = val
            else:
                self.states = val

        elif op == "GET_NOISE":
            if self.states is not None:
                n = self.states.shape[0]
                self.data_stack.append(np.random.normal(0, 1.0, n))
            else:
                self.data_stack.append(np.array([random.gauss(0, 1.0)]))

        elif op == "GET_ENT_EST":
            if self.states is not None:
                # Basic entropy estimate (histogram based)
                counts, _ = np.histogram(self.states, bins=10, range=(0, 1))
                probs = counts / np.sum(counts)
                probs = probs[probs > 0]
                ent = -np.sum(probs * np.log2(probs)) / np.log2(10) # Normalized
                self.data_stack.append(float(ent))
            else:
                self.data_stack.append(0.0)

        elif op == "GET_SIZE":
            if self.states is not None:
                self.data_stack.append(int(self.states.shape[0]))
            else:
                self.data_stack.append(0)

        elif op == "CHECK_MAIL":
            # Push mailbox content if exists, else 0
            if self.mailbox is not None:
                self.data_stack.append(self.mailbox)
            else:
                self.data_stack.append(0.0)

        elif op == "CLEAR_MAIL":
            self.mailbox = None

        elif op == "LOAD_METAB":
            self.data_stack.append(self.metabolism)

        elif op == "STORE_METAB":
            val = self.data_stack.pop()
            if self.metabolism is not None:
                if val.shape == self.metabolism.shape:
                    np.copyto(self.metabolism, val)
                else:
                    self.metabolism = val
            else:
                self.metabolism = val

        elif op == "GE":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            self.data_stack.append(1.0 if a >= b else 0.0)

        elif op == "LE":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            self.data_stack.append(1.0 if a <= b else 0.0)

        elif op == "GT":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            self.data_stack.append(a > b)
        elif op == "LT":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            self.data_stack.append(a < b)

# CLI for running bytecode
def main():
    if len(sys.argv) > 1:
        vm = FluxVM()
        vm.load_from_file(sys.argv[1])
        vm.run()

if __name__ == "__main__":
    main()
