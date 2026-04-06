---
read_when:
    - OpenClaw OAuth sürecini uçtan uca anlamak istiyorsunuz
    - Belirteç geçersizleşmesi / oturum kapatma sorunlarıyla karşılaştınız
    - Claude CLI veya OAuth kimlik doğrulama akışlarını istiyorsunuz
    - Birden fazla hesap veya profil yönlendirmesi istiyorsunuz
summary: 'OpenClaw içinde OAuth: belirteç değişimi, depolama ve çok hesaplı kullanım kalıpları'
title: OAuth
x-i18n:
    generated_at: "2026-04-06T03:07:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: 402e20dfeb6ae87a90cba5824a56a7ba3b964f3716508ea5cc48a47e5affdd73
    source_path: concepts/oauth.md
    workflow: 15
---

# OAuth

OpenClaw, bunu sunan sağlayıcılar için OAuth üzerinden “abonelik kimlik doğrulamasını” destekler
(özellikle **OpenAI Codex (ChatGPT OAuth)**). Anthropic için pratik ayrım
artık şöyledir:

- **Anthropic API anahtarı**: normal Anthropic API faturalandırması
- **OpenClaw içinde Anthropic abonelik kimlik doğrulaması**: Anthropic, OpenClaw
  kullanıcılarına **4 Nisan 2026 saat 12:00 PT / 20:00 BST** tarihinde bunun artık
  **Extra Usage** gerektirdiğini bildirdi

OpenAI Codex OAuth, OpenClaw gibi harici araçlarda kullanım için açıkça desteklenir.
Bu sayfa şunları açıklar:

Anthropic için üretimde, önerilen daha güvenli yol API anahtarı kimlik doğrulamasıdır.

- OAuth **belirteç değişiminin** nasıl çalıştığını (PKCE)
- belirteçlerin **nerede depolandığını** (ve neden)
- **birden fazla hesabın** nasıl ele alınacağını (profiller + oturum başına geçersiz kılmalar)

OpenClaw ayrıca kendi OAuth veya API anahtarı
akışlarını gönderen **sağlayıcı plugin**'lerini de destekler. Bunları şu şekilde çalıştırın:

```bash
openclaw models auth login --provider <id>
```

## Belirteç havuzu (neden var)

OAuth sağlayıcıları genellikle oturum açma/yenileme akışları sırasında **yeni bir yenileme belirteci** üretir. Bazı sağlayıcılar (veya OAuth istemcileri), aynı kullanıcı/uygulama için yenisi verildiğinde eski yenileme belirteçlerini geçersiz kılabilir.

Pratik belirti:

- OpenClaw üzerinden _ve_ Claude Code / Codex CLI üzerinden oturum açarsınız → bunlardan biri daha sonra rastgele “oturumu kapatılmış” olur

Bunu azaltmak için OpenClaw, `auth-profiles.json` dosyasını bir **belirteç havuzu** olarak ele alır:

- çalışma zamanı kimlik bilgilerini **tek bir yerden** okur
- birden fazla profili tutabilir ve bunları deterministik şekilde yönlendirebiliriz
- kimlik bilgileri Codex CLI gibi harici bir CLI'dan yeniden kullanıldığında, OpenClaw
  bunları kaynak bilgisiyle yansıtır ve yenileme belirtecini kendi başına
  döndürmek yerine bu harici kaynağı yeniden okur

## Depolama (belirteçler nerede bulunur)

Gizli bilgiler **aracı başına** saklanır:

- Kimlik doğrulama profilleri (OAuth + API anahtarları + isteğe bağlı değer düzeyi başvurular): `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- Eski uyumluluk dosyası: `~/.openclaw/agents/<agentId>/agent/auth.json`
  (statik `api_key` girdileri bulunduğunda temizlenir)

Eski yalnızca içe aktarma dosyası (hâlâ desteklenir, ancak ana depo değildir):

- `~/.openclaw/credentials/oauth.json` (ilk kullanımda `auth-profiles.json` içine içe aktarılır)

Yukarıdakilerin tümü `$OPENCLAW_STATE_DIR` değerine de uyar (durum dizini geçersiz kılması). Tam başvuru: [/gateway/configuration](/tr/gateway/configuration-reference#auth-storage)

Statik gizli başvurular ve çalışma zamanı anlık görüntü etkinleştirme davranışı için bkz. [Secrets Management](/tr/gateway/secrets).

## Anthropic eski belirteç uyumluluğu

<Warning>
Anthropic'in herkese açık Claude Code belgeleri, Claude Code'un doğrudan kullanımının
Claude abonelik sınırları içinde kaldığını söyler. Ayrı olarak, Anthropic **4 Nisan 2026 saat 12:00 PT / 20:00 BST** tarihinde OpenClaw kullanıcılarına **OpenClaw'ın bir
üçüncü taraf harness** olarak sayıldığını bildirdi. Mevcut Anthropic belirteç profilleri teknik olarak OpenClaw içinde kullanılabilir durumda kalır, ancak Anthropic, OpenClaw yolunun artık bu trafik için **Extra
Usage** gerektirdiğini söylüyor (abonelikten ayrı olarak kullandıkça öde şeklinde faturalandırılır).

Anthropic'in mevcut doğrudan-Claude-Code plan belgeleri için bkz. [Using Claude Code
with your Pro or Max
plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
ve [Using Claude Code with your Team or Enterprise
plan](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/).

OpenClaw içinde diğer abonelik tarzı seçenekleri istiyorsanız bkz. [OpenAI
Codex](/tr/providers/openai), [Qwen Cloud Coding
Plan](/tr/providers/qwen), [MiniMax Coding Plan](/tr/providers/minimax),
ve [Z.AI / GLM Coding Plan](/tr/providers/glm).
</Warning>

OpenClaw artık Anthropic setup-token'ı yeniden eski/el ile bir yol olarak sunuyor.
Anthropic'in OpenClaw'a özgü faturalandırma bildirimi bu yol için de geçerlidir; bu nedenle
Anthropic'in OpenClaw güdümlü Claude oturum açma trafiği için **Extra Usage** gerektirdiği beklentisiyle kullanın.

## Anthropic Claude CLI geçişi

Anthropic artık OpenClaw içinde desteklenen yerel bir Claude CLI geçiş yoluna sahip değildir.
Anthropic trafiği için Anthropic API anahtarlarını kullanın veya eski
belirteç tabanlı kimlik doğrulamayı yalnızca zaten yapılandırılmış olduğu yerlerde ve
Anthropic'in bu OpenClaw yolunu **Extra Usage** olarak değerlendirdiği beklentisiyle koruyun.

## OAuth değişimi (oturum açma nasıl çalışır)

OpenClaw'ın etkileşimli oturum açma akışları `@mariozechner/pi-ai` içinde uygulanır ve sihirbazlara/komutlara bağlanır.

### Anthropic setup-token

Akış biçimi:

1. OpenClaw içinden Anthropic setup-token başlatın veya paste-token yapın
2. OpenClaw ortaya çıkan Anthropic kimlik bilgisini bir kimlik doğrulama profilinde saklar
3. model seçimi `anthropic/...` üzerinde kalır
4. mevcut Anthropic kimlik doğrulama profilleri geri alma/sıra denetimi için kullanılabilir kalır

### OpenAI Codex (ChatGPT OAuth)

OpenAI Codex OAuth, OpenClaw iş akışları dahil olmak üzere Codex CLI dışında kullanım için açıkça desteklenir.

Akış biçimi (PKCE):

1. PKCE doğrulayıcı/sorgulama + rastgele `state` oluşturun
2. `https://auth.openai.com/oauth/authorize?...` adresini açın
3. geri çağırmayı `http://127.0.0.1:1455/auth/callback` üzerinde yakalamayı deneyin
4. geri çağırma bağlanamazsa (veya uzak/headless kullanıyorsanız), yönlendirme URL'sini/kodunu yapıştırın
5. `https://auth.openai.com/oauth/token` adresinde değişim yapın
6. erişim belirtecinden `accountId` çıkarın ve `{ access, refresh, expires, accountId }` olarak saklayın

Sihirbaz yolu `openclaw onboard` → kimlik doğrulama seçimi `openai-codex` şeklindedir.

## Yenileme + süre sonu

Profiller bir `expires` zaman damgası saklar.

Çalışma zamanında:

- `expires` gelecekteyse → saklanan erişim belirtecini kullanın
- süresi dolmuşsa → yenileyin (bir dosya kilidi altında) ve saklanan kimlik bilgilerini üzerine yazın
- istisna: yeniden kullanılan harici CLI kimlik bilgileri harici olarak yönetilmeye devam eder; OpenClaw
  CLI kimlik doğrulama deposunu yeniden okur ve kopyalanan yenileme belirtecini asla kendisi harcamaz

Yenileme akışı otomatiktir; genel olarak belirteçleri el ile yönetmeniz gerekmez.

## Birden fazla hesap (profiller) + yönlendirme

İki kalıp:

### 1) Tercih edilen: ayrı aracılar

“kişisel” ve “iş” hesaplarının hiç etkileşime girmemesini istiyorsanız yalıtılmış aracılar kullanın (ayrı oturumlar + kimlik bilgileri + çalışma alanı):

```bash
openclaw agents add work
openclaw agents add personal
```

Ardından aracı başına kimlik doğrulamayı yapılandırın (sihirbaz) ve sohbetleri doğru aracıya yönlendirin.

### 2) Gelişmiş: tek bir aracıda birden fazla profil

`auth-profiles.json`, aynı sağlayıcı için birden fazla profil kimliğini destekler.

Hangi profilin kullanılacağını seçin:

- genel olarak yapılandırma sıralamasıyla (`auth.order`)
- oturum başına `/model ...@<profileId>` ile

Örnek (oturum geçersiz kılması):

- `/model Opus@anthropic:work`

Hangi profil kimliklerinin var olduğunu görme yolu:

- `openclaw channels list --json` (`auth[]` alanını gösterir)

İlgili belgeler:

- [/concepts/model-failover](/tr/concepts/model-failover) (döndürme + bekleme süresi kuralları)
- [/tools/slash-commands](/tr/tools/slash-commands) (komut yüzeyi)

## İlgili

- [Authentication](/tr/gateway/authentication) — model sağlayıcı kimlik doğrulamasına genel bakış
- [Secrets](/tr/gateway/secrets) — kimlik bilgisi depolama ve SecretRef
- [Configuration Reference](/tr/gateway/configuration-reference#auth-storage) — kimlik doğrulama yapılandırma anahtarları
