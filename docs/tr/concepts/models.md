---
read_when:
    - Models CLI ekliyor veya değiştiriyorsunuz (models list/set/scan/aliases/fallbacks)
    - Model yedeğe düşme davranışını veya seçim UX’ini değiştiriyorsunuz
    - Model tarama yoklamalarını güncelliyorsunuz (araçlar/görseller)
summary: 'Models CLI: listeleme, ayarlama, takma adlar, yedekler, tarama, durum'
title: Models CLI
x-i18n:
    generated_at: "2026-04-06T03:07:16Z"
    model: gpt-5.4
    provider: openai
    source_hash: 299602ccbe0c3d6bbdb2deab22bc60e1300ef6843ed0b8b36be574cc0213c155
    source_path: concepts/models.md
    workflow: 15
---

# Models CLI

Kimlik doğrulama profili rotasyonu, cooldown süreleri ve bunun yedeklerle nasıl etkileştiği için bkz. [/concepts/model-failover](/tr/concepts/model-failover).
Hızlı sağlayıcı genel görünümü + örnekler: [/concepts/model-providers](/tr/concepts/model-providers).

## Model seçimi nasıl çalışır

OpenClaw modelleri şu sırayla seçer:

1. **Birincil** model (`agents.defaults.model.primary` veya `agents.defaults.model`).
2. `agents.defaults.model.fallbacks` içindeki **yedekler** (sırayla).
3. **Sağlayıcı kimlik doğrulama yedeğe düşmesi**, bir sonraki modele geçmeden önce sağlayıcının içinde gerçekleşir.

İlgili:

- `agents.defaults.models`, OpenClaw’un kullanabileceği modellerin izin listesidir/kataloğudur (artı takma adlar).
- `agents.defaults.imageModel`, **yalnızca** birincil model görselleri kabul edemediğinde kullanılır.
- `agents.defaults.pdfModel`, `pdf` aracı tarafından kullanılır. Belirtilmezse araç sırasıyla `agents.defaults.imageModel`, ardından çözümlenmiş oturum/varsayılan modele geri döner.
- `agents.defaults.imageGenerationModel`, paylaşılan görsel oluşturma yeteneği tarafından kullanılır. Belirtilmezse `image_generate`, kimlik doğrulama destekli bir sağlayıcı varsayılanını yine de çıkarabilir. Önce mevcut varsayılan sağlayıcıyı, ardından sağlayıcı kimliği sırasına göre kayıtlı diğer görsel oluşturma sağlayıcılarını dener. Belirli bir sağlayıcı/model ayarlarsanız, o sağlayıcının kimlik doğrulamasını/API anahtarını da yapılandırın.
- `agents.defaults.musicGenerationModel`, paylaşılan müzik oluşturma yeteneği tarafından kullanılır. Belirtilmezse `music_generate`, kimlik doğrulama destekli bir sağlayıcı varsayılanını yine de çıkarabilir. Önce mevcut varsayılan sağlayıcıyı, ardından sağlayıcı kimliği sırasına göre kayıtlı diğer müzik oluşturma sağlayıcılarını dener. Belirli bir sağlayıcı/model ayarlarsanız, o sağlayıcının kimlik doğrulamasını/API anahtarını da yapılandırın.
- `agents.defaults.videoGenerationModel`, paylaşılan video oluşturma yeteneği tarafından kullanılır. Belirtilmezse `video_generate`, kimlik doğrulama destekli bir sağlayıcı varsayılanını yine de çıkarabilir. Önce mevcut varsayılan sağlayıcıyı, ardından sağlayıcı kimliği sırasına göre kayıtlı diğer video oluşturma sağlayıcılarını dener. Belirli bir sağlayıcı/model ayarlarsanız, o sağlayıcının kimlik doğrulamasını/API anahtarını da yapılandırın.
- Aracı başına varsayılanlar, `agents.list[].model` ve bağlamalar aracılığıyla `agents.defaults.model` değerini geçersiz kılabilir (bkz. [/concepts/multi-agent](/tr/concepts/multi-agent)).

## Hızlı model ilkesi

- Birincil modelinizi, sizin için mevcut olan en güçlü en yeni nesil model olarak ayarlayın.
- Maliyet/gecikmeye duyarlı işler ve daha düşük riskli sohbetler için yedekleri kullanın.
- Araç etkin aracılar veya güvenilmeyen girdiler için eski/daha zayıf model katmanlarından kaçının.

