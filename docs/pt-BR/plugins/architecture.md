---
read_when:
    - Criando ou depurando plugins nativos do OpenClaw
    - Entender o modelo de capacidades do plugin ou os limites de propriedade
    - Trabalhar no pipeline de carregamento ou no registro de plugins
    - Implementar hooks de runtime de provedores ou plugins de canal
sidebarTitle: Internals
summary: 'Internos de plugins: modelo de capacidades, propriedade, contratos, pipeline de carregamento e auxiliares de runtime'
title: Internos de plugins
x-i18n:
    generated_at: "2026-04-12T05:33:13Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6165a9da8b40de3bb7334fcb16023da5515deb83c4897ca1df1726f4a97db9e0
    source_path: plugins/architecture.md
    workflow: 15
---

# Internos de plugins

<Info>
  Esta é a **referência profunda de arquitetura**. Para guias práticos, consulte:
  - [Instalar e usar plugins](/pt-BR/tools/plugin) — guia do usuário
  - [Primeiros passos](/pt-BR/plugins/building-plugins) — primeiro tutorial de plugin
  - [Plugins de canal](/pt-BR/plugins/sdk-channel-plugins) — crie um canal de mensagens
  - [Plugins de provedor](/pt-BR/plugins/sdk-provider-plugins) — crie um provedor de modelos
  - [Visão geral do SDK](/pt-BR/plugins/sdk-overview) — mapa de importação e API de registro
</Info>

Esta página cobre a arquitetura interna do sistema de plugins do OpenClaw.

## Modelo público de capacidades

Capacidades são o modelo público de **plugin nativo** dentro do OpenClaw. Todo
plugin nativo do OpenClaw registra uma ou mais capacidades:

| Capacidade             | Método de registro                              | Plugins de exemplo                  |
| ---------------------- | ----------------------------------------------- | ----------------------------------- |
| Inferência de texto    | `api.registerProvider(...)`                     | `openai`, `anthropic`               |
| Backend de inferência da CLI | `api.registerCliBackend(...)`             | `openai`, `anthropic`               |
| Fala                   | `api.registerSpeechProvider(...)`               | `elevenlabs`, `microsoft`           |
| Transcrição em tempo real | `api.registerRealtimeTranscriptionProvider(...)` | `openai`                        |
| Voz em tempo real      | `api.registerRealtimeVoiceProvider(...)`        | `openai`                            |
| Entendimento de mídia  | `api.registerMediaUnderstandingProvider(...)`   | `openai`, `google`                  |
| Geração de imagens     | `api.registerImageGenerationProvider(...)`      | `openai`, `google`, `fal`, `minimax` |
| Geração de música      | `api.registerMusicGenerationProvider(...)`      | `google`, `minimax`                 |
| Geração de vídeo       | `api.registerVideoGenerationProvider(...)`      | `qwen`                              |
| Busca na web           | `api.registerWebFetchProvider(...)`             | `firecrawl`                         |
| Pesquisa na web        | `api.registerWebSearchProvider(...)`            | `google`                            |
| Canal / mensagens      | `api.registerChannel(...)`                      | `msteams`, `matrix`                 |

Um plugin que registra zero capacidades, mas fornece hooks, ferramentas ou
serviços, é um plugin **legado apenas com hooks**. Esse padrão ainda é
totalmente suportado.

### Posição de compatibilidade externa

O modelo de capacidades foi incorporado ao core e é usado hoje por plugins
nativos/inclusos, mas a compatibilidade de plugins externos ainda precisa de um
critério mais rigoroso do que "está exportado, portanto está congelado".

Orientação atual:

- **plugins externos existentes:** mantenha integrações baseadas em hooks funcionando; trate
  isso como a base de compatibilidade
- **novos plugins nativos/inclusos:** prefira registro explícito de capacidades em vez de
  acessos específicos de fornecedor ou novos designs apenas com hooks
- **plugins externos adotando registro de capacidades:** permitido, mas trate as
  superfícies auxiliares específicas de capacidade como evolutivas, a menos que a documentação
  marque explicitamente um contrato como estável

Regra prática:

- APIs de registro de capacidades são a direção pretendida
- hooks legados continuam sendo o caminho mais seguro, sem quebras, para plugins externos durante
  a transição
- nem todos os subcaminhos auxiliares exportados são equivalentes; prefira o contrato
  estreito documentado, não exports auxiliares incidentais

### Formatos de plugin

O OpenClaw classifica cada plugin carregado em um formato com base no seu
comportamento real de registro (não apenas em metadados estáticos):

- **plain-capability** -- registra exatamente um tipo de capacidade (por exemplo, um
  plugin somente de provedor como `mistral`)
- **hybrid-capability** -- registra vários tipos de capacidade (por exemplo,
  `openai` é responsável por inferência de texto, fala, entendimento de mídia e geração
  de imagens)
- **hook-only** -- registra apenas hooks (tipados ou personalizados), sem
  capacidades, ferramentas, comandos ou serviços
- **non-capability** -- registra ferramentas, comandos, serviços ou rotas, mas sem
  capacidades

