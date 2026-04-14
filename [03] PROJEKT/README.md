# Rust State Tracker

# Autorzy

Karol Baran – kabaran@student.agh.edu.pl

Łukasz Borysiuk – lborysiuk@student.agh.edu.pl

## Założenia programu

- **Ogólne cele programu:**
    - Stworzenie narzędzia analitycznego do śledzenia cyklu życia zmiennych w języku Rust.
    - Wizualizacja skomplikowanych mechanizmów zarządzania pamięcią (ownership, borrowing, lifetime).
    - Pomoc w zrozumieniu działania mechanizmu Borrow Checker poprzez generowanie czytelnej osi czasu (timeline) zmian stanów.

- **Rodzaj translatora:**
  Interpreter

- **Planowany wynik działania programu:**
    - **Oś czasu stanów (Timeline):** Sekwencyjne zestawienie zmian dla każdej zmiennej (np. _Declared_ -> _Initialized_ -> _Borrowed_ -> _Dropped_).
    - **Wizualizacja graficzna:** Generowanie grafów zależności (format DOT/Graphviz) przedstawiających relacje między zmiennymi a referencjami.

- **Język implementacji:**
    - **Python 3.13+**.

- **Sposób realizacji skanera/parsera:**
    - Wykorzystanie generatora parserów **PLY (Python Lex-Yacc)**.
    - Skaner oparty na wyrażeniach regularnych.
    - Parser LALR budujący drzewo składniowe (AST).

## Możliwe rozszerzenia

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

## Struktura projektu

```bash
rust_state_tracker/
├── src/
│   ├── parser/             # PLY Lexer and Parser definitions
│   │   ├── __init__.py
│   │   ├── lexer.py        # Token definitions for Rust subset
│   │   └── grammar.py      # Yacc production rules & AST building
│   ├── analyzer/           # The "Brain" (Static Analysis)
│   │   ├── __init__.py
│   │   ├── models.py       # Classes for Variable, Reference, Scope
│   │   ├── tracker.py      # Logic for Ownership/Borrowing rules
│   │   └── timeline.py     # Generates the sequence of states
│   ├── visualization/      # Output logic
│   │   ├── __init__.py
│   │   ├── text_render.py  # CLI/Terminal output
│   │   └── graph_gen.py    # Export to Graphviz or Interactive plots
│   ├── main.py             # Entry point (CLI handling)
│   └── utils.py            # Helpers (logging, file I/O)
├── tests/                  # Test suite
│   ├── test_lexer.py
│   ├── test_ownership.py   # Test cases for move/borrow logic
│   └── samples/            # Real .rs files to feed into your tool
│       ├── basic_move.rs
│       └── borrow_conflict.rs
├── .gitignore
├── pyproject.toml          # Managed by UV
├── uv.lock                 # Managed by UV
└── README.md
```

---

## Tokeny i gramatyka

- Link do opisu: [lexer_and_grammar](utils/lexer_grammar.md)
