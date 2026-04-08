---
read_when:
    - OpenClaw'ı yerel bir inferrs sunucusuna karşı çalıştırmak istiyorsunuz
    - Gemma'yı veya başka bir modeli inferrs üzerinden sunuyorsunuz
    - inferrs için tam OpenClaw uyumluluk işaretlerine ihtiyacınız var
summary: OpenClaw'ı inferrs üzerinden çalıştırın (OpenAI uyumlu yerel sunucu)
title: inferrs
x-i18n:
    generated_at: "2026-04-08T02:17:36Z"
    model: gpt-5.4
    provider: openai
    source_hash: d84f660d49a682d0c0878707eebe1bc1e83dd115850687076ea3938b9f9c86c6
    source_path: providers/inferrs.md
    workflow: 15
---

# inferrs

[inferrs](https://github.com/ericcurtin/inferrs), yerel modelleri
OpenAI uyumlu bir `/v1` API'sinin arkasında sunabilir. OpenClaw, `inferrs` ile genel
`openai-completions` yolu üzerinden çalışır.

`inferrs` şu anda özel, self-hosted, OpenAI uyumlu bir
arka uç olarak ele alınmalıdır; özel bir OpenClaw sağlayıcı plugin'i olarak değil.

## Hızlı başlangıç

1. `inferrs`'i bir model ile başlatın.

Örnek:

```bash
inferrs serve gg-hf-gg/gemma-4-E2B-it \
  --host 127.0.0.1 \
  --port 8080 \
  --device metal
```

2. Sunucuya erişilebildiğini doğrulayın.

```bash
curl http://127.0.0.1:8080/health
curl http://127.0.0.1:8080/v1/models
```

3. Açık bir OpenClaw sağlayıcı girdisi ekleyin ve varsayılan modelinizi buna yönlendirin.

## Tam yapılandırma örneği

Bu örnek, yerel bir `inferrs` sunucusunda Gemma 4 kullanır.

```json5
{
  agents: {
    defaults: {
      model: { primary: "inferrs/gg-hf-gg/gemma-4-E2B-it" },
      models: {
        "inferrs/gg-hf-gg/gemma-4-E2B-it": {
          alias: "Gemma 4 (inferrs)",
        },
      },
    },
  },
  models: {
    mode: "merge",
    providers: {
      inferrs: {
        baseUrl: "http://127.0.0.1:8080/v1",
        apiKey: "inferrs-local",
        api: "openai-completions",
        models: [
          {
            id: "gg-hf-gg/gemma-4-E2B-it",
            name: "Gemma 4 E2B (inferrs)",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 131072,
            maxTokens: 4096,
            compat: {
              requiresStringContent: true,
            },
          },
        ],
      },
    },
  },
}
```

## `requiresStringContent` neden önemlidir

Bazı `inferrs` Chat Completions yolları, yapılandırılmış içerik parça dizileri yerine
yalnızca dize biçimindeki `messages[].content` değerini kabul eder.

OpenClaw çalıştırmaları şu tür bir hatayla başarısız olursa:

```text
messages[1].content: invalid type: sequence, expected a string
```

şunu ayarlayın:

```json5
compat: {
  requiresStringContent: true
}
```

OpenClaw, isteği göndermeden önce yalnızca metin içeren içerik parçalarını düz
dizelere indirger.

## Gemma ve tool-schema uyarısı

Bazı güncel `inferrs` + Gemma birleşimleri, küçük doğrudan
`/v1/chat/completions` isteklerini kabul ederken tam OpenClaw agent-runtime
turlarında yine de başarısız olabilir.

Bu olursa önce şunu deneyin:

```json5
compat: {
  requiresStringContent: true,
  supportsTools: false
}
```

Bu, model için OpenClaw'ın araç şeması yüzeyini devre dışı bırakır ve daha katı
yerel arka uçlarda istem yükü baskısını azaltabilir.

Küçük doğrudan istekler hâlâ çalışıyor ama normal OpenClaw agent turları
`inferrs` içinde çökmeye devam ediyorsa, kalan sorun genellikle OpenClaw'ın taşıma
katmanından ziyade yukarı akış model/sunucu davranışıdır.

## El ile smoke test

Yapılandırmadan sonra her iki katmanı da test edin:

```bash
curl http://127.0.0.1:8080/v1/chat/completions \
  -H 'content-type: application/json' \
  -d '{"model":"gg-hf-gg/gemma-4-E2B-it","messages":[{"role":"user","content":"What is 2 + 2?"}],"stream":false}'

openclaw infer model run \
  --model inferrs/gg-hf-gg/gemma-4-E2B-it \
  --prompt "What is 2 + 2? Reply with one short sentence." \
  --json
```

İlk komut çalışıyor ama ikincisi başarısız oluyorsa, aşağıdaki sorun giderme
notlarını kullanın.

## Sorun giderme

- `curl /v1/models` başarısız oluyor: `inferrs` çalışmıyor, erişilemiyor veya
  beklenen ana makine/port'a bağlanmamış.
- `messages[].content ... expected a string`: şunu ayarlayın:
  `compat.requiresStringContent: true`.
- Doğrudan küçük `/v1/chat/completions` çağrıları başarılı oluyor, ancak `openclaw infer model run`
  başarısız oluyor: `compat.supportsTools: false` deneyin.
- OpenClaw artık şema hataları almıyor ama `inferrs` daha büyük
  agent turlarında hâlâ çöküyor: bunu yukarı akış `inferrs` veya model sınırlaması olarak değerlendirin ve
  istem baskısını azaltın ya da yerel arka ucu/modeli değiştirin.

## Proxy tarzı davranış

`inferrs`, yerel bir OpenAI uç noktası olarak değil, proxy tarzı OpenAI uyumlu bir `/v1`
arka uç olarak ele alınır.

- yerel OpenAI'ya özgü istek şekillendirme burada uygulanmaz
- `service_tier`, Responses `store`, prompt-cache ipuçları ve
  OpenAI reasoning-compat istem yükü şekillendirmesi yoktur
- gizli OpenClaw atıf başlıkları (`originator`, `version`, `User-Agent`),
  özel `inferrs` base URL'lerine eklenmez

## Ayrıca bakın

- [Yerel modeller](/tr/gateway/local-models)
- [Gateway sorun giderme](/tr/gateway/troubleshooting#local-openai-compatible-backend-passes-direct-probes-but-agent-runs-fail)
- [Model sağlayıcıları](/tr/concepts/model-providers)
