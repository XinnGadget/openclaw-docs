---
read_when:
    - Recherche d’une étape ou d’un drapeau d’onboarding spécifique
    - Automatiser l’onboarding avec le mode non interactif
    - Déboguer le comportement de l’onboarding
sidebarTitle: Onboarding Reference
summary: 'Référence complète pour l’onboarding de la CLI : chaque étape, drapeau et champ de configuration'
title: Référence d’onboarding
x-i18n:
    generated_at: "2026-04-15T14:40:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1db3ff789422617634e6624f9d12c18b6a6c573721226b9c0fa6f6b7956ef33d
    source_path: reference/wizard.md
    workflow: 15
---

# Référence d’onboarding

Voici la référence complète de `openclaw onboard`.
Pour une vue d’ensemble de haut niveau, consultez [Onboarding (CLI)](/fr/start/wizard).

## Détails du flux (mode local)

<Steps>
  <Step title="Détection de la configuration existante">
    - Si `~/.openclaw/openclaw.json` existe, choisissez **Conserver / Modifier / Réinitialiser**.
    - Relancer l’onboarding n’efface **rien** à moins que vous choisissiez explicitement **Réinitialiser**
      (ou que vous passiez `--reset`).
    - Le drapeau CLI `--reset` utilise par défaut `config+creds+sessions` ; utilisez `--reset-scope full`
      pour supprimer également l’espace de travail.
    - Si la configuration est invalide ou contient des clés héritées, l’assistant s’arrête et vous demande
      d’exécuter `openclaw doctor` avant de continuer.
    - La réinitialisation utilise `trash` (jamais `rm`) et propose les portées suivantes :
      - Configuration uniquement
      - Configuration + identifiants + sessions
      - Réinitialisation complète (supprime aussi l’espace de travail)
  </Step>
  <Step title="Modèle/Auth">
    - **Clé API Anthropic** : utilise `ANTHROPIC_API_KEY` si présent ou demande une clé, puis l’enregistre pour l’utilisation du daemon.
    - **Clé API Anthropic** : choix d’assistant Anthropic privilégié dans l’onboarding/configuration.
    - **Jeton de configuration Anthropic** : toujours disponible dans l’onboarding/configuration, bien qu’OpenClaw préfère désormais la réutilisation de Claude CLI lorsqu’elle est disponible.
    - **Abonnement OpenAI Code (Codex) (Codex CLI)** : si `~/.codex/auth.json` existe, l’onboarding peut le réutiliser. Les identifiants Codex CLI réutilisés restent gérés par Codex CLI ; à l’expiration, OpenClaw relit d’abord cette source et, lorsque le fournisseur peut les actualiser, écrit l’identifiant actualisé dans le stockage Codex au lieu d’en prendre lui-même la gestion.
    - **Abonnement OpenAI Code (Codex) (OAuth)** : flux navigateur ; collez le `code#state`.
      - Définit `agents.defaults.model` sur `openai-codex/gpt-5.4` lorsque le modèle n’est pas défini ou vaut `openai/*`.
    - **Clé API OpenAI** : utilise `OPENAI_API_KEY` si présent ou demande une clé, puis la stocke dans les profils d’authentification.
      - Définit `agents.defaults.model` sur `openai/gpt-5.4` lorsque le modèle n’est pas défini, vaut `openai/*` ou `openai-codex/*`.
    - **Clé API xAI (Grok)** : demande `XAI_API_KEY` et configure xAI comme fournisseur de modèle.
    - **OpenCode** : demande `OPENCODE_API_KEY` (ou `OPENCODE_ZEN_API_KEY`, à obtenir sur https://opencode.ai/auth) et vous permet de choisir le catalogue Zen ou Go.
    - **Ollama** : propose d’abord **Cloud + Local**, **Cloud only** ou **Local only**. `Cloud only` demande `OLLAMA_API_KEY` et utilise `https://ollama.com` ; les modes adossés à l’hôte demandent l’URL de base Ollama, détectent les modèles disponibles et récupèrent automatiquement le modèle local sélectionné si nécessaire ; `Cloud + Local` vérifie aussi si cet hôte Ollama est connecté pour l’accès cloud.
    - Plus de détails : [Ollama](/fr/providers/ollama)
    - **Clé API** : stocke la clé pour vous.
    - **Vercel AI Gateway (proxy multi-modèles)** : demande `AI_GATEWAY_API_KEY`.
    - Plus de détails : [Vercel AI Gateway](/fr/providers/vercel-ai-gateway)
    - **Cloudflare AI Gateway** : demande l’ID de compte, l’ID Gateway et `CLOUDFLARE_AI_GATEWAY_API_KEY`.
    - Plus de détails : [Cloudflare AI Gateway](/fr/providers/cloudflare-ai-gateway)
    - **MiniMax** : la configuration est écrite automatiquement ; le modèle hébergé par défaut est `MiniMax-M2.7`.
      La configuration par clé API utilise `minimax/...`, et la configuration OAuth utilise
      `minimax-portal/...`.
    - Plus de détails : [MiniMax](/fr/providers/minimax)
    - **StepFun** : la configuration est écrite automatiquement pour StepFun standard ou Step Plan sur les points de terminaison Chine ou globaux.
    - La version standard inclut actuellement `step-3.5-flash`, et Step Plan inclut également `step-3.5-flash-2603`.
    - Plus de détails : [StepFun](/fr/providers/stepfun)
    - **Synthetic (compatible Anthropic)** : demande `SYNTHETIC_API_KEY`.
    - Plus de détails : [Synthetic](/fr/providers/synthetic)
    - **Moonshot (Kimi K2)** : la configuration est écrite automatiquement.
    - **Kimi Coding** : la configuration est écrite automatiquement.
    - Plus de détails : [Moonshot AI (Kimi + Kimi Coding)](/fr/providers/moonshot)
    - **Ignorer** : aucune authentification n’est encore configurée.
    - Choisissez un modèle par défaut parmi les options détectées (ou saisissez manuellement provider/model). Pour une qualité optimale et un risque plus faible d’injection de prompt, choisissez le modèle le plus puissant et de dernière génération disponible dans votre pile de fournisseurs.
    - L’onboarding exécute une vérification du modèle et affiche un avertissement si le modèle configuré est inconnu ou si l’authentification manque.
    - Le mode de stockage des clés API utilise par défaut des valeurs de profils d’authentification en texte brut. Utilisez `--secret-input-mode ref` pour stocker à la place des références adossées à l’environnement (par exemple `keyRef: { source: "env", provider: "default", id: "OPENAI_API_KEY" }`).
    - Les profils d’authentification se trouvent dans `~/.openclaw/agents/<agentId>/agent/auth-profiles.json` (clés API + OAuth). `~/.openclaw/credentials/oauth.json` est un mécanisme hérité réservé à l’importation.
    - Plus de détails : [/concepts/oauth](/fr/concepts/oauth)
    <Note>
    Astuce pour les environnements headless/serveur : terminez OAuth sur une machine disposant d’un navigateur, puis copiez
    le `auth-profiles.json` de cet agent (par exemple
    `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`, ou le chemin
    correspondant sous `$OPENCLAW_STATE_DIR/...`) vers l’hôte Gateway. `credentials/oauth.json`
    n’est qu’une source d’importation héritée.
    </Note>
  </Step>
  <Step title="Espace de travail">
    - Valeur par défaut : `~/.openclaw/workspace` (configurable).
    - Initialise les fichiers d’espace de travail nécessaires au rituel de bootstrap de l’agent.
    - Disposition complète de l’espace de travail + guide de sauvegarde : [Espace de travail de l’agent](/fr/concepts/agent-workspace)
  </Step>
  <Step title="Gateway">
    - Port, bind, mode d’authentification, exposition Tailscale.
    - Recommandation d’authentification : conservez **Token** même pour loopback afin que les clients WS locaux doivent s’authentifier.
    - En mode token, la configuration interactive propose :
      - **Générer/stocker un token en texte brut** (par défaut)
      - **Utiliser SecretRef** (optionnel)
      - Quickstart réutilise les SecretRef `gateway.auth.token` existants sur les fournisseurs `env`, `file` et `exec` pour le bootstrap de la sonde d’onboarding/du tableau de bord.
      - Si ce SecretRef est configuré mais ne peut pas être résolu, l’onboarding échoue tôt avec un message de correction clair au lieu de dégrader silencieusement l’authentification à l’exécution.
    - En mode mot de passe, la configuration interactive prend également en charge le stockage en texte brut ou via SecretRef.
    - Chemin SecretRef de token non interactif : `--gateway-token-ref-env <ENV_VAR>`.
      - Nécessite une variable d’environnement non vide dans l’environnement du processus d’onboarding.
      - Ne peut pas être combiné avec `--gateway-token`.
    - Désactivez l’authentification uniquement si vous faites entièrement confiance à chaque processus local.
    - Les binds non loopback exigent toujours une authentification.
  </Step>
  <Step title="Canaux">
    - [WhatsApp](/fr/channels/whatsapp) : connexion par QR facultative.
    - [Telegram](/fr/channels/telegram) : token de bot.
    - [Discord](/fr/channels/discord) : token de bot.
    - [Google Chat](/fr/channels/googlechat) : JSON de compte de service + audience Webhook.
    - [Mattermost](/fr/channels/mattermost) (Plugin) : token de bot + URL de base.
    - [Signal](/fr/channels/signal) : installation facultative de `signal-cli` + configuration du compte.
    - [BlueBubbles](/fr/channels/bluebubbles) : **recommandé pour iMessage** ; URL du serveur + mot de passe + webhook.
    - [iMessage](/fr/channels/imessage) : chemin CLI `imsg` hérité + accès à la base de données.
    - Sécurité des DM : l’appairage est le mode par défaut. Le premier DM envoie un code ; approuvez-le via `openclaw pairing approve <channel> <code>` ou utilisez des listes d’autorisation.
  </Step>
  <Step title="Recherche web">
    - Choisissez un fournisseur pris en charge comme Brave, DuckDuckGo, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search, Ollama Web Search, Perplexity, SearXNG ou Tavily (ou ignorez cette étape).
    - Les fournisseurs adossés à une API peuvent utiliser des variables d’environnement ou une configuration existante pour une configuration rapide ; les fournisseurs sans clé utilisent à la place leurs prérequis spécifiques.
    - Ignorez avec `--skip-search`.
    - Configurez plus tard : `openclaw configure --section web`.
  </Step>
  <Step title="Installation du daemon">
    - macOS : LaunchAgent
      - Nécessite une session utilisateur connectée ; pour un environnement headless, utilisez un LaunchDaemon personnalisé (non fourni).
    - Linux (et Windows via WSL2) : unité utilisateur systemd
      - L’onboarding tente d’activer le lingering via `loginctl enable-linger <user>` afin que la Gateway reste active après la déconnexion.
      - Peut demander sudo (écriture dans `/var/lib/systemd/linger`) ; il essaie d’abord sans sudo.
    - **Sélection du runtime :** Node (recommandé ; requis pour WhatsApp/Telegram). Bun est **déconseillé**.
    - Si l’authentification par token exige un token et que `gateway.auth.token` est géré par SecretRef, l’installation du daemon le valide mais ne persiste pas les valeurs de token en texte brut résolues dans les métadonnées d’environnement du service superviseur.
    - Si l’authentification par token exige un token et que le SecretRef de token configuré n’est pas résolu, l’installation du daemon est bloquée avec des instructions exploitables.
    - Si `gateway.auth.token` et `gateway.auth.password` sont tous deux configurés et que `gateway.auth.mode` n’est pas défini, l’installation du daemon est bloquée jusqu’à ce que le mode soit explicitement défini.
  </Step>
  <Step title="Vérification de l’état de santé">
    - Démarre la Gateway (si nécessaire) et exécute `openclaw health`.
    - Astuce : `openclaw status --deep` ajoute la sonde d’état de santé de la Gateway en direct à la sortie d’état, y compris les sondes de canaux lorsque prises en charge (nécessite une Gateway accessible).
  </Step>
  <Step title="Skills (recommandé)">
    - Lit les Skills disponibles et vérifie les prérequis.
    - Vous permet de choisir un gestionnaire Node : **npm / pnpm** (bun est déconseillé).
    - Installe les dépendances facultatives (certaines utilisent Homebrew sur macOS).
  </Step>
  <Step title="Fin">
    - Résumé + prochaines étapes, y compris les applications iOS/Android/macOS pour des fonctionnalités supplémentaires.
  </Step>
</Steps>

<Note>
Si aucune interface graphique n’est détectée, l’onboarding affiche des instructions de redirection de port SSH pour l’interface de contrôle au lieu d’ouvrir un navigateur.
Si les ressources de l’interface de contrôle sont absentes, l’onboarding tente de les construire ; la solution de repli est `pnpm ui:build` (installe automatiquement les dépendances de l’interface).
</Note>

## Mode non interactif

Utilisez `--non-interactive` pour automatiser ou scriptiser l’onboarding :

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice apiKey \
  --anthropic-api-key "$ANTHROPIC_API_KEY" \
  --gateway-port 18789 \
  --gateway-bind loopback \
  --install-daemon \
  --daemon-runtime node \
  --skip-skills
```

Ajoutez `--json` pour obtenir un résumé lisible par machine.

Token Gateway SecretRef en mode non interactif :

```bash
export OPENCLAW_GATEWAY_TOKEN="your-token"
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice skip \
  --gateway-auth token \
  --gateway-token-ref-env OPENCLAW_GATEWAY_TOKEN
```

`--gateway-token` et `--gateway-token-ref-env` s’excluent mutuellement.

<Note>
`--json` n’implique **pas** le mode non interactif. Utilisez `--non-interactive` (et `--workspace`) pour les scripts.
</Note>

Des exemples de commandes spécifiques aux fournisseurs se trouvent dans [Automatisation CLI](/fr/start/wizard-cli-automation#provider-specific-examples).
Utilisez cette page de référence pour la sémantique des drapeaux et l’ordre des étapes.

### Ajouter un agent (mode non interactif)

```bash
openclaw agents add work \
  --workspace ~/.openclaw/workspace-work \
  --model openai/gpt-5.4 \
  --bind whatsapp:biz \
  --non-interactive \
  --json
```

## RPC de l’assistant Gateway

La Gateway expose le flux d’onboarding via RPC (`wizard.start`, `wizard.next`, `wizard.cancel`, `wizard.status`).
Les clients (application macOS, interface de contrôle) peuvent afficher les étapes sans réimplémenter la logique d’onboarding.

## Configuration de Signal (`signal-cli`)

L’onboarding peut installer `signal-cli` depuis les releases GitHub :

- Télécharge la ressource de release appropriée.
- La stocke sous `~/.openclaw/tools/signal-cli/<version>/`.
- Écrit `channels.signal.cliPath` dans votre configuration.

Remarques :

- Les builds JVM nécessitent **Java 21**.
- Les builds natives sont utilisées lorsqu’elles sont disponibles.
- Windows utilise WSL2 ; l’installation de signal-cli suit le flux Linux à l’intérieur de WSL.

## Ce que l’assistant écrit

Champs typiques dans `~/.openclaw/openclaw.json` :

- `agents.defaults.workspace`
- `agents.defaults.model` / `models.providers` (si MiniMax est choisi)
- `tools.profile` (l’onboarding local utilise par défaut `"coding"` lorsqu’il n’est pas défini ; les valeurs explicites existantes sont conservées)
- `gateway.*` (mode, bind, auth, tailscale)
- `session.dmScope` (détails du comportement : [Référence de configuration CLI](/fr/start/wizard-cli-reference#outputs-and-internals))
- `channels.telegram.botToken`, `channels.discord.token`, `channels.matrix.*`, `channels.signal.*`, `channels.imessage.*`
- Listes d’autorisation de canaux (Slack/Discord/Matrix/Microsoft Teams) lorsque vous activez cette option pendant les invites (les noms sont résolus en ID lorsque c’est possible).
- `skills.install.nodeManager`
  - `setup --node-manager` accepte `npm`, `pnpm` ou `bun`.
  - La configuration manuelle peut toujours utiliser `yarn` en définissant directement `skills.install.nodeManager`.
- `wizard.lastRunAt`
- `wizard.lastRunVersion`
- `wizard.lastRunCommit`
- `wizard.lastRunCommand`
- `wizard.lastRunMode`

`openclaw agents add` écrit dans `agents.list[]` et `bindings` en option.

Les identifiants WhatsApp sont stockés sous `~/.openclaw/credentials/whatsapp/<accountId>/`.
Les sessions sont stockées sous `~/.openclaw/agents/<agentId>/sessions/`.

Certains canaux sont fournis sous forme de plugins. Lorsque vous en choisissez un pendant la configuration, l’onboarding
vous invitera à l’installer (npm ou un chemin local) avant qu’il puisse être configuré.

## Documentation associée

- Vue d’ensemble de l’onboarding : [Onboarding (CLI)](/fr/start/wizard)
- Onboarding de l’application macOS : [Onboarding](/fr/start/onboarding)
- Référence de configuration : [Configuration de la Gateway](/fr/gateway/configuration)
- Fournisseurs : [WhatsApp](/fr/channels/whatsapp), [Telegram](/fr/channels/telegram), [Discord](/fr/channels/discord), [Google Chat](/fr/channels/googlechat), [Signal](/fr/channels/signal), [BlueBubbles](/fr/channels/bluebubbles) (iMessage), [iMessage](/fr/channels/imessage) (hérité)
- Skills : [Skills](/fr/tools/skills), [Configuration des Skills](/fr/tools/skills-config)
