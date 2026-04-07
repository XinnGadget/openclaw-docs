---
read_when:
    - Depurar la autenticación del modelo o el vencimiento de OAuth
    - Documentar la autenticación o el almacenamiento de credenciales
summary: 'Autenticación de modelos: OAuth, claves de API, reutilización de Claude CLI y setup-token de Anthropic'
title: Autenticación
x-i18n:
    generated_at: "2026-04-07T05:02:23Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9db0ad9eccd7e3e3ca328adaad260bc4288a8ccdbe2dc0c24d9fd049b7ab9231
    source_path: gateway/authentication.md
    workflow: 15
---

# Autenticación (proveedores de modelos)

<Note>
Esta página cubre la autenticación de **proveedores de modelos** (claves de API, OAuth, reutilización de Claude CLI y setup-token de Anthropic). Para la autenticación de **conexión del gateway** (token, contraseña, trusted-proxy), consulta [Configuración](/es/gateway/configuration) y [Trusted Proxy Auth](/es/gateway/trusted-proxy-auth).
</Note>

OpenClaw admite OAuth y claves de API para proveedores de modelos. Para hosts de gateway siempre activos, las claves de API suelen ser la opción más predecible. Los flujos de suscripción/OAuth también son compatibles cuando coinciden con el modelo de cuenta de tu proveedor.

Consulta [/concepts/oauth](/es/concepts/oauth) para ver el flujo completo de OAuth y la estructura de almacenamiento.
Para la autenticación basada en SecretRef (proveedores `env`/`file`/`exec`), consulta [Gestión de secretos](/es/gateway/secrets).
Para las reglas de elegibilidad de credenciales/códigos de motivo que usa `models status --probe`, consulta
[Semántica de credenciales de autenticación](/es/auth-credential-semantics).

## Configuración recomendada (clave de API, cualquier proveedor)

Si estás ejecutando un gateway de larga duración, comienza con una clave de API para el proveedor que elijas.
En el caso concreto de Anthropic, la autenticación con clave de API sigue siendo la configuración de servidor más predecible, pero OpenClaw también admite reutilizar un inicio de sesión local de Claude CLI.

1. Crea una clave de API en la consola de tu proveedor.
2. Colócala en el **host del gateway** (la máquina que ejecuta `openclaw gateway`).

```bash
export <PROVIDER>_API_KEY="..."
openclaw models status
```

3. Si el Gateway se ejecuta con systemd/launchd, es preferible poner la clave en
   `~/.openclaw/.env` para que el daemon pueda leerla:

```bash
cat >> ~/.openclaw/.env <<'EOF'
<PROVIDER>_API_KEY=...
EOF
```

Luego reinicia el daemon (o reinicia tu proceso de Gateway) y vuelve a comprobar:

```bash
openclaw models status
openclaw doctor
```

Si prefieres no gestionar las variables de entorno manualmente, el onboarding puede almacenar
claves de API para que las use el daemon: `openclaw onboard`.

Consulta [Ayuda](/es/help) para obtener detalles sobre la herencia de variables de entorno (`env.shellEnv`,
`~/.openclaw/.env`, systemd/launchd).

## Anthropic: compatibilidad de Claude CLI y token

La autenticación con setup-token de Anthropic sigue estando disponible en OpenClaw como una ruta de token admitida. Desde entonces, el personal de Anthropic nos ha dicho que el uso de Claude CLI al estilo OpenClaw vuelve a estar permitido, por lo que OpenClaw trata la reutilización de Claude CLI y el uso de `claude -p` como autorizados para esta integración, a menos que Anthropic publique una nueva política. Cuando la reutilización de Claude CLI está disponible en el host, esa es ahora la ruta preferida.

Para hosts de gateway de larga duración, una clave de API de Anthropic sigue siendo la configuración más predecible. Si quieres reutilizar un inicio de sesión existente de Claude en el mismo host, usa la ruta de Anthropic Claude CLI en onboarding/configure.

Entrada manual de token (cualquier proveedor; escribe `auth-profiles.json` + actualiza la configuración):

```bash
openclaw models auth paste-token --provider openrouter
```

Las referencias a perfiles de autenticación también son compatibles para credenciales estáticas:

- Las credenciales `api_key` pueden usar `keyRef: { source, provider, id }`
- Las credenciales `token` pueden usar `tokenRef: { source, provider, id }`
- Los perfiles en modo OAuth no admiten credenciales SecretRef; si `auth.profiles.<id>.mode` está configurado como `"oauth"`, se rechaza la entrada `keyRef`/`tokenRef` respaldada por SecretRef para ese perfil.

