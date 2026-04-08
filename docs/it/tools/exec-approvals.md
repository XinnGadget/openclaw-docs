---
read_when:
    - Configurazione di approvazioni exec o allowlist
    - Implementazione della UX delle approvazioni exec nell'app macOS
    - Revisione dei prompt di uscita dalla sandbox e delle relative implicazioni
summary: Approvazioni exec, allowlist e prompt di uscita dalla sandbox
title: Approvazioni exec
x-i18n:
    generated_at: "2026-04-08T02:19:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6041929185bab051ad873cc4822288cb7d6f0470e19e7ae7a16b70f76dfc2cd9
    source_path: tools/exec-approvals.md
    workflow: 15
---

# Approvazioni exec

Le approvazioni exec sono il **guardrail dell'app companion / host del nodo** per consentire a un agente in sandbox di eseguire
comandi su un host reale (`gateway` o `node`). Considerale come un interblocco di sicurezza:
i comandi sono consentiti solo quando policy + allowlist + (eventuale) approvazione dell'utente concordano tutte.
Le approvazioni exec sono **aggiuntive** rispetto alla tool policy e al gating elevato (a meno che elevated non sia impostato su `full`, che salta le approvazioni).
La policy effettiva è la **più restrittiva** tra `tools.exec.*` e i valori predefiniti delle approvazioni; se un campo delle approvazioni viene omesso, viene usato il valore di `tools.exec`.
L'exec host usa anche lo stato locale delle approvazioni su quella macchina. Un valore host-local
`ask: "always"` in `~/.openclaw/exec-approvals.json` continua a richiedere prompt anche se
i valori predefiniti della sessione o della configurazione richiedono `ask: "on-miss"`.
Usa `openclaw approvals get`, `openclaw approvals get --gateway` oppure
`openclaw approvals get --node <id|name|ip>` per ispezionare la policy richiesta,
le fonti della policy host e il risultato effettivo.

Se l'interfaccia dell'app companion **non è disponibile**, qualsiasi richiesta che richiede un prompt viene
risolta tramite il **fallback ask** (predefinito: deny).

I client di approvazione chat nativi possono anche esporre affordance specifiche del canale sul
messaggio di approvazione in sospeso. Ad esempio, Matrix può precompilare scorciatoie a reazione sul
prompt di approvazione (`✅` consenti una volta, `❌` nega e `♾️` consenti sempre quando disponibile)
lasciando comunque i comandi `/approve ...` nel messaggio come fallback.

## Dove si applica

Le approvazioni exec sono applicate localmente sull'host di esecuzione:

- **gateway host** → processo `openclaw` sulla macchina gateway
- **node host** → runner del nodo (app companion macOS o host nodo headless)

Nota sul modello di fiducia:

- I chiamanti autenticati al gateway sono operator trusted per quel gateway.
- I nodi associati estendono questa capacità di operatore trusted all'host del nodo.
- Le approvazioni exec riducono il rischio di esecuzione accidentale, ma non sono un confine di auth per utente.
- Le esecuzioni approvate sull'host del nodo vincolano il contesto di esecuzione canonico: `cwd` canonico, `argv` esatto, binding dell'env
  quando presente e path dell'eseguibile fissato quando applicabile.
- Per script shell e invocazioni dirette di file interpreter/runtime, OpenClaw prova anche a vincolare
  un singolo operando file locale concreto. Se quel file vincolato cambia dopo l'approvazione ma prima dell'esecuzione,
  l'esecuzione viene negata invece di eseguire contenuto modificato.
- Questo binding dei file è intenzionalmente best-effort, non un modello semantico completo di ogni
  percorso di caricamento di interpreter/runtime. Se la modalità di approvazione non riesce a identificare esattamente un file locale concreto
  da vincolare, rifiuta di emettere un'esecuzione supportata da approvazione invece di fingere una copertura completa.

Suddivisione macOS:

- Il **servizio host del nodo** inoltra `system.run` alla **app macOS** tramite IPC locale.
- La **app macOS** applica le approvazioni + esegue il comando nel contesto UI.

