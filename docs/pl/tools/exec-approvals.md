---
read_when:
    - Konfigurowanie zatwierdzeń exec lub list dozwolonych
    - Implementacja UX zatwierdzeń exec w aplikacji macOS
    - Przegląd promptów wyjścia z sandboxa i ich konsekwencji
summary: Zatwierdzenia exec, listy dozwolonych i prompty wyjścia z sandboxa
title: Zatwierdzenia exec
x-i18n:
    generated_at: "2026-04-10T09:45:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: 5f4a2e2f1f3c13a1d1926c9de0720513ea8a74d1ca571dbe74b188d8c560c14c
    source_path: tools/exec-approvals.md
    workflow: 15
---

# Zatwierdzenia exec

Zatwierdzenia exec to **zabezpieczenie aplikacji towarzyszącej / hosta węzła** umożliwiające agentowi działającemu w sandboxie uruchamianie
poleceń na rzeczywistym hoście (`gateway` lub `node`). Traktuj to jak blokadę bezpieczeństwa:
polecenia są dozwolone tylko wtedy, gdy polityka + lista dozwolonych + (opcjonalnie) zgoda użytkownika są ze sobą zgodne.
Zatwierdzenia exec działają **dodatkowo** względem polityki narzędzi i bramkowania elevated (chyba że elevated jest ustawione na `full`, co pomija zatwierdzenia).
Skuteczna polityka jest **bardziej restrykcyjną** z `tools.exec.*` i domyślnych ustawień zatwierdzeń; jeśli pole zatwierdzeń jest pominięte, używana jest wartość z `tools.exec`.
Exec hosta używa także lokalnego stanu zatwierdzeń na tej maszynie. Lokalne ustawienie hosta
`ask: "always"` w `~/.openclaw/exec-approvals.json` powoduje dalsze wyświetlanie promptów, nawet jeśli
sesja lub domyślna konfiguracja żądają `ask: "on-miss"`.
Użyj `openclaw approvals get`, `openclaw approvals get --gateway` lub
`openclaw approvals get --node <id|name|ip>`, aby sprawdzić żądaną politykę,
źródła polityki hosta oraz wynik skuteczny.
Dla maszyny lokalnej `openclaw exec-policy show` pokazuje ten sam scalony widok, a
`openclaw exec-policy set|preset` może zsynchronizować lokalnie żądaną politykę z
lokalnym plikiem zatwierdzeń hosta w jednym kroku. Gdy zakres lokalny żąda `host=node`,
`openclaw exec-policy show` zgłasza ten zakres w czasie działania jako zarządzany przez node, zamiast
udawać, że lokalny plik zatwierdzeń jest skutecznym źródłem prawdy.

Jeśli interfejs aplikacji towarzyszącej **nie jest dostępny**, każde żądanie wymagające promptu jest
rozstrzygane przez **awaryjne zachowanie ask** (domyślnie: odmowa).

Natywne klienckie mechanizmy zatwierdzania na czacie mogą również udostępniać udogodnienia specyficzne dla kanału w oczekującej wiadomości o zatwierdzeniu. Na przykład Matrix może inicjalizować skróty reakcji w prompcie zatwierdzenia (`✅` zezwól raz, `❌` odmów oraz `♾️` zezwól zawsze, gdy dostępne),
jednocześnie pozostawiając polecenia `/approve ...` w wiadomości jako mechanizm zapasowy.

## Gdzie ma to zastosowanie

Zatwierdzenia exec są wymuszane lokalnie na hoście wykonania:

- **host gateway** → proces `openclaw` na maszynie gateway
- **host node** → runner węzła (aplikacja towarzysząca macOS lub bezgłowy host node)

Uwaga dotycząca modelu zaufania:

- Wywołujący uwierzytelnieni względem Gateway są zaufanymi operatorami tego Gateway.
- Sparowane węzły rozszerzają te zaufane uprawnienia operatora na host node.
- Zatwierdzenia exec ograniczają ryzyko przypadkowego wykonania, ale nie stanowią granicy uwierzytelniania per użytkownik.
- Zatwierdzone uruchomienia na hoście node wiążą kanoniczny kontekst wykonania: kanoniczny cwd, dokładne argv, powiązanie env,
  gdy występuje, oraz przypiętą ścieżkę do pliku wykonywalnego, gdy ma to zastosowanie.
- Dla skryptów powłoki i bezpośrednich wywołań plików interpretera/runtime OpenClaw próbuje także powiązać
  jeden konkretny operand lokalnego pliku. Jeśli ten powiązany plik zmieni się po zatwierdzeniu, ale przed wykonaniem,
  uruchomienie zostanie odrzucone zamiast wykonać zmienioną treść.