Comprobación apta para automatización (salida `1` cuando falta o está vencido, `2` cuando está por vencer):

```bash
openclaw models status --check
```

Sondeos de autenticación en vivo:

```bash
openclaw models status --probe
```

Notas:

- Las filas del sondeo pueden proceder de perfiles de autenticación, credenciales de entorno o `models.json`.
- Si `auth.order.<provider>` explícito omite un perfil almacenado, el sondeo informa
  `excluded_by_auth_order` para ese perfil en lugar de intentarlo.
- Si existe autenticación pero OpenClaw no puede resolver un candidato de modelo apto para sondeo para
  ese proveedor, el sondeo informa `status: no_model`.
- Los enfriamientos de límite de tasa pueden tener alcance por modelo. Un perfil en enfriamiento para un
  modelo puede seguir siendo utilizable para un modelo hermano en el mismo proveedor.

Los scripts operativos opcionales (systemd/Termux) están documentados aquí:
[Scripts de supervisión de autenticación](/es/help/scripts#auth-monitoring-scripts)

## Nota sobre Anthropic

El backend `claude-cli` de Anthropic vuelve a ser compatible.

- El personal de Anthropic nos dijo que esta ruta de integración de OpenClaw vuelve a estar permitida.
- Por lo tanto, OpenClaw trata la reutilización de Claude CLI y el uso de `claude -p` como autorizados
  para ejecuciones respaldadas por Anthropic, a menos que Anthropic publique una nueva política.
- Las claves de API de Anthropic siguen siendo la opción más predecible para hosts de gateway
  de larga duración y para un control explícito de la facturación del lado del servidor.

## Comprobar el estado de autenticación del modelo

```bash
openclaw models status
openclaw doctor
```

## Comportamiento de rotación de claves de API (gateway)

Algunos proveedores admiten reintentar una solicitud con claves alternativas cuando una llamada a la API
alcanza un límite de tasa del proveedor.

- Orden de prioridad:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY` (anulación única)
  - `<PROVIDER>_API_KEYS`
  - `<PROVIDER>_API_KEY`
  - `<PROVIDER>_API_KEY_*`
- Los proveedores de Google también incluyen `GOOGLE_API_KEY` como respaldo adicional.
- La misma lista de claves se deduplica antes de usarse.
- OpenClaw reintenta con la siguiente clave solo para errores de límite de tasa (por ejemplo
  `429`, `rate_limit`, `quota`, `resource exhausted`, `Too many concurrent
requests`, `ThrottlingException`, `concurrency limit reached`, o
  `workers_ai ... quota limit exceeded`).
- Los errores que no son de límite de tasa no se reintentan con claves alternativas.
- Si fallan todas las claves, se devuelve el error final del último intento.

## Controlar qué credencial se usa

### Por sesión (comando de chat)

Usa `/model <alias-or-id>@<profileId>` para fijar una credencial concreta de proveedor para la sesión actual (ejemplos de ids de perfil: `anthropic:default`, `anthropic:work`).

Usa `/model` (o `/model list`) para un selector compacto; usa `/model status` para la vista completa (candidatos + siguiente perfil de autenticación, además de detalles del endpoint del proveedor cuando están configurados).

### Por agente (anulación de CLI)

Configura una anulación explícita del orden de perfiles de autenticación para un agente (se almacena en el `auth-state.json` de ese agente):

```bash
openclaw models auth order get --provider anthropic
openclaw models auth order set --provider anthropic anthropic:default
openclaw models auth order clear --provider anthropic
```

Usa `--agent <id>` para dirigirte a un agente específico; omítelo para usar el agente predeterminado configurado.
Cuando depures problemas de orden, `openclaw models status --probe` muestra los perfiles almacenados omitidos
como `excluded_by_auth_order` en lugar de omitirlos silenciosamente.
Cuando depures problemas de enfriamiento, recuerda que los enfriamientos por límite de tasa pueden estar vinculados
a un único id de modelo en lugar de a todo el perfil del proveedor.

## Solución de problemas

### "No credentials found"

Si falta el perfil de Anthropic, configura una clave de API de Anthropic en el
**host del gateway** o configura la ruta de setup-token de Anthropic, y luego vuelve a comprobar:

```bash
openclaw models status
```

### Token a punto de vencer/vencido

Ejecuta `openclaw models status` para confirmar qué perfil está por vencer. Si falta un
perfil de token de Anthropic o está vencido, actualiza esa configuración mediante
setup-token o migra a una clave de API de Anthropic.
