---
read_when:
    - Ativando texto para fala para respostas
    - Configurando provedores ou limites de TTS
    - Usando comandos `/tts`
summary: Texto para fala (TTS) para respostas enviadas
title: Texto para fala
x-i18n:
    generated_at: "2026-04-16T19:31:05Z"
    model: gpt-5.4
    provider: openai
    source_hash: de7c1dc8831c1ba307596afd48cb4d36f844724887a13b17e35f41ef5174a86f
    source_path: tools/tts.md
    workflow: 15
---

# Texto para fala (TTS)

O OpenClaw pode converter respostas enviadas em áudio usando ElevenLabs, Google Gemini, Microsoft, MiniMax ou OpenAI.
Funciona em qualquer lugar onde o OpenClaw puder enviar áudio.

## Serviços compatíveis

- **ElevenLabs** (provedor principal ou de fallback)
- **Google Gemini** (provedor principal ou de fallback; usa TTS da API Gemini)
- **Microsoft** (provedor principal ou de fallback; a implementação empacotada atual usa `node-edge-tts`)
- **MiniMax** (provedor principal ou de fallback; usa a API T2A v2)
- **OpenAI** (provedor principal ou de fallback; também usado para resumos)

### Observações sobre fala da Microsoft

Atualmente, o provedor de fala da Microsoft empacotado usa o serviço de TTS neural
online do Microsoft Edge por meio da biblioteca `node-edge-tts`. É um serviço hospedado (não
local), usa endpoints da Microsoft e não exige uma chave de API.
`node-edge-tts` expõe opções de configuração de fala e formatos de saída, mas
nem todas as opções são compatíveis com o serviço. Configuração legada e entrada de diretiva
usando `edge` ainda funcionam e são normalizadas para `microsoft`.

Como esse caminho usa um serviço web público sem SLA ou cota publicados,
trate-o como melhor esforço. Se você precisar de limites garantidos e suporte, use OpenAI
ou ElevenLabs.

## Chaves opcionais

Se você quiser OpenAI, ElevenLabs, Google Gemini ou MiniMax:

- `ELEVENLABS_API_KEY` (ou `XI_API_KEY`)
- `GEMINI_API_KEY` (ou `GOOGLE_API_KEY`)
- `MINIMAX_API_KEY`
- `OPENAI_API_KEY`

A fala da Microsoft **não** exige uma chave de API.

Se vários provedores estiverem configurados, o provedor selecionado será usado primeiro, e os demais serão opções de fallback.
O resumo automático usa o `summaryModel` configurado (ou `agents.defaults.model.primary`),
então esse provedor também deve estar autenticado se você ativar resumos.

## Links dos serviços

