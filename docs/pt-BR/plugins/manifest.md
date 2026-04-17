---
read_when:
    - Você está criando um Plugin do OpenClaw
    - Você precisa entregar um esquema de configuração de Plugin ou depurar erros de validação de Plugin
summary: Manifesto do Plugin + requisitos do esquema JSON (validação estrita de configuração)
title: Manifesto do Plugin
x-i18n:
    generated_at: "2026-04-15T05:33:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: ba2183bfa8802871e4ef33a0ebea290606e8351e9e83e25ee72456addb768730
    source_path: plugins/manifest.md
    workflow: 15
---

# Manifesto do Plugin (`openclaw.plugin.json`)

Esta página é apenas para o **manifesto de Plugin nativo do OpenClaw**.

Para layouts de bundle compatíveis, consulte [Bundles de Plugin](/pt-BR/plugins/bundles).

Formatos de bundle compatíveis usam arquivos de manifesto diferentes:

- Bundle do Codex: `.codex-plugin/plugin.json`
- Bundle do Claude: `.claude-plugin/plugin.json` ou o layout de componente padrão do Claude sem manifesto
- Bundle do Cursor: `.cursor-plugin/plugin.json`

O OpenClaw também detecta automaticamente esses layouts de bundle, mas eles não são validados em relação ao esquema `openclaw.plugin.json` descrito aqui.

Para bundles compatíveis, o OpenClaw atualmente lê os metadados do bundle mais as raízes de Skills declaradas, raízes de comandos do Claude, padrões de `settings.json` do bundle do Claude, padrões de LSP do bundle do Claude e pacotes de hooks compatíveis quando o layout corresponde às expectativas de runtime do OpenClaw.

Todo Plugin nativo do OpenClaw **deve** incluir um arquivo `openclaw.plugin.json` na **raiz do Plugin**. O OpenClaw usa esse manifesto para validar a configuração **sem executar código do Plugin**. Manifestos ausentes ou inválidos são tratados como erros de Plugin e bloqueiam a validação da configuração.

