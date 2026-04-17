---
read_when:
    - Vous voulez utiliser le harnais app-server Codex intégré
    - Vous avez besoin de références de modèle Codex et d'exemples de configuration
    - Vous voulez désactiver le fallback PI pour les déploiements Codex uniquement
summary: Exécuter les tours d'agent intégrés d'OpenClaw via le harnais app-server Codex intégré
title: Harnais Codex
x-i18n:
    generated_at: "2026-04-11T02:45:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: 60e1dcf4f1a00c63c3ef31d72feac44bce255421c032c58fa4fd67295b3daf23
    source_path: plugins/codex-harness.md
    workflow: 15
---

# Harnais Codex

Le plugin `codex` intégré permet à OpenClaw d'exécuter des tours d'agent intégrés via le
app-server Codex au lieu du harnais PI intégré.

Utilisez-le lorsque vous voulez que Codex prenne en charge la session d'agent de bas niveau : découverte
des modèles, reprise native des fils, compaction native et exécution via app-server.
OpenClaw conserve la responsabilité des chat channels, des fichiers de session, de la sélection des modèles, des outils,
des approbations, de la livraison des médias et du miroir de transcription visible.

Le harnais est désactivé par défaut. Il n'est sélectionné que lorsque le plugin `codex` est
activé et que le modèle résolu est un modèle `codex/*`, ou lorsque vous forcez explicitement
`embeddedHarness.runtime: "codex"` ou `OPENCLAW_AGENT_RUNTIME=codex`.
Si vous ne configurez jamais `codex/*`, les exécutions PI, OpenAI, Anthropic, Gemini, local
et custom-provider existantes conservent leur comportement actuel.

## Choisir le bon préfixe de modèle

OpenClaw possède des routes distinctes pour l'accès de type OpenAI et Codex :

| Référence de modèle   | Chemin d'exécution                            | À utiliser lorsque                                                      |
| --------------------- | --------------------------------------------- | ----------------------------------------------------------------------- |
| `openai/gpt-5.4`      | Fournisseur OpenAI via le plumbing OpenClaw/PI | Vous voulez un accès direct à l'API OpenAI Platform avec `OPENAI_API_KEY`. |
| `openai-codex/gpt-5.4` | Fournisseur OpenAI Codex OAuth via PI        | Vous voulez ChatGPT/Codex OAuth sans le harnais app-server Codex.       |
| `codex/gpt-5.4`       | Fournisseur Codex intégré plus harnais Codex  | Vous voulez l'exécution native app-server Codex pour le tour d'agent intégré. |

Le harnais Codex ne prend en charge que les références de modèle `codex/*`. Les références existantes `openai/*`,
`openai-codex/*`, Anthropic, Gemini, xAI, local et custom provider conservent
leurs chemins normaux.

## Exigences

- OpenClaw avec le plugin `codex` intégré disponible.
- app-server Codex `0.118.0` ou version plus récente.
- Authentification Codex disponible pour le processus app-server.

Le plugin bloque les handshakes app-server anciens ou sans version. Cela maintient
OpenClaw sur la surface de protocole avec laquelle il a été testé.

Pour les tests smoke live et Docker, l'authentification provient généralement de `OPENAI_API_KEY`, plus
des fichiers CLI Codex facultatifs tels que `~/.codex/auth.json` et
`~/.codex/config.toml`. Utilisez les mêmes éléments d'authentification que votre app-server Codex local
utilise.

## Configuration minimale

