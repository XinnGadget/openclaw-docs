---
read_when:
    - Anda ingin mengonfigurasi Perplexity sebagai provider pencarian web
    - Anda memerlukan API key Perplexity atau setup proxy OpenRouter
summary: Setup provider pencarian web Perplexity (API key, mode pencarian, pemfilteran)
title: Perplexity
x-i18n:
    generated_at: "2026-04-12T23:32:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: 55c089e96601ebe05480d305364272c7f0ac721caa79746297c73002a9f20f55
    source_path: providers/perplexity-provider.md
    workflow: 15
---

# Perplexity (Provider Pencarian Web)

Plugin Perplexity menyediakan kapabilitas pencarian web melalui Perplexity
Search API atau Perplexity Sonar melalui OpenRouter.

<Note>
Halaman ini membahas setup **provider** Perplexity. Untuk **tool**
Perplexity (bagaimana agen menggunakannya), lihat [Tool Perplexity](/id/tools/perplexity-search).
</Note>

| Properti    | Nilai                                                                 |
| ----------- | --------------------------------------------------------------------- |
| Tipe        | Provider pencarian web (bukan provider model)                         |
| Auth        | `PERPLEXITY_API_KEY` (langsung) atau `OPENROUTER_API_KEY` (melalui OpenRouter) |
| Path config | `plugins.entries.perplexity.config.webSearch.apiKey`                  |

## Memulai

<Steps>
  <Step title="Atur API key">
    Jalankan flow konfigurasi pencarian web interaktif:

    ```bash
    openclaw configure --section web
    ```

    Atau atur key secara langsung:

    ```bash
    openclaw config set plugins.entries.perplexity.config.webSearch.apiKey "pplx-xxxxxxxxxxxx"
    ```

  </Step>
  <Step title="Mulai mencari">
    Agen akan otomatis menggunakan Perplexity untuk pencarian web setelah key
    dikonfigurasi. Tidak diperlukan langkah tambahan.
  </Step>
</Steps>

## Mode pencarian

Plugin otomatis memilih transport berdasarkan prefiks API key:

<Tabs>
  <Tab title="Native Perplexity API (pplx-)">
    Saat key Anda diawali dengan `pplx-`, OpenClaw menggunakan Perplexity Search
    API native. Transport ini mengembalikan hasil terstruktur dan mendukung filter domain, bahasa,
    dan tanggal (lihat opsi pemfilteran di bawah).
  </Tab>
  <Tab title="OpenRouter / Sonar (sk-or-)">
    Saat key Anda diawali dengan `sk-or-`, OpenClaw merutekan melalui OpenRouter menggunakan
    model Perplexity Sonar. Transport ini mengembalikan jawaban yang disintesis AI dengan
    sitasi.
  </Tab>
</Tabs>

| Prefiks key | Transport                    | Fitur                                            |
| ----------- | ---------------------------- | ------------------------------------------------ |
| `pplx-`     | Native Perplexity Search API | Hasil terstruktur, filter domain/bahasa/tanggal  |
| `sk-or-`    | OpenRouter (Sonar)           | Jawaban yang disintesis AI dengan sitasi         |

## Pemfilteran Native API

<Note>
Opsi pemfilteran hanya tersedia saat menggunakan Native Perplexity API
(key `pplx-`). Pencarian OpenRouter/Sonar tidak mendukung parameter ini.
</Note>

Saat menggunakan Native Perplexity API, pencarian mendukung filter berikut:

| Filter          | Deskripsi                             | Contoh                              |
| --------------- | ------------------------------------- | ----------------------------------- |
| Negara          | Kode negara 2 huruf                   | `us`, `de`, `jp`                    |
| Bahasa          | Kode bahasa ISO 639-1                 | `en`, `fr`, `zh`                    |
| Rentang tanggal | Jendela kekinian                      | `day`, `week`, `month`, `year`      |
| Filter domain   | Allowlist atau denylist (maks 20 domain) | `example.com`                    |
| Anggaran konten | Batas token per respons / per halaman | `max_tokens`, `max_tokens_per_page` |

## Catatan lanjutan

<AccordionGroup>
  <Accordion title="Environment variable untuk proses daemon">
    Jika OpenClaw Gateway berjalan sebagai daemon (launchd/systemd), pastikan
    `PERPLEXITY_API_KEY` tersedia untuk proses tersebut.

    <Warning>
    Key yang hanya diatur di `~/.profile` tidak akan terlihat oleh daemon launchd/systemd
    kecuali environment tersebut diimpor secara eksplisit. Atur key di
    `~/.openclaw/.env` atau melalui `env.shellEnv` untuk memastikan proses gateway dapat
    membacanya.
    </Warning>

  </Accordion>

  <Accordion title="Setup proxy OpenRouter">
    Jika Anda lebih memilih merutekan pencarian Perplexity melalui OpenRouter, atur
    `OPENROUTER_API_KEY` (prefiks `sk-or-`) alih-alih key Perplexity native.
    OpenClaw akan mendeteksi prefiks tersebut dan otomatis beralih ke transport Sonar.

    <Tip>
    Transport OpenRouter berguna jika Anda sudah memiliki akun OpenRouter
    dan menginginkan penagihan terpusat di beberapa provider.
    </Tip>

  </Accordion>
</AccordionGroup>

## Terkait

<CardGroup cols={2}>
  <Card title="Tool pencarian Perplexity" href="/id/tools/perplexity-search" icon="magnifying-glass">
    Cara agen memanggil pencarian Perplexity dan menafsirkan hasilnya.
  </Card>
  <Card title="Referensi konfigurasi" href="/id/gateway/configuration-reference" icon="gear">
    Referensi konfigurasi lengkap termasuk entri plugin.
  </Card>
</CardGroup>
