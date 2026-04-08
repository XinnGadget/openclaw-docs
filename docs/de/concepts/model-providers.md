---
read_when:
    - Sie benötigen eine Referenz zur Modelleinrichtung für einzelne Anbieter
    - Sie möchten Beispielkonfigurationen oder CLI-Onboarding-Befehle für Modellanbieter
summary: Übersicht über Modellanbieter mit Beispielkonfigurationen und CLI-Abläufen
title: Modellanbieter
x-i18n:
    generated_at: "2026-04-08T06:03:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: 558ac9e34b67fcc3dd6791a01bebc17e1c34152fa6c5611593d681e8cfa532d9
    source_path: concepts/model-providers.md
    workflow: 15
---

# Modellanbieter

Diese Seite behandelt **LLM-/Modellanbieter** (keine Chat-Kanäle wie WhatsApp/Telegram).
Regeln zur Modellauswahl finden Sie unter [/concepts/models](/de/concepts/models).

## Schnellregeln

- Modellreferenzen verwenden `provider/model` (Beispiel: `opencode/claude-opus-4-6`).
- Wenn Sie `agents.defaults.models` festlegen, wird es zur Allowlist.
- CLI-Helfer: `openclaw onboard`, `openclaw models list`, `openclaw models set <provider/model>`.
- Fallback-Laufzeitregeln, Cooldown-Prüfungen und die Persistenz von Sitzungsüberschreibungen sind in [/concepts/model-failover](/de/concepts/model-failover) dokumentiert.
- `models.providers.*.models[].contextWindow` sind native Modellmetadaten;
  `models.providers.*.models[].contextTokens` ist die effektive Laufzeitgrenze.
- Anbieter-Plugins können Modellkataloge über `registerProvider({ catalog })` einfügen;
  OpenClaw führt diese Ausgabe in `models.providers` zusammen, bevor
  `models.json` geschrieben wird.
- Anbieter-Manifeste können `providerAuthEnvVars` deklarieren, sodass generische
  umgebungsvariablenbasierte Auth-Prüfungen die Plugin-Laufzeit nicht laden
  müssen. Die verbleibende Core-Umgebungsvariablenzuordnung ist jetzt nur noch
  für Nicht-Plugin-/Core-Anbieter und einige generische Vorrangfälle da, etwa
  Anthropic-Onboarding mit API-Schlüssel zuerst.
- Anbieter-Plugins können auch das Laufzeitverhalten des Anbieters über
  `normalizeModelId`, `normalizeTransport`, `normalizeConfig`,
  `applyNativeStreamingUsageCompat`, `resolveConfigApiKey`,
  `resolveSyntheticAuth`, `shouldDeferSyntheticProfileAuth`,
  `resolveDynamicModel`, `prepareDynamicModel`,
  `normalizeResolvedModel`, `contributeResolvedModelCompat`,
  `capabilities`, `normalizeToolSchemas`,
  `inspectToolSchemas`, `resolveReasoningOutputMode`,
  `prepareExtraParams`, `createStreamFn`, `wrapStreamFn`,
  `resolveTransportTurnState`, `resolveWebSocketSessionPolicy`,
  `createEmbeddingProvider`, `formatApiKey`, `refreshOAuth`,
  `buildAuthDoctorHint`,
  `matchesContextOverflowError`, `classifyFailoverReason`,
  `isCacheTtlEligible`, `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `isBinaryThinking`, `supportsXHighThinking`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`,
  `prepareRuntimeAuth`, `resolveUsageAuth`, `fetchUsageSnapshot` und
  `onModelSelected` steuern.
