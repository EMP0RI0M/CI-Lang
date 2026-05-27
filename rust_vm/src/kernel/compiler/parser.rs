use crate::kernel::vm::instruction::{Instruction, Opcode};
use crate::kernel::compiler::lexer::Token;
use alloc::vec::Vec;
use alloc::string::String;
use alloc::boxed::Box;

pub struct Parser {
    tokens: Vec<Token>,
    pos: usize,
}

impl Parser {
    pub fn new(tokens: Vec<Token>) -> Self {
        Self { tokens, pos: 0 }
    }

    fn peek(&self) -> Option<&Token> {
        self.tokens.get(self.pos)
    }

    fn advance(&mut self) -> Option<&Token> {
        let tok = self.tokens.get(self.pos);
        self.pos += 1;
        tok
    }
    
    // Quick and dirty string leak for no_std MVP Opcode compatibility
    fn leak_string(s: String) -> &'static str {
        Box::leak(s.into_boxed_str())
    }

    pub fn parse(&mut self) -> Result<Vec<Instruction>, &'static str> {
        let mut code = Vec::new();
        
        while self.pos < self.tokens.len() {
            let tok = self.advance().unwrap().clone();
            match tok {
                Token::Let => {
                    // let ident = expr
                    let ident_tok = self.advance().ok_or("Expected identifier after let")?;
                    let ident_name = if let Token::Identifier(name) = ident_tok {
                        name.clone()
                    } else {
                        return Err("Expected identifier after let");
                    };
                    
                    let eq_tok = self.advance().ok_or("Expected = after identifier")?;
                    if *eq_tok != Token::Equals {
                        return Err("Expected =");
                    }
                    
                    // Parse simple expression (supports 1 operator for now)
                    self.parse_expression(&mut code)?;
                    
                    code.push(Instruction::new(Opcode::Store(Self::leak_string(ident_name))));
                }
                Token::Agent => {
                    // agent Ident:
                    self.advance(); // Ident
                    self.advance(); // Colon
                    
                    // MVP: Skip block contents until we find 'spawn'
                    while let Some(tok) = self.peek() {
                        if *tok == Token::Spawn { break; }
                        self.advance();
                    }
                }
                Token::Spawn => {
                    // spawn Ident size = 50;
                    self.advance(); // Ident
                    if let Some(tok) = self.advance() {
                        if *tok == Token::Size {
                            self.advance(); // =
                            let num = self.advance().unwrap().clone();
                            if let Token::Number(n) = num {
                                code.push(Instruction::new(Opcode::SpawnAgent(n as usize)));
                            }
                            // consume optional semicolon
                            if let Some(semi) = self.peek() {
                                if *semi == Token::Semicolon {
                                    self.advance();
                                }
                            }
                        }
                    }
                }
                Token::ProcYield => {
                    code.push(Instruction::new(Opcode::ProcYield));
                }
                Token::EntropySample => {
                    // ENTROPY_SAMPLE(ident)
                    if let Some(Token::Identifier(name)) = self.advance() {
                        code.push(Instruction::new(Opcode::EntropySample(Self::leak_string(name.clone()))));
                    }
                }
                Token::StallOnDiv => {
                    // STALL_ON_DIV(num)
                    if let Some(Token::Number(num)) = self.advance() {
                        code.push(Instruction::new(Opcode::StallOnDiv(*num)));
                    }
                }
                Token::AdaptGain => {
                    // ADAPT_GAIN(num)
                    if let Some(Token::Number(num)) = self.advance() {
                        code.push(Instruction::new(Opcode::AdaptGain(*num)));
                    }
                }
                Token::Identifier(_name) => {}
                _ => {}
            }
        }
        
        code.push(Instruction::new(Opcode::Halt));
        Ok(code)
    }
    
    fn parse_expression(&mut self, code: &mut Vec<Instruction>) -> Result<(), &'static str> {
        // Parse left operand
        self.parse_primary(code)?;
        
        // Peek at operator
        if let Some(tok) = self.peek() {
            let op = match tok {
                Token::Plus => Some(Opcode::Add),
                Token::Minus => Some(Opcode::Sub),
                Token::Star => Some(Opcode::Mul),
                Token::Slash => Some(Opcode::Div),
                _ => None,
            };
            
            if let Some(opcode) = op {
                self.advance(); // consume operator
                self.parse_primary(code)?; // right operand
                code.push(Instruction::new(opcode));
            }
        }
        Ok(())
    }
    
    fn parse_primary(&mut self, code: &mut Vec<Instruction>) -> Result<(), &'static str> {
        let tok = self.advance().ok_or("Unexpected end of expression")?.clone();
        match tok {
            Token::Number(n) => {
                code.push(Instruction::new(Opcode::Lit(n)));
            }
            Token::Identifier(name) => {
                code.push(Instruction::new(Opcode::Load(Self::leak_string(name))));
            }
            _ => return Err("Expected Number or Identifier in expression"),
        }
        Ok(())
    }
}
