---
read_when:
    - Anda ingin memahami apa arti “konteks” di OpenClaw
    - Anda sedang men-debug mengapa model “mengetahui” sesuatu (atau melupakannya)
    - Anda ingin mengurangi overhead konteks (`/context`, `/status`, `/compact`)
summary: 'Konteks: apa yang dilihat model, bagaimana model dibangun, dan cara memeriksanya'
title: Konteks
x-i18n:
    generated_at: "2026-04-12T23:28:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3620db1a8c1956d91a01328966df491388d3a32c4003dc4447197eb34316c77d
    source_path: concepts/context.md
    workflow: 15
---

# Konteks

“Konteks” adalah **segala hal yang OpenClaw kirim ke model untuk suatu eksekusi**. Konteks dibatasi oleh **jendela konteks** model (batas token).

Model mental untuk pemula:

- **System prompt** (dibangun oleh OpenClaw): aturan, tools, daftar skills, waktu/runtime, dan file workspace yang disuntikkan.
- **Riwayat percakapan**: pesan Anda + pesan asisten untuk sesi ini.
- **Panggilan/hasil tool + lampiran**: output perintah, pembacaan file, gambar/audio, dan sebagainya.

Konteks _tidak sama_ dengan “memory”: memory dapat disimpan di disk dan dimuat ulang nanti; konteks adalah apa yang ada di dalam jendela model saat ini.

## Mulai cepat (memeriksa konteks)

- `/status` → tampilan cepat “seberapa penuh jendela saya?” + pengaturan sesi.
- `/context list` → apa saja yang disuntikkan + perkiraan ukuran (per file + total).
- `/context detail` → rincian yang lebih dalam: per file, ukuran skema per-tool, ukuran entri per-skill, dan ukuran system prompt.
- `/usage tokens` → tambahkan footer penggunaan per-balasan ke balasan normal.
- `/compact` → ringkas riwayat lama menjadi entri ringkas untuk membebaskan ruang jendela.

Lihat juga: [Perintah slash](/id/tools/slash-commands), [Penggunaan token & biaya](/id/reference/token-use), [Compaction](/id/concepts/compaction).

## Contoh output

Nilai bervariasi menurut model, provider, kebijakan tool, dan apa yang ada di workspace Anda.

### `/context list`

```
🧠 Rincian konteks
Workspace: <workspaceDir>
Maks bootstrap/file: 20,000 karakter
Sandbox: mode=non-main sandboxed=false
System prompt (eksekusi): 38,412 karakter (~9,603 token) (Konteks Proyek 23,901 karakter (~5,976 token))

File workspace yang disuntikkan:
- AGENTS.md: OK | mentah 1,742 karakter (~436 token) | disuntikkan 1,742 karakter (~436 token)
- SOUL.md: OK | mentah 912 karakter (~228 token) | disuntikkan 912 karakter (~228 token)
- TOOLS.md: DIPOTONG | mentah 54,210 karakter (~13,553 token) | disuntikkan 20,962 karakter (~5,241 token)
- IDENTITY.md: OK | mentah 211 karakter (~53 token) | disuntikkan 211 karakter (~53 token)
- USER.md: OK | mentah 388 karakter (~97 token) | disuntikkan 388 karakter (~97 token)
- HEARTBEAT.md: TIDAK DITEMUKAN | mentah 0 | disuntikkan 0
- BOOTSTRAP.md: OK | mentah 0 karakter (~0 token) | disuntikkan 0 karakter (~0 token)

Daftar skills (teks system prompt): 2,184 karakter (~546 token) (12 skills)
Tools: read, edit, write, exec, process, browser, message, sessions_send, …
Daftar tool (teks system prompt): 1,032 karakter (~258 token)
Skema tool (JSON): 31,988 karakter (~7,997 token) (dihitung ke dalam konteks; tidak ditampilkan sebagai teks)
Tools: (sama seperti di atas)

Token sesi (cache): total 14,250 / ctx=32,000
```

### `/context detail`

```
🧠 Rincian konteks (detail)
…
Skills teratas (ukuran entri prompt):
- frontend-design: 412 karakter (~103 token)
- oracle: 401 karakter (~101 token)
… (+10 skill lainnya)

Tools teratas (ukuran skema):
- browser: 9,812 karakter (~2,453 token)
- exec: 6,240 karakter (~1,560 token)
… (+N lainnya)
```

## Apa yang dihitung terhadap jendela konteks

Segala yang diterima model dihitung, termasuk:

- System prompt (semua bagian).
- Riwayat percakapan.
- Panggilan tool + hasil tool.
- Lampiran/transkrip (gambar/audio/file).
- Ringkasan compaction dan artefak pruning.
- “Wrapper” provider atau header tersembunyi (tidak terlihat, tetap dihitung).

## Cara OpenClaw membangun system prompt

System prompt adalah milik **OpenClaw** dan dibangun ulang setiap eksekusi. Isinya mencakup:

- Daftar tool + deskripsi singkat.
- Daftar skills (metadata saja; lihat di bawah).
- Lokasi workspace.
- Waktu (UTC + waktu pengguna yang dikonversi jika dikonfigurasi).
- Metadata runtime (host/OS/model/thinking).
- File bootstrap workspace yang disuntikkan di bawah **Konteks Proyek**.

