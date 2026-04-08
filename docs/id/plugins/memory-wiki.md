---
read_when:
    - Anda menginginkan pengetahuan persisten melampaui catatan MEMORY.md biasa
    - Anda sedang mengonfigurasi plugin memory-wiki bawaan
    - Anda ingin memahami wiki_search, wiki_get, atau mode bridge
summary: 'memory-wiki: brankas pengetahuan terkompilasi dengan provenance, klaim, dasbor, dan mode bridge'
title: Memory Wiki
x-i18n:
    generated_at: "2026-04-08T06:01:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: b78dd6a4ef4451dae6b53197bf0c7c2a2ba846b08e4a3a93c1026366b1598d82
    source_path: plugins/memory-wiki.md
    workflow: 15
---

# Memory Wiki

`memory-wiki` adalah plugin bawaan yang mengubah memori tahan lama menjadi
brankas pengetahuan terkompilasi.

Plugin ini **tidak** menggantikan plugin memori aktif. Plugin memori aktif tetap
mengelola recall, promotion, indexing, dan dreaming. `memory-wiki` berada di
sampingnya dan mengompilasi pengetahuan tahan lama menjadi wiki yang dapat
dinavigasi dengan halaman deterministik, klaim terstruktur, provenance, dasbor,
dan digest yang dapat dibaca mesin.

Gunakan ini ketika Anda ingin memori berperilaku lebih seperti lapisan
pengetahuan yang dipelihara dan lebih sedikit seperti tumpukan file Markdown.

## Yang ditambahkan

- Brankas wiki khusus dengan tata letak halaman deterministik
- Metadata klaim dan bukti yang terstruktur, bukan sekadar prosa
- Provenance, confidence, contradiction, dan open question pada tingkat halaman
- Digest terkompilasi untuk konsumen agent/runtime
- Tool wiki-native untuk search/get/apply/lint
- Mode bridge opsional yang mengimpor artifact publik dari plugin memori aktif
- Mode render yang ramah Obsidian dan integrasi CLI opsional

## Bagaimana ini sesuai dengan memori

Anggap pembagiannya seperti ini:

| Lapisan                                                | Mengelola                                                                                  |
| ------------------------------------------------------ | ------------------------------------------------------------------------------------------ |
| Plugin memori aktif (`memory-core`, QMD, Honcho, dll.) | Recall, semantic search, promotion, dreaming, runtime memori                               |
| `memory-wiki`                                          | Halaman wiki terkompilasi, sintesis kaya provenance, dasbor, wiki-specific search/get/apply |

Jika plugin memori aktif mengekspos artifact recall bersama, OpenClaw dapat
mencari di kedua lapisan dalam satu lintasan dengan `memory_search corpus=all`.

Saat Anda membutuhkan ranking, provenance, atau akses halaman langsung yang
khusus wiki, gunakan tool wiki-native sebagai gantinya.

## Mode brankas

`memory-wiki` mendukung tiga mode brankas:

### `isolated`

Brankas sendiri, sumber sendiri, tanpa ketergantungan pada `memory-core`.

Gunakan ini ketika Anda ingin wiki menjadi penyimpanan pengetahuan terkurasi
miliknya sendiri.

### `bridge`

Membaca artifact memori publik dan event memori dari plugin memori aktif
melalui seam SDK plugin publik.

Gunakan ini ketika Anda ingin wiki mengompilasi dan mengatur artifact yang
diekspor plugin memori tanpa menjangkau internal plugin privat.

Mode bridge dapat mengindeks:

- artifact memori yang diekspor
- laporan dream
- catatan harian
- file root memori
- log event memori

### `unsafe-local`

Escape hatch eksplisit pada mesin yang sama untuk path privat lokal.

Mode ini sengaja bersifat eksperimental dan tidak portabel. Gunakan hanya
ketika Anda memahami trust boundary dan secara khusus memerlukan akses sistem
berkas lokal yang tidak dapat disediakan oleh mode bridge.

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

Konten terkelola tetap berada di dalam blok yang dihasilkan. Blok catatan
manusia dipertahankan.

Kelompok halaman utama adalah:

- `sources/` untuk bahan mentah yang diimpor dan halaman yang didukung bridge
- `entities/` untuk hal, orang, sistem, proyek, dan objek yang tahan lama
- `concepts/` untuk ide, abstraksi, pola, dan kebijakan
- `syntheses/` untuk ringkasan terkompilasi dan rollup yang dipelihara
- `reports/` untuk dasbor yang dihasilkan

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
sekadar tumpukan catatan pasif. Klaim dapat dilacak, diberi skor,
dipersengketakan, dan diselesaikan kembali ke sumber.

## Pipeline compile

Langkah compile membaca halaman wiki, menormalkan ringkasan, dan menghasilkan
artifact stabil yang menghadap mesin di bawah:

- `.openclaw-wiki/cache/agent-digest.json`
- `.openclaw-wiki/cache/claims.jsonl`

Digest ini ada agar agent dan kode runtime tidak perlu mengikis halaman
Markdown.

Output terkompilasi juga mendukung:

- pengindeksan wiki lintasan pertama untuk alur search/get
- lookup claim-id kembali ke halaman pemiliknya
- suplemen prompt yang ringkas
- pembuatan laporan/dasbor

