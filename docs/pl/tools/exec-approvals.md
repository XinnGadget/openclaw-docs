---
read_when:
    - Konfigurowanie zatwierdzeń exec lub allowlist
    - Implementowanie UX zatwierdzeń exec w aplikacji macOS
    - Przegląd promptów wyjścia z sandboxa i ich konsekwencji
summary: Zatwierdzenia exec, allowlisty i prompty wyjścia z sandboxa
title: Zatwierdzenia exec
x-i18n:
    generated_at: "2026-04-06T03:14:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: 39e91cd5c7615bdb9a6b201a85bde7514327910f6f12da5a4b0532bceb229c22
    source_path: tools/exec-approvals.md
    workflow: 15
---

# Zatwierdzenia exec

Zatwierdzenia exec to **zabezpieczenie aplikacji towarzyszącej / hosta node** umożliwiające uruchamianie przez sandboxowanego agenta
poleceń na prawdziwym hoście (`gateway` lub `node`). Potraktuj to jak blokadę bezpieczeństwa:
polecenia są dozwolone tylko wtedy, gdy zasada + allowlista + (opcjonalnie) zatwierdzenie użytkownika są zgodne.
Zatwierdzenia exec działają **dodatkowo** względem polityki narzędzi i bramkowania elevated (chyba że elevated ma wartość `full`, co pomija zatwierdzenia).
Skuteczna polityka jest **bardziej restrykcyjną** z `tools.exec.*` i domyślnych ustawień zatwierdzeń; jeśli pole zatwierdzeń zostanie pominięte, używana jest wartość z `tools.exec`.
Host exec używa też lokalnego stanu zatwierdzeń na tej maszynie. Lokalna dla hosta
wartość `ask: "always"` w `~/.openclaw/exec-approvals.json` będzie nadal wymuszać prompty, nawet jeśli
domyślne ustawienia sesji lub konfiguracji żądają `ask: "on-miss"`.
Użyj `openclaw approvals get`, `openclaw approvals get --gateway` lub
`openclaw approvals get --node <id|name|ip>`, aby sprawdzić żądaną politykę,
źródła polityki hosta i wynik skuteczny.

Jeśli UI aplikacji towarzyszącej **nie jest dostępny**, każde żądanie wymagające promptu
jest rozwiązywane przez **ask fallback** (domyślnie: deny).

Natywni klienci zatwierdzeń na czacie mogą też udostępniać elementy interfejsu specyficzne dla kanału na
wiadomości z oczekującym zatwierdzeniem. Na przykład Matrix może dodać skróty reakcji do
promptu zatwierdzenia (`✅` pozwól raz, `❌` odmów i `♾️` zawsze pozwalaj, gdy dostępne),
jednocześnie pozostawiając w wiadomości polecenia `/approve ...` jako fallback.

## Gdzie ma to zastosowanie

Zatwierdzenia exec są egzekwowane lokalnie na hoście wykonawczym:

- **host gatewaya** → proces `openclaw` na maszynie gatewaya
- **host node** → runner node (aplikacja towarzysząca macOS lub bezgłowy host node)

Uwaga o modelu zaufania:

- Wywołujący uwierzytelnieni przez Gateway są zaufanymi operatorami tego Gatewaya.
- Sparowane nody rozszerzają tę zdolność zaufanego operatora na host node.
- Zatwierdzenia exec zmniejszają ryzyko przypadkowego wykonania, ale nie stanowią granicy auth per użytkownik.
- Zatwierdzone uruchomienia na hoście node wiążą kanoniczny kontekst wykonania: kanoniczne cwd, dokładne argv, powiązanie env
  gdy występuje oraz przypiętą ścieżkę wykonywalną, gdy ma to zastosowanie.
- Dla skryptów powłoki i bezpośrednich wywołań plików interpreterów/runtime OpenClaw próbuje również powiązać
  jeden konkretny lokalny operand plikowy. Jeśli ten powiązany plik zmieni się po zatwierdzeniu, ale przed wykonaniem,
  uruchomienie zostanie odrzucone zamiast wykonywać zmienioną treść.
- To powiązanie pliku jest celowo wykonywane w trybie best-effort, a nie jako kompletny model semantyczny dla każdej
  ścieżki ładowania interpretera/runtime. Jeśli tryb zatwierdzania nie może zidentyfikować dokładnie jednego konkretnego lokalnego
  pliku do powiązania, odmawia wygenerowania uruchomienia opartego na zatwierdzeniu zamiast udawać pełne pokrycie.

Podział na macOS:

- **usługa hosta node** przekazuje `system.run` do **aplikacji macOS** przez lokalne IPC.
- **aplikacja macOS** egzekwuje zatwierdzenia + wykonuje polecenie w kontekście UI.

## Ustawienia i przechowywanie

