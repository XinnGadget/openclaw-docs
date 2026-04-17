---
read_when:
    - Anda ingin memahami cara kerja memori
    - Anda ingin mengetahui file memori apa yang harus ditulis
summary: Bagaimana OpenClaw mengingat berbagai hal di seluruh sesi
title: Ikhtisar Memori
x-i18n:
    generated_at: "2026-04-15T14:40:32Z"
    model: gpt-5.4
    provider: openai
    source_hash: ad1adafe1d81f1703d24f48a9c9da2b25a0ebbd4aad4f65d8bde5df78195d55b
    source_path: concepts/memory.md
    workflow: 15
---

# Ikhtisar Memori

OpenClaw mengingat berbagai hal dengan menulis **file Markdown biasa** di workspace agen Anda. Model hanya "mengingat" apa yang disimpan ke disk -- tidak ada state tersembunyi.

## Cara kerjanya

Agen Anda memiliki tiga file yang terkait dengan memori:

- **`MEMORY.md`** -- memori jangka panjang. Fakta, preferensi, dan keputusan yang bertahan lama. Dimuat pada awal setiap sesi DM.
- **`memory/YYYY-MM-DD.md`** -- catatan harian. Konteks dan observasi yang berjalan. Catatan hari ini dan kemarin dimuat secara otomatis.
- **`DREAMS.md`** (opsional) -- Buku Harian Mimpi dan ringkasan penyapuan Dreaming untuk tinjauan manusia, termasuk entri backfill historis yang terlandaskan.

File-file ini berada di workspace agen (default `~/.openclaw/workspace`).

<Tip>
Jika Anda ingin agen Anda mengingat sesuatu, cukup minta: "Ingat bahwa saya lebih suka TypeScript." Agen akan menuliskannya ke file yang sesuai.
</Tip>

## Alat memori

Agen memiliki dua alat untuk bekerja dengan memori:

- **`memory_search`** -- menemukan catatan yang relevan menggunakan pencarian semantik, bahkan ketika susunan katanya berbeda dari aslinya.
- **`memory_get`** -- membaca file memori tertentu atau rentang baris.

Kedua alat disediakan oleh Plugin memori aktif (default: `memory-core`).

## Plugin pendamping Memory Wiki

Jika Anda ingin memori yang bertahan lama berperilaku lebih seperti basis pengetahuan yang dipelihara daripada sekadar catatan mentah, gunakan Plugin bawaan `memory-wiki`.

`memory-wiki` mengompilasi pengetahuan yang bertahan lama ke dalam vault wiki dengan:

- struktur halaman yang deterministik
- klaim dan bukti yang terstruktur
- pelacakan kontradiksi dan kebaruan
- dasbor yang dihasilkan
- digest terkompilasi untuk konsumen agen/runtime
- alat yang native untuk wiki seperti `wiki_search`, `wiki_get`, `wiki_apply`, dan `wiki_lint`

Ini tidak menggantikan Plugin memori aktif. Plugin memori aktif tetap memiliki recall, promosi, dan Dreaming. `memory-wiki` menambahkan lapisan pengetahuan yang kaya provenance di sampingnya.

Lihat [Memory Wiki](/id/plugins/memory-wiki).

## Pencarian memori

Ketika penyedia embedding dikonfigurasi, `memory_search` menggunakan **pencarian hibrida** -- menggabungkan kemiripan vektor (makna semantik) dengan pencocokan kata kunci (istilah persis seperti ID dan simbol kode). Ini berfungsi langsung setelah Anda memiliki API key untuk penyedia yang didukung.

<Info>
OpenClaw secara otomatis mendeteksi penyedia embedding Anda dari API key yang tersedia. Jika Anda telah mengonfigurasi key OpenAI, Gemini, Voyage, atau Mistral, pencarian memori akan diaktifkan secara otomatis.
</Info>

Untuk detail tentang cara kerja pencarian, opsi penyesuaian, dan penyiapan penyedia, lihat
[Pencarian Memori](/id/concepts/memory-search).

## Backend memori

<CardGroup cols={3}>
<Card title="Bawaan (default)" icon="database" href="/id/concepts/memory-builtin">
Berbasis SQLite. Berfungsi langsung dengan pencarian kata kunci, kemiripan vektor, dan pencarian hibrida. Tidak memerlukan dependensi tambahan.
</Card>
<Card title="QMD" icon="search" href="/id/concepts/memory-qmd">
Sidecar local-first dengan reranking, perluasan kueri, dan kemampuan untuk mengindeks direktori di luar workspace.
</Card>
<Card title="Honcho" icon="brain" href="/id/concepts/memory-honcho">
Memori lintas sesi yang native AI dengan pemodelan pengguna, pencarian semantik, dan kesadaran multi-agen. Instalasi Plugin.
</Card>
</CardGroup>

