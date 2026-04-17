---
read_when:
    - Chcesz używać lokalnych przepływów pracy ComfyUI z OpenClaw
    - Chcesz używać Comfy Cloud z przepływami pracy obrazów, wideo lub muzyki
    - Potrzebujesz kluczy konfiguracji bundlowego Pluginu comfy
summary: Konfiguracja generowania obrazów, wideo i muzyki w przepływie pracy ComfyUI w OpenClaw
title: ComfyUI
x-i18n:
    generated_at: "2026-04-12T23:30:29Z"
    model: gpt-5.4
    provider: openai
    source_hash: 85db395b171f37f80b34b22f3e7707bffc1fd9138e7d10687eef13eaaa55cf24
    source_path: providers/comfy.md
    workflow: 15
---

# ComfyUI

OpenClaw dostarcza bundlowy Plugin `comfy` do uruchamiania ComfyUI sterowanego przepływami pracy. Plugin jest w pełni sterowany przepływem pracy, więc OpenClaw nie próbuje mapować ogólnych ustawień `size`, `aspectRatio`, `resolution`, `durationSeconds` ani kontrolek w stylu TTS na Twój graf.

| Właściwość       | Szczegóły                                                                        |
| ---------------- | -------------------------------------------------------------------------------- |
| Dostawca         | `comfy`                                                                          |
| Modele           | `comfy/workflow`                                                                 |
| Wspólne powierzchnie | `image_generate`, `video_generate`, `music_generate`                         |
| Auth             | Brak dla lokalnego ComfyUI; `COMFY_API_KEY` lub `COMFY_CLOUD_API_KEY` dla Comfy Cloud |
| API              | ComfyUI `/prompt` / `/history` / `/view` oraz Comfy Cloud `/api/*`               |

## Co jest obsługiwane

- Generowanie obrazów z JSON przepływu pracy
- Edycja obrazów z 1 przesłanym obrazem referencyjnym
- Generowanie wideo z JSON przepływu pracy
- Generowanie wideo z 1 przesłanym obrazem referencyjnym
- Generowanie muzyki lub audio przez wspólne narzędzie `music_generate`
- Pobieranie danych wyjściowych ze skonfigurowanego węzła lub ze wszystkich pasujących węzłów wyjściowych

## Pierwsze kroki

Wybierz między uruchamianiem ComfyUI na własnym komputerze a użyciem Comfy Cloud.

<Tabs>
  <Tab title="Lokalnie">
    **Najlepsze do:** uruchamiania własnej instancji ComfyUI na komputerze lub w sieci LAN.

    <Steps>
      <Step title="Uruchom ComfyUI lokalnie">
        Upewnij się, że lokalna instancja ComfyUI jest uruchomiona (domyślnie `http://127.0.0.1:8188`).
      </Step>
      <Step title="Przygotuj JSON przepływu pracy">
        Wyeksportuj lub utwórz plik JSON przepływu pracy ComfyUI. Zanotuj identyfikatory węzłów dla węzła wejścia promptu i węzła wyjściowego, z którego OpenClaw ma odczytywać dane.
      </Step>
      <Step title="Skonfiguruj dostawcę">
        Ustaw `mode: "local"` i wskaż plik przepływu pracy. Oto minimalny przykład dla obrazu:

        ```json5
        {
          models: {
            providers: {
              comfy: {
                mode: "local",
                baseUrl: "http://127.0.0.1:8188",
                image: {
                  workflowPath: "./workflows/flux-api.json",
                  promptNodeId: "6",
                  outputNodeId: "9",
                },
              },
            },
          },
        }
        ```
      </Step>
      <Step title="Ustaw model domyślny">
        Skieruj OpenClaw na model `comfy/workflow` dla skonfigurowanej capability:

        ```json5
        {
          agents: {
            defaults: {
              imageGenerationModel: {
                primary: "comfy/workflow",
              },
            },
          },
        }
        ```
      </Step>
      <Step title="Zweryfikuj">
        ```bash
        openclaw models list --provider comfy
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="Comfy Cloud">
    **Najlepsze do:** uruchamiania przepływów pracy w Comfy Cloud bez zarządzania lokalnymi zasobami GPU.

    <Steps>
      <Step title="Pobierz klucz API">
        Zarejestruj się na [comfy.org](https://comfy.org) i wygeneruj klucz API w panelu konta.
      </Step>
      <Step title="Ustaw klucz API">
        Podaj klucz jedną z poniższych metod:

        ```bash
        # Zmienna środowiskowa (zalecane)
        export COMFY_API_KEY="your-key"

        # Alternatywna zmienna środowiskowa
        export COMFY_CLOUD_API_KEY="your-key"

        # Albo bezpośrednio w konfiguracji
        openclaw config set models.providers.comfy.apiKey "your-key"
        ```
      </Step>
      <Step title="Przygotuj JSON przepływu pracy">
        Wyeksportuj lub utwórz plik JSON przepływu pracy ComfyUI. Zanotuj identyfikatory węzłów dla węzła wejścia promptu i węzła wyjściowego.
      </Step>
      <Step title="Skonfiguruj dostawcę">
        Ustaw `mode: "cloud"` i wskaż plik przepływu pracy:

        ```json5
        {
          models: {
            providers: {
              comfy: {
                mode: "cloud",
                image: {
                  workflowPath: "./workflows/flux-api.json",
                  promptNodeId: "6",
                  outputNodeId: "9",
                },
              },
            },
          },
        }
        ```

        <Tip>
        W trybie chmurowym `baseUrl` domyślnie ma wartość `https://cloud.comfy.org`. `baseUrl` trzeba ustawić tylko wtedy, gdy używasz niestandardowego endpointu chmurowego.
        </Tip>
      </Step>
      <Step title="Ustaw model domyślny">
        ```json5
        {
          agents: {
            defaults: {
              imageGenerationModel: {
                primary: "comfy/workflow",
              },
            },
          },
        }
        ```
      </Step>
      <Step title="Zweryfikuj">
        ```bash
        openclaw models list --provider comfy
        ```
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Konfiguracja

