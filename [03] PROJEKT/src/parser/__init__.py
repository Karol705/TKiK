from .lexer import Lexer
from .grammar import Parser

def parse_rust_code(code_string: str):
    """
    High-level utility to transform raw Rust code into an AST.
    This abstracts away the PLY boilerplate for the rest of the app.
    """
    lexer = Lexer()
    parser = Parser()
    
    # Standard PLY pattern: the parser needs the lexer object
    return parser.parse(code_string, lexer=lexer.get_lexer())

__all__ = ["Lexer", "Parser", "parse_rust_code"]