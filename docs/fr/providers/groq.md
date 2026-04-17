---
read_when:
    - Vous souhaitez utiliser Groq avec OpenClaw
    - Vous avez besoin de la variable d’environnement de clé d’API ou du choix d’authentification CLI
summary: Configuration de Groq (authentification + sélection du modèle)
title: Groq
x-i18n:
    generated_at: "2026-04-12T23:30:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 613289efc36fedd002e1ebf9366e0e7119ea1f9e14a1dae773b90ea57100baee
    source_path: providers/groq.md
    workflow: 15
---

# Groq

[Groq](https://groq.com) fournit une inférence ultra-rapide sur des modèles open source
(Llama, Gemma, Mistral, et plus encore) à l’aide d’un matériel LPU personnalisé. OpenClaw se connecte
à Groq via son API compatible OpenAI.

| Property | Value             |
| -------- | ----------------- |
| Provider | `groq`            |
| Auth     | `GROQ_API_KEY`    |
| API      | Compatible OpenAI |

## Prise en main

<Steps>
  <Step title="Obtenir une clé d’API">
    Créez une clé d’API sur [console.groq.com/keys](https://console.groq.com/keys).
  </Step>
  <Step title="Définir la clé d’API">
    ```bash
    export GROQ_API_KEY="gsk_..."
    ```
  </Step>
  <Step title="Définir un modèle par défaut">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "groq/llama-3.3-70b-versatile" },
        },
      },
    }
    ```
  </Step>
</Steps>

### Exemple de fichier de configuration

```json5
{
  env: { GROQ_API_KEY: "gsk_..." },
  agents: {
    defaults: {
      model: { primary: "groq/llama-3.3-70b-versatile" },
    },
  },
}
```

## Modèles disponibles

Le catalogue de modèles de Groq change fréquemment. Exécutez `openclaw models list | grep groq`
pour voir les modèles actuellement disponibles, ou consultez
[console.groq.com/docs/models](https://console.groq.com/docs/models).

| Model                       | Notes                               |
| --------------------------- | ----------------------------------- |
| **Llama 3.3 70B Versatile** | Usage général, grand contexte       |
| **Llama 3.1 8B Instant**    | Rapide, léger                       |
| **Gemma 2 9B**              | Compact, efficace                   |
| **Mixtral 8x7B**            | Architecture MoE, raisonnement solide |

<Tip>
Utilisez `openclaw models list --provider groq` pour obtenir la liste la plus à jour
des modèles disponibles sur votre compte.
</Tip>

## Transcription audio

Groq fournit également une transcription audio rapide basée sur Whisper. Lorsqu’il est configuré comme
fournisseur de compréhension des médias, OpenClaw utilise le modèle `whisper-large-v3-turbo` de Groq
pour transcrire les messages vocaux via la surface partagée `tools.media.audio`.

```json5
{
  tools: {
    media: {
      audio: {
        models: [{ provider: "groq" }],
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Détails de la transcription audio">
    | Property | Value |
    |----------|-------|
    | Shared config path | `tools.media.audio` |
    | Default base URL   | `https://api.groq.com/openai/v1` |
    | Default model      | `whisper-large-v3-turbo` |
    | API endpoint       | `/audio/transcriptions` compatible OpenAI |
  </Accordion>

  <Accordion title="Remarque sur l’environnement">
    Si la Gateway s’exécute comme démon (launchd/systemd), assurez-vous que `GROQ_API_KEY` est
    disponible pour ce processus (par exemple, dans `~/.openclaw/.env` ou via
    `env.shellEnv`).

    <Warning>
    Les clés définies uniquement dans votre shell interactif ne sont pas visibles des
    processus Gateway gérés comme démons. Utilisez `~/.openclaw/.env` ou la configuration `env.shellEnv` pour
    une disponibilité persistante.
    </Warning>

  </Accordion>
</AccordionGroup>

## Connexe

<CardGroup cols={2}>
  <Card title="Model selection" href="/fr/concepts/model-providers" icon="layers">
    Choisir les fournisseurs, les références de modèles et le comportement de basculement.
  </Card>
  <Card title="Configuration reference" href="/fr/gateway/configuration-reference" icon="gear">
    Schéma complet de configuration, y compris les paramètres fournisseur et audio.
  </Card>
  <Card title="Groq Console" href="https://console.groq.com" icon="arrow-up-right-from-square">
    Tableau de bord Groq, documentation API et tarification.
  </Card>
  <Card title="Groq model list" href="https://console.groq.com/docs/models" icon="list">
    Catalogue officiel des modèles Groq.
  </Card>
</CardGroup>