- Hinweis: Laufzeit-`capabilities` des Anbieters sind gemeinsame Runner-Metadaten (Anbieterfamilie, Besonderheiten bei Transkripten/Tools, Transport-/Cache-Hinweise). Sie sind nicht dasselbe wie das [öffentliche Fähigkeitsmodell](/de/plugins/architecture#public-capability-model),
  das beschreibt, was ein Plugin registriert (Textinferenz, Sprache usw.).

## Plugin-eigenes Anbieterverhalten

Anbieter-Plugins können jetzt den Großteil der anbieterspezifischen Logik
übernehmen, während OpenClaw die generische Inferenzschleife beibehält.

Typische Aufteilung:

- `auth[].run` / `auth[].runNonInteractive`: Der Anbieter übernimmt Onboarding-/Login-Abläufe für `openclaw onboard`, `openclaw models auth` und Headless-Einrichtung
- `wizard.setup` / `wizard.modelPicker`: Der Anbieter übernimmt Beschriftungen für Auth-Auswahl, Legacy-Aliasse, Hinweise zur Onboarding-Allowlist und Einrichtungseinträge in Onboarding-/Modellauswahlen
- `catalog`: Der Anbieter erscheint in `models.providers`
- `normalizeModelId`: Der Anbieter normalisiert Legacy-/Vorschau-Modell-IDs vor
  Lookup oder Kanonisierung
- `normalizeTransport`: Der Anbieter normalisiert `api` / `baseUrl` der
  Transportfamilie vor der generischen Modellerstellung; OpenClaw prüft zuerst
  den passenden Anbieter, dann andere hook-fähige Anbieter-Plugins, bis eines
  den Transport tatsächlich ändert
- `normalizeConfig`: Der Anbieter normalisiert die Konfiguration
  `models.providers.<id>`, bevor die Laufzeit sie verwendet; OpenClaw prüft
  zuerst den passenden Anbieter, dann andere hook-fähige Anbieter-Plugins, bis
  eines die Konfiguration tatsächlich ändert. Wenn kein Anbieter-Hook die
  Konfiguration umschreibt, normalisieren gebündelte Google-Familien-Helfer
  weiterhin unterstützte Google-Anbietereinträge.
- `applyNativeStreamingUsageCompat`: Der Anbieter wendet endpointgesteuerte native Streaming-Usage-Kompatibilitätsanpassungen für Konfigurationsanbieter an
- `resolveConfigApiKey`: Der Anbieter löst umgebungsmarkierungsbasierte Auth für Konfigurationsanbieter auf, ohne das vollständige Laufzeit-Auth laden zu müssen. `amazon-bedrock` hat hier außerdem einen eingebauten AWS-Umgebungsmarkierungs-Resolver, obwohl die Bedrock-Laufzeit-Auth die Standardkette des AWS SDK verwendet.
- `resolveSyntheticAuth`: Der Anbieter kann lokale/self-hosted oder andere
  konfigurationsgestützte Auth-Verfügbarkeit bereitstellen, ohne Klartext-Geheimnisse zu speichern
- `shouldDeferSyntheticProfileAuth`: Der Anbieter kann gespeicherte synthetische Profilplatzhalter als nachrangig gegenüber umgebungs-/konfigurationsgestützter Auth markieren
- `resolveDynamicModel`: Der Anbieter akzeptiert Modell-IDs, die noch nicht im
  lokalen statischen Katalog vorhanden sind
- `prepareDynamicModel`: Der Anbieter benötigt eine Metadatenaktualisierung,
  bevor die dynamische Auflösung erneut versucht wird
- `normalizeResolvedModel`: Der Anbieter benötigt Umschreibungen für Transport
  oder Basis-URL
- `contributeResolvedModelCompat`: Der Anbieter steuert Kompatibilitätsflags für seine Anbietermodelle bei, selbst wenn sie über einen anderen kompatiblen Transport ankommen
- `capabilities`: Der Anbieter veröffentlicht Besonderheiten bei Transkripten/Tools/Anbieterfamilien
- `normalizeToolSchemas`: Der Anbieter bereinigt Toolschemas, bevor der eingebettete Runner sie sieht
- `inspectToolSchemas`: Der Anbieter gibt transportspezifische Schemawarnungen nach der Normalisierung aus
- `resolveReasoningOutputMode`: Der Anbieter wählt native gegenüber getaggten Reasoning-Ausgabeverträgen
- `prepareExtraParams`: Der Anbieter legt pro-Modell-Anfrageparameter standardmäßig fest oder normalisiert sie
- `createStreamFn`: Der Anbieter ersetzt den normalen Stream-Pfad durch einen vollständig benutzerdefinierten Transport
- `wrapStreamFn`: Der Anbieter wendet Wrapper für Anfrageheader/-body/Modellkompatibilität an
- `resolveTransportTurnState`: Der Anbieter liefert native Transportheader
  oder Metadaten pro Zug
- `resolveWebSocketSessionPolicy`: Der Anbieter liefert native WebSocket-Sitzungsheader oder eine Sitzungs-Cooldown-Richtlinie
- `createEmbeddingProvider`: Der Anbieter besitzt das Verhalten für Memory-Embeddings, wenn es besser zum Anbieter-Plugin als zur Core-Embedding-Switchboard gehört
- `formatApiKey`: Der Anbieter formatiert gespeicherte Auth-Profile in den zur Laufzeit erwarteten `apiKey`-String des Transports
- `refreshOAuth`: Der Anbieter übernimmt OAuth-Aktualisierung, wenn die gemeinsamen `pi-ai`-Refresher nicht ausreichen
- `buildAuthDoctorHint`: Der Anbieter hängt Reparaturhinweise an, wenn die OAuth-Aktualisierung fehlschlägt
- `matchesContextOverflowError`: Der Anbieter erkennt anbieterspezifische Fehler bei Kontextfensterüberläufen, die generische Heuristiken übersehen würden
- `classifyFailoverReason`: Der Anbieter ordnet anbieterspezifische rohe Transport-/API-Fehler Failover-Gründen wie Ratenlimit oder Überlastung zu
- `isCacheTtlEligible`: Der Anbieter entscheidet, welche Upstream-Modell-IDs Prompt-Cache-TTL unterstützen
- `buildMissingAuthMessage`: Der Anbieter ersetzt den generischen Fehler des Auth-Speichers durch einen anbieterspezifischen Wiederherstellungshinweis
- `suppressBuiltInModel`: Der Anbieter blendet veraltete Upstream-Zeilen aus und kann für direkte Auflösungsfehler einen anbieterdefinierten Fehler zurückgeben
- `augmentModelCatalog`: Der Anbieter hängt nach Erkennung und Konfigurationszusammenführung synthetische/abschließende Katalogzeilen an
- `isBinaryThinking`: Der Anbieter besitzt die binäre Ein/Aus-Thinking-UX
- `supportsXHighThinking`: Der Anbieter aktiviert `xhigh` für ausgewählte Modelle
- `resolveDefaultThinkingLevel`: Der Anbieter besitzt die standardmäßige `/think`-Richtlinie für eine Modellfamilie
- `applyConfigDefaults`: Der Anbieter wendet anbieterspezifische globale Standardwerte während der Konfigurationsmaterialisierung anhand von Auth-Modus, Umgebung oder Modellfamilie an
- `isModernModelRef`: Der Anbieter besitzt die Zuordnung bevorzugter Modelle für live/smoke
- `prepareRuntimeAuth`: Der Anbieter wandelt konfigurierte Anmeldedaten in ein kurzlebiges Laufzeittoken um
- `resolveUsageAuth`: Der Anbieter löst Nutzungs-/Kontingent-Anmeldedaten für `/usage` und verwandte Status-/Berichtsoberflächen auf
- `fetchUsageSnapshot`: Der Anbieter übernimmt Abruf/Parsing des Nutzungsendpunkts, während der Core weiterhin die Zusammenfassungs-Hülle und Formatierung übernimmt
- `onModelSelected`: Der Anbieter führt Seiteneffekte nach der Modellauswahl aus, etwa Telemetrie oder anbieterdefinierte Sitzungsbuchhaltung

Aktuelle gebündelte Beispiele:

- `anthropic`: Claude-4.6-Vorwärtskompatibilitäts-Fallback, Auth-Reparaturhinweise, Abruf des Nutzungsendpunkts, Cache-TTL-/Anbieterfamilien-Metadaten und auth-bewusste globale Konfigurationsstandards
- `amazon-bedrock`: anbieterdefinierte Erkennung von Kontextüberlauf und Klassifizierung von Failover-Gründen für Bedrock-spezifische Throttle-/Not-ready-Fehler sowie die gemeinsame Replay-Familie `anthropic-by-model` für Claude-spezifische Replay-Richtlinienwächter auf Anthropic-Datenverkehr
- `anthropic-vertex`: Claude-spezifische Replay-Richtlinienwächter für Anthropic-Messages-Datenverkehr
- `openrouter`: Durchreichen von Modell-IDs, Anfrage-Wrapper, Hinweise zu Anbieterfähigkeiten, Bereinigung von Gemini-Thought-Signatures bei Proxy-Gemini-Datenverkehr, Proxy-Reasoning-Injektion über die Stream-Familie `openrouter-thinking`, Weiterleitung von Routing-Metadaten und Cache-TTL-Richtlinie
- `github-copilot`: Onboarding/Gerätelogin, Vorwärtskompatibilitäts-Fallback für Modelle, Claude-Thinking-Transkripthinweise, Laufzeit-Token-Austausch und Abruf des Nutzungsendpunkts
- `openai`: GPT-5.4-Vorwärtskompatibilitäts-Fallback, direkte OpenAI-Transportnormalisierung, Codex-bewusste Missing-Auth-Hinweise, Spark-Unterdrückung, synthetische OpenAI-/Codex-Katalogzeilen, Thinking-/Live-Modell-Richtlinie, Alias-Normalisierung von Usage-Token (`input` / `output` und `prompt` / `completion`-Familien), die gemeinsame Stream-Familie `openai-responses-defaults` für native OpenAI-/Codex-Wrapper, Anbieterfamilien-Metadaten, gebündelte Registrierung des Bildgenerierungsanbieters für `gpt-image-1` und gebündelte Registrierung des Videogenerierungsanbieters für `sora-2`
- `google` und `google-gemini-cli`: Gemini-3.1-Vorwärtskompatibilitäts-Fallback, native Gemini-Replay-Validierung, Bereinigung von Bootstrap-Replays, getaggter Reasoning-Ausgabemodus, Modern-Model-Matching, gebündelte Registrierung des Bildgenerierungsanbieters für Gemini-Image-Preview-Modelle und gebündelte Registrierung des Videogenerierungsanbieters für Veo-Modelle; Gemini CLI OAuth besitzt außerdem die Formatierung von Auth-Profil-Token, Parsing von Usage-Token und Abruf des Kontingentendpunkts für Nutzungsoberflächen
- `moonshot`: gemeinsamer Transport, plugin-eigene Normalisierung von Thinking-Payloads
- `kilocode`: gemeinsamer Transport, plugin-eigene Anfrageheader, Normalisierung von Reasoning-Payloads, Bereinigung von Proxy-Gemini-Thought-Signatures und Cache-TTL-Richtlinie
- `zai`: GLM-5-Vorwärtskompatibilitäts-Fallback, Standardwerte für `tool_stream`, Cache-TTL-Richtlinie, Richtlinie für binäres Thinking/live-Modelle sowie Usage-Auth und Abruf von Kontingenten; unbekannte `glm-5*`-IDs werden aus der gebündelten Vorlage `glm-4.7` synthetisiert
- `xai`: native Normalisierung des Responses-Transports, Umschreibungen des Alias `/fast` für schnelle Grok-Varianten, Standard-`tool_stream`, xAI-spezifische Bereinigung von Toolschemas / Reasoning-Payloads und gebündelte Registrierung des Videogenerierungsanbieters für `grok-imagine-video`
- `mistral`: plugin-eigene Fähigkeitsmetadaten
- `opencode` und `opencode-go`: plugin-eigene Fähigkeitsmetadaten sowie Bereinigung von Proxy-Gemini-Thought-Signatures
- `alibaba`: plugin-eigener Videogenerierungskatalog für direkte Wan-Modellreferenzen wie `alibaba/wan2.6-t2v`
- `byteplus`: plugin-eigene Kataloge sowie gebündelte Registrierung des Videogenerierungsanbieters für Seedance-Text-zu-Video-/Bild-zu-Video-Modelle
- `fal`: gebündelte Registrierung des Videogenerierungsanbieters für gehostete Drittanbieter-Registrierung des Bildgenerierungsanbieters für FLUX-Bildmodelle sowie gebündelte Registrierung des Videogenerierungsanbieters für gehostete Drittanbieter-Videomodelle
- `cloudflare-ai-gateway`, `huggingface`, `kimi`, `nvidia`, `qianfan`,
  `stepfun`, `synthetic`, `venice`, `vercel-ai-gateway` und `volcengine`:
  nur plugin-eigene Kataloge
- `qwen`: plugin-eigene Kataloge für Textmodelle sowie gemeinsame Registrierungen von Media-Understanding- und Videogenerierungsanbietern für seine multimodalen Oberflächen; Qwen-Videogenerierung verwendet die Standard-DashScope-Videoendpunkte mit gebündelten Wan-Modellen wie `wan2.6-t2v` und `wan2.7-r2v`
- `runway`: plugin-eigene Registrierung des Videogenerierungsanbieters für native aufgabenbasierte Runway-Modelle wie `gen4.5`
- `minimax`: plugin-eigene Kataloge, gebündelte Registrierung des Videogenerierungsanbieters für Hailuo-Videomodelle, gebündelte Registrierung des Bildgenerierungsanbieters für `image-01`, hybride Auswahl von Anthropic-/OpenAI-Replay-Richtlinien sowie Usage-Auth-/Snapshot-Logik
- `together`: plugin-eigene Kataloge sowie gebündelte Registrierung des Videogenerierungsanbieters für Wan-Videomodelle
- `xiaomi`: plugin-eigene Kataloge sowie Usage-Auth-/Snapshot-Logik

Das gebündelte Plugin `openai` besitzt jetzt beide Anbieter-IDs: `openai` und
`openai-codex`.

Damit sind Anbieter abgedeckt, die noch in die normalen Transporte von OpenClaw passen. Ein Anbieter, der einen vollständig benutzerdefinierten Anfrage-Executor benötigt, ist eine separate, tiefere Erweiterungsoberfläche.

## API-Schlüsselrotation

- Unterstützt generische Anbieterrotation für ausgewählte Anbieter.
- Konfigurieren Sie mehrere Schlüssel über:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY` (einzelne Live-Überschreibung, höchste Priorität)
  - `<PROVIDER>_API_KEYS` (durch Komma oder Semikolon getrennte Liste)
  - `<PROVIDER>_API_KEY` (primärer Schlüssel)
  - `<PROVIDER>_API_KEY_*` (nummerierte Liste, z. B. `<PROVIDER>_API_KEY_1`)
- Für Google-Anbieter wird `GOOGLE_API_KEY` zusätzlich als Fallback einbezogen.
- Die Reihenfolge der Schlüsselauswahl bewahrt die Priorität und dedupliziert Werte.
- Anfragen werden nur bei Antworten mit Ratenlimit mit dem nächsten Schlüssel wiederholt (zum Beispiel `429`, `rate_limit`, `quota`, `resource exhausted`, `Too many
concurrent requests`, `ThrottlingException`, `concurrency limit reached`,
  `workers_ai ... quota limit exceeded` oder periodische Usage-Limit-Meldungen).
- Fehler ohne Ratenlimit schlagen sofort fehl; es wird keine Schlüsselrotation versucht.
- Wenn alle Kandidatenschlüssel fehlschlagen, wird der letzte Fehler des letzten Versuchs zurückgegeben.

## Integrierte Anbieter (pi-ai-Katalog)

OpenClaw wird mit dem pi‑ai-Katalog ausgeliefert. Diese Anbieter erfordern **keine**
`models.providers`-Konfiguration; legen Sie einfach Auth fest und wählen Sie ein Modell aus.

### OpenAI

- Anbieter: `openai`
- Auth: `OPENAI_API_KEY`
- Optionale Rotation: `OPENAI_API_KEYS`, `OPENAI_API_KEY_1`, `OPENAI_API_KEY_2` sowie `OPENCLAW_LIVE_OPENAI_KEY` (einzelne Überschreibung)
- Beispielmodelle: `openai/gpt-5.4`, `openai/gpt-5.4-pro`
- CLI: `openclaw onboard --auth-choice openai-api-key`
- Der Standardtransport ist `auto` (zuerst WebSocket, dann SSE als Fallback)
- Pro Modell überschreiben über `agents.defaults.models["openai/<model>"].params.transport` (`"sse"`, `"websocket"` oder `"auto"`)
- OpenAI-Responses-WebSocket-Aufwärmen ist standardmäßig über `params.openaiWsWarmup` aktiviert (`true`/`false`)
- OpenAI-Prioritätsverarbeitung kann über `agents.defaults.models["openai/<model>"].params.serviceTier` aktiviert werden
- `/fast` und `params.fastMode` ordnen direkte `openai/*`-Responses-Anfragen auf `api.openai.com` `service_tier=priority` zu
- Verwenden Sie `params.serviceTier`, wenn Sie einen expliziten Tier statt des gemeinsamen `/fast`-Schalters möchten
- Versteckte OpenClaw-Zuordnungsheader (`originator`, `version`,
  `User-Agent`) werden nur auf nativem OpenAI-Datenverkehr zu `api.openai.com` angewendet, nicht auf generischen OpenAI-kompatiblen Proxys
- Native OpenAI-Routen behalten auch Responses-`store`, Prompt-Cache-Hinweise und OpenAI-Reasoning-Kompatibilitäts-Payload-Shaping bei; Proxy-Routen nicht
- `openai/gpt-5.3-codex-spark` wird in OpenClaw absichtlich unterdrückt, weil die Live-OpenAI-API es ablehnt; Spark wird als nur für Codex behandelt

```json5
{
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

### Anthropic

- Anbieter: `anthropic`
- Auth: `ANTHROPIC_API_KEY`
- Optionale Rotation: `ANTHROPIC_API_KEYS`, `ANTHROPIC_API_KEY_1`, `ANTHROPIC_API_KEY_2` sowie `OPENCLAW_LIVE_ANTHROPIC_KEY` (einzelne Überschreibung)
- Beispielmodell: `anthropic/claude-opus-4-6`
- CLI: `openclaw onboard --auth-choice apiKey`
- Direkte öffentliche Anthropic-Anfragen unterstützen den gemeinsamen `/fast`-Schalter und `params.fastMode`, einschließlich per API-Schlüssel und OAuth authentifiziertem Datenverkehr an `api.anthropic.com`; OpenClaw ordnet dies Anthropic-`service_tier` zu (`auto` vs `standard_only`)
- Anthropic-Hinweis: Anthropic-Mitarbeiter haben uns mitgeteilt, dass OpenClaw-artige Claude-CLI-Nutzung wieder erlaubt ist, daher behandelt OpenClaw die Wiederverwendung von Claude CLI und die Nutzung von `claude -p` für diese Integration als zulässig, sofern Anthropic keine neue Richtlinie veröffentlicht.
- Anthropic-Setup-Token bleibt als unterstützter OpenClaw-Tokenpfad verfügbar, aber OpenClaw bevorzugt jetzt, wenn verfügbar, die Wiederverwendung von Claude CLI und `claude -p`.

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

### OpenAI Code (Codex)

- Anbieter: `openai-codex`
- Auth: OAuth (ChatGPT)
- Beispielmodell: `openai-codex/gpt-5.4`
- CLI: `openclaw onboard --auth-choice openai-codex` oder `openclaw models auth login --provider openai-codex`
- Der Standardtransport ist `auto` (zuerst WebSocket, dann SSE als Fallback)
- Pro Modell überschreiben über `agents.defaults.models["openai-codex/<model>"].params.transport` (`"sse"`, `"websocket"` oder `"auto"`)
- `params.serviceTier` wird auch bei nativen Codex-Responses-Anfragen (`chatgpt.com/backend-api`) weitergeleitet
- Versteckte OpenClaw-Zuordnungsheader (`originator`, `version`,
  `User-Agent`) werden nur auf nativem Codex-Datenverkehr zu
  `chatgpt.com/backend-api` angehängt, nicht auf generischen OpenAI-kompatiblen Proxys
- Verwendet denselben `/fast`-Schalter und dieselbe `params.fastMode`-Konfiguration wie direktes `openai/*`; OpenClaw ordnet dies `service_tier=priority` zu
- `openai-codex/gpt-5.3-codex-spark` bleibt verfügbar, wenn der Codex-OAuth-Katalog es bereitstellt; abhängig von Berechtigungen
- `openai-codex/gpt-5.4` behält natives `contextWindow = 1050000` und ein Standard-Laufzeit-`contextTokens = 272000`; überschreiben Sie die Laufzeitgrenze mit `models.providers.openai-codex.models[].contextTokens`
- Richtlinienhinweis: OpenAI-Codex-OAuth wird explizit für externe Tools/Workflows wie OpenClaw unterstützt.

```json5
{
  agents: { defaults: { model: { primary: "openai-codex/gpt-5.4" } } },
}
```

```json5
{
  models: {
    providers: {
      "openai-codex": {
        models: [{ id: "gpt-5.4", contextTokens: 160000 }],
      },
    },
  },
}
```

### Andere abonnementsbasierte gehostete Optionen

- [Qwen Cloud](/de/providers/qwen): Qwen-Cloud-Anbieteroberfläche sowie Alibaba-DashScope- und Coding-Plan-Endpunktzuordnung
- [MiniMax](/de/providers/minimax): MiniMax-Coding-Plan-OAuth- oder API-Schlüsselzugriff
- [GLM Models](/de/providers/glm): Z.AI-Coding-Plan oder allgemeine API-Endpunkte

### OpenCode

- Auth: `OPENCODE_API_KEY` (oder `OPENCODE_ZEN_API_KEY`)
- Zen-Laufzeitanbieter: `opencode`
- Go-Laufzeitanbieter: `opencode-go`
- Beispielmodelle: `opencode/claude-opus-4-6`, `opencode-go/kimi-k2.5`
- CLI: `openclaw onboard --auth-choice opencode-zen` oder `openclaw onboard --auth-choice opencode-go`

```json5
{
  agents: { defaults: { model: { primary: "opencode/claude-opus-4-6" } } },
}
```

### Google Gemini (API-Schlüssel)

- Anbieter: `google`
- Auth: `GEMINI_API_KEY`
- Optionale Rotation: `GEMINI_API_KEYS`, `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`, `GOOGLE_API_KEY` als Fallback sowie `OPENCLAW_LIVE_GEMINI_KEY` (einzelne Überschreibung)
- Beispielmodelle: `google/gemini-3.1-pro-preview`, `google/gemini-3-flash-preview`
- Kompatibilität: Legacy-OpenClaw-Konfiguration mit `google/gemini-3.1-flash-preview` wird zu `google/gemini-3-flash-preview` normalisiert
- CLI: `openclaw onboard --auth-choice gemini-api-key`
- Direkte Gemini-Läufe akzeptieren außerdem `agents.defaults.models["google/<model>"].params.cachedContent`
  (oder das Legacy-`cached_content`), um einen anbieterinternen
  `cachedContents/...`-Handle weiterzuleiten; Gemini-Cache-Treffer erscheinen als OpenClaw-`cacheRead`

### Google Vertex und Gemini CLI

- Anbieter: `google-vertex`, `google-gemini-cli`
- Auth: Vertex verwendet gcloud ADC; Gemini CLI verwendet seinen OAuth-Ablauf
- Vorsicht: Gemini-CLI-OAuth in OpenClaw ist eine inoffizielle Integration. Einige Nutzer haben von Einschränkungen ihres Google-Kontos nach der Nutzung von Drittanbieter-Clients berichtet. Prüfen Sie die Google-Nutzungsbedingungen und verwenden Sie ein nicht kritisches Konto, wenn Sie sich dafür entscheiden.
- Gemini-CLI-OAuth wird als Teil des gebündelten `google`-Plugins ausgeliefert.
  - Installieren Sie zuerst Gemini CLI:
    - `brew install gemini-cli`
    - oder `npm install -g @google/gemini-cli`
  - Aktivieren: `openclaw plugins enable google`
  - Login: `openclaw models auth login --provider google-gemini-cli --set-default`
  - Standardmodell: `google-gemini-cli/gemini-3-flash-preview`
  - Hinweis: Sie fügen **keine** Client-ID oder kein Secret in `openclaw.json` ein. Der CLI-Login-Ablauf speichert Tokens in Auth-Profilen auf dem Gateway-Host.
  - Wenn Anfragen nach dem Login fehlschlagen, setzen Sie `GOOGLE_CLOUD_PROJECT` oder `GOOGLE_CLOUD_PROJECT_ID` auf dem Gateway-Host.
  - Gemini-CLI-JSON-Antworten werden aus `response` geparst; die Nutzung fällt auf
    `stats` zurück, wobei `stats.cached` zu OpenClaw-`cacheRead` normalisiert wird.

### Z.AI (GLM)

- Anbieter: `zai`
- Auth: `ZAI_API_KEY`
- Beispielmodell: `zai/glm-5.1`
- CLI: `openclaw onboard --auth-choice zai-api-key`
  - Aliasse: `z.ai/*` und `z-ai/*` werden zu `zai/*` normalisiert
  - `zai-api-key` erkennt den passenden Z.AI-Endpunkt automatisch; `zai-coding-global`, `zai-coding-cn`, `zai-global` und `zai-cn` erzwingen eine bestimmte Oberfläche

### Vercel AI Gateway

- Anbieter: `vercel-ai-gateway`
- Auth: `AI_GATEWAY_API_KEY`
- Beispielmodell: `vercel-ai-gateway/anthropic/claude-opus-4.6`
- CLI: `openclaw onboard --auth-choice ai-gateway-api-key`

### Kilo Gateway

- Anbieter: `kilocode`
- Auth: `KILOCODE_API_KEY`
- Beispielmodell: `kilocode/kilo/auto`
- CLI: `openclaw onboard --auth-choice kilocode-api-key`
- Basis-URL: `https://api.kilo.ai/api/gateway/`
- Der statische Fallback-Katalog enthält `kilocode/kilo/auto`; die Live-Erkennung unter
  `https://api.kilo.ai/api/gateway/models` kann den Laufzeitkatalog weiter
  erweitern.
- Das genaue Upstream-Routing hinter `kilocode/kilo/auto` gehört zu Kilo Gateway
  und ist nicht in OpenClaw fest codiert.

Siehe [/providers/kilocode](/de/providers/kilocode) für Einrichtungsdetails.

### Andere gebündelte Anbieter-Plugins

- OpenRouter: `openrouter` (`OPENROUTER_API_KEY`)
- Beispielmodell: `openrouter/auto`
- OpenClaw wendet die dokumentierten App-Zuordnungsheader von OpenRouter nur an, wenn die Anfrage tatsächlich an `openrouter.ai` geht
- OpenRouter-spezifische Anthropic-`cache_control`-Marker werden entsprechend nur für verifizierte OpenRouter-Routen aktiviert, nicht für beliebige Proxy-URLs
- OpenRouter bleibt auf dem proxyartigen OpenAI-kompatiblen Pfad, daher wird natives nur-OpenAI-Request-Shaping (`serviceTier`, Responses-`store`,
  Prompt-Cache-Hinweise, OpenAI-Reasoning-Kompatibilitäts-Payloads) nicht weitergeleitet
- Gemini-gestützte OpenRouter-Referenzen behalten nur die Bereinigung von Proxy-Gemini-Thought-Signatures; native Gemini-Replay-Validierung und Bootstrap-Umschreibungen bleiben deaktiviert
- Kilo Gateway: `kilocode` (`KILOCODE_API_KEY`)
- Beispielmodell: `kilocode/kilo/auto`
- Gemini-gestützte Kilo-Referenzen behalten denselben Bereinigungspfad für Proxy-Gemini-Thought-Signatures; `kilocode/kilo/auto` und andere Hinweise auf nicht unterstütztes Proxy-Reasoning überspringen die Proxy-Reasoning-Injektion
- MiniMax: `minimax` (API-Schlüssel) und `minimax-portal` (OAuth)
- Auth: `MINIMAX_API_KEY` für `minimax`; `MINIMAX_OAUTH_TOKEN` oder `MINIMAX_API_KEY` für `minimax-portal`
- Beispielmodell: `minimax/MiniMax-M2.7` oder `minimax-portal/MiniMax-M2.7`
- MiniMax-Onboarding-/API-Schlüssel-Einrichtung schreibt explizite M2.7-Modell-Definitionen mit
  `input: ["text", "image"]`; der gebündelte Anbieterkatalog hält die Chat-Referenzen text-only, bis diese Anbieterkonfiguration materialisiert wird
- Moonshot: `moonshot` (`MOONSHOT_API_KEY`)
- Beispielmodell: `moonshot/kimi-k2.5`
- Kimi Coding: `kimi` (`KIMI_API_KEY` oder `KIMICODE_API_KEY`)
- Beispielmodell: `kimi/kimi-code`
- Qianfan: `qianfan` (`QIANFAN_API_KEY`)
- Beispielmodell: `qianfan/deepseek-v3.2`
- Qwen Cloud: `qwen` (`QWEN_API_KEY`, `MODELSTUDIO_API_KEY` oder `DASHSCOPE_API_KEY`)
- Beispielmodell: `qwen/qwen3.5-plus`
- NVIDIA: `nvidia` (`NVIDIA_API_KEY`)
- Beispielmodell: `nvidia/nvidia/llama-3.1-nemotron-70b-instruct`
- StepFun: `stepfun` / `stepfun-plan` (`STEPFUN_API_KEY`)
- Beispielmodelle: `stepfun/step-3.5-flash`, `stepfun-plan/step-3.5-flash-2603`
- Together: `together` (`TOGETHER_API_KEY`)
- Beispielmodell: `together/moonshotai/Kimi-K2.5`
- Venice: `venice` (`VENICE_API_KEY`)
- Xiaomi: `xiaomi` (`XIAOMI_API_KEY`)
- Beispielmodell: `xiaomi/mimo-v2-flash`
- Vercel AI Gateway: `vercel-ai-gateway` (`AI_GATEWAY_API_KEY`)
- Hugging Face Inference: `huggingface` (`HUGGINGFACE_HUB_TOKEN` oder `HF_TOKEN`)
- Cloudflare AI Gateway: `cloudflare-ai-gateway` (`CLOUDFLARE_AI_GATEWAY_API_KEY`)
- Volcengine: `volcengine` (`VOLCANO_ENGINE_API_KEY`)
- Beispielmodell: `volcengine-plan/ark-code-latest`
- BytePlus: `byteplus` (`BYTEPLUS_API_KEY`)
- Beispielmodell: `byteplus-plan/ark-code-latest`
- xAI: `xai` (`XAI_API_KEY`)
  - Native gebündelte xAI-Anfragen verwenden den xAI-Responses-Pfad
  - `/fast` oder `params.fastMode: true` schreiben `grok-3`, `grok-3-mini`,
    `grok-4` und `grok-4-0709` in ihre `*-fast`-Varianten um
  - `tool_stream` ist standardmäßig aktiviert; setzen Sie
    `agents.defaults.models["xai/<model>"].params.tool_stream` auf `false`, um
    es zu deaktivieren
- Mistral: `mistral` (`MISTRAL_API_KEY`)
- Beispielmodell: `mistral/mistral-large-latest`
- CLI: `openclaw onboard --auth-choice mistral-api-key`
- Groq: `groq` (`GROQ_API_KEY`)
- Cerebras: `cerebras` (`CEREBRAS_API_KEY`)
  - GLM-Modelle auf Cerebras verwenden die IDs `zai-glm-4.7` und `zai-glm-4.6`.
  - OpenAI-kompatible Basis-URL: `https://api.cerebras.ai/v1`.
- GitHub Copilot: `github-copilot` (`COPILOT_GITHUB_TOKEN` / `GH_TOKEN` / `GITHUB_TOKEN`)
- Beispielmodell für Hugging Face Inference: `huggingface/deepseek-ai/DeepSeek-R1`; CLI: `openclaw onboard --auth-choice huggingface-api-key`. Siehe [Hugging Face (Inference)](/de/providers/huggingface).

## Anbieter über `models.providers` (benutzerdefinierte/Basis-URL)

Verwenden Sie `models.providers` (oder `models.json`), um **benutzerdefinierte** Anbieter oder
OpenAI-/Anthropic-kompatible Proxys hinzuzufügen.

Viele der gebündelten Anbieter-Plugins unten veröffentlichen bereits einen Standardkatalog.
Verwenden Sie explizite Einträge `models.providers.<id>` nur dann, wenn Sie die
Standard-Basis-URL, Header oder Modellliste überschreiben möchten.

### Moonshot AI (Kimi)

Moonshot wird als gebündeltes Anbieter-Plugin ausgeliefert. Verwenden Sie
standardmäßig den integrierten Anbieter und fügen Sie nur dann einen expliziten Eintrag `models.providers.moonshot` hinzu, wenn Sie die Basis-URL oder Modellmetadaten überschreiben müssen:

- Anbieter: `moonshot`
- Auth: `MOONSHOT_API_KEY`
- Beispielmodell: `moonshot/kimi-k2.5`
- CLI: `openclaw onboard --auth-choice moonshot-api-key` oder `openclaw onboard --auth-choice moonshot-api-key-cn`

Kimi-K2-Modell-IDs:

[//]: # "moonshot-kimi-k2-model-refs:start"

- `moonshot/kimi-k2.5`
- `moonshot/kimi-k2-thinking`
- `moonshot/kimi-k2-thinking-turbo`
- `moonshot/kimi-k2-turbo`

[//]: # "moonshot-kimi-k2-model-refs:end"

```json5
{
  agents: {
    defaults: { model: { primary: "moonshot/kimi-k2.5" } },
  },
  models: {
    mode: "merge",
    providers: {
      moonshot: {
        baseUrl: "https://api.moonshot.ai/v1",
        apiKey: "${MOONSHOT_API_KEY}",
        api: "openai-completions",
        models: [{ id: "kimi-k2.5", name: "Kimi K2.5" }],
      },
    },
  },
}
```

### Kimi Coding

Kimi Coding verwendet den Anthropic-kompatiblen Endpunkt von Moonshot AI:

- Anbieter: `kimi`
- Auth: `KIMI_API_KEY`
- Beispielmodell: `kimi/kimi-code`

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: { model: { primary: "kimi/kimi-code" } },
  },
}
```

Legacy-`kimi/k2p5` bleibt als Kompatibilitätsmodell-ID akzeptiert.

### Volcano Engine (Doubao)

Volcano Engine (火山引擎) bietet in China Zugriff auf Doubao und andere Modelle.

- Anbieter: `volcengine` (Coding: `volcengine-plan`)
- Auth: `VOLCANO_ENGINE_API_KEY`
- Beispielmodell: `volcengine-plan/ark-code-latest`
- CLI: `openclaw onboard --auth-choice volcengine-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "volcengine-plan/ark-code-latest" } },
  },
}
```

Onboarding verwendet standardmäßig die Coding-Oberfläche, aber der allgemeine `volcengine/*`-Katalog wird gleichzeitig registriert.

In Onboarding-/Modellauswahllisten für die Modellkonfiguration bevorzugt die Volcengine-Auth-Auswahl sowohl Zeilen mit `volcengine/*` als auch mit `volcengine-plan/*`. Wenn diese Modelle noch nicht geladen sind, fällt OpenClaw auf den ungefilterten Katalog zurück, statt eine leere anbieterbezogene Auswahl anzuzeigen.

Verfügbare Modelle:

- `volcengine/doubao-seed-1-8-251228` (Doubao Seed 1.8)
- `volcengine/doubao-seed-code-preview-251028`
- `volcengine/kimi-k2-5-260127` (Kimi K2.5)
- `volcengine/glm-4-7-251222` (GLM 4.7)
- `volcengine/deepseek-v3-2-251201` (DeepSeek V3.2 128K)

Coding-Modelle (`volcengine-plan`):

- `volcengine-plan/ark-code-latest`
- `volcengine-plan/doubao-seed-code`
- `volcengine-plan/kimi-k2.5`
- `volcengine-plan/kimi-k2-thinking`
- `volcengine-plan/glm-4.7`

### BytePlus (International)

BytePlus ARK bietet internationalen Nutzern Zugriff auf dieselben Modelle wie Volcano Engine.

- Anbieter: `byteplus` (Coding: `byteplus-plan`)
- Auth: `BYTEPLUS_API_KEY`
- Beispielmodell: `byteplus-plan/ark-code-latest`
- CLI: `openclaw onboard --auth-choice byteplus-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "byteplus-plan/ark-code-latest" } },
  },
}
```

Onboarding verwendet standardmäßig die Coding-Oberfläche, aber der allgemeine `byteplus/*`-Katalog wird gleichzeitig registriert.

In Onboarding-/Modellauswahllisten für die Modellkonfiguration bevorzugt die BytePlus-Auth-Auswahl sowohl Zeilen mit `byteplus/*` als auch mit `byteplus-plan/*`. Wenn diese Modelle noch nicht geladen sind, fällt OpenClaw auf den ungefilterten Katalog zurück, statt eine leere anbieterbezogene Auswahl anzuzeigen.

Verfügbare Modelle:

- `byteplus/seed-1-8-251228` (Seed 1.8)
- `byteplus/kimi-k2-5-260127` (Kimi K2.5)
- `byteplus/glm-4-7-251222` (GLM 4.7)

Coding-Modelle (`byteplus-plan`):

- `byteplus-plan/ark-code-latest`
- `byteplus-plan/doubao-seed-code`
- `byteplus-plan/kimi-k2.5`
- `byteplus-plan/kimi-k2-thinking`
- `byteplus-plan/glm-4.7`

### Synthetic

Synthetic stellt Anthropic-kompatible Modelle hinter dem Anbieter `synthetic` bereit:

- Anbieter: `synthetic`
- Auth: `SYNTHETIC_API_KEY`
- Beispielmodell: `synthetic/hf:MiniMaxAI/MiniMax-M2.5`
- CLI: `openclaw onboard --auth-choice synthetic-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.5" } },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [{ id: "hf:MiniMaxAI/MiniMax-M2.5", name: "MiniMax M2.5" }],
      },
    },
  },
}
```

### MiniMax

MiniMax wird über `models.providers` konfiguriert, da es benutzerdefinierte Endpunkte verwendet:

- MiniMax OAuth (global): `--auth-choice minimax-global-oauth`
- MiniMax OAuth (CN): `--auth-choice minimax-cn-oauth`
- MiniMax-API-Schlüssel (global): `--auth-choice minimax-global-api`
- MiniMax-API-Schlüssel (CN): `--auth-choice minimax-cn-api`
- Auth: `MINIMAX_API_KEY` für `minimax`; `MINIMAX_OAUTH_TOKEN` oder
  `MINIMAX_API_KEY` für `minimax-portal`

Siehe [/providers/minimax](/de/providers/minimax) für Einrichtungsdetails, Modelloptionen und Konfigurationsausschnitte.

Auf dem Anthropic-kompatiblen Streaming-Pfad von MiniMax deaktiviert OpenClaw Thinking standardmäßig, sofern Sie es nicht explizit festlegen, und `/fast on` schreibt
`MiniMax-M2.7` in `MiniMax-M2.7-highspeed` um.

Aufteilung der plugin-eigenen Fähigkeiten:

- Standardwerte für Text/Chat bleiben auf `minimax/MiniMax-M2.7`
- Bildgenerierung ist `minimax/image-01` oder `minimax-portal/image-01`
- Bildverständnis ist plugin-eigenes `MiniMax-VL-01` auf beiden MiniMax-Auth-Pfaden
- Websuche bleibt auf Anbieter-ID `minimax`

### Ollama

Ollama wird als gebündeltes Anbieter-Plugin ausgeliefert und verwendet die native API von Ollama:

- Anbieter: `ollama`
- Auth: Nicht erforderlich (lokaler Server)
- Beispielmodell: `ollama/llama3.3`
- Installation: [https://ollama.com/download](https://ollama.com/download)

```bash
# Install Ollama, then pull a model:
ollama pull llama3.3
```

```json5
{
  agents: {
    defaults: { model: { primary: "ollama/llama3.3" } },
  },
}
```

Ollama wird lokal unter `http://127.0.0.1:11434` erkannt, wenn Sie mit
`OLLAMA_API_KEY` optieren, und das gebündelte Anbieter-Plugin fügt Ollama direkt zu
`openclaw onboard` und der Modellauswahl hinzu. Siehe [/providers/ollama](/de/providers/ollama)
für Onboarding, Cloud-/lokalen Modus und benutzerdefinierte Konfiguration.

### vLLM

vLLM wird als gebündeltes Anbieter-Plugin für lokale/self-hosted OpenAI-kompatible
Server ausgeliefert:

- Anbieter: `vllm`
- Auth: Optional (abhängig von Ihrem Server)
- Standard-Basis-URL: `http://127.0.0.1:8000/v1`

So aktivieren Sie lokale Auto-Erkennung (jeder Wert funktioniert, wenn Ihr Server keine Auth erzwingt):

```bash
export VLLM_API_KEY="vllm-local"
```

Legen Sie dann ein Modell fest (ersetzen Sie es durch eine der IDs, die von `/v1/models` zurückgegeben werden):

```json5
{
  agents: {
    defaults: { model: { primary: "vllm/your-model-id" } },
  },
}
```

Siehe [/providers/vllm](/de/providers/vllm) für Details.

### SGLang

SGLang wird als gebündeltes Anbieter-Plugin für schnelle self-hosted
OpenAI-kompatible Server ausgeliefert:

- Anbieter: `sglang`
- Auth: Optional (abhängig von Ihrem Server)
- Standard-Basis-URL: `http://127.0.0.1:30000/v1`

So aktivieren Sie lokale Auto-Erkennung (jeder Wert funktioniert, wenn Ihr Server keine Auth erzwingt):

```bash
export SGLANG_API_KEY="sglang-local"
```

Legen Sie dann ein Modell fest (ersetzen Sie es durch eine der IDs, die von `/v1/models` zurückgegeben werden):

```json5
{
  agents: {
    defaults: { model: { primary: "sglang/your-model-id" } },
  },
}
```

Siehe [/providers/sglang](/de/providers/sglang) für Details.

### Lokale Proxys (LM Studio, vLLM, LiteLLM usw.)

Beispiel (OpenAI-kompatibel):

```json5
{
  agents: {
    defaults: {
      model: { primary: "lmstudio/my-local-model" },
      models: { "lmstudio/my-local-model": { alias: "Local" } },
    },
  },
  models: {
    providers: {
      lmstudio: {
        baseUrl: "http://localhost:1234/v1",
        apiKey: "LMSTUDIO_KEY",
        api: "openai-completions",
        models: [
          {
            id: "my-local-model",
            name: "Local Model",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 200000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
}
```

Hinweise:

- Für benutzerdefinierte Anbieter sind `reasoning`, `input`, `cost`, `contextWindow` und `maxTokens` optional.
  Wenn sie weggelassen werden, verwendet OpenClaw standardmäßig:
  - `reasoning: false`
  - `input: ["text"]`
  - `cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 }`
  - `contextWindow: 200000`
  - `maxTokens: 8192`
- Empfohlen: Legen Sie explizite Werte fest, die zu den Grenzen Ihres Proxys/Modells passen.
- Für `api: "openai-completions"` auf nicht nativen Endpunkten (jede nicht leere `baseUrl`, deren Host nicht `api.openai.com` ist), erzwingt OpenClaw `compat.supportsDeveloperRole: false`, um Provider-400-Fehler für nicht unterstützte `developer`-Rollen zu vermeiden.
- Proxyartige OpenAI-kompatible Routen überspringen ebenfalls natives nur-OpenAI-Request-Shaping: kein `service_tier`, kein Responses-`store`, keine Prompt-Cache-Hinweise, kein OpenAI-Reasoning-Kompatibilitäts-Payload-Shaping und keine versteckten OpenClaw-Zuordnungsheader.
- Wenn `baseUrl` leer ist oder fehlt, behält OpenClaw das Standard-OpenAI-Verhalten bei (das zu `api.openai.com` aufgelöst wird).
- Aus Sicherheitsgründen wird ein explizites `compat.supportsDeveloperRole: true` auf nicht nativen `openai-completions`-Endpunkten weiterhin überschrieben.

## CLI-Beispiele

```bash
openclaw onboard --auth-choice opencode-zen
openclaw models set opencode/claude-opus-4-6
openclaw models list
```

Siehe auch: [/gateway/configuration](/de/gateway/configuration) für vollständige Konfigurationsbeispiele.

## Verwandt

- [Models](/de/concepts/models) — Modellkonfiguration und Aliasse
- [Model Failover](/de/concepts/model-failover) — Fallback-Ketten und Wiederholungsverhalten
- [Configuration Reference](/de/gateway/configuration-reference#agent-defaults) — Modellkonfigurationsschlüssel
- [Providers](/de/providers) — Einrichtungsanleitungen pro Anbieter
