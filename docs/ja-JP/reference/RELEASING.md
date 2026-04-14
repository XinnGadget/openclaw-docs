---
read_when:
    - 公開リリースチャネルの定義を探す
    - バージョン命名とリリース頻度を探す
summary: 公開リリースチャネル、バージョン命名、およびリリース頻度
title: リリースポリシー
x-i18n:
    generated_at: "2026-04-14T04:43:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3eaf9f1786b8c9fd4f5a9c657b623cb69d1a485958e1a9b8f108511839b63587
    source_path: reference/RELEASING.md
    workflow: 15
---

# リリースポリシー

OpenClaw には 3 つの公開リリースレーンがあります。

- stable: タグ付きリリースで、デフォルトでは npm の `beta` に公開され、明示的に要求された場合は npm の `latest` に公開されます
- beta: npm の `beta` に公開されるプレリリースタグ
- dev: `main` の移動する先頭

## バージョン命名

- stable リリースのバージョン: `YYYY.M.D`
  - Git タグ: `vYYYY.M.D`
- stable 修正リリースのバージョン: `YYYY.M.D-N`
  - Git タグ: `vYYYY.M.D-N`
- beta プレリリースのバージョン: `YYYY.M.D-beta.N`
  - Git タグ: `vYYYY.M.D-beta.N`
- 月や日はゼロ埋めしないでください
- `latest` は現在昇格済みの stable npm リリースを意味します
- `beta` は現在の beta インストール対象を意味します
- stable および stable 修正リリースはデフォルトで npm の `beta` に公開されます。リリース運用者は明示的に `latest` を対象にすることも、検証済みの beta ビルドを後で昇格させることもできます
- すべての OpenClaw リリースでは、npm パッケージと macOS アプリが一緒に出荷されます

## リリース頻度

- リリースは beta-first で進みます
- stable は最新の beta が検証された後にのみ続きます
- 詳細なリリース手順、承認、認証情報、復旧メモは
  maintainer 限定です

## リリース事前確認

- pack
  検証ステップで期待される `dist/*` のリリース成果物と Control UI バンドルが存在するように、`pnpm release:check` の前に `pnpm build && pnpm ui:build` を実行してください
- すべてのタグ付きリリースの前に `pnpm release:check` を実行してください
- リリースチェックは現在、別個の手動ワークフローで実行されます:
  `OpenClaw Release Checks`
- この分離は意図的なものです。実際の npm リリース経路を短く、
  決定的で、成果物重視のものに保ちながら、低速なライブチェックは
  独自のレーンに分離し、公開を停滞またはブロックしないようにします
- リリースチェックは `main` のワークフロー ref からディスパッチする必要があります。これにより、
  ワークフローロジックとシークレットが正規のものに保たれます
- そのワークフローは、既存のリリースタグまたは現在の完全な
  40 文字の `main` コミット SHA のいずれかを受け付けます
- コミット SHA モードでは、現在の `origin/main` HEAD のみを受け付けます。古いリリースコミットには
  リリースタグを使用してください
- `OpenClaw NPM Release` の検証専用事前確認でも、プッシュ済みタグを必要とせずに現在の完全な 40 文字の `main` コミット SHA を受け付けます
- その SHA パスは検証専用であり、実際の公開に昇格することはできません
- SHA モードでは、ワークフローはパッケージメタデータチェックのためにのみ `v<package.json version>` を合成します。実際の公開には依然として実際のリリースタグが必要です
- 両方のワークフローは、実際の公開および昇格経路を GitHub-hosted
  ランナー上に維持しつつ、変更を伴わない検証経路ではより大きな
  Blacksmith Linux ランナーを使用できます
- そのワークフローは
  `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_CACHE_TEST=1 pnpm test:live:cache`
  を、`OPENAI_API_KEY` と `ANTHROPIC_API_KEY` の両方のワークフローシークレットを使用して実行します
- npm リリース事前確認は、別個のリリースチェックレーンを待たなくなりました
- 承認前に
  `RELEASE_TAG=vYYYY.M.D node --import tsx scripts/openclaw-npm-release-check.ts`
  （または対応する beta/修正タグ）を実行してください
