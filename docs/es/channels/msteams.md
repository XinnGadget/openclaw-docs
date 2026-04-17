---
read_when:
    - Trabajando en las funciones del canal de Microsoft Teams
summary: Estado de soporte del bot de Microsoft Teams, capacidades y configuración
title: Microsoft Teams
x-i18n:
    generated_at: "2026-04-12T00:19:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3e6841a618fb030e4c2029b3652d45dedd516392e2ae17309ff46b93648ffb79
    source_path: channels/msteams.md
    workflow: 15
---

# Microsoft Teams

> "Abandonad toda esperanza, quienes entráis aquí."

Actualizado: 2026-03-25

Estado: se admiten texto + archivos adjuntos en mensajes directos; el envío de archivos en canales/grupos requiere `sharePointSiteId` + permisos de Graph (consulta [Envío de archivos en chats grupales](#sending-files-in-group-chats)). Las encuestas se envían mediante Adaptive Cards. Las acciones de mensaje exponen `upload-file` explícito para envíos centrados primero en archivos.

## Plugin incluido

Microsoft Teams se distribuye como un plugin incluido en las versiones actuales de OpenClaw, por lo que no se requiere una instalación independiente en la compilación empaquetada normal.

Si estás en una compilación anterior o en una instalación personalizada que excluye Teams incluido,
instálalo manualmente:

```bash
openclaw plugins install @openclaw/msteams
```

Checkout local (al ejecutarlo desde un repositorio git):

```bash
openclaw plugins install ./path/to/local/msteams-plugin
```

Detalles: [Plugins](/es/tools/plugin)

## Configuración rápida (principiante)

1. Asegúrate de que el plugin de Microsoft Teams esté disponible.
   - Las versiones empaquetadas actuales de OpenClaw ya lo incluyen.
   - Las instalaciones antiguas/personalizadas pueden añadirlo manualmente con los comandos anteriores.
2. Crea un **Azure Bot** (App ID + secreto de cliente + tenant ID).
3. Configura OpenClaw con esas credenciales.
4. Expón `/api/messages` (puerto 3978 de forma predeterminada) mediante una URL pública o un túnel.
5. Instala el paquete de la aplicación de Teams e inicia el gateway.

Configuración mínima (secreto de cliente):

```json5
{
  channels: {
    msteams: {
      enabled: true,
      appId: "<APP_ID>",
      appPassword: "<APP_PASSWORD>",
      tenantId: "<TENANT_ID>",
      webhook: { port: 3978, path: "/api/messages" },
    },
  },
}
```

Para implementaciones de producción, considera usar [autenticación federada](#federated-authentication-certificate--managed-identity) (certificado o identidad administrada) en lugar de secretos de cliente.

Nota: los chats grupales están bloqueados de forma predeterminada (`channels.msteams.groupPolicy: "allowlist"`). Para permitir respuestas en grupo, establece `channels.msteams.groupAllowFrom` (o usa `groupPolicy: "open"` para permitir cualquier miembro, con restricción por mención).

## Objetivos

- Hablar con OpenClaw mediante mensajes directos de Teams, chats grupales o canales.
- Mantener el enrutamiento determinista: las respuestas siempre vuelven al canal por el que llegaron.
- Usar un comportamiento de canal seguro de forma predeterminada (se requieren menciones salvo que se configure lo contrario).

## Escrituras de configuración

De forma predeterminada, Microsoft Teams puede escribir actualizaciones de configuración activadas por `/config set|unset` (requiere `commands.config: true`).

Desactívalo con:

```json5
{
  channels: { msteams: { configWrites: false } },
}
```

## Control de acceso (mensajes directos + grupos)

**Acceso a mensajes directos**

- Predeterminado: `channels.msteams.dmPolicy = "pairing"`. Los remitentes desconocidos se ignoran hasta que se aprueban.
- `channels.msteams.allowFrom` debe usar IDs de objeto AAD estables.
- Los UPN/nombres para mostrar son mutables; la coincidencia directa está desactivada de forma predeterminada y solo se habilita con `channels.msteams.dangerouslyAllowNameMatching: true`.
- El asistente puede resolver nombres a IDs mediante Microsoft Graph cuando las credenciales lo permiten.

**Acceso a grupos**

- Predeterminado: `channels.msteams.groupPolicy = "allowlist"` (bloqueado a menos que añadas `groupAllowFrom`). Usa `channels.defaults.groupPolicy` para sobrescribir el valor predeterminado cuando no esté establecido.
- `channels.msteams.groupAllowFrom` controla qué remitentes pueden activar en chats grupales/canales (recurre a `channels.msteams.allowFrom`).
- Establece `groupPolicy: "open"` para permitir cualquier miembro (aun así, con restricción por mención de forma predeterminada).
- Para no permitir **ningún canal**, establece `channels.msteams.groupPolicy: "disabled"`.

Ejemplo:

```json5
{
  channels: {
    msteams: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["user@org.com"],
    },
  },
}
```

**Lista de permitidos de Teams + canal**

- Limita las respuestas de grupo/canal listando equipos y canales en `channels.msteams.teams`.
- Las claves deben usar IDs estables de equipo e IDs de conversación de canal.
- Cuando `groupPolicy="allowlist"` y hay una lista de permitidos de equipos presente, solo se aceptan los equipos/canales listados (con restricción por mención).
- El asistente de configuración acepta entradas `Team/Channel` y las guarda por ti.
- Al iniciar, OpenClaw resuelve nombres de equipo/canal y nombres de usuario de la lista de permitidos a IDs (cuando los permisos de Graph lo permiten)
  y registra la asignación; los nombres de equipo/canal no resueltos se conservan tal como se escribieron, pero se ignoran para el enrutamiento de forma predeterminada a menos que `channels.msteams.dangerouslyAllowNameMatching: true` esté habilitado.

Ejemplo:

```json5
{
  channels: {
    msteams: {
      groupPolicy: "allowlist",
      teams: {
        "My Team": {
          channels: {
            General: { requireMention: true },
          },
        },
      },
    },
  },
}
```

## Cómo funciona

1. Asegúrate de que el plugin de Microsoft Teams esté disponible.
   - Las versiones empaquetadas actuales de OpenClaw ya lo incluyen.
   - Las instalaciones antiguas/personalizadas pueden añadirlo manualmente con los comandos anteriores.
2. Crea un **Azure Bot** (App ID + secreto + tenant ID).
3. Crea un **paquete de aplicación de Teams** que haga referencia al bot e incluya los permisos RSC de abajo.
4. Carga/instala la aplicación de Teams en un equipo (o en alcance personal para mensajes directos).
5. Configura `msteams` en `~/.openclaw/openclaw.json` (o variables de entorno) e inicia el gateway.
6. El gateway escucha el tráfico del webhook de Bot Framework en `/api/messages` de forma predeterminada.

## Configuración de Azure Bot (requisitos previos)

Antes de configurar OpenClaw, necesitas crear un recurso Azure Bot.

### Paso 1: Crear Azure Bot

1. Ve a [Create Azure Bot](https://portal.azure.com/#create/Microsoft.AzureBot)
2. Completa la pestaña **Basics**:

   | Campo              | Valor                                                    |
   | ------------------ | -------------------------------------------------------- |
   | **Bot handle**     | El nombre de tu bot, p. ej., `openclaw-msteams` (debe ser único) |
   | **Subscription**   | Selecciona tu suscripción de Azure                       |
   | **Resource group** | Crea uno nuevo o usa uno existente                       |
   | **Pricing tier**   | **Free** para desarrollo/pruebas                         |
   | **Type of App**    | **Single Tenant** (recomendado: consulta la nota abajo) |
   | **Creation type**  | **Create new Microsoft App ID**                          |

> **Aviso de retirada:** La creación de nuevos bots multi-tenant quedó obsoleta después del 2025-07-31. Usa **Single Tenant** para bots nuevos.

3. Haz clic en **Review + create** → **Create** (espera ~1-2 minutos)

### Paso 2: Obtener credenciales

1. Ve a tu recurso Azure Bot → **Configuration**
2. Copia **Microsoft App ID** → este es tu `appId`
3. Haz clic en **Manage Password** → ve al registro de la aplicación
4. En **Certificates & secrets** → **New client secret** → copia el **Value** → este es tu `appPassword`
5. Ve a **Overview** → copia **Directory (tenant) ID** → este es tu `tenantId`

### Paso 3: Configurar el endpoint de mensajería

1. En Azure Bot → **Configuration**
2. Establece **Messaging endpoint** en tu URL de webhook:
   - Producción: `https://your-domain.com/api/messages`
   - Desarrollo local: usa un túnel (consulta [Desarrollo local](#local-development-tunneling) abajo)

### Paso 4: Habilitar el canal de Teams

1. En Azure Bot → **Channels**
2. Haz clic en **Microsoft Teams** → Configure → Save
3. Acepta las Condiciones del servicio

## Autenticación federada (certificado + identidad administrada)

> Añadido en 2026.3.24

Para implementaciones de producción, OpenClaw admite **autenticación federada** como alternativa más segura a los secretos de cliente. Hay dos métodos disponibles:

### Opción A: autenticación basada en certificado

Usa un certificado PEM registrado con el registro de tu aplicación de Entra ID.

**Configuración:**

1. Genera u obtén un certificado (formato PEM con clave privada).
2. En Entra ID → App Registration → **Certificates & secrets** → **Certificates** → carga el certificado público.

**Config:**

```json5
{
  channels: {
    msteams: {
      enabled: true,
      appId: "<APP_ID>",
      tenantId: "<TENANT_ID>",
      authType: "federated",
      certificatePath: "/path/to/cert.pem",
      webhook: { port: 3978, path: "/api/messages" },
    },
  },
}
```

**Variables de entorno:**

- `MSTEAMS_AUTH_TYPE=federated`
- `MSTEAMS_CERTIFICATE_PATH=/path/to/cert.pem`

### Opción B: Azure Managed Identity

Usa Azure Managed Identity para autenticación sin contraseña. Esto es ideal para implementaciones en infraestructura de Azure (AKS, App Service, máquinas virtuales de Azure) donde hay una identidad administrada disponible.

**Cómo funciona:**

1. El pod/VM del bot tiene una identidad administrada (asignada por el sistema o por el usuario).
2. Una **credencial de identidad federada** vincula la identidad administrada con el registro de la aplicación de Entra ID.
3. En tiempo de ejecución, OpenClaw usa `@azure/identity` para adquirir tokens desde el endpoint Azure IMDS (`169.254.169.254`).
4. El token se pasa al SDK de Teams para la autenticación del bot.

**Requisitos previos:**

- Infraestructura de Azure con identidad administrada habilitada (identidad de carga de trabajo de AKS, App Service, VM)
- Credencial de identidad federada creada en el registro de la aplicación de Entra ID
- Acceso de red a IMDS (`169.254.169.254:80`) desde el pod/VM

**Config (identidad administrada asignada por el sistema):**

```json5
{
  channels: {
    msteams: {
      enabled: true,
      appId: "<APP_ID>",
      tenantId: "<TENANT_ID>",
      authType: "federated",
      useManagedIdentity: true,
      webhook: { port: 3978, path: "/api/messages" },
    },
  },
}
```

**Config (identidad administrada asignada por el usuario):**

```json5
{
  channels: {
    msteams: {
      enabled: true,
      appId: "<APP_ID>",
      tenantId: "<TENANT_ID>",
      authType: "federated",
      useManagedIdentity: true,
      managedIdentityClientId: "<MI_CLIENT_ID>",
      webhook: { port: 3978, path: "/api/messages" },
    },
  },
}
```

**Variables de entorno:**

- `MSTEAMS_AUTH_TYPE=federated`
- `MSTEAMS_USE_MANAGED_IDENTITY=true`
- `MSTEAMS_MANAGED_IDENTITY_CLIENT_ID=<client-id>` (solo para identidades asignadas por el usuario)

### Configuración de identidad de carga de trabajo de AKS

Para implementaciones de AKS que usan identidad de carga de trabajo:

1. **Habilita la identidad de carga de trabajo** en tu clúster de AKS.
2. **Crea una credencial de identidad federada** en el registro de la aplicación de Entra ID:

   ```bash
   az ad app federated-credential create --id <APP_OBJECT_ID> --parameters '{
     "name": "my-bot-workload-identity",
     "issuer": "<AKS_OIDC_ISSUER_URL>",
     "subject": "system:serviceaccount:<NAMESPACE>:<SERVICE_ACCOUNT>",
     "audiences": ["api://AzureADTokenExchange"]
   }'
   ```

3. **Anota la cuenta de servicio de Kubernetes** con el client ID de la aplicación:

   ```yaml
   apiVersion: v1
   kind: ServiceAccount
   metadata:
     name: my-bot-sa
     annotations:
       azure.workload.identity/client-id: "<APP_CLIENT_ID>"
   ```

4. **Etiqueta el pod** para la inyección de identidad de carga de trabajo:

   ```yaml
   metadata:
     labels:
       azure.workload.identity/use: "true"
   ```

5. **Asegura el acceso de red** a IMDS (`169.254.169.254`) — si usas NetworkPolicy, añade una regla de salida que permita tráfico a `169.254.169.254/32` en el puerto 80.

### Comparación de tipos de autenticación

| Método               | Configuración                                  | Ventajas                           | Desventajas                           |
| -------------------- | ---------------------------------------------- | ---------------------------------- | ------------------------------------- |
| **Secreto de cliente** | `appPassword`                                | Configuración simple               | Requiere rotación de secretos, menos seguro |
| **Certificado**      | `authType: "federated"` + `certificatePath`    | No hay secreto compartido por la red | Sobrecarga de gestión de certificados |
| **Managed Identity** | `authType: "federated"` + `useManagedIdentity` | Sin contraseña, sin secretos que gestionar | Requiere infraestructura de Azure     |

**Comportamiento predeterminado:** Cuando `authType` no está establecido, OpenClaw usa autenticación con secreto de cliente de forma predeterminada. Las configuraciones existentes siguen funcionando sin cambios.

## Desarrollo local (túneles)

Teams no puede llegar a `localhost`. Usa un túnel para desarrollo local:

**Opción A: ngrok**

```bash
ngrok http 3978
# Copia la URL https, p. ej., https://abc123.ngrok.io
# Establece el endpoint de mensajería en: https://abc123.ngrok.io/api/messages
```

**Opción B: Tailscale Funnel**

```bash
tailscale funnel 3978
# Usa tu URL de funnel de Tailscale como endpoint de mensajería
```

## Teams Developer Portal (alternativa)

En lugar de crear manualmente un ZIP del manifiesto, puedes usar el [Teams Developer Portal](https://dev.teams.microsoft.com/apps):

1. Haz clic en **+ New app**
2. Completa la información básica (nombre, descripción, información del desarrollador)
3. Ve a **App features** → **Bot**
4. Selecciona **Enter a bot ID manually** y pega el App ID de tu Azure Bot
5. Marca los alcances: **Personal**, **Team**, **Group Chat**
6. Haz clic en **Distribute** → **Download app package**
7. En Teams: **Apps** → **Manage your apps** → **Upload a custom app** → selecciona el ZIP

Esto suele ser más fácil que editar manifiestos JSON a mano.

## Probar el bot

**Opción A: Azure Web Chat (verifica primero el webhook)**

1. En Azure Portal → tu recurso Azure Bot → **Test in Web Chat**
2. Envía un mensaje; deberías ver una respuesta
3. Esto confirma que tu endpoint de webhook funciona antes de configurar Teams

**Opción B: Teams (después de instalar la aplicación)**

1. Instala la aplicación de Teams (carga lateral o catálogo de la organización)
2. Encuentra el bot en Teams y envíale un mensaje directo
3. Revisa los registros del gateway para ver la actividad entrante

## Configuración (mínima, solo texto)

1. **Asegúrate de que el plugin de Microsoft Teams esté disponible**
   - Las versiones empaquetadas actuales de OpenClaw ya lo incluyen.
   - Las instalaciones antiguas/personalizadas pueden añadirlo manualmente:
     - Desde npm: `openclaw plugins install @openclaw/msteams`
     - Desde un checkout local: `openclaw plugins install ./path/to/local/msteams-plugin`

2. **Registro del bot**
   - Crea un Azure Bot (consulta arriba) y anota:
     - App ID
     - Secreto de cliente (contraseña de la aplicación)
     - Tenant ID (single-tenant)

3. **Manifiesto de la aplicación de Teams**
   - Incluye una entrada `bot` con `botId = <App ID>`.
   - Alcances: `personal`, `team`, `groupChat`.
   - `supportsFiles: true` (obligatorio para el manejo de archivos en el alcance personal).
   - Añade permisos RSC (abajo).
   - Crea iconos: `outline.png` (32x32) y `color.png` (192x192).
   - Comprime juntos los tres archivos: `manifest.json`, `outline.png`, `color.png`.

4. **Configura OpenClaw**

   ```json5
   {
     channels: {
       msteams: {
         enabled: true,
         appId: "<APP_ID>",
         appPassword: "<APP_PASSWORD>",
         tenantId: "<TENANT_ID>",
         webhook: { port: 3978, path: "/api/messages" },
       },
     },
   }
   ```

   También puedes usar variables de entorno en lugar de claves de configuración:
   - `MSTEAMS_APP_ID`
   - `MSTEAMS_APP_PASSWORD`
   - `MSTEAMS_TENANT_ID`
   - `MSTEAMS_AUTH_TYPE` (opcional: `"secret"` o `"federated"`)
   - `MSTEAMS_CERTIFICATE_PATH` (federada + certificado)
   - `MSTEAMS_CERTIFICATE_THUMBPRINT` (opcional, no requerido para la autenticación)
   - `MSTEAMS_USE_MANAGED_IDENTITY` (federada + identidad administrada)
   - `MSTEAMS_MANAGED_IDENTITY_CLIENT_ID` (solo MI asignada por el usuario)

5. **Endpoint del bot**
   - Establece el Azure Bot Messaging Endpoint en:
     - `https://<host>:3978/api/messages` (o la ruta/puerto que elijas).

6. **Ejecuta el gateway**
   - El canal de Teams se inicia automáticamente cuando el plugin incluido o instalado manualmente está disponible y existe configuración `msteams` con credenciales.

## Acción de información de miembro

OpenClaw expone una acción `member-info` respaldada por Graph para Microsoft Teams, de modo que los agentes y las automatizaciones puedan resolver directamente desde Microsoft Graph los detalles de miembros del canal (nombre para mostrar, correo electrónico, rol).

Requisitos:

- Permiso RSC `Member.Read.Group` (ya está en el manifiesto recomendado)
- Para búsquedas entre equipos: permiso de aplicación Graph `User.Read.All` con consentimiento de administrador

La acción está controlada por `channels.msteams.actions.memberInfo` (predeterminado: habilitada cuando hay credenciales de Graph disponibles).

## Contexto de historial

- `channels.msteams.historyLimit` controla cuántos mensajes recientes de canal/grupo se incluyen en el prompt.
- Recurre a `messages.groupChat.historyLimit`. Establece `0` para desactivarlo (predeterminado: 50).
- El historial de hilo recuperado se filtra por listas de remitentes permitidos (`allowFrom` / `groupAllowFrom`), por lo que la inicialización del contexto del hilo solo incluye mensajes de remitentes permitidos.
- El contexto de archivos adjuntos citados (`ReplyTo*` derivado del HTML de respuesta de Teams) actualmente se pasa tal como se recibe.
- En otras palabras, las listas de permitidos controlan quién puede activar el agente; hoy solo se filtran determinadas rutas de contexto complementario.
- El historial de mensajes directos puede limitarse con `channels.msteams.dmHistoryLimit` (turnos del usuario). Sobrescrituras por usuario: `channels.msteams.dms["<user_id>"].historyLimit`.

## Permisos RSC actuales de Teams (manifiesto)

Estos son los **permisos resourceSpecific existentes** en nuestro manifiesto de la aplicación de Teams. Solo se aplican dentro del equipo/chat donde la aplicación está instalada.

**Para canales (alcance de equipo):**

- `ChannelMessage.Read.Group` (Application) - recibir todo el contenido de texto de los mensajes de canal sin @mention
- `ChannelMessage.Send.Group` (Application)
- `Member.Read.Group` (Application)
- `Owner.Read.Group` (Application)
- `ChannelSettings.Read.Group` (Application)
- `TeamMember.Read.Group` (Application)
- `TeamSettings.Read.Group` (Application)

**Para chats grupales:**

- `ChatMessage.Read.Chat` (Application) - recibir todos los mensajes del chat grupal sin @mention

## Ejemplo de manifiesto de Teams (con datos ocultos)

Ejemplo mínimo y válido con los campos requeridos. Sustituye los ID y las URL.

```json5
{
  $schema: "https://developer.microsoft.com/en-us/json-schemas/teams/v1.23/MicrosoftTeams.schema.json",
  manifestVersion: "1.23",
  version: "1.0.0",
  id: "00000000-0000-0000-0000-000000000000",
  name: { short: "OpenClaw" },
  developer: {
    name: "Your Org",
    websiteUrl: "https://example.com",
    privacyUrl: "https://example.com/privacy",
    termsOfUseUrl: "https://example.com/terms",
  },
  description: { short: "OpenClaw in Teams", full: "OpenClaw in Teams" },
  icons: { outline: "outline.png", color: "color.png" },
  accentColor: "#5B6DEF",
  bots: [
    {
      botId: "11111111-1111-1111-1111-111111111111",
      scopes: ["personal", "team", "groupChat"],
      isNotificationOnly: false,
      supportsCalling: false,
      supportsVideo: false,
      supportsFiles: true,
    },
  ],
  webApplicationInfo: {
    id: "11111111-1111-1111-1111-111111111111",
  },
  authorization: {
    permissions: {
      resourceSpecific: [
        { name: "ChannelMessage.Read.Group", type: "Application" },
        { name: "ChannelMessage.Send.Group", type: "Application" },
        { name: "Member.Read.Group", type: "Application" },
        { name: "Owner.Read.Group", type: "Application" },
        { name: "ChannelSettings.Read.Group", type: "Application" },
        { name: "TeamMember.Read.Group", type: "Application" },
        { name: "TeamSettings.Read.Group", type: "Application" },
        { name: "ChatMessage.Read.Chat", type: "Application" },
      ],
    },
  },
}
```

### Advertencias sobre el manifiesto (campos obligatorios)

- `bots[].botId` **debe** coincidir con el Azure Bot App ID.
- `webApplicationInfo.id` **debe** coincidir con el Azure Bot App ID.
- `bots[].scopes` debe incluir las superficies que planeas usar (`personal`, `team`, `groupChat`).
- `bots[].supportsFiles: true` es obligatorio para el manejo de archivos en el alcance personal.
- `authorization.permissions.resourceSpecific` debe incluir lectura/envío de canal si quieres tráfico de canal.

### Actualizar una aplicación existente

Para actualizar una aplicación de Teams ya instalada (por ejemplo, para añadir permisos RSC):

1. Actualiza tu `manifest.json` con la nueva configuración
2. **Incrementa el campo `version`** (por ejemplo, `1.0.0` → `1.1.0`)
3. **Vuelve a comprimir** el manifiesto con los iconos (`manifest.json`, `outline.png`, `color.png`)
4. Carga el nuevo zip:
   - **Opción A (Teams Admin Center):** Teams Admin Center → Teams apps → Manage apps → busca tu aplicación → Upload new version
   - **Opción B (carga lateral):** En Teams → Apps → Manage your apps → Upload a custom app
5. **Para canales de equipo:** reinstala la aplicación en cada equipo para que los nuevos permisos surtan efecto
6. **Cierra completamente y vuelve a abrir Teams** (no solo cierres la ventana) para borrar los metadatos en caché de la aplicación

## Capacidades: solo RSC frente a Graph

### Con **solo Teams RSC** (aplicación instalada, sin permisos de la API de Graph)

Funciona:

- Leer el contenido de **texto** de mensajes de canal.
- Enviar contenido de **texto** en mensajes de canal.
- Recibir archivos adjuntos en **mensajes directos**.

NO funciona:

- Contenido de **imágenes o archivos** en canales/grupos (la carga útil solo incluye un stub HTML).
- Descargar archivos adjuntos almacenados en SharePoint/OneDrive.
- Leer el historial de mensajes (más allá del evento en vivo del webhook).

### Con **Teams RSC + permisos de aplicación de Microsoft Graph**

Añade:

- Descarga de contenidos alojados (imágenes pegadas en mensajes).
- Descarga de archivos adjuntos almacenados en SharePoint/OneDrive.
- Lectura del historial de mensajes de canal/chat mediante Graph.

### RSC frente a la API de Graph

| Capacidad               | Permisos RSC        | API de Graph                         |
| ----------------------- | ------------------- | ------------------------------------ |
| **Mensajes en tiempo real** | Sí (mediante webhook) | No (solo sondeo)                  |
| **Mensajes históricos** | No                  | Sí (puede consultar el historial)    |
| **Complejidad de configuración** | Solo manifiesto de la aplicación | Requiere consentimiento de administrador + flujo de tokens |
| **Funciona sin conexión** | No (debe estar ejecutándose) | Sí (puede consultar en cualquier momento) |

**En resumen:** RSC sirve para escucha en tiempo real; la API de Graph es para acceso histórico. Para ponerse al día con mensajes perdidos mientras estabas desconectado, necesitas la API de Graph con `ChannelMessage.Read.All` (requiere consentimiento de administrador).

## Medios + historial habilitados con Graph (obligatorio para canales)

Si necesitas imágenes/archivos en **canales** o quieres obtener el **historial de mensajes**, debes habilitar permisos de Microsoft Graph y conceder consentimiento de administrador.

1. En **App Registration** de Entra ID (Azure AD), añade permisos de **Application** de Microsoft Graph:
   - `ChannelMessage.Read.All` (archivos adjuntos e historial de canal)
   - `Chat.Read.All` o `ChatMessage.Read.All` (chats grupales)
2. **Concede consentimiento de administrador** para el tenant.
3. Incrementa la **versión del manifiesto** de la aplicación de Teams, vuelve a cargarlo y **reinstala la aplicación en Teams**.
4. **Cierra completamente y vuelve a abrir Teams** para borrar los metadatos en caché de la aplicación.

**Permiso adicional para menciones de usuario:** Las @mentions de usuario funcionan de inmediato para usuarios que están en la conversación. Sin embargo, si quieres buscar y mencionar dinámicamente usuarios que **no están en la conversación actual**, añade el permiso de aplicación `User.Read.All` y concede consentimiento de administrador.

## Limitaciones conocidas

### Tiempos de espera del webhook

Teams entrega los mensajes mediante webhook HTTP. Si el procesamiento tarda demasiado (por ejemplo, respuestas lentas del LLM), puedes ver:

- Tiempos de espera del gateway
- Teams reintentando el mensaje (causando duplicados)
- Respuestas descartadas

OpenClaw maneja esto devolviendo rápido y enviando respuestas de forma proactiva, pero las respuestas muy lentas pueden seguir causando problemas.

### Formato

El markdown de Teams es más limitado que el de Slack o Discord:

- El formato básico funciona: **negrita**, _cursiva_, `code`, enlaces
- El markdown complejo (tablas, listas anidadas) puede no renderizarse correctamente
- Se admiten Adaptive Cards para encuestas y envíos arbitrarios de tarjetas (consulta abajo)

## Configuración

Ajustes clave (consulta `/gateway/configuration` para patrones compartidos de canales):

- `channels.msteams.enabled`: habilita/deshabilita el canal.
- `channels.msteams.appId`, `channels.msteams.appPassword`, `channels.msteams.tenantId`: credenciales del bot.
- `channels.msteams.webhook.port` (predeterminado: `3978`)
- `channels.msteams.webhook.path` (predeterminado: `/api/messages`)
- `channels.msteams.dmPolicy`: `pairing | allowlist | open | disabled` (predeterminado: pairing)
- `channels.msteams.allowFrom`: lista de permitidos para mensajes directos (se recomiendan IDs de objeto AAD). El asistente resuelve nombres a IDs durante la configuración cuando hay acceso a Graph disponible.
- `channels.msteams.dangerouslyAllowNameMatching`: interruptor de emergencia para volver a habilitar la coincidencia de UPN/nombre para mostrar mutable y el enrutamiento directo por nombre de equipo/canal.
- `channels.msteams.textChunkLimit`: tamaño de fragmentación del texto saliente.
- `channels.msteams.chunkMode`: `length` (predeterminado) o `newline` para dividir por líneas en blanco (límites de párrafo) antes de fragmentar por longitud.
- `channels.msteams.mediaAllowHosts`: lista de permitidos para hosts de archivos adjuntos entrantes (predeterminado: dominios de Microsoft/Teams).
- `channels.msteams.mediaAuthAllowHosts`: lista de permitidos para adjuntar encabezados Authorization en reintentos de medios (predeterminado: hosts de Graph + Bot Framework).
- `channels.msteams.requireMention`: requiere @mention en canales/grupos (predeterminado: true).
- `channels.msteams.replyStyle`: `thread | top-level` (consulta [Estilo de respuesta](#reply-style-threads-vs-posts)).
- `channels.msteams.teams.<teamId>.replyStyle`: sobrescritura por equipo.
- `channels.msteams.teams.<teamId>.requireMention`: sobrescritura por equipo.
- `channels.msteams.teams.<teamId>.tools`: sobrescrituras predeterminadas de la política de herramientas por equipo (`allow`/`deny`/`alsoAllow`) usadas cuando falta una sobrescritura de canal.
- `channels.msteams.teams.<teamId>.toolsBySender`: sobrescrituras predeterminadas de la política de herramientas por equipo y por remitente (se admite el comodín `"*"`).
- `channels.msteams.teams.<teamId>.channels.<conversationId>.replyStyle`: sobrescritura por canal.
- `channels.msteams.teams.<teamId>.channels.<conversationId>.requireMention`: sobrescritura por canal.
- `channels.msteams.teams.<teamId>.channels.<conversationId>.tools`: sobrescrituras de la política de herramientas por canal (`allow`/`deny`/`alsoAllow`).
- `channels.msteams.teams.<teamId>.channels.<conversationId>.toolsBySender`: sobrescrituras de la política de herramientas por canal y por remitente (se admite el comodín `"*"`).
- Las claves `toolsBySender` deben usar prefijos explícitos:
  `id:`, `e164:`, `username:`, `name:` (las claves heredadas sin prefijo siguen asignándose solo a `id:`).
- `channels.msteams.actions.memberInfo`: habilita o deshabilita la acción de información de miembro respaldada por Graph (predeterminado: habilitada cuando hay credenciales de Graph disponibles).
- `channels.msteams.authType`: tipo de autenticación — `"secret"` (predeterminado) o `"federated"`.
- `channels.msteams.certificatePath`: ruta al archivo de certificado PEM (federada + autenticación por certificado).
- `channels.msteams.certificateThumbprint`: huella digital del certificado (opcional, no requerida para la autenticación).
- `channels.msteams.useManagedIdentity`: habilita autenticación con identidad administrada (modo federado).
- `channels.msteams.managedIdentityClientId`: client ID para identidad administrada asignada por el usuario.
- `channels.msteams.sharePointSiteId`: ID del sitio de SharePoint para cargas de archivos en chats grupales/canales (consulta [Envío de archivos en chats grupales](#sending-files-in-group-chats)).

## Enrutamiento y sesiones

- Las claves de sesión siguen el formato estándar de agente (consulta [/concepts/session](/es/concepts/session)):
  - Los mensajes directos comparten la sesión principal (`agent:<agentId>:<mainKey>`).
  - Los mensajes de canal/grupo usan el ID de conversación:
    - `agent:<agentId>:msteams:channel:<conversationId>`
    - `agent:<agentId>:msteams:group:<conversationId>`

## Estilo de respuesta: hilos frente a publicaciones

Teams introdujo recientemente dos estilos de interfaz de canal sobre el mismo modelo de datos subyacente:

| Estilo                  | Descripción                                              | `replyStyle` recomendado |
| ----------------------- | -------------------------------------------------------- | ------------------------ |
| **Posts** (clásico)     | Los mensajes aparecen como tarjetas con respuestas en hilo debajo | `thread` (predeterminado) |
| **Threads** (tipo Slack) | Los mensajes fluyen linealmente, más parecido a Slack   | `top-level`              |

**El problema:** La API de Teams no expone qué estilo de interfaz usa un canal. Si usas el `replyStyle` incorrecto:

- `thread` en un canal con estilo Threads → las respuestas aparecen anidadas de forma extraña
- `top-level` en un canal con estilo Posts → las respuestas aparecen como publicaciones independientes de nivel superior en lugar de dentro del hilo

**Solución:** Configura `replyStyle` por canal según cómo esté configurado el canal:

```json5
{
  channels: {
    msteams: {
      replyStyle: "thread",
      teams: {
        "19:abc...@thread.tacv2": {
          channels: {
            "19:xyz...@thread.tacv2": {
              replyStyle: "top-level",
            },
          },
        },
      },
    },
  },
}
```

## Archivos adjuntos e imágenes

**Limitaciones actuales:**

- **Mensajes directos:** las imágenes y los archivos adjuntos funcionan mediante las API de archivos del bot de Teams.
- **Canales/grupos:** los archivos adjuntos viven en el almacenamiento de M365 (SharePoint/OneDrive). La carga útil del webhook solo incluye un stub HTML, no los bytes reales del archivo. **Se requieren permisos de la API de Graph** para descargar archivos adjuntos de canal.
- Para envíos explícitos centrados primero en archivos, usa `action=upload-file` con `media` / `filePath` / `path`; el `message` opcional pasa a ser el texto/comentario adjunto, y `filename` sobrescribe el nombre cargado.

Sin permisos de Graph, los mensajes de canal con imágenes se recibirán solo como texto (el contenido de la imagen no es accesible para el bot).
De forma predeterminada, OpenClaw solo descarga medios desde nombres de host de Microsoft/Teams. Sobrescribe esto con `channels.msteams.mediaAllowHosts` (usa `["*"]` para permitir cualquier host).
Los encabezados Authorization solo se adjuntan para hosts en `channels.msteams.mediaAuthAllowHosts` (predeterminado: hosts de Graph + Bot Framework). Mantén esta lista estricta (evita sufijos multi-tenant).

## Envío de archivos en chats grupales

Los bots pueden enviar archivos en mensajes directos mediante el flujo FileConsentCard (integrado). Sin embargo, **enviar archivos en chats grupales/canales** requiere configuración adicional:

| Contexto                 | Cómo se envían los archivos               | Configuración necesaria                          |
| ------------------------ | ----------------------------------------- | ------------------------------------------------ |
| **Mensajes directos**    | FileConsentCard → el usuario acepta → el bot carga | Funciona de inmediato                      |
| **Chats grupales/canales** | Cargar en SharePoint → compartir enlace | Requiere `sharePointSiteId` + permisos de Graph |
| **Imágenes (cualquier contexto)** | Inline codificado en Base64       | Funciona de inmediato                            |

### Por qué los chats grupales necesitan SharePoint

Los bots no tienen una unidad personal de OneDrive (el endpoint de la API de Graph `/me/drive` no funciona para identidades de aplicación). Para enviar archivos en chats grupales/canales, el bot carga el archivo en un **sitio de SharePoint** y crea un enlace para compartir.

### Configuración

1. **Añade permisos de la API de Graph** en Entra ID (Azure AD) → App Registration:
   - `Sites.ReadWrite.All` (Application) - cargar archivos en SharePoint
   - `Chat.Read.All` (Application) - opcional, habilita enlaces para compartir por usuario

2. **Concede consentimiento de administrador** para el tenant.

3. **Obtén el ID de tu sitio de SharePoint:**

   ```bash
   # Mediante Graph Explorer o curl con un token válido:
   curl -H "Authorization: Bearer $TOKEN" \
     "https://graph.microsoft.com/v1.0/sites/{hostname}:/{site-path}"

   # Ejemplo: para un sitio en "contoso.sharepoint.com/sites/BotFiles"
   curl -H "Authorization: Bearer $TOKEN" \
     "https://graph.microsoft.com/v1.0/sites/contoso.sharepoint.com:/sites/BotFiles"

   # La respuesta incluye: "id": "contoso.sharepoint.com,guid1,guid2"
   ```

4. **Configura OpenClaw:**

   ```json5
   {
     channels: {
       msteams: {
         // ... other config ...
         sharePointSiteId: "contoso.sharepoint.com,guid1,guid2",
       },
     },
   }
   ```

### Comportamiento de uso compartido

| Permiso                                | Comportamiento de uso compartido                         |
| -------------------------------------- | -------------------------------------------------------- |
| `Sites.ReadWrite.All` solo             | Enlace para compartir en toda la organización (cualquiera en la organización puede acceder) |
| `Sites.ReadWrite.All` + `Chat.Read.All` | Enlace para compartir por usuario (solo los miembros del chat pueden acceder) |

El uso compartido por usuario es más seguro, ya que solo los participantes del chat pueden acceder al archivo. Si falta el permiso `Chat.Read.All`, el bot recurre al uso compartido para toda la organización.

### Comportamiento de respaldo

| Escenario                                         | Resultado                                         |
| ------------------------------------------------- | ------------------------------------------------- |
| Chat grupal + archivo + `sharePointSiteId` configurado | Carga en SharePoint, envía enlace para compartir |
| Chat grupal + archivo + sin `sharePointSiteId`    | Intenta cargar en OneDrive (puede fallar), envía solo texto |
| Chat personal + archivo                           | Flujo FileConsentCard (funciona sin SharePoint)   |
| Cualquier contexto + imagen                       | Inline codificado en Base64 (funciona sin SharePoint) |

### Ubicación donde se almacenan los archivos

Los archivos cargados se almacenan en una carpeta `/OpenClawShared/` dentro de la biblioteca de documentos predeterminada del sitio de SharePoint configurado.

## Encuestas (Adaptive Cards)

OpenClaw envía encuestas de Teams como Adaptive Cards (no hay una API nativa de encuestas en Teams).

- CLI: `openclaw message poll --channel msteams --target conversation:<id> ...`
- Los votos los registra el gateway en `~/.openclaw/msteams-polls.json`.
- El gateway debe permanecer en línea para registrar votos.
- Las encuestas aún no publican automáticamente resúmenes de resultados (inspecciona el archivo de almacenamiento si hace falta).

## Adaptive Cards (arbitrarias)

Envía cualquier JSON de Adaptive Card a usuarios o conversaciones de Teams usando la herramienta `message` o la CLI.

El parámetro `card` acepta un objeto JSON de Adaptive Card. Cuando se proporciona `card`, el texto del mensaje es opcional.

**Herramienta del agente:**

```json5
{
  action: "send",
  channel: "msteams",
  target: "user:<id>",
  card: {
    type: "AdaptiveCard",
    version: "1.5",
    body: [{ type: "TextBlock", text: "Hello!" }],
  },
}
```

**CLI:**

```bash
openclaw message send --channel msteams \
  --target "conversation:19:abc...@thread.tacv2" \
  --card '{"type":"AdaptiveCard","version":"1.5","body":[{"type":"TextBlock","text":"Hello!"}]}'
```

Consulta la [documentación de Adaptive Cards](https://adaptivecards.io/) para ver el esquema de tarjetas y ejemplos. Para conocer los detalles del formato de destino, consulta [Formatos de destino](#target-formats) abajo.

## Formatos de destino

Los destinos de MSTeams usan prefijos para distinguir entre usuarios y conversaciones:

| Tipo de destino        | Formato                          | Ejemplo                                             |
| ---------------------- | -------------------------------- | --------------------------------------------------- |
| Usuario (por ID)       | `user:<aad-object-id>`           | `user:40a1a0ed-4ff2-4164-a219-55518990c197`         |
| Usuario (por nombre)   | `user:<display-name>`            | `user:John Smith` (requiere la API de Graph)        |
| Grupo/canal            | `conversation:<conversation-id>` | `conversation:19:abc123...@thread.tacv2`            |
| Grupo/canal (sin procesar) | `<conversation-id>`         | `19:abc123...@thread.tacv2` (si contiene `@thread`) |

**Ejemplos de CLI:**

```bash
# Enviar a un usuario por ID
openclaw message send --channel msteams --target "user:40a1a0ed-..." --message "Hello"

# Enviar a un usuario por nombre para mostrar (activa la búsqueda con la API de Graph)
openclaw message send --channel msteams --target "user:John Smith" --message "Hello"

# Enviar a un chat grupal o canal
openclaw message send --channel msteams --target "conversation:19:abc...@thread.tacv2" --message "Hello"

# Enviar una Adaptive Card a una conversación
openclaw message send --channel msteams --target "conversation:19:abc...@thread.tacv2" \
  --card '{"type":"AdaptiveCard","version":"1.5","body":[{"type":"TextBlock","text":"Hello"}]}'
```

**Ejemplos de herramientas del agente:**

```json5
{
  action: "send",
  channel: "msteams",
  target: "user:John Smith",
  message: "Hello!",
}
```

```json5
{
  action: "send",
  channel: "msteams",
  target: "conversation:19:abc...@thread.tacv2",
  card: {
    type: "AdaptiveCard",
    version: "1.5",
    body: [{ type: "TextBlock", text: "Hello" }],
  },
}
```

Nota: Sin el prefijo `user:`, los nombres usan por defecto la resolución de grupo/equipo. Usa siempre `user:` cuando apuntes a personas por nombre para mostrar.

## Mensajería proactiva

- Los mensajes proactivos solo son posibles **después** de que un usuario haya interactuado, porque almacenamos referencias de conversación en ese momento.
- Consulta `/gateway/configuration` para `dmPolicy` y el control mediante lista de permitidos.

## IDs de equipo y canal (error común)

El parámetro de consulta `groupId` en las URL de Teams **NO** es el ID de equipo usado para la configuración. Extrae los IDs de la ruta de la URL en su lugar:

**URL del equipo:**

```
https://teams.microsoft.com/l/team/19%3ABk4j...%40thread.tacv2/conversations?groupId=...
                                    └────────────────────────────┘
                                    ID del equipo (decodifica esta URL)
```

**URL del canal:**

```
https://teams.microsoft.com/l/channel/19%3A15bc...%40thread.tacv2/ChannelName?groupId=...
                                      └─────────────────────────┘
                                      ID del canal (decodifica esta URL)
```

**Para la configuración:**

- ID del equipo = segmento de ruta después de `/team/` (URL decodificada, por ejemplo, `19:Bk4j...@thread.tacv2`)
- ID del canal = segmento de ruta después de `/channel/` (URL decodificada)
- **Ignora** el parámetro de consulta `groupId`

## Canales privados

Los bots tienen soporte limitado en canales privados:

| Función                      | Canales estándar | Canales privados      |
| --------------------------- | ---------------- | --------------------- |
| Instalación del bot         | Sí               | Limitada              |
| Mensajes en tiempo real (webhook) | Sí        | Puede no funcionar    |
| Permisos RSC                | Sí               | Pueden comportarse de forma distinta |
| @mentions                   | Sí               | Si el bot es accesible |
| Historial con la API de Graph | Sí             | Sí (con permisos)     |

**Soluciones si los canales privados no funcionan:**

1. Usa canales estándar para interacciones con el bot
2. Usa mensajes directos: los usuarios siempre pueden enviar mensajes directamente al bot
3. Usa la API de Graph para acceso histórico (requiere `ChannelMessage.Read.All`)

## Solución de problemas

### Problemas comunes

- **Las imágenes no aparecen en canales:** faltan permisos de Graph o consentimiento de administrador. Reinstala la aplicación de Teams y cierra/reabre Teams por completo.
- **No hay respuestas en el canal:** las menciones son obligatorias de forma predeterminada; establece `channels.msteams.requireMention=false` o configúralo por equipo/canal.
- **Desajuste de versión (Teams sigue mostrando el manifiesto anterior):** elimina y vuelve a añadir la aplicación, y cierra Teams por completo para actualizar.
- **401 Unauthorized desde el webhook:** es lo esperado al probar manualmente sin Azure JWT; significa que el endpoint es accesible, pero la autenticación falló. Usa Azure Web Chat para probar correctamente.

### Errores al cargar el manifiesto

- **"Icon file cannot be empty":** El manifiesto hace referencia a archivos de icono de 0 bytes. Crea iconos PNG válidos (32x32 para `outline.png`, 192x192 para `color.png`).
- **"webApplicationInfo.Id already in use":** La aplicación sigue instalada en otro equipo/chat. Búscala y desinstálala primero, o espera 5-10 minutos para la propagación.
- **"Something went wrong" al cargar:** Cárgala mediante [https://admin.teams.microsoft.com](https://admin.teams.microsoft.com) en su lugar, abre las herramientas de desarrollo del navegador (F12) → pestaña Network, y revisa el cuerpo de la respuesta para ver el error real.
- **Fallo de carga lateral:** Prueba con "Upload an app to your org's app catalog" en lugar de "Upload a custom app"; esto suele omitir las restricciones de carga lateral.

### Los permisos RSC no funcionan

1. Verifica que `webApplicationInfo.id` coincida exactamente con el App ID de tu bot
2. Vuelve a cargar la aplicación y reinstálala en el equipo/chat
3. Comprueba si el administrador de tu organización ha bloqueado los permisos RSC
4. Confirma que estás usando el alcance correcto: `ChannelMessage.Read.Group` para equipos, `ChatMessage.Read.Chat` para chats grupales

## Referencias

- [Create Azure Bot](https://learn.microsoft.com/en-us/azure/bot-service/bot-service-quickstart-registration) - guía de configuración de Azure Bot
- [Teams Developer Portal](https://dev.teams.microsoft.com/apps) - crear/gestionar aplicaciones de Teams
- [Teams app manifest schema](https://learn.microsoft.com/en-us/microsoftteams/platform/resources/schema/manifest-schema)
- [Receive channel messages with RSC](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/conversations/channel-messages-with-rsc)
- [RSC permissions reference](https://learn.microsoft.com/en-us/microsoftteams/platform/graph-api/rsc/resource-specific-consent)
- [Teams bot file handling](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/bots-filesv4) (canal/grupo requiere Graph)
- [Proactive messaging](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/conversations/send-proactive-messages)

## Relacionado

- [Resumen de canales](/es/channels) — todos los canales compatibles
- [Pairing](/es/channels/pairing) — autenticación de mensajes directos y flujo de emparejamiento
- [Grupos](/es/channels/groups) — comportamiento del chat grupal y restricción por mención
- [Enrutamiento de canales](/es/channels/channel-routing) — enrutamiento de sesiones para mensajes
- [Seguridad](/es/gateway/security) — modelo de acceso y fortalecimiento