Utilisez `codex/gpt-5.4`, activez le plugin intégré et forcez le harnais `codex` :

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
  agents: {
    defaults: {
      model: "codex/gpt-5.4",
      embeddedHarness: {
        runtime: "codex",
        fallback: "none",
      },
    },
  },
}
```

Si votre configuration utilise `plugins.allow`, incluez aussi `codex` :

```json5
{
  plugins: {
    allow: ["codex"],
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
}
```

Définir `agents.defaults.model` ou le modèle d'un agent sur `codex/<model>` active également
automatiquement le plugin `codex` intégré. L'entrée de plugin explicite reste
utile dans les configurations partagées, car elle rend l'intention de déploiement évidente.

## Ajouter Codex sans remplacer les autres modèles

Conservez `runtime: "auto"` lorsque vous voulez Codex pour les modèles `codex/*` et PI pour
tout le reste :

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
  agents: {
    defaults: {
      model: {
        primary: "codex/gpt-5.4",
        fallbacks: ["openai/gpt-5.4", "anthropic/claude-opus-4-6"],
      },
      models: {
        "codex/gpt-5.4": { alias: "codex" },
        "codex/gpt-5.4-mini": { alias: "codex-mini" },
        "openai/gpt-5.4": { alias: "gpt" },
        "anthropic/claude-opus-4-6": { alias: "opus" },
      },
      embeddedHarness: {
        runtime: "auto",
        fallback: "pi",
      },
    },
  },
}
```

Avec cette structure :

- `/model codex` ou `/model codex/gpt-5.4` utilise le harnais app-server Codex.
- `/model gpt` ou `/model openai/gpt-5.4` utilise le chemin du fournisseur OpenAI.
- `/model opus` utilise le chemin du fournisseur Anthropic.
- Si un modèle non Codex est sélectionné, PI reste le harnais de compatibilité.

## Déploiements Codex uniquement

Désactivez le fallback PI lorsque vous devez prouver que chaque tour d'agent intégré utilise
le harnais Codex :

```json5
{
  agents: {
    defaults: {
      model: "codex/gpt-5.4",
      embeddedHarness: {
        runtime: "codex",
        fallback: "none",
      },
    },
  },
}
```

Surcharge d'environnement :

```bash
OPENCLAW_AGENT_RUNTIME=codex \
OPENCLAW_AGENT_HARNESS_FALLBACK=none \
openclaw gateway run
```

Avec le fallback désactivé, OpenClaw échoue rapidement si le plugin Codex est désactivé,
si le modèle demandé n'est pas une référence `codex/*`, si le app-server est trop ancien, ou si le
app-server ne peut pas démarrer.

## Codex par agent

Vous pouvez rendre un agent Codex uniquement tandis que l'agent par défaut conserve la
sélection automatique normale :

```json5
{
  agents: {
    defaults: {
      embeddedHarness: {
        runtime: "auto",
        fallback: "pi",
      },
    },
    list: [
      {
        id: "main",
        default: true,
        model: "anthropic/claude-opus-4-6",
      },
      {
        id: "codex",
        name: "Codex",
        model: "codex/gpt-5.4",
        embeddedHarness: {
          runtime: "codex",
          fallback: "none",
        },
      },
    ],
  },
}
```

Utilisez les commandes de session normales pour changer d'agent et de modèle. `/new` crée une nouvelle
session OpenClaw et le harnais Codex crée ou reprend son fil app-server sidecar
selon les besoins. `/reset` efface la liaison de session OpenClaw pour ce fil.

## Découverte des modèles

Par défaut, le plugin Codex interroge le app-server pour connaître les modèles disponibles. Si
la découverte échoue ou expire, il utilise le catalogue de fallback intégré :

- `codex/gpt-5.4`
- `codex/gpt-5.4-mini`
- `codex/gpt-5.2`

Vous pouvez ajuster la découverte sous `plugins.entries.codex.config.discovery` :

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          discovery: {
            enabled: true,
            timeoutMs: 2500,
          },
        },
      },
    },
  },
}
```

Désactivez la découverte lorsque vous voulez que le démarrage évite de sonder Codex et s'en tienne au
catalogue de fallback :

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          discovery: {
            enabled: false,
          },
        },
      },
    },
  },
}
```

## Connexion app-server et politique

Par défaut, le plugin démarre Codex localement avec :

```bash
codex app-server --listen stdio://
```

Vous pouvez conserver cette valeur par défaut et ajuster uniquement la politique native Codex :

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          appServer: {
            approvalPolicy: "on-request",
            sandbox: "workspace-write",
            serviceTier: "priority",
          },
        },
      },
    },
  },
}
```

Pour un app-server déjà en cours d'exécution, utilisez le transport WebSocket :

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          appServer: {
            transport: "websocket",
            url: "ws://127.0.0.1:39175",
            authToken: "${CODEX_APP_SERVER_TOKEN}",
            requestTimeoutMs: 60000,
          },
        },
      },
    },
  },
}
```

Champs `appServer` pris en charge :

| Champ               | Valeur par défaut                           | Signification                                                            |
| ------------------- | ------------------------------------------- | ------------------------------------------------------------------------ |
| `transport`         | `"stdio"`                                   | `"stdio"` lance Codex ; `"websocket"` se connecte à `url`.              |
| `command`           | `"codex"`                                   | Exécutable pour le transport stdio.                                      |
| `args`              | `["app-server", "--listen", "stdio://"]`    | Arguments pour le transport stdio.                                       |
| `url`               | non défini                                  | URL WebSocket du app-server.                                             |
| `authToken`         | non défini                                  | Jeton Bearer pour le transport WebSocket.                                |
| `headers`           | `{}`                                        | En-têtes WebSocket supplémentaires.                                      |
| `requestTimeoutMs`  | `60000`                                     | Délai d'expiration pour les appels du plan de contrôle app-server.       |
| `approvalPolicy`    | `"never"`                                   | Politique d'approbation native Codex envoyée au démarrage/reprise/tour du fil. |
| `sandbox`           | `"workspace-write"`                         | Mode sandbox natif Codex envoyé au démarrage/reprise du fil.             |
| `approvalsReviewer` | `"user"`                                    | Utilisez `"guardian_subagent"` pour laisser le guardian Codex examiner les approbations natives. |
| `serviceTier`       | non défini                                  | Niveau de service Codex facultatif, par exemple `"priority"`.            |

Les anciennes variables d'environnement fonctionnent toujours comme fallbacks pour les tests locaux lorsque
le champ de configuration correspondant n'est pas défini :

- `OPENCLAW_CODEX_APP_SERVER_BIN`
- `OPENCLAW_CODEX_APP_SERVER_ARGS`
- `OPENCLAW_CODEX_APP_SERVER_APPROVAL_POLICY`
- `OPENCLAW_CODEX_APP_SERVER_SANDBOX`
- `OPENCLAW_CODEX_APP_SERVER_GUARDIAN=1`

La configuration est à privilégier pour des déploiements reproductibles.

## Recettes courantes

Codex local avec le transport stdio par défaut :

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
}
```

Validation du harnais Codex uniquement, avec fallback PI désactivé :

```json5
{
  embeddedHarness: {
    fallback: "none",
  },
  plugins: {
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
}
```

Approbations Codex examinées par guardian :

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          appServer: {
            approvalPolicy: "on-request",
            approvalsReviewer: "guardian_subagent",
            sandbox: "workspace-write",
          },
        },
      },
    },
  },
}
```

app-server distant avec en-têtes explicites :

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          appServer: {
            transport: "websocket",
            url: "ws://gateway-host:39175",
            headers: {
              "X-OpenClaw-Agent": "main",
            },
          },
        },
      },
    },
  },
}
```

Le changement de modèle reste contrôlé par OpenClaw. Lorsqu'une session OpenClaw est attachée
à un fil Codex existant, le tour suivant renvoie de nouveau le modèle
`codex/*`, le fournisseur, la politique d'approbation, le sandbox et le niveau de service actuellement sélectionnés à
app-server. Passer de `codex/gpt-5.4` à `codex/gpt-5.2` conserve la
liaison du fil mais demande à Codex de continuer avec le modèle nouvellement sélectionné.

## Commande Codex

Le plugin intégré enregistre `/codex` comme commande slash autorisée. Elle est
générique et fonctionne sur tout channel qui prend en charge les commandes texte OpenClaw.

Formes courantes :

- `/codex status` affiche la connectivité app-server en direct, les modèles, le compte, les limites de débit, les serveurs MCP et les Skills.
- `/codex models` liste les modèles app-server Codex en direct.
- `/codex threads [filter]` liste les fils Codex récents.
- `/codex resume <thread-id>` attache la session OpenClaw actuelle à un fil Codex existant.
- `/codex compact` demande à app-server Codex de compacter le fil attaché.
- `/codex review` démarre la révision native Codex pour le fil attaché.
- `/codex account` affiche l'état du compte et des limites de débit.
- `/codex mcp` liste l'état des serveurs MCP app-server Codex.
- `/codex skills` liste les Skills app-server Codex.

`/codex resume` écrit le même fichier de liaison sidecar que le harnais utilise pour
les tours normaux. Au message suivant, OpenClaw reprend ce fil Codex, transmet le
modèle OpenClaw `codex/*` actuellement sélectionné à app-server et conserve l'historique
étendu activé.

La surface de commande exige Codex app-server `0.118.0` ou une version plus récente. Les méthodes de
contrôle individuelles sont signalées comme `unsupported by this Codex app-server` si un
app-server futur ou personnalisé n'expose pas cette méthode JSON-RPC.

## Outils, médias et compaction

Le harnais Codex modifie uniquement l'exécuteur d'agent intégré de bas niveau.

OpenClaw continue de construire la liste des outils et de recevoir les résultats d'outils dynamiques depuis le
harnais. Le texte, les images, la vidéo, la musique, la synthèse vocale, les approbations et la sortie des outils de messagerie
continuent de passer par le chemin de livraison normal d'OpenClaw.

Lorsque le modèle sélectionné utilise le harnais Codex, la compaction native du fil est
déléguée à app-server Codex. OpenClaw conserve un miroir de transcription pour l'historique du channel,
la recherche, `/new`, `/reset` et les futurs changements de modèle ou de harnais. Le
miroir inclut l'invite utilisateur, le texte final de l'assistant et des enregistrements légers de raisonnement ou de plan Codex lorsque le
app-server les émet.

La génération de médias ne nécessite pas PI. L'image, la vidéo, la musique, le PDF, la synthèse vocale et la
compréhension des médias continuent d'utiliser les paramètres provider/model correspondants tels que
`agents.defaults.imageGenerationModel`, `videoGenerationModel`, `pdfModel` et
`messages.tts`.

## Dépannage

**Codex n'apparaît pas dans `/model` :** activez `plugins.entries.codex.enabled`,
définissez une référence de modèle `codex/*`, ou vérifiez si `plugins.allow` exclut `codex`.

**OpenClaw bascule vers PI :** définissez `embeddedHarness.fallback: "none"` ou
`OPENCLAW_AGENT_HARNESS_FALLBACK=none` pendant les tests.

**Le app-server est rejeté :** mettez à niveau Codex afin que le handshake app-server
signale la version `0.118.0` ou une version plus récente.

**La découverte des modèles est lente :** réduisez `plugins.entries.codex.config.discovery.timeoutMs`
ou désactivez la découverte.

**Le transport WebSocket échoue immédiatement :** vérifiez `appServer.url`, `authToken`,
et que le app-server distant parle la même version du protocole app-server Codex.

**Un modèle non Codex utilise PI :** c'est attendu. Le harnais Codex ne prend en charge
que les références de modèle `codex/*`.

## Voir aussi

- [Plugins de harnais d'agent](/fr/plugins/sdk-agent-harness)
- [Fournisseurs de modèles](/fr/concepts/model-providers)
- [Référence de configuration](/fr/gateway/configuration-reference)
- [Tests](/fr/help/testing#live-codex-app-server-harness-smoke)
