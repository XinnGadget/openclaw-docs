---
read_when:
    - Vous créez un plugin OpenClaw
    - Vous devez fournir un schéma de configuration de plugin ou déboguer des erreurs de validation du plugin
summary: Exigences du manifeste de plugin + schéma JSON (validation stricte de la configuration)
title: Manifeste de plugin
x-i18n:
    generated_at: "2026-04-11T15:16:01Z"
    model: gpt-5.4
    provider: openai
    source_hash: 42d454b560a8f6bf714c5d782f34216be1216d83d0a319d08d7349332c91a9e4
    source_path: plugins/manifest.md
    workflow: 15
---

# Manifeste de plugin (`openclaw.plugin.json`)

Cette page concerne uniquement le **manifeste de plugin natif OpenClaw**.

Pour les dispositions de bundles compatibles, voir [Bundles de plugins](/fr/plugins/bundles).

Les formats de bundle compatibles utilisent des fichiers de manifeste différents :

- Bundle Codex : `.codex-plugin/plugin.json`
- Bundle Claude : `.claude-plugin/plugin.json` ou la disposition par défaut du composant Claude
  sans manifeste
- Bundle Cursor : `.cursor-plugin/plugin.json`

OpenClaw détecte automatiquement ces dispositions de bundle également, mais elles ne sont pas validées
par rapport au schéma `openclaw.plugin.json` décrit ici.

Pour les bundles compatibles, OpenClaw lit actuellement les métadonnées du bundle ainsi que les
racines de compétences déclarées, les racines de commandes Claude, les valeurs par défaut de `settings.json` du bundle Claude,
les valeurs par défaut LSP du bundle Claude, et les packs de hooks pris en charge lorsque la disposition correspond
aux attentes d’exécution d’OpenClaw.

Chaque plugin OpenClaw natif **doit** fournir un fichier `openclaw.plugin.json` dans la
**racine du plugin**. OpenClaw utilise ce manifeste pour valider la configuration
**sans exécuter le code du plugin**. Les manifestes manquants ou invalides sont traités comme des
erreurs de plugin et bloquent la validation de la configuration.

