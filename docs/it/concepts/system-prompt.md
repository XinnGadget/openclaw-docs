---
read_when:
    - Modifica del testo del system prompt, dell'elenco degli strumenti o delle sezioni ora/heartbeat
    - Modifica del bootstrap del workspace o del comportamento di iniezione delle Skills
summary: Cosa contiene il system prompt di OpenClaw e come viene assemblato
title: System Prompt
x-i18n:
    generated_at: "2026-04-08T02:14:25Z"
    model: gpt-5.4
    provider: openai
    source_hash: e55fc886bc8ec47584d07c9e60dfacd964dc69c7db976ea373877dc4fe09a79a
    source_path: concepts/system-prompt.md
    workflow: 15
---

# System Prompt

OpenClaw crea un system prompt personalizzato per ogni esecuzione dell'agente. Il prompt è **di proprietà di OpenClaw** e non usa il prompt predefinito di pi-coding-agent.

Il prompt viene assemblato da OpenClaw e iniettato in ogni esecuzione dell'agente.

I plugin provider possono contribuire con indicazioni per il prompt consapevoli della cache senza sostituire l'intero prompt di proprietà di OpenClaw. Il runtime del provider può:

- sostituire un piccolo insieme di sezioni core denominate (`interaction_style`,
  `tool_call_style`, `execution_bias`)
- iniettare un **prefisso stabile** sopra il confine della cache del prompt
- iniettare un **suffisso dinamico** sotto il confine della cache del prompt

Usa i contributi di proprietà del provider per la regolazione specifica della famiglia di modelli. Mantieni la mutazione legacy del prompt `before_prompt_build` per compatibilità o per modifiche del prompt realmente globali, non per il normale comportamento del provider.

## Struttura

Il prompt è intenzionalmente compatto e usa sezioni fisse:

- **Tooling**: promemoria della fonte di verità degli strumenti strutturati più indicazioni di runtime sull'uso degli strumenti.
- **Safety**: breve promemoria dei guardrail per evitare comportamenti di ricerca del potere o aggiramento della supervisione.
- **Skills** (quando disponibili): indica al modello come caricare su richiesta le istruzioni delle skill.
- **OpenClaw Self-Update**: come ispezionare in sicurezza la configurazione con
  `config.schema.lookup`, modificare la configurazione con `config.patch`, sostituire l'intera
  configurazione con `config.apply` ed eseguire `update.run` solo su esplicita
  richiesta dell'utente. Anche lo strumento `gateway`, riservato al proprietario, rifiuta di riscrivere
  `tools.exec.ask` / `tools.exec.security`, incluse le alias legacy `tools.bash.*`
  che vengono normalizzate in quei percorsi exec protetti.
- **Workspace**: directory di lavoro (`agents.defaults.workspace`).
- **Documentation**: percorso locale della documentazione di OpenClaw (repo o pacchetto npm) e quando leggerla.
- **Workspace Files (injected)**: indica che i file bootstrap sono inclusi sotto.
- **Sandbox** (quando abilitato): indica il runtime sandboxed, i percorsi della sandbox e se è disponibile l'exec con privilegi elevati.
- **Current Date & Time**: ora locale dell'utente, fuso orario e formato dell'ora.
- **Reply Tags**: sintassi facoltativa dei tag di risposta per i provider supportati.
- **Heartbeats**: prompt heartbeat e comportamento di ack, quando gli heartbeat sono abilitati per l'agente predefinito.
- **Runtime**: host, OS, node, root del repo (quando rilevata), livello di thinking (una riga).
- **Reasoning**: livello di visibilità corrente + suggerimento per il toggle /reasoning.

La sezione Tooling include anche indicazioni di runtime per lavori di lunga durata:

- usare cron per follow-up futuri (`check back later`, promemoria, lavoro ricorrente)
  invece di cicli sleep di `exec`, trucchi di ritardo `yieldMs` o polling ripetuto di `process`
- usare `exec` / `process` solo per comandi che iniziano subito e continuano a essere eseguiti
  in background
- quando il risveglio automatico al completamento è abilitato, avviare il comando una sola volta e fare affidamento
  sul percorso di risveglio push-based quando emette output o fallisce
- usare `process` per log, stato, input o intervento quando è necessario
  ispezionare un comando in esecuzione
- se l'attività è più grande, preferire `sessions_spawn`; il completamento del sotto-agente è
  push-based e viene annunciato automaticamente al richiedente
- non fare polling di `subagents list` / `sessions_list` in un ciclo solo per attendere
  il completamento

Quando lo strumento sperimentale `update_plan` è abilitato, Tooling indica anche al
modello di usarlo solo per lavori multi-step non banali, mantenere esattamente un passaggio
`in_progress` ed evitare di ripetere l'intero piano dopo ogni aggiornamento.

I guardrail di sicurezza nel system prompt sono indicativi. Guidano il comportamento del modello ma non applicano policy. Usa tool policy, approvazioni exec, sandboxing e allowlist dei canali per un'applicazione rigorosa; gli operatori possono disabilitarli intenzionalmente.

Sui canali con card/pulsanti di approvazione nativi, il prompt di runtime ora indica all'
agente di fare prima affidamento su quell'interfaccia di approvazione nativa. Dovrebbe includere un comando manuale
`/approve` solo quando il risultato dello strumento indica che le approvazioni in chat non sono disponibili o che
l'approvazione manuale è l'unico percorso.

## Modalità del prompt

