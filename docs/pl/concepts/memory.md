---
read_when:
    - Chcesz zrozumieć, jak działa pamięć
    - Chcesz wiedzieć, które pliki pamięci zapisywać
summary: Jak OpenClaw zapamiętuje rzeczy między sesjami
title: Przegląd pamięci
x-i18n:
    generated_at: "2026-04-15T14:40:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: ad1adafe1d81f1703d24f48a9c9da2b25a0ebbd4aad4f65d8bde5df78195d55b
    source_path: concepts/memory.md
    workflow: 15
---

# Przegląd pamięci

OpenClaw zapamiętuje rzeczy, zapisując **zwykłe pliki Markdown** w obszarze roboczym Twojego agenta. Model „pamięta” tylko to, co zostanie zapisane na dysku — nie ma żadnego ukrytego stanu.

## Jak to działa

Twój agent ma trzy pliki związane z pamięcią:

- **`MEMORY.md`** — pamięć długoterminowa. Trwałe fakty, preferencje i decyzje. Wczytywany na początku każdej sesji DM.
- **`memory/YYYY-MM-DD.md`** — notatki dzienne. Bieżący kontekst i obserwacje. Dzisiejsze i wczorajsze notatki są wczytywane automatycznie.
- **`DREAMS.md`** (opcjonalnie) — Dziennik snów i podsumowania przebiegów Dreaming do przeglądu przez człowieka, w tym ugruntowane wpisy historycznego backfillu.

Te pliki znajdują się w obszarze roboczym agenta (domyślnie `~/.openclaw/workspace`).

<Tip>
Jeśli chcesz, aby Twój agent coś zapamiętał, po prostu go o to poproś: „Zapamiętaj, że preferuję TypeScript.” Zapisze to w odpowiednim pliku.
</Tip>

## Narzędzia pamięci

Agent ma dwa narzędzia do pracy z pamięcią:

- **`memory_search`** — znajduje odpowiednie notatki za pomocą wyszukiwania semantycznego, nawet gdy sformułowanie różni się od oryginału.
- **`memory_get`** — odczytuje konkretny plik pamięci lub zakres linii.

Oba narzędzia są dostarczane przez aktywny Plugin pamięci (domyślnie: `memory-core`).

## Towarzyszący Plugin Memory Wiki

Jeśli chcesz, aby trwała pamięć działała bardziej jak utrzymywana baza wiedzy niż tylko surowe notatki, użyj dołączonego Pluginu `memory-wiki`.

`memory-wiki` kompiluje trwałą wiedzę do skarbca wiki z:

- deterministyczną strukturą stron
- uporządkowanymi twierdzeniami i dowodami
- śledzeniem sprzeczności i aktualności
- generowanymi pulpitami
- skompilowanymi skrótami dla konsumentów agentów/runtime
- natywnymi dla wiki narzędziami, takimi jak `wiki_search`, `wiki_get`, `wiki_apply` i `wiki_lint`

Nie zastępuje aktywnego Pluginu pamięci. Aktywny Plugin pamięci nadal odpowiada za przypominanie, promowanie i Dreaming. `memory-wiki` dodaje obok niego warstwę wiedzy bogatą w pochodzenie.

Zobacz [Memory Wiki](/pl/plugins/memory-wiki).

## Wyszukiwanie w pamięci

Gdy skonfigurowany jest dostawca embeddingów, `memory_search` używa **wyszukiwania hybrydowego** — łączącego podobieństwo wektorowe (znaczenie semantyczne) z dopasowaniem słów kluczowych (dokładne terminy, takie jak identyfikatory i symbole kodu). Działa to od razu po skonfigurowaniu klucza API dla dowolnego obsługiwanego dostawcy.

<Info>
OpenClaw automatycznie wykrywa Twojego dostawcę embeddingów na podstawie dostępnych kluczy API. Jeśli masz skonfigurowany klucz OpenAI, Gemini, Voyage lub Mistral, wyszukiwanie w pamięci jest włączane automatycznie.
</Info>

Szczegółowe informacje o działaniu wyszukiwania, opcjach strojenia i konfiguracji dostawców znajdziesz w [Memory Search](/pl/concepts/memory-search).

## Backendy pamięci

<CardGroup cols={3}>
<Card title="Wbudowany (domyślny)" icon="database" href="/pl/concepts/memory-builtin">
Oparty na SQLite. Działa od razu z wyszukiwaniem słów kluczowych, podobieństwem wektorowym i wyszukiwaniem hybrydowym. Bez dodatkowych zależności.
</Card>
<Card title="QMD" icon="search" href="/pl/concepts/memory-qmd">
Lokalny sidecar z rerankingiem, rozszerzaniem zapytań i możliwością indeksowania katalogów poza obszarem roboczym.
</Card>
<Card title="Honcho" icon="brain" href="/pl/concepts/memory-honcho">
Natywna dla AI pamięć między sesjami z modelowaniem użytkownika, wyszukiwaniem semantycznym i świadomością wielu agentów. Instalacja Pluginu.
</Card>
</CardGroup>