Consultez le guide complet du système de plugins : [Plugins](/fr/tools/plugin).
Pour le modèle de capacités natif et les recommandations actuelles de compatibilité externe :
[Modèle de capacités](/fr/plugins/architecture#public-capability-model).

## À quoi sert ce fichier

`openclaw.plugin.json` contient les métadonnées qu’OpenClaw lit avant de charger le
code de votre plugin.

Utilisez-le pour :

- l’identité du plugin
- la validation de la configuration
- les métadonnées d’authentification et d’intégration qui doivent être disponibles sans démarrer l’exécution du plugin
- les indices d’activation légers que les surfaces du plan de contrôle peuvent inspecter avant le chargement de l’exécution
- les descripteurs de configuration légers que les surfaces de configuration/intégration peuvent inspecter avant le chargement de l’exécution
- les métadonnées d’alias et d’activation automatique qui doivent être résolues avant le chargement de l’exécution du plugin
- les métadonnées abrégées de propriété de famille de modèles qui doivent activer automatiquement le plugin avant le chargement de l’exécution
- les instantanés statiques de propriété de capacités utilisés pour le câblage de compatibilité groupée et la couverture des contrats
- les métadonnées de configuration spécifiques aux canaux qui doivent être fusionnées dans les surfaces de catalogue et de validation sans charger l’exécution
- les indices d’interface pour la configuration

Ne l’utilisez pas pour :

- enregistrer le comportement d’exécution
- déclarer des points d’entrée de code
- les métadonnées d’installation npm

Ces éléments appartiennent au code de votre plugin et à `package.json`.

## Exemple minimal

```json
{
  "id": "voice-call",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

## Exemple complet

```json
{
  "id": "openrouter",
  "name": "OpenRouter",
  "description": "Plugin de fournisseur OpenRouter",
  "version": "1.0.0",
  "providers": ["openrouter"],
  "modelSupport": {
    "modelPrefixes": ["router-"]
  },
  "cliBackends": ["openrouter-cli"],
  "providerAuthEnvVars": {
    "openrouter": ["OPENROUTER_API_KEY"]
  },
  "providerAuthAliases": {
    "openrouter-coding": "openrouter"
  },
  "channelEnvVars": {
    "openrouter-chatops": ["OPENROUTER_CHATOPS_TOKEN"]
  },
  "providerAuthChoices": [
    {
      "provider": "openrouter",
      "method": "api-key",
      "choiceId": "openrouter-api-key",
      "choiceLabel": "Clé API OpenRouter",
      "groupId": "openrouter",
      "groupLabel": "OpenRouter",
      "optionKey": "openrouterApiKey",
      "cliFlag": "--openrouter-api-key",
      "cliOption": "--openrouter-api-key <key>",
      "cliDescription": "Clé API OpenRouter",
      "onboardingScopes": ["text-inference"]
    }
  ],
  "uiHints": {
    "apiKey": {
      "label": "Clé API",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  },
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "apiKey": {
        "type": "string"
      }
    }
  }
}
```

## Référence des champs de niveau supérieur

| Champ                               | Obligatoire | Type                             | Signification                                                                                                                                                                                                 |
| ----------------------------------- | ----------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `id`                                | Oui         | `string`                         | ID canonique du plugin. Il s’agit de l’ID utilisé dans `plugins.entries.<id>`.                                                                                                                               |
| `configSchema`                      | Oui         | `object`                         | Schéma JSON inline pour la configuration de ce plugin.                                                                                                                                                        |
| `enabledByDefault`                  | Non         | `true`                           | Marque un plugin groupé comme activé par défaut. Omettez-le, ou définissez toute valeur autre que `true`, pour laisser le plugin désactivé par défaut.                                                     |
| `legacyPluginIds`                   | Non         | `string[]`                       | IDs hérités qui sont normalisés vers cet ID canonique de plugin.                                                                                                                                             |
| `autoEnableWhenConfiguredProviders` | Non         | `string[]`                       | IDs de fournisseurs qui doivent activer automatiquement ce plugin lorsque l’authentification, la configuration ou les références de modèles les mentionnent.                                                |
| `kind`                              | Non         | `"memory"` \| `"context-engine"` | Déclare un type exclusif de plugin utilisé par `plugins.slots.*`.                                                                                                                                            |
| `channels`                          | Non         | `string[]`                       | IDs de canaux appartenant à ce plugin. Utilisés pour la découverte et la validation de la configuration.                                                                                                     |
| `providers`                         | Non         | `string[]`                       | IDs de fournisseurs appartenant à ce plugin.                                                                                                                                                                  |
| `modelSupport`                      | Non         | `object`                         | Métadonnées abrégées de famille de modèles possédées par le manifeste, utilisées pour charger automatiquement le plugin avant l’exécution.                                                                  |
| `cliBackends`                       | Non         | `string[]`                       | IDs de backends d’inférence CLI appartenant à ce plugin. Utilisés pour l’auto-activation au démarrage à partir de références de configuration explicites.                                                  |
| `commandAliases`                    | Non         | `object[]`                       | Noms de commandes appartenant à ce plugin qui doivent produire une configuration sensible au plugin et des diagnostics CLI avant le chargement de l’exécution.                                               |
| `providerAuthEnvVars`               | Non         | `Record<string, string[]>`       | Métadonnées légères de variables d’environnement d’authentification fournisseur qu’OpenClaw peut inspecter sans charger le code du plugin.                                                                  |
| `providerAuthAliases`               | Non         | `Record<string, string>`         | IDs de fournisseurs qui doivent réutiliser un autre ID de fournisseur pour la recherche d’authentification, par exemple un fournisseur de code qui partage la clé API et les profils d’authentification du fournisseur de base. |
| `channelEnvVars`                    | Non         | `Record<string, string[]>`       | Métadonnées légères de variables d’environnement de canal qu’OpenClaw peut inspecter sans charger le code du plugin. Utilisez-les pour les surfaces de configuration ou d’authentification de canaux pilotées par des variables d’environnement que les assistants génériques de démarrage/configuration doivent voir. |
| `providerAuthChoices`               | Non         | `object[]`                       | Métadonnées légères de choix d’authentification pour les sélecteurs d’intégration, la résolution du fournisseur préféré et le câblage simple des options CLI.                                               |
| `activation`                        | Non         | `object`                         | Indices d’activation légers pour le chargement déclenché par les fournisseurs, commandes, canaux, routes et capacités. Métadonnées uniquement ; l’exécution du plugin reste propriétaire du comportement réel. |
| `setup`                             | Non         | `object`                         | Descripteurs légers de configuration/intégration que les surfaces de découverte et de configuration peuvent inspecter sans charger l’exécution du plugin.                                                    |
| `contracts`                         | Non         | `object`                         | Instantané statique des capacités groupées pour la parole, la transcription en temps réel, la voix en temps réel, la compréhension des médias, la génération d’images, la génération de musique, la génération de vidéo, la récupération web, la recherche web et la propriété des outils. |
| `channelConfigs`                    | Non         | `Record<string, object>`         | Métadonnées de configuration de canal possédées par le manifeste, fusionnées dans les surfaces de découverte et de validation avant le chargement de l’exécution.                                           |
| `skills`                            | Non         | `string[]`                       | Répertoires Skills à charger, relatifs à la racine du plugin.                                                                                                                                                |
| `name`                              | Non         | `string`                         | Nom lisible du plugin.                                                                                                                                                                                        |
| `description`                       | Non         | `string`                         | Résumé court affiché dans les surfaces de plugin.                                                                                                                                                             |
| `version`                           | Non         | `string`                         | Version informative du plugin.                                                                                                                                                                                |
| `uiHints`                           | Non         | `Record<string, object>`         | Libellés d’interface, espaces réservés et indices de sensibilité pour les champs de configuration.                                                                                                           |

## Référence de `providerAuthChoices`

Chaque entrée `providerAuthChoices` décrit un choix d’intégration ou d’authentification.
OpenClaw lit ces informations avant le chargement de l’exécution du fournisseur.

| Champ                 | Obligatoire | Type                                            | Signification                                                                                              |
| --------------------- | ----------- | ----------------------------------------------- | ---------------------------------------------------------------------------------------------------------- |
| `provider`            | Oui         | `string`                                        | ID du fournisseur auquel appartient ce choix.                                                              |
| `method`              | Oui         | `string`                                        | ID de méthode d’authentification vers lequel dispatcher.                                                   |
| `choiceId`            | Oui         | `string`                                        | ID stable de choix d’authentification utilisé par les flux d’intégration et CLI.                           |
| `choiceLabel`         | Non         | `string`                                        | Libellé visible par l’utilisateur. S’il est omis, OpenClaw utilise `choiceId` comme repli.                |
| `choiceHint`          | Non         | `string`                                        | Court texte d’aide pour le sélecteur.                                                                      |
| `assistantPriority`   | Non         | `number`                                        | Les valeurs plus basses sont triées plus tôt dans les sélecteurs interactifs pilotés par l’assistant.     |
| `assistantVisibility` | Non         | `"visible"` \| `"manual-only"`                  | Masque ce choix dans les sélecteurs de l’assistant tout en autorisant sa sélection manuelle via la CLI.   |
| `deprecatedChoiceIds` | Non         | `string[]`                                      | IDs de choix hérités qui doivent rediriger les utilisateurs vers ce choix de remplacement.                 |
| `groupId`             | Non         | `string`                                        | ID de groupe facultatif pour regrouper des choix liés.                                                     |
| `groupLabel`          | Non         | `string`                                        | Libellé visible par l’utilisateur pour ce groupe.                                                          |
| `groupHint`           | Non         | `string`                                        | Court texte d’aide pour le groupe.                                                                         |
| `optionKey`           | Non         | `string`                                        | Clé d’option interne pour les flux d’authentification simples à un seul drapeau.                           |
| `cliFlag`             | Non         | `string`                                        | Nom du drapeau CLI, par exemple `--openrouter-api-key`.                                                    |
| `cliOption`           | Non         | `string`                                        | Forme complète de l’option CLI, par exemple `--openrouter-api-key <key>`.                                  |
| `cliDescription`      | Non         | `string`                                        | Description utilisée dans l’aide CLI.                                                                      |
| `onboardingScopes`    | Non         | `Array<"text-inference" \| "image-generation">` | Sur quelles surfaces d’intégration ce choix doit apparaître. Si omis, la valeur par défaut est `["text-inference"]`. |

## Référence de `commandAliases`

Utilisez `commandAliases` lorsqu’un plugin possède un nom de commande d’exécution que les utilisateurs peuvent
mettre par erreur dans `plugins.allow` ou essayer d’exécuter comme commande CLI racine. OpenClaw
utilise ces métadonnées pour les diagnostics sans importer le code d’exécution du plugin.

```json
{
  "commandAliases": [
    {
      "name": "dreaming",
      "kind": "runtime-slash",
      "cliCommand": "memory"
    }
  ]
}
```

| Champ        | Obligatoire | Type              | Signification                                                              |
| ------------ | ----------- | ----------------- | -------------------------------------------------------------------------- |
| `name`       | Oui         | `string`          | Nom de commande qui appartient à ce plugin.                                |
| `kind`       | Non         | `"runtime-slash"` | Marque l’alias comme une commande slash de chat plutôt qu’une commande CLI racine. |
| `cliCommand` | Non         | `string`          | Commande CLI racine associée à suggérer pour les opérations CLI, si elle existe. |

## Référence de `activation`

Utilisez `activation` lorsque le plugin peut déclarer à faible coût quels événements du plan de contrôle
doivent l’activer plus tard.

Ce bloc contient uniquement des métadonnées. Il n’enregistre pas de comportement d’exécution, et il
ne remplace pas `register(...)`, `setupEntry` ou d’autres points d’entrée d’exécution/plugin.

```json
{
  "activation": {
    "onProviders": ["openai"],
    "onCommands": ["models"],
    "onChannels": ["web"],
    "onRoutes": ["gateway-webhook"],
    "onCapabilities": ["provider", "tool"]
  }
}
```

| Champ            | Obligatoire | Type                                                 | Signification                                                    |
| ---------------- | ----------- | ---------------------------------------------------- | ---------------------------------------------------------------- |
| `onProviders`    | Non         | `string[]`                                           | IDs de fournisseurs qui doivent activer ce plugin lorsqu’ils sont demandés. |
| `onCommands`     | Non         | `string[]`                                           | IDs de commandes qui doivent activer ce plugin.                  |
| `onChannels`     | Non         | `string[]`                                           | IDs de canaux qui doivent activer ce plugin.                     |
| `onRoutes`       | Non         | `string[]`                                           | Types de routes qui doivent activer ce plugin.                   |
| `onCapabilities` | Non         | `Array<"provider" \| "channel" \| "tool" \| "hook">` | Indices généraux de capacités utilisés par la planification d’activation du plan de contrôle. |

## Référence de `setup`

Utilisez `setup` lorsque les surfaces de configuration et d’intégration ont besoin de métadonnées légères appartenant au plugin
avant le chargement de l’exécution.

```json
{
  "setup": {
    "providers": [
      {
        "id": "openai",
        "authMethods": ["api-key"],
        "envVars": ["OPENAI_API_KEY"]
      }
    ],
    "cliBackends": ["openai-cli"],
    "configMigrations": ["legacy-openai-auth"],
    "requiresRuntime": false
  }
}
```

Le champ `cliBackends` de niveau supérieur reste valide et continue de décrire les
backends d’inférence CLI. `setup.cliBackends` est la surface de descripteur spécifique à la configuration pour
les flux du plan de contrôle/de configuration qui doivent rester purement basés sur des métadonnées.

### Référence de `setup.providers`

| Champ         | Obligatoire | Type       | Signification                                                                     |
| ------------- | ----------- | ---------- | --------------------------------------------------------------------------------- |
| `id`          | Oui         | `string`   | ID du fournisseur exposé pendant la configuration ou l’intégration.               |
| `authMethods` | Non         | `string[]` | IDs de méthodes de configuration/authentification que ce fournisseur prend en charge sans charger l’exécution complète. |
| `envVars`     | Non         | `string[]` | Variables d’environnement que les surfaces génériques de configuration/statut peuvent vérifier avant le chargement de l’exécution du plugin. |

### Champs de `setup`

| Champ              | Obligatoire | Type       | Signification                                                              |
| ------------------ | ----------- | ---------- | -------------------------------------------------------------------------- |
| `providers`        | Non         | `object[]` | Descripteurs de configuration de fournisseur exposés pendant la configuration et l’intégration. |
| `cliBackends`      | Non         | `string[]` | IDs de backend disponibles au moment de la configuration sans activation complète de l’exécution. |
| `configMigrations` | Non         | `string[]` | IDs de migration de configuration appartenant à la surface de configuration de ce plugin. |
| `requiresRuntime`  | Non         | `boolean`  | Indique si la configuration nécessite encore l’exécution du plugin après la recherche du descripteur. |

## Référence de `uiHints`

`uiHints` est une map des noms de champs de configuration vers de petits indices de rendu.

```json
{
  "uiHints": {
    "apiKey": {
      "label": "Clé API",
      "help": "Utilisée pour les requêtes OpenRouter",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  }
}
```

Chaque indice de champ peut inclure :

| Champ         | Type       | Signification                          |
| ------------- | ---------- | -------------------------------------- |
| `label`       | `string`   | Libellé du champ visible par l’utilisateur. |
| `help`        | `string`   | Court texte d’aide.                    |
| `tags`        | `string[]` | Étiquettes d’interface facultatives.   |
| `advanced`    | `boolean`  | Marque le champ comme avancé.          |
| `sensitive`   | `boolean`  | Marque le champ comme secret ou sensible. |
| `placeholder` | `string`   | Texte d’espace réservé pour les champs de formulaire. |

## Référence de `contracts`

Utilisez `contracts` uniquement pour les métadonnées statiques de propriété de capacités qu’OpenClaw peut
lire sans importer l’exécution du plugin.

```json
{
  "contracts": {
    "speechProviders": ["openai"],
    "realtimeTranscriptionProviders": ["openai"],
    "realtimeVoiceProviders": ["openai"],
    "mediaUnderstandingProviders": ["openai", "openai-codex"],
    "imageGenerationProviders": ["openai"],
    "videoGenerationProviders": ["qwen"],
    "webFetchProviders": ["firecrawl"],
    "webSearchProviders": ["gemini"],
    "tools": ["firecrawl_search", "firecrawl_scrape"]
  }
}
```

Chaque liste est facultative :

| Champ                            | Type       | Signification                                                 |
| -------------------------------- | ---------- | ------------------------------------------------------------- |
| `speechProviders`                | `string[]` | IDs des fournisseurs de parole appartenant à ce plugin.       |
| `realtimeTranscriptionProviders` | `string[]` | IDs des fournisseurs de transcription en temps réel appartenant à ce plugin. |
| `realtimeVoiceProviders`         | `string[]` | IDs des fournisseurs de voix en temps réel appartenant à ce plugin. |
| `mediaUnderstandingProviders`    | `string[]` | IDs des fournisseurs de compréhension des médias appartenant à ce plugin. |
| `imageGenerationProviders`       | `string[]` | IDs des fournisseurs de génération d’images appartenant à ce plugin. |
| `videoGenerationProviders`       | `string[]` | IDs des fournisseurs de génération de vidéo appartenant à ce plugin. |
| `webFetchProviders`              | `string[]` | IDs des fournisseurs de récupération web appartenant à ce plugin. |
| `webSearchProviders`             | `string[]` | IDs des fournisseurs de recherche web appartenant à ce plugin. |
| `tools`                          | `string[]` | Noms d’outils d’agent appartenant à ce plugin pour les vérifications de contrats groupés. |

## Référence de `channelConfigs`

Utilisez `channelConfigs` lorsqu’un plugin de canal a besoin de métadonnées de configuration légères avant
le chargement de l’exécution.

```json
{
  "channelConfigs": {
    "matrix": {
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "homeserverUrl": { "type": "string" }
        }
      },
      "uiHints": {
        "homeserverUrl": {
          "label": "URL du homeserver",
          "placeholder": "https://matrix.example.com"
        }
      },
      "label": "Matrix",
      "description": "Connexion au homeserver Matrix",
      "preferOver": ["matrix-legacy"]
    }
  }
}
```

Chaque entrée de canal peut inclure :

| Champ         | Type                     | Signification                                                                                |
| ------------- | ------------------------ | -------------------------------------------------------------------------------------------- |
| `schema`      | `object`                 | Schéma JSON pour `channels.<id>`. Obligatoire pour chaque entrée déclarée de configuration de canal. |
| `uiHints`     | `Record<string, object>` | Libellés d’interface, espaces réservés et indices de sensibilité facultatifs pour cette section de configuration de canal. |
| `label`       | `string`                 | Libellé du canal fusionné dans les surfaces de sélecteur et d’inspection lorsque les métadonnées d’exécution ne sont pas prêtes. |
| `description` | `string`                 | Brève description du canal pour les surfaces d’inspection et de catalogue.                  |
| `preferOver`  | `string[]`               | IDs de plugins hérités ou de priorité inférieure que ce canal doit surpasser dans les surfaces de sélection. |

## Référence de `modelSupport`

Utilisez `modelSupport` lorsqu’OpenClaw doit déduire votre plugin fournisseur à partir
d’IDs de modèles abrégés comme `gpt-5.4` ou `claude-sonnet-4.6` avant le chargement de l’exécution du plugin.

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

OpenClaw applique cet ordre de priorité :

- les références explicites `provider/model` utilisent les métadonnées `providers` du manifeste propriétaire
- `modelPatterns` ont priorité sur `modelPrefixes`
- si un plugin non groupé et un plugin groupé correspondent tous deux, le plugin non groupé
  l’emporte
- les ambiguïtés restantes sont ignorées jusqu’à ce que l’utilisateur ou la configuration spécifie un fournisseur

Champs :

| Champ           | Type       | Signification                                                                  |
| --------------- | ---------- | ------------------------------------------------------------------------------ |
| `modelPrefixes` | `string[]` | Préfixes comparés avec `startsWith` aux IDs de modèles abrégés.               |
| `modelPatterns` | `string[]` | Sources regex comparées aux IDs de modèles abrégés après suppression du suffixe de profil. |

Les clés de capacité héritées au niveau supérieur sont obsolètes. Utilisez `openclaw doctor --fix` pour
déplacer `speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`,
`webFetchProviders` et `webSearchProviders` sous `contracts` ; le chargement normal
du manifeste ne traite plus ces champs de niveau supérieur comme de la
propriété de capacités.

## Manifeste versus package.json

Les deux fichiers ont des rôles différents :

| Fichier                | À utiliser pour                                                                                                                     |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json` | La découverte, la validation de la configuration, les métadonnées de choix d’authentification et les indices d’interface qui doivent exister avant l’exécution du code du plugin |
| `package.json`         | Les métadonnées npm, l’installation des dépendances, et le bloc `openclaw` utilisé pour les points d’entrée, le contrôle d’installation, la configuration ou les métadonnées de catalogue |

