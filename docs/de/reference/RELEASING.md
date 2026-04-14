---
read_when:
    - Suche nach öffentlichen Release-Kanal-Definitionen
    - Suche nach Versionsbenennung und Kadenz
summary: Öffentliche Release-Kanäle, Versionsbenennung und Kadenz
title: Release-Richtlinie
x-i18n:
    generated_at: "2026-04-14T02:08:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: fdc32839447205d74ba7a20a45fbac8e13b199174b442a1e260e3fce056c63da
    source_path: reference/RELEASING.md
    workflow: 15
---

# Release-Richtlinie

OpenClaw hat drei öffentliche Release-Kanäle:

- stable: getaggte Releases, die standardmäßig auf npm `beta` veröffentlichen oder bei ausdrücklicher Anforderung auf npm `latest`
- beta: Prerelease-Tags, die auf npm `beta` veröffentlichen
- dev: der fortlaufende aktuelle Stand von `main`

## Versionsbenennung

- Version für stabiles Release: `YYYY.M.D`
  - Git-Tag: `vYYYY.M.D`
- Version für stabiles Korrektur-Release: `YYYY.M.D-N`
  - Git-Tag: `vYYYY.M.D-N`
- Version für Beta-Prerelease: `YYYY.M.D-beta.N`
  - Git-Tag: `vYYYY.M.D-beta.N`
- Monat oder Tag nicht mit führenden Nullen auffüllen
- `latest` bedeutet das aktuell beworbene stabile npm-Release
- `beta` bedeutet das aktuelle Beta-Installationsziel
- Stabile und stabile Korrektur-Releases veröffentlichen standardmäßig auf npm `beta`; Release-Operatoren können explizit `latest` als Ziel wählen oder einen geprüften Beta-Build später hochstufen
- Jedes OpenClaw-Release liefert das npm-Paket und die macOS-App gemeinsam aus

## Release-Kadenz

- Releases gehen zuerst in `beta`
- `stable` folgt erst, nachdem die neueste Beta validiert wurde
- Das detaillierte Release-Verfahren, Freigaben, Zugangsdaten und Hinweise zur Wiederherstellung sind nur für Maintainer bestimmt

## Release-Preflight

- Führe `pnpm build && pnpm ui:build` vor `pnpm release:check` aus, damit die erwarteten `dist/*`-Release-Artefakte und das Control-UI-Bundle für den Schritt zur Paketvalidierung vorhanden sind
- Führe `pnpm release:check` vor jedem getaggten Release aus
- Release-Prüfungen laufen jetzt in einem separaten manuellen Workflow:
  `OpenClaw Release Checks`
- Diese Aufteilung ist beabsichtigt: Der echte npm-Release-Pfad bleibt kurz,
  deterministisch und artefaktorientiert, während langsamere Live-Prüfungen in
  ihrer eigenen Spur bleiben, damit sie die Veröffentlichung nicht verzögern
  oder blockieren
- Release-Prüfungen müssen vom Workflow-Ref `main` ausgelöst werden, damit die
  Workflow-Logik und Secrets kanonisch bleiben
- Dieser Workflow akzeptiert entweder ein vorhandenes Release-Tag oder den
  aktuellen vollständigen 40-stelligen `main`-Commit-SHA
- Im Commit-SHA-Modus wird nur der aktuelle `origin/main`-HEAD akzeptiert; für
  ältere Release-Commits muss ein Release-Tag verwendet werden
- Das nur validierende Preflight von `OpenClaw NPM Release` akzeptiert ebenfalls
  den aktuellen vollständigen 40-stelligen `main`-Commit-SHA, ohne dass ein
  gepushtes Tag erforderlich ist
- Dieser SHA-Pfad dient nur der Validierung und kann nicht in eine echte
  Veröffentlichung hochgestuft werden
- Im SHA-Modus synthetisiert der Workflow `v<package.json version>` nur für die
  Prüfung der Paketmetadaten; für die echte Veröffentlichung ist weiterhin ein
  echtes Release-Tag erforderlich
- Beide Workflows halten den echten Veröffentlichungs- und Hochstufungspfad auf
  GitHub-gehosteten Runnern, während der nicht mutierende Validierungspfad die
  größeren Blacksmith-Linux-Runner verwenden kann
- Dieser Workflow führt
  `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_CACHE_TEST=1 pnpm test:live:cache`
  unter Verwendung der Workflow-Secrets `OPENAI_API_KEY` und
  `ANTHROPIC_API_KEY` aus
- Das npm-Release-Preflight wartet nicht mehr auf die separate Spur für
  Release-Prüfungen
- Führe vor der Freigabe
  `RELEASE_TAG=vYYYY.M.D node --import tsx scripts/openclaw-npm-release-check.ts`
  aus (oder das entsprechende Beta-/Korrektur-Tag)
