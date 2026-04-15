---
read_when:
    - Anda memerlukan perilaku terperinci untuk `openclaw onboard`
    - Anda sedang men-debug hasil onboarding atau mengintegrasikan klien onboarding
sidebarTitle: CLI reference
summary: Referensi lengkap untuk alur penyiapan CLI, penyiapan autentikasi/model, output, dan detail internal
title: Referensi Penyiapan CLI
x-i18n:
    generated_at: "2026-04-15T14:41:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: 61ca679caca3b43fa02388294007f89db22d343e49e10b61d8d118cd8fbb7369
    source_path: start/wizard-cli-reference.md
    workflow: 15
---

# Referensi Penyiapan CLI

Halaman ini adalah referensi lengkap untuk `openclaw onboard`.
Untuk panduan singkat, lihat [Onboarding (CLI)](/id/start/wizard).

## Apa yang dilakukan wizard

Mode lokal (default) memandu Anda melalui:

- Penyiapan model dan autentikasi (OAuth langganan OpenAI Code, Anthropic Claude CLI atau API key, serta opsi MiniMax, GLM, Ollama, Moonshot, StepFun, dan AI Gateway)
- Lokasi workspace dan file bootstrap
- Pengaturan Gateway (port, bind, auth, tailscale)
- Channel dan provider (Telegram, WhatsApp, Discord, Google Chat, Mattermost, Signal, BlueBubbles, dan Plugin channel bawaan lainnya)
- Instalasi daemon (LaunchAgent, systemd user unit, atau Scheduled Task Windows native dengan fallback folder Startup)
- Pemeriksaan kesehatan
- Penyiapan Skills

Mode remote mengonfigurasi mesin ini untuk terhubung ke gateway di tempat lain.
Mode ini tidak menginstal atau mengubah apa pun di host remote.

## Detail alur lokal

