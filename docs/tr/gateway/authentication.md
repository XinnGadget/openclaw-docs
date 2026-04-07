---
read_when:
    - Model kimlik doğrulamasını veya OAuth süresinin dolmasını hata ayıklarken
    - Kimlik doğrulamayı veya kimlik bilgisi depolamayı belgelendirirken
summary: 'Model kimlik doğrulaması: OAuth, API anahtarları, Claude CLI yeniden kullanımı ve Anthropic setup-token'
title: Kimlik Doğrulama
x-i18n:
    generated_at: "2026-04-07T08:44:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9db0ad9eccd7e3e3ca328adaad260bc4288a8ccdbe2dc0c24d9fd049b7ab9231
    source_path: gateway/authentication.md
    workflow: 15
---

# Kimlik Doğrulama (Model Sağlayıcıları)

<Note>
Bu sayfa **model sağlayıcısı** kimlik doğrulamasını kapsar (API anahtarları, OAuth, Claude CLI yeniden kullanımı ve Anthropic setup-token). **Gateway bağlantısı** kimlik doğrulaması için (token, parola, trusted-proxy), bkz. [Configuration](/tr/gateway/configuration) ve [Trusted Proxy Auth](/tr/gateway/trusted-proxy-auth).
</Note>

OpenClaw, model sağlayıcıları için OAuth ve API anahtarlarını destekler. Sürekli
çalışan gateway host'ları için API anahtarları genellikle en öngörülebilir
seçenektir. Abonelik/OAuth akışları da sağlayıcı hesap modelinizle eşleştiğinde
desteklenir.

Tam OAuth akışı ve depolama düzeni için bkz. [/concepts/oauth](/tr/concepts/oauth).
SecretRef tabanlı kimlik doğrulama için (`env`/`file`/`exec` sağlayıcıları), bkz. [Secrets Management](/tr/gateway/secrets).
`models status --probe` tarafından kullanılan kimlik bilgisi uygunluğu/neden-kodu kuralları için
bkz. [Auth Credential Semantics](/tr/auth-credential-semantics).

## Önerilen kurulum (API anahtarı, herhangi bir sağlayıcı)

Uzun ömürlü bir gateway çalıştırıyorsanız, seçtiğiniz sağlayıcı için bir API
anahtarıyla başlayın.
Özellikle Anthropic için, API anahtarı kimlik doğrulaması hâlâ en öngörülebilir
sunucu kurulumudur, ancak OpenClaw yerel bir Claude CLI oturumunu yeniden
kullanmayı da destekler.

1. Sağlayıcı konsolunuzda bir API anahtarı oluşturun.
2. Bunu **gateway host** üzerine koyun (`openclaw gateway` çalıştıran makine).

```bash
export <PROVIDER>_API_KEY="..."
openclaw models status
```

3. Gateway systemd/launchd altında çalışıyorsa, anahtarı daemon'ın okuyabilmesi için
   `~/.openclaw/.env` içine koymayı tercih edin:

```bash
cat >> ~/.openclaw/.env <<'EOF'
<PROVIDER>_API_KEY=...
EOF
```

Ardından daemon'ı yeniden başlatın (veya Gateway sürecinizi yeniden başlatın) ve tekrar kontrol edin:

```bash
openclaw models status
openclaw doctor
```

Ortam değişkenlerini kendiniz yönetmek istemiyorsanız, onboarding API
anahtarlarını daemon kullanımı için saklayabilir: `openclaw onboard`.

Ortam devralma ayrıntıları için bkz. [Help](/tr/help) (`env.shellEnv`,
`~/.openclaw/.env`, systemd/launchd).

## Anthropic: Claude CLI ve token uyumluluğu

Anthropic setup-token kimlik doğrulaması, OpenClaw'da desteklenen bir token
yolu olarak hâlâ kullanılabilir. Anthropic çalışanları daha sonra bize
OpenClaw tarzı Claude CLI kullanımına yeniden izin verildiğini söyledi; bu nedenle
Anthropic yeni bir politika yayımlamadıkça OpenClaw bu entegrasyon için Claude CLI
yeniden kullanımını ve `claude -p` kullanımını onaylanmış kabul eder. Host üzerinde
Claude CLI yeniden kullanımı mevcutsa, artık tercih edilen yol budur.

Uzun ömürlü gateway host'ları için Anthropic API anahtarı hâlâ en öngörülebilir
kurulumdur. Aynı host üzerindeki mevcut bir Claude oturumunu yeniden kullanmak
istiyorsanız, onboarding/configure içindeki Anthropic Claude CLI yolunu kullanın.

