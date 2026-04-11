---
read_when:
    - Estás creando un nuevo plugin de canal de mensajería
    - Quieres conectar OpenClaw a una plataforma de mensajería
    - Necesitas entender la superficie del adaptador ChannelPlugin
sidebarTitle: Channel Plugins
summary: Guía paso a paso para crear un plugin de canal de mensajería para OpenClaw
title: Crear plugins de canal
x-i18n:
    generated_at: "2026-04-11T02:46:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8a026e924f9ae8a3ddd46287674443bcfccb0247be504261522b078e1f440aef
    source_path: plugins/sdk-channel-plugins.md
    workflow: 15
---

# Crear plugins de canal

Esta guía recorre la creación de un plugin de canal que conecta OpenClaw con una
plataforma de mensajería. Al final tendrás un canal funcional con seguridad en DM,
pairing, threading de respuestas y mensajería saliente.

<Info>
  Si aún no has creado ningún plugin de OpenClaw, lee primero
  [Getting Started](/es/plugins/building-plugins) para conocer la estructura básica
  del paquete y la configuración del manifiesto.
</Info>

## Cómo funcionan los plugins de canal

Los plugins de canal no necesitan sus propias herramientas de enviar/editar/reaccionar. OpenClaw mantiene una
única herramienta `message` compartida en el core. Tu plugin se encarga de:

- **Configuración** — resolución de cuentas y asistente de configuración
- **Seguridad** — política de DM y allowlists
- **Pairing** — flujo de aprobación de DM
- **Gramática de sesión** — cómo los ids de conversación específicos del proveedor se mapean a chats base, ids de hilo y respaldos del padre
- **Salida** — envío de texto, medios y encuestas a la plataforma
- **Threading** — cómo se encadenan las respuestas

El core se encarga de la herramienta de mensaje compartida, la conexión de prompts, la forma externa de la clave de sesión,
la contabilidad genérica de `:thread:` y el despacho.

Si tu plataforma almacena scope adicional dentro de los ids de conversación, mantén ese análisis
en el plugin con `messaging.resolveSessionConversation(...)`. Ese es el hook canónico para mapear
`rawId` al id base de la conversación, id opcional del hilo, `baseConversationId` explícito y cualquier
`parentConversationCandidates`.
Cuando devuelvas `parentConversationCandidates`, mantenlos ordenados del padre más específico al
más amplio/base.

Los plugins incluidos que necesiten el mismo análisis antes de que se inicie el registro del canal
también pueden exponer un archivo `session-key-api.ts` de nivel superior con una exportación
`resolveSessionConversation(...)` equivalente. El core usa esa superficie segura para bootstrap
solo cuando el registro de plugins en runtime aún no está disponible.

`messaging.resolveParentConversationCandidates(...)` sigue disponible como respaldo heredado de compatibilidad cuando un plugin solo necesita
respaldos de padre además del id genérico/raw. Si existen ambos hooks, el core usa primero
`resolveSessionConversation(...).parentConversationCandidates` y solo recurre a
`resolveParentConversationCandidates(...)` cuando el hook canónico los omite.

## Aprobaciones y capacidades del canal

La mayoría de los plugins de canal no necesitan código específico de aprobaciones.