Comfy obsługuje wspólne ustawienia połączenia najwyższego poziomu oraz sekcje przepływów pracy per capability (`image`, `video`, `music`):

```json5
{
  models: {
    providers: {
      comfy: {
        mode: "local",
        baseUrl: "http://127.0.0.1:8188",
        image: {
          workflowPath: "./workflows/flux-api.json",
          promptNodeId: "6",
          outputNodeId: "9",
        },
        video: {
          workflowPath: "./workflows/video-api.json",
          promptNodeId: "12",
          outputNodeId: "21",
        },
        music: {
          workflowPath: "./workflows/music-api.json",
          promptNodeId: "3",
          outputNodeId: "18",
        },
      },
    },
  },
}
```

### Wspólne klucze

| Klucz                 | Typ                    | Opis                                                                                     |
| --------------------- | ---------------------- | ---------------------------------------------------------------------------------------- |
| `mode`                | `"local"` or `"cloud"` | Tryb połączenia.                                                                         |
| `baseUrl`             | string                 | Domyślnie `http://127.0.0.1:8188` dla trybu lokalnego albo `https://cloud.comfy.org` dla trybu chmurowego. |
| `apiKey`              | string                 | Opcjonalny klucz podany bezpośrednio, alternatywa dla zmiennych env `COMFY_API_KEY` / `COMFY_CLOUD_API_KEY`. |
| `allowPrivateNetwork` | boolean                | Zezwala na prywatny/LAN `baseUrl` w trybie chmurowym.                                    |

### Klucze per capability

Te klucze obowiązują wewnątrz sekcji `image`, `video` albo `music`:

| Klucz                        | Wymagane | Domyślnie | Opis                                                                         |
| ---------------------------- | -------- | --------- | ---------------------------------------------------------------------------- |
| `workflow` lub `workflowPath` | Tak     | --        | Ścieżka do pliku JSON przepływu pracy ComfyUI.                               |
| `promptNodeId`               | Tak      | --        | Identyfikator węzła odbierającego prompt tekstowy.                           |
| `promptInputName`            | Nie      | `"text"`  | Nazwa wejścia w węźle promptu.                                               |
| `outputNodeId`               | Nie      | --        | Identyfikator węzła, z którego należy odczytać dane wyjściowe. Jeśli zostanie pominięty, używane są wszystkie pasujące węzły wyjściowe. |
| `pollIntervalMs`             | Nie      | --        | Interwał odpytywania w milisekundach dla ukończenia zadania.                 |
| `timeoutMs`                  | Nie      | --        | Limit czasu w milisekundach dla uruchomienia przepływu pracy.                |

Sekcje `image` i `video` obsługują także:

| Klucz                 | Wymagane                              | Domyślnie | Opis                                                     |
| --------------------- | ------------------------------------- | --------- | -------------------------------------------------------- |
| `inputImageNodeId`    | Tak (przy przekazywaniu obrazu referencyjnego) | --   | Identyfikator węzła odbierającego przesłany obraz referencyjny. |
| `inputImageInputName` | Nie                                   | `"image"` | Nazwa wejścia w węźle obrazu.                            |

