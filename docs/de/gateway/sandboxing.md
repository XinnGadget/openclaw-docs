---
read_when: You want a dedicated explanation of sandboxing or need to tune agents.defaults.sandbox.
status: active
summary: 'Wie OpenClaw-Sandboxing funktioniert: Modi, Geltungsbereiche, Workspace-Zugriff und Bilder'
title: Sandboxing
x-i18n:
    generated_at: "2026-04-14T02:08:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2573d0d7462f63a68eb1750e5432211522ff5b42989a17379d3e188468bbce52
    source_path: gateway/sandboxing.md
    workflow: 15
---

# Sandboxing

OpenClaw kann **Tools innerhalb von Sandbox-Backends** ausführen, um den Explosionsradius zu verringern.
Dies ist **optional** und wird über die Konfiguration gesteuert (`agents.defaults.sandbox` oder
`agents.list[].sandbox`). Wenn Sandboxing deaktiviert ist, werden Tools auf dem Host ausgeführt.
Das Gateway bleibt auf dem Host; die Tool-Ausführung läuft in einer isolierten Sandbox,
wenn sie aktiviert ist.

Dies ist keine perfekte Sicherheitsgrenze, aber es schränkt den Zugriff auf Dateisystem
und Prozesse erheblich ein, wenn das Modell etwas Dummes tut.

## Was in die Sandbox kommt

- Tool-Ausführung (`exec`, `read`, `write`, `edit`, `apply_patch`, `process` usw.).
- Optionaler Browser in Sandbox (`agents.defaults.sandbox.browser`).
  - Standardmäßig startet der Sandbox-Browser automatisch (stellt sicher, dass CDP erreichbar ist), wenn das Browser-Tool ihn benötigt.
    Konfigurieren Sie dies über `agents.defaults.sandbox.browser.autoStart` und `agents.defaults.sandbox.browser.autoStartTimeoutMs`.
  - Standardmäßig verwenden Sandbox-Browser-Container ein dediziertes Docker-Netzwerk (`openclaw-sandbox-browser`) anstelle des globalen `bridge`-Netzwerks.
    Konfigurieren Sie dies mit `agents.defaults.sandbox.browser.network`.
  - Optional beschränkt `agents.defaults.sandbox.browser.cdpSourceRange` eingehenden CDP-Zugriff am Container-Rand mit einer CIDR-Allowlist (zum Beispiel `172.21.0.1/32`).
  - Der noVNC-Beobachterzugriff ist standardmäßig passwortgeschützt; OpenClaw gibt eine kurzlebige Token-URL aus, die eine lokale Bootstrap-Seite bereitstellt und noVNC mit dem Passwort im URL-Fragment öffnet (nicht in Query-/Header-Logs).
  - `agents.defaults.sandbox.browser.allowHostControl` erlaubt es Sessions in der Sandbox, den Host-Browser explizit anzusteuern.
  - Optionale Allowlists begrenzen `target: "custom"`: `allowedControlUrls`, `allowedControlHosts`, `allowedControlPorts`.

Nicht in der Sandbox:

- Der Gateway-Prozess selbst.
- Jedes Tool, das explizit außerhalb der Sandbox ausgeführt werden darf (z. B. `tools.elevated`).
  - **Erhöhtes `exec` umgeht das Sandboxing und verwendet den konfigurierten Escape-Pfad (`gateway` standardmäßig oder `node`, wenn das `exec`-Ziel `node` ist).**
  - Wenn Sandboxing deaktiviert ist, ändert `tools.elevated` die Ausführung nicht (läuft bereits auf dem Host). Siehe [Elevated Mode](/de/tools/elevated).

## Modi

`agents.defaults.sandbox.mode` steuert, **wann** Sandboxing verwendet wird:

- `"off"`: kein Sandboxing.
- `"non-main"`: Sandbox nur für **Nicht-Haupt-**Sessions (Standard, wenn normale Chats auf dem Host laufen sollen).
- `"all"`: jede Session läuft in einer Sandbox.
  Hinweis: `"non-main"` basiert auf `session.mainKey` (Standard `"main"`), nicht auf der Agent-ID.
  Gruppen-/Kanal-Sessions verwenden ihre eigenen Schlüssel, zählen also als Nicht-Haupt-Sessions und werden in eine Sandbox gesetzt.

## Geltungsbereich

`agents.defaults.sandbox.scope` steuert, **wie viele Container** erstellt werden:

- `"agent"` (Standard): ein Container pro Agent.
- `"session"`: ein Container pro Session.
- `"shared"`: ein Container, der von allen Sessions in der Sandbox gemeinsam genutzt wird.

## Backend

`agents.defaults.sandbox.backend` steuert, **welche Laufzeitumgebung** die Sandbox bereitstellt:

- `"docker"` (Standard): lokale Docker-basierte Sandbox-Laufzeit.
- `"ssh"`: generische SSH-basierte Remote-Sandbox-Laufzeit.
- `"openshell"`: OpenShell-basierte Sandbox-Laufzeit.

SSH-spezifische Konfiguration befindet sich unter `agents.defaults.sandbox.ssh`.
OpenShell-spezifische Konfiguration befindet sich unter `plugins.entries.openshell.config`.

### Ein Backend auswählen

|                     | Docker                           | SSH                            | OpenShell                                                   |
| ------------------- | -------------------------------- | ------------------------------ | ----------------------------------------------------------- |
| **Wo es läuft**     | Lokaler Container                | Jeder per SSH erreichbare Host | Von OpenShell verwaltete Sandbox                            |
| **Einrichtung**     | `scripts/sandbox-setup.sh`       | SSH-Schlüssel + Zielhost       | OpenShell-Plugin aktiviert                                  |
| **Workspace-Modell** | Bind-Mount oder Kopie            | Remote-kanonisch (einmal seeden) | `mirror` oder `remote`                                      |
| **Netzwerksteuerung** | `docker.network` (Standard: none) | Hängt vom Remote-Host ab       | Hängt von OpenShell ab                                      |
| **Browser-Sandbox** | Unterstützt                      | Nicht unterstützt              | Noch nicht unterstützt                                      |
| **Bind-Mounts**     | `docker.binds`                   | N/V                            | N/V                                                         |
| **Am besten geeignet für** | Lokale Entwicklung, vollständige Isolation | Auslagerung auf einen Remote-Rechner | Verwaltete Remote-Sandboxes mit optionaler bidirektionaler Synchronisierung |

### Docker-Backend

Das Docker-Backend ist die Standard-Laufzeit und führt Tools sowie Browser in der Sandbox lokal über den Docker-Daemon-Socket (`/var/run/docker.sock`) aus. Die Isolation der Sandbox-Container wird durch Docker-Namespaces bestimmt.

**Docker-out-of-Docker-(DooD)-Einschränkungen**:
Wenn Sie das OpenClaw Gateway selbst als Docker-Container bereitstellen, orchestriert es Geschwister-Container für die Sandbox über den Docker-Socket des Hosts (DooD). Daraus ergibt sich eine spezielle Einschränkung beim Pfad-Mapping:

- **Konfiguration erfordert Host-Pfade**: Die `workspace`-Konfiguration in `openclaw.json` MUSS den **absoluten Pfad des Hosts** enthalten (z. B. `/home/user/.openclaw/workspaces`), nicht den internen Pfad des Gateway-Containers. Wenn OpenClaw den Docker-Daemon auffordert, eine Sandbox zu starten, wertet der Daemon Pfade relativ zum Namespace des Host-Betriebssystems aus, nicht zum Gateway-Namespace.
- **FS-Bridge-Parität (identisches Volume-Mapping)**: Der native OpenClaw-Gateway-Prozess schreibt außerdem Heartbeat- und Bridge-Dateien in das `workspace`-Verzeichnis. Da das Gateway denselben String (den Host-Pfad) innerhalb seiner eigenen containerisierten Umgebung auswertet, MUSS die Gateway-Bereitstellung ein identisches Volume-Mapping enthalten, das den Host-Namespace nativ verknüpft (`-v /home/user/.openclaw:/home/user/.openclaw`).

