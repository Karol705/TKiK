import ply.lex as lex

class Lexer:
    
    reserved = {
        'let':    'LET',
        'mut':    'MUT',
        'fn':     'FN',
        'return': 'RETURN',
        'if':     'IF',
        'else':   'ELSE',
        'while':  'WHILE',
        'loop':   'LOOP',
        'break':  'BREAK',
        'true':   'TRUE',
        'false':  'FALSE',
        'const':  'CONST',
        'static': 'STATIC',
    }
    
    tokens = (
        list({
            'IDENT', 'INTEGER', 'FLOAT', 'STRING', 'LIFETIME',
            'EQ', 'NEQ', 'LEQ', 'GEQ', 'LT', 'GT', 'OR', 'NOT', 'AMP',
            'PLUS', 'MINUS', 'STAR', 'SLASH', 'PERCENT',
            'ASSIGN',
            'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
            'SEMICOLON', 'COLON', 'COMMA', 'DOT',
            'ARROW',
        }) + list(reserved.values())
    )
        
    
    
    # Literały i identyfikatory
    def t_FLOAT(self,t):
        r'\d+\.\d+'
        t.value = float(t.value)
        return t

    def t_INTEGER(self,t):
        r'\d[\d_]*'
        t.value = int(t.value.replace('_', ''))
        return t

    def t_STRING(self,t):
        r'"([^"\\]|\\.)*"'
        t.value = t.value[1:-1]
        return t

    def t_LIFETIME(self,t):
        r"'[a-zA-Z_][a-zA-Z0-9_]*"
        return t

    def t_IDENT(self,t):
        r'[a-zA-Z_][a-zA-Z0-9_]*'
        t.type = self.reserved.get(t.value, 'IDENT')
        return t
    
    # Operatory wieloznakowe — wymagają funkcji lub jawnej kolejności
    t_EQ      = r'=='
    t_NEQ     = r'!='
    t_LEQ     = r'<='
    t_GEQ     = r'>='
    t_OR      = r'\|\|'

    # Operatory jednoznakowe
    t_LT      = r'<'
    t_GT      = r'>'
    t_NOT     = r'!'
    t_AMP     = r'&'
    t_PLUS    = r'\+'
    t_MINUS   = r'-'
    t_STAR    = r'\*'
    t_SLASH   = r'/'
    t_PERCENT = r'%'
    t_ASSIGN  = r'='
    
    # Znaki przestankowe
    t_LPAREN      = r'\('
    t_RPAREN      = r'\)'
    t_LBRACE      = r'\{'
    t_RBRACE      = r'\}'
    t_SEMICOLON   = r';'
    t_COLON       = r':'
    t_COMMA       = r','
    t_DOT         = r'\.'
    t_ARROW       = r'->'

    # Białe znaki (spacje, tabulacje)
    t_ignore = ' \t'

    # Nowe linie — zliczamy dla numerów linii
    def t_newline(self,t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    # Komentarze jednoliniowe
    def t_COMMENT(self,t):
        r'//[^\n]*'
        pass  # pomijamy, nie zwracamy tokenu

    # Obsługa błędów
    def t_error(self,t):
        print(f"Nieznany znak '{t.value[0]}' w linii {t.lineno}")
        t.lexer.skip(1)

    def __init__(self):
        # Build the lexer
        self.lexer = lex.lex(module=self)

    def get_lexer(self):
        return self.lexer