Use `openclaw plugins inspect <id>` para ver o formato de um plugin e o detalhamento
das capacidades. Consulte [referência da CLI](/cli/plugins#inspect) para mais detalhes.

### Hooks legados

O hook `before_agent_start` continua suportado como caminho de compatibilidade para
plugins apenas com hooks. Plugins legados do mundo real ainda dependem dele.

Direção:

- mantenha-o funcionando
- documente-o como legado
- prefira `before_model_resolve` para trabalho de substituição de modelo/provedor
- prefira `before_prompt_build` para trabalho de mutação de prompt
- remova-o apenas depois que o uso real diminuir e a cobertura de fixtures comprovar a segurança da migração

### Sinais de compatibilidade

Quando você executa `openclaw doctor` ou `openclaw plugins inspect <id>`, pode ver
um destes rótulos:

| Sinal                     | Significado                                                   |
| ------------------------- | ------------------------------------------------------------- |
| **config valid**          | A configuração é analisada corretamente e os plugins são resolvidos |
| **compatibility advisory** | O plugin usa um padrão suportado, mas mais antigo (por exemplo, `hook-only`) |
| **legacy warning**        | O plugin usa `before_agent_start`, que está obsoleto         |
| **hard error**            | A configuração é inválida ou o plugin falhou ao carregar     |

Nem `hook-only` nem `before_agent_start` vão quebrar seu plugin hoje --
`hook-only` é apenas informativo, e `before_agent_start` só gera um aviso. Esses
sinais também aparecem em `openclaw status --all` e `openclaw plugins doctor`.

## Visão geral da arquitetura

O sistema de plugins do OpenClaw tem quatro camadas:

1. **Manifesto + descoberta**
   O OpenClaw encontra plugins candidatos em caminhos configurados, raízes de workspace,
   raízes globais de extensões e extensões incluídas. A descoberta lê primeiro
   manifestos nativos `openclaw.plugin.json` e manifestos de bundle suportados.
2. **Habilitação + validação**
   O core decide se um plugin descoberto está habilitado, desabilitado, bloqueado ou
   selecionado para um slot exclusivo, como memória.
3. **Carregamento em runtime**
   Plugins nativos do OpenClaw são carregados no processo via jiti e registram
   capacidades em um registro central. Bundles compatíveis são normalizados em
   registros do registro sem importar código de runtime.
4. **Consumo de superfície**
   O restante do OpenClaw lê o registro para expor ferramentas, canais, configuração
   de provedores, hooks, rotas HTTP, comandos da CLI e serviços.

Especificamente para a CLI de plugins, a descoberta de comandos raiz é dividida em duas fases:

- metadados em tempo de análise vêm de `registerCli(..., { descriptors: [...] })`
- o módulo real da CLI do plugin pode permanecer lazy e ser registrado na primeira invocação

Isso mantém o código de CLI pertencente ao plugin dentro do plugin, ao mesmo tempo que permite ao OpenClaw
reservar nomes de comandos raiz antes da análise.

O limite de design importante:

- descoberta + validação de configuração devem funcionar a partir de **metadados de manifesto/schema**
  sem executar código do plugin
- o comportamento nativo em runtime vem do caminho `register(api)` do módulo do plugin

Essa separação permite que o OpenClaw valide configuração, explique plugins ausentes/desabilitados e
construa dicas de UI/schema antes que todo o runtime esteja ativo.

### Plugins de canal e a ferramenta compartilhada de mensagem

Plugins de canal não precisam registrar uma ferramenta separada de enviar/editar/reagir para
ações normais de chat. O OpenClaw mantém uma ferramenta `message` compartilhada no core, e
os plugins de canal são responsáveis pela descoberta e execução específicas do canal por trás dela.

O limite atual é:

- o core é responsável pelo host da ferramenta `message` compartilhada, wiring de prompt, controle de sessão/thread
  e despacho de execução
- plugins de canal são responsáveis pela descoberta de ações com escopo, descoberta de capacidades e quaisquer
  fragmentos de schema específicos do canal
- plugins de canal são responsáveis pela gramática de conversa de sessão específica do provedor, como
  IDs de conversa codificam IDs de thread ou herdam de conversas pai
- plugins de canal executam a ação final por meio de seu adaptador de ações

Para plugins de canal, a superfície do SDK é
`ChannelMessageActionAdapter.describeMessageTool(...)`. Essa chamada unificada de descoberta
permite que um plugin retorne suas ações visíveis, capacidades e contribuições de schema
juntas, para que essas partes não se desalinhem.

O core passa o escopo de runtime para essa etapa de descoberta. Campos importantes incluem:

- `accountId`
- `currentChannelId`
- `currentThreadTs`
- `currentMessageId`
- `sessionKey`
- `sessionId`
- `agentId`
- `requesterSenderId` de entrada confiável

Isso é importante para plugins sensíveis ao contexto. Um canal pode ocultar ou expor
ações de mensagem com base na conta ativa, sala/thread/mensagem atual, ou
identidade confiável do solicitante, sem codificar ramificações específicas do canal
na ferramenta `message` do core.

É por isso que mudanças de roteamento do runner incorporado ainda são trabalho de plugin: o runner é
responsável por encaminhar a identidade atual do chat/sessão para o limite de descoberta do plugin
para que a ferramenta `message` compartilhada exponha a superfície pertencente ao canal correta
para o turno atual.

Para auxiliares de execução pertencentes ao canal, plugins incluídos devem manter o runtime de execução
dentro de seus próprios módulos de extensão. O core não é mais responsável pelos runtimes de ação de mensagem
de Discord, Slack, Telegram ou WhatsApp em `src/agents/tools`.
Não publicamos subcaminhos separados `plugin-sdk/*-action-runtime`, e plugins incluídos
devem importar seu próprio código de runtime local diretamente de seus
módulos pertencentes à extensão.

O mesmo limite se aplica a seams do SDK nomeados por provedor em geral: o core não
deve importar barris de conveniência específicos de canal para extensões como Slack, Discord, Signal,
WhatsApp ou semelhantes. Se o core precisa de um comportamento, deve consumir o próprio barril
`api.ts` / `runtime-api.ts` do plugin incluído ou promover a necessidade
a uma capacidade genérica e estreita no SDK compartilhado.

Especificamente para enquetes, existem dois caminhos de execução:

- `outbound.sendPoll` é a base compartilhada para canais compatíveis com o modelo comum de
  enquete
- `actions.handleAction("poll")` é o caminho preferido para semântica de enquete específica do canal
  ou parâmetros extras de enquete

O core agora adia a análise compartilhada de enquetes até que o despacho da enquete do plugin recuse
a ação, para que manipuladores de enquete pertencentes ao plugin possam aceitar campos de enquete específicos do canal
sem serem bloqueados primeiro pelo analisador genérico de enquetes.

Consulte [Pipeline de carregamento](#load-pipeline) para a sequência completa de inicialização.

## Modelo de propriedade de capacidades

O OpenClaw trata um plugin nativo como o limite de propriedade para uma **empresa** ou um
**recurso**, não como uma coleção de integrações não relacionadas.

Isso significa:

- um plugin de empresa normalmente deve ser responsável por todas as superfícies do OpenClaw
  dessa empresa
- um plugin de recurso normalmente deve ser responsável por toda a superfície do recurso que introduz
- canais devem consumir capacidades compartilhadas do core em vez de reimplementar
  comportamento de provedor de forma ad hoc

Exemplos:

- o plugin incluído `openai` é responsável pelo comportamento de provedor de modelos da OpenAI e pelo comportamento de
  fala + voz em tempo real + entendimento de mídia + geração de imagens da OpenAI
- o plugin incluído `elevenlabs` é responsável pelo comportamento de fala da ElevenLabs
- o plugin incluído `microsoft` é responsável pelo comportamento de fala da Microsoft
- o plugin incluído `google` é responsável pelo comportamento de provedor de modelos do Google, além do comportamento de
  entendimento de mídia + geração de imagens + pesquisa na web do Google
- o plugin incluído `firecrawl` é responsável pelo comportamento de busca na web do Firecrawl
- os plugins incluídos `minimax`, `mistral`, `moonshot` e `zai` são responsáveis por seus
  backends de entendimento de mídia
- o plugin incluído `qwen` é responsável pelo comportamento de provedor de texto do Qwen, além do
  comportamento de entendimento de mídia e geração de vídeo
- o plugin `voice-call` é um plugin de recurso: ele é responsável por transporte de chamada, ferramentas,
  CLI, rotas e bridging de fluxo de mídia do Twilio, mas consome capacidades compartilhadas de fala
  mais transcrição em tempo real e voz em tempo real em vez de importar plugins de fornecedor diretamente

O estado final pretendido é:

- a OpenAI fica em um único plugin, mesmo que abranja modelos de texto, fala, imagens e
  vídeo no futuro
- outro fornecedor pode fazer o mesmo para sua própria área de atuação
- canais não se importam com qual plugin de fornecedor é responsável pelo provedor; eles consomem o
  contrato de capacidade compartilhada exposto pelo core

Esta é a distinção principal:

- **plugin** = limite de propriedade
- **capability** = contrato do core que vários plugins podem implementar ou consumir

Então, se o OpenClaw adicionar um novo domínio, como vídeo, a primeira pergunta não é
"qual provedor deve codificar o tratamento de vídeo?" A primeira pergunta é "qual é
o contrato de capacidade de vídeo do core?" Assim que esse contrato existir, plugins de fornecedores
poderão se registrar nele e plugins de canal/recurso poderão consumi-lo.

Se a capacidade ainda não existir, a ação correta geralmente é:

1. definir a capacidade ausente no core
2. expô-la por meio da API/runtime de plugin de forma tipada
3. conectar canais/recursos a essa capacidade
4. permitir que plugins de fornecedores registrem implementações

Isso mantém a propriedade explícita e evita comportamento no core que dependa de um
único fornecedor ou de um caminho de código específico de plugin e pontual.

### Camadas de capacidade

Use este modelo mental ao decidir onde o código deve ficar:

- **camada de capacidade do core**: orquestração compartilhada, política, fallback, regras de
  mesclagem de configuração, semântica de entrega e contratos tipados
- **camada de plugin de fornecedor**: APIs específicas do fornecedor, autenticação, catálogos de modelos, síntese
  de fala, geração de imagens, futuros backends de vídeo, endpoints de uso
- **camada de plugin de canal/recurso**: integração com Slack/Discord/voice-call/etc.
  que consome capacidades do core e as apresenta em uma superfície

Por exemplo, TTS segue este formato:

- o core é responsável pela política de TTS no momento da resposta, ordem de fallback, preferências e entrega por canal
- `openai`, `elevenlabs` e `microsoft` são responsáveis pelas implementações de síntese
- `voice-call` consome o auxiliar de runtime de TTS de telefonia

Esse mesmo padrão deve ser preferido para capacidades futuras.

### Exemplo de plugin de empresa com múltiplas capacidades

Um plugin de empresa deve parecer coeso por fora. Se o OpenClaw tiver contratos compartilhados
para modelos, fala, transcrição em tempo real, voz em tempo real, entendimento de mídia,
geração de imagens, geração de vídeo, busca na web e pesquisa na web,
um fornecedor pode ser responsável por todas as suas superfícies em um só lugar:

```ts
import type { OpenClawPluginDefinition } from "openclaw/plugin-sdk/plugin-entry";
import {
  describeImageWithModel,
  transcribeOpenAiCompatibleAudio,
} from "openclaw/plugin-sdk/media-understanding";

const plugin: OpenClawPluginDefinition = {
  id: "exampleai",
  name: "ExampleAI",
  register(api) {
    api.registerProvider({
      id: "exampleai",
      // auth/model catalog/runtime hooks
    });

    api.registerSpeechProvider({
      id: "exampleai",
      // vendor speech config — implement the SpeechProviderPlugin interface directly
    });

    api.registerMediaUnderstandingProvider({
      id: "exampleai",
      capabilities: ["image", "audio", "video"],
      async describeImage(req) {
        return describeImageWithModel({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
      async transcribeAudio(req) {
        return transcribeOpenAiCompatibleAudio({
          provider: "exampleai",
          model: req.model,
          input: req.input,
        });
      },
    });

    api.registerWebSearchProvider(
      createPluginBackedWebSearchProvider({
        id: "exampleai-search",
        // credential + fetch logic
      }),
    );
  },
};

export default plugin;
```

O que importa não são os nomes exatos dos auxiliares. O que importa é o formato:

- um plugin é responsável pela superfície do fornecedor
- o core continua sendo responsável pelos contratos de capacidade
- canais e plugins de recurso consomem auxiliares `api.runtime.*`, não código do fornecedor
- testes de contrato podem afirmar que o plugin registrou as capacidades que
  afirma possuir

### Exemplo de capacidade: entendimento de vídeo

O OpenClaw já trata entendimento de imagem/áudio/vídeo como uma única
capacidade compartilhada. O mesmo modelo de propriedade se aplica aqui:

1. o core define o contrato de media-understanding
2. plugins de fornecedores registram `describeImage`, `transcribeAudio` e
   `describeVideo`, conforme aplicável
3. canais e plugins de recurso consomem o comportamento compartilhado do core em vez de
   se conectarem diretamente ao código do fornecedor

Isso evita incorporar ao core as suposições de vídeo de um único provedor. O plugin é responsável pela
superfície do fornecedor; o core é responsável pelo contrato de capacidade e pelo comportamento de fallback.

A geração de vídeo já usa essa mesma sequência: o core é responsável pelo contrato tipado de
capacidade e pelo auxiliar de runtime, e plugins de fornecedores registram
implementações `api.registerVideoGenerationProvider(...)` nele.

Precisa de um checklist concreto de rollout? Consulte
[Livro de receitas de capacidades](/pt-BR/plugins/architecture).

## Contratos e aplicação

A superfície da API de plugin é intencionalmente tipada e centralizada em
`OpenClawPluginApi`. Esse contrato define os pontos de registro suportados e
os auxiliares de runtime nos quais um plugin pode confiar.

Por que isso importa:

- autores de plugins obtêm um padrão interno estável
- o core pode rejeitar propriedade duplicada, como dois plugins registrando o mesmo
  ID de provedor
- a inicialização pode expor diagnósticos acionáveis para registros malformados
- testes de contrato podem aplicar a propriedade de plugins incluídos e evitar deriva silenciosa

Há duas camadas de aplicação:

1. **aplicação do registro em runtime**
   O registro de plugins valida os registros à medida que os plugins são carregados. Exemplos:
   IDs de provedor duplicados, IDs de provedor de fala duplicados e registros
   malformados produzem diagnósticos de plugin em vez de comportamento indefinido.
2. **testes de contrato**
   Plugins incluídos são capturados em registros de contrato durante execuções de teste, para que o
   OpenClaw possa afirmar a propriedade explicitamente. Hoje isso é usado para
   provedores de modelos, provedores de fala, provedores de pesquisa na web e propriedade de registro incluída.

O efeito prático é que o OpenClaw sabe, antecipadamente, qual plugin é responsável por qual
superfície. Isso permite que o core e os canais componham sem atrito porque a propriedade é
declarada, tipada e testável, em vez de implícita.

### O que pertence a um contrato

Bons contratos de plugin são:

- tipados
- pequenos
- específicos por capacidade
- pertencentes ao core
- reutilizáveis por múltiplos plugins
- consumíveis por canais/recursos sem conhecimento do fornecedor

Maus contratos de plugin são:

- política específica de fornecedor oculta no core
- escapes pontuais de plugin que contornam o registro
- código de canal acessando diretamente uma implementação de fornecedor
- objetos de runtime ad hoc que não fazem parte de `OpenClawPluginApi` ou
  `api.runtime`

Em caso de dúvida, eleve o nível de abstração: defina primeiro a capacidade e depois
permita que os plugins se conectem a ela.

## Modelo de execução

Plugins nativos do OpenClaw são executados **no processo** com o Gateway. Eles não
são isolados em sandbox. Um plugin nativo carregado tem o mesmo limite de confiança no nível de processo que
o código do core.

Implicações:

- um plugin nativo pode registrar ferramentas, handlers de rede, hooks e serviços
- um bug em um plugin nativo pode travar ou desestabilizar o gateway
- um plugin nativo malicioso equivale a execução arbitrária de código dentro do
  processo do OpenClaw

Bundles compatíveis são mais seguros por padrão porque o OpenClaw atualmente os trata
como pacotes de metadados/conteúdo. Nas versões atuais, isso significa principalmente
Skills incluídas.

Use allowlists e caminhos explícitos de instalação/carregamento para plugins não incluídos. Trate
plugins de workspace como código de desenvolvimento, não como padrão de produção.

Para nomes de pacotes de workspace incluídos, mantenha o ID do plugin ancorado no nome npm:
`@openclaw/<id>` por padrão, ou um sufixo tipado aprovado, como
`-provider`, `-plugin`, `-speech`, `-sandbox` ou `-media-understanding`, quando
o pacote expõe intencionalmente uma função de plugin mais restrita.

Observação importante sobre confiança:

- `plugins.allow` confia em **IDs de plugin**, não na procedência da origem.
- Um plugin de workspace com o mesmo ID de um plugin incluído intencionalmente sombreia
  a cópia incluída quando esse plugin de workspace está habilitado/em allowlist.
- Isso é normal e útil para desenvolvimento local, testes de patch e hotfixes.

## Limite de exportação

O OpenClaw exporta capacidades, não conveniências de implementação.

Mantenha público o registro de capacidades. Remova exports auxiliares fora de contrato:

- subcaminhos auxiliares específicos de plugins incluídos
- subcaminhos de plumbing de runtime não destinados a serem API pública
- auxiliares de conveniência específicos de fornecedor
- auxiliares de configuração/onboarding que são detalhes de implementação

Alguns subcaminhos auxiliares de plugins incluídos ainda permanecem no mapa de exportação
gerado do SDK por compatibilidade e manutenção de plugins incluídos. Exemplos atuais incluem
`plugin-sdk/feishu`, `plugin-sdk/feishu-setup`, `plugin-sdk/zalo`,
`plugin-sdk/zalo-setup` e vários seams `plugin-sdk/matrix*`. Trate-os como
exports reservados de detalhe de implementação, não como o padrão de SDK recomendado para
novos plugins de terceiros.

## Pipeline de carregamento

Na inicialização, o OpenClaw faz aproximadamente isto:

1. descobre raízes de plugins candidatas
2. lê manifestos nativos ou de bundle compatível e metadados de pacote
3. rejeita candidatos inseguros
4. normaliza a configuração de plugins (`plugins.enabled`, `allow`, `deny`, `entries`,
   `slots`, `load.paths`)
5. decide a habilitação de cada candidato
6. carrega módulos nativos habilitados via jiti
7. chama hooks nativos `register(api)` (ou `activate(api)` — um alias legado) e coleta os registros no registro de plugins
8. expõe o registro para superfícies de comandos/runtime

<Note>
`activate` é um alias legado para `register` — o loader resolve o que estiver presente (`def.register ?? def.activate`) e o chama no mesmo ponto. Todos os plugins incluídos usam `register`; prefira `register` em novos plugins.
</Note>

As barreiras de segurança acontecem **antes** da execução em runtime. Candidatos são bloqueados
quando a entrada escapa da raiz do plugin, o caminho pode ser escrito por qualquer usuário ou a propriedade do caminho parece suspeita para plugins não incluídos.

### Comportamento orientado por manifesto

O manifesto é a fonte de verdade do plano de controle. O OpenClaw o usa para:

- identificar o plugin
- descobrir canais/Skills/schema de configuração declarados ou capacidades do bundle
- validar `plugins.entries.<id>.config`
- complementar rótulos/placeholders da UI de controle
- mostrar metadados de instalação/catálogo
- preservar descritores baratos de ativação e configuração sem carregar o runtime do plugin

Para plugins nativos, o módulo de runtime é a parte do plano de dados. Ele registra
comportamento real, como hooks, ferramentas, comandos ou fluxos de provedor.

Blocos opcionais `activation` e `setup` do manifesto permanecem no plano de controle.
Eles são descritores somente de metadados para planejamento de ativação e descoberta de configuração;
não substituem registro em runtime, `register(...)` ou `setupEntry`.

A descoberta de configuração agora prefere IDs pertencentes a descritores, como
`setup.providers` e `setup.cliBackends`, para restringir plugins candidatos antes de recorrer a
`setup-api` para plugins que ainda precisam de hooks de runtime em tempo de configuração. Se mais de
um plugin descoberto afirmar o mesmo ID normalizado de provedor de configuração ou backend de CLI, a busca de configuração recusa o proprietário ambíguo em vez de depender da ordem de descoberta.

### O que o loader armazena em cache

O OpenClaw mantém caches curtos no processo para:

- resultados de descoberta
- dados do registro de manifestos
- registros de plugins carregados

Esses caches reduzem picos de inicialização e sobrecarga de comandos repetidos. É seguro
pensar neles como caches de desempenho de curta duração, não como persistência.

Observação de desempenho:

- Defina `OPENCLAW_DISABLE_PLUGIN_DISCOVERY_CACHE=1` ou
  `OPENCLAW_DISABLE_PLUGIN_MANIFEST_CACHE=1` para desabilitar esses caches.
- Ajuste as janelas de cache com `OPENCLAW_PLUGIN_DISCOVERY_CACHE_MS` e
  `OPENCLAW_PLUGIN_MANIFEST_CACHE_MS`.

## Modelo de registro

Plugins carregados não mutam diretamente globais aleatórios do core. Eles se registram em um
registro central de plugins.

O registro rastreia:

- registros de plugin (identidade, origem, procedência, status, diagnósticos)
- ferramentas
- hooks legados e hooks tipados
- canais
- provedores
- handlers RPC do gateway
- rotas HTTP
- registradores da CLI
- serviços em segundo plano
- comandos pertencentes a plugins

Os recursos do core então leem esse registro em vez de falar diretamente com módulos de plugin.
Isso mantém o carregamento unidirecional:

- módulo do plugin -> registro no registry
- runtime do core -> consumo do registry

Essa separação é importante para a manutenção. Significa que a maioria das superfícies do core
precisa de apenas um ponto de integração: "ler o registry", e não "tratar cada módulo de plugin
como caso especial".

## Callbacks de vínculo de conversa

Plugins que vinculam uma conversa podem reagir quando uma aprovação é resolvida.

Use `api.onConversationBindingResolved(...)` para receber um callback depois que uma solicitação de vínculo for aprovada ou negada:

```ts
export default {
  id: "my-plugin",
  register(api) {
    api.onConversationBindingResolved(async (event) => {
      if (event.status === "approved") {
        // A binding now exists for this plugin + conversation.
        console.log(event.binding?.conversationId);
        return;
      }

      // The request was denied; clear any local pending state.
      console.log(event.request.conversation.conversationId);
    });
  },
};
```

Campos do payload do callback:

- `status`: `"approved"` ou `"denied"`
- `decision`: `"allow-once"`, `"allow-always"` ou `"deny"`
- `binding`: o vínculo resolvido para solicitações aprovadas
- `request`: o resumo da solicitação original, dica de desvinculação, ID do remetente e
  metadados da conversa

Esse callback é apenas de notificação. Ele não muda quem tem permissão para vincular uma
conversa e é executado depois que o tratamento de aprovação do core termina.

## Hooks de runtime de provedor

Plugins de provedor agora têm duas camadas:

- metadados do manifesto: `providerAuthEnvVars` para busca barata de autenticação do provedor por env
  antes do carregamento em runtime, `providerAuthAliases` para variantes de provedor que compartilham
  autenticação, `channelEnvVars` para busca barata de env/configuração de canal antes do carregamento em runtime,
  além de `providerAuthChoices` para rótulos baratos de onboarding/escolha de autenticação e
  metadados de flags da CLI antes do carregamento em runtime
- hooks em tempo de configuração: `catalog` / legado `discovery` mais `applyConfigDefaults`
- hooks de runtime: `normalizeModelId`, `normalizeTransport`,
  `normalizeConfig`,
  `applyNativeStreamingUsageCompat`, `resolveConfigApiKey`,
  `resolveSyntheticAuth`, `resolveExternalAuthProfiles`,
  `shouldDeferSyntheticProfileAuth`,
  `resolveDynamicModel`, `prepareDynamicModel`, `normalizeResolvedModel`,
  `contributeResolvedModelCompat`, `capabilities`,
  `normalizeToolSchemas`, `inspectToolSchemas`,
  `resolveReasoningOutputMode`, `prepareExtraParams`, `createStreamFn`,
  `wrapStreamFn`, `resolveTransportTurnState`,
  `resolveWebSocketSessionPolicy`, `formatApiKey`, `refreshOAuth`,
  `buildAuthDoctorHint`, `matchesContextOverflowError`,
  `classifyFailoverReason`, `isCacheTtlEligible`,
  `buildMissingAuthMessage`, `suppressBuiltInModel`, `augmentModelCatalog`,
  `isBinaryThinking`, `supportsXHighThinking`,
  `resolveDefaultThinkingLevel`, `isModernModelRef`, `prepareRuntimeAuth`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `createEmbeddingProvider`,
  `buildReplayPolicy`,
  `sanitizeReplayHistory`, `validateReplayTurns`, `onModelSelected`

O OpenClaw continua sendo responsável pelo loop genérico do agente, failover, tratamento de transcrição e
política de ferramentas. Esses hooks são a superfície de extensão para comportamento específico de provedor sem
precisar de um transporte de inferência totalmente personalizado.

Use o `providerAuthEnvVars` do manifesto quando o provedor tiver credenciais baseadas em env
que caminhos genéricos de autenticação/status/seletor de modelo devam enxergar sem carregar o runtime do plugin.
Use `providerAuthAliases` do manifesto quando um ID de provedor precisar reutilizar as variáveis de ambiente,
perfis de autenticação, autenticação baseada em configuração e opção de onboarding de chave de API de outro ID de provedor.
Use `providerAuthChoices` do manifesto quando as superfícies da CLI de onboarding/escolha de autenticação
precisarem conhecer o ID de escolha do provedor, rótulos de grupo e wiring simples de autenticação com uma única flag
sem carregar o runtime do provedor. Mantenha `envVars` no runtime do provedor para dicas voltadas ao operador, como
rótulos de onboarding ou variáveis de configuração de client-id/client-secret de OAuth.

Use `channelEnvVars` do manifesto quando um canal tiver autenticação ou configuração orientada por env que
fallback genérico de env do shell, verificações de config/status ou prompts de configuração devam enxergar
sem carregar o runtime do canal.

### Ordem e uso dos hooks

Para plugins de modelo/provedor, o OpenClaw chama hooks aproximadamente nesta ordem.
A coluna "Quando usar" é o guia rápido de decisão.

| #   | Hook                              | O que faz                                                                                                      | Quando usar                                                                                                                                  |
| --- | --------------------------------- | -------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| 1   | `catalog`                         | Publica a configuração do provedor em `models.providers` durante a geração de `models.json`                  | O provedor é responsável por um catálogo ou por padrões de URL base                                                                          |
| 2   | `applyConfigDefaults`             | Aplica padrões globais de configuração pertencentes ao provedor durante a materialização da configuração      | Os padrões dependem do modo de autenticação, env ou da semântica da família de modelos do provedor                                          |
| --  | _(built-in model lookup)_         | O OpenClaw tenta primeiro o caminho normal de registry/catálogo                                               | _(não é um hook de plugin)_                                                                                                                  |
| 3   | `normalizeModelId`                | Normaliza aliases legados ou de preview de IDs de modelo antes da busca                                      | O provedor é responsável pela limpeza de aliases antes da resolução canônica do modelo                                                       |
| 4   | `normalizeTransport`              | Normaliza `api` / `baseUrl` da família do provedor antes da montagem genérica do modelo                      | O provedor é responsável pela limpeza do transporte para IDs de provedor personalizados na mesma família de transporte                      |
| 5   | `normalizeConfig`                 | Normaliza `models.providers.<id>` antes da resolução em runtime/do provedor                                  | O provedor precisa de limpeza de configuração que deve ficar junto com o plugin; auxiliares incluídos da família Google também dão suporte a entradas de configuração do Google compatíveis |
| 6   | `applyNativeStreamingUsageCompat` | Aplica reescritas de compatibilidade de uso de streaming nativo a provedores de configuração                 | O provedor precisa de correções de metadados de uso de streaming nativo orientadas por endpoint                                              |
| 7   | `resolveConfigApiKey`             | Resolve autenticação por marcador de env para provedores de configuração antes do carregamento da autenticação em runtime | O provedor tem resolução de chave de API por marcador de env pertencente ao provedor; `amazon-bedrock` também tem aqui um resolvedor integrado de marcador de env da AWS |
| 8   | `resolveSyntheticAuth`            | Expõe autenticação local/self-hosted ou baseada em configuração sem persistir texto simples                  | O provedor pode operar com um marcador de credencial sintética/local                                                                         |
| 9   | `resolveExternalAuthProfiles`     | Sobrepõe perfis externos de autenticação pertencentes ao provedor; o `persistence` padrão é `runtime-only` para credenciais pertencentes à CLI/ao app | O provedor reutiliza credenciais externas de autenticação sem persistir tokens de refresh copiados                                           |
| 10  | `shouldDeferSyntheticProfileAuth` | Rebaixa placeholders armazenados de perfis sintéticos abaixo da autenticação baseada em env/configuração     | O provedor armazena perfis placeholder sintéticos que não devem ter precedência                                                             |
| 11  | `resolveDynamicModel`             | Fallback síncrono para IDs de modelo pertencentes ao provedor que ainda não estão no registry local         | O provedor aceita IDs arbitrários de modelos upstream                                                                                        |
| 12  | `prepareDynamicModel`             | Aquecimento assíncrono; depois, `resolveDynamicModel` é executado novamente                                  | O provedor precisa de metadados de rede antes de resolver IDs desconhecidos                                                                 |
| 13  | `normalizeResolvedModel`          | Reescrita final antes de o runner incorporado usar o modelo resolvido                                        | O provedor precisa de reescritas de transporte, mas ainda usa um transporte do core                                                         |
| 14  | `contributeResolvedModelCompat`   | Contribui com flags de compatibilidade para modelos de fornecedor por trás de outro transporte compatível    | O provedor reconhece seus próprios modelos em transportes proxy sem assumir o controle do provedor                                          |
| 15  | `capabilities`                    | Metadados de transcrição/ferramentas pertencentes ao provedor usados pela lógica compartilhada do core      | O provedor precisa de peculiaridades de transcrição/família de provedor                                                                     |
| 16  | `normalizeToolSchemas`            | Normaliza schemas de ferramentas antes de o runner incorporado vê-los                                        | O provedor precisa de limpeza de schema da família de transporte                                                                             |
| 17  | `inspectToolSchemas`              | Expõe diagnósticos de schema pertencentes ao provedor após a normalização                                    | O provedor quer avisos de palavras-chave sem ensinar regras específicas do provedor ao core                                                 |
| 18  | `resolveReasoningOutputMode`      | Seleciona o contrato de saída de raciocínio nativo versus marcado                                            | O provedor precisa de saída final/de raciocínio marcada em vez de campos nativos                                                            |
| 19  | `prepareExtraParams`              | Normalização de parâmetros de requisição antes de wrappers genéricos de opções de stream                    | O provedor precisa de parâmetros padrão de requisição ou limpeza de parâmetros por provedor                                                 |
| 20  | `createStreamFn`                  | Substitui totalmente o caminho normal de stream por um transporte personalizado                              | O provedor precisa de um protocolo de transporte personalizado, e não apenas de um wrapper                                                  |
| 21  | `wrapStreamFn`                    | Wrapper de stream após a aplicação dos wrappers genéricos                                                    | O provedor precisa de wrappers de compatibilidade para cabeçalhos/corpo/modelo de requisição sem um transporte personalizado               |
| 22  | `resolveTransportTurnState`       | Anexa cabeçalhos ou metadados nativos por turno do transporte                                                | O provedor quer que transportes genéricos enviem identidade de turno nativa do provedor                                                    |
| 23  | `resolveWebSocketSessionPolicy`   | Anexa cabeçalhos nativos de WebSocket ou política de resfriamento de sessão                                  | O provedor quer que transportes WS genéricos ajustem cabeçalhos de sessão ou política de fallback                                          |
| 24  | `formatApiKey`                    | Formatador de perfil de autenticação: o perfil armazenado se torna a string `apiKey` em runtime             | O provedor armazena metadados extras de autenticação e precisa de um formato personalizado de token em runtime                             |
| 25  | `refreshOAuth`                    | Substituição da atualização de OAuth para endpoints personalizados de refresh ou política de falha na atualização | O provedor não se encaixa nos atualizadores compartilhados de `pi-ai`                                                                       |
| 26  | `buildAuthDoctorHint`             | Dica de reparo anexada quando a atualização de OAuth falha                                                   | O provedor precisa de orientação de reparo de autenticação pertencente ao provedor após falha na atualização                               |
| 27  | `matchesContextOverflowError`     | Correspondência de overflow de janela de contexto pertencente ao provedor                                    | O provedor tem erros brutos de overflow que heurísticas genéricas não detectariam                                                          |
| 28  | `classifyFailoverReason`          | Classificação do motivo de failover pertencente ao provedor                                                  | O provedor pode mapear erros brutos de API/transporte para limite de taxa/sobrecarga/etc.                                                  |
| 29  | `isCacheTtlEligible`              | Política de cache de prompt para provedores proxy/backhaul                                                   | O provedor precisa de controle de TTL de cache específico de proxy                                                                          |
| 30  | `buildMissingAuthMessage`         | Substituição para a mensagem genérica de recuperação de autenticação ausente                                 | O provedor precisa de uma dica de recuperação de autenticação ausente específica do provedor                                                |
| 31  | `suppressBuiltInModel`            | Supressão de modelo upstream desatualizado mais dica opcional de erro voltada ao usuário                     | O provedor precisa ocultar linhas upstream desatualizadas ou substituí-las por uma dica do fornecedor                                      |
| 32  | `augmentModelCatalog`             | Linhas sintéticas/finais de catálogo anexadas após a descoberta                                              | O provedor precisa de linhas sintéticas de compatibilidade futura em `models list` e seletores                                             |
| 33  | `isBinaryThinking`                | Alternância de raciocínio ligado/desligado para provedores de raciocínio binário                            | O provedor expõe apenas raciocínio binário ligado/desligado                                                                                 |
| 34  | `supportsXHighThinking`           | Suporte a raciocínio `xhigh` para modelos selecionados                                                       | O provedor quer `xhigh` apenas em um subconjunto de modelos                                                                                 |
| 35  | `resolveDefaultThinkingLevel`     | Nível padrão de `/think` para uma família de modelos específica                                              | O provedor é responsável pela política padrão de `/think` para uma família de modelos                                                       |
| 36  | `isModernModelRef`                | Correspondência de modelo moderno para filtros de perfil ao vivo e seleção de smoke                          | O provedor é responsável pela correspondência de modelo preferido para testes ao vivo/smoke                                                |
| 37  | `prepareRuntimeAuth`              | Troca uma credencial configurada pelo token/chave real de runtime imediatamente antes da inferência         | O provedor precisa de uma troca de token ou de uma credencial de requisição de curta duração                                               |
| 38  | `resolveUsageAuth`                | Resolve credenciais de uso/faturamento para `/usage` e superfícies relacionadas de status                     | O provedor precisa de parsing personalizado de token de uso/cota ou de uma credencial de uso diferente                                     |
| 39  | `fetchUsageSnapshot`              | Busca e normaliza snapshots de uso/cota específicos do provedor após a resolução da autenticação              | O provedor precisa de um endpoint de uso específico do provedor ou de um parser de payload                                                 |
| 40  | `createEmbeddingProvider`         | Cria um adaptador de embeddings pertencente ao provedor para memória/pesquisa                                 | O comportamento de embeddings de memória pertence ao plugin do provedor                                                                     |
| 41  | `buildReplayPolicy`               | Retorna uma política de replay que controla o tratamento da transcrição para o provedor                       | O provedor precisa de uma política de transcrição personalizada (por exemplo, remoção de blocos de raciocínio)                            |
| 42  | `sanitizeReplayHistory`           | Reescreve o histórico de replay após a limpeza genérica da transcrição                                        | O provedor precisa de reescritas de replay específicas do provedor além dos auxiliares compartilhados de compactação                      |
| 43  | `validateReplayTurns`             | Validação final ou remodelagem dos turnos de replay antes do runner incorporado                               | O transporte do provedor precisa de validação mais rígida dos turnos após a sanitização genérica                                           |
| 44  | `onModelSelected`                 | Executa efeitos colaterais pós-seleção pertencentes ao provedor                                               | O provedor precisa de telemetria ou de estado pertencente ao provedor quando um modelo se torna ativo                                      |

`normalizeModelId`, `normalizeTransport` e `normalizeConfig` primeiro verificam o
plugin de provedor correspondente e depois passam pelos outros plugins de provedor capazes de usar hooks
até que um realmente altere o ID do modelo ou o transporte/configuração. Isso mantém
shims de alias/provedor compatível funcionando sem exigir que o chamador saiba qual
plugin incluído é responsável pela reescrita. Se nenhum hook de provedor reescrever uma entrada de configuração compatível da
família Google, o normalizador de configuração incluído do Google ainda aplica essa limpeza de compatibilidade.

Se o provedor precisar de um protocolo de comunicação totalmente personalizado ou de um executor de requisição personalizado,
essa é uma classe diferente de extensão. Esses hooks são para comportamento de provedor
que ainda é executado no loop normal de inferência do OpenClaw.

### Exemplo de provedor

```ts
api.registerProvider({
  id: "example-proxy",
  label: "Example Proxy",
  auth: [],
  catalog: {
    order: "simple",
    run: async (ctx) => {
      const apiKey = ctx.resolveProviderApiKey("example-proxy").apiKey;
      if (!apiKey) {
        return null;
      }
      return {
        provider: {
          baseUrl: "https://proxy.example.com/v1",
          apiKey,
          api: "openai-completions",
          models: [{ id: "auto", name: "Auto" }],
        },
      };
    },
  },
  resolveDynamicModel: (ctx) => ({
    id: ctx.modelId,
    name: ctx.modelId,
    provider: "example-proxy",
    api: "openai-completions",
    baseUrl: "https://proxy.example.com/v1",
    reasoning: false,
    input: ["text"],
    cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
    contextWindow: 128000,
    maxTokens: 8192,
  }),
  prepareRuntimeAuth: async (ctx) => {
    const exchanged = await exchangeToken(ctx.apiKey);
    return {
      apiKey: exchanged.token,
      baseUrl: exchanged.baseUrl,
      expiresAt: exchanged.expiresAt,
    };
  },
  resolveUsageAuth: async (ctx) => {
    const auth = await ctx.resolveOAuthToken();
    return auth ? { token: auth.token } : null;
  },
  fetchUsageSnapshot: async (ctx) => {
    return await fetchExampleProxyUsage(ctx.token, ctx.timeoutMs, ctx.fetchFn);
  },
});
```

### Exemplos incluídos

- Anthropic usa `resolveDynamicModel`, `capabilities`, `buildAuthDoctorHint`,
  `resolveUsageAuth`, `fetchUsageSnapshot`, `isCacheTtlEligible`,
  `resolveDefaultThinkingLevel`, `applyConfigDefaults`, `isModernModelRef`
  e `wrapStreamFn` porque é responsável por compatibilidade futura com Claude 4.6,
  dicas de família de provedor, orientação de reparo de autenticação, integração
  com endpoint de uso, elegibilidade de cache de prompt, padrões de configuração com reconhecimento de autenticação, política
  padrão/adaptativa de raciocínio do Claude e modelagem de stream específica da Anthropic para
  cabeçalhos beta, `/fast` / `serviceTier` e `context1m`.
- Os auxiliares de stream específicos do Claude da Anthropic permanecem, por enquanto, no próprio
  seam público `api.ts` / `contract-api.ts` do plugin incluído. Essa superfície do pacote
  exporta `wrapAnthropicProviderStream`, `resolveAnthropicBetas`,
  `resolveAnthropicFastMode`, `resolveAnthropicServiceTier` e os builders de wrapper
  de nível inferior da Anthropic, em vez de ampliar o SDK genérico em torno das regras de cabeçalho beta
  de um único provedor.
- OpenAI usa `resolveDynamicModel`, `normalizeResolvedModel` e
  `capabilities`, além de `buildMissingAuthMessage`, `suppressBuiltInModel`,
  `augmentModelCatalog`, `supportsXHighThinking` e `isModernModelRef`
  porque é responsável por compatibilidade futura com GPT-5.4, pela normalização direta da OpenAI de
  `openai-completions` -> `openai-responses`, dicas de autenticação com reconhecimento de Codex,
  supressão do Spark, linhas sintéticas da lista OpenAI e política de raciocínio / modelo ao vivo do GPT-5; a família de stream `openai-responses-defaults` é responsável pelos
  wrappers nativos compartilhados do OpenAI Responses para cabeçalhos de atribuição,
  `/fast`/`serviceTier`, verbosidade de texto, pesquisa na web nativa do Codex,
  modelagem de payload de compatibilidade de raciocínio e gerenciamento de contexto do Responses.
- OpenRouter usa `catalog`, além de `resolveDynamicModel` e
  `prepareDynamicModel`, porque o provedor é pass-through e pode expor novos
  IDs de modelo antes das atualizações do catálogo estático do OpenClaw; também usa
  `capabilities`, `wrapStreamFn` e `isCacheTtlEligible` para manter
  cabeçalhos de requisição específicos do provedor, metadados de roteamento, patches de raciocínio e
  política de cache de prompt fora do core. Sua política de replay vem da
  família `passthrough-gemini`, enquanto a família de stream `openrouter-thinking`
  é responsável pela injeção de raciocínio via proxy e pelos ignoramentos de modelo não suportado / `auto`.
- GitHub Copilot usa `catalog`, `auth`, `resolveDynamicModel` e
  `capabilities`, além de `prepareRuntimeAuth` e `fetchUsageSnapshot`, porque
  precisa de login por dispositivo pertencente ao provedor, comportamento de fallback de modelo, peculiaridades
  de transcrição do Claude, troca de token GitHub -> token Copilot e um endpoint de uso pertencente ao provedor.
- OpenAI Codex usa `catalog`, `resolveDynamicModel`,
  `normalizeResolvedModel`, `refreshOAuth` e `augmentModelCatalog`, além de
  `prepareExtraParams`, `resolveUsageAuth` e `fetchUsageSnapshot`, porque
  ainda é executado nos transportes OpenAI do core, mas é responsável por sua normalização
  de transporte/URL base, política de fallback de atualização de OAuth, escolha padrão
  de transporte, linhas sintéticas de catálogo do Codex e integração com endpoint de uso do ChatGPT; ele
  compartilha a mesma família de stream `openai-responses-defaults` da OpenAI direta.
- Google AI Studio e Gemini CLI OAuth usam `resolveDynamicModel`,
  `buildReplayPolicy`, `sanitizeReplayHistory`,
  `resolveReasoningOutputMode`, `wrapStreamFn` e `isModernModelRef` porque a
  família de replay `google-gemini` é responsável pelo fallback de compatibilidade futura do Gemini 3.1,
  validação nativa de replay do Gemini, sanitização de replay na inicialização, modo
  de saída de raciocínio marcada e correspondência de modelos modernos, enquanto a
  família de stream `google-thinking` é responsável pela normalização do payload de raciocínio do Gemini;
  Gemini CLI OAuth também usa `formatApiKey`, `resolveUsageAuth` e
  `fetchUsageSnapshot` para formatação de token, parsing de token e
  wiring do endpoint de cota.
- Anthropic Vertex usa `buildReplayPolicy` por meio da
  família de replay `anthropic-by-model`, para que a limpeza de replay específica do Claude permaneça
  restrita a IDs do Claude em vez de todo transporte `anthropic-messages`.
- Amazon Bedrock usa `buildReplayPolicy`, `matchesContextOverflowError`,
  `classifyFailoverReason` e `resolveDefaultThinkingLevel` porque é responsável pela classificação de erros específicos do Bedrock de throttling/não pronto/overflow de contexto
  para tráfego Anthropic-on-Bedrock; sua política de replay ainda compartilha a mesma
  proteção somente para Claude `anthropic-by-model`.
- OpenRouter, Kilocode, Opencode e Opencode Go usam `buildReplayPolicy`
  por meio da família de replay `passthrough-gemini`, porque fazem proxy de modelos Gemini
  por transportes compatíveis com OpenAI e precisam de sanitização de assinatura de pensamento do Gemini
  sem validação nativa de replay do Gemini nem reescritas de inicialização.
- MiniMax usa `buildReplayPolicy` por meio da
  família de replay `hybrid-anthropic-openai`, porque um provedor é responsável tanto pela semântica
  de mensagens Anthropic quanto pela semântica compatível com OpenAI; ele mantém
  a remoção de blocos de pensamento somente do Claude no lado Anthropic, enquanto substitui o modo de
  saída de raciocínio de volta para nativo, e a família de stream `minimax-fast-mode` é responsável pelas reescritas de modelos
  de modo rápido no caminho compartilhado de stream.
- Moonshot usa `catalog`, além de `wrapStreamFn`, porque ainda usa o transporte
  compartilhado da OpenAI, mas precisa de normalização de payload de raciocínio pertencente ao provedor; a
  família de stream `moonshot-thinking` mapeia configuração mais estado de `/think` para seu
  payload nativo de raciocínio binário.
- Kilocode usa `catalog`, `capabilities`, `wrapStreamFn` e
  `isCacheTtlEligible` porque precisa de cabeçalhos de requisição pertencentes ao provedor,
  normalização de payload de raciocínio, dicas de transcrição do Gemini e controle de
  TTL de cache da Anthropic; a família de stream `kilocode-thinking` mantém a injeção de raciocínio do Kilo
  no caminho compartilhado de stream por proxy, enquanto ignora `kilo/auto` e
  outros IDs de modelo proxy que não suportam payloads explícitos de raciocínio.
- Z.AI usa `resolveDynamicModel`, `prepareExtraParams`, `wrapStreamFn`,
  `isCacheTtlEligible`, `isBinaryThinking`, `isModernModelRef`,
  `resolveUsageAuth` e `fetchUsageSnapshot` porque é responsável pelo fallback do GLM-5,
  pelos padrões de `tool_stream`, UX de raciocínio binário, correspondência de modelos modernos e por autenticação de uso + busca de cota; a família de stream `tool-stream-default-on` mantém o wrapper
  padrão ligado de `tool_stream` fora de glue manual por provedor.
- xAI usa `normalizeResolvedModel`, `normalizeTransport`,
  `contributeResolvedModelCompat`, `prepareExtraParams`, `wrapStreamFn`,
  `resolveSyntheticAuth`, `resolveDynamicModel` e `isModernModelRef`
  porque é responsável pela normalização nativa do transporte xAI Responses, reescritas de alias
  do modo rápido do Grok, `tool_stream` padrão, limpeza estrita de ferramenta / payload de raciocínio,
  reutilização de autenticação de fallback para ferramentas pertencentes ao plugin, resolução de modelo Grok
  compatível com versões futuras e patches de compatibilidade pertencentes ao provedor, como perfil de schema de ferramentas da xAI,
  palavras-chave de schema não suportadas, `web_search` nativo e decodificação
  de entidades HTML em argumentos de chamadas de ferramenta.
- Mistral, OpenCode Zen e OpenCode Go usam apenas `capabilities` para manter
  peculiaridades de transcrição/ferramentas fora do core.
- Provedores incluídos somente de catálogo, como `byteplus`, `cloudflare-ai-gateway`,
  `huggingface`, `kimi-coding`, `nvidia`, `qianfan`,
  `synthetic`, `together`, `venice`, `vercel-ai-gateway` e `volcengine`, usam
  apenas `catalog`.
- Qwen usa `catalog` para seu provedor de texto, além de registros compartilhados de media-understanding e
  video-generation para suas superfícies multimodais.
- MiniMax e Xiaomi usam `catalog` mais hooks de uso porque seu comportamento de `/usage`
  pertence ao plugin, embora a inferência ainda seja executada pelos transportes compartilhados.

## Auxiliares de runtime

Plugins podem acessar auxiliares selecionados do core por meio de `api.runtime`. Para TTS:

```ts
const clip = await api.runtime.tts.textToSpeech({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const result = await api.runtime.tts.textToSpeechTelephony({
  text: "Hello from OpenClaw",
  cfg: api.config,
});

const voices = await api.runtime.tts.listVoices({
  provider: "elevenlabs",
  cfg: api.config,
});
```

Observações:

- `textToSpeech` retorna o payload normal de saída de TTS do core para superfícies de arquivo/mensagem de voz.
- Usa a configuração `messages.tts` do core e a seleção de provedor.
- Retorna buffer de áudio PCM + taxa de amostragem. Plugins devem reamostrar/codificar para provedores.
- `listVoices` é opcional por provedor. Use-o para seletores de voz pertencentes ao fornecedor ou fluxos de configuração.
- Listagens de vozes podem incluir metadados mais ricos, como localidade, gênero e tags de personalidade para seletores com reconhecimento de provedor.
- OpenAI e ElevenLabs oferecem suporte a telefonia hoje. Microsoft não.

Plugins também podem registrar provedores de fala via `api.registerSpeechProvider(...)`.

```ts
api.registerSpeechProvider({
  id: "acme-speech",
  label: "Acme Speech",
  isConfigured: ({ config }) => Boolean(config.messages?.tts),
  synthesize: async (req) => {
    return {
      audioBuffer: Buffer.from([]),
      outputFormat: "mp3",
      fileExtension: ".mp3",
      voiceCompatible: false,
    };
  },
});
```

Observações:

- Mantenha política de TTS, fallback e entrega de resposta no core.
- Use provedores de fala para comportamento de síntese pertencente ao fornecedor.
- A entrada legada `edge` da Microsoft é normalizada para o ID de provedor `microsoft`.
- O modelo de propriedade preferido é orientado por empresa: um plugin de fornecedor pode ser responsável por
  texto, fala, imagem e futuros provedores de mídia à medida que o OpenClaw adiciona esses
  contratos de capacidade.

Para entendimento de imagem/áudio/vídeo, plugins registram um provedor tipado de
media-understanding em vez de um pacote genérico de chave/valor:

```ts
api.registerMediaUnderstandingProvider({
  id: "google",
  capabilities: ["image", "audio", "video"],
  describeImage: async (req) => ({ text: "..." }),
  transcribeAudio: async (req) => ({ text: "..." }),
  describeVideo: async (req) => ({ text: "..." }),
});
```

Observações:

- Mantenha orquestração, fallback, configuração e wiring de canal no core.
- Mantenha o comportamento do fornecedor no plugin do provedor.
- A expansão aditiva deve permanecer tipada: novos métodos opcionais, novos
  campos de resultado opcionais, novas capacidades opcionais.
- A geração de vídeo já segue o mesmo padrão:
  - o core é responsável pelo contrato de capacidade e pelo auxiliar de runtime
  - plugins de fornecedores registram `api.registerVideoGenerationProvider(...)`
  - plugins de recurso/canal consomem `api.runtime.videoGeneration.*`

Para auxiliares de runtime de media-understanding, plugins podem chamar:

```ts
const image = await api.runtime.mediaUnderstanding.describeImageFile({
  filePath: "/tmp/inbound-photo.jpg",
  cfg: api.config,
  agentDir: "/tmp/agent",
});

const video = await api.runtime.mediaUnderstanding.describeVideoFile({
  filePath: "/tmp/inbound-video.mp4",
  cfg: api.config,
});
```

Para transcrição de áudio, plugins podem usar o runtime de media-understanding
ou o alias STT mais antigo:

```ts
const { text } = await api.runtime.mediaUnderstanding.transcribeAudioFile({
  filePath: "/tmp/inbound-audio.ogg",
  cfg: api.config,
  // Optional when MIME cannot be inferred reliably:
  mime: "audio/ogg",
});
```

Observações:

- `api.runtime.mediaUnderstanding.*` é a superfície compartilhada preferida para
  entendimento de imagem/áudio/vídeo.
- Usa a configuração de áudio de media-understanding do core (`tools.media.audio`) e a ordem de fallback do provedor.
- Retorna `{ text: undefined }` quando nenhuma saída de transcrição é produzida (por exemplo, entrada ignorada/não suportada).
- `api.runtime.stt.transcribeAudioFile(...)` permanece como um alias de compatibilidade.

Plugins também podem iniciar execuções de subagente em segundo plano por meio de `api.runtime.subagent`:

```ts
const result = await api.runtime.subagent.run({
  sessionKey: "agent:main:subagent:search-helper",
  message: "Expand this query into focused follow-up searches.",
  provider: "openai",
  model: "gpt-4.1-mini",
  deliver: false,
});
```

Observações:

- `provider` e `model` são substituições opcionais por execução, não mudanças persistentes de sessão.
- O OpenClaw só respeita esses campos de substituição para chamadores confiáveis.
- Para execuções de fallback pertencentes ao plugin, operadores precisam optar por isso com `plugins.entries.<id>.subagent.allowModelOverride: true`.
- Use `plugins.entries.<id>.subagent.allowedModels` para restringir plugins confiáveis a destinos canônicos específicos `provider/model`, ou `"*"` para permitir explicitamente qualquer destino.
- Execuções de subagente de plugins não confiáveis ainda funcionam, mas solicitações de substituição são rejeitadas em vez de cair silenciosamente em fallback.

Para pesquisa na web, plugins podem consumir o auxiliar compartilhado de runtime em vez de
acessar o wiring da ferramenta do agente:

```ts
const providers = api.runtime.webSearch.listProviders({
  config: api.config,
});

const result = await api.runtime.webSearch.search({
  config: api.config,
  args: {
    query: "OpenClaw plugin runtime helpers",
    count: 5,
  },
});
```

Plugins também podem registrar provedores de pesquisa na web via
`api.registerWebSearchProvider(...)`.

Observações:

- Mantenha seleção de provedor, resolução de credenciais e semântica compartilhada de requisição no core.
- Use provedores de pesquisa na web para transportes de pesquisa específicos do fornecedor.
- `api.runtime.webSearch.*` é a superfície compartilhada preferida para plugins de recurso/canal que precisam de comportamento de pesquisa sem depender do wrapper da ferramenta do agente.

### `api.runtime.imageGeneration`

```ts
const result = await api.runtime.imageGeneration.generate({
  config: api.config,
  args: { prompt: "A friendly lobster mascot", size: "1024x1024" },
});

const providers = api.runtime.imageGeneration.listProviders({
  config: api.config,
});
```

- `generate(...)`: gera uma imagem usando a cadeia configurada de provedores de geração de imagem.
- `listProviders(...)`: lista os provedores de geração de imagem disponíveis e suas capacidades.

## Rotas HTTP do Gateway

Plugins podem expor endpoints HTTP com `api.registerHttpRoute(...)`.

```ts
api.registerHttpRoute({
  path: "/acme/webhook",
  auth: "plugin",
  match: "exact",
  handler: async (_req, res) => {
    res.statusCode = 200;
    res.end("ok");
    return true;
  },
});
```

Campos da rota:

- `path`: caminho da rota sob o servidor HTTP do gateway.
- `auth`: obrigatório. Use `"gateway"` para exigir a autenticação normal do gateway, ou `"plugin"` para autenticação gerenciada por plugin/verificação de webhook.
- `match`: opcional. `"exact"` (padrão) ou `"prefix"`.
- `replaceExisting`: opcional. Permite que o mesmo plugin substitua seu próprio registro de rota existente.
- `handler`: retorne `true` quando a rota tiver tratado a requisição.

Observações:

- `api.registerHttpHandler(...)` foi removido e causará um erro de carregamento do plugin. Use `api.registerHttpRoute(...)` no lugar.
- Rotas de plugin devem declarar `auth` explicitamente.
- Conflitos exatos de `path + match` são rejeitados, a menos que `replaceExisting: true`, e um plugin não pode substituir a rota de outro plugin.
- Rotas sobrepostas com níveis de `auth` diferentes são rejeitadas. Mantenha cadeias de fallback `exact`/`prefix` apenas no mesmo nível de autenticação.
- Rotas `auth: "plugin"` **não** recebem automaticamente escopos de runtime do operador. Elas são para webhooks/verificação de assinatura gerenciados por plugin, não para chamadas auxiliares privilegiadas do Gateway.
- Rotas `auth: "gateway"` são executadas dentro de um escopo de runtime de requisição do Gateway, mas esse escopo é intencionalmente conservador:
  - autenticação bearer por segredo compartilhado (`gateway.auth.mode = "token"` / `"password"`) mantém os escopos de runtime da rota do plugin fixos em `operator.write`, mesmo que o chamador envie `x-openclaw-scopes`
  - modos HTTP confiáveis com identidade (por exemplo `trusted-proxy` ou `gateway.auth.mode = "none"` em uma entrada privada) respeitam `x-openclaw-scopes` apenas quando o cabeçalho está explicitamente presente
  - se `x-openclaw-scopes` estiver ausente nessas requisições de rota de plugin com identidade, o escopo de runtime recai para `operator.write`
- Regra prática: não assuma que uma rota de plugin autenticada pelo gateway é implicitamente uma superfície de administrador. Se sua rota precisar de comportamento restrito a admin, exija um modo de autenticação com identidade e documente o contrato explícito do cabeçalho `x-openclaw-scopes`.

## Caminhos de importação do Plugin SDK

Use subcaminhos do SDK em vez da importação monolítica `openclaw/plugin-sdk` ao
criar plugins:

- `openclaw/plugin-sdk/plugin-entry` para primitivas de registro de plugin.
- `openclaw/plugin-sdk/core` para o contrato genérico compartilhado voltado a plugins.
- `openclaw/plugin-sdk/config-schema` para o export do schema Zod raiz de `openclaw.json`
  (`OpenClawSchema`).
- Primitivas estáveis de canal, como `openclaw/plugin-sdk/channel-setup`,
  `openclaw/plugin-sdk/setup-runtime`,
  `openclaw/plugin-sdk/setup-adapter-runtime`,
  `openclaw/plugin-sdk/setup-tools`,
  `openclaw/plugin-sdk/channel-pairing`,
  `openclaw/plugin-sdk/channel-contract`,
  `openclaw/plugin-sdk/channel-feedback`,
  `openclaw/plugin-sdk/channel-inbound`,
  `openclaw/plugin-sdk/channel-lifecycle`,
  `openclaw/plugin-sdk/channel-reply-pipeline`,
  `openclaw/plugin-sdk/command-auth`,
  `openclaw/plugin-sdk/secret-input` e
  `openclaw/plugin-sdk/webhook-ingress` para wiring compartilhado de
  configuração/autenticação/resposta/webhook. `channel-inbound` é o local compartilhado para debounce, correspondência de menções,
  auxiliares de política de menção de entrada, formatação de envelope e
  auxiliares de contexto de envelope de entrada.
  `channel-setup` é o seam estreito de configuração opcional de instalação.
  `setup-runtime` é a superfície de configuração segura para runtime usada por `setupEntry` /
  inicialização adiada, incluindo os adaptadores de patch de configuração seguros para importação.
  `setup-adapter-runtime` é o seam de adaptador de configuração de conta com reconhecimento de env.
  `setup-tools` é o seam pequeno de auxiliares de CLI/arquivo/docs (`formatCliCommand`,
  `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`,
  `CONFIG_DIR`).
- Subcaminhos de domínio como `openclaw/plugin-sdk/channel-config-helpers`,
  `openclaw/plugin-sdk/allow-from`,
  `openclaw/plugin-sdk/channel-config-schema`,
  `openclaw/plugin-sdk/telegram-command-config`,
  `openclaw/plugin-sdk/channel-policy`,
  `openclaw/plugin-sdk/approval-gateway-runtime`,
  `openclaw/plugin-sdk/approval-handler-adapter-runtime`,
  `openclaw/plugin-sdk/approval-handler-runtime`,
  `openclaw/plugin-sdk/approval-runtime`,
  `openclaw/plugin-sdk/config-runtime`,
  `openclaw/plugin-sdk/infra-runtime`,
  `openclaw/plugin-sdk/agent-runtime`,
  `openclaw/plugin-sdk/lazy-runtime`,
  `openclaw/plugin-sdk/reply-history`,
  `openclaw/plugin-sdk/routing`,
  `openclaw/plugin-sdk/status-helpers`,
  `openclaw/plugin-sdk/text-runtime`,
  `openclaw/plugin-sdk/runtime-store` e
  `openclaw/plugin-sdk/directory-runtime` para auxiliares compartilhados de runtime/configuração.
  `telegram-command-config` é o seam público estreito para normalização/validação de comando personalizado do Telegram e permanece disponível mesmo que a superfície de contrato incluída do Telegram esteja temporariamente indisponível.
  `text-runtime` é o seam compartilhado de texto/markdown/logging, incluindo
  remoção de texto visível ao assistente, auxiliares de renderização/fragmentação de markdown, auxiliares de redação,
  auxiliares de tags de diretiva e utilitários de texto seguro.
- Seams de canal específicos de aprovação devem preferir um único contrato `approvalCapability`
  no plugin. O core então lê autenticação de aprovação, entrega, renderização,
  roteamento nativo e comportamento lazy de handler nativo por meio dessa única
  capacidade, em vez de misturar comportamento de aprovação em campos não relacionados do plugin.
- `openclaw/plugin-sdk/channel-runtime` está obsoleto e permanece apenas como um
  shim de compatibilidade para plugins mais antigos. Código novo deve importar as primitivas genéricas mais estreitas, e o código do repositório não deve adicionar novos imports do
  shim.
- Internos de extensões incluídas continuam privados. Plugins externos devem usar apenas subcaminhos `openclaw/plugin-sdk/*`. Código do core/teste do OpenClaw pode usar os
  pontos de entrada públicos do repositório sob a raiz de um pacote de plugin, como `index.js`, `api.js`,
  `runtime-api.js`, `setup-entry.js` e arquivos de escopo estreito, como
  `login-qr-api.js`. Nunca importe `src/*` de um pacote de plugin a partir do core ou de
  outra extensão.
- Divisão do ponto de entrada do repositório:
  `<plugin-package-root>/api.js` é o barrel de auxiliares/tipos,
  `<plugin-package-root>/runtime-api.js` é o barrel somente de runtime,
  `<plugin-package-root>/index.js` é a entrada do plugin incluído,
  e `<plugin-package-root>/setup-entry.js` é a entrada do plugin de configuração.
- Exemplos atuais de provedores incluídos:
  - Anthropic usa `api.js` / `contract-api.js` para auxiliares de stream do Claude, como
    `wrapAnthropicProviderStream`, auxiliares de cabeçalho beta e parsing de `service_tier`.
  - OpenAI usa `api.js` para builders de provedor, auxiliares de modelo padrão e
    builders de provedor em tempo real.
  - OpenRouter usa `api.js` para seu builder de provedor, além de auxiliares de onboarding/configuração,
    enquanto `register.runtime.js` ainda pode reexportar auxiliares genéricos
    `plugin-sdk/provider-stream` para uso local no repositório.
- Pontos de entrada públicos carregados por facade preferem o snapshot de configuração de runtime ativo
  quando ele existe e, em seguida, recorrem ao arquivo de configuração resolvido em disco quando o
  OpenClaw ainda não está servindo um snapshot de runtime.
- Primitivas genéricas compartilhadas continuam sendo o contrato público preferido do SDK. Ainda existe um pequeno
  conjunto reservado de compatibilidade de seams auxiliares com marca de canal incluído. Trate-os como seams de manutenção/compatibilidade de incluídos, não como novos alvos de importação de terceiros; novos contratos entre canais ainda devem ficar em subcaminhos genéricos `plugin-sdk/*` ou nos barrels locais do plugin `api.js` /
  `runtime-api.js`.

Observação de compatibilidade:

- Evite o barrel raiz `openclaw/plugin-sdk` em código novo.
- Prefira primeiro as primitivas estáveis e estreitas. Os subcaminhos mais novos de setup/pairing/reply/
  feedback/contract/inbound/threading/command/secret-input/webhook/infra/
  allowlist/status/message-tool são o contrato pretendido para novos trabalhos
  de plugins incluídos e externos.
  Parsing/correspondência de destinos pertence a `openclaw/plugin-sdk/channel-targets`.
  Gates de ação de mensagem e auxiliares de ID de mensagem de reação pertencem a
  `openclaw/plugin-sdk/channel-actions`.
- Barrels auxiliares específicos de extensões incluídas não são estáveis por padrão. Se um
  auxiliar for necessário apenas para uma extensão incluída, mantenha-o por trás do seam local
  `api.js` ou `runtime-api.js` da extensão, em vez de promovê-lo para
  `openclaw/plugin-sdk/<extension>`.
- Novos seams auxiliares compartilhados devem ser genéricos, não associados a uma marca de canal. O parsing compartilhado de destino
  pertence a `openclaw/plugin-sdk/channel-targets`; internos específicos do canal
  permanecem por trás do seam local `api.js` ou `runtime-api.js` do plugin proprietário.
- Subcaminhos específicos de capacidade, como `image-generation`,
  `media-understanding` e `speech`, existem porque plugins nativos/incluídos os usam
  hoje. Sua presença não significa, por si só, que todo auxiliar exportado seja um
  contrato externo congelado de longo prazo.

## Schemas da ferramenta de mensagem

Plugins devem ser responsáveis por contribuições de schema específicas de canal em
`describeMessageTool(...)`. Mantenha campos específicos do provedor no plugin, não no core compartilhado.

Para fragmentos de schema portáveis compartilhados, reutilize os auxiliares genéricos exportados por
`openclaw/plugin-sdk/channel-actions`:

- `createMessageToolButtonsSchema()` para payloads no estilo grade de botões
- `createMessageToolCardSchema()` para payloads estruturados de cartão

Se um formato de schema só fizer sentido para um provedor, defina-o no próprio
código-fonte desse plugin em vez de promovê-lo ao SDK compartilhado.

## Resolução de destinos de canal

Plugins de canal devem ser responsáveis por semântica de destino específica do canal. Mantenha o
host compartilhado de saída genérico e use a superfície do adaptador de mensagens para regras do provedor:

- `messaging.inferTargetChatType({ to })` decide se um destino normalizado
  deve ser tratado como `direct`, `group` ou `channel` antes da busca no diretório.
- `messaging.targetResolver.looksLikeId(raw, normalized)` informa ao core se uma
  entrada deve pular direto para resolução semelhante a ID em vez de busca no diretório.
- `messaging.targetResolver.resolveTarget(...)` é o fallback do plugin quando o
  core precisa de uma resolução final pertencente ao provedor após normalização ou após falha no diretório.
- `messaging.resolveOutboundSessionRoute(...)` é responsável pela construção de rota de sessão
  específica do provedor depois que um destino é resolvido.

Divisão recomendada:

- Use `inferTargetChatType` para decisões de categoria que devem acontecer antes de
  pesquisar pares/grupos.
- Use `looksLikeId` para verificações do tipo "trate isto como um ID de destino explícito/nativo".
- Use `resolveTarget` para fallback de normalização específico do provedor, não para
  busca ampla em diretório.
- Mantenha IDs nativos do provedor, como chat ids, thread ids, JIDs, handles e room
  ids, dentro de valores `target` ou parâmetros específicos do provedor, não em campos genéricos do SDK.

## Diretórios baseados em configuração

Plugins que derivam entradas de diretório da configuração devem manter essa lógica no
plugin e reutilizar os auxiliares compartilhados de
`openclaw/plugin-sdk/directory-runtime`.

Use isso quando um canal precisar de pares/grupos baseados em configuração, como:

- pares de DM orientados por allowlist
- mapas configurados de canal/grupo
- fallbacks estáticos de diretório com escopo de conta

Os auxiliares compartilhados em `directory-runtime` lidam apenas com operações genéricas:

- filtragem de consulta
- aplicação de limite
- auxiliares de deduplicação/normalização
- construção de `ChannelDirectoryEntry[]`

Inspeção de conta específica do canal e normalização de ID devem permanecer na
implementação do plugin.

## Catálogos de provedores

Plugins de provedor podem definir catálogos de modelos para inferência com
`registerProvider({ catalog: { run(...) { ... } } })`.

`catalog.run(...)` retorna o mesmo formato que o OpenClaw grava em
`models.providers`:

- `{ provider }` para uma entrada de provedor
- `{ providers }` para várias entradas de provedor

Use `catalog` quando o plugin for responsável por IDs de modelo específicos do provedor, padrões de URL base
ou metadados de modelo controlados por autenticação.

`catalog.order` controla quando o catálogo de um plugin é mesclado em relação aos
provedores implícitos internos do OpenClaw:

- `simple`: provedores simples por chave de API ou orientados por env
- `profile`: provedores que aparecem quando existem perfis de autenticação
- `paired`: provedores que sintetizam várias entradas de provedor relacionadas
- `late`: última passagem, após outros provedores implícitos

Provedores posteriores vencem em colisão de chave, então plugins podem substituir intencionalmente
uma entrada de provedor interna com o mesmo ID de provedor.

Compatibilidade:

- `discovery` ainda funciona como alias legado
- se `catalog` e `discovery` forem registrados, o OpenClaw usa `catalog`

## Inspeção de canal somente leitura

Se o seu plugin registrar um canal, prefira implementar
`plugin.config.inspectAccount(cfg, accountId)` junto com `resolveAccount(...)`.

Por quê:

- `resolveAccount(...)` é o caminho de runtime. Pode assumir que as credenciais
  estão totalmente materializadas e pode falhar rapidamente quando segredos obrigatórios estiverem ausentes.
- Caminhos de comando somente leitura, como `openclaw status`, `openclaw status --all`,
  `openclaw channels status`, `openclaw channels resolve` e fluxos de reparo de doctor/config
  não devem precisar materializar credenciais de runtime apenas para
  descrever a configuração.

Comportamento recomendado de `inspectAccount(...)`:

- Retorne apenas o estado descritivo da conta.
- Preserve `enabled` e `configured`.
- Inclua campos de origem/status de credencial quando relevante, como:
  - `tokenSource`, `tokenStatus`
  - `botTokenSource`, `botTokenStatus`
  - `appTokenSource`, `appTokenStatus`
  - `signingSecretSource`, `signingSecretStatus`
- Você não precisa retornar valores brutos de token apenas para relatar disponibilidade somente leitura.
  Retornar `tokenStatus: "available"` (e o campo de origem correspondente)
  é suficiente para comandos no estilo status.
- Use `configured_unavailable` quando uma credencial estiver configurada via SecretRef, mas
  indisponível no caminho de comando atual.

Isso permite que comandos somente leitura relatem "configurado, mas indisponível neste caminho de comando"
em vez de travar ou relatar incorretamente a conta como não configurada.

## Packs de pacote

Um diretório de plugin pode incluir um `package.json` com `openclaw.extensions`:

```json
{
  "name": "my-pack",
  "openclaw": {
    "extensions": ["./src/safety.ts", "./src/tools.ts"],
    "setupEntry": "./src/setup-entry.ts"
  }
}
```

Cada entrada vira um plugin. Se o pack listar várias extensões, o ID do plugin
passa a ser `name/<fileBase>`.

Se seu plugin importar dependências npm, instale-as nesse diretório para que
`node_modules` esteja disponível (`npm install` / `pnpm install`).

Barreira de segurança: toda entrada em `openclaw.extensions` deve permanecer dentro do diretório do plugin
após a resolução de symlink. Entradas que escapem do diretório do pacote são
rejeitadas.

Observação de segurança: `openclaw plugins install` instala dependências de plugin com
`npm install --omit=dev --ignore-scripts` (sem scripts de ciclo de vida, sem dependências de desenvolvimento em runtime). Mantenha as árvores de dependências do plugin em "JS/TS puro" e evite pacotes que exijam builds em `postinstall`.

Opcional: `openclaw.setupEntry` pode apontar para um módulo leve somente de configuração.
Quando o OpenClaw precisa de superfícies de configuração para um plugin de canal desabilitado, ou
quando um plugin de canal está habilitado, mas ainda não configurado, ele carrega `setupEntry`
em vez da entrada completa do plugin. Isso mantém a inicialização e a configuração mais leves
quando a entrada principal do seu plugin também conecta ferramentas, hooks ou outro
código somente de runtime.

Opcional: `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen`
pode fazer um plugin de canal optar por esse mesmo caminho `setupEntry` durante a
fase de inicialização pré-listen do gateway, mesmo quando o canal já estiver configurado.

Use isso apenas quando `setupEntry` cobrir totalmente a superfície de inicialização que deve existir
antes que o gateway comece a escutar. Na prática, isso significa que a entrada de configuração
deve registrar toda capacidade pertencente ao canal da qual a inicialização depende, como:

- o próprio registro do canal
- quaisquer rotas HTTP que precisem estar disponíveis antes de o gateway começar a escutar
- quaisquer métodos, ferramentas ou serviços do gateway que precisem existir durante essa mesma janela

Se sua entrada completa ainda for responsável por qualquer capacidade de inicialização obrigatória, não habilite
essa flag. Mantenha o comportamento padrão do plugin e deixe o OpenClaw carregar a
entrada completa durante a inicialização.

Canais incluídos também podem publicar auxiliares de superfície de contrato somente de configuração que o core
pode consultar antes de o runtime completo do canal ser carregado. A superfície atual de promoção de configuração
é:

- `singleAccountKeysToMove`
- `namedAccountPromotionKeys`
- `resolveSingleAccountPromotionTarget(...)`

O core usa essa superfície quando precisa promover uma configuração legada de canal com conta única
para `channels.<id>.accounts.*` sem carregar a entrada completa do plugin.
Matrix é o exemplo incluído atual: ele move apenas chaves de autenticação/bootstrap para uma
conta promovida com nome quando contas nomeadas já existem e pode preservar uma
chave de conta padrão configurada e não canônica em vez de sempre criar
`accounts.default`.

Esses adaptadores de patch de configuração mantêm a descoberta da superfície de contrato incluída de forma lazy.
O tempo de importação permanece leve; a superfície de promoção é carregada apenas no primeiro uso, em vez de reentrar na inicialização do canal incluído na importação do módulo.

Quando essas superfícies de inicialização incluírem métodos RPC do gateway, mantenha-os em um
prefixo específico do plugin. Namespaces administrativos do core (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) continuam reservados e sempre são resolvidos
como `operator.admin`, mesmo que um plugin solicite um escopo mais estreito.

Exemplo:

```json
{
  "name": "@scope/my-channel",
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "startup": {
      "deferConfiguredChannelFullLoadUntilAfterListen": true
    }
  }
}
```

### Metadados de catálogo de canal

Plugins de canal podem anunciar metadados de configuração/descoberta via `openclaw.channel` e
dicas de instalação via `openclaw.install`. Isso mantém os dados de catálogo do core vazios.

Exemplo:

```json
{
  "name": "@openclaw/nextcloud-talk",
  "openclaw": {
    "extensions": ["./index.ts"],
    "channel": {
      "id": "nextcloud-talk",
      "label": "Nextcloud Talk",
      "selectionLabel": "Nextcloud Talk (self-hosted)",
      "docsPath": "/channels/nextcloud-talk",
      "docsLabel": "nextcloud-talk",
      "blurb": "Self-hosted chat via Nextcloud Talk webhook bots.",
      "order": 65,
      "aliases": ["nc-talk", "nc"]
    },
    "install": {
      "npmSpec": "@openclaw/nextcloud-talk",
      "localPath": "<bundled-plugin-local-path>",
      "defaultChoice": "npm"
    }
  }
}
```

Campos úteis de `openclaw.channel` além do exemplo mínimo:

- `detailLabel`: rótulo secundário para superfícies mais ricas de catálogo/status
- `docsLabel`: substitui o texto do link para os docs
- `preferOver`: IDs de plugin/canal de prioridade mais baixa que esta entrada de catálogo deve superar
- `selectionDocsPrefix`, `selectionDocsOmitLabel`, `selectionExtras`: controles de cópia da superfície de seleção
- `markdownCapable`: marca o canal como compatível com markdown para decisões de formatação de saída
- `exposure.configured`: oculta o canal das superfícies de listagem de canais configurados quando definido como `false`
- `exposure.setup`: oculta o canal dos seletores interativos de configuração quando definido como `false`
- `exposure.docs`: marca o canal como interno/privado para superfícies de navegação de docs
- `showConfigured` / `showInSetup`: aliases legados ainda aceitos por compatibilidade; prefira `exposure`
- `quickstartAllowFrom`: faz o canal optar pelo fluxo padrão de início rápido `allowFrom`
- `forceAccountBinding`: exige vínculo explícito de conta mesmo quando existe apenas uma conta
- `preferSessionLookupForAnnounceTarget`: prefere busca de sessão ao resolver destinos de anúncio

O OpenClaw também pode mesclar **catálogos externos de canal** (por exemplo, uma exportação
de registro MPM). Coloque um arquivo JSON em um destes locais:

- `~/.openclaw/mpm/plugins.json`
- `~/.openclaw/mpm/catalog.json`
- `~/.openclaw/plugins/catalog.json`

Ou aponte `OPENCLAW_PLUGIN_CATALOG_PATHS` (ou `OPENCLAW_MPM_CATALOG_PATHS`) para
um ou mais arquivos JSON (delimitados por vírgula/ponto e vírgula/`PATH`). Cada arquivo deve
conter `{ "entries": [ { "name": "@scope/pkg", "openclaw": { "channel": {...}, "install": {...} } } ] }`. O parser também aceita `"packages"` ou `"plugins"` como aliases legados para a chave `"entries"`.

## Plugins de mecanismo de contexto

Plugins de mecanismo de contexto são responsáveis pela orquestração do contexto da sessão para ingestão, montagem
e compactação. Registre-os a partir do seu plugin com
`api.registerContextEngine(id, factory)` e depois selecione o mecanismo ativo com
`plugins.slots.contextEngine`.

Use isso quando seu plugin precisar substituir ou estender o pipeline de contexto padrão,
em vez de apenas adicionar pesquisa de memória ou hooks.

```ts
import { buildMemorySystemPromptAddition } from "openclaw/plugin-sdk/core";

export default function (api) {
  api.registerContextEngine("lossless-claw", () => ({
    info: { id: "lossless-claw", name: "Lossless Claw", ownsCompaction: true },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages, availableTools, citationsMode }) {
      return {
        messages,
        estimatedTokens: 0,
        systemPromptAddition: buildMemorySystemPromptAddition({
          availableTools: availableTools ?? new Set(),
          citationsMode,
        }),
      };
    },
    async compact() {
      return { ok: true, compacted: false };
    },
  }));
}
```

Se seu mecanismo **não** for responsável pelo algoritmo de compactação, mantenha `compact()`
implementado e delegue-o explicitamente:

```ts
import {
  buildMemorySystemPromptAddition,
  delegateCompactionToRuntime,
} from "openclaw/plugin-sdk/core";

export default function (api) {
  api.registerContextEngine("my-memory-engine", () => ({
    info: {
      id: "my-memory-engine",
      name: "My Memory Engine",
      ownsCompaction: false,
    },
    async ingest() {
      return { ingested: true };
    },
    async assemble({ messages, availableTools, citationsMode }) {
      return {
        messages,
        estimatedTokens: 0,
        systemPromptAddition: buildMemorySystemPromptAddition({
          availableTools: availableTools ?? new Set(),
          citationsMode,
        }),
      };
    },
    async compact(params) {
      return await delegateCompactionToRuntime(params);
    },
  }));
}
```

## Adicionar uma nova capacidade

Quando um plugin precisa de um comportamento que não se encaixa na API atual, não contorne
o sistema de plugins com um acesso privado interno. Adicione a capacidade ausente.

Sequência recomendada:

1. defina o contrato do core
   Decida qual comportamento compartilhado o core deve possuir: política, fallback, mesclagem de configuração,
   ciclo de vida, semântica voltada a canais e formato do auxiliar de runtime.
2. adicione superfícies tipadas de registro/runtime de plugin
   Estenda `OpenClawPluginApi` e/ou `api.runtime` com a menor superfície útil de capacidade tipada.
3. conecte consumidores do core + canal/recurso
   Canais e plugins de recurso devem consumir a nova capacidade por meio do core,
   não importando diretamente uma implementação de fornecedor.
4. registre implementações de fornecedor
   Plugins de fornecedores então registram seus backends nessa capacidade.
5. adicione cobertura de contrato
   Adicione testes para que a propriedade e o formato do registro permaneçam explícitos ao longo do tempo.

É assim que o OpenClaw permanece opinativo sem ficar codificado rigidamente à visão de mundo
de um único provedor. Consulte o [Livro de receitas de capacidades](/pt-BR/plugins/architecture)
para um checklist concreto de arquivos e um exemplo completo.

### Checklist de capacidade

Quando você adiciona uma nova capacidade, a implementação normalmente deve tocar estas
superfícies em conjunto:

- tipos de contrato do core em `src/<capability>/types.ts`
- runner/auxiliar de runtime do core em `src/<capability>/runtime.ts`
- superfície da API de registro de plugin em `src/plugins/types.ts`
- wiring do registro de plugins em `src/plugins/registry.ts`
- exposição de runtime de plugin em `src/plugins/runtime/*` quando plugins de recurso/canal
  precisarem consumi-la
- auxiliares de captura/teste em `src/test-utils/plugin-registration.ts`
- asserções de propriedade/contrato em `src/plugins/contracts/registry.ts`
- documentação para operadores/plugins em `docs/`

Se uma dessas superfícies estiver ausente, isso geralmente é um sinal de que a capacidade
ainda não está totalmente integrada.

### Template de capacidade

Padrão mínimo:

```ts
// core contract
export type VideoGenerationProviderPlugin = {
  id: string;
  label: string;
  generateVideo: (req: VideoGenerationRequest) => Promise<VideoGenerationResult>;
};

// plugin API
api.registerVideoGenerationProvider({
  id: "openai",
  label: "OpenAI",
  async generateVideo(req) {
    return await generateOpenAiVideo(req);
  },
});

// shared runtime helper for feature/channel plugins
const clip = await api.runtime.videoGeneration.generate({
  prompt: "Show the robot walking through the lab.",
  cfg,
});
```

Padrão de teste de contrato:

```ts
expect(findVideoGenerationProviderIdsForPlugin("openai")).toEqual(["openai"]);
```

Isso mantém a regra simples:

- o core é responsável pelo contrato de capacidade + orquestração
- plugins de fornecedores são responsáveis por implementações de fornecedor
- plugins de recurso/canal consomem auxiliares de runtime
- testes de contrato mantêm a propriedade explícita
