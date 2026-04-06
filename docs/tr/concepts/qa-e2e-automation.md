---
read_when:
    - qa-lab veya qa-channel genişletilirken
    - repo destekli QA senaryoları eklerken
    - Gateway panosu etrafında daha gerçekçi QA otomasyonu oluştururken
summary: qa-lab, qa-channel, tohumlanmış senaryolar ve protokol raporları için özel QA otomasyon yapısı
title: QA E2E Otomasyonu
x-i18n:
    generated_at: "2026-04-06T03:06:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: df35f353d5ab0e0432e6a828c82772f9a88edb41c20ec5037315b7ba310b28e6
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# QA E2E Otomasyonu

Özel QA yığını, OpenClaw'u tek birim testinin yapabileceğinden daha gerçekçi,
kanal biçimli bir şekilde çalıştırmak için tasarlanmıştır.

Mevcut parçalar:

- `extensions/qa-channel`: DM, kanal, konu,
  tepki, düzenleme ve silme yüzeylerine sahip sentetik mesaj kanalı.
- `extensions/qa-lab`: transkripti gözlemlemek,
  gelen mesajları enjekte etmek ve bir Markdown raporu dışa aktarmak için hata ayıklayıcı UI ve QA veri yolu.
- `qa/`: başlangıç görevi ve temel QA
  senaryoları için repo destekli tohum varlıkları.

Uzun vadeli hedef, iki panelli bir QA sitesi oluşturmaktır:

- Sol: aracıyla birlikte Gateway panosu (Control UI).
- Sağ: Slack benzeri transkripti ve senaryo planını gösteren QA Lab.

Bu, bir operatörün veya otomasyon döngüsünün aracıya bir QA görevi vermesine, gerçek kanal davranışını gözlemlemesine ve neyin işe yaradığını, neyin başarısız olduğunu veya neyin engelli kaldığını kaydetmesine olanak tanır.

## Repo destekli tohumlar

Tohum varlıkları `qa/` içinde bulunur:

- `qa/QA_KICKOFF_TASK.md`
- `qa/seed-scenarios.json`

Bunlar, QA planının hem insanlar hem de
aracı tarafından görünür olması için kasıtlı olarak git içinde tutulur. Temel listenin kapsayacak kadar geniş kalması gerekir:

- DM ve kanal sohbeti
- konu davranışı
- mesaj eylemi yaşam döngüsü
- cron geri çağrıları
- bellekten hatırlama
- model değiştirme
- alt aracı devri
- repo okuma ve belge okuma
- Lobster Invaders gibi küçük bir build görevi

## Raporlama

`qa-lab`, gözlemlenen veri yolu zaman çizelgesinden bir Markdown protokol raporu dışa aktarır.
Rapor şu sorulara yanıt vermelidir:

- Ne işe yaradı
- Ne başarısız oldu
- Ne engelli kaldı
- Hangi takip senaryolarının eklenmesi değerli olur

## İlgili belgeler

- [Testing](/tr/help/testing)
- [QA Channel](/channels/qa-channel)
- [Dashboard](/web/dashboard)
