---
read_when:
    - Model kimlik doğrulamasını veya OAuth süre sonunu ayıklarken
    - Kimlik doğrulama veya kimlik bilgisi depolamayı belgelerken
summary: 'Model kimlik doğrulaması: OAuth, API anahtarları ve eski Anthropic setup-token'
title: Kimlik Doğrulama
x-i18n:
    generated_at: "2026-04-06T03:07:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: f59ede3fcd7e692ad4132287782a850526acf35474b5bfcea29e0e23610636c2
    source_path: gateway/authentication.md
    workflow: 15
---

# Kimlik Doğrulama (Model Sağlayıcıları)

<Note>
Bu sayfa **model sağlayıcısı** kimlik doğrulamasını kapsar (API anahtarları, OAuth ve eski Anthropic setup-token). **Ağ geçidi bağlantısı** kimlik doğrulaması için (token, parola, trusted-proxy), [Configuration](/tr/gateway/configuration) ve [Trusted Proxy Auth](/tr/gateway/trusted-proxy-auth) sayfalarına bakın.
</Note>

OpenClaw, model sağlayıcıları için OAuth ve API anahtarlarını destekler. Her zaman açık ağ geçidi ana bilgisayarları için API anahtarları genellikle en öngörülebilir seçenektir. Sağlayıcı hesap modelinize uyuyorsa abonelik/OAuth akışları da desteklenir.

Tam OAuth akışı ve depolama düzeni için [/concepts/oauth](/tr/concepts/oauth) bölümüne bakın.
SecretRef tabanlı kimlik doğrulaması için (`env`/`file`/`exec` sağlayıcıları), [Secrets Management](/tr/gateway/secrets) bölümüne bakın.
`models status --probe` tarafından kullanılan kimlik bilgisi uygunluğu/neden kodu kuralları için
[Auth Credential Semantics](/tr/auth-credential-semantics) bölümüne bakın.

## Önerilen kurulum (API anahtarı, herhangi bir sağlayıcı)

Uzun ömürlü bir ağ geçidi çalıştırıyorsanız, seçtiğiniz sağlayıcı için bir API anahtarıyla başlayın.
Özellikle Anthropic için API anahtarı kimlik doğrulaması güvenli yoldur. OpenClaw içindeki Anthropic
abonelik tarzı kimlik doğrulama, eski setup-token yoludur ve plan sınırları yolu olarak değil,
**Ek Kullanım** yolu olarak değerlendirilmelidir.

1. Sağlayıcı konsolunuzda bir API anahtarı oluşturun.
2. Bunu **ağ geçidi ana bilgisayarına** (`openclaw gateway` çalıştıran makine) yerleştirin.

```bash
export <PROVIDER>_API_KEY="..."
openclaw models status
```

3. Gateway systemd/launchd altında çalışıyorsa, daemon'un okuyabilmesi için
   anahtarı `~/.openclaw/.env` içine koymayı tercih edin:

```bash
cat >> ~/.openclaw/.env <<'EOF'
<PROVIDER>_API_KEY=...
EOF
```

Ardından daemon'u yeniden başlatın (veya Gateway sürecinizi yeniden başlatın) ve tekrar kontrol edin:

```bash
openclaw models status
openclaw doctor
```

Ortam değişkenlerini kendiniz yönetmek istemiyorsanız, ilk kurulum sihirbazı
daemon kullanımı için API anahtarlarını depolayabilir: `openclaw onboard`.

`env.shellEnv`,
`~/.openclaw/.env`, systemd/launchd konularında ayrıntılar için [Help](/tr/help) bölümüne bakın.

## Anthropic: eski token uyumluluğu

Anthropic setup-token kimlik doğrulaması, OpenClaw içinde
eski/elle kullanılan bir yol olarak hâlâ mevcuttur. Anthropic'in herkese açık Claude Code belgeleri hâlâ doğrudan
Claude planları altında Claude Code terminal kullanımını kapsar, ancak Anthropic ayrıca
OpenClaw kullanıcılarına **OpenClaw** Claude giriş yolunun üçüncü taraf
araç kullanımı olarak sayıldığını ve abonelikten ayrı olarak faturalandırılan **Ek Kullanım**
gerektirdiğini bildirmiştir.

En açık kurulum yolu için bir Anthropic API anahtarı kullanın. OpenClaw içinde
abonelik tarzı bir Anthropic yolunu korumanız gerekiyorsa, Anthropic'in bunu **Ek Kullanım**
olarak değerlendirdiği beklentisiyle eski setup-token yolunu kullanın.

Elle token girişi (herhangi bir sağlayıcı; `auth-profiles.json` yazar + yapılandırmayı günceller):

```bash
openclaw models auth paste-token --provider openrouter
```

Sabit kimlik bilgileri için kimlik doğrulama profil başvuruları da desteklenir:

- `api_key` kimlik bilgileri `keyRef: { source, provider, id }` kullanabilir
- `token` kimlik bilgileri `tokenRef: { source, provider, id }` kullanabilir
- OAuth kipindeki profiller SecretRef kimlik bilgilerini desteklemez; `auth.profiles.<id>.mode` `"oauth"` olarak ayarlanmışsa, bu profil için SecretRef destekli `keyRef`/`tokenRef` girdisi reddedilir.

Otomasyona uygun kontrol (süresi dolmuş/eksikse çıkış `1`, süresi dolmak üzereyse `2`):

```bash
openclaw models status --check
```

Canlı kimlik doğrulama yoklamaları:

```bash
openclaw models status --probe
```

Notlar:

