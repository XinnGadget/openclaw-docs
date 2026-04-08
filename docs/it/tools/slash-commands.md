---
read_when:
    - Usare o configurare i comandi di chat
    - Eseguire il debug dell'instradamento dei comandi o delle autorizzazioni
summary: 'Comandi slash: testo vs nativi, configurazione e comandi supportati'
title: Comandi Slash
x-i18n:
    generated_at: "2026-04-08T06:01:59Z"
    model: gpt-5.4
    provider: openai
    source_hash: 4a7ee7f1a8012058279b9e632889b291d4e659e4ec81209ca8978afbb9ad4b96
    source_path: tools/slash-commands.md
    workflow: 15
---

# Comandi slash

I comandi sono gestiti dal Gateway. La maggior parte dei comandi deve essere inviata come messaggio **autonomo** che inizia con `/`.
Il comando bash di chat solo host usa `! <cmd>` (con `/bash <cmd>` come alias).

Esistono due sistemi correlati:

- **Comandi**: messaggi `/...` autonomi.
- **Direttive**: `/think`, `/fast`, `/verbose`, `/reasoning`, `/elevated`, `/exec`, `/model`, `/queue`.
  - Le direttive vengono rimosse dal messaggio prima che il modello lo veda.
  - Nei normali messaggi di chat (non composti solo da direttive), vengono trattate come “suggerimenti inline” e **non** rendono persistenti le impostazioni della sessione.
  - Nei messaggi composti solo da direttive (il messaggio contiene solo direttive), rendono persistenti le impostazioni nella sessione e rispondono con una conferma.
  - Le direttive vengono applicate solo ai **mittenti autorizzati**. Se `commands.allowFrom` è impostato, è l'unica
    allowlist usata; altrimenti l'autorizzazione deriva dalle allowlist del canale/dall'abbinamento più `commands.useAccessGroups`.
    I mittenti non autorizzati vedono le direttive trattate come testo normale.

Esistono anche alcune **scorciatoie inline** (solo per mittenti in allowlist/autorizzati): `/help`, `/commands`, `/status`, `/whoami` (`/id`).
Vengono eseguite immediatamente, vengono rimosse prima che il modello veda il messaggio e il testo rimanente continua nel flusso normale.

## Configurazione

```json5
{
  commands: {
    native: "auto",
    nativeSkills: "auto",
    text: true,
    bash: false,
    bashForegroundMs: 2000,
    config: false,
    mcp: false,
    plugins: false,
    debug: false,
    restart: true,
    ownerAllowFrom: ["discord:123456789012345678"],
    ownerDisplay: "raw",
    ownerDisplaySecret: "${OWNER_ID_HASH_SECRET}",
    allowFrom: {
      "*": ["user1"],
      discord: ["user:123"],
    },
    useAccessGroups: true,
  },
}
```

- `commands.text` (predefinito `true`) abilita il parsing di `/...` nei messaggi di chat.
  - Nelle superfici senza comandi nativi (WhatsApp/WebChat/Signal/iMessage/Google Chat/Microsoft Teams), i comandi testuali continuano a funzionare anche se imposti questo valore su `false`.
- `commands.native` (predefinito `"auto"`) registra i comandi nativi.
  - Auto: attivo per Discord/Telegram; disattivo per Slack (finché non aggiungi i comandi slash); ignorato per i provider senza supporto nativo.
  - Imposta `channels.discord.commands.native`, `channels.telegram.commands.native` o `channels.slack.commands.native` per eseguire un override per provider (bool o `"auto"`).
  - `false` cancella all'avvio i comandi registrati in precedenza su Discord/Telegram. I comandi Slack sono gestiti nell'app Slack e non vengono rimossi automaticamente.
- `commands.nativeSkills` (predefinito `"auto"`) registra in modo nativo i comandi **Skill** quando supportati.
  - Auto: attivo per Discord/Telegram; disattivo per Slack (Slack richiede la creazione di un comando slash per ogni skill).
  - Imposta `channels.discord.commands.nativeSkills`, `channels.telegram.commands.nativeSkills` o `channels.slack.commands.nativeSkills` per eseguire un override per provider (bool o `"auto"`).
- `commands.bash` (predefinito `false`) abilita `! <cmd>` per eseguire comandi shell sull'host (`/bash <cmd>` è un alias; richiede le allowlist di `tools.elevated`).
- `commands.bashForegroundMs` (predefinito `2000`) controlla per quanto tempo bash attende prima di passare alla modalità in background (`0` manda immediatamente in background).
- `commands.config` (predefinito `false`) abilita `/config` (legge/scrive `openclaw.json`).
- `commands.mcp` (predefinito `false`) abilita `/mcp` (legge/scrive la configurazione MCP gestita da OpenClaw sotto `mcp.servers`).
- `commands.plugins` (predefinito `false`) abilita `/plugins` (rilevamento/stato dei plugin più controlli di installazione + abilitazione/disabilitazione).
- `commands.debug` (predefinito `false`) abilita `/debug` (override solo runtime).
- `commands.restart` (predefinito `true`) abilita `/restart` più le azioni degli strumenti di riavvio del gateway.
- `commands.ownerAllowFrom` (opzionale) imposta la allowlist esplicita del proprietario per le superfici di comandi/strumenti riservate al proprietario. È separata da `commands.allowFrom`.
- `commands.ownerDisplay` controlla come gli ID proprietario compaiono nel prompt di sistema: `raw` o `hash`.
- `commands.ownerDisplaySecret` imposta facoltativamente il segreto HMAC usato quando `commands.ownerDisplay="hash"`.
- `commands.allowFrom` (opzionale) imposta una allowlist per provider per l'autorizzazione dei comandi. Quando configurata, è l'unica
  fonte di autorizzazione per comandi e direttive (le allowlist del canale/l'abbinamento e `commands.useAccessGroups`
  vengono ignorati). Usa `"*"` per un valore predefinito globale; le chiavi specifiche del provider lo sovrascrivono.
- `commands.useAccessGroups` (predefinito `true`) applica allowlist/policy ai comandi quando `commands.allowFrom` non è impostato.

## Elenco dei comandi

Fonte di verità attuale:

- i built-in core provengono da `src/auto-reply/commands-registry.shared.ts`
- i comandi dock generati provengono da `src/auto-reply/commands-registry.data.ts`
- i comandi dei plugin provengono dalle chiamate `registerCommand()` dei plugin
- la disponibilità effettiva sul tuo gateway dipende comunque dai flag di configurazione, dalla superficie del canale e dai plugin installati/abilitati

### Comandi built-in core

Comandi built-in disponibili oggi:

