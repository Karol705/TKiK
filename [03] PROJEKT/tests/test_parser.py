"""
Testy jednostkowe dla leksera i parsera rust_state_tracker.
Uruchomienie: pytest tests/test_parser.py -v
"""

import pytest
from src.parser import parse_rust_code
from src.parser.lexer import Lexer


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def parse(code: str):
    """Zwraca węzeł 'program' lub None przy błędzie składni."""
    return parse_rust_code(code)


def items(ast) -> list:
    """Zwraca listę elementów najwyższego poziomu (fn_def itp.)."""
    assert ast is not None, "Parser zwrócił None — błąd składni"
    assert ast[0] == "program"
    return ast[1]


def lex_tokens(code: str) -> list[tuple]:
    """Zwraca listę par (typ, wartość) ze strumienia tokenów."""
    lexer = Lexer()
    lex = lexer.get_lexer()
    lex.input(code)
    return [(tok.type, tok.value) for tok in lex]


# ===========================================================================
# 1. TESTY LEKSERA
# ===========================================================================


class TestLexerLiterals:
    def test_integer(self):
        tokens = lex_tokens("42")
        assert tokens == [("INTEGER", 42)]

    def test_integer_with_underscores(self):
        tokens = lex_tokens("1_000_000")
        assert tokens == [("INTEGER", 1_000_000)]

    def test_float(self):
        tokens = lex_tokens("3.14")
        assert tokens == [("FLOAT", 3.14)]

    def test_string(self):
        tokens = lex_tokens('"hello world"')
        assert tokens == [("STRING", "hello world")]

    def test_string_with_escape(self):
        tokens = lex_tokens(r'"he said \"hi\""')
        assert tokens[0][0] == "STRING"

    def test_lifetime(self):
        tokens = lex_tokens("'a")
        assert tokens == [("LIFETIME", "'a")]

    def test_lifetime_static(self):
        tokens = lex_tokens("'static")
        assert tokens == [("LIFETIME", "'static")]


class TestLexerKeywords:
    @pytest.mark.parametrize("keyword,expected_type", [
        ("let",    "LET"),
        ("mut",    "MUT"),
        ("fn",     "FN"),
        ("return", "RETURN"),
        ("if",     "IF"),
        ("else",   "ELSE"),
        ("while",  "WHILE"),
        ("loop",   "LOOP"),
        ("break",  "BREAK"),
        ("true",   "TRUE"),
        ("false",  "FALSE"),
    ])
    def test_reserved_word(self, keyword, expected_type):
        tokens = lex_tokens(keyword)
        assert len(tokens) == 1
        assert tokens[0][0] == expected_type

    def test_ident_not_keyword(self):
        tokens = lex_tokens("letter")
        assert tokens == [("IDENT", "letter")]

    def test_ident_starting_with_keyword(self):
        # "letting" nie powinien być rozpoznany jako LET + IDENT
        tokens = lex_tokens("letting")
        assert tokens == [("IDENT", "letting")]


class TestLexerOperators:
    @pytest.mark.parametrize("src,expected_type", [
        ("==", "EQ"),
        ("!=", "NEQ"),
        ("<=", "LEQ"),
        (">=", "GEQ"),
        ("&&", "AND"),
        ("||", "OR"),
    ])
    def test_multi_char_operator(self, src, expected_type):
        tokens = lex_tokens(src)
        assert len(tokens) == 1
        assert tokens[0][0] == expected_type

    def test_eq_not_confused_with_assign(self):
        tokens = lex_tokens("==")
        assert tokens[0][0] == "EQ"
        tokens2 = lex_tokens("=")
        assert tokens2[0][0] == "ASSIGN"

    def test_neq_not_confused_with_not(self):
        # '!=' to NEQ, same '!' to NOT
        tokens = lex_tokens("!=")
        assert tokens[0][0] == "NEQ"
        tokens2 = lex_tokens("!")
        assert tokens2[0][0] == "NOT"


class TestLexerIgnored:
    def test_comment_ignored(self):
        tokens = lex_tokens("// cały wiersz komentarza\n42")
        assert tokens == [("INTEGER", 42)]

    def test_whitespace_ignored(self):
        tokens = lex_tokens("   42   ")
        assert tokens == [("INTEGER", 42)]


# ===========================================================================
# 2. TESTY PARSERA — DEKLARACJE ZMIENNYCH (let)
# ===========================================================================