<Steps>
  <Step title="Deteksi konfigurasi yang ada">
    - Jika `~/.openclaw/openclaw.json` ada, pilih Keep, Modify, atau Reset.
    - Menjalankan ulang wizard tidak akan menghapus apa pun kecuali Anda secara eksplisit memilih Reset (atau memberikan `--reset`).
    - CLI `--reset` default ke `config+creds+sessions`; gunakan `--reset-scope full` untuk juga menghapus workspace.
    - Jika konfigurasi tidak valid atau berisi key lama, wizard berhenti dan meminta Anda menjalankan `openclaw doctor` sebelum melanjutkan.
    - Reset menggunakan `trash` dan menawarkan cakupan:
      - Hanya konfigurasi
      - Konfigurasi + kredensial + sesi
      - Reset penuh (juga menghapus workspace)
  </Step>
  <Step title="Model dan autentikasi">
    - Matriks opsi lengkap ada di [Opsi autentikasi dan model](#auth-and-model-options).
  </Step>
  <Step title="Workspace">
    - Default `~/.openclaw/workspace` (dapat dikonfigurasi).
    - Menyiapkan file workspace yang diperlukan untuk ritual bootstrap saat pertama kali dijalankan.
    - Tata letak workspace: [Workspace agen](/id/concepts/agent-workspace).
  </Step>
  <Step title="Gateway">
    - Meminta port, bind, mode auth, dan eksposur tailscale.
    - Direkomendasikan: tetap aktifkan auth token bahkan untuk loopback agar klien WS lokal harus melakukan autentikasi.
    - Dalam mode token, penyiapan interaktif menawarkan:
      - **Generate/store plaintext token** (default)
      - **Use SecretRef** (opsional)
    - Dalam mode kata sandi, penyiapan interaktif juga mendukung penyimpanan plaintext atau SecretRef.
    - Jalur SecretRef token non-interaktif: `--gateway-token-ref-env <ENV_VAR>`.
      - Memerlukan env var yang tidak kosong di environment proses onboarding.
      - Tidak dapat digabungkan dengan `--gateway-token`.
    - Nonaktifkan auth hanya jika Anda sepenuhnya memercayai setiap proses lokal.
    - Bind non-loopback tetap memerlukan auth.
  </Step>
  <Step title="Channel">
    - [WhatsApp](/id/channels/whatsapp): login QR opsional
    - [Telegram](/id/channels/telegram): token bot
    - [Discord](/id/channels/discord): token bot
    - [Google Chat](/id/channels/googlechat): JSON akun layanan + audiens webhook
    - [Mattermost](/id/channels/mattermost): token bot + URL dasar
    - [Signal](/id/channels/signal): instalasi `signal-cli` opsional + konfigurasi akun
    - [BlueBubbles](/id/channels/bluebubbles): direkomendasikan untuk iMessage; URL server + kata sandi + webhook
    - [iMessage](/id/channels/imessage): jalur CLI `imsg` lama + akses DB
    - Keamanan DM: default-nya adalah pairing. DM pertama mengirim kode; setujui melalui
      `openclaw pairing approve <channel> <code>` atau gunakan allowlist.
  </Step>
  <Step title="Instalasi daemon">
    - macOS: LaunchAgent
      - Memerlukan sesi pengguna yang sedang login; untuk headless, gunakan LaunchDaemon kustom (tidak disertakan).
    - Linux dan Windows melalui WSL2: systemd user unit
      - Wizard mencoba `loginctl enable-linger <user>` agar gateway tetap berjalan setelah logout.
      - Mungkin meminta sudo (menulis `/var/lib/systemd/linger`); pertama-tama mencoba tanpa sudo.
    - Windows native: Scheduled Task terlebih dahulu
      - Jika pembuatan task ditolak, OpenClaw akan fallback ke item login folder Startup per pengguna dan segera memulai gateway.
      - Scheduled Task tetap lebih disukai karena memberikan status supervisor yang lebih baik.
    - Pemilihan runtime: Node (direkomendasikan; diperlukan untuk WhatsApp dan Telegram). Bun tidak direkomendasikan.
  </Step>
  <Step title="Pemeriksaan kesehatan">
    - Memulai gateway (jika perlu) dan menjalankan `openclaw health`.
    - `openclaw status --deep` menambahkan probe kesehatan gateway langsung ke output status, termasuk probe channel jika didukung.
  </Step>
  <Step title="Skills">
    - Membaca Skills yang tersedia dan memeriksa persyaratan.
    - Memungkinkan Anda memilih manajer node: npm, pnpm, atau bun.
    - Menginstal dependensi opsional (beberapa menggunakan Homebrew di macOS).
  </Step>
  <Step title="Selesai">
    - Ringkasan dan langkah berikutnya, termasuk opsi aplikasi iOS, Android, dan macOS.
  </Step>
</Steps>

<Note>
Jika tidak ada GUI yang terdeteksi, wizard mencetak instruksi port-forward SSH untuk Control UI alih-alih membuka browser.
Jika aset Control UI tidak ada, wizard mencoba membangunnya; fallback-nya adalah `pnpm ui:build` (secara otomatis menginstal dependensi UI).
</Note>

## Detail mode remote

Mode remote mengonfigurasi mesin ini untuk terhubung ke gateway di tempat lain.

<Info>
Mode remote tidak menginstal atau mengubah apa pun di host remote.
</Info>

Yang Anda atur:

- URL gateway remote (`ws://...`)
- Token jika auth gateway remote diperlukan (direkomendasikan)

<Note>
- Jika gateway hanya loopback, gunakan tunneling SSH atau tailnet.
- Petunjuk discovery:
  - macOS: Bonjour (`dns-sd`)
  - Linux: Avahi (`avahi-browse`)
</Note>

## Opsi autentikasi dan model

<AccordionGroup>
  <Accordion title="Anthropic API key">
    Menggunakan `ANTHROPIC_API_KEY` jika ada atau meminta key, lalu menyimpannya untuk penggunaan daemon.
  </Accordion>
  <Accordion title="Langganan OpenAI Code (penggunaan ulang Codex CLI)">
    Jika `~/.codex/auth.json` ada, wizard dapat menggunakannya kembali.
    Kredensial Codex CLI yang digunakan ulang tetap dikelola oleh Codex CLI; saat kedaluwarsa OpenClaw
    terlebih dahulu membaca ulang sumber tersebut dan, ketika provider dapat me-refresh-nya, menulis
    kembali kredensial yang diperbarui ke penyimpanan Codex alih-alih mengambil alih pengelolaannya
    sendiri.
  </Accordion>
  <Accordion title="Langganan OpenAI Code (OAuth)">
    Alur browser; tempel `code#state`.

    Mengatur `agents.defaults.model` ke `openai-codex/gpt-5.4` saat model belum disetel atau `openai/*`.

  </Accordion>
  <Accordion title="OpenAI API key">
    Menggunakan `OPENAI_API_KEY` jika ada atau meminta key, lalu menyimpan kredensial dalam profil auth.

    Mengatur `agents.defaults.model` ke `openai/gpt-5.4` saat model belum disetel, `openai/*`, atau `openai-codex/*`.

  </Accordion>
  <Accordion title="xAI (Grok) API key">
    Meminta `XAI_API_KEY` dan mengonfigurasi xAI sebagai provider model.
  </Accordion>
  <Accordion title="OpenCode">
    Meminta `OPENCODE_API_KEY` (atau `OPENCODE_ZEN_API_KEY`) dan memungkinkan Anda memilih katalog Zen atau Go.
    URL penyiapan: [opencode.ai/auth](https://opencode.ai/auth).
  </Accordion>
  <Accordion title="API key (generik)">
    Menyimpan key untuk Anda.
  </Accordion>
  <Accordion title="Vercel AI Gateway">
    Meminta `AI_GATEWAY_API_KEY`.
    Detail lebih lanjut: [Vercel AI Gateway](/id/providers/vercel-ai-gateway).
  </Accordion>
  <Accordion title="Cloudflare AI Gateway">
    Meminta ID akun, ID gateway, dan `CLOUDFLARE_AI_GATEWAY_API_KEY`.
    Detail lebih lanjut: [Cloudflare AI Gateway](/id/providers/cloudflare-ai-gateway).
  </Accordion>
  <Accordion title="MiniMax">
    Konfigurasi ditulis otomatis. Default host adalah `MiniMax-M2.7`; penyiapan API key menggunakan
    `minimax/...`, dan penyiapan OAuth menggunakan `minimax-portal/...`.
    Detail lebih lanjut: [MiniMax](/id/providers/minimax).
  </Accordion>
  <Accordion title="StepFun">
    Konfigurasi ditulis otomatis untuk StepFun standard atau Step Plan pada endpoint China atau global.
    Standard saat ini mencakup `step-3.5-flash`, dan Step Plan juga mencakup `step-3.5-flash-2603`.
    Detail lebih lanjut: [StepFun](/id/providers/stepfun).
  </Accordion>
  <Accordion title="Synthetic (kompatibel Anthropic)">
    Meminta `SYNTHETIC_API_KEY`.
    Detail lebih lanjut: [Synthetic](/id/providers/synthetic).
  </Accordion>
  <Accordion title="Ollama (Cloud dan model terbuka lokal)">
    Pertama meminta `Cloud + Local`, `Cloud only`, atau `Local only`.
    `Cloud only` menggunakan `OLLAMA_API_KEY` dengan `https://ollama.com`.
    Mode berbasis host meminta URL dasar (default `http://127.0.0.1:11434`), menemukan model yang tersedia, dan menyarankan default.
    `Cloud + Local` juga memeriksa apakah host Ollama tersebut sudah login untuk akses cloud.
    Detail lebih lanjut: [Ollama](/id/providers/ollama).
  </Accordion>
  <Accordion title="Moonshot dan Kimi Coding">
    Konfigurasi Moonshot (Kimi K2) dan Kimi Coding ditulis otomatis.
    Detail lebih lanjut: [Moonshot AI (Kimi + Kimi Coding)](/id/providers/moonshot).
  </Accordion>
  <Accordion title="Provider kustom">
    Bekerja dengan endpoint yang kompatibel dengan OpenAI dan kompatibel dengan Anthropic.

    Onboarding interaktif mendukung pilihan penyimpanan API key yang sama seperti alur API key provider lainnya:
    - **Paste API key now** (plaintext)
    - **Use secret reference** (referensi env atau referensi provider yang dikonfigurasi, dengan validasi preflight)

    Flag non-interaktif:
    - `--auth-choice custom-api-key`
    - `--custom-base-url`
    - `--custom-model-id`
    - `--custom-api-key` (opsional; fallback ke `CUSTOM_API_KEY`)
    - `--custom-provider-id` (opsional)
    - `--custom-compatibility <openai|anthropic>` (opsional; default `openai`)

  </Accordion>
  <Accordion title="Lewati">
    Membiarkan auth tidak dikonfigurasi.
  </Accordion>
</AccordionGroup>

Perilaku model:

- Pilih model default dari opsi yang terdeteksi, atau masukkan provider dan model secara manual.
- Saat onboarding dimulai dari pilihan auth provider, pemilih model akan memprioritaskan
  provider tersebut secara otomatis. Untuk Volcengine dan BytePlus, preferensi yang sama
  juga cocok dengan varian coding-plan mereka (`volcengine-plan/*`,
  `byteplus-plan/*`).
- Jika filter provider yang diprioritaskan itu kosong, pemilih akan fallback ke
  katalog lengkap alih-alih tidak menampilkan model apa pun.
- Wizard menjalankan pemeriksaan model dan memperingatkan jika model yang dikonfigurasi tidak dikenal atau auth tidak ada.

Jalur kredensial dan profil:

- Profil auth (API key + OAuth): `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- Impor OAuth lama: `~/.openclaw/credentials/oauth.json`

Mode penyimpanan kredensial:

- Perilaku onboarding default menyimpan API key sebagai nilai plaintext dalam profil auth.
- `--secret-input-mode ref` mengaktifkan mode referensi alih-alih penyimpanan key plaintext.
  Dalam penyiapan interaktif, Anda dapat memilih salah satu:
  - referensi env var (misalnya `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`)
  - referensi provider yang dikonfigurasi (`file` atau `exec`) dengan alias provider + id
- Mode referensi interaktif menjalankan validasi preflight cepat sebelum menyimpan.
  - Referensi env: memvalidasi nama variabel + nilai tidak kosong di environment onboarding saat ini.
  - Referensi provider: memvalidasi konfigurasi provider dan me-resolve id yang diminta.
  - Jika preflight gagal, onboarding menampilkan error dan memungkinkan Anda mencoba lagi.
- Dalam mode non-interaktif, `--secret-input-mode ref` hanya didukung dengan env.
  - Setel env var provider di environment proses onboarding.
  - Flag key inline (misalnya `--openai-api-key`) mensyaratkan env var tersebut disetel; jika tidak, onboarding gagal cepat.
  - Untuk provider kustom, mode `ref` non-interaktif menyimpan `models.providers.<id>.apiKey` sebagai `{ source: "env", provider: "default", id: "CUSTOM_API_KEY" }`.
  - Dalam kasus provider kustom tersebut, `--custom-api-key` mensyaratkan `CUSTOM_API_KEY` disetel; jika tidak, onboarding gagal cepat.
- Kredensial auth gateway mendukung pilihan plaintext dan SecretRef dalam penyiapan interaktif:
  - Mode token: **Generate/store plaintext token** (default) atau **Use SecretRef**.
  - Mode kata sandi: plaintext atau SecretRef.
- Jalur SecretRef token non-interaktif: `--gateway-token-ref-env <ENV_VAR>`.
- Penyiapan plaintext yang sudah ada tetap berfungsi tanpa perubahan.

<Note>
Tip untuk headless dan server: selesaikan OAuth di mesin dengan browser, lalu salin
`auth-profiles.json` agen tersebut (misalnya
`~/.openclaw/agents/<agentId>/agent/auth-profiles.json`, atau path
`$OPENCLAW_STATE_DIR/...` yang sesuai) ke host gateway. `credentials/oauth.json`
hanya merupakan sumber impor lama.
</Note>

## Output dan detail internal

Field umum dalam `~/.openclaw/openclaw.json`:

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers` (jika Minimax dipilih)
- `tools.profile` (onboarding lokal default ke `"coding"` saat belum disetel; nilai eksplisit yang sudah ada tetap dipertahankan)
- `gateway.*` (mode, bind, auth, tailscale)
- `session.dmScope` (onboarding lokal secara default menetapkan ini ke `per-channel-peer` saat belum disetel; nilai eksplisit yang sudah ada tetap dipertahankan)
- `channels.telegram.botToken`, `channels.discord.token`, `channels.matrix.*`, `channels.signal.*`, `channels.imessage.*`
- Allowlist channel (Slack, Discord, Matrix, Microsoft Teams) saat Anda ikut serta selama prompt (nama di-resolve menjadi ID jika memungkinkan)
- `skills.install.nodeManager`
  - Flag `setup --node-manager` menerima `npm`, `pnpm`, atau `bun`.
  - Konfigurasi manual masih dapat menetapkan `skills.install.nodeManager: "yarn"` nanti.
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add` menulis `agents.list[]` dan `bindings` opsional.

Kredensial WhatsApp berada di bawah `~/.openclaw/credentials/whatsapp/<accountId>/`.
Sesi disimpan di bawah `~/.openclaw/agents/<agentId>/sessions/`.

<Note>
Beberapa channel dikirim sebagai Plugin. Saat dipilih selama penyiapan, wizard
meminta untuk menginstal Plugin (npm atau path lokal) sebelum konfigurasi channel.
</Note>

RPC wizard Gateway:

- `wizard.start`
- `wizard.next`
- `wizard.cancel`
- `wizard.status`

Klien (aplikasi macOS dan Control UI) dapat merender langkah-langkah tanpa mengimplementasikan ulang logika onboarding.

Perilaku penyiapan Signal:

- Mengunduh aset rilis yang sesuai
- Menyimpannya di bawah `~/.openclaw/tools/signal-cli/<version>/`
- Menulis `channels.signal.cliPath` dalam konfigurasi
- Build JVM memerlukan Java 21
- Build native digunakan jika tersedia
- Windows menggunakan WSL2 dan mengikuti alur Linux signal-cli di dalam WSL

## Dokumen terkait

- Hub onboarding: [Onboarding (CLI)](/id/start/wizard)
- Otomatisasi dan skrip: [Otomatisasi CLI](/id/start/wizard-cli-automation)
- Referensi perintah: [`openclaw onboard`](/cli/onboard)