- Führe nach der npm-Veröffentlichung
  `node --import tsx scripts/openclaw-npm-postpublish-verify.ts YYYY.M.D`
  aus (oder die entsprechende Beta-/Korrekturversion), um den veröffentlichten
  Registry-Installationspfad in einem frischen temporären Prefix zu verifizieren
- Die Maintainer-Release-Automatisierung verwendet jetzt Preflight-then-Promote:
  - eine echte npm-Veröffentlichung muss ein erfolgreiches npm-`preflight_run_id` bestehen
  - stabile npm-Releases verwenden standardmäßig `beta`
  - stabile npm-Veröffentlichungen können `latest` explizit über einen Workflow-Input als Ziel verwenden
  - die Hochstufung eines stabilen npm-Releases von `beta` auf `latest` ist weiterhin als expliziter manueller Modus im vertrauenswürdigen Workflow `OpenClaw NPM Release` verfügbar
  - direkte stabile Veröffentlichungen können außerdem einen expliziten Dist-Tag-Synchronisationsmodus ausführen, der sowohl `latest` als auch `beta` auf die bereits veröffentlichte stabile Version setzt
  - diese Dist-Tag-Modi benötigen weiterhin ein gültiges `NPM_TOKEN` in der Umgebung `npm-release`, weil die Verwaltung von npm-`dist-tag` getrennt vom vertrauenswürdigen Publishing erfolgt
  - die öffentliche `macOS Release` ist nur zur Validierung
  - eine echte private macOS-Veröffentlichung muss erfolgreiche private macOS-`preflight_run_id` und `validate_run_id` bestehen
  - die echten Veröffentlichungspfade stufen vorbereitete Artefakte hoch, anstatt sie erneut zu bauen
- Bei stabilen Korrektur-Releases wie `YYYY.M.D-N` prüft der Verifier nach der
  Veröffentlichung außerdem denselben temporären Prefix-Upgrade-Pfad von
  `YYYY.M.D` zu `YYYY.M.D-N`, damit Release-Korrekturen nicht stillschweigend
  ältere globale Installationen auf der Basis-Nutzlast des stabilen Releases
  belassen
- Das npm-Release-Preflight schlägt standardmäßig geschlossen fehl, es sei denn,
  das Tarball enthält sowohl `dist/control-ui/index.html` als auch eine nicht
  leere Nutzlast in `dist/control-ui/assets/`, damit wir nicht noch einmal ein
  leeres Browser-Dashboard ausliefern
- Wenn die Release-Arbeit die CI-Planung, Timing-Manifeste von Erweiterungen
  oder Testmatrizen von Erweiterungen berührt hat, generiere und prüfe vor der
  Freigabe die planner-eigenen Workflow-Matrix-Ausgaben `checks-node-extensions`
  aus `.github/workflows/ci.yml`, damit Release Notes keine veraltete
  CI-Struktur beschreiben
- Die Bereitschaft für ein stabiles macOS-Release umfasst auch die Updater-Oberflächen:
  - Das GitHub-Release muss am Ende die paketierten Dateien `.zip`, `.dmg` und `.dSYM.zip` enthalten
  - `appcast.xml` auf `main` muss nach der Veröffentlichung auf die neue stabile ZIP-Datei zeigen
  - Die paketierte App muss eine nicht für Debug bestimmte Bundle-ID, eine nicht leere Sparkle-Feed-URL und eine `CFBundleVersion` auf oder über der kanonischen Sparkle-Build-Untergrenze für diese Release-Version behalten

## NPM-Workflow-Inputs

`OpenClaw NPM Release` akzeptiert diese operatorgesteuerten Inputs:

- `tag`: erforderliches Release-Tag wie `v2026.4.2`, `v2026.4.2-1` oder
  `v2026.4.2-beta.1`; wenn `preflight_only=true`, darf dies auch der aktuelle
  vollständige 40-stellige `main`-Commit-SHA für ein nur validierendes
  Preflight sein
- `preflight_only`: `true` nur für Validierung/Build/Paketierung, `false` für
  den echten Veröffentlichungspfad
- `preflight_run_id`: im echten Veröffentlichungspfad erforderlich, damit der
  Workflow das vorbereitete Tarball aus dem erfolgreichen Preflight-Lauf
  wiederverwendet
- `npm_dist_tag`: npm-Ziel-Tag für den Veröffentlichungspfad; Standard ist `beta`
- `promote_beta_to_latest`: `true`, um die Veröffentlichung zu überspringen und
  einen bereits veröffentlichten stabilen `beta`-Build auf `latest` zu
  verschieben
- `sync_stable_dist_tags`: `true`, um die Veröffentlichung zu überspringen und
  sowohl `latest` als auch `beta` auf eine bereits veröffentlichte stabile
  Version zu setzen

