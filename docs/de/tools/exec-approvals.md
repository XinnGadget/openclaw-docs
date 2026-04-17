---
read_when:
    - Konfigurieren von Ausführungsfreigaben oder Zulassungslisten
    - Implementierung der UX für Ausführungsfreigaben in der macOS-App
    - Überprüfung von Sandbox-Escape-Aufforderungen und ihren Auswirkungen
summary: Ausführungsfreigaben, Zulassungslisten und Sandbox-Escape-Aufforderungen
title: Ausführungsfreigaben
x-i18n:
    generated_at: "2026-04-10T06:21:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5f4a2e2f1f3c13a1d1926c9de0720513ea8a74d1ca571dbe74b188d8c560c14c
    source_path: tools/exec-approvals.md
    workflow: 15
---

# Ausführungsfreigaben

Ausführungsfreigaben sind die **Sicherheitsleitplanke der Companion-App bzw. des Node-Hosts**, damit ein in einer Sandbox ausgeführter Agent Befehle auf einem echten Host (`gateway` oder `node`) ausführen kann. Sie funktionieren wie eine Sicherheitsverriegelung:
Befehle sind nur erlaubt, wenn Richtlinie + Zulassungsliste + (optionale) Benutzerfreigabe alle zustimmen.
Ausführungsfreigaben gelten **zusätzlich** zur Tool-Richtlinie und zu Elevated-Gating (außer wenn Elevated auf `full` gesetzt ist; dann werden Freigaben übersprungen).
Die effektive Richtlinie ist die **strengere** von `tools.exec.*` und den Standardwerten für Freigaben; wenn ein Feld bei den Freigaben weggelassen wird, wird stattdessen der Wert aus `tools.exec` verwendet.
Die Host-Ausführung verwendet außerdem den lokalen Freigabestatus auf diesem Rechner. Ein hostlokales
`ask: "always"` in `~/.openclaw/exec-approvals.json` sorgt weiterhin für Eingabeaufforderungen, auch wenn
Sitzungs- oder Konfigurationsstandardwerte `ask: "on-miss"` anfordern.
Verwenden Sie `openclaw approvals get`, `openclaw approvals get --gateway` oder
`openclaw approvals get --node <id|name|ip>`, um die angeforderte Richtlinie,
die Quellen der Host-Richtlinie und das effektive Ergebnis zu prüfen.
Für den lokalen Rechner zeigt `openclaw exec-policy show` dieselbe zusammengeführte Ansicht an, und
`openclaw exec-policy set|preset` kann die lokal angeforderte Richtlinie in einem Schritt mit der
lokalen Host-Freigabedatei synchronisieren. Wenn ein lokaler Geltungsbereich `host=node` anfordert,
meldet `openclaw exec-policy show` diesen Geltungsbereich zur Laufzeit als von einem Node verwaltet, statt
so zu tun, als wäre die lokale Freigabedatei die tatsächlich maßgebliche Quelle.

Wenn die UI der Companion-App **nicht verfügbar** ist, wird jede Anforderung, die eine Eingabeaufforderung benötigt,
über das **ask-Fallback** aufgelöst (Standard: deny).

Native Chat-Freigabe-Clients können außerdem kanalspezifische Bedienelemente in der ausstehenden
Freigabenachricht anzeigen. Matrix kann zum Beispiel Reaktionskürzel in der
Freigabeaufforderung vorbelegen (`✅` einmal erlauben, `❌` verweigern und `♾️` immer erlauben, sofern verfügbar),
während die `/approve ...`-Befehle in der Nachricht weiterhin als Fallback bleiben.

## Wo dies gilt

Ausführungsfreigaben werden lokal auf dem Ausführungshost durchgesetzt:

- **gateway-Host** → `openclaw`-Prozess auf dem Gateway-Rechner
- **node-Host** → Node-Runner (macOS-Companion-App oder kopfloser Node-Host)

Hinweis zum Vertrauensmodell:

- Über das Gateway authentifizierte Aufrufer sind vertrauenswürdige Operatoren für dieses Gateway.
- Gekoppelte Nodes erweitern diese vertrauenswürdige Operatorfähigkeit auf den Node-Host.
- Ausführungsfreigaben verringern das Risiko versehentlicher Ausführung, sind aber keine Authentifizierungsgrenze pro Benutzer.
- Genehmigte Ausführungen auf dem Node-Host binden den kanonischen Ausführungskontext: kanonisches cwd, exaktes argv, env-Bindung
  sofern vorhanden und angehefteter Pfad zur ausführbaren Datei, falls zutreffend.
- Für Shell-Skripte und direkte Interpreter-/Runtime-Dateiaufrufe versucht OpenClaw außerdem,
  genau einen konkreten lokalen Dateiopeanden zu binden. Wenn sich diese gebundene Datei nach der
  Freigabe, aber vor der Ausführung ändert, wird die Ausführung verweigert, statt Inhalte mit Abweichungen auszuführen.
- Diese Dateibindung ist absichtlich nur nach bestem Bemühen implementiert, nicht als vollständiges semantisches Modell jedes
  Interpreter-/Runtime-Ladepfads. Wenn der Freigabemodus nicht genau eine konkrete lokale Datei zur Bindung identifizieren kann,
  wird die Erzeugung einer freigabegestützten Ausführung verweigert, statt eine vollständige Abdeckung vorzutäuschen.

