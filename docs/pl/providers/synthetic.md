---
read_when:
    - Chcesz używać Synthetic jako dostawcy modeli
    - Potrzebujesz konfiguracji klucza API lub bazowego URL-a Synthetic
summary: Używaj zgodnego z Anthropic API Synthetic w OpenClaw
title: Synthetic
x-i18n:
    generated_at: "2026-04-12T23:33:16Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1c4d2c6635482e09acaf603a75c8a85f0782e42a4a68ef6166f423a48d184ffa
    source_path: providers/synthetic.md
    workflow: 15
---

# Synthetic

[Synthetic](https://synthetic.new) udostępnia punkty końcowe zgodne z Anthropic.
OpenClaw rejestruje go jako dostawcę `synthetic` i używa
Anthropic Messages API.

| Właściwość | Wartość                               |
| ---------- | ------------------------------------- |
| Dostawca   | `synthetic`                           |
| Uwierzytelnianie | `SYNTHETIC_API_KEY`             |
| API        | Anthropic Messages                    |
| Bazowy URL | `https://api.synthetic.new/anthropic` |

## Pierwsze kroki

<Steps>
  <Step title="Pobierz klucz API">
    Uzyskaj `SYNTHETIC_API_KEY` ze swojego konta Synthetic lub pozwól,
    aby kreator onboardingu poprosił cię o jego podanie.
  </Step>
  <Step title="Uruchom onboarding">
    ```bash
    openclaw onboard --auth-choice synthetic-api-key
    ```
  </Step>
  <Step title="Sprawdź model domyślny">
    Po onboardingu domyślny model jest ustawiony na:
    ```
    synthetic/hf:MiniMaxAI/MiniMax-M2.5
    ```
  </Step>
</Steps>

<Warning>
Klient Anthropic w OpenClaw automatycznie dodaje `/v1` do bazowego URL-a, więc użyj
`https://api.synthetic.new/anthropic` (nie `/anthropic/v1`). Jeśli Synthetic
zmieni swój bazowy URL, nadpisz `models.providers.synthetic.baseUrl`.
</Warning>

## Przykład konfiguracji

```json5
{
  env: { SYNTHETIC_API_KEY: "sk-..." },
  agents: {
    defaults: {
      model: { primary: "synthetic/hf:MiniMaxAI/MiniMax-M2.5" },
      models: { "synthetic/hf:MiniMaxAI/MiniMax-M2.5": { alias: "MiniMax M2.5" } },
    },
  },
  models: {
    mode: "merge",
    providers: {
      synthetic: {
        baseUrl: "https://api.synthetic.new/anthropic",
        apiKey: "${SYNTHETIC_API_KEY}",
        api: "anthropic-messages",
        models: [
          {
            id: "hf:MiniMaxAI/MiniMax-M2.5",
            name: "MiniMax M2.5",
            reasoning: false,
            input: ["text"],
            cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
            contextWindow: 192000,
            maxTokens: 65536,
          },
        ],
      },
    },
  },
}
```

## Katalog modeli

Wszystkie modele Synthetic używają kosztu `0` (wejście/wyjście/cache).

| Id modelu                                              | Okno kontekstu | Maks. tokenów | Rozumowanie | Wejście       |
| ------------------------------------------------------ | -------------- | ------------- | ----------- | ------------- |
| `hf:MiniMaxAI/MiniMax-M2.5`                            | 192,000        | 65,536        | nie         | tekst         |
| `hf:moonshotai/Kimi-K2-Thinking`                       | 256,000        | 8,192         | tak         | tekst         |
| `hf:zai-org/GLM-4.7`                                   | 198,000        | 128,000       | nie         | tekst         |
| `hf:deepseek-ai/DeepSeek-R1-0528`                      | 128,000        | 8,192         | nie         | tekst         |
| `hf:deepseek-ai/DeepSeek-V3-0324`                      | 128,000        | 8,192         | nie         | tekst         |
| `hf:deepseek-ai/DeepSeek-V3.1`                         | 128,000        | 8,192         | nie         | tekst         |
| `hf:deepseek-ai/DeepSeek-V3.1-Terminus`                | 128,000        | 8,192         | nie         | tekst         |
| `hf:deepseek-ai/DeepSeek-V3.2`                         | 159,000        | 8,192         | nie         | tekst         |
| `hf:meta-llama/Llama-3.3-70B-Instruct`                 | 128,000        | 8,192         | nie         | tekst         |
| `hf:meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | 524,000        | 8,192         | nie         | tekst         |
| `hf:moonshotai/Kimi-K2-Instruct-0905`                  | 256,000        | 8,192         | nie         | tekst         |
| `hf:moonshotai/Kimi-K2.5`                              | 256,000        | 8,192         | tak         | tekst + obraz |
| `hf:openai/gpt-oss-120b`                               | 128,000        | 8,192         | nie         | tekst         |
| `hf:Qwen/Qwen3-235B-A22B-Instruct-2507`                | 256,000        | 8,192         | nie         | tekst         |
| `hf:Qwen/Qwen3-Coder-480B-A35B-Instruct`               | 256,000        | 8,192         | nie         | tekst         |
| `hf:Qwen/Qwen3-VL-235B-A22B-Instruct`                  | 250,000        | 8,192         | nie         | tekst + obraz |
| `hf:zai-org/GLM-4.5`                                   | 128,000        | 128,000       | nie         | tekst         |
| `hf:zai-org/GLM-4.6`                                   | 198,000        | 128,000       | nie         | tekst         |
| `hf:zai-org/GLM-5`                                     | 256,000        | 128,000       | tak         | tekst + obraz |
| `hf:deepseek-ai/DeepSeek-V3`                           | 128,000        | 8,192         | nie         | tekst         |
| `hf:Qwen/Qwen3-235B-A22B-Thinking-2507`                | 256,000        | 8,192         | tak         | tekst         |

<Tip>
Odwołania do modeli mają postać `synthetic/<modelId>`. Użyj
`openclaw models list --provider synthetic`, aby zobaczyć wszystkie modele dostępne na twoim
koncie.
</Tip>

<AccordionGroup>
  <Accordion title="Allowlista modeli">
    Jeśli włączysz allowlistę modeli (`agents.defaults.models`), dodaj każdy
    model Synthetic, którego planujesz używać. Modele nieobecne na allowliście będą ukryte
    przed agentem.
  </Accordion>

  <Accordion title="Nadpisanie bazowego URL-a">
    Jeśli Synthetic zmieni swój punkt końcowy API, nadpisz bazowy URL w konfiguracji:

    ```json5
    {
      models: {
        providers: {
          synthetic: {
            baseUrl: "https://new-api.synthetic.new/anthropic",
          },
        },
      },
    }
    ```

    Pamiętaj, że OpenClaw automatycznie dodaje `/v1`.

  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Dostawcy modeli" href="/pl/concepts/model-providers" icon="layers">
    Zasady dostawców, odwołania do modeli i zachowanie failover.
  </Card>
  <Card title="Dokumentacja konfiguracji" href="/pl/gateway/configuration-reference" icon="gear">
    Pełny schemat konfiguracji, w tym ustawienia dostawców.
  </Card>
  <Card title="Synthetic" href="https://synthetic.new" icon="arrow-up-right-from-square">
    Panel Synthetic i dokumentacja API.
  </Card>
</CardGroup>
