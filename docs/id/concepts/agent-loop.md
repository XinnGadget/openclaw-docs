---
read_when:
    - Anda memerlukan panduan langkah demi langkah yang tepat tentang loop agen atau peristiwa siklus hidupnya
summary: Siklus hidup loop agen, aliran, dan semantik penantian
title: Loop Agen
x-i18n:
    generated_at: "2026-04-12T23:28:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3c2986708b444055340e0c91b8fce7d32225fcccf3d197b797665fd36b1991a5
    source_path: concepts/agent-loop.md
    workflow: 15
---

# Loop Agen (OpenClaw)

Loop agentik adalah keseluruhan proses “nyata” dari sebuah agen: intake → perakitan konteks → inferensi model →
eksekusi alat → balasan streaming → persistensi. Ini adalah jalur otoritatif yang mengubah sebuah pesan
menjadi tindakan dan balasan akhir, sambil menjaga status sesi tetap konsisten.

Di OpenClaw, sebuah loop adalah satu eksekusi terserialisasi per sesi yang memancarkan peristiwa lifecycle dan stream
saat model berpikir, memanggil alat, dan melakukan streaming output. Dokumen ini menjelaskan bagaimana loop autentik tersebut
terhubung dari ujung ke ujung.

## Titik masuk

- Gateway RPC: `agent` dan `agent.wait`.
- CLI: perintah `agent`.

## Cara kerjanya (tingkat tinggi)

1. RPC `agent` memvalidasi parameter, menyelesaikan sesi (sessionKey/sessionId), menyimpan metadata sesi, lalu segera mengembalikan `{ runId, acceptedAt }`.
2. `agentCommand` menjalankan agen:
   - menyelesaikan default model + thinking/verbose/trace
   - memuat snapshot Skills
   - memanggil `runEmbeddedPiAgent` (runtime pi-agent-core)
   - memancarkan **lifecycle end/error** jika loop tersemat tidak memancarkan salah satunya
3. `runEmbeddedPiAgent`:
   - menyerialkan eksekusi melalui antrean per sesi + global
   - menyelesaikan model + profil autentikasi dan membangun sesi pi
   - berlangganan ke peristiwa pi dan melakukan streaming delta assistant/alat
   - menerapkan timeout -> membatalkan eksekusi jika terlampaui
   - mengembalikan payload + metadata penggunaan
4. `subscribeEmbeddedPiSession` menjembatani peristiwa pi-agent-core ke stream `agent` OpenClaw:
   - peristiwa alat => `stream: "tool"`
   - delta assistant => `stream: "assistant"`
   - peristiwa lifecycle => `stream: "lifecycle"` (`phase: "start" | "end" | "error"`)
5. `agent.wait` menggunakan `waitForAgentRun`:
   - menunggu **lifecycle end/error** untuk `runId`
   - mengembalikan `{ status: ok|error|timeout, startedAt, endedAt, error? }`

## Antrean + konkurensi

- Eksekusi diserialkan per kunci sesi (jalur sesi) dan secara opsional melalui jalur global.
- Ini mencegah race pada alat/sesi dan menjaga riwayat sesi tetap konsisten.
- Channel perpesanan dapat memilih mode antrean (collect/steer/followup) yang memasok ke sistem jalur ini.
  Lihat [Command Queue](/id/concepts/queue).

## Persiapan sesi + workspace

- Workspace diselesaikan dan dibuat; eksekusi tersandbox dapat mengarahkan ulang ke root workspace sandbox.
- Skills dimuat (atau digunakan ulang dari snapshot) dan disuntikkan ke env serta prompt.
- Berkas bootstrap/konteks diselesaikan dan disuntikkan ke laporan system prompt.
- Kunci tulis sesi diambil; `SessionManager` dibuka dan disiapkan sebelum streaming.

## Perakitan prompt + system prompt

- System prompt dibangun dari prompt dasar OpenClaw, prompt Skills, konteks bootstrap, dan override per eksekusi.
- Batas khusus model dan token cadangan Compaction diterapkan.
- Lihat [System prompt](/id/concepts/system-prompt) untuk apa yang dilihat model.

## Titik hook (tempat Anda dapat melakukan intersepsi)

OpenClaw memiliki dua sistem hook:

- **Hook internal** (hook Gateway): skrip berbasis peristiwa untuk perintah dan peristiwa lifecycle.
- **Hook Plugin**: titik ekstensi di dalam lifecycle agen/alat dan pipeline gateway.

### Hook internal (hook Gateway)

- **`agent:bootstrap`**: berjalan saat membangun berkas bootstrap sebelum system prompt difinalkan.
  Gunakan ini untuk menambahkan/menghapus berkas konteks bootstrap.
- **Hook perintah**: `/new`, `/reset`, `/stop`, dan peristiwa perintah lainnya (lihat dokumen Hooks).

Lihat [Hooks](/id/automation/hooks) untuk penyiapan dan contoh.

### Hook Plugin (lifecycle agen + gateway)

Ini berjalan di dalam loop agen atau pipeline gateway:

- **`before_model_resolve`**: berjalan pra-sesi (tanpa `messages`) untuk menimpa provider/model secara deterministik sebelum penyelesaian model.
- **`before_prompt_build`**: berjalan setelah sesi dimuat (dengan `messages`) untuk menyuntikkan `prependContext`, `systemPrompt`, `prependSystemContext`, atau `appendSystemContext` sebelum pengiriman prompt. Gunakan `prependContext` untuk teks dinamis per giliran dan field system-context untuk panduan stabil yang seharusnya berada di ruang system prompt.
- **`before_agent_start`**: hook kompatibilitas lama yang dapat berjalan di salah satu fase; pilih hook eksplisit di atas.
- **`before_agent_reply`**: berjalan setelah tindakan inline dan sebelum pemanggilan LLM, memungkinkan Plugin mengklaim giliran dan mengembalikan balasan sintetis atau membisukan giliran sepenuhnya.
- **`agent_end`**: memeriksa daftar pesan akhir dan metadata eksekusi setelah selesai.
- **`before_compaction` / `after_compaction`**: mengamati atau memberi anotasi pada siklus Compaction.
- **`before_tool_call` / `after_tool_call`**: mengintersepsi parameter/hasil alat.
- **`before_install`**: memeriksa temuan pemindaian bawaan dan secara opsional memblokir instalasi skill atau Plugin.
- **`tool_result_persist`**: mentransformasikan hasil alat secara sinkron sebelum ditulis ke transkrip sesi.
- **`message_received` / `message_sending` / `message_sent`**: hook pesan masuk + keluar.
- **`session_start` / `session_end`**: batas lifecycle sesi.
- **`gateway_start` / `gateway_stop`**: peristiwa lifecycle gateway.

Aturan keputusan hook untuk guard alat/keluar:

- `before_tool_call`: `{ block: true }` bersifat terminal dan menghentikan handler prioritas lebih rendah.
- `before_tool_call`: `{ block: false }` adalah no-op dan tidak menghapus blok sebelumnya.
- `before_install`: `{ block: true }` bersifat terminal dan menghentikan handler prioritas lebih rendah.
- `before_install`: `{ block: false }` adalah no-op dan tidak menghapus blok sebelumnya.
- `message_sending`: `{ cancel: true }` bersifat terminal dan menghentikan handler prioritas lebih rendah.
- `message_sending`: `{ cancel: false }` adalah no-op dan tidak menghapus pembatalan sebelumnya.

Lihat [Plugin hooks](/id/plugins/architecture#provider-runtime-hooks) untuk API hook dan detail pendaftaran.

## Streaming + balasan parsial

- Delta assistant di-streaming dari pi-agent-core dan dipancarkan sebagai peristiwa `assistant`.
- Streaming blok dapat memancarkan balasan parsial baik pada `text_end` maupun `message_end`.
- Streaming penalaran dapat dipancarkan sebagai stream terpisah atau sebagai balasan blok.
- Lihat [Streaming](/id/concepts/streaming) untuk perilaku chunking dan balasan blok.

## Eksekusi alat + alat perpesanan

- Peristiwa start/update/end alat dipancarkan pada stream `tool`.
- Hasil alat disanitasi untuk ukuran dan payload gambar sebelum dicatat/dipancarkan.
- Pengiriman alat perpesanan dilacak untuk menekan konfirmasi assistant yang duplikat.

## Pembentukan balasan + penekanan

- Payload akhir dirakit dari:
  - teks assistant (dan penalaran opsional)
  - ringkasan alat inline (saat verbose + diizinkan)
  - teks galat assistant saat model mengalami galat
- Token senyap persis `NO_REPLY` / `no_reply` disaring dari
  payload keluar.
- Duplikat alat perpesanan dihapus dari daftar payload akhir.
- Jika tidak ada payload yang dapat dirender tersisa dan sebuah alat mengalami galat, balasan galat alat fallback dipancarkan
  (kecuali alat perpesanan sudah mengirim balasan yang terlihat oleh pengguna).

## Compaction + percobaan ulang

- Compaction otomatis memancarkan peristiwa stream `compaction` dan dapat memicu percobaan ulang.
- Saat percobaan ulang, buffer dalam memori dan ringkasan alat direset untuk menghindari output duplikat.
- Lihat [Compaction](/id/concepts/compaction) untuk pipeline Compaction.

## Stream peristiwa (saat ini)

- `lifecycle`: dipancarkan oleh `subscribeEmbeddedPiSession` (dan sebagai fallback oleh `agentCommand`)
- `assistant`: delta streaming dari pi-agent-core
- `tool`: peristiwa alat streaming dari pi-agent-core

## Penanganan channel chat

- Delta assistant dibuffer menjadi pesan chat `delta`.
- `final` chat dipancarkan pada **lifecycle end/error**.

## Timeout

- Default `agent.wait`: 30 dtk (hanya penantian). Parameter `timeoutMs` menimpa.
- Runtime agen: default `agents.defaults.timeoutSeconds` 172800 dtk (48 jam); diterapkan di timer pembatalan `runEmbeddedPiAgent`.
- Timeout idle LLM: `agents.defaults.llm.idleTimeoutSeconds` membatalkan permintaan model ketika tidak ada chunk respons yang tiba sebelum jendela idle berakhir. Tetapkan secara eksplisit untuk model lokal lambat atau provider penalaran/pemanggilan alat; setel ke 0 untuk menonaktifkan. Jika tidak disetel, OpenClaw menggunakan `agents.defaults.timeoutSeconds` saat dikonfigurasi, jika tidak 120 dtk. Eksekusi yang dipicu Cron tanpa timeout LLM atau agen eksplisit akan menonaktifkan watchdog idle dan mengandalkan timeout luar Cron.

## Tempat hal-hal dapat berakhir lebih awal

- Timeout agen (abort)
- AbortSignal (batal)
- Gateway terputus atau timeout RPC
- Timeout `agent.wait` (hanya penantian, tidak menghentikan agen)

## Terkait

- [Tools](/id/tools) — alat agen yang tersedia
- [Hooks](/id/automation/hooks) — skrip berbasis peristiwa yang dipicu oleh peristiwa lifecycle agen
- [Compaction](/id/concepts/compaction) — bagaimana percakapan panjang diringkas
- [Exec Approvals](/id/tools/exec-approvals) — gerbang persetujuan untuk perintah shell
- [Thinking](/id/tools/thinking) — konfigurasi tingkat thinking/penalaran
