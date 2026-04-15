---
read_when:
    - Você quer entender como a memória funciona
    - Você quer saber quais arquivos de memória escrever
summary: Como o OpenClaw se lembra das coisas entre sessões
title: Visão geral da memória
x-i18n:
    generated_at: "2026-04-15T14:40:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: ad1adafe1d81f1703d24f48a9c9da2b25a0ebbd4aad4f65d8bde5df78195d55b
    source_path: concepts/memory.md
    workflow: 15
---

# Visão geral da memória

O OpenClaw se lembra das coisas escrevendo **arquivos Markdown simples** no
workspace do seu agente. O modelo só "se lembra" do que é salvo em disco -- não
há estado oculto.

## Como funciona

Seu agente tem três arquivos relacionados à memória:

- **`MEMORY.md`** -- memória de longo prazo. Fatos, preferências e
  decisões duráveis. Carregado no início de cada sessão de DM.
- **`memory/YYYY-MM-DD.md`** -- notas diárias. Contexto contínuo e observações.
  As notas de hoje e de ontem são carregadas automaticamente.
- **`DREAMS.md`** (opcional) -- Diário de Sonhos e resumos de varreduras de
  Dreaming para revisão humana, incluindo entradas históricas de backfill fundamentado.

Esses arquivos ficam no workspace do agente (padrão `~/.openclaw/workspace`).

<Tip>
Se você quiser que seu agente se lembre de algo, basta pedir: "Lembre-se de que
eu prefiro TypeScript." Ele escreverá isso no arquivo apropriado.
</Tip>

## Ferramentas de memória

O agente tem duas ferramentas para trabalhar com memória:

- **`memory_search`** -- encontra notas relevantes usando busca semântica, mesmo
  quando a redação difere da original.
- **`memory_get`** -- lê um arquivo de memória específico ou um intervalo de linhas.

Ambas as ferramentas são fornecidas pelo Plugin de memória ativo (padrão: `memory-core`).

## Plugin complementar Memory Wiki

Se você quiser que a memória durável se comporte mais como uma base de
conhecimento mantida do que apenas notas brutas, use o Plugin empacotado `memory-wiki`.

O `memory-wiki` compila conhecimento durável em um cofre wiki com:

- estrutura de página determinística
- afirmações e evidências estruturadas
- rastreamento de contradições e atualidade
- painéis gerados
- resumos compilados para consumidores do agente/runtime
- ferramentas nativas de wiki como `wiki_search`, `wiki_get`, `wiki_apply` e `wiki_lint`

Ele não substitui o Plugin de memória ativo. O Plugin de memória ativo ainda
é responsável por recordação, promoção e Dreaming. O `memory-wiki` adiciona
uma camada de conhecimento rica em procedência ao lado dele.

Veja [Memory Wiki](/pt-BR/plugins/memory-wiki).

## Busca de memória

Quando um provedor de embeddings está configurado, `memory_search` usa **busca
híbrida** -- combinando similaridade vetorial (significado semântico) com correspondência por palavra-chave
(termos exatos como IDs e símbolos de código). Isso funciona imediatamente assim que você tiver
uma chave de API para qualquer provedor compatível.

<Info>
O OpenClaw detecta automaticamente seu provedor de embeddings a partir das chaves de API disponíveis. Se você
tiver uma chave do OpenAI, Gemini, Voyage ou Mistral configurada, a busca de memória será
ativada automaticamente.
</Info>

Para detalhes sobre como a busca funciona, opções de ajuste e configuração de provedor, veja
[Memory Search](/pt-BR/concepts/memory-search).

## Backends de memória

<CardGroup cols={3}>
<Card title="Integrado (padrão)" icon="database" href="/pt-BR/concepts/memory-builtin">
Baseado em SQLite. Funciona imediatamente com busca por palavra-chave, similaridade vetorial e
busca híbrida. Sem dependências extras.
</Card>
<Card title="QMD" icon="search" href="/pt-BR/concepts/memory-qmd">
Sidecar local-first com reranqueamento, expansão de consulta e a capacidade de indexar
diretórios fora do workspace.
</Card>
<Card title="Honcho" icon="brain" href="/pt-BR/concepts/memory-honcho">
Memória entre sessões nativa para IA com modelagem de usuário, busca semântica e
consciência de múltiplos agentes. Instalação via Plugin.
</Card>
</CardGroup>

## Camada de wiki de conhecimento

