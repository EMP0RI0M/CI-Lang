use alloc::string::String;
use alloc::vec::Vec;

#[derive(Debug, PartialEq, Clone)]
pub enum Token {
    Let,
    Spawn,
    Agent,
    Size,
    ProcYield,
    EntropySample,
    StallOnDiv,
    AdaptGain,
    Identifier(String),
    Number(f64),
    Equals,
    Plus,
    Minus,
    Star,
    Slash,
    Arrow,
    Colon,
    Semicolon,
    EOF,
}

pub struct Lexer<'a> {
    input: &'a str,
    pos: usize,
    chars: Vec<char>,
}

impl<'a> Lexer<'a> {
    pub fn new(input: &'a str) -> Self {
        Self {
            input,
            pos: 0,
            chars: input.chars().collect(),
        }
    }

    fn skip_whitespace(&mut self) {
        while self.pos < self.chars.len() && self.chars[self.pos].is_whitespace() {
            self.pos += 1;
        }
    }

    pub fn next_token(&mut self) -> Token {
        self.skip_whitespace();
        
        if self.pos >= self.chars.len() {
            return Token::EOF;
        }

        let c = self.chars[self.pos];

        // Operators
        match c {
            '=' => { self.pos += 1; return Token::Equals; }
            '+' => { self.pos += 1; return Token::Plus; }
            '-' => { self.pos += 1; return Token::Minus; }
            '*' => { self.pos += 1; return Token::Star; }
            '/' => { self.pos += 1; return Token::Slash; }
            '→' => { self.pos += 1; return Token::Arrow; }
            ':' => { self.pos += 1; return Token::Colon; }
            ';' => { self.pos += 1; return Token::Semicolon; }
            _ => {}
        }

        // Numbers
        if c.is_ascii_digit() {
            let mut num_str = String::new();
            while self.pos < self.chars.len() && (self.chars[self.pos].is_ascii_digit() || self.chars[self.pos] == '.') {
                num_str.push(self.chars[self.pos]);
                self.pos += 1;
            }
            if let Ok(num) = num_str.parse::<f64>() {
                return Token::Number(num);
            }
        }

        // Identifiers and Keywords
        if c.is_alphabetic() || c == '_' {
            let mut ident = String::new();
            while self.pos < self.chars.len() && (self.chars[self.pos].is_alphanumeric() || self.chars[self.pos] == '_') {
                ident.push(self.chars[self.pos]);
                self.pos += 1;
            }
            
            return match ident.as_str() {
                "let" => Token::Let,
                "spawn" => Token::Spawn,
                "agent" => Token::Agent,
                "size" => Token::Size,
                "PROC_YIELD" => Token::ProcYield,
                "ENTROPY_SAMPLE" => Token::EntropySample,
                "STALL_ON_DIV" => Token::StallOnDiv,
                "ADAPT_GAIN" => Token::AdaptGain,
                _ => Token::Identifier(ident),
            };
        }

        // Skip unknown chars for now
        self.pos += 1;
        self.next_token()
    }
    
    pub fn tokenize(&mut self) -> Vec<Token> {
        let mut tokens = Vec::new();
        loop {
            let tok = self.next_token();
            if tok == Token::EOF { break; }
            tokens.push(tok);
        }
        tokens
    }
}
