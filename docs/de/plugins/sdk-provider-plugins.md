---
read_when:
    - Sie erstellen ein neues Modell-Provider-Plugin
    - Sie möchten einen OpenAI-kompatiblen Proxy oder ein benutzerdefiniertes LLM zu OpenClaw hinzufügen
    - Sie müssen Provider-Authentifizierung, Kataloge und Laufzeit-Hooks verstehen
sidebarTitle: Provider Plugins
summary: Schritt-für-Schritt-Anleitung zum Erstellen eines Modell-Provider-Plugins für OpenClaw
title: Provider-Plugins erstellen
x-i18n:
    generated_at: "2026-04-09T01:31:16Z"
    model: gpt-5.4
    provider: openai
    source_hash: 38d9af522dc19e49c81203a83a4096f01c2398b1df771c848a30ad98f251e9e1
    source_path: plugins/sdk-provider-plugins.md
    workflow: 15
---

# Provider-Plugins erstellen

Diese Anleitung führt Sie durch das Erstellen eines Provider-Plugins, das einen Modell-Provider
(LLM) zu OpenClaw hinzufügt. Am Ende verfügen Sie über einen Provider mit Modellkatalog,
API-Schlüssel-Authentifizierung und dynamischer Modellauflösung.

<Info>
  Wenn Sie noch nie zuvor ein OpenClaw-Plugin erstellt haben, lesen Sie zuerst
  [Getting Started](/de/plugins/building-plugins), um sich mit der grundlegenden Paketstruktur
  und der Manifest-Einrichtung vertraut zu machen.
</Info>

