---
read_when:
    - Anda ingin memahami cara kerja memori
    - Anda ingin mengetahui file memori apa yang harus ditulis
summary: Bagaimana OpenClaw mengingat berbagai hal di seluruh sesi
title: Ikhtisar Memori
x-i18n:
    generated_at: "2026-04-08T06:00:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3bb8552341b0b651609edaaae826a22fdc535d240aed4fad4af4b069454004af
    source_path: concepts/memory.md
    workflow: 15
---

# Ikhtisar Memori

OpenClaw mengingat berbagai hal dengan menulis **file Markdown biasa** di
workspace agen Anda. Model hanya "mengingat" apa yang disimpan ke disk -- tidak ada
status tersembunyi.

## Cara kerjanya

Agen Anda memiliki tiga file yang terkait dengan memori:

- **`MEMORY.md`** -- memori jangka panjang. Fakta, preferensi, dan
  keputusan yang tahan lama. Dimuat pada awal setiap sesi DM.
- **`memory/YYYY-MM-DD.md`** -- catatan harian. Konteks berjalan dan pengamatan.
  Catatan hari ini dan kemarin dimuat secara otomatis.
- **`DREAMS.md`** (eksperimental, opsional) -- Buku Harian Mimpi dan ringkasan
  penyapuan dreaming untuk ditinjau manusia.

File-file ini berada di workspace agen (default `~/.openclaw/workspace`).

<Tip>
Jika Anda ingin agen Anda mengingat sesuatu, cukup minta: "Ingat bahwa saya
lebih memilih TypeScript." Agen akan menuliskannya ke file yang sesuai.
</Tip>

## Alat memori

Agen memiliki dua alat untuk bekerja dengan memori:

- **`memory_search`** -- menemukan catatan yang relevan menggunakan pencarian semantik, bahkan saat
  kata-katanya berbeda dari aslinya.
- **`memory_get`** -- membaca file memori tertentu atau rentang baris.

Kedua alat ini disediakan oleh plugin memori yang aktif (default: `memory-core`).

## Plugin pendamping Memory Wiki

Jika Anda ingin memori tahan lama berperilaku lebih seperti basis pengetahuan yang dipelihara daripada
sekadar catatan mentah, gunakan plugin bawaan `memory-wiki`.

`memory-wiki` menyusun pengetahuan tahan lama ke dalam vault wiki dengan:

- struktur halaman yang deterministik
- klaim dan bukti yang terstruktur
- pelacakan kontradiksi dan kebaruan
- dasbor yang dihasilkan
- ringkasan terkompilasi untuk konsumen agen/runtime
- alat native wiki seperti `wiki_search`, `wiki_get`, `wiki_apply`, dan `wiki_lint`

Ini tidak menggantikan plugin memori aktif. Plugin memori aktif tetap
memiliki recall, promosi, dan dreaming. `memory-wiki` menambahkan
lapisan pengetahuan kaya provenance di sampingnya.

Lihat [Memory Wiki](/id/plugins/memory-wiki).

## Pencarian memori

Saat penyedia embedding dikonfigurasi, `memory_search` menggunakan **pencarian
hibrida** -- menggabungkan kemiripan vektor (makna semantik) dengan pencocokan kata kunci
(istilah persis seperti ID dan simbol kode). Ini langsung berfungsi setelah Anda memiliki
kunci API untuk penyedia yang didukung.

<Info>
OpenClaw mendeteksi otomatis penyedia embedding Anda dari kunci API yang tersedia. Jika Anda
telah mengonfigurasi kunci OpenAI, Gemini, Voyage, atau Mistral, pencarian memori
diaktifkan secara otomatis.
</Info>

Untuk detail tentang cara kerja pencarian, opsi penyesuaian, dan penyiapan penyedia, lihat
[Pencarian Memori](/id/concepts/memory-search).

## Backend memori