Elle token girişi (herhangi bir sağlayıcı; `auth-profiles.json` yazar + config'i günceller):

```bash
openclaw models auth paste-token --provider openrouter
```

Kimlik doğrulama profili referansları, statik kimlik bilgileri için de desteklenir:

- `api_key` kimlik bilgileri `keyRef: { source, provider, id }` kullanabilir
- `token` kimlik bilgileri `tokenRef: { source, provider, id }` kullanabilir
- OAuth modundaki profiller SecretRef kimlik bilgilerini desteklemez; `auth.profiles.<id>.mode` `"oauth"` olarak ayarlanırsa, o profil için SecretRef destekli `keyRef`/`tokenRef` girişi reddedilir.

Otomasyon dostu kontrol (süresi dolmuş/eksikse çıkış `1`, süresi dolmak üzereyse `2`):

```bash
openclaw models status --check
```

Canlı kimlik doğrulama probları:

```bash
openclaw models status --probe
```

Notlar:

- Prob satırları kimlik doğrulama profillerinden, ortam kimlik bilgilerinden veya `models.json` dosyasından gelebilir.
- Açık `auth.order.<provider>` saklanan bir profili dışarıda bırakırsa, prob
  onu denemek yerine o profil için `excluded_by_auth_order` bildirir.
- Kimlik doğrulama varsa ancak OpenClaw bu sağlayıcı için prob yapılabilir bir model adayı çözemiyorsa,
  prob `status: no_model` bildirir.
- Hız sınırı cooldown'ları model kapsamlı olabilir. Bir model için cooldown durumundaki bir profil,
  aynı sağlayıcıdaki kardeş bir model için yine de kullanılabilir olabilir.

İsteğe bağlı operasyon betikleri (systemd/Termux) burada belgelenmiştir:
[Kimlik doğrulama izleme betikleri](/tr/help/scripts#auth-monitoring-scripts)

## Anthropic notu

Anthropic `claude-cli` backend yeniden desteklenmektedir.

- Anthropic çalışanları bize bu OpenClaw entegrasyon yoluna yeniden izin verildiğini söyledi.
- Bu nedenle OpenClaw, Anthropic yeni bir politika yayımlamadıkça
  Anthropic destekli çalıştırmalar için Claude CLI yeniden kullanımını ve `claude -p` kullanımını
  onaylanmış kabul eder.
- Anthropic API anahtarları, uzun ömürlü gateway host'ları ve açık sunucu tarafı
  faturalama kontrolü için en öngörülebilir seçenek olmaya devam eder.

## Model kimlik doğrulama durumunu kontrol etme

```bash
openclaw models status
openclaw doctor
```

## API anahtarı döndürme davranışı (gateway)

Bazı sağlayıcılar, bir API çağrısı sağlayıcı hız sınırına takıldığında
isteği alternatif anahtarlarla yeniden denemeyi destekler.

- Öncelik sırası:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY` (tek geçersiz kılma)
  - `<PROVIDER>_API_KEYS`
  - `<PROVIDER>_API_KEY`
  - `<PROVIDER>_API_KEY_*`
- Google sağlayıcıları ek yedek olarak `GOOGLE_API_KEY` değerini de içerir.
- Aynı anahtar listesi kullanılmadan önce tekrarları kaldırılarak tekilleştirilir.
- OpenClaw yalnızca hız sınırı hatalarında bir sonraki anahtarla yeniden dener (örneğin
  `429`, `rate_limit`, `quota`, `resource exhausted`, `Too many concurrent
requests`, `ThrottlingException`, `concurrency limit reached` veya
  `workers_ai ... quota limit exceeded`).
- Hız sınırı dışındaki hatalar alternatif anahtarlarla yeniden denenmez.
- Tüm anahtarlar başarısız olursa, son denemeden gelen son hata döndürülür.

## Hangi kimlik bilgisinin kullanılacağını kontrol etme

### Oturum başına (sohbet komutu)

Geçerli oturum için belirli bir sağlayıcı kimlik bilgisini sabitlemek üzere `/model <alias-or-id>@<profileId>` kullanın (örnek profil kimlikleri: `anthropic:default`, `anthropic:work`).

Kompakt bir seçici için `/model` (veya `/model list`) kullanın; tam görünüm için `/model status` kullanın (adaylar + sonraki kimlik doğrulama profili, ayrıca yapılandırılmışsa sağlayıcı uç nokta ayrıntıları).

### Aracı başına (CLI geçersiz kılma)

Bir aracı için açık kimlik doğrulama profili sırası geçersiz kılmasını ayarlayın (o aracının `auth-state.json` dosyasında saklanır):

```bash
openclaw models auth order get --provider anthropic
openclaw models auth order set --provider anthropic anthropic:default
openclaw models auth order clear --provider anthropic
```

Belirli bir aracıyı hedeflemek için `--agent <id>` kullanın; yapılandırılmış varsayılan aracıyı kullanmak için bunu atlayın.
Sıra sorunlarını hata ayıklarken, `openclaw models status --probe` dışarıda bırakılan
saklanan profilleri sessizce atlamak yerine `excluded_by_auth_order` olarak gösterir.
Cooldown sorunlarını hata ayıklarken, hız sınırı cooldown'larının tüm sağlayıcı profiline değil,
tek bir model kimliğine bağlı olabileceğini unutmayın.

## Sorun giderme

### "No credentials found"

Anthropic profili eksikse, **gateway host** üzerinde bir Anthropic API anahtarı yapılandırın
veya Anthropic setup-token yolunu kurun, ardından yeniden kontrol edin:

```bash
openclaw models status
```

### Token süresi dolmak üzere/dolmuş

Hangi profilin süresinin dolmak üzere olduğunu doğrulamak için `openclaw models status` çalıştırın. Bir
Anthropic token profili eksikse veya süresi dolmuşsa, bu kurulumu
setup-token ile yenileyin veya bir Anthropic API anahtarına geçin.
