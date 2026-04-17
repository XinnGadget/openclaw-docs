---
read_when:
    - Répondre aux questions fréquentes sur la configuration, l’installation, l’intégration initiale ou le support à l’exécution
    - Trier les problèmes signalés par les utilisateurs avant un débogage plus approfondi
summary: Questions fréquentes sur l’installation, la configuration et l’utilisation d’OpenClaw
title: FAQ
x-i18n:
    generated_at: "2026-04-12T23:28:36Z"
    model: gpt-5.4
    provider: openai
    source_hash: d2a78d0fea9596625cc2753e6dc8cc42c2379a3a0c91729265eee0261fe53eaa
    source_path: help/faq.md
    workflow: 15
---

# FAQ

Réponses rapides ainsi qu’un dépannage plus approfondi pour des configurations réelles (développement local, VPS, multi-agent, OAuth/clés API, bascule de modèle). Pour les diagnostics d’exécution, consultez [Troubleshooting](/fr/gateway/troubleshooting). Pour la référence complète de configuration, consultez [Configuration](/fr/gateway/configuration).

## Les 60 premières secondes si quelque chose est cassé

1. **Statut rapide (première vérification)**

   ```bash
   openclaw status
   ```

   Résumé local rapide : OS + mise à jour, accessibilité de la Gateway/du service, agents/sessions, configuration des fournisseurs + problèmes d’exécution (lorsque la Gateway est accessible).

2. **Rapport prêt à partager (sans risque)**

   ```bash
   openclaw status --all
   ```

   Diagnostic en lecture seule avec fin de journal (tokens masqués).

3. **État du daemon + du port**

   ```bash
   openclaw gateway status
   ```

   Affiche l’exécution du superviseur par rapport à l’accessibilité RPC, l’URL cible du probe et la configuration probablement utilisée par le service.

4. **Probes approfondis**

   ```bash
   openclaw status --deep
   ```

   Exécute un probe de santé actif de la Gateway, y compris des probes de canal lorsque pris en charge
   (nécessite une Gateway accessible). Consultez [Health](/fr/gateway/health).

5. **Suivre le journal le plus récent**

   ```bash
   openclaw logs --follow
   ```

   Si le RPC est indisponible, utilisez à la place :

   ```bash
   tail -f "$(ls -t /tmp/openclaw/openclaw-*.log | head -1)"
   ```

   Les journaux de fichiers sont distincts des journaux du service ; consultez [Logging](/fr/logging) et [Troubleshooting](/fr/gateway/troubleshooting).

6. **Exécuter le doctor (réparations)**

   ```bash
   openclaw doctor
   ```

   Répare/migre la configuration et l’état + exécute des vérifications de santé. Consultez [Doctor](/fr/gateway/doctor).

7. **Instantané de la Gateway**

   ```bash
   openclaw health --json
   openclaw health --verbose   # affiche l’URL cible + le chemin de configuration en cas d’erreur
   ```

   Demande à la Gateway en cours d’exécution un instantané complet (WS uniquement). Consultez [Health](/fr/gateway/health).

## Démarrage rapide et configuration initiale

