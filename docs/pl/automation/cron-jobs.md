---
read_when:
    - Planowanie zadań w tle lub wybudzeń
    - Podłączanie zewnętrznych wyzwalaczy (webhooków, Gmaila) do OpenClaw
    - Wybór między Heartbeat a Cron dla zaplanowanych zadań
summary: Zaplanowane zadania, webhooki i wyzwalacze Gmail PubSub dla harmonogramu Gateway
title: Zaplanowane zadania
x-i18n:
    generated_at: "2026-04-12T09:33:31Z"
    model: gpt-5.4
    provider: openai
    source_hash: f42bcaeedd0595d025728d7f236a724a0ebc67b6813c57233f4d739b3088317f
    source_path: automation/cron-jobs.md
    workflow: 15
---

# Zaplanowane zadania (Cron)

Cron to wbudowany harmonogram Gateway. Utrwala zadania, wybudza agenta we właściwym czasie i może dostarczać wyniki z powrotem do kanału czatu lub punktu końcowego Webhook.

## Szybki start

```bash
# Add a one-shot reminder
openclaw cron add \
  --name "Reminder" \
  --at "2026-02-01T16:00:00Z" \
  --session main \
  --system-event "Reminder: check the cron docs draft" \
  --wake now \
  --delete-after-run

# Check your jobs
openclaw cron list

# See run history
openclaw cron runs --id <job-id>
```

## Jak działa cron

- Cron działa **wewnątrz procesu Gateway** (nie wewnątrz modelu).
- Zadania są przechowywane w `~/.openclaw/cron/jobs.json`, więc restarty nie powodują utraty harmonogramów.
- Wszystkie wykonania cron tworzą rekordy [zadań w tle](/pl/automation/tasks).
- Zadania jednorazowe (`--at`) domyślnie usuwają się automatycznie po powodzeniu.
- Izolowane uruchomienia cron po zakończeniu działania podejmują próbę zamknięcia śledzonych kart/procesów przeglądarki dla swojej sesji `cron:<jobId>`, aby odłączona automatyzacja przeglądarki nie pozostawiała osieroconych procesów.
- Izolowane uruchomienia cron chronią też przed nieaktualnymi odpowiedziami potwierdzającymi. Jeśli
  pierwszy wynik jest tylko tymczasową aktualizacją statusu (`on it`, `pulling everything
together` i podobne wskazówki), a żadne podrzędne uruchomienie subagenta nie jest już
  odpowiedzialne za końcową odpowiedź, OpenClaw ponownie wysyła monit raz, aby uzyskać właściwy
  wynik przed dostarczeniem.

<a id="maintenance"></a>

Uzgadnianie zadań dla cron jest zarządzane przez środowisko uruchomieniowe: aktywne zadanie cron pozostaje aktywne, dopóki
środowisko wykonawcze cron nadal śledzi to zadanie jako uruchomione, nawet jeśli nadal istnieje stary wiersz sesji podrzędnej.
Gdy środowisko przestaje zarządzać zadaniem i upłynie 5-minutowe okno karencji, konserwacja może
oznaczyć zadanie jako `lost`.

## Typy harmonogramów

| Rodzaj  | Flaga CLI | Opis                                                      |
| ------- | --------- | --------------------------------------------------------- |
| `at`    | `--at`    | Jednorazowy znacznik czasu (ISO 8601 lub względny, np. `20m`) |
| `every` | `--every` | Stały interwał                                            |
| `cron`  | `--cron`  | 5-polowe lub 6-polowe wyrażenie cron z opcjonalnym `--tz` |

Znaczniki czasu bez strefy czasowej są traktowane jako UTC. Dodaj `--tz America/New_York`, aby użyć lokalnego harmonogramu według czasu ściennego.

Powtarzające się wyrażenia uruchamiane na początku godziny są automatycznie rozkładane do 5 minut, aby ograniczyć skoki obciążenia. Użyj `--exact`, aby wymusić precyzyjny czas, lub `--stagger 30s`, aby ustawić jawne okno.

### Dzień miesiąca i dzień tygodnia używają logiki OR

