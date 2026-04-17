---
read_when:
    - Chcesz używać Qwen z OpenClaw
    - Wcześniej używałeś Qwen OAuth
summary: Używaj Qwen Cloud przez dołączonego dostawcę qwen w OpenClaw
title: Qwen
x-i18n:
    generated_at: "2026-04-12T23:33:03Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5247f851ef891645df6572d748ea15deeea47cd1d75858bc0d044a2930065106
    source_path: providers/qwen.md
    workflow: 15
---

# Qwen

<Warning>

**Qwen OAuth zostało usunięte.** Integracja darmowej warstwy OAuth
(`qwen-portal`), która używała endpointów `portal.qwen.ai`, nie jest już dostępna.
Tło znajdziesz w [Issue #49557](https://github.com/openclaw/openclaw/issues/49557).

</Warning>

OpenClaw traktuje teraz Qwen jako pełnoprawnego dołączonego dostawcę z kanonicznym identyfikatorem
`qwen`. Dołączony dostawca kieruje ruch do endpointów Qwen Cloud / Alibaba DashScope oraz
Coding Plan i zachowuje starsze identyfikatory `modelstudio` jako alias zgodności.

- Dostawca: `qwen`
- Preferowana zmienna środowiskowa: `QWEN_API_KEY`
- Akceptowane także dla zgodności: `MODELSTUDIO_API_KEY`, `DASHSCOPE_API_KEY`
- Styl API: zgodny z OpenAI

<Tip>
Jeśli chcesz używać `qwen3.6-plus`, wybierz endpoint **Standard (pay-as-you-go)**.
Obsługa Coding Plan może pozostawać w tyle za publicznym katalogiem.
</Tip>

## Pierwsze kroki

Wybierz typ planu i wykonaj kroki konfiguracji.

<Tabs>
  <Tab title="Coding Plan (subskrypcja)">
    **Najlepsze dla:** dostępu opartego na subskrypcji przez Qwen Coding Plan.

    <Steps>
      <Step title="Pobierz swój klucz API">
        Utwórz lub skopiuj klucz API z [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys).
      </Step>
      <Step title="Uruchom onboarding">
        Dla endpointu **Global**:

        ```bash
        openclaw onboard --auth-choice qwen-api-key
        ```

        Dla endpointu **China**:

        ```bash
        openclaw onboard --auth-choice qwen-api-key-cn
        ```
      </Step>
      <Step title="Ustaw model domyślny">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "qwen/qwen3.5-plus" },
            },
          },
        }
        ```
      </Step>
      <Step title="Sprawdź, czy model jest dostępny">
        ```bash
        openclaw models list --provider qwen
        ```
      </Step>
    </Steps>

    <Note>
    Starsze identyfikatory `auth-choice` z rodziny `modelstudio-*` oraz odwołania do modeli `modelstudio/...` nadal
    działają jako aliasy zgodności, ale nowe przepływy konfiguracji powinny preferować kanoniczne
    identyfikatory `auth-choice` z rodziny `qwen-*` oraz odwołania do modeli `qwen/...`.
    </Note>

  </Tab>

  <Tab title="Standard (pay-as-you-go)">
    **Najlepsze dla:** dostępu pay-as-you-go przez endpoint Standard Model Studio, w tym modeli takich jak `qwen3.6-plus`, które mogą nie być dostępne w Coding Plan.

    <Steps>
      <Step title="Pobierz swój klucz API">
        Utwórz lub skopiuj klucz API z [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys).
      </Step>
      <Step title="Uruchom onboarding">
        Dla endpointu **Global**:

        ```bash
        openclaw onboard --auth-choice qwen-standard-api-key
        ```

        Dla endpointu **China**:

        ```bash
        openclaw onboard --auth-choice qwen-standard-api-key-cn
        ```
      </Step>
      <Step title="Ustaw model domyślny">
        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "qwen/qwen3.5-plus" },
            },
          },
        }
        ```
      </Step>
      <Step title="Sprawdź, czy model jest dostępny">
        ```bash
        openclaw models list --provider qwen
        ```
      </Step>
    </Steps>

    <Note>
    Starsze identyfikatory `auth-choice` z rodziny `modelstudio-*` oraz odwołania do modeli `modelstudio/...` nadal
    działają jako aliasy zgodności, ale nowe przepływy konfiguracji powinny preferować kanoniczne
    identyfikatory `auth-choice` z rodziny `qwen-*` oraz odwołania do modeli `qwen/...`.
    </Note>

  </Tab>
</Tabs>

## Typy planów i endpointy

