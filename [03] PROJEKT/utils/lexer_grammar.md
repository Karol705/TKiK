# Tokeny i gramatyka

---

## 1. Tokeny leksera (`lexer.py`)

### 1.1 Słowa kluczowe

Słowa kluczowe są rozpoznawane w regule dla `IDENT` — jeśli dopasowany identyfikator należy do zbioru słów kluczowych, zwracany jest odpowiedni typ tokenu.

| Token    | Wartość w kodzie |
| -------- | ---------------- |
| `LET`    | `let`            |
| `MUT`    | `mut`            |
| `FN`     | `fn`             |
| `RETURN` | `return`         |
| `IF`     | `if`             |
| `ELSE`   | `else`           |
| `WHILE`  | `while`          |
| `LOOP`   | `loop`           |
| `BREAK`  | `break`          |
| `TRUE`   | `true`           |
| `FALSE`  | `false`          |
| `CONST`  | `const`          |
| `STATIC` | `static`         |

```python
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
```

### 1.2 Literały i identyfikatory

| Token      | Opis                                  | Przykład             |
| ---------- | ------------------------------------- | -------------------- |
| `IDENT`    | Identyfikator (zmienna, funkcja, typ) | `x`, `my_var`, `i32` |
| `INTEGER`  | Całkowita liczba dziesiętna           | `42`, `0`, `1_000`   |
| `FLOAT`    | Liczba zmiennoprzecinkowa             | `3.14`, `0.5`        |
| `STRING`   | Łańcuch znaków w cudzysłowie          | `"hello"`            |
| `LIFETIME` | Etykieta czasu życia                  | `'a`, `'static`      |

```python
def t_FLOAT(t):
    r'\d+\.\d+'
    t.value = float(t.value)
    return t

def t_INTEGER(t):
    r'\d[\d_]*'
    t.value = int(t.value.replace('_', ''))
    return t

def t_STRING(t):
    r'"([^"\\]|\\.)*"'
    t.value = t.value[1:-1]
    return t

def t_LIFETIME(t):
    r"'[a-zA-Z_][a-zA-Z0-9_]*"
    return t

def t_IDENT(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    t.type = reserved.get(t.value, 'IDENT')
    return t
```

> **Uwaga:** Kolejność reguł ma znaczenie — `t_FLOAT` musi być zdefiniowany przed `t_INTEGER`.

### 1.3 Operatory

| Token    | Symbol | Token     | Symbol |
| -------- | ------ | --------- | ------ |
| `EQ`     | `==`   | `NEQ`     | `!=`   |
| `LEQ`    | `<=`   | `GEQ`     | `>=`   |
| `LT`     | `<`    | `GT`      | `>`    |
| `OR`     | `\|\|` | `NOT`     | `!`    |
| `AMP`    | `&`    | `PLUS`    | `+`    |
| `MINUS`  | `-`    | `STAR`    | `*`    |
| `SLASH`  | `/`    | `PERCENT` | `%`    |
| `ASSIGN` | `=`    |           |        |

> Tokeny wieloznakowe (`==`, `!=`, `<=`, `>=`, `||`) **muszą** być zdefiniowane jako funkcje lub wymienione przed jednozbiorowymi odpowiednikami, aby PLY dopasował dłuższy wariant.

```python
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
```

### 1.4 Znaki przestankowe

| Token       | Symbol | Token    | Symbol |
| ----------- | ------ | -------- | ------ |
| `LPAREN`    | `(`    | `RPAREN` | `)`    |
| `LBRACE`    | `{`    | `RBRACE` | `}`    |
| `SEMICOLON` | `;`    | `COLON`  | `:`    |
| `COMMA`     | `,`    | `DOT`    | `.`    |
| `ARROW`     | `->`   |          |        |

```python
t_LPAREN      = r'\('
t_RPAREN      = r'\)'
t_LBRACE      = r'\{'
t_RBRACE      = r'\}'
t_SEMICOLON   = r';'
t_COLON       = r':'
t_COMMA       = r','
t_DOT         = r'\.'
t_ARROW       = r'->'
```

### 1.5 Ignorowane znaki i komentarze

