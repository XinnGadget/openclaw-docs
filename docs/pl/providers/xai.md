---
read_when:
    - Chcesz używać modeli Grok w OpenClaw
    - Konfigurujesz uwierzytelnianie xAI lub identyfikatory modeli
summary: Używaj modeli xAI Grok w OpenClaw
title: xAI
x-i18n:
    generated_at: "2026-04-12T23:33:41Z"
    model: gpt-5.4
    provider: openai
    source_hash: 820fef290c67d9815e41a96909d567216f67ca0f01df1d325008fd04666ad255
    source_path: providers/xai.md
    workflow: 15
---

# xAI

OpenClaw dostarcza dołączony Plugin dostawcy `xai` dla modeli Grok.

## Pierwsze kroki

<Steps>
  <Step title="Utwórz klucz API">
    Utwórz klucz API w [konsoli xAI](https://console.x.ai/).
  </Step>
  <Step title="Ustaw klucz API">
    Ustaw `XAI_API_KEY` albo uruchom:

    ```bash
    openclaw onboard --auth-choice xai-api-key
    ```

  </Step>
  <Step title="Wybierz model">
    ```json5
    {
      agents: { defaults: { model: { primary: "xai/grok-4" } } },
    }
    ```
  </Step>
</Steps>

<Note>
OpenClaw używa xAI Responses API jako dołączonego transportu xAI. Ten sam
`XAI_API_KEY` może także zasilać `web_search` oparty na Grok, natywne `x_search`
oraz zdalne `code_execution`.
Jeśli przechowujesz klucz xAI w `plugins.entries.xai.config.webSearch.apiKey`,
dołączony dostawca modeli xAI także używa tego klucza jako fallbacku.
Dostrajanie `code_execution` znajduje się w `plugins.entries.xai.config.codeExecution`.
</Note>

## Dołączony katalog modeli

OpenClaw zawiera domyślnie następujące rodziny modeli xAI:

| Rodzina        | Identyfikatory modeli                                                    |
| -------------- | ------------------------------------------------------------------------ |
| Grok 3         | `grok-3`, `grok-3-fast`, `grok-3-mini`, `grok-3-mini-fast`               |
| Grok 4         | `grok-4`, `grok-4-0709`                                                  |
| Grok 4 Fast    | `grok-4-fast`, `grok-4-fast-non-reasoning`                               |
| Grok 4.1 Fast  | `grok-4-1-fast`, `grok-4-1-fast-non-reasoning`                           |
| Grok 4.20 Beta | `grok-4.20-beta-latest-reasoning`, `grok-4.20-beta-latest-non-reasoning` |
| Grok Code      | `grok-code-fast-1`                                                       |

Plugin dodatkowo forward-resolve’uje nowsze identyfikatory `grok-4*` i `grok-code-fast*`, gdy
mają ten sam kształt API.

<Tip>
`grok-4-fast`, `grok-4-1-fast` oraz warianty `grok-4.20-beta-*` to
obecne referencje Grok z obsługą obrazów w dołączonym katalogu.
</Tip>

### Mapowania trybu fast

`/fast on` lub `agents.defaults.models["xai/<model>"].params.fastMode: true`
przepisuje natywne żądania xAI w następujący sposób:

| Model źródłowy | Cel trybu fast    |
| -------------- | ----------------- |
| `grok-3`       | `grok-3-fast`     |
| `grok-3-mini`  | `grok-3-mini-fast` |
| `grok-4`       | `grok-4-fast`     |
| `grok-4-0709`  | `grok-4-fast`     |

### Aliasy zgodności legacy

Aliasom legacy nadal odpowiadają kanoniczne dołączone identyfikatory:

| Alias legacy              | Identyfikator kanoniczny             |
| ------------------------- | ------------------------------------ |
| `grok-4-fast-reasoning`   | `grok-4-fast`                        |
| `grok-4-1-fast-reasoning` | `grok-4-1-fast`                      |
| `grok-4.20-reasoning`     | `grok-4.20-beta-latest-reasoning`    |
| `grok-4.20-non-reasoning` | `grok-4.20-beta-latest-non-reasoning` |

## Funkcje

<AccordionGroup>
  <Accordion title="Web search">
    Dołączony dostawca `grok` dla web search także używa `XAI_API_KEY`:

    ```bash
    openclaw config set tools.web.search.provider grok
    ```

  </Accordion>

  <Accordion title="Generowanie wideo">
    Dołączony Plugin `xai` rejestruje generowanie wideo przez współdzielone
    narzędzie `video_generate`.

    - Domyślny model wideo: `xai/grok-imagine-video`
    - Tryby: tekst-na-wideo, obraz-na-wideo oraz zdalne przepływy edycji/rozszerzania wideo
    - Obsługuje `aspectRatio` i `resolution`

    <Warning>
    Lokalne bufory wideo nie są akceptowane. Używaj zdalnych URL-i `http(s)` dla
    wejść referencyjnych wideo i wejść edycji.
    </Warning>

    Aby używać xAI jako domyślnego dostawcy wideo:

    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "xai/grok-imagine-video",
          },
        },
      },
    }
    ```

    <Note>
    Zobacz [Video Generation](/pl/tools/video-generation), aby poznać wspólne parametry narzędzia,
    wybór dostawcy i zachowanie failover.
    </Note>

  </Accordion>

  <Accordion title="Konfiguracja x_search">
    Dołączony Plugin xAI udostępnia `x_search` jako narzędzie OpenClaw do przeszukiwania
    treści X (dawniej Twitter) przez Grok.

    Ścieżka konfiguracji: `plugins.entries.xai.config.xSearch`

    | Klucz             | Typ     | Domyślnie          | Opis                                 |
    | ----------------- | ------- | ------------------ | ------------------------------------ |
    | `enabled`         | boolean | —                  | Włącza lub wyłącza x_search          |
    | `model`           | string  | `grok-4-1-fast`    | Model używany do żądań x_search      |
    | `inlineCitations` | boolean | —                  | Dołącza cytowania inline w wynikach  |
    | `maxTurns`        | number  | —                  | Maksymalna liczba tur rozmowy        |
    | `timeoutSeconds`  | number  | —                  | Timeout żądania w sekundach          |
    | `cacheTtlMinutes` | number  | —                  | Czas życia cache w minutach          |

    ```json5
    {
      plugins: {
        entries: {
          xai: {
            config: {
              xSearch: {
                enabled: true,
                model: "grok-4-1-fast",
                inlineCitations: true,
              },
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Konfiguracja code_execution">
    Dołączony Plugin xAI udostępnia `code_execution` jako narzędzie OpenClaw do
    zdalnego wykonywania kodu w środowisku sandbox xAI.

    Ścieżka konfiguracji: `plugins.entries.xai.config.codeExecution`

    | Klucz             | Typ     | Domyślnie                    | Opis                                      |
    | ----------------- | ------- | ---------------------------- | ----------------------------------------- |
    | `enabled`         | boolean | `true` (jeśli klucz jest dostępny) | Włącza lub wyłącza wykonywanie kodu |
    | `model`           | string  | `grok-4-1-fast`              | Model używany do żądań wykonywania kodu   |
    | `maxTurns`        | number  | —                            | Maksymalna liczba tur rozmowy             |
    | `timeoutSeconds`  | number  | —                            | Timeout żądania w sekundach               |

    <Note>
    To jest zdalne wykonywanie w sandboxie xAI, a nie lokalne [`exec`](/pl/tools/exec).
    </Note>

    ```json5
    {
      plugins: {
        entries: {
          xai: {
            config: {
              codeExecution: {
                enabled: true,
                model: "grok-4-1-fast",
              },
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Znane ograniczenia">
    - Obecnie uwierzytelnianie obsługuje tylko klucz API. OpenClaw nie ma jeszcze OAuth ani przepływu device-code dla xAI.
    - `grok-4.20-multi-agent-experimental-beta-0304` nie jest obsługiwany na
      zwykłej ścieżce dostawcy xAI, ponieważ wymaga innej powierzchni upstream API
      niż standardowy transport xAI w OpenClaw.
  </Accordion>

  <Accordion title="Uwagi zaawansowane">
    - OpenClaw automatycznie stosuje poprawki zgodności schematów narzędzi i wywołań narzędzi specyficzne dla xAI na współdzielonej ścieżce runnera.
    - Natywne żądania xAI domyślnie używają `tool_stream: true`. Ustaw
      `agents.defaults.models["xai/<model>"].params.tool_stream` na `false`, aby
      to wyłączyć.
    - Dołączony wrapper xAI usuwa nieobsługiwane ścisłe flagi schematu narzędzi i
      klucze payloadu reasoning przed wysłaniem natywnych żądań xAI.
    - `web_search`, `x_search` i `code_execution` są udostępniane jako narzędzia OpenClaw. OpenClaw włącza konkretny wbudowany mechanizm xAI, którego potrzebuje, wewnątrz każdego żądania narzędzia, zamiast dołączać wszystkie natywne narzędzia do każdej tury czatu.
    - `x_search` i `code_execution` należą do dołączonego Pluginu xAI, a nie są na stałe zakodowane w głównym runtime modeli.
    - `code_execution` to zdalne wykonywanie w sandboxie xAI, a nie lokalne
      [`exec`](/pl/tools/exec).
  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, referencji modeli i zachowania failover.
  </Card>
  <Card title="Generowanie wideo" href="/pl/tools/video-generation" icon="video">
    Wspólne parametry narzędzia wideo i wybór dostawcy.
  </Card>
  <Card title="Wszyscy dostawcy" href="/pl/providers/index" icon="grid-2">
    Szerszy przegląd dostawców.
  </Card>
  <Card title="Rozwiązywanie problemów" href="/pl/help/troubleshooting" icon="wrench">
    Typowe problemy i poprawki.
  </Card>
</CardGroup>
