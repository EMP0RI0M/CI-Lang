import re

class Token:
    def __init__(self, type, value, line, column):
        self.type = type
        self.value = value
        self.line = line
        self.column = column

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)}, {self.line}:{self.column})"

class Lexer:
    TOKEN_SPEC = [
        ('COMMENT',  r'(//|#).*'),          # Single-line comment
        ('NUMBER',   r'\d+(\.\d*)?'),  # Integer or decimal number
        ('STRING',   r'"[^"]*"'),      # String literals
        ('IMPORT',   r'import\b'),     # import keyword
        ('LET',      r'let\b'),        # let keyword
        ('VAR',      r'var\b'),        # Mojo/Python style var
        ('FUNC',     r'func\b'),       # func keyword
        ('DEF',      r'def\b'),         # Mojo/Python style def
        ('CLASS',    r'class\b'),      # class keyword
        ('STRUCT',   r'struct\b'),     # Mojo style struct
        ('AGENT',    r'agent\b'),      # agent keyword
        ('SYSTEM',   r'system\b'),     # system keyword
        ('SPAWN',    r'spawn\b'),      # spawn keyword
        ('CLIP',     r'clip\b'),       # clip keyword
        ('VOLATILITY', r'volatility\b'), # volatility keyword
        ('UPDATE',   r'update\b'),     # update keyword
        ('STATE',    r'state\b'),      # state keyword
        ('CHAOS',    r'chaos\b'),      # chaos keyword
        ('ADAPT',    r'adapt\b'),      # adapt keyword
        ('TO',       r'to\b'),         # to keyword
        ('RETURN',   r'return\b'),     # return keyword
        ('IF',       r'if\b'),         # if keyword
        ('ELSE',     r'else\b'),       # else keyword
        ('WHILE',    r'while\b'),      # while keyword
        ('PUSH',     r'push\b'),       # push keyword
        ('PRINT',    r'print\b'),      # print keyword
        ('SET_E',    r'entropy::set\b'), # Special built-in
        ('GET_E',    r'entropy::measure\b'), # Special built-in
        ('GET_ID',   r'reflect::get_id\b'),
        ('IDENTIFIER', r'[a-zA-Z_]\w*'), # Identifiers
        ('CH_EQ',    r'≈'),            # Chaos equality
        ('ARROW',    r'→'),            # Entropy flow
        ('PLUS',     r'\+'),           # Plus
        ('MINUS',    r'-'),            # Minus
        ('MUL',      r'\*'),           # Multiply
        ('MATMUL',   r'@'),            # Matrix Multiply
        ('DIV',      r'/'),            # Divide
        ('MOD',      r'%'),            # Modulo
        ('EQ',       r'=='),           # Equality
        ('GE',       r'>='),           # Greater or Equal
        ('LE',       r'<='),           # Less or Equal
        ('GT',       r'>'),            # Greater Than
        ('LT',       r'<'),            # Less Than
        ('ASSIGN',   r'='),            # Assignment
        ('CH_BR_L',  r'⟨'),             # Chaos bracket L
        ('CH_BR_R',  r'⟩'),             # Chaos bracket R
        ('LPAREN',   r'\('),           # (
        ('RPAREN',   r'\)'),           # )
        ('LBRACE',   r'\{'),           # {
        ('RBRACE',   r'\}'),           # }
        ('LBRACKET', r'\['),           # [
        ('RBRACKET', r'\]'),           # ]
        ('SEMICOLON', r';'),           # ;
        ('COLON',    r':'),            # :
        ('COMMA',    r','),            # ,
        ('DOT',      r'\.'),           # .
        ('NEWLINE',  r'\n'),           # Line endings
        ('WHITESPACE', r'[ \t]+'),      # Skip whitespace
        ('MISMATCH', r'.'),            # Any other character
    ]

    def __init__(self, source_code):
        self.source_code = source_code
        self.tokens = []
        self.line_num = 1
        self.line_start = 0
        self.indent_stack = [0]

    def tokenize(self):
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in self.TOKEN_SPEC)
        lines = self.source_code.split('\n')
        
        for i, line in enumerate(lines):
            line_num = i + 1
            if not line.strip():
                continue
                
            # Leading whitespace for indentation
            indent_match = re.match(r'[ \t]*', line)
            indent_level = len(indent_match.group().expandtabs(4))
            
            # Emit INDENT/DEDENT
            if indent_level > self.indent_stack[-1]:
                self.indent_stack.append(indent_level)
                self.tokens.append(Token('INDENT', '', line_num, 0))
            elif indent_level < self.indent_stack[-1]:
                while indent_level < self.indent_stack[-1]:
                    self.indent_stack.pop()
                    self.tokens.append(Token('DEDENT', '', line_num, 0))
                if indent_level != self.indent_stack[-1]:
                    raise SyntaxError(f"Inconsistent indentation at line {line_num}")
            
            for mo in re.finditer(tok_regex, line):
                kind = mo.lastgroup
                value = mo.group()
                column = mo.start()
                
                if kind == 'NUMBER':
                    value = float(value) if '.' in value else int(value)
                elif kind == 'STRING':
                    value = value[1:-1]
                elif kind == 'WHITESPACE' or kind == 'COMMENT':
                    continue
                elif kind == 'MISMATCH':
                    raise SyntaxError(f'Unexpected character {value!r} on line {line_num}')
                
                self.tokens.append(Token(kind, value, line_num, column))
            
            self.tokens.append(Token('NEWLINE', '\n', line_num, len(line)))

        # Final DEDENTs
        while len(self.indent_stack) > 1:
            self.indent_stack.pop()
            self.tokens.append(Token('DEDENT', '', len(lines), 0))
            
        return self.tokens

if __name__ == "__main__":
    code = """
def stabilize(x):
    if x ≈ 50:
        return 50
    return x
    
agent A:
    state { val: 0 }
"""
    lexer = Lexer(code)
    for token in lexer.tokenize():
        print(token)
