---
read_when:
    - Você precisa saber de qual subcaminho do SDK importar
    - Você quer uma referência de todos os métodos de registro em `OpenClawPluginApi`
    - Você está procurando uma exportação específica do SDK
sidebarTitle: SDK Overview
summary: Mapa de importação, referência da API de registro e arquitetura do SDK
title: Visão geral do Plugin SDK
x-i18n:
    generated_at: "2026-04-17T05:36:06Z"
    model: gpt-5.4
    provider: openai
    source_hash: b177fdb6830f415d998a24812bc2c7db8124d3ba77b0174c9a67ac7d747f7e5a
    source_path: plugins/sdk-overview.md
    workflow: 15
---

# Visão geral do Plugin SDK

O SDK de plugin é o contrato tipado entre plugins e o núcleo. Esta página é a
referência para **o que importar** e **o que você pode registrar**.

<Tip>
  **Procurando um guia prático?**
  - Primeiro plugin? Comece com [Primeiros passos](/pt-BR/plugins/building-plugins)
  - Plugin de canal? Veja [Plugins de canal](/pt-BR/plugins/sdk-channel-plugins)
  - Plugin de provedor? Veja [Plugins de provedor](/pt-BR/plugins/sdk-provider-plugins)
</Tip>

## Convenção de importação

Sempre importe de um subcaminho específico:

```typescript
import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
```

Cada subcaminho é um módulo pequeno e autocontido. Isso mantém a inicialização rápida e
evita problemas de dependência circular. Para auxiliares específicos de
entrada/construção de canal, prefira `openclaw/plugin-sdk/channel-core`; mantenha `openclaw/plugin-sdk/core` para
a superfície guarda-chuva mais ampla e auxiliares compartilhados, como
`buildChannelConfigSchema`.

Não adicione nem dependa de seams de conveniência com nome de provedor, como
`openclaw/plugin-sdk/slack`, `openclaw/plugin-sdk/discord`,
`openclaw/plugin-sdk/signal`, `openclaw/plugin-sdk/whatsapp`, ou
seams auxiliares com marca de canal. Plugins empacotados devem compor
subcaminhos genéricos do SDK dentro de seus próprios barrels `api.ts` ou `runtime-api.ts`, e o núcleo
deve usar esses barrels locais do plugin ou adicionar um contrato genérico e restrito do SDK
quando a necessidade for realmente entre canais.

O mapa de exportação gerado ainda contém um pequeno conjunto de
seams auxiliares de plugins empacotados, como `plugin-sdk/feishu`, `plugin-sdk/feishu-setup`,
`plugin-sdk/zalo`, `plugin-sdk/zalo-setup` e `plugin-sdk/matrix*`. Esses
subcaminhos existem apenas para manutenção e compatibilidade de plugins empacotados; eles são
intencionalmente omitidos da tabela comum abaixo e não são o caminho de
importação recomendado para novos plugins de terceiros.

## Referência de subcaminhos

Os subcaminhos usados com mais frequência, agrupados por finalidade. A lista completa gerada de
mais de 200 subcaminhos está em `scripts/lib/plugin-sdk-entrypoints.json`.

Subcaminhos auxiliares reservados para plugins empacotados ainda aparecem nessa lista gerada.
Trate-os como superfícies de detalhe de implementação/compatibilidade, a menos que uma página da documentação
promova explicitamente um deles como público.

### Entrada do plugin

| Subcaminho                | Principais exportações                                                                                                                 |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
| `plugin-sdk/plugin-entry`   | `definePluginEntry`                                                                                                                    |
| `plugin-sdk/core`           | `defineChannelPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase`, `defineSetupPluginEntry`, `buildChannelConfigSchema` |
| `plugin-sdk/config-schema`  | `OpenClawSchema`                                                                                                                       |
| `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry`                                                                                                      |

