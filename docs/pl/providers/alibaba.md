---
read_when:
    - Chcesz używać generowania wideo Alibaba Wan w OpenClaw
    - Potrzebujesz konfiguracji klucza API Model Studio lub DashScope do generowania wideo
summary: Generowanie wideo Wan w Alibaba Model Studio w OpenClaw
title: Alibaba Model Studio
x-i18n:
    generated_at: "2026-04-06T03:10:18Z"
    model: gpt-5.4
    provider: openai
    source_hash: 97a1eddc7cbd816776b9368f2a926b5ef9ee543f08d151a490023736f67dc635
    source_path: providers/alibaba.md
    workflow: 15
---

# Alibaba Model Studio

OpenClaw dostarcza wbudowanego dostawcę generowania wideo `alibaba` dla modeli Wan w
Alibaba Model Studio / DashScope.

- Dostawca: `alibaba`
- Preferowane uwierzytelnianie: `MODELSTUDIO_API_KEY`
- Akceptowane również: `DASHSCOPE_API_KEY`, `QWEN_API_KEY`
- API: asynchroniczne generowanie wideo DashScope / Model Studio

## Szybki start

1. Ustaw klucz API:

```bash
openclaw onboard --auth-choice qwen-standard-api-key
```

2. Ustaw domyślny model wideo:

```json5
{
  agents: {
    defaults: {
      videoGenerationModel: {
        primary: "alibaba/wan2.6-t2v",
      },
    },
  },
}
```

## Wbudowane modele Wan

Wbudowany dostawca `alibaba` rejestruje obecnie:

- `alibaba/wan2.6-t2v`
- `alibaba/wan2.6-i2v`
- `alibaba/wan2.6-r2v`
- `alibaba/wan2.6-r2v-flash`
- `alibaba/wan2.7-r2v`

## Bieżące limity

- Maksymalnie **1** wyjściowe wideo na żądanie
- Maksymalnie **1** obraz wejściowy
- Maksymalnie **4** wejściowe pliki wideo
- Maksymalnie **10 sekund** długości
- Obsługuje `size`, `aspectRatio`, `resolution`, `audio` i `watermark`
- Tryb obrazu/wideo referencyjnego wymaga obecnie **zdalnych adresów URL http(s)**

## Relacja z Qwen

Wbudowany dostawca `qwen` również używa hostowanych przez Alibaba endpointów DashScope do
generowania wideo Wan. Użyj:

- `qwen/...`, gdy chcesz używać kanonicznej powierzchni dostawcy Qwen
- `alibaba/...`, gdy chcesz używać bezpośredniej, należącej do dostawcy powierzchni wideo Wan

## Powiązane

- [Generowanie wideo](/tools/video-generation)
- [Qwen](/pl/providers/qwen)
- [Dokumentacja konfiguracji](/pl/gateway/configuration-reference#agent-defaults)
