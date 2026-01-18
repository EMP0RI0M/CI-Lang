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
        ('FUNC',     r'func\b'),       # func keyword
        ('CLASS',    r'class\b'),      # class keyword
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
        ('PRINT',    r'print\b'),      # print keyword
        ('SET_E',    r'entropy::set\b'), # Special built-in
        ('GET_E',    r'entropy::measure\b'), # Special built-in
        ('LOAD_W',   r'reflect::load_w\b'),
        ('STORE_W',  r'reflect::store_w\b'),
        ('LOAD_WEIGHTS', r'reflect::weights\b'),  # New: Load whole matrix
        ('STORE_WEIGHTS', r'reflect::store_weights\b'), # New: Store whole matrix
        ('LOAD_STATES', r'reflect::states\b'),    # New: Load all state vector
        ('STORE_STATES', r'reflect::store_states\b'),   # New: Store all state vector
        ('LOAD_PREV_STATES', r'reflect::prev_states\b'), # New: Load all prev states
        ('GET_NOISE', r'reflect::noise\b'),       # New: Get noise vector
        ('GET_ENT_EST', r'reflect::estimate_entropy\b'), # New: Est entropy
        ('GET_SIZE', r'reflect::size\b'),         # New: Get swarm size
        ('CHECK_MAIL', r'reflect::check_mailbox\b'), # New: Check host input
        ('CLEAR_MAIL', r'reflect::clear_mailbox\b'), # New: Clear host input
        ('LOAD_METAB', r'reflect::metabolism\b'),    # New: Phase 21 Biology
        ('STORE_METAB', r'reflect::store_metabolism\b'), # New: Phase 21 Biology
        ('LOAD_S',   r'reflect::load_s\b'),
        ('LOAD_PREV_S', r'reflect::load_prev_s\b'),
        ('STORE_S',  r'reflect::store_s\b'),
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
        ('WHITESPACE', r'[ \t]+'),      # Skip whitespace
        ('NEWLINE',  r'\n'),           # Line endings
        ('MISMATCH', r'.'),            # Any other character
    ]

    def __init__(self, source_code):
        self.source_code = source_code
        self.tokens = []
        self.line_num = 1
        self.line_start = 0

    def tokenize(self):
        tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in self.TOKEN_SPEC)
        for mo in re.finditer(tok_regex, self.source_code):
            kind = mo.lastgroup
            value = mo.group()
            column = mo.start() - self.line_start
            if kind == 'NUMBER':
                value = float(value) if '.' in value else int(value)
            elif kind == 'STRING':
                value = value[1:-1] # Strip quotes
            elif kind == 'NEWLINE':
                self.line_start = mo.end()
                self.line_num += 1
                continue
            elif kind == 'COMMENT' or kind == 'WHITESPACE':
                continue
            elif kind == 'MISMATCH':
                raise SyntaxError(f'Unexpected character {value!r} on line {self.line_num}')
            
            self.tokens.append(Token(kind, value, self.line_num, column))
        return self.tokens

if __name__ == "__main__":
    code = 'let x = 10; chaos { if (x ≈ 10) { print("Chaos!"); } }'
    lexer = Lexer(code)
    for token in lexer.tokenize():
        print(token)
