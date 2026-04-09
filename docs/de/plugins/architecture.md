---
read_when:
    - Sie erstellen oder debuggen native OpenClaw-Plugins
    - Sie möchten das Plugin-Fähigkeitsmodell oder Ownership-Grenzen verstehen
    - Sie arbeiten an der Plugin-Ladepipeline oder Registry
    - Sie implementieren Provider-Laufzeit-Hooks oder Kanal-Plugins
sidebarTitle: Internals
summary: 'Plugin-Interna: Fähigkeitsmodell, Ownership, Verträge, Ladepipeline und Laufzeit-Helfer'
title: Plugin-Interna
x-i18n:
    generated_at: "2026-04-09T01:31:44Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2575791f835990589219bb06d8ca92e16a8c38b317f0bfe50b421682f253ef18
    source_path: plugins/architecture.md
    workflow: 15
---

# Plugin-Interna

<Info>
  Dies ist die **Referenz für die tiefgehende Architektur**. Praktische Anleitungen finden Sie hier:
  - [Plugins installieren und verwenden](/de/tools/plugin) — Benutzerleitfaden
  - [Erste Schritte](/de/plugins/building-plugins) — erstes Plugin-Tutorial
  - [Kanal-Plugins](/de/plugins/sdk-channel-plugins) — einen Messaging-Kanal erstellen
  - [Provider-Plugins](/de/plugins/sdk-provider-plugins) — einen Modellanbieter erstellen
  - [SDK-Überblick](/de/plugins/sdk-overview) — Importzuordnung und Registrierungs-API
</Info>

Diese Seite behandelt die interne Architektur des OpenClaw-Plugin-Systems.

## Öffentliches Fähigkeitsmodell

Fähigkeiten sind das öffentliche Modell für **native Plugins** innerhalb von OpenClaw. Jedes
native OpenClaw-Plugin registriert sich für einen oder mehrere Fähigkeitstypen:

| Fähigkeit              | Registrierungsmethode                           | Beispiel-Plugins                     |
| ---------------------- | ------------------------------------------------ | ------------------------------------ |
| Textinferenz           | `api.registerProvider(...)`                      | `openai`, `anthropic`                |
| CLI-Inferenz-Backend   | `api.registerCliBackend(...)`                    | `openai`, `anthropic`                |
| Sprache                | `api.registerSpeechProvider(...)`                | `elevenlabs`, `microsoft`            |
| Echtzeit-Transkription | `api.registerRealtimeTranscriptionProvider(...)` | `openai`                             |
| Echtzeit-Sprache       | `api.registerRealtimeVoiceProvider(...)`         | `openai`                             |
| Medienverständnis      | `api.registerMediaUnderstandingProvider(...)`    | `openai`, `google`                   |
| Bildgenerierung        | `api.registerImageGenerationProvider(...)`       | `openai`, `google`, `fal`, `minimax` |
| Musikgenerierung       | `api.registerMusicGenerationProvider(...)`       | `google`, `minimax`                  |
| Videogenerierung       | `api.registerVideoGenerationProvider(...)`       | `qwen`                               |
| Web-Abruf              | `api.registerWebFetchProvider(...)`              | `firecrawl`                          |
| Websuche               | `api.registerWebSearchProvider(...)`             | `google`                             |
| Kanal / Messaging      | `api.registerChannel(...)`                       | `msteams`, `matrix`                  |

Ein Plugin, das null Fähigkeiten registriert, aber Hooks, Tools oder
Services bereitstellt, ist ein **Legacy-Hook-only**-Plugin. Dieses Muster wird weiterhin vollständig unterstützt.

### Haltung zur externen Kompatibilität

Das Fähigkeitsmodell ist im Kernsystem eingeführt und wird heute von gebündelten/nativen Plugins
verwendet, aber für die Kompatibilität externer Plugins braucht es weiterhin eine strengere Messlatte als „es ist
exportiert, also ist es eingefroren“.

Aktuelle Richtlinien:

- **bestehende externe Plugins:** halten Sie hook-basierte Integrationen funktionsfähig; behandeln Sie
  dies als Kompatibilitäts-Basislinie
- **neue gebündelte/native Plugins:** bevorzugen Sie explizite Fähigkeitsregistrierung statt
  anbieterspezifischer Eingriffe oder neuer Hook-only-Designs
- **externe Plugins, die Fähigkeitsregistrierung übernehmen:** erlaubt, aber behandeln Sie
  fähigkeitsspezifische Helferoberflächen als weiterentwickelbar, sofern die Dokumentation einen
  Vertrag nicht ausdrücklich als stabil kennzeichnet

Praktische Regel:

- APIs zur Fähigkeitsregistrierung sind die vorgesehene Richtung
- Legacy-Hooks bleiben während des
  Übergangs der sicherste Weg ohne Inkompatibilitäten für externe Plugins
- exportierte Helper-Subpaths sind nicht alle gleich; bevorzugen Sie den schmalen dokumentierten
  Vertrag, nicht beiläufig exportierte Helfer

### Plugin-Formen

OpenClaw klassifiziert jedes geladene Plugin anhand seines tatsächlichen
Registrierungsverhaltens in eine Form (nicht nur anhand statischer Metadaten):

- **plain-capability** -- registriert genau einen Fähigkeitstyp (zum Beispiel ein
  reines Provider-Plugin wie `mistral`)
- **hybrid-capability** -- registriert mehrere Fähigkeitstypen (zum Beispiel
  `openai` besitzt Textinferenz, Sprache, Medienverständnis und Bild-
  generierung)
- **hook-only** -- registriert nur Hooks (typisiert oder benutzerdefiniert), keine Fähigkeiten,
  Tools, Befehle oder Services
- **non-capability** -- registriert Tools, Befehle, Services oder Routen, aber keine
  Fähigkeiten

