---
read_when:
    - Anda ingin promosi memori berjalan secara otomatis
    - Anda ingin memahami apa yang dilakukan setiap fase Dreaming
    - Anda ingin menyetel konsolidasi tanpa mengotori `MEMORY.md`
summary: Konsolidasi memori latar belakang dengan fase ringan, dalam, dan REM serta Jurnal Mimpi
title: Dreaming
x-i18n:
    generated_at: "2026-04-15T14:40:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: a5bcaec80f62e7611ed533094ef1917bd72c885f57252824db910e1f0496adc6
    source_path: concepts/dreaming.md
    workflow: 15
---

# Dreaming

Dreaming adalah sistem konsolidasi memori latar belakang di `memory-core`.
Sistem ini membantu OpenClaw memindahkan sinyal jangka pendek yang kuat ke memori tahan lama sambil
menjaga prosesnya tetap dapat dijelaskan dan ditinjau.

Dreaming bersifat **opsional** dan dinonaktifkan secara default.

## Apa yang ditulis oleh dreaming

Dreaming menyimpan dua jenis output:

- **Status mesin** di `memory/.dreams/` (penyimpanan recall, sinyal fase, checkpoint ingestion, lock).
- **Output yang dapat dibaca manusia** di `DREAMS.md` (atau `dreams.md` yang sudah ada) dan file laporan fase opsional di bawah `memory/dreaming/<phase>/YYYY-MM-DD.md`.

Promosi jangka panjang tetap hanya menulis ke `MEMORY.md`.

## Model fase

Dreaming menggunakan tiga fase kooperatif:

| Fase | Tujuan                                   | Penulisan tahan lama |
| ----- | ---------------------------------------- | -------------------- |
| Light | Menyortir dan menyiapkan materi jangka pendek terbaru | Tidak                |
| Deep  | Memberi skor dan mempromosikan kandidat tahan lama    | Ya (`MEMORY.md`)     |
| REM   | Merefleksikan tema dan gagasan yang berulang          | Tidak                |

Fase-fase ini adalah detail implementasi internal, bukan "mode"
terpisah yang dikonfigurasi oleh pengguna.

### Fase Light

Fase Light mengingest sinyal memori harian terbaru dan jejak recall, menghapus duplikasi,
dan menyiapkan baris kandidat.

- Membaca dari status recall jangka pendek, file memori harian terbaru, dan transkrip sesi yang telah disunting jika tersedia.
- Menulis blok `## Light Sleep` yang dikelola ketika penyimpanan mencakup output inline.
- Mencatat sinyal reinforcement untuk pemeringkatan deep nanti.
- Tidak pernah menulis ke `MEMORY.md`.

### Fase Deep

Fase Deep memutuskan apa yang menjadi memori jangka panjang.

- Memeringkat kandidat menggunakan penilaian berbobot dan ambang batas.
- Mengharuskan `minScore`, `minRecallCount`, dan `minUniqueQueries` terpenuhi.
- Menghidrasi ulang cuplikan dari file harian langsung sebelum menulis, sehingga cuplikan usang/terhapus dilewati.
- Menambahkan entri yang dipromosikan ke `MEMORY.md`.
- Menulis ringkasan `## Deep Sleep` ke `DREAMS.md` dan secara opsional menulis `memory/dreaming/deep/YYYY-MM-DD.md`.

### Fase REM

Fase REM mengekstrak pola dan sinyal reflektif.

- Membangun ringkasan tema dan refleksi dari jejak jangka pendek terbaru.
- Menulis blok `## REM Sleep` yang dikelola ketika penyimpanan mencakup output inline.
- Mencatat sinyal reinforcement REM yang digunakan oleh pemeringkatan deep.
- Tidak pernah menulis ke `MEMORY.md`.

## Ingestion transkrip sesi

Dreaming dapat mengingest transkrip sesi yang telah disunting ke dalam korpus dreaming. Saat
transkrip tersedia, transkrip tersebut dimasukkan ke fase Light bersama
sinyal memori harian dan jejak recall. Konten pribadi dan sensitif disunting
sebelum ingestion.

## Jurnal Mimpi

Dreaming juga menyimpan **Jurnal Mimpi** naratif di `DREAMS.md`.
Setelah setiap fase memiliki materi yang cukup, `memory-core` menjalankan giliran subagen latar belakang
best-effort (menggunakan model runtime default) dan menambahkan entri jurnal singkat.

Jurnal ini untuk dibaca manusia di UI Dreams, bukan sumber promosi.
Artefak jurnal/laporan yang dihasilkan Dreaming dikecualikan dari
promosi jangka pendek. Hanya cuplikan memori yang berlandaskan data yang memenuhi syarat untuk dipromosikan ke
`MEMORY.md`.

Ada juga jalur backfill historis yang berlandaskan data untuk pekerjaan peninjauan dan pemulihan:

- `memory rem-harness --path ... --grounded` mempratinjau output jurnal berlandaskan data dari catatan historis `YYYY-MM-DD.md`.
- `memory rem-backfill --path ...` menulis entri jurnal berlandaskan data yang dapat dibalik ke `DREAMS.md`.
- `memory rem-backfill --path ... --stage-short-term` menyiapkan kandidat tahan lama berlandaskan data ke penyimpanan bukti jangka pendek yang sama yang sudah digunakan fase deep normal.
- `memory rem-backfill --rollback` dan `--rollback-short-term` menghapus artefak backfill yang disiapkan tersebut tanpa menyentuh entri jurnal biasa atau recall jangka pendek langsung.

UI Control menampilkan alur backfill/reset jurnal yang sama sehingga Anda dapat memeriksa
hasilnya di scene Dreams sebelum memutuskan apakah kandidat berlandaskan data
layak dipromosikan. Scene juga menampilkan jalur berlandaskan data yang terpisah sehingga Anda dapat melihat
entri jangka pendek yang disiapkan mana yang berasal dari pemutaran ulang historis, item yang dipromosikan
mana yang dipimpin oleh data berlandaskan, dan menghapus hanya entri yang disiapkan khusus berlandaskan data tanpa
menyentuh status jangka pendek langsung biasa.

## Sinyal pemeringkatan Deep

Pemeringkatan Deep menggunakan enam sinyal dasar berbobot ditambah reinforcement fase:

| Sinyal              | Bobot | Deskripsi                                        |
| ------------------- | ----- | ------------------------------------------------ |
| Frekuensi           | 0.24  | Berapa banyak sinyal jangka pendek yang dikumpulkan entri |
| Relevansi           | 0.30  | Kualitas pengambilan rata-rata untuk entri       |
| Keragaman kueri     | 0.15  | Konteks kueri/hari berbeda yang memunculkannya   |
| Keterkinian         | 0.15  | Skor kesegaran dengan peluruhan waktu            |
| Konsolidasi         | 0.10  | Kekuatan kemunculan ulang lintas hari            |
| Kekayaan konseptual | 0.06  | Kepadatan tag konsep dari cuplikan/path          |

Hit fase Light dan REM menambahkan sedikit peningkatan dengan peluruhan keterkinian dari
`memory/.dreams/phase-signals.json`.

## Penjadwalan

Saat diaktifkan, `memory-core` mengelola secara otomatis satu tugas Cron untuk satu sapuan dreaming penuh. Setiap sapuan menjalankan fase secara berurutan: light -> REM -> deep.

Perilaku kadensi default:

| Pengaturan           | Default     |
| -------------------- | ----------- |
| `dreaming.frequency` | `0 3 * * *` |

## Mulai cepat

Aktifkan dreaming:

```json
{
  "plugins": {
    "entries": {
      "memory-core": {
        "config": {
          "dreaming": {
            "enabled": true
          }
        }
      }
    }
  }
}
```

Aktifkan dreaming dengan kadensi sapuan kustom:

```json
{
  "plugins": {
    "entries": {
      "memory-core": {
        "config": {
          "dreaming": {
            "enabled": true,
            "timezone": "America/Los_Angeles",
            "frequency": "0 */6 * * *"
          }
        }
      }
    }
  }
}
```

## Perintah slash

```
/dreaming status
/dreaming on
/dreaming off
/dreaming help
```

## Alur kerja CLI

Gunakan promosi CLI untuk pratinjau atau penerapan manual:

```bash
openclaw memory promote
openclaw memory promote --apply
openclaw memory promote --limit 5
openclaw memory status --deep
```

`memory promote` manual menggunakan ambang fase deep secara default kecuali diganti
dengan flag CLI.

Jelaskan mengapa kandidat tertentu akan atau tidak akan dipromosikan:

```bash
openclaw memory promote-explain "router vlan"
openclaw memory promote-explain "router vlan" --json
```

Pratinjau refleksi REM, kebenaran kandidat, dan output promosi deep tanpa
menulis apa pun:

```bash
openclaw memory rem-harness
openclaw memory rem-harness --json
```

## Nilai default utama

Semua pengaturan berada di bawah `plugins.entries.memory-core.config.dreaming`.

| Kunci       | Default     |
| ----------- | ----------- |
| `enabled`   | `false`     |
| `frequency` | `0 3 * * *` |

Kebijakan fase, ambang batas, dan perilaku penyimpanan adalah detail implementasi
internal (bukan konfigurasi yang dihadapi pengguna).

Lihat [Referensi konfigurasi Memory](/id/reference/memory-config#dreaming)
untuk daftar kunci lengkap.

## UI Dreams

Saat diaktifkan, tab **Dreams** di Gateway menampilkan:

- status aktif dreaming saat ini
- status tingkat fase dan keberadaan sapuan terkelola
- jumlah jangka pendek, berlandaskan data, sinyal, dan yang dipromosikan hari ini
- waktu jadwal eksekusi berikutnya
- jalur Scene berlandaskan data yang terpisah untuk entri pemutaran ulang historis yang disiapkan
- pembaca Jurnal Mimpi yang dapat diperluas yang didukung oleh `doctor.memory.dreamDiary`

## Terkait

- [Memory](/id/concepts/memory)
- [Pencarian Memory](/id/concepts/memory-search)
- [CLI memory](/cli/memory)
- [Referensi konfigurasi Memory](/id/reference/memory-config)
