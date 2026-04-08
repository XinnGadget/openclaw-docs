---
read_when:
    - Vuoi usare modelli aperti in OpenClaw gratuitamente
    - Ti serve la configurazione di NVIDIA_API_KEY
summary: Usa l'API compatibile con OpenAI di NVIDIA in OpenClaw
title: NVIDIA
x-i18n:
    generated_at: "2026-04-08T02:17:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: b00f8cedaf223a33ba9f6a6dd8cf066d88cebeea52d391b871e435026182228a
    source_path: providers/nvidia.md
    workflow: 15
---

# NVIDIA

NVIDIA fornisce un'API compatibile con OpenAI all'indirizzo `https://integrate.api.nvidia.com/v1` per usare gratuitamente modelli aperti. Autenticati con una chiave API da [build.nvidia.com](https://build.nvidia.com/settings/api-keys).

## Configurazione CLI

Esporta la chiave una volta, poi esegui l'onboarding e imposta un modello NVIDIA:

```bash
export NVIDIA_API_KEY="nvapi-..."
openclaw onboard --auth-choice skip
openclaw models set nvidia/nvidia/nemotron-3-super-120b-a12b
```

Se passi ancora `--token`, ricorda che finisce nella cronologia della shell e nell'output di `ps`; quando possibile, preferisci la variabile d'ambiente.

## Snippet di configurazione

```json5
{
  env: { NVIDIA_API_KEY: "nvapi-..." },
  models: {
    providers: {
      nvidia: {
        baseUrl: "https://integrate.api.nvidia.com/v1",
        api: "openai-completions",
      },
    },
  },
  agents: {
    defaults: {
      model: { primary: "nvidia/nvidia/nemotron-3-super-120b-a12b" },
    },
  },
}
```

## ID dei modelli

| Model ref                                  | Nome                         | Contesto | Output massimo |
| ------------------------------------------ | ---------------------------- | -------- | -------------- |
| `nvidia/nvidia/nemotron-3-super-120b-a12b` | NVIDIA Nemotron 3 Super 120B | 262,144  | 8,192          |
| `nvidia/moonshotai/kimi-k2.5`              | Kimi K2.5                    | 262,144  | 8,192          |
| `nvidia/minimaxai/minimax-m2.5`            | Minimax M2.5                 | 196,608  | 8,192          |
| `nvidia/z-ai/glm5`                         | GLM 5                        | 202,752  | 8,192          |

## Note

- Endpoint `/v1` compatibile con OpenAI; usa una chiave API da [build.nvidia.com](https://build.nvidia.com/).
- Il provider si abilita automaticamente quando `NVIDIA_API_KEY` è impostata.
- Il catalogo bundled è statico; nel sorgente i costi sono impostati su `0`.
