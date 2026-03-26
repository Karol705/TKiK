# Syntax Highlighter (C)

## 📌 Opis

Program w C realizujący kolorowanie składni kodu źródłowego C poprzez analizę leksykalną i generowanie pliku HTML z odpowiednimi stylami.

---

## ⚙️ Kluczowe cechy

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

## ▶️ Uruchomienie

```bash id="i7f1n2"
gcc syntax_highlighter.c -o highlighter
./highlighter input.c output.html
```

---

## 📚 Jak działa

- Czyta plik znak po znaku
- Rozpoznaje tokeny (jak w kompilatorze)
- Mapuje tokeny na elementy HTML (`span` z klasami)
- Dodaje CSS i zapisuje wynik jako gotową stronę HTML