macOS-Aufteilung:

- Der **node host service** leitet `system.run` über lokale IPC an die **macOS-App** weiter.
- Die **macOS-App** erzwingt Freigaben und führt den Befehl im UI-Kontext aus.

## Einstellungen und Speicherung

Freigaben werden in einer lokalen JSON-Datei auf dem Ausführungshost gespeichert:

`~/.openclaw/exec-approvals.json`

Beispielschema:

```json
{
  "version": 1,
  "socket": {
    "path": "~/.openclaw/exec-approvals.sock",
    "token": "base64url-token"
  },
  "defaults": {
    "security": "deny",
    "ask": "on-miss",
    "askFallback": "deny",
    "autoAllowSkills": false
  },
  "agents": {
    "main": {
      "security": "allowlist",
      "ask": "on-miss",
      "askFallback": "deny",
      "autoAllowSkills": true,
      "allowlist": [
        {
          "id": "B0C8C0B3-2C2D-4F8A-9A3C-5A4B3C2D1E0F",
          "pattern": "~/Projects/**/bin/rg",
          "lastUsedAt": 1737150000000,
          "lastUsedCommand": "rg -n TODO",
          "lastResolvedPath": "/Users/user/Projects/.../bin/rg"
        }
      ]
    }
  }
}
```

## Modus „YOLO“ ohne Freigaben

Wenn Sie möchten, dass die Host-Ausführung ohne Freigabeaufforderungen ausgeführt wird, müssen Sie **beide** Richtlinienebenen öffnen:

- angeforderte Ausführungsrichtlinie in der OpenClaw-Konfiguration (`tools.exec.*`)
- hostlokale Freigaberichtlinie in `~/.openclaw/exec-approvals.json`

Dies ist jetzt das Standardverhalten für den Host, sofern Sie es nicht explizit verschärfen:

- `tools.exec.security`: `full` auf `gateway`/`node`
- `tools.exec.ask`: `off`
- host `askFallback`: `full`

Wichtige Unterscheidung:

- `tools.exec.host=auto` wählt aus, wo die Ausführung stattfindet: in der Sandbox, wenn verfügbar, andernfalls auf dem Gateway.
- YOLO wählt aus, wie die Host-Ausführung freigegeben wird: `security=full` plus `ask=off`.
- Im YOLO-Modus legt OpenClaw keine zusätzliche heuristische Freigabeschranke für Befehlsverschleierung über die konfigurierte Host-Ausführungsrichtlinie.
- `auto` macht Gateway-Routing nicht zu einer freien Umgehung aus einer Sandbox-Sitzung heraus. Eine Anforderung pro Aufruf mit `host=node` ist aus `auto` heraus erlaubt, und `host=gateway` ist aus `auto` nur dann erlaubt, wenn keine Sandbox-Runtime aktiv ist. Wenn Sie einen stabilen Standardwert ohne `auto` möchten, setzen Sie `tools.exec.host` oder verwenden Sie `/exec host=...` explizit.

Wenn Sie eine konservativere Einrichtung möchten, verschärfen Sie eine der Ebenen wieder auf `allowlist` / `on-miss`
oder `deny`.

Dauerhafte Einrichtung „nie nachfragen“ für den Gateway-Host:

```bash
openclaw config set tools.exec.host gateway
openclaw config set tools.exec.security full
openclaw config set tools.exec.ask off
openclaw gateway restart
```

Setzen Sie dann die Host-Freigabedatei passend dazu:

```bash
openclaw approvals set --stdin <<'EOF'
{
  version: 1,
  defaults: {
    security: "full",
    ask: "off",
    askFallback: "full"
  }
}
EOF
```

Lokale Abkürzung für dieselbe Gateway-Host-Richtlinie auf dem aktuellen Rechner:

```bash
openclaw exec-policy preset yolo
```

Diese lokale Abkürzung aktualisiert beides:

- lokale `tools.exec.host/security/ask`
- lokale Standardwerte in `~/.openclaw/exec-approvals.json`

Sie ist absichtlich nur lokal wirksam. Wenn Sie Freigaben für Gateway-Host oder Node-Host
remote ändern müssen, verwenden Sie weiterhin `openclaw approvals set --gateway` oder
`openclaw approvals set --node <id|name|ip>`.

Für einen Node-Host wenden Sie stattdessen dieselbe Freigabedatei auf diesem Node an:

```bash
openclaw approvals set --node <id|name|ip> --stdin <<'EOF'
{
  version: 1,
  defaults: {
    security: "full",
    ask: "off",
    askFallback: "full"
  }
}
EOF
```

Wichtige Einschränkung nur für lokal:

- `openclaw exec-policy` synchronisiert keine Node-Freigaben
- `openclaw exec-policy set --host node` wird abgelehnt
- Node-Ausführungsfreigaben werden zur Laufzeit vom Node abgerufen, daher müssen Node-bezogene Aktualisierungen über `openclaw approvals --node ...` erfolgen

Abkürzung nur für die Sitzung:

- `/exec security=full ask=off` ändert nur die aktuelle Sitzung.
- `/elevated full` ist eine Break-Glass-Abkürzung, die Ausführungsfreigaben für diese Sitzung ebenfalls überspringt.

Wenn die Host-Freigabedatei strenger bleibt als die Konfiguration, gewinnt weiterhin die strengere Host-Richtlinie.

## Richtlinienoptionen

### Security (`exec.security`)

- **deny**: blockiert alle Anfragen zur Host-Ausführung.
- **allowlist**: erlaubt nur Befehle auf der Zulassungsliste.
- **full**: erlaubt alles (entspricht elevated).

### Ask (`exec.ask`)

- **off**: niemals nachfragen.
- **on-miss**: nur nachfragen, wenn die Zulassungsliste nicht passt.
- **always**: bei jedem Befehl nachfragen.
- Dauerhaftes Vertrauen über `allow-always` unterdrückt Eingabeaufforderungen nicht, wenn der effektive ask-Modus `always` ist

### Ask-Fallback (`askFallback`)

Wenn eine Eingabeaufforderung erforderlich ist, aber keine UI erreichbar ist, entscheidet das Fallback:

- **deny**: blockieren.
- **allowlist**: nur erlauben, wenn die Zulassungsliste passt.
- **full**: erlauben.

### Härtung für Inline-Interpreterauswertung (`tools.exec.strictInlineEval`)

Wenn `tools.exec.strictInlineEval=true`, behandelt OpenClaw Formen der Inline-Codeauswertung als nur per Freigabe erlaubt, auch wenn das Interpreter-Binary selbst auf der Zulassungsliste steht.

Beispiele:

- `python -c`
- `node -e`, `node --eval`, `node -p`
- `ruby -e`
- `perl -e`, `perl -E`
- `php -r`
- `lua -e`
- `osascript -e`

Dies ist eine zusätzliche Schutzmaßnahme für Interpreter-Lader, die sich nicht sauber auf einen stabilen Dateiopeanden abbilden lassen. Im strikten Modus gilt:

- diese Befehle benötigen weiterhin eine explizite Freigabe;
- `allow-always` speichert für sie nicht automatisch neue Zulassungslisteneinträge.

## Zulassungsliste (pro Agent)

Zulassungslisten gelten **pro Agent**. Wenn mehrere Agents vorhanden sind, wechseln Sie in der
macOS-App zu dem Agent, den Sie bearbeiten möchten. Muster sind **globale Abgleiche ohne Beachtung der Groß-/Kleinschreibung**.
Muster sollten zu **Binary-Pfaden** aufgelöst werden (Einträge nur mit Basename werden ignoriert).
Veraltete `agents.default`-Einträge werden beim Laden nach `agents.main` migriert.
Shell-Verkettungen wie `echo ok && pwd` erfordern weiterhin, dass jedes Segment der obersten Ebene die Regeln der Zulassungsliste erfüllt.

Beispiele:

- `~/Projects/**/bin/peekaboo`
- `~/.local/bin/*`
- `/opt/homebrew/bin/rg`

Jeder Eintrag in der Zulassungsliste erfasst:

- **id** stabile UUID für die UI-Identität (optional)
- **last used** Zeitstempel
- **last used command**
- **last resolved path**

## CLI von Skills automatisch zulassen

Wenn **CLI von Skills automatisch zulassen** aktiviert ist, werden ausführbare Dateien, auf die bekannte Skills verweisen,
auf Nodes (macOS-Node oder kopfloser Node-Host) als auf der Zulassungsliste behandelt. Dazu wird
`skills.bins` über Gateway-RPC verwendet, um die Binärdateiliste des Skills abzurufen. Deaktivieren Sie dies, wenn Sie strikte manuelle Zulassungslisten möchten.

Wichtige Hinweise zum Vertrauensmodell:

- Dies ist eine **implizite Komfort-Zulassungsliste**, getrennt von manuellen Pfadeinträgen in der Zulassungsliste.
- Sie ist für vertrauenswürdige Operatorumgebungen gedacht, in denen Gateway und Node innerhalb derselben Vertrauensgrenze liegen.
- Wenn Sie striktes explizites Vertrauen benötigen, lassen Sie `autoAllowSkills: false` gesetzt und verwenden Sie nur manuelle Pfadeinträge in der Zulassungsliste.

## Sichere Binaries (nur stdin)

