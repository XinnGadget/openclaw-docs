---
read_when:
    - Você está criando um plugin do OpenClaw
    - Você precisa fornecer um esquema de configuração do plugin ou depurar erros de validação do plugin
summary: Manifesto do plugin + requisitos do esquema JSON (validação estrita de configuração)
title: Manifesto do plugin
x-i18n:
    generated_at: "2026-04-12T05:33:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: bf666b0f41f07641375a248f52e29ba6a68c3ec20404bedb6b52a20a5cd92e91
    source_path: plugins/manifest.md
    workflow: 15
---

# Manifesto do plugin (`openclaw.plugin.json`)

Esta página é apenas para o **manifesto nativo de plugin do OpenClaw**.

Para layouts de bundle compatíveis, veja [Bundles de plugins](/pt-BR/plugins/bundles).

Formatos de bundle compatíveis usam arquivos de manifesto diferentes:

- Bundle do Codex: `.codex-plugin/plugin.json`
- Bundle do Claude: `.claude-plugin/plugin.json` ou o layout padrão de componente do Claude
  sem manifesto
- Bundle do Cursor: `.cursor-plugin/plugin.json`

O OpenClaw também detecta automaticamente esses layouts de bundle, mas eles não são validados
em relação ao esquema `openclaw.plugin.json` descrito aqui.

Para bundles compatíveis, o OpenClaw atualmente lê os metadados do bundle mais as
raízes de skill declaradas, raízes de comando do Claude, padrões `settings.json` do bundle do Claude,
padrões de LSP do bundle do Claude e pacotes de hooks compatíveis quando o layout corresponde
às expectativas de runtime do OpenClaw.

Todo plugin nativo do OpenClaw **deve** fornecer um arquivo `openclaw.plugin.json` na
**raiz do plugin**. O OpenClaw usa esse manifesto para validar a configuração
**sem executar o código do plugin**. Manifestos ausentes ou inválidos são tratados como
erros de plugin e bloqueiam a validação da configuração.

Veja o guia completo do sistema de plugins: [Plugins](/pt-BR/tools/plugin).
Para o modelo nativo de capacidades e a orientação atual de compatibilidade externa:
[Modelo de capacidades](/pt-BR/plugins/architecture#public-capability-model).

## O que esse arquivo faz

`openclaw.plugin.json` são os metadados que o OpenClaw lê antes de carregar o
código do seu plugin.

Use-o para:

- identidade do plugin
- validação de configuração
- metadados de autenticação e onboarding que devem estar disponíveis sem iniciar o
  runtime do plugin
- dicas baratas de ativação que superfícies do plano de controle podem inspecionar antes de o runtime
  carregar
- descritores baratos de configuração que superfícies de configuração/onboarding podem inspecionar antes
  de o runtime carregar
- metadados de alias e autoativação que devem ser resolvidos antes de o runtime do plugin carregar
- metadados abreviados de propriedade de família de modelos que devem autoativar o
  plugin antes de o runtime carregar
- snapshots estáticos de propriedade de capacidades usados para wiring de compatibilidade
  empacotada e cobertura de contrato
- metadados de configuração específicos de canal que devem ser mesclados em superfícies
  de catálogo e validação sem carregar o runtime
- dicas de UI de configuração

Não o use para:

- registrar comportamento de runtime
- declarar entrypoints de código
- metadados de instalação npm

Esses pertencem ao código do seu plugin e ao `package.json`.

## Exemplo mínimo

```json
{
  "id": "voice-call",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

## Exemplo completo

```json
{
  "id": "openrouter",
  "name": "OpenRouter",
  "description": "Plugin de provedor OpenRouter",
  "version": "1.0.0",
  "providers": ["openrouter"],
  "modelSupport": {
    "modelPrefixes": ["router-"]
  },
  "cliBackends": ["openrouter-cli"],
  "providerAuthEnvVars": {
    "openrouter": ["OPENROUTER_API_KEY"]
  },
  "providerAuthAliases": {
    "openrouter-coding": "openrouter"
  },
  "channelEnvVars": {
    "openrouter-chatops": ["OPENROUTER_CHATOPS_TOKEN"]
  },
  "providerAuthChoices": [
    {
      "provider": "openrouter",
      "method": "api-key",
      "choiceId": "openrouter-api-key",
      "choiceLabel": "Chave de API do OpenRouter",
      "groupId": "openrouter",
      "groupLabel": "OpenRouter",
      "optionKey": "openrouterApiKey",
      "cliFlag": "--openrouter-api-key",
      "cliOption": "--openrouter-api-key <key>",
      "cliDescription": "Chave de API do OpenRouter",
      "onboardingScopes": ["text-inference"]
    }
  ],
  "uiHints": {
    "apiKey": {
      "label": "Chave de API",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  },
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "apiKey": {
        "type": "string"
      }
    }
  }
}
```

## Referência de campos de nível superior

| Campo                               | Obrigatório | Tipo                             | O que significa                                                                                                                                                                                              |
| ----------------------------------- | ----------- | -------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `id`                                | Sim         | `string`                         | ID canônico do plugin. Esse é o ID usado em `plugins.entries.<id>`.                                                                                                                                         |
| `configSchema`                      | Sim         | `object`                         | Esquema JSON inline para a configuração deste plugin.                                                                                                                                                        |
| `enabledByDefault`                  | Não         | `true`                           | Marca um plugin empacotado como habilitado por padrão. Omita-o, ou defina qualquer valor diferente de `true`, para manter o plugin desabilitado por padrão.                                              |
| `legacyPluginIds`                   | Não         | `string[]`                       | IDs legados que são normalizados para este ID canônico de plugin.                                                                                                                                            |
| `autoEnableWhenConfiguredProviders` | Não         | `string[]`                       | IDs de provedores que devem autoativar este plugin quando autenticação, configuração ou referências de modelo os mencionarem.                                                                               |
| `kind`                              | Não         | `"memory"` \| `"context-engine"` | Declara um tipo exclusivo de plugin usado por `plugins.slots.*`.                                                                                                                                             |
| `channels`                          | Não         | `string[]`                       | IDs de canais pertencentes a este plugin. Usado para descoberta e validação de configuração.                                                                                                                |
| `providers`                         | Não         | `string[]`                       | IDs de provedores pertencentes a este plugin.                                                                                                                                                                |
| `modelSupport`                      | Não         | `object`                         | Metadados abreviados de família de modelos pertencentes ao manifesto usados para autocarregar o plugin antes do runtime.                                                                                   |
| `cliBackends`                       | Não         | `string[]`                       | IDs de backend de inferência da CLI pertencentes a este plugin. Usado para autoativação na inicialização a partir de referências explícitas de configuração.                                              |
| `commandAliases`                    | Não         | `object[]`                       | Nomes de comando pertencentes a este plugin que devem produzir diagnósticos de configuração e CLI com reconhecimento de plugin antes de o runtime carregar.                                                |
| `providerAuthEnvVars`               | Não         | `Record<string, string[]>`       | Metadados leves de variáveis de ambiente de autenticação do provedor que o OpenClaw pode inspecionar sem carregar o código do plugin.                                                                      |
| `providerAuthAliases`               | Não         | `Record<string, string>`         | IDs de provedores que devem reutilizar outro ID de provedor para busca de autenticação, por exemplo um provedor de código que compartilha a chave de API e os perfis de autenticação do provedor base.    |
| `channelEnvVars`                    | Não         | `Record<string, string[]>`       | Metadados leves de variáveis de ambiente de canal que o OpenClaw pode inspecionar sem carregar o código do plugin. Use isso para superfícies de configuração ou autenticação de canal baseadas em env que helpers genéricos de inicialização/configuração devem enxergar. |
| `providerAuthChoices`               | Não         | `object[]`                       | Metadados leves de escolha de autenticação para seletores de onboarding, resolução de provedor preferencial e wiring simples de flags da CLI.                                                              |
| `activation`                        | Não         | `object`                         | Dicas leves de ativação para carregamento disparado por provedor, comando, canal, rota e capacidade. Apenas metadados; o runtime do plugin ainda é dono do comportamento real.                            |
| `setup`                             | Não         | `object`                         | Descritores leves de configuração/onboarding que superfícies de descoberta e configuração podem inspecionar sem carregar o runtime do plugin.                                                               |
| `contracts`                         | Não         | `object`                         | Snapshot estático de capacidades empacotadas para fala, transcrição em tempo real, voz em tempo real, compreensão de mídia, geração de imagem, geração de música, geração de vídeo, web-fetch, pesquisa na web e propriedade de ferramentas. |
| `channelConfigs`                    | Não         | `Record<string, object>`         | Metadados de configuração de canal pertencentes ao manifesto, mesclados em superfícies de descoberta e validação antes de o runtime carregar.                                                              |
| `skills`                            | Não         | `string[]`                       | Diretórios de Skills a carregar, relativos à raiz do plugin.                                                                                                                                                 |
| `name`                              | Não         | `string`                         | Nome legível do plugin.                                                                                                                                                                                      |
| `description`                       | Não         | `string`                         | Resumo curto mostrado nas superfícies do plugin.                                                                                                                                                             |
| `version`                           | Não         | `string`                         | Versão informativa do plugin.                                                                                                                                                                                |
| `uiHints`                           | Não         | `Record<string, object>`         | Rótulos de UI, placeholders e dicas de sensibilidade para campos de configuração.                                                                                                                            |

## Referência de `providerAuthChoices`

Cada entrada de `providerAuthChoices` descreve uma escolha de onboarding ou autenticação.
O OpenClaw lê isso antes de o runtime do provedor carregar.

| Campo                 | Obrigatório | Tipo                                            | O que significa                                                                                          |
| --------------------- | ----------- | ----------------------------------------------- | -------------------------------------------------------------------------------------------------------- |
| `provider`            | Sim         | `string`                                        | ID do provedor ao qual esta escolha pertence.                                                            |
| `method`              | Sim         | `string`                                        | ID do método de autenticação para o qual encaminhar.                                                     |
| `choiceId`            | Sim         | `string`                                        | ID estável de escolha de autenticação usado por fluxos de onboarding e da CLI.                          |
| `choiceLabel`         | Não         | `string`                                        | Rótulo voltado ao usuário. Se omitido, o OpenClaw usa `choiceId` como fallback.                         |
| `choiceHint`          | Não         | `string`                                        | Texto curto de ajuda para o seletor.                                                                     |
| `assistantPriority`   | Não         | `number`                                        | Valores menores aparecem primeiro em seletores interativos conduzidos pelo assistente.                  |
| `assistantVisibility` | Não         | `"visible"` \| `"manual-only"`                  | Oculta a escolha dos seletores do assistente, mas ainda permite seleção manual pela CLI.                |
| `deprecatedChoiceIds` | Não         | `string[]`                                      | IDs legados de escolha que devem redirecionar os usuários para esta escolha de substituição.            |
| `groupId`             | Não         | `string`                                        | ID de grupo opcional para agrupar escolhas relacionadas.                                                 |
| `groupLabel`          | Não         | `string`                                        | Rótulo voltado ao usuário para esse grupo.                                                               |
| `groupHint`           | Não         | `string`                                        | Texto curto de ajuda para o grupo.                                                                       |
| `optionKey`           | Não         | `string`                                        | Chave interna de opção para fluxos simples de autenticação com uma única flag.                           |
| `cliFlag`             | Não         | `string`                                        | Nome da flag da CLI, como `--openrouter-api-key`.                                                        |
| `cliOption`           | Não         | `string`                                        | Formato completo da opção da CLI, como `--openrouter-api-key <key>`.                                     |
| `cliDescription`      | Não         | `string`                                        | Descrição usada na ajuda da CLI.                                                                         |
| `onboardingScopes`    | Não         | `Array<"text-inference" \| "image-generation">` | Em quais superfícies de onboarding esta escolha deve aparecer. Se omitido, o padrão é `["text-inference"]`. |

## Referência de `commandAliases`

Use `commandAliases` quando um plugin é dono de um nome de comando de runtime que os usuários podem
colocar por engano em `plugins.allow` ou tentar executar como um comando raiz da CLI. O OpenClaw
usa esses metadados para diagnósticos sem importar o código de runtime do plugin.

```json
{
  "commandAliases": [
    {
      "name": "dreaming",
      "kind": "runtime-slash",
      "cliCommand": "memory"
    }
  ]
}
```

| Campo        | Obrigatório | Tipo              | O que significa                                                           |
| ------------ | ----------- | ----------------- | ------------------------------------------------------------------------- |
| `name`       | Sim         | `string`          | Nome do comando que pertence a este plugin.                               |
| `kind`       | Não         | `"runtime-slash"` | Marca o alias como um comando slash de chat em vez de um comando raiz da CLI. |
| `cliCommand` | Não         | `string`          | Comando raiz relacionado da CLI a ser sugerido para operações da CLI, se existir. |

## Referência de `activation`

Use `activation` quando o plugin puder declarar de forma leve quais eventos do plano de controle
devem ativá-lo depois.

Esse bloco é apenas metadados. Ele não registra comportamento de runtime e não
substitui `register(...)`, `setupEntry` nem outros entrypoints de runtime/plugin.

```json
{
  "activation": {
    "onProviders": ["openai"],
    "onCommands": ["models"],
    "onChannels": ["web"],
    "onRoutes": ["gateway-webhook"],
    "onCapabilities": ["provider", "tool"]
  }
}
```

| Campo            | Obrigatório | Tipo                                                 | O que significa                                                     |
| ---------------- | ----------- | ---------------------------------------------------- | ------------------------------------------------------------------- |
| `onProviders`    | Não         | `string[]`                                           | IDs de provedores que devem ativar este plugin quando solicitados.  |
| `onCommands`     | Não         | `string[]`                                           | IDs de comandos que devem ativar este plugin.                       |
| `onChannels`     | Não         | `string[]`                                           | IDs de canais que devem ativar este plugin.                         |
| `onRoutes`       | Não         | `string[]`                                           | Tipos de rota que devem ativar este plugin.                         |
| `onCapabilities` | Não         | `Array<"provider" \| "channel" \| "tool" \| "hook">` | Dicas amplas de capacidade usadas pelo planejamento de ativação do plano de controle. |

## Referência de `setup`

Use `setup` quando superfícies de configuração e onboarding precisarem de metadados leves pertencentes ao plugin
antes de o runtime carregar.

```json
{
  "setup": {
    "providers": [
      {
        "id": "openai",
        "authMethods": ["api-key"],
        "envVars": ["OPENAI_API_KEY"]
      }
    ],
    "cliBackends": ["openai-cli"],
    "configMigrations": ["legacy-openai-auth"],
    "requiresRuntime": false
  }
}
```

O `cliBackends` de nível superior continua válido e segue descrevendo backends
de inferência da CLI. `setup.cliBackends` é a superfície de descritor específica de configuração para
fluxos do plano de controle/configuração que devem permanecer apenas como metadados.

Quando presentes, `setup.providers` e `setup.cliBackends` são a superfície preferencial
baseada em descritores para busca de configuração. Se o descritor apenas restringir
o plugin candidato e a configuração ainda precisar de hooks de runtime mais ricos no momento da configuração,
defina `requiresRuntime: true` e mantenha `setup-api` como caminho de execução
de fallback.

Como a busca de configuração pode executar código `setup-api` pertencente ao plugin, os valores normalizados de
`setup.providers[].id` e `setup.cliBackends[]` devem permanecer exclusivos entre
os plugins descobertos. Propriedade ambígua falha de forma fechada em vez de escolher
um vencedor com base na ordem de descoberta.

### Referência de `setup.providers`

| Campo         | Obrigatório | Tipo       | O que significa                                                                      |
| ------------- | ----------- | ---------- | ------------------------------------------------------------------------------------ |
| `id`          | Sim         | `string`   | ID do provedor exposto durante a configuração ou onboarding. Mantenha IDs normalizados globalmente exclusivos. |
| `authMethods` | Não         | `string[]` | IDs de métodos de configuração/autenticação que este provedor oferece sem carregar o runtime completo. |
| `envVars`     | Não         | `string[]` | Variáveis de ambiente que superfícies genéricas de configuração/status podem verificar antes de o runtime do plugin carregar. |

### Campos de `setup`

| Campo              | Obrigatório | Tipo       | O que significa                                                                                     |
| ------------------ | ----------- | ---------- | --------------------------------------------------------------------------------------------------- |
| `providers`        | Não         | `object[]` | Descritores de configuração de provedor expostos durante a configuração e o onboarding.            |
| `cliBackends`      | Não         | `string[]` | IDs de backend em tempo de configuração usados para busca de configuração com base em descritor primeiro. Mantenha IDs normalizados globalmente exclusivos. |
| `configMigrations` | Não         | `string[]` | IDs de migração de configuração pertencentes à superfície de configuração deste plugin.             |
| `requiresRuntime`  | Não         | `boolean`  | Se a configuração ainda precisa da execução de `setup-api` após a busca por descritor.             |

## Referência de `uiHints`

`uiHints` é um mapa dos nomes de campos de configuração para pequenas dicas de renderização.

```json
{
  "uiHints": {
    "apiKey": {
      "label": "Chave de API",
      "help": "Usada para solicitações do OpenRouter",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  }
}
```

Cada dica de campo pode incluir:

| Campo         | Tipo       | O que significa                          |
| ------------- | ---------- | ---------------------------------------- |
| `label`       | `string`   | Rótulo do campo voltado ao usuário.      |
| `help`        | `string`   | Texto curto de ajuda.                    |
| `tags`        | `string[]` | Tags opcionais de UI.                    |
| `advanced`    | `boolean`  | Marca o campo como avançado.             |
| `sensitive`   | `boolean`  | Marca o campo como secreto ou sensível.  |
| `placeholder` | `string`   | Texto de placeholder para entradas de formulário. |

## Referência de `contracts`

Use `contracts` apenas para metadados estáticos de propriedade de capacidades que o OpenClaw pode
ler sem importar o runtime do plugin.

```json
{
  "contracts": {
    "speechProviders": ["openai"],
    "realtimeTranscriptionProviders": ["openai"],
    "realtimeVoiceProviders": ["openai"],
    "mediaUnderstandingProviders": ["openai", "openai-codex"],
    "imageGenerationProviders": ["openai"],
    "videoGenerationProviders": ["qwen"],
    "webFetchProviders": ["firecrawl"],
    "webSearchProviders": ["gemini"],
    "tools": ["firecrawl_search", "firecrawl_scrape"]
  }
}
```

Cada lista é opcional:

| Campo                            | Tipo       | O que significa                                              |
| -------------------------------- | ---------- | ------------------------------------------------------------ |
| `speechProviders`                | `string[]` | IDs de provedores de fala pertencentes a este plugin.        |
| `realtimeTranscriptionProviders` | `string[]` | IDs de provedores de transcrição em tempo real pertencentes a este plugin. |
| `realtimeVoiceProviders`         | `string[]` | IDs de provedores de voz em tempo real pertencentes a este plugin. |
| `mediaUnderstandingProviders`    | `string[]` | IDs de provedores de compreensão de mídia pertencentes a este plugin. |
| `imageGenerationProviders`       | `string[]` | IDs de provedores de geração de imagem pertencentes a este plugin. |
| `videoGenerationProviders`       | `string[]` | IDs de provedores de geração de vídeo pertencentes a este plugin. |
| `webFetchProviders`              | `string[]` | IDs de provedores de web-fetch pertencentes a este plugin.   |
| `webSearchProviders`             | `string[]` | IDs de provedores de pesquisa na web pertencentes a este plugin. |
| `tools`                          | `string[]` | Nomes de ferramentas do agente pertencentes a este plugin para verificações de contrato empacotadas. |

## Referência de `channelConfigs`

Use `channelConfigs` quando um plugin de canal precisar de metadados leves de configuração antes de o
runtime carregar.

```json
{
  "channelConfigs": {
    "matrix": {
      "schema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "homeserverUrl": { "type": "string" }
        }
      },
      "uiHints": {
        "homeserverUrl": {
          "label": "URL do homeserver",
          "placeholder": "https://matrix.example.com"
        }
      },
      "label": "Matrix",
      "description": "Conexão com o homeserver Matrix",
      "preferOver": ["matrix-legacy"]
    }
  }
}
```

Cada entrada de canal pode incluir:

| Campo         | Tipo                     | O que significa                                                                        |
| ------------- | ------------------------ | -------------------------------------------------------------------------------------- |
| `schema`      | `object`                 | Esquema JSON para `channels.<id>`. Obrigatório para cada entrada declarada de configuração de canal. |
| `uiHints`     | `Record<string, object>` | Rótulos/placeholders/dicas de sensibilidade de UI opcionais para essa seção de configuração de canal. |
| `label`       | `string`                 | Rótulo do canal mesclado em superfícies de seletor e inspeção quando os metadados de runtime ainda não estiverem prontos. |
| `description` | `string`                 | Descrição curta do canal para superfícies de inspeção e catálogo.                      |
| `preferOver`  | `string[]`               | IDs de plugin legados ou de menor prioridade que este canal deve superar em superfícies de seleção. |

## Referência de `modelSupport`

Use `modelSupport` quando o OpenClaw precisar inferir seu plugin de provedor a partir de
IDs abreviados de modelo, como `gpt-5.4` ou `claude-sonnet-4.6`, antes de o runtime do plugin
carregar.

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

O OpenClaw aplica esta precedência:

- referências explícitas `provider/model` usam os metadados de manifesto `providers` do plugin proprietário
- `modelPatterns` têm precedência sobre `modelPrefixes`
- se um plugin não empacotado e um plugin empacotado corresponderem ao mesmo tempo, o plugin não empacotado
  vence
- a ambiguidade restante é ignorada até que o usuário ou a configuração especifique um provedor

Campos:

| Campo           | Tipo       | O que significa                                                                  |
| --------------- | ---------- | -------------------------------------------------------------------------------- |
| `modelPrefixes` | `string[]` | Prefixos correspondidos com `startsWith` em IDs abreviados de modelo.           |
| `modelPatterns` | `string[]` | Fontes de regex correspondidas em IDs abreviados de modelo após a remoção do sufixo de perfil. |

Chaves legadas de capacidade no nível superior estão obsoletas. Use `openclaw doctor --fix` para
mover `speechProviders`, `realtimeTranscriptionProviders`,
`realtimeVoiceProviders`, `mediaUnderstandingProviders`,
`imageGenerationProviders`, `videoGenerationProviders`,
`webFetchProviders` e `webSearchProviders` para `contracts`; o carregamento normal
do manifesto não trata mais esses campos de nível superior como propriedade
de capacidades.

## Manifesto versus package.json

Os dois arquivos têm funções diferentes:

| Arquivo                | Use para                                                                                                                             |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| `openclaw.plugin.json` | Descoberta, validação de configuração, metadados de escolha de autenticação e dicas de UI que devem existir antes de o código do plugin executar |
| `package.json`         | Metadados npm, instalação de dependências e o bloco `openclaw` usado para entrypoints, controle de instalação, configuração ou metadados de catálogo |

Se você não tiver certeza de onde um metadado pertence, use esta regra:

- se o OpenClaw precisa conhecê-lo antes de carregar o código do plugin, coloque-o em `openclaw.plugin.json`
- se for sobre empacotamento, arquivos de entrada ou comportamento de instalação do npm, coloque-o em `package.json`

### Campos de `package.json` que afetam a descoberta

Alguns metadados de plugin pré-runtime intencionalmente ficam em `package.json` no bloco
`openclaw`, em vez de `openclaw.plugin.json`.

Exemplos importantes:

| Campo                                                             | O que significa                                                                                                                              |
| ----------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | Declara entrypoints de plugin nativo.                                                                                                        |
| `openclaw.setupEntry`                                             | Entrypoint leve apenas de configuração usado durante onboarding e inicialização adiada de canal.                                             |
| `openclaw.channel`                                                | Metadados leves de catálogo de canal, como rótulos, caminhos de documentação, aliases e texto de seleção.                                  |
| `openclaw.channel.configuredState`                                | Metadados leves do verificador de estado configurado que podem responder "já existe configuração somente por env?" sem carregar o runtime completo do canal. |
| `openclaw.channel.persistedAuthState`                             | Metadados leves do verificador de autenticação persistida que podem responder "já existe algo autenticado?" sem carregar o runtime completo do canal. |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | Dicas de instalação/atualização para plugins empacotados e publicados externamente.                                                         |
| `openclaw.install.defaultChoice`                                  | Caminho de instalação preferido quando várias fontes de instalação estão disponíveis.                                                        |
| `openclaw.install.minHostVersion`                                 | Versão mínima suportada do host OpenClaw, usando um piso semver como `>=2026.3.22`.                                                         |
| `openclaw.install.allowInvalidConfigRecovery`                     | Permite um caminho restrito de recuperação por reinstalação de plugin empacotado quando a configuração é inválida.                          |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | Permite que superfícies de canal apenas de configuração carreguem antes do plugin de canal completo durante a inicialização.                |

`openclaw.install.minHostVersion` é aplicado durante a instalação e o carregamento do registro
de manifestos. Valores inválidos são rejeitados; valores válidos, mas mais novos, ignoram o
plugin em hosts mais antigos.

`openclaw.install.allowInvalidConfigRecovery` é intencionalmente restrito. Ele não torna
instaláveis configurações arbitrariamente quebradas. Hoje, ele apenas permite que fluxos de instalação
se recuperem de falhas específicas e obsoletas de atualização de plugin empacotado, como um
caminho ausente do plugin empacotado ou uma entrada `channels.<id>` obsoleta para esse mesmo
plugin empacotado. Erros de configuração não relacionados ainda bloqueiam a instalação e enviam os
operadores para `openclaw doctor --fix`.

`openclaw.channel.persistedAuthState` é um metadado de pacote para um módulo verificador
mínimo:

```json
{
  "openclaw": {
    "channel": {
      "id": "whatsapp",
      "persistedAuthState": {
        "specifier": "./auth-presence",
        "exportName": "hasAnyWhatsAppAuth"
      }
    }
  }
}
```

Use isso quando fluxos de configuração, doctor ou estado configurado precisarem de uma sondagem barata
de autenticação sim/não antes de o plugin completo do canal carregar. A exportação de destino deve ser uma função
pequena que leia apenas o estado persistido; não a encaminhe pelo barrel completo do runtime do
canal.

`openclaw.channel.configuredState` segue o mesmo formato para verificações leves de estado
configurado somente por env:

```json
{
  "openclaw": {
    "channel": {
      "id": "telegram",
      "configuredState": {
        "specifier": "./configured-state",
        "exportName": "hasTelegramConfiguredState"
      }
    }
  }
}
```

Use isso quando um canal puder responder ao estado configurado a partir de env ou de outras entradas
mínimas não ligadas ao runtime. Se a verificação precisar da resolução completa da configuração ou do runtime
real do canal, mantenha essa lógica no hook `config.hasConfiguredState` do plugin.

## Requisitos do esquema JSON

- **Todo plugin deve fornecer um esquema JSON**, mesmo que não aceite configuração.
- Um esquema vazio é aceitável (por exemplo, `{ "type": "object", "additionalProperties": false }`).
- Os esquemas são validados no momento de leitura/gravação da configuração, não em runtime.

## Comportamento de validação

- Chaves desconhecidas em `channels.*` são **erros**, a menos que o ID do canal seja declarado por
  um manifesto de plugin.
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny` e `plugins.slots.*`
  devem referenciar IDs de plugin **detectáveis**. IDs desconhecidos são **erros**.
- Se um plugin estiver instalado, mas tiver um manifesto ou esquema ausente ou quebrado,
  a validação falhará e o Doctor reportará o erro do plugin.
- Se existir configuração de plugin, mas o plugin estiver **desabilitado**, a configuração será mantida e
  um **aviso** será exibido no Doctor + logs.

Veja [Referência de configuração](/pt-BR/gateway/configuration) para o esquema completo de `plugins.*`.

## Observações

- O manifesto é **obrigatório para plugins nativos do OpenClaw**, incluindo carregamentos locais do sistema de arquivos.
- O runtime ainda carrega o módulo do plugin separadamente; o manifesto serve apenas para
  descoberta + validação.
- Manifestos nativos são analisados com JSON5, então comentários, vírgulas à direita e
  chaves sem aspas são aceitos, contanto que o valor final continue sendo um objeto.
- Apenas campos documentados do manifesto são lidos pelo carregador de manifestos. Evite adicionar
  chaves personalizadas de nível superior aqui.
- `providerAuthEnvVars` é o caminho leve de metadados para sondagens de autenticação, validação de marcadores de env
  e superfícies semelhantes de autenticação de provedor que não devem iniciar o runtime do plugin
  apenas para inspecionar nomes de env.
- `providerAuthAliases` permite que variantes de provedor reutilizem as variáveis de ambiente de autenticação de outro provedor,
  perfis de autenticação, autenticação baseada em configuração e escolha de onboarding de chave de API
  sem codificar esse relacionamento no core.