- `/new [model]` avvia una nuova sessione; `/reset` è l'alias di reset.
- `/compact [instructions]` compatta il contesto della sessione. Vedi [/concepts/compaction](/it/concepts/compaction).
- `/stop` interrompe l'esecuzione corrente.
- `/session idle <duration|off>` e `/session max-age <duration|off>` gestiscono la scadenza del binding del thread.
- `/think <off|minimal|low|medium|high|xhigh>` imposta il livello di thinking. Alias: `/thinking`, `/t`.
- `/verbose on|off|full` attiva/disattiva l'output verboso. Alias: `/v`.
- `/fast [status|on|off]` mostra o imposta la modalità veloce.
- `/reasoning [on|off|stream]` attiva/disattiva la visibilità del reasoning. Alias: `/reason`.
- `/elevated [on|off|ask|full]` attiva/disattiva la modalità elevata. Alias: `/elev`.
- `/exec host=<auto|sandbox|gateway|node> security=<deny|allowlist|full> ask=<off|on-miss|always> node=<id>` mostra o imposta i valori predefiniti di exec.
- `/model [name|#|status]` mostra o imposta il modello.
- `/models [provider] [page] [limit=<n>|size=<n>|all]` elenca i provider o i modelli di un provider.
- `/queue <mode>` gestisce il comportamento della coda (`steer`, `interrupt`, `followup`, `collect`, `steer-backlog`) più opzioni come `debounce:2s cap:25 drop:summarize`.
- `/help` mostra il riepilogo breve della guida.
- `/commands` mostra il catalogo dei comandi generato.
- `/tools [compact|verbose]` mostra cosa può usare in questo momento l'agente corrente.
- `/status` mostra lo stato del runtime, incluso l'uso/quota del provider quando disponibile.
- `/tasks` elenca le attività in background attive/recenti per la sessione corrente.
- `/context [list|detail|json]` spiega come viene assemblato il contesto.
- `/export-session [path]` esporta la sessione corrente in HTML. Alias: `/export`.
- `/whoami` mostra il tuo ID mittente. Alias: `/id`.
- `/skill <name> [input]` esegue una skill per nome.
- `/allowlist [list|add|remove] ...` gestisce le voci della allowlist. Solo testo.
- `/approve <id> <decision>` risolve le richieste di approvazione exec.
- `/btw <question>` pone una domanda laterale senza modificare il contesto futuro della sessione. Vedi [/tools/btw](/it/tools/btw).
- `/subagents list|kill|log|info|send|steer|spawn` gestisce le esecuzioni dei sub-agent per la sessione corrente.
- `/acp spawn|cancel|steer|close|sessions|status|set-mode|set|cwd|permissions|timeout|model|reset-options|doctor|install|help` gestisce le sessioni ACP e le opzioni del runtime.
- `/focus <target>` collega il thread Discord corrente o il topic/conversation Telegram a un target di sessione.
- `/unfocus` rimuove il binding corrente.
- `/agents` elenca gli agenti collegati al thread per la sessione corrente.
- `/kill <id|#|all>` interrompe uno o tutti i sub-agent in esecuzione.
- `/steer <id|#> <message>` invia indicazioni a un sub-agent in esecuzione. Alias: `/tell`.
- `/config show|get|set|unset` legge o scrive `openclaw.json`. Solo proprietario. Richiede `commands.config: true`.
- `/mcp show|get|set|unset` legge o scrive la configurazione del server MCP gestita da OpenClaw sotto `mcp.servers`. Solo proprietario. Richiede `commands.mcp: true`.
- `/plugins list|inspect|show|get|install|enable|disable` ispeziona o modifica lo stato dei plugin. `/plugin` è un alias. Solo proprietario per le scritture. Richiede `commands.plugins: true`.
- `/debug show|set|unset|reset` gestisce gli override di configurazione solo runtime. Solo proprietario. Richiede `commands.debug: true`.
- `/usage off|tokens|full|cost` controlla il piè di pagina di utilizzo per risposta oppure stampa un riepilogo locale dei costi.
- `/tts on|off|status|provider|limit|summary|audio|help` controlla TTS. Vedi [/tools/tts](/it/tools/tts).
- `/restart` riavvia OpenClaw quando abilitato. Predefinito: abilitato; imposta `commands.restart: false` per disabilitarlo.
- `/activation mention|always` imposta la modalità di attivazione del gruppo.
- `/send on|off|inherit` imposta la policy di invio. Solo proprietario.
- `/bash <command>` esegue un comando shell sull'host. Solo testo. Alias: `! <command>`. Richiede `commands.bash: true` più le allowlist di `tools.elevated`.
- `!poll [sessionId]` controlla un job bash in background.
- `!stop [sessionId]` arresta un job bash in background.

### Comandi dock generati

I comandi dock vengono generati dai plugin canale con supporto per i comandi nativi. Set bundled attuale:

- `/dock-discord` (alias: `/dock_discord`)
- `/dock-mattermost` (alias: `/dock_mattermost`)
- `/dock-slack` (alias: `/dock_slack`)
- `/dock-telegram` (alias: `/dock_telegram`)

### Comandi dei plugin bundled

I plugin bundled possono aggiungere altri comandi slash. Comandi bundled attuali in questo repo:

- `/dreaming [on|off|status|help]` attiva/disattiva il memory dreaming. Vedi [Dreaming](/it/concepts/dreaming).
- `/pair [qr|status|pending|approve|cleanup|notify]` gestisce il flusso di abbinamento/configurazione del dispositivo. Vedi [Pairing](/it/channels/pairing).
- `/phone status|arm <camera|screen|writes|all> [duration]|disarm` abilita temporaneamente i comandi del nodo telefono ad alto rischio.
- `/voice status|list [limit]|set <voiceId|name>` gestisce la configurazione della voce Talk. Su Discord, il nome del comando nativo è `/talkvoice`.
- `/card ...` invia preset di rich card LINE. Vedi [LINE](/it/channels/line).
- Comandi solo QQBot:
  - `/bot-ping`
  - `/bot-version`
  - `/bot-help`
  - `/bot-upgrade`
  - `/bot-logs`

### Comandi skill dinamici

