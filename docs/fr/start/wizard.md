---
read_when:
    - Exécuter ou configurer l’onboarding CLI
    - Configurer une nouvelle machine
sidebarTitle: 'Onboarding: CLI'
summary: 'Onboarding CLI : configuration guidée pour la gateway, l’espace de travail, les canaux et les Skills'
title: Onboarding (CLI)
x-i18n:
    generated_at: "2026-04-05T10:51:42Z"
    model: gpt-5.4
    provider: openai
    source_hash: 81e33fb4f8be30e7c2c6e0024bf9bdcf48583ca58eaf5fff5afd37a1cd628523
    source_path: start/wizard.md
    workflow: 15
---

# Onboarding (CLI)

L’onboarding CLI est la méthode **recommandée** pour configurer OpenClaw sur macOS,
Linux ou Windows (via WSL2 ; fortement recommandé).
Il configure une Gateway locale ou une connexion à une Gateway distante, ainsi que les canaux, les Skills
et les paramètres par défaut de l’espace de travail dans un seul flux guidé.

```bash
openclaw onboard
```

<Info>
Premier chat le plus rapide : ouvrez la Control UI (aucune configuration de canal n’est nécessaire). Exécutez
`openclaw dashboard` et discutez dans le navigateur. Documentation : [Dashboard](/web/dashboard).
</Info>

Pour reconfigurer plus tard :

```bash
openclaw configure
openclaw agents add <name>
```

<Note>
`--json` n’implique pas le mode non interactif. Pour les scripts, utilisez `--non-interactive`.
</Note>

<Tip>
L’onboarding CLI inclut une étape de recherche web où vous pouvez choisir un fournisseur
comme Brave, DuckDuckGo, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search,
Ollama Web Search, Perplexity, SearXNG ou Tavily. Certains fournisseurs nécessitent une
clé API, tandis que d’autres n’en demandent pas. Vous pouvez aussi configurer cela plus tard avec
`openclaw configure --section web`. Documentation : [Outils web](/tools/web).
</Tip>

## QuickStart vs Avancé

L’onboarding commence par **QuickStart** (par défaut) ou **Avancé** (contrôle complet).

