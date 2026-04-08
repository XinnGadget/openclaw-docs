---
x-i18n:
    generated_at: "2026-04-08T06:01:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4a9066b2a939c5a9ba69141d75405f0e8097997b523164340e2f0e9a0d5060dd
    source_path: refactor/qa.md
    workflow: 15
---

# Refaktor QA

Status: migrasi fondasional telah diterapkan.

## Tujuan

Memindahkan QA OpenClaw dari model definisi terpisah ke satu sumber kebenaran:

- metadata skenario
- prompt yang dikirim ke model
- setup dan teardown
- logika harness
- asersi dan kriteria keberhasilan
- artefak dan petunjuk laporan

Keadaan akhir yang diinginkan adalah harness QA generik yang memuat file definisi skenario yang kuat alih-alih meng-hardcode sebagian besar perilaku di TypeScript.

## Status Saat Ini

Sumber kebenaran utama sekarang berada di `qa/scenarios/index.md` ditambah satu file per
skenario di bawah `qa/scenarios/*.md`.

Yang sudah diterapkan:

- `qa/scenarios/index.md`
  - metadata paket QA kanonis
  - identitas operator
  - misi awal
- `qa/scenarios/*.md`
  - satu file markdown per skenario
  - metadata skenario
  - binding handler
  - konfigurasi eksekusi spesifik skenario
- `extensions/qa-lab/src/scenario-catalog.ts`
  - parser paket markdown + validasi zod
- `extensions/qa-lab/src/qa-agent-bootstrap.ts`
  - rendering rencana dari paket markdown
- `extensions/qa-lab/src/qa-agent-workspace.ts`
  - seed file kompatibilitas yang dihasilkan plus `QA_SCENARIOS.md`
- `extensions/qa-lab/src/suite.ts`
  - memilih skenario yang dapat dieksekusi melalui binding handler yang didefinisikan di markdown
- protokol bus QA + UI
  - lampiran inline generik untuk rendering gambar/video/audio/file

Permukaan terpisah yang masih tersisa:

- `extensions/qa-lab/src/suite.ts`
  - masih memiliki sebagian besar logika handler kustom yang dapat dieksekusi
- `extensions/qa-lab/src/report.ts`
  - masih menurunkan struktur laporan dari output runtime

Jadi pembagian sumber kebenaran sudah diperbaiki, tetapi eksekusi masih sebagian besar didukung handler, bukan sepenuhnya deklaratif.

## Seperti Apa Permukaan Skenario Nyata

Membaca suite saat ini menunjukkan beberapa kelas skenario yang berbeda.

### Interaksi sederhana

- baseline channel
- baseline DM
- tindak lanjut ber-thread
- pergantian model
- tindak lanjut persetujuan
- reaksi/edit/hapus

### Mutasi konfigurasi dan runtime

- penonaktifan skill lewat patch config
- apply config restart wake-up
- pembalikan kapabilitas saat restart config
- pemeriksaan drift inventaris runtime

### Asersi filesystem dan repo

- laporan penemuan source/dokumen
- build Lobster Invaders
- pencarian artefak gambar yang dihasilkan

### Orkestrasi memori

- pemanggilan memori
- tool memori dalam konteks channel
- fallback kegagalan memori
- peringkat memori sesi
- isolasi memori thread
- memory dreaming sweep

### Integrasi tool dan plugin

- panggilan plugin-tools MCP
- visibilitas skill
- hot install skill
- pembuatan gambar native
- image roundtrip
- pemahaman gambar dari lampiran

### Multi-turn dan multi-aktor

- handoff subagen
- sintesis fanout subagen
- alur bergaya pemulihan setelah restart

Kategori-kategori ini penting karena mendorong kebutuhan DSL. Daftar datar berisi prompt + teks yang diharapkan saja tidak cukup.

## Arah

### Satu sumber kebenaran