- npm 公開後、公開されたレジストリの
  インストール経路を新しい一時プレフィックスで検証するために、
  `node --import tsx scripts/openclaw-npm-postpublish-verify.ts YYYY.M.D`
  （または対応する beta/修正バージョン）を実行してください
- maintainer 向けリリース自動化は現在、事前確認してから昇格する方式を使用します:
  - 実際の npm 公開は、成功した npm `preflight_run_id` に合格している必要があります
  - stable npm リリースのデフォルトは `beta` です
  - stable npm 公開は、ワークフロー入力で明示的に `latest` を対象にできます
  - `beta` から `latest` への stable npm 昇格は、信頼済みの `OpenClaw NPM Release` ワークフロー上で明示的な手動モードとして引き続き利用できます
  - 直接の stable 公開では、すでに公開済みの stable バージョンに `latest` と `beta` の両方を向ける明示的な dist-tag 同期モードも実行できます
  - これらの dist-tag モードでも、npm の `dist-tag` 管理は信頼済み公開とは別であるため、`npm-release` 環境内の有効な `NPM_TOKEN` が引き続き必要です
  - 公開の `macOS Release` は検証専用です
  - 実際の private mac 公開は、成功した private mac の
    `preflight_run_id` と `validate_run_id` に合格している必要があります
  - 実際の公開経路では、準備済み成果物を再ビルドせずに昇格させます
- `YYYY.M.D-N` のような stable 修正リリースでは、公開後検証ツールは
  `YYYY.M.D` から `YYYY.M.D-N` への同じ一時プレフィックスのアップグレード経路も確認するため、
  リリース修正によって古いグローバルインストールが元の stable ペイロードのまま
  気づかれず残ることはありません
- npm リリース事前確認は、tarball に `dist/control-ui/index.html` と空でない `dist/control-ui/assets/` ペイロードの両方が含まれていない限り fail closed になるため、
  空のブラウザダッシュボードを再び出荷することはありません
- `pnpm test:install:smoke` は候補アップデート tarball の npm pack `unpackedSize` 予算も適用するため、
  インストーラー E2E で公開経路の前に pack の意図しない肥大化を検出できます
- リリース作業で CI 計画、拡張タイミングマニフェスト、または
  拡張テストマトリクスに触れた場合は、承認前に `.github/workflows/ci.yml` から planner が所有する
  `checks-node-extensions` ワークフローマトリクス出力を再生成して確認してください。これによりリリースノートが古い CI レイアウトを説明することを防げます
- stable macOS リリースの準備完了には、アップデーター関連の面も含まれます:
  - GitHub リリースには、パッケージ化された `.zip`、`.dmg`、および `.dSYM.zip` が含まれている必要があります
  - `main` 上の `appcast.xml` は、公開後に新しい stable zip を指している必要があります
  - パッケージ化されたアプリは、デバッグ以外の bundle id、空でない Sparkle feed
    URL、およびそのリリースバージョンに対する正規の Sparkle build floor 以上の `CFBundleVersion` を維持する必要があります

## NPM ワークフロー入力

`OpenClaw NPM Release` は、以下の運用者制御入力を受け付けます。

- `tag`: 必須のリリースタグ。例: `v2026.4.2`、`v2026.4.2-1`、または
  `v2026.4.2-beta.1`。`preflight_only=true` の場合は、検証専用事前確認のために現在の完全な
  40 文字の `main` コミット SHA も使用できます
- `preflight_only`: 検証/ビルド/パッケージのみの場合は `true`、実際の公開経路の場合は `false`
- `preflight_run_id`: 実際の公開経路では必須です。これにより、ワークフローは成功した事前確認実行から準備済み tarball を再利用します
- `npm_dist_tag`: 公開経路の npm 対象タグ。デフォルトは `beta`
- `promote_beta_to_latest`: 公開をスキップし、すでに公開済みの
  stable `beta` ビルドを `latest` に移動する場合は `true`
- `sync_stable_dist_tags`: 公開をスキップし、すでに公開済みの stable バージョンに `latest` と
  `beta` の両方を向ける場合は `true`