## Szczegóły przepływu pracy

<AccordionGroup>
  <Accordion title="Przepływy pracy obrazów">
    Ustaw domyślny model obrazu na `comfy/workflow`:

    ```json5
    {
      agents: {
        defaults: {
          imageGenerationModel: {
            primary: "comfy/workflow",
          },
        },
      },
    }
    ```

    **Przykład edycji z obrazem referencyjnym:**

    Aby włączyć edycję obrazów z użyciem przesłanego obrazu referencyjnego, dodaj `inputImageNodeId` do konfiguracji obrazu:

    ```json5
    {
      models: {
        providers: {
          comfy: {
            image: {
              workflowPath: "./workflows/edit-api.json",
              promptNodeId: "6",
              inputImageNodeId: "7",
              inputImageInputName: "image",
              outputNodeId: "9",
            },
          },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Przepływy pracy wideo">
    Ustaw domyślny model wideo na `comfy/workflow`:

    ```json5
    {
      agents: {
        defaults: {
          videoGenerationModel: {
            primary: "comfy/workflow",
          },
        },
      },
    }
    ```

    Przepływy pracy wideo Comfy obsługują text-to-video i image-to-video przez skonfigurowany graf.

    <Note>
    OpenClaw nie przekazuje wejściowych plików wideo do przepływów pracy Comfy. Jako dane wejściowe obsługiwane są tylko prompty tekstowe i pojedyncze obrazy referencyjne.
    </Note>

  </Accordion>

  <Accordion title="Przepływy pracy muzyki">
    Bundlowy Plugin rejestruje dostawcę generowania muzyki dla wyjść audio lub muzyki zdefiniowanych w przepływie pracy, udostępnianych przez wspólne narzędzie `music_generate`:

    ```text
    /tool music_generate prompt="Ciepła ambientowa pętla syntezatorowa z miękką fakturą taśmy"
    ```

    Użyj sekcji konfiguracji `music`, aby wskazać JSON przepływu pracy audio i węzeł wyjściowy.

  </Accordion>

  <Accordion title="Zgodność wsteczna">
    Istniejąca konfiguracja obrazu najwyższego poziomu (bez zagnieżdżonej sekcji `image`) nadal działa:

    ```json5
    {
      models: {
        providers: {
          comfy: {
            workflowPath: "./workflows/flux-api.json",
            promptNodeId: "6",
            outputNodeId: "9",
          },
        },
      },
    }
    ```

    OpenClaw traktuje ten starszy kształt jako konfigurację przepływu pracy obrazu. Nie musisz migrować od razu, ale dla nowych konfiguracji zalecane są zagnieżdżone sekcje `image` / `video` / `music`.

    <Tip>
    Jeśli używasz tylko generowania obrazów, starsza płaska konfiguracja i nowa zagnieżdżona sekcja `image` są funkcjonalnie równoważne.
    </Tip>

  </Accordion>

  <Accordion title="Testy live">
    Dla bundlowego Pluginu istnieje opcjonalne pokrycie live:

    ```bash
    OPENCLAW_LIVE_TEST=1 COMFY_LIVE_TEST=1 pnpm test:live -- extensions/comfy/comfy.live.test.ts
    ```

    Test live pomija poszczególne przypadki obrazów, wideo lub muzyki, chyba że skonfigurowana jest odpowiadająca im sekcja przepływu pracy Comfy.

  </Accordion>
</AccordionGroup>

## Powiązane

<CardGroup cols={2}>
  <Card title="Generowanie obrazów" href="/pl/tools/image-generation" icon="image">
    Konfiguracja i użycie narzędzia do generowania obrazów.
  </Card>
  <Card title="Generowanie wideo" href="/pl/tools/video-generation" icon="video">
    Konfiguracja i użycie narzędzia do generowania wideo.
  </Card>
  <Card title="Generowanie muzyki" href="/pl/tools/music-generation" icon="music">
    Konfiguracja generowania muzyki i audio.
  </Card>
  <Card title="Katalog dostawców" href="/pl/providers/index" icon="layers">
    Przegląd wszystkich dostawców i odwołań do modeli.
  </Card>
  <Card title="Informacje o konfiguracji" href="/pl/gateway/configuration-reference#agent-defaults" icon="gear">
    Pełne informacje o konfiguracji, w tym ustawienia domyślne agenta.
  </Card>
</CardGroup>
