---
read_when:
    - Anda ingin menggunakan langganan Claude Max dengan tool yang kompatibel dengan OpenAI
    - Anda menginginkan server API lokal yang membungkus Claude Code CLI
    - Anda ingin mengevaluasi akses Anthropic berbasis langganan versus berbasis kunci API
summary: Proxy komunitas untuk mengekspos kredensial langganan Claude sebagai endpoint yang kompatibel dengan OpenAI
title: Claude Max API Proxy
x-i18n:
    generated_at: "2026-04-12T23:29:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: 534bc3d189e68529fb090258eb0d6db6d367eb7e027ad04b1f0be55f6aa7d889
    source_path: providers/claude-max-api-proxy.md
    workflow: 15
---

# Claude Max API Proxy

**claude-max-api-proxy** adalah tool komunitas yang mengekspos langganan Claude Max/Pro Anda sebagai endpoint API yang kompatibel dengan OpenAI. Ini memungkinkan Anda menggunakan langganan tersebut dengan tool apa pun yang mendukung format API OpenAI.

<Warning>
Jalur ini hanya untuk kompatibilitas teknis. Anthropic pernah memblokir sebagian penggunaan
langganan di luar Claude Code. Anda harus memutuskan sendiri apakah akan menggunakannya
dan memverifikasi ketentuan Anthropic saat ini sebelum mengandalkannya.
</Warning>

## Mengapa menggunakan ini?

| Pendekatan              | Biaya                                              | Paling cocok untuk                          |
| ----------------------- | -------------------------------------------------- | ------------------------------------------ |
| Anthropic API           | Bayar per token (~$15/M input, $75/M output untuk Opus) | Aplikasi produksi, volume tinggi      |
| Langganan Claude Max    | Tetap $200/bulan                                   | Penggunaan pribadi, pengembangan, penggunaan tanpa batas |

Jika Anda memiliki langganan Claude Max dan ingin menggunakannya dengan tool yang kompatibel dengan OpenAI, proxy ini dapat mengurangi biaya untuk beberapa alur kerja. Kunci API tetap menjadi jalur kebijakan yang lebih jelas untuk penggunaan produksi.

## Cara kerjanya

```
Aplikasi Anda → claude-max-api-proxy → Claude Code CLI → Anthropic (melalui langganan)
   (format OpenAI)         (mengonversi format)         (menggunakan login Anda)
```

Proxy ini:

1. Menerima permintaan format OpenAI di `http://localhost:3456/v1/chat/completions`
2. Mengonversinya menjadi perintah Claude Code CLI
3. Mengembalikan respons dalam format OpenAI (streaming didukung)

## Memulai

<Steps>
  <Step title="Instal proxy">
    Memerlukan Node.js 20+ dan Claude Code CLI.

    ```bash
    npm install -g claude-max-api-proxy

    # Verifikasi Claude CLI telah diautentikasi
    claude --version
    ```

  </Step>
  <Step title="Jalankan server">
    ```bash
    claude-max-api
    # Server berjalan di http://localhost:3456
    ```
  </Step>
  <Step title="Uji proxy">
    ```bash
    # Pemeriksaan kesehatan
    curl http://localhost:3456/health

    # Daftar model
    curl http://localhost:3456/v1/models

    # Chat completion
    curl http://localhost:3456/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d '{
        "model": "claude-opus-4",
        "messages": [{"role": "user", "content": "Hello!"}]
      }'
    ```

  </Step>
  <Step title="Konfigurasikan OpenClaw">
    Arahkan OpenClaw ke proxy sebagai endpoint kustom yang kompatibel dengan OpenAI:

    ```json5
    {
      env: {
        OPENAI_API_KEY: "not-needed",
        OPENAI_BASE_URL: "http://localhost:3456/v1",
      },
      agents: {
        defaults: {
          model: { primary: "openai/claude-opus-4" },
        },
      },
    }
    ```

  </Step>
</Steps>

## Model yang tersedia

| ID Model          | Dipetakan ke     |
| ----------------- | ---------------- |
| `claude-opus-4`   | Claude Opus 4    |
| `claude-sonnet-4` | Claude Sonnet 4  |
| `claude-haiku-4`  | Claude Haiku 4   |

## Lanjutan

<AccordionGroup>
  <Accordion title="Catatan gaya proxy yang kompatibel dengan OpenAI">
    Jalur ini menggunakan rute gaya proxy yang kompatibel dengan OpenAI yang sama seperti backend
    `/v1` kustom lainnya:

    - Pembentukan permintaan native khusus OpenAI tidak berlaku
    - Tidak ada `service_tier`, tidak ada Responses `store`, tidak ada petunjuk prompt-cache, dan tidak ada
      pembentukan payload kompatibilitas reasoning OpenAI
    - Header atribusi OpenClaw tersembunyi (`originator`, `version`, `User-Agent`)
      tidak disuntikkan pada URL proxy

  </Accordion>

  <Accordion title="Mulai otomatis di macOS dengan LaunchAgent">
    Buat LaunchAgent untuk menjalankan proxy secara otomatis:

    ```bash
    cat > ~/Library/LaunchAgents/com.claude-max-api.plist << 'EOF'
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
      <key>Label</key>
      <string>com.claude-max-api</string>
      <key>RunAtLoad</key>
      <true/>
      <key>KeepAlive</key>
      <true/>
      <key>ProgramArguments</key>
      <array>
        <string>/usr/local/bin/node</string>
        <string>/usr/local/lib/node_modules/claude-max-api-proxy/dist/server/standalone.js</string>
      </array>
      <key>EnvironmentVariables</key>
      <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/opt/homebrew/bin:~/.local/bin:/usr/bin:/bin</string>
      </dict>
    </dict>
    </plist>
    EOF

    launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.claude-max-api.plist
    ```

  </Accordion>
</AccordionGroup>

## Tautan

- **npm:** [https://www.npmjs.com/package/claude-max-api-proxy](https://www.npmjs.com/package/claude-max-api-proxy)
- **GitHub:** [https://github.com/atalovesyou/claude-max-api-proxy](https://github.com/atalovesyou/claude-max-api-proxy)
- **Issues:** [https://github.com/atalovesyou/claude-max-api-proxy/issues](https://github.com/atalovesyou/claude-max-api-proxy/issues)

## Catatan

- Ini adalah **tool komunitas**, tidak didukung secara resmi oleh Anthropic atau OpenClaw
- Memerlukan langganan Claude Max/Pro yang aktif dengan Claude Code CLI yang sudah diautentikasi
- Proxy berjalan secara lokal dan tidak mengirim data ke server pihak ketiga mana pun
- Respons streaming didukung sepenuhnya

<Note>
Untuk integrasi Anthropic native dengan Claude CLI atau kunci API, lihat [provider Anthropic](/id/providers/anthropic). Untuk langganan OpenAI/Codex, lihat [provider OpenAI](/id/providers/openai).
</Note>

## Terkait

<CardGroup cols={2}>
  <Card title="Provider Anthropic" href="/id/providers/anthropic" icon="bolt">
    Integrasi OpenClaw native dengan Claude CLI atau kunci API.
  </Card>
  <Card title="Provider OpenAI" href="/id/providers/openai" icon="robot">
    Untuk langganan OpenAI/Codex.
  </Card>
  <Card title="Provider model" href="/id/concepts/model-providers" icon="layers">
    Ikhtisar semua provider, ref model, dan perilaku failover.
  </Card>
  <Card title="Konfigurasi" href="/id/gateway/configuration" icon="gear">
    Referensi config lengkap.
  </Card>
</CardGroup>