Consulte o guia completo do sistema de plugins: [Plugins](/pt-BR/tools/plugin).
Para o modelo nativo de capacidades e a orientação atual de compatibilidade externa:
[Modelo de capacidades](/pt-BR/plugins/architecture#public-capability-model).

## O que este arquivo faz

`openclaw.plugin.json` é o metadado que o OpenClaw lê antes de carregar o código do seu Plugin.

Use-o para:

- identidade do Plugin
- validação de configuração
- metadados de autenticação e onboarding que devem estar disponíveis sem iniciar o runtime do Plugin
- dicas baratas de ativação que superfícies do plano de controle podem inspecionar antes de o runtime carregar
- descritores baratos de configuração que superfícies de configuração/onboarding podem inspecionar antes de o runtime carregar
- metadados de alias e autoativação que devem ser resolvidos antes de o runtime do Plugin carregar
- metadados abreviados de propriedade de família de modelos que devem autoativar o Plugin antes de o runtime carregar
- snapshots estáticos de propriedade de capacidades usados para wiring de compatibilidade de bundles e cobertura de contratos
- metadados baratos do executor de QA que o host compartilhado `openclaw qa` pode inspecionar antes de o runtime do Plugin carregar
- metadados de configuração específicos de canal que devem ser mesclados em superfícies de catálogo e validação sem carregar o runtime
- dicas de UI de configuração

Não o use para:

- registrar comportamento de runtime
- declarar entrypoints de código
- metadados de instalação npm

Esses pertencem ao código do seu Plugin e ao `package.json`.

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
  "description": "OpenRouter provider plugin",
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
      "choiceLabel": "OpenRouter API key",
      "groupId": "openrouter",
      "groupLabel": "OpenRouter",
      "optionKey": "openrouterApiKey",
      "cliFlag": "--openrouter-api-key",
      "cliOption": "--openrouter-api-key <key>",
      "cliDescription": "OpenRouter API key",
      "onboardingScopes": ["text-inference"]
    }
  ],
  "uiHints": {
    "apiKey": {
      "label": "API key",
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
| `id`                                | Sim         | `string`                         | ID canônico do Plugin. Este é o ID usado em `plugins.entries.<id>`.                                                                                                                                         |
| `configSchema`                      | Sim         | `object`                         | Esquema JSON inline para a configuração deste Plugin.                                                                                                                                                        |
| `enabledByDefault`                  | Não         | `true`                           | Marca um Plugin empacotado como habilitado por padrão. Omita-o, ou defina qualquer valor diferente de `true`, para deixar o Plugin desabilitado por padrão.                                               |
| `legacyPluginIds`                   | Não         | `string[]`                       | IDs legados que são normalizados para este ID canônico de Plugin.                                                                                                                                            |
| `autoEnableWhenConfiguredProviders` | Não         | `string[]`                       | IDs de provider que devem autoabilitar este Plugin quando autenticação, configuração ou referências de modelo os mencionarem.                                                                               |
| `kind`                              | Não         | `"memory"` \| `"context-engine"` | Declara um tipo exclusivo de Plugin usado por `plugins.slots.*`.                                                                                                                                            |
| `channels`                          | Não         | `string[]`                       | IDs de canal pertencentes a este Plugin. Usado para descoberta e validação de configuração.                                                                                                                 |
| `providers`                         | Não         | `string[]`                       | IDs de provider pertencentes a este Plugin.                                                                                                                                                                  |
| `modelSupport`                      | Não         | `object`                         | Metadados abreviados de família de modelos pertencentes ao manifesto usados para carregar automaticamente o Plugin antes do runtime.                                                                        |
| `cliBackends`                       | Não         | `string[]`                       | IDs de backend de inferência da CLI pertencentes a este Plugin. Usado para autoativação na inicialização a partir de referências explícitas de configuração.                                               |
| `commandAliases`                    | Não         | `object[]`                       | Nomes de comando pertencentes a este Plugin que devem produzir configuração e diagnósticos de CLI cientes do Plugin antes de o runtime carregar.                                                           |
| `providerAuthEnvVars`               | Não         | `Record<string, string[]>`       | Metadados baratos de variáveis de ambiente para autenticação de provider que o OpenClaw pode inspecionar sem carregar o código do Plugin.                                                                  |
| `providerAuthAliases`               | Não         | `Record<string, string>`         | IDs de provider que devem reutilizar outro ID de provider para busca de autenticação, por exemplo, um provider de coding que compartilha a chave de API e os perfis de autenticação do provider base.    |
| `channelEnvVars`                    | Não         | `Record<string, string[]>`       | Metadados baratos de variáveis de ambiente de canal que o OpenClaw pode inspecionar sem carregar o código do Plugin. Use isso para superfícies de configuração ou autenticação de canal orientadas por env que helpers genéricos de inicialização/configuração devem enxergar. |
| `providerAuthChoices`               | Não         | `object[]`                       | Metadados baratos de opções de autenticação para seletores de onboarding, resolução de provider preferido e wiring simples de flags da CLI.                                                                |
| `activation`                        | Não         | `object`                         | Dicas baratas de ativação para carregamento acionado por provider, comando, canal, rota e capacidade. Apenas metadados; o runtime do Plugin ainda é dono do comportamento real.                           |
| `setup`                             | Não         | `object`                         | Descritores baratos de configuração/onboarding que superfícies de descoberta e configuração podem inspecionar sem carregar o runtime do Plugin.                                                            |
| `qaRunners`                         | Não         | `object[]`                       | Descritores baratos de executores de QA usados pelo host compartilhado `openclaw qa` antes de o runtime do Plugin carregar.                                                                                |
| `contracts`                         | Não         | `object`                         | Snapshot estático de capacidades empacotadas para fala, transcrição em tempo real, voz em tempo real, media-understanding, image-generation, music-generation, video-generation, web-fetch, busca na web e propriedade de ferramentas. |
| `channelConfigs`                    | Não         | `Record<string, object>`         | Metadados de configuração de canal pertencentes ao manifesto, mesclados em superfícies de descoberta e validação antes de o runtime carregar.                                                              |
| `skills`                            | Não         | `string[]`                       | Diretórios de Skills a serem carregados, relativos à raiz do Plugin.                                                                                                                                        |
| `name`                              | Não         | `string`                         | Nome legível do Plugin.                                                                                                                                                                                      |
| `description`                       | Não         | `string`                         | Resumo curto exibido em superfícies de Plugin.                                                                                                                                                               |
| `version`                           | Não         | `string`                         | Versão informativa do Plugin.                                                                                                                                                                                |
| `uiHints`                           | Não         | `Record<string, object>`         | Rótulos de UI, placeholders e dicas de sensibilidade para campos de configuração.                                                                                                                            |

## Referência de `providerAuthChoices`

Cada entrada de `providerAuthChoices` descreve uma opção de onboarding ou autenticação.
O OpenClaw lê isso antes de o runtime do provider carregar.

| Campo                 | Obrigatório | Tipo                                            | O que significa                                                                                           |
| --------------------- | ----------- | ----------------------------------------------- | --------------------------------------------------------------------------------------------------------- |
| `provider`            | Sim         | `string`                                        | ID do provider ao qual esta opção pertence.                                                               |
| `method`              | Sim         | `string`                                        | ID do método de autenticação para despacho.                                                               |
| `choiceId`            | Sim         | `string`                                        | ID estável da opção de autenticação usado por fluxos de onboarding e CLI.                                |
| `choiceLabel`         | Não         | `string`                                        | Rótulo voltado ao usuário. Se omitido, o OpenClaw usa `choiceId` como fallback.                          |
| `choiceHint`          | Não         | `string`                                        | Texto auxiliar curto para o seletor.                                                                      |
| `assistantPriority`   | Não         | `number`                                        | Valores menores são ordenados primeiro em seletores interativos guiados pelo assistente.                 |
| `assistantVisibility` | Não         | `"visible"` \| `"manual-only"`                  | Oculta a opção dos seletores do assistente, mas ainda permite seleção manual pela CLI.                   |
| `deprecatedChoiceIds` | Não         | `string[]`                                      | IDs legados de opção que devem redirecionar os usuários para esta opção de substituição.                 |
| `groupId`             | Não         | `string`                                        | ID opcional de grupo para agrupar opções relacionadas.                                                    |
| `groupLabel`          | Não         | `string`                                        | Rótulo voltado ao usuário para esse grupo.                                                                |
| `groupHint`           | Não         | `string`                                        | Texto auxiliar curto para o grupo.                                                                        |
| `optionKey`           | Não         | `string`                                        | Chave interna de opção para fluxos de autenticação simples com uma única flag.                            |
| `cliFlag`             | Não         | `string`                                        | Nome da flag da CLI, como `--openrouter-api-key`.                                                         |
| `cliOption`           | Não         | `string`                                        | Formato completo da opção da CLI, como `--openrouter-api-key <key>`.                                      |
| `cliDescription`      | Não         | `string`                                        | Descrição usada na ajuda da CLI.                                                                          |
| `onboardingScopes`    | Não         | `Array<"text-inference" \| "image-generation">` | Em quais superfícies de onboarding esta opção deve aparecer. Se omitido, o padrão é `["text-inference"]`. |

## Referência de `commandAliases`

Use `commandAliases` quando um Plugin é dono de um nome de comando de runtime que os usuários podem, por engano,
colocar em `plugins.allow` ou tentar executar como um comando raiz da CLI. O OpenClaw
usa esses metadados para diagnósticos sem importar o código de runtime do Plugin.

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
| `name`       | Sim         | `string`          | Nome do comando que pertence a este Plugin.                               |
| `kind`       | Não         | `"runtime-slash"` | Marca o alias como um comando slash de chat em vez de um comando raiz da CLI. |
| `cliCommand` | Não         | `string`          | Comando raiz relacionado da CLI a ser sugerido para operações de CLI, se existir. |

## Referência de `activation`

Use `activation` quando o Plugin pode declarar de forma barata quais eventos do plano de controle
devem ativá-lo depois.

## Referência de `qaRunners`

Use `qaRunners` quando um Plugin contribui com um ou mais executores de transporte sob a raiz compartilhada `openclaw qa`. Mantenha esses metadados baratos e estáticos; o runtime do Plugin ainda é dono do registro real da CLI por meio de uma superfície leve `runtime-api.ts` que exporta `qaRunnerCliRegistrations`.

```json
{
  "qaRunners": [
    {
      "commandName": "matrix",
      "description": "Run the Docker-backed Matrix live QA lane against a disposable homeserver"
    }
  ]
}
```

| Campo         | Obrigatório | Tipo     | O que significa                                                     |
| ------------- | ----------- | -------- | ------------------------------------------------------------------- |
| `commandName` | Sim         | `string` | Subcomando montado sob `openclaw qa`, por exemplo `matrix`.         |
| `description` | Não         | `string` | Texto de ajuda de fallback usado quando o host compartilhado precisa de um comando stub. |

Este bloco é apenas metadados. Ele não registra comportamento de runtime e não substitui `register(...)`, `setupEntry` nem outros entrypoints de runtime/Plugin.
Os consumidores atuais o usam como uma dica de refinamento antes de um carregamento mais amplo de Plugins, portanto a ausência de metadados de ativação normalmente só afeta o desempenho; ela não deve
alterar a correção enquanto os fallbacks legados de propriedade no manifesto ainda existirem.

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

| Campo            | Obrigatório | Tipo                                                 | O que significa                                                    |
| ---------------- | ----------- | ---------------------------------------------------- | ------------------------------------------------------------------ |
| `onProviders`    | Não         | `string[]`                                           | IDs de provider que devem ativar este Plugin quando solicitados.   |
| `onCommands`     | Não         | `string[]`                                           | IDs de comando que devem ativar este Plugin.                       |
| `onChannels`     | Não         | `string[]`                                           | IDs de canal que devem ativar este Plugin.                         |
| `onRoutes`       | Não         | `string[]`                                           | Tipos de rota que devem ativar este Plugin.                        |
| `onCapabilities` | Não         | `Array<"provider" \| "channel" \| "tool" \| "hook">` | Dicas amplas de capacidade usadas pelo planejamento de ativação do plano de controle. |

Consumidores ativos atualmente:

- o planejamento da CLI acionado por comando usa como fallback
  `commandAliases[].cliCommand` ou `commandAliases[].name`
- o planejamento de configuração/canal acionado por canal usa como fallback a propriedade legada de `channels[]`
  quando faltam metadados explícitos de ativação de canal
- o planejamento de configuração/runtime acionado por provider usa como fallback a propriedade legada de
  `providers[]` e `cliBackends[]` de nível superior quando faltam metadados explícitos de ativação de provider

## Referência de `setup`

Use `setup` quando as superfícies de configuração e onboarding precisarem de metadados baratos pertencentes ao Plugin
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

`cliBackends` de nível superior continua válido e segue descrevendo backends de inferência da CLI. `setup.cliBackends` é a superfície de descritor específica de configuração para fluxos de plano de controle/configuração que devem permanecer apenas como metadados.

Quando presentes, `setup.providers` e `setup.cliBackends` são a superfície preferencial de busca guiada por descritores para descoberta de configuração. Se o descritor apenas restringir o Plugin candidato e a configuração ainda precisar de hooks de runtime mais ricos em tempo de configuração, defina `requiresRuntime: true` e mantenha `setup-api` como o caminho de execução de fallback.

Como a busca de configuração pode executar código `setup-api` pertencente ao Plugin, os valores normalizados de `setup.providers[].id` e `setup.cliBackends[]` devem permanecer únicos entre os plugins descobertos. Propriedade ambígua falha em modo fechado em vez de escolher um vencedor pela ordem de descoberta.

### Referência de `setup.providers`

| Campo         | Obrigatório | Tipo       | O que significa                                                                     |
| ------------- | ----------- | ---------- | ----------------------------------------------------------------------------------- |
| `id`          | Sim         | `string`   | ID do provider exposto durante a configuração ou o onboarding. Mantenha IDs normalizados globalmente únicos. |
| `authMethods` | Não         | `string[]` | IDs de método de configuração/autenticação compatíveis com este provider sem carregar o runtime completo. |
| `envVars`     | Não         | `string[]` | Variáveis de ambiente que superfícies genéricas de configuração/status podem verificar antes de o runtime do Plugin carregar. |

### Campos de `setup`

| Campo              | Obrigatório | Tipo       | O que significa                                                                                      |
| ------------------ | ----------- | ---------- | ---------------------------------------------------------------------------------------------------- |
| `providers`        | Não         | `object[]` | Descritores de configuração de provider expostos durante a configuração e o onboarding.              |
| `cliBackends`      | Não         | `string[]` | IDs de backend em tempo de configuração usados para busca de configuração guiada por descritores. Mantenha IDs normalizados globalmente únicos. |
| `configMigrations` | Não         | `string[]` | IDs de migração de configuração pertencentes à superfície de configuração deste Plugin.              |
| `requiresRuntime`  | Não         | `boolean`  | Se a configuração ainda precisa de execução de `setup-api` após a busca por descritor.              |

## Referência de `uiHints`

`uiHints` é um mapa de nomes de campos de configuração para pequenas dicas de renderização.

```json
{
  "uiHints": {
    "apiKey": {
      "label": "API key",
      "help": "Used for OpenRouter requests",
      "placeholder": "sk-or-v1-...",
      "sensitive": true
    }
  }
}
```

Cada dica de campo pode incluir:

| Campo         | Tipo       | O que significa                         |
| ------------- | ---------- | --------------------------------------- |
| `label`       | `string`   | Rótulo do campo voltado ao usuário.     |
| `help`        | `string`   | Texto auxiliar curto.                   |
| `tags`        | `string[]` | Tags opcionais de UI.                   |
| `advanced`    | `boolean`  | Marca o campo como avançado.            |
| `sensitive`   | `boolean`  | Marca o campo como secreto ou sensível. |
| `placeholder` | `string`   | Texto de placeholder para entradas de formulário. |

## Referência de `contracts`

Use `contracts` apenas para metadados estáticos de propriedade de capacidades que o OpenClaw pode
ler sem importar o runtime do Plugin.

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

| Campo                            | Tipo       | O que significa                                               |
| -------------------------------- | ---------- | ------------------------------------------------------------- |
| `speechProviders`                | `string[]` | IDs de provider de fala pertencentes a este Plugin.           |
| `realtimeTranscriptionProviders` | `string[]` | IDs de provider de transcrição em tempo real pertencentes a este Plugin. |
| `realtimeVoiceProviders`         | `string[]` | IDs de provider de voz em tempo real pertencentes a este Plugin. |
| `mediaUnderstandingProviders`    | `string[]` | IDs de provider de media-understanding pertencentes a este Plugin. |
| `imageGenerationProviders`       | `string[]` | IDs de provider de geração de imagem pertencentes a este Plugin. |
| `videoGenerationProviders`       | `string[]` | IDs de provider de geração de vídeo pertencentes a este Plugin. |
| `webFetchProviders`              | `string[]` | IDs de provider de web-fetch pertencentes a este Plugin.      |
| `webSearchProviders`             | `string[]` | IDs de provider de busca na web pertencentes a este Plugin.   |
| `tools`                          | `string[]` | Nomes de ferramentas de agente pertencentes a este Plugin para verificações de contrato de bundles. |

## Referência de `channelConfigs`

Use `channelConfigs` quando um Plugin de canal precisar de metadados baratos de configuração antes de o runtime carregar.

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
          "label": "Homeserver URL",
          "placeholder": "https://matrix.example.com"
        }
      },
      "label": "Matrix",
      "description": "Matrix homeserver connection",
      "preferOver": ["matrix-legacy"]
    }
  }
}
```

Cada entrada de canal pode incluir:

| Campo         | Tipo                     | O que significa                                                                          |
| ------------- | ------------------------ | ---------------------------------------------------------------------------------------- |
| `schema`      | `object`                 | Esquema JSON para `channels.<id>`. Obrigatório para cada entrada declarada de configuração de canal. |
| `uiHints`     | `Record<string, object>` | Rótulos/placeholders/dicas de sensibilidade de UI opcionais para essa seção de configuração de canal. |
| `label`       | `string`                 | Rótulo do canal mesclado em superfícies de seletor e inspeção quando os metadados de runtime não estiverem prontos. |
| `description` | `string`                 | Descrição curta do canal para superfícies de inspeção e catálogo.                        |
| `preferOver`  | `string[]`               | IDs legados ou de menor prioridade de Plugin que este canal deve superar em superfícies de seleção. |

## Referência de `modelSupport`

Use `modelSupport` quando o OpenClaw precisar inferir seu Plugin de provider a partir de IDs abreviados de modelo, como `gpt-5.4` ou `claude-sonnet-4.6`, antes de o runtime do Plugin carregar.

```json
{
  "modelSupport": {
    "modelPrefixes": ["gpt-", "o1", "o3", "o4"],
    "modelPatterns": ["^computer-use-preview"]
  }
}
```

O OpenClaw aplica esta precedência:

- referências explícitas `provider/model` usam os metadados de manifesto `providers` do proprietário
- `modelPatterns` têm precedência sobre `modelPrefixes`
- se um Plugin não empacotado e um Plugin empacotado corresponderem, o Plugin não empacotado vence
- ambiguidades restantes são ignoradas até que o usuário ou a configuração especifique um provider

Campos:

| Campo           | Tipo       | O que significa                                                                  |
| --------------- | ---------- | -------------------------------------------------------------------------------- |
| `modelPrefixes` | `string[]` | Prefixos correspondidos com `startsWith` em relação a IDs abreviados de modelo.  |
| `modelPatterns` | `string[]` | Fontes de regex correspondidas em relação a IDs abreviados de modelo após a remoção do sufixo do perfil. |

Chaves legadas de capacidade de nível superior estão obsoletas. Use `openclaw doctor --fix` para mover `speechProviders`, `realtimeTranscriptionProviders`, `realtimeVoiceProviders`, `mediaUnderstandingProviders`, `imageGenerationProviders`, `videoGenerationProviders`, `webFetchProviders` e `webSearchProviders` para `contracts`; o carregamento normal do manifesto não trata mais esses campos de nível superior como propriedade de capacidades.

## Manifesto versus package.json

Os dois arquivos cumprem funções diferentes:

| Arquivo                | Use para                                                                                                                                |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.plugin.json` | Descoberta, validação de configuração, metadados de opções de autenticação e dicas de UI que devem existir antes de o código do Plugin rodar |
| `package.json`         | Metadados npm, instalação de dependências e o bloco `openclaw` usado para entrypoints, bloqueio de instalação, configuração ou metadados de catálogo |

