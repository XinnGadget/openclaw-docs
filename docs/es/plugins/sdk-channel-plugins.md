---
read_when:
    - Estás creando un nuevo plugin de canal de mensajería
    - Quieres conectar OpenClaw a una plataforma de mensajería
    - Necesitas comprender la superficie del adaptador ChannelPlugin
sidebarTitle: Channel Plugins
summary: Guía paso a paso para crear un plugin de canal de mensajería para OpenClaw
title: Creación de plugins de canal
x-i18n:
    generated_at: "2026-04-07T05:04:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: 25ac0591d9b0ba401925b29ae4b9572f18b2cbffc2b6ca6ed5252740e7cf97e9
    source_path: plugins/sdk-channel-plugins.md
    workflow: 15
---

# Creación de plugins de canal

Esta guía explica cómo crear un plugin de canal que conecta OpenClaw con una
plataforma de mensajería. Al final tendrás un canal funcional con seguridad de
mensajes directos, emparejamiento, hilos de respuesta y mensajería saliente.

<Info>
  Si todavía no has creado ningún plugin de OpenClaw, lee primero
  [Primeros pasos](/es/plugins/building-plugins) para conocer la estructura básica
  del paquete y la configuración del manifiesto.
</Info>

## Cómo funcionan los plugins de canal

Los plugins de canal no necesitan sus propias herramientas de enviar/editar/reaccionar. OpenClaw mantiene una
herramienta `message` compartida en el núcleo. Tu plugin es responsable de:

- **Configuración** — resolución de cuentas y asistente de configuración
- **Seguridad** — política de mensajes directos y allowlists
- **Emparejamiento** — flujo de aprobación para mensajes directos
- **Gramática de sesión** — cómo los IDs de conversación específicos del proveedor se asignan a chats base, IDs de hilo y respaldos del elemento padre
- **Saliente** — envío de texto, medios y encuestas a la plataforma
- **Hilos** — cómo se organizan las respuestas en hilos

El núcleo se encarga de la herramienta de mensajes compartida, la conexión del prompt, la forma externa de la clave de sesión,
la contabilidad genérica de `:thread:` y el despacho.

Si tu plataforma almacena alcance adicional dentro de los IDs de conversación, mantén ese análisis
en el plugin con `messaging.resolveSessionConversation(...)`. Ese es el hook
canónico para asignar `rawId` al ID de conversación base, un ID de hilo
opcional, un `baseConversationId` explícito y cualquier `parentConversationCandidates`.
Cuando devuelvas `parentConversationCandidates`, mantenlos ordenados desde el
elemento padre más específico hasta la conversación base/más amplia.

Los plugins incluidos que necesiten el mismo análisis antes de que se inicie el registro del canal
también pueden exponer un archivo `session-key-api.ts` de nivel superior con una
exportación `resolveSessionConversation(...)` coincidente. El núcleo usa esa superficie segura
para bootstrap solo cuando el registro de plugins en tiempo de ejecución aún no está disponible.

`messaging.resolveParentConversationCandidates(...)` sigue disponible como una
ruta de compatibilidad heredada cuando un plugin solo necesita
respaldos de conversación padre además del ID genérico/raw. Si existen ambos hooks, el núcleo usa primero
`resolveSessionConversation(...).parentConversationCandidates` y solo
recurre a `resolveParentConversationCandidates(...)` cuando el hook canónico
los omite.

## Aprobaciones y capacidades del canal

La mayoría de los plugins de canal no necesitan código específico de aprobaciones.