Wyrażenia Cron są parsowane przez [croner](https://github.com/Hexagon/croner). Gdy zarówno pola dnia miesiąca, jak i dnia tygodnia nie są symbolami wieloznacznymi, croner dopasowuje, gdy **którekolwiek** z pól pasuje — nie oba. To standardowe zachowanie Vixie cron.

```
# Intended: "9 AM on the 15th, only if it's a Monday"
# Actual:   "9 AM on every 15th, AND 9 AM on every Monday"
0 9 15 * 1
```

To uruchamia się około 5–6 razy w miesiącu zamiast 0–1 razy w miesiącu. OpenClaw używa tutaj domyślnego zachowania OR w Cronerze. Aby wymagać obu warunków, użyj modyfikatora dnia tygodnia `+` w Cronerze (`0 9 15 * +1`) albo ustaw harmonogram dla jednego pola i sprawdzaj drugie w monicie lub poleceniu zadania.

## Style wykonywania

| Styl            | Wartość `--session` | Uruchamiane w             | Najlepsze do                    |
| --------------- | ------------------- | ------------------------- | ------------------------------- |
| Sesja główna    | `main`              | Następna tura Heartbeat   | Przypomnienia, zdarzenia systemowe |
| Izolowane       | `isolated`          | Dedykowane `cron:<jobId>` | Raporty, zadania w tle          |
| Bieżąca sesja   | `current`           | Powiązane przy tworzeniu  | Cykliczna praca zależna od kontekstu |
| Sesja niestandardowa | `session:custom-id` | Trwała nazwana sesja   | Przepływy pracy budowane na historii |

Zadania **sesji głównej** umieszczają zdarzenie systemowe w kolejce i opcjonalnie wybudzają Heartbeat (`--wake now` lub `--wake next-heartbeat`). Zadania **izolowane** uruchamiają dedykowaną turę agenta ze świeżą sesją. **Sesje niestandardowe** (`session:xxx`) zachowują kontekst między uruchomieniami, umożliwiając przepływy pracy, takie jak codzienne stand-upy, które bazują na wcześniejszych podsumowaniach.

Dla zadań izolowanych zamykanie środowiska uruchomieniowego obejmuje teraz próbę oczyszczenia przeglądarki dla tej sesji cron. Błędy czyszczenia są ignorowane, aby rzeczywisty wynik cron nadal miał pierwszeństwo.

Gdy izolowane uruchomienia cron orkiestrują subagentów, dostarczanie preferuje też końcowy
wynik potomny zamiast nieaktualnego tymczasowego tekstu nadrzędnego. Jeśli potomkowie nadal
działają, OpenClaw pomija tę częściową aktualizację nadrzędną zamiast ją ogłaszać.

### Opcje ładunku dla zadań izolowanych

- `--message`: tekst monitu (wymagany dla izolowanych)
- `--model` / `--thinking`: nadpisania modelu i poziomu myślenia
- `--light-context`: pomiń wstrzykiwanie plików bootstrap obszaru roboczego
- `--tools exec,read`: ogranicz, których narzędzi zadanie może używać

`--model` używa wybranego dozwolonego modelu dla tego zadania. Jeśli żądany model
nie jest dozwolony, cron zapisuje ostrzeżenie i wraca do wyboru modelu agenta/domyślnego dla tego zadania.
Skonfigurowane łańcuchy zapasowe nadal mają zastosowanie, ale zwykłe nadpisanie
modelu bez jawnej listy zapasowej dla zadania nie dopisuje już głównego modelu agenta jako ukrytego dodatkowego celu ponowienia.

Kolejność pierwszeństwa wyboru modelu dla zadań izolowanych jest następująca:

1. Nadpisanie modelu przez hook Gmaila (gdy uruchomienie pochodzi z Gmaila i to nadpisanie jest dozwolone)
2. `model` w ładunku per zadanie
3. Zapisane nadpisanie modelu sesji cron
4. Domyślny wybór modelu agenta

Tryb szybki również podąża za rozstrzygniętym wyborem live. Jeśli konfiguracja wybranego modelu
ma `params.fastMode`, izolowany cron domyślnie używa tej wartości. Zapisane nadpisanie
`fastMode` dla sesji nadal ma pierwszeństwo nad konfiguracją w obie strony.

Jeśli izolowane uruchomienie napotka live handoff przełączenia modelu, cron ponawia próbę z
przełączonym dostawcą/modelem i utrwala ten wybór live przed ponowieniem. Gdy przełączenie
obejmuje też nowy profil uwierzytelniania, cron utrwala również nadpisanie tego profilu uwierzytelniania.
Liczba ponowień jest ograniczona: po początkowej próbie oraz 2 ponowieniach po przełączeniu
cron przerywa zamiast zapętlać się w nieskończoność.

## Dostarczanie i wyniki

| Tryb      | Co się dzieje                                           |
| --------- | ------------------------------------------------------- |
| `announce` | Dostarcza podsumowanie do kanału docelowego (domyślnie dla izolowanych) |
| `webhook`  | Wysyła ładunek zdarzenia zakończenia metodą POST pod adres URL |
| `none`     | Tylko wewnętrznie, bez dostarczania                     |

Użyj `--announce --channel telegram --to "-1001234567890"` do dostarczania do kanału. Dla tematów forum Telegram użyj `-1001234567890:topic:123`. Cele Slack/Discord/Mattermost powinny używać jawnych prefiksów (`channel:<id>`, `user:<id>`).

W przypadku izolowanych zadań zarządzanych przez cron ścieżka końcowego dostarczenia należy do wykonawcy.
Agent otrzymuje monit o zwrócenie podsumowania w postaci zwykłego tekstu, a następnie to podsumowanie jest wysyłane przez
`announce`, `webhook` albo pozostaje wewnętrzne dla `none`. `--no-deliver` nie oddaje dostarczania z powrotem agentowi;
utrzymuje uruchomienie jako wewnętrzne.

Jeśli oryginalne zadanie wyraźnie mówi o wysłaniu wiadomości do jakiegoś zewnętrznego odbiorcy,
agent powinien wskazać w swoim wyniku, do kogo/gdzie ta wiadomość powinna trafić, zamiast próbować wysłać ją bezpośrednio.

Powiadomienia o błędach korzystają z osobnej ścieżki docelowej:

- `cron.failureDestination` ustawia globalny domyślny cel dla powiadomień o błędach.
- `job.delivery.failureDestination` nadpisuje go dla konkretnego zadania.
- Jeśli żaden z nich nie jest ustawiony, a zadanie już dostarcza przez `announce`, powiadomienia o błędach wracają teraz domyślnie do tego głównego celu ogłoszenia.
- `delivery.failureDestination` jest obsługiwane tylko dla zadań z `sessionTarget="isolated"`, chyba że głównym trybem dostarczania jest `webhook`.

## Przykłady CLI

Jednorazowe przypomnienie (sesja główna):

```bash
openclaw cron add \
  --name "Calendar check" \
  --at "20m" \
  --session main \
  --system-event "Next heartbeat: check calendar." \
  --wake now
```

Powtarzające się zadanie izolowane z dostarczaniem:

```bash
openclaw cron add \
  --name "Morning brief" \
  --cron "0 7 * * *" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Summarize overnight updates." \
  --announce \
  --channel slack \
  --to "channel:C1234567890"
```

Zadanie izolowane z nadpisaniem modelu i poziomu myślenia:

```bash
openclaw cron add \
  --name "Deep analysis" \
  --cron "0 6 * * 1" \
  --tz "America/Los_Angeles" \
  --session isolated \
  --message "Weekly deep analysis of project progress." \
  --model "opus" \
  --thinking high \
  --announce
```

## Webhooki

Gateway może udostępniać punkty końcowe HTTP Webhook dla zewnętrznych wyzwalaczy. Włącz w konfiguracji:

```json5
{
  hooks: {
    enabled: true,
    token: "shared-secret",
    path: "/hooks",
  },
}
```

### Uwierzytelnianie

Każde żądanie musi zawierać token hooka w nagłówku:

- `Authorization: Bearer <token>` (zalecane)
- `x-openclaw-token: <token>`

Tokeny w ciągu zapytania są odrzucane.

### POST /hooks/wake

Umieszcza zdarzenie systemowe w kolejce dla sesji głównej:

```bash
curl -X POST http://127.0.0.1:18789/hooks/wake \
  -H 'Authorization: Bearer SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"text":"New email received","mode":"now"}'
```

- `text` (wymagane): opis zdarzenia
- `mode` (opcjonalne): `now` (domyślnie) lub `next-heartbeat`

### POST /hooks/agent

Uruchamia izolowaną turę agenta:

```bash
curl -X POST http://127.0.0.1:18789/hooks/agent \
  -H 'Authorization: Bearer SECRET' \
  -H 'Content-Type: application/json' \
  -d '{"message":"Summarize inbox","name":"Email","model":"openai/gpt-5.4-mini"}'
```

Pola: `message` (wymagane), `name`, `agentId`, `wakeMode`, `deliver`, `channel`, `to`, `model`, `thinking`, `timeoutSeconds`.

### Mapowane hooki (POST /hooks/\<name\>)

Niestandardowe nazwy hooków są rozwiązywane przez `hooks.mappings` w konfiguracji. Mapowania mogą przekształcać dowolne ładunki w działania `wake` lub `agent` za pomocą szablonów albo transformacji kodu.

### Bezpieczeństwo

- Trzymaj punkty końcowe hooków za loopback, tailnet albo zaufanym reverse proxy.
- Używaj dedykowanego tokenu hooka; nie używaj ponownie tokenów uwierzytelniania Gateway.
- Utrzymuj `hooks.path` w dedykowanej podścieżce; `/` jest odrzucane.
- Ustaw `hooks.allowedAgentIds`, aby ograniczyć jawne kierowanie `agentId`.
- Zachowaj `hooks.allowRequestSessionKey=false`, chyba że potrzebujesz sesji wybieranych przez wywołującego.
- Jeśli włączysz `hooks.allowRequestSessionKey`, ustaw także `hooks.allowedSessionKeyPrefixes`, aby ograniczyć dozwolone kształty kluczy sesji.
- Ładunki hooków są domyślnie opakowywane granicami bezpieczeństwa.

## Integracja Gmail PubSub

Podłącz wyzwalacze skrzynki odbiorczej Gmail do OpenClaw przez Google PubSub.

**Wymagania wstępne**: CLI `gcloud`, `gog` (gogcli), włączone hooki OpenClaw, Tailscale dla publicznego punktu końcowego HTTPS.

### Konfiguracja kreatorem (zalecane)

```bash
openclaw webhooks gmail setup --account openclaw@gmail.com
```

To zapisuje konfigurację `hooks.gmail`, włącza preset Gmaila i używa Tailscale Funnel dla punktu końcowego push.

### Automatyczny start Gateway

Gdy `hooks.enabled=true` i ustawione jest `hooks.gmail.account`, Gateway uruchamia przy starcie `gog gmail watch serve` i automatycznie odnawia obserwację. Ustaw `OPENCLAW_SKIP_GMAIL_WATCHER=1`, aby z tego zrezygnować.

### Ręczna jednorazowa konfiguracja

1. Wybierz projekt GCP, który jest właścicielem klienta OAuth używanego przez `gog`:

```bash
gcloud auth login
gcloud config set project <project-id>
gcloud services enable gmail.googleapis.com pubsub.googleapis.com
```

2. Utwórz temat i przyznaj Gmailowi dostęp push:

```bash
gcloud pubsub topics create gog-gmail-watch
gcloud pubsub topics add-iam-policy-binding gog-gmail-watch \
  --member=serviceAccount:gmail-api-push@system.gserviceaccount.com \
  --role=roles/pubsub.publisher
```

3. Uruchom obserwację:

```bash
gog gmail watch start \
  --account openclaw@gmail.com \
  --label INBOX \
  --topic projects/<project-id>/topics/gog-gmail-watch
```

### Nadpisanie modelu Gmaila

```json5
{
  hooks: {
    gmail: {
      model: "openrouter/meta-llama/llama-3.3-70b-instruct:free",
      thinking: "off",
    },
  },
}
```

## Zarządzanie zadaniami

```bash
# List all jobs
openclaw cron list

# Edit a job
openclaw cron edit <jobId> --message "Updated prompt" --model "opus"

# Force run a job now
openclaw cron run <jobId>

# Run only if due
openclaw cron run <jobId> --due

# View run history
openclaw cron runs --id <jobId> --limit 50

# Delete a job
openclaw cron remove <jobId>

# Agent selection (multi-agent setups)
openclaw cron add --name "Ops sweep" --cron "0 6 * * *" --session isolated --message "Check ops queue" --agent ops
openclaw cron edit <jobId> --clear-agent
```

Uwaga dotycząca nadpisania modelu:

- `openclaw cron add|edit --model ...` zmienia wybrany model zadania.
- Jeśli model jest dozwolony, dokładnie ten dostawca/model trafia do izolowanego
  uruchomienia agenta.
- Jeśli nie jest dozwolony, cron wyświetla ostrzeżenie i wraca do domyślnego
  wyboru modelu agenta dla tego zadania.
- Skonfigurowane łańcuchy zapasowe nadal mają zastosowanie, ale zwykłe nadpisanie `--model`
  bez jawnej listy zapasowej dla zadania nie przechodzi już dalej do głównego modelu agenta
  jako cichego dodatkowego celu ponowienia.

## Konfiguracja

```json5
{
  cron: {
    enabled: true,
    store: "~/.openclaw/cron/jobs.json",
    maxConcurrentRuns: 1,
    retry: {
      maxAttempts: 3,
      backoffMs: [60000, 120000, 300000],
      retryOn: ["rate_limit", "overloaded", "network", "server_error"],
    },
    webhookToken: "replace-with-dedicated-webhook-token",
    sessionRetention: "24h",
    runLog: { maxBytes: "2mb", keepLines: 2000 },
  },
}
```

Wyłącz cron: `cron.enabled: false` lub `OPENCLAW_SKIP_CRON=1`.

**Ponowienia zadań jednorazowych**: błędy przejściowe (limit szybkości, przeciążenie, sieć, błąd serwera) są ponawiane maksymalnie 3 razy z wykładniczym opóźnieniem. Błędy trwałe powodują natychmiastowe wyłączenie.

**Ponowienia zadań cyklicznych**: wykładnicze opóźnienie (od 30 s do 60 min) między ponowieniami. Opóźnienie resetuje się po następnym udanym uruchomieniu.

**Konserwacja**: `cron.sessionRetention` (domyślnie `24h`) przycina wpisy sesji izolowanych uruchomień. `cron.runLog.maxBytes` / `cron.runLog.keepLines` automatycznie przycinają pliki dziennika uruchomień.

## Rozwiązywanie problemów

### Sekwencja poleceń

```bash
openclaw status
openclaw gateway status
openclaw cron status
openclaw cron list
openclaw cron runs --id <jobId> --limit 20
openclaw system heartbeat last
openclaw logs --follow
openclaw doctor
```

### Cron się nie uruchamia

- Sprawdź `cron.enabled` oraz zmienną środowiskową `OPENCLAW_SKIP_CRON`.
- Potwierdź, że Gateway działa nieprzerwanie.
- Dla harmonogramów `cron` sprawdź strefę czasową (`--tz`) względem strefy czasowej hosta.
- `reason: not-due` w danych wyjściowych uruchomienia oznacza, że ręczne uruchomienie zostało sprawdzone poleceniem `openclaw cron run <jobId> --due` i zadanie nie było jeszcze należne.

### Cron uruchomił się, ale nic nie zostało dostarczone

- Tryb dostarczania `none` oznacza, że nie należy oczekiwać żadnej zewnętrznej wiadomości.
- Brakujący/nieprawidłowy cel dostarczania (`channel`/`to`) oznacza, że wysyłka została pominięta.
- Błędy uwierzytelniania kanału (`unauthorized`, `Forbidden`) oznaczają, że dostarczanie zostało zablokowane przez poświadczenia.
- Jeśli izolowane uruchomienie zwraca tylko cichy token (`NO_REPLY` / `no_reply`),
  OpenClaw pomija bezpośrednie dostarczanie na zewnątrz, a także pomija zapasową
  ścieżkę podsumowania w kolejce, więc nic nie jest publikowane z powrotem na czacie.
- W przypadku izolowanych zadań zarządzanych przez cron nie oczekuj, że agent użyje narzędzia wiadomości
  jako rozwiązania zapasowego. Wykonawca odpowiada za końcowe dostarczenie; `--no-deliver` utrzymuje je
  wewnętrznie zamiast pozwalać na bezpośrednią wysyłkę.

### Pułapki związane ze strefą czasową

- Cron bez `--tz` używa strefy czasowej hosta Gateway.
- Harmonogramy `at` bez strefy czasowej są traktowane jako UTC.
- Heartbeat `activeHours` używa skonfigurowanego rozpoznawania strefy czasowej.

## Powiązane

- [Automatyzacja i zadania](/pl/automation) — wszystkie mechanizmy automatyzacji w skrócie
- [Zadania w tle](/pl/automation/tasks) — rejestr zadań dla wykonań cron
- [Heartbeat](/pl/gateway/heartbeat) — okresowe tury sesji głównej
- [Strefa czasowa](/pl/concepts/timezone) — konfiguracja strefy czasowej