## Anleitung

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="Paket und Manifest">
    <CodeGroup>
    ```json package.json
    {
      "name": "@myorg/openclaw-acme-ai",
      "version": "1.0.0",
      "type": "module",
      "openclaw": {
        "extensions": ["./index.ts"],
        "providers": ["acme-ai"],
        "compat": {
          "pluginApi": ">=2026.3.24-beta.2",
          "minGatewayVersion": "2026.3.24-beta.2"
        },
        "build": {
          "openclawVersion": "2026.3.24-beta.2",
          "pluginSdkVersion": "2026.3.24-beta.2"
        }
      }
    }
    ```

    ```json openclaw.plugin.json
    {
      "id": "acme-ai",
      "name": "Acme AI",
      "description": "Acme AI model provider",
      "providers": ["acme-ai"],
      "modelSupport": {
        "modelPrefixes": ["acme-"]
      },
      "providerAuthEnvVars": {
        "acme-ai": ["ACME_AI_API_KEY"]
      },
      "providerAuthAliases": {
        "acme-ai-coding": "acme-ai"
      },
      "providerAuthChoices": [
        {
          "provider": "acme-ai",
          "method": "api-key",
          "choiceId": "acme-ai-api-key",
          "choiceLabel": "Acme AI API key",
          "groupId": "acme-ai",
          "groupLabel": "Acme AI",
          "cliFlag": "--acme-ai-api-key",
          "cliOption": "--acme-ai-api-key <key>",
          "cliDescription": "Acme AI API key"
        }
      ],
      "configSchema": {
        "type": "object",
        "additionalProperties": false
      }
    }
    ```
    </CodeGroup>

    Das Manifest deklariert `providerAuthEnvVars`, damit OpenClaw
    Anmeldedaten erkennen kann, ohne die Laufzeit Ihres Plugins zu laden. Fügen Sie `providerAuthAliases`
    hinzu, wenn eine Provider-Variante die Authentifizierung einer anderen Provider-ID wiederverwenden soll. `modelSupport`
    ist optional und ermöglicht es OpenClaw, Ihr Provider-Plugin automatisch aus Kurzform-
    Modell-IDs wie `acme-large` zu laden, bevor Laufzeit-Hooks existieren. Wenn Sie den
    Provider auf ClawHub veröffentlichen, sind diese Felder `openclaw.compat` und `openclaw.build`
    in `package.json` erforderlich.

  </Step>

  <Step title="Den Provider registrieren">
    Ein minimaler Provider benötigt `id`, `label`, `auth` und `catalog`:

    ```typescript index.ts
    import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
    import { createProviderApiKeyAuthMethod } from "openclaw/plugin-sdk/provider-auth";

    export default definePluginEntry({
      id: "acme-ai",
      name: "Acme AI",
      description: "Acme AI model provider",
      register(api) {
        api.registerProvider({
          id: "acme-ai",
          label: "Acme AI",
          docsPath: "/providers/acme-ai",
          envVars: ["ACME_AI_API_KEY"],

          auth: [
            createProviderApiKeyAuthMethod({
              providerId: "acme-ai",
              methodId: "api-key",
              label: "Acme AI API key",
              hint: "API key from your Acme AI dashboard",
              optionKey: "acmeAiApiKey",
              flagName: "--acme-ai-api-key",
              envVar: "ACME_AI_API_KEY",
              promptMessage: "Enter your Acme AI API key",
              defaultModel: "acme-ai/acme-large",
            }),
          ],

          catalog: {
            order: "simple",
            run: async (ctx) => {
              const apiKey =
                ctx.resolveProviderApiKey("acme-ai").apiKey;
              if (!apiKey) return null;
              return {
                provider: {
                  baseUrl: "https://api.acme-ai.com/v1",
                  apiKey,
                  api: "openai-completions",
                  models: [
                    {
                      id: "acme-large",
                      name: "Acme Large",
                      reasoning: true,
                      input: ["text", "image"],
                      cost: { input: 3, output: 15, cacheRead: 0.3, cacheWrite: 3.75 },
                      contextWindow: 200000,
                      maxTokens: 32768,
                    },
                    {
                      id: "acme-small",
                      name: "Acme Small",
                      reasoning: false,
                      input: ["text"],
                      cost: { input: 1, output: 5, cacheRead: 0.1, cacheWrite: 1.25 },
                      contextWindow: 128000,
                      maxTokens: 8192,
                    },
                  ],
                },
              };
            },
          },
        });
      },
    });
    ```

    Das ist ein funktionierender Provider. Benutzer können nun
    `openclaw onboard --acme-ai-api-key <key>` verwenden und
    `acme-ai/acme-large` als Modell auswählen.

    Für gebündelte Provider, die nur einen Text-Provider mit API-Key-
    Authentifizierung plus eine einzelne kataloggestützte Laufzeit registrieren, sollten Sie bevorzugt
    den schmaleren Helper `defineSingleProviderPluginEntry(...)` verwenden:

    ```typescript
    import { defineSingleProviderPluginEntry } from "openclaw/plugin-sdk/provider-entry";

    export default defineSingleProviderPluginEntry({
      id: "acme-ai",
      name: "Acme AI",
      description: "Acme AI model provider",
      provider: {
        label: "Acme AI",
        docsPath: "/providers/acme-ai",
        auth: [
          {
            methodId: "api-key",
            label: "Acme AI API key",
            hint: "API key from your Acme AI dashboard",
            optionKey: "acmeAiApiKey",
            flagName: "--acme-ai-api-key",
            envVar: "ACME_AI_API_KEY",
            promptMessage: "Enter your Acme AI API key",
            defaultModel: "acme-ai/acme-large",
          },
        ],
        catalog: {
          buildProvider: () => ({
            api: "openai-completions",
            baseUrl: "https://api.acme-ai.com/v1",
            models: [{ id: "acme-large", name: "Acme Large" }],
          }),
        },
      },
    });
    ```

    Wenn Ihr Authentifizierungsablauf während des Onboardings außerdem
    `models.providers.*`, Aliasse und das Standardmodell des Agenten anpassen muss, verwenden Sie die Preset-Helper aus
    `openclaw/plugin-sdk/provider-onboard`. Die schmalsten Helper sind
    `createDefaultModelPresetAppliers(...)`,
    `createDefaultModelsPresetAppliers(...)` und
    `createModelCatalogPresetAppliers(...)`.

    Wenn ein nativer Endpunkt eines Providers gestreamte Nutzungsblöcke auf dem
    normalen Transport `openai-completions` unterstützt, verwenden Sie bevorzugt die gemeinsamen Katalog-Helper in
    `openclaw/plugin-sdk/provider-catalog-shared`, anstatt Prüfungen auf Provider-IDs hart zu codieren.
    `supportsNativeStreamingUsageCompat(...)` und
    `applyProviderNativeStreamingUsageCompat(...)` erkennen die Unterstützung anhand der
    Endpunkt-Fähigkeitszuordnung, sodass native Moonshot-/DashScope-artige Endpunkte weiterhin
    opt-in können, selbst wenn ein Plugin eine benutzerdefinierte Provider-ID verwendet.

  </Step>

  <Step title="Dynamische Modellauflösung hinzufügen">
    Wenn Ihr Provider beliebige Modell-IDs akzeptiert (wie ein Proxy oder Router),
    fügen Sie `resolveDynamicModel` hinzu:

    ```typescript
    api.registerProvider({
      // ... id, label, auth, catalog from above

      resolveDynamicModel: (ctx) => ({
        id: ctx.modelId,
        name: ctx.modelId,
        provider: "acme-ai",
        api: "openai-completions",
        baseUrl: "https://api.acme-ai.com/v1",
        reasoning: false,
        input: ["text"],
        cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
        contextWindow: 128000,
        maxTokens: 8192,
      }),
    });
    ```

    Wenn für die Auflösung ein Netzwerkaufruf erforderlich ist, verwenden Sie `prepareDynamicModel` für asynchrones
    Aufwärmen — `resolveDynamicModel` wird nach Abschluss erneut ausgeführt.

  </Step>

  <Step title="Laufzeit-Hooks hinzufügen (bei Bedarf)">
    Die meisten Provider benötigen nur `catalog` + `resolveDynamicModel`. Fügen Sie Hooks
    schrittweise hinzu, wenn Ihr Provider sie benötigt.

    Gemeinsame Helper-Builder decken jetzt die häufigsten Familien für Replay/Tool-Kompatibilität
    ab, sodass Plugins normalerweise nicht jeden Hook einzeln manuell verdrahten müssen:

    ```typescript
    import { buildProviderReplayFamilyHooks } from "openclaw/plugin-sdk/provider-model-shared";
    import { buildProviderStreamFamilyHooks } from "openclaw/plugin-sdk/provider-stream";
    import { buildProviderToolCompatFamilyHooks } from "openclaw/plugin-sdk/provider-tools";

    const GOOGLE_FAMILY_HOOKS = {
      ...buildProviderReplayFamilyHooks({ family: "google-gemini" }),
      ...buildProviderStreamFamilyHooks("google-thinking"),
      ...buildProviderToolCompatFamilyHooks("gemini"),
    };

    api.registerProvider({
      id: "acme-gemini-compatible",
      // ...
      ...GOOGLE_FAMILY_HOOKS,
    });
    ```

    Heute verfügbare Replay-Familien:

    | Family | Was sie verdrahtet |
    | --- | --- |
    | `openai-compatible` | Gemeinsame Replay-Richtlinie im OpenAI-Stil für OpenAI-kompatible Transporte, einschließlich Bereinigung von Tool-Call-IDs, Korrekturen der Assistant-First-Reihenfolge und generischer Gemini-Turn-Validierung, wo der Transport sie benötigt |
    | `anthropic-by-model` | Claude-bewusste Replay-Richtlinie, ausgewählt über `modelId`, sodass Transports vom Typ Anthropic Messages nur dann Claude-spezifische Bereinigung von Thinking-Blöcken erhalten, wenn das aufgelöste Modell tatsächlich eine Claude-ID ist |
    | `google-gemini` | Native Gemini-Replay-Richtlinie plus Bootstrap-Replay-Bereinigung und Modus für getaggte Reasoning-Ausgabe |
    | `passthrough-gemini` | Bereinigung der Gemini-Thought-Signatur für Gemini-Modelle, die über OpenAI-kompatible Proxy-Transporte laufen; aktiviert keine native Gemini-Replay-Validierung oder Bootstrap-Umschreibungen |
    | `hybrid-anthropic-openai` | Hybride Richtlinie für Provider, die Anthropic-Message- und OpenAI-kompatible Modelloberflächen in einem Plugin kombinieren; optionales Entfernen von Claude-only-Thinking-Blöcken bleibt auf die Anthropic-Seite beschränkt |

    Reale gebündelte Beispiele:

    - `google` und `google-gemini-cli`: `google-gemini`
    - `openrouter`, `kilocode`, `opencode` und `opencode-go`: `passthrough-gemini`
    - `amazon-bedrock` und `anthropic-vertex`: `anthropic-by-model`
    - `minimax`: `hybrid-anthropic-openai`
    - `moonshot`, `ollama`, `xai` und `zai`: `openai-compatible`

    Heute verfügbare Stream-Familien:

    | Family | Was sie verdrahtet |
    | --- | --- |
    | `google-thinking` | Normalisierung der Gemini-Thinking-Payload auf dem gemeinsamen Stream-Pfad |
    | `kilocode-thinking` | Kilo-Reasoning-Wrapper auf dem gemeinsamen Proxy-Stream-Pfad, wobei `kilo/auto` und nicht unterstützte Proxy-Reasoning-IDs das injizierte Thinking überspringen |
    | `moonshot-thinking` | Abbildung der nativen binären Thinking-Payload von Moonshot aus Konfiguration + `/think`-Level |
    | `minimax-fast-mode` | Umschreiben von MiniMax-Fast-Mode-Modellen auf dem gemeinsamen Stream-Pfad |
    | `openai-responses-defaults` | Gemeinsame Wrapper für native OpenAI/Codex Responses: Attributions-Header, `/fast`/`serviceTier`, Text-Verbosity, native Codex-Websuche, kompatible Payload-Gestaltung für Reasoning und Kontextverwaltung für Responses |
    | `openrouter-thinking` | OpenRouter-Reasoning-Wrapper für Proxy-Routen, wobei übersprungene nicht unterstützte Modelle/`auto` zentral behandelt werden |
    | `tool-stream-default-on` | Standardmäßig aktivierter `tool_stream`-Wrapper für Provider wie Z.AI, die Tool-Streaming wünschen, sofern es nicht explizit deaktiviert wird |

    Reale gebündelte Beispiele:

    - `google` und `google-gemini-cli`: `google-thinking`
    - `kilocode`: `kilocode-thinking`
    - `moonshot`: `moonshot-thinking`
    - `minimax` und `minimax-portal`: `minimax-fast-mode`
    - `openai` und `openai-codex`: `openai-responses-defaults`
    - `openrouter`: `openrouter-thinking`
    - `zai`: `tool-stream-default-on`

    `openclaw/plugin-sdk/provider-model-shared` exportiert außerdem die Replay-Family-
    Enum sowie die gemeinsamen Helper, aus denen diese Familien aufgebaut sind. Häufige öffentliche
    Exporte umfassen:

    - `ProviderReplayFamily`
    - `buildProviderReplayFamilyHooks(...)`
    - gemeinsame Replay-Builder wie `buildOpenAICompatibleReplayPolicy(...)`,
      `buildAnthropicReplayPolicyForModel(...)`,
      `buildGoogleGeminiReplayPolicy(...)` und
      `buildHybridAnthropicOrOpenAIReplayPolicy(...)`
    - Gemini-Replay-Helper wie `sanitizeGoogleGeminiReplayHistory(...)`
      und `resolveTaggedReasoningOutputMode()`
    - Endpunkt-/Modell-Helper wie `resolveProviderEndpoint(...)`,
      `normalizeProviderId(...)`, `normalizeGooglePreviewModelId(...)` und
      `normalizeNativeXaiModelId(...)`

    `openclaw/plugin-sdk/provider-stream` stellt sowohl den Family-Builder als
    auch die öffentlichen Wrapper-Helper bereit, die diese Familien wiederverwenden. Häufige öffentliche
    Exporte umfassen:

    - `ProviderStreamFamily`
    - `buildProviderStreamFamilyHooks(...)`
    - `composeProviderStreamWrappers(...)`
    - gemeinsame OpenAI-/Codex-Wrapper wie
      `createOpenAIAttributionHeadersWrapper(...)`,
      `createOpenAIFastModeWrapper(...)`,
      `createOpenAIServiceTierWrapper(...)`,
      `createOpenAIResponsesContextManagementWrapper(...)` und
      `createCodexNativeWebSearchWrapper(...)`
    - gemeinsame Proxy-/Provider-Wrapper wie `createOpenRouterWrapper(...)`,
      `createToolStreamWrapper(...)` und `createMinimaxFastModeWrapper(...)`

    Einige Stream-Helper bleiben absichtlich Provider-lokal. Aktuelles gebündeltes
    Beispiel: `@openclaw/anthropic-provider` exportiert
    `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
    `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` und die
    Low-Level-Builder für Anthropic-Wrapper über die öffentliche Abgrenzung `api.ts` /
    `contract-api.ts`. Diese Helper bleiben Anthropic-spezifisch, weil
    sie außerdem Claude-OAuth-Beta-Handling und `context1m`-Gating codieren.

    Andere gebündelte Provider behalten ebenfalls transport-spezifische Wrapper lokal, wenn
    das Verhalten nicht sauber zwischen Familien geteilt werden kann. Aktuelles Beispiel: Das
    gebündelte xAI-Plugin hält die native Gestaltung von xAI Responses in seinem eigenen
    `wrapStreamFn`, einschließlich Umschreiben von `/fast`-Aliasen, standardmäßigem `tool_stream`,
    Bereinigung nicht unterstützter strikter Tools und Entfernen
    xAI-spezifischer Reasoning-Payloads.

    `openclaw/plugin-sdk/provider-tools` stellt derzeit eine gemeinsame
    Tool-Schema-Familie plus gemeinsame Schema-/Kompatibilitäts-Helper bereit:

    - `ProviderToolCompatFamily` dokumentiert heute das gemeinsame Family-Inventar.
    - `buildProviderToolCompatFamilyHooks("gemini")` verdrahtet die Bereinigung und
      Diagnose von Gemini-Schemata für Provider, die Gemini-sichere Tool-Schemata benötigen.
    - `normalizeGeminiToolSchemas(...)` und `inspectGeminiToolSchemas(...)`
      sind die zugrunde liegenden öffentlichen Helper für Gemini-Schemata.
    - `resolveXaiModelCompatPatch()` gibt den gebündelten xAI-Kompatibilitätspatch zurück:
      `toolSchemaProfile: "xai"`, nicht unterstützte Schema-Schlüsselwörter, native
      Unterstützung für `web_search` und Decodierung von Tool-Call-Argumenten mit HTML-Entities.
    - `applyXaiModelCompat(model)` wendet denselben xAI-Kompatibilitätspatch auf ein
      aufgelöstes Modell an, bevor es den Runner erreicht.

    Reales gebündeltes Beispiel: Das xAI-Plugin verwendet `normalizeResolvedModel` plus
    `contributeResolvedModelCompat`, damit diese Kompatibilitätsmetadaten dem
    Provider zugeordnet bleiben, anstatt xAI-Regeln hart im Core zu codieren.

    Dasselbe Muster am Paket-Root unterstützt auch andere gebündelte Provider:

    - `@openclaw/openai-provider`: `api.ts` exportiert Provider-Builder,
      Standardmodell-Helper und Builder für Realtime-Provider
    - `@openclaw/openrouter-provider`: `api.ts` exportiert den Provider-Builder
      plus Onboarding-/Konfigurations-Helper

    <Tabs>
      <Tab title="Token-Austausch">
        Für Provider, die vor jedem Inferenzaufruf einen Token-Austausch benötigen:

        ```typescript
        prepareRuntimeAuth: async (ctx) => {
          const exchanged = await exchangeToken(ctx.apiKey);
          return {
            apiKey: exchanged.token,
            baseUrl: exchanged.baseUrl,
            expiresAt: exchanged.expiresAt,
          };
        },
        ```
      </Tab>
      <Tab title="Benutzerdefinierte Header">
        Für Provider, die benutzerdefinierte Request-Header oder Änderungen am Body benötigen:

        ```typescript
        // wrapStreamFn returns a StreamFn derived from ctx.streamFn
        wrapStreamFn: (ctx) => {
          if (!ctx.streamFn) return undefined;
          const inner = ctx.streamFn;
          return async (params) => {
            params.headers = {
              ...params.headers,
              "X-Acme-Version": "2",
            };
            return inner(params);
          };
        },
        ```
      </Tab>
      <Tab title="Native Transport-Identität">
        Für Provider, die native Request-/Sitzungs-Header oder Metadaten auf
        generischen HTTP- oder WebSocket-Transporten benötigen:

        ```typescript
        resolveTransportTurnState: (ctx) => ({
          headers: {
            "x-request-id": ctx.turnId,
          },
          metadata: {
            session_id: ctx.sessionId ?? "",
            turn_id: ctx.turnId,
          },
        }),
        resolveWebSocketSessionPolicy: (ctx) => ({
          headers: {
            "x-session-id": ctx.sessionId ?? "",
          },
          degradeCooldownMs: 60_000,
        }),
        ```
      </Tab>
      <Tab title="Nutzung und Abrechnung">
        Für Provider, die Nutzungs-/Abrechnungsdaten bereitstellen:

        ```typescript
        resolveUsageAuth: async (ctx) => {
          const auth = await ctx.resolveOAuthToken();
          return auth ? { token: auth.token } : null;
        },
        fetchUsageSnapshot: async (ctx) => {
          return await fetchAcmeUsage(ctx.token, ctx.timeoutMs);
        },
        ```
      </Tab>
    </Tabs>

    <Accordion title="Alle verfügbaren Provider-Hooks">
      OpenClaw ruft Hooks in dieser Reihenfolge auf. Die meisten Provider verwenden nur 2-3:

      | # | Hook | Wann er verwendet wird |
      | --- | --- | --- |
      | 1 | `catalog` | Modellkatalog oder Standardwerte für Base-URL |
      | 2 | `applyConfigDefaults` | Provider-eigene globale Standardwerte während der Materialisierung der Konfiguration |
      | 3 | `normalizeModelId` | Bereinigung veralteter/Vorschau-Aliasse von Modell-IDs vor der Suche |
      | 4 | `normalizeTransport` | Bereinigung von `api` / `baseUrl` für die Provider-Familie vor der generischen Modellerstellung |
      | 5 | `normalizeConfig` | `models.providers.<id>`-Konfiguration normalisieren |
      | 6 | `applyNativeStreamingUsageCompat` | Native Streaming-Usage-Kompatibilitäts-Umschreibungen für Konfigurations-Provider |
      | 7 | `resolveConfigApiKey` | Provider-eigene Auflösung von Env-Marker-Authentifizierung |
      | 8 | `resolveSyntheticAuth` | Synthetische Authentifizierung lokal/selbst gehostet oder konfigurationsgestützt |
      | 9 | `shouldDeferSyntheticProfileAuth` | Platziert synthetische Platzhalter für gespeicherte Profile hinter Env-/Konfigurations-Authentifizierung |
      | 10 | `resolveDynamicModel` | Beliebige Upstream-Modell-IDs akzeptieren |
      | 11 | `prepareDynamicModel` | Asynchrones Abrufen von Metadaten vor der Auflösung |
      | 12 | `normalizeResolvedModel` | Umschreibungen des Transports vor dem Runner |

      Hinweise zum Laufzeit-Fallback:

      - `normalizeConfig` prüft zuerst den passenden Provider, dann andere
        Hook-fähige Provider-Plugins, bis eines die Konfiguration tatsächlich ändert.
        Wenn kein Provider-Hook einen unterstützten Google-Family-Konfigurationseintrag umschreibt,
        wird weiterhin der gebündelte Google-Konfigurations-Normalisierer angewendet.
      - `resolveConfigApiKey` verwendet den Provider-Hook, wenn er bereitgestellt wird. Der gebündelte
        Pfad `amazon-bedrock` hat hier außerdem einen eingebauten AWS-Env-Marker-Resolver,
        auch wenn Bedrock-Laufzeit-Authentifizierung selbst weiterhin die Standardkette des AWS SDK verwendet.
      | 13 | `contributeResolvedModelCompat` | Kompatibilitäts-Flags für Anbietermodelle hinter einem anderen kompatiblen Transport |
      | 14 | `capabilities` | Veralteter statischer Capability-Bag; nur zur Kompatibilität |
      | 15 | `normalizeToolSchemas` | Provider-eigene Bereinigung von Tool-Schemata vor der Registrierung |
      | 16 | `inspectToolSchemas` | Provider-eigene Diagnose für Tool-Schemata |
      | 17 | `resolveReasoningOutputMode` | Vertrag für getaggte vs. native Reasoning-Ausgabe |
      | 18 | `prepareExtraParams` | Standard-Request-Parameter |
      | 19 | `createStreamFn` | Vollständig benutzerdefinierter StreamFn-Transport |
      | 20 | `wrapStreamFn` | Benutzerdefinierte Header-/Body-Wrapper auf dem normalen Stream-Pfad |
      | 21 | `resolveTransportTurnState` | Native Header/Metadaten pro Turn |
      | 22 | `resolveWebSocketSessionPolicy` | Native WS-Sitzungs-Header/Cool-down |
      | 23 | `formatApiKey` | Benutzerdefinierte Form von Laufzeit-Tokens |
      | 24 | `refreshOAuth` | Benutzerdefiniertes OAuth-Refresh |
      | 25 | `buildAuthDoctorHint` | Hinweise zur Reparatur der Authentifizierung |
      | 26 | `matchesContextOverflowError` | Provider-eigene Erkennung von Kontextüberlauf |
      | 27 | `classifyFailoverReason` | Provider-eigene Klassifizierung von Ratenlimit-/Überlastgründen |
      | 28 | `isCacheTtlEligible` | TTL-Gating für Prompt-Cache |
      | 29 | `buildMissingAuthMessage` | Benutzerdefinierter Hinweis bei fehlender Authentifizierung |
      | 30 | `suppressBuiltInModel` | Veraltete Upstream-Zeilen ausblenden |
      | 31 | `augmentModelCatalog` | Synthetische Zeilen für Vorwärtskompatibilität |
      | 32 | `isBinaryThinking` | Binäres Thinking an/aus |
      | 33 | `supportsXHighThinking` | Unterstützung für `xhigh`-Reasoning |
      | 34 | `resolveDefaultThinkingLevel` | Standardrichtlinie für `/think` |
      | 35 | `isModernModelRef` | Live-/Smoke-Matching von Modellen |
      | 36 | `prepareRuntimeAuth` | Token-Austausch vor der Inferenz |
      | 37 | `resolveUsageAuth` | Benutzerdefiniertes Parsen von Nutzungsanmeldedaten |
      | 38 | `fetchUsageSnapshot` | Benutzerdefinierter Nutzungsendpunkt |
      | 39 | `createEmbeddingProvider` | Provider-eigener Embedding-Adapter für Speicher/Suche |
      | 40 | `buildReplayPolicy` | Benutzerdefinierte Richtlinie für Transcript-Replay/-Kompaktierung |
      | 41 | `sanitizeReplayHistory` | Provider-spezifische Replay-Umschreibungen nach generischer Bereinigung |
      | 42 | `validateReplayTurns` | Strikte Validierung von Replay-Turns vor dem eingebetteten Runner |
      | 43 | `onModelSelected` | Callback nach der Auswahl (z. B. Telemetrie) |

      Hinweis zum Prompt-Tuning:

      - `resolveSystemPromptContribution` erlaubt es einem Provider, cache-bewusste
        System-Prompt-Hinweise für eine Modelfamilie zu injizieren. Verwenden Sie dies bevorzugt gegenüber
        `before_prompt_build`, wenn das Verhalten zu einer Provider-/Modellfamilie gehört
        und die stabile/dynamische Cache-Aufteilung erhalten bleiben soll.

      Ausführliche Beschreibungen und Praxisbeispiele finden Sie unter
      [Internals: Provider Runtime Hooks](/de/plugins/architecture#provider-runtime-hooks).
    </Accordion>

  </Step>

  <Step title="Zusätzliche Fähigkeiten hinzufügen (optional)">
    <a id="step-5-add-extra-capabilities"></a>
    Ein Provider-Plugin kann zusätzlich zu Textinferenz Sprachsynthese, Echtzeittranskription,
    Echtzeitstimme, Medienverständnis, Bildgenerierung, Videogenerierung, Web-Abruf
    und Websuche registrieren:

    ```typescript
    register(api) {
      api.registerProvider({ id: "acme-ai", /* ... */ });

      api.registerSpeechProvider({
        id: "acme-ai",
        label: "Acme Speech",
        isConfigured: ({ config }) => Boolean(config.messages?.tts),
        synthesize: async (req) => ({
          audioBuffer: Buffer.from(/* PCM data */),
          outputFormat: "mp3",
          fileExtension: ".mp3",
          voiceCompatible: false,
        }),
      });

      api.registerRealtimeTranscriptionProvider({
        id: "acme-ai",
        label: "Acme Realtime Transcription",
        isConfigured: () => true,
        createSession: (req) => ({
          connect: async () => {},
          sendAudio: () => {},
          close: () => {},
          isConnected: () => true,
        }),
      });

      api.registerRealtimeVoiceProvider({
        id: "acme-ai",
        label: "Acme Realtime Voice",
        isConfigured: ({ providerConfig }) => Boolean(providerConfig.apiKey),
        createBridge: (req) => ({
          connect: async () => {},
          sendAudio: () => {},
          setMediaTimestamp: () => {},
          submitToolResult: () => {},
          acknowledgeMark: () => {},
          close: () => {},
          isConnected: () => true,
        }),
      });

      api.registerMediaUnderstandingProvider({
        id: "acme-ai",
        capabilities: ["image", "audio"],
        describeImage: async (req) => ({ text: "A photo of..." }),
        transcribeAudio: async (req) => ({ text: "Transcript..." }),
      });

      api.registerImageGenerationProvider({
        id: "acme-ai",
        label: "Acme Images",
        generate: async (req) => ({ /* image result */ }),
      });

      api.registerVideoGenerationProvider({
        id: "acme-ai",
        label: "Acme Video",
        capabilities: {
          generate: {
            maxVideos: 1,
            maxDurationSeconds: 10,
            supportsResolution: true,
          },
          imageToVideo: {
            enabled: true,
            maxVideos: 1,
            maxInputImages: 1,
            maxDurationSeconds: 5,
          },
          videoToVideo: {
            enabled: false,
          },
        },
        generateVideo: async (req) => ({ videos: [] }),
      });

      api.registerWebFetchProvider({
        id: "acme-ai-fetch",
        label: "Acme Fetch",
        hint: "Fetch pages through Acme's rendering backend.",
        envVars: ["ACME_FETCH_API_KEY"],
        placeholder: "acme-...",
        signupUrl: "https://acme.example.com/fetch",
        credentialPath: "plugins.entries.acme.config.webFetch.apiKey",
        getCredentialValue: (fetchConfig) => fetchConfig?.acme?.apiKey,
        setCredentialValue: (fetchConfigTarget, value) => {
          const acme = (fetchConfigTarget.acme ??= {});
          acme.apiKey = value;
        },
        createTool: () => ({
          description: "Fetch a page through Acme Fetch.",
          parameters: {},
          execute: async (args) => ({ content: [] }),
        }),
      });

      api.registerWebSearchProvider({
        id: "acme-ai-search",
        label: "Acme Search",
        search: async (req) => ({ content: [] }),
      });
    }
    ```

    OpenClaw klassifiziert dies als Plugin mit **hybrid-capability**. Dies ist das
    empfohlene Muster für Unternehmens-Plugins (ein Plugin pro Anbieter). Siehe
    [Internals: Capability Ownership](/de/plugins/architecture#capability-ownership-model).

    Für Videogenerierung bevorzugen Sie die oben gezeigte, modusbewusste Fähigkeitsform:
    `generate`, `imageToVideo` und `videoToVideo`. Flache aggregierte Felder wie
    `maxInputImages`, `maxInputVideos` und `maxDurationSeconds` reichen
    nicht aus, um Unterstützung für Transformationsmodi oder deaktivierte Modi sauber anzugeben.

    Provider für Musikgenerierung sollten demselben Muster folgen:
    `generate` für reine Prompt-basierte Generierung und `edit` für referenzbildbasierte
    Generierung. Flache aggregierte Felder wie `maxInputImages`,
    `supportsLyrics` und `supportsFormat` reichen nicht aus, um Unterstützung für
    Bearbeitung anzugeben; explizite Blöcke `generate` / `edit` sind der erwartete Vertrag.

  </Step>

  <Step title="Testen">
    <a id="step-6-test"></a>
    ```typescript src/provider.test.ts
    import { describe, it, expect } from "vitest";
    // Export your provider config object from index.ts or a dedicated file
    import { acmeProvider } from "./provider.js";

    describe("acme-ai provider", () => {
      it("resolves dynamic models", () => {
        const model = acmeProvider.resolveDynamicModel!({
          modelId: "acme-beta-v3",
        } as any);
        expect(model.id).toBe("acme-beta-v3");
        expect(model.provider).toBe("acme-ai");
      });

      it("returns catalog when key is available", async () => {
        const result = await acmeProvider.catalog!.run({
          resolveProviderApiKey: () => ({ apiKey: "test-key" }),
        } as any);
        expect(result?.provider?.models).toHaveLength(2);
      });

      it("returns null catalog when no key", async () => {
        const result = await acmeProvider.catalog!.run({
          resolveProviderApiKey: () => ({ apiKey: undefined }),
        } as any);
        expect(result).toBeNull();
      });
    });
    ```

  </Step>
</Steps>

## Auf ClawHub veröffentlichen

Provider-Plugins werden auf dieselbe Weise veröffentlicht wie jedes andere externe Code-Plugin:

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

Verwenden Sie hier nicht den veralteten skill-only-Publish-Alias; Plugin-Pakete sollten
`clawhub package publish` verwenden.

## Dateistruktur

```
<bundled-plugin-root>/acme-ai/
├── package.json              # openclaw.providers-Metadaten
├── openclaw.plugin.json      # Manifest mit Provider-Authentifizierungsmetadaten
├── index.ts                  # definePluginEntry + registerProvider
└── src/
    ├── provider.test.ts      # Tests
    └── usage.ts              # Nutzungsendpunkt (optional)
```

## Referenz zur Katalogreihenfolge

`catalog.order` steuert, wann Ihr Katalog im Verhältnis zu eingebauten
Providern zusammengeführt wird:

| Order     | Wann          | Anwendungsfall                                 |
| --------- | ------------- | ---------------------------------------------- |
| `simple`  | Erster Durchlauf | Einfache Provider mit API-Schlüssel          |
| `profile` | Nach simple   | Provider, die von Authentifizierungsprofilen abhängen |
| `paired`  | Nach profile  | Mehrere verwandte Einträge synthetisieren      |
| `late`    | Letzter Durchlauf | Vorhandene Provider überschreiben (gewinnt bei Kollision) |

## Nächste Schritte

- [Channel Plugins](/de/plugins/sdk-channel-plugins) — wenn Ihr Plugin auch einen Kanal bereitstellt
- [SDK Runtime](/de/plugins/sdk-runtime) — `api.runtime`-Helper (TTS, Suche, Subagent)
- [SDK Overview](/de/plugins/sdk-overview) — vollständige Referenz für Subpath-Importe
- [Plugin Internals](/de/plugins/architecture#provider-runtime-hooks) — Hook-Details und gebündelte Beispiele
