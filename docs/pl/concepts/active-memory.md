---
read_when:
    - Chcesz zrozumieć, do czego służy aktywna pamięć
    - Chcesz włączyć aktywną pamięć dla agenta konwersacyjnego
    - Chcesz dostroić działanie aktywnej pamięci bez włączania jej wszędzie
summary: Wtyczkowy podrzędny agent blokującej pamięci, który wstrzykuje odpowiednią pamięć do interaktywnych sesji czatu
title: Aktywna pamięć
x-i18n:
    generated_at: "2026-04-11T09:30:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: e8b0e6539e09678e9e8def68795f8bcb992f98509423da3da3123eda88ec1dd5
    source_path: concepts/active-memory.md
    workflow: 15
---

# Aktywna pamięć

Aktywna pamięć to opcjonalny, należący do wtyczki blokujący podrzędny agent pamięci, który działa
przed główną odpowiedzią dla kwalifikujących się sesji konwersacyjnych.

Istnieje, ponieważ większość systemów pamięci jest skuteczna, ale reaktywna. Polegają one
na tym, że główny agent zdecyduje, kiedy przeszukać pamięć, albo na tym, że użytkownik powie coś
w rodzaju „zapamiętaj to” lub „przeszukaj pamięć”. Wtedy moment, w którym pamięć sprawiłaby,
że odpowiedź byłaby naturalna, już minął.

Aktywna pamięć daje systemowi jedną ograniczoną szansę na wydobycie istotnej pamięci
przed wygenerowaniem głównej odpowiedzi.

## Wklej to do swojego agenta

Wklej to do swojego agenta, jeśli chcesz włączyć Aktywną pamięć z
samowystarczalną konfiguracją z bezpiecznymi ustawieniami domyślnymi:

```json5
{
  plugins: {
    entries: {
      "active-memory": {
        enabled: true,
        config: {
          enabled: true,
          agents: ["main"],
          allowedChatTypes: ["direct"],
          modelFallbackPolicy: "default-remote",
          queryMode: "recent",
          promptStyle: "balanced",
          timeoutMs: 15000,
          maxSummaryChars: 220,
          persistTranscripts: false,
          logging: true,
        },
      },
    },
  },
}
```

Spowoduje to włączenie wtyczki dla agenta `main`, domyślnie ograniczy ją do sesji
w stylu wiadomości bezpośrednich, pozwoli jej najpierw dziedziczyć bieżący model sesji, a także
nadal dopuści wbudowany zdalny mechanizm awaryjny, jeśli nie jest dostępny żaden jawny ani odziedziczony model.

Następnie uruchom ponownie bramę:

```bash
openclaw gateway
```

Aby obserwować to na żywo w rozmowie:

```text
/verbose on
```

## Włącz aktywną pamięć

Najbezpieczniejsza konfiguracja to:

1. włącz wtyczkę
2. wskaż jednego agenta konwersacyjnego
3. pozostaw logowanie włączone tylko podczas dostrajania

Zacznij od tego w `openclaw.json`:

```json5
{
  plugins: {
    entries: {
      "active-memory": {
        enabled: true,
        config: {
          agents: ["main"],
          allowedChatTypes: ["direct"],
          modelFallbackPolicy: "default-remote",
          queryMode: "recent",
          promptStyle: "balanced",
          timeoutMs: 15000,
          maxSummaryChars: 220,
          persistTranscripts: false,
          logging: true,
        },
      },
    },
  },
}
```

Następnie uruchom ponownie bramę:

```bash
openclaw gateway
```

Co to oznacza:

- `plugins.entries.active-memory.enabled: true` włącza wtyczkę
- `config.agents: ["main"]` włącza aktywną pamięć tylko dla agenta `main`
- `config.allowedChatTypes: ["direct"]` domyślnie utrzymuje aktywną pamięć tylko dla sesji w stylu wiadomości bezpośrednich
- jeśli `config.model` nie jest ustawione, aktywna pamięć najpierw dziedziczy bieżący model sesji
- `config.modelFallbackPolicy: "default-remote"` zachowuje wbudowany zdalny mechanizm awaryjny jako domyślny, gdy nie jest dostępny żaden jawny ani odziedziczony model
- `config.promptStyle: "balanced"` używa domyślnego stylu promptu ogólnego przeznaczenia dla trybu `recent`
- aktywna pamięć nadal działa tylko w kwalifikujących się interaktywnych trwałych sesjach czatu

## Jak to zobaczyć

Aktywna pamięć wstrzykuje ukryty kontekst systemowy dla modelu. Nie ujawnia
surowych tagów `<active_memory_plugin>...</active_memory_plugin>` klientowi.

