---
read_when:
    - Chcesz używać modeli Anthropic w OpenClaw
summary: Używaj Anthropic Claude za pomocą kluczy API lub Claude CLI w OpenClaw
title: Anthropic
x-i18n:
    generated_at: "2026-04-12T23:29:04Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5e3dda5f98ade9d4c3841888103bfb43d59e075d358a701ed0ae3ffb8d5694a7
    source_path: providers/anthropic.md
    workflow: 15
---

# Anthropic (Claude)

Anthropic tworzy rodzinę modeli **Claude**. OpenClaw obsługuje dwie ścieżki uwierzytelniania:

- **Klucz API** — bezpośredni dostęp do API Anthropic z rozliczaniem zależnym od użycia (modele `anthropic/*`)
- **Claude CLI** — ponowne wykorzystanie istniejącego logowania Claude CLI na tym samym hoście

<Warning>
Pracownicy Anthropic poinformowali nas, że użycie Claude CLI w stylu OpenClaw jest znowu dozwolone, więc OpenClaw traktuje ponowne wykorzystanie Claude CLI i użycie `claude -p` jako dozwolone, chyba że Anthropic opublikuje nową politykę.

W przypadku długotrwale działających hostów Gateway klucze API Anthropic nadal są najjaśniejszą i najbardziej przewidywalną ścieżką produkcyjną.

Aktualna publiczna dokumentacja Anthropic:

- [Referencja Claude Code CLI](https://code.claude.com/docs/en/cli-reference)
- [Przegląd Claude Agent SDK](https://platform.claude.com/docs/en/agent-sdk/overview)
- [Używanie Claude Code z planem Pro lub Max](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- [Używanie Claude Code z planem Team lub Enterprise](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/)
  </Warning>

## Pierwsze kroki

<Tabs>
  <Tab title="Klucz API">
    **Najlepsze do:** standardowego dostępu do API i rozliczania zależnego od użycia.

    <Steps>
      <Step title="Pobierz klucz API">
        Utwórz klucz API w [Anthropic Console](https://console.anthropic.com/).
      </Step>
      <Step title="Uruchom onboarding">
        ```bash
        openclaw onboard
        # wybierz: Anthropic API key
        ```

        Albo przekaż klucz bezpośrednio:

        ```bash
        openclaw onboard --anthropic-api-key "$ANTHROPIC_API_KEY"
        ```
      </Step>
      <Step title="Sprawdź, czy model jest dostępny">
        ```bash
        openclaw models list --provider anthropic
        ```
      </Step>
    </Steps>

    ### Przykład konfiguracji

    ```json5
    {
      env: { ANTHROPIC_API_KEY: "sk-ant-..." },
      agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
    }
    ```

  </Tab>

  <Tab title="Claude CLI">
    **Najlepsze do:** ponownego wykorzystania istniejącego logowania Claude CLI bez osobnego klucza API.

    <Steps>
      <Step title="Upewnij się, że Claude CLI jest zainstalowane i zalogowane">
        Sprawdź za pomocą:

        ```bash
        claude --version
        ```
      </Step>
      <Step title="Uruchom onboarding">
        ```bash
        openclaw onboard
        # wybierz: Claude CLI
        ```

        OpenClaw wykrywa i ponownie wykorzystuje istniejące poświadczenia Claude CLI.
      </Step>
      <Step title="Sprawdź, czy model jest dostępny">
        ```bash
        openclaw models list --provider anthropic
        ```
      </Step>
    </Steps>

    <Note>
    Szczegóły konfiguracji i działania backendu Claude CLI znajdują się w [CLI Backends](/pl/gateway/cli-backends).
    </Note>

    <Tip>
    Jeśli chcesz mieć najjaśniejszą ścieżkę rozliczania, zamiast tego użyj klucza API Anthropic. OpenClaw obsługuje też opcje subskrypcyjne z [OpenAI Codex](/pl/providers/openai), [Qwen Cloud](/pl/providers/qwen), [MiniMax](/pl/providers/minimax) i [Z.AI / GLM](/pl/providers/glm).
    </Tip>

  </Tab>
</Tabs>

## Domyślne ustawienia thinking (Claude 4.6)

Modele Claude 4.6 domyślnie używają `adaptive` thinking w OpenClaw, gdy nie ustawiono jawnego poziomu thinking.

Nadpisz dla pojedynczej wiadomości za pomocą `/think:<level>` albo w parametrach modelu:

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { thinking: "adaptive" },
        },
      },
    },
  },
}
```

<Note>
Powiązana dokumentacja Anthropic:
- [Adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking)
- [Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)
</Note>

## Cache promptów

OpenClaw obsługuje funkcję cache promptów Anthropic dla uwierzytelniania kluczem API.

| Wartość             | Czas trwania cache | Opis                                           |
| ------------------- | ------------------ | ---------------------------------------------- |
| `"short"` (domyślne) | 5 minut           | Stosowane automatycznie dla uwierzytelniania kluczem API |
| `"long"`            | 1 godzina          | Rozszerzony cache                              |
| `"none"`            | Brak cache         | Wyłącza cache promptów                         |

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" },
        },
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Nadpisania cache dla poszczególnych agentów">
    Użyj parametrów na poziomie modelu jako wartości bazowej, a następnie nadpisz konkretne agenty przez `agents.list[].params`:

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "anthropic/claude-opus-4-6" },
          models: {
            "anthropic/claude-opus-4-6": {
              params: { cacheRetention: "long" },
            },
          },
        },
        list: [
          { id: "research", default: true },
          { id: "alerts", params: { cacheRetention: "none" } },
        ],
      },
    }
    ```

    Kolejność scalania konfiguracji:

    1. `agents.defaults.models["provider/model"].params`
    2. `agents.list[].params` (dopasowane `id`, nadpisuje według klucza)

    Dzięki temu jeden agent może zachować długotrwały cache, podczas gdy inny agent na tym samym modelu wyłączy cache dla skokowego ruchu o niskim poziomie ponownego użycia.

  </Accordion>

  <Accordion title="Uwagi o Claude na Bedrock">
    - Modele Anthropic Claude na Bedrock (`amazon-bedrock/*anthropic.claude*`) akceptują przekazanie `cacheRetention`, jeśli jest skonfigurowane.
    - Modele Bedrock inne niż Anthropic są w czasie działania wymuszane na `cacheRetention: "none"`.
    - Inteligentne ustawienia domyślne dla klucza API ustawiają też `cacheRetention: "short"` dla odwołań do Claude na Bedrock, gdy nie ustawiono jawnej wartości.
  </Accordion>