- El core se encarga de `/approve` en el mismo chat, las cargas compartidas de botones de aprobación y la entrega genérica de respaldo.
- Prefiere un solo objeto `approvalCapability` en el plugin del canal cuando el canal necesita comportamiento específico de aprobaciones.
- `ChannelPlugin.approvals` se eliminó. Coloca los datos de entrega/aprobación nativa/renderizado/auth en `approvalCapability`.
- `plugin.auth` es solo para login/logout; el core ya no lee hooks de auth de aprobación desde ese objeto.
- `approvalCapability.authorizeActorAction` y `approvalCapability.getActionAvailabilityState` son la separación canónica para auth de aprobaciones.
- Usa `approvalCapability.getActionAvailabilityState` para la disponibilidad de auth de aprobación en el mismo chat.
- Si tu canal expone aprobaciones exec nativas, usa `approvalCapability.getExecInitiatingSurfaceState` para el estado de superficie iniciadora/cliente nativo cuando difiere de la auth de aprobación en el mismo chat. El core usa ese hook específico de exec para distinguir `enabled` frente a `disabled`, decidir si el canal iniciador admite aprobaciones exec nativas e incluir el canal en la guía de respaldo del cliente nativo. `createApproverRestrictedNativeApprovalCapability(...)` completa esto para el caso común.
- Usa `outbound.shouldSuppressLocalPayloadPrompt` o `outbound.beforeDeliverPayload` para el comportamiento del ciclo de vida de cargas específico del canal, como ocultar prompts locales de aprobación duplicados o enviar indicadores de escritura antes de la entrega.
- Usa `approvalCapability.delivery` solo para enrutamiento de aprobación nativa o supresión de respaldo.
- Usa `approvalCapability.nativeRuntime` para datos de aprobación nativa propios del canal. Manténlo lazy en entrypoints calientes del canal con `createLazyChannelApprovalNativeRuntimeAdapter(...)`, que puede importar tu módulo runtime bajo demanda mientras permite que el core ensamble el ciclo de vida de aprobación.
- Usa `approvalCapability.render` solo cuando un canal realmente necesite cargas de aprobación personalizadas en lugar del renderizador compartido.
- Usa `approvalCapability.describeExecApprovalSetup` cuando el canal quiera que la respuesta de ruta deshabilitada explique las claves exactas de configuración necesarias para habilitar aprobaciones exec nativas. El hook recibe `{ channel, channelLabel, accountId }`; los canales con cuentas nombradas deben renderizar rutas con scope por cuenta como `channels.<channel>.accounts.<id>.execApprovals.*` en lugar de valores predeterminados de nivel superior.
- Si un canal puede inferir identidades DM estables de tipo propietario a partir de la configuración existente, usa `createResolvedApproverActionAuthAdapter` de `openclaw/plugin-sdk/approval-runtime` para restringir `/approve` en el mismo chat sin agregar lógica del core específica de aprobaciones.
- Si un canal necesita entrega de aprobación nativa, mantén el código del canal enfocado en la normalización de destino más los datos de transporte/presentación. Usa `createChannelExecApprovalProfile`, `createChannelNativeOriginTargetResolver`, `createChannelApproverDmTargetResolver` y `createApproverRestrictedNativeApprovalCapability` de `openclaw/plugin-sdk/approval-runtime`. Coloca los datos específicos del canal detrás de `approvalCapability.nativeRuntime`, idealmente mediante `createChannelApprovalNativeRuntimeAdapter(...)` o `createLazyChannelApprovalNativeRuntimeAdapter(...)`, para que el core pueda ensamblar el handler y encargarse del filtrado de solicitudes, enrutamiento, deduplicación, expiración, suscripción al gateway y avisos de redirección. `nativeRuntime` se divide en unas pocas separaciones más pequeñas:
- `availability` — si la cuenta está configurada y si una solicitud debe manejarse
- `presentation` — mapear el modelo de vista de aprobación compartido en cargas nativas pendientes/resueltas/expiradas o acciones finales
- `transport` — preparar destinos más enviar/actualizar/eliminar mensajes de aprobación nativa
- `interactions` — hooks opcionales para bind/unbind/clear-action para botones o reacciones nativas
- `observe` — hooks opcionales de diagnóstico de entrega
- Si el canal necesita objetos propios del runtime como un cliente, token, app Bolt o receptor webhook, regístralos a través de `openclaw/plugin-sdk/channel-runtime-context`. El registro genérico de runtime-context permite al core iniciar handlers controlados por capacidades a partir del estado de inicio del canal sin agregar glue wrapper específico de aprobaciones.
- Recurre a `createChannelApprovalHandler` o `createChannelNativeApprovalRuntime` de nivel más bajo solo cuando la separación basada en capacidades aún no sea lo bastante expresiva.
- Los canales de aprobación nativa deben enrutar tanto `accountId` como `approvalKind` a través de esos helpers. `accountId` mantiene la política de aprobación multicuenta con scope para la cuenta de bot correcta, y `approvalKind` mantiene disponible para el canal el comportamiento de aprobación exec frente a plugin sin ramas hardcoded en el core.
- El core ahora también se encarga de los avisos de redirección de aprobación. Los plugins de canal no deben enviar sus propios mensajes de seguimiento tipo "la aprobación fue a los DM / a otro canal" desde `createChannelNativeApprovalRuntime`; en su lugar, expón un enrutamiento preciso de origen + DM del aprobador mediante los helpers compartidos de capacidades de aprobación y deja que el core agregue las entregas reales antes de publicar cualquier aviso de vuelta en el chat iniciador.
- Conserva de extremo a extremo el tipo de id de aprobación entregado. Los clientes nativos no deben
  adivinar ni reescribir el enrutamiento de aprobación exec frente a plugin desde el estado local del canal.
