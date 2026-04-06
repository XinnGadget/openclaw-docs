---
read_when:
    - Używasz lub modyfikujesz narzędzie exec
    - Debugujesz zachowanie stdin lub TTY
summary: Użycie narzędzia exec, tryby stdin i obsługa TTY
title: Narzędzie Exec
x-i18n:
    generated_at: "2026-04-06T03:14:03Z"
    model: gpt-5.4
    provider: openai
    source_hash: 28388971c627292dba9bf65ae38d7af8cde49a33bb3b5fc8b20da4f0e350bedd
    source_path: tools/exec.md
    workflow: 15
---

# Narzędzie Exec

Uruchamia polecenia powłoki w obszarze roboczym. Obsługuje wykonanie na pierwszym planie i w tle przez `process`.
Jeśli `process` jest niedozwolone, `exec` działa synchronicznie i ignoruje `yieldMs`/`background`.
Sesje w tle są ograniczone do agenta; `process` widzi tylko sesje tego samego agenta.

## Parametry

- `command` (wymagane)
- `workdir` (domyślnie cwd)
- `env` (nadpisania klucz/wartość)
- `yieldMs` (domyślnie 10000): automatyczne przejście do tła po opóźnieniu
- `background` (bool): natychmiastowe uruchomienie w tle
- `timeout` (sekundy, domyślnie 1800): zabicie po wygaśnięciu
- `pty` (bool): uruchomienie w pseudo-terminalu, gdy dostępny (CLI tylko z TTY, agenci kodujący, interfejsy terminalowe)
- `host` (`auto | sandbox | gateway | node`): miejsce wykonania
- `security` (`deny | allowlist | full`): tryb egzekwowania dla `gateway`/`node`
- `ask` (`off | on-miss | always`): prompty zatwierdzeń dla `gateway`/`node`
- `node` (string): identyfikator/nazwa węzła dla `host=node`
- `elevated` (bool): żądanie trybu podwyższonego (wyjście z sandboxa na skonfigurowaną ścieżkę hosta); `security=full` jest wymuszane tylko wtedy, gdy elevated rozpozna się jako `full`

Uwagi:

- `host` domyślnie ma wartość `auto`: sandbox, gdy runtime sandboxa jest aktywny dla sesji, w przeciwnym razie gateway.
- `auto` to domyślna strategia routingu, a nie wildcard. `host=node` dla pojedynczego wywołania jest dozwolone z `auto`; `host=gateway` dla pojedynczego wywołania jest dozwolone tylko wtedy, gdy żaden runtime sandboxa nie jest aktywny.
- Bez dodatkowej konfiguracji `host=auto` nadal „po prostu działa”: bez sandboxa rozpoznaje się do `gateway`; aktywny sandbox utrzymuje wykonanie w sandboxie.
- `elevated` wychodzi z sandboxa na skonfigurowaną ścieżkę hosta: domyślnie `gateway` lub `node`, gdy `tools.exec.host=node` (albo domyślna sesji to `host=node`). Jest dostępne tylko wtedy, gdy dostęp podwyższony jest włączony dla bieżącej sesji/dostawcy.
- Zatwierdzenia `gateway`/`node` są kontrolowane przez `~/.openclaw/exec-approvals.json`.
- `node` wymaga sparowanego węzła (aplikacja towarzysząca lub bezgłowy host node).
- Jeśli dostępnych jest wiele węzłów, ustaw `exec.node` lub `tools.exec.node`, aby wybrać jeden.
- `exec host=node` to jedyna ścieżka wykonywania powłoki dla węzłów; starsze opakowanie `nodes.run` zostało usunięte.
- Na hostach innych niż Windows exec używa `SHELL`, jeśli jest ustawione; jeśli `SHELL` to `fish`, preferuje `bash` (lub `sh`)
  z `PATH`, aby uniknąć skryptów niezgodnych z fish, a dopiero potem przechodzi awaryjnie do `SHELL`, jeśli żaden z nich nie istnieje.
- Na hostach Windows exec preferuje wykrywanie PowerShell 7 (`pwsh`) (Program Files, ProgramW6432, a potem PATH),
  a następnie przechodzi awaryjnie do Windows PowerShell 5.1.
- Wykonanie na hoście (`gateway`/`node`) odrzuca `env.PATH` i nadpisania loadera (`LD_*`/`DYLD_*`), aby
  zapobiec przechwytywaniu binarek lub wstrzyknięciu kodu.