<AccordionGroup>
  <Accordion title="Subcaminhos de canal">
    | Subcaminho | Principais exportações |
    | --- | --- |
    | `plugin-sdk/channel-core` | `defineChannelPluginEntry`, `defineSetupPluginEntry`, `createChatChannelPlugin`, `createChannelPluginBase` |
    | `plugin-sdk/config-schema` | Exportação do esquema Zod raiz de `openclaw.json` (`OpenClawSchema`) |
    | `plugin-sdk/channel-setup` | `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`, `createOptionalChannelSetupWizard`, além de `DEFAULT_ACCOUNT_ID`, `createTopLevelChannelDmPolicy`, `setSetupChannelEnabled`, `splitSetupEntries` |
    | `plugin-sdk/setup` | Auxiliares compartilhados do assistente de configuração, prompts de allowlist, construtores de status de configuração |
    | `plugin-sdk/setup-runtime` | `createPatchedAccountSetupAdapter`, `createEnvPatchedAccountSetupAdapter`, `createSetupInputPresenceValidator`, `noteChannelLookupFailure`, `noteChannelLookupSummary`, `promptResolvedAllowFrom`, `splitSetupEntries`, `createAllowlistSetupWizardProxy`, `createDelegatedSetupWizardProxy` |
    | `plugin-sdk/setup-adapter-runtime` | `createEnvPatchedAccountSetupAdapter` |
    | `plugin-sdk/setup-tools` | `formatCliCommand`, `detectBinary`, `extractArchive`, `resolveBrewExecutable`, `formatDocsLink`, `CONFIG_DIR` |
    | `plugin-sdk/account-core` | Auxiliares de gate de ação/configuração com múltiplas contas, auxiliares de fallback de conta padrão |
    | `plugin-sdk/account-id` | `DEFAULT_ACCOUNT_ID`, auxiliares de normalização de ID de conta |
    | `plugin-sdk/account-resolution` | Auxiliares de busca de conta + fallback padrão |
    | `plugin-sdk/account-helpers` | Auxiliares restritos para lista de contas/ação de conta |
    | `plugin-sdk/channel-pairing` | `createChannelPairingController` |
    | `plugin-sdk/channel-reply-pipeline` | `createChannelReplyPipeline` |
    | `plugin-sdk/channel-config-helpers` | `createHybridChannelConfigAdapter` |
    | `plugin-sdk/channel-config-schema` | Tipos de esquema de configuração de canal |
    | `plugin-sdk/telegram-command-config` | Auxiliares de normalização/validação de comandos personalizados do Telegram com fallback de contrato empacotado |
    | `plugin-sdk/channel-policy` | `resolveChannelGroupRequireMention` |
    | `plugin-sdk/channel-lifecycle` | `createAccountStatusSink` |
    | `plugin-sdk/inbound-envelope` | Auxiliares compartilhados de rota de entrada + construtor de envelope |
    | `plugin-sdk/inbound-reply-dispatch` | Auxiliares compartilhados de registro e despacho de entrada |
    | `plugin-sdk/messaging-targets` | Auxiliares de análise/correspondência de alvos |
    | `plugin-sdk/outbound-media` | Auxiliares compartilhados de carregamento de mídia de saída |
    | `plugin-sdk/outbound-runtime` | Auxiliares de identidade de saída/delegação de envio |
    | `plugin-sdk/thread-bindings-runtime` | Ciclo de vida de vínculo de thread e auxiliares de adaptador |
    | `plugin-sdk/agent-media-payload` | Construtor legado de payload de mídia do agente |
    | `plugin-sdk/conversation-runtime` | Auxiliares de vínculo de conversa/thread, pareamento e vínculo configurado |
    | `plugin-sdk/runtime-config-snapshot` | Auxiliar de snapshot de configuração em runtime |
    | `plugin-sdk/runtime-group-policy` | Auxiliares de resolução de política de grupo em runtime |
    | `plugin-sdk/channel-status` | Auxiliares compartilhados de snapshot/resumo de status do canal |
    | `plugin-sdk/channel-config-primitives` | Primitivas restritas de esquema de configuração de canal |
    | `plugin-sdk/channel-config-writes` | Auxiliares de autorização de gravação de configuração de canal |
    | `plugin-sdk/channel-plugin-common` | Exportações de prelúdio compartilhadas de plugin de canal |
    | `plugin-sdk/allowlist-config-edit` | Auxiliares de leitura/edição de configuração de allowlist |
    | `plugin-sdk/group-access` | Auxiliares compartilhados de decisão de acesso a grupo |
    | `plugin-sdk/direct-dm` | Auxiliares compartilhados de autenticação/proteção de DM direta |
    | `plugin-sdk/interactive-runtime` | Auxiliares de normalização/redução de payload de resposta interativa |
    | `plugin-sdk/channel-inbound` | Debounce de entrada, correspondência de menção, auxiliares de política de menção e auxiliares de envelope |
    | `plugin-sdk/channel-send-result` | Tipos de resultado de resposta |
    | `plugin-sdk/channel-actions` | `createMessageToolButtonsSchema`, `createMessageToolCardSchema` |
    | `plugin-sdk/channel-targets` | Auxiliares de análise/correspondência de alvos |
    | `plugin-sdk/channel-contract` | Tipos de contrato de canal |
    | `plugin-sdk/channel-feedback` | Ligação de feedback/reação |
    | `plugin-sdk/channel-secret-runtime` | Auxiliares restritos de contrato de segredo, como `collectSimpleChannelFieldAssignments`, `getChannelSurface`, `pushAssignment` e tipos de alvo de segredo |
  </Accordion>

  <Accordion title="Subcaminhos de provedor">
    | Subcaminho | Principais exportações |
    | --- | --- |
    | `plugin-sdk/provider-entry` | `defineSingleProviderPluginEntry` |
    | `plugin-sdk/provider-setup` | Auxiliares curados de configuração de provedor local/self-hosted |
    | `plugin-sdk/self-hosted-provider-setup` | Auxiliares focados de configuração de provedor self-hosted compatível com OpenAI |
    | `plugin-sdk/cli-backend` | Padrões de backend da CLI + constantes de watchdog |
    | `plugin-sdk/provider-auth-runtime` | Auxiliares de runtime para resolução de chave de API para plugins de provedor |
    | `plugin-sdk/provider-auth-api-key` | Auxiliares de onboarding/gravação de perfil de chave de API, como `upsertApiKeyProfile` |
    | `plugin-sdk/provider-auth-result` | Construtor padrão de resultado de autenticação OAuth |
    | `plugin-sdk/provider-auth-login` | Auxiliares compartilhados de login interativo para plugins de provedor |
    | `plugin-sdk/provider-env-vars` | Auxiliares de busca de variáveis de ambiente de autenticação do provedor |
    | `plugin-sdk/provider-auth` | `createProviderApiKeyAuthMethod`, `ensureApiKeyFromOptionEnvOrPrompt`, `upsertAuthProfile`, `upsertApiKeyProfile`, `writeOAuthCredentials` |
    | `plugin-sdk/provider-model-shared` | `ProviderReplayFamily`, `buildProviderReplayFamilyHooks`, `normalizeModelCompat`, construtores compartilhados de política de replay, auxiliares de endpoint do provedor e auxiliares de normalização de ID de modelo, como `normalizeNativeXaiModelId` |
    | `plugin-sdk/provider-catalog-shared` | `findCatalogTemplate`, `buildSingleProviderApiKeyCatalog`, `supportsNativeStreamingUsageCompat`, `applyProviderNativeStreamingUsageCompat` |
    | `plugin-sdk/provider-http` | Auxiliares genéricos de HTTP/capacidade de endpoint do provedor |
    | `plugin-sdk/provider-web-fetch-contract` | Auxiliares restritos de contrato de configuração/seleção de web-fetch, como `enablePluginInConfig` e `WebFetchProviderPlugin` |
    | `plugin-sdk/provider-web-fetch` | Auxiliares de registro/cache de provedor web-fetch |
    | `plugin-sdk/provider-web-search-config-contract` | Auxiliares restritos de configuração/credencial de web-search para provedores que não precisam de ligação de ativação de plugin |
    | `plugin-sdk/provider-web-search-contract` | Auxiliares restritos de contrato de configuração/credencial de web-search, como `createWebSearchProviderContractFields`, `enablePluginInConfig`, `resolveProviderWebSearchPluginConfig` e setters/getters de credenciais com escopo |
    | `plugin-sdk/provider-web-search` | Auxiliares de runtime/registro/cache de provedor web-search |
    | `plugin-sdk/provider-tools` | `ProviderToolCompatFamily`, `buildProviderToolCompatFamilyHooks`, limpeza + diagnóstico de esquema Gemini e auxiliares de compatibilidade xAI, como `resolveXaiModelCompatPatch` / `applyXaiModelCompat` |
    | `plugin-sdk/provider-usage` | `fetchClaudeUsage` e similares |
    | `plugin-sdk/provider-stream` | `ProviderStreamFamily`, `buildProviderStreamFamilyHooks`, `composeProviderStreamWrappers`, tipos de wrapper de stream e auxiliares compartilhados de wrapper para Anthropic/Bedrock/Google/Kilocode/Moonshot/OpenAI/OpenRouter/Z.A.I/MiniMax/Copilot |
    | `plugin-sdk/provider-onboard` | Auxiliares de patch de configuração de onboarding |
    | `plugin-sdk/global-singleton` | Auxiliares de singleton/mapa/cache local ao processo |
  </Accordion>

  <Accordion title="Subcaminhos de autenticação e segurança">
    | Subcaminho | Principais exportações |
    | --- | --- |
    | `plugin-sdk/command-auth` | `resolveControlCommandGate`, auxiliares de registro de comandos, auxiliares de autorização do remetente |
    | `plugin-sdk/command-status` | Construtores de mensagem de comando/ajuda, como `buildCommandsMessagePaginated` e `buildHelpMessage` |
    | `plugin-sdk/approval-auth-runtime` | Resolução de aprovador e auxiliares de autenticação de ação no mesmo chat |
    | `plugin-sdk/approval-client-runtime` | Auxiliares de perfil/filtro de aprovação para execução nativa |
    | `plugin-sdk/approval-delivery-runtime` | Adaptadores nativos de capacidade/entrega de aprovação |
    | `plugin-sdk/approval-gateway-runtime` | Auxiliar compartilhado de resolução de Gateway de aprovação |
    | `plugin-sdk/approval-handler-adapter-runtime` | Auxiliares leves de carregamento de adaptador de aprovação nativa para entrypoints de canal de hot path |
    | `plugin-sdk/approval-handler-runtime` | Auxiliares mais amplos de runtime do manipulador de aprovação; prefira os seams mais restritos de adaptador/Gateway quando forem suficientes |
    | `plugin-sdk/approval-native-runtime` | Auxiliares nativos de alvo de aprovação + vínculo de conta |
    | `plugin-sdk/approval-reply-runtime` | Auxiliares de payload de resposta de aprovação de execução/plugin |
    | `plugin-sdk/command-auth-native` | Auxiliares nativos de autenticação de comando + alvo de sessão nativa |
    | `plugin-sdk/command-detection` | Auxiliares compartilhados de detecção de comandos |
    | `plugin-sdk/command-surface` | Auxiliares de normalização de corpo de comando e superfície de comando |
    | `plugin-sdk/allow-from` | `formatAllowFromLowercase` |
    | `plugin-sdk/channel-secret-runtime` | Auxiliares restritos de coleta de contrato de segredo para superfícies de segredo de canal/plugin |
    | `plugin-sdk/secret-ref-runtime` | Auxiliares restritos de tipagem de `coerceSecretRef` e SecretRef para parsing de contrato/configuração de segredo |
    | `plugin-sdk/security-runtime` | Auxiliares compartilhados de confiança, controle de DM, conteúdo externo e coleta de segredos |
    | `plugin-sdk/ssrf-policy` | Auxiliares de allowlist de host e política de SSRF para rede privada |
    | `plugin-sdk/ssrf-runtime` | Auxiliares de dispatcher fixado, fetch protegido contra SSRF e política de SSRF |
    | `plugin-sdk/secret-input` | Auxiliares de parsing de entrada de segredo |
    | `plugin-sdk/webhook-ingress` | Auxiliares de requisição/alvo de Webhook |
    | `plugin-sdk/webhook-request-guards` | Auxiliares de tamanho do corpo/timeout da requisição |
  </Accordion>

  <Accordion title="Subcaminhos de runtime e armazenamento">
    | Subcaminho | Principais exportações |
    | --- | --- |
    | `plugin-sdk/runtime` | Auxiliares amplos de runtime/logging/backup/instalação de plugin |
    | `plugin-sdk/runtime-env` | Auxiliares restritos de ambiente de runtime, logger, timeout, retry e backoff |
    | `plugin-sdk/channel-runtime-context` | Auxiliares genéricos de registro e busca de contexto de runtime de canal |
    | `plugin-sdk/runtime-store` | `createPluginRuntimeStore` |
    | `plugin-sdk/plugin-runtime` | Auxiliares compartilhados de comando/hook/http/interativo de plugin |
    | `plugin-sdk/hook-runtime` | Auxiliares compartilhados de pipeline de Webhook/hook interno |
    | `plugin-sdk/lazy-runtime` | Auxiliares de importação/vínculo lazy de runtime, como `createLazyRuntimeModule`, `createLazyRuntimeMethod` e `createLazyRuntimeSurface` |
    | `plugin-sdk/process-runtime` | Auxiliares de execução de processo |
    | `plugin-sdk/cli-runtime` | Auxiliares de formatação, espera e versão da CLI |
    | `plugin-sdk/gateway-runtime` | Auxiliares de cliente Gateway e patch de status de canal |
    | `plugin-sdk/config-runtime` | Auxiliares de carregamento/gravação de configuração |
    | `plugin-sdk/telegram-command-config` | Normalização de nome/descrição de comando do Telegram e verificações de duplicidade/conflito, mesmo quando a superfície de contrato empacotada do Telegram não está disponível |
    | `plugin-sdk/approval-runtime` | Auxiliares de aprovação de execução/plugin, construtores de capacidade de aprovação, auxiliares de autenticação/perfil, auxiliares nativos de roteamento/runtime |
    | `plugin-sdk/reply-runtime` | Auxiliares compartilhados de runtime de entrada/resposta, fragmentação, despacho, Heartbeat, planejador de resposta |
    | `plugin-sdk/reply-dispatch-runtime` | Auxiliares restritos de despacho/finalização de resposta |
    | `plugin-sdk/reply-history` | Auxiliares compartilhados de histórico de respostas de janela curta, como `buildHistoryContext`, `recordPendingHistoryEntry` e `clearHistoryEntriesIfEnabled` |
    | `plugin-sdk/reply-reference` | `createReplyReferencePlanner` |
    | `plugin-sdk/reply-chunking` | Auxiliares restritos de fragmentação de texto/markdown |
    | `plugin-sdk/session-store-runtime` | Auxiliares de caminho da store de sessão + updated-at |
    | `plugin-sdk/state-paths` | Auxiliares de caminho de diretório de estado/OAuth |
    | `plugin-sdk/routing` | Auxiliares de roteamento/chave de sessão/vínculo de conta, como `resolveAgentRoute`, `buildAgentSessionKey` e `resolveDefaultAgentBoundAccountId` |
    | `plugin-sdk/status-helpers` | Auxiliares compartilhados de resumo de status de canal/conta, padrões de estado de runtime e auxiliares de metadados de problema |
    | `plugin-sdk/target-resolver-runtime` | Auxiliares compartilhados de resolvedor de alvo |
    | `plugin-sdk/string-normalization-runtime` | Auxiliares de normalização de slug/string |
    | `plugin-sdk/request-url` | Extrair URLs em string de entradas do tipo fetch/request |
    | `plugin-sdk/run-command` | Executor de comandos com tempo controlado e resultados normalizados de stdout/stderr |
    | `plugin-sdk/param-readers` | Leitores comuns de parâmetros de ferramenta/CLI |
    | `plugin-sdk/tool-payload` | Extrair payloads normalizados de objetos de resultado de ferramenta |
    | `plugin-sdk/tool-send` | Extrair campos canônicos de alvo de envio de argumentos de ferramenta |
    | `plugin-sdk/temp-path` | Auxiliares compartilhados de caminho temporário para download |
    | `plugin-sdk/logging-core` | Auxiliares de logger de subsistema e redação |
    | `plugin-sdk/markdown-table-runtime` | Auxiliares de modo de tabela em Markdown |
    | `plugin-sdk/json-store` | Pequenos auxiliares de leitura/gravação de estado JSON |
    | `plugin-sdk/file-lock` | Auxiliares de file lock reentrante |
    | `plugin-sdk/persistent-dedupe` | Auxiliares de cache de deduplicação com persistência em disco |
    | `plugin-sdk/acp-runtime` | Auxiliares de runtime/sessão do ACP e despacho de resposta |
    | `plugin-sdk/agent-config-primitives` | Primitivas restritas de esquema de configuração de runtime de agente |
    | `plugin-sdk/boolean-param` | Leitor flexível de parâmetro booleano |
    | `plugin-sdk/dangerous-name-runtime` | Auxiliares de resolução de correspondência de nomes perigosos |
    | `plugin-sdk/device-bootstrap` | Auxiliares de bootstrap de dispositivo e token de pareamento |
    | `plugin-sdk/extension-shared` | Primitivas auxiliares compartilhadas de canal passivo, status e proxy ambiente |
    | `plugin-sdk/models-provider-runtime` | Auxiliares de resposta de provedor/comando `/models` |
    | `plugin-sdk/skill-commands-runtime` | Auxiliares de listagem de comandos de Skills |
    | `plugin-sdk/native-command-registry` | Auxiliares de registro/construção/serialização de comandos nativos |
    | `plugin-sdk/agent-harness` | Superfície experimental de plugin confiável para harnesses de agente de baixo nível: tipos de harness, auxiliares de condução/aborto de execução ativa, auxiliares de ponte de ferramenta do OpenClaw e utilitários de resultado de tentativa |
    | `plugin-sdk/provider-zai-endpoint` | Auxiliares de detecção de endpoint do Z.A.I |
    | `plugin-sdk/infra-runtime` | Auxiliares de evento do sistema/Heartbeat |
    | `plugin-sdk/collection-runtime` | Pequenos auxiliares de cache limitado |
    | `plugin-sdk/diagnostic-runtime` | Auxiliares de flag e evento de diagnóstico |
    | `plugin-sdk/error-runtime` | Grafo de erros, formatação, auxiliares compartilhados de classificação de erros, `isApprovalNotFoundError` |
    | `plugin-sdk/fetch-runtime` | Auxiliares de fetch encapsulado, proxy e busca fixada |
    | `plugin-sdk/host-runtime` | Auxiliares de normalização de hostname e host SCP |
    | `plugin-sdk/retry-runtime` | Auxiliares de configuração de retry e executor de retry |
    | `plugin-sdk/agent-runtime` | Auxiliares de diretório/identidade/workspace de agente |
    | `plugin-sdk/directory-runtime` | Consulta/deduplicação de diretório com base em configuração |
    | `plugin-sdk/keyed-async-queue` | `KeyedAsyncQueue` |
  </Accordion>

  <Accordion title="Subcaminhos de capacidade e testes">
    | Subcaminho | Principais exportações |
    | --- | --- |
    | `plugin-sdk/media-runtime` | Auxiliares compartilhados de busca/transformação/armazenamento de mídia, além de construtores de payload de mídia |
    | `plugin-sdk/media-generation-runtime` | Auxiliares compartilhados de failover de geração de mídia, seleção de candidatos e mensagens para modelo ausente |
    | `plugin-sdk/media-understanding` | Tipos de provedor de entendimento de mídia, além de exportações auxiliares voltadas ao provedor para imagem/áudio |
    | `plugin-sdk/text-runtime` | Auxiliares compartilhados de texto/markdown/logging, como remoção de texto visível ao assistente, auxiliares de renderização/fragmentação/tabela em markdown, auxiliares de redação, auxiliares de tag de diretiva e utilitários de texto seguro |
    | `plugin-sdk/text-chunking` | Auxiliar de fragmentação de texto de saída |
    | `plugin-sdk/speech` | Tipos de provedor de fala, além de auxiliares voltados ao provedor para diretiva, registro e validação |
    | `plugin-sdk/speech-core` | Tipos compartilhados de provedor de fala, auxiliares de registro, diretiva e normalização |
    | `plugin-sdk/realtime-transcription` | Tipos de provedor de transcrição em tempo real e auxiliares de registro |
    | `plugin-sdk/realtime-voice` | Tipos de provedor de voz em tempo real e auxiliares de registro |
    | `plugin-sdk/image-generation` | Tipos de provedor de geração de imagem |
    | `plugin-sdk/image-generation-core` | Tipos compartilhados de geração de imagem, auxiliares de failover, autenticação e registro |
    | `plugin-sdk/music-generation` | Tipos de provedor/requisição/resultado de geração de música |
    | `plugin-sdk/music-generation-core` | Tipos compartilhados de geração de música, auxiliares de failover, busca de provedor e parsing de referência de modelo |
    | `plugin-sdk/video-generation` | Tipos de provedor/requisição/resultado de geração de vídeo |
    | `plugin-sdk/video-generation-core` | Tipos compartilhados de geração de vídeo, auxiliares de failover, busca de provedor e parsing de referência de modelo |
    | `plugin-sdk/webhook-targets` | Registro de alvos de Webhook e auxiliares de instalação de rota |
    | `plugin-sdk/webhook-path` | Auxiliares de normalização de caminho de Webhook |
    | `plugin-sdk/web-media` | Auxiliares compartilhados de carregamento de mídia remota/local |
    | `plugin-sdk/zod` | `zod` reexportado para consumidores do Plugin SDK |
    | `plugin-sdk/testing` | `installCommonResolveTargetErrorCases`, `shouldAckReaction` |
  </Accordion>

  <Accordion title="Subcaminhos de memória">
    | Subcaminho | Principais exportações |
    | --- | --- |
    | `plugin-sdk/memory-core` | Superfície auxiliar empacotada de memory-core para auxiliares de manager/configuração/arquivo/CLI |
    | `plugin-sdk/memory-core-engine-runtime` | Fachada de runtime de índice/busca de memória |
    | `plugin-sdk/memory-core-host-engine-foundation` | Exportações do engine foundation do host de memória |
    | `plugin-sdk/memory-core-host-engine-embeddings` | Contratos de embedding do host de memória, acesso ao registro, provedor local e auxiliares genéricos de lote/remoto |
    | `plugin-sdk/memory-core-host-engine-qmd` | Exportações do engine QMD do host de memória |
    | `plugin-sdk/memory-core-host-engine-storage` | Exportações do engine de armazenamento do host de memória |
    | `plugin-sdk/memory-core-host-multimodal` | Auxiliares multimodais do host de memória |
    | `plugin-sdk/memory-core-host-query` | Auxiliares de consulta do host de memória |
    | `plugin-sdk/memory-core-host-secret` | Auxiliares de segredo do host de memória |
    | `plugin-sdk/memory-core-host-events` | Auxiliares de journal de eventos do host de memória |
    | `plugin-sdk/memory-core-host-status` | Auxiliares de status do host de memória |
    | `plugin-sdk/memory-core-host-runtime-cli` | Auxiliares de runtime da CLI do host de memória |
    | `plugin-sdk/memory-core-host-runtime-core` | Auxiliares centrais de runtime do host de memória |
    | `plugin-sdk/memory-core-host-runtime-files` | Auxiliares de arquivo/runtime do host de memória |
    | `plugin-sdk/memory-host-core` | Alias neutro em relação ao fornecedor para os auxiliares centrais de runtime do host de memória |
    | `plugin-sdk/memory-host-events` | Alias neutro em relação ao fornecedor para os auxiliares de journal de eventos do host de memória |
    | `plugin-sdk/memory-host-files` | Alias neutro em relação ao fornecedor para os auxiliares de arquivo/runtime do host de memória |
    | `plugin-sdk/memory-host-markdown` | Auxiliares compartilhados de managed-markdown para plugins adjacentes à memória |
    | `plugin-sdk/memory-host-search` | Fachada de runtime de Active Memory para acesso ao gerenciador de busca |
    | `plugin-sdk/memory-host-status` | Alias neutro em relação ao fornecedor para os auxiliares de status do host de memória |
    | `plugin-sdk/memory-lancedb` | Superfície auxiliar empacotada de memory-lancedb |
  </Accordion>

  <Accordion title="Subcaminhos auxiliares empacotados reservados">
    | Família | Subcaminhos atuais | Uso pretendido |
    | --- | --- | --- |
    | Browser | `plugin-sdk/browser-cdp`, `plugin-sdk/browser-config-runtime`, `plugin-sdk/browser-config-support`, `plugin-sdk/browser-control-auth`, `plugin-sdk/browser-node-runtime`, `plugin-sdk/browser-profiles`, `plugin-sdk/browser-security-runtime`, `plugin-sdk/browser-setup-tools`, `plugin-sdk/browser-support` | Auxiliares de suporte do Plugin de navegador empacotado (`browser-support` continua sendo o barrel de compatibilidade) |
    | Matrix | `plugin-sdk/matrix`, `plugin-sdk/matrix-helper`, `plugin-sdk/matrix-runtime-heavy`, `plugin-sdk/matrix-runtime-shared`, `plugin-sdk/matrix-runtime-surface`, `plugin-sdk/matrix-surface`, `plugin-sdk/matrix-thread-bindings` | Superfície auxiliar/runtime empacotada do Matrix |
    | Line | `plugin-sdk/line`, `plugin-sdk/line-core`, `plugin-sdk/line-runtime`, `plugin-sdk/line-surface` | Superfície auxiliar/runtime empacotada do LINE |
    | IRC | `plugin-sdk/irc`, `plugin-sdk/irc-surface` | Superfície auxiliar empacotada do IRC |
    | Auxiliares específicos de canal | `plugin-sdk/googlechat`, `plugin-sdk/zalouser`, `plugin-sdk/bluebubbles`, `plugin-sdk/bluebubbles-policy`, `plugin-sdk/mattermost`, `plugin-sdk/mattermost-policy`, `plugin-sdk/feishu-conversation`, `plugin-sdk/msteams`, `plugin-sdk/nextcloud-talk`, `plugin-sdk/nostr`, `plugin-sdk/tlon`, `plugin-sdk/twitch` | Seams de compatibilidade/auxiliares de canais empacotados |
    | Auxiliares específicos de autenticação/plugin | `plugin-sdk/github-copilot-login`, `plugin-sdk/github-copilot-token`, `plugin-sdk/diagnostics-otel`, `plugin-sdk/diffs`, `plugin-sdk/llm-task`, `plugin-sdk/thread-ownership`, `plugin-sdk/voice-call` | Seams auxiliares de recursos/plugins empacotados; `plugin-sdk/github-copilot-token` atualmente exporta `DEFAULT_COPILOT_API_BASE_URL`, `deriveCopilotApiBaseUrlFromToken` e `resolveCopilotApiToken` |
  </Accordion>
