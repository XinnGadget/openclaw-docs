---
read_when:
    - Estendendo o qa-lab ou o qa-channel
    - Adicionando cenários de QA com suporte do repositório
    - Criando uma automação de QA com maior realismo em torno do painel do Gateway
summary: Forma da automação privada de QA para qa-lab, qa-channel, cenários com seed e relatórios de protocolo
title: Automação E2E de QA
x-i18n:
    generated_at: "2026-04-17T05:36:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: 51f97293c184d7c04c95d9858305668fbc0f93273f587ec7e54896ad5d603ab0
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# Automação E2E de QA

A stack privada de QA foi feita para exercitar o OpenClaw de uma forma mais realista,
no formato de canais, do que um único teste unitário consegue.

Peças atuais:

- `extensions/qa-channel`: canal de mensagens sintético com superfícies de DM, canal, thread,
  reação, edição e exclusão.
- `extensions/qa-lab`: UI de depuração e barramento de QA para observar a transcrição,
  injetar mensagens recebidas e exportar um relatório em Markdown.
- `qa/`: recursos seed com suporte do repositório para a tarefa inicial e cenários
  básicos de QA.

O fluxo atual do operador de QA é um site de QA com dois painéis:

- Esquerda: painel do Gateway (Control UI) com o agente.
- Direita: QA Lab, mostrando a transcrição em estilo Slack e o plano de cenário.

Execute com:

```bash
pnpm qa:lab:up
```

Isso compila o site de QA, inicia a lane do gateway com suporte de Docker e expõe a
página do QA Lab, onde um operador ou loop de automação pode dar ao agente uma
missão de QA, observar o comportamento real do canal e registrar o que funcionou,
falhou ou permaneceu bloqueado.

Para uma iteração mais rápida da UI do QA Lab sem reconstruir a imagem Docker a cada vez,
inicie a stack com um bundle do QA Lab montado por bind mount:

```bash
pnpm openclaw qa docker-build-image
pnpm qa:lab:build
pnpm qa:lab:up:fast
pnpm qa:lab:watch
```

`qa:lab:up:fast` mantém os serviços Docker em uma imagem pré-compilada e faz bind mount de
`extensions/qa-lab/web/dist` no contêiner `qa-lab`. `qa:lab:watch`
recompila esse bundle quando há mudanças, e o navegador recarrega automaticamente quando o hash
do recurso do QA Lab muda.

Para uma lane de smoke do Matrix com transporte real, execute:

```bash
pnpm openclaw qa matrix
```

Essa lane provisiona um homeserver Tuwunel descartável no Docker, registra usuários
temporários de driver, SUT e observador, cria uma sala privada e então executa
o Plugin real do Matrix dentro de um filho de gateway de QA. A lane de transporte ao vivo mantém
a configuração do filho restrita ao transporte em teste, então o Matrix roda sem
`qa-channel` na configuração do filho. Ela grava os artefatos do relatório estruturado e
um log combinado de stdout/stderr no diretório de saída de QA do Matrix selecionado. Para
capturar também a saída externa de compilação/launcher de `scripts/run-node.mjs`, defina
`OPENCLAW_RUN_NODE_OUTPUT_LOG=<path>` para um arquivo de log local ao repositório.

Para uma lane de smoke do Telegram com transporte real, execute:

```bash
pnpm openclaw qa telegram
```

Essa lane usa um grupo privado real do Telegram em vez de provisionar um
servidor descartável. Ela exige `OPENCLAW_QA_TELEGRAM_GROUP_ID`,
`OPENCLAW_QA_TELEGRAM_DRIVER_BOT_TOKEN` e
`OPENCLAW_QA_TELEGRAM_SUT_BOT_TOKEN`, além de dois bots distintos no mesmo
grupo privado. O bot SUT precisa ter um nome de usuário no Telegram, e a
observação bot-para-bot funciona melhor quando ambos os bots têm o Bot-to-Bot Communication Mode
ativado no `@BotFather`.

As lanes de transporte ao vivo agora compartilham um contrato menor em vez de cada uma
inventar o próprio formato de lista de cenários.

`qa-channel` continua sendo a suíte ampla de comportamento sintético do produto e não faz parte
da matriz de cobertura de transporte ao vivo.

