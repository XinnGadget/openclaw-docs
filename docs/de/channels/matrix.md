---
read_when:
    - Matrix in OpenClaw einrichten
    - Matrix-E2EE und Verifizierung konfigurieren
summary: Status der Matrix-Unterstützung, Einrichtung und Konfigurationsbeispiele
title: Matrix
x-i18n:
    generated_at: "2026-04-06T06:23:23Z"
    model: gpt-5.4
    provider: openai
    source_hash: 06f833bf0ede81bad69f140994c32e8cc5d1635764f95fc5db4fc5dc25f2b85e
    source_path: channels/matrix.md
    workflow: 15
---

# Matrix

Matrix ist das gebündelte Matrix-Kanal-Plugin für OpenClaw.
Es verwendet das offizielle `matrix-js-sdk` und unterstützt DMs, Räume, Threads, Medien, Reaktionen, Umfragen, Standort und E2EE.

## Gebündeltes Plugin

Matrix wird in aktuellen OpenClaw-Releases als gebündeltes Plugin ausgeliefert, daher
benötigen normale paketierte Builds keine separate Installation.

Wenn Sie einen älteren Build oder eine benutzerdefinierte Installation verwenden, die Matrix ausschließt,
installieren Sie es manuell:

Von npm installieren:

```bash
openclaw plugins install @openclaw/matrix
```

Von einem lokalen Checkout installieren:

```bash
openclaw plugins install ./path/to/local/matrix-plugin
```

Siehe [Plugins](/de/tools/plugin) für Plugin-Verhalten und Installationsregeln.

## Einrichtung

1. Stellen Sie sicher, dass das Matrix-Plugin verfügbar ist.
   - Aktuelle paketierte OpenClaw-Releases enthalten es bereits.
   - Ältere/benutzerdefinierte Installationen können es manuell mit den obigen Befehlen hinzufügen.
2. Erstellen Sie ein Matrix-Konto auf Ihrem Homeserver.
3. Konfigurieren Sie `channels.matrix` mit entweder:
   - `homeserver` + `accessToken`, oder
   - `homeserver` + `userId` + `password`.
4. Starten Sie das Gateway neu.
5. Starten Sie einen DM mit dem Bot oder laden Sie ihn in einen Raum ein.

Interaktive Einrichtungswege:

```bash
openclaw channels add
openclaw configure --section channels
```

Wonach der Matrix-Assistent tatsächlich fragt:

- Homeserver-URL
- Authentifizierungsmethode: Access-Token oder Passwort
- Benutzer-ID nur, wenn Sie Passwort-Authentifizierung wählen
- optionaler Gerätename
- ob E2EE aktiviert werden soll
- ob Matrix-Raumzugriff jetzt konfiguriert werden soll

Wichtiges Verhalten des Assistenten:

- Wenn für das ausgewählte Konto bereits Matrix-Authentifizierungs-Umgebungsvariablen vorhanden sind und für dieses Konto noch keine Authentifizierung in der Konfiguration gespeichert ist, bietet der Assistent eine Env-Verknüpfung an und schreibt nur `enabled: true` für dieses Konto.
- Wenn Sie interaktiv ein weiteres Matrix-Konto hinzufügen, wird der eingegebene Kontoname in die Konto-ID normalisiert, die in Konfiguration und Env-Variablen verwendet wird. Zum Beispiel wird `Ops Bot` zu `ops-bot`.
- DM-Allowlist-Eingabeaufforderungen akzeptieren sofort vollständige `@user:server`-Werte. Anzeigenamen funktionieren nur, wenn die Live-Verzeichnissuche genau eine Übereinstimmung findet; andernfalls fordert der Assistent Sie auf, es mit einer vollständigen Matrix-ID erneut zu versuchen.
- Raum-Allowlist-Eingabeaufforderungen akzeptieren Raum-IDs und Aliasse direkt. Sie können auch Namen beigetretener Räume live auflösen, aber nicht aufgelöste Namen werden bei der Einrichtung nur wie eingegeben beibehalten und später von der Laufzeit-Allowlist-Auflösung ignoriert. Bevorzugen Sie `!room:server` oder `#alias:server`.
- Die Laufzeitidentität für Raum/Sitzung verwendet die stabile Matrix-Raum-ID. In Räumen deklarierte Aliasse werden nur als Lookup-Eingaben verwendet, nicht als langfristiger Sitzungsschlüssel oder stabile Gruppenidentität.
- Um Raumnamen aufzulösen, bevor Sie sie speichern, verwenden Sie `openclaw channels resolve --channel matrix "Project Room"`.

Minimale tokenbasierte Einrichtung:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      dm: { policy: "pairing" },
    },
  },
}
```

Passwortbasierte Einrichtung (Token wird nach der Anmeldung zwischengespeichert):

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      userId: "@bot:example.org",
      password: "replace-me", // pragma: allowlist secret
      deviceName: "OpenClaw Gateway",
    },
  },
}
```

Matrix speichert zwischengespeicherte Anmeldedaten in `~/.openclaw/credentials/matrix/`.
Das Standardkonto verwendet `credentials.json`; benannte Konten verwenden `credentials-<account>.json`.
Wenn dort zwischengespeicherte Anmeldedaten vorhanden sind, betrachtet OpenClaw Matrix für Einrichtung, Doctor und Kanalstatus-Erkennung als konfiguriert, auch wenn die aktuelle Authentifizierung nicht direkt in der Konfiguration gesetzt ist.

Entsprechende Umgebungsvariablen (werden verwendet, wenn der Konfigurationsschlüssel nicht gesetzt ist):

- `MATRIX_HOMESERVER`
- `MATRIX_ACCESS_TOKEN`
- `MATRIX_USER_ID`
- `MATRIX_PASSWORD`
- `MATRIX_DEVICE_ID`
- `MATRIX_DEVICE_NAME`

Für Nicht-Standardkonten verwenden Sie kontobezogene Env-Variablen:

- `MATRIX_<ACCOUNT_ID>_HOMESERVER`
- `MATRIX_<ACCOUNT_ID>_ACCESS_TOKEN`
- `MATRIX_<ACCOUNT_ID>_USER_ID`
- `MATRIX_<ACCOUNT_ID>_PASSWORD`
- `MATRIX_<ACCOUNT_ID>_DEVICE_ID`
- `MATRIX_<ACCOUNT_ID>_DEVICE_NAME`

Beispiel für Konto `ops`:

- `MATRIX_OPS_HOMESERVER`
- `MATRIX_OPS_ACCESS_TOKEN`

Für die normalisierte Konto-ID `ops-bot` verwenden Sie:

- `MATRIX_OPS_X2D_BOT_HOMESERVER`
- `MATRIX_OPS_X2D_BOT_ACCESS_TOKEN`

Matrix maskiert Satzzeichen in Konto-IDs, um Kollisionen bei kontobezogenen Env-Variablen zu vermeiden.
Zum Beispiel wird `-` zu `_X2D_`, daher wird `ops-prod` zu `MATRIX_OPS_X2D_PROD_*`.

Der interaktive Assistent bietet die Env-Variablen-Verknüpfung nur an, wenn diese Auth-Env-Variablen bereits vorhanden sind und für das ausgewählte Konto noch keine Matrix-Authentifizierung in der Konfiguration gespeichert ist.

## Konfigurationsbeispiel

