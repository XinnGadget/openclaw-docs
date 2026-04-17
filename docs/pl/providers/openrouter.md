---
read_when:
    - Chcesz używać jednego klucza API do wielu LLM-ów
    - Chcesz uruchamiać modele przez OpenRouter w OpenClaw
summary: Używaj ujednoliconego API OpenRouter, aby uzyskać dostęp do wielu modeli w OpenClaw
title: OpenRouter
x-i18n:
    generated_at: "2026-04-12T23:32:40Z"
    model: gpt-5.4
    provider: openai
    source_hash: 9083c30b9e9846a9d4ef071c350576d4c3083475f4108871eabbef0b9bb9a368
    source_path: providers/openrouter.md
    workflow: 15
---

# OpenRouter

OpenRouter udostępnia **ujednolicone API**, które kieruje żądania do wielu modeli za jednym
endpointem i kluczem API. Jest zgodne z OpenAI, więc większość SDK OpenAI działa po zmianie bazowego URL.

## Pierwsze kroki

<Steps>
  <Step title="Pobierz klucz API">
    Utwórz klucz API na [openrouter.ai/keys](https://openrouter.ai/keys).
  </Step>
  <Step title="Uruchom onboarding">
    ```bash
    openclaw onboard --auth-choice openrouter-api-key
    ```
  </Step>
  <Step title="(Opcjonalnie) Przełącz na konkretny model">
    Onboarding domyślnie ustawia `openrouter/auto`. Później wybierz konkretny model:

    ```bash
    openclaw models set openrouter/<provider>/<model>
    ```

  </Step>
</Steps>

## Przykład konfiguracji

```json5
{
  env: { OPENROUTER_API_KEY: "sk-or-..." },
  agents: {
    defaults: {
      model: { primary: "openrouter/auto" },
    },
  },
}
```

## Odwołania do modeli

<Note>
Odwołania do modeli mają postać `openrouter/<provider>/<model>`. Pełną listę
dostępnych dostawców i modeli znajdziesz w [/concepts/model-providers](/pl/concepts/model-providers).
</Note>

## Uwierzytelnianie i nagłówki

OpenRouter używa wewnętrznie tokenu Bearer z Twoim kluczem API.

Przy rzeczywistych żądaniach OpenRouter (`https://openrouter.ai/api/v1`) OpenClaw dodaje też
udokumentowane przez OpenRouter nagłówki atrybucji aplikacji:

| Nagłówek                 | Wartość               |
| ------------------------ | --------------------- |
| `HTTP-Referer`           | `https://openclaw.ai` |
| `X-OpenRouter-Title`     | `OpenClaw`            |
| `X-OpenRouter-Categories`| `cli-agent`           |

<Warning>
Jeśli przekierujesz dostawcę OpenRouter na inne proxy lub bazowy URL, OpenClaw
**nie** wstrzykuje tych nagłówków specyficznych dla OpenRouter ani znaczników cache Anthropic.
</Warning>

## Uwagi zaawansowane

<AccordionGroup>
  <Accordion title="Znaczniki cache Anthropic">
    Na zweryfikowanych trasach OpenRouter odwołania do modeli Anthropic zachowują
    specyficzne dla OpenRouter znaczniki Anthropic `cache_control`, których OpenClaw używa do
    lepszego ponownego użycia cache promptów w blokach promptów system/developer.
  </Accordion>

  <Accordion title="Wstrzykiwanie thinking / reasoning">
    Na obsługiwanych trasach innych niż `auto` OpenClaw mapuje wybrany poziom thinking na
    payloady reasoning proxy OpenRouter. Nieobsługiwane wskazówki modelu oraz
    `openrouter/auto` pomijają to wstrzykiwanie reasoning.
  </Accordion>

  <Accordion title="Formatowanie żądań tylko dla OpenAI">
    OpenRouter nadal działa przez kompatybilną z OpenAI ścieżkę w stylu proxy, więc
    natywne formatowanie żądań tylko dla OpenAI, takie jak `serviceTier`, `store` dla Responses,
    payloady zgodności reasoning OpenAI i wskazówki cache promptów, nie jest przekazywane dalej.
  </Accordion>

  <Accordion title="Trasy oparte na Gemini">
    Odwołania OpenRouter oparte na Gemini pozostają na ścieżce proxy-Gemini: OpenClaw zachowuje tam
    sanityzację podpisu myśli Gemini, ale nie włącza natywnej walidacji replay Gemini
    ani przepisania bootstrapu.
  </Accordion>

  <Accordion title="Metadane routingu dostawcy">
    Jeśli przekażesz routing dostawcy OpenRouter w parametrach modelu, OpenClaw przekaże
    go jako metadane routingu OpenRouter, zanim uruchomią się współdzielone wrappery streamu.
  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, odwołań do modeli i zachowania failover.
  </Card>
  <Card title="Referencja konfiguracji" href="/pl/gateway/configuration-reference" icon="gear">
    Pełna referencja konfiguracji agentów, modeli i dostawców.
  </Card>
</CardGroup>