| Plan                       | Region | Auth choice                | Endpoint                                         |
| -------------------------- | ------ | -------------------------- | ------------------------------------------------ |
| Standard (pay-as-you-go)   | China  | `qwen-standard-api-key-cn` | `dashscope.aliyuncs.com/compatible-mode/v1`      |
| Standard (pay-as-you-go)   | Global | `qwen-standard-api-key`    | `dashscope-intl.aliyuncs.com/compatible-mode/v1` |
| Coding Plan (subskrypcja)  | China  | `qwen-api-key-cn`          | `coding.dashscope.aliyuncs.com/v1`               |
| Coding Plan (subskrypcja)  | Global | `qwen-api-key`             | `coding-intl.dashscope.aliyuncs.com/v1`          |

Dostawca automatycznie wybiera endpoint na podstawie Twojego `auth choice`. Kanoniczne
wybory używają rodziny `qwen-*`; `modelstudio-*` pozostaje tylko dla zgodności.
Możesz nadpisać to przez niestandardowe `baseUrl` w konfiguracji.

<Tip>
**Zarządzanie kluczami:** [home.qwencloud.com/api-keys](https://home.qwencloud.com/api-keys) |
**Dokumentacja:** [docs.qwencloud.com](https://docs.qwencloud.com/developer-guides/getting-started/introduction)
</Tip>

## Wbudowany katalog

OpenClaw obecnie dostarcza ten dołączony katalog Qwen. Skonfigurowany katalog jest
świadomy endpointu: konfiguracje Coding Plan pomijają modele, o których wiadomo, że działają
tylko na endpointach Standard.

| Odwołanie do modelu        | Wejście     | Kontekst  | Uwagi                                               |
| -------------------------- | ----------- | --------- | --------------------------------------------------- |
| `qwen/qwen3.5-plus`        | text, image | 1,000,000 | Model domyślny                                      |
| `qwen/qwen3.6-plus`        | text, image | 1,000,000 | Gdy potrzebujesz tego modelu, preferuj endpointy Standard |
| `qwen/qwen3-max-2026-01-23`| text        | 262,144   | Linia Qwen Max                                      |
| `qwen/qwen3-coder-next`    | text        | 262,144   | Kodowanie                                           |
| `qwen/qwen3-coder-plus`    | text        | 1,000,000 | Kodowanie                                           |
| `qwen/MiniMax-M2.5`        | text        | 1,000,000 | Obsługa rozumowania włączona                        |
| `qwen/glm-5`               | text        | 202,752   | GLM                                                 |
| `qwen/glm-4.7`             | text        | 202,752   | GLM                                                 |
| `qwen/kimi-k2.5`           | text, image | 262,144   | Moonshot AI przez Alibaba                           |

<Note>
Dostępność nadal może się różnić w zależności od endpointu i planu rozliczeniowego, nawet jeśli model
występuje w dołączonym katalogu.
</Note>

## Dodatki multimodalne

Rozszerzenie `qwen` udostępnia także możliwości multimodalne na endpointach **Standard**
DashScope (nie na endpointach Coding Plan):

- **Rozumienie wideo** przez `qwen-vl-max-latest`
- **Generowanie wideo Wan** przez `wan2.6-t2v` (domyślnie), `wan2.6-i2v`, `wan2.6-r2v`, `wan2.6-r2v-flash`, `wan2.7-r2v`

Aby używać Qwen jako domyślnego dostawcy wideo:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: { primary: "qwen/wan2.6-t2v" },
    },
  },
}
```

<Note>
Zobacz [Video Generation](/pl/tools/video-generation), aby poznać wspólne parametry narzędzia, wybór dostawcy i zachowanie failover.
</Note>

## Zaawansowane

<AccordionGroup>
  <Accordion title="Rozumienie obrazów i wideo">
    Dołączony Plugin Qwen rejestruje rozumienie mediów dla obrazów i wideo
    na endpointach **Standard** DashScope (nie na endpointach Coding Plan).

    | Właściwość      | Wartość              |
    | --------------- | -------------------- |
    | Model           | `qwen-vl-max-latest` |
    | Obsługiwane wejście | Obrazy, wideo     |

    Rozumienie mediów jest automatycznie rozpoznawane na podstawie skonfigurowanego uwierzytelniania Qwen — nie
    jest potrzebna żadna dodatkowa konfiguracja. Upewnij się, że używasz endpointu Standard (pay-as-you-go),
    jeśli chcesz obsługi rozumienia mediów.

  </Accordion>

  <Accordion title="Dostępność Qwen 3.6 Plus">
    `qwen3.6-plus` jest dostępny na endpointach Standard (pay-as-you-go) Model Studio:

    - China: `dashscope.aliyuncs.com/compatible-mode/v1`
    - Global: `dashscope-intl.aliyuncs.com/compatible-mode/v1`

    Jeśli endpointy Coding Plan zwracają błąd „unsupported model” dla
    `qwen3.6-plus`, przełącz się na Standard (pay-as-you-go) zamiast pary
    endpoint/klucz Coding Plan.

  </Accordion>

  <Accordion title="Plan możliwości">
    Rozszerzenie `qwen` jest pozycjonowane jako dom dostawcy dla pełnej powierzchni Qwen
    Cloud, a nie tylko modeli do kodowania/tekstu.

    - **Modele tekstowe/czatowe:** dołączone teraz
    - **Wywoływanie narzędzi, strukturalne wyjście, myślenie:** dziedziczone z transportu zgodnego z OpenAI
    - **Generowanie obrazów:** planowane na warstwie Pluginu dostawcy
    - **Rozumienie obrazów/wideo:** dołączone teraz na endpointach Standard
    - **Mowa/audio:** planowane na warstwie Pluginu dostawcy
    - **Osadzania/reranking pamięci:** planowane przez powierzchnię adaptera osadzania
    - **Generowanie wideo:** dołączone teraz przez współdzieloną możliwość generowania wideo

  </Accordion>

  <Accordion title="Szczegóły generowania wideo">
    W przypadku generowania wideo OpenClaw mapuje skonfigurowany region Qwen na pasujący
    host DashScope AIGC przed wysłaniem zadania:

    - Global/Intl: `https://dashscope-intl.aliyuncs.com`
    - China: `https://dashscope.aliyuncs.com`

    Oznacza to, że zwykłe `models.providers.qwen.baseUrl` wskazujące na hosty Qwen
    Coding Plan lub Standard nadal utrzymuje generowanie wideo na prawidłowym
    regionalnym endpointcie wideo DashScope.

    Bieżące limity dołączonego generowania wideo Qwen:

    - Maksymalnie **1** wyjściowe wideo na żądanie
    - Maksymalnie **1** obraz wejściowy
    - Maksymalnie **4** wejściowe wideo
    - Maksymalnie **10 sekund** czasu trwania
    - Obsługuje `size`, `aspectRatio`, `resolution`, `audio` i `watermark`
    - Tryb obrazu/wideo referencyjnego obecnie wymaga **zdalnych URL-i http(s)**. Lokalne
      ścieżki plików są odrzucane od razu, ponieważ endpoint wideo DashScope nie
      akceptuje przesłanych lokalnych buforów dla takich odniesień.

  </Accordion>

  <Accordion title="Zgodność użycia strumieniowego">
    Natywne endpointy Model Studio deklarują zgodność użycia strumieniowego na
    współdzielonym transporcie `openai-completions`. OpenClaw opiera to teraz na możliwościach endpointu,
    więc niestandardowe identyfikatory dostawców zgodnych z DashScope kierujące na
    te same natywne hosty dziedziczą to samo zachowanie użycia strumieniowego zamiast
    wymagać konkretnie wbudowanego identyfikatora dostawcy `qwen`.

    Zgodność natywnego użycia strumieniowego dotyczy zarówno hostów Coding Plan, jak i
    hostów Standard zgodnych z DashScope:

    - `https://coding.dashscope.aliyuncs.com/v1`
    - `https://coding-intl.dashscope.aliyuncs.com/v1`
    - `https://dashscope.aliyuncs.com/compatible-mode/v1`
    - `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`

  </Accordion>

  <Accordion title="Regiony endpointów multimodalnych">
    Powierzchnie multimodalne (rozumienie wideo i generowanie wideo Wan) używają
    endpointów **Standard** DashScope, a nie endpointów Coding Plan:

    - Global/Intl Standard base URL: `https://dashscope-intl.aliyuncs.com/compatible-mode/v1`
    - China Standard base URL: `https://dashscope.aliyuncs.com/compatible-mode/v1`

  </Accordion>

  <Accordion title="Konfiguracja środowiska i demona">
    Jeśli Gateway działa jako demon (launchd/systemd), upewnij się, że `QWEN_API_KEY` jest
    dostępny dla tego procesu (na przykład w `~/.openclaw/.env` lub przez
    `env.shellEnv`).
  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, odwołań do modeli i zachowania failover.
  </Card>
  <Card title="Video generation" href="/pl/tools/video-generation" icon="video">
    Wspólne parametry narzędzia wideo i wybór dostawcy.
  </Card>
  <Card title="Alibaba (ModelStudio)" href="/pl/providers/alibaba" icon="cloud">
    Starszy dostawca ModelStudio i uwagi dotyczące migracji.
  </Card>
  <Card title="Rozwiązywanie problemów" href="/pl/help/troubleshooting" icon="wrench">
    Ogólne rozwiązywanie problemów i FAQ.
  </Card>
</CardGroup>
