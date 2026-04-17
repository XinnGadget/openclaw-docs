---
read_when:
    - Mengerjakan fitur saluran Microsoft Teams
summary: Status dukungan, kemampuan, dan konfigurasi bot Microsoft Teams
title: Microsoft Teams
x-i18n:
    generated_at: "2026-04-12T00:18:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3e6841a618fb030e4c2029b3652d45dedd516392e2ae17309ff46b93648ffb79
    source_path: channels/msteams.md
    workflow: 15
---

# Microsoft Teams

> "Tinggalkan segala harapan, wahai kalian yang masuk ke sini."

Diperbarui: 2026-03-25

Status: teks + lampiran DM didukung; pengiriman file saluran/grup memerlukan `sharePointSiteId` + izin Graph (lihat [Mengirim file di obrolan grup](#sending-files-in-group-chats)). Polls dikirim melalui Adaptive Cards. Tindakan pesan mengekspos `upload-file` yang eksplisit untuk pengiriman yang mengutamakan file.

## Plugin bawaan

Microsoft Teams dikirim sebagai plugin bawaan dalam rilis OpenClaw saat ini, jadi
tidak diperlukan instalasi terpisah pada build paket normal.

Jika Anda menggunakan build lama atau instalasi kustom yang tidak menyertakan Teams bawaan,
instal secara manual:

```bash
openclaw plugins install @openclaw/msteams
```

Checkout lokal (saat berjalan dari repo git):

```bash
openclaw plugins install ./path/to/local/msteams-plugin
```

Detail: [Plugins](/id/tools/plugin)

## Penyiapan cepat (pemula)

1. Pastikan plugin Microsoft Teams tersedia.
   - Rilis OpenClaw paket saat ini sudah menyertakannya secara bawaan.
   - Instalasi lama/kustom dapat menambahkannya secara manual dengan perintah di atas.
2. Buat **Azure Bot** (App ID + client secret + tenant ID).
3. Konfigurasikan OpenClaw dengan kredensial tersebut.
4. Ekspos `/api/messages` (port 3978 secara default) melalui URL publik atau tunnel.
5. Instal paket aplikasi Teams dan jalankan gateway.

Konfigurasi minimal (client secret):

```json5
{
  channels: {
    msteams: {
      enabled: true,
      appId: "<APP_ID>",
      appPassword: "<APP_PASSWORD>",
      tenantId: "<TENANT_ID>",
      webhook: { port: 3978, path: "/api/messages" },
    },
  },
}
```

Untuk deployment produksi, pertimbangkan menggunakan [autentikasi federasi](#federated-authentication-certificate--managed-identity) (sertifikat atau managed identity) alih-alih client secret.

Catatan: obrolan grup diblokir secara default (`channels.msteams.groupPolicy: "allowlist"`). Untuk mengizinkan balasan grup, setel `channels.msteams.groupAllowFrom` (atau gunakan `groupPolicy: "open"` untuk mengizinkan anggota mana pun, dengan gerbang mention).

## Tujuan

- Berbicara dengan OpenClaw melalui DM Teams, obrolan grup, atau saluran.
- Menjaga perutean tetap deterministik: balasan selalu kembali ke saluran tempat pesan datang.
- Menggunakan perilaku saluran yang aman secara default (mention wajib kecuali dikonfigurasi sebaliknya).

## Penulisan konfigurasi

Secara default, Microsoft Teams diizinkan menulis pembaruan konfigurasi yang dipicu oleh `/config set|unset` (memerlukan `commands.config: true`).

Nonaktifkan dengan:

```json5
{
  channels: { msteams: { configWrites: false } },
}
```

## Kontrol akses (DM + grup)

**Akses DM**

- Default: `channels.msteams.dmPolicy = "pairing"`. Pengirim yang tidak dikenal diabaikan sampai disetujui.
- `channels.msteams.allowFrom` sebaiknya menggunakan ID objek AAD yang stabil.
- UPN/nama tampilan dapat berubah; pencocokan langsung dinonaktifkan secara default dan hanya diaktifkan dengan `channels.msteams.dangerouslyAllowNameMatching: true`.
- Wizard dapat menyelesaikan nama menjadi ID melalui Microsoft Graph jika kredensial mengizinkan.

**Akses grup**

- Default: `channels.msteams.groupPolicy = "allowlist"` (diblokir kecuali Anda menambahkan `groupAllowFrom`). Gunakan `channels.defaults.groupPolicy` untuk mengganti default saat tidak disetel.
- `channels.msteams.groupAllowFrom` mengontrol pengirim mana yang dapat memicu di obrolan grup/saluran (fallback ke `channels.msteams.allowFrom`).
- Setel `groupPolicy: "open"` untuk mengizinkan anggota mana pun (tetap dengan gerbang mention secara default).
- Untuk mengizinkan **tidak ada saluran**, setel `channels.msteams.groupPolicy: "disabled"`.

Contoh:

```json5
{
  channels: {
    msteams: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["user@org.com"],
    },
  },
}
```

**Allowlist Teams + saluran**

- Batasi balasan grup/saluran dengan mencantumkan teams dan saluran di bawah `channels.msteams.teams`.
- Kunci sebaiknya menggunakan ID team yang stabil dan ID percakapan saluran.
- Saat `groupPolicy="allowlist"` dan allowlist teams tersedia, hanya teams/saluran yang tercantum yang diterima (dengan gerbang mention).
- Wizard konfigurasi menerima entri `Team/Channel` dan menyimpannya untuk Anda.
- Saat startup, OpenClaw menyelesaikan nama team/saluran dan nama pengguna pada allowlist menjadi ID (jika izin Graph mengizinkan)
  dan mencatat pemetaannya; nama team/saluran yang tidak terselesaikan tetap disimpan seperti yang diketik tetapi diabaikan untuk perutean secara default kecuali `channels.msteams.dangerouslyAllowNameMatching: true` diaktifkan.

Contoh:

```json5
{
  channels: {
    msteams: {
      groupPolicy: "allowlist",
      teams: {
        "My Team": {
          channels: {
            General: { requireMention: true },
          },
        },
      },
    },
  },
}
```

## Cara kerjanya

1. Pastikan plugin Microsoft Teams tersedia.
   - Rilis OpenClaw paket saat ini sudah menyertakannya secara bawaan.
   - Instalasi lama/kustom dapat menambahkannya secara manual dengan perintah di atas.
2. Buat **Azure Bot** (App ID + secret + tenant ID).
3. Bangun **paket aplikasi Teams** yang mereferensikan bot dan menyertakan izin RSC di bawah ini.
4. Unggah/instal aplikasi Teams ke dalam team (atau cakupan personal untuk DM).
5. Konfigurasikan `msteams` di `~/.openclaw/openclaw.json` (atau env vars) dan jalankan gateway.
6. Gateway mendengarkan lalu lintas webhook Bot Framework pada `/api/messages` secara default.

## Penyiapan Azure Bot (Prasyarat)

Sebelum mengonfigurasi OpenClaw, Anda perlu membuat resource Azure Bot.

### Langkah 1: Buat Azure Bot

1. Buka [Create Azure Bot](https://portal.azure.com/#create/Microsoft.AzureBot)
2. Isi tab **Basics**:

   | Field              | Value                                                            |
   | ------------------ | ---------------------------------------------------------------- |
   | **Bot handle**     | Nama bot Anda, misalnya `openclaw-msteams` (harus unik)          |
   | **Subscription**   | Pilih langganan Azure Anda                                       |
   | **Resource group** | Buat baru atau gunakan yang sudah ada                            |
   | **Pricing tier**   | **Free** untuk dev/pengujian                                     |
   | **Type of App**    | **Single Tenant** (disarankan - lihat catatan di bawah)          |
   | **Creation type**  | **Create new Microsoft App ID**                                  |

> **Pemberitahuan deprecasi:** Pembuatan bot multi-tenant baru telah deprecated setelah 2025-07-31. Gunakan **Single Tenant** untuk bot baru.

3. Klik **Review + create** → **Create** (tunggu ~1-2 menit)

### Langkah 2: Dapatkan Kredensial

1. Buka resource Azure Bot Anda → **Configuration**
2. Salin **Microsoft App ID** → ini adalah `appId` Anda
3. Klik **Manage Password** → buka App Registration
4. Di bawah **Certificates & secrets** → **New client secret** → salin **Value** → ini adalah `appPassword` Anda
5. Buka **Overview** → salin **Directory (tenant) ID** → ini adalah `tenantId` Anda

### Langkah 3: Konfigurasikan Endpoint Pesan

1. Di Azure Bot → **Configuration**
2. Setel **Messaging endpoint** ke URL webhook Anda:
   - Produksi: `https://your-domain.com/api/messages`
   - Dev lokal: Gunakan tunnel (lihat [Pengembangan Lokal](#local-development-tunneling) di bawah)

### Langkah 4: Aktifkan Saluran Teams

1. Di Azure Bot → **Channels**
2. Klik **Microsoft Teams** → Configure → Save
3. Setujui Terms of Service

## Autentikasi Federasi (Sertifikat + Managed Identity)

> Ditambahkan pada 2026.3.24

Untuk deployment produksi, OpenClaw mendukung **autentikasi federasi** sebagai alternatif yang lebih aman dibandingkan client secret. Tersedia dua metode:

### Opsi A: Autentikasi berbasis sertifikat

Gunakan sertifikat PEM yang terdaftar pada app registration Entra ID Anda.

**Penyiapan:**

1. Buat atau dapatkan sertifikat (format PEM dengan private key).
2. Di Entra ID → App Registration → **Certificates & secrets** → **Certificates** → unggah sertifikat publik.

**Konfigurasi:**

```json5
{
  channels: {
    msteams: {
      enabled: true,
      appId: "<APP_ID>",
      tenantId: "<TENANT_ID>",
      authType: "federated",
      certificatePath: "/path/to/cert.pem",
      webhook: { port: 3978, path: "/api/messages" },
    },
  },
}
```

**Env vars:**

- `MSTEAMS_AUTH_TYPE=federated`
- `MSTEAMS_CERTIFICATE_PATH=/path/to/cert.pem`

### Opsi B: Azure Managed Identity

Gunakan Azure Managed Identity untuk autentikasi tanpa kata sandi. Ini ideal untuk deployment pada infrastruktur Azure (AKS, App Service, Azure VM) yang memiliki managed identity.

**Cara kerjanya:**

1. Pod/VM bot memiliki managed identity (system-assigned atau user-assigned).
2. Sebuah **federated identity credential** menautkan managed identity ke app registration Entra ID.
3. Saat runtime, OpenClaw menggunakan `@azure/identity` untuk memperoleh token dari endpoint Azure IMDS (`169.254.169.254`).
4. Token diteruskan ke SDK Teams untuk autentikasi bot.

**Prasyarat:**

- Infrastruktur Azure dengan managed identity diaktifkan (AKS workload identity, App Service, VM)
- Federated identity credential dibuat pada app registration Entra ID
- Akses jaringan ke IMDS (`169.254.169.254:80`) dari pod/VM

**Konfigurasi (system-assigned managed identity):**

```json5
{
  channels: {
    msteams: {
      enabled: true,
      appId: "<APP_ID>",
      tenantId: "<TENANT_ID>",
      authType: "federated",
      useManagedIdentity: true,
      webhook: { port: 3978, path: "/api/messages" },
    },
  },
}
```

**Konfigurasi (user-assigned managed identity):**

```json5
{
  channels: {
    msteams: {
      enabled: true,
      appId: "<APP_ID>",
      tenantId: "<TENANT_ID>",
      authType: "federated",
      useManagedIdentity: true,
      managedIdentityClientId: "<MI_CLIENT_ID>",
      webhook: { port: 3978, path: "/api/messages" },
    },
  },
}
```

**Env vars:**

- `MSTEAMS_AUTH_TYPE=federated`
- `MSTEAMS_USE_MANAGED_IDENTITY=true`
- `MSTEAMS_MANAGED_IDENTITY_CLIENT_ID=<client-id>` (hanya untuk user-assigned)

### Penyiapan AKS Workload Identity

Untuk deployment AKS yang menggunakan workload identity:

1. **Aktifkan workload identity** pada cluster AKS Anda.
2. **Buat federated identity credential** pada app registration Entra ID:

   ```bash
   az ad app federated-credential create --id <APP_OBJECT_ID> --parameters '{
     "name": "my-bot-workload-identity",
     "issuer": "<AKS_OIDC_ISSUER_URL>",
     "subject": "system:serviceaccount:<NAMESPACE>:<SERVICE_ACCOUNT>",
     "audiences": ["api://AzureADTokenExchange"]
   }'
   ```

3. **Tambahkan anotasi pada service account Kubernetes** dengan app client ID:

   ```yaml
   apiVersion: v1
   kind: ServiceAccount
   metadata:
     name: my-bot-sa
     annotations:
       azure.workload.identity/client-id: "<APP_CLIENT_ID>"
   ```

4. **Tambahkan label pada pod** untuk injeksi workload identity:

   ```yaml
   metadata:
     labels:
       azure.workload.identity/use: "true"
   ```

5. **Pastikan akses jaringan** ke IMDS (`169.254.169.254`) — jika menggunakan NetworkPolicy, tambahkan aturan egress yang mengizinkan lalu lintas ke `169.254.169.254/32` pada port 80.

### Perbandingan jenis autentikasi

| Method               | Config                                         | Pros                                  | Cons                                     |
| -------------------- | ---------------------------------------------- | ------------------------------------- | ---------------------------------------- |
| **Client secret**    | `appPassword`                                  | Penyiapan sederhana                   | Perlu rotasi secret, kurang aman         |
| **Certificate**      | `authType: "federated"` + `certificatePath`    | Tidak ada shared secret di jaringan   | Ada beban pengelolaan sertifikat         |
| **Managed Identity** | `authType: "federated"` + `useManagedIdentity` | Tanpa kata sandi, tidak perlu kelola secret | Memerlukan infrastruktur Azure      |

**Perilaku default:** Saat `authType` tidak disetel, OpenClaw secara default menggunakan autentikasi client secret. Konfigurasi yang ada tetap berfungsi tanpa perubahan.

## Pengembangan Lokal (Tunneling)

Teams tidak dapat menjangkau `localhost`. Gunakan tunnel untuk pengembangan lokal:

**Opsi A: ngrok**

```bash
ngrok http 3978
# Salin URL https, misalnya https://abc123.ngrok.io
# Setel messaging endpoint ke: https://abc123.ngrok.io/api/messages
```

**Opsi B: Tailscale Funnel**

```bash
tailscale funnel 3978
# Gunakan URL funnel Tailscale Anda sebagai messaging endpoint
```

## Teams Developer Portal (Alternatif)

Alih-alih membuat ZIP manifest secara manual, Anda dapat menggunakan [Teams Developer Portal](https://dev.teams.microsoft.com/apps):

1. Klik **+ New app**
2. Isi info dasar (nama, deskripsi, info pengembang)
3. Buka **App features** → **Bot**
4. Pilih **Enter a bot ID manually** dan tempel Azure Bot App ID Anda
5. Centang cakupan: **Personal**, **Team**, **Group Chat**
6. Klik **Distribute** → **Download app package**
7. Di Teams: **Apps** → **Manage your apps** → **Upload a custom app** → pilih ZIP

Ini sering kali lebih mudah daripada mengedit manifest JSON secara manual.

## Menguji Bot

**Opsi A: Azure Web Chat (verifikasi webhook terlebih dahulu)**

1. Di Azure Portal → resource Azure Bot Anda → **Test in Web Chat**
2. Kirim pesan - Anda seharusnya melihat respons
3. Ini mengonfirmasi endpoint webhook Anda berfungsi sebelum penyiapan Teams

**Opsi B: Teams (setelah instalasi aplikasi)**

1. Instal aplikasi Teams (sideload atau katalog organisasi)
2. Temukan bot di Teams dan kirim DM
3. Periksa log gateway untuk aktivitas masuk

## Penyiapan (minimal hanya teks)

1. **Pastikan plugin Microsoft Teams tersedia**
   - Rilis OpenClaw paket saat ini sudah menyertakannya secara bawaan.
   - Instalasi lama/kustom dapat menambahkannya secara manual:
     - Dari npm: `openclaw plugins install @openclaw/msteams`
     - Dari checkout lokal: `openclaw plugins install ./path/to/local/msteams-plugin`

2. **Pendaftaran bot**
   - Buat Azure Bot (lihat di atas) dan catat:
     - App ID
     - Client secret (App password)
     - Tenant ID (single-tenant)

3. **Manifest aplikasi Teams**
   - Sertakan entri `bot` dengan `botId = <App ID>`.
   - Cakupan: `personal`, `team`, `groupChat`.
   - `supportsFiles: true` (wajib untuk penanganan file pada cakupan personal).
   - Tambahkan izin RSC (di bawah).
   - Buat ikon: `outline.png` (32x32) dan `color.png` (192x192).
   - Zip ketiga file bersama-sama: `manifest.json`, `outline.png`, `color.png`.

4. **Konfigurasikan OpenClaw**

   ```json5
   {
     channels: {
       msteams: {
         enabled: true,
         appId: "<APP_ID>",
         appPassword: "<APP_PASSWORD>",
         tenantId: "<TENANT_ID>",
         webhook: { port: 3978, path: "/api/messages" },
       },
     },
   }
   ```

   Anda juga dapat menggunakan environment variable alih-alih kunci konfigurasi:
   - `MSTEAMS_APP_ID`
   - `MSTEAMS_APP_PASSWORD`
   - `MSTEAMS_TENANT_ID`
   - `MSTEAMS_AUTH_TYPE` (opsional: `"secret"` atau `"federated"`)
   - `MSTEAMS_CERTIFICATE_PATH` (federated + sertifikat)
   - `MSTEAMS_CERTIFICATE_THUMBPRINT` (opsional, tidak wajib untuk autentikasi)
   - `MSTEAMS_USE_MANAGED_IDENTITY` (federated + managed identity)
   - `MSTEAMS_MANAGED_IDENTITY_CLIENT_ID` (hanya untuk user-assigned MI)

5. **Endpoint bot**
   - Setel Azure Bot Messaging Endpoint ke:
     - `https://<host>:3978/api/messages` (atau path/port pilihan Anda).

6. **Jalankan gateway**
   - Saluran Teams dimulai secara otomatis saat plugin bawaan atau plugin yang diinstal manual tersedia dan konfigurasi `msteams` ada beserta kredensialnya.

## Tindakan info anggota

OpenClaw mengekspos tindakan `member-info` berbasis Graph untuk Microsoft Teams agar agen dan otomasi dapat menyelesaikan detail anggota saluran (nama tampilan, email, peran) langsung dari Microsoft Graph.

Persyaratan:

- Izin RSC `Member.Read.Group` (sudah ada dalam manifest yang direkomendasikan)
- Untuk lookup lintas team: izin Aplikasi Graph `User.Read.All` dengan admin consent

Tindakan ini dikendalikan oleh `channels.msteams.actions.memberInfo` (default: aktif saat kredensial Graph tersedia).

## Konteks riwayat

- `channels.msteams.historyLimit` mengontrol berapa banyak pesan saluran/grup terbaru yang dibungkus ke dalam prompt.
- Fallback ke `messages.groupChat.historyLimit`. Setel `0` untuk menonaktifkan (default 50).
- Riwayat thread yang diambil difilter berdasarkan allowlist pengirim (`allowFrom` / `groupAllowFrom`), jadi penyemaian konteks thread hanya menyertakan pesan dari pengirim yang diizinkan.
- Konteks lampiran kutipan (`ReplyTo*` yang diturunkan dari HTML balasan Teams) saat ini diteruskan sebagaimana diterima.
- Dengan kata lain, allowlist mengendalikan siapa yang dapat memicu agen; saat ini hanya jalur konteks tambahan tertentu yang difilter.
- Riwayat DM dapat dibatasi dengan `channels.msteams.dmHistoryLimit` (giliran pengguna). Override per pengguna: `channels.msteams.dms["<user_id>"].historyLimit`.

## Izin RSC Teams Saat Ini (Manifest)

Ini adalah **izin resourceSpecific yang ada** dalam manifest aplikasi Teams kami. Izin ini hanya berlaku di dalam team/chat tempat aplikasi diinstal.

**Untuk saluran (cakupan team):**

- `ChannelMessage.Read.Group` (Application) - menerima semua pesan saluran tanpa @mention
- `ChannelMessage.Send.Group` (Application)
- `Member.Read.Group` (Application)
- `Owner.Read.Group` (Application)
- `ChannelSettings.Read.Group` (Application)
- `TeamMember.Read.Group` (Application)
- `TeamSettings.Read.Group` (Application)

**Untuk obrolan grup:**

- `ChatMessage.Read.Chat` (Application) - menerima semua pesan obrolan grup tanpa @mention

## Contoh Manifest Teams (disamarkan)

Contoh minimal yang valid dengan field yang diperlukan. Ganti ID dan URL.

```json5
{
  $schema: "https://developer.microsoft.com/en-us/json-schemas/teams/v1.23/MicrosoftTeams.schema.json",
  manifestVersion: "1.23",
  version: "1.0.0",
  id: "00000000-0000-0000-0000-000000000000",
  name: { short: "OpenClaw" },
  developer: {
    name: "Your Org",
    websiteUrl: "https://example.com",
    privacyUrl: "https://example.com/privacy",
    termsOfUseUrl: "https://example.com/terms",
  },
  description: { short: "OpenClaw in Teams", full: "OpenClaw in Teams" },
  icons: { outline: "outline.png", color: "color.png" },
  accentColor: "#5B6DEF",
  bots: [
    {
      botId: "11111111-1111-1111-1111-111111111111",
      scopes: ["personal", "team", "groupChat"],
      isNotificationOnly: false,
      supportsCalling: false,
      supportsVideo: false,
      supportsFiles: true,
    },
  ],
  webApplicationInfo: {
    id: "11111111-1111-1111-1111-111111111111",
  },
  authorization: {
    permissions: {
      resourceSpecific: [
        { name: "ChannelMessage.Read.Group", type: "Application" },
        { name: "ChannelMessage.Send.Group", type: "Application" },
        { name: "Member.Read.Group", type: "Application" },
        { name: "Owner.Read.Group", type: "Application" },
        { name: "ChannelSettings.Read.Group", type: "Application" },
        { name: "TeamMember.Read.Group", type: "Application" },
        { name: "TeamSettings.Read.Group", type: "Application" },
        { name: "ChatMessage.Read.Chat", type: "Application" },
      ],
    },
  },
}
```

### Catatan manifest (field yang wajib ada)

- `bots[].botId` **harus** cocok dengan Azure Bot App ID.
- `webApplicationInfo.id` **harus** cocok dengan Azure Bot App ID.
- `bots[].scopes` harus menyertakan permukaan yang ingin Anda gunakan (`personal`, `team`, `groupChat`).
- `bots[].supportsFiles: true` wajib untuk penanganan file pada cakupan personal.
- `authorization.permissions.resourceSpecific` harus menyertakan pembacaan/pengiriman saluran jika Anda menginginkan lalu lintas saluran.

### Memperbarui aplikasi yang sudah ada

Untuk memperbarui aplikasi Teams yang sudah terinstal (misalnya, untuk menambahkan izin RSC):

1. Perbarui `manifest.json` Anda dengan pengaturan baru
2. **Naikkan field `version`** (misalnya `1.0.0` → `1.1.0`)
3. **Zip ulang** manifest dengan ikon (`manifest.json`, `outline.png`, `color.png`)
4. Unggah zip baru:
   - **Opsi A (Teams Admin Center):** Teams Admin Center → Teams apps → Manage apps → temukan aplikasi Anda → Upload new version
   - **Opsi B (Sideload):** Di Teams → Apps → Manage your apps → Upload a custom app
5. **Untuk saluran team:** Instal ulang aplikasi di setiap team agar izin baru berlaku
6. **Keluar sepenuhnya dan luncurkan ulang Teams** (bukan hanya menutup jendela) untuk menghapus metadata aplikasi yang tersimpan di cache

## Kemampuan: hanya RSC vs Graph

### Dengan **Teams RSC saja** (aplikasi terinstal, tanpa izin API Graph)

Berfungsi:

- Membaca konten **teks** pesan saluran.
- Mengirim konten **teks** pesan saluran.
- Menerima lampiran file **personal (DM)**.

TIDAK berfungsi:

- Konten **gambar atau file** saluran/grup (payload hanya menyertakan stub HTML).
- Mengunduh lampiran yang disimpan di SharePoint/OneDrive.
- Membaca riwayat pesan (di luar event webhook langsung).

### Dengan **Teams RSC + izin Aplikasi Microsoft Graph**

Menambahkan:

- Mengunduh konten yang di-host (gambar yang ditempel ke dalam pesan).
- Mengunduh lampiran file yang disimpan di SharePoint/OneDrive.
- Membaca riwayat pesan saluran/chat melalui Graph.

### RSC vs Graph API

| Capability              | RSC Permissions       | Graph API                               |
| ----------------------- | --------------------- | --------------------------------------- |
| **Pesan real-time**     | Ya (melalui webhook)  | Tidak (hanya polling)                   |
| **Pesan historis**      | Tidak                 | Ya (dapat mengkueri riwayat)            |
| **Kompleksitas setup**  | Hanya manifest aplikasi | Memerlukan admin consent + alur token |
| **Berfungsi offline**   | Tidak (harus berjalan) | Ya (dapat mengkueri kapan saja)       |

**Intinya:** RSC adalah untuk mendengarkan secara real-time; Graph API adalah untuk akses historis. Untuk mengejar pesan yang terlewat saat offline, Anda memerlukan Graph API dengan `ChannelMessage.Read.All` (memerlukan admin consent).

## Media + riwayat dengan Graph (wajib untuk saluran)

Jika Anda memerlukan gambar/file di **saluran** atau ingin mengambil **riwayat pesan**, Anda harus mengaktifkan izin Microsoft Graph dan memberikan admin consent.

1. Di **App Registration** Entra ID (Azure AD), tambahkan izin **Aplikasi** Microsoft Graph:
   - `ChannelMessage.Read.All` (lampiran saluran + riwayat)
   - `Chat.Read.All` atau `ChatMessage.Read.All` (obrolan grup)
2. **Berikan admin consent** untuk tenant.
3. Naikkan **versi manifest** aplikasi Teams, unggah ulang, dan **instal ulang aplikasi di Teams**.
4. **Keluar sepenuhnya dan luncurkan ulang Teams** untuk menghapus metadata aplikasi yang tersimpan di cache.

**Izin tambahan untuk mention pengguna:** @mention pengguna berfungsi langsung untuk pengguna yang ada dalam percakapan. Namun, jika Anda ingin mencari dan menyebut pengguna secara dinamis yang **tidak ada dalam percakapan saat ini**, tambahkan izin `User.Read.All` (Application) dan berikan admin consent.

## Keterbatasan yang Diketahui

### Timeout webhook

Teams mengirimkan pesan melalui webhook HTTP. Jika pemrosesan memakan waktu terlalu lama (misalnya, respons LLM lambat), Anda mungkin melihat:

- Timeout gateway
- Teams mencoba ulang pesan (menyebabkan duplikasi)
- Balasan yang terlewat

OpenClaw menangani ini dengan mengembalikan respons cepat dan mengirim balasan secara proaktif, tetapi respons yang sangat lambat tetap dapat menimbulkan masalah.

### Pemformatan

Markdown Teams lebih terbatas daripada Slack atau Discord:

- Pemformatan dasar berfungsi: **tebal**, _miring_, `code`, tautan
- Markdown kompleks (tabel, daftar bertingkat) mungkin tidak dirender dengan benar
- Adaptive Cards didukung untuk polls dan pengiriman kartu arbitrer (lihat di bawah)

## Konfigurasi

Pengaturan utama (lihat `/gateway/configuration` untuk pola saluran bersama):

- `channels.msteams.enabled`: aktifkan/nonaktifkan saluran.
- `channels.msteams.appId`, `channels.msteams.appPassword`, `channels.msteams.tenantId`: kredensial bot.
- `channels.msteams.webhook.port` (default `3978`)
- `channels.msteams.webhook.path` (default `/api/messages`)
- `channels.msteams.dmPolicy`: `pairing | allowlist | open | disabled` (default: pairing)
- `channels.msteams.allowFrom`: allowlist DM (ID objek AAD direkomendasikan). Wizard menyelesaikan nama menjadi ID selama penyiapan saat akses Graph tersedia.
- `channels.msteams.dangerouslyAllowNameMatching`: toggle break-glass untuk mengaktifkan kembali pencocokan UPN/nama tampilan yang dapat berubah dan perutean langsung nama team/saluran.
- `channels.msteams.textChunkLimit`: ukuran chunk teks keluar.
- `channels.msteams.chunkMode`: `length` (default) atau `newline` untuk memisah pada baris kosong (batas paragraf) sebelum chunking berdasarkan panjang.
- `channels.msteams.mediaAllowHosts`: allowlist untuk host lampiran masuk (default ke domain Microsoft/Teams).
- `channels.msteams.mediaAuthAllowHosts`: allowlist untuk melampirkan header Authorization pada percobaan ulang media (default ke host Graph + Bot Framework).
- `channels.msteams.requireMention`: mewajibkan @mention di saluran/grup (default true).
- `channels.msteams.replyStyle`: `thread | top-level` (lihat [Gaya Balasan](#reply-style-threads-vs-posts)).
- `channels.msteams.teams.<teamId>.replyStyle`: override per-team.
- `channels.msteams.teams.<teamId>.requireMention`: override per-team.
- `channels.msteams.teams.<teamId>.tools`: override kebijakan tool default per-team (`allow`/`deny`/`alsoAllow`) yang digunakan saat override saluran tidak ada.
- `channels.msteams.teams.<teamId>.toolsBySender`: override kebijakan tool default per-team per-pengirim (`"*"` wildcard didukung).
- `channels.msteams.teams.<teamId>.channels.<conversationId>.replyStyle`: override per-saluran.
- `channels.msteams.teams.<teamId>.channels.<conversationId>.requireMention`: override per-saluran.
- `channels.msteams.teams.<teamId>.channels.<conversationId>.tools`: override kebijakan tool per-saluran (`allow`/`deny`/`alsoAllow`).
- `channels.msteams.teams.<teamId>.channels.<conversationId>.toolsBySender`: override kebijakan tool per-saluran per-pengirim (`"*"` wildcard didukung).
- Kunci `toolsBySender` harus menggunakan prefiks eksplisit:
  `id:`, `e164:`, `username:`, `name:` (kunci lama tanpa prefiks masih dipetakan ke `id:` saja).
- `channels.msteams.actions.memberInfo`: aktifkan atau nonaktifkan tindakan info anggota berbasis Graph (default: aktif saat kredensial Graph tersedia).
- `channels.msteams.authType`: jenis autentikasi — `"secret"` (default) atau `"federated"`.
- `channels.msteams.certificatePath`: path ke file sertifikat PEM (federated + autentikasi sertifikat).
- `channels.msteams.certificateThumbprint`: thumbprint sertifikat (opsional, tidak wajib untuk autentikasi).
- `channels.msteams.useManagedIdentity`: aktifkan autentikasi managed identity (mode federated).
- `channels.msteams.managedIdentityClientId`: client ID untuk managed identity user-assigned.
- `channels.msteams.sharePointSiteId`: ID situs SharePoint untuk unggahan file di obrolan grup/saluran (lihat [Mengirim file di obrolan grup](#sending-files-in-group-chats)).

## Perutean & Sesi

- Kunci sesi mengikuti format agen standar (lihat [/concepts/session](/id/concepts/session)):
  - Pesan langsung berbagi sesi utama (`agent:<agentId>:<mainKey>`).
  - Pesan saluran/grup menggunakan ID percakapan:
    - `agent:<agentId>:msteams:channel:<conversationId>`
    - `agent:<agentId>:msteams:group:<conversationId>`

## Gaya Balasan: Thread vs Postingan

Teams baru-baru ini memperkenalkan dua gaya UI saluran di atas model data dasar yang sama:

| Style                    | Description                                                  | `replyStyle` yang direkomendasikan |
| ------------------------ | ------------------------------------------------------------ | ---------------------------------- |
| **Posts** (klasik)       | Pesan muncul sebagai kartu dengan balasan berutas di bawahnya | `thread` (default)                 |
| **Threads** (mirip Slack) | Pesan mengalir secara linear, lebih mirip Slack            | `top-level`                        |

**Masalahnya:** API Teams tidak mengekspos gaya UI yang digunakan saluran. Jika Anda menggunakan `replyStyle` yang salah:

- `thread` di saluran bergaya Threads → balasan tampak bertingkat dengan canggung
- `top-level` di saluran bergaya Posts → balasan muncul sebagai postingan tingkat atas terpisah, bukan di dalam thread

**Solusi:** Konfigurasikan `replyStyle` per-saluran berdasarkan cara saluran disiapkan:

```json5
{
  channels: {
    msteams: {
      replyStyle: "thread",
      teams: {
        "19:abc...@thread.tacv2": {
          channels: {
            "19:xyz...@thread.tacv2": {
              replyStyle: "top-level",
            },
          },
        },
      },
    },
  },
}
```

## Lampiran & Gambar

**Keterbatasan saat ini:**

- **DM:** Gambar dan lampiran file berfungsi melalui API file bot Teams.
- **Saluran/grup:** Lampiran berada di penyimpanan M365 (SharePoint/OneDrive). Payload webhook hanya menyertakan stub HTML, bukan byte file sebenarnya. **Izin Graph API diperlukan** untuk mengunduh lampiran saluran.
- Untuk pengiriman eksplisit yang mengutamakan file, gunakan `action=upload-file` dengan `media` / `filePath` / `path`; `message` opsional menjadi teks/komentar pendamping, dan `filename` menggantikan nama yang diunggah.

Tanpa izin Graph, pesan saluran dengan gambar akan diterima sebagai teks saja (konten gambar tidak dapat diakses oleh bot).
Secara default, OpenClaw hanya mengunduh media dari hostname Microsoft/Teams. Override dengan `channels.msteams.mediaAllowHosts` (gunakan `["*"]` untuk mengizinkan host apa pun).
Header Authorization hanya dilampirkan untuk host di `channels.msteams.mediaAuthAllowHosts` (default ke host Graph + Bot Framework). Pertahankan daftar ini tetap ketat (hindari suffix multi-tenant).

## Mengirim file di obrolan grup

Bot dapat mengirim file di DM menggunakan alur FileConsentCard (bawaan). Namun, **mengirim file di obrolan grup/saluran** memerlukan penyiapan tambahan:

| Context                  | How files are sent                         | Setup needed                                    |
| ------------------------ | ------------------------------------------ | ----------------------------------------------- |
| **DM**                   | FileConsentCard → pengguna menerima → bot mengunggah | Langsung berfungsi                    |
| **Obrolan grup/saluran** | Unggah ke SharePoint → bagikan tautan      | Memerlukan `sharePointSiteId` + izin Graph      |
| **Gambar (konteks apa pun)** | Inline dengan enkode Base64            | Langsung berfungsi                              |

### Mengapa obrolan grup memerlukan SharePoint

Bot tidak memiliki drive OneDrive personal (endpoint Graph API `/me/drive` tidak berfungsi untuk identitas aplikasi). Untuk mengirim file di obrolan grup/saluran, bot mengunggah ke **situs SharePoint** dan membuat tautan berbagi.

### Penyiapan

1. **Tambahkan izin Graph API** di Entra ID (Azure AD) → App Registration:
   - `Sites.ReadWrite.All` (Application) - unggah file ke SharePoint
   - `Chat.Read.All` (Application) - opsional, mengaktifkan tautan berbagi per-pengguna

2. **Berikan admin consent** untuk tenant.

3. **Dapatkan ID situs SharePoint Anda:**

   ```bash
   # Melalui Graph Explorer atau curl dengan token yang valid:
   curl -H "Authorization: Bearer $TOKEN" \
     "https://graph.microsoft.com/v1.0/sites/{hostname}:/{site-path}"

   # Contoh: untuk situs di "contoso.sharepoint.com/sites/BotFiles"
   curl -H "Authorization: Bearer $TOKEN" \
     "https://graph.microsoft.com/v1.0/sites/contoso.sharepoint.com:/sites/BotFiles"

   # Respons mencakup: "id": "contoso.sharepoint.com,guid1,guid2"
   ```

4. **Konfigurasikan OpenClaw:**

   ```json5
   {
     channels: {
       msteams: {
         // ... konfigurasi lain ...
         sharePointSiteId: "contoso.sharepoint.com,guid1,guid2",
       },
     },
   }
   ```

### Perilaku berbagi

| Permission                              | Sharing behavior                                             |
| --------------------------------------- | ------------------------------------------------------------ |
| `Sites.ReadWrite.All` saja              | Tautan berbagi ke seluruh organisasi (siapa pun di organisasi dapat mengakses) |
| `Sites.ReadWrite.All` + `Chat.Read.All` | Tautan berbagi per-pengguna (hanya anggota chat yang dapat mengakses)          |

Berbagi per-pengguna lebih aman karena hanya peserta chat yang dapat mengakses file. Jika izin `Chat.Read.All` tidak ada, bot akan fallback ke berbagi ke seluruh organisasi.

### Perilaku fallback

| Scenario                                          | Result                                               |
| ------------------------------------------------- | ---------------------------------------------------- |
| Obrolan grup + file + `sharePointSiteId` dikonfigurasi | Unggah ke SharePoint, kirim tautan berbagi       |
| Obrolan grup + file + tidak ada `sharePointSiteId` | Coba unggah ke OneDrive (mungkin gagal), kirim teks saja |
| Chat personal + file                              | Alur FileConsentCard (berfungsi tanpa SharePoint)    |
| Konteks apa pun + gambar                          | Inline dengan enkode Base64 (berfungsi tanpa SharePoint) |

### Lokasi penyimpanan file

File yang diunggah disimpan di folder `/OpenClawShared/` dalam pustaka dokumen default situs SharePoint yang dikonfigurasi.

## Polls (Adaptive Cards)

OpenClaw mengirim polls Teams sebagai Adaptive Cards (tidak ada API poll Teams native).

- CLI: `openclaw message poll --channel msteams --target conversation:<id> ...`
- Vote dicatat oleh gateway di `~/.openclaw/msteams-polls.json`.
- Gateway harus tetap online untuk mencatat vote.
- Poll belum otomatis memposting ringkasan hasil (periksa file store jika diperlukan).

## Adaptive Cards (arbitrer)

Kirim JSON Adaptive Card apa pun ke pengguna atau percakapan Teams menggunakan tool `message` atau CLI.

Parameter `card` menerima objek JSON Adaptive Card. Saat `card` diberikan, teks pesan bersifat opsional.

**Tool agen:**

```json5
{
  action: "send",
  channel: "msteams",
  target: "user:<id>",
  card: {
    type: "AdaptiveCard",
    version: "1.5",
    body: [{ type: "TextBlock", text: "Hello!" }],
  },
}
```

**CLI:**

```bash
openclaw message send --channel msteams \
  --target "conversation:19:abc...@thread.tacv2" \
  --card '{"type":"AdaptiveCard","version":"1.5","body":[{"type":"TextBlock","text":"Hello!"}]}'
```

Lihat [dokumentasi Adaptive Cards](https://adaptivecards.io/) untuk skema kartu dan contoh. Untuk detail format target, lihat [Format target](#target-formats) di bawah.

## Format target

Target MSTeams menggunakan prefiks untuk membedakan pengguna dan percakapan:

| Target type         | Format                           | Example                                             |
| ------------------- | -------------------------------- | --------------------------------------------------- |
| Pengguna (berdasarkan ID) | `user:<aad-object-id>`     | `user:40a1a0ed-4ff2-4164-a219-55518990c197`         |
| Pengguna (berdasarkan nama) | `user:<display-name>`   | `user:John Smith` (memerlukan Graph API)            |
| Grup/saluran        | `conversation:<conversation-id>` | `conversation:19:abc123...@thread.tacv2`            |
| Grup/saluran (raw)  | `<conversation-id>`              | `19:abc123...@thread.tacv2` (jika mengandung `@thread`) |

**Contoh CLI:**

```bash
# Kirim ke pengguna berdasarkan ID
openclaw message send --channel msteams --target "user:40a1a0ed-..." --message "Hello"

# Kirim ke pengguna berdasarkan nama tampilan (memicu lookup Graph API)
openclaw message send --channel msteams --target "user:John Smith" --message "Hello"

# Kirim ke obrolan grup atau saluran
openclaw message send --channel msteams --target "conversation:19:abc...@thread.tacv2" --message "Hello"

# Kirim Adaptive Card ke percakapan
openclaw message send --channel msteams --target "conversation:19:abc...@thread.tacv2" \
  --card '{"type":"AdaptiveCard","version":"1.5","body":[{"type":"TextBlock","text":"Hello"}]}'
```

**Contoh tool agen:**

```json5
{
  action: "send",
  channel: "msteams",
  target: "user:John Smith",
  message: "Hello!",
}
```

```json5
{
  action: "send",
  channel: "msteams",
  target: "conversation:19:abc...@thread.tacv2",
  card: {
    type: "AdaptiveCard",
    version: "1.5",
    body: [{ type: "TextBlock", text: "Hello" }],
  },
}
```

Catatan: Tanpa prefiks `user:`, nama secara default akan menggunakan resolusi grup/team. Selalu gunakan `user:` saat menargetkan orang berdasarkan nama tampilan.

## Pesan proaktif

- Pesan proaktif hanya dimungkinkan **setelah** pengguna berinteraksi, karena kami menyimpan referensi percakapan pada saat itu.
- Lihat `/gateway/configuration` untuk gerbang `dmPolicy` dan allowlist.

## ID Team dan Saluran (Kesalahan Umum)

Parameter kueri `groupId` dalam URL Teams **BUKAN** ID team yang digunakan untuk konfigurasi. Ekstrak ID dari path URL sebagai gantinya:

**URL Team:**

```
https://teams.microsoft.com/l/team/19%3ABk4j...%40thread.tacv2/conversations?groupId=...
                                    └────────────────────────────┘
                                    ID Team (lakukan URL-decode untuk ini)
```

**URL Saluran:**

```
https://teams.microsoft.com/l/channel/19%3A15bc...%40thread.tacv2/ChannelName?groupId=...
                                      └─────────────────────────┘
                                      ID Saluran (lakukan URL-decode untuk ini)
```

**Untuk konfigurasi:**

- ID Team = segmen path setelah `/team/` (hasil URL-decode, misalnya `19:Bk4j...@thread.tacv2`)
- ID Saluran = segmen path setelah `/channel/` (hasil URL-decode)
- **Abaikan** parameter kueri `groupId`

## Saluran Privat

Bot memiliki dukungan terbatas di saluran privat:

| Feature                      | Standard Channels | Private Channels      |
| ---------------------------- | ----------------- | --------------------- |
| Instalasi bot                | Ya                | Terbatas              |
| Pesan real-time (webhook)    | Ya                | Mungkin tidak berfungsi |
| Izin RSC                     | Ya                | Mungkin berperilaku berbeda |
| @mentions                    | Ya                | Jika bot dapat diakses |
| Riwayat Graph API            | Ya                | Ya (dengan izin)      |

**Solusi jika saluran privat tidak berfungsi:**

1. Gunakan saluran standar untuk interaksi bot
2. Gunakan DM - pengguna selalu dapat mengirim pesan langsung ke bot
3. Gunakan Graph API untuk akses historis (memerlukan `ChannelMessage.Read.All`)

## Pemecahan Masalah

### Masalah umum

- **Gambar tidak muncul di saluran:** izin Graph atau admin consent belum ada. Instal ulang aplikasi Teams dan keluar/buka kembali Teams sepenuhnya.
- **Tidak ada respons di saluran:** mention diwajibkan secara default; setel `channels.msteams.requireMention=false` atau konfigurasikan per team/saluran.
- **Versi tidak cocok (Teams masih menampilkan manifest lama):** hapus + tambahkan ulang aplikasi dan keluar dari Teams sepenuhnya untuk menyegarkan.
- **401 Unauthorized dari webhook:** Ini wajar saat menguji secara manual tanpa Azure JWT - artinya endpoint dapat dijangkau tetapi autentikasi gagal. Gunakan Azure Web Chat untuk pengujian yang benar.

### Kesalahan unggah manifest

- **"Icon file cannot be empty":** Manifest mereferensikan file ikon yang berukuran 0 byte. Buat ikon PNG yang valid (32x32 untuk `outline.png`, 192x192 untuk `color.png`).
- **"webApplicationInfo.Id already in use":** Aplikasi masih terinstal di team/chat lain. Temukan dan copot pemasangannya terlebih dahulu, atau tunggu 5-10 menit untuk propagasi.
- **"Something went wrong" saat unggah:** Unggah melalui [https://admin.teams.microsoft.com](https://admin.teams.microsoft.com) sebagai gantinya, buka browser DevTools (F12) → tab Network, dan periksa body respons untuk melihat kesalahan sebenarnya.
- **Sideload gagal:** Coba "Upload an app to your org's app catalog" alih-alih "Upload a custom app" - ini sering melewati pembatasan sideload.

### Izin RSC tidak berfungsi

1. Verifikasi `webApplicationInfo.id` cocok persis dengan App ID bot Anda
2. Unggah ulang aplikasi dan instal ulang di team/chat
3. Periksa apakah admin organisasi Anda memblokir izin RSC
4. Konfirmasikan Anda menggunakan cakupan yang benar: `ChannelMessage.Read.Group` untuk teams, `ChatMessage.Read.Chat` untuk obrolan grup

## Referensi

- [Create Azure Bot](https://learn.microsoft.com/en-us/azure/bot-service/bot-service-quickstart-registration) - panduan penyiapan Azure Bot
- [Teams Developer Portal](https://dev.teams.microsoft.com/apps) - membuat/mengelola aplikasi Teams
- [Teams app manifest schema](https://learn.microsoft.com/en-us/microsoftteams/platform/resources/schema/manifest-schema)
- [Receive channel messages with RSC](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/conversations/channel-messages-with-rsc)
- [RSC permissions reference](https://learn.microsoft.com/en-us/microsoftteams/platform/graph-api/rsc/resource-specific-consent)
- [Teams bot file handling](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/bots-filesv4) (saluran/grup memerlukan Graph)
- [Proactive messaging](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/conversations/send-proactive-messages)

## Terkait

- [Ikhtisar Saluran](/id/channels) — semua saluran yang didukung
- [Pairing](/id/channels/pairing) — autentikasi DM dan alur pairing
- [Grup](/id/channels/groups) — perilaku obrolan grup dan gerbang mention
- [Perutean Saluran](/id/channels/channel-routing) — perutean sesi untuk pesan
- [Keamanan](/id/gateway/security) — model akses dan hardening
