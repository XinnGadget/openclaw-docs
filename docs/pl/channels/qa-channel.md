---
read_when:
    - Integrujesz syntetyczny transport QA z lokalnym uruchomieniem testowym lub uruchomieniem testowym w CI
    - Potrzebujesz powierzchni konfiguracji dołączonego qa-channel
    - Pracujesz iteracyjnie nad kompleksową automatyzacją QA
summary: Syntetyczna wtyczka kanału klasy Slack do deterministycznych scenariuszy QA OpenClaw
title: Kanał QA
x-i18n:
    generated_at: "2026-04-06T03:05:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3b88cd73df2f61b34ad1eb83c3450f8fe15a51ac69fbb5a9eca0097564d67a06
    source_path: channels/qa-channel.md
    workflow: 15
---

# Kanał QA

`qa-channel` to dołączony syntetyczny transport wiadomości do zautomatyzowanego QA OpenClaw.

Nie jest to kanał produkcyjny. Istnieje po to, aby testować tę samą granicę wtyczki kanału, której używają rzeczywiste transporty, przy jednoczesnym zachowaniu deterministycznego i w pełni kontrolowalnego stanu.

## Co robi obecnie

- Gramatyka celu klasy Slack:
  - `dm:<user>`
  - `channel:<room>`
  - `thread:<room>/<thread>`
- Syntetyczna magistrala oparta na HTTP do:
  - wstrzykiwania wiadomości przychodzących
  - przechwytywania transkryptu wiadomości wychodzących
  - tworzenia wątków
  - reakcji
  - edycji
  - usuwania
  - działań wyszukiwania i odczytu
- Dołączony uruchamiacz samokontroli po stronie hosta, który zapisuje raport w Markdown

## Konfiguracja

```json
{
  "channels": {
    "qa-channel": {
      "baseUrl": "http://127.0.0.1:43123",
      "botUserId": "openclaw",
      "botDisplayName": "OpenClaw QA",
      "allowFrom": ["*"],
      "pollTimeoutMs": 1000
    }
  }
}
```

Obsługiwane klucze konta:

- `baseUrl`
- `botUserId`
- `botDisplayName`
- `pollTimeoutMs`
- `allowFrom`
- `defaultTo`
- `actions.messages`
- `actions.reactions`
- `actions.search`
- `actions.threads`

## Uruchamiacz

Obecny pionowy wycinek:

```bash
pnpm qa:e2e
```

Teraz jest to kierowane przez dołączone rozszerzenie `qa-lab`. Uruchamia ono znajdującą się w repozytorium magistralę QA, startuje dołączony wycinek środowiska uruchomieniowego `qa-channel`, wykonuje deterministyczną samokontrolę i zapisuje raport w Markdown w katalogu `.artifacts/qa-e2e/`.

Prywatny interfejs debuggera:

```bash
pnpm qa:lab:build
pnpm openclaw qa ui
```

Pełny zestaw QA oparty na repozytorium:

```bash
pnpm openclaw qa suite
```

Uruchamia to prywatny debugger QA pod lokalnym adresem URL, oddzielnie od dostarczanego pakietu Control UI.

## Zakres

Obecny zakres jest celowo wąski:

- magistrala + transport wtyczki
- gramatyka routingu wątkowego
- działania na wiadomościach należące do kanału
- raportowanie w Markdown

Dalsze prace dodadzą:

- orkiestrację OpenClaw w Dockerze
- wykonywanie macierzy dostawca/model
- bogatsze wykrywanie scenariuszy
- później natywną dla OpenClaw orkiestrację