## Przełącznik sesji

Użyj polecenia wtyczki, jeśli chcesz wstrzymać lub wznowić aktywną pamięć dla
bieżącej sesji czatu bez edytowania konfiguracji:

```text
/active-memory status
/active-memory off
/active-memory on
```

To działa w zakresie sesji. Nie zmienia
`plugins.entries.active-memory.enabled`, wskazywania agenta ani innej globalnej
konfiguracji.

Jeśli chcesz, aby polecenie zapisywało konfigurację oraz wstrzymywało lub wznawiało aktywną pamięć dla
wszystkich sesji, użyj jawnej formy globalnej:

```text
/active-memory status --global
/active-memory off --global
/active-memory on --global
```

Forma globalna zapisuje `plugins.entries.active-memory.config.enabled`. Pozostawia
`plugins.entries.active-memory.enabled` włączone, aby polecenie nadal było dostępne do
późniejszego ponownego włączenia aktywnej pamięci.

Jeśli chcesz zobaczyć, co aktywna pamięć robi w sesji na żywo, włącz tryb szczegółowy
dla tej sesji:

```text
/verbose on
```

Przy włączonym trybie szczegółowym OpenClaw może wyświetlić:

- wiersz stanu aktywnej pamięci, taki jak `Active Memory: ok 842ms recent 34 chars`
- czytelne podsumowanie debugowania, takie jak `Active Memory Debug: Lemon pepper wings with blue cheese.`

Te wiersze pochodzą z tego samego przebiegu aktywnej pamięci, który zasila ukryty
kontekst systemowy, ale są sformatowane dla ludzi zamiast ujawniać surowe znaczniki promptu.

Domyślnie transkrypt blokującego podrzędnego agenta pamięci jest tymczasowy i usuwany
po zakończeniu działania.

Przykładowy przebieg:

```text
/verbose on
jakie skrzydełka powinienem zamówić?
```

Oczekiwany kształt widocznej odpowiedzi:

```text
...zwykła odpowiedź asystenta...

🧩 Active Memory: ok 842ms recent 34 chars
🔎 Active Memory Debug: Skrzydełka lemon pepper z sosem blue cheese.
```

## Kiedy działa

Aktywna pamięć używa dwóch bramek:

1. **Włączenie w konfiguracji**
   Wtyczka musi być włączona, a identyfikator bieżącego agenta musi występować w
   `plugins.entries.active-memory.config.agents`.
2. **Ścisła kwalifikacja w czasie działania**
   Nawet gdy jest włączona i wskazana, aktywna pamięć działa tylko dla kwalifikujących się
   interaktywnych trwałych sesji czatu.

Rzeczywista reguła wygląda tak:

```text
wtyczka włączona
+
wskazany identyfikator agenta
+
dozwolony typ czatu
+
kwalifikująca się interaktywna trwała sesja czatu
=
aktywna pamięć działa
```

Jeśli którykolwiek z tych warunków nie jest spełniony, aktywna pamięć nie działa.

## Typy sesji

`config.allowedChatTypes` określa, w jakich rodzajach rozmów Aktywna
Pamięć może w ogóle działać.

Wartość domyślna to:

```json5
allowedChatTypes: ["direct"]
```

Oznacza to, że Aktywna pamięć działa domyślnie w sesjach w stylu wiadomości bezpośrednich, ale
nie w sesjach grupowych ani kanałowych, chyba że jawnie je włączysz.

Przykłady:

```json5
allowedChatTypes: ["direct"]
```

```json5
allowedChatTypes: ["direct", "group"]
```

```json5
allowedChatTypes: ["direct", "group", "channel"]
```

## Gdzie działa

Aktywna pamięć to funkcja wzbogacania rozmów, a nie
ogólnoplatformowa funkcja wnioskowania.

| Powierzchnia                                                         | Czy aktywna pamięć działa?                              |
| -------------------------------------------------------------------- | ------------------------------------------------------- |
| Trwałe sesje Control UI / czatu webowego                             | Tak, jeśli wtyczka jest włączona i agent jest wskazany  |
| Inne interaktywne sesje kanałowe na tej samej trwałej ścieżce czatu  | Tak, jeśli wtyczka jest włączona i agent jest wskazany  |
| Bezgłowe uruchomienia jednorazowe                                    | Nie                                                     |
| Uruchomienia heartbeat/tła                                           | Nie                                                     |
| Ogólne wewnętrzne ścieżki `agent-command`                            | Nie                                                     |
| Wykonywanie podrzędnego agenta/wewnętrznego pomocnika                | Nie                                                     |

