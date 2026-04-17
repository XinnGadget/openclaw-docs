---
read_when:
    - Editando o texto do prompt de sistema, a lista de ferramentas ou as seções de hora/Heartbeat
    - Alterando o bootstrap do workspace ou o comportamento de injeção de Skills
summary: O que o prompt de sistema do OpenClaw contém e como ele é montado
title: Prompt de sistema
x-i18n:
    generated_at: "2026-04-15T19:41:35Z"
    model: gpt-5.4
    provider: openai
    source_hash: c740e4646bc4980567338237bfb55126af0df72499ca00a48e4848d9a3608ab4
    source_path: concepts/system-prompt.md
    workflow: 15
---

# Prompt de sistema

O OpenClaw monta um prompt de sistema personalizado para cada execução de agente. O prompt é **de propriedade do OpenClaw** e não usa o prompt padrão do pi-coding-agent.

O prompt é montado pelo OpenClaw e injetado em cada execução de agente.

Plugins de provedor podem contribuir com orientações de prompt com reconhecimento de cache sem substituir todo o prompt de propriedade do OpenClaw. O runtime do provedor pode:

- substituir um pequeno conjunto de seções centrais nomeadas (`interaction_style`,
  `tool_call_style`, `execution_bias`)
- injetar um **prefixo estável** acima do limite de cache do prompt
- injetar um **sufixo dinâmico** abaixo do limite de cache do prompt

Use contribuições de propriedade do provedor para ajustes específicos de famílias de modelos. Mantenha a mutação legada de prompt `before_prompt_build` para compatibilidade ou mudanças de prompt realmente globais, não para o comportamento normal do provedor.

## Estrutura

O prompt é intencionalmente compacto e usa seções fixas:

- **Ferramentas**: lembrete da fonte da verdade de ferramentas estruturadas, além de orientações de uso de ferramentas em runtime.
- **Segurança**: lembrete curto de proteção para evitar comportamento de busca de poder ou desvio de supervisão.
- **Skills** (quando disponíveis): informa ao modelo como carregar instruções de skill sob demanda.
- **Autoatualização do OpenClaw**: como inspecionar a configuração com segurança usando
  `config.schema.lookup`, aplicar patch na configuração com `config.patch`, substituir toda a
  configuração com `config.apply` e executar `update.run` somente mediante solicitação explícita do usuário. A ferramenta `gateway`, restrita ao proprietário, também se recusa a reescrever
  `tools.exec.ask` / `tools.exec.security`, incluindo aliases legados `tools.bash.*`
  que são normalizados para esses caminhos protegidos de exec.
- **Workspace**: diretório de trabalho (`agents.defaults.workspace`).
- **Documentação**: caminho local para a documentação do OpenClaw (repositório ou pacote npm) e quando lê-la.
- **Arquivos do Workspace (injetados)**: indica que os arquivos de bootstrap estão incluídos abaixo.
- **Sandbox** (quando habilitado): indica runtime em sandbox, caminhos do sandbox e se exec elevado está disponível.
- **Data e hora atuais**: hora local do usuário, fuso horário e formato de hora.
- **Tags de resposta**: sintaxe opcional de tags de resposta para provedores compatíveis.
- **Heartbeats**: prompt de heartbeat e comportamento de confirmação, quando heartbeats estão habilitados para o agente padrão.
- **Runtime**: host, SO, node, raiz do repositório (quando detectada), nível de raciocínio (uma linha).
- **Raciocínio**: nível atual de visibilidade + dica de alternância com /reasoning.

A seção Ferramentas também inclui orientações de runtime para trabalhos de longa duração:

- use Cron para acompanhamento futuro (`check back later`, lembretes, trabalho recorrente)
  em vez de loops de `exec` com sleep, truques de atraso com `yieldMs` ou polling repetido de `process`
- use `exec` / `process` apenas para comandos que começam agora e continuam rodando
  em segundo plano
