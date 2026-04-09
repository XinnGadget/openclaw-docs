---
read_when:
    - Anda perlu memahami mengapa sebuah job CI berjalan atau tidak berjalan
    - Anda sedang men-debug pemeriksaan GitHub Actions yang gagal
summary: Graf job CI, gerbang cakupan, dan padanan perintah lokal
title: Pipeline CI
x-i18n:
    generated_at: "2026-04-09T09:13:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: d104f2510fadd674d7952aa08ad73e10f685afebea8d7f19adc1d428e2bdc908
    source_path: ci.md
    workflow: 15
---

# Pipeline CI

CI berjalan pada setiap push ke `main` dan setiap pull request. CI menggunakan cakupan cerdas untuk melewati job mahal ketika hanya area yang tidak terkait yang berubah.

## Ikhtisar Job

| Job                      | Tujuan                                                                                   | Kapan berjalan                      |
| ------------------------ | ---------------------------------------------------------------------------------------- | ----------------------------------- |
| `preflight`              | Mendeteksi perubahan khusus docs, cakupan yang berubah, ekstensi yang berubah, dan membangun manifes CI | Selalu pada push dan PR non-draf    |
| `security-fast`          | Deteksi kunci privat, audit workflow melalui `zizmor`, audit dependensi produksi         | Selalu pada push dan PR non-draf    |
| `build-artifacts`        | Membangun `dist/` dan Control UI sekali, mengunggah artefak yang dapat digunakan ulang untuk job downstream | Perubahan yang relevan dengan Node  |
| `checks-fast-core`       | Lane kebenaran Linux cepat seperti pemeriksaan bundled/plugin-contract/protocol          | Perubahan yang relevan dengan Node  |
| `checks-fast-extensions` | Mengagregasikan lane shard ekstensi setelah `checks-fast-extensions-shard` selesai      | Perubahan yang relevan dengan Node  |
| `extension-fast`         | Pengujian terfokus hanya untuk plugin bawaan yang berubah                                | Saat perubahan ekstensi terdeteksi  |
| `check`                  | Gerbang lokal utama di CI: `pnpm check` plus `pnpm build:strict-smoke`                  | Perubahan yang relevan dengan Node  |
| `check-additional`       | Penjaga arsitektur, boundary, import-cycle plus harness regresi watch gateway           | Perubahan yang relevan dengan Node  |
| `build-smoke`            | Pengujian smoke CLI hasil build dan smoke memori saat startup                            | Perubahan yang relevan dengan Node  |
| `checks`                 | Lane Node Linux yang lebih berat: pengujian penuh, pengujian channel, dan kompatibilitas Node 22 khusus push | Perubahan yang relevan dengan Node  |
| `check-docs`             | Pemeriksaan format, lint, dan tautan rusak docs                                          | Docs berubah                        |
| `skills-python`          | Ruff + pytest untuk Skills berbasis Python                                               | Perubahan yang relevan dengan Skills Python |
| `checks-windows`         | Lane pengujian khusus Windows                                                            | Perubahan yang relevan dengan Windows |
| `macos-node`             | Lane pengujian TypeScript macOS menggunakan artefak build bersama                        | Perubahan yang relevan dengan macOS |
| `macos-swift`            | Lint, build, dan pengujian Swift untuk aplikasi macOS                                    | Perubahan yang relevan dengan macOS |
| `android`                | Matriks build dan pengujian Android                                                      | Perubahan yang relevan dengan Android |

## Urutan Gagal-Cepat

Job diurutkan agar pemeriksaan murah gagal sebelum yang mahal berjalan:

1. `preflight` menentukan lane mana yang ada sama sekali. Logika `docs-scope` dan `changed-scope` adalah langkah di dalam job ini, bukan job terpisah.
2. `security-fast`, `check`, `check-additional`, `check-docs`, dan `skills-python` gagal cepat tanpa menunggu job artefak dan matriks platform yang lebih berat.
3. `build-artifacts` berjalan tumpang tindih dengan lane Linux cepat agar konsumen downstream bisa mulai segera setelah build bersama siap.
4. Setelah itu, lane platform dan runtime yang lebih berat bercabang keluar: `checks-fast-core`, `checks-fast-extensions`, `extension-fast`, `checks`, `checks-windows`, `macos-node`, `macos-swift`, dan `android`.

Logika cakupan berada di `scripts/ci-changed-scope.mjs` dan dicakup oleh unit test di `src/scripts/ci-changed-scope.test.ts`.
Workflow `install-smoke` yang terpisah menggunakan ulang skrip cakupan yang sama melalui job `preflight` miliknya sendiri. Workflow ini menghitung `run_install_smoke` dari sinyal changed-smoke yang lebih sempit, sehingga smoke Docker/install hanya berjalan untuk perubahan yang relevan dengan instalasi, packaging, dan container.

Pada push, matriks `checks` menambahkan lane `compat-node22` yang khusus push. Pada pull request, lane itu dilewati dan matriks tetap berfokus pada lane pengujian/channel normal.

## Runner

| Runner                           | Job                                                                                                  |
| -------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `blacksmith-16vcpu-ubuntu-2404`  | `preflight`, `security-fast`, `build-artifacts`, pemeriksaan Linux, pemeriksaan docs, Skills Python, `android` |
| `blacksmith-32vcpu-windows-2025` | `checks-windows`                                                                                     |
| `macos-latest`                   | `macos-node`, `macos-swift`                                                                          |

## Padanan Lokal

```bash
pnpm check          # types + lint + format
pnpm build:strict-smoke
pnpm check:import-cycles
pnpm test:gateway:watch-regression
pnpm test           # vitest tests
pnpm test:channels
pnpm check:docs     # format docs + lint + broken links
pnpm build          # build dist saat lane artefak/build-smoke CI relevan
```
