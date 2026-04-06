# 📌 Opis projektu

Projekt ma na celu stworzenie narzędzia analityczno-wizualizacyjnego, które przyjmuje kod napisany w języku Rust jako wejście, a następnie przedstawia szczegółowy przebieg stanów zmiennych w trakcie działania programu. Głównym założeniem jest odwzorowanie mechanizmów zarządzania pamięcią charakterystycznych dla Rusta — takich jak własność (ownership), pożyczanie (borrowing), mutowalność czy czas życia zmiennych — w sposób czytelny i zrozumiały.

Program analizuje kod statycznie (bez jego rzeczywistego uruchamiania), budując wewnętrzną reprezentację programu i śledząc zmiany stanów zmiennych w kolejnych krokach wykonania. Wynikiem działania jest uporządkowana sekwencja stanów (tzw. timeline), która pokazuje, jak zmieniają się właściwości każdej zmiennej w czasie — np. kiedy następuje przeniesienie własności, utworzenie referencji czy zakończenie czasu życia.

---

## ⚙️ Podstawowa funkcjonalność

- analiza kodu Rust (wybrany podzbiór języka),
- śledzenie stanów zmiennych w czasie,
- odwzorowanie kluczowych aspektów:
    - własność (ownership),
    - lokalizacja w pamięci (stos/ster­ta),
    - mutowalność,
    - inicjalizacja,
    - pożyczanie i referencje,
    - czas życia (lifetime),

- generowanie sekwencji stanów (timeline),
- prezentacja wyników w formie tekstowej lub graficznej (np. graf zależności między zmiennymi).

---

## 🚀 Możliwe rozszerzenia

Projekt może zostać rozbudowany o bardziej zaawansowane funkcjonalności, takie jak:

- analiza współbieżności:
    - śledzenie dostępu do zmiennych w wielu wątkach,
    - wykrywanie potencjalnych konfliktów (data races),
    - wizualizacja synchronizacji (Send/Sync),

- zaawansowana analiza borrow checkera:
    - wykrywanie błędów związanych z pożyczaniem,
    - wizualizacja konfliktów mutowalnych i niemutowalnych referencji,

- obsługa bardziej złożonych konstrukcji języka Rust:
    - funkcje i przekazywanie własności między nimi,
    - struktury danych (np. `Vec`, `Box`),
    - zarządzanie pamięcią na stercie,

- wizualizacja dynamiczna:
    - animacja zmian stanów w czasie,
    - interaktywne przeglądanie kroków programu,

- analiza przepływu sterowania:
    - obsługa instrukcji warunkowych i pętli,
    - rozgałęzienia wykonania programu,

---

## 🔤 Tokeny

Poniżej zdefiniowany jest pełny zestaw tokenów dla analizowanego podzbioru języka Rust. Tokeny pogrupowane są według kategorii. Lekser powinien je rozpoznawać w podanej kolejności priorytetów (tokeny wieloznakowe przed jednoznakowymi, słowa kluczowe przed identyfikatorami).

> **Notacja:** Wyrażenia regularne zapisano w składni PCRE. Tokeny oznaczone `[R]` są uwzględnione z myślą o rozszerzeniach, ale wymagają minimalnego nakładu implementacyjnego już na tym etapie — ich pominięcie teraz utrudniłoby późniejsze dodanie.

---

### Komentarze (pomijane przez lekser)

| Token           | Wyrażenie regularne / opis          |
| --------------- | ----------------------------------- |
| `COMMENT_LINE`  | `//[^\n]*`                          |
| `COMMENT_BLOCK` | `/\*[\s\S]*?\*/` (nie zagnieżdżone) |
| `WHITESPACE`    | `[ \t\r\n]+`                        |

---

### Słowa kluczowe

Słowa kluczowe mają wyższy priorytet niż identyfikatory — lekser rozpoznaje je przed próbą dopasowania `IDENT`.

