---
read_when:
    - Ampliar qa-lab o qa-channel
    - Añadir escenarios de QA respaldados por el repositorio
    - Crear una automatización de QA más realista en torno al panel del Gateway
summary: Estructura de la automatización privada de QA para qa-lab, qa-channel, escenarios sembrados e informes de protocolo
title: Automatización E2E de QA
x-i18n:
    generated_at: "2026-04-07T05:02:00Z"
    model: gpt-5.4
    provider: openai
    source_hash: 113e89d8d3ee8ef3058d95b9aea9a1c2335b07794446be2d231c0faeb044b23b
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# Automatización E2E de QA

La pila privada de QA está pensada para poner a prueba OpenClaw de una forma
más realista y con forma de canal que lo que puede lograr una sola prueba
unitaria.

Piezas actuales:

- `extensions/qa-channel`: canal de mensajes sintético con superficies de MD, canal, hilo,
  reacción, edición y eliminación.
- `extensions/qa-lab`: interfaz de usuario de depuración y bus de QA para observar la transcripción,
  inyectar mensajes entrantes y exportar un informe en Markdown.
- `qa/`: recursos semilla respaldados por el repositorio para la tarea de inicio y los
  escenarios base de QA.

El flujo actual del operador de QA es un sitio de QA de dos paneles:

- Izquierda: panel del Gateway (Control UI) con el agente.
- Derecha: QA Lab, que muestra la transcripción tipo Slack y el plan de escenarios.

Ejecuta esto con:

```bash
pnpm qa:lab:up
```

Eso compila el sitio de QA, inicia la vía del gateway respaldada por Docker y expone la
página de QA Lab, donde un operador o un bucle de automatización puede darle al agente una
misión de QA, observar el comportamiento real del canal y registrar qué funcionó, qué falló o qué
siguió bloqueado.

## Semillas respaldadas por el repositorio

Los recursos semilla viven en `qa/`:

- `qa/QA_KICKOFF_TASK.md`
- `qa/seed-scenarios.json`

Estos están intencionadamente en git para que el plan de QA sea visible tanto para las personas como para el
agente. La lista base debe seguir siendo lo bastante amplia como para cubrir:

- chat por MD y en canal
- comportamiento de hilos
- ciclo de vida de las acciones de mensajes
- callbacks de cron
- recuperación de memoria
- cambio de modelo
- transferencia a subagente
- lectura del repositorio y de la documentación
- una tarea de compilación pequeña, como Lobster Invaders

## Informes

`qa-lab` exporta un informe de protocolo en Markdown a partir de la línea de tiempo del bus observada.
El informe debe responder:

- Qué funcionó
- Qué falló
- Qué siguió bloqueado
- Qué escenarios de seguimiento vale la pena añadir

## Documentación relacionada

- [Pruebas](/es/help/testing)
- [QA Channel](/es/channels/qa-channel)
- [Panel](/web/dashboard)
