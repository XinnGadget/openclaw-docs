---
read_when:
    - Vous souhaitez utiliser l’abonnement Claude Max avec des outils compatibles OpenAI
    - Vous souhaitez un serveur API local qui encapsule la CLI Claude Code
    - Vous souhaitez évaluer un accès Anthropic basé sur abonnement par rapport à un accès basé sur clé API
summary: Proxy communautaire pour exposer les identifiants d’abonnement Claude comme point de terminaison compatible OpenAI
title: Proxy API Claude Max
x-i18n:
    generated_at: "2026-04-12T23:29:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: 534bc3d189e68529fb090258eb0d6db6d367eb7e027ad04b1f0be55f6aa7d889
    source_path: providers/claude-max-api-proxy.md
    workflow: 15
---

# Proxy API Claude Max

**claude-max-api-proxy** est un outil communautaire qui expose votre abonnement Claude Max/Pro comme un point de terminaison API compatible OpenAI. Cela vous permet d’utiliser votre abonnement avec n’importe quel outil prenant en charge le format d’API OpenAI.

<Warning>
Cette voie est uniquement une compatibilité technique. Anthropic a déjà bloqué certains usages d’abonnement
en dehors de Claude Code par le passé. Vous devez décider vous-même si vous souhaitez
l’utiliser et vérifier les conditions actuelles d’Anthropic avant de vous y fier.
</Warning>

## Pourquoi utiliser cela ?

| Approche                | Coût                                                | Idéal pour                                  |
| ----------------------- | --------------------------------------------------- | ------------------------------------------- |
| API Anthropic           | Paiement au token (~15 $/M en entrée, 75 $/M en sortie pour Opus) | Applications de production, volume élevé    |
| Abonnement Claude Max   | 200 $/mois fixe                                     | Usage personnel, développement, usage illimité |

Si vous avez un abonnement Claude Max et souhaitez l’utiliser avec des outils compatibles OpenAI, ce proxy peut réduire le coût pour certains workflows. Les clés API restent la voie de politique la plus claire pour un usage en production.

## Comment cela fonctionne

```
Votre application → claude-max-api-proxy → CLI Claude Code → Anthropic (via abonnement)
   (format OpenAI)                 (convertit le format)      (utilise votre connexion)
```

Le proxy :

1. Accepte les requêtes au format OpenAI sur `http://localhost:3456/v1/chat/completions`
2. Les convertit en commandes de la CLI Claude Code
3. Renvoie les réponses au format OpenAI (streaming pris en charge)

## Prise en main

<Steps>
  <Step title="Installer le proxy">
    Nécessite Node.js 20+ et la CLI Claude Code.

    ```bash
    npm install -g claude-max-api-proxy

    # Vérifier que la CLI Claude est authentifiée
    claude --version
    ```

  </Step>
  <Step title="Démarrer le serveur">
    ```bash
    claude-max-api
    # Le serveur s’exécute sur http://localhost:3456
    ```
  </Step>
  <Step title="Tester le proxy">
    ```bash
    # Vérification d’état
    curl http://localhost:3456/health

    # Lister les modèles
    curl http://localhost:3456/v1/models

    # Complétion de chat
    curl http://localhost:3456/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d '{
        "model": "claude-opus-4",
        "messages": [{"role": "user", "content": "Hello!"}]
      }'
    ```

  </Step>
  <Step title="Configurer OpenClaw">
    Pointez OpenClaw vers le proxy comme point de terminaison personnalisé compatible OpenAI :

    ```json5
    {
      env: {
        OPENAI_API_KEY: "not-needed",
        OPENAI_BASE_URL: "http://localhost:3456/v1",
      },
      agents: {
        defaults: {
          model: { primary: "openai/claude-opus-4" },
        },
      },
    }
    ```

  </Step>
</Steps>

## Modèles disponibles

| ID du modèle      | Correspond à      |
| ----------------- | ----------------- |
| `claude-opus-4`   | Claude Opus 4     |
| `claude-sonnet-4` | Claude Sonnet 4   |
| `claude-haiku-4`  | Claude Haiku 4    |

## Avancé

<AccordionGroup>
  <Accordion title="Notes sur la voie proxy compatible OpenAI">
    Cette voie utilise la même route de type proxy compatible OpenAI que les autres backends
    personnalisés `/v1` :

    - La mise en forme des requêtes native OpenAI uniquement ne s’applique pas
    - Pas de `service_tier`, pas de `store` Responses, pas d’indices de cache d’invite, ni de
      mise en forme de charge utile de compatibilité de raisonnement OpenAI
    - Les en-têtes d’attribution OpenClaw cachés (`originator`, `version`, `User-Agent`)
      ne sont pas injectés sur l’URL du proxy

  </Accordion>

  <Accordion title="Démarrage automatique sur macOS avec LaunchAgent">
    Créez un LaunchAgent pour exécuter automatiquement le proxy :

    ```bash
    cat > ~/Library/LaunchAgents/com.claude-max-api.plist << 'EOF'
    <?xml version="1.0" encoding="UTF-8"?>
    <!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
    <plist version="1.0">
    <dict>
      <key>Label</key>
      <string>com.claude-max-api</string>
      <key>RunAtLoad</key>
      <true/>
      <key>KeepAlive</key>
      <true/>
      <key>ProgramArguments</key>
      <array>
        <string>/usr/local/bin/node</string>
        <string>/usr/local/lib/node_modules/claude-max-api-proxy/dist/server/standalone.js</string>
      </array>
      <key>EnvironmentVariables</key>
      <dict>
        <key>PATH</key>
        <string>/usr/local/bin:/opt/homebrew/bin:~/.local/bin:/usr/bin:/bin</string>
      </dict>
    </dict>
    </plist>
    EOF

    launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.claude-max-api.plist
    ```

  </Accordion>
</AccordionGroup>

## Liens

- **npm :** [https://www.npmjs.com/package/claude-max-api-proxy](https://www.npmjs.com/package/claude-max-api-proxy)
- **GitHub :** [https://github.com/atalovesyou/claude-max-api-proxy](https://github.com/atalovesyou/claude-max-api-proxy)
- **Issues :** [https://github.com/atalovesyou/claude-max-api-proxy/issues](https://github.com/atalovesyou/claude-max-api-proxy/issues)

## Remarques

- Il s’agit d’un **outil communautaire**, non officiellement pris en charge par Anthropic ni par OpenClaw
- Nécessite un abonnement Claude Max/Pro actif avec une CLI Claude Code authentifiée
- Le proxy s’exécute localement et n’envoie pas de données à des serveurs tiers
- Les réponses en streaming sont entièrement prises en charge

<Note>
Pour une intégration Anthropic native avec la CLI Claude ou des clés API, voir [Anthropic provider](/fr/providers/anthropic). Pour les abonnements OpenAI/Codex, voir [OpenAI provider](/fr/providers/openai).
</Note>

## Liens associés

<CardGroup cols={2}>
  <Card title="Anthropic provider" href="/fr/providers/anthropic" icon="bolt">
    Intégration OpenClaw native avec la CLI Claude ou des clés API.
  </Card>
  <Card title="OpenAI provider" href="/fr/providers/openai" icon="robot">
    Pour les abonnements OpenAI/Codex.
  </Card>
  <Card title="Model providers" href="/fr/concepts/model-providers" icon="layers">
    Vue d’ensemble de tous les fournisseurs, des références de modèles et du comportement de basculement.
  </Card>
  <Card title="Configuration" href="/fr/gateway/configuration" icon="gear">
    Référence complète de configuration.
  </Card>
</CardGroup>