| Token         | Wartość    | Uwagi                                        |
| ------------- | ---------- | -------------------------------------------- |
| `KW_LET`      | `let`      |                                              |
| `KW_MUT`      | `mut`      |                                              |
| `KW_FN`       | `fn`       |                                              |
| `KW_RETURN`   | `return`   |                                              |
| `KW_IF`       | `if`       |                                              |
| `KW_ELSE`     | `else`     |                                              |
| `KW_WHILE`    | `while`    |                                              |
| `KW_LOOP`     | `loop`     |                                              |
| `KW_FOR`      | `for`      |                                              |
| `KW_IN`       | `in`       |                                              |
| `KW_BREAK`    | `break`    |                                              |
| `KW_CONTINUE` | `continue` |                                              |
| `KW_STRUCT`   | `struct`   |                                              |
| `KW_IMPL`     | `impl`     |                                              |
| `KW_SELF`     | `self`     | Wartość `self` (małe litery)                 |
| `KW_PUB`      | `pub`      |                                              |
| `KW_USE`      | `use`      |                                              |
| `KW_MOD`      | `mod`      | `[R]` potrzebne przy modułach                |
| `KW_MOVE`     | `move`     | Zamknięcia z przeniesieniem własności        |
| `KW_REF`      | `ref`      | Wiązanie przez referencję w wzorcach         |
| `KW_MATCH`    | `match`    | `[R]` szkielet już teraz; rozbudowa o wzorce |
| `KW_AS`       | `as`       | `[R]` rzutowanie typów                       |
| `KW_CONST`    | `const`    | `[R]` stałe i surowe wskaźniki               |
| `KW_STATIC`   | `static`   | `[R]` czas życia `'static`                   |
| `KW_TYPE`     | `type`     | `[R]` aliasy typów                           |
| `KW_UNSAFE`   | `unsafe`   | `[R]` bloki niebezpieczne                    |
| `KW_EXTERN`   | `extern`   | `[R]` interfejsy FFI                         |
| `KW_TRUE`     | `true`     | Literał logiczny                             |
| `KW_FALSE`    | `false`    | Literał logiczny                             |

---

### Identyfikatory i czasy życia

| Token            | Wyrażenie regularne       | Uwagi                                                   |
| ---------------- | ------------------------- | ------------------------------------------------------- |
| `LIFETIME_IDENT` | `'[a-zA-Z_][a-zA-Z0-9_]*` | Np. `'a`, `'static`, `'_`. Wyższy priorytet niż `CHAR`. |
| `LIFETIME_ANON`  | `'_`                      | Anonimowy czas życia; można scalić z `LIFETIME_IDENT`.  |
| `IDENT`          | `[a-zA-Z_][a-zA-Z0-9_]*`  | Identyfikator (po wykluczeniu słów kluczowych).         |

> **Uwaga dot. rozszerzeń:** Tokeny `LIFETIME_IDENT` i `LIFETIME_ANON` są niezbędne już w podstawowej wersji — analiza własności i pożyczania bez adnotacji czasu życia jest niemożliwa dla funkcji z wieloma referencjami. Ich dodanie post factum wymagałoby przebudowy zarówno leksera, jak i parsera typów.

---

### Literały

| Token          | Wyrażenie regularne                                                                         | Uwagi                                                    |
| -------------- | ------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| `LIT_INT`      | `[0-9][0-9_]*(u8\|u16\|u32\|u64\|u128\|usize\|i8\|i16\|i32\|i64\|i128\|isize)?`             | Sufiks opcjonalny.                                       |
| `LIT_INT_HEX`  | `0x[0-9a-fA-F_]+(sufiks)?`                                                                  | Zapis szesnastkowy.                                      |
| `LIT_INT_BIN`  | `0b[01_]+(sufiks)?`                                                                         | Zapis binarny.                                           |
| `LIT_FLOAT`    | `[0-9][0-9_]*\.[0-9][0-9_]*(e[+-]?[0-9]+)?(f32\|f64)?`                                      |                                                          |
| `LIT_STR`      | `"([^"\\]                                                                       \| \\.)\*"` | Literał łańcuchowy.                                      |
| `LIT_STR_RAW`  | `r#*"[\s\S]*?"#*`                                                                           | Surowy literał łańcuchowy.                               |
| `LIT_CHAR`     | `'([^'\\]                                                                       \| \\.)'`   | Literał znakowy (niższy priorytet niż `LIFETIME_IDENT`). |
| `LIT_BYTE`     | `b'([^'\\]                                                                      \| \\.)'`   | `[R]`                                                    |
| `LIT_BYTE_STR` | `b"([^"\\]                                                                      \| \\.)\*"` | `[R]`                                                    |