- El núcleo gestiona `/approve` en el mismo chat, cargas útiles compartidas de botones de aprobación y la entrega genérica de respaldo.
- Prefiere un único objeto `approvalCapability` en el plugin de canal cuando el canal necesite comportamiento específico de aprobación.
- `approvalCapability.authorizeActorAction` y `approvalCapability.getActionAvailabilityState` son la unión canónica de autenticación para aprobaciones.
- Si tu canal expone aprobaciones nativas de exec, implementa `approvalCapability.getActionAvailabilityState` incluso cuando el transporte nativo viva por completo bajo `approvalCapability.native`. El núcleo usa ese hook de disponibilidad para distinguir `enabled` frente a `disabled`, decidir si el canal iniciador admite aprobaciones nativas e incluir el canal en la orientación de respaldo del cliente nativo.
- Usa `outbound.shouldSuppressLocalPayloadPrompt` o `outbound.beforeDeliverPayload` para comportamiento específico del canal en el ciclo de vida de la carga útil, como ocultar solicitudes locales de aprobación duplicadas o enviar indicadores de escritura antes de la entrega.
- Usa `approvalCapability.delivery` solo para enrutamiento nativo de aprobaciones o supresión de respaldo.
- Usa `approvalCapability.render` solo cuando un canal realmente necesite cargas útiles de aprobación personalizadas en lugar del renderizador compartido.
- Usa `approvalCapability.describeExecApprovalSetup` cuando el canal quiera que la respuesta de ruta deshabilitada explique los ajustes exactos de configuración necesarios para habilitar las aprobaciones nativas de exec. El hook recibe `{ channel, channelLabel, accountId }`; los canales con cuentas con nombre deben renderizar rutas con alcance por cuenta como `channels.<channel>.accounts.<id>.execApprovals.*` en lugar de valores predeterminados de nivel superior.
- Si un canal puede inferir identidades estables tipo propietario en mensajes directos a partir de la configuración existente, usa `createResolvedApproverActionAuthAdapter` desde `openclaw/plugin-sdk/approval-runtime` para restringir `/approve` en el mismo chat sin añadir lógica específica de aprobaciones en el núcleo.
- Si un canal necesita entrega nativa de aprobaciones, mantén el código del canal enfocado en la normalización de destino y los hooks de transporte. Usa `createChannelExecApprovalProfile`, `createChannelNativeOriginTargetResolver`, `createChannelApproverDmTargetResolver`, `createApproverRestrictedNativeApprovalCapability` y `createChannelNativeApprovalRuntime` desde `openclaw/plugin-sdk/approval-runtime` para que el núcleo gestione el filtrado de solicitudes, enrutamiento, deduplicación, caducidad y suscripción del gateway.
- Los canales de aprobación nativa deben enrutar tanto `accountId` como `approvalKind` a través de esos helpers. `accountId` mantiene la política de aprobación multicuenta limitada a la cuenta correcta del bot, y `approvalKind` mantiene disponible para el canal el comportamiento de aprobación de exec frente a plugin sin ramas codificadas en el núcleo.
- Conserva de extremo a extremo el tipo de ID de aprobación entregado. Los clientes nativos no deben
  deducir ni reescribir el enrutamiento de aprobación de exec frente a plugin a partir del estado local del canal.
- Diferentes tipos de aprobación pueden exponer intencionadamente superficies nativas distintas.
  Ejemplos actuales incluidos:
  - Slack mantiene disponible el enrutamiento nativo de aprobaciones tanto para IDs de exec como de plugin.
  - Matrix mantiene el enrutamiento nativo por DM/canal solo para aprobaciones de exec y deja
    las aprobaciones de plugins en la ruta compartida `/approve` del mismo chat.
- `createApproverRestrictedNativeApprovalAdapter` sigue existiendo como envoltorio de compatibilidad, pero el código nuevo debería preferir el constructor de capacidades y exponer `approvalCapability` en el plugin.

Para puntos de entrada calientes del canal, prefiere las subrutas de tiempo de ejecución más estrechas cuando solo
necesites una parte de esa familia:

- `openclaw/plugin-sdk/approval-auth-runtime`
- `openclaw/plugin-sdk/approval-client-runtime`
- `openclaw/plugin-sdk/approval-delivery-runtime`
- `openclaw/plugin-sdk/approval-native-runtime`
- `openclaw/plugin-sdk/approval-reply-runtime`