Dies ist eine praktische Basiskonfiguration mit DM-Pairing, Raum-Allowlist und aktiviertem E2EE:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      encryption: true,

      dm: {
        policy: "pairing",
        sessionScope: "per-room",
        threadReplies: "off",
      },

      groupPolicy: "allowlist",
      groupAllowFrom: ["@admin:example.org"],
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },

      autoJoin: "allowlist",
      autoJoinAllowlist: ["!roomid:example.org"],
      threadReplies: "inbound",
      replyToMode: "off",
      streaming: "partial",
    },
  },
}
```

`autoJoin` gilt allgemein für Matrix-Einladungen, nicht nur für Raum-/Gruppeneinladungen.
Dazu gehören auch neue DM-artige Einladungen. Zum Zeitpunkt der Einladung weiß OpenClaw nicht zuverlässig, ob der
eingeladene Raum letztlich als DM oder als Gruppe behandelt wird, daher durchlaufen alle Einladungen zuerst dieselbe
`autoJoin`-Entscheidung. `dm.policy` gilt weiterhin, nachdem der Bot beigetreten ist und der Raum
als DM klassifiziert wurde. Daher steuert `autoJoin` das Beitrittsverhalten, während `dm.policy` das Antwort-/Zugriffs-
verhalten steuert.

## Streaming-Vorschauen

Antwort-Streaming in Matrix ist optional.

Setzen Sie `channels.matrix.streaming` auf `"partial"`, wenn OpenClaw eine einzelne Live-Vorschau
als Antwort senden, diese Vorschau während der Texterzeugung durch das Modell an Ort und Stelle bearbeiten
und sie abschließen soll, wenn die Antwort fertig ist:

```json5
{
  channels: {
    matrix: {
      streaming: "partial",
    },
  },
}
```

- `streaming: "off"` ist der Standard. OpenClaw wartet auf die endgültige Antwort und sendet sie einmal.
- `streaming: "partial"` erstellt eine bearbeitbare Vorschau-Nachricht für den aktuellen Assistant-Block mit normalen Matrix-Textnachrichten. Dadurch bleibt das ältere Benachrichtigungsverhalten von Matrix mit Vorschau zuerst erhalten, sodass Standard-Clients möglicherweise bei der ersten gestreamten Vorschau statt beim fertigen Block benachrichtigen.
- `streaming: "quiet"` erstellt eine bearbeitbare stille Vorschau-Mitteilung für den aktuellen Assistant-Block. Verwenden Sie dies nur, wenn Sie zusätzlich Push-Regeln für Empfänger für finalisierte Vorschau-Bearbeitungen konfigurieren.
- `blockStreaming: true` aktiviert separate Matrix-Fortschrittsnachrichten. Wenn Vorschau-Streaming aktiviert ist, behält Matrix den Live-Entwurf für den aktuellen Block bei und bewahrt abgeschlossene Blöcke als separate Nachrichten.
- Wenn Vorschau-Streaming aktiviert und `blockStreaming` deaktiviert ist, bearbeitet Matrix den Live-Entwurf an Ort und Stelle und finalisiert dasselbe Ereignis, wenn der Block oder Turn endet.
- Wenn die Vorschau nicht mehr in ein einzelnes Matrix-Ereignis passt, beendet OpenClaw das Vorschau-Streaming und fällt auf normale endgültige Zustellung zurück.
- Medienantworten senden Anhänge weiterhin normal. Wenn eine veraltete Vorschau nicht mehr sicher wiederverwendet werden kann, redigiert OpenClaw sie, bevor die endgültige Medienantwort gesendet wird.
- Vorschau-Bearbeitungen verursachen zusätzliche Matrix-API-Aufrufe. Lassen Sie Streaming deaktiviert, wenn Sie das konservativste Rate-Limit-Verhalten möchten.

`blockStreaming` aktiviert keine Entwurfsvorschauen von selbst.
Verwenden Sie `streaming: "partial"` oder `streaming: "quiet"` für Vorschau-Bearbeitungen; fügen Sie dann `blockStreaming: true` nur hinzu, wenn abgeschlossene Assistant-Blöcke auch als separate Fortschrittsnachrichten sichtbar bleiben sollen.

Wenn Sie Matrix-Standardbenachrichtigungen ohne benutzerdefinierte Push-Regeln benötigen, verwenden Sie `streaming: "partial"` für Vorschau-zuerst-Verhalten oder lassen Sie `streaming` für reine Endzustellung deaktiviert. Mit `streaming: "off"`:

- `blockStreaming: true` sendet jeden abgeschlossenen Block als normale benachrichtigende Matrix-Nachricht.
- `blockStreaming: false` sendet nur die endgültige abgeschlossene Antwort als normale benachrichtigende Matrix-Nachricht.

### Selbst gehostete Push-Regeln für stille finalisierte Vorschauen

Wenn Sie Ihre eigene Matrix-Infrastruktur betreiben und möchten, dass stille Vorschauen nur benachrichtigen, wenn ein Block oder die
endgültige Antwort fertig ist, setzen Sie `streaming: "quiet"` und fügen Sie pro Benutzer eine Push-Regel für finalisierte Vorschau-Bearbeitungen hinzu.

Dies ist in der Regel eine Empfänger-Benutzerkonfiguration, keine homeserverweite Konfigurationsänderung:

Kurzübersicht, bevor Sie beginnen:

- Empfängerbenutzer = die Person, die die Benachrichtigung erhalten soll
- Bot-Benutzer = das OpenClaw-Matrix-Konto, das die Antwort sendet
- verwenden Sie für die folgenden API-Aufrufe das Access-Token des Empfängerbenutzers
- gleichen Sie `sender` in der Push-Regel mit der vollständigen MXID des Bot-Benutzers ab

1. Konfigurieren Sie OpenClaw für stille Vorschauen:

```json5
{
  channels: {
    matrix: {
      streaming: "quiet",
    },
  },
}
```

2. Stellen Sie sicher, dass das Empfängerkonto bereits normale Matrix-Push-Benachrichtigungen erhält. Regeln für stille Vorschauen
   funktionieren nur, wenn dieser Benutzer bereits funktionierende Pushers/Geräte hat.

3. Rufen Sie das Access-Token des Empfängerbenutzers ab.
   - Verwenden Sie das Token des empfangenden Benutzers, nicht das Token des Bots.
   - Die Wiederverwendung eines vorhandenen Client-Sitzungstokens ist normalerweise am einfachsten.
   - Wenn Sie ein neues Token erzeugen müssen, können Sie sich über die Standard-Matrix-Client-Server-API anmelden:

```bash
curl -sS -X POST \
  "https://matrix.example.org/_matrix/client/v3/login" \
  -H "Content-Type: application/json" \
  --data '{
    "type": "m.login.password",
    "identifier": {
      "type": "m.id.user",
      "user": "@alice:example.org"
    },
    "password": "REDACTED"
  }'
```

4. Prüfen Sie, ob das Empfängerkonto bereits Pushers hat:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushers"
```

Wenn dies keine aktiven Pushers/Geräte zurückgibt, beheben Sie zuerst normale Matrix-Benachrichtigungen, bevor Sie die
folgende OpenClaw-Regel hinzufügen.

OpenClaw kennzeichnet finalisierte reine Text-Vorschau-Bearbeitungen mit:

```json
{
  "com.openclaw.finalized_preview": true
}
```

5. Erstellen Sie für jedes Empfängerkonto, das diese Benachrichtigungen erhalten soll, eine Override-Push-Regel:

```bash
curl -sS -X PUT \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname" \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  --data '{
    "conditions": [
      { "kind": "event_match", "key": "type", "pattern": "m.room.message" },
      {
        "kind": "event_property_is",
        "key": "content.m\\.relates_to.rel_type",
        "value": "m.replace"
      },
      {
        "kind": "event_property_is",
        "key": "content.com\\.openclaw\\.finalized_preview",
        "value": true
      },
      { "kind": "event_match", "key": "sender", "pattern": "@bot:example.org" }
    ],
    "actions": [
      "notify",
      { "set_tweak": "sound", "value": "default" },
      { "set_tweak": "highlight", "value": false }
    ]
  }'
```

Ersetzen Sie diese Werte, bevor Sie den Befehl ausführen:

- `https://matrix.example.org`: die Basis-URL Ihres Homeservers
- `$USER_ACCESS_TOKEN`: das Access-Token des empfangenden Benutzers
- `openclaw-finalized-preview-botname`: eine Regel-ID, die für diesen Bot bei diesem empfangenden Benutzer eindeutig ist
- `@bot:example.org`: Ihre OpenClaw-Matrix-Bot-MXID, nicht die MXID des empfangenden Benutzers

Wichtig für Multi-Bot-Setups:

- Push-Regeln werden über `ruleId` identifiziert. Ein erneutes `PUT` auf dieselbe Regel-ID aktualisiert genau diese Regel.
- Wenn ein empfangender Benutzer für mehrere OpenClaw-Matrix-Bot-Konten Benachrichtigungen erhalten soll, erstellen Sie pro Bot eine Regel mit jeweils eindeutiger Regel-ID für jede Sender-Übereinstimmung.
- Ein einfaches Muster ist `openclaw-finalized-preview-<botname>`, zum Beispiel `openclaw-finalized-preview-ops` oder `openclaw-finalized-preview-support`.

Die Regel wird gegen den Ereignis-`sender` ausgewertet:

- authentifizieren Sie sich mit dem Token des empfangenden Benutzers
- gleichen Sie `sender` mit der MXID des OpenClaw-Bots ab

6. Prüfen Sie, ob die Regel vorhanden ist:

```bash
curl -sS \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

7. Testen Sie eine gestreamte Antwort. Im stillen Modus sollte der Raum eine stille Entwurfsvorschau anzeigen und die endgültige
   Bearbeitung an Ort und Stelle sollte benachrichtigen, sobald der Block oder Turn endet.

Wenn Sie die Regel später entfernen müssen, löschen Sie dieselbe Regel-ID mit dem Token des empfangenden Benutzers:

```bash
curl -sS -X DELETE \
  -H "Authorization: Bearer $USER_ACCESS_TOKEN" \
  "https://matrix.example.org/_matrix/client/v3/pushrules/global/override/openclaw-finalized-preview-botname"