---

### Operatory

Tokeny wieloznakowe rozpoznawane przed jednoznakowymi.

| Token           | Wartość | Kategoria                          |
| --------------- | ------- | ---------------------------------- |
| `OP_ARROW`      | `->`    | Typ zwracany funkcji               |
| `OP_FAT_ARROW`  | `=>`    | Ramię `match` `[R]`                |
| `OP_PATH`       | `::`    | Separator ścieżki                  |
| `OP_DOTDOT`     | `..`    | Zakres / reszta struktury          |
| `OP_DOTDOTEQ`   | `..=`   | Zakres domknięty `[R]`             |
| `OP_AND_AND`    | `&&`    | Logiczne AND                       |
| `OP_OR_OR`      | `\|\|`  | Logiczne OR                        |
| `OP_EQ_EQ`      | `==`    | Równość                            |
| `OP_NE`         | `!=`    | Nierówność                         |
| `OP_LE`         | `<=`    | Mniejsze lub równe                 |
| `OP_GE`         | `>=`    | Większe lub równe                  |
| `OP_SHL`        | `<<`    | Przesunięcie w lewo `[R]`          |
| `OP_SHR`        | `>>`    | Przesunięcie w prawo `[R]`         |
| `OP_ADD_ASSIGN` | `+=`    | Dodawanie z przypisaniem           |
| `OP_SUB_ASSIGN` | `-=`    | Odejmowanie z przypisaniem         |
| `OP_MUL_ASSIGN` | `*=`    | Mnożenie z przypisaniem `[R]`      |
| `OP_DIV_ASSIGN` | `/=`    | Dzielenie z przypisaniem `[R]`     |
| `OP_REM_ASSIGN` | `%=`    | Reszta z przypisaniem `[R]`        |
| `OP_ASSIGN`     | `=`     | Przypisanie                        |
| `OP_LT`         | `<`     | Mniejsze niż / otwierający generic |
| `OP_GT`         | `>`     | Większe niż / zamykający generic   |
| `OP_AMP`        | `&`     | Referencja / AND bitowe            |
| `OP_PIPE`       | `\|`    | Wzorzec OR / OR bitowe `[R]`       |
| `OP_STAR`       | `*`     | Wyłuskanie / mnożenie              |
| `OP_PLUS`       | `+`     | Dodawanie / ograniczenie cechy     |
| `OP_MINUS`      | `-`     | Odejmowanie / negacja              |
| `OP_SLASH`      | `/`     | Dzielenie                          |
| `OP_PERCENT`    | `%`     | Reszta `[R]`                       |
| `OP_BANG`       | `!`     | Negacja logiczna / makro           |
| `OP_CARET`      | `^`     | XOR bitowy `[R]`                   |
| `OP_TILDE`      | `~`     | Zarezerwowane                      |
| `OP_AT`         | `@`     | Wiązanie wzorca `[R]`              |
| `OP_HASH`       | `#`     | Atrybuty `[R]`                     |
| `OP_QUESTION`   | `?`     | Propagacja błędu `[R]`             |

---

### Separatory

| Token        | Wartość | Uwagi                                             |
| ------------ | ------- | ------------------------------------------------- |
| `LBRACE`     | `{`     | Otwarcie bloku / ciała struktury                  |
| `RBRACE`     | `}`     | Zamknięcie bloku                                  |
| `LPAREN`     | `(`     | Otwarcie listy parametrów / wyrażenia             |
| `RPAREN`     | `)`     | Zamknięcie                                        |
| `LBRACKET`   | `[`     | Otwarcie indeksu / tablicy                        |
| `RBRACKET`   | `]`     | Zamknięcie                                        |
| `SEMI`       | `;`     | Koniec instrukcji                                 |
| `COLON`      | `:`     | Adnotacja typu / etykieta                         |
| `COMMA`      | `,`     | Separator                                         |
| `DOT`        | `.`     | Dostęp do pola / metody                           |
| `UNDERSCORE` | `_`     | Wzorzec „ignoruj" (jako token odrębny od `IDENT`) |

