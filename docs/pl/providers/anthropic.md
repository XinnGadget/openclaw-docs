---
read_when:
    - Chcesz używać modeli Anthropic w OpenClaw
summary: Używanie Anthropic Claude za pomocą kluczy API w OpenClaw
title: Anthropic
x-i18n:
    generated_at: "2026-04-06T03:10:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: bbc6c4938674aedf20ff944bc04e742c9a7e77a5ff10ae4f95b5718504c57c2d
    source_path: providers/anthropic.md
    workflow: 15
---

# Anthropic (Claude)

Anthropic tworzy rodzinę modeli **Claude** i udostępnia do nich dostęp przez API.
W OpenClaw nowe konfiguracje Anthropic powinny używać klucza API. Istniejące starsze
profile tokenów Anthropic są nadal honorowane w runtime, jeśli są już
skonfigurowane.

<Warning>
W przypadku Anthropic w OpenClaw podział rozliczeń wygląda następująco:

- **Klucz API Anthropic**: standardowe rozliczanie API Anthropic.
- **Uwierzytelnianie subskrypcją Claude wewnątrz OpenClaw**: Anthropic poinformował użytkowników OpenClaw
  **4 kwietnia 2026 o 12:00 PT / 20:00 BST**, że jest to traktowane jako
  użycie zewnętrznego harnessu i wymaga **Extra Usage** (pay-as-you-go,
  rozliczanego oddzielnie od subskrypcji).

Nasze lokalne reprodukcje potwierdzają ten podział:

- bezpośrednie `claude -p` może nadal działać
- `claude -p --append-system-prompt ...` może uruchomić blokadę Extra Usage, gdy
  prompt identyfikuje OpenClaw
- ten sam prompt systemowy podobny do OpenClaw **nie** odtwarza blokady na
  ścieżce Anthropic SDK + `ANTHROPIC_API_KEY`

Praktyczna zasada jest więc taka: **klucz API Anthropic albo subskrypcja Claude z
Extra Usage**. Jeśli chcesz wybrać najczytelniejszą ścieżkę produkcyjną, użyj klucza API Anthropic.

Aktualna publiczna dokumentacja Anthropic:

- [Claude Code CLI reference](https://code.claude.com/docs/en/cli-reference)
- [Claude Agent SDK overview](https://platform.claude.com/docs/en/agent-sdk/overview)

- [Using Claude Code with your Pro or Max plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
- [Using Claude Code with your Team or Enterprise plan](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/)

Jeśli chcesz mieć najjaśniejszą ścieżkę rozliczeń, zamiast tego użyj klucza API Anthropic.
OpenClaw obsługuje też inne opcje w stylu subskrypcji, w tym [OpenAI
Codex](/pl/providers/openai), [Qwen Cloud Coding Plan](/pl/providers/qwen),
[MiniMax Coding Plan](/pl/providers/minimax) oraz [Z.AI / GLM Coding
Plan](/pl/providers/glm).
</Warning>

## Opcja A: klucz API Anthropic

**Najlepsze dla:** standardowego dostępu do API i rozliczeń zależnych od użycia.
Utwórz klucz API w Anthropic Console.

### Konfiguracja CLI

```bash
openclaw onboard
# choose: Anthropic API key

# or non-interactive
openclaw onboard --anthropic-api-key "$ANTHROPIC_API_KEY"
```

### Fragment konfiguracji Anthropic

```json5
{
  env: { ANTHROPIC_API_KEY: "sk-ant-..." },
  agents: { defaults: { model: { primary: "anthropic/claude-opus-4-6" } } },
}
```

## Domyślne ustawienia myślenia (Claude 4.6)

- Modele Anthropic Claude 4.6 domyślnie używają myślenia `adaptive` w OpenClaw, gdy nie ustawiono jawnie poziomu myślenia.
- Możesz to nadpisać dla pojedynczej wiadomości (`/think:<level>`) albo w parametrach modelu:
  `agents.defaults.models["anthropic/<model>"].params.thinking`.
- Powiązana dokumentacja Anthropic:
  - [Adaptive thinking](https://platform.claude.com/docs/en/build-with-claude/adaptive-thinking)
  - [Extended thinking](https://platform.claude.com/docs/en/build-with-claude/extended-thinking)

## Tryb szybki (Anthropic API)

Współdzielony przełącznik `/fast` w OpenClaw obsługuje też bezpośredni publiczny ruch Anthropic, w tym żądania uwierzytelniane kluczem API i OAuth wysyłane do `api.anthropic.com`.

- `/fast on` jest mapowane na `service_tier: "auto"`
- `/fast off` jest mapowane na `service_tier: "standard_only"`
- Domyślna konfiguracja:

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-sonnet-4-6": {
          params: { fastMode: true },
        },
      },
    },
  },
}
```

Ważne ograniczenia:

- OpenClaw wstrzykuje poziomy usług Anthropic tylko dla bezpośrednich żądań do `api.anthropic.com`. Jeśli kierujesz `anthropic/*` przez proxy lub gateway, `/fast` pozostawia `service_tier` bez zmian.
- Jawne parametry modelu Anthropic `serviceTier` lub `service_tier` mają pierwszeństwo przed domyślnym ustawieniem `/fast`, gdy ustawione są oba.
- Anthropic raportuje efektywny poziom w odpowiedzi pod `usage.service_tier`. Na kontach bez pojemności Priority Tier `service_tier: "auto"` może nadal zostać rozstrzygnięte jako `standard`.

## Cache promptów (Anthropic API)

OpenClaw obsługuje funkcję cache promptów Anthropic. Jest to funkcja **tylko dla API**; starsze uwierzytelnianie tokenami Anthropic nie respektuje ustawień cache.

### Konfiguracja

Użyj parametru `cacheRetention` w konfiguracji modelu:

| Wartość   | Czas trwania cache | Opis              |
| ------- | -------------- | ------------------------ |
| `none`  | Brak cache     | Wyłącz cache promptów   |
| `short` | 5 minut      | Domyślne dla uwierzytelniania kluczem API |
| `long`  | 1 godzina         | Rozszerzony cache           |

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" },
        },
      },
    },
  },
}
```

### Wartości domyślne

Gdy używasz uwierzytelniania kluczem API Anthropic, OpenClaw automatycznie stosuje `cacheRetention: "short"` (5-minutowy cache) dla wszystkich modeli Anthropic. Możesz to nadpisać, jawnie ustawiając `cacheRetention` w konfiguracji.

### Nadpisania `cacheRetention` per-agent

Używaj parametrów na poziomie modelu jako ustawienia bazowego, a następnie nadpisuj konkretne agenty przez `agents.list[].params`.

```json5
{
  agents: {
    defaults: {
      model: { primary: "anthropic/claude-opus-4-6" },
      models: {
        "anthropic/claude-opus-4-6": {
          params: { cacheRetention: "long" }, // baseline for most agents
        },
      },
    },
    list: [
      { id: "research", default: true },
      { id: "alerts", params: { cacheRetention: "none" } }, // override for this agent only
    ],
  },
}
```

Kolejność scalania konfiguracji dla parametrów związanych z cache:

1. `agents.defaults.models["provider/model"].params`
2. `agents.list[].params` (pasujące `id`, nadpisanie według klucza)

Pozwala to jednemu agentowi utrzymywać długotrwały cache, podczas gdy inny agent na tym samym modelu wyłącza cache, aby uniknąć kosztów zapisu przy skokowym ruchu o niskim ponownym użyciu.

### Uwagi o Bedrock Claude

- Modele Anthropic Claude na Bedrock (`amazon-bedrock/*anthropic.claude*`) akceptują przekazywanie `cacheRetention`, jeśli jest skonfigurowane.
- Modele Bedrock inne niż Anthropic są w runtime wymuszane do `cacheRetention: "none"`.
- Inteligentne wartości domyślne dla klucza API Anthropic ustawiają także `cacheRetention: "short"` dla odwołań do modeli Claude-on-Bedrock, gdy nie ustawiono jawnej wartości.

## Okno kontekstu 1M (beta Anthropic)

Okno kontekstu 1M Anthropic jest objęte bramką beta. W OpenClaw włączysz je dla modelu
przez `params.context1m: true` dla obsługiwanych modeli Opus/Sonnet.

```json5
{
  agents: {
    defaults: {
      models: {
        "anthropic/claude-opus-4-6": {
          params: { context1m: true },
        },
      },
    },
  },
}
```

OpenClaw mapuje to na `anthropic-beta: context-1m-2025-08-07` w żądaniach Anthropic.

Jest to aktywowane tylko wtedy, gdy `params.context1m` jest jawnie ustawione na `true` dla
danego modelu.

Wymaganie: Anthropic musi zezwalać na użycie długiego kontekstu dla tego poświadczenia
(zwykle rozliczanie kluczem API albo ścieżka logowania Claude w OpenClaw / starsze uwierzytelnianie tokenami
z włączonym Extra Usage). W przeciwnym razie Anthropic zwraca:
`HTTP 429: rate_limit_error: Extra usage is required for long context requests`.

Uwaga: Anthropic obecnie odrzuca żądania beta `context-1m-*` przy użyciu
starszego uwierzytelniania tokenami Anthropic (`sk-ant-oat-*`). Jeśli skonfigurujesz
`context1m: true` z tym starszym trybem auth, OpenClaw zapisze ostrzeżenie i
powróci do standardowego okna kontekstu, pomijając nagłówek beta context1m
przy jednoczesnym zachowaniu wymaganych bet OAuth.

## Usunięte: backend Claude CLI

Wbudowany backend Anthropic `claude-cli` został usunięty.

- Powiadomienie Anthropic z 4 kwietnia 2026 mówi, że ruch logowania Claude inicjowany przez OpenClaw jest
  użyciem zewnętrznego harnessu i wymaga **Extra Usage**.
- Nasze lokalne reprodukcje pokazują też, że bezpośrednie
  `claude -p --append-system-prompt ...` może uruchamiać tę samą blokadę, gdy
  dołączony prompt identyfikuje OpenClaw.
- Ten sam prompt podobny do OpenClaw nie uruchamia tej blokady na
  ścieżce Anthropic SDK + `ANTHROPIC_API_KEY`.
- Używaj kluczy API Anthropic dla ruchu Anthropic w OpenClaw.

## Uwagi

- Publiczna dokumentacja Claude Code Anthropic nadal opisuje bezpośrednie użycie CLI, takie jak
  `claude -p`, ale oddzielne powiadomienie Anthropic dla użytkowników OpenClaw mówi, że
  ścieżka logowania Claude przez **OpenClaw** jest użyciem zewnętrznego harnessu i wymaga
  **Extra Usage** (pay-as-you-go rozliczanego oddzielnie od subskrypcji).
  Nasze lokalne reprodukcje pokazują też, że bezpośrednie
  `claude -p --append-system-prompt ...` może uruchamiać tę samą blokadę, gdy
  dołączony prompt identyfikuje OpenClaw, podczas gdy ten sam kształt promptu nie
  odtwarza się na ścieżce Anthropic SDK + `ANTHROPIC_API_KEY`. W środowisku produkcyjnym
  zalecamy zamiast tego klucze API Anthropic.
- Anthropic setup-token jest ponownie dostępny w OpenClaw jako starsza/ręczna ścieżka. Powiadomienie Anthropic o rozliczeniach specyficznych dla OpenClaw nadal obowiązuje, więc używaj jej z założeniem, że Anthropic wymaga **Extra Usage** dla tej ścieżki.
- Szczegóły auth i zasady ponownego użycia znajdują się w [/concepts/oauth](/pl/concepts/oauth).

## Rozwiązywanie problemów

**Błędy 401 / token nagle nieprawidłowy**

- Starsze uwierzytelnianie tokenami Anthropic może wygasnąć lub zostać odwołane.
- W nowych konfiguracjach przejdź na klucz API Anthropic.

**Nie znaleziono klucza API dla dostawcy "anthropic"**

- Auth jest **per agent**. Nowi agenci nie dziedziczą kluczy głównego agenta.
- Ponownie uruchom onboarding dla tego agenta albo skonfiguruj klucz API na hoście
  gateway, a następnie zweryfikuj przez `openclaw models status`.

**Nie znaleziono poświadczeń dla profilu `anthropic:default`**

- Uruchom `openclaw models status`, aby zobaczyć, który profil auth jest aktywny.
- Ponownie uruchom onboarding albo skonfiguruj klucz API dla ścieżki tego profilu.

**Brak dostępnego profilu auth (wszystkie w cooldown/unavailable)**

- Sprawdź `openclaw models status --json` pod kątem `auth.unusableProfiles`.
- Cooldowny limitów Anthropic mogą być przypisane do konkretnego modelu, więc pokrewny model Anthropic
  może nadal nadawać się do użycia, nawet gdy bieżący jest w cooldownie.
- Dodaj kolejny profil Anthropic albo poczekaj na zakończenie cooldownu.

Więcej: [/gateway/troubleshooting](/pl/gateway/troubleshooting) i [/help/faq](/pl/help/faq).
