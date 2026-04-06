---
read_when:
    - Dodajesz lub modyfikujesz CLI modeli (models list/set/scan/aliases/fallbacks)
    - Zmieniasz zachowanie fallbacku modeli lub UX wyboru
    - Aktualizujesz sondy skanowania modeli (narzędzia/obrazy)
summary: 'CLI modeli: lista, ustawianie, aliasy, fallbacki, skanowanie, status'
title: CLI modeli
x-i18n:
    generated_at: "2026-04-06T03:07:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: 299602ccbe0c3d6bbdb2deab22bc60e1300ef6843ed0b8b36be574cc0213c155
    source_path: concepts/models.md
    workflow: 15
---

# CLI modeli

Zobacz [/concepts/model-failover](/pl/concepts/model-failover), aby poznać rotację
profili uwierzytelniania, okresy cooldown i to, jak współgra to z fallbackami.
Szybki przegląd dostawców + przykłady: [/concepts/model-providers](/pl/concepts/model-providers).

## Jak działa wybór modelu

OpenClaw wybiera modele w tej kolejności:

1. **Główny** model (`agents.defaults.model.primary` lub `agents.defaults.model`).
2. **Fallbacki** w `agents.defaults.model.fallbacks` (w podanej kolejności).
3. **Failover uwierzytelniania dostawcy** zachodzi wewnątrz dostawcy przed przejściem do
   następnego modelu.

Powiązane:

- `agents.defaults.models` to allowlista/katalog modeli, których OpenClaw może używać (wraz z aliasami).
- `agents.defaults.imageModel` jest używany **tylko wtedy**, gdy główny model nie może przyjmować obrazów.
- `agents.defaults.pdfModel` jest używany przez narzędzie `pdf`. Jeśli nie jest ustawiony, narzędzie
  przechodzi kolejno do `agents.defaults.imageModel`, a następnie do rozstrzygniętego modelu sesji/domysłnego.
- `agents.defaults.imageGenerationModel` jest używany przez współdzieloną funkcję generowania obrazów. Jeśli nie jest ustawiony, `image_generate` nadal może wywnioskować domyślny model dostawcy na podstawie uwierzytelniania. Najpierw próbuje bieżącego domyślnego dostawcy, a następnie pozostałych zarejestrowanych dostawców generowania obrazów w kolejności identyfikatorów dostawców. Jeśli ustawisz konkretny dostawca/model, skonfiguruj również uwierzytelnianie/klucz API tego dostawcy.
- `agents.defaults.musicGenerationModel` jest używany przez współdzieloną funkcję generowania muzyki. Jeśli nie jest ustawiony, `music_generate` nadal może wywnioskować domyślny model dostawcy na podstawie uwierzytelniania. Najpierw próbuje bieżącego domyślnego dostawcy, a następnie pozostałych zarejestrowanych dostawców generowania muzyki w kolejności identyfikatorów dostawców. Jeśli ustawisz konkretny dostawca/model, skonfiguruj również uwierzytelnianie/klucz API tego dostawcy.
- `agents.defaults.videoGenerationModel` jest używany przez współdzieloną funkcję generowania wideo. Jeśli nie jest ustawiony, `video_generate` nadal może wywnioskować domyślny model dostawcy na podstawie uwierzytelniania. Najpierw próbuje bieżącego domyślnego dostawcy, a następnie pozostałych zarejestrowanych dostawców generowania wideo w kolejności identyfikatorów dostawców. Jeśli ustawisz konkretny dostawca/model, skonfiguruj również uwierzytelnianie/klucz API tego dostawcy.
- Domyślne ustawienia per agent mogą nadpisać `agents.defaults.model` przez `agents.list[].model` wraz z powiązaniami (zobacz [/concepts/multi-agent](/pl/concepts/multi-agent)).

## Szybka polityka modeli

- Ustaw główny model na najsilniejszy model najnowszej generacji, do którego masz dostęp.
- Używaj fallbacków do zadań wrażliwych na koszt/latencję i czatu o mniejszej wadze.
- W przypadku agentów z włączonymi narzędziami lub niezaufanych danych wejściowych unikaj starszych/słabszych klas modeli.