---

## 📐 Gramatyka

Gramatyka opisana jest w notacji EBNF:

- `A ::= B C` — konkatenacja,
- `A | B` — alternatywa,
- `A?` — opcjonalnie (0 lub 1),
- `A*` — zero lub więcej,
- `A+` — jedno lub więcej,
- `( A )` — grupowanie,
- `"tekst"` — literał terminalny.

Terminale pisane `WIELKIMI_LITERAMI` odpowiadają tokenom z sekcji powyżej. Dla czytelności niektóre często powtarzające się grupy tokenów są skrótowo opisane komentarzem.

---

### Program i elementy najwyższego poziomu

```ebnf
program         ::= item*

item            ::= fn_def
                  | struct_def
                  | impl_block
                  | use_decl
                  | type_alias        (* [R] *)
                  | const_def         (* [R] *)
                  | mod_block         (* [R] *)
                  | attr item         (* [R] atrybuty #[...] *)

visibility      ::= KW_PUB ( "(" KW_SELF ")" | "(" "super" ")" )?
                  | (* puste — prywatny *)

attr            ::= OP_HASH LBRACKET attr_body RBRACKET  (* [R] *)
attr_body       ::= IDENT ( LPAREN attr_args RPAREN )?
attr_args       ::= (* dowolne tokeny do pasującego ] *)
```

---

### Definicja funkcji

```ebnf
fn_def          ::= visibility? KW_FN IDENT generic_params? LPAREN param_list? RPAREN
                    return_type? where_clause? block

param_list      ::= param ( COMMA param )* COMMA?

param           ::= KW_SELF
                  | ( OP_AMP lifetime? KW_MUT? ) KW_SELF
                  | pattern COLON type

return_type     ::= OP_ARROW type

generic_params  ::= OP_LT generic_param ( COMMA generic_param )* COMMA? OP_GT

generic_param   ::= LIFETIME_IDENT ( COLON lifetime_bounds )?
                  | IDENT ( COLON type_bounds )?   (* [R] granice cech *)

lifetime_bounds ::= LIFETIME_IDENT ( OP_PLUS LIFETIME_IDENT )*

type_bounds     ::= type_bound ( OP_PLUS type_bound )*   (* [R] *)
type_bound      ::= LIFETIME_IDENT | path_type           (* [R] *)

where_clause    ::= "where" where_pred ( COMMA where_pred )* COMMA?  (* [R] *)
where_pred      ::= lifetime COLON lifetime_bounds
                  | type COLON type_bounds              (* [R] *)
```

> **Uzasadnienie wczesnego włączenia generic_params i lifetime:** Analiza pożyczania dla funkcji przyjmujących wiele referencji jest niemożliwa bez rozróżniania czasów życia. Próba dodania tego mechanizmu po zaprojektowaniu AST wymagałaby istotnych zmian w węzłach `FnDef`, `Type` i `Expr`. Koszt uwzględnienia tych tokenów i reguł gramatycznych już teraz jest niski.

---

### Definicja struktury

```ebnf
struct_def      ::= visibility? KW_STRUCT IDENT generic_params? where_clause?
                    ( struct_body | tuple_body SEMI | SEMI )

struct_body     ::= LBRACE ( struct_field ( COMMA struct_field )* COMMA? )? RBRACE

struct_field    ::= visibility? IDENT COLON type

tuple_body      ::= LPAREN ( visibility? type ( COMMA visibility? type )* COMMA? )? RPAREN
```

---

### Blok implementacji

```ebnf
impl_block      ::= KW_IMPL generic_params? type where_clause? LBRACE impl_item* RBRACE

impl_item       ::= fn_def
                  | type_alias   (* [R] typy skojarzone *)
                  | attr impl_item
```

---

### Deklaracja użycia