- Yoklama satırları kimlik doğrulama profillerinden, ortam kimlik bilgilerinden veya `models.json` dosyasından gelebilir.
- Açık `auth.order.<provider>` depolanmış bir profili dışlıyorsa, yoklama
  o profili denemek yerine `excluded_by_auth_order` bildirir.
- Kimlik doğrulama mevcutsa ancak OpenClaw o sağlayıcı için yoklanabilir bir model adayı çözemiyorsa,
  yoklama `status: no_model` bildirir.
- Hız sınırı bekleme süreleri modele özgü olabilir. Bir model için bekleme süresinde olan
  profil, aynı sağlayıcıdaki kardeş bir model için yine de kullanılabilir olabilir.

İsteğe bağlı işlem betikleri (systemd/Termux) burada belgelenmiştir:
[Auth monitoring scripts](/tr/help/scripts#auth-monitoring-scripts)

## Anthropic notu

Anthropic `claude-cli` arka ucu kaldırıldı.

- OpenClaw içindeki Anthropic trafiği için Anthropic API anahtarlarını kullanın.
- Anthropic setup-token eski/elle kullanılan bir yol olarak kalır ve
  Anthropic'in OpenClaw kullanıcılarına ilettiği Ek Kullanım faturalandırma beklentisiyle kullanılmalıdır.
- `openclaw doctor` artık eski kaldırılmış Anthropic Claude CLI durumunu algılar. Eğer
  depolanmış kimlik bilgisi baytları hâlâ mevcutsa, doctor bunları yeniden
  Anthropic token/OAuth profillerine dönüştürür. Değilse doctor eski Claude CLI
  yapılandırmasını kaldırır ve sizi API anahtarı veya setup-token kurtarmaya yönlendirir.

## Model kimlik doğrulama durumunu kontrol etme

```bash
openclaw models status
openclaw doctor
```

## API anahtarı döndürme davranışı (ağ geçidi)

Bazı sağlayıcılar, bir API çağrısı
sağlayıcı hız sınırına takıldığında isteği alternatif anahtarlarla yeniden denemeyi destekler.

- Öncelik sırası:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY` (tek geçersiz kılma)
  - `<PROVIDER>_API_KEYS`
  - `<PROVIDER>_API_KEY`
  - `<PROVIDER>_API_KEY_*`
- Google sağlayıcıları ek geri dönüş olarak `GOOGLE_API_KEY` değerini de içerir.
- Aynı anahtar listesi kullanılmadan önce tekilleştirilir.
- OpenClaw yalnızca hız sınırı hatalarında sonraki anahtarla yeniden dener (örneğin
  `429`, `rate_limit`, `quota`, `resource exhausted`, `Too many concurrent
requests`, `ThrottlingException`, `concurrency limit reached` veya
  `workers_ai ... quota limit exceeded`).
- Hız sınırı dışındaki hatalarda alternatif anahtarlarla yeniden deneme yapılmaz.
- Tüm anahtarlar başarısız olursa, son denemeden gelen nihai hata döndürülür.

## Hangi kimlik bilgisinin kullanılacağını denetleme

### Oturum başına (sohbet komutu)

Geçerli oturum için belirli bir sağlayıcı kimlik bilgisini sabitlemek üzere `/model <alias-or-id>@<profileId>` kullanın (örnek profil kimlikleri: `anthropic:default`, `anthropic:work`).

Kompakt bir seçici için `/model` (veya `/model list`) kullanın; tam görünüm için `/model status` kullanın (adaylar + sonraki kimlik doğrulama profili, ayrıca yapılandırılmışsa sağlayıcı uç nokta ayrıntıları).

### Temsilci başına (CLI geçersiz kılma)

Bir temsilci için açık bir kimlik doğrulama profili sırası geçersiz kılması ayarlayın (o temsilcinin `auth-profiles.json` dosyasında depolanır):

```bash
openclaw models auth order get --provider anthropic
openclaw models auth order set --provider anthropic anthropic:default
openclaw models auth order clear --provider anthropic
```

Belirli bir temsilciyi hedeflemek için `--agent <id>` kullanın; yapılandırılmış varsayılan temsilciyi kullanmak için bunu atlayın.
Sıra sorunlarını ayıklarken, `openclaw models status --probe` atlanan
depolanmış profilleri sessizce geçmek yerine `excluded_by_auth_order` olarak gösterir.
Bekleme süresi sorunlarını ayıklarken, hız sınırı bekleme sürelerinin tüm sağlayıcı profiline değil,
tek bir model kimliğine bağlı olabileceğini unutmayın.

## Sorun giderme

### "No credentials found"

Anthropic profili eksikse, **ağ geçidi ana bilgisayarında**
bir Anthropic API anahtarı yapılandırın veya eski Anthropic setup-token yolunu ayarlayın, ardından tekrar kontrol edin:

```bash
openclaw models status
```

### Token süresi doluyor/doldu

Hangi profilin süresinin dolmak üzere olduğunu doğrulamak için `openclaw models status` çalıştırın. Eski bir
Anthropic token profili eksikse veya süresi dolmuşsa, bu kurulumu
setup-token ile yenileyin veya bir Anthropic API anahtarına geçin.

Makinede daha eski
derlemelerden kalma eski kaldırılmış Anthropic Claude CLI durumu hâlâ varsa şunu çalıştırın:

```bash
openclaw doctor --yes
```

Depolanmış kimlik bilgisi baytları hâlâ mevcutsa Doctor, `anthropic:claude-cli` profilini yeniden Anthropic token/OAuth'a dönüştürür.
Aksi takdirde eski Claude CLI
profilini/yapılandırmasını/model başvurularını kaldırır ve sonraki adım yönergelerini bırakır.