## Lapisan wiki pengetahuan

<CardGroup cols={1}>
<Card title="Memory Wiki" icon="book" href="/id/plugins/memory-wiki">
Mengompilasi memori yang bertahan lama ke dalam vault wiki yang kaya provenance dengan klaim, dasbor, mode bridge, dan alur kerja yang ramah Obsidian.
</Card>
</CardGroup>

## Flush memori otomatis

Sebelum [Compaction](/id/concepts/compaction) merangkum percakapan Anda, OpenClaw menjalankan giliran senyap yang mengingatkan agen untuk menyimpan konteks penting ke file memori. Ini aktif secara default -- Anda tidak perlu mengonfigurasi apa pun.

<Tip>
Flush memori mencegah kehilangan konteks selama Compaction. Jika agen Anda memiliki fakta penting dalam percakapan yang belum ditulis ke file, fakta tersebut akan disimpan secara otomatis sebelum peringkasan terjadi.
</Tip>

## Dreaming

Dreaming adalah proses konsolidasi latar belakang opsional untuk memori. Ini mengumpulkan sinyal jangka pendek, memberi skor pada kandidat, dan hanya mempromosikan item yang memenuhi syarat ke memori jangka panjang (`MEMORY.md`).

Ini dirancang untuk menjaga agar memori jangka panjang tetap memiliki sinyal tinggi:

- **Opt-in**: dinonaktifkan secara default.
- **Terjadwal**: saat diaktifkan, `memory-core` secara otomatis mengelola satu pekerjaan Cron berulang untuk penyapuan Dreaming penuh.
- **Berambang batas**: promosi harus melewati gerbang skor, frekuensi recall, dan keragaman kueri.
- **Dapat ditinjau**: ringkasan fase dan entri buku harian ditulis ke `DREAMS.md` untuk tinjauan manusia.

Untuk perilaku fase, sinyal penilaian, dan detail Buku Harian Mimpi, lihat
[Dreaming](/id/concepts/dreaming).

## Backfill terlandaskan dan promosi langsung

Sistem Dreaming kini memiliki dua jalur peninjauan yang sangat terkait:

- **Dreaming langsung** bekerja dari penyimpanan Dreaming jangka pendek di bawah
  `memory/.dreams/` dan itulah yang digunakan fase mendalam normal saat memutuskan apa yang
  dapat lulus ke `MEMORY.md`.
- **Backfill terlandaskan** membaca catatan historis `memory/YYYY-MM-DD.md` sebagai
  file harian mandiri dan menulis keluaran tinjauan terstruktur ke `DREAMS.md`.

Backfill terlandaskan berguna ketika Anda ingin memutar ulang catatan lama dan memeriksa apa yang menurut sistem bersifat tahan lama tanpa mengedit `MEMORY.md` secara manual.

Saat Anda menggunakan:

```bash
openclaw memory rem-backfill --path ./memory --stage-short-term
```

kandidat tahan lama yang terlandaskan tidak dipromosikan secara langsung. Kandidat tersebut dipentaskan ke penyimpanan Dreaming jangka pendek yang sama yang sudah digunakan fase mendalam normal. Artinya:

- `DREAMS.md` tetap menjadi permukaan tinjauan manusia.
- penyimpanan jangka pendek tetap menjadi permukaan pemeringkatan yang menghadap mesin.
- `MEMORY.md` tetap hanya ditulis oleh promosi mendalam.

Jika Anda memutuskan pemutaran ulang itu tidak berguna, Anda dapat menghapus artefak yang dipentaskan tanpa menyentuh entri buku harian biasa atau state recall normal:

```bash
openclaw memory rem-backfill --rollback
openclaw memory rem-backfill --rollback-short-term
```

## CLI

```bash
openclaw memory status          # Periksa status indeks dan penyedia
openclaw memory search "query"  # Cari dari baris perintah
openclaw memory index --force   # Bangun ulang indeks
```

## Bacaan lanjutan

- [Builtin Memory Engine](/id/concepts/memory-builtin) -- backend SQLite default
- [QMD Memory Engine](/id/concepts/memory-qmd) -- sidecar local-first tingkat lanjut
- [Honcho Memory](/id/concepts/memory-honcho) -- memori lintas sesi yang native AI
- [Memory Wiki](/id/plugins/memory-wiki) -- vault pengetahuan terkompilasi dan alat yang native untuk wiki
- [Pencarian Memori](/id/concepts/memory-search) -- pipeline pencarian, penyedia, dan
  penyesuaian
- [Dreaming](/id/concepts/dreaming) -- promosi latar belakang
  dari recall jangka pendek ke memori jangka panjang
- [Referensi konfigurasi memori](/id/reference/memory-config) -- semua opsi konfigurasi
- [Compaction](/id/concepts/compaction) -- bagaimana Compaction berinteraksi dengan memori