- OpenClaw ustawia `OPENCLAW_SHELL=exec` w środowisku uruchomionego polecenia (w tym dla wykonania PTY i w sandboxie), aby reguły powłoki/profilu mogły wykryć kontekst narzędzia exec.
- Ważne: sandboxing jest **domyślnie wyłączony**. Jeśli sandboxing jest wyłączony, niejawne `host=auto`
  rozpoznaje się do `gateway`. Jawne `host=sandbox` nadal kończy się bezpieczną odmową zamiast cicho
  uruchamiać się na hoście gateway. Włącz sandboxing albo użyj `host=gateway` z zatwierdzeniami.
- Kontrole wstępne skryptów (dla typowych błędów składni powłoki Python/Node) sprawdzają tylko pliki wewnątrz
  skutecznej granicy `workdir`. Jeśli ścieżka skryptu rozpoznaje się poza `workdir`, kontrola wstępna jest
  pomijana dla tego pliku.
- W przypadku długotrwałej pracy, która zaczyna się teraz, uruchom ją raz i polegaj na automatycznym
  wybudzeniu po zakończeniu, gdy jest włączone, a polecenie emituje dane wyjściowe lub kończy się błędem.
  Używaj `process` do logów, stanu, wejścia lub interwencji; nie emuluj
  planowania za pomocą pętli sleep, pętli timeout ani wielokrotnego odpytywania.
- Dla pracy, która ma wydarzyć się później albo według harmonogramu, używaj crona zamiast
  wzorców sleep/delay w `exec`.

## Config

