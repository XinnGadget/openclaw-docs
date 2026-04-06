---
read_when:
    - Chcesz, aby promowanie pamięci uruchamiało się automatycznie
    - Chcesz zrozumieć, co robi każda faza śnienia
    - Chcesz dostroić konsolidację bez zaśmiecania pliku MEMORY.md
summary: Konsolidacja pamięci w tle z fazami lekką, głęboką i REM oraz Dziennikiem snów
title: Śnienie (eksperymentalne)
x-i18n:
    generated_at: "2026-04-06T03:06:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: f27da718176bebf59fe8a80fddd4fb5b6d814ac5647f6c1e8344bcfb328db9de
    source_path: concepts/dreaming.md
    workflow: 15
---

# Śnienie (eksperymentalne)

Śnienie to system konsolidacji pamięci działający w tle w `memory-core`.
Pomaga OpenClaw przenosić silne sygnały pamięci krótkoterminowej do trwałej pamięci, jednocześnie
zachowując przejrzystość i możliwość przeglądu całego procesu.

Śnienie jest funkcją **opcjonalną** i domyślnie jest wyłączone.

## Co zapisuje śnienie

Śnienie przechowuje dwa rodzaje danych wyjściowych:

- **Stan maszyny** w `memory/.dreams/` (magazyn recall, sygnały faz, punkty kontrolne przetwarzania, blokady).
- **Czytelne dla człowieka dane wyjściowe** w `DREAMS.md` (lub istniejącym `dreams.md`) oraz opcjonalnych plikach raportów faz w `memory/dreaming/<phase>/YYYY-MM-DD.md`.

Promowanie do pamięci długoterminowej nadal zapisuje dane wyłącznie do `MEMORY.md`.

## Model faz

Śnienie wykorzystuje trzy współpracujące fazy:

| Faza | Cel                                       | Trwały zapis      |
| ----- | ----------------------------------------- | ----------------- |
| Lekka | Sortowanie i przygotowywanie niedawnych materiałów krótkoterminowych | Nie               |
| Głęboka  | Ocenianie i promowanie trwałych kandydatów      | Tak (`MEMORY.md`) |
| REM   | Refleksja nad tematami i powracającymi ideami     | Nie               |

Te fazy są wewnętrznymi szczegółami implementacji, a nie osobnymi
„trybami” konfigurowanymi przez użytkownika.

### Faza lekka

Faza lekka przetwarza niedawne dzienne sygnały pamięci i ślady recall, usuwa duplikaty
i przygotowuje linie kandydatów.

- Odczytuje stan recall pamięci krótkoterminowej i niedawne dzienne pliki pamięci.
- Zapisuje zarządzany blok `## Light Sleep`, gdy magazyn obejmuje dane wyjściowe wbudowane w plik.
- Rejestruje sygnały wzmacniające do późniejszego głębokiego rankingu.
- Nigdy nie zapisuje do `MEMORY.md`.

### Faza głęboka

Faza głęboka decyduje, co staje się pamięcią długoterminową.

- Nadaje ranking kandydatom przy użyciu ważonej punktacji i progów.
- Wymaga spełnienia `minScore`, `minRecallCount` i `minUniqueQueries`.
- Przed zapisem ponownie pobiera fragmenty z aktywnych dziennych plików, więc nieaktualne lub usunięte fragmenty są pomijane.
- Dopisuje promowane wpisy do `MEMORY.md`.
- Zapisuje podsumowanie `## Deep Sleep` w `DREAMS.md` i opcjonalnie zapisuje `memory/dreaming/deep/YYYY-MM-DD.md`.

### Faza REM

Faza REM wyodrębnia wzorce i sygnały refleksyjne.

- Tworzy podsumowania tematów i refleksji na podstawie niedawnych śladów krótkoterminowych.
- Zapisuje zarządzany blok `## REM Sleep`, gdy magazyn obejmuje dane wyjściowe wbudowane w plik.
- Rejestruje sygnały wzmacniające REM używane przez głęboki ranking.
- Nigdy nie zapisuje do `MEMORY.md`.

