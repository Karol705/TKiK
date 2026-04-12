import ply.yacc as yacc
from .lexer import Lexer

class Parser:
    tokens = Lexer.tokens

    def __init__(self):
        self.parser = yacc.yacc(module=self, write_tables=False)
    
    def parse(self, text, lexer=None):
        # This is the method called by your __init__.py
        return self.parser.parse(text, lexer=lexer)
    
# PROGRAM
    def p_program(self,p):
        """program : item_list"""
        p[0] = ('program', p[1])

    def p_item_list(self,p):
        """item_list : item_list item
                    | empty"""
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = []

    def p_item(self,p):
        """item : fn_def
                | const_def
                | static_def"""
        p[0] = p[1]
        
# FUNKCJA
    def p_fn_def(self,p):
        """fn_def : FN IDENT LPAREN param_list RPAREN ARROW type block
                | FN IDENT LPAREN param_list RPAREN block"""
        if len(p) == 9:
            p[0] = ('fn_def', p[2], p[4], p[7], p[8])
        else:
            p[0] = ('fn_def', p[2], p[4], None, p[6])

    def p_param_list_empty(self,p):
        """param_list : empty"""
        p[0] = []

    def p_param_list_single(self,p):
        """param_list : param"""
        p[0] = [p[1]]

    def p_param_list_multi(self,p):
        """param_list : param_list COMMA param"""
        p[0] = p[1] + [p[3]]

    def p_param(self,p):
        """param : IDENT COLON type"""
        p[0] = ('param', p[1], p[3])

# TYPY
    def p_type_ident(self,p):
        """type : IDENT"""
        p[0] = ('type_name', p[1])

    def p_type_ref(self,p):
        """type : AMP type"""
        p[0] = ('ref', False, p[2])

    def p_type_mut_ref(self,p):
        """type : AMP MUT type"""
        p[0] = ('ref', True, p[3])

    def p_type_lifetime_ref(self,p):
        """type : AMP LIFETIME type"""
        p[0] = ('ref_lifetime', p[2], False, p[3])

    def p_type_lifetime_mut_ref(self,p):
        """type : AMP LIFETIME MUT type"""
        p[0] = ('ref_lifetime', p[2], True, p[4])
        
# BLOK I INSTRUKCJE
    def p_block(self,p):
        """block : LBRACE stmt_list RBRACE
                | LBRACE stmt_list expr RBRACE"""
        if len(p) == 4:
            p[0] = ('block', p[2], None)
        else:
            p[0] = ('block', p[2], p[3])

    def p_stmt_list(self,p):
        """stmt_list : stmt_list stmt
                    | empty"""
        if len(p) == 3:
            p[0] = p[1] + [p[2]]
        else:
            p[0] = []

    def p_stmt(self,p):
        """stmt : let_stmt
                | expr_stmt
                | return_stmt
                | if_stmt
                | while_stmt
                | loop_stmt
                | break_stmt
                | item"""
        p[0] = p[1]

# DEKLARACJA ZMIENNEJ        
    def p_let_stmt_full(self,p):
        """let_stmt : LET opt_mut IDENT opt_type_annotation opt_init SEMICOLON"""
        p[0] = ('let', p[2], p[3], p[4], p[5])

    def p_opt_mut(self, p):
        """opt_mut : MUT
                | empty"""
        p[0] = True if p[1] is not None else False

    def p_opt_type_annotation(self, p):
        """opt_type_annotation : COLON type
                            | empty"""
        if len(p) == 3:
            p[0] = p[2]
        else:
            p[0] = None

    def p_opt_init(self, p):
        """opt_init : ASSIGN expr
                    | empty"""
        if len(p) == 3:
            p[0] = p[2]
        else:
            p[0] = None
        
# CONST
    def p_const_def(self,p):
        """const_def : CONST IDENT COLON type ASSIGN expr SEMICOLON"""
        p[0] = ('const_def', p[2], p[4], p[6])

# STATIC
    def p_static_def(self,p):
        """static_def : STATIC opt_mut IDENT COLON type ASSIGN expr SEMICOLON"""
        p[0] = ('static_def', p[2], p[3], p[5], p[7])

# INSTRUKCJA WYRAŻENIA
    def p_expr_stmt(self,p):
        """expr_stmt : expr SEMICOLON"""
        p[0] = ('expr_stmt', p[1])

