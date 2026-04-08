---
read_when:
    - Eseguire o correggere i test
summary: Come eseguire i test in locale (vitest) e quando usare le modalità force/coverage
title: Test
x-i18n:
    generated_at: "2026-04-08T02:18:14Z"
    model: gpt-5.4
    provider: openai
    source_hash: f7c19390f7577b3a29796c67514c96fe4c86c9fa0c7686cd4e377c6e31dcd085
    source_path: reference/test.md
    workflow: 15
---

# Test

- Kit di test completo (suite, live, Docker): [Testing](/it/help/testing)

- `pnpm test:force`: termina qualunque processo gateway rimasto in esecuzione che occupa la porta di controllo predefinita, poi esegue l'intera suite Vitest con una porta gateway isolata in modo che i test del server non vadano in conflitto con un'istanza in esecuzione. Usa questa modalità quando una precedente esecuzione del gateway ha lasciato occupata la porta 18789.
- `pnpm test:coverage`: esegue la suite unit con copertura V8 (tramite `vitest.unit.config.ts`). Le soglie globali sono 70% per righe/branch/funzioni/statement. La copertura esclude entrypoint con integrazione pesante (wiring CLI, bridge gateway/telegram, server statico webchat) per mantenere l'obiettivo concentrato sulla logica testabile con test unitari.
- `pnpm test:coverage:changed`: esegue la copertura unit solo per i file modificati rispetto a `origin/main`.
- `pnpm test:changed`: espande i percorsi git modificati in lane Vitest con ambito quando il diff tocca solo file sorgente/test instradabili. Le modifiche a config/setup ricadono ancora nell'esecuzione nativa dei root project, così le modifiche al wiring rieseguono in modo ampio quando serve.
- `pnpm test`: instrada i target espliciti file/directory attraverso lane Vitest con ambito. Le esecuzioni senza target ora eseguono undici configurazioni shard sequenziali (`vitest.full-core-unit-src.config.ts`, `vitest.full-core-unit-security.config.ts`, `vitest.full-core-unit-ui.config.ts`, `vitest.full-core-unit-support.config.ts`, `vitest.full-core-support-boundary.config.ts`, `vitest.full-core-contracts.config.ts`, `vitest.full-core-bundled.config.ts`, `vitest.full-core-runtime.config.ts`, `vitest.full-agentic.config.ts`, `vitest.full-auto-reply.config.ts`, `vitest.full-extensions.config.ts`) invece di un unico enorme processo root-project.
- I file di test `plugin-sdk` e `commands` selezionati ora passano attraverso lane leggere dedicate che mantengono solo `test/setup.ts`, lasciando i casi pesanti a livello runtime nelle loro lane esistenti.
- Alcuni file sorgente helper `plugin-sdk` e `commands` selezionati mappano anche `pnpm test:changed` verso test sibling espliciti in quelle lane leggere, così piccole modifiche agli helper evitano di rieseguire le suite pesanti supportate dal runtime.
- `auto-reply` ora è anche suddiviso in tre configurazioni dedicate (`core`, `top-level`, `reply`) così l'harness reply non domina i test più leggeri di stato/token/helper di primo livello.
- La configurazione base di Vitest ora usa per impostazione predefinita `pool: "threads"` e `isolate: false`, con il runner condiviso non isolato abilitato nelle configurazioni del repository.
- `pnpm test:channels` esegue `vitest.channels.config.ts`.
- `pnpm test:extensions` esegue `vitest.extensions.config.ts`.
- `pnpm test:extensions`: esegue le suite extension/plugin.
- `pnpm test:perf:imports`: abilita il reporting Vitest della durata degli import + il dettaglio degli import, continuando comunque a usare il routing tramite lane con ambito per i target espliciti file/directory.
- `pnpm test:perf:imports:changed`: stesso profiling degli import, ma solo per i file modificati rispetto a `origin/main`.
- `pnpm test:perf:changed:bench -- --ref <git-ref>` misura il percorso instradato in modalità changed rispetto all'esecuzione nativa root-project per lo stesso diff git committed.
- `pnpm test:perf:changed:bench -- --worktree` misura l'insieme di modifiche del worktree corrente senza prima fare commit.
- `pnpm test:perf:profile:main`: scrive un profilo CPU per il thread principale di Vitest (`.artifacts/vitest-main-profile`).
- `pnpm test:perf:profile:runner`: scrive profili CPU + heap per il runner unit (`.artifacts/vitest-runner-profile`).
- Integrazione gateway: opt-in tramite `OPENCLAW_TEST_INCLUDE_GATEWAY=1 pnpm test` oppure `pnpm test:gateway`.
- `pnpm test:e2e`: esegue i test smoke end-to-end del gateway (pairing multiistanza WS/HTTP/nodo). Per impostazione predefinita usa `threads` + `isolate: false` con worker adattivi in `vitest.e2e.config.ts`; regola con `OPENCLAW_E2E_WORKERS=<n>` e imposta `OPENCLAW_E2E_VERBOSE=1` per log dettagliati.
- `pnpm test:live`: esegue i test live dei provider (minimax/zai). Richiede chiavi API e `LIVE=1` (oppure `*_LIVE_TEST=1` specifico del provider) per togliere lo skip.
- `pnpm test:docker:openwebui`: avvia OpenClaw + Open WebUI in Docker, accede tramite Open WebUI, controlla `/api/models`, quindi esegue una vera chat proxata tramite `/api/chat/completions`. Richiede una chiave di modello live utilizzabile (ad esempio OpenAI in `~/.profile`), scarica un'immagine Open WebUI esterna e non è pensato per essere stabile in CI come le normali suite unit/e2e.
- `pnpm test:docker:mcp-channels`: avvia un container Gateway seeded e un secondo container client che esegue `openclaw mcp serve`, poi verifica discovery delle conversazioni instradate, letture della trascrizione, metadati degli allegati, comportamento della coda eventi live, instradamento degli invii in uscita e notifiche in stile Claude di canale + permessi sul vero bridge stdio. L'asserzione sulle notifiche Claude legge direttamente i frame MCP stdio grezzi così lo smoke riflette ciò che il bridge emette davvero.