## Dasbor dan laporan kesehatan

Saat `render.createDashboards` diaktifkan, compile memelihara dasbor di bawah
`reports/`.

Laporan bawaan mencakup:

- `reports/open-questions.md`
- `reports/contradictions.md`
- `reports/low-confidence.md`
- `reports/claim-health.md`
- `reports/stale-pages.md`

Laporan ini melacak hal-hal seperti:

- cluster catatan contradiction
- cluster klaim yang saling bersaing
- klaim yang tidak memiliki bukti terstruktur
- halaman dan klaim dengan confidence rendah
- kesegaran basi atau tidak diketahui
- halaman dengan pertanyaan yang belum terselesaikan

## Pencarian dan pengambilan

`memory-wiki` mendukung dua backend pencarian:

- `shared`: gunakan alur pencarian memori bersama jika tersedia
- `local`: cari wiki secara lokal

Plugin ini juga mendukung tiga corpus:

- `wiki`
- `memory`
- `all`

Perilaku penting:

- `wiki_search` dan `wiki_get` menggunakan digest terkompilasi sebagai lintasan
  pertama jika memungkinkan
- id klaim dapat diselesaikan kembali ke halaman pemiliknya
- klaim contested/stale/fresh memengaruhi ranking
- label provenance dapat dipertahankan hingga ke hasil

Aturan praktis:

- gunakan `memory_search corpus=all` untuk satu lintasan recall yang luas
- gunakan `wiki_search` + `wiki_get` ketika Anda peduli pada ranking khusus
  wiki, provenance, atau struktur keyakinan tingkat halaman

## Tool agent

Plugin mendaftarkan tool berikut:

- `wiki_status`
- `wiki_search`
- `wiki_get`
- `wiki_apply`
- `wiki_lint`

Fungsinya:

- `wiki_status`: mode brankas saat ini, kesehatan, ketersediaan CLI Obsidian
- `wiki_search`: mencari halaman wiki dan, saat dikonfigurasi, corpus memori bersama
- `wiki_get`: membaca halaman wiki berdasarkan id/path atau fallback ke corpus memori bersama
- `wiki_apply`: mutasi sintesis/metadata sempit tanpa operasi bebas pada halaman
- `wiki_lint`: pemeriksaan struktural, celah provenance, contradiction, open question

Plugin ini juga mendaftarkan suplemen corpus memori non-eksklusif, sehingga
`memory_search` dan `memory_get` bersama dapat menjangkau wiki saat plugin
memori aktif mendukung pemilihan corpus.

## Perilaku prompt dan konteks

Saat `context.includeCompiledDigestPrompt` diaktifkan, bagian prompt memori
menambahkan snapshot terkompilasi yang ringkas dari `agent-digest.json`.

Snapshot itu sengaja kecil dan bernilai sinyal tinggi:

- hanya halaman teratas
- hanya klaim teratas
- jumlah contradiction
- jumlah pertanyaan
- qualifier confidence/freshness

Ini bersifat opt-in karena mengubah bentuk prompt dan terutama berguna untuk
engine konteks atau perakitan prompt lama yang secara eksplisit mengonsumsi
suplemen memori.

## Konfigurasi

Tempatkan konfigurasi di bawah `plugins.entries.memory-wiki.config`:

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

Toggle utama:

- `vaultMode`: `isolated`, `bridge`, `unsafe-local`
- `vault.renderMode`: `native` atau `obsidian`
- `bridge.readMemoryArtifacts`: impor artifact publik plugin memori aktif
- `bridge.followMemoryEvents`: sertakan log event dalam mode bridge
- `search.backend`: `shared` atau `local`
- `search.corpus`: `wiki`, `memory`, atau `all`
- `context.includeCompiledDigestPrompt`: tambahkan snapshot digest ringkas ke bagian prompt memori
- `render.createBacklinks`: hasilkan blok terkait yang deterministik
- `render.createDashboards`: hasilkan halaman dasbor

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

Saat `vault.renderMode` adalah `obsidian`, plugin menulis Markdown yang ramah
Obsidian dan dapat secara opsional menggunakan CLI `obsidian` resmi.

Alur kerja yang didukung mencakup:

- probe status
- pencarian brankas
- membuka halaman
- memanggil perintah Obsidian
- melompat ke catatan harian

Ini bersifat opsional. Wiki tetap berfungsi dalam mode native tanpa Obsidian.

## Alur kerja yang direkomendasikan

1. Pertahankan plugin memori aktif Anda untuk recall/promotion/dreaming.
2. Aktifkan `memory-wiki`.
3. Mulailah dengan mode `isolated` kecuali Anda secara eksplisit menginginkan mode bridge.
4. Gunakan `wiki_search` / `wiki_get` saat provenance penting.
5. Gunakan `wiki_apply` untuk sintesis sempit atau pembaruan metadata.
6. Jalankan `wiki_lint` setelah perubahan yang bermakna.
7. Aktifkan dasbor jika Anda menginginkan visibilitas stale/contradiction.

## Dokumen terkait

- [Ikhtisar Memori](/id/concepts/memory)
- [CLI: memory](/cli/memory)
- [CLI: wiki](/cli/wiki)
- [Ikhtisar SDK Plugin](/id/plugins/sdk-overview)