- [Guia de Text-to-Speech da OpenAI](https://platform.openai.com/docs/guides/text-to-speech)
- [Referência da API de áudio da OpenAI](https://platform.openai.com/docs/api-reference/audio)
- [Text to Speech da ElevenLabs](https://elevenlabs.io/docs/api-reference/text-to-speech)
- [Autenticação da ElevenLabs](https://elevenlabs.io/docs/api-reference/authentication)
- [API MiniMax T2A v2](https://platform.minimaxi.com/document/T2A%20V2)
- [node-edge-tts](https://github.com/SchneeHertz/node-edge-tts)
- [Formatos de saída de fala da Microsoft](https://learn.microsoft.com/azure/ai-services/speech-service/rest-text-to-speech#audio-outputs)

## Isso vem ativado por padrão?

Não. O TTS automático vem **desativado** por padrão. Ative-o na configuração com
`messages.tts.auto` ou localmente com `/tts on`.

Quando `messages.tts.provider` não está definido, o OpenClaw escolhe o primeiro
provedor de fala configurado na ordem de seleção automática do registro.

## Configuração

A configuração de TTS fica em `messages.tts` no `openclaw.json`.
O schema completo está em [Configuração do Gateway](/pt-BR/gateway/configuration).

### Configuração mínima (ativar + provedor)

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "elevenlabs",
    },
  },
}
```

### OpenAI como principal com fallback para ElevenLabs

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "openai",
      summaryModel: "openai/gpt-4.1-mini",
      modelOverrides: {
        enabled: true,
      },
      providers: {
        openai: {
          apiKey: "openai_api_key",
          baseUrl: "https://api.openai.com/v1",
          model: "gpt-4o-mini-tts",
          voice: "alloy",
        },
        elevenlabs: {
          apiKey: "elevenlabs_api_key",
          baseUrl: "https://api.elevenlabs.io",
          voiceId: "voice_id",
          modelId: "eleven_multilingual_v2",
          seed: 42,
          applyTextNormalization: "auto",
          languageCode: "en",
          voiceSettings: {
            stability: 0.5,
            similarityBoost: 0.75,
            style: 0.0,
            useSpeakerBoost: true,
            speed: 1.0,
          },
        },
      },
    },
  },
}
```

### Microsoft como principal (sem chave de API)

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "microsoft",
      providers: {
        microsoft: {
          enabled: true,
          voice: "en-US-MichelleNeural",
          lang: "en-US",
          outputFormat: "audio-24khz-48kbitrate-mono-mp3",
          rate: "+10%",
          pitch: "-5%",
        },
      },
    },
  },
}
```

### MiniMax como principal

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "minimax",
      providers: {
        minimax: {
          apiKey: "minimax_api_key",
          baseUrl: "https://api.minimax.io",
          model: "speech-2.8-hd",
          voiceId: "English_expressive_narrator",
          speed: 1.0,
          vol: 1.0,
          pitch: 0,
        },
      },
    },
  },
}
```

### Google Gemini como principal

```json5
{
  messages: {
    tts: {
      auto: "always",
      provider: "google",
      providers: {
        google: {
          apiKey: "gemini_api_key",
          model: "gemini-3.1-flash-tts-preview",
          voiceName: "Kore",
        },
      },
    },
  },
}
```

O TTS do Google Gemini usa o caminho de chave de API do Gemini. Uma chave de API do Google Cloud Console
restrita à API Gemini é válida aqui, e é o mesmo tipo de chave usado
pelo provedor empacotado de geração de imagens do Google. A ordem de resolução é
`messages.tts.providers.google.apiKey` -> `models.providers.google.apiKey` ->
`GEMINI_API_KEY` -> `GOOGLE_API_KEY`.

### Desativar fala da Microsoft

```json5
{
  messages: {
    tts: {
      providers: {
        microsoft: {
          enabled: false,
        },
      },
    },
  },
}
```

### Limites personalizados + caminho de preferências

```json5
{
  messages: {
    tts: {
      auto: "always",
      maxTextLength: 4000,
      timeoutMs: 30000,
      prefsPath: "~/.openclaw/settings/tts.json",
    },
  },
}
```

### Responder com áudio apenas após uma mensagem de voz recebida

```json5
{
  messages: {
    tts: {
      auto: "inbound",
    },
  },
}
```

### Desativar o resumo automático para respostas longas

```json5
{
  messages: {
    tts: {
      auto: "always",
    },
  },
}
```

Depois execute:

```
/tts summary off
```

### Observações sobre os campos

- `auto`: modo de TTS automático (`off`, `always`, `inbound`, `tagged`).
  - `inbound` só envia áudio após uma mensagem de voz recebida.
  - `tagged` só envia áudio quando a resposta inclui diretivas `[[tts:key=value]]` ou um bloco `[[tts:text]]...[[/tts:text]]`.
- `enabled`: alternância legada (o doctor migra isso para `auto`).
- `mode`: `"final"` (padrão) ou `"all"` (inclui respostas de ferramentas/blocos).
- `provider`: id do provedor de fala, como `"elevenlabs"`, `"google"`, `"microsoft"`, `"minimax"` ou `"openai"` (o fallback é automático).
- Se `provider` **não estiver definido**, o OpenClaw usa o primeiro provedor de fala configurado na ordem de seleção automática do registro.
- O legado `provider: "edge"` ainda funciona e é normalizado para `microsoft`.
- `summaryModel`: modelo barato opcional para resumo automático; por padrão usa `agents.defaults.model.primary`.
  - Aceita `provider/model` ou um alias de modelo configurado.
- `modelOverrides`: permite que o modelo emita diretivas de TTS (ativado por padrão).
  - `allowProvider` é `false` por padrão (a troca de provedor é opt-in).
- `providers.<id>`: configurações do provedor, indexadas pelo id do provedor de fala.
- Blocos diretos de provedor legados (`messages.tts.openai`, `messages.tts.elevenlabs`, `messages.tts.microsoft`, `messages.tts.edge`) são migrados automaticamente para `messages.tts.providers.<id>` no carregamento.
- `maxTextLength`: limite rígido para entrada de TTS (caracteres). `/tts audio` falha se for excedido.
- `timeoutMs`: tempo limite da solicitação (ms).
- `prefsPath`: substitui o caminho local do JSON de preferências (provedor/limite/resumo).
- Os valores de `apiKey` usam fallback para variáveis de ambiente (`ELEVENLABS_API_KEY`/`XI_API_KEY`, `GEMINI_API_KEY`/`GOOGLE_API_KEY`, `MINIMAX_API_KEY`, `OPENAI_API_KEY`).
- `providers.elevenlabs.baseUrl`: substitui a URL base da API da ElevenLabs.
- `providers.openai.baseUrl`: substitui o endpoint de TTS da OpenAI.
  - Ordem de resolução: `messages.tts.providers.openai.baseUrl` -> `OPENAI_TTS_BASE_URL` -> `https://api.openai.com/v1`
  - Valores diferentes do padrão são tratados como endpoints de TTS compatíveis com OpenAI, então nomes personalizados de modelo e voz são aceitos.
- `providers.elevenlabs.voiceSettings`:
  - `stability`, `similarityBoost`, `style`: `0..1`
  - `useSpeakerBoost`: `true|false`
  - `speed`: `0.5..2.0` (1.0 = normal)
- `providers.elevenlabs.applyTextNormalization`: `auto|on|off`
- `providers.elevenlabs.languageCode`: ISO 639-1 de 2 letras (por exemplo, `en`, `de`)
- `providers.elevenlabs.seed`: inteiro `0..4294967295` (determinismo de melhor esforço)
- `providers.minimax.baseUrl`: substitui a URL base da API MiniMax (padrão `https://api.minimax.io`, env: `MINIMAX_API_HOST`).
- `providers.minimax.model`: modelo de TTS (padrão `speech-2.8-hd`, env: `MINIMAX_TTS_MODEL`).
- `providers.minimax.voiceId`: identificador de voz (padrão `English_expressive_narrator`, env: `MINIMAX_TTS_VOICE_ID`).
- `providers.minimax.speed`: velocidade de reprodução `0.5..2.0` (padrão 1.0).
- `providers.minimax.vol`: volume `(0, 10]` (padrão 1.0; deve ser maior que 0).
- `providers.minimax.pitch`: deslocamento de tom `-12..12` (padrão 0).
- `providers.google.model`: modelo de TTS do Gemini (padrão `gemini-3.1-flash-tts-preview`).
- `providers.google.voiceName`: nome de voz predefinida do Gemini (padrão `Kore`; `voice` também é aceito).
- `providers.google.baseUrl`: substitui a URL base da API Gemini. Somente `https://generativelanguage.googleapis.com` é aceito.
  - Se `messages.tts.providers.google.apiKey` for omitido, o TTS pode reutilizar `models.providers.google.apiKey` antes do fallback para env.
- `providers.microsoft.enabled`: permite o uso da fala da Microsoft (padrão `true`; sem chave de API).
- `providers.microsoft.voice`: nome da voz neural da Microsoft (por exemplo, `en-US-MichelleNeural`).
- `providers.microsoft.lang`: código do idioma (por exemplo, `en-US`).
- `providers.microsoft.outputFormat`: formato de saída da Microsoft (por exemplo, `audio-24khz-48kbitrate-mono-mp3`).
  - Consulte os formatos de saída de fala da Microsoft para valores válidos; nem todos os formatos são compatíveis com o transporte empacotado baseado em Edge.
- `providers.microsoft.rate` / `providers.microsoft.pitch` / `providers.microsoft.volume`: strings de porcentagem (por exemplo, `+10%`, `-5%`).
- `providers.microsoft.saveSubtitles`: grava legendas em JSON ao lado do arquivo de áudio.
- `providers.microsoft.proxy`: URL de proxy para solicitações de fala da Microsoft.
- `providers.microsoft.timeoutMs`: substituição do tempo limite da solicitação (ms).
- `edge.*`: alias legado para as mesmas configurações da Microsoft.

## Substituições controladas pelo modelo (ativadas por padrão)

Por padrão, o modelo **pode** emitir diretivas de TTS para uma única resposta.
Quando `messages.tts.auto` é `tagged`, essas diretivas são obrigatórias para acionar o áudio.

Quando ativado, o modelo pode emitir diretivas `[[tts:...]]` para substituir a voz
em uma única resposta, além de um bloco opcional `[[tts:text]]...[[/tts:text]]` para
fornecer tags expressivas (risadas, indicações de canto etc.) que devem aparecer apenas
no áudio.

Diretivas `provider=...` são ignoradas, a menos que `modelOverrides.allowProvider: true`.

Exemplo de payload de resposta:

```
Aqui está.

[[tts:voiceId=pMsXgVXv3BLzUgSXRplE model=eleven_v3 speed=1.1]]
[[tts:text]](ri) Leia a música mais uma vez.[[/tts:text]]
```

Chaves de diretiva disponíveis (quando ativadas):

- `provider` (id de provedor de fala registrado, por exemplo `openai`, `elevenlabs`, `google`, `minimax` ou `microsoft`; exige `allowProvider: true`)
- `voice` (voz da OpenAI), `voiceName` / `voice_name` / `google_voice` (voz do Google) ou `voiceId` (ElevenLabs / MiniMax)
- `model` (modelo de TTS da OpenAI, id de modelo da ElevenLabs ou modelo da MiniMax) ou `google_model` (modelo de TTS do Google)
- `stability`, `similarityBoost`, `style`, `speed`, `useSpeakerBoost`
- `vol` / `volume` (volume da MiniMax, 0-10)
- `pitch` (tom da MiniMax, -12 a 12)
- `applyTextNormalization` (`auto|on|off`)
- `languageCode` (ISO 639-1)
- `seed`

Desative todas as substituições do modelo:

```json5
{
  messages: {
    tts: {
      modelOverrides: {
        enabled: false,
      },
    },
  },
}
```

Allowlist opcional (ativa a troca de provedor enquanto mantém outros controles configuráveis):

```json5
{
  messages: {
    tts: {
      modelOverrides: {
        enabled: true,
        allowProvider: true,
        allowSeed: false,
      },
    },
  },
}
```

## Preferências por usuário

Comandos slash gravam substituições locais em `prefsPath` (padrão:
`~/.openclaw/settings/tts.json`, substitua com `OPENCLAW_TTS_PREFS` ou
`messages.tts.prefsPath`).

Campos armazenados:

- `enabled`
- `provider`
- `maxLength` (limite para resumo; padrão de 1500 caracteres)
- `summarize` (padrão `true`)

Eles substituem `messages.tts.*` nesse host.

## Formatos de saída (fixos)

- **Feishu / Matrix / Telegram / WhatsApp**: mensagem de voz Opus (`opus_48000_64` da ElevenLabs, `opus` da OpenAI).
  - 48kHz / 64kbps é um bom equilíbrio para mensagens de voz.
- **Outros canais**: MP3 (`mp3_44100_128` da ElevenLabs, `mp3` da OpenAI).
  - 44,1kHz / 128kbps é o equilíbrio padrão para clareza da fala.
- **MiniMax**: MP3 (modelo `speech-2.8-hd`, taxa de amostragem de 32kHz). O formato de nota de voz não é compatível nativamente; use OpenAI ou ElevenLabs para mensagens de voz Opus garantidas.
- **Google Gemini**: o TTS da API Gemini retorna PCM bruto em 24kHz. O OpenClaw o empacota como WAV para anexos de áudio e retorna PCM diretamente para Talk/telefonia. O formato nativo de nota de voz Opus não é compatível com esse caminho.
- **Microsoft**: usa `microsoft.outputFormat` (padrão `audio-24khz-48kbitrate-mono-mp3`).
  - O transporte empacotado aceita um `outputFormat`, mas nem todos os formatos estão disponíveis no serviço.
  - Os valores de formato de saída seguem os formatos de saída do Microsoft Speech (incluindo Ogg/WebM Opus).
  - O `sendVoice` do Telegram aceita OGG/MP3/M4A; use OpenAI/ElevenLabs se você precisar de
    mensagens de voz Opus garantidas.
  - Se o formato de saída configurado da Microsoft falhar, o OpenClaw tenta novamente com MP3.

Os formatos de saída de OpenAI/ElevenLabs são fixos por canal (veja acima).

## Comportamento do TTS automático

Quando ativado, o OpenClaw:

- ignora o TTS se a resposta já contiver mídia ou uma diretiva `MEDIA:`.
- ignora respostas muito curtas (< 10 caracteres).
- resume respostas longas quando ativado usando `agents.defaults.model.primary` (ou `summaryModel`).
- anexa o áudio gerado à resposta.

Se a resposta exceder `maxLength` e o resumo estiver desativado (ou não houver chave de API para o
modelo de resumo), o áudio
será ignorado e a resposta de texto normal será enviada.

## Diagrama de fluxo

```
Resposta -> TTS ativado?
  não -> enviar texto
  sim -> tem mídia / MEDIA: / curta?
          sim -> enviar texto
          não -> tamanho > limite?
                   não -> TTS -> anexar áudio
                   sim -> resumo ativado?
                            não -> enviar texto
                            sim -> resumir (summaryModel ou agents.defaults.model.primary)
                                      -> TTS -> anexar áudio
```

## Uso do comando slash

Há um único comando: `/tts`.
Veja [Comandos slash](/pt-BR/tools/slash-commands) para detalhes de ativação.

Observação sobre o Discord: `/tts` é um comando nativo do Discord, então o OpenClaw registra
`/voice` como o comando nativo lá. O texto `/tts ...` ainda funciona.

```
/tts off
/tts on
/tts status
/tts provider openai
/tts limit 2000
/tts summary off
/tts audio Hello from OpenClaw
```

Observações:

- Os comandos exigem um remetente autorizado (regras de allowlist/proprietário ainda se aplicam).
- `commands.text` ou o registro de comando nativo deve estar ativado.
- A configuração `messages.tts.auto` aceita `off|always|inbound|tagged`.
- `/tts on` grava a preferência local de TTS como `always`; `/tts off` grava como `off`.
- Use a configuração quando quiser padrões `inbound` ou `tagged`.
- `limit` e `summary` são armazenados nas preferências locais, não na configuração principal.
- `/tts audio` gera uma resposta de áudio única (não ativa o TTS).
- `/tts status` inclui visibilidade de fallback para a tentativa mais recente:
  - fallback com sucesso: `Fallback: <primary> -> <used>` mais `Attempts: ...`
  - falha: `Error: ...` mais `Attempts: ...`
  - diagnósticos detalhados: `Attempt details: provider:outcome(reasonCode) latency`
- Falhas de API de OpenAI e ElevenLabs agora incluem detalhes de erro do provedor analisados e id da solicitação (quando retornado pelo provedor), o que aparece em erros/logs de TTS.

## Ferramenta do agente

A ferramenta `tts` converte texto em fala e retorna um anexo de áudio para
entrega na resposta. Quando o canal é Feishu, Matrix, Telegram ou WhatsApp,
o áudio é entregue como mensagem de voz em vez de anexo de arquivo.

## RPC do Gateway

Métodos do Gateway:

- `tts.status`
- `tts.enable`
- `tts.disable`
- `tts.convert`
- `tts.setProvider`
- `tts.providers`
