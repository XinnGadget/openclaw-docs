---
read_when:
    - Menyiapkan OpenClaw untuk pertama kalinya
    - Mencari pola konfigurasi umum
    - Menavigasi ke bagian konfigurasi tertentu
summary: 'Ikhtisar konfigurasi: tugas umum, penyiapan cepat, dan tautan ke referensi lengkap'
title: Konfigurasi
x-i18n:
    generated_at: "2026-04-08T06:01:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: 199a1e515bd4003319e71593a2659bb883299a76ff67e273d92583df03c96604
    source_path: gateway/configuration.md
    workflow: 15
---

# Konfigurasi

OpenClaw membaca config <Tooltip tip="JSON5 mendukung komentar dan koma di akhir">**JSON5**</Tooltip> opsional dari `~/.openclaw/openclaw.json`.

Jika file tidak ada, OpenClaw menggunakan default yang aman. Alasan umum untuk menambahkan config:

- Menghubungkan channel dan mengontrol siapa yang dapat mengirim pesan ke bot
- Menetapkan model, alat, sandboxing, atau otomatisasi (cron, hook)
- Menyesuaikan sesi, media, jaringan, atau UI

Lihat [referensi lengkap](/id/gateway/configuration-reference) untuk setiap field yang tersedia.

<Tip>
**Baru mengenal konfigurasi?** Mulailah dengan `openclaw onboard` untuk penyiapan interaktif, atau lihat panduan [Contoh Konfigurasi](/id/gateway/configuration-examples) untuk config lengkap yang bisa langsung disalin-tempel.
</Tip>

## Config minimal

```json5
// ~/.openclaw/openclaw.json
{
  agents: { defaults: { workspace: "~/.openclaw/workspace" } },
  channels: { whatsapp: { allowFrom: ["+15555550123"] } },
}
```

## Mengedit config

