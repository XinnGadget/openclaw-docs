# openclaw-docs

Mirror repo for the published OpenClaw docs site.

Source of truth lives in [`openclaw/openclaw`](https://github.com/openclaw/openclaw), under `docs/`.

## How it works

1. English docs are authored in `openclaw/openclaw`.
2. `openclaw/openclaw/.github/workflows/docs-sync-publish.yml` mirrors the docs tree into this repo.
3. This repo stores the published docs tree plus generated locale output.
4. `openclaw/docs/.github/workflows/translate-zh-cn.yml`, `translate-ja-jp.yml`, `translate-es.yml`, `translate-pt-br.yml`, `translate-ko.yml`, `translate-de.yml`, `translate-fr.yml`, `translate-ar.yml`, `translate-it.yml`, `translate-tr.yml`, `translate-id.yml`, and `translate-pl.yml` refresh the generated locale trees on a staggered daily schedule, on manual dispatch, and after release dispatches from `openclaw/openclaw`.

## Translation behavior

- zh-CN, ja-JP, es, pt-BR, ko, de, fr, ar, it, tr, id, and pl pages are generated output.
- Each translated page stores `x-i18n.source_hash`.
- The translate workflow computes a pending file list before calling the model.
- If no English source hashes changed, the workflow skips the expensive translation step entirely.
- If files changed, only the pending files are translated.
- The workflow retries transient model-format failures.
- Published releases in `openclaw/openclaw` dispatch extra locale refreshes so release-adjacent docs updates do not wait for the daily cron.

## Editing rules

- Do not treat this repo as the primary place for English doc edits.
- Make English doc changes in `openclaw/openclaw`, then let sync copy them here.
- Generated locale pages in `docs/zh-CN/**`, `docs/ja-JP/**`, `docs/es/**`, `docs/pt-BR/**`, `docs/ko/**`, `docs/de/**`, `docs/fr/**`, `docs/ar/**`, `docs/it/**`, `docs/tr/**`, `docs/id/**`, and `docs/pl/**` are generated output.
- `.openclaw-sync/source.json` records which `openclaw/openclaw` commit this mirror was synced from.

## Secrets

- `OPENCLAW_DOCS_SYNC_TOKEN` lives in `openclaw/openclaw` and lets the source repo push into this repo.
- `OPENCLAW_DOCS_I18N_OPENAI_API_KEY` lives in this repo and powers locale translation refreshes.