- `tools.exec.notifyOnExit` (domyślnie: true): gdy true, sesje exec uruchomione w tle kolejkają zdarzenie systemowe i żądają heartbeat po zakończeniu.
- `tools.exec.approvalRunningNoticeMs` (domyślnie: 10000): emituje pojedyncze powiadomienie „running”, gdy exec objęty zatwierdzeniem działa dłużej niż ten czas (0 wyłącza).
- `tools.exec.host` (domyślnie: `auto`; rozpoznaje się do `sandbox`, gdy runtime sandboxa jest aktywny, w przeciwnym razie do `gateway`)
- `tools.exec.security` (domyślnie: `deny` dla sandboxa, `full` dla gateway + node, gdy nieustawione)
- `tools.exec.ask` (domyślnie: `off`)
- Wykonanie hosta bez zatwierdzeń to ustawienie domyślne dla gateway + node. Jeśli chcesz zachowania z zatwierdzeniami/listą dozwolonych, zaostrz zarówno `tools.exec.*`, jak i zasady hosta w `~/.openclaw/exec-approvals.json`; zobacz [Zatwierdzenia exec](/pl/tools/exec-approvals#no-approval-yolo-mode).
- YOLO wynika z domyślnych ustawień zasad hosta (`security=full`, `ask=off`), a nie z `host=auto`. Jeśli chcesz wymusić routing przez gateway lub node, ustaw `tools.exec.host` albo użyj `/exec host=...`.
- W trybie `security=full` plus `ask=off` wykonanie hosta stosuje skonfigurowaną politykę bezpośrednio; nie ma dodatkowego heurystycznego prefiltru zaciemniania poleceń.
- `tools.exec.node` (domyślnie: nieustawione)
- `tools.exec.strictInlineEval` (domyślnie: false): gdy true, formy inline eval interpreterów, takie jak `python -c`, `node -e`, `ruby -e`, `perl -e`, `php -r`, `lua -e` i `osascript -e`, zawsze wymagają jawnego zatwierdzenia. `allow-always` może nadal utrwalać łagodne wywołania interpretera/skryptu, ale formy inline eval nadal pytają za każdym razem.
- `tools.exec.pathPrepend`: lista katalogów do dodania na początek `PATH` dla uruchomień exec (tylko gateway + sandbox).
- `tools.exec.safeBins`: bezpieczne binarki tylko do stdin, które mogą działać bez jawnych wpisów na liście dozwolonych. Szczegóły zachowania znajdziesz w [Safe bins](/pl/tools/exec-approvals#safe-bins-stdin-only).
- `tools.exec.safeBinTrustedDirs`: dodatkowe jawne katalogi zaufane dla kontroli ścieżek wykonywalnych `safeBins`. Wpisy `PATH` nigdy nie stają się automatycznie zaufane. Wbudowane wartości domyślne to `/bin` i `/usr/bin`.
- `tools.exec.safeBinProfiles`: opcjonalna niestandardowa polityka argv dla każdego safe bin (`minPositional`, `maxPositional`, `allowedValueFlags`, `deniedFlags`).

Przykład:

```json5
{
  tools: {
    exec: {
      pathPrepend: ["~/bin", "/opt/oss/bin"],
    },
  },
}
```

### Obsługa PATH

- `host=gateway`: scala `PATH` z powłoki logowania do środowiska exec. Nadpisania `env.PATH` są
  odrzucane dla wykonania na hoście. Sam demon nadal działa z minimalnym `PATH`:
  - macOS: `/opt/homebrew/bin`, `/usr/local/bin`, `/usr/bin`, `/bin`
  - Linux: `/usr/local/bin`, `/usr/bin`, `/bin`
- `host=sandbox`: uruchamia `sh -lc` (powłoka logowania) wewnątrz kontenera, więc `/etc/profile` może zresetować `PATH`.
  OpenClaw dodaje `env.PATH` na początek po wczytaniu profilu przez wewnętrzną zmienną env (bez interpolacji powłoki);
  `tools.exec.pathPrepend` także ma tu zastosowanie.
- `host=node`: tylko nieblokowane nadpisania env, które przekażesz, są wysyłane do węzła. Nadpisania `env.PATH` są
  odrzucane dla wykonania na hoście i ignorowane przez hosty node. Jeśli potrzebujesz dodatkowych wpisów PATH na węźle,
  skonfiguruj środowisko usługi hosta node (systemd/launchd) albo zainstaluj narzędzia w standardowych lokalizacjach.

Powiązanie węzła dla agenta (użyj indeksu listy agentów w config):

```bash
openclaw config get agents.list
openclaw config set agents.list[0].tools.exec.node "node-id-or-name"
```

Control UI: karta Nodes zawiera mały panel „Exec node binding” dla tych samych ustawień.

## Nadpisania sesji (`/exec`)

Użyj `/exec`, aby ustawić **domyślne wartości dla sesji** dla `host`, `security`, `ask` i `node`.
Wyślij `/exec` bez argumentów, aby wyświetlić bieżące wartości.

Przykład:

```
/exec host=auto security=allowlist ask=on-miss node=mac-1
```

## Model autoryzacji

`/exec` jest honorowane tylko dla **autoryzowanych nadawców** (listy dozwolonych kanału/parowanie plus `commands.useAccessGroups`).
Aktualizuje **tylko stan sesji** i nie zapisuje config. Aby całkowicie wyłączyć exec, zabroń go przez politykę narzędzi
(`tools.deny: ["exec"]` lub dla konkretnego agenta). Zatwierdzenia hosta nadal obowiązują, chyba że jawnie ustawisz
`security=full` i `ask=off`.

## Zatwierdzenia exec (aplikacja towarzysząca / host node)

Agenci działający w sandboxie mogą wymagać zatwierdzenia dla każdego żądania, zanim `exec` uruchomi się na hoście gateway lub node.
Zobacz [Zatwierdzenia exec](/pl/tools/exec-approvals), aby poznać politykę, listę dozwolonych i przepływ UI.

Gdy zatwierdzenia są wymagane, narzędzie exec zwraca natychmiast
`status: "approval-pending"` i identyfikator zatwierdzenia. Po zatwierdzeniu (lub odmowie / przekroczeniu czasu),
Gateway emituje zdarzenia systemowe (`Exec finished` / `Exec denied`). Jeśli polecenie nadal
działa po `tools.exec.approvalRunningNoticeMs`, emitowane jest pojedyncze powiadomienie `Exec running`.
W kanałach z natywnymi kartami/przyciskami zatwierdzeń agent powinien w pierwszej kolejności polegać na
tym natywnym UI i dołączać ręczne polecenie `/approve` tylko wtedy, gdy wynik
narzędzia wyraźnie mówi, że zatwierdzenia na czacie są niedostępne lub ręczne zatwierdzenie jest
jedyną ścieżką.

## Allowlist + safe bins

Ręczne egzekwowanie listy dozwolonych dopasowuje **tylko rozpoznane ścieżki binarek** (bez dopasowań po samej nazwie). Gdy
`security=allowlist`, polecenia powłoki są automatycznie dozwolone tylko wtedy, gdy każdy segment potoku jest
na liście dozwolonych lub jest safe bin. Łączenie (`;`, `&&`, `||`) i przekierowania są odrzucane w
trybie allowlist, chyba że każdy segment najwyższego poziomu spełnia warunki listy dozwolonych (w tym safe bins).
Przekierowania pozostają nieobsługiwane.
Trwałe zaufanie `allow-always` nie omija tej reguły: polecenie łączone nadal wymaga, aby każdy
segment najwyższego poziomu pasował.

`autoAllowSkills` to osobna ścieżka wygody w zatwierdzeniach exec. To nie to samo co
ręczne wpisy ścieżek na liście dozwolonych. Dla ścisłego jawnego zaufania trzymaj `autoAllowSkills` wyłączone.

Używaj tych dwóch mechanizmów do różnych zadań:

- `tools.exec.safeBins`: małe filtry strumieni działające tylko na stdin.
- `tools.exec.safeBinTrustedDirs`: jawne dodatkowe zaufane katalogi dla ścieżek wykonywalnych safe bin.
- `tools.exec.safeBinProfiles`: jawna polityka argv dla niestandardowych safe bins.
- allowlist: jawne zaufanie dla ścieżek wykonywalnych.

Nie traktuj `safeBins` jako ogólnej listy dozwolonych i nie dodawaj binarek interpreterów/runtime (na przykład `python3`, `node`, `ruby`, `bash`). Jeśli ich potrzebujesz, użyj jawnych wpisów na liście dozwolonych i pozostaw włączone prompty zatwierdzeń.
`openclaw security audit` ostrzega, gdy wpisom interpreterów/runtime w `safeBins` brakuje jawnych profili, a `openclaw doctor --fix` może utworzyć brakujące niestandardowe wpisy `safeBinProfiles`.
`openclaw security audit` i `openclaw doctor` ostrzegają także, gdy jawnie dodajesz z powrotem do `safeBins` binarki o szerokim zachowaniu, takie jak `jq`.
Jeśli jawnie umieszczasz interpretery na liście dozwolonych, włącz `tools.exec.strictInlineEval`, aby formy inline code-eval nadal wymagały nowego zatwierdzenia.

Pełne szczegóły polityki i przykłady znajdziesz w [Zatwierdzenia exec](/pl/tools/exec-approvals#safe-bins-stdin-only) i [Safe bins a allowlist](/pl/tools/exec-approvals#safe-bins-versus-allowlist).

## Przykłady

Pierwszy plan:

```json
{ "tool": "exec", "command": "ls -la" }
```

Tło + odpytywanie:

```json
{"tool":"exec","command":"npm run build","yieldMs":1000}
{"tool":"process","action":"poll","sessionId":"<id>"}
```

Odpytywanie służy do sprawdzania stanu na żądanie, a nie do pętli oczekiwania. Jeśli automatyczne wybudzenie po zakończeniu
jest włączone, polecenie może wybudzić sesję, gdy emituje dane wyjściowe lub kończy się błędem.

Wysyłanie klawiszy (w stylu tmux):

```json
{"tool":"process","action":"send-keys","sessionId":"<id>","keys":["Enter"]}
{"tool":"process","action":"send-keys","sessionId":"<id>","keys":["C-c"]}
{"tool":"process","action":"send-keys","sessionId":"<id>","keys":["Up","Up","Enter"]}
```

Submit (wysyła tylko CR):

```json
{ "tool": "process", "action": "submit", "sessionId": "<id>" }
```

Wklejanie (domyślnie w nawiasach):

```json
{ "tool": "process", "action": "paste", "sessionId": "<id>", "text": "line1\nline2\n" }
```

## apply_patch

`apply_patch` to podnarzędzie `exec` do ustrukturyzowanych wieloplikowych edycji.
Jest domyślnie włączone dla modeli OpenAI i OpenAI Codex. Używaj config tylko
wtedy, gdy chcesz je wyłączyć lub ograniczyć do konkretnych modeli:

```json5
{
  tools: {
    exec: {
      applyPatch: { workspaceOnly: true, allowModels: ["gpt-5.4"] },
    },
  },
}
```

Uwagi:

- Dostępne tylko dla modeli OpenAI/OpenAI Codex.
- Polityka narzędzi nadal obowiązuje; `allow: ["write"]` domyślnie zezwala także na `apply_patch`.
- Config znajduje się pod `tools.exec.applyPatch`.
- `tools.exec.applyPatch.enabled` domyślnie ma wartość `true`; ustaw `false`, aby wyłączyć narzędzie dla modeli OpenAI.
- `tools.exec.applyPatch.workspaceOnly` domyślnie ma wartość `true` (ograniczone do obszaru roboczego). Ustaw `false` tylko wtedy, gdy celowo chcesz, aby `apply_patch` zapisywało/usuwalo poza katalogiem obszaru roboczego.

## Powiązane

- [Zatwierdzenia exec](/pl/tools/exec-approvals) — bramki zatwierdzeń dla poleceń powłoki
- [Sandboxing](/pl/gateway/sandboxing) — uruchamianie poleceń w środowiskach sandbox
- [Proces w tle](/pl/gateway/background-process) — długotrwałe exec i narzędzie process
- [Bezpieczeństwo](/pl/gateway/security) — polityka narzędzi i dostęp podwyższony
