---
read_when:
    - Sie benötigen eine Referenz zur Modelleinrichtung nach Anbieter
    - Sie möchten Beispielkonfigurationen oder CLI-Onboarding-Befehle für Modellanbieter
summary: Überblick über Modellanbieter mit Beispielkonfigurationen und CLI-Abläufen
title: Modellanbieter
x-i18n:
    generated_at: "2026-04-09T01:29:26Z"
    model: gpt-5.4
    provider: openai
    source_hash: 53e3141256781002bbe1d7e7b78724a18d061fcf36a203baae04a091b8c9ea1b
    source_path: concepts/model-providers.md
    workflow: 15
---

# Modellanbieter

Diese Seite behandelt **LLM-/Modellanbieter** (nicht Chat-Kanäle wie WhatsApp/Telegram).
Regeln zur Modellauswahl finden Sie unter [/concepts/models](/de/concepts/models).

## Kurzregeln

- Modellreferenzen verwenden `provider/model` (Beispiel: `opencode/claude-opus-4-6`).
- Wenn Sie `agents.defaults.models` festlegen, wird es zur Allowlist.
- CLI-Helfer: `openclaw onboard`, `openclaw models list`, `openclaw models set <provider/model>`.
- Fallback-Laufzeitregeln, Cooldown-Prüfungen und die Persistenz von Sitzungsüberschreibungen
  sind in [/concepts/model-failover](/de/concepts/model-failover)
  dokumentiert.
- `models.providers.*.models[].contextWindow` sind native Modellmetadaten;
  `models.providers.*.models[].contextTokens` ist die effektive Laufzeitgrenze.
- Anbieter-Plugins können Modellkataloge über `registerProvider({ catalog })` einfügen;
  OpenClaw führt diese Ausgabe in `models.providers` zusammen, bevor
  `models.json` geschrieben wird.
- Anbieter-Manifeste können `providerAuthEnvVars` und
  `providerAuthAliases` deklarieren, sodass generische authentifizierungsbasierte Umgebungsvariablen-Prüfungen und Anbietervarianten
  keine Plugin-Laufzeit laden müssen. Die verbleibende Kern-Zuordnung von Umgebungsvariablen ist jetzt
  nur noch für Nicht-Plugin-/Kern-Anbieter und einige generische Prioritätsfälle gedacht,
  wie z. B. Anthropic-Onboarding mit API-Schlüssel zuerst.
- Anbieter-Plugins können auch das Laufzeitverhalten von Anbietern übernehmen über
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
  `onModelSelected`.