## Impostazioni e archiviazione

Le approvazioni vivono in un file JSON locale sull'host di esecuzione:

`~/.openclaw/exec-approvals.json`

Schema di esempio:

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

## Modalità "YOLO" senza approvazione

Se vuoi che l'exec host venga eseguito senza prompt di approvazione, devi aprire **entrambi** i livelli di policy:

- policy exec richiesta nella configurazione di OpenClaw (`tools.exec.*`)
- policy locale delle approvazioni host in `~/.openclaw/exec-approvals.json`

Questo ora è il comportamento host predefinito a meno che tu non lo restringa esplicitamente:

- `tools.exec.security`: `full` su `gateway`/`node`
- `tools.exec.ask`: `off`
- host `askFallback`: `full`

Distinzione importante:

- `tools.exec.host=auto` sceglie dove eseguire exec: nella sandbox quando disponibile, altrimenti sul gateway.
- YOLO sceglie come viene approvato l'exec host: `security=full` più `ask=off`.
- In modalità YOLO, OpenClaw non aggiunge un gate separato di approvazione euristica per l'offuscamento dei comandi sopra la policy exec host configurata.
- `auto` non rende il routing gateway una sovrascrittura libera da una sessione in sandbox. Una richiesta per chiamata `host=node` è consentita da `auto`, e `host=gateway` è consentito da `auto` solo quando non è attivo alcun runtime sandbox. Se vuoi un valore predefinito stabile non-auto, imposta `tools.exec.host` o usa esplicitamente `/exec host=...`.

Se vuoi una configurazione più conservativa, restringi di nuovo uno dei due livelli a `allowlist` / `on-miss`
oppure `deny`.

Configurazione persistente gateway-host "non chiedere mai":

```bash
openclaw config set tools.exec.host gateway
openclaw config set tools.exec.security full
openclaw config set tools.exec.ask off
openclaw gateway restart
```

Quindi imposta il file delle approvazioni host in modo corrispondente:

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

Per un host nodo, applica invece lo stesso file delle approvazioni su quel nodo:

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

Scorciatoia solo sessione:

- `/exec security=full ask=off` cambia solo la sessione corrente.
- `/elevated full` è una scorciatoia break-glass che salta anche le approvazioni exec per quella sessione.

Se il file delle approvazioni host resta più restrittivo della configurazione, la policy host più restrittiva continua a prevalere.

## Manopole della policy

### Security (`exec.security`)

- **deny**: blocca tutte le richieste exec host.
- **allowlist**: consente solo i comandi presenti nell'allowlist.
- **full**: consente tutto (equivalente a elevated).

### Ask (`exec.ask`)

- **off**: non chiedere mai.
- **on-miss**: chiedi solo quando l'allowlist non corrisponde.
- **always**: chiedi per ogni comando.
- la fiducia persistente `allow-always` non sopprime i prompt quando la modalità ask effettiva è `always`

### Ask fallback (`askFallback`)

Se è richiesto un prompt ma nessuna UI è raggiungibile, fallback decide:

- **deny**: blocca.
- **allowlist**: consente solo se l'allowlist corrisponde.
- **full**: consente.

### Hardening dell'eval inline dell'interpreter (`tools.exec.strictInlineEval`)

Quando `tools.exec.strictInlineEval=true`, OpenClaw tratta le forme di eval inline del codice come solo-approvazione anche se il binario dell'interpreter stesso è nell'allowlist.

Esempi:

- `python -c`
- `node -e`, `node --eval`, `node -p`
- `ruby -e`
- `perl -e`, `perl -E`
- `php -r`
- `lua -e`
- `osascript -e`

Questo è un meccanismo di difesa in profondità per loader di interpreter che non si mappano in modo pulito a un singolo operando file stabile. In modalità strict:

- questi comandi richiedono comunque approvazione esplicita;
- `allow-always` non persiste automaticamente nuove voci di allowlist per essi.

## Allowlist (per agente)

