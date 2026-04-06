---
read_when:
    - Chcesz zrozumieć, jak działa pamięć
    - Chcesz wiedzieć, jakie pliki pamięci zapisywać
summary: Jak OpenClaw zapamiętuje rzeczy między sesjami
title: Przegląd pamięci
x-i18n:
    generated_at: "2026-04-06T03:06:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: d19d4fa9c4b3232b7a97f7a382311d2a375b562040de15e9fe4a0b1990b825e7
    source_path: concepts/memory.md
    workflow: 15
---

# Przegląd pamięci

OpenClaw zapamiętuje rzeczy, zapisując **zwykłe pliki Markdown** w obszarze
roboczym agenta. Model „pamięta” tylko to, co zostanie zapisane na dysku — nie ma
żadnego ukrytego stanu.

## Jak to działa

Twój agent ma trzy pliki związane z pamięcią:

- **`MEMORY.md`** — pamięć długoterminowa. Trwałe fakty, preferencje i
  decyzje. Ładowane na początku każdej sesji DM.
- **`memory/YYYY-MM-DD.md`** — notatki dzienne. Bieżący kontekst i obserwacje.
  Dzisiejsze i wczorajsze notatki są ładowane automatycznie.
- **`DREAMS.md`** (eksperymentalne, opcjonalne) — Dream Diary i podsumowania
  przebiegów dreaming do przeglądu przez człowieka.

Te pliki znajdują się w obszarze roboczym agenta (domyślnie `~/.openclaw/workspace`).

<Tip>
Jeśli chcesz, aby agent coś zapamiętał, po prostu mu to powiedz: „Zapamiętaj, że
wolę TypeScript”. Zapisze to w odpowiednim pliku.
</Tip>

## Narzędzia pamięci

Agent ma dwa narzędzia do pracy z pamięcią:

- **`memory_search`** — znajduje odpowiednie notatki przy użyciu wyszukiwania semantycznego, nawet gdy
  sformułowanie różni się od oryginału.
- **`memory_get`** — odczytuje konkretny plik pamięci lub zakres wierszy.

Oba narzędzia są dostarczane przez aktywną wtyczkę pamięci (domyślnie: `memory-core`).

## Wyszukiwanie w pamięci

Gdy skonfigurowano dostawcę osadzania, `memory_search` używa **wyszukiwania
hybrydowego** — łączącego podobieństwo wektorowe (znaczenie semantyczne) z dopasowaniem słów kluczowych
(dokładne terminy, takie jak identyfikatory i symbole kodu). Działa to od razu po
skonfigurowaniu klucza API dla dowolnego obsługiwanego dostawcy.

<Info>
OpenClaw automatycznie wykrywa dostawcę osadzania na podstawie dostępnych kluczy API. Jeśli
masz skonfigurowany klucz OpenAI, Gemini, Voyage lub Mistral, wyszukiwanie w pamięci
jest włączane automatycznie.
</Info>

Szczegóły działania wyszukiwania, opcji dostrajania i konfiguracji dostawców znajdziesz w
[Wyszukiwanie w pamięci](/pl/concepts/memory-search).

## Backendy pamięci

<CardGroup cols={3}>
<Card title="Wbudowany (domyślny)" icon="database" href="/pl/concepts/memory-builtin">
Oparty na SQLite. Działa od razu z wyszukiwaniem słów kluczowych, podobieństwem wektorowym i
wyszukiwaniem hybrydowym. Bez dodatkowych zależności.
</Card>
<Card title="QMD" icon="search" href="/pl/concepts/memory-qmd">
Lokalny sidecar z rerankingiem, rozwijaniem zapytań i możliwością indeksowania
katalogów poza obszarem roboczym.
</Card>
<Card title="Honcho" icon="brain" href="/pl/concepts/memory-honcho">
Natywna dla AI pamięć między sesjami z modelowaniem użytkownika, wyszukiwaniem semantycznym i
świadomością wielu agentów. Instalacja jako wtyczka.
</Card>
</CardGroup>

## Automatyczne opróżnianie pamięci

Zanim [kompaktowanie](/pl/concepts/compaction) podsumuje rozmowę, OpenClaw
uruchamia cichą turę, która przypomina agentowi o zapisaniu ważnego kontekstu do plików
pamięci. Jest to włączone domyślnie — nie musisz nic konfigurować.

<Tip>
Opróżnianie pamięci zapobiega utracie kontekstu podczas kompaktowania. Jeśli w rozmowie
znajdują się ważne fakty, które nie zostały jeszcze zapisane do pliku, zostaną
automatycznie zapisane przed utworzeniem podsumowania.
</Tip>

## Dreaming (eksperymentalne)

Dreaming to opcjonalny przebieg konsolidacji pamięci w tle. Zbiera
sygnały krótkoterminowe, ocenia kandydatów i promuje tylko kwalifikujące się elementy do
pamięci długoterminowej (`MEMORY.md`).

Został zaprojektowany tak, aby utrzymywać wysoki stosunek sygnału do szumu w pamięci długoterminowej:

- **Opt-in**: domyślnie wyłączone.
- **Zaplanowane**: po włączeniu `memory-core` automatycznie zarządza jednym cyklicznym zadaniem cron
  dla pełnego przebiegu dreaming.
- **Z progami**: promocje muszą przejść bramki wyniku, częstotliwości przywołań i
  różnorodności zapytań.
- **Możliwe do przeglądu**: podsumowania faz i wpisy dziennika są zapisywane do `DREAMS.md`
  do przeglądu przez człowieka.

Szczegóły zachowania faz, sygnałów punktacji i Dream Diary znajdziesz w
[Dreaming (eksperymentalne)](/concepts/dreaming).

## CLI

```bash
openclaw memory status          # Sprawdź stan indeksu i dostawcę
openclaw memory search "query"  # Szukaj z wiersza poleceń
openclaw memory index --force   # Odbuduj indeks
```

## Dalsza lektura

- [Wbudowany silnik pamięci](/pl/concepts/memory-builtin) — domyślny backend SQLite
- [Silnik pamięci QMD](/pl/concepts/memory-qmd) — zaawansowany lokalny sidecar
- [Pamięć Honcho](/pl/concepts/memory-honcho) — natywna dla AI pamięć między sesjami
- [Wyszukiwanie w pamięci](/pl/concepts/memory-search) — potok wyszukiwania, dostawcy i
  dostrajanie
- [Dreaming (eksperymentalne)](/concepts/dreaming) — promocja w tle
  z przywołań krótkoterminowych do pamięci długoterminowej
- [Referencja konfiguracji pamięci](/pl/reference/memory-config) — wszystkie opcje konfiguracji
- [Kompaktowanie](/pl/concepts/compaction) — jak kompaktowanie współpracuje z pamięcią