`OpenClaw Release Checks` は、以下の運用者制御入力を受け付けます。

- `ref`: 検証する既存のリリースタグ、または現在の完全な 40 文字の `main` コミット
  SHA

ルール:

- stable および修正タグは `beta` または `latest` のどちらにも公開できます
- beta プレリリースタグは `beta` にのみ公開できます
- 完全なコミット SHA 入力は `preflight_only=true` の場合にのみ許可されます
- リリースチェックのコミット SHA モードでも、現在の `origin/main` HEAD が必要です
- 実際の公開経路では、事前確認時に使用したものと同じ `npm_dist_tag` を使用する必要があります。
  ワークフローは公開を続行する前にそのメタデータを検証します
- 昇格モードでは、stable または修正タグ、`preflight_only=false`、
  空の `preflight_run_id`、および `npm_dist_tag=beta` を使用する必要があります
- dist-tag 同期モードでは、stable または修正タグ、
  `preflight_only=false`、空の `preflight_run_id`、`npm_dist_tag=latest`、
  および `promote_beta_to_latest=false` を使用する必要があります
- 昇格モードおよび dist-tag 同期モードでも、有効な `NPM_TOKEN` が必要です。これは
  `npm dist-tag add` に通常の npm 認証が依然として必要であり、信頼済み公開は
  パッケージ公開経路のみをカバーするためです

## stable npm リリース手順

stable npm リリースを行うときは、次の手順に従います。

1. `preflight_only=true` で `OpenClaw NPM Release` を実行します
   - タグがまだ存在しない場合は、
     事前確認ワークフローの検証専用ドライランとして現在の完全な `main` コミット SHA を使用できます
2. 通常の beta-first フローでは `npm_dist_tag=beta` を選択し、
   意図的に stable を直接公開したい場合にのみ `latest` を選択します
3. ライブ prompt cache カバレッジが必要な場合は、同じタグまたは
   現在の完全な `main` コミット SHA を指定して `OpenClaw Release Checks` を別途実行します
   - これは意図的な分離です。これにより、長時間実行または不安定なチェックを公開ワークフローに再結合することなく、
     ライブカバレッジを利用可能なまま維持できます
4. 成功した `preflight_run_id` を保存します
5. `preflight_only=false`、同じ
   `tag`、同じ `npm_dist_tag`、および保存した `preflight_run_id` を指定して、再度 `OpenClaw NPM Release` を実行します
6. リリースが `beta` に公開された場合は、その
   公開済みビルドを `latest` に移動したいタイミングで、同じ stable `tag`、
   `promote_beta_to_latest=true`、`preflight_only=false`、
   空の `preflight_run_id`、および `npm_dist_tag=beta` を指定して後で `OpenClaw NPM Release` を実行します
7. リリースが意図的に `latest` に直接公開され、`beta`
   も同じ stable ビルドを指すべき場合は、同じ
   stable `tag`、`sync_stable_dist_tags=true`、`promote_beta_to_latest=false`、
   `preflight_only=false`、空の `preflight_run_id`、および `npm_dist_tag=latest` を指定して `OpenClaw NPM Release` を実行します

昇格モードおよび dist-tag 同期モードでも、`npm-release`
環境の承認と、そのワークフロー実行からアクセス可能な有効な `NPM_TOKEN` が引き続き必要です。

これにより、直接公開経路と beta-first 昇格経路の両方が
文書化され、運用者に見える形で維持されます。

## 公開リファレンス

- [`.github/workflows/openclaw-npm-release.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-npm-release.yml)
- [`.github/workflows/openclaw-release-checks.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-release-checks.yml)
- [`scripts/openclaw-npm-release-check.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/openclaw-npm-release-check.ts)
- [`scripts/package-mac-dist.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-dist.sh)
- [`scripts/make_appcast.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/make_appcast.sh)

maintainer は、実際のランブックについて
[`openclaw/maintainers/release/README.md`](https://github.com/openclaw/maintainers/blob/main/release/README.md)
にある private のリリースドキュメントを使用します。
