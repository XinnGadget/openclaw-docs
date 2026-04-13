---
read_when:
    - Étendre qa-lab ou qa-channel
    - Ajout de scénarios QA adossés au dépôt
    - Créer une automatisation QA plus réaliste autour du tableau de bord Gateway
summary: Forme de l’automatisation QA privée pour qa-lab, qa-channel, les scénarios préconfigurés et les rapports de protocole
title: Automatisation QA E2E
x-i18n:
    generated_at: "2026-04-13T07:04:03Z"
    model: gpt-5.4
    provider: openai
    source_hash: a4a4f5c765163565c95c2a071f201775fd9d8d60cad4ff25d71e4710559c1570
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# Automatisation QA E2E

La pile QA privée est conçue pour exercer OpenClaw d’une manière plus réaliste,
façonnée par les canaux, qu’un simple test unitaire ne peut le faire.

Éléments actuels :

- `extensions/qa-channel` : canal de messages synthétique avec des surfaces pour les MP, les canaux, les fils,
  les réactions, les modifications et les suppressions.
- `extensions/qa-lab` : UI de débogage et bus QA pour observer la transcription,
  injecter des messages entrants et exporter un rapport Markdown.
- `qa/` : ressources d’amorçage adossées au dépôt pour la tâche de lancement et les
  scénarios QA de référence.

Le flux actuel de l’opérateur QA est un site QA à deux volets :

- Gauche : tableau de bord Gateway (Control UI) avec l’agent.
- Droite : QA Lab, affichant la transcription de style Slack et le plan de scénario.

Lancez-le avec :

```bash
pnpm qa:lab:up
```

Cela construit le site QA, démarre la voie Gateway adossée à Docker et expose la
page QA Lab où un opérateur ou une boucle d’automatisation peut donner à l’agent une mission
QA, observer le comportement réel du canal et consigner ce qui a fonctionné, échoué ou
est resté bloqué.

Pour une itération plus rapide sur l’UI de QA Lab sans reconstruire l’image Docker à chaque fois,
démarrez la pile avec un bundle QA Lab monté en liaison :

```bash
pnpm openclaw qa docker-build-image
pnpm qa:lab:build
pnpm qa:lab:up:fast
pnpm qa:lab:watch
```

`qa:lab:up:fast` conserve les services Docker sur une image préconstruite et monte en liaison
`extensions/qa-lab/web/dist` dans le conteneur `qa-lab`. `qa:lab:watch`
reconstruit ce bundle lors des changements, et le navigateur se recharge automatiquement lorsque
le hachage de ressource QA Lab change.

Pour une voie Matrix de smoke test sur transport réel, exécutez :

```bash
pnpm openclaw qa matrix
```

Cette voie provisionne un homeserver Tuwunel jetable dans Docker, enregistre des
utilisateurs temporaires pour le pilote, le SUT et l’observateur, crée un salon privé, puis exécute
le Plugin Matrix réel dans un enfant QA gateway. La voie à transport réel garde la
configuration enfant limitée au transport testé, afin que Matrix s’exécute sans
`qa-channel` dans la configuration enfant.

Pour une voie Telegram de smoke test sur transport réel, exécutez :

```bash
pnpm openclaw qa telegram
```

Cette voie cible un groupe privé Telegram réel au lieu de provisionner un serveur
jetable. Elle nécessite `OPENCLAW_QA_TELEGRAM_GROUP_ID`,
`OPENCLAW_QA_TELEGRAM_DRIVER_BOT_TOKEN` et
`OPENCLAW_QA_TELEGRAM_SUT_BOT_TOKEN`, ainsi que deux bots distincts dans le même
groupe privé. Le bot SUT doit avoir un nom d’utilisateur Telegram, et
l’observation bot-à-bot fonctionne mieux lorsque les deux bots ont le mode
Bot-to-Bot Communication activé dans `@BotFather`.

Les voies de transport en direct partagent désormais un contrat plus petit au lieu que chacune
invente sa propre forme de liste de scénarios :

`qa-channel` reste la suite large de comportements produit synthétiques et ne fait pas partie
de la matrice de couverture des transports en direct.