## Onboarding (zalecane)

Jeśli nie chcesz ręcznie edytować konfiguracji, uruchom onboarding:

```bash
openclaw onboard
```

Może on skonfigurować model + uwierzytelnianie dla popularnych dostawców, w tym **subskrypcję
OpenAI Code (Codex)** (OAuth) i **Anthropic** (klucz API lub Claude CLI).

## Klucze konfiguracji (przegląd)

- `agents.defaults.model.primary` i `agents.defaults.model.fallbacks`
- `agents.defaults.imageModel.primary` i `agents.defaults.imageModel.fallbacks`
- `agents.defaults.pdfModel.primary` i `agents.defaults.pdfModel.fallbacks`
- `agents.defaults.imageGenerationModel.primary` i `agents.defaults.imageGenerationModel.fallbacks`
- `agents.defaults.videoGenerationModel.primary` i `agents.defaults.videoGenerationModel.fallbacks`
- `agents.defaults.models` (allowlista + aliasy + parametry dostawcy)
- `models.providers` (niestandardowi dostawcy zapisywani do `models.json`)

Odwołania do modeli są normalizowane do małych liter. Aliasy dostawców, takie jak `z.ai/*`, są normalizowane
do `zai/*`.

Przykłady konfiguracji dostawców (w tym OpenCode) znajdują się w
[/providers/opencode](/pl/providers/opencode).

## „Model is not allowed” (i dlaczego odpowiedzi się zatrzymują)

Jeśli ustawiono `agents.defaults.models`, staje się ono **allowlistą** dla `/model` oraz dla
nadpisań sesji. Gdy użytkownik wybierze model, którego nie ma na tej allowliście,
OpenClaw zwraca:

```
Model "provider/model" is not allowed. Use /model to list available models.
```

Dzieje się to **zanim** zostanie wygenerowana zwykła odpowiedź, więc wiadomość może sprawiać wrażenie,
jakby „nie odpowiedziała”. Rozwiązanie to:

- Dodać model do `agents.defaults.models`, albo
- Wyczyścić allowlistę (usunąć `agents.defaults.models`), albo
- Wybrać model z `/model list`.

Przykładowa konfiguracja allowlisty:

```json5
{
  agent: {
    model: { primary: "anthropic/claude-sonnet-4-6" },
    models: {
      "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
      "anthropic/claude-opus-4-6": { alias: "Opus" },
    },
  },
}
```

## Przełączanie modeli na czacie (`/model`)

Możesz przełączać modele dla bieżącej sesji bez restartu:

```
/model
/model list
/model 3
/model openai/gpt-5.4
/model status
```

Uwagi:

- `/model` (i `/model list`) to kompaktowy, numerowany selektor (rodzina modeli + dostępni dostawcy).
- Na Discord `/model` i `/models` otwierają interaktywny selektor z listami rozwijanymi dostawcy i modelu oraz krokiem Submit.
- `/model <#>` wybiera z tego selektora.
- `/model` natychmiast zapisuje nowy wybór sesji.
- Jeśli agent jest bezczynny, następne uruchomienie od razu użyje nowego modelu.
- Jeśli uruchomienie jest już aktywne, OpenClaw oznacza przełączenie na żywo jako oczekujące i restartuje do nowego modelu dopiero w czystym punkcie ponowienia.
- Jeśli aktywność narzędzi lub generowanie odpowiedzi już się rozpoczęły, oczekujące przełączenie może pozostać w kolejce do późniejszej okazji ponowienia lub do następnej tury użytkownika.
- `/model status` to widok szczegółowy (kandydaci uwierzytelniania oraz, gdy skonfigurowano, `baseUrl` endpointu dostawcy + tryb `api`).
- Odwołania do modeli są parsowane przez podział według **pierwszego** `/`. Użyj `provider/model`, wpisując `/model <ref>`.
- Jeśli samo ID modelu zawiera `/` (styl OpenRouter), musisz podać prefiks dostawcy (przykład: `/model openrouter/moonshotai/kimi-k2`).
- Jeśli pominiesz dostawcę, OpenClaw rozstrzyga dane wejściowe w tej kolejności:
  1. dopasowanie aliasu
  2. unikalne dopasowanie skonfigurowanego dostawcy dla dokładnie tego modelu bez prefiksu
  3. przestarzały fallback do skonfigurowanego domyślnego dostawcy
     Jeśli ten dostawca nie udostępnia już skonfigurowanego modelu domyślnego, OpenClaw
     zamiast tego przechodzi do pierwszego skonfigurowanego dostawcy/modelu, aby uniknąć
     pokazywania nieaktualnego domyślnego modelu usuniętego dostawcy.

