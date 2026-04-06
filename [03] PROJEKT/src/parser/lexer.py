import ply.lex as lex

class Lexer:
    # =========================
    # SŁOWA KLUCZOWE
    # =========================

    reserved = {
        'let': 'KW_LET',
        'mut': 'KW_MUT',
        'fn': 'KW_FN',
        'return': 'KW_RETURN',
        'if': 'KW_IF',
        'else': 'KW_ELSE',
        'while': 'KW_WHILE',
        'loop': 'KW_LOOP',
        'for': 'KW_FOR',
        'in': 'KW_IN',
        'break': 'KW_BREAK',
        'continue': 'KW_CONTINUE',
        'struct': 'KW_STRUCT',
        'impl': 'KW_IMPL',
        'self': 'KW_SELF',
        'pub': 'KW_PUB',
        'use': 'KW_USE',
        'mod': 'KW_MOD',           # [R]
        'move': 'KW_MOVE',
        'ref': 'KW_REF',
        'match': 'KW_MATCH',       # [R]
        'as': 'KW_AS',             # [R]
        'const': 'KW_CONST',       # [R]
        'static': 'KW_STATIC',     # [R]
        'type': 'KW_TYPE',         # [R]
        'unsafe': 'KW_UNSAFE',     # [R]
        'extern': 'KW_EXTERN',     # [R]
        'true': 'KW_TRUE',
        'false': 'KW_FALSE',
    }

    # =========================
    # TOKENY
    # =========================

    tokens = [
        # Identyfikatory i lifetimes
        'IDENT',
        'LIFETIME_IDENT',
        'LIFETIME_ANON',

        # Literały
        'LIT_INT',
        'LIT_INT_HEX',
        'LIT_INT_BIN',
        'LIT_FLOAT',
        'LIT_STR',
        'LIT_STR_RAW',
        'LIT_CHAR',
        'LIT_BYTE',        # [R]
        'LIT_BYTE_STR',    # [R]

        # Operatory
        'OP_ARROW',
        'OP_FAT_ARROW',
        'OP_PATH',
        'OP_DOTDOTEQ',
        'OP_DOTDOT',
        'OP_AND_AND',
        'OP_OR_OR',
        'OP_EQ_EQ',
        'OP_NE',
        'OP_LE',
        'OP_GE',
        'OP_SHL',          # [R]
        'OP_SHR',          # [R]
        'OP_ADD_ASSIGN',
        'OP_SUB_ASSIGN',
        'OP_MUL_ASSIGN',   # [R]
        'OP_DIV_ASSIGN',   # [R]
        'OP_REM_ASSIGN',   # [R]

        'OP_ASSIGN',
        'OP_LT',
        'OP_GT',
        'OP_AMP',
        'OP_PIPE',         # [R]
        'OP_STAR',
        'OP_PLUS',
        'OP_MINUS',
        'OP_SLASH',
        'OP_PERCENT',      # [R]
        'OP_BANG',
        'OP_CARET',        # [R]
        'OP_TILDE',
        'OP_AT',           # [R]
        'OP_HASH',         # [R]
        'OP_QUESTION',     # [R]

        # Separatory
        'LBRACE', 'RBRACE',
        'LPAREN', 'RPAREN',
        'LBRACKET', 'RBRACKET',
        'SEMI', 'COLON',
        'COMMA', 'DOT',
        'UNDERSCORE',
    ] + list(reserved.values())

    # =========================
    # KOMENTARZE I WHITESPACE
    # =========================

    t_ignore = ' \t\r'

    def t_COMMENT_LINE(self, t):
        r'//[^\n]*'
        pass

    def t_COMMENT_BLOCK(self, t):
        r'/\*[\s\S]*?\*/'
        pass

    def t_newline(self, t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # =========================
    # OPERATORY (kolejność ważna!)
    # =========================

    t_OP_ARROW = r'->'
    t_OP_FAT_ARROW = r'=>'
    t_OP_PATH = r'::'
    t_OP_DOTDOTEQ = r'\.\.='
    t_OP_DOTDOT = r'\.\.'
    t_OP_AND_AND = r'&&'
    t_OP_OR_OR = r'\|\|'
    t_OP_EQ_EQ = r'=='
    t_OP_NE = r'!='
    t_OP_LE = r'<='
    t_OP_GE = r'>='
    t_OP_SHL = r'<<'
    t_OP_SHR = r'>>'
    t_OP_ADD_ASSIGN = r'\+='
    t_OP_SUB_ASSIGN = r'-='
    t_OP_MUL_ASSIGN = r'\*='
    t_OP_DIV_ASSIGN = r'/='
    t_OP_REM_ASSIGN = r'%='

    t_OP_ASSIGN = r'='
    t_OP_LT = r'<'
    t_OP_GT = r'>'
    t_OP_AMP = r'&'
    t_OP_PIPE = r'\|'
    t_OP_STAR = r'\*'
    t_OP_PLUS = r'\+'
    t_OP_MINUS = r'-'
    t_OP_SLASH = r'/'
    t_OP_PERCENT = r'%'
    t_OP_BANG = r'!'
    t_OP_CARET = r'\^'
    t_OP_TILDE = r'~'
    t_OP_AT = r'@'
    t_OP_HASH = r'\#'
    t_OP_QUESTION = r'\?'

    # =========================
    # SEPARATORY
    # =========================

    t_LBRACE = r'\{'
    t_RBRACE = r'\}'
    t_LPAREN = r'\('
    t_RPAREN = r'\)'
    t_LBRACKET = r'\['
    t_RBRACKET = r'\]'
    t_SEMI = r';'
    t_COLON = r':'
    t_COMMA = r','
    t_DOT = r'\.'

    def t_UNDERSCORE(self, t):
        r'_'
        return t

    # =========================
    # LIFETIMES (wyższy priorytet niż CHAR)
    # =========================

    def t_LIFETIME_IDENT(self, t):
        r"'[a-zA-Z_][a-zA-Z0-9_]*"
        return t

    def t_LIFETIME_ANON(self, t):
        r"'_"
        return t

    # =========================
    # LITERAŁY
    # =========================

    def t_LIT_FLOAT(self, t):
        r'[0-9][0-9_]*\.[0-9][0-9_]*(e[+-]?[0-9]+)?(f32|f64)?'
        return t

    def t_LIT_INT_HEX(self, t):
        r'0x[0-9a-fA-F_]+'
        return t

    def t_LIT_INT_BIN(self, t):
        r'0b[01_]+'
        return t

    def t_LIT_INT(self, t):
        r'[0-9][0-9_]*(u8|u16|u32|u64|u128|usize|i8|i16|i32|i64|i128|isize)?'
        return t

    def t_LIT_STR_RAW(self, t):
        r'r\#*".*?"\#*'
        return t

    def t_LIT_STR(self, t):
        r'"([^"\\]|\\.)*"'
        return t

    def t_LIT_BYTE_STR(self, t):
        r'b"([^"\\]|\\.)*"'
        return t

    def t_LIT_BYTE(self, t):
        r"b'([^'\\]|\\.)'"
        return t

    def t_LIT_CHAR(self, t):
        r"'([^'\\]|\\.)'"
        return t

    # =========================
    # IDENTYFIKATORY
    # =========================

    def t_IDENT(self, t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = reserved.get(t.value, 'IDENT')
        return t

    # =========================
    # OBSŁUGA BŁĘDÓW
    # =========================

    def t_error(self, t):
        print(f"Illegal character '{t.value[0]}' at line {t.lineno}")
        t.lexer.skip(1)

    def __init__(self):
        # Build the lexer
        self.lexer = lex.lex(module=self)

    def get_lexer(self):
        return self.lexer