class TestLetStatements:
    def _let(self, code: str):
        """Zwraca pierwsze wyrażenie w ciele funkcji opakowującej."""
        src = f"fn _f() {{ {code} }}"
        ast = parse(src)
        block = items(ast)[0][4]   # fn_def[4] = block
        return block[1][0]         # block[1] = stmt_list, [0] = pierwszy stmt

    def test_simple_let(self):
        node = self._let("let x = 5;")
        assert node[0] == "let"
        assert node[1] is False    # nie mut
        assert node[2] == "x"
        assert node[3] is None     # brak adnotacji typowej
        assert node[4] == ("literal", 5)

    def test_let_mut(self):
        node = self._let("let mut y = 10;")
        assert node[1] is True     # mut
        assert node[2] == "y"

    def test_let_with_type(self):
        node = self._let("let x: i32 = 42;")
        assert node[3] == ("type_name", "i32")
        assert node[4] == ("literal", 42)

    def test_let_mut_with_type(self):
        node = self._let("let mut z: f64 = 3.14;")
        assert node[1] is True
        assert node[3] == ("type_name", "f64")

    def test_let_no_init(self):
        node = self._let("let x: i32;")
        assert node[4] is None

    def test_let_borrow(self):
        node = self._let("let r = &x;")
        assert node[4] == ("borrow", False, ("ident", "x"))

    def test_let_mut_borrow(self):
        node = self._let("let r = &mut x;")
        assert node[4] == ("borrow", True, ("ident", "x"))


# ===========================================================================
# 3. TESTY PARSERA — DEFINICJE FUNKCJI
# ===========================================================================


class TestFunctionDefinitions:
    def test_fn_no_params_no_return(self):
        ast = parse("fn main() { }")
        fn = items(ast)[0]
        assert fn[0] == "fn_def"
        assert fn[1] == "main"
        assert fn[2] == []         # param_list
        assert fn[3] is None       # brak typu zwracanego

    def test_fn_with_return_type(self):
        ast = parse("fn answer() -> i32 { }")
        fn = items(ast)[0]
        assert fn[3] == ("type_name", "i32")

    def test_fn_with_params(self):
        ast = parse("fn add(a: i32, b: i32) -> i32 { }")
        fn = items(ast)[0]
        params = fn[2]
        assert len(params) == 2
        assert params[0] == ("param", "a", ("type_name", "i32"))
        assert params[1] == ("param", "b", ("type_name", "i32"))

    def test_fn_ref_param(self):
        ast = parse("fn foo(x: &i32) { }")
        fn = items(ast)[0]
        assert fn[2][0] == ("param", "x", ("ref", False, ("type_name", "i32")))

    def test_fn_mut_ref_param(self):
        ast = parse("fn bar(x: &mut i32) { }")
        fn = items(ast)[0]
        assert fn[2][0] == ("param", "x", ("ref", True, ("type_name", "i32")))

    def test_fn_lifetime_ref_param(self):
        ast = parse("fn baz(x: &'a i32) { }")
        fn = items(ast)[0]
        assert fn[2][0] == ("param", "x", ("ref_lifetime", "'a", False, ("type_name", "i32")))

    def test_multiple_fns(self):
        code = "fn foo() { } fn bar() { }"
        ast = parse(code)
        assert len(items(ast)) == 2

    def test_fn_trailing_expr(self):
        """Blok z wyrażeniem bez średnika jako wartość zwracana."""
        ast = parse("fn id(x: i32) -> i32 { x }")
        fn = items(ast)[0]
        block = fn[4]              # block
        assert block[2] == ("ident", "x")   # wyrażenie końcowe


# ===========================================================================
# 4. TESTY PARSERA — WYRAŻENIA
# ===========================================================================