Le skill invocabili dall'utente sono esposte anche come comandi slash:

- `/skill <name> [input]` funziona sempre come entrypoint generico.
- le skill possono anche comparire come comandi diretti come `/prose` quando la skill/il plugin li registra.
- la registrazione nativa dei comandi skill è controllata da `commands.nativeSkills` e `channels.<provider>.commands.nativeSkills`.

Note:

- I comandi accettano un `:` facoltativo tra il comando e gli argomenti (ad esempio `/think: high`, `/send: on`, `/help:`).
- `/new <model>` accetta un alias di modello, `provider/model` o un nome provider (corrispondenza fuzzy); se non c'è corrispondenza, il testo viene trattato come corpo del messaggio.
- Per il dettaglio completo dell'utilizzo del provider, usa `openclaw status --usage`.
- `/allowlist add|remove` richiede `commands.config=true` e rispetta `configWrites` del canale.
- Nei canali multi-account, anche `/allowlist --account <id>` mirato alla configurazione e `/config set channels.<provider>.accounts.<id>...` rispettano `configWrites` dell'account di destinazione.
- `/usage` controlla il piè di pagina di utilizzo per risposta; `/usage cost` stampa un riepilogo locale dei costi dai log di sessione OpenClaw.
- `/restart` è abilitato per impostazione predefinita; imposta `commands.restart: false` per disabilitarlo.
- `/plugins install <spec>` accetta le stesse specifiche di plugin di `openclaw plugins install`: percorso/archivio locale, pacchetto npm o `clawhub:<pkg>`.
- `/plugins enable|disable` aggiorna la configurazione del plugin e può richiedere un riavvio.
- Comando nativo solo Discord: `/vc join|leave|status` controlla i canali vocali (richiede `channels.discord.voice` e comandi nativi; non disponibile come testo).
- I comandi di binding del thread Discord (`/focus`, `/unfocus`, `/agents`, `/session idle`, `/session max-age`) richiedono che i binding del thread effettivi siano abilitati (`session.threadBindings.enabled` e/o `channels.discord.threadBindings.enabled`).
- Riferimento dei comandi ACP e comportamento del runtime: [ACP Agents](/it/tools/acp-agents).
- `/verbose` è pensato per il debug e per una visibilità aggiuntiva; tienilo **off** nell'uso normale.
- `/fast on|off` rende persistente un override della sessione. Usa l'opzione `inherit` dell'interfaccia Sessions per cancellarlo e tornare ai valori predefiniti della configurazione.
- `/fast` è specifico del provider: OpenAI/OpenAI Codex lo mappano a `service_tier=priority` sugli endpoint nativi Responses, mentre le richieste Anthropic pubbliche dirette, incluso il traffico autenticato OAuth inviato a `api.anthropic.com`, lo mappano a `service_tier=auto` o `standard_only`. Vedi [OpenAI](/it/providers/openai) e [Anthropic](/it/providers/anthropic).
- I riepiloghi degli errori degli strumenti vengono comunque mostrati quando pertinenti, ma il testo dettagliato dell'errore viene incluso solo quando `/verbose` è `on` o `full`.
- `/reasoning` (e `/verbose`) sono rischiosi in contesti di gruppo: possono rivelare reasoning interno o output degli strumenti che non intendevi esporre. È preferibile lasciarli disattivati, soprattutto nelle chat di gruppo.
- `/model` rende immediatamente persistente il nuovo modello di sessione.
- Se l'agente è inattivo, la prossima esecuzione lo usa subito.
- Se un'esecuzione è già attiva, OpenClaw contrassegna un cambio live come in sospeso e riavvia nel nuovo modello solo in un punto di retry pulito.
- Se l'attività degli strumenti o l'output della risposta sono già iniziati, il cambio in sospeso può restare in coda fino a una successiva opportunità di retry o al turno utente successivo.
- **Percorso rapido:** i messaggi composti solo da comandi provenienti da mittenti in allowlist vengono gestiti immediatamente (saltano coda + modello).
- **Blocco per menzione nei gruppi:** i messaggi composti solo da comandi provenienti da mittenti in allowlist saltano i requisiti di menzione.
- **Scorciatoie inline (solo mittenti in allowlist):** alcuni comandi funzionano anche quando incorporati in un messaggio normale e vengono rimossi prima che il modello veda il testo rimanente.
  - Esempio: `hey /status` attiva una risposta di stato e il testo rimanente continua nel flusso normale.
