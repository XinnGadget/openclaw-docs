---
read_when:
    - Anda sedang mengubah runtime agen tertanam atau registry harness
    - Anda sedang mendaftarkan harness agen dari plugin bawaan atau tepercaya
    - Anda perlu memahami bagaimana plugin Codex berhubungan dengan penyedia model
sidebarTitle: Agent Harness
summary: Permukaan SDK eksperimental untuk plugin yang menggantikan eksekutor agen tertanam tingkat rendah
title: Plugin Agent Harness
x-i18n:
    generated_at: "2026-04-12T00:18:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: 62b88fd24ce8b600179db27e16e8d764a2cd7a14e5c5df76374c33121aa5e365
    source_path: plugins/sdk-agent-harness.md
    workflow: 15
---

# Plugin Agent Harness

**Agent harness** adalah eksekutor tingkat rendah untuk satu giliran agen OpenClaw
yang sudah disiapkan. Ini bukan penyedia model, bukan channel, dan bukan registry tool.

Gunakan permukaan ini hanya untuk plugin native bawaan atau tepercaya. Kontrak ini
masih eksperimental karena tipe parameternya sengaja mencerminkan runner
tertanam saat ini.

## Kapan menggunakan harness

Daftarkan agent harness saat sebuah keluarga model memiliki runtime sesi native
sendiri dan transport penyedia OpenClaw normal adalah abstraksi yang salah.

Contoh:

- server agen pengodean native yang memiliki thread dan compaction
- CLI atau daemon lokal yang harus melakukan streaming event plan/reasoning/tool native
- runtime model yang memerlukan resume id sendiri selain transkrip sesi OpenClaw

Jangan mendaftarkan harness hanya untuk menambahkan API LLM baru. Untuk API model HTTP atau
WebSocket normal, bangun [plugin provider](/id/plugins/sdk-provider-plugins).

## Yang masih dimiliki core

Sebelum sebuah harness dipilih, OpenClaw sudah menyelesaikan:

- penyedia dan model
- status auth runtime
- tingkat berpikir dan anggaran konteks
- file transkrip/sesi OpenClaw
- workspace, sandbox, dan kebijakan tool
- callback balasan channel dan callback streaming
- kebijakan fallback model dan peralihan model live

Pemisahan itu disengaja. Sebuah harness menjalankan upaya yang sudah disiapkan;
ia tidak memilih penyedia, menggantikan pengiriman channel, atau diam-diam
mengganti model.

## Daftarkan harness

**Import:** `openclaw/plugin-sdk/agent-harness`

```typescript
import type { AgentHarness } from "openclaw/plugin-sdk/agent-harness";
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

const myHarness: AgentHarness = {
  id: "my-harness",
  label: "My native agent harness",

  supports(ctx) {
    return ctx.provider === "my-provider"
      ? { supported: true, priority: 100 }
      : { supported: false };
  },

  async runAttempt(params) {
    // Start or resume your native thread.
    // Use params.prompt, params.tools, params.images, params.onPartialReply,
    // params.onAgentEvent, and the other prepared attempt fields.
    return await runMyNativeTurn(params);
  },
};

export default definePluginEntry({
  id: "my-native-agent",
  name: "My Native Agent",
  description: "Runs selected models through a native agent daemon.",
  register(api) {
    api.registerAgentHarness(myHarness);
  },
});
```

## Kebijakan pemilihan

OpenClaw memilih harness setelah resolusi provider/model:

1. `OPENCLAW_AGENT_RUNTIME=<id>` memaksa harness terdaftar dengan id tersebut.
2. `OPENCLAW_AGENT_RUNTIME=pi` memaksa harness PI bawaan.
3. `OPENCLAW_AGENT_RUNTIME=auto` meminta harness terdaftar apakah mereka mendukung provider/model
   yang telah diselesaikan.
4. Jika tidak ada harness terdaftar yang cocok, OpenClaw menggunakan PI kecuali fallback PI
   dinonaktifkan.

Kegagalan harness plugin yang dipaksakan akan muncul sebagai kegagalan run. Dalam mode `auto`,
OpenClaw dapat fallback ke PI ketika harness plugin terpilih gagal sebelum sebuah
giliran menghasilkan efek samping. Tetapkan `OPENCLAW_AGENT_HARNESS_FALLBACK=none` atau
`embeddedHarness.fallback: "none"` agar fallback itu menjadi kegagalan keras.

