class ASTNode:
    pass

class ImportNode(ASTNode):
    def __init__(self, filename):
        self.filename = filename

class ProgramNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class FuncDeclNode(ASTNode):
    def __init__(self, name, params, return_type, block):
        self.name = name
        self.params = params
        self.return_type = return_type
        self.block = block

class ClassNode(ASTNode):
    def __init__(self, name, parent, body):
        self.name = name
        self.parent = parent
        self.body = body

class ReturnNode(ASTNode):
    def __init__(self, expression):
        self.expression = expression

class AdaptNode(ASTNode):
    def __init__(self, target, source):
        self.target = target
        self.source = source

class CallNode(ASTNode):
    def __init__(self, callee, args):
        self.callee = callee
        self.args = args

class VarDeclNode(ASTNode):
    def __init__(self, name, value):
        self.name = name
        self.value = value

class PrintNode(ASTNode):
    def __init__(self, expression):
        self.expression = expression

class ChaosBlockNode(ASTNode):
    def __init__(self, statements):
        self.statements = statements

class IfNode(ASTNode):
    def __init__(self, condition, then_block, else_block=None):
        self.condition = condition
        self.then_block = then_block
        self.else_block = else_block

class EntropySetNode(ASTNode):
    def __init__(self, expression):
        self.expression = expression

class EntropyMeasureNode(ASTNode):
    pass

class ChaosBracketNode(ASTNode):
    def __init__(self, expression):
        self.expression = expression

class BinaryOpNode(ASTNode):
    def __init__(self, left, op, right):
        self.left = left
        self.op = op
        self.right = right

class LiteralNode(ASTNode):
    def __init__(self, value):
        self.value = value

class IdentifierNode(ASTNode):
    def __init__(self, name):
        self.name = name

class SystemNode(ASTNode):
    def __init__(self, name, statements):
        self.name = name
        self.statements = statements

class AgentNode(ASTNode):
    def __init__(self, name, states, volatility, update_block):
        self.name = name
        self.states = states
        self.volatility = volatility
        self.update_block = update_block

class SpawnNode(ASTNode):
    def __init__(self, agent_name, size, topology=None):
        self.agent_name = agent_name
        self.size = size
        self.topology = topology

class VolatilityStmtNode(ASTNode):
    def __init__(self, var_name, expression):
        self.var_name = var_name
        self.expression = expression

class ReflectiveLoadWNode(ASTNode):
    def __init__(self, i_expr, j_expr):
        self.i_expr = i_expr
        self.j_expr = j_expr

class ReflectiveStoreWNode(ASTNode):
    def __init__(self, i_expr, j_expr, val_expr):
        self.i_expr = i_expr
        self.j_expr = j_expr
        self.val_expr = val_expr

class ReflectiveLoadSNode(ASTNode):
    def __init__(self, i_expr):
        self.i_expr = i_expr

class ReflectiveLoadPrevSNode(ASTNode):
    def __init__(self, i_expr):
        self.i_expr = i_expr

class ReflectiveStoreSNode(ASTNode):
    def __init__(self, i_expr, val_expr):
        self.i_expr = i_expr
        self.val_expr = val_expr

class ReflectiveGetIdNode(ASTNode):
    pass

class ArrayNode(ASTNode):
    def __init__(self, elements):
        self.elements = elements

class ReflectiveLoadWeightsNode(ASTNode):
    pass

class ReflectiveLoadStatesNode(ASTNode):
    pass

class ReflectiveLoadPrevStatesNode(ASTNode):
    pass

class ReflectiveStoreWeightsNode(ASTNode):
    def __init__(self, expr):
        self.expr = expr

class ReflectiveStoreStatesNode(ASTNode):
    def __init__(self, expr):
        self.expr = expr

class ReflectiveGetNoiseNode(ASTNode):
    pass

class ReflectiveGetEntEstNode(ASTNode):
    pass

class ReflectiveGetSizeNode(ASTNode):
    pass

class ReflectiveCheckMailNode(ASTNode):
    pass

class ReflectiveClearMailNode(ASTNode):
    pass

class ReflectiveLoadMetabNode(ASTNode):
    pass

class ReflectiveStoreMetabNode(ASTNode):
    def __init__(self, expr):
        self.expr = expr

class ClipNode(ASTNode):
    def __init__(self, expr, min_val, max_val):
        self.expr = expr
        self.min_val = min_val
        self.max_val = max_val

class IndexNode(ASTNode):
    def __init__(self, left, index):
        self.left = left
        self.index = index

