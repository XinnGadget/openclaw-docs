---
read_when:
    - Travailler sur les réactions dans n’importe quel canal
    - Comprendre en quoi les réactions emoji diffèrent selon les plateformes
summary: Sémantique de l’outil de réaction sur tous les canaux pris en charge
title: Réactions
x-i18n:
    generated_at: "2026-04-11T02:47:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: cfac31b7f0effc89cc696e3cf34cd89503ccdbb28996723945025e4b6e159986
    source_path: tools/reactions.md
    workflow: 15
---

# Réactions

L’agent peut ajouter et supprimer des réactions emoji sur les messages à l’aide de l’outil `message`
avec l’action `react`. Le comportement des réactions varie selon le canal.

## Fonctionnement

```json
{
  "action": "react",
  "messageId": "msg-123",
  "emoji": "thumbsup"
}
```

- `emoji` est requis lors de l’ajout d’une réaction.
- Définissez `emoji` sur une chaîne vide (`""`) pour supprimer la/les réaction(s) du bot.
- Définissez `remove: true` pour supprimer un emoji spécifique (nécessite un `emoji` non vide).

## Comportement selon le canal

<AccordionGroup>
  <Accordion title="Discord et Slack">
    - Un `emoji` vide supprime toutes les réactions du bot sur le message.
    - `remove: true` supprime uniquement l’emoji spécifié.
  </Accordion>

  <Accordion title="Google Chat">
    - Un `emoji` vide supprime les réactions de l’application sur le message.
    - `remove: true` supprime uniquement l’emoji spécifié.
  </Accordion>

  <Accordion title="Telegram">
    - Un `emoji` vide supprime les réactions du bot.
    - `remove: true` supprime également les réactions mais nécessite toujours un `emoji` non vide pour la validation de l’outil.
  </Accordion>

  <Accordion title="WhatsApp">
    - Un `emoji` vide supprime la réaction du bot.
    - `remove: true` est converti en emoji vide en interne (nécessite quand même `emoji` dans l’appel de l’outil).
  </Accordion>

  <Accordion title="Zalo Personal (zalouser)">
    - Nécessite un `emoji` non vide.
    - `remove: true` supprime cette réaction emoji spécifique.
  </Accordion>

  <Accordion title="Feishu/Lark">
    - Utilisez l’outil `feishu_reaction` avec les actions `add`, `remove`, et `list`.
    - L’ajout/la suppression nécessite `emoji_type` ; la suppression nécessite aussi `reaction_id`.
  </Accordion>

  <Accordion title="Signal">
    - Les notifications de réaction entrantes sont contrôlées par `channels.signal.reactionNotifications` : `"off"` les désactive, `"own"` (par défaut) émet des événements lorsque les utilisateurs réagissent aux messages du bot, et `"all"` émet des événements pour toutes les réactions.
  </Accordion>
</AccordionGroup>

## Niveau de réaction

La configuration `reactionLevel` par canal contrôle dans quelle mesure l’agent utilise les réactions. Les valeurs sont généralement `off`, `ack`, `minimal`, ou `extensive`.

- [Telegram reactionLevel](/fr/channels/telegram#reaction-notifications) — `channels.telegram.reactionLevel`
- [WhatsApp reactionLevel](/fr/channels/whatsapp#reaction-level) — `channels.whatsapp.reactionLevel`

Définissez `reactionLevel` sur des canaux individuels afin d’ajuster à quel point l’agent réagit activement aux messages sur chaque plateforme.

## Voir aussi

- [Agent Send](/fr/tools/agent-send) — l’outil `message` qui inclut `react`
- [Channels](/fr/channels) — configuration spécifique au canal