<AccordionGroup>
  <Accordion title="Je suis bloqué, quel est le moyen le plus rapide de me débloquer ?">
    Utilisez un agent IA local qui peut **voir votre machine**. C’est beaucoup plus efficace que de demander
    sur Discord, car la plupart des cas de type « je suis bloqué » sont des **problèmes locaux de configuration ou d’environnement**
    que des personnes à distance ne peuvent pas inspecter.

    - **Claude Code** : [https://www.anthropic.com/claude-code/](https://www.anthropic.com/claude-code/)
    - **OpenAI Codex** : [https://openai.com/codex/](https://openai.com/codex/)

    Ces outils peuvent lire le dépôt, exécuter des commandes, inspecter les journaux et aider à corriger votre configuration
    au niveau machine (PATH, services, permissions, fichiers d’authentification). Donnez-leur la **copie complète du code source**
    via l’installation hackable (git) :

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Cela installe OpenClaw **à partir d’une copie git**, afin que l’agent puisse lire le code + la documentation et
    raisonner sur la version exacte que vous utilisez. Vous pourrez toujours revenir à la version stable plus tard
    en relançant l’installateur sans `--install-method git`.

    Conseil : demandez à l’agent de **planifier et superviser** la correction (étape par étape), puis d’exécuter uniquement les
    commandes nécessaires. Cela limite les changements et les rend plus faciles à auditer.

    Si vous découvrez un vrai bug ou un correctif, veuillez ouvrir une GitHub issue ou envoyer une PR :
    [https://github.com/openclaw/openclaw/issues](https://github.com/openclaw/openclaw/issues)
    [https://github.com/openclaw/openclaw/pulls](https://github.com/openclaw/openclaw/pulls)

    Commencez par ces commandes (partagez les sorties lorsque vous demandez de l’aide) :

    ```bash
    openclaw status
    openclaw models status
    openclaw doctor
    ```

    Ce qu’elles font :

    - `openclaw status` : instantané rapide de la santé de la Gateway/de l’agent + configuration de base.
    - `openclaw models status` : vérifie l’authentification des fournisseurs + la disponibilité des modèles.
    - `openclaw doctor` : valide et répare les problèmes courants de configuration/d’état.

    Autres vérifications CLI utiles : `openclaw status --all`, `openclaw logs --follow`,
    `openclaw gateway status`, `openclaw health --verbose`.

    Boucle de débogage rapide : [Les 60 premières secondes si quelque chose est cassé](#les-60-premières-secondes-si-quelque-chose-est-cassé).
    Documentation d’installation : [Install](/fr/install), [Installer flags](/fr/install/installer), [Updating](/fr/install/updating).

  </Accordion>

  <Accordion title="Heartbeat est constamment ignoré. Que signifient les raisons d’ignorance ?">
    Raisons courantes pour lesquelles Heartbeat est ignoré :

    - `quiet-hours` : en dehors de la fenêtre `active-hours` configurée
    - `empty-heartbeat-file` : `HEARTBEAT.md` existe mais ne contient qu’une structure vide ou uniquement des en-têtes
    - `no-tasks-due` : le mode tâche de `HEARTBEAT.md` est actif, mais aucun intervalle de tâche n’est encore arrivé à échéance
    - `alerts-disabled` : toute la visibilité de Heartbeat est désactivée (`showOk`, `showAlerts` et `useIndicator` sont tous désactivés)

    En mode tâche, les horodatages d’échéance ne sont avancés qu’après l’achèvement
    d’une véritable exécution de Heartbeat. Les exécutions ignorées ne marquent pas les tâches comme terminées.

    Documentation : [Heartbeat](/fr/gateway/heartbeat), [Automation & Tasks](/fr/automation).

  </Accordion>

  <Accordion title="Méthode recommandée pour installer et configurer OpenClaw">
    Le dépôt recommande une exécution depuis les sources et l’utilisation de l’onboarding :

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash
    openclaw onboard --install-daemon
    ```

    L’assistant peut aussi construire automatiquement les ressources UI. Après l’onboarding, vous exécutez généralement la Gateway sur le port **18789**.

    Depuis les sources (contributeurs/développement) :

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    pnpm ui:build # installe automatiquement les dépendances UI au premier lancement
    openclaw onboard
    ```

    Si vous n’avez pas encore d’installation globale, exécutez-le via `pnpm openclaw onboard`.

  </Accordion>

  <Accordion title="Comment ouvrir le tableau de bord après l’onboarding ?">
    L’assistant ouvre votre navigateur avec une URL de tableau de bord propre (sans token) juste après l’onboarding et affiche aussi le lien dans le résumé. Gardez cet onglet ouvert ; s’il ne s’est pas lancé, copiez/collez l’URL affichée sur la même machine.
  </Accordion>

  <Accordion title="Comment authentifier le tableau de bord sur localhost ou à distance ?">
    **Localhost (même machine) :**

    - Ouvrez `http://127.0.0.1:18789/`.
    - S’il demande une authentification par secret partagé, collez le token ou le mot de passe configuré dans les paramètres du Control UI.
    - Source du token : `gateway.auth.token` (ou `OPENCLAW_GATEWAY_TOKEN`).
    - Source du mot de passe : `gateway.auth.password` (ou `OPENCLAW_GATEWAY_PASSWORD`).
    - Si aucun secret partagé n’est encore configuré, générez un token avec `openclaw doctor --generate-gateway-token`.

    **Pas sur localhost :**

    - **Tailscale Serve** (recommandé) : conservez le bind loopback, exécutez `openclaw gateway --tailscale serve`, ouvrez `https://<magicdns>/`. Si `gateway.auth.allowTailscale` vaut `true`, les en-têtes d’identité satisfont l’authentification de Control UI/WebSocket (pas de secret partagé à coller, en supposant un hôte Gateway de confiance) ; les API HTTP nécessitent toujours une authentification par secret partagé, sauf si vous utilisez délibérément `none` pour l’ingress privé ou l’authentification HTTP par proxy de confiance.
      Les tentatives concurrentes d’authentification Serve erronées depuis le même client sont sérialisées avant que le limiteur d’échecs d’authentification ne les enregistre, donc le second mauvais nouvel essai peut déjà afficher `retry later`.
    - **Bind tailnet** : exécutez `openclaw gateway --bind tailnet --token "<token>"` (ou configurez une authentification par mot de passe), ouvrez `http://<tailscale-ip>:18789/`, puis collez le secret partagé correspondant dans les paramètres du tableau de bord.
    - **Reverse proxy tenant compte de l’identité** : conservez la Gateway derrière un proxy de confiance non loopback, configurez `gateway.auth.mode: "trusted-proxy"`, puis ouvrez l’URL du proxy.
    - **Tunnel SSH** : `ssh -N -L 18789:127.0.0.1:18789 user@host` puis ouvrez `http://127.0.0.1:18789/`. L’authentification par secret partagé s’applique toujours à travers le tunnel ; collez le token ou le mot de passe configuré si demandé.

    Consultez [Dashboard](/web/dashboard) et [Web surfaces](/web) pour les modes de bind et les détails d’authentification.

  </Accordion>

  <Accordion title="Pourquoi existe-t-il deux configurations d’approbation exec pour les approbations par chat ?">
    Elles contrôlent des couches différentes :

    - `approvals.exec` : transmet les invites d’approbation vers les destinations de chat
    - `channels.<channel>.execApprovals` : fait de ce canal un client d’approbation natif pour les approbations exec

    La politique exec de l’hôte reste la véritable barrière d’approbation. La configuration du chat contrôle seulement où les invites d’approbation
    apparaissent et comment les personnes peuvent y répondre.

    Dans la plupart des configurations, vous n’avez **pas** besoin des deux :

    - Si le chat prend déjà en charge les commandes et les réponses, `/approve` dans le même chat fonctionne via le chemin partagé.
    - Si un canal natif pris en charge peut déduire les approbateurs en toute sécurité, OpenClaw active désormais automatiquement les approbations natives DM-first lorsque `channels.<channel>.execApprovals.enabled` est non défini ou vaut `"auto"`.
    - Lorsque des cartes/boutons d’approbation natifs sont disponibles, cette UI native est le chemin principal ; l’agent ne doit inclure une commande manuelle `/approve` que si le résultat de l’outil indique que les approbations par chat ne sont pas disponibles ou que l’approbation manuelle est le seul chemin possible.
    - Utilisez `approvals.exec` uniquement si les invites doivent également être transmises à d’autres chats ou à des salons d’opérations explicites.
    - Utilisez `channels.<channel>.execApprovals.target: "channel"` ou `"both"` uniquement si vous voulez explicitement que les invites d’approbation soient republiées dans le salon/sujet d’origine.
    - Les approbations de Plugin sont encore distinctes : elles utilisent par défaut `/approve` dans le même chat, la transmission facultative `approvals.plugin`, et seuls certains canaux natifs conservent en plus une gestion native des approbations de Plugin.

    Version courte : la transmission sert au routage, la configuration du client natif sert à une UX plus riche spécifique au canal.
    Consultez [Exec Approvals](/fr/tools/exec-approvals).

  </Accordion>

  <Accordion title="De quel runtime ai-je besoin ?">
    Node **>= 22** est requis. `pnpm` est recommandé. Bun est **non recommandé** pour la Gateway.
  </Accordion>

  <Accordion title="Est-ce que cela fonctionne sur Raspberry Pi ?">
    Oui. La Gateway est légère : la documentation indique que **512MB-1GB de RAM**, **1 cœur**, et environ **500MB**
    de disque suffisent pour un usage personnel, et précise qu’un **Raspberry Pi 4 peut l’exécuter**.

    Si vous voulez plus de marge (journaux, médias, autres services), **2GB sont recommandés**, mais ce
    n’est pas un minimum strict.

    Conseil : un petit Pi/VPS peut héberger la Gateway, et vous pouvez associer des **Node** sur votre ordinateur/téléphone pour
    l’écran/la caméra/le canvas local ou l’exécution de commandes. Consultez [Nodes](/fr/nodes).

  </Accordion>

  <Accordion title="Des conseils pour les installations sur Raspberry Pi ?">
    Version courte : cela fonctionne, mais attendez-vous à quelques aspérités.

    - Utilisez un OS **64 bits** et conservez Node >= 22.
    - Préférez l’**installation hackable (git)** afin de pouvoir voir les journaux et mettre à jour rapidement.
    - Commencez sans canaux/Skills, puis ajoutez-les un par un.
    - Si vous rencontrez d’étranges problèmes binaires, il s’agit généralement d’un problème de **compatibilité ARM**.

    Documentation : [Linux](/fr/platforms/linux), [Install](/fr/install).

  </Accordion>

  <Accordion title="C’est bloqué sur wake up my friend / l’onboarding ne démarre pas. Que faire ?">
    Cet écran dépend du fait que la Gateway soit accessible et authentifiée. Le TUI envoie aussi
    automatiquement « Wake up, my friend! » au premier lancement. Si vous voyez cette ligne sans **aucune réponse**
    et que les tokens restent à 0, l’agent ne s’est jamais exécuté.

    1. Redémarrez la Gateway :

    ```bash
    openclaw gateway restart
    ```

    2. Vérifiez le statut + l’authentification :

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    3. Si cela reste bloqué, exécutez :

    ```bash
    openclaw doctor
    ```

    Si la Gateway est distante, assurez-vous que la connexion tunnel/Tailscale est active et que l’UI
    pointe vers la bonne Gateway. Consultez [Remote access](/fr/gateway/remote).

  </Accordion>

  <Accordion title="Puis-je migrer ma configuration vers une nouvelle machine (Mac mini) sans refaire l’onboarding ?">
    Oui. Copiez le **répertoire d’état** et le **workspace**, puis exécutez Doctor une fois. Cela
    conserve votre bot « exactement identique » (mémoire, historique de session, authentification et
    état des canaux) tant que vous copiez **ces deux** emplacements :

    1. Installez OpenClaw sur la nouvelle machine.
    2. Copiez `$OPENCLAW_STATE_DIR` (par défaut : `~/.openclaw`) depuis l’ancienne machine.
    3. Copiez votre workspace (par défaut : `~/.openclaw/workspace`).
    4. Exécutez `openclaw doctor` et redémarrez le service Gateway.

    Cela préserve la configuration, les profils d’authentification, les identifiants WhatsApp, les sessions et la mémoire. Si vous êtes en
    mode distant, n’oubliez pas que l’hôte de la Gateway possède le magasin de sessions et le workspace.

    **Important :** si vous ne faites que commit/push votre workspace vers GitHub, vous sauvegardez
    **la mémoire + les fichiers d’amorçage**, mais **pas** l’historique des sessions ni l’authentification. Ceux-ci se trouvent
    sous `~/.openclaw/` (par exemple `~/.openclaw/agents/<agentId>/sessions/`).

    Voir aussi : [Migrating](/fr/install/migrating), [Where things live on disk](#where-things-live-on-disk),
    [Agent workspace](/fr/concepts/agent-workspace), [Doctor](/fr/gateway/doctor),
    [Remote mode](/fr/gateway/remote).

  </Accordion>

  <Accordion title="Où puis-je voir les nouveautés de la dernière version ?">
    Consultez le changelog GitHub :
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    Les entrées les plus récentes sont en haut. Si la section du haut est marquée **Unreleased**, la section datée suivante
    correspond à la dernière version publiée. Les entrées sont regroupées en **Highlights**, **Changes** et
    **Fixes** (avec des sections docs/autres si nécessaire).

  </Accordion>

  <Accordion title="Impossible d’accéder à docs.openclaw.ai (erreur SSL)">
    Certaines connexions Comcast/Xfinity bloquent incorrectement `docs.openclaw.ai` via Xfinity
    Advanced Security. Désactivez-le ou ajoutez `docs.openclaw.ai` à la liste d’autorisation, puis réessayez.
    Merci de nous aider à le débloquer en le signalant ici : [https://spa.xfinity.com/check_url_status](https://spa.xfinity.com/check_url_status).

    Si vous ne pouvez toujours pas accéder au site, la documentation est mise en miroir sur GitHub :
    [https://github.com/openclaw/openclaw/tree/main/docs](https://github.com/openclaw/openclaw/tree/main/docs)

  </Accordion>

  <Accordion title="Différence entre stable et beta">
    **Stable** et **beta** sont des **dist-tags npm**, pas des lignes de code distinctes :

    - `latest` = stable
    - `beta` = version précoce pour les tests

    En général, une version stable arrive d’abord sur **beta**, puis une étape explicite
    de promotion déplace cette même version vers `latest`. Les mainteneurs peuvent aussi
    publier directement vers `latest` si nécessaire. C’est pourquoi beta et stable peuvent
    pointer vers la **même version** après promotion.

    Voyez ce qui a changé :
    [https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md](https://github.com/openclaw/openclaw/blob/main/CHANGELOG.md)

    Pour les commandes d’installation en une ligne et la différence entre beta et dev, consultez l’accordéon ci-dessous.

  </Accordion>

  <Accordion title="Comment installer la version beta et quelle est la différence entre beta et dev ?">
    **Beta** est le dist-tag npm `beta` (peut correspondre à `latest` après promotion).
    **Dev** est la tête mouvante de `main` (git) ; lorsqu’elle est publiée, elle utilise le dist-tag npm `dev`.

    Commandes en une ligne (macOS/Linux) :

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --beta
    ```

    ```bash
    curl -fsSL --proto '=https' --tlsv1.2 https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Installateur Windows (PowerShell) :
    [https://openclaw.ai/install.ps1](https://openclaw.ai/install.ps1)

    Plus de détails : [Development channels](/fr/install/development-channels) et [Installer flags](/fr/install/installer).

  </Accordion>

  <Accordion title="Comment essayer les toutes dernières versions ?">
    Deux options :

    1. **Canal dev (copie git) :**

    ```bash
    openclaw update --channel dev
    ```

    Cela bascule vers la branche `main` et met à jour depuis les sources.

    2. **Installation hackable (depuis le site de l’installateur) :**

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Cela vous donne un dépôt local que vous pouvez modifier, puis mettre à jour via git.

    Si vous préférez faire un clone propre manuellement, utilisez :

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    ```

    Documentation : [Update](/cli/update), [Development channels](/fr/install/development-channels),
    [Install](/fr/install).

  </Accordion>

  <Accordion title="Combien de temps prennent généralement l’installation et l’onboarding ?">
    Ordre de grandeur :

    - **Installation :** 2 à 5 minutes
    - **Onboarding :** 5 à 15 minutes selon le nombre de canaux/modèles que vous configurez

    Si cela bloque, utilisez [Installer stuck](#quick-start-and-first-run-setup)
    et la boucle de débogage rapide dans [I am stuck](#quick-start-and-first-run-setup).

  </Accordion>

  <Accordion title="L’installateur est bloqué ? Comment obtenir plus d’informations ?">
    Relancez l’installateur avec la **sortie verbeuse** :

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --verbose
    ```

    Installation beta avec sortie verbeuse :

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --beta --verbose
    ```

    Pour une installation hackable (git) :

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git --verbose
    ```

    Équivalent Windows (PowerShell) :

    ```powershell
    # install.ps1 n’a pas encore d’option dédiée -Verbose.
    Set-PSDebug -Trace 1
    & ([scriptblock]::Create((iwr -useb https://openclaw.ai/install.ps1))) -NoOnboard
    Set-PSDebug -Trace 0
    ```

    Plus d’options : [Installer flags](/fr/install/installer).

  </Accordion>

  <Accordion title="L’installation Windows indique git introuvable ou openclaw non reconnu">
    Deux problèmes Windows fréquents :

    **1) erreur npm spawn git / git introuvable**

    - Installez **Git for Windows** et assurez-vous que `git` est dans votre PATH.
    - Fermez puis rouvrez PowerShell, puis relancez l’installateur.

    **2) openclaw n’est pas reconnu après l’installation**

    - Le dossier npm global bin n’est pas dans votre PATH.
    - Vérifiez le chemin :

      ```powershell
      npm config get prefix
      ```

    - Ajoutez ce répertoire à votre PATH utilisateur (pas besoin de suffixe `\bin` sous Windows ; sur la plupart des systèmes, il s’agit de `%AppData%\npm`).
    - Fermez puis rouvrez PowerShell après avoir mis à jour le PATH.

    Si vous voulez la configuration Windows la plus fluide, utilisez **WSL2** plutôt que Windows natif.
    Documentation : [Windows](/fr/platforms/windows).

  </Accordion>

  <Accordion title="La sortie exec sous Windows affiche du texte chinois illisible — que dois-je faire ?">
    Il s’agit généralement d’un décalage de page de code de console sur les shells Windows natifs.

    Symptômes :

    - La sortie de `system.run`/`exec` affiche le chinois de manière illisible
    - La même commande s’affiche correctement dans un autre profil de terminal

    Solution de contournement rapide dans PowerShell :

    ```powershell
    chcp 65001
    [Console]::InputEncoding = [System.Text.UTF8Encoding]::new($false)
    [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    $OutputEncoding = [System.Text.UTF8Encoding]::new($false)
    ```

    Redémarrez ensuite la Gateway et réessayez votre commande :

    ```powershell
    openclaw gateway restart
    ```

    Si vous reproduisez toujours cela sur la dernière version d’OpenClaw, suivez/signalisez-le ici :

    - [Issue #30640](https://github.com/openclaw/openclaw/issues/30640)

  </Accordion>

  <Accordion title="La documentation n’a pas répondu à ma question — comment obtenir une meilleure réponse ?">
    Utilisez l’**installation hackable (git)** afin d’avoir localement l’intégralité du code source et de la documentation, puis posez
    votre question à votre bot (ou à Claude/Codex) _depuis ce dossier_ afin qu’il puisse lire le dépôt et répondre avec précision.

    ```bash
    curl -fsSL https://openclaw.ai/install.sh | bash -s -- --install-method git
    ```

    Plus de détails : [Install](/fr/install) et [Installer flags](/fr/install/installer).

  </Accordion>

  <Accordion title="Comment installer OpenClaw sur Linux ?">
    Réponse courte : suivez le guide Linux, puis lancez l’onboarding.

    - Parcours Linux rapide + installation du service : [Linux](/fr/platforms/linux).
    - Guide complet : [Getting Started](/fr/start/getting-started).
    - Installateur + mises à jour : [Install & updates](/fr/install/updating).

  </Accordion>

  <Accordion title="Comment installer OpenClaw sur un VPS ?">
    N’importe quel VPS Linux convient. Installez sur le serveur, puis utilisez SSH/Tailscale pour accéder à la Gateway.

    Guides : [exe.dev](/fr/install/exe-dev), [Hetzner](/fr/install/hetzner), [Fly.io](/fr/install/fly).
    Accès distant : [Gateway remote](/fr/gateway/remote).

  </Accordion>

  <Accordion title="Où se trouvent les guides d’installation cloud/VPS ?">
    Nous avons un **hub d’hébergement** avec les fournisseurs les plus courants. Choisissez-en un et suivez le guide :

    - [VPS hosting](/fr/vps) (tous les fournisseurs en un seul endroit)
    - [Fly.io](/fr/install/fly)
    - [Hetzner](/fr/install/hetzner)
    - [exe.dev](/fr/install/exe-dev)

    Fonctionnement dans le cloud : la **Gateway s’exécute sur le serveur**, et vous y accédez
    depuis votre ordinateur/téléphone via le Control UI (ou Tailscale/SSH). Votre état + workspace
    se trouvent sur le serveur, traitez donc l’hôte comme la source de vérité et sauvegardez-le.

    Vous pouvez associer des **Node** (Mac/iOS/Android/headless) à cette Gateway cloud pour accéder à
    l’écran/la caméra/le canvas local ou exécuter des commandes sur votre ordinateur tout en gardant la
    Gateway dans le cloud.

    Hub : [Platforms](/fr/platforms). Accès distant : [Gateway remote](/fr/gateway/remote).
    Nodes : [Nodes](/fr/nodes), [Nodes CLI](/cli/nodes).

  </Accordion>

  <Accordion title="Puis-je demander à OpenClaw de se mettre à jour lui-même ?">
    Réponse courte : **possible, mais non recommandé**. Le processus de mise à jour peut redémarrer la
    Gateway (ce qui interrompt la session active), peut nécessiter une copie git propre, et
    peut demander une confirmation. Plus sûr : exécuter les mises à jour depuis un shell en tant qu’opérateur.

    Utilisez la CLI :

    ```bash
    openclaw update
    openclaw update status
    openclaw update --channel stable|beta|dev
    openclaw update --tag <dist-tag|version>
    openclaw update --no-restart
    ```

    Si vous devez absolument automatiser cela depuis un agent :

    ```bash
    openclaw update --yes --no-restart
    openclaw gateway restart
    ```

    Documentation : [Update](/cli/update), [Updating](/fr/install/updating).

  </Accordion>

  <Accordion title="Que fait réellement l’onboarding ?">
    `openclaw onboard` est le parcours de configuration recommandé. En **mode local**, il vous guide à travers :

    - **La configuration du modèle/de l’authentification** (OAuth fournisseur, clés API, setup-token Anthropic, ainsi que les options de modèles locaux comme LM Studio)
    - **L’emplacement du workspace** + les fichiers d’amorçage
    - **Les paramètres de la Gateway** (bind/port/auth/tailscale)
    - **Les canaux** (WhatsApp, Telegram, Discord, Mattermost, Signal, iMessage, ainsi que des Plugins de canal intégrés comme QQ Bot)
    - **L’installation du daemon** (LaunchAgent sur macOS ; unité utilisateur systemd sur Linux/WSL2)
    - **Les vérifications de santé** et la sélection des **Skills**

    Il avertit également si votre modèle configuré est inconnu ou s’il manque une authentification.

  </Accordion>

  <Accordion title="Ai-je besoin d’un abonnement Claude ou OpenAI pour l’utiliser ?">
    Non. Vous pouvez exécuter OpenClaw avec des **clés API** (Anthropic/OpenAI/autres) ou avec des
    **modèles uniquement locaux** afin que vos données restent sur votre appareil. Les abonnements (Claude
    Pro/Max ou OpenAI Codex) sont des moyens facultatifs d’authentifier ces fournisseurs.

    Pour Anthropic dans OpenClaw, la distinction pratique est la suivante :

    - **Clé API Anthropic** : facturation API Anthropic normale
    - **Authentification Claude CLI / abonnement Claude dans OpenClaw** : le personnel d’Anthropic
      nous a indiqué que cet usage est de nouveau autorisé, et OpenClaw considère l’utilisation de `claude -p`
      comme approuvée pour cette intégration, sauf si Anthropic publie une nouvelle
      politique

    Pour les hôtes Gateway de longue durée, les clés API Anthropic restent la
    configuration la plus prévisible. L’OAuth OpenAI Codex est explicitement pris en charge pour les outils externes comme OpenClaw.

    OpenClaw prend également en charge d’autres options hébergées de type abonnement, notamment
    **Qwen Cloud Coding Plan**, **MiniMax Coding Plan**, et
    **Z.AI / GLM Coding Plan**.

    Documentation : [Anthropic](/fr/providers/anthropic), [OpenAI](/fr/providers/openai),
    [Qwen Cloud](/fr/providers/qwen),
    [MiniMax](/fr/providers/minimax), [GLM Models](/fr/providers/glm),
    [Local models](/fr/gateway/local-models), [Models](/fr/concepts/models).

  </Accordion>

  <Accordion title="Puis-je utiliser l’abonnement Claude Max sans clé API ?">
    Oui.

    Le personnel d’Anthropic nous a indiqué que l’utilisation du type Claude CLI d’OpenClaw est de nouveau autorisée, donc
    OpenClaw considère l’authentification par abonnement Claude et l’utilisation de `claude -p` comme approuvées
    pour cette intégration, sauf si Anthropic publie une nouvelle politique. Si vous souhaitez
    la configuration côté serveur la plus prévisible, utilisez plutôt une clé API Anthropic.

  </Accordion>

  <Accordion title="Prenez-vous en charge l’authentification par abonnement Claude (Claude Pro ou Max) ?">
    Oui.

    Le personnel d’Anthropic nous a indiqué que cet usage est de nouveau autorisé, donc OpenClaw considère
    la réutilisation de Claude CLI et l’utilisation de `claude -p` comme approuvées pour cette intégration,
    sauf si Anthropic publie une nouvelle politique.

    Le setup-token Anthropic reste disponible comme chemin de jeton pris en charge par OpenClaw, mais OpenClaw privilégie désormais la réutilisation de Claude CLI et `claude -p` lorsque disponibles.
    Pour les charges de travail de production ou multi-utilisateur, l’authentification par clé API Anthropic reste le
    choix le plus sûr et le plus prévisible. Si vous voulez d’autres options hébergées de type abonnement
    dans OpenClaw, consultez [OpenAI](/fr/providers/openai), [Qwen / Model
    Cloud](/fr/providers/qwen), [MiniMax](/fr/providers/minimax), et [GLM
    Models](/fr/providers/glm).

  </Accordion>

<a id="why-am-i-seeing-http-429-ratelimiterror-from-anthropic"></a>
<Accordion title="Pourquoi est-ce que je vois HTTP 429 rate_limit_error de la part d’Anthropic ?">
Cela signifie que votre **quota/limite de débit Anthropic** est épuisé pour la fenêtre actuelle. Si vous
utilisez **Claude CLI**, attendez la réinitialisation de la fenêtre ou passez à une offre supérieure. Si vous
utilisez une **clé API Anthropic**, vérifiez la Console Anthropic
pour l’utilisation/la facturation et augmentez les limites si nécessaire.

    Si le message est précisément :
    `Extra usage is required for long context requests`, la requête essaie d’utiliser
    la bêta 1M de contexte d’Anthropic (`context1m: true`). Cela ne fonctionne que lorsque votre
    identifiant est éligible à la facturation long contexte (facturation par clé API ou
    chemin Claude-login OpenClaw avec Extra Usage activé).

    Conseil : définissez un **modèle de secours** afin qu’OpenClaw puisse continuer à répondre pendant qu’un fournisseur est limité par le débit.
    Consultez [Models](/cli/models), [OAuth](/fr/concepts/oauth), et
    [/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context](/fr/gateway/troubleshooting#anthropic-429-extra-usage-required-for-long-context).

  </Accordion>

  <Accordion title="AWS Bedrock est-il pris en charge ?">
    Oui. OpenClaw inclut un fournisseur **Amazon Bedrock (Converse)**. Lorsque les marqueurs d’environnement AWS sont présents, OpenClaw peut découvrir automatiquement le catalogue Bedrock streaming/texte et le fusionner comme fournisseur implicite `amazon-bedrock` ; sinon, vous pouvez activer explicitement `plugins.entries.amazon-bedrock.config.discovery.enabled` ou ajouter une entrée de fournisseur manuelle. Consultez [Amazon Bedrock](/fr/providers/bedrock) et [Model providers](/fr/providers/models). Si vous préférez un flux de clé géré, un proxy compatible OpenAI devant Bedrock reste une option valable.
  </Accordion>

  <Accordion title="Comment fonctionne l’authentification Codex ?">
    OpenClaw prend en charge **OpenAI Code (Codex)** via OAuth (connexion ChatGPT). L’onboarding peut exécuter le flux OAuth et définira le modèle par défaut sur `openai-codex/gpt-5.4` lorsque c’est approprié. Consultez [Model providers](/fr/concepts/model-providers) et [Onboarding (CLI)](/fr/start/wizard).
  </Accordion>

  <Accordion title="Pourquoi ChatGPT GPT-5.4 ne débloque-t-il pas openai/gpt-5.4 dans OpenClaw ?">
    OpenClaw traite les deux chemins séparément :

    - `openai-codex/gpt-5.4` = OAuth ChatGPT/Codex
    - `openai/gpt-5.4` = API directe OpenAI Platform

    Dans OpenClaw, la connexion ChatGPT/Codex est reliée au chemin `openai-codex/*`,
    et non au chemin direct `openai/*`. Si vous voulez le chemin API direct dans
    OpenClaw, définissez `OPENAI_API_KEY` (ou la configuration équivalente du fournisseur OpenAI).
    Si vous voulez utiliser la connexion ChatGPT/Codex dans OpenClaw, utilisez `openai-codex/*`.

  </Accordion>

  <Accordion title="Pourquoi les limites OAuth Codex peuvent-elles différer de celles du web ChatGPT ?">
    `openai-codex/*` utilise le chemin OAuth Codex, et ses fenêtres de quota utilisables sont
    gérées par OpenAI et dépendent de l’offre. En pratique, ces limites peuvent différer de
    l’expérience du site/de l’application ChatGPT, même lorsque les deux sont liés au même compte.

    OpenClaw peut afficher les fenêtres actuelles visibles d’utilisation/quota du fournisseur dans
    `openclaw models status`, mais il n’invente ni ne normalise les
    droits du web ChatGPT en accès API direct. Si vous voulez le chemin direct de facturation/limite OpenAI Platform, utilisez `openai/*` avec une clé API.

  </Accordion>

  <Accordion title="Prenez-vous en charge l’authentification par abonnement OpenAI (OAuth Codex) ?">
    Oui. OpenClaw prend entièrement en charge **l’OAuth par abonnement OpenAI Code (Codex)**.
    OpenAI autorise explicitement l’utilisation d’un OAuth par abonnement dans des outils/workflows externes
    comme OpenClaw. L’onboarding peut exécuter le flux OAuth pour vous.

    Consultez [OAuth](/fr/concepts/oauth), [Model providers](/fr/concepts/model-providers), et [Onboarding (CLI)](/fr/start/wizard).

  </Accordion>

  <Accordion title="Comment configurer l’OAuth Gemini CLI ?">
    Gemini CLI utilise un **flux d’authentification de Plugin**, et non un client id ou un secret dans `openclaw.json`.

    Étapes :

    1. Installez Gemini CLI localement afin que `gemini` soit dans le `PATH`
       - Homebrew : `brew install gemini-cli`
       - npm : `npm install -g @google/gemini-cli`
    2. Activez le Plugin : `openclaw plugins enable google`
    3. Connectez-vous : `openclaw models auth login --provider google-gemini-cli --set-default`
    4. Modèle par défaut après connexion : `google-gemini-cli/gemini-3-flash-preview`
    5. Si les requêtes échouent, définissez `GOOGLE_CLOUD_PROJECT` ou `GOOGLE_CLOUD_PROJECT_ID` sur l’hôte Gateway

    Cela stocke les tokens OAuth dans les profils d’authentification sur l’hôte Gateway. Détails : [Model providers](/fr/concepts/model-providers).

  </Accordion>

  <Accordion title="Un modèle local convient-il pour des discussions occasionnelles ?">
    En général non. OpenClaw a besoin d’un grand contexte et d’une sécurité forte ; les petites cartes tronquent et laissent fuiter. Si vous y tenez, exécutez la version de modèle **la plus grande** possible localement (LM Studio) et consultez [/gateway/local-models](/fr/gateway/local-models). Les modèles plus petits/quantifiés augmentent le risque d’injection de prompt — consultez [Security](/fr/gateway/security).
  </Accordion>

  <Accordion title="Comment garder le trafic de modèles hébergés dans une région spécifique ?">
    Choisissez des endpoints épinglés à une région. OpenRouter expose des options hébergées aux États-Unis pour MiniMax, Kimi et GLM ; choisissez la variante hébergée aux États-Unis pour garder les données dans la région. Vous pouvez toujours lister Anthropic/OpenAI à côté de celles-ci en utilisant `models.mode: "merge"` afin que les modèles de secours restent disponibles tout en respectant le fournisseur régional que vous sélectionnez.
  </Accordion>

  <Accordion title="Dois-je acheter un Mac mini pour installer cela ?">
    Non. OpenClaw fonctionne sur macOS ou Linux (Windows via WSL2). Un Mac mini est facultatif : certaines personnes
    en achètent un comme hôte toujours allumé, mais un petit VPS, un serveur domestique ou une machine de classe Raspberry Pi conviennent aussi.

    Vous n’avez besoin d’un Mac **que pour les outils uniquement macOS**. Pour iMessage, utilisez [BlueBubbles](/fr/channels/bluebubbles) (recommandé) — le serveur BlueBubbles fonctionne sur n’importe quel Mac, et la Gateway peut fonctionner sur Linux ou ailleurs. Si vous voulez d’autres outils uniquement macOS, exécutez la Gateway sur un Mac ou associez un Node macOS.

    Documentation : [BlueBubbles](/fr/channels/bluebubbles), [Nodes](/fr/nodes), [Mac remote mode](/fr/platforms/mac/remote).

  </Accordion>

  <Accordion title="Ai-je besoin d’un Mac mini pour la prise en charge d’iMessage ?">
    Vous avez besoin de **n’importe quel appareil macOS** connecté à Messages. Ce n’est **pas** nécessairement un Mac mini —
    n’importe quel Mac convient. **Utilisez [BlueBubbles](/fr/channels/bluebubbles)** (recommandé) pour iMessage — le serveur BlueBubbles fonctionne sur macOS, tandis que la Gateway peut fonctionner sur Linux ou ailleurs.

    Configurations courantes :

    - Exécutez la Gateway sur Linux/VPS, et exécutez le serveur BlueBubbles sur n’importe quel Mac connecté à Messages.
    - Exécutez tout sur le Mac si vous voulez la configuration sur une seule machine la plus simple.

    Documentation : [BlueBubbles](/fr/channels/bluebubbles), [Nodes](/fr/nodes),
    [Mac remote mode](/fr/platforms/mac/remote).

  </Accordion>

  <Accordion title="Si j’achète un Mac mini pour exécuter OpenClaw, puis-je le connecter à mon MacBook Pro ?">
    Oui. Le **Mac mini peut exécuter la Gateway**, et votre MacBook Pro peut se connecter en tant que
    **Node** (appareil compagnon). Les Nodes n’exécutent pas la Gateway — ils fournissent des
    capacités supplémentaires comme l’écran/la caméra/le canvas et `system.run` sur cet appareil.

    Configuration courante :

    - Gateway sur le Mac mini (toujours allumé).
    - Le MacBook Pro exécute l’application macOS ou un hôte Node et s’associe à la Gateway.
    - Utilisez `openclaw nodes status` / `openclaw nodes list` pour le voir.

    Documentation : [Nodes](/fr/nodes), [Nodes CLI](/cli/nodes).

  </Accordion>

  <Accordion title="Puis-je utiliser Bun ?">
    Bun est **non recommandé**. Nous observons des bugs d’exécution, en particulier avec WhatsApp et Telegram.
    Utilisez **Node** pour des Gateways stables.

    Si vous voulez malgré tout expérimenter avec Bun, faites-le sur une Gateway non production
    sans WhatsApp/Telegram.

  </Accordion>

  <Accordion title="Telegram : que faut-il mettre dans allowFrom ?">
    `channels.telegram.allowFrom` correspond à **l’ID utilisateur Telegram de l’expéditeur humain** (numérique). Ce n’est pas le nom d’utilisateur du bot.

    L’onboarding accepte une saisie `@username` et la résout en ID numérique, mais l’autorisation OpenClaw utilise uniquement des ID numériques.

    Plus sûr (sans bot tiers) :

    - Envoyez un message privé à votre bot, puis exécutez `openclaw logs --follow` et lisez `from.id`.

    API Bot officielle :

    - Envoyez un message privé à votre bot, puis appelez `https://api.telegram.org/bot<bot_token>/getUpdates` et lisez `message.from.id`.

    Tiers (moins privé) :

    - Envoyez un message privé à `@userinfobot` ou `@getidsbot`.

    Consultez [/channels/telegram](/fr/channels/telegram#access-control-and-activation).

  </Accordion>

  <Accordion title="Plusieurs personnes peuvent-elles utiliser un même numéro WhatsApp avec différentes instances OpenClaw ?">
    Oui, via le **routage multi-agent**. Associez le **message privé** WhatsApp (peer `kind: "direct"`, expéditeur E.164 comme `+15551234567`) de chaque expéditeur à un `agentId` différent, afin que chaque personne dispose de son propre workspace et de son propre magasin de sessions. Les réponses proviennent toujours du **même compte WhatsApp**, et le contrôle d’accès des messages privés (`channels.whatsapp.dmPolicy` / `channels.whatsapp.allowFrom`) est global par compte WhatsApp. Consultez [Multi-Agent Routing](/fr/concepts/multi-agent) et [WhatsApp](/fr/channels/whatsapp).
  </Accordion>

  <Accordion title='Puis-je exécuter un agent "fast chat" et un agent "Opus for coding" ?'>
    Oui. Utilisez le routage multi-agent : donnez à chaque agent son propre modèle par défaut, puis associez des routes entrantes (compte fournisseur ou peers spécifiques) à chaque agent. Un exemple de configuration se trouve dans [Multi-Agent Routing](/fr/concepts/multi-agent). Consultez aussi [Models](/fr/concepts/models) et [Configuration](/fr/gateway/configuration).
  </Accordion>

  <Accordion title="Homebrew fonctionne-t-il sur Linux ?">
    Oui. Homebrew prend en charge Linux (Linuxbrew). Configuration rapide :

    ```bash
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
    echo 'eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"' >> ~/.profile
    eval "$(/home/linuxbrew/.linuxbrew/bin/brew shellenv)"
    brew install <formula>
    ```

    Si vous exécutez OpenClaw via systemd, assurez-vous que le PATH du service inclut `/home/linuxbrew/.linuxbrew/bin` (ou votre préfixe brew) afin que les outils installés via `brew` soient résolus dans les shells non login.
    Les versions récentes préfixent également les répertoires bin utilisateur courants sur les services Linux systemd (par exemple `~/.local/bin`, `~/.npm-global/bin`, `~/.local/share/pnpm`, `~/.bun/bin`) et respectent `PNPM_HOME`, `NPM_CONFIG_PREFIX`, `BUN_INSTALL`, `VOLTA_HOME`, `ASDF_DATA_DIR`, `NVM_DIR`, et `FNM_DIR` lorsqu’ils sont définis.

  </Accordion>

  <Accordion title="Différence entre l’installation git hackable et npm install">
    - **Installation hackable (git) :** copie complète du code source, modifiable, idéale pour les contributeurs.
      Vous exécutez les builds localement et pouvez corriger le code/la documentation.
    - **npm install :** installation globale de la CLI, sans dépôt, idéale pour « exécuter simplement ».
      Les mises à jour proviennent des dist-tags npm.

    Documentation : [Getting started](/fr/start/getting-started), [Updating](/fr/install/updating).

  </Accordion>

  <Accordion title="Puis-je basculer plus tard entre les installations npm et git ?">
    Oui. Installez l’autre variante, puis exécutez Doctor afin que le service Gateway pointe vers le nouvel entrypoint.
    Cela **ne supprime pas vos données** — cela change uniquement l’installation du code OpenClaw. Votre état
    (`~/.openclaw`) et votre workspace (`~/.openclaw/workspace`) restent intacts.

    De npm vers git :

    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    pnpm install
    pnpm build
    openclaw doctor
    openclaw gateway restart
    ```

    De git vers npm :

    ```bash
    npm install -g openclaw@latest
    openclaw doctor
    openclaw gateway restart
    ```

    Doctor détecte un décalage d’entrypoint du service Gateway et propose de réécrire la configuration du service pour qu’elle corresponde à l’installation actuelle (utilisez `--repair` dans l’automatisation).

    Conseils de sauvegarde : consultez [Backup strategy](#where-things-live-on-disk).

  </Accordion>

  <Accordion title="Dois-je exécuter la Gateway sur mon ordinateur portable ou sur un VPS ?">
    Réponse courte : **si vous voulez une fiabilité 24 h/24 et 7 j/7, utilisez un VPS**. Si vous voulez le
    moins de friction possible et que les mises en veille/redémarrages ne vous gênent pas, exécutez-la localement.

    **Ordinateur portable (Gateway locale)**

    - **Avantages :** aucun coût de serveur, accès direct aux fichiers locaux, fenêtre de navigateur visible en direct.
    - **Inconvénients :** veille/coupures réseau = déconnexions, mises à jour/redémarrages de l’OS interrompent le service, la machine doit rester éveillée.

    **VPS / cloud**

    - **Avantages :** toujours allumé, réseau stable, pas de problèmes liés à la mise en veille du portable, plus facile à laisser tourner.
    - **Inconvénients :** fonctionnement souvent headless (utilisez des captures d’écran), accès uniquement aux fichiers distants, mises à jour à faire en SSH.

    **Remarque spécifique à OpenClaw :** WhatsApp/Telegram/Slack/Mattermost/Discord fonctionnent tous très bien sur un VPS. Le seul véritable compromis concerne **le navigateur headless** par rapport à une fenêtre visible. Consultez [Browser](/fr/tools/browser).

    **Recommandation par défaut :** VPS si vous avez déjà eu des déconnexions de Gateway. Le mode local est excellent lorsque vous utilisez activement le Mac et voulez l’accès aux fichiers locaux ou l’automatisation UI avec un navigateur visible.

  </Accordion>

  <Accordion title="Est-il important d’exécuter OpenClaw sur une machine dédiée ?">
    Ce n’est pas obligatoire, mais **recommandé pour la fiabilité et l’isolation**.

    - **Hôte dédié (VPS/Mac mini/Pi) :** toujours allumé, moins d’interruptions dues à la veille/aux redémarrages, permissions plus propres, plus facile à laisser tourner.
    - **Ordinateur portable/de bureau partagé :** tout à fait acceptable pour les tests et l’usage actif, mais attendez-vous à des pauses lorsque la machine se met en veille ou se met à jour.

    Si vous voulez le meilleur des deux mondes, gardez la Gateway sur un hôte dédié et associez votre ordinateur portable comme **Node** pour les outils locaux d’écran/caméra/exec. Consultez [Nodes](/fr/nodes).
    Pour les conseils de sécurité, lisez [Security](/fr/gateway/security).

  </Accordion>

  <Accordion title="Quelles sont les exigences minimales pour un VPS et l’OS recommandé ?">
    OpenClaw est léger. Pour une Gateway de base + un canal de chat :

    - **Minimum absolu :** 1 vCPU, 1GB de RAM, ~500MB de disque.
    - **Recommandé :** 1 à 2 vCPU, 2GB de RAM ou plus pour avoir de la marge (journaux, médias, plusieurs canaux). Les outils Node et l’automatisation du navigateur peuvent être gourmands en ressources.

    OS : utilisez **Ubuntu LTS** (ou toute distribution Debian/Ubuntu moderne). Le parcours d’installation Linux y est le mieux testé.

    Documentation : [Linux](/fr/platforms/linux), [VPS hosting](/fr/vps).

  </Accordion>

  <Accordion title="Puis-je exécuter OpenClaw dans une VM et quelles sont les exigences ?">
    Oui. Traitez une VM comme un VPS : elle doit être toujours allumée, accessible, et disposer de suffisamment de
    RAM pour la Gateway et tous les canaux que vous activez.

    Recommandations de base :

    - **Minimum absolu :** 1 vCPU, 1GB de RAM.
    - **Recommandé :** 2GB de RAM ou plus si vous exécutez plusieurs canaux, de l’automatisation du navigateur ou des outils média.
    - **OS :** Ubuntu LTS ou une autre distribution Debian/Ubuntu moderne.

    Si vous êtes sur Windows, **WSL2 est la configuration de type VM la plus simple** et offre la meilleure
    compatibilité avec les outils. Consultez [Windows](/fr/platforms/windows), [VPS hosting](/fr/vps).
    Si vous exécutez macOS dans une VM, consultez [macOS VM](/fr/install/macos-vm).

  </Accordion>
</AccordionGroup>

## Qu’est-ce qu’OpenClaw ?

<AccordionGroup>
  <Accordion title="Qu’est-ce qu’OpenClaw, en un paragraphe ?">
    OpenClaw est un assistant IA personnel que vous exécutez sur vos propres appareils. Il répond sur les surfaces de messagerie que vous utilisez déjà (WhatsApp, Telegram, Slack, Mattermost, Discord, Google Chat, Signal, iMessage, WebChat, ainsi que des Plugins de canal intégrés comme QQ Bot) et peut aussi gérer la voix + un Canvas en direct sur les plateformes prises en charge. La **Gateway** est le plan de contrôle toujours actif ; l’assistant est le produit.
  </Accordion>

  <Accordion title="Proposition de valeur">
    OpenClaw n’est pas « juste un wrapper Claude ». C’est un **plan de contrôle local-first** qui vous permet d’exécuter un
    assistant performant sur **votre propre matériel**, accessible depuis les applications de chat que vous utilisez déjà, avec
    des sessions avec état, de la mémoire et des outils — sans confier le contrôle de vos workflows à un
    SaaS hébergé.

    Points forts :

    - **Vos appareils, vos données :** exécutez la Gateway où vous voulez (Mac, Linux, VPS) et conservez le
      workspace + l’historique des sessions en local.
    - **De vrais canaux, pas un bac à sable web :** WhatsApp/Telegram/Slack/Discord/Signal/iMessage/etc.,
      plus la voix mobile et Canvas sur les plateformes prises en charge.
    - **Indépendant du modèle :** utilisez Anthropic, OpenAI, MiniMax, OpenRouter, etc., avec routage
      par agent et bascule.
    - **Option 100 % locale :** exécutez des modèles locaux pour que **toutes les données puissent rester sur votre appareil** si vous le souhaitez.
    - **Routage multi-agent :** séparez les agents par canal, compte ou tâche, chacun avec son propre
      workspace et ses valeurs par défaut.
    - **Open source et modifiable :** inspectez, étendez et auto-hébergez sans verrouillage fournisseur.

    Documentation : [Gateway](/fr/gateway), [Channels](/fr/channels), [Multi-agent](/fr/concepts/multi-agent),
    [Memory](/fr/concepts/memory).

  </Accordion>

  <Accordion title="Je viens de l’installer — que devrais-je faire en premier ?">
    Quelques bons premiers projets :

    - Créer un site web (WordPress, Shopify ou un simple site statique).
    - Prototyper une application mobile (plan, écrans, plan d’API).
    - Organiser les fichiers et dossiers (nettoyage, nommage, étiquetage).
    - Connecter Gmail et automatiser les résumés ou les relances.

    Il peut gérer de grosses tâches, mais il fonctionne mieux lorsque vous les découpez en phases et
    utilisez des sous-agents pour le travail en parallèle.

  </Accordion>

  <Accordion title="Quels sont les cinq cas d’usage quotidiens les plus utiles pour OpenClaw ?">
    Les gains du quotidien ressemblent généralement à ceci :

    - **Briefings personnels :** résumés de la boîte de réception, du calendrier et des actualités qui vous intéressent.
    - **Recherche et rédaction :** recherches rapides, résumés et premiers brouillons d’e-mails ou de documents.
    - **Rappels et relances :** nudges et checklists pilotés par Cron ou Heartbeat.
    - **Automatisation du navigateur :** remplissage de formulaires, collecte de données et répétition de tâches web.
    - **Coordination inter-appareils :** envoyez une tâche depuis votre téléphone, laissez la Gateway l’exécuter sur un serveur, puis recevez le résultat dans le chat.

  </Accordion>

  <Accordion title="OpenClaw peut-il aider pour la génération de leads, la prospection, les publicités et les blogs pour un SaaS ?">
    Oui pour la **recherche, la qualification et la rédaction**. Il peut analyser des sites, constituer des shortlists,
    résumer des prospects et rédiger des brouillons de prospection ou de textes publicitaires.

    Pour la **prospection ou les campagnes publicitaires**, gardez un humain dans la boucle. Évitez le spam, respectez les lois locales et
    les politiques des plateformes, et relisez tout avant envoi. Le schéma le plus sûr consiste à laisser
    OpenClaw rédiger, puis à approuver manuellement.

    Documentation : [Security](/fr/gateway/security).

  </Accordion>

  <Accordion title="Quels sont les avantages par rapport à Claude Code pour le développement web ?">
    OpenClaw est un **assistant personnel** et une couche de coordination, pas un remplacement d’IDE. Utilisez
    Claude Code ou Codex pour la boucle de développement la plus rapide directement dans un dépôt. Utilisez OpenClaw lorsque vous
    voulez une mémoire durable, un accès inter-appareils et une orchestration d’outils.

    Avantages :

    - **Mémoire persistante + workspace** entre les sessions
    - **Accès multiplateforme** (WhatsApp, Telegram, TUI, WebChat)
    - **Orchestration d’outils** (navigateur, fichiers, planification, hooks)
    - **Gateway toujours active** (exécutez-la sur un VPS, interagissez depuis n’importe où)
    - **Nodes** pour navigateur/écran/caméra/exec locaux

    Démonstration : [https://openclaw.ai/showcase](https://openclaw.ai/showcase)

  </Accordion>
</AccordionGroup>

## Skills et automatisation

<AccordionGroup>
  <Accordion title="Comment personnaliser les Skills sans garder le dépôt modifié ?">
    Utilisez des remplacements gérés au lieu de modifier la copie du dépôt. Placez vos changements dans `~/.openclaw/skills/<name>/SKILL.md` (ou ajoutez un dossier via `skills.load.extraDirs` dans `~/.openclaw/openclaw.json`). La priorité est `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → intégré → `skills.load.extraDirs`, donc les remplacements gérés l’emportent toujours sur les Skills intégrées sans toucher à git. Si vous avez besoin que la skill soit installée globalement mais visible uniquement par certains agents, gardez la copie partagée dans `~/.openclaw/skills` et contrôlez la visibilité avec `agents.defaults.skills` et `agents.list[].skills`. Seules les modifications dignes d’être intégrées en amont devraient vivre dans le dépôt et être envoyées via PR.
  </Accordion>

  <Accordion title="Puis-je charger des Skills depuis un dossier personnalisé ?">
    Oui. Ajoutez des répertoires supplémentaires via `skills.load.extraDirs` dans `~/.openclaw/openclaw.json` (priorité la plus basse). L’ordre de priorité par défaut est `<workspace>/skills` → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → intégré → `skills.load.extraDirs`. `clawhub` installe dans `./skills` par défaut, qu’OpenClaw traite comme `<workspace>/skills` à la session suivante. Si la skill ne doit être visible que pour certains agents, associez cela à `agents.defaults.skills` ou `agents.list[].skills`.
  </Accordion>

  <Accordion title="Comment utiliser différents modèles pour différentes tâches ?">
    Aujourd’hui, les schémas pris en charge sont les suivants :

    - **Tâches Cron** : les tâches isolées peuvent définir une surcharge `model` par tâche.
    - **Sous-agents** : routez les tâches vers des agents distincts avec des modèles par défaut différents.
    - **Changement à la demande** : utilisez `/model` pour changer le modèle de la session en cours à tout moment.

    Consultez [Cron jobs](/fr/automation/cron-jobs), [Multi-Agent Routing](/fr/concepts/multi-agent), et [Slash commands](/fr/tools/slash-commands).

  </Accordion>

  <Accordion title="Le bot se fige pendant un travail lourd. Comment décharger cela ?">
    Utilisez des **sous-agents** pour les tâches longues ou parallèles. Les sous-agents s’exécutent dans leur propre session,
    renvoient un résumé et gardent votre chat principal réactif.

    Demandez à votre bot de « lancer un sous-agent pour cette tâche » ou utilisez `/subagents`.
    Utilisez `/status` dans le chat pour voir ce que la Gateway fait en ce moment (et si elle est occupée).

    Conseil sur les tokens : les tâches longues et les sous-agents consomment tous deux des tokens. Si le coût est un sujet, définissez un
    modèle moins cher pour les sous-agents via `agents.defaults.subagents.model`.

    Documentation : [Sub-agents](/fr/tools/subagents), [Background Tasks](/fr/automation/tasks).

  </Accordion>

  <Accordion title="Comment fonctionnent les sessions de sous-agent liées à un fil sur Discord ?">
    Utilisez des liaisons de fils. Vous pouvez lier un fil Discord à un sous-agent ou à une cible de session afin que les messages de suivi dans ce fil restent sur cette session liée.

    Flux de base :

    - Lancez avec `sessions_spawn` en utilisant `thread: true` (et éventuellement `mode: "session"` pour un suivi persistant).
    - Ou liez manuellement avec `/focus <target>`.
    - Utilisez `/agents` pour inspecter l’état de la liaison.
    - Utilisez `/session idle <duration|off>` et `/session max-age <duration|off>` pour contrôler le détachement automatique.
    - Utilisez `/unfocus` pour détacher le fil.

    Configuration requise :

    - Valeurs par défaut globales : `session.threadBindings.enabled`, `session.threadBindings.idleHours`, `session.threadBindings.maxAgeHours`.
    - Surcharges Discord : `channels.discord.threadBindings.enabled`, `channels.discord.threadBindings.idleHours`, `channels.discord.threadBindings.maxAgeHours`.
    - Liaison automatique au lancement : définissez `channels.discord.threadBindings.spawnSubagentSessions: true`.

    Documentation : [Sub-agents](/fr/tools/subagents), [Discord](/fr/channels/discord), [Configuration Reference](/fr/gateway/configuration-reference), [Slash commands](/fr/tools/slash-commands).

  </Accordion>

  <Accordion title="Un sous-agent a terminé, mais la mise à jour de fin est arrivée au mauvais endroit ou n’a jamais été publiée. Que dois-je vérifier ?">
    Vérifiez d’abord la route du demandeur résolue :

    - La livraison des sous-agents en mode fin préfère tout fil ou toute route de conversation liée lorsqu’il en existe un.
    - Si l’origine de fin ne porte qu’un canal, OpenClaw se replie sur la route stockée de la session du demandeur (`lastChannel` / `lastTo` / `lastAccountId`) afin que la livraison directe puisse encore réussir.
    - S’il n’existe ni route liée ni route stockée exploitable, la livraison directe peut échouer et le résultat se replie alors sur une livraison en file d’attente de session au lieu d’être publié immédiatement dans le chat.
    - Des cibles invalides ou obsolètes peuvent encore forcer le repli en file d’attente ou l’échec final de la livraison.
    - Si la dernière réponse visible de l’assistant enfant est exactement le jeton silencieux `NO_REPLY` / `no_reply`, ou exactement `ANNOUNCE_SKIP`, OpenClaw supprime intentionnellement l’annonce au lieu de publier une progression antérieure obsolète.
    - Si l’enfant a expiré après seulement des appels d’outil, l’annonce peut condenser cela en un court résumé de progression partielle au lieu de rejouer la sortie brute des outils.

    Débogage :

    ```bash
    openclaw tasks show <runId-or-sessionKey>
    ```

    Documentation : [Sub-agents](/fr/tools/subagents), [Background Tasks](/fr/automation/tasks), [Session Tools](/fr/concepts/session-tool).

  </Accordion>

  <Accordion title="Cron ou les rappels ne se déclenchent pas. Que dois-je vérifier ?">
    Cron s’exécute dans le processus Gateway. Si la Gateway n’est pas exécutée en continu,
    les tâches planifiées ne s’exécuteront pas.

    Liste de vérification :

    - Confirmez que Cron est activé (`cron.enabled`) et que `OPENCLAW_SKIP_CRON` n’est pas défini.
    - Vérifiez que la Gateway fonctionne 24 h/24 et 7 j/7 (sans mise en veille/redémarrages).
    - Vérifiez les paramètres de fuseau horaire de la tâche (`--tz` par rapport au fuseau horaire de l’hôte).

    Débogage :

    ```bash
    openclaw cron run <jobId>
    openclaw cron runs --id <jobId> --limit 50
    ```

    Documentation : [Cron jobs](/fr/automation/cron-jobs), [Automation & Tasks](/fr/automation).

  </Accordion>

  <Accordion title="Cron s’est déclenché, mais rien n’a été envoyé au canal. Pourquoi ?">
    Vérifiez d’abord le mode de livraison :

    - `--no-deliver` / `delivery.mode: "none"` signifie qu’aucun message externe n’est attendu.
    - Une cible d’annonce manquante ou invalide (`channel` / `to`) signifie que le runner a ignoré la livraison sortante.
    - Des échecs d’authentification du canal (`unauthorized`, `Forbidden`) signifient que le runner a tenté de livrer, mais que les identifiants l’en ont empêché.
    - Un résultat isolé silencieux (`NO_REPLY` / `no_reply` uniquement) est traité comme intentionnellement non livrable, donc le runner supprime également la livraison de repli en file d’attente.

    Pour les tâches Cron isolées, le runner prend en charge la livraison finale. L’agent doit
    renvoyer un résumé en texte brut que le runner enverra. `--no-deliver` conserve
    ce résultat en interne ; cela ne permet pas à l’agent d’envoyer directement avec l’outil
    de message à la place.

    Débogage :

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    Documentation : [Cron jobs](/fr/automation/cron-jobs), [Background Tasks](/fr/automation/tasks).

  </Accordion>

  <Accordion title="Pourquoi une exécution Cron isolée a-t-elle changé de modèle ou réessayé une fois ?">
    Il s’agit généralement du chemin de changement de modèle en direct, pas d’une planification en double.

    Cron isolé peut conserver un transfert de modèle d’exécution et réessayer lorsque l’exécution active
    lève `LiveSessionModelSwitchError`. Le nouvel essai conserve le
    fournisseur/modèle changé, et si le changement comportait une nouvelle surcharge de profil d’authentification, Cron
    conserve cela aussi avant de réessayer.

    Règles de sélection associées :

    - La surcharge de modèle du hook Gmail gagne en premier lorsqu’elle s’applique.
    - Ensuite vient le `model` par tâche.
    - Ensuite, toute surcharge de modèle de session Cron stockée.
    - Ensuite, la sélection normale du modèle par agent/par défaut.

    La boucle de nouvel essai est bornée. Après la tentative initiale plus 2 nouveaux essais après changement,
    Cron abandonne au lieu de boucler indéfiniment.

    Débogage :

    ```bash
    openclaw cron runs --id <jobId> --limit 50
    openclaw tasks show <runId-or-sessionKey>
    ```

    Documentation : [Cron jobs](/fr/automation/cron-jobs), [cron CLI](/cli/cron).

  </Accordion>

  <Accordion title="Comment installer des Skills sur Linux ?">
    Utilisez les commandes natives `openclaw skills` ou déposez des Skills dans votre workspace. L’UI Skills de macOS n’est pas disponible sur Linux.
    Parcourez les Skills sur [https://clawhub.ai](https://clawhub.ai).

    ```bash
    openclaw skills search "calendar"
    openclaw skills search --limit 20
    openclaw skills install <skill-slug>
    openclaw skills install <skill-slug> --version <version>
    openclaw skills install <skill-slug> --force
    openclaw skills update --all
    openclaw skills list --eligible
    openclaw skills check
    ```

    L’installation native avec `openclaw skills install` écrit dans le répertoire `skills/`
    du workspace actif. Installez la CLI `clawhub` séparée uniquement si vous voulez publier ou
    synchroniser vos propres Skills. Pour des installations partagées entre agents, placez la skill dans
    `~/.openclaw/skills` et utilisez `agents.defaults.skills` ou
    `agents.list[].skills` si vous voulez restreindre les agents qui peuvent la voir.

  </Accordion>

  <Accordion title="OpenClaw peut-il exécuter des tâches selon un planning ou en continu en arrière-plan ?">
    Oui. Utilisez le planificateur de la Gateway :

    - **Tâches Cron** pour les tâches planifiées ou récurrentes (persistantes après redémarrage).
    - **Heartbeat** pour les vérifications périodiques de la « session principale ».
    - **Tâches isolées** pour des agents autonomes qui publient des résumés ou livrent vers des chats.

    Documentation : [Cron jobs](/fr/automation/cron-jobs), [Automation & Tasks](/fr/automation),
    [Heartbeat](/fr/gateway/heartbeat).

  </Accordion>

  <Accordion title="Puis-je exécuter des Skills Apple uniquement macOS depuis Linux ?">
    Pas directement. Les Skills macOS sont contrôlées par `metadata.openclaw.os` ainsi que par les binaires requis, et les skills n’apparaissent dans le prompt système que lorsqu’elles sont éligibles sur l’**hôte Gateway**. Sous Linux, les skills `darwin` uniquement (comme `apple-notes`, `apple-reminders`, `things-mac`) ne seront pas chargées sauf si vous contournez ce contrôle.

    Vous avez trois schémas pris en charge :

    **Option A - exécuter la Gateway sur un Mac (le plus simple).**
    Exécutez la Gateway là où les binaires macOS existent, puis connectez-vous depuis Linux en [mode distant](#gateway-ports-already-running-and-remote-mode) ou via Tailscale. Les skills se chargent normalement parce que l’hôte Gateway est sous macOS.

    **Option B - utiliser un Node macOS (sans SSH).**
    Exécutez la Gateway sur Linux, associez un Node macOS (application de barre de menus), et réglez **Node Run Commands** sur « Always Ask » ou « Always Allow » sur le Mac. OpenClaw peut traiter les Skills uniquement macOS comme éligibles lorsque les binaires requis existent sur le Node. L’agent exécute ces skills via l’outil `nodes`. Si vous choisissez « Always Ask », approuver « Always Allow » dans l’invite ajoute cette commande à la liste d’autorisation.

    **Option C - proxifier des binaires macOS via SSH (avancé).**
    Gardez la Gateway sur Linux, mais faites en sorte que les binaires CLI requis se résolvent vers des wrappers SSH qui s’exécutent sur un Mac. Remplacez ensuite la skill pour autoriser Linux afin qu’elle reste éligible.

    1. Créez un wrapper SSH pour le binaire (exemple : `memo` pour Apple Notes) :

       ```bash
       #!/usr/bin/env bash
       set -euo pipefail
       exec ssh -T user@mac-host /opt/homebrew/bin/memo "$@"
       ```

    2. Placez le wrapper dans le `PATH` sur l’hôte Linux (par exemple `~/bin/memo`).
    3. Remplacez les métadonnées de la skill (workspace ou `~/.openclaw/skills`) pour autoriser Linux :

       ```markdown
       ---
       name: apple-notes
       description: Gérer Apple Notes via la CLI memo sur macOS.
       metadata: { "openclaw": { "os": ["darwin", "linux"], "requires": { "bins": ["memo"] } } }
       ---
       ```

    4. Démarrez une nouvelle session afin que l’instantané des Skills soit actualisé.

  </Accordion>

  <Accordion title="Avez-vous une intégration Notion ou HeyGen ?">
    Pas intégrée aujourd’hui.

    Options :

    - **Skill / Plugin personnalisé :** meilleur choix pour un accès API fiable (Notion et HeyGen ont tous deux des API).
    - **Automatisation du navigateur :** fonctionne sans code, mais c’est plus lent et plus fragile.

    Si vous souhaitez conserver le contexte par client (workflows d’agence), un schéma simple consiste à utiliser :

    - Une page Notion par client (contexte + préférences + travail en cours).
    - Demander à l’agent de récupérer cette page au début d’une session.

    Si vous voulez une intégration native, ouvrez une demande de fonctionnalité ou créez une skill
    ciblant ces API.

    Installer des Skills :

    ```bash
    openclaw skills install <skill-slug>
    openclaw skills update --all
    ```

    Les installations natives arrivent dans le répertoire `skills/` du workspace actif. Pour des Skills partagées entre agents, placez-les dans `~/.openclaw/skills/<name>/SKILL.md`. Si seules certaines agents doivent voir une installation partagée, configurez `agents.defaults.skills` ou `agents.list[].skills`. Certaines skills attendent des binaires installés via Homebrew ; sous Linux, cela signifie Linuxbrew (voir l’entrée FAQ Homebrew Linux ci-dessus). Consultez [Skills](/fr/tools/skills), [Skills config](/fr/tools/skills-config), et [ClawHub](/fr/tools/clawhub).

  </Accordion>

  <Accordion title="Comment utiliser mon Chrome déjà connecté avec OpenClaw ?">
    Utilisez le profil de navigateur intégré `user`, qui se connecte via Chrome DevTools MCP :

    ```bash
    openclaw browser --browser-profile user tabs
    openclaw browser --browser-profile user snapshot
    ```

    Si vous voulez un nom personnalisé, créez un profil MCP explicite :

    ```bash
    openclaw browser create-profile --name chrome-live --driver existing-session
    openclaw browser --browser-profile chrome-live tabs
    ```

    Ce chemin est local à l’hôte. Si la Gateway s’exécute ailleurs, exécutez soit un hôte Node sur la machine du navigateur, soit utilisez CDP distant à la place.

    Limites actuelles de `existing-session` / `user` :

    - les actions sont pilotées par `ref`, et non par sélecteur CSS
    - les téléversements nécessitent `ref` / `inputRef` et ne prennent actuellement en charge qu’un seul fichier à la fois
    - `responsebody`, l’export PDF, l’interception des téléchargements et les actions par lot nécessitent encore un navigateur géré ou un profil CDP brut

  </Accordion>
</AccordionGroup>

## Sandbox et mémoire

<AccordionGroup>
  <Accordion title="Existe-t-il une documentation dédiée au sandboxing ?">
    Oui. Consultez [Sandboxing](/fr/gateway/sandboxing). Pour la configuration spécifique à Docker (Gateway complète dans Docker ou images sandbox), consultez [Docker](/fr/install/docker).
  </Accordion>

  <Accordion title="Docker semble limité — comment activer toutes les fonctionnalités ?">
    L’image par défaut privilégie la sécurité et s’exécute en tant qu’utilisateur `node`, elle n’inclut donc pas
    les paquets système, Homebrew, ni les navigateurs intégrés. Pour une configuration plus complète :

    - Rendez `/home/node` persistant avec `OPENCLAW_HOME_VOLUME` afin que les caches survivent.
    - Intégrez les dépendances système dans l’image avec `OPENCLAW_DOCKER_APT_PACKAGES`.
    - Installez les navigateurs Playwright via la CLI intégrée :
      `node /app/node_modules/playwright-core/cli.js install chromium`
    - Définissez `PLAYWRIGHT_BROWSERS_PATH` et assurez-vous que le chemin est persistant.

    Documentation : [Docker](/fr/install/docker), [Browser](/fr/tools/browser).

  </Accordion>

  <Accordion title="Puis-je garder les messages privés personnels tout en rendant les groupes publics/sandboxés avec un seul agent ?">
    Oui — si votre trafic privé correspond aux **messages privés** et votre trafic public aux **groupes**.

    Utilisez `agents.defaults.sandbox.mode: "non-main"` afin que les sessions de groupe/canal (clés non principales) s’exécutent dans Docker, tandis que la session principale de message privé reste sur l’hôte. Restreignez ensuite les outils disponibles dans les sessions sandboxées via `tools.sandbox.tools`.

    Guide de configuration + exemple : [Groups: personal DMs + public groups](/fr/channels/groups#pattern-personal-dms-public-groups-single-agent)

    Référence de configuration clé : [Gateway configuration](/fr/gateway/configuration-reference#agentsdefaultssandbox)

  </Accordion>

  <Accordion title="Comment lier un dossier hôte dans le sandbox ?">
    Définissez `agents.defaults.sandbox.docker.binds` sur `["host:path:mode"]` (par exemple `"/home/user/src:/src:ro"`). Les liaisons globales et par agent sont fusionnées ; les liaisons par agent sont ignorées lorsque `scope: "shared"`. Utilisez `:ro` pour tout ce qui est sensible et rappelez-vous que les liaisons contournent les barrières du système de fichiers du sandbox.

    OpenClaw valide les sources de liaison à la fois par rapport au chemin normalisé et au chemin canonique résolu via l’ancêtre existant le plus profond. Cela signifie que les échappements via un parent symlink échouent toujours de manière fermée même lorsque le dernier segment du chemin n’existe pas encore, et que les vérifications de racine autorisée s’appliquent toujours après résolution des symlinks.

    Consultez [Sandboxing](/fr/gateway/sandboxing#custom-bind-mounts) et [Sandbox vs Tool Policy vs Elevated](/fr/gateway/sandbox-vs-tool-policy-vs-elevated#bind-mounts-security-quick-check) pour des exemples et des remarques de sécurité.

  </Accordion>

  <Accordion title="Comment fonctionne la mémoire ?">
    La mémoire OpenClaw n’est constituée que de fichiers Markdown dans le workspace de l’agent :

    - Notes quotidiennes dans `memory/YYYY-MM-DD.md`
    - Notes durables organisées dans `MEMORY.md` (sessions principales/privées uniquement)

    OpenClaw exécute également un **flush mémoire silencieux avant Compaction** afin de rappeler au modèle
    d’écrire des notes durables avant la Compaction automatique. Cela ne s’exécute que lorsque le workspace
    est accessible en écriture (les sandboxes en lecture seule l’ignorent). Consultez [Memory](/fr/concepts/memory).

  </Accordion>

  <Accordion title="La mémoire oublie toujours des choses. Comment faire pour que cela tienne ?">
    Demandez au bot **d’écrire l’information dans la mémoire**. Les notes durables doivent aller dans `MEMORY.md`,
    le contexte à court terme va dans `memory/YYYY-MM-DD.md`.

    C’est encore un domaine que nous améliorons. Il est utile de rappeler au modèle de stocker des souvenirs ;
    il saura quoi faire. S’il continue d’oublier, vérifiez que la Gateway utilise le même
    workspace à chaque exécution.

    Documentation : [Memory](/fr/concepts/memory), [Agent workspace](/fr/concepts/agent-workspace).

  </Accordion>

  <Accordion title="La mémoire persiste-t-elle indéfiniment ? Quelles sont les limites ?">
    Les fichiers de mémoire vivent sur le disque et persistent jusqu’à leur suppression. La limite est votre
    stockage, pas le modèle. Le **contexte de session** reste toutefois limité par la fenêtre de contexte
    du modèle, donc les longues conversations peuvent être compactées ou tronquées. C’est pourquoi
    la recherche mémoire existe : elle ne réinjecte dans le contexte que les parties pertinentes.

    Documentation : [Memory](/fr/concepts/memory), [Context](/fr/concepts/context).

  </Accordion>

  <Accordion title="La recherche sémantique de mémoire nécessite-t-elle une clé API OpenAI ?">
    Uniquement si vous utilisez les **embeddings OpenAI**. L’OAuth Codex couvre le chat/les complétions et
    ne donne **pas** accès aux embeddings, donc **se connecter avec Codex (OAuth ou la
    connexion CLI Codex)** n’aide pas pour la recherche sémantique de mémoire. Les embeddings OpenAI
    nécessitent toujours une vraie clé API (`OPENAI_API_KEY` ou `models.providers.openai.apiKey`).

    Si vous ne définissez pas explicitement un fournisseur, OpenClaw sélectionne automatiquement un fournisseur lorsqu’il
    peut résoudre une clé API (profils d’authentification, `models.providers.*.apiKey`, ou variables d’environnement).
    Il préfère OpenAI si une clé OpenAI est résolue, sinon Gemini si une clé Gemini
    est résolue, puis Voyage, puis Mistral. Si aucune clé distante n’est disponible, la recherche mémoire
    reste désactivée jusqu’à ce que vous la configuriez. Si vous avez un chemin de modèle local
    configuré et présent, OpenClaw
    préfère `local`. Ollama est pris en charge lorsque vous définissez explicitement
    `memorySearch.provider = "ollama"`.

    Si vous préférez rester en local, définissez `memorySearch.provider = "local"` (et éventuellement
    `memorySearch.fallback = "none"`). Si vous voulez des embeddings Gemini, définissez
    `memorySearch.provider = "gemini"` et fournissez `GEMINI_API_KEY` (ou
    `memorySearch.remote.apiKey`). Nous prenons en charge les modèles d’embeddings **OpenAI, Gemini, Voyage, Mistral, Ollama ou local** —
    consultez [Memory](/fr/concepts/memory) pour les détails de configuration.

  </Accordion>
</AccordionGroup>

## Où se trouvent les éléments sur le disque

<AccordionGroup>
  <Accordion title="Toutes les données utilisées avec OpenClaw sont-elles enregistrées localement ?">
    Non — **l’état d’OpenClaw est local**, mais **les services externes voient toujours ce que vous leur envoyez**.

    - **Local par défaut :** sessions, fichiers de mémoire, configuration et workspace se trouvent sur l’hôte Gateway
      (`~/.openclaw` + votre répertoire de workspace).
    - **Distant par nécessité :** les messages que vous envoyez aux fournisseurs de modèles (Anthropic/OpenAI/etc.) vont vers
      leurs API, et les plateformes de chat (WhatsApp/Telegram/Slack/etc.) stockent les données des messages sur leurs
      serveurs.
    - **Vous contrôlez l’empreinte :** l’utilisation de modèles locaux garde les prompts sur votre machine, mais le trafic
      des canaux passe toujours par les serveurs du canal.

    Voir aussi : [Agent workspace](/fr/concepts/agent-workspace), [Memory](/fr/concepts/memory).

  </Accordion>

  <Accordion title="Où OpenClaw stocke-t-il ses données ?">
    Tout se trouve sous `$OPENCLAW_STATE_DIR` (par défaut : `~/.openclaw`) :

    | Path                                                            | Purpose                                                            |
    | --------------------------------------------------------------- | ------------------------------------------------------------------ |
    | `$OPENCLAW_STATE_DIR/openclaw.json`                             | Configuration principale (JSON5)                                   |
    | `$OPENCLAW_STATE_DIR/credentials/oauth.json`                    | Import OAuth hérité (copié dans les profils d’authentification lors de la première utilisation) |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth-profiles.json` | Profils d’authentification (OAuth, clés API et `keyRef`/`tokenRef` facultatifs) |
    | `$OPENCLAW_STATE_DIR/secrets.json`                              | Payload secret facultatif basé sur fichier pour les fournisseurs SecretRef `file` |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/agent/auth.json`          | Fichier de compatibilité hérité (entrées `api_key` statiques nettoyées) |
    | `$OPENCLAW_STATE_DIR/credentials/`                              | État des fournisseurs (par ex. `whatsapp/<accountId>/creds.json`)  |
    | `$OPENCLAW_STATE_DIR/agents/`                                   | État par agent (agentDir + sessions)                               |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/`                | Historique et état des conversations (par agent)                   |
    | `$OPENCLAW_STATE_DIR/agents/<agentId>/sessions/sessions.json`   | Métadonnées de session (par agent)                                 |

    Chemin hérité mono-agent : `~/.openclaw/agent/*` (migré par `openclaw doctor`).

    Votre **workspace** (`AGENTS.md`, fichiers de mémoire, skills, etc.) est séparé et configuré via `agents.defaults.workspace` (par défaut : `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title="Où doivent se trouver AGENTS.md / SOUL.md / USER.md / MEMORY.md ?">
    Ces fichiers se trouvent dans le **workspace de l’agent**, et non dans `~/.openclaw`.

    - **Workspace (par agent)** : `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`,
      `MEMORY.md` (ou le repli hérité `memory.md` lorsque `MEMORY.md` est absent),
      `memory/YYYY-MM-DD.md`, `HEARTBEAT.md` facultatif.
    - **Répertoire d’état (`~/.openclaw`)** : configuration, état des canaux/fournisseurs, profils d’authentification, sessions, journaux,
      et skills partagées (`~/.openclaw/skills`).

    Le workspace par défaut est `~/.openclaw/workspace`, configurable via :

    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
    }
    ```

    Si le bot « oublie » après un redémarrage, confirmez que la Gateway utilise le même
    workspace à chaque lancement (et rappelez-vous : le mode distant utilise le workspace
    de l’**hôte Gateway**, pas celui de votre ordinateur portable local).

    Conseil : si vous voulez un comportement ou une préférence durable, demandez au bot de **l’écrire dans
    AGENTS.md ou MEMORY.md** plutôt que de vous appuyer sur l’historique du chat.

    Consultez [Agent workspace](/fr/concepts/agent-workspace) et [Memory](/fr/concepts/memory).

  </Accordion>

  <Accordion title="Stratégie de sauvegarde recommandée">
    Placez votre **workspace d’agent** dans un dépôt git **privé** et sauvegardez-le dans un endroit
    privé (par exemple GitHub privé). Cela capture la mémoire + les fichiers AGENTS/SOUL/USER
    et vous permet de restaurer plus tard « l’esprit » de l’assistant.

    Ne faites **pas** de commit de quoi que ce soit sous `~/.openclaw` (identifiants, sessions, tokens ou payloads secrets chiffrés).
    Si vous avez besoin d’une restauration complète, sauvegardez séparément à la fois le workspace et le répertoire d’état
    (voir la question sur la migration ci-dessus).

    Documentation : [Agent workspace](/fr/concepts/agent-workspace).

  </Accordion>

  <Accordion title="Comment désinstaller complètement OpenClaw ?">
    Consultez le guide dédié : [Uninstall](/fr/install/uninstall).
  </Accordion>

  <Accordion title="Les agents peuvent-ils travailler en dehors du workspace ?">
    Oui. Le workspace est le **cwd par défaut** et l’ancre mémoire, pas un sandbox strict.
    Les chemins relatifs se résolvent à l’intérieur du workspace, mais les chemins absolus peuvent accéder à d’autres
    emplacements de l’hôte sauf si le sandboxing est activé. Si vous avez besoin d’isolation, utilisez
    [`agents.defaults.sandbox`](/fr/gateway/sandboxing) ou les paramètres de sandbox par agent. Si vous
    voulez qu’un dépôt soit le répertoire de travail par défaut, pointez le `workspace`
    de cet agent vers la racine du dépôt. Le dépôt OpenClaw n’est que du code source ; gardez le
    workspace séparé sauf si vous voulez intentionnellement que l’agent travaille dedans.

    Exemple (dépôt comme cwd par défaut) :

    ```json5
    {
      agents: {
        defaults: {
          workspace: "~/Projects/my-repo",
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Mode distant : où se trouve le magasin de sessions ?">
    L’état des sessions appartient à l’**hôte Gateway**. Si vous êtes en mode distant, le magasin de sessions qui vous intéresse se trouve sur la machine distante, pas sur votre ordinateur portable local. Consultez [Session management](/fr/concepts/session).
  </Accordion>
</AccordionGroup>

## Bases de la configuration

<AccordionGroup>
  <Accordion title="Quel est le format de la configuration ? Où se trouve-t-elle ?">
    OpenClaw lit une configuration **JSON5** facultative depuis `$OPENCLAW_CONFIG_PATH` (par défaut : `~/.openclaw/openclaw.json`) :

    ```
    $OPENCLAW_CONFIG_PATH
    ```

    Si le fichier est absent, des valeurs par défaut relativement sûres sont utilisées (y compris un workspace par défaut de `~/.openclaw/workspace`).

  </Accordion>

  <Accordion title='J’ai défini gateway.bind: "lan" (ou "tailnet") et maintenant rien n’écoute / l’UI dit unauthorized'>
    Les binds non loopback **nécessitent un chemin d’authentification Gateway valide**. En pratique, cela signifie :

    - authentification par secret partagé : token ou mot de passe
    - `gateway.auth.mode: "trusted-proxy"` derrière un reverse proxy conscient de l’identité correctement configuré et non loopback

    ```json5
    {
      gateway: {
        bind: "lan",
        auth: {
          mode: "token",
          token: "replace-me",
        },
      },
    }
    ```

    Remarques :

    - `gateway.remote.token` / `.password` **n’activent pas** à eux seuls l’authentification de la Gateway locale.
    - Les chemins d’appel locaux peuvent utiliser `gateway.remote.*` comme repli uniquement lorsque `gateway.auth.*` n’est pas défini.
    - Pour l’authentification par mot de passe, définissez à la place `gateway.auth.mode: "password"` plus `gateway.auth.password` (ou `OPENCLAW_GATEWAY_PASSWORD`).
    - Si `gateway.auth.token` / `gateway.auth.password` est explicitement configuré via SecretRef et non résolu, la résolution échoue en mode fermé (aucun repli distant ne masque cela).
    - Les configurations Control UI à secret partagé s’authentifient via `connect.params.auth.token` ou `connect.params.auth.password` (stockés dans les paramètres de l’application/de l’UI). Les modes porteurs d’identité comme Tailscale Serve ou `trusted-proxy` utilisent à la place des en-têtes de requête. Évitez de mettre des secrets partagés dans les URL.
    - Avec `gateway.auth.mode: "trusted-proxy"`, les reverse proxies loopback sur le même hôte ne satisfont toujours **pas** l’authentification trusted-proxy. Le proxy de confiance doit être une source non loopback configurée.

  </Accordion>

  <Accordion title="Pourquoi ai-je maintenant besoin d’un token sur localhost ?">
    OpenClaw applique désormais l’authentification Gateway par défaut, y compris en loopback. Dans le chemin par défaut normal, cela signifie une authentification par token : si aucun chemin d’authentification explicite n’est configuré, le démarrage de la Gateway se résout en mode token et en génère automatiquement un, en l’enregistrant dans `gateway.auth.token`, donc **les clients WS locaux doivent s’authentifier**. Cela empêche les autres processus locaux d’appeler la Gateway.

    Si vous préférez un autre chemin d’authentification, vous pouvez choisir explicitement le mode mot de passe (ou, pour les reverse proxies non loopback conscients de l’identité, `trusted-proxy`). Si vous voulez **vraiment** un loopback ouvert, définissez explicitement `gateway.auth.mode: "none"` dans votre configuration. Doctor peut générer un token pour vous à tout moment : `openclaw doctor --generate-gateway-token`.

  </Accordion>

  <Accordion title="Dois-je redémarrer après avoir modifié la configuration ?">
    La Gateway surveille la configuration et prend en charge le rechargement à chaud :

    - `gateway.reload.mode: "hybrid"` (par défaut) : applique à chaud les changements sûrs, redémarre pour les changements critiques
    - `hot`, `restart`, `off` sont également pris en charge

  </Accordion>

  <Accordion title="Comment désactiver les slogans amusants de la CLI ?">
    Définissez `cli.banner.taglineMode` dans la configuration :

    ```json5
    {
      cli: {
        banner: {
          taglineMode: "off", // random | default | off
        },
      },
    }
    ```

    - `off` : masque le texte du slogan mais conserve la ligne de titre/version de la bannière.
    - `default` : utilise `All your chats, one OpenClaw.` à chaque fois.
    - `random` : slogans amusants/de saison tournants (comportement par défaut).
    - Si vous ne voulez aucune bannière du tout, définissez la variable d’environnement `OPENCLAW_HIDE_BANNER=1`.

  </Accordion>

  <Accordion title="Comment activer la recherche web (et la récupération web) ?">
    `web_fetch` fonctionne sans clé API. `web_search` dépend du
    fournisseur sélectionné :

    - Les fournisseurs basés sur API comme Brave, Exa, Firecrawl, Gemini, Grok, Kimi, MiniMax Search, Perplexity et Tavily nécessitent leur configuration normale de clé API.
    - Ollama Web Search ne nécessite pas de clé, mais utilise votre hôte Ollama configuré et requiert `ollama signin`.
    - DuckDuckGo ne nécessite pas de clé, mais c’est une intégration non officielle basée sur HTML.
    - SearXNG ne nécessite pas de clé/est auto-hébergé ; configurez `SEARXNG_BASE_URL` ou `plugins.entries.searxng.config.webSearch.baseUrl`.

    **Recommandé :** exécutez `openclaw configure --section web` et choisissez un fournisseur.
    Alternatives via variables d’environnement :

    - Brave : `BRAVE_API_KEY`
    - Exa : `EXA_API_KEY`
    - Firecrawl : `FIRECRAWL_API_KEY`
    - Gemini : `GEMINI_API_KEY`
    - Grok : `XAI_API_KEY`
    - Kimi : `KIMI_API_KEY` ou `MOONSHOT_API_KEY`
    - MiniMax Search : `MINIMAX_CODE_PLAN_KEY`, `MINIMAX_CODING_API_KEY`, ou `MINIMAX_API_KEY`
    - Perplexity : `PERPLEXITY_API_KEY` ou `OPENROUTER_API_KEY`
    - SearXNG : `SEARXNG_BASE_URL`
    - Tavily : `TAVILY_API_KEY`

    ```json5
    {
      plugins: {
        entries: {
          brave: {
            config: {
              webSearch: {
                apiKey: "BRAVE_API_KEY_HERE",
              },
            },
          },
        },
        },
        tools: {
          web: {
            search: {
              enabled: true,
              provider: "brave",
              maxResults: 5,
            },
            fetch: {
              enabled: true,
              provider: "firecrawl", // facultatif ; omettez pour la détection automatique
            },
          },
        },
    }
    ```

    La configuration de recherche web spécifique au fournisseur se trouve désormais sous `plugins.entries.<plugin>.config.webSearch.*`.
    Les anciens chemins de fournisseur `tools.web.search.*` sont encore chargés temporairement pour compatibilité, mais ne doivent pas être utilisés pour les nouvelles configurations.
    La configuration de repli web-fetch de Firecrawl se trouve sous `plugins.entries.firecrawl.config.webFetch.*`.

    Remarques :

    - Si vous utilisez des listes d’autorisation, ajoutez `web_search`/`web_fetch`/`x_search` ou `group:web`.
    - `web_fetch` est activé par défaut (sauf s’il est explicitement désactivé).
    - Si `tools.web.fetch.provider` est omis, OpenClaw détecte automatiquement le premier fournisseur de repli fetch prêt à l’emploi à partir des identifiants disponibles. Aujourd’hui, le fournisseur intégré est Firecrawl.
    - Les daemons lisent les variables d’environnement depuis `~/.openclaw/.env` (ou l’environnement du service).

    Documentation : [Web tools](/fr/tools/web).

  </Accordion>

  <Accordion title="config.apply a effacé ma configuration. Comment récupérer et éviter cela ?">
    `config.apply` remplace la **configuration entière**. Si vous envoyez un objet partiel, tout
    le reste est supprimé.

    Récupération :

    - Restaurez depuis une sauvegarde (git ou une copie de `~/.openclaw/openclaw.json`).
    - Si vous n’avez pas de sauvegarde, relancez `openclaw doctor` puis reconfigurez les canaux/modèles.
    - Si cela était inattendu, ouvrez un bug et incluez votre dernière configuration connue ou toute sauvegarde.
    - Un agent de développement local peut souvent reconstruire une configuration fonctionnelle à partir des journaux ou de l’historique.

    Pour éviter cela :

    - Utilisez `openclaw config set` pour les petits changements.
    - Utilisez `openclaw configure` pour les modifications interactives.
    - Utilisez d’abord `config.schema.lookup` lorsque vous n’êtes pas sûr d’un chemin exact ou de la forme d’un champ ; il renvoie un nœud de schéma superficiel ainsi que des résumés immédiats des enfants pour approfondir.
    - Utilisez `config.patch` pour les modifications RPC partielles ; réservez `config.apply` au remplacement complet de la configuration.
    - Si vous utilisez l’outil `gateway` réservé au propriétaire depuis une exécution d’agent, il rejettera toujours les écritures dans `tools.exec.ask` / `tools.exec.security` (y compris les alias hérités `tools.bash.*` qui se normalisent vers les mêmes chemins exec protégés).

    Documentation : [Config](/cli/config), [Configure](/cli/configure), [Doctor](/fr/gateway/doctor).

  </Accordion>

  <Accordion title="Comment exécuter une Gateway centrale avec des workers spécialisés sur plusieurs appareils ?">
    Le schéma courant est **une Gateway** (par ex. Raspberry Pi) plus des **Node** et des **agents** :

    - **Gateway (centrale)** : possède les canaux (Signal/WhatsApp), le routage et les sessions.
    - **Nodes (appareils)** : les Mac/iOS/Android se connectent comme périphériques et exposent des outils locaux (`system.run`, `canvas`, `camera`).
    - **Agents (workers)** : cerveaux/workspaces séparés pour des rôles spécialisés (par ex. « Hetzner ops », « Données personnelles »).
    - **Sous-agents** : lancent du travail en arrière-plan depuis un agent principal lorsque vous voulez du parallélisme.
    - **TUI** : se connecte à la Gateway et permet de changer d’agent/session.

    Documentation : [Nodes](/fr/nodes), [Remote access](/fr/gateway/remote), [Multi-Agent Routing](/fr/concepts/multi-agent), [Sub-agents](/fr/tools/subagents), [TUI](/web/tui).

  </Accordion>

  <Accordion title="Le navigateur OpenClaw peut-il s’exécuter en mode headless ?">
    Oui. C’est une option de configuration :

    ```json5
    {
      browser: { headless: true },
      agents: {
        defaults: {
          sandbox: { browser: { headless: true } },
        },
      },
    }
    ```

    La valeur par défaut est `false` (avec interface visible). Le mode headless est plus susceptible de déclencher des vérifications anti-bot sur certains sites. Consultez [Browser](/fr/tools/browser).

    Le mode headless utilise le **même moteur Chromium** et fonctionne pour la plupart des automatisations (formulaires, clics, scraping, connexions). Les principales différences :

    - Aucune fenêtre de navigateur visible (utilisez des captures d’écran si vous avez besoin de visuels).
    - Certains sites sont plus stricts vis-à-vis de l’automatisation en mode headless (CAPTCHAs, anti-bot).
      Par exemple, X/Twitter bloque souvent les sessions headless.

  </Accordion>

  <Accordion title="Comment utiliser Brave pour le contrôle du navigateur ?">
    Définissez `browser.executablePath` sur votre binaire Brave (ou tout autre navigateur basé sur Chromium), puis redémarrez la Gateway.
    Consultez les exemples complets de configuration dans [Browser](/fr/tools/browser#use-brave-or-another-chromium-based-browser).
  </Accordion>
</AccordionGroup>

## Gateways distantes et Nodes

<AccordionGroup>
  <Accordion title="Comment les commandes se propagent-elles entre Telegram, la Gateway et les Nodes ?">
    Les messages Telegram sont gérés par la **Gateway**. La Gateway exécute l’agent puis
    appelle seulement les Nodes via le **WebSocket Gateway** lorsqu’un outil Node est nécessaire :

    Telegram → Gateway → Agent → `node.*` → Node → Gateway → Telegram

    Les Nodes ne voient pas le trafic entrant du fournisseur ; ils ne reçoivent que des appels RPC Node.

  </Accordion>

  <Accordion title="Comment mon agent peut-il accéder à mon ordinateur si la Gateway est hébergée à distance ?">
    Réponse courte : **associez votre ordinateur en tant que Node**. La Gateway s’exécute ailleurs, mais elle peut
    appeler les outils `node.*` (écran, caméra, système) sur votre machine locale via le WebSocket Gateway.

    Configuration typique :

    1. Exécutez la Gateway sur l’hôte toujours allumé (VPS/serveur domestique).
    2. Placez l’hôte Gateway et votre ordinateur sur le même tailnet.
    3. Assurez-vous que le WS Gateway est accessible (bind tailnet ou tunnel SSH).
    4. Ouvrez l’application macOS localement et connectez-vous en mode **Remote over SSH** (ou tailnet direct)
       afin qu’elle puisse s’enregistrer comme Node.
    5. Approuvez le Node sur la Gateway :

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    Aucun pont TCP séparé n’est nécessaire ; les Nodes se connectent via le WebSocket Gateway.

    Rappel de sécurité : associer un Node macOS autorise `system.run` sur cette machine. N’associez
    que des appareils de confiance et consultez [Security](/fr/gateway/security).

    Documentation : [Nodes](/fr/nodes), [Gateway protocol](/fr/gateway/protocol), [macOS remote mode](/fr/platforms/mac/remote), [Security](/fr/gateway/security).

  </Accordion>

  <Accordion title="Tailscale est connecté mais je n’obtiens aucune réponse. Que faire ?">
    Vérifiez les bases :

    - La Gateway est en cours d’exécution : `openclaw gateway status`
    - Santé de la Gateway : `openclaw status`
    - Santé des canaux : `openclaw channels status`

    Vérifiez ensuite l’authentification et le routage :

    - Si vous utilisez Tailscale Serve, assurez-vous que `gateway.auth.allowTailscale` est correctement défini.
    - Si vous vous connectez via un tunnel SSH, confirmez que le tunnel local est actif et pointe vers le bon port.
    - Confirmez que vos listes d’autorisation (messages privés ou groupes) incluent votre compte.

    Documentation : [Tailscale](/fr/gateway/tailscale), [Remote access](/fr/gateway/remote), [Channels](/fr/channels).

  </Accordion>

  <Accordion title="Deux instances OpenClaw peuvent-elles se parler (local + VPS) ?">
    Oui. Il n’existe pas de pont « bot à bot » intégré, mais vous pouvez le mettre en place de plusieurs
    façons fiables :

    **Le plus simple :** utilisez un canal de chat normal auquel les deux bots peuvent accéder (Telegram/Slack/WhatsApp).
    Demandez au bot A d’envoyer un message au bot B, puis laissez le bot B répondre normalement.

    **Pont CLI (générique) :** exécutez un script qui appelle l’autre Gateway avec
    `openclaw agent --message ... --deliver`, en ciblant un chat où l’autre bot
    écoute. Si l’un des bots est sur un VPS distant, pointez votre CLI vers cette Gateway distante
    via SSH/Tailscale (consultez [Remote access](/fr/gateway/remote)).

    Exemple de schéma (à exécuter depuis une machine pouvant atteindre la Gateway cible) :

    ```bash
    openclaw agent --message "Hello from local bot" --deliver --channel telegram --reply-to <chat-id>
    ```

    Conseil : ajoutez un garde-fou afin que les deux bots ne bouclent pas indéfiniment (mode mention uniquement, listes d’autorisation de canaux, ou règle « ne pas répondre aux messages de bot »).

    Documentation : [Remote access](/fr/gateway/remote), [Agent CLI](/cli/agent), [Agent send](/fr/tools/agent-send).

  </Accordion>

  <Accordion title="Ai-je besoin de VPS séparés pour plusieurs agents ?">
    Non. Une Gateway peut héberger plusieurs agents, chacun avec son propre workspace, ses modèles par défaut,
    et son routage. C’est la configuration normale, et elle est bien moins coûteuse et plus simple que d’exécuter
    un VPS par agent.

    Utilisez des VPS séparés uniquement lorsque vous avez besoin d’une isolation forte (frontières de sécurité) ou de
    configurations très différentes que vous ne voulez pas partager. Sinon, conservez une seule Gateway et
    utilisez plusieurs agents ou sous-agents.

  </Accordion>

  <Accordion title="Y a-t-il un avantage à utiliser un Node sur mon ordinateur portable personnel plutôt que SSH depuis un VPS ?">
    Oui — les Nodes sont la méthode de premier ordre pour atteindre votre ordinateur portable depuis une Gateway distante, et ils
    offrent davantage qu’un simple accès shell. La Gateway fonctionne sur macOS/Linux (Windows via WSL2) et est
    légère (un petit VPS ou une machine de classe Raspberry Pi suffit ; 4 GB de RAM sont largement suffisants), donc une configuration
    courante consiste à avoir un hôte toujours allumé et votre ordinateur portable comme Node.

    - **Aucun SSH entrant requis.** Les Nodes se connectent en sortie au WebSocket Gateway et utilisent l’association d’appareil.
    - **Contrôles d’exécution plus sûrs.** `system.run` est protégé par des listes d’autorisation/des approbations Node sur cet ordinateur portable.
    - **Davantage d’outils appareil.** Les Nodes exposent `canvas`, `camera`, et `screen` en plus de `system.run`.
    - **Automatisation locale du navigateur.** Gardez la Gateway sur un VPS, mais exécutez Chrome localement via un hôte Node sur l’ordinateur portable, ou attachez-vous à Chrome local sur l’hôte via Chrome MCP.

    SSH convient pour un accès shell ponctuel, mais les Nodes sont plus simples pour les workflows d’agent continus et
    l’automatisation des appareils.

    Documentation : [Nodes](/fr/nodes), [Nodes CLI](/cli/nodes), [Browser](/fr/tools/browser).

  </Accordion>

  <Accordion title="Les Nodes exécutent-ils un service Gateway ?">
    Non. Une seule **Gateway** doit s’exécuter par hôte, sauf si vous exécutez intentionnellement des profils isolés (consultez [Multiple gateways](/fr/gateway/multiple-gateways)). Les Nodes sont des périphériques qui se connectent
    à la Gateway (Nodes iOS/Android, ou « mode Node » macOS dans l’application de barre de menus). Pour les hôtes Node headless
    et le contrôle CLI, consultez [Node host CLI](/cli/node).

    Un redémarrage complet est requis pour les modifications de `gateway`, `discovery` et `canvasHost`.

  </Accordion>

  <Accordion title="Existe-t-il un moyen API / RPC d’appliquer la configuration ?">
    Oui.

    - `config.schema.lookup` : inspecter un sous-arbre de configuration avec son nœud de schéma superficiel, l’indication d’UI correspondante et les résumés immédiats des enfants avant écriture
    - `config.get` : récupérer l’instantané actuel + le hash
    - `config.patch` : mise à jour partielle sûre (préférée pour la plupart des modifications RPC) ; recharge à chaud lorsque possible et redémarre si nécessaire
    - `config.apply` : valider + remplacer la configuration complète ; recharge à chaud lorsque possible et redémarre si nécessaire
    - L’outil d’exécution `gateway`, réservé au propriétaire, refuse toujours de réécrire `tools.exec.ask` / `tools.exec.security` ; les alias hérités `tools.bash.*` se normalisent vers les mêmes chemins exec protégés

  </Accordion>

  <Accordion title="Configuration minimale raisonnable pour une première installation">
    ```json5
    {
      agents: { defaults: { workspace: "~/.openclaw/workspace" } },
      channels: { whatsapp: { allowFrom: ["+15555550123"] } },
    }
    ```

    Cela définit votre workspace et restreint les personnes pouvant déclencher le bot.

  </Accordion>

  <Accordion title="Comment configurer Tailscale sur un VPS et me connecter depuis mon Mac ?">
    Étapes minimales :

    1. **Installer + se connecter sur le VPS**

       ```bash
       curl -fsSL https://tailscale.com/install.sh | sh
       sudo tailscale up
       ```

    2. **Installer + se connecter sur votre Mac**
       - Utilisez l’application Tailscale et connectez-vous au même tailnet.
    3. **Activer MagicDNS (recommandé)**
       - Dans la console d’administration Tailscale, activez MagicDNS afin que le VPS ait un nom stable.
    4. **Utiliser le nom d’hôte tailnet**
       - SSH : `ssh user@your-vps.tailnet-xxxx.ts.net`
       - WS Gateway : `ws://your-vps.tailnet-xxxx.ts.net:18789`

    Si vous voulez le Control UI sans SSH, utilisez Tailscale Serve sur le VPS :

    ```bash
    openclaw gateway --tailscale serve
    ```

    Cela garde la Gateway liée au loopback et expose HTTPS via Tailscale. Consultez [Tailscale](/fr/gateway/tailscale).

  </Accordion>

  <Accordion title="Comment connecter un Node Mac à une Gateway distante (Tailscale Serve) ?">
    Serve expose le **Control UI + WS Gateway**. Les Nodes se connectent via le même endpoint WS Gateway.

    Configuration recommandée :

    1. **Assurez-vous que le VPS + le Mac sont sur le même tailnet**.
    2. **Utilisez l’application macOS en mode Remote** (la cible SSH peut être le nom d’hôte tailnet).
       L’application établira un tunnel du port Gateway et se connectera comme Node.
    3. **Approuvez le Node** sur la Gateway :

       ```bash
       openclaw devices list
       openclaw devices approve <requestId>
       ```

    Documentation : [Gateway protocol](/fr/gateway/protocol), [Discovery](/fr/gateway/discovery), [macOS remote mode](/fr/platforms/mac/remote).

  </Accordion>

  <Accordion title="Dois-je installer sur un second ordinateur portable ou simplement ajouter un Node ?">
    Si vous n’avez besoin que d’**outils locaux** (écran/caméra/exec) sur le second ordinateur portable, ajoutez-le comme
    **Node**. Cela permet de conserver une seule Gateway et évite de dupliquer la configuration. Les outils Node locaux sont
    actuellement réservés à macOS, mais nous prévoyons de les étendre à d’autres OS.

    N’installez une seconde Gateway que si vous avez besoin d’une **isolation forte** ou de deux bots complètement séparés.

    Documentation : [Nodes](/fr/nodes), [Nodes CLI](/cli/nodes), [Multiple gateways](/fr/gateway/multiple-gateways).

  </Accordion>
</AccordionGroup>

## Variables d’environnement et chargement de .env

<AccordionGroup>
  <Accordion title="Comment OpenClaw charge-t-il les variables d’environnement ?">
    OpenClaw lit les variables d’environnement depuis le processus parent (shell, launchd/systemd, CI, etc.) et charge en plus :

    - `.env` depuis le répertoire de travail actuel
    - un `.env` global de repli depuis `~/.openclaw/.env` (alias `$OPENCLAW_STATE_DIR/.env`)

    Aucun de ces fichiers `.env` ne remplace des variables d’environnement déjà existantes.

    Vous pouvez aussi définir des variables d’environnement inline dans la configuration (appliquées uniquement si elles sont absentes de l’environnement du processus) :

    ```json5
    {
      env: {
        OPENROUTER_API_KEY: "sk-or-...",
        vars: { GROQ_API_KEY: "gsk-..." },
      },
    }
    ```

    Consultez [/environment](/fr/help/environment) pour l’ordre de priorité complet et les sources.

  </Accordion>

  <Accordion title="J’ai démarré la Gateway via le service et mes variables d’environnement ont disparu. Que faire ?">
    Deux correctifs courants :

    1. Placez les clés manquantes dans `~/.openclaw/.env` afin qu’elles soient prises en compte même lorsque le service n’hérite pas de l’environnement de votre shell.
    2. Activez l’import depuis le shell (option pratique sur activation) :

    ```json5
    {
      env: {
        shellEnv: {
          enabled: true,
          timeoutMs: 15000,
        },
      },
    }
    ```

    Cela exécute votre shell de connexion et n’importe que les clés attendues manquantes (sans jamais remplacer). Équivalents en variable d’environnement :
    `OPENCLAW_LOAD_SHELL_ENV=1`, `OPENCLAW_SHELL_ENV_TIMEOUT_MS=15000`.

  </Accordion>

  <Accordion title='J’ai défini COPILOT_GITHUB_TOKEN, mais models status affiche "Shell env: off." Pourquoi ?'>
    `openclaw models status` indique si **l’import d’environnement du shell** est activé. « Shell env: off »
    ne signifie **pas** que vos variables d’environnement sont absentes — cela signifie simplement qu’OpenClaw ne chargera pas
    automatiquement votre shell de connexion.

    Si la Gateway s’exécute comme service (launchd/systemd), elle n’héritera pas de l’environnement
    de votre shell. Corrigez cela de l’une des façons suivantes :

    1. Placez le token dans `~/.openclaw/.env` :

       ```
       COPILOT_GITHUB_TOKEN=...
       ```

    2. Ou activez l’import depuis le shell (`env.shellEnv.enabled: true`).
    3. Ou ajoutez-le à votre bloc `env` dans la configuration (s’applique uniquement s’il est absent).

    Redémarrez ensuite la Gateway et vérifiez à nouveau :

    ```bash
    openclaw models status
    ```

    Les tokens Copilot sont lus depuis `COPILOT_GITHUB_TOKEN` (également `GH_TOKEN` / `GITHUB_TOKEN`).
    Consultez [/concepts/model-providers](/fr/concepts/model-providers) et [/environment](/fr/help/environment).

  </Accordion>
</AccordionGroup>

## Sessions et discussions multiples

<AccordionGroup>
  <Accordion title="Comment démarrer une nouvelle conversation ?">
    Envoyez `/new` ou `/reset` comme message autonome. Consultez [Session management](/fr/concepts/session).
  </Accordion>

  <Accordion title="Les sessions se réinitialisent-elles automatiquement si je n’envoie jamais /new ?">
    Les sessions peuvent expirer après `session.idleMinutes`, mais cela est **désactivé par défaut** (valeur par défaut **0**).
    Définissez une valeur positive pour activer l’expiration par inactivité. Lorsqu’elle est activée, le **message suivant**
    après la période d’inactivité démarre un nouvel ID de session pour cette clé de chat.
    Cela ne supprime pas les transcriptions — cela démarre simplement une nouvelle session.

    ```json5
    {
      session: {
        idleMinutes: 240,
      },
    }
    ```

  </Accordion>

  <Accordion title="Existe-t-il un moyen de créer une équipe d’instances OpenClaw (un CEO et plusieurs agents) ?">
    Oui, via le **routage multi-agent** et les **sous-agents**. Vous pouvez créer un agent
    coordinateur et plusieurs agents workers avec leurs propres workspaces et modèles.

    Cela dit, il vaut mieux voir cela comme une **expérience amusante**. Cela consomme beaucoup de tokens et c’est souvent
    moins efficace que d’utiliser un seul bot avec des sessions séparées. Le modèle typique que nous
    envisageons est un bot unique avec lequel vous discutez, avec différentes sessions pour le travail parallèle. Ce
    bot peut également lancer des sous-agents si nécessaire.

    Documentation : [Multi-agent routing](/fr/concepts/multi-agent), [Sub-agents](/fr/tools/subagents), [Agents CLI](/cli/agents).

  </Accordion>

  <Accordion title="Pourquoi le contexte a-t-il été tronqué au milieu d’une tâche ? Comment l’éviter ?">
    Le contexte de session est limité par la fenêtre du modèle. Les longues discussions, les sorties d’outil volumineuses ou de nombreux
    fichiers peuvent déclencher une Compaction ou une troncature.

    Ce qui aide :

    - Demandez au bot de résumer l’état actuel et de l’écrire dans un fichier.
    - Utilisez `/compact` avant les longues tâches, et `/new` lorsque vous changez de sujet.
    - Gardez le contexte important dans le workspace et demandez au bot de le relire.
    - Utilisez des sous-agents pour les travaux longs ou parallèles afin de garder la discussion principale plus légère.
    - Choisissez un modèle avec une fenêtre de contexte plus grande si cela se produit souvent.

  </Accordion>

  <Accordion title="Comment réinitialiser complètement OpenClaw tout en le gardant installé ?">
    Utilisez la commande de réinitialisation :

    ```bash
    openclaw reset
    ```

    Réinitialisation complète non interactive :

    ```bash
    openclaw reset --scope full --yes --non-interactive
    ```

    Puis relancez la configuration :

    ```bash
    openclaw onboard --install-daemon
    ```

    Remarques :

    - L’onboarding propose aussi **Reset** s’il détecte une configuration existante. Consultez [Onboarding (CLI)](/fr/start/wizard).
    - Si vous avez utilisé des profils (`--profile` / `OPENCLAW_PROFILE`), réinitialisez chaque répertoire d’état (les valeurs par défaut sont `~/.openclaw-<profile>`).
    - Réinitialisation dev : `openclaw gateway --dev --reset` (réservé au développement ; efface la configuration dev + les identifiants + les sessions + le workspace).

  </Accordion>

  <Accordion title='J’obtiens des erreurs "context too large" — comment réinitialiser ou compacter ?'>
    Utilisez l’une de ces options :

    - **Compacter** (conserve la conversation mais résume les anciens tours) :

      ```
      /compact
      ```

      ou `/compact <instructions>` pour guider le résumé.

    - **Réinitialiser** (nouvel ID de session pour la même clé de chat) :

      ```
      /new
      /reset
      ```

    Si cela continue à se produire :

    - Activez ou ajustez **l’élagage de session** (`agents.defaults.contextPruning`) pour réduire les anciennes sorties d’outil.
    - Utilisez un modèle avec une fenêtre de contexte plus grande.

    Documentation : [Compaction](/fr/concepts/compaction), [Session pruning](/fr/concepts/session-pruning), [Session management](/fr/concepts/session).

  </Accordion>

  <Accordion title='Pourquoi est-ce que je vois "LLM request rejected: messages.content.tool_use.input field required" ?'>
    Il s’agit d’une erreur de validation du fournisseur : le modèle a émis un bloc `tool_use` sans le
    `input` requis. Cela signifie généralement que l’historique de session est obsolète ou corrompu (souvent après de longs fils
    ou un changement d’outil/de schéma).

    Correctif : démarrez une nouvelle session avec `/new` (message autonome).

  </Accordion>

  <Accordion title="Pourquoi est-ce que je reçois des messages Heartbeat toutes les 30 minutes ?">
    Les Heartbeat s’exécutent toutes les **30 min** par défaut (**1 h** lors de l’utilisation d’une authentification OAuth). Ajustez-les ou désactivez-les :

    ```json5
    {
      agents: {
        defaults: {
          heartbeat: {
            every: "2h", // ou "0m" pour désactiver
          },
        },
      },
    }
    ```

    Si `HEARTBEAT.md` existe mais est en pratique vide (uniquement des lignes vides et des
    en-têtes Markdown comme `# Heading`), OpenClaw ignore l’exécution de Heartbeat pour économiser des appels API.
    Si le fichier est absent, Heartbeat s’exécute quand même et le modèle décide quoi faire.

    Les surcharges par agent utilisent `agents.list[].heartbeat`. Documentation : [Heartbeat](/fr/gateway/heartbeat).

  </Accordion>

  <Accordion title='Dois-je ajouter un "compte bot" à un groupe WhatsApp ?'>
    Non. OpenClaw s’exécute sur **votre propre compte**, donc si vous êtes dans le groupe, OpenClaw peut le voir.
    Par défaut, les réponses dans les groupes sont bloquées jusqu’à ce que vous autorisiez des expéditeurs (`groupPolicy: "allowlist"`).

    Si vous voulez que **vous seul** puissiez déclencher les réponses dans le groupe :

    ```json5
    {
      channels: {
        whatsapp: {
          groupPolicy: "allowlist",
          groupAllowFrom: ["+15551234567"],
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Comment obtenir le JID d’un groupe WhatsApp ?">
    Option 1 (la plus rapide) : suivez les journaux et envoyez un message de test dans le groupe :

    ```bash
    openclaw logs --follow --json
    ```

    Recherchez `chatId` (ou `from`) se terminant par `@g.us`, par exemple :
    `1234567890-1234567890@g.us`.

    Option 2 (si déjà configuré/sur liste d’autorisation) : lister les groupes depuis la configuration :

    ```bash
    openclaw directory groups list --channel whatsapp
    ```

    Documentation : [WhatsApp](/fr/channels/whatsapp), [Directory](/cli/directory), [Logs](/cli/logs).

  </Accordion>

  <Accordion title="Pourquoi OpenClaw ne répond-il pas dans un groupe ?">
    Deux causes fréquentes :

    - Le filtrage par mention est activé (par défaut). Vous devez @mentionner le bot (ou correspondre à `mentionPatterns`).
    - Vous avez configuré `channels.whatsapp.groups` sans `"*"` et le groupe n’est pas dans la liste d’autorisation.

    Consultez [Groups](/fr/channels/groups) et [Group messages](/fr/channels/group-messages).

  </Accordion>

  <Accordion title="Les groupes/fils partagent-ils le contexte avec les messages privés ?">
    Les chats directs sont ramenés à la session principale par défaut. Les groupes/canaux ont leurs propres clés de session, et les sujets Telegram / fils Discord sont des sessions séparées. Consultez [Groups](/fr/channels/groups) et [Group messages](/fr/channels/group-messages).
  </Accordion>

  <Accordion title="Combien de workspaces et d’agents puis-je créer ?">
    Il n’y a pas de limite stricte. Des dizaines (voire des centaines) conviennent très bien, mais surveillez :

    - **La croissance du disque :** les sessions + transcriptions se trouvent sous `~/.openclaw/agents/<agentId>/sessions/`.
    - **Le coût en tokens :** plus d’agents signifie plus d’utilisation concurrente des modèles.
    - **La charge opérationnelle :** profils d’authentification, workspaces et routage de canaux par agent.

    Conseils :

    - Gardez un workspace **actif** par agent (`agents.defaults.workspace`).
    - Élaguez les anciennes sessions (supprimez les JSONL ou les entrées du magasin) si le disque grossit.
    - Utilisez `openclaw doctor` pour repérer les workspaces isolés et les incohérences de profils.

  </Accordion>

  <Accordion title="Puis-je exécuter plusieurs bots ou chats en même temps (Slack), et comment devrais-je configurer cela ?">
    Oui. Utilisez le **routage multi-agent** pour exécuter plusieurs agents isolés et router les messages entrants par
    canal/compte/peer. Slack est pris en charge comme canal et peut être lié à des agents spécifiques.

    L’accès au navigateur est puissant mais ne signifie pas « faire tout ce qu’un humain peut faire » — anti-bot, CAPTCHAs et MFA peuvent
    toujours bloquer l’automatisation. Pour le contrôle de navigateur le plus fiable, utilisez Chrome MCP local sur l’hôte,
    ou utilisez CDP sur la machine qui exécute réellement le navigateur.

    Configuration recommandée :

    - Hôte Gateway toujours allumé (VPS/Mac mini).
    - Un agent par rôle (liaisons).
    - Canal/canaux Slack liés à ces agents.
    - Navigateur local via Chrome MCP ou un Node si nécessaire.

    Documentation : [Multi-Agent Routing](/fr/concepts/multi-agent), [Slack](/fr/channels/slack),
    [Browser](/fr/tools/browser), [Nodes](/fr/nodes).

  </Accordion>
</AccordionGroup>

## Modèles : valeurs par défaut, sélection, alias, changement

<AccordionGroup>
  <Accordion title='Qu’est-ce que le « modèle par défaut » ?'>
    Le modèle par défaut d’OpenClaw est celui que vous définissez comme :

    ```
    agents.defaults.model.primary
    ```

    Les modèles sont référencés sous la forme `provider/model` (exemple : `openai/gpt-5.4`). Si vous omettez le fournisseur, OpenClaw essaie d’abord un alias, puis une correspondance unique de fournisseur configuré pour cet identifiant de modèle exact, et ce n’est qu’ensuite qu’il revient au fournisseur par défaut configuré comme chemin de compatibilité obsolète. Si ce fournisseur n’expose plus le modèle par défaut configuré, OpenClaw se replie sur le premier fournisseur/modèle configuré au lieu d’exposer une valeur par défaut obsolète pointant vers un fournisseur supprimé. Vous devriez quand même **définir explicitement** `provider/model`.

  </Accordion>

  <Accordion title="Quel modèle recommandez-vous ?">
    **Recommandation par défaut :** utilisez le modèle de dernière génération le plus performant disponible dans votre pile de fournisseurs.
    **Pour les agents avec outils activés ou recevant des entrées non fiables :** privilégiez la puissance du modèle plutôt que le coût.
    **Pour les discussions de routine / à faible enjeu :** utilisez des modèles de secours moins chers et routez par rôle d’agent.

    MiniMax a sa propre documentation : [MiniMax](/fr/providers/minimax) et
    [Local models](/fr/gateway/local-models).

    Règle générale : utilisez le **meilleur modèle que vous pouvez vous permettre** pour les travaux à enjeu élevé, et un modèle moins cher
    pour les discussions de routine ou les résumés. Vous pouvez router les modèles par agent et utiliser des sous-agents pour
    paralléliser les longues tâches (chaque sous-agent consomme des tokens). Consultez [Models](/fr/concepts/models) et
    [Sub-agents](/fr/tools/subagents).

    Avertissement important : les modèles plus faibles / trop quantifiés sont plus vulnérables à l’injection de prompt
    et aux comportements non sûrs. Consultez [Security](/fr/gateway/security).

    Plus de contexte : [Models](/fr/concepts/models).

  </Accordion>

  <Accordion title="Comment changer de modèle sans effacer ma configuration ?">
    Utilisez des **commandes de modèle** ou modifiez uniquement les champs **model**. Évitez les remplacements complets de configuration.

    Options sûres :

    - `/model` dans le chat (rapide, par session)
    - `openclaw models set ...` (met à jour uniquement la configuration du modèle)
    - `openclaw configure --section model` (interactif)
    - modifier `agents.defaults.model` dans `~/.openclaw/openclaw.json`

    Évitez `config.apply` avec un objet partiel sauf si vous avez l’intention de remplacer toute la configuration.
    Pour les modifications RPC, inspectez d’abord avec `config.schema.lookup` et privilégiez `config.patch`. La payload de lookup vous donne le chemin normalisé, la documentation/les contraintes du schéma superficiel, ainsi que les résumés immédiats des enfants.
    pour les mises à jour partielles.
    Si vous avez écrasé la configuration, restaurez-la depuis une sauvegarde ou relancez `openclaw doctor` pour réparer.

    Documentation : [Models](/fr/concepts/models), [Configure](/cli/configure), [Config](/cli/config), [Doctor](/fr/gateway/doctor).

  </Accordion>

  <Accordion title="Puis-je utiliser des modèles auto-hébergés (llama.cpp, vLLM, Ollama) ?">
    Oui. Ollama est le chemin le plus simple pour les modèles locaux.

    Configuration la plus rapide :

    1. Installez Ollama depuis `https://ollama.com/download`
    2. Téléchargez un modèle local tel que `ollama pull gemma4`
    3. Si vous voulez aussi des modèles cloud, exécutez `ollama signin`
    4. Exécutez `openclaw onboard` et choisissez `Ollama`
    5. Choisissez `Local` ou `Cloud + Local`

    Remarques :

    - `Cloud + Local` vous donne des modèles cloud en plus de vos modèles Ollama locaux
    - les modèles cloud tels que `kimi-k2.5:cloud` ne nécessitent pas de téléchargement local
    - pour un changement manuel, utilisez `openclaw models list` et `openclaw models set ollama/<model>`

    Remarque de sécurité : les modèles plus petits ou fortement quantifiés sont plus vulnérables à l’injection de prompt.
    Nous recommandons vivement les **grands modèles** pour tout bot pouvant utiliser des outils.
    Si vous voulez malgré tout de petits modèles, activez le sandboxing et des listes d’autorisation d’outils strictes.

    Documentation : [Ollama](/fr/providers/ollama), [Local models](/fr/gateway/local-models),
    [Model providers](/fr/concepts/model-providers), [Security](/fr/gateway/security),
    [Sandboxing](/fr/gateway/sandboxing).

  </Accordion>

  <Accordion title="Quels modèles utilisent OpenClaw, Flawd et Krill ?">
    - Ces déploiements peuvent différer et évoluer dans le temps ; il n’existe pas de recommandation de fournisseur fixe.
    - Vérifiez le paramètre d’exécution actuel sur chaque Gateway avec `openclaw models status`.
    - Pour les agents sensibles à la sécurité / avec outils activés, utilisez le modèle de dernière génération le plus performant disponible.
  </Accordion>

  <Accordion title="Comment changer de modèle à la volée (sans redémarrer) ?">
    Utilisez la commande `/model` comme message autonome :

    ```
    /model sonnet
    /model opus
    /model gpt
    /model gpt-mini
    /model gemini
    /model gemini-flash
    /model gemini-flash-lite
    ```

    Ce sont les alias intégrés. Des alias personnalisés peuvent être ajoutés via `agents.defaults.models`.

    Vous pouvez lister les modèles disponibles avec `/model`, `/model list`, ou `/model status`.

    `/model` (et `/model list`) affiche un sélecteur compact numéroté. Sélectionnez par numéro :

    ```
    /model 3
    ```

    Vous pouvez aussi forcer un profil d’authentification spécifique pour le fournisseur (par session) :

    ```
    /model opus@anthropic:default
    /model opus@anthropic:work
    ```

    Conseil : `/model status` affiche quel agent est actif, quel fichier `auth-profiles.json` est utilisé, et quel profil d’authentification sera essayé ensuite.
    Il affiche aussi l’endpoint fournisseur configuré (`baseUrl`) et le mode API (`api`) lorsqu’ils sont disponibles.

    **Comment retirer l’épinglage d’un profil défini avec @profile ?**

    Relancez `/model` **sans** le suffixe `@profile` :

    ```
    /model anthropic/claude-opus-4-6
    ```

    Si vous voulez revenir à la valeur par défaut, choisissez-la depuis `/model` (ou envoyez `/model <default provider/model>`).
    Utilisez `/model status` pour confirmer quel profil d’authentification est actif.

  </Accordion>

  <Accordion title="Puis-je utiliser GPT 5.2 pour les tâches quotidiennes et Codex 5.3 pour le code ?">
    Oui. Définissez l’un comme valeur par défaut et changez selon les besoins :

    - **Changement rapide (par session) :** `/model gpt-5.4` pour les tâches quotidiennes, `/model openai-codex/gpt-5.4` pour le code avec OAuth Codex.
    - **Valeur par défaut + changement :** définissez `agents.defaults.model.primary` sur `openai/gpt-5.4`, puis passez à `openai-codex/gpt-5.4` pour coder (ou l’inverse).
    - **Sous-agents :** routez les tâches de code vers des sous-agents avec un modèle par défaut différent.

    Consultez [Models](/fr/concepts/models) et [Slash commands](/fr/tools/slash-commands).

  </Accordion>

  <Accordion title="Comment configurer le mode rapide pour GPT 5.4 ?">
    Utilisez soit un basculement de session, soit une valeur par défaut dans la configuration :

    - **Par session :** envoyez `/fast on` pendant que la session utilise `openai/gpt-5.4` ou `openai-codex/gpt-5.4`.
    - **Valeur par défaut par modèle :** définissez `agents.defaults.models["openai/gpt-5.4"].params.fastMode` sur `true`.
    - **OAuth Codex aussi :** si vous utilisez également `openai-codex/gpt-5.4`, définissez le même indicateur à cet endroit.

    Exemple :

    ```json5
    {
      agents: {
        defaults: {
          models: {
            "openai/gpt-5.4": {
              params: {
                fastMode: true,
              },
            },
            "openai-codex/gpt-5.4": {
              params: {
                fastMode: true,
              },
            },
          },
        },
      },
    }
    ```

    Pour OpenAI, le mode rapide correspond à `service_tier = "priority"` sur les requêtes Responses natives prises en charge. Les surcharges de session `/fast` l’emportent sur les valeurs par défaut de configuration.

    Consultez [Thinking and fast mode](/fr/tools/thinking) et [OpenAI fast mode](/fr/providers/openai#openai-fast-mode).

  </Accordion>

  <Accordion title='Pourquoi est-ce que je vois "Model ... is not allowed" puis aucune réponse ?'>
    Si `agents.defaults.models` est défini, il devient la **liste d’autorisation** pour `/model` et toutes les
    surcharges de session. Choisir un modèle qui n’est pas dans cette liste renvoie :

    ```
    Model "provider/model" is not allowed. Use /model to list available models.
    ```

    Cette erreur est renvoyée **à la place** d’une réponse normale. Correctif : ajoutez le modèle à
    `agents.defaults.models`, supprimez la liste d’autorisation, ou choisissez un modèle depuis `/model list`.

  </Accordion>

  <Accordion title='Pourquoi est-ce que je vois "Unknown model: minimax/MiniMax-M2.7" ?'>
    Cela signifie que le **fournisseur n’est pas configuré** (aucune configuration MiniMax ou aucun profil
    d’authentification n’a été trouvé), donc le modèle ne peut pas être résolu.

    Liste de vérification pour corriger :

    1. Mettez à niveau vers une version actuelle d’OpenClaw (ou exécutez depuis la source `main`), puis redémarrez la Gateway.
    2. Assurez-vous que MiniMax est configuré (assistant ou JSON), ou que l’authentification MiniMax
       existe dans l’environnement/les profils d’authentification afin que le fournisseur correspondant puisse être injecté
       (`MINIMAX_API_KEY` pour `minimax`, `MINIMAX_OAUTH_TOKEN` ou OAuth MiniMax
       stocké pour `minimax-portal`).
    3. Utilisez l’identifiant de modèle exact (sensible à la casse) pour votre chemin d’authentification :
       `minimax/MiniMax-M2.7` ou `minimax/MiniMax-M2.7-highspeed` pour une configuration
       par clé API, ou `minimax-portal/MiniMax-M2.7` /
       `minimax-portal/MiniMax-M2.7-highspeed` pour une configuration OAuth.
    4. Exécutez :

       ```bash
       openclaw models list
       ```

       et choisissez dans la liste (ou `/model list` dans le chat).

    Consultez [MiniMax](/fr/providers/minimax) et [Models](/fr/concepts/models).

  </Accordion>

  <Accordion title="Puis-je utiliser MiniMax par défaut et OpenAI pour les tâches complexes ?">
    Oui. Utilisez **MiniMax comme valeur par défaut** et changez de modèle **par session** lorsque nécessaire.
    Les secours sont destinés aux **erreurs**, pas aux « tâches difficiles », donc utilisez `/model` ou un agent séparé.

    **Option A : changer par session**

    ```json5
    {
      env: { MINIMAX_API_KEY: "sk-...", OPENAI_API_KEY: "sk-..." },
      agents: {
        defaults: {
          model: { primary: "minimax/MiniMax-M2.7" },
          models: {
            "minimax/MiniMax-M2.7": { alias: "minimax" },
            "openai/gpt-5.4": { alias: "gpt" },
          },
        },
      },
    }
    ```

    Ensuite :

    ```
    /model gpt
    ```

    **Option B : agents séparés**

    - Valeur par défaut de l’agent A : MiniMax
    - Valeur par défaut de l’agent B : OpenAI
    - Routez par agent ou utilisez `/agent` pour changer

    Documentation : [Models](/fr/concepts/models), [Multi-Agent Routing](/fr/concepts/multi-agent), [MiniMax](/fr/providers/minimax), [OpenAI](/fr/providers/openai).

  </Accordion>

  <Accordion title="Les raccourcis opus / sonnet / gpt sont-ils intégrés ?">
    Oui. OpenClaw fournit quelques raccourcis par défaut (appliqués uniquement lorsque le modèle existe dans `agents.defaults.models`) :

    - `opus` → `anthropic/claude-opus-4-6`
    - `sonnet` → `anthropic/claude-sonnet-4-6`
    - `gpt` → `openai/gpt-5.4`
    - `gpt-mini` → `openai/gpt-5.4-mini`
    - `gpt-nano` → `openai/gpt-5.4-nano`
    - `gemini` → `google/gemini-3.1-pro-preview`
    - `gemini-flash` → `google/gemini-3-flash-preview`
    - `gemini-flash-lite` → `google/gemini-3.1-flash-lite-preview`

    Si vous définissez votre propre alias avec le même nom, votre valeur l’emporte.

  </Accordion>

  <Accordion title="Comment définir/remplacer des raccourcis de modèle (alias) ?">
    Les alias proviennent de `agents.defaults.models.<modelId>.alias`. Exemple :

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "anthropic/claude-opus-4-6" },
          models: {
            "anthropic/claude-opus-4-6": { alias: "opus" },
            "anthropic/claude-sonnet-4-6": { alias: "sonnet" },
            "anthropic/claude-haiku-4-5": { alias: "haiku" },
          },
        },
      },
    }
    ```

    Ensuite, `/model sonnet` (ou `/<alias>` lorsque pris en charge) se résout vers cet identifiant de modèle.

  </Accordion>

  <Accordion title="Comment ajouter des modèles d’autres fournisseurs comme OpenRouter ou Z.AI ?">
    OpenRouter (paiement au token ; nombreux modèles) :

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "openrouter/anthropic/claude-sonnet-4-6" },
          models: { "openrouter/anthropic/claude-sonnet-4-6": {} },
        },
      },
      env: { OPENROUTER_API_KEY: "sk-or-..." },
    }
    ```

    Z.AI (modèles GLM) :

    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "zai/glm-5" },
          models: { "zai/glm-5": {} },
        },
      },
      env: { ZAI_API_KEY: "..." },
    }
    ```

    Si vous référencez un fournisseur/modèle mais que la clé de fournisseur requise est absente, vous obtiendrez une erreur d’authentification à l’exécution (par ex. `No API key found for provider "zai"`).

    **Aucune clé API trouvée pour le fournisseur après l’ajout d’un nouvel agent**

    Cela signifie généralement que le **nouvel agent** a un magasin d’authentification vide. L’authentification est propre à chaque agent et
    stockée dans :

    ```
    ~/.openclaw/agents/<agentId>/agent/auth-profiles.json
    ```

    Options pour corriger :

    - Exécutez `openclaw agents add <id>` et configurez l’authentification pendant l’assistant.
    - Ou copiez `auth-profiles.json` depuis `agentDir` de l’agent principal vers `agentDir` du nouvel agent.

    Ne **réutilisez pas** `agentDir` entre agents ; cela provoque des collisions d’authentification/session.

  </Accordion>
</AccordionGroup>

## Secours de modèle et « All models failed »

<AccordionGroup>
  <Accordion title="Comment fonctionne le failover ?">
    Le failover se produit en deux étapes :

    1. **Rotation des profils d’authentification** au sein du même fournisseur.
    2. **Secours de modèle** vers le modèle suivant dans `agents.defaults.model.fallbacks`.

    Des délais de refroidissement s’appliquent aux profils en échec (backoff exponentiel), de sorte qu’OpenClaw peut continuer à répondre même lorsqu’un fournisseur est limité en débit ou temporairement défaillant.

    Le compartiment de limitation de débit inclut davantage que de simples réponses `429`. OpenClaw
    traite aussi des messages comme `Too many concurrent requests`,
    `ThrottlingException`, `concurrency limit reached`,
    `workers_ai ... quota limit exceeded`, `resource exhausted`, et des limites
    périodiques de fenêtre d’utilisation (`weekly/monthly limit reached`) comme des
    limitations de débit justifiant un failover.

    Certaines réponses ressemblant à de la facturation ne sont pas des `402`, et certaines réponses HTTP `402`
    restent également dans ce compartiment transitoire. Si un fournisseur renvoie
    un texte explicite de facturation sur `401` ou `403`, OpenClaw peut toujours le conserver dans
    la catégorie facturation, mais les correspondances textuelles spécifiques au fournisseur restent limitées au
    fournisseur qui les possède (par exemple OpenRouter `Key limit exceeded`). Si un message `402`
    ressemble plutôt à une fenêtre d’utilisation réessayable ou à une
    limite de dépense d’organisation/workspace (`daily limit reached, resets tomorrow`,
    `organization spending limit exceeded`), OpenClaw le traite comme
    `rate_limit`, et non comme une désactivation longue liée à la facturation.

    Les erreurs de dépassement de contexte sont différentes : des signatures telles que
    `request_too_large`, `input exceeds the maximum number of tokens`,
    `input token count exceeds the maximum number of input tokens`,
    `input is too long for the model`, ou `ollama error: context length
    exceeded` restent sur le chemin de Compaction/réessai au lieu de faire avancer le
    secours de modèle.

    Le texte générique d’erreur serveur est volontairement plus restreint que « tout ce qui contient
    unknown/error ». OpenClaw traite bien certaines formes transitoires limitées au fournisseur
    comme Anthropic `An unknown error occurred`, OpenRouter
    `Provider returned error`, des erreurs de raison d’arrêt comme `Unhandled stop reason:
    error`, des payloads JSON `api_error` avec du texte serveur transitoire
    (`internal server error`, `unknown error, 520`, `upstream error`, `backend
    error`), et des erreurs de fournisseur occupé comme `ModelNotReadyException` comme
    des signaux de timeout/surcharge justifiant un failover lorsque le contexte fournisseur
    correspond.
    Un texte générique de repli interne comme `LLM request failed with an unknown
    error.` reste conservateur et ne déclenche pas à lui seul un secours de modèle.

  </Accordion>

  <Accordion title='Que signifie "No credentials found for profile anthropic:default" ?'>
    Cela signifie que le système a tenté d’utiliser l’identifiant de profil d’authentification `anthropic:default`, mais n’a pas pu trouver les identifiants correspondants dans le magasin d’authentification attendu.

    **Liste de vérification pour corriger :**

    - **Confirmez l’emplacement des profils d’authentification** (nouveaux chemins vs hérités)
      - Actuel : `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
      - Hérité : `~/.openclaw/agent/*` (migré par `openclaw doctor`)
    - **Confirmez que votre variable d’environnement est chargée par la Gateway**
      - Si vous définissez `ANTHROPIC_API_KEY` dans votre shell mais exécutez la Gateway via systemd/launchd, elle peut ne pas l’hériter. Placez-la dans `~/.openclaw/.env` ou activez `env.shellEnv`.
    - **Assurez-vous de modifier le bon agent**
      - Les configurations multi-agent signifient qu’il peut y avoir plusieurs fichiers `auth-profiles.json`.
    - **Vérifiez rapidement l’état modèle/authentification**
      - Utilisez `openclaw models status` pour voir les modèles configurés et si les fournisseurs sont authentifiés.

    **Liste de vérification pour corriger "No credentials found for profile anthropic"**

    Cela signifie que l’exécution est épinglée à un profil d’authentification Anthropic, mais que la Gateway
    ne peut pas le trouver dans son magasin d’authentification.

    - **Utiliser Claude CLI**
      - Exécutez `openclaw models auth login --provider anthropic --method cli --set-default` sur l’hôte Gateway.
    - **Si vous voulez utiliser une clé API à la place**
      - Placez `ANTHROPIC_API_KEY` dans `~/.openclaw/.env` sur l’**hôte Gateway**.
      - Effacez tout ordre épinglé qui force un profil manquant :

        ```bash
        openclaw models auth order clear --provider anthropic
        ```

    - **Confirmez que vous exécutez les commandes sur l’hôte Gateway**
      - En mode distant, les profils d’authentification se trouvent sur la machine Gateway, pas sur votre ordinateur portable.

  </Accordion>

  <Accordion title="Pourquoi a-t-il aussi essayé Google Gemini puis échoué ?">
    Si votre configuration de modèle inclut Google Gemini comme secours (ou si vous êtes passé à un raccourci Gemini), OpenClaw l’essaiera lors du secours de modèle. Si vous n’avez pas configuré d’identifiants Google, vous verrez `No API key found for provider "google"`.

    Correctif : fournissez une authentification Google, ou supprimez/évitez les modèles Google dans `agents.defaults.model.fallbacks` / alias afin que le secours n’y route pas.

    **LLM request rejected: thinking signature required (Google Antigravity)**

    Cause : l’historique de session contient des **blocs de réflexion sans signature** (souvent issus
    d’un flux interrompu/partiel). Google Antigravity exige des signatures pour les blocs de réflexion.

    Correctif : OpenClaw supprime désormais les blocs de réflexion non signés pour Google Antigravity Claude. Si cela apparaît encore, démarrez une **nouvelle session** ou définissez `/thinking off` pour cet agent.

  </Accordion>
</AccordionGroup>

## Profils d’authentification : ce qu’ils sont et comment les gérer

Voir aussi : [/concepts/oauth](/fr/concepts/oauth) (flux OAuth, stockage des tokens, schémas multi-comptes)

<AccordionGroup>
  <Accordion title="Qu’est-ce qu’un profil d’authentification ?">
    Un profil d’authentification est un enregistrement d’identifiants nommé (OAuth ou clé API) lié à un fournisseur. Les profils se trouvent dans :

    ```
    ~/.openclaw/agents/<agentId>/agent/auth-profiles.json
    ```

  </Accordion>

  <Accordion title="Quels sont les identifiants de profil typiques ?">
    OpenClaw utilise des identifiants préfixés par fournisseur comme :

    - `anthropic:default` (courant lorsqu’aucune identité e-mail n’existe)
    - `anthropic:<email>` pour les identités OAuth
    - des identifiants personnalisés que vous choisissez (par ex. `anthropic:work`)

  </Accordion>

  <Accordion title="Puis-je contrôler quel profil d’authentification est essayé en premier ?">
    Oui. La configuration prend en charge des métadonnées facultatives pour les profils et un ordre par fournisseur (`auth.order.<provider>`). Cela **ne** stocke **pas** les secrets ; cela associe les identifiants au fournisseur/mode et définit l’ordre de rotation.

    OpenClaw peut temporairement ignorer un profil s’il est dans un court **délai de refroidissement** (limitations de débit/timeouts/échecs d’authentification) ou dans un état plus long **désactivé** (facturation/crédits insuffisants). Pour inspecter cela, exécutez `openclaw models status --json` et vérifiez `auth.unusableProfiles`. Réglage : `auth.cooldowns.billingBackoffHours*`.

    Les délais de refroidissement dus aux limitations de débit peuvent être limités à un modèle. Un profil en refroidissement
    pour un modèle peut encore être utilisable pour un modèle frère chez le même fournisseur,
    tandis que les fenêtres de facturation/désactivation bloquent toujours le profil entier.

    Vous pouvez aussi définir une surcharge d’ordre **par agent** (stockée dans le `auth-state.json` de cet agent) via la CLI :

    ```bash
    # Utilise par défaut l’agent par défaut configuré (omettez --agent)
    openclaw models auth order get --provider anthropic

    # Verrouiller la rotation sur un seul profil (n’essayer que celui-ci)
    openclaw models auth order set --provider anthropic anthropic:default

    # Ou définir un ordre explicite (secours au sein du fournisseur)
    openclaw models auth order set --provider anthropic anthropic:work anthropic:default

    # Effacer la surcharge (revenir à config auth.order / round-robin)
    openclaw models auth order clear --provider anthropic
    ```

    Pour cibler un agent spécifique :

    ```bash
    openclaw models auth order set --provider anthropic --agent main anthropic:default
    ```

    Pour vérifier ce qui sera réellement essayé, utilisez :

    ```bash
    openclaw models status --probe
    ```

    Si un profil stocké est omis de l’ordre explicite, le probe signale
    `excluded_by_auth_order` pour ce profil au lieu de l’essayer silencieusement.

  </Accordion>

  <Accordion title="OAuth vs clé API — quelle est la différence ?">
    OpenClaw prend en charge les deux :

    - **OAuth** exploite souvent un accès par abonnement (lorsque applicable).
    - **Clés API** utilisent une facturation au token.

    L’assistant prend explicitement en charge Anthropic Claude CLI, OpenAI Codex OAuth et les clés API.

  </Accordion>
</AccordionGroup>

## Gateway : ports, « déjà en cours d’exécution » et mode distant

<AccordionGroup>
  <Accordion title="Quel port utilise la Gateway ?">
    `gateway.port` contrôle le port multiplexé unique pour WebSocket + HTTP (Control UI, hooks, etc.).

    Ordre de priorité :

    ```
    --port > OPENCLAW_GATEWAY_PORT > gateway.port > valeur par défaut 18789
    ```

  </Accordion>

  <Accordion title='Pourquoi openclaw gateway status affiche-t-il "Runtime: running" mais "RPC probe: failed" ?'>
    Parce que « running » est la vue du **superviseur** (launchd/systemd/schtasks). Le probe RPC correspond au fait que la CLI se connecte réellement au WebSocket de la Gateway et appelle `status`.

    Utilisez `openclaw gateway status` et fiez-vous à ces lignes :

    - `Probe target:` (l’URL réellement utilisée par le probe)
    - `Listening:` (ce qui est réellement lié au port)
    - `Last gateway error:` (cause racine fréquente lorsque le processus est vivant mais que le port n’écoute pas)

  </Accordion>

  <Accordion title='Pourquoi openclaw gateway status affiche-t-il "Config (cli)" et "Config (service)" différents ?'>
    Vous modifiez un fichier de configuration alors que le service en exécute un autre (souvent un décalage `--profile` / `OPENCLAW_STATE_DIR`).

    Correctif :

    ```bash
    openclaw gateway install --force
    ```

    Exécutez cela depuis le même `--profile` / environnement que celui que vous voulez voir utilisé par le service.

  </Accordion>

  <Accordion title='Que signifie "another gateway instance is already listening" ?'>
    OpenClaw applique un verrou d’exécution en liant immédiatement l’écouteur WebSocket au démarrage (par défaut `ws://127.0.0.1:18789`). Si le bind échoue avec `EADDRINUSE`, il lève `GatewayLockError` indiquant qu’une autre instance écoute déjà.

    Correctif : arrêtez l’autre instance, libérez le port, ou exécutez avec `openclaw gateway --port <port>`.

  </Accordion>

  <Accordion title="Comment exécuter OpenClaw en mode distant (le client se connecte à une Gateway ailleurs) ?">
    Définissez `gateway.mode: "remote"` et pointez vers une URL WebSocket distante, éventuellement avec des identifiants distants à secret partagé :

    ```json5
    {
      gateway: {
        mode: "remote",
        remote: {
          url: "ws://gateway.tailnet:18789",
          token: "your-token",
          password: "your-password",
        },
      },
    }
    ```

    Remarques :

    - `openclaw gateway` ne démarre que lorsque `gateway.mode` vaut `local` (ou si vous passez le flag de surcharge).
    - L’application macOS surveille le fichier de configuration et change de mode en direct lorsque ces valeurs changent.
    - `gateway.remote.token` / `.password` sont uniquement des identifiants distants côté client ; ils n’activent pas à eux seuls l’authentification de la Gateway locale.

  </Accordion>

  <Accordion title='Le Control UI affiche "unauthorized" (ou se reconnecte sans cesse). Que faire ?'>
    Le chemin d’authentification de votre Gateway et la méthode d’authentification de l’UI ne correspondent pas.

    Faits (issus du code) :

    - Le Control UI conserve le token dans `sessionStorage` pour la session d’onglet de navigateur en cours et l’URL Gateway sélectionnée, de sorte que les actualisations dans le même onglet continuent de fonctionner sans restaurer une persistance longue durée du token dans `localStorage`.
    - En cas de `AUTH_TOKEN_MISMATCH`, les clients de confiance peuvent tenter un nouvel essai borné avec un token d’appareil en cache lorsque la Gateway renvoie des indications de nouvel essai (`canRetryWithDeviceToken=true`, `recommendedNextStep=retry_with_device_token`).
    - Ce nouvel essai avec token en cache réutilise désormais les scopes approuvés mis en cache stockés avec le token d’appareil. Les appelants explicites `deviceToken` / `scopes` explicites conservent toutefois leur ensemble de scopes demandé au lieu d’hériter des scopes en cache.
    - En dehors de ce chemin de nouvel essai, l’ordre de priorité de l’authentification de connexion est : secret partagé explicite token/mot de passe d’abord, puis `deviceToken` explicite, puis token d’appareil stocké, puis bootstrap token.
    - Les vérifications de portée du bootstrap token sont préfixées par rôle. La liste d’autorisation intégrée de l’opérateur bootstrap ne satisfait que les requêtes opérateur ; les rôles Node ou autres rôles non opérateur nécessitent toujours des scopes sous leur propre préfixe de rôle.

    Correctif :

    - Le plus rapide : `openclaw dashboard` (affiche + copie l’URL du tableau de bord, tente de l’ouvrir ; affiche une indication SSH en mode headless).
    - Si vous n’avez pas encore de token : `openclaw doctor --generate-gateway-token`.
    - Si vous êtes à distance, créez d’abord un tunnel : `ssh -N -L 18789:127.0.0.1:18789 user@host` puis ouvrez `http://127.0.0.1:18789/`.
    - Mode secret partagé : définissez `gateway.auth.token` / `OPENCLAW_GATEWAY_TOKEN` ou `gateway.auth.password` / `OPENCLAW_GATEWAY_PASSWORD`, puis collez le secret correspondant dans les paramètres du Control UI.
    - Mode Tailscale Serve : assurez-vous que `gateway.auth.allowTailscale` est activé et que vous ouvrez l’URL Serve, pas une URL loopback/tailnet brute qui contourne les en-têtes d’identité Tailscale.
    - Mode trusted-proxy : assurez-vous de passer par le proxy conscient de l’identité non loopback configuré, et non par un proxy loopback sur le même hôte ou une URL Gateway brute.
    - Si le décalage persiste après l’unique nouvel essai, faites tourner/réapprouvez le token d’appareil appairé :
      - `openclaw devices list`
      - `openclaw devices rotate --device <id> --role operator`
    - Si cet appel rotate indique qu’il a été refusé, vérifiez deux choses :
      - les sessions d’appareils appairés ne peuvent faire tourner que **leur propre** appareil, sauf si elles ont aussi `operator.admin`
      - les valeurs `--scope` explicites ne peuvent pas dépasser les scopes opérateur actuels de l’appelant
    - Toujours bloqué ? Exécutez `openclaw status --all` et suivez [Troubleshooting](/fr/gateway/troubleshooting). Consultez [Dashboard](/web/dashboard) pour les détails d’authentification.

  </Accordion>

  <Accordion title="J’ai défini gateway.bind tailnet mais le bind échoue et rien n’écoute">
    Le bind `tailnet` choisit une IP Tailscale parmi vos interfaces réseau (100.64.0.0/10). Si la machine n’est pas sur Tailscale (ou si l’interface est inactive), il n’y a rien à lier.

    Correctif :

    - Démarrez Tailscale sur cet hôte (afin qu’il ait une adresse 100.x), ou
    - Basculez vers `gateway.bind: "loopback"` / `"lan"`.

    Remarque : `tailnet` est explicite. `auto` préfère le loopback ; utilisez `gateway.bind: "tailnet"` lorsque vous voulez un bind réservé au tailnet.

  </Accordion>

  <Accordion title="Puis-je exécuter plusieurs Gateways sur le même hôte ?">
    En général non — une seule Gateway peut exécuter plusieurs canaux de messagerie et agents. Utilisez plusieurs Gateways uniquement lorsque vous avez besoin de redondance (par ex. bot de secours) ou d’une isolation forte.

    Oui, mais vous devez isoler :

    - `OPENCLAW_CONFIG_PATH` (configuration par instance)
    - `OPENCLAW_STATE_DIR` (état par instance)
    - `agents.defaults.workspace` (isolation du workspace)
    - `gateway.port` (ports uniques)

    Configuration rapide (recommandée) :

    - Utilisez `openclaw --profile <name> ...` par instance (crée automatiquement `~/.openclaw-<name>`).
    - Définissez un `gateway.port` unique dans chaque configuration de profil (ou passez `--port` pour les exécutions manuelles).
    - Installez un service par profil : `openclaw --profile <name> gateway install`.

    Les profils ajoutent aussi un suffixe aux noms de service (`ai.openclaw.<profile>` ; hérités `com.openclaw.*`, `openclaw-gateway-<profile>.service`, `OpenClaw Gateway (<profile>)`).
    Guide complet : [Multiple gateways](/fr/gateway/multiple-gateways).

  </Accordion>

  <Accordion title='Que signifie "invalid handshake" / code 1008 ?'>
    La Gateway est un **serveur WebSocket**, et elle s’attend à ce que le tout premier message
    soit une trame `connect`. Si elle reçoit autre chose, elle ferme la connexion
    avec le **code 1008** (violation de politique).

    Causes fréquentes :

    - Vous avez ouvert l’URL **HTTP** dans un navigateur (`http://...`) au lieu d’un client WS.
    - Vous avez utilisé le mauvais port ou chemin.
    - Un proxy ou un tunnel a supprimé les en-têtes d’authentification ou envoyé une requête non Gateway.

    Correctifs rapides :

    1. Utilisez l’URL WS : `ws://<host>:18789` (ou `wss://...` si HTTPS).
    2. N’ouvrez pas le port WS dans un onglet de navigateur normal.
    3. Si l’authentification est activée, incluez le token/mot de passe dans la trame `connect`.

    Si vous utilisez la CLI ou le TUI, l’URL doit ressembler à :

    ```
    openclaw tui --url ws://<host>:18789 --token <token>
    ```

    Détails du protocole : [Gateway protocol](/fr/gateway/protocol).

  </Accordion>
</AccordionGroup>

## Journalisation et débogage

<AccordionGroup>
  <Accordion title="Où se trouvent les journaux ?">
    Journaux de fichiers (structurés) :

    ```
    /tmp/openclaw/openclaw-YYYY-MM-DD.log
    ```

    Vous pouvez définir un chemin stable via `logging.file`. Le niveau de journal de fichier est contrôlé par `logging.level`. La verbosité console est contrôlée par `--verbose` et `logging.consoleLevel`.

    Fin de journal la plus rapide :

    ```bash
    openclaw logs --follow
    ```

    Journaux du service/superviseur (lorsque la Gateway s’exécute via launchd/systemd) :

    - macOS : `$OPENCLAW_STATE_DIR/logs/gateway.log` et `gateway.err.log` (par défaut : `~/.openclaw/logs/...` ; les profils utilisent `~/.openclaw-<profile>/logs/...`)
    - Linux : `journalctl --user -u openclaw-gateway[-<profile>].service -n 200 --no-pager`
    - Windows : `schtasks /Query /TN "OpenClaw Gateway (<profile>)" /V /FO LIST`

    Consultez [Troubleshooting](/fr/gateway/troubleshooting) pour plus d’informations.

  </Accordion>

  <Accordion title="Comment démarrer/arrêter/redémarrer le service Gateway ?">
    Utilisez les helpers Gateway :

    ```bash
    openclaw gateway status
    openclaw gateway restart
    ```

    Si vous exécutez la Gateway manuellement, `openclaw gateway --force` peut récupérer le port. Consultez [Gateway](/fr/gateway).

  </Accordion>

  <Accordion title="J’ai fermé mon terminal sous Windows — comment redémarrer OpenClaw ?">
    Il existe **deux modes d’installation Windows** :

    **1) WSL2 (recommandé) :** la Gateway s’exécute dans Linux.

    Ouvrez PowerShell, entrez dans WSL, puis redémarrez :

    ```powershell
    wsl
    openclaw gateway status
    openclaw gateway restart
    ```

    Si vous n’avez jamais installé le service, démarrez-la au premier plan :

    ```bash
    openclaw gateway run
    ```

    **2) Windows natif (non recommandé) :** la Gateway s’exécute directement dans Windows.

    Ouvrez PowerShell et exécutez :

    ```powershell
    openclaw gateway status
    openclaw gateway restart
    ```

    Si vous l’exécutez manuellement (sans service), utilisez :

    ```powershell
    openclaw gateway run
    ```

    Documentation : [Windows (WSL2)](/fr/platforms/windows), [Gateway service runbook](/fr/gateway).

  </Accordion>

  <Accordion title="La Gateway est active mais les réponses n’arrivent jamais. Que dois-je vérifier ?">
    Commencez par un balayage rapide de l’état :

    ```bash
    openclaw status
    openclaw models status
    openclaw channels status
    openclaw logs --follow
    ```

    Causes fréquentes :

    - L’authentification du modèle n’est pas chargée sur l’**hôte Gateway** (vérifiez `models status`).
    - L’appairage du canal / la liste d’autorisation bloque les réponses (vérifiez la configuration du canal + les journaux).
    - WebChat/Dashboard est ouvert sans le bon token.

    Si vous êtes à distance, confirmez que la connexion tunnel/Tailscale est active et que le
    WebSocket Gateway est accessible.

    Documentation : [Channels](/fr/channels), [Troubleshooting](/fr/gateway/troubleshooting), [Remote access](/fr/gateway/remote).

  </Accordion>

  <Accordion title='"Disconnected from gateway: no reason" — que faire ?'>
    Cela signifie généralement que l’UI a perdu la connexion WebSocket. Vérifiez :

    1. La Gateway est-elle en cours d’exécution ? `openclaw gateway status`
    2. La Gateway est-elle saine ? `openclaw status`
    3. L’UI a-t-elle le bon token ? `openclaw dashboard`
    4. Si vous êtes à distance, le lien tunnel/Tailscale est-il actif ?

    Puis suivez les journaux :

    ```bash
    openclaw logs --follow
    ```

    Documentation : [Dashboard](/web/dashboard), [Remote access](/fr/gateway/remote), [Troubleshooting](/fr/gateway/troubleshooting).

  </Accordion>

  <Accordion title="Telegram setMyCommands échoue. Que dois-je vérifier ?">
    Commencez par les journaux et le statut du canal :

    ```bash
    openclaw channels status
    openclaw channels logs --channel telegram
    ```

    Faites ensuite correspondre l’erreur :

    - `BOT_COMMANDS_TOO_MUCH` : le menu Telegram contient trop d’entrées. OpenClaw réduit déjà jusqu’à la limite Telegram et réessaie avec moins de commandes, mais certaines entrées du menu doivent encore être supprimées. Réduisez les commandes de plugin/skill/personnalisées, ou désactivez `channels.telegram.commands.native` si vous n’avez pas besoin du menu.
    - `TypeError: fetch failed`, `Network request for 'setMyCommands' failed!`, ou erreurs réseau similaires : si vous êtes sur un VPS ou derrière un proxy, confirmez que l’HTTPS sortant est autorisé et que le DNS fonctionne pour `api.telegram.org`.

    Si la Gateway est distante, assurez-vous de consulter les journaux sur l’hôte Gateway.

    Documentation : [Telegram](/fr/channels/telegram), [Channel troubleshooting](/fr/channels/troubleshooting).

  </Accordion>

  <Accordion title="Le TUI n’affiche aucune sortie. Que dois-je vérifier ?">
    Confirmez d’abord que la Gateway est accessible et que l’agent peut s’exécuter :

    ```bash
    openclaw status
    openclaw models status
    openclaw logs --follow
    ```

    Dans le TUI, utilisez `/status` pour voir l’état actuel. Si vous attendez des réponses dans un
    canal de chat, assurez-vous que la livraison est activée (`/deliver on`).

    Documentation : [TUI](/web/tui), [Slash commands](/fr/tools/slash-commands).

  </Accordion>

  <Accordion title="Comment arrêter complètement puis redémarrer la Gateway ?">
    Si vous avez installé le service :

    ```bash
    openclaw gateway stop
    openclaw gateway start
    ```

    Cela arrête/démarre le **service supervisé** (launchd sur macOS, systemd sur Linux).
    Utilisez ceci lorsque la Gateway s’exécute en arrière-plan comme daemon.

    Si vous l’exécutez au premier plan, arrêtez-la avec Ctrl-C, puis :

    ```bash
    openclaw gateway run
    ```

    Documentation : [Gateway service runbook](/fr/gateway).

  </Accordion>

  <Accordion title="ELI5 : openclaw gateway restart vs openclaw gateway">
    - `openclaw gateway restart` : redémarre le **service d’arrière-plan** (launchd/systemd).
    - `openclaw gateway` : exécute la Gateway **au premier plan** pour cette session de terminal.

    Si vous avez installé le service, utilisez les commandes Gateway. Utilisez `openclaw gateway` lorsque
    vous voulez une exécution ponctuelle au premier plan.

  </Accordion>

  <Accordion title="Le moyen le plus rapide d’obtenir plus de détails lorsqu’un échec se produit">
    Démarrez la Gateway avec `--verbose` pour obtenir plus de détails dans la console. Inspectez ensuite le fichier journal pour l’authentification des canaux, le routage des modèles et les erreurs RPC.
  </Accordion>
</AccordionGroup>

## Médias et pièces jointes

<AccordionGroup>
  <Accordion title="Ma skill a généré une image/un PDF, mais rien n’a été envoyé">
    Les pièces jointes sortantes de l’agent doivent inclure une ligne `MEDIA:<path-or-url>` (sur sa propre ligne). Consultez [OpenClaw assistant setup](/fr/start/openclaw) et [Agent send](/fr/tools/agent-send).

    Envoi via CLI :

    ```bash
    openclaw message send --target +15555550123 --message "Here you go" --media /path/to/file.png
    ```

    Vérifiez aussi :

    - Le canal cible prend en charge les médias sortants et n’est pas bloqué par les listes d’autorisation.
    - Le fichier respecte les limites de taille du fournisseur (les images sont redimensionnées à un maximum de 2048 px).
    - `tools.fs.workspaceOnly=true` limite les envois de chemins locaux au workspace, au temp/media-store et aux fichiers validés par le sandbox.
    - `tools.fs.workspaceOnly=false` permet à `MEDIA:` d’envoyer des fichiers locaux de l’hôte que l’agent peut déjà lire, mais uniquement pour les médias et les types de documents sûrs (images, audio, vidéo, PDF et documents Office). Les fichiers texte brut et les fichiers ressemblant à des secrets restent bloqués.

    Consultez [Images](/fr/nodes/images).

  </Accordion>
</AccordionGroup>

## Sécurité et contrôle d’accès

<AccordionGroup>
  <Accordion title="Est-il sûr d’exposer OpenClaw à des messages privés entrants ?">
    Traitez les messages privés entrants comme des entrées non fiables. Les valeurs par défaut sont conçues pour réduire le risque :

    - Le comportement par défaut sur les canaux compatibles DM est l’**appairage** :
      - Les expéditeurs inconnus reçoivent un code d’appairage ; le bot ne traite pas leur message.
      - Approuvez avec : `openclaw pairing approve --channel <channel> [--account <id>] <code>`
      - Les demandes en attente sont limitées à **3 par canal** ; vérifiez `openclaw pairing list --channel <channel> [--account <id>]` si un code n’est pas arrivé.
    - Ouvrir publiquement les messages privés exige une activation explicite (`dmPolicy: "open"` et liste d’autorisation `"*"`).

    Exécutez `openclaw doctor` pour faire apparaître les politiques DM risquées.

  </Accordion>

  <Accordion title="L’injection de prompt est-elle seulement un problème pour les bots publics ?">
    Non. L’injection de prompt concerne le **contenu non fiable**, pas seulement les personnes autorisées à envoyer des messages privés au bot.
    Si votre assistant lit du contenu externe (recherche/récupération web, pages de navigateur, e-mails,
    documents, pièces jointes, journaux collés), ce contenu peut inclure des instructions qui essaient
    de détourner le modèle. Cela peut se produire même si **vous êtes le seul expéditeur**.

    Le plus grand risque survient lorsque les outils sont activés : le modèle peut être amené à
    exfiltrer du contexte ou à appeler des outils en votre nom. Réduisez le rayon d’impact en :

    - utilisant un agent « lecteur » en lecture seule ou sans outils pour résumer le contenu non fiable
    - gardant `web_search` / `web_fetch` / `browser` désactivés pour les agents avec outils activés
    - traitant aussi le texte décodé des fichiers/documents comme non fiable : OpenResponses
      `input_file` et l’extraction depuis les pièces jointes média encapsulent tous deux le texte extrait dans
      des marqueurs explicites de frontière de contenu externe au lieu de transmettre le texte brut du fichier
    - utilisant le sandboxing et des listes d’autorisation d’outils strictes

    Détails : [Security](/fr/gateway/security).

  </Accordion>

  <Accordion title="Mon bot devrait-il avoir sa propre adresse e-mail, son propre compte GitHub ou son propre numéro de téléphone ?">
    Oui, pour la plupart des configurations. Isoler le bot avec des comptes et numéros de téléphone séparés
    réduit le rayon d’impact si quelque chose se passe mal. Cela facilite aussi la rotation
    des identifiants ou la révocation d’accès sans impacter vos comptes personnels.

    Commencez petit. Donnez l’accès uniquement aux outils et comptes dont vous avez réellement besoin, puis élargissez
    plus tard si nécessaire.

    Documentation : [Security](/fr/gateway/security), [Pairing](/fr/channels/pairing).

  </Accordion>

  <Accordion title="Puis-je lui donner de l’autonomie sur mes messages texte et est-ce sûr ?">
    Nous **ne recommandons pas** une autonomie complète sur vos messages personnels. Le schéma le plus sûr est :

    - Gardez les DM en **mode appairage** ou avec une liste d’autorisation stricte.
    - Utilisez un **numéro ou un compte séparé** si vous voulez qu’il envoie des messages en votre nom.
    - Laissez-le rédiger, puis **approuvez avant envoi**.

    Si vous voulez expérimenter, faites-le sur un compte dédié et gardez-le isolé. Consultez
    [Security](/fr/gateway/security).

  </Accordion>

  <Accordion title="Puis-je utiliser des modèles moins chers pour des tâches d’assistant personnel ?">
    Oui, **si** l’agent est uniquement orienté chat et que les entrées sont fiables. Les petits modèles sont
    plus sensibles au détournement d’instructions, donc évitez-les pour les agents avec outils activés
    ou lorsqu’ils lisent du contenu non fiable. Si vous devez utiliser un modèle plus petit, verrouillez
    les outils et exécutez-le dans un sandbox. Consultez [Security](/fr/gateway/security).
  </Accordion>

  <Accordion title="J’ai exécuté /start dans Telegram mais je n’ai pas reçu de code d’appairage">
    Les codes d’appairage sont envoyés **uniquement** lorsqu’un expéditeur inconnu envoie un message au bot et que
    `dmPolicy: "pairing"` est activé. `/start` à lui seul ne génère pas de code.

    Vérifiez les demandes en attente :

    ```bash
    openclaw pairing list telegram
    ```

    Si vous voulez un accès immédiat, ajoutez votre identifiant expéditeur à la liste d’autorisation ou définissez `dmPolicy: "open"`
    pour ce compte.

  </Accordion>

  <Accordion title="WhatsApp : enverra-t-il des messages à mes contacts ? Comment fonctionne l’appairage ?">
    Non. La politique DM WhatsApp par défaut est l’**appairage**. Les expéditeurs inconnus ne reçoivent qu’un code d’appairage et leur message **n’est pas traité**. OpenClaw ne répond qu’aux chats qu’il reçoit ou aux envois explicites que vous déclenchez.

    Approuvez l’appairage avec :

    ```bash
    openclaw pairing approve whatsapp <code>
    ```

    Lister les demandes en attente :

    ```bash
    openclaw pairing list whatsapp
    ```

    La demande de numéro de téléphone dans l’assistant est utilisée pour définir votre **liste d’autorisation/propriétaire** afin que vos propres DM soient autorisés. Elle n’est pas utilisée pour l’envoi automatique. Si vous utilisez votre numéro WhatsApp personnel, utilisez ce numéro et activez `channels.whatsapp.selfChatMode`.

  </Accordion>
</AccordionGroup>

## Commandes de chat, interruption des tâches, et « il ne s’arrête pas »

<AccordionGroup>
  <Accordion title="Comment empêcher les messages système internes de s’afficher dans le chat ?">
    La plupart des messages internes ou d’outil n’apparaissent que lorsque **verbose**, **trace**, ou **reasoning** est activé
    pour cette session.

    Corrigez cela dans le chat où vous le voyez :

    ```
    /verbose off
    /trace off
    /reasoning off
    ```

    Si cela reste bruyant, vérifiez les paramètres de session dans le Control UI et définissez verbose
    sur **inherit**. Confirmez aussi que vous n’utilisez pas un profil de bot avec `verboseDefault` défini
    sur `on` dans la configuration.

    Documentation : [Thinking and verbose](/fr/tools/thinking), [Security](/fr/gateway/security#reasoning-verbose-output-in-groups).

  </Accordion>

  <Accordion title="Comment arrêter/annuler une tâche en cours ?">
    Envoyez l’un de ces messages **comme message autonome** (sans slash) :

    ```
    stop
    stop action
    stop current action
    stop run
    stop current run
    stop agent
    stop the agent
    stop openclaw
    openclaw stop
    stop don't do anything
    stop do not do anything
    stop doing anything
    please stop
    stop please
    abort
    esc
    wait
    exit
    interrupt
    ```

    Ce sont des déclencheurs d’arrêt (pas des slash commands).

    Pour les processus en arrière-plan (issus de l’outil exec), vous pouvez demander à l’agent d’exécuter :

    ```
    process action:kill sessionId:XXX
    ```

    Vue d’ensemble des slash commands : consultez [Slash commands](/fr/tools/slash-commands).

    La plupart des commandes doivent être envoyées comme **message autonome** commençant par `/`, mais quelques raccourcis (comme `/status`) fonctionnent aussi en ligne pour les expéditeurs autorisés.

  </Accordion>

  <Accordion title='Comment envoyer un message Discord depuis Telegram ? ("Cross-context messaging denied")'>
    OpenClaw bloque par défaut la messagerie **inter-fournisseurs**. Si un appel d’outil est lié
    à Telegram, il n’enverra pas vers Discord sauf si vous l’autorisez explicitement.

    Activez la messagerie inter-fournisseurs pour l’agent :

    ```json5
    {
      tools: {
        message: {
          crossContext: {
            allowAcrossProviders: true,
            marker: { enabled: true, prefix: "[from {channel}] " },
          },
        },
      },
    }
    ```

    Redémarrez la Gateway après modification de la configuration.

  </Accordion>

  <Accordion title='Pourquoi ai-je l’impression que le bot "ignore" les messages envoyés en rafale ?'>
    Le mode de file contrôle la façon dont les nouveaux messages interagissent avec une exécution en cours. Utilisez `/queue` pour changer de mode :

    - `steer` - les nouveaux messages redirigent la tâche en cours
    - `followup` - traite les messages un par un
    - `collect` - regroupe les messages et répond une seule fois (par défaut)
    - `steer-backlog` - redirige maintenant, puis traite l’arriéré
    - `interrupt` - interrompt l’exécution actuelle et redémarre à neuf

    Vous pouvez ajouter des options comme `debounce:2s cap:25 drop:summarize` pour les modes de suivi.

  </Accordion>
</AccordionGroup>

## Divers

<AccordionGroup>
  <Accordion title='Quel est le modèle par défaut pour Anthropic avec une clé API ?'>
    Dans OpenClaw, les identifiants et la sélection du modèle sont séparés. Définir `ANTHROPIC_API_KEY` (ou stocker une clé API Anthropic dans les profils d’authentification) active l’authentification, mais le véritable modèle par défaut est celui que vous configurez dans `agents.defaults.model.primary` (par exemple, `anthropic/claude-sonnet-4-6` ou `anthropic/claude-opus-4-6`). Si vous voyez `No credentials found for profile "anthropic:default"`, cela signifie que la Gateway n’a pas pu trouver d’identifiants Anthropic dans le `auth-profiles.json` attendu pour l’agent en cours d’exécution.
  </Accordion>
</AccordionGroup>

---

Toujours bloqué ? Demandez dans [Discord](https://discord.com/invite/clawd) ou ouvrez une [discussion GitHub](https://github.com/openclaw/openclaw/discussions).
