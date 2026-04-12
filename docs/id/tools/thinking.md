---
read_when:
    - Menyesuaikan penguraian atau default directive thinking, fast-mode, atau verbose
summary: Sintaks directive untuk /think, /fast, /verbose, /trace, dan visibilitas reasoning
title: Tingkat Thinking
x-i18n:
    generated_at: "2026-04-12T23:33:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4f3b1341281f07ba4e9061e3355845dca234be04cc0d358594312beeb7676e68
    source_path: tools/thinking.md
    workflow: 15
---

# Tingkat Thinking (/think directives)

## Fungsinya

- Directive inline di body masuk mana pun: `/t <level>`, `/think:<level>`, atau `/thinking <level>`.
- Level (alias): `off | minimal | low | medium | high | xhigh | adaptive`
  - minimal → “think”
  - low → “think hard”
  - medium → “think harder”
  - high → “ultrathink” (anggaran maksimum)
  - xhigh → “ultrathink+” (khusus model GPT-5.2 + Codex)
  - adaptive → anggaran reasoning adaptif yang dikelola provider (didukung untuk keluarga model Anthropic Claude 4.6)
  - `x-high`, `x_high`, `extra-high`, `extra high`, dan `extra_high` dipetakan ke `xhigh`.
  - `highest`, `max` dipetakan ke `high`.
- Catatan provider:
  - Model Anthropic Claude 4.6 default ke `adaptive` saat tidak ada level thinking eksplisit yang disetel.
  - MiniMax (`minimax/*`) pada jalur streaming yang kompatibel dengan Anthropic default ke `thinking: { type: "disabled" }` kecuali Anda secara eksplisit menyetel thinking di param model atau param permintaan. Ini mencegah delta `reasoning_content` yang bocor dari format stream Anthropic non-native milik MiniMax.
  - Z.AI (`zai/*`) hanya mendukung thinking biner (`on`/`off`). Level apa pun selain `off` diperlakukan sebagai `on` (dipetakan ke `low`).
  - Moonshot (`moonshot/*`) memetakan `/think off` ke `thinking: { type: "disabled" }` dan level selain `off` ke `thinking: { type: "enabled" }`. Saat thinking diaktifkan, Moonshot hanya menerima `tool_choice` `auto|none`; OpenClaw menormalkan nilai yang tidak kompatibel ke `auto`.

## Urutan resolusi

1. Directive inline pada pesan (hanya berlaku untuk pesan itu).
2. Override sesi (diatur dengan mengirim pesan yang hanya berisi directive).
3. Default per agent (`agents.list[].thinkingDefault` di config).
4. Default global (`agents.defaults.thinkingDefault` di config).
5. Fallback: `adaptive` untuk model Anthropic Claude 4.6, `low` untuk model lain yang mendukung reasoning, `off` untuk selain itu.

## Menetapkan default sesi

- Kirim pesan yang **hanya** berisi directive (spasi diperbolehkan), misalnya `/think:medium` atau `/t high`.
- Ini akan menempel untuk sesi saat ini (default-nya per pengirim); dibersihkan oleh `/think:off` atau reset idle sesi.
- Balasan konfirmasi dikirim (`Thinking level set to high.` / `Thinking disabled.`). Jika level tidak valid (misalnya `/thinking big`), perintah ditolak dengan petunjuk dan state sesi dibiarkan tidak berubah.
- Kirim `/think` (atau `/think:`) tanpa argumen untuk melihat level thinking saat ini.

## Penerapan per agent

- **Pi tertanam**: level yang di-resolve diteruskan ke runtime agent Pi di dalam proses.

## Fast mode (/fast)

- Level: `on|off`.
- Pesan yang hanya berisi directive mengaktifkan/nonaktifkan override fast-mode sesi dan membalas `Fast mode enabled.` / `Fast mode disabled.`.
- Kirim `/fast` (atau `/fast status`) tanpa mode untuk melihat state fast-mode efektif saat ini.
- OpenClaw me-resolve fast mode dalam urutan berikut:
  1. `/fast on|off` inline/directive-only
  2. Override sesi
  3. Default per agent (`agents.list[].fastModeDefault`)
  4. Config per model: `agents.defaults.models["<provider>/<model>"].params.fastMode`
  5. Fallback: `off`
- Untuk `openai/*`, fast mode dipetakan ke pemrosesan prioritas OpenAI dengan mengirim `service_tier=priority` pada permintaan Responses yang didukung.
- Untuk `openai-codex/*`, fast mode mengirim flag `service_tier=priority` yang sama pada Codex Responses. OpenClaw mempertahankan satu toggle `/fast` bersama di kedua jalur auth.
- Untuk permintaan `anthropic/*` publik langsung, termasuk lalu lintas terautentikasi OAuth yang dikirim ke `api.anthropic.com`, fast mode dipetakan ke service tier Anthropic: `/fast on` menetapkan `service_tier=auto`, `/fast off` menetapkan `service_tier=standard_only`.
- Untuk `minimax/*` pada jalur yang kompatibel dengan Anthropic, `/fast on` (atau `params.fastMode: true`) menulis ulang `MiniMax-M2.7` menjadi `MiniMax-M2.7-highspeed`.
- Param model Anthropic `serviceTier` / `service_tier` yang eksplisit akan mengoverride default fast-mode saat keduanya disetel. OpenClaw tetap melewati injeksi service-tier Anthropic untuk base URL proxy non-Anthropic.

