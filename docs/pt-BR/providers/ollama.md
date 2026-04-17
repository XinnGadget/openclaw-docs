---
read_when:
    - Você quer executar o OpenClaw com modelos na nuvem ou locais via Ollama
    - Você precisa de orientações de instalação e configuração do Ollama
summary: Execute o OpenClaw com o Ollama (modelos na nuvem e locais)
title: Ollama
x-i18n:
    generated_at: "2026-04-15T14:40:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: 098e083e0fc484bddb5270eb630c55d7832039b462d1710372b6afece5cefcdf
    source_path: providers/ollama.md
    workflow: 15
---

# Ollama

O OpenClaw integra-se com a API nativa do Ollama (`/api/chat`) para modelos hospedados na nuvem e servidores Ollama locais/autohospedados. Você pode usar o Ollama em três modos: `Cloud + Local` por meio de um host Ollama acessível, `Cloud only` em `https://ollama.com` ou `Local only` em um host Ollama acessível.

<Warning>
**Usuários de Ollama remoto**: Não use a URL compatível com OpenAI `/v1` (`http://host:11434/v1`) com o OpenClaw. Isso quebra a chamada de ferramentas e os modelos podem gerar JSON bruto de ferramentas como texto simples. Use a URL nativa da API do Ollama: `baseUrl: "http://host:11434"` (sem `/v1`).
</Warning>

## Primeiros passos

Escolha seu método e modo de configuração preferidos.

<Tabs>
  <Tab title="Onboarding (recomendado)">
    **Melhor para:** o caminho mais rápido para uma configuração funcional do Ollama na nuvem ou local.

    <Steps>
      <Step title="Executar o onboarding">
        ```bash
        openclaw onboard
        ```

        Selecione **Ollama** na lista de provedores.
      </Step>
      <Step title="Escolher seu modo">
        - **Cloud + Local** — host Ollama local mais modelos na nuvem roteados por esse host
        - **Cloud only** — modelos Ollama hospedados via `https://ollama.com`
        - **Local only** — apenas modelos locais
      </Step>
      <Step title="Selecionar um modelo">
        `Cloud only` solicita `OLLAMA_API_KEY` e sugere padrões hospedados na nuvem. `Cloud + Local` e `Local only` pedem uma URL base do Ollama, descobrem os modelos disponíveis e fazem `pull` automaticamente do modelo local selecionado se ele ainda não estiver disponível. `Cloud + Local` também verifica se esse host Ollama está autenticado para acesso à nuvem.
      </Step>
      <Step title="Verificar se o modelo está disponível">
        ```bash
        openclaw models list --provider ollama
        ```
      </Step>
    </Steps>

    ### Modo não interativo

    ```bash
    openclaw onboard --non-interactive \
      --auth-choice ollama \
      --accept-risk
    ```

    Opcionalmente, especifique uma URL base personalizada ou um modelo:

    ```bash
    openclaw onboard --non-interactive \
      --auth-choice ollama \
      --custom-base-url "http://ollama-host:11434" \
      --custom-model-id "qwen3.5:27b" \
      --accept-risk
    ```

  </Tab>

  <Tab title="Configuração manual">
    **Melhor para:** controle total sobre configuração na nuvem ou local.

    <Steps>
      <Step title="Escolher nuvem ou local">
        - **Cloud + Local**: instale o Ollama, autentique-se com `ollama signin` e encaminhe as solicitações de nuvem por esse host
        - **Cloud only**: use `https://ollama.com` com uma `OLLAMA_API_KEY`
        - **Local only**: instale o Ollama em [ollama.com/download](https://ollama.com/download)
      </Step>
      <Step title="Fazer pull de um modelo local (apenas local)">
        ```bash
        ollama pull gemma4
        # ou
        ollama pull gpt-oss:20b
        # ou
        ollama pull llama3.3
        ```
      </Step>
      <Step title="Ativar o Ollama no OpenClaw">
        Para `Cloud only`, use sua `OLLAMA_API_KEY` real. Para configurações baseadas em host, qualquer valor placeholder funciona:

        ```bash
        # Nuvem
        export OLLAMA_API_KEY="your-ollama-api-key"

        # Apenas local
        export OLLAMA_API_KEY="ollama-local"

        # Ou configure no seu arquivo de configuração
        openclaw config set models.providers.ollama.apiKey "OLLAMA_API_KEY"
        ```
      </Step>
      <Step title="Inspecionar e definir seu modelo">
        ```bash
        openclaw models list
        openclaw models set ollama/gemma4
        ```

        Ou defina o padrão na configuração:

        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "ollama/gemma4" },
            },
          },
        }
        ```
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Modelos na nuvem

<Tabs>
  <Tab title="Cloud + Local">
    `Cloud + Local` usa um host Ollama acessível como ponto de controle tanto para modelos locais quanto na nuvem. Esse é o fluxo híbrido preferido do Ollama.

    Use **Cloud + Local** durante a configuração. O OpenClaw solicita a URL base do Ollama, descobre os modelos locais desse host e verifica se o host está autenticado para acesso à nuvem com `ollama signin`. Quando o host está autenticado, o OpenClaw também sugere padrões hospedados na nuvem, como `kimi-k2.5:cloud`, `minimax-m2.7:cloud` e `glm-5.1:cloud`.

    Se o host ainda não estiver autenticado, o OpenClaw mantém a configuração apenas local até você executar `ollama signin`.

  </Tab>

  <Tab title="Cloud only">
    `Cloud only` é executado na API hospedada do Ollama em `https://ollama.com`.

    Use **Cloud only** durante a configuração. O OpenClaw solicita `OLLAMA_API_KEY`, define `baseUrl: "https://ollama.com"` e inicializa a lista de modelos hospedados na nuvem. Esse caminho **não** exige um servidor Ollama local nem `ollama signin`.

  </Tab>

  <Tab title="Local only">
    No modo somente local, o OpenClaw descobre modelos a partir da instância Ollama configurada. Esse caminho é para servidores Ollama locais ou autohospedados.

    Atualmente, o OpenClaw sugere `gemma4` como padrão local.

  </Tab>