Zatwierdzenia znajdują się w lokalnym pliku JSON na hoście wykonawczym:

`~/.openclaw/exec-approvals.json`

Przykładowy schemat:

```json
{
  "version": 1,
  "socket": {
    "path": "~/.openclaw/exec-approvals.sock",
    "token": "base64url-token"
  },
  "defaults": {
    "security": "deny",
    "ask": "on-miss",
    "askFallback": "deny",
    "autoAllowSkills": false
  },
  "agents": {
    "main": {
      "security": "allowlist",
      "ask": "on-miss",
      "askFallback": "deny",
      "autoAllowSkills": true,
      "allowlist": [
        {
          "id": "B0C8C0B3-2C2D-4F8A-9A3C-5A4B3C2D1E0F",
          "pattern": "~/Projects/**/bin/rg",
          "lastUsedAt": 1737150000000,
          "lastUsedCommand": "rg -n TODO",
          "lastResolvedPath": "/Users/user/Projects/.../bin/rg"
        }
      ]
    }
  }
}
```

## Tryb bez zatwierdzeń „YOLO”

Jeśli chcesz, aby host exec działał bez promptów zatwierdzania, musisz otworzyć **obie** warstwy polityki:

- żądaną politykę exec w konfiguracji OpenClaw (`tools.exec.*`)
- lokalną politykę zatwierdzeń hosta w `~/.openclaw/exec-approvals.json`

To jest teraz domyślne zachowanie hosta, chyba że jawnie je zaostrzysz:

- `tools.exec.security`: `full` na `gateway`/`node`
- `tools.exec.ask`: `off`
- host `askFallback`: `full`

Ważne rozróżnienie:

- `tools.exec.host=auto` wybiera miejsce wykonania exec: sandbox, jeśli dostępny, w przeciwnym razie gateway.
- YOLO wybiera sposób zatwierdzania host exec: `security=full` plus `ask=off`.
- W trybie YOLO OpenClaw nie dodaje osobnej heurystycznej bramki zatwierdzenia zaciemniania poleceń ponad skonfigurowaną politykę host exec.
- `auto` nie sprawia, że routing do gatewaya staje się darmowym nadpisaniem z sesji sandboxowanej. Żądanie per wywołanie `host=node` jest dozwolone z `auto`, a `host=gateway` jest dozwolone z `auto` tylko wtedy, gdy żaden runtime sandboxa nie jest aktywny. Jeśli chcesz stabilną domyślną wartość inną niż auto, ustaw `tools.exec.host` albo użyj jawnie `/exec host=...`.

Jeśli chcesz bardziej zachowawczej konfiguracji, zaostrz z powrotem którąkolwiek warstwę do `allowlist` / `on-miss`
albo `deny`.

Trwała konfiguracja „nigdy nie pytaj” dla hosta gatewaya:

```bash
openclaw config set tools.exec.host gateway
openclaw config set tools.exec.security full
openclaw config set tools.exec.ask off
openclaw gateway restart
```

Następnie ustaw plik zatwierdzeń hosta zgodnie z tym:

```bash
openclaw approvals set --stdin <<'EOF'
{
  version: 1,
  defaults: {
    security: "full",
    ask: "off",
    askFallback: "full"
  }
}
EOF
```

Dla hosta node zastosuj zamiast tego ten sam plik zatwierdzeń na tym nodzie:

```bash
openclaw approvals set --node <id|name|ip> --stdin <<'EOF'
{
  version: 1,
  defaults: {
    security: "full",
    ask: "off",
    askFallback: "full"
  }
}
EOF
```

Skrót tylko dla sesji:

- `/exec security=full ask=off` zmienia tylko bieżącą sesję.
- `/elevated full` to skrót break-glass, który również pomija zatwierdzenia exec dla tej sesji.

Jeśli plik zatwierdzeń hosta pozostaje bardziej restrykcyjny niż konfiguracja, nadal wygrywa bardziej restrykcyjna polityka hosta.

## Pokrętła polityki

### Security (`exec.security`)

- **deny**: blokuje wszystkie żądania host exec.
- **allowlist**: pozwala tylko na polecenia z allowlisty.
- **full**: pozwala na wszystko (równoważne elevated).

### Ask (`exec.ask`)

- **off**: nigdy nie pytaj.
- **on-miss**: pytaj tylko wtedy, gdy allowlista nie pasuje.
- **always**: pytaj przy każdym poleceniu.
- trwałe zaufanie `allow-always` nie tłumi promptów, gdy skuteczny tryb ask to `always`

### Ask fallback (`askFallback`)

Jeśli prompt jest wymagany, ale żadne UI nie jest osiągalne, fallback decyduje:

- **deny**: blokuj.
- **allowlist**: pozwól tylko, jeśli allowlista pasuje.
- **full**: pozwól.