## Warstwa wiki wiedzy

<CardGroup cols={1}>
<Card title="Memory Wiki" icon="book" href="/pl/plugins/memory-wiki">
Kompiluje trwałą pamięć do skarbca wiki bogatego w pochodzenie, z twierdzeniami, pulpitami, trybem mostka i przepływami pracy przyjaznymi dla Obsidian.
</Card>
</CardGroup>

## Automatyczny zapis pamięci

Zanim [Compaction](/pl/concepts/compaction) podsumuje Twoją rozmowę, OpenClaw uruchamia cichą turę, która przypomina agentowi o zapisaniu ważnego kontekstu do plików pamięci. Jest to włączone domyślnie — nie musisz niczego konfigurować.

<Tip>
Automatyczny zapis pamięci zapobiega utracie kontekstu podczas Compaction. Jeśli agent ma w rozmowie ważne fakty, które nie zostały jeszcze zapisane do pliku, zostaną zapisane automatycznie przed utworzeniem podsumowania.
</Tip>

## Dreaming

Dreaming to opcjonalny proces konsolidacji pamięci działający w tle. Zbiera sygnały krótkoterminowe, ocenia kandydatów i promuje do pamięci długoterminowej (`MEMORY.md`) tylko zakwalifikowane elementy.

Został zaprojektowany tak, aby utrzymywać wysoki stosunek sygnału do szumu w pamięci długoterminowej:

- **Dobrowolny**: domyślnie wyłączony.
- **Harmonogramowany**: po włączeniu `memory-core` automatycznie zarządza jednym cyklicznym zadaniem Cron dla pełnego przebiegu Dreaming.
- **Progowy**: promocje muszą przejść progi punktacji, częstotliwości przypomnień i różnorodności zapytań.
- **Możliwy do przeglądu**: podsumowania faz i wpisy dziennika są zapisywane do `DREAMS.md` do przeglądu przez człowieka.

Informacje o zachowaniu faz, sygnałach punktacji i szczegółach Dziennika snów znajdziesz w [Dreaming](/pl/concepts/dreaming).

## Ugruntowany backfill i promocja na żywo

System Dreaming ma teraz dwa ściśle powiązane tory przeglądu:

- **Live dreaming** działa na podstawie krótkoterminowego magazynu Dreaming w `memory/.dreams/` i właśnie z niego normalna głęboka faza korzysta przy podejmowaniu decyzji, co może zostać przeniesione do `MEMORY.md`.
- **Grounded backfill** odczytuje historyczne notatki `memory/YYYY-MM-DD.md` jako samodzielne pliki dzienne i zapisuje uporządkowane wyniki przeglądu do `DREAMS.md`.

Grounded backfill jest przydatny, gdy chcesz ponownie przeanalizować starsze notatki i sprawdzić, co system uznaje za trwałe, bez ręcznej edycji `MEMORY.md`.

Gdy użyjesz:

```bash
openclaw memory rem-backfill --path ./memory --stage-short-term
```

ugruntowani kandydaci trwałej pamięci nie są promowani bezpośrednio. Zamiast tego są etapowani w tym samym krótkoterminowym magazynie Dreaming, z którego korzysta już zwykła głęboka faza. Oznacza to, że:

- `DREAMS.md` pozostaje powierzchnią przeglądu dla człowieka.
- magazyn krótkoterminowy pozostaje powierzchnią rankingu dla maszyny.
- `MEMORY.md` nadal jest zapisywany wyłącznie przez głęboką promocję.

Jeśli uznasz, że to ponowne przetwarzanie nie było przydatne, możesz usunąć etapowane artefakty bez naruszania zwykłych wpisów dziennika ani normalnego stanu przypominania:

```bash
openclaw memory rem-backfill --rollback
openclaw memory rem-backfill --rollback-short-term
```

## CLI

```bash
openclaw memory status          # Sprawdź stan indeksu i dostawcę
openclaw memory search "query"  # Wyszukuj z wiersza poleceń
openclaw memory index --force   # Odbuduj indeks
```

## Dalsza lektura

- [Builtin Memory Engine](/pl/concepts/memory-builtin) — domyślny backend SQLite
- [QMD Memory Engine](/pl/concepts/memory-qmd) — zaawansowany lokalny sidecar
- [Honcho Memory](/pl/concepts/memory-honcho) — natywna dla AI pamięć między sesjami
- [Memory Wiki](/pl/plugins/memory-wiki) — skompilowany skarbiec wiedzy i narzędzia natywne dla wiki
- [Memory Search](/pl/concepts/memory-search) — potok wyszukiwania, dostawcy i strojenie
- [Dreaming](/pl/concepts/dreaming) — promocja w tle
  z krótkoterminowego przypominania do pamięci długoterminowej
- [Memory configuration reference](/pl/reference/memory-config) — wszystkie opcje konfiguracji
- [Compaction](/pl/concepts/compaction) — jak Compaction współdziała z pamięcią
