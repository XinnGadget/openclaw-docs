---
read_when:
    - Menjelaskan cara kerja streaming atau chunking pada kanal
    - Mengubah perilaku streaming blok atau chunking kanal
    - Men-debug balasan blok duplikat/terlalu awal atau streaming pratinjau kanal
summary: Perilaku streaming + chunking (balasan blok, streaming pratinjau kanal, pemetaan mode)
title: Streaming dan Chunking
x-i18n:
    generated_at: "2026-04-08T06:01:04Z"
    model: gpt-5.4
    provider: openai
    source_hash: a8e847bb7da890818cd79dec7777f6ae488e6d6c0468e948e56b6b6c598e0000
    source_path: concepts/streaming.md
    workflow: 15
---

# Streaming + chunking

OpenClaw memiliki dua lapisan streaming yang terpisah:

- **Streaming blok (kanal):** mengirim **blok** yang sudah selesai saat asisten menulis. Ini adalah pesan kanal biasa (bukan delta token).
- **Streaming pratinjau (Telegram/Discord/Slack):** memperbarui **pesan pratinjau** sementara selama pembuatan.

Saat ini **tidak ada streaming delta-token yang sebenarnya** ke pesan kanal. Streaming pratinjau berbasis pesan (kirim + edit/tambahkan).

## Streaming blok (pesan kanal)

Streaming blok mengirim keluaran asisten dalam potongan kasar saat tersedia.

```
Model output
  └─ text_delta/events
       ├─ (blockStreamingBreak=text_end)
       │    └─ chunker emits blocks as buffer grows
       └─ (blockStreamingBreak=message_end)
            └─ chunker flushes at message_end
                   └─ channel send (block replies)
```

Legenda:

- `text_delta/events`: peristiwa stream model (bisa jarang untuk model non-streaming).
- `chunker`: `EmbeddedBlockChunker` yang menerapkan batas minimum/maksimum + preferensi pemisahan.
- `channel send`: pesan keluar aktual (balasan blok).

**Kontrol:**

- `agents.defaults.blockStreamingDefault`: `"on"`/`"off"` (default mati).
- Override kanal: `*.blockStreaming` (dan varian per akun) untuk memaksa `"on"`/`"off"` per kanal.
- `agents.defaults.blockStreamingBreak`: `"text_end"` atau `"message_end"`.
- `agents.defaults.blockStreamingChunk`: `{ minChars, maxChars, breakPreference? }`.
- `agents.defaults.blockStreamingCoalesce`: `{ minChars?, maxChars?, idleMs? }` (menggabungkan blok yang di-stream sebelum dikirim).
- Batas keras kanal: `*.textChunkLimit` (misalnya, `channels.whatsapp.textChunkLimit`).
- Mode chunk kanal: `*.chunkMode` (`length` default, `newline` membagi pada baris kosong (batas paragraf) sebelum chunking berdasarkan panjang).
- Batas lunak Discord: `channels.discord.maxLinesPerMessage` (default 17) membagi balasan tinggi untuk menghindari pemotongan UI.

**Semantik batas:**

- `text_end`: stream blok segera setelah chunker mengeluarkan hasil; flush pada setiap `text_end`.
- `message_end`: tunggu sampai pesan asisten selesai, lalu flush keluaran yang dibuffer.

`message_end` tetap menggunakan chunker jika teks yang dibuffer melebihi `maxChars`, sehingga dapat mengeluarkan beberapa chunk di akhir.

## Algoritma chunking (batas bawah/atas)

Chunking blok diimplementasikan oleh `EmbeddedBlockChunker`:

- **Batas bawah:** jangan keluarkan hasil sampai buffer >= `minChars` (kecuali dipaksa).
- **Batas atas:** utamakan pemisahan sebelum `maxChars`; jika dipaksa, pisahkan pada `maxChars`.
- **Preferensi pemisahan:** `paragraph` → `newline` → `sentence` → `whitespace` → pemisahan keras.
- **Code fence:** jangan pernah membagi di dalam fence; saat dipaksa pada `maxChars`, tutup + buka kembali fence agar Markdown tetap valid.

`maxChars` dibatasi ke `textChunkLimit` kanal, jadi Anda tidak bisa melebihi batas per kanal.

## Coalescing (menggabungkan blok yang di-stream)

Saat streaming blok diaktifkan, OpenClaw dapat **menggabungkan chunk blok berturut-turut**
sebelum mengirimkannya. Ini mengurangi “spam satu baris” sambil tetap menyediakan
keluaran progresif.

- Coalescing menunggu **jeda idle** (`idleMs`) sebelum flush.
- Buffer dibatasi oleh `maxChars` dan akan flush jika melampauinya.
- `minChars` mencegah fragmen kecil terkirim sampai cukup banyak teks terkumpul
  (flush akhir selalu mengirim teks yang tersisa).