</AccordionGroup>

## API de registro

O callback `register(api)` recebe um objeto `OpenClawPluginApi` com estes
métodos:

### Registro de capacidades

| Método                                           | O que ele registra                  |
| ------------------------------------------------ | ----------------------------------- |
| `api.registerProvider(...)`                      | Inferência de texto (LLM)           |
| `api.registerAgentHarness(...)`                  | Executor experimental de agente de baixo nível |
| `api.registerCliBackend(...)`                    | Backend de inferência local da CLI  |
| `api.registerChannel(...)`                       | Canal de mensagens                  |
| `api.registerSpeechProvider(...)`                | Síntese de texto para fala / STT    |
| `api.registerRealtimeTranscriptionProvider(...)` | Transcrição em tempo real por streaming |
| `api.registerRealtimeVoiceProvider(...)`         | Sessões de voz duplex em tempo real |
| `api.registerMediaUnderstandingProvider(...)`    | Análise de imagem/áudio/vídeo       |
| `api.registerImageGenerationProvider(...)`       | Geração de imagem                   |
| `api.registerMusicGenerationProvider(...)`       | Geração de música                   |
| `api.registerVideoGenerationProvider(...)`       | Geração de vídeo                    |
| `api.registerWebFetchProvider(...)`              | Provedor de busca/scrape da web     |
| `api.registerWebSearchProvider(...)`             | Busca na web                        |