<CardGroup cols={3}>
<Card title="Bawaan (default)" icon="database" href="/id/concepts/memory-builtin">
Berbasis SQLite. Berfungsi langsung dengan pencarian kata kunci, kemiripan vektor, dan
pencarian hibrida. Tanpa dependensi tambahan.
</Card>
<Card title="QMD" icon="search" href="/id/concepts/memory-qmd">
Sidecar local-first dengan reranking, perluasan kueri, dan kemampuan untuk mengindeks
direktori di luar workspace.
</Card>
<Card title="Honcho" icon="brain" href="/id/concepts/memory-honcho">
Memori lintas sesi native AI dengan pemodelan pengguna, pencarian semantik, dan
kesadaran multi-agen. Instalasi plugin.
</Card>
</CardGroup>

## Lapisan wiki pengetahuan

<CardGroup cols={1}>
<Card title="Memory Wiki" icon="book" href="/id/plugins/memory-wiki">
Menyusun memori tahan lama menjadi vault wiki kaya provenance dengan klaim,
dasbor, mode bridge, dan alur kerja yang ramah Obsidian.
</Card>
</CardGroup>

## Flush memori otomatis

Sebelum [compaction](/id/concepts/compaction) merangkum percakapan Anda, OpenClaw
menjalankan giliran senyap yang mengingatkan agen untuk menyimpan konteks penting ke file
memori. Ini aktif secara default -- Anda tidak perlu mengonfigurasi apa pun.

<Tip>
Flush memori mencegah hilangnya konteks selama compaction. Jika agen Anda memiliki
fakta penting dalam percakapan yang belum ditulis ke file, fakta tersebut
akan disimpan secara otomatis sebelum ringkasan dibuat.
</Tip>

## Dreaming (eksperimental)

Dreaming adalah proses konsolidasi latar belakang opsional untuk memori. Ini mengumpulkan
sinyal jangka pendek, memberi skor pada kandidat, dan hanya mempromosikan item yang memenuhi syarat ke
memori jangka panjang (`MEMORY.md`).

Ini dirancang untuk menjaga memori jangka panjang tetap bernilai tinggi:

- **Opt-in**: dinonaktifkan secara default.
- **Terjadwal**: saat diaktifkan, `memory-core` mengelola otomatis satu pekerjaan cron berulang
  untuk penyapuan dreaming penuh.
- **Berambang batas**: promosi harus lolos gerbang skor, frekuensi recall, dan
  keragaman kueri.
- **Dapat ditinjau**: ringkasan fase dan entri buku harian ditulis ke `DREAMS.md`
  untuk ditinjau manusia.

Untuk perilaku fase, sinyal penilaian, dan detail Buku Harian Mimpi, lihat
[Dreaming (eksperimental)](/id/concepts/dreaming).

## CLI

```bash
openclaw memory status          # Periksa status indeks dan penyedia
openclaw memory search "query"  # Cari dari baris perintah
openclaw memory index --force   # Bangun ulang indeks
```

## Bacaan lebih lanjut

- [Builtin Memory Engine](/id/concepts/memory-builtin) -- backend SQLite default
- [QMD Memory Engine](/id/concepts/memory-qmd) -- sidecar local-first lanjutan
- [Honcho Memory](/id/concepts/memory-honcho) -- memori lintas sesi native AI
- [Memory Wiki](/id/plugins/memory-wiki) -- vault pengetahuan terkompilasi dan alat native wiki
- [Memory Search](/id/concepts/memory-search) -- pipeline pencarian, penyedia, dan
  penyesuaian
- [Dreaming (eksperimental)](/id/concepts/dreaming) -- promosi latar belakang
  dari recall jangka pendek ke memori jangka panjang
- [Referensi konfigurasi memori](/id/reference/memory-config) -- semua opsi konfigurasi
- [Compaction](/id/concepts/compaction) -- bagaimana compaction berinteraksi dengan memori
