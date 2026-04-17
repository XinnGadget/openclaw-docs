---
read_when:
    - Vous voulez exécuter OpenClaw avec des modèles cloud ou locaux via Ollama
    - Vous avez besoin d’un guide de configuration et de paramétrage pour Ollama
summary: Exécuter OpenClaw avec Ollama (modèles cloud et locaux)
title: Ollama
x-i18n:
    generated_at: "2026-04-15T14:41:03Z"
    model: gpt-5.4
    provider: openai
    source_hash: 098e083e0fc484bddb5270eb630c55d7832039b462d1710372b6afece5cefcdf
    source_path: providers/ollama.md
    workflow: 15
---

# Ollama

OpenClaw s’intègre à l’API native d’Ollama (`/api/chat`) pour les modèles cloud hébergés et les serveurs Ollama locaux/autohébergés. Vous pouvez utiliser Ollama selon trois modes : `Cloud + Local` via un hôte Ollama accessible, `Cloud only` sur `https://ollama.com`, ou `Local only` via un hôte Ollama accessible.

<Warning>
**Utilisateurs d’Ollama à distance** : n’utilisez pas l’URL compatible OpenAI `/v1` (`http://host:11434/v1`) avec OpenClaw. Cela casse l’appel d’outils et les modèles peuvent produire du JSON d’outil brut sous forme de texte brut. Utilisez plutôt l’URL de l’API native d’Ollama : `baseUrl: "http://host:11434"` (sans `/v1`).
</Warning>

## Premiers pas

Choisissez votre méthode de configuration et votre mode préférés.

<Tabs>
  <Tab title="Intégration guidée (recommandée)">
    **Idéal pour :** le chemin le plus rapide vers une configuration Ollama cloud ou locale fonctionnelle.

    <Steps>
      <Step title="Lancer l’intégration guidée">
        ```bash
        openclaw onboard
        ```

        Sélectionnez **Ollama** dans la liste des fournisseurs.
      </Step>
      <Step title="Choisir votre mode">
        - **Cloud + Local** — hôte Ollama local plus modèles cloud routés via cet hôte
        - **Cloud only** — modèles Ollama hébergés via `https://ollama.com`
        - **Local only** — modèles locaux uniquement
      </Step>
      <Step title="Sélectionner un modèle">
        `Cloud only` demande `OLLAMA_API_KEY` et suggère des valeurs par défaut cloud hébergées. `Cloud + Local` et `Local only` demandent une URL de base Ollama, découvrent les modèles disponibles et téléchargent automatiquement le modèle local sélectionné s’il n’est pas encore disponible. `Cloud + Local` vérifie aussi si cet hôte Ollama est connecté pour l’accès cloud.
      </Step>
      <Step title="Vérifier que le modèle est disponible">
        ```bash
        openclaw models list --provider ollama
        ```
      </Step>
    </Steps>

    ### Mode non interactif

    ```bash
    openclaw onboard --non-interactive \
      --auth-choice ollama \
      --accept-risk
    ```

    Vous pouvez éventuellement indiquer une URL de base ou un modèle personnalisé :

    ```bash
    openclaw onboard --non-interactive \
      --auth-choice ollama \
      --custom-base-url "http://ollama-host:11434" \
      --custom-model-id "qwen3.5:27b" \
      --accept-risk
    ```

  </Tab>

  <Tab title="Configuration manuelle">
    **Idéal pour :** un contrôle complet de la configuration cloud ou locale.

    <Steps>
      <Step title="Choisir cloud ou local">
        - **Cloud + Local** : installez Ollama, connectez-vous avec `ollama signin` et acheminez les requêtes cloud via cet hôte
        - **Cloud only** : utilisez `https://ollama.com` avec une `OLLAMA_API_KEY`
        - **Local only** : installez Ollama depuis [ollama.com/download](https://ollama.com/download)
      </Step>
      <Step title="Télécharger un modèle local (local only)">
        ```bash
        ollama pull gemma4
        # ou
        ollama pull gpt-oss:20b
        # ou
        ollama pull llama3.3
        ```
      </Step>
      <Step title="Activer Ollama pour OpenClaw">
        Pour `Cloud only`, utilisez votre vraie `OLLAMA_API_KEY`. Pour les configurations reposant sur un hôte, n’importe quelle valeur fictive fonctionne :

        ```bash
        # Cloud
        export OLLAMA_API_KEY="your-ollama-api-key"

        # Local-only
        export OLLAMA_API_KEY="ollama-local"

        # Ou configurer dans votre fichier de configuration
        openclaw config set models.providers.ollama.apiKey "OLLAMA_API_KEY"
        ```
      </Step>
      <Step title="Inspecter et définir votre modèle">
        ```bash
        openclaw models list
        openclaw models set ollama/gemma4
        ```

        Ou définissez la valeur par défaut dans la configuration :

        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "ollama/gemma4" },
            },
          },
        }
        ```
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Modèles cloud

<Tabs>
  <Tab title="Cloud + Local">
    `Cloud + Local` utilise un hôte Ollama accessible comme point de contrôle pour les modèles locaux et cloud. Il s’agit du flux hybride recommandé par Ollama.

    Utilisez **Cloud + Local** pendant la configuration. OpenClaw demande l’URL de base Ollama, découvre les modèles locaux sur cet hôte et vérifie si l’hôte est connecté pour l’accès cloud avec `ollama signin`. Lorsque l’hôte est connecté, OpenClaw suggère aussi des valeurs par défaut cloud hébergées comme `kimi-k2.5:cloud`, `minimax-m2.7:cloud` et `glm-5.1:cloud`.

    Si l’hôte n’est pas encore connecté, OpenClaw conserve une configuration locale uniquement jusqu’à ce que vous exécutiez `ollama signin`.

  </Tab>

  <Tab title="Cloud only">
    `Cloud only` s’exécute sur l’API hébergée d’Ollama à l’adresse `https://ollama.com`.

    Utilisez **Cloud only** pendant la configuration. OpenClaw demande `OLLAMA_API_KEY`, définit `baseUrl: "https://ollama.com"` et initialise la liste des modèles cloud hébergés. Ce chemin **n’exige pas** de serveur Ollama local ni `ollama signin`.

  </Tab>

  <Tab title="Local only">
    En mode local uniquement, OpenClaw découvre les modèles à partir de l’instance Ollama configurée. Ce chemin est destiné aux serveurs Ollama locaux ou autohébergés.

    OpenClaw suggère actuellement `gemma4` comme valeur locale par défaut.

  </Tab>
