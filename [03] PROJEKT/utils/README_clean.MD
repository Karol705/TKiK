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