</AccordionGroup>

## Konfiguracja zaawansowana

<AccordionGroup>
  <Accordion title="Tryb fast">
    Wspólny przełącznik `/fast` w OpenClaw obsługuje bezpośredni ruch Anthropic (klucz API i OAuth do `api.anthropic.com`).

    | Polecenie | Mapuje na |
    |---------|---------|
    | `/fast on` | `service_tier: "auto"` |
    | `/fast off` | `service_tier: "standard_only"` |

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "anthropic/claude-sonnet-4-6": {
              params: { fastMode: true },
            },
          },
        },
      },
    }
    ```

    <Note>
    - Wstrzykiwane tylko dla bezpośrednich żądań do `api.anthropic.com`. Trasy proxy pozostawiają `service_tier` bez zmian.
    - Jawne parametry `serviceTier` lub `service_tier` mają pierwszeństwo przed `/fast`, gdy ustawione są oba.
    - Na kontach bez pojemności Priority Tier `service_tier: "auto"` może zostać rozwiązane jako `standard`.
    </Note>

  </Accordion>

  <Accordion title="Rozumienie mediów (obraz i PDF)">
    Dołączony Plugin Anthropic rejestruje rozumienie obrazów i plików PDF. OpenClaw
    automatycznie rozwiązuje możliwości mediów na podstawie skonfigurowanego uwierzytelniania Anthropic — nie jest potrzebna dodatkowa konfiguracja.

    | Właściwość        | Wartość              |
    | ----------------- | -------------------- |
    | Model domyślny    | `claude-opus-4-6`    |
    | Obsługiwane wejście | Obrazy, dokumenty PDF |

    Gdy do rozmowy zostanie dołączony obraz lub plik PDF, OpenClaw automatycznie
    kieruje go przez dostawcę rozumienia mediów Anthropic.

  </Accordion>

  <Accordion title="Okno kontekstu 1M (beta)">
    Okno kontekstu 1M w Anthropic jest dostępne za bramką beta. Włącz je dla wybranego modelu:

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "anthropic/claude-opus-4-6": {
              params: { context1m: true },
            },
          },
        },
      },
    }
    ```

    OpenClaw mapuje to w żądaniach na `anthropic-beta: context-1m-2025-08-07`.

    <Warning>
    Wymaga dostępu do długiego kontekstu na Twoim poświadczeniu Anthropic. Starsze uwierzytelnianie tokenem (`sk-ant-oat-*`) jest odrzucane dla żądań kontekstu 1M — OpenClaw zapisuje ostrzeżenie w logach i wraca do standardowego okna kontekstu.
    </Warning>

  </Accordion>
</AccordionGroup>

## Rozwiązywanie problemów

<AccordionGroup>
  <Accordion title="Błędy 401 / token nagle nieważny">
    Uwierzytelnianie tokenem Anthropic może wygasnąć lub zostać cofnięte. W nowych konfiguracjach przejdź na klucz API Anthropic.
  </Accordion>

  <Accordion title='Nie znaleziono klucza API dla dostawcy "anthropic"'>
    Uwierzytelnianie jest **na agenta**. Nowi agenci nie dziedziczą kluczy głównego agenta. Uruchom onboarding ponownie dla tego agenta albo skonfiguruj klucz API na hoście Gateway, a następnie sprawdź za pomocą `openclaw models status`.
  </Accordion>

  <Accordion title='Nie znaleziono poświadczeń dla profilu "anthropic:default"'>
    Uruchom `openclaw models status`, aby zobaczyć, który profil uwierzytelniania jest aktywny. Uruchom onboarding ponownie albo skonfiguruj klucz API dla tej ścieżki profilu.
  </Accordion>

  <Accordion title="Brak dostępnego profilu uwierzytelniania (wszystkie w cooldown)">
    Sprawdź `openclaw models status --json` dla `auth.unusableProfiles`. Cooldowny limitów szybkości Anthropic mogą być ograniczone do modelu, więc pokrewny model Anthropic nadal może być użyteczny. Dodaj kolejny profil Anthropic albo poczekaj na koniec cooldownu.
  </Accordion>
</AccordionGroup>

<Note>
Więcej pomocy: [Rozwiązywanie problemów](/pl/help/troubleshooting) i [FAQ](/pl/help/faq).
</Note>

## Powiązane

<CardGroup cols={2}>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, odwołań do modeli i zachowania failover.
  </Card>
  <Card title="CLI backends" href="/pl/gateway/cli-backends" icon="terminal">
    Konfiguracja backendu Claude CLI i szczegóły działania.
  </Card>
  <Card title="Cache promptów" href="/pl/reference/prompt-caching" icon="database">
    Jak działa cache promptów u różnych dostawców.
  </Card>
  <Card title="OAuth i uwierzytelnianie" href="/pl/gateway/authentication" icon="key">
    Szczegóły uwierzytelniania i zasady ponownego wykorzystania poświadczeń.
  </Card>
</CardGroup>
