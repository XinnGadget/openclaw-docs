---
read_when:
    - Anda ingin menggunakan GitHub Copilot sebagai provider model
    - Anda memerlukan alur `openclaw models auth login-github-copilot`
summary: Masuk ke GitHub Copilot dari OpenClaw menggunakan device flow
title: GitHub Copilot
x-i18n:
    generated_at: "2026-04-12T23:30:48Z"
    model: gpt-5.4
    provider: openai
    source_hash: 51fee006e7d4e78e37b0c29356b0090b132de727d99b603441767d3fb642140b
    source_path: providers/github-copilot.md
    workflow: 15
---

# GitHub Copilot

GitHub Copilot adalah asisten coding AI dari GitHub. Ini menyediakan akses ke model
Copilot untuk akun dan paket GitHub Anda. OpenClaw dapat menggunakan Copilot sebagai provider model
dengan dua cara yang berbeda.

## Dua cara menggunakan Copilot di OpenClaw

<Tabs>
  <Tab title="Provider bawaan (github-copilot)">
    Gunakan alur login perangkat native untuk mendapatkan token GitHub, lalu menukarkannya dengan
    token API Copilot saat OpenClaw berjalan. Ini adalah jalur **default** dan paling sederhana
    karena tidak memerlukan VS Code.

    <Steps>
      <Step title="Jalankan perintah login">
        ```bash
        openclaw models auth login-github-copilot
        ```

        Anda akan diminta mengunjungi URL dan memasukkan kode satu kali. Biarkan
        terminal tetap terbuka sampai selesai.
      </Step>
      <Step title="Setel model default">
        ```bash
        openclaw models set github-copilot/gpt-4o
        ```

        Atau di config:

        ```json5
        {
          agents: { defaults: { model: { primary: "github-copilot/gpt-4o" } } },
        }
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="Plugin Copilot Proxy (copilot-proxy)">
    Gunakan ekstensi VS Code **Copilot Proxy** sebagai bridge lokal. OpenClaw berbicara ke
    endpoint `/v1` milik proxy dan menggunakan daftar model yang Anda konfigurasikan di sana.

    <Note>
    Pilih ini ketika Anda sudah menjalankan Copilot Proxy di VS Code atau perlu merutekan
    melaluinya. Anda harus mengaktifkan Plugin dan menjaga ekstensi VS Code tetap berjalan.
    </Note>

  </Tab>
</Tabs>

## Flag opsional

| Flag            | Deskripsi                                            |
| --------------- | ---------------------------------------------------- |
| `--yes`         | Lewati prompt konfirmasi                             |
| `--set-default` | Terapkan juga model default yang direkomendasikan provider |

```bash
# Lewati konfirmasi
openclaw models auth login-github-copilot --yes

# Login dan setel model default dalam satu langkah
openclaw models auth login --provider github-copilot --method device --set-default
```

<AccordionGroup>
  <Accordion title="Memerlukan TTY interaktif">
    Alur login perangkat memerlukan TTY interaktif. Jalankan langsung di
    terminal, bukan di skrip non-interaktif atau pipeline CI.
  </Accordion>

  <Accordion title="Ketersediaan model bergantung pada paket Anda">
    Ketersediaan model Copilot bergantung pada paket GitHub Anda. Jika suatu model
    ditolak, coba ID lain (misalnya `github-copilot/gpt-4.1`).
  </Accordion>

  <Accordion title="Pemilihan transport">
    ID model Claude menggunakan transport Anthropic Messages secara otomatis. GPT,
    model seri-o, dan Gemini tetap menggunakan transport OpenAI Responses. OpenClaw
    memilih transport yang benar berdasarkan ref model.
  </Accordion>

  <Accordion title="Urutan resolusi variabel environment">
    OpenClaw menyelesaikan auth Copilot dari variabel environment dalam
    urutan prioritas berikut:

    | Prioritas | Variabel              | Catatan                               |
    | --------- | --------------------- | ------------------------------------- |
    | 1         | `COPILOT_GITHUB_TOKEN` | Prioritas tertinggi, khusus Copilot |
    | 2         | `GH_TOKEN`            | Token GitHub CLI (fallback)           |
    | 3         | `GITHUB_TOKEN`        | Token GitHub standar (terendah)       |

    Saat beberapa variabel disetel, OpenClaw menggunakan yang berprioritas tertinggi.
    Alur login perangkat (`openclaw models auth login-github-copilot`) menyimpan
    tokennya di penyimpanan profil auth dan memiliki prioritas di atas semua
    variabel environment.

  </Accordion>

  <Accordion title="Penyimpanan token">
    Login menyimpan token GitHub di penyimpanan profil auth dan menukarkannya
    dengan token API Copilot saat OpenClaw berjalan. Anda tidak perlu mengelola
    token secara manual.
  </Accordion>
</AccordionGroup>

<Warning>
Memerlukan TTY interaktif. Jalankan perintah login langsung di terminal, bukan
di dalam skrip headless atau job CI.
</Warning>

## Terkait

<CardGroup cols={2}>
  <Card title="Pemilihan model" href="/id/concepts/model-providers" icon="layers">
    Memilih provider, ref model, dan perilaku failover.
  </Card>
  <Card title="OAuth dan auth" href="/id/gateway/authentication" icon="key">
    Detail auth dan aturan penggunaan ulang kredensial.
  </Card>
</CardGroup>
