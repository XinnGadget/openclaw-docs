---
read_when:
    - Edytowanie tekstu promptu systemowego, listy narzędzi lub sekcji czasu/Heartbeat
    - Zmiana zachowania bootstrapu przestrzeni roboczej lub wstrzykiwania Skills
summary: Co zawiera prompt systemowy OpenClaw i jak jest składany
title: Prompt systemowy
x-i18n:
    generated_at: "2026-04-15T19:41:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: c740e4646bc4980567338237bfb55126af0df72499ca00a48e4848d9a3608ab4
    source_path: concepts/system-prompt.md
    workflow: 15
---

# Prompt systemowy

OpenClaw tworzy niestandardowy prompt systemowy dla każdego uruchomienia agenta. Prompt jest **własnością OpenClaw** i nie używa domyślnego promptu `pi-coding-agent`.

Prompt jest składany przez OpenClaw i wstrzykiwany do każdego uruchomienia agenta.

Pluginy dostawców mogą wnosić wskazówki do promptu uwzględniające cache bez zastępowania
pełnego promptu należącego do OpenClaw. Runtime dostawcy może:

- zastąpić mały zestaw nazwanych sekcji rdzeniowych (`interaction_style`,
  `tool_call_style`, `execution_bias`)
- wstrzyknąć **stabilny prefiks** powyżej granicy cache promptu
- wstrzyknąć **dynamiczny sufiks** poniżej granicy cache promptu

Używaj wkładów należących do dostawcy do dostrajania specyficznego dla rodziny modeli. Zachowaj starszą
mutację promptu `before_prompt_build` dla zgodności lub rzeczywiście globalnych zmian promptu, a nie dla zwykłego zachowania dostawcy.

## Struktura

Prompt jest celowo zwięzły i używa stałych sekcji:

- **Tooling**: przypomnienie o źródle prawdy dla narzędzi strukturalnych oraz wskazówki dotyczące użycia narzędzi w runtime.
- **Safety**: krótkie przypomnienie o zabezpieczeniach, aby unikać zachowań dążących do przejęcia kontroli lub omijania nadzoru.
- **Skills** (gdy dostępne): informuje model, jak na żądanie ładować instrukcje umiejętności.
- **OpenClaw Self-Update**: jak bezpiecznie sprawdzać konfigurację za pomocą
  `config.schema.lookup`, modyfikować konfigurację za pomocą `config.patch`, zastępować pełną
  konfigurację za pomocą `config.apply` i uruchamiać `update.run` tylko na wyraźną
  prośbę użytkownika. Narzędzie `gateway`, dostępne tylko dla właściciela, również odmawia przepisywania
  `tools.exec.ask` / `tools.exec.security`, w tym starszych aliasów `tools.bash.*`,
  które są normalizowane do tych chronionych ścieżek exec.
- **Workspace**: katalog roboczy (`agents.defaults.workspace`).
- **Documentation**: lokalna ścieżka do dokumentacji OpenClaw (repozytorium lub pakiet npm) i kiedy ją czytać.
- **Workspace Files (injected)**: wskazuje, że pliki bootstrap są dołączone poniżej.
- **Sandbox** (gdy włączony): wskazuje środowisko sandbox, ścieżki sandboxa i to, czy podwyższony exec jest dostępny.
- **Current Date & Time**: lokalny czas użytkownika, strefa czasowa i format czasu.
- **Reply Tags**: opcjonalna składnia tagów odpowiedzi dla obsługiwanych dostawców.
- **Heartbeats**: prompt heartbeat i zachowanie potwierdzenia, gdy heartbeat jest włączony dla domyślnego agenta.
- **Runtime**: host, system operacyjny, node, model, katalog główny repozytorium (gdy wykryty), poziom myślenia (jedna linia).
- **Reasoning**: bieżący poziom widoczności + podpowiedź przełączania `/reasoning`.

Sekcja Tooling zawiera również wskazówki runtime dla długotrwałej pracy:

- używaj Cron do przyszłych działań następczych (`check back later`, przypomnienia, zadania cykliczne)
  zamiast pętli uśpienia `exec`, trików opóźnień `yieldMs` lub powtarzanego odpytywania `process`
- używaj `exec` / `process` tylko dla poleceń, które uruchamiają się teraz i nadal działają
  w tle
