---
read_when:
    - Edytowanie tekstu promptu systemowego, listy narzędzi lub sekcji czasu/Heartbeat
    - Zmiana zachowania bootstrapu obszaru roboczego lub wstrzykiwania Skills
summary: Co zawiera prompt systemowy OpenClaw i jak jest składany
title: Prompt systemowy
x-i18n:
    generated_at: "2026-04-12T09:33:35Z"
    model: gpt-5.4
    provider: openai
    source_hash: 057f01aac51f7737b5223f61f5d55e552d9011232aebb130426e269d8f6c257f
    source_path: concepts/system-prompt.md
    workflow: 15
---

# Prompt systemowy

OpenClaw tworzy niestandardowy prompt systemowy dla każdego uruchomienia agenta. Prompt jest **własnością OpenClaw** i nie używa domyślnego promptu `pi-coding-agent`.

Prompt jest składany przez OpenClaw i wstrzykiwany do każdego uruchomienia agenta.

Pluginy dostawców mogą wnosić wskazówki do promptu uwzględniające cache bez zastępowania
całego promptu należącego do OpenClaw. Runtime dostawcy może:

- zastąpić niewielki zestaw nazwanych sekcji rdzeniowych (`interaction_style`,
  `tool_call_style`, `execution_bias`)
- wstrzyknąć **stabilny prefiks** powyżej granicy cache promptu
- wstrzyknąć **dynamiczny sufiks** poniżej granicy cache promptu

Używaj wkładów należących do dostawcy do strojenia specyficznego dla rodziny modeli. Zachowaj starszą
mutację promptu `before_prompt_build` dla kompatybilności lub rzeczywiście globalnych zmian promptu,
a nie dla zwykłego zachowania dostawcy.

## Struktura

Prompt jest celowo zwięzły i używa stałych sekcji:

- **Narzędzia**: przypomnienie o źródle prawdy dla narzędzi strukturalnych oraz wskazówki dotyczące użycia narzędzi w runtime.
- **Bezpieczeństwo**: krótkie przypomnienie o zabezpieczeniach, aby unikać zachowań dążących do zdobycia władzy lub obchodzenia nadzoru.
- **Skills** (gdy dostępne): informuje model, jak ładować instrukcje Skills na żądanie.
- **Samodzielna aktualizacja OpenClaw**: jak bezpiecznie sprawdzać konfigurację za pomocą
  `config.schema.lookup`, poprawiać konfigurację za pomocą `config.patch`, zastępować całą
  konfigurację za pomocą `config.apply` oraz uruchamiać `update.run` wyłącznie na wyraźne żądanie
  użytkownika. Narzędzie `gateway`, dostępne tylko dla właściciela, również odmawia przepisywania
  `tools.exec.ask` / `tools.exec.security`, w tym starszych aliasów `tools.bash.*`,
  które normalizują się do tych chronionych ścieżek exec.
- **Obszar roboczy**: katalog roboczy (`agents.defaults.workspace`).
- **Dokumentacja**: lokalna ścieżka do dokumentacji OpenClaw (repozytorium lub pakiet npm) oraz kiedy ją czytać.
- **Pliki obszaru roboczego (wstrzyknięte)**: wskazuje, że pliki bootstrapu są dołączone poniżej.
- **Sandbox** (gdy włączony): wskazuje runtime w piaskownicy, ścieżki sandboxa i to, czy dostępne jest podwyższone exec.
- **Bieżąca data i godzina**: lokalny czas użytkownika, strefa czasowa i format czasu.
- **Tagi odpowiedzi**: opcjonalna składnia tagów odpowiedzi dla obsługiwanych dostawców.
- **Heartbeat**: prompt Heartbeat i zachowanie potwierdzeń, gdy Heartbeat jest włączony dla domyślnego agenta.
- **Runtime**: host, system operacyjny, node, model, katalog główny repozytorium (jeśli wykryto), poziom myślenia (jedna linia).
- **Rozumowanie**: bieżący poziom widoczności + wskazówka przełączania `/reasoning`.

Sekcja Narzędzia zawiera również wskazówki runtime dotyczące długotrwałej pracy:

- używaj Cron do przyszłych działań następczych (`check back later`, przypomnienia, zadania cykliczne)
  zamiast pętli `sleep` w `exec`, sztuczek opóźniających `yieldMs` lub powtarzanego
  odpytywania `process`
- używaj `exec` / `process` tylko do poleceń, które uruchamiają się teraz i nadal działają
  w tle
- gdy włączone jest automatyczne wybudzanie po zakończeniu, uruchom polecenie tylko raz i polegaj na
  ścieżce wybudzania opartej na push, gdy zwróci dane wyjściowe lub zakończy się błędem
- używaj `process` do logów, statusu, wejścia lub interwencji, gdy musisz
  sprawdzić działające polecenie
- jeśli zadanie jest większe, preferuj `sessions_spawn`; zakończenie podagenta jest
  oparte na push i jest automatycznie anonsowane z powrotem do zlecającego
- nie odpytywaj w pętli `subagents list` / `sessions_list` tylko po to, aby czekać na
  zakończenie

Gdy eksperymentalne narzędzie `update_plan` jest włączone, sekcja Narzędzia mówi również
modelowi, aby używał go tylko do nietrywialnej pracy wieloetapowej, utrzymywał dokładnie jeden krok
`in_progress` i unikał powtarzania całego planu po każdej aktualizacji.

Zabezpieczenia bezpieczeństwa w prompcie systemowym mają charakter doradczy. Kierują zachowaniem modelu, ale nie egzekwują zasad. Do twardego egzekwowania używaj polityki narzędzi, zatwierdzeń exec, sandboxingu i list dozwolonych kanałów; operatorzy mogą je celowo wyłączyć.

W kanałach z natywnymi kartami/przyciskami zatwierdzeń prompt runtime instruuje teraz
agenta, aby najpierw polegał na tym natywnym interfejsie zatwierdzania. Powinien dołączać ręczne
polecenie `/approve` tylko wtedy, gdy wynik narzędzia mówi, że zatwierdzenia na czacie są niedostępne
albo ręczne zatwierdzenie jest jedyną ścieżką.

## Tryby promptu

OpenClaw może renderować mniejsze prompty systemowe dla podagentów. Runtime ustawia
`promptMode` dla każdego uruchomienia (nie jest to konfiguracja widoczna dla użytkownika):

- `full` (domyślnie): zawiera wszystkie sekcje powyżej.
- `minimal`: używany dla podagentów; pomija **Skills**, **Przywoływanie pamięci**, **Samodzielną aktualizację OpenClaw**, **Aliasy modeli**, **Tożsamość użytkownika**, **Tagi odpowiedzi**,
  **Wiadomości**, **Ciche odpowiedzi** i **Heartbeat**. Narzędzia, **Bezpieczeństwo**,
  Obszar roboczy, Sandbox, Bieżąca data i godzina (gdy znane), Runtime oraz wstrzyknięty
  kontekst pozostają dostępne.
- `none`: zwraca tylko bazową linię tożsamości.

Gdy `promptMode=minimal`, dodatkowe wstrzyknięte prompty są oznaczane jako **Kontekst
podagenta** zamiast **Kontekst czatu grupowego**.

## Wstrzykiwanie bootstrapu obszaru roboczego