| Lane     | Canary | Bloqueio por menção | Bloqueio por allowlist | Resposta de nível superior | Retomada após reinício | Acompanhamento em thread | Isolamento de thread | Observação de reação | Comando de ajuda |
| -------- | ------ | ------------------- | ---------------------- | -------------------------- | ---------------------- | ------------------------ | -------------------- | -------------------- | ---------------- |
| Matrix   | x      | x                   | x                      | x                          | x                      | x                        | x                    | x                    |                  |
| Telegram | x      |                     |                        |                            |                        |                          |                      |                      | x                |

Isso mantém `qa-channel` como a suíte ampla de comportamento do produto, enquanto Matrix,
Telegram e futuros transportes ao vivo compartilham uma checklist explícita de contrato de transporte.

Para uma lane de VM Linux descartável sem colocar Docker no caminho de QA, execute:

```bash
pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline
```

Isso inicializa um guest novo do Multipass, instala dependências, compila o OpenClaw
dentro do guest, executa `qa suite` e então copia o relatório e
resumo normais de QA de volta para `.artifacts/qa-e2e/...` no host.
Isso reutiliza o mesmo comportamento de seleção de cenário de `qa suite` no host.
As execuções da suíte no host e no Multipass executam vários cenários selecionados em paralelo
com workers de gateway isolados por padrão, até 64 workers ou a contagem de cenários
selecionados. Use `--concurrency <count>` para ajustar a quantidade de workers, ou
`--concurrency 1` para execução serial.
As execuções ao vivo encaminham as entradas de autenticação de QA suportadas que são práticas para o
guest: chaves de provider via variável de ambiente, o caminho de configuração do provider ao vivo de QA e
`CODEX_HOME` quando presente. Mantenha `--output-dir` sob a raiz do repositório para que o guest
possa gravar de volta pelo workspace montado.

## Seeds com suporte do repositório

Os recursos seed ficam em `qa/`:

- `qa/scenarios/index.md`
- `qa/scenarios/*.md`

Eles ficam intencionalmente no git para que o plano de QA seja visível tanto para humanos
quanto para o agente.

`qa-lab` deve permanecer um executor genérico de Markdown. Cada arquivo Markdown de cenário é
a fonte da verdade para uma execução de teste e deve definir:

- metadados do cenário
- referências de docs e código
- requisitos opcionais de plugin
- patch opcional de configuração do gateway
- o `qa-flow` executável

A superfície de runtime reutilizável que dá suporte ao `qa-flow` pode permanecer genérica
e transversal. Por exemplo, cenários em Markdown podem combinar helpers do lado do transporte
com helpers do lado do navegador que controlam a Control UI embutida por meio da
superfície `browser.request` do Gateway sem adicionar um executor com caso especial.

A lista básica deve permanecer ampla o suficiente para cobrir:

- chat em DM e em canal
- comportamento de thread
- ciclo de vida de ações de mensagem
- callbacks de Cron
- recuperação de memória
- troca de modelo
- handoff para subagente
- leitura do repositório e de docs
- uma pequena tarefa de compilação, como Lobster Invaders

## Lanes de mock de provider

`qa suite` tem duas lanes locais de mock de provider:

- `mock-openai` é o mock do OpenClaw sensível ao cenário. Ele continua sendo a
  lane de mock determinística padrão para QA com suporte do repositório e gates de paridade.
- `aimock` inicia um servidor de provider com suporte do AIMock para cobertura experimental de protocolo,
  fixture, gravação/reprodução e caos. Ele é aditivo e não substitui o dispatcher
  de cenários do `mock-openai`.

A implementação da lane de provider fica em `extensions/qa-lab/src/providers/`.
Cada provider é dono dos próprios padrões, inicialização do servidor local, configuração
de modelo do gateway, necessidades de preparação de perfil de autenticação e flags de capacidade
ao vivo/mock. O código compartilhado da suíte e do gateway deve rotear pelo registro de providers em vez de
ramificar com base em nomes de providers.

## Adaptadores de transporte

`qa-lab` é dono de uma superfície genérica de transporte para cenários de QA em Markdown.
`qa-channel` é o primeiro adaptador nessa superfície, mas o objetivo do design é mais amplo:
canais futuros, reais ou sintéticos, devem se conectar ao mesmo executor de suíte em vez de
adicionar um executor de QA específico para cada transporte.

No nível de arquitetura, a divisão é:

- `qa-lab` é dono da execução genérica de cenários, concorrência de workers, gravação de artefatos e relatórios.
- o adaptador de transporte é dono da configuração do gateway, prontidão, observação de entrada e saída, ações de transporte e estado de transporte normalizado.
- arquivos de cenário em Markdown em `qa/scenarios/` definem a execução de teste; `qa-lab` fornece a superfície de runtime reutilizável que os executa.

A orientação de adoção voltada para maintainers para novos adaptadores de canal está em
[Testing](/pt-BR/help/testing#adding-a-channel-to-qa).

## Relatórios

`qa-lab` exporta um relatório de protocolo em Markdown a partir da linha do tempo do barramento observado.
O relatório deve responder:

- O que funcionou
- O que falhou
- O que permaneceu bloqueado
- Quais cenários de acompanhamento valem a pena adicionar

Para verificações de caráter e estilo, execute o mesmo cenário em várias refs de modelos ao vivo
e grave um relatório em Markdown avaliado:

```bash
pnpm openclaw qa character-eval \
  --model openai/gpt-5.4,thinking=xhigh \
  --model openai/gpt-5.2,thinking=xhigh \
  --model openai/gpt-5,thinking=xhigh \
  --model anthropic/claude-opus-4-6,thinking=high \
  --model anthropic/claude-sonnet-4-6,thinking=high \
  --model zai/glm-5.1,thinking=high \
  --model moonshot/kimi-k2.5,thinking=high \
  --model google/gemini-3.1-pro-preview,thinking=high \
  --judge-model openai/gpt-5.4,thinking=xhigh,fast \
  --judge-model anthropic/claude-opus-4-6,thinking=high \
  --blind-judge-models \
  --concurrency 16 \
  --judge-concurrency 16
```

O comando executa processos filhos locais do gateway de QA, não Docker. Cenários de avaliação de caráter
devem definir a persona por meio de `SOUL.md` e então executar turnos normais de usuário
como chat, ajuda sobre o workspace e pequenas tarefas em arquivos. O modelo candidato
não deve ser informado de que está sendo avaliado. O comando preserva cada transcrição
completa, registra estatísticas básicas da execução e então pede que os modelos juízes, em modo fast com
raciocínio `xhigh`, classifiquem as execuções por naturalidade, vibe e humor.
Use `--blind-judge-models` ao comparar providers: o prompt do juiz ainda recebe
cada transcrição e status da execução, mas as refs candidatas são substituídas por rótulos neutros
como `candidate-01`; o relatório mapeia as classificações de volta para as refs reais após
o parsing.
As execuções dos candidatos usam por padrão `high` thinking, com `xhigh` para modelos OpenAI que
oferecem suporte. Substitua um candidato específico inline com
`--model provider/model,thinking=<level>`. `--thinking <level>` ainda define um fallback
global, e o formato mais antigo `--model-thinking <provider/model=level>` é
mantido por compatibilidade.
As refs candidatas da OpenAI usam o modo fast por padrão para que o processamento prioritário seja usado
quando o provider oferecer suporte. Adicione `,fast`, `,no-fast` ou `,fast=false` inline quando
um único candidato ou juiz precisar de uma substituição. Passe `--fast` apenas quando quiser
forçar o modo fast para todos os modelos candidatos. As durações de candidatos e juízes são
registradas no relatório para análise de benchmark, mas os prompts dos juízes dizem explicitamente
para não classificar com base em velocidade.
As execuções dos modelos candidatos e dos juízes usam concorrência 16 por padrão. Reduza
`--concurrency` ou `--judge-concurrency` quando limites do provider ou pressão no gateway local
tornarem uma execução muito ruidosa.
Quando nenhum `--model` candidato é passado, a avaliação de caráter usa por padrão
`openai/gpt-5.4`, `openai/gpt-5.2`, `openai/gpt-5`, `anthropic/claude-opus-4-6`,
`anthropic/claude-sonnet-4-6`, `zai/glm-5.1`,
`moonshot/kimi-k2.5` e
`google/gemini-3.1-pro-preview` quando nenhum `--model` é passado.
Quando nenhum `--judge-model` é passado, os juízes usam por padrão
`openai/gpt-5.4,thinking=xhigh,fast` e
`anthropic/claude-opus-4-6,thinking=high`.

## Docs relacionadas

- [Testing](/pt-BR/help/testing)
- [QA Channel](/pt-BR/channels/qa-channel)
- [Dashboard](/web/dashboard)