- Hinweis: Laufzeit-`capabilities` des Anbieters sind gemeinsame Runner-Metadaten (Anbieter-
  Familie, Eigenheiten bei Transkripten/Tooling, Transport-/Cache-Hinweise). Sie sind nicht
  identisch mit dem [öffentlichen Fähigkeitsmodell](/de/plugins/architecture#public-capability-model),
  das beschreibt, was ein Plugin registriert (Textinferenz, Sprache usw.).

## Plugin-eigenes Anbieterverhalten

Anbieter-Plugins können jetzt den Großteil der anbieterbezogenen Logik übernehmen, während OpenClaw
die generische Inferenzschleife beibehält.

Typische Aufteilung:

- `auth[].run` / `auth[].runNonInteractive`: Anbieter besitzt Onboarding-/Login-
  Abläufe für `openclaw onboard`, `openclaw models auth` und kopflose Einrichtung
- `wizard.setup` / `wizard.modelPicker`: Anbieter besitzt Beschriftungen für Authentifizierungsoptionen,
  Legacy-Aliase, Hinweise zur Allowlist beim Onboarding und Einträge zur Einrichtung in Onboarding-/Modellauswahlen
- `catalog`: Anbieter erscheint in `models.providers`
- `normalizeModelId`: Anbieter normalisiert Legacy-/Vorschau-Modell-IDs vor
  Lookup oder Kanonisierung
- `normalizeTransport`: Anbieter normalisiert `api` / `baseUrl` der Transportfamilie
  vor der generischen Modellzusammenstellung; OpenClaw prüft zuerst den passenden Anbieter,
  dann andere Hook-fähige Anbieter-Plugins, bis eines den
  Transport tatsächlich ändert
- `normalizeConfig`: Anbieter normalisiert die Konfiguration `models.providers.<id>`, bevor
  die Laufzeit sie verwendet; OpenClaw prüft zuerst den passenden Anbieter, dann andere
  Hook-fähige Anbieter-Plugins, bis eines die Konfiguration tatsächlich ändert. Falls kein
  Anbieter-Hook die Konfiguration umschreibt, normalisieren gebündelte Google-Familien-Helfer weiterhin
  unterstützte Google-Anbietereinträge.
- `applyNativeStreamingUsageCompat`: Anbieter wendet endpoint-gesteuerte Kompatibilitätsumschreibungen für native Streaming-Nutzung auf Konfigurationsanbieter an
- `resolveConfigApiKey`: Anbieter löst umgebungsmarkierte Authentifizierung für Konfigurationsanbieter auf,
  ohne das vollständige Laufzeit-Authentifizierungsmodul laden zu müssen. `amazon-bedrock` hat hier ebenfalls einen
  eingebauten AWS-Resolver für Umgebungsmarker, obwohl die Bedrock-Laufzeit-Authentifizierung
  die AWS-SDK-Standardkette verwendet.
- `resolveSyntheticAuth`: Anbieter kann lokale/selbst gehostete oder andere
  konfigurationsgestützte Authentifizierungsverfügbarkeit verfügbar machen, ohne Klartext-Geheimnisse
  zu persistieren
- `shouldDeferSyntheticProfileAuth`: Anbieter kann gespeicherte synthetische Profil-
  Platzhalter als niedrigere Priorität als umgebungs-/konfigurationsgestützte Authentifizierung markieren
- `resolveDynamicModel`: Anbieter akzeptiert Modell-IDs, die noch nicht im lokalen
  statischen Katalog vorhanden sind
- `prepareDynamicModel`: Anbieter benötigt eine Metadatenaktualisierung, bevor die dynamische
  Auflösung erneut versucht wird
- `normalizeResolvedModel`: Anbieter benötigt Umschreibungen für Transport oder Basis-URL
- `contributeResolvedModelCompat`: Anbieter steuert Kompatibilitäts-Flags für seine
  Herstellermodelle bei, selbst wenn sie über einen anderen kompatiblen Transport ankommen
- `capabilities`: Anbieter veröffentlicht Eigenheiten bei Transkripten/Tooling/Anbieterfamilie
- `normalizeToolSchemas`: Anbieter bereinigt Tool-Schemas, bevor der eingebettete
  Runner sie sieht
- `inspectToolSchemas`: Anbieter stellt transportspezifische Schemawarnungen
  nach der Normalisierung bereit
- `resolveReasoningOutputMode`: Anbieter wählt native oder markierte
  Contracts für Reasoning-Ausgaben
- `prepareExtraParams`: Anbieter setzt Standardwerte für anfragespezifische Parameter pro Modell oder normalisiert sie
- `createStreamFn`: Anbieter ersetzt den normalen Stream-Pfad durch einen vollständig
  benutzerdefinierten Transport
- `wrapStreamFn`: Anbieter wendet Kompatibilitäts-Wrapper für Anforderungsheader/-body/-modell an
- `resolveTransportTurnState`: Anbieter liefert native Transport-
  Header oder Metadaten pro Turn
- `resolveWebSocketSessionPolicy`: Anbieter liefert native WebSocket-Sitzungs-
  Header oder Cooldown-Richtlinien für Sitzungen
- `createEmbeddingProvider`: Anbieter besitzt das Verhalten für Speicher-Embeddings, wenn es
  beim Anbieter-Plugin statt im Kern-Switchboard für Embeddings liegen soll
- `formatApiKey`: Anbieter formatiert gespeicherte Authentifizierungsprofile in den Laufzeit-
  String `apiKey`, der vom Transport erwartet wird
- `refreshOAuth`: Anbieter besitzt die OAuth-Aktualisierung, wenn die gemeinsamen `pi-ai`-
  Refresher nicht ausreichen
- `buildAuthDoctorHint`: Anbieter ergänzt Reparaturanweisungen, wenn die OAuth-Aktualisierung
  fehlschlägt
- `matchesContextOverflowError`: Anbieter erkennt anbieterspezifische
  Fehler bei Überschreitungen des Kontextfensters, die generische Heuristiken übersehen würden
- `classifyFailoverReason`: Anbieter ordnet anbieterspezifische rohe Transport-/API-
  Fehler Failover-Gründen wie Ratenbegrenzung oder Überlastung zu
- `isCacheTtlEligible`: Anbieter entscheidet, welche Upstream-Modell-IDs Prompt-Cache-TTL unterstützen
- `buildMissingAuthMessage`: Anbieter ersetzt den generischen Fehler des Authentifizierungsspeichers
  durch einen anbieterspezifischen Wiederherstellungshinweis
- `suppressBuiltInModel`: Anbieter blendet veraltete Upstream-Zeilen aus und kann einen
  herstellereigenen Fehler bei direkten Auflösungsfehlern zurückgeben
- `augmentModelCatalog`: Anbieter hängt synthetische/finale Katalogzeilen nach
  Discovery und Konfigurationszusammenführung an
- `isBinaryThinking`: Anbieter besitzt die binäre Ein/Aus-Denken-UX
- `supportsXHighThinking`: Anbieter aktiviert `xhigh` für ausgewählte Modelle
- `resolveDefaultThinkingLevel`: Anbieter besitzt die Standardrichtlinie von `/think` für eine
  Modellfamilie
- `applyConfigDefaults`: Anbieter wendet anbieterspezifische globale Standardwerte
  während der Materialisierung der Konfiguration basierend auf Authentifizierungsmodus, Umgebung oder Modellfamilie an
- `isModernModelRef`: Anbieter besitzt die Zuordnung bevorzugter Modelle für Live-/Smoke-Tests
- `prepareRuntimeAuth`: Anbieter wandelt eine konfigurierte Berechtigung in ein kurzlebiges
  Laufzeit-Token um
- `resolveUsageAuth`: Anbieter löst Anmeldedaten für Nutzung/Kontingente für `/usage`
  und zugehörige Status-/Berichtsoberflächen auf
- `fetchUsageSnapshot`: Anbieter besitzt das Abrufen/Parsen des Nutzungsendpunkts, während
  der Kern weiterhin die Zusammenfassungs-Hülle und Formatierung übernimmt
- `onModelSelected`: Anbieter führt Seiteneffekte nach der Modellauswahl aus, z. B.
  Telemetrie oder anbietereigene Sitzungsbuchhaltung

Aktuelle gebündelte Beispiele:

- `anthropic`: Claude-4.6-Vorwärtskompatibilitäts-Fallback, Hinweise zur Authentifizierungsreparatur, Abruf des
  Nutzungsendpunkts, Cache-TTL-/Anbieterfamilien-Metadaten und auth-aware globale
  Konfigurationsstandardwerte
- `amazon-bedrock`: anbieterbezogene Erkennung von Kontextüberläufen und Failover-
  Klassifizierung für Bedrock-spezifische Fehler bei Drosselung/Nicht-Bereitschaft sowie
  die gemeinsame Replay-Familie `anthropic-by-model` für Claude-spezifische Replay-Richtlinien-
  Schutzmaßnahmen auf Anthropic-Datenverkehr
- `anthropic-vertex`: Claude-spezifische Replay-Richtlinien-Schutzmaßnahmen auf Anthropic-Message-
  Datenverkehr
- `openrouter`: Durchreichen von Modell-IDs, Anforderungs-Wrapper, Hinweise zu Anbieterfunktionen,
  Bereinigung von Gemini-Thinking-Signaturen bei proxybasiertem Gemini-Datenverkehr,
  Proxy-Reasoning-Injektion über die Stream-Familie `openrouter-thinking`, Weiterleitung
  von Routing-Metadaten und Cache-TTL-Richtlinie
- `github-copilot`: Onboarding/Geräte-Login, Vorwärtskompatibilitäts-Fallback für Modelle,
  Hinweise zu Claude-Thinking-Transkripten, Austausch von Laufzeit-Token und Abruf des Nutzungsendpunkts
- `openai`: GPT-5.4-Vorwärtskompatibilitäts-Fallback, direkte OpenAI-Transport-
  Normalisierung, Codex-spezifische Hinweise bei fehlender Authentifizierung, Spark-Unterdrückung, synthetische
  OpenAI-/Codex-Katalogzeilen, Thinking-/Live-Modell-Richtlinie, Normalisierung von Aliasen für Nutzungstoken
  (`input` / `output` und `prompt` / `completion`-Familien), die
  gemeinsame Stream-Familie `openai-responses-defaults` für native OpenAI-/Codex-
  Wrapper, Anbieterfamilien-Metadaten, gebündelte Registrierung von Bildgenerierungsanbietern
  für `gpt-image-1` und gebündelte Registrierung von Videogenerierungsanbietern
  für `sora-2`
- `google` und `google-gemini-cli`: Gemini-3.1-Vorwärtskompatibilitäts-Fallback,
  native Gemini-Replay-Validierung, Bereinigung von Bootstrap-Replays, markierter
  Modus für Reasoning-Ausgaben, Modern-Model-Matching, gebündelte Registrierung von Bildgenerierungs-
  Anbietern für Gemini-Image-Preview-Modelle und gebündelte
  Registrierung von Videogenerierungsanbietern für Veo-Modelle; Gemini-CLI-OAuth übernimmt außerdem
  die Tokenformatierung für Authentifizierungsprofile, das Parsen von Nutzungstoken und das Abrufen des Kontingentendpunkts
  für Nutzungsoberflächen
- `moonshot`: gemeinsamer Transport, plugin-eigene Normalisierung von Thinking-Payloads
- `kilocode`: gemeinsamer Transport, plugin-eigene Anforderungsheader, Normalisierung von Reasoning-Payloads,
  Bereinigung von Proxy-Gemini-Thinking-Signaturen und Cache-TTL-
  Richtlinie
- `zai`: GLM-5-Vorwärtskompatibilitäts-Fallback, Standardwerte für `tool_stream`, Cache-TTL-
  Richtlinie, binäre Thinking-/Live-Modell-Richtlinie und Nutzungsauthentifizierung + Kontingentabruf;
  unbekannte `glm-5*`-IDs werden aus der gebündelten Vorlage `glm-4.7` synthetisiert
- `xai`: native Responses-Transportnormalisierung, Umschreibungen von `/fast`-Aliasen für
  schnelle Grok-Varianten, standardmäßiges `tool_stream`, xAI-spezifische Bereinigung von Tool-Schemas /
  Reasoning-Payloads und gebündelte Registrierung von Videogenerierungsanbietern
  für `grok-imagine-video`
- `mistral`: plugin-eigene Fähigkeitsmetadaten
- `opencode` und `opencode-go`: plugin-eigene Fähigkeitsmetadaten plus
  Bereinigung von Proxy-Gemini-Thinking-Signaturen
- `alibaba`: plugin-eigener Videogenerierungskatalog für direkte Wan-Modellreferenzen
  wie `alibaba/wan2.6-t2v`
- `byteplus`: plugin-eigene Kataloge plus gebündelte Registrierung von Videogenerierungsanbietern
  für Seedance-Text-zu-Video-/Bild-zu-Video-Modelle
- `fal`: gebündelte Registrierung von Videogenerierungsanbietern für gehostete Drittanbieter-
  Registrierung von Bildgenerierungsanbietern für FLUX-Bildmodelle plus gebündelte
  Registrierung von Videogenerierungsanbietern für gehostete Drittanbieter-Videomodelle
- `cloudflare-ai-gateway`, `huggingface`, `kimi`, `nvidia`, `qianfan`,
  `stepfun`, `synthetic`, `venice`, `vercel-ai-gateway` und `volcengine`:
  nur plugin-eigene Kataloge
- `qwen`: plugin-eigene Kataloge für Textmodelle plus gemeinsame
  Registrierungen von Anbietern für Media Understanding und Videogenerierung für seine
  multimodalen Oberflächen; die Qwen-Videogenerierung verwendet die Standard-DashScope-Video-
  Endpunkte mit gebündelten Wan-Modellen wie `wan2.6-t2v` und `wan2.7-r2v`
- `runway`: plugin-eigene Registrierung von Videogenerierungsanbietern für native
  taskbasierte Runway-Modelle wie `gen4.5`
- `minimax`: plugin-eigene Kataloge, gebündelte Registrierung von Videogenerierungsanbietern
  für Hailuo-Videomodelle, gebündelte Registrierung von Bildgenerierungsanbietern
  für `image-01`, hybride Auswahl der Anthropic-/OpenAI-Replay-Richtlinie sowie Logik für Nutzungsauthentifizierung/Snapshots
- `together`: plugin-eigene Kataloge plus gebündelte Registrierung von Videogenerierungsanbietern
  für Wan-Videomodelle
- `xiaomi`: plugin-eigene Kataloge plus Logik für Nutzungsauthentifizierung/Snapshots

Das gebündelte Plugin `openai` besitzt jetzt beide Anbieter-IDs: `openai` und
`openai-codex`.

Das deckt Anbieter ab, die noch in die normalen Transporte von OpenClaw passen. Ein Anbieter,
der einen vollständig benutzerdefinierten Request-Executor benötigt, ist eine separate, tiefere Erweiterungsoberfläche.

## Rotation von API-Schlüsseln

- Unterstützt generische Anbieterrrotation für ausgewählte Anbieter.
- Konfigurieren Sie mehrere Schlüssel über:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY` (einzelne Live-Überschreibung, höchste Priorität)
  - `<PROVIDER>_API_KEYS` (komma- oder semikolongetrennte Liste)
  - `<PROVIDER>_API_KEY` (primärer Schlüssel)
  - `<PROVIDER>_API_KEY_*` (nummerierte Liste, z. B. `<PROVIDER>_API_KEY_1`)
- Für Google-Anbieter ist `GOOGLE_API_KEY` zusätzlich als Fallback enthalten.
- Die Reihenfolge der Schlüsselauswahl bewahrt die Priorität und entfernt doppelte Werte.
- Anfragen werden nur bei Antworten mit Ratenbegrenzung mit dem nächsten Schlüssel erneut versucht (zum
  Beispiel `429`, `rate_limit`, `quota`, `resource exhausted`, `Too many
concurrent requests`, `ThrottlingException`, `concurrency limit reached`,
  `workers_ai ... quota limit exceeded` oder periodische Meldungen zur Nutzungsbegrenzung).
- Fehler ohne Ratenbegrenzung schlagen sofort fehl; es wird keine Schlüsselrotation versucht.
- Wenn alle Kandidatenschlüssel fehlschlagen, wird der letzte Fehler des letzten Versuchs zurückgegeben.

## Integrierte Anbieter (pi-ai-Katalog)

OpenClaw wird mit dem pi-ai-Katalog ausgeliefert. Diese Anbieter erfordern **keine**
Konfiguration in `models.providers`; setzen Sie einfach die Authentifizierung und wählen Sie ein Modell aus.

### OpenAI

- Anbieter: `openai`
- Authentifizierung: `OPENAI_API_KEY`
- Optionale Rotation: `OPENAI_API_KEYS`, `OPENAI_API_KEY_1`, `OPENAI_API_KEY_2` sowie `OPENCLAW_LIVE_OPENAI_KEY` (einzelne Überschreibung)
- Beispielmodelle: `openai/gpt-5.4`, `openai/gpt-5.4-pro`
- CLI: `openclaw onboard --auth-choice openai-api-key`
- Standardtransport ist `auto` (WebSocket zuerst, SSE als Fallback)
- Überschreibung pro Modell über `agents.defaults.models["openai/<model>"].params.transport` (`"sse"`, `"websocket"` oder `"auto"`)
- Das Aufwärmen von OpenAI-Responses-WebSocket ist standardmäßig über `params.openaiWsWarmup` aktiviert (`true`/`false`)
- Prioritätsverarbeitung von OpenAI kann über `agents.defaults.models["openai/<model>"].params.serviceTier` aktiviert werden
- `/fast` und `params.fastMode` ordnen direkte `openai/*`-Responses-Anfragen `service_tier=priority` auf `api.openai.com` zu
- Verwenden Sie `params.serviceTier`, wenn Sie eine explizite Stufe statt des gemeinsamen Schalters `/fast` möchten
- Versteckte OpenClaw-Attributionsheader (`originator`, `version`,
  `User-Agent`) gelten nur für nativen OpenAI-Datenverkehr an `api.openai.com`, nicht
  für generische OpenAI-kompatible Proxys
- Native OpenAI-Routen behalten außerdem Responses-`store`, Prompt-Cache-Hinweise und
  OpenAI-Reasoning-kompatible Payload-Aufbereitung bei; Proxy-Routen nicht
- `openai/gpt-5.3-codex-spark` wird in OpenClaw absichtlich unterdrückt, weil die Live-OpenAI-API es ablehnt; Spark wird nur als Codex behandelt

```json5
{
  agents: { defaults: { model: { primary: "openai/gpt-5.4" } } },
}
```

### Anthropic

- Anbieter: `anthropic`
- Authentifizierung: `ANTHROPIC_API_KEY`
- Optionale Rotation: `ANTHROPIC_API_KEYS`, `ANTHROPIC_API_KEY_1`, `ANTHROPIC_API_KEY_2` sowie `OPENCLAW_LIVE_ANTHROPIC_KEY` (einzelne Überschreibung)
- Beispielmodell: `anthropic/claude-opus-4-6`
- CLI: `openclaw onboard --auth-choice apiKey`
- Direkte öffentliche Anthropic-Anfragen unterstützen den gemeinsamen Schalter `/fast` und `params.fastMode`, einschließlich mit API-Schlüssel und OAuth authentifiziertem Datenverkehr an `api.anthropic.com`; OpenClaw ordnet dies Anthropic-`service_tier` zu (`auto` vs `standard_only`)
- Anthropic-Hinweis: Anthropic-Mitarbeiter haben uns mitgeteilt, dass die Nutzung im Stil von OpenClaw Claude CLI wieder erlaubt ist, daher behandelt OpenClaw die Wiederverwendung von Claude CLI und die Nutzung von `claude -p` als für diese Integration zulässig, sofern Anthropic keine neue Richtlinie veröffentlicht.
- Das Anthropic-Setup-Token bleibt als unterstützter OpenClaw-Tokenpfad verfügbar, aber OpenClaw bevorzugt jetzt die Wiederverwendung von Claude CLI und `claude -p`, wenn verfügbar.

```json5
{
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

### OpenAI Code (Codex)

- Anbieter: `openai-codex`
- Authentifizierung: OAuth (ChatGPT)
- Beispielmodell: `openai-codex/gpt-5.4`
- CLI: `openclaw onboard --auth-choice openai-codex` oder `openclaw models auth login --provider openai-codex`
- Standardtransport ist `auto` (WebSocket zuerst, SSE als Fallback)
- Überschreibung pro Modell über `agents.defaults.models["openai-codex/<model>"].params.transport` (`"sse"`, `"websocket"` oder `"auto"`)
- `params.serviceTier` wird auch bei nativen Codex-Responses-Anfragen weitergegeben (`chatgpt.com/backend-api`)
- Versteckte OpenClaw-Attributionsheader (`originator`, `version`,
  `User-Agent`) werden nur bei nativem Codex-Datenverkehr an
  `chatgpt.com/backend-api` angehängt, nicht bei generischen OpenAI-kompatiblen Proxys
- Verwendet denselben `/fast`-Schalter und dieselbe `params.fastMode`-Konfiguration wie direktes `openai/*`; OpenClaw ordnet dies `service_tier=priority` zu
- `openai-codex/gpt-5.3-codex-spark` bleibt verfügbar, wenn der Codex-OAuth-Katalog es bereitstellt; abhängig von Berechtigungen
- `openai-codex/gpt-5.4` behält nativ `contextWindow = 1050000` und standardmäßig zur Laufzeit `contextTokens = 272000`; überschreiben Sie die Laufzeitgrenze mit `models.providers.openai-codex.models[].contextTokens`
- Richtlinienhinweis: OpenAI-Codex-OAuth wird ausdrücklich für externe Tools/Workflows wie OpenClaw unterstützt.

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

### Andere gehostete Optionen im Abonnementstil

- [Qwen Cloud](/de/providers/qwen): Qwen-Cloud-Anbieteroberfläche plus Endpoint-Zuordnung für Alibaba DashScope und Coding Plan
- [MiniMax](/de/providers/minimax): MiniMax-Coding-Plan-Zugriff per OAuth oder API-Schlüssel
- [GLM Models](/de/providers/glm): Z.AI Coding Plan oder allgemeine API-Endpunkte

### OpenCode

- Authentifizierung: `OPENCODE_API_KEY` (oder `OPENCODE_ZEN_API_KEY`)
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
- Authentifizierung: `GEMINI_API_KEY`
- Optionale Rotation: `GEMINI_API_KEYS`, `GEMINI_API_KEY_1`, `GEMINI_API_KEY_2`, `GOOGLE_API_KEY` als Fallback und `OPENCLAW_LIVE_GEMINI_KEY` (einzelne Überschreibung)
- Beispielmodelle: `google/gemini-3.1-pro-preview`, `google/gemini-3-flash-preview`
- Kompatibilität: Legacy-OpenClaw-Konfiguration mit `google/gemini-3.1-flash-preview` wird zu `google/gemini-3-flash-preview` normalisiert
- CLI: `openclaw onboard --auth-choice gemini-api-key`
- Direkte Gemini-Ausführungen akzeptieren außerdem `agents.defaults.models["google/<model>"].params.cachedContent`
  (oder das Legacy-`cached_content`), um ein anbieter-
  natives Handle `cachedContents/...` weiterzuleiten; Gemini-Cache-Treffer erscheinen als OpenClaw-`cacheRead`

### Google Vertex und Gemini CLI

- Anbieter: `google-vertex`, `google-gemini-cli`
- Authentifizierung: Vertex verwendet gcloud ADC; Gemini CLI verwendet seinen OAuth-Ablauf
- Achtung: Gemini-CLI-OAuth in OpenClaw ist eine inoffizielle Integration. Einige Nutzer haben von Einschränkungen ihres Google-Kontos nach der Verwendung von Drittanbieter-Clients berichtet. Prüfen Sie die Google-Bedingungen und verwenden Sie bei Bedarf ein nicht kritisches Konto.
- Gemini-CLI-OAuth wird als Teil des gebündelten Plugins `google` ausgeliefert.
  - Installieren Sie zuerst Gemini CLI:
    - `brew install gemini-cli`
    - oder `npm install -g @google/gemini-cli`
  - Aktivieren: `openclaw plugins enable google`
  - Login: `openclaw models auth login --provider google-gemini-cli --set-default`
  - Standardmodell: `google-gemini-cli/gemini-3-flash-preview`
  - Hinweis: Sie fügen **keine** Client-ID oder kein Secret in `openclaw.json` ein. Der CLI-Login-Ablauf speichert
    Tokens in Authentifizierungsprofilen auf dem Gateway-Host.
  - Wenn Anfragen nach dem Login fehlschlagen, setzen Sie `GOOGLE_CLOUD_PROJECT` oder `GOOGLE_CLOUD_PROJECT_ID` auf dem Gateway-Host.
  - JSON-Antworten von Gemini CLI werden aus `response` geparst; die Nutzung fällt auf
    `stats` zurück, wobei `stats.cached` in OpenClaw-`cacheRead` normalisiert wird.

### Z.AI (GLM)

- Anbieter: `zai`
- Authentifizierung: `ZAI_API_KEY`
- Beispielmodell: `zai/glm-5.1`
- CLI: `openclaw onboard --auth-choice zai-api-key`
  - Aliase: `z.ai/*` und `z-ai/*` werden zu `zai/*` normalisiert
  - `zai-api-key` erkennt den passenden Z.AI-Endpunkt automatisch; `zai-coding-global`, `zai-coding-cn`, `zai-global` und `zai-cn` erzwingen eine bestimmte Oberfläche

### Vercel AI Gateway

- Anbieter: `vercel-ai-gateway`
- Authentifizierung: `AI_GATEWAY_API_KEY`
- Beispielmodell: `vercel-ai-gateway/anthropic/claude-opus-4.6`
- CLI: `openclaw onboard --auth-choice ai-gateway-api-key`

### Kilo Gateway

- Anbieter: `kilocode`
- Authentifizierung: `KILOCODE_API_KEY`
- Beispielmodell: `kilocode/kilo/auto`
- CLI: `openclaw onboard --auth-choice kilocode-api-key`
- Basis-URL: `https://api.kilo.ai/api/gateway/`
- Der statische Fallback-Katalog enthält `kilocode/kilo/auto`; die Live-
  Discovery unter `https://api.kilo.ai/api/gateway/models` kann den Laufzeit-
  Katalog weiter erweitern.
- Das genaue Upstream-Routing hinter `kilocode/kilo/auto` wird von Kilo Gateway verwaltet
  und ist nicht fest in OpenClaw kodiert.

Einzelheiten zur Einrichtung finden Sie unter [/providers/kilocode](/de/providers/kilocode).

### Andere gebündelte Anbieter-Plugins

- OpenRouter: `openrouter` (`OPENROUTER_API_KEY`)
- Beispielmodell: `openrouter/auto`
- OpenClaw wendet die dokumentierten App-Attributionsheader von OpenRouter nur an, wenn
  die Anfrage tatsächlich `openrouter.ai` als Ziel hat
- OpenRouter-spezifische Anthropic-`cache_control`-Marker werden ebenfalls nur auf
  verifizierten OpenRouter-Routen angewendet, nicht auf beliebigen Proxy-URLs
- OpenRouter bleibt auf dem proxyartigen OpenAI-kompatiblen Pfad, daher wird native
  nur-OpenAI-Request-Aufbereitung (`serviceTier`, Responses-`store`,
  Prompt-Cache-Hinweise, OpenAI-reasoning-kompatible Payloads) nicht weitergeleitet
- Gemini-basierte OpenRouter-Referenzen behalten nur die Bereinigung der Proxy-Gemini-
  Thinking-Signatur bei; native Gemini-Replay-Validierung und Bootstrap-Umschreibungen bleiben deaktiviert
- Kilo Gateway: `kilocode` (`KILOCODE_API_KEY`)
- Beispielmodell: `kilocode/kilo/auto`
- Gemini-basierte Kilo-Referenzen behalten denselben Bereinigungspfad für Proxy-Gemini-Thinking-
  Signaturen; `kilocode/kilo/auto` und andere Hinweise ohne Unterstützung für Proxy-Reasoning
  überspringen die Injektion von Proxy-Reasoning
- MiniMax: `minimax` (API-Schlüssel) und `minimax-portal` (OAuth)
- Authentifizierung: `MINIMAX_API_KEY` für `minimax`; `MINIMAX_OAUTH_TOKEN` oder `MINIMAX_API_KEY` für `minimax-portal`
- Beispielmodell: `minimax/MiniMax-M2.7` oder `minimax-portal/MiniMax-M2.7`
- MiniMax-Onboarding/Einrichtung mit API-Schlüssel schreibt explizite M2.7-Modelldefinitionen mit
  `input: ["text", "image"]`; der gebündelte Anbieterkatalog hält die Chat-Referenzen
  als nur Text, bis diese Anbieterkonfiguration materialisiert wird
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

## Anbieter über `models.providers` (benutzerdefiniert/Basis-URL)

Verwenden Sie `models.providers` (oder `models.json`), um **benutzerdefinierte** Anbieter oder
OpenAI-/Anthropic-kompatible Proxys hinzuzufügen.

Viele der unten aufgeführten gebündelten Anbieter-Plugins veröffentlichen bereits einen Standardkatalog.
Verwenden Sie explizite Einträge in `models.providers.<id>` nur dann, wenn Sie die
Standard-Basis-URL, Header oder Modellliste überschreiben möchten.

### Moonshot AI (Kimi)

Moonshot wird als gebündeltes Anbieter-Plugin ausgeliefert. Verwenden Sie standardmäßig den integrierten Anbieter
und fügen Sie nur dann einen expliziten Eintrag `models.providers.moonshot` hinzu, wenn Sie
die Basis-URL oder Modellmetadaten überschreiben müssen:

- Anbieter: `moonshot`
- Authentifizierung: `MOONSHOT_API_KEY`
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
- Authentifizierung: `KIMI_API_KEY`
- Beispielmodell: `kimi/kimi-code`

```json5
{
  env: { KIMI_API_KEY: "sk-..." },
  agents: {
    defaults: { model: { primary: "kimi/kimi-code" } },
  },
}
```

Das Legacy-`kimi/k2p5` bleibt als kompatible Modell-ID weiterhin akzeptiert.

### Volcano Engine (Doubao)

Volcano Engine (火山引擎) bietet in China Zugriff auf Doubao und andere Modelle.

- Anbieter: `volcengine` (Coding: `volcengine-plan`)
- Authentifizierung: `VOLCANO_ENGINE_API_KEY`
- Beispielmodell: `volcengine-plan/ark-code-latest`
- CLI: `openclaw onboard --auth-choice volcengine-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "volcengine-plan/ark-code-latest" } },
  },
}
```

Beim Onboarding wird standardmäßig die Coding-Oberfläche verwendet, aber der allgemeine Katalog `volcengine/*`
wird gleichzeitig registriert.

In Onboarding-/Modellauswahlen für die Konfiguration bevorzugt die Volcengine-Authentifizierungsoption sowohl
Zeilen `volcengine/*` als auch `volcengine-plan/*`. Wenn diese Modelle noch nicht geladen sind,
fällt OpenClaw auf den ungefilterten Katalog zurück, anstatt eine leere
anbieterspezifische Auswahl anzuzeigen.

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
- Authentifizierung: `BYTEPLUS_API_KEY`
- Beispielmodell: `byteplus-plan/ark-code-latest`
- CLI: `openclaw onboard --auth-choice byteplus-api-key`

```json5
{
  agents: {
    defaults: { model: { primary: "byteplus-plan/ark-code-latest" } },
  },
}
```

Beim Onboarding wird standardmäßig die Coding-Oberfläche verwendet, aber der allgemeine Katalog `byteplus/*`
wird gleichzeitig registriert.

In Onboarding-/Modellauswahlen für die Konfiguration bevorzugt die BytePlus-Authentifizierungsoption sowohl
Zeilen `byteplus/*` als auch `byteplus-plan/*`. Wenn diese Modelle noch nicht geladen sind,
fällt OpenClaw auf den ungefilterten Katalog zurück, anstatt eine leere
anbieterspezifische Auswahl anzuzeigen.

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
- Authentifizierung: `SYNTHETIC_API_KEY`
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

MiniMax wird über `models.providers` konfiguriert, weil es benutzerdefinierte Endpunkte verwendet:

- MiniMax OAuth (Global): `--auth-choice minimax-global-oauth`
- MiniMax OAuth (CN): `--auth-choice minimax-cn-oauth`
- MiniMax API-Schlüssel (Global): `--auth-choice minimax-global-api`
- MiniMax API-Schlüssel (CN): `--auth-choice minimax-cn-api`
- Authentifizierung: `MINIMAX_API_KEY` für `minimax`; `MINIMAX_OAUTH_TOKEN` oder
  `MINIMAX_API_KEY` für `minimax-portal`

Einzelheiten zur Einrichtung, Modelloptionen und Konfigurationsbeispiele finden Sie unter [/providers/minimax](/de/providers/minimax).

Auf dem Anthropic-kompatiblen Streaming-Pfad von MiniMax deaktiviert OpenClaw Thinking standardmäßig,
es sei denn, Sie setzen es explizit, und `/fast on` schreibt
`MiniMax-M2.7` in `MiniMax-M2.7-highspeed` um.

Plugin-eigene Aufteilung der Fähigkeiten:

- Standardwerte für Text/Chat bleiben auf `minimax/MiniMax-M2.7`
- Bildgenerierung ist `minimax/image-01` oder `minimax-portal/image-01`
- Bildverständnis ist plugin-eigenes `MiniMax-VL-01` auf beiden MiniMax-Authentifizierungspfaden
- Websuche bleibt auf Anbieter-ID `minimax`

### Ollama

Ollama wird als gebündeltes Anbieter-Plugin ausgeliefert und verwendet die native API von Ollama:

- Anbieter: `ollama`
- Authentifizierung: Keine erforderlich (lokaler Server)
- Beispielmodell: `ollama/llama3.3`
- Installation: [https://ollama.com/download](https://ollama.com/download)

```bash
# Installieren Sie Ollama und ziehen Sie dann ein Modell:
ollama pull llama3.3
```

```json5
{
  agents: {
    defaults: { model: { primary: "ollama/llama3.3" } },
  },
}
```

Ollama wird lokal unter `http://127.0.0.1:11434` erkannt, wenn Sie sich mit
`OLLAMA_API_KEY` dafür anmelden, und das gebündelte Anbieter-Plugin fügt Ollama direkt zu
`openclaw onboard` und der Modellauswahl hinzu. Siehe [/providers/ollama](/de/providers/ollama)
für Onboarding, Cloud-/lokalen Modus und benutzerdefinierte Konfiguration.

### vLLM

vLLM wird als gebündeltes Anbieter-Plugin für lokale/selbst gehostete OpenAI-kompatible
Server ausgeliefert:

- Anbieter: `vllm`
- Authentifizierung: Optional (abhängig von Ihrem Server)
- Standard-Basis-URL: `http://127.0.0.1:8000/v1`

Um sich lokal für die automatische Erkennung anzumelden (jeder Wert funktioniert, wenn Ihr Server keine Authentifizierung erzwingt):

```bash
export VLLM_API_KEY="vllm-local"
```

Setzen Sie dann ein Modell (ersetzen Sie es durch eine der IDs, die von `/v1/models` zurückgegeben werden):

```json5
{
  agents: {
    defaults: { model: { primary: "vllm/your-model-id" } },
  },
}
```

Einzelheiten finden Sie unter [/providers/vllm](/de/providers/vllm).

### SGLang

SGLang wird als gebündeltes Anbieter-Plugin für schnelle selbst gehostete
OpenAI-kompatible Server ausgeliefert:

- Anbieter: `sglang`
- Authentifizierung: Optional (abhängig von Ihrem Server)
- Standard-Basis-URL: `http://127.0.0.1:30000/v1`

Um sich lokal für die automatische Erkennung anzumelden (jeder Wert funktioniert, wenn Ihr Server keine
Authentifizierung erzwingt):

```bash
export SGLANG_API_KEY="sglang-local"
```

Setzen Sie dann ein Modell (ersetzen Sie es durch eine der IDs, die von `/v1/models` zurückgegeben werden):

```json5
{
  agents: {
    defaults: { model: { primary: "sglang/your-model-id" } },
  },
}
```

Einzelheiten finden Sie unter [/providers/sglang](/de/providers/sglang).

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
- Empfohlen: Setzen Sie explizite Werte, die zu den Grenzen Ihres Proxys/Modells passen.
- Für `api: "openai-completions"` auf nicht nativen Endpunkten (jede nicht leere `baseUrl`, deren Host nicht `api.openai.com` ist), erzwingt OpenClaw `compat.supportsDeveloperRole: false`, um Provider-400-Fehler für nicht unterstützte `developer`-Rollen zu vermeiden.
- Proxyartige OpenAI-kompatible Routen überspringen außerdem native nur-OpenAI-Request-
  Aufbereitung: kein `service_tier`, kein Responses-`store`, keine Prompt-Cache-Hinweise, keine
  OpenAI-reasoning-kompatible Payload-Aufbereitung und keine versteckten OpenClaw-Attributions-
  Header.
- Wenn `baseUrl` leer ist oder weggelassen wird, behält OpenClaw das Standard-OpenAI-Verhalten bei (das zu `api.openai.com` aufgelöst wird).
- Aus Sicherheitsgründen wird ein explizites `compat.supportsDeveloperRole: true` auf nicht nativen `openai-completions`-Endpunkten weiterhin überschrieben.

## CLI-Beispiele

```bash
openclaw onboard --auth-choice opencode-zen
openclaw models set opencode/claude-opus-4-6
openclaw models list
```

Siehe auch: [/gateway/configuration](/de/gateway/configuration) für vollständige Konfigurationsbeispiele.

## Verwandt

- [Models](/de/concepts/models) — Modellkonfiguration und Aliase
- [Model Failover](/de/concepts/model-failover) — Fallback-Ketten und Wiederholungsverhalten
- [Configuration Reference](/de/gateway/configuration-reference#agent-defaults) — Konfigurationsschlüssel für Modelle
- [Providers](/de/providers) — Einrichtungsanleitungen pro Anbieter
