---
read_when:
    - Vous modifiez le runtime d’agent embarqué ou le registre de harnesss d’agent
    - Vous enregistrez un harness d’agent à partir d’un plugin intégré ou de confiance
    - Vous devez comprendre comment le plugin Codex est lié aux fournisseurs de modèles
sidebarTitle: Agent Harness
summary: Surface SDK expérimentale pour les plugins qui remplacent l’exécuteur d’agent embarqué de bas niveau
title: Plugins de harness d’agent
x-i18n:
    generated_at: "2026-04-12T00:18:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: 62b88fd24ce8b600179db27e16e8d764a2cd7a14e5c5df76374c33121aa5e365
    source_path: plugins/sdk-agent-harness.md
    workflow: 15
---

# Plugins de harness d’agent

Un **harness d’agent** est l’exécuteur de bas niveau pour un tour préparé d’un agent OpenClaw. Ce n’est pas un fournisseur de modèles, ni un canal, ni un registre d’outils.

Utilisez cette surface uniquement pour les plugins natifs intégrés ou de confiance. Le contrat reste expérimental, car les types de paramètres reflètent intentionnellement le runner embarqué actuel.

## Quand utiliser un harness

Enregistrez un harness d’agent lorsqu’une famille de modèles possède son propre runtime de session natif et que le transport de fournisseur OpenClaw normal est la mauvaise abstraction.

Exemples :

- un serveur d’agent de codage natif qui gère les threads et la compaction
- une CLI ou un démon local qui doit diffuser des événements natifs de planification/raisonnement/outils
- un runtime de modèle qui a besoin de son propre identifiant de reprise en plus de la transcription de session OpenClaw

N’enregistrez **pas** un harness uniquement pour ajouter une nouvelle API LLM. Pour les API de modèles HTTP ou WebSocket normales, créez un [plugin de fournisseur](/fr/plugins/sdk-provider-plugins).

## Ce que le cœur continue de gérer

Avant qu’un harness soit sélectionné, OpenClaw a déjà résolu :

- le fournisseur et le modèle
- l’état d’authentification du runtime
- le niveau de réflexion et le budget de contexte
- le fichier de transcription/session OpenClaw
- l’espace de travail, le bac à sable et la politique des outils
- les callbacks de réponse du canal et les callbacks de diffusion en continu
- la politique de repli du modèle et de bascule de modèle en direct

Cette séparation est intentionnelle. Un harness exécute une tentative préparée ; il ne choisit pas les fournisseurs, ne remplace pas la distribution par canal et ne change pas silencieusement de modèle.

## Enregistrer un harness

**Importation :** `openclaw/plugin-sdk/agent-harness`

```typescript
import type { AgentHarness } from "openclaw/plugin-sdk/agent-harness";
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

const myHarness: AgentHarness = {
  id: "my-harness",
  label: "My native agent harness",

  supports(ctx) {
    return ctx.provider === "my-provider"
      ? { supported: true, priority: 100 }
      : { supported: false };
  },

  async runAttempt(params) {
    // Start or resume your native thread.
    // Use params.prompt, params.tools, params.images, params.onPartialReply,
    // params.onAgentEvent, and the other prepared attempt fields.
    return await runMyNativeTurn(params);
  },
};

export default definePluginEntry({
  id: "my-native-agent",
  name: "My Native Agent",
  description: "Runs selected models through a native agent daemon.",
  register(api) {
    api.registerAgentHarness(myHarness);
  },
});
```

## Politique de sélection

OpenClaw choisit un harness après la résolution du fournisseur/modèle :

1. `OPENCLAW_AGENT_RUNTIME=<id>` force un harness enregistré avec cet identifiant.
2. `OPENCLAW_AGENT_RUNTIME=pi` force le harness PI intégré.
3. `OPENCLAW_AGENT_RUNTIME=auto` demande aux harness enregistrés s’ils prennent en charge le fournisseur/modèle résolu.
4. Si aucun harness enregistré ne correspond, OpenClaw utilise PI sauf si le repli vers PI est désactivé.

