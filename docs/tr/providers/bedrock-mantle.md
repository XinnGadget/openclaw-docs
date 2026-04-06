---
read_when:
    - OpenClaw ile Bedrock Mantle üzerinde barındırılan OSS modellerini kullanmak istiyorsunuz
    - GPT-OSS, Qwen, Kimi veya GLM için Mantle OpenAI uyumlu uç noktaya ihtiyacınız var
summary: OpenClaw ile Amazon Bedrock Mantle (OpenAI uyumlu) modellerini kullanın
title: Amazon Bedrock Mantle
x-i18n:
    generated_at: "2026-04-06T03:10:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4e5b33ede4067fb7de02a046f3e375cbd2af4bf68e7751c8dd687447f1a78c86
    source_path: providers/bedrock-mantle.md
    workflow: 15
---

# Amazon Bedrock Mantle

OpenClaw, Mantle OpenAI uyumlu uç noktaya bağlanan paketlenmiş bir **Amazon Bedrock Mantle** sağlayıcısı içerir. Mantle, Bedrock altyapısıyla desteklenen standart bir
`/v1/chat/completions` yüzeyi üzerinden açık kaynaklı ve
üçüncü taraf modelleri (GPT-OSS, Qwen, Kimi, GLM ve benzerleri) barındırır.

## OpenClaw'ın destekledikleri

- Sağlayıcı: `amazon-bedrock-mantle`
- API: `openai-completions` (OpenAI uyumlu)
- Kimlik doğrulama: açık `AWS_BEARER_TOKEN_BEDROCK` veya IAM kimlik bilgisi zinciriyle bearer token üretimi
- Bölge: `AWS_REGION` veya `AWS_DEFAULT_REGION` (varsayılan: `us-east-1`)

## Otomatik model keşfi

`AWS_BEARER_TOKEN_BEDROCK` ayarlandığında OpenClaw bunu doğrudan kullanır. Aksi halde,
OpenClaw, paylaşılan kimlik bilgisi/yapılandırma profilleri, SSO, web
identity ve instance veya task rollerini içeren AWS varsayılan
kimlik bilgisi zincirinden bir Mantle bearer token üretmeyi dener. Ardından, kullanılabilir Mantle
modellerini bölgenin `/v1/models` uç noktasını sorgulayarak keşfeder. Keşif sonuçları
1 saat boyunca önbelleğe alınır ve IAM'den türetilen bearer token'lar saat başı yenilenir.

Desteklenen bölgeler: `us-east-1`, `us-east-2`, `us-west-2`, `ap-northeast-1`,
`ap-south-1`, `ap-southeast-3`, `eu-central-1`, `eu-west-1`, `eu-west-2`,
`eu-south-1`, `eu-north-1`, `sa-east-1`.

## Onboarding

1. **gateway host** üzerinde bir kimlik doğrulama yolu seçin:

Açık bearer token:

```bash
export AWS_BEARER_TOKEN_BEDROCK="..."
# Optional (defaults to us-east-1):
export AWS_REGION="us-west-2"
```

IAM kimlik bilgileri:

```bash
# Any AWS SDK-compatible auth source works here, for example:
export AWS_PROFILE="default"
export AWS_REGION="us-west-2"
```

2. Modellerin keşfedildiğini doğrulayın:

```bash
openclaw models list
```

Keşfedilen modeller `amazon-bedrock-mantle` sağlayıcısı altında görünür. Varsayılanları geçersiz kılmak istemediğiniz sürece ek
bir yapılandırma gerekmez.

## Elle yapılandırma

Otomatik keşif yerine açık yapılandırmayı tercih ediyorsanız:

```json5
{
  models: {
    providers: {
      "amazon-bedrock-mantle": {
        baseUrl: "https://bedrock-mantle.us-east-1.api.aws/v1",
        api: "openai-completions",
        auth: "api-key",
        apiKey: "env:AWS_BEARER_TOKEN_BEDROCK",
        models: [
          {
            id: "gpt-oss-120b",
            name: "GPT-OSS 120B",
            reasoning: true,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 32000,
            maxTokens: 4096,
          },
        ],
      },
    },
  },
}
```

## Notlar

- `AWS_BEARER_TOKEN_BEDROCK` ayarlı değilse, OpenClaw AWS SDK uyumlu
  IAM kimlik bilgileri üzerinden Mantle bearer token'ı sizin için oluşturabilir.
- Bearer token, standart
  [Amazon Bedrock](/tr/providers/bedrock) sağlayıcısı tarafından kullanılan aynı `AWS_BEARER_TOKEN_BEDROCK` değeridir.
- Reasoning desteği, `thinking`, `reasoner` veya `gpt-oss-120b` gibi desenler içeren model kimliklerinden çıkarılır.
- Mantle uç noktası kullanılamıyorsa veya hiç model döndürmüyorsa, sağlayıcı
  sessizce atlanır.
