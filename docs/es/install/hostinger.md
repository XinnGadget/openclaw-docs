---
read_when:
    - Configurar OpenClaw en Hostinger
    - Buscando un VPS administrado para OpenClaw
    - Usar el OpenClaw de 1 clic de Hostinger
summary: Aloja OpenClaw en Hostinger
title: Hostinger
x-i18n:
    generated_at: "2026-04-14T02:08:42Z"
    model: gpt-5.4
    provider: openai
    source_hash: cf173cdcf6344f8ee22e839a27f4e063a3a102186f9acc07c4a33d4794e2c034
    source_path: install/hostinger.md
    workflow: 15
---

# Hostinger

Ejecuta un Gateway persistente de OpenClaw en [Hostinger](https://www.hostinger.com/openclaw) mediante una implementación administrada de **1 clic** o una instalación en **VPS**.

## Requisitos previos

- Cuenta de Hostinger ([registro](https://www.hostinger.com/openclaw))
- Aproximadamente 5-10 minutos

## Opción A: OpenClaw de 1 clic

La forma más rápida de empezar. Hostinger se encarga de la infraestructura, Docker y las actualizaciones automáticas.

<Steps>
  <Step title="Comprar e iniciar">
    1. En la [página de OpenClaw de Hostinger](https://www.hostinger.com/openclaw), elige un plan de OpenClaw administrado y completa la compra.

    <Note>
    Durante la compra puedes seleccionar créditos de **Ready-to-Use AI** que se compran por adelantado y se integran al instante dentro de OpenClaw; no se necesitan cuentas externas ni claves de API de otros proveedores. Puedes empezar a chatear de inmediato. Como alternativa, puedes proporcionar tu propia clave de Anthropic, OpenAI, Google Gemini o xAI durante la configuración.
    </Note>

  </Step>

  <Step title="Seleccionar un canal de mensajería">
    Elige uno o más canales para conectar:

    - **WhatsApp** -- escanea el código QR que se muestra en el asistente de configuración.
    - **Telegram** -- pega el token del bot de [BotFather](https://t.me/BotFather).

  </Step>

  <Step title="Completar la instalación">
    Haz clic en **Finish** para implementar la instancia. Cuando esté lista, accede al panel de OpenClaw desde **OpenClaw Overview** en hPanel.
  </Step>

</Steps>

## Opción B: OpenClaw en VPS

Más control sobre tu servidor. Hostinger implementa OpenClaw mediante Docker en tu VPS y tú lo administras a través de **Docker Manager** en hPanel.

<Steps>
  <Step title="Comprar un VPS">
    1. En la [página de OpenClaw de Hostinger](https://www.hostinger.com/openclaw), elige un plan de OpenClaw en VPS y completa la compra.

    <Note>
    Puedes seleccionar créditos de **Ready-to-Use AI** durante la compra; se compran por adelantado y se integran al instante dentro de OpenClaw, para que puedas empezar a chatear sin cuentas externas ni claves de API de otros proveedores.
    </Note>

  </Step>

  <Step title="Configurar OpenClaw">
    Cuando se aprovisione el VPS, completa los campos de configuración:

    - **Gateway token** -- se genera automáticamente; guárdalo para usarlo más tarde.
    - **Número de WhatsApp** -- tu número con código de país (opcional).
    - **Token del bot de Telegram** -- de [BotFather](https://t.me/BotFather) (opcional).
    - **Claves de API** -- solo son necesarias si no seleccionaste créditos de Ready-to-Use AI durante la compra.

  </Step>

  <Step title="Iniciar OpenClaw">
    Haz clic en **Deploy**. Una vez en ejecución, abre el panel de OpenClaw desde hPanel haciendo clic en **Open**.
  </Step>

</Steps>

Los registros, reinicios y actualizaciones se gestionan directamente desde la interfaz de Docker Manager en hPanel. Para actualizar, pulsa **Update** en Docker Manager y eso descargará la imagen más reciente.

## Verifica tu configuración

Envía "Hi" a tu asistente en el canal que conectaste. OpenClaw responderá y te guiará por las preferencias iniciales.

## Solución de problemas

**El panel no carga** -- Espera unos minutos a que el contenedor termine de aprovisionarse. Revisa los registros de Docker Manager en hPanel.

**El contenedor de Docker se reinicia continuamente** -- Abre los registros de Docker Manager y busca errores de configuración (tokens faltantes, claves de API no válidas).

**El bot de Telegram no responde** -- Envía tu mensaje de código de emparejamiento desde Telegram directamente como un mensaje dentro de tu chat de OpenClaw para completar la conexión.

## Siguientes pasos

- [Canales](/es/channels) -- conecta Telegram, WhatsApp, Discord y más
- [Configuración del Gateway](/es/gateway/configuration) -- todas las opciones de configuración
