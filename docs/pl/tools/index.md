---
read_when:
    - Chcesz zrozumieć, jakie narzędzia udostępnia OpenClaw
    - Musisz skonfigurować narzędzia, zezwolić na nie lub je zablokować
    - Decydujesz między narzędziami wbudowanymi, Skills i wtyczkami
summary: 'Przegląd narzędzi i wtyczek OpenClaw: co agent potrafi robić i jak go rozszerzać'
title: Narzędzia i wtyczki
x-i18n:
    generated_at: "2026-04-06T03:13:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: b2371239316997b0fe389bfa2ec38404e1d3e177755ad81ff8035ac583d9adeb
    source_path: tools/index.md
    workflow: 15
---

# Narzędzia i wtyczki

Wszystko, co agent robi poza generowaniem tekstu, odbywa się przez **narzędzia**.
Narzędzia to sposób, w jaki agent odczytuje pliki, uruchamia polecenia, przegląda sieć, wysyła
wiadomości i wchodzi w interakcję z urządzeniami.

## Narzędzia, Skills i wtyczki

OpenClaw ma trzy współpracujące ze sobą warstwy:

<Steps>
  <Step title="Narzędzia to to, co wywołuje agent">
    Narzędzie to typowana funkcja, którą agent może wywołać (np. `exec`, `browser`,
    `web_search`, `message`). OpenClaw dostarcza zestaw **wbudowanych narzędzi**, a
    wtyczki mogą rejestrować dodatkowe.

    Agent widzi narzędzia jako ustrukturyzowane definicje funkcji wysyłane do API modelu.

  </Step>

  <Step title="Skills uczą agenta kiedy i jak">
    Skill to plik Markdown (`SKILL.md`) wstrzykiwany do system promptu.
    Skills dostarczają agentowi kontekstu, ograniczeń i wskazówek krok po kroku
    dotyczących skutecznego używania narzędzi. Skills znajdują się w twoim workspace, w folderach współdzielonych
    albo są dostarczane wewnątrz wtyczek.

    [Dokumentacja Skills](/pl/tools/skills) | [Tworzenie Skills](/pl/tools/creating-skills)

  </Step>

  <Step title="Wtyczki pakują wszystko razem">
    Wtyczka to pakiet, który może zarejestrować dowolną kombinację capabilities:
    kanały, dostawców modeli, narzędzia, Skills, mowę, transkrypcję realtime,
    głos realtime, rozumienie multimediów, generowanie obrazów, generowanie wideo,
    web fetch, web search i inne. Niektóre wtyczki są **rdzeniowe** (dostarczane z
    OpenClaw), a inne są **zewnętrzne** (publikowane na npm przez społeczność).

    [Instalowanie i konfigurowanie wtyczek](/pl/tools/plugin) | [Stwórz własną](/pl/plugins/building-plugins)

  </Step>
</Steps>

## Wbudowane narzędzia

Te narzędzia są dostarczane z OpenClaw i są dostępne bez instalowania jakichkolwiek wtyczek:

| Narzędzie                                  | Co robi                                                               | Strona                                      |
| ------------------------------------------ | --------------------------------------------------------------------- | ------------------------------------------- |
| `exec` / `process`                         | Uruchamia polecenia powłoki, zarządza procesami w tle                 | [Exec](/pl/tools/exec)                         |
| `code_execution`                           | Uruchamia izolowaną zdalną analizę w Pythonie                         | [Code Execution](/pl/tools/code-execution)     |
| `browser`                                  | Steruje przeglądarką Chromium (nawigacja, kliknięcia, zrzuty ekranu)  | [Browser](/pl/tools/browser)                   |
| `web_search` / `x_search` / `web_fetch`    | Przeszukuje sieć, przeszukuje posty X, pobiera treść stron            | [Web](/pl/tools/web)                           |
| `read` / `write` / `edit`                  | Operacje wejścia/wyjścia na plikach w workspace                       |                                             |
| `apply_patch`                              | Wielohunkowe patche plików                                            | [Apply Patch](/pl/tools/apply-patch)           |
| `message`                                  | Wysyła wiadomości przez wszystkie kanały                              | [Agent Send](/pl/tools/agent-send)             |
| `canvas`                                   | Steruje node Canvas (present, eval, snapshot)                         |                                             |
| `nodes`                                    | Wykrywa sparowane urządzenia i kieruje działania do nich              |                                             |
| `cron` / `gateway`                         | Zarządza zaplanowanymi zadaniami; inspektuje, patchuje, restartuje lub aktualizuje gateway |                                             |
| `image` / `image_generate`                 | Analizuje lub generuje obrazy                                         | [Image Generation](/pl/tools/image-generation) |
| `music_generate`                           | Generuje utwory muzyczne                                              | [Music Generation](/tools/music-generation) |
| `video_generate`                           | Generuje wideo                                                        | [Video Generation](/tools/video-generation) |
| `tts`                                      | Jednorazowa konwersja tekstu na mowę                                  | [TTS](/pl/tools/tts)                           |
| `sessions_*` / `subagents` / `agents_list` | Zarządzanie sesjami, stan i orkiestracja podagentów                   | [Sub-agents](/pl/tools/subagents)              |
| `session_status`                           | Lekki odczyt w stylu `/status` i nadpisanie modelu dla sesji          | [Session Tools](/pl/concepts/session-tool)     |

Do pracy z obrazami używaj `image` do analizy oraz `image_generate` do generowania lub edycji. Jeśli kierujesz żądanie do `openai/*`, `google/*`, `fal/*` albo innego niedomyślnego dostawcy obrazów, najpierw skonfiguruj auth/klucz API tego dostawcy.

Do pracy z muzyką używaj `music_generate`. Jeśli kierujesz żądanie do `google/*`, `minimax/*` albo innego niedomyślnego dostawcy muzyki, najpierw skonfiguruj auth/klucz API tego dostawcy.

Do pracy z wideo używaj `video_generate`. Jeśli kierujesz żądanie do `qwen/*` albo innego niedomyślnego dostawcy wideo, najpierw skonfiguruj auth/klucz API tego dostawcy.

Do generowania audio sterowanego workflow używaj `music_generate`, gdy wtyczka taka jak
ComfyUI je rejestruje. To jest oddzielne od `tts`, które oznacza text-to-speech.

`session_status` to lekkie narzędzie status/odczyt w grupie sesji.
Odpowiada na pytania w stylu `/status` dotyczące bieżącej sesji i może
opcjonalnie ustawić nadpisanie modelu dla danej sesji; `model=default` czyści to
nadpisanie. Podobnie jak `/status`, może uzupełniać rzadkie liczniki tokenów/cache oraz
etykietę aktywnego modelu runtime na podstawie najnowszego wpisu usage w transkrypcie.

`gateway` to narzędzie runtime tylko dla właściciela do operacji na gateway:

- `config.schema.lookup` dla jednego poddrzewa konfiguracji o określonej ścieżce przed edycją
- `config.get` dla bieżącej migawki konfiguracji + hasha
- `config.patch` dla częściowych aktualizacji konfiguracji z restartem
- `config.apply` tylko do pełnego zastąpienia konfiguracji
- `update.run` do jawnej samoaktualizacji + restartu

W przypadku zmian częściowych preferuj `config.schema.lookup`, a następnie `config.patch`. Używaj
`config.apply` tylko wtedy, gdy celowo zastępujesz całą konfigurację.
Narzędzie odmawia również zmiany `tools.exec.ask` lub `tools.exec.security`;
starsze aliasy `tools.bash.*` są normalizowane do tych samych chronionych ścieżek exec.

### Narzędzia dostarczane przez wtyczki

Wtyczki mogą rejestrować dodatkowe narzędzia. Kilka przykładów:

- [Lobster](/pl/tools/lobster) — typowane środowisko wykonawcze workflow z możliwością wznawiania zatwierdzeń
- [LLM Task](/pl/tools/llm-task) — krok LLM tylko-JSON dla ustrukturyzowanego wyjścia
- [Music Generation](/tools/music-generation) — współdzielone narzędzie `music_generate` z dostawcami opartymi na workflow
- [Diffs](/pl/tools/diffs) — przeglądarka i renderer diffów
- [OpenProse](/pl/prose) — orkiestracja workflow z podejściem Markdown-first

## Konfiguracja narzędzi

### Listy zezwalania i blokowania

Kontroluj, które narzędzia agent może wywoływać, za pomocą `tools.allow` / `tools.deny` w
konfiguracji. Blokowanie zawsze ma pierwszeństwo przed zezwoleniem.

```json5
{
  tools: {
    allow: ["group:fs", "browser", "web_search"],
    deny: ["exec"],
  },
}
```

### Profile narzędzi

`tools.profile` ustawia bazową allowlistę przed zastosowaniem `allow`/`deny`.
Nadpisanie per agent: `agents.list[].tools.profile`.

| Profil      | Co obejmuje                                                                                                                                      |
| ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| `full`      | Bez ograniczeń (to samo co brak ustawienia)                                                                                                      |
| `coding`    | `group:fs`, `group:runtime`, `group:web`, `group:sessions`, `group:memory`, `cron`, `image`, `image_generate`, `music_generate`, `video_generate` |
| `messaging` | `group:messaging`, `sessions_list`, `sessions_history`, `sessions_send`, `session_status`                                                       |
| `minimal`   | Tylko `session_status`                                                                                                                           |

### Grupy narzędzi

Używaj skrótów `group:*` w listach allow/deny:

| Grupa              | Narzędzia                                                                                              |
| ------------------ | ------------------------------------------------------------------------------------------------------ |
| `group:runtime`    | exec, process, code_execution (`bash` jest akceptowany jako alias dla `exec`)                         |
| `group:fs`         | read, write, edit, apply_patch                                                                         |
| `group:sessions`   | sessions_list, sessions_history, sessions_send, sessions_spawn, sessions_yield, subagents, session_status |
| `group:memory`     | memory_search, memory_get                                                                              |
| `group:web`        | web_search, x_search, web_fetch                                                                        |
| `group:ui`         | browser, canvas                                                                                        |
| `group:automation` | cron, gateway                                                                                          |
| `group:messaging`  | message                                                                                                |
| `group:nodes`      | nodes                                                                                                  |
| `group:agents`     | agents_list                                                                                            |
| `group:media`      | image, image_generate, music_generate, video_generate, tts                                             |
| `group:openclaw`   | Wszystkie wbudowane narzędzia OpenClaw (bez narzędzi wtyczek)                                          |

`seessions_history` zwraca ograniczony widok odtworzenia z filtrami bezpieczeństwa. Usuwa
tagi thinking, strukturę `<relevant-memories>`, payloady XML wywołań narzędzi w zwykłym tekście
(w tym `<tool_call>...</tool_call>`,
`<function_call>...</function_call>`, `<tool_calls>...</tool_calls>`,
`<function_calls>...</function_calls>` oraz obcięte bloki wywołań narzędzi),
zdegradowaną strukturę wywołań narzędzi, wyciekłe tokeny sterujące modelem ASCII/full-width
oraz nieprawidłowy XML wywołań narzędzi MiniMax z tekstu asystenta, a następnie stosuje
redakcję/obcinanie i ewentualne placeholders dla zbyt dużych wierszy zamiast działać
jak surowy zrzut transkryptu.

### Ograniczenia specyficzne dla dostawcy

Użyj `tools.byProvider`, aby ograniczyć narzędzia dla określonych dostawców bez
zmiany globalnych ustawień domyślnych:

```json5
{
  tools: {
    profile: "coding",
    byProvider: {
      "google-antigravity": { profile: "minimal" },
    },
  },
}
```
