---
read_when:
    - qa-lab veya qa-channel genişletiyorsunuz
    - repo destekli QA senaryoları ekliyorsunuz
    - Gateway dashboard etrafında daha yüksek gerçekçiliğe sahip QA otomasyonu oluşturuyorsunuz
summary: qa-lab, qa-channel, tohumlanmış senaryolar ve protokol raporları için özel QA otomasyon yapısı
title: QA E2E Otomasyonu
x-i18n:
    generated_at: "2026-04-07T08:44:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: 113e89d8d3ee8ef3058d95b9aea9a1c2335b07794446be2d231c0faeb044b23b
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# QA E2E Otomasyonu

Özel QA yığını, OpenClaw'ı tek birim testinin sağlayabileceğinden daha gerçekçi,
kanal biçimli bir şekilde çalıştırmayı amaçlar.

Mevcut parçalar:

- `extensions/qa-channel`: DM, kanal, ileti dizisi,
  tepki, düzenleme ve silme yüzeylerine sahip sentetik mesaj kanalı.
- `extensions/qa-lab`: transkripti gözlemlemek,
  gelen mesajları enjekte etmek ve bir Markdown raporu dışa aktarmak için hata ayıklayıcı arayüzü ve QA veri yolu.
- `qa/`: başlangıç görevi ve temel QA
  senaryoları için repo destekli tohum varlıkları.

Mevcut QA operatör akışı iki panelli bir QA sitesidir:

- Sol: aracı ile Gateway dashboard (Kontrol Arayüzü).
- Sağ: Slack benzeri transkripti ve senaryo planını gösteren QA Lab.

Bunu şu komutla çalıştırın:

```bash
pnpm qa:lab:up
```

Bu, QA sitesini derler, Docker destekli gateway hattını başlatır ve
bir operatörün veya otomasyon döngüsünün aracıya bir QA
görevi verebildiği, gerçek kanal davranışını gözlemleyebildiği ve neyin işe yaradığını, neyin başarısız olduğunu veya
neyin engelli kaldığını kaydedebildiği QA Lab sayfasını açığa çıkarır.

## Repo destekli tohumlar

Tohum varlıkları `qa/` içinde bulunur:

- `qa/QA_KICKOFF_TASK.md`
- `qa/seed-scenarios.json`

Bunlar bilerek git içinde tutulur; böylece QA planı hem insanlar hem de
aracı tarafından görülebilir. Temel listenin kapsayacak kadar geniş kalması gerekir:

- DM ve kanal sohbeti
- ileti dizisi davranışı
- mesaj eylemi yaşam döngüsü
- cron geri çağrımları
- bellekten geri çağırma
- model değiştirme
- alt aracı devri
- repo okuma ve belge okuma
- Lobster Invaders gibi küçük bir derleme görevi

## Raporlama

`qa-lab`, gözlemlenen veri yolu zaman çizelgesinden bir Markdown protokol raporu dışa aktarır.
Rapor şu sorulara yanıt vermelidir:

- Neler işe yaradı
- Neler başarısız oldu
- Neler engelli kaldı
- Hangi takip senaryolarını eklemeye değer

## İlgili belgeler

- [Testing](/tr/help/testing)
- [QA Channel](/tr/channels/qa-channel)
- [Dashboard](/web/dashboard)
