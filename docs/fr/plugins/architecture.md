---
read_when:
    - Création ou débogage des plugins OpenClaw natifs
    - Comprendre le modèle de capacités des plugins ou les limites de propriété
    - Travailler sur le pipeline de chargement des plugins ou le registre
    - Implémenter des hooks d’exécution de fournisseur ou des plugins de canal
sidebarTitle: Internals
summary: 'Composants internes des plugins : modèle de capacités, propriété, contrats, pipeline de chargement et assistants d’exécution'
title: Composants internes des plugins
x-i18n:
    generated_at: "2026-04-11T15:16:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: 7cac67984d0d729c0905bcf5c18372fb0d9b02bbd3a531580b7e2ef483ef40a6
    source_path: plugins/architecture.md
    workflow: 15
---

# Composants internes des plugins

<Info>
  Il s’agit de la **référence d’architecture approfondie**. Pour des guides pratiques, voir :
  - [Installer et utiliser des plugins](/fr/tools/plugin) — guide utilisateur
  - [Premiers pas](/fr/plugins/building-plugins) — premier tutoriel de plugin
  - [Plugins de canal](/fr/plugins/sdk-channel-plugins) — créer un canal de messagerie
  - [Plugins de fournisseur](/fr/plugins/sdk-provider-plugins) — créer un fournisseur de modèles
  - [Vue d’ensemble du SDK](/fr/plugins/sdk-overview) — carte des imports et API d’enregistrement
</Info>

Cette page couvre l’architecture interne du système de plugins OpenClaw.

## Modèle de capacités public

Les capacités constituent le modèle public des **plugins natifs** dans OpenClaw. Chaque
plugin OpenClaw natif s’enregistre pour un ou plusieurs types de capacités :

| Capability             | Registration method                              | Example plugins                      |
| ---------------------- | ------------------------------------------------ | ------------------------------------ |
| Inférence de texte     | `api.registerProvider(...)`                      | `openai`, `anthropic`                |
| Backend d’inférence CLI  | `api.registerCliBackend(...)`                    | `openai`, `anthropic`                |
| Parole                 | `api.registerSpeechProvider(...)`                | `elevenlabs`, `microsoft`            |
| Transcription en temps réel | `api.registerRealtimeTranscriptionProvider(...)` | `openai`                             |
| Voix en temps réel     | `api.registerRealtimeVoiceProvider(...)`         | `openai`                             |
| Compréhension des médias    | `api.registerMediaUnderstandingProvider(...)`    | `openai`, `google`                   |
| Génération d’images    | `api.registerImageGenerationProvider(...)`       | `openai`, `google`, `fal`, `minimax` |
| Génération musicale    | `api.registerMusicGenerationProvider(...)`       | `google`, `minimax`                  |
| Génération de vidéos   | `api.registerVideoGenerationProvider(...)`       | `qwen`                               |
| Récupération web       | `api.registerWebFetchProvider(...)`              | `firecrawl`                          |
| Recherche web          | `api.registerWebSearchProvider(...)`             | `google`                             |
| Canal / messagerie     | `api.registerChannel(...)`                       | `msteams`, `matrix`                  |

Un plugin qui enregistre zéro capacité mais fournit des hooks, des outils ou des
services est un plugin **legacy hook-only**. Ce modèle reste entièrement pris en charge.

### Position de compatibilité externe

Le modèle de capacités est intégré au cœur et utilisé par les plugins
bundled/natifs aujourd’hui, mais la compatibilité des plugins externes exige
encore un niveau d’exigence plus élevé que « c’est exporté, donc c’est figé ».

Recommandations actuelles :

- **plugins externes existants :** conserver le fonctionnement des intégrations basées sur des hooks ; traiter cela comme la base de compatibilité
- **nouveaux plugins bundled/natifs :** préférer un enregistrement explicite des capacités plutôt que des accès spécifiques à un fournisseur ou de nouveaux modèles hook-only
- **plugins externes adoptant l’enregistrement des capacités :** autorisés, mais considérer les surfaces d’assistance spécifiques aux capacités comme évolutives, sauf si la documentation marque explicitement un contrat comme stable

Règle pratique :

- les API d’enregistrement des capacités sont l’orientation voulue
- les hooks legacy restent la voie la plus sûre pour éviter les ruptures pour les plugins externes pendant la transition
- tous les sous-chemins d’assistance exportés ne se valent pas ; préférez le contrat documenté étroit, et non des exports d’assistance accessoires

### Formes de plugins

OpenClaw classe chaque plugin chargé selon une forme basée sur son comportement
réel d’enregistrement (et non uniquement sur des métadonnées statiques) :

- **plain-capability** -- enregistre exactement un type de capacité (par exemple un plugin de fournisseur uniquement comme `mistral`)
- **hybrid-capability** -- enregistre plusieurs types de capacités (par exemple `openai` possède l’inférence de texte, la parole, la compréhension des médias et la génération d’images)
- **hook-only** -- enregistre uniquement des hooks (typés ou personnalisés), sans capacités, outils, commandes ni services
- **non-capability** -- enregistre des outils, commandes, services ou routes, mais aucune capacité