# INSTRUKCJA RETURN
    def p_return_stmt(self,p):
        """return_stmt : RETURN expr SEMICOLON
                    | RETURN SEMICOLON"""
        if len(p) == 4:
            p[0] = ('return', p[2])
        else:
            p[0] = ('return', None)

# INSTRUKCJA WARUNKOWA if/else
    def p_if_stmt(self,p):
        """if_stmt : IF expr block
                | IF expr block ELSE block
                | IF expr block ELSE if_stmt"""
        if len(p) == 4:
            p[0] = ('if', p[2], p[3], None)
        else:
            p[0] = ('if', p[2], p[3], p[5])

# PĘTLA WHILE       
    def p_while_stmt(self,p):
        """while_stmt : WHILE expr block"""
        p[0] = ('while', p[2], p[3])

# PĘTLA LOOP I BREAK
    def p_loop_stmt(self,p):
        """loop_stmt : LOOP block"""
        p[0] = ('loop', p[2])

    def p_break_stmt(self,p):
        """break_stmt : BREAK SEMICOLON"""
        p[0] = ('break',)

    # Deklaracja priorytetów dla PLY (rozwiązuje konflikty shift/reduce)
    precedence = (
        ('right',  'ASSIGN'),
        ('left',   'OR'),
        ('left',   'AMP'),
        ('nonassoc', 'EQ', 'NEQ'),
        ('nonassoc', 'LT', 'GT', 'LEQ', 'GEQ'),
        ('left',   'PLUS', 'MINUS'),
        ('left',   'STAR', 'SLASH', 'PERCENT'),
        ('right',  'UMINUS', 'NOT', 'UREF', 'UMUTREF'),
        ('left',   'DOT', 'LPAREN'),
    )

    def p_expr_assign(self,p):
        """expr : IDENT ASSIGN expr"""
        p[0] = ('assign', p[1], p[3])

    def p_expr_binop(self,p):
        """expr : expr OR  expr
                | expr AMP AMP expr
                | expr EQ  expr
                | expr NEQ expr
                | expr LT  expr
                | expr GT  expr
                | expr LEQ expr
                | expr GEQ expr
                | expr PLUS   expr
                | expr MINUS  expr
                | expr STAR   expr
                | expr SLASH  expr
                | expr PERCENT expr"""
        if len(p) == 5:  # AMP AMP case
            p[0] = ('binop', '&&', p[1], p[4])
        else:
            p[0] = ('binop', p[2], p[1], p[3])

    def p_expr_unary_minus(self,p):
        """expr : MINUS expr %prec UMINUS"""
        p[0] = ('unary', '-', p[2])

    def p_expr_unary_not(self,p):
        """expr : NOT expr"""
        p[0] = ('unary', '!', p[2])

    def p_expr_ref(self,p):
        """expr : AMP expr %prec UREF"""
        p[0] = ('borrow', False, p[2])

    def p_expr_mut_ref(self,p):
        """expr : AMP MUT expr %prec UMUTREF"""
        p[0] = ('borrow', True, p[3])

    def p_expr_atom(self,p):
        """expr : INTEGER
                | FLOAT
                | STRING
                | TRUE
                | FALSE"""
        p[0] = ('literal', p[1])

    def p_expr_ident(self,p):
        """expr : IDENT"""
        p[0] = ('ident', p[1])

    def p_expr_paren(self,p):
        """expr : LPAREN expr RPAREN"""
        p[0] = p[2]

    def p_expr_fn_call(self,p):
        """expr : IDENT LPAREN arg_list RPAREN"""
        p[0] = ('call', p[1], p[3])

    def p_expr_method_call(self,p):
        """expr : expr DOT IDENT LPAREN arg_list RPAREN"""
        p[0] = ('method_call', p[1], p[3], p[5])

    def p_arg_list_empty(self,p):
        """arg_list : empty"""
        p[0] = []

    def p_arg_list_single(self,p):
        """arg_list : expr"""
        p[0] = [p[1]]

    def p_arg_list_multi(self,p):
        """arg_list : arg_list COMMA expr"""
        p[0] = p[1] + [p[3]]
        
    def p_empty(self,p):
        """empty :"""
        p[0] = None
        
    def p_error(self,p):
        if p:
            print(f"Błąd składni: nieoczekiwany token '{p.value}' ({p.type}) w linii {p.lineno}")
        else:
            print("Błąd składni: nieoczekiwany koniec pliku")