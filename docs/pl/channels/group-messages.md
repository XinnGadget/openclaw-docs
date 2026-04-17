---
read_when:
    - Zmiana reguł wiadomości grupowych lub wzmianek
summary: Zachowanie i konfiguracja obsługi wiadomości grupowych w WhatsApp (`mentionPatterns` są współdzielone między interfejsami)
title: Wiadomości grupowe
x-i18n:
    generated_at: "2026-04-12T23:28:02Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5d9484dd1de74d42f8dce4c3ac80d60c24864df30a7802e64893ef55506230fe
    source_path: channels/group-messages.md
    workflow: 15
---

# Wiadomości grupowe (kanał internetowy WhatsApp)

Cel: pozwolić Clawd działać w grupach WhatsApp, wybudzać się tylko po wywołaniu i utrzymywać ten wątek oddzielnie od osobistej sesji DM.

Uwaga: `agents.list[].groupChat.mentionPatterns` jest teraz używane również przez Telegram/Discord/Slack/iMessage; ten dokument koncentruje się na zachowaniu specyficznym dla WhatsApp. W konfiguracjach z wieloma agentami ustaw `agents.list[].groupChat.mentionPatterns` dla każdego agenta (lub użyj `messages.groupChat.mentionPatterns` jako globalnego ustawienia zapasowego).

## Bieżąca implementacja (2025-12-03)

- Tryby aktywacji: `mention` (domyślnie) lub `always`. `mention` wymaga wywołania (rzeczywiste wzmianki WhatsApp @ przez `mentionedJids`, bezpieczne wzorce regex lub numer E.164 bota w dowolnym miejscu tekstu). `always` wybudza agenta przy każdej wiadomości, ale powinien on odpowiadać tylko wtedy, gdy może wnieść istotną wartość; w przeciwnym razie zwraca dokładny cichy token `NO_REPLY` / `no_reply`. Ustawienia domyślne można skonfigurować w konfiguracji (`channels.whatsapp.groups`) i nadpisać dla każdej grupy przez `/activation`. Gdy ustawione jest `channels.whatsapp.groups`, działa ono również jako lista dozwolonych grup (uwzględnij `"*"` aby zezwolić na wszystkie).
- Zasada dla grup: `channels.whatsapp.groupPolicy` kontroluje, czy wiadomości grupowe są akceptowane (`open|disabled|allowlist`). `allowlist` używa `channels.whatsapp.groupAllowFrom` (ustawienie zapasowe: jawne `channels.whatsapp.allowFrom`). Domyślna wartość to `allowlist` (blokowane, dopóki nie dodasz nadawców).
- Sesje per grupa: klucze sesji mają postać `agent:<agentId>:whatsapp:group:<jid>`, więc polecenia takie jak `/verbose on`, `/trace on` lub `/think high` (wysyłane jako samodzielne wiadomości) są ograniczone do tej grupy; stan osobistego DM pozostaje nienaruszony. Heartbeat jest pomijany dla wątków grupowych.
- Wstrzykiwanie kontekstu: **tylko oczekujące** wiadomości grupowe (domyślnie 50), które _nie_ uruchomiły wykonania, są poprzedzane sekcją `[Chat messages since your last reply - for context]`, a linia wyzwalająca znajduje się pod `[Current message - respond to this]`. Wiadomości już obecne w sesji nie są wstrzykiwane ponownie.
- Ujawnianie nadawcy: każda partia grupowa kończy się teraz znacznikiem `[from: Sender Name (+E164)]`, aby Pi wiedział, kto mówi.
- Ephemeral/view-once: rozpakowujemy je przed wyodrębnieniem tekstu/wzmianek, więc wywołania w ich treści nadal uruchamiają działanie.
- Prompt systemowy grupy: przy pierwszej turze sesji grupowej (oraz zawsze, gdy `/activation` zmienia tryb) wstrzykujemy krótki opis do promptu systemowego, np. `You are replying inside the WhatsApp group "<subject>". Group members: Alice (+44...), Bob (+43...), … Activation: trigger-only … Address the specific sender noted in the message context.` Jeśli metadane nie są dostępne, nadal informujemy agenta, że jest to czat grupowy.

## Przykład konfiguracji (WhatsApp)

Dodaj blok `groupChat` do `~/.openclaw/openclaw.json`, aby wzmianki po nazwie wyświetlanej działały nawet wtedy, gdy WhatsApp usuwa wizualne `@` z treści tekstu:

```json5
{
  channels: {
    whatsapp: {
      groups: {
        "*": { requireMention: true },
      },
    },
  },
  agents: {
    list: [
      {
        id: "main",
        groupChat: {
          historyLimit: 50,
          mentionPatterns: ["@?openclaw", "\\+?15555550123"],
        },
      },
    ],
  },
}
```

Uwagi:

- Regexy nie rozróżniają wielkości liter i używają tych samych zabezpieczeń safe-regex co inne powierzchnie regex w konfiguracji; nieprawidłowe wzorce i niebezpieczne zagnieżdżone powtórzenia są ignorowane.
- WhatsApp nadal wysyła kanoniczne wzmianki przez `mentionedJids`, gdy ktoś kliknie kontakt, więc zapasowe dopasowanie po numerze jest rzadko potrzebne, ale stanowi przydatne zabezpieczenie.

### Polecenie aktywacji (tylko właściciel)

Użyj polecenia czatu grupowego:

- `/activation mention`
- `/activation always`

Tylko numer właściciela (z `channels.whatsapp.allowFrom` lub własny numer E.164 bota, jeśli nie jest ustawiony) może to zmienić. Wyślij `/status` jako samodzielną wiadomość w grupie, aby zobaczyć bieżący tryb aktywacji.

## Jak używać

1. Dodaj swoje konto WhatsApp (to, na którym działa OpenClaw) do grupy.
2. Napisz `@openclaw …` (lub podaj numer). Tylko nadawcy z listy dozwolonych mogą to uruchomić, chyba że ustawisz `groupPolicy: "open"`.
3. Prompt agenta będzie zawierał ostatni kontekst grupy oraz końcowy znacznik `[from: …]`, dzięki czemu będzie mógł zwrócić się do właściwej osoby.
4. Dyrektywy na poziomie sesji (`/verbose on`, `/trace on`, `/think high`, `/new` lub `/reset`, `/compact`) dotyczą wyłącznie sesji tej grupy; wysyłaj je jako samodzielne wiadomości, aby zostały zarejestrowane. Twoja osobista sesja DM pozostaje niezależna.

## Testowanie / weryfikacja

- Ręczny smoke test:
  - Wyślij wywołanie `@openclaw` w grupie i potwierdź odpowiedź, która odnosi się do nazwy nadawcy.
  - Wyślij drugie wywołanie i sprawdź, czy blok historii został dołączony, a następnie wyczyszczony przy kolejnej turze.
- Sprawdź logi Gateway (uruchomione z `--verbose`), aby zobaczyć wpisy `inbound web message` pokazujące `from: <groupJid>` oraz sufiks `[from: …]`.

## Znane kwestie

- Heartbeat jest celowo pomijany dla grup, aby uniknąć głośnych rozgłoszeń.
- Tłumienie echa używa połączonego ciągu partii; jeśli wyślesz ten sam tekst dwa razy bez wzmianek, odpowiedź zostanie wygenerowana tylko za pierwszym razem.
- Wpisy magazynu sesji będą widoczne jako `agent:<agentId>:whatsapp:group:<jid>` w magazynie sesji (domyślnie `~/.openclaw/agents/<agentId>/sessions/sessions.json`); brak wpisu oznacza tylko, że grupa nie uruchomiła jeszcze wykonania.
- Wskaźniki pisania w grupach są zgodne z `agents.defaults.typingMode` (domyślnie: `message`, gdy nie ma wzmianki).
