# Syntax Highlighter (C)

## Opis

Program w C realizujący kolorowanie składni kodu źródłowego C poprzez analizę leksykalną i generowanie pliku HTML z odpowiednimi stylami.

---

## Kluczowe cechy

- Własny skaner leksykalny (tokenizacja kodu C)
- Obsługa:
    - słów kluczowych (`if`, `for`, `int`, itd.)
    - identyfikatorów
    - liczb (int i float)
    - stringów i znaków
    - operatorów i znaków specjalnych
    - komentarzy (`//`, `/* */`)
    - dyrektyw preprocesora (`#include`, `#define`)

- Zachowanie formatowania (spacje, taby, nowe linie)
- Generowanie kolorowanego kodu w HTML (`<span class="...">`)
- Stylowanie przez CSS (ciemny motyw)

---

## Tabela tokenów

Poniższa tabela przedstawia wszystkie typy tokenów rozpoznawane przez skaner leksykalny wraz z przykładami.

| Kategoria                    | Typy tokenów (TokenType)                                                                                                                                            | Przykłady                                                |
| ---------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------- |
| Identyfikatory               | `TOKEN_IDENTIFIER`                                                                                                                                                  | `zmienna`, `funkcja`, `x1`                               |
| Literały numeryczne          | `TOKEN_NUMBER`, `TOKEN_FLOAT`                                                                                                                                       | `123`, `45.67`, `1e-5`                                   |
| Literały napisowe i znakowe  | `TOKEN_STRING`, `TOKEN_CHAR`                                                                                                                                        | `"hello"`, `'a'`, `'\n'`                                 |
| Słowa kluczowe typów         | `TOKEN_INT`, `TOKEN_FLOAT_KW`, `TOKEN_CHAR_KW`, `TOKEN_VOID`                                                                                                        | `int`, `float`, `char`, `void`                           |
| Słowa kluczowe sterujące     | `TOKEN_IF`, `TOKEN_ELSE`, `TOKEN_FOR`, `TOKEN_WHILE`, `TOKEN_RETURN`                                                                                                | `if`, `else`, `for`, `while`, `return`                   |
| Operatory arytmetyczne       | `TOKEN_PLUS`, `TOKEN_MINUS`, `TOKEN_MULTIPLY`, `TOKEN_DIVIDE`, `TOKEN_MODULO`,<br>`TOKEN_INCREMENT`, `TOKEN_DECREMENT`                                              | `+`, `-`, `*`, `/`, `%`, `++`, `--`                      |
| Operatory relacyjne/logiczne | `TOKEN_ASSIGN`, `TOKEN_EQUAL`, `TOKEN_NOT_EQUAL`, `TOKEN_LESS`, `TOKEN_LESS_EQUAL`,<br>`TOKEN_GREATER`, `TOKEN_GREATER_EQUAL`, `TOKEN_AND`, `TOKEN_OR`, `TOKEN_NOT` | `=`, `==`, `!=`, `<`, `<=`, `>`, `>=`, `&&`, `\|\|`, `!` |
| Nawiasy i klamry             | `TOKEN_LPAREN`, `TOKEN_RPAREN`, `TOKEN_LBRACE`, `TOKEN_RBRACE`,<br>`TOKEN_LBRACKET`, `TOKEN_RBRACKET`                                                               | `(`, `)`, `{`, `}`, `[`, `]`                             |
| Znaki interpunkcyjne         | `TOKEN_SEMICOLON`, `TOKEN_COMMA`, `TOKEN_DOT`, `TOKEN_COLON`                                                                                                        | `;`, `,`, `.`, `:`                                       |
| Dyrektywy preprocesora       | `TOKEN_PREPROCESSOR` (cała linia)                                                                                                                                   | `#include <stdio.h>`, `#define MAX 100`                  |
| Komentarze                   | `TOKEN_COMMENT` (cały komentarz)                                                                                                                                    | `// komentarz`, `/* blok */`                             |
| Biały znak                   | `TOKEN_SPACE`, `TOKEN_TAB`, `TOKEN_CR`, `TOKEN_EOL`                                                                                                                 | spacja, tabulator, nowa linia                            |
| Koniec pliku                 | `TOKEN_EOF`                                                                                                                                                         | –                                                        |
| Nieznany znak                | `TOKEN_UNKNOWN`                                                                                                                                                     | znaki niedozwolone w składni C                           |

---

## Uruchomienie

```bash id="i7f1n2"
gcc syntax_highlighter.c -o highlighter
./highlighter input.c output.html
```

---

## Jak działa

- Czyta plik znak po znaku
- Rozpoznaje tokeny (jak w kompilatorze)
- Mapuje tokeny na elementy HTML (`span` z klasami)
- Dodaje CSS i zapisuje wynik jako gotową stronę HTML
