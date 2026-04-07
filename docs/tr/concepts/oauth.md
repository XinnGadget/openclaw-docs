---
read_when:
    - OpenClaw OAuth'u uçtan uca anlamak istiyorsunuz
    - Token geçersizleşmesi / oturum kapanması sorunlarıyla karşılaştınız
    - Claude CLI veya OAuth kimlik doğrulama akışlarını istiyorsunuz
    - Birden fazla hesap veya profil yönlendirmesi istiyorsunuz
summary: 'OpenClaw''da OAuth: token değişimi, depolama ve çoklu hesap düzenleri'
title: OAuth
x-i18n:
    generated_at: "2026-04-07T08:44:24Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4117fee70e3e64fd3a762403454ac2b78de695d2b85a7146750c6de615921e02
    source_path: concepts/oauth.md
    workflow: 15
---

# OAuth

OpenClaw, bunu sunan sağlayıcılar için OAuth aracılığıyla “subscription auth” desteği sağlar
(özellikle **OpenAI Codex (ChatGPT OAuth)**). Anthropic için pratik ayrım artık şöyledir:

- **Anthropic API key**: normal Anthropic API faturalandırması
- **OpenClaw içinde Anthropic Claude CLI / subscription auth**: Anthropic personeli
  bu kullanımın tekrar izinli olduğunu bize söyledi

OpenAI Codex OAuth, OpenClaw gibi harici araçlarda kullanım için açıkça desteklenir. Bu sayfa şunları açıklar:

Üretimde Anthropic için, önerilen daha güvenli yol API key kimlik doğrulamasıdır.

- OAuth **token exchange** işleminin nasıl çalıştığı (PKCE)
- token'ların **nerede depolandığı** (ve neden)
- **birden fazla hesabın** nasıl ele alınacağı (profiller + oturum başına geçersiz kılmalar)

OpenClaw ayrıca kendi OAuth veya API‑key
akışlarıyla gelen **provider plugins** desteği de sunar. Şu komutla çalıştırın:

```bash
openclaw models auth login --provider <id>
```

## Token sink (neden vardır)

OAuth sağlayıcıları, giriş/yenileme akışları sırasında yaygın olarak **yeni bir refresh token** üretir. Bazı sağlayıcılar (veya OAuth istemcileri), aynı kullanıcı/uygulama için yenisi verildiğinde daha eski refresh token'ları geçersiz kılabilir.

Pratik belirti:

- OpenClaw üzerinden _ve_ Claude Code / Codex CLI üzerinden giriş yaparsınız → bunlardan biri daha sonra rastgele “oturumu kapanmış” hale gelir

Bunu azaltmak için OpenClaw, `auth-profiles.json` dosyasını bir **token sink** olarak ele alır:

- çalışma zamanı kimlik bilgilerini **tek bir yerden** okur
- birden fazla profili tutabilir ve bunları deterministik olarak yönlendirebiliriz
- kimlik bilgileri Codex CLI gibi harici bir CLI'dan yeniden kullanıldığında, OpenClaw
  bunları kaynak bilgisiyle yansıtır ve refresh token'ı kendisi döndürmek yerine
  o harici kaynağı yeniden okur

## Depolama (token'lar nerede bulunur)

Gizli bilgiler **agent başına** depolanır:

- Kimlik doğrulama profilleri (OAuth + API key'ler + isteğe bağlı değer düzeyi başvurular): `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- Legacy uyumluluk dosyası: `~/.openclaw/agents/<agentId>/agent/auth.json`
  (statik `api_key` girdileri bulunduğunda temizlenir)

Yalnızca legacy içe aktarma dosyası (hala desteklenir, ancak ana depo değildir):

- `~/.openclaw/credentials/oauth.json` (ilk kullanımda `auth-profiles.json` içine aktarılır)

Yukarıdakilerin tümü `$OPENCLAW_STATE_DIR` (durum dizini geçersiz kılması) ayarına da uyar. Tam başvuru: [/gateway/configuration](/tr/gateway/configuration-reference#auth-storage)

Statik gizli bilgi başvuruları ve çalışma zamanı anlık görüntü etkinleştirme davranışı için bkz. [Secrets Management](/tr/gateway/secrets).

## Anthropic legacy token uyumluluğu

<Warning>
Anthropic'in herkese açık Claude Code belgelerinde, Claude Code'un doğrudan kullanımının
Claude abonelik sınırları içinde kaldığı belirtilir ve Anthropic personeli bize
OpenClaw tarzı Claude CLI kullanımına tekrar izin verildiğini söyledi. Bu nedenle OpenClaw,
Anthropic yeni bir ilke
yayınlamadıkça, Claude CLI yeniden kullanımını ve `claude -p` kullanımını bu entegrasyon için onaylı kabul eder.

Anthropic'in güncel doğrudan-Claude-Code plan belgeleri için bkz. [Using Claude Code
with your Pro or Max
plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
ve [Using Claude Code with your Team or Enterprise
plan](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/).

OpenClaw'da diğer abonelik tarzı seçenekleri istiyorsanız bkz. [OpenAI
Codex](/tr/providers/openai), [Qwen Cloud Coding
Plan](/tr/providers/qwen), [MiniMax Coding Plan](/tr/providers/minimax)
ve [Z.AI / GLM Coding Plan](/tr/providers/glm).
</Warning>

OpenClaw, Anthropic setup-token'ı desteklenen bir token-auth yolu olarak da sunar, ancak artık mümkün olduğunda Claude CLI yeniden kullanımını ve `claude -p` kullanımını tercih eder.

## Anthropic Claude CLI geçişi

OpenClaw, Anthropic Claude CLI yeniden kullanımını yeniden destekler. Ana makinede
zaten yerel bir Claude girişiniz varsa, onboarding/configure bunu doğrudan yeniden kullanabilir.

## OAuth değişimi (giriş nasıl çalışır)

OpenClaw'ın etkileşimli giriş akışları `@mariozechner/pi-ai` içinde uygulanır ve sihirbazlara/komutlara bağlanır.

### Anthropic setup-token

Akış şekli:

1. OpenClaw'dan Anthropic setup-token'ı başlatın veya token yapıştırın
2. OpenClaw, ortaya çıkan Anthropic kimlik bilgisini bir auth profile içinde depolar
3. model seçimi `anthropic/...` üzerinde kalır
4. mevcut Anthropic auth profile'ları geri alma/sıralama denetimi için kullanılabilir olmaya devam eder

### OpenAI Codex (ChatGPT OAuth)

OpenAI Codex OAuth, Codex CLI dışındaki kullanımlar için, OpenClaw iş akışları dahil, açıkça desteklenir.

Akış şekli (PKCE):

1. PKCE verifier/challenge + rastgele `state` üretin
2. `https://auth.openai.com/oauth/authorize?...` adresini açın
3. geri çağrıyı `http://127.0.0.1:1455/auth/callback` üzerinde yakalamayı deneyin
4. geri çağrı bağlanamazsa (veya uzaktan/headless çalışıyorsanız), yönlendirme URL'sini/kodunu yapıştırın
5. `https://auth.openai.com/oauth/token` üzerinde değiş tokuş yapın
6. access token'dan `accountId` değerini çıkarın ve `{ access, refresh, expires, accountId }` değerini depolayın

Sihirbaz yolu: `openclaw onboard` → kimlik doğrulama seçeneği `openai-codex`.

## Yenileme + süre sonu

Profiller bir `expires` zaman damgası depolar.

Çalışma zamanında:

- `expires` gelecekteyse → depolanan access token'ı kullanın
- süresi dolmuşsa → yenileyin (bir dosya kilidi altında) ve depolanan kimlik bilgilerini üzerine yazın
- istisna: yeniden kullanılan harici CLI kimlik bilgileri haricen yönetilmeye devam eder; OpenClaw
  CLI auth deposunu yeniden okur ve kopyalanmış refresh token'ı asla kendisi kullanmaz

Yenileme akışı otomatiktir; genel olarak token'ları elle yönetmeniz gerekmez.

## Birden fazla hesap (profiller) + yönlendirme

İki düzen vardır:

### 1) Tercih edilen: ayrı agent'lar

“kişisel” ve “iş” hesaplarının asla etkileşmemesini istiyorsanız, yalıtılmış agent'lar kullanın (ayrı oturumlar + kimlik bilgileri + çalışma alanı):

```bash
openclaw agents add work
openclaw agents add personal
```

Ardından agent başına kimlik doğrulamayı yapılandırın (sihirbaz) ve sohbetleri doğru agent'a yönlendirin.

### 2) Gelişmiş: tek bir agent içinde birden fazla profil

`auth-profiles.json`, aynı sağlayıcı için birden fazla profil kimliğini destekler.

Hangi profilin kullanılacağını seçin:

- genel olarak yapılandırma sıralamasıyla (`auth.order`)
- oturum başına `/model ...@<profileId>` ile

Örnek (oturum geçersiz kılması):

- `/model Opus@anthropic:work`

Hangi profil kimliklerinin mevcut olduğunu görme:

- `openclaw channels list --json` (`auth[]` gösterir)

İlgili belgeler:

- [/concepts/model-failover](/tr/concepts/model-failover) (döndürme + bekleme süresi kuralları)
- [/tools/slash-commands](/tr/tools/slash-commands) (komut yüzeyi)

## İlgili

- [Authentication](/tr/gateway/authentication) — model sağlayıcısı kimlik doğrulamaya genel bakış
- [Secrets](/tr/gateway/secrets) — kimlik bilgisi depolama ve SecretRef
- [Configuration Reference](/tr/gateway/configuration-reference#auth-storage) — auth yapılandırma anahtarları