Rincian lengkap: [System Prompt](/id/concepts/system-prompt).

## File workspace yang disuntikkan (Konteks Proyek)

Secara default, OpenClaw menyuntikkan sekumpulan file workspace tetap (jika ada):

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md` (hanya saat pertama kali dijalankan)

File besar dipotong per file menggunakan `agents.defaults.bootstrapMaxChars` (default `20000` karakter). OpenClaw juga menerapkan batas total injeksi bootstrap di seluruh file dengan `agents.defaults.bootstrapTotalMaxChars` (default `150000` karakter). `/context` menampilkan ukuran **mentah vs yang disuntikkan** dan apakah pemotongan terjadi.

Saat pemotongan terjadi, runtime dapat menyuntikkan blok peringatan di dalam prompt di bawah Konteks Proyek. Konfigurasikan ini dengan `agents.defaults.bootstrapPromptTruncationWarning` (`off`, `once`, `always`; default `once`).

## Skills: disuntikkan vs dimuat sesuai permintaan

System prompt menyertakan **daftar skills** yang ringkas (nama + deskripsi + lokasi). Daftar ini memiliki overhead nyata.

Instruksi skill _tidak_ disertakan secara default. Model diharapkan melakukan `read` pada `SKILL.md` milik skill **hanya saat diperlukan**.

## Tools: ada dua biaya

Tools memengaruhi konteks dalam dua cara:

1. **Teks daftar tool** di system prompt (yang Anda lihat sebagai “Tooling”).
2. **Skema tool** (JSON). Ini dikirim ke model agar model dapat memanggil tools. Semuanya dihitung ke dalam konteks meskipun Anda tidak melihatnya sebagai teks biasa.

`/context detail` merinci skema tool terbesar agar Anda dapat melihat apa yang paling mendominasi.

## Perintah, directive, dan "inline shortcuts"

Perintah slash ditangani oleh Gateway. Ada beberapa perilaku yang berbeda:

- **Perintah mandiri**: pesan yang hanya berisi `/...` dijalankan sebagai perintah.
- **Directive**: `/think`, `/verbose`, `/trace`, `/reasoning`, `/elevated`, `/model`, `/queue` dihapus sebelum model melihat pesan.
  - Pesan yang hanya berisi directive akan menyimpan pengaturan sesi.
  - Directive inline di dalam pesan normal bertindak sebagai petunjuk per pesan.
- **Inline shortcuts** (hanya pengirim yang ada dalam allowlist): token `/...` tertentu di dalam pesan normal dapat langsung dijalankan (contoh: “hey /status”), lalu dihapus sebelum model melihat sisa teks.

Detail: [Perintah slash](/id/tools/slash-commands).

## Sesi, compaction, dan pruning (apa yang dipertahankan)

Apa yang dipertahankan di antara pesan bergantung pada mekanismenya:

- **Riwayat normal** dipertahankan dalam transkrip sesi sampai di-compact/di-prune oleh kebijakan.
- **Compaction** mempertahankan ringkasan ke dalam transkrip dan menjaga pesan terbaru tetap utuh.
- **Pruning** menghapus hasil tool lama dari prompt _dalam memori_ untuk suatu eksekusi, tetapi tidak menulis ulang transkrip.

Dokumentasi: [Sesi](/id/concepts/session), [Compaction](/id/concepts/compaction), [Session pruning](/id/concepts/session-pruning).

Secara default, OpenClaw menggunakan context engine bawaan `legacy` untuk perakitan dan
compaction. Jika Anda memasang Plugin yang menyediakan `kind: "context-engine"` dan
memilihnya dengan `plugins.slots.contextEngine`, OpenClaw akan mendelegasikan perakitan konteks,
`/compact`, dan hook siklus hidup konteks subagent terkait ke
engine tersebut. `ownsCompaction: false` tidak otomatis kembali ke
engine legacy; engine aktif tetap harus mengimplementasikan `compact()` dengan benar. Lihat
[Context Engine](/id/concepts/context-engine) untuk
antarmuka pluggable lengkap, hook siklus hidup, dan konfigurasinya.

## Apa yang sebenarnya dilaporkan `/context`

`/context` mengutamakan laporan system prompt **yang dibangun saat eksekusi** terbaru jika tersedia:

- `System prompt (run)` = diambil dari eksekusi embedded (mampu menggunakan tool) terakhir dan disimpan di session store.
- `System prompt (estimate)` = dihitung saat itu juga ketika belum ada laporan eksekusi (atau saat dijalankan melalui backend CLI yang tidak menghasilkan laporan tersebut).

Dalam kedua kasus, ini melaporkan ukuran dan kontributor teratas; ini **tidak** menampilkan seluruh system prompt atau skema tool.

## Terkait

- [Context Engine](/id/concepts/context-engine) — injeksi konteks kustom melalui plugin
- [Compaction](/id/concepts/compaction) — meringkas percakapan panjang
- [System Prompt](/id/concepts/system-prompt) — cara system prompt dibangun
- [Agent Loop](/id/concepts/agent-loop) — siklus eksekusi agen secara lengkap