Del mismo modo, prefiere `openclaw/plugin-sdk/setup-runtime`,
`openclaw/plugin-sdk/setup-adapter-runtime`,
`openclaw/plugin-sdk/reply-runtime`,
`openclaw/plugin-sdk/reply-dispatch-runtime`,
`openclaw/plugin-sdk/reply-reference` y
`openclaw/plugin-sdk/reply-chunking` cuando no necesites la
superficie paraguas más amplia.

Específicamente para configuración:

- `openclaw/plugin-sdk/setup-runtime` cubre los helpers de configuración seguros en tiempo de ejecución:
  adaptadores de parcheo de configuración seguros para importación (`createPatchedAccountSetupAdapter`,
  `createEnvPatchedAccountSetupAdapter`,
  `createSetupInputPresenceValidator`), salida de notas de búsqueda,
  `promptResolvedAllowFrom`, `splitSetupEntries` y los constructores
  delegados del proxy de configuración
- `openclaw/plugin-sdk/setup-adapter-runtime` es la unión de adaptador estrecha con reconocimiento de entorno
  para `createEnvPatchedAccountSetupAdapter`
- `openclaw/plugin-sdk/channel-setup` cubre los constructores de configuración
  de instalación opcional más algunas primitivas seguras para configuración:
  `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`,

Si tu canal admite configuración o autenticación basada en variables de entorno y los flujos
genéricos de inicio/configuración deben conocer esos nombres de entorno antes de que se cargue el tiempo de ejecución,
decláralos en el manifiesto del plugin con `channelEnvVars`. Mantén `envVars` del tiempo de ejecución del canal o las constantes locales solo para el texto orientado al operador.
`createOptionalChannelSetupWizard`, `DEFAULT_ACCOUNT_ID`,
`createTopLevelChannelDmPolicy`, `setSetupChannelEnabled` y
`splitSetupEntries`

- usa la unión más amplia `openclaw/plugin-sdk/setup` solo cuando también necesites los
  helpers compartidos más pesados de configuración/configuración como
  `moveSingleAccountChannelSectionToDefaultAccount(...)`

Si tu canal solo quiere anunciar "instala este plugin primero" en superficies de configuración, prefiere `createOptionalChannelSetupSurface(...)`. El
adaptador/asistente generado falla de forma cerrada en escrituras de configuración y finalización, y reutiliza
el mismo mensaje de instalación requerida en validación, finalización y texto
de enlace a documentación.

Para otras rutas calientes del canal, prefiere los helpers estrechos frente a las superficies heredadas más amplias:

- `openclaw/plugin-sdk/account-core`,
  `openclaw/plugin-sdk/account-id`,
  `openclaw/plugin-sdk/account-resolution` y
  `openclaw/plugin-sdk/account-helpers` para configuración multicuenta y
  respaldo de cuenta predeterminada
- `openclaw/plugin-sdk/inbound-envelope` y
  `openclaw/plugin-sdk/inbound-reply-dispatch` para la conexión del sobre/ruta entrante y
  el registro y despacho
- `openclaw/plugin-sdk/messaging-targets` para análisis/coincidencia de destinos
- `openclaw/plugin-sdk/outbound-media` y
  `openclaw/plugin-sdk/outbound-runtime` para carga de medios más delegados
  de identidad/envío saliente
- `openclaw/plugin-sdk/thread-bindings-runtime` para el ciclo de vida de vinculaciones de hilos
  y el registro de adaptadores
- `openclaw/plugin-sdk/agent-media-payload` solo cuando siga siendo necesario un diseño heredado
  de campos de carga útil de agente/medios
- `openclaw/plugin-sdk/telegram-command-config` para normalización de comandos
  personalizados de Telegram, validación de duplicados/conflictos y un contrato
  de configuración de comandos estable para respaldo

Los canales solo de autenticación normalmente pueden quedarse en la ruta predeterminada: el núcleo gestiona las aprobaciones y el plugin solo expone capacidades de salida/autenticación. Los canales con aprobaciones nativas, como Matrix, Slack, Telegram y transportes de chat personalizados, deben usar los helpers nativos compartidos en lugar de crear su propio ciclo de vida de aprobación.

