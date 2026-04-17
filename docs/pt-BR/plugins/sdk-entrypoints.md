---
read_when:
    - Você precisa da assinatura de tipo exata de `definePluginEntry` ou `defineChannelPluginEntry`
    - Você quer entender o modo de registro (completo vs configuração vs metadados da CLI)
    - Você está procurando opções de ponto de entrada
sidebarTitle: Entry Points
summary: Referência para `definePluginEntry`, `defineChannelPluginEntry` e `defineSetupPluginEntry`
title: Pontos de entrada do Plugin
x-i18n:
    generated_at: "2026-04-15T19:41:37Z"
    model: gpt-5.4
    provider: openai
    source_hash: aabca25bc9b8ff1b5bb4852bafe83640ffeba006ea6b6a8eff4e2c37a10f1fe4
    source_path: plugins/sdk-entrypoints.md
    workflow: 15
---

# Pontos de entrada do Plugin

Todo Plugin exporta um objeto de entrada padrão. O SDK fornece três helpers para
criá-los.

<Tip>
  **Procurando um passo a passo?** Veja [Plugins de canal](/pt-BR/plugins/sdk-channel-plugins)
  ou [Plugins de provedor](/pt-BR/plugins/sdk-provider-plugins) para guias passo a passo.
</Tip>

## `definePluginEntry`

**Importação:** `openclaw/plugin-sdk/plugin-entry`

Para plugins de provedor, plugins de ferramenta, plugins de hook e qualquer coisa que **não**
seja um canal de mensagens.

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";

export default definePluginEntry({
  id: "my-plugin",
  name: "My Plugin",
  description: "Short summary",
  register(api) {
    api.registerProvider({
      /* ... */
    });
    api.registerTool({
      /* ... */
    });
  },
});
```

| Campo          | Tipo                                                             | Obrigatório | Padrão              |
| -------------- | ---------------------------------------------------------------- | ----------- | ------------------- |
| `id`           | `string`                                                         | Sim         | —                   |
| `name`         | `string`                                                         | Sim         | —                   |
| `description`  | `string`                                                         | Sim         | —                   |
| `kind`         | `string`                                                         | Não         | —                   |
| `configSchema` | `OpenClawPluginConfigSchema \| () => OpenClawPluginConfigSchema` | Não         | Esquema de objeto vazio |
| `register`     | `(api: OpenClawPluginApi) => void`                               | Sim         | —                   |

- `id` deve corresponder ao seu manifesto `openclaw.plugin.json`.
- `kind` é para slots exclusivos: `"memory"` ou `"context-engine"`.
- `configSchema` pode ser uma função para avaliação preguiçosa.
- O OpenClaw resolve e memoriza esse esquema no primeiro acesso, então builders de esquema
  custosos são executados apenas uma vez.

## `defineChannelPluginEntry`

**Importação:** `openclaw/plugin-sdk/channel-core`

Encapsula `definePluginEntry` com a integração específica de canal. Chama
automaticamente `api.registerChannel({ plugin })`, expõe uma costura opcional de metadados
da CLI de ajuda raiz e controla `registerFull` com base no modo de registro.

```typescript
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";

export default defineChannelPluginEntry({
  id: "my-channel",
  name: "My Channel",
  description: "Short summary",
  plugin: myChannelPlugin,
  setRuntime: setMyRuntime,
  registerCliMetadata(api) {
    api.registerCli(/* ... */);
  },
  registerFull(api) {
    api.registerGatewayMethod(/* ... */);
  },
});
```

| Campo                 | Tipo                                                             | Obrigatório | Padrão              |
| --------------------- | ---------------------------------------------------------------- | ----------- | ------------------- |
| `id`                  | `string`                                                         | Sim         | —                   |
| `name`                | `string`                                                         | Sim         | —                   |
| `description`         | `string`                                                         | Sim         | —                   |
| `plugin`              | `ChannelPlugin`                                                  | Sim         | —                   |
| `configSchema`        | `OpenClawPluginConfigSchema \| () => OpenClawPluginConfigSchema` | Não         | Esquema de objeto vazio |
| `setRuntime`          | `(runtime: PluginRuntime) => void`                               | Não         | —                   |
| `registerCliMetadata` | `(api: OpenClawPluginApi) => void`                               | Não         | —                   |
| `registerFull`        | `(api: OpenClawPluginApi) => void`                               | Não         | —                   |

- `setRuntime` é chamado durante o registro para que você possa armazenar a referência de runtime
  (normalmente via `createPluginRuntimeStore`). Ele é ignorado durante a captura
  de metadados da CLI.
- `registerCliMetadata` é executado tanto durante `api.registrationMode === "cli-metadata"`
  quanto durante `api.registrationMode === "full"`.
  Use-o como o lugar canônico para descritores de CLI pertencentes ao canal, para que a ajuda
  raiz não ative o carregamento enquanto o registro normal de comandos da CLI continua compatível
  com carregamentos completos do Plugin.
- `registerFull` só é executado quando `api.registrationMode === "full"`. Ele é ignorado
  durante o carregamento somente de configuração.
- Assim como `definePluginEntry`, `configSchema` pode ser uma fábrica preguiçosa e o OpenClaw
  memoriza o esquema resolvido no primeiro acesso.
- Para comandos raiz da CLI pertencentes ao Plugin, prefira `api.registerCli(..., { descriptors: [...] })`
  quando você quiser que o comando permaneça com carregamento preguiçoso sem desaparecer da
  árvore de parsing da CLI raiz. Para plugins de canal, prefira registrar esses descritores
  em `registerCliMetadata(...)` e mantenha `registerFull(...)` focado em trabalho somente de runtime.
- Se `registerFull(...)` também registrar métodos RPC do Gateway, mantenha-os em um
  prefixo específico do Plugin. Namespaces administrativos centrais reservados (`config.*`,
  `exec.approvals.*`, `wizard.*`, `update.*`) são sempre forçados para
  `operator.admin`.

## `defineSetupPluginEntry`

**Importação:** `openclaw/plugin-sdk/channel-core`

Para o arquivo leve `setup-entry.ts`. Retorna apenas `{ plugin }`, sem
integração de runtime nem de CLI.

```typescript
import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";

