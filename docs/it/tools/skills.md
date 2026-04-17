---
read_when:
    - Aggiungere o modificare Skills
    - Modificare il gating delle Skills o le regole di caricamento
summary: 'Skills: gestite vs workspace, regole di gating e configurazione/env wiring'
title: Skills
x-i18n:
    generated_at: "2026-04-11T02:48:01Z"
    model: gpt-5.4
    provider: openai
    source_hash: b1eaf130966950b6eb24f859d9a77ecbf81c6cb80deaaa6a3a79d2c16d83115d
    source_path: tools/skills.md
    workflow: 15
---

# Skills (OpenClaw)

OpenClaw usa cartelle di skill compatibili con **[AgentSkills](https://agentskills.io)** per insegnare all'agente come usare gli strumenti. Ogni skill è una directory che contiene un file `SKILL.md` con frontmatter YAML e istruzioni. OpenClaw carica le **skills incluse** più eventuali override locali e le filtra al momento del caricamento in base all'ambiente, alla configurazione e alla presenza dei binari.

## Posizioni e precedenza

OpenClaw carica le skills da queste origini:

1. **Cartelle di skill extra**: configurate con `skills.load.extraDirs`
2. **Skills incluse**: fornite con l'installazione (package npm o OpenClaw.app)
3. **Skills gestite/locali**: `~/.openclaw/skills`
4. **Skills agente personali**: `~/.agents/skills`
5. **Skills agente del progetto**: `<workspace>/.agents/skills`
6. **Skills workspace**: `<workspace>/skills`

Se c'è un conflitto tra nomi di skill, la precedenza è:

`<workspace>/skills` (massima) → `<workspace>/.agents/skills` → `~/.agents/skills` → `~/.openclaw/skills` → skills incluse → `skills.load.extraDirs` (minima)

## Skills per agente vs condivise

Nelle configurazioni **multi-agent**, ogni agente ha il proprio workspace. Ciò significa che:

- Le **skills per agente** si trovano in `<workspace>/skills` solo per quell'agente.
- Le **skills agente del progetto** si trovano in `<workspace>/.agents/skills` e si applicano a
  quel workspace prima della normale cartella workspace `skills/`.
- Le **skills agente personali** si trovano in `~/.agents/skills` e si applicano a tutti i
  workspace su quella macchina.
- Le **skills condivise** si trovano in `~/.openclaw/skills` (gestite/locali) e sono visibili
  a **tutti gli agenti** sulla stessa macchina.
- Le **cartelle condivise** possono anche essere aggiunte tramite `skills.load.extraDirs` (precedenza
  minima) se vuoi un pacchetto comune di skills usato da più agenti.

Se lo stesso nome di skill esiste in più di una posizione, si applica la normale precedenza:
vince il workspace, poi le skills agente del progetto, poi le skills agente personali,
poi quelle gestite/locali, poi quelle incluse, poi le cartelle extra.

## Allowlists di skill per agente

La **posizione** della skill e la **visibilità** della skill sono controlli separati.

- Posizione/precedenza decide quale copia di una skill con lo stesso nome vince.
- Le allowlist dell'agente decidono quali skill visibili un agente può effettivamente usare.

Usa `agents.defaults.skills` per una baseline condivisa, poi fai override per agente con
`agents.list[].skills`:

```json5
{
  agents: {
    defaults: {
      skills: ["github", "weather"],
    },
    list: [
      { id: "writer" }, // eredita github, weather
      { id: "docs", skills: ["docs-search"] }, // sostituisce i valori predefiniti
      { id: "locked-down", skills: [] }, // nessuna skill
    ],
  },
}
```

Regole:

- Ometti `agents.defaults.skills` per avere Skills senza restrizioni per impostazione predefinita.
- Ometti `agents.list[].skills` per ereditare `agents.defaults.skills`.
- Imposta `agents.list[].skills: []` per non avere Skills.
- Un elenco non vuoto in `agents.list[].skills` è l'insieme finale per quell'agente; non
  viene unito ai valori predefiniti.

OpenClaw applica l'insieme effettivo di Skills dell'agente alla creazione del prompt, alla
scoperta dei comandi slash delle skill, alla sincronizzazione del sandbox e agli snapshot delle skill.

## Plugin + skills

I plugin possono includere le proprie skills elencando directory `skills` in
`openclaw.plugin.json` (percorsi relativi alla radice del plugin). Le skill del plugin si caricano
quando il plugin è abilitato. Oggi quelle directory vengono unite nello stesso percorso
a bassa precedenza di `skills.load.extraDirs`, quindi una skill inclusa, gestita,
agente o workspace con lo stesso nome la sovrascrive.
Puoi applicare il gating tramite `metadata.openclaw.requires.config` sulla voce di configurazione
del plugin. Consulta [Plugin](/it/tools/plugin) per scoperta/configurazione e [Strumenti](/it/tools) per la
superficie strumenti che quelle skills insegnano.

## ClawHub (installazione + sincronizzazione)

ClawHub è il registro pubblico delle skills per OpenClaw. Sfoglialo su
[https://clawhub.ai](https://clawhub.ai). Usa i comandi nativi `openclaw skills`
per scoprire/installare/aggiornare skills, oppure la CLI separata `clawhub` quando
ti servono flussi di pubblicazione/sincronizzazione.
Guida completa: [ClawHub](/it/tools/clawhub).

Flussi comuni:

- Installare una skill nel tuo workspace:
  - `openclaw skills install <skill-slug>`
- Aggiornare tutte le skill installate:
  - `openclaw skills update --all`
- Sincronizzare (scansione + pubblicazione aggiornamenti):
  - `clawhub sync --all`

Il comando nativo `openclaw skills install` installa nella directory `skills/`
del workspace attivo. Anche la CLI separata `clawhub` installa in `./skills` sotto la
directory di lavoro corrente (o ricade sul workspace OpenClaw configurato).
OpenClaw rileva questo come `<workspace>/skills` nella sessione successiva.

## Note di sicurezza

- Tratta le skills di terze parti come **codice non attendibile**. Leggile prima di abilitarle.
- Preferisci esecuzioni sandboxate per input non attendibili e strumenti rischiosi. Consulta [Sandboxing](/it/gateway/sandboxing).
- La scoperta di skill nel workspace e nelle cartelle extra accetta solo radici skill e file `SKILL.md` il cui realpath risolto rimane all'interno della radice configurata.
- Le installazioni di dipendenze delle skill supportate dal Gateway (`skills.install`, onboarding e la UI impostazioni Skills) eseguono lo scanner integrato per codice pericoloso prima di eseguire i metadati dell'installer. I rilevamenti `critical` bloccano per impostazione predefinita a meno che il chiamante non imposti esplicitamente l'override per il pericoloso; i rilevamenti sospetti continuano invece solo a generare avvisi.
- `openclaw skills install <slug>` è diverso: scarica una cartella skill da ClawHub nel workspace e non usa il percorso di metadati installer descritto sopra.
- `skills.entries.*.env` e `skills.entries.*.apiKey` iniettano segreti nel processo **host**
  per quel turno dell'agente (non nel sandbox). Mantieni i segreti fuori dai prompt e dai log.
- Per un modello di minaccia più ampio e checklist, consulta [Sicurezza](/it/gateway/security).

## Formato (compatibile con AgentSkills + Pi)

`SKILL.md` deve includere almeno:

```markdown
---
name: image-lab
description: Generate or edit images via a provider-backed image workflow
---
```

Note:

- Seguiamo la specifica AgentSkills per layout/intento.
- Il parser usato dall'agente integrato supporta solo chiavi frontmatter **su singola riga**.
- `metadata` deve essere un **oggetto JSON su singola riga**.
- Usa `{baseDir}` nelle istruzioni per fare riferimento al percorso della cartella skill.
- Chiavi frontmatter facoltative:
  - `homepage` — URL mostrato come “Website” nella UI Skills di macOS (supportato anche tramite `metadata.openclaw.homepage`).
  - `user-invocable` — `true|false` (predefinito: `true`). Quando è `true`, la skill viene esposta come comando slash utente.
  - `disable-model-invocation` — `true|false` (predefinito: `false`). Quando è `true`, la skill viene esclusa dal prompt del modello (resta comunque disponibile tramite invocazione utente).
  - `command-dispatch` — `tool` (facoltativo). Quando impostato su `tool`, il comando slash bypassa il modello e viene inviato direttamente a uno strumento.
  - `command-tool` — nome dello strumento da invocare quando è impostato `command-dispatch: tool`.
  - `command-arg-mode` — `raw` (predefinito). Per il dispatch a uno strumento, inoltra la stringa raw degli argomenti allo strumento (senza parsing del core).

    Lo strumento viene invocato con i parametri:
    `{ command: "<raw args>", commandName: "<slash command>", skillName: "<skill name>" }`.

## Gating (filtri al caricamento)

OpenClaw **filtra le skills al momento del caricamento** usando `metadata` (JSON su singola riga):

```markdown
---
name: image-lab
description: Generate or edit images via a provider-backed image workflow
metadata:
  {
    "openclaw":
      {
        "requires": { "bins": ["uv"], "env": ["GEMINI_API_KEY"], "config": ["browser.enabled"] },
        "primaryEnv": "GEMINI_API_KEY",
      },
  }
---
```

Campi sotto `metadata.openclaw`:

- `always: true` — include sempre la skill (salta gli altri gate).
- `emoji` — emoji facoltativa usata dalla UI Skills di macOS.
- `homepage` — URL facoltativo mostrato come “Website” nella UI Skills di macOS.
- `os` — elenco facoltativo di piattaforme (`darwin`, `linux`, `win32`). Se impostato, la skill è idonea solo su quegli OS.
- `requires.bins` — elenco; ognuno deve esistere in `PATH`.
- `requires.anyBins` — elenco; almeno uno deve esistere in `PATH`.
- `requires.env` — elenco; la variabile di ambiente deve esistere **oppure** essere fornita nella configurazione.
- `requires.config` — elenco di percorsi `openclaw.json` che devono essere truthy.
- `primaryEnv` — nome della variabile di ambiente associata a `skills.entries.<name>.apiKey`.
- `install` — array facoltativo di specifiche installer usate dalla UI Skills di macOS (brew/node/go/uv/download).

Nota sul sandboxing:

- `requires.bins` viene controllato sull'**host** al momento del caricamento della skill.
- Se un agente è sandboxato, il binario deve esistere anche **dentro il container**.
  Installalo tramite `agents.defaults.sandbox.docker.setupCommand` (o un'immagine personalizzata).
  `setupCommand` viene eseguito una sola volta dopo la creazione del container.
  Le installazioni di package richiedono anche uscita di rete, un filesystem root scrivibile e un utente root nel sandbox.
  Esempio: la skill `summarize` (`skills/summarize/SKILL.md`) ha bisogno della CLI `summarize`
  nel container sandbox per poter essere eseguita lì.

Esempio di installer:

```markdown
---
name: gemini
description: Use Gemini CLI for coding assistance and Google search lookups.
metadata:
  {
    "openclaw":
      {
        "emoji": "♊️",
        "requires": { "bins": ["gemini"] },
        "install":
          [
            {
              "id": "brew",
              "kind": "brew",
              "formula": "gemini-cli",
              "bins": ["gemini"],
              "label": "Install Gemini CLI (brew)",
            },
          ],
      },
  }
---
```

Note:

- Se sono elencati più installer, il gateway sceglie una **sola** opzione preferita (brew quando disponibile, altrimenti node).
- Se tutti gli installer sono `download`, OpenClaw elenca ogni voce così puoi vedere gli artefatti disponibili.
- Le specifiche installer possono includere `os: ["darwin"|"linux"|"win32"]` per filtrare le opzioni in base alla piattaforma.
- Le installazioni Node rispettano `skills.install.nodeManager` in `openclaw.json` (predefinito: npm; opzioni: npm/pnpm/yarn/bun).
  Questo influisce solo sulle **installazioni di skill**; il runtime del Gateway dovrebbe comunque restare Node
  (Bun non è consigliato per WhatsApp/Telegram).
- La selezione dell'installer supportata dal Gateway è basata sulle preferenze, non solo su node:
  quando le specifiche di installazione mescolano tipi diversi, OpenClaw preferisce Homebrew quando
  `skills.install.preferBrew` è abilitato e `brew` esiste, poi `uv`, poi il
  node manager configurato, quindi altri fallback come `go` o `download`.
- Se ogni specifica di installazione è `download`, OpenClaw mostra tutte le opzioni di download
  invece di ridurle a un solo installer preferito.
- Installazioni Go: se `go` manca e `brew` è disponibile, il gateway installa prima Go tramite Homebrew e imposta `GOBIN` su `bin` di Homebrew quando possibile.
- Installazioni download: `url` (obbligatorio), `archive` (`tar.gz` | `tar.bz2` | `zip`), `extract` (predefinito: automatico quando viene rilevato un archivio), `stripComponents`, `targetDir` (predefinito: `~/.openclaw/tools/<skillKey>`).

Se `metadata.openclaw` non è presente, la skill è sempre idonea (a meno che
non sia disabilitata nella configurazione o bloccata da `skills.allowBundled` per le skill incluse).

## Override di configurazione (`~/.openclaw/openclaw.json`)

Le skill incluse/gestite possono essere attivate/disattivate e ricevere valori env:

```json5
{
  skills: {
    entries: {
      "image-lab": {
        enabled: true,
        apiKey: { source: "env", provider: "default", id: "GEMINI_API_KEY" }, // oppure stringa plaintext
        env: {
          GEMINI_API_KEY: "GEMINI_KEY_HERE",
        },
        config: {
          endpoint: "https://example.invalid",
          model: "nano-pro",
        },
      },
      peekaboo: { enabled: true },
      sag: { enabled: false },
    },
  },
}
```

Nota: se il nome della skill contiene trattini, racchiudi la chiave tra virgolette (JSON5 consente chiavi tra virgolette).

Se vuoi generazione/modifica di immagini stock direttamente in OpenClaw, usa lo
strumento core `image_generate` con `agents.defaults.imageGenerationModel` invece di una
skill inclusa. Gli esempi di skill qui sono per flussi di lavoro personalizzati o di terze parti.

Per l'analisi nativa delle immagini, usa lo strumento `image` con `agents.defaults.imageModel`.
Per la generazione/modifica nativa delle immagini, usa `image_generate` con
`agents.defaults.imageGenerationModel`. Se scegli `openai/*`, `google/*`,
`fal/*` o un altro modello immagine specifico del provider, aggiungi anche l'autenticazione/chiave API di quel provider.

Le chiavi di configurazione corrispondono al **nome della skill** per impostazione predefinita. Se una skill definisce
`metadata.openclaw.skillKey`, usa quella chiave sotto `skills.entries`.

Regole:

- `enabled: false` disabilita la skill anche se è inclusa/installata.
- `env`: iniettato **solo se** la variabile non è già impostata nel processo.
- `apiKey`: scorciatoia per le skill che dichiarano `metadata.openclaw.primaryEnv`.
  Supporta una stringa plaintext o un oggetto SecretRef (`{ source, provider, id }`).
- `config`: contenitore facoltativo per campi personalizzati per skill; le chiavi personalizzate devono stare qui.
- `allowBundled`: allowlist facoltativa solo per le skill **incluse**. Se impostata, sono idonee solo
  le skill incluse presenti nell'elenco (le skill gestite/workspace non sono interessate).

## Iniezione dell'ambiente (per esecuzione agente)

Quando inizia un'esecuzione dell'agente, OpenClaw:

1. Legge i metadati della skill.
2. Applica eventuali `skills.entries.<key>.env` o `skills.entries.<key>.apiKey` a
   `process.env`.
3. Costruisce il prompt di sistema con le skill **idonee**.
4. Ripristina l'ambiente originale dopo la fine dell'esecuzione.

Questo è **limitato all'esecuzione dell'agente**, non a un ambiente shell globale.

Per il backend `claude-cli` incluso, OpenClaw materializza anche lo stesso
snapshot idoneo come plugin temporaneo Claude Code e lo passa con
`--plugin-dir`. Claude Code può quindi usare il suo resolver di skill nativo mentre
OpenClaw continua a gestire precedenza, allowlist per agente, gating e
iniezione env/chiave API di `skills.entries.*`. Gli altri backend CLI usano solo il
catalogo del prompt.

## Snapshot della sessione (prestazioni)

OpenClaw crea uno snapshot delle skill idonee **quando una sessione inizia** e riutilizza quell'elenco per i turni successivi della stessa sessione. Le modifiche a skill o configurazione entrano in vigore nella prossima nuova sessione.

Le skill possono anche aggiornarsi a metà sessione quando il watcher delle skill è abilitato o quando appare un nuovo nodo remoto idoneo (vedi sotto). Consideralo come un **hot reload**: l'elenco aggiornato viene acquisito al turno agente successivo.

Se l'allowlist effettiva delle Skills dell'agente cambia per quella sessione, OpenClaw
aggiorna lo snapshot in modo che le skill visibili restino allineate con l'agente
corrente.

## Nodi macOS remoti (gateway Linux)

Se il Gateway è in esecuzione su Linux ma è connesso un **nodo macOS** **con `system.run` consentito** (la sicurezza delle approvazioni Exec non impostata su `deny`), OpenClaw può trattare come idonee le skill solo macOS quando i binari richiesti sono presenti su quel nodo. L'agente dovrebbe eseguire quelle skill tramite lo strumento `exec` con `host=node`.

Questo si basa sul fatto che il nodo riporti il supporto ai comandi e su una verifica dei binari tramite `system.run`. Se il nodo macOS in seguito va offline, le skill restano visibili; le invocazioni potrebbero fallire finché il nodo non si riconnette.

## Watcher delle skill (aggiornamento automatico)

Per impostazione predefinita, OpenClaw monitora le cartelle delle skill e incrementa lo snapshot delle skill quando i file `SKILL.md` cambiano. Configuralo sotto `skills.load`:

```json5
{
  skills: {
    load: {
      watch: true,
      watchDebounceMs: 250,
    },
  },
}
```

## Impatto sui token (elenco skill)

Quando le skill sono idonee, OpenClaw inietta un elenco XML compatto delle skill disponibili nel prompt di sistema (tramite `formatSkillsForPrompt` in `pi-coding-agent`). Il costo è deterministico:

- **Overhead base (solo quando ≥1 skill):** 195 caratteri.
- **Per skill:** 97 caratteri + la lunghezza dei valori XML-escaped di `<name>`, `<description>` e `<location>`.

Formula (caratteri):

```
total = 195 + Σ (97 + len(name_escaped) + len(description_escaped) + len(location_escaped))
```

Note:

- L'escaping XML espande `& < > " '` in entità (`&amp;`, `&lt;`, ecc.), aumentando la lunghezza.
- Il conteggio dei token varia in base al tokenizer del modello. Una stima approssimativa in stile OpenAI è ~4 caratteri/token, quindi **97 caratteri ≈ 24 token** per skill più la lunghezza effettiva dei tuoi campi.

## Ciclo di vita delle skill gestite

OpenClaw fornisce un insieme base di skill come **skills incluse** come parte dell'installazione
(package npm o OpenClaw.app). `~/.openclaw/skills` esiste per override locali (ad
esempio per fissare/applicare patch a una skill senza modificare la copia
inclusa). Le skill workspace sono di proprietà dell'utente e hanno precedenza su entrambe in caso di conflitto di nome.

## Riferimento della configurazione

Consulta [Configurazione delle Skills](/it/tools/skills-config) per lo schema di configurazione completo.

## Cerchi altre skill?

Sfoglia [https://clawhub.ai](https://clawhub.ai).

---

## Correlati

- [Creazione di Skills](/it/tools/creating-skills) — creare skill personalizzate
- [Configurazione delle Skills](/it/tools/skills-config) — riferimento della configurazione delle skill
- [Comandi slash](/it/tools/slash-commands) — tutti i comandi slash disponibili
- [Plugin](/it/tools/plugin) — panoramica del sistema di plugin