### Ferramentas e comandos

| Método                          | O que ele registra                           |
| ------------------------------- | -------------------------------------------- |
| `api.registerTool(tool, opts?)` | Ferramenta do agente (obrigatória ou `{ optional: true }`) |
| `api.registerCommand(def)`      | Comando personalizado (ignora o LLM)        |

### Infraestrutura

| Método                                         | O que ele registra                     |
| ---------------------------------------------- | -------------------------------------- |
| `api.registerHook(events, handler, opts?)`     | Hook de evento                         |
| `api.registerHttpRoute(params)`                | Endpoint HTTP do Gateway               |
| `api.registerGatewayMethod(name, handler)`     | Método RPC do Gateway                  |
| `api.registerCli(registrar, opts?)`            | Subcomando da CLI                      |
| `api.registerService(service)`                 | Serviço em segundo plano               |
| `api.registerInteractiveHandler(registration)` | Manipulador interativo                 |
| `api.registerMemoryPromptSupplement(builder)`  | Seção de prompt aditiva adjacente à memória |
| `api.registerMemoryCorpusSupplement(adapter)`  | Corpus aditivo de busca/leitura de memória |

Namespaces administrativos reservados do núcleo (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) sempre permanecem `operator.admin`, mesmo que um plugin tente atribuir um
escopo mais restrito ao método do Gateway. Prefira prefixos específicos do plugin para
métodos pertencentes ao plugin.

