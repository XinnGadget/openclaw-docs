---
read_when:
    - Première configuration à partir de zéro
    - Vous voulez le chemin le plus rapide vers un chat fonctionnel
summary: Installez OpenClaw et lancez votre premier chat en quelques minutes.
title: Getting Started
x-i18n:
    generated_at: "2026-04-05T10:51:21Z"
    model: gpt-5.4
    provider: openai
    source_hash: c43eee6f0d3f593e3cf0767bfacb3e0ae38f51a2615d594303786ae1d4a6d2c3
    source_path: start/getting-started.md
    workflow: 15
---

# Getting Started

Installez OpenClaw, lancez l’onboarding et discutez avec votre assistant IA — le tout en
environ 5 minutes. À la fin, vous aurez une Gateway en cours d’exécution, une authentification
configurée et une session de chat fonctionnelle.

## Ce dont vous avez besoin

- **Node.js** — Node 24 recommandé (Node 22.14+ également pris en charge)
- **Une clé API** d’un fournisseur de modèles (Anthropic, OpenAI, Google, etc.) — l’onboarding vous la demandera

<Tip>
Vérifiez votre version de Node avec `node --version`.
**Utilisateurs Windows :** Windows natif et WSL2 sont tous deux pris en charge. WSL2 est plus
stable et recommandé pour l’expérience complète. Voir [Windows](/platforms/windows).
Besoin d’installer Node ? Voir [Configuration de Node](/install/node).
</Tip>

## Configuration rapide

<Steps>
  <Step title="Installer OpenClaw">
    <Tabs>
      <Tab title="macOS / Linux">
        ```bash
        curl -fsSL https://openclaw.ai/install.sh | bash
        ```
        <img
  src="/assets/install-script.svg"
  alt="Processus du script d’installation"
  className="rounded-lg"
/>
      </Tab>
      <Tab title="Windows (PowerShell)">
        ```powershell
        iwr -useb https://openclaw.ai/install.ps1 | iex
        ```
      </Tab>
    </Tabs>

    <Note>
    Autres méthodes d’installation (Docker, Nix, npm) : [Installation](/install).
    </Note>

  </Step>
  <Step title="Lancer l’onboarding">
    ```bash
    openclaw onboard --install-daemon
    ```

    L’assistant vous guide pour choisir un fournisseur de modèles, définir une clé API
    et configurer la Gateway. Cela prend environ 2 minutes.

    Voir [Onboarding (CLI)](/start/wizard) pour la référence complète.

  </Step>
  <Step title="Vérifier que la Gateway est en cours d’exécution">
    ```bash
    openclaw gateway status
    ```

    Vous devriez voir que la Gateway écoute sur le port 18789.

  </Step>
  <Step title="Ouvrir le tableau de bord">
    ```bash
    openclaw dashboard
    ```

    Cela ouvre la Control UI dans votre navigateur. Si elle se charge, tout fonctionne.

  </Step>
  <Step title="Envoyer votre premier message">
    Saisissez un message dans le chat de la Control UI et vous devriez recevoir une réponse de l’IA.

    Vous voulez plutôt discuter depuis votre téléphone ? Le canal le plus rapide à configurer est
    [Telegram](/channels/telegram) (juste un jeton de bot). Voir [Canaux](/channels)
    pour toutes les options.

  </Step>
</Steps>

<Accordion title="Avancé : monter une version personnalisée de la Control UI">
  Si vous maintenez une version localisée ou personnalisée du tableau de bord, pointez
  `gateway.controlUi.root` vers un répertoire qui contient vos ressources statiques
  compilées et `index.html`.

```bash
mkdir -p "$HOME/.openclaw/control-ui-custom"
# Copy your built static files into that directory.
```

Puis définissez :

```json
{
  "gateway": {
    "controlUi": {
      "enabled": true,
      "root": "$HOME/.openclaw/control-ui-custom"
    }
  }
}
```

Redémarrez la gateway et rouvrez le tableau de bord :

```bash
openclaw gateway restart
openclaw dashboard
```

</Accordion>

## Que faire ensuite

<Columns>
  <Card title="Connecter un canal" href="/channels" icon="message-square">
    Discord, Feishu, iMessage, Matrix, Microsoft Teams, Signal, Slack, Telegram, WhatsApp, Zalo, et plus encore.
  </Card>
  <Card title="Appairage et sécurité" href="/channels/pairing" icon="shield">
    Contrôlez qui peut envoyer des messages à votre agent.
  </Card>
  <Card title="Configurer la Gateway" href="/gateway/configuration" icon="settings">
    Modèles, outils, sandbox et paramètres avancés.
  </Card>
  <Card title="Parcourir les outils" href="/tools" icon="wrench">
    Navigateur, exécution, recherche web, Skills et plugins.
  </Card>
</Columns>

<Accordion title="Avancé : variables d’environnement">
  Si vous exécutez OpenClaw avec un compte de service ou si vous voulez des chemins personnalisés :

- `OPENCLAW_HOME` — répertoire personnel pour la résolution des chemins internes
- `OPENCLAW_STATE_DIR` — remplace le répertoire d’état
- `OPENCLAW_CONFIG_PATH` — remplace le chemin du fichier de configuration

Référence complète : [Variables d’environnement](/help/environment).
</Accordion>
