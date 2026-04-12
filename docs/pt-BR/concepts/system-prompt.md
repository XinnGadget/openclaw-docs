---
read_when:
    - Editar o texto do prompt do sistema, a lista de ferramentas ou as seções de hora/heartbeat
    - Alterar o comportamento de bootstrap do workspace ou da injeção de Skills
summary: O que o prompt do sistema do OpenClaw contém e como ele é montado
title: Prompt do sistema
x-i18n:
    generated_at: "2026-04-12T05:33:09Z"
    model: gpt-5.4
    provider: openai
    source_hash: 057f01aac51f7737b5223f61f5d55e552d9011232aebb130426e269d8f6c257f
    source_path: concepts/system-prompt.md
    workflow: 15
---

# Prompt do sistema

O OpenClaw cria um prompt do sistema personalizado para cada execução de agente. O prompt é **de propriedade do OpenClaw** e não usa o prompt padrão do pi-coding-agent.

O prompt é montado pelo OpenClaw e injetado em cada execução de agente.

Plugins de provedor podem contribuir com orientações de prompt compatíveis com cache sem substituir o prompt completo de propriedade do OpenClaw. O runtime do provedor pode:

- substituir um pequeno conjunto de seções centrais nomeadas (`interaction_style`,
  `tool_call_style`, `execution_bias`)
- injetar um **prefixo estável** acima do limite de cache do prompt
- injetar um **sufixo dinâmico** abaixo do limite de cache do prompt

Use contribuições de propriedade do provedor para ajustes específicos de famílias de modelos. Mantenha a mutação legada de prompt `before_prompt_build` para compatibilidade ou para mudanças de prompt realmente globais, não para o comportamento normal do provedor.

## Estrutura

O prompt é intencionalmente compacto e usa seções fixas:

- **Ferramentas**: lembrete da fonte da verdade de ferramentas estruturadas mais orientações de runtime para uso de ferramentas.
- **Segurança**: lembrete curto de proteção para evitar comportamento de busca por poder ou de contorno de supervisão.
- **Skills** (quando disponíveis): informa ao modelo como carregar instruções de skill sob demanda.
- **Autoatualização do OpenClaw**: como inspecionar a configuração com segurança usando
  `config.schema.lookup`, aplicar patch na configuração com `config.patch`, substituir a configuração completa com `config.apply` e executar `update.run` apenas mediante solicitação explícita do usuário. A ferramenta `gateway`, exclusiva do proprietário, também se recusa a reescrever
  `tools.exec.ask` / `tools.exec.security`, incluindo aliases legados `tools.bash.*`
  que são normalizados para esses caminhos de exec protegidos.
- **Workspace**: diretório de trabalho (`agents.defaults.workspace`).
- **Documentação**: caminho local para a documentação do OpenClaw (repositório ou pacote npm) e quando lê-la.
- **Arquivos do workspace (injetados)**: indica que os arquivos de bootstrap estão incluídos abaixo.
- **Sandbox** (quando habilitado): indica runtime em sandbox, caminhos do sandbox e se exec com privilégios elevados está disponível.
- **Data e hora atuais**: hora local do usuário, fuso horário e formato de hora.
- **Tags de resposta**: sintaxe opcional de tags de resposta para provedores compatíveis.
- **Heartbeats**: prompt de heartbeat e comportamento de confirmação, quando heartbeats estão habilitados para o agente padrão.
- **Runtime**: host, SO, node, raiz do repositório (quando detectada), nível de raciocínio (uma linha).
- **Raciocínio**: nível atual de visibilidade + dica do toggle `/reasoning`.

A seção Ferramentas também inclui orientações de runtime para trabalhos de longa duração:

- use cron para acompanhamento futuro (`check back later`, lembretes, trabalho recorrente)
  em vez de loops de sleep com `exec`, truques de atraso com `yieldMs` ou polling repetido de `process`
- use `exec` / `process` apenas para comandos que começam agora e continuam em execução
  em segundo plano
- quando o wake automático por conclusão estiver habilitado, inicie o comando uma vez e confie
  no caminho de wake baseado em push quando ele emitir saída ou falhar
- use `process` para logs, status, entrada ou intervenção quando precisar
  inspecionar um comando em execução
- se a tarefa for maior, prefira `sessions_spawn`; a conclusão de subagentes é
  baseada em push e é anunciada automaticamente de volta ao solicitante
- não faça polling de `subagents list` / `sessions_list` em loop apenas para aguardar
  a conclusão

Quando a ferramenta experimental `update_plan` está habilitada, Ferramentas também informa ao
modelo para usá-la apenas em trabalhos não triviais com múltiplas etapas, manter exatamente uma
etapa `in_progress` e evitar repetir o plano inteiro após cada atualização.

As proteções de segurança no prompt do sistema são consultivas. Elas orientam o comportamento do modelo, mas não impõem política. Use política de ferramentas, aprovações de exec, sandboxing e listas de permissões de canais para imposição rígida; operadores podem desativá-las por design.

Em canais com cartões/botões de aprovação nativos, o prompt de runtime agora informa ao
agente para depender primeiro dessa UI de aprovação nativa. Ele só deve incluir um comando manual
`/approve` quando o resultado da ferramenta disser que aprovações no chat não estão disponíveis ou
que a aprovação manual é o único caminho.

## Modos de prompt

O OpenClaw pode renderizar prompts do sistema menores para subagentes. O runtime define um
`promptMode` para cada execução (não é uma configuração voltada ao usuário):

