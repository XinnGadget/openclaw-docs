---
read_when:
    - Cerco le definizioni dei canali di rilascio pubblici
    - Cerco la denominazione delle versioni e la cadenza
summary: Canali di rilascio pubblici, denominazione delle versioni e cadenza
title: Politica di rilascio
x-i18n:
    generated_at: "2026-04-14T08:16:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3eaf9f1786b8c9fd4f5a9c657b623cb69d1a485958e1a9b8f108511839b63587
    source_path: reference/RELEASING.md
    workflow: 15
---

# Politica di rilascio

OpenClaw ha tre canali di rilascio pubblici:

- stable: release con tag che pubblicano su npm `beta` per impostazione predefinita, oppure su npm `latest` quando richiesto esplicitamente
- beta: tag di prerelease che pubblicano su npm `beta`
- dev: la head mobile di `main`

## Denominazione delle versioni

- Versione della release stabile: `YYYY.M.D`
  - Tag Git: `vYYYY.M.D`
- Versione della release di correzione stabile: `YYYY.M.D-N`
  - Tag Git: `vYYYY.M.D-N`
- Versione della prerelease beta: `YYYY.M.D-beta.N`
  - Tag Git: `vYYYY.M.D-beta.N`
- Non aggiungere zeri iniziali a mese o giorno
- `latest` indica l'attuale release npm stabile promossa
- `beta` indica l'attuale destinazione di installazione beta
- Le release stabili e le release di correzione stabile pubblicano su npm `beta` per impostazione predefinita; gli operatori della release possono scegliere esplicitamente `latest` come destinazione, oppure promuovere in seguito una build beta verificata
- Ogni release di OpenClaw distribuisce insieme il pacchetto npm e l'app macOS

## Cadenza di rilascio

- Le release passano prima da beta
- stable segue solo dopo che l'ultima beta è stata convalidata
- La procedura dettagliata di rilascio, le approvazioni, le credenziali e le note di recupero sono
  riservate ai maintainer

## Controlli preliminari della release

- Esegui `pnpm build && pnpm ui:build` prima di `pnpm release:check` in modo che gli attesi
  artifact di rilascio `dist/*` e il bundle della Control UI esistano per il passaggio di
  validazione del pack
- Esegui `pnpm release:check` prima di ogni release con tag
- I controlli di rilascio ora vengono eseguiti in un workflow manuale separato:
  `OpenClaw Release Checks`
- Questa separazione è intenzionale: mantiene il percorso reale di release npm breve,
  deterministico e focalizzato sugli artifact, mentre i controlli live più lenti rimangono nel loro
  canale così da non rallentare o bloccare la pubblicazione
- I controlli di rilascio devono essere avviati dal workflow ref di `main` in modo che la
  logica del workflow e i secret rimangano canonici
- Quel workflow accetta come input un tag di release esistente oppure l'attuale commit SHA completo a 40 caratteri di `main`
- In modalità commit-SHA accetta solo l'attuale HEAD di `origin/main`; usa un
  tag di release per commit di release precedenti
- Anche il controllo preliminare di sola validazione `OpenClaw NPM Release` accetta l'attuale
  commit SHA completo a 40 caratteri di `main` senza richiedere un tag pubblicato
- Il percorso basato su SHA è solo di validazione e non può essere promosso a una pubblicazione reale
- In modalità SHA il workflow sintetizza `v<package.json version>` solo per il
  controllo dei metadati del pacchetto; la pubblicazione reale richiede comunque un vero tag di release
- Entrambi i workflow mantengono il percorso reale di pubblicazione e promozione su runner ospitati da GitHub,
  mentre il percorso di validazione non mutante può usare i runner Linux
  Blacksmith più grandi
- Quel workflow esegue
  `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_CACHE_TEST=1 pnpm test:live:cache`
  usando entrambi i secret di workflow `OPENAI_API_KEY` e `ANTHROPIC_API_KEY`
- Il controllo preliminare della release npm non attende più il canale separato dei controlli di rilascio
- Esegui `RELEASE_TAG=vYYYY.M.D node --import tsx scripts/openclaw-npm-release-check.ts`
  (oppure il tag beta/correzione corrispondente) prima dell'approvazione
