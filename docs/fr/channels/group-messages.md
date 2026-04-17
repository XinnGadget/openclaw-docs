---
read_when:
    - Modification des règles ou des mentions pour les messages de groupe
summary: Comportement et configuration pour la gestion des messages de groupe WhatsApp (`mentionPatterns` sont partagés entre les surfaces)
title: Messages de groupe
x-i18n:
    generated_at: "2026-04-12T23:28:13Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5d9484dd1de74d42f8dce4c3ac80d60c24864df30a7802e64893ef55506230fe
    source_path: channels/group-messages.md
    workflow: 15
---

# Messages de groupe (canal web WhatsApp)

Objectif : permettre à Clawd de rester dans des groupes WhatsApp, de ne se réveiller que lorsqu’il est sollicité, et de garder ce fil séparé de la session de message privé personnelle.

Remarque : `agents.list[].groupChat.mentionPatterns` est désormais utilisé aussi par Telegram/Discord/Slack/iMessage ; cette documentation se concentre sur le comportement spécifique à WhatsApp. Pour les configurations multi-agent, définissez `agents.list[].groupChat.mentionPatterns` par agent (ou utilisez `messages.groupChat.mentionPatterns` comme solution de repli globale).

## Implémentation actuelle (2025-12-03)

- Modes d’activation : `mention` (par défaut) ou `always`. `mention` nécessite un signalement (véritables @-mentions WhatsApp via `mentionedJids`, motifs regex sûrs, ou le numéro E.164 du bot n’importe où dans le texte). `always` réveille l’agent à chaque message, mais il ne doit répondre que lorsqu’il peut apporter une réelle valeur ajoutée ; sinon il renvoie le jeton silencieux exact `NO_REPLY` / `no_reply`. Les valeurs par défaut peuvent être définies dans la configuration (`channels.whatsapp.groups`) et remplacées par groupe via `/activation`. Lorsque `channels.whatsapp.groups` est défini, il sert aussi de liste d’autorisation des groupes (incluez `"*"` pour tous les autoriser).
- Politique de groupe : `channels.whatsapp.groupPolicy` contrôle si les messages de groupe sont acceptés (`open|disabled|allowlist`). `allowlist` utilise `channels.whatsapp.groupAllowFrom` (repli : `channels.whatsapp.allowFrom` explicite). La valeur par défaut est `allowlist` (bloqué tant que vous n’ajoutez pas d’expéditeurs).
- Sessions par groupe : les clés de session ressemblent à `agent:<agentId>:whatsapp:group:<jid>`, de sorte que des commandes comme `/verbose on`, `/trace on` ou `/think high` (envoyées comme messages autonomes) sont limitées à ce groupe ; l’état du message privé personnel n’est pas modifié. Les Heartbeat sont ignorés pour les fils de groupe.
- Injection de contexte : les messages de groupe **en attente uniquement** (50 par défaut) qui _n’ont pas_ déclenché d’exécution sont préfixés sous `[Chat messages since your last reply - for context]`, avec la ligne déclenchante sous `[Current message - respond to this]`. Les messages déjà présents dans la session ne sont pas réinjectés.
- Affichage de l’expéditeur : chaque lot de groupe se termine désormais par `[from: Sender Name (+E164)]` afin que Pi sache qui parle.
- Éphémères / view-once : nous les déballons avant d’extraire le texte/les mentions, de sorte que les sollicitations qu’ils contiennent déclenchent quand même l’agent.
- Prompt système de groupe : au premier tour d’une session de groupe (et chaque fois que `/activation` change le mode), nous injectons un court texte dans le prompt système, par exemple `You are replying inside the WhatsApp group "<subject>". Group members: Alice (+44...), Bob (+43...), … Activation: trigger-only … Address the specific sender noted in the message context.` Si les métadonnées ne sont pas disponibles, nous indiquons tout de même à l’agent qu’il s’agit d’une discussion de groupe.

## Exemple de configuration (WhatsApp)

Ajoutez un bloc `groupChat` à `~/.openclaw/openclaw.json` pour que les sollicitations par nom d’affichage fonctionnent même lorsque WhatsApp supprime le `@` visuel dans le corps du texte :

```json5
{
  channels: {
    whatsapp: {
      groups: {
        "*": { requireMention: true },
      },
    },
  },
  agents: {
    list: [
      {
        id: "main",
        groupChat: {
          historyLimit: 50,
          mentionPatterns: ["@?openclaw", "\\+?15555550123"],
        },
      },
    ],
  },
}
```

Remarques :

- Les regex ne tiennent pas compte de la casse et utilisent les mêmes garde-fous de regex sûres que les autres surfaces de configuration utilisant des regex ; les motifs invalides et les répétitions imbriquées non sûres sont ignorés.
- WhatsApp envoie toujours des mentions canoniques via `mentionedJids` lorsqu’une personne sélectionne le contact, donc le repli sur le numéro est rarement nécessaire, mais reste un filet de sécurité utile.

### Commande d’activation (propriétaire uniquement)

Utilisez la commande de discussion de groupe :

- `/activation mention`
- `/activation always`

Seul le numéro du propriétaire (depuis `channels.whatsapp.allowFrom`, ou le numéro E.164 du bot si non défini) peut modifier cela. Envoyez `/status` comme message autonome dans le groupe pour voir le mode d’activation actuel.

## Comment l’utiliser

1. Ajoutez votre compte WhatsApp (celui qui exécute OpenClaw) au groupe.
2. Dites `@openclaw …` (ou incluez le numéro). Seuls les expéditeurs autorisés peuvent le déclencher, sauf si vous définissez `groupPolicy: "open"`.
3. Le prompt de l’agent inclura le contexte récent du groupe ainsi que le marqueur final `[from: …]` afin qu’il puisse s’adresser à la bonne personne.
4. Les directives au niveau de la session (`/verbose on`, `/trace on`, `/think high`, `/new` ou `/reset`, `/compact`) s’appliquent uniquement à la session de ce groupe ; envoyez-les comme messages autonomes pour qu’elles soient prises en compte. Votre session de message privé personnelle reste indépendante.

## Test / vérification

- Vérification manuelle :
  - Envoyez un signalement `@openclaw` dans le groupe et confirmez une réponse qui fait référence au nom de l’expéditeur.
  - Envoyez un deuxième signalement et vérifiez que le bloc d’historique est inclus puis effacé au tour suivant.
- Vérifiez les journaux de la Gateway (exécutée avec `--verbose`) pour voir les entrées `inbound web message` affichant `from: <groupJid>` et le suffixe `[from: …]`.

## Points à considérer

- Les Heartbeat sont volontairement ignorés pour les groupes afin d’éviter des diffusions trop bruyantes.
- La suppression d’écho utilise la chaîne combinée du lot ; si vous envoyez deux fois un texte identique sans mention, seul le premier recevra une réponse.
- Les entrées du magasin de sessions apparaîtront sous la forme `agent:<agentId>:whatsapp:group:<jid>` dans le magasin de sessions (`~/.openclaw/agents/<agentId>/sessions/sessions.json` par défaut) ; une entrée manquante signifie simplement que le groupe n’a pas encore déclenché d’exécution.
- Les indicateurs de saisie dans les groupes suivent `agents.defaults.typingMode` (par défaut : `message` lorsqu’il n’y a pas de mention).
