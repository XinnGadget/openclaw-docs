---
read_when:
    - Erstellen oder Debuggen nativer OpenClaw-Plugins
    - Das Fähigkeitsmodell oder die Eigentumsgrenzen von Plugins verstehen
    - An der Ladepipeline oder Registry von Plugins arbeiten
    - Implementieren von Provider-Laufzeit-Hooks oder Kanal-Plugins
sidebarTitle: Internals
summary: 'Plugin-Interna: Fähigkeitsmodell, Eigentümerschaft, Verträge, Ladepipeline und Laufzeit-Hilfsfunktionen'
title: Plugin-Interna
x-i18n:
    generated_at: "2026-04-11T15:15:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7cac67984d0d729c0905bcf5c18372fb0d9b02bbd3a531580b7e2ef483ef40a6
    source_path: plugins/architecture.md
    workflow: 15
---

# Plugin-Interna

<Info>
  Dies ist die **umfassende Architekturreferenz**. Praktische Anleitungen finden Sie unter:
  - [Plugins installieren und verwenden](/de/tools/plugin) — Benutzerhandbuch
  - [Erste Schritte](/de/plugins/building-plugins) — erstes Plugin-Tutorial
  - [Kanal-Plugins](/de/plugins/sdk-channel-plugins) — einen Messaging-Kanal erstellen
  - [Provider-Plugins](/de/plugins/sdk-provider-plugins) — einen Modell-Provider erstellen
  - [SDK-Überblick](/de/plugins/sdk-overview) — Importzuordnung und Registrierungs-API
</Info>

Diese Seite behandelt die interne Architektur des OpenClaw-Plugin-Systems.

## Öffentliches Fähigkeitsmodell

Fähigkeiten sind das öffentliche Modell für **native Plugins** in OpenClaw. Jedes
native OpenClaw-Plugin registriert sich für einen oder mehrere Fähigkeitstypen:

| Fähigkeit              | Registrierungsmethode                             | Beispiel-Plugins                     |
| ---------------------- | ------------------------------------------------- | ------------------------------------ |
| Textinferenz           | `api.registerProvider(...)`                       | `openai`, `anthropic`                |
| CLI-Inferenz-Backend   | `api.registerCliBackend(...)`                     | `openai`, `anthropic`                |
| Sprache                | `api.registerSpeechProvider(...)`                 | `elevenlabs`, `microsoft`            |
| Echtzeit-Transkription | `api.registerRealtimeTranscriptionProvider(...)`  | `openai`                             |
| Echtzeit-Stimme        | `api.registerRealtimeVoiceProvider(...)`          | `openai`                             |
| Medienverständnis      | `api.registerMediaUnderstandingProvider(...)`     | `openai`, `google`                   |
| Bildgenerierung        | `api.registerImageGenerationProvider(...)`        | `openai`, `google`, `fal`, `minimax` |
| Musikgenerierung       | `api.registerMusicGenerationProvider(...)`        | `google`, `minimax`                  |
| Videogenerierung       | `api.registerVideoGenerationProvider(...)`        | `qwen`                               |
| Web-Abruf              | `api.registerWebFetchProvider(...)`               | `firecrawl`                          |
| Websuche               | `api.registerWebSearchProvider(...)`              | `google`                             |
| Kanal / Messaging      | `api.registerChannel(...)`                        | `msteams`, `matrix`                  |

Ein Plugin, das null Fähigkeiten registriert, aber Hooks, Tools oder
Dienste bereitstellt, ist ein **Legacy-Plugin nur mit Hooks**. Dieses Muster wird
weiterhin vollständig unterstützt.

### Haltung zur externen Kompatibilität

Das Fähigkeitsmodell ist im Kern angekommen und wird heute von gebündelten/nativen Plugins
verwendet, aber die Kompatibilität externer Plugins braucht weiterhin einen strengeren Maßstab als „es ist
exportiert, also ist es eingefroren“.

Aktuelle Richtlinien:

- **bestehende externe Plugins:** hook-basierte Integrationen funktionsfähig halten; behandeln
  Sie dies als Kompatibilitätsgrundlage
- **neue gebündelte/native Plugins:** explizite Fähigkeitsregistrierung gegenüber
  anbieterspezifischen Zugriffen oder neuen Nur-Hook-Designs bevorzugen
- **externe Plugins, die Fähigkeitsregistrierung übernehmen:** erlaubt, aber die
  fähigkeitsspezifischen Hilfsoberflächen als weiterentwickelnd behandeln, sofern die Dokumentation einen
  Vertrag nicht ausdrücklich als stabil kennzeichnet

Praktische Regel:

- APIs zur Fähigkeitsregistrierung sind die beabsichtigte Richtung
- Legacy-Hooks bleiben während des Übergangs der sicherste Weg ohne
  Kompatibilitätsbrüche für externe Plugins
- exportierte Hilfs-Unterpfade sind nicht alle gleich; bevorzugen Sie den schmalen dokumentierten
  Vertrag, nicht zufällig exportierte Hilfsfunktionen

### Plugin-Formen

OpenClaw klassifiziert jedes geladene Plugin anhand seines tatsächlichen
Registrierungsverhaltens in eine Form (nicht nur anhand statischer Metadaten):

- **plain-capability** -- registriert genau einen Fähigkeitstyp (zum Beispiel ein
  reines Provider-Plugin wie `mistral`)
- **hybrid-capability** -- registriert mehrere Fähigkeitstypen (zum Beispiel
  besitzt `openai` Textinferenz, Sprache, Medienverständnis und
  Bildgenerierung)
- **hook-only** -- registriert nur Hooks (typisiert oder benutzerdefiniert), keine
  Fähigkeiten, Tools, Befehle oder Dienste
- **non-capability** -- registriert Tools, Befehle, Dienste oder Routen, aber keine
  Fähigkeiten

