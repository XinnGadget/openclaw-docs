---
read_when:
    - Primeira configuração do zero
    - Você quer o caminho mais rápido para um chat funcionando
summary: Instale o OpenClaw e inicie seu primeiro chat em minutos.
title: Primeiros passos
x-i18n:
    generated_at: "2026-04-05T10:48:00Z"
    model: gpt-5.4
    provider: openai
    source_hash: c43eee6f0d3f593e3cf0767bfacb3e0ae38f51a2615d594303786ae1d4a6d2c3
    source_path: start/getting-started.md
    workflow: 15
---

# Primeiros passos

Instale o OpenClaw, execute o onboarding e converse com seu assistente de IA —
tudo em cerca de 5 minutos. Ao final, você terá um Gateway em execução, a
autenticação configurada e uma sessão de chat funcionando.

## O que você precisa

- **Node.js** — Node 24 recomendado (Node 22.14+ também é compatível)
- **Uma chave de API** de um provedor de modelos (Anthropic, OpenAI, Google etc.) — o onboarding vai solicitar

<Tip>
Verifique sua versão do Node com `node --version`.
**Usuários do Windows:** tanto o Windows nativo quanto o WSL2 são compatíveis. O WSL2 é mais
estável e recomendado para a experiência completa. Consulte [Windows](/platforms/windows).
Precisa instalar o Node? Consulte [Configuração do Node](/install/node).
</Tip>

## Configuração rápida

<Steps>
  <Step title="Instale o OpenClaw">
    <Tabs>
      <Tab title="macOS / Linux">
        ```bash
        curl -fsSL https://openclaw.ai/install.sh | bash
        ```
        <img
  src="/assets/install-script.svg"
  alt="Processo do script de instalação"
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
    Outros métodos de instalação (Docker, Nix, npm): [Instalação](/install).
    </Note>

  </Step>
  <Step title="Execute o onboarding">
    ```bash
    openclaw onboard --install-daemon
    ```

    O assistente orienta você na escolha de um provedor de modelo, na definição de uma chave de API
    e na configuração do Gateway. Isso leva cerca de 2 minutos.

    Consulte [Onboarding (CLI)](/start/wizard) para a referência completa.

  </Step>
  <Step title="Verifique se o Gateway está em execução">
    ```bash
    openclaw gateway status
    ```

    Você deverá ver o Gateway escutando na porta 18789.

  </Step>
  <Step title="Abra o painel">
    ```bash
    openclaw dashboard
    ```

    Isso abre a UI de controle no navegador. Se ela carregar, tudo está funcionando.

  </Step>
  <Step title="Envie sua primeira mensagem">
    Digite uma mensagem no chat da UI de controle e você deverá receber uma resposta da IA.

    Quer conversar pelo telefone em vez disso? O canal mais rápido de configurar é o
    [Telegram](/channels/telegram) (basta um token de bot). Consulte [Canais](/channels)
    para ver todas as opções.

  </Step>
</Steps>

<Accordion title="Avançado: montar uma build personalizada da UI de controle">
  Se você mantém uma build localizada ou personalizada do painel, aponte
  `gateway.controlUi.root` para um diretório que contenha seus assets estáticos
  compilados e o `index.html`.

```bash
mkdir -p "$HOME/.openclaw/control-ui-custom"
# Copie seus arquivos estáticos compilados para esse diretório.
```

Depois defina:

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

Reinicie o gateway e reabra o painel:

```bash
openclaw gateway restart
openclaw dashboard
```

</Accordion>

## O que fazer em seguida

<Columns>
  <Card title="Conectar um canal" href="/channels" icon="message-square">
    Discord, Feishu, iMessage, Matrix, Microsoft Teams, Signal, Slack, Telegram, WhatsApp, Zalo e muito mais.
  </Card>
  <Card title="Pareamento e segurança" href="/channels/pairing" icon="shield">
    Controle quem pode enviar mensagens ao seu agente.
  </Card>
  <Card title="Configurar o Gateway" href="/gateway/configuration" icon="settings">
    Modelos, ferramentas, sandbox e configurações avançadas.
  </Card>
  <Card title="Explorar ferramentas" href="/tools" icon="wrench">
    Navegador, exec, pesquisa na web, Skills e plugins.
  </Card>
</Columns>

<Accordion title="Avançado: variáveis de ambiente">
  Se você executa o OpenClaw como uma conta de serviço ou quer caminhos personalizados:

- `OPENCLAW_HOME` — diretório home para resolução de caminhos internos
- `OPENCLAW_STATE_DIR` — substitui o diretório de estado
- `OPENCLAW_CONFIG_PATH` — substitui o caminho do arquivo de configuração

Referência completa: [Variáveis de ambiente](/help/environment).
</Accordion>
