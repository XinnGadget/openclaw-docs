---
read_when:
    - Anda menginginkan pengetahuan persisten yang melampaui catatan `MEMORY.md` biasa
    - Anda sedang mengonfigurasi Plugin memory-wiki bawaan
    - Anda ingin memahami `wiki_search`, `wiki_get`, atau mode bridge
summary: 'memory-wiki: brankas pengetahuan terkompilasi dengan provenance, klaim, dashboard, dan mode bridge'
title: Wiki Memori
x-i18n:
    generated_at: "2026-04-12T23:28:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: 44d168a7096f744c56566ecac57499192eb101b4dd8a78e1b92f3aa0d6da3ad1
    source_path: plugins/memory-wiki.md
    workflow: 15
---

# Wiki Memori

`memory-wiki` adalah Plugin bawaan yang mengubah memori tahan lama menjadi
brankas pengetahuan terkompilasi.

Ini **tidak** menggantikan Plugin Active Memory. Plugin Active Memory tetap
memiliki recall, promotion, indexing, dan Dreaming. `memory-wiki` berada di
sampingnya dan mengompilasi pengetahuan tahan lama menjadi wiki yang dapat dinavigasi dengan halaman deterministik,
klaim terstruktur, provenance, dashboard, dan digest yang dapat dibaca mesin.

Gunakan ini ketika Anda ingin memori berperilaku lebih seperti lapisan pengetahuan yang terpelihara dan
tidak hanya seperti tumpukan file Markdown.

## Apa yang ditambahkan

- Brankas wiki khusus dengan tata letak halaman deterministik
- Metadata klaim dan bukti terstruktur, bukan hanya prosa
- Provenance, confidence, contradiction, dan pertanyaan terbuka di tingkat halaman
- Digest terkompilasi untuk konsumen agen/runtime
- Tool search/get/apply/lint native wiki
- Mode bridge opsional yang mengimpor artefak publik dari Plugin Active Memory
- Mode render ramah Obsidian dan integrasi CLI opsional

## Cara kerjanya dengan memori

Anggap pembagiannya seperti ini:

| Lapisan                                                 | Kepemilikan                                                                                 |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------- |
| Plugin Active Memory (`memory-core`, QMD, Honcho, dll.) | Recall, pencarian semantik, promotion, Dreaming, runtime memori                             |
| `memory-wiki`                                           | Halaman wiki terkompilasi, sintesis kaya provenance, dashboard, search/get/apply khusus wiki |

Jika Plugin Active Memory mengekspos artefak recall bersama, OpenClaw dapat mencari
kedua lapisan dalam satu lintasan dengan `memory_search corpus=all`.

Saat Anda membutuhkan ranking khusus wiki, provenance, atau akses halaman langsung, gunakan
tool native wiki sebagai gantinya.

## Pola hibrida yang direkomendasikan

Default yang kuat untuk pengaturan local-first adalah:

- QMD sebagai backend memori aktif untuk recall dan pencarian semantik yang luas
- `memory-wiki` dalam mode `bridge` untuk halaman pengetahuan sintetis yang tahan lama

Pemisahan itu bekerja dengan baik karena setiap lapisan tetap fokus:

- QMD menjaga catatan mentah, ekspor sesi, dan koleksi tambahan tetap dapat dicari
- `memory-wiki` mengompilasi entitas, klaim, dashboard, dan halaman sumber yang stabil

Aturan praktis:

- gunakan `memory_search` saat Anda menginginkan satu lintasan recall luas di seluruh memori
- gunakan `wiki_search` dan `wiki_get` saat Anda menginginkan hasil wiki yang sadar provenance
- gunakan `memory_search corpus=all` saat Anda ingin pencarian bersama mencakup kedua lapisan

Jika mode bridge melaporkan nol artefak yang diekspor, Plugin Active Memory saat ini
belum mengekspos input bridge publik. Jalankan `openclaw wiki doctor` terlebih dahulu,
lalu pastikan Plugin Active Memory mendukung artefak publik.

## Mode brankas

`memory-wiki` mendukung tiga mode brankas:

### `isolated`

Brankas sendiri, sumber sendiri, tidak bergantung pada `memory-core`.

Gunakan ini ketika Anda ingin wiki menjadi penyimpanan pengetahuan terkurasi miliknya sendiri.

### `bridge`

Membaca artefak memori publik dan event memori dari Plugin Active Memory
melalui seam SDK Plugin publik.

Gunakan ini ketika Anda ingin wiki mengompilasi dan mengatur artefak yang diekspor
oleh Plugin memori tanpa menjangkau internal Plugin privat.

Mode bridge dapat mengindeks:

- artefak memori yang diekspor
- laporan Dreaming
- catatan harian
- file root memori
- log event memori

### `unsafe-local`

Jalur keluar eksplisit pada mesin yang sama untuk jalur privat lokal.

Mode ini sengaja eksperimental dan tidak portabel. Gunakan hanya ketika Anda
memahami batas kepercayaannya dan secara khusus membutuhkan akses filesystem lokal yang
tidak dapat disediakan oleh mode bridge.