```ebnf
use_decl        ::= visibility? KW_USE use_tree SEMI

use_tree        ::= path ( OP_PATH LBRACE use_tree ( COMMA use_tree )* COMMA? RBRACE
                          | OP_PATH OP_STAR
                          | (* puste — import ścieżki *)
                          )
                  | LBRACE use_tree ( COMMA use_tree )* COMMA? RBRACE

path            ::= IDENT ( OP_PATH IDENT )*
```

---

### Definicje dodatkowe `[R]`

```ebnf
type_alias      ::= visibility? KW_TYPE IDENT generic_params? OP_ASSIGN type SEMI

const_def       ::= visibility? KW_CONST IDENT COLON type OP_ASSIGN expr SEMI

mod_block       ::= visibility? KW_MOD IDENT ( LBRACE item* RBRACE | SEMI )
```

---

### Blok i instrukcje

```ebnf
block           ::= LBRACE stmt* expr? RBRACE

stmt            ::= let_stmt
                  | expr_stmt
                  | return_stmt
                  | break_stmt
                  | continue_stmt
                  | item          (* definicja lokalna [R] *)

let_stmt        ::= KW_LET KW_MUT? pattern ( COLON type )? ( OP_ASSIGN expr )? SEMI

expr_stmt       ::= expr SEMI

return_stmt     ::= KW_RETURN expr? SEMI

break_stmt      ::= KW_BREAK LIFETIME_IDENT? expr? SEMI

continue_stmt   ::= KW_CONTINUE LIFETIME_IDENT? SEMI
```

---

### Wyrażenia

Wyrażenia zorganizowane są według priorytetów, od najniższego do najwyższego. Każdy poziom deleguje do następnego.

```ebnf
expr            ::= assign_expr

(* Priorytet 1 — przypisania (prawostronne) *)
assign_expr     ::= range_expr ( assign_op assign_expr )?

assign_op       ::= OP_ASSIGN
                  | OP_ADD_ASSIGN | OP_SUB_ASSIGN
                  | OP_MUL_ASSIGN | OP_DIV_ASSIGN | OP_REM_ASSIGN  (* [R] *)

(* Priorytet 2 — zakresy [R] *)
range_expr      ::= or_expr ( ( OP_DOTDOT | OP_DOTDOTEQ ) or_expr? )?

(* Priorytet 3 — logiczne OR *)
or_expr         ::= and_expr ( OP_OR_OR and_expr )*

(* Priorytet 4 — logiczne AND *)
and_expr        ::= cmp_expr ( OP_AND_AND cmp_expr )*

(* Priorytet 5 — porównania *)
cmp_expr        ::= add_expr ( cmp_op add_expr )*

cmp_op          ::= OP_EQ_EQ | OP_NE | OP_LT | OP_GT | OP_LE | OP_GE

(* Priorytet 6 — dodawanie i odejmowanie *)
add_expr        ::= mul_expr ( ( OP_PLUS | OP_MINUS ) mul_expr )*

(* Priorytet 7 — mnożenie, dzielenie, reszta *)
mul_expr        ::= cast_expr ( ( OP_STAR | OP_SLASH | OP_PERCENT ) cast_expr )*

(* Priorytet 8 — rzutowanie [R] *)
cast_expr       ::= unary_expr ( KW_AS type )*

(* Priorytet 9 — operatory unarne *)
unary_expr      ::= OP_MINUS unary_expr
                  | OP_BANG  unary_expr
                  | OP_STAR  unary_expr          (* wyłuskanie *)
                  | borrow_expr
                  | postfix_expr

borrow_expr     ::= OP_AMP lifetime? KW_MUT? unary_expr

(* Priorytet 10 — wyrażenia przyrostkowe *)
postfix_expr    ::= primary_expr postfix_op*

postfix_op      ::= DOT IDENT                                (* dostęp do pola *)
                  | DOT IDENT generic_args? LPAREN arg_list? RPAREN  (* wywołanie metody *)
                  | LBRACKET expr RBRACKET                   (* indeksowanie *)
                  | LPAREN arg_list? RPAREN                  (* wywołanie funkcji *)
                  | OP_QUESTION                              (* propagacja błędu [R] *)

arg_list        ::= expr ( COMMA expr )* COMMA?
```

