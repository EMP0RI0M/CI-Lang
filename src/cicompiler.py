import os
from ciparser import ProgramNode, VarDeclNode, PrintNode, ChaosBlockNode, BinaryOpNode, LiteralNode, IdentifierNode, IfNode, EntropySetNode, EntropyMeasureNode, ChaosBracketNode, FuncDeclNode, ReturnNode, AdaptNode, CallNode, SystemNode, AgentNode, SpawnNode, VolatilityStmtNode, ReflectiveLoadWNode, ReflectiveStoreWNode, ReflectiveLoadSNode, ReflectiveStoreSNode, WhileNode, ReflectiveGetIdNode, ReflectiveLoadPrevSNode, ArrayNode, ReflectiveLoadWeightsNode, ReflectiveLoadStatesNode, ReflectiveLoadPrevStatesNode, ReflectiveStoreWeightsNode, ReflectiveStoreStatesNode, ReflectiveGetNoiseNode, ClassNode, ReflectiveGetEntEstNode, ReflectiveGetSizeNode, ImportNode, IndexNode, IndexAssignNode, ReflectiveCheckMailNode, ReflectiveClearMailNode, ReflectiveLoadMetabNode, ReflectiveStoreMetabNode, ClipNode, PushNode

class Compiler:
    def __init__(self):
        self.bytecode = []
        self.functions = {} # name -> index in bytecode

    def compile(self, node):
        if isinstance(node, ProgramNode):
            for stmt in node.statements:
                self.compile(stmt)
            self.bytecode.append(("HALT",))
        
        elif isinstance(node, VarDeclNode):
            self.compile(node.value)
            self.bytecode.append(("STORE", node.name))
        
        elif isinstance(node, PrintNode):
            self.compile(node.expression)
            self.bytecode.append(("PRINT",))
        
        elif isinstance(node, PushNode):
            self.compile(node.expression)
            self.bytecode.append(("PUSH_OUT",))
        
        elif isinstance(node, ChaosBlockNode):
            for stmt in node.statements:
                self.compile(stmt)

        elif isinstance(node, IfNode):
            self.compile(node.condition)
            self.bytecode.append(("NOT",))
            
            # Placeholder for JMP_IF (jump to else)
            jmp_if_idx = len(self.bytecode)
            self.bytecode.append(("JMP_IF", 0))
            
            # Compile then_block
            for stmt in node.then_block:
                self.compile(stmt)
            
            if node.else_block:
                # Placeholder for JMP (jump to end)
                jmp_end_idx = len(self.bytecode)
                self.bytecode.append(("JMP", 0))
                
                # Fixup JMP_IF to point to else_block
                else_start_idx = len(self.bytecode)
                self.bytecode[jmp_if_idx] = ("JMP_IF", else_start_idx - jmp_if_idx - 1)
                
                # Compile else_block
                for stmt in node.else_block:
                    self.compile(stmt)
                
                # Fixup JMP to point to end
                end_idx = len(self.bytecode)
                self.bytecode[jmp_end_idx] = ("JMP", end_idx - jmp_end_idx - 1)
            else:
                # No else block
                end_idx = len(self.bytecode)
                self.bytecode[jmp_if_idx] = ("JMP_IF", end_idx - jmp_if_idx - 1)

        elif isinstance(node, BinaryOpNode):
            self.compile(node.left)
            self.compile(node.right)
            if node.op == 'PLUS':
                self.bytecode.append(("ADD",))
            elif node.op == 'MINUS':
                self.bytecode.append(("SUB",))
            elif node.op == 'MUL':
                self.bytecode.append(("MUL",))
            elif node.op == 'DIV':
                self.bytecode.append(("DIV",))
            elif node.op == 'EQ':
                self.bytecode.append(("EQ",))
            elif node.op == 'GT':
                self.bytecode.append(("GT",))
            elif node.op == 'LT':
                self.bytecode.append(("LT",))
            elif node.op == 'GE':
                self.bytecode.append(("GE",))
            elif node.op == 'LE':
                self.bytecode.append(("LE",))
            elif node.op == 'CH_EQ':
                self.bytecode.append(("CHAOS_EQ",))
            elif node.op == 'MATMUL':
                self.bytecode.append(("MATMUL",))
            elif node.op == 'MOD':
                self.bytecode.append(("MOD",))
            else:
                pass

        elif isinstance(node, LiteralNode):
            self.bytecode.append(("LIT", node.value))
        
        elif isinstance(node, IdentifierNode):
            self.bytecode.append(("LOAD", node.name))

        elif isinstance(node, EntropySetNode):
            self.compile(node.expression)
            self.bytecode.append(("SET_E",))
        
        elif isinstance(node, EntropyMeasureNode):
            self.bytecode.append(("GET_E",))
        
        elif isinstance(node, ChaosBracketNode):
            # Chaos bracket ⟨ expression ⟩ - wrap in ENTROPIZE
            self.compile(node.expression)
            self.bytecode.append(("ENTROPIZE",))

        elif isinstance(node, FuncDeclNode):
            # Jump around the function body
            skip_jmp_idx = len(self.bytecode)
            self.bytecode.append(("JMP", 0))
            
            self.functions[node.name] = len(self.bytecode)
            # Handle params (reverse order since they are on stack)
            for p_name, _ in reversed(node.params):
                self.bytecode.append(("STORE", p_name))
            
            for stmt in node.block:
                self.compile(stmt)
            
            # Ensure return at end of function
            self.bytecode.append(("RET",))
            
            end_idx = len(self.bytecode)
            self.bytecode[skip_jmp_idx] = ("JMP", end_idx - skip_jmp_idx - 1)

        elif isinstance(node, CallNode):
            # Push args
            for arg in node.args:
                self.compile(arg)
            
            if isinstance(node.callee, IdentifierNode):
                name = node.callee.name
                
                # Built-in Intrinsics for Foundation High-Performance Math
                math_ops = {
                    "sqrt": "SQRT", "exp": "EXP", "sin": "SIN", "cos": "COS", 
                    "tan": "TAN", "log": "LOG", "log10": "LOG10", 
                    "ceil": "CEIL", "floor": "FLOOR", "round": "ROUND"
                }
                if name in math_ops:
                    self.bytecode.append((math_ops[name],))
                    return
                elif name == "pow":
                    self.bytecode.append(("POW",))
                    return

                if name not in self.functions:
                    raise Exception(f"Undefined function: {name}")
                self.bytecode.append(("CALL", self.functions[name]))
            else:
                # Dynamic call - not supported yet or handle differently
                raise Exception("Dynamic calls via expression not supported yet")

        elif isinstance(node, ReturnNode):
            self.compile(node.expression)
            self.bytecode.append(("RET",))

        elif isinstance(node, AdaptNode):
            self.bytecode.append(("ADAPT", node.target))

        elif isinstance(node, SystemNode):
            for stmt in node.statements:
                self.compile(stmt)

        elif isinstance(node, AgentNode):
            # Compile agent update block as a "pseudo-function"
            entry_pc = len(self.bytecode)
            # Skip jump around the agent body
            skip_jmp_idx = len(self.bytecode)
            self.bytecode.append(("JMP", 0))
            
            # Agent update entry point
            update_start_pc = len(self.bytecode)
            for stmt in node.update_block:
                self.compile(stmt)
            self.bytecode.append(("RET",))
            
            end_idx = len(self.bytecode)
            self.bytecode[skip_jmp_idx] = ("JMP", end_idx - skip_jmp_idx - 1)
            
            # Define the agent template
            # States are compiled to literals for metadata
            states_data = {}
            for s_name, s_expr in node.states.items():
                if isinstance(s_expr, LiteralNode):
                    states_data[s_name] = s_expr.value
                else:
                    states_data[s_name] = 0.0 # Placeholder for non-literal init
            
            # If volatility is an expression, we evaluate it in-place or store as a value
            vol_val = 0.1
            if isinstance(node.volatility, LiteralNode):
                vol_val = node.volatility.value
            
            self.bytecode.append(("AGENT_DEF", node.name, update_start_pc, states_data, vol_val))

        elif isinstance(node, SpawnNode):
            # We'll assume the size is a literal for now as per current parser
            self.bytecode.append(("SPAWN", node.agent_name, node.size))

        elif isinstance(node, VolatilityStmtNode):
            self.compile(node.expression)
            self.bytecode.append(("SET_VOL", node.var_name))

        elif isinstance(node, ClipNode):
            self.compile(node.expr)
            self.compile(node.min_val)
            self.compile(node.max_val)
            self.bytecode.append(("CLIP",))

        elif isinstance(node, ReflectiveLoadWNode):
            self.compile(node.i_expr)
            self.compile(node.j_expr)
            self.bytecode.append(("LOAD_W",))

        elif isinstance(node, ReflectiveStoreWNode):
            self.compile(node.i_expr)
            self.compile(node.j_expr)
            self.compile(node.val_expr)
            self.bytecode.append(("STORE_W",))

        elif isinstance(node, ReflectiveLoadSNode):
            self.compile(node.i_expr)
            self.bytecode.append(("LOAD_S",))

        elif isinstance(node, ReflectiveLoadPrevSNode):
            self.compile(node.i_expr)
            self.bytecode.append(("LOAD_PREV_S",))

        elif isinstance(node, ReflectiveStoreSNode):
            self.compile(node.i_expr)
            self.compile(node.val_expr)
            self.bytecode.append(("STORE_S",))

        elif isinstance(node, ReflectiveGetIdNode):
            self.bytecode.append(("GET_ID",))

        elif isinstance(node, ArrayNode):
            for elem in node.elements:
                self.compile(elem)
            self.bytecode.append(("BUILD_ARRAY", len(node.elements)))

        elif isinstance(node, ReflectiveLoadWeightsNode):
            self.bytecode.append(("LOAD_WEIGHTS",))

        elif isinstance(node, ReflectiveLoadStatesNode):
            self.bytecode.append(("LOAD_STATES",))

        elif isinstance(node, ReflectiveLoadPrevStatesNode):
            self.bytecode.append(("LOAD_PREV_STATES",))

        elif isinstance(node, ReflectiveStoreWeightsNode):
            self.compile(node.expr)
            self.bytecode.append(("STORE_WEIGHTS",))

        elif isinstance(node, ReflectiveStoreStatesNode):
            self.compile(node.expr)
            self.bytecode.append(("STORE_STATES",))

        elif isinstance(node, ReflectiveGetNoiseNode):
            self.bytecode.append(("GET_NOISE",))

        elif isinstance(node, ReflectiveGetEntEstNode):
            self.bytecode.append(("GET_ENT_EST",))

        elif isinstance(node, ReflectiveGetSizeNode):
            self.bytecode.append(("GET_SIZE",))

        elif isinstance(node, ReflectiveCheckMailNode):
            self.bytecode.append(("CHECK_MAIL",))

        elif isinstance(node, ReflectiveClearMailNode):
            self.bytecode.append(("CLEAR_MAIL",))

        elif isinstance(node, ReflectiveLoadMetabNode):
            self.bytecode.append(("LOAD_METAB",))

        elif isinstance(node, ReflectiveStoreMetabNode):
            self.compile(node.expr)
            self.bytecode.append(("STORE_METAB",))

        elif isinstance(node, ClassNode):
            for stmt in node.body:
                if isinstance(stmt, FuncDeclNode):
                    orig_name = stmt.name
                    stmt.name = f"{node.name}.{orig_name}"
                    self.compile(stmt)
                    stmt.name = orig_name
                else:
                    self.compile(stmt)

        elif isinstance(node, ImportNode):
            # Dynamic import resolution
            filename = node.filename
            paths_to_check = [
                filename,
                os.path.join("stdlib", filename),
                os.path.join(os.path.dirname(__file__), "..", "stdlib", filename)
            ]
            
            resolved_path = None
            for p in paths_to_check:
                if os.path.exists(p):
                    resolved_path = p
                    break
            
            if resolved_path:
                from cilexer import Lexer
                from ciparser import Parser
                with open(resolved_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                lexer = Lexer(content)
                parser = Parser(lexer.tokenize())
                imported_ast = parser.parse_program()
                # Compile statements from imported program
                for stmt in imported_ast.statements:
                    self.compile(stmt)
            else:
                raise Exception(f"Import failed: file not found {filename} after checking stdlib.")

        elif isinstance(node, IndexNode):
            self.compile(node.left)
            self.compile(node.index)
            self.bytecode.append(("INDEX",))

        elif isinstance(node, IndexAssignNode):
            self.bytecode.append(("LOAD", node.name))
            self.compile(node.index)
            self.compile(node.value)
            self.bytecode.append(("STORE_INDEX",))

        elif isinstance(node, WhileNode):
            # Loop Start
            loop_start_idx = len(self.bytecode)
            
            # Compile condition
            self.compile(node.condition)
            self.bytecode.append(("NOT",))
            
            # Placeholder for JMP_IF (jump to end)
            jmp_end_idx = len(self.bytecode)
            self.bytecode.append(("JMP_IF", 0))
            
            # Compile block
            for stmt in node.block:
                self.compile(stmt)
                
            # Jump back to start
            self.bytecode.append(("JMP", loop_start_idx - len(self.bytecode) - 1))
            
            # Fixup JMP_IF to point to end
            end_idx = len(self.bytecode)
            self.bytecode[jmp_end_idx] = ("JMP_IF", end_idx - jmp_end_idx - 1)

        return self.bytecode