## Tata letak brankas

Plugin menginisialisasi brankas seperti ini:

```text
<vault>/
  AGENTS.md
  WIKI.md
  index.md
  inbox.md
  entities/
  concepts/
  syntheses/
  sources/
  reports/
  _attachments/
  _views/
  .openclaw-wiki/
```

Konten yang dikelola tetap berada di dalam blok yang dihasilkan. Blok catatan manusia dipertahankan.

Kelompok halaman utamanya adalah:

- `sources/` untuk materi mentah yang diimpor dan halaman yang didukung bridge
- `entities/` untuk hal, orang, sistem, proyek, dan objek yang tahan lama
- `concepts/` untuk ide, abstraksi, pola, dan kebijakan
- `syntheses/` untuk ringkasan terkompilasi dan rollup yang dipelihara
- `reports/` untuk dashboard yang dihasilkan

## Klaim dan bukti terstruktur

Halaman dapat membawa frontmatter `claims` terstruktur, bukan hanya teks bebas.

Setiap klaim dapat mencakup:

- `id`
- `text`
- `status`
- `confidence`
- `evidence[]`
- `updatedAt`

Entri bukti dapat mencakup:

- `sourceId`
- `path`
- `lines`
- `weight`
- `note`
- `updatedAt`

Inilah yang membuat wiki bertindak lebih seperti lapisan keyakinan daripada
sekadar dump catatan pasif. Klaim dapat dilacak, diberi skor, diperdebatkan, dan diselesaikan kembali ke sumber.

## Pipeline kompilasi

Langkah kompilasi membaca halaman wiki, menormalkan ringkasan, dan menghasilkan
artefak stabil yang menghadap mesin di bawah:

- `.openclaw-wiki/cache/agent-digest.json`
- `.openclaw-wiki/cache/claims.jsonl`

Digest ini ada agar agen dan kode runtime tidak perlu mengurai halaman Markdown.

Output terkompilasi juga mendukung:

- pengindeksan wiki lintasan pertama untuk alur search/get
- lookup claim-id kembali ke halaman pemilik
- suplemen prompt yang ringkas
- pembuatan laporan/dashboard

## Dashboard dan laporan kesehatan

Saat `render.createDashboards` diaktifkan, kompilasi memelihara dashboard di bawah `reports/`.

Laporan bawaan mencakup:

- `reports/open-questions.md`
- `reports/contradictions.md`
- `reports/low-confidence.md`
- `reports/claim-health.md`
- `reports/stale-pages.md`

Laporan ini melacak hal-hal seperti:

- klaster catatan contradiction
- klaster klaim yang saling bersaing
- klaim yang tidak memiliki bukti terstruktur
- halaman dan klaim dengan confidence rendah
- kesegaran yang basi atau tidak diketahui
- halaman dengan pertanyaan yang belum terselesaikan

## Pencarian dan pengambilan

`memory-wiki` mendukung dua backend pencarian:

- `shared`: gunakan alur pencarian memori bersama jika tersedia
- `local`: cari wiki secara lokal

Ini juga mendukung tiga corpus:

- `wiki`
- `memory`
- `all`

Perilaku penting:

- `wiki_search` dan `wiki_get` menggunakan digest terkompilasi sebagai lintasan pertama bila memungkinkan
- id klaim dapat diselesaikan kembali ke halaman pemilik
- klaim contested/stale/fresh memengaruhi ranking
- label provenance dapat dipertahankan hingga hasil

Aturan praktis:

- gunakan `memory_search corpus=all` untuk satu lintasan recall luas
- gunakan `wiki_search` + `wiki_get` saat Anda peduli pada ranking khusus wiki,
  provenance, atau struktur keyakinan di tingkat halaman

## Tool agen

Plugin mendaftarkan tool berikut:

- `wiki_status`
- `wiki_search`
- `wiki_get`
- `wiki_apply`
- `wiki_lint`

Fungsinya:

- `wiki_status`: mode brankas saat ini, kesehatan, ketersediaan CLI Obsidian
- `wiki_search`: mencari halaman wiki dan, jika dikonfigurasi, corpus memori bersama
- `wiki_get`: membaca halaman wiki berdasarkan id/path atau fallback ke corpus memori bersama
- `wiki_apply`: mutasi sintesis/metadata yang sempit tanpa pembedahan halaman bentuk bebas
- `wiki_lint`: pemeriksaan struktural, celah provenance, contradiction, pertanyaan terbuka

Plugin juga mendaftarkan suplemen corpus memori non-eksklusif, sehingga
`memory_search` dan `memory_get` bersama dapat menjangkau wiki saat Plugin Active Memory
mendukung pemilihan corpus.

## Perilaku prompt dan konteks

Saat `context.includeCompiledDigestPrompt` diaktifkan, bagian prompt memori
menambahkan snapshot terkompilasi ringkas dari `agent-digest.json`.

Snapshot tersebut sengaja kecil dan bernilai sinyal tinggi:

- hanya halaman teratas
- hanya klaim teratas
- jumlah contradiction
- jumlah pertanyaan
- qualifier confidence/freshness

Ini bersifat opt-in karena mengubah bentuk prompt dan terutama berguna untuk
mesin konteks atau perakitan prompt lama yang secara eksplisit menggunakan suplemen memori.

## Konfigurasi

Letakkan config di bawah `plugins.entries.memory-wiki.config`:

```json5
{
  plugins: {
    entries: {
      "memory-wiki": {
        enabled: true,
        config: {
          vaultMode: "isolated",
          vault: {
            path: "~/.openclaw/wiki/main",
            renderMode: "obsidian",
          },
          obsidian: {
            enabled: true,
            useOfficialCli: true,
            vaultName: "OpenClaw Wiki",
            openAfterWrites: false,
          },
          bridge: {
            enabled: false,
            readMemoryArtifacts: true,
            indexDreamReports: true,
            indexDailyNotes: true,
            indexMemoryRoot: true,
            followMemoryEvents: true,
          },
          ingest: {
            autoCompile: true,
            maxConcurrentJobs: 1,
            allowUrlIngest: true,
          },
          search: {
            backend: "shared",
            corpus: "wiki",
          },
          context: {
            includeCompiledDigestPrompt: false,
          },
          render: {
            preserveHumanBlocks: true,
            createBacklinks: true,
            createDashboards: true,
          },
        },
      },
    },
  },
}
```

Pengaturan kunci:

- `vaultMode`: `isolated`, `bridge`, `unsafe-local`
- `vault.renderMode`: `native` atau `obsidian`
- `bridge.readMemoryArtifacts`: impor artefak publik Plugin Active Memory
- `bridge.followMemoryEvents`: sertakan log event dalam mode bridge
- `search.backend`: `shared` atau `local`
- `search.corpus`: `wiki`, `memory`, atau `all`
- `context.includeCompiledDigestPrompt`: tambahkan snapshot digest ringkas ke bagian prompt memori
- `render.createBacklinks`: hasilkan blok terkait deterministik
- `render.createDashboards`: hasilkan halaman dashboard

### Contoh: QMD + mode bridge

Gunakan ini ketika Anda menginginkan QMD untuk recall dan `memory-wiki` untuk lapisan
pengetahuan yang dipelihara:

```json5
{
  memory: {
    backend: "qmd",
      "memory-wiki": {
        enabled: true,
        config: {
          vaultMode: "bridge",
          bridge: {
            enabled: true,
            readMemoryArtifacts: true,
            indexDreamReports: true,
            indexDailyNotes: true,
            indexMemoryRoot: true,
            followMemoryEvents: true,
          },
          search: {
            backend: "shared",
            corpus: "all",
          },
          context: {
            includeCompiledDigestPrompt: false,
          },
        },
      },
    },
  },
}
```

Ini menjaga:

- QMD bertanggung jawab atas recall memori aktif
- `memory-wiki` tetap fokus pada halaman terkompilasi dan dashboard
- bentuk prompt tetap tidak berubah sampai Anda sengaja mengaktifkan prompt digest terkompilasi

## CLI

`memory-wiki` juga mengekspos permukaan CLI tingkat atas:

```bash
openclaw wiki status
openclaw wiki doctor
openclaw wiki init
openclaw wiki ingest ./notes/alpha.md
openclaw wiki compile
openclaw wiki lint
openclaw wiki search "alpha"
openclaw wiki get entity.alpha
openclaw wiki apply synthesis "Alpha Summary" --body "..." --source-id source.alpha
openclaw wiki bridge import
openclaw wiki obsidian status
```

Lihat [CLI: wiki](/cli/wiki) untuk referensi perintah lengkap.

## Dukungan Obsidian

Saat `vault.renderMode` bernilai `obsidian`, Plugin menulis Markdown yang ramah Obsidian
dan secara opsional dapat menggunakan CLI `obsidian` resmi.

Alur kerja yang didukung mencakup:

- pemeriksaan status
- pencarian brankas
- membuka halaman
- memanggil perintah Obsidian
- melompat ke catatan harian

Ini opsional. Wiki tetap berfungsi dalam mode native tanpa Obsidian.

## Alur kerja yang direkomendasikan

1. Pertahankan Plugin Active Memory Anda untuk recall/promotion/Dreaming.
2. Aktifkan `memory-wiki`.
3. Mulai dengan mode `isolated` kecuali Anda secara eksplisit menginginkan mode bridge.
4. Gunakan `wiki_search` / `wiki_get` saat provenance penting.
5. Gunakan `wiki_apply` untuk sintesis sempit atau pembaruan metadata.
6. Jalankan `wiki_lint` setelah perubahan yang bermakna.
7. Aktifkan dashboard jika Anda menginginkan visibilitas basi/contradiction.

## Dokumen terkait

- [Ikhtisar Memori](/id/concepts/memory)
- [CLI: memory](/cli/memory)
- [CLI: wiki](/cli/wiki)
- [Ikhtisar SDK Plugin](/id/plugins/sdk-overview)