### Metadados de registro da CLI

`api.registerCli(registrar, opts?)` aceita dois tipos de metadados de nível superior:

- `commands`: raízes de comando explícitas pertencentes ao registrador
- `descriptors`: descritores de comando em tempo de parsing usados para ajuda da CLI raiz,
  roteamento e registro lazy da CLI do plugin

Se você quiser que um comando de plugin permaneça com carregamento lazy no caminho normal da CLI raiz,
forneça `descriptors` que cubram toda raiz de comando de nível superior exposta por esse
registrador.

```typescript
api.registerCli(
  async ({ program }) => {
    const { registerMatrixCli } = await import("./src/cli.js");
    registerMatrixCli({ program });
  },
  {
    descriptors: [
      {
        name: "matrix",
        description: "Gerencie contas do Matrix, verificação, dispositivos e estado do perfil",
        hasSubcommands: true,
      },
    ],
  },
);
```

Use `commands` sozinho apenas quando você não precisar de registro lazy na CLI raiz.
Esse caminho de compatibilidade eager continua sendo compatível, mas não instala
placeholders com suporte de descritor para carregamento lazy em tempo de parsing.

### Registro de backend da CLI

`api.registerCliBackend(...)` permite que um plugin seja o dono da configuração padrão de um
backend local de CLI de IA, como `codex-cli`.