Si vous ne savez pas où placer une métadonnée, utilisez cette règle :

- si OpenClaw doit la connaître avant de charger le code du plugin, placez-la dans `openclaw.plugin.json`
- si elle concerne le packaging, les fichiers de point d’entrée ou le comportement d’installation npm, placez-la dans `package.json`

### Champs de `package.json` qui affectent la découverte

Certaines métadonnées de plugin avant exécution vivent intentionnellement dans `package.json` sous le bloc
`openclaw` plutôt que dans `openclaw.plugin.json`.

Exemples importants :

| Champ                                                             | Signification                                                                                                                             |
| ----------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | Déclare les points d’entrée de plugins natifs.                                                                                            |
| `openclaw.setupEntry`                                             | Point d’entrée léger réservé à la configuration utilisé pendant l’intégration et le démarrage différé des canaux.                       |
| `openclaw.channel`                                                | Métadonnées légères du catalogue de canaux comme les libellés, les chemins de documentation, les alias et le texte de sélection.       |
| `openclaw.channel.configuredState`                                | Métadonnées légères de vérification de l’état configuré qui peuvent répondre à « une configuration basée uniquement sur l’environnement existe-t-elle déjà ? » sans charger l’exécution complète du canal. |
| `openclaw.channel.persistedAuthState`                             | Métadonnées légères de vérification d’authentification persistée qui peuvent répondre à « quelque chose est-il déjà connecté ? » sans charger l’exécution complète du canal. |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | Indices d’installation/mise à jour pour les plugins groupés et publiés en externe.                                                      |
| `openclaw.install.defaultChoice`                                  | Chemin d’installation préféré lorsque plusieurs sources d’installation sont disponibles.                                                 |
| `openclaw.install.minHostVersion`                                 | Version minimale prise en charge de l’hôte OpenClaw, en utilisant un plancher semver comme `>=2026.3.22`.                              |
| `openclaw.install.allowInvalidConfigRecovery`                     | Autorise un chemin de récupération de réinstallation étroit pour les plugins groupés lorsque la configuration est invalide.            |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | Permet aux surfaces de canal réservées à la configuration de se charger avant le plugin de canal complet pendant le démarrage.         |