```python
# Białe znaki (spacje, tabulacje)
t_ignore = ' \t'

# Nowe linie — zliczamy dla numerów linii
def t_newline(t):
    r'\n+'
    t.lexer.lineno += len(t.value)

# Komentarze jednoliniowe
def t_COMMENT(t):
    r'//[^\n]*'
    pass  # pomijamy, nie zwracamy tokenu

# Obsługa błędów
def t_error(t):
    print(f"Nieznany znak '{t.value[0]}' w linii {t.lineno}")
    t.lexer.skip(1)
```

---

## 2. Gramatyka (`grammar.py`)

Gramatyka opisana jest w notacji BNF, a następnie w postaci reguł PLY (dekoratory `p_*`).
Symbole terminalne pisane są WIELKIMI LITERAMI, nieterminalne — małymi.

### 2.1 Pełna lista tokenów dla PLY

```python
tokens = [
    # Identyfikatory i literały
    'IDENT', 'INTEGER', 'FLOAT', 'STRING', 'LIFETIME',
    # Operatory
    'EQ', 'NEQ', 'LEQ', 'GEQ', 'LT', 'GT',
    'OR', 'NOT', 'AMP',
    'PLUS', 'MINUS', 'STAR', 'SLASH', 'PERCENT',
    'ASSIGN',
    # Znaki przestankowe
    'LPAREN', 'RPAREN', 'LBRACE', 'RBRACE',
    'SEMICOLON', 'COLON', 'COMMA', 'DOT',
    'ARROW',
] + list(reserved.values())
```

---

### 2.2 Program i elementy najwyższego poziomu

```
program     → item*

item        → fn_def
            | const_def
            | static_def
```

Program składa się z listy definicji funkcji. Na tym poziomie nie obsługujemy
modułów, `use`, `struct` ani `impl`.

```python
def p_program(p):
    """program : item_list"""
    p[0] = ('program', p[1])

def p_item_list(p):
    """item_list : item_list item
                 | empty"""
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_item(p):
    """item : fn_def
            | const_def
            | static_def"""
    p[0] = p[1]
```

---

### 2.3 Definicja funkcji

```
fn_def      → 'fn' IDENT '(' param_list ')' return_type block
            | 'fn' IDENT '(' param_list ')' block

return_type → '->' type

param_list  → ε
            | param
            | param_list ',' param

param       → IDENT ':' type
```

```python
def p_fn_def(p):
    """fn_def : FN IDENT LPAREN param_list RPAREN ARROW type block
              | FN IDENT LPAREN param_list RPAREN block"""
    if len(p) == 9:
        p[0] = ('fn_def', p[2], p[4], p[7], p[8])
    else:
        p[0] = ('fn_def', p[2], p[4], None, p[6])

def p_param_list_empty(p):
    """param_list : empty"""
    p[0] = []

def p_param_list_single(p):
    """param_list : param"""
    p[0] = [p[1]]

def p_param_list_multi(p):
    """param_list : param_list COMMA param"""
    p[0] = p[1] + [p[3]]

def p_param(p):
    """param : IDENT COLON type"""
    p[0] = ('param', p[1], p[3])
```

---

### 2.4 Typy

Obsługiwane typy to typy pierwotne, referencje oraz typy nazwane (np. `String`).
Tablice i krotki są poza zakresem projektu.

```
type        → IDENT                     # i32, u64, bool, f64, String, ...
            | '&' type                  # referencja niemutowalna
            | '&' 'mut' type            # referencja mutowalna
            | '&' LIFETIME type         # referencja z czasem życia (rozszerzenie)
            | '&' LIFETIME 'mut' type   # mutowalna referencja z czasem życia
```

```python
def p_type_ident(p):
    """type : IDENT"""
    p[0] = ('type_name', p[1])

def p_type_ref(p):
    """type : AMP type"""
    p[0] = ('ref', False, p[2])

def p_type_mut_ref(p):
    """type : AMP MUT type"""
    p[0] = ('ref', True, p[3])

def p_type_lifetime_ref(p):
    """type : AMP LIFETIME type"""
    p[0] = ('ref_lifetime', p[2], False, p[3])

def p_type_lifetime_mut_ref(p):
    """type : AMP LIFETIME MUT type"""
    p[0] = ('ref_lifetime', p[2], True, p[4])
```

