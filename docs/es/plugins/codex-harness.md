---
read_when:
    - Quieres usar el arnés app-server de Codex incluido
    - Necesitas referencias de modelos de Codex y ejemplos de configuración
    - Quieres desactivar el respaldo de PI para despliegues solo de Codex
summary: Ejecutar turnos de agente integrados de OpenClaw mediante el arnés app-server de Codex incluido
title: Arnés de Codex
x-i18n:
    generated_at: "2026-04-11T02:45:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: 60e1dcf4f1a00c63c3ef31d72feac44bce255421c032c58fa4fd67295b3daf23
    source_path: plugins/codex-harness.md
    workflow: 15
---

# Arnés de Codex

El plugin `codex` incluido permite que OpenClaw ejecute turnos de agente integrados a través del app-server de Codex en lugar del arnés PI integrado.

Úsalo cuando quieras que Codex controle la sesión del agente de bajo nivel: descubrimiento de modelos, reanudación nativa de hilos, compactación nativa y ejecución del app-server.
OpenClaw sigue controlando los canales de chat, los archivos de sesión, la selección de modelos, las herramientas,
las aprobaciones, la entrega de medios y el espejo visible de la transcripción.

El arnés está desactivado de forma predeterminada. Solo se selecciona cuando el plugin `codex` está
habilitado y el modelo resuelto es un modelo `codex/*`, o cuando fuerzas explícitamente
`embeddedHarness.runtime: "codex"` o `OPENCLAW_AGENT_RUNTIME=codex`.
Si nunca configuras `codex/*`, las ejecuciones existentes de PI, OpenAI, Anthropic, Gemini, local
y proveedores personalizados mantienen su comportamiento actual.

## Elige el prefijo de modelo correcto

OpenClaw tiene rutas separadas para el acceso con forma de OpenAI y de Codex:

| Referencia de modelo  | Ruta de runtime                              | Úsalo cuando                                                             |
| --------------------- | -------------------------------------------- | ------------------------------------------------------------------------ |
| `openai/gpt-5.4`      | Proveedor OpenAI mediante la infraestructura OpenClaw/PI | Quieres acceso directo a la API de OpenAI Platform con `OPENAI_API_KEY`. |
| `openai-codex/gpt-5.4` | Proveedor OpenAI Codex OAuth mediante PI    | Quieres ChatGPT/Codex OAuth sin el arnés app-server de Codex.            |
| `codex/gpt-5.4`       | Proveedor Codex incluido más arnés de Codex | Quieres ejecución nativa del app-server de Codex para el turno del agente integrado. |

El arnés de Codex solo toma referencias de modelo `codex/*`. Las referencias existentes `openai/*`,
`openai-codex/*`, Anthropic, Gemini, xAI, locales y de proveedores personalizados mantienen
sus rutas normales.

## Requisitos

- OpenClaw con el plugin `codex` incluido disponible.
- App-server de Codex `0.118.0` o más reciente.
- Autenticación de Codex disponible para el proceso del app-server.

El plugin bloquea handshakes del app-server más antiguos o sin versión. Eso mantiene
a OpenClaw en la superficie de protocolo con la que se ha probado.

Para las pruebas smoke en vivo y con Docker, la autenticación suele provenir de `OPENAI_API_KEY`, además de
archivos opcionales de Codex CLI como `~/.codex/auth.json` y
`~/.codex/config.toml`. Usa el mismo material de autenticación que usa tu app-server de Codex local.

## Configuración mínima