<CardGroup cols={1}>
<Card title="Memory Wiki" icon="book" href="/pt-BR/plugins/memory-wiki">
Compila memória durável em um cofre wiki rico em procedência com afirmações,
painéis, modo bridge e fluxos de trabalho compatíveis com Obsidian.
</Card>
</CardGroup>

## Gravação automática da memória

Antes que a [Compaction](/pt-BR/concepts/compaction) resuma sua conversa, o OpenClaw
executa um turno silencioso que lembra o agente de salvar contexto importante
nos arquivos de memória. Isso vem ativado por padrão -- você não precisa configurar nada.

<Tip>
A gravação da memória evita perda de contexto durante a Compaction. Se seu agente tiver
fatos importantes na conversa que ainda não foram escritos em um arquivo, eles
serão salvos automaticamente antes que o resumo aconteça.
</Tip>

## Dreaming

Dreaming é uma etapa opcional de consolidação em segundo plano para a memória. Ela coleta
sinais de curto prazo, pontua candidatos e promove apenas itens qualificados para a
memória de longo prazo (`MEMORY.md`).

Ela foi projetada para manter a memória de longo prazo com alto sinal:

- **Adesão opcional**: desativado por padrão.
- **Agendado**: quando ativado, `memory-core` gerencia automaticamente um trabalho recorrente de Cron
  para uma varredura completa de Dreaming.
- **Com limiar**: promoções precisam passar por barreiras de pontuação, frequência de recordação e
  diversidade de consultas.
- **Revisável**: resumos de fases e entradas de diário são gravados em `DREAMS.md`
  para revisão humana.

Para comportamento por fase, sinais de pontuação e detalhes do Diário de Sonhos, veja
[Dreaming](/pt-BR/concepts/dreaming).

## Backfill fundamentado e promoção ao vivo

O sistema de Dreaming agora tem dois fluxos de revisão intimamente relacionados:

- **Dreaming ao vivo** funciona a partir do armazenamento de Dreaming de curto prazo em
  `memory/.dreams/` e é o que a fase profunda normal usa ao decidir o que
  pode ser promovido para `MEMORY.md`.
- **Backfill fundamentado** lê notas históricas `memory/YYYY-MM-DD.md` como
  arquivos diários independentes e grava saída estruturada de revisão em `DREAMS.md`.

O backfill fundamentado é útil quando você quer reproduzir notas antigas e inspecionar o que
o sistema considera durável sem editar manualmente o `MEMORY.md`.

Quando você usa:

```bash
openclaw memory rem-backfill --path ./memory --stage-short-term
```

os candidatos duráveis fundamentados não são promovidos diretamente. Eles são colocados em estágio
no mesmo armazenamento de Dreaming de curto prazo que a fase profunda normal já usa. Isso
significa que:

- `DREAMS.md` continua sendo a superfície de revisão humana.
- o armazenamento de curto prazo continua sendo a superfície de ranqueamento voltada à máquina.
- `MEMORY.md` ainda é gravado apenas pela promoção profunda.

Se você decidir que a reprodução não foi útil, poderá remover os artefatos colocados em estágio
sem tocar em entradas normais de diário nem no estado normal de recordação:

```bash
openclaw memory rem-backfill --rollback
openclaw memory rem-backfill --rollback-short-term
```

## CLI

```bash
openclaw memory status          # Verificar status do índice e do provedor
openclaw memory search "query"  # Buscar pela linha de comando
openclaw memory index --force   # Reconstruir o índice
```

## Leitura adicional

- [Builtin Memory Engine](/pt-BR/concepts/memory-builtin) -- backend padrão em SQLite
- [QMD Memory Engine](/pt-BR/concepts/memory-qmd) -- sidecar local-first avançado
- [Honcho Memory](/pt-BR/concepts/memory-honcho) -- memória entre sessões nativa para IA
- [Memory Wiki](/pt-BR/plugins/memory-wiki) -- cofre de conhecimento compilado e ferramentas nativas de wiki
- [Memory Search](/pt-BR/concepts/memory-search) -- pipeline de busca, provedores e
  ajuste
- [Dreaming](/pt-BR/concepts/dreaming) -- promoção em segundo plano
  da recordação de curto prazo para a memória de longo prazo
- [Referência de configuração de memória](/pt-BR/reference/memory-config) -- todas as opções de configuração
- [Compaction](/pt-BR/concepts/compaction) -- como a Compaction interage com a memória
