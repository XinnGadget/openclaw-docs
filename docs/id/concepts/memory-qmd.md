---
read_when:
    - Anda ingin menyiapkan QMD sebagai backend memori Anda
    - Anda menginginkan fitur memori lanjutan seperti reranking atau jalur yang diindeks tambahan
summary: Sidecar pencarian local-first dengan BM25, vektor, reranking, dan ekspansi kueri
title: Mesin Memori QMD
x-i18n:
    generated_at: "2026-04-12T23:28:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: 27afc996b959d71caed964a3cae437e0e29721728b30ebe7f014db124c88da04
    source_path: concepts/memory-qmd.md
    workflow: 15
---

# Mesin Memori QMD

[QMD](https://github.com/tobi/qmd) adalah sidecar pencarian local-first yang berjalan
berdampingan dengan OpenClaw. Ini menggabungkan BM25, pencarian vektor, dan reranking dalam satu
biner, dan dapat mengindeks konten di luar file memori workspace Anda.

## Apa yang ditambahkan dibandingkan bawaan

- **Reranking dan ekspansi kueri** untuk recall yang lebih baik.
- **Mengindeks direktori tambahan** -- dokumentasi proyek, catatan tim, apa pun di disk.
- **Mengindeks transkrip sesi** -- mengingat percakapan sebelumnya.
- **Sepenuhnya lokal** -- berjalan melalui Bun + node-llama-cpp, otomatis mengunduh model GGUF.
- **Fallback otomatis** -- jika QMD tidak tersedia, OpenClaw kembali ke
  mesin bawaan tanpa hambatan.

## Memulai

### Prasyarat

- Instal QMD: `npm install -g @tobilu/qmd` atau `bun install -g @tobilu/qmd`
- Build SQLite yang mengizinkan ekstensi (`brew install sqlite` di macOS).
- QMD harus ada di `PATH` milik Gateway.
- macOS dan Linux berfungsi langsung. Windows paling didukung melalui WSL2.

### Aktifkan

```json5
{
  memory: {
    backend: "qmd",
  },
}
```

OpenClaw membuat home QMD mandiri di bawah
`~/.openclaw/agents/<agentId>/qmd/` dan mengelola siklus hidup sidecar
secara otomatis -- koleksi, pembaruan, dan proses embedding ditangani untuk Anda.
Ini mengutamakan bentuk koleksi QMD dan kueri MCP saat ini, tetapi tetap kembali ke
flag koleksi `--mask` lama dan nama tool MCP yang lebih lama bila diperlukan.

## Cara kerja sidecar

- OpenClaw membuat koleksi dari file memori workspace Anda dan semua
  `memory.qmd.paths` yang dikonfigurasi, lalu menjalankan `qmd update` + `qmd embed` saat boot
  dan secara berkala (default setiap 5 menit).
- Koleksi workspace default melacak `MEMORY.md` plus tree `memory/`.
  `memory.md` huruf kecil tetap menjadi fallback bootstrap, bukan koleksi QMD
  terpisah.
- Refresh saat boot berjalan di latar belakang agar startup chat tidak terhambat.
- Pencarian menggunakan `searchMode` yang dikonfigurasi (default: `search`; juga mendukung
  `vsearch` dan `query`). Jika suatu mode gagal, OpenClaw mencoba lagi dengan `qmd query`.
- Jika QMD gagal sepenuhnya, OpenClaw kembali ke mesin SQLite bawaan.

<Info>
Pencarian pertama mungkin lambat -- QMD otomatis mengunduh model GGUF (~2 GB) untuk
reranking dan ekspansi kueri pada eksekusi pertama `qmd query`.
</Info>

## Override model

Variabel environment model QMD diteruskan tanpa perubahan dari proses Gateway,
jadi Anda dapat menyesuaikan QMD secara global tanpa menambahkan config OpenClaw baru:

```bash
export QMD_EMBED_MODEL="hf:Qwen/Qwen3-Embedding-0.6B-GGUF/Qwen3-Embedding-0.6B-Q8_0.gguf"
export QMD_RERANK_MODEL="/absolute/path/to/reranker.gguf"
export QMD_GENERATE_MODEL="/absolute/path/to/generator.gguf"
```

Setelah mengubah model embedding, jalankan ulang embedding agar indeks sesuai dengan
ruang vektor yang baru.

## Mengindeks jalur tambahan

Arahkan QMD ke direktori tambahan agar dapat dicari:

```json5
{
  memory: {
    backend: "qmd",
    qmd: {
      paths: [{ name: "docs", path: "~/notes", pattern: "**/*.md" }],
    },
  },
}
```

Cuplikan dari jalur tambahan muncul sebagai `qmd/<collection>/<relative-path>` di
hasil pencarian. `memory_get` memahami prefiks ini dan membaca dari root
koleksi yang benar.

## Mengindeks transkrip sesi

Aktifkan pengindeksan sesi untuk mengingat percakapan sebelumnya:

```json5
{
  memory: {
    backend: "qmd",
    qmd: {
      sessions: { enabled: true },
    },
  },
}
```

Transkrip diekspor sebagai giliran User/Assistant yang disanitasi ke koleksi QMD
khusus di bawah `~/.openclaw/agents/<id>/qmd/sessions/`.

## Cakupan pencarian

Secara default, hasil pencarian QMD ditampilkan dalam sesi langsung dan channel
(bukan grup). Konfigurasikan `memory.qmd.scope` untuk mengubahnya:

```json5
{
  memory: {
    qmd: {
      scope: {
        default: "deny",
        rules: [{ action: "allow", match: { chatType: "direct" } }],
      },
    },
  },
}
```

Ketika cakupan menolak pencarian, OpenClaw mencatat peringatan dengan channel turunan dan
jenis chat agar hasil kosong lebih mudah di-debug.

## Sitasi

Saat `memory.citations` bernilai `auto` atau `on`, cuplikan pencarian menyertakan
footer `Source: <path#line>`. Setel `memory.citations = "off"` untuk menghilangkan footer
sambil tetap meneruskan jalur ke agen secara internal.

## Kapan digunakan

Pilih QMD ketika Anda memerlukan:

- Reranking untuk hasil berkualitas lebih tinggi.
- Mencari dokumentasi proyek atau catatan di luar workspace.
- Mengingat percakapan sesi sebelumnya.
- Pencarian sepenuhnya lokal tanpa API key.

Untuk pengaturan yang lebih sederhana, [mesin bawaan](/id/concepts/memory-builtin) bekerja dengan baik
tanpa dependensi tambahan.

## Pemecahan masalah

**QMD tidak ditemukan?** Pastikan biner ada di `PATH` milik Gateway. Jika OpenClaw
berjalan sebagai layanan, buat symlink:
`sudo ln -s ~/.bun/bin/qmd /usr/local/bin/qmd`.

**Pencarian pertama sangat lambat?** QMD mengunduh model GGUF saat pertama kali digunakan. Lakukan pre-warm
dengan `qmd query "test"` menggunakan direktori XDG yang sama seperti yang digunakan OpenClaw.

**Pencarian timeout?** Tingkatkan `memory.qmd.limits.timeoutMs` (default: 4000ms).
Setel ke `120000` untuk hardware yang lebih lambat.

**Hasil kosong di chat grup?** Periksa `memory.qmd.scope` -- default hanya
mengizinkan sesi langsung dan channel.

**Repo sementara yang terlihat dari workspace menyebabkan `ENAMETOOLONG` atau pengindeksan rusak?**
Traversal QMD saat ini mengikuti perilaku pemindai QMD yang mendasarinya, bukan
aturan symlink bawaan OpenClaw. Simpan checkout monorepo sementara di bawah
direktori tersembunyi seperti `.tmp/` atau di luar root QMD yang diindeks sampai QMD menyediakan
traversal aman-siklus atau kontrol pengecualian yang eksplisit.

## Konfigurasi

Untuk seluruh permukaan config (`memory.qmd.*`), mode pencarian, interval pembaruan,
aturan cakupan, dan semua knob lainnya, lihat
[Referensi konfigurasi memori](/id/reference/memory-config).