Le allowlist sono **per agente**. Se esistono più agenti, cambia l'agente che stai
modificando nell'app macOS. I pattern sono **corrispondenze glob case-insensitive**.
I pattern dovrebbero risolversi in **path di binari** (le voci con solo basename vengono ignorate).
Le voci legacy `agents.default` vengono migrate a `agents.main` al caricamento.
Le catene shell come `echo ok && pwd` richiedono comunque che ogni segmento di primo livello soddisfi le regole dell'allowlist.

Esempi:

- `~/Projects/**/bin/peekaboo`
- `~/.local/bin/*`
- `/opt/homebrew/bin/rg`

Ogni voce di allowlist tiene traccia di:

- **id** UUID stabile usato per l'identità UI (facoltativo)
- timestamp **ultimo utilizzo**
- **ultimo comando usato**
- **ultimo path risolto**

## Auto-allow delle CLI delle skill

Quando **Auto-allow skill CLIs** è abilitato, gli eseguibili referenziati da skill note
sono trattati come presenti nell'allowlist sui nodi (nodo macOS o host nodo headless). Questo usa
`skills.bins` tramite Gateway RPC per recuperare l'elenco dei bin delle skill. Disabilitalo se vuoi allowlist manuali rigorose.

Note importanti sul trust:

- Questa è un'**allowlist implicita di comodità**, separata dalle voci manuali di allowlist dei path.
- È pensata per ambienti trusted dell'operatore in cui gateway e nodo si trovano nello stesso confine di fiducia.
- Se ti serve una fiducia esplicita rigorosa, mantieni `autoAllowSkills: false` e usa solo voci manuali di allowlist dei path.

## Safe bins (solo stdin)

`tools.exec.safeBins` definisce un piccolo elenco di binari **solo stdin** (ad esempio `cut`)
che possono essere eseguiti in modalità allowlist **senza** voci esplicite di allowlist. I safe bin rifiutano
argomenti file posizionali e token simili a path, quindi possono operare solo sul flusso in ingresso.
Trattalo come un percorso rapido ristretto per filtri di stream, non come un elenco generale di fiducia.
**Non** aggiungere binari interpreter o runtime (ad esempio `python3`, `node`, `ruby`, `bash`, `sh`, `zsh`) a `safeBins`.
Se un comando può valutare codice, eseguire sottocomandi o leggere file per progettazione, preferisci voci esplicite di allowlist e mantieni abilitati i prompt di approvazione.
I safe bin personalizzati devono definire un profilo esplicito in `tools.exec.safeBinProfiles.<bin>`.
La validazione è deterministica solo dalla forma di argv (nessun controllo di esistenza del filesystem host), il che
impedisce comportamenti da oracolo sull'esistenza dei file derivanti da differenze allow/deny.
Le opzioni orientate ai file sono negate per i safe bin predefiniti (ad esempio `sort -o`, `sort --output`,
`sort --files0-from`, `sort --compress-program`, `sort --random-source`,
`sort --temporary-directory`/`-T`, `wc --files0-from`, `jq -f/--from-file`,
`grep -f/--file`).
I safe bin applicano anche una policy esplicita per binario sui flag che rompono il comportamento solo-stdin
(ad esempio `sort -o/--output/--compress-program` e i flag ricorsivi di grep).
Le opzioni lunghe vengono validate in modalità safe-bin con fail-closed: flag sconosciuti e abbreviazioni
ambigue vengono rifiutati.
Flag negati per profilo safe-bin:

[//]: # "SAFE_BIN_DENIED_FLAGS:START"

- `grep`: `--dereference-recursive`, `--directories`, `--exclude-from`, `--file`, `--recursive`, `-R`, `-d`, `-f`, `-r`
- `jq`: `--argfile`, `--from-file`, `--library-path`, `--rawfile`, `--slurpfile`, `-L`, `-f`
- `sort`: `--compress-program`, `--files0-from`, `--output`, `--random-source`, `--temporary-directory`, `-T`, `-o`
- `wc`: `--files0-from`

[//]: # "SAFE_BIN_DENIED_FLAGS:END"

I safe bin forzano anche i token argv a essere trattati come **testo letterale** al momento dell'esecuzione (niente globbing
e nessuna espansione di `$VARS`) per i segmenti solo-stdin, così pattern come `*` o `$HOME/...` non possono essere
usati per introdurre di nascosto letture di file.
I safe bin devono inoltre risolversi da directory di binari trusted (valori predefiniti di sistema più eventuali
`tools.exec.safeBinTrustedDirs`). Le voci `PATH` non sono mai auto-trusted.
Le directory trusted predefinite dei safe bin sono intenzionalmente minime: `/bin`, `/usr/bin`.
Se il tuo eseguibile safe-bin si trova in path di package-manager/utente (ad esempio
`/opt/homebrew/bin`, `/usr/local/bin`, `/opt/local/bin`, `/snap/bin`), aggiungili esplicitamente
a `tools.exec.safeBinTrustedDirs`.
Il chaining shell e le redirezioni non sono auto-consentiti in modalità allowlist.

Il chaining shell (`&&`, `||`, `;`) è consentito quando ogni segmento di primo livello soddisfa l'allowlist
(inclusi safe bin o auto-allow delle skill). Le redirezioni restano non supportate in modalità allowlist.
La command substitution (`$()` / backtick) viene rifiutata durante il parsing dell'allowlist, inclusa all'interno
delle virgolette doppie; usa virgolette singole se ti serve testo letterale `$()`.
Nelle approvazioni dell'app companion macOS, il testo shell grezzo contenente sintassi di controllo o espansione della shell
(`&&`, `||`, `;`, `|`, `` ` ``, `$`, `<`, `>`, `(`, `)`) viene trattato come un mancato match dell'allowlist a meno che
il binario shell stesso non sia nell'allowlist.
Per i wrapper shell (`bash|sh|zsh ... -c/-lc`), gli override env con ambito richiesta sono ridotti a una
piccola allowlist esplicita (`TERM`, `LANG`, `LC_*`, `COLORTERM`, `NO_COLOR`, `FORCE_COLOR`).
Per le decisioni allow-always in modalità allowlist, i wrapper di dispatch noti
(`env`, `nice`, `nohup`, `stdbuf`, `timeout`) persistono i path degli eseguibili interni invece dei path dei wrapper.
Anche i multiplexer shell (`busybox`, `toybox`) vengono spacchettati per gli applet shell (`sh`, `ash`,
ecc.) così vengono persistiti gli eseguibili interni invece dei binari del multiplexer. Se un wrapper o
multiplexer non può essere spacchettato in sicurezza, nessuna voce di allowlist viene persistita automaticamente.
Se inserisci nell'allowlist interpreter come `python3` o `node`, preferisci `tools.exec.strictInlineEval=true` così l'eval inline richiede comunque approvazione esplicita. In modalità strict, `allow-always` può ancora persistere invocazioni benigne di interpreter/script, ma i vettori di eval inline non vengono persistiti automaticamente.

Safe bin predefiniti:

[//]: # "SAFE_BIN_DEFAULTS:START"

`cut`, `uniq`, `head`, `tail`, `tr`, `wc`

[//]: # "SAFE_BIN_DEFAULTS:END"

`grep` e `sort` non sono nell'elenco predefinito. Se li abiliti esplicitamente, mantieni voci di allowlist esplicite per
i loro workflow non-stdin.
Per `grep` in modalità safe-bin, fornisci il pattern con `-e`/`--regexp`; la forma con pattern posizionale è
rifiutata così gli operandi file non possono essere introdotti di nascosto come posizionali ambigui.

### Safe bins vs allowlist

| Argomento | `tools.exec.safeBins` | Allowlist (`exec-approvals.json`) |
| ---------------- | ------------------------------------------------------ | ------------------------------------------------------------ |
| Obiettivo | Auto-consentire filtri stdin ristretti | Affidarsi esplicitamente a eseguibili specifici |
| Tipo di corrispondenza | Nome dell'eseguibile + policy argv del safe-bin | Pattern glob del path dell'eseguibile risolto |
| Ambito degli argomenti | Limitato dal profilo safe-bin e dalle regole dei token letterali | Solo corrispondenza del path; gli argomenti sono altrimenti responsabilità tua |
| Esempi tipici | `head`, `tail`, `tr`, `wc` | `jq`, `python3`, `node`, `ffmpeg`, CLI personalizzate |
| Miglior uso | Trasformazioni testuali a basso rischio nelle pipeline | Qualsiasi strumento con comportamento più ampio o effetti collaterali |

Posizione della configurazione:

- `safeBins` proviene dalla configurazione (`tools.exec.safeBins` oppure per agente `agents.list[].tools.exec.safeBins`).
- `safeBinTrustedDirs` proviene dalla configurazione (`tools.exec.safeBinTrustedDirs` oppure per agente `agents.list[].tools.exec.safeBinTrustedDirs`).
- `safeBinProfiles` proviene dalla configurazione (`tools.exec.safeBinProfiles` oppure per agente `agents.list[].tools.exec.safeBinProfiles`). Le chiavi dei profili per agente sovrascrivono le chiavi globali.
- Le voci di allowlist vivono nel file host-local `~/.openclaw/exec-approvals.json` sotto `agents.<id>.allowlist` (oppure tramite Control UI / `openclaw approvals allowlist ...`).
- `openclaw security audit` avvisa con `tools.exec.safe_bins_interpreter_unprofiled` quando bin interpreter/runtime compaiono in `safeBins` senza profili espliciti.
- `openclaw doctor --fix` può creare lo scaffold delle voci mancanti `safeBinProfiles.<bin>` come `{}` (rivedile e restringile in seguito). I bin interpreter/runtime non vengono creati automaticamente.

Esempio di profilo personalizzato:
__OC_I18N_900004__
Se includi esplicitamente `jq` in `safeBins`, OpenClaw rifiuta comunque il builtin `env` in modalità safe-bin
così `jq -n env` non può scaricare l'ambiente del processo host senza un path esplicito nell'allowlist
o un prompt di approvazione.

## Modifica nella Control UI

Usa la scheda **Control UI → Nodes → Exec approvals** per modificare valori predefiniti, override
per agente e allowlist. Scegli un ambito (Defaults o un agente), modifica la policy,
aggiungi/rimuovi pattern di allowlist, quindi fai clic su **Save**. La UI mostra i metadati di **ultimo utilizzo**
per pattern così puoi mantenere l'elenco ordinato.

Il selettore del target sceglie **Gateway** (approvazioni locali) oppure un **Node**. I nodi
devono pubblicizzare `system.execApprovals.get/set` (app macOS o host nodo headless).
Se un nodo non pubblicizza ancora le approvazioni exec, modifica direttamente il suo file locale
`~/.openclaw/exec-approvals.json`.

CLI: `openclaw approvals` supporta la modifica del gateway o del nodo (vedi [Approvals CLI](/cli/approvals)).

## Flusso di approvazione

Quando è richiesto un prompt, il gateway trasmette `exec.approval.requested` ai client operator.
La Control UI e la app macOS lo risolvono tramite `exec.approval.resolve`, quindi il gateway inoltra la
richiesta approvata all'host del nodo.

Per `host=node`, le richieste di approvazione includono un payload canonico `systemRunPlan`. Il gateway usa
quel piano come contesto autorevole di comando/cwd/sessione quando inoltra richieste approvate `system.run`.

Questo è importante per la latenza dell'approvazione asincrona:

- il percorso exec del nodo prepara un unico piano canonico in anticipo
- il record di approvazione memorizza quel piano e i relativi metadati di binding
- una volta approvato, la chiamata finale inoltrata `system.run` riusa il piano memorizzato
  invece di fidarsi di successive modifiche del chiamante
- se il chiamante cambia `command`, `rawCommand`, `cwd`, `agentId` oppure
  `sessionKey` dopo che la richiesta di approvazione è stata creata, il gateway rifiuta l'esecuzione
  inoltrata come mismatch di approvazione

## Comandi interpreter/runtime

Le esecuzioni di interpreter/runtime supportate da approvazione sono intenzionalmente conservative:

- Il contesto esatto di argv/cwd/env viene sempre vincolato.
- Le forme di script shell diretto e file runtime diretto vengono vincolate in best-effort a uno snapshot di file locale concreto.
- Le forme comuni di wrapper di package manager che si risolvono comunque in un singolo file locale diretto (ad esempio
  `pnpm exec`, `pnpm node`, `npm exec`, `npx`) vengono spacchettate prima del binding.
- Se OpenClaw non riesce a identificare esattamente un singolo file locale concreto per un comando interpreter/runtime
  (ad esempio script di package, forme eval, catene di loader specifiche del runtime o forme ambigue multi-file),
  l'esecuzione supportata da approvazione viene negata invece di affermare una copertura semantica che in realtà non
  possiede.
- Per questi workflow, preferisci la sandbox, un confine host separato o un workflow esplicito trusted
  di allowlist/full in cui l'operatore accetta la semantica runtime più ampia.

Quando sono richieste approvazioni, lo strumento exec restituisce immediatamente un id di approvazione. Usa quell'id per
correlare eventi di sistema successivi (`Exec finished` / `Exec denied`). Se non arriva alcuna decisione prima del
timeout, la richiesta viene trattata come timeout di approvazione e mostrata come motivo di negazione.

### Comportamento di consegna del follow-up

Dopo che un exec asincrono approvato è terminato, OpenClaw invia un turno `agent` di follow-up alla stessa sessione.

- Se esiste un target di consegna esterno valido (canale consegnabile più target `to`), il follow-up usa quel canale.
- Nei flussi solo webchat o sessione interna senza target esterno, la consegna del follow-up resta solo di sessione (`deliver: false`).
- Se un chiamante richiede esplicitamente una consegna esterna rigorosa senza alcun canale esterno risolvibile, la richiesta fallisce con `INVALID_REQUEST`.
- Se `bestEffortDeliver` è abilitato e non è possibile risolvere alcun canale esterno, la consegna viene degradata a sola sessione invece di fallire.

La finestra di dialogo di conferma include:

- comando + argomenti
- cwd
- id agente
- path dell'eseguibile risolto
- host + metadati della policy

Azioni:

- **Allow once** → esegui ora
- **Always allow** → aggiungi all'allowlist + esegui
- **Deny** → blocca

## Inoltro delle approvazioni ai canali chat

Puoi inoltrare i prompt di approvazione exec a qualsiasi canale chat (inclusi i canali plugin) e approvarli
con `/approve`. Questo usa il normale pipeline di consegna in uscita.

Configurazione:
__OC_I18N_900005__
Rispondi in chat:
__OC_I18N_900006__
Il comando `/approve` gestisce sia le approvazioni exec sia le approvazioni dei plugin. Se l'ID non corrisponde a un'approvazione exec in sospeso, controlla automaticamente invece le approvazioni dei plugin.

### Inoltro delle approvazioni dei plugin

L'inoltro delle approvazioni dei plugin usa lo stesso pipeline di consegna delle approvazioni exec ma ha una
configurazione indipendente sotto `approvals.plugin`. Abilitare o disabilitare l'una non influisce sull'altra.
__OC_I18N_900007__
La forma della configurazione è identica a `approvals.exec`: `enabled`, `mode`, `agentFilter`,
`sessionFilter` e `targets` funzionano allo stesso modo.

I canali che supportano risposte interattive condivise renderizzano gli stessi pulsanti di approvazione sia per le approvazioni exec sia per quelle dei plugin. I canali senza UI interattiva condivisa ricadono su testo semplice con istruzioni `/approve`.

### Approvazioni nella stessa chat su qualsiasi canale

Quando una richiesta di approvazione exec o plugin ha origine da una superficie chat consegnabile, la stessa chat
può ora approvarla con `/approve` per impostazione predefinita. Questo si applica a canali come Slack, Matrix e
Microsoft Teams oltre ai flussi già esistenti di Web UI e terminal UI.

Questo percorso condiviso tramite comando testuale usa il normale modello auth del canale per quella conversazione. Se la
chat di origine può già inviare comandi e ricevere risposte, le richieste di approvazione non hanno più bisogno di un
adattatore di consegna nativo separato solo per restare in sospeso.

Discord e Telegram supportano anche `/approve` nella stessa chat, ma quei canali usano ancora
il loro elenco di approvatori risolto per l'autorizzazione anche quando la consegna nativa delle approvazioni è disabilitata.

Per Telegram e altri client di approvazione nativi che chiamano direttamente il Gateway,
questo fallback è intenzionalmente limitato ai fallimenti "approvazione non trovata". Un vero
rifiuto/errore di approvazione exec non ritenta silenziosamente come approvazione plugin.

### Consegna di approvazioni native

Alcuni canali possono anche agire come client nativi di approvazione. I client nativi aggiungono DM degli approvatori, fanout della chat di origine e UX di approvazione interattiva specifica del canale sopra il flusso condiviso `/approve`
nella stessa chat.

Quando sono disponibili card/pulsanti di approvazione nativi, quella UI nativa è il
percorso principale rivolto all'agente. L'agente non dovrebbe anche ripetere un duplicato del comando semplice in chat
`/approve`, a meno che il risultato dello strumento non dica che le approvazioni in chat non sono disponibili o che
l'approvazione manuale sia l'unico percorso rimasto.

Modello generico:

- la policy exec host continua a decidere se è richiesta l'approvazione exec
- `approvals.exec` controlla l'inoltro dei prompt di approvazione ad altre destinazioni chat
- `channels.<channel>.execApprovals` controlla se quel canale agisce come client nativo di approvazione

I client nativi di approvazione abilitano automaticamente la consegna DM-first quando tutte queste condizioni sono vere:

- il canale supporta la consegna nativa delle approvazioni
- gli approvatori possono essere risolti da `execApprovals.approvers` espliciti o dalle fonti di fallback documentate
  di quel canale
- `channels.<channel>.execApprovals.enabled` non è impostato oppure è `"auto"`

Imposta `enabled: false` per disabilitare esplicitamente un client nativo di approvazione. Imposta `enabled: true` per forzarlo
quando gli approvatori si risolvono. La consegna pubblica nella chat di origine resta esplicita tramite
`channels.<channel>.execApprovals.target`.

FAQ: [Perché ci sono due configurazioni delle approvazioni exec per le approvazioni chat?](/help/faq#why-are-there-two-exec-approval-configs-for-chat-approvals)

- Discord: `channels.discord.execApprovals.*`
- Slack: `channels.slack.execApprovals.*`
- Telegram: `channels.telegram.execApprovals.*`

Questi client nativi di approvazione aggiungono routing DM e fanout facoltativo del canale sopra il flusso condiviso
`/approve` nella stessa chat e i pulsanti di approvazione condivisi.

Comportamento condiviso:

- Slack, Matrix, Microsoft Teams e chat consegnabili simili usano il normale modello auth del canale
  per `/approve` nella stessa chat
- quando un client nativo di approvazione si abilita automaticamente, il target di consegna nativo predefinito sono i DM degli approvatori
- per Discord e Telegram, solo gli approvatori risolti possono approvare o negare
- gli approvatori Discord possono essere espliciti (`execApprovals.approvers`) o dedotti da `commands.ownerAllowFrom`
- gli approvatori Telegram possono essere espliciti (`execApprovals.approvers`) o dedotti dalla configurazione owner esistente (`allowFrom`, più `defaultTo` dei messaggi diretti dove supportato)
- gli approvatori Slack possono essere espliciti (`execApprovals.approvers`) o dedotti da `commands.ownerAllowFrom`
- i pulsanti nativi Slack preservano il tipo di id di approvazione, così gli id `plugin:` possono risolvere le approvazioni dei plugin
  senza un secondo livello di fallback locale a Slack
- il routing DM/canale nativo di Matrix e le scorciatoie a reazione gestiscono sia le approvazioni exec sia quelle plugin;
  l'autorizzazione dei plugin continua comunque a provenire da `channels.matrix.dm.allowFrom`
- il richiedente non deve necessariamente essere un approvatore
- la chat di origine può approvare direttamente con `/approve` quando quella chat supporta già comandi e risposte
- i pulsanti nativi di approvazione Discord instradano in base al tipo di id di approvazione: gli id `plugin:` vanno
  direttamente alle approvazioni dei plugin, tutto il resto va alle approvazioni exec
- i pulsanti nativi di approvazione Telegram seguono lo stesso fallback limitato da exec a plugin di `/approve`
- quando `target` nativo abilita la consegna nella chat di origine, i prompt di approvazione includono il testo del comando
- le approvazioni exec in sospeso scadono dopo 30 minuti per impostazione predefinita
- se nessuna UI operatore o client di approvazione configurato può accettare la richiesta, il prompt torna a `askFallback`

Telegram usa come predefinito i DM degli approvatori (`target: "dm"`). Puoi passare a `channel` o `both` quando
vuoi che i prompt di approvazione appaiano anche nella chat/topic Telegram di origine. Per i topic forum Telegram,
OpenClaw preserva il topic per il prompt di approvazione e per il follow-up post-approvazione.

Vedi:

- [Discord](/channels/discord)
- [Telegram](/channels/telegram)

### Flusso IPC macOS
__OC_I18N_900008__
Note di sicurezza:

- Modalità socket Unix `0600`, token memorizzato in `exec-approvals.json`.
- Controllo del peer con stesso UID.
- Challenge/response (nonce + token HMAC + hash della richiesta) + TTL breve.

## Eventi di sistema

Il ciclo di vita exec viene esposto come messaggi di sistema:

- `Exec running` (solo se il comando supera la soglia di notifica running)
- `Exec finished`
- `Exec denied`

Questi vengono pubblicati nella sessione dell'agente dopo che il nodo segnala l'evento.
Le approvazioni exec sull'host gateway emettono gli stessi eventi di ciclo di vita quando il comando termina (e facoltativamente quando è in esecuzione oltre la soglia).
Gli exec soggetti ad approvazione riutilizzano l'id di approvazione come `runId` in questi messaggi per una facile correlazione.

## Comportamento delle approvazioni negate

Quando un'approvazione exec asincrona viene negata, OpenClaw impedisce all'agente di riutilizzare
l'output di eventuali esecuzioni precedenti dello stesso comando nella sessione. Il motivo della negazione
viene passato con indicazioni esplicite che nessun output del comando è disponibile, il che impedisce
all'agente di affermare che c'è nuovo output o di ripetere il comando negato con
risultati obsoleti di una precedente esecuzione riuscita.

## Implicazioni

- **full** è potente; preferisci le allowlist quando possibile.
- **ask** ti mantiene nel ciclo consentendo comunque approvazioni rapide.
- Le allowlist per agente impediscono che le approvazioni di un agente si trasferiscano ad altri.
- Le approvazioni si applicano solo alle richieste exec host provenienti da **mittenti autorizzati**. I mittenti non autorizzati non possono emettere `/exec`.
- `/exec security=full` è una comodità a livello di sessione per operatori autorizzati e salta le approvazioni per progettazione.
  Per bloccare rigidamente l'exec host, imposta la security delle approvazioni su `deny` oppure nega lo strumento `exec` tramite tool policy.

Correlati:

- [Strumento exec](/it/tools/exec)
- [Modalità elevated](/it/tools/elevated)
- [Skills](/it/tools/skills)

## Correlati

- [Exec](/it/tools/exec) — strumento di esecuzione dei comandi shell
- [Sandboxing](/it/gateway/sandboxing) — modalità sandbox e accesso al workspace
- [Security](/it/gateway/security) — modello di sicurezza e hardening
- [Sandbox vs Tool Policy vs Elevated](/it/gateway/sandbox-vs-tool-policy-vs-elevated) — quando usare ciascuno