OpenClaw può generare system prompt più piccoli per i sotto-agenti. Il runtime imposta una
`promptMode` per ogni esecuzione (non è una configurazione visibile all'utente):

- `full` (predefinita): include tutte le sezioni sopra.
- `minimal`: usata per i sotto-agenti; omette **Skills**, **Memory Recall**, **OpenClaw
  Self-Update**, **Model Aliases**, **User Identity**, **Reply Tags**,
  **Messaging**, **Silent Replies** e **Heartbeats**. Tooling, **Safety**,
  Workspace, Sandbox, Current Date & Time (quando noto), Runtime e il contesto
  iniettato restano disponibili.
- `none`: restituisce solo la riga di identità di base.

Quando `promptMode=minimal`, i prompt extra iniettati sono etichettati come **Subagent
Context** invece che **Group Chat Context**.

## Iniezione del bootstrap del workspace

I file bootstrap vengono tagliati e aggiunti sotto **Project Context** così il modello vede il contesto di identità e profilo senza richiedere letture esplicite:

- `AGENTS.md`
- `SOUL.md`
- `TOOLS.md`
- `IDENTITY.md`
- `USER.md`
- `HEARTBEAT.md`
- `BOOTSTRAP.md` (solo nei workspace appena creati)
- `MEMORY.md` quando presente, altrimenti `memory.md` come fallback in minuscolo

Tutti questi file vengono **iniettati nella finestra di contesto** a ogni turno, a meno che
non si applichi un gate specifico del file. `HEARTBEAT.md` viene omesso nelle esecuzioni normali quando
gli heartbeat sono disabilitati per l'agente predefinito oppure
`agents.defaults.heartbeat.includeSystemPromptSection` è false. Mantieni i file
iniettati concisi, soprattutto `MEMORY.md`, che può crescere nel tempo e portare a
un uso del contesto inaspettatamente elevato e a compattazioni più frequenti.

> **Nota:** i file giornalieri `memory/*.md` **non** vengono iniettati automaticamente. Vengono
> accessibili su richiesta tramite gli strumenti `memory_search` e `memory_get`, quindi non
> contano nella finestra di contesto a meno che il modello non li legga esplicitamente.

I file di grandi dimensioni vengono troncati con un marcatore. La dimensione massima per file è controllata da
`agents.defaults.bootstrapMaxChars` (predefinito: 20000). Il contenuto bootstrap totale iniettato
tra i vari file è limitato da `agents.defaults.bootstrapTotalMaxChars`
(predefinito: 150000). I file mancanti iniettano un breve marcatore di file mancante. Quando si verifica il troncamento,
OpenClaw può iniettare un blocco di avviso in Project Context; controllalo con
`agents.defaults.bootstrapPromptTruncationWarning` (`off`, `once`, `always`;
predefinito: `once`).

Le sessioni dei sotto-agenti iniettano solo `AGENTS.md` e `TOOLS.md` (gli altri file bootstrap
vengono filtrati per mantenere piccolo il contesto del sotto-agente).

Gli hook interni possono intercettare questo passaggio tramite `agent:bootstrap` per modificare o sostituire
i file bootstrap iniettati (per esempio sostituendo `SOUL.md` con una persona alternativa).

Se vuoi rendere l'agente meno generico, inizia con
[SOUL.md Personality Guide](/it/concepts/soul).

Per ispezionare quanto contribuisce ogni file iniettato (grezzo vs iniettato, troncamento, oltre all'overhead dello schema degli strumenti), usa `/context list` o `/context detail`. Vedi [Context](/it/concepts/context).

## Gestione del tempo

Il system prompt include una sezione dedicata **Current Date & Time** quando il
fuso orario dell'utente è noto. Per mantenere stabile la cache del prompt, ora include solo il
**fuso orario** (nessun orologio dinamico o formato dell'ora).

Usa `session_status` quando l'agente ha bisogno dell'ora corrente; la card di stato
include una riga con timestamp. Lo stesso strumento può facoltativamente impostare un override
del modello per sessione (`model=default` lo cancella).

Configura con:

- `agents.defaults.userTimezone`
- `agents.defaults.timeFormat` (`auto` | `12` | `24`)

Vedi [Date & Time](/it/date-time) per i dettagli completi del comportamento.

## Skills

Quando esistono skill idonee, OpenClaw inietta un elenco compatto delle skill disponibili
(`formatSkillsForPrompt`) che include il **percorso del file** per ogni skill. Il
prompt indica al modello di usare `read` per caricare lo SKILL.md nella posizione
elencata (workspace, gestita o inclusa). Se non ci sono skill idonee, la
sezione Skills viene omessa.

L'idoneità include gate dei metadati della skill, controlli dell'ambiente/configurazione di runtime
e l'allowlist effettiva delle skill dell'agente quando `agents.defaults.skills` o
`agents.list[].skills` è configurato.

```
<available_skills>
  <skill>
    <name>...</name>
    <description>...</description>
    <location>...</location>
  </skill>
</available_skills>
```

Questo mantiene piccolo il prompt di base pur consentendo un uso mirato delle skill.

## Documentazione

Quando disponibile, il system prompt include una sezione **Documentation** che indica la
directory locale della documentazione di OpenClaw (o `docs/` nel workspace del repo oppure la documentazione del
pacchetto npm incluso) e menziona anche il mirror pubblico, il repo sorgente, la community Discord e
ClawHub ([https://clawhub.ai](https://clawhub.ai)) per la scoperta delle skill. Il prompt indica al modello di consultare prima la documentazione locale
per il comportamento, i comandi, la configurazione o l'architettura di OpenClaw, e di eseguire
`openclaw status` direttamente quando possibile (chiedendo all'utente solo quando non ha accesso).