- O `id` do backend se torna o prefixo do provedor em referências de modelo como `codex-cli/gpt-5`.
- A `config` do backend usa o mesmo formato de `agents.defaults.cliBackends.<id>`.
- A configuração do usuário continua tendo prioridade. O OpenClaw mescla `agents.defaults.cliBackends.<id>` sobre o
  padrão do plugin antes de executar a CLI.
- Use `normalizeConfig` quando um backend precisar de reescritas de compatibilidade após a mesclagem
  (por exemplo, normalizando formatos antigos de flags).

### Slots exclusivos

| Método                                     | O que ele registra                                                                                                                                         |
| ------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `api.registerContextEngine(id, factory)`   | Mecanismo de contexto (apenas um ativo por vez). O callback `assemble()` recebe `availableTools` e `citationsMode` para que o mecanismo adapte adições ao prompt. |
| `api.registerMemoryCapability(capability)` | Capacidade de memória unificada                                                                                                                           |
| `api.registerMemoryPromptSection(builder)` | Construtor de seção de prompt de memória                                                                                                                  |
| `api.registerMemoryFlushPlan(resolver)`    | Resolvedor de plano de flush de memória                                                                                                                   |
| `api.registerMemoryRuntime(runtime)`       | Adaptador de runtime de memória                                                                                                                           |