export default defineSetupPluginEntry(myChannelPlugin);
```

O OpenClaw carrega isso em vez da entrada completa quando um canal está desabilitado,
não configurado ou quando o carregamento adiado está ativado. Veja
[Configuração e setup](/pt-BR/plugins/sdk-setup#setup-entry) para saber quando isso importa.

Na prática, combine `defineSetupPluginEntry(...)` com as famílias estreitas de helpers de setup:

- `openclaw/plugin-sdk/setup-runtime` para helpers de setup seguros para runtime, como
  adaptadores de patch de setup seguros para importação, saída de nota de consulta,
  `promptResolvedAllowFrom`, `splitSetupEntries` e proxies de setup delegados
- `openclaw/plugin-sdk/channel-setup` para superfícies de setup de instalação opcional
- `openclaw/plugin-sdk/setup-tools` para helpers de setup/instalação de CLI/arquivo/docs

Mantenha SDKs pesados, registro de CLI e serviços de runtime de longa duração na
entrada completa.

Canais empacotados do workspace que dividem superfícies de setup e runtime podem usar
`defineBundledChannelSetupEntry(...)` de
`openclaw/plugin-sdk/channel-entry-contract` em vez disso. Esse contrato permite que a
entrada de setup mantenha exportações de plugin/secrets seguras para setup enquanto ainda expõe
um setter de runtime:

```typescript
import { defineBundledChannelSetupEntry } from "openclaw/plugin-sdk/channel-entry-contract";

export default defineBundledChannelSetupEntry({
  importMetaUrl: import.meta.url,
  plugin: {
    specifier: "./channel-plugin-api.js",
    exportName: "myChannelPlugin",
  },
  runtime: {
    specifier: "./runtime-api.js",
    exportName: "setMyChannelRuntime",
  },
});
```

Use esse contrato empacotado apenas quando os fluxos de setup realmente precisarem de um setter
de runtime leve antes que a entrada completa do canal seja carregada.

## Modo de registro

`api.registrationMode` informa ao seu Plugin como ele foi carregado:

| Modo              | Quando                            | O que registrar                                                                         |
| ----------------- | --------------------------------- | --------------------------------------------------------------------------------------- |
| `"full"`          | Inicialização normal do Gateway   | Tudo                                                                                   |
| `"setup-only"`    | Canal desabilitado/não configurado | Apenas registro de canal                                                               |
| `"setup-runtime"` | Fluxo de setup com runtime disponível | Registro de canal mais apenas o runtime leve necessário antes do carregamento da entrada completa |
| `"cli-metadata"`  | Ajuda raiz / captura de metadados da CLI | Apenas descritores de CLI                                                             |

`defineChannelPluginEntry` lida com essa divisão automaticamente. Se você usar
`definePluginEntry` diretamente para um canal, verifique o modo por conta própria:

```typescript
register(api) {
  if (api.registrationMode === "cli-metadata" || api.registrationMode === "full") {
    api.registerCli(/* ... */);
    if (api.registrationMode === "cli-metadata") return;
  }

  api.registerChannel({ plugin: myPlugin });
  if (api.registrationMode !== "full") return;

  // Registros pesados somente de runtime
  api.registerService(/* ... */);
}
```

Trate `"setup-runtime"` como a janela em que superfícies de inicialização somente de setup devem
existir sem reentrar no runtime completo do canal empacotado. Bons usos incluem
registro de canal, rotas HTTP seguras para setup, métodos do Gateway seguros para setup e
helpers de setup delegados. Serviços pesados em segundo plano, registradores de CLI e
bootstraps de SDKs de provedor/cliente ainda pertencem a `"full"`.

Especificamente para registradores de CLI:

- use `descriptors` quando o registrador possuir um ou mais comandos raiz e você
  quiser que o OpenClaw carregue o módulo real da CLI de forma preguiçosa na primeira invocação
- certifique-se de que esses descritores cubram todos os comandos raiz de nível superior expostos pelo
  registrador
- use apenas `commands` somente para caminhos de compatibilidade ansiosos

## Formatos de Plugin

O OpenClaw classifica Plugins carregados pelo comportamento de registro deles:

| Formato              | Descrição                                         |
| -------------------- | ------------------------------------------------- |
| **plain-capability**  | Um tipo de capacidade (por exemplo, somente provedor) |
| **hybrid-capability** | Vários tipos de capacidade (por exemplo, provedor + fala) |
| **hook-only**         | Apenas hooks, sem capacidades                    |
| **non-capability**    | Ferramentas/comandos/serviços, mas sem capacidades |

Use `openclaw plugins inspect <id>` para ver o formato de um Plugin.

## Relacionado

- [Visão geral do SDK](/pt-BR/plugins/sdk-overview) — API de registro e referência de subpaths
- [Helpers de runtime](/pt-BR/plugins/sdk-runtime) — `api.runtime` e `createPluginRuntimeStore`
- [Setup e configuração](/pt-BR/plugins/sdk-setup) — manifesto, entrada de setup, carregamento adiado
- [Plugins de canal](/pt-BR/plugins/sdk-channel-plugins) — criando o objeto `ChannelPlugin`
- [Plugins de provedor](/pt-BR/plugins/sdk-provider-plugins) — registro de provedor e hooks