<Tabs>
  <Tab title="Wizard interaktif">
    ```bash
    openclaw onboard       # alur onboarding lengkap
    openclaw configure     # wizard config
    ```
  </Tab>
  <Tab title="CLI (satu baris)">
    ```bash
    openclaw config get agents.defaults.workspace
    openclaw config set agents.defaults.heartbeat.every "2h"
    openclaw config unset plugins.entries.brave.config.webSearch.apiKey
    ```
  </Tab>
  <Tab title="Control UI">
    Buka [http://127.0.0.1:18789](http://127.0.0.1:18789) dan gunakan tab **Config**.
    Control UI merender formulir dari skema config aktif, termasuk metadata docs
    `title` / `description` field serta skema plugin dan channel jika tersedia,
    dengan editor **Raw JSON** sebagai jalan keluar. Untuk UI penelusuran mendalam
    dan alat lainnya, gateway juga mengekspos `config.schema.lookup` untuk
    mengambil satu node skema dengan cakupan path beserta ringkasan turunan langsung.
  </Tab>
  <Tab title="Edit langsung">
    Edit `~/.openclaw/openclaw.json` secara langsung. Gateway memantau file tersebut dan menerapkan perubahan secara otomatis (lihat [hot reload](#config-hot-reload)).
  </Tab>
</Tabs>

## Validasi ketat

<Warning>
OpenClaw hanya menerima konfigurasi yang sepenuhnya cocok dengan skema. Key yang tidak dikenal, tipe yang salah format, atau nilai yang tidak valid akan membuat Gateway **menolak untuk memulai**. Satu-satunya pengecualian di level root adalah `$schema` (string), agar editor dapat melampirkan metadata JSON Schema.
</Warning>

Catatan alat skema:

- `openclaw config schema` mencetak keluarga JSON Schema yang sama yang digunakan oleh Control UI
  dan validasi config.
- Perlakukan keluaran skema tersebut sebagai kontrak kanonis yang dapat dibaca mesin untuk
  `openclaw.json`; ikhtisar ini dan referensi konfigurasi merangkumnya.
- Nilai `title` dan `description` field dibawa ke keluaran skema untuk
  alat editor dan formulir.
- Entri objek bertingkat, wildcard (`*`), dan item array (`[]`) mewarisi metadata docs yang sama
  ketika dokumentasi field yang cocok tersedia.
- Cabang komposisi `anyOf` / `oneOf` / `allOf` juga mewarisi metadata docs
  yang sama, sehingga varian union/intersection tetap memiliki bantuan field yang sama.
- `config.schema.lookup` mengembalikan satu path config yang dinormalisasi dengan node skema
  dangkal (`title`, `description`, `type`, `enum`, `const`, batas umum,
  dan field validasi serupa), metadata petunjuk UI yang cocok, dan ringkasan turunan langsung
  untuk alat penelusuran mendalam.
- Skema plugin/channel runtime digabungkan ketika gateway dapat memuat
  registri manifes saat ini.
- `pnpm config:docs:check` mendeteksi ketidaksesuaian antara artefak baseline config
  yang berhadapan dengan docs dan permukaan skema saat ini.

Saat validasi gagal:

- Gateway tidak akan berjalan
- Hanya perintah diagnostik yang berfungsi (`openclaw doctor`, `openclaw logs`, `openclaw health`, `openclaw status`)
- Jalankan `openclaw doctor` untuk melihat masalah yang tepat
- Jalankan `openclaw doctor --fix` (atau `--yes`) untuk menerapkan perbaikan

## Tugas umum

<AccordionGroup>
  <Accordion title="Siapkan channel (WhatsApp, Telegram, Discord, dll.)">
    Setiap channel memiliki bagian config sendiri di bawah `channels.<provider>`. Lihat halaman channel khusus untuk langkah penyiapan:

    - [WhatsApp](/id/channels/whatsapp) — `channels.whatsapp`
    - [Telegram](/id/channels/telegram) — `channels.telegram`
    - [Discord](/id/channels/discord) — `channels.discord`
    - [Feishu](/id/channels/feishu) — `channels.feishu`
    - [Google Chat](/id/channels/googlechat) — `channels.googlechat`
    - [Microsoft Teams](/id/channels/msteams) — `channels.msteams`
    - [Slack](/id/channels/slack) — `channels.slack`
    - [Signal](/id/channels/signal) — `channels.signal`
    - [iMessage](/id/channels/imessage) — `channels.imessage`
    - [Mattermost](/id/channels/mattermost) — `channels.mattermost`

    Semua channel berbagi pola kebijakan DM yang sama:

    ```json5
    {
      channels: {
        telegram: {
          enabled: true,
          botToken: "123:abc",
          dmPolicy: "pairing",   // pairing | allowlist | open | disabled
          allowFrom: ["tg:123"], // only for allowlist/open
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Pilih dan konfigurasikan model">
    Tetapkan model utama dan fallback opsional:

    ```json5
    {
      agents: {
        defaults: {
          model: {
            primary: "anthropic/claude-sonnet-4-6",
            fallbacks: ["openai/gpt-5.4"],
          },
          models: {
            "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
            "openai/gpt-5.4": { alias: "GPT" },
          },
        },
      },
    }
    ```

    - `agents.defaults.models` mendefinisikan katalog model dan berfungsi sebagai allowlist untuk `/model`.
    - Referensi model menggunakan format `provider/model` (misalnya `anthropic/claude-opus-4-6`).
    - `agents.defaults.imageMaxDimensionPx` mengontrol downscaling gambar transkrip/alat (default `1200`); nilai yang lebih rendah biasanya mengurangi penggunaan vision-token pada proses yang banyak screenshot.
    - Lihat [Models CLI](/id/concepts/models) untuk mengganti model di chat dan [Model Failover](/id/concepts/model-failover) untuk rotasi auth dan perilaku fallback.
    - Untuk provider kustom/self-hosted, lihat [Custom providers](/id/gateway/configuration-reference#custom-providers-and-base-urls) di referensi.

  </Accordion>

  <Accordion title="Kontrol siapa yang dapat mengirim pesan ke bot">
    Akses DM dikontrol per channel melalui `dmPolicy`:

    - `"pairing"` (default): pengirim yang tidak dikenal mendapatkan kode pairing sekali pakai untuk persetujuan
    - `"allowlist"`: hanya pengirim di `allowFrom` (atau penyimpanan izin hasil pairing)
    - `"open"`: izinkan semua DM masuk (memerlukan `allowFrom: ["*"]`)
    - `"disabled"`: abaikan semua DM

    Untuk grup, gunakan `groupPolicy` + `groupAllowFrom` atau allowlist khusus channel.

    Lihat [referensi lengkap](/id/gateway/configuration-reference#dm-and-group-access) untuk detail per channel.

  </Accordion>

  <Accordion title="Siapkan penyaringan mention untuk chat grup">
    Pesan grup secara default **memerlukan mention**. Konfigurasikan pola per agen:

    ```json5
    {
      agents: {
        list: [
          {
            id: "main",
            groupChat: {
              mentionPatterns: ["@openclaw", "openclaw"],
            },
          },
        ],
      },
      channels: {
        whatsapp: {
          groups: { "*": { requireMention: true } },
        },
      },
    }
    ```

    - **Metadata mentions**: @-mention native (WhatsApp tap-to-mention, Telegram @bot, dll.)
    - **Pola teks**: pola regex aman di `mentionPatterns`
    - Lihat [referensi lengkap](/id/gateway/configuration-reference#group-chat-mention-gating) untuk override per channel dan mode chat dengan diri sendiri.

  </Accordion>

  <Accordion title="Batasi Skills per agen">
    Gunakan `agents.defaults.skills` untuk baseline bersama, lalu override agen tertentu dengan `agents.list[].skills`:

    ```json5
    {
      agents: {
        defaults: {
          skills: ["github", "weather"],
        },
        list: [
          { id: "writer" }, // inherits github, weather
          { id: "docs", skills: ["docs-search"] }, // replaces defaults
          { id: "locked-down", skills: [] }, // no skills
        ],
      },
    }
    ```

    - Hilangkan `agents.defaults.skills` agar Skills tidak dibatasi secara default.
    - Hilangkan `agents.list[].skills` untuk mewarisi default.
    - Tetapkan `agents.list[].skills: []` agar tidak ada Skills.
    - Lihat [Skills](/id/tools/skills), [Skills config](/id/tools/skills-config), dan
      [Configuration Reference](/id/gateway/configuration-reference#agentsdefaultsskills).

  </Accordion>

  <Accordion title="Sesuaikan pemantauan kesehatan channel gateway">
    Kontrol seberapa agresif gateway me-restart channel yang terlihat stale:

    ```json5
    {
      gateway: {
        channelHealthCheckMinutes: 5,
        channelStaleEventThresholdMinutes: 30,
        channelMaxRestartsPerHour: 10,
      },
      channels: {
        telegram: {
          healthMonitor: { enabled: false },
          accounts: {
            alerts: {
              healthMonitor: { enabled: true },
            },
          },
        },
      },
    }
    ```

    - Tetapkan `gateway.channelHealthCheckMinutes: 0` untuk menonaktifkan restart pemantauan kesehatan secara global.
    - `channelStaleEventThresholdMinutes` harus lebih besar atau sama dengan interval pemeriksaan.
    - Gunakan `channels.<provider>.healthMonitor.enabled` atau `channels.<provider>.accounts.<id>.healthMonitor.enabled` untuk menonaktifkan restart otomatis pada satu channel atau akun tanpa menonaktifkan pemantau global.
    - Lihat [Health Checks](/id/gateway/health) untuk debugging operasional dan [referensi lengkap](/id/gateway/configuration-reference#gateway) untuk semua field.

  </Accordion>

  <Accordion title="Konfigurasikan sesi dan reset">
    Sesi mengontrol kesinambungan dan isolasi percakapan:

    ```json5
    {
      session: {
        dmScope: "per-channel-peer",  // recommended for multi-user
        threadBindings: {
          enabled: true,
          idleHours: 24,
          maxAgeHours: 0,
        },
        reset: {
          mode: "daily",
          atHour: 4,
          idleMinutes: 120,
        },
      },
    }
    ```

    - `dmScope`: `main` (dibagikan) | `per-peer` | `per-channel-peer` | `per-account-channel-peer`
    - `threadBindings`: default global untuk perutean sesi yang terikat thread (Discord mendukung `/focus`, `/unfocus`, `/agents`, `/session idle`, dan `/session max-age`).
    - Lihat [Session Management](/id/concepts/session) untuk cakupan, tautan identitas, dan kebijakan pengiriman.
    - Lihat [referensi lengkap](/id/gateway/configuration-reference#session) untuk semua field.

  </Accordion>

  <Accordion title="Aktifkan sandboxing">
    Jalankan sesi agen dalam container Docker yang terisolasi:

    ```json5
    {
      agents: {
        defaults: {
          sandbox: {
            mode: "non-main",  // off | non-main | all
            scope: "agent",    // session | agent | shared
          },
        },
      },
    }
    ```

    Bangun image terlebih dahulu: `scripts/sandbox-setup.sh`

    Lihat [Sandboxing](/id/gateway/sandboxing) untuk panduan lengkap dan [referensi lengkap](/id/gateway/configuration-reference#agentsdefaultssandbox) untuk semua opsi.

  </Accordion>

  <Accordion title="Aktifkan push berbasis relay untuk build iOS resmi">
    Push berbasis relay dikonfigurasi di `openclaw.json`.

    Tetapkan ini di config gateway:

    ```json5
    {
      gateway: {
        push: {
          apns: {
            relay: {
              baseUrl: "https://relay.example.com",
              // Opsional. Default: 10000
              timeoutMs: 10000,
            },
          },
        },
      },
    }
    ```

    Setara CLI:

    ```bash
    openclaw config set gateway.push.apns.relay.baseUrl https://relay.example.com
    ```

    Yang dilakukan ini:

    - Memungkinkan gateway mengirim `push.test`, dorongan bangun, dan bangun penyambungan ulang melalui relay eksternal.
    - Menggunakan izin kirim dengan cakupan registrasi yang diteruskan oleh app iOS yang dipasangkan. Gateway tidak memerlukan token relay cakupan deployment.
    - Mengikat setiap registrasi berbasis relay ke identitas gateway yang dipasangkan oleh app iOS, sehingga gateway lain tidak dapat menggunakan kembali registrasi yang tersimpan.
    - Mempertahankan build iOS lokal/manual pada APNs langsung. Pengiriman berbasis relay hanya berlaku untuk build resmi yang didistribusikan dan mendaftar melalui relay.
    - Harus cocok dengan base URL relay yang ditanamkan ke dalam build iOS resmi/TestFlight, sehingga lalu lintas registrasi dan pengiriman mencapai deployment relay yang sama.

    Alur end-to-end:

    1. Instal build iOS resmi/TestFlight yang dikompilasi dengan base URL relay yang sama.
    2. Konfigurasikan `gateway.push.apns.relay.baseUrl` pada gateway.
    3. Pasangkan app iOS ke gateway dan biarkan sesi node serta operator terhubung.
    4. App iOS mengambil identitas gateway, mendaftar ke relay menggunakan App Attest plus receipt app, lalu memublikasikan payload `push.apns.register` berbasis relay ke gateway yang dipasangkan.
    5. Gateway menyimpan handle relay dan izin kirim, lalu menggunakannya untuk `push.test`, dorongan bangun, dan bangun penyambungan ulang.

    Catatan operasional:

    - Jika Anda memindahkan app iOS ke gateway yang berbeda, sambungkan ulang app agar dapat memublikasikan registrasi relay baru yang terikat ke gateway tersebut.
    - Jika Anda merilis build iOS baru yang mengarah ke deployment relay berbeda, app akan menyegarkan registrasi relay cache-nya alih-alih menggunakan kembali origin relay lama.

    Catatan kompatibilitas:

    - `OPENCLAW_APNS_RELAY_BASE_URL` dan `OPENCLAW_APNS_RELAY_TIMEOUT_MS` tetap berfungsi sebagai override env sementara.
    - `OPENCLAW_APNS_RELAY_ALLOW_HTTP=true` tetap menjadi jalan keluar pengembangan khusus loopback; jangan simpan URL relay HTTP di config.

    Lihat [iOS App](/id/platforms/ios#relay-backed-push-for-official-builds) untuk alur end-to-end dan [Authentication and trust flow](/id/platforms/ios#authentication-and-trust-flow) untuk model keamanan relay.

  </Accordion>

  <Accordion title="Siapkan heartbeat (check-in berkala)">
    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "30m",
            target: "last",
          },
        },
      },
    }
    ```

    - `every`: string durasi (`30m`, `2h`). Tetapkan `0m` untuk menonaktifkan.
    - `target`: `last` | `none` | `<channel-id>` (misalnya `discord`, `matrix`, `telegram`, atau `whatsapp`)
    - `directPolicy`: `allow` (default) atau `block` untuk target heartbeat bergaya DM
    - Lihat [Heartbeat](/id/gateway/heartbeat) untuk panduan lengkap.

  </Accordion>

  <Accordion title="Konfigurasikan job cron">
    ```json5
    {
      cron: {
        enabled: true,
        maxConcurrentRuns: 2,
        sessionRetention: "24h",
        runLog: {
          maxBytes: "2mb",
          keepLines: 2000,
        },
      },
    }
    ```

    - `sessionRetention`: pangkas sesi proses terisolasi yang sudah selesai dari `sessions.json` (default `24h`; tetapkan `false` untuk menonaktifkan).
    - `runLog`: pangkas `cron/runs/<jobId>.jsonl` berdasarkan ukuran dan jumlah baris yang dipertahankan.
    - Lihat [Cron jobs](/id/automation/cron-jobs) untuk ikhtisar fitur dan contoh CLI.

  </Accordion>

  <Accordion title="Siapkan webhook (hook)">
    Aktifkan endpoint webhook HTTP pada Gateway:

    ```json5
    {
      hooks: {
        enabled: true,
        token: "shared-secret",
        path: "/hooks",
        defaultSessionKey: "hook:ingress",
        allowRequestSessionKey: false,
        allowedSessionKeyPrefixes: ["hook:"],
        mappings: [
          {
            match: { path: "gmail" },
            action: "agent",
            agentId: "main",
            deliver: true,
          },
        ],
      },
    }
    ```

    Catatan keamanan:
    - Perlakukan semua konten payload hook/webhook sebagai input yang tidak tepercaya.
    - Gunakan `hooks.token` khusus; jangan gunakan ulang token Gateway bersama.
    - Auth hook hanya melalui header (`Authorization: Bearer ...` atau `x-openclaw-token`); token query-string ditolak.
    - `hooks.path` tidak boleh `/`; pertahankan ingress webhook pada subpath khusus seperti `/hooks`.
    - Biarkan flag bypass konten tidak aman tetap dinonaktifkan (`hooks.gmail.allowUnsafeExternalContent`, `hooks.mappings[].allowUnsafeExternalContent`) kecuali untuk debugging yang sangat terbatas.
    - Jika Anda mengaktifkan `hooks.allowRequestSessionKey`, tetapkan juga `hooks.allowedSessionKeyPrefixes` untuk membatasi session key yang dipilih pemanggil.
    - Untuk agen yang digerakkan hook, utamakan tier model modern yang kuat dan kebijakan alat yang ketat (misalnya hanya pengiriman pesan ditambah sandboxing jika memungkinkan).

    Lihat [referensi lengkap](/id/gateway/configuration-reference#hooks) untuk semua opsi mapping dan integrasi Gmail.

  </Accordion>

  <Accordion title="Konfigurasikan routing multi-agent">
    Jalankan beberapa agen terisolasi dengan workspace dan sesi terpisah:

    ```json5
    {
      agents: {
        list: [
          { id: "home", default: true, workspace: "~/.openclaw/workspace-home" },
          { id: "work", workspace: "~/.openclaw/workspace-work" },
        ],
      },
      bindings: [
        { agentId: "home", match: { channel: "whatsapp", accountId: "personal" } },
        { agentId: "work", match: { channel: "whatsapp", accountId: "biz" } },
      ],
    }
    ```

    Lihat [Multi-Agent](/id/concepts/multi-agent) dan [referensi lengkap](/id/gateway/configuration-reference#multi-agent-routing) untuk aturan binding dan profil akses per agen.

  </Accordion>

  <Accordion title="Pisahkan config ke beberapa file ($include)">
    Gunakan `$include` untuk mengatur config besar:

    ```json5
    // ~/.openclaw/openclaw.json
    {
      gateway: { port: 18789 },
      agents: { $include: "./agents.json5" },
      broadcast: {
        $include: ["./clients/a.json5", "./clients/b.json5"],
      },
    }
    ```

    - **File tunggal**: menggantikan objek yang memuatnya
    - **Array file**: digabungkan secara deep-merge sesuai urutan (yang belakangan menang)
    - **Key saudara**: digabungkan setelah include (menimpa nilai yang disertakan)
    - **Include bertingkat**: didukung hingga 10 level kedalaman
    - **Path relatif**: diselesaikan relatif terhadap file yang menyertakan
    - **Penanganan error**: error yang jelas untuk file yang hilang, parse error, dan include melingkar

  </Accordion>
</AccordionGroup>

## Hot reload config

Gateway memantau `~/.openclaw/openclaw.json` dan menerapkan perubahan secara otomatis — tidak perlu restart manual untuk sebagian besar pengaturan.

### Mode reload

| Mode                   | Perilaku                                                                                |
| ---------------------- | --------------------------------------------------------------------------------------- |
| **`hybrid`** (default) | Menerapkan hot perubahan yang aman secara instan. Otomatis restart untuk yang kritis.  |
| **`hot`**              | Hanya menerapkan hot perubahan yang aman. Mencatat peringatan saat restart diperlukan — Anda yang menanganinya. |
| **`restart`**          | Me-restart Gateway pada setiap perubahan config, aman atau tidak.                       |
| **`off`**              | Menonaktifkan pemantauan file. Perubahan berlaku pada restart manual berikutnya.        |

```json5
{
  gateway: {
    reload: { mode: "hybrid", debounceMs: 300 },
  },
}
```

### Apa yang diterapkan hot vs apa yang perlu restart

Sebagian besar field diterapkan secara hot tanpa downtime. Dalam mode `hybrid`, perubahan yang memerlukan restart ditangani secara otomatis.

| Kategori            | Field                                                                | Perlu restart? |
| ------------------- | -------------------------------------------------------------------- | -------------- |
| Channel             | `channels.*`, `web` (WhatsApp) — semua channel bawaan dan ekstensi   | Tidak          |
| Agen & model        | `agent`, `agents`, `models`, `routing`                               | Tidak          |
| Otomatisasi         | `hooks`, `cron`, `agent.heartbeat`                                   | Tidak          |
| Sesi & pesan        | `session`, `messages`                                                | Tidak          |
| Alat & media        | `tools`, `browser`, `skills`, `audio`, `talk`                        | Tidak          |
| UI & lain-lain      | `ui`, `logging`, `identity`, `bindings`                              | Tidak          |
| Server gateway      | `gateway.*` (port, bind, auth, tailscale, TLS, HTTP)                 | **Ya**         |
| Infrastruktur       | `discovery`, `canvasHost`, `plugins`                                 | **Ya**         |

<Note>
`gateway.reload` dan `gateway.remote` adalah pengecualian — mengubahnya **tidak** memicu restart.
</Note>

## RPC config (pembaruan terprogram)

<Note>
RPC penulisan control-plane (`config.apply`, `config.patch`, `update.run`) dibatasi hingga **3 permintaan per 60 detik** per `deviceId+clientIp`. Saat dibatasi, RPC mengembalikan `UNAVAILABLE` dengan `retryAfterMs`.
</Note>

Alur aman/default:

- `config.schema.lookup`: periksa satu subtree config dengan cakupan path dengan node skema dangkal,
  metadata petunjuk yang cocok, dan ringkasan turunan langsung
- `config.get`: ambil snapshot + hash saat ini
- `config.patch`: jalur pembaruan parsial yang disukai
- `config.apply`: hanya untuk penggantian config penuh
- `update.run`: self-update + restart eksplisit

Jika Anda tidak mengganti seluruh config, utamakan `config.schema.lookup`
lalu `config.patch`.

<AccordionGroup>
  <Accordion title="config.apply (ganti penuh)">
    Memvalidasi + menulis config penuh dan me-restart Gateway dalam satu langkah.

    <Warning>
    `config.apply` menggantikan **seluruh config**. Gunakan `config.patch` untuk pembaruan parsial, atau `openclaw config set` untuk key tunggal.
    </Warning>

    Parameter:

    - `raw` (string) — payload JSON5 untuk seluruh config
    - `baseHash` (opsional) — hash config dari `config.get` (wajib saat config sudah ada)
    - `sessionKey` (opsional) — session key untuk ping bangun pasca-restart
    - `note` (opsional) — catatan untuk sentinel restart
    - `restartDelayMs` (opsional) — jeda sebelum restart (default 2000)

    Permintaan restart digabungkan saat satu restart sudah tertunda/sedang berlangsung, dan cooldown 30 detik berlaku di antara siklus restart.

    ```bash
    openclaw gateway call config.get --params '{}'  # capture payload.hash
    openclaw gateway call config.apply --params '{
      "raw": "{ agents: { defaults: { workspace: \"~/.openclaw/workspace\" } } }",
      "baseHash": "<hash>",
      "sessionKey": "agent:main:whatsapp:direct:+15555550123"
    }'
    ```

  </Accordion>

  <Accordion title="config.patch (pembaruan parsial)">
    Menggabungkan pembaruan parsial ke config yang ada (semantik JSON merge patch):

    - Objek digabungkan secara rekursif
    - `null` menghapus key
    - Array menggantikan

    Parameter:

    - `raw` (string) — JSON5 hanya dengan key yang akan diubah
    - `baseHash` (wajib) — hash config dari `config.get`
    - `sessionKey`, `note`, `restartDelayMs` — sama seperti `config.apply`

    Perilaku restart sama dengan `config.apply`: restart tertunda digabungkan ditambah cooldown 30 detik di antara siklus restart.

    ```bash
    openclaw gateway call config.patch --params '{
      "raw": "{ channels: { telegram: { groups: { \"*\": { requireMention: false } } } } }",
      "baseHash": "<hash>"
    }'
    ```

  </Accordion>
</AccordionGroup>

## Variabel lingkungan

OpenClaw membaca env vars dari proses induk ditambah:

- `.env` dari direktori kerja saat ini (jika ada)
- `~/.openclaw/.env` (fallback global)

Keduanya tidak menimpa env vars yang sudah ada. Anda juga dapat menetapkan env vars inline di config:

```json5
{
  env: {
    OPENROUTER_API_KEY: "sk-or-...",
    vars: { GROQ_API_KEY: "gsk-..." },
  },
}
```

<Accordion title="Impor env shell (opsional)">
  Jika diaktifkan dan key yang diharapkan belum ditetapkan, OpenClaw menjalankan shell login Anda dan hanya mengimpor key yang hilang:

```json5
{
  env: {
    shellEnv: { enabled: true, timeoutMs: 15000 },
  },
}
```

Setara env var: `OPENCLAW_LOAD_SHELL_ENV=1`
</Accordion>

<Accordion title="Substitusi env var dalam nilai config">
  Referensikan env vars dalam nilai string config apa pun dengan `${VAR_NAME}`:

```json5
{
  gateway: { auth: { token: "${OPENCLAW_GATEWAY_TOKEN}" } },
  models: { providers: { custom: { apiKey: "${CUSTOM_API_KEY}" } } },
}
```

Aturan:

- Hanya nama huruf besar yang cocok: `[A-Z_][A-Z0-9_]*`
- Variabel yang hilang/kosong memunculkan error saat waktu muat
- Escape dengan `$${VAR}` untuk keluaran literal
- Berfungsi di dalam file `$include`
- Substitusi inline: `"${BASE}/v1"` → `"https://api.example.com/v1"`

</Accordion>

<Accordion title="Referensi rahasia (env, file, exec)">
  Untuk field yang mendukung objek SecretRef, Anda dapat menggunakan:

```json5
{
  models: {
    providers: {
      openai: { apiKey: { source: "env", provider: "default", id: "OPENAI_API_KEY" } },
    },
  },
  skills: {
    entries: {
      "image-lab": {
        apiKey: {
          source: "file",
          provider: "filemain",
          id: "/skills/entries/image-lab/apiKey",
        },
      },
    },
  },
  channels: {
    googlechat: {
      serviceAccountRef: {
        source: "exec",
        provider: "vault",
        id: "channels/googlechat/serviceAccount",
      },
    },
  },
}
```

Detail SecretRef (termasuk `secrets.providers` untuk `env`/`file`/`exec`) ada di [Secrets Management](/id/gateway/secrets).
Path kredensial yang didukung tercantum di [SecretRef Credential Surface](/id/reference/secretref-credential-surface).
</Accordion>

Lihat [Environment](/id/help/environment) untuk prioritas dan sumber lengkap.

## Referensi lengkap

Untuk referensi lengkap per field, lihat **[Configuration Reference](/id/gateway/configuration-reference)**.

---

_Terkait: [Configuration Examples](/id/gateway/configuration-examples) · [Configuration Reference](/id/gateway/configuration-reference) · [Doctor](/id/gateway/doctor)_