Usa `codex/gpt-5.4`, habilita el plugin incluido y fuerza el arnés `codex`:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
  agents: {
    defaults: {
      model: "codex/gpt-5.4",
      embeddedHarness: {
        runtime: "codex",
        fallback: "none",
      },
    },
  },
}
```

Si tu configuración usa `plugins.allow`, incluye también `codex` allí:

```json5
{
  plugins: {
    allow: ["codex"],
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
}
```

Establecer `agents.defaults.model` o el modelo de un agente en `codex/<model>` también
habilita automáticamente el plugin `codex` incluido. La entrada explícita del plugin sigue siendo
útil en configuraciones compartidas porque deja clara la intención del despliegue.

## Agregar Codex sin reemplazar otros modelos

Mantén `runtime: "auto"` cuando quieras Codex para los modelos `codex/*` y PI para
todo lo demás:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
  agents: {
    defaults: {
      model: {
        primary: "codex/gpt-5.4",
        fallbacks: ["openai/gpt-5.4", "anthropic/claude-opus-4-6"],
      },
      models: {
        "codex/gpt-5.4": { alias: "codex" },
        "codex/gpt-5.4-mini": { alias: "codex-mini" },
        "openai/gpt-5.4": { alias: "gpt" },
        "anthropic/claude-opus-4-6": { alias: "opus" },
      },
      embeddedHarness: {
        runtime: "auto",
        fallback: "pi",
      },
    },
  },
}
```

Con esta forma:

- `/model codex` o `/model codex/gpt-5.4` usa el arnés app-server de Codex.
- `/model gpt` o `/model openai/gpt-5.4` usa la ruta del proveedor OpenAI.
- `/model opus` usa la ruta del proveedor Anthropic.
- Si se selecciona un modelo que no es Codex, PI sigue siendo el arnés de compatibilidad.

## Despliegues solo con Codex

Desactiva el respaldo de PI cuando necesites demostrar que cada turno de agente integrado usa
el arnés de Codex:

```json5
{
  agents: {
    defaults: {
      model: "codex/gpt-5.4",
      embeddedHarness: {
        runtime: "codex",
        fallback: "none",
      },
    },
  },
}
```

Anulación por entorno:

```bash
OPENCLAW_AGENT_RUNTIME=codex \
OPENCLAW_AGENT_HARNESS_FALLBACK=none \
openclaw gateway run
```

Con el respaldo desactivado, OpenClaw falla pronto si el plugin Codex está desactivado,
si el modelo solicitado no es una referencia `codex/*`, si el app-server es demasiado antiguo o si el
app-server no puede iniciarse.

## Codex por agente

Puedes hacer que un agente use solo Codex mientras el agente predeterminado mantiene la
selección automática normal:

```json5
{
  agents: {
    defaults: {
      embeddedHarness: {
        runtime: "auto",
        fallback: "pi",
      },
    },
    list: [
      {
        id: "main",
        default: true,
        model: "anthropic/claude-opus-4-6",
      },
      {
        id: "codex",
        name: "Codex",
        model: "codex/gpt-5.4",
        embeddedHarness: {
          runtime: "codex",
          fallback: "none",
        },
      },
    ],
  },
}
```

Usa los comandos de sesión normales para cambiar de agente y modelo. `/new` crea una sesión nueva de
OpenClaw y el arnés de Codex crea o reanuda su hilo sidecar del app-server según sea necesario.
`/reset` borra el vínculo de sesión de OpenClaw para ese hilo.

## Descubrimiento de modelos

De forma predeterminada, el plugin Codex consulta al app-server los modelos disponibles. Si
el descubrimiento falla o agota el tiempo, usa el catálogo de respaldo incluido:

- `codex/gpt-5.4`
- `codex/gpt-5.4-mini`
- `codex/gpt-5.2`

Puedes ajustar el descubrimiento en `plugins.entries.codex.config.discovery`:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          discovery: {
            enabled: true,
            timeoutMs: 2500,
          },
        },
      },
    },
  },
}
```

Desactiva el descubrimiento cuando quieras que el inicio evite sondear Codex y se limite al
catálogo de respaldo:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          discovery: {
            enabled: false,
          },
        },
      },
    },
  },
}
```

## Conexión y política del app-server

De forma predeterminada, el plugin inicia Codex localmente con:

```bash
codex app-server --listen stdio://
```

Puedes mantener ese valor predeterminado y ajustar solo la política nativa de Codex:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          appServer: {
            approvalPolicy: "on-request",
            sandbox: "workspace-write",
            serviceTier: "priority",
          },
        },
      },
    },
  },
}
```

Para un app-server que ya esté en ejecución, usa transporte WebSocket:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          appServer: {
            transport: "websocket",
            url: "ws://127.0.0.1:39175",
            authToken: "${CODEX_APP_SERVER_TOKEN}",
            requestTimeoutMs: 60000,
          },
        },
      },
    },
  },
}
```

Campos `appServer` compatibles:

| Campo               | Predeterminado                             | Significado                                                              |
| ------------------- | ------------------------------------------ | ------------------------------------------------------------------------ |
| `transport`         | `"stdio"`                                  | `"stdio"` inicia Codex; `"websocket"` se conecta a `url`.                |
| `command`           | `"codex"`                                  | Ejecutable para transporte stdio.                                        |
| `args`              | `["app-server", "--listen", "stdio://"]`   | Argumentos para transporte stdio.                                        |
| `url`               | sin establecer                             | URL del app-server WebSocket.                                            |
| `authToken`         | sin establecer                             | Token Bearer para transporte WebSocket.                                  |
| `headers`           | `{}`                                       | Encabezados WebSocket adicionales.                                       |
| `requestTimeoutMs`  | `60000`                                    | Tiempo de espera para llamadas del plano de control del app-server.      |
| `approvalPolicy`    | `"never"`                                  | Política nativa de aprobaciones de Codex enviada al inicio/reanudación/turno del hilo. |
| `sandbox`           | `"workspace-write"`                        | Modo nativo de sandbox de Codex enviado al inicio/reanudación del hilo.  |
| `approvalsReviewer` | `"user"`                                   | Usa `"guardian_subagent"` para que el guardián de Codex revise las aprobaciones nativas. |
| `serviceTier`       | sin establecer                             | Nivel de servicio opcional de Codex, por ejemplo `"priority"`.           |

Las variables de entorno más antiguas siguen funcionando como respaldo para pruebas locales cuando
el campo de configuración correspondiente no está establecido:

- `OPENCLAW_CODEX_APP_SERVER_BIN`
- `OPENCLAW_CODEX_APP_SERVER_ARGS`
- `OPENCLAW_CODEX_APP_SERVER_APPROVAL_POLICY`
- `OPENCLAW_CODEX_APP_SERVER_SANDBOX`
- `OPENCLAW_CODEX_APP_SERVER_GUARDIAN=1`

La configuración es preferible para despliegues reproducibles.

## Recetas comunes

Codex local con el transporte stdio predeterminado:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
}
```

Validación de arnés solo con Codex, con el respaldo de PI desactivado:

```json5
{
  embeddedHarness: {
    fallback: "none",
  },
  plugins: {
    entries: {
      codex: {
        enabled: true,
      },
    },
  },
}
```

Aprobaciones de Codex revisadas por Guardian:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          appServer: {
            approvalPolicy: "on-request",
            approvalsReviewer: "guardian_subagent",
            sandbox: "workspace-write",
          },
        },
      },
    },
  },
}
```

App-server remoto con encabezados explícitos:

```json5
{
  plugins: {
    entries: {
      codex: {
        enabled: true,
        config: {
          appServer: {
            transport: "websocket",
            url: "ws://gateway-host:39175",
            headers: {
              "X-OpenClaw-Agent": "main",
            },
          },
        },
      },
    },
  },
}
```

El cambio de modelo sigue estando controlado por OpenClaw. Cuando una sesión de OpenClaw está asociada
a un hilo existente de Codex, el siguiente turno vuelve a enviar al
app-server el modelo `codex/*`, el proveedor, la política de aprobaciones, el sandbox y el nivel de servicio
actualmente seleccionados. Cambiar de `codex/gpt-5.4` a `codex/gpt-5.2` mantiene el
vínculo con el hilo, pero le pide a Codex que continúe con el modelo recién seleccionado.

## Comando Codex

El plugin incluido registra `/codex` como un comando de barra autorizado. Es
genérico y funciona en cualquier canal que admita comandos de texto de OpenClaw.

Formas comunes:

- `/codex status` muestra conectividad en vivo con el app-server, modelos, cuenta, límites de velocidad, servidores MCP y Skills.
- `/codex models` enumera los modelos en vivo del app-server de Codex.
- `/codex threads [filter]` enumera los hilos recientes de Codex.
- `/codex resume <thread-id>` adjunta la sesión actual de OpenClaw a un hilo existente de Codex.
- `/codex compact` le pide al app-server de Codex que compacte el hilo adjunto.
- `/codex review` inicia la revisión nativa de Codex para el hilo adjunto.
- `/codex account` muestra el estado de la cuenta y de los límites de velocidad.
- `/codex mcp` enumera el estado de los servidores MCP del app-server de Codex.
- `/codex skills` enumera las Skills del app-server de Codex.

`/codex resume` escribe el mismo archivo de vinculación sidecar que usa el arnés para
los turnos normales. En el siguiente mensaje, OpenClaw reanuda ese hilo de Codex, pasa el
modelo `codex/*` de OpenClaw actualmente seleccionado al app-server y mantiene habilitado el historial
extendido.

La superficie de comandos requiere un app-server de Codex `0.118.0` o más reciente. Los métodos de
control individuales se informan como `unsupported by this Codex app-server` si un
app-server futuro o personalizado no expone ese método JSON-RPC.

## Herramientas, medios y compactación

El arnés de Codex solo cambia el ejecutor de agente integrado de bajo nivel.

OpenClaw sigue compilando la lista de herramientas y recibiendo resultados dinámicos de herramientas desde el
arnés. El texto, las imágenes, el video, la música, TTS, las aprobaciones y la salida
de herramientas de mensajería continúan por la ruta normal de entrega de OpenClaw.

Cuando el modelo seleccionado usa el arnés de Codex, la compactación nativa de hilos se
delegada al app-server de Codex. OpenClaw mantiene un espejo de la transcripción para el historial de canales,
la búsqueda, `/new`, `/reset` y futuros cambios de modelo o arnés. El
espejo incluye el prompt del usuario, el texto final del asistente y registros ligeros de razonamiento o plan de Codex cuando el
app-server los emite.

La generación de medios no requiere PI. La generación de imágenes, video, música, PDF, TTS y la
comprensión de medios siguen usando la configuración correspondiente de proveedor/modelo, como
`agents.defaults.imageGenerationModel`, `videoGenerationModel`, `pdfModel` y
`messages.tts`.

## Solución de problemas

**Codex no aparece en `/model`:** habilita `plugins.entries.codex.enabled`,
establece una referencia de modelo `codex/*`, o comprueba si `plugins.allow` excluye `codex`.

**OpenClaw vuelve a PI:** establece `embeddedHarness.fallback: "none"` o
`OPENCLAW_AGENT_HARNESS_FALLBACK=none` durante las pruebas.

**El app-server es rechazado:** actualiza Codex para que el handshake del app-server
informe la versión `0.118.0` o posterior.

**El descubrimiento de modelos es lento:** reduce `plugins.entries.codex.config.discovery.timeoutMs`
o desactiva el descubrimiento.

**El transporte WebSocket falla de inmediato:** comprueba `appServer.url`, `authToken`
y que el app-server remoto use la misma versión del protocolo app-server de Codex.

**Un modelo que no es Codex usa PI:** eso es lo esperado. El arnés de Codex solo toma
referencias de modelo `codex/*`.

## Relacionado

- [Plugins de arnés de agente](/es/plugins/sdk-agent-harness)
- [Proveedores de modelos](/es/concepts/model-providers)
- [Referencia de configuración](/es/gateway/configuration-reference)
- [Pruebas](/es/help/testing#live-codex-app-server-harness-smoke)