- `full` (padrão): inclui todas as seções acima.
- `minimal`: usado para subagentes; omite **Skills**, **Recuperação de memória**, **Autoatualização do OpenClaw**, **Aliases de modelo**, **Identidade do usuário**, **Tags de resposta**,
  **Mensagens**, **Respostas silenciosas** e **Heartbeats**. Ferramentas, **Segurança**,
  Workspace, Sandbox, Data e hora atuais (quando conhecidas), Runtime e contexto
  injetado continuam disponíveis.
- `none`: retorna apenas a linha de identidade base.

Quando `promptMode=minimal`, prompts extras injetados são rotulados como **Contexto do subagente**
em vez de **Contexto do chat em grupo**.

## Injeção de bootstrap do workspace

Os arquivos de bootstrap são aparados e anexados em **Contexto do projeto** para que o modelo veja o contexto de identidade e perfil sem precisar fazer leituras explícitas:

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md` (apenas em workspaces totalmente novos)
- `MEMORY.md` quando presente, caso contrário `memory.md` como fallback em minúsculas

Todos esses arquivos são **injetados na janela de contexto** em cada turno, a menos que
se aplique um gate específico do arquivo. `HEARTBEAT.md` é omitido em execuções normais quando
heartbeats estão desabilitados para o agente padrão ou quando
`agents.defaults.heartbeat.includeSystemPromptSection` é false. Mantenha os arquivos injetados concisos — especialmente `MEMORY.md`, que pode crescer com o tempo e levar a uso de contexto inesperadamente alto e compactação mais frequente.

> **Observação:** arquivos diários `memory/*.md` **não** fazem parte do bootstrap normal de
> Contexto do projeto. Em turnos comuns, eles são acessados sob demanda por meio das
> ferramentas `memory_search` e `memory_get`, portanto não contam contra a janela de
> contexto, a menos que o modelo os leia explicitamente. Turnos simples de `/new` e
> `/reset` são a exceção: o runtime pode prependar memória diária recente
> como um bloco único de contexto de inicialização para esse primeiro turno.

Arquivos grandes são truncados com um marcador. O tamanho máximo por arquivo é controlado por
`agents.defaults.bootstrapMaxChars` (padrão: 20000). O conteúdo total de bootstrap injetado
entre os arquivos é limitado por `agents.defaults.bootstrapTotalMaxChars`
(padrão: 150000). Arquivos ausentes injetam um marcador curto de arquivo ausente. Quando ocorre truncamento,
o OpenClaw pode injetar um bloco de aviso em Contexto do projeto; controle isso com
`agents.defaults.bootstrapPromptTruncationWarning` (`off`, `once`, `always`;
padrão: `once`).

Sessões de subagente injetam apenas `AGENTS.md` e `TOOLS.md` (os outros arquivos de bootstrap
são filtrados para manter pequeno o contexto do subagente).

Hooks internos podem interceptar esta etapa via `agent:bootstrap` para modificar ou substituir
os arquivos de bootstrap injetados (por exemplo, trocando `SOUL.md` por uma persona alternativa).

Se você quiser fazer o agente soar menos genérico, comece com
[Guia de personalidade do SOUL.md](/pt-BR/concepts/soul).

Para inspecionar quanto cada arquivo injetado contribui (bruto vs. injetado, truncamento, além da sobrecarga do schema de ferramentas), use `/context list` ou `/context detail`. Veja [Contexto](/pt-BR/concepts/context).

## Tratamento de tempo

O prompt do sistema inclui uma seção dedicada **Data e hora atuais** quando o
fuso horário do usuário é conhecido. Para manter o cache do prompt estável, agora ele inclui apenas o
**fuso horário** (sem relógio dinâmico nem formato de hora).

Use `session_status` quando o agente precisar da hora atual; o cartão de status
inclui uma linha de timestamp. A mesma ferramenta também pode opcionalmente definir uma substituição
de modelo por sessão (`model=default` a limpa).

Configure com:

- `agents.defaults.userTimezone`
- `agents.defaults.timeFormat` (`auto` | `12` | `24`)

Veja [Data e hora](/pt-BR/date-time) para detalhes completos do comportamento.

## Skills

Quando existem skills elegíveis, o OpenClaw injeta uma **lista compacta de skills disponíveis**
(`formatSkillsForPrompt`) que inclui o **caminho do arquivo** de cada skill. O
prompt instrui o modelo a usar `read` para carregar o SKILL.md no local listado
(workspace, gerenciado ou empacotado). Se não houver skills elegíveis, a seção
Skills é omitida.

A elegibilidade inclui gates de metadados da skill, verificações de ambiente/configuração de runtime
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

Isso mantém o prompt base pequeno, ao mesmo tempo que ainda permite uso direcionado de skills.

## Documentação

Quando disponível, o prompt do sistema inclui uma seção **Documentação** que aponta para o
diretório local da documentação do OpenClaw (seja `docs/` no workspace do repositório ou a documentação do
pacote npm empacotado) e também menciona o espelho público, o repositório de origem, o Discord da comunidade e o
ClawHub ([https://clawhub.ai](https://clawhub.ai)) para descoberta de skills. O prompt instrui o modelo a consultar primeiro a documentação local
para comportamento, comandos, configuração ou arquitetura do OpenClaw e a executar
`openclaw status` por conta própria quando possível (pedindo ao usuário apenas quando não tiver acesso).