Wenn Sie Pfade intern mappen, ohne absolute Host-Parität zu gewährleisten, wirft OpenClaw nativ einen `EACCES`-Berechtigungsfehler, wenn versucht wird, seinen Heartbeat innerhalb der Container-Umgebung zu schreiben, weil der vollständig qualifizierte Pfadstring nativ nicht existiert.

### SSH-Backend

Verwenden Sie `backend: "ssh"`, wenn OpenClaw `exec`, Dateitools und Medienlesevorgänge
auf einem beliebigen per SSH erreichbaren Rechner in einer Sandbox ausführen soll.

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "all",
        backend: "ssh",
        scope: "session",
        workspaceAccess: "rw",
        ssh: {
          target: "user@gateway-host:22",
          workspaceRoot: "/tmp/openclaw-sandboxes",
          strictHostKeyChecking: true,
          updateHostKeys: true,
          identityFile: "~/.ssh/id_ed25519",
          certificateFile: "~/.ssh/id_ed25519-cert.pub",
          knownHostsFile: "~/.ssh/known_hosts",
          // Oder verwenden Sie SecretRefs / Inline-Inhalte statt lokaler Dateien:
          // identityData: { source: "env", provider: "default", id: "SSH_IDENTITY" },
          // certificateData: { source: "env", provider: "default", id: "SSH_CERTIFICATE" },
          // knownHostsData: { source: "env", provider: "default", id: "SSH_KNOWN_HOSTS" },
        },
      },
    },
  },
}
```

So funktioniert es:

- OpenClaw erstellt pro Geltungsbereich ein Remote-Root unter `sandbox.ssh.workspaceRoot`.
- Bei der ersten Verwendung nach dem Erstellen oder Neuerstellen überträgt OpenClaw diesen Remote-Workspace einmalig aus dem lokalen Workspace.
- Danach werden `exec`, `read`, `write`, `edit`, `apply_patch`, promptbasierte Medienlesevorgänge und das Staging eingehender Medien direkt per SSH gegen den Remote-Workspace ausgeführt.
- OpenClaw synchronisiert Remote-Änderungen nicht automatisch zurück in den lokalen Workspace.

Authentifizierungsmaterial:

- `identityFile`, `certificateFile`, `knownHostsFile`: vorhandene lokale Dateien verwenden und über die OpenSSH-Konfiguration durchreichen.
- `identityData`, `certificateData`, `knownHostsData`: Inline-Strings oder SecretRefs verwenden. OpenClaw löst sie über den normalen Secrets-Laufzeit-Snapshot auf, schreibt sie mit `0600` in temporäre Dateien und löscht sie, wenn die SSH-Session endet.
- Wenn für denselben Eintrag sowohl `*File` als auch `*Data` gesetzt sind, gewinnt `*Data` für diese SSH-Session.

Dies ist ein **Remote-kanonisches** Modell. Der Remote-SSH-Workspace wird nach dem initialen Seeding zum tatsächlichen Sandbox-Status.

Wichtige Konsequenzen:

- Lokal auf dem Host vorgenommene Änderungen außerhalb von OpenClaw sind nach dem Seeding-Schritt remote nicht sichtbar, bis Sie die Sandbox neu erstellen.
- `openclaw sandbox recreate` löscht das Remote-Root pro Geltungsbereich und seedet es bei der nächsten Verwendung erneut aus dem lokalen Workspace.
- Browser-Sandboxing wird vom SSH-Backend nicht unterstützt.
- Einstellungen unter `sandbox.docker.*` gelten nicht für das SSH-Backend.

### OpenShell-Backend

Verwenden Sie `backend: "openshell"`, wenn OpenClaw Tools in einer
von OpenShell verwalteten Remote-Umgebung in einer Sandbox ausführen soll. Die vollständige Einrichtungsanleitung, Konfigurationsreferenz
und den Vergleich der Workspace-Modi finden Sie auf der dedizierten
[OpenShell-Seite](/de/gateway/openshell).

OpenShell verwendet denselben zentralen SSH-Transport und dieselbe Remote-Dateisystem-Bridge wie das
generische SSH-Backend und ergänzt OpenShell-spezifische Lifecycle-Abläufe
(`sandbox create/get/delete`, `sandbox ssh-config`) sowie den optionalen
Workspace-Modus `mirror`.

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "all",
        backend: "openshell",
        scope: "session",
        workspaceAccess: "rw",
      },
    },
  },
  plugins: {
    entries: {
      openshell: {
        enabled: true,
        config: {
          from: "openclaw",
          mode: "remote", // mirror | remote
          remoteWorkspaceDir: "/sandbox",
          remoteAgentWorkspaceDir: "/agent",
        },
      },
    },
  },
}
```