## Onboarding (önerilir)

Yapılandırmayı elle düzenlemek istemiyorsanız onboarding çalıştırın:

```bash
openclaw onboard
```

Bu, yaygın sağlayıcılar için model + kimlik doğrulama kurulumu yapabilir; buna **OpenAI Code (Codex) subscription** (OAuth) ve **Anthropic** (API anahtarı veya Claude CLI) dahildir.

## Yapılandırma anahtarları (genel bakış)

- `agents.defaults.model.primary` ve `agents.defaults.model.fallbacks`
- `agents.defaults.imageModel.primary` ve `agents.defaults.imageModel.fallbacks`
- `agents.defaults.pdfModel.primary` ve `agents.defaults.pdfModel.fallbacks`
- `agents.defaults.imageGenerationModel.primary` ve `agents.defaults.imageGenerationModel.fallbacks`
- `agents.defaults.videoGenerationModel.primary` ve `agents.defaults.videoGenerationModel.fallbacks`
- `agents.defaults.models` (izin listesi + takma adlar + sağlayıcı parametreleri)
- `models.providers` (`models.json` içine yazılan özel sağlayıcılar)

Model başvuruları küçük harfe normalize edilir. `z.ai/*` gibi sağlayıcı takma adları `zai/*` olarak normalize edilir.

Sağlayıcı yapılandırma örnekleri (OpenCode dahil) şurada bulunur:
[/providers/opencode](/tr/providers/opencode).

## "Model is not allowed" (ve yanıtların neden durduğu)

`agents.defaults.models` ayarlanmışsa, `/model` ve oturum geçersiz kılmaları için **izin listesi** haline gelir. Kullanıcı bu izin listesinde olmayan bir modeli seçtiğinde OpenClaw şunu döndürür:

```
Model "provider/model" is not allowed. Use /model to list available models.
```

Bu, normal bir yanıt üretilmeden **önce** gerçekleşir; bu yüzden mesaj sanki “yanıt vermedi” gibi hissedilebilir. Düzeltmek için şunlardan birini yapın:

- Modeli `agents.defaults.models` içine ekleyin, veya
- İzin listesini temizleyin (`agents.defaults.models` değerini kaldırın), veya
- `/model list` içinden bir model seçin.

Örnek izin listesi yapılandırması:

```json5
{
  agent: {
    model: { primary: "anthropic/claude-sonnet-4-6" },
    models: {
      "anthropic/claude-sonnet-4-6": { alias: "Sonnet" },
      "anthropic/claude-opus-4-6": { alias: "Opus" },
    },
  },
}
```

## Sohbette model değiştirme (`/model`)

Yeniden başlatmadan geçerli oturum için modelleri değiştirebilirsiniz:

```
/model
/model list
/model 3
/model openai/gpt-5.4
/model status
```

Notlar:

- `/model` (ve `/model list`) kompakt, numaralandırılmış bir seçicidir (model ailesi + kullanılabilir sağlayıcılar).
- Discord üzerinde `/model` ve `/models`, sağlayıcı ve model açılır listeleri ile bir Submit adımı içeren etkileşimli bir seçici açar.
- `/model <#>`, bu seçiciden seçim yapar.
- `/model`, yeni oturum seçimini hemen kalıcı hale getirir.
- Aracı boşta ise bir sonraki çalıştırma yeni modeli hemen kullanır.
- Bir çalıştırma zaten etkinse OpenClaw canlı geçişi beklemede olarak işaretler ve yalnızca temiz bir yeniden deneme noktasında yeni modele yeniden başlar.
- Araç etkinliği veya yanıt çıktısı zaten başladıysa, bekleyen geçiş daha sonraki bir yeniden deneme fırsatına ya da sonraki kullanıcı turuna kadar kuyrukta kalabilir.
- `/model status` ayrıntılı görünümdür (kimlik doğrulama adayları ve yapılandırılmışsa sağlayıcı uç noktası `baseUrl` + `api` modu).
- Model başvuruları ilk `/` karakterine göre bölünerek ayrıştırılır. `/model <ref>` yazarken `provider/model` kullanın.
- Model kimliğinin kendisi `/` içeriyorsa (OpenRouter tarzı), sağlayıcı önekini eklemelisiniz (örnek: `/model openrouter/moonshotai/kimi-k2`).
- Sağlayıcıyı atlarsanız OpenClaw girdiyi şu sırayla çözümler:
  1. takma ad eşleşmesi
  2. bu tam öneksiz model kimliği için benzersiz yapılandırılmış sağlayıcı eşleşmesi
  3. yapılandırılmış varsayılan sağlayıcıya yönelik kullanımdan kaldırılmış geri dönüş
     O sağlayıcı artık yapılandırılmış varsayılan modeli sunmuyorsa, OpenClaw eski kaldırılmış-sağlayıcı varsayılanını göstermemek için bunun yerine ilk yapılandırılmış sağlayıcı/model çiftine geri döner.