- Distintos tipos de aprobación pueden exponer intencionalmente superficies nativas diferentes.
  Ejemplos incluidos actualmente:
  - Slack mantiene disponible el enrutamiento de aprobación nativa tanto para ids exec como para ids de plugin.
  - Matrix mantiene el mismo enrutamiento nativo DM/canal y UX de reacciones para aprobaciones exec
    y de plugin, aunque sigue permitiendo que la auth difiera por tipo de aprobación.
- `createApproverRestrictedNativeApprovalAdapter` sigue existiendo como wrapper de compatibilidad, pero el código nuevo debe preferir el constructor de capacidades y exponer `approvalCapability` en el plugin.

Para entrypoints calientes del canal, prefiere los subpaths runtime más estrechos cuando solo
necesites una parte de esa familia:

- `openclaw/plugin-sdk/approval-auth-runtime`
- `openclaw/plugin-sdk/approval-client-runtime`
- `openclaw/plugin-sdk/approval-delivery-runtime`
- `openclaw/plugin-sdk/approval-gateway-runtime`
- `openclaw/plugin-sdk/approval-handler-adapter-runtime`
- `openclaw/plugin-sdk/approval-handler-runtime`
- `openclaw/plugin-sdk/approval-native-runtime`
- `openclaw/plugin-sdk/approval-reply-runtime`
- `openclaw/plugin-sdk/channel-runtime-context`

Del mismo modo, prefiere `openclaw/plugin-sdk/setup-runtime`,
`openclaw/plugin-sdk/setup-adapter-runtime`,
`openclaw/plugin-sdk/reply-runtime`,
`openclaw/plugin-sdk/reply-dispatch-runtime`,
`openclaw/plugin-sdk/reply-reference` y
`openclaw/plugin-sdk/reply-chunking` cuando no necesites la
superficie general más amplia.

Para setup en particular:

- `openclaw/plugin-sdk/setup-runtime` cubre los helpers de setup seguros para runtime:
  adaptadores de parcheo de setup seguros para importación (`createPatchedAccountSetupAdapter`,
  `createEnvPatchedAccountSetupAdapter`,
  `createSetupInputPresenceValidator`), salida de notas de lookup,
  `promptResolvedAllowFrom`, `splitSetupEntries` y los builders de
  setup-proxy delegados
- `openclaw/plugin-sdk/setup-adapter-runtime` es la separación estrecha del adaptador con reconocimiento de env
  para `createEnvPatchedAccountSetupAdapter`
- `openclaw/plugin-sdk/channel-setup` cubre los builders de setup con instalación opcional
  más algunas primitivas seguras para setup:
  `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`,

Si tu canal admite setup o auth impulsados por env y los flujos genéricos de inicio/configuración
deben conocer esos nombres de env antes de que cargue el runtime, decláralos en el
manifiesto del plugin con `channelEnvVars`. Mantén `envVars` del runtime del canal o constantes locales
solo para texto orientado al operator.
`createOptionalChannelSetupWizard`, `DEFAULT_ACCOUNT_ID`,
`createTopLevelChannelDmPolicy`, `setSetupChannelEnabled` y
`splitSetupEntries`

- usa la separación más amplia `openclaw/plugin-sdk/setup` solo cuando también necesites los
  helpers compartidos más pesados de setup/configuración como
  `moveSingleAccountChannelSectionToDefaultAccount(...)`

