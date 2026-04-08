---
read_when:
    - Vuoi usare Z.AI / i modelli GLM in OpenClaw
    - Hai bisogno di una semplice configurazione con ZAI_API_KEY
summary: Usare Z.AI (modelli GLM) con OpenClaw
title: Z.AI
x-i18n:
    generated_at: "2026-04-08T06:01:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: 66cbd9813ee28d202dcae34debab1b0cf9927793acb00743c1c62b48d9e381f9
    source_path: providers/zai.md
    workflow: 15
---

# Z.AI

Z.AI è la piattaforma API per i modelli **GLM**. Fornisce API REST per GLM e usa chiavi API
per l'autenticazione. Crea la tua chiave API nella console di Z.AI. OpenClaw usa il provider `zai`
con una chiave API di Z.AI.

## Configurazione della CLI

```bash
# Configurazione generica della chiave API con rilevamento automatico dell'endpoint
openclaw onboard --auth-choice zai-api-key

# Piano Coding Global, consigliato per gli utenti di Coding Plan
openclaw onboard --auth-choice zai-coding-global

# Piano Coding CN (regione Cina), consigliato per gli utenti di Coding Plan
openclaw onboard --auth-choice zai-coding-cn

# API generale
openclaw onboard --auth-choice zai-global

# API generale CN (regione Cina)
openclaw onboard --auth-choice zai-cn
```

## Frammento di configurazione

```json5
{
  env: { ZAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "zai/glm-5.1" } } },
}
```

`zai-api-key` consente a OpenClaw di rilevare l'endpoint Z.AI corrispondente dalla chiave e
applicare automaticamente l'URL di base corretto. Usa le scelte regionali esplicite quando
vuoi forzare una specifica superficie del Piano Coding o dell'API generale.

## Catalogo GLM bundled

OpenClaw attualmente inizializza il provider `zai` bundled con:

- `glm-5.1`
- `glm-5`
- `glm-5-turbo`
- `glm-5v-turbo`
- `glm-4.7`
- `glm-4.7-flash`
- `glm-4.7-flashx`
- `glm-4.6`
- `glm-4.6v`
- `glm-4.5`
- `glm-4.5-air`
- `glm-4.5-flash`
- `glm-4.5v`

## Note

- I modelli GLM sono disponibili come `zai/<model>` (esempio: `zai/glm-5`).
- Riferimento al modello bundled predefinito: `zai/glm-5.1`
- Gli ID `glm-5*` sconosciuti continuano a essere risolti in inoltro sul percorso del provider bundled
  sintetizzando metadati di proprietà del provider dal modello `glm-4.7` quando l'ID
  corrisponde alla forma attuale della famiglia GLM-5.
- `tool_stream` è abilitato per impostazione predefinita per lo streaming delle chiamate agli strumenti di Z.AI. Imposta
  `agents.defaults.models["zai/<model>"].params.tool_stream` su `false` per disabilitarlo.
- Vedi [/providers/glm](/it/providers/glm) per la panoramica della famiglia di modelli.
- Z.AI usa l'autenticazione Bearer con la tua chiave API.