- Attualmente: `/help`, `/commands`, `/status`, `/whoami` (`/id`).
- I messaggi composti solo da comandi non autorizzati vengono ignorati silenziosamente, e i token inline `/...` vengono trattati come testo normale.
- **Comandi skill:** le skill `user-invocable` sono esposte come comandi slash. I nomi vengono sanitizzati in `a-z0-9_` (massimo 32 caratteri); i conflitti ricevono suffissi numerici (ad esempio `_2`).
  - `/skill <name> [input]` esegue una skill per nome (utile quando i limiti dei comandi nativi impediscono comandi per singola skill).
  - Per impostazione predefinita, i comandi skill vengono inoltrati al modello come richiesta normale.
  - Le skill possono facoltativamente dichiarare `command-dispatch: tool` per instradare il comando direttamente a uno strumento (deterministico, senza modello).
  - Esempio: `/prose` (plugin OpenProse) — vedi [OpenProse](/it/prose).
- **Argomenti dei comandi nativi:** Discord usa l'autocomplete per le opzioni dinamiche (e menu a pulsanti quando ometti argomenti obbligatori). Telegram e Slack mostrano un menu a pulsanti quando un comando supporta scelte e ometti l'argomento.

## `/tools`

`/tools` risponde a una domanda di runtime, non a una domanda di configurazione: **cosa questo agente può usare in questo momento in
questa conversazione**.

- Il valore predefinito di `/tools` è compatto e ottimizzato per una scansione rapida.
- `/tools verbose` aggiunge brevi descrizioni.
- Le superfici dei comandi nativi che supportano argomenti espongono lo stesso cambio di modalità come `compact|verbose`.
- I risultati sono limitati alla sessione, quindi cambiare agente, canale, thread, autorizzazione del mittente o modello può
  cambiare l'output.
- `/tools` include gli strumenti effettivamente raggiungibili a runtime, inclusi strumenti core, strumenti dei
  plugin connessi e strumenti posseduti dal canale.

Per la modifica di profili e override, usa il pannello Tools della Control UI o le superfici config/catalogo
invece di trattare `/tools` come un catalogo statico.

## Superfici di utilizzo (cosa compare dove)

- **Uso/quota del provider** (esempio: “Claude 80% left”) compare in `/status` per il provider del modello corrente quando il tracciamento dell'utilizzo è abilitato. OpenClaw normalizza le finestre dei provider in `% left`; per MiniMax, i campi percentuali solo-rimanenti vengono invertiti prima della visualizzazione, e le risposte `model_remains` preferiscono la voce del modello di chat più un'etichetta del piano con tag del modello.
- **Righe token/cache** in `/status` possono ripiegare sull'ultima voce di utilizzo della trascrizione quando lo snapshot live della sessione è scarno. I valori live non zero esistenti continuano comunque a prevalere, e il fallback alla trascrizione può anche recuperare l'etichetta del modello runtime attivo più un totale più ampio orientato al prompt quando i totali memorizzati mancano o sono inferiori.
- **Token/costo per risposta** è controllato da `/usage off|tokens|full` (aggiunto alle risposte normali).
- `/model status` riguarda **modelli/auth/endpoint**, non l'utilizzo.

## Selezione del modello (`/model`)

`/model` è implementato come direttiva.

Esempi:

```
/model
/model list
/model 3
/model openai/gpt-5.4
/model opus@anthropic:default
/model status
```

Note:

- `/model` e `/model list` mostrano un selettore compatto numerato (famiglia di modelli + provider disponibili).
- Su Discord, `/model` e `/models` aprono un selettore interattivo con menu a discesa per provider e modello più un passaggio Submit.
- `/model <#>` seleziona da quel selettore (e preferisce il provider corrente quando possibile).
- `/model status` mostra la vista dettagliata, incluso l'endpoint provider configurato (`baseUrl`) e la modalità API (`api`) quando disponibili.

## Override di debug

`/debug` ti permette di impostare override di configurazione **solo runtime** (in memoria, non su disco). Solo proprietario. Disabilitato per impostazione predefinita; abilitalo con `commands.debug: true`.

Esempi:

```
/debug show
/debug set messages.responsePrefix="[openclaw]"
/debug set channels.whatsapp.allowFrom=["+1555","+4477"]
/debug unset messages.responsePrefix
/debug reset
```

Note:

- Gli override si applicano immediatamente alle nuove letture della configurazione, ma **non** scrivono in `openclaw.json`.
- Usa `/debug reset` per cancellare tutti gli override e tornare alla configurazione su disco.

## Aggiornamenti della configurazione

`/config` scrive nella configurazione su disco (`openclaw.json`). Solo proprietario. Disabilitato per impostazione predefinita; abilitalo con `commands.config: true`.

Esempi:

```
/config show
/config show messages.responsePrefix
/config get messages.responsePrefix
/config set messages.responsePrefix="[openclaw]"
/config unset messages.responsePrefix
```

Note:

- La configurazione viene validata prima della scrittura; le modifiche non valide vengono rifiutate.
- Gli aggiornamenti di `/config` persistono dopo i riavvii.

## Aggiornamenti MCP

`/mcp` scrive le definizioni del server MCP gestite da OpenClaw sotto `mcp.servers`. Solo proprietario. Disabilitato per impostazione predefinita; abilitalo con `commands.mcp: true`.

Esempi:

```text
/mcp show
/mcp show context7
/mcp set context7={"command":"uvx","args":["context7-mcp"]}
/mcp unset context7
```

Note:

- `/mcp` memorizza la configurazione nella configurazione OpenClaw, non nelle impostazioni di progetto possedute da Pi.
- Gli adapter di runtime decidono quali transport sono effettivamente eseguibili.

## Aggiornamenti dei plugin

`/plugins` permette agli operatori di ispezionare i plugin rilevati e attivare/disattivare l'abilitazione nella configurazione. I flussi di sola lettura possono usare `/plugin` come alias. Disabilitato per impostazione predefinita; abilitalo con `commands.plugins: true`.

Esempi:

```text
/plugins
/plugins list
/plugin show context7
/plugins enable context7
/plugins disable context7
```

Note:

- `/plugins list` e `/plugins show` usano il rilevamento reale dei plugin rispetto al workspace corrente più la configurazione su disco.
- `/plugins enable|disable` aggiorna solo la configurazione del plugin; non installa né disinstalla i plugin.
- Dopo modifiche di abilitazione/disabilitazione, riavvia il gateway per applicarle.

## Note sulle superfici

- **Comandi testuali** vengono eseguiti nella normale sessione di chat (i DM condividono `main`, i gruppi hanno la propria sessione).
- **Comandi nativi** usano sessioni isolate:
  - Discord: `agent:<agentId>:discord:slash:<userId>`
  - Slack: `agent:<agentId>:slack:slash:<userId>` (prefisso configurabile tramite `channels.slack.slashCommand.sessionPrefix`)
  - Telegram: `telegram:slash:<userId>` (destina la sessione di chat tramite `CommandTargetSessionKey`)
- **`/stop`** punta alla sessione di chat attiva così da poter interrompere l'esecuzione corrente.
- **Slack:** `channels.slack.slashCommand` è ancora supportato per un singolo comando in stile `/openclaw`. Se abiliti `commands.native`, devi creare un comando slash Slack per ogni comando built-in (con gli stessi nomi di `/help`). I menu argomenti dei comandi per Slack vengono consegnati come pulsanti Block Kit effimeri.
  - Eccezione nativa Slack: registra `/agentstatus` (non `/status`) perché Slack riserva `/status`. Il testo `/status` continua comunque a funzionare nei messaggi Slack.

## Domande laterali BTW

`/btw` è una rapida **domanda laterale** sulla sessione corrente.

A differenza della chat normale:

- usa la sessione corrente come contesto di sfondo,
- viene eseguita come chiamata separata **senza strumenti** e one-shot,
- non modifica il contesto futuro della sessione,
- non viene scritta nella cronologia della trascrizione,
- viene consegnata come risultato laterale live invece che come normale messaggio dell'assistente.

Questo rende `/btw` utile quando vuoi un chiarimento temporaneo mentre
l'attività principale continua.

Esempio:

```text
/btw cosa stiamo facendo in questo momento?
```

Vedi [BTW Side Questions](/it/tools/btw) per il comportamento completo e i
dettagli UX del client.
