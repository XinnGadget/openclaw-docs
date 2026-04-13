---
read_when:
    - Chcesz zrozumieć, które funkcje mogą wywoływać płatne API.
    - Musisz przeprowadzić audyt kluczy, kosztów i widoczności zużycia.
    - Wyjaśniasz raportowanie kosztów w `/status` lub `/usage`.
summary: Sprawdź, co może generować koszty, które klucze są używane i jak wyświetlić zużycie.
title: Zużycie API i koszty
x-i18n:
    generated_at: "2026-04-13T08:50:45Z"
    model: gpt-5.4
    provider: openai
    source_hash: f5077e74d38ef781ac7a72603e9f9e3829a628b95c5a9967915ab0f321565429
    source_path: reference/api-usage-costs.md
    workflow: 15
---

# Zużycie API i koszty

Ten dokument zawiera listę **funkcji, które mogą wywoływać klucze API** oraz wskazuje, gdzie pojawiają się ich koszty. Skupia się na funkcjach OpenClaw, które mogą generować zużycie dostawców lub płatne wywołania API.

## Gdzie pojawiają się koszty (czat + CLI)

**Migawka kosztów dla sesji**

- `/status` pokazuje bieżący model sesji, użycie kontekstu i tokeny ostatniej odpowiedzi.
- Jeśli model używa **uwierzytelniania kluczem API**, `/status` pokazuje także **szacowany koszt** ostatniej odpowiedzi.
- Jeśli metadane aktywnej sesji są ubogie, `/status` może odzyskać liczniki tokenów/pamięci podręcznej oraz etykietę aktywnego modelu środowiska uruchomieniowego z najnowszego wpisu użycia w transkrypcie. Istniejące niezerowe wartości na żywo nadal mają pierwszeństwo, a sumy z transkryptu o rozmiarze promptu mogą wygrać, gdy zapisane sumy są nieobecne lub mniejsze.

**Stopka kosztu dla wiadomości**

- `/usage full` dodaje stopkę użycia do każdej odpowiedzi, w tym **szacowany koszt** (tylko klucz API).
- `/usage tokens` pokazuje tylko tokeny; przepływy OAuth/token w stylu subskrypcyjnym oraz przepływy CLI ukrywają koszt w dolarach.
- Uwaga dotycząca Gemini CLI: gdy CLI zwraca dane wyjściowe w formacie JSON, OpenClaw odczytuje użycie z `stats`, normalizuje `stats.cached` do `cacheRead` i w razie potrzeby wylicza tokeny wejściowe z `stats.input_tokens - stats.cached`.

Uwaga dotycząca Anthropic: pracownicy Anthropic poinformowali nas, że użycie Claude CLI w stylu OpenClaw jest znowu dozwolone, więc OpenClaw traktuje ponowne użycie Claude CLI i użycie `claude -p` jako zatwierdzone dla tej integracji, chyba że Anthropic opublikuje nową politykę.
Anthropic nadal nie udostępnia szacunku kosztu w dolarach dla pojedynczej wiadomości, który OpenClaw mógłby pokazać w `/usage full`.

**Okna użycia CLI (limity dostawców)**

- `openclaw status --usage` i `openclaw channels list` pokazują **okna użycia** dostawcy (migawki limitów, a nie koszty pojedynczych wiadomości).
- Dane wyjściowe dla ludzi są normalizowane do postaci `X% left` dla wszystkich dostawców.
- Obecni dostawcy okien użycia: Anthropic, GitHub Copilot, Gemini CLI, OpenAI Codex, MiniMax, Xiaomi i z.ai.
- Uwaga dotycząca MiniMax: jego surowe pola `usage_percent` / `usagePercent` oznaczają pozostały limit, więc OpenClaw odwraca je przed wyświetleniem. Pola oparte na liczbie nadal mają pierwszeństwo, jeśli są obecne. Jeśli dostawca zwraca `model_remains`, OpenClaw preferuje wpis modelu czatu, w razie potrzeby wyprowadza etykietę okna z sygnatur czasowych i uwzględnia nazwę modelu w etykiecie planu.
- Uwierzytelnianie użycia dla tych okien limitów pochodzi z hooków specyficznych dla dostawcy, gdy są dostępne; w przeciwnym razie OpenClaw przechodzi do dopasowywania poświadczeń OAuth/kluczy API z profili uwierzytelniania, środowiska lub konfiguracji.