Komutun tam davranışı/yapılandırması: [Slash komutları](/tr/tools/slash-commands).

## CLI komutları

```bash
openclaw models list
openclaw models status
openclaw models set <provider/model>
openclaw models set-image <provider/model>

openclaw models aliases list
openclaw models aliases add <alias> <provider/model>
openclaw models aliases remove <alias>

openclaw models fallbacks list
openclaw models fallbacks add <provider/model>
openclaw models fallbacks remove <provider/model>
openclaw models fallbacks clear

openclaw models image-fallbacks list
openclaw models image-fallbacks add <provider/model>
openclaw models image-fallbacks remove <provider/model>
openclaw models image-fallbacks clear
```

`openclaw models` (alt komut olmadan), `models status` için bir kısayoldur.

### `models list`

Varsayılan olarak yapılandırılmış modelleri gösterir. Faydalı bayraklar:

- `--all`: tam katalog
- `--local`: yalnızca yerel sağlayıcılar
- `--provider <name>`: sağlayıcıya göre filtrele
- `--plain`: satır başına bir model
- `--json`: makine tarafından okunabilir çıktı

### `models status`

Çözümlenmiş birincil modeli, yedekleri, görsel modelini ve yapılandırılmış sağlayıcıların kimlik doğrulama genel görünümünü gösterir. Ayrıca kimlik doğrulama deposunda bulunan profiller için OAuth sona erme durumunu da gösterir (varsayılan olarak 24 saat içinde uyarır). `--plain` yalnızca çözümlenmiş birincil modeli yazdırır.
OAuth durumu her zaman gösterilir (ve `--json` çıktısına dahil edilir). Yapılandırılmış bir sağlayıcının kimlik bilgileri yoksa `models status`, bir **Missing auth** bölümü yazdırır.
JSON, `auth.oauth` (uyarı penceresi + profiller) ve `auth.providers` (ortam değişkeni destekli kimlik bilgileri dahil, sağlayıcı başına etkin kimlik doğrulama) alanlarını içerir. `auth.oauth` yalnızca kimlik doğrulama deposu profillerinin sağlık durumudur; yalnızca ortam değişkeni kullanan sağlayıcılar burada görünmez.
Otomasyon için `--check` kullanın (eksik/süresi dolmuşsa çıkış `1`, süresi dolmak üzereyse `2`).
Canlı kimlik doğrulama kontrolleri için `--probe` kullanın; yoklama satırları kimlik doğrulama profillerinden, ortam değişkeni kimlik bilgilerinden veya `models.json` içinden gelebilir.
Açık `auth.order.<provider>` depolanmış bir profili dışarıda bırakıyorsa, yoklama bunu denemek yerine `excluded_by_auth_order` bildirir. Kimlik doğrulama varsa ama o sağlayıcı için yoklanabilir bir model çözümlenemiyorsa, yoklama `status: no_model` bildirir.

Kimlik doğrulama seçimi sağlayıcıya/hesaba bağlıdır. Her zaman açık gateway host’ları için API anahtarları genellikle en öngörülebilir seçenektir; Claude CLI yeniden kullanımı ve mevcut Anthropic OAuth/token profilleri de desteklenir.

Örnek (Claude CLI):

```bash
claude auth login
openclaw models status
```

## Tarama (OpenRouter ücretsiz modelleri)

`openclaw models scan`, OpenRouter’ın **ücretsiz model kataloğunu** inceler ve isteğe bağlı olarak modelleri araç ve görsel desteği açısından yoklayabilir.

