---
read_when:
    - Chcesz używać Qwen z OpenClaw
    - Wcześniej używałeś OAuth Qwen
summary: Używaj Qwen Cloud przez wbudowanego providera qwen w OpenClaw
title: Qwen
x-i18n:
    generated_at: "2026-04-06T03:12:03Z"
    model: gpt-5.4
    provider: openai
    source_hash: f175793693ab6a4c3f1f4d42040e673c15faf7603a500757423e9e06977c989d
    source_path: providers/qwen.md
    workflow: 15
---

# Qwen

<Warning>

**OAuth Qwen został usunięty.** Integracja OAuth w warstwie darmowej
(`qwen-portal`), która używała endpointów `portal.qwen.ai`, nie jest już dostępna.
Szczegóły znajdziesz w [Issue #49557](https://github.com/openclaw/openclaw/issues/49557).

</Warning>

## Zalecane: Qwen Cloud

OpenClaw traktuje teraz Qwen jako pełnoprawnego wbudowanego providera z kanonicznym identyfikatorem
`qwen`. Wbudowany provider kieruje ruch do endpointów Qwen Cloud / Alibaba DashScope oraz
Coding Plan i zachowuje starsze identyfikatory `modelstudio` jako alias
zgodności.

- Provider: `qwen`
- Preferowana zmienna środowiskowa: `QWEN_API_KEY`
- Akceptowane również dla zgodności: `MODELSTUDIO_API_KEY`, `DASHSCOPE_API_KEY`
- Styl API: zgodny z OpenAI

Jeśli chcesz używać `qwen3.6-plus`, preferuj endpoint **Standard (pay-as-you-go)**.
Obsługa Coding Plan może być opóźniona względem publicznego katalogu.

```bash
# Globalny endpoint Coding Plan
openclaw onboard --auth-choice qwen-api-key

# Chiński endpoint Coding Plan
openclaw onboard --auth-choice qwen-api-key-cn

# Globalny endpoint Standard (pay-as-you-go)
openclaw onboard --auth-choice qwen-standard-api-key

# Chiński endpoint Standard (pay-as-you-go)
openclaw onboard --auth-choice qwen-standard-api-key-cn
```

Starsze identyfikatory `modelstudio-*` dla `auth-choice` oraz odwołania do modeli `modelstudio/...` nadal
działają jako aliasy zgodności, ale nowe przepływy konfiguracji powinny preferować kanoniczne
identyfikatory `qwen-*` dla `auth-choice` oraz odwołania do modeli `qwen/...`.

Po onboardingu ustaw model domyślny:

```json5
{
  agents: {
    defaults: {
      model: { primary: "qwen/qwen3.5-plus" },
    },
  },
}
```

## Typy planów i endpointy

| Plan                       | Region | Auth choice                | Endpoint                                         |
| -------------------------- | ------ | -------------------------- | ------------------------------------------------ |
| Standard (pay-as-you-go)   | Chiny  | `qwen-standard-api-key-cn` | `dashscope.aliyuncs.com/compatible-mode/v1`      |
| Standard (pay-as-you-go)   | Global | `qwen-standard-api-key`    | `dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| Coding Plan (subskrypcja)  | Chiny  | `qwen-api-key-cn`          | `coding.dashscope.aliyuncs.com/v1`               |
| Coding Plan (subskrypcja)  | Global | `qwen-api-key`             | `coding-intl.dashscope.aliyuncs.com/v1`          |

Provider automatycznie wybiera endpoint na podstawie Twojego wyboru auth. Kanoniczne
wybory używają rodziny `qwen-*`; `modelstudio-*` pozostaje wyłącznie warstwą zgodności.
Możesz nadpisać to własnym `baseUrl` w konfiguracji.

Natywne endpointy Model Studio sygnalizują zgodność użycia streamingu na
współdzielonym transporcie `openai-completions`. OpenClaw opiera to teraz na możliwościach endpointu, więc
niestandardowe identyfikatory providerów zgodne z DashScope, kierujące ruch na te same
natywne hosty, dziedziczą to samo zachowanie użycia streamingu zamiast
wymagać konkretnie wbudowanego identyfikatora providera `qwen`.

## Pobierz swój klucz API

- **Zarządzanie kluczami**: [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys)
- **Dokumentacja**: [docs.qwencloud.com](https://docs.qwencloud.com/developer-guides/getting-started/introduction)

## Wbudowany katalog

OpenClaw obecnie dostarcza ten wbudowany katalog Qwen:

| Model ref                   | Input       | Context   | Notes                                              |
| --------------------------- | ----------- | --------- | -------------------------------------------------- |
| `qwen/qwen3.5-plus`         | text, image | 1,000,000 | Model domyślny                                     |
| `qwen/qwen3.6-plus`         | text, image | 1,000,000 | Preferuj endpointy Standard, jeśli potrzebujesz tego modelu |
| `qwen/qwen3-max-2026-01-23` | text        | 262,144   | Linia Qwen Max                                     |
| `qwen/qwen3-coder-next`     | text        | 262,144   | Coding                                             |
| `qwen/qwen3-coder-plus`     | text        | 1,000,000 | Coding                                             |
| `qwen/MiniMax-M2.5`         | text        | 1,000,000 | Reasoning włączony                                 |
| `qwen/glm-5`                | text        | 202,752   | GLM                                                |
| `qwen/glm-4.7`              | text        | 202,752   | GLM                                                |
| `qwen/kimi-k2.5`            | text, image | 262,144   | Moonshot AI przez Alibaba                          |

Dostępność może nadal różnić się w zależności od endpointu i planu rozliczeń, nawet jeśli model
jest obecny we wbudowanym katalogu.

Zgodność użycia native-streaming dotyczy zarówno hostów Coding Plan, jak i
hostów Standard zgodnych z DashScope:

- `https://coding.dashscope.aliyuncs.com/v1`
- `https://coding-intl.dashscope.aliyuncs.com/v1`
- `https://dashscope.aliyuncs.com/compatible-mode/v1`
- `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`

## Dostępność Qwen 3.6 Plus

`qwen3.6-plus` jest dostępny na endpointach Model Studio Standard (pay-as-you-go):

- Chiny: `dashscope.aliyuncs.com/compatible-mode/v1`
- Global: `dashscope-intl.aliyuncs.com/compatible-mode/v1`

Jeśli endpointy Coding Plan zwracają błąd „unsupported model” dla
`qwen3.6-plus`, przełącz się na Standard (pay-as-you-go) zamiast używać pary
endpoint/klucz dla Coding Plan.

## Plan możliwości

Rozszerzenie `qwen` jest pozycjonowane jako docelowe miejsce dostawcy dla całej powierzchni Qwen
Cloud, a nie tylko modeli coding/text.

- Modele text/chat: już wbudowane
- Tool calling, structured output, thinking: dziedziczone z transportu zgodnego z OpenAI
- Image generation: planowane na warstwie pluginu providera
- Image/video understanding: już wbudowane na endpointach Standard
- Speech/audio: planowane na warstwie pluginu providera
- Embeddingi/reranking pamięci: planowane przez powierzchnię adaptera embeddingów
- Video generation: już wbudowane przez współdzieloną możliwość generowania wideo

## Dodatki multimodalne

Rozszerzenie `qwen` udostępnia teraz także:

- Video understanding przez `qwen-vl-max-latest`
- Generowanie wideo Wan przez:
  - `wan2.6-t2v` (domyślnie)
  - `wan2.6-i2v`
  - `wan2.6-r2v`
  - `wan2.6-r2v-flash`
  - `wan2.7-r2v`

Te powierzchnie multimodalne używają endpointów DashScope **Standard**, a nie
endpointów Coding Plan.

- Globalny/międzynarodowy podstawowy URL Standard: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
- Chiński podstawowy URL Standard: `https://dashscope.aliyuncs.com/compatible-mode/v1`

Dla generowania wideo OpenClaw mapuje skonfigurowany region Qwen na odpowiadający mu
host DashScope AIGC przed wysłaniem zadania:

- Global/Intl: `https://dashscope-intl.aliyuncs.com`
- Chiny: `https://dashscope.aliyuncs.com`

Oznacza to, że zwykłe `models.providers.qwen.baseUrl` wskazujące na hosty Qwen
Coding Plan lub Standard nadal utrzymuje generowanie wideo na poprawnym
regionalnym endpointzie wideo DashScope.

Dla generowania wideo ustaw model domyślny jawnie:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: { primary: "qwen/wan2.6-t2v" },
    },
  },
}
```

Bieżące ograniczenia wbudowanego generowania wideo Qwen:

- Maksymalnie **1** wyjściowe wideo na żądanie
- Maksymalnie **1** obraz wejściowy
- Maksymalnie **4** wejściowe wideo
- Maksymalnie **10 sekund** czasu trwania
- Obsługuje `size`, `aspectRatio`, `resolution`, `audio` i `watermark`
- Tryb obrazu/wideo referencyjnego obecnie wymaga **zdalnych URL `http(s)`**. Lokalne
  ścieżki plików są odrzucane od razu, ponieważ endpoint wideo DashScope nie
  akceptuje przesyłanych lokalnych buforów dla tych referencji.

Zobacz [Generowanie wideo](/tools/video-generation), aby poznać współdzielone
parametry narzędzia, wybór providera i zachowanie failover.

## Uwaga dotycząca środowiska

Jeśli Gateway działa jako daemon (launchd/systemd), upewnij się, że `QWEN_API_KEY` jest
dostępny dla tego procesu (na przykład w `~/.openclaw/.env` lub przez
`env.shellEnv`).