`openclaw.install.minHostVersion` est appliqué pendant l’installation et lors du chargement du registre
des manifestes. Les valeurs invalides sont rejetées ; les valeurs valides mais plus récentes ignorent le
plugin sur les hôtes plus anciens.

`openclaw.install.allowInvalidConfigRecovery` est volontairement limité. Il
ne rend pas installables des configurations cassées arbitraires. Aujourd’hui, il permet seulement aux flux d’installation
de récupérer de certains échecs obsolètes de mise à niveau de plugins groupés, comme un
chemin de plugin groupé manquant ou une entrée `channels.<id>` obsolète pour ce même
plugin groupé. Les erreurs de configuration sans rapport bloquent toujours l’installation et redirigent les opérateurs
vers `openclaw doctor --fix`.

`openclaw.channel.persistedAuthState` est une métadonnée de package pour un petit
module de vérification :

```json
{
  "openclaw": {
    "channel": {
      "id": "whatsapp",
      "persistedAuthState": {
        "specifier": "./auth-presence",
        "exportName": "hasAnyWhatsAppAuth"
      }
    }
  }
}
```

Utilisez-le lorsque les flux de configuration, doctor ou d’état configuré ont besoin d’une
vérification légère oui/non de l’authentification avant le chargement du plugin de canal complet. L’export ciblé doit être une petite
fonction qui lit uniquement l’état persisté ; ne le faites pas passer par le barrel complet d’exécution du
canal.