## Dziennik snów

Śnienie prowadzi też narracyjny **Dziennik snów** w `DREAMS.md`.
Gdy po każdej fazie zbierze się wystarczająco dużo materiału, `memory-core` uruchamia w tle
pomocniczą turę subagenta w trybie best-effort (z użyciem domyślnego modelu runtime)
i dopisuje krótki wpis do dziennika.

Ten dziennik jest przeznaczony do czytania przez człowieka w interfejsie Dreams, a nie jako źródło promocji.

## Sygnały głębokiego rankingu

Głęboki ranking wykorzystuje sześć ważonych sygnałów bazowych oraz wzmocnienie faz:

| Sygnał              | Waga | Opis                                       |
| ------------------- | ------ | ------------------------------------------------- |
| Częstotliwość           | 0.24   | Ile krótkoterminowych sygnałów zgromadził wpis |
| Trafność           | 0.30   | Średnia jakość wyszukiwania dla wpisu           |
| Różnorodność zapytań     | 0.15   | Różne konteksty zapytań/dni, w których się pojawił      |
| Aktualność             | 0.15   | Wynik świeżości osłabiany w czasie                      |
| Konsolidacja       | 0.10   | Siła nawrotów w wielu dniach                     |
| Bogactwo pojęciowe | 0.06   | Gęstość tagów pojęciowych na podstawie fragmentu/ścieżki             |

Trafienia z faz lekkiej i REM dodają niewielkie wzmocnienie osłabiane przez aktualność z
`memory/.dreams/phase-signals.json`.

## Harmonogram

Po włączeniu `memory-core` automatycznie zarządza jednym zadaniem cron dla pełnego
przebiegu śnienia. Każdy przebieg uruchamia fazy po kolei: lekka -> REM -> głęboka.

Domyślne zachowanie harmonogramu:

| Ustawienie              | Domyślnie     |
| -------------------- | ----------- |
| `dreaming.frequency` | `0 3 * * *` |

## Szybki start

Włącz śnienie:

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

Włącz śnienie z niestandardowym harmonogramem przebiegu:

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

## Komenda ukośnikowa

```
/dreaming status
/dreaming on
/dreaming off
/dreaming help
```

## Przepływ pracy CLI

Użyj promowania przez CLI do podglądu lub ręcznego zastosowania:

```bash
openclaw memory promote
openclaw memory promote --apply
openclaw memory promote --limit 5
openclaw memory status --deep
```

Ręczne `memory promote` domyślnie używa progów fazy głębokiej, chyba że zostaną one nadpisane
flagami CLI.

## Kluczowe wartości domyślne

Wszystkie ustawienia znajdują się pod `plugins.entries.memory-core.config.dreaming`.

| Klucz         | Domyślnie     |
| ----------- | ----------- |
| `enabled`   | `false`     |
| `frequency` | `0 3 * * *` |

Zasady faz, progi i zachowanie magazynu są wewnętrznymi szczegółami implementacji
(i nie stanowią konfiguracji dostępnej dla użytkownika).

Pełną listę kluczy znajdziesz w [Dokumentacji konfiguracji pamięci](/pl/reference/memory-config#dreaming-experimental).

## Interfejs Dreams

Po włączeniu karta **Dreams** w Gateway pokazuje:

- bieżący stan włączenia śnienia
- status na poziomie faz i obecność zarządzanego przebiegu
- liczbę elementów krótkoterminowych, długoterminowych i promowanych dzisiaj
- czas następnego zaplanowanego uruchomienia
- rozwijany czytnik Dziennika snów oparty na `doctor.memory.dreamDiary`

## Powiązane

- [Pamięć](/pl/concepts/memory)
- [Wyszukiwanie w pamięci](/pl/concepts/memory-search)
- [CLI pamięci](/cli/memory)
- [Dokumentacja konfiguracji pamięci](/pl/reference/memory-config)