## Directive verbose (/verbose atau /v)

- Level: `on` (minimal) | `full` | `off` (default).
- Pesan yang hanya berisi directive mengaktifkan/nonaktifkan verbose sesi dan membalas `Verbose logging enabled.` / `Verbose logging disabled.`; level tidak valid mengembalikan petunjuk tanpa mengubah state.
- `/verbose off` menyimpan override sesi eksplisit; hapus melalui UI Sessions dengan memilih `inherit`.
- Directive inline hanya berlaku untuk pesan itu; default sesi/global berlaku di luar itu.
- Kirim `/verbose` (atau `/verbose:`) tanpa argumen untuk melihat level verbose saat ini.
- Saat verbose aktif, agent yang mengeluarkan hasil tool terstruktur (Pi, agent JSON lain) mengirim setiap pemanggilan tool kembali sebagai pesan khusus metadata tersendiri, diawali dengan `<emoji> <tool-name>: <arg>` bila tersedia (path/perintah). Ringkasan tool ini dikirim segera saat setiap tool dimulai (bubble terpisah), bukan sebagai delta streaming.
- Ringkasan kegagalan tool tetap terlihat dalam mode normal, tetapi sufiks detail error mentah disembunyikan kecuali verbose adalah `on` atau `full`.
- Saat verbose adalah `full`, output tool juga diteruskan setelah selesai (bubble terpisah, dipotong ke panjang yang aman). Jika Anda mengubah `/verbose on|full|off` saat eksekusi sedang berlangsung, bubble tool berikutnya akan mengikuti pengaturan baru.

## Directive trace Plugin (/trace)

- Level: `on` | `off` (default).
- Pesan yang hanya berisi directive mengaktifkan/nonaktifkan output trace Plugin sesi dan membalas `Plugin trace enabled.` / `Plugin trace disabled.`.
- Directive inline hanya berlaku untuk pesan itu; default sesi/global berlaku di luar itu.
- Kirim `/trace` (atau `/trace:`) tanpa argumen untuk melihat level trace saat ini.
- `/trace` lebih sempit daripada `/verbose`: ini hanya mengekspos baris trace/debug milik Plugin seperti ringkasan debug Active Memory.
- Baris trace dapat muncul di `/status` dan sebagai pesan diagnostik lanjutan setelah balasan asisten normal.

## Visibilitas reasoning (/reasoning)

- Level: `on|off|stream`.
- Pesan yang hanya berisi directive mengaktifkan/nonaktifkan apakah blok thinking ditampilkan dalam balasan.
- Saat diaktifkan, reasoning dikirim sebagai **pesan terpisah** yang diawali dengan `Reasoning:`.
- `stream` (khusus Telegram): men-stream reasoning ke bubble draft Telegram saat balasan sedang dibuat, lalu mengirim jawaban akhir tanpa reasoning.
- Alias: `/reason`.
- Kirim `/reasoning` (atau `/reasoning:`) tanpa argumen untuk melihat level reasoning saat ini.
- Urutan resolusi: directive inline, lalu override sesi, lalu default per agent (`agents.list[].reasoningDefault`), lalu fallback (`off`).

## Terkait

- Dokumen mode Elevated ada di [Mode Elevated](/id/tools/elevated).

## Heartbeat

- Body probe Heartbeat adalah prompt heartbeat yang dikonfigurasi (default: `Read HEARTBEAT.md if it exists (workspace context). Follow it strictly. Do not infer or repeat old tasks from prior chats. If nothing needs attention, reply HEARTBEAT_OK.`). Directive inline dalam pesan heartbeat berlaku seperti biasa (tetapi hindari mengubah default sesi dari Heartbeat).
- Pengiriman Heartbeat default ke payload akhir saja. Untuk juga mengirim pesan `Reasoning:` terpisah (bila tersedia), set `agents.defaults.heartbeat.includeReasoning: true` atau per-agent `agents.list[].heartbeat.includeReasoning: true`.

## UI chat web

- Pemilih thinking di UI chat web mencerminkan level tersimpan sesi dari penyimpanan/config sesi masuk saat halaman dimuat.
- Memilih level lain langsung menulis override sesi melalui `sessions.patch`; tidak menunggu pengiriman berikutnya dan bukan override `thinkingOnce` sekali pakai.
- Opsi pertama selalu `Default (<resolved level>)`, di mana default yang di-resolve berasal dari model sesi aktif: `adaptive` untuk Claude 4.6 di Anthropic/Bedrock, `low` untuk model lain yang mendukung reasoning, `off` untuk selain itu.
- Picker tetap sadar provider:
  - sebagian besar provider menampilkan `off | minimal | low | medium | high | adaptive`
  - Z.AI menampilkan biner `off | on`
- `/think:<level>` tetap berfungsi dan memperbarui level sesi tersimpan yang sama, sehingga directive chat dan picker tetap sinkron.
