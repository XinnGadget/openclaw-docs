---
read_when:
    - Chcesz, aby awans pamięci działał automatycznie
    - Chcesz zrozumieć, co robi każda faza Dreaming
    - Chcesz dostroić konsolidację bez zaśmiecania `MEMORY.md`
summary: Konsolidacja pamięci w tle z fazami light, deep i REM oraz Dziennikiem snów
title: Dreaming
x-i18n:
    generated_at: "2026-04-15T14:40:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: a5bcaec80f62e7611ed533094ef1917bd72c885f57252824db910e1f0496adc6
    source_path: concepts/dreaming.md
    workflow: 15
---

# Dreaming

Dreaming to system konsolidacji pamięci działający w tle w `memory-core`.
Pomaga OpenClaw przenosić silne sygnały z pamięci krótkotrwałej do trwałej pamięci,
zachowując przy tym przejrzystość i możliwość przeglądu procesu.

Dreaming jest **opcjonalny** i domyślnie wyłączony.

## Co zapisuje Dreaming

Dreaming przechowuje dwa rodzaje danych wyjściowych:

- **Stan maszyny** w `memory/.dreams/` (magazyn recall, sygnały faz, punkty kontrolne ingestii, blokady).
- **Czytelne dla człowieka dane wyjściowe** w `DREAMS.md` (lub istniejącym `dreams.md`) oraz opcjonalne pliki raportów faz w `memory/dreaming/<phase>/YYYY-MM-DD.md`.

Promowanie do pamięci długotrwałej nadal zapisuje dane wyłącznie do `MEMORY.md`.

## Model faz

Dreaming używa trzech współpracujących faz:

| Faza | Cel | Trwały zapis |
| ----- | --- | ------------ |
| Light | Sortowanie i przygotowanie ostatnich materiałów z pamięci krótkotrwałej | Nie |
| Deep  | Ocenianie i promowanie trwałych kandydatów | Tak (`MEMORY.md`) |
| REM   | Refleksja nad motywami i powtarzającymi się ideami | Nie |

Te fazy są wewnętrznymi szczegółami implementacji, a nie oddzielnymi
konfigurowanymi przez użytkownika „trybami”.

### Faza Light

Faza Light pobiera ostatnie sygnały z codziennej pamięci i ślady recall, usuwa duplikaty
oraz przygotowuje wiersze kandydatów.

- Odczytuje stan recall pamięci krótkotrwałej, ostatnie pliki codziennej pamięci oraz zredagowane transkrypty sesji, jeśli są dostępne.
- Zapisuje zarządzany blok `## Light Sleep`, gdy magazyn obejmuje dane wyjściowe inline.
- Rejestruje sygnały wzmocnienia do późniejszego rankingu deep.
- Nigdy nie zapisuje do `MEMORY.md`.

### Faza Deep

Faza Deep decyduje o tym, co staje się pamięcią długotrwałą.

- Nadaje kandydatom ranking przy użyciu ważonej punktacji i progów.
- Wymaga spełnienia `minScore`, `minRecallCount` i `minUniqueQueries`.
- Przed zapisem ponownie pobiera fragmenty z aktywnych plików dziennych, dzięki czemu nieaktualne/usunięte fragmenty są pomijane.
- Dopisuje promowane wpisy do `MEMORY.md`.
- Zapisuje podsumowanie `## Deep Sleep` w `DREAMS.md` i opcjonalnie zapisuje `memory/dreaming/deep/YYYY-MM-DD.md`.

### Faza REM

Faza REM wyodrębnia wzorce i sygnały refleksyjne.

- Buduje podsumowania motywów i refleksji na podstawie ostatnich śladów pamięci krótkotrwałej.
- Zapisuje zarządzany blok `## REM Sleep`, gdy magazyn obejmuje dane wyjściowe inline.
- Rejestruje sygnały wzmocnienia REM używane przez ranking deep.
- Nigdy nie zapisuje do `MEMORY.md`.

## Ingestia transkryptów sesji

Dreaming może pobierać zredagowane transkrypty sesji do korpusu Dreaming. Gdy
transkrypty są dostępne, trafiają do fazy light wraz z sygnałami codziennej
pamięci i śladami recall. Treści osobiste i wrażliwe są redagowane
przed ingestą.

## Dziennik snów

Dreaming prowadzi także narracyjny **Dziennik snów** w `DREAMS.md`.
Gdy po każdej fazie zbierze się wystarczająco dużo materiału, `memory-core` uruchamia
w tle, w trybie best-effort, turę subagenta (z użyciem domyślnego modelu runtime)
i dopisuje krótki wpis do dziennika.

Ten dziennik jest przeznaczony do czytania przez ludzi w interfejsie Dreams, a nie jako źródło promocji.
Artefakty dziennika/raportów wygenerowane przez Dreaming są wykluczone z promocji
pamięci krótkotrwałej. Do promowania do
`MEMORY.md` kwalifikują się wyłącznie ugruntowane fragmenty pamięci.

Istnieje także ugruntowana ścieżka historycznego backfillu do przeglądu i odzyskiwania danych:

- `memory rem-harness --path ... --grounded` wyświetla podgląd ugruntowanych danych wyjściowych dziennika na podstawie historycznych notatek `YYYY-MM-DD.md`.
- `memory rem-backfill --path ...` zapisuje odwracalne ugruntowane wpisy dziennika w `DREAMS.md`.
- `memory rem-backfill --path ... --stage-short-term` przygotowuje ugruntowanych trwałych kandydatów w tym samym magazynie dowodów krótkoterminowych, którego używa już normalna faza deep.
- `memory rem-backfill --rollback` i `--rollback-short-term` usuwają te przygotowane artefakty backfillu bez naruszania zwykłych wpisów dziennika ani aktywnego recall pamięci krótkotrwałej.

Interfejs Control udostępnia ten sam przepływ backfillu/resetowania dziennika, dzięki czemu możesz sprawdzić
wyniki w scenie Dreams, zanim zdecydujesz, czy ugruntowani kandydaci
zasługują na promocję. Scena pokazuje także osobną ugruntowaną ścieżkę, aby było widać,
które przygotowane wpisy krótkoterminowe pochodzą z historycznego odtwarzania, które promowane
elementy były prowadzone przez dane ugruntowane, oraz umożliwia wyczyszczenie wyłącznie
ugruntowanych przygotowanych wpisów bez naruszania zwykłego aktywnego stanu pamięci krótkotrwałej.

## Sygnały rankingu deep

Ranking deep używa sześciu ważonych sygnałów bazowych oraz wzmocnienia faz:

| Sygnał | Waga | Opis |
| ------ | ---- | ---- |
| Częstotliwość | 0.24 | Ile sygnałów pamięci krótkotrwałej zgromadził wpis |
| Trafność | 0.30 | Średnia jakość odzyskiwania dla wpisu |
| Różnorodność zapytań | 0.15 | Różne konteksty zapytań/dni, w których się pojawił |
| Aktualność | 0.15 | Punktacja świeżości z osłabieniem w czasie |
| Konsolidacja | 0.10 | Siła nawrotów w wielu dniach |
| Bogactwo koncepcyjne | 0.06 | Gęstość tagów pojęciowych na podstawie fragmentu/ścieżki |

Trafienia faz Light i REM dodają niewielkie wzmocnienie z osłabieniem w czasie
z `memory/.dreams/phase-signals.json`.

## Harmonogram

Po włączeniu `memory-core` automatycznie zarządza jednym zadaniem Cron dla pełnego przebiegu Dreaming.
Każdy przebieg uruchamia fazy po kolei: light -> REM -> deep.

Domyślne zachowanie harmonogramu:

| Ustawienie | Domyślna wartość |
| ---------- | ---------------- |
| `dreaming.frequency` | `0 3 * * *` |

## Szybki start

Włącz Dreaming:

```json
{
  "plugins": {
    "entries": {
      "memory-core": {
        "config": {
          "dreaming": {
            "enabled": true
          }
        }
      }
    }
  }
}
```

Włącz Dreaming z własnym harmonogramem przebiegów:

```json
{
  "plugins": {
    "entries": {
      "memory-core": {
        "config": {
          "dreaming": {
            "enabled": true,
            "timezone": "America/Los_Angeles",
            "frequency": "0 */6 * * *"
          }
        }
      }
    }
  }
}
```

## Komenda slash

```
/dreaming status
/dreaming on
/dreaming off
/dreaming help
```

## Przepływ pracy CLI

Użyj promocji CLI do podglądu lub ręcznego zastosowania:

```bash
openclaw memory promote
openclaw memory promote --apply
openclaw memory promote --limit 5
openclaw memory status --deep
```

Ręczne `memory promote` domyślnie używa progów fazy deep, chyba że zostaną nadpisane
flagami CLI.

Wyjaśnij, dlaczego konkretny kandydat zostałby lub nie zostałby promowany:

```bash
openclaw memory promote-explain "router vlan"
openclaw memory promote-explain "router vlan" --json
```

Wyświetl podgląd refleksji REM, prawd kandydatów i danych wyjściowych promocji deep bez
zapisywania czegokolwiek:

```bash
openclaw memory rem-harness
openclaw memory rem-harness --json
```

## Kluczowe wartości domyślne

Wszystkie ustawienia znajdują się w `plugins.entries.memory-core.config.dreaming`.

| Klucz | Domyślna wartość |
| ----- | ---------------- |
| `enabled` | `false` |
| `frequency` | `0 3 * * *` |

Zasady faz, progi i zachowanie magazynu są wewnętrznymi szczegółami implementacji
(i nie stanowią konfiguracji dostępnej dla użytkownika).

Pełną listę kluczy znajdziesz w [Dokumentacji konfiguracji pamięci](/pl/reference/memory-config#dreaming).

## Interfejs Dreams

Po włączeniu karta **Dreams** w Gateway pokazuje:

- bieżący stan włączenia Dreaming
- status na poziomie faz oraz obecność zarządzanego przebiegu
- liczbę wpisów krótkoterminowych, ugruntowanych, sygnałów i promowanych dzisiaj
- czas do następnego zaplanowanego uruchomienia
- osobną ugruntowaną ścieżkę sceny dla przygotowanych wpisów z historycznego odtwarzania
- rozwijany czytnik Dziennika snów oparty na `doctor.memory.dreamDiary`

## Powiązane

- [Pamięć](/pl/concepts/memory)
- [Wyszukiwanie pamięci](/pl/concepts/memory-search)
- [CLI pamięci](/cli/memory)
- [Dokumentacja konfiguracji pamięci](/pl/reference/memory-config)
