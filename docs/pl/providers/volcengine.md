---
read_when:
    - Chcesz używać modeli Volcano Engine lub Doubao z OpenClaw
    - Potrzebujesz konfiguracji klucza API Volcengine
summary: Konfiguracja Volcano Engine (modele Doubao, endpointy ogólne + do kodowania)
title: Volcengine (Doubao)
x-i18n:
    generated_at: "2026-04-12T23:33:36Z"
    model: gpt-5.4
    provider: openai
    source_hash: a21f390da719f79c88c6d55a7d952d35c2ce5ff26d910c9f10020132cd7d2f4c
    source_path: providers/volcengine.md
    workflow: 15
---

# Volcengine (Doubao)

Dostawca Volcengine zapewnia dostęp do modeli Doubao i modeli zewnętrznych
hostowanych na Volcano Engine, z oddzielnymi endpointami dla obciążeń ogólnych i związanych z kodowaniem.

| Szczegół   | Wartość                                             |
| ---------- | --------------------------------------------------- |
| Dostawcy   | `volcengine` (ogólne) + `volcengine-plan` (kodowanie) |
| Uwierzytelnianie | `VOLCANO_ENGINE_API_KEY`                      |
| API        | Zgodne z OpenAI                                     |

## Pierwsze kroki

<Steps>
  <Step title="Ustaw klucz API">
    Uruchom interaktywny onboarding:

    ```bash
    openclaw onboard --auth-choice volcengine-api-key
    ```

    To rejestruje zarówno dostawcę ogólnego (`volcengine`), jak i dostawcę do kodowania (`volcengine-plan`) przy użyciu jednego klucza API.

  </Step>
  <Step title="Ustaw model domyślny">
    ```json5
    {
      agents: {
        defaults: {
          model: { primary: "volcengine-plan/ark-code-latest" },
        },
      },
    }
    ```
  </Step>
  <Step title="Sprawdź, czy model jest dostępny">
    ```bash
    openclaw models list --provider volcengine
    openclaw models list --provider volcengine-plan
    ```
  </Step>
</Steps>

<Tip>
W przypadku konfiguracji nieinteraktywnej (CI, skrypty) przekaż klucz bezpośrednio:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice volcengine-api-key \
  --volcengine-api-key "$VOLCANO_ENGINE_API_KEY"
```

</Tip>

## Dostawcy i endpointy

| Dostawca          | Endpoint                                  | Przypadek użycia |
| ----------------- | ----------------------------------------- | ---------------- |
| `volcengine`      | `ark.cn-beijing.volces.com/api/v3`        | Modele ogólne    |
| `volcengine-plan` | `ark.cn-beijing.volces.com/api/coding/v3` | Modele do kodowania |

<Note>
Obaj dostawcy są konfigurowani przy użyciu jednego klucza API. Konfiguracja rejestruje obu automatycznie.
</Note>

## Dostępne modele

<Tabs>
  <Tab title="Ogólne (volcengine)">
    | Odwołanie modelu                            | Nazwa                           | Wejście     | Kontekst |
    | ------------------------------------------- | ------------------------------- | ----------- | -------- |
    | `volcengine/doubao-seed-1-8-251228`         | Doubao Seed 1.8                 | text, image | 256,000  |
    | `volcengine/doubao-seed-code-preview-251028`| doubao-seed-code-preview-251028 | text, image | 256,000  |
    | `volcengine/kimi-k2-5-260127`               | Kimi K2.5                       | text, image | 256,000  |
    | `volcengine/glm-4-7-251222`                 | GLM 4.7                         | text, image | 200,000  |
    | `volcengine/deepseek-v3-2-251201`           | DeepSeek V3.2                   | text, image | 128,000  |
  </Tab>
  <Tab title="Kodowanie (volcengine-plan)">
    | Odwołanie modelu                                | Nazwa                    | Wejście | Kontekst |
    | ------------------------------------------------ | ------------------------ | ------- | -------- |
    | `volcengine-plan/ark-code-latest`                | Ark Coding Plan          | text    | 256,000  |
    | `volcengine-plan/doubao-seed-code`               | Doubao Seed Code         | text    | 256,000  |
    | `volcengine-plan/glm-4.7`                        | GLM 4.7 Coding           | text    | 200,000  |
    | `volcengine-plan/kimi-k2-thinking`               | Kimi K2 Thinking         | text    | 256,000  |
    | `volcengine-plan/kimi-k2.5`                      | Kimi K2.5 Coding         | text    | 256,000  |
    | `volcengine-plan/doubao-seed-code-preview-251028`| Doubao Seed Code Preview | text    | 256,000  |
  </Tab>
</Tabs>

## Uwagi zaawansowane

<AccordionGroup>
  <Accordion title="Model domyślny po onboardingu">
    `openclaw onboard --auth-choice volcengine-api-key` obecnie ustawia
    `volcengine-plan/ark-code-latest` jako model domyślny, jednocześnie rejestrując
    ogólny katalog `volcengine`.
  </Accordion>

  <Accordion title="Zachowanie fallbacku selektora modeli">
    Podczas wybierania modelu w onboardingu/konfiguracji opcja uwierzytelniania Volcengine preferuje
    zarówno wiersze `volcengine/*`, jak i `volcengine-plan/*`. Jeśli te modele nie są jeszcze
    załadowane, OpenClaw wraca do niefiltrowanego katalogu zamiast pokazywać pusty
    selektor ograniczony do dostawcy.
  </Accordion>

  <Accordion title="Zmienne środowiskowe dla procesów demona">
    Jeśli Gateway działa jako demon (launchd/systemd), upewnij się, że
    `VOLCANO_ENGINE_API_KEY` jest dostępne dla tego procesu (na przykład w
    `~/.openclaw/.env` albo przez `env.shellEnv`).
  </Accordion>
</AccordionGroup>

<Warning>
Podczas uruchamiania OpenClaw jako usługi w tle zmienne środowiskowe ustawione w Twojej
interaktywnej powłoce nie są dziedziczone automatycznie. Zobacz uwagę o demonie powyżej.
</Warning>

## Powiązane

<CardGroup cols={2}>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, odwołań do modeli i zachowania failover.
  </Card>
  <Card title="Konfiguracja" href="/pl/gateway/configuration" icon="gear">
    Pełna referencja konfiguracji agentów, modeli i dostawców.
  </Card>
  <Card title="Rozwiązywanie problemów" href="/pl/help/troubleshooting" icon="wrench">
    Typowe problemy i kroki debugowania.
  </Card>
  <Card title="FAQ" href="/pl/help/faq" icon="circle-question">
    Najczęściej zadawane pytania dotyczące konfiguracji OpenClaw.
  </Card>
</CardGroup>