`openclaw.channel.configuredState` suit la même forme pour des vérifications légères de l’état
configuré basées uniquement sur l’environnement :

```json
{
  "openclaw": {
    "channel": {
      "id": "telegram",
      "configuredState": {
        "specifier": "./configured-state",
        "exportName": "hasTelegramConfiguredState"
      }
    }
  }
}
```

Utilisez-le lorsqu’un canal peut répondre à l’état configuré à partir de l’environnement ou d’autres petites
entrées hors exécution. Si la vérification nécessite la résolution complète de la configuration ou la véritable
exécution du canal, conservez cette logique dans le hook `config.hasConfiguredState`
du plugin.

## Exigences du schéma JSON

- **Chaque plugin doit fournir un schéma JSON**, même s’il n’accepte aucune configuration.
- Un schéma vide est acceptable (par exemple, `{ "type": "object", "additionalProperties": false }`).
- Les schémas sont validés au moment de la lecture/écriture de la configuration, pas à l’exécution.

## Comportement de validation

- Les clés inconnues `channels.*` sont des **erreurs**, sauf si l’ID du canal est déclaré par
  un manifeste de plugin.
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny` et `plugins.slots.*`
  doivent référencer des IDs de plugin **détectables**. Les IDs inconnus sont des **erreurs**.
- Si un plugin est installé mais possède un manifeste ou un schéma manquant ou cassé,
  la validation échoue et Doctor signale l’erreur du plugin.
- Si la configuration du plugin existe mais que le plugin est **désactivé**, la configuration est conservée et
  un **avertissement** est affiché dans Doctor + les journaux.

Consultez la [Référence de configuration](/fr/gateway/configuration) pour le schéma complet de `plugins.*`.

## Remarques

- Le manifeste est **obligatoire pour les plugins OpenClaw natifs**, y compris les chargements depuis le système de fichiers local.
- L’exécution charge toujours séparément le module du plugin ; le manifeste sert uniquement à la
  découverte + validation.
- Les manifestes natifs sont analysés avec JSON5, donc les commentaires, virgules finales et
  clés non entre guillemets sont acceptés tant que la valeur finale reste un objet.
- Seuls les champs de manifeste documentés sont lus par le chargeur de manifeste. Évitez d’ajouter
  ici des clés personnalisées de niveau supérieur.
- `providerAuthEnvVars` est le chemin léger de métadonnées pour les sondes d’authentification, la
  validation des marqueurs d’environnement, et des surfaces similaires d’authentification fournisseur qui ne doivent pas démarrer l’exécution du plugin
  simplement pour inspecter des noms de variables d’environnement.
- `providerAuthAliases` permet aux variantes de fournisseurs de réutiliser les variables d’environnement d’authentification,
  les profils d’authentification, l’authentification fondée sur la configuration et le choix d’intégration par clé API d’un autre fournisseur
  sans coder en dur cette relation dans le cœur.
- `channelEnvVars` est le chemin léger de métadonnées pour le repli sur les variables d’environnement du shell, les invites de configuration
  et des surfaces de canaux similaires qui ne doivent pas démarrer l’exécution du plugin
  simplement pour inspecter des noms de variables d’environnement.
- `providerAuthChoices` est le chemin léger de métadonnées pour les sélecteurs de choix d’authentification,
  la résolution de `--auth-choice`, le mappage du fournisseur préféré et l’enregistrement simple des drapeaux CLI
  avant le chargement de l’exécution du fournisseur. Pour les métadonnées d’assistant d’exécution
  qui nécessitent le code du fournisseur, voir
  [Hooks d’exécution du fournisseur](/fr/plugins/architecture#provider-runtime-hooks).
- Les types de plugin exclusifs sont sélectionnés via `plugins.slots.*`.
  - `kind: "memory"` est sélectionné par `plugins.slots.memory`.
  - `kind: "context-engine"` est sélectionné par `plugins.slots.contextEngine`
    (par défaut : `legacy` intégré).
- `channels`, `providers`, `cliBackends` et `skills` peuvent être omis lorsqu’un
  plugin n’en a pas besoin.
- Si votre plugin dépend de modules natifs, documentez les étapes de compilation et toute
  exigence de liste d’autorisation du gestionnaire de paquets (par exemple, pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`).

## Liens connexes

- [Créer des plugins](/fr/plugins/building-plugins) — bien démarrer avec les plugins
- [Architecture des plugins](/fr/plugins/architecture) — architecture interne
- [Vue d’ensemble du SDK](/fr/plugins/sdk-overview) — référence du SDK de plugin
