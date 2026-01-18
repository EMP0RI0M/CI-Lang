import sys
import pickle
from cilexer import Lexer
from ciparser import Parser
from cicompiler import Compiler

def main():
    if len(sys.argv) < 2:
        print("Usage: python cic.py <source.ci> [-o <output.bc>]")
        return

    source_file = sys.argv[1]
    output_file = "output.bc"
    
    if "-o" in sys.argv:
        idx = sys.argv.index("-o")
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]

    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            source_code = f.read()

        lexer = Lexer(source_code)
        tokens = lexer.tokenize()
        
        parser = Parser(tokens)
        ast = parser.parse_program()
        
        compiler = Compiler()
        bytecode = compiler.compile(ast)
        
        with open(output_file, 'wb') as f:
            pickle.dump(bytecode, f)
            
        print(f"Compilation successful. Bytecode written to {output_file}")

    except Exception as e:
        print(f"Compilation Error: {e}")

if __name__ == "__main__":
    main()
