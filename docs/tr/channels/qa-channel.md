---
read_when:
    - Sentetik QA taşımasını yerel veya CI test çalışmasına bağlıyorsunuz
    - Paketlenmiş qa-channel yapılandırma yüzeyine ihtiyacınız var
    - Uçtan uca QA otomasyonu üzerinde yineleme yapıyorsunuz
summary: Deterministik OpenClaw QA senaryoları için sentetik Slack sınıfı kanal eklentisi
title: QA Kanalı
x-i18n:
    generated_at: "2026-04-06T03:05:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3b88cd73df2f61b34ad1eb83c3450f8fe15a51ac69fbb5a9eca0097564d67a06
    source_path: channels/qa-channel.md
    workflow: 15
---

# QA Kanalı

`qa-channel`, otomatik OpenClaw QA için paketlenmiş sentetik bir mesaj taşımasıdır.

Bu, üretim için kullanılan bir kanal değildir. Gerçek taşımaların kullandığı aynı kanal eklentisi
sınırını kullanırken durumu deterministik ve tamamen
incelenebilir tutmak için vardır.

## Bugün ne yapıyor

- Slack sınıfı hedef dil bilgisi:
  - `dm:<user>`
  - `channel:<room>`
  - `thread:<room>/<thread>`
- Şunlar için HTTP destekli sentetik veri yolu:
  - gelen mesaj ekleme
  - giden transkript yakalama
  - iş parçacığı oluşturma
  - tepkiler
  - düzenlemeler
  - silmeler
  - arama ve okuma eylemleri
- Markdown raporu yazan paketlenmiş ana makine tarafı öz denetim çalıştırıcısı

## Yapılandırma

```json
{
  "channels": {
    "qa-channel": {
      "baseUrl": "http://127.0.0.1:43123",
      "botUserId": "openclaw",
      "botDisplayName": "OpenClaw QA",
      "allowFrom": ["*"],
      "pollTimeoutMs": 1000
    }
  }
}
```

Desteklenen hesap anahtarları:

- `baseUrl`
- `botUserId`
- `botDisplayName`
- `pollTimeoutMs`
- `allowFrom`
- `defaultTo`
- `actions.messages`
- `actions.reactions`
- `actions.search`
- `actions.threads`

## Çalıştırıcı

Geçerli dikey dilim:

```bash
pnpm qa:e2e
```

Bu artık paketlenmiş `qa-lab` uzantısı üzerinden yönlendiriliyor. Depo içindeki
QA veri yolunu başlatır, paketlenmiş `qa-channel` çalışma zamanı dilimini önyükler, deterministik bir
öz denetim çalıştırır ve `.artifacts/qa-e2e/` altında bir Markdown raporu yazar.

Özel hata ayıklayıcı kullanıcı arayüzü:

```bash
pnpm qa:lab:build
pnpm openclaw qa ui
```

Tam depo destekli QA paketi:

```bash
pnpm openclaw qa suite
```

Bu, dağıtılan Control UI paketinden ayrı olarak, yerel bir URL'de
özel QA hata ayıklayıcısını başlatır.

## Kapsam

Geçerli kapsam kasıtlı olarak dardır:

- veri yolu + eklenti taşıması
- iş parçacıklı yönlendirme dil bilgisi
- kanalın sahip olduğu mesaj eylemleri
- Markdown raporlama

Sonraki çalışmalar şunları ekleyecek:

- Docker ile kapsüllenmiş OpenClaw orkestrasyonu
- sağlayıcı/model matris yürütmesi
- daha zengin senaryo keşfi
- daha sonra OpenClaw yerel orkestrasyonu