<Tabs>
  <Tab title="QuickStart (par défaut)">
    - Gateway locale (loopback)
    - Espace de travail par défaut (ou espace de travail existant)
    - Port de la Gateway : **18789**
    - Authentification de la Gateway : **Token** (généré automatiquement, même en loopback)
    - Politique d’outils par défaut pour les nouvelles configurations locales : `tools.profile: "coding"` (le profil explicite existant est conservé)
    - Valeur par défaut pour l’isolation des messages privés : l’onboarding local écrit `session.dmScope: "per-channel-peer"` si non défini. Détails : [Référence de configuration CLI](/start/wizard-cli-reference#outputs-and-internals)
    - Exposition Tailscale : **désactivée**
    - Les messages privés Telegram et WhatsApp utilisent par défaut une **liste d’autorisation** (votre numéro de téléphone vous sera demandé)
  </Tab>
  <Tab title="Avancé (contrôle complet)">
    - Expose chaque étape (mode, espace de travail, gateway, canaux, daemon, Skills).
  </Tab>
</Tabs>

## Ce que l’onboarding configure

**Le mode local (par défaut)** vous guide à travers ces étapes :

1. **Modèle/Auth** — choisissez n’importe quel flux fournisseur/authentification pris en charge (clé API, OAuth ou authentification manuelle spécifique au fournisseur), y compris Custom Provider
   (compatible OpenAI, compatible Anthropic ou détection automatique Unknown). Choisissez un modèle par défaut.
   Note de sécurité : si cet agent doit exécuter des outils ou traiter du contenu de webhook/hooks, privilégiez le modèle de dernière génération le plus performant disponible et gardez une politique d’outils stricte. Les niveaux plus faibles ou plus anciens sont plus faciles à manipuler par injection de prompt.
   Pour les exécutions non interactives, `--secret-input-mode ref` stocke des références adossées à des variables d’environnement dans les profils d’authentification au lieu de valeurs de clé API en clair.
   En mode non interactif `ref`, la variable d’environnement du fournisseur doit être définie ; passer des drapeaux de clé en ligne sans cette variable d’environnement échoue immédiatement.
   Dans les exécutions interactives, choisir le mode de référence secrète vous permet de pointer soit vers une variable d’environnement, soit vers une référence fournisseur configurée (`file` ou `exec`), avec une validation préalable rapide avant l’enregistrement.
   Pour Anthropic, l’onboarding/configuration interactif propose **Anthropic Claude CLI** comme solution locale de secours et **Anthropic API key** comme chemin de production recommandé. Anthropic setup-token est également de nouveau disponible comme ancien chemin manuel spécifique à OpenClaw, avec l’attente de facturation **Extra Usage** spécifique à OpenClaw chez Anthropic.
2. **Espace de travail** — emplacement des fichiers de l’agent (par défaut `~/.openclaw/workspace`). Initialise les fichiers d’amorçage.
3. **Gateway** — port, adresse d’écoute, mode d’authentification, exposition Tailscale.
   En mode interactif avec token, choisissez le stockage par défaut du token en clair ou optez pour SecretRef.
   Chemin SecretRef du token en mode non interactif : `--gateway-token-ref-env <ENV_VAR>`.
4. **Canaux** — canaux de chat intégrés et groupés tels que BlueBubbles, Discord, Feishu, Google Chat, Mattermost, Microsoft Teams, QQ Bot, Signal, Slack, Telegram, WhatsApp, etc.
5. **Daemon** — installe un LaunchAgent (macOS), une unité utilisateur systemd (Linux/WSL2) ou une tâche planifiée Windows native avec repli par utilisateur vers le dossier de démarrage.
   Si l’authentification par token nécessite un token et que `gateway.auth.token` est géré par SecretRef, l’installation du daemon le valide mais ne persiste pas le token résolu dans les métadonnées d’environnement du service superviseur.
   Si l’authentification par token nécessite un token et que le SecretRef de token configuré n’est pas résolu, l’installation du daemon est bloquée avec des instructions exploitables.
   Si `gateway.auth.token` et `gateway.auth.password` sont tous deux configurés et que `gateway.auth.mode` n’est pas défini, l’installation du daemon est bloquée jusqu’à ce que le mode soit défini explicitement.
6. **Contrôle de santé** — démarre la Gateway et vérifie qu’elle fonctionne.
7. **Skills** — installe les Skills recommandées et les dépendances facultatives.

<Note>
Relancer l’onboarding **n’efface rien** sauf si vous choisissez explicitement **Reset** (ou passez `--reset`).
CLI `--reset` cible par défaut la configuration, les identifiants et les sessions ; utilisez `--reset-scope full` pour inclure l’espace de travail.
Si la configuration est invalide ou contient des clés héritées, l’onboarding vous demande d’exécuter d’abord `openclaw doctor`.
</Note>

**Le mode distant** configure uniquement le client local pour se connecter à une Gateway ailleurs.
Il **n’installe ni ne modifie rien** sur l’hôte distant.

## Ajouter un autre agent

Utilisez `openclaw agents add <name>` pour créer un agent distinct avec son propre espace de travail,
ses sessions et ses profils d’authentification. Une exécution sans `--workspace` lance l’onboarding.

Ce qu’il définit :

- `agents.list[].name`
- `agents.list[].workspace`
- `agents.list[].agentDir`

Remarques :

- Les espaces de travail par défaut suivent `~/.openclaw/workspace-<agentId>`.
- Ajoutez `bindings` pour acheminer les messages entrants (l’onboarding peut le faire).
- Drapeaux non interactifs : `--model`, `--agent-dir`, `--bind`, `--non-interactive`.

## Référence complète

Pour des descriptions détaillées étape par étape et les sorties de configuration, voir
[Référence de configuration CLI](/start/wizard-cli-reference).
Pour des exemples non interactifs, voir [Automatisation CLI](/start/wizard-cli-automation).
Pour la référence technique plus approfondie, y compris les détails RPC, voir
[Référence d’onboarding](/reference/wizard).

## Documentation associée

- Référence des commandes CLI : [`openclaw onboard`](/cli/onboard)
- Vue d’ensemble de l’onboarding : [Vue d’ensemble de l’onboarding](/start/onboarding-overview)
- Onboarding de l’app macOS : [Onboarding](/start/onboarding)
- Rituel de premier démarrage de l’agent : [Amorçage de l’agent](/start/bootstrapping)
