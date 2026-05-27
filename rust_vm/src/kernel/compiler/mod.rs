pub mod lexer;
pub mod parser;

use alloc::vec::Vec;
use crate::kernel::vm::instruction::Instruction;

pub fn compile(source: &str) -> Result<Vec<Instruction>, &'static str> {
    let mut lexer = lexer::Lexer::new(source);
    let tokens = lexer.tokenize();
    let mut parser = parser::Parser::new(tokens);
    parser.parse()
}