</Tabs>

## Descoberta de modelos (provedor implícito)

Quando você define `OLLAMA_API_KEY` (ou um perfil de autenticação) e **não** define `models.providers.ollama`, o OpenClaw descobre modelos da instância local do Ollama em `http://127.0.0.1:11434`.

| Comportamento       | Detalhe                                                                                                                                                              |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Consulta ao catálogo | Consulta `/api/tags`                                                                                                                                                 |
| Detecção de capacidades | Usa buscas `/api/show` por melhor esforço para ler `contextWindow` e detectar capacidades (incluindo visão)                                                        |
| Modelos com visão   | Modelos com capacidade `vision` reportada por `/api/show` são marcados como compatíveis com imagem (`input: ["text", "image"]`), então o OpenClaw injeta imagens automaticamente no prompt |
| Detecção de raciocínio | Marca `reasoning` com uma heurística baseada no nome do modelo (`r1`, `reasoning`, `think`)                                                                         |
| Limites de tokens   | Define `maxTokens` com o limite máximo de tokens padrão do Ollama usado pelo OpenClaw                                                                                |
| Custos              | Define todos os custos como `0`                                                                                                                                      |

Isso evita entradas manuais de modelos e mantém o catálogo alinhado com a instância local do Ollama.

```bash
# Veja quais modelos estão disponíveis
ollama list
openclaw models list
```

Para adicionar um novo modelo, basta fazer `pull` dele com o Ollama:

```bash
ollama pull mistral
```

O novo modelo será descoberto automaticamente e ficará disponível para uso.

<Note>
Se você definir `models.providers.ollama` explicitamente, a descoberta automática será ignorada e você terá que definir os modelos manualmente. Consulte a seção de configuração explícita abaixo.
</Note>

## Configuração

