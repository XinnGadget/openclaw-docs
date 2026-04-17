---
read_when:
    - Native OpenClaw-Plugins erstellen oder debuggen
    - Das Fähigkeitsmodell von Plugins oder Eigentumsgrenzen verstehen
    - An der Lade-Pipeline oder der Registrierung von Plugins arbeiten
    - Provider-Laufzeit-Hooks oder Channel-Plugins implementieren
sidebarTitle: Internals
summary: 'Plugin-Interna: Fähigkeitsmodell, Besitzverhältnisse, Verträge, Lade-Pipeline und Laufzeit-Hilfsfunktionen'
title: Plugin-Interna
x-i18n:
    generated_at: "2026-04-15T06:21:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: f86798b5d2b0ad82d2397a52a6c21ed37fe6eee1dd3d124a9e4150c4f630b841
    source_path: plugins/architecture.md
    workflow: 15
---

# Plugin-Interna

<Info>
  Dies ist die **umfassende Architekturreferenz**. Praktische Anleitungen finden Sie hier:
  - [Plugins installieren und verwenden](/de/tools/plugin) — Benutzerhandbuch
  - [Erste Schritte](/de/plugins/building-plugins) — erstes Plugin-Tutorial
  - [Channel-Plugins](/de/plugins/sdk-channel-plugins) — einen Messaging-Channel erstellen
  - [Provider-Plugins](/de/plugins/sdk-provider-plugins) — einen Modell-Provider erstellen
  - [SDK-Überblick](/de/plugins/sdk-overview) — Importzuordnung und Registrierungs-API
</Info>

Diese Seite behandelt die interne Architektur des OpenClaw-Plugin-Systems.

## Öffentliches Fähigkeitsmodell

Fähigkeiten sind das öffentliche Modell für **native Plugins** innerhalb von OpenClaw. Jedes
native OpenClaw-Plugin registriert sich für einen oder mehrere Fähigkeitstypen:

| Fähigkeit              | Registrierungsmethode                           | Beispiel-Plugins                    |
| ---------------------- | ----------------------------------------------- | ----------------------------------- |
| Textinferenz           | `api.registerProvider(...)`                     | `openai`, `anthropic`               |
| CLI-Inferenz-Backend   | `api.registerCliBackend(...)`                   | `openai`, `anthropic`               |
| Sprache                | `api.registerSpeechProvider(...)`               | `elevenlabs`, `microsoft`           |
| Echtzeit-Transkription | `api.registerRealtimeTranscriptionProvider(...)` | `openai`                            |
| Echtzeit-Sprache       | `api.registerRealtimeVoiceProvider(...)`        | `openai`                            |
| Medienverständnis      | `api.registerMediaUnderstandingProvider(...)`   | `openai`, `google`                  |
| Bildgenerierung        | `api.registerImageGenerationProvider(...)`      | `openai`, `google`, `fal`, `minimax` |
| Musikgenerierung       | `api.registerMusicGenerationProvider(...)`      | `google`, `minimax`                 |
| Videogenerierung       | `api.registerVideoGenerationProvider(...)`      | `qwen`                              |
| Web-Abruf              | `api.registerWebFetchProvider(...)`             | `firecrawl`                         |
| Websuche               | `api.registerWebSearchProvider(...)`            | `google`                            |
| Channel / Messaging    | `api.registerChannel(...)`                      | `msteams`, `matrix`                 |

Ein Plugin, das null Fähigkeiten registriert, aber Hooks, Tools oder
Dienste bereitstellt, ist ein **altes reines Hook-Plugin**. Dieses Muster wird weiterhin vollständig unterstützt.

### Haltung zur externen Kompatibilität

Das Fähigkeitsmodell ist im Core angekommen und wird heute von gebündelten/nativen Plugins
verwendet, aber die Kompatibilität externer Plugins braucht weiterhin eine höhere Hürde als „es ist
exportiert, also ist es eingefroren“.

Aktuelle Richtlinie:

- **bestehende externe Plugins:** hook-basierte Integrationen funktionsfähig halten; behandeln Sie
  dies als Kompatibilitätsbasis
- **neue gebündelte/native Plugins:** explizite Fähigkeitsregistrierung gegenüber
  anbieterbezogenen Direktzugriffen oder neuen reinen Hook-Designs bevorzugen
- **externe Plugins, die Fähigkeitsregistrierung übernehmen:** erlaubt, aber die
  fähigkeitsspezifischen Hilfsoberflächen als in Entwicklung betrachten, sofern die Dokumentation einen
  Vertrag nicht ausdrücklich als stabil kennzeichnet

Praktische Regel:

- APIs zur Fähigkeitsregistrierung sind die vorgesehene Richtung
- alte Hooks bleiben während des Übergangs der sicherste Weg ohne Bruch für externe Plugins
- exportierte Hilfs-Subpfade sind nicht alle gleich; bevorzugen Sie den eng dokumentierten
  Vertrag, nicht zufällige Hilfsexporte

### Plugin-Formen

OpenClaw klassifiziert jedes geladene Plugin anhand seines tatsächlichen
Registrierungsverhaltens in eine Form (nicht nur anhand statischer Metadaten):

- **plain-capability** -- registriert genau einen Fähigkeitstyp (zum Beispiel ein
  reines Provider-Plugin wie `mistral`)
- **hybrid-capability** -- registriert mehrere Fähigkeitstypen (zum Beispiel
  besitzt `openai` Textinferenz, Sprache, Medienverständnis und Bildgenerierung)
- **hook-only** -- registriert nur Hooks (typisiert oder benutzerdefiniert), keine Fähigkeiten,
  Tools, Befehle oder Dienste
- **non-capability** -- registriert Tools, Befehle, Dienste oder Routen, aber keine
  Fähigkeiten