- Joiner diturunkan dari `blockStreamingChunk.breakPreference`
  (`paragraph` → `\n\n`, `newline` → `\n`, `sentence` → spasi).
- Override kanal tersedia melalui `*.blockStreamingCoalesce` (termasuk konfigurasi per akun).
- Default coalesce `minChars` dinaikkan menjadi 1500 untuk Signal/Slack/Discord kecuali dioverride.

## Tempo seperti manusia antarblok

Saat streaming blok diaktifkan, Anda dapat menambahkan **jeda acak** di antara
balasan blok (setelah blok pertama). Ini membuat respons multi-gelembung terasa
lebih alami.

- Config: `agents.defaults.humanDelay` (override per agen melalui `agents.list[].humanDelay`).
- Mode: `off` (default), `natural` (800–2500ms), `custom` (`minMs`/`maxMs`).
- Hanya berlaku untuk **balasan blok**, bukan balasan akhir atau ringkasan tool.

## "Stream chunk atau semuanya"

Ini dipetakan ke:

- **Stream chunk:** `blockStreamingDefault: "on"` + `blockStreamingBreak: "text_end"` (kirim saat berjalan). Kanal non-Telegram juga memerlukan `*.blockStreaming: true`.
- **Stream semuanya di akhir:** `blockStreamingBreak: "message_end"` (flush sekali, mungkin beberapa chunk jika sangat panjang).
- **Tanpa streaming blok:** `blockStreamingDefault: "off"` (hanya balasan akhir).

**Catatan kanal:** Streaming blok **mati kecuali**
`*.blockStreaming` secara eksplisit disetel ke `true`. Kanal dapat menayangkan pratinjau langsung
(`channels.<channel>.streaming`) tanpa balasan blok.

Pengingat lokasi config: default `blockStreaming*` berada di bawah
`agents.defaults`, bukan config root.

## Mode streaming pratinjau

Kunci kanonis: `channels.<channel>.streaming`

Mode:

- `off`: nonaktifkan streaming pratinjau.
- `partial`: satu pratinjau yang diganti dengan teks terbaru.
- `block`: pembaruan pratinjau dalam langkah chunked/appended.
- `progress`: pratinjau progres/status selama pembuatan, jawaban akhir saat selesai.

### Pemetaan kanal

| Kanal    | `off` | `partial` | `block` | `progress`            |
| -------- | ----- | --------- | ------- | --------------------- |
| Telegram | ✅    | ✅        | ✅      | dipetakan ke `partial` |
| Discord  | ✅    | ✅        | ✅      | dipetakan ke `partial` |
| Slack    | ✅    | ✅        | ✅      | ✅                    |

Khusus Slack:

- `channels.slack.streaming.nativeTransport` mengaktifkan/nonaktifkan panggilan API streaming native Slack saat `channels.slack.streaming.mode="partial"` (default: `true`).
- Streaming native Slack dan status thread asisten Slack memerlukan target thread balasan; DM level atas tidak menampilkan pratinjau bergaya thread tersebut.

Migrasi kunci lama:

- Telegram: `streamMode` + boolean `streaming` dimigrasikan otomatis ke enum `streaming`.
- Discord: `streamMode` + boolean `streaming` dimigrasikan otomatis ke enum `streaming`.
- Slack: `streamMode` dimigrasikan otomatis ke `streaming.mode`; boolean `streaming` dimigrasikan otomatis ke `streaming.mode` plus `streaming.nativeTransport`; `nativeStreaming` lama dimigrasikan otomatis ke `streaming.nativeTransport`.

### Perilaku runtime

Telegram:

- Menggunakan pembaruan pratinjau `sendMessage` + `editMessageText` di DM dan grup/topik.
- Streaming pratinjau dilewati saat streaming blok Telegram diaktifkan secara eksplisit (untuk menghindari streaming ganda).
- `/reasoning stream` dapat menulis penalaran ke pratinjau.

Discord:

- Menggunakan pesan pratinjau kirim + edit.
- Mode `block` menggunakan draft chunking (`draftChunk`).
- Streaming pratinjau dilewati saat streaming blok Discord diaktifkan secara eksplisit.

Slack:

- `partial` dapat menggunakan streaming native Slack (`chat.startStream`/`append`/`stop`) saat tersedia.
- `block` menggunakan pratinjau draft bergaya append.
- `progress` menggunakan teks pratinjau status, lalu jawaban akhir.

## Terkait

- [Pesan](/id/concepts/messages) — siklus hidup dan pengiriman pesan
- [Coba lagi](/id/concepts/retry) — perilaku percobaan ulang saat pengiriman gagal
- [Kanal](/id/channels) — dukungan streaming per kanal