<Tabs>
  <Tab title="Básica (descoberta implícita)">
    O caminho mais simples para ativação somente local é por variável de ambiente:

    ```bash
    export OLLAMA_API_KEY="ollama-local"
    ```

    <Tip>
    Se `OLLAMA_API_KEY` estiver definida, você pode omitir `apiKey` na entrada do provedor e o OpenClaw a preencherá para verificações de disponibilidade.
    </Tip>

  </Tab>

  <Tab title="Explícita (modelos manuais)">
    Use configuração explícita quando quiser uma configuração hospedada na nuvem, o Ollama estiver em outro host/porta, você quiser forçar janelas de contexto ou listas de modelos específicas, ou quiser definições de modelos totalmente manuais.

    ```json5
    {
      models: {
        providers: {
          ollama: {
            baseUrl: "https://ollama.com",
            apiKey: "OLLAMA_API_KEY",
            api: "ollama",
            models: [
              {
                id: "kimi-k2.5:cloud",
                name: "kimi-k2.5:cloud",
                reasoning: false,
                input: ["text", "image"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 128000,
                maxTokens: 8192
              }
            ]
          }
        }
      }
    }
    ```

  </Tab>

  <Tab title="URL base personalizada">
    Se o Ollama estiver em execução em outro host ou porta (a configuração explícita desativa a descoberta automática, então defina os modelos manualmente):

    ```json5
    {
      models: {
        providers: {
          ollama: {
            apiKey: "ollama-local",
            baseUrl: "http://ollama-host:11434", // Sem /v1 - use a URL nativa da API do Ollama
            api: "ollama", // Defina explicitamente para garantir o comportamento nativo de chamada de ferramentas
          },
        },
      },
    }
    ```

    <Warning>
    Não adicione `/v1` à URL. O caminho `/v1` usa o modo compatível com OpenAI, no qual a chamada de ferramentas não é confiável. Use a URL base do Ollama sem sufixo de caminho.
    </Warning>

  </Tab>
</Tabs>

### Seleção de modelo

Depois de configurados, todos os seus modelos Ollama ficam disponíveis:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "ollama/gpt-oss:20b",
        fallbacks: ["ollama/llama3.3", "ollama/qwen2.5-coder:32b"],
      },
    },
  },
}
```

## Ollama Web Search

O OpenClaw oferece suporte ao **Ollama Web Search** como um provedor `web_search` incluído.

| Propriedade | Detalhe                                                                                                            |
| ----------- | ------------------------------------------------------------------------------------------------------------------ |
| Host        | Usa o host Ollama configurado (`models.providers.ollama.baseUrl` quando definido, caso contrário `http://127.0.0.1:11434`) |
| Auth        | Sem chave                                                                                                          |
| Requisito   | O Ollama deve estar em execução e autenticado com `ollama signin`                                                 |

Escolha **Ollama Web Search** durante `openclaw onboard` ou `openclaw configure --section web`, ou defina:

```json5
{
  tools: {
    web: {
      search: {
        provider: "ollama",
      },
    },
  },
}
```

<Note>
Para detalhes completos sobre configuração e comportamento, consulte [Ollama Web Search](/pt-BR/tools/ollama-search).
</Note>

## Configuração avançada