## Dlaczego warto jej używać

Używaj aktywnej pamięci, gdy:

- sesja jest trwała i skierowana do użytkownika
- agent ma sensowną pamięć długoterminową do przeszukania
- ciągłość i personalizacja są ważniejsze niż surowy determinizm promptu

Sprawdza się szczególnie dobrze dla:

- stabilnych preferencji
- powtarzających się nawyków
- długoterminowego kontekstu użytkownika, który powinien pojawiać się naturalnie

Słabo nadaje się do:

- automatyzacji
- wewnętrznych procesów roboczych
- jednorazowych zadań API
- miejsc, w których ukryta personalizacja byłaby zaskakująca

## Jak to działa

Kształt działania w czasie wykonywania wygląda tak:

```mermaid
flowchart LR
  U["Wiadomość użytkownika"] --> Q["Zbuduj zapytanie do pamięci"]
  Q --> R["Blokujący podrzędny agent pamięci Aktywnej pamięci"]
  R -->|NONE or empty| M["Główna odpowiedź"]
  R -->|relevant summary| I["Dołącz ukryty kontekst systemowy active_memory_plugin"]
  I --> M["Główna odpowiedź"]
```

Blokujący podrzędny agent pamięci może używać tylko:

- `memory_search`
- `memory_get`

Jeśli połączenie jest słabe, powinien zwrócić `NONE`.

## Tryby zapytania

`config.queryMode` określa, jak dużą część rozmowy widzi blokujący podrzędny agent pamięci.

## Style promptu

`config.promptStyle` określa, jak chętny lub restrykcyjny jest blokujący podrzędny agent pamięci
przy podejmowaniu decyzji, czy zwrócić pamięć.

Dostępne style:

- `balanced`: domyślny styl ogólnego przeznaczenia dla trybu `recent`
- `strict`: najmniej chętny; najlepszy, gdy chcesz bardzo małego przenikania z pobliskiego kontekstu
- `contextual`: najbardziej sprzyjający ciągłości; najlepszy, gdy historia rozmowy powinna mieć większe znaczenie
- `recall-heavy`: bardziej skłonny do wydobywania pamięci przy słabszych, ale nadal prawdopodobnych dopasowaniach
- `precision-heavy`: zdecydowanie preferuje `NONE`, chyba że dopasowanie jest oczywiste
- `preference-only`: zoptymalizowany pod ulubione rzeczy, nawyki, rutyny, gust i powtarzające się fakty osobiste

Domyślne mapowanie, gdy `config.promptStyle` nie jest ustawione:

```text
message -> strict
recent -> balanced
full -> contextual
```

Jeśli jawnie ustawisz `config.promptStyle`, to nadpisanie ma pierwszeństwo.

Przykład:

```json5
promptStyle: "preference-only"
```

## Zasada awaryjnego doboru modelu

Jeśli `config.model` nie jest ustawione, Aktywna pamięć próbuje rozwiązać model w tej kolejności:

```text
jawny model wtyczki
-> bieżący model sesji
-> podstawowy model agenta
-> opcjonalny wbudowany zdalny mechanizm awaryjny
```

`config.modelFallbackPolicy` kontroluje ostatni krok.

Wartość domyślna:

```json5
modelFallbackPolicy: "default-remote"
```

Inna opcja:

```json5
modelFallbackPolicy: "resolved-only"
```

Użyj `resolved-only`, jeśli chcesz, aby Aktywna pamięć pomijała przywoływanie zamiast
korzystać z wbudowanego zdalnego domyślnego mechanizmu awaryjnego, gdy nie jest dostępny żaden jawny ani odziedziczony model.

## Zaawansowane opcje awaryjne

Te opcje celowo nie są częścią zalecanej konfiguracji.

`config.thinking` może nadpisać poziom myślenia blokującego podrzędnego agenta pamięci:

```json5
thinking: "medium"
```

Wartość domyślna:

```json5
thinking: "off"
```

Nie włączaj tego domyślnie. Aktywna pamięć działa na ścieżce odpowiedzi, więc dodatkowy
czas myślenia bezpośrednio zwiększa opóźnienie widoczne dla użytkownika.

`config.promptAppend` dodaje dodatkowe instrukcje operatora po domyślnym prompcie Aktywnej
pamięci i przed kontekstem rozmowy:

```json5
promptAppend: "Prefer stable long-term preferences over one-off events."
```

`config.promptOverride` zastępuje domyślny prompt Aktywnej pamięci. OpenClaw
nadal dołącza później kontekst rozmowy:

```json5
promptOverride: "You are a memory search agent. Return NONE or one compact user fact."
```

Dostosowywanie promptu nie jest zalecane, chyba że celowo testujesz inny
kontrakt przywoływania. Domyślny prompt jest dostrojony tak, aby zwracał `NONE`
albo zwięzły kontekst faktów o użytkowniku dla głównego modelu.

### `message`

Wysyłana jest tylko najnowsza wiadomość użytkownika.

```text
Tylko najnowsza wiadomość użytkownika
```

Używaj tego, gdy:

- chcesz najszybszego działania
- chcesz najsilniejszego ukierunkowania na przywoływanie stabilnych preferencji
- kolejne tury nie wymagają kontekstu rozmowy

Zalecany limit czasu:

- zacznij od około `3000` do `5000` ms

### `recent`

Wysyłana jest najnowsza wiadomość użytkownika oraz niewielki ogon ostatniej rozmowy.

```text
Niedawny ogon rozmowy:
user: ...
assistant: ...
user: ...

Najnowsza wiadomość użytkownika:
...
```

Używaj tego, gdy:

- chcesz lepszej równowagi między szybkością a osadzeniem w rozmowie
- pytania uzupełniające często zależą od kilku ostatnich tur

Zalecany limit czasu:

- zacznij od około `15000` ms

### `full`

Cała rozmowa jest wysyłana do blokującego podrzędnego agenta pamięci.

```text
Pełny kontekst rozmowy:
user: ...
assistant: ...
user: ...
...
```

Używaj tego, gdy:

- najwyższa jakość przywoływania ma większe znaczenie niż opóźnienie
- rozmowa zawiera ważne przygotowanie daleko wcześniej w wątku

Zalecany limit czasu:

- zwiększ go znacząco w porównaniu z `message` lub `recent`
- zacznij od około `15000` ms lub więcej, zależnie od rozmiaru wątku

Ogólnie limit czasu powinien rosnąć wraz z rozmiarem kontekstu:

```text
message < recent < full
```

## Trwałość transkryptu

Uruchomienia blokującego podrzędnego agenta pamięci aktywnej pamięci tworzą rzeczywisty transkrypt `session.jsonl`
podczas wywołania blokującego podrzędnego agenta pamięci.

Domyślnie ten transkrypt jest tymczasowy:

- jest zapisywany w katalogu tymczasowym
- jest używany tylko na potrzeby przebiegu blokującego podrzędnego agenta pamięci
- jest usuwany natychmiast po zakończeniu przebiegu

Jeśli chcesz zachować te transkrypty blokującego podrzędnego agenta pamięci na dysku do debugowania lub
inspekcji, jawnie włącz trwałość:

```json5
{
  plugins: {
    entries: {
      "active-memory": {
        enabled: true,
        config: {
          agents: ["main"],
          persistTranscripts: true,
          transcriptDir: "active-memory",
        },
      },
    },
  },
}
```

Po włączeniu aktywna pamięć przechowuje transkrypty w osobnym katalogu w folderze
sesji docelowego agenta, a nie w głównej ścieżce transkryptu rozmowy użytkownika.

Domyślny układ koncepcyjnie wygląda tak:

```text
agents/<agent>/sessions/active-memory/<blocking-memory-sub-agent-session-id>.jsonl
```

Możesz zmienić względny podkatalog za pomocą `config.transcriptDir`.

Używaj tego ostrożnie:

- transkrypty blokującego podrzędnego agenta pamięci mogą szybko się gromadzić w intensywnie używanych sesjach
- tryb zapytania `full` może duplikować dużą część kontekstu rozmowy
- te transkrypty zawierają ukryty kontekst promptu i przywołane wspomnienia

## Konfiguracja

Cała konfiguracja aktywnej pamięci znajduje się w:

```text
plugins.entries.active-memory
```

Najważniejsze pola to:

| Klucz                       | Typ                                                                                                  | Znaczenie                                                                                              |
| --------------------------- | ---------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------ |
| `enabled`                   | `boolean`                                                                                            | Włącza samą wtyczkę                                                                                    |
| `config.agents`             | `string[]`                                                                                           | Identyfikatory agentów, które mogą używać aktywnej pamięci                                            |
| `config.model`              | `string`                                                                                             | Opcjonalne odwołanie do modelu blokującego podrzędnego agenta pamięci; gdy nie jest ustawione, aktywna pamięć używa bieżącego modelu sesji |
| `config.queryMode`          | `"message" \| "recent" \| "full"`                                                                    | Określa, jak dużą część rozmowy widzi blokujący podrzędny agent pamięci                               |
| `config.promptStyle`        | `"balanced" \| "strict" \| "contextual" \| "recall-heavy" \| "precision-heavy" \| "preference-only"` | Określa, jak chętny lub restrykcyjny jest blokujący podrzędny agent pamięci przy podejmowaniu decyzji, czy zwrócić pamięć |
| `config.thinking`           | `"off" \| "minimal" \| "low" \| "medium" \| "high" \| "xhigh" \| "adaptive"`                         | Zaawansowane nadpisanie poziomu myślenia dla blokującego podrzędnego agenta pamięci; domyślnie `off` dla szybkości |
| `config.promptOverride`     | `string`                                                                                             | Zaawansowane pełne zastąpienie promptu; niezalecane do normalnego użycia                              |
| `config.promptAppend`       | `string`                                                                                             | Zaawansowane dodatkowe instrukcje dołączane do domyślnego lub nadpisanego promptu                     |
| `config.timeoutMs`          | `number`                                                                                             | Twardy limit czasu dla blokującego podrzędnego agenta pamięci                                         |
| `config.maxSummaryChars`    | `number`                                                                                             | Maksymalna łączna liczba znaków dozwolona w podsumowaniu active-memory                                 |
| `config.logging`            | `boolean`                                                                                            | Emisja logów aktywnej pamięci podczas dostrajania                                                     |
| `config.persistTranscripts` | `boolean`                                                                                            | Zachowuje transkrypty blokującego podrzędnego agenta pamięci na dysku zamiast usuwać pliki tymczasowe |
| `config.transcriptDir`      | `string`                                                                                             | Względny katalog transkryptów blokującego podrzędnego agenta pamięci w folderze sesji agenta          |

Przydatne pola do dostrajania:

| Klucz                         | Typ     | Znaczenie                                                     |
| ----------------------------- | -------- | ------------------------------------------------------------- |
| `config.maxSummaryChars`      | `number` | Maksymalna łączna liczba znaków dozwolona w podsumowaniu active-memory |
| `config.recentUserTurns`      | `number` | Poprzednie tury użytkownika do uwzględnienia, gdy `queryMode` ma wartość `recent` |
| `config.recentAssistantTurns` | `number` | Poprzednie tury asystenta do uwzględnienia, gdy `queryMode` ma wartość `recent` |
| `config.recentUserChars`      | `number` | Maksymalna liczba znaków na ostatnią turę użytkownika         |
| `config.recentAssistantChars` | `number` | Maksymalna liczba znaków na ostatnią turę asystenta           |
| `config.cacheTtlMs`           | `number` | Ponowne użycie pamięci podręcznej dla powtarzających się identycznych zapytań |

## Zalecana konfiguracja

Zacznij od `recent`.

```json5
{
  plugins: {
    entries: {
      "active-memory": {
        enabled: true,
        config: {
          agents: ["main"],
          queryMode: "recent",
          promptStyle: "balanced",
          timeoutMs: 15000,
          maxSummaryChars: 220,
          logging: true,
        },
      },
    },
  },
}
```

Jeśli chcesz sprawdzać zachowanie na żywo podczas dostrajania, użyj `/verbose on` w
sesji zamiast szukać osobnego polecenia debugowania active-memory.

Następnie przejdź do:

- `message`, jeśli chcesz mniejszych opóźnień
- `full`, jeśli uznasz, że dodatkowy kontekst jest wart wolniejszego blokującego podrzędnego agenta pamięci

## Debugowanie

Jeśli aktywna pamięć nie pojawia się tam, gdzie tego oczekujesz:

1. Potwierdź, że wtyczka jest włączona w `plugins.entries.active-memory.enabled`.
2. Potwierdź, że identyfikator bieżącego agenta znajduje się na liście `config.agents`.
3. Potwierdź, że testujesz przez interaktywną trwałą sesję czatu.
4. Włącz `config.logging: true` i obserwuj logi bramy.
5. Zweryfikuj, że samo przeszukiwanie pamięci działa, używając `openclaw memory status --deep`.

Jeśli trafienia pamięci są zbyt chaotyczne, zaostrz:

- `maxSummaryChars`

Jeśli aktywna pamięć działa zbyt wolno:

- obniż `queryMode`
- obniż `timeoutMs`
- zmniejsz liczbę ostatnich tur
- zmniejsz limity znaków na turę

## Powiązane strony

- [Wyszukiwanie w pamięci](/pl/concepts/memory-search)
- [Dokumentacja konfiguracji pamięci](/pl/reference/memory-config)
- [Konfiguracja Plugin SDK](/pl/plugins/sdk-setup)