- quando o despertar automático na conclusão estiver habilitado, inicie o comando uma vez e confie no caminho de despertar baseado em push quando ele emitir saída ou falhar
- use `process` para logs, status, entrada ou intervenção quando precisar
  inspecionar um comando em execução
- se a tarefa for maior, prefira `sessions_spawn`; a conclusão de subagentes é
  baseada em push e anunciada automaticamente de volta ao solicitante
- não faça polling de `subagents list` / `sessions_list` em loop apenas para esperar
  a conclusão

Quando a ferramenta experimental `update_plan` está habilitada, Ferramentas também informa ao
modelo para usá-la apenas em trabalhos não triviais de várias etapas, manter exatamente uma
etapa `in_progress` e evitar repetir o plano inteiro após cada atualização.

As proteções de segurança no prompt de sistema são orientativas. Elas orientam o comportamento do modelo, mas não impõem política. Use política de ferramentas, aprovações de exec, sandboxing e allowlists de canais para imposição rígida; operadores podem desabilitar isso por design.

Em canais com cartões/botões de aprovação nativos, o prompt de runtime agora instrui o
agente a confiar primeiro nessa interface nativa de aprovação. Ele só deve incluir um comando manual
`/approve` quando o resultado da ferramenta informar que aprovações no chat não estão disponíveis ou
que aprovação manual é o único caminho.

## Modos de prompt

O OpenClaw pode renderizar prompts de sistema menores para subagentes. O runtime define um
`promptMode` para cada execução (não é uma configuração voltada ao usuário):

- `full` (padrão): inclui todas as seções acima.
- `minimal`: usado para subagentes; omite **Skills**, **Recordação de Memória**, **Autoatualização do OpenClaw**, **Aliases de modelos**, **Identidade do usuário**, **Tags de resposta**,
  **Mensageria**, **Respostas silenciosas** e **Heartbeats**. Ferramentas, **Segurança**,
  Workspace, Sandbox, Data e hora atuais (quando conhecidas), Runtime e contexto
  injetado continuam disponíveis.
- `none`: retorna apenas a linha base de identidade.

Quando `promptMode=minimal`, prompts extras injetados são rotulados como **Contexto do subagente**
em vez de **Contexto de chat em grupo**.

## Injeção de bootstrap do workspace