Verwenden Sie `openclaw plugins inspect <id>`, um die Form und die Fähigkeitsaufschlüsselung
eines Plugins anzuzeigen. Siehe [CLI-Referenz](/cli/plugins#inspect) für Details.

### Alte Hooks

Der Hook `before_agent_start` bleibt als Kompatibilitätspfad für
reine Hook-Plugins unterstützt. Reale ältere Plugins sind weiterhin davon abhängig.

Richtung:

- funktionsfähig halten
- als alt dokumentieren
- `before_model_resolve` für Arbeiten an Modell-/Provider-Überschreibungen bevorzugen
- `before_prompt_build` für Arbeiten an Prompt-Mutationen bevorzugen
- erst entfernen, wenn die tatsächliche Nutzung sinkt und die Fixture-Abdeckung die Migrationssicherheit belegt

### Kompatibilitätssignale

Wenn Sie `openclaw doctor` oder `openclaw plugins inspect <id>` ausführen, sehen Sie möglicherweise
eines dieser Labels:

| Signal                     | Bedeutung                                                   |
| -------------------------- | ----------------------------------------------------------- |
| **config valid**           | Die Konfiguration wird korrekt geparst und Plugins werden aufgelöst |
| **compatibility advisory** | Das Plugin verwendet ein unterstütztes, aber älteres Muster (z. B. `hook-only`) |
| **legacy warning**         | Das Plugin verwendet `before_agent_start`, was veraltet ist |
| **hard error**             | Die Konfiguration ist ungültig oder das Plugin konnte nicht geladen werden |

Weder `hook-only` noch `before_agent_start` werden Ihr Plugin heute beschädigen --
`hook-only` ist ein Hinweis, und `before_agent_start` löst nur eine Warnung aus. Diese
Signale erscheinen auch in `openclaw status --all` und `openclaw plugins doctor`.

## Architekturüberblick

Das Plugin-System von OpenClaw hat vier Ebenen:

1. **Manifest + Erkennung**
   OpenClaw findet mögliche Plugins aus konfigurierten Pfaden, Workspace-Wurzeln,
   globalen Erweiterungswurzeln und gebündelten Erweiterungen. Die Erkennung liest zuerst native
   `openclaw.plugin.json`-Manifeste sowie unterstützte Bundle-Manifeste.
2. **Aktivierung + Validierung**
   Der Core entscheidet, ob ein erkanntes Plugin aktiviert, deaktiviert, blockiert oder
   für einen exklusiven Slot wie Speicher ausgewählt ist.
3. **Laufzeitladen**
   Native OpenClaw-Plugins werden prozessintern über jiti geladen und registrieren
   Fähigkeiten in einer zentralen Registry. Kompatible Bundles werden in
   Registry-Einträge normalisiert, ohne Laufzeitcode zu importieren.
4. **Nutzung der Oberflächen**
   Der Rest von OpenClaw liest die Registry, um Tools, Channels, Provider-
   Einrichtung, Hooks, HTTP-Routen, CLI-Befehle und Dienste bereitzustellen.

Speziell für die Plugin-CLI ist die Erkennung von Root-Befehlen in zwei Phasen aufgeteilt:

- Parsezeit-Metadaten stammen aus `registerCli(..., { descriptors: [...] })`
- das eigentliche Plugin-CLI-Modul kann lazy bleiben und sich beim ersten Aufruf registrieren

Dadurch bleibt plugin-eigener CLI-Code innerhalb des Plugins, während OpenClaw dennoch
Root-Befehlsnamen vor dem Parsen reservieren kann.

Die wichtige Entwurfsgrenze:

- Erkennung + Konfigurationsvalidierung sollten aus **Manifest-/Schema-Metadaten**
  funktionieren, ohne Plugin-Code auszuführen
- natives Laufzeitverhalten stammt aus dem Pfad `register(api)` des Plugin-Moduls

Diese Aufteilung ermöglicht es OpenClaw, Konfigurationen zu validieren, fehlende/deaktivierte Plugins zu erklären und
UI-/Schema-Hinweise zu erzeugen, bevor die vollständige Laufzeit aktiv ist.

### Channel-Plugins und das gemeinsame Nachrichtentool

Channel-Plugins müssen für normale Chat-Aktionen kein separates Tool zum Senden/Bearbeiten/Reagieren registrieren.
OpenClaw behält ein gemeinsames `message`-Tool im Core, und
Channel-Plugins besitzen die channelspezifische Erkennung und Ausführung dahinter.

Die aktuelle Grenze ist:

- der Core besitzt den gemeinsamen `message`-Tool-Host, Prompt-Verdrahtung, Sitzungs-/Thread-
  Buchführung und Ausführungs-Dispatch
- Channel-Plugins besitzen die bereichsbezogene Aktionserkennung, Fähigkeitserkennung und alle
  channelspezifischen Schemafragmente
- Channel-Plugins besitzen die provider-spezifische Sitzungs-Konversationsgrammatik, also zum Beispiel,
  wie Konversations-IDs Thread-IDs codieren oder von übergeordneten Konversationen erben
- Channel-Plugins führen die endgültige Aktion über ihren Aktionsadapter aus

Für Channel-Plugins ist die SDK-Oberfläche
`ChannelMessageActionAdapter.describeMessageTool(...)`. Dieser vereinheitlichte Erkennungsaufruf
ermöglicht es einem Plugin, seine sichtbaren Aktionen, Fähigkeiten und Schema-
Beiträge gemeinsam zurückzugeben, damit diese Teile nicht auseinanderdriften.

Wenn ein channelspezifischer Message-Tool-Parameter eine Medienquelle wie einen
lokalen Pfad oder eine Remote-Medien-URL trägt, sollte das Plugin außerdem
`mediaSourceParams` von `describeMessageTool(...)` zurückgeben. Der Core verwendet diese explizite
Liste, um Sandbox-Pfadnormalisierung und Hinweise für ausgehenden Medienzugriff anzuwenden,
ohne plugin-eigene Parameternamen hart zu codieren.
Bevorzugen Sie dort aktionsbezogene Zuordnungen statt einer flachen kanalweiten Liste,
damit ein nur für Profile vorgesehener Medienparameter nicht bei nicht verwandten Aktionen wie
`send` normalisiert wird.

Der Core übergibt Laufzeitkontext in diesen Erkennungsschritt. Wichtige Felder sind:

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- vertrauenswürdige eingehende `requesterSenderId`

Das ist für kontextsensitive Plugins wichtig. Ein Channel kann Nachrichtenaktionen
abhängig vom aktiven Konto, dem aktuellen Raum/Thread/Nachricht oder der
vertrauenswürdigen Identität des Anfragenden ausblenden oder sichtbar machen, ohne
channelspezifische Verzweigungen im Core-`message`-Tool hart zu codieren.

Deshalb sind eingebettete Runner-Routing-Änderungen weiterhin Plugin-Arbeit: Der Runner ist
dafür verantwortlich, die aktuelle Chat-/Sitzungsidentität an die Plugin-
Erkennungsgrenze weiterzuleiten, damit das gemeinsame `message`-Tool die richtige
plugin-eigene Channel-Oberfläche für den aktuellen Turn bereitstellt.

Für Channel-eigene Ausführungs-Hilfsfunktionen sollten gebündelte Plugins die Ausführungs-
Laufzeit innerhalb ihrer eigenen Erweiterungsmodule halten. Der Core besitzt die Discord-,
Slack-, Telegram- oder WhatsApp-Nachrichtenaktions-Laufzeiten unter `src/agents/tools` nicht mehr.
Wir veröffentlichen keine separaten `plugin-sdk/*-action-runtime`-Subpfade, und gebündelte
Plugins sollten ihren eigenen lokalen Laufzeitcode direkt aus ihren
erweiterungseigenen Modulen importieren.

Dieselbe Grenze gilt allgemein für providerbenannte SDK-Seams: Der Core sollte
keine channelspezifischen Convenience-Barrels für Slack, Discord, Signal,
WhatsApp oder ähnliche Erweiterungen importieren. Wenn der Core ein Verhalten benötigt,
soll er entweder das eigene Barrel `api.ts` / `runtime-api.ts` des gebündelten Plugins verwenden oder
den Bedarf in eine enge generische Fähigkeit im gemeinsamen SDK überführen.

Speziell für Umfragen gibt es zwei Ausführungspfade:

- `outbound.sendPoll` ist die gemeinsame Baseline für Channels, die zum gemeinsamen
  Umfragemodell passen
- `actions.handleAction("poll")` ist der bevorzugte Pfad für channelspezifische
  Umfragesemantik oder zusätzliche Umfrageparameter

Der Core verschiebt das gemeinsame Umfrage-Parsen jetzt, bis der Plugin-Umfrage-Dispatch
die Aktion ablehnt, sodass plugin-eigene Umfrage-Handler channelspezifische Umfragefelder akzeptieren können,
ohne vorher durch den generischen Umfrage-Parser blockiert zu werden.

Siehe [Lade-Pipeline](#load-pipeline) für die vollständige Startsequenz.

## Modell zur Besitzerschaft von Fähigkeiten

OpenClaw behandelt ein natives Plugin als Besitzgrenze für ein **Unternehmen** oder ein
**Feature**, nicht als Sammelsurium unzusammenhängender Integrationen.

Das bedeutet:

- ein Unternehmens-Plugin sollte normalerweise alle OpenClaw-bezogenen
  Oberflächen dieses Unternehmens besitzen
- ein Feature-Plugin sollte normalerweise die vollständige Feature-Oberfläche besitzen, die es einführt
- Channels sollten gemeinsame Core-Fähigkeiten nutzen, statt Provider-Verhalten ad hoc neu zu implementieren

Beispiele:

- das gebündelte `openai`-Plugin besitzt das OpenAI-Modell-Provider-Verhalten sowie das OpenAI-Verhalten für
  Sprache + Echtzeit-Sprache + Medienverständnis + Bildgenerierung
- das gebündelte `elevenlabs`-Plugin besitzt das ElevenLabs-Sprachverhalten
- das gebündelte `microsoft`-Plugin besitzt das Microsoft-Sprachverhalten
- das gebündelte `google`-Plugin besitzt das Google-Modell-Provider-Verhalten sowie das Google-Verhalten für
  Medienverständnis + Bildgenerierung + Websuche
- das gebündelte `firecrawl`-Plugin besitzt das Firecrawl-Web-Abruf-Verhalten
- die gebündelten Plugins `minimax`, `mistral`, `moonshot` und `zai` besitzen ihre
  Backends für Medienverständnis
- das gebündelte `qwen`-Plugin besitzt das Qwen-Text-Provider-Verhalten sowie
  Medienverständnis- und Videogenerierungs-Verhalten
- das `voice-call`-Plugin ist ein Feature-Plugin: Es besitzt Anruftransport, Tools,
  CLI, Routen und Twilio-Medienstream-Bridge, nutzt aber gemeinsame Sprach-,
  Echtzeit-Transkriptions- und Echtzeit-Sprach-Fähigkeiten, statt
  Anbieter-Plugins direkt zu importieren

Der angestrebte Endzustand ist:

- OpenAI lebt in einem Plugin, auch wenn es Textmodelle, Sprache, Bilder und
  künftig Video umfasst
- ein anderer Anbieter kann dasselbe für seinen eigenen Oberflächenbereich tun
- Channels ist es egal, welches Anbieter-Plugin den Provider besitzt; sie nutzen den
  gemeinsamen Fähigkeitsvertrag, den der Core bereitstellt

Das ist der entscheidende Unterschied:

- **Plugin** = Besitzgrenze
- **Fähigkeit** = Core-Vertrag, den mehrere Plugins implementieren oder nutzen können

Wenn OpenClaw also einen neuen Bereich wie Video hinzufügt, lautet die erste Frage nicht
„welcher Provider soll die Videoverarbeitung hart codieren?“ Die erste Frage lautet: „wie sieht
der zentrale Video-Fähigkeitsvertrag aus?“ Sobald dieser Vertrag existiert, können sich
Anbieter-Plugins dafür registrieren und Channel-/Feature-Plugins ihn nutzen.

Wenn die Fähigkeit noch nicht existiert, ist der richtige Schritt normalerweise:

1. die fehlende Fähigkeit im Core definieren
2. sie typisiert über die Plugin-API/Laufzeit bereitstellen
3. Channels/Features gegen diese Fähigkeit verdrahten
4. Anbieter-Plugins Implementierungen registrieren lassen

So bleibt die Besitzerschaft explizit, während Core-Verhalten vermieden wird, das von einem
einzigen Anbieter oder einem einmaligen pluginspezifischen Codepfad abhängt.

### Fähigkeitsschichtung

Verwenden Sie dieses Denkmodell, wenn Sie entscheiden, wohin Code gehört:

- **Core-Fähigkeitsschicht**: gemeinsame Orchestrierung, Richtlinien, Fallback,
  Konfigurations-Zusammenführungsregeln, Auslieferungssemantik und typisierte Verträge
- **Anbieter-Plugin-Schicht**: anbieterbezogene APIs, Authentifizierung, Modellkataloge, Sprach-
  synthese, Bildgenerierung, künftige Video-Backends, Nutzungsendpunkte
- **Channel-/Feature-Plugin-Schicht**: Slack-/Discord-/voice-call-/usw.-Integration,
  die Core-Fähigkeiten nutzt und auf einer Oberfläche präsentiert

Zum Beispiel folgt TTS dieser Struktur:

- der Core besitzt die TTS-Richtlinie zur Antwortzeit, Fallback-Reihenfolge, Präferenzen und Channel-Auslieferung
- `openai`, `elevenlabs` und `microsoft` besitzen die Synthese-Implementierungen
- `voice-call` nutzt die TTS-Laufzeit-Hilfsfunktion für Telefonie

Dasselbe Muster sollte für künftige Fähigkeiten bevorzugt werden.

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

Wichtig sind nicht die genauen Namen der Hilfsfunktionen. Die Struktur ist entscheidend:

- ein Plugin besitzt die Anbieteroberfläche
- der Core besitzt weiterhin die Fähigkeitsverträge
- Channels und Feature-Plugins nutzen `api.runtime.*`-Hilfsfunktionen, nicht Anbietercode
- Vertragstests können prüfen, dass das Plugin die Fähigkeiten registriert hat, die es
  beansprucht zu besitzen

### Fähigkeitsbeispiel: Videoverständnis

OpenClaw behandelt Bild-/Audio-/Videoverständnis bereits als eine gemeinsame
Fähigkeit. Dasselbe Besitzmodell gilt dort:

1. der Core definiert den Vertrag für Medienverständnis
2. Anbieter-Plugins registrieren `describeImage`, `transcribeAudio` und
   `describeVideo`, soweit zutreffend
3. Channels und Feature-Plugins nutzen das gemeinsame Core-Verhalten, statt
   direkt an Anbietercode verdrahtet zu sein

So werden die Video-Annahmen eines einzelnen Providers nicht in den Core eingebaut. Das Plugin besitzt
die Anbieteroberfläche; der Core besitzt den Fähigkeitsvertrag und das Fallback-Verhalten.

Videogenerierung verwendet bereits dieselbe Abfolge: Der Core besitzt den typisierten
Fähigkeitsvertrag und die Laufzeit-Hilfsfunktion, und Anbieter-Plugins registrieren
`api.registerVideoGenerationProvider(...)`-Implementierungen dagegen.

Benötigen Sie eine konkrete Checkliste für die Einführung? Siehe
[Capability Cookbook](/de/plugins/architecture).

## Verträge und Durchsetzung

Die Oberfläche der Plugin-API ist absichtlich typisiert und in
`OpenClawPluginApi` zentralisiert. Dieser Vertrag definiert die unterstützten Registrierungspunkte und
die Laufzeit-Hilfsfunktionen, auf die sich ein Plugin verlassen darf.

Warum das wichtig ist:

- Plugin-Autoren erhalten einen stabilen internen Standard
- der Core kann doppelte Besitzansprüche ablehnen, etwa wenn zwei Plugins dieselbe
  Provider-ID registrieren
- beim Start können umsetzbare Diagnosen für fehlerhafte Registrierungen angezeigt werden
- Vertragstests können die Besitzerschaft gebündelter Plugins durchsetzen und stilles Drift verhindern

Es gibt zwei Ebenen der Durchsetzung:

1. **Durchsetzung der Laufzeitregistrierung**
   Die Plugin-Registry validiert Registrierungen, während Plugins geladen werden. Beispiele:
   doppelte Provider-IDs, doppelte Sprach-Provider-IDs und fehlerhafte
   Registrierungen erzeugen Plugin-Diagnosen statt undefinierten Verhaltens.
2. **Vertragstests**
   Gebündelte Plugins werden während Testläufen in Vertrags-Registries erfasst, damit
   OpenClaw die Besitzerschaft explizit prüfen kann. Heute wird dies für Modell-
   Provider, Sprach-Provider, Websuch-Provider und die Besitzerschaft gebündelter Registrierungen verwendet.

Die praktische Wirkung ist, dass OpenClaw von Anfang an weiß, welches Plugin welche
Oberfläche besitzt. Dadurch können Core und Channels nahtlos zusammenspielen, weil die
Besitzerschaft deklariert, typisiert und testbar ist, statt implizit zu sein.

### Was in einen Vertrag gehört

Gute Plugin-Verträge sind:

- typisiert
- klein
- fähigkeitsspezifisch
- im Besitz des Core
- von mehreren Plugins wiederverwendbar
- von Channels/Features ohne Anbieterwissen nutzbar

Schlechte Plugin-Verträge sind:

- anbieterbezogene Richtlinien, die im Core versteckt sind
- einmalige Plugin-Notausgänge, die die Registry umgehen
- Channel-Code, der direkt auf eine Anbieterimplementierung zugreift
- ad hoc-Laufzeitobjekte, die nicht Teil von `OpenClawPluginApi` oder
  `api.runtime` sind

Im Zweifel sollte die Abstraktionsebene angehoben werden: Definieren Sie zuerst die Fähigkeit und lassen Sie dann Plugins daran andocken.

## Ausführungsmodell

Native OpenClaw-Plugins laufen **im Prozess** mit dem Gateway. Sie sind nicht
sandboxed. Ein geladenes natives Plugin hat dieselbe Vertrauensgrenze auf Prozessebene wie
Core-Code.

Folgen:

- ein natives Plugin kann Tools, Netzwerk-Handler, Hooks und Dienste registrieren
- ein Fehler in einem nativen Plugin kann das Gateway zum Absturz bringen oder destabilisieren
- ein bösartiges natives Plugin entspricht beliebiger Codeausführung innerhalb des
  OpenClaw-Prozesses

Kompatible Bundles sind standardmäßig sicherer, weil OpenClaw sie derzeit
als Metadaten-/Inhaltspakete behandelt. In aktuellen Releases bedeutet das überwiegend gebündelte
Skills.

Verwenden Sie Zulassungslisten und explizite Installations-/Ladepfade für nicht gebündelte Plugins. Behandeln Sie
Workspace-Plugins als Code für die Entwicklungszeit, nicht als Produktionsstandard.

Bei gebündelten Workspace-Paketnamen sollte die Plugin-ID im npm-
Namen verankert bleiben: standardmäßig `@openclaw/<id>` oder ein genehmigtes typisiertes Suffix wie
`-provider`, `-plugin`, `-speech`, `-sandbox` oder `-media-understanding`, wenn
das Paket absichtlich eine engere Plugin-Rolle bereitstellt.

Wichtiger Hinweis zum Vertrauensmodell:

- `plugins.allow` vertraut **Plugin-IDs**, nicht der Herkunft der Quelle.
- Ein Workspace-Plugin mit derselben ID wie ein gebündeltes Plugin überschattet
  absichtlich die gebündelte Kopie, wenn dieses Workspace-Plugin aktiviert/auf die Zulassungsliste gesetzt ist.
- Das ist normal und nützlich für lokale Entwicklung, Patch-Tests und Hotfixes.

## Exportgrenze

OpenClaw exportiert Fähigkeiten, keine Implementierungs-Bequemlichkeit.

Halten Sie die Fähigkeitsregistrierung öffentlich. Reduzieren Sie nicht-vertragliche Hilfsexporte:

- Hilfs-Subpfade spezifisch für gebündelte Plugins
- Laufzeit-Plumbing-Subpfade, die nicht als öffentliche API gedacht sind
- anbieterbezogene Convenience-Hilfsfunktionen
- Einrichtungs-/Onboarding-Hilfsfunktionen, die Implementierungsdetails sind

Einige Hilfs-Subpfade gebündelter Plugins verbleiben aus Kompatibilitätsgründen und zur
Pflege gebündelter Plugins weiterhin in der generierten SDK-Exportzuordnung. Aktuelle Beispiele sind
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` und mehrere `plugin-sdk/matrix*`-Seams. Behandeln Sie diese als
reservierte Exporte für Implementierungsdetails, nicht als empfohlenes SDK-Muster für
neue Drittanbieter-Plugins.

## Lade-Pipeline

Beim Start macht OpenClaw grob Folgendes:

1. mögliche Plugin-Wurzeln erkennen
2. native oder kompatible Bundle-Manifeste und Paketmetadaten lesen
3. unsichere Kandidaten ablehnen
4. Plugin-Konfiguration normalisieren (`plugins.enabled`, `allow`, `deny`, `entries`,
   `slots`, `load.paths`)
5. Aktivierung für jeden Kandidaten entscheiden
6. aktivierte native Module über jiti laden
7. native Hooks `register(api)` (oder `activate(api)` — ein alter Alias) aufrufen und Registrierungen in der Plugin-Registry sammeln
8. die Registry für Befehle/Laufzeitoberflächen bereitstellen

<Note>
`activate` ist ein alter Alias für `register` — der Loader löst auf, was vorhanden ist (`def.register ?? def.activate`), und ruft es an derselben Stelle auf. Alle gebündelten Plugins verwenden `register`; für neue Plugins sollte `register` bevorzugt werden.
</Note>

Die Sicherheitsprüfungen erfolgen **vor** der Laufzeitausführung. Kandidaten werden blockiert,
wenn der Einstiegspunkt die Plugin-Wurzel verlässt, der Pfad weltweit beschreibbar ist oder die
Pfadbesitzverhältnisse bei nicht gebündelten Plugins verdächtig wirken.

### Manifest-zentriertes Verhalten

Das Manifest ist die Quelle der Wahrheit für die Steuerungsebene. OpenClaw verwendet es, um:

- das Plugin zu identifizieren
- deklarierte Channels/Skills/Konfigurationsschema oder Bundle-Fähigkeiten zu erkennen
- `plugins.entries.<id>.config` zu validieren
- Label/Platzhalter der Control UI zu erweitern
- Installations-/Katalog-Metadaten anzuzeigen
- günstige Aktivierungs- und Einrichtungsdeskriptoren zu erhalten, ohne die Plugin-Laufzeit zu laden

Für native Plugins ist das Laufzeitmodul der Teil der Datenebene. Es registriert
das tatsächliche Verhalten wie Hooks, Tools, Befehle oder Provider-Flows.

Optionale Manifest-Blöcke `activation` und `setup` bleiben auf der Steuerungsebene.
Sie sind reine Metadaten-Deskriptoren für Aktivierungsplanung und Einrichtungserkennung;
sie ersetzen weder die Laufzeitregistrierung, `register(...)` noch `setupEntry`.
Die ersten Live-Aktivierungs-Consumer nutzen jetzt Manifest-Hinweise zu Befehlen, Channels und Providern,
um das Laden von Plugins vor einer breiteren Materialisierung der Registry einzugrenzen:

- das CLI-Laden wird auf Plugins eingegrenzt, die den angeforderten primären Befehl besitzen
- die Auflösung von Channel-Einrichtung/Plugin wird auf Plugins eingegrenzt, die die angeforderte
  Channel-ID besitzen
- die explizite Auflösung von Provider-Einrichtung/Laufzeit wird auf Plugins eingegrenzt, die die
  angeforderte Provider-ID besitzen

Die Einrichtungs-Erkennung bevorzugt jetzt deskriptor-eigene IDs wie `setup.providers` und
`setup.cliBackends`, um Kandidaten-Plugins einzugrenzen, bevor auf
`setup-api` zurückgegriffen wird für Plugins, die weiterhin Laufzeit-Hooks zur Einrichtungszeit benötigen. Wenn mehr als
ein erkanntes Plugin dieselbe normalisierte Einrichtungs-Provider- oder CLI-Backend-
ID beansprucht, verweigert die Einrichtungsauflösung den mehrdeutigen Besitzer, statt sich auf die
Erkennungsreihenfolge zu verlassen.

### Was der Loader zwischenspeichert

OpenClaw behält kurze prozessinterne Caches für:

- Erkennungsergebnisse
- Daten der Manifest-Registry
- geladene Plugin-Registries

Diese Caches reduzieren burstartige Starts und den Overhead wiederholter Befehle. Sie können
sicher als kurzlebige Performance-Caches und nicht als Persistenz betrachtet werden.

Hinweis zur Performance:

- Setzen Sie `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` oder
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1`, um diese Caches zu deaktivieren.
- Passen Sie Cache-Fenster mit `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` und
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS` an.

## Registry-Modell

Geladene Plugins verändern nicht direkt beliebige globale Zustände im Core. Sie registrieren sich in einer
zentralen Plugin-Registry.

Die Registry verfolgt:

- Plugin-Einträge (Identität, Quelle, Herkunft, Status, Diagnosen)
- Tools
- alte Hooks und typisierte Hooks
- Channels
- Provider
- Gateway-RPC-Handler
- HTTP-Routen
- CLI-Registrare
- Hintergrunddienste
- plugin-eigene Befehle

Core-Features lesen dann aus dieser Registry, statt direkt mit Plugin-Modulen zu sprechen.
Dadurch bleibt das Laden unidirektional:

- Plugin-Modul -> Registrierung in der Registry
- Core-Laufzeit -> Nutzung der Registry

Diese Trennung ist für die Wartbarkeit wichtig. Sie bedeutet, dass die meisten Core-Oberflächen nur
einen Integrationspunkt brauchen: „die Registry lesen“, nicht „jedes Plugin-Modul speziell behandeln“.

## Callbacks für Konversationsbindung

Plugins, die eine Konversation binden, können reagieren, wenn eine Genehmigung aufgelöst wurde.

Verwenden Sie `api.onConversationBindingResolved(...)`, um einen Callback zu erhalten, nachdem eine Bindungsanfrage genehmigt oder abgelehnt wurde:

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
- `request`: die ursprüngliche Anfrageszusammenfassung, Trennhinweis, Sender-ID und
  Konversationsmetadaten

Dieser Callback dient nur zur Benachrichtigung. Er ändert nicht, wer eine Konversation
binden darf, und er läuft, nachdem die Genehmigungsbehandlung im Core abgeschlossen ist.

## Provider-Laufzeit-Hooks

Provider-Plugins haben jetzt zwei Ebenen:

- Manifest-Metadaten: `providerAuthEnvVars` für günstige Provider-Env-Auth-Abfrage
  vor dem Laden der Laufzeit, `providerAuthAliases` für Provider-Varianten, die sich
  Auth teilen, `channelEnvVars` für günstige Channel-Env-/Einrichtungsabfrage vor dem
  Laden der Laufzeit sowie `providerAuthChoices` für günstige Labels bei Onboarding/Auth-Auswahl und
  CLI-Flag-Metadaten vor dem Laden der Laufzeit
- Hooks zur Konfigurationszeit: `catalog` / altes `discovery` sowie `applyConfigDefaults`
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

OpenClaw besitzt weiterhin die generische Agent-Schleife, Failover, Transcript-Behandlung und
Tool-Richtlinien. Diese Hooks sind die Erweiterungsoberfläche für anbieterspezifisches Verhalten, ohne
einen vollständig benutzerdefinierten Inferenz-Transport zu benötigen.

Verwenden Sie das Manifest `providerAuthEnvVars`, wenn der Provider Env-basierte Zugangsdaten hat,
die generische Pfade für Auth/Status/Modellauswahl sehen sollen, ohne die Plugin-Laufzeit zu laden.
Verwenden Sie das Manifest `providerAuthAliases`, wenn eine Provider-ID die Env-Variablen,
Auth-Profile, config-gestützte Authentifizierung und die API-Key-Onboarding-Auswahl einer anderen
Provider-ID wiederverwenden soll. Verwenden Sie das Manifest `providerAuthChoices`, wenn Oberflächen für Onboarding/Auth-Auswahl in der
CLI die Auswahl-ID des Providers, Gruppenlabels und einfache
Authentifizierungsverdrahtung mit einem einzelnen Flag kennen sollen, ohne die Provider-Laufzeit zu laden. Behalten Sie die
Provider-Laufzeit-`envVars` für operatorseitige Hinweise wie Onboarding-Labels oder
Einrichtungsvariablen für OAuth-Client-ID/Client-Secret.

Verwenden Sie das Manifest `channelEnvVars`, wenn ein Channel env-gesteuerte Authentifizierung oder Einrichtung hat,
die generische Shell-Env-Fallbacks, Konfigurations-/Statusprüfungen oder Einrichtungsaufforderungen
sehen sollen, ohne die Channel-Laufzeit zu laden.

### Hook-Reihenfolge und Verwendung

Für Modell-/Provider-Plugins ruft OpenClaw Hooks in ungefähr dieser Reihenfolge auf.
Die Spalte „Wann verwenden“ ist der schnelle Entscheidungsleitfaden.

| #   | Hook                              | Funktion                                                                                                       | Wann verwenden                                                                                                                              |
| --- | --------------------------------- | -------------------------------------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `catalog`                         | Provider-Konfiguration während der Generierung von `models.json` in `models.providers` veröffentlichen         | Der Provider besitzt einen Katalog oder Standardwerte für `baseUrl`                                                                         |
| 2   | `applyConfigDefaults`             | Provider-eigene globale Konfigurationsstandardwerte während der Konfigurationsmaterialisierung anwenden        | Standardwerte hängen von Auth-Modus, Env oder der Semantik der Modellfamilie des Providers ab                                              |
| --  | _(integrierte Modellsuche)_       | OpenClaw versucht zuerst den normalen Registry-/Katalogpfad                                                    | _(kein Plugin-Hook)_                                                                                                                        |
| 3   | `normalizeModelId`                | Veraltete oder Vorschau-Aliase für Modell-IDs vor der Suche normalisieren                                      | Der Provider besitzt die Alias-Bereinigung vor der Auflösung kanonischer Modelle                                                            |
| 4   | `normalizeTransport`              | `api` / `baseUrl` einer Provider-Familie vor dem generischen Modellaufbau normalisieren                       | Der Provider besitzt die Transport-Bereinigung für benutzerdefinierte Provider-IDs in derselben Transportfamilie                           |
| 5   | `normalizeConfig`                 | `models.providers.<id>` vor der Laufzeit-/Provider-Auflösung normalisieren                                     | Der Provider braucht Konfigurationsbereinigung, die beim Plugin liegen sollte; gebündelte Hilfsfunktionen der Google-Familie stützen außerdem unterstützte Google-Konfigurationseinträge ab |
| 6   | `applyNativeStreamingUsageCompat` | Umschreibungen für native Streaming-Usage-Kompatibilität auf Konfigurations-Provider anwenden                  | Der Provider braucht endpunktgesteuerte Korrekturen an nativen Streaming-Usage-Metadaten                                                   |
| 7   | `resolveConfigApiKey`             | Authentifizierung über Env-Marker für Konfigurations-Provider vor dem Laden der Laufzeit-Authentifizierung auflösen | Der Provider besitzt eine provider-eigene Auflösung von API-Keys über Env-Marker; `amazon-bedrock` hat hier außerdem einen integrierten AWS-Env-Marker-Resolver |
| 8   | `resolveSyntheticAuth`            | Lokale/self-hosted oder konfigurationsgestützte Authentifizierung bereitstellen, ohne Klartext zu persistieren | Der Provider kann mit einem synthetischen/lokalen Zugangsdatenmarker arbeiten                                                               |
| 9   | `resolveExternalAuthProfiles`     | Provider-eigene externe Auth-Profile überlagern; der Standard für `persistence` ist `runtime-only` bei CLI-/app-eigenen Zugangsdaten | Der Provider verwendet externe Auth-Zugangsdaten wieder, ohne kopierte Refresh-Tokens zu persistieren                                      |
| 10  | `shouldDeferSyntheticProfileAuth` | Gespeicherte synthetische Profil-Platzhalter hinter env-/config-gestützte Authentifizierung zurückstufen      | Der Provider speichert synthetische Platzhalterprofile, die keine Priorität haben sollten                                                   |
| 11  | `resolveDynamicModel`             | Synchrones Fallback für provider-eigene Modell-IDs, die noch nicht in der lokalen Registry sind                | Der Provider akzeptiert beliebige Upstream-Modell-IDs                                                                                       |
| 12  | `prepareDynamicModel`             | Asynchrones Warm-up, danach läuft `resolveDynamicModel` erneut                                                 | Der Provider benötigt Netzwerkmetadaten, bevor unbekannte IDs aufgelöst werden können                                                       |
| 13  | `normalizeResolvedModel`          | Letzte Umschreibung, bevor der eingebettete Runner das aufgelöste Modell verwendet                             | Der Provider braucht Transport-Umschreibungen, nutzt aber weiterhin einen Core-Transport                                                    |
| 14  | `contributeResolvedModelCompat`   | Kompatibilitäts-Flags für Anbietermodelle hinter einem anderen kompatiblen Transport beitragen                 | Der Provider erkennt seine eigenen Modelle auf Proxy-Transporten, ohne den Provider zu übernehmen                                           |
| 15  | `capabilities`                    | Provider-eigene Transcript-/Tooling-Metadaten, die von gemeinsamer Core-Logik verwendet werden                | Der Provider braucht Besonderheiten bei Transcript oder Provider-Familie                                                                     |
| 16  | `normalizeToolSchemas`            | Tool-Schemas normalisieren, bevor der eingebettete Runner sie sieht                                            | Der Provider braucht Schema-Bereinigung für eine Transportfamilie                                                                           |
| 17  | `inspectToolSchemas`              | Provider-eigene Schema-Diagnosen nach der Normalisierung bereitstellen                                         | Der Provider möchte Keyword-Warnungen bereitstellen, ohne dem Core anbieterspezifische Regeln beizubringen                                 |
| 18  | `resolveReasoningOutputMode`      | Nativen oder getaggten Vertrag für Reasoning-Ausgaben auswählen                                                | Der Provider braucht getaggte Reasoning-/Final-Output-Ausgaben statt nativer Felder                                                        |
| 19  | `prepareExtraParams`              | Normalisierung von Anforderungsparametern vor generischen Stream-Options-Wrappern                              | Der Provider braucht Standard-Anforderungsparameter oder providerbezogene Bereinigung von Parametern                                        |
| 20  | `createStreamFn`                  | Den normalen Stream-Pfad vollständig durch einen benutzerdefinierten Transport ersetzen                        | Der Provider braucht ein benutzerdefiniertes Wire-Protocol, nicht nur einen Wrapper                                                         |
| 21  | `wrapStreamFn`                    | Stream-Wrapper, nachdem generische Wrapper angewendet wurden                                                   | Der Provider braucht Wrapper für Header/Body/Modell-Kompatibilität bei Anforderungen, ohne einen benutzerdefinierten Transport            |
| 22  | `resolveTransportTurnState`       | Native Header oder Metadaten pro Turn für den Transport anhängen                                               | Der Provider möchte, dass generische Transporte eine providereigene Turn-Identität senden                                                   |
| 23  | `resolveWebSocketSessionPolicy`   | Native WebSocket-Header oder Session-Cool-down-Richtlinie anhängen                                             | Der Provider möchte, dass generische WS-Transporte Session-Header oder Fallback-Richtlinien anpassen                                       |
| 24  | `formatApiKey`                    | Formatter für Auth-Profile: gespeichertes Profil wird zur Laufzeit-Zeichenfolge `apiKey`                      | Der Provider speichert zusätzliche Auth-Metadaten und braucht eine benutzerdefinierte Laufzeit-Tokenform                                   |
| 25  | `refreshOAuth`                    | OAuth-Refresh-Override für benutzerdefinierte Refresh-Endpunkte oder Richtlinien bei Refresh-Fehlern          | Der Provider passt nicht zu den gemeinsamen `pi-ai`-Refresh-Mechanismen                                                                     |
| 26  | `buildAuthDoctorHint`             | Reparaturhinweis, der angehängt wird, wenn OAuth-Refresh fehlschlägt                                           | Der Provider braucht provider-eigene Hinweise zur Auth-Reparatur nach einem Refresh-Fehler                                                  |
| 27  | `matchesContextOverflowError`     | Provider-eigener Matcher für Überschreitungen des Kontextfensters                                              | Der Provider hat rohe Overflow-Fehler, die generische Heuristiken übersehen würden                                                         |
| 28  | `classifyFailoverReason`          | Provider-eigene Klassifikation des Failover-Grundes                                                            | Der Provider kann rohe API-/Transportfehler auf Rate-Limit/Überlast/etc. abbilden                                                          |
| 29  | `isCacheTtlEligible`              | Prompt-Cache-Richtlinie für Proxy-/Backhaul-Provider                                                           | Der Provider braucht Proxy-spezifische Steuerung für Cache-TTL                                                                              |
| 30  | `buildMissingAuthMessage`         | Ersatz für die generische Wiederherstellungsnachricht bei fehlender Authentifizierung                          | Der Provider braucht einen provider-spezifischen Wiederherstellungshinweis bei fehlender Authentifizierung                                  |
| 31  | `suppressBuiltInModel`            | Unterdrückung veralteter Upstream-Modelle plus optionaler benutzerseitiger Fehlerhinweis                      | Der Provider muss veraltete Upstream-Zeilen ausblenden oder durch einen Anbieterhinweis ersetzen                                            |
| 32  | `augmentModelCatalog`             | Synthetische/endgültige Katalogzeilen, die nach der Erkennung angehängt werden                                | Der Provider braucht synthetische Forward-Compat-Zeilen in `models list` und Auswahllisten                                                  |
| 33  | `isBinaryThinking`                | Reasoning-Umschalter Ein/Aus für Provider mit binärem Denken                                                   | Der Provider bietet nur binäres Denken Ein/Aus an                                                                                           |
| 34  | `supportsXHighThinking`           | Unterstützung von `xhigh`-Reasoning für ausgewählte Modelle                                                    | Der Provider möchte `xhigh` nur für eine Teilmenge von Modellen                                                                             |
| 35  | `resolveDefaultThinkingLevel`     | Standardstufe für `/think` für eine bestimmte Modellfamilie auflösen                                           | Der Provider besitzt die Standardrichtlinie für `/think` für eine Modellfamilie                                                             |
| 36  | `isModernModelRef`                | Matcher für moderne Modelle für Live-Profilfilter und Smoke-Auswahl                                            | Der Provider besitzt die Zuordnung bevorzugter Modelle für Live-/Smoke-Läufe                                                                |
| 37  | `prepareRuntimeAuth`              | Ein konfiguriertes Zugangsdatenobjekt direkt vor der Inferenz in das tatsächliche Laufzeit-Token/den Schlüssel umwandeln | Der Provider braucht einen Tokenaustausch oder kurzlebige Zugangsdaten für Anforderungen                                                   |
| 38  | `resolveUsageAuth`                | Zugangsdaten für Nutzung/Abrechnung für `/usage` und verwandte Statusoberflächen auflösen                      | Der Provider braucht benutzerdefiniertes Parsing von Nutzungs-/Kontingent-Token oder andere Zugangsdaten für Nutzung                       |
| 39  | `fetchUsageSnapshot`              | Providerspezifische Nutzungs-/Kontingent-Snapshots abrufen und normalisieren, nachdem die Authentifizierung aufgelöst wurde | Der Provider braucht einen providerspezifischen Nutzungsendpunkt oder Payload-Parser                                                       |
| 40  | `createEmbeddingProvider`         | Einen provider-eigenen Embedding-Adapter für Speicher/Suche erstellen                                          | Verhalten für Speicher-Embeddings gehört zum Provider-Plugin                                                                                |
| 41  | `buildReplayPolicy`               | Eine Replay-Richtlinie zurückgeben, die die Transcript-Behandlung für den Provider steuert                     | Der Provider braucht eine benutzerdefinierte Transcript-Richtlinie (zum Beispiel das Entfernen von Thinking-Blöcken)                       |
| 42  | `sanitizeReplayHistory`           | Replay-Verlauf nach der generischen Transcript-Bereinigung umschreiben                                         | Der Provider braucht providerspezifische Replay-Umschreibungen über gemeinsame Compaction-Hilfsfunktionen hinaus                           |
| 43  | `validateReplayTurns`             | Finale Validierung oder Umformung von Replay-Turns vor dem eingebetteten Runner                                | Der Provider-Transport braucht nach der generischen Bereinigung eine strengere Turn-Validierung                                            |
| 44  | `onModelSelected`                 | Provider-eigene Nebeneffekte nach der Auswahl ausführen                                                        | Der Provider braucht Telemetrie oder provider-eigenen Zustand, wenn ein Modell aktiv wird                                                  |

`normalizeModelId`, `normalizeTransport` und `normalizeConfig` prüfen zuerst das
zugeordnete Provider-Plugin und fallen dann auf andere Hook-fähige Provider-Plugins
zurück, bis eines die Modell-ID oder den Transport/die Konfiguration tatsächlich ändert. So bleiben
Alias-/Kompatibilitäts-Shims für Provider funktionsfähig, ohne dass der Aufrufer wissen muss, welches
gebündelte Plugin die Umschreibung besitzt. Wenn kein Provider-Hook einen unterstützten
Konfigurationseintrag der Google-Familie umschreibt, wendet der gebündelte Google-Konfigurationsnormalisierer
diese Kompatibilitätsbereinigung weiterhin an.

Wenn der Provider ein vollständig benutzerdefiniertes Wire-Protocol oder einen benutzerdefinierten
Request-Executor benötigt, ist das eine andere Klasse von Erweiterung. Diese Hooks sind für Provider-Verhalten gedacht,
das weiterhin in der normalen Inferenzschleife von OpenClaw läuft.

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
  und `wrapStreamFn`, weil es Claude-4.6-Forward-Compat,
  Hinweise zur Provider-Familie, Auth-Reparaturhinweise, Integration des
  Nutzungsendpunkts, Prompt-Cache-Eignung, auth-bewusste Konfigurationsstandardwerte, die
  Claude-Standard-/adaptive Thinking-Richtlinie und Anthropic-spezifische Stream-Formung für
  Beta-Header, `/fast` / `serviceTier` und `context1m` besitzt.
- Anthropic-spezifische Stream-Hilfsfunktionen für Claude bleiben vorerst im eigenen
  öffentlichen Seam `api.ts` / `contract-api.ts` des gebündelten Plugins. Diese Paketoberfläche
  exportiert `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
  `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` und die niedrigstufigen
  Anthropic-Wrapper-Builder, statt das generische SDK rund um die
  Beta-Header-Regeln eines einzelnen Providers zu erweitern.
- OpenAI verwendet `resolveDynamicModel`, `normalizeResolvedModel` und
  `capabilities` sowie `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `supportsXHighThinking` und `isModernModelRef`,
  weil es GPT-5.4-Forward-Compat, die direkte OpenAI-
  Normalisierung `openai-completions` -> `openai-responses`, Codex-bewusste Auth-
  Hinweise, Spark-Unterdrückung, synthetische OpenAI-Listenzeilen und die Thinking-/
  Live-Modell-Richtlinie für GPT-5 besitzt; die Stream-Familie `openai-responses-defaults` besitzt die
  gemeinsamen nativen OpenAI-Responses-Wrapper für Zuordnungs-Header,
  `/fast`/`serviceTier`, Textausführlichkeit, native Codex-Websuche,
  Reasoning-Compat-Payload-Formung und Responses-Kontextverwaltung.
- OpenRouter verwendet `catalog` sowie `resolveDynamicModel` und
  `prepareDynamicModel`, weil der Provider ein Pass-through ist und neue
  Modell-IDs verfügbar machen kann, bevor der statische Katalog von OpenClaw aktualisiert wird; außerdem verwendet er
  `capabilities`, `wrapStreamFn` und `isCacheTtlEligible`, damit
  providerspezifische Request-Header, Routing-Metadaten, Reasoning-Patches und
  Prompt-Cache-Richtlinien aus dem Core herausgehalten werden. Seine Replay-Richtlinie stammt aus der
  Familie `passthrough-gemini`, während die Stream-Familie `openrouter-thinking`
  die Proxy-Reasoning-Injektion sowie die Sprünge für nicht unterstützte Modelle / `auto` besitzt.
- GitHub Copilot verwendet `catalog`, `auth`, `resolveDynamicModel` und
  `capabilities` sowie `prepareRuntimeAuth` und `fetchUsageSnapshot`, weil es
  provider-eigenen Device-Login, Modell-Fallback-Verhalten, Claude-Transcript-
  Besonderheiten, einen GitHub-Token -> Copilot-Token-Austausch und einen provider-eigenen Nutzungsendpunkt benötigt.
- OpenAI Codex verwendet `catalog`, `resolveDynamicModel`,
  `normalizeResolvedModel`, `refreshOAuth` und `augmentModelCatalog` sowie
  `prepareExtraParams`, `resolveUsageAuth` und `fetchUsageSnapshot`, weil es
  weiterhin auf zentralen OpenAI-Transporten läuft, aber seine Transport-/`baseUrl`-
  Normalisierung, OAuth-Refresh-Fallback-Richtlinie, Standardwahl des Transports,
  synthetische Codex-Katalogzeilen und die Integration des ChatGPT-Nutzungsendpunkts besitzt; es
  teilt dieselbe Stream-Familie `openai-responses-defaults` wie direktes OpenAI.
- Google AI Studio und Gemini CLI OAuth verwenden `resolveDynamicModel`,
  `buildReplayPolicy`, `sanitizeReplayHistory`,
  `resolveReasoningOutputMode`, `wrapStreamFn` und `isModernModelRef`, weil die
  Replay-Familie `google-gemini` Gemini-3.1-Forward-Compat-Fallback,
  native Gemini-Replay-Validierung, Bootstrap-Replay-Bereinigung, den Modus für getaggte
  Reasoning-Ausgaben und modernes Modell-Matching besitzt, während die
  Stream-Familie `google-thinking` die Normalisierung von Gemini-Thinking-Payloads besitzt;
  Gemini CLI OAuth verwendet außerdem `formatApiKey`, `resolveUsageAuth` und
  `fetchUsageSnapshot` für Tokenformatierung, Token-Parsing und das Verdrahten des
  Kontingent-Endpunkts.
- Anthropic Vertex verwendet `buildReplayPolicy` über die
  Replay-Familie `anthropic-by-model`, sodass die Claude-spezifische Replay-Bereinigung auf
  Claude-IDs begrenzt bleibt statt auf jeden Transport `anthropic-messages`.
- Amazon Bedrock verwendet `buildReplayPolicy`, `matchesContextOverflowError`,
  `classifyFailoverReason` und `resolveDefaultThinkingLevel`, weil es
  Bedrock-spezifische Klassifikation von Throttle-/Not-ready-/Context-Overflow-Fehlern
  für Anthropic-on-Bedrock-Datenverkehr besitzt; seine Replay-Richtlinie teilt dennoch denselben
  nur für Claude geltenden Guard `anthropic-by-model`.
- OpenRouter, Kilocode, Opencode und Opencode Go verwenden `buildReplayPolicy`
  über die Replay-Familie `passthrough-gemini`, weil sie Gemini-
  Modelle über OpenAI-kompatible Transporte proxien und Gemini-
  Thought-Signature-Bereinigung ohne native Gemini-Replay-Validierung oder
  Bootstrap-Umschreibungen benötigen.
- MiniMax verwendet `buildReplayPolicy` über die
  Replay-Familie `hybrid-anthropic-openai`, weil ein Provider sowohl
  Anthropic-Message- als auch OpenAI-kompatible Semantik besitzt; dabei bleibt das
  nur für Claude geltende Entfernen von Thinking-Blöcken auf der Anthropic-Seite, während der Modus für Reasoning-
  Ausgaben auf nativ zurückgesetzt wird, und die Stream-Familie `minimax-fast-mode` besitzt
  Umschreibungen für Fast-Mode-Modelle auf dem gemeinsamen Stream-Pfad.
- Moonshot verwendet `catalog` sowie `wrapStreamFn`, weil es weiterhin den gemeinsamen
  OpenAI-Transport nutzt, aber providerspezifische Normalisierung von Thinking-Payloads benötigt; die
  Stream-Familie `moonshot-thinking` bildet Konfiguration und Zustand von `/think` auf ihre
  native Payload für binäres Thinking ab.
- Kilocode verwendet `catalog`, `capabilities`, `wrapStreamFn` und
  `isCacheTtlEligible`, weil es provider-eigene Request-Header,
  Reasoning-Payload-Normalisierung, Gemini-Transcript-Hinweise und Anthropic-
  Cache-TTL-Steuerung benötigt; die Stream-Familie `kilocode-thinking` hält die Kilo-Thinking-
  Injektion auf dem gemeinsamen Proxy-Stream-Pfad, während `kilo/auto` und
  andere Proxy-Modell-IDs ausgelassen werden, die keine expliziten Reasoning-Payloads unterstützen.
- Z.AI verwendet `resolveDynamicModel`, `prepareExtraParams`, `wrapStreamFn`,
  `isCacheTtlEligible`, `isBinaryThinking`, `isModernModelRef`,
  `resolveUsageAuth` und `fetchUsageSnapshot`, weil es GLM-5-Fallback,
  Standardwerte für `tool_stream`, UX für binäres Thinking, modernes Modell-Matching sowie sowohl
  Nutzungs-Auth als auch das Abrufen von Kontingenten besitzt; die Stream-Familie `tool-stream-default-on` hält
  den standardmäßig aktivierten `tool_stream`-Wrapper aus handgeschriebenem pro-Provider-Glue heraus.
- xAI verwendet `normalizeResolvedModel`, `normalizeTransport`,
  `contributeResolvedModelCompat`, `prepareExtraParams`, `wrapStreamFn`,
  `resolveSyntheticAuth`, `resolveDynamicModel` und `isModernModelRef`,
  weil es native xAI-Responses-Transportnormalisierung, Umschreibungen von Grok-Fast-Mode-
  Aliasen, Standard-`tool_stream`, Bereinigung von Strict-Tool / Reasoning-Payload,
  Wiederverwendung von Fallback-Auth für plugin-eigene Tools, Forward-Compat-Auflösung von Grok-
  Modellen und provider-eigene Kompatibilitätspatches wie das xAI-Tool-Schema-
  Profil, nicht unterstützte Schema-Keywords, natives `web_search` und das Decodieren von HTML-Entities in
  Argumenten von Tool-Aufrufen besitzt.
- Mistral, OpenCode Zen und OpenCode Go verwenden nur `capabilities`, um
  Transcript-/Tooling-Besonderheiten aus dem Core herauszuhalten.
- Gebündelte Provider nur mit Katalog wie `byteplus`, `cloudflare-ai-gateway`,
  `huggingface`, `kimi-coding`, `nvidia`, `qianfan`,
  `synthetic`, `together`, `venice`, `vercel-ai-gateway` und `volcengine` verwenden
  nur `catalog`.
- Qwen verwendet `catalog` für seinen Text-Provider sowie gemeinsame Registrierungen für Medienverständnis und
  Videogenerierung für seine multimodalen Oberflächen.
- MiniMax und Xiaomi verwenden `catalog` sowie Usage-Hooks, weil ihr `/usage`-
  Verhalten plugin-eigen ist, obwohl die Inferenz weiterhin über die gemeinsamen Transporte läuft.

## Laufzeit-Hilfsfunktionen

Plugins können über `api.runtime` auf ausgewählte Hilfsfunktionen des Core zugreifen. Für TTS:

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

- `textToSpeech` gibt die normale Core-TTS-Ausgabe-Payload für Datei-/Sprachnotiz-Oberflächen zurück.
- Verwendet die zentrale Konfiguration `messages.tts` und Provider-Auswahl.
- Gibt einen PCM-Audiopuffer + Abtastrate zurück. Plugins müssen für Provider neu sampeln/kodieren.
- `listVoices` ist optional pro Provider. Verwenden Sie es für provider-eigene Stimmauswahl oder Einrichtungsabläufe.
- Sprachlisten können reichere Metadaten wie Gebietsschema, Geschlecht und Personality-Tags für providerbewusste Auswahlen enthalten.
- OpenAI und ElevenLabs unterstützen heute Telefonie. Microsoft nicht.

Plugins können außerdem Sprach-Provider über `api.registerSpeechProvider(...)` registrieren.

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

- Behalten Sie TTS-Richtlinien, Fallback und Antwortauslieferung im Core.
- Verwenden Sie Sprach-Provider für anbieter-eigenes Syntheseverhalten.
- Der alte Microsoft-Input `edge` wird auf die Provider-ID `microsoft` normalisiert.
- Das bevorzugte Besitzmodell ist unternehmensorientiert: Ein Anbieter-Plugin kann
  Text-, Sprach-, Bild- und künftige Medien-Provider besitzen, wenn OpenClaw diese
  Fähigkeitsverträge hinzufügt.

Für Bild-/Audio-/Videoverständnis registrieren Plugins einen typisierten
Provider für Medienverständnis statt eines generischen Key/Value-Bags:

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

- Behalten Sie Orchestrierung, Fallback, Konfiguration und Channel-Verdrahtung im Core.
- Behalten Sie Anbieterverhalten im Provider-Plugin.
- Additive Erweiterungen sollten typisiert bleiben: neue optionale Methoden, neue optionale
  Ergebnisfelder, neue optionale Fähigkeiten.
- Videogenerierung folgt bereits demselben Muster:
  - der Core besitzt den Fähigkeitsvertrag und die Laufzeit-Hilfsfunktion
  - Anbieter-Plugins registrieren `api.registerVideoGenerationProvider(...)`
  - Feature-/Channel-Plugins nutzen `api.runtime.videoGeneration.*`

Für Laufzeit-Hilfsfunktionen für Medienverständnis können Plugins Folgendes aufrufen:

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

Für Audio-Transkription können Plugins entweder die Laufzeit für Medienverständnis
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
- Verwendet die zentrale Audiokonfiguration für Medienverständnis (`tools.media.audio`) und die Fallback-Reihenfolge der Provider.
- Gibt `{ text: undefined }` zurück, wenn keine Transkriptionsausgabe erzeugt wird (zum Beispiel bei übersprungener/nicht unterstützter Eingabe).
- `api.runtime.stt.transcribeAudioFile(...)` bleibt als Kompatibilitätsalias bestehen.

Plugins können außerdem Hintergrundläufe von Subagents über `api.runtime.subagent` starten:

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
- Für plugin-eigene Fallback-Läufe müssen Operatoren sich mit `plugins.entries.<id>.subagent.allowModelOverride: true` explizit dafür entscheiden.
- Verwenden Sie `plugins.entries.<id>.subagent.allowedModels`, um vertrauenswürdige Plugins auf bestimmte kanonische Ziele `provider/model` zu beschränken, oder `"*"`, um jedes Ziel explizit zu erlauben.
- Nicht vertrauenswürdige Subagent-Läufe von Plugins funktionieren weiterhin, aber Überschreibungsanfragen werden abgelehnt, statt stillschweigend auf Fallback zurückzufallen.

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

Plugins können Websuch-Provider außerdem über
`api.registerWebSearchProvider(...)` registrieren.

Hinweise:

- Behalten Sie Providerauswahl, Auflösung von Zugangsdaten und gemeinsame Anfragesemantik im Core.
- Verwenden Sie Websuch-Provider für anbieterbezogene Suchtransporte.
- `api.runtime.webSearch.*` ist die bevorzugte gemeinsame Oberfläche für Feature-/Channel-Plugins, die Suchverhalten benötigen, ohne von dem Agent-Tool-Wrapper abhängig zu sein.

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
- `auth`: erforderlich. Verwenden Sie `"gateway"`, um normale Gateway-Authentifizierung zu verlangen, oder `"plugin"` für pluginverwaltete Authentifizierung/Webhook-Verifikation.
- `match`: optional. `"exact"` (Standard) oder `"prefix"`.
- `replaceExisting`: optional. Erlaubt demselben Plugin, seine eigene bestehende Routenregistrierung zu ersetzen.
- `handler`: gibt `true` zurück, wenn die Route die Anfrage verarbeitet hat.

Hinweise:

- `api.registerHttpHandler(...)` wurde entfernt und führt zu einem Fehler beim Laden des Plugins. Verwenden Sie stattdessen `api.registerHttpRoute(...)`.
- Plugin-Routen müssen `auth` explizit deklarieren.
- Konflikte bei exakt gleichem `path + match` werden abgelehnt, außer bei `replaceExisting: true`, und ein Plugin kann die Route eines anderen Plugins nicht ersetzen.
- Überlappende Routen mit unterschiedlichen `auth`-Stufen werden abgelehnt. Halten Sie Fallthrough-Ketten für `exact`/`prefix` nur auf derselben `auth`-Stufe.
- Routen mit `auth: "plugin"` erhalten nicht automatisch Runtime-Scopes des Operators. Sie sind für pluginverwaltete Webhooks/Signaturverifikation gedacht, nicht für privilegierte Gateway-Hilfsaufrufe.
- Routen mit `auth: "gateway"` laufen innerhalb eines Runtime-Scopes für Gateway-Anfragen, aber dieser Scope ist absichtlich konservativ:
  - Shared-Secret-Bearer-Authentifizierung (`gateway.auth.mode = "token"` / `"password"`) hält Runtime-Scopes von Plugin-Routen auf `operator.write` fest, selbst wenn der Aufrufer `x-openclaw-scopes` sendet
  - vertrauenswürdige HTTP-Modi mit Identitätsträgern (zum Beispiel `trusted-proxy` oder `gateway.auth.mode = "none"` bei privatem Ingress) berücksichtigen `x-openclaw-scopes` nur dann, wenn der Header explizit vorhanden ist
  - wenn `x-openclaw-scopes` bei diesen Plugin-Routenanfragen mit Identitätsträgern fehlt, fällt der Runtime-Scope auf `operator.write` zurück
- Praktische Regel: Gehen Sie nicht davon aus, dass eine plugin-Route mit Gateway-Authentifizierung implizit eine Admin-Oberfläche ist. Wenn Ihre Route nur für Admins bestimmtes Verhalten benötigt, verlangen Sie einen Authentifizierungsmodus mit Identitätsträgern und dokumentieren Sie den expliziten Header-Vertrag für `x-openclaw-scopes`.

## Importpfade des Plugin SDK

Verwenden Sie SDK-Subpfade statt des monolithischen Imports `openclaw/plugin-sdk`, wenn
Sie Plugins erstellen:

- `openclaw/plugin-sdk/plugin-entry` für Primitive zur Plugin-Registrierung.
- `openclaw/plugin-sdk/core` für den generischen gemeinsamen, pluginseitigen Vertrag.
- `openclaw/plugin-sdk/config-schema` für den Export des Zod-Schemas des Wurzel-`openclaw.json`
  (`OpenClawSchema`).
- Stabile Channel-Primitive wie `openclaw/plugin-sdk/channel-setup`,
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
  `openclaw/plugin-sdk/webhook-ingress` für gemeinsame Verdrahtung von Einrichtung/Auth/Antwort/Webhook.
  `channel-inbound` ist die gemeinsame Heimat für Debounce, Mention-Matching,
  Hilfsfunktionen für eingehende Mention-Richtlinien, Envelope-Formatierung und Hilfsfunktionen für
  den Kontext eingehender Envelopes.
  `channel-setup` ist der enge Seam für optionale Installations-Einrichtung.
  `setup-runtime` ist die laufzeitsichere Einrichtungsoberfläche, die von `setupEntry` /
  verzögertem Start verwendet wird, einschließlich der importsicheren Adapter für Einrichtungs-Patches.
  `setup-adapter-runtime` ist der env-bewusste Seam für Account-Einrichtungsadapter.
  `setup-tools` ist der kleine Seam für Hilfsfunktionen für CLI/Archive/Dokumentation (`formatCliCommand`,
  `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`,
  `CONFIG_DIR`).
- Domänen-Subpfade wie `openclaw/plugin-sdk/channel-config-helpers`,
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
  `openclaw/plugin-sdk/directory-runtime` für gemeinsame Laufzeit-/Konfigurationshilfsfunktionen.
  `telegram-command-config` ist der enge öffentliche Seam für die Normalisierung/Validierung benutzerdefinierter
  Telegram-Befehle und bleibt verfügbar, auch wenn die Oberfläche des gebündelten
  Telegram-Vertrags vorübergehend nicht verfügbar ist.
  `text-runtime` ist der gemeinsame Seam für Text/Markdown/Logging, einschließlich
  des Entfernens von für Assistenten sichtbarem Text, Hilfsfunktionen zum Rendern/Chunking von Markdown, Hilfsfunktionen zur
  Schwärzung, Hilfsfunktionen für Direktiven-Tags und sichere Text-Utilities.
- Approval-spezifische Channel-Seams sollten einen einzelnen Vertrag `approvalCapability`
  auf dem Plugin bevorzugen. Der Core liest dann Approval-Authentifizierung, Auslieferung, Rendering,
  natives Routing und das träge Laden nativer Handler über diese eine Fähigkeit,
  statt Approval-Verhalten mit nicht verwandten Plugin-Feldern zu vermischen.
- `openclaw/plugin-sdk/channel-runtime` ist veraltet und bleibt nur als
  Kompatibilitäts-Shim für ältere Plugins bestehen. Neuer Code sollte stattdessen die engeren
  generischen Primitive importieren, und Repository-Code sollte keine neuen Importe des
  Shims hinzufügen.
- Interna gebündelter Erweiterungen bleiben privat. Externe Plugins sollten nur
  `openclaw/plugin-sdk/*`-Subpfade verwenden. OpenClaw-Core-/Test-Code kann die
  öffentlichen Entry-Points des Repositorys unter einem Plugin-Paket-Wurzelpfad wie `index.js`, `api.js`,
  `runtime-api.js`, `setup-entry.js` und eng abgegrenzte Dateien wie
  `login-qr-api.js` verwenden. Importieren Sie niemals `src/*` eines Plugin-Pakets aus dem Core oder aus
  einer anderen Erweiterung.
- Aufteilung der Entry-Points im Repository:
  `<plugin-package-root>/api.js` ist das Barrel für Hilfsfunktionen/Typen,
  `<plugin-package-root>/runtime-api.js` ist das reine Laufzeit-Barrel,
  `<plugin-package-root>/index.js` ist der Entry-Point des gebündelten Plugins,
  und `<plugin-package-root>/setup-entry.js` ist der Entry-Point des Einrichtungs-Plugins.
- Aktuelle Beispiele für gebündelte Provider:
  - Anthropic verwendet `api.js` / `contract-api.js` für Claude-Stream-Hilfsfunktionen wie
    `wrapAnthropicProviderStream`, Hilfsfunktionen für Beta-Header und das Parsen von `service_tier`.
  - OpenAI verwendet `api.js` für Provider-Builder, Hilfsfunktionen für Standardmodelle und
    Builder für Realtime-Provider.
  - OpenRouter verwendet `api.js` für seinen Provider-Builder sowie Hilfsfunktionen für Onboarding/Konfiguration,
    während `register.runtime.js` weiterhin generische
    Hilfsfunktionen `plugin-sdk/provider-stream` für repository-lokale Nutzung re-exportieren kann.
- Öffentlich zugängliche Entry-Points, die über Facades geladen werden, bevorzugen den aktiven Runtime-Konfigurations-Snapshot,
  wenn einer vorhanden ist, und greifen andernfalls auf die auf dem Datenträger aufgelöste Konfigurationsdatei zurück, wenn
  OpenClaw noch keinen Runtime-Snapshot bereitstellt.
- Generische gemeinsame Primitive bleiben der bevorzugte öffentliche Vertrag des SDK. Ein kleines
  reserviertes Kompatibilitätsset von kanalmarkierten Hilfs-Seams gebündelter Plugins existiert weiterhin.
  Behandeln Sie diese als Seams für gebündelte Wartung/Kompatibilität, nicht als neue Importziele für
  Drittanbieter; neue kanalübergreifende Verträge sollten weiterhin auf generischen
  `plugin-sdk/*`-Subpfaden oder den pluginlokalen Barrels `api.js` /
  `runtime-api.js` landen.

Kompatibilitätshinweis:

- Vermeiden Sie für neuen Code das Root-Barrel `openclaw/plugin-sdk`.
- Bevorzugen Sie zuerst die schmalen stabilen Primitive. Die neueren Subpfade für setup/pairing/reply/
  feedback/contract/inbound/threading/command/secret-input/webhook/infra/
  allowlist/status/message-tool sind der vorgesehene Vertrag für neue
  Arbeit an gebündelten und externen Plugins.
  Ziel-Parsing/-Matching gehört auf `openclaw/plugin-sdk/channel-targets`.
  Gates für Nachrichtenaktionen und Hilfsfunktionen für Reaktions-Nachrichten-IDs gehören auf
  `openclaw/plugin-sdk/channel-actions`.
- Hilfs-Barrels, die spezifisch für gebündelte Erweiterungen sind, sind standardmäßig nicht stabil. Wenn eine
  Hilfsfunktion nur von einer gebündelten Erweiterung benötigt wird, halten Sie sie hinter dem
  lokalen Seam `api.js` oder `runtime-api.js` der Erweiterung, statt sie nach
  `openclaw/plugin-sdk/<extension>` zu befördern.
- Neue gemeinsame Hilfs-Seams sollten generisch sein, nicht channel-markiert. Gemeinsames Ziel-
  Parsing gehört auf `openclaw/plugin-sdk/channel-targets`; channelspezifische
  Interna bleiben hinter dem lokalen Seam `api.js` oder `runtime-api.js` des besitzenden Plugins.
- Fähigkeitsspezifische Subpfade wie `image-generation`,
  `media-understanding` und `speech` existieren, weil gebündelte/native Plugins sie
  heute verwenden. Ihre Existenz bedeutet nicht automatisch, dass jede exportierte Hilfsfunktion ein
  langfristig eingefrorener externer Vertrag ist.

## Schemas des Nachrichtentools

Plugins sollten channelspezifische Schema-Beiträge für `describeMessageTool(...)`
besitzen. Behalten Sie providerspezifische Felder im Plugin, nicht im gemeinsamen Core.

Für gemeinsame portable Schemafragmente verwenden Sie die generischen Hilfsfunktionen, die über
`openclaw/plugin-sdk/channel-actions` exportiert werden:

- `createMessageToolButtonsSchema()` für Payloads im Stil von Button-Rastern
- `createMessageToolCardSchema()` für strukturierte Card-Payloads

Wenn eine Schemaform nur für einen Provider sinnvoll ist, definieren Sie sie in der
eigenen Quelle dieses Plugins, statt sie in das gemeinsame SDK zu befördern.

## Auflösung von Channel-Zielen

Channel-Plugins sollten channelspezifische Zielsemantik besitzen. Halten Sie den gemeinsamen
Outbound-Host generisch und verwenden Sie die Oberfläche des Messaging-Adapters für Provider-Regeln:

- `messaging.inferTargetChatType({ to })` entscheidet, ob ein normalisiertes Ziel
  vor der Verzeichnissuche als `direct`, `group` oder `channel` behandelt werden soll.
- `messaging.targetResolver.looksLikeId(raw, normalized)` teilt dem Core mit, ob eine
  Eingabe direkt zur ID-artigen Auflösung springen sollte, statt zur Verzeichnissuche.
- `messaging.targetResolver.resolveTarget(...)` ist das Plugin-Fallback, wenn der
  Core nach der Normalisierung oder nach einem Verzeichnis-Fehlschlag eine endgültige provider-eigene Auflösung benötigt.
- `messaging.resolveOutboundSessionRoute(...)` besitzt den providerspezifischen Aufbau der Session-
  Route, sobald ein Ziel aufgelöst ist.

Empfohlene Aufteilung:

- Verwenden Sie `inferTargetChatType` für Kategorieentscheidungen, die vor
  der Suche in Peers/Gruppen erfolgen sollten.
- Verwenden Sie `looksLikeId` für Prüfungen im Stil „als explizite/native Ziel-ID behandeln“.
- Verwenden Sie `resolveTarget` für providerspezifisches Normalisierungs-Fallback, nicht für
  eine breite Verzeichnissuche.
- Halten Sie provider-native IDs wie Chat-IDs, Thread-IDs, JIDs, Handles und Raum-IDs
  innerhalb von `target`-Werten oder providerspezifischen Parametern, nicht in generischen SDK-Feldern.

## Konfigurationsgestützte Verzeichnisse

Plugins, die Verzeichniseinträge aus der Konfiguration ableiten, sollten diese Logik im
Plugin behalten und die gemeinsamen Hilfsfunktionen aus
`openclaw/plugin-sdk/directory-runtime` wiederverwenden.

Verwenden Sie dies, wenn ein Channel konfigurationsgestützte Peers/Gruppen benötigt wie:

- DM-Peers, die von der Zulassungsliste gesteuert werden
- konfigurierte Channel-/Gruppenzuordnungen
- account-bezogene statische Verzeichnis-Fallbacks

Die gemeinsamen Hilfsfunktionen in `directory-runtime` behandeln nur generische Operationen:

- Abfragefilterung
- Anwenden von Limits
- Hilfsfunktionen für Deduplizierung/Normalisierung
- Erstellen von `ChannelDirectoryEntry[]`

Channelspezifische Kontoinspektion und ID-Normalisierung sollten in der
Plugin-Implementierung bleiben.

## Provider-Kataloge

Provider-Plugins können Modellkataloge für Inferenz mit
`registerProvider({ catalog: { run(...) { ... } } })` definieren.

`catalog.run(...)` gibt dieselbe Form zurück, die OpenClaw in
`models.providers` schreibt:

- `{ provider }` für einen Provider-Eintrag
- `{ providers }` für mehrere Provider-Einträge

Verwenden Sie `catalog`, wenn das Plugin providerspezifische Modell-IDs, Standardwerte für Base-URLs
oder auth-gesteuerte Modellmetadaten besitzt.

`catalog.order` steuert, wann der Katalog eines Plugins relativ zu den
integrierten impliziten Providern von OpenClaw zusammengeführt wird:

- `simple`: einfache Provider mit API-Key oder env-gesteuert
- `profile`: Provider, die erscheinen, wenn Auth-Profile vorhanden sind
- `paired`: Provider, die mehrere zusammengehörige Provider-Einträge synthetisieren
- `late`: letzter Durchlauf, nach anderen impliziten Providern

Spätere Provider gewinnen bei Schlüsselkonflikten, sodass Plugins absichtlich einen
integrierten Provider-Eintrag mit derselben Provider-ID überschreiben können.

Kompatibilität:

- `discovery` funktioniert weiterhin als alter Alias
- wenn sowohl `catalog` als auch `discovery` registriert sind, verwendet OpenClaw `catalog`

## Schreibgeschützte Channel-Inspektion

Wenn Ihr Plugin einen Channel registriert, sollten Sie bevorzugt
`plugin.config.inspectAccount(cfg, accountId)` zusammen mit `resolveAccount(...)` implementieren.

Warum:

- `resolveAccount(...)` ist der Laufzeitpfad. Er darf annehmen, dass Zugangsdaten
  vollständig materialisiert sind, und schnell fehlschlagen, wenn erforderliche Secrets fehlen.
- Schreibgeschützte Befehlspfade wie `openclaw status`, `openclaw status --all`,
  `openclaw channels status`, `openclaw channels resolve` und Doctor-/Config-
  Reparaturabläufe sollten keine Laufzeit-Zugangsdaten materialisieren müssen, nur um
  die Konfiguration zu beschreiben.

Empfohlenes Verhalten von `inspectAccount(...)`:

- Geben Sie nur den beschreibenden Kontozustand zurück.
- Bewahren Sie `enabled` und `configured`.
- Schließen Sie Felder für Quelle/Status von Zugangsdaten ein, wenn relevant, etwa:
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- Sie müssen keine Rohwerte von Tokens zurückgeben, nur um schreibgeschützte
  Verfügbarkeit zu melden. Die Rückgabe von `tokenStatus: "available"` (und des passenden Quellfelds)
  reicht für statusartige Befehle aus.
- Verwenden Sie `configured_unavailable`, wenn ein Zugangsdatenobjekt über SecretRef konfiguriert ist, aber
  im aktuellen Befehlspfad nicht verfügbar ist.

Dadurch können schreibgeschützte Befehle „konfiguriert, aber in diesem Befehlspfad nicht verfügbar“
melden, statt abzustürzen oder das Konto fälschlich als nicht konfiguriert zu melden.

## Package-Packs

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

Jeder Eintrag wird zu einem Plugin. Wenn das Pack mehrere Erweiterungen auflistet, wird die Plugin-ID zu
`name/<fileBase>`.

Wenn Ihr Plugin npm-Abhängigkeiten importiert, installieren Sie sie in diesem Verzeichnis, damit
`node_modules` verfügbar ist (`npm install` / `pnpm install`).

Sicherheitsleitplanke: Jeder Eintrag in `openclaw.extensions` muss nach der Auflösung von Symlinks innerhalb des Plugin-
Verzeichnisses bleiben. Einträge, die das Paketverzeichnis verlassen, werden
abgelehnt.

Sicherheitshinweis: `openclaw plugins install` installiert Plugin-Abhängigkeiten mit
`npm install --omit=dev --ignore-scripts` (keine Lifecycle-Skripte, keine Dev-Abhängigkeiten zur Laufzeit). Halten Sie Plugin-Abhängigkeits-
bäume „reines JS/TS“ und vermeiden Sie Pakete, die `postinstall`-Builds benötigen.

Optional: `openclaw.setupEntry` kann auf ein leichtgewichtiges Modul nur für die Einrichtung zeigen.
Wenn OpenClaw Einrichtungsoberflächen für ein deaktiviertes Channel-Plugin benötigt oder
wenn ein Channel-Plugin aktiviert, aber noch nicht konfiguriert ist, lädt es `setupEntry`
anstelle des vollständigen Plugin-Entry-Points. Dadurch bleiben Start und Einrichtung leichter,
wenn Ihr Haupteinstieg des Plugins auch Tools, Hooks oder anderen nur für die Laufzeit bestimmten
Code verdrahtet.

Optional: `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`
kann ein Channel-Plugin beim Vor-dem-Listen-Start des Gateways in denselben `setupEntry`-Pfad
opt-in versetzen, auch wenn der Channel bereits konfiguriert ist.

Verwenden Sie dies nur, wenn `setupEntry` die Startoberfläche vollständig abdeckt, die
vor dem Beginn des Listenens des Gateways vorhanden sein muss. In der Praxis bedeutet das, dass der
Setup-Entry jede channelspezifische Fähigkeit registrieren muss, von der der Start abhängt, etwa:

- die Channel-Registrierung selbst
- alle HTTP-Routen, die verfügbar sein müssen, bevor das Gateway zu lauschen beginnt
- alle Gateway-Methoden, Tools oder Dienste, die in demselben Zeitfenster vorhanden sein müssen

Wenn Ihr vollständiger Entry weiterhin eine erforderliche Startfähigkeit besitzt, aktivieren Sie
dieses Flag nicht. Behalten Sie das Standardverhalten des Plugins bei und lassen Sie OpenClaw den
vollständigen Entry beim Start laden.

Gebündelte Channels können auch Hilfsfunktionen für die Einrichtungsoberfläche eines Vertrags veröffentlichen, die der Core
abfragen kann, bevor die vollständige Channel-Laufzeit geladen ist. Die aktuelle Oberfläche für Setup-
Promotion ist:

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

Der Core verwendet diese Oberfläche, wenn er eine alte Einzelkonto-Channel-
Konfiguration nach `channels.<id>.accounts.*` überführen muss, ohne den vollständigen Plugin-Entry zu laden.
Matrix ist das aktuelle gebündelte Beispiel: Es verschiebt nur Auth-/Bootstrap-Schlüssel in ein
benanntes befördertes Konto, wenn benannte Konten bereits existieren, und es kann einen
konfigurierten nicht-kanonischen Standard-Kontoschlüssel beibehalten, statt immer
`accounts.default` zu erstellen.

Diese Adapter für Setup-Patches halten die Erkennung von gebündelten Vertragsoberflächen träge. Die Import-
Zeit bleibt leicht; die Promotionsoberfläche wird erst bei der ersten Verwendung geladen, statt beim Modulimport erneut in den Start gebündelter Channels einzutreten.

Wenn diese Startoberflächen Gateway-RPC-Methoden enthalten, halten Sie sie auf einem
pluginspezifischen Präfix. Core-Admin-Namespaces (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) bleiben reserviert und werden immer
zu `operator.admin` aufgelöst, selbst wenn ein Plugin einen engeren Scope anfordert.

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

### Channel-Katalogmetadaten

Channel-Plugins können Metadaten für Einrichtung/Erkennung über `openclaw.channel` und
Installationshinweise über `openclaw.install` bekanntgeben. So bleiben die Katalogdaten im Core frei von Daten.

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

Nützliche Felder von `openclaw.channel` über das minimale Beispiel hinaus:

- `detailLabel`: sekundäres Label für reichhaltigere Katalog-/Statusoberflächen
- `docsLabel`: Linktext für den Doku-Link überschreiben
- `preferOver`: Plugin-/Channel-IDs mit niedrigerer Priorität, die dieser Katalogeintrag übertreffen soll
- `selectionDocsPrefix`, `selectionDocsOmitLabel`, `selectionExtras`: Steuerung der Texte auf Auswahloberflächen
- `markdownCapable`: markiert den Channel als markdownfähig für Entscheidungen zur ausgehenden Formatierung
- `exposure.configured`: den Channel aus Oberflächen zum Auflisten konfigurierter Channels ausblenden, wenn auf `false` gesetzt
- `exposure.setup`: den Channel aus interaktiven Einrichtungs-/Konfigurations-Auswahlen ausblenden, wenn auf `false` gesetzt
- `exposure.docs`: den Channel auf Doku-Navigationsoberflächen als intern/privat markieren
- `showConfigured` / `showInSetup`: alte Aliase werden aus Kompatibilitätsgründen weiterhin akzeptiert; bevorzugen Sie `exposure`
- `quickstartAllowFrom`: den Channel in den Standard-Quickstart-Ablauf `allowFrom` einbeziehen
- `forceAccountBinding`: explizite Kontobindung verlangen, auch wenn nur ein Konto existiert
- `preferSessionLookupForAnnounceTarget`: Session-Lookup bei der Auflösung von Ankündigungszielen bevorzugen

OpenClaw kann außerdem **externe Channel-Kataloge** zusammenführen (zum Beispiel einen Export einer MPM-
Registry). Legen Sie eine JSON-Datei an einem der folgenden Orte ab:

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

Oder verweisen Sie `OPENCLAW_PLUGIN_CATALOG_PATHS` (oder `OPENCLAW_MPM_CATALOG_PATHS`) auf
eine oder mehrere JSON-Dateien (durch Komma/Semikolon/`PATH` getrennt). Jede Datei sollte
`{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }` enthalten. Der Parser akzeptiert außerdem `"packages"` oder `"plugins"` als alte Aliase für den Schlüssel `"entries"`.

## Context-Engine-Plugins

Context-Engine-Plugins besitzen die Orchestrierung des Sitzungskontexts für Ingest, Assemblierung
und Compaction. Registrieren Sie sie aus Ihrem Plugin mit
`api.registerContextEngine(id, factory)` und wählen Sie dann die aktive Engine mit
`plugins.slots.contextEngine` aus.

Verwenden Sie dies, wenn Ihr Plugin die Standard-
Context-Pipeline ersetzen oder erweitern muss, statt nur Speichersuche oder Hooks hinzuzufügen.

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

Wenn Ihre Engine den Compaction-Algorithmus **nicht** besitzt, behalten Sie `compact()`
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

## Hinzufügen einer neuen Fähigkeit

Wenn ein Plugin Verhalten benötigt, das nicht zur aktuellen API passt, umgehen Sie
das Plugin-System nicht mit einem privaten Direktzugriff. Fügen Sie die fehlende Fähigkeit hinzu.

Empfohlene Reihenfolge:

1. den Core-Vertrag definieren
   Entscheiden Sie, welches gemeinsame Verhalten der Core besitzen soll: Richtlinien, Fallback, Konfigurationszusammenführung,
   Lebenszyklus, semantics auf Channel-Seite und Form der Laufzeit-Hilfsfunktionen.
2. typisierte Oberflächen für Plugin-Registrierung/Laufzeit hinzufügen
   Erweitern Sie `OpenClawPluginApi` und/oder `api.runtime` um die kleinste nützliche
   typisierte Fähigkeitsoberfläche.
3. Core- + Channel-/Feature-Consumer verdrahten
   Channels und Feature-Plugins sollten die neue Fähigkeit über den Core nutzen,
   nicht durch direkten Import einer Anbieterimplementierung.
4. Anbieterimplementierungen registrieren
   Anbieter-Plugins registrieren dann ihre Backends für die Fähigkeit.
5. Vertragsabdeckung hinzufügen
   Fügen Sie Tests hinzu, damit Besitzerschaft und Registrierungsform über die Zeit explizit bleiben.

So bleibt OpenClaw meinungsstark, ohne auf das Weltbild eines einzelnen
Providers fest codiert zu sein. Siehe das [Capability Cookbook](/de/plugins/architecture)
für eine konkrete Dateicheckliste und ein ausgearbeitetes Beispiel.

### Checkliste für Fähigkeiten

Wenn Sie eine neue Fähigkeit hinzufügen, sollte die Implementierung normalerweise diese
Oberflächen gemeinsam berühren:

- Core-Vertragstypen in `src/<capability>/types.ts`
- Core-Runner/Laufzeit-Hilfsfunktion in `src/<capability>/runtime.ts`
- Plugin-API-Registrierungsoberfläche in `src/plugins/types.ts`
- Verdrahtung der Plugin-Registry in `src/plugins/registry.ts`
- Freigabe in der Plugin-Laufzeit in `src/plugins/runtime/*`, wenn Feature-/Channel-
  Plugins sie nutzen müssen
- Erfassungs-/Testhilfsfunktionen in `src/test-utils/plugin-registration.ts`
- Assertions zu Besitzerschaft/Vertrag in `src/plugins/contracts/registry.ts`
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

- der Core besitzt den Fähigkeitsvertrag + die Orchestrierung
- Anbieter-Plugins besitzen Anbieterimplementierungen
- Feature-/Channel-Plugins nutzen Laufzeit-Hilfsfunktionen
- Vertragstests halten die Besitzerschaft explizit