`OpenClaw Release Checks` akzeptiert diese operatorgesteuerten Inputs:

- `ref`: vorhandenes Release-Tag oder der aktuelle vollständige 40-stellige
  `main`-Commit-SHA zur Validierung

Regeln:

- Stabile und Korrektur-Tags dürfen entweder auf `beta` oder `latest` veröffentlichen
- Beta-Prerelease-Tags dürfen nur auf `beta` veröffentlichen
- Die Eingabe eines vollständigen Commit-SHA ist nur erlaubt, wenn `preflight_only=true`
- Der Commit-SHA-Modus für Release-Prüfungen erfordert ebenfalls den aktuellen `origin/main`-HEAD
- Der echte Veröffentlichungspfad muss dasselbe `npm_dist_tag` verwenden wie im Preflight; der Workflow verifiziert diese Metadaten, bevor die Veröffentlichung fortgesetzt wird
- Der Hochstufungsmodus muss ein stabiles oder Korrektur-Tag, `preflight_only=false`, eine leere `preflight_run_id` und `npm_dist_tag=beta` verwenden
- Der Dist-Tag-Synchronisationsmodus muss ein stabiles oder Korrektur-Tag,
  `preflight_only=false`, eine leere `preflight_run_id`, `npm_dist_tag=latest`
  und `promote_beta_to_latest=false` verwenden
- Hochstufungs- und Dist-Tag-Synchronisationsmodi erfordern außerdem ein
  gültiges `NPM_TOKEN`, weil `npm dist-tag add` weiterhin normale npm-Auth
  benötigt; vertrauenswürdiges Publishing deckt nur den Paket-Veröffentlichungspfad ab

## Sequenz für stabiles npm-Release

Beim Erstellen eines stabilen npm-Releases:

1. Führe `OpenClaw NPM Release` mit `preflight_only=true` aus
   - Bevor ein Tag existiert, kannst du den aktuellen vollständigen
     `main`-Commit-SHA für einen nur validierenden Probelauf des
     Preflight-Workflows verwenden
2. Wähle `npm_dist_tag=beta` für den normalen Beta-first-Ablauf oder `latest`
   nur dann, wenn du absichtlich eine direkte stabile Veröffentlichung willst
3. Führe `OpenClaw Release Checks` separat mit demselben Tag oder dem
   vollständigen aktuellen `main`-Commit-SHA aus, wenn du Live-Abdeckung für
   den Prompt-Cache möchtest
   - Dies ist absichtlich getrennt, damit Live-Abdeckung verfügbar bleibt,
     ohne lang laufende oder instabile Prüfungen wieder an den
     Veröffentlichungs-Workflow zu koppeln
4. Speichere die erfolgreiche `preflight_run_id`
5. Führe `OpenClaw NPM Release` erneut mit `preflight_only=false`, demselben
   `tag`, demselben `npm_dist_tag` und der gespeicherten `preflight_run_id` aus
6. Wenn das Release auf `beta` gelandet ist, führe `OpenClaw NPM Release`
   später mit demselben stabilen `tag`, `promote_beta_to_latest=true`,
   `preflight_only=false`, leerer `preflight_run_id` und `npm_dist_tag=beta`
   aus, wenn du diesen veröffentlichten Build auf `latest` verschieben willst
7. Wenn das Release absichtlich direkt auf `latest` veröffentlicht wurde und
   `beta` demselben stabilen Build folgen soll, führe `OpenClaw NPM Release`
   mit demselben stabilen `tag`, `sync_stable_dist_tags=true`,
   `promote_beta_to_latest=false`, `preflight_only=false`, leerer
   `preflight_run_id` und `npm_dist_tag=latest` aus

Die Hochstufungs- und Dist-Tag-Synchronisationsmodi benötigen weiterhin die
Freigabe für die Umgebung `npm-release` und ein gültiges `NPM_TOKEN`, auf das
dieser Workflow-Lauf zugreifen kann.

Damit bleiben sowohl der direkte Veröffentlichungspfad als auch der
Beta-first-Hochstufungspfad dokumentiert und für Operatoren sichtbar.

## Öffentliche Referenzen

- [`.github/workflows/openclaw-npm-release.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-npm-release.yml)
- [`.github/workflows/openclaw-release-checks.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-release-checks.yml)
- [`scripts/openclaw-npm-release-check.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/openclaw-npm-release-check.ts)
- [`scripts/package-mac-dist.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-dist.sh)
- [`scripts/make_appcast.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/make_appcast.sh)

Maintainer verwenden die privaten Release-Dokumente in
[`openclaw/maintainers/release/README.md`](https://github.com/openclaw/maintainers/blob/main/release/README.md)
als tatsächliches Runbook.