Szczegóły i przykłady znajdziesz w [Użycie tokenów i koszty](/pl/reference/token-use).

## Jak wykrywane są klucze

OpenClaw może pobierać poświadczenia z:

- **Profili uwierzytelniania** (na agenta, przechowywanych w `auth-profiles.json`).
- **Zmienne środowiskowe** (np. `OPENAI_API_KEY`, `BRAVE_API_KEY`, `FIRECRAWL_API_KEY`).
- **Konfiguracja** (`models.providers.*.apiKey`, `plugins.entries.*.config.webSearch.apiKey`,
  `plugins.entries.firecrawl.config.webFetch.apiKey`, `memorySearch.*`,
  `talk.providers.*.apiKey`).
- **Skills** (`skills.entries.<name>.apiKey`), które mogą eksportować klucze do środowiska procesu Skill.

## Funkcje, które mogą korzystać z kluczy

### 1) Odpowiedzi modelu podstawowego (czat + narzędzia)

Każda odpowiedź lub wywołanie narzędzia używa **bieżącego dostawcy modelu** (OpenAI, Anthropic itd.). To podstawowe źródło użycia i kosztów.

Obejmuje to także hostowanych dostawców w stylu subskrypcyjnym, którzy nadal rozliczają poza lokalnym interfejsem OpenClaw, takich jak **OpenAI Codex**, **Alibaba Cloud Model Studio
Coding Plan**, **MiniMax Coding Plan**, **Z.AI / GLM Coding Plan** oraz ścieżka logowania Anthropic do Claude w OpenClaw z włączonym **Extra Usage**.

Zobacz [Modele](/pl/providers/models), aby poznać konfigurację cen, oraz [Użycie tokenów i koszty](/pl/reference/token-use), aby poznać sposób wyświetlania.

### 2) Rozumienie mediów (audio/obraz/wideo)

Media przychodzące mogą być streszczane/transkrybowane przed wygenerowaniem odpowiedzi. Wykorzystuje to interfejsy API modelu/dostawcy.

- Audio: OpenAI / Groq / Deepgram / Google / Mistral.
- Obraz: OpenAI / OpenRouter / Anthropic / Google / MiniMax / Moonshot / Qwen / Z.AI.
- Wideo: Google / Qwen / Moonshot.

Zobacz [Rozumienie mediów](/pl/nodes/media-understanding).

### 3) Generowanie obrazów i wideo

Współdzielone możliwości generowania również mogą wykorzystywać klucze dostawców:

- Generowanie obrazów: OpenAI / Google / fal / MiniMax
- Generowanie wideo: Qwen

Generowanie obrazów może wywnioskować domyślnego dostawcę opartego na uwierzytelnianiu, gdy
`agents.defaults.imageGenerationModel` nie jest ustawione. Generowanie wideo obecnie
wymaga jawnego `agents.defaults.videoGenerationModel`, takiego jak
`qwen/wan2.6-t2v`.

Zobacz [Generowanie obrazów](/pl/tools/image-generation), [Qwen Cloud](/pl/providers/qwen)
i [Modele](/pl/concepts/models).

### 4) Osadzania pamięci + wyszukiwanie semantyczne

Semantyczne wyszukiwanie pamięci używa **interfejsów API osadzań**, gdy jest skonfigurowane dla zdalnych dostawców:

- `memorySearch.provider = "openai"` → osadzania OpenAI
- `memorySearch.provider = "gemini"` → osadzania Gemini
- `memorySearch.provider = "voyage"` → osadzania Voyage
- `memorySearch.provider = "mistral"` → osadzania Mistral
- `memorySearch.provider = "lmstudio"` → osadzania LM Studio (lokalne/self-hosted)
- `memorySearch.provider = "ollama"` → osadzania Ollama (lokalne/self-hosted; zwykle bez rozliczeń za hostowane API)
- Opcjonalny fallback do zdalnego dostawcy, jeśli lokalne osadzania zakończą się niepowodzeniem

Możesz pozostać lokalnie, używając `memorySearch.provider = "local"` (bez użycia API).

Zobacz [Pamięć](/pl/concepts/memory).

### 5) Narzędzie wyszukiwania w sieci

`web_search` może generować opłaty za użycie w zależności od dostawcy:

- **Brave Search API**: `BRAVE_API_KEY` lub `plugins.entries.brave.config.webSearch.apiKey`
- **Exa**: `EXA_API_KEY` lub `plugins.entries.exa.config.webSearch.apiKey`
- **Firecrawl**: `FIRECRAWL_API_KEY` lub `plugins.entries.firecrawl.config.webSearch.apiKey`
- **Gemini (Google Search)**: `GEMINI_API_KEY` lub `plugins.entries.google.config.webSearch.apiKey`
- **Grok (xAI)**: `XAI_API_KEY` lub `plugins.entries.xai.config.webSearch.apiKey`
- **Kimi (Moonshot)**: `KIMI_API_KEY`, `MOONSHOT_API_KEY` lub `plugins.entries.moonshot.config.webSearch.apiKey`
- **MiniMax Search**: `MINIMAX_CODE_PLAN_KEY`, `MINIMAX_CODING_API_KEY`, `MINIMAX_API_KEY` lub `plugins.entries.minimax.config.webSearch.apiKey`
- **Ollama Web Search**: domyślnie bez klucza, ale wymaga osiągalnego hosta Ollama oraz `ollama signin`; może także ponownie używać zwykłego uwierzytelniania bearer dostawcy Ollama, gdy host tego wymaga
- **Perplexity Search API**: `PERPLEXITY_API_KEY`, `OPENROUTER_API_KEY` lub `plugins.entries.perplexity.config.webSearch.apiKey`
- **Tavily**: `TAVILY_API_KEY` lub `plugins.entries.tavily.config.webSearch.apiKey`
- **DuckDuckGo**: fallback bez klucza (bez rozliczeń API, ale nieoficjalny i oparty na HTML)
- **SearXNG**: `SEARXNG_BASE_URL` lub `plugins.entries.searxng.config.webSearch.baseUrl` (bez klucza/self-hosted; bez rozliczeń za hostowane API)

Starsze ścieżki dostawcy `tools.web.search.*` są nadal wczytywane przez tymczasową warstwę zgodności, ale nie są już zalecaną powierzchnią konfiguracji.

**Darmowy kredyt Brave Search:** Każdy plan Brave obejmuje odnawialny
darmowy kredyt w wysokości \$5/miesiąc. Plan Search kosztuje \$5 za 1000 żądań, więc ten kredyt pokrywa
1000 żądań/miesiąc bez opłat. Ustaw limit użycia w panelu Brave,
aby uniknąć nieoczekiwanych kosztów.

Zobacz [Narzędzia webowe](/pl/tools/web).

### 5) Narzędzie pobierania z sieci (Firecrawl)

`web_fetch` może wywoływać **Firecrawl**, gdy obecny jest klucz API:

- `FIRECRAWL_API_KEY` lub `plugins.entries.firecrawl.config.webFetch.apiKey`

Jeśli Firecrawl nie jest skonfigurowany, narzędzie przechodzi do bezpośredniego pobierania + readability (bez płatnego API).

Zobacz [Narzędzia webowe](/pl/tools/web).

### 6) Migawki użycia dostawcy (status/stan)

Niektóre polecenia statusu wywołują **punkty końcowe użycia dostawcy**, aby wyświetlić okna limitów lub stan uwierzytelniania.
Są to zwykle wywołania o małej częstotliwości, ale nadal trafiają do API dostawcy:

- `openclaw status --usage`
- `openclaw models status --json`

Zobacz [CLI modeli](/cli/models).

### 7) Zabezpieczające podsumowywanie Compaction

Zabezpieczenie Compaction może podsumowywać historię sesji przy użyciu **bieżącego modelu**, co
wywołuje interfejsy API dostawcy podczas działania.

Zobacz [Zarządzanie sesją + Compaction](/pl/reference/session-management-compaction).

### 8) Skanowanie / sondowanie modeli

`openclaw models scan` może sondować modele OpenRouter i używa `OPENROUTER_API_KEY`, gdy
sondowanie jest włączone.

Zobacz [CLI modeli](/cli/models).

### 9) Talk (mowa)

Tryb Talk może wywoływać **ElevenLabs**, gdy jest skonfigurowany:

- `ELEVENLABS_API_KEY` lub `talk.providers.elevenlabs.apiKey`

Zobacz [Tryb Talk](/pl/nodes/talk).

### 10) Skills (API innych firm)

Skills mogą przechowywać `apiKey` w `skills.entries.<name>.apiKey`. Jeśli Skill używa tego klucza do zewnętrznych
API, może generować koszty zgodnie z dostawcą danego Skill.

Zobacz [Skills](/pl/tools/skills).