### Adaptadores de embedding de memória

| Método                                         | O que ele registra                         |
| ---------------------------------------------- | ------------------------------------------ |
| `api.registerMemoryEmbeddingProvider(adapter)` | Adaptador de embedding de memória para o Plugin ativo |

- `registerMemoryCapability` é a API exclusiva preferida para plugin de memória.
- `registerMemoryCapability` também pode expor `publicArtifacts.listArtifacts(...)`
  para que plugins complementares consumam artefatos de memória exportados por meio de
  `openclaw/plugin-sdk/memory-host-core` em vez de acessar o layout privado de um
  plugin de memória específico.
- `registerMemoryPromptSection`, `registerMemoryFlushPlan` e
  `registerMemoryRuntime` são APIs exclusivas de plugin de memória compatíveis com versões legadas.
- `registerMemoryEmbeddingProvider` permite que o Plugin de memória ativo registre um
  ou mais IDs de adaptador de embedding (por exemplo, `openai`, `gemini` ou um ID
  personalizado definido pelo plugin).
- Configurações do usuário como `agents.defaults.memorySearch.provider` e
  `agents.defaults.memorySearch.fallback` são resolvidas com base nesses IDs de
  adaptador registrados.

### Eventos e ciclo de vida

| Método                                       | O que ele faz                 |
| -------------------------------------------- | ----------------------------- |
| `api.on(hookName, handler, opts?)`           | Hook tipado de ciclo de vida  |
| `api.onConversationBindingResolved(handler)` | Callback de vínculo de conversa |

### Semântica de decisão de hook

