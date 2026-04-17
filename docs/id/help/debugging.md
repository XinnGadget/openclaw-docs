---
read_when:
    - Anda perlu memeriksa output model mentah untuk kebocoran penalaran
    - Anda ingin menjalankan Gateway dalam mode watch saat melakukan iterasi
    - Anda memerlukan alur kerja debugging yang dapat diulang
summary: 'Alat debugging: mode watch, stream model mentah, dan pelacakan kebocoran penalaran'
title: Debugging
x-i18n:
    generated_at: "2026-04-12T23:28:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: bc31ce9b41e92a14c4309f32df569b7050b18024f83280930e53714d3bfcd5cc
    source_path: help/debugging.md
    workflow: 15
---

# Debugging

Halaman ini membahas helper debugging untuk output streaming, terutama ketika sebuah provider mencampurkan penalaran ke dalam teks normal.

## Override debug runtime

Gunakan `/debug` di chat untuk menetapkan override config **hanya-runtime** (memori, bukan disk).
`/debug` dinonaktifkan secara default; aktifkan dengan `commands.debug: true`.
Ini berguna ketika Anda perlu mengubah pengaturan yang jarang digunakan tanpa mengedit `openclaw.json`.

Contoh:

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug unset messages.responsePrefix
/debug reset
```

`/debug reset` menghapus semua override dan kembali ke config di disk.

## Output trace sesi

Gunakan `/trace` saat Anda ingin melihat baris trace/debug milik Plugin dalam satu sesi
tanpa menyalakan mode verbose penuh.

Contoh:

```text
/trace
/trace on
/trace off
```

Gunakan `/trace` untuk diagnostik Plugin seperti ringkasan debug Active Memory.
Tetap gunakan `/verbose` untuk output status/tool verbose normal, dan tetap gunakan
`/debug` untuk override config hanya-runtime.

## Mode watch Gateway

Untuk iterasi cepat, jalankan gateway di bawah file watcher:

```bash
pnpm gateway:watch
```

Ini dipetakan ke:

```bash
node scripts/watch-node.mjs gateway --force
```

Watcher akan memulai ulang pada file yang relevan dengan build di bawah `src/`, file source extension,
metadata extension `package.json` dan `openclaw.plugin.json`, `tsconfig.json`,
`package.json`, dan `tsdown.config.ts`. Perubahan metadata extension memulai ulang
gateway tanpa memaksa rebuild `tsdown`; perubahan source dan config tetap
membangun ulang `dist` terlebih dahulu.

Tambahkan flag CLI gateway apa pun setelah `gateway:watch` dan flag tersebut akan diteruskan pada
setiap restart. Menjalankan ulang perintah watch yang sama untuk repo/kumpulan flag yang sama sekarang
menggantikan watcher lama alih-alih meninggalkan parent watcher duplikat.

## Profil dev + gateway dev (`--dev`)

Gunakan profil dev untuk mengisolasi state dan menyiapkan lingkungan yang aman serta sementara untuk
debugging. Ada **dua** flag `--dev`:

- **`--dev` global (profil):** mengisolasi state di bawah `~/.openclaw-dev` dan
  secara default menetapkan port gateway ke `19001` (port turunan bergeser mengikutinya).
- **`gateway --dev`: memberi tahu Gateway untuk otomatis membuat config default +
  workspace** saat belum ada (dan melewati `BOOTSTRAP.md`).

Alur yang direkomendasikan (profil dev + bootstrap dev):

```bash
pnpm gateway:dev
OPENCLAW_PROFILE=dev openclaw tui
```

Jika Anda belum memiliki instalasi global, jalankan CLI melalui `pnpm openclaw ...`.

Yang dilakukan ini:

1. **Isolasi profil** (`--dev` global)
   - `OPENCLAW_PROFILE=dev`
   - `OPENCLAW_STATE_DIR=~/.openclaw-dev`
   - `OPENCLAW_CONFIG_PATH=~/.openclaw-dev/openclaw.json`
   - `OPENCLAW_GATEWAY_PORT=19001` (browser/canvas ikut bergeser)

2. **Bootstrap dev** (`gateway --dev`)
   - Menulis config minimal jika belum ada (`gateway.mode=local`, bind loopback).
   - Menetapkan `agent.workspace` ke workspace dev.
   - Menetapkan `agent.skipBootstrap=true` (tanpa `BOOTSTRAP.md`).
   - Mengisi file workspace jika belum ada:
     `AGENTS.md`, `SOUL.md`, `TOOLS.md`, `IDENTITY.md`, `USER.md`, `HEARTBEAT.md`.
   - Identitas default: **C3‑PO** (droid protokol).
   - Melewati provider channel dalam mode dev (`OPENCLAW_SKIP_CHANNELS=1`).

Alur reset (mulai baru):

```bash
pnpm gateway:dev:reset
```

Catatan: `--dev` adalah flag profil **global** dan bisa dikonsumsi oleh beberapa runner.
Jika Anda perlu menuliskannya secara eksplisit, gunakan bentuk env var:

```bash
OPENCLAW_PROFILE=dev openclaw gateway --dev --reset
```

`--reset` menghapus config, kredensial, sesi, dan workspace dev (menggunakan
`trash`, bukan `rm`), lalu membuat ulang penyiapan dev default.

Tip: jika gateway non-dev sudah berjalan (launchd/systemd), hentikan terlebih dahulu:

```bash
openclaw gateway stop
```

## Logging stream mentah (OpenClaw)

OpenClaw dapat mencatat **stream assistant mentah** sebelum pemfilteran/pemformatan apa pun.
Ini adalah cara terbaik untuk melihat apakah penalaran tiba sebagai delta teks biasa
(atau sebagai blok thinking terpisah).

Aktifkan melalui CLI:

```bash
pnpm gateway:watch --raw-stream
```

Override path opsional:

```bash
pnpm gateway:watch --raw-stream --raw-stream-path ~/.openclaw/logs/raw-stream.jsonl
```

Env var yang setara:

```bash
OPENCLAW_RAW_STREAM=1
OPENCLAW_RAW_STREAM_PATH=~/.openclaw/logs/raw-stream.jsonl
```

File default:

`~/.openclaw/logs/raw-stream.jsonl`

## Logging chunk mentah (pi-mono)

Untuk menangkap **chunk OpenAI-compat mentah** sebelum diurai menjadi blok,
pi-mono menyediakan logger terpisah:

```bash
PI_RAW_STREAM=1
```

Path opsional:

```bash
PI_RAW_STREAM_PATH=~/.pi-mono/logs/raw-openai-completions.jsonl
```

File default:

`~/.pi-mono/logs/raw-openai-completions.jsonl`

> Catatan: ini hanya dihasilkan oleh proses yang menggunakan provider
> `openai-completions` milik pi-mono.

## Catatan keamanan

- Log stream mentah dapat mencakup prompt lengkap, output tool, dan data pengguna.
- Simpan log secara lokal dan hapus setelah debugging.
- Jika Anda membagikan log, bersihkan secret dan PII terlebih dahulu.