## Recorrido

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="Paquete y manifiesto">
    Crea los archivos estándar del plugin. El campo `channel` en `package.json` es
    lo que convierte esto en un plugin de canal. Para la superficie completa de metadatos del paquete,
    consulta [Configuración y config del plugin](/es/plugins/sdk-setup#openclawchannel):

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
          "blurb": "Conecta OpenClaw con Acme Chat."
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
      "description": "Plugin de canal Acme Chat",
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

  <Step title="Crea el objeto plugin de canal">
    La interfaz `ChannelPlugin` tiene muchas superficies de adaptador opcionales. Empieza con
    lo mínimo — `id` y `setup` — y añade adaptadores según los necesites.

    Crea `src/channel.ts`:

    ```typescript src/channel.ts
    import {
      createChatChannelPlugin,
      createChannelPluginBase,
    } from "openclaw/plugin-sdk/channel-core";
    import type { OpenClawConfig } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatApi } from "./client.js"; // your platform API client

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

      // DM security: who can message the bot
      security: {
        dm: {
          channelKey: "acme-chat",
          resolvePolicy: (account) => account.dmPolicy,
          resolveAllowFrom: (account) => account.allowFrom,
          defaultPolicy: "allowlist",
        },
      },

      // Pairing: approval flow for new DM contacts
      pairing: {
        text: {
          idLabel: "Acme Chat username",
          message: "Send this code to verify your identity:",
          notify: async ({ target, code }) => {
            await acmeChatApi.sendDm(target, `Pairing code: ${code}`);
          },
        },
      },

      // Threading: how replies are delivered
      threading: { topLevelReplyToMode: "reply" },

      // Outbound: send messages to the platform
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
      opciones declarativas y el constructor las compone:

      | Opción | Qué conecta |
      | --- | --- |
      | `security.dm` | Resolutor de seguridad de DM con alcance desde campos de configuración |
      | `pairing.text` | Flujo de emparejamiento de DM basado en texto con intercambio de código |
      | `threading` | Resolutor del modo reply-to (fijo, con alcance por cuenta o personalizado) |
      | `outbound.attachedResults` | Funciones de envío que devuelven metadatos del resultado (IDs de mensaje) |

      También puedes pasar objetos de adaptador sin procesar en lugar de opciones declarativas
      si necesitas control total.
    </Accordion>

  </Step>

  <Step title="Conecta el punto de entrada">
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

    Coloca los descriptores de CLI del canal en `registerCliMetadata(...)` para que OpenClaw
    pueda mostrarlos en la ayuda raíz sin activar el tiempo de ejecución completo del canal,
    mientras que las cargas completas normales siguen recogiendo los mismos descriptores para el registro real de comandos.
    Mantén `registerFull(...)` para trabajo exclusivo de tiempo de ejecución.
    Si `registerFull(...)` registra métodos RPC del gateway, usa un prefijo
    específico del plugin. Los espacios de nombres de administración del núcleo (`config.*`,
    `exec.approvals.*`, `wizard.*`, `update.*`) permanecen reservados y siempre
    se resuelven como `operator.admin`.
    `defineChannelPluginEntry` gestiona automáticamente la división de modos de registro. Consulta
    [Puntos de entrada](/es/plugins/sdk-entrypoints#definechannelpluginentry) para ver todas las
    opciones.

  </Step>

  <Step title="Añade una entrada de configuración">
    Crea `setup-entry.ts` para una carga ligera durante la incorporación:

    ```typescript setup-entry.ts
    import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineSetupPluginEntry(acmeChatPlugin);
    ```

    OpenClaw carga esto en lugar de la entrada completa cuando el canal está deshabilitado
    o sin configurar. Evita cargar código pesado de tiempo de ejecución durante los flujos de configuración.
    Consulta [Configuración y config](/es/plugins/sdk-setup#setup-entry) para más detalles.

  </Step>

  <Step title="Gestiona los mensajes entrantes">
    Tu plugin necesita recibir mensajes desde la plataforma y reenviarlos a
    OpenClaw. El patrón típico es un webhook que verifica la solicitud y la
    despacha a través del controlador de entrada de tu canal:

    ```typescript
    registerFull(api) {
      api.registerHttpRoute({
        path: "/acme-chat/webhook",
        auth: "plugin", // plugin-managed auth (verify signatures yourself)
        handler: async (req, res) => {
          const event = parseWebhookPayload(req);

          // Your inbound handler dispatches the message to OpenClaw.
          // The exact wiring depends on your platform SDK —
          // see a real example in the bundled Microsoft Teams or Google Chat plugin package.
          await handleAcmeChatInbound(api, event);

          res.statusCode = 200;
          res.end("ok");
          return true;
        },
      });
    }
    ```

    <Note>
      La gestión de mensajes entrantes es específica de cada canal. Cada plugin de canal es responsable
      de su propia canalización de entrada. Mira los plugins de canal incluidos
      (por ejemplo, el paquete del plugin de Microsoft Teams o Google Chat) para ver patrones reales.
    </Note>

  </Step>

<a id="step-6-test"></a>
<Step title="Prueba">
Escribe pruebas colocadas junto al código en `src/channel.test.ts`:

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

    Para helpers de prueba compartidos, consulta [Pruebas](/es/plugins/sdk-testing).

  </Step>
</Steps>

## Estructura de archivos

```
<bundled-plugin-root>/acme-chat/
├── package.json              # metadatos openclaw.channel
├── openclaw.plugin.json      # manifiesto con esquema de configuración
├── index.ts                  # defineChannelPluginEntry
├── setup-entry.ts            # defineSetupPluginEntry
├── api.ts                    # exportaciones públicas (opcional)
├── runtime-api.ts            # exportaciones internas de tiempo de ejecución (opcional)
└── src/
    ├── channel.ts            # ChannelPlugin mediante createChatChannelPlugin
    ├── channel.test.ts       # Pruebas
    ├── client.ts             # Cliente de la API de la plataforma
    └── runtime.ts            # Almacén de tiempo de ejecución (si es necesario)
```

## Temas avanzados

<CardGroup cols={2}>
  <Card title="Opciones de hilos" icon="git-branch" href="/es/plugins/sdk-entrypoints#registration-mode">
    Modos de respuesta fijos, con alcance por cuenta o personalizados
  </Card>
  <Card title="Integración de la herramienta de mensajes" icon="puzzle" href="/es/plugins/architecture#channel-plugins-and-the-shared-message-tool">
    describeMessageTool y descubrimiento de acciones
  </Card>
  <Card title="Resolución de destino" icon="crosshair" href="/es/plugins/architecture#channel-target-resolution">
    inferTargetChatType, looksLikeId, resolveTarget
  </Card>
  <Card title="Helpers de tiempo de ejecución" icon="settings" href="/es/plugins/sdk-runtime">
    TTS, STT, medios, subagente mediante api.runtime
  </Card>
</CardGroup>

<Note>
Algunas uniones de helpers incluidos siguen existiendo para mantenimiento y
compatibilidad de plugins incluidos. No son el patrón recomendado para nuevos plugins de canal;
prefiere las subrutas genéricas comunes del SDK para canal/configuración/respuesta/tiempo de ejecución
a menos que estés manteniendo directamente esa familia de plugins incluidos.
</Note>

## Próximos pasos

- [Plugins de proveedor](/es/plugins/sdk-provider-plugins) — si tu plugin también proporciona modelos
- [Resumen del SDK](/es/plugins/sdk-overview) — referencia completa de importaciones por subruta
- [Pruebas del SDK](/es/plugins/sdk-testing) — utilidades de prueba y pruebas de contrato
- [Manifiesto del plugin](/es/plugins/manifest) — esquema completo del manifiesto
