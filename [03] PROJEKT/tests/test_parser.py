import pytest
# Assuming you implemented the __init__.py as discussed previously
from src.parser import parse_rust_code

# ---------------------------------------------------------
# 1. Basic Variable Declarations (let_stmt)
# ---------------------------------------------------------
def test_let_statements():
    valid_code = [
        "let x = 5;",
        "let mut y = 10;",
        "let z: i32 = 15;",
        "let mut a: f64 = 3.14;",
        "let b;" # Uninitialized
    ]
    for code in valid_code:
        # Wrap in a fn block since let_stmt usually lives inside a block
        source = f"fn main() {{ {code} }}"
        ast = parse_rust_code(source)
        assert ast is not None, f"Failed to parse: {code}"

# ---------------------------------------------------------
# 2. Ownership & Borrowing (borrow_expr, lifetimes)
# ---------------------------------------------------------
def test_borrowing_and_lifetimes():
    source = """
    fn longest<'a, 'b>(x: &'a str, y: &'b str) -> &'a str {
        let a = &x;
        let mut b = &mut y;
        let c = *b; // Dereference
        return x;
    }
    """
    ast = parse_rust_code(source)
    assert ast is not None

# ---------------------------------------------------------
# 3. Control Flow (if, while, loop, for)
# ---------------------------------------------------------
def test_control_flow():
    source = """
    fn main() {
        let mut x = 0;
        
        if x == 0 {
            x = 1;
        } else if x < 5 {
            x += 2;
        } else {
            x = 10;
        }

        while x < 20 {
            x += 1;
        }

        'outer: loop {
            break 'outer;
        }

        for i in 0..10 {
            continue;
        }
    }
    """
    ast = parse_rust_code(source)
    assert ast is not None

# ---------------------------------------------------------
# 4. Structs and Instantiation
# ---------------------------------------------------------
def test_struct_definitions():
    source = """
    pub struct Point<'a> {
        x: f64,
        y: f64,
        name: &'a str,
    }

    fn main() {
        let p = Point { x: 1.0, y: 2.0, name: "Origin" };
        let p2 = Point { x: 3.0, ..p }; // Struct update syntax
    }
    """
    ast = parse_rust_code(source)
    assert ast is not None

# ---------------------------------------------------------
# 5. Functions and Generics
# ---------------------------------------------------------
def test_function_and_generics():
    source = """
    pub fn do_something<T, U>(a: T, b: U) -> T 
    where 
        T: 'static,
    {
        return a;
    }
    """
    ast = parse_rust_code(source)
    assert ast is not None

# ---------------------------------------------------------
# 6. Match Expressions (match_expr)
# ---------------------------------------------------------
def test_match_expression():
    source = """
    fn main() {
        let x = 5;
        match x {
            1 => { let a = 1; },
            2 | 3 => 4,
            _ => 0,
        }
    }
    """
    ast = parse_rust_code(source)
    assert ast is not None

# ---------------------------------------------------------
# 7. Expressions and Operator Precedence
# ---------------------------------------------------------
def test_operator_precedence():
    source = """
    fn main() {
        let a = 1 + 2 * 3;          # mul before add
        let b = (1 + 2) * 3;        # parens override
        let c = a == b && true;     # cmp before and
        let d = my_func(a, b).field[0]; # postfix operators
    }
    """
    ast = parse_rust_code(source)
    assert ast is not None

# ---------------------------------------------------------
# 8. Syntax Error Handling
# ---------------------------------------------------------
def test_invalid_syntax_raises_error():
    invalid_code = [
        "fn main() { let x = ; }",       # Missing expression
        "fn main() { let 5 = x; }",      # Invalid left-hand side
        "struct { x: i32 }",             # Missing struct name
        "fn main() { if true let x = 1; }", # Missing braces around if block
    ]
    
    for code in invalid_code:
        # Assuming your parser raises a SyntaxError or custom ParseError on failure.
        # If your parser just returns None on error, change this to: assert parse_rust_code(code) is None
        with pytest.raises(Exception): 
            parse_rust_code(code)