- gdy włączone jest automatyczne wybudzanie po zakończeniu, uruchom polecenie raz i polegaj na
  mechanizmie wybudzania opartym na push, gdy wygeneruje wynik lub zakończy się błędem
- używaj `process` do logów, statusu, wejścia lub interwencji, gdy musisz
  sprawdzić działające polecenie
- jeśli zadanie jest większe, preferuj `sessions_spawn`; zakończenie sub-agentów działa
  w oparciu o push i jest automatycznie ogłaszane z powrotem do żądającego
- nie odpytywuj `subagents list` / `sessions_list` w pętli tylko po to, by czekać na
  zakończenie

Gdy eksperymentalne narzędzie `update_plan` jest włączone, Tooling informuje również model,
aby używać go tylko do nietrywialnej pracy wieloetapowej, utrzymywać dokładnie jeden krok
`in_progress` i unikać powtarzania całego planu po każdej aktualizacji.

Zabezpieczenia bezpieczeństwa w prompcie systemowym mają charakter doradczy. Kierują zachowaniem modelu, ale nie wymuszają polityki. Do twardego egzekwowania używaj polityki narzędzi, zatwierdzeń exec, sandboxingu i list dozwolonych kanałów; operatorzy mogą je celowo wyłączyć.

Na kanałach z natywnymi kartami/przyciskami zatwierdzania prompt runtime informuje teraz
agenta, aby najpierw polegał na tym natywnym interfejsie zatwierdzania. Powinien uwzględniać ręczne
polecenie `/approve` tylko wtedy, gdy wynik narzędzia mówi, że zatwierdzenia w czacie są niedostępne lub
ręczne zatwierdzenie jest jedyną drogą.

## Tryby promptu

OpenClaw może renderować mniejsze prompty systemowe dla sub-agentów. Runtime ustawia
`promptMode` dla każdego uruchomienia (nie jest to konfiguracja widoczna dla użytkownika):

- `full` (domyślnie): zawiera wszystkie powyższe sekcje.
- `minimal`: używany dla sub-agentów; pomija **Skills**, **Memory Recall**, **OpenClaw
  Self-Update**, **Model Aliases**, **User Identity**, **Reply Tags**,
  **Messaging**, **Silent Replies** i **Heartbeats**. Tooling, **Safety**,
  Workspace, Sandbox, Current Date & Time (gdy znane), Runtime i wstrzyknięty
  kontekst pozostają dostępne.
- `none`: zwraca tylko podstawową linię tożsamości.

Gdy `promptMode=minimal`, dodatkowe wstrzyknięte prompty są oznaczane jako **Subagent
Context** zamiast **Group Chat Context**.

## Wstrzykiwanie bootstrapu przestrzeni roboczej

