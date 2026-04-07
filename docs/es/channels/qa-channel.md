---
read_when:
    - Estás conectando el transporte sintético de QA en una ejecución de prueba local o de CI
    - Necesitas la superficie de configuración de `qa-channel` incluida
    - Estás iterando en la automatización de QA de extremo a extremo
summary: Plugin de canal sintético de clase Slack para escenarios de QA deterministas de OpenClaw
title: Canal de QA
x-i18n:
    generated_at: "2026-04-07T05:01:35Z"
    model: gpt-5.4
    provider: openai
    source_hash: 65c2c908d3ec27c827087616c4ea278f10686810091058321ff26f68296a1782
    source_path: channels/qa-channel.md
    workflow: 15
---

# Canal de QA

`qa-channel` es un transporte de mensajes sintético incluido para la QA automatizada de OpenClaw.

No es un canal de producción. Existe para ejercitar el mismo límite de plugin
de canal que usan los transportes reales, mientras mantiene el estado
determinista y completamente inspeccionable.

## Lo que hace hoy

- Gramática de destino de clase Slack:
  - `dm:<user>`
  - `channel:<room>`
  - `thread:<room>/<thread>`
- Bus sintético respaldado por HTTP para:
  - inyección de mensajes entrantes
  - captura de transcripciones salientes
  - creación de hilos
  - reacciones
  - ediciones
  - eliminaciones
  - acciones de búsqueda y lectura
- Ejecutor de autoverificación del lado del host incluido que escribe un informe en Markdown

## Configuración

```json
{
  "channels": {
    "qa-channel": {
      "baseUrl": "http://127.0.0.1:43123",
      "botUserId": "openclaw",
      "botDisplayName": "OpenClaw QA",
      "allowFrom": ["*"],
      "pollTimeoutMs": 1000
    }
  }
}
```

Claves de cuenta compatibles:

- `baseUrl`
- `botUserId`
- `botDisplayName`
- `pollTimeoutMs`
- `allowFrom`
- `defaultTo`
- `actions.messages`
- `actions.reactions`
- `actions.search`
- `actions.threads`

## Ejecutor

Corte vertical actual:

```bash
pnpm qa:e2e
```

Esto ahora se enruta a través de la extensión incluida `qa-lab`. Inicia el bus
de QA dentro del repositorio, arranca el segmento de ejecución incluido de
`qa-channel`, ejecuta una autoverificación determinista y escribe un informe en
Markdown en `.artifacts/qa-e2e/`.

UI privada de depuración:

```bash
pnpm qa:lab:up
```

Ese único comando compila el sitio de QA, inicia la pila de gateway + QA Lab
respaldada por Docker e imprime la URL de QA Lab. Desde ese sitio puedes
seleccionar escenarios, elegir la vía del modelo, lanzar ejecuciones
individuales y ver los resultados en vivo.

Suite completa de QA respaldada por el repositorio:

```bash
pnpm openclaw qa suite
```

Eso inicia el depurador privado de QA en una URL local, separado del paquete de
Control UI distribuido.

## Alcance

El alcance actual es intencionalmente limitado:

- bus + transporte de plugin
- gramática de enrutamiento con hilos
- acciones de mensajes que pertenecen al canal
- informes en Markdown
- sitio de QA respaldado por Docker con controles de ejecución

El trabajo de seguimiento añadirá:

- ejecución de matriz de proveedor/modelo
- detección de escenarios más rica
- orquestación nativa de OpenClaw más adelante
