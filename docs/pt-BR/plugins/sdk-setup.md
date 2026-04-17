---
read_when:
    - Você está adicionando um assistente de configuração a um Plugin
    - Você precisa entender `setup-entry.ts` versus `index.ts`
    - Você está definindo esquemas de config do Plugin ou metadados `openclaw` no `package.json`
sidebarTitle: Setup and Config
summary: Assistentes de configuração, setup-entry.ts, esquemas de configuração e metadados do package.json
title: Configuração e Config do Plugin
x-i18n:
    generated_at: "2026-04-15T19:41:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: ddf28e25e381a4a38ac478e531586f59612e1a278732597375f87c2eeefc521b
    source_path: plugins/sdk-setup.md
    workflow: 15
---

# Configuração e Config do Plugin

Referência para empacotamento de Plugin (metadados do `package.json`), manifestos
(`openclaw.plugin.json`), entradas de configuração e esquemas de config.

<Tip>
  **Está procurando um passo a passo?** Os guias práticos cobrem o empacotamento em contexto:
  [Plugins de Canal](/pt-BR/plugins/sdk-channel-plugins#step-1-package-and-manifest) e
  [Plugins de Provedor](/pt-BR/plugins/sdk-provider-plugins#step-1-package-and-manifest).
</Tip>

## Metadados do pacote

Seu `package.json` precisa de um campo `openclaw` que informe ao sistema de plugins o que
seu Plugin fornece:

**Plugin de canal:**

```json
{
  "name": "@myorg/openclaw-my-channel",
  "version": "1.0.0",
  "type": "module",
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "channel": {
      "id": "my-channel",
      "label": "My Channel",
      "blurb": "Short description of the channel."
    }
  }
}
```

**Plugin de provedor / linha de base de publicação do ClawHub:**

```json openclaw-clawhub-package.json
{
  "name": "@myorg/openclaw-my-plugin",
  "version": "1.0.0",
  "type": "module",
  "openclaw": {
    "extensions": ["./index.ts"],
    "compat": {
      "pluginApi": ">=2026.3.24-beta.2",
      "minGatewayVersion": "2026.3.24-beta.2"
    },
    "build": {
      "openclawVersion": "2026.3.24-beta.2",
      "pluginSdkVersion": "2026.3.24-beta.2"
    }
  }
}
```

Se você publicar o Plugin externamente no ClawHub, esses campos `compat` e `build`
serão obrigatórios. Os snippets canônicos de publicação ficam em
`docs/snippets/plugin-publish/`.

### Campos `openclaw`

| Campo        | Tipo       | Descrição                                                                                             |
| ------------ | ---------- | ----------------------------------------------------------------------------------------------------- |
| `extensions` | `string[]` | Arquivos de ponto de entrada (relativos à raiz do pacote)                                             |
| `setupEntry` | `string`   | Entrada leve apenas para configuração (opcional)                                                      |
| `channel`    | `object`   | Metadados do catálogo de canais para configuração, seletor, início rápido e superfícies de status     |
| `providers`  | `string[]` | IDs de provedores registrados por este Plugin                                                         |
| `install`    | `object`   | Dicas de instalação: `npmSpec`, `localPath`, `defaultChoice`, `minHostVersion`, `allowInvalidConfigRecovery` |
| `startup`    | `object`   | Flags de comportamento de inicialização                                                               |

### `openclaw.channel`

`openclaw.channel` é um metadado barato de pacote para descoberta de canais e
superfícies de configuração antes que o runtime seja carregado.

| Campo                                  | Tipo       | O que significa                                                               |
| -------------------------------------- | ---------- | ----------------------------------------------------------------------------- |
| `id`                                   | `string`   | ID canônico do canal.                                                         |
| `label`                                | `string`   | Rótulo principal do canal.                                                    |
| `selectionLabel`                       | `string`   | Rótulo do seletor/configuração quando deve ser diferente de `label`.          |
| `detailLabel`                          | `string`   | Rótulo de detalhe secundário para catálogos de canais e superfícies de status mais ricos. |
| `docsPath`                             | `string`   | Caminho da documentação para links de configuração e seleção.                 |
| `docsLabel`                            | `string`   | Rótulo substituto usado para links de documentação quando deve ser diferente do ID do canal. |
| `blurb`                                | `string`   | Descrição curta para onboarding/catálogo.                                     |
| `order`                                | `number`   | Ordem de classificação em catálogos de canais.                                |
| `aliases`                              | `string[]` | Aliases extras de busca para seleção de canal.                                |
| `preferOver`                           | `string[]` | IDs de Plugin/canal de prioridade inferior que este canal deve superar.       |
| `systemImage`                          | `string`   | Nome opcional de ícone/imagem do sistema para catálogos de UI de canais.      |
| `selectionDocsPrefix`                  | `string`   | Texto de prefixo antes dos links de documentação nas superfícies de seleção.  |
| `selectionDocsOmitLabel`               | `boolean`  | Mostra o caminho da documentação diretamente em vez de um link rotulado na cópia de seleção. |
| `selectionExtras`                      | `string[]` | Strings curtas extras anexadas na cópia de seleção.                           |
| `markdownCapable`                      | `boolean`  | Marca o canal como compatível com Markdown para decisões de formatação de saída. |
| `exposure`                             | `object`   | Controles de visibilidade do canal para configuração, listas configuradas e superfícies de documentação. |
| `quickstartAllowFrom`                  | `boolean`  | Inclui este canal no fluxo padrão de configuração `allowFrom` de início rápido. |
| `forceAccountBinding`                  | `boolean`  | Exige vínculo explícito de conta mesmo quando existe apenas uma conta.         |
| `preferSessionLookupForAnnounceTarget` | `boolean`  | Prefere busca de sessão ao resolver destinos de anúncio para este canal.       |

Exemplo:

```json
{
  "openclaw": {
    "channel": {
      "id": "my-channel",
      "label": "My Channel",
      "selectionLabel": "My Channel (self-hosted)",
      "detailLabel": "My Channel Bot",
      "docsPath": "/channels/my-channel",
      "docsLabel": "my-channel",
      "blurb": "Webhook-based self-hosted chat integration.",
      "order": 80,
      "aliases": ["mc"],
      "preferOver": ["my-channel-legacy"],
      "selectionDocsPrefix": "Guide:",
      "selectionExtras": ["Markdown"],
      "markdownCapable": true,
      "exposure": {
        "configured": true,
        "setup": true,
        "docs": true
      },
      "quickstartAllowFrom": true
    }
  }
}
```

`exposure` oferece suporte a:

- `configured`: incluir o canal em superfícies de listagem no estilo configurado/status
- `setup`: incluir o canal em seletores interativos de configuração/configurar
- `docs`: marcar o canal como voltado ao público em superfícies de documentação/navegação

`showConfigured` e `showInSetup` continuam com suporte como aliases legados. Prefira
`exposure`.

### `openclaw.install`

`openclaw.install` é um metadado de pacote, não um metadado de manifesto.

| Campo                        | Tipo                 | O que significa                                                                  |
| ---------------------------- | -------------------- | -------------------------------------------------------------------------------- |
| `npmSpec`                    | `string`             | Especificação npm canônica para fluxos de instalação/atualização.                |
| `localPath`                  | `string`             | Caminho local de desenvolvimento ou instalação empacotada.                        |
| `defaultChoice`              | `"npm"` \| `"local"` | Fonte de instalação preferida quando ambas estiverem disponíveis.                |
| `minHostVersion`             | `string`             | Versão mínima suportada do OpenClaw no formato `>=x.y.z`.                        |
| `allowInvalidConfigRecovery` | `boolean`            | Permite que fluxos de reinstalação de Plugin empacotado recuperem falhas específicas de config obsoleta. |

Se `minHostVersion` estiver definido, tanto a instalação quanto o carregamento do registro de manifesto o aplicarão.
Hosts mais antigos ignoram o Plugin; strings de versão inválidas são rejeitadas.

`allowInvalidConfigRecovery` não é um bypass geral para configs quebradas. É
para recuperação restrita apenas de Plugin empacotado, de modo que reinstalação/configuração possa reparar sobras conhecidas
de upgrade, como um caminho ausente de Plugin empacotado ou uma entrada obsoleta `channels.<id>`
desse mesmo Plugin. Se a config estiver quebrada por motivos não relacionados, a instalação
ainda falhará de forma fechada e informará ao operador para executar `openclaw doctor --fix`.

### Adiamento do carregamento completo

Plugins de canal podem optar por carregamento adiado com:

```json
{
  "openclaw": {
    "extensions": ["./index.ts"],
    "setupEntry": "./setup-entry.ts",
    "startup": {
      "deferConfiguredChannelFullLoadUntilAfterListen": true
    }
  }
}
```

Quando ativado, o OpenClaw carrega apenas `setupEntry` durante a fase de
inicialização anterior ao listen, mesmo para canais já configurados. A entrada completa é carregada após o
gateway começar a escutar.

<Warning>
  Ative o carregamento adiado apenas quando seu `setupEntry` registrar tudo o que o
  gateway precisa antes de começar a escutar (registro de canal, rotas HTTP,
  métodos do gateway). Se a entrada completa possuir recursos de inicialização obrigatórios, mantenha
  o comportamento padrão.
</Warning>

Se sua entrada de configuração/completa registrar métodos RPC do gateway, mantenha-os em um
prefixo específico do Plugin. Namespaces administrativos reservados do core (`config.*`,
`exec.approvals.*`, `wizard.*`, `update.*`) continuam pertencendo ao core e sempre serão resolvidos
para `operator.admin`.

## Manifesto do Plugin

Todo Plugin nativo deve incluir um `openclaw.plugin.json` na raiz do pacote.
O OpenClaw usa isso para validar a config sem executar código do Plugin.

```json
{
  "id": "my-plugin",
  "name": "My Plugin",
  "description": "Adds My Plugin capabilities to OpenClaw",
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {
      "webhookSecret": {
        "type": "string",
        "description": "Webhook verification secret"
      }
    }
  }
}
```

Para Plugins de canal, adicione `kind` e `channels`:

```json
{
  "id": "my-channel",
  "kind": "channel",
  "channels": ["my-channel"],
  "configSchema": {
    "type": "object",
    "additionalProperties": false,
    "properties": {}
  }
}
```

Mesmo Plugins sem config devem incluir um esquema. Um esquema vazio é válido:

```json
{
  "id": "my-plugin",
  "configSchema": {
    "type": "object",
    "additionalProperties": false
  }
}
```

Consulte [Manifesto do Plugin](/pt-BR/plugins/manifest) para a referência completa do esquema.

## Publicação no ClawHub

Para pacotes de Plugin, use o comando do ClawHub específico para pacotes:

```bash
clawhub package publish your-org/your-plugin --dry-run
clawhub package publish your-org/your-plugin
```

O alias legado de publicação apenas para Skills é para Skills. Pacotes de Plugin devem
sempre usar `clawhub package publish`.

## Entrada de configuração

O arquivo `setup-entry.ts` é uma alternativa leve a `index.ts` que
o OpenClaw carrega quando precisa apenas das superfícies de configuração (onboarding, reparo
de config, inspeção de canal desativado).

```typescript
// setup-entry.ts
import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
import { myChannelPlugin } from "./src/channel.js";

export default defineSetupPluginEntry(myChannelPlugin);
```

Isso evita carregar código pesado de runtime (bibliotecas de criptografia, registros
de CLI, serviços em segundo plano) durante fluxos de configuração.

Canais empacotados do workspace que mantêm exportações seguras para configuração em módulos sidecar podem
usar `defineBundledChannelSetupEntry(...)` de
`openclaw/plugin-sdk/channel-entry-contract` em vez de
`defineSetupPluginEntry(...)`. Esse contrato empacotado também oferece suporte a uma exportação opcional
`runtime`, para que o wiring de runtime em tempo de configuração permaneça leve e explícito.

**Quando o OpenClaw usa `setupEntry` em vez da entrada completa:**

- O canal está desativado, mas precisa de superfícies de configuração/onboarding
- O canal está ativado, mas não configurado
- O carregamento adiado está ativado (`deferConfiguredChannelFullLoadUntilAfterListen`)

**O que `setupEntry` deve registrar:**

- O objeto do Plugin de canal (via `defineSetupPluginEntry`)
- Quaisquer rotas HTTP necessárias antes de o gateway entrar em listen
- Quaisquer métodos do gateway necessários durante a inicialização

Esses métodos de gateway de inicialização ainda devem evitar namespaces administrativos reservados do core
como `config.*` ou `update.*`.

**O que `setupEntry` NÃO deve incluir:**

- Registros de CLI
- Serviços em segundo plano
- Imports pesados de runtime (crypto, SDKs)
- Métodos do gateway necessários apenas após a inicialização

### Imports restritos de helpers de configuração

Para caminhos quentes apenas de configuração, prefira os seams restritos de helper de configuração em vez do umbrella mais amplo
`plugin-sdk/setup` quando você precisar apenas de parte da superfície de configuração:

| Caminho de importação               | Use para                                                                                  | Exportações principais                                                                                                                                                                                                                                                                        |
| ----------------------------------- | ----------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/setup-runtime`          | helpers de runtime em tempo de configuração que permanecem disponíveis em `setupEntry` / inicialização adiada de canal | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
| `plugin-sdk/setup-adapter-runtime`  | adaptadores de configuração de conta com reconhecimento de ambiente                       | `createEnvPatchedAccountSetupAdapter`                                                                                                                                                                                                                                                        |
| `plugin-sdk/setup-tools`            | helpers de CLI/arquivo/documentação para configuração/instalação                          | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR`                                                                                                                                                                              |

Use o seam mais amplo `plugin-sdk/setup` quando quiser a caixa de ferramentas completa e compartilhada de configuração,
incluindo helpers de patch de config como
`moveSingleAccountChannelSectionToDefaultAccount(...)`.

Os adaptadores de patch de configuração continuam seguros para importação em caminhos quentes. A busca da superfície de contrato empacotada
para promoção de conta única é lazy, portanto importar
`plugin-sdk/setup-runtime` não carrega antecipadamente a descoberta da superfície de contrato empacotada
antes de o adaptador realmente ser usado.

### Promoção de conta única controlada pelo canal

Quando um canal é atualizado de uma config de nível superior de conta única para
`channels.<id>.accounts.*`, o comportamento compartilhado padrão é mover valores
promovidos com escopo de conta para `accounts.default`.

Canais empacotados podem restringir ou substituir essa promoção por meio de sua
superfície de contrato de configuração:

- `singleAccountKeysToMove`: chaves extras de nível superior que devem ser movidas para a
  conta promovida
- `namedAccountPromotionKeys`: quando contas nomeadas já existem, apenas estas
  chaves são movidas para a conta promovida; chaves compartilhadas de política/entrega permanecem na raiz
  do canal
- `resolveSingleAccountPromotionTarget(...)`: escolhe qual conta existente
  recebe os valores promovidos

Matrix é o exemplo empacotado atual. Se exatamente uma conta Matrix nomeada
já existir, ou se `defaultAccount` apontar para uma chave não canônica existente
como `Ops`, a promoção preserva essa conta em vez de criar uma nova
entrada `accounts.default`.

## Esquema de config

A config do Plugin é validada em relação ao JSON Schema no seu manifesto. Os usuários
configuram plugins por meio de:

```json5
{
  plugins: {
    entries: {
      "my-plugin": {
        config: {
          webhookSecret: "abc123",
        },
      },
    },
  },
}
```

Seu Plugin recebe essa config como `api.pluginConfig` durante o registro.

Para config específica de canal, use a seção de config do canal:

```json5
{
  channels: {
    "my-channel": {
      token: "bot-token",
      allowFrom: ["user1", "user2"],
    },
  },
}
```

### Criando esquemas de config de canal

Use `buildChannelConfigSchema` de `openclaw/plugin-sdk/core` para converter um
esquema Zod no wrapper `ChannelConfigSchema` que o OpenClaw valida:

```typescript
import { z } from "zod";
import { buildChannelConfigSchema } from "openclaw/plugin-sdk/core";

const accountSchema = z.object({
  token: z.string().optional(),
  allowFrom: z.array(z.string()).optional(),
  accounts: z.object({}).catchall(z.any()).optional(),
  defaultAccount: z.string().optional(),
});

const configSchema = buildChannelConfigSchema(accountSchema);
```

## Assistentes de configuração

Plugins de canal podem fornecer assistentes interativos de configuração para `openclaw onboard`.
O assistente é um objeto `ChannelSetupWizard` no `ChannelPlugin`:

```typescript
import type { ChannelSetupWizard } from "openclaw/plugin-sdk/channel-setup";

const setupWizard: ChannelSetupWizard = {
  channel: "my-channel",
  status: {
    configuredLabel: "Connected",
    unconfiguredLabel: "Not configured",
    resolveConfigured: ({ cfg }) => Boolean((cfg.channels as any)?.["my-channel"]?.token),
  },
  credentials: [
    {
      inputKey: "token",
      providerHint: "my-channel",
      credentialLabel: "Bot token",
      preferredEnvVar: "MY_CHANNEL_BOT_TOKEN",
      envPrompt: "Use MY_CHANNEL_BOT_TOKEN from environment?",
      keepPrompt: "Keep current token?",
      inputPrompt: "Enter your bot token:",
      inspect: ({ cfg, accountId }) => {
        const token = (cfg.channels as any)?.["my-channel"]?.token;
        return {
          accountConfigured: Boolean(token),
          hasConfiguredValue: Boolean(token),
        };
      },
    },
  ],
};
```

O tipo `ChannelSetupWizard` oferece suporte a `credentials`, `textInputs`,
`dmPolicy`, `allowFrom`, `groupAccess`, `prepare`, `finalize` e mais.
Consulte os pacotes de Plugin empacotados (por exemplo, o Plugin do Discord em `src/channel.setup.ts`) para
exemplos completos.

Para prompts de allowlist de DM que precisam apenas do fluxo padrão
`note -> prompt -> parse -> merge -> patch`, prefira os helpers compartilhados de configuração
de `openclaw/plugin-sdk/setup`: `createPromptParsedAllowFromForAccount(...)`,
`createTopLevelChannelParsedAllowFromPrompt(...)` e
`createNestedChannelParsedAllowFromPrompt(...)`.

Para blocos de status de configuração de canal que variam apenas por rótulos, pontuações e linhas extras opcionais,
prefira `createStandardChannelSetupStatus(...)` de
`openclaw/plugin-sdk/setup` em vez de montar manualmente o mesmo objeto `status` em
cada Plugin.

Para superfícies opcionais de configuração que devem aparecer apenas em certos contextos, use
`createOptionalChannelSetupSurface` de `openclaw/plugin-sdk/channel-setup`:

```typescript
import { createOptionalChannelSetupSurface } from "openclaw/plugin-sdk/channel-setup";

const setupSurface = createOptionalChannelSetupSurface({
  channel: "my-channel",
  label: "My Channel",
  npmSpec: "@myorg/openclaw-my-channel",
  docsPath: "/channels/my-channel",
});
// Returns { setupAdapter, setupWizard }
```

`plugin-sdk/channel-setup` também expõe os builders de nível mais baixo
`createOptionalChannelSetupAdapter(...)` e
`createOptionalChannelSetupWizard(...)` quando você precisa apenas de uma metade
dessa superfície de instalação opcional.

O adaptador/assistente opcional gerado falha de forma fechada em gravações reais de config. Eles
reutilizam uma única mensagem de instalação obrigatória em `validateInput`,
`applyAccountConfig` e `finalize`, e acrescentam um link de documentação quando `docsPath` está
definido.

Para UIs de configuração baseadas em binário, prefira os helpers delegados compartilhados em vez de
copiar a mesma cola de binário/status em cada canal:

- `createDetectedBinaryStatus(...)` para blocos de status que variam apenas por rótulos,
  dicas, pontuações e detecção de binário
- `createCliPathTextInput(...)` para entradas de texto baseadas em caminho
- `createDelegatedSetupWizardStatusResolvers(...)`,
  `createDelegatedPrepare(...)`, `createDelegatedFinalize(...)` e
  `createDelegatedResolveConfigured(...)` quando `setupEntry` precisa encaminhar para
  um assistente completo mais pesado de forma lazy
- `createDelegatedTextInputShouldPrompt(...)` quando `setupEntry` precisa apenas
  delegar uma decisão `textInputs[*].shouldPrompt`

## Publicação e instalação

**Plugins externos:** publique no [ClawHub](/pt-BR/tools/clawhub) ou no npm e depois instale:

```bash
openclaw plugins install @myorg/openclaw-my-plugin
```

O OpenClaw tenta primeiro o ClawHub e recorre automaticamente ao npm. Você também pode
forçar explicitamente o ClawHub:

```bash
openclaw plugins install clawhub:@myorg/openclaw-my-plugin   # somente ClawHub
```

Não existe uma substituição correspondente `npm:`. Use a especificação normal de pacote npm quando
quiser o caminho npm após o fallback do ClawHub:

```bash
openclaw plugins install @myorg/openclaw-my-plugin
```

**Plugins no repositório:** coloque-os na árvore de workspace de plugins empacotados e eles serão automaticamente
descobertos durante o build.

**Os usuários podem instalar:**

```bash
openclaw plugins install <package-name>
```

<Info>
  Para instalações vindas do npm, `openclaw plugins install` executa
  `npm install --ignore-scripts` (sem scripts de ciclo de vida). Mantenha as árvores
  de dependências do Plugin em JS/TS puro e evite pacotes que exijam builds em `postinstall`.
</Info>

## Relacionado

- [Pontos de entrada do SDK](/pt-BR/plugins/sdk-entrypoints) -- `definePluginEntry` e `defineChannelPluginEntry`
- [Manifesto do Plugin](/pt-BR/plugins/manifest) -- referência completa do esquema do manifesto
- [Criando Plugins](/pt-BR/plugins/building-plugins) -- guia passo a passo para começar
