---
read_when:
    - Cerchi le definizioni pubbliche dei canali di rilascio
    - Cerchi la denominazione delle versioni e la cadenza
summary: Canali di rilascio pubblici, denominazione delle versioni e cadenza
title: Policy di rilascio
x-i18n:
    generated_at: "2026-04-11T02:47:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: ca613d094c93670c012f0b79720fad0d5d85be802f54b0acb7a8f22aca5bde12
    source_path: reference/RELEASING.md
    workflow: 15
---

# Policy di rilascio

OpenClaw ha tre canali di rilascio pubblici:

- stable: release con tag che pubblicano su npm `beta` per impostazione predefinita, oppure su npm `latest` quando richiesto esplicitamente
- beta: tag di prerelease che pubblicano su npm `beta`
- dev: l'head mobile di `main`

## Denominazione delle versioni

- Versione di rilascio stable: `YYYY.M.D`
  - Tag Git: `vYYYY.M.D`
- Versione di rilascio stable correttivo: `YYYY.M.D-N`
  - Tag Git: `vYYYY.M.D-N`
- Versione di prerelease beta: `YYYY.M.D-beta.N`
  - Tag Git: `vYYYY.M.D-beta.N`
- Non aggiungere zeri iniziali a mese o giorno
- `latest` indica l'attuale release npm stable promossa
- `beta` indica l'attuale target di installazione beta
- Le release stable e stable correttive pubblicano su npm `beta` per impostazione predefinita; gli operatori di rilascio possono scegliere esplicitamente `latest` come target, oppure promuovere in un secondo momento una build beta verificata
- Ogni release OpenClaw distribuisce insieme il pacchetto npm e l'app macOS

## Cadenza di rilascio

- Le release passano prima da beta
- Stable segue solo dopo la convalida dell'ultima beta
- Procedura dettagliata di rilascio, approvazioni, credenziali e note di recupero sono
  riservate ai maintainer

## Controlli preliminari al rilascio

- Esegui `pnpm build && pnpm ui:build` prima di `pnpm release:check` in modo che gli attesi
  artifact di rilascio `dist/*` e il bundle di Control UI esistano per il passaggio
  di validazione del pacchetto
- Esegui `pnpm release:check` prima di ogni release con tag
- Il controllo preliminare npm del branch main esegue anche
  `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_CACHE_TEST=1 pnpm test:live:cache`
  prima del packaging del tarball, usando entrambi i secret di workflow
  `OPENAI_API_KEY` e `ANTHROPIC_API_KEY`
- Esegui `RELEASE_TAG=vYYYY.M.D node --import tsx scripts/openclaw-npm-release-check.ts`
  (oppure il tag beta/correttivo corrispondente) prima dell'approvazione
- Dopo la pubblicazione npm, esegui
  `node --import tsx scripts/openclaw-npm-postpublish-verify.ts YYYY.M.D`
  (oppure la versione beta/correttiva corrispondente) per verificare il percorso
  di installazione pubblicato nel registro in un prefisso temporaneo nuovo
- L'automazione di rilascio dei maintainer ora usa il modello preflight-then-promote:
  - la vera pubblicazione npm deve superare con successo un `preflight_run_id` npm
  - le release npm stable hanno come destinazione predefinita `beta`
  - la pubblicazione npm stable può scegliere esplicitamente `latest` tramite input del workflow
  - la promozione npm stable da `beta` a `latest` è ancora disponibile come modalità manuale esplicita nel workflow fidato `OpenClaw NPM Release`
  - questa modalità di promozione richiede comunque un `NPM_TOKEN` valido nell'ambiente `npm-release` perché la gestione di `dist-tag` npm è separata dalla pubblicazione fidata
  - il `macOS Release` pubblico è solo di validazione
  - la vera pubblicazione privata mac deve superare con successo il private mac
    `preflight_run_id` e `validate_run_id`
  - i veri percorsi di pubblicazione promuovono artifact preparati invece di ricostruirli nuovamente
- Per release stable correttive come `YYYY.M.D-N`, il verificatore post-pubblicazione
  controlla anche lo stesso percorso di aggiornamento con prefisso temporaneo da `YYYY.M.D` a `YYYY.M.D-N`
  in modo che le correzioni di rilascio non possano lasciare silenziosamente installazioni
  globali precedenti ferme al payload stable di base
