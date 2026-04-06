---
read_when:
    - OpenClaw ile Amazon Bedrock modellerini kullanmak istiyorsunuz
    - Model çağrıları için AWS kimlik bilgisi/bölge kurulumu gerekiyor
summary: OpenClaw ile Amazon Bedrock (Converse API) modellerini kullanın
title: Amazon Bedrock
x-i18n:
    generated_at: "2026-04-06T03:11:35Z"
    model: gpt-5.4
    provider: openai
    source_hash: 70bb29fe9199084b1179ced60935b5908318f5b80ced490bf44a45e0467c4929
    source_path: providers/bedrock.md
    workflow: 15
---

# Amazon Bedrock

OpenClaw, pi‑ai'nin **Bedrock Converse** akış sağlayıcısı üzerinden **Amazon Bedrock** modellerini kullanabilir.
Bedrock kimlik doğrulaması bir API anahtarı değil, **AWS SDK varsayılan kimlik bilgisi zinciri** kullanır.

## pi-ai neleri destekler

- Sağlayıcı: `amazon-bedrock`
- API: `bedrock-converse-stream`
- Kimlik doğrulama: AWS kimlik bilgileri (ortam değişkenleri, paylaşılan yapılandırma veya instance rolü)
- Bölge: `AWS_REGION` veya `AWS_DEFAULT_REGION` (varsayılan: `us-east-1`)

## Otomatik model keşfi

OpenClaw, **streaming** ve **metin çıktısı** destekleyen Bedrock modellerini otomatik olarak keşfedebilir.
Keşif, `bedrock:ListFoundationModels` ve
`bedrock:ListInferenceProfiles` kullanır ve sonuçlar önbelleğe alınır (varsayılan: 1 saat).

Örtük sağlayıcının nasıl etkinleştirildiği:

- `plugins.entries.amazon-bedrock.config.discovery.enabled` değeri `true` ise,
  OpenClaw hiçbir AWS env işaretleyicisi olmasa bile keşif yapmayı dener.
- `plugins.entries.amazon-bedrock.config.discovery.enabled` ayarlı değilse,
  OpenClaw örtük Bedrock sağlayıcısını yalnızca
  şu AWS kimlik doğrulama işaretleyicilerinden birini gördüğünde otomatik ekler:
  `AWS_BEARER_TOKEN_BEDROCK`, `AWS_ACCESS_KEY_ID` +
  `AWS_SECRET_ACCESS_KEY` veya `AWS_PROFILE`.
- Gerçek Bedrock çalışma zamanı kimlik doğrulama yolu yine AWS SDK varsayılan zincirini kullanır; bu nedenle
  keşif için `enabled: true` ile açıkça etkinleştirme gerekse bile
  paylaşılan yapılandırma, SSO ve IMDS instance-role kimlik doğrulaması çalışabilir.

Yapılandırma seçenekleri `plugins.entries.amazon-bedrock.config.discovery` altında bulunur:

```json5
{
  plugins: {
    entries: {
      "amazon-bedrock": {
        config: {
          discovery: {
            enabled: true,
            region: "us-east-1",
            providerFilter: ["anthropic", "amazon"],
            refreshInterval: 3600,
            defaultContextWindow: 32000,
            defaultMaxTokens: 4096,
          },
        },
      },
    },
  },
}
```

Notlar:

- `enabled` varsayılan olarak otomatik moddur. Otomatik modda OpenClaw, örtük
  Bedrock sağlayıcısını yalnızca desteklenen bir AWS env işaretleyicisi gördüğünde etkinleştirir.
- `region` varsayılan olarak `AWS_REGION` veya `AWS_DEFAULT_REGION`, ardından `us-east-1` olur.
- `providerFilter`, Bedrock sağlayıcı adlarıyla eşleşir (örneğin `anthropic`).
- `refreshInterval` saniye cinsindendir; önbelleği devre dışı bırakmak için `0` ayarlayın.
- `defaultContextWindow` (varsayılan: `32000`) ve `defaultMaxTokens` (varsayılan: `4096`)
  keşfedilen modeller için kullanılır (model sınırlarınızı biliyorsanız geçersiz kılın).
- Açık `models.providers["amazon-bedrock"]` girdileri için OpenClaw, tam çalışma zamanı kimlik doğrulama yüklemesini zorlamadan
  `AWS_BEARER_TOKEN_BEDROCK` gibi AWS env işaretleyicilerinden Bedrock env işaretleyici kimlik doğrulamasını erken çözümleyebilir.
  Gerçek model çağrısı kimlik doğrulama yolu yine AWS SDK varsayılan zincirini kullanır.

## Onboarding

1. AWS kimlik bilgilerinin **gateway host** üzerinde mevcut olduğundan emin olun:

```bash
export AWS_ACCESS_KEY_ID="AKIA..."
export AWS_SECRET_ACCESS_KEY="..."
export AWS_REGION="us-east-1"
# Optional:
export AWS_SESSION_TOKEN="..."
export AWS_PROFILE="your-profile"
# Optional (Bedrock API key/bearer token):
export AWS_BEARER_TOKEN_BEDROCK="..."
```

2. Yapılandırmanıza bir Bedrock sağlayıcısı ve model ekleyin (`apiKey` gerekmez):

```json5
{
  models: {
    providers: {
      "amazon-bedrock": {
        baseUrl: "https://bedrock-runtime.us-east-1.amazonaws.com",
        api: "bedrock-converse-stream",
        auth: "aws-sdk",
        models: [
          {
            id: "us.anthropic.claude-opus-4-6-v1:0",
            name: "Claude Opus 4.6 (Bedrock)",
            reasoning: true,
            input: ["text", "image"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 200000,
            maxTokens: 8192,
          },
        ],
      },
    },
  },
  agents: {
    defaults: {
      model: { primary: "amazon-bedrock/us.anthropic.claude-opus-4-6-v1:0" },
    },
  },
}
```

## EC2 Instance Rolleri

OpenClaw, eklenmiş bir IAM rolüyle bir EC2 instance üzerinde çalıştırıldığında AWS SDK,
kimlik doğrulaması için instance metadata service (IMDS) kullanabilir. Bedrock
model keşfi için OpenClaw, siz açıkça
`plugins.entries.amazon-bedrock.config.discovery.enabled: true` ayarlamadığınız sürece örtük sağlayıcıyı yalnızca AWS env
işaretleyicilerinden otomatik etkinleştirir.

IMDS destekli host'lar için önerilen kurulum:

- `plugins.entries.amazon-bedrock.config.discovery.enabled` değerini `true` yapın.
- `plugins.entries.amazon-bedrock.config.discovery.region` ayarlayın (veya `AWS_REGION` dışa aktarın).
- Sahte bir API anahtarına **ihtiyacınız yoktur**.
- Yalnızca otomatik mod veya durum yüzeyleri için özellikle bir env işaretleyicisi istiyorsanız `AWS_PROFILE=default` gerekir.

```bash
# Recommended: explicit discovery enable + region
openclaw config set plugins.entries.amazon-bedrock.config.discovery.enabled true
openclaw config set plugins.entries.amazon-bedrock.config.discovery.region us-east-1

# Optional: add an env marker if you want auto mode without explicit enable
export AWS_PROFILE=default
export AWS_REGION=us-east-1
```

EC2 instance rolü için **gerekli IAM izinleri**:

- `bedrock:InvokeModel`
- `bedrock:InvokeModelWithResponseStream`
- `bedrock:ListFoundationModels` (otomatik keşif için)
- `bedrock:ListInferenceProfiles` (çıkarım profili keşfi için)

Veya yönetilen `AmazonBedrockFullAccess` ilkesini ekleyin.

## Hızlı kurulum (AWS yolu)

```bash
# 1. Create IAM role and instance profile
aws iam create-role --role-name EC2-Bedrock-Access \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ec2.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

aws iam attach-role-policy --role-name EC2-Bedrock-Access \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

aws iam create-instance-profile --instance-profile-name EC2-Bedrock-Access
aws iam add-role-to-instance-profile \
  --instance-profile-name EC2-Bedrock-Access \
  --role-name EC2-Bedrock-Access

# 2. Attach to your EC2 instance
aws ec2 associate-iam-instance-profile \
  --instance-id i-xxxxx \
  --iam-instance-profile Name=EC2-Bedrock-Access

# 3. On the EC2 instance, enable discovery explicitly
openclaw config set plugins.entries.amazon-bedrock.config.discovery.enabled true
openclaw config set plugins.entries.amazon-bedrock.config.discovery.region us-east-1

# 4. Optional: add an env marker if you want auto mode without explicit enable
echo 'export AWS_PROFILE=default' >> ~/.bashrc
echo 'export AWS_REGION=us-east-1' >> ~/.bashrc
source ~/.bashrc

# 5. Verify models are discovered
openclaw models list
```

## Çıkarım profilleri

OpenClaw, foundation modellerin yanında **bölgesel ve genel çıkarım profillerini** de keşfeder.
Bir profil bilinen bir foundation modele eşlendiğinde,
profil bu modelin yeteneklerini (bağlam penceresi, maksimum token,
reasoning, vision) devralır ve doğru Bedrock istek bölgesi otomatik olarak
eklenir. Bu, bölgeler arası Claude profillerinin manuel
sağlayıcı geçersiz kılmaları olmadan çalıştığı anlamına gelir.

Çıkarım profili kimlikleri `us.anthropic.claude-opus-4-6-v1:0` (bölgesel)
veya `anthropic.claude-opus-4-6-v1:0` (genel) gibi görünür. Destekleyen model zaten
keşif sonuçlarında yer alıyorsa, profil onun tam yetenek kümesini devralır;
aksi halde güvenli varsayılanlar uygulanır.

