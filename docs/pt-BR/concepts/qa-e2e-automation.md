---
read_when:
    - Estendendo qa-lab ou qa-channel
    - Adicionando cenários de QA com suporte do repositório
    - Criando automação de QA com maior realismo em torno do painel do Gateway
summary: Formato privado de automação de QA para qa-lab, qa-channel, cenários com seed e relatórios de protocolo
title: Automação E2E de QA
x-i18n:
    generated_at: "2026-04-10T05:34:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: 357d6698304ff7a8c4aa8a7be97f684d50f72b524740050aa761ac0ee68266de
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# Automação E2E de QA

A pilha privada de QA foi projetada para exercitar o OpenClaw de uma forma mais realista,
no formato de canal, do que um único teste unitário consegue.

Peças atuais:

- `extensions/qa-channel`: canal de mensagens sintético com superfícies de DM, canal, thread,
  reação, edição e exclusão.
- `extensions/qa-lab`: interface de depuração e barramento de QA para observar a transcrição,
  injetar mensagens de entrada e exportar um relatório em Markdown.
- `qa/`: ativos de seed com suporte do repositório para a tarefa inicial e cenários
  básicos de QA.

O fluxo atual do operador de QA é um site de QA com dois painéis:

- Esquerda: painel do Gateway (Control UI) com o agente.
- Direita: QA Lab, mostrando a transcrição no estilo do Slack e o plano de cenário.

Execute com:

```bash
pnpm qa:lab:up
```

Isso compila o site de QA, inicia a faixa do gateway com suporte do Docker e expõe a
página do QA Lab onde um operador ou loop de automação pode dar ao agente uma missão
de QA, observar o comportamento real do canal e registrar o que funcionou, falhou ou
permaneceu bloqueado.

Para uma iteração mais rápida na UI do QA Lab sem recompilar a imagem Docker a cada vez,
inicie a pilha com um bundle do QA Lab montado por bind:

```bash
pnpm openclaw qa docker-build-image
pnpm qa:lab:build
pnpm qa:lab:up:fast
pnpm qa:lab:watch
```

`qa:lab:up:fast` mantém os serviços Docker em uma imagem pré-compilada e faz bind-mount de
`extensions/qa-lab/web/dist` no contêiner `qa-lab`. `qa:lab:watch`
recompila esse bundle quando há mudanças, e o navegador recarrega automaticamente quando o hash
do ativo do QA Lab muda.

Para uma faixa descartável em VM Linux sem colocar o Docker no caminho do QA, execute:

```bash
pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline
```

Isso inicializa um guest novo do Multipass, instala as dependências, compila o OpenClaw
dentro do guest, executa `qa suite` e depois copia o relatório normal de QA e o
resumo de volta para `.artifacts/qa-e2e/...` no host.
Ele reutiliza o mesmo comportamento de seleção de cenário que `qa suite` no host.
Execuções ao vivo encaminham as entradas de autenticação de QA compatíveis que são práticas para o
guest: chaves de provedor baseadas em ambiente, o caminho de configuração do provedor ao vivo de QA e
`CODEX_HOME` quando presente. Mantenha `--output-dir` sob a raiz do repositório para que o guest
possa gravar de volta por meio do workspace montado.

## Seeds com suporte do repositório

Os ativos de seed ficam em `qa/`:

- `qa/scenarios/index.md`
- `qa/scenarios/*.md`

Eles estão intencionalmente no git para que o plano de QA fique visível tanto para humanos quanto para o
agente. A lista básica deve permanecer ampla o suficiente para cobrir:

- chat em DM e em canal
- comportamento de thread
- ciclo de vida de ações de mensagem
- callbacks de cron
- recuperação de memória
- troca de modelo
- handoff para subagente
- leitura do repositório e leitura da documentação
- uma pequena tarefa de build, como Lobster Invaders

## Relatórios

`qa-lab` exporta um relatório de protocolo em Markdown a partir da linha do tempo observada no barramento.
O relatório deve responder:

- O que funcionou
- O que falhou
- O que permaneceu bloqueado
- Quais cenários de acompanhamento valem a pena adicionar

Para verificações de personalidade e estilo, execute o mesmo cenário em várias refs de modelo ao vivo
e escreva um relatório em Markdown avaliado:

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

O comando executa processos filhos locais do gateway de QA, não Docker. Os cenários de avaliação de personalidade
devem definir a persona por meio de `SOUL.md` e depois executar turnos normais de usuário,
como chat, ajuda com o workspace e pequenas tarefas em arquivos. Não se deve informar ao
modelo candidato que ele está sendo avaliado. O comando preserva cada transcrição completa,
registra estatísticas básicas de execução e depois pede aos modelos juízes em modo rápido com
raciocínio `xhigh` para classificar as execuções por naturalidade, vibe e humor.
Use `--blind-judge-models` ao comparar provedores: o prompt do juiz ainda recebe
cada transcrição e status de execução, mas as refs candidatas são substituídas por rótulos neutros
como `candidate-01`; o relatório mapeia as classificações de volta para as refs reais após a
análise.
As execuções candidatas usam `high` thinking por padrão, com `xhigh` para modelos OpenAI que
o suportam. Substitua um candidato específico inline com
`--model provider/model,thinking=<level>`. `--thinking <level>` ainda define um
fallback global, e o formato antigo `--model-thinking <provider/model=level>` é
mantido por compatibilidade.
As refs candidatas da OpenAI usam o modo rápido por padrão para que o processamento prioritário seja usado onde
o provedor o suportar. Adicione `,fast`, `,no-fast` ou `,fast=false` inline quando um
único candidato ou juiz precisar de uma substituição. Passe `--fast` somente quando quiser
forçar o modo rápido para todos os modelos candidatos. As durações de candidatos e juízes são
registradas no relatório para análise comparativa, mas os prompts dos juízes dizem explicitamente
para não classificar por velocidade.
As execuções de modelos candidatos e juízes usam simultaneidade 16 por padrão. Reduza
`--concurrency` ou `--judge-concurrency` quando os limites do provedor ou a pressão no gateway local
tornarem uma execução barulhenta demais.
Quando nenhum candidato `--model` é passado, a avaliação de personalidade usa por padrão
`openai/gpt-5.4`, `openai/gpt-5.2`, `openai/gpt-5`, `anthropic/claude-opus-4-6`,
`anthropic/claude-sonnet-4-6`, `zai/glm-5.1`,
`moonshot/kimi-k2.5` e
`google/gemini-3.1-pro-preview` quando nenhum `--model` é passado.
Quando nenhum `--judge-model` é passado, os juízes usam por padrão
`openai/gpt-5.4,thinking=xhigh,fast` e
`anthropic/claude-opus-4-6,thinking=high`.

## Documentação relacionada

- [Testing](/pt-BR/help/testing)
- [QA Channel](/pt-BR/channels/qa-channel)
- [Dashboard](/web/dashboard)
