import ply.yacc as yacc
from .lexer import Lexer

class Parser:
    tokens = Lexer.tokens

    def __init__(self):
        self.parser = yacc.yacc(module=self, write_tables=False)
    
    def parse(self, text, lexer=None):
        # This is the method called by your __init__.py
        return self.parser.parse(text, lexer=lexer)
    
    # =========================
    # POMOCNICZE
    # =========================

    def p_empty(self, p):
        'empty :'
        pass

    # =========================
    # PROGRAM
    # =========================

    def p_program(self, p):
        '''program : program item
                | empty'''
        if len(self, p) == 3:
            p[0] = ('program', p[1], p[2])
        else:
            p[0] = []

    # =========================
    # ITEM
    # =========================

    def p_item(self, p):
        '''item : fn_def
                | struct_def
                | impl_block
                | use_decl
                | type_alias
                | const_def
                | mod_block
                | attr item'''
        p[0] = ('item', p[1:])

    # =========================
    # ATTR
    # =========================

    def p_attr(self, p):
        'attr : OP_HASH LBRACKET attr_body RBRACKET'
        p[0] = ('attr', p[3])

    def p_attr_body(self, p):
        '''attr_body : IDENT
                    | IDENT LPAREN attr_args RPAREN'''
        p[0] = ('attr_body', p[1:])

    def p_attr_args(self, p):
        '''attr_args : attr_args IDENT
                    | empty'''
        p[0] = p[1:]

    # =========================
    # VISIBILITY
    # =========================

    def p_visibility(self, p):
        '''visibility : KW_PUB
                    | KW_PUB LPAREN KW_SELF RPAREN
                    | KW_PUB LPAREN IDENT RPAREN
                    | empty'''
        p[0] = ('vis', p[1:])

    # =========================
    # FUNCTION
    # =========================

    def p_fn_def(self, p):
        '''fn_def : visibility KW_FN IDENT generic_params_opt LPAREN param_list_opt RPAREN return_type_opt where_clause_opt block'''
        p[0] = ('fn', p[3], p[5], p[7], p[9])

    def p_param_list_opt(self, p):
        '''param_list_opt : param_list
                        | empty'''
        p[0] = p[1]

    def p_param_list(self, p):
        '''param_list : param
                    | param_list COMMA param'''
        p[0] = ('params', p[1:])

    def p_param(self, p):
        '''param : KW_SELF
                | OP_AMP lifetime_opt KW_MUT_opt KW_SELF
                | pattern COLON type'''
        p[0] = ('param', p[1:])

    def p_return_type_opt(self, p):
        '''return_type_opt : return_type
                        | empty'''
        p[0] = p[1]

    def p_return_type(self, p):
        'return_type : OP_ARROW type'
        p[0] = ('ret', p[2])

    # =========================
    # GENERICS [R]
    # =========================

    def p_generic_params_opt(self, p):
        '''generic_params_opt : generic_params
                            | empty'''
        p[0] = p[1]

    def p_generic_params(self, p):
        'generic_params : OP_LT generic_param_list OP_GT'
        p[0] = p[2]

    def p_generic_param_list(self, p):
        '''generic_param_list : generic_param
                            | generic_param_list COMMA generic_param'''
        p[0] = ('gen', p[1:])

    def p_generic_param(self, p):
        '''generic_param : LIFETIME_IDENT
                        | IDENT
                        | IDENT COLON type'''
        p[0] = ('gen_param', p[1:])

    # =========================
    # WHERE [R]
    # =========================

    def p_where_clause_opt(self, p):
        '''where_clause_opt : where_clause
                            | empty'''
        p[0] = p[1]

    def p_where_clause(self, p):
        'where_clause : IDENT where_pred_list'
        p[0] = ('where', p[2])

    def p_where_pred_list(self, p):
        '''where_pred_list : where_pred
                        | where_pred_list COMMA where_pred'''
        p[0] = ('where_list', p[1:])

    def p_where_pred(self, p):
        '''where_pred : type COLON type
                    | LIFETIME_IDENT COLON LIFETIME_IDENT'''
        p[0] = ('where_pred', p[1:])

    # =========================
    # STRUCT
    # =========================

    def p_struct_def(self, p):
        '''struct_def : visibility KW_STRUCT IDENT generic_params_opt struct_body
                    | visibility KW_STRUCT IDENT generic_params_opt SEMI'''
        p[0] = ('struct', p[3])

    def p_struct_body(self, p):
        'struct_body : LBRACE struct_fields_opt RBRACE'
        p[0] = p[2]

    def p_struct_fields_opt(self, p):
        '''struct_fields_opt : struct_field
                            | struct_fields_opt COMMA struct_field
                            | empty'''
        p[0] = p[1:]

    def p_struct_field(self, p):
        'struct_field : visibility IDENT COLON type'
        p[0] = ('field', p[2], p[4])

    # =========================
    # IMPL [R]
    # =========================

    def p_impl_block(self, p):
        'impl_block : KW_IMPL generic_params_opt type LBRACE impl_items RBRACE'
        p[0] = ('impl', p[3], p[5])

    def p_impl_items(self, p):
        '''impl_items : impl_item
                    | impl_items impl_item
                    | empty'''
        p[0] = p[1:]

    def p_impl_item(self, p):
        '''impl_item : fn_def
                    | type_alias
                    | attr impl_item'''
        p[0] = ('impl_item', p[1:])

    # =========================
    # USE
    # =========================

    def p_use_decl(self, p):
        'use_decl : visibility KW_USE use_tree SEMI'
        p[0] = ('use', p[3])

    def p_use_tree(self, p):
        '''use_tree : path
                    | LBRACE use_tree_list RBRACE'''
        p[0] = ('use_tree', p[1:])

    def p_use_tree_list(self, p):
        '''use_tree_list : use_tree
                        | use_tree_list COMMA use_tree'''
        p[0] = p[1:]

    def p_path(self, p):
        '''path : IDENT
                | path OP_PATH IDENT'''
        p[0] = ('path', p[1:])

    # =========================
    # EXTRA [R]
    # =========================

    def p_type_alias(self, p):
        'type_alias : visibility KW_TYPE IDENT OP_ASSIGN type SEMI'
        p[0] = ('type_alias', p[3], p[5])

    def p_const_def(self, p):
        'const_def : visibility KW_CONST IDENT COLON type OP_ASSIGN expr SEMI'
        p[0] = ('const', p[3])

    def p_mod_block(self, p):
        '''mod_block : visibility KW_MOD IDENT LBRACE program RBRACE
                    | visibility KW_MOD IDENT SEMI'''
        p[0] = ('mod', p[3])

    # =========================
    # BLOCK / STMT
    # =========================

    def p_block(self, p):
        'block : LBRACE stmt_list RBRACE'
        p[0] = ('block', p[2])

    def p_stmt_list(self, p):
        '''stmt_list : stmt
                    | stmt_list stmt
                    | empty'''
        p[0] = p[1:]

    def p_stmt(self, p):
        '''stmt : let_stmt
                | expr_stmt
                | return_stmt
                | break_stmt
                | continue_stmt
                | item'''
        p[0] = ('stmt', p[1])

    def p_let_stmt(self, p):
        'let_stmt : KW_LET KW_MUT_opt pattern SEMI'
        p[0] = ('let', p[3])

    def p_expr_stmt(self, p):
        'expr_stmt : expr SEMI'
        p[0] = ('expr_stmt', p[1])

    def p_return_stmt(self, p):
        'return_stmt : KW_RETURN expr_opt SEMI'
        p[0] = ('return', p[2])

    def p_break_stmt(self, p):
        'break_stmt : KW_BREAK expr_opt SEMI'
        p[0] = ('break', p[2])

    def p_continue_stmt(self, p):
        'continue_stmt : KW_CONTINUE SEMI'
        p[0] = ('continue',)

    # =========================
    # WYRAŻENIA (pełna hierarchia)
    # =========================

    def p_expr(self, p):
        'expr : assign_expr'
        p[0] = p[1]

    def p_assign_expr(self, p):
        '''assign_expr : range_expr
                    | range_expr assign_op assign_expr'''
        p[0] = ('assign', p[1:])

    def p_assign_op(self, p):
        '''assign_op : OP_ASSIGN
                    | OP_ADD_ASSIGN
                    | OP_SUB_ASSIGN
                    | OP_MUL_ASSIGN
                    | OP_DIV_ASSIGN
                    | OP_REM_ASSIGN'''
        p[0] = p[1]

    def p_range_expr(self, p):
        '''range_expr : or_expr
                    | or_expr OP_DOTDOT or_expr
                    | or_expr OP_DOTDOTEQ or_expr'''
        p[0] = ('range', p[1:])

    def p_or_expr(self, p):
        '''or_expr : and_expr
                | or_expr OP_OR_OR and_expr'''
        p[0] = ('or', p[1:])

    def p_and_expr(self, p):
        '''and_expr : cmp_expr
                    | and_expr OP_AND_AND cmp_expr'''
        p[0] = ('and', p[1:])

    def p_cmp_expr(self, p):
        '''cmp_expr : add_expr
                    | cmp_expr cmp_op add_expr'''
        p[0] = ('cmp', p[1:])

    def p_cmp_op(self, p):
        '''cmp_op : OP_EQ_EQ 
                    | OP_NE 
                    | OP_LT 
                    | OP_GT 
                    | OP_LE 
                    | OP_GE'''
        p[0] = p[1]

    def p_add_expr(self, p):
        '''add_expr : mul_expr
                    | add_expr OP_PLUS mul_expr
                    | add_expr OP_MINUS mul_expr'''
        p[0] = ('add', p[1:])

    def p_mul_expr(self, p):
        '''mul_expr : cast_expr
                    | mul_expr OP_STAR cast_expr
                    | mul_expr OP_SLASH cast_expr
                    | mul_expr OP_PERCENT cast_expr'''
        p[0] = ('mul', p[1:])

    def p_cast_expr(self, p):
        '''cast_expr : unary_expr
                    | cast_expr KW_AS type'''
        p[0] = ('cast', p[1:])

    def p_unary_expr(self, p):
        '''unary_expr : OP_MINUS unary_expr
                    | OP_BANG unary_expr
                    | OP_STAR unary_expr
                    | postfix_expr'''
        p[0] = ('unary', p[1:])

    def p_postfix_expr(self, p):
        '''postfix_expr : primary_expr
                        | postfix_expr postfix_op'''
        p[0] = ('postfix', p[1:])

    def p_postfix_op(self, p):
        '''postfix_op : DOT IDENT
                    | LPAREN RPAREN
                    | OP_QUESTION'''
        p[0] = ('postfix_op', p[1:])

    # =========================
    # PRIMARY
    # =========================

    def p_primary_expr(self, p):
        '''primary_expr : literal
                        | IDENT
                        | path
                        | block
                        | LPAREN expr RPAREN'''
        p[0] = ('primary', p[1:])

    # =========================
    # LITERAL
    # =========================

    def p_literal(self, p):
        '''literal : LIT_INT
                | LIT_INT_HEX
                | LIT_INT_BIN
                | LIT_FLOAT
                | LIT_STR
                | LIT_STR_RAW
                | LIT_CHAR
                | KW_TRUE
                | KW_FALSE'''
        p[0] = ('lit', p[1])

    # =========================
    # TYPE (uproszczone ale kompletne strukturalnie)
    # =========================

    def p_type(self, p):
        '''type : IDENT
                | OP_AMP type
                | OP_STAR type
                | LPAREN type RPAREN'''
        p[0] = ('type', p[1:])

    # =========================
    # OPTIONAL HELPERS
    # =========================

    def p_expr_opt(self, p):
        '''expr_opt : expr
                    | empty'''
        p[0] = p[1]

    def p_lifetime_opt(self, p):
        '''lifetime_opt : LIFETIME_IDENT
                        | empty'''
        p[0] = p[1]

    def p_KW_MUT_opt(self, p):
        '''KW_MUT_opt : KW_MUT
                    | empty'''
        p[0] = p[1]

    # =========================
    # ERROR
    # =========================

    def p_error(self, p):
        if p:
            print(f"Syntax error at {p.value}")
        else:
            print("Syntax error at EOF")