Os arquivos de bootstrap são recortados e anexados em **Contexto do projeto** para que o modelo veja o contexto de identidade e perfil sem precisar de leituras explícitas:

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md` (somente em workspaces totalmente novos)
- `MEMORY.md` quando presente, caso contrário `memory.md` como fallback em minúsculas

Todos esses arquivos são **injetados na janela de contexto** em toda rodada, a menos que
se aplique um bloqueio específico do arquivo. `HEARTBEAT.md` é omitido em execuções normais quando
heartbeats estão desabilitados para o agente padrão ou
`agents.defaults.heartbeat.includeSystemPromptSection` é false. Mantenha os arquivos injetados concisos — especialmente `MEMORY.md`, que pode crescer com o tempo e levar a uso de contexto inesperadamente alto e compaction mais frequente.

> **Observação:** arquivos diários `memory/*.md` **não** fazem parte do Contexto do projeto
> normal do bootstrap. Em rodadas comuns, eles são acessados sob demanda por meio das
> ferramentas `memory_search` e `memory_get`, portanto não contam contra a
> janela de contexto, a menos que o modelo os leia explicitamente. Rodadas simples de `/new` e
> `/reset` são a exceção: o runtime pode antepor memória diária recente
> como um bloco único de contexto inicial para essa primeira rodada.

Arquivos grandes são truncados com um marcador. O tamanho máximo por arquivo é controlado por
`agents.defaults.bootstrapMaxChars` (padrão: 20000). O conteúdo total de bootstrap injetado
entre arquivos é limitado por `agents.defaults.bootstrapTotalMaxChars`
(padrão: 150000). Arquivos ausentes injetam um marcador curto de arquivo ausente. Quando ocorre truncamento,
o OpenClaw pode injetar um bloco de aviso em Contexto do projeto; controle isso com
`agents.defaults.bootstrapPromptTruncationWarning` (`off`, `once`, `always`;
padrão: `once`).

Sessões de subagentes injetam apenas `AGENTS.md` e `TOOLS.md` (outros arquivos de bootstrap
são filtrados para manter pequeno o contexto do subagente).

Hooks internos podem interceptar esta etapa por meio de `agent:bootstrap` para mutar ou substituir
os arquivos de bootstrap injetados (por exemplo, trocando `SOUL.md` por uma persona alternativa).

Se você quiser fazer o agente soar menos genérico, comece com
[Guia de personalidade do SOUL.md](/pt-BR/concepts/soul).

Para inspecionar quanto cada arquivo injetado contribui (bruto vs injetado, truncamento, além da sobrecarga do schema da ferramenta), use `/context list` ou `/context detail`. Veja [Contexto](/pt-BR/concepts/context).

## Tratamento de hora

O prompt de sistema inclui uma seção dedicada **Data e hora atuais** quando o
fuso horário do usuário é conhecido. Para manter o cache do prompt estável, agora ela inclui apenas o
**fuso horário** (sem relógio dinâmico nem formato de hora).

Use `session_status` quando o agente precisar da hora atual; o cartão de status
inclui uma linha de timestamp. A mesma ferramenta também pode opcionalmente definir uma substituição
de modelo por sessão (`model=default` a remove).

Configure com:

- `agents.defaults.userTimezone`
- `agents.defaults.timeFormat` (`auto` | `12` | `24`)

Veja [Data e hora](/pt-BR/date-time) para detalhes completos do comportamento.

## Skills

Quando existem skills elegíveis, o OpenClaw injeta uma **lista compacta de skills disponíveis**
(`formatSkillsForPrompt`) que inclui o **caminho do arquivo** de cada skill. O
prompt instrui o modelo a usar `read` para carregar o SKILL.md no local listado
(workspace, gerenciado ou empacotado). Se não houver skills elegíveis, a
seção Skills é omitida.

A elegibilidade inclui bloqueios de metadados da skill, verificações de ambiente/configuração de runtime
e a allowlist efetiva de skills do agente quando `agents.defaults.skills` ou
`agents.list[].skills` está configurado.

```
<available_skills>
  <skill>
    <name>...</name>
    <description>...</description>
    <location>...</location>
  </skill>
</available_skills>
```

Isso mantém o prompt base pequeno enquanto ainda permite uso direcionado de skills.

O orçamento da lista de skills pertence ao subsistema de skills:

- Padrão global: `skills.limits.maxSkillsPromptChars`
- Sobrescrita por agente: `agents.list[].skillsLimits.maxSkillsPromptChars`

Trechos genéricos limitados de runtime usam uma superfície diferente:

- `agents.defaults.contextLimits.*`
- `agents.list[].contextLimits.*`

Essa separação mantém o dimensionamento de skills separado do dimensionamento de leitura/injeção de runtime, como
`memory_get`, resultados de ferramentas ao vivo e atualizações de `AGENTS.md` após compaction.

## Documentação

Quando disponível, o prompt de sistema inclui uma seção **Documentação** que aponta para o
diretório local da documentação do OpenClaw (seja `docs/` no workspace do repositório ou a documentação do
pacote npm empacotado) e também menciona o espelho público, o repositório de origem, o Discord da comunidade e o
ClawHub ([https://clawhub.ai](https://clawhub.ai)) para descoberta de skills. O prompt instrui o modelo a consultar primeiro a documentação local
para comportamento, comandos, configuração ou arquitetura do OpenClaw, e a executar
`openclaw status` por conta própria quando possível (pedindo ao usuário apenas quando não tiver acesso).
