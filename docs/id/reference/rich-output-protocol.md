---
x-i18n:
    generated_at: "2026-04-11T15:15:49Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2a8884fc2c304bf96d4675f0c1d1ff781d6dc1ae8c49d92ce08040c9c7709035
    source_path: reference/rich-output-protocol.md
    workflow: 15
---

# Protokol Output Kaya

Output asisten dapat membawa sekumpulan kecil arahan pengiriman/perenderan:

- `MEDIA:` untuk pengiriman lampiran
- `[[audio_as_voice]]` untuk petunjuk penyajian audio
- `[[reply_to_current]]` / `[[reply_to:<id>]]` untuk metadata balasan
- `[embed ...]` untuk perenderan kaya UI Kontrol

Arahan ini terpisah. `MEDIA:` dan tag balasan/suara tetap merupakan metadata pengiriman; `[embed ...]` adalah jalur render kaya khusus web.

## `[embed ...]`

`[embed ...]` adalah satu-satunya sintaks render kaya yang ditujukan untuk agen bagi UI Kontrol.

Contoh self-closing:

```text
[embed ref="cv_123" title="Status" /]
```

Aturan:

- `[view ...]` tidak lagi valid untuk output baru.
- Kode pendek embed dirender hanya di permukaan pesan asisten.
- Hanya embed berbasis URL yang dirender. Gunakan `ref="..."` atau `url="..."`.
- Kode pendek embed HTML inline berbentuk blok tidak dirender.
- UI web menghapus kode pendek dari teks yang terlihat dan merender embed secara inline.
- `MEDIA:` bukan alias embed dan tidak boleh digunakan untuk perenderan embed kaya.

## Bentuk Perenderan yang Disimpan

Blok konten asisten yang dinormalisasi/disimpan adalah item `canvas` terstruktur:

```json
{
  "type": "canvas",
  "preview": {
    "kind": "canvas",
    "surface": "assistant_message",
    "render": "url",
    "viewId": "cv_123",
    "url": "/__openclaw__/canvas/documents/cv_123/index.html",
    "title": "Status",
    "preferredHeight": 320
  }
}
```

Blok kaya yang disimpan/dirender menggunakan bentuk `canvas` ini secara langsung. `present_view` tidak dikenali.
