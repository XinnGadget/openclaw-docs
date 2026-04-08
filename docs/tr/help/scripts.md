---
read_when:
    - Depodaki betikleri çalıştırırken
    - '`./scripts` altına betik eklerken veya değiştirirken'
summary: 'Depo betikleri: amaç, kapsam ve güvenlik notları'
title: Betikler
x-i18n:
    generated_at: "2026-04-08T02:15:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3ecf1e9327929948fb75f80e306963af49b353c0aa8d3b6fa532ca964ff8b975
    source_path: help/scripts.md
    workflow: 15
---

# Betikler

`scripts/` dizini, yerel iş akışları ve operasyon görevleri için yardımcı betikler içerir.
Bir görev açıkça bir betikle bağlantılıysa bunları kullanın; aksi durumda CLI tercih edin.

## Kurallar

- Betikler, dokümanlarda veya sürüm kontrol listelerinde referans verilmediği sürece **isteğe bağlıdır**.
- Varsa CLI yüzeylerini tercih edin (örnek: kimlik doğrulama izleme `openclaw models status --check` kullanır).
- Betiklerin ana makineye özgü olduğunu varsayın; yeni bir makinede çalıştırmadan önce okuyun.

## Kimlik doğrulama izleme betikleri

Kimlik doğrulama izleme [Kimlik Doğrulama](/tr/gateway/authentication) bölümünde ele alınır. `scripts/` altındaki betikler, systemd/Termux telefon iş akışları için isteğe bağlı eklerdir.

## GitHub okuma yardımcısı

Normal `gh` kullanımını yazma işlemleri için kişisel oturum açmanızda bırakırken, depo kapsamlı okuma çağrıları için `gh` aracının bir GitHub App kurulum token'ı kullanmasını istediğinizde `scripts/gh-read` kullanın.

Gerekli ortam değişkenleri:

- `OPENCLAW_GH_READ_APP_ID`
- `OPENCLAW_GH_READ_PRIVATE_KEY_FILE`

İsteğe bağlı ortam değişkenleri:

- Depo tabanlı kurulum aramasını atlamak istediğinizde `OPENCLAW_GH_READ_INSTALLATION_ID`
- İstenecek okuma izinleri alt kümesi için virgülle ayrılmış geçersiz kılma olarak `OPENCLAW_GH_READ_PERMISSIONS`

Depo çözümleme sırası:

- `gh ... -R owner/repo`
- `GH_REPO`
- `git remote origin`

Örnekler:

- `scripts/gh-read pr view 123`
- `scripts/gh-read run list -R openclaw/openclaw`
- `scripts/gh-read api repos/openclaw/openclaw/pulls/123`

## Betik eklerken

- Betikleri odaklı ve belgelenmiş tutun.
- İlgili dokümana kısa bir giriş ekleyin (veya eksikse oluşturun).
