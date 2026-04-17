---
read_when:
    - Mengubah aturan pesan grup atau penyebutan
summary: Perilaku dan konfigurasi untuk penanganan pesan grup WhatsApp (`mentionPatterns` dibagikan di seluruh permukaan)
title: Pesan Grup
x-i18n:
    generated_at: "2026-04-12T23:28:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5d9484dd1de74d42f8dce4c3ac80d60c24864df30a7802e64893ef55506230fe
    source_path: channels/group-messages.md
    workflow: 15
---

# Pesan grup (channel web WhatsApp)

Tujuan: biarkan Clawd tetap berada di grup WhatsApp, aktif hanya saat dipanggil, dan pisahkan thread tersebut dari sesi DM pribadi.

Catatan: `agents.list[].groupChat.mentionPatterns` sekarang juga digunakan oleh Telegram/Discord/Slack/iMessage; dokumen ini berfokus pada perilaku khusus WhatsApp. Untuk penyiapan multi-agent, atur `agents.list[].groupChat.mentionPatterns` per agent (atau gunakan `messages.groupChat.mentionPatterns` sebagai fallback global).

## Implementasi saat ini (2025-12-03)

- Mode aktivasi: `mention` (default) atau `always`. `mention` memerlukan panggilan (WhatsApp @-mention nyata melalui `mentionedJids`, pola regex aman, atau E.164 bot di mana saja dalam teks). `always` membangunkan agent pada setiap pesan, tetapi agent seharusnya hanya membalas saat dapat menambahkan nilai yang bermakna; jika tidak, agent mengembalikan token diam yang persis `NO_REPLY` / `no_reply`. Default dapat diatur di config (`channels.whatsapp.groups`) dan dioverride per grup melalui `/activation`. Saat `channels.whatsapp.groups` diatur, ini juga berfungsi sebagai allowlist grup (sertakan `"*"` untuk mengizinkan semua).
- Kebijakan grup: `channels.whatsapp.groupPolicy` mengontrol apakah pesan grup diterima (`open|disabled|allowlist`). `allowlist` menggunakan `channels.whatsapp.groupAllowFrom` (fallback: `channels.whatsapp.allowFrom` yang eksplisit). Default-nya adalah `allowlist` (diblokir sampai Anda menambahkan pengirim).
- Sesi per grup: kunci sesi terlihat seperti `agent:<agentId>:whatsapp:group:<jid>` sehingga perintah seperti `/verbose on`, `/trace on`, atau `/think high` (dikirim sebagai pesan mandiri) dibatasi untuk grup tersebut; status DM pribadi tidak terpengaruh. Heartbeat dilewati untuk thread grup.
- Injeksi konteks: pesan grup **hanya-pending** (default 50) yang _tidak_ memicu eksekusi diawali di bawah `[Chat messages since your last reply - for context]`, dengan baris pemicu di bawah `[Current message - respond to this]`. Pesan yang sudah ada dalam sesi tidak diinjeksi ulang.
- Penampilan pengirim: setiap batch grup sekarang diakhiri dengan `[from: Sender Name (+E164)]` agar Pi tahu siapa yang sedang berbicara.
- Ephemeral/view-once: kami membuka bungkusnya sebelum mengekstrak teks/mention, sehingga panggilan di dalamnya tetap memicu.
- System prompt grup: pada giliran pertama sesi grup (dan setiap kali `/activation` mengubah mode) kami menyuntikkan uraian singkat ke dalam system prompt seperti `You are replying inside the WhatsApp group "<subject>". Group members: Alice (+44...), Bob (+43...), … Activation: trigger-only … Address the specific sender noted in the message context.` Jika metadata tidak tersedia, kami tetap memberi tahu agent bahwa ini adalah chat grup.

## Contoh config (WhatsApp)

Tambahkan blok `groupChat` ke `~/.openclaw/openclaw.json` agar panggilan nama tampilan berfungsi meskipun WhatsApp menghapus `@` visual di isi teks:

```json5
{
  channels: {
    whatsapp: {
      groups: {
        "*": { requireMention: true },
      },
    },
  },
  agents: {
    list: [
      {
        id: "main",
        groupChat: {
          historyLimit: 50,
          mentionPatterns: ["@?openclaw", "\\+?15555550123"],
        },
      },
    ],
  },
}
```

Catatan:

- Regex bersifat case-insensitive dan menggunakan guardrail safe-regex yang sama seperti permukaan regex config lainnya; pola yang tidak valid dan nested repetition yang tidak aman diabaikan.
- WhatsApp tetap mengirim mention kanonis melalui `mentionedJids` ketika seseorang mengetuk kontak, jadi fallback nomor jarang diperlukan tetapi merupakan jaring pengaman yang berguna.

### Perintah aktivasi (khusus owner)

Gunakan perintah chat grup:

- `/activation mention`
- `/activation always`

Hanya nomor owner (dari `channels.whatsapp.allowFrom`, atau E.164 bot sendiri saat tidak diatur) yang dapat mengubah ini. Kirim `/status` sebagai pesan mandiri di grup untuk melihat mode aktivasi saat ini.

## Cara menggunakan

1. Tambahkan akun WhatsApp Anda (yang menjalankan OpenClaw) ke grup.
2. Ucapkan `@openclaw …` (atau sertakan nomornya). Hanya pengirim dalam allowlist yang dapat memicunya kecuali Anda mengatur `groupPolicy: "open"`.
3. Prompt agent akan menyertakan konteks grup terbaru ditambah penanda `[from: …]` di bagian akhir agar agent dapat menyapa orang yang tepat.
4. Direktif tingkat sesi (`/verbose on`, `/trace on`, `/think high`, `/new` atau `/reset`, `/compact`) hanya berlaku untuk sesi grup tersebut; kirim sebagai pesan mandiri agar terdaftar. Sesi DM pribadi Anda tetap independen.

## Pengujian / verifikasi

- Smoke test manual:
  - Kirim panggilan `@openclaw` di grup dan konfirmasi balasan yang merujuk ke nama pengirim.
  - Kirim panggilan kedua dan verifikasi blok riwayat disertakan lalu dibersihkan pada giliran berikutnya.
- Periksa log gateway (jalankan dengan `--verbose`) untuk melihat entri `inbound web message` yang menampilkan `from: <groupJid>` dan sufiks `[from: …]`.

## Pertimbangan yang diketahui

- Heartbeat sengaja dilewati untuk grup agar tidak menimbulkan siaran yang berisik.
- Penekanan echo menggunakan string batch gabungan; jika Anda mengirim teks yang identik dua kali tanpa mention, hanya yang pertama yang akan mendapat respons.
- Entri penyimpanan sesi akan muncul sebagai `agent:<agentId>:whatsapp:group:<jid>` di session store (`~/.openclaw/agents/<agentId>/sessions/sessions.json` secara default); entri yang tidak ada hanya berarti grup tersebut belum memicu eksekusi.
- Indikator mengetik di grup mengikuti `agents.defaults.typingMode` (default: `message` saat tidak di-mention).