Les échecs d’un harness de plugin forcé apparaissent comme des échecs d’exécution. En mode `auto`, OpenClaw peut revenir à PI lorsque le harness de plugin sélectionné échoue avant qu’un tour ait produit des effets de bord. Définissez `OPENCLAW_AGENT_HARNESS_FALLBACK=none` ou `embeddedHarness.fallback: "none"` pour faire de ce repli un échec définitif à la place.

Le plugin Codex intégré enregistre `codex` comme identifiant de harness. Le cœur traite cela comme un identifiant de harness de plugin ordinaire ; les alias spécifiques à Codex relèvent du plugin ou de la configuration de l’opérateur, pas du sélecteur de runtime partagé.

## Appairage fournisseur plus harness

La plupart des harness devraient aussi enregistrer un fournisseur. Le fournisseur rend visibles au reste d’OpenClaw les références de modèle, l’état d’authentification, les métadonnées du modèle et la sélection `/model`. Le harness revendique ensuite ce fournisseur dans `supports(...)`.

Le plugin Codex intégré suit ce modèle :

- identifiant du fournisseur : `codex`
- références de modèle utilisateur : `codex/gpt-5.4`, `codex/gpt-5.2` ou un autre modèle renvoyé par le serveur d’application Codex
- identifiant du harness : `codex`
- authentification : disponibilité synthétique du fournisseur, parce que le harness Codex gère la connexion/session Codex native
- requête app-server : OpenClaw envoie l’identifiant nu du modèle à Codex et laisse le harness parler au protocole app-server natif

Le plugin Codex est additif. Les références simples `openai/gpt-*` restent des références du fournisseur OpenAI et continuent d’utiliser le chemin normal du fournisseur OpenClaw. Sélectionnez `codex/gpt-*` lorsque vous voulez une authentification gérée par Codex, la découverte des modèles Codex, des threads natifs et l’exécution via l’app-server Codex. `/model` peut basculer parmi les modèles Codex renvoyés par le serveur d’application Codex sans nécessiter d’identifiants du fournisseur OpenAI.

Pour la configuration opérateur, les exemples de préfixes de modèle et les configurations propres à Codex, voir [Harness Codex](/fr/plugins/codex-harness).

OpenClaw exige Codex app-server `0.118.0` ou plus récent. Le plugin Codex vérifie la poignée de main d’initialisation de l’app-server et bloque les serveurs plus anciens ou sans version, afin qu’OpenClaw ne s’exécute que sur la surface de protocole avec laquelle il a été testé.

### Mode harness Codex natif

Le harness `codex` intégré est le mode Codex natif pour les tours d’agent OpenClaw embarqués. Activez d’abord le plugin `codex` intégré et incluez `codex` dans `plugins.allow` si votre configuration utilise une liste d’autorisation restrictive. Il est différent de `openai-codex/*` :

- `openai-codex/*` utilise l’OAuth ChatGPT/Codex via le chemin normal du fournisseur OpenClaw.
- `codex/*` utilise le fournisseur Codex intégré et achemine le tour via Codex app-server.

Lorsque ce mode s’exécute, Codex gère l’identifiant natif du thread, le comportement de reprise, la compaction et l’exécution app-server. OpenClaw continue de gérer le canal de discussion, le miroir de transcription visible, la politique des outils, les approbations, la distribution des médias et la sélection de session. Utilisez `embeddedHarness.runtime: "codex"` avec `embeddedHarness.fallback: "none"` lorsque vous devez prouver que le chemin app-server Codex est utilisé et que le repli vers PI ne masque pas un harness natif défectueux.

## Désactiver le repli vers PI

Par défaut, OpenClaw exécute les agents embarqués avec `agents.defaults.embeddedHarness` défini sur `{ runtime: "auto", fallback: "pi" }`. En mode `auto`, les harness de plugin enregistrés peuvent revendiquer une paire fournisseur/modèle. Si aucun ne correspond, ou si un harness de plugin sélectionné automatiquement échoue avant de produire une sortie, OpenClaw revient à PI.

Définissez `fallback: "none"` lorsque vous devez prouver qu’un harness de plugin est le seul runtime exercé. Cela désactive le repli automatique vers PI ; cela ne bloque pas un `runtime: "pi"` explicite ni `OPENCLAW_AGENT_RUNTIME=pi`.

