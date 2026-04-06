---
x-i18n:
    generated_at: "2026-04-06T03:05:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6e1cf417b0c04d001bc494fbe03ac2fcb66866f759e21646dbfd1a9c3a968bff
    source_path: .i18n/README.md
    workflow: 15
---

# Zasoby i18n dokumentacji OpenClaw

Ten folder przechowuje konfigurację tłumaczeń dla repozytorium źródłowego dokumentacji.

Wygenerowane strony lokalizacji i aktywna pamięć tłumaczeń dla lokalizacji znajdują się teraz w repozytorium publikacji (`openclaw/docs`, lokalny sąsiedni checkout `~/Projects/openclaw-docs`).

## Pliki

- `glossary.<lang>.json` — preferowane mapowania terminów (używane we wskazówkach promptu).
- `<lang>.tm.jsonl` — pamięć tłumaczeń (pamięć podręczna) z kluczami workflow + model + hash tekstu. W tym repozytorium pliki TM lokalizacji są generowane na żądanie.

## Format glosariusza

`glossary.<lang>.json` to tablica wpisów:

```json
{
  "source": "troubleshooting",
  "target": "故障排除",
  "ignore_case": true,
  "whole_word": false
}
```

Pola:

- `source`: angielska (lub źródłowa) fraza, która ma być preferowana.
- `target`: preferowany wynik tłumaczenia.

## Uwagi

- Wpisy glosariusza są przekazywane do modelu jako **wskazówki promptu** (bez deterministycznych przepisań).
- `scripts/docs-i18n` nadal odpowiada za generowanie tłumaczeń.
- Repozytorium źródłowe synchronizuje angielską dokumentację z repozytorium publikacji; generowanie lokalizacji jest tam uruchamiane dla każdego języka przy pushu, według harmonogramu i przy wysyłce wydania.