## Gate PR locale

Per i controlli locali di land/gate PR, esegui:

- `pnpm check`
- `pnpm build`
- `pnpm test`
- `pnpm check:docs`

Se `pnpm test` è instabile su un host sotto carico, rieseguilo una volta prima di trattarlo come regressione, poi isola con `pnpm test <path/to/test>`. Per host con memoria limitata, usa:

- `OPENCLAW_VITEST_MAX_WORKERS=1 pnpm test`
- `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/tmp/openclaw-vitest-cache pnpm test:changed`

## Benchmark della latenza del modello (chiavi locali)

Script: [`scripts/bench-model.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/bench-model.ts)

Uso:

- `source ~/.profile && pnpm tsx scripts/bench-model.ts --runs 10`
- Variabili env facoltative: `MINIMAX_API_KEY`, `MINIMAX_BASE_URL`, `MINIMAX_MODEL`, `ANTHROPIC_API_KEY`
- Prompt predefinito: “Rispondi con una sola parola: ok. Nessuna punteggiatura o testo aggiuntivo.”

Ultima esecuzione (2025-12-31, 20 esecuzioni):

- minimax mediana 1279ms (min 1114, max 2431)
- opus mediana 2454ms (min 1224, max 3170)

## Benchmark di avvio della CLI

Script: [`scripts/bench-cli-startup.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/bench-cli-startup.ts)

Uso:

- `pnpm test:startup:bench`
- `pnpm test:startup:bench:smoke`
- `pnpm test:startup:bench:save`
- `pnpm test:startup:bench:update`
- `pnpm test:startup:bench:check`
- `pnpm tsx scripts/bench-cli-startup.ts`
- `pnpm tsx scripts/bench-cli-startup.ts --runs 12`
- `pnpm tsx scripts/bench-cli-startup.ts --preset real`
- `pnpm tsx scripts/bench-cli-startup.ts --preset real --case status --case gatewayStatus --runs 3`
- `pnpm tsx scripts/bench-cli-startup.ts --entry openclaw.mjs --entry-secondary dist/entry.js --preset all`
- `pnpm tsx scripts/bench-cli-startup.ts --preset all --output .artifacts/cli-startup-bench-all.json`
- `pnpm tsx scripts/bench-cli-startup.ts --preset real --case gatewayStatusJson --output .artifacts/cli-startup-bench-smoke.json`
- `pnpm tsx scripts/bench-cli-startup.ts --preset real --cpu-prof-dir .artifacts/cli-cpu`
- `pnpm tsx scripts/bench-cli-startup.ts --json`

Preset:

- `startup`: `--version`, `--help`, `health`, `health --json`, `status --json`, `status`
- `real`: `health`, `status`, `status --json`, `sessions`, `sessions --json`, `agents list --json`, `gateway status`, `gateway status --json`, `gateway health --json`, `config get gateway.port`
- `all`: entrambi i preset

L'output include `sampleCount`, avg, p50, p95, min/max, distribuzione exit-code/signal e riepiloghi max RSS per ogni comando. `--cpu-prof-dir` / `--heap-prof-dir` facoltativi scrivono profili V8 per esecuzione così la misurazione dei tempi e la cattura dei profili usano lo stesso harness.

Convenzioni per l'output salvato:

- `pnpm test:startup:bench:smoke` scrive l'artefatto smoke mirato in `.artifacts/cli-startup-bench-smoke.json`
- `pnpm test:startup:bench:save` scrive l'artefatto della suite completa in `.artifacts/cli-startup-bench-all.json` usando `runs=5` e `warmup=1`
- `pnpm test:startup:bench:update` aggiorna il fixture baseline versionato in `test/fixtures/cli-startup-bench.json` usando `runs=5` e `warmup=1`

Fixture versionato:

- `test/fixtures/cli-startup-bench.json`
- Aggiornalo con `pnpm test:startup:bench:update`
- Confronta i risultati correnti con il fixture usando `pnpm test:startup:bench:check`

## Onboarding E2E (Docker)

Docker è facoltativo; serve solo per i test smoke di onboarding containerizzati.

Flusso completo da cold start in un container Linux pulito:

```bash
scripts/e2e/onboard-docker.sh
```

Questo script guida la procedura guidata interattiva tramite uno pseudo-TTY, verifica i file di config/workspace/sessione, poi avvia il gateway ed esegue `openclaw health`.

## Smoke di importazione QR (Docker)

Verifica che `qrcode-terminal` venga caricato nei runtime Docker Node supportati (Node 24 predefinito, Node 22 compatibile):

```bash
pnpm test:docker:qr
```