Pour des exécutions embarquées Codex uniquement :

```json
{
  "agents": {
    "defaults": {
      "model": "codex/gpt-5.4",
      "embeddedHarness": {
        "runtime": "codex",
        "fallback": "none"
      }
    }
  }
}
```

Si vous voulez que n’importe quel harness de plugin enregistré puisse revendiquer les modèles correspondants mais ne voulez jamais qu’OpenClaw revienne silencieusement à PI, conservez `runtime: "auto"` et désactivez le repli :

```json
{
  "agents": {
    "defaults": {
      "embeddedHarness": {
        "runtime": "auto",
        "fallback": "none"
      }
    }
  }
}
```

Les remplacements par agent utilisent la même forme :

```json
{
  "agents": {
    "defaults": {
      "embeddedHarness": {
        "runtime": "auto",
        "fallback": "pi"
      }
    },
    "list": [
      {
        "id": "codex-only",
        "model": "codex/gpt-5.4",
        "embeddedHarness": {
          "runtime": "codex",
          "fallback": "none"
        }
      }
    ]
  }
}
```

`OPENCLAW_AGENT_RUNTIME` remplace toujours le runtime configuré. Utilisez `OPENCLAW_AGENT_HARNESS_FALLBACK=none` pour désactiver le repli vers PI depuis l’environnement.

```bash
OPENCLAW_AGENT_RUNTIME=codex \
OPENCLAW_AGENT_HARNESS_FALLBACK=none \
openclaw gateway run
```

Avec le repli désactivé, une session échoue tôt lorsque le harness demandé n’est pas enregistré, ne prend pas en charge le fournisseur/modèle résolu, ou échoue avant de produire des effets de bord du tour. C’est intentionnel pour les déploiements Codex uniquement et pour les tests en direct qui doivent prouver que le chemin app-server Codex est réellement utilisé.

Ce paramètre contrôle uniquement le harness d’agent embarqué. Il ne désactive pas le routage spécifique au fournisseur pour les images, vidéos, musique, TTS, PDF ou autres modèles.

## Sessions natives et miroir de transcription

Un harness peut conserver un identifiant de session natif, un identifiant de thread ou un jeton de reprise côté démon. Gardez cette liaison explicitement associée à la session OpenClaw, et continuez à refléter dans la transcription OpenClaw la sortie de l’assistant/des outils visible par l’utilisateur.

La transcription OpenClaw reste la couche de compatibilité pour :

- l’historique de session visible dans le canal
- la recherche et l’indexation de transcription
- le retour au harness PI intégré lors d’un tour ultérieur
- le comportement générique de `/new`, `/reset` et de suppression de session

Si votre harness stocke une liaison auxiliaire, implémentez `reset(...)` afin qu’OpenClaw puisse l’effacer lorsque la session OpenClaw propriétaire est réinitialisée.

## Résultats des outils et des médias

Le cœur construit la liste des outils OpenClaw et la transmet à la tentative préparée. Lorsqu’un harness exécute un appel d’outil dynamique, renvoyez le résultat de l’outil via la forme de résultat du harness au lieu d’envoyer vous-même les médias du canal.

Cela maintient les sorties de texte, image, vidéo, musique, TTS, approbation et outils de messagerie sur le même chemin de distribution que les exécutions reposant sur PI.

## Limites actuelles

- Le chemin d’importation public est générique, mais certains alias de type de tentative/résultat portent encore des noms `Pi` pour des raisons de compatibilité.
- L’installation de harness tiers est expérimentale. Préférez les plugins de fournisseur jusqu’à ce que vous ayez besoin d’un runtime de session natif.
- Le changement de harness est pris en charge d’un tour à l’autre. Ne changez pas de harness au milieu d’un tour après le démarrage d’outils natifs, d’approbations, de texte d’assistant ou d’envois de messages.

## Liens associés

- [Vue d’ensemble du SDK](/fr/plugins/sdk-overview)
- [Helpers de runtime](/fr/plugins/sdk-runtime)
- [Plugins de fournisseur](/fr/plugins/sdk-provider-plugins)
- [Harness Codex](/fr/plugins/codex-harness)
- [Fournisseurs de modèles](/fr/concepts/model-providers)
