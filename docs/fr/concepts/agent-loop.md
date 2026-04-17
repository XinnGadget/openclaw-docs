---
read_when:
    - Vous avez besoin d’une présentation détaillée exacte de la boucle de l’agent ou des événements du cycle de vie
summary: Cycle de vie de la boucle de l’agent, flux et sémantique d’attente
title: Boucle de l’agent
x-i18n:
    generated_at: "2026-04-12T23:28:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3c2986708b444055340e0c91b8fce7d32225fcccf3d197b797665fd36b1991a5
    source_path: concepts/agent-loop.md
    workflow: 15
---

# Boucle de l’agent (OpenClaw)

Une boucle agentique correspond à l’exécution complète « réelle » d’un agent : ingestion → assemblage du contexte → inférence du modèle →
exécution des outils → réponses en flux → persistance. Il s’agit du chemin d’autorité qui transforme un message
en actions et en une réponse finale, tout en gardant l’état de la session cohérent.

Dans OpenClaw, une boucle est une exécution unique, sérialisée par session, qui émet des événements de cycle de vie et de flux
pendant que le modèle réfléchit, appelle des outils et diffuse sa sortie en flux. Ce document explique comment cette boucle authentique est
câblée de bout en bout.

## Points d’entrée

- RPC Gateway : `agent` et `agent.wait`.
- CLI : commande `agent`.

## Fonctionnement (vue d’ensemble)

1. Le RPC `agent` valide les paramètres, résout la session (`sessionKey`/`sessionId`), persiste les métadonnées de session et renvoie `{ runId, acceptedAt }` immédiatement.
2. `agentCommand` exécute l’agent :
   - résout le modèle ainsi que les valeurs par défaut de thinking/verbose/trace
   - charge le snapshot des Skills
   - appelle `runEmbeddedPiAgent` (runtime pi-agent-core)
   - émet **lifecycle end/error** si la boucle embarquée n’en émet pas
3. `runEmbeddedPiAgent` :
   - sérialise les exécutions via des files d’attente par session et globale
   - résout le profil de modèle et d’authentification, puis construit la session Pi
   - s’abonne aux événements pi et diffuse les deltas assistant/outils
   - applique le délai d’expiration -> abandonne l’exécution si dépassé
   - renvoie les payloads et les métadonnées d’usage
4. `subscribeEmbeddedPiSession` fait le pont entre les événements pi-agent-core et le flux `agent` d’OpenClaw :
   - événements d’outil => `stream: "tool"`
   - deltas de l’assistant => `stream: "assistant"`
   - événements de cycle de vie => `stream: "lifecycle"` (`phase: "start" | "end" | "error"`)
5. `agent.wait` utilise `waitForAgentRun` :
   - attend **lifecycle end/error** pour `runId`
   - renvoie `{ status: ok|error|timeout, startedAt, endedAt, error? }`

## Mise en file d’attente + concurrence

- Les exécutions sont sérialisées par clé de session (voie de session) et éventuellement via une voie globale.
- Cela évite les courses entre outils/sessions et maintient l’historique de session cohérent.
- Les canaux de messagerie peuvent choisir des modes de file d’attente (collect/steer/followup) qui alimentent ce système de voies.
  Voir [Command Queue](/fr/concepts/queue).

## Préparation de la session + de l’espace de travail

- L’espace de travail est résolu et créé ; les exécutions en sandbox peuvent rediriger vers une racine d’espace de travail sandboxée.
- Les Skills sont chargées (ou réutilisées depuis un snapshot) et injectées dans l’environnement et le prompt.
- Les fichiers bootstrap/contexte sont résolus et injectés dans le rapport du prompt système.
- Un verrou d’écriture de session est acquis ; `SessionManager` est ouvert et préparé avant le streaming.

## Assemblage du prompt + prompt système

