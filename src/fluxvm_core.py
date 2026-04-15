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
    __slots__ = ['id', 'template_name', 'variables', 'pc', 'entry_pc', 'volatility']
    def __init__(self, id, template_name, variables, pc, volatility):
        self.id = id
        self.template_name = template_name
        self.variables = variables # dict of name -> MemoryCell
        self.pc = pc
        self.entry_pc = pc
        self.volatility = volatility

class FluxVM:
    __slots__ = ['data_stack', 'chaos_stack', 'entropy_register', 'pc', 'code', 'running', 'variables', 'call_stack', 'functions', 'checkpoints', 'weights', 'states', 'prev_states', 'agent_id', 'spawned_agents', 'mailbox', 'print_callback', 'metabolism', 'outputs', 'entry_pc', 'rng']
    
    def __init__(self, weights=None, states=None, prev_states=None, agent_id=None, print_callback=None, seed=None):
        self.data_stack = []
        self.chaos_stack = []
        self.entropy_register = 0.5
        self.pc = 0
        self.code = []
        self.running = False
        self.call_stack = []
        self.functions = {} # Name to entry PC / Metadata
        self.checkpoints = {} # ID to snapshot
        self.outputs = []
        self.entry_pc = 0
        self.rng = random.Random(seed) if seed is not None else random.Random()
        
        # --- Built-in Math Constants (Industrial Baseline) ---
        self.variables = {
            "PI": MemoryCell(math.pi),
            "E":  MemoryCell(math.e),
            "INF": MemoryCell(float('inf')),
            "NAN": MemoryCell(float('nan'))
        }
        
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
                noise = self.rng.gauss(0, cell.volatility * self.entropy_register)
                cell.value += noise

    def load_bytecode(self, bytecode):
        self.code = bytecode
        self.pc = 0

    def load_from_file(self, filename):
        with open(filename, 'rb') as f:
            self.code = pickle.load(f)
        self.pc = 0

    def execute(self, instr):
        op = instr[0]
        args = instr[1:] if len(instr) > 1 else []

        if op == "LOAD":
            name = args[0]
            # Industrial Guard: Stack Overflow
            if len(self.data_stack) > 1000:
                raise RuntimeError("FluxVM: Stack Overflow (limit 1000)")
            cell = self.variables.get(name, MemoryCell(0.0))
            self.data_stack.append(cell.value)
        elif op == "STORE":
            name = args[0]
            val = self.data_stack.pop()
            if name in self.variables:
                self.variables[name].value = val
            else:
                self.variables[name] = MemoryCell(val)
        elif op == "LIT":
            if len(self.data_stack) > 1000:
                raise RuntimeError("FluxVM: Stack Overflow (limit 1000)")
            self.data_stack.append(args[0])
        elif op == "PRINT":
            val = self.data_stack.pop()
            self.print_callback(val)
        elif op == "HALT":
            self.running = False
        elif op == "JMP":
            self.pc += args[0]
        elif op == "JMP_IF":
            cond = self.data_stack.pop()
            if cond:
                self.pc += args[0]
        elif op == "CALL":
            # Basic call - PC jump
            self.call_stack.append(self.pc)
            self.pc = args[0]
        elif op == "RET":
            if self.call_stack:
                self.pc = self.call_stack.pop()
            else:
                self.running = False
        elif op == "AGENT_DEF":
            name, pc, states_meta, vol = args
            self.functions[name] = {
                'pc': pc,
                'states': states_meta,
                'volatility': vol
            }
        elif op == "SPAWN":
            template_name, count = args
            if template_name in self.functions:
                template = self.functions[template_name]
                for i in range(int(count)):
                    local_vars = {k: MemoryCell(v) for k, v in template['states'].items()}
                    agent = AgentInstance(
                        id=len(self.spawned_agents),
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

        # --- Hardened Arithmetic & Operators ---
        elif op == "ADD":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            # Bimodal support: string concat or numeric add
            if isinstance(a, str) or isinstance(b, str):
                self.data_stack.append(str(a) + str(b))
            else:
                if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                    raise TypeError(f"ADD expects numeric operands, got {type(a)} and {type(b)}")
                self.data_stack.append(a + b)
        elif op == "SUB":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                raise TypeError(f"SUB expects numeric operands, got {type(a)} and {type(b)}")
            self.data_stack.append(a - b)
        elif op == "MUL":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                raise TypeError(f"MUL expects numeric operands, got {type(a)} and {type(b)}")
            self.data_stack.append(a * b)
        elif op == "DIV":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                raise TypeError(f"DIV expects numeric operands, got {type(a)} and {type(b)}")
            if b == 0: raise ZeroDivisionError("FluxVM: Division by zero")
            self.data_stack.append(a / b)
        elif op == "MOD":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            self.data_stack.append(a % b)

        elif op == "ARROW":
            target = self.data_stack.pop()
            current = self.data_stack.pop()
            if not isinstance(current, (int, float)) or not isinstance(target, (int, float)):
                raise TypeError(f"ARROW (\u2192) expects numeric operands, got {type(current)} and {type(target)}")
            rate = 1.0 - self.entropy_register
            result = current + rate * (target - current)
            self.data_stack.append(result)

        elif op == "CH_EQ":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            if not isinstance(a, (int, float)) or not isinstance(b, (int, float)):
                raise TypeError(f"CH_EQ (\u2248) expects numeric operands, got {type(a)} and {type(b)}")
            sensitivity = 0.1
            match = abs(a - b) < (self.entropy_register * sensitivity)
            self.data_stack.append(1.0 if match else 0.0)

        # --- High-Performance Math Suite ---
        elif op == "SQRT":
            a = self.data_stack.pop()
            if not isinstance(a, (int, float)): raise TypeError(f"SQRT expects numeric, got {type(a)}")
            self.data_stack.append(math.sqrt(a))
        elif op == "EXP":
            a = self.data_stack.pop()
            if not isinstance(a, (int, float)): raise TypeError(f"EXP expects numeric, got {type(a)}")
            self.data_stack.append(math.exp(a))
        elif op == "SIN":
            a = self.data_stack.pop()
            if not isinstance(a, (int, float)): raise TypeError(f"SIN expects numeric, got {type(a)}")
            self.data_stack.append(math.sin(a))
        elif op == "COS":
            a = self.data_stack.pop()
            if not isinstance(a, (int, float)): raise TypeError(f"COS expects numeric, got {type(a)}")
            self.data_stack.append(math.cos(a))
        elif op == "TAN":
            a = self.data_stack.pop()
            if not isinstance(a, (int, float)): raise TypeError(f"TAN expects numeric, got {type(a)}")
            self.data_stack.append(math.tan(a))
        elif op == "LOG":
            a = self.data_stack.pop()
            if not isinstance(a, (int, float)): raise TypeError(f"LOG expects numeric, got {type(a)}")
            self.data_stack.append(math.log(a))
        elif op == "LOG10":
            a = self.data_stack.pop()
            if not isinstance(a, (int, float)): raise TypeError(f"LOG10 expects numeric, got {type(a)}")
            self.data_stack.append(math.log10(a))
        elif op == "CEIL":
            self.data_stack.append(math.ceil(self.data_stack.pop()))
        elif op == "FLOOR":
            self.data_stack.append(math.floor(self.data_stack.pop()))
        elif op == "POW":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            self.data_stack.append(math.pow(a, b))
        elif op == "ROUND":
            self.data_stack.append(round(self.data_stack.pop()))

        # --- Reflective & Swarm Ops ---
        elif op == "MATMUL":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            self.data_stack.append(np.dot(a, b))
        elif op == "PUSH_OUT":
            val = self.data_stack.pop()
            # Constant Memory Buffer: Limit 500 outputs per tick
            if len(self.outputs) > 500:
                self.outputs.pop(0)
            self.outputs.append(val)
        elif op == "INDEX":
            idx = self.data_stack.pop()
            container = self.data_stack.pop()
            if isinstance(idx, float): idx = int(idx)
            self.data_stack.append(container[idx])
        elif op == "STORE_INDEX":
            val = self.data_stack.pop()
            idx = self.data_stack.pop()
            container = self.data_stack.pop()
            if isinstance(idx, float): idx = int(idx)
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
        elif op == "GT":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            self.data_stack.append(a > b)
        elif op == "LT":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            self.data_stack.append(a < b)
        elif op == "GE":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            self.data_stack.append(a >= b)
        elif op == "LE":
            b = self.data_stack.pop()
            a = self.data_stack.pop()
            self.data_stack.append(a <= b)
        elif op == "NOT":
            a = self.data_stack.pop()
            self.data_stack.append(not a)
        
        # Reflective Loads
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
                if val.shape == self.weights.shape: np.copyto(self.weights, val)
                else: self.weights = val
            else: self.weights = val
        elif op == "STORE_STATES":
            val = self.data_stack.pop()
            if self.states is not None:
                if val.shape == self.states.shape: np.copyto(self.states, val)
                else: self.states = val
            else: self.states = val
        elif op == "GET_NOISE":
            if self.states is not None:
                n = self.states.shape[0]
                self.data_stack.append(np.random.normal(0, 1.0, n))
            else:
                self.data_stack.append(np.array([random.gauss(0, 1.0)]))
        elif op == "GET_ENT_EST":
            if self.states is not None and self.states.size > 0:
                counts, _ = np.histogram(self.states, bins=10, range=(0, 1))
                probs = counts / np.sum(counts)
                probs = probs[probs > 0]
                ent = -np.sum(probs * np.log2(probs)) / np.log2(10)
                self.data_stack.append(float(ent))
            else:
                self.data_stack.append(0.0)
        elif op == "GET_SIZE":
            if self.states is not None: self.data_stack.append(int(self.states.shape[0]))
            else: self.data_stack.append(0)
        elif op == "CHECK_MAIL":
            if self.mailbox is not None: self.data_stack.append(self.mailbox)
            else: self.data_stack.append(0.0)
        elif op == "CLEAR_MAIL":
            self.mailbox = None
        elif op == "LOAD_METAB":
            self.data_stack.append(self.metabolism)
        elif op == "STORE_METAB":
            val = self.data_stack.pop()
            if self.metabolism is not None:
                if val.shape == self.metabolism.shape: np.copyto(self.metabolism, val)
                else: self.metabolism = val
            else: self.metabolism = val

    def run(self, max_instructions=100000):
        self.running = True
        count = 0
        while self.running and self.pc < len(self.code):
            instr = self.code[self.pc]
            self.pc += 1
            self.execute(instr)
            count += 1
            if count > max_instructions:
                raise RuntimeError(f"FluxVM: Instruction Limit Exceeded ({max_instructions})")

def main():
    if len(sys.argv) > 1:
        vm = FluxVM()
        vm.load_from_file(sys.argv[1])
        vm.run()

if __name__ == "__main__":
    main()
