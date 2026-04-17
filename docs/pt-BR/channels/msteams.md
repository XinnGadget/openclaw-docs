---
read_when:
    - Trabalhando nos recursos do canal Microsoft Teams
summary: status do suporte de bot do Microsoft Teams, capacidades e configuração
title: Microsoft Teams
x-i18n:
    generated_at: "2026-04-12T00:18:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3e6841a618fb030e4c2029b3652d45dedd516392e2ae17309ff46b93648ffb79
    source_path: channels/msteams.md
    workflow: 15
---

# Microsoft Teams

> "Abandonai toda esperança, vós que aqui entrais."

Atualizado: 2026-03-25

Status: texto + anexos em DM são compatíveis; o envio de arquivos em canal/grupo exige `sharePointSiteId` + permissões do Graph (consulte [Envio de arquivos em chats de grupo](#sending-files-in-group-chats)). Enquetes são enviadas por meio de Adaptive Cards. As ações de mensagem expõem `upload-file` explícito para envios com arquivo primeiro.

## Plugin incluído

O Microsoft Teams é fornecido como um plugin incluído nas versões atuais do OpenClaw, portanto
nenhuma instalação separada é necessária na compilação empacotada normal.

Se você estiver em uma versão mais antiga ou em uma instalação personalizada que exclui o Teams incluído,
instale-o manualmente:

```bash
openclaw plugins install @openclaw/msteams
```

Checkout local (ao executar a partir de um repositório git):

```bash
openclaw plugins install ./path/to/local/msteams-plugin
```

Detalhes: [Plugins](/pt-BR/tools/plugin)

## Configuração rápida (iniciante)

1. Verifique se o plugin do Microsoft Teams está disponível.
   - As versões empacotadas atuais do OpenClaw já o incluem.
   - Instalações antigas/personalizadas podem adicioná-lo manualmente com os comandos acima.
2. Crie um **Azure Bot** (App ID + segredo do cliente + ID do locatário).
3. Configure o OpenClaw com essas credenciais.
4. Exponha `/api/messages` (porta 3978 por padrão) por meio de uma URL pública ou túnel.
5. Instale o pacote do aplicativo Teams e inicie o gateway.

Configuração mínima (segredo do cliente):

```json5
{
  channels: {
    msteams: {
      enabled: true,
      appId: "<APP_ID>",
      appPassword: "<APP_PASSWORD>",
      tenantId: "<TENANT_ID>",
      webhook: { port: 3978, path: "/api/messages" },
    },
  },
}
```

Para implantações em produção, considere usar [autenticação federada](#federated-authentication-certificate--managed-identity) (certificado ou identidade gerenciada) em vez de segredos do cliente.

Observação: chats em grupo são bloqueados por padrão (`channels.msteams.groupPolicy: "allowlist"`). Para permitir respostas em grupo, defina `channels.msteams.groupAllowFrom` (ou use `groupPolicy: "open"` para permitir qualquer membro, condicionado a menção).

## Objetivos

- Conversar com o OpenClaw por DMs, chats em grupo ou canais do Teams.
- Manter o roteamento determinístico: as respostas sempre voltam para o canal em que chegaram.
- Adotar por padrão um comportamento seguro no canal (menções obrigatórias, salvo configuração em contrário).

## Escritas de configuração

Por padrão, o Microsoft Teams pode gravar atualizações de configuração acionadas por `/config set|unset` (requer `commands.config: true`).

Desative com:

```json5
{
  channels: { msteams: { configWrites: false } },
}
```

## Controle de acesso (DMs + grupos)

**Acesso por DM**

- Padrão: `channels.msteams.dmPolicy = "pairing"`. Remetentes desconhecidos são ignorados até serem aprovados.
- `channels.msteams.allowFrom` deve usar IDs de objeto AAD estáveis.
- UPNs/nomes de exibição são mutáveis; a correspondência direta fica desativada por padrão e só é ativada com `channels.msteams.dangerouslyAllowNameMatching: true`.
- O assistente pode resolver nomes para IDs por meio do Microsoft Graph quando as credenciais permitirem.

**Acesso em grupo**

- Padrão: `channels.msteams.groupPolicy = "allowlist"` (bloqueado, a menos que você adicione `groupAllowFrom`). Use `channels.defaults.groupPolicy` para substituir o padrão quando não definido.
- `channels.msteams.groupAllowFrom` controla quais remetentes podem acionar em chats/canais de grupo (usa `channels.msteams.allowFrom` como fallback).
- Defina `groupPolicy: "open"` para permitir qualquer membro (ainda condicionado a menção por padrão).
- Para não permitir **nenhum canal**, defina `channels.msteams.groupPolicy: "disabled"`.

Exemplo:

```json5
{
  channels: {
    msteams: {
      groupPolicy: "allowlist",
      groupAllowFrom: ["user@org.com"],
    },
  },
}
```

**Teams + lista de permissões de canais**

- Delimite respostas em grupos/canais listando equipes e canais em `channels.msteams.teams`.
- As chaves devem usar IDs estáveis de equipe e IDs de conversa de canal.
- Quando `groupPolicy="allowlist"` e houver uma lista de permissões de equipes, somente as equipes/canais listados serão aceitos (condicionados a menção).
- O assistente de configuração aceita entradas `Team/Channel` e as armazena para você.
- Na inicialização, o OpenClaw resolve nomes de equipe/canal e nomes de usuários da lista de permissões para IDs (quando as permissões do Graph permitem)
  e registra o mapeamento em log; nomes de equipe/canal não resolvidos são mantidos como digitados, mas ignorados para roteamento por padrão, a menos que `channels.msteams.dangerouslyAllowNameMatching: true` esteja ativado.

Exemplo:

```json5
{
  channels: {
    msteams: {
      groupPolicy: "allowlist",
      teams: {
        "My Team": {
          channels: {
            General: { requireMention: true },
          },
        },
      },
    },
  },
}
```

## Como funciona

1. Verifique se o plugin do Microsoft Teams está disponível.
   - As versões empacotadas atuais do OpenClaw já o incluem.
   - Instalações antigas/personalizadas podem adicioná-lo manualmente com os comandos acima.
2. Crie um **Azure Bot** (App ID + segredo + ID do locatário).
3. Crie um **pacote de aplicativo Teams** que faça referência ao bot e inclua as permissões RSC abaixo.
4. Envie/instale o aplicativo Teams em uma equipe (ou no escopo pessoal para DMs).
5. Configure `msteams` em `~/.openclaw/openclaw.json` (ou variáveis de ambiente) e inicie o gateway.
6. O gateway escuta o tráfego de webhook do Bot Framework em `/api/messages` por padrão.

## Configuração do Azure Bot (Pré-requisitos)

Antes de configurar o OpenClaw, você precisa criar um recurso Azure Bot.

### Etapa 1: Criar Azure Bot

1. Acesse [Create Azure Bot](https://portal.azure.com/#create/Microsoft.AzureBot)
2. Preencha a guia **Basics**:

   | Campo              | Valor                                                    |
   | ------------------ | -------------------------------------------------------- |
   | **Bot handle**     | O nome do seu bot, por exemplo, `openclaw-msteams` (deve ser único) |
   | **Subscription**   | Selecione sua assinatura do Azure                        |
   | **Resource group** | Crie um novo ou use um existente                         |
   | **Pricing tier**   | **Free** para desenvolvimento/testes                     |
   | **Type of App**    | **Single Tenant** (recomendado - consulte a observação abaixo) |
   | **Creation type**  | **Create new Microsoft App ID**                          |

> **Aviso de descontinuação:** a criação de novos bots multilocatário foi descontinuada após 2025-07-31. Use **Single Tenant** para novos bots.

3. Clique em **Review + create** → **Create** (aguarde ~1-2 minutos)

### Etapa 2: Obter credenciais

1. Acesse seu recurso Azure Bot → **Configuration**
2. Copie **Microsoft App ID** → este é o seu `appId`
3. Clique em **Manage Password** → vá para o Registro de Aplicativo
4. Em **Certificates & secrets** → **New client secret** → copie o **Value** → este é o seu `appPassword`
5. Acesse **Overview** → copie **Directory (tenant) ID** → este é o seu `tenantId`

### Etapa 3: Configurar endpoint de mensagens

1. Em Azure Bot → **Configuration**
2. Defina **Messaging endpoint** como a URL do seu webhook:
   - Produção: `https://your-domain.com/api/messages`
   - Desenvolvimento local: use um túnel (consulte [Desenvolvimento local](#local-development-tunneling) abaixo)

### Etapa 4: Ativar canal Teams

1. Em Azure Bot → **Channels**
2. Clique em **Microsoft Teams** → Configure → Save
3. Aceite os Termos de Serviço

## Autenticação federada (Certificado + Identidade Gerenciada)

> Adicionado em 2026.3.24

Para implantações em produção, o OpenClaw oferece suporte a **autenticação federada** como uma alternativa mais segura aos segredos do cliente. Há dois métodos disponíveis:

### Opção A: Autenticação baseada em certificado

Use um certificado PEM registrado no registro do aplicativo Entra ID.

**Configuração:**

1. Gere ou obtenha um certificado (formato PEM com chave privada).
2. Em Entra ID → App Registration → **Certificates & secrets** → **Certificates** → envie o certificado público.

**Configuração:**

```json5
{
  channels: {
    msteams: {
      enabled: true,
      appId: "<APP_ID>",
      tenantId: "<TENANT_ID>",
      authType: "federated",
      certificatePath: "/path/to/cert.pem",
      webhook: { port: 3978, path: "/api/messages" },
    },
  },
}
```

**Variáveis de ambiente:**

- `MSTEAMS_AUTH_TYPE=federated`
- `MSTEAMS_CERTIFICATE_PATH=/path/to/cert.pem`

### Opção B: Identidade Gerenciada do Azure

Use a Identidade Gerenciada do Azure para autenticação sem senha. Isso é ideal para implantações na infraestrutura do Azure (AKS, App Service, VMs do Azure) em que uma identidade gerenciada está disponível.

**Como funciona:**

1. O pod/VM do bot tem uma identidade gerenciada (atribuída pelo sistema ou pelo usuário).
2. Uma **credencial de identidade federada** vincula a identidade gerenciada ao registro do aplicativo Entra ID.
3. Em tempo de execução, o OpenClaw usa `@azure/identity` para adquirir tokens do endpoint Azure IMDS (`169.254.169.254`).
4. O token é passado ao SDK do Teams para autenticação do bot.

**Pré-requisitos:**

- Infraestrutura do Azure com identidade gerenciada ativada (identidade de workload do AKS, App Service, VM)
- Credencial de identidade federada criada no registro do aplicativo Entra ID
- Acesso de rede ao IMDS (`169.254.169.254:80`) a partir do pod/VM

**Configuração (identidade gerenciada atribuída pelo sistema):**

```json5
{
  channels: {
    msteams: {
      enabled: true,
      appId: "<APP_ID>",
      tenantId: "<TENANT_ID>",
      authType: "federated",
      useManagedIdentity: true,
      webhook: { port: 3978, path: "/api/messages" },
    },
  },
}
```

**Configuração (identidade gerenciada atribuída pelo usuário):**

```json5
{
  channels: {
    msteams: {
      enabled: true,
      appId: "<APP_ID>",
      tenantId: "<TENANT_ID>",
      authType: "federated",
      useManagedIdentity: true,
      managedIdentityClientId: "<MI_CLIENT_ID>",
      webhook: { port: 3978, path: "/api/messages" },
    },
  },
}
```

**Variáveis de ambiente:**

- `MSTEAMS_AUTH_TYPE=federated`
- `MSTEAMS_USE_MANAGED_IDENTITY=true`
- `MSTEAMS_MANAGED_IDENTITY_CLIENT_ID=<client-id>` (somente para atribuição pelo usuário)

### Configuração da identidade de workload do AKS

Para implantações do AKS usando identidade de workload:

1. **Ative a identidade de workload** no cluster do AKS.
2. **Crie uma credencial de identidade federada** no registro do aplicativo Entra ID:

   ```bash
   az ad app federated-credential create --id <APP_OBJECT_ID> --parameters '{
     "name": "my-bot-workload-identity",
     "issuer": "<AKS_OIDC_ISSUER_URL>",
     "subject": "system:serviceaccount:<NAMESPACE>:<SERVICE_ACCOUNT>",
     "audiences": ["api://AzureADTokenExchange"]
   }'
   ```

3. **Anote a conta de serviço do Kubernetes** com o ID do cliente do aplicativo:

   ```yaml
   apiVersion: v1
   kind: ServiceAccount
   metadata:
     name: my-bot-sa
     annotations:
       azure.workload.identity/client-id: "<APP_CLIENT_ID>"
   ```

4. **Rotule o pod** para injeção da identidade de workload:

   ```yaml
   metadata:
     labels:
       azure.workload.identity/use: "true"
   ```

5. **Garanta o acesso de rede** ao IMDS (`169.254.169.254`) — se estiver usando `NetworkPolicy`, adicione uma regra de saída permitindo tráfego para `169.254.169.254/32` na porta 80.

### Comparação dos tipos de autenticação

| Método               | Configuração                                  | Prós                               | Contras                                |
| -------------------- | --------------------------------------------- | ---------------------------------- | -------------------------------------- |
| **Client secret**    | `appPassword`                                 | Configuração simples               | Rotação de segredo necessária, menos seguro |
| **Certificate**      | `authType: "federated"` + `certificatePath`   | Sem segredo compartilhado pela rede | Sobrecarga de gerenciamento de certificado |
| **Managed Identity** | `authType: "federated"` + `useManagedIdentity` | Sem senha, sem segredos para gerenciar | Infraestrutura do Azure obrigatória    |

**Comportamento padrão:** quando `authType` não está definido, o OpenClaw usa autenticação por segredo do cliente por padrão. As configurações existentes continuam funcionando sem alterações.

## Desenvolvimento local (Tunelamento)

O Teams não consegue alcançar `localhost`. Use um túnel para desenvolvimento local:

**Opção A: ngrok**

```bash
ngrok http 3978
# Copie a URL https, por exemplo, https://abc123.ngrok.io
# Defina o endpoint de mensagens como: https://abc123.ngrok.io/api/messages
```

**Opção B: Tailscale Funnel**

```bash
tailscale funnel 3978
# Use sua URL do Tailscale funnel como endpoint de mensagens
```

## Portal do Desenvolvedor do Teams (Alternativa)

Em vez de criar manualmente um ZIP de manifesto, você pode usar o [Portal do Desenvolvedor do Teams](https://dev.teams.microsoft.com/apps):

1. Clique em **+ New app**
2. Preencha as informações básicas (nome, descrição, informações do desenvolvedor)
3. Vá para **App features** → **Bot**
4. Selecione **Enter a bot ID manually** e cole o App ID do seu Azure Bot
5. Marque os escopos: **Personal**, **Team**, **Group Chat**
6. Clique em **Distribute** → **Download app package**
7. No Teams: **Apps** → **Manage your apps** → **Upload a custom app** → selecione o ZIP

Isso costuma ser mais fácil do que editar manifestos JSON manualmente.

## Testando o bot

**Opção A: Azure Web Chat (verifique o webhook primeiro)**

1. No Portal do Azure → seu recurso Azure Bot → **Test in Web Chat**
2. Envie uma mensagem — você deverá ver uma resposta
3. Isso confirma que seu endpoint de webhook funciona antes da configuração do Teams

**Opção B: Teams (após a instalação do aplicativo)**

1. Instale o aplicativo do Teams (sideload ou catálogo da organização)
2. Encontre o bot no Teams e envie uma DM
3. Verifique os logs do gateway para atividade recebida

## Configuração (mínima, somente texto)

1. **Verifique se o plugin do Microsoft Teams está disponível**
   - As versões empacotadas atuais do OpenClaw já o incluem.
   - Instalações antigas/personalizadas podem adicioná-lo manualmente:
     - Do npm: `openclaw plugins install @openclaw/msteams`
     - De um checkout local: `openclaw plugins install ./path/to/local/msteams-plugin`

2. **Registro do bot**
   - Crie um Azure Bot (consulte acima) e anote:
     - App ID
     - Segredo do cliente (senha do aplicativo)
     - ID do locatário (locatário único)

3. **Manifesto do aplicativo Teams**
   - Inclua uma entrada `bot` com `botId = <App ID>`.
   - Escopos: `personal`, `team`, `groupChat`.
   - `supportsFiles: true` (obrigatório para manipulação de arquivos no escopo pessoal).
   - Adicione permissões RSC (abaixo).
   - Crie ícones: `outline.png` (32x32) e `color.png` (192x192).
   - Compacte os três arquivos juntos: `manifest.json`, `outline.png`, `color.png`.

4. **Configure o OpenClaw**

   ```json5
   {
     channels: {
       msteams: {
         enabled: true,
         appId: "<APP_ID>",
         appPassword: "<APP_PASSWORD>",
         tenantId: "<TENANT_ID>",
         webhook: { port: 3978, path: "/api/messages" },
       },
     },
   }
   ```

   Você também pode usar variáveis de ambiente em vez de chaves de configuração:
   - `MSTEAMS_APP_ID`
   - `MSTEAMS_APP_PASSWORD`
   - `MSTEAMS_TENANT_ID`
   - `MSTEAMS_AUTH_TYPE` (opcional: `"secret"` ou `"federated"`)
   - `MSTEAMS_CERTIFICATE_PATH` (federada + certificado)
   - `MSTEAMS_CERTIFICATE_THUMBPRINT` (opcional, não obrigatório para autenticação)
   - `MSTEAMS_USE_MANAGED_IDENTITY` (federada + identidade gerenciada)
   - `MSTEAMS_MANAGED_IDENTITY_CLIENT_ID` (somente MI atribuída pelo usuário)

5. **Endpoint do bot**
   - Defina o endpoint de mensagens do Azure Bot como:
     - `https://<host>:3978/api/messages` (ou o caminho/porta que você escolher).

6. **Execute o gateway**
   - O canal Teams inicia automaticamente quando o plugin incluído ou instalado manualmente está disponível e existe configuração `msteams` com credenciais.

## Ação de informações do membro

O OpenClaw expõe uma ação `member-info` com suporte do Graph para o Microsoft Teams, para que agentes e automações possam resolver detalhes de membros do canal (nome de exibição, email, função) diretamente do Microsoft Graph.

Requisitos:

- Permissão RSC `Member.Read.Group` (já incluída no manifesto recomendado)
- Para consultas entre equipes: permissão de Aplicativo do Graph `User.Read.All` com consentimento de administrador

A ação é controlada por `channels.msteams.actions.memberInfo` (padrão: ativada quando credenciais do Graph estão disponíveis).

## Contexto do histórico

- `channels.msteams.historyLimit` controla quantas mensagens recentes de canal/grupo são incluídas no prompt.
- Usa `messages.groupChat.historyLimit` como fallback. Defina `0` para desativar (padrão: 50).
- O histórico de thread obtido é filtrado pelas listas de permissões de remetentes (`allowFrom` / `groupAllowFrom`), portanto a semeadura de contexto da thread inclui apenas mensagens de remetentes permitidos.
- O contexto de anexo citado (`ReplyTo*` derivado do HTML de resposta do Teams) atualmente é repassado como recebido.
- Em outras palavras, as listas de permissões controlam quem pode acionar o agente; hoje, apenas caminhos específicos de contexto suplementar são filtrados.
- O histórico de DM pode ser limitado com `channels.msteams.dmHistoryLimit` (turnos do usuário). Substituições por usuário: `channels.msteams.dms["<user_id>"].historyLimit`.

## Permissões RSC atuais do Teams (Manifesto)

Estas são as **permissões resourceSpecific existentes** no nosso manifesto do aplicativo Teams. Elas só se aplicam dentro da equipe/chat onde o aplicativo está instalado.

**Para canais (escopo de equipe):**

- `ChannelMessage.Read.Group` (Application) - receber todas as mensagens do canal sem @menção
- `ChannelMessage.Send.Group` (Application)
- `Member.Read.Group` (Application)
- `Owner.Read.Group` (Application)
- `ChannelSettings.Read.Group` (Application)
- `TeamMember.Read.Group` (Application)
- `TeamSettings.Read.Group` (Application)

**Para chats em grupo:**

- `ChatMessage.Read.Chat` (Application) - receber todas as mensagens de chat em grupo sem @menção

## Exemplo de manifesto do Teams (redigido)

Exemplo mínimo e válido com os campos obrigatórios. Substitua IDs e URLs.

```json5
{
  $schema: "https://developer.microsoft.com/en-us/json-schemas/teams/v1.23/MicrosoftTeams.schema.json",
  manifestVersion: "1.23",
  version: "1.0.0",
  id: "00000000-0000-0000-0000-000000000000",
  name: { short: "OpenClaw" },
  developer: {
    name: "Your Org",
    websiteUrl: "https://example.com",
    privacyUrl: "https://example.com/privacy",
    termsOfUseUrl: "https://example.com/terms",
  },
  description: { short: "OpenClaw in Teams", full: "OpenClaw in Teams" },
  icons: { outline: "outline.png", color: "color.png" },
  accentColor: "#5B6DEF",
  bots: [
    {
      botId: "11111111-1111-1111-1111-111111111111",
      scopes: ["personal", "team", "groupChat"],
      isNotificationOnly: false,
      supportsCalling: false,
      supportsVideo: false,
      supportsFiles: true,
    },
  ],
  webApplicationInfo: {
    id: "11111111-1111-1111-1111-111111111111",
  },
  authorization: {
    permissions: {
      resourceSpecific: [
        { name: "ChannelMessage.Read.Group", type: "Application" },
        { name: "ChannelMessage.Send.Group", type: "Application" },
        { name: "Member.Read.Group", type: "Application" },
        { name: "Owner.Read.Group", type: "Application" },
        { name: "ChannelSettings.Read.Group", type: "Application" },
        { name: "TeamMember.Read.Group", type: "Application" },
        { name: "TeamSettings.Read.Group", type: "Application" },
        { name: "ChatMessage.Read.Chat", type: "Application" },
      ],
    },
  },
}
```

### Observações sobre o manifesto (campos obrigatórios)

- `bots[].botId` **deve** corresponder ao App ID do Azure Bot.
- `webApplicationInfo.id` **deve** corresponder ao App ID do Azure Bot.
- `bots[].scopes` deve incluir as superfícies que você pretende usar (`personal`, `team`, `groupChat`).
- `bots[].supportsFiles: true` é obrigatório para manipulação de arquivos no escopo pessoal.
- `authorization.permissions.resourceSpecific` deve incluir leitura/envio de canal se você quiser tráfego de canal.

### Atualizando um aplicativo existente

Para atualizar um aplicativo Teams já instalado (por exemplo, para adicionar permissões RSC):

1. Atualize seu `manifest.json` com as novas configurações
2. **Incremente o campo `version`** (por exemplo, `1.0.0` → `1.1.0`)
3. **Compacte novamente** o manifesto com os ícones (`manifest.json`, `outline.png`, `color.png`)
4. Envie o novo zip:
   - **Opção A (Teams Admin Center):** Teams Admin Center → Teams apps → Manage apps → encontre seu aplicativo → Upload new version
   - **Opção B (Sideload):** No Teams → Apps → Manage your apps → Upload a custom app
5. **Para canais de equipe:** reinstale o aplicativo em cada equipe para que as novas permissões entrem em vigor
6. **Feche completamente e reabra o Teams** (não apenas feche a janela) para limpar os metadados em cache do aplicativo

## Capacidades: somente RSC vs Graph

### Com **somente Teams RSC** (aplicativo instalado, sem permissões da API Graph)

Funciona:

- Ler conteúdo de **texto** de mensagens do canal.
- Enviar conteúdo de **texto** para mensagens do canal.
- Receber anexos de arquivos em **escopo pessoal (DM)**.

NÃO funciona:

- Conteúdo de **imagem ou arquivo** de canal/grupo (a carga inclui apenas um stub HTML).
- Download de anexos armazenados no SharePoint/OneDrive.
- Leitura do histórico de mensagens (além do evento de webhook em tempo real).

### Com **Teams RSC + permissões de Aplicativo do Microsoft Graph**

Adiciona:

- Download de conteúdos hospedados (imagens coladas em mensagens).
- Download de anexos de arquivos armazenados no SharePoint/OneDrive.
- Leitura do histórico de mensagens de canal/chat via Graph.

### RSC vs API Graph

| Capacidade              | Permissões RSC       | API Graph                           |
| ----------------------- | -------------------- | ----------------------------------- |
| **Mensagens em tempo real** | Sim (via webhook) | Não (somente polling)               |
| **Mensagens históricas** | Não                 | Sim (pode consultar o histórico)    |
| **Complexidade de configuração** | Somente manifesto do aplicativo | Requer consentimento de administrador + fluxo de token |
| **Funciona offline**    | Não (deve estar em execução) | Sim (consulta a qualquer momento) |

**Resumo:** RSC é para escuta em tempo real; a API Graph é para acesso histórico. Para recuperar mensagens perdidas enquanto estiver offline, você precisa da API Graph com `ChannelMessage.Read.All` (requer consentimento de administrador).

## Mídia + histórico com Graph ativado (obrigatório para canais)

Se você precisar de imagens/arquivos em **canais** ou quiser obter o **histórico de mensagens**, deve ativar as permissões do Microsoft Graph e conceder consentimento de administrador.

1. No **App Registration** do Entra ID (Azure AD), adicione permissões de **Aplicativo** do Microsoft Graph:
   - `ChannelMessage.Read.All` (anexos de canal + histórico)
   - `Chat.Read.All` ou `ChatMessage.Read.All` (chats em grupo)
2. **Conceda consentimento de administrador** para o locatário.
3. Aumente a **versão do manifesto** do aplicativo Teams, envie novamente e **reinstale o aplicativo no Teams**.
4. **Feche completamente e reabra o Teams** para limpar os metadados em cache do aplicativo.

**Permissão adicional para menções de usuário:** as @menções de usuário funcionam prontamente para usuários na conversa. No entanto, se você quiser pesquisar e mencionar dinamicamente usuários que **não estão na conversa atual**, adicione a permissão `User.Read.All` (Application) e conceda consentimento de administrador.

## Limitações conhecidas

### Timeouts de webhook

O Teams entrega mensagens por webhook HTTP. Se o processamento levar muito tempo (por exemplo, respostas lentas do LLM), você poderá ver:

- Timeouts do gateway
- O Teams tentando reenviar a mensagem (causando duplicatas)
- Respostas descartadas

O OpenClaw lida com isso respondendo rapidamente e enviando respostas de forma proativa, mas respostas muito lentas ainda podem causar problemas.

### Formatação

O markdown do Teams é mais limitado que o do Slack ou Discord:

- A formatação básica funciona: **negrito**, _itálico_, `code`, links
- Markdown complexo (tabelas, listas aninhadas) pode não ser renderizado corretamente
- Adaptive Cards são compatíveis para enquetes e envios arbitrários de cartões (consulte abaixo)

## Configuração

Principais configurações (consulte `/gateway/configuration` para padrões compartilhados de canal):

- `channels.msteams.enabled`: ativa/desativa o canal.
- `channels.msteams.appId`, `channels.msteams.appPassword`, `channels.msteams.tenantId`: credenciais do bot.
- `channels.msteams.webhook.port` (padrão `3978`)
- `channels.msteams.webhook.path` (padrão `/api/messages`)
- `channels.msteams.dmPolicy`: `pairing | allowlist | open | disabled` (padrão: pairing)
- `channels.msteams.allowFrom`: lista de permissões de DM (recomendam-se IDs de objeto AAD). O assistente resolve nomes para IDs durante a configuração quando o acesso ao Graph está disponível.
- `channels.msteams.dangerouslyAllowNameMatching`: opção de emergência para reativar a correspondência por UPN/nome de exibição mutáveis e o roteamento direto por nome de equipe/canal.
- `channels.msteams.textChunkLimit`: tamanho do bloco de texto de saída.
- `channels.msteams.chunkMode`: `length` (padrão) ou `newline` para dividir em linhas em branco (limites de parágrafo) antes da divisão por comprimento.
- `channels.msteams.mediaAllowHosts`: lista de permissões para hosts de anexos de entrada (por padrão, domínios da Microsoft/Teams).
- `channels.msteams.mediaAuthAllowHosts`: lista de permissões para anexar cabeçalhos `Authorization` em novas tentativas de mídia (por padrão, hosts do Graph + Bot Framework).
- `channels.msteams.requireMention`: exige @menção em canais/grupos (padrão: true).
- `channels.msteams.replyStyle`: `thread | top-level` (consulte [Estilo de resposta](#reply-style-threads-vs-posts)).
- `channels.msteams.teams.<teamId>.replyStyle`: substituição por equipe.
- `channels.msteams.teams.<teamId>.requireMention`: substituição por equipe.
- `channels.msteams.teams.<teamId>.tools`: substituições padrão de política de ferramentas por equipe (`allow`/`deny`/`alsoAllow`) usadas quando não há uma substituição de canal.
- `channels.msteams.teams.<teamId>.toolsBySender`: substituições padrão de política de ferramentas por equipe e por remetente (compatível com curinga `"*"`).
- `channels.msteams.teams.<teamId>.channels.<conversationId>.replyStyle`: substituição por canal.
- `channels.msteams.teams.<teamId>.channels.<conversationId>.requireMention`: substituição por canal.
- `channels.msteams.teams.<teamId>.channels.<conversationId>.tools`: substituições de política de ferramentas por canal (`allow`/`deny`/`alsoAllow`).
- `channels.msteams.teams.<teamId>.channels.<conversationId>.toolsBySender`: substituições de política de ferramentas por canal e por remetente (compatível com curinga `"*"`).
- As chaves de `toolsBySender` devem usar prefixos explícitos:
  `id:`, `e164:`, `username:`, `name:` (chaves legadas sem prefixo ainda são mapeadas apenas para `id:`).
- `channels.msteams.actions.memberInfo`: ativa ou desativa a ação de informações de membro com suporte do Graph (padrão: ativada quando credenciais do Graph estão disponíveis).
- `channels.msteams.authType`: tipo de autenticação — `"secret"` (padrão) ou `"federated"`.
- `channels.msteams.certificatePath`: caminho para o arquivo de certificado PEM (federada + autenticação por certificado).
- `channels.msteams.certificateThumbprint`: impressão digital do certificado (opcional, não obrigatória para autenticação).
- `channels.msteams.useManagedIdentity`: ativa autenticação por identidade gerenciada (modo federado).
- `channels.msteams.managedIdentityClientId`: ID do cliente para identidade gerenciada atribuída pelo usuário.
- `channels.msteams.sharePointSiteId`: ID do site do SharePoint para uploads de arquivos em chats/canais de grupo (consulte [Envio de arquivos em chats de grupo](#sending-files-in-group-chats)).

## Roteamento e sessões

- As chaves de sessão seguem o formato padrão de agente (consulte [/concepts/session](/pt-BR/concepts/session)):
  - Mensagens diretas compartilham a sessão principal (`agent:<agentId>:<mainKey>`).
  - Mensagens de canal/grupo usam o ID da conversa:
    - `agent:<agentId>:msteams:channel:<conversationId>`
    - `agent:<agentId>:msteams:group:<conversationId>`

## Estilo de resposta: threads vs publicações

O Teams introduziu recentemente dois estilos de interface de canal sobre o mesmo modelo de dados subjacente:

| Estilo                  | Descrição                                                | `replyStyle` recomendado |
| ----------------------- | -------------------------------------------------------- | ------------------------ |
| **Posts** (clássico)    | As mensagens aparecem como cartões com respostas em thread abaixo | `thread` (padrão)        |
| **Threads** (semelhante ao Slack) | As mensagens fluem linearmente, mais parecido com o Slack | `top-level`              |

**O problema:** a API do Teams não informa qual estilo de interface um canal usa. Se você usar o `replyStyle` errado:

- `thread` em um canal no estilo Threads → as respostas aparecem aninhadas de forma estranha
- `top-level` em um canal no estilo Posts → as respostas aparecem como publicações separadas de nível superior em vez de na thread

**Solução:** configure `replyStyle` por canal com base em como o canal está configurado:

```json5
{
  channels: {
    msteams: {
      replyStyle: "thread",
      teams: {
        "19:abc...@thread.tacv2": {
          channels: {
            "19:xyz...@thread.tacv2": {
              replyStyle: "top-level",
            },
          },
        },
      },
    },
  },
}
```

## Anexos e imagens

**Limitações atuais:**

- **DMs:** imagens e anexos de arquivo funcionam por meio das APIs de arquivo do bot do Teams.
- **Canais/grupos:** anexos ficam armazenados no M365 (SharePoint/OneDrive). A carga útil do webhook inclui apenas um stub HTML, não os bytes reais do arquivo. **Permissões da API Graph são obrigatórias** para baixar anexos de canal.
- Para envios explícitos com arquivo primeiro, use `action=upload-file` com `media` / `filePath` / `path`; `message` opcional torna-se o texto/comentário que acompanha, e `filename` substitui o nome enviado.

Sem permissões do Graph, mensagens de canal com imagens serão recebidas apenas como texto (o conteúdo da imagem não fica acessível ao bot).
Por padrão, o OpenClaw baixa mídia apenas de nomes de host da Microsoft/Teams. Substitua com `channels.msteams.mediaAllowHosts` (use `["*"]` para permitir qualquer host).
Cabeçalhos de autorização são anexados apenas para hosts em `channels.msteams.mediaAuthAllowHosts` (por padrão, hosts do Graph + Bot Framework). Mantenha essa lista restrita (evite sufixos multilocatário).

## Envio de arquivos em chats de grupo

Bots podem enviar arquivos em DMs usando o fluxo FileConsentCard (integrado). No entanto, **enviar arquivos em chats/canais de grupo** exige configuração adicional:

| Contexto                 | Como os arquivos são enviados              | Configuração necessária                         |
| ------------------------ | ------------------------------------------ | ----------------------------------------------- |
| **DMs**                  | FileConsentCard → usuário aceita → bot envia | Funciona imediatamente                          |
| **Chats/canais de grupo** | Upload para o SharePoint → compartilhar link | Requer `sharePointSiteId` + permissões do Graph |
| **Imagens (qualquer contexto)** | Inline codificado em Base64          | Funciona imediatamente                          |

### Por que chats de grupo exigem SharePoint

Bots não têm um drive pessoal do OneDrive (o endpoint `/me/drive` da API Graph não funciona para identidades de aplicativo). Para enviar arquivos em chats/canais de grupo, o bot faz upload para um **site do SharePoint** e cria um link de compartilhamento.

### Configuração

1. **Adicione permissões da API Graph** em Entra ID (Azure AD) → App Registration:
   - `Sites.ReadWrite.All` (Application) - enviar arquivos para o SharePoint
   - `Chat.Read.All` (Application) - opcional, ativa links de compartilhamento por usuário

2. **Conceda consentimento de administrador** para o locatário.

3. **Obtenha o ID do seu site do SharePoint:**

   ```bash
   # Via Graph Explorer ou curl com um token válido:
   curl -H "Authorization: Bearer $TOKEN" \
     "https://graph.microsoft.com/v1.0/sites/{hostname}:/{site-path}"

   # Exemplo: para um site em "contoso.sharepoint.com/sites/BotFiles"
   curl -H "Authorization: Bearer $TOKEN" \
     "https://graph.microsoft.com/v1.0/sites/contoso.sharepoint.com:/sites/BotFiles"

   # A resposta inclui: "id": "contoso.sharepoint.com,guid1,guid2"
   ```

4. **Configure o OpenClaw:**

   ```json5
   {
     channels: {
       msteams: {
         // ... other config ...
         sharePointSiteId: "contoso.sharepoint.com,guid1,guid2",
       },
     },
   }
   ```

### Comportamento de compartilhamento

| Permissão                              | Comportamento de compartilhamento                         |
| -------------------------------------- | --------------------------------------------------------- |
| `Sites.ReadWrite.All` apenas           | Link de compartilhamento para toda a organização (qualquer pessoa na organização pode acessar) |
| `Sites.ReadWrite.All` + `Chat.Read.All` | Link de compartilhamento por usuário (somente membros do chat podem acessar) |

O compartilhamento por usuário é mais seguro, pois apenas os participantes do chat podem acessar o arquivo. Se a permissão `Chat.Read.All` estiver ausente, o bot usa como fallback o compartilhamento para toda a organização.

### Comportamento de fallback

| Cenário                                           | Resultado                                          |
| ------------------------------------------------- | -------------------------------------------------- |
| Chat em grupo + arquivo + `sharePointSiteId` configurado | Upload para o SharePoint, envio de link de compartilhamento |
| Chat em grupo + arquivo + sem `sharePointSiteId`  | Tenta upload no OneDrive (pode falhar), envia apenas texto |
| Chat pessoal + arquivo                            | Fluxo FileConsentCard (funciona sem SharePoint)    |
| Qualquer contexto + imagem                        | Inline codificado em Base64 (funciona sem SharePoint) |

### Local onde os arquivos são armazenados

Os arquivos enviados são armazenados em uma pasta `/OpenClawShared/` na biblioteca de documentos padrão do site do SharePoint configurado.

## Enquetes (Adaptive Cards)

O OpenClaw envia enquetes do Teams como Adaptive Cards (não há API nativa de enquetes do Teams).

- CLI: `openclaw message poll --channel msteams --target conversation:<id> ...`
- Os votos são registrados pelo gateway em `~/.openclaw/msteams-polls.json`.
- O gateway deve permanecer online para registrar votos.
- As enquetes ainda não publicam automaticamente resumos de resultados (inspecione o arquivo de armazenamento, se necessário).

## Adaptive Cards (arbitrários)

Envie qualquer JSON de Adaptive Card para usuários ou conversas do Teams usando a ferramenta `message` ou a CLI.

O parâmetro `card` aceita um objeto JSON de Adaptive Card. Quando `card` é fornecido, o texto da mensagem é opcional.

**Ferramenta do agente:**

```json5
{
  action: "send",
  channel: "msteams",
  target: "user:<id>",
  card: {
    type: "AdaptiveCard",
    version: "1.5",
    body: [{ type: "TextBlock", text: "Hello!" }],
  },
}
```

**CLI:**

```bash
openclaw message send --channel msteams \
  --target "conversation:19:abc...@thread.tacv2" \
  --card '{"type":"AdaptiveCard","version":"1.5","body":[{"type":"TextBlock","text":"Hello!"}]}'
```

Consulte a [documentação do Adaptive Cards](https://adaptivecards.io/) para o esquema do cartão e exemplos. Para detalhes sobre o formato do destino, consulte [Formatos de destino](#target-formats) abaixo.

## Formatos de destino

Os destinos do MSTeams usam prefixos para distinguir entre usuários e conversas:

| Tipo de destino         | Formato                         | Exemplo                                             |
| ----------------------- | ------------------------------- | --------------------------------------------------- |
| Usuário (por ID)        | `user:<aad-object-id>`          | `user:40a1a0ed-4ff2-4164-a219-55518990c197`         |
| Usuário (por nome)      | `user:<display-name>`           | `user:John Smith` (requer API Graph)               |
| Grupo/canal             | `conversation:<conversation-id>` | `conversation:19:abc123...@thread.tacv2`           |
| Grupo/canal (bruto)     | `<conversation-id>`             | `19:abc123...@thread.tacv2` (se contiver `@thread`) |

**Exemplos de CLI:**

```bash
# Enviar para um usuário por ID
openclaw message send --channel msteams --target "user:40a1a0ed-..." --message "Hello"

# Enviar para um usuário por nome de exibição (dispara consulta na API Graph)
openclaw message send --channel msteams --target "user:John Smith" --message "Hello"

# Enviar para um chat em grupo ou canal
openclaw message send --channel msteams --target "conversation:19:abc...@thread.tacv2" --message "Hello"

# Enviar um Adaptive Card para uma conversa
openclaw message send --channel msteams --target "conversation:19:abc...@thread.tacv2" \
  --card '{"type":"AdaptiveCard","version":"1.5","body":[{"type":"TextBlock","text":"Hello"}]}'
```

**Exemplos de ferramenta do agente:**

```json5
{
  action: "send",
  channel: "msteams",
  target: "user:John Smith",
  message: "Hello!",
}
```

```json5
{
  action: "send",
  channel: "msteams",
  target: "conversation:19:abc...@thread.tacv2",
  card: {
    type: "AdaptiveCard",
    version: "1.5",
    body: [{ type: "TextBlock", text: "Hello" }],
  },
}
```

Observação: sem o prefixo `user:`, os nomes usam por padrão a resolução de grupo/equipe. Sempre use `user:` ao direcionar pessoas por nome de exibição.

## Mensagens proativas

- Mensagens proativas só são possíveis **depois** que um usuário interagiu, porque armazenamos referências de conversa nesse momento.
- Consulte `/gateway/configuration` para `dmPolicy` e controle por lista de permissões.

## IDs de equipe e canal (pegadinha comum)

O parâmetro de consulta `groupId` nas URLs do Teams **NÃO** é o ID de equipe usado para configuração. Extraia os IDs do caminho da URL:

**URL da equipe:**

```
https://teams.microsoft.com/l/team/19%3ABk4j...%40thread.tacv2/conversations?groupId=...
                                    └────────────────────────────┘
                                    ID da equipe (faça URL decode disso)
```

**URL do canal:**

```
https://teams.microsoft.com/l/channel/19%3A15bc...%40thread.tacv2/ChannelName?groupId=...
                                      └─────────────────────────┘
                                      ID do canal (faça URL decode disso)
```

**Para configuração:**

- ID da equipe = segmento do caminho após `/team/` (decodificado da URL, por exemplo, `19:Bk4j...@thread.tacv2`)
- ID do canal = segmento do caminho após `/channel/` (decodificado da URL)
- **Ignore** o parâmetro de consulta `groupId`

## Canais privados

Bots têm suporte limitado em canais privados:

| Recurso                      | Canais padrão     | Canais privados       |
| ---------------------------- | ----------------- | --------------------- |
| Instalação do bot            | Sim               | Limitado              |
| Mensagens em tempo real (webhook) | Sim         | Pode não funcionar    |
| Permissões RSC               | Sim               | Podem se comportar de forma diferente |
| @menções                     | Sim               | Se o bot estiver acessível |
| Histórico via API Graph      | Sim               | Sim (com permissões)  |

**Alternativas se canais privados não funcionarem:**

1. Use canais padrão para interações com o bot
2. Use DMs - os usuários sempre podem enviar mensagens diretamente ao bot
3. Use a API Graph para acesso histórico (requer `ChannelMessage.Read.All`)

## Solução de problemas

### Problemas comuns

- **Imagens não aparecem em canais:** faltam permissões do Graph ou consentimento de administrador. Reinstale o aplicativo Teams e feche/reabra completamente o Teams.
- **Sem respostas no canal:** menções são obrigatórias por padrão; defina `channels.msteams.requireMention=false` ou configure por equipe/canal.
- **Incompatibilidade de versão (o Teams ainda mostra o manifesto antigo):** remova e adicione o aplicativo novamente e feche completamente o Teams para atualizar.
- **401 Unauthorized do webhook:** esperado ao testar manualmente sem JWT do Azure - significa que o endpoint está acessível, mas a autenticação falhou. Use o Azure Web Chat para testar corretamente.

### Erros no envio do manifesto

- **"Icon file cannot be empty":** o manifesto faz referência a arquivos de ícone com 0 bytes. Crie ícones PNG válidos (32x32 para `outline.png`, 192x192 para `color.png`).
- **"webApplicationInfo.Id already in use":** o aplicativo ainda está instalado em outra equipe/chat. Localize e desinstale-o primeiro ou aguarde de 5 a 10 minutos pela propagação.
- **"Something went wrong" ao enviar:** faça o envio por [https://admin.teams.microsoft.com](https://admin.teams.microsoft.com), abra as DevTools do navegador (F12) → aba Network e verifique o corpo da resposta para ver o erro real.
- **Falha no sideload:** tente "Upload an app to your org's app catalog" em vez de "Upload a custom app" - isso geralmente contorna restrições de sideload.

### Permissões RSC não funcionam

1. Verifique se `webApplicationInfo.id` corresponde exatamente ao App ID do seu bot
2. Envie novamente o aplicativo e reinstale-o na equipe/chat
3. Verifique se o administrador da sua organização bloqueou permissões RSC
4. Confirme se você está usando o escopo correto: `ChannelMessage.Read.Group` para equipes, `ChatMessage.Read.Chat` para chats em grupo

## Referências

- [Create Azure Bot](https://learn.microsoft.com/en-us/azure/bot-service/bot-service-quickstart-registration) - guia de configuração do Azure Bot
- [Teams Developer Portal](https://dev.teams.microsoft.com/apps) - criar/gerenciar aplicativos do Teams
- [Teams app manifest schema](https://learn.microsoft.com/en-us/microsoftteams/platform/resources/schema/manifest-schema)
- [Receive channel messages with RSC](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/conversations/channel-messages-with-rsc)
- [RSC permissions reference](https://learn.microsoft.com/en-us/microsoftteams/platform/graph-api/rsc/resource-specific-consent)
- [Teams bot file handling](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/bots-filesv4) (canal/grupo requer Graph)
- [Proactive messaging](https://learn.microsoft.com/en-us/microsoftteams/platform/bots/how-to/conversations/send-proactive-messages)

## Relacionado

- [Visão geral dos canais](/pt-BR/channels) — todos os canais compatíveis
- [Pareamento](/pt-BR/channels/pairing) — autenticação por DM e fluxo de pareamento
- [Grupos](/pt-BR/channels/groups) — comportamento de chat em grupo e exigência de menção
- [Roteamento de canal](/pt-BR/channels/channel-routing) — roteamento de sessão para mensagens
- [Segurança](/pt-BR/gateway/security) — modelo de acesso e proteção 강화
