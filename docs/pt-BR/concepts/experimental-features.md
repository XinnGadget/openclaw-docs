---
read_when:
    - Você vê uma chave de configuração `.experimental` e quer saber se ela é estável
    - Você quer experimentar recursos de runtime em prévia sem confundi-los com os padrões normais
    - Você quer um lugar único para encontrar as flags experimentais documentadas atualmente
summary: O que significam as flags experimentais no OpenClaw e quais estão documentadas atualmente?
title: Recursos experimentais
x-i18n:
    generated_at: "2026-04-15T14:40:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2d1c7b3d4cd56ef8a0bdab1deb9918e9b2c9a33f956d63193246087f8633dcf3
    source_path: concepts/experimental-features.md
    workflow: 15
---

# Recursos experimentais

Os recursos experimentais no OpenClaw são **superfícies de prévia com ativação opcional**. Eles ficam
atrás de flags explícitas porque ainda precisam de uso no mundo real antes de
merecerem um padrão estável ou um contrato público de longa duração.

Trate-os de forma diferente da configuração normal:

- Mantenha-os **desativados por padrão** a menos que a documentação relacionada diga para você testar algum.
- Espere que a **estrutura e o comportamento mudem** mais rapidamente do que na configuração estável.
- Prefira primeiro o caminho estável quando ele já existir.
- Se você estiver implantando o OpenClaw amplamente, teste as flags experimentais em um ambiente menor
  antes de incorporá-las a uma baseline compartilhada.

## Flags documentadas atualmente

| Superfície               | Chave                                                     | Use quando                                                                                                     | Mais                                                                                          |
| ------------------------ | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Runtime de modelo local  | `agents.defaults.experimental.localModelLean`             | Um backend local menor ou mais rígido engasga com toda a superfície de ferramentas padrão do OpenClaw         | [Modelos locais](/pt-BR/gateway/local-models)                                                       |
| Busca de memória         | `agents.defaults.memorySearch.experimental.sessionMemory` | Você quer que `memory_search` indexe transcrições de sessões anteriores e aceita o custo extra de armazenamento/indexação | [Referência de configuração de memória](/pt-BR/reference/memory-config#session-memory-search-experimental) |
| Ferramenta de planejamento estruturado | `tools.experimental.planTool`                             | Você quer a ferramenta estruturada `update_plan` exposta para acompanhamento de trabalho em várias etapas em runtimes e UIs compatíveis | [Referência de configuração do Gateway](/pt-BR/gateway/configuration-reference#toolsexperimental)         |

## Modo enxuto para modelo local

`agents.defaults.experimental.localModelLean: true` é uma válvula de alívio
para configurações de modelo local mais fracas. Ele reduz ferramentas padrão
mais pesadas, como `browser`, `cron` e `message`, para que o formato do prompt seja menor e menos frágil
para backends compatíveis com OpenAI com contexto pequeno ou mais rígidos.

Esse **não** é intencionalmente o caminho normal. Se o seu backend lida bem com o
runtime completo, deixe isso desativado.

## Experimental não significa oculto

Se um recurso é experimental, o OpenClaw deve dizer isso claramente na documentação e no
próprio caminho de configuração. O que ele **não** deve fazer é introduzir comportamento de prévia
em um controle de aparência estável e fingir que isso é normal. É assim que
as superfícies de configuração ficam bagunçadas.
