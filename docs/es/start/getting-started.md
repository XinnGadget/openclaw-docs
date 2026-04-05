---
read_when:
    - Configuración inicial desde cero
    - Quieres la ruta más rápida hacia un chat funcional
summary: Instala OpenClaw y ejecuta tu primer chat en minutos.
title: Primeros pasos
x-i18n:
    generated_at: "2026-04-05T10:46:53Z"
    model: gpt-5.4
    provider: openai
    source_hash: c43eee6f0d3f593e3cf0767bfacb3e0ae38f51a2615d594303786ae1d4a6d2c3
    source_path: start/getting-started.md
    workflow: 15
---

# Primeros pasos

Instala OpenClaw, ejecuta la incorporación y chatea con tu asistente de IA, todo en
unos 5 minutos. Al final tendrás una Gateway en funcionamiento, la autenticación
configurada y una sesión de chat operativa.

## Qué necesitas

- **Node.js** — se recomienda Node 24 (también se admite Node 22.14+)
- **Una clave de API** de un proveedor de modelos (Anthropic, OpenAI, Google, etc.) — la incorporación te la solicitará

<Tip>
Comprueba tu versión de Node con `node --version`.
**Usuarios de Windows:** tanto Windows nativo como WSL2 son compatibles. WSL2 es más
estable y se recomienda para la experiencia completa. Consulta [Windows](/platforms/windows).
¿Necesitas instalar Node? Consulta [Configuración de Node](/install/node).
</Tip>

## Configuración rápida

<Steps>
  <Step title="Instalar OpenClaw">
    <Tabs>
      <Tab title="macOS / Linux">
        ```bash
        curl -fsSL https://openclaw.ai/install.sh | bash
        ```
        <img
  src="/assets/install-script.svg"
  alt="Proceso del script de instalación"
  className="rounded-lg"
/>
      </Tab>
      <Tab title="Windows (PowerShell)">
        ```powershell
        iwr -useb https://openclaw.ai/install.ps1 | iex
        ```
      </Tab>
    </Tabs>

    <Note>
    Otros métodos de instalación (Docker, Nix, npm): [Instalación](/install).
    </Note>

  </Step>
  <Step title="Ejecutar la incorporación">
    ```bash
    openclaw onboard --install-daemon
    ```

    El asistente te guía para elegir un proveedor de modelos, establecer una clave de API
    y configurar la Gateway. Tarda unos 2 minutos.

    Consulta [Incorporación (CLI)](/start/wizard) para la referencia completa.

  </Step>
  <Step title="Verificar que la Gateway está en ejecución">
    ```bash
    openclaw gateway status
    ```

    Deberías ver que la Gateway está escuchando en el puerto 18789.

  </Step>
  <Step title="Abrir el panel">
    ```bash
    openclaw dashboard
    ```

    Esto abre la IU de control en tu navegador. Si carga, todo está funcionando.

  </Step>
  <Step title="Enviar tu primer mensaje">
    Escribe un mensaje en el chat de la IU de control y deberías recibir una respuesta de la IA.

    ¿Quieres chatear desde tu teléfono? El canal más rápido de configurar es
    [Telegram](/channels/telegram) (solo se necesita un token de bot). Consulta [Canales](/channels)
    para ver todas las opciones.

  </Step>
</Steps>

<Accordion title="Avanzado: montar una compilación personalizada de la IU de control">
  Si mantienes una compilación localizada o personalizada del panel, dirige
  `gateway.controlUi.root` a un directorio que contenga tus recursos estáticos
  compilados y `index.html`.

```bash
mkdir -p "$HOME/.openclaw/control-ui-custom"
# Copia tus archivos estáticos compilados en ese directorio.
```

Luego establece:

```json
{
  "gateway": {
    "controlUi": {
      "enabled": true,
      "root": "$HOME/.openclaw/control-ui-custom"
    }
  }
}
```

Reinicia la gateway y vuelve a abrir el panel:

```bash
openclaw gateway restart
openclaw dashboard
```

</Accordion>

## Qué hacer después

<Columns>
  <Card title="Conectar un canal" href="/channels" icon="message-square">
    Discord, Feishu, iMessage, Matrix, Microsoft Teams, Signal, Slack, Telegram, WhatsApp, Zalo y más.
  </Card>
  <Card title="Emparejamiento y seguridad" href="/channels/pairing" icon="shield">
    Controla quién puede enviar mensajes a tu agente.
  </Card>
  <Card title="Configurar la Gateway" href="/gateway/configuration" icon="settings">
    Modelos, herramientas, sandbox y configuraciones avanzadas.
  </Card>
  <Card title="Explorar herramientas" href="/tools" icon="wrench">
    Navegador, exec, búsqueda web, Skills y plugins.
  </Card>
</Columns>

<Accordion title="Avanzado: variables de entorno">
  Si ejecutas OpenClaw como una cuenta de servicio o quieres rutas personalizadas:

- `OPENCLAW_HOME` — directorio principal para la resolución interna de rutas
- `OPENCLAW_STATE_DIR` — reemplaza el directorio de estado
- `OPENCLAW_CONFIG_PATH` — reemplaza la ruta del archivo de configuración

Referencia completa: [Variables de entorno](/help/environment).
</Accordion>