class TestExpressions:
    def _expr(self, expr_code: str):
        """Parsuje wyrażenie opakowane w minimalną funkcję."""
        src = f"fn _f() {{ {expr_code}; }}"
        ast = parse(src)
        stmt = items(ast)[0][4][1][0]  # pierwszy stmt
        assert stmt[0] == "expr_stmt"
        return stmt[1]

    # --- literały ---
    def test_integer_literal(self):
        assert self._expr("42") == ("literal", 42)

    def test_float_literal(self):
        assert self._expr("3.14") == ("literal", 3.14)

    def test_string_literal(self):
        assert self._expr('"hi"') == ("literal", "hi")

    def test_true_literal(self):
        assert self._expr("true") == ("literal", "true")  # lub wartość bool zależnie od impl.

    def test_false_literal(self):
        assert self._expr("false")[0] == "literal"

    # --- operatory arytmetyczne ---
    def test_addition(self):
        assert self._expr("1 + 2") == ("binop", "+", ("literal", 1), ("literal", 2))

    def test_subtraction(self):
        assert self._expr("5 - 3") == ("binop", "-", ("literal", 5), ("literal", 3))

    def test_multiplication(self):
        assert self._expr("4 * 7") == ("binop", "*", ("literal", 4), ("literal", 7))

    def test_division(self):
        assert self._expr("8 / 2") == ("binop", "/", ("literal", 8), ("literal", 2))

    def test_modulo(self):
        assert self._expr("9 % 4") == ("binop", "%", ("literal", 9), ("literal", 4))

    # --- pierwszeństwo operatorów ---
    def test_precedence_mul_over_add(self):
        # 1 + 2 * 3  =>  binop(+, 1, binop(*, 2, 3))
        node = self._expr("1 + 2 * 3")
        assert node == ("binop", "+", ("literal", 1),
                        ("binop", "*", ("literal", 2), ("literal", 3)))

    def test_precedence_parens_override(self):
        # (1 + 2) * 3  =>  binop(*, binop(+, 1, 2), 3)
        node = self._expr("(1 + 2) * 3")
        assert node == ("binop", "*",
                        ("binop", "+", ("literal", 1), ("literal", 2)),
                        ("literal", 3))

    def test_precedence_cmp_over_logical(self):
        # a < b && c > d  =>  AND( LT(a,b), GT(c,d) )
        node = self._expr("a < b && c > d")
        assert node[0] == "binop"
        assert node[1] == "&&"
        assert node[2][1] == "<"
        assert node[3][1] == ">"

    # --- operatory porównania ---
    def test_eq(self):
        assert self._expr("x == y") == ("binop", "==", ("ident", "x"), ("ident", "y"))

    def test_neq(self):
        assert self._expr("x != y") == ("binop", "!=", ("ident", "x"), ("ident", "y"))

    def test_leq(self):
        assert self._expr("x <= y") == ("binop", "<=", ("ident", "x"), ("ident", "y"))

    # --- operatory unarne ---
    def test_unary_minus(self):
        assert self._expr("-5") == ("unary", "-", ("literal", 5))

    def test_unary_not(self):
        assert self._expr("!flag") == ("unary", "!", ("ident", "flag"))

    # --- referencje ---
    def test_borrow(self):
        assert self._expr("&x") == ("borrow", False, ("ident", "x"))

    def test_mut_borrow(self):
        assert self._expr("&mut x") == ("borrow", True, ("ident", "x"))

    # --- przypisanie ---
    def test_assign(self):
        assert self._expr("x = 10") == ("assign", "x", ("literal", 10))

    def test_assign_right_assoc(self):
        # x = y = 5  =>  assign(x, assign(y, 5))
        node = self._expr("x = y = 5")
        assert node == ("assign", "x", ("assign", "y", ("literal", 5)))

    # --- wywołania ---
    def test_fn_call_no_args(self):
        assert self._expr("foo()") == ("call", "foo", [])

    def test_fn_call_with_args(self):
        assert self._expr("add(1, 2)") == (
            "call", "add", [("literal", 1), ("literal", 2)]
        )

    def test_method_call(self):
        node = self._expr("v.len()")
        assert node == ("method_call", ("ident", "v"), "len", [])

    def test_method_call_with_args(self):
        node = self._expr("s.push(x)")
        assert node == ("method_call", ("ident", "s"), "push", [("ident", "x")])


# ===========================================================================
# 5. TESTY PARSERA — INSTRUKCJE STERUJĄCE
# ===========================================================================


class TestControlFlow:
    def _stmts(self, code: str) -> list:
        src = f"fn _f() {{ {code} }}"
        ast = parse(src)
        return items(ast)[0][4][1]

    def test_return_with_value(self):
        stmts = self._stmts("return 42;")
        assert stmts[0] == ("return", ("literal", 42))

    def test_return_without_value(self):
        stmts = self._stmts("return;")
        assert stmts[0] == ("return", None)

    def test_if_simple(self):
        stmts = self._stmts("if x { }")
        node = stmts[0]
        assert node[0] == "if"
        assert node[1] == ("ident", "x")
        assert node[3] is None    # brak else

    def test_if_else(self):
        stmts = self._stmts("if x { } else { }")
        node = stmts[0]
        assert node[0] == "if"
        assert node[3] is not None

    def test_if_else_if(self):
        stmts = self._stmts("if a { } else if b { }")
        node = stmts[0]
        # else-gałąź powinna być zagnieżdżonym węzłem 'if'
        assert node[3][0] == "if"
        assert node[3][1] == ("ident", "b")

    def test_while(self):
        stmts = self._stmts("while cond { }")
        assert stmts[0][0] == "while"
        assert stmts[0][1] == ("ident", "cond")

    def test_loop(self):
        stmts = self._stmts("loop { }")
        assert stmts[0][0] == "loop"

    def test_break(self):
        stmts = self._stmts("loop { break; }")
        inner = stmts[0][1][1]    # loop -> block -> stmt_list
        assert inner[0][0] == "break"

    def test_while_with_condition_expr(self):
        stmts = self._stmts("while i < 10 { }")
        cond = stmts[0][1]
        assert cond == ("binop", "<", ("ident", "i"), ("literal", 10))


