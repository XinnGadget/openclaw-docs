---
read_when:
    - Trabajar con reacciones en cualquier canal
    - Comprender cómo difieren las reacciones con emoji entre plataformas
summary: Semántica de la herramienta de reacciones en todos los canales compatibles
title: Reacciones
x-i18n:
    generated_at: "2026-04-11T02:47:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: cfac31b7f0effc89cc696e3cf34cd89503ccdbb28996723945025e4b6e159986
    source_path: tools/reactions.md
    workflow: 15
---

# Reacciones

El agente puede agregar y quitar reacciones con emoji en los mensajes usando la herramienta `message` con la acción `react`. El comportamiento de las reacciones varía según el canal.

## Cómo funciona

```json
{
  "action": "react",
  "messageId": "msg-123",
  "emoji": "thumbsup"
}
```

- `emoji` es obligatorio al agregar una reacción.
- Establece `emoji` como una cadena vacía (`""`) para quitar la(s) reacción(es) del bot.
- Establece `remove: true` para quitar un emoji específico (requiere `emoji` no vacío).

## Comportamiento por canal

<AccordionGroup>
  <Accordion title="Discord and Slack">
    - Un `emoji` vacío quita todas las reacciones del bot en el mensaje.
    - `remove: true` quita solo el emoji especificado.
  </Accordion>

  <Accordion title="Google Chat">
    - Un `emoji` vacío quita las reacciones de la app en el mensaje.
    - `remove: true` quita solo el emoji especificado.
  </Accordion>

  <Accordion title="Telegram">
    - Un `emoji` vacío quita las reacciones del bot.
    - `remove: true` también quita reacciones, pero sigue requiriendo un `emoji` no vacío para la validación de la herramienta.
  </Accordion>

  <Accordion title="WhatsApp">
    - Un `emoji` vacío quita la reacción del bot.
    - `remove: true` se asigna internamente a emoji vacío (sigue requiriendo `emoji` en la llamada de la herramienta).
  </Accordion>

  <Accordion title="Zalo Personal (zalouser)">
    - Requiere `emoji` no vacío.
    - `remove: true` quita esa reacción de emoji específica.
  </Accordion>

  <Accordion title="Feishu/Lark">
    - Usa la herramienta `feishu_reaction` con las acciones `add`, `remove` y `list`.
    - Agregar/quitar requiere `emoji_type`; quitar también requiere `reaction_id`.
  </Accordion>

  <Accordion title="Signal">
    - Las notificaciones de reacciones entrantes se controlan con `channels.signal.reactionNotifications`: `"off"` las desactiva, `"own"` (predeterminado) emite eventos cuando los usuarios reaccionan a los mensajes del bot, y `"all"` emite eventos para todas las reacciones.
  </Accordion>
</AccordionGroup>

## Nivel de reacción

La configuración `reactionLevel` por canal controla qué tan ampliamente usa reacciones el agente. Los valores suelen ser `off`, `ack`, `minimal` o `extensive`.

- [reactionLevel de Telegram](/es/channels/telegram#reaction-notifications) — `channels.telegram.reactionLevel`
- [reactionLevel de WhatsApp](/es/channels/whatsapp#reaction-level) — `channels.whatsapp.reactionLevel`

Configura `reactionLevel` en canales individuales para ajustar qué tan activamente reacciona el agente a los mensajes en cada plataforma.

## Relacionado

- [Envío del agente](/es/tools/agent-send) — la herramienta `message` que incluye `react`
- [Canales](/es/channels) — configuración específica del canal