Se você não tiver certeza de onde um metadado deve ficar, use esta regra:

- se o OpenClaw precisar conhecê-lo antes de carregar o código do Plugin, coloque-o em `openclaw.plugin.json`
- se for sobre empacotamento, arquivos de entrada ou comportamento de instalação do npm, coloque-o em `package.json`

### Campos de `package.json` que afetam a descoberta

Alguns metadados de Plugin pré-runtime intencionalmente ficam em `package.json` sob o bloco `openclaw` em vez de `openclaw.plugin.json`.

Exemplos importantes:

| Campo                                                             | O que significa                                                                                                                             |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `openclaw.extensions`                                             | Declara entrypoints nativos de Plugin.                                                                                                      |
| `openclaw.setupEntry`                                             | Entrypoint leve apenas de configuração usado durante onboarding e inicialização adiada de canal.                                            |
| `openclaw.channel`                                                | Metadados baratos de catálogo de canal, como rótulos, caminhos de documentação, aliases e texto de seleção.                               |
| `openclaw.channel.configuredState`                                | Metadados leves de verificador de estado configurado que podem responder "já existe uma configuração apenas por env?" sem carregar o runtime completo do canal. |
| `openclaw.channel.persistedAuthState`                             | Metadados leves de verificador de autenticação persistida que podem responder "já existe algo autenticado?" sem carregar o runtime completo do canal. |
| `openclaw.install.npmSpec` / `openclaw.install.localPath`         | Dicas de instalação/atualização para plugins empacotados e publicados externamente.                                                        |
| `openclaw.install.defaultChoice`                                  | Caminho de instalação preferido quando várias fontes de instalação estão disponíveis.                                                       |
| `openclaw.install.minHostVersion`                                 | Versão mínima compatível do host OpenClaw, usando um piso semver como `>=2026.3.22`.                                                       |
| `openclaw.install.allowInvalidConfigRecovery`                     | Permite um caminho restrito de recuperação por reinstalação de Plugin empacotado quando a configuração é inválida.                        |
| `openclaw.startup.deferConfiguredChannelFullLoadUntilAfterListen` | Permite que superfícies de canal apenas de configuração carreguem antes do Plugin de canal completo durante a inicialização.               |