---

### Wyrażenia podstawowe

```ebnf
primary_expr    ::= literal
                  | IDENT
                  | path_expr
                  | block
                  | if_expr
                  | while_expr
                  | loop_expr
                  | for_expr
                  | match_expr
                  | struct_literal
                  | closure_expr
                  | LPAREN expr RPAREN

(* Ścieżka z opcjonalnymi argumentami generycznymi *)
path_expr       ::= IDENT ( OP_PATH IDENT )* ( OP_PATH generic_args )?

generic_args    ::= OP_LT generic_arg ( COMMA generic_arg )* COMMA? OP_GT

generic_arg     ::= lifetime
                  | type
                  | expr             (* stałe generyczne [R] *)

(* Wyrażenie if / if-else *)
if_expr         ::= KW_IF expr block ( KW_ELSE ( if_expr | block ) )?

(* Pętle *)
while_expr      ::= ( LIFETIME_IDENT COLON )? KW_WHILE expr block

loop_expr       ::= ( LIFETIME_IDENT COLON )? KW_LOOP block

for_expr        ::= ( LIFETIME_IDENT COLON )? KW_FOR pattern KW_IN expr block

(* Wyrażenie match — szkielet wspierający rozszerzenia *)
match_expr      ::= KW_MATCH expr LBRACE match_arm* RBRACE

match_arm       ::= attr* pattern ( KW_IF expr )? OP_FAT_ARROW ( expr COMMA | block )

(* Literał struktury *)
struct_literal  ::= path_expr LBRACE struct_field_init* RBRACE

struct_field_init ::= IDENT COLON expr COMMA?
                    | IDENT COMMA?           (* inicjalizacja skrócona *)
                    | OP_DOTDOT expr         (* aktualizacja pozostałych pól *)

(* Domknięcie *)
closure_expr    ::= KW_MOVE? OP_PIPE closure_param_list? OP_PIPE
                    ( expr | block )

closure_param_list ::= closure_param ( COMMA closure_param )* COMMA?

closure_param   ::= pattern ( COLON type )?
```

> **Uzasadnienie wczesnego włączenia `match` i domknięć:** Szkielet `match_expr` z jednym poziomem wzorców (patrz sekcja poniżej) można rozbudować o złożone wzorce bez zmiany gramatyki – wystarczy rozszerzyć regułę `pattern`. Domknięcia z `move` są kluczowe dla analizy własności (przeniesienie przechwyconych zmiennych) i trudno je dodać bez modyfikacji węzłów AST reprezentujących wyrażenia.

---

### Wzorce

```ebnf
pattern         ::= UNDERSCORE
                  | literal
                  | KW_TRUE | KW_FALSE
                  | KW_REF KW_MUT? IDENT ( OP_AMP pattern )?
                  | KW_MUT? IDENT ( OP_AMP pattern )?
                  | OP_AMP KW_MUT? pattern                      (* wzorzec referencji *)
                  | LPAREN pattern_tuple RPAREN                  (* krotka *)
                  | path_pattern                                 (* enum / stała *)
                  | struct_pattern                               (* struktura *)
                  | range_pattern                               (* [R] zakres *)
                  | OP_OR? pattern ( OP_PIPE pattern )+          (* [R] OR wzorców *)

path_pattern    ::= path_expr ( LPAREN pattern_tuple? RPAREN
                              | LBRACE struct_pat_fields? RBRACE )?

pattern_tuple   ::= pattern ( COMMA pattern )* ( COMMA OP_DOTDOT )?
                  | OP_DOTDOT

struct_pattern  ::= path_expr LBRACE struct_pat_fields? RBRACE

struct_pat_fields ::= struct_pat_field ( COMMA struct_pat_field )* ( COMMA OP_DOTDOT )?
                    | OP_DOTDOT

struct_pat_field  ::= IDENT COLON pattern
                    | KW_REF? KW_MUT? IDENT

range_pattern   ::= literal OP_DOTDOTEQ literal   (* [R] *)
```

---

### Typy