Pliki bootstrapu są przycinane i dołączane w sekcji **Kontekst projektu**, aby model widział kontekst tożsamości i profilu bez potrzeby jawnego odczytu:

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md` (tylko w zupełnie nowych obszarach roboczych)
- `MEMORY.md` jeśli istnieje, w przeciwnym razie `memory.md` jako zapasowy wariant małymi literami

Wszystkie te pliki są **wstrzykiwane do okna kontekstowego** przy każdej turze, chyba że
obowiązuje bramka specyficzna dla pliku. `HEARTBEAT.md` jest pomijany przy zwykłych uruchomieniach, gdy
Heartbeat jest wyłączony dla domyślnego agenta albo
`agents.defaults.heartbeat.includeSystemPromptSection` ma wartość false. Utrzymuj wstrzykiwane
pliki zwięzłe — szczególnie `MEMORY.md`, który może z czasem rosnąć i prowadzić do
nieoczekiwanie wysokiego użycia kontekstu oraz częstszej Compaction.

> **Uwaga:** dzienne pliki `memory/*.md` **nie** są częścią zwykłego bootstrapowego
> Kontekstu projektu. W zwykłych turach są dostępne na żądanie przez narzędzia
> `memory_search` i `memory_get`, więc nie zajmują miejsca w oknie
> kontekstowym, chyba że model jawnie je odczyta. Wyjątkiem są zwykłe tury `/new` i
> `/reset`: runtime może dodać na początku ostatnią dzienną pamięć jako jednorazowy blok
> kontekstu startowego dla tej pierwszej tury.

Duże pliki są obcinane ze znacznikiem. Maksymalny rozmiar na plik jest kontrolowany przez
`agents.defaults.bootstrapMaxChars` (domyślnie: 20000). Całkowita wstrzyknięta zawartość bootstrapu
we wszystkich plikach jest ograniczona przez `agents.defaults.bootstrapTotalMaxChars`
(domyślnie: 150000). Brakujące pliki wstrzykują krótki znacznik brakującego pliku. Gdy dochodzi do obcięcia,
OpenClaw może wstrzyknąć blok ostrzeżenia w Kontekście projektu; kontroluje to
`agents.defaults.bootstrapPromptTruncationWarning` (`off`, `once`, `always`;
domyślnie: `once`).

Sesje podagentów wstrzykują tylko `AGENTS.md` i `TOOLS.md` (pozostałe pliki bootstrapu
są odfiltrowywane, aby zachować mały kontekst podagenta).

Wewnętrzne hooki mogą przechwycić ten krok przez `agent:bootstrap`, aby modyfikować lub zastępować
wstrzykiwane pliki bootstrapu (na przykład zamieniając `SOUL.md` na alternatywną personę).

Jeśli chcesz, aby agent brzmiał mniej generycznie, zacznij od
[Przewodnika osobowości SOUL.md](/pl/concepts/soul).

Aby sprawdzić, jaki wkład ma każdy wstrzyknięty plik (surowy vs wstrzyknięty, obcięcie oraz narzut schematu narzędzi), użyj `/context list` lub `/context detail`. Zobacz [Kontekst](/pl/concepts/context).

## Obsługa czasu

Prompt systemowy zawiera dedykowaną sekcję **Bieżąca data i godzina**, gdy znana jest
strefa czasowa użytkownika. Aby zachować stabilność cache promptu, zawiera ona teraz tylko
**strefę czasową** (bez dynamicznego zegara ani formatu czasu).

Użyj `session_status`, gdy agent potrzebuje bieżącego czasu; karta statusu
zawiera wiersz ze znacznikiem czasu. To samo narzędzie może opcjonalnie ustawić zastąpienie modelu
dla sesji (`model=default` je czyści).

Skonfiguruj za pomocą:

- `agents.defaults.userTimezone`
- `agents.defaults.timeFormat` (`auto` | `12` | `24`)

Pełne szczegóły zachowania znajdziesz w [Data i czas](/pl/date-time).

## Skills

Gdy istnieją kwalifikujące się Skills, OpenClaw wstrzykuje zwartą **listę dostępnych Skills**
(`formatSkillsForPrompt`), która zawiera **ścieżkę do pliku** dla każdej Skills. Prompt
instruuje model, aby użył `read` do wczytania SKILL.md w podanej lokalizacji
(obszar roboczy, zarządzane lub dołączone). Jeśli nie ma kwalifikujących się Skills, sekcja
Skills jest pomijana.

Kwalifikacja obejmuje bramki metadanych Skills, kontrole środowiska/runtime i konfiguracji
oraz efektywną listę dozwolonych Skills agenta, gdy skonfigurowano `agents.defaults.skills` lub
`agents.list[].skills`.

```
<available_skills>
  <skill>
    <name>...</name>
    <description>...</description>
    <location>...</location>
  </skill>
</available_skills>
```

Pozwala to zachować mały bazowy prompt, a jednocześnie nadal umożliwia ukierunkowane użycie Skills.

## Dokumentacja

Gdy jest dostępna, prompt systemowy zawiera sekcję **Dokumentacja**, która wskazuje
lokalny katalog dokumentacji OpenClaw (albo `docs/` w obszarze roboczym repozytorium, albo dokumentację dołączonego
pakietu npm) i wspomina również o publicznym mirrorze, źródłowym repozytorium, społecznościowym Discordzie oraz
ClawHub ([https://clawhub.ai](https://clawhub.ai)) do odkrywania Skills. Prompt instruuje model, aby najpierw sprawdzał lokalną dokumentację
w sprawach zachowania OpenClaw, poleceń, konfiguracji lub architektury oraz aby
sam uruchamiał `openclaw status`, gdy to możliwe (prosząc użytkownika tylko wtedy, gdy nie ma dostępu).