---

### 2.5 Blok i instrukcje

```
block       → '{' stmt_list '}'
            | '{' stmt_list expr '}'    # blok z wyrażeniem końcowym

stmt_list   → ε
            | stmt_list stmt

stmt        → let_stmt
            | expr_stmt
            | return_stmt
            | if_stmt
            | while_stmt
            | loop_stmt
            | break_stmt
            | item
```

```python
def p_block(p):
    """block : LBRACE stmt_list RBRACE
             | LBRACE stmt_list expr RBRACE"""
    if len(p) == 4:
        p[0] = ('block', p[2], None)
    else:
        p[0] = ('block', p[2], p[3])

def p_stmt_list(p):
    """stmt_list : stmt_list stmt
                 | empty"""
    if len(p) == 3:
        p[0] = p[1] + [p[2]]
    else:
        p[0] = []

def p_stmt(p):
    """stmt : let_stmt
            | expr_stmt
            | return_stmt
            | if_stmt
            | while_stmt
            | loop_stmt
            | break_stmt
            | item"""
    p[0] = p[1]
```

#### 2.5.1 Deklaracja zmiennej (`let`)

```
let_stmt    → 'let' opt_mut IDENT opt_type_annotation opt_init ';'

opt_mut     → ε
            | 'mut'

opt_type_annotation
            → ε
            | ':' type

opt_init    → ε
            | '=' expr
```

```python
def p_let_stmt_full(p):
    """let_stmt : LET opt_mut IDENT opt_type_annotation opt_init SEMICOLON"""
    p[0] = ('let', p[2], p[3], p[4], p[5])

def p_opt_mut(p):
    """opt_mut : MUT
               | empty"""
    p[0] = True if p[1] is not None else False

def p_opt_type_annotation(p):
    """opt_type_annotation : COLON type
                           | empty"""
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = None

def p_opt_init(p):
    """opt_init : ASSIGN expr
                | empty"""
    if len(p) == 3:
        p[0] = p[2]
    else:
        p[0] = None
```

##### 2.5.1.1 Definicja `const`

```
const_def   → 'const' IDENT ':' type '=' expr ';'
```

```python
def p_const_def(p):
    """const_def : CONST IDENT COLON type ASSIGN expr SEMICOLON"""
    p[0] = ('const_def', p[2], p[4], p[6])
```

---

##### 2.5.1.2 Definicja `static`

```
static_def  → 'static' opt_mut IDENT ':' type '=' expr ';'
```

```python
def p_static_def(p):
    """static_def : STATIC opt_mut IDENT COLON type ASSIGN expr SEMICOLON"""
    p[0] = ('static_def', p[2], p[3], p[5], p[7])
```

---

#### 2.5.2 Instrukcja wyrażenia

```
expr_stmt   → expr ';'
```

```python
def p_expr_stmt(p):
    """expr_stmt : expr SEMICOLON"""
    p[0] = ('expr_stmt', p[1])
```

#### 2.5.3 Instrukcja `return`

```
return_stmt → 'return' expr ';'
            | 'return' ';'
```

```python
def p_return_stmt(p):
    """return_stmt : RETURN expr SEMICOLON
                   | RETURN SEMICOLON"""
    if len(p) == 4:
        p[0] = ('return', p[2])
    else:
        p[0] = ('return', None)
```

#### 2.5.4 Instrukcja warunkowa `if/else`

```
if_stmt     → 'if' expr block
            | 'if' expr block 'else' block
            | 'if' expr block 'else' if_stmt
```

```python
def p_if_stmt(p):
    """if_stmt : IF expr block
               | IF expr block ELSE block
               | IF expr block ELSE if_stmt"""
    if len(p) == 4:
        p[0] = ('if', p[2], p[3], None)
    else:
        p[0] = ('if', p[2], p[3], p[5])
```

#### 2.5.5 Pętla `while`

```
while_stmt  → 'while' expr block
```

```python
def p_while_stmt(p):
    """while_stmt : WHILE expr block"""
    p[0] = ('while', p[2], p[3])
```

