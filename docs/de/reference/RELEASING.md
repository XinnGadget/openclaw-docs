---
read_when:
    - Suche nach Definitionen öffentlicher Release-Kanäle
    - Suche nach Versionsbenennung und Veröffentlichungsrhythmus
summary: Öffentliche Release-Kanäle, Versionsbenennung und Veröffentlichungsrhythmus
title: Release-Richtlinie
x-i18n:
    generated_at: "2026-04-15T06:21:27Z"
    model: gpt-5.4
    provider: openai
    source_hash: 88724307269ab783a9fbf8a0540fea198d8a3add68457f4e64d5707114fa518c
    source_path: reference/RELEASING.md
    workflow: 15
---

# Release-Richtlinie

OpenClaw hat drei öffentliche Release-Kanäle:

- stable: getaggte Releases, die standardmäßig auf npm `beta` veröffentlicht werden, oder auf npm `latest`, wenn dies ausdrücklich angefordert wird
- beta: Prerelease-Tags, die auf npm `beta` veröffentlicht werden
- dev: der fortlaufende Stand von `main`

## Versionsbenennung

- Stabile Release-Version: `YYYY.M.D`
  - Git-Tag: `vYYYY.M.D`
- Stabile Korrektur-Release-Version: `YYYY.M.D-N`
  - Git-Tag: `vYYYY.M.D-N`
- Beta-Prerelease-Version: `YYYY.M.D-beta.N`
  - Git-Tag: `vYYYY.M.D-beta.N`
- Monat oder Tag nicht mit führenden Nullen auffüllen
- `latest` bedeutet das aktuell beworbene stabile npm-Release
- `beta` bedeutet das aktuelle Beta-Installationsziel
- Stabile und stabile Korrektur-Releases werden standardmäßig auf npm `beta` veröffentlicht; Release-Verantwortliche können ausdrücklich `latest` als Ziel festlegen oder später einen geprüften Beta-Build heraufstufen
- Jedes OpenClaw-Release liefert das npm-Paket und die macOS-App gemeinsam aus

## Release-Rhythmus

- Releases laufen nach dem Beta-first-Prinzip
- Stable folgt erst, nachdem die neueste Beta validiert wurde
- Detailliertes Release-Verfahren, Freigaben, Anmeldedaten und Wiederherstellungshinweise sind
  nur für Maintainer bestimmt

## Release-Preflight

- Führe `pnpm build && pnpm ui:build` vor `pnpm release:check` aus, damit die erwarteten
  `dist/*`-Release-Artefakte und das Control-UI-Bundle für den
  Pack-Validierungsschritt vorhanden sind
- Führe `pnpm release:check` vor jedem getaggten Release aus
- Release-Prüfungen laufen jetzt in einem separaten manuellen Workflow:
  `OpenClaw Release Checks`
- Die laufzeitbezogene Cross-OS-Installations- und Upgrade-Validierung wird aus dem
  privaten aufrufenden Workflow
  `openclaw/releases-private/.github/workflows/openclaw-cross-os-release-checks.yml`
  ausgelöst, der den wiederverwendbaren öffentlichen Workflow
  `.github/workflows/openclaw-cross-os-release-checks-reusable.yml`
  aufruft
- Diese Aufteilung ist beabsichtigt: Der echte npm-Release-Pfad soll kurz,
  deterministisch und artefaktfokussiert bleiben, während langsamere Live-Prüfungen in ihrem
  eigenen Kanal bleiben, damit sie die Veröffentlichung nicht verzögern oder blockieren
- Release-Prüfungen müssen von der Workflow-Referenz `main` ausgelöst werden, damit die
  Workflow-Logik und Secrets kanonisch bleiben
- Dieser Workflow akzeptiert entweder ein vorhandenes Release-Tag oder den aktuellen vollständigen
  40-stelligen `main`-Commit-SHA
- Im Commit-SHA-Modus akzeptiert er nur den aktuellen `origin/main`-HEAD; verwende ein
  Release-Tag für ältere Release-Commits
- Das nur zur Validierung dienende Preflight von `OpenClaw NPM Release` akzeptiert ebenfalls den aktuellen
  vollständigen 40-stelligen `main`-Commit-SHA, ohne ein gepushtes Tag zu erfordern
- Dieser SHA-Pfad dient nur der Validierung und kann nicht in eine echte Veröffentlichung überführt werden
- Im SHA-Modus synthetisiert der Workflow `v<package.json version>` nur für die
  Prüfung der Paketmetadaten; für die echte Veröffentlichung ist weiterhin ein echtes Release-Tag erforderlich
