---
read_when:
    - Sie möchten GLM-Modelle in OpenClaw verwenden
    - Sie benötigen die Modellbenennungskonvention und die Einrichtung
summary: Überblick über die GLM-Modellfamilie und wie sie in OpenClaw verwendet wird
title: GLM-Modelle
x-i18n:
    generated_at: "2026-04-08T06:01:07Z"
    model: gpt-5.4
    provider: openai
    source_hash: 79a55acfa139847b4b85dbc09f1068cbd2febb1e49f984a23ea9e3b43bc910eb
    source_path: providers/glm.md
    workflow: 15
---

# GLM-Modelle

GLM ist eine **Modellfamilie** (kein Unternehmen), die über die Z.AI-Plattform verfügbar ist. In OpenClaw werden GLM-
Modelle über den Provider `zai` und Modell-IDs wie `zai/glm-5` aufgerufen.

## CLI-Einrichtung

```bash
# Allgemeine API-Key-Einrichtung mit automatischer Endpunkterkennung
openclaw onboard --auth-choice zai-api-key

# Coding Plan Global, empfohlen für Coding-Plan-Benutzer
openclaw onboard --auth-choice zai-coding-global

# Coding Plan CN (China-Region), empfohlen für Coding-Plan-Benutzer
openclaw onboard --auth-choice zai-coding-cn

# Allgemeine API
openclaw onboard --auth-choice zai-global

# Allgemeine API CN (China-Region)
openclaw onboard --auth-choice zai-cn
```

## Konfigurationsbeispiel

```json5
{
  env: { ZAI_API_KEY: "sk-..." },
  agents: { defaults: { model: { primary: "zai/glm-5.1" } } },
}
```

Mit `zai-api-key` kann OpenClaw den passenden Z.AI-Endpunkt anhand des Schlüssels erkennen und
automatisch die richtige Basis-URL anwenden. Verwenden Sie die expliziten regionalen Optionen, wenn
Sie eine bestimmte Coding-Plan- oder allgemeine API-Oberfläche erzwingen möchten.

## Aktuelle gebündelte GLM-Modelle

OpenClaw versieht den gebündelten Provider `zai` derzeit mit diesen GLM-Referenzen:

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

## Hinweise

- GLM-Versionen und -Verfügbarkeit können sich ändern; prüfen Sie die Z.AI-Dokumentation auf die neuesten Informationen.
- Die standardmäßig gebündelte Modellreferenz ist `zai/glm-5.1`.
- Einzelheiten zum Provider finden Sie unter [/providers/zai](/de/providers/zai).