- Le prompt système est construit à partir du prompt de base d’OpenClaw, du prompt des Skills, du contexte bootstrap et des surcharges par exécution.
- Les limites spécifiques au modèle et les tokens réservés à Compaction sont appliqués.
- Voir [System prompt](/fr/concepts/system-prompt) pour savoir ce que voit le modèle.

## Points de hook (où vous pouvez intercepter)

OpenClaw dispose de deux systèmes de hooks :

- **Hooks internes** (hooks Gateway) : scripts pilotés par événements pour les commandes et les événements de cycle de vie.
- **Hooks de Plugin** : points d’extension à l’intérieur du cycle de vie de l’agent/de l’outil et du pipeline Gateway.

### Hooks internes (hooks Gateway)

- **`agent:bootstrap`** : s’exécute pendant la construction des fichiers bootstrap avant la finalisation du prompt système.
  Utilisez-le pour ajouter/supprimer des fichiers de contexte bootstrap.
- **Hooks de commande** : `/new`, `/reset`, `/stop` et autres événements de commande (voir le document Hooks).

Voir [Hooks](/fr/automation/hooks) pour la configuration et des exemples.

### Hooks de Plugin (cycle de vie agent + gateway)

Ils s’exécutent à l’intérieur de la boucle de l’agent ou du pipeline Gateway :

- **`before_model_resolve`** : s’exécute avant la session (sans `messages`) pour surcharger de façon déterministe le fournisseur/modèle avant la résolution du modèle.
- **`before_prompt_build`** : s’exécute après le chargement de la session (avec `messages`) pour injecter `prependContext`, `systemPrompt`, `prependSystemContext` ou `appendSystemContext` avant l’envoi du prompt. Utilisez `prependContext` pour du texte dynamique par tour et les champs de contexte système pour des consignes stables qui doivent rester dans l’espace du prompt système.
- **`before_agent_start`** : hook de compatibilité hérité qui peut s’exécuter dans l’une ou l’autre phase ; préférez les hooks explicites ci-dessus.
- **`before_agent_reply`** : s’exécute après les actions inline et avant l’appel au LLM, permettant à un Plugin de prendre en charge le tour et de renvoyer une réponse synthétique ou de rendre le tour complètement silencieux.
- **`agent_end`** : inspecte la liste finale des messages et les métadonnées d’exécution après l’achèvement.
- **`before_compaction` / `after_compaction`** : observe ou annote les cycles de Compaction.
- **`before_tool_call` / `after_tool_call`** : intercepte les paramètres/résultats des outils.
- **`before_install`** : inspecte les résultats d’analyse intégrés et peut bloquer les installations de Skills ou de Plugins.
- **`tool_result_persist`** : transforme de façon synchrone les résultats d’outil avant leur écriture dans le transcript de session.
- **`message_received` / `message_sending` / `message_sent`** : hooks de messages entrants + sortants.
- **`session_start` / `session_end`** : bornes du cycle de vie de la session.
- **`gateway_start` / `gateway_stop`** : événements du cycle de vie Gateway.

Règles de décision des hooks pour les garde-fous sortants/outils :

- `before_tool_call`: `{ block: true }` est terminal et arrête les gestionnaires de priorité inférieure.
- `before_tool_call`: `{ block: false }` n’a aucun effet et n’efface pas un blocage antérieur.
- `before_install`: `{ block: true }` est terminal et arrête les gestionnaires de priorité inférieure.
- `before_install`: `{ block: false }` n’a aucun effet et n’efface pas un blocage antérieur.
- `message_sending`: `{ cancel: true }` est terminal et arrête les gestionnaires de priorité inférieure.
- `message_sending`: `{ cancel: false }` n’a aucun effet et n’efface pas une annulation antérieure.