```

Hinweise:

- Erstellen Sie die Regel mit dem Access-Token des empfangenden Benutzers, nicht mit dem des Bots.
- Neue benutzerdefinierte `override`-Regeln werden vor den Standard-Unterdrückungsregeln eingefügt, daher ist kein zusätzlicher Reihenfolgeparameter erforderlich.
- Dies betrifft nur reine Text-Vorschau-Bearbeitungen, die OpenClaw sicher an Ort und Stelle finalisieren kann. Medien-Fallbacks und veraltete Vorschau-Fallbacks verwenden weiterhin die normale Matrix-Zustellung.
- Wenn `GET /_matrix/client/v3/pushers` keine Pushers zeigt, verfügt der Benutzer für dieses Konto/Gerät noch nicht über funktionierende Matrix-Push-Zustellung.

#### Synapse

Für Synapse genügt die obige Einrichtung in der Regel bereits:

- Es ist keine spezielle Änderung an `homeserver.yaml` für finalisierte OpenClaw-Vorschau-Benachrichtigungen erforderlich.
- Wenn Ihre Synapse-Bereitstellung bereits normale Matrix-Push-Benachrichtigungen sendet, sind das Benutzertoken und der oben gezeigte `pushrules`-Aufruf der wichtigste Einrichtungsschritt.
- Wenn Sie Synapse hinter einem Reverse-Proxy oder mit Workern betreiben, stellen Sie sicher, dass `/_matrix/client/.../pushrules/` Synapse korrekt erreicht.
- Wenn Sie Synapse-Worker verwenden, stellen Sie sicher, dass die Pushers ordnungsgemäß funktionieren. Die Push-Zustellung wird vom Hauptprozess oder von `synapse.app.pusher` / konfigurierten Pusher-Workern übernommen.

#### Tuwunel

Verwenden Sie für Tuwunel denselben Einrichtungsablauf und denselben oben gezeigten `pushrules`-API-Aufruf:

- Für den finalisierten Vorschau-Marker selbst ist keine Tuwunel-spezifische Konfiguration erforderlich.
- Wenn normale Matrix-Benachrichtigungen für diesen Benutzer bereits funktionieren, sind das Benutzertoken und der oben gezeigte `pushrules`-Aufruf der wichtigste Einrichtungsschritt.
- Wenn Benachrichtigungen zu verschwinden scheinen, während der Benutzer auf einem anderen Gerät aktiv ist, prüfen Sie, ob `suppress_push_when_active` aktiviert ist. Tuwunel hat diese Option in Tuwunel 1.4.2 am 12. September 2025 hinzugefügt, und sie kann Pushes an andere Geräte absichtlich unterdrücken, während ein Gerät aktiv ist.

## Verschlüsselung und Verifizierung

In verschlüsselten (E2EE) Räumen verwenden ausgehende Bildereignisse `thumbnail_file`, sodass Bildvorschauen zusammen mit dem vollständigen Anhang verschlüsselt werden. Unverschlüsselte Räume verwenden weiterhin einfaches `thumbnail_url`. Keine Konfiguration erforderlich — das Plugin erkennt den E2EE-Status automatisch.

### Bot-zu-Bot-Räume

Standardmäßig werden Matrix-Nachrichten von anderen konfigurierten OpenClaw-Matrix-Konten ignoriert.

Verwenden Sie `allowBots`, wenn Sie absichtlich Matrix-Verkehr zwischen Agenten zulassen möchten:

```json5
{
  channels: {
    matrix: {
      allowBots: "mentions", // true | "mentions"
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

- `allowBots: true` akzeptiert Nachrichten von anderen konfigurierten Matrix-Bot-Konten in erlaubten Räumen und DMs.
- `allowBots: "mentions"` akzeptiert diese Nachrichten in Räumen nur dann, wenn sie diesen Bot sichtbar erwähnen. DMs bleiben weiterhin erlaubt.
- `groups.<room>.allowBots` überschreibt die Einstellung auf Kontoebene für einen Raum.
- OpenClaw ignoriert weiterhin Nachrichten derselben Matrix-Benutzer-ID, um Selbstantwort-Schleifen zu vermeiden.
- Matrix stellt hier kein natives Bot-Flag bereit; OpenClaw behandelt „von Bot verfasst“ als „von einem anderen konfigurierten Matrix-Konto auf diesem OpenClaw-Gateway gesendet“.

Verwenden Sie strikte Raum-Allowlists und Erwähnungsanforderungen, wenn Sie Bot-zu-Bot-Verkehr in gemeinsam genutzten Räumen aktivieren.

Verschlüsselung aktivieren:

```json5
{
  channels: {
    matrix: {
      enabled: true,
      homeserver: "https://matrix.example.org",
      accessToken: "syt_xxx",
      encryption: true,
      dm: { policy: "pairing" },
    },
  },
}
```

Verifizierungsstatus prüfen:

```bash
openclaw matrix verify status
```

Ausführlicher Status (vollständige Diagnose):

```bash
openclaw matrix verify status --verbose
```

Gespeicherten Recovery-Schlüssel in maschinenlesbarer Ausgabe einbeziehen:

```bash
openclaw matrix verify status --include-recovery-key --json
```

Cross-Signing- und Verifizierungsstatus initialisieren:

```bash
openclaw matrix verify bootstrap
```

Multi-Account-Unterstützung: Verwenden Sie `channels.matrix.accounts` mit kontospezifischen Anmeldedaten und optionalem `name`. Siehe [Konfigurationsreferenz](/de/gateway/configuration-reference#multi-account-all-channels) für das gemeinsame Muster.

Ausführliche Bootstrap-Diagnose:

```bash
openclaw matrix verify bootstrap --verbose
```

Frisches Zurücksetzen der Cross-Signing-Identität vor dem Bootstrap erzwingen:

```bash
openclaw matrix verify bootstrap --force-reset-cross-signing
```

Dieses Gerät mit einem Recovery-Schlüssel verifizieren:

```bash
openclaw matrix verify device "<your-recovery-key>"
```

Ausführliche Details zur Geräteverifizierung:

```bash
openclaw matrix verify device "<your-recovery-key>" --verbose
```

Integrität des Raumschlüssel-Backups prüfen:

```bash
openclaw matrix verify backup status
```

Ausführliche Diagnose zur Backup-Integrität:

```bash
openclaw matrix verify backup status --verbose
```

Raumschlüssel aus dem Server-Backup wiederherstellen:

```bash
openclaw matrix verify backup restore
```

Ausführliche Diagnose zur Wiederherstellung:

```bash
openclaw matrix verify backup restore --verbose
```

Das aktuelle Server-Backup löschen und eine frische Backup-Basis erstellen. Wenn der gespeicherte
Backup-Schlüssel nicht sauber geladen werden kann, kann dieses Zurücksetzen auch den Secret Storage neu erstellen, sodass
zukünftige Kaltstarts den neuen Backup-Schlüssel laden können:

```bash
openclaw matrix verify backup reset --yes
```

Alle `verify`-Befehle sind standardmäßig kompakt (einschließlich stiller interner SDK-Protokollierung) und zeigen detaillierte Diagnosen nur mit `--verbose`.
Verwenden Sie `--json` für vollständige maschinenlesbare Ausgabe bei Skripting.

In Multi-Account-Setups verwenden Matrix-CLI-Befehle das implizite Matrix-Standardkonto, sofern Sie nicht `--account <id>` übergeben.
Wenn Sie mehrere benannte Konten konfigurieren, setzen Sie zuerst `channels.matrix.defaultAccount`, andernfalls werden diese impliziten CLI-Operationen angehalten und Sie werden aufgefordert, explizit ein Konto auszuwählen.
Verwenden Sie `--account`, wenn Verifizierungs- oder Geräteoperationen explizit ein benanntes Konto ansprechen sollen:

```bash
openclaw matrix verify status --account assistant
openclaw matrix verify backup restore --account assistant
openclaw matrix devices list --account assistant
```

Wenn die Verschlüsselung für ein benanntes Konto deaktiviert oder nicht verfügbar ist, verweisen Matrix-Warnungen und Verifizierungsfehler auf den Konfigurationsschlüssel dieses Kontos, zum Beispiel `channels.matrix.accounts.assistant.encryption`.

### Was „verifiziert“ bedeutet

OpenClaw behandelt dieses Matrix-Gerät nur dann als verifiziert, wenn es von Ihrer eigenen Cross-Signing-Identität verifiziert wurde.
In der Praxis zeigt `openclaw matrix verify status --verbose` drei Vertrauenssignale an:

- `Locally trusted`: Dieses Gerät wird nur vom aktuellen Client als vertrauenswürdig eingestuft
- `Cross-signing verified`: Das SDK meldet das Gerät als per Cross-Signing verifiziert
- `Signed by owner`: Das Gerät ist mit Ihrem eigenen Self-Signing-Schlüssel signiert

`Verified by owner` wird nur dann `yes`, wenn Cross-Signing-Verifizierung oder Owner-Signing vorhanden ist.
Lokales Vertrauen allein reicht nicht aus, damit OpenClaw das Gerät als vollständig verifiziert behandelt.

### Was Bootstrap tut

`openclaw matrix verify bootstrap` ist der Reparatur- und Einrichtungsbefehl für verschlüsselte Matrix-Konten.
Er führt in dieser Reihenfolge Folgendes aus:

- initialisiert Secret Storage und verwendet nach Möglichkeit einen vorhandenen Recovery-Schlüssel wieder
- initialisiert Cross-Signing und lädt fehlende öffentliche Cross-Signing-Schlüssel hoch
- versucht, das aktuelle Gerät zu markieren und per Cross-Signing zu signieren
- erstellt ein neues serverseitiges Raumschlüssel-Backup, falls noch keines vorhanden ist

Wenn der Homeserver interaktive Authentifizierung für das Hochladen von Cross-Signing-Schlüsseln verlangt, versucht OpenClaw das Hochladen zuerst ohne Authentifizierung, dann mit `m.login.dummy` und anschließend mit `m.login.password`, wenn `channels.matrix.password` konfiguriert ist.

Verwenden Sie `--force-reset-cross-signing` nur, wenn Sie die aktuelle Cross-Signing-Identität absichtlich verwerfen und eine neue erstellen möchten.

Wenn Sie das aktuelle Raumschlüssel-Backup absichtlich verwerfen und für zukünftige Nachrichten
eine neue Backup-Basis beginnen möchten, verwenden Sie `openclaw matrix verify backup reset --yes`.
Tun Sie dies nur, wenn Sie akzeptieren, dass nicht wiederherstellbarer alter verschlüsselter Verlauf
weiterhin nicht verfügbar bleibt und OpenClaw Secret Storage möglicherweise neu erstellt, wenn das aktuelle Backup-
Geheimnis nicht sicher geladen werden kann.

### Frische Backup-Basis

Wenn Sie zukünftige verschlüsselte Nachrichten funktionsfähig halten und den Verlust nicht wiederherstellbarer alter Chronik akzeptieren möchten, führen Sie diese Befehle in dieser Reihenfolge aus:

```bash
openclaw matrix verify backup reset --yes
openclaw matrix verify backup status --verbose
openclaw matrix verify status
```

Fügen Sie zu jedem Befehl `--account <id>` hinzu, wenn Sie explizit ein benanntes Matrix-Konto ansprechen möchten.

### Startverhalten

Wenn `encryption: true` gesetzt ist, verwendet Matrix standardmäßig `startupVerification` mit dem Wert `"if-unverified"`.
Beim Start fordert Matrix eine Selbstverifizierung in einem anderen Matrix-Client an, falls dieses Gerät noch nicht verifiziert ist,
überspringt doppelte Anforderungen, solange bereits eine aussteht, und wendet vor erneuten Versuchen nach Neustarts eine lokale Abkühlphase an.
Fehlgeschlagene Anforderungsversuche werden standardmäßig früher erneut versucht als erfolgreich erzeugte Anforderungen.
Setzen Sie `startupVerification: "off"`, um automatische Startanforderungen zu deaktivieren, oder passen Sie `startupVerificationCooldownHours`
an, wenn Sie ein kürzeres oder längeres Wiederholungsfenster möchten.

Beim Start wird außerdem automatisch ein konservativer Krypto-Bootstrap-Durchlauf ausgeführt.
Dieser Durchlauf versucht zuerst, den aktuellen Secret Storage und die aktuelle Cross-Signing-Identität wiederzuverwenden, und vermeidet das Zurücksetzen von Cross-Signing, sofern Sie nicht einen expliziten Bootstrap-Reparaturablauf ausführen.

Wenn beim Start ein defekter Bootstrap-Status erkannt wird und `channels.matrix.password` konfiguriert ist, kann OpenClaw einen strengeren Reparaturpfad versuchen.
Wenn das aktuelle Gerät bereits vom Eigentümer signiert ist, bewahrt OpenClaw diese Identität, statt sie automatisch zurückzusetzen.

Upgrade vom vorherigen öffentlichen Matrix-Plugin:

- OpenClaw verwendet nach Möglichkeit automatisch dasselbe Matrix-Konto, denselben Access-Token und dieselbe Geräteidentität wieder.
- Bevor umsetzbare Matrix-Migrationsänderungen ausgeführt werden, erstellt oder verwendet OpenClaw einen Recovery-Snapshot unter `~/Backups/openclaw-migrations/`.
- Wenn Sie mehrere Matrix-Konten verwenden, setzen Sie vor dem Upgrade vom alten Flat-Store-Layout `channels.matrix.defaultAccount`, damit OpenClaw weiß, welches Konto diesen gemeinsamen Legacy-Status erhalten soll.
- Wenn das vorherige Plugin lokal einen Entschlüsselungsschlüssel für ein Matrix-Raumschlüssel-Backup gespeichert hat, importieren der Start oder `openclaw doctor --fix` ihn automatisch in den neuen Recovery-Schlüssel-Ablauf.
- Wenn sich der Matrix-Access-Token geändert hat, nachdem die Migration vorbereitet wurde, durchsucht der Start jetzt benachbarte Token-Hash-Speicherwurzeln nach ausstehendem Legacy-Wiederherstellungsstatus, bevor die automatische Backup-Wiederherstellung aufgegeben wird.
- Wenn sich der Matrix-Access-Token später für dasselbe Konto, denselben Homeserver und denselben Benutzer ändert, verwendet OpenClaw nun bevorzugt die vollständigste vorhandene Token-Hash-Speicherwurzel wieder, statt mit einem leeren Matrix-Statusverzeichnis zu beginnen.
- Beim nächsten Gateway-Start werden gesicherte Raumschlüssel automatisch in den neuen Krypto-Store wiederhergestellt.
- Wenn das alte Plugin nur lokal vorhandene Raumschlüssel hatte, die nie gesichert wurden, warnt OpenClaw deutlich. Diese Schlüssel können nicht automatisch aus dem vorherigen Rust-Krypto-Store exportiert werden, sodass ein Teil des alten verschlüsselten Verlaufs bis zur manuellen Wiederherstellung möglicherweise nicht verfügbar bleibt.
- Siehe [Matrix-Migration](/de/install/migrating-matrix) für den vollständigen Upgrade-Ablauf, Einschränkungen, Wiederherstellungsbefehle und häufige Migrationsmeldungen.

Der verschlüsselte Laufzeitstatus ist unter token-hash-basierten Wurzeln pro Konto und Benutzer in
`~/.openclaw/matrix/accounts/<account>/<homeserver>__<user>/<token-hash>/` organisiert.
Dieses Verzeichnis enthält den Sync-Store (`bot-storage.json`), den Krypto-Store (`crypto/`),
die Recovery-Schlüsseldatei (`recovery-key.json`), den IndexedDB-Snapshot (`crypto-idb-snapshot.json`),
Thread-Bindings (`thread-bindings.json`) und den Status der Startverifizierung (`startup-verification.json`),
wenn diese Funktionen verwendet werden.
Wenn sich das Token ändert, die Kontoidentität aber gleich bleibt, verwendet OpenClaw die beste vorhandene
Wurzel für dieses Konto-/Homeserver-/Benutzer-Tupel wieder, sodass vorheriger Sync-Status, Krypto-Status, Thread-Bindings
und Startverifizierungsstatus sichtbar bleiben.

### Node-Krypto-Store-Modell

Matrix-E2EE in diesem Plugin verwendet in Node den offiziellen Rust-Krypto-Pfad von `matrix-js-sdk`.
Dieser Pfad erwartet IndexedDB-basierte Persistenz, wenn der Krypto-Status Neustarts überdauern soll.

OpenClaw stellt dies in Node derzeit bereit, indem es:

- `fake-indexeddb` als vom SDK erwarteten IndexedDB-API-Shim verwendet
- die Rust-Krypto-IndexedDB-Inhalte vor `initRustCrypto` aus `crypto-idb-snapshot.json` wiederherstellt
- die aktualisierten IndexedDB-Inhalte nach der Initialisierung und während der Laufzeit zurück in `crypto-idb-snapshot.json` persistiert
- Snapshot-Wiederherstellung und Persistenz gegenüber `crypto-idb-snapshot.json` mit einer beratenden Dateisperre serialisiert, damit Gateway-Laufzeitpersistenz und CLI-Wartung nicht um dieselbe Snapshot-Datei konkurrieren

Dies ist Kompatibilitäts-/Speicher-Plumbing, keine benutzerdefinierte Krypto-Implementierung.
Die Snapshot-Datei ist sensibler Laufzeitstatus und wird mit restriktiven Dateiberechtigungen gespeichert.
Nach dem Sicherheitsmodell von OpenClaw befinden sich der Gateway-Host und das lokale OpenClaw-Statusverzeichnis bereits innerhalb der vertrauenswürdigen Operator-Grenze, daher ist dies primär ein Problem der Betriebssicherheit und keine separate Remote-Vertrauensgrenze.

Geplante Verbesserung:

- SecretRef-Unterstützung für persistentes Matrix-Schlüsselmaterial hinzufügen, damit Recovery-Schlüssel und verwandte Store-Verschlüsselungsgeheimnisse aus OpenClaw-Secret-Providern statt nur aus lokalen Dateien bezogen werden können

## Profilverwaltung

Aktualisieren Sie das Matrix-Selbstprofil für das ausgewählte Konto mit:

```bash
openclaw matrix profile set --name "OpenClaw Assistant"
openclaw matrix profile set --avatar-url https://cdn.example.org/avatar.png
```

Fügen Sie `--account <id>` hinzu, wenn Sie explizit ein benanntes Matrix-Konto ansprechen möchten.

Matrix akzeptiert `mxc://`-Avatar-URLs direkt. Wenn Sie eine `http://`- oder `https://`-Avatar-URL übergeben, lädt OpenClaw sie zuerst zu Matrix hoch und speichert die aufgelöste `mxc://`-URL zurück in `channels.matrix.avatarUrl` (oder in die ausgewählte Kontoüberschreibung).

## Automatische Verifizierungsmitteilungen

Matrix veröffentlicht jetzt Hinweise zum Verifizierungslebenszyklus direkt im strikten DM-Verifizierungsraum als `m.notice`-Nachrichten.
Dazu gehören:

- Hinweise zu Verifizierungsanfragen
- Hinweise, dass die Verifizierung bereit ist (mit explizitem Hinweis „Per Emoji verifizieren“)
- Hinweise zum Start und Abschluss der Verifizierung
- SAS-Details (Emoji und Dezimalwerte), wenn verfügbar

Eingehende Verifizierungsanfragen von einem anderen Matrix-Client werden von OpenClaw nachverfolgt und automatisch akzeptiert.
Bei Selbstverifizierungsabläufen startet OpenClaw außerdem den SAS-Ablauf automatisch, sobald die Emoji-Verifizierung verfügbar ist, und bestätigt seine eigene Seite.
Bei Verifizierungsanfragen von einem anderen Matrix-Benutzer/-Gerät akzeptiert OpenClaw die Anfrage automatisch und wartet dann darauf, dass der SAS-Ablauf normal fortgesetzt wird.
Sie müssen die Emoji- oder Dezimal-SAS weiterhin in Ihrem Matrix-Client vergleichen und dort „Sie stimmen überein“ bestätigen, um die Verifizierung abzuschließen.

OpenClaw akzeptiert selbst initiierte doppelte Abläufe nicht blind automatisch. Beim Start wird keine neue Anfrage erstellt, wenn bereits eine Selbstverifizierungsanfrage aussteht.

Hinweise des Verifizierungsprotokolls/-systems werden nicht an die Agent-Chat-Pipeline weitergeleitet, daher erzeugen sie kein `NO_REPLY`.

### Gerätehygiene

Alte von OpenClaw verwaltete Matrix-Geräte können sich auf dem Konto ansammeln und das Vertrauen in verschlüsselten Räumen schwerer nachvollziehbar machen.
Listen Sie sie auf mit:

```bash
openclaw matrix devices list
```

Entfernen Sie veraltete von OpenClaw verwaltete Geräte mit:

```bash
openclaw matrix devices prune-stale
```

### Reparatur direkter Räume

Wenn der Status direkter Nachrichten nicht synchron ist, kann OpenClaw veraltete `m.direct`-Zuordnungen erhalten, die auf alte Soloräume statt auf den aktuellen DM zeigen. Prüfen Sie die aktuelle Zuordnung für einen Peer mit:

```bash
openclaw matrix direct inspect --user-id @alice:example.org
```

Reparieren Sie sie mit:

```bash
openclaw matrix direct repair --user-id @alice:example.org
```

Die Reparatur hält die Matrix-spezifische Logik im Plugin:

- bevorzugt wird ein strikter 1:1-DM, der bereits in `m.direct` zugeordnet ist
- andernfalls wird auf einen beliebigen aktuell beigetretenen strikten 1:1-DM mit diesem Benutzer zurückgegriffen
- wenn kein intakter DM existiert, wird ein neuer direkter Raum erstellt und `m.direct` so neu geschrieben, dass er darauf zeigt

Der Reparaturablauf löscht alte Räume nicht automatisch. Er wählt nur den intakten DM aus und aktualisiert die Zuordnung, sodass neue Matrix-Sendungen, Verifizierungshinweise und andere Direktnachrichtenabläufe wieder den richtigen Raum ansprechen.

## Threads

Matrix unterstützt native Matrix-Threads sowohl für automatische Antworten als auch für Message-Tool-Sendungen.

- `dm.sessionScope: "per-user"` (Standard) hält das Matrix-DM-Routing absenderspezifisch, sodass mehrere DM-Räume eine Sitzung gemeinsam nutzen können, wenn sie demselben Peer zugeordnet werden.
- `dm.sessionScope: "per-room"` isoliert jeden Matrix-DM-Raum in seinen eigenen Sitzungsschlüssel und verwendet dabei weiterhin normale DM-Authentifizierungs- und Allowlist-Prüfungen.
- Explizite Matrix-Konversations-Bindings haben weiterhin Vorrang vor `dm.sessionScope`, sodass gebundene Räume und Threads ihren gewählten Ziel-Session beibehalten.
- `threadReplies: "off"` hält Antworten auf der obersten Ebene und eingehende Thread-Nachrichten auf der übergeordneten Sitzung.
- `threadReplies: "inbound"` antwortet innerhalb eines Threads nur dann, wenn die eingehende Nachricht bereits in diesem Thread war.
- `threadReplies: "always"` hält Raumantworten in einem Thread mit der auslösenden Nachricht als Wurzel und leitet diese Konversation ab der ersten auslösenden Nachricht durch die passende threadbezogene Sitzung.
- `dm.threadReplies` überschreibt die Einstellung auf oberster Ebene nur für DMs. Sie können zum Beispiel Raum-Threads isoliert halten und DMs flach halten.
- Eingehende Thread-Nachrichten enthalten die Thread-Wurzelnachricht als zusätzlichen Agent-Kontext.
- Message-Tool-Sendungen übernehmen jetzt automatisch den aktuellen Matrix-Thread, wenn das Ziel derselbe Raum oder dasselbe DM-Benutzerziel ist, sofern nicht explizit `threadId` angegeben wird.
- Dieselbe sitzungsbezogene Wiederverwendung für DM-Benutzerziele greift nur, wenn die aktuellen Sitzungsmetadaten denselben DM-Peer im selben Matrix-Konto nachweisen; andernfalls fällt OpenClaw auf normales benutzerbezogenes Routing zurück.
- Wenn OpenClaw erkennt, dass ein Matrix-DM-Raum mit einem anderen DM-Raum in derselben gemeinsam genutzten Matrix-DM-Sitzung kollidiert, sendet es einmalig ein `m.notice` in diesem Raum mit dem `/focus`-Ausweg, wenn Thread-Bindings aktiviert sind, sowie dem Hinweis `dm.sessionScope`.
- Laufzeit-Thread-Bindings werden für Matrix unterstützt. `/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age` und threadgebundenes `/acp spawn` funktionieren jetzt in Matrix-Räumen und DMs.
- Ein `/focus` auf oberster Ebene in Matrix-Raum/DM erstellt einen neuen Matrix-Thread und bindet ihn an die Zielsitzung, wenn `threadBindings.spawnSubagentSessions=true`.
- Wenn `/focus` oder `/acp spawn --thread here` innerhalb eines bestehenden Matrix-Threads ausgeführt wird, wird stattdessen dieser aktuelle Thread gebunden.

## ACP-Konversations-Bindings

Matrix-Räume, DMs und bestehende Matrix-Threads können in dauerhafte ACP-Workspaces umgewandelt werden, ohne die Chat-Oberfläche zu ändern.

Schneller Operator-Ablauf:

- Führen Sie `/acp spawn codex --bind here` innerhalb des Matrix-DM, Raums oder bestehenden Threads aus, den Sie weiterverwenden möchten.
- In einem Matrix-DM oder Raum auf oberster Ebene bleibt der aktuelle DM/Raum die Chat-Oberfläche und zukünftige Nachrichten werden an die erzeugte ACP-Sitzung weitergeleitet.
- Innerhalb eines bestehenden Matrix-Threads bindet `--bind here` diesen aktuellen Thread direkt.
- `/new` und `/reset` setzen dieselbe gebundene ACP-Sitzung direkt zurück.
- `/acp close` schließt die ACP-Sitzung und entfernt die Bindung.

Hinweise:

- `--bind here` erstellt keinen untergeordneten Matrix-Thread.
- `threadBindings.spawnAcpSessions` ist nur für `/acp spawn --thread auto|here` erforderlich, wenn OpenClaw einen untergeordneten Matrix-Thread erstellen oder binden muss.

### Thread-Binding-Konfiguration

Matrix übernimmt globale Standards von `session.threadBindings` und unterstützt außerdem kanalbezogene Überschreibungen:

- `threadBindings.enabled`
- `threadBindings.idleHours`
- `threadBindings.maxAgeHours`
- `threadBindings.spawnSubagentSessions`
- `threadBindings.spawnAcpSessions`

Threadgebundene Spawn-Flags für Matrix sind optional:

- Setzen Sie `threadBindings.spawnSubagentSessions: true`, um `/focus` auf oberster Ebene zu erlauben, neue Matrix-Threads zu erstellen und zu binden.
- Setzen Sie `threadBindings.spawnAcpSessions: true`, um `/acp spawn --thread auto|here` zu erlauben, ACP-Sitzungen an Matrix-Threads zu binden.

## Reaktionen

Matrix unterstützt ausgehende Reaktionsaktionen, eingehende Reaktionsbenachrichtigungen und eingehende Bestätigungsreaktionen.

- Outbound-Reaktions-Tooling wird durch `channels["matrix"].actions.reactions` gesteuert.
- `react` fügt einem bestimmten Matrix-Ereignis eine Reaktion hinzu.
- `reactions` listet die aktuelle Reaktionszusammenfassung für ein bestimmtes Matrix-Ereignis auf.
- `emoji=""` entfernt die eigenen Reaktionen des Bot-Kontos auf dieses Ereignis.
- `remove: true` entfernt nur die angegebene Emoji-Reaktion vom Bot-Konto.

Der Geltungsbereich für Bestätigungsreaktionen wird in der Standardreihenfolge von OpenClaw aufgelöst:

- `channels["matrix"].accounts.<accountId>.ackReaction`
- `channels["matrix"].ackReaction`
- `messages.ackReaction`
- Emoji-Fallback der Agent-Identität

Der Geltungsbereich der Bestätigungsreaktion wird in dieser Reihenfolge aufgelöst:

- `channels["matrix"].accounts.<accountId>.ackReactionScope`
- `channels["matrix"].ackReactionScope`
- `messages.ackReactionScope`

Der Modus für Reaktionsbenachrichtigungen wird in dieser Reihenfolge aufgelöst:

- `channels["matrix"].accounts.<accountId>.reactionNotifications`
- `channels["matrix"].reactionNotifications`
- Standard: `own`

Aktuelles Verhalten:

- `reactionNotifications: "own"` leitet hinzugefügte `m.reaction`-Ereignisse weiter, wenn sie auf vom Bot verfasste Matrix-Nachrichten zielen.
- `reactionNotifications: "off"` deaktiviert Reaktionssystemereignisse.
- Das Entfernen von Reaktionen wird weiterhin nicht in Systemereignisse synthetisiert, da Matrix diese als Redigierungen und nicht als eigenständige `m.reaction`-Entfernungen darstellt.

## Verlaufs-Kontext

- `channels.matrix.historyLimit` steuert, wie viele aktuelle Raumnachrichten als `InboundHistory` einbezogen werden, wenn eine Matrix-Raumnachricht den Agent auslöst.
- Es greift auf `messages.groupChat.historyLimit` zurück. Wenn beides nicht gesetzt ist, ist der effektive Standardwert `0`, sodass durch Erwähnungen ausgelöste Raumnachrichten nicht gepuffert werden. Setzen Sie `0`, um zu deaktivieren.
- Matrix-Raumverlauf ist nur raumbezogen. DMs verwenden weiterhin den normalen Sitzungsverlauf.
- Matrix-Raumverlauf ist nur für ausstehende Nachrichten: OpenClaw puffert Raumnachrichten, die noch keine Antwort ausgelöst haben, und erstellt dann einen Snapshot dieses Fensters, wenn eine Erwähnung oder ein anderer Auslöser eintrifft.
- Die aktuelle Auslösernachricht wird nicht in `InboundHistory` aufgenommen; sie bleibt für diesen Turn im Hauptteil der eingehenden Nachricht.
- Wiederholungen desselben Matrix-Ereignisses verwenden den ursprünglichen Verlaufs-Snapshot wieder, statt mit neueren Raumnachrichten weiterzuwandern.

## Kontextsichtbarkeit

Matrix unterstützt die gemeinsame `contextVisibility`-Steuerung für ergänzenden Raumkontext wie abgerufenen Antworttext, Thread-Wurzeln und ausstehenden Verlauf.

- `contextVisibility: "all"` ist der Standard. Ergänzender Kontext bleibt wie empfangen erhalten.
- `contextVisibility: "allowlist"` filtert ergänzenden Kontext auf Absender, die durch die aktiven Allowlist-Prüfungen für Raum/Benutzer erlaubt sind.
- `contextVisibility: "allowlist_quote"` verhält sich wie `allowlist`, behält aber weiterhin eine explizit zitierte Antwort bei.

Diese Einstellung wirkt sich auf die Sichtbarkeit ergänzenden Kontexts aus, nicht darauf, ob die eingehende Nachricht selbst eine Antwort auslösen kann.
Die Berechtigung zum Auslösen wird weiterhin durch `groupPolicy`, `groups`, `groupAllowFrom` und DM-Richtlinieneinstellungen bestimmt.

## Beispiel für DM- und Raumrichtlinie

```json5
{
  channels: {
    matrix: {
      dm: {
        policy: "allowlist",
        allowFrom: ["@admin:example.org"],
        threadReplies: "off",
      },
      groupPolicy: "allowlist",
      groupAllowFrom: ["@admin:example.org"],
      groups: {
        "!roomid:example.org": {
          requireMention: true,
        },
      },
    },
  },
}
```

Siehe [Groups](/de/channels/groups) für Verhalten bei Erwähnungs-Gating und Allowlist.

Pairing-Beispiel für Matrix-DMs:

```bash
openclaw pairing list matrix
openclaw pairing approve matrix <CODE>
```

Wenn ein nicht genehmigter Matrix-Benutzer Ihnen vor der Genehmigung weiterhin Nachrichten sendet, verwendet OpenClaw denselben ausstehenden Pairing-Code erneut und sendet nach einer kurzen Abkühlzeit möglicherweise erneut eine Erinnerungsantwort, statt einen neuen Code zu erzeugen.

Siehe [Pairing](/de/channels/pairing) für den gemeinsamen DM-Pairing-Ablauf und das Speicherlayout.

## Exec-Genehmigungen

Matrix kann als Exec-Genehmigungs-Client für ein Matrix-Konto fungieren.

- `channels.matrix.execApprovals.enabled`
- `channels.matrix.execApprovals.approvers` (optional; greift auf `channels.matrix.dm.allowFrom` zurück)
- `channels.matrix.execApprovals.target` (`dm` | `channel` | `both`, Standard: `dm`)
- `channels.matrix.execApprovals.agentFilter`
- `channels.matrix.execApprovals.sessionFilter`

Genehmigende Benutzer müssen Matrix-Benutzer-IDs wie `@owner:example.org` sein. Matrix aktiviert native Exec-Genehmigungen automatisch, wenn `enabled` nicht gesetzt oder `"auto"` ist und mindestens ein Genehmigender aufgelöst werden kann, entweder aus `execApprovals.approvers` oder aus `channels.matrix.dm.allowFrom`. Setzen Sie `enabled: false`, um Matrix explizit als nativen Genehmigungs-Client zu deaktivieren. Genehmigungsanfragen greifen andernfalls auf andere konfigurierte Genehmigungsrouten oder die Fallback-Richtlinie für Exec-Genehmigungen zurück.

Natives Matrix-Routing gilt derzeit nur für Exec:

- `channels.matrix.execApprovals.*` steuert natives DM-/Kanal-Routing nur für Exec-Genehmigungen.
- Plugin-Genehmigungen verwenden weiterhin das gemeinsame `/approve` im selben Chat sowie jede konfigurierte Weiterleitung `approvals.plugin`.
- Matrix kann `channels.matrix.dm.allowFrom` weiterhin für die Autorisierung von Plugin-Genehmigungen wiederverwenden, wenn Genehmigende sicher abgeleitet werden können, bietet jedoch keinen separaten nativen DM-/Kanal-Fanout-Pfad für Plugin-Genehmigungen.

Zustellungsregeln:

- `target: "dm"` sendet Genehmigungsaufforderungen an DMs der genehmigenden Benutzer
- `target: "channel"` sendet die Aufforderung zurück an den auslösenden Matrix-Raum oder DM
- `target: "both"` sendet an DMs der genehmigenden Benutzer und an den auslösenden Matrix-Raum oder DM

Matrix-Genehmigungsaufforderungen setzen Reaktionskürzel auf der primären Genehmigungsnachricht:

- `✅` = einmal erlauben
- `❌` = ablehnen
- `♾️` = immer erlauben, wenn diese Entscheidung durch die effektive Exec-Richtlinie zulässig ist

Genehmigende Benutzer können auf diese Nachricht reagieren oder die Fallback-Slash-Befehle verwenden: `/approve <id> allow-once`, `/approve <id> allow-always` oder `/approve <id> deny`.

Nur aufgelöste Genehmigende können genehmigen oder ablehnen. Kanalzustellung enthält den Befehlstext, daher sollten Sie `channel` oder `both` nur in vertrauenswürdigen Räumen aktivieren.

Matrix-Genehmigungsaufforderungen verwenden den gemeinsamen Core-Genehmigungsplaner wieder. Die Matrix-spezifische native Oberfläche ist nur der Transport für Exec-Genehmigungen: Raum-/DM-Routing und Verhalten beim Senden/Aktualisieren/Löschen von Nachrichten.

Kontobezogene Überschreibung:

- `channels.matrix.accounts.<account>.execApprovals`

Verwandte Dokumentation: [Exec approvals](/de/tools/exec-approvals)

## Multi-Account-Beispiel

```json5
{
  channels: {
    matrix: {
      enabled: true,
      defaultAccount: "assistant",
      dm: { policy: "pairing" },
      accounts: {
        assistant: {
          homeserver: "https://matrix.example.org",
          accessToken: "syt_assistant_xxx",
          encryption: true,
        },
        alerts: {
          homeserver: "https://matrix.example.org",
          accessToken: "syt_alerts_xxx",
          dm: {
            policy: "allowlist",
            allowFrom: ["@ops:example.org"],
            threadReplies: "off",
          },
        },
      },
    },
  },
}
```

Werte auf oberster Ebene unter `channels.matrix` fungieren als Standardwerte für benannte Konten, sofern ein Konto sie nicht überschreibt.
Sie können geerbte Raumeinträge auf ein Matrix-Konto beschränken mit `groups.<room>.account` (oder dem Legacy-Wert `rooms.<room>.account`).
Einträge ohne `account` bleiben für alle Matrix-Konten gemeinsam, und Einträge mit `account: "default"` funktionieren weiterhin, wenn das Standardkonto direkt auf oberster Ebene unter `channels.matrix.*` konfiguriert ist.
Partielle gemeinsame Auth-Standardwerte erzeugen für sich genommen kein separates implizites Standardkonto. OpenClaw synthetisiert das Standardkonto auf oberster Ebene `default` nur dann, wenn dieses Standardkonto frische Authentifizierung hat (`homeserver` plus `accessToken` oder `homeserver` plus `userId` und `password`); benannte Konten können weiterhin anhand von `homeserver` plus `userId` erkennbar bleiben, wenn zwischengespeicherte Anmeldedaten später die Authentifizierung erfüllen.
Wenn Matrix bereits genau ein benanntes Konto hat oder `defaultAccount` auf einen vorhandenen benannten Kontoschlüssel zeigt, bewahrt die Reparatur-/Einrichtungs-Promotion von Single-Account zu Multi-Account dieses Konto, statt einen neuen `accounts.default`-Eintrag zu erstellen. Nur Auth-/Bootstrap-Schlüssel für Matrix werden in dieses hochgestufte Konto verschoben; gemeinsame Zustellungsrichtlinien-Schlüssel bleiben auf oberster Ebene.
Setzen Sie `defaultAccount`, wenn OpenClaw ein benanntes Matrix-Konto für implizites Routing, Probe und CLI-Operationen bevorzugen soll.
Wenn Sie mehrere benannte Konten konfigurieren, setzen Sie `defaultAccount` oder übergeben Sie `--account <id>` für CLI-Befehle, die auf impliziter Kontenauswahl basieren.
Übergeben Sie `--account <id>` an `openclaw matrix verify ...` und `openclaw matrix devices ...`, wenn Sie diese implizite Auswahl für einen Befehl überschreiben möchten.

## Private/LAN-Homeserver

Standardmäßig blockiert OpenClaw private/interne Matrix-Homeserver zum SSRF-Schutz, sofern Sie
dies nicht explizit pro Konto aktivieren.

Wenn Ihr Homeserver auf localhost, einer LAN-/Tailscale-IP oder einem internen Hostnamen läuft, aktivieren Sie
`allowPrivateNetwork` für dieses Matrix-Konto:

```json5
{
  channels: {
    matrix: {
      homeserver: "http://matrix-synapse:8008",
      allowPrivateNetwork: true,
      accessToken: "syt_internal_xxx",
    },
  },
}
```

CLI-Einrichtungsbeispiel:

```bash
openclaw matrix account add \
  --account ops \
  --homeserver http://matrix-synapse:8008 \
  --allow-private-network \
  --access-token syt_ops_xxx
```

Diese Aktivierung erlaubt nur vertrauenswürdige private/interne Ziele. Öffentliche unverschlüsselte Homeserver wie
`http://matrix.example.org:8008` bleiben blockiert. Bevorzugen Sie nach Möglichkeit `https://`.

## Matrix-Datenverkehr über Proxy leiten

Wenn Ihre Matrix-Bereitstellung einen expliziten ausgehenden HTTP(S)-Proxy benötigt, setzen Sie `channels.matrix.proxy`:

```json5
{
  channels: {
    matrix: {
      homeserver: "https://matrix.example.org",
      accessToken: "syt_bot_xxx",
      proxy: "http://127.0.0.1:7890",
    },
  },
}
```

Benannte Konten können den Standardwert auf oberster Ebene mit `channels.matrix.accounts.<id>.proxy` überschreiben.
OpenClaw verwendet dieselbe Proxy-Einstellung für Matrix-Laufzeitverkehr und Konto-Statusprobes.

## Zielauflösung

Matrix akzeptiert diese Zielformen überall dort, wo OpenClaw Sie nach einem Raum- oder Benutzerziel fragt:

- Benutzer: `@user:server`, `user:@user:server` oder `matrix:user:@user:server`
- Räume: `!room:server`, `room:!room:server` oder `matrix:room:!room:server`
- Aliasse: `#alias:server`, `channel:#alias:server` oder `matrix:channel:#alias:server`

Die Live-Verzeichnissuche verwendet das angemeldete Matrix-Konto:

- Benutzer-Lookups fragen das Matrix-Benutzerverzeichnis auf diesem Homeserver ab.
- Raum-Lookups akzeptieren explizite Raum-IDs und Aliasse direkt und greifen dann auf die Suche in Namen beigetretener Räume für dieses Konto zurück.
- Die Namenssuche in beigetretenen Räumen erfolgt nach bestem Bemühen. Wenn ein Raumname nicht in eine ID oder einen Alias aufgelöst werden kann, wird er von der Laufzeit-Allowlist-Auflösung ignoriert.

## Konfigurationsreferenz

- `enabled`: den Kanal aktivieren oder deaktivieren.
- `name`: optionale Bezeichnung für das Konto.
- `defaultAccount`: bevorzugte Konto-ID, wenn mehrere Matrix-Konten konfiguriert sind.
- `homeserver`: Homeserver-URL, zum Beispiel `https://matrix.example.org`.
- `allowPrivateNetwork`: diesem Matrix-Konto erlauben, sich mit privaten/internen Homeservern zu verbinden. Aktivieren Sie dies, wenn der Homeserver zu `localhost`, einer LAN-/Tailscale-IP oder einem internen Host wie `matrix-synapse` aufgelöst wird.
- `proxy`: optionale HTTP(S)-Proxy-URL für Matrix-Datenverkehr. Benannte Konten können den Standardwert auf oberster Ebene mit ihrem eigenen `proxy` überschreiben.
- `userId`: vollständige Matrix-Benutzer-ID, zum Beispiel `@bot:example.org`.
- `accessToken`: Access-Token für tokenbasierte Authentifizierung. Klartextwerte und SecretRef-Werte werden für `channels.matrix.accessToken` und `channels.matrix.accounts.<id>.accessToken` über Env-/File-/Exec-Provider unterstützt. Siehe [Secrets Management](/de/gateway/secrets).
- `password`: Passwort für passwortbasierte Anmeldung. Klartextwerte und SecretRef-Werte werden unterstützt.
- `deviceId`: explizite Matrix-Geräte-ID.
- `deviceName`: Geräteanzeigename für die Passwortanmeldung.
- `avatarUrl`: gespeicherte Self-Avatar-URL für Profilsynchronisierung und `set-profile`-Updates.
- `initialSyncLimit`: Ereignislimit für die Startsynchronisierung.
- `encryption`: E2EE aktivieren.
- `allowlistOnly`: Verhalten nur mit Allowlist für DMs und Räume erzwingen.
- `allowBots`: Nachrichten von anderen konfigurierten OpenClaw-Matrix-Konten erlauben (`true` oder `"mentions"`).
- `groupPolicy`: `open`, `allowlist` oder `disabled`.
- `contextVisibility`: Sichtbarkeitsmodus für ergänzenden Raumkontext (`all`, `allowlist`, `allowlist_quote`).
- `groupAllowFrom`: Allowlist von Benutzer-IDs für Raumverkehr.
- Einträge in `groupAllowFrom` sollten vollständige Matrix-Benutzer-IDs sein. Nicht aufgelöste Namen werden zur Laufzeit ignoriert.
- `historyLimit`: maximale Anzahl von Raumnachrichten, die als Gruppenverlaufs-Kontext einbezogen werden. Greift auf `messages.groupChat.historyLimit` zurück; wenn beides nicht gesetzt ist, ist der effektive Standardwert `0`. Setzen Sie `0`, um zu deaktivieren.
- `replyToMode`: `off`, `first` oder `all`.
- `markdown`: optionale Markdown-Rendering-Konfiguration für ausgehenden Matrix-Text.
- `streaming`: `off` (Standard), `partial`, `quiet`, `true` oder `false`. `partial` und `true` aktivieren Vorschau-zuerst-Entwurfsaktualisierungen mit normalen Matrix-Textnachrichten. `quiet` verwendet nicht benachrichtigende Vorschau-Mitteilungen für selbst gehostete Push-Regel-Setups.
- `blockStreaming`: `true` aktiviert separate Fortschrittsnachrichten für abgeschlossene Assistant-Blöcke, während Entwurfsvorschau-Streaming aktiv ist.
- `threadReplies`: `off`, `inbound` oder `always`.
- `threadBindings`: kanalbezogene Überschreibungen für threadgebundenes Sitzungsrouting und Lebenszyklus.
- `startupVerification`: Modus für automatische Selbstverifizierungsanfragen beim Start (`if-unverified`, `off`).
- `startupVerificationCooldownHours`: Abkühlzeit vor erneuten automatischen Startverifizierungsanfragen.
- `textChunkLimit`: Chunk-Größe für ausgehende Nachrichten.
- `chunkMode`: `length` oder `newline`.
- `responsePrefix`: optionales Nachrichtenpräfix für ausgehende Antworten.
- `ackReaction`: optionale Überschreibung der Bestätigungsreaktion für diesen Kanal/dieses Konto.
- `ackReactionScope`: optionale Überschreibung des Geltungsbereichs der Bestätigungsreaktion (`group-mentions`, `group-all`, `direct`, `all`, `none`, `off`).
- `reactionNotifications`: Modus für eingehende Reaktionsbenachrichtigungen (`own`, `off`).
- `mediaMaxMb`: Mediengrößenlimit in MB für die Matrix-Medienverarbeitung. Es gilt für ausgehende Sendungen und die Verarbeitung eingehender Medien.
- `autoJoin`: Richtlinie für automatischen Einladungsbeitritt (`always`, `allowlist`, `off`). Standard: `off`. Dies gilt allgemein für Matrix-Einladungen, einschließlich DM-artiger Einladungen, nicht nur für Raum-/Gruppeneinladungen. OpenClaw trifft diese Entscheidung zum Zeitpunkt der Einladung, bevor der beigetretene Raum zuverlässig als DM oder Gruppe klassifiziert werden kann.
- `autoJoinAllowlist`: Räume/Aliasse, die erlaubt sind, wenn `autoJoin` auf `allowlist` steht. Alias-Einträge werden während der Einladungsverarbeitung in Raum-IDs aufgelöst; OpenClaw vertraut keinem Alias-Status, der vom eingeladenen Raum behauptet wird.
- `dm`: DM-Richtlinienblock (`enabled`, `policy`, `allowFrom`, `sessionScope`, `threadReplies`).
- `dm.policy`: steuert den DM-Zugriff, nachdem OpenClaw dem Raum beigetreten ist und ihn als DM klassifiziert hat. Dies ändert nicht, ob einer Einladung automatisch beigetreten wird.
- Einträge in `dm.allowFrom` sollten vollständige Matrix-Benutzer-IDs sein, es sei denn, Sie haben sie bereits über die Live-Verzeichnissuche aufgelöst.
- `dm.sessionScope`: `per-user` (Standard) oder `per-room`. Verwenden Sie `per-room`, wenn jeder Matrix-DM-Raum einen separaten Kontext behalten soll, selbst wenn der Peer derselbe ist.
- `dm.threadReplies`: nur für DMs geltende Überschreibung der Thread-Richtlinie (`off`, `inbound`, `always`). Sie überschreibt die Einstellung `threadReplies` auf oberster Ebene sowohl für die Platzierung von Antworten als auch für die Sitzungsisolierung in DMs.
- `execApprovals`: Matrix-native Zustellung von Exec-Genehmigungen (`enabled`, `approvers`, `target`, `agentFilter`, `sessionFilter`).
- `execApprovals.approvers`: Matrix-Benutzer-IDs, die Exec-Anfragen genehmigen dürfen. Optional, wenn `dm.allowFrom` die Genehmigenden bereits identifiziert.
- `execApprovals.target`: `dm | channel | both` (Standard: `dm`).
- `accounts`: benannte kontospezifische Überschreibungen. Werte auf oberster Ebene unter `channels.matrix` fungieren als Standardwerte für diese Einträge.
- `groups`: raumbezogene Richtlinienzuordnung. Bevorzugen Sie Raum-IDs oder Aliasse; nicht aufgelöste Raumnamen werden zur Laufzeit ignoriert. Die Sitzungs-/Gruppenidentität verwendet nach der Auflösung die stabile Raum-ID, während menschenlesbare Bezeichnungen weiterhin von Raumnamen stammen.
- `groups.<room>.account`: einen geerbten Raumeintrag in Multi-Account-Setups auf ein bestimmtes Matrix-Konto beschränken.
- `groups.<room>.allowBots`: raumbezogene Überschreibung für Absender aus konfigurierten Bot-Konten (`true` oder `"mentions"`).
- `groups.<room>.users`: absenderbezogene Allowlist pro Raum.
- `groups.<room>.tools`: raumbezogene Tool-Allow-/Deny-Überschreibungen.
- `groups.<room>.autoReply`: raumbezogene Überschreibung für Erwähnungs-Gating. `true` deaktiviert Erwähnungsanforderungen für diesen Raum; `false` erzwingt sie wieder.
- `groups.<room>.skills`: optionaler raumbezogener Skills-Filter.
- `groups.<room>.systemPrompt`: optionales raumbezogenes System-Prompt-Snippet.
- `rooms`: Legacy-Alias für `groups`.
- `actions`: Tool-Gating pro Aktion (`messages`, `reactions`, `pins`, `profile`, `memberInfo`, `channelInfo`, `verification`).

## Verwandt

- [Channels Overview](/de/channels) — alle unterstützten Kanäle
- [Pairing](/de/channels/pairing) — DM-Authentifizierung und Pairing-Ablauf
- [Groups](/de/channels/groups) — Verhalten in Gruppenchats und Erwähnungs-Gating
- [Channel Routing](/de/channels/channel-routing) — Sitzungsrouting für Nachrichten
- [Security](/de/gateway/security) — Zugriffsmodell und Härtung
