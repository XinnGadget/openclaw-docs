---
read_when:
    - Betiklerde veya CI içinde onboarding otomasyonu yapıyorsunuz
    - Belirli sağlayıcılar için etkileşimsiz örneklere ihtiyacınız var
sidebarTitle: CLI automation
summary: OpenClaw CLI için betikli onboarding ve ajan kurulumu
title: CLI Otomasyonu
x-i18n:
    generated_at: "2026-04-06T03:12:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: 878ea3fa9f2a75cff9f1a803ccb8a52a1219102e2970883ad18e3aaec5967fd2
    source_path: start/wizard-cli-automation.md
    workflow: 15
---

# CLI Otomasyonu

`openclaw onboard` otomasyonu için `--non-interactive` kullanın.

<Note>
`--json`, etkileşimsiz modu ima etmez. Betikler için `--non-interactive` (ve `--workspace`) kullanın.
</Note>

## Temel etkileşimsiz örnek

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice apiKey \
  --anthropic-api-key "$ANTHROPIC_API_KEY" \
  --secret-input-mode plaintext \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --install-daemon \
  --daemon-runtime node \
  --skip-skills
```

Makine tarafından okunabilir bir özet için `--json` ekleyin.

Düz metin değerler yerine env destekli başvuruları auth profillerinde saklamak için `--secret-input-mode ref` kullanın.
Env başvuruları ile yapılandırılmış sağlayıcı başvuruları (`file` veya `exec`) arasında etkileşimli seçim onboarding akışında kullanılabilir.

Etkileşimsiz `ref` modunda, sağlayıcı env değişkenleri süreç ortamında ayarlı olmalıdır.
Eşleşen env değişkeni olmadan satır içi anahtar bayrakları geçirmek artık hızlıca hata verir.

Örnek:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice openai-api-key \
  --secret-input-mode ref \
  --accept-risk
```

## Sağlayıcıya özgü örnekler

<AccordionGroup>
  <Accordion title="Anthropic API anahtarı örneği">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice apiKey \
      --anthropic-api-key "$ANTHROPIC_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Gemini örneği">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice gemini-api-key \
      --gemini-api-key "$GEMINI_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Z.AI örneği">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice zai-api-key \
      --zai-api-key "$ZAI_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Vercel AI Gateway örneği">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice ai-gateway-api-key \
      --ai-gateway-api-key "$AI_GATEWAY_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Cloudflare AI Gateway örneği">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice cloudflare-ai-gateway-api-key \
      --cloudflare-ai-gateway-account-id "your-account-id" \
      --cloudflare-ai-gateway-gateway-id "your-gateway-id" \
      --cloudflare-ai-gateway-api-key "$CLOUDFLARE_AI_GATEWAY_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Moonshot örneği">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice moonshot-api-key \
      --moonshot-api-key "$MOONSHOT_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Mistral örneği">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice mistral-api-key \
      --mistral-api-key "$MISTRAL_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Synthetic örneği">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice synthetic-api-key \
      --synthetic-api-key "$SYNTHETIC_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="OpenCode örneği">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice opencode-zen \
      --opencode-zen-api-key "$OPENCODE_API_KEY" \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
    Go kataloğu için `--auth-choice opencode-go --opencode-go-api-key "$OPENCODE_API_KEY"` ile değiştirin.
  </Accordion>
  <Accordion title="Ollama örneği">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice ollama \
      --custom-model-id "qwen3.5:27b" \
      --accept-risk \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```
  </Accordion>
  <Accordion title="Özel sağlayıcı örneği">
    ```bash
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice custom-api-key \
      --custom-base-url "https://llm.example.com/v1" \
      --custom-model-id "foo-large" \
      --custom-api-key "$CUSTOM_API_KEY" \
      --custom-provider-id "my-custom" \
      --custom-compatibility anthropic \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```

    `--custom-api-key` isteğe bağlıdır. Atlanırsa onboarding `CUSTOM_API_KEY` değerini kontrol eder.

    Ref modu varyantı:

    ```bash
    export CUSTOM_API_KEY="your-key"
    openclaw onboard --non-interactive \
      --mode local \
      --auth-choice custom-api-key \
      --custom-base-url "https://llm.example.com/v1" \
      --custom-model-id "foo-large" \
      --secret-input-mode ref \
      --custom-provider-id "my-custom" \
      --custom-compatibility anthropic \
      --gateway-port 18789 \
      --gateway-bind loopback
    ```

    Bu modda onboarding, `apiKey` değerini `{ source: "env", provider: "default", id: "CUSTOM_API_KEY" }` olarak saklar.

  </Accordion>
</AccordionGroup>

Anthropic setup-token artık eski/manuel onboarding yolu olarak yeniden kullanılabilir.
Bunu, Anthropic'in OpenClaw kullanıcılarına OpenClaw
Claude-login yolunun **Extra Usage** gerektirdiğini söylediği beklentisiyle kullanın. Üretim için
Anthropic API anahtarı tercih edin.

## Başka bir ajan ekleme

Kendi çalışma alanı,
oturumları ve auth profilleri olan ayrı bir ajan oluşturmak için `openclaw agents add <name>` kullanın. `--workspace` olmadan çalıştırmak sihirbazı başlatır.

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.4 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

Ayarladıkları:

- `agents.list[].name`
- `agents.list[].workspace`
- `agents.list[].agentDir`

Notlar:

- Varsayılan çalışma alanları `~/.openclaw/workspace-<agentId>` düzenini izler.
- Gelen iletileri yönlendirmek için `bindings` ekleyin (sihirbaz bunu yapabilir).
- Etkileşimsiz bayraklar: `--model`, `--agent-dir`, `--bind`, `--non-interactive`.

## İlgili belgeler

- Onboarding merkezi: [Onboarding (CLI)](/tr/start/wizard)
- Tam başvuru: [CLI Setup Reference](/tr/start/wizard-cli-reference)
- Komut başvurusu: [`openclaw onboard`](/cli/onboard)