class IndexAssignNode(ASTNode):
    def __init__(self, name, index, value):
        self.name = name
        self.index = index
        self.value = value

class WhileNode(ASTNode):
    def __init__(self, condition, block):
        self.condition = condition
        self.block = block

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0

    def peek(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consume(self, expected_type=None):
        token = self.peek()
        if not token:
            raise SyntaxError("Unexpected end of input")
        if expected_type and token.type != expected_type:
            raise SyntaxError(f"Expected {expected_type}, got {token.type} at {token.line}:{token.column}")
        self.pos += 1
        return token

    def parse_program(self):
        statements = []
        while self.peek():
            statements.append(self.parse_statement())
        return ProgramNode(statements)

    def parse_statement(self):
        token = self.peek()
        if token.type == 'IMPORT':
            return self.parse_import()
        elif token.type == 'LET':
            return self.parse_var_decl()
        elif token.type == 'PRINT':
            return self.parse_print()
        elif token.type == 'CHAOS':
            return self.parse_chaos_block()
        elif token.type == 'IF':
            return self.parse_if()
        elif token.type == 'WHILE':
            return self.parse_while()
        elif token.type == 'SET_E':
            return self.parse_entropy_set()
        elif token.type == 'FUNC':
            return self.parse_func_decl()
        elif token.type == 'RETURN':
            return self.parse_return()
        elif token.type == 'ADAPT':
            return self.parse_adapt()
        elif token.type == 'SYSTEM':
            return self.parse_system()
        elif token.type == 'AGENT':
            return self.parse_agent()
        elif token.type == 'CLASS':
            return self.parse_class()
        elif token.type == 'SPAWN':
            return self.parse_spawn()
        elif token.type == 'VOLATILITY':
            return self.parse_volatility()
        elif token.type in ('STORE_W', 'STORE_S', 'LOAD_W', 'LOAD_S', 'GET_ID', 'LOAD_PREV_S', 'STORE_WEIGHTS', 'STORE_STATES', 'LOAD_WEIGHTS', 'LOAD_STATES', 'LOAD_PREV_STATES', 'GET_NOISE', 'GET_ENT_EST', 'GET_SIZE', 'CHECK_MAIL', 'CLEAR_MAIL', 'LOAD_METAB', 'STORE_METAB'):
            node = self.parse_expression()
            self.consume('SEMICOLON')
            return node
        elif token.type == 'IDENTIFIER':
            return self.parse_id_statement()
        else:
            raise SyntaxError(f"Unknown statement starting with {token.type} at {token.line}:{token.column}")

    def parse_import(self):
        self.consume('IMPORT')
        filename = self.consume('STRING').value
        self.consume('SEMICOLON')
        return ImportNode(filename)

    def parse_id_statement(self):
        # We need to handle:
        # 1. x = val
        # 2. x.y = val
        # 3. x[i] = val
        # 4. x.y(args)
        
        # Start by parsing the LValue/method target
        name = self.consume('IDENTIFIER').value
        while self.peek() and self.peek().type == 'DOT':
            self.consume('DOT')
            name += "." + self.consume('IDENTIFIER').value
            
        if self.peek() and self.peek().type == 'LBRACKET':
            # Index assignment
            self.consume('LBRACKET')
            idx_expr = self.parse_expression()
            self.consume('RBRACKET')
            self.consume('ASSIGN')
            value = self.parse_expression()
            self.consume('SEMICOLON')
            return IndexAssignNode(name, idx_expr, value)
            
        if self.peek() and self.peek().type == 'ASSIGN':
            self.consume('ASSIGN')
            value = self.parse_expression()
            self.consume('SEMICOLON')
            return VarDeclNode(name, value)
        elif self.peek() and self.peek().type == 'LPAREN':
            node = self.parse_call(name)
            self.consume('SEMICOLON')
            return node
        else:
            raise SyntaxError(f"Unexpected token after identifier {name}: {self.peek().type}")

    def parse_system(self):
        self.consume('SYSTEM')
        name = self.consume('IDENTIFIER').value
        self.consume('LBRACE')
        statements = []
        while self.peek() and self.peek().type != 'RBRACE':
            statements.append(self.parse_statement())
        self.consume('RBRACE')
        return SystemNode(name, statements)

    def parse_class(self):
        self.consume('CLASS')
        name = self.consume('IDENTIFIER').value
        parent = None
        if self.peek() and self.peek().type == 'COLON':
            self.consume('COLON')
            parent = self.consume('IDENTIFIER').value
        body = self.parse_block()
        return ClassNode(name, parent, body)

    def parse_agent(self):
        self.consume('AGENT')
        name = self.consume('IDENTIFIER').value
        self.consume('LBRACE')
        states = {}
        volatility = None
        update_block = []
        
        while self.peek() and self.peek().type != 'RBRACE':
            t = self.peek().type
            if t == 'STATE':
                self.consume('STATE')
                self.consume('LBRACE')
                while self.peek() and self.peek().type != 'RBRACE':
                    s_name = self.consume('IDENTIFIER').value
                    self.consume('COLON')
                    s_val = self.parse_expression()
                    states[s_name] = s_val
                    if self.peek() and self.peek().type == 'COMMA':
                        self.consume('COMMA')
                self.consume('RBRACE')
            elif t == 'VOLATILITY':
                self.consume('VOLATILITY')
                self.consume('ASSIGN')
                volatility = self.parse_expression()
                self.consume('SEMICOLON')
            elif t == 'UPDATE':
                self.consume('UPDATE')
                self.consume('LPAREN')
                self.consume('IDENTIFIER') # dt
                self.consume('RPAREN')
                update_block = self.parse_block()
            else:
                raise SyntaxError(f"Unexpected token in agent: {t}")
        
        self.consume('RBRACE')
        return AgentNode(name, states, volatility, update_block)

    def parse_spawn(self):
        self.consume('SPAWN')
        agent_name = self.consume('IDENTIFIER').value
        self.consume('IDENTIFIER') # 'size'
        self.consume('ASSIGN')
        size = self.consume('NUMBER').value
        topology = None
        if self.peek() and self.peek().type == 'IDENTIFIER' and self.peek().value == 'topology':
            self.consume('IDENTIFIER')
            self.consume('ASSIGN')
            topology = self.consume('IDENTIFIER').value # basic support for topology name
            if self.peek() and self.peek().type == 'LPAREN':
                self.consume('LPAREN')
                # Parse params if needed
                while self.peek() and self.peek().type != 'RPAREN':
                    self.consume()
                self.consume('RPAREN')
        self.consume('SEMICOLON')
        return SpawnNode(agent_name, size, topology)

    def parse_volatility(self):
        self.consume('VOLATILITY')
        # This can be 'volatility x = 0.5;' or 'volatility = 0.5;' inside agent update
        if self.peek() and self.peek().type == 'IDENTIFIER':
            var_name = self.consume('IDENTIFIER').value
            self.consume('ASSIGN')
            expr = self.parse_expression()
            self.consume('SEMICOLON')
            return VolatilityStmtNode(var_name, expr)
        else:
            # Inside agent potentially? or global?
            # For now, assume format 'volatility var = expr;'
            raise SyntaxError("Expected identifier after volatility")

    def parse_func_decl(self):
        self.consume('FUNC')
        name = self.consume('IDENTIFIER').value
        self.consume('LPAREN')
        params = []
        if self.peek() and self.peek().type != 'RPAREN':
            while True:
                p_name = self.consume('IDENTIFIER').value
                p_type = None
                if self.peek() and self.peek().type == 'COLON':
                    self.consume('COLON')
                    p_type = self.consume('IDENTIFIER').value
                params.append((p_name, p_type))
                if self.peek() and self.peek().type == 'COMMA':
                    self.consume('COMMA')
                else:
                    break
        self.consume('RPAREN')
        ret_type = None
        if self.peek() and self.peek().type == 'COLON':
            self.consume('COLON')
            ret_type = self.consume('IDENTIFIER').value
        block = self.parse_block()
        return FuncDeclNode(name, params, ret_type, block)

    def parse_return(self):
        self.consume('RETURN')
        expr = self.parse_expression()
        self.consume('SEMICOLON')
        return ReturnNode(expr)

    def parse_adapt(self):
        self.consume('ADAPT')
        target = self.consume('IDENTIFIER').value
        self.consume('TO')
        source = self.consume('IDENTIFIER').value
        self.consume('SEMICOLON')
        return AdaptNode(target, source)

    def parse_entropy_set(self):
        self.consume('SET_E')
        self.consume('LPAREN')
        expr = self.parse_expression()
        self.consume('RPAREN')
        self.consume('SEMICOLON')
        return EntropySetNode(expr)

    def parse_clip(self):
        self.consume('CLIP')
        self.consume('LPAREN')
        expr = self.parse_expression()
        self.consume('COMMA')
        min_v = self.parse_expression()
        self.consume('COMMA')
        max_v = self.parse_expression()
        self.consume('RPAREN')
        return ClipNode(expr, min_v, max_v)
    
    def parse_if(self):
        self.consume('IF')
        self.consume('LPAREN')
        cond = self.parse_expression()
        self.consume('RPAREN')
        then_block = self.parse_block()
        else_block = None
        if self.peek() and self.peek().type == 'ELSE':
            self.consume('ELSE')
            else_block = self.parse_block()
        return IfNode(cond, then_block, else_block)

    def parse_while(self):
        self.consume('WHILE')
        self.consume('LPAREN')
        cond = self.parse_expression()
        self.consume('RPAREN')
        block = self.parse_block()
        return WhileNode(cond, block)

    def parse_block(self):
        self.consume('LBRACE')
        statements = []
        while self.peek() and self.peek().type != 'RBRACE':
            statements.append(self.parse_statement())
        self.consume('RBRACE')
        return statements

    def parse_var_decl(self):
        self.consume('LET')
        name = self.consume('IDENTIFIER').value
        self.consume('ASSIGN')
        value = self.parse_expression()
        self.consume('SEMICOLON')
        return VarDeclNode(name, value)

    def parse_print(self):
        self.consume('PRINT')
        self.consume('LPAREN')
        expr = self.parse_expression()
        self.consume('RPAREN')
        self.consume('SEMICOLON')
        return PrintNode(expr)

    def parse_chaos_block(self):
        self.consume('CHAOS')
        self.consume('LBRACE')
        statements = []
        while self.peek() and self.peek().type != 'RBRACE':
            statements.append(self.parse_statement())
        self.consume('RBRACE')
        return ChaosBlockNode(statements)

    def parse_expression(self):
        # Handle binary operations including MATMUL
        left = self.parse_primary()
        while self.peek() and self.peek().type in ('PLUS', 'MINUS', 'MUL', 'DIV', 'MOD', 'CH_EQ', 'GT', 'LT', 'GE', 'LE', 'EQ', 'MATMUL'):
            op = self.consume().type
            right = self.parse_primary()
            left = BinaryOpNode(left, op, right)
        return left

    def parse_primary(self):
        token = self.peek()
        if token.type == 'NUMBER' or token.type == 'STRING':
            return LiteralNode(self.consume().value)
        elif token.type == 'IDENTIFIER':
            id_val = self.consume().value
            while self.peek() and self.peek().type == 'DOT':
                self.consume('DOT')
                id_val += "." + self.consume('IDENTIFIER').value
            
            node = IdentifierNode(id_val)
            
            # Handle possible call or index
            while self.peek() and self.peek().type in ('LPAREN', 'LBRACKET'):
                if self.peek().type == 'LPAREN':
                    node = self.parse_call_on(node)
                elif self.peek().type == 'LBRACKET':
                    self.consume('LBRACKET')
                    idx_expr = self.parse_expression()
                    self.consume('RBRACKET')
                    node = IndexNode(node, idx_expr)
            return node
        elif token.type == 'GET_E':
            self.consume('GET_E')
            self.consume('LPAREN')
            self.consume('RPAREN')
            return EntropyMeasureNode()
        elif token.type == 'CH_BR_L':
            self.consume('CH_BR_L')
            expr = self.parse_expression()
            self.consume('CH_BR_R')
            return ChaosBracketNode(expr)
        elif token.type == 'LOAD_W':
            self.consume('LOAD_W')
            self.consume('LPAREN')
            i = self.parse_expression()
            self.consume('COMMA')
            j = self.parse_expression()
            self.consume('RPAREN')
            return ReflectiveLoadWNode(i, j)
        elif token.type == 'STORE_W':
            self.consume('STORE_W')
            self.consume('LPAREN')
            i = self.parse_expression()
            self.consume('COMMA')
            j = self.parse_expression()
            self.consume('COMMA')
            val = self.parse_expression()
            self.consume('RPAREN')
            return ReflectiveStoreWNode(i, j, val)
        elif token.type == 'LOAD_S':
            self.consume('LOAD_S')
            self.consume('LPAREN')
            i = self.parse_expression()
            self.consume('RPAREN')
            return ReflectiveLoadSNode(i)
        elif token.type == 'LOAD_PREV_S':
            self.consume('LOAD_PREV_S')
            self.consume('LPAREN')
            i = self.parse_expression()
            self.consume('RPAREN')
            return ReflectiveLoadPrevSNode(i)
        elif token.type == 'STORE_S':
            self.consume('STORE_S')
            self.consume('LPAREN')
            i = self.parse_expression()
            self.consume('COMMA')
            val = self.parse_expression()
            self.consume('RPAREN')
            return ReflectiveStoreSNode(i, val)
        elif token.type == 'GET_ID':
            self.consume('GET_ID')
            self.consume('LPAREN')
            self.consume('RPAREN')
            return ReflectiveGetIdNode()
        elif token.type == 'LBRACKET':
            return self.parse_array()
        elif token.type == 'LOAD_WEIGHTS':
            self.consume('LOAD_WEIGHTS')
            self.consume('LPAREN')
            self.consume('RPAREN')
            return ReflectiveLoadWeightsNode()
        elif token.type == 'LOAD_STATES':
            self.consume('LOAD_STATES')
            self.consume('LPAREN')
            self.consume('RPAREN')
            return ReflectiveLoadStatesNode()
        elif token.type == 'LOAD_PREV_STATES':
            self.consume('LOAD_PREV_STATES')
            self.consume('LPAREN')
            self.consume('RPAREN')
            return ReflectiveLoadPrevStatesNode()
        elif token.type == 'STORE_WEIGHTS':
            self.consume('STORE_WEIGHTS')
            self.consume('LPAREN')
            expr = self.parse_expression()
            self.consume('RPAREN')
            return ReflectiveStoreWeightsNode(expr)
        elif token.type == 'STORE_STATES':
            self.consume('STORE_STATES')
            self.consume('LPAREN')
            expr = self.parse_expression()
            self.consume('RPAREN')
            return ReflectiveStoreStatesNode(expr)
        elif token.type == 'GET_NOISE':
            self.consume('GET_NOISE')
            self.consume('LPAREN')
            self.consume('RPAREN')
            return ReflectiveGetNoiseNode()
        elif token.type == 'GET_ENT_EST':
            self.consume('GET_ENT_EST')
            self.consume('LPAREN')
            self.consume('RPAREN')
            return ReflectiveGetEntEstNode()
        elif token.type == 'GET_SIZE':
            self.consume('GET_SIZE')
            self.consume('LPAREN')
            self.consume('RPAREN')
            return ReflectiveGetSizeNode()
        elif token.type == 'CHECK_MAIL':
            self.consume('CHECK_MAIL')
            self.consume('LPAREN')
            self.consume('RPAREN')
            return ReflectiveCheckMailNode()
        elif token.type == 'CLEAR_MAIL':
            self.consume('CLEAR_MAIL')
            self.consume('LPAREN')
            self.consume('RPAREN')
            return ReflectiveClearMailNode()
        elif token.type == 'LOAD_METAB':
            self.consume('LOAD_METAB')
            self.consume('LPAREN')
            self.consume('RPAREN')
            return ReflectiveLoadMetabNode()
        elif token.type == 'STORE_METAB':
            self.consume('STORE_METAB')
            self.consume('LPAREN')
            expr = self.parse_expression()
            self.consume('RPAREN')
            return ReflectiveStoreMetabNode(expr)
        elif token.type == 'CLIP':
            return self.parse_clip()
        elif token.type == 'LPAREN':
            self.consume('LPAREN')
            expr = self.parse_expression()
            self.consume('RPAREN')
            return expr
        elif token.type == 'MINUS':
            self.consume('MINUS')
            expr = self.parse_primary()
            return BinaryOpNode(LiteralNode(0.0), 'MINUS', expr)
        else:
            raise SyntaxError(f"Unexpected token in expression: {token.type}")

    def parse_array(self):
        self.consume('LBRACKET')
        elements = []
        if self.peek() and self.peek().type != 'RBRACKET':
            while True:
                elements.append(self.parse_expression())
                if self.peek() and self.peek().type == 'COMMA':
                    self.consume('COMMA')
                else:
                    break
        self.consume('RBRACKET')
        return ArrayNode(elements)

    def parse_call(self, name):
        node = IdentifierNode(name)
        return self.parse_call_on(node)

    def parse_call_on(self, callee_node):
        self.consume('LPAREN')
        args = []
        if self.peek() and self.peek().type != 'RPAREN':
            while True:
                args.append(self.parse_expression())
                if self.peek() and self.peek().type == 'COMMA':
                    self.consume('COMMA')
                else:
                    break
        self.consume('RPAREN')
        return CallNode(callee_node, args)

if __name__ == "__main__":
    from cilexer import Lexer
    code = 'let x = 10; print(x); chaos { print(x ≈ 10); }'
    lexer = Lexer(code)
    parser = Parser(lexer.tokenize())
    ast = parser.parse_program()
    print("AST generated successfully")