- Dopo la pubblicazione su npm, esegui
  `node --import tsx scripts/openclaw-npm-postpublish-verify.ts YYYY.M.D`
  (oppure la versione beta/correzione corrispondente) per verificare il percorso di
  installazione del registro pubblicato in un nuovo prefisso temporaneo
- L'automazione di rilascio dei maintainer ora usa il modello controllo preliminare-poi-promozione:
  - la pubblicazione npm reale deve superare con successo un npm `preflight_run_id`
  - le release npm stabili usano `beta` per impostazione predefinita
  - la pubblicazione npm stabile può scegliere esplicitamente `latest` tramite input del workflow
  - la promozione npm stabile da `beta` a `latest` è ancora disponibile come modalità manuale esplicita nel workflow attendibile `OpenClaw NPM Release`
  - le pubblicazioni stabili dirette possono anche eseguire una modalità esplicita di sincronizzazione dei dist-tag che
    punta sia `latest` sia `beta` alla versione stabile già pubblicata
  - quelle modalità dist-tag richiedono comunque un `NPM_TOKEN` valido nell'ambiente `npm-release` perché la gestione dei `dist-tag` npm è separata dalla pubblicazione attendibile
  - `macOS Release` pubblico è solo di validazione
  - la pubblicazione reale privata per mac deve superare con successo i controlli preliminari privati per mac
    `preflight_run_id` e `validate_run_id`
  - i percorsi di pubblicazione reale promuovono artifact preparati invece di ricostruirli
    di nuovo
- Per release di correzione stabile come `YYYY.M.D-N`, il verificatore post-pubblicazione
  controlla anche lo stesso percorso di aggiornamento con prefisso temporaneo da `YYYY.M.D` a `YYYY.M.D-N`
  in modo che le correzioni di rilascio non possano lasciare silenziosamente vecchie installazioni globali sul
  payload stabile di base
- Il controllo preliminare della release npm fallisce in modo restrittivo se il tarball non include sia
  `dist/control-ui/index.html` sia un payload non vuoto `dist/control-ui/assets/`
  così da non distribuire di nuovo una dashboard browser vuota
- `pnpm test:install:smoke` applica anche il budget `unpackedSize` del pack npm al
  tarball candidato per l'aggiornamento, così l'installer e2e intercetta l'aumento accidentale del pack
  prima del percorso di pubblicazione della release
- Se il lavoro di release ha toccato la pianificazione CI, i manifest temporali delle estensioni o
  le matrici di test delle estensioni, rigenera e rivedi gli output della matrice del workflow
  `checks-node-extensions` posseduti dal planner da `.github/workflows/ci.yml`
  prima dell'approvazione, così le note di rilascio non descrivono un layout CI obsoleto
- La prontezza della release stabile macOS include anche le superfici dell'updater:
  - la release GitHub deve finire con `.zip`, `.dmg` e `.dSYM.zip` pacchettizzati
  - `appcast.xml` su `main` deve puntare al nuovo zip stabile dopo la pubblicazione
  - l'app pacchettizzata deve mantenere un bundle id non di debug, un feed Sparkle URL non vuoto
    e un `CFBundleVersion` pari o superiore alla soglia canonica di build Sparkle
    per quella versione di rilascio

## Input del workflow NPM

`OpenClaw NPM Release` accetta questi input controllati dall'operatore:

- `tag`: tag di release obbligatorio come `v2026.4.2`, `v2026.4.2-1`, oppure
  `v2026.4.2-beta.1`; quando `preflight_only=true`, può anche essere l'attuale
  commit SHA completo a 40 caratteri di `main` per un controllo preliminare di sola validazione
- `preflight_only`: `true` per sola validazione/build/package, `false` per il
  percorso di pubblicazione reale
- `preflight_run_id`: obbligatorio nel percorso di pubblicazione reale in modo che il workflow riutilizzi
  il tarball preparato dal controllo preliminare riuscito
- `npm_dist_tag`: tag npm di destinazione per il percorso di pubblicazione; il valore predefinito è `beta`
- `promote_beta_to_latest`: `true` per saltare la pubblicazione e spostare una build stabile `beta`
  già pubblicata su `latest`