Pliki bootstrap są przycinane i dołączane w sekcji **Project Context**, aby model widział kontekst tożsamości i profilu bez potrzeby ich jawnego odczytu:

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md` (tylko w zupełnie nowych przestrzeniach roboczych)
- `MEMORY.md`, jeśli istnieje, w przeciwnym razie `memory.md` jako zapasowy wariant pisany małymi literami

Wszystkie te pliki są **wstrzykiwane do okna kontekstowego** przy każdej turze, chyba że
obowiązuje bramka specyficzna dla danego pliku. `HEARTBEAT.md` jest pomijany przy zwykłych uruchomieniach, gdy
heartbeat jest wyłączony dla domyślnego agenta lub
`agents.defaults.heartbeat.includeSystemPromptSection` ma wartość false. Utrzymuj wstrzykiwane
pliki zwięzłe — szczególnie `MEMORY.md`, który może z czasem rosnąć i prowadzić do
nieoczekiwanie wysokiego użycia kontekstu oraz częstszej Compaction.

> **Uwaga:** codzienne pliki `memory/*.md` **nie** są częścią zwykłego bootstrapowego
> Project Context. W zwykłych turach są odczytywane na żądanie przez
> narzędzia `memory_search` i `memory_get`, więc nie liczą się do
> okna kontekstowego, chyba że model jawnie je odczyta. Wyjątkiem są zwykłe tury `/new` i
> `/reset`: runtime może dołączyć ostatnią codzienną pamięć jako jednorazowy blok
> kontekstu startowego dla tej pierwszej tury.

Duże pliki są przycinane z markerem. Maksymalny rozmiar na plik jest kontrolowany przez
`agents.defaults.bootstrapMaxChars` (domyślnie: 20000). Łączna wstrzyknięta zawartość bootstrapu
we wszystkich plikach jest ograniczona przez `agents.defaults.bootstrapTotalMaxChars`
(domyślnie: 150000). Brakujące pliki wstrzykują krótki znacznik brakującego pliku. Gdy dochodzi do przycięcia,
OpenClaw może wstrzyknąć blok ostrzeżenia w Project Context; kontroluje się to przez
`agents.defaults.bootstrapPromptTruncationWarning` (`off`, `once`, `always`;
domyślnie: `once`).

Sesje sub-agentów wstrzykują tylko `AGENTS.md` i `TOOLS.md` (pozostałe pliki bootstrap
są odfiltrowywane, aby zachować mały kontekst sub-agenta).

Wewnętrzne hooki mogą przechwycić ten krok przez `agent:bootstrap`, aby mutować lub zastępować
wstrzyknięte pliki bootstrap (na przykład zamieniając `SOUL.md` na alternatywną personę).

Jeśli chcesz, aby agent brzmiał mniej generycznie, zacznij od
[Przewodnika osobowości SOUL.md](/pl/concepts/soul).

Aby sprawdzić, jaki wkład ma każdy wstrzyknięty plik (surowy vs wstrzyknięty, przycięcie oraz narzut schematu narzędzi), użyj `/context list` lub `/context detail`. Zobacz [Context](/pl/concepts/context).

## Obsługa czasu

Prompt systemowy zawiera dedykowaną sekcję **Current Date & Time**, gdy znana jest
strefa czasowa użytkownika. Aby zachować stabilność cache promptu, zawiera teraz tylko
**strefę czasową** (bez dynamicznego zegara ani formatu czasu).

Użyj `session_status`, gdy agent potrzebuje bieżącego czasu; karta statusu
zawiera wiersz znacznika czasu. To samo narzędzie może opcjonalnie ustawić
nadpisanie modelu dla sesji (`model=default` je czyści).

Konfiguracja:

- `agents.defaults.userTimezone`
- `agents.defaults.timeFormat` (`auto` | `12` | `24`)

Pełne szczegóły zachowania znajdziesz w [Date & Time](/pl/date-time).

## Skills

Gdy istnieją kwalifikujące się Skills, OpenClaw wstrzykuje zwartą **listę dostępnych Skills**
(`formatSkillsForPrompt`), która zawiera **ścieżkę pliku** dla każdego Skill. Prompt
nakazuje modelowi użyć `read`, aby wczytać SKILL.md z podanej
lokalizacji (przestrzeń robocza, zarządzana lub dołączona). Jeśli nie ma kwalifikujących się Skills, sekcja
Skills jest pomijana.

Kwalifikacja obejmuje bramki metadanych Skill, kontrole środowiska runtime/konfiguracji
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

Pozwala to zachować mały podstawowy prompt, a jednocześnie umożliwia ukierunkowane użycie Skills.

Budżet listy Skills należy do podsystemu Skills:

- Globalna wartość domyślna: `skills.limits.maxSkillsPromptChars`
- Nadpisanie dla agenta: `agents.list[].skillsLimits.maxSkillsPromptChars`

Ogólne ograniczone fragmenty runtime używają innej powierzchni:

- `agents.defaults.contextLimits.*`
- `agents.list[].contextLimits.*`

Ten podział utrzymuje rozmiar Skills oddzielnie od rozmiaru odczytu/wstrzykiwania runtime, takiego jak
`memory_get`, wyniki narzędzi na żywo i odświeżenia AGENTS.md po Compaction.

## Documentation

Gdy to możliwe, prompt systemowy zawiera sekcję **Documentation**, która wskazuje
lokalny katalog dokumentacji OpenClaw (albo `docs/` w przestrzeni roboczej repozytorium, albo dokumentację
dołączonego pakietu npm) oraz wspomina też o publicznym mirrorze, repozytorium źródłowym, społecznościowym Discordzie i
ClawHub ([https://clawhub.ai](https://clawhub.ai)) do odkrywania Skills. Prompt instruuje model, aby najpierw konsultował lokalną dokumentację
w sprawach zachowania, poleceń, konfiguracji lub architektury OpenClaw oraz aby
samodzielnie uruchamiał `openclaw status`, kiedy to możliwe (prosząc użytkownika tylko wtedy, gdy nie ma dostępu).