```ebnf
type            ::= ref_type
                  | ptr_type
                  | slice_type
                  | array_type
                  | tuple_type
                  | fn_ptr_type      (* [R] *)
                  | never_type       (* [R] *)
                  | path_type

(* Referencja: &T, &mut T, &'a T, &'a mut T *)
ref_type        ::= OP_AMP lifetime? KW_MUT? type

(* Surowy wskaźnik [R] *)
ptr_type        ::= OP_STAR ( KW_CONST | KW_MUT ) type

(* Wycinek: [T] *)
slice_type      ::= LBRACKET type RBRACKET

(* Tablica: [T; N] *)
array_type      ::= LBRACKET type SEMI expr RBRACKET

(* Krotka: (T, U) *)
tuple_type      ::= LPAREN ( type ( COMMA type )* COMMA? )? RPAREN

(* Wskaźnik na funkcję [R] *)
fn_ptr_type     ::= KW_FN LPAREN ( type ( COMMA type )* COMMA? )? RPAREN return_type?

(* Typ dywergentny [R] *)
never_type      ::= OP_BANG

(* Ścieżka typów: T, A::B, Vec<T>, Option<&'a T> *)
path_type       ::= IDENT ( OP_PATH IDENT )* ( OP_PATH? generic_args )?
```

> **Wbudowane typy generyczne** (`Vec<T>`, `Box<T>`, `Option<T>`, `Result<T, E>`, `String`, `str`) traktowane są przez parser jako zwykłe `path_type`. Ich specjalna semantyka (alokacja na stercie, opcjonalność) jest obsługiwana na etapie analizy semantycznej, a nie gramatyki — co upraszcza rozbudowę o nowe typy biblioteczne.

---

### Literały (reguły gramatyczne)

```ebnf
literal         ::= LIT_INT
                  | LIT_INT_HEX
                  | LIT_INT_BIN
                  | LIT_FLOAT
                  | LIT_STR
                  | LIT_STR_RAW
                  | LIT_CHAR
                  | KW_TRUE
                  | KW_FALSE
```

---

## 📊 Podsumowanie tokenów `[R]`

Poniżej zebrano tokeny i reguły oznaczone `[R]` wraz z uzasadnieniem decyzji o ich wczesnym lub późnym włączeniu:

| Element                   | Decyzja     | Uzasadnienie                                                                   |
| ------------------------- | ----------- | ------------------------------------------------------------------------------ |
| `LIFETIME_IDENT`          | **Teraz**   | Fundamentalny dla analizy pożyczania; retrofit wymaga przebudowy AST.          |
| `generic_params`          | **Teraz**   | Funkcje z `<'a>` są powszechne; parsowanie bez tego jest niekompletne.         |
| `KW_MATCH` + `match_expr` | **Teraz**   | Szkielet z prostymi wzorcami; rozbudowa wzorców nie wymaga zmiany gramatyki.   |
| `closure_expr`            | **Teraz**   | `move` jest kluczowe dla własności; dodanie later wymaga zmian w węzłach AST.  |
| `OP_QUESTION`             | **Teraz**   | Token tani; semantyka propagacji błędu może być dodana później.                |
| `range_expr`              | **Teraz**   | `for x in 0..n` jest powszechnym wzorcem; brak wymaga specjalnego traktowania. |
| Atrybuty `#[...]`         | **Teraz**   | Token tani (`OP_HASH`); pełna analiza atrybutów może być odłożona.             |
| `ptr_type` (`*const`)     | **Później** | Wymagałby analizy niebezpiecznej pamięci; duży nakład semantyczny.             |
| `fn_ptr_type`             | **Później** | Skomplikowana semantyka własności; niska częstość w analizowanym podzbiorze.   |
| `async`/`await`           | **Później** | Wymagają modelu współbieżności; zupełnie oddzielna ścieżka rozszerzenia.       |
| Makra (`vec![]`)          | **Później** | Wymagają ekspansji makr; można wstępnie parsować jako `path OP_BANG (...)`.    |
| Cechy (`trait`, `dyn`)    | **Później** | Duży zakres; gramatyka `type_bounds` przygotowuje grunt pod to rozszerzenie.   |