- `before_tool_call`: retornar `{ block: true }` é terminal. Assim que qualquer manipulador definir isso, manipuladores de menor prioridade serão ignorados.
- `before_tool_call`: retornar `{ block: false }` é tratado como nenhuma decisão (igual a omitir `block`), não como uma substituição.
- `before_install`: retornar `{ block: true }` é terminal. Assim que qualquer manipulador definir isso, manipuladores de menor prioridade serão ignorados.
- `before_install`: retornar `{ block: false }` é tratado como nenhuma decisão (igual a omitir `block`), não como uma substituição.
- `reply_dispatch`: retornar `{ handled: true, ... }` é terminal. Assim que qualquer manipulador assumir o despacho, manipuladores de menor prioridade e o caminho padrão de despacho do modelo serão ignorados.
- `message_sending`: retornar `{ cancel: true }` é terminal. Assim que qualquer manipulador definir isso, manipuladores de menor prioridade serão ignorados.
- `message_sending`: retornar `{ cancel: false }` é tratado como nenhuma decisão (igual a omitir `cancel`), não como uma substituição.

### Campos do objeto da API

| Campo                    | Tipo                      | Descrição                                                                                  |
| ------------------------ | ------------------------- | ------------------------------------------------------------------------------------------ |
| `api.id`                 | `string`                  | ID do plugin                                                                               |
| `api.name`               | `string`                  | Nome de exibição                                                                           |
| `api.version`            | `string?`                 | Versão do plugin (opcional)                                                                |
| `api.description`        | `string?`                 | Descrição do plugin (opcional)                                                             |
| `api.source`             | `string`                  | Caminho de origem do plugin                                                                |
| `api.rootDir`            | `string?`                 | Diretório raiz do plugin (opcional)                                                        |
| `api.config`             | `OpenClawConfig`          | Snapshot da configuração atual (snapshot ativo em memória no runtime quando disponível)    |
| `api.pluginConfig`       | `Record<string, unknown>` | Configuração específica do plugin em `plugins.entries.<id>.config`                         |
| `api.runtime`            | `PluginRuntime`           | [Auxiliares de runtime](/pt-BR/plugins/sdk-runtime)                                              |
| `api.logger`             | `PluginLogger`            | Logger com escopo (`debug`, `info`, `warn`, `error`)                                       |
| `api.registrationMode`   | `PluginRegistrationMode`  | Modo de carregamento atual; `"setup-runtime"` é a janela leve de inicialização/configuração antes da entrada completa |
| `api.resolvePath(input)` | `(string) => string`      | Resolve o caminho em relação à raiz do plugin                                              |

## Convenção de módulos internos

Dentro do seu plugin, use arquivos barrel locais para importações internas:

```
my-plugin/
  api.ts            # Exportações públicas para consumidores externos
  runtime-api.ts    # Exportações de runtime somente internas
  index.ts          # Ponto de entrada do plugin
  setup-entry.ts    # Entrada leve somente para configuração (opcional)
```

<Warning>
  Nunca importe seu próprio plugin por meio de `openclaw/plugin-sdk/<your-plugin>`
  a partir de código de produção. Direcione importações internas por `./api.ts` ou
  `./runtime-api.ts`. O caminho do SDK é apenas o contrato externo.
</Warning>

Superfícies públicas de plugins empacotados carregadas por fachada (`api.ts`, `runtime-api.ts`,
`index.ts`, `setup-entry.ts` e arquivos públicos de entrada semelhantes) agora preferem o
snapshot ativo de configuração do runtime quando o OpenClaw já está em execução. Se ainda não existir
um snapshot de runtime, elas recorrem à configuração resolvida no arquivo em disco.

Plugins de provedor também podem expor um barrel de contrato local e restrito ao plugin quando um
auxiliar for intencionalmente específico do provedor e ainda não pertencer a um subcaminho genérico do SDK.
Exemplo empacotado atual: o provedor Anthropic mantém seus auxiliares de stream do Claude em seu próprio
seam público `api.ts` / `contract-api.ts`, em vez de promover a lógica de cabeçalho beta do Anthropic e `service_tier`
para um contrato genérico `plugin-sdk/*`.

Outros exemplos empacotados atuais:

- `@openclaw/openai-provider`: `api.ts` exporta construtores de provedor,
  auxiliares de modelo padrão e construtores de provedor em tempo real
- `@openclaw/openrouter-provider`: `api.ts` exporta o construtor do provedor e
  auxiliares de onboarding/configuração

<Warning>
  O código de produção de extensões também deve evitar importações de `openclaw/plugin-sdk/<other-plugin>`.
  Se um auxiliar for realmente compartilhado, promova-o a um subcaminho neutro do SDK,
  como `openclaw/plugin-sdk/speech`, `.../provider-model-shared` ou outra
  superfície orientada por capacidade, em vez de acoplar dois plugins.
</Warning>

## Relacionado

- [Pontos de entrada](/pt-BR/plugins/sdk-entrypoints) — opções de `definePluginEntry` e `defineChannelPluginEntry`
- [Auxiliares de runtime](/pt-BR/plugins/sdk-runtime) — referência completa do namespace `api.runtime`
- [Configuração e setup](/pt-BR/plugins/sdk-setup) — empacotamento, manifests, esquemas de configuração
- [Testes](/pt-BR/plugins/sdk-testing) — utilitários de teste e regras de lint
- [Migração do SDK](/pt-BR/plugins/sdk-migration) — migração de superfícies descontinuadas
- [Internals de plugin](/pt-BR/plugins/architecture) — arquitetura detalhada e modelo de capacidade