| Voie     | Canary | Filtrage des mentions | Blocage par liste d’autorisation | Réponse de premier niveau | Reprise après redémarrage | Suivi de fil | Isolation du fil | Observation des réactions | Commande help |
| -------- | ------ | --------------------- | -------------------------------- | ------------------------- | ------------------------- | ------------ | ---------------- | ------------------------- | ------------- |
| Matrix   | x      | x                     | x                                | x                         | x                         | x            | x                | x                         |               |
| Telegram | x      |                       |                                  |                           |                           |              |                  |                           | x             |

Cela permet à `qa-channel` de rester la suite large de comportements produit tandis que Matrix,
Telegram et les futurs transports en direct partagent une checklist explicite de contrat de transport.

Pour une voie VM Linux jetable sans intégrer Docker au parcours QA, exécutez :

```bash
pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline
```

Cela démarre un invité Multipass neuf, installe les dépendances, construit OpenClaw
dans l’invité, exécute `qa suite`, puis copie le rapport QA normal et le
résumé dans `.artifacts/qa-e2e/...` sur l’hôte.
Il réutilise le même comportement de sélection de scénarios que `qa suite` sur l’hôte.
Les exécutions sur l’hôte et sur Multipass exécutent plusieurs scénarios sélectionnés en parallèle
avec des workers Gateway isolés par défaut, jusqu’à 64 workers ou le nombre de
scénarios sélectionnés. Utilisez `--concurrency <count>` pour ajuster le nombre de workers, ou
`--concurrency 1` pour une exécution en série.
Les exécutions en direct transmettent les entrées d’auth QA prises en charge qui sont pratiques pour
l’invité : clés de fournisseur basées sur l’environnement, chemin de configuration du fournisseur QA live, et
`CODEX_HOME` lorsqu’il est présent. Gardez `--output-dir` sous la racine du dépôt afin que l’invité
puisse réécrire via l’espace de travail monté.

## Ressources d’amorçage adossées au dépôt

Les ressources d’amorçage se trouvent dans `qa/` :

- `qa/scenarios/index.md`
- `qa/scenarios/*.md`

Elles sont intentionnellement dans git afin que le plan QA soit visible à la fois pour les humains et pour
l’agent.

`qa-lab` doit rester un exécuteur Markdown générique. Chaque fichier Markdown de scénario est
la source de vérité pour une exécution de test et doit définir :

- les métadonnées du scénario
- les références de documentation et de code
- les exigences de Plugin facultatives
- le correctif de configuration Gateway facultatif
- le `qa-flow` exécutable

La surface d’exécution réutilisable qui sous-tend `qa-flow` peut rester générique
et transversale. Par exemple, les scénarios Markdown peuvent combiner des helpers côté
transport avec des helpers côté navigateur qui pilotent la Control UI intégrée via la surface
Gateway `browser.request` sans ajouter d’exécuteur à cas particulier.

La liste de référence doit rester suffisamment large pour couvrir :

- les MP et le chat de canal
- le comportement des fils
- le cycle de vie des actions sur les messages
- les rappels Cron
- le rappel mémoire
- le changement de modèle
- le transfert à un sous-agent
- la lecture du dépôt et de la documentation
- une petite tâche de build comme Lobster Invaders

## Adaptateurs de transport

`qa-lab` possède une interface de transport générique pour les scénarios QA Markdown.
`qa-channel` est le premier adaptateur sur cette interface, mais l’objectif de conception est plus large :
les futurs canaux réels ou synthétiques doivent s’intégrer au même exécuteur de suite
au lieu d’ajouter un exécuteur QA spécifique à un transport.

Au niveau de l’architecture, la répartition est la suivante :

- `qa-lab` possède l’exécution générique des scénarios, la concurrence des workers, l’écriture des artefacts et le reporting.
- l’adaptateur de transport possède la configuration Gateway, l’état de préparation, l’observation entrante et sortante, les actions de transport et l’état de transport normalisé.
- les fichiers de scénarios Markdown sous `qa/scenarios/` définissent l’exécution de test ; `qa-lab` fournit la surface d’exécution réutilisable qui les exécute.