Si tu canal solo quiere anunciar "instala primero este plugin" en las superficies
de setup, prefiere `createOptionalChannelSetupSurface(...)`. El
adaptador/asistente generado falla en cerrado en escrituras de configuración y finalización, y reutiliza
el mismo mensaje de instalación requerida en validación, finalización y texto de enlace a docs.

Para otras rutas calientes del canal, prefiere los helpers estrechos sobre las
superficies heredadas más amplias:

- `openclaw/plugin-sdk/account-core`,
  `openclaw/plugin-sdk/account-id`,
  `openclaw/plugin-sdk/account-resolution` y
  `openclaw/plugin-sdk/account-helpers` para configuración multicuenta y
  respaldo de cuenta predeterminada
- `openclaw/plugin-sdk/inbound-envelope` y
  `openclaw/plugin-sdk/inbound-reply-dispatch` para la conexión de ruta/sobre entrante y
  de registro y despacho
- `openclaw/plugin-sdk/messaging-targets` para análisis/coincidencia de destinos
- `openclaw/plugin-sdk/outbound-media` y
  `openclaw/plugin-sdk/outbound-runtime` para carga de medios más delegados de
  identidad/envío saliente
- `openclaw/plugin-sdk/thread-bindings-runtime` para el ciclo de vida de thread-binding
  y el registro del adaptador
- `openclaw/plugin-sdk/agent-media-payload` solo cuando aún se requiera un diseño heredado
  de campos de carga de agente/medios
- `openclaw/plugin-sdk/telegram-command-config` para normalización de comandos personalizados de Telegram,
  validación de duplicados/conflictos y un contrato de configuración de comandos
  estable ante respaldos

Los canales solo de auth suelen poder quedarse en la ruta predeterminada: el core se encarga de las aprobaciones y el plugin solo expone capacidades salientes/de auth. Los canales con aprobación nativa como Matrix, Slack, Telegram y transportes de chat personalizados deben usar los helpers nativos compartidos en lugar de crear su propio ciclo de vida de aprobación.

## Política de mención entrante

Mantén el manejo de menciones entrantes dividido en dos capas:

- recopilación de evidencia propia del plugin
- evaluación compartida de políticas

Usa `openclaw/plugin-sdk/channel-inbound` para la capa compartida.

Buen caso para lógica local del plugin:

- detección de respuesta al bot
- detección de cita del bot
- comprobaciones de participación en el hilo
- exclusiones de mensajes de servicio/sistema
- cachés nativas de la plataforma necesarias para demostrar la participación del bot

Buen caso para el helper compartido:

- `requireMention`
- resultado explícito de mención
- allowlist de mención implícita
- omisión de comandos
- decisión final de omitir

Flujo preferido:

1. Calcula los datos locales de mención.
2. Pasa esos datos a `resolveInboundMentionDecision({ facts, policy })`.
3. Usa `decision.effectiveWasMentioned`, `decision.shouldBypassMention` y `decision.shouldSkip` en tu barrera de entrada.

```typescript
import {
  implicitMentionKindWhen,
  matchesMentionWithExplicit,
  resolveInboundMentionDecision,
} from "openclaw/plugin-sdk/channel-inbound";

const mentionMatch = matchesMentionWithExplicit(text, {
  mentionRegexes,
  mentionPatterns,
});

const facts = {
  canDetectMention: true,
  wasMentioned: mentionMatch.matched,
  hasAnyMention: mentionMatch.hasExplicitMention,
  implicitMentionKinds: [
    ...implicitMentionKindWhen("reply_to_bot", isReplyToBot),
    ...implicitMentionKindWhen("quoted_bot", isQuoteOfBot),
  ],
};

const decision = resolveInboundMentionDecision({
  facts,
  policy: {
    isGroup,
    requireMention,
    allowedImplicitMentionKinds: requireExplicitMention ? [] : ["reply_to_bot", "quoted_bot"],
    allowTextCommands,
    hasControlCommand,
    commandAuthorized,
  },
});

if (decision.shouldSkip) return;
```

`api.runtime.channel.mentions` expone los mismos helpers compartidos de mención para
plugins de canal incluidos que ya dependen de la inyección en runtime:

- `buildMentionRegexes`
- `matchesMentionPatterns`
- `matchesMentionWithExplicit`
- `implicitMentionKindWhen`
- `resolveInboundMentionDecision`

Los helpers antiguos `resolveMentionGating*` siguen en
`openclaw/plugin-sdk/channel-inbound` solo como exportaciones de compatibilidad. El código nuevo
debe usar `resolveInboundMentionDecision({ facts, policy })`.

## Recorrido

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="Paquete y manifiesto">
    Crea los archivos estándar del plugin. El campo `channel` en `package.json` es
    lo que hace que este sea un plugin de canal. Para ver toda la superficie de metadatos
    del paquete, consulta [Plugin Setup and Config](/es/plugins/sdk-setup#openclaw-channel):

    <CodeGroup>
    ```json package.json
    {
      "name": "@myorg/openclaw-acme-chat",
      "version": "1.0.0",
      "type": "module",
      "openclaw": {
        "extensions": ["./index.ts"],
        "setupEntry": "./setup-entry.ts",
        "channel": {
          "id": "acme-chat",
          "label": "Acme Chat",
          "blurb": "Connect OpenClaw to Acme Chat."
        }
      }
    }
    ```

    ```json openclaw.plugin.json
    {
      "id": "acme-chat",
      "kind": "channel",
      "channels": ["acme-chat"],
      "name": "Acme Chat",
      "description": "Acme Chat channel plugin",
      "configSchema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "acme-chat": {
            "type": "object",
            "properties": {
              "token": { "type": "string" },
              "allowFrom": {
                "type": "array",
                "items": { "type": "string" }
              }
            }
          }
        }
      }
    }
    ```
    </CodeGroup>

  </Step>

  <Step title="Crear el objeto del plugin de canal">
    La interfaz `ChannelPlugin` tiene muchas superficies de adaptador opcionales. Empieza con
    lo mínimo — `id` y `setup` — y agrega adaptadores según los necesites.

    Crea `src/channel.ts`:

    ```typescript src/channel.ts
    import {
      createChatChannelPlugin,
      createChannelPluginBase,
    } from "openclaw/plugin-sdk/channel-core";
    import type { OpenClawConfig } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatApi } from "./client.js"; // tu cliente API de la plataforma

    type ResolvedAccount = {
      accountId: string | null;
      token: string;
      allowFrom: string[];
      dmPolicy: string | undefined;
    };

    function resolveAccount(
      cfg: OpenClawConfig,
      accountId?: string | null,
    ): ResolvedAccount {
      const section = (cfg.channels as Record<string, any>)?.["acme-chat"];
      const token = section?.token;
      if (!token) throw new Error("acme-chat: token is required");
      return {
        accountId: accountId ?? null,
        token,
        allowFrom: section?.allowFrom ?? [],
        dmPolicy: section?.dmSecurity,
      };
    }

    export const acmeChatPlugin = createChatChannelPlugin<ResolvedAccount>({
      base: createChannelPluginBase({
        id: "acme-chat",
        setup: {
          resolveAccount,
          inspectAccount(cfg, accountId) {
            const section =
              (cfg.channels as Record<string, any>)?.["acme-chat"];
            return {
              enabled: Boolean(section?.token),
              configured: Boolean(section?.token),
              tokenStatus: section?.token ? "available" : "missing",
            };
          },
        },
      }),

      // Seguridad de DM: quién puede enviar mensajes al bot
      security: {
        dm: {
          channelKey: "acme-chat",
          resolvePolicy: (account) => account.dmPolicy,
          resolveAllowFrom: (account) => account.allowFrom,
          defaultPolicy: "allowlist",
        },
      },

      // Pairing: flujo de aprobación para nuevos contactos por DM
      pairing: {
        text: {
          idLabel: "Acme Chat username",
          message: "Send this code to verify your identity:",
          notify: async ({ target, code }) => {
            await acmeChatApi.sendDm(target, `Pairing code: ${code}`);
          },
        },
      },

      // Threading: cómo se entregan las respuestas
      threading: { topLevelReplyToMode: "reply" },

      // Salida: enviar mensajes a la plataforma
      outbound: {
        attachedResults: {
          sendText: async (params) => {
            const result = await acmeChatApi.sendMessage(
              params.to,
              params.text,
            );
            return { messageId: result.id };
          },
        },
        base: {
          sendMedia: async (params) => {
            await acmeChatApi.sendFile(params.to, params.filePath);
          },
        },
      },
    });
    ```

    <Accordion title="Qué hace por ti createChatChannelPlugin">
      En lugar de implementar manualmente interfaces de adaptador de bajo nivel, pasas
      opciones declarativas y el builder las compone:

      | Opción | Qué conecta |
      | --- | --- |
      | `security.dm` | Resolver de seguridad de DM con scope a partir de campos de configuración |
      | `pairing.text` | Flujo de pairing por DM basado en texto con intercambio de código |
      | `threading` | Resolver del modo reply-to (fijo, con scope por cuenta o personalizado) |
      | `outbound.attachedResults` | Funciones de envío que devuelven metadatos del resultado (IDs de mensaje) |

      También puedes pasar objetos de adaptador sin procesar en lugar de las opciones declarativas
      si necesitas control total.
    </Accordion>

  </Step>

  <Step title="Conectar el punto de entrada">
    Crea `index.ts`:

    ```typescript index.ts
    import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineChannelPluginEntry({
      id: "acme-chat",
      name: "Acme Chat",
      description: "Acme Chat channel plugin",
      plugin: acmeChatPlugin,
      registerCliMetadata(api) {
        api.registerCli(
          ({ program }) => {
            program
              .command("acme-chat")
              .description("Acme Chat management");
          },
          {
            descriptors: [
              {
                name: "acme-chat",
                description: "Acme Chat management",
                hasSubcommands: false,
              },
            ],
          },
        );
      },
      registerFull(api) {
        api.registerGatewayMethod(/* ... */);
      },
    });
    ```

    Coloca los descriptores CLI propios del canal en `registerCliMetadata(...)` para que OpenClaw
    pueda mostrarlos en la ayuda raíz sin activar el runtime completo del canal,
    mientras que las cargas completas normales siguen recogiendo esos mismos descriptores para el registro real
    de comandos. Mantén `registerFull(...)` para trabajo exclusivo de runtime.
    Si `registerFull(...)` registra métodos RPC del gateway, usa un
    prefijo específico del plugin. Los espacios de nombres admin del core (`config.*`,
    `exec.approvals.*`, `wizard.*`, `update.*`) permanecen reservados y siempre
    se resuelven a `operator.admin`.
    `defineChannelPluginEntry` maneja automáticamente la división del modo de registro. Consulta
    [Entry Points](/es/plugins/sdk-entrypoints#definechannelpluginentry) para ver todas las
    opciones.

  </Step>

  <Step title="Agregar una entrada de setup">
    Crea `setup-entry.ts` para una carga ligera durante el onboarding:

    ```typescript setup-entry.ts
    import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineSetupPluginEntry(acmeChatPlugin);
    ```

    OpenClaw carga esto en lugar de la entrada completa cuando el canal está deshabilitado
    o sin configurar. Evita cargar código pesado de runtime durante los flujos de setup.
    Consulta [Setup and Config](/es/plugins/sdk-setup#setup-entry) para más detalles.

  </Step>

  <Step title="Manejar mensajes entrantes">
    Tu plugin necesita recibir mensajes de la plataforma y reenviarlos a
    OpenClaw. El patrón típico es un webhook que verifica la solicitud y
    la despacha a través del handler entrante de tu canal:

    ```typescript
    registerFull(api) {
      api.registerHttpRoute({
        path: "/acme-chat/webhook",
        auth: "plugin", // auth administrada por el plugin (verifica tú mismo las firmas)
        handler: async (req, res) => {
          const event = parseWebhookPayload(req);

          // Tu handler entrante despacha el mensaje a OpenClaw.
          // La conexión exacta depende del SDK de tu plataforma —
          // consulta un ejemplo real en el paquete de plugin incluido de Microsoft Teams o Google Chat.
          await handleAcmeChatInbound(api, event);

          res.statusCode = 200;
          res.end("ok");
          return true;
        },
      });
    }
    ```

    <Note>
      El manejo de mensajes entrantes es específico del canal. Cada plugin de canal controla
      su propio pipeline de entrada. Revisa los plugins de canal incluidos
      (por ejemplo el paquete de plugin de Microsoft Teams o Google Chat) para ver patrones reales.
    </Note>

  </Step>

<a id="step-6-test"></a>
<Step title="Probar">
Escribe pruebas colocadas en `src/channel.test.ts`:

    ```typescript src/channel.test.ts
    import { describe, it, expect } from "vitest";
    import { acmeChatPlugin } from "./channel.js";

    describe("acme-chat plugin", () => {
      it("resolves account from config", () => {
        const cfg = {
          channels: {
            "acme-chat": { token: "test-token", allowFrom: ["user1"] },
          },
        } as any;
        const account = acmeChatPlugin.setup!.resolveAccount(cfg, undefined);
        expect(account.token).toBe("test-token");
      });

      it("inspects account without materializing secrets", () => {
        const cfg = {
          channels: { "acme-chat": { token: "test-token" } },
        } as any;
        const result = acmeChatPlugin.setup!.inspectAccount!(cfg, undefined);
        expect(result.configured).toBe(true);
        expect(result.tokenStatus).toBe("available");
      });

      it("reports missing config", () => {
        const cfg = { channels: {} } as any;
        const result = acmeChatPlugin.setup!.inspectAccount!(cfg, undefined);
        expect(result.configured).toBe(false);
      });
    });
    ```

    ```bash
    pnpm test -- <bundled-plugin-root>/acme-chat/
    ```

    Para helpers de prueba compartidos, consulta [Testing](/es/plugins/sdk-testing).

  </Step>
</Steps>

## Estructura de archivos

```text
<bundled-plugin-root>/acme-chat/
├── package.json              # metadatos openclaw.channel
├── openclaw.plugin.json      # Manifiesto con esquema de configuración
├── index.ts                  # defineChannelPluginEntry
├── setup-entry.ts            # defineSetupPluginEntry
├── api.ts                    # Exportaciones públicas (opcional)
├── runtime-api.ts            # Exportaciones internas de runtime (opcional)
└── src/
    ├── channel.ts            # ChannelPlugin mediante createChatChannelPlugin
    ├── channel.test.ts       # Pruebas
    ├── client.ts             # Cliente API de la plataforma
    └── runtime.ts            # Almacén de runtime (si es necesario)
```

## Temas avanzados

<CardGroup cols={2}>
  <Card title="Opciones de threading" icon="git-branch" href="/es/plugins/sdk-entrypoints#registration-mode">
    Modos de respuesta fijos, con scope por cuenta o personalizados
  </Card>
  <Card title="Integración con la herramienta de mensajes" icon="puzzle" href="/es/plugins/architecture#channel-plugins-and-the-shared-message-tool">
    describeMessageTool y descubrimiento de acciones
  </Card>
  <Card title="Resolución de destinos" icon="crosshair" href="/es/plugins/architecture#channel-target-resolution">
    inferTargetChatType, looksLikeId, resolveTarget
  </Card>
  <Card title="Helpers de runtime" icon="settings" href="/es/plugins/sdk-runtime">
    TTS, STT, medios, subagente mediante api.runtime
  </Card>
</CardGroup>

<Note>
Algunas separaciones de helpers incluidos todavía existen para mantenimiento de plugins incluidos y
compatibilidad. No son el patrón recomendado para nuevos plugins de canal;
prefiere los subpaths genéricos de canal/setup/reply/runtime de la superficie común del SDK
a menos que estés manteniendo directamente esa familia de plugins incluidos.
</Note>

## Siguientes pasos

- [Provider Plugins](/es/plugins/sdk-provider-plugins) — si tu plugin también proporciona modelos
- [SDK Overview](/es/plugins/sdk-overview) — referencia completa de importación de subpaths
- [SDK Testing](/es/plugins/sdk-testing) — utilidades de prueba y pruebas de contrato
- [Plugin Manifest](/es/plugins/manifest) — esquema completo del manifiesto
