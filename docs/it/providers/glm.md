---
read_when:
    - Vuoi usare i modelli GLM in OpenClaw
    - Hai bisogno della convenzione di denominazione dei modelli e della configurazione
summary: Panoramica della famiglia di modelli GLM + come usarla in OpenClaw
title: Modelli GLM
x-i18n:
    generated_at: "2026-04-08T06:00:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 79a55acfa139847b4b85dbc09f1068cbd2febb1e49f984a23ea9e3b43bc910eb
    source_path: providers/glm.md
    workflow: 15
---

# Modelli GLM

GLM è una **famiglia di modelli** (non un'azienda) disponibile tramite la piattaforma Z.AI. In OpenClaw, i modelli GLM
si usano tramite il provider `zai` e ID modello come `zai/glm-5`.

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

## Modelli GLM bundled attuali

OpenClaw attualmente inizializza il provider `zai` bundled con questi riferimenti GLM:

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

- Le versioni e la disponibilità di GLM possono cambiare; controlla la documentazione di Z.AI per le informazioni più aggiornate.
- Il riferimento al modello bundled predefinito è `zai/glm-5.1`.
- Per i dettagli sul provider, vedi [/providers/zai](/it/providers/zai).