OpenShell-Modi:

- `mirror` (Standard): Der lokale Workspace bleibt kanonisch. OpenClaw synchronisiert lokale Dateien vor `exec` in OpenShell und synchronisiert den Remote-Workspace nach `exec` zurück.
- `remote`: Der OpenShell-Workspace ist kanonisch, nachdem die Sandbox erstellt wurde. OpenClaw seedet den Remote-Workspace einmalig aus dem lokalen Workspace, danach laufen Dateitools und `exec` direkt gegen die Remote-Sandbox, ohne Änderungen zurückzusynchronisieren.

Details zum Remote-Transport:

- OpenClaw fordert von OpenShell eine sandboxspezifische SSH-Konfiguration über `openshell sandbox ssh-config <name>` an.
- Der Kern schreibt diese SSH-Konfiguration in eine temporäre Datei, öffnet die SSH-Session und verwendet dieselbe Remote-Dateisystem-Bridge wie bei `backend: "ssh"` wieder.
- Nur im Modus `mirror` unterscheidet sich der Lifecycle: vor `exec` lokal nach remote synchronisieren, danach zurücksynchronisieren.

Aktuelle Einschränkungen von OpenShell:

- Browser in der Sandbox wird noch nicht unterstützt
- `sandbox.docker.binds` wird vom OpenShell-Backend nicht unterstützt
- Docker-spezifische Laufzeitparameter unter `sandbox.docker.*` gelten weiterhin nur für das Docker-Backend

#### Workspace-Modi

OpenShell hat zwei Workspace-Modelle. Das ist in der Praxis der wichtigste Teil.

##### `mirror`

Verwenden Sie `plugins.entries.openshell.config.mode: "mirror"`, wenn der **lokale Workspace kanonisch bleiben** soll.

Verhalten:

- Vor `exec` synchronisiert OpenClaw den lokalen Workspace in die OpenShell-Sandbox.
- Nach `exec` synchronisiert OpenClaw den Remote-Workspace zurück in den lokalen Workspace.
- Dateitools arbeiten weiterhin über die Sandbox-Bridge, aber der lokale Workspace bleibt zwischen den Turns die Quelle der Wahrheit.

Verwenden Sie dies, wenn:

- Sie Dateien lokal außerhalb von OpenClaw bearbeiten und möchten, dass diese Änderungen automatisch in der Sandbox erscheinen
- sich die OpenShell-Sandbox möglichst ähnlich wie das Docker-Backend verhalten soll
- der Host-Workspace Sandbox-Schreibvorgänge nach jedem `exec`-Turn widerspiegeln soll

Kompromiss:

- zusätzlicher Synchronisierungsaufwand vor und nach `exec`

##### `remote`

Verwenden Sie `plugins.entries.openshell.config.mode: "remote"`, wenn der **OpenShell-Workspace kanonisch werden** soll.

Verhalten:

- Wenn die Sandbox zum ersten Mal erstellt wird, seedet OpenClaw den Remote-Workspace einmalig aus dem lokalen Workspace.
- Danach arbeiten `exec`, `read`, `write`, `edit` und `apply_patch` direkt gegen den Remote-OpenShell-Workspace.
- OpenClaw synchronisiert Remote-Änderungen nach `exec` **nicht** zurück in den lokalen Workspace.
- Medienlesevorgänge zur Prompt-Zeit funktionieren weiterhin, weil Datei- und Medien-Tools über die Sandbox-Bridge lesen, anstatt von einem lokalen Host-Pfad auszugehen.
- Der Transport erfolgt per SSH in die OpenShell-Sandbox, die von `openshell sandbox ssh-config` zurückgegeben wird.

Wichtige Konsequenzen:

- Wenn Sie Dateien nach dem Seeding-Schritt auf dem Host außerhalb von OpenClaw bearbeiten, sieht die Remote-Sandbox diese Änderungen **nicht** automatisch.
- Wenn die Sandbox neu erstellt wird, wird der Remote-Workspace erneut aus dem lokalen Workspace geseedet.
- Bei `scope: "agent"` oder `scope: "shared"` wird dieser Remote-Workspace auf genau diesem Geltungsbereich gemeinsam genutzt.

Verwenden Sie dies, wenn:

- die Sandbox primär auf der Remote-Seite von OpenShell leben soll
- Sie geringeren Synchronisierungsaufwand pro Turn wünschen
- Sie nicht möchten, dass lokale Bearbeitungen auf dem Host stillschweigend den Zustand der Remote-Sandbox überschreiben

Wählen Sie `mirror`, wenn Sie die Sandbox als temporäre Ausführungsumgebung betrachten.
Wählen Sie `remote`, wenn Sie die Sandbox als den eigentlichen Workspace betrachten.

#### OpenShell-Lifecycle

OpenShell-Sandboxes werden weiterhin über den normalen Sandbox-Lifecycle verwaltet:

- `openclaw sandbox list` zeigt OpenShell-Laufzeiten ebenso wie Docker-Laufzeiten an
- `openclaw sandbox recreate` löscht die aktuelle Laufzeit und lässt OpenClaw sie bei der nächsten Verwendung neu erstellen
- Die Bereinigungslogik ist ebenfalls backendbewusst

Für den Modus `remote` ist `recreate` besonders wichtig:

- `recreate` löscht den kanonischen Remote-Workspace für diesen Geltungsbereich
- bei der nächsten Verwendung wird ein frischer Remote-Workspace aus dem lokalen Workspace geseedet

Für den Modus `mirror` setzt `recreate` hauptsächlich die Remote-Ausführungsumgebung zurück,
weil der lokale Workspace ohnehin kanonisch bleibt.

## Workspace-Zugriff

`agents.defaults.sandbox.workspaceAccess` steuert, **was die Sandbox sehen kann**:

- `"none"` (Standard): Tools sehen einen Sandbox-Workspace unter `~/.openclaw/sandboxes`.
- `"ro"`: bindet den Agent-Workspace schreibgeschützt unter `/agent` ein (deaktiviert `write`/`edit`/`apply_patch`).
- `"rw"`: bindet den Agent-Workspace mit Lese-/Schreibzugriff unter `/workspace` ein.

Mit dem OpenShell-Backend:

- im Modus `mirror` bleibt der lokale Workspace zwischen `exec`-Turns weiterhin die kanonische Quelle
- im Modus `remote` ist nach dem initialen Seeding der Remote-OpenShell-Workspace die kanonische Quelle
- `workspaceAccess: "ro"` und `"none"` schränken Schreibverhalten weiterhin auf dieselbe Weise ein