Les consignes d’adoption destinées aux mainteneurs pour les nouveaux adaptateurs de canal se trouvent dans
[Testing](/fr/help/testing#adding-a-channel-to-qa).

## Rapports

`qa-lab` exporte un rapport de protocole Markdown à partir de la chronologie observée du bus.
Le rapport doit répondre à ces questions :

- Ce qui a fonctionné
- Ce qui a échoué
- Ce qui est resté bloqué
- Quels scénarios de suivi valent la peine d’être ajoutés

Pour les vérifications de caractère et de style, exécutez le même scénario sur plusieurs références de modèles live
et écrivez un rapport Markdown évalué :

```bash
pnpm openclaw qa character-eval \
  --model openai/gpt-5.4,thinking=xhigh \
  --model openai/gpt-5.2,thinking=xhigh \
  --model openai/gpt-5,thinking=xhigh \
  --model anthropic/claude-opus-4-6,thinking=high \
  --model anthropic/claude-sonnet-4-6,thinking=high \
  --model zai/glm-5.1,thinking=high \
  --model moonshot/kimi-k2.5,thinking=high \
  --model google/gemini-3.1-pro-preview,thinking=high \
  --judge-model openai/gpt-5.4,thinking=xhigh,fast \
  --judge-model anthropic/claude-opus-4-6,thinking=high \
  --blind-judge-models \
  --concurrency 16 \
  --judge-concurrency 16
```

La commande exécute des processus enfants locaux QA gateway, pas Docker. Les scénarios
d’évaluation du caractère doivent définir la persona via `SOUL.md`, puis exécuter des tours utilisateur ordinaires
comme le chat, l’aide sur l’espace de travail et de petites tâches sur des fichiers. Le modèle candidat
ne doit pas être informé qu’il est en cours d’évaluation. La commande conserve chaque
transcription complète, enregistre des statistiques d’exécution de base, puis demande aux modèles juges en mode fast avec
un raisonnement `xhigh` de classer les exécutions selon leur naturel, leur ambiance et leur humour.
Utilisez `--blind-judge-models` lors de la comparaison de fournisseurs : l’invite du juge reçoit toujours
chaque transcription et statut d’exécution, mais les références candidates sont remplacées par des étiquettes neutres
comme `candidate-01` ; le rapport remappe les classements vers les vraies références après
l’analyse.
Les exécutions candidates utilisent par défaut le niveau de réflexion `high`, avec `xhigh` pour les modèles OpenAI qui le
prennent en charge. Remplacez un candidat spécifique en ligne avec
`--model provider/model,thinking=<level>`. `--thinking <level>` définit toujours une
valeur de repli globale, et l’ancienne forme `--model-thinking <provider/model=level>` est
conservée pour compatibilité.
Les références candidates OpenAI utilisent par défaut le mode fast afin que le traitement prioritaire soit utilisé là où
le fournisseur le prend en charge. Ajoutez `,fast`, `,no-fast` ou `,fast=false` en ligne lorsqu’un
candidat ou juge unique a besoin d’un remplacement. Passez `--fast` uniquement si vous souhaitez
forcer le mode fast pour tous les modèles candidats. Les durées des candidats et des juges sont
enregistrées dans le rapport pour l’analyse comparative, mais les invites des juges indiquent explicitement
de ne pas classer selon la vitesse.
Les exécutions des modèles candidats et juges utilisent toutes deux par défaut une concurrence de 16. Réduisez
`--concurrency` ou `--judge-concurrency` lorsque les limites du fournisseur ou la pression sur la Gateway locale
rendent une exécution trop bruitée.
Lorsqu’aucun `--model` candidat n’est transmis, l’évaluation du caractère utilise par défaut
`openai/gpt-5.4`, `openai/gpt-5.2`, `openai/gpt-5`, `anthropic/claude-opus-4-6`,
`anthropic/claude-sonnet-4-6`, `zai/glm-5.1`,
`moonshot/kimi-k2.5` et
`google/gemini-3.1-pro-preview` lorsqu’aucun `--model` n’est transmis.
Lorsqu’aucun `--judge-model` n’est transmis, les juges utilisent par défaut
`openai/gpt-5.4,thinking=xhigh,fast` et
`anthropic/claude-opus-4-6,thinking=high`.

## Documentation associée

- [Testing](/fr/help/testing)
- [QA Channel](/fr/channels/qa-channel)
- [Dashboard](/web/dashboard)