#### 2.5.6 Pętla `loop` i `break`

```
loop_stmt   → 'loop' block

break_stmt  → 'break' ';'
```

```python
def p_loop_stmt(p):
    """loop_stmt : LOOP block"""
    p[0] = ('loop', p[2])

def p_break_stmt(p):
    """break_stmt : BREAK SEMICOLON"""
    p[0] = ('break',)
```

---

### 2.6 Wyrażenia

Hierarchia priorytetów operatorów (od najniższego do najwyższego):

| Poziom | Operator(y)                        | Łączność         |
| ------ | ---------------------------------- | ---------------- |
| 1      | `=`                                | prawostronny     |
| 2      | `\|\|`                             | lewostronny      |
| 3      | `&&`                               | lewostronny      |
| 4      | `==`, `!=`                         | brak (niełączny) |
| 5      | `<`, `>`, `<=`, `>=`               | brak (niełączny) |
| 6      | `+`, `-`                           | lewostronny      |
| 7      | `*`, `/`, `%`                      | lewostronny      |
| 8      | `-` (unarny), `!`, `&`, `&mut`     | prawostronny     |
| 9      | wywołanie funkcji, `.`             | lewostronny      |
| 10     | literały, identyfikatory, `(expr)` | —                |

```
expr            → assign_expr

assign_expr     → IDENT '=' expr
                | or_expr

or_expr         → or_expr '||' and_expr
                | and_expr

and_expr        → and_expr '&&' eq_expr
                | eq_expr

eq_expr         → rel_expr '==' rel_expr
                | rel_expr '!=' rel_expr
                | rel_expr

rel_expr        → add_expr '<' add_expr
                | add_expr '>' add_expr
                | add_expr '<=' add_expr
                | add_expr '>=' add_expr
                | add_expr

add_expr        → add_expr '+' mul_expr
                | add_expr '-' mul_expr
                | mul_expr

mul_expr        → mul_expr '*' unary_expr
                | mul_expr '/' unary_expr
                | mul_expr '%' unary_expr
                | unary_expr

unary_expr      → '-' unary_expr
                | '!' unary_expr
                | '&' unary_expr
                | '&' 'mut' unary_expr
                | primary_expr

primary_expr    → IDENT
                | INTEGER
                | FLOAT
                | STRING
                | TRUE
                | FALSE
                | '(' expr ')'
                | fn_call
                | method_call

fn_call         → IDENT '(' arg_list ')'

method_call     → primary_expr '.' IDENT '(' arg_list ')'

arg_list        → ε
                | expr
                | arg_list ',' expr
```

```python
# Deklaracja priorytetów dla PLY (rozwiązuje konflikty shift/reduce)
precedence = (
    ('right',  'ASSIGN'),
    ('left',   'OR'),
    ('left',   'AMP'), # Priorytet dla AND (&&)
    ('nonassoc', 'EQ', 'NEQ'),
    ('nonassoc', 'LT', 'GT', 'LEQ', 'GEQ'),
    ('left',   'PLUS', 'MINUS'),
    ('left',   'STAR', 'SLASH', 'PERCENT'),
    ('right',  'UMINUS', 'NOT', 'UREF', 'UMUTREF'),
    ('left',   'DOT', 'LPAREN'),
)

def p_expr_assign(p):
    """expr : IDENT ASSIGN expr"""
    p[0] = ('assign', p[1], p[3])

def p_expr_binop(p):
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


def p_expr_unary_minus(p):
    """expr : MINUS expr %prec UMINUS"""
    p[0] = ('unary', '-', p[2])

def p_expr_unary_not(p):
    """expr : NOT expr"""
    p[0] = ('unary', '!', p[2])

def p_expr_ref(p):
    """expr : AMP expr %prec UREF"""
    p[0] = ('borrow', False, p[2])

def p_expr_mut_ref(p):
    """expr : AMP MUT expr %prec UMUTREF"""
    p[0] = ('borrow', True, p[3])

def p_expr_atom(p):
    """expr : INTEGER
            | FLOAT
            | STRING
            | TRUE
            | FALSE"""
    p[0] = ('literal', p[1])

def p_expr_ident(p):
    """expr : IDENT"""
    p[0] = ('ident', p[1])

def p_expr_paren(p):
    """expr : LPAREN expr RPAREN"""
    p[0] = p[2]

def p_expr_fn_call(p):
    """expr : IDENT LPAREN arg_list RPAREN"""
    p[0] = ('call', p[1], p[3])

def p_expr_method_call(p):
    """expr : expr DOT IDENT LPAREN arg_list RPAREN"""
    p[0] = ('method_call', p[1], p[3], p[5])

def p_arg_list_empty(p):
    """arg_list : empty"""
    p[0] = []

def p_arg_list_single(p):
    """arg_list : expr"""
    p[0] = [p[1]]

def p_arg_list_multi(p):
    """arg_list : arg_list COMMA expr"""
    p[0] = p[1] + [p[3]]
```