Eingehende Medien werden in den aktiven Sandbox-Workspace kopiert (`media/inbound/*`).
Hinweis zu Skills: Das Tool `read` ist auf die Sandbox-Wurzel beschränkt. Bei `workspaceAccess: "none"`
spiegelt OpenClaw geeignete Skills in den Sandbox-Workspace (`.../skills`),
damit sie gelesen werden können. Mit `"rw"` sind Workspace-Skills unter
`/workspace/skills` lesbar.

## Benutzerdefinierte Bind-Mounts

`agents.defaults.sandbox.docker.binds` bindet zusätzliche Host-Verzeichnisse in den Container ein.
Format: `host:container:mode` (z. B. `"/home/user/source:/source:rw"`).

Globale und agent-spezifische Bind-Mounts werden **zusammengeführt** (nicht ersetzt). Unter `scope: "shared"` werden agent-spezifische Bind-Mounts ignoriert.

`agents.defaults.sandbox.browser.binds` bindet zusätzliche Host-Verzeichnisse nur in den **Browser-Container der Sandbox** ein.

- Wenn gesetzt (einschließlich `[]`), ersetzt es `agents.defaults.sandbox.docker.binds` für den Browser-Container.
- Wenn nicht gesetzt, greift der Browser-Container auf `agents.defaults.sandbox.docker.binds` zurück (abwärtskompatibel).

Beispiel (schreibgeschützter Quellcode + ein zusätzliches Datenverzeichnis):

```json5
{
  agents: {
    defaults: {
      sandbox: {
        docker: {
          binds: ["/home/user/source:/source:ro", "/var/data/myapp:/data:ro"],
        },
      },
    },
    list: [
      {
        id: "build",
        sandbox: {
          docker: {
            binds: ["/mnt/cache:/cache:rw"],
          },
        },
      },
    ],
  },
}
```

Sicherheitshinweise:

- Bind-Mounts umgehen das Sandbox-Dateisystem: Sie geben Host-Pfade mit dem jeweils gesetzten Modus frei (`:ro` oder `:rw`).
- OpenClaw blockiert gefährliche Bind-Quellen (zum Beispiel: `docker.sock`, `/etc`, `/proc`, `/sys`, `/dev` und übergeordnete Mounts, die diese freigeben würden).
- OpenClaw blockiert außerdem gängige Credential-Wurzeln im Home-Verzeichnis wie `~/.aws`, `~/.cargo`, `~/.config`, `~/.docker`, `~/.gnupg`, `~/.netrc`, `~/.npm` und `~/.ssh`.
- Die Bind-Validierung ist nicht nur String-Matching. OpenClaw normalisiert den Quellpfad und löst ihn dann erneut über den tiefsten vorhandenen Vorfahren auf, bevor blockierte Pfade und erlaubte Wurzeln erneut geprüft werden.
- Das bedeutet, dass auch Symlink-Escapes über Elternpfade weiterhin fail-closed sind, selbst wenn das endgültige Blatt noch nicht existiert. Beispiel: `/workspace/run-link/new-file` wird weiterhin als `/var/run/...` aufgelöst, wenn `run-link` dorthin zeigt.
- Erlaubte Quellwurzeln werden auf dieselbe Weise kanonisiert, daher wird ein Pfad, der nur vor der Symlink-Auflösung so aussieht, als läge er in der Allowlist, weiterhin als `outside allowed roots` abgelehnt.
- Sensible Mounts (Secrets, SSH-Schlüssel, Service-Credentials) sollten `:ro` sein, sofern nicht unbedingt erforderlich.
- Kombinieren Sie dies mit `workspaceAccess: "ro"`, wenn Sie nur Lesezugriff auf den Workspace benötigen; die Bind-Modi bleiben unabhängig.
- Siehe [Sandbox vs Tool Policy vs Elevated](/de/gateway/sandbox-vs-tool-policy-vs-elevated), um zu verstehen, wie Bind-Mounts mit Tool-Richtlinien und erhöhtem `exec` zusammenspielen.

## Images + Einrichtung

Standard-Docker-Image: `openclaw-sandbox:bookworm-slim`

Einmalig bauen:

```bash
scripts/sandbox-setup.sh
```

Hinweis: Das Standard-Image enthält **kein** Node. Wenn ein Skill Node (oder
andere Laufzeitumgebungen) benötigt, backen Sie entweder ein benutzerdefiniertes Image oder installieren es über
`sandbox.docker.setupCommand` (erfordert Netzwerk-Egress + beschreibbare Root +
Root-Benutzer).

Wenn Sie ein funktionsreicheres Sandbox-Image mit gängigen Tools (zum Beispiel
`curl`, `jq`, `nodejs`, `python3`, `git`) möchten, bauen Sie:

```bash
scripts/sandbox-common-setup.sh
```

Setzen Sie dann `agents.defaults.sandbox.docker.image` auf
`openclaw-sandbox-common:bookworm-slim`.

Image für Browser in der Sandbox:

```bash
scripts/sandbox-browser-setup.sh
```

Standardmäßig laufen Docker-Sandbox-Container **ohne Netzwerk**.
Überschreiben Sie dies mit `agents.defaults.sandbox.docker.network`.

Das gebündelte Browser-Image für die Sandbox verwendet außerdem konservative Chromium-Startstandards
für containerisierte Workloads. Zu den aktuellen Container-Standards gehören:

- `--remote-debugging-address=127.0.0.1`
- `--remote-debugging-port=<derived from OPENCLAW_BROWSER_CDP_PORT>`
- `--user-data-dir=${HOME}/.chrome`
- `--no-first-run`
- `--no-default-browser-check`
- `--disable-3d-apis`
- `--disable-gpu`
- `--disable-dev-shm-usage`
- `--disable-background-networking`
- `--disable-extensions`
- `--disable-features=TranslateUI`
- `--disable-breakpad`
- `--disable-crash-reporter`
- `--disable-software-rasterizer`
- `--no-zygote`
- `--metrics-recording-only`
- `--renderer-process-limit=2`
- `--no-sandbox` und `--disable-setuid-sandbox`, wenn `noSandbox` aktiviert ist.
- Die drei Grafik-Hardening-Flags (`--disable-3d-apis`,
  `--disable-software-rasterizer`, `--disable-gpu`) sind optional und nützlich,
  wenn Container keine GPU-Unterstützung haben. Setzen Sie `OPENCLAW_BROWSER_DISABLE_GRAPHICS_FLAGS=0`,
  wenn Ihr Workload WebGL oder andere 3D-/Browser-Funktionen benötigt.
- `--disable-extensions` ist standardmäßig aktiviert und kann mit
  `OPENCLAW_BROWSER_DISABLE_EXTENSIONS=0` für ablauforientierte Erweiterungsszenarien deaktiviert werden.
- `--renderer-process-limit=2` wird über
  `OPENCLAW_BROWSER_RENDERER_PROCESS_LIMIT=<N>` gesteuert, wobei `0` den Chromium-Standard beibehält.

Wenn Sie ein anderes Laufzeitprofil benötigen, verwenden Sie ein benutzerdefiniertes Browser-Image und stellen
einen eigenen Entrypoint bereit. Für lokale (nicht containerisierte) Chromium-Profile verwenden Sie
`browser.extraArgs`, um zusätzliche Start-Flags anzuhängen.

Sicherheitsstandards:

- `network: "host"` ist blockiert.
- `network: "container:<id>"` ist standardmäßig blockiert (Umgehungsrisiko durch Namespace-Join).
- Break-Glass-Override: `agents.defaults.sandbox.docker.dangerouslyAllowContainerNamespaceJoin: true`.

Docker-Installationen und das containerisierte Gateway sind hier beschrieben:
[Docker](/de/install/docker)