Başlıca bayraklar:

- `--no-probe`: canlı yoklamaları atla (yalnızca meta veriler)
- `--min-params <b>`: minimum parametre boyutu (milyar)
- `--max-age-days <days>`: daha eski modelleri atla
- `--provider <name>`: sağlayıcı öneki filtresi
- `--max-candidates <n>`: yedek liste boyutu
- `--set-default`: `agents.defaults.model.primary` değerini ilk seçime ayarla
- `--set-image`: `agents.defaults.imageModel.primary` değerini ilk görsel seçime ayarla

Yoklama için bir OpenRouter API anahtarı gerekir (kimlik doğrulama profillerinden veya `OPENROUTER_API_KEY` üzerinden).
Anahtar olmadan yalnızca adayları listelemek için `--no-probe` kullanın.

Tarama sonuçları şu ölçütlere göre sıralanır:

1. Görsel desteği
2. Araç gecikmesi
3. Bağlam boyutu
4. Parametre sayısı

Girdi

- OpenRouter `/models` listesi (`:free` filtresi)
- Kimlik doğrulama profillerinden veya `OPENROUTER_API_KEY` üzerinden OpenRouter API anahtarı gerektirir (bkz. [/environment](/tr/help/environment))
- İsteğe bağlı filtreler: `--max-age-days`, `--min-params`, `--provider`, `--max-candidates`
- Yoklama denetimleri: `--timeout`, `--concurrency`

Bir TTY içinde çalıştırıldığında yedekleri etkileşimli olarak seçebilirsiniz. Etkileşimsiz kipte varsayılanları kabul etmek için `--yes` kullanın.

## Model kayıt defteri (`models.json`)

`models.providers` içindeki özel sağlayıcılar, aracı dizini altındaki `models.json` dosyasına yazılır (varsayılan `~/.openclaw/agents/<agentId>/agent/models.json`). `models.mode`, `replace` olarak ayarlanmadıkça bu dosya varsayılan olarak birleştirilir.

Eşleşen sağlayıcı kimlikleri için birleştirme kipi önceliği:

- Aracı `models.json` içinde zaten bulunan boş olmayan `baseUrl` kazanır.
- Aracı `models.json` içindeki boş olmayan `apiKey`, yalnızca o sağlayıcı mevcut yapılandırma/kimlik doğrulama profili bağlamında SecretRef tarafından yönetilmiyorsa kazanır.
- SecretRef tarafından yönetilen sağlayıcı `apiKey` değerleri, çözümlenmiş gizli değerleri kalıcı hale getirmek yerine kaynak işaretleyicilerden (`ENV_VAR_NAME` ortam başvuruları için, dosya/exec başvuruları için `secretref-managed`) yenilenir.
- SecretRef tarafından yönetilen sağlayıcı başlık değerleri, kaynak işaretleyicilerden yenilenir (ortam başvuruları için `secretref-env:ENV_VAR_NAME`, dosya/exec başvuruları için `secretref-managed`).
- Boş veya eksik aracı `apiKey`/`baseUrl` değerleri, yapılandırmadaki `models.providers` değerine geri döner.
- Diğer sağlayıcı alanları yapılandırmadan ve normalize edilmiş katalog verilerinden yenilenir.

İşaretleyici kalıcılığı kaynak tarafından belirlenir: OpenClaw işaretleyicileri çözümlenmiş çalışma zamanı gizli değerlerinden değil, etkin kaynak yapılandırma anlık görüntüsünden (çözümleme öncesi) yazar.
Bu, `openclaw agent` gibi komut odaklı yollar dahil olmak üzere OpenClaw `models.json` dosyasını her yeniden oluşturduğunda geçerlidir.

## İlgili

- [Model Providers](/tr/concepts/model-providers) — sağlayıcı yönlendirme ve kimlik doğrulama
- [Model Failover](/tr/concepts/model-failover) — yedek zincirleri
- [Image Generation](/tr/tools/image-generation) — görsel model yapılandırması
- [Music Generation](/tools/music-generation) — müzik model yapılandırması
- [Video Generation](/tools/video-generation) — video model yapılandırması
- [Configuration Reference](/tr/gateway/configuration-reference#agent-defaults) — model yapılandırma anahtarları