---

### 2.7 Reguła pomocnicza `empty`

```python
def p_empty(p):
    """empty :"""
    p[0] = None
```

### 2.8 Obsługa błędów parsera

```python
def p_error(p):
    if p:
        print(f"Błąd składni: nieoczekiwany token '{p.value}' ({p.type}) w linii {p.lineno}")
    else:
        print("Błąd składni: nieoczekiwany koniec pliku")
```

---

## 3. Zakres obsługiwanego podzbioru języka

### ✅ Obsługiwane konstrukcje

| Kategoria               | Przykład                                 |
| ----------------------- | ---------------------------------------- |
| Deklaracja zmiennej     | `let x = 5;`                             |
| Deklaracja mutowalna    | `let mut y = 10;`                        |
| Adnotacja typowa        | `let x: i32 = 5;`                        |
| Referencja niemutowalna | `let r = &x;`                            |
| Referencja mutowalna    | `let r = &mut x;`                        |
| Przeniesienie własności | `let b = a;` (gdzie `a` nie jest `Copy`) |
| Definicja funkcji       | `fn foo(x: i32) -> i32 { ... }`          |
| Wywołanie funkcji       | `foo(x)`                                 |
| Instrukcja warunkowa    | `if cond { ... } else { ... }`           |
| Pętla `while`           | `while cond { ... }`                     |
| Pętla `loop` / `break`  | `loop { break; }`                        |
| Operatory arytmetyczne  | `+`, `-`, `*`, `/`, `%`                  |
| Operatory porównania    | `==`, `!=`, `<`, `>`, `<=`, `>=`         |
| Operatory logiczne      | `&&`, `\|\|`, `!`                        |
| Literały czasu życia    | `'a` w typach referencji                 |
| Wywołanie metody        | `v.len()`                                |

### ❌ Celowo pominięte konstrukcje

| Kategoria                         | Uzasadnienie pominięcia                            |
| --------------------------------- | -------------------------------------------------- |
| `struct`, `enum`, `impl`          | Znacząco zwiększa złożoność analizatora            |
| `match` / dopasowanie wzorców     | Złożona semantyka, duży nakład pracy               |
| Domknięcia (`\|x\| x + 1`)        | Wymagają obsługi środowisk i przechwytywania       |
| Tablice `[T; N]` i wycinki `&[T]` | Poza zakresem analizy ownership                    |
| Generyki (`fn foo<T>`)            | Wymagają systemu typów                             |
| Cechy (`trait`, `impl Trait`)     | Poza zakresem projektu                             |
| `use`, `mod`, wiele plików        | Niezbędne tylko przy dużych projektach             |
| `for` (iteratory)                 | Wymaga rozstrzygnięcia pożyczania iteratora        |
| Operatory przypisania złożonego   | `+=`, `-=` itd. — łatwe rozszerzenie w razie czasu |

---

## 4. Przykładowe wejście i oczekiwane AST

### Wejście

```rust
fn main() {
    let x = 5;
    let mut y = x;
    let r = &y;
}
```

### Oczekiwane AST (uproszczone)

```
('program', [
  ('fn_def', 'main', [], None,
    ('block', [
      ('let', False, 'x', None, ('literal', 5)),
      ('let', True,  'y', None, ('ident', 'x')),
      ('let', False, 'r', None, ('borrow', False, ('ident', 'y'))),
    ], None)
  )
])
```