`tools.exec.safeBins` definiert eine kleine Liste von **nur-stdin**-Binaries (zum Beispiel `cut`),
die im Modus `allowlist` **ohne** explizite Einträge in der Zulassungsliste ausgeführt werden können. Sichere Binaries lehnen
positionale Dateiar gumente und pfadähnliche Token ab, sodass sie nur auf dem eingehenden Stream arbeiten können.
Behandeln Sie dies als engen Schnellpfad für Stream-Filter, nicht als allgemeine Vertrauensliste.
Fügen Sie **keine** Interpreter- oder Runtime-Binaries (zum Beispiel `python3`, `node`, `ruby`, `bash`, `sh`, `zsh`) zu `safeBins` hinzu.
Wenn ein Befehl Code auswerten, Unterbefehle ausführen oder konstruktionsbedingt Dateien lesen kann, bevorzugen Sie explizite Einträge in der Zulassungsliste und lassen Sie Freigabeaufforderungen aktiviert.
Benutzerdefinierte sichere Binaries müssen ein explizites Profil in `tools.exec.safeBinProfiles.<bin>` definieren.
Die Validierung ist allein anhand der Form von argv deterministisch (keine Prüfungen auf Dateiexistenz im Host-Dateisystem), was
Oracle-Verhalten über Dateiexistenz durch Unterschiede zwischen Erlauben und Verweigern verhindert.
Dateiorientierte Optionen werden für Standard-Safe-Bins verweigert (zum Beispiel `sort -o`, `sort --output`,
`sort --files0-from`, `sort --compress-program`, `sort --random-source`,
`sort --temporary-directory`/`-T`, `wc --files0-from`, `jq -f/--from-file`,
`grep -f/--file`).
Sichere Binaries erzwingen außerdem eine explizite Richtlinie pro Binary für Flags, die das Nur-stdin-
Verhalten aufheben (zum Beispiel `sort -o/--output/--compress-program` und rekursive grep-Flags).
Lange Optionen werden im Safe-Bin-Modus fehlersicher validiert: unbekannte Flags und mehrdeutige
Abkürzungen werden abgelehnt.
Durch Safe-Bin-Profile verweigerte Flags:

[//]: # "SAFE_BIN_DENIED_FLAGS:START"

- `grep`: `--dereference-recursive`, `--directories`, `--exclude-from`, `--file`, `--recursive`, `-R`, `-d`, `-f`, `-r`
- `jq`: `--argfile`, `--from-file`, `--library-path`, `--rawfile`, `--slurpfile`, `-L`, `-f`
- `sort`: `--compress-program`, `--files0-from`, `--output`, `--random-source`, `--temporary-directory`, `-T`, `-o`
- `wc`: `--files0-from`

[//]: # "SAFE_BIN_DENIED_FLAGS:END"

Sichere Binaries erzwingen außerdem, dass argv-Token zur Ausführungszeit als **wörtlicher Text** behandelt werden (kein Globbing
und keine `$VARS`-Erweiterung) für Nur-stdin-Segmente, sodass Muster wie `*` oder `$HOME/...` nicht
zum Einschleusen von Dateilesen verwendet werden können.
Sichere Binaries müssen außerdem aus vertrauenswürdigen Binary-Verzeichnissen aufgelöst werden (Systemstandards plus optionale
`tools.exec.safeBinTrustedDirs`). `PATH`-Einträge werden niemals automatisch als vertrauenswürdig behandelt.
Die standardmäßig vertrauenswürdigen Verzeichnisse für sichere Binaries sind absichtlich minimal: `/bin`, `/usr/bin`.
Wenn sich Ihr Safe-Bin-Executable in Paketmanager- oder Benutzerpfaden befindet (zum Beispiel
`/opt/homebrew/bin`, `/usr/local/bin`, `/opt/local/bin`, `/snap/bin`), fügen Sie sie explizit
zu `tools.exec.safeBinTrustedDirs` hinzu.
Shell-Verkettungen und Umleitungen werden im Modus `allowlist` nicht automatisch erlaubt.

Shell-Verkettung (`&&`, `||`, `;`) ist erlaubt, wenn jedes Segment der obersten Ebene die Zulassungsliste erfüllt
(einschließlich sicherer Binaries oder automatischer Zulassung von Skills). Umleitungen werden im Modus `allowlist` weiterhin nicht unterstützt.
Befehlssubstitution (`$()` / Backticks) wird beim Parsen der Zulassungsliste abgelehnt, auch innerhalb
doppelter Anführungszeichen; verwenden Sie einfache Anführungszeichen, wenn Sie wörtlichen `$()`-Text benötigen.
Bei Freigaben der macOS-Companion-App wird roher Shell-Text, der Shell-Steuer- oder Erweiterungssyntax enthält
(`&&`, `||`, `;`, `|`, `` ` ``, `$`, `<`, `>`, `(`, `)`), als Nichttreffer der Zulassungsliste behandelt, sofern
das Shell-Binary selbst nicht auf der Zulassungsliste steht.
Für Shell-Wrapper (`bash|sh|zsh ... -c/-lc`) werden anforderungsbezogene env-Overrides auf eine
kleine explizite Zulassungsliste reduziert (`TERM`, `LANG`, `LC_*`, `COLORTERM`, `NO_COLOR`, `FORCE_COLOR`).
Bei Entscheidungen vom Typ „immer erlauben“ im Modus `allowlist` speichern bekannte
Dispatch-Wrapper (`env`, `nice`, `nohup`, `stdbuf`, `timeout`) innere Executable-Pfade statt Wrapper-Pfaden.
Shell-Multiplexer (`busybox`, `toybox`) werden für Shell-Applets (`sh`, `ash`,
usw.) ebenfalls entpackt, sodass innere Executables statt Multiplexer-Binaries gespeichert werden. Wenn ein Wrapper oder
Multiplexer nicht sicher entpackt werden kann, wird kein Eintrag in der Zulassungsliste automatisch gespeichert.
Wenn Sie Interpreter wie `python3` oder `node` auf die Zulassungsliste setzen, sollten Sie `tools.exec.strictInlineEval=true` bevorzugen, damit Inline-Eval weiterhin eine explizite Freigabe erfordert. Im strikten Modus kann `allow-always` weiterhin harmlose Interpreter-/Skriptaufrufe speichern, aber Träger von Inline-Eval werden nicht automatisch gespeichert.

Standardmäßig sichere Binaries:

[//]: # "SAFE_BIN_DEFAULTS:START"

`cut`, `uniq`, `head`, `tail`, `tr`, `wc`

[//]: # "SAFE_BIN_DEFAULTS:END"

`grep` und `sort` sind nicht in der Standardliste enthalten. Wenn Sie sich bewusst dafür entscheiden, behalten Sie explizite Einträge in der Zulassungsliste für
deren Workflows, die nicht nur stdin verwenden.
Für `grep` im Safe-Bin-Modus geben Sie das Muster mit `-e`/`--regexp` an; die
positionale Musterform wird abgelehnt, damit Dateiopeanden nicht als mehrdeutige positionale Argumente eingeschleust werden können.

### Sichere Binaries im Vergleich zur Zulassungsliste

| Thema            | `tools.exec.safeBins`                                  | Zulassungsliste (`exec-approvals.json`)                      |
| ---------------- | ------------------------------------------------------ | ------------------------------------------------------------ |
| Ziel             | Schmale stdin-Filter automatisch erlauben              | Bestimmten Executables explizit vertrauen                    |
| Abgleichstyp     | Executable-Name + argv-Richtlinie für sichere Binaries | Glob-Muster des aufgelösten Executable-Pfads                 |
| Argumentbereich  | Durch Safe-Bin-Profil und Literal-Token-Regeln eingeschränkt | Nur Pfadabgleich; Argumente liegen sonst in Ihrer Verantwortung |
| Typische Beispiele | `head`, `tail`, `tr`, `wc`                           | `jq`, `python3`, `node`, `ffmpeg`, benutzerdefinierte CLIs   |
| Beste Verwendung | Texttransformationen mit geringem Risiko in Pipelines  | Jedes Tool mit breiterem Verhalten oder Nebeneffekten        |

Ort der Konfiguration:

- `safeBins` stammt aus der Konfiguration (`tools.exec.safeBins` oder pro Agent `agents.list[].tools.exec.safeBins`).
- `safeBinTrustedDirs` stammt aus der Konfiguration (`tools.exec.safeBinTrustedDirs` oder pro Agent `agents.list[].tools.exec.safeBinTrustedDirs`).
- `safeBinProfiles` stammt aus der Konfiguration (`tools.exec.safeBinProfiles` oder pro Agent `agents.list[].tools.exec.safeBinProfiles`). Profilschlüssel pro Agent überschreiben globale Schlüssel.
- Einträge in der Zulassungsliste liegen hostlokal in `~/.openclaw/exec-approvals.json` unter `agents.<id>.allowlist` (oder über die Control UI / `openclaw approvals allowlist ...`).
- `openclaw security audit` warnt mit `tools.exec.safe_bins_interpreter_unprofiled`, wenn Interpreter-/Runtime-Binaries in `safeBins` ohne explizite Profile erscheinen.
- `openclaw doctor --fix` kann fehlende benutzerdefinierte `safeBinProfiles.<bin>`-Einträge als `{}` erzeugen (anschließend prüfen und verschärfen). Interpreter-/Runtime-Binaries werden nicht automatisch erzeugt.

Beispiel für ein benutzerdefiniertes Profil:
__OC_I18N_900005__
Wenn Sie `jq` explizit in `safeBins` aufnehmen, lehnt OpenClaw das Built-in `env` im Safe-Bin-
Modus dennoch ab, sodass `jq -n env` die Host-Prozessumgebung nicht ohne einen expliziten Pfad in der Zulassungsliste
oder eine Freigabeaufforderung ausgeben kann.

## Bearbeitung in der Control UI

Verwenden Sie **Control UI → Nodes → Exec approvals**, um Standardwerte, agentbezogene
Überschreibungen und Zulassungslisten zu bearbeiten. Wählen Sie einen Geltungsbereich (Standardwerte oder einen Agent), passen Sie die Richtlinie an,
fügen Sie Muster für die Zulassungsliste hinzu oder entfernen Sie sie und klicken Sie dann auf **Save**. Die UI zeigt Metadaten zu **last used**
pro Muster an, damit Sie die Liste übersichtlich halten können.

Mit der Zielauswahl wählen Sie **Gateway** (lokale Freigaben) oder einen **Node**. Nodes
müssen `system.execApprovals.get/set` ankündigen (macOS-App oder kopfloser Node-Host).
Wenn ein Node noch keine Ausführungsfreigaben ankündigt, bearbeiten Sie seine lokale
`~/.openclaw/exec-approvals.json` direkt.

CLI: `openclaw approvals` unterstützt die Bearbeitung für Gateway oder Node (siehe [Approvals CLI](/cli/approvals)).

## Freigabeablauf

Wenn eine Eingabeaufforderung erforderlich ist, sendet das Gateway `exec.approval.requested` an Operator-Clients.
Die Control UI und die macOS-App lösen dies über `exec.approval.resolve` auf, dann leitet das Gateway die
genehmigte Anforderung an den Node-Host weiter.

Für `host=node` enthalten Freigabeanforderungen eine kanonische `systemRunPlan`-Payload. Das Gateway verwendet
diesen Plan als maßgeblichen Kontext für Befehl/cwd/Sitzung, wenn genehmigte `system.run`-
Anforderungen weitergeleitet werden.

Das ist für asynchrone Latenz bei Freigaben wichtig:

- der Node-Exec-Pfad bereitet im Voraus einen kanonischen Plan vor
- der Freigabedatensatz speichert diesen Plan und seine Bindungsmetadaten
- nach der Genehmigung verwendet der endgültig weitergeleitete `system.run`-Aufruf den gespeicherten Plan wieder,
  statt späteren Änderungen durch den Aufrufer zu vertrauen
- wenn der Aufrufer `command`, `rawCommand`, `cwd`, `agentId` oder
  `sessionKey` ändert, nachdem die Freigabeanforderung erstellt wurde, lehnt das Gateway die
  weitergeleitete Ausführung als Freigabe-Nichtübereinstimmung ab

## Interpreter-/Runtime-Befehle

Durch Freigaben abgesicherte Interpreter-/Runtime-Ausführungen sind absichtlich konservativ:

- Exakter Kontext aus argv/cwd/env wird immer gebunden.
- Direkte Shell-Skript- und direkte Runtime-Dateiformen werden nach bestem Bemühen an einen konkreten lokalen
  Dateisnapshot gebunden.
- Häufige Paketmanager-Wrapper-Formen, die sich dennoch zu einer direkten lokalen Datei auflösen lassen (zum Beispiel
  `pnpm exec`, `pnpm node`, `npm exec`, `npx`), werden vor der Bindung entpackt.
- Wenn OpenClaw für einen Interpreter-/Runtime-Befehl nicht genau eine konkrete lokale Datei identifizieren kann
  (zum Beispiel Paketskripte, Eval-Formen, runtime-spezifische Loader-Ketten oder mehrdeutige Formen mit mehreren Dateien),
  wird die durch Freigaben abgesicherte Ausführung verweigert, statt semantische Abdeckung zu behaupten, die tatsächlich
  nicht vorhanden ist.
- Für diese Workflows sollten Sie Sandboxing, eine separate Host-Grenze oder einen expliziten vertrauenswürdigen
  Workflow mit Zulassungsliste/full bevorzugen, bei dem der Operator die breitere Runtime-Semantik akzeptiert.

Wenn Freigaben erforderlich sind, gibt das Exec-Tool sofort eine Freigabe-ID zurück. Verwenden Sie diese ID, um
spätere Systemereignisse zuzuordnen (`Exec finished` / `Exec denied`). Wenn vor dem
Timeout keine Entscheidung eintrifft, wird die Anforderung als Freigabe-Timeout behandelt und als Grund für die Verweigerung angezeigt.

### Verhalten bei der Zustellung von Folgeaktionen

Nachdem eine genehmigte asynchrone Ausführung abgeschlossen ist, sendet OpenClaw einen nachfolgenden `agent`-Turn an dieselbe Sitzung.

- Wenn ein gültiges externes Zustellziel vorhanden ist (zustellbarer Kanal plus Ziel `to`), verwendet die Zustellung der Folgeaktion diesen Kanal.
- In reinem Webchat oder internen Sitzungsabläufen ohne externes Ziel bleibt die Zustellung der Folgeaktion nur sitzungsintern (`deliver: false`).
- Wenn ein Aufrufer explizit eine strikte externe Zustellung anfordert, aber kein externer Kanal aufgelöst werden kann, schlägt die Anforderung mit `INVALID_REQUEST` fehl.
- Wenn `bestEffortDeliver` aktiviert ist und kein externer Kanal aufgelöst werden kann, wird die Zustellung statt eines Fehlers auf nur sitzungsintern herabgestuft.

Der Bestätigungsdialog enthält:

- Befehl + Argumente
- cwd
- Agent-ID
- aufgelöster Executable-Pfad
- Host- und Richtlinienmetadaten

Aktionen:

- **Allow once** → jetzt ausführen
- **Always allow** → zur Zulassungsliste hinzufügen + ausführen
- **Deny** → blockieren

## Weiterleitung von Freigaben an Chat-Kanäle

Sie können Aufforderungen für Exec-Freigaben an jeden Chat-Kanal weiterleiten (einschließlich Plugin-Kanälen) und sie
mit `/approve` genehmigen. Dies verwendet die normale Pipeline für ausgehende Zustellung.

Konfiguration:
__OC_I18N_900006__
Antwort im Chat:
__OC_I18N_900007__
Der Befehl `/approve` verarbeitet sowohl Exec-Freigaben als auch Plugin-Freigaben. Wenn die ID nicht zu einer ausstehenden Exec-Freigabe passt, wird automatisch stattdessen nach Plugin-Freigaben gesucht.

### Weiterleitung von Plugin-Freigaben

Die Weiterleitung von Plugin-Freigaben verwendet dieselbe Zustellungspipeline wie Exec-Freigaben, hat aber eine eigene
unabhängige Konfiguration unter `approvals.plugin`. Das Aktivieren oder Deaktivieren der einen hat keine Auswirkungen auf die andere.
__OC_I18N_900008__
Die Konfigurationsstruktur ist identisch mit `approvals.exec`: `enabled`, `mode`, `agentFilter`,
`sessionFilter` und `targets` funktionieren gleich.

Kanäle, die gemeinsame interaktive Antworten unterstützen, stellen für Exec- und
Plugin-Freigaben dieselben Freigabeschaltflächen dar. Kanäle ohne gemeinsame interaktive UI greifen auf Klartext mit
Anweisungen für `/approve` zurück.

### Freigaben im selben Chat auf jedem Kanal

Wenn eine Exec- oder Plugin-Freigabeanforderung von einer zustellbaren Chat-Oberfläche stammt, kann derselbe Chat sie
nun standardmäßig mit `/approve` genehmigen. Das gilt für Kanäle wie Slack, Matrix und
Microsoft Teams zusätzlich zu den bereits vorhandenen Abläufen in Web-UI und Terminal-UI.

Dieser gemeinsame Pfad über Textbefehle verwendet das normale Kanal-Authentifizierungsmodell für diese Unterhaltung. Wenn der
ursprüngliche Chat bereits Befehle senden und Antworten empfangen kann, benötigen Freigabeanforderungen keinen
separaten nativen Zustelladapter mehr, nur damit sie ausstehend bleiben.

Discord und Telegram unterstützen ebenfalls `/approve` im selben Chat, aber diese Kanäle verwenden weiterhin ihre
aufgelöste Liste zulässiger Genehmiger zur Autorisierung, auch wenn die native Freigabezustellung deaktiviert ist.

Für Telegram und andere native Freigabe-Clients, die das Gateway direkt aufrufen,
ist dieses Fallback absichtlich auf Fehler vom Typ „Freigabe nicht gefunden“ begrenzt. Eine echte
Exec-Freigabeverweigerung bzw. ein echter Fehler wird nicht stillschweigend als Plugin-Freigabe erneut versucht.

### Native Freigabezustellung

Einige Kanäle können außerdem als native Freigabe-Clients fungieren. Native Clients ergänzen Genehmiger-DMs, Fanout an den Ursprungs-Chat
und kanalspezifische interaktive UX für Freigaben zusätzlich zum gemeinsamen `/approve`-Ablauf im selben Chat.

Wenn native Freigabekarten/-schaltflächen verfügbar sind, ist diese native UI der primäre
agentseitige Pfad. Der Agent sollte dann nicht zusätzlich einen doppelten einfachen Chat-
Befehl `/approve` ausgeben, es sei denn, das Tool-Ergebnis sagt, dass Chat-Freigaben nicht verfügbar sind oder
eine manuelle Freigabe der einzige verbleibende Pfad ist.

Allgemeines Modell:

- die Host-Exec-Richtlinie entscheidet weiterhin, ob eine Exec-Freigabe erforderlich ist
- `approvals.exec` steuert die Weiterleitung von Freigabeaufforderungen an andere Chat-Ziele
- `channels.<channel>.execApprovals` steuert, ob dieser Kanal als nativer Freigabe-Client fungiert

Native Freigabe-Clients aktivieren automatisch DM-first-Zustellung, wenn alle folgenden Bedingungen erfüllt sind:

- der Kanal unterstützt native Freigabezustellung
- Genehmiger können aus explizitem `execApprovals.approvers` oder den
  dokumentierten Fallback-Quellen dieses Kanals aufgelöst werden
- `channels.<channel>.execApprovals.enabled` ist nicht gesetzt oder `"auto"`

Setzen Sie `enabled: false`, um einen nativen Freigabe-Client explizit zu deaktivieren. Setzen Sie `enabled: true`, um ihn
zu erzwingen, wenn Genehmiger aufgelöst werden. Öffentliche Zustellung an den Ursprungs-Chat bleibt explizit über
`channels.<channel>.execApprovals.target`.

FAQ: [Warum gibt es zwei Konfigurationen für Exec-Freigaben bei Chat-Freigaben?](/help/faq#why-are-there-two-exec-approval-configs-for-chat-approvals)

- Discord: `channels.discord.execApprovals.*`
- Slack: `channels.slack.execApprovals.*`
- Telegram: `channels.telegram.execApprovals.*`

Diese nativen Freigabe-Clients ergänzen DM-Routing und optionales Fanout an den Kanal zusätzlich zum gemeinsamen
`/approve`-Ablauf im selben Chat und den gemeinsamen Freigabeschaltflächen.

Gemeinsames Verhalten:

- Slack, Matrix, Microsoft Teams und ähnliche zustellbare Chats verwenden das normale Kanal-Authentifizierungsmodell
  für `/approve` im selben Chat
- wenn ein nativer Freigabe-Client automatisch aktiviert wird, ist das Standardziel für die native Zustellung Genehmiger-DMs
- für Discord und Telegram können nur aufgelöste Genehmiger genehmigen oder verweigern
- Discord-Genehmiger können explizit sein (`execApprovals.approvers`) oder aus `commands.ownerAllowFrom` abgeleitet werden
- Telegram-Genehmiger können explizit sein (`execApprovals.approvers`) oder aus bestehender Eigentümerkonfiguration abgeleitet werden (`allowFrom`, plus `defaultTo` für Direktnachrichten, wo unterstützt)
- Slack-Genehmiger können explizit sein (`execApprovals.approvers`) oder aus `commands.ownerAllowFrom` abgeleitet werden
- native Slack-Schaltflächen behalten die Art der Freigabe-ID bei, sodass `plugin:`-IDs Plugin-Freigaben
  ohne eine zweite Slack-lokale Fallback-Ebene auflösen können
- natives Matrix-DM-/Kanal-Routing und Reaktionskürzel verarbeiten sowohl Exec- als auch Plugin-Freigaben;
  die Plugin-Autorisierung kommt weiterhin von `channels.matrix.dm.allowFrom`
- der Anforderer muss kein Genehmiger sein
- der Ursprungs-Chat kann direkt mit `/approve` genehmigen, wenn dieser Chat bereits Befehle und Antworten unterstützt
- native Discord-Freigabeschaltflächen routen nach Art der Freigabe-ID: `plugin:`-IDs gehen
  direkt zu Plugin-Freigaben, alles andere zu Exec-Freigaben
- native Telegram-Freigabeschaltflächen folgen demselben begrenzten Exec-zu-Plugin-Fallback wie `/approve`
- wenn natives `target` die Zustellung an den Ursprungs-Chat aktiviert, enthalten Freigabeaufforderungen den Befehlstext
- ausstehende Exec-Freigaben laufen standardmäßig nach 30 Minuten ab
- wenn keine Operator-UI oder kein konfigurierter Freigabe-Client die Anforderung annehmen kann, fällt die Aufforderung auf `askFallback` zurück

Telegram verwendet standardmäßig Genehmiger-DMs (`target: "dm"`). Sie können zu `channel` oder `both` wechseln, wenn Sie
möchten, dass Freigabeaufforderungen auch im ursprünglichen Telegram-Chat/-Thema erscheinen. Bei Telegram-Forenthemen
bewahrt OpenClaw das Thema für die Freigabeaufforderung und die Folgeaktion nach der Freigabe.

Siehe:

- [Discord](/channels/discord)
- [Telegram](/channels/telegram)

### macOS-IPC-Ablauf
__OC_I18N_900009__
Sicherheitshinweise:

- Unix-Socket-Modus `0600`, Token wird in `exec-approvals.json` gespeichert.
- Same-UID-Peer-Prüfung.
- Challenge/Response (Nonce + HMAC-Token + Request-Hash) + kurze TTL.

## Systemereignisse

Der Lebenszyklus von Exec wird als Systemnachrichten angezeigt:

- `Exec running` (nur wenn der Befehl den Schwellenwert für die Laufmeldung überschreitet)
- `Exec finished`
- `Exec denied`

Diese werden in die Sitzung des Agents gepostet, nachdem der Node das Ereignis gemeldet hat.
Exec-Freigaben auf dem Gateway-Host geben dieselben Lebenszyklusereignisse aus, wenn der Befehl abgeschlossen ist (und optional, wenn er länger als den Schwellenwert läuft).
Durch Freigaben geschützte Execs verwenden die Freigabe-ID in diesen Nachrichten erneut als `runId`, damit sie leicht zugeordnet werden können.

## Verhalten bei verweigerter Freigabe

Wenn eine asynchrone Exec-Freigabe verweigert wird, verhindert OpenClaw, dass der Agent
Ausgabe aus einer früheren Ausführung desselben Befehls in der Sitzung wiederverwendet. Der Grund für die Verweigerung
wird mit einem expliziten Hinweis weitergegeben, dass keine Befehlsausgabe verfügbar ist; das verhindert,
dass der Agent behauptet, es gebe neue Ausgabe, oder den verweigerten Befehl mit
veralteten Ergebnissen aus einer früheren erfolgreichen Ausführung wiederholt.

## Auswirkungen

- **full** ist leistungsstark; bevorzugen Sie nach Möglichkeit Zulassungslisten.
- **ask** bindet Sie ein, ermöglicht aber weiterhin schnelle Freigaben.
- Zulassungslisten pro Agent verhindern, dass Freigaben eines Agents in andere übergreifen.
- Freigaben gelten nur für Host-Exec-Anforderungen von **autorisierten Absendern**. Nicht autorisierte Absender können kein `/exec` ausführen.
- `/exec security=full` ist eine sitzungsbezogene Komfortfunktion für autorisierte Operatoren und überspringt Freigaben absichtlich.
  Um Host-Exec hart zu blockieren, setzen Sie die Freigabesicherheit auf `deny` oder verweigern Sie das Tool `exec` über die Tool-Richtlinie.

Verwandt:

- [Exec-Tool](/de/tools/exec)
- [Elevated-Modus](/de/tools/elevated)
- [Skills](/de/tools/skills)

## Verwandt

- [Exec](/de/tools/exec) — Tool zur Ausführung von Shell-Befehlen
- [Sandboxing](/de/gateway/sandboxing) — Sandbox-Modi und Workspace-Zugriff
- [Security](/de/gateway/security) — Sicherheitsmodell und Härtung
- [Sandbox vs Tool Policy vs Elevated](/de/gateway/sandbox-vs-tool-policy-vs-elevated) — wann welches verwendet werden sollte