Ek yapılandırma gerekmez. Keşif etkin olduğu ve IAM
principal `bedrock:ListInferenceProfiles` iznine sahip olduğu sürece profiller,
`openclaw models list` içinde foundation modellerle birlikte görünür.

## Notlar

- Bedrock, AWS hesabınızda/bölgenizde **model erişiminin** etkin olmasını gerektirir.
- Otomatik keşif için `bedrock:ListFoundationModels` ve
  `bedrock:ListInferenceProfiles` izinleri gerekir.
- Otomatik moda güveniyorsanız, desteklenen AWS kimlik doğrulama env işaretleyicilerinden birini
  gateway host üzerinde ayarlayın. Env işaretleyicileri olmadan IMDS/paylaşılan yapılandırma kimlik doğrulamasını tercih ediyorsanız,
  `plugins.entries.amazon-bedrock.config.discovery.enabled: true` ayarlayın.
- OpenClaw kimlik bilgisi kaynağını şu sırayla gösterir: `AWS_BEARER_TOKEN_BEDROCK`,
  ardından `AWS_ACCESS_KEY_ID` + `AWS_SECRET_ACCESS_KEY`, ardından `AWS_PROFILE`, sonra
  varsayılan AWS SDK zinciri.
- Reasoning desteği modele bağlıdır; güncel yetenekler için
  Bedrock model kartını kontrol edin.
- Yönetilen anahtar akışını tercih ediyorsanız, Bedrock'ın önüne OpenAI uyumlu
  bir proxy yerleştirip bunu bunun yerine bir OpenAI sağlayıcısı olarak yapılandırabilirsiniz.

## Guardrails

Tüm Bedrock model çağrılarına [Amazon Bedrock Guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails.html)
uygulamak için
`amazon-bedrock` eklenti yapılandırmasına bir `guardrail` nesnesi ekleyebilirsiniz. Guardrails; içerik filtreleme,
konu reddi, sözcük filtreleri, hassas bilgi filtreleri ve bağlamsal
grounding denetimlerini zorunlu kılmanızı sağlar.

```json5
{
  plugins: {
    entries: {
      "amazon-bedrock": {
        config: {
          guardrail: {
            guardrailIdentifier: "abc123", // guardrail ID or full ARN
            guardrailVersion: "1", // version number or "DRAFT"
            streamProcessingMode: "sync", // optional: "sync" or "async"
            trace: "enabled", // optional: "enabled", "disabled", or "enabled_full"
          },
        },
      },
    },
  },
}
```

- `guardrailIdentifier` (zorunlu), bir guardrail kimliği (ör. `abc123`) veya
  tam bir ARN (ör. `arn:aws:bedrock:us-east-1:123456789012:guardrail/abc123`) kabul eder.
- `guardrailVersion` (zorunlu), hangi yayımlanmış sürümün kullanılacağını belirtir veya
  çalışan taslak için `"DRAFT"` kullanılır.
- `streamProcessingMode` (isteğe bağlı), akış sırasında guardrail değerlendirmesinin
  eşzamanlı (`"sync"`) mı yoksa eşzamansız (`"async"`) mı çalışacağını kontrol eder. Atlanırsa
  Bedrock varsayılan davranışını kullanır.
- `trace` (isteğe bağlı), API yanıtında guardrail iz çıktısını etkinleştirir. Hata ayıklama için
  `"enabled"` veya `"enabled_full"` olarak ayarlayın; üretim için
  atlayın veya `"disabled"` yapın.

Gateway tarafından kullanılan IAM principal, standart çağırma izinlerine ek olarak
`bedrock:ApplyGuardrail` iznine sahip olmalıdır.

## Memory search için embeddings

Bedrock ayrıca
[memory search](/tr/concepts/memory-search) için embedding sağlayıcısı olarak da kullanılabilir. Bu, inference sağlayıcısından ayrı yapılandırılır —
`agents.defaults.memorySearch.provider` değerini `"bedrock"` olarak ayarlayın:

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "bedrock",
        model: "amazon.titan-embed-text-v2:0", // default
      },
    },
  },
}
```

Bedrock embeddings, inference ile aynı AWS SDK kimlik bilgisi zincirini kullanır (instance
rolleri, SSO, erişim anahtarları, paylaşılan yapılandırma ve web identity). API anahtarı
gerekmez. `provider` değeri `"auto"` olduğunda Bedrock, bu
kimlik bilgisi zinciri başarıyla çözülürse otomatik algılanır.

Desteklenen embedding modelleri arasında Amazon Titan Embed (v1, v2), Amazon Nova
Embed, Cohere Embed (v3, v4) ve TwelveLabs Marengo bulunur. Tam model listesi ve boyut seçenekleri için
[Memory configuration reference — Bedrock](/tr/reference/memory-config#bedrock-embedding-config)
bölümüne bakın.