- To wiązanie plików jest celowo rozwiązaniem opartym na najlepszej próbie, a nie kompletnym modelem semantycznym każdego
  interpretera/runtime i każdej ścieżki ładowania. Jeśli tryb zatwierdzania nie potrafi zidentyfikować dokładnie jednego konkretnego lokalnego
  pliku do powiązania, odmawia utworzenia uruchomienia opartego na zatwierdzeniu, zamiast udawać pełne pokrycie.

Podział na macOS:

- **usługa hosta node** przekazuje `system.run` do **aplikacji macOS** przez lokalne IPC.
- **aplikacja macOS** wymusza zatwierdzenia i wykonuje polecenie w kontekście UI.

## Ustawienia i przechowywanie

Zatwierdzenia są przechowywane w lokalnym pliku JSON na hoście wykonania:

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

## Tryb „YOLO” bez zatwierdzania

Jeśli chcesz, aby exec hosta działał bez promptów zatwierdzenia, musisz otworzyć **obie** warstwy polityki:

- żądaną politykę exec w konfiguracji OpenClaw (`tools.exec.*`)
- lokalną politykę zatwierdzeń hosta w `~/.openclaw/exec-approvals.json`

Jest to teraz domyślne zachowanie hosta, o ile nie zaostrzysz go jawnie:

- `tools.exec.security`: `full` na `gateway`/`node`
- `tools.exec.ask`: `off`
- host `askFallback`: `full`

Ważne rozróżnienie:

- `tools.exec.host=auto` wybiera miejsce wykonywania exec: sandbox, jeśli jest dostępny, w przeciwnym razie gateway.
- YOLO wybiera sposób zatwierdzania exec hosta: `security=full` plus `ask=off`.
- W trybie YOLO OpenClaw nie dodaje osobnej heurystycznej bramki zatwierdzania zaciemniania poleceń ponad skonfigurowaną politykę exec hosta.
- `auto` nie sprawia, że routowanie do gateway staje się darmowym obejściem z sesji sandboxowanej. Żądanie per wywołanie `host=node` jest dozwolone z `auto`, a `host=gateway` jest dozwolone z `auto` tylko wtedy, gdy nie działa żadne środowisko sandbox. Jeśli chcesz stabilnej domyślnej wartości innej niż auto, ustaw `tools.exec.host` lub użyj jawnie `/exec host=...`.

Jeśli chcesz bardziej zachowawczej konfiguracji, ponownie zaostrz dowolną z warstw do `allowlist` / `on-miss`
lub `deny`.

Trwała konfiguracja hosta gateway „nigdy nie pytaj”:

```bash
openclaw config set tools.exec.host gateway
openclaw config set tools.exec.security full
openclaw config set tools.exec.ask off
openclaw gateway restart
```

Następnie ustaw zgodny plik zatwierdzeń hosta:

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

Lokalny skrót do tej samej polityki hosta gateway na bieżącej maszynie:

```bash
openclaw exec-policy preset yolo
```

Ten lokalny skrót aktualizuje oba elementy:

- lokalne `tools.exec.host/security/ask`
- lokalne ustawienia domyślne `~/.openclaw/exec-approvals.json`

Jest on celowo ograniczony tylko do lokalnego środowiska. Jeśli musisz zdalnie zmienić zatwierdzenia hosta gateway lub hosta node,
nadal używaj `openclaw approvals set --gateway` lub
`openclaw approvals set --node <id|name|ip>`.

Dla hosta node zastosuj zamiast tego ten sam plik zatwierdzeń na danym węźle:

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

Ważne ograniczenie tylko lokalne:

- `openclaw exec-policy` nie synchronizuje zatwierdzeń node
- `openclaw exec-policy set --host node` jest odrzucane
- zatwierdzenia exec dla node są pobierane z node w czasie działania, więc aktualizacje kierowane do node muszą używać `openclaw approvals --node ...`

Skrót tylko dla sesji:

- `/exec security=full ask=off` zmienia tylko bieżącą sesję.
- `/elevated full` to skrót awaryjny break-glass, który również pomija zatwierdzenia exec dla tej sesji.

Jeśli plik zatwierdzeń hosta pozostanie bardziej restrykcyjny niż konfiguracja, bardziej restrykcyjna polityka hosta nadal wygrywa.

## Elementy sterujące polityki

### Security (`exec.security`)

- **deny**: blokuje wszystkie żądania exec hosta.
- **allowlist**: zezwala tylko na polecenia znajdujące się na liście dozwolonych.
- **full**: zezwala na wszystko (odpowiednik elevated).

### Ask (`exec.ask`)

- **off**: nigdy nie wyświetla promptu.
- **on-miss**: wyświetla prompt tylko wtedy, gdy lista dozwolonych nie pasuje.
- **always**: wyświetla prompt przy każdym poleceniu.
- trwałe zaufanie `allow-always` nie wyłącza promptów, gdy skuteczny tryb ask to `always`

### Ask fallback (`askFallback`)

Jeśli prompt jest wymagany, ale żaden UI nie jest osiągalny, zachowanie awaryjne określa wynik:

