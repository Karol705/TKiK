import sys

from src.parser import parse_rust_code
from src.utils import pretty_print_ast  


def main():
    input_file = "example-rust.r"
    output_file = "example-ast.txt"
        # Read Rust code from file
    with open(input_file, "r", encoding="utf-8") as f:
        rust_code = f.read()

    print(f"Parsing {input_file}...")
    
    try:
        # Parse the code
        ast = parse_rust_code(rust_code)
        
        # Write AST to output file (use repr for a raw Python representation)
        with open(output_file, "w", encoding="utf-8") as out:
            out.write(pretty_print_ast(ast))
        
        print(f"AST successfully written to {output_file}")
    except Exception as e:
        print(f"Parsing failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
