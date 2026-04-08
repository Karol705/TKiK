# Equation Scanner

## 📌 Opis

Prosty skaner leksykalny napisany w C, który przetwarza plik wejściowy i zamienia go na ciąg tokenów dla wyrażeń arytmetycznych.

---

## ⚙️ Kluczowe cechy

- Obsługa liczb całkowitych (`NUMBER`)
- Podstawowe operatory: `+`, `-`, `*`, `/`
- Nawiasy: `(`, `)`
- Pomijanie białych znaków (spacje, taby, nowe linie)
- Śledzenie pozycji tokenów (linia, kolumna)
- Zapis tokenów do pliku wyjściowego

---

## 🧱 Tokeny

| Token      | Opis                 | Przykład |
| ---------- | -------------------- | -------- |
| `NUMBER`   | Liczba całkowita     | `123`    |
| `PLUS`     | Operator dodawania   | `+`      |
| `MINUS`    | Operator odejmowania | `-`      |
| `MULTIPLY` | Operator mnożenia    | `*`      |
| `DIVIDE`   | Operator dzielenia   | `/`      |
| `LPAREN`   | Nawias lewy          | `(`      |
| `RPAREN`   | Nawias prawy         | `)`      |
| `EOF`      | Koniec pliku         | –        |

---

## ▶️ Uruchomienie

```bash
gcc scanner.c -o scanner
./scanner input.txt output.txt
```

---

## 📚 Jak działa

- Czyta plik znak po znaku
- Pomija białe znaki
- Rozpoznaje liczby i operatory
- Zwraca tokeny z informacją o pozycji
- Kończy na `EOF`