Gunakan `qa/scenarios/index.md` ditambah `qa/scenarios/*.md` sebagai sumber kebenaran yang ditulis.

Paket harus tetap:

- mudah dibaca manusia dalam review
- dapat di-parse mesin
- cukup kaya untuk mendorong:
  - eksekusi suite
  - bootstrap workspace QA
  - metadata UI QA Lab
  - prompt docs/discovery
  - pembuatan laporan

### Format penulisan yang disarankan

Gunakan markdown sebagai format tingkat atas, dengan YAML terstruktur di dalamnya.

Bentuk yang direkomendasikan:

- frontmatter YAML
  - id
  - title
  - surface
  - tags
  - referensi dokumen
  - referensi kode
  - override model/provider
  - prasyarat
- bagian prosa
  - objective
  - notes
  - debugging hints
- blok YAML berpagar
  - setup
  - steps
  - assertions
  - cleanup

Ini memberikan:

- keterbacaan PR yang lebih baik daripada JSON besar
- konteks yang lebih kaya daripada YAML murni
- parsing ketat dan validasi zod

JSON mentah dapat diterima hanya sebagai bentuk hasil generate antara.

## Bentuk File Skenario yang Diusulkan

Contoh:

````md
---
id: image-generation-roundtrip
title: Image generation roundtrip
surface: image
tags: [media, image, roundtrip]
models:
  primary: openai/gpt-5.4
requires:
  tools: [image_generate]
  plugins: [openai, qa-channel]
docsRefs:
  - docs/help/testing.md
  - docs/concepts/model-providers.md
codeRefs:
  - extensions/qa-lab/src/suite.ts
  - src/gateway/chat-attachments.ts
---

# Objective

Verify generated media is reattached on the follow-up turn.

# Setup

```yaml scenario.setup
- action: config.patch
  patch:
    agents:
      defaults:
        imageGenerationModel:
          primary: openai/gpt-image-1
- action: session.create
  key: agent:qa:image-roundtrip
```

# Steps

```yaml scenario.steps
- action: agent.send
  session: agent:qa:image-roundtrip
  message: |
    Image generation check: generate a QA lighthouse image and summarize it in one short sentence.
- action: artifact.capture
  kind: generated-image
  promptSnippet: Image generation check
  saveAs: lighthouseImage
- action: agent.send
  session: agent:qa:image-roundtrip
  message: |
    Roundtrip image inspection check: describe the generated lighthouse attachment in one short sentence.
  attachments:
    - fromArtifact: lighthouseImage
```

# Expect

```yaml scenario.expect
- assert: outbound.textIncludes
  value: lighthouse
- assert: requestLog.matches
  where:
    promptIncludes: Roundtrip image inspection check
  imageInputCountGte: 1
- assert: artifact.exists
  ref: lighthouseImage
```
````

## Kemampuan Runner yang Harus Dicakup DSL

Berdasarkan suite saat ini, runner generik memerlukan lebih dari sekadar eksekusi prompt.

### Tindakan environment dan setup

- `bus.reset`
- `gateway.waitHealthy`
- `channel.waitReady`
- `session.create`
- `thread.create`
- `workspace.writeSkill`

### Tindakan giliran agen

- `agent.send`
- `agent.wait`
- `bus.injectInbound`
- `bus.injectOutbound`

### Tindakan konfigurasi dan runtime

- `config.get`
- `config.patch`
- `config.apply`
- `gateway.restart`
- `tools.effective`
- `skills.status`

### Tindakan file dan artefak

- `file.write`
- `file.read`
- `file.delete`
- `file.touchTime`
- `artifact.captureGeneratedImage`
- `artifact.capturePath`

### Tindakan memori dan cron

- `memory.indexForce`
- `memory.searchCli`
- `doctor.memory.status`
- `cron.list`
- `cron.run`
- `cron.waitCompletion`
- `sessionTranscript.write`

### Tindakan MCP

- `mcp.callTool`

### Asersi