Utilisez `openclaw plugins inspect <id>` pour voir la forme d’un plugin et le
détail de ses capacités. Voir [Référence CLI](/cli/plugins#inspect) pour plus de détails.

### Hooks legacy

Le hook `before_agent_start` reste pris en charge comme voie de compatibilité pour
les plugins hook-only. Des plugins legacy utilisés en conditions réelles en dépendent encore.

Orientation :

- le conserver fonctionnel
- le documenter comme legacy
- préférer `before_model_resolve` pour le travail de substitution de modèle/fournisseur
- préférer `before_prompt_build` pour le travail de mutation de prompt
- ne le supprimer qu’après baisse de l’usage réel et lorsque la couverture des fixtures prouve la sécurité de la migration

### Signaux de compatibilité

Lorsque vous exécutez `openclaw doctor` ou `openclaw plugins inspect <id>`, vous pouvez voir
l’un de ces libellés :

| Signal                     | Signification                                                  |
| -------------------------- | -------------------------------------------------------------- |
| **config valid**           | La configuration est analysée correctement et les plugins se résolvent |
| **compatibility advisory** | Le plugin utilise un modèle pris en charge mais plus ancien (par ex. `hook-only`) |
| **legacy warning**         | Le plugin utilise `before_agent_start`, qui est obsolète        |
| **hard error**             | La configuration est invalide ou le plugin n’a pas pu être chargé |

Ni `hook-only` ni `before_agent_start` ne casseront votre plugin aujourd’hui --
`hook-only` est un avis, et `before_agent_start` ne déclenche qu’un avertissement. Ces
signaux apparaissent aussi dans `openclaw status --all` et `openclaw plugins doctor`.

## Vue d’ensemble de l’architecture

Le système de plugins d’OpenClaw comporte quatre couches :

1. **Manifeste + découverte**
   OpenClaw trouve les plugins candidats à partir des chemins configurés, des racines d’espace de travail,
   des racines globales d’extensions et des extensions bundled. La découverte lit d’abord
   les manifestes natifs `openclaw.plugin.json` ainsi que les manifestes de bundle pris en charge.
2. **Activation + validation**
   Le cœur décide si un plugin découvert est activé, désactivé, bloqué ou
   sélectionné pour un emplacement exclusif comme la mémoire.
3. **Chargement à l’exécution**
   Les plugins OpenClaw natifs sont chargés dans le processus via jiti et enregistrent
   des capacités dans un registre central. Les bundles compatibles sont normalisés en
   enregistrements de registre sans importer de code d’exécution.
4. **Consommation des surfaces**
   Le reste d’OpenClaw lit le registre pour exposer les outils, canaux, configuration des fournisseurs,
   hooks, routes HTTP, commandes CLI et services.

Pour la CLI des plugins en particulier, la découverte des commandes racine est divisée en deux phases :

- les métadonnées au moment de l’analyse viennent de `registerCli(..., { descriptors: [...] })`
- le véritable module CLI du plugin peut rester paresseux et s’enregistrer lors de la première invocation

Cela permet de conserver le code CLI appartenant au plugin dans le plugin tout en laissant OpenClaw
réserver les noms de commandes racine avant l’analyse.

La limite de conception importante :

- la découverte + validation de la configuration doivent fonctionner à partir des **métadonnées de manifeste/schéma**
  sans exécuter de code de plugin
- le comportement d’exécution natif provient du chemin `register(api)` du module du plugin

Cette séparation permet à OpenClaw de valider la configuration, d’expliquer les plugins manquants/désactivés et
de construire des indications d’interface/schéma avant que l’exécution complète ne soit active.

### Plugins de canal et outil de message partagé

Les plugins de canal n’ont pas besoin d’enregistrer un outil séparé d’envoi/édition/réaction pour
les actions de chat normales. OpenClaw conserve un outil `message` partagé dans le cœur, et
les plugins de canal possèdent la découverte et l’exécution spécifiques au canal qui se trouvent derrière.

La limite actuelle est la suivante :

- le cœur possède l’hôte de l’outil `message` partagé, le câblage des prompts, la
  tenue des sessions/fils et la répartition de l’exécution
- les plugins de canal possèdent la découverte d’actions délimitées, la découverte des
  capacités et tout fragment de schéma spécifique au canal
- les plugins de canal possèdent la grammaire de conversation de session spécifique au fournisseur, comme
  la manière dont les identifiants de conversation encodent les identifiants de fil ou héritent des conversations parentes
- les plugins de canal exécutent l’action finale via leur adaptateur d’action

Pour les plugins de canal, la surface SDK est
`ChannelMessageActionAdapter.describeMessageTool(...)`. Cet appel de découverte unifié
permet à un plugin de renvoyer ensemble ses actions visibles, ses capacités et ses contributions au schéma,
afin que ces éléments ne divergent pas.

Le cœur transmet la portée d’exécution à cette étape de découverte. Les champs importants incluent :

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- `requesterSenderId` entrant approuvé

C’est important pour les plugins sensibles au contexte. Un canal peut masquer ou exposer
des actions de message en fonction du compte actif, de la salle/du fil/du message courant, ou de
l’identité de demandeur approuvée, sans coder en dur des branches spécifiques au canal dans
l’outil `message` du cœur.

C’est pourquoi les modifications de routage de l’embedded-runner restent du travail de plugin : le runner est
responsable de transmettre l’identité actuelle du chat/de la session à la limite de découverte du plugin afin que
l’outil `message` partagé expose la bonne surface appartenant au canal pour le tour courant.

Pour les assistants d’exécution appartenant aux canaux, les plugins bundled doivent conserver l’exécution
dans leurs propres modules d’extension. Le cœur ne possède plus les environnements d’exécution d’actions de message
Discord, Slack, Telegram ou WhatsApp sous `src/agents/tools`.
Nous ne publions pas de sous-chemins `plugin-sdk/*-action-runtime` séparés, et les plugins bundled
doivent importer directement leur propre code d’exécution local depuis leurs
modules appartenant à l’extension.

La même limite s’applique de manière générale aux points d’intégration SDK nommés d’après un fournisseur :
le cœur ne doit pas importer de barils de commodité spécifiques à un canal pour Slack, Discord, Signal,
WhatsApp ou des extensions similaires. Si le cœur a besoin d’un comportement, il doit soit consommer
le propre baril `api.ts` / `runtime-api.ts` du plugin bundled, soit faire évoluer le besoin
vers une capacité générique étroite dans le SDK partagé.

Pour les sondages en particulier, il existe deux chemins d’exécution :

- `outbound.sendPoll` est la base partagée pour les canaux qui correspondent au modèle de sondage commun
- `actions.handleAction("poll")` est le chemin préféré pour la sémantique de sondage spécifique au canal ou pour des paramètres de sondage supplémentaires

Le cœur diffère désormais l’analyse partagée des sondages jusqu’à ce que la répartition du sondage par plugin décline
l’action, afin que les gestionnaires de sondages appartenant au plugin puissent accepter des champs
de sondage spécifiques au canal sans être bloqués d’abord par l’analyseur générique de sondages.

Voir [Pipeline de chargement](#load-pipeline) pour la séquence complète de démarrage.

## Modèle de propriété des capacités

OpenClaw considère un plugin natif comme la limite de propriété pour une **entreprise** ou une
**fonctionnalité**, et non comme un regroupement d’intégrations sans lien.

Cela signifie :

- un plugin d’entreprise doit généralement posséder toutes les surfaces OpenClaw de cette entreprise
- un plugin de fonctionnalité doit généralement posséder l’ensemble de la surface de la fonctionnalité qu’il introduit
- les canaux doivent consommer les capacités partagées du cœur au lieu de réimplémenter de manière ad hoc le comportement des fournisseurs

Exemples :

- le plugin bundled `openai` possède le comportement de fournisseur de modèles OpenAI et le comportement OpenAI pour la parole + la voix en temps réel + la compréhension des médias + la génération d’images
- le plugin bundled `elevenlabs` possède le comportement de parole ElevenLabs
- le plugin bundled `microsoft` possède le comportement de parole Microsoft
- le plugin bundled `google` possède le comportement de fournisseur de modèles Google ainsi que les comportements Google de compréhension des médias + génération d’images + recherche web
- le plugin bundled `firecrawl` possède le comportement de récupération web Firecrawl
- les plugins bundled `minimax`, `mistral`, `moonshot` et `zai` possèdent leurs backends de compréhension des médias
- le plugin bundled `qwen` possède le comportement de fournisseur de texte Qwen ainsi que les comportements de compréhension des médias et de génération de vidéos
- le plugin `voice-call` est un plugin de fonctionnalité : il possède le transport d’appel, les outils,
  la CLI, les routes et le pontage de flux média Twilio, mais il consomme les capacités partagées de parole,
  plus la transcription en temps réel et la voix en temps réel au lieu d’importer directement les plugins fournisseurs

L’état final visé est :

- OpenAI se trouve dans un seul plugin même s’il couvre les modèles de texte, la parole, les images et, à l’avenir, la vidéo
- un autre fournisseur peut faire de même pour sa propre surface fonctionnelle
- les canaux ne se soucient pas du plugin fournisseur qui possède le fournisseur ; ils consomment le contrat de capacité partagé exposé par le cœur

C’est la distinction clé :

- **plugin** = limite de propriété
- **capability** = contrat du cœur que plusieurs plugins peuvent implémenter ou consommer

Ainsi, si OpenClaw ajoute un nouveau domaine comme la vidéo, la première question n’est pas
« quel fournisseur doit coder en dur la gestion de la vidéo ? » La première question est « quel est
le contrat de capacité vidéo du cœur ? » Une fois ce contrat en place, les plugins fournisseurs
peuvent s’y enregistrer et les plugins de canal/de fonctionnalité peuvent le consommer.

Si la capacité n’existe pas encore, la bonne démarche est généralement :

1. définir la capacité manquante dans le cœur
2. l’exposer de manière typée via l’API/l’exécution des plugins
3. raccorder les canaux/fonctionnalités à cette capacité
4. laisser les plugins fournisseurs enregistrer les implémentations

Cela permet de garder une propriété explicite tout en évitant un comportement du cœur qui dépend
d’un seul fournisseur ou d’un chemin de code spécifique à un plugin ponctuel.

### Stratification des capacités

Utilisez ce modèle mental pour décider où le code doit se trouver :

- **couche de capacité du cœur** : orchestration partagée, politique, repli,
  règles de fusion de configuration, sémantique de livraison et contrats typés
- **couche de plugin fournisseur** : API spécifiques au fournisseur, authentification, catalogues de modèles, synthèse vocale,
  génération d’images, backends vidéo futurs, points de terminaison d’usage
- **couche de plugin de canal/fonctionnalité** : intégration Slack/Discord/voice-call/etc.
  qui consomme les capacités du cœur et les présente sur une surface

Par exemple, la synthèse vocale suit cette forme :

- le cœur possède la politique TTS au moment de la réponse, l’ordre de repli, les préférences et la livraison au canal
- `openai`, `elevenlabs` et `microsoft` possèdent les implémentations de synthèse
- `voice-call` consomme l’assistant d’exécution TTS de téléphonie

Ce même schéma doit être privilégié pour les capacités futures.

### Exemple de plugin d’entreprise multi-capacités

Un plugin d’entreprise doit sembler cohérent de l’extérieur. Si OpenClaw a des
contrats partagés pour les modèles, la parole, la transcription en temps réel, la voix en temps réel, la
compréhension des médias, la génération d’images, la génération de vidéos, la récupération web et la recherche web,
un fournisseur peut posséder toutes ses surfaces au même endroit :

```ts
import type { OpenClawPluginDefinition } from "openclaw/plugin-sdk/plugin-entry";
import {
  describeImageWithModel,
  transcribeOpenAiCompatibleAudio,
} from "openclaw/plugin-sdk/media-understanding";

const plugin: OpenClawPluginDefinition = {
  id: "exampleai",
  name: "ExampleAI",
  register(api) {
    api.registerProvider({
      id: "exampleai",
      // hooks d’authentification/de catalogue de modèles/d’exécution
    });

    api.registerSpeechProvider({
      id: "exampleai",
      // config de parole du fournisseur — implémente directement l’interface SpeechProviderPlugin
    });

    api.registerMediaUnderstandingProvider({
      id: "exampleai",
      capabilities: ["image", "audio", "video"],
      async describeImage(req) {
        return describeImageWithModel({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
      async transcribeAudio(req) {
        return transcribeOpenAiCompatibleAudio({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
    });

    api.registerWebSearchProvider(
      createPluginBackedWebSearchProvider({
        id: "exampleai-search",
        // logique d’identifiants + de récupération
      }),
    );
  },
};

export default plugin;
```

Ce qui compte, ce ne sont pas les noms exacts des assistants. C’est la forme qui compte :

- un seul plugin possède la surface du fournisseur
- le cœur possède toujours les contrats de capacité
- les canaux et plugins de fonctionnalité consomment les assistants `api.runtime.*`, pas le code du fournisseur
- les tests de contrat peuvent vérifier que le plugin a enregistré les capacités
  qu’il prétend posséder

### Exemple de capacité : compréhension vidéo

OpenClaw traite déjà la compréhension d’image/audio/vidéo comme une seule
capacité partagée. Le même modèle de propriété s’y applique :

1. le cœur définit le contrat de compréhension des médias
2. les plugins fournisseurs enregistrent `describeImage`, `transcribeAudio` et
   `describeVideo` selon le cas
3. les canaux et plugins de fonctionnalité consomment le comportement partagé du cœur au lieu de
   se raccorder directement au code du fournisseur

Cela évite d’intégrer dans le cœur les hypothèses vidéo d’un seul fournisseur. Le plugin possède
la surface du fournisseur ; le cœur possède le contrat de capacité et le comportement de repli.

La génération vidéo utilise déjà cette même séquence : le cœur possède le
contrat de capacité typé et l’assistant d’exécution, et les plugins fournisseurs enregistrent
des implémentations `api.registerVideoGenerationProvider(...)` sur cette base.

Besoin d’une liste de déploiement concrète ? Voir
[Recettes de capacités](/fr/plugins/architecture).

## Contrats et application

La surface de l’API des plugins est intentionnellement typée et centralisée dans
`OpenClawPluginApi`. Ce contrat définit les points d’enregistrement pris en charge et
les assistants d’exécution sur lesquels un plugin peut s’appuyer.

Pourquoi c’est important :

- les auteurs de plugins bénéficient d’une norme interne stable
- le cœur peut rejeter une propriété en double, par exemple deux plugins enregistrant le même identifiant de fournisseur
- le démarrage peut afficher des diagnostics exploitables pour un enregistrement mal formé
- les tests de contrat peuvent imposer la propriété des plugins bundled et éviter les dérives silencieuses

Il existe deux couches d’application :

1. **application de l’enregistrement à l’exécution**
   Le registre des plugins valide les enregistrements à mesure que les plugins se chargent. Exemples :
   les identifiants de fournisseurs en double, les identifiants de fournisseurs de parole en double, et les
   enregistrements mal formés produisent des diagnostics de plugin au lieu d’un comportement indéfini.
2. **tests de contrat**
   Les plugins bundled sont capturés dans des registres de contrat pendant les exécutions de test afin
   qu’OpenClaw puisse affirmer explicitement la propriété. Aujourd’hui, cela est utilisé pour les
   fournisseurs de modèles, fournisseurs de parole, fournisseurs de recherche web et la propriété de l’enregistrement bundled.

L’effet pratique est qu’OpenClaw sait, dès le départ, quel plugin possède quelle
surface. Cela permet au cœur et aux canaux de se composer de manière fluide parce que la propriété est
déclarée, typée et testable plutôt qu’implicite.

### Ce qui a sa place dans un contrat

Les bons contrats de plugin sont :

- typés
- petits
- spécifiques à une capacité
- possédés par le cœur
- réutilisables par plusieurs plugins
- consommables par les canaux/fonctionnalités sans connaissance d’un fournisseur

Les mauvais contrats de plugin sont :

- une politique spécifique au fournisseur cachée dans le cœur
- des échappatoires ponctuelles de plugin qui contournent le registre
- du code de canal qui accède directement à une implémentation de fournisseur
- des objets d’exécution ad hoc qui ne font pas partie de `OpenClawPluginApi` ou de
  `api.runtime`

En cas de doute, élevez le niveau d’abstraction : définissez d’abord la capacité, puis
laissez les plugins s’y brancher.

## Modèle d’exécution

Les plugins OpenClaw natifs s’exécutent **dans le processus** avec la Gateway. Ils ne sont pas
sandboxés. Un plugin natif chargé partage la même limite de confiance au niveau du processus que
le code du cœur.

Implications :

- un plugin natif peut enregistrer des outils, des gestionnaires réseau, des hooks et des services
- un bug dans un plugin natif peut faire planter ou déstabiliser la gateway
- un plugin natif malveillant équivaut à une exécution de code arbitraire dans le processus OpenClaw

Les bundles compatibles sont plus sûrs par défaut parce qu’OpenClaw les traite actuellement
comme des packs de métadonnées/contenu. Dans les versions actuelles, cela signifie surtout des
Skills bundled.

Utilisez des listes d’autorisation et des chemins d’installation/de chargement explicites pour les plugins non bundled. Traitez
les plugins d’espace de travail comme du code de développement, et non comme des valeurs par défaut de production.

Pour les noms de packages d’espace de travail bundled, gardez l’identifiant du plugin ancré dans le nom npm :
`@openclaw/<id>` par défaut, ou un suffixe typé approuvé tel que
`-provider`, `-plugin`, `-speech`, `-sandbox` ou `-media-understanding` lorsque
le package expose intentionnellement un rôle de plugin plus étroit.

Note de confiance importante :

- `plugins.allow` fait confiance aux **identifiants de plugin**, et non à la provenance de la source.
- Un plugin d’espace de travail portant le même identifiant qu’un plugin bundled masque intentionnellement
  la copie bundled lorsque ce plugin d’espace de travail est activé/sur liste d’autorisation.
- C’est normal et utile pour le développement local, les tests de correctifs et les correctifs urgents.

## Limite d’export

OpenClaw exporte des capacités, pas des commodités d’implémentation.

Gardez l’enregistrement des capacités public. Réduisez les exports d’assistance hors contrat :

- sous-chemins d’assistance spécifiques à un plugin bundled
- sous-chemins de plomberie d’exécution non destinés à l’API publique
- assistants de commodité spécifiques à un fournisseur
- assistants de configuration/d’onboarding qui sont des détails d’implémentation

Certains sous-chemins d’assistance de plugins bundled restent encore présents dans la carte d’exports SDK générée
pour des raisons de compatibilité et de maintenance des plugins bundled. Exemples actuels :
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup`, et plusieurs points d’intégration `plugin-sdk/matrix*`. Traitez-les comme des
exports réservés de détail d’implémentation, et non comme le modèle SDK recommandé pour
de nouveaux plugins tiers.

## Pipeline de chargement

Au démarrage, OpenClaw fait grosso modo ceci :

1. découvre les racines de plugins candidates
2. lit les manifestes natifs ou de bundles compatibles et les métadonnées de package
3. rejette les candidats non sûrs
4. normalise la configuration des plugins (`plugins.enabled`, `allow`, `deny`, `entries`,
   `slots`, `load.paths`)
5. décide de l’activation pour chaque candidat
6. charge les modules natifs activés via jiti
7. appelle les hooks natifs `register(api)` (ou `activate(api)` — un alias legacy) et collecte les enregistrements dans le registre des plugins
8. expose le registre aux surfaces de commandes/d’exécution

<Note>
`activate` est un alias legacy de `register` — le chargeur résout celui qui est présent (`def.register ?? def.activate`) et l’appelle au même moment. Tous les plugins bundled utilisent `register` ; préférez `register` pour les nouveaux plugins.
</Note>

Les barrières de sécurité interviennent **avant** l’exécution à l’exécution. Les candidats sont bloqués
lorsque le point d’entrée sort de la racine du plugin, que le chemin est accessible en écriture par tout le monde, ou que la propriété du chemin semble suspecte pour les plugins non bundled.

### Comportement manifest-first

Le manifeste est la source de vérité du plan de contrôle. OpenClaw l’utilise pour :

- identifier le plugin
- découvrir les canaux/Skills/schéma de configuration déclarés ou les capacités de bundle
- valider `plugins.entries.<id>.config`
- enrichir les libellés/placeholders de l’interface de contrôle
- afficher les métadonnées d’installation/de catalogue
- conserver des descripteurs bon marché d’activation et de configuration sans charger l’exécution du plugin

Pour les plugins natifs, le module d’exécution est la partie plan de données. Il enregistre le
comportement réel tel que hooks, outils, commandes ou flux de fournisseur.

Les blocs facultatifs `activation` et `setup` du manifeste restent sur le plan de contrôle.
Ce sont des descripteurs de métadonnées uniquement pour la planification d’activation et la découverte de configuration ;
ils ne remplacent pas l’enregistrement d’exécution, `register(...)` ou `setupEntry`.

### Ce que le chargeur met en cache

OpenClaw conserve de courts caches en processus pour :

- les résultats de découverte
- les données du registre de manifestes
- les registres de plugins chargés

Ces caches réduisent les démarrages brusques et la surcharge des commandes répétées. On peut les considérer sans danger
comme des caches de performance à courte durée de vie, et non comme de la persistance.

Note sur les performances :

- Définissez `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` ou
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1` pour désactiver ces caches.
- Ajustez les fenêtres de cache avec `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` et
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS`.

## Modèle de registre

Les plugins chargés ne mutent pas directement des variables globales arbitraires du cœur. Ils s’enregistrent dans un
registre central des plugins.

Le registre suit :

- les enregistrements de plugins (identité, source, origine, statut, diagnostics)
- les outils
- les hooks legacy et hooks typés
- les canaux
- les fournisseurs
- les gestionnaires Gateway RPC
- les routes HTTP
- les enregistreurs CLI
- les services d’arrière-plan
- les commandes appartenant au plugin

Les fonctionnalités du cœur lisent ensuite ce registre au lieu de parler directement aux modules de plugin.
Cela maintient un chargement à sens unique :

- module de plugin -> enregistrement dans le registre
- exécution du cœur -> consommation du registre

Cette séparation est importante pour la maintenabilité. Cela signifie que la plupart des surfaces du cœur n’ont besoin
que d’un seul point d’intégration : « lire le registre », et non « traiter spécialement chaque module de plugin ».

## Callbacks de liaison de conversation

Les plugins qui lient une conversation peuvent réagir lorsqu’une approbation est résolue.

Utilisez `api.onConversationBindingResolved(...)` pour recevoir un callback après qu’une requête de liaison
est approuvée ou refusée :

```ts
export default {
  id: "my-plugin",
  register(api) {
    api.onConversationBindingResolved(async (event) => {
      if (event.status === "approved") {
        // Une liaison existe maintenant pour ce plugin + cette conversation.
        console.log(event.binding?.conversationId);
        return;
      }

      // La requête a été refusée ; effacez tout état local en attente.
      console.log(event.request.conversation.conversationId);
    });
  },
};
```

Champs de la charge utile du callback :

- `status`: `"approved"` ou `"denied"`
- `decision`: `"allow-once"`, `"allow-always"` ou `"deny"`
- `binding`: la liaison résolue pour les requêtes approuvées
- `request`: le résumé de la requête d’origine, l’indication de détachement, l’identifiant de l’expéditeur et
  les métadonnées de conversation

Ce callback est uniquement une notification. Il ne modifie pas qui est autorisé à lier une
conversation, et il s’exécute une fois le traitement d’approbation du cœur terminé.

## Hooks d’exécution du fournisseur

Les plugins de fournisseur ont désormais deux couches :

- métadonnées de manifeste : `providerAuthEnvVars` pour une recherche légère de l’authentification du fournisseur par variable d’environnement
  avant le chargement de l’exécution, `providerAuthAliases` pour les variantes de fournisseur qui partagent
  l’authentification, `channelEnvVars` pour une recherche légère de l’environnement/de la configuration du canal avant le
  chargement de l’exécution, ainsi que `providerAuthChoices` pour des libellés légers d’onboarding/de choix d’authentification et
  des métadonnées d’indicateurs CLI avant le chargement de l’exécution
- hooks au moment de la configuration : `catalog` / ancien `discovery` plus `applyConfigDefaults`
- hooks d’exécution : `normalizeModelId`, `normalizeTransport`,
  `normalizeConfig`,
  `applyNativeStreamingUsageCompat`, `resolveConfigApiKey`,
  `resolveSyntheticAuth`, `resolveExternalAuthProfiles`,
  `shouldDeferSyntheticProfileAuth`,
  `resolveDynamicModel`, `prepareDynamicModel`, `normalizeResolvedModel`,
  `contributeResolvedModelCompat`, `capabilities`,
  `normalizeToolSchemas`, `inspectToolSchemas`,
  `resolveReasoningOutputMode`, `prepareExtraParams`, `createStreamFn`,
  `wrapStreamFn`, `resolveTransportTurnState`,
  `resolveWebSocketSessionPolicy`, `formatApiKey`, `refreshOAuth`,
  `buildAuthDoctorHint`, `matchesContextOverflowError`,
  `classifyFailoverReason`, `isCacheTtlEligible`,
  `buildMissingAuthMessage`, `suppressBuiltInModel`, `augmentModelCatalog`,
  `isBinaryThinking`, `supportsXHighThinking`,
  `resolveDefaultThinkingLevel`, `isModernModelRef`, `prepareRuntimeAuth`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `createEmbeddingProvider`,
  `buildReplayPolicy`,
  `sanitizeReplayHistory`, `validateReplayTurns`, `onModelSelected`

OpenClaw possède toujours la boucle d’agent générique, le basculement, la gestion des transcriptions et
la politique des outils. Ces hooks constituent la surface d’extension pour le comportement spécifique au fournisseur sans
avoir besoin d’un transport d’inférence entièrement personnalisé.

Utilisez le `providerAuthEnvVars` du manifeste lorsque le fournisseur dispose d’identifiants basés sur l’environnement
que les chemins génériques d’authentification/statut/sélecteur de modèle doivent voir sans charger l’exécution du plugin.
Utilisez `providerAuthAliases` du manifeste lorsqu’un identifiant de fournisseur doit réutiliser
les variables d’environnement, profils d’authentification, authentification basée sur la configuration et choix d’onboarding par clé API d’un autre identifiant de fournisseur.
Utilisez `providerAuthChoices` du manifeste lorsque les
surfaces CLI d’onboarding/de choix d’authentification doivent connaître l’identifiant de choix du fournisseur, les libellés de groupe et le câblage simple d’authentification par indicateur unique sans charger l’exécution du fournisseur. Conservez `envVars` de l’exécution du fournisseur pour les indications destinées à l’opérateur, comme les libellés d’onboarding ou les
variables de configuration de client OAuth `client-id`/`client-secret`.

Utilisez `channelEnvVars` du manifeste lorsqu’un canal possède une authentification ou une configuration pilotée par l’environnement
que le repli générique sur l’environnement shell, les vérifications config/statut ou les invites de configuration doivent voir
sans charger l’exécution du canal.

### Ordre et usage des hooks

Pour les plugins de modèle/fournisseur, OpenClaw appelle les hooks approximativement dans cet ordre.
La colonne « Quand l’utiliser » sert de guide rapide de décision.

| #   | Hook                              | Ce qu’il fait                                                                                                   | Quand l’utiliser                                                                                                                             |
| --- | --------------------------------- | ---------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `catalog`                         | Publie la configuration du fournisseur dans `models.providers` pendant la génération de `models.json`          | Le fournisseur possède un catalogue ou des valeurs par défaut de base URL                                                                    |
| 2   | `applyConfigDefaults`             | Applique les valeurs par défaut globales de configuration appartenant au fournisseur pendant la matérialisation de la configuration | Les valeurs par défaut dépendent du mode d’authentification, de l’environnement ou de la sémantique de famille de modèles du fournisseur    |
| --  | _(recherche de modèle intégrée)_  | OpenClaw essaie d’abord le chemin normal registre/catalogue                                                      | _(pas un hook de plugin)_                                                                                                                    |
| 3   | `normalizeModelId`                | Normalise les alias legacy ou de préversion des identifiants de modèle avant la recherche                       | Le fournisseur possède le nettoyage des alias avant la résolution canonique du modèle                                                        |
| 4   | `normalizeTransport`              | Normalise `api` / `baseUrl` d’une famille de fournisseurs avant l’assemblage générique du modèle               | Le fournisseur possède le nettoyage du transport pour des identifiants de fournisseurs personnalisés dans la même famille de transport       |
| 5   | `normalizeConfig`                 | Normalise `models.providers.<id>` avant la résolution d’exécution/du fournisseur                                 | Le fournisseur a besoin d’un nettoyage de configuration qui doit vivre avec le plugin ; les assistants bundled de la famille Google servent aussi de solution de secours pour les entrées de configuration Google prises en charge |
| 6   | `applyNativeStreamingUsageCompat` | Applique aux fournisseurs de configuration des réécritures de compatibilité d’usage en streaming natif         | Le fournisseur a besoin de correctifs de métadonnées d’usage en streaming natif pilotés par le point de terminaison                         |
| 7   | `resolveConfigApiKey`             | Résout l’authentification par marqueur d’environnement pour les fournisseurs de configuration avant le chargement de l’authentification d’exécution | Le fournisseur possède sa propre résolution de clé API par marqueur d’environnement ; `amazon-bedrock` a aussi ici un résolveur intégré de marqueur d’environnement AWS |
| 8   | `resolveSyntheticAuth`            | Expose une authentification locale/autohébergée ou adossée à la configuration sans persister du texte brut     | Le fournisseur peut fonctionner avec un marqueur d’identifiants synthétiques/locaux                                                         |
| 9   | `resolveExternalAuthProfiles`     | Superpose des profils d’authentification externe appartenant au fournisseur ; `persistence` vaut par défaut `runtime-only` pour les identifiants détenus par la CLI/l’application | Le fournisseur réutilise des identifiants d’authentification externes sans persister de jetons d’actualisation copiés                      |
| 10  | `shouldDeferSyntheticProfileAuth` | Fait passer les placeholders de profils synthétiques stockés après l’authentification adossée à l’environnement/à la configuration | Le fournisseur stocke des profils placeholders synthétiques qui ne doivent pas avoir la priorité                                            |
| 11  | `resolveDynamicModel`             | Repli synchrone pour les identifiants de modèle appartenant au fournisseur qui ne sont pas encore dans le registre local | Le fournisseur accepte des identifiants de modèle amont arbitraires                                                                         |
| 12  | `prepareDynamicModel`             | Préchauffage asynchrone, puis `resolveDynamicModel` s’exécute à nouveau                                          | Le fournisseur a besoin de métadonnées réseau avant de résoudre des identifiants inconnus                                                   |
| 13  | `normalizeResolvedModel`          | Réécriture finale avant que l’embedded runner n’utilise le modèle résolu                                         | Le fournisseur a besoin de réécritures de transport tout en utilisant toujours un transport du cœur                                         |
| 14  | `contributeResolvedModelCompat`   | Contribue des drapeaux de compatibilité pour des modèles fournisseurs derrière un autre transport compatible     | Le fournisseur reconnaît ses propres modèles sur des transports proxy sans prendre le contrôle du fournisseur                               |
| 15  | `capabilities`                    | Métadonnées de transcription/d’outillage appartenant au fournisseur utilisées par la logique partagée du cœur   | Le fournisseur a besoin de particularités de transcription/de famille de fournisseurs                                                        |
| 16  | `normalizeToolSchemas`            | Normalise les schémas d’outils avant que l’embedded runner ne les voie                                           | Le fournisseur a besoin d’un nettoyage de schéma propre à une famille de transport                                                          |
| 17  | `inspectToolSchemas`              | Expose des diagnostics de schéma appartenant au fournisseur après normalisation                                  | Le fournisseur veut des avertissements sur les mots-clés sans enseigner au cœur des règles spécifiques au fournisseur                       |
| 18  | `resolveReasoningOutputMode`      | Sélectionne le contrat de sortie de raisonnement natif ou balisé                                                 | Le fournisseur a besoin d’une sortie raisonnement/finale balisée au lieu de champs natifs                                                   |
| 19  | `prepareExtraParams`              | Normalisation des paramètres de requête avant les wrappers génériques d’options de flux                         | Le fournisseur a besoin de paramètres de requête par défaut ou d’un nettoyage de paramètres par fournisseur                                 |
| 20  | `createStreamFn`                  | Remplace entièrement le chemin de flux normal par un transport personnalisé                                      | Le fournisseur a besoin d’un protocole filaire personnalisé, et pas seulement d’un wrapper                                                  |
| 21  | `wrapStreamFn`                    | Wrapper de flux après application des wrappers génériques                                                        | Le fournisseur a besoin de wrappers de compatibilité pour en-têtes/corps/modèle de requête sans transport personnalisé                     |
| 22  | `resolveTransportTurnState`       | Attache des en-têtes ou métadonnées de transport natives par tour                                                | Le fournisseur veut que les transports génériques envoient une identité de tour native au fournisseur                                       |
| 23  | `resolveWebSocketSessionPolicy`   | Attache des en-têtes WebSocket natifs ou une politique de refroidissement de session                             | Le fournisseur veut que les transports WS génériques ajustent les en-têtes de session ou la politique de repli                             |
| 24  | `formatApiKey`                    | Formateur de profil d’authentification : le profil stocké devient la chaîne `apiKey` à l’exécution             | Le fournisseur stocke des métadonnées d’authentification supplémentaires et a besoin d’une forme de jeton d’exécution personnalisée        |
| 25  | `refreshOAuth`                    | Remplacement de l’actualisation OAuth pour des points de terminaison d’actualisation personnalisés ou une politique d’échec d’actualisation | Le fournisseur ne correspond pas aux actualisateurs partagés `pi-ai`                                                                        |
| 26  | `buildAuthDoctorHint`             | Indication de réparation ajoutée lorsque l’actualisation OAuth échoue                                            | Le fournisseur a besoin de conseils de réparation d’authentification lui appartenant après l’échec d’actualisation                         |
| 27  | `matchesContextOverflowError`     | Détecteur appartenant au fournisseur des débordements de fenêtre de contexte                                     | Le fournisseur possède des erreurs brutes de débordement que les heuristiques génériques manqueraient                                      |
| 28  | `classifyFailoverReason`          | Classification appartenant au fournisseur des raisons de basculement                                             | Le fournisseur peut mapper les erreurs brutes d’API/de transport vers limitation de débit/surcharge/etc.                                    |
| 29  | `isCacheTtlEligible`              | Politique de cache de prompt pour les fournisseurs proxy/backhaul                                                | Le fournisseur a besoin d’une régulation TTL du cache spécifique au proxy                                                                   |
| 30  | `buildMissingAuthMessage`         | Remplacement du message générique de récupération en cas d’authentification manquante                           | Le fournisseur a besoin d’une indication de récupération spécifique au fournisseur en cas d’authentification manquante                     |
| 31  | `suppressBuiltInModel`            | Suppression des modèles amont obsolètes avec indication d’erreur facultative destinée à l’utilisateur           | Le fournisseur doit masquer des lignes amont obsolètes ou les remplacer par une indication fournisseur                                     |
| 32  | `augmentModelCatalog`             | Lignes de catalogue synthétiques/finales ajoutées après la découverte                                            | Le fournisseur a besoin de lignes synthétiques compatibles vers l’avant dans `models list` et les sélecteurs                               |
| 33  | `isBinaryThinking`                | Bascule de raisonnement marche/arrêt pour les fournisseurs à raisonnement binaire                                | Le fournisseur n’expose qu’un raisonnement binaire activé/désactivé                                                                         |
| 34  | `supportsXHighThinking`           | Prise en charge du raisonnement `xhigh` pour certains modèles                                                    | Le fournisseur veut `xhigh` uniquement sur un sous-ensemble de modèles                                                                      |
| 35  | `resolveDefaultThinkingLevel`     | Niveau `/think` par défaut pour une famille de modèles spécifique                                                | Le fournisseur possède la politique `/think` par défaut pour une famille de modèles                                                         |
| 36  | `isModernModelRef`                | Détecteur de modèles modernes pour les filtres de profils live et la sélection smoke                            | Le fournisseur possède la logique de correspondance des modèles préférés live/smoke                                                         |
| 37  | `prepareRuntimeAuth`              | Échange un identifiant configuré contre le véritable jeton/clé d’exécution juste avant l’inférence              | Le fournisseur a besoin d’un échange de jeton ou d’un identifiant de requête de courte durée                                               |
| 38  | `resolveUsageAuth`                | Résout les identifiants d’usage/facturation pour `/usage` et les surfaces de statut associées                 | Le fournisseur a besoin d’une analyse personnalisée des jetons d’usage/de quota ou d’un identifiant d’usage différent                      |
| 39  | `fetchUsageSnapshot`              | Récupère et normalise des instantanés d’usage/de quota spécifiques au fournisseur une fois l’authentification résolue | Le fournisseur a besoin d’un point de terminaison d’usage spécifique au fournisseur ou d’un analyseur de charge utile                     |
| 40  | `createEmbeddingProvider`         | Construit un adaptateur d’embedding appartenant au fournisseur pour la mémoire/la recherche                    | Le comportement d’embedding mémoire appartient au plugin fournisseur                                                                        |
| 41  | `buildReplayPolicy`               | Renvoie une politique de rejeu qui contrôle la gestion des transcriptions pour le fournisseur                  | Le fournisseur a besoin d’une politique de transcription personnalisée (par exemple, suppression des blocs de réflexion)                   |
| 42  | `sanitizeReplayHistory`           | Réécrit l’historique de rejeu après le nettoyage générique des transcriptions                                  | Le fournisseur a besoin de réécritures de rejeu spécifiques au fournisseur au-delà des assistants partagés de compaction                   |
| 43  | `validateReplayTurns`             | Validation finale ou remodelage des tours de rejeu avant l’embedded runner                                     | Le transport du fournisseur a besoin d’une validation plus stricte des tours après l’assainissement générique                              |
| 44  | `onModelSelected`                 | Exécute des effets de bord post-sélection appartenant au fournisseur                                           | Le fournisseur a besoin de télémétrie ou d’un état appartenant au fournisseur lorsqu’un modèle devient actif                               |

`normalizeModelId`, `normalizeTransport` et `normalizeConfig` vérifient d’abord le
plugin fournisseur correspondant, puis passent aux autres plugins fournisseurs compatibles avec les hooks
jusqu’à ce que l’un d’eux modifie réellement l’identifiant du modèle ou le transport/la configuration. Cela permet aux
shims d’alias/de fournisseurs compatibles de continuer à fonctionner sans obliger l’appelant à savoir quel
plugin bundled possède la réécriture. Si aucun hook fournisseur ne réécrit une entrée de configuration prise en charge de la famille
Google, le normaliseur de configuration Google bundled applique toujours ce nettoyage de compatibilité.

Si le fournisseur a besoin d’un protocole filaire entièrement personnalisé ou d’un exécuteur de requêtes personnalisé,
il s’agit d’une autre classe d’extension. Ces hooks concernent le comportement du fournisseur qui
s’exécute toujours sur la boucle d’inférence normale d’OpenClaw.

### Exemple de fournisseur

```ts
api.registerProvider({
  id: "example-proxy",
  label: "Example Proxy",
  auth: [],
  catalog: {
    order: "simple",
    run: async (ctx) => {
      const apiKey = ctx.resolveProviderApiKey("example-proxy").apiKey;
      if (!apiKey) {
        return null;
      }
      return {
        provider: {
          baseUrl: "https://proxy.example.com/v1",
          apiKey,
          api: "openai-completions",
          models: [{ id: "auto", name: "Auto" }],
        },
      };
    },
  },
  resolveDynamicModel: (ctx) => ({
    id: ctx.modelId,
    name: ctx.modelId,
    provider: "example-proxy",
    api: "openai-completions",
    baseUrl: "https://proxy.example.com/v1",
    reasoning: false,
    input: ["text"],
    cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
    contextWindow: 128000,
    maxTokens: 8192,
  }),
  prepareRuntimeAuth: async (ctx) => {
    const exchanged = await exchangeToken(ctx.apiKey);
    return {
      apiKey: exchanged.token,
      baseUrl: exchanged.baseUrl,
      expiresAt: exchanged.expiresAt,
    };
  },
  resolveUsageAuth: async (ctx) => {
    const auth = await ctx.resolveOAuthToken();
    return auth ? { token: auth.token } : null;
  },
  fetchUsageSnapshot: async (ctx) => {
    return await fetchExampleProxyUsage(ctx.token, ctx.timeoutMs, ctx.fetchFn);
  },
});
```

### Exemples intégrés

- Anthropic utilise `resolveDynamicModel`, `capabilities`, `buildAuthDoctorHint`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `isCacheTtlEligible`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`,
  et `wrapStreamFn` parce qu’il possède la compatibilité ascendante de Claude 4.6,
  les indications de famille de fournisseurs, les conseils de réparation de l’authentification, l’intégration du point de terminaison d’usage,
  l’éligibilité du cache de prompt, les valeurs par défaut de configuration sensibles à l’authentification, la politique
  par défaut/adaptative de réflexion de Claude, ainsi que la mise en forme de flux spécifique à Anthropic pour
  les en-têtes bêta, `/fast` / `serviceTier`, et `context1m`.
- Les assistants de flux spécifiques à Claude d’Anthropic restent pour l’instant dans le point d’intégration public
  `api.ts` / `contract-api.ts` du plugin bundled. Cette surface de package
  exporte `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
  `resolveAnthropicFastMode`, `resolveAnthropicServiceTier`, ainsi que les constructeurs de wrappers Anthropic
  de niveau inférieur, au lieu d’élargir le SDK générique autour des règles d’en-tête bêta d’un seul
  fournisseur.
- OpenAI utilise `resolveDynamicModel`, `normalizeResolvedModel` et
  `capabilities`, ainsi que `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `supportsXHighThinking` et `isModernModelRef`
  parce qu’il possède la compatibilité ascendante de GPT-5.4, la normalisation directe OpenAI
  `openai-completions` -> `openai-responses`, les indications d’authentification adaptées à Codex,
  la suppression de Spark, les lignes synthétiques de liste OpenAI, ainsi que la politique de réflexion / de modèle live de GPT-5 ; la famille de flux `openai-responses-defaults`
  possède les wrappers natifs partagés OpenAI Responses pour les en-têtes d’attribution,
  `/fast`/`serviceTier`, la verbosité du texte, la recherche web Codex native,
  la mise en forme de charge utile compatible avec le raisonnement, et la gestion du contexte Responses.
- OpenRouter utilise `catalog`, ainsi que `resolveDynamicModel` et
  `prepareDynamicModel`, parce que le fournisseur est en passthrough et peut exposer de nouveaux
  identifiants de modèle avant la mise à jour du catalogue statique d’OpenClaw ; il utilise aussi
  `capabilities`, `wrapStreamFn` et `isCacheTtlEligible` afin de maintenir hors du cœur
  les en-têtes de requête spécifiques au fournisseur, les métadonnées de routage, les correctifs de raisonnement et
  la politique de cache de prompt. Sa politique de rejeu vient de la
  famille `passthrough-gemini`, tandis que la famille de flux `openrouter-thinking`
  possède l’injection de raisonnement proxy et les omissions de modèles non pris en charge / `auto`.
- GitHub Copilot utilise `catalog`, `auth`, `resolveDynamicModel` et
  `capabilities`, ainsi que `prepareRuntimeAuth` et `fetchUsageSnapshot`, car il
  a besoin d’un login par appareil appartenant au fournisseur, d’un comportement de repli de modèle, des particularités de transcription Claude,
  d’un échange de jeton GitHub -> jeton Copilot, ainsi que d’un point de terminaison d’usage appartenant au fournisseur.
- OpenAI Codex utilise `catalog`, `resolveDynamicModel`,
  `normalizeResolvedModel`, `refreshOAuth` et `augmentModelCatalog`, ainsi que
  `prepareExtraParams`, `resolveUsageAuth` et `fetchUsageSnapshot`, parce qu’il
  s’exécute encore sur les transports OpenAI du cœur mais possède sa normalisation de transport/base URL,
  sa politique de repli d’actualisation OAuth, son choix de transport par défaut,
  ses lignes synthétiques de catalogue Codex, ainsi que l’intégration du point de terminaison d’usage ChatGPT ; il
  partage la même famille de flux `openai-responses-defaults` que l’OpenAI direct.
- Google AI Studio et Gemini CLI OAuth utilisent `resolveDynamicModel`,
  `buildReplayPolicy`, `sanitizeReplayHistory`,
  `resolveReasoningOutputMode`, `wrapStreamFn` et `isModernModelRef` parce que la
  famille de rejeu `google-gemini` possède le repli de compatibilité ascendante Gemini 3.1,
  la validation native du rejeu Gemini, l’assainissement du rejeu au démarrage, le mode de sortie de raisonnement
  balisé, ainsi que la correspondance des modèles modernes, tandis que la
  famille de flux `google-thinking` possède la normalisation de charge utile de réflexion Gemini ;
  Gemini CLI OAuth utilise aussi `formatApiKey`, `resolveUsageAuth` et
  `fetchUsageSnapshot` pour la mise en forme des jetons, l’analyse des jetons et le
  câblage du point de terminaison de quota.
- Anthropic Vertex utilise `buildReplayPolicy` via la
  famille de rejeu `anthropic-by-model` afin que le nettoyage du rejeu spécifique à Claude reste
  limité aux identifiants Claude au lieu de tous les transports `anthropic-messages`.
- Amazon Bedrock utilise `buildReplayPolicy`, `matchesContextOverflowError`,
  `classifyFailoverReason` et `resolveDefaultThinkingLevel` parce qu’il possède
  la classification spécifique à Bedrock des erreurs throttle/not-ready/context-overflow
  pour le trafic Anthropic-sur-Bedrock ; sa politique de rejeu partage toujours la même
  protection `anthropic-by-model` limitée à Claude.
- OpenRouter, Kilocode, Opencode et Opencode Go utilisent `buildReplayPolicy`
  via la famille de rejeu `passthrough-gemini` parce qu’ils proxifient des modèles Gemini
  au travers de transports compatibles OpenAI et ont besoin de l’assainissement de signature de pensée
  Gemini sans validation native du rejeu Gemini ni réécritures au
  démarrage.
- MiniMax utilise `buildReplayPolicy` via la
  famille de rejeu `hybrid-anthropic-openai` parce qu’un seul fournisseur possède à la fois
  la sémantique Anthropic-message et OpenAI-compatible ; il conserve
  l’abandon des blocs de réflexion limités à Claude du côté Anthropic tout en remplaçant le mode de sortie
  du raisonnement pour revenir au natif, et la famille de flux `minimax-fast-mode` possède
  les réécritures de modèles fast-mode sur le chemin de flux partagé.
- Moonshot utilise `catalog` ainsi que `wrapStreamFn` parce qu’il utilise toujours le
  transport OpenAI partagé mais a besoin d’une normalisation de charge utile de réflexion appartenant au fournisseur ; la
  famille de flux `moonshot-thinking` mappe la configuration ainsi que l’état `/think` sur sa
  charge utile native de réflexion binaire.
- Kilocode utilise `catalog`, `capabilities`, `wrapStreamFn` et
  `isCacheTtlEligible` parce qu’il a besoin d’en-têtes de requête appartenant au fournisseur,
  de normalisation de charge utile de raisonnement, d’indications de transcription Gemini et d’une régulation
  Anthropic du cache TTL ; la famille de flux `kilocode-thinking` conserve l’injection de réflexion Kilo
  sur le chemin de flux proxy partagé tout en ignorant `kilo/auto` et
  d’autres identifiants de modèle proxy qui ne prennent pas en charge des charges utiles de raisonnement explicites.
- Z.AI utilise `resolveDynamicModel`, `prepareExtraParams`, `wrapStreamFn`,
  `isCacheTtlEligible`, `isBinaryThinking`, `isModernModelRef`,
  `resolveUsageAuth` et `fetchUsageSnapshot` parce qu’il possède le repli GLM-5,
  les valeurs par défaut `tool_stream`, l’UX de réflexion binaire, la correspondance des modèles modernes, ainsi que
  l’authentification d’usage et la récupération de quota ; la famille de flux `tool-stream-default-on`
  maintient hors du code manuscrit par fournisseur le wrapper `tool_stream` activé par défaut.
- xAI utilise `normalizeResolvedModel`, `normalizeTransport`,
  `contributeResolvedModelCompat`, `prepareExtraParams`, `wrapStreamFn`,
  `resolveSyntheticAuth`, `resolveDynamicModel` et `isModernModelRef`
  parce qu’il possède la normalisation native du transport xAI Responses, les réécritures d’alias Grok fast-mode, le `tool_stream` par défaut, le nettoyage strict-tool / charge utile de raisonnement,
  la réutilisation d’authentification de repli pour les outils appartenant au plugin, la résolution
  compatible vers l’avant des modèles Grok, ainsi que des correctifs de compatibilité appartenant au fournisseur comme le profil de schéma d’outils xAI,
  les mots-clés de schéma non pris en charge, le `web_search` natif, et le décodage des arguments d’appel d’outil
  avec entités HTML.
- Mistral, OpenCode Zen et OpenCode Go utilisent uniquement `capabilities` pour maintenir hors du cœur
  les particularités de transcription/d’outillage.
- Les fournisseurs bundled uniquement catalogue tels que `byteplus`, `cloudflare-ai-gateway`,
  `huggingface`, `kimi-coding`, `nvidia`, `qianfan`,
  `synthetic`, `together`, `venice`, `vercel-ai-gateway` et `volcengine` utilisent
  uniquement `catalog`.
- Qwen utilise `catalog` pour son fournisseur de texte ainsi que des enregistrements partagés de compréhension des médias et de génération de vidéos pour ses surfaces multimodales.
- MiniMax et Xiaomi utilisent `catalog` ainsi que les hooks d’usage parce que leur comportement `/usage`
  appartient au plugin même si l’inférence s’exécute encore via les transports partagés.

## Assistants d’exécution

Les plugins peuvent accéder à certains assistants du cœur via `api.runtime`. Pour la synthèse vocale :

```ts
const clip = await api.runtime.tts.textToSpeech({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const result = await api.runtime.tts.textToSpeechTelephony({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const voices = await api.runtime.tts.listVoices({
  provider: "elevenlabs",
  cfg: api.config,
});
```

Remarques :

- `textToSpeech` renvoie la charge utile normale de sortie TTS du cœur pour les surfaces de fichier/note vocale.
- Utilise la configuration du cœur `messages.tts` et la sélection de fournisseur.
- Renvoie un tampon audio PCM + une fréquence d’échantillonnage. Les plugins doivent rééchantillonner/encoder pour les fournisseurs.
- `listVoices` est facultatif selon le fournisseur. Utilisez-le pour les sélecteurs de voix appartenant au fournisseur ou les flux de configuration.
- Les listes de voix peuvent inclure des métadonnées plus riches telles que la locale, le genre et des tags de personnalité pour des sélecteurs conscients du fournisseur.
- OpenAI et ElevenLabs prennent aujourd’hui en charge la téléphonie. Microsoft non.

Les plugins peuvent également enregistrer des fournisseurs de parole via `api.registerSpeechProvider(...)`.

```ts
api.registerSpeechProvider({
  id: "acme-speech",
  label: "Acme Speech",
  isConfigured: ({ config }) => Boolean(config.messages?.tts),
  synthesize: async (req) => {
    return {
      audioBuffer: Buffer.from([]),
      outputFormat: "mp3",
      fileExtension: ".mp3",
      voiceCompatible: false,
    };
  },
});
```

Remarques :

- Conservez dans le cœur la politique TTS, le repli et la livraison des réponses.
- Utilisez les fournisseurs de parole pour le comportement de synthèse appartenant au fournisseur.
- L’entrée Microsoft legacy `edge` est normalisée vers l’identifiant de fournisseur `microsoft`.
- Le modèle de propriété privilégié est orienté entreprise : un même plugin fournisseur peut posséder
  le texte, la parole, l’image et les futurs fournisseurs de médias à mesure qu’OpenClaw ajoute ces
  contrats de capacité.

Pour la compréhension d’image/audio/vidéo, les plugins enregistrent un fournisseur de
compréhension des médias typé au lieu d’un sac générique clé/valeur :

```ts
api.registerMediaUnderstandingProvider({
  id: "google",
  capabilities: ["image", "audio", "video"],
  describeImage: async (req) => ({ text: "..." }),
  transcribeAudio: async (req) => ({ text: "..." }),
  describeVideo: async (req) => ({ text: "..." }),
});
```

Remarques :

- Conservez dans le cœur l’orchestration, le repli, la configuration et le câblage des canaux.
- Conservez le comportement du fournisseur dans le plugin fournisseur.
- L’extension additive doit rester typée : nouvelles méthodes optionnelles, nouveaux champs de résultat
  optionnels, nouvelles capacités optionnelles.
- La génération de vidéos suit déjà le même schéma :
  - le cœur possède le contrat de capacité et l’assistant d’exécution
  - les plugins fournisseurs enregistrent `api.registerVideoGenerationProvider(...)`
  - les plugins de fonctionnalité/de canal consomment `api.runtime.videoGeneration.*`

Pour les assistants d’exécution de compréhension des médias, les plugins peuvent appeler :

```ts
const image = await api.runtime.mediaUnderstanding.describeImageFile({
  filePath: "/tmp/inbound-photo.jpg",
  cfg: api.config,
  agentDir: "/tmp/agent",
});

const video = await api.runtime.mediaUnderstanding.describeVideoFile({
  filePath: "/tmp/inbound-video.mp4",
  cfg: api.config,
});
```

Pour la transcription audio, les plugins peuvent utiliser soit l’exécution media-understanding,
soit l’ancien alias STT :

```ts
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  // Facultatif lorsque le type MIME ne peut pas être déduit de façon fiable :
  mime: "audio/ogg",
});
```

Remarques :

- `api.runtime.mediaUnderstanding.*` est la surface partagée privilégiée pour la
  compréhension d’image/audio/vidéo.
- Utilise la configuration audio media-understanding du cœur (`tools.media.audio`) et l’ordre de repli du fournisseur.
- Renvoie `{ text: undefined }` lorsqu’aucune sortie de transcription n’est produite (par exemple entrée ignorée/non prise en charge).
- `api.runtime.stt.transcribeAudioFile(...)` reste disponible comme alias de compatibilité.

Les plugins peuvent aussi lancer des exécutions de sous-agent en arrière-plan via `api.runtime.subagent` :

```ts
const result = await api.runtime.subagent.run({
  sessionKey: "agent:main:subagent:search-helper",
  message: "Développe cette requête en recherches de suivi ciblées.",
  provider: "openai",
  model: "gpt-4.1-mini",
  deliver: false,
});
```

Remarques :

- `provider` et `model` sont des remplacements par exécution facultatifs, et non des modifications persistantes de session.
- OpenClaw n’honore ces champs de remplacement que pour les appelants de confiance.
- Pour les exécutions de repli appartenant au plugin, les opérateurs doivent activer explicitement `plugins.entries.<id>.subagent.allowModelOverride: true`.
- Utilisez `plugins.entries.<id>.subagent.allowedModels` pour limiter les plugins de confiance à des cibles canoniques `provider/model` spécifiques, ou `"*"` pour autoriser explicitement n’importe quelle cible.
- Les exécutions de sous-agent de plugins non fiables fonctionnent toujours, mais les demandes de remplacement sont rejetées au lieu d’entraîner silencieusement un repli.

Pour la recherche web, les plugins peuvent consommer l’assistant d’exécution partagé au lieu
d’accéder directement au câblage de l’outil d’agent :

```ts
const providers = api.runtime.webSearch.listProviders({
  config: api.config,
});

const result = await api.runtime.webSearch.search({
  config: api.config,
  args: {
    query: "Assistants d’exécution des plugins OpenClaw",
    count: 5,
  },
});
```

Les plugins peuvent aussi enregistrer des fournisseurs de recherche web via
`api.registerWebSearchProvider(...)`.

Remarques :

- Conservez dans le cœur la sélection du fournisseur, la résolution des identifiants et la sémantique partagée des requêtes.
- Utilisez les fournisseurs de recherche web pour les transports de recherche spécifiques à un fournisseur.
- `api.runtime.webSearch.*` est la surface partagée privilégiée pour les plugins de fonctionnalité/de canal qui ont besoin d’un comportement de recherche sans dépendre du wrapper de l’outil d’agent.

### `api.runtime.imageGeneration`

```ts
const result = await api.runtime.imageGeneration.generate({
  config: api.config,
  args: { prompt: "Une mascotte homard amicale", size: "1024x1024" },
});

const providers = api.runtime.imageGeneration.listProviders({
  config: api.config,
});
```

- `generate(...)` : génère une image en utilisant la chaîne configurée de fournisseurs de génération d’images.
- `listProviders(...)` : liste les fournisseurs de génération d’images disponibles et leurs capacités.

## Routes HTTP Gateway

Les plugins peuvent exposer des points de terminaison HTTP avec `api.registerHttpRoute(...)`.

```ts
api.registerHttpRoute({
  path: "/acme/webhook",
  auth: "plugin",
  match: "exact",
  handler: async (_req, res) => {
    res.statusCode = 200;
    res.end("ok");
    return true;
  },
});
```

Champs de route :

- `path` : chemin de route sous le serveur HTTP Gateway.
- `auth` : obligatoire. Utilisez `"gateway"` pour exiger l’authentification normale de la gateway, ou `"plugin"` pour l’authentification/la vérification de webhook gérée par le plugin.
- `match` : facultatif. `"exact"` (par défaut) ou `"prefix"`.
- `replaceExisting` : facultatif. Permet au même plugin de remplacer son propre enregistrement de route existant.
- `handler` : renvoie `true` lorsque la route a traité la requête.

Remarques :

- `api.registerHttpHandler(...)` a été supprimé et provoquera une erreur de chargement du plugin. Utilisez `api.registerHttpRoute(...)` à la place.
- Les routes de plugin doivent déclarer `auth` explicitement.
- Les conflits exacts `path + match` sont rejetés sauf si `replaceExisting: true`, et un plugin ne peut pas remplacer la route d’un autre plugin.
- Les routes qui se chevauchent avec des niveaux `auth` différents sont rejetées. Gardez les chaînes de retombée `exact`/`prefix` uniquement au même niveau d’authentification.
- Les routes `auth: "plugin"` ne reçoivent **pas** automatiquement les portées d’exécution de l’opérateur. Elles sont destinées aux webhooks gérés par le plugin / à la vérification de signature, et non aux appels d’assistants Gateway privilégiés.
- Les routes `auth: "gateway"` s’exécutent dans une portée d’exécution de requête Gateway, mais cette portée est volontairement prudente :
  - l’authentification bearer par secret partagé (`gateway.auth.mode = "token"` / `"password"`) maintient les portées d’exécution des routes de plugin fixées à `operator.write`, même si l’appelant envoie `x-openclaw-scopes`
  - les modes HTTP de confiance avec identité (par exemple `trusted-proxy` ou `gateway.auth.mode = "none"` sur une entrée privée) n’honorent `x-openclaw-scopes` que lorsque l’en-tête est explicitement présent
  - si `x-openclaw-scopes` est absent sur ces requêtes de route de plugin porteuses d’identité, la portée d’exécution retombe à `operator.write`
- Règle pratique : ne supposez pas qu’une route de plugin authentifiée par la gateway est implicitement une surface d’administration. Si votre route a besoin d’un comportement réservé à l’administrateur, exigez un mode d’authentification porteur d’identité et documentez le contrat explicite de l’en-tête `x-openclaw-scopes`.

## Chemins d’import du SDK de plugin

Utilisez les sous-chemins du SDK au lieu de l’import monolithique `openclaw/plugin-sdk` lorsque
vous créez des plugins :

- `openclaw/plugin-sdk/plugin-entry` pour les primitives d’enregistrement des plugins.
- `openclaw/plugin-sdk/core` pour le contrat partagé générique côté plugin.
- `openclaw/plugin-sdk/config-schema` pour l’export du schéma Zod racine `openclaw.json`
  (`OpenClawSchema`).
- Primitives de canal stables telles que `openclaw/plugin-sdk/channel-setup`,
  `openclaw/plugin-sdk/setup-runtime`,
  `openclaw/plugin-sdk/setup-adapter-runtime`,
  `openclaw/plugin-sdk/setup-tools`,
  `openclaw/plugin-sdk/channel-pairing`,
  `openclaw/plugin-sdk/channel-contract`,
  `openclaw/plugin-sdk/channel-feedback`,
  `openclaw/plugin-sdk/channel-inbound`,
  `openclaw/plugin-sdk/channel-lifecycle`,
  `openclaw/plugin-sdk/channel-reply-pipeline`,
  `openclaw/plugin-sdk/command-auth`,
  `openclaw/plugin-sdk/secret-input`, et
  `openclaw/plugin-sdk/webhook-ingress` pour le câblage partagé de configuration/authentification/réponse/webhook.
  `channel-inbound` est la surface partagée pour l’anti-rebond, la correspondance des mentions,
  les assistants de politique de mention entrante, le formatage d’enveloppe et les
  assistants de contexte d’enveloppe entrante.
  `channel-setup` est le point d’intégration étroit de configuration à installation facultative.
  `setup-runtime` est la surface de configuration sûre à l’exécution utilisée par `setupEntry` /
  le démarrage différé, y compris les adaptateurs de patch de configuration sûrs à l’import.
  `setup-adapter-runtime` est le point d’intégration des adaptateurs de configuration de compte sensibles à l’environnement.
  `setup-tools` est le petit point d’intégration d’assistance CLI/archive/docs (`formatCliCommand`,
  `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`,
  `CONFIG_DIR`).
- Sous-chemins de domaine tels que `openclaw/plugin-sdk/channel-config-helpers`,
  `openclaw/plugin-sdk/allow-from`,
  `openclaw/plugin-sdk/channel-config-schema`,
  `openclaw/plugin-sdk/telegram-command-config`,
  `openclaw/plugin-sdk/channel-policy`,
  `openclaw/plugin-sdk/approval-gateway-runtime`,
  `openclaw/plugin-sdk/approval-handler-adapter-runtime`,
  `openclaw/plugin-sdk/approval-handler-runtime`,
  `openclaw/plugin-sdk/approval-runtime`,
  `openclaw/plugin-sdk/config-runtime`,
  `openclaw/plugin-sdk/infra-runtime`,
  `openclaw/plugin-sdk/agent-runtime`,
  `openclaw/plugin-sdk/lazy-runtime`,
  `openclaw/plugin-sdk/reply-history`,
  `openclaw/plugin-sdk/routing`,
  `openclaw/plugin-sdk/status-helpers`,
  `openclaw/plugin-sdk/text-runtime`,
  `openclaw/plugin-sdk/runtime-store`, et
  `openclaw/plugin-sdk/directory-runtime` pour les assistants partagés d’exécution/de configuration.
  `telegram-command-config` est le point d’intégration public étroit pour la normalisation/validation des commandes personnalisées Telegram et reste disponible même si la surface de contrat Telegram bundled est temporairement indisponible.
  `text-runtime` est la surface partagée pour le texte/Markdown/la journalisation, y compris
  la suppression du texte visible par l’assistant, les assistants de rendu/de découpage Markdown, les assistants de rédaction,
  les assistants de balises de directive et les utilitaires de texte sûr.
- Les points d’intégration de canal spécifiques à l’approbation doivent préférer un seul contrat `approvalCapability`
  sur le plugin. Le cœur lit ensuite l’authentification, la livraison, le rendu,
  le routage natif et le comportement paresseux du gestionnaire natif d’approbation via cette seule capacité
  au lieu de mélanger le comportement d’approbation dans des champs de plugin sans lien.
- `openclaw/plugin-sdk/channel-runtime` est obsolète et ne subsiste que comme
  shim de compatibilité pour les anciens plugins. Le nouveau code doit importer les primitives génériques
  plus étroites à la place, et le code du dépôt ne doit pas ajouter de nouveaux imports du
  shim.
- Les composants internes des extensions bundled restent privés. Les plugins externes doivent utiliser uniquement
  les sous-chemins `openclaw/plugin-sdk/*`. Le code cœur/test d’OpenClaw peut utiliser les
  points d’entrée publics du dépôt sous une racine de package de plugin tels que `index.js`, `api.js`,
  `runtime-api.js`, `setup-entry.js`, et des fichiers à portée étroite tels que
  `login-qr-api.js`. N’importez jamais `src/*` d’un package de plugin depuis le cœur ou depuis
  une autre extension.
- Séparation des points d’entrée du dépôt :
  `<plugin-package-root>/api.js` est le baril d’assistants/types,
  `<plugin-package-root>/runtime-api.js` est le baril réservé à l’exécution,
  `<plugin-package-root>/index.js` est le point d’entrée du plugin bundled,
  et `<plugin-package-root>/setup-entry.js` est le point d’entrée du plugin de configuration.
- Exemples actuels de fournisseurs bundled :
  - Anthropic utilise `api.js` / `contract-api.js` pour les assistants de flux Claude tels
    que `wrapAnthropicProviderStream`, les assistants d’en-tête bêta et l’analyse de `service_tier`.
  - OpenAI utilise `api.js` pour les constructeurs de fournisseur, les assistants de modèle par défaut et
    les constructeurs de fournisseur en temps réel.
  - OpenRouter utilise `api.js` pour son constructeur de fournisseur ainsi que des assistants d’onboarding/de configuration,
    tandis que `register.runtime.js` peut toujours réexporter des assistants génériques
    `plugin-sdk/provider-stream` pour un usage local au dépôt.
- Les points d’entrée publics chargés par façade préfèrent l’instantané de configuration d’exécution actif
  lorsqu’il existe, puis retombent sur le fichier de configuration résolu sur disque lorsque
  OpenClaw ne sert pas encore d’instantané d’exécution.
- Les primitives génériques partagées restent le contrat public préféré du SDK. Un petit
  ensemble réservé de compatibilité de points d’intégration d’assistance portant la marque de canaux bundled existe encore. Traitez-les comme des points d’intégration de maintenance bundled/de compatibilité, et non comme de nouvelles cibles d’import tierces ; les nouveaux contrats transversaux entre canaux doivent toujours être introduits sur des sous-chemins génériques `plugin-sdk/*` ou sur les barils locaux au plugin `api.js` /
  `runtime-api.js`.

Note de compatibilité :

- Évitez le baril racine `openclaw/plugin-sdk` pour le nouveau code.
- Préférez d’abord les primitives stables étroites. Les nouveaux sous-chemins setup/pairing/reply/
  feedback/contract/inbound/threading/command/secret-input/webhook/infra/
  allowlist/status/message-tool constituent le contrat prévu pour les nouveaux travaux de plugins
  bundled et externes.
  L’analyse/la correspondance des cibles appartient à `openclaw/plugin-sdk/channel-targets`.
  Les barrières d’actions de message et les assistants d’identifiant de message de réaction appartiennent à
  `openclaw/plugin-sdk/channel-actions`.
- Les barils d’assistance spécifiques à une extension bundled ne sont pas stables par défaut. Si un
  assistant n’est nécessaire qu’à une extension bundled, conservez-le derrière le point d’intégration local
  `api.js` ou `runtime-api.js` de l’extension au lieu de le promouvoir dans
  `openclaw/plugin-sdk/<extension>`.
- Les nouveaux points d’intégration d’assistance partagée doivent être génériques, et non marqués par un canal. L’analyse partagée des cibles
  appartient à `openclaw/plugin-sdk/channel-targets` ; les composants internes spécifiques au canal
  restent derrière le point d’intégration local `api.js` ou `runtime-api.js` du plugin propriétaire.
- Des sous-chemins spécifiques à une capacité tels que `image-generation`,
  `media-understanding` et `speech` existent parce que les plugins bundled/natifs les utilisent
  aujourd’hui. Leur présence ne signifie pas à elle seule que chaque assistant exporté constitue un contrat externe figé à long terme.

## Schémas de l’outil de message

Les plugins doivent posséder les contributions de schéma `describeMessageTool(...)` spécifiques au canal.
Conservez les champs spécifiques au fournisseur dans le plugin, et non dans le cœur partagé.

Pour les fragments de schéma portables partagés, réutilisez les assistants génériques exportés via
`openclaw/plugin-sdk/channel-actions` :

- `createMessageToolButtonsSchema()` pour les charges utiles de style grille de boutons
- `createMessageToolCardSchema()` pour les charges utiles de cartes structurées

Si une forme de schéma n’a de sens que pour un seul fournisseur, définissez-la dans les
sources propres à ce plugin au lieu de la promouvoir dans le SDK partagé.

## Résolution de cible de canal

Les plugins de canal doivent posséder la sémantique de cible spécifique au canal. Gardez l’hôte
sortant partagé générique et utilisez la surface de l’adaptateur de messagerie pour les règles fournisseur :

- `messaging.inferTargetChatType({ to })` décide si une cible normalisée
  doit être traitée comme `direct`, `group` ou `channel` avant la recherche dans l’annuaire.
- `messaging.targetResolver.looksLikeId(raw, normalized)` indique au cœur si une
  entrée doit passer directement à une résolution de type identifiant au lieu d’une recherche dans l’annuaire.
- `messaging.targetResolver.resolveTarget(...)` est le repli du plugin lorsque le
  cœur a besoin d’une résolution finale appartenant au fournisseur après normalisation ou après un
  échec de recherche dans l’annuaire.
- `messaging.resolveOutboundSessionRoute(...)` possède la construction de route de session
  spécifique au fournisseur une fois qu’une cible est résolue.

Répartition recommandée :

- Utilisez `inferTargetChatType` pour les décisions de catégorie qui doivent intervenir avant la
  recherche parmi pairs/groupes.
- Utilisez `looksLikeId` pour les vérifications de type « traiter ceci comme un identifiant de cible explicite/natif ».
- Utilisez `resolveTarget` pour le repli de normalisation spécifique au fournisseur, et non pour une
  recherche large dans l’annuaire.
- Conservez les identifiants natifs du fournisseur comme les identifiants de chat, identifiants de fil, JID, handles et identifiants de salle
  dans les valeurs `target` ou les paramètres spécifiques au fournisseur, pas dans des champs SDK génériques.

## Annuaires adossés à la configuration

Les plugins qui dérivent des entrées d’annuaire à partir de la configuration doivent conserver cette logique dans le
plugin et réutiliser les assistants partagés de
`openclaw/plugin-sdk/directory-runtime`.

Utilisez cela lorsqu’un canal a besoin de pairs/groupes adossés à la configuration tels que :

- pairs de messages privés pilotés par liste d’autorisation
- mappages configurés de canaux/groupes
- replis d’annuaire statiques à portée de compte

Les assistants partagés de `directory-runtime` ne gèrent que les opérations génériques :

- filtrage de requête
- application de limite
- assistants de déduplication/normalisation
- construction de `ChannelDirectoryEntry[]`

L’inspection de compte spécifique au canal et la normalisation des identifiants doivent rester dans
l’implémentation du plugin.

## Catalogues de fournisseurs

Les plugins fournisseurs peuvent définir des catalogues de modèles pour l’inférence avec
`registerProvider({ catalog: { run(...) { ... } } })`.

`catalog.run(...)` renvoie la même forme que celle qu’OpenClaw écrit dans
`models.providers` :

- `{ provider }` pour une entrée de fournisseur
- `{ providers }` pour plusieurs entrées de fournisseur

Utilisez `catalog` lorsque le plugin possède des identifiants de modèle spécifiques au fournisseur, des valeurs par défaut de base URL,
ou des métadonnées de modèle protégées par authentification.

`catalog.order` contrôle le moment où le catalogue d’un plugin fusionne par rapport aux
fournisseurs implicites intégrés d’OpenClaw :

- `simple` : fournisseurs simples pilotés par clé API ou environnement
- `profile` : fournisseurs qui apparaissent lorsque des profils d’authentification existent
- `paired` : fournisseurs qui synthétisent plusieurs entrées de fournisseur liées
- `late` : dernier passage, après les autres fournisseurs implicites

Les fournisseurs plus tardifs l’emportent en cas de collision de clé, ce qui permet aux plugins de remplacer intentionnellement une
entrée de fournisseur intégrée avec le même identifiant de fournisseur.

Compatibilité :

- `discovery` fonctionne toujours comme alias legacy
- si `catalog` et `discovery` sont tous deux enregistrés, OpenClaw utilise `catalog`

## Inspection de canal en lecture seule

Si votre plugin enregistre un canal, préférez implémenter
`plugin.config.inspectAccount(cfg, accountId)` en plus de `resolveAccount(...)`.

Pourquoi :

- `resolveAccount(...)` est le chemin d’exécution. Il peut supposer que les identifiants
  sont entièrement matérialisés et peut échouer rapidement si les secrets requis sont absents.
- Les chemins de commandes en lecture seule tels que `openclaw status`, `openclaw status --all`,
  `openclaw channels status`, `openclaw channels resolve`, ainsi que les flux de réparation doctor/config
  ne doivent pas avoir besoin de matérialiser les identifiants d’exécution juste pour
  décrire la configuration.

Comportement recommandé de `inspectAccount(...)` :

- Renvoyer uniquement un état descriptif du compte.
- Préserver `enabled` et `configured`.
- Inclure les champs de source/statut des identifiants lorsque cela est pertinent, tels que :
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- Vous n’avez pas besoin de renvoyer les valeurs brutes de jeton simplement pour signaler une
  disponibilité en lecture seule. Renvoyer `tokenStatus: "available"` (et le champ source correspondant)
  suffit pour les commandes de type statut.
- Utilisez `configured_unavailable` lorsqu’un identifiant est configuré via SecretRef mais
  indisponible dans le chemin de commande courant.

Cela permet aux commandes en lecture seule d’indiquer « configuré mais indisponible dans ce chemin de commande »
au lieu de planter ou de signaler à tort que le compte n’est pas configuré.

## Packs de packages

Un répertoire de plugin peut inclure un `package.json` avec `openclaw.extensions` :

```json
{
  "name": "my-pack",
  "openclaw": {
    "extensions": ["./src/safety.ts", "./src/tools.ts"],
    "setupEntry": "./src/setup-entry.ts"
  }
}
```

Chaque entrée devient un plugin. Si le pack liste plusieurs extensions, l’identifiant du plugin
devient `name/<fileBase>`.

Si votre plugin importe des dépendances npm, installez-les dans ce répertoire afin que
`node_modules` soit disponible (`npm install` / `pnpm install`).

Garde-fou de sécurité : chaque entrée `openclaw.extensions` doit rester dans le répertoire du plugin
après résolution des liens symboliques. Les entrées qui sortent du répertoire du package sont
rejetées.

Note de sécurité : `openclaw plugins install` installe les dépendances du plugin avec
`npm install --omit=dev --ignore-scripts` (pas de scripts de cycle de vie, pas de dépendances de développement à l’exécution). Gardez les arbres de dépendances des plugins en
« JS/TS pur » et évitez les packages qui nécessitent des compilations `postinstall`.

Facultatif : `openclaw.setupEntry` peut pointer vers un module léger réservé à la configuration.
Lorsque OpenClaw a besoin de surfaces de configuration pour un plugin de canal désactivé, ou
lorsqu’un plugin de canal est activé mais encore non configuré, il charge `setupEntry`
au lieu du point d’entrée complet du plugin. Cela allège le démarrage et la configuration
lorsque le point d’entrée principal de votre plugin connecte aussi des outils, hooks ou tout autre code
réservé à l’exécution.

Facultatif : `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`
peut faire participer un plugin de canal au même chemin `setupEntry` pendant la
phase de démarrage pré-listen de la gateway, même lorsque le canal est déjà configuré.

N’utilisez cela que si `setupEntry` couvre entièrement la surface de démarrage qui doit exister
avant que la gateway commence à écouter. En pratique, cela signifie que le point d’entrée de configuration
doit enregistrer chaque capacité appartenant au canal dont dépend le démarrage, comme :

- l’enregistrement du canal lui-même
- toute route HTTP qui doit être disponible avant que la gateway commence à écouter
- toute méthode gateway, tout outil ou tout service qui doit exister pendant cette même fenêtre

Si votre point d’entrée complet possède encore une capacité de démarrage requise, n’activez pas
ce drapeau. Conservez le comportement par défaut du plugin et laissez OpenClaw charger le
point d’entrée complet pendant le démarrage.

Les canaux bundled peuvent aussi publier des assistants de surface de contrat réservés à la configuration que le cœur
peut consulter avant le chargement de l’exécution complète du canal. La surface actuelle de promotion de configuration est :

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

Le cœur utilise cette surface lorsqu’il doit promouvoir une configuration de canal legacy à compte unique
vers `channels.<id>.accounts.*` sans charger le point d’entrée complet du plugin.
Matrix est l’exemple bundled actuel : il ne déplace que les clés d’authentification/d’amorçage vers un
compte promu nommé lorsque des comptes nommés existent déjà, et il peut préserver une
clé de compte par défaut configurée non canonique au lieu de toujours créer
`accounts.default`.

Ces adaptateurs de patch de configuration maintiennent la découverte de surface de contrat bundled de façon paresseuse. Le temps d’import reste léger ; la surface de promotion n’est chargée qu’au premier usage au lieu de réentrer dans le démarrage du canal bundled à l’import du module.

Lorsque ces surfaces de démarrage incluent des méthodes Gateway RPC, conservez-les sur un
préfixe spécifique au plugin. Les espaces de noms d’administration du cœur (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) restent réservés et se résolvent toujours
vers `operator.admin`, même si un plugin demande une portée plus étroite.

Exemple :

```json
{
  "name": "@scope/my-channel",
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "startup": {
      "deferConfiguredChannelFullLoadUntilAfterListen": true
    }
  }
}
```

### Métadonnées de catalogue de canal

Les plugins de canal peuvent annoncer des métadonnées de configuration/découverte via `openclaw.channel` et
des indications d’installation via `openclaw.install`. Cela permet au catalogue du cœur de rester sans données.

Exemple :

```json
{
  "name": "@openclaw/nextcloud-talk",
  "openclaw": {
    "extensions": ["./index.ts"],
    "channel": {
      "id": "nextcloud-talk",
      "label": "Nextcloud Talk",
      "selectionLabel": "Nextcloud Talk (autohébergé)",
      "docsPath": "/channels/nextcloud-talk",
      "docsLabel": "nextcloud-talk",
      "blurb": "Chat autohébergé via des bots webhook Nextcloud Talk.",
      "order": 65,
      "aliases": ["nc-talk", "nc"]
    },
    "install": {
      "npmSpec": "@openclaw/nextcloud-talk",
      "localPath": "<bundled-plugin-local-path>",
      "defaultChoice": "npm"
    }
  }
}
```

Champs `openclaw.channel` utiles au-delà de l’exemple minimal :

- `detailLabel` : libellé secondaire pour des surfaces plus riches de catalogue/statut
- `docsLabel` : remplace le texte du lien de documentation
- `preferOver` : identifiants de plugin/canal de priorité inférieure que cette entrée de catalogue doit surpasser
- `selectionDocsPrefix`, `selectionDocsOmitLabel`, `selectionExtras` : contrôles de texte de la surface de sélection
- `markdownCapable` : marque le canal comme compatible Markdown pour les décisions de formatage sortant
- `exposure.configured` : masque le canal des surfaces de liste de canaux configurés lorsqu’il est défini sur `false`
- `exposure.setup` : masque le canal des sélecteurs interactifs de configuration lorsqu’il est défini sur `false`
- `exposure.docs` : marque le canal comme interne/privé pour les surfaces de navigation de documentation
- `showConfigured` / `showInSetup` : alias legacy encore acceptés pour compatibilité ; préférez `exposure`
- `quickstartAllowFrom` : fait participer le canal au flux standard `allowFrom` de démarrage rapide
- `forceAccountBinding` : exige une liaison explicite de compte même lorsqu’un seul compte existe
- `preferSessionLookupForAnnounceTarget` : préfère la recherche de session lors de la résolution des cibles d’annonce

OpenClaw peut aussi fusionner des **catalogues de canaux externes** (par exemple, un export de registre MPM).
Déposez un fichier JSON à l’un de ces emplacements :

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

Ou pointez `OPENCLAW_PLUGIN_CATALOG_PATHS` (ou `OPENCLAW_MPM_CATALOG_PATHS`) vers
un ou plusieurs fichiers JSON (délimités par virgule/point-virgule/`PATH`). Chaque fichier doit
contenir `{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }`. L’analyseur accepte aussi `"packages"` ou `"plugins"` comme alias legacy de la clé `"entries"`.

## Plugins de moteur de contexte

Les plugins de moteur de contexte possèdent l’orchestration du contexte de session pour l’ingestion, l’assemblage,
et la compaction. Enregistrez-les depuis votre plugin avec
`api.registerContextEngine(id, factory)`, puis sélectionnez le moteur actif avec
`plugins.slots.contextEngine`.

Utilisez cela lorsque votre plugin a besoin de remplacer ou d’étendre le pipeline de contexte par défaut
plutôt que de simplement ajouter une recherche mémoire ou des hooks.

```ts
import { buildMemorySystemPromptAddition } from "openclaw/plugin-sdk/core";

export default function (api) {
  api.registerContextEngine("lossless-claw", () => ({
    info: { id: "lossless-claw", name: "Lossless Claw", ownsCompaction: true },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages, availableTools, citationsMode }) {
      return {
        messages,
        estimatedTokens: 0,
        systemPromptAddition: buildMemorySystemPromptAddition({
          availableTools: availableTools ?? new Set(),
          citationsMode,
        }),
      };
    },
    async compact() {
      return { ok: true, compacted: false };
    },
  }));
}
```

Si votre moteur ne possède **pas** l’algorithme de compaction, laissez `compact()`
implémenté et déléguez-le explicitement :

```ts
import {
  buildMemorySystemPromptAddition,
  delegateCompactionToRuntime,
} from "openclaw/plugin-sdk/core";

export default function (api) {
  api.registerContextEngine("my-memory-engine", () => ({
    info: {
      id: "my-memory-engine",
      name: "My Memory Engine",
      ownsCompaction: false,
    },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages, availableTools, citationsMode }) {
      return {
        messages,
        estimatedTokens: 0,
        systemPromptAddition: buildMemorySystemPromptAddition({
          availableTools: availableTools ?? new Set(),
          citationsMode,
        }),
      };
    },
    async compact(params) {
      return await delegateCompactionToRuntime(params);
    },
  }));
}
```

## Ajouter une nouvelle capacité

Lorsqu’un plugin a besoin d’un comportement qui ne correspond pas à l’API actuelle, ne contournez pas
le système de plugins avec un accès privé direct. Ajoutez la capacité manquante.

Séquence recommandée :

1. définir le contrat du cœur
   Décidez quel comportement partagé le cœur doit posséder : politique, repli, fusion de configuration,
   cycle de vie, sémantique côté canal et forme de l’assistant d’exécution.
2. ajouter des surfaces typées d’enregistrement/d’exécution des plugins
   Étendez `OpenClawPluginApi` et/ou `api.runtime` avec la plus petite
   surface de capacité typée utile.
3. raccorder le cœur + les consommateurs canal/fonctionnalité
   Les canaux et plugins de fonctionnalité doivent consommer la nouvelle capacité via le cœur,
   et non en important directement une implémentation fournisseur.
4. enregistrer les implémentations fournisseur
   Les plugins fournisseurs enregistrent ensuite leurs backends sur cette capacité.
5. ajouter une couverture de contrat
   Ajoutez des tests afin que la propriété et la forme d’enregistrement restent explicites au fil du temps.

C’est ainsi qu’OpenClaw reste structuré sans devenir codé en dur selon la vision du monde
d’un seul fournisseur. Voir les [Recettes de capacités](/fr/plugins/architecture)
pour une liste concrète de fichiers et un exemple détaillé.

### Liste de contrôle des capacités

Lorsque vous ajoutez une nouvelle capacité, l’implémentation doit généralement toucher ensemble ces
surfaces :

- types de contrat du cœur dans `src/<capability>/types.ts`
- runner du cœur/assistant d’exécution dans `src/<capability>/runtime.ts`
- surface d’enregistrement de l’API des plugins dans `src/plugins/types.ts`
- câblage du registre des plugins dans `src/plugins/registry.ts`
- exposition de l’exécution des plugins dans `src/plugins/runtime/*` lorsque les plugins de fonctionnalité/de canal
  doivent la consommer
- assistants de capture/test dans `src/test-utils/plugin-registration.ts`
- assertions de propriété/de contrat dans `src/plugins/contracts/registry.ts`
- documentation opérateur/plugin dans `docs/`

Si l’une de ces surfaces manque, c’est généralement le signe que la capacité n’est
pas encore entièrement intégrée.

### Modèle de capacité

Motif minimal :

```ts
// contrat du cœur
export type VideoGenerationProviderPlugin = {
  id: string;
  label: string;
  generateVideo: (req: VideoGenerationRequest) => Promise<VideoGenerationResult>;
};

// API du plugin
api.registerVideoGenerationProvider({
  id: "openai",
  label: "OpenAI",
  async generateVideo(req) {
    return await generateOpenAiVideo(req);
  },
});

// assistant d’exécution partagé pour les plugins de fonctionnalité/de canal
const clip = await api.runtime.videoGeneration.generate({
  prompt: "Montre le robot marchant dans le laboratoire.",
  cfg,
});
```

Motif de test de contrat :

```ts
expect(findVideoGenerationProviderIdsForPlugin("openai")).toEqual(["openai"]);
```

Cela garde la règle simple :

- le cœur possède le contrat de capacité + l’orchestration
- les plugins fournisseurs possèdent les implémentations fournisseur
- les plugins de fonctionnalité/de canal consomment les assistants d’exécution
- les tests de contrat gardent une propriété explicite