- `sync_stable_dist_tags`: `true` per saltare la pubblicazione e far puntare sia `latest` sia
  `beta` a una versione stabile già pubblicata

`OpenClaw Release Checks` accetta questi input controllati dall'operatore:

- `ref`: tag di release esistente oppure l'attuale commit
  SHA completo a 40 caratteri di `main` da convalidare

Regole:

- I tag stabili e di correzione possono pubblicare sia su `beta` sia su `latest`
- I tag di prerelease beta possono pubblicare solo su `beta`
- L'input con commit SHA completo è consentito solo quando `preflight_only=true`
- La modalità commit-SHA dei controlli di rilascio richiede anche l'attuale HEAD di `origin/main`
- Il percorso di pubblicazione reale deve usare lo stesso `npm_dist_tag` usato durante il controllo preliminare;
  il workflow verifica quei metadati prima che la pubblicazione prosegua
- La modalità di promozione deve usare un tag stabile o di correzione, `preflight_only=false`,
  un `preflight_run_id` vuoto e `npm_dist_tag=beta`
- La modalità di sincronizzazione dist-tag deve usare un tag stabile o di correzione,
  `preflight_only=false`, un `preflight_run_id` vuoto, `npm_dist_tag=latest`,
  e `promote_beta_to_latest=false`
- Le modalità di promozione e sincronizzazione dist-tag richiedono anche un `NPM_TOKEN` valido perché
  `npm dist-tag add` richiede ancora la normale autenticazione npm; la pubblicazione attendibile copre
  solo il percorso di pubblicazione del pacchetto

## Sequenza della release npm stabile

Quando si prepara una release npm stabile:

1. Esegui `OpenClaw NPM Release` con `preflight_only=true`
   - Prima che esista un tag, puoi usare l'attuale commit SHA completo di `main` per un
     dry run di sola validazione del workflow di controllo preliminare
2. Scegli `npm_dist_tag=beta` per il normale flusso beta-first, oppure `latest` solo
   quando vuoi intenzionalmente una pubblicazione stabile diretta
3. Esegui `OpenClaw Release Checks` separatamente con lo stesso tag oppure con il
   commit SHA completo attuale di `main` quando vuoi la copertura live della prompt cache
   - Questo è separato apposta così la copertura live resta disponibile senza
     riaccoppiare controlli lunghi o instabili al workflow di pubblicazione
4. Salva il `preflight_run_id` riuscito
5. Esegui di nuovo `OpenClaw NPM Release` con `preflight_only=false`, lo stesso
   `tag`, lo stesso `npm_dist_tag` e il `preflight_run_id` salvato
6. Se la release è arrivata su `beta`, esegui `OpenClaw NPM Release` più tardi con lo
   stesso `tag` stabile, `promote_beta_to_latest=true`, `preflight_only=false`,
   `preflight_run_id` vuoto e `npm_dist_tag=beta` quando vuoi spostare quella
   build pubblicata su `latest`
7. Se la release è stata intenzionalmente pubblicata direttamente su `latest` e `beta`
   deve seguire la stessa build stabile, esegui `OpenClaw NPM Release` con lo stesso
   `tag` stabile, `sync_stable_dist_tags=true`, `promote_beta_to_latest=false`,
   `preflight_only=false`, `preflight_run_id` vuoto e `npm_dist_tag=latest`

Le modalità di promozione e sincronizzazione dist-tag richiedono comunque l'approvazione dell'ambiente `npm-release`
e un `NPM_TOKEN` valido accessibile a quell'esecuzione del workflow.

Questo mantiene sia il percorso di pubblicazione diretta sia il percorso di promozione beta-first
documentati e visibili agli operatori.

## Riferimenti pubblici

- [`.github/workflows/openclaw-npm-release.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-npm-release.yml)
- [`.github/workflows/openclaw-release-checks.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-release-checks.yml)
- [`scripts/openclaw-npm-release-check.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/openclaw-npm-release-check.ts)
- [`scripts/package-mac-dist.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-dist.sh)
- [`scripts/make_appcast.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/make_appcast.sh)

I maintainer usano la documentazione privata di rilascio in
[`openclaw/maintainers/release/README.md`](https://github.com/openclaw/maintainers/blob/main/release/README.md)
per la runbook effettiva.
