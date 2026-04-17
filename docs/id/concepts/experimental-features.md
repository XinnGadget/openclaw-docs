---
read_when:
    - Anda melihat kunci konfigurasi `.experimental` dan ingin mengetahui apakah itu stabil
    - Anda ingin mencoba fitur runtime pratinjau tanpa membingungkannya dengan default normal
    - Anda ingin satu tempat untuk menemukan flag eksperimental yang saat ini didokumentasikan
summary: Apa arti flag eksperimental di OpenClaw dan mana saja yang saat ini didokumentasikan
title: Fitur Eksperimental
x-i18n:
    generated_at: "2026-04-15T14:40:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2d1c7b3d4cd56ef8a0bdab1deb9918e9b2c9a33f956d63193246087f8633dcf3
    source_path: concepts/experimental-features.md
    workflow: 15
---

# Fitur eksperimental

Fitur eksperimental di OpenClaw adalah **permukaan pratinjau yang bersifat opt-in**. Fitur-fitur ini
berada di balik flag eksplisit karena masih memerlukan penggunaan di dunia nyata
sebelum layak mendapatkan default yang stabil atau kontrak publik yang
berumur panjang.

Perlakukan ini berbeda dari konfigurasi normal:

- Biarkan **nonaktif secara default** kecuali dokumen terkait menyarankan Anda untuk mencobanya.
- Harapkan **bentuk dan perilaku berubah** lebih cepat dibandingkan konfigurasi stabil.
- Utamakan jalur stabil terlebih dahulu jika sudah tersedia.
- Jika Anda menerapkan OpenClaw secara luas, uji flag eksperimental di lingkungan
  yang lebih kecil sebelum memasukkannya ke baseline bersama.

## Flag yang saat ini didokumentasikan

| Permukaan                | Kunci                                                     | Gunakan saat                                                                                                   | Selengkapnya                                                                                  |
| ------------------------ | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Runtime model lokal      | `agents.defaults.experimental.localModelLean`             | Backend lokal yang lebih kecil atau lebih ketat mengalami kendala dengan permukaan tool default penuh OpenClaw | [Model Lokal](/id/gateway/local-models)                                                          |
| Pencarian memori         | `agents.defaults.memorySearch.experimental.sessionMemory` | Anda ingin `memory_search` mengindeks transkrip sesi sebelumnya dan menerima biaya penyimpanan/pengindeksan tambahan | [Referensi konfigurasi memori](/id/reference/memory-config#session-memory-search-experimental) |
| Tool perencanaan terstruktur | `tools.experimental.planTool`                         | Anda ingin tool `update_plan` terstruktur diekspos untuk pelacakan pekerjaan multi-langkah di runtime dan UI yang kompatibel | [Referensi konfigurasi Gateway](/id/gateway/configuration-reference#toolsexperimental)         |

## Mode lean model lokal

`agents.defaults.experimental.localModelLean: true` adalah katup pelepas tekanan
untuk penyiapan model lokal yang lebih lemah. Ini memangkas tool default yang
berat seperti `browser`, `cron`, dan `message` sehingga bentuk prompt menjadi lebih kecil dan kurang rapuh
untuk backend kompatibel OpenAI yang memiliki konteks kecil atau lebih ketat.

Ini memang **bukan** jalur normal. Jika backend Anda menangani runtime penuh
dengan baik, biarkan ini nonaktif.

## Eksperimental bukan berarti tersembunyi

Jika sebuah fitur bersifat eksperimental, OpenClaw harus menyatakannya dengan
jelas di dokumen dan di jalur konfigurasinya sendiri. Yang **tidak** boleh
dilakukan adalah menyelundupkan perilaku pratinjau ke dalam knob default yang
terlihat stabil lalu berpura-pura itu normal. Begitulah cara permukaan
konfigurasi menjadi berantakan.
