---
read_when:
    - Sentetik QA taşımasını yerel veya CI test çalışmasına bağlıyorsunuz
    - Paketle gelen qa-channel yapılandırma yüzeyine ihtiyacınız var
    - Uçtan uca QA otomasyonu üzerinde yineleme yapıyorsunuz
summary: Belirlenimci OpenClaw QA senaryoları için sentetik, Slack sınıfı kanal eklentisi
title: QA Kanalı
x-i18n:
    generated_at: "2026-04-07T08:43:28Z"
    model: gpt-5.4
    provider: openai
    source_hash: 65c2c908d3ec27c827087616c4ea278f10686810091058321ff26f68296a1782
    source_path: channels/qa-channel.md
    workflow: 15
---

# QA Kanalı

`qa-channel`, otomatik OpenClaw QA için paketle gelen sentetik bir mesaj taşımasıdır.

Bu bir üretim kanalı değildir. Gerçek taşımalarda kullanılan aynı kanal eklentisi
sınırını, durumu belirlenimci ve tamamen
incelenebilir tutarken test etmek için vardır.

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
- Markdown raporu yazan, paketle gelen ana makine tarafı self-check çalıştırıcısı

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

Bu artık paketle gelen `qa-lab` uzantısı üzerinden yönlendiriliyor. Depo içindeki
QA veri yolunu başlatır, paketle gelen `qa-channel` çalışma zamanı dilimini açar, belirlenimci
bir self-check çalıştırır ve `.artifacts/qa-e2e/` altında bir Markdown raporu yazar.

Özel hata ayıklayıcı arayüzü:

```bash
pnpm qa:lab:up
```

Bu tek komut QA sitesini derler, Docker destekli gateway + QA Lab
yığınını başlatır ve QA Lab URL'sini yazdırır. Bu siteden senaryolar seçebilir,
model hattını seçebilir, tek tek çalıştırmaları başlatabilir ve sonuçları canlı izleyebilirsiniz.

Tam depo destekli QA paketi:

```bash
pnpm openclaw qa suite
```

Bu, paketlenmiş Control UI paketinden ayrı olarak, özel QA hata ayıklayıcısını
yerel bir URL'de başlatır.

## Kapsam

Geçerli kapsam kasıtlı olarak dardır:

- veri yolu + eklenti taşıması
- iş parçacıklı yönlendirme dil bilgisi
- kanala ait mesaj eylemleri
- Markdown raporlama
- çalıştırma denetimlerine sahip Docker destekli QA sitesi

Sonraki çalışmalar şunları ekleyecek:

- sağlayıcı/model matris yürütmesi
- daha zengin senaryo keşfi
- daha sonra OpenClaw yerel düzenlemesi
