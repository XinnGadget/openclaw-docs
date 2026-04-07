---
read_when:
    - Testleri çalıştırırken veya düzeltirken
summary: Testlerin yerelde nasıl çalıştırılacağı (vitest) ve force/coverage modlarının ne zaman kullanılacağı
title: Testler
x-i18n:
    generated_at: "2026-04-07T08:49:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: f7c19390f7577b3a29796c67514c96fe4c86c9fa0c7686cd4e377c6e31dcd085
    source_path: reference/test.md
    workflow: 15
---

# Testler

- Tam test kiti (suite'ler, canlı, Docker): [Testing](/tr/help/testing)

- `pnpm test:force`: Varsayılan kontrol portunu tutan kalıcı bir gateway sürecini sonlandırır, ardından tam Vitest paketini yalıtılmış bir gateway portuyla çalıştırır; böylece sunucu testleri çalışan bir örnekle çakışmaz. Önceki bir gateway çalıştırması 18789 portunu dolu bıraktığında bunu kullanın.
- `pnpm test:coverage`: Birim paketini V8 coverage ile çalıştırır (`vitest.unit.config.ts` üzerinden). Genel eşikler satırlar/dallar/fonksiyonlar/ifadeler için %70'tir. Coverage, hedefi birim test edilebilir mantığa odaklı tutmak için entegrasyon ağırlıklı entrypoint'leri (CLI bağlantıları, gateway/telegram köprüleri, webchat statik sunucusu) hariç tutar.
- `pnpm test:coverage:changed`: Yalnızca `origin/main` sonrasında değişen dosyalar için birim coverage çalıştırır.
- `pnpm test:changed`: Diff yalnızca yönlendirilebilir kaynak/test dosyalarına dokunduğunda değişen git yollarını kapsamlı Vitest lane'lerine genişletir. Config/setup değişiklikleri yine yerel kök proje çalıştırmasına geri döner; böylece bağlantı düzenlemeleri gerektiğinde daha geniş yeniden çalıştırılır.
- `pnpm test`: Açık dosya/dizin hedeflerini kapsamlı Vitest lane'leri üzerinden yönlendirir. Hedef verilmemiş çalıştırmalar artık tek dev bir root-project süreci yerine art arda on bir shard config çalıştırır (`vitest.full-core-unit-src.config.ts`, `vitest.full-core-unit-security.config.ts`, `vitest.full-core-unit-ui.config.ts`, `vitest.full-core-unit-support.config.ts`, `vitest.full-core-support-boundary.config.ts`, `vitest.full-core-contracts.config.ts`, `vitest.full-core-bundled.config.ts`, `vitest.full-core-runtime.config.ts`, `vitest.full-agentic.config.ts`, `vitest.full-auto-reply.config.ts`, `vitest.full-extensions.config.ts`).
- Seçili `plugin-sdk` ve `commands` test dosyaları artık yalnızca `test/setup.ts` dosyasını koruyan özel hafif lane'ler üzerinden yönlendirilir; çalışma zamanı ağırlıklı durumlar mevcut lane'lerinde kalır.
- Seçili `plugin-sdk` ve `commands` yardımcı kaynak dosyaları da `pnpm test:changed` için bu hafif lane'lerde açık kardeş testlere eşlenir; böylece küçük yardımcı düzenlemeleri ağır çalışma zamanı destekli suite'leri yeniden çalıştırmaz.
- `auto-reply` artık ayrıca üç özel config'e bölünür (`core`, `top-level`, `reply`); böylece yanıt harness'i daha hafif üst düzey durum/token/helper testlerine baskın gelmez.
- Temel Vitest config'i artık varsayılan olarak `pool: "threads"` ve `isolate: false` kullanır; paylaşılan yalıtımsız çalıştırıcı depo config'leri genelinde etkinleştirilmiştir.
- `pnpm test:channels`, `vitest.channels.config.ts` çalıştırır.
- `pnpm test:extensions`, `vitest.extensions.config.ts` çalıştırır.
- `pnpm test:extensions`: uzantı/plugin suite'lerini çalıştırır.
- `pnpm test:perf:imports`: Açık dosya/dizin hedefleri için yine kapsamlı lane yönlendirmesi kullanırken Vitest import süresi + import dökümü raporlamasını etkinleştirir.
- `pnpm test:perf:imports:changed`: Aynı import profillemesi, ancak yalnızca `origin/main` sonrasında değişen dosyalar için.
- `pnpm test:perf:changed:bench -- --ref <git-ref>`: Yönlendirilmiş changed-mode yolunu aynı commit edilmiş git diff'i için yerel root-project çalıştırmasıyla karşılaştırmalı ölçer.
- `pnpm test:perf:changed:bench -- --worktree`: Önce commit etmeden geçerli worktree değişiklik kümesini karşılaştırmalı ölçer.
- `pnpm test:perf:profile:main`: Vitest ana iş parçacığı için bir CPU profili yazar (`.artifacts/vitest-main-profile`).
- `pnpm test:perf:profile:runner`: Birim çalıştırıcı için CPU + heap profilleri yazar (`.artifacts/vitest-runner-profile`).
- Gateway entegrasyonu: `OPENCLAW_TEST_INCLUDE_GATEWAY=1 pnpm test` veya `pnpm test:gateway` ile isteğe bağlı olarak etkinleştirilir.
- `pnpm test:e2e`: Gateway uçtan uca smoke testlerini çalıştırır (çoklu örnek WS/HTTP/node eşleştirmesi). Varsayılan olarak `vitest.e2e.config.ts` içinde uyarlanabilir worker'larla `threads` + `isolate: false` kullanır; `OPENCLAW_E2E_WORKERS=<n>` ile ayarlayın ve ayrıntılı loglar için `OPENCLAW_E2E_VERBOSE=1` kullanın.
- `pnpm test:live`: Sağlayıcı canlı testlerini çalıştırır (minimax/zai). API anahtarları ve atlamayı kaldırmak için `LIVE=1` (veya sağlayıcıya özgü `*_LIVE_TEST=1`) gerekir.
- `pnpm test:docker:openwebui`: Docker içinde OpenClaw + Open WebUI başlatır, Open WebUI üzerinden oturum açar, `/api/models` yolunu kontrol eder, ardından `/api/chat/completions` üzerinden gerçek bir proxy'lenmiş sohbet çalıştırır. Kullanılabilir bir canlı model anahtarı gerektirir (örneğin `~/.profile` içindeki OpenAI), harici bir Open WebUI image'ı çeker ve normal birim/e2e suite'leri gibi CI-kararlı olması beklenmez.
- `pnpm test:docker:mcp-channels`: Önceden seed edilmiş bir Gateway container'ı ve `openclaw mcp serve` başlatan ikinci bir istemci container'ı başlatır; ardından gerçek stdio köprüsü üzerinden yönlendirilmiş konuşma keşfini, transcript okumalarını, ek meta verilerini, canlı olay kuyruğu davranışını, giden gönderim yönlendirmesini ve Claude tarzı kanal + izin bildirimlerini doğrular. Claude bildirim doğrulaması, smoke test'in köprünün gerçekten ne yaydığını yansıtması için ham stdio MCP frame'lerini doğrudan okur.

## Yerel PR kapısı

Yerel PR gönderme/kapı kontrolleri için şunları çalıştırın:

- `pnpm check`
- `pnpm build`
- `pnpm test`
- `pnpm check:docs`

`pnpm test`, yük altında bir host üzerinde dalgalanırsa, bunu gerileme kabul etmeden önce bir kez yeniden çalıştırın, ardından `pnpm test <path/to/test>` ile izole edin. Belleği kısıtlı host'lar için şunları kullanın:

- `OPENCLAW_VITEST_MAX_WORKERS=1 pnpm test`
- `OPENCLAW_VITEST_FS_MODULE_CACHE_PATH=/tmp/openclaw-vitest-cache pnpm test:changed`

## Model gecikme kıyaslaması (yerel anahtarlar)

Betik: [`scripts/bench-model.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/bench-model.ts)

Kullanım:

- `source ~/.profile && pnpm tsx scripts/bench-model.ts --runs 10`
- İsteğe bağlı env: `MINIMAX_API_KEY`, `MINIMAX_BASE_URL`, `MINIMAX_MODEL`, `ANTHROPIC_API_KEY`
- Varsayılan prompt: “Reply with a single word: ok. No punctuation or extra text.”

Son çalıştırma (2025-12-31, 20 çalıştırma):

- minimax medyan 1279ms (min 1114, maks 2431)
- opus medyan 2454ms (min 1224, maks 3170)

## CLI başlangıç kıyaslaması

Betik: [`scripts/bench-cli-startup.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/bench-cli-startup.ts)

Kullanım:

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

Hazır ayarlar:

- `startup`: `--version`, `--help`, `health`, `health --json`, `status --json`, `status`
- `real`: `health`, `status`, `status --json`, `sessions`, `sessions --json`, `agents list --json`, `gateway status`, `gateway status --json`, `gateway health --json`, `config get gateway.port`
- `all`: her iki hazır ayar

Çıktı, her komut için `sampleCount`, avg, p50, p95, min/maks, exit-code/signal dağılımı ve maks RSS özetlerini içerir. İsteğe bağlı `--cpu-prof-dir` / `--heap-prof-dir`, zamanlama ve profil yakalamanın aynı harness'i kullanması için çalıştırma başına V8 profilleri yazar.

Kaydedilen çıktı kuralları:

- `pnpm test:startup:bench:smoke`, hedeflenen smoke artefact'ını `.artifacts/cli-startup-bench-smoke.json` içine yazar
- `pnpm test:startup:bench:save`, `runs=5` ve `warmup=1` kullanarak tam suite artefact'ını `.artifacts/cli-startup-bench-all.json` içine yazar
- `pnpm test:startup:bench:update`, `runs=5` ve `warmup=1` kullanarak depoya kaydedilmiş temel fixture'ı `test/fixtures/cli-startup-bench.json` içinde yeniler

Depoya kaydedilmiş fixture:

- `test/fixtures/cli-startup-bench.json`
- `pnpm test:startup:bench:update` ile yenileyin
- Geçerli sonuçları fixture ile `pnpm test:startup:bench:check` kullanarak karşılaştırın

## Onboarding E2E (Docker)

Docker isteğe bağlıdır; buna yalnızca container içinde onboarding smoke testleri için ihtiyaç vardır.

Temiz bir Linux container'ı içinde tam soğuk başlangıç akışı:

```bash
scripts/e2e/onboard-docker.sh
```

Bu betik, etkileşimli sihirbazı bir pseudo-tty üzerinden sürer, config/workspace/session dosyalarını doğrular, ardından gateway'i başlatır ve `openclaw health` çalıştırır.

## QR import smoke (Docker)

`qrcode-terminal` bileşeninin desteklenen Docker Node çalışma zamanlarında yüklendiğini doğrular (Node 24 varsayılan, Node 22 uyumlu):

```bash
pnpm test:docker:qr
```