Für Docker-Gateway-Deployments kann `scripts/docker/setup.sh` die Sandbox-Konfiguration bootstrappen.
Setzen Sie `OPENCLAW_SANDBOX=1` (oder `true`/`yes`/`on`), um diesen Pfad zu aktivieren. Sie können
den Socket-Speicherort mit `OPENCLAW_DOCKER_SOCKET` überschreiben. Vollständige Einrichtung und Env-Referenz:
[Docker](/de/install/docker#agent-sandbox).

## setupCommand (einmalige Container-Einrichtung)

`setupCommand` wird **einmal** ausgeführt, nachdem der Sandbox-Container erstellt wurde (nicht bei jedem Lauf).
Es wird innerhalb des Containers über `sh -lc` ausgeführt.

Pfade:

- Global: `agents.defaults.sandbox.docker.setupCommand`
- Pro Agent: `agents.list[].sandbox.docker.setupCommand`

Häufige Fallstricke:

- Standardmäßig ist `docker.network` `"none"` (kein Egress), daher schlagen Paketinstallationen fehl.
- `docker.network: "container:<id>"` erfordert `dangerouslyAllowContainerNamespaceJoin: true` und ist nur als Break-Glass gedacht.
- `readOnlyRoot: true` verhindert Schreibzugriffe; setzen Sie `readOnlyRoot: false` oder backen Sie ein benutzerdefiniertes Image.
- `user` muss für Paketinstallationen Root sein (lassen Sie `user` weg oder setzen Sie `user: "0:0"`).
- Sandbox-`exec` übernimmt **nicht** das Host-`process.env`. Verwenden Sie
  `agents.defaults.sandbox.docker.env` (oder ein benutzerdefiniertes Image) für Skill-API-Schlüssel.

## Tool-Richtlinien + Escape-Hatches

Allow/Deny-Richtlinien für Tools gelten weiterhin vor den Sandbox-Regeln. Wenn ein Tool global
oder pro Agent verweigert wird, bringt Sandboxing es nicht zurück.

`tools.elevated` ist ein expliziter Escape-Hatch, der `exec` außerhalb der Sandbox ausführt (`gateway` standardmäßig oder `node`, wenn das `exec`-Ziel `node` ist).
Direktiven für `/exec` gelten nur für autorisierte Absender und bleiben pro Session bestehen; um `exec` hart zu deaktivieren,
verwenden Sie Tool-Policy-Deny (siehe [Sandbox vs Tool Policy vs Elevated](/de/gateway/sandbox-vs-tool-policy-vs-elevated)).

Debugging:

- Verwenden Sie `openclaw sandbox explain`, um den effektiven Sandbox-Modus, die Tool-Richtlinie und Konfigurationsschlüssel für Korrekturen zu prüfen.
- Siehe [Sandbox vs Tool Policy vs Elevated](/de/gateway/sandbox-vs-tool-policy-vs-elevated) für das mentale Modell zu „Warum ist das blockiert?“.
  Halten Sie es streng eingeschränkt.

## Überschreibungen für mehrere Agenten

Jeder Agent kann Sandbox + Tools überschreiben:
`agents.list[].sandbox` und `agents.list[].tools` (plus `agents.list[].tools.sandbox.tools` für die Sandbox-Tool-Richtlinie).
Siehe [Multi-Agent Sandbox & Tools](/de/tools/multi-agent-sandbox-tools) für Vorrangregeln.

## Minimales Aktivierungsbeispiel

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main",
        scope: "session",
        workspaceAccess: "none",
      },
    },
  },
}
```

## Verwandte Dokumente

- [OpenShell](/de/gateway/openshell) -- Einrichtung des verwalteten Sandbox-Backends, Workspace-Modi und Konfigurationsreferenz
- [Sandbox Configuration](/de/gateway/configuration-reference#agentsdefaultssandbox)
- [Sandbox vs Tool Policy vs Elevated](/de/gateway/sandbox-vs-tool-policy-vs-elevated) -- Debugging von „Warum ist das blockiert?“
- [Multi-Agent Sandbox & Tools](/de/tools/multi-agent-sandbox-tools) -- Überschreibungen pro Agent und Vorrangregeln
- [Security](/de/gateway/security)
