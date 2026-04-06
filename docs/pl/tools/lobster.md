---
read_when:
    - Chcesz deterministycznych wieloetapowych workflow z jawnymi zatwierdzeniami
    - Musisz wznowić workflow bez ponownego uruchamiania wcześniejszych kroków
summary: Typowane środowisko uruchomieniowe workflow dla OpenClaw z wznawialnymi bramkami zatwierdzeń.
title: Lobster
x-i18n:
    generated_at: "2026-04-06T03:14:10Z"
    model: gpt-5.4
    provider: openai
    source_hash: c1014945d104ef8fdca0d30be89e35136def1b274c6403b06de29e8502b8124b
    source_path: tools/lobster.md
    workflow: 15
---

# Lobster

Lobster to powłoka workflow, która pozwala OpenClaw uruchamiać wieloetapowe sekwencje narzędzi jako jedną, deterministyczną operację z jawnymi punktami kontrolnymi zatwierdzania.

Lobster to warstwa autorska o jeden poziom wyżej niż odłączona praca w tle. W przypadku orkiestracji przepływu ponad pojedynczymi zadaniami zobacz [Task Flow](/pl/automation/taskflow) (`openclaw tasks flow`). Rejestr aktywności zadań znajdziesz w [`openclaw tasks`](/pl/automation/tasks).

## Hook

Twój asystent może budować narzędzia, którymi sam sobą zarządza. Poproś o workflow, a 30 minut później masz CLI oraz pipeline’y, które działają jako jedno wywołanie. Lobster to brakujący element: deterministyczne pipeline’y, jawne zatwierdzenia i stan możliwy do wznowienia.

## Dlaczego

Obecnie złożone workflow wymagają wielu wywołań narzędzi tam i z powrotem. Każde wywołanie kosztuje tokeny, a LLM musi orkiestracją zarządzać na każdym kroku. Lobster przenosi tę orkiestrację do typowanego środowiska uruchomieniowego:

- **Jedno wywołanie zamiast wielu**: OpenClaw wykonuje jedno wywołanie narzędzia Lobster i otrzymuje ustrukturyzowany wynik.
- **Wbudowane zatwierdzenia**: Efekty uboczne (wysłanie e-maila, opublikowanie komentarza) zatrzymują workflow, dopóki nie zostaną jawnie zatwierdzone.
- **Możliwość wznowienia**: Zatrzymane workflow zwracają token; zatwierdź i wznów bez ponownego uruchamiania wszystkiego.

## Dlaczego DSL zamiast zwykłych programów?

Lobster jest celowo mały. Celem nie jest „nowy język”, tylko przewidywalna, przyjazna AI specyfikacja pipeline’u z natywną obsługą zatwierdzeń i tokenów wznowienia.

- **Approve/resume jest wbudowane**: Zwykły program może poprosić człowieka o decyzję, ale nie potrafi _zatrzymać się i wznowić_ z trwałym tokenem bez samodzielnego zbudowania takiego runtime.
- **Deterministyczność + audytowalność**: Pipeline’y są danymi, więc łatwo je logować, porównywać, odtwarzać i recenzować.
- **Ograniczona powierzchnia dla AI**: Mała gramatyka + przekazywanie JSON zmniejszają „kreatywne” ścieżki kodu i czynią walidację realistyczną.
- **Wbudowane zasady bezpieczeństwa**: Timeouty, limity wyjścia, kontrole sandboxa i listy dozwolonych są egzekwowane przez runtime, a nie przez każdy skrypt osobno.
- **Nadal programowalne**: Każdy krok może wywołać dowolne CLI lub skrypt. Jeśli chcesz JS/TS, generuj pliki `.lobster` z kodu.

## Jak to działa

OpenClaw uruchamia workflow Lobster **w procesie** przy użyciu osadzonego runnera. Nie jest uruchamiany żaden zewnętrzny subprocess CLI; silnik workflow wykonuje się wewnątrz procesu gateway i zwraca bezpośrednio kopertę JSON.
Jeśli pipeline zatrzyma się na potrzeby zatwierdzenia, narzędzie zwraca `resumeToken`, aby można było kontynuować później.

## Wzorzec: małe CLI + potoki JSON + zatwierdzenia

Buduj małe polecenia, które komunikują się przez JSON, a następnie łącz je w jedno wywołanie Lobster. (Nazwy poleceń poniżej to tylko przykłady — podmień je na własne).

```bash
inbox list --json
inbox categorize --json
inbox apply --json
```

```json
{
  "action": "run",
  "pipeline": "exec --json --shell 'inbox list --json' | exec --stdin json --shell 'inbox categorize --json' | exec --stdin json --shell 'inbox apply --json' | approve --preview-from-stdin --limit 5 --prompt 'Apply changes?'",
  "timeoutMs": 30000
}
```

Jeśli pipeline zażąda zatwierdzenia, wznów go przy użyciu tokena:

```json
{
  "action": "resume",
  "token": "<resumeToken>",
  "approve": true
}
```

AI wyzwala workflow; Lobster wykonuje kroki. Bramki zatwierdzeń sprawiają, że efekty uboczne są jawne i audytowalne.

Przykład: mapowanie elementów wejściowych na wywołania narzędzi:

```bash
gog.gmail.search --query 'newer_than:1d' \
  | openclaw.invoke --tool message --action send --each --item-key message --args-json '{"provider":"telegram","to":"..."}'
```

## Kroki LLM tylko w JSON (`llm-task`)

Dla workflow, które potrzebują **ustrukturyzowanego kroku LLM**, włącz opcjonalne
narzędzie pluginu `llm-task` i wywołuj je z Lobster. Pozwala to zachować deterministyczność
workflow, a jednocześnie nadal umożliwia klasyfikację/podsumowywanie/tworzenie szkiców przy użyciu modelu.

Włącz narzędzie:

```json
{
  "plugins": {
    "entries": {
      "llm-task": { "enabled": true }
    }
  },
  "agents": {
    "list": [
      {
        "id": "main",
        "tools": { "allow": ["llm-task"] }
      }
    ]
  }
}
```

Użycie w pipeline:

```lobster
openclaw.invoke --tool llm-task --action json --args-json '{
  "prompt": "Given the input email, return intent and draft.",
  "thinking": "low",
  "input": { "subject": "Hello", "body": "Can you help?" },
  "schema": {
    "type": "object",
    "properties": {
      "intent": { "type": "string" },
      "draft": { "type": "string" }
    },
    "required": ["intent", "draft"],
    "additionalProperties": false
  }
}'
```

Zobacz [LLM Task](/pl/tools/llm-task), aby poznać szczegóły i opcje konfiguracji.

## Pliki workflow (.lobster)

Lobster może uruchamiać pliki workflow YAML/JSON z polami `name`, `args`, `steps`, `env`, `condition` i `approval`. W wywołaniach narzędzi OpenClaw ustaw `pipeline` na ścieżkę do pliku.

```yaml
name: inbox-triage
args:
  tag:
    default: "family"
steps:
  - id: collect
    command: inbox list --json
  - id: categorize
    command: inbox categorize --json
    stdin: $collect.stdout
  - id: approve
    command: inbox apply --approve
    stdin: $categorize.stdout
    approval: required
  - id: execute
    command: inbox apply --execute
    stdin: $categorize.stdout
    condition: $approve.approved
```

Uwagi:

- `stdin: $step.stdout` i `stdin: $step.json` przekazują wyjście wcześniejszego kroku.
- `condition` (lub `when`) może bramkować kroki na podstawie `$step.approved`.

## Instalacja Lobster

Bundlowane workflow Lobster działają w procesie; nie jest wymagany osobny binarny plik `lobster`. Osadzony runner jest dostarczany wraz z pluginem Lobster.

Jeśli potrzebujesz samodzielnego CLI Lobster do pracy deweloperskiej albo zewnętrznych pipeline’ów, zainstaluj go z [repozytorium Lobster](https://github.com/openclaw/lobster) i upewnij się, że `lobster` znajduje się w `PATH`.

## Włącz narzędzie

Lobster to **opcjonalne** narzędzie pluginu (domyślnie wyłączone).

Zalecane (addytywne, bezpieczne):

```json
{
  "tools": {
    "alsoAllow": ["lobster"]
  }
}
```

Albo dla konkretnego agenta:

```json
{
  "agents": {
    "list": [
      {
        "id": "main",
        "tools": {
          "alsoAllow": ["lobster"]
        }
      }
    ]
  }
}
```

Unikaj używania `tools.allow: ["lobster"]`, chyba że zamierzasz działać w restrykcyjnym trybie listy dozwolonych.

Uwaga: listy dozwolonych są opcjonalne dla pluginów opcjonalnych. Jeśli Twoja lista dozwolonych wymienia tylko
narzędzia pluginów (takie jak `lobster`), OpenClaw pozostawia narzędzia rdzenia włączone. Aby ograniczyć narzędzia rdzenia,
uwzględnij na liście dozwolonych również narzędzia lub grupy rdzenia, których chcesz używać.

## Przykład: triage e-maili

Bez Lobster:

```
User: "Check my email and draft replies"
→ openclaw calls gmail.list
→ LLM summarizes
→ User: "draft replies to #2 and #5"
→ LLM drafts
→ User: "send #2"
→ openclaw calls gmail.send
(repeat daily, no memory of what was triaged)
```

Z Lobster:

```json
{
  "action": "run",
  "pipeline": "email.triage --limit 20",
  "timeoutMs": 30000
}
```

Zwraca kopertę JSON (skróconą):

```json
{
  "ok": true,
  "status": "needs_approval",
  "output": [{ "summary": "5 need replies, 2 need action" }],
  "requiresApproval": {
    "type": "approval_request",
    "prompt": "Send 2 draft replies?",
    "items": [],
    "resumeToken": "..."
  }
}
```

Użytkownik zatwierdza → wznowienie:

```json
{
  "action": "resume",
  "token": "<resumeToken>",
  "approve": true
}
```

Jeden workflow. Deterministyczny. Bezpieczny.

## Parametry narzędzia

### `run`

Uruchom pipeline w trybie narzędzia.

```json
{
  "action": "run",
  "pipeline": "gog.gmail.search --query 'newer_than:1d' | email.triage",
  "cwd": "workspace",
  "timeoutMs": 30000,
  "maxStdoutBytes": 512000
}
```

Uruchom plik workflow z argumentami:

```json
{
  "action": "run",
  "pipeline": "/path/to/inbox-triage.lobster",
  "argsJson": "{\"tag\":\"family\"}"
}
```

### `resume`

Kontynuuj zatrzymany workflow po zatwierdzeniu.

```json
{
  "action": "resume",
  "token": "<resumeToken>",
  "approve": true
}
```

### Opcjonalne dane wejściowe

- `cwd`: Względny katalog roboczy dla pipeline’u (musi pozostać w obrębie katalogu roboczego gateway).
- `timeoutMs`: Przerwij workflow, jeśli przekroczy ten czas (domyślnie: 20000).
- `maxStdoutBytes`: Przerwij workflow, jeśli wyjście przekroczy ten rozmiar (domyślnie: 512000).
- `argsJson`: Ciąg JSON przekazywany do `lobster run --args-json` (tylko pliki workflow).

## Koperta wyjściowa

Lobster zwraca kopertę JSON z jednym z trzech statusów:

- `ok` → zakończono pomyślnie
- `needs_approval` → wstrzymano; `requiresApproval.resumeToken` jest wymagany do wznowienia
- `cancelled` → jawnie odrzucono lub anulowano

Narzędzie udostępnia kopertę zarówno w `content` (ładnie sformatowany JSON), jak i w `details` (surowy obiekt).

## Zatwierdzenia

Jeśli występuje `requiresApproval`, sprawdź prompt i zdecyduj:

- `approve: true` → wznów i kontynuuj efekty uboczne
- `approve: false` → anuluj i zakończ workflow

Użyj `approve --preview-from-stdin --limit N`, aby dołączać podgląd JSON do żądań zatwierdzenia bez własnego klejenia `jq`/heredoc. Tokeny wznowienia są teraz zwięzłe: Lobster przechowuje stan wznowienia workflow w swoim katalogu stanu i zwraca mały klucz tokena.

## OpenProse

OpenProse dobrze współpracuje z Lobster: użyj `/prose` do orkiestracji przygotowania wieloagentowego, a następnie uruchom pipeline Lobster dla deterministycznych zatwierdzeń. Jeśli program Prose potrzebuje Lobster, zezwól na narzędzie `lobster` dla subagentów przez `tools.subagents.tools`. Zobacz [OpenProse](/pl/prose).

## Bezpieczeństwo

- **Tylko lokalnie, w procesie** — workflow wykonują się wewnątrz procesu gateway; sam plugin nie wykonuje wywołań sieciowych.
- **Bez sekretów** — Lobster nie zarządza OAuth; wywołuje narzędzia OpenClaw, które to robią.
- **Świadomy sandboxa** — wyłączony, gdy kontekst narzędzia jest sandboxowany.
- **Wzmocniony** — timeouty i limity wyjścia są egzekwowane przez osadzony runner.

## Rozwiązywanie problemów

- **`lobster timed out`** → zwiększ `timeoutMs` albo podziel długi pipeline.
- **`lobster output exceeded maxStdoutBytes`** → zwiększ `maxStdoutBytes` albo zmniejsz rozmiar wyjścia.
- **`lobster returned invalid JSON`** → upewnij się, że pipeline działa w trybie narzędzia i wypisuje tylko JSON.
- **`lobster failed`** → sprawdź logi gateway, aby uzyskać szczegóły błędu osadzonego runnera.

## Dowiedz się więcej

- [Plugins](/pl/tools/plugin)
- [Plugin tool authoring](/pl/plugins/building-plugins#registering-agent-tools)

## Studium przypadku: workflow społeczności

Jeden publiczny przykład: CLI typu „second brain” + pipeline’y Lobster, które zarządzają trzema skarbcami Markdown (osobistym, partnera i współdzielonym). CLI emituje JSON dla statystyk, list skrzynki odbiorczej i skanów przestarzałych wpisów; Lobster łączy te polecenia w workflow takie jak `weekly-review`, `inbox-triage`, `memory-consolidation` i `shared-task-sync`, każde z bramkami zatwierdzeń. AI obsługuje ocenę (kategoryzację), gdy jest dostępna, a w przeciwnym razie wraca do deterministycznych reguł.

- Wątek: [https://x.com/plattenschieber/status/2014508656335770033](https://x.com/plattenschieber/status/2014508656335770033)
- Repozytorium: [https://github.com/bloomedai/brain-cli](https://github.com/bloomedai/brain-cli)

## Powiązane

- [Automation & Tasks](/pl/automation) — planowanie workflow Lobster
- [Automation Overview](/pl/automation) — wszystkie mechanizmy automatyzacji
- [Tools Overview](/pl/tools) — wszystkie dostępne narzędzia agenta