Verwenden Sie `openclaw plugins inspect <id>`, um die Form und die Aufschlüsselung der
Fähigkeiten eines Plugins anzuzeigen. Details finden Sie in der [CLI-Referenz](/cli/plugins#inspect).

### Legacy-Hooks

Der Hook `before_agent_start` bleibt als Kompatibilitätspfad für
Hook-only-Plugins unterstützt. Bestehende Plugins aus der Praxis hängen weiterhin davon ab.

Ausrichtung:

- funktionsfähig halten
- als Legacy dokumentieren
- `before_model_resolve` für Arbeiten an Modell-/Provider-Überschreibungen bevorzugen
- `before_prompt_build` für Arbeiten an Prompt-Mutationen bevorzugen
- erst entfernen, wenn die reale Nutzung sinkt und die Abdeckung durch Fixtures eine sichere Migration belegt

### Kompatibilitätssignale

Wenn Sie `openclaw doctor` oder `openclaw plugins inspect <id>` ausführen, sehen Sie möglicherweise
eines dieser Labels:

| Signal                     | Bedeutung                                                  |
| -------------------------- | ---------------------------------------------------------- |
| **config valid**           | Konfiguration wird korrekt geparst und Plugins werden aufgelöst |
| **compatibility advisory** | Plugin verwendet ein unterstütztes, aber älteres Muster (z. B. `hook-only`) |
| **legacy warning**         | Plugin verwendet `before_agent_start`, das veraltet ist    |
| **hard error**             | Konfiguration ist ungültig oder Plugin konnte nicht geladen werden |

Weder `hook-only` noch `before_agent_start` machen Ihr Plugin heute kaputt --
`hook-only` ist ein Hinweis, und `before_agent_start` löst nur eine Warnung aus. Diese
Signale erscheinen auch in `openclaw status --all` und `openclaw plugins doctor`.

## Architekturüberblick

Das Plugin-System von OpenClaw hat vier Ebenen:

1. **Manifest + Discovery**
   OpenClaw findet potenzielle Plugins aus konfigurierten Pfaden, Workspace-Wurzeln,
   globalen Extension-Wurzeln und gebündelten Extensions. Discovery liest zuerst native
   `openclaw.plugin.json`-Manifeste sowie unterstützte Bundle-Manifeste.
2. **Aktivierung + Validierung**
   Der Kern entscheidet, ob ein entdecktes Plugin aktiviert, deaktiviert, blockiert oder
   für einen exklusiven Slot wie Speicher ausgewählt wird.
3. **Laufzeitladen**
   Native OpenClaw-Plugins werden über jiti im Prozess geladen und registrieren
   Fähigkeiten in einer zentralen Registry. Kompatible Bundles werden in
   Registry-Einträge normalisiert, ohne Laufzeitcode zu importieren.
4. **Oberflächennutzung**
   Der Rest von OpenClaw liest die Registry, um Tools, Kanäle, Provider-
   Einrichtung, Hooks, HTTP-Routen, CLI-Befehle und Services bereitzustellen.

Speziell für die Plugin-CLI ist die Erkennung von Root-Befehlen in zwei Phasen aufgeteilt:

- Parse-Zeit-Metadaten kommen aus `registerCli(..., { descriptors: [...] })`
- das eigentliche Plugin-CLI-Modul kann lazy bleiben und sich erst beim ersten Aufruf registrieren

Dadurch bleibt die dem Plugin gehörende CLI im Plugin, während OpenClaw dennoch
Root-Befehlsnamen vor dem Parsen reservieren kann.

Die wichtige Designgrenze:

- Discovery + Konfigurationsvalidierung sollten anhand von **Manifest-/Schema-Metadaten**
  funktionieren, ohne Plugin-Code auszuführen
- natives Laufzeitverhalten kommt aus dem Pfad `register(api)` des Plugin-Moduls

Diese Trennung ermöglicht OpenClaw, Konfigurationen zu validieren, fehlende/deaktivierte Plugins
zu erklären und UI-/Schema-Hinweise zu erzeugen, bevor die vollständige Laufzeit aktiv ist.

### Kanal-Plugins und das gemeinsame `message`-Tool

Kanal-Plugins müssen für normale Chat-Aktionen kein separates Tool zum Senden/Bearbeiten/Reagieren registrieren.
OpenClaw behält ein gemeinsames `message`-Tool im Kern, und
Kanal-Plugins besitzen die kanalspezifische Discovery und Ausführung dahinter.

Die aktuelle Grenze ist:

- der Kern besitzt den gemeinsamen `message`-Tool-Host, Prompt-Verdrahtung, Sitzungs-/Thread-
  Buchführung und Ausführungs-Dispatch
- Kanal-Plugins besitzen Scoped-Action-Discovery, Fähigkeits-Discovery und beliebige
  kanalspezifische Schemafragmente
- Kanal-Plugins besitzen anbieterspezifische Sitzungs-/Unterhaltungsgrammatik, etwa
  wie Unterhaltungs-IDs Thread-IDs kodieren oder von Elternunterhaltungen erben
- Kanal-Plugins führen die endgültige Aktion über ihren Action-Adapter aus

Für Kanal-Plugins ist die SDK-Oberfläche
`ChannelMessageActionAdapter.describeMessageTool(...)`. Dieser einheitliche Discovery-
Aufruf erlaubt es einem Plugin, seine sichtbaren Aktionen, Fähigkeiten und Schema-
Beiträge zusammen zurückzugeben, damit diese Teile nicht auseinanderdriften.

Der Kern übergibt den Laufzeitkontext in diesen Discovery-Schritt. Wichtige Felder sind:

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- vertrauenswürdige eingehende `requesterSenderId`

Das ist für kontextsensitive Plugins wichtig. Ein Kanal kann
Nachrichtenaktionen abhängig vom aktiven Konto, dem aktuellen Raum/Thread/der aktuellen Nachricht oder
der vertrauenswürdigen Anforderer-Identität ein- oder ausblenden, ohne
kanalspezifische Verzweigungen im Kern-`message`-Tool fest zu verdrahten.

Deshalb sind Änderungen am Embedded-Runner-Routing weiterhin Plugin-Arbeit: Der Runner ist
dafür verantwortlich, die aktuelle Chat-/Sitzungsidentität in die Plugin-
Discovery-Grenze weiterzuleiten, damit das gemeinsame `message`-Tool die richtige, dem Kanal gehörende
Oberfläche für den aktuellen Turn bereitstellt.

Für kanaleigene Ausführungshelfer sollten gebündelte Plugins die Ausführungs-
Laufzeit innerhalb ihrer eigenen Extension-Module behalten. Der Kern besitzt nicht mehr die Laufzeiten
für Discord-, Slack-, Telegram- oder WhatsApp-Nachrichtenaktionen unter `src/agents/tools`.
Wir veröffentlichen keine separaten `plugin-sdk/*-action-runtime`-Subpaths, und gebündelte
Plugins sollten ihren eigenen lokalen Laufzeitcode direkt aus ihren
Extension-eigenen Modulen importieren.

Dieselbe Grenze gilt allgemein für providerbenannte SDK-Seams: Der Kern sollte
keine kanalspezifischen Convenience-Barrels für Slack, Discord, Signal,
WhatsApp oder ähnliche Extensions importieren. Wenn der Kern ein Verhalten benötigt, dann entweder
über das eigene Barrel `api.ts` / `runtime-api.ts` des gebündelten Plugins oder durch Anheben
dieses Bedarfs in eine schmale generische Fähigkeit im gemeinsamen SDK.

Speziell für Umfragen gibt es zwei Ausführungspfade:

- `outbound.sendPoll` ist die gemeinsame Basis für Kanäle, die zum gemeinsamen
  Umfragemodell passen
- `actions.handleAction("poll")` ist der bevorzugte Pfad für kanalspezifische
  Umfragesemantik oder zusätzliche Umfrageparameter

Der Kern verschiebt das gemeinsame Umfrage-Parsing jetzt so lange, bis der
Plugin-Umfrage-Dispatch die Aktion ablehnt, damit plugin-eigene Umfrage-Handler
kanalspezifische Umfragefelder akzeptieren können, ohne zuerst vom generischen
Umfrage-Parser blockiert zu werden.

Die vollständige Startsequenz finden Sie unter [Ladepipeline](#load-pipeline).

## Ownership-Modell für Fähigkeiten

OpenClaw behandelt ein natives Plugin als Ownership-Grenze für ein **Unternehmen** oder ein
**Feature**, nicht als Sammelsurium unabhängiger Integrationen.

Das bedeutet:

- ein Unternehmens-Plugin sollte normalerweise alle OpenClaw-seitigen
  Oberflächen dieses Unternehmens besitzen
- ein Feature-Plugin sollte normalerweise die gesamte von ihm eingeführte Feature-Oberfläche besitzen
- Kanäle sollten gemeinsame Kernfähigkeiten konsumieren, statt Provider-Verhalten ad hoc
  neu zu implementieren

Beispiele:

- das gebündelte Plugin `openai` besitzt das OpenAI-Modellprovider-Verhalten und OpenAI-
  Verhalten für Sprache + Echtzeit-Sprache + Medienverständnis + Bildgenerierung
- das gebündelte Plugin `elevenlabs` besitzt das ElevenLabs-Sprachverhalten
- das gebündelte Plugin `microsoft` besitzt das Microsoft-Sprachverhalten
- das gebündelte Plugin `google` besitzt das Google-Modellprovider-Verhalten sowie Google-
  Verhalten für Medienverständnis + Bildgenerierung + Websuche
- das gebündelte Plugin `firecrawl` besitzt das Firecrawl-Web-Abruf-Verhalten
- die gebündelten Plugins `minimax`, `mistral`, `moonshot` und `zai` besitzen ihre
  Backends für Medienverständnis
- das Plugin `voice-call` ist ein Feature-Plugin: Es besitzt Anruftransport, Tools,
  CLI, Routen und Twilio-Medienstrom-Bridging, nutzt aber gemeinsame Sprach- sowie
  Echtzeit-Transkriptions- und Echtzeit-Sprach-Fähigkeiten, statt Anbieter-Plugins direkt
  zu importieren

Der angestrebte Endzustand ist:

- OpenAI lebt in einem Plugin, auch wenn es Textmodelle, Sprache, Bilder und
  künftig Video umfasst
- ein anderer Anbieter kann dasselbe für seinen eigenen Oberflächenbereich tun
- Kanäle ist es egal, welches Anbieter-Plugin den Provider besitzt; sie konsumieren den
  gemeinsamen Fähigkeitsvertrag, den der Kern bereitstellt

Das ist die zentrale Unterscheidung:

- **Plugin** = Ownership-Grenze
- **Fähigkeit** = Kernvertrag, den mehrere Plugins implementieren oder konsumieren können

Wenn OpenClaw also eine neue Domäne wie Video hinzufügt, ist die erste Frage nicht
„welcher Provider sollte die Videoverarbeitung fest einkodieren?“ Die erste Frage lautet „wie sieht
der Kernvertrag für die Videofähigkeit aus?“ Sobald dieser Vertrag existiert, können sich Anbieter-
Plugins dagegen registrieren und Kanal-/Feature-Plugins ihn konsumieren.

Wenn die Fähigkeit noch nicht existiert, ist der richtige Weg in der Regel:

1. die fehlende Fähigkeit im Kern definieren
2. sie typisiert über die Plugin-API/Laufzeit verfügbar machen
3. Kanäle/Features gegen diese Fähigkeit verdrahten
4. Anbieter-Plugins Implementierungen registrieren lassen

So bleibt Ownership explizit, ohne Kernverhalten zu schaffen, das von
einem einzelnen Anbieter oder einem einmaligen plugin-spezifischen Codepfad abhängt.

### Schichtung von Fähigkeiten

Verwenden Sie dieses mentale Modell, um zu entscheiden, wohin Code gehört:

- **Kern-Fähigkeitsschicht**: gemeinsame Orchestrierung, Richtlinien, Fallback, Konfigurations-
  Merge-Regeln, Bereitstellungssemantik und typisierte Verträge
- **Anbieter-Plugin-Schicht**: anbieterspezifische APIs, Authentifizierung, Modellkataloge, Sprach-
  synthese, Bildgenerierung, zukünftige Video-Backends, Nutzungsendpunkte
- **Kanal-/Feature-Plugin-Schicht**: Slack/Discord/voice-call/etc.-Integration,
  die Kernfähigkeiten konsumiert und auf einer Oberfläche präsentiert

Zum Beispiel folgt TTS dieser Form:

- der Kern besitzt TTS-Richtlinien zur Antwortzeit, Fallback-Reihenfolge, Präferenzen und Kanalzustellung
- `openai`, `elevenlabs` und `microsoft` besitzen Syntheseimplementierungen
- `voice-call` konsumiert den Laufzeithelfer für Telefonie-TTS

Dasselbe Muster sollte für zukünftige Fähigkeiten bevorzugt werden.

### Beispiel für ein Unternehmens-Plugin mit mehreren Fähigkeiten

Ein Unternehmens-Plugin sollte sich von außen kohärent anfühlen. Wenn OpenClaw gemeinsame
Verträge für Modelle, Sprache, Echtzeit-Transkription, Echtzeit-Sprache, Medien-
verständnis, Bildgenerierung, Videogenerierung, Web-Abruf und Websuche hat,
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

Entscheidend sind nicht die exakten Helper-Namen. Entscheidend ist die Form:

- ein Plugin besitzt die Anbieteroberfläche
- der Kern besitzt weiterhin die Fähigkeitsverträge
- Kanäle und Feature-Plugins konsumieren `api.runtime.*`-Helfer, nicht Anbieter-Code
- Vertragstests können prüfen, dass das Plugin die Fähigkeiten registriert hat, die es
  laut eigener Angabe besitzt

### Fähigkeitsbeispiel: Videoverständnis

OpenClaw behandelt Bild-/Audio-/Videoverständnis bereits als eine gemeinsame
Fähigkeit. Dasselbe Ownership-Modell gilt auch hier:

1. der Kern definiert den Vertrag für Medienverständnis
2. Anbieter-Plugins registrieren je nach Bedarf `describeImage`, `transcribeAudio` und
   `describeVideo`
3. Kanal- und Feature-Plugins konsumieren das gemeinsame Kernverhalten, statt
   direkt mit Anbieter-Code verdrahtet zu sein

Dadurch wird vermieden, die Video-Annahmen eines einzelnen Providers in den Kern einzubacken. Das Plugin besitzt
die Anbieteroberfläche; der Kern besitzt den Fähigkeitsvertrag und das Fallback-Verhalten.

Die Videogenerierung folgt bereits derselben Sequenz: Der Kern besitzt den typisierten
Fähigkeitsvertrag und den Laufzeithelfer, und Anbieter-Plugins registrieren
`api.registerVideoGenerationProvider(...)`-Implementierungen dagegen.

Sie brauchen eine konkrete Checkliste für die Einführung? Siehe
[Capability Cookbook](/de/plugins/architecture).

## Verträge und Durchsetzung

Die Oberfläche der Plugin-API ist absichtlich typisiert und in
`OpenClawPluginApi` zentralisiert. Dieser Vertrag definiert die unterstützten Registrierungspunkte und
die Laufzeit-Helfer, auf die sich ein Plugin verlassen darf.

Warum das wichtig ist:

- Plugin-Autorinnen und -Autoren erhalten einen stabilen internen Standard
- der Kern kann doppelte Ownership ablehnen, etwa wenn zwei Plugins dieselbe
  Provider-ID registrieren
- beim Start können verwertbare Diagnosen für fehlerhafte Registrierungen ausgegeben werden
- Vertragstests können die Ownership gebündelter Plugins durchsetzen und stilles Driften verhindern

Es gibt zwei Ebenen der Durchsetzung:

1. **Durchsetzung bei der Laufzeitregistrierung**
   Die Plugin-Registry validiert Registrierungen während Plugins geladen werden. Beispiele:
   doppelte Provider-IDs, doppelte Speech-Provider-IDs und fehlerhafte
   Registrierungen erzeugen Plugin-Diagnosen statt undefiniertem Verhalten.
2. **Vertragstests**
   Gebündelte Plugins werden in Vertrag-Registries während Testläufen erfasst, damit
   OpenClaw Ownership explizit prüfen kann. Heute wird dies für Modell-
   provider, Speech-Provider, Websuch-Provider und die Ownership gebündelter Registrierungen verwendet.

Der praktische Effekt ist, dass OpenClaw von Anfang an weiß, welches Plugin welche
Oberfläche besitzt. Dadurch können Kern und Kanäle nahtlos zusammenspielen, weil Ownership
deklariert, typisiert und testbar ist statt implizit.

### Was in einen Vertrag gehört

Gute Plugin-Verträge sind:

- typisiert
- klein
- fähigkeitsspezifisch
- im Besitz des Kerns
- von mehreren Plugins wiederverwendbar
- von Kanälen/Features ohne Anbieterwissen konsumierbar

Schlechte Plugin-Verträge sind:

- im Kern versteckte anbieterspezifische Richtlinien
- einmalige Plugin-Escape-Hatches, die die Registry umgehen
- Kanal-Code, der direkt in eine Anbieterimplementierung greift
- ad hoc erzeugte Laufzeitobjekte, die nicht Teil von `OpenClawPluginApi` oder
  `api.runtime` sind

Wenn Sie unsicher sind, heben Sie die Abstraktionsebene an: Definieren Sie zuerst die Fähigkeit und
lassen Sie dann Plugins daran andocken.

## Ausführungsmodell

Native OpenClaw-Plugins laufen **im Prozess** mit dem Gateway. Sie sind nicht
sandboxed. Ein geladenes natives Plugin hat dieselbe Vertrauen-Grenze auf Prozessebene wie
Kerncode.

Auswirkungen:

- ein natives Plugin kann Tools, Netzwerk-Handler, Hooks und Services registrieren
- ein Fehler in einem nativen Plugin kann das Gateway zum Absturz bringen oder destabilisieren
- ein bösartiges natives Plugin ist gleichbedeutend mit beliebiger Codeausführung innerhalb
  des OpenClaw-Prozesses

Kompatible Bundles sind standardmäßig sicherer, weil OpenClaw sie derzeit
als Metadaten-/Content-Pakete behandelt. In aktuellen Releases bedeutet das meist
gebündelte Skills.

Verwenden Sie Allowlists und explizite Installations-/Ladepfade für nicht gebündelte Plugins. Behandeln Sie
Workspace-Plugins als Entwicklungszeit-Code, nicht als Produktionsstandard.

Bei gebündelten Workspace-Paketnamen sollte die Plugin-ID im npm-
Namen verankert bleiben: standardmäßig `@openclaw/<id>` oder ein genehmigtes typisiertes Suffix wie
`-provider`, `-plugin`, `-speech`, `-sandbox` oder `-media-understanding`, wenn
das Paket absichtlich eine engere Plugin-Rolle bereitstellt.

Wichtiger Vertrauenshinweis:

- `plugins.allow` vertraut **Plugin-IDs**, nicht der Herkunft der Quelle.
- Ein Workspace-Plugin mit derselben ID wie ein gebündeltes Plugin überschattet
  absichtlich die gebündelte Kopie, wenn dieses Workspace-Plugin aktiviert/allowlisted ist.
- Das ist normal und nützlich für lokale Entwicklung, Patch-Tests und Hotfixes.

## Exportgrenze

OpenClaw exportiert Fähigkeiten, keine Implementierungs-Convenience.

Halten Sie Fähigkeitsregistrierungen öffentlich. Reduzieren Sie nicht-vertragliche Helper-Exporte:

- gebündelte plugin-spezifische Helper-Subpaths
- Laufzeit-Plumbing-Subpaths, die nicht als öffentliche API gedacht sind
- anbieterspezifische Convenience-Helper
- Setup-/Onboarding-Helfer, die Implementierungsdetails sind

Einige Helper-Subpaths gebündelter Plugins verbleiben aus Kompatibilitäts- und Wartungsgründen
weiterhin in der generierten SDK-Exportzuordnung. Aktuelle Beispiele sind
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` und mehrere `plugin-sdk/matrix*`-Seams. Behandeln Sie diese als
reservierte Exporte für Implementierungsdetails, nicht als empfohlenes SDK-Muster für
neue Drittanbieter-Plugins.

## Ladepipeline

Beim Start macht OpenClaw grob Folgendes:

1. potenzielle Plugin-Wurzeln entdecken
2. native oder kompatible Bundle-Manifeste und Paketmetadaten lesen
3. unsichere Kandidaten ablehnen
4. Plugin-Konfiguration normalisieren (`plugins.enabled`, `allow`, `deny`, `entries`,
   `slots`, `load.paths`)
5. Aktivierung für jeden Kandidaten entscheiden
6. aktivierte native Module per jiti laden
7. native Hooks `register(api)` (oder `activate(api)` — ein Legacy-Alias) aufrufen und Registrierungen in die Plugin-Registry einsammeln
8. die Registry für Befehle/Laufzeitoberflächen bereitstellen

<Note>
`activate` ist ein Legacy-Alias für `register` — der Loader löst auf, was vorhanden ist (`def.register ?? def.activate`), und ruft es an derselben Stelle auf. Alle gebündelten Plugins verwenden `register`; bevorzugen Sie `register` für neue Plugins.
</Note>

Die Sicherheitsprüfungen erfolgen **vor** der Laufzeitausführung. Kandidaten werden blockiert,
wenn der Einstiegspunkt die Plugin-Wurzel verlässt, der Pfad weltweit beschreibbar ist oder die Pfad-
Ownership bei nicht gebündelten Plugins verdächtig aussieht.

### Manifest-first-Verhalten

Das Manifest ist die Quelle der Wahrheit auf der Control-Plane. OpenClaw verwendet es, um:

- das Plugin zu identifizieren
- deklarierte Kanäle/Skills/Konfigurationsschema oder Bundle-Fähigkeiten zu entdecken
- `plugins.entries.<id>.config` zu validieren
- Labels/Platzhalter in der Control UI zu ergänzen
- Installations-/Katalogmetadaten anzuzeigen

Für native Plugins ist das Laufzeitmodul der Data-Plane-Teil. Es registriert
tatsächliches Verhalten wie Hooks, Tools, Befehle oder Provider-Flows.

### Was der Loader cached

OpenClaw hält kurze In-Process-Caches für:

- Discovery-Ergebnisse
- Daten der Manifest-Registry
- geladene Plugin-Registries

Diese Caches reduzieren burstartige Starts und den Overhead wiederholter Befehle. Man kann sie
als kurzlebige Performance-Caches betrachten, nicht als Persistenz.

Leistungshinweis:

- Setzen Sie `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` oder
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1`, um diese Caches zu deaktivieren.
- Passen Sie Cache-Fenster mit `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` und
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS` an.

## Registry-Modell

Geladene Plugins verändern nicht direkt beliebige globale Kernzustände. Sie registrieren sich in einer
zentralen Plugin-Registry.

Die Registry verfolgt:

- Plugin-Einträge (Identität, Quelle, Herkunft, Status, Diagnosen)
- Tools
- Legacy-Hooks und typisierte Hooks
- Kanäle
- Provider
- Gateway-RPC-Handler
- HTTP-Routen
- CLI-Registrare
- Hintergrund-Services
- plugin-eigene Befehle

Kern-Features lesen dann aus dieser Registry, statt direkt mit Plugin-Modulen
zu sprechen. Dadurch bleibt das Laden eindirektional:

- Plugin-Modul -> Registry-Registrierung
- Kern-Laufzeit -> Registry-Konsum

Diese Trennung ist für die Wartbarkeit wichtig. Sie bedeutet, dass die meisten Kernoberflächen nur
einen Integrationspunkt brauchen: „Registry lesen“, nicht „jedes Plugin-Modul gesondert behandeln“.

## Callbacks für Konversationsbindung

Plugins, die eine Konversation binden, können reagieren, wenn eine Genehmigung entschieden wurde.

Verwenden Sie `api.onConversationBindingResolved(...)`, um einen Callback zu erhalten, nachdem eine Bindungs-
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

Felder der Callback-Nutzlast:

- `status`: `"approved"` oder `"denied"`
- `decision`: `"allow-once"`, `"allow-always"` oder `"deny"`
- `binding`: die aufgelöste Bindung für genehmigte Anfragen
- `request`: die ursprüngliche Anforderungszusammenfassung, Detach-Hinweis, Sender-ID und
  Konversationsmetadaten

Dieser Callback dient nur zur Benachrichtigung. Er ändert nicht, wer eine
Konversation binden darf, und läuft erst, nachdem die Kernbehandlung der Genehmigung abgeschlossen ist.

## Provider-Laufzeit-Hooks

Provider-Plugins haben jetzt zwei Ebenen:

- Manifest-Metadaten: `providerAuthEnvVars` für günstige Provider-
  Env-Auth-Erkennung vor dem Laden der Laufzeit, `providerAuthAliases` für Provider-Varianten, die sich
  Auth teilen, `channelEnvVars` für günstige Kanal-Env-/Setup-Erkennung vor dem
  Laden der Laufzeit sowie `providerAuthChoices` für günstige Labels bei Onboarding/Auth-Auswahl und
  CLI-Flag-Metadaten vor dem Laden der Laufzeit
- Hooks zur Konfigurationszeit: `catalog` / Legacy-`discovery` sowie `applyConfigDefaults`
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

OpenClaw besitzt weiterhin die generische Agent-Schleife, den Failover, die Verarbeitung von Transkripten und
Tool-Richtlinien. Diese Hooks sind die Erweiterungsoberfläche für anbieterspezifisches Verhalten, ohne
einen vollständig benutzerdefinierten Inferenztransport zu benötigen.

Verwenden Sie das Manifest `providerAuthEnvVars`, wenn der Provider env-basierte
Anmeldedaten hat, die generische Auth-/Status-/Modell-Picker-Pfade sehen sollen, ohne die Plugin-Laufzeit
zu laden. Verwenden Sie Manifest-`providerAuthAliases`, wenn eine Provider-ID die Env-Variablen,
Auth-Profile, konfigurationsgestützte Auth und die API-Key-Onboarding-Wahl einer anderen Provider-ID
wiederverwenden soll. Verwenden Sie Manifest-`providerAuthChoices`, wenn CLI-Oberflächen
für Onboarding/Auth-Auswahl die Choice-ID des Providers, Gruppenlabels und einfache
Auth-Verdrahtung per Einzelflag kennen sollen, ohne die Provider-Laufzeit zu laden. Behalten Sie in der Provider-Laufzeit
`envVars` für operatorseitige Hinweise wie Onboarding-Labels oder
Setup-Variablen für OAuth-Client-ID/Client-Secret.

Verwenden Sie Manifest-`channelEnvVars`, wenn ein Kanal env-gesteuerte Auth oder Einrichtung hat,
die generischer Shell-Env-Fallback, Konfigurations-/Statusprüfungen oder Setup-Prompts sehen sollen,
ohne die Kanal-Laufzeit zu laden.

### Hook-Reihenfolge und Verwendung

Für Modell-/Provider-Plugins ruft OpenClaw Hooks ungefähr in dieser Reihenfolge auf.
Die Spalte „Wann verwenden“ ist die schnelle Entscheidungshilfe.

| #   | Hook                              | Was er macht                                                                                                   | Wann verwenden                                                                                                                              |
| --- | --------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `catalog`                         | Provider-Konfiguration bei der Generierung von `models.json` in `models.providers` veröffentlichen             | Der Provider besitzt einen Katalog oder Standardwerte für `baseUrl`                                                                         |
| 2   | `applyConfigDefaults`             | plugin-eigene globale Konfigurationsstandards während der Konfigurationsmaterialisierung anwenden              | Standardwerte hängen von Auth-Modus, Env oder der Semantik der Provider-Modellfamilie ab                                                   |
| --  | _(integrierte Modellsuche)_       | OpenClaw versucht zuerst den normalen Registry-/Katalog-Pfad                                                   | _(kein Plugin-Hook)_                                                                                                                        |
| 3   | `normalizeModelId`                | Legacy- oder Preview-Aliase für Modell-IDs vor der Suche normalisieren                                         | Der Provider besitzt Alias-Bereinigung vor der kanonischen Modellauflösung                                                                  |
| 4   | `normalizeTransport`              | Provider-Familien-`api` / `baseUrl` vor generischer Modellzusammenstellung normalisieren                      | Der Provider besitzt Transport-Bereinigung für benutzerdefinierte Provider-IDs in derselben Transportfamilie                               |
| 5   | `normalizeConfig`                 | `models.providers.<id>` vor Laufzeit-/Provider-Auflösung normalisieren                                         | Der Provider benötigt Konfigurationsbereinigung, die beim Plugin leben sollte; gebündelte Google-Familien-Helper fangen auch unterstützte Google-Konfigurationseinträge ab |
| 6   | `applyNativeStreamingUsageCompat` | Native Streaming-Usage-Kompatibilitäts-Umschreibungen auf Konfigurationsprovider anwenden                      | Der Provider benötigt endpunktgesteuerte Korrekturen für native Streaming-Usage-Metadaten                                                  |
| 7   | `resolveConfigApiKey`             | Env-Marker-Auth für Konfigurationsprovider vor dem Laden der Laufzeit-Auth auflösen                            | Der Provider besitzt eine plugin-eigene Auflösung von Env-Marker-API-Keys; `amazon-bedrock` hat hier ebenfalls einen eingebauten AWS-Env-Marker-Resolver |
| 8   | `resolveSyntheticAuth`            | lokale/self-hosted oder konfigurationsgestützte Auth anzeigen, ohne Klartext zu persistieren                  | Der Provider kann mit einem synthetischen/lokalen Credential-Marker arbeiten                                                                |
| 9   | `resolveExternalAuthProfiles`     | plugin-eigene externe Auth-Profile überlagern; Standard-`persistence` ist `runtime-only` für CLI-/app-eigene Credentials | Der Provider verwendet externe Auth-Credentials wieder, ohne kopierte Refresh-Tokens zu persistieren                                       |
| 10  | `shouldDeferSyntheticProfileAuth` | gespeicherte synthetische Profil-Platzhalter hinter env-/konfigurationsgestützter Auth zurückstufen           | Der Provider speichert synthetische Platzhalterprofile, die keine Priorität haben sollten                                                  |
| 11  | `resolveDynamicModel`             | synchroner Fallback für plugin-eigene Modell-IDs, die noch nicht in der lokalen Registry sind                 | Der Provider akzeptiert beliebige Upstream-Modell-IDs                                                                                       |
| 12  | `prepareDynamicModel`             | asynchrones Warm-up, dann läuft `resolveDynamicModel` erneut                                                   | Der Provider benötigt Netzwerkmetadaten, bevor unbekannte IDs aufgelöst werden können                                                      |
| 13  | `normalizeResolvedModel`          | endgültige Umschreibung, bevor der Embedded-Runner das aufgelöste Modell verwendet                             | Der Provider benötigt Transport-Umschreibungen, verwendet aber weiterhin einen Kerntransport                                                |
| 14  | `contributeResolvedModelCompat`   | Kompatibilitätsflags für Anbietermodelle hinter einem anderen kompatiblen Transport beisteuern                 | Der Provider erkennt seine eigenen Modelle auf Proxy-Transporten, ohne den Provider zu übernehmen                                          |
| 15  | `capabilities`                    | plugin-eigene Transkript-/Tooling-Metadaten, die von gemeinsamer Kernlogik verwendet werden                   | Der Provider benötigt Besonderheiten für Transkripte/Provider-Familien                                                                      |
| 16  | `normalizeToolSchemas`            | Tool-Schemas normalisieren, bevor der Embedded-Runner sie sieht                                                | Der Provider benötigt schemaseitige Bereinigung für eine Transportfamilie                                                                   |
| 17  | `inspectToolSchemas`              | plugin-eigene Schema-Diagnosen nach der Normalisierung ausgeben                                                | Der Provider möchte Keyword-Warnungen ausgeben, ohne dem Kern anbieterspezifische Regeln beizubringen                                      |
| 18  | `resolveReasoningOutputMode`      | nativen versus getaggten Vertrag für Reasoning-Ausgaben auswählen                                              | Der Provider benötigt getaggtes Reasoning/finale Ausgabe statt nativer Felder                                                               |
| 19  | `prepareExtraParams`              | Normalisierung von Anfrageparametern vor generischen Stream-Option-Wrappern                                    | Der Provider benötigt Standard-Anfrageparameter oder anbieterspezifische Parameterbereinigung                                               |
| 20  | `createStreamFn`                  | normalen Stream-Pfad vollständig durch einen benutzerdefinierten Transport ersetzen                            | Der Provider benötigt ein benutzerdefiniertes Wire-Protokoll, nicht nur einen Wrapper                                                      |
| 21  | `wrapStreamFn`                    | Stream-Wrapper, nachdem generische Wrapper angewendet wurden                                                   | Der Provider benötigt Wrapper für Anfrageheader/Body/Modell-Kompatibilität ohne benutzerdefinierten Transport                              |
| 22  | `resolveTransportTurnState`       | native turnbezogene Transport-Header oder -Metadaten anhängen                                                  | Der Provider möchte, dass generische Transporte die providereigene Turn-Identität senden                                                   |
| 23  | `resolveWebSocketSessionPolicy`   | native WebSocket-Header oder Richtlinien zur Session-Abkühlung anhängen                                        | Der Provider möchte, dass generische WS-Transporte Session-Header oder Fallback-Richtlinien abstimmen                                      |
| 24  | `formatApiKey`                    | Auth-Profil-Formatierer: gespeichertes Profil wird zur Laufzeit-Zeichenfolge `apiKey`                         | Der Provider speichert zusätzliche Auth-Metadaten und benötigt eine benutzerdefinierte Laufzeit-Tokenform                                  |
| 25  | `refreshOAuth`                    | OAuth-Refresh-Override für benutzerdefinierte Refresh-Endpunkte oder Richtlinien bei Refresh-Fehlschlägen     | Der Provider passt nicht zu den gemeinsamen `pi-ai`-Refreshern                                                                              |
| 26  | `buildAuthDoctorHint`             | Reparaturhinweis, der angehängt wird, wenn OAuth-Refresh fehlschlägt                                           | Der Provider benötigt plugin-eigene Hinweise zur Auth-Reparatur nach einem Refresh-Fehler                                                  |
| 27  | `matchesContextOverflowError`     | plugin-eigener Matcher für Überläufe des Kontextfensters                                                       | Der Provider hat rohe Overflow-Fehler, die generische Heuristiken übersehen würden                                                         |
| 28  | `classifyFailoverReason`          | plugin-eigene Klassifizierung des Failover-Grunds                                                              | Der Provider kann rohe API-/Transportfehler auf Ratenbegrenzung/Überlast/etc. abbilden                                                     |
| 29  | `isCacheTtlEligible`              | Richtlinie für Prompt-Cache bei Proxy-/Backhaul-Providern                                                     | Der Provider benötigt proxy-spezifisches Cache-TTL-Gating                                                                                   |
| 30  | `buildMissingAuthMessage`         | Ersatz für die generische Wiederherstellungsnachricht bei fehlender Auth                                       | Der Provider benötigt einen provider-spezifischen Hinweis zur Wiederherstellung fehlender Auth                                              |
| 31  | `suppressBuiltInModel`            | Unterdrückung veralteter Upstream-Modelle plus optionaler benutzerseitiger Fehlerhinweis                      | Der Provider muss veraltete Upstream-Zeilen ausblenden oder durch einen Anbieterhinweis ersetzen                                           |
| 32  | `augmentModelCatalog`             | synthetische/endgültige Katalogzeilen, die nach Discovery angehängt werden                                     | Der Provider benötigt synthetische Vorwärtskompatibilitäts-Zeilen in `models list` und Pickern                                             |
| 33  | `isBinaryThinking`                | Ein/Aus-Reasoning-Umschaltung für Anbieter mit binärem Thinking                                                | Der Provider bietet nur binäres Thinking an/aus an                                                                                          |
| 34  | `supportsXHighThinking`           | `xhigh`-Reasoning-Unterstützung für ausgewählte Modelle                                                        | Der Provider möchte `xhigh` nur für eine Teilmenge von Modellen                                                                             |
| 35  | `resolveDefaultThinkingLevel`     | Standard-`/think`-Level für eine bestimmte Modellfamilie                                                       | Der Provider besitzt die Standard-`/think`-Richtlinie für eine Modellfamilie                                                                |
| 36  | `isModernModelRef`                | Matcher für moderne Modelle für Live-Profil-Filter und Smoke-Auswahl                                           | Der Provider besitzt das Matching bevorzugter Modelle für Live/Smoke                                                                        |
| 37  | `prepareRuntimeAuth`              | konfiguriertes Credential direkt vor der Inferenz in das tatsächliche Laufzeit-Token/den Schlüssel umtauschen | Der Provider benötigt einen Tokenaustausch oder kurzlebige Anfrage-Credentials                                                              |
| 38  | `resolveUsageAuth`                | Credentials für Nutzung/Abrechnung für `/usage` und verwandte Statusoberflächen auflösen                       | Der Provider benötigt benutzerdefinierte Tokenanalyse für Nutzung/Quota oder andere Usage-Credentials                                       |
| 39  | `fetchUsageSnapshot`              | provider-spezifische Nutzung-/Quota-Snapshots abrufen und normalisieren, nachdem Auth aufgelöst wurde         | Der Provider benötigt einen provider-spezifischen Usage-Endpunkt oder Payload-Parser                                                       |
| 40  | `createEmbeddingProvider`         | plugin-eigenen Embedding-Adapter für Speicher/Suche bauen                                                     | Verhalten für Memory-Embeddings gehört zum Provider-Plugin                                                                                  |
| 41  | `buildReplayPolicy`               | eine Replay-Richtlinie zurückgeben, die den Umgang des Providers mit Transkripten steuert                     | Der Provider benötigt eine benutzerdefinierte Transkript-Richtlinie (zum Beispiel Entfernen von Thinking-Blöcken)                          |
| 42  | `sanitizeReplayHistory`           | Replay-Verlauf nach generischer Transkript-Bereinigung umschreiben                                             | Der Provider benötigt provider-spezifische Replay-Umschreibungen über gemeinsame Kompaktion-Helper hinaus                                  |
| 43  | `validateReplayTurns`             | endgültige Validierung oder Umformung von Replay-Turns vor dem Embedded-Runner                                | Der Provider-Transport benötigt strengere Turn-Validierung nach generischer Bereinigung                                                     |
| 44  | `onModelSelected`                 | plugin-eigene Nebeneffekte nach Auswahl des Modells ausführen                                                  | Der Provider benötigt Telemetrie oder provider-eigenen Zustand, wenn ein Modell aktiv wird                                                  |

`normalizeModelId`, `normalizeTransport` und `normalizeConfig` prüfen zuerst das
zugeordnete Provider-Plugin und greifen dann auf andere hook-fähige Provider-Plugins zurück,
bis eines tatsächlich die Modell-ID oder den Transport/die Konfiguration ändert. Das hält
Alias-/Kompatibilitäts-Provider-Shims funktionsfähig, ohne vom Aufrufer zu verlangen zu wissen,
welches gebündelte Plugin die Umschreibung besitzt. Wenn kein Provider-Hook einen unterstützten
Google-Familien-Konfigurationseintrag umschreibt, greift weiterhin der gebündelte Google-Konfigurations-
Normalizer für diese Kompatibilitätsbereinigung.

Wenn der Provider ein vollständig benutzerdefiniertes Wire-Protokoll oder einen benutzerdefinierten Request-
Executor benötigt, ist das eine andere Klasse von Erweiterung. Diese Hooks sind für Provider-Verhalten gedacht,
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
  Hinweise zur Provider-Familie, Anleitungen zur Auth-Reparatur, Integration von
  Nutzungsendpunkten, Prompt-Cache-Eignung, auth-bewusste Konfigurationsstandards, die
  Standard-/adaptive Thinking-Richtlinie für Claude sowie Anthropic-spezifisches Stream-Shaping für
  Beta-Header, `/fast` / `serviceTier` und `context1m` besitzt.
- Die Claude-spezifischen Stream-Helper von Anthropic verbleiben vorerst in der eigenen
  öffentlichen Naht `api.ts` / `contract-api.ts` des gebündelten Plugins. Diese Paketoberfläche
  exportiert `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
  `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` sowie die Low-Level-
  Anthropic-Wrapper-Builder, statt das generische SDK um die Beta-Header-Regeln eines
  einzelnen Providers zu erweitern.
- OpenAI verwendet `resolveDynamicModel`, `normalizeResolvedModel` und
  `capabilities` sowie `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `supportsXHighThinking` und `isModernModelRef`,
  weil es Vorwärtskompatibilität für GPT-5.4, die direkte OpenAI-
  Normalisierung `openai-completions` -> `openai-responses`, Codex-bewusste Auth-
  Hinweise, Spark-Unterdrückung, synthetische OpenAI-Listenzeilen und GPT-5-Thinking-/
  Live-Modell-Richtlinien besitzt; die Stream-Familie `openai-responses-defaults` besitzt die
  gemeinsamen nativen OpenAI-Responses-Wrapper für Zuordnungsheader,
  `/fast`/`serviceTier`, Textausführlichkeit, native Codex-Websuche,
  Reasoning-kompatibles Payload-Shaping und Responses-Kontextverwaltung.
- OpenRouter verwendet `catalog` sowie `resolveDynamicModel` und
  `prepareDynamicModel`, weil der Provider ein Pass-through ist und neue
  Modell-IDs verfügbar machen kann, bevor der statische Katalog von OpenClaw aktualisiert wird; außerdem nutzt es
  `capabilities`, `wrapStreamFn` und `isCacheTtlEligible`, um
  provider-spezifische Request-Header, Routing-Metadaten, Reasoning-Patches und
  Prompt-Cache-Richtlinien aus dem Kern herauszuhalten. Seine Replay-Richtlinie stammt aus der
  Familie `passthrough-gemini`, während die Stream-Familie `openrouter-thinking`
  Proxy-Reasoning-Injection und das Überspringen nicht unterstützter Modelle bzw. von `auto` besitzt.
- GitHub Copilot verwendet `catalog`, `auth`, `resolveDynamicModel` und
  `capabilities` sowie `prepareRuntimeAuth` und `fetchUsageSnapshot`, weil es
  provider-eigenes Device-Login, Modell-Fallback-Verhalten, Besonderheiten bei Claude-Transkripten,
  einen GitHub-Token -> Copilot-Token-Austausch und einen provider-eigenen Nutzungsendpunkt benötigt.
- OpenAI Codex verwendet `catalog`, `resolveDynamicModel`,
  `normalizeResolvedModel`, `refreshOAuth` und `augmentModelCatalog` sowie
  `prepareExtraParams`, `resolveUsageAuth` und `fetchUsageSnapshot`, weil es
  weiterhin auf Kern-OpenAI-Transporten läuft, aber seine Transport-/`baseUrl`-
  Normalisierung, Richtlinien zum OAuth-Refresh-Fallback, die Standardwahl des Transports,
  synthetische Codex-Katalogzeilen und die Integration des ChatGPT-Nutzungsendpunkts besitzt; es
  teilt sich dieselbe Stream-Familie `openai-responses-defaults` wie direktes OpenAI.
- Google AI Studio und Gemini CLI OAuth verwenden `resolveDynamicModel`,
  `buildReplayPolicy`, `sanitizeReplayHistory`,
  `resolveReasoningOutputMode`, `wrapStreamFn` und `isModernModelRef`, weil die
  Replay-Familie `google-gemini` den Vorwärtskompatibilitäts-Fallback für Gemini 3.1,
  native Gemini-Replay-Validierung, Bootstrap-Replay-Säuberung, den getaggten
  Reasoning-Ausgabemodus und das Matching moderner Modelle besitzt, während die
  Stream-Familie `google-thinking` die Normalisierung von Gemini-Thinking-Payloads besitzt;
  Gemini CLI OAuth verwendet außerdem `formatApiKey`, `resolveUsageAuth` und
  `fetchUsageSnapshot` für Token-Formatierung, Token-Parsing und
  Verdrahtung des Quota-Endpunkts.
- Anthropic Vertex verwendet `buildReplayPolicy` über die
  Replay-Familie `anthropic-by-model`, damit Claude-spezifische Replay-Bereinigung
  auf Claude-IDs beschränkt bleibt statt auf jeden Transport `anthropic-messages`.
- Amazon Bedrock verwendet `buildReplayPolicy`, `matchesContextOverflowError`,
  `classifyFailoverReason` und `resolveDefaultThinkingLevel`, weil es
  Bedrock-spezifische Klassifizierung von Throttle-/Not-ready-/Context-Overflow-Fehlern
  für Anthropic-auf-Bedrock-Datenverkehr besitzt; seine Replay-Richtlinie teilt sich weiterhin denselben
  nur-für-Claude-Schutz `anthropic-by-model`.
- OpenRouter, Kilocode, Opencode und Opencode Go verwenden `buildReplayPolicy`
  über die Replay-Familie `passthrough-gemini`, weil sie Gemini-
  Modelle über OpenAI-kompatible Transporte proxien und eine Bereinigung von Gemini-
  Thought-Signatures ohne native Gemini-Replay-Validierung oder
  Bootstrap-Umschreibungen benötigen.
- MiniMax verwendet `buildReplayPolicy` über die
  Replay-Familie `hybrid-anthropic-openai`, weil ein Provider sowohl Semantik
  für Anthropic-Nachrichten als auch OpenAI-Kompatibilität besitzt; Claude-spezifisches
  Entfernen von Thinking-Blöcken bleibt auf der Anthropic-Seite, während der
  Reasoning-Ausgabemodus zurück auf nativ gesetzt wird, und die Stream-Familie `minimax-fast-mode`
  besitzt Umschreibungen für den Fast-Modus auf dem gemeinsamen Stream-Pfad.
- Moonshot verwendet `catalog` sowie `wrapStreamFn`, weil es weiterhin den gemeinsamen
  OpenAI-Transport nutzt, aber provider-eigene Normalisierung von Thinking-Payloads benötigt; die
  Stream-Familie `moonshot-thinking` ordnet Konfiguration plus `/think`-Zustand seiner
  nativen binären Thinking-Payload zu.
- Kilocode verwendet `catalog`, `capabilities`, `wrapStreamFn` und
  `isCacheTtlEligible`, weil es provider-eigene Request-Header,
  Normalisierung von Reasoning-Payloads, Hinweise für Gemini-Transkripte und Anthropic-
  Cache-TTL-Gating benötigt; die Stream-Familie `kilocode-thinking` hält die Kilo-
  Thinking-Injektion auf dem gemeinsamen Proxy-Stream-Pfad, während `kilo/auto` und
  andere Proxy-Modell-IDs, die keine expliziten Reasoning-Payloads unterstützen, ausgelassen werden.
- Z.AI verwendet `resolveDynamicModel`, `prepareExtraParams`, `wrapStreamFn`,
  `isCacheTtlEligible`, `isBinaryThinking`, `isModernModelRef`,
  `resolveUsageAuth` und `fetchUsageSnapshot`, weil es GLM-5-Fallback,
  Standardwerte für `tool_stream`, binäre Thinking-UX, Matching moderner Modelle sowie
  sowohl Usage-Auth als auch Quota-Abruf besitzt; die Stream-Familie `tool-stream-default-on`
  hält den standardmäßig aktivierten `tool_stream`-Wrapper aus handgeschriebenem
  Glue-Code pro Provider heraus.
- xAI verwendet `normalizeResolvedModel`, `normalizeTransport`,
  `contributeResolvedModelCompat`, `prepareExtraParams`, `wrapStreamFn`,
  `resolveSyntheticAuth`, `resolveDynamicModel` und `isModernModelRef`,
  weil es die Normalisierung des nativen xAI-Responses-Transports, Umschreibungen von Grok-
  Fast-Mode-Aliassen, Standardwerte für `tool_stream`, Bereinigung für strikte Tools / Reasoning-Payloads,
  Wiederverwendung von Fallback-Auth für plugin-eigene Tools, Vorwärtskompatibilitäts-
  Auflösung von Grok-Modellen und provider-eigene Kompatibilitätspatches wie xAI-Tool-Schema-
  Profil, nicht unterstützte Schema-Keywords, natives `web_search` und HTML-Entity-
  Dekodierung für Tool-Call-Argumente besitzt.
- Mistral, OpenCode Zen und OpenCode Go verwenden nur `capabilities`, um
  Besonderheiten bei Transkripten/Tooling aus dem Kern herauszuhalten.
- Nur-Katalog-gebündelte Provider wie `byteplus`, `cloudflare-ai-gateway`,
  `huggingface`, `kimi-coding`, `nvidia`, `qianfan`,
  `synthetic`, `together`, `venice`, `vercel-ai-gateway` und `volcengine` verwenden
  nur `catalog`.
- Qwen verwendet `catalog` für seinen Textprovider sowie gemeinsame Registrierungen für
  Medienverständnis und Videogenerierung für seine multimodalen Oberflächen.
- MiniMax und Xiaomi verwenden `catalog` sowie Usage-Hooks, weil ihr `/usage`-
  Verhalten plugin-eigen ist, obwohl die Inferenz weiterhin über die gemeinsamen Transporte läuft.

## Laufzeit-Helfer

Plugins können über `api.runtime` auf ausgewählte Kern-Helper zugreifen. Für TTS:

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

- `textToSpeech` gibt die normale Kern-TTS-Ausgabe-Nutzlast für Datei-/Voice-Note-Oberflächen zurück.
- Verwendet die Kernkonfiguration `messages.tts` und Provider-Auswahl.
- Gibt PCM-Audiopuffer + Samplerate zurück. Plugins müssen für Provider neu sampeln/kodieren.
- `listVoices` ist pro Provider optional. Verwenden Sie es für anbietereigene Sprach-Auswahllisten oder Setup-Flows.
- Sprachlisten können reichere Metadaten wie Gebietsschema, Geschlecht und Persönlichkeits-Tags für providerbewusste Picker enthalten.
- OpenAI und ElevenLabs unterstützen heute Telefonie. Microsoft nicht.

Plugins können auch Speech-Provider über `api.registerSpeechProvider(...)` registrieren.

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
- Verwenden Sie Speech-Provider für anbietereigene Syntheseimplementierungen.
- Legacy-Microsoft-`edge`-Eingabe wird auf die Provider-ID `microsoft` normalisiert.
- Das bevorzugte Ownership-Modell ist unternehmensorientiert: Ein Anbieter-Plugin kann
  Text-, Sprach-, Bild- und künftige Medien-Provider besitzen, wenn OpenClaw diese
  Fähigkeitsverträge hinzufügt.

Für Bild-/Audio-/Videoverständnis registrieren Plugins einen typisierten
Provider für Medienverständnis statt eines generischen Schlüssel/Wert-Sacks:

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
- Die Videogenerierung folgt bereits demselben Muster:
  - der Kern besitzt den Fähigkeitsvertrag und den Laufzeithelfer
  - Anbieter-Plugins registrieren `api.registerVideoGenerationProvider(...)`
  - Feature-/Kanal-Plugins konsumieren `api.runtime.videoGeneration.*`

Für Laufzeit-Helfer des Medienverständnisses können Plugins Folgendes aufrufen:

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

Für Audiotranskription können Plugins entweder die Laufzeit des Medienverständnisses
oder das ältere STT-Alias verwenden:

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
- Verwendet die Audio-Konfiguration des Kern-Medienverständnisses (`tools.media.audio`) und die Provider-Fallback-Reihenfolge.
- Gibt `{ text: undefined }` zurück, wenn keine Transkriptionsausgabe erzeugt wird (zum Beispiel bei übersprungenen/nicht unterstützten Eingaben).
- `api.runtime.stt.transcribeAudioFile(...)` bleibt als Kompatibilitäts-Alias bestehen.

Plugins können auch Hintergrundläufe von Subagents über `api.runtime.subagent` starten:

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
- OpenClaw berücksichtigt diese Override-Felder nur für vertrauenswürdige Aufrufer.
- Für plugin-eigene Fallback-Läufe müssen Operatoren mit `plugins.entries.<id>.subagent.allowModelOverride: true` zustimmen.
- Verwenden Sie `plugins.entries.<id>.subagent.allowedModels`, um vertrauenswürdige Plugins auf bestimmte kanonische Ziele `provider/model` zu beschränken, oder `"*"`, um explizit jedes Ziel zu erlauben.
- Läufe von Subagents durch nicht vertrauenswürdige Plugins funktionieren weiterhin, aber Override-Anfragen werden abgelehnt, statt stillschweigend zurückzufallen.

Für die Websuche können Plugins den gemeinsamen Laufzeit-Helfer konsumieren, statt
in die Verdrahtung des Agent-Tools zu greifen:

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

- Behalten Sie Provider-Auswahl, Auflösung von Credentials und gemeinsame Request-Semantik im Kern.
- Verwenden Sie Websuch-Provider für anbieterspezifische Suchtransporte.
- `api.runtime.webSearch.*` ist die bevorzugte gemeinsame Oberfläche für Feature-/Kanal-Plugins, die Suchverhalten benötigen, ohne von dem Agent-Tool-Wrapper abhängig zu sein.

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

- `generate(...)`: ein Bild mit der konfigurierten Kette von Bildgenerierungs-Providern erzeugen.
- `listProviders(...)`: verfügbare Bildgenerierungs-Provider und ihre Fähigkeiten auflisten.

## Gateway-HTTP-Routen

Plugins können HTTP-Endpunkte mit `api.registerHttpRoute(...)` bereitstellen.

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
- `auth`: erforderlich. Verwenden Sie `"gateway"`, um normale Gateway-Auth zu verlangen, oder `"plugin"` für pluginverwaltete Auth/Webhook-Verifikation.
- `match`: optional. `"exact"` (Standard) oder `"prefix"`.
- `replaceExisting`: optional. Erlaubt demselben Plugin, seine eigene bestehende Routenregistrierung zu ersetzen.
- `handler`: gibt `true` zurück, wenn die Route die Anfrage verarbeitet hat.

Hinweise:

- `api.registerHttpHandler(...)` wurde entfernt und führt zu einem Fehler beim Laden des Plugins. Verwenden Sie stattdessen `api.registerHttpRoute(...)`.
- Plugin-Routen müssen `auth` explizit deklarieren.
- Exakte Konflikte von `path + match` werden abgelehnt, außer `replaceExisting: true` ist gesetzt, und ein Plugin kann keine Route eines anderen Plugins ersetzen.
- Überlappende Routen mit unterschiedlichen `auth`-Leveln werden abgelehnt. Halten Sie `exact`-/`prefix`-Fallthrough-Ketten nur auf derselben Auth-Stufe.
- Routen mit `auth: "plugin"` erhalten nicht automatisch Runtime-Scopes des Operators. Sie sind für pluginverwaltete Webhooks/Signaturprüfung gedacht, nicht für privilegierte Gateway-Helper-Aufrufe.
- Routen mit `auth: "gateway"` laufen innerhalb eines Gateway-Request-Runtime-Scopes, aber dieser Scope ist bewusst konservativ:
  - Bearer-Auth mit Shared Secret (`gateway.auth.mode = "token"` / `"password"`) hält die Runtime-Scopes von Plugin-Routen auf `operator.write` fest, selbst wenn der Aufrufer `x-openclaw-scopes` sendet
  - vertrauenswürdige HTTP-Modi mit identitätstragenden Daten (zum Beispiel `trusted-proxy` oder `gateway.auth.mode = "none"` an einem privaten Ingress) beachten `x-openclaw-scopes` nur, wenn der Header ausdrücklich vorhanden ist
  - wenn `x-openclaw-scopes` bei solchen identitätstragenden Plugin-Routenanfragen fehlt, fällt der Runtime-Scope auf `operator.write` zurück
- Praktische Regel: Gehen Sie nicht davon aus, dass eine Gateway-authentifizierte Plugin-Route implizit eine Admin-Oberfläche ist. Wenn Ihre Route rein administratives Verhalten braucht, verlangen Sie einen identitätstragenden Auth-Modus und dokumentieren Sie den expliziten Vertragsumfang des Headers `x-openclaw-scopes`.

## Importpfade des Plugin SDK

Verwenden Sie SDK-Subpaths statt des monolithischen Imports `openclaw/plugin-sdk`,
wenn Sie Plugins erstellen:

- `openclaw/plugin-sdk/plugin-entry` für Plugin-Registrierungsprimitive.
- `openclaw/plugin-sdk/core` für den generischen gemeinsamen pluginseitigen Vertrag.
- `openclaw/plugin-sdk/config-schema` für den Export des Zod-Schemas der Wurzel `openclaw.json`
  (`OpenClawSchema`).
- Stabile Kanal-Primitive wie `openclaw/plugin-sdk/channel-setup`,
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
  Helper für Inbound-Mention-Richtlinien, Envelope-Formatierung und
  Kontext-Helper für Inbound-Envelopes.
  `channel-setup` ist die schmale optionale Setup-Naht.
  `setup-runtime` ist die laufzeitsichere Setup-Oberfläche, die von `setupEntry` /
  verzögertem Start verwendet wird, einschließlich der importsicheren Setup-Patch-Adapter.
  `setup-adapter-runtime` ist die env-bewusste Naht für Account-Setup-Adapter.
  `setup-tools` ist die kleine Naht für CLI-/Archiv-/Dokumentations-Helfer (`formatCliCommand`,
  `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`,
  `CONFIG_DIR`).
- Domänen-Subpaths wie `openclaw/plugin-sdk/channel-config-helpers`,
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
  `openclaw/plugin-sdk/directory-runtime` für gemeinsame Laufzeit-/Konfigurations-Helfer.
  `telegram-command-config` ist die schmale öffentliche Naht für Normalisierung/Validierung von benutzerdefinierten Telegram-
  Befehlen und bleibt verfügbar, selbst wenn die Vertragsoberfläche des gebündelten
  Telegram vorübergehend nicht verfügbar ist.
  `text-runtime` ist die gemeinsame Naht für Text/Markdown/Logging, einschließlich
  Entfernen von für Assistenten sichtbarem Text, Helpern für Markdown-Rendering/Chunking, Redaktions-
  Helpern, Helpern für Richtlinien-Tags und Safe-Text-Utilities.
- Kanalspezifische Approval-Seams sollten bevorzugt einen einzigen `approvalCapability`-
  Vertrag auf dem Plugin verwenden. Der Kern liest dann Auth, Bereitstellung, Rendering,
  natives Routing und lazy natives Handler-Verhalten für Approvals über diese eine Fähigkeit,
  statt Approval-Verhalten in unabhängige Plugin-Felder zu mischen.
- `openclaw/plugin-sdk/channel-runtime` ist veraltet und verbleibt nur als
  Kompatibilitäts-Shim für ältere Plugins. Neuer Code sollte stattdessen die schmaleren
  generischen Primitive importieren, und Repo-Code sollte keine neuen Importe dieses
  Shims hinzufügen.
- Interne Elemente gebündelter Extensions bleiben privat. Externe Plugins sollten nur
  `openclaw/plugin-sdk/*`-Subpaths verwenden. OpenClaw-Kern-/Test-Code kann die
  öffentlichen Repo-Einstiegspunkte unter einer Plugin-Paketwurzel wie `index.js`, `api.js`,
  `runtime-api.js`, `setup-entry.js` und eng begrenzte Dateien wie
  `login-qr-api.js` verwenden. Importieren Sie niemals `src/*` eines Plugin-Pakets aus dem Kern oder aus
  einer anderen Extension.
- Aufteilung der Repo-Einstiegspunkte:
  `<plugin-package-root>/api.js` ist das Barrel für Helfer/Typen,
  `<plugin-package-root>/runtime-api.js` ist das nur-Laufzeit-Barrel,
  `<plugin-package-root>/index.js` ist der Einstieg des gebündelten Plugins,
  und `<plugin-package-root>/setup-entry.js` ist der Einstieg des Setup-Plugins.
- Aktuelle Beispiele für gebündelte Provider:
  - Anthropic verwendet `api.js` / `contract-api.js` für Claude-Stream-Helper wie
    `wrapAnthropicProviderStream`, Helper für Beta-Header und Parsing von `service_tier`.
  - OpenAI verwendet `api.js` für Provider-Builder, Helper für Standardmodelle und
    Builder für Realtime-Provider.
  - OpenRouter verwendet `api.js` für seinen Provider-Builder sowie Onboarding-/Konfigurations-
    Helper, während `register.runtime.js` weiterhin generische
    `plugin-sdk/provider-stream`-Helper für die repo-lokale Nutzung re-exportieren kann.
- Über Fassade geladene öffentliche Einstiegspunkte bevorzugen den aktiven Laufzeit-
  Konfigurations-Snapshot, wenn einer existiert, und fallen andernfalls auf die auf der Platte aufgelöste Konfigurationsdatei zurück,
  wenn OpenClaw noch keinen Laufzeit-Snapshot bereitstellt.
- Generische gemeinsame Primitive bleiben der bevorzugte öffentliche SDK-Vertrag. Ein kleiner
  reservierter Kompatibilitätssatz gebündelter, kanalmarkierter Helper-Seams existiert weiterhin.
  Behandeln Sie diese als Seams für gebündelte Wartung/Kompatibilität, nicht als neue
  Importziele für Drittanbieter; neue kanalübergreifende Verträge sollten weiterhin auf
  generischen `plugin-sdk/*`-Subpaths oder den plugin-lokalen Barrels `api.js` /
  `runtime-api.js` landen.

Kompatibilitätshinweis:

- Vermeiden Sie für neuen Code das Root-Barrel `openclaw/plugin-sdk`.
- Bevorzugen Sie zuerst die schmalen stabilen Primitive. Die neueren Subpaths für setup/pairing/reply/
  feedback/contract/inbound/threading/command/secret-input/webhook/infra/
  allowlist/status/message-tool sind der vorgesehene Vertrag für neue
  gebündelte und externe Plugin-Arbeit.
  Target-Parsing/-Matching gehört auf `openclaw/plugin-sdk/channel-targets`.
  Gates für Message-Actions und Helper für Reaktions-Message-IDs gehören auf
  `openclaw/plugin-sdk/channel-actions`.
- Extensionspezifische Helper-Barrels gebündelter Plugins sind standardmäßig nicht stabil. Wenn ein
  Helper nur von einer gebündelten Extension benötigt wird, behalten Sie ihn hinter der
  lokalen Naht `api.js` oder `runtime-api.js` der Extension, statt ihn nach
  `openclaw/plugin-sdk/<extension>` zu befördern.
- Neue gemeinsame Helper-Seams sollten generisch sein, nicht kanalmarkiert. Gemeinsames Target-
  Parsing gehört auf `openclaw/plugin-sdk/channel-targets`; kanalspezifische
  Interna bleiben hinter dem lokalen `api.js` oder `runtime-api.js` des besitzenden Plugins.
- Fähigkeitsspezifische Subpaths wie `image-generation`,
  `media-understanding` und `speech` existieren, weil gebündelte/native Plugins sie
  heute verwenden. Ihre Existenz bedeutet für sich genommen nicht, dass jeder exportierte Helper ein
  langfristig eingefrorener externer Vertrag ist.

## Schemas für das Message-Tool

Plugins sollten kanalspezifische Schema-Beiträge für `describeMessageTool(...)`
besitzen. Behalten Sie providerspezifische Felder im Plugin, nicht im gemeinsamen Kern.

Für gemeinsame portable Schemafragmente verwenden Sie die generischen Helper, die über
`openclaw/plugin-sdk/channel-actions` exportiert werden:

- `createMessageToolButtonsSchema()` für Payloads im Stil von Schaltflächengittern
- `createMessageToolCardSchema()` für strukturierte Karten-Payloads

Wenn eine Schemaform nur für einen Provider sinnvoll ist, definieren Sie sie im
eigenen Quellcode dieses Plugins, statt sie in das gemeinsame SDK zu befördern.

## Auflösung von Kanalzielen

Kanal-Plugins sollten die kanalspezifische Zielsemantik besitzen. Halten Sie den gemeinsamen
Outbound-Host generisch und verwenden Sie die Oberfläche des Messaging-Adapters für Provider-Regeln:

- `messaging.inferTargetChatType({ to })` entscheidet, ob ein normalisiertes Ziel
  vor der Verzeichnissuche als `direct`, `group` oder `channel` behandelt werden soll.
- `messaging.targetResolver.looksLikeId(raw, normalized)` teilt dem Kern mit, ob eine
  Eingabe direkt in die Auflösung einer ID-ähnlichen Form übergehen soll, statt in die Verzeichnissuche.
- `messaging.targetResolver.resolveTarget(...)` ist der Plugin-Fallback, wenn
  der Kern nach der Normalisierung oder nach einem Verzeichnis-Fehlschlag eine endgültige
  providereigene Auflösung benötigt.
- `messaging.resolveOutboundSessionRoute(...)` besitzt die providerspezifische Konstruktion der Sitzungsroute,
  sobald ein Ziel aufgelöst ist.

Empfohlene Aufteilung:

- Verwenden Sie `inferTargetChatType` für Kategorientscheidungen, die vor
  der Suche nach Peers/Gruppen stattfinden sollten.
- Verwenden Sie `looksLikeId` für Prüfungen wie „dies als explizite/native Ziel-ID behandeln“.
- Verwenden Sie `resolveTarget` für provider-spezifischen Normalisierungs-Fallback, nicht für
  umfangreiche Verzeichnissuche.
- Behalten Sie native Provider-IDs wie Chat-IDs, Thread-IDs, JIDs, Handles und Raum-IDs
  innerhalb von `target`-Werten oder providerspezifischen Parametern, nicht in generischen SDK-Feldern.

## Konfigurationsgestützte Verzeichnisse

Plugins, die Verzeichniseinträge aus der Konfiguration ableiten, sollten diese Logik im
Plugin behalten und die gemeinsamen Helper aus
`openclaw/plugin-sdk/directory-runtime` wiederverwenden.

Verwenden Sie dies, wenn ein Kanal konfigurationsgestützte Peers/Gruppen benötigt, wie etwa:

- Allowlist-gesteuerte DM-Peers
- konfigurierte Kanal-/Gruppenzuordnungen
- kontobezogene statische Verzeichnis-Fallbacks

Die gemeinsamen Helper in `directory-runtime` behandeln nur generische Operationen:

- Query-Filterung
- Anwenden von Limits
- Helfer für Deduplizierung/Normalisierung
- Erstellen von `ChannelDirectoryEntry[]`

Kanalspezifische Kontoinspektion und ID-Normalisierung sollten in der
Plugin-Implementierung verbleiben.

## Provider-Kataloge

Provider-Plugins können Modellkataloge für die Inferenz definieren mit
`registerProvider({ catalog: { run(...) { ... } } })`.

`catalog.run(...)` gibt dieselbe Form zurück, die OpenClaw in
`models.providers` schreibt:

- `{ provider }` für einen Provider-Eintrag
- `{ providers }` für mehrere Provider-Einträge

Verwenden Sie `catalog`, wenn das Plugin providerspezifische Modell-IDs, Standardwerte für `baseUrl`
oder auth-gesteuerte Modellmetadaten besitzt.

`catalog.order` steuert, wann der Katalog eines Plugins relativ zu den
integrierten impliziten Providern von OpenClaw zusammengeführt wird:

- `simple`: einfache API-Key- oder env-gesteuerte Provider
- `profile`: Provider, die erscheinen, wenn Auth-Profile vorhanden sind
- `paired`: Provider, die mehrere zusammengehörige Provider-Einträge synthetisieren
- `late`: letzter Durchlauf, nach anderen impliziten Providern

Spätere Provider gewinnen bei Schlüsselkollisionen, sodass Plugins absichtlich einen
integrierten Provider-Eintrag mit derselben Provider-ID überschreiben können.

Kompatibilität:

- `discovery` funktioniert weiterhin als Legacy-Alias
- wenn sowohl `catalog` als auch `discovery` registriert sind, verwendet OpenClaw `catalog`

## Schreibgeschützte Kanalinspektion

Wenn Ihr Plugin einen Kanal registriert, bevorzugen Sie die Implementierung von
`plugin.config.inspectAccount(cfg, accountId)` zusammen mit `resolveAccount(...)`.

Warum:

- `resolveAccount(...)` ist der Laufzeitpfad. Es darf davon ausgehen, dass Credentials
  vollständig materialisiert sind, und bei fehlenden erforderlichen Secrets schnell fehlschlagen.
- Schreibgeschützte Befehlspfade wie `openclaw status`, `openclaw status --all`,
  `openclaw channels status`, `openclaw channels resolve` und Doctor-/Konfigurations-
  Reparaturabläufe sollten keine Laufzeit-Credentials materialisieren müssen, nur um
  Konfiguration zu beschreiben.

Empfohlenes Verhalten von `inspectAccount(...)`:

- Nur beschreibenden Kontozustand zurückgeben.
- `enabled` und `configured` beibehalten.
- Felder zu Credential-Quelle/-Status einschließen, wenn relevant, z. B.:
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- Sie müssen keine rohen Tokenwerte zurückgeben, nur um schreibgeschützte
  Verfügbarkeit zu melden. Die Rückgabe von `tokenStatus: "available"` (und dem zugehörigen
  Quellenfeld) reicht für statusartige Befehle aus.
- Verwenden Sie `configured_unavailable`, wenn ein Credential über SecretRef konfiguriert ist, im
  aktuellen Befehlspfad aber nicht verfügbar ist.

Dadurch können schreibgeschützte Befehle „konfiguriert, aber in diesem Befehlspfad nicht verfügbar“
melden, statt abzustürzen oder das Konto fälschlich als nicht konfiguriert zu melden.

## Paket-Packs

Ein Plugin-Verzeichnis kann ein `package.json` mit `openclaw.extensions` enthalten:

```json
{
  "name": "my-pack",
  "openclaw": {
    "extensions": ["./src/safety.ts", "./src/tools.ts"],
    "setupEntry": "./src/setup-entry.ts"
  }
}
```

Jeder Eintrag wird zu einem Plugin. Wenn das Pack mehrere Extensions auflistet, wird die Plugin-ID
zu `name/<fileBase>`.

Wenn Ihr Plugin npm-Abhängigkeiten importiert, installieren Sie sie in diesem Verzeichnis, damit
`node_modules` verfügbar ist (`npm install` / `pnpm install`).

Sicherheitsleitplanke: Jeder Eintrag in `openclaw.extensions` muss nach der Auflösung von Symlinks innerhalb des Plugin-
Verzeichnisses bleiben. Einträge, die das Paketverzeichnis verlassen, werden
abgelehnt.

Sicherheitshinweis: `openclaw plugins install` installiert Plugin-Abhängigkeiten mit
`npm install --omit=dev --ignore-scripts` (keine Lifecycle-Skripte, keine Dev-Abhängigkeiten zur Laufzeit). Halten Sie Plugin-Abhängigkeits-
Bäume „reines JS/TS“ und vermeiden Sie Pakete, die `postinstall`-Builds benötigen.

Optional: `openclaw.setupEntry` kann auf ein leichtgewichtiges Nur-Setup-Modul verweisen.
Wenn OpenClaw Setup-Oberflächen für ein deaktiviertes Kanal-Plugin benötigt oder
wenn ein Kanal-Plugin aktiviert, aber noch nicht konfiguriert ist, lädt es `setupEntry`
statt des vollständigen Plugin-Einstiegs. Das hält Start und Einrichtung leichter,
wenn Ihr Haupteinstieg außerdem Tools, Hooks oder anderen rein laufzeitbezogenen
Code verdrahtet.

Optional: `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`
kann ein Kanal-Plugin während der Phase vor `listen` beim Gateway-Start ebenfalls in denselben `setupEntry`-
Pfad opt-in versetzen, selbst wenn der Kanal bereits konfiguriert ist.

Verwenden Sie dies nur, wenn `setupEntry` die Startoberfläche vollständig abdeckt, die
existieren muss, bevor das Gateway zu lauschen beginnt. In der Praxis bedeutet das, dass der
Setup-Einstieg jede kanaleigene Fähigkeit registrieren muss, von der der Start abhängt, wie z. B.:

- die Kanalregistrierung selbst
- beliebige HTTP-Routen, die verfügbar sein müssen, bevor das Gateway zu lauschen beginnt
- beliebige Gateway-Methoden, Tools oder Services, die in diesem Zeitraum vorhanden sein müssen

Wenn Ihr vollständiger Einstieg noch eine erforderliche Startfähigkeit besitzt, aktivieren Sie
dieses Flag nicht. Behalten Sie das Standardverhalten bei und lassen Sie OpenClaw den
vollständigen Einstieg während des Starts laden.

Gebündelte Kanäle können auch nur-Setup-Helfer für Vertragsoberflächen veröffentlichen, die der Kern
abfragen kann, bevor die vollständige Kanal-Laufzeit geladen ist. Die aktuelle Oberfläche
für Setup-Promotion ist:

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

Der Kern nutzt diese Oberfläche, wenn er eine Legacy-Einzelkonto-Kanal-
Konfiguration in `channels.<id>.accounts.*` überführen muss, ohne den vollständigen Plugin-Einstieg zu laden.
Matrix ist das aktuelle gebündelte Beispiel: Es verschiebt nur Auth-/Bootstrap-Schlüssel in ein
benanntes hochgestuftes Konto, wenn bereits benannte Konten existieren, und es kann
einen konfigurierten nicht-kanonischen Standard-Kontoschlüssel beibehalten, statt immer
`accounts.default` zu erstellen.

Diese Setup-Patch-Adapter halten die Discovery gebündelter Vertragsoberflächen lazy. Die Importzeit
bleibt gering; die Promotionsoberfläche wird nur bei der ersten Verwendung geladen, statt beim Modulimport
erneut den Start gebündelter Kanäle zu betreten.

Wenn diese Startoberflächen Gateway-RPC-Methoden enthalten, behalten Sie sie auf einem
plugin-spezifischen Präfix. Kern-Admin-Namespaces (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) bleiben reserviert und werden immer
nach `operator.admin` aufgelöst, selbst wenn ein Plugin einen schmaleren Scope anfordert.

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

### Katalogmetadaten für Kanäle

Kanal-Plugins können Setup-/Discovery-Metadaten über `openclaw.channel` und
Installationshinweise über `openclaw.install` bekanntgeben. Dadurch bleiben die Katalogdaten des Kerns datenfrei.

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

Nützliche Felder in `openclaw.channel` über das Minimalbeispiel hinaus:

- `detailLabel`: sekundäres Label für reichhaltigere Katalog-/Statusoberflächen
- `docsLabel`: Linktext für den Dokumentationslink überschreiben
- `preferOver`: Plugin-/Kanal-IDs niedrigerer Priorität, die dieser Katalogeintrag übertreffen sollte
- `selectionDocsPrefix`, `selectionDocsOmitLabel`, `selectionExtras`: Steuerung von Texten auf Auswahloberflächen
- `markdownCapable`: markiert den Kanal für Entscheidungen zur Outbound-Formatierung als Markdown-fähig
- `exposure.configured`: blendet den Kanal aus Oberflächen mit konfigurierten Kanälen aus, wenn auf `false` gesetzt
- `exposure.setup`: blendet den Kanal aus interaktiven Setup-/Configure-Pickern aus, wenn auf `false` gesetzt
- `exposure.docs`: markiert den Kanal für Dokumentations-Navigationsoberflächen als intern/privat
- `showConfigured` / `showInSetup`: Legacy-Aliase werden aus Kompatibilitätsgründen weiterhin akzeptiert; bevorzugen Sie `exposure`
- `quickstartAllowFrom`: nimmt den Kanal in den Standard-Quickstart-Ablauf `allowFrom` auf
- `forceAccountBinding`: explizite Kontobindung erzwingen, selbst wenn nur ein Konto existiert
- `preferSessionLookupForAnnounceTarget`: Sitzungs-Lookup bei der Auflösung von Ankündigungszielen bevorzugen

OpenClaw kann auch **externe Kanalkataloge** zusammenführen (zum Beispiel einen Export aus einer MPM-
Registry). Legen Sie eine JSON-Datei an einem der folgenden Orte ab:

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

Oder setzen Sie `OPENCLAW_PLUGIN_CATALOG_PATHS` (oder `OPENCLAW_MPM_CATALOG_PATHS`) auf
eine oder mehrere JSON-Dateien (durch Komma/Semikolon/`PATH` getrennt). Jede Datei sollte
`{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }` enthalten. Der Parser akzeptiert auch `"packages"` oder `"plugins"` als Legacy-Aliase für den Schlüssel `"entries"`.

## Context-Engine-Plugins

Context-Engine-Plugins besitzen die Orchestrierung des Sitzungs-Kontexts für Ingest, Zusammenstellung
und Kompaktierung. Registrieren Sie sie aus Ihrem Plugin mit
`api.registerContextEngine(id, factory)` und wählen Sie dann die aktive Engine mit
`plugins.slots.contextEngine`.

Verwenden Sie dies, wenn Ihr Plugin die Standard-
Context-Pipeline ersetzen oder erweitern muss, statt nur Memory Search oder Hooks hinzuzufügen.

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

Wenn Ihre Engine den Kompaktierungsalgorithmus **nicht** besitzt, implementieren Sie `compact()`
trotzdem und delegieren Sie ihn explizit:

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
das Plugin-System nicht mit einem privaten Reach-in. Fügen Sie die fehlende Fähigkeit hinzu.

Empfohlene Reihenfolge:

1. den Kernvertrag definieren
   Entscheiden Sie, welches gemeinsame Verhalten der Kern besitzen soll: Richtlinie, Fallback, Konfigurations-Merge,
   Lebenszyklus, kanalorientierte Semantik und Form des Laufzeit-Helfers.
2. typisierte Oberflächen für Plugin-Registrierung/Laufzeit hinzufügen
   Erweitern Sie `OpenClawPluginApi` und/oder `api.runtime` um die kleinste nützliche
   typisierte Fähigkeitsoberfläche.
3. Kern + Kanal-/Feature-Konsumenten verdrahten
   Kanäle und Feature-Plugins sollten die neue Fähigkeit über den Kern konsumieren,
   nicht durch direkten Import einer Anbieterimplementierung.
4. Anbieterimplementierungen registrieren
   Anbieter-Plugins registrieren dann ihre Backends gegen die Fähigkeit.
5. Vertragsabdeckung hinzufügen
   Fügen Sie Tests hinzu, damit Ownership und Registrierungsform im Laufe der Zeit explizit bleiben.

So bleibt OpenClaw meinungsstark, ohne an die Sichtweise eines einzelnen
Providers hart gekoppelt zu werden. Eine konkrete Dateicheckliste und ein ausgearbeitetes Beispiel finden Sie im [Capability Cookbook](/de/plugins/architecture).

### Checkliste für Fähigkeiten

Wenn Sie eine neue Fähigkeit hinzufügen, sollte die Implementierung in der Regel diese
Oberflächen gemeinsam berühren:

- Kernvertragstypen in `src/<capability>/types.ts`
- Kern-Runner/Laufzeit-Helper in `src/<capability>/runtime.ts`
- Plugin-API-Registrierungsoberfläche in `src/plugins/types.ts`
- Verdrahtung der Plugin-Registry in `src/plugins/registry.ts`
- Bereitstellung der Plugin-Laufzeit in `src/plugins/runtime/*`, wenn Feature-/Kanal-
  Plugins sie konsumieren müssen
- Capture-/Test-Helper in `src/test-utils/plugin-registration.ts`
- Ownership-/Vertragsprüfungen in `src/plugins/contracts/registry.ts`
- Operator-/Plugin-Dokumentation in `docs/`

Wenn eine dieser Oberflächen fehlt, ist das in der Regel ein Zeichen dafür, dass die Fähigkeit
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

Das hält die Regel einfach:

- der Kern besitzt den Fähigkeitsvertrag + die Orchestrierung
- Anbieter-Plugins besitzen Anbieterimplementierungen
- Feature-/Kanal-Plugins konsumieren Laufzeit-Helfer
- Vertragstests halten Ownership explizit