</Tabs>

## Découverte des modèles (fournisseur implicite)

Lorsque vous définissez `OLLAMA_API_KEY` (ou un profil d’authentification) et que vous **ne définissez pas** `models.providers.ollama`, OpenClaw découvre les modèles à partir de l’instance Ollama locale à l’adresse `http://127.0.0.1:11434`.

| Comportement             | Détail                                                                                                                                                              |
| ------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Requête du catalogue     | Interroge `/api/tags`                                                                                                                                               |
| Détection des capacités  | Utilise des recherches `/api/show` au mieux pour lire `contextWindow` et détecter les capacités (y compris la vision)                                             |
| Modèles avec vision      | Les modèles avec une capacité `vision` signalée par `/api/show` sont marqués comme compatibles image (`input: ["text", "image"]`), afin qu’OpenClaw injecte automatiquement les images dans le prompt |
| Détection du raisonnement | Marque `reasoning` avec une heuristique basée sur le nom du modèle (`r1`, `reasoning`, `think`)                                                                   |
| Limites de jetons        | Définit `maxTokens` sur la limite maximale de jetons Ollama par défaut utilisée par OpenClaw                                                                       |
| Coûts                    | Définit tous les coûts à `0`                                                                                                                                         |

Cela évite les entrées de modèle manuelles tout en gardant le catalogue aligné sur l’instance Ollama locale.

```bash
# Voir quels modèles sont disponibles
ollama list
openclaw models list
```

Pour ajouter un nouveau modèle, il suffit de le télécharger avec Ollama :

```bash
ollama pull mistral
```

Le nouveau modèle sera automatiquement découvert et disponible à l’utilisation.

<Note>
Si vous définissez explicitement `models.providers.ollama`, la découverte automatique est ignorée et vous devez définir les modèles manuellement. Voir la section de configuration explicite ci-dessous.
</Note>

## Configuration