Plugin Codex bawaan mendaftarkan `codex` sebagai harness id-nya. Core memperlakukan itu
sebagai id harness plugin biasa; alias khusus Codex harus berada di plugin
atau konfigurasi operator, bukan di selector runtime bersama.

## Pairing provider plus harness

Sebagian besar harness juga sebaiknya mendaftarkan provider. Provider membuat ref model,
status auth, metadata model, dan pemilihan `/model` terlihat oleh seluruh
OpenClaw. Harness kemudian mengklaim provider itu di `supports(...)`.

Plugin Codex bawaan mengikuti pola ini:

- provider id: `codex`
- ref model pengguna: `codex/gpt-5.4`, `codex/gpt-5.2`, atau model lain yang dikembalikan
  oleh server aplikasi Codex
- harness id: `codex`
- auth: ketersediaan provider sintetis, karena harness Codex memiliki
  login/sesi Codex native
- permintaan app-server: OpenClaw mengirim bare model id ke Codex dan membiarkan
  harness berbicara dengan protokol app-server native

Plugin Codex bersifat aditif. Ref `openai/gpt-*` biasa tetap menjadi ref provider OpenAI
dan terus menggunakan jalur provider OpenClaw normal. Pilih `codex/gpt-*`
saat Anda menginginkan auth yang dikelola Codex, penemuan model Codex, thread native, dan
eksekusi app-server Codex. `/model` dapat beralih di antara model Codex yang
dikembalikan oleh app-server Codex tanpa memerlukan kredensial provider OpenAI.

Untuk penyiapan operator, contoh prefiks model, dan konfigurasi khusus Codex, lihat
[Codex Harness](/id/plugins/codex-harness).

OpenClaw memerlukan app-server Codex `0.118.0` atau yang lebih baru. Plugin Codex memeriksa
initialize handshake app-server dan memblokir server yang lebih lama atau tanpa versi agar
OpenClaw hanya berjalan terhadap permukaan protokol yang telah diuji.

### Mode harness Codex native

Harness `codex` bawaan adalah mode Codex native untuk giliran agen OpenClaw
tertanam. Aktifkan plugin `codex` bawaan terlebih dahulu, dan sertakan `codex` di
`plugins.allow` jika konfigurasi Anda menggunakan allowlist yang ketat. Ini berbeda
dari `openai-codex/*`:

- `openai-codex/*` menggunakan OAuth ChatGPT/Codex melalui jalur provider OpenClaw normal.
- `codex/*` menggunakan provider Codex bawaan dan merutekan giliran melalui Codex
  app-server.

Saat mode ini berjalan, Codex memiliki thread id native, perilaku resume,
compaction, dan eksekusi app-server. OpenClaw tetap memiliki channel chat,
mirror transkrip yang terlihat, kebijakan tool, persetujuan, pengiriman media, dan
pemilihan sesi. Gunakan `embeddedHarness.runtime: "codex"` dengan
`embeddedHarness.fallback: "none"` saat Anda perlu membuktikan bahwa jalur
app-server Codex digunakan dan fallback PI tidak menyembunyikan harness native yang rusak.

## Nonaktifkan fallback PI

Secara default, OpenClaw menjalankan agen tertanam dengan `agents.defaults.embeddedHarness`
diatur ke `{ runtime: "auto", fallback: "pi" }`. Dalam mode `auto`, plugin
harness yang terdaftar dapat mengklaim pasangan provider/model. Jika tidak ada yang cocok,
atau jika harness plugin yang dipilih otomatis gagal sebelum menghasilkan output,
OpenClaw fallback ke PI.

Tetapkan `fallback: "none"` saat Anda perlu membuktikan bahwa harness plugin adalah satu-satunya
runtime yang sedang diuji. Ini menonaktifkan fallback PI otomatis; ini tidak memblokir
`runtime: "pi"` yang eksplisit atau `OPENCLAW_AGENT_RUNTIME=pi`.

Untuk run tertanam khusus Codex:

```json
{
  "agents": {
    "defaults": {
      "model": "codex/gpt-5.4",
      "embeddedHarness": {
        "runtime": "codex",
        "fallback": "none"
      }
    }
  }
}
```

Jika Anda ingin harness plugin terdaftar mana pun mengklaim model yang cocok tetapi tidak pernah
ingin OpenClaw diam-diam fallback ke PI, pertahankan `runtime: "auto"` dan nonaktifkan
fallback:

```json
{
  "agents": {
    "defaults": {
      "embeddedHarness": {
        "runtime": "auto",
        "fallback": "none"
      }
    }
  }
}
```

Override per agen menggunakan bentuk yang sama:

```json
{
  "agents": {
    "defaults": {
      "embeddedHarness": {
        "runtime": "auto",
        "fallback": "pi"
      }
    },
    "list": [
      {
        "id": "codex-only",
        "model": "codex/gpt-5.4",
        "embeddedHarness": {
          "runtime": "codex",
          "fallback": "none"
        }
      }
    ]
  }
}
```

`OPENCLAW_AGENT_RUNTIME` tetap menimpa runtime yang dikonfigurasi. Gunakan
`OPENCLAW_AGENT_HARNESS_FALLBACK=none` untuk menonaktifkan fallback PI dari
environment.

```bash
OPENCLAW_AGENT_RUNTIME=codex \
OPENCLAW_AGENT_HARNESS_FALLBACK=none \
openclaw gateway run
```

Dengan fallback dinonaktifkan, sebuah sesi gagal lebih awal saat harness yang diminta tidak
terdaftar, tidak mendukung provider/model yang telah diselesaikan, atau gagal sebelum
menghasilkan efek samping giliran. Ini disengaja untuk deployment khusus Codex dan
untuk live test yang harus membuktikan bahwa jalur app-server Codex benar-benar digunakan.

Pengaturan ini hanya mengontrol harness agen tertanam. Ini tidak menonaktifkan
perutean model khusus provider untuk gambar, video, musik, TTS, PDF, atau yang lainnya.

## Sesi native dan mirror transkrip

Sebuah harness dapat menyimpan session id native, thread id, atau token resume di sisi daemon.
Pertahankan pengikatan itu secara eksplisit terkait dengan sesi OpenClaw, dan tetap
mirror output asisten/tool yang terlihat oleh pengguna ke dalam transkrip OpenClaw.

Transkrip OpenClaw tetap menjadi lapisan kompatibilitas untuk:

- riwayat sesi yang terlihat di channel
- pencarian dan pengindeksan transkrip
- beralih kembali ke harness PI bawaan pada giliran berikutnya
- perilaku `/new`, `/reset`, dan penghapusan sesi generik

Jika harness Anda menyimpan sidecar binding, implementasikan `reset(...)` agar OpenClaw dapat
menghapusnya saat sesi OpenClaw pemilik di-reset.

## Hasil tool dan media

Core membangun daftar tool OpenClaw dan meneruskannya ke upaya yang sudah disiapkan.
Saat sebuah harness mengeksekusi pemanggilan tool dinamis, kembalikan hasil tool melalui
bentuk hasil harness alih-alih mengirim media channel sendiri.

Ini menjaga output teks, gambar, video, musik, TTS, persetujuan, dan tool perpesanan
tetap berada pada jalur pengiriman yang sama seperti run berbasis PI.

## Batasan saat ini

- Jalur import publik bersifat generik, tetapi beberapa alias tipe attempt/result masih
  membawa nama `Pi` demi kompatibilitas.
- Pemasangan harness pihak ketiga masih eksperimental. Utamakan plugin provider
  sampai Anda memerlukan runtime sesi native.
- Peralihan harness didukung antar giliran. Jangan mengganti harness di tengah
  giliran setelah tool native, persetujuan, teks asisten, atau pengiriman
  pesan telah dimulai.

## Terkait

- [Ikhtisar SDK](/id/plugins/sdk-overview)
- [Helper Runtime](/id/plugins/sdk-runtime)
- [Plugin Provider](/id/plugins/sdk-provider-plugins)
- [Codex Harness](/id/plugins/codex-harness)
- [Provider Model](/id/concepts/model-providers)