# ===========================================================================
# 6. TESTY PARSERA — TYPY
# ===========================================================================


class TestTypes:
    def _param_type(self, type_str: str):
        ast = parse(f"fn _f(x: {type_str}) {{ }}")
        return items(ast)[0][2][0][2]   # fn_def -> params -> param[0] -> type

    def test_simple_type(self):
        assert self._param_type("i32") == ("type_name", "i32")

    def test_ref_type(self):
        assert self._param_type("&i32") == ("ref", False, ("type_name", "i32"))

    def test_mut_ref_type(self):
        assert self._param_type("&mut i32") == ("ref", True, ("type_name", "i32"))

    def test_lifetime_ref_type(self):
        assert self._param_type("&'a i32") == ("ref_lifetime", "'a", False, ("type_name", "i32"))

    def test_lifetime_mut_ref_type(self):
        assert self._param_type("&'a mut i32") == ("ref_lifetime", "'a", True, ("type_name", "i32"))

    def test_nested_ref(self):
        assert self._param_type("&&i32") == ("ref", False, ("ref", False, ("type_name", "i32")))


# ===========================================================================
# 7. TESTY BŁĘDÓW SKŁADNI
# ===========================================================================


class TestSyntaxErrors:
    def test_missing_semicolon(self):
        # Bez średnika parser powinien zwrócić None (lub wywołać p_error)
        result = parse("fn f() { let x = 5 }")
        assert result is None

    def test_missing_closing_brace(self):
        result = parse("fn f() { let x = 5;")
        assert result is None

    def test_empty_input(self):
        ast = parse("")
        assert ast == ("program", [])

    def test_fn_missing_body(self):
        result = parse("fn foo();")
        assert result is None

    def test_invalid_token(self):
        # '@' nie jest tokenem — lekser zgłosi błąd, parser zwróci None
        result = parse("fn f() { let x = @5; }")
        assert result is None


# ===========================================================================
# 8. TESTY INTEGRACYJNE — złożone programy
# ===========================================================================


class TestIntegration:
    def test_full_ownership_example(self):
        """Przykład z dokumentacji projektu."""
        code = """
        fn main() {
            let x = 5;
            let mut y = x;
            let r = &y;
        }
        """
        ast = parse(code)
        fn = items(ast)[0]
        stmts = fn[4][1]
        assert stmts[0] == ("let", False, "x", None, ("literal", 5))
        assert stmts[1] == ("let", True,  "y", None, ("ident",   "x"))
        assert stmts[2] == ("let", False, "r", None, ("borrow", False, ("ident", "y")))

    def test_function_calling_function(self):
        code = """
        fn square(x: i32) -> i32 {
            x * x
        }
        fn main() {
            let result = square(4);
        }
        """
        ast = parse(code)
        assert len(items(ast)) == 2
        main_stmts = items(ast)[1][4][1]
        call = main_stmts[0][4]
        assert call == ("call", "square", [("literal", 4)])

    def test_while_loop_with_break(self):
        code = """
        fn count() {
            let mut i = 0;
            while i < 10 {
                i = i + 1;
            }
        }
        """
        ast = parse(code)
        stmts = items(ast)[0][4][1]
        assert stmts[0][0] == "let"
        assert stmts[1][0] == "while"

    def test_nested_if(self):
        code = """
        fn classify(x: i32) -> i32 {
            if x < 0 {
                return -1;
            } else if x == 0 {
                return 0;
            } else {
                return 1;
            }
        }
        """
        ast = parse(code)
        stmts = items(ast)[0][4][1]
        node = stmts[0]
        assert node[0] == "if"
        assert node[3][0] == "if"       # else if
        assert node[3][3] is not None   # else

    def test_borrowing_in_function(self):
        code = """
        fn sum(a: &i32, b: &i32) -> i32 {
            a + b
        }
        """
        ast = parse(code)
        fn = items(ast)[0]
        assert fn[2][0][2] == ("ref", False, ("type_name", "i32"))
        tail_expr = fn[4][2]
        assert tail_expr == ("binop", "+", ("ident", "a"), ("ident", "b"))