- `outbound.textIncludes`
- `outbound.inThread`
- `outbound.notInRoot`
- `tool.called`
- `tool.notPresent`
- `skill.visible`
- `skill.disabled`
- `file.contains`
- `memory.contains`
- `requestLog.matches`
- `sessionStore.matches`
- `cron.managedPresent`
- `artifact.exists`

## Variabel dan Referensi Artefak

DSL harus mendukung output yang disimpan dan referensi berikutnya.

Contoh dari suite saat ini:

- membuat thread, lalu menggunakan ulang `threadId`
- membuat sesi, lalu menggunakan ulang `sessionKey`
- menghasilkan gambar, lalu melampirkan file pada giliran berikutnya
- menghasilkan string penanda wake, lalu mengasertikan bahwa string itu muncul nanti

Kemampuan yang dibutuhkan:

- `saveAs`
- `${vars.name}`
- `${artifacts.name}`
- referensi bertipe untuk path, kunci sesi, id thread, penanda, output tool

Tanpa dukungan variabel, harness akan terus membocorkan logika skenario kembali ke TypeScript.

## Apa yang Harus Tetap Menjadi Escape Hatch

Runner deklaratif yang sepenuhnya murni tidak realistis pada fase 1.

Beberapa skenario secara inheren berat pada orkestrasi:

- memory dreaming sweep
- config apply restart wake-up
- config restart capability flip
- resolusi artefak gambar yang dihasilkan berdasarkan timestamp/path
- evaluasi discovery-report

Untuk saat ini, ini sebaiknya menggunakan handler kustom eksplisit.

Aturan yang direkomendasikan:

- 85-90% deklaratif
- langkah `customHandler` eksplisit untuk sisa yang sulit
- hanya handler kustom bernama dan terdokumentasi
- tidak ada kode inline anonim di file skenario

Itu menjaga engine generik tetap bersih sambil tetap memungkinkan kemajuan.

## Perubahan Arsitektur

### Saat Ini

Markdown skenario sudah menjadi sumber kebenaran untuk:

- eksekusi suite
- file bootstrap workspace
- katalog skenario UI QA Lab
- metadata laporan
- prompt discovery

Kompatibilitas yang dihasilkan:

- workspace seeded masih menyertakan `QA_KICKOFF_TASK.md`
- workspace seeded masih menyertakan `QA_SCENARIO_PLAN.md`
- workspace seeded sekarang juga menyertakan `QA_SCENARIOS.md`

## Rencana Refaktor

### Fase 1: loader dan skema

Selesai.

- menambahkan `qa/scenarios/index.md`
- memisahkan skenario ke `qa/scenarios/*.md`
- menambahkan parser untuk konten paket YAML markdown bernama
- memvalidasi dengan zod
- mengganti konsumen ke paket yang telah di-parse
- menghapus `qa/seed-scenarios.json` dan `qa/QA_KICKOFF_TASK.md` di tingkat repo

### Fase 2: engine generik

- memisahkan `extensions/qa-lab/src/suite.ts` menjadi:
  - loader
  - engine
  - registry tindakan
  - registry asersi
  - handler kustom
- mempertahankan fungsi helper yang ada sebagai operasi engine

Hasil kerja:

- engine mengeksekusi skenario deklaratif sederhana

Mulai dengan skenario yang sebagian besar berupa prompt + tunggu + asersi:

- tindak lanjut ber-thread
- pemahaman gambar dari lampiran
- visibilitas dan pemanggilan skill
- baseline channel

Hasil kerja:

- skenario pertama yang benar-benar didefinisikan dalam markdown dikirim melalui engine generik

### Fase 4: migrasikan skenario tingkat menengah

- image generation roundtrip
- tool memori dalam konteks channel
- peringkat memori sesi
- handoff subagen
- sintesis fanout subagen

Hasil kerja:

- variabel, artefak, asersi tool, dan asersi request-log terbukti berfungsi