- **deny**: blokuje.
- **allowlist**: zezwala tylko wtedy, gdy lista dozwolonych pasuje.
- **full**: zezwala.

### Wzmocnienie inline interpreter eval (`tools.exec.strictInlineEval`)

Gdy `tools.exec.strictInlineEval=true`, OpenClaw traktuje formy inline code-eval jako wymagające zatwierdzenia, nawet jeśli sam binarny interpreter znajduje się na liście dozwolonych.

Przykłady:

- `python -c`
- `node -e`, `node --eval`, `node -p`
- `ruby -e`
- `perl -e`, `perl -E`
- `php -r`
- `lua -e`
- `osascript -e`

To mechanizm defense-in-depth dla loaderów interpreterów, które nie mapują się czysto na jeden stabilny operand pliku. W trybie ścisłym:

- te polecenia nadal wymagają jawnego zatwierdzenia;
- `allow-always` nie utrwala dla nich automatycznie nowych wpisów listy dozwolonych.

## Lista dozwolonych (per agent)

Listy dozwolonych są **per agent**. Jeśli istnieje wielu agentów, przełącz agenta,
którego edytujesz, w aplikacji macOS. Wzorce to **dopasowania glob bez rozróżniania wielkości liter**.
Wzorce powinny rozwiązywać się do **ścieżek binarnych** (wpisy zawierające tylko basename są ignorowane).
Starsze wpisy `agents.default` są migrowane do `agents.main` podczas ładowania.
Łańcuchy powłoki, takie jak `echo ok && pwd`, nadal wymagają, aby każdy segment najwyższego poziomu spełniał reguły listy dozwolonych.

Przykłady:

- `~/Projects/**/bin/peekaboo`
- `~/.local/bin/*`
- `/opt/homebrew/bin/rg`

Każdy wpis listy dozwolonych śledzi:

- **id** stabilny UUID używany jako tożsamość w UI (opcjonalnie)
- **ostatnie użycie** znacznik czasu
- **ostatnio użyte polecenie**
- **ostatnio rozpoznana ścieżka**

## Automatyczne zezwalanie na CLI Skills

Gdy **Auto-allow skill CLIs** jest włączone, pliki wykonywalne wskazywane przez znane Skills
są traktowane jako znajdujące się na liście dozwolonych na węzłach (macOS node lub bezgłowy host node). Wykorzystuje to
`skills.bins` przez Gateway RPC do pobrania listy binariów Skills. Wyłącz tę opcję, jeśli chcesz stosować ścisłe ręczne listy dozwolonych.

Ważne uwagi dotyczące zaufania:

- To **niejawna wygodna lista dozwolonych**, oddzielona od ręcznych wpisów listy dozwolonych opartych na ścieżkach.
- Jest przeznaczona dla zaufanych środowisk operatora, w których Gateway i node znajdują się w tej samej granicy zaufania.
- Jeśli potrzebujesz ściśle jawnego zaufania, pozostaw `autoAllowSkills: false` i używaj wyłącznie ręcznych wpisów ścieżek na liście dozwolonych.

## Safe bins (tylko stdin)

`tools.exec.safeBins` definiuje małą listę binariów **tylko stdin** (na przykład `cut`),
które mogą działać w trybie allowlist **bez** jawnych wpisów na liście dozwolonych. Safe bins odrzucają
pozycyjne argumenty plików i tokeny przypominające ścieżki, więc mogą działać wyłącznie na strumieniu wejściowym.
Traktuj to jako wąską szybką ścieżkę dla filtrów strumienia, a nie ogólną listę zaufania.
**Nie** dodawaj interpreterów ani binariów runtime (na przykład `python3`, `node`, `ruby`, `bash`, `sh`, `zsh`) do `safeBins`.
Jeśli polecenie z założenia może wykonywać kod, uruchamiać podpolecenia lub odczytywać pliki, preferuj jawne wpisy listy dozwolonych i pozostaw włączone prompty zatwierdzania.
Niestandardowe safe bins muszą definiować jawny profil w `tools.exec.safeBinProfiles.<bin>`.
Walidacja jest deterministyczna wyłącznie na podstawie kształtu argv (bez sprawdzania istnienia plików w systemie plików hosta), co
zapobiega zachowaniu typu oracle istnienia pliku wynikającemu z różnic między allow/deny.
Opcje zorientowane na pliki są odrzucane dla domyślnych safe bins (na przykład `sort -o`, `sort --output`,
`sort --files0-from`, `sort --compress-program`, `sort --random-source`,
`sort --temporary-directory`/`-T`, `wc --files0-from`, `jq -f/--from-file`,
`grep -f/--file`).
Safe bins wymuszają także jawną politykę flag per binarium dla opcji, które naruszają zachowanie ograniczone do stdin
(na przykład `sort -o/--output/--compress-program` i flagi rekurencyjne grep).
Długie opcje są walidowane w trybie safe-bin zgodnie z zasadą fail-closed: nieznane flagi i niejednoznaczne
skróty są odrzucane.
Flagi odrzucane przez profil safe-bin:

[//]: # "SAFE_BIN_DENIED_FLAGS:START"

- `grep`: `--dereference-recursive`, `--directories`, `--exclude-from`, `--file`, `--recursive`, `-R`, `-d`, `-f`, `-r`
- `jq`: `--argfile`, `--from-file`, `--library-path`, `--rawfile`, `--slurpfile`, `-L`, `-f`
- `sort`: `--compress-program`, `--files0-from`, `--output`, `--random-source`, `--temporary-directory`, `-T`, `-o`
- `wc`: `--files0-from`

[//]: # "SAFE_BIN_DENIED_FLAGS:END"

Safe bins wymuszają także traktowanie tokenów argv jako **tekstu dosłownego** podczas wykonania (bez rozwijania globów
i bez rozwijania `$VARS`) dla segmentów tylko stdin, więc wzorce takie jak `*` lub `$HOME/...` nie mogą zostać
użyte do przemycania odczytów plików.
Safe bins muszą również rozwiązywać się z zaufanych katalogów binarnych (domyślne katalogi systemowe plus opcjonalne
`tools.exec.safeBinTrustedDirs`). Wpisy `PATH` nigdy nie są automatycznie uznawane za zaufane.
Domyślne zaufane katalogi safe-bin są celowo minimalne: `/bin`, `/usr/bin`.
Jeśli Twój plik wykonywalny safe-bin znajduje się w ścieżkach menedżera pakietów/użytkownika (na przykład
`/opt/homebrew/bin`, `/usr/local/bin`, `/opt/local/bin`, `/snap/bin`), dodaj je jawnie
do `tools.exec.safeBinTrustedDirs`.
Łączenie poleceń powłoki i przekierowania nie są automatycznie dozwolone w trybie allowlist.

Łączenie poleceń powłoki (`&&`, `||`, `;`) jest dozwolone, gdy każdy segment najwyższego poziomu spełnia reguły allowlist
(w tym safe bins lub automatyczne zezwalanie na Skills). Przekierowania pozostają nieobsługiwane w trybie allowlist.
Podstawianie poleceń (`$()` / backticks) jest odrzucane podczas parsowania allowlist, również wewnątrz
podwójnych cudzysłowów; użyj pojedynczych cudzysłowów, jeśli potrzebujesz dosłownego tekstu `$()`.
W zatwierdzeniach aplikacji towarzyszącej macOS surowy tekst powłoki zawierający składnię sterowania powłoką lub rozwijania
(`&&`, `||`, `;`, `|`, `` ` ``, `$`, `<`, `>`, `(`, `)`) jest traktowany jako brak dopasowania allowlist, chyba że
sam binarny plik powłoki znajduje się na liście dozwolonych.
Dla wrapperów powłoki (`bash|sh|zsh ... -c/-lc`) nadpisania env w zakresie żądania są redukowane do
małej jawnej listy dozwolonych (`TERM`, `LANG`, `LC_*`, `COLORTERM`, `NO_COLOR`, `FORCE_COLOR`).
W przypadku decyzji allow-always w trybie allowlist znane wrappery dyspozytorskie
(`env`, `nice`, `nohup`, `stdbuf`, `timeout`) utrwalają ścieżki wewnętrznych plików wykonywalnych zamiast ścieżek wrapperów. Multipleksery powłoki (`busybox`, `toybox`) są również rozwijane dla apletów powłoki (`sh`, `ash`,
itp.), tak aby utrwalać wewnętrzne pliki wykonywalne zamiast binariów multipleksera. Jeśli wrapper lub
multiplekser nie może zostać bezpiecznie rozwinięty, żaden wpis allowlist nie jest utrwalany automatycznie.
Jeśli umieszczasz na liście dozwolonych interpretery takie jak `python3` lub `node`, preferuj `tools.exec.strictInlineEval=true`, aby inline eval nadal wymagało jawnego zatwierdzenia. W trybie ścisłym `allow-always` nadal może utrwalać nieszkodliwe wywołania interpretera/skryptu, ale nośniki inline-eval nie są utrwalane automatycznie.

Domyślne safe bins:

[//]: # "SAFE_BIN_DEFAULTS:START"

`cut`, `uniq`, `head`, `tail`, `tr`, `wc`

[//]: # "SAFE_BIN_DEFAULTS:END"

`grep` i `sort` nie znajdują się na liście domyślnej. Jeśli jawnie je włączysz, zachowaj jawne wpisy allowlist dla
ich przepływów pracy innych niż stdin.
Dla `grep` w trybie safe-bin podawaj wzorzec za pomocą `-e`/`--regexp`; forma wzorca pozycyjnego jest
odrzucana, aby operandy plików nie mogły być przemycane jako niejednoznaczne argumenty pozycyjne.

### Safe bins a allowlist

| Temat            | `tools.exec.safeBins`                                  | Allowlist (`exec-approvals.json`)                            |
| ---------------- | ------------------------------------------------------ | ------------------------------------------------------------ |
| Cel              | Automatyczne zezwalanie na wąskie filtry stdin         | Jawne zaufanie określonym plikom wykonywalnym                |
| Typ dopasowania  | Nazwa pliku wykonywalnego + polityka argv safe-bin     | Wzorzec glob dopasowujący rozwiązaną ścieżkę pliku wykonywalnego |
| Zakres argumentów | Ograniczony przez profil safe-bin i reguły tokenów dosłownych | Tylko dopasowanie ścieżki; argumenty są poza tym Twoją odpowiedzialnością |
| Typowe przykłady | `head`, `tail`, `tr`, `wc`                             | `jq`, `python3`, `node`, `ffmpeg`, niestandardowe CLI        |
| Najlepsze zastosowanie | Niskiego ryzyka przekształcenia tekstu w potokach | Dowolne narzędzie o szerszym zachowaniu lub skutkach ubocznych |

Lokalizacja konfiguracji:

- `safeBins` pochodzi z konfiguracji (`tools.exec.safeBins` lub per agent `agents.list[].tools.exec.safeBins`).
- `safeBinTrustedDirs` pochodzi z konfiguracji (`tools.exec.safeBinTrustedDirs` lub per agent `agents.list[].tools.exec.safeBinTrustedDirs`).
- `safeBinProfiles` pochodzi z konfiguracji (`tools.exec.safeBinProfiles` lub per agent `agents.list[].tools.exec.safeBinProfiles`). Klucze profili per agent nadpisują klucze globalne.
- wpisy allowlist znajdują się w lokalnym dla hosta pliku `~/.openclaw/exec-approvals.json` w `agents.<id>.allowlist` (lub przez Control UI / `openclaw approvals allowlist ...`).
- `openclaw security audit` ostrzega za pomocą `tools.exec.safe_bins_interpreter_unprofiled`, gdy binaria interpretera/runtime pojawiają się w `safeBins` bez jawnych profili.
- `openclaw doctor --fix` może utworzyć brakujące niestandardowe wpisy `safeBinProfiles.<bin>` jako `{}` (następnie przejrzyj je i zaostrz). Binaria interpretera/runtime nie są tworzone automatycznie.

Przykład profilu niestandardowego:
__OC_I18N_900005__
Jeśli jawnie włączysz `jq` do `safeBins`, OpenClaw nadal odrzuci wbudowane `env` w trybie safe-bin,
tak aby `jq -n env` nie mogło zrzucić środowiska procesu hosta bez jawnej ścieżki allowlist
lub promptu zatwierdzenia.

## Edycja w Control UI

Użyj karty **Control UI → Nodes → Exec approvals**, aby edytować ustawienia domyślne, nadpisania
per agent i listy dozwolonych. Wybierz zakres (Defaults lub agent), dostosuj politykę,
dodaj/usuń wzorce allowlist, a następnie kliknij **Save**. UI pokazuje metadane **ostatniego użycia**
dla każdego wzorca, dzięki czemu można utrzymywać porządek na liście.

Selektor celu wybiera **Gateway** (lokalne zatwierdzenia) lub **Node**. Węzły
muszą ogłaszać `system.execApprovals.get/set` (aplikacja macOS lub bezgłowy host node).
Jeśli węzeł nie ogłasza jeszcze zatwierdzeń exec, edytuj bezpośrednio jego lokalny plik
`~/.openclaw/exec-approvals.json`.

CLI: `openclaw approvals` obsługuje edycję gateway lub node (zobacz [Approvals CLI](/cli/approvals)).

## Przepływ zatwierdzania

Gdy prompt jest wymagany, gateway rozsyła `exec.approval.requested` do klientów operatora.
Control UI i aplikacja macOS rozstrzygają go przez `exec.approval.resolve`, po czym gateway przekazuje
zatwierdzone żądanie do hosta node.

Dla `host=node` żądania zatwierdzenia zawierają kanoniczny ładunek `systemRunPlan`. Gateway używa
tego planu jako autorytatywnego kontekstu polecenia/cwd/sesji podczas przekazywania zatwierdzonych żądań
`system.run`.

Ma to znaczenie przy opóźnieniach asynchronicznego zatwierdzania:

- ścieżka node exec przygotowuje z góry jeden kanoniczny plan
- rekord zatwierdzenia przechowuje ten plan i jego metadane powiązania
- po zatwierdzeniu końcowe przekazane wywołanie `system.run` ponownie używa zapisanego planu
  zamiast ufać późniejszym zmianom wywołującego
- jeśli wywołujący zmieni `command`, `rawCommand`, `cwd`, `agentId` lub
  `sessionKey` po utworzeniu żądania zatwierdzenia, gateway odrzuci przekazane
  uruchomienie jako niedopasowanie zatwierdzenia

## Polecenia interpretera/runtime

Uruchomienia interpretera/runtime oparte na zatwierdzeniu są celowo konserwatywne:

- Dokładny kontekst argv/cwd/env jest zawsze powiązany.
- Bezpośrednie formy skryptów powłoki i bezpośrednich plików runtime są, zgodnie z najlepszą próbą, powiązywane z jedną konkretną migawką pliku lokalnego.
- Typowe formy wrapperów menedżera pakietów, które nadal rozwiązują się do jednego bezpośredniego pliku lokalnego (na przykład
  `pnpm exec`, `pnpm node`, `npm exec`, `npx`), są rozwijane przed powiązaniem.
- Jeśli OpenClaw nie potrafi zidentyfikować dokładnie jednego konkretnego pliku lokalnego dla polecenia interpretera/runtime
  (na przykład skrypty pakietów, formy eval, łańcuchy loaderów specyficzne dla runtime lub niejednoznaczne formy
  wieloplikowe), wykonanie oparte na zatwierdzeniu zostaje odrzucone zamiast deklarować pokrycie semantyczne, którego faktycznie
  nie ma.
- Dla takich przepływów pracy preferuj sandboxing, osobną granicę hosta lub jawny zaufany
  przepływ allowlist/full, w którym operator akceptuje szerszą semantykę runtime.

Gdy zatwierdzenia są wymagane, narzędzie exec zwraca natychmiast identyfikator zatwierdzenia. Użyj tego identyfikatora do
skorelowania późniejszych zdarzeń systemowych (`Exec finished` / `Exec denied`). Jeśli przed upływem limitu czasu nie nadejdzie
żadna decyzja, żądanie jest traktowane jako przekroczenie czasu zatwierdzenia i prezentowane jako powód odmowy.

### Zachowanie dostarczania follow-up

Po zakończeniu zatwierdzonego asynchronicznego exec OpenClaw wysyła follow-upowy obrót `agent` do tej samej sesji.

- Jeśli istnieje prawidłowy zewnętrzny cel dostarczenia (kanał dostarczalny plus docelowe `to`), dostarczenie follow-up używa tego kanału.
- W przepływach wyłącznie webchat lub sesjach wewnętrznych bez zewnętrznego celu dostarczenie follow-up pozostaje tylko w sesji (`deliver: false`).
- Jeśli wywołujący jawnie żąda ścisłego dostarczenia zewnętrznego, ale nie można rozwiązać żadnego zewnętrznego kanału, żądanie kończy się błędem `INVALID_REQUEST`.
- Jeśli włączono `bestEffortDeliver` i nie można rozwiązać zewnętrznego kanału, dostarczenie zostaje obniżone do trybu tylko sesyjnego zamiast zakończyć się błędem.

Okno potwierdzenia zawiera:

- polecenie + argumenty
- cwd
- id agenta
- rozwiązaną ścieżkę pliku wykonywalnego
- metadane hosta + polityki

Działania:

- **Allow once** → uruchom teraz
- **Always allow** → dodaj do allowlist + uruchom
- **Deny** → zablokuj

## Przekazywanie zatwierdzeń do kanałów czatu

Możesz przekazywać prompty zatwierdzeń exec do dowolnego kanału czatu (w tym kanałów pluginów) i zatwierdzać
je za pomocą `/approve`. Używa to zwykłego potoku dostarczania wychodzącego.

Konfiguracja:
__OC_I18N_900006__
Odpowiedź na czacie:
__OC_I18N_900007__
Polecenie `/approve` obsługuje zarówno zatwierdzenia exec, jak i zatwierdzenia pluginów. Jeśli identyfikator nie pasuje do oczekującego zatwierdzenia exec, automatycznie sprawdza zamiast tego zatwierdzenia pluginów.

### Przekazywanie zatwierdzeń pluginów

Przekazywanie zatwierdzeń pluginów używa tego samego potoku dostarczania co zatwierdzenia exec, ale ma własną
niezależną konfigurację w `approvals.plugin`. Włączenie lub wyłączenie jednego nie wpływa na drugie.
__OC_I18N_900008__
Kształt konfiguracji jest identyczny jak w `approvals.exec`: `enabled`, `mode`, `agentFilter`,
`sessionFilter` i `targets` działają tak samo.

Kanały obsługujące współdzielone interaktywne odpowiedzi renderują te same przyciski zatwierdzania zarówno dla zatwierdzeń exec, jak i
pluginów. Kanały bez współdzielonego interaktywnego UI wracają do zwykłego tekstu z instrukcjami `/approve`.

### Zatwierdzenia w tym samym czacie na dowolnym kanale

Gdy żądanie zatwierdzenia exec lub pluginu pochodzi z dostarczalnej powierzchni czatu, ten sam czat
może je teraz domyślnie zatwierdzić za pomocą `/approve`. Dotyczy to kanałów takich jak Slack, Matrix i
Microsoft Teams, oprócz istniejących przepływów Web UI i terminal UI.

Ta współdzielona ścieżka poleceń tekstowych używa normalnego modelu uwierzytelniania kanału dla danej rozmowy. Jeśli
czat źródłowy może już wysyłać polecenia i odbierać odpowiedzi, żądania zatwierdzenia nie potrzebują już
osobnego natywnego adaptera dostarczania tylko po to, by pozostać w stanie oczekiwania.

Discord i Telegram również obsługują `/approve` w tym samym czacie, ale te kanały nadal używają
swojej rozpoznanej listy zatwierdzających do autoryzacji, nawet gdy natywne dostarczanie zatwierdzeń jest wyłączone.

Dla Telegrama i innych natywnych klientów zatwierdzeń, które wywołują Gateway bezpośrednio,
to zachowanie zapasowe jest celowo ograniczone do błędów typu „nie znaleziono zatwierdzenia”. Rzeczywista
odmowa/błąd zatwierdzenia exec nie powoduje cichego ponownego sprawdzenia jako zatwierdzenie pluginu.

### Natywne dostarczanie zatwierdzeń

Niektóre kanały mogą również działać jako natywni klienci zatwierdzeń. Natywni klienci dodają DM-y zatwierdzających, fanout do czatu źródłowego
oraz interaktywny UX zatwierdzania specyficzny dla kanału ponad współdzielony przepływ `/approve`
w tym samym czacie.

Gdy dostępne są natywne karty/przyciski zatwierdzania, to natywne UI jest podstawową
ścieżką widoczną dla agenta. Agent nie powinien również powielać zwykłego polecenia czatu
`/approve`, chyba że wynik narzędzia wskazuje, że zatwierdzenia na czacie są niedostępne lub
jedyną pozostałą ścieżką jest zatwierdzenie ręczne.

Model ogólny:

- polityka hosta exec nadal decyduje, czy zatwierdzenie exec jest wymagane
- `approvals.exec` kontroluje przekazywanie promptów zatwierdzeń do innych miejsc docelowych czatu
- `channels.<channel>.execApprovals` kontroluje, czy dany kanał działa jako natywny klient zatwierdzeń

Natywni klienci zatwierdzeń automatycznie włączają dostarczanie z priorytetem DM, gdy spełnione są wszystkie poniższe warunki:

- kanał obsługuje natywne dostarczanie zatwierdzeń
- osoby zatwierdzające można rozpoznać na podstawie jawnego `execApprovals.approvers` lub
  udokumentowanych źródeł zapasowych tego kanału
- `channels.<channel>.execApprovals.enabled` nie jest ustawione lub ma wartość `"auto"`

Ustaw `enabled: false`, aby jawnie wyłączyć natywnego klienta zatwierdzeń. Ustaw `enabled: true`, aby wymusić
jego włączenie, gdy uda się rozpoznać osoby zatwierdzające. Publiczne dostarczanie do czatu źródłowego pozostaje
jawnie kontrolowane przez `channels.<channel>.execApprovals.target`.

FAQ: [Dlaczego istnieją dwie konfiguracje zatwierdzeń exec dla zatwierdzeń na czacie?](/help/faq#why-are-there-two-exec-approval-configs-for-chat-approvals)

- Discord: `channels.discord.execApprovals.*`
- Slack: `channels.slack.execApprovals.*`
- Telegram: `channels.telegram.execApprovals.*`

Ci natywni klienci zatwierdzeń dodają routowanie do DM-ów i opcjonalny fanout do kanału ponad współdzielony
przepływ `/approve` w tym samym czacie oraz współdzielone przyciski zatwierdzeń.

Wspólne zachowanie:

- Slack, Matrix, Microsoft Teams i podobne dostarczalne czaty używają normalnego modelu uwierzytelniania kanału
  dla `/approve` w tym samym czacie
- gdy natywny klient zatwierdzeń włącza się automatycznie, domyślnym celem natywnego dostarczania są DM-y osób zatwierdzających
- dla Discorda i Telegrama tylko rozpoznane osoby zatwierdzające mogą zatwierdzać lub odmawiać
- osoby zatwierdzające w Discord mogą być jawne (`execApprovals.approvers`) lub wywnioskowane z `commands.ownerAllowFrom`
- osoby zatwierdzające w Telegramie mogą być jawne (`execApprovals.approvers`) lub wywnioskowane z istniejącej konfiguracji ownera (`allowFrom` oraz `defaultTo` dla wiadomości bezpośrednich tam, gdzie jest obsługiwane)
- osoby zatwierdzające w Slack mogą być jawne (`execApprovals.approvers`) lub wywnioskowane z `commands.ownerAllowFrom`
- natywne przyciski Slack zachowują rodzaj id zatwierdzenia, więc identyfikatory `plugin:` mogą rozwiązywać zatwierdzenia pluginów
  bez drugiej lokalnej warstwy zapasowej specyficznej dla Slacka
- natywne routowanie DM/kanału i skróty reakcji w Matrix obsługują zarówno zatwierdzenia exec, jak i pluginów;
  autoryzacja pluginów nadal pochodzi z `channels.matrix.dm.allowFrom`
- zgłaszający nie musi być osobą zatwierdzającą
- czat źródłowy może zatwierdzać bezpośrednio za pomocą `/approve`, gdy ten czat już obsługuje polecenia i odpowiedzi
- natywne przyciski zatwierdzeń Discord routują według rodzaju id zatwierdzenia: identyfikatory `plugin:` trafiają
  bezpośrednio do zatwierdzeń pluginów, a wszystko inne do zatwierdzeń exec
- natywne przyciski zatwierdzeń Telegram stosują to samo ograniczone zachowanie zapasowe exec-to-plugin co `/approve`
- gdy natywne `target` włącza dostarczanie do czatu źródłowego, prompty zatwierdzeń zawierają tekst polecenia
- oczekujące zatwierdzenia exec wygasają domyślnie po 30 minutach
- jeśli żaden UI operatora ani skonfigurowany klient zatwierdzeń nie może przyjąć żądania, prompt wraca do `askFallback`

Telegram domyślnie kieruje do DM-ów osób zatwierdzających (`target: "dm"`). Możesz przełączyć na `channel` lub `both`, gdy
chcesz, aby prompty zatwierdzeń pojawiały się również w źródłowym czacie/wątku Telegrama. Dla tematów forum Telegrama
OpenClaw zachowuje temat dla promptu zatwierdzenia oraz follow-up po zatwierdzeniu.

Zobacz:

- [Discord](/channels/discord)
- [Telegram](/channels/telegram)

### Przepływ IPC na macOS
__OC_I18N_900009__
Uwagi dotyczące bezpieczeństwa:

- Tryb gniazda Unix `0600`, token przechowywany w `exec-approvals.json`.
- Sprawdzanie peera z tym samym UID.
- Challenge/response (nonce + token HMAC + hash żądania) + krótki TTL.

## Zdarzenia systemowe

Cykl życia exec jest ujawniany jako komunikaty systemowe:

- `Exec running` (tylko jeśli polecenie przekroczy próg powiadomienia o wykonywaniu)
- `Exec finished`
- `Exec denied`

Są one publikowane do sesji agenta po zgłoszeniu zdarzenia przez node.
Zatwierdzenia exec na hoście gateway emitują te same zdarzenia cyklu życia, gdy polecenie się zakończy (oraz opcjonalnie, gdy działa dłużej niż próg).
Exec objęte zatwierdzeniem używają ponownie identyfikatora zatwierdzenia jako `runId` w tych komunikatach, co ułatwia korelację.

## Zachowanie przy odmowie zatwierdzenia

Gdy asynchroniczne zatwierdzenie exec zostaje odrzucone, OpenClaw uniemożliwia agentowi ponowne użycie
wyników z wcześniejszego uruchomienia tego samego polecenia w sesji. Powód odmowy
jest przekazywany wraz z jawną wskazówką, że żadne dane wyjściowe polecenia nie są dostępne, co powstrzymuje
agenta przed twierdzeniem, że istnieją nowe dane wyjściowe, lub przed powtarzaniem odrzuconego polecenia z
nieaktualnymi wynikami z wcześniejszego pomyślnego uruchomienia.

## Konsekwencje

- **full** ma szerokie uprawnienia; gdy to możliwe, preferuj listy dozwolonych.
- **ask** pozwala Ci zachować kontrolę, a jednocześnie umożliwia szybkie zatwierdzanie.
- Listy dozwolonych per agent zapobiegają przenikaniu zatwierdzeń jednego agenta do innych.
- Zatwierdzenia mają zastosowanie tylko do żądań exec hosta od **autoryzowanych nadawców**. Nieautoryzowani nadawcy nie mogą wydawać `/exec`.
- `/exec security=full` to wygodne ustawienie na poziomie sesji dla autoryzowanych operatorów i zgodnie z założeniem pomija zatwierdzenia.
  Aby całkowicie zablokować exec hosta, ustaw security zatwierdzeń na `deny` lub zablokuj narzędzie `exec` za pomocą polityki narzędzi.

Powiązane:

- [Exec tool](/pl/tools/exec)
- [Elevated mode](/pl/tools/elevated)
- [Skills](/pl/tools/skills)

## Powiązane

- [Exec](/pl/tools/exec) — narzędzie do wykonywania poleceń powłoki
- [Sandboxing](/pl/gateway/sandboxing) — tryby sandboxa i dostęp do obszaru roboczego
- [Security](/pl/gateway/security) — model bezpieczeństwa i utwardzanie
- [Sandbox vs Tool Policy vs Elevated](/pl/gateway/sandbox-vs-tool-policy-vs-elevated) — kiedy używać każdego z nich
