---
read_when:
    - Configuration d’OpenClaw sur Hostinger
    - Vous recherchez un VPS géré pour OpenClaw
    - Utiliser OpenClaw en 1 clic sur Hostinger
summary: Héberger OpenClaw sur Hostinger
title: Hostinger
x-i18n:
    generated_at: "2026-04-14T02:08:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: cf173cdcf6344f8ee22e839a27f4e063a3a102186f9acc07c4a33d4794e2c034
    source_path: install/hostinger.md
    workflow: 15
---

# Hostinger

Exécutez une Gateway OpenClaw persistante sur [Hostinger](https://www.hostinger.com/openclaw) via un déploiement géré en **1 clic** ou une installation sur **VPS**.

## Prérequis

- Compte Hostinger ([inscription](https://www.hostinger.com/openclaw))
- Environ 5 à 10 minutes

## Option A : OpenClaw en 1 clic

La façon la plus rapide de commencer. Hostinger gère l’infrastructure, Docker et les mises à jour automatiques.

<Steps>
  <Step title="Acheter et lancer">
    1. Depuis la [page OpenClaw de Hostinger](https://www.hostinger.com/openclaw), choisissez une offre OpenClaw gérée et finalisez la commande.

    <Note>
    Lors du paiement, vous pouvez sélectionner des crédits **Ready-to-Use AI** préachetés et intégrés instantanément dans OpenClaw : aucun compte externe ni clé API d’autres fournisseurs n’est nécessaire. Vous pouvez commencer à discuter immédiatement. Vous pouvez aussi fournir votre propre clé d’Anthropic, OpenAI, Google Gemini ou xAI pendant la configuration.
    </Note>

  </Step>

  <Step title="Sélectionner un canal de messagerie">
    Choisissez un ou plusieurs canaux à connecter :

    - **WhatsApp** -- scannez le code QR affiché dans l’assistant de configuration.
    - **Telegram** -- collez le jeton du bot depuis [BotFather](https://t.me/BotFather).

  </Step>

  <Step title="Terminer l’installation">
    Cliquez sur **Finish** pour déployer l’instance. Une fois prête, accédez au tableau de bord OpenClaw depuis **OpenClaw Overview** dans hPanel.
  </Step>

</Steps>

## Option B : OpenClaw sur VPS

Plus de contrôle sur votre serveur. Hostinger déploie OpenClaw via Docker sur votre VPS et vous le gérez via le **Docker Manager** dans hPanel.

<Steps>
  <Step title="Acheter un VPS">
    1. Depuis la [page OpenClaw de Hostinger](https://www.hostinger.com/openclaw), choisissez une offre OpenClaw sur VPS et finalisez la commande.

    <Note>
    Vous pouvez sélectionner des crédits **Ready-to-Use AI** lors du paiement : ils sont préachetés et intégrés instantanément dans OpenClaw, ce qui vous permet de commencer à discuter sans aucun compte externe ni clé API d’autres fournisseurs.
    </Note>

  </Step>

  <Step title="Configurer OpenClaw">
    Une fois le VPS provisionné, remplissez les champs de configuration :

    - **Gateway token** -- généré automatiquement ; enregistrez-le pour l’utiliser plus tard.
    - **Numéro WhatsApp** -- votre numéro avec l’indicatif du pays (facultatif).
    - **Jeton du bot Telegram** -- depuis [BotFather](https://t.me/BotFather) (facultatif).
    - **Clés API** -- nécessaires uniquement si vous n’avez pas sélectionné de crédits Ready-to-Use AI lors du paiement.

  </Step>

  <Step title="Démarrer OpenClaw">
    Cliquez sur **Deploy**. Une fois le service en cours d’exécution, ouvrez le tableau de bord OpenClaw depuis hPanel en cliquant sur **Open**.
  </Step>

</Steps>

Les journaux, redémarrages et mises à jour sont gérés directement depuis l’interface Docker Manager dans hPanel. Pour mettre à jour, appuyez sur **Update** dans Docker Manager ; cela récupérera la dernière image.

## Vérifier votre configuration

Envoyez « Hi » à votre assistant sur le canal que vous avez connecté. OpenClaw répondra et vous guidera dans la configuration initiale de vos préférences.

## Dépannage

**Le tableau de bord ne se charge pas** -- Attendez quelques minutes que le conteneur termine son provisionnement. Vérifiez les journaux du Docker Manager dans hPanel.

**Le conteneur Docker redémarre sans arrêt** -- Ouvrez les journaux du Docker Manager et recherchez des erreurs de configuration (jetons manquants, clés API invalides).

**Le bot Telegram ne répond pas** -- Envoyez votre message de code d’appairage depuis Telegram directement comme message dans votre discussion OpenClaw afin de terminer la connexion.

## Prochaines étapes

- [Canaux](/fr/channels) -- connectez Telegram, WhatsApp, Discord et plus encore
- [Configuration de la Gateway](/fr/gateway/configuration) -- toutes les options de configuration