Verwenden Sie `openclaw plugins inspect <id>`, um die Form und die Aufschlüsselung der Fähigkeiten
eines Plugins zu sehen. Details finden Sie in der [CLI-Referenz](/cli/plugins#inspect).

### Legacy-Hooks

Der Hook `before_agent_start` bleibt als Kompatibilitätspfad für
Plugins nur mit Hooks unterstützt. Reale Legacy-Plugins sind weiterhin davon abhängig.

Ausrichtung:

- funktionsfähig halten
- als veraltet dokumentieren
- `before_model_resolve` für Arbeiten zur Modell-/Provider-Überschreibung bevorzugen
- `before_prompt_build` für Arbeiten zur Prompt-Mutation bevorzugen
- erst entfernen, wenn die reale Nutzung sinkt und die Fixture-Abdeckung die Sicherheit der Migration belegt

### Kompatibilitätssignale

Wenn Sie `openclaw doctor` oder `openclaw plugins inspect <id>` ausführen, sehen Sie möglicherweise
eines dieser Labels:

| Signal                     | Bedeutung                                                   |
| -------------------------- | ----------------------------------------------------------- |
| **config valid**           | Die Konfiguration wird sauber geparst und Plugins werden aufgelöst |
| **compatibility advisory** | Das Plugin verwendet ein unterstütztes, aber älteres Muster (z. B. `hook-only`) |
| **legacy warning**         | Das Plugin verwendet `before_agent_start`, was veraltet ist |
| **hard error**             | Die Konfiguration ist ungültig oder das Plugin konnte nicht geladen werden |

Weder `hook-only` noch `before_agent_start` führen heute dazu, dass Ihr Plugin nicht mehr funktioniert --
`hook-only` ist ein Hinweis, und `before_agent_start` löst nur eine Warnung aus. Diese
Signale erscheinen auch in `openclaw status --all` und `openclaw plugins doctor`.

## Architekturüberblick

Das Plugin-System von OpenClaw hat vier Ebenen:

1. **Manifest + Erkennung**
   OpenClaw findet mögliche Plugins aus konfigurierten Pfaden, Workspace-Wurzeln,
   globalen Erweiterungswurzeln und gebündelten Erweiterungen. Die Erkennung liest zuerst native
   `openclaw.plugin.json`-Manifeste sowie unterstützte Bundle-Manifeste.
2. **Aktivierung + Validierung**
   Der Kern entscheidet, ob ein erkanntes Plugin aktiviert, deaktiviert, blockiert oder
   für einen exklusiven Slot wie Speicher ausgewählt wird.
3. **Laufzeitladen**
   Native OpenClaw-Plugins werden im Prozess per jiti geladen und registrieren
   Fähigkeiten in einer zentralen Registry. Kompatible Bundles werden in
   Registry-Einträge normalisiert, ohne Laufzeitcode zu importieren.
4. **Nutzung der Oberflächen**
   Der Rest von OpenClaw liest die Registry, um Tools, Kanäle, Provider-
   Einrichtung, Hooks, HTTP-Routen, CLI-Befehle und Dienste bereitzustellen.

Speziell für die Plugin-CLI ist die Erkennung von Root-Befehlen in zwei Phasen aufgeteilt:

- Parse-Zeit-Metadaten kommen aus `registerCli(..., { descriptors: [...] })`
- das eigentliche Plugin-CLI-Modul kann träge bleiben und sich beim ersten Aufruf registrieren

Dadurch bleibt Plugin-eigener CLI-Code innerhalb des Plugins, während OpenClaw
Root-Befehlsnamen weiterhin vor dem Parsen reservieren kann.

Die wichtige Designgrenze:

- Erkennung + Konfigurationsvalidierung sollten anhand von **Manifest-/Schema-Metadaten**
  funktionieren, ohne Plugin-Code auszuführen
- natives Laufzeitverhalten kommt aus dem Pfad `register(api)` des Plugin-Moduls

Diese Trennung ermöglicht OpenClaw, Konfigurationen zu validieren, fehlende/deaktivierte Plugins zu erklären und
UI-/Schema-Hinweise aufzubauen, bevor die vollständige Laufzeit aktiv ist.

### Kanal-Plugins und das gemeinsame Nachrichtentool

Kanal-Plugins müssen für normale Chat-Aktionen kein separates Senden-/Bearbeiten-/Reagieren-Tool registrieren.
OpenClaw behält ein gemeinsames `message`-Tool im Kern, und
Kanal-Plugins besitzen die kanalspezifische Erkennung und Ausführung dahinter.

Die aktuelle Grenze ist:

- der Kern besitzt den gemeinsamen `message`-Tool-Host, Prompt-Verdrahtung, Sitzungs-/Thread-
  Buchführung und den Ausführungs-Dispatch
- Kanal-Plugins besitzen die erkennungsbezogene Bereichslogik für Aktionen, die Fähigkeitserkennung
  und alle kanalspezifischen Schemafragmente
- Kanal-Plugins besitzen die providerspezifische Sitzungs-Konversationsgrammatik, etwa
  wie Konversations-IDs Thread-IDs kodieren oder von Elternkonversationen erben
- Kanal-Plugins führen die endgültige Aktion über ihren Aktionsadapter aus

Für Kanal-Plugins ist die SDK-Oberfläche
`ChannelMessageActionAdapter.describeMessageTool(...)`. Dieser vereinheitlichte Erkennungsaufruf
ermöglicht es einem Plugin, seine sichtbaren Aktionen, Fähigkeiten und Schemaparameter
gemeinsam zurückzugeben, damit diese Teile nicht auseinanderlaufen.

Der Kern übergibt den Laufzeitbereich an diesen Erkennungsschritt. Wichtige Felder sind:

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- vertrauenswürdige eingehende `requesterSenderId`

Das ist für kontextsensitive Plugins wichtig. Ein Kanal kann
Nachrichtenaktionen basierend auf dem aktiven Konto, dem aktuellen Raum/Thread/Nachricht oder der
vertrauenswürdigen Identität des Anfragenden ausblenden oder einblenden, ohne
kanalspezifische Verzweigungen im Kern-`message`-Tool fest zu verdrahten.

Deshalb sind Änderungen am Embedded-Runner-Routing weiterhin Plugin-Arbeit: Der Runner ist
dafür verantwortlich, die aktuelle Chat-/Sitzungsidentität in die Plugin-
Erkennungsgrenze weiterzugeben, damit das gemeinsame `message`-Tool die richtige
kanaleigene Oberfläche für den aktuellen Turn bereitstellt.

Für kanal-eigene Ausführungshilfen sollten gebündelte Plugins die Ausführungs-
Laufzeit innerhalb ihrer eigenen Erweiterungsmodule halten. Der Kern besitzt nicht mehr die Discord-,
Slack-, Telegram- oder WhatsApp-Nachrichtenaktions-Laufzeiten unter `src/agents/tools`.
Wir veröffentlichen keine separaten `plugin-sdk/*-action-runtime`-Unterpfade, und gebündelte
Plugins sollten ihren eigenen lokalen Laufzeitcode direkt aus ihren
erweiterungseigenen Modulen importieren.

Dieselbe Grenze gilt im Allgemeinen auch für providerbenannte SDK-Seams: Der Kern sollte
keine kanalspezifischen Convenience-Barrels für Slack, Discord, Signal,
WhatsApp oder ähnliche Erweiterungen importieren. Wenn der Kern ein Verhalten benötigt, sollte er entweder
das eigene Barrel `api.ts` / `runtime-api.ts` des gebündelten Plugins verwenden oder den Bedarf
in eine schmale generische Fähigkeit im gemeinsamen SDK überführen.

Speziell für Umfragen gibt es zwei Ausführungspfade:

- `outbound.sendPoll` ist die gemeinsame Grundlage für Kanäle, die in das gemeinsame
  Umfragemodell passen
- `actions.handleAction("poll")` ist der bevorzugte Pfad für kanalspezifische
  Umfragesemantik oder zusätzliche Umfrageparameter

Der Kern verschiebt das gemeinsame Parsing von Umfragen jetzt, bis der
Plugin-eigene Umfrage-Dispatch die Aktion abgelehnt hat, sodass Plugin-eigene
Umfrage-Handler kanalspezifische Umfragefelder akzeptieren können, ohne zuerst
vom generischen Umfrageparser blockiert zu werden.

Siehe [Ladepipeline](#load-pipeline) für die vollständige Startsequenz.

## Modell der Fähigkeits-Eigentümerschaft

OpenClaw behandelt ein natives Plugin als Eigentumsgrenze für ein **Unternehmen** oder ein
**Feature**, nicht als Sammelsurium nicht zusammenhängender Integrationen.

Das bedeutet:

- ein Unternehmens-Plugin sollte normalerweise alle OpenClaw-bezogenen
  Oberflächen dieses Unternehmens besitzen
- ein Feature-Plugin sollte normalerweise die vollständige Oberfläche des von ihm eingeführten
  Features besitzen
- Kanäle sollten gemeinsame Kernfähigkeiten nutzen, statt Provider-Verhalten ad hoc
  neu zu implementieren

Beispiele:

- das gebündelte Plugin `openai` besitzt OpenAI-Modell-Provider-Verhalten und OpenAI-
  Verhalten für Sprache + Echtzeit-Stimme + Medienverständnis + Bildgenerierung
- das gebündelte Plugin `elevenlabs` besitzt das Sprachverhalten von ElevenLabs
- das gebündelte Plugin `microsoft` besitzt das Sprachverhalten von Microsoft
- das gebündelte Plugin `google` besitzt das Google-Modell-Provider-Verhalten sowie Google-
  Verhalten für Medienverständnis + Bildgenerierung + Websuche
- das gebündelte Plugin `firecrawl` besitzt das Web-Abruf-Verhalten von Firecrawl
- die gebündelten Plugins `minimax`, `mistral`, `moonshot` und `zai` besitzen ihre
  Backends für Medienverständnis
- das gebündelte Plugin `qwen` besitzt das Qwen-Text-Provider-Verhalten sowie
  Medienverständnis- und Videogenerierungsverhalten
- das Plugin `voice-call` ist ein Feature-Plugin: Es besitzt Anruftransport, Tools,
  CLI, Routen und Twilio-Media-Stream-Bridging, nutzt aber gemeinsame Fähigkeiten für Sprache
  sowie Echtzeit-Transkription und Echtzeit-Stimme, statt Anbieter-Plugins direkt
  zu importieren

Der angestrebte Endzustand ist:

- OpenAI lebt in einem Plugin, auch wenn es Textmodelle, Sprache, Bilder und
  zukünftiges Video umfasst
- ein anderer Anbieter kann dasselbe für seinen eigenen Oberflächenbereich tun
- Kanäle kümmern sich nicht darum, welches Anbieter-Plugin den Provider besitzt; sie nutzen den
  gemeinsamen Fähigkeitsvertrag, den der Kern bereitstellt

Das ist der entscheidende Unterschied:

- **plugin** = Eigentumsgrenze
- **capability** = Kernvertrag, den mehrere Plugins implementieren oder nutzen können

Wenn OpenClaw also eine neue Domäne wie Video hinzufügt, lautet die erste Frage nicht
„welcher Provider sollte die Videoverarbeitung fest verdrahten?“ Die erste Frage ist „was ist
der zentrale Video-Fähigkeitsvertrag?“ Sobald dieser Vertrag existiert, können Anbieter-Plugins
sich dafür registrieren und Kanal-/Feature-Plugins ihn nutzen.

Wenn die Fähigkeit noch nicht existiert, ist der richtige Schritt normalerweise:

1. die fehlende Fähigkeit im Kern definieren
2. sie typisiert über die Plugin-API/Laufzeit verfügbar machen
3. Kanäle/Features an diese Fähigkeit anbinden
4. Anbieter-Plugins ihre Implementierungen registrieren lassen

So bleibt Eigentümerschaft explizit, während Kernverhalten vermieden wird, das von einem
einzigen Anbieter oder einem einmaligen plugin-spezifischen Codepfad abhängt.

### Fähigkeitsschichtung

Verwenden Sie dieses Denkmodell, wenn Sie entscheiden, wohin Code gehört:

- **Kern-Fähigkeitsebene**: gemeinsame Orchestrierung, Richtlinien, Fallback,
  Regeln zum Zusammenführen von Konfigurationen, Zustellungssemantik und typisierte Verträge
- **Anbieter-Plugin-Ebene**: anbieterspezifische APIs, Authentifizierung, Modellkataloge, Sprach-
  synthese, Bildgenerierung, zukünftige Video-Backends, Nutzungsendpunkte
- **Kanal-/Feature-Plugin-Ebene**: Integration für Slack/Discord/voice-call/usw.,
  die Kernfähigkeiten nutzt und auf einer Oberfläche bereitstellt

Zum Beispiel folgt TTS dieser Struktur:

- der Kern besitzt die TTS-Richtlinie zur Antwortzeit, Fallback-Reihenfolge, Präferenzen und Kanalzustellung
- `openai`, `elevenlabs` und `microsoft` besitzen die Synthese-Implementierungen
- `voice-call` nutzt die Laufzeit-Hilfsfunktion für Telefonie-TTS

Dasselbe Muster sollte für zukünftige Fähigkeiten bevorzugt werden.

### Beispiel für ein Unternehmens-Plugin mit mehreren Fähigkeiten

Ein Unternehmens-Plugin sollte sich von außen kohärent anfühlen. Wenn OpenClaw gemeinsame
Verträge für Modelle, Sprache, Echtzeit-Transkription, Echtzeit-Stimme, Medienverständnis,
Bildgenerierung, Videogenerierung, Web-Abruf und Websuche hat,
kann ein Anbieter alle seine Oberflächen an einer Stelle besitzen:

```ts
import type { OpenClawPluginDefinition } from "openclaw/plugin-sdk/plugin-entry";
import {
  describeImageWithModel,
  transcribeOpenAiCompatibleAudio,
} from "openclaw/plugin-sdk/media-understanding";

const plugin: OpenClawPluginDefinition = {
  id: "exampleai",
  name: "ExampleAI",
  register(api) {
    api.registerProvider({
      id: "exampleai",
      // auth/model catalog/runtime hooks
    });

    api.registerSpeechProvider({
      id: "exampleai",
      // vendor speech config — implement the SpeechProviderPlugin interface directly
    });

    api.registerMediaUnderstandingProvider({
      id: "exampleai",
      capabilities: ["image", "audio", "video"],
      async describeImage(req) {
        return describeImageWithModel({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
      async transcribeAudio(req) {
        return transcribeOpenAiCompatibleAudio({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
    });

    api.registerWebSearchProvider(
      createPluginBackedWebSearchProvider({
        id: "exampleai-search",
        // credential + fetch logic
      }),
    );
  },
};

export default plugin;
```

Wichtig sind nicht die genauen Namen der Hilfsfunktionen. Die Struktur ist entscheidend:

- ein Plugin besitzt die Anbieteroberfläche
- der Kern besitzt weiterhin die Fähigkeitsverträge
- Kanal- und Feature-Plugins nutzen Hilfsfunktionen aus `api.runtime.*`, nicht Anbietercode
- Vertragstests können prüfen, dass das Plugin die Fähigkeiten registriert hat,
  die es für sich beansprucht

### Fähigkeitsbeispiel: Videoverständnis

OpenClaw behandelt Bild-/Audio-/Videoverständnis bereits als eine gemeinsame
Fähigkeit. Dasselbe Eigentumsmodell gilt auch dort:

1. der Kern definiert den Vertrag für Medienverständnis
2. Anbieter-Plugins registrieren je nach Anwendbarkeit `describeImage`, `transcribeAudio` und
   `describeVideo`
3. Kanal- und Feature-Plugins nutzen das gemeinsame Kernverhalten, statt
   direkt Anbietercode anzubinden

So wird vermieden, die Video-Annahmen eines Anbieters im Kern fest einzubauen. Das Plugin besitzt
die Anbieteroberfläche; der Kern besitzt den Fähigkeitsvertrag und das Fallback-Verhalten.

Videogenerierung verwendet bereits genau diese Reihenfolge: Der Kern besitzt den typisierten
Fähigkeitsvertrag und die Laufzeit-Hilfsfunktion, und Anbieter-Plugins registrieren
Implementierungen von `api.registerVideoGenerationProvider(...)` dafür.

Benötigen Sie eine konkrete Checkliste für die Einführung? Siehe
[Capability Cookbook](/de/plugins/architecture).

## Verträge und Durchsetzung

Die Plugin-API-Oberfläche ist absichtlich typisiert und in
`OpenClawPluginApi` zentralisiert. Dieser Vertrag definiert die unterstützten Registrierungspunkte und
die Laufzeit-Hilfsfunktionen, auf die sich ein Plugin verlassen darf.

Warum das wichtig ist:

- Plugin-Autoren erhalten einen stabilen internen Standard
- der Kern kann doppelte Eigentümerschaft ablehnen, etwa wenn zwei Plugins dieselbe
  Provider-ID registrieren
- beim Start können umsetzbare Diagnosen für fehlerhafte Registrierungen angezeigt werden
- Vertragstests können die Eigentümerschaft gebündelter Plugins durchsetzen und lautlose Abweichungen verhindern

Es gibt zwei Ebenen der Durchsetzung:

1. **Durchsetzung bei der Laufzeitregistrierung**
   Die Plugin-Registry validiert Registrierungen während des Ladens der Plugins. Beispiele:
   doppelte Provider-IDs, doppelte Sprach-Provider-IDs und fehlerhafte
   Registrierungen erzeugen Plugin-Diagnosen statt undefiniertes Verhalten.
2. **Vertragstests**
   Gebündelte Plugins werden bei Testläufen in Vertrags-Registries erfasst, sodass
   OpenClaw Eigentümerschaft explizit prüfen kann. Heute wird das für Modell-
   Provider, Sprach-Provider, Websuch-Provider und gebündelte Registrierungseigentümerschaft verwendet.

Der praktische Effekt ist, dass OpenClaw von vornherein weiß, welches Plugin welche
Oberfläche besitzt. Das ermöglicht es Kern und Kanälen, nahtlos zusammenzusetzen, weil
Eigentümerschaft deklariert, typisiert und testbar ist statt implizit.

### Was in einen Vertrag gehört

Gute Plugin-Verträge sind:

- typisiert
- klein
- fähigkeitsspezifisch
- im Besitz des Kerns
- von mehreren Plugins wiederverwendbar
- von Kanälen/Features ohne Anbieterwissen nutzbar

Schlechte Plugin-Verträge sind:

- anbieterspezifische Richtlinien, die im Kern verborgen sind
- einmalige Plugin-Notausgänge, die die Registry umgehen
- Kanalcode, der direkt in eine Anbieterimplementierung greift
- ad hoc erzeugte Laufzeitobjekte, die nicht Teil von `OpenClawPluginApi` oder
  `api.runtime` sind

Im Zweifel: heben Sie die Abstraktionsebene an. Definieren Sie zuerst die Fähigkeit und lassen Sie
dann Plugins daran andocken.

## Ausführungsmodell

Native OpenClaw-Plugins laufen **im Prozess** mit dem Gateway. Sie sind nicht
sandboxed. Ein geladenes natives Plugin hat dieselbe prozessweite Vertrauensgrenze wie
Kerncode.

Auswirkungen:

- ein natives Plugin kann Tools, Netzwerk-Handler, Hooks und Dienste registrieren
- ein Fehler in einem nativen Plugin kann das Gateway zum Absturz bringen oder destabilisieren
- ein bösartiges natives Plugin entspricht beliebiger Codeausführung innerhalb des
  OpenClaw-Prozesses

Kompatible Bundles sind standardmäßig sicherer, weil OpenClaw sie derzeit als
Metadaten-/Inhaltspakete behandelt. In aktuellen Releases bedeutet das größtenteils gebündelte
Skills.

Verwenden Sie Allowlists und explizite Installations-/Ladepfade für nicht gebündelte Plugins. Behandeln Sie
Workspace-Plugins als Code für die Entwicklungszeit, nicht als Produktionsstandard.

Für gebündelte Workspace-Paketnamen sollte die Plugin-ID im npm-Namen verankert bleiben:
standardmäßig `@openclaw/<id>` oder ein genehmigtes typisiertes Suffix wie
`-provider`, `-plugin`, `-speech`, `-sandbox` oder `-media-understanding`, wenn
das Paket absichtlich eine engere Plugin-Rolle bereitstellt.

Wichtiger Vertrauenshinweis:

- `plugins.allow` vertraut **Plugin-IDs**, nicht der Herkunft der Quelle.
- Ein Workspace-Plugin mit derselben ID wie ein gebündeltes Plugin überschattet
  absichtlich die gebündelte Kopie, wenn dieses Workspace-Plugin aktiviert/in der Allowlist ist.
- Das ist normal und nützlich für lokale Entwicklung, Patch-Tests und Hotfixes.

## Exportgrenze

OpenClaw exportiert Fähigkeiten, nicht Implementierungs-Bequemlichkeit.

Halten Sie die Fähigkeitsregistrierung öffentlich. Beschneiden Sie Nicht-Vertrags-Hilfsexporte:

- Hilfs-Unterpfade spezifisch für gebündelte Plugins
- Laufzeit-Plumbing-Unterpfade, die nicht als öffentliche API gedacht sind
- anbieterspezifische Convenience-Hilfsfunktionen
- Setup-/Onboarding-Hilfsfunktionen, die Implementierungsdetails sind

Einige Hilfs-Unterpfade gebündelter Plugins bleiben aus Kompatibilitätsgründen und für die Pflege
gebündelter Plugins weiterhin in der generierten SDK-Exportzuordnung enthalten. Aktuelle Beispiele sind
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` und mehrere `plugin-sdk/matrix*`-Seams. Behandeln Sie diese als
reservierte, implementierungsbezogene Exporte und nicht als das empfohlene SDK-Muster für
neue Drittanbieter-Plugins.

## Ladepipeline

Beim Start macht OpenClaw grob Folgendes:

1. mögliche Plugin-Wurzeln erkennen
2. native oder kompatible Bundle-Manifeste und Paketmetadaten lesen
3. unsichere Kandidaten ablehnen
4. Plugin-Konfiguration normalisieren (`plugins.enabled`, `allow`, `deny`, `entries`,
   `slots`, `load.paths`)
5. für jeden Kandidaten die Aktivierung entscheiden
6. aktivierte native Module per jiti laden
7. native Hooks `register(api)` (oder `activate(api)` — ein Legacy-Alias) aufrufen und Registrierungen in der Plugin-Registry sammeln
8. die Registry für Befehle/Laufzeitoberflächen verfügbar machen

<Note>
`activate` ist ein Legacy-Alias für `register` — der Loader löst den vorhandenen Hook auf (`def.register ?? def.activate`) und ruft ihn an derselben Stelle auf. Alle gebündelten Plugins verwenden `register`; bevorzugen Sie `register` für neue Plugins.
</Note>

Die Sicherheitsprüfungen erfolgen **vor** der Laufzeitausführung. Kandidaten werden blockiert,
wenn der Einstiegspunkt die Plugin-Wurzel verlässt, der Pfad weltweit beschreibbar ist oder die Pfad-
Eigentümerschaft bei nicht gebündelten Plugins verdächtig aussieht.

### Manifest-First-Verhalten

Das Manifest ist die Quelle der Wahrheit für die Steuerungsebene. OpenClaw nutzt es, um:

- das Plugin zu identifizieren
- deklarierte Kanäle/Skills/Konfigurationsschema oder Bundle-Fähigkeiten zu erkennen
- `plugins.entries.<id>.config` zu validieren
- Labels/Platzhalter der Control UI zu ergänzen
- Installations-/Katalogmetadaten anzuzeigen
- günstige Aktivierungs- und Setup-Deskriptoren zu erhalten, ohne die Plugin-Laufzeit zu laden

Für native Plugins ist das Laufzeitmodul der Teil der Datenebene. Es registriert
tatsächliches Verhalten wie Hooks, Tools, Befehle oder Provider-Flows.

Optionale Manifest-Blöcke `activation` und `setup` bleiben auf der Steuerungsebene.
Sie sind reine Metadaten-Deskriptoren für Aktivierungsplanung und Setup-Erkennung;
sie ersetzen nicht die Laufzeitregistrierung, `register(...)` oder `setupEntry`.

### Was der Loader zwischenspeichert

OpenClaw hält kurze prozessinterne Caches für:

- Erkennungsergebnisse
- Manifest-Registry-Daten
- geladene Plugin-Registries

Diese Caches reduzieren burstartigen Startaufwand und den Overhead wiederholter Befehle. Sie lassen sich sicher
als kurzlebige Performance-Caches verstehen, nicht als Persistenz.

Hinweis zur Performance:

- Setzen Sie `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` oder
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1`, um diese Caches zu deaktivieren.
- Passen Sie die Cache-Fenster mit `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` und
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS` an.

## Registry-Modell

Geladene Plugins verändern nicht direkt beliebige globale Kernzustände. Sie registrieren sich in einer
zentralen Plugin-Registry.

Die Registry verfolgt:

- Plugin-Einträge (Identität, Quelle, Ursprung, Status, Diagnosen)
- Tools
- Legacy-Hooks und typisierte Hooks
- Kanäle
- Provider
- Gateway-RPC-Handler
- HTTP-Routen
- CLI-Registrare
- Hintergrunddienste
- Plugin-eigene Befehle

Kernfunktionen lesen dann aus dieser Registry, statt direkt mit Plugin-Modulen zu sprechen.
Dadurch bleibt das Laden einseitig:

- Plugin-Modul -> Registry-Registrierung
- Kern-Laufzeit -> Registry-Nutzung

Diese Trennung ist wichtig für die Wartbarkeit. Sie bedeutet, dass die meisten Kernoberflächen nur
einen Integrationspunkt brauchen: „die Registry lesen“, nicht „jedes Plugin-Modul speziell behandeln“.

## Rückrufe für Konversationsbindung

Plugins, die eine Konversation binden, können reagieren, wenn eine Genehmigung aufgelöst wird.

Verwenden Sie `api.onConversationBindingResolved(...)`, um einen Rückruf zu erhalten, nachdem eine Bindungs-
anfrage genehmigt oder abgelehnt wurde:

```ts
export default {
  id: "my-plugin",
  register(api) {
    api.onConversationBindingResolved(async (event) => {
      if (event.status === "approved") {
        // A binding now exists for this plugin + conversation.
        console.log(event.binding?.conversationId);
        return;
      }

      // The request was denied; clear any local pending state.
      console.log(event.request.conversation.conversationId);
    });
  },
};
```

Felder der Rückrufnutzlast:

- `status`: `"approved"` oder `"denied"`
- `decision`: `"allow-once"`, `"allow-always"` oder `"deny"`
- `binding`: die aufgelöste Bindung für genehmigte Anfragen
- `request`: die ursprüngliche Anfragezusammenfassung, Trennhinweis, Sender-ID und
  Konversationsmetadaten

Dieser Rückruf dient nur zur Benachrichtigung. Er ändert nicht, wer eine Konversation binden darf,
und er läuft, nachdem die Genehmigungsverarbeitung des Kerns abgeschlossen ist.

## Provider-Laufzeit-Hooks

Provider-Plugins haben jetzt zwei Ebenen:

- Manifest-Metadaten: `providerAuthEnvVars` für günstige Provider-Umgebungs-Auth-Abfragen
  vor dem Laden der Laufzeit, `providerAuthAliases` für Provider-Varianten, die sich
  Auth teilen, `channelEnvVars` für günstige Kanal-Umgebungs-/Setup-Abfragen vor dem Laden der Laufzeit,
  sowie `providerAuthChoices` für günstige Onboarding-/Auth-Auswahllabels und
  CLI-Flag-Metadaten vor dem Laden der Laufzeit
- Hooks zur Konfigurationszeit: `catalog` / Legacy-`discovery` plus `applyConfigDefaults`
- Laufzeit-Hooks: `normalizeModelId`, `normalizeTransport`,
  `normalizeConfig`,
  `applyNativeStreamingUsageCompat`, `resolveConfigApiKey`,
  `resolveSyntheticAuth`, `resolveExternalAuthProfiles`,
  `shouldDeferSyntheticProfileAuth`,
  `resolveDynamicModel`, `prepareDynamicModel`, `normalizeResolvedModel`,
  `contributeResolvedModelCompat`, `capabilities`,
  `normalizeToolSchemas`, `inspectToolSchemas`,
  `resolveReasoningOutputMode`, `prepareExtraParams`, `createStreamFn`,
  `wrapStreamFn`, `resolveTransportTurnState`,
  `resolveWebSocketSessionPolicy`, `formatApiKey`, `refreshOAuth`,
  `buildAuthDoctorHint`, `matchesContextOverflowError`,
  `classifyFailoverReason`, `isCacheTtlEligible`,
  `buildMissingAuthMessage`, `suppressBuiltInModel`, `augmentModelCatalog`,
  `isBinaryThinking`, `supportsXHighThinking`,
  `resolveDefaultThinkingLevel`, `isModernModelRef`, `prepareRuntimeAuth`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `createEmbeddingProvider`,
  `buildReplayPolicy`,
  `sanitizeReplayHistory`, `validateReplayTurns`, `onModelSelected`

OpenClaw besitzt weiterhin die generische Agent-Schleife, Failover, Transkriptbehandlung und
Tool-Richtlinien. Diese Hooks sind die Erweiterungsoberfläche für anbieterspezifisches Verhalten, ohne
einen vollständig benutzerdefinierten Inferenztransport zu benötigen.

Verwenden Sie Manifest-`providerAuthEnvVars`, wenn der Provider umgebungsbasierte Anmeldedaten hat,
die generische Auth-/Status-/Modellauswahlpfade sehen sollen, ohne die Plugin-
Laufzeit zu laden. Verwenden Sie Manifest-`providerAuthAliases`, wenn eine Provider-ID die
Umgebungsvariablen, Auth-Profile, konfigurationsgestützte Authentifizierung und die
API-Schlüssel-Onboarding-Auswahl einer anderen Provider-ID wiederverwenden soll. Verwenden Sie Manifest-`providerAuthChoices`, wenn
CLI-Oberflächen für Onboarding-/Auth-Auswahl die Auswahl-ID, Gruppenlabels und einfache
Auth-Verdrahtung mit einem Flag des Providers kennen sollen, ohne die Provider-Laufzeit zu laden. Behalten Sie in der Provider-Laufzeit
`envVars` für operatorseitige Hinweise wie Onboarding-Labels oder OAuth-
client-id-/client-secret-Setup-Variablen.

Verwenden Sie Manifest-`channelEnvVars`, wenn ein Kanal umgebungsgetriebene Authentifizierung oder Einrichtung hat,
die generischer Shell-Umgebungs-Fallback, Konfigurations-/Statusprüfungen oder Setup-Prompts sehen sollen,
ohne die Kanal-Laufzeit zu laden.

### Hook-Reihenfolge und Verwendung

Für Modell-/Provider-Plugins ruft OpenClaw Hooks in ungefähr dieser Reihenfolge auf.
Die Spalte „Wann verwenden“ ist der schnelle Entscheidungsleitfaden.

| #   | Hook                              | Was er macht                                                                                                   | Wann verwenden                                                                                                                              |
| --- | --------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `catalog`                         | Provider-Konfiguration während der Generierung von `models.json` in `models.providers` veröffentlichen         | Der Provider besitzt einen Katalog oder Standardwerte für die Basis-URL                                                                     |
| 2   | `applyConfigDefaults`             | Provider-eigene globale Konfigurationsstandardwerte bei der Materialisierung der Konfiguration anwenden        | Standardwerte hängen vom Auth-Modus, der Umgebung oder der Semantik der Provider-Modellfamilie ab                                          |
| --  | _(integrierte Modellsuche)_       | OpenClaw versucht zuerst den normalen Registry-/Katalogpfad                                                    | _(kein Plugin-Hook)_                                                                                                                        |
| 3   | `normalizeModelId`                | Legacy- oder Vorschau-Aliasse für Modell-IDs vor der Suche normalisieren                                       | Der Provider besitzt die Alias-Bereinigung vor der kanonischen Modellauflösung                                                              |
| 4   | `normalizeTransport`              | `api` / `baseUrl` einer Provider-Familie vor der generischen Modellzusammensetzung normalisieren              | Der Provider besitzt die Transport-Bereinigung für benutzerdefinierte Provider-IDs in derselben Transportfamilie                           |
| 5   | `normalizeConfig`                 | `models.providers.<id>` vor der Laufzeit-/Provider-Auflösung normalisieren                                     | Der Provider benötigt Konfigurationsbereinigung, die beim Plugin liegen sollte; gebündelte Hilfsfunktionen der Google-Familie stützen auch unterstützte Google-Konfigurationseinträge ab |
| 6   | `applyNativeStreamingUsageCompat` | Umschreibungen für Kompatibilität der nativen Streaming-Nutzung auf Konfigurations-Provider anwenden           | Der Provider benötigt endpunktgesteuerte Korrekturen an Metadaten zur nativen Streaming-Nutzung                                            |
| 7   | `resolveConfigApiKey`             | Authentifizierung über Umgebungsmarker für Konfigurations-Provider vor dem Laden der Laufzeit-Auth auflösen   | Der Provider besitzt die Auflösung von API-Schlüsseln über Umgebungsmarker; `amazon-bedrock` hat hier ebenfalls einen eingebauten AWS-Umgebungsmarker-Resolver |
| 8   | `resolveSyntheticAuth`            | lokale/self-hosted oder konfigurationsgestützte Authentifizierung bereitstellen, ohne Klartext zu persistieren | Der Provider kann mit einem synthetischen/lokalen Anmeldedatenmarker arbeiten                                                               |
| 9   | `resolveExternalAuthProfiles`     | provider-eigene externe Auth-Profile überlagern; standardmäßige `persistence` ist `runtime-only` für CLI-/app-eigene Anmeldedaten | Der Provider verwendet externe Auth-Anmeldedaten wieder, ohne kopierte Refresh-Tokens zu persistieren                                      |
| 10  | `shouldDeferSyntheticProfileAuth` | gespeicherte synthetische Profil-Platzhalter hinter umgebungs-/konfigurationsgestützter Authentifizierung einordnen | Der Provider speichert synthetische Platzhalterprofile, die keinen Vorrang haben sollten                                                    |
| 11  | `resolveDynamicModel`             | synchrones Fallback für provider-eigene Modell-IDs, die noch nicht in der lokalen Registry sind               | Der Provider akzeptiert beliebige vorgelagerte Modell-IDs                                                                                   |
| 12  | `prepareDynamicModel`             | asynchrones Aufwärmen, dann wird `resolveDynamicModel` erneut ausgeführt                                       | Der Provider benötigt Netzwerkmetadaten, bevor unbekannte IDs aufgelöst werden können                                                      |
| 13  | `normalizeResolvedModel`          | endgültige Umschreibung, bevor der eingebettete Runner das aufgelöste Modell verwendet                         | Der Provider benötigt Transport-Umschreibungen, verwendet aber weiterhin einen Kern-Transport                                               |
| 14  | `contributeResolvedModelCompat`   | Kompatibilitäts-Flags für Anbietermodelle hinter einem anderen kompatiblen Transport beitragen                 | Der Provider erkennt seine eigenen Modelle auf Proxy-Transporten, ohne den Provider zu übernehmen                                           |
| 15  | `capabilities`                    | provider-eigene Transkript-/Tooling-Metadaten, die von gemeinsamer Kernlogik genutzt werden                   | Der Provider benötigt Besonderheiten für Transkripte oder Provider-Familien                                                                 |
| 16  | `normalizeToolSchemas`            | Tool-Schemata normalisieren, bevor der eingebettete Runner sie sieht                                           | Der Provider benötigt Schemabereinigung für Transportfamilien                                                                               |
| 17  | `inspectToolSchemas`              | provider-eigene Schemadiagnosen nach der Normalisierung sichtbar machen                                        | Der Provider möchte Schlüsselwortwarnungen anzeigen, ohne dem Kern providerspezifische Regeln beizubringen                                 |
| 18  | `resolveReasoningOutputMode`      | nativen oder getaggten Vertrag für Reasoning-Ausgaben auswählen                                                | Der Provider benötigt getaggte Reasoning-/Final-Ausgabe statt nativer Felder                                                                |
| 19  | `prepareExtraParams`              | Normalisierung von Anfrageparametern vor generischen Wrappern für Stream-Optionen                              | Der Provider benötigt Standard-Anfrageparameter oder providerbezogene Parameterbereinigung                                                  |
| 20  | `createStreamFn`                  | den normalen Stream-Pfad vollständig durch einen benutzerdefinierten Transport ersetzen                        | Der Provider benötigt ein benutzerdefiniertes Wire-Protokoll, nicht nur einen Wrapper                                                      |
| 21  | `wrapStreamFn`                    | Stream-Wrapper, nachdem generische Wrapper angewendet wurden                                                   | Der Provider benötigt Kompatibilitäts-Wrapper für Anfrage-Header/Body/Modell ohne benutzerdefinierten Transport                            |
| 22  | `resolveTransportTurnState`       | native turnbezogene Transport-Header oder Metadaten anhängen                                                   | Der Provider möchte, dass generische Transporte die native Turn-Identität des Providers senden                                              |
| 23  | `resolveWebSocketSessionPolicy`   | native WebSocket-Header oder Richtlinie für Session-Abklingzeit anhängen                                       | Der Provider möchte, dass generische WS-Transporte Session-Header oder Fallback-Richtlinien abstimmen                                      |
| 24  | `formatApiKey`                    | Formatter für Auth-Profile: gespeichertes Profil wird zur Laufzeitzeichenfolge `apiKey`                        | Der Provider speichert zusätzliche Auth-Metadaten und benötigt eine benutzerdefinierte Laufzeit-Tokenform                                  |
| 25  | `refreshOAuth`                    | OAuth-Refresh-Override für benutzerdefinierte Refresh-Endpunkte oder Richtlinien bei Refresh-Fehlern           | Der Provider passt nicht zu den gemeinsamen `pi-ai`-Refreshern                                                                              |
| 26  | `buildAuthDoctorHint`             | Reparaturhinweis, der angehängt wird, wenn der OAuth-Refresh fehlschlägt                                       | Der Provider benötigt provider-eigene Hinweise zur Auth-Reparatur nach einem Refresh-Fehler                                                |
| 27  | `matchesContextOverflowError`     | provider-eigener Matcher für Überläufe des Kontextfensters                                                     | Der Provider hat rohe Überlauffehler, die generische Heuristiken übersehen würden                                                          |
| 28  | `classifyFailoverReason`          | provider-eigene Klassifizierung von Failover-Gründen                                                           | Der Provider kann rohe API-/Transportfehler auf Ratenbegrenzung/Überlastung/usw. abbilden                                                  |
| 29  | `isCacheTtlEligible`              | Richtlinie für Prompt-Cache bei Proxy-/Backhaul-Providern                                                      | Der Provider benötigt proxyspezifische Steuerung für Cache-TTL                                                                              |
| 30  | `buildMissingAuthMessage`         | Ersatz für die generische Wiederherstellungsnachricht bei fehlender Authentifizierung                          | Der Provider benötigt einen providerspezifischen Wiederherstellungshinweis bei fehlender Authentifizierung                                  |
| 31  | `suppressBuiltInModel`            | Unterdrückung veralteter vorgelagerter Modelle plus optionaler benutzerseitiger Fehlerhinweis                 | Der Provider muss veraltete vorgelagerte Zeilen ausblenden oder durch einen Anbieterhinweis ersetzen                                       |
| 32  | `augmentModelCatalog`             | synthetische/endgültige Katalogzeilen, die nach der Erkennung angehängt werden                                 | Der Provider benötigt synthetische Vorwärtskompatibilitäts-Zeilen in `models list` und Auswahllisten                                       |
| 33  | `isBinaryThinking`                | Reasoning-Umschalter Ein/Aus für Provider mit binärem Thinking                                                 | Der Provider bietet nur binäres Thinking Ein/Aus an                                                                                         |
| 34  | `supportsXHighThinking`           | `xhigh`-Reasoning-Unterstützung für ausgewählte Modelle                                                        | Der Provider möchte `xhigh` nur für eine Teilmenge von Modellen                                                                             |
| 35  | `resolveDefaultThinkingLevel`     | Standardstufe für `/think` für eine bestimmte Modellfamilie auflösen                                           | Der Provider besitzt die Standardrichtlinie für `/think` einer Modellfamilie                                                                |
| 36  | `isModernModelRef`                | Matcher für moderne Modelle für Live-Profilfilter und Smoke-Auswahl                                            | Der Provider besitzt das Matching bevorzugter Modelle für Live-/Smoke-Tests                                                                 |
| 37  | `prepareRuntimeAuth`              | eine konfigurierte Anmeldedate in das tatsächliche Laufzeit-Token/den tatsächlichen Schlüssel direkt vor der Inferenz umwandeln | Der Provider benötigt einen Tokenaustausch oder kurzlebige Anfrage-Anmeldedaten                                                            |
| 38  | `resolveUsageAuth`                | Nutzungs-/Abrechnungs-Anmeldedaten für `/usage` und verwandte Statusoberflächen auflösen                      | Der Provider benötigt benutzerdefiniertes Token-Parsen für Nutzung/Kontingente oder andere Nutzungs-Anmeldedaten                           |
| 39  | `fetchUsageSnapshot`              | provider-spezifische Nutzungs-/Kontingent-Snapshots abrufen und normalisieren, nachdem die Authentifizierung aufgelöst wurde | Der Provider benötigt einen provider-spezifischen Nutzungsendpunkt oder Payload-Parser                                                     |
| 40  | `createEmbeddingProvider`         | einen provider-eigenen Embedding-Adapter für Speicher/Suche erstellen                                          | Embedding-Verhalten für Speicher gehört zum Provider-Plugin                                                                                 |
| 41  | `buildReplayPolicy`               | eine Replay-Richtlinie zurückgeben, die die Transkriptbehandlung für den Provider steuert                      | Der Provider benötigt eine benutzerdefinierte Transkript-Richtlinie (zum Beispiel das Entfernen von Thinking-Blöcken)                      |
| 42  | `sanitizeReplayHistory`           | Replay-Verlauf nach generischer Transkriptbereinigung umschreiben                                              | Der Provider benötigt provider-spezifische Umschreibungen des Replay-Verlaufs über gemeinsame Hilfsfunktionen zur Kompaktierung hinaus     |
| 43  | `validateReplayTurns`             | endgültige Validierung oder Umformung von Replay-Turns vor dem eingebetteten Runner                            | Der Provider-Transport benötigt strengere Turn-Validierung nach generischer Bereinigung                                                    |
| 44  | `onModelSelected`                 | provider-eigene Seiteneffekte nach der Modellauswahl ausführen                                                 | Der Provider benötigt Telemetrie oder provider-eigenen Zustand, wenn ein Modell aktiv wird                                                 |

`normalizeModelId`, `normalizeTransport` und `normalizeConfig` prüfen zuerst das
zugeordnete Provider-Plugin und fallen dann auf andere Hook-fähige Provider-Plugins zurück,
bis eines tatsächlich die Modell-ID oder den Transport/die Konfiguration ändert. So bleiben
Alias-/Kompatibilitäts-Shims für Provider funktionsfähig, ohne dass der Aufrufer wissen muss, welches
gebündelte Plugin die Umschreibung besitzt. Wenn kein Provider-Hook einen unterstützten
Google-Familien-Konfigurationseintrag umschreibt, führt der gebündelte Google-Konfigurationsnormalisierer
diese Kompatibilitätsbereinigung weiterhin aus.

Wenn der Provider ein vollständig benutzerdefiniertes Wire-Protokoll oder einen benutzerdefinierten Anfrage-Ausführer benötigt,
ist das eine andere Klasse von Erweiterung. Diese Hooks sind für Provider-Verhalten gedacht,
das weiterhin auf der normalen Inferenzschleife von OpenClaw läuft.

### Provider-Beispiel

```ts
api.registerProvider({
  id: "example-proxy",
  label: "Example Proxy",
  auth: [],
  catalog: {
    order: "simple",
    run: async (ctx) => {
      const apiKey = ctx.resolveProviderApiKey("example-proxy").apiKey;
      if (!apiKey) {
        return null;
      }
      return {
        provider: {
          baseUrl: "https://proxy.example.com/v1",
          apiKey,
          api: "openai-completions",
          models: [{ id: "auto", name: "Auto" }],
        },
      };
    },
  },
  resolveDynamicModel: (ctx) => ({
    id: ctx.modelId,
    name: ctx.modelId,
    provider: "example-proxy",
    api: "openai-completions",
    baseUrl: "https://proxy.example.com/v1",
    reasoning: false,
    input: ["text"],
    cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
    contextWindow: 128000,
    maxTokens: 8192,
  }),
  prepareRuntimeAuth: async (ctx) => {
    const exchanged = await exchangeToken(ctx.apiKey);
    return {
      apiKey: exchanged.token,
      baseUrl: exchanged.baseUrl,
      expiresAt: exchanged.expiresAt,
    };
  },
  resolveUsageAuth: async (ctx) => {
    const auth = await ctx.resolveOAuthToken();
    return auth ? { token: auth.token } : null;
  },
  fetchUsageSnapshot: async (ctx) => {
    return await fetchExampleProxyUsage(ctx.token, ctx.timeoutMs, ctx.fetchFn);
  },
});
```

### Integrierte Beispiele

- Anthropic verwendet `resolveDynamicModel`, `capabilities`, `buildAuthDoctorHint`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `isCacheTtlEligible`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`
  und `wrapStreamFn`, weil es Vorwärtskompatibilität für Claude 4.6,
  Hinweise für Provider-Familien, Leitlinien zur Auth-Reparatur, Integration von Nutzungsendpunkten,
  Prompt-Cache-Eignung, auth-sensitive Konfigurationsstandardwerte, die
  Standard-/adaptive Thinking-Richtlinie für Claude und Anthropic-spezifische Stream-Gestaltung für
  Beta-Header, `/fast` / `serviceTier` und `context1m` besitzt.
- Die Claude-spezifischen Stream-Hilfsfunktionen von Anthropic bleiben vorerst in der eigenen
  öffentlichen `api.ts` / `contract-api.ts`-Seam des gebündelten Plugins. Diese Paketoberfläche
  exportiert `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
  `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` und die niedrigeren
  Builder für Anthropic-Wrapper, statt das generische SDK um die Beta-Header-Regeln
  eines einzelnen Providers zu erweitern.
- OpenAI verwendet `resolveDynamicModel`, `normalizeResolvedModel` und
  `capabilities` sowie `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `supportsXHighThinking` und `isModernModelRef`,
  weil es Vorwärtskompatibilität für GPT-5.4, die direkte OpenAI-
  Normalisierung `openai-completions` -> `openai-responses`, Codex-sensible Auth-
  Hinweise, Spark-Unterdrückung, synthetische OpenAI-Listenzeilen und die Thinking- /
  Live-Modell-Richtlinie für GPT-5 besitzt; die Stream-Familie `openai-responses-defaults` besitzt die
  gemeinsamen nativen OpenAI-Responses-Wrapper für Attribution-Header,
  `/fast`/`serviceTier`, Text-Verbosity, native Codex-Websuche,
  kompatible Formung von Reasoning-Payloads und Responses-Kontextverwaltung.
- OpenRouter verwendet `catalog` sowie `resolveDynamicModel` und
  `prepareDynamicModel`, weil der Provider ein Pass-through ist und neue
  Modell-IDs verfügbar machen kann, bevor der statische Katalog von OpenClaw aktualisiert wird; außerdem verwendet es
  `capabilities`, `wrapStreamFn` und `isCacheTtlEligible`, um
  provider-spezifische Anfrage-Header, Routing-Metadaten, Reasoning-Patches und
  Prompt-Cache-Richtlinien aus dem Kern herauszuhalten. Seine Replay-Richtlinie stammt aus der
  Familie `passthrough-gemini`, während die Stream-Familie `openrouter-thinking`
  die Proxy-Reasoning-Injektion und das Überspringen von nicht unterstützten Modellen / `auto` besitzt.
- GitHub Copilot verwendet `catalog`, `auth`, `resolveDynamicModel` und
  `capabilities` sowie `prepareRuntimeAuth` und `fetchUsageSnapshot`, weil es
  provider-eigenen Device-Login, Modell-Fallback-Verhalten, Eigenheiten von Claude-Transkripten,
  einen GitHub-Token -> Copilot-Token-Austausch und einen provider-eigenen Nutzungsendpunkt benötigt.
- OpenAI Codex verwendet `catalog`, `resolveDynamicModel`,
  `normalizeResolvedModel`, `refreshOAuth` und `augmentModelCatalog` sowie
  `prepareExtraParams`, `resolveUsageAuth` und `fetchUsageSnapshot`, weil es
  weiterhin auf Kern-OpenAI-Transporten läuft, aber seine Transport-/Basis-URL-
  Normalisierung, OAuth-Refresh-Fallback-Richtlinie, Standard-Transportauswahl,
  synthetische Codex-Katalogzeilen und die Integration des ChatGPT-Nutzungsendpunkts besitzt; es
  teilt dieselbe Stream-Familie `openai-responses-defaults` wie direktes OpenAI.
- Google AI Studio und Gemini CLI OAuth verwenden `resolveDynamicModel`,
  `buildReplayPolicy`, `sanitizeReplayHistory`,
  `resolveReasoningOutputMode`, `wrapStreamFn` und `isModernModelRef`, weil die
  Replay-Familie `google-gemini` Vorwärtskompatibilitäts-Fallback für Gemini 3.1,
  native Replay-Validierung für Gemini, Bereinigung von Bootstrap-Replays,
  getaggten Reasoning-Output-Modus und Matching für moderne Modelle besitzt, während die
  Stream-Familie `google-thinking` die Normalisierung von Gemini-Thinking-Payloads besitzt;
  Gemini CLI OAuth verwendet außerdem `formatApiKey`, `resolveUsageAuth` und
  `fetchUsageSnapshot` für Tokenformatierung, Token-Parsen und Verdrahtung des
  Kontingent-Endpunkts.
- Anthropic Vertex verwendet `buildReplayPolicy` über die
  Replay-Familie `anthropic-by-model`, sodass Claude-spezifische Replay-Bereinigung
  auf Claude-IDs beschränkt bleibt statt auf jeden `anthropic-messages`-Transport.
- Amazon Bedrock verwendet `buildReplayPolicy`, `matchesContextOverflowError`,
  `classifyFailoverReason` und `resolveDefaultThinkingLevel`, weil es
  die Bedrock-spezifische Klassifizierung von Fehlern wie Drosselung/Nicht-bereit/Kontextüberlauf
  für Anthropic-on-Bedrock-Datenverkehr besitzt; seine Replay-Richtlinie teilt weiterhin denselben
  Claude-spezifischen Guard `anthropic-by-model`.
- OpenRouter, Kilocode, Opencode und Opencode Go verwenden `buildReplayPolicy`
  über die Replay-Familie `passthrough-gemini`, weil sie Gemini-
  Modelle über OpenAI-kompatible Transporte proxien und eine Bereinigung von Gemini-
  Thought-Signaturen benötigen, jedoch keine native Gemini-Replay-Validierung oder
  Bootstrap-Umschreibungen.
- MiniMax verwendet `buildReplayPolicy` über die
  Replay-Familie `hybrid-anthropic-openai`, weil ein Provider sowohl
  Anthropic-Nachrichten- als auch OpenAI-kompatible Semantik besitzt; dadurch bleibt das
  Entfernen von Thinking-Blöcken nur auf der Anthropic-Seite auf Claude beschränkt, während der
  Reasoning-Output-Modus wieder auf nativ zurückgesetzt wird, und die Stream-Familie `minimax-fast-mode`
  besitzt Umschreibungen für den Fast-Modus auf dem gemeinsamen Stream-Pfad.
- Moonshot verwendet `catalog` sowie `wrapStreamFn`, weil es weiterhin den gemeinsamen
  OpenAI-Transport nutzt, aber provider-eigene Normalisierung von Thinking-Payloads benötigt; die
  Stream-Familie `moonshot-thinking` bildet Konfiguration plus `/think`-Status auf ihre
  native binäre Thinking-Payload ab.
- Kilocode verwendet `catalog`, `capabilities`, `wrapStreamFn` und
  `isCacheTtlEligible`, weil es provider-eigene Anfrage-Header,
  Normalisierung von Reasoning-Payloads, Gemini-Transkripthinweise und Anthropic-
  Cache-TTL-Steuerung benötigt; die Stream-Familie `kilocode-thinking` hält die Kilo-Thinking-
  Injektion auf dem gemeinsamen Proxy-Stream-Pfad, während `kilo/auto` und
  andere Proxy-Modell-IDs übersprungen werden, die keine expliziten Reasoning-Payloads unterstützen.
- Z.AI verwendet `resolveDynamicModel`, `prepareExtraParams`, `wrapStreamFn`,
  `isCacheTtlEligible`, `isBinaryThinking`, `isModernModelRef`,
  `resolveUsageAuth` und `fetchUsageSnapshot`, weil es GLM-5-Fallback,
  Standardwerte für `tool_stream`, UX für binäres Thinking, Matching moderner Modelle sowie sowohl
  Nutzungs-Auth als auch Kontingentabruf besitzt; die Stream-Familie `tool-stream-default-on` hält
  den standardmäßig aktivierten `tool_stream`-Wrapper aus handgeschriebenem Glue pro Provider heraus.
- xAI verwendet `normalizeResolvedModel`, `normalizeTransport`,
  `contributeResolvedModelCompat`, `prepareExtraParams`, `wrapStreamFn`,
  `resolveSyntheticAuth`, `resolveDynamicModel` und `isModernModelRef`,
  weil es die Normalisierung des nativen xAI-Responses-Transports, Umschreibungen von Grok-
  Fast-Mode-Aliassen, standardmäßiges `tool_stream`, Bereinigung von Strict-Tool / Reasoning-Payload,
  Fallback-Wiederverwendung von Auth für plugin-eigene Tools, Vorwärtskompatibilitäts-Auflösung von Grok-
  Modellen und provider-eigene Kompatibilitätspatches wie xAI-Tool-Schema-
  Profil, nicht unterstützte Schema-Schlüsselwörter, natives `web_search` und HTML-Entity-
  Dekodierung von Tool-Call-Argumenten besitzt.
- Mistral, OpenCode Zen und OpenCode Go verwenden nur `capabilities`, um
  Eigenheiten von Transkripten/Tooling aus dem Kern herauszuhalten.
- Gebündelte Provider nur mit Katalog wie `byteplus`, `cloudflare-ai-gateway`,
  `huggingface`, `kimi-coding`, `nvidia`, `qianfan`,
  `synthetic`, `together`, `venice`, `vercel-ai-gateway` und `volcengine` verwenden
  nur `catalog`.
- Qwen verwendet `catalog` für seinen Text-Provider sowie gemeinsame Registrierungen für Medienverständnis und
  Videogenerierung für seine multimodalen Oberflächen.
- MiniMax und Xiaomi verwenden `catalog` sowie Nutzungs-Hooks, weil ihr `/usage`-
  Verhalten dem Plugin gehört, auch wenn die Inferenz weiterhin über die gemeinsamen
  Transporte läuft.

## Laufzeit-Hilfsfunktionen

Plugins können über `api.runtime` auf ausgewählte Kern-Hilfsfunktionen zugreifen. Für TTS:

```ts
const clip = await api.runtime.tts.textToSpeech({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const result = await api.runtime.tts.textToSpeechTelephony({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const voices = await api.runtime.tts.listVoices({
  provider: "elevenlabs",
  cfg: api.config,
});
```

Hinweise:

- `textToSpeech` gibt die normale Kern-TTS-Ausgabe-Payload für Datei-/Sprachnotiz-Oberflächen zurück.
- Verwendet die Kernkonfiguration `messages.tts` und die Providerauswahl.
- Gibt PCM-Audiopuffer + Abtastrate zurück. Plugins müssen für Provider neu sampeln/kodieren.
- `listVoices` ist je nach Provider optional. Verwenden Sie es für anbieter-eigene Sprachauswahlfelder oder Setup-Flows.
- Sprachlisten können umfangreichere Metadaten wie Sprache, Geschlecht und Persönlichkeitstags für providerbewusste Auswahllisten enthalten.
- OpenAI und ElevenLabs unterstützen heute Telefonie. Microsoft nicht.

Plugins können auch Sprach-Provider über `api.registerSpeechProvider(...)` registrieren.

```ts
api.registerSpeechProvider({
  id: "acme-speech",
  label: "Acme Speech",
  isConfigured: ({ config }) => Boolean(config.messages?.tts),
  synthesize: async (req) => {
    return {
      audioBuffer: Buffer.from([]),
      outputFormat: "mp3",
      fileExtension: ".mp3",
      voiceCompatible: false,
    };
  },
});
```

Hinweise:

- Behalten Sie TTS-Richtlinien, Fallback und Antwortzustellung im Kern.
- Verwenden Sie Sprach-Provider für anbieter-eigenes Syntheseverhalten.
- Legacy-Microsoft-`edge`-Eingabe wird auf die Provider-ID `microsoft` normalisiert.
- Das bevorzugte Eigentumsmodell ist unternehmensorientiert: Ein Anbieter-Plugin kann
  Text-, Sprach-, Bild- und zukünftige Medien-Provider besitzen, wenn OpenClaw diese
  Fähigkeitsverträge hinzufügt.

Für Bild-/Audio-/Videoverständnis registrieren Plugins einen typisierten
Provider für Medienverständnis statt eines generischen Schlüssel-/Wert-Sacks:

```ts
api.registerMediaUnderstandingProvider({
  id: "google",
  capabilities: ["image", "audio", "video"],
  describeImage: async (req) => ({ text: "..." }),
  transcribeAudio: async (req) => ({ text: "..." }),
  describeVideo: async (req) => ({ text: "..." }),
});
```

Hinweise:

- Behalten Sie Orchestrierung, Fallback, Konfiguration und Kanalverdrahtung im Kern.
- Behalten Sie Anbieterverhalten im Provider-Plugin.
- Additive Erweiterungen sollten typisiert bleiben: neue optionale Methoden, neue optionale
  Ergebnisfelder, neue optionale Fähigkeiten.
- Videogenerierung folgt bereits demselben Muster:
  - der Kern besitzt den Fähigkeitsvertrag und die Laufzeit-Hilfsfunktion
  - Anbieter-Plugins registrieren `api.registerVideoGenerationProvider(...)`
  - Feature-/Kanal-Plugins nutzen `api.runtime.videoGeneration.*`

Für Laufzeit-Hilfsfunktionen des Medienverständnisses können Plugins Folgendes aufrufen:

```ts
const image = await api.runtime.mediaUnderstanding.describeImageFile({
  filePath: "/tmp/inbound-photo.jpg",
  cfg: api.config,
  agentDir: "/tmp/agent",
});

const video = await api.runtime.mediaUnderstanding.describeVideoFile({
  filePath: "/tmp/inbound-video.mp4",
  cfg: api.config,
});
```

Für Audio-Transkription können Plugins entweder die Laufzeit des Medienverständnisses
oder den älteren STT-Alias verwenden:

```ts
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  // Optional when MIME cannot be inferred reliably:
  mime: "audio/ogg",
});
```

Hinweise:

- `api.runtime.mediaUnderstanding.*` ist die bevorzugte gemeinsame Oberfläche für
  Bild-/Audio-/Videoverständnis.
- Verwendet die Audiokonfiguration des Kern-Medienverständnisses (`tools.media.audio`) und die Fallback-Reihenfolge der Provider.
- Gibt `{ text: undefined }` zurück, wenn keine Transkriptionsausgabe erzeugt wird (zum Beispiel bei übersprungenen/nicht unterstützten Eingaben).
- `api.runtime.stt.transcribeAudioFile(...)` bleibt als Kompatibilitätsalias bestehen.

Plugins können auch Hintergrund-Subagent-Läufe über `api.runtime.subagent` starten:

```ts
const result = await api.runtime.subagent.run({
  sessionKey: "agent:main:subagent:search-helper",
  message: "Expand this query into focused follow-up searches.",
  provider: "openai",
  model: "gpt-4.1-mini",
  deliver: false,
});
```

Hinweise:

- `provider` und `model` sind optionale Überschreibungen pro Lauf, keine persistenten Sitzungsänderungen.
- OpenClaw berücksichtigt diese Überschreibungsfelder nur für vertrauenswürdige Aufrufer.
- Für plugin-eigene Fallback-Läufe müssen Operatoren mit `plugins.entries.<id>.subagent.allowModelOverride: true` zustimmen.
- Verwenden Sie `plugins.entries.<id>.subagent.allowedModels`, um vertrauenswürdige Plugins auf bestimmte kanonische Ziele `provider/model` zu beschränken, oder `"*"`, um jedes Ziel explizit zu erlauben.
- Läufe untrusted Plugin-Subagenten funktionieren weiterhin, aber Überschreibungsanfragen werden abgelehnt, statt stillschweigend auf Fallback umzuschalten.

Für Websuche können Plugins die gemeinsame Laufzeit-Hilfsfunktion nutzen, statt
in die Verdrahtung des Agent-Tools einzugreifen:

```ts
const providers = api.runtime.webSearch.listProviders({
  config: api.config,
});

const result = await api.runtime.webSearch.search({
  config: api.config,
  args: {
    query: "OpenClaw plugin runtime helpers",
    count: 5,
  },
});
```

Plugins können Websuch-Provider auch über
`api.registerWebSearchProvider(...)` registrieren.

Hinweise:

- Behalten Sie Providerauswahl, Auflösung von Anmeldedaten und gemeinsame Anfrage-Semantik im Kern.
- Verwenden Sie Websuch-Provider für anbieterspezifische Suchtransporte.
- `api.runtime.webSearch.*` ist die bevorzugte gemeinsame Oberfläche für Feature-/Kanal-Plugins, die Suchverhalten benötigen, ohne von dem Wrapper des Agent-Tools abhängig zu sein.

### `api.runtime.imageGeneration`

```ts
const result = await api.runtime.imageGeneration.generate({
  config: api.config,
  args: { prompt: "A friendly lobster mascot", size: "1024x1024" },
});

const providers = api.runtime.imageGeneration.listProviders({
  config: api.config,
});
```

- `generate(...)`: ein Bild mit der konfigurierten Provider-Kette für Bildgenerierung erzeugen.
- `listProviders(...)`: verfügbare Provider für Bildgenerierung und ihre Fähigkeiten auflisten.

## Gateway-HTTP-Routen

Plugins können HTTP-Endpunkte mit `api.registerHttpRoute(...)` verfügbar machen.

```ts
api.registerHttpRoute({
  path: "/acme/webhook",
  auth: "plugin",
  match: "exact",
  handler: async (_req, res) => {
    res.statusCode = 200;
    res.end("ok");
    return true;
  },
});
```

Routenfelder:

- `path`: Routenpfad unter dem Gateway-HTTP-Server.
- `auth`: erforderlich. Verwenden Sie `"gateway"`, um normale Gateway-Authentifizierung zu verlangen, oder `"plugin"` für pluginverwaltete Authentifizierung/Webhook-Verifizierung.
- `match`: optional. `"exact"` (Standard) oder `"prefix"`.
- `replaceExisting`: optional. Erlaubt demselben Plugin, seine eigene vorhandene Routenregistrierung zu ersetzen.
- `handler`: gibt `true` zurück, wenn die Route die Anfrage verarbeitet hat.

Hinweise:

- `api.registerHttpHandler(...)` wurde entfernt und verursacht einen Plugin-Ladefehler. Verwenden Sie stattdessen `api.registerHttpRoute(...)`.
- Plugin-Routen müssen `auth` explizit deklarieren.
- Exakte Konflikte bei `path + match` werden abgelehnt, es sei denn, `replaceExisting: true` ist gesetzt, und ein Plugin kann die Route eines anderen Plugins nicht ersetzen.
- Überlappende Routen mit unterschiedlichen `auth`-Stufen werden abgelehnt. Halten Sie Fallthrough-Ketten mit `exact`/`prefix` nur auf derselben Auth-Stufe.
- Routen mit `auth: "plugin"` erhalten **nicht** automatisch Operator-Laufzeit-Scope. Sie sind für pluginverwaltete Webhooks/Signaturverifizierung gedacht, nicht für privilegierte Gateway-Hilfsaufrufe.
- Routen mit `auth: "gateway"` laufen innerhalb eines Gateway-Anfrage-Laufzeit-Scopes, aber dieser Scope ist absichtlich konservativ:
  - Bearer-Authentifizierung mit gemeinsamem Secret (`gateway.auth.mode = "token"` / `"password"`) hält die Laufzeit-Scopes für Plugin-Routen auf `operator.write` fest, auch wenn der Aufrufer `x-openclaw-scopes` sendet
  - vertrauenswürdige HTTP-Modi mit Identität (zum Beispiel `trusted-proxy` oder `gateway.auth.mode = "none"` bei privatem Ingress) berücksichtigen `x-openclaw-scopes` nur, wenn der Header explizit vorhanden ist
  - wenn `x-openclaw-scopes` bei solchen identitätstragenden Plugin-Routenanfragen fehlt, fällt der Laufzeit-Scope auf `operator.write` zurück
- Praktische Regel: Gehen Sie nicht davon aus, dass eine gateway-auth-Plugin-Route implizit eine Admin-Oberfläche ist. Wenn Ihre Route Verhalten nur für Admins benötigt, verlangen Sie einen identitätstragenden Auth-Modus und dokumentieren Sie den expliziten Header-Vertrag `x-openclaw-scopes`.

## Importpfade des Plugin SDK

Verwenden Sie SDK-Unterpfade statt des monolithischen Imports `openclaw/plugin-sdk`, wenn
Sie Plugins erstellen:

- `openclaw/plugin-sdk/plugin-entry` für Primitiven zur Plugin-Registrierung.
- `openclaw/plugin-sdk/core` für den generischen gemeinsamen pluginseitigen Vertrag.
- `openclaw/plugin-sdk/config-schema` für den Export des Zod-Schemas des
  Root-`openclaw.json` (`OpenClawSchema`).
- Stabile Kanal-Primitiven wie `openclaw/plugin-sdk/channel-setup`,
  `openclaw/plugin-sdk/setup-runtime`,
  `openclaw/plugin-sdk/setup-adapter-runtime`,
  `openclaw/plugin-sdk/setup-tools`,
  `openclaw/plugin-sdk/channel-pairing`,
  `openclaw/plugin-sdk/channel-contract`,
  `openclaw/plugin-sdk/channel-feedback`,
  `openclaw/plugin-sdk/channel-inbound`,
  `openclaw/plugin-sdk/channel-lifecycle`,
  `openclaw/plugin-sdk/channel-reply-pipeline`,
  `openclaw/plugin-sdk/command-auth`,
  `openclaw/plugin-sdk/secret-input` und
  `openclaw/plugin-sdk/webhook-ingress` für gemeinsame Setup-/Auth-/Antwort-/Webhook-
  Verdrahtung. `channel-inbound` ist die gemeinsame Heimat für Debounce, Mention-Matching,
  Hilfsfunktionen für eingehende Mention-Richtlinien, Envelope-Formatierung und Hilfsfunktionen für
  den Kontext eingehender Envelopes.
  `channel-setup` ist die schmale Setup-Seam für optionale Installationen.
  `setup-runtime` ist die laufzeitsichere Setup-Oberfläche, die von `setupEntry` /
  verzögertem Start verwendet wird, einschließlich importsicherer Setup-Patch-Adapter.
  `setup-adapter-runtime` ist die umgebungsbewusste Seam für Account-Setup-Adapter.
  `setup-tools` ist die kleine Hilfs-Seam für CLI/Archiv/Dokumentation (`formatCliCommand`,
  `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`,
  `CONFIG_DIR`).
- Domänen-Unterpfade wie `openclaw/plugin-sdk/channel-config-helpers`,
  `openclaw/plugin-sdk/allow-from`,
  `openclaw/plugin-sdk/channel-config-schema`,
  `openclaw/plugin-sdk/telegram-command-config`,
  `openclaw/plugin-sdk/channel-policy`,
  `openclaw/plugin-sdk/approval-gateway-runtime`,
  `openclaw/plugin-sdk/approval-handler-adapter-runtime`,
  `openclaw/plugin-sdk/approval-handler-runtime`,
  `openclaw/plugin-sdk/approval-runtime`,
  `openclaw/plugin-sdk/config-runtime`,
  `openclaw/plugin-sdk/infra-runtime`,
  `openclaw/plugin-sdk/agent-runtime`,
  `openclaw/plugin-sdk/lazy-runtime`,
  `openclaw/plugin-sdk/reply-history`,
  `openclaw/plugin-sdk/routing`,
  `openclaw/plugin-sdk/status-helpers`,
  `openclaw/plugin-sdk/text-runtime`,
  `openclaw/plugin-sdk/runtime-store` und
  `openclaw/plugin-sdk/directory-runtime` für gemeinsame Laufzeit-/Konfigurations-Hilfsfunktionen.
  `telegram-command-config` ist die schmale öffentliche Seam für die Normalisierung/Validierung benutzerdefinierter
  Telegram-Befehle und bleibt verfügbar, auch wenn die gebündelte
  Telegram-Vertragsoberfläche vorübergehend nicht verfügbar ist.
  `text-runtime` ist die gemeinsame Text-/Markdown-/Logging-Seam, einschließlich
  des Entfernens von für Assistenten sichtbarem Text, Hilfsfunktionen zum Rendern/Chunking von Markdown, Redaktions-
  Hilfsfunktionen, Hilfsfunktionen für Direktiven-Tags und sichere Text-Hilfsfunktionen.
- Kanalspezifische Seams für Freigaben sollten einen einzigen Vertrag `approvalCapability`
  auf dem Plugin bevorzugen. Der Kern liest dann Authentifizierung, Zustellung, Rendering,
  natives Routing und träges natives Handler-Verhalten für Freigaben über diese eine Fähigkeit,
  statt Freigabeverhalten in nicht zusammenhängende Plugin-Felder zu mischen.
- `openclaw/plugin-sdk/channel-runtime` ist veraltet und bleibt nur als
  Kompatibilitäts-Shim für ältere Plugins bestehen. Neuer Code sollte stattdessen die schmaleren
  generischen Primitiven importieren, und Repo-Code sollte keine neuen Importe dieses
  Shims hinzufügen.
- Interna gebündelter Erweiterungen bleiben privat. Externe Plugins sollten nur
  Unterpfade `openclaw/plugin-sdk/*` verwenden. OpenClaw-Kern-/Testcode darf die öffentlichen
  Repo-Einstiegspunkte unter einer Plugin-Paketwurzel wie `index.js`, `api.js`,
  `runtime-api.js`, `setup-entry.js` und eng begrenzte Dateien wie
  `login-qr-api.js` verwenden. Importieren Sie niemals `src/*` eines Plugin-Pakets aus dem Kern oder aus
  einer anderen Erweiterung.
- Aufteilung der Repo-Einstiegspunkte:
  `<plugin-package-root>/api.js` ist das Barrel für Hilfsfunktionen/Typen,
  `<plugin-package-root>/runtime-api.js` ist das Barrel nur für die Laufzeit,
  `<plugin-package-root>/index.js` ist der Einstiegspunkt des gebündelten Plugins
  und `<plugin-package-root>/setup-entry.js` ist der Einstiegspunkt des Setup-Plugins.
- Aktuelle Beispiele für gebündelte Provider:
  - Anthropic verwendet `api.js` / `contract-api.js` für Claude-Stream-Hilfsfunktionen wie
    `wrapAnthropicProviderStream`, Hilfsfunktionen für Beta-Header und das Parsen von `service_tier`.
  - OpenAI verwendet `api.js` für Provider-Builder, Hilfsfunktionen für Standardmodelle und
    Builder für Realtime-Provider.
  - OpenRouter verwendet `api.js` für seinen Provider-Builder sowie Hilfsfunktionen für Onboarding/Konfiguration,
    während `register.runtime.js` weiterhin generische
    Hilfsfunktionen `plugin-sdk/provider-stream` für die repo-lokale Nutzung reexportieren kann.
- Öffentlich verfügbare Einstiegspunkte, die über Fassaden geladen werden, bevorzugen den aktiven Laufzeit-Konfigurations-Snapshot,
  wenn einer vorhanden ist, und fallen dann auf die auf der Festplatte aufgelöste Konfigurationsdatei zurück, wenn
  OpenClaw noch keinen Laufzeit-Snapshot bereitstellt.
- Generische gemeinsame Primitiven bleiben der bevorzugte öffentliche SDK-Vertrag. Eine kleine
  reservierte Kompatibilitätsmenge an Hilfs-Seams mit Branding gebündelter Kanäle existiert weiterhin.
  Behandeln Sie diese als Seams für Pflege/Kompatibilität gebündelter Komponenten, nicht als neue Importziele für Drittanbieter;
  neue kanalübergreifende Verträge sollten weiterhin auf generischen Unterpfaden `plugin-sdk/*` oder in den plugin-lokalen Barrels `api.js` /
  `runtime-api.js` landen.

Kompatibilitätshinweis:

- Vermeiden Sie für neuen Code das Root-Barrel `openclaw/plugin-sdk`.
- Bevorzugen Sie zuerst die schmalen stabilen Primitiven. Die neueren Unterpfade für setup/pairing/reply/
  feedback/contract/inbound/threading/command/secret-input/webhook/infra/
  allowlist/status/message-tool sind der beabsichtigte Vertrag für neue
  gebündelte und externe Plugin-Arbeit.
  Zielparsing/-matching gehört auf `openclaw/plugin-sdk/channel-targets`.
  Gates für Nachrichtenaktionen und Hilfsfunktionen für Reaktions-Nachrichten-IDs gehören auf
  `openclaw/plugin-sdk/channel-actions`.
- Hilfs-Barrels für gebündelte erweiterungsspezifische Komponenten sind standardmäßig nicht stabil. Wenn eine
  Hilfsfunktion nur von einer gebündelten Erweiterung benötigt wird, behalten Sie sie hinter der
  lokalen Seam `api.js` oder `runtime-api.js` der Erweiterung, statt sie nach
  `openclaw/plugin-sdk/<extension>` zu befördern.
- Neue gemeinsam genutzte Hilfs-Seams sollten generisch sein, nicht kanalgebrandet. Gemeinsames Ziel-
  Parsing gehört auf `openclaw/plugin-sdk/channel-targets`; kanalspezifische
  Interna bleiben hinter der lokalen Seam `api.js` oder `runtime-api.js` des besitzenden Plugins.
- Fähigkeitsspezifische Unterpfade wie `image-generation`,
  `media-understanding` und `speech` existieren, weil gebündelte/native Plugins sie
  heute verwenden. Ihre Existenz bedeutet nicht automatisch, dass jede exportierte Hilfsfunktion ein
  langfristig eingefrorener externer Vertrag ist.

## Schemata des Nachrichtentools

Plugins sollten kanalspezifische Schemabeiträge für
`describeMessageTool(...)` besitzen. Behalten Sie providerspezifische Felder im Plugin, nicht im gemeinsamen Kern.

Für gemeinsam nutzbare portable Schemafragmente verwenden Sie die generischen Hilfsfunktionen wieder, die über
`openclaw/plugin-sdk/channel-actions` exportiert werden:

- `createMessageToolButtonsSchema()` für Payloads im Stil eines Button-Rasters
- `createMessageToolCardSchema()` für strukturierte Karten-Payloads

Wenn eine Schemaform nur für einen Provider sinnvoll ist, definieren Sie sie im
eigenen Quellcode dieses Plugins, statt sie in das gemeinsame SDK zu übernehmen.

## Auflösung von Kanalzielen

Kanal-Plugins sollten kanalspezifische Zielsemantik besitzen. Halten Sie den gemeinsamen
ausgehenden Host generisch und verwenden Sie die Oberfläche des Messaging-Adapters für Provider-Regeln:

- `messaging.inferTargetChatType({ to })` entscheidet, ob ein normalisiertes Ziel
  vor der Verzeichnissuche als `direct`, `group` oder `channel` behandelt werden soll.
- `messaging.targetResolver.looksLikeId(raw, normalized)` teilt dem Kern mit, ob eine
  Eingabe direkt zur ID-ähnlichen Auflösung springen soll statt zur Verzeichnissuche.
- `messaging.targetResolver.resolveTarget(...)` ist das Plugin-Fallback, wenn
  der Kern nach der Normalisierung oder nach einem Verzeichnis-Fehlschlag eine endgültige provider-eigene Auflösung braucht.
- `messaging.resolveOutboundSessionRoute(...)` besitzt die providerspezifische Sitzungs-
  Routenbildung, sobald ein Ziel aufgelöst ist.

Empfohlene Aufteilung:

- Verwenden Sie `inferTargetChatType` für Kategorieentscheidungen, die vor der
  Suche nach Peers/Gruppen getroffen werden sollten.
- Verwenden Sie `looksLikeId` für Prüfungen vom Typ „dies als explizite/native Ziel-ID behandeln“.
- Verwenden Sie `resolveTarget` für provider-spezifisches Normalisierungs-Fallback, nicht für eine
  allgemeine Verzeichnissuche.
- Behalten Sie provider-native IDs wie Chat-IDs, Thread-IDs, JIDs, Handles und Raum-IDs
  innerhalb von `target`-Werten oder providerspezifischen Parametern, nicht in generischen SDK-Feldern.

## Konfigurationsgestützte Verzeichnisse

Plugins, die Verzeichniseinträge aus der Konfiguration ableiten, sollten diese Logik im
Plugin behalten und die gemeinsamen Hilfsfunktionen aus
`openclaw/plugin-sdk/directory-runtime` wiederverwenden.

Verwenden Sie dies, wenn ein Kanal konfigurationsgestützte Peers/Gruppen benötigt, wie etwa:

- allowlist-gesteuerte DM-Peers
- konfigurierte Kanal-/Gruppenzuordnungen
- kontobezogene statische Verzeichnis-Fallbacks

Die gemeinsamen Hilfsfunktionen in `directory-runtime` verarbeiten nur generische Operationen:

- Abfragefilterung
- Anwenden von Limits
- Hilfsfunktionen für Deduplizierung/Normalisierung
- Aufbau von `ChannelDirectoryEntry[]`

Kanalspezifische Kontoprüfung und ID-Normalisierung sollten in der
Plugin-Implementierung bleiben.

## Provider-Kataloge

Provider-Plugins können Modellkataloge für Inferenz definieren mit
`registerProvider({ catalog: { run(...) { ... } } })`.

`catalog.run(...)` gibt dieselbe Form zurück, die OpenClaw in
`models.providers` schreibt:

- `{ provider }` für einen Providereintrag
- `{ providers }` für mehrere Providereinträge

Verwenden Sie `catalog`, wenn das Plugin providerspezifische Modell-IDs, Standardwerte für Basis-URLs
oder auth-gesteuerte Modellmetadaten besitzt.

`catalog.order` steuert, wann der Katalog eines Plugins relativ zu den
integrierten impliziten Providern von OpenClaw zusammengeführt wird:

- `simple`: einfache API-Schlüssel- oder umgebungsgetriebene Provider
- `profile`: Provider, die erscheinen, wenn Auth-Profile vorhanden sind
- `paired`: Provider, die mehrere zusammengehörige Providereinträge synthetisieren
- `late`: letzter Durchgang, nach anderen impliziten Providern

Spätere Provider gewinnen bei Schlüsselkollisionen, sodass Plugins absichtlich einen
integrierten Providereintrag mit derselben Provider-ID überschreiben können.

Kompatibilität:

- `discovery` funktioniert weiterhin als Legacy-Alias
- wenn sowohl `catalog` als auch `discovery` registriert sind, verwendet OpenClaw `catalog`

## Schreibgeschützte Kanalinspektion

Wenn Ihr Plugin einen Kanal registriert, sollten Sie bevorzugt
`plugin.config.inspectAccount(cfg, accountId)` neben `resolveAccount(...)` implementieren.

Warum:

- `resolveAccount(...)` ist der Laufzeitpfad. Er darf davon ausgehen, dass Anmeldedaten
  vollständig materialisiert sind, und kann schnell fehlschlagen, wenn erforderliche Secrets fehlen.
- Schreibgeschützte Befehlspfade wie `openclaw status`, `openclaw status --all`,
  `openclaw channels status`, `openclaw channels resolve` und doctor/config-
  Reparaturabläufe sollten keine Laufzeit-Anmeldedaten materialisieren müssen, nur um
  die Konfiguration zu beschreiben.

Empfohlenes Verhalten von `inspectAccount(...)`:

- Geben Sie nur beschreibenden Kontozustand zurück.
- Behalten Sie `enabled` und `configured`.
- Schließen Sie relevante Felder für Quelle/Status von Anmeldedaten ein, zum Beispiel:
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- Sie müssen keine rohen Tokenwerte zurückgeben, nur um die schreibgeschützte
  Verfügbarkeit zu melden. `tokenStatus: "available"` (und das passende Quellfeld)
  reicht für statusartige Befehle aus.
- Verwenden Sie `configured_unavailable`, wenn Anmeldedaten über SecretRef konfiguriert sind, aber
  im aktuellen Befehlspfad nicht verfügbar sind.

Dadurch können schreibgeschützte Befehle „konfiguriert, aber in diesem Befehlspfad nicht verfügbar“
melden, statt abzustürzen oder das Konto fälschlich als nicht konfiguriert zu melden.

## Paket-Packs

Ein Plugin-Verzeichnis kann eine `package.json` mit `openclaw.extensions` enthalten:

```json
{
  "name": "my-pack",
  "openclaw": {
    "extensions": ["./src/safety.ts", "./src/tools.ts"],
    "setupEntry": "./src/setup-entry.ts"
  }
}
```

Jeder Eintrag wird zu einem Plugin. Wenn das Pack mehrere Erweiterungen aufführt, wird die Plugin-ID
zu `name/<fileBase>`.

Wenn Ihr Plugin npm-Abhängigkeiten importiert, installieren Sie sie in diesem Verzeichnis, sodass
`node_modules` verfügbar ist (`npm install` / `pnpm install`).

Sicherheitsleitplanke: Jeder Eintrag in `openclaw.extensions` muss nach der Auflösung von Symlinks innerhalb des Plugin-
Verzeichnisses bleiben. Einträge, die das Paketverzeichnis verlassen, werden
abgelehnt.

Sicherheitshinweis: `openclaw plugins install` installiert Plugin-Abhängigkeiten mit
`npm install --omit=dev --ignore-scripts` (keine Lifecycle-Skripte, keine Dev-Abhängigkeiten zur Laufzeit). Halten Sie die Bäume der Plugin-Abhängigkeiten
„reines JS/TS“ und vermeiden Sie Pakete, die `postinstall`-Builds benötigen.

Optional: `openclaw.setupEntry` kann auf ein leichtgewichtiges Modul nur für das Setup zeigen.
Wenn OpenClaw Setup-Oberflächen für ein deaktiviertes Kanal-Plugin benötigt oder
wenn ein Kanal-Plugin aktiviert, aber noch nicht konfiguriert ist, lädt es `setupEntry`
anstelle des vollständigen Plugin-Einstiegspunkts. Das hält Start und Setup leichter,
wenn Ihr Haupteinstiegspunkt des Plugins zusätzlich Tools, Hooks oder anderen nur zur Laufzeit nötigen
Code verdrahtet.

Optional: `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`
kann ein Kanal-Plugin während der Pre-Listen-Startphase des Gateways in denselben `setupEntry`-Pfad aufnehmen,
selbst wenn der Kanal bereits konfiguriert ist.

Verwenden Sie dies nur, wenn `setupEntry` die Startoberfläche vollständig abdeckt, die vor dem
Beginn des Lauschen des Gateways existieren muss. In der Praxis bedeutet das, dass der Setup-Einstiegspunkt
jede kanal-eigene Fähigkeit registrieren muss, von der der Start abhängt, zum Beispiel:

- die Kanalregistrierung selbst
- alle HTTP-Routen, die verfügbar sein müssen, bevor das Gateway beginnt zu lauschen
- alle Gateway-Methoden, Tools oder Dienste, die in diesem selben Zeitfenster existieren müssen

Wenn Ihr vollständiger Einstiegspunkt weiterhin eine erforderliche Startfähigkeit besitzt, aktivieren Sie
dieses Flag nicht. Behalten Sie das Standardverhalten für das Plugin bei und lassen Sie OpenClaw den
vollständigen Einstiegspunkt während des Starts laden.

Gebündelte Kanäle können auch Hilfsfunktionen für die Vertragoberfläche nur für das Setup veröffentlichen, die der Kern
konsultieren kann, bevor die vollständige Kanal-Laufzeit geladen ist. Die aktuelle Oberfläche für Setup-
Promotion ist:

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

Der Kern verwendet diese Oberfläche, wenn er eine Legacy-Einkonto-Kanal-
Konfiguration nach `channels.<id>.accounts.*` befördern muss, ohne den vollständigen Plugin-Einstiegspunkt zu laden.
Matrix ist das aktuelle gebündelte Beispiel: Es verschiebt nur Auth-/Bootstrap-Schlüssel in ein
benanntes befördertes Konto, wenn bereits benannte Konten existieren, und es kann einen
konfigurierten nicht-kanonischen Standardschlüssel für das Standardkonto beibehalten, statt immer
`accounts.default` zu erzeugen.

Diese Setup-Patch-Adapter halten die Erkennung der Vertragoberfläche gebündelter Komponenten träge. Die Import-
Zeit bleibt leicht; die Promotionsoberfläche wird erst bei der ersten Verwendung geladen, statt den Start
gebündelter Kanäle beim Modulimport erneut zu betreten.

Wenn diese Startoberflächen Gateway-RPC-Methoden enthalten, behalten Sie sie auf einem
pluginspezifischen Präfix. Kern-Admin-Namespaces (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) bleiben reserviert und werden immer
zu `operator.admin` aufgelöst, selbst wenn ein Plugin einen schmaleren Scope anfordert.

Beispiel:

```json
{
  "name": "@scope/my-channel",
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "startup": {
      "deferConfiguredChannelFullLoadUntilAfterListen": true
    }
  }
}
```

### Metadaten des Kanalkatalogs

Kanal-Plugins können Setup-/Erkennungsmetadaten über `openclaw.channel` und
Installationshinweise über `openclaw.install` bekanntgeben. Dadurch bleibt der Kerndatenkatalog frei von Daten.

Beispiel:

```json
{
  "name": "@openclaw/nextcloud-talk",
  "openclaw": {
    "extensions": ["./index.ts"],
    "channel": {
      "id": "nextcloud-talk",
      "label": "Nextcloud Talk",
      "selectionLabel": "Nextcloud Talk (self-hosted)",
      "docsPath": "/channels/nextcloud-talk",
      "docsLabel": "nextcloud-talk",
      "blurb": "Self-hosted chat via Nextcloud Talk webhook bots.",
      "order": 65,
      "aliases": ["nc-talk", "nc"]
    },
    "install": {
      "npmSpec": "@openclaw/nextcloud-talk",
      "localPath": "<bundled-plugin-local-path>",
      "defaultChoice": "npm"
    }
  }
}
```

Nützliche Felder von `openclaw.channel` über das Minimalbeispiel hinaus:

- `detailLabel`: sekundäres Label für umfassendere Katalog-/Statusoberflächen
- `docsLabel`: Linktext für den Dokumentationslink überschreiben
- `preferOver`: IDs von Plugins/Kanälen mit niedrigerer Priorität, die dieser Katalogeintrag übertreffen soll
- `selectionDocsPrefix`, `selectionDocsOmitLabel`, `selectionExtras`: Steuerelemente für Text auf Auswahloberflächen
- `markdownCapable`: markiert den Kanal als Markdown-fähig für Entscheidungen zur ausgehenden Formatierung
- `exposure.configured`: blendet den Kanal in Oberflächen zur Auflistung konfigurierter Kanäle aus, wenn auf `false` gesetzt
- `exposure.setup`: blendet den Kanal in interaktiven Setup-/Konfigurations-Auswahllisten aus, wenn auf `false` gesetzt
- `exposure.docs`: markiert den Kanal für Oberflächen der Dokumentationsnavigation als intern/privat
- `showConfigured` / `showInSetup`: Legacy-Aliasse werden aus Kompatibilitätsgründen weiterhin akzeptiert; bevorzugen Sie `exposure`
- `quickstartAllowFrom`: nimmt den Kanal in den standardmäßigen Quickstart-Flow `allowFrom` auf
- `forceAccountBinding`: erzwingt explizite Kontobindung, selbst wenn nur ein Konto existiert
- `preferSessionLookupForAnnounceTarget`: bevorzugt die Sitzungssuche beim Auflösen von Ankündigungszielen

OpenClaw kann auch **externe Kanalkataloge** zusammenführen (zum Beispiel einen Export einer MPM-
Registry). Legen Sie eine JSON-Datei an einem der folgenden Orte ab:

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

Oder verweisen Sie mit `OPENCLAW_PLUGIN_CATALOG_PATHS` (oder `OPENCLAW_MPM_CATALOG_PATHS`) auf
eine oder mehrere JSON-Dateien (durch Komma/Semikolon/`PATH` getrennt). Jede Datei sollte
`{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }` enthalten. Der Parser akzeptiert außerdem `"packages"` oder `"plugins"` als Legacy-Aliasse für den Schlüssel `"entries"`.

## Plugins für die Kontext-Engine

Plugins für die Kontext-Engine besitzen die Orchestrierung des Sitzungskontexts für Ingest, Zusammenstellung
und Kompaktierung. Registrieren Sie sie in Ihrem Plugin mit
`api.registerContextEngine(id, factory)` und wählen Sie dann die aktive Engine mit
`plugins.slots.contextEngine` aus.

Verwenden Sie dies, wenn Ihr Plugin die Standard-Kontext-
Pipeline ersetzen oder erweitern muss, statt nur Erinnerungssuche oder Hooks hinzuzufügen.

```ts
import { buildMemorySystemPromptAddition } from "openclaw/plugin-sdk/core";

export default function (api) {
  api.registerContextEngine("lossless-claw", () => ({
    info: { id: "lossless-claw", name: "Lossless Claw", ownsCompaction: true },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages, availableTools, citationsMode }) {
      return {
        messages,
        estimatedTokens: 0,
        systemPromptAddition: buildMemorySystemPromptAddition({
          availableTools: availableTools ?? new Set(),
          citationsMode,
        }),
      };
    },
    async compact() {
      return { ok: true, compacted: false };
    },
  }));
}
```

Wenn Ihre Engine den Kompaktierungsalgorithmus **nicht** besitzt, behalten Sie `compact()`
implementiert und delegieren Sie ihn explizit:

```ts
import {
  buildMemorySystemPromptAddition,
  delegateCompactionToRuntime,
} from "openclaw/plugin-sdk/core";

export default function (api) {
  api.registerContextEngine("my-memory-engine", () => ({
    info: {
      id: "my-memory-engine",
      name: "My Memory Engine",
      ownsCompaction: false,
    },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages, availableTools, citationsMode }) {
      return {
        messages,
        estimatedTokens: 0,
        systemPromptAddition: buildMemorySystemPromptAddition({
          availableTools: availableTools ?? new Set(),
          citationsMode,
        }),
      };
    },
    async compact(params) {
      return await delegateCompactionToRuntime(params);
    },
  }));
}
```

## Eine neue Fähigkeit hinzufügen

Wenn ein Plugin Verhalten benötigt, das nicht in die aktuelle API passt, umgehen Sie
das Plugin-System nicht mit einem privaten Zugriff. Fügen Sie die fehlende Fähigkeit hinzu.

Empfohlene Reihenfolge:

1. den Kernvertrag definieren
   Entscheiden Sie, welches gemeinsame Verhalten der Kern besitzen soll: Richtlinie, Fallback, Zusammenführung von Konfigurationen,
   Lebenszyklus, kanalseitige Semantik und Form der Laufzeit-Hilfsfunktion.
2. typisierte Oberflächen für Plugin-Registrierung/Laufzeit hinzufügen
   Erweitern Sie `OpenClawPluginApi` und/oder `api.runtime` um die kleinste sinnvolle
   typisierte Fähigkeitsoberfläche.
3. Kern + Kanal-/Feature-Konsumenten anbinden
   Kanäle und Feature-Plugins sollten die neue Fähigkeit über den Kern nutzen,
   nicht durch direktes Importieren einer Anbieterimplementierung.
4. Anbieterimplementierungen registrieren
   Anbieter-Plugins registrieren dann ihre Backends für diese Fähigkeit.
5. Vertragsabdeckung hinzufügen
   Fügen Sie Tests hinzu, damit Eigentümerschaft und Registrierungsform über die Zeit explizit bleiben.

So bleibt OpenClaw meinungsstark, ohne fest auf das Weltbild eines einzelnen
Providers codiert zu werden. Ein konkretes Datei-Checklisten- und Beispiel finden Sie im [Capability Cookbook](/de/plugins/architecture).

### Checkliste für Fähigkeiten

Wenn Sie eine neue Fähigkeit hinzufügen, sollte die Implementierung normalerweise diese
Oberflächen gemeinsam berühren:

- Kernvertragstypen in `src/<capability>/types.ts`
- Kern-Runner/Laufzeit-Hilfsfunktion in `src/<capability>/runtime.ts`
- Plugin-API-Registrierungsoberfläche in `src/plugins/types.ts`
- Plugin-Registry-Verdrahtung in `src/plugins/registry.ts`
- Plugin-Laufzeitfreigabe in `src/plugins/runtime/*`, wenn Feature-/Kanal-
  Plugins sie nutzen müssen
- Erfassungs-/Test-Hilfsfunktionen in `src/test-utils/plugin-registration.ts`
- Assertions zu Eigentümerschaft/Verträgen in `src/plugins/contracts/registry.ts`
- Operator-/Plugin-Dokumentation in `docs/`

Wenn eine dieser Oberflächen fehlt, ist das normalerweise ein Zeichen dafür, dass die Fähigkeit
noch nicht vollständig integriert ist.

### Vorlage für Fähigkeiten

Minimales Muster:

```ts
// core contract
export type VideoGenerationProviderPlugin = {
  id: string;
  label: string;
  generateVideo: (req: VideoGenerationRequest) => Promise<VideoGenerationResult>;
};

// plugin API
api.registerVideoGenerationProvider({
  id: "openai",
  label: "OpenAI",
  async generateVideo(req) {
    return await generateOpenAiVideo(req);
  },
});

// shared runtime helper for feature/channel plugins
const clip = await api.runtime.videoGeneration.generate({
  prompt: "Show the robot walking through the lab.",
  cfg,
});
```

Muster für Vertragstests:

```ts
expect(findVideoGenerationProviderIdsForPlugin("openai")).toEqual(["openai"]);
```

Damit bleibt die Regel einfach:

- der Kern besitzt den Fähigkeitsvertrag + die Orchestrierung
- Anbieter-Plugins besitzen Anbieterimplementierungen
- Feature-/Kanal-Plugins nutzen Laufzeit-Hilfsfunktionen
- Vertragstests halten Eigentümerschaft explizit