<AccordionGroup>
  <Accordion title="Modo legado compatível com OpenAI">
    <Warning>
    **A chamada de ferramentas não é confiável no modo compatível com OpenAI.** Use esse modo apenas se você precisar do formato OpenAI para um proxy e não depender do comportamento nativo de chamada de ferramentas.
    </Warning>

    Se você precisar usar o endpoint compatível com OpenAI em vez disso (por exemplo, atrás de um proxy que só oferece suporte ao formato OpenAI), defina `api: "openai-completions"` explicitamente:

    ```json5
    {
      models: {
        providers: {
          ollama: {
            baseUrl: "http://ollama-host:11434/v1",
            api: "openai-completions",
            injectNumCtxForOpenAICompat: true, // padrão: true
            apiKey: "ollama-local",
            models: [...]
          }
        }
      }
    }
    ```

    Esse modo pode não oferecer suporte a streaming e chamada de ferramentas simultaneamente. Talvez seja necessário desativar o streaming com `params: { streaming: false }` na configuração do modelo.

    Quando `api: "openai-completions"` é usado com o Ollama, o OpenClaw injeta `options.num_ctx` por padrão para que o Ollama não recue silenciosamente para uma janela de contexto de 4096. Se seu proxy/upstream rejeitar campos `options` desconhecidos, desative esse comportamento:

    ```json5
    {
      models: {
        providers: {
          ollama: {
            baseUrl: "http://ollama-host:11434/v1",
            api: "openai-completions",
            injectNumCtxForOpenAICompat: false,
            apiKey: "ollama-local",
            models: [...]
          }
        }
      }
    }
    ```

  </Accordion>

  <Accordion title="Janelas de contexto">
    Para modelos descobertos automaticamente, o OpenClaw usa a janela de contexto reportada pelo Ollama quando disponível; caso contrário, ele recorre à janela de contexto padrão do Ollama usada pelo OpenClaw.

    Você pode sobrescrever `contextWindow` e `maxTokens` na configuração explícita do provedor:

    ```json5
    {
      models: {
        providers: {
          ollama: {
            models: [
              {
                id: "llama3.3",
                contextWindow: 131072,
                maxTokens: 65536,
              }
            ]
          }
        }
      }
    }
    ```

  </Accordion>

  <Accordion title="Modelos de raciocínio">
    O OpenClaw trata modelos com nomes como `deepseek-r1`, `reasoning` ou `think` como compatíveis com raciocínio por padrão.

    ```bash
    ollama pull deepseek-r1:32b
    ```

    Nenhuma configuração adicional é necessária -- o OpenClaw os marca automaticamente.

  </Accordion>

  <Accordion title="Custos de modelo">
    O Ollama é gratuito e é executado localmente, então todos os custos de modelo são definidos como $0. Isso se aplica tanto a modelos descobertos automaticamente quanto a modelos definidos manualmente.
  </Accordion>

  <Accordion title="Embeddings de memória">
    O Plugin Ollama incluído registra um provedor de embedding de memória para
    [busca de memória](/pt-BR/concepts/memory). Ele usa a URL base do Ollama
    configurada e a chave de API.

    | Propriedade   | Valor               |
    | ------------- | ------------------- |
    | Modelo padrão | `nomic-embed-text`  |
    | Pull automático     | Sim — o modelo de embedding é obtido automaticamente se não estiver presente localmente |

    Para selecionar o Ollama como provedor de embedding da busca de memória:

    ```json5
    {
      agents: {
        defaults: {
          memorySearch: { provider: "ollama" },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Configuração de streaming">
    A integração do Ollama no OpenClaw usa a **API nativa do Ollama** (`/api/chat`) por padrão, que oferece suporte completo a streaming e chamada de ferramentas simultaneamente. Nenhuma configuração especial é necessária.

    <Tip>
    Se você precisar usar o endpoint compatível com OpenAI, consulte a seção "Modo legado compatível com OpenAI" acima. Streaming e chamada de ferramentas podem não funcionar simultaneamente nesse modo.
    </Tip>

  </Accordion>
</AccordionGroup>

## Solução de problemas

<AccordionGroup>
  <Accordion title="Ollama não detectado">
    Certifique-se de que o Ollama está em execução, que você definiu `OLLAMA_API_KEY` (ou um perfil de autenticação) e que você **não** definiu uma entrada explícita `models.providers.ollama`:

    ```bash
    ollama serve
    ```

    Verifique se a API está acessível:

    ```bash
    curl http://localhost:11434/api/tags
    ```

  </Accordion>

  <Accordion title="Nenhum modelo disponível">
    Se o seu modelo não estiver listado, faça `pull` do modelo localmente ou defina-o explicitamente em `models.providers.ollama`.

    ```bash
    ollama list  # Veja o que está instalado
    ollama pull gemma4
    ollama pull gpt-oss:20b
    ollama pull llama3.3     # Ou outro modelo
    ```

  </Accordion>

  <Accordion title="Conexão recusada">
    Verifique se o Ollama está em execução na porta correta:

    ```bash
    # Verifique se o Ollama está em execução
    ps aux | grep ollama

    # Ou reinicie o Ollama
    ollama serve
    ```

  </Accordion>
</AccordionGroup>

<Note>
Mais ajuda: [Solução de problemas](/pt-BR/help/troubleshooting) e [Perguntas frequentes](/pt-BR/help/faq).
</Note>

## Relacionado

<CardGroup cols={2}>
  <Card title="Provedores de modelo" href="/pt-BR/concepts/model-providers" icon="layers">
    Visão geral de todos os provedores, refs de modelo e comportamento de failover.
  </Card>
  <Card title="Seleção de modelo" href="/pt-BR/concepts/models" icon="brain">
    Como escolher e configurar modelos.
  </Card>
  <Card title="Ollama Web Search" href="/pt-BR/tools/ollama-search" icon="magnifying-glass">
    Detalhes completos de configuração e comportamento para busca na web com tecnologia Ollama.
  </Card>
  <Card title="Configuração" href="/pt-BR/gateway/configuration" icon="gear">
    Referência completa de configuração.
  </Card>
</CardGroup>