`openclaw.install.minHostVersion` é aplicado durante a instalação e o carregamento do registro de manifestos. Valores inválidos são rejeitados; valores mais novos, porém válidos, fazem o Plugin ser ignorado em hosts mais antigos.

`openclaw.install.allowInvalidConfigRecovery` é intencionalmente restrito. Ele não torna instaláveis configurações arbitrariamente quebradas. Hoje ele só permite que fluxos de instalação se recuperem de falhas específicas e antigas de upgrade de Plugin empacotado, como um caminho ausente de Plugin empacotado ou uma entrada antiga `channels.<id>` para esse mesmo Plugin empacotado. Erros de configuração não relacionados ainda bloqueiam a instalação e enviam operadores para `openclaw doctor --fix`.

`openclaw.channel.persistedAuthState` é um metadado de pacote para um pequeno módulo verificador:

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

Use-o quando fluxos de configuração, doctor ou estado configurado precisarem de uma sondagem barata de autenticação sim/não antes de o Plugin de canal completo carregar. A exportação de destino deve ser uma função pequena que leia apenas o estado persistido; não a encaminhe pelo barrel completo de runtime do canal.

`openclaw.channel.configuredState` segue o mesmo formato para verificações baratas de estado configurado apenas por env:

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

Use-o quando um canal puder responder o estado configurado a partir de env ou outras entradas pequenas sem runtime. Se a verificação precisar da resolução completa da configuração ou do runtime real do canal, mantenha essa lógica no hook `config.hasConfiguredState` do Plugin.

## Requisitos de JSON Schema

- **Todo Plugin deve incluir um JSON Schema**, mesmo que não aceite nenhuma configuração.
- Um esquema vazio é aceitável (por exemplo, `{ "type": "object", "additionalProperties": false }`).
- Os esquemas são validados no momento de leitura/gravação da configuração, não em runtime.

## Comportamento de validação

- Chaves desconhecidas em `channels.*` são **erros**, a menos que o ID do canal seja declarado por um manifesto de Plugin.
- `plugins.entries.<id>`, `plugins.allow`, `plugins.deny` e `plugins.slots.*`
  devem referenciar IDs de Plugin **detectáveis**. IDs desconhecidos são **erros**.
- Se um Plugin estiver instalado, mas tiver um manifesto ou esquema ausente ou quebrado,
  a validação falha e o Doctor relata o erro do Plugin.
- Se a configuração do Plugin existir, mas o Plugin estiver **desabilitado**, a configuração será mantida e um **aviso** será exibido no Doctor + logs.

Consulte [Referência de configuração](/pt-BR/gateway/configuration) para o esquema completo de `plugins.*`.

## Observações

- O manifesto é **obrigatório para plugins nativos do OpenClaw**, incluindo carregamentos locais do sistema de arquivos.
- O runtime ainda carrega o módulo do Plugin separadamente; o manifesto é apenas para descoberta + validação.
- Manifestos nativos são analisados com JSON5, então comentários, vírgulas finais e chaves sem aspas são aceitos, desde que o valor final ainda seja um objeto.
- Apenas os campos de manifesto documentados são lidos pelo carregador de manifesto. Evite adicionar chaves personalizadas de nível superior aqui.
- `providerAuthEnvVars` é o caminho barato de metadados para sondagens de autenticação, validação de marcadores de env e superfícies semelhantes de autenticação de provider que não devem iniciar o runtime do Plugin apenas para inspecionar nomes de env.
- `providerAuthAliases` permite que variantes de provider reutilizem as variáveis de ambiente de autenticação, perfis de autenticação, autenticação baseada em configuração e a opção de onboarding com chave de API de outro provider sem hardcodar essa relação no core.
- `channelEnvVars` é o caminho barato de metadados para fallback de shell-env, prompts de configuração e superfícies de canal semelhantes que não devem iniciar o runtime do Plugin apenas para inspecionar nomes de env.
- `providerAuthChoices` é o caminho barato de metadados para seletores de opção de autenticação, resolução de `--auth-choice`, mapeamento de provider preferido e registro simples de flags de CLI de onboarding antes de o runtime do provider carregar. Para metadados de assistente de runtime que exigem código de provider, consulte [Hooks de runtime de provider](/pt-BR/plugins/architecture#provider-runtime-hooks).
- Tipos exclusivos de Plugin são selecionados por meio de `plugins.slots.*`.
  - `kind: "memory"` é selecionado por `plugins.slots.memory`.
  - `kind: "context-engine"` é selecionado por `plugins.slots.contextEngine`
    (padrão: `legacy` embutido).
- `channels`, `providers`, `cliBackends` e `skills` podem ser omitidos quando um Plugin não precisar deles.
- Se o seu Plugin depender de módulos nativos, documente as etapas de build e quaisquer requisitos de allowlist do gerenciador de pacotes (por exemplo, pnpm `allow-build-scripts`
  - `pnpm rebuild <package>`).

## Relacionado

- [Criando Plugins](/pt-BR/plugins/building-plugins) — primeiros passos com plugins
- [Arquitetura de Plugin](/pt-BR/plugins/architecture) — arquitetura interna
- [Visão geral do SDK](/pt-BR/plugins/sdk-overview) — referência do SDK de Plugin