Pełne zachowanie polecenia/konfiguracja: [Polecenia slash](/pl/tools/slash-commands).

## Polecenia CLI

```bash
openclaw models list
openclaw models status
openclaw models set <provider/model>
openclaw models set-image <provider/model>

openclaw models aliases list
openclaw models aliases add <alias> <provider/model>
openclaw models aliases remove <alias>

openclaw models fallbacks list
openclaw models fallbacks add <provider/model>
openclaw models fallbacks remove <provider/model>
openclaw models fallbacks clear

openclaw models image-fallbacks list
openclaw models image-fallbacks add <provider/model>
openclaw models image-fallbacks remove <provider/model>
openclaw models image-fallbacks clear
```

`openclaw models` (bez podpolecenia) to skrót dla `models status`.

### `models list`

Domyślnie pokazuje skonfigurowane modele. Przydatne flagi:

- `--all`: pełny katalog
- `--local`: tylko lokalni dostawcy
- `--provider <name>`: filtr według dostawcy
- `--plain`: jeden model w wierszu
- `--json`: wyjście do odczytu maszynowego

### `models status`

Pokazuje rozstrzygnięty model główny, fallbacki, model obrazu oraz przegląd uwierzytelniania
skonfigurowanych dostawców. Pokazuje także stan wygaśnięcia OAuth dla profili znalezionych
w magazynie uwierzytelniania (domyślnie ostrzega w ciągu 24 h). `--plain` wypisuje tylko
rozstrzygnięty model główny.
Stan OAuth jest zawsze pokazywany (i uwzględniany w wyjściu `--json`). Jeśli skonfigurowany
dostawca nie ma poświadczeń, `models status` wypisuje sekcję **Missing auth**.
JSON zawiera `auth.oauth` (okno ostrzeżenia + profile) oraz `auth.providers`
(efektywne uwierzytelnianie per dostawca, w tym poświadczenia oparte na env). `auth.oauth`
dotyczy wyłącznie kondycji profili w magazynie uwierzytelniania; dostawcy wyłącznie z env nie pojawiają się tam.
Użyj `--check` do automatyzacji (kod wyjścia `1` przy braku/wygaszeniu, `2` przy zbliżającym się wygaśnięciu).
Użyj `--probe` do aktywnych kontroli uwierzytelniania; wiersze sondy mogą pochodzić z profili uwierzytelniania, poświadczeń env
lub `models.json`.
Jeśli jawne `auth.order.<provider>` pomija zapisany profil, sonda zgłasza
`excluded_by_auth_order` zamiast próbować go użyć. Jeśli uwierzytelnianie istnieje, ale nie można rozstrzygnąć modelu
nadającego się do sondowania dla tego dostawcy, sonda zgłasza `status: no_model`.

Wybór uwierzytelniania zależy od dostawcy/konta. W przypadku hostów bramy działających stale klucze API
są zwykle najbardziej przewidywalne; ponowne użycie Claude CLI i istniejące profile Anthropic
OAuth/token również są obsługiwane.

Przykład (Claude CLI):

```bash
claude auth login
openclaw models status
```

## Skanowanie (darmowe modele OpenRouter)

`openclaw models scan` sprawdza **katalog darmowych modeli** OpenRouter i może
opcjonalnie sondować modele pod kątem obsługi narzędzi i obrazów.

Najważniejsze flagi:

- `--no-probe`: pomiń aktywne sondy (tylko metadane)
- `--min-params <b>`: minimalna liczba parametrów (w miliardach)
- `--max-age-days <days>`: pomiń starsze modele
- `--provider <name>`: filtr prefiksu dostawcy
- `--max-candidates <n>`: rozmiar listy fallbacków
- `--set-default`: ustaw `agents.defaults.model.primary` na pierwszy wybrany model
- `--set-image`: ustaw `agents.defaults.imageModel.primary` na pierwszy wybrany model obrazu

Sondowanie wymaga klucza API OpenRouter (z profili uwierzytelniania lub
`OPENROUTER_API_KEY`). Bez klucza użyj `--no-probe`, aby tylko wyświetlić kandydatów.

Wyniki skanowania są klasyfikowane według:

1. Obsługi obrazów
2. Latencji narzędzi
3. Rozmiaru kontekstu
4. Liczby parametrów

Dane wejściowe

- Lista OpenRouter `/models` (filtr `:free`)
- Wymaga klucza API OpenRouter z profili uwierzytelniania lub `OPENROUTER_API_KEY` (zobacz [/environment](/pl/help/environment))
- Opcjonalne filtry: `--max-age-days`, `--min-params`, `--provider`, `--max-candidates`
- Ustawienia sondowania: `--timeout`, `--concurrency`

Po uruchomieniu w TTY możesz interaktywnie wybrać fallbacki. W trybie nieinteraktywnym
przekaż `--yes`, aby zaakceptować ustawienia domyślne.

## Rejestr modeli (`models.json`)

Niestandardowi dostawcy w `models.providers` są zapisywani do `models.json` w katalogu
agenta (domyślnie `~/.openclaw/agents/<agentId>/agent/models.json`). Ten plik
jest domyślnie scalany, chyba że `models.mode` ustawiono na `replace`.

Priorytet w trybie scalania dla pasujących identyfikatorów dostawców:

- Niepuste `baseUrl`, już obecne w `models.json` agenta, ma pierwszeństwo.
- Niepuste `apiKey` w `models.json` agenta ma pierwszeństwo tylko wtedy, gdy ten dostawca nie jest zarządzany przez SecretRef w bieżącym kontekście konfiguracji/profilu uwierzytelniania.
- Wartości `apiKey` dostawców zarządzanych przez SecretRef są odświeżane ze znaczników źródłowych (`ENV_VAR_NAME` dla odwołań env, `secretref-managed` dla odwołań file/exec) zamiast utrwalania rozstrzygniętych sekretów.
- Wartości nagłówków dostawców zarządzanych przez SecretRef są odświeżane ze znaczników źródłowych (`secretref-env:ENV_VAR_NAME` dla odwołań env, `secretref-managed` dla odwołań file/exec).
- Puste lub brakujące `apiKey`/`baseUrl` agenta przechodzą do konfiguracji `models.providers`.
- Inne pola dostawcy są odświeżane z konfiguracji i znormalizowanych danych katalogu.

Trwałość znaczników jest sterowana przez źródło: OpenClaw zapisuje znaczniki z migawki aktywnej konfiguracji źródłowej (przed rozstrzygnięciem), a nie z rozstrzygniętych wartości sekretów w czasie działania.
Dotyczy to każdej sytuacji, gdy OpenClaw regeneruje `models.json`, w tym ścieżek sterowanych poleceniami, takich jak `openclaw agent`.

## Powiązane

- [Dostawcy modeli](/pl/concepts/model-providers) — routing dostawców i uwierzytelnianie
- [Failover modeli](/pl/concepts/model-failover) — łańcuchy fallbacków
- [Generowanie obrazów](/pl/tools/image-generation) — konfiguracja modeli obrazów
- [Generowanie muzyki](/tools/music-generation) — konfiguracja modeli muzyki
- [Generowanie wideo](/tools/video-generation) — konfiguracja modeli wideo
- [Referencja konfiguracji](/pl/gateway/configuration-reference#agent-defaults) — klucze konfiguracji modeli
