---
read_when:
    - qa-lab veya qa-channel genişletilirken
    - repo destekli QA senaryoları eklerken
    - Gateway kontrol paneli etrafında daha yüksek gerçekçiliğe sahip QA otomasyonu oluştururken
summary: qa-lab, qa-channel, tohumlanmış senaryolar ve protokol raporları için özel QA otomasyon yapısı
title: QA E2E Otomasyonu
x-i18n:
    generated_at: "2026-04-08T02:13:58Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3b4aa5acc8e77303f4045d4f04372494cae21b89d2fdaba856dbb4855ced9d27
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# QA E2E Otomasyonu

Özel QA yığını, OpenClaw'ı tek birim testinin yapabileceğinden daha gerçekçi,
kanal biçimli bir şekilde çalıştırmak için tasarlanmıştır.

Mevcut parçalar:

- `extensions/qa-channel`: DM, kanal, konu, tepki,
  düzenleme ve silme yüzeylerine sahip sentetik mesaj kanalı.
- `extensions/qa-lab`: transkripti gözlemlemek,
  gelen mesajları enjekte etmek ve bir Markdown raporu dışa aktarmak için hata ayıklayıcı UI'ı ve QA veri yolu.
- `qa/`: başlangıç görevi ve temel QA
  senaryoları için repo destekli tohum varlıkları.

Geçerli QA operatörü akışı iki panelli bir QA sitesidir:

- Sol: Aracının bulunduğu Gateway kontrol paneli (Control UI).
- Sağ: Slack benzeri transkript ve senaryo planını gösteren QA Lab.

Bunu şu komutla çalıştırın:

```bash
pnpm qa:lab:up
```

Bu, QA sitesini derler, Docker destekli gateway hattını başlatır ve bir operatörün veya otomasyon döngüsünün aracıya bir QA
görevi verebildiği, gerçek kanal davranışını gözlemleyebildiği ve neyin işe yaradığını, neyin başarısız olduğunu veya
neyin engelli kaldığını kaydedebildiği QA Lab sayfasını açığa çıkarır.

Docker imajını her seferinde yeniden derlemeden daha hızlı QA Lab UI yinelemesi için,
yığını bind-mount edilmiş bir QA Lab paketiyle başlatın:

```bash
pnpm openclaw qa docker-build-image
pnpm qa:lab:build
pnpm qa:lab:up:fast
pnpm qa:lab:watch
```

`qa:lab:up:fast`, Docker hizmetlerini önceden derlenmiş bir imajda tutar ve
`extensions/qa-lab/web/dist` dizinini `qa-lab` kapsayıcısına bind-mount eder. `qa:lab:watch`
bu paketi değişikliklerde yeniden derler ve QA Lab varlık karması değiştiğinde tarayıcı otomatik olarak yeniden yüklenir.

## Repo destekli tohumlar

Tohum varlıkları `qa/` içinde bulunur:

- `qa/scenarios.md`

Bunlar, QA planı hem insanlar hem de
aracı için görünür olsun diye kasıtlı olarak git içinde tutulur. Temel liste, şunları kapsayacak kadar geniş kalmalıdır:

- DM ve kanal sohbeti
- konu davranışı
- mesaj eylemi yaşam döngüsü
- cron geri çağrıları
- bellekten geri çağırma
- model değiştirme
- alt aracı devri
- repo okuma ve doküman okuma
- Lobster Invaders gibi küçük bir derleme görevi

## Raporlama

`qa-lab`, gözlemlenen veri yolu zaman çizelgesinden bir Markdown protokol raporu dışa aktarır.
Rapor şu sorulara yanıt vermelidir:

- Ne işe yaradı
- Ne başarısız oldu
- Ne engelli kaldı
- Hangi takip senaryolarını eklemeye değer

## İlgili dokümanlar

- [Testler](/tr/help/testing)
- [QA Kanalı](/tr/channels/qa-channel)
- [Kontrol Paneli](/web/dashboard)