- `channelEnvVars` é o caminho leve de metadados para fallback de env do shell, prompts de configuração
  e superfícies semelhantes de canal que não devem iniciar o runtime do plugin
  apenas para inspecionar nomes de env.
- `providerAuthChoices` é o caminho leve de metadados para seletores de escolha de autenticação,
  resolução de `--auth-choice`, mapeamento de provedor preferencial e registro simples
  de flags de CLI de onboarding antes de o runtime do provedor carregar. Para metadados
  de assistente de runtime que exigem código do provedor, veja
  [Hooks de runtime do provedor](/pt-BR/plugins/architecture#provider-runtime-hooks).
- Tipos exclusivos de plugin são selecionados por meio de `plugins.slots.*`.
  - `kind: "memory"` é selecionado por `plugins.slots.memory`.
  - `kind: "context-engine"` é selecionado por `plugins.slots.contextEngine`
    (padrão: `legacy` embutido).
- `channels`, `providers`, `cliBackends` e `skills` podem ser omitidos quando um
  plugin não precisar deles.
- Se seu plugin depender de módulos nativos, documente as etapas de build e quaisquer
  requisitos de allowlist do gerenciador de pacotes (por exemplo, pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`).

## Relacionado

- [Criando Plugins](/pt-BR/plugins/building-plugins) — introdução a plugins
- [Arquitetura de Plugins](/pt-BR/plugins/architecture) — arquitetura interna
- [Visão geral do SDK](/pt-BR/plugins/sdk-overview) — referência do SDK de Plugins