- Beide Workflows behalten den echten Veröffentlichungs- und Promotionspfad auf von GitHub gehosteten
  Runnern, während der nicht-mutierende Validierungspfad die größeren
  Blacksmith-Linux-Runner verwenden kann
- Dieser Workflow führt
  `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_CACHE_TEST=1 pnpm test:live:cache`
  aus und verwendet dabei sowohl die Workflow-Secrets `OPENAI_API_KEY` als auch `ANTHROPIC_API_KEY`
- Das npm-Release-Preflight wartet nicht mehr auf den separaten Kanal für Release-Prüfungen
- Führe `RELEASE_TAG=vYYYY.M.D node --import tsx scripts/openclaw-npm-release-check.ts`
  (oder das passende Beta-/Korrektur-Tag) vor der Freigabe aus
- Führe nach der npm-Veröffentlichung
  `node --import tsx scripts/openclaw-npm-postpublish-verify.ts YYYY.M.D`
  (oder die passende Beta-/Korrektur-Version) aus, um den veröffentlichten Registry-
  Installationspfad in einem frischen temporären Prefix zu verifizieren
- Die Maintainer-Release-Automatisierung verwendet jetzt Preflight-then-promote:
  - die echte npm-Veröffentlichung muss ein erfolgreiches npm-`preflight_run_id` bestehen
  - stabile npm-Releases verwenden standardmäßig `beta`
  - die stabile npm-Veröffentlichung kann über Workflow-Eingabe ausdrücklich `latest` als Ziel verwenden
  - tokenbasierte npm-dist-tag-Mutationen liegen jetzt in
    `openclaw/releases-private/.github/workflows/openclaw-npm-dist-tags.yml`
    aus Sicherheitsgründen, weil `npm dist-tag add` weiterhin `NPM_TOKEN` benötigt, während das
    öffentliche Repo nur OIDC-basierte Veröffentlichung beibehält
  - öffentliches `macOS Release` dient nur der Validierung
  - die echte private mac-Veröffentlichung muss ein erfolgreiches privates mac-
    `preflight_run_id` und `validate_run_id` bestehen
  - die echten Veröffentlichungspfade stufen vorbereitete Artefakte herauf, statt sie
    erneut neu zu erstellen
- Für stabile Korrektur-Releases wie `YYYY.M.D-N` prüft der Post-Publish-Verifizierer
  zusätzlich denselben temporären Prefix-Upgrade-Pfad von `YYYY.M.D` auf `YYYY.M.D-N`,
  damit Release-Korrekturen nicht stillschweigend ältere globale Installationen auf der
  Basis-Stable-Nutzlast belassen
- Das npm-Release-Preflight schlägt standardmäßig fehl, sofern das Tarball nicht sowohl
  `dist/control-ui/index.html` als auch eine nicht leere `dist/control-ui/assets/`-Nutzlast enthält,
  damit wir nicht erneut ein leeres Browser-Dashboard ausliefern
- `pnpm test:install:smoke` erzwingt außerdem das `unpackedSize`-Budget des npm-Packs für
  das Kandidaten-Update-Tarball, sodass das Installer-E2E versehentliche Pack-Aufblähung
  vor dem Release-Veröffentlichungspfad erkennt
- Wenn die Release-Arbeit die CI-Planung, Timing-Manifeste von Plugins oder
  Plugin-Testmatrizen betroffen hat, generiere und prüfe vor der Freigabe die vom Planner verwalteten
  Ausgaben der Workflow-Matrix `checks-node-extensions` aus `.github/workflows/ci.yml`
  erneut, damit die Release Notes kein veraltetes CI-Layout beschreiben
- Zur Bereitschaft eines stabilen macOS-Releases gehören auch die Updater-Oberflächen:
  - Das GitHub-Release muss schließlich die paketierten `.zip`-, `.dmg`- und `.dSYM.zip`-Dateien enthalten
  - `appcast.xml` auf `main` muss nach der Veröffentlichung auf die neue stabile ZIP-Datei zeigen
  - Die paketierte App muss eine Nicht-Debug-Bundle-ID, eine nicht leere Sparkle-Feed-
    URL und eine `CFBundleVersion` beibehalten, die mindestens der kanonischen Sparkle-Build-Untergrenze
    für diese Release-Version entspricht

## NPM-Workflow-Eingaben

`OpenClaw NPM Release` akzeptiert diese operatorgesteuerten Eingaben:

- `tag`: erforderliches Release-Tag wie `v2026.4.2`, `v2026.4.2-1` oder
  `v2026.4.2-beta.1`; wenn `preflight_only=true`, kann dies auch der aktuelle
  vollständige 40-stellige `main`-Commit-SHA für ein nur zur Validierung dienendes Preflight sein
- `preflight_only`: `true` nur für Validierung/Build/Paketierung, `false` für den
  echten Veröffentlichungspfad
- `preflight_run_id`: im echten Veröffentlichungspfad erforderlich, damit der Workflow das
  vorbereitete Tarball aus dem erfolgreichen Preflight-Lauf wiederverwendet
- `npm_dist_tag`: npm-Ziel-Tag für den Veröffentlichungspfad; Standardwert ist `beta`

`OpenClaw Release Checks` akzeptiert diese operatorgesteuerten Eingaben:

- `ref`: vorhandenes Release-Tag oder der aktuelle vollständige 40-stellige `main`-Commit-
  SHA zur Validierung

Regeln:

- Stable- und Korrektur-Tags können entweder auf `beta` oder `latest` veröffentlicht werden
- Beta-Prerelease-Tags dürfen nur auf `beta` veröffentlicht werden
- Die Eingabe eines vollständigen Commit-SHA ist nur erlaubt, wenn `preflight_only=true`
- Der Commit-SHA-Modus für Release-Prüfungen erfordert außerdem den aktuellen `origin/main`-HEAD
- Der echte Veröffentlichungspfad muss denselben `npm_dist_tag` verwenden, der auch während des Preflights verwendet wurde;
  der Workflow prüft diese Metadaten, bevor die Veröffentlichung fortgesetzt wird

## Sequenz für stabiles npm-Release

Beim Erstellen eines stabilen npm-Releases:

1. Führe `OpenClaw NPM Release` mit `preflight_only=true` aus
   - Bevor ein Tag existiert, kannst du den aktuellen vollständigen `main`-Commit-SHA für einen
     nur zur Validierung dienenden Dry-Run des Preflight-Workflows verwenden
2. Wähle `npm_dist_tag=beta` für den normalen Beta-first-Ablauf oder `latest` nur dann,
   wenn du absichtlich eine direkte stabile Veröffentlichung möchtest
3. Führe `OpenClaw Release Checks` separat mit demselben Tag oder dem
   vollständigen aktuellen `main`-Commit-SHA aus, wenn du eine Live-Abdeckung für den Prompt-Cache möchtest
   - Dies ist absichtlich getrennt, damit Live-Abdeckung verfügbar bleibt, ohne
     lang laufende oder instabile Prüfungen wieder an den Veröffentlichungs-Workflow zu koppeln
4. Speichere die erfolgreiche `preflight_run_id`
5. Führe `OpenClaw NPM Release` erneut mit `preflight_only=false`, demselben
   `tag`, demselben `npm_dist_tag` und der gespeicherten `preflight_run_id` aus
6. Wenn das Release auf `beta` gelandet ist, verwende den privaten
   Workflow `openclaw/releases-private/.github/workflows/openclaw-npm-dist-tags.yml`,
   um diese stabile Version von `beta` auf `latest` heraufzustufen
7. Wenn das Release absichtlich direkt auf `latest` veröffentlicht wurde und `beta`
   sofort demselben stabilen Build folgen soll, verwende denselben privaten
   Workflow, um beide Dist-Tags auf die stabile Version zu setzen, oder überlasse es seiner geplanten
   Selbstheilungs-Synchronisierung, `beta` später zu verschieben

Die Dist-Tag-Mutation liegt aus Sicherheitsgründen im privaten Repo, da sie weiterhin
`NPM_TOKEN` erfordert, während das öffentliche Repo nur OIDC-basierte Veröffentlichung beibehält.

Dadurch bleiben sowohl der direkte Veröffentlichungspfad als auch der Beta-first-Promotionspfad
dokumentiert und für Operatoren sichtbar.

## Öffentliche Referenzen

- [`.github/workflows/openclaw-npm-release.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-npm-release.yml)
- [`.github/workflows/openclaw-release-checks.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-release-checks.yml)
- [`.github/workflows/openclaw-cross-os-release-checks-reusable.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-cross-os-release-checks-reusable.yml)
- [`scripts/openclaw-npm-release-check.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/openclaw-npm-release-check.ts)
- [`scripts/package-mac-dist.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-dist.sh)
- [`scripts/make_appcast.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/make_appcast.sh)

Maintainer verwenden die privaten Release-Dokumente in
[`openclaw/maintainers/release/README.md`](https://github.com/openclaw/maintainers/blob/main/release/README.md)
als tatsächliches Runbook.
