---
read_when:
    - Chcesz używać Fireworks z OpenClaw
    - Potrzebujesz zmiennej środowiskowej z kluczem API Fireworks albo domyślnego ID modelu
summary: Konfiguracja Fireworks (uwierzytelnianie + wybór modelu)
title: Fireworks
x-i18n:
    generated_at: "2026-04-12T23:30:49Z"
    model: gpt-5.4
    provider: openai
    source_hash: 1a85d9507c19e275fdd846a303d844eda8045d008774d4dde1eae408e8716b6f
    source_path: providers/fireworks.md
    workflow: 15
---

# Fireworks

[Fireworks](https://fireworks.ai) udostępnia modele open-weight i routowane przez API zgodne z OpenAI. OpenClaw zawiera dołączony Plugin dostawcy Fireworks.

| Właściwość     | Wartość                                                |
| -------------- | ------------------------------------------------------ |
| Dostawca       | `fireworks`                                            |
| Uwierzytelnianie | `FIREWORKS_API_KEY`                                  |
| API            | Zgodne z OpenAI chat/completions                       |
| Bazowy URL     | `https://api.fireworks.ai/inference/v1`                |
| Model domyślny | `fireworks/accounts/fireworks/routers/kimi-k2p5-turbo` |

## Pierwsze kroki

<Steps>
  <Step title="Skonfiguruj uwierzytelnianie Fireworks przez onboarding">
    ```bash
    openclaw onboard --auth-choice fireworks-api-key
    ```

    To zapisuje Twój klucz Fireworks w konfiguracji OpenClaw i ustawia model startowy Fire Pass jako domyślny.

  </Step>
  <Step title="Sprawdź, czy model jest dostępny">
    ```bash
    openclaw models list --provider fireworks
    ```
  </Step>
</Steps>

## Przykład nieinteraktywny

W przypadku konfiguracji skryptowych lub CI przekaż wszystkie wartości w wierszu poleceń:

```bash
openclaw onboard --non-interactive \
  --mode local \
  --auth-choice fireworks-api-key \
  --fireworks-api-key "$FIREWORKS_API_KEY" \
  --skip-health \
  --accept-risk
```

## Wbudowany katalog

| Odwołanie modelu                                      | Nazwa                       | Wejście    | Kontekst | Maks. wyjście | Uwagi                                      |
| ----------------------------------------------------- | --------------------------- | ---------- | -------- | ------------- | ------------------------------------------ |
| `fireworks/accounts/fireworks/routers/kimi-k2p5-turbo` | Kimi K2.5 Turbo (Fire Pass) | text,image | 256,000  | 256,000       | Domyślny dołączony model startowy w Fireworks |

<Tip>
Jeśli Fireworks opublikuje nowszy model, taki jak świeże wydanie Qwen lub Gemma, możesz przełączyć się na niego bezpośrednio, używając jego ID modelu Fireworks bez czekania na aktualizację dołączonego katalogu.
</Tip>

## Niestandardowe ID modeli Fireworks

OpenClaw akceptuje również dynamiczne ID modeli Fireworks. Użyj dokładnego ID modelu lub routera pokazanego przez Fireworks i poprzedź je `fireworks/`.

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "fireworks/accounts/fireworks/routers/kimi-k2p5-turbo",
      },
    },
  },
}
```

<AccordionGroup>
  <Accordion title="Jak działa prefiksowanie ID modelu">
    Każde odwołanie do modelu Fireworks w OpenClaw zaczyna się od `fireworks/`, po którym następuje dokładne ID lub ścieżka routera z platformy Fireworks. Na przykład:

    - Model routera: `fireworks/accounts/fireworks/routers/kimi-k2p5-turbo`
    - Model bezpośredni: `fireworks/accounts/fireworks/models/<model-name>`

    OpenClaw usuwa prefiks `fireworks/` podczas budowania żądania API i wysyła pozostałą ścieżkę do endpointu Fireworks.

  </Accordion>

  <Accordion title="Uwaga o środowisku">
    Jeśli Gateway działa poza Twoją interaktywną powłoką, upewnij się, że `FIREWORKS_API_KEY` jest dostępne również dla tego procesu.

    <Warning>
    Klucz zapisany tylko w `~/.profile` nie pomoże demonowi launchd/systemd, jeśli to środowisko nie zostanie tam również zaimportowane. Ustaw klucz w `~/.openclaw/.env` albo przez `env.shellEnv`, aby proces gateway mógł go odczytać.
    </Warning>

  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Wybór modelu" href="/pl/concepts/model-providers" icon="layers">
    Wybór dostawców, odwołań do modeli i zachowania failover.
  </Card>
  <Card title="Rozwiązywanie problemów" href="/pl/help/troubleshooting" icon="wrench">
    Ogólne rozwiązywanie problemów i FAQ.
  </Card>
</CardGroup>