Voir [Plugin hooks](/fr/plugins/architecture#provider-runtime-hooks) pour l’API des hooks et les détails d’enregistrement.

## Streaming + réponses partielles

- Les deltas de l’assistant sont diffusés depuis pi-agent-core et émis comme événements `assistant`.
- Le streaming par bloc peut émettre des réponses partielles soit sur `text_end`, soit sur `message_end`.
- Le streaming du raisonnement peut être émis comme flux séparé ou comme réponses par bloc.
- Voir [Streaming](/fr/concepts/streaming) pour le découpage en morceaux et le comportement des réponses par bloc.

## Exécution des outils + outils de messagerie

- Les événements de début/mise à jour/fin d’outil sont émis sur le flux `tool`.
- Les résultats d’outil sont assainis pour la taille et les payloads d’image avant journalisation/émission.
- Les envois d’outils de messagerie sont suivis pour supprimer les confirmations d’assistant en double.

## Mise en forme de la réponse + suppression

- Les payloads finaux sont assemblés à partir de :
  - texte de l’assistant (et raisonnement facultatif)
  - résumés d’outils inline (quand verbose + autorisé)
  - texte d’erreur de l’assistant lorsque le modèle renvoie une erreur
- Le jeton silencieux exact `NO_REPLY` / `no_reply` est filtré des
  payloads sortants.
- Les doublons des outils de messagerie sont supprimés de la liste finale des payloads.
- S’il ne reste aucun payload affichable et qu’un outil a renvoyé une erreur, une réponse de secours d’erreur d’outil est émise
  (sauf si un outil de messagerie a déjà envoyé une réponse visible par l’utilisateur).

## Compaction + nouvelles tentatives

- La Compaction automatique émet des événements de flux `compaction` et peut déclencher une nouvelle tentative.
- Lors d’une nouvelle tentative, les buffers en mémoire et les résumés d’outils sont réinitialisés pour éviter les sorties en double.
- Voir [Compaction](/fr/concepts/compaction) pour le pipeline de Compaction.

## Flux d’événements (aujourd’hui)

- `lifecycle` : émis par `subscribeEmbeddedPiSession` (et en secours par `agentCommand`)
- `assistant` : deltas diffusés en flux depuis pi-agent-core
- `tool` : événements d’outil diffusés en flux depuis pi-agent-core

## Gestion des canaux de chat

- Les deltas de l’assistant sont mis en tampon dans des messages `delta` de chat.
- Un `final` de chat est émis à **lifecycle end/error**.

## Délais d’expiration

- Valeur par défaut de `agent.wait` : 30 s (attente uniquement). Le paramètre `timeoutMs` remplace cette valeur.
- Runtime de l’agent : `agents.defaults.timeoutSeconds` vaut par défaut 172800 s (48 heures) ; appliqué dans le minuteur d’abandon de `runEmbeddedPiAgent`.
- Délai d’inactivité du LLM : `agents.defaults.llm.idleTimeoutSeconds` abandonne une requête de modèle si aucun morceau de réponse n’arrive avant la fenêtre d’inactivité. Définissez-le explicitement pour les modèles locaux lents ou les fournisseurs de raisonnement/d’appel d’outils ; définissez-le à 0 pour le désactiver. S’il n’est pas défini, OpenClaw utilise `agents.defaults.timeoutSeconds` lorsqu’il est configuré, sinon 120 s. Les exécutions déclenchées par Cron sans délai explicite LLM ou agent désactivent le watchdog d’inactivité et s’appuient sur le délai d’expiration externe de Cron.

## Cas de fin anticipée

- Délai d’expiration de l’agent (abandon)
- AbortSignal (annulation)
- Déconnexion Gateway ou délai d’expiration RPC
- Délai d’expiration de `agent.wait` (attente uniquement, n’arrête pas l’agent)

## Connexe

- [Tools](/fr/tools) — outils d’agent disponibles
- [Hooks](/fr/automation/hooks) — scripts pilotés par événements déclenchés par les événements du cycle de vie de l’agent
- [Compaction](/fr/concepts/compaction) — comment les longues conversations sont résumées
- [Exec Approvals](/fr/tools/exec-approvals) — barrières d’approbation pour les commandes shell
- [Thinking](/fr/tools/thinking) — configuration du niveau de réflexion/raisonnement