### Wzmacnianie inline interpreter eval (`tools.exec.strictInlineEval`)

Gdy `tools.exec.strictInlineEval=true`, OpenClaw traktuje formy inline code-eval jako wymagające zatwierdzenia, nawet jeśli sama binarka interpretera jest na allowliście.

Przykłady:

- `python -c`
- `node -e`, `node --eval`, `node -p`
- `ruby -e`
- `perl -e`, `perl -E`
- `php -r`
- `lua -e`
- `osascript -e`

To defense-in-depth dla loaderów interpreterów, które nie mapują się czysto do jednego stabilnego operandu plikowego. W trybie ścisłym:

- te polecenia nadal wymagają jawnego zatwierdzenia;
- `allow-always` nie zapisuje dla nich automatycznie nowych wpisów allowlisty.

## Allowlista (per agent)

Allowlisty są **per agent**. Jeśli istnieje wielu agentów, przełącz agenta, którego
edytujesz, w aplikacji macOS. Wzorce to **dopasowania glob bez rozróżniania wielkości liter**.
Wzorce powinny rozwiązywać się do **ścieżek binarek** (wpisy tylko z basename są ignorowane).
Starsze wpisy `agents.default` są migrowane do `agents.main` przy ładowaniu.
Łańcuchy powłoki takie jak `echo ok && pwd` nadal wymagają, aby każdy segment najwyższego poziomu spełniał reguły allowlisty.

Przykłady:

- `~/Projects/**/bin/peekaboo`
- `~/.local/bin/*`
- `/opt/homebrew/bin/rg`

Każdy wpis allowlisty śledzi:

- **id** stabilny UUID używany do tożsamości w UI (opcjonalny)
- **last used** znacznik czasu
- **last used command**
- **last resolved path**

## Auto-allow Skills CLI

Gdy włączone jest **Auto-allow Skills CLI**, pliki wykonywalne wskazane przez znane Skills
są traktowane jako znajdujące się na allowliście na nodach (macOS node lub bezgłowy host node). Wykorzystuje to
`skills.bins` przez Gateway RPC do pobrania listy binarek skilli. Wyłącz to, jeśli chcesz ścisłych ręcznych allowlist.

Ważne uwagi dotyczące zaufania:

- To **niejawna wygodna allowlista**, oddzielona od ręcznych wpisów allowlisty ścieżek.
- Jest przeznaczona dla zaufanych środowisk operatora, w których Gateway i node znajdują się w tej samej granicy zaufania.
- Jeśli wymagasz ścisłego jawnego zaufania, pozostaw `autoAllowSkills: false` i używaj wyłącznie ręcznych wpisów allowlisty ścieżek.

## Safe bins (tylko stdin)

`tools.exec.safeBins` definiuje małą listę binarek **tylko stdin** (na przykład `cut`),
które mogą działać w trybie allowlisty **bez** jawnych wpisów allowlisty. Safe bins odrzucają
pozycyjne argumenty plikowe i tokeny podobne do ścieżek, więc mogą działać tylko na strumieniu wejściowym.
Traktuj to jako wąską szybką ścieżkę dla filtrów strumieniowych, a nie ogólną listę zaufania.
**Nie** dodawaj binarek interpreterów ani runtime (na przykład `python3`, `node`, `ruby`, `bash`, `sh`, `zsh`) do `safeBins`.
Jeśli polecenie może z założenia wykonywać kod, uruchamiać podpolecenia lub odczytywać pliki, preferuj jawne wpisy allowlisty i pozostaw włączone prompty zatwierdzeń.
Niestandardowe safe bins muszą definiować jawny profil w `tools.exec.safeBinProfiles.<bin>`.
Walidacja jest deterministyczna wyłącznie na podstawie kształtu argv (bez sprawdzania istnienia systemu plików hosta), co
zapobiega zachowaniu typu oracle istnienia pliku wynikającemu z różnic allow/deny.
Opcje zorientowane na pliki są odrzucane dla domyślnych safe bins (na przykład `sort -o`, `sort --output`,
`sort --files0-from`, `sort --compress-program`, `sort --random-source`,
`sort --temporary-directory`/`-T`, `wc --files0-from`, `jq -f/--from-file`,
`grep -f/--file`).
Safe bins wymuszają również jawne zasady flag per binarka dla opcji, które łamią zachowanie tylko stdin
(na przykład `sort -o/--output/--compress-program` i flagi rekurencyjne grep).
Długie opcje są walidowane w trybie fail-closed w safe-bin mode: nieznane flagi i niejednoznaczne
skróty są odrzucane.
Odrzucane flagi według profilu safe-bin:

[//]: # "SAFE_BIN_DENIED_FLAGS:START"

- `grep`: `--dereference-recursive`, `--directories`, `--exclude-from`, `--file`, `--recursive`, `-R`, `-d`, `-f`, `-r`
- `jq`: `--argfile`, `--from-file`, `--library-path`, `--rawfile`, `--slurpfile`, `-L`, `-f`
- `sort`: `--compress-program`, `--files0-from`, `--output`, `--random-source`, `--temporary-directory`, `-T`, `-o`
- `wc`: `--files0-from`

[//]: # "SAFE_BIN_DENIED_FLAGS:END"

Safe bins wymuszają również traktowanie tokenów argv jako **dosłowny tekst** w czasie wykonania (bez globbing
i bez rozwijania `$VARS`) dla segmentów tylko stdin, więc wzorce takie jak `*` lub `$HOME/...` nie mogą być
użyte do przemycania odczytów plików.
Safe bins muszą także rozwiązywać się z zaufanych katalogów binarek (domyślne katalogi systemowe plus opcjonalne
`tools.exec.safeBinTrustedDirs`). Wpisy `PATH` nigdy nie są automatycznie zaufane.
Domyślne zaufane katalogi safe-bin są celowo minimalne: `/bin`, `/usr/bin`.
Jeśli Twój plik wykonywalny safe-bin znajduje się w ścieżkach menedżera pakietów/użytkownika (na przykład
`/opt/homebrew/bin`, `/usr/local/bin`, `/opt/local/bin`, `/snap/bin`), dodaj je jawnie
do `tools.exec.safeBinTrustedDirs`.
Łańcuchy powłoki i przekierowania nie są automatycznie dozwolone w trybie allowlisty.

Łańcuchy powłoki (`&&`, `||`, `;`) są dozwolone, gdy każdy segment najwyższego poziomu spełnia allowlistę
(w tym safe bins lub skill auto-allow). Przekierowania nadal nie są obsługiwane w trybie allowlisty.
Podstawianie poleceń (`$()` / backticks) jest odrzucane podczas parsowania allowlisty, także wewnątrz
podwójnych cudzysłowów; użyj pojedynczych cudzysłowów, jeśli potrzebujesz dosłownego tekstu `$()`.
W zatwierdzeniach aplikacji towarzyszącej macOS surowy tekst powłoki zawierający składnię kontroli lub rozwijania powłoki
(`&&`, `||`, `;`, `|`, `` ` ``, `$`, `<`, `>`, `(`, `)`) jest traktowany jako nietrafienie allowlisty, chyba że
sama binarka powłoki znajduje się na allowliście.
Dla wrapperów powłoki (`bash|sh|zsh ... -c/-lc`) nadpisania env o zakresie żądania są redukowane do małej jawnej
allowlisty (`TERM`, `LANG`, `LC_*`, `COLORTERM`, `NO_COLOR`, `FORCE_COLOR`).
Dla decyzji allow-always w trybie allowlisty znane wrappery dispatch
(`env`, `nice`, `nohup`, `stdbuf`, `timeout`) zapisują wewnętrzne ścieżki wykonywalne zamiast ścieżek wrapperów. Multipleksery powłoki (`busybox`, `toybox`) są również rozpakowywane dla apletów powłoki (`sh`, `ash`,
itd.), tak aby zapisywane były wewnętrzne pliki wykonywalne zamiast binarek multipleksera. Jeśli wrapper lub
multiplekser nie może zostać bezpiecznie rozpakowany, żaden wpis allowlisty nie jest zapisywany automatycznie.
Jeśli umieszczasz na allowliście interpretery takie jak `python3` lub `node`, preferuj `tools.exec.strictInlineEval=true`, aby inline eval nadal wymagał jawnego zatwierdzenia. W trybie ścisłym `allow-always` nadal może zapisywać nieszkodliwe wywołania interpreterów/skryptów, ale nośniki inline-eval nie są zapisywane automatycznie.

Domyślne safe bins:

[//]: # "SAFE_BIN_DEFAULTS:START"

`cut`, `uniq`, `head`, `tail`, `tr`, `wc`

[//]: # "SAFE_BIN_DEFAULTS:END"

`grep` i `sort` nie znajdują się na liście domyślnej. Jeśli jawnie je włączysz, zachowaj jawne wpisy allowlisty dla
ich przepływów pracy innych niż stdin.
Dla `grep` w safe-bin mode podawaj wzorzec przez `-e`/`--regexp`; forma wzorca pozycyjnego jest
odrzucana, aby nie dało się przemycić operandów plikowych jako niejednoznacznych pozycji.

### Safe bins a allowlista

| Topic            | `tools.exec.safeBins`                                  | Allowlist (`exec-approvals.json`)                            |
| ---------------- | ------------------------------------------------------ | ------------------------------------------------------------ |
| Goal             | Automatyczne zezwalanie na wąskie filtry stdin         | Jawne zaufanie do określonych plików wykonywalnych           |
| Match type       | Nazwa pliku wykonywalnego + zasada argv safe-bin       | Wzorzec glob rozwiązanej ścieżki pliku wykonywalnego         |
| Argument scope   | Ograniczany przez profil safe-bin i zasady tokenów dosłownych | Tylko dopasowanie ścieżki; argumenty są poza tym Twoją odpowiedzialnością |
| Typical examples | `head`, `tail`, `tr`, `wc`                             | `jq`, `python3`, `node`, `ffmpeg`, niestandardowe CLI        |
| Best use         | Niskiego ryzyka przekształcenia tekstu w pipeline      | Dowolne narzędzie o szerszym zachowaniu lub efektach ubocznych |

Lokalizacja konfiguracji:

- `safeBins` pochodzi z konfiguracji (`tools.exec.safeBins` lub per agent `agents.list[].tools.exec.safeBins`).
- `safeBinTrustedDirs` pochodzi z konfiguracji (`tools.exec.safeBinTrustedDirs` lub per agent `agents.list[].tools.exec.safeBinTrustedDirs`).
- `safeBinProfiles` pochodzi z konfiguracji (`tools.exec.safeBinProfiles` lub per agent `agents.list[].tools.exec.safeBinProfiles`). Klucze profili per agent nadpisują klucze globalne.
- wpisy allowlisty znajdują się w lokalnym dla hosta `~/.openclaw/exec-approvals.json` pod `agents.<id>.allowlist` (lub przez Control UI / `openclaw approvals allowlist ...`).
- `openclaw security audit` ostrzega przez `tools.exec.safe_bins_interpreter_unprofiled`, gdy binarki interpreterów/runtime pojawiają się w `safeBins` bez jawnych profili.
- `openclaw doctor --fix` może utworzyć szkielety brakujących wpisów `safeBinProfiles.<bin>` jako `{}` (po tym przejrzyj i zaostrz). Binarki interpreterów/runtime nie są tworzone automatycznie.

Przykład niestandardowego profilu:
__OC_I18N_900004__
Jeśli jawnie dodasz `jq` do `safeBins`, OpenClaw nadal odrzuci builtin `env` w safe-bin
mode, aby `jq -n env` nie mogło zrzucić środowiska procesu hosta bez jawnej ścieżki allowlisty
lub promptu zatwierdzenia.

## Edycja w Control UI

Użyj karty **Control UI → Nodes → Exec approvals**, aby edytować wartości domyślne, nadpisania
per agent i allowlisty. Wybierz zakres (Defaults lub agent), dostosuj politykę,
dodaj/usuń wzorce allowlisty, a następnie kliknij **Save**. UI pokazuje metadane **last used**
dla każdego wzorca, aby ułatwić utrzymanie porządku na liście.

Selektor celu wybiera **Gateway** (lokalne zatwierdzenia) albo **Node**. Nody
muszą ogłaszać `system.execApprovals.get/set` (aplikacja macOS lub bezgłowy host node).
Jeśli node nie ogłasza jeszcze zatwierdzeń exec, edytuj jego lokalny
`~/.openclaw/exec-approvals.json` bezpośrednio.

CLI: `openclaw approvals` obsługuje edycję gatewaya lub node (zobacz [CLI zatwierdzeń](/cli/approvals)).

## Przepływ zatwierdzania

Gdy prompt jest wymagany, gateway rozgłasza `exec.approval.requested` do klientów operatora.
Control UI i aplikacja macOS rozwiązują to przez `exec.approval.resolve`, a następnie gateway przekazuje
zatwierdzone żądanie do hosta node.

Dla `host=node` żądania zatwierdzenia zawierają kanoniczny payload `systemRunPlan`. Gateway używa
tego planu jako autorytatywnego kontekstu polecenia/cwd/sesji przy przekazywaniu zatwierdzonych żądań `system.run`.

To ma znaczenie przy opóźnieniach asynchronicznego zatwierdzania:

- ścieżka exec node przygotowuje z góry jeden kanoniczny plan
- rekord zatwierdzenia przechowuje ten plan i jego metadane powiązania
- po zatwierdzeniu końcowe przekazane wywołanie `system.run` ponownie używa zapisanego planu
  zamiast ufać późniejszym zmianom wywołującego
- jeśli wywołujący zmieni `command`, `rawCommand`, `cwd`, `agentId` lub
  `sessionKey` po utworzeniu żądania zatwierdzenia, gateway odrzuci
  przekazane uruchomienie jako niedopasowanie zatwierdzenia

## Polecenia interpreterów/runtime

Uruchomienia interpreterów/runtime oparte na zatwierdzeniach są celowo konserwatywne:

- Dokładny kontekst argv/cwd/env jest zawsze wiązany.
- Bezpośrednie formy skryptów powłoki i bezpośrednich plików runtime są wiązane w trybie best-effort z jedną konkretną migawką lokalnego
  pliku.
- Typowe formy wrapperów menedżerów pakietów, które nadal rozwiązują się do jednego bezpośredniego lokalnego pliku (na przykład
  `pnpm exec`, `pnpm node`, `npm exec`, `npx`), są rozpakowywane przed powiązaniem.
- Jeśli OpenClaw nie może zidentyfikować dokładnie jednego konkretnego lokalnego pliku dla polecenia interpretera/runtime
  (na przykład skrypty pakietów, formy eval, łańcuchy loaderów specyficzne dla runtime lub niejednoznaczne formy
  wieloplikowe), wykonanie oparte na zatwierdzeniu jest odrzucane zamiast twierdzić, że obejmuje semantykę, której
  nie obejmuje.
- Dla takich przepływów pracy preferuj sandboxing, oddzielną granicę hosta albo jawny zaufany
  przepływ allowlist/full, w którym operator akceptuje szerszą semantykę runtime.

Gdy zatwierdzenia są wymagane, narzędzie exec zwraca natychmiast identyfikator zatwierdzenia. Użyj tego identyfikatora, aby
powiązać późniejsze zdarzenia systemowe (`Exec finished` / `Exec denied`). Jeśli żadna decyzja nie nadejdzie przed
upływem limitu czasu, żądanie jest traktowane jako timeout zatwierdzenia i prezentowane jako powód odmowy.

### Zachowanie dostarczania follow-up

Po zakończeniu zatwierdzonego asynchronicznego exec OpenClaw wysyła follow-up jako turę `agent` do tej samej sesji.

- Jeśli istnieje prawidłowy zewnętrzny cel dostarczenia (kanał z możliwością dostarczenia plus cel `to`), dostarczenie follow-up używa tego kanału.
- W przepływach wyłącznie webchat lub sesji wewnętrznych bez zewnętrznego celu, dostarczenie follow-up pozostaje tylko w sesji (`deliver: false`).
- Jeśli wywołujący jawnie zażąda ścisłego dostarczenia zewnętrznego bez możliwego do rozwiązania kanału zewnętrznego, żądanie kończy się błędem `INVALID_REQUEST`.
- Jeśli włączono `bestEffortDeliver` i nie można rozwiązać zewnętrznego kanału, dostarczenie jest obniżane do trybu tylko sesji zamiast kończyć się błędem.

Okno potwierdzenia zawiera:

- polecenie + argumenty
- cwd
- identyfikator agenta
- rozwiązaną ścieżkę pliku wykonywalnego
- host + metadane polityki

Działania:

- **Allow once** → uruchom teraz
- **Always allow** → dodaj do allowlisty + uruchom
- **Deny** → zablokuj

## Przekazywanie zatwierdzeń do kanałów czatu

Możesz przekazywać prompty zatwierdzeń exec do dowolnego kanału czatu (w tym kanałów pluginów) i zatwierdzać
je za pomocą `/approve`. Używa to zwykłego pipeline'u dostarczania wychodzącego.

Konfiguracja:
__OC_I18N_900005__
Odpowiedź na czacie:
__OC_I18N_900006__
Polecenie `/approve` obsługuje zarówno zatwierdzenia exec, jak i zatwierdzenia pluginów. Jeśli identyfikator nie pasuje do oczekującego zatwierdzenia exec, automatycznie sprawdza zamiast tego zatwierdzenia pluginów.

### Przekazywanie zatwierdzeń pluginów

Przekazywanie zatwierdzeń pluginów używa tego samego pipeline'u dostarczania co zatwierdzenia exec, ale ma własną
niezależną konfigurację pod `approvals.plugin`. Włączenie lub wyłączenie jednego nie wpływa na drugie.
__OC_I18N_900007__
Kształt konfiguracji jest identyczny jak `approvals.exec`: `enabled`, `mode`, `agentFilter`,
`sessionFilter` i `targets` działają tak samo.

Kanały obsługujące współdzielone odpowiedzi interaktywne renderują te same przyciski zatwierdzeń zarówno dla zatwierdzeń exec,
jak i pluginów. Kanały bez współdzielonego interaktywnego UI wracają do zwykłego tekstu z instrukcjami `/approve`.

### Zatwierdzenia w tym samym czacie na dowolnym kanale

Gdy żądanie zatwierdzenia exec lub pluginu pochodzi z dostarczalnej powierzchni czatu, ten sam czat
może teraz domyślnie zatwierdzić je przez `/approve`. Dotyczy to kanałów takich jak Slack, Matrix i
Microsoft Teams, oprócz istniejących już przepływów Web UI i UI terminala.

Ta współdzielona ścieżka poleceń tekstowych używa zwykłego modelu auth kanału dla tej konwersacji. Jeśli
czat źródłowy może już wysyłać polecenia i odbierać odpowiedzi, żądania zatwierdzeń nie wymagają już
osobnego natywnego adaptera dostarczania tylko po to, aby pozostawać oczekującymi.

Discord i Telegram również obsługują `/approve` w tym samym czacie, ale te kanały nadal używają
rozwiązanej listy zatwierdzających do autoryzacji, nawet gdy natywne dostarczanie zatwierdzeń jest wyłączone.

Dla Telegram i innych natywnych klientów zatwierdzeń, które wywołują Gateway bezpośrednio,
ten fallback jest celowo ograniczony do błędów typu „approval not found”. Prawdziwa
odmowa/błąd zatwierdzenia exec nie jest po cichu ponawiana jako zatwierdzenie pluginu.

### Natywne dostarczanie zatwierdzeń

Niektóre kanały mogą też działać jako natywni klienci zatwierdzeń. Natywni klienci dodają wiadomości prywatne do zatwierdzających, fanout do czatu źródłowego
i interaktywny UX zatwierdzeń specyficzny dla kanału ponad współdzielonym przepływem `/approve` w tym samym czacie.

Gdy dostępne są natywne karty/przyciski zatwierdzeń, to natywne UI jest podstawową
ścieżką po stronie agenta. Agent nie powinien też powtarzać zduplikowanego zwykłego polecenia czatu
`/approve`, chyba że wynik narzędzia mówi, że zatwierdzenia na czacie są niedostępne lub
ręczne zatwierdzenie jest jedyną pozostałą ścieżką.

Model ogólny:

- polityka host exec nadal decyduje, czy zatwierdzenie exec jest wymagane
- `approvals.exec` kontroluje przekazywanie promptów zatwierdzeń do innych miejsc docelowych czatu
- `channels.<channel>.execApprovals` kontroluje, czy dany kanał działa jako natywny klient zatwierdzeń

Natywni klienci zatwierdzeń automatycznie włączają dostarczanie najpierw do wiadomości prywatnych, gdy wszystkie poniższe warunki są spełnione:

- kanał obsługuje natywne dostarczanie zatwierdzeń
- zatwierdzających można rozwiązać z jawnego `execApprovals.approvers` lub z
  udokumentowanych dla tego kanału źródeł fallbacku
- `channels.<channel>.execApprovals.enabled` nie jest ustawione albo ma wartość `"auto"`

Ustaw `enabled: false`, aby jawnie wyłączyć natywnego klienta zatwierdzeń. Ustaw `enabled: true`, aby wymusić
jego włączenie, gdy zatwierdzający zostaną rozwiązani. Publiczne dostarczanie do czatu źródłowego pozostaje jawne przez
`channels.<channel>.execApprovals.target`.

FAQ: [Dlaczego istnieją dwie konfiguracje zatwierdzeń exec dla zatwierdzeń na czacie?](/help/faq#why-are-there-two-exec-approval-configs-for-chat-approvals)

- Discord: `channels.discord.execApprovals.*`
- Slack: `channels.slack.execApprovals.*`
- Telegram: `channels.telegram.execApprovals.*`

Ci natywni klienci zatwierdzeń dodają routing wiadomości prywatnych i opcjonalny fanout na kanał ponad współdzielonym
przepływem `/approve` w tym samym czacie i współdzielonymi przyciskami zatwierdzeń.

Wspólne zachowanie:

- Slack, Matrix, Microsoft Teams i podobne dostarczalne czaty używają zwykłego modelu auth kanału
  dla `/approve` w tym samym czacie
- gdy natywny klient zatwierdzeń włączy się automatycznie, domyślnym natywnym celem dostarczenia są wiadomości prywatne zatwierdzających
- dla Discord i Telegram tylko rozwiązani zatwierdzający mogą zatwierdzać lub odrzucać
- zatwierdzający Discord mogą być jawni (`execApprovals.approvers`) lub wywnioskowani z `commands.ownerAllowFrom`
- zatwierdzający Telegram mogą być jawni (`execApprovals.approvers`) lub wywnioskowani z istniejącej konfiguracji właściciela (`allowFrom` oraz `defaultTo` dla wiadomości prywatnych, gdzie obsługiwane)
- zatwierdzający Slack mogą być jawni (`execApprovals.approvers`) lub wywnioskowani z `commands.ownerAllowFrom`
- natywne przyciski Slack zachowują rodzaj identyfikatora zatwierdzenia, więc identyfikatory `plugin:` mogą rozwiązywać zatwierdzenia pluginów
  bez drugiej lokalnej warstwy fallbacku Slack
- natywny routing wiadomości prywatnych/kanałów Matrix jest tylko dla exec; zatwierdzenia pluginów Matrix pozostają na współdzielonej
  ścieżce `/approve` w tym samym czacie oraz opcjonalnym przekazywaniu `approvals.plugin`
- żądający nie musi być zatwierdzającym
- czat źródłowy może zatwierdzić bezpośrednio przez `/approve`, gdy ten czat już obsługuje polecenia i odpowiedzi
- natywne przyciski zatwierdzeń Discord kierują według rodzaju identyfikatora zatwierdzenia: identyfikatory `plugin:` trafiają
  bezpośrednio do zatwierdzeń pluginów, wszystko inne do zatwierdzeń exec
- natywne przyciski zatwierdzeń Telegram stosują ten sam ograniczony fallback exec-do-plugin co `/approve`
- gdy natywne `target` włącza dostarczanie do czatu źródłowego, prompty zatwierdzeń zawierają tekst polecenia
- oczekujące zatwierdzenia exec wygasają domyślnie po 30 minutach
- jeśli żadne UI operatora ani skonfigurowany klient zatwierdzeń nie mogą przyjąć żądania, prompt wraca do `askFallback`

Telegram domyślnie kieruje do wiadomości prywatnych zatwierdzających (`target: "dm"`). Możesz przełączyć na `channel` lub `both`, gdy
chcesz, aby prompty zatwierdzeń pojawiały się także w czacie/temacie źródłowym Telegram. W przypadku tematów forum Telegram
OpenClaw zachowuje temat dla promptu zatwierdzenia i follow-up po zatwierdzeniu.

Zobacz:

- [Discord](/channels/discord)
- [Telegram](/channels/telegram)

### Przepływ IPC na macOS
__OC_I18N_900008__
Uwagi dotyczące bezpieczeństwa:

- Tryb gniazda Unix `0600`, token przechowywany w `exec-approvals.json`.
- Kontrola peera z tym samym UID.
- Challenge/response (nonce + token HMAC + hash żądania) + krótki TTL.

## Zdarzenia systemowe

Cykl życia exec jest pokazywany jako wiadomości systemowe:

- `Exec running` (tylko jeśli polecenie przekracza próg powiadomienia o uruchomieniu)
- `Exec finished`
- `Exec denied`

Są one publikowane do sesji agenta po zgłoszeniu zdarzenia przez node.
Zatwierdzenia exec na hoście gatewaya emitują ten sam cykl życia zdarzeń, gdy polecenie się zakończy (i opcjonalnie także podczas działania dłuższego niż próg).
Exec objęte zatwierdzeniem używają ponownie identyfikatora zatwierdzenia jako `runId` w tych wiadomościach, aby ułatwić korelację.

## Zachowanie przy odmowie zatwierdzenia

Gdy asynchroniczne zatwierdzenie exec zostanie odrzucone, OpenClaw uniemożliwia agentowi ponowne użycie
wyjścia z jakiegokolwiek wcześniejszego uruchomienia tego samego polecenia w sesji. Powód odmowy
jest przekazywany z jawną informacją, że żadne wyjście polecenia nie jest dostępne, co powstrzymuje
agenta przed twierdzeniem, że istnieje nowe wyjście, albo przed powtarzaniem odrzuconego polecenia z
nieaktualnymi wynikami z wcześniejszego udanego uruchomienia.

## Konsekwencje

- **full** jest potężne; jeśli to możliwe, preferuj allowlisty.
- **ask** utrzymuje Cię w pętli, a jednocześnie pozwala na szybkie zatwierdzanie.
- Allowlisty per agent zapobiegają przeciekaniu zatwierdzeń jednego agenta do innych.
- Zatwierdzenia dotyczą tylko żądań host exec od **autoryzowanych nadawców**. Nieautoryzowani nadawcy nie mogą wydawać `/exec`.
- `/exec security=full` to wygodna opcja na poziomie sesji dla autoryzowanych operatorów i z założenia pomija zatwierdzenia.
  Aby twardo zablokować host exec, ustaw security zatwierdzeń na `deny` albo zabroń narzędzia `exec` przez politykę narzędzi.

Powiązane:

- [Narzędzie exec](/pl/tools/exec)
- [Tryb elevated](/pl/tools/elevated)
- [Skills](/pl/tools/skills)

## Powiązane

- [Exec](/pl/tools/exec) — narzędzie wykonywania poleceń powłoki
- [Sandboxing](/pl/gateway/sandboxing) — tryby sandboxa i dostęp do workspace
- [Bezpieczeństwo](/pl/gateway/security) — model bezpieczeństwa i utwardzanie
- [Sandbox vs Tool Policy vs Elevated](/pl/gateway/sandbox-vs-tool-policy-vs-elevated) — kiedy używać każdego z nich