### Fase 5: biarkan skenario sulit tetap memakai handler kustom

- memory dreaming sweep
- config apply restart wake-up
- config restart capability flip
- drift inventaris runtime

Hasil kerja:

- format penulisan yang sama, tetapi dengan blok langkah kustom eksplisit saat diperlukan

### Fase 6: hapus map skenario yang di-hardcode

Setelah cakupan paket cukup baik:

- hapus sebagian besar percabangan TypeScript spesifik skenario dari `extensions/qa-lab/src/suite.ts`

## Slack Palsu / Dukungan Media Kaya

Bus QA saat ini berfokus pada teks.

File yang relevan:

- `extensions/qa-channel/src/protocol.ts`
- `extensions/qa-lab/src/bus-state.ts`
- `extensions/qa-lab/src/bus-queries.ts`
- `extensions/qa-lab/src/bus-server.ts`
- `extensions/qa-lab/web/src/ui-render.ts`

Saat ini bus QA mendukung:

- teks
- reaksi
- thread

Bus ini belum memodelkan lampiran media inline.

### Kontrak transport yang dibutuhkan

Tambahkan model lampiran bus QA generik:

```ts
type QaBusAttachment = {
  id: string;
  kind: "image" | "video" | "audio" | "file";
  mimeType: string;
  fileName?: string;
  inline?: boolean;
  url?: string;
  contentBase64?: string;
  width?: number;
  height?: number;
  durationMs?: number;
  altText?: string;
  transcript?: string;
};
```

Lalu tambahkan `attachments?: QaBusAttachment[]` ke:

- `QaBusMessage`
- `QaBusInboundMessageInput`
- `QaBusOutboundMessageInput`

### Mengapa generik dulu

Jangan membangun model media khusus Slack.

Sebaliknya:

- satu model transport QA generik
- beberapa renderer di atasnya
  - chat QA Lab saat ini
  - fake Slack web di masa depan
  - tampilan transport palsu lainnya

Ini mencegah duplikasi logika dan memungkinkan skenario media tetap agnostik terhadap transport.

### Pekerjaan UI yang dibutuhkan

Perbarui UI QA untuk merender:

- pratinjau gambar inline
- pemutar audio inline
- pemutar video inline
- chip lampiran file

UI saat ini sudah dapat merender thread dan reaksi, jadi rendering lampiran seharusnya dapat dilapiskan ke model kartu pesan yang sama.

### Pekerjaan skenario yang dimungkinkan oleh transport media

Setelah lampiran mengalir melalui bus QA, kita dapat menambahkan skenario fake-chat yang lebih kaya:

- balasan gambar inline di fake Slack
- pemahaman lampiran audio
- pemahaman lampiran video
- pengurutan lampiran campuran
- balasan thread dengan media yang dipertahankan

## Rekomendasi

Bagian implementasi berikutnya sebaiknya adalah:

1. menambahkan loader skenario markdown + skema zod
2. menghasilkan katalog saat ini dari markdown
3. memigrasikan beberapa skenario sederhana terlebih dahulu
4. menambahkan dukungan lampiran bus QA generik
5. merender gambar inline di UI QA
6. lalu memperluas ke audio dan video

Ini adalah jalur terkecil yang membuktikan kedua tujuan:

- QA generik yang didefinisikan dengan markdown
- permukaan pesan palsu yang lebih kaya

## Pertanyaan Terbuka

- apakah file skenario sebaiknya mengizinkan templat prompt markdown tertanam dengan interpolasi variabel
- apakah setup/cleanup sebaiknya berupa bagian bernama atau hanya daftar tindakan berurutan
- apakah referensi artefak sebaiknya bertipe kuat di skema atau berbasis string
- apakah handler kustom sebaiknya berada dalam satu registry atau registry per permukaan
- apakah file kompatibilitas JSON yang dihasilkan sebaiknya tetap di-check-in selama migrasi