- Il controllo preliminare della release npm fallisce in modalità closed-fail a meno che il tarball non includa sia
  `dist/control-ui/index.html` sia un payload non vuoto `dist/control-ui/assets/`
  così da non distribuire di nuovo una dashboard browser vuota
- Se il lavoro di rilascio ha toccato la pianificazione CI, i manifest temporali delle estensioni o
  le matrici di test delle estensioni, rigenera e rivedi gli output della matrice del workflow
  `checks-node-extensions` posseduti dal planner da `.github/workflows/ci.yml`
  prima dell'approvazione, così le note di rilascio non descrivono un layout CI obsoleto
- Lo stato di prontezza della release macOS stable include anche le superfici di aggiornamento:
  - la release GitHub deve finire con i pacchetti `.zip`, `.dmg` e `.dSYM.zip`
  - `appcast.xml` su `main` deve puntare al nuovo zip stable dopo la pubblicazione
  - l'app pacchettizzata deve mantenere un bundle id non di debug, un feed
    URL Sparkle non vuoto e un `CFBundleVersion` pari o superiore al floor canonico di build Sparkle
    per quella versione di rilascio

## Input del workflow NPM

`OpenClaw NPM Release` accetta questi input controllati dall'operatore:

- `tag`: tag di rilascio obbligatorio come `v2026.4.2`, `v2026.4.2-1` o
  `v2026.4.2-beta.1`
- `preflight_only`: `true` solo per validazione/build/package, `false` per il
  vero percorso di pubblicazione
- `preflight_run_id`: obbligatorio nel vero percorso di pubblicazione così il workflow riutilizza
  il tarball preparato dall'esecuzione di preflight riuscita
- `npm_dist_tag`: tag npm di destinazione per il percorso di pubblicazione; il valore predefinito è `beta`
- `promote_beta_to_latest`: `true` per saltare la pubblicazione e spostare una
  build stable `beta` già pubblicata su `latest`

Regole:

- I tag stable e correttivi possono pubblicare sia su `beta` sia su `latest`
- I tag di prerelease beta possono pubblicare solo su `beta`
- Il vero percorso di pubblicazione deve usare lo stesso `npm_dist_tag` usato durante il preflight;
  il workflow verifica quei metadati prima di continuare con la pubblicazione
- La modalità di promozione deve usare un tag stable o correttivo, `preflight_only=false`,
  `preflight_run_id` vuoto e `npm_dist_tag=beta`
- La modalità di promozione richiede anche un `NPM_TOKEN` valido nell'ambiente `npm-release`
  perché `npm dist-tag add` richiede ancora la normale autenticazione npm

## Sequenza di rilascio npm stable

Quando tagli una release npm stable:

1. Esegui `OpenClaw NPM Release` con `preflight_only=true`
2. Scegli `npm_dist_tag=beta` per il normale flusso beta-first, oppure `latest` solo
   quando vuoi intenzionalmente una pubblicazione stable diretta
3. Salva il `preflight_run_id` riuscito
4. Esegui di nuovo `OpenClaw NPM Release` con `preflight_only=false`, lo stesso
   `tag`, lo stesso `npm_dist_tag` e il `preflight_run_id` salvato
5. Se la release è arrivata su `beta`, esegui in seguito `OpenClaw NPM Release` con lo
   stesso `tag` stable, `promote_beta_to_latest=true`, `preflight_only=false`,
   `preflight_run_id` vuoto e `npm_dist_tag=beta` quando vuoi spostare quella
   build pubblicata su `latest`

La modalità di promozione richiede comunque l'approvazione dell'ambiente `npm-release` e un
`NPM_TOKEN` valido in quell'ambiente.

Questo mantiene sia il percorso di pubblicazione diretta sia il percorso di promozione beta-first
documentati e visibili agli operatori.

## Riferimenti pubblici

- [`.github/workflows/openclaw-npm-release.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-npm-release.yml)
- [`scripts/openclaw-npm-release-check.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/openclaw-npm-release-check.ts)
- [`scripts/package-mac-dist.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-dist.sh)
- [`scripts/make_appcast.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/make_appcast.sh)

I maintainer usano la documentazione privata di rilascio in
[`openclaw/maintainers/release/README.md`](https://github.com/openclaw/maintainers/blob/main/release/README.md)
per il runbook effettivo.
