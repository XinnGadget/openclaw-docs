---
read_when:
    - Chcesz używać Together AI z OpenClaw
    - Potrzebujesz zmiennej środowiskowej klucza API lub opcji uwierzytelniania w CLI
summary: Konfiguracja Together AI (uwierzytelnianie + wybór modelu)
title: Together AI
x-i18n:
    generated_at: "2026-04-06T03:11:57Z"
    model: gpt-5.4
    provider: openai
    source_hash: b68fdc15bfcac8d59e3e0c06a39162abd48d9d41a9a64a0ac622cd8e3f80a595
    source_path: providers/together.md
    workflow: 15
---

# Together AI

[Together AI](https://together.ai) zapewnia dostęp do czołowych modeli open source, w tym Llama, DeepSeek, Kimi i innych, przez ujednolicone API.

- Dostawca: `together`
- Uwierzytelnianie: `TOGETHER_API_KEY`
- API: zgodne z OpenAI
- Bazowy URL: `https://api.together.xyz/v1`

## Szybki start

1. Ustaw klucz API (zalecane: zapisz go dla Gateway):

```bash
openclaw onboard --auth-choice together-api-key
```

2. Ustaw model domyślny:

```json5
{
  agents: {
    defaults: {
      model: { primary: "together/moonshotai/Kimi-K2.5" },
    },
  },
}
```

## Przykład nieinteraktywny

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice together-api-key \
  --together-api-key "$TOGETHER_API_KEY"
```

Spowoduje to ustawienie `together/moonshotai/Kimi-K2.5` jako modelu domyślnego.

## Uwaga dotycząca środowiska

Jeśli Gateway działa jako demon (`launchd/systemd`), upewnij się, że `TOGETHER_API_KEY`
jest dostępne dla tego procesu (na przykład w `~/.openclaw/.env` albo przez
`env.shellEnv`).

## Wbudowany katalog

OpenClaw obecnie dostarcza ten wbudowany katalog Together:

| Model ref                                                    | Nazwa                                   | Wejście       | Kontekst    | Uwagi                            |
| ------------------------------------------------------------ | -------------------------------------- | ----------- | ---------- | -------------------------------- |
| `together/moonshotai/Kimi-K2.5`                              | Kimi K2.5                              | tekst, obraz | 262,144    | Model domyślny; reasoning włączony |
| `together/zai-org/GLM-4.7`                                   | GLM 4.7 Fp8                            | tekst        | 202,752    | Model tekstowy ogólnego przeznaczenia       |
| `together/meta-llama/Llama-3.3-70B-Instruct-Turbo`           | Llama 3.3 70B Instruct Turbo           | tekst        | 131,072    | Szybki model instrukcyjny           |
| `together/meta-llama/Llama-4-Scout-17B-16E-Instruct`         | Llama 4 Scout 17B 16E Instruct         | tekst, obraz | 10,000,000 | Multimodalny                       |
| `together/meta-llama/Llama-4-Maverick-17B-128E-Instruct-FP8` | Llama 4 Maverick 17B 128E Instruct FP8 | tekst, obraz | 20,000,000 | Multimodalny                       |
| `together/deepseek-ai/DeepSeek-V3.1`                         | DeepSeek V3.1                          | tekst        | 131,072    | Ogólny model tekstowy               |
| `together/deepseek-ai/DeepSeek-R1`                           | DeepSeek R1                            | tekst        | 131,072    | Model reasoning                  |
| `together/moonshotai/Kimi-K2-Instruct-0905`                  | Kimi K2-Instruct 0905                  | tekst        | 262,144    | Dodatkowy model tekstowy Kimi        |

Preset onboardingu ustawia `together/moonshotai/Kimi-K2.5` jako model domyślny.

## Generowanie wideo

Wbudowany plugin `together` rejestruje także generowanie wideo przez
współdzielone narzędzie `video_generate`.

- Domyślny model wideo: `together/Wan-AI/Wan2.2-T2V-A14B`
- Tryby: text-to-video oraz przepływy z pojedynczym obrazem referencyjnym
- Obsługuje `aspectRatio` i `resolution`

Aby używać Together jako domyślnego dostawcy wideo:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "together/Wan-AI/Wan2.2-T2V-A14B",
      },
    },
  },
}
```

Zobacz [Generowanie wideo](/tools/video-generation), aby poznać współdzielone
parametry narzędzia, wybór dostawcy i zachowanie failover.