<Tabs>
  <Tab title="Basique (découverte implicite)">
    Le chemin le plus simple pour activer le mode local uniquement passe par une variable d’environnement :

    ```bash
    export OLLAMA_API_KEY="ollama-local"
    ```

    <Tip>
    Si `OLLAMA_API_KEY` est défini, vous pouvez omettre `apiKey` dans l’entrée du fournisseur et OpenClaw le renseignera pour les vérifications de disponibilité.
    </Tip>

  </Tab>

  <Tab title="Explicite (modèles manuels)">
    Utilisez une configuration explicite si vous voulez une configuration cloud hébergée, si Ollama s’exécute sur un autre hôte/port, si vous voulez forcer des fenêtres de contexte ou des listes de modèles spécifiques, ou si vous voulez des définitions de modèles entièrement manuelles.

    ```json5
    {
      models: {
        providers: {
          ollama: {
            baseUrl: "https://ollama.com",
            apiKey: "OLLAMA_API_KEY",
            api: "ollama",
            models: [
              {
                id: "kimi-k2.5:cloud",
                name: "kimi-k2.5:cloud",
                reasoning: false,
                input: ["text", "image"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 128000,
                maxTokens: 8192
              }
            ]
          }
        }
      }
    }
    ```

  </Tab>

  <Tab title="URL de base personnalisée">
    Si Ollama s’exécute sur un autre hôte ou port (la configuration explicite désactive la découverte automatique, définissez donc les modèles manuellement) :

    ```json5
    {
      models: {
        providers: {
          ollama: {
            apiKey: "ollama-local",
            baseUrl: "http://ollama-host:11434", // Pas de /v1 - utilisez l’URL de l’API native Ollama
            api: "ollama", // Définissez-la explicitement pour garantir le comportement natif d’appel d’outils
          },
        },
      },
    }
    ```

    <Warning>
    N’ajoutez pas `/v1` à l’URL. Le chemin `/v1` utilise le mode compatible OpenAI, dans lequel l’appel d’outils n’est pas fiable. Utilisez l’URL de base Ollama sans suffixe de chemin.
    </Warning>

  </Tab>
</Tabs>

### Sélection de modèle

Une fois configurés, tous vos modèles Ollama sont disponibles :

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "ollama/gpt-oss:20b",
        fallbacks: ["ollama/llama3.3", "ollama/qwen2.5-coder:32b"],
      },
    },
  },
}
```

## Recherche Web Ollama

OpenClaw prend en charge **Ollama Web Search** comme fournisseur `web_search` intégré.

| Propriété   | Détail                                                                                                            |
| ----------- | ----------------------------------------------------------------------------------------------------------------- |
| Hôte        | Utilise votre hôte Ollama configuré (`models.providers.ollama.baseUrl` lorsqu’il est défini, sinon `http://127.0.0.1:11434`) |
| Authentification | Sans clé                                                                                                    |
| Condition requise | Ollama doit être en cours d’exécution et connecté avec `ollama signin`                                   |

Choisissez **Ollama Web Search** pendant `openclaw onboard` ou `openclaw configure --section web`, ou définissez :

```json5
{
  tools: {
    web: {
      search: {
        provider: "ollama",
      },
    },
  },
}
```

<Note>
Pour tous les détails de configuration et de comportement, voir [Ollama Web Search](/fr/tools/ollama-search).
</Note>

## Configuration avancée

<AccordionGroup>
  <Accordion title="Mode hérité compatible OpenAI">
    <Warning>
    **L’appel d’outils n’est pas fiable en mode compatible OpenAI.** Utilisez ce mode uniquement si vous avez besoin du format OpenAI pour un proxy et que vous ne dépendez pas du comportement natif d’appel d’outils.
    </Warning>

    Si vous devez utiliser à la place le point de terminaison compatible OpenAI (par exemple derrière un proxy qui ne prend en charge que le format OpenAI), définissez explicitement `api: "openai-completions"` :

    ```json5
    {
      models: {
        providers: {
          ollama: {
            baseUrl: "http://ollama-host:11434/v1",
            api: "openai-completions",
            injectNumCtxForOpenAICompat: true, // par défaut : true
            apiKey: "ollama-local",
            models: [...]
          }
        }
      }
    }
    ```

    Ce mode peut ne pas prendre en charge simultanément le streaming et l’appel d’outils. Vous devrez peut-être désactiver le streaming avec `params: { streaming: false }` dans la configuration du modèle.

    Lorsque `api: "openai-completions"` est utilisé avec Ollama, OpenClaw injecte `options.num_ctx` par défaut afin qu’Ollama ne revienne pas silencieusement à une fenêtre de contexte de 4096. Si votre proxy/amont rejette les champs `options` inconnus, désactivez ce comportement :

    ```json5
    {
      models: {
        providers: {
          ollama: {
            baseUrl: "http://ollama-host:11434/v1",
            api: "openai-completions",
            injectNumCtxForOpenAICompat: false,
            apiKey: "ollama-local",
            models: [...]
          }
        }
      }
    }
    ```

  </Accordion>

  <Accordion title="Fenêtres de contexte">
    Pour les modèles découverts automatiquement, OpenClaw utilise la fenêtre de contexte signalée par Ollama lorsqu’elle est disponible ; sinon, il revient à la fenêtre de contexte Ollama par défaut utilisée par OpenClaw.

    Vous pouvez remplacer `contextWindow` et `maxTokens` dans la configuration explicite du fournisseur :

    ```json5
    {
      models: {
        providers: {
          ollama: {
            models: [
              {
                id: "llama3.3",
                contextWindow: 131072,
                maxTokens: 65536,
              }
            ]
          }
        }
      }
    }
    ```

  </Accordion>

  <Accordion title="Modèles de raisonnement">
    OpenClaw considère par défaut que les modèles portant des noms comme `deepseek-r1`, `reasoning` ou `think` sont capables de raisonnement.

    ```bash
    ollama pull deepseek-r1:32b
    ```

    Aucune configuration supplémentaire n’est nécessaire -- OpenClaw les marque automatiquement.

  </Accordion>

  <Accordion title="Coûts des modèles">
    Ollama est gratuit et s’exécute localement, donc tous les coûts des modèles sont définis à 0 $. Cela s’applique aussi bien aux modèles découverts automatiquement qu’aux modèles définis manuellement.
  </Accordion>

  <Accordion title="Embeddings de mémoire">
    Le Plugin Ollama intégré enregistre un fournisseur d’embeddings de mémoire pour la
    [recherche en mémoire](/fr/concepts/memory). Il utilise l’URL de base Ollama
    et la clé API configurées.

    | Property      | Value               |
    | ------------- | ------------------- |
    | Modèle par défaut | `nomic-embed-text`  |
    | Téléchargement automatique     | Oui — le modèle d’embedding est téléchargé automatiquement s’il n’est pas présent localement |

    Pour sélectionner Ollama comme fournisseur d’embeddings pour la recherche en mémoire :

    ```json5
    {
      agents: {
        defaults: {
          memorySearch: { provider: "ollama" },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Configuration du streaming">
    L’intégration Ollama d’OpenClaw utilise par défaut l’**API native d’Ollama** (`/api/chat`), qui prend entièrement en charge simultanément le streaming et l’appel d’outils. Aucune configuration particulière n’est nécessaire.

    <Tip>
    Si vous devez utiliser le point de terminaison compatible OpenAI, consultez la section « Mode hérité compatible OpenAI » ci-dessus. Le streaming et l’appel d’outils peuvent ne pas fonctionner simultanément dans ce mode.
    </Tip>

  </Accordion>
</AccordionGroup>

## Dépannage

<AccordionGroup>
  <Accordion title="Ollama non détecté">
    Assurez-vous qu’Ollama est en cours d’exécution, que vous avez défini `OLLAMA_API_KEY` (ou un profil d’authentification), et que vous **n’avez pas** défini d’entrée `models.providers.ollama` explicite :

    ```bash
    ollama serve
    ```

    Vérifiez que l’API est accessible :

    ```bash
    curl http://localhost:11434/api/tags
    ```

  </Accordion>

  <Accordion title="Aucun modèle disponible">
    Si votre modèle n’apparaît pas dans la liste, téléchargez-le localement ou définissez-le explicitement dans `models.providers.ollama`.

    ```bash
    ollama list  # Voir ce qui est installé
    ollama pull gemma4
    ollama pull gpt-oss:20b
    ollama pull llama3.3     # Ou un autre modèle
    ```

  </Accordion>

  <Accordion title="Connexion refusée">
    Vérifiez qu’Ollama s’exécute sur le bon port :

    ```bash
    # Vérifier si Ollama est en cours d’exécution
    ps aux | grep ollama

    # Ou redémarrer Ollama
    ollama serve
    ```

  </Accordion>
</AccordionGroup>

<Note>
Plus d’aide : [Dépannage](/fr/help/troubleshooting) et [FAQ](/fr/help/faq).
</Note>

## En lien

<CardGroup cols={2}>
  <Card title="Fournisseurs de modèles" href="/fr/concepts/model-providers" icon="layers">
    Vue d’ensemble de tous les fournisseurs, des références de modèles et du comportement de basculement.
  </Card>
  <Card title="Sélection de modèle" href="/fr/concepts/models" icon="brain">
    Comment choisir et configurer les modèles.
  </Card>
  <Card title="Ollama Web Search" href="/fr/tools/ollama-search" icon="magnifying-glass">
    Détails complets de configuration et de comportement pour la recherche web alimentée par Ollama.
  </Card>
  <Card title="Configuration" href="/fr/gateway/configuration" icon="gear">
    Référence complète de configuration.
  </Card>
</CardGroup>
