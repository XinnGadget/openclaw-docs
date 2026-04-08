---
read_when:
    - Estendere qa-lab o qa-channel
    - Aggiungere scenari QA supportati dal repository
    - Creare un'automazione QA più realistica attorno alla dashboard del Gateway
summary: Struttura dell'automazione QA privata per qa-lab, qa-channel, scenari predefiniti e report di protocollo
title: Automazione QA E2E
x-i18n:
    generated_at: "2026-04-08T02:14:03Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3b4aa5acc8e77303f4045d4f04372494cae21b89d2fdaba856dbb4855ced9d27
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# Automazione QA E2E

Lo stack QA privato è pensato per esercitare OpenClaw in modo più realistico,
con una forma simile a quella dei canali, rispetto a quanto possa fare un
singolo test unitario.

Componenti attuali:

- `extensions/qa-channel`: canale di messaggi sintetico con superfici per DM, canale, thread,
  reazione, modifica ed eliminazione.
- `extensions/qa-lab`: interfaccia utente di debug e bus QA per osservare la trascrizione,
  iniettare messaggi in ingresso ed esportare un report in Markdown.
- `qa/`: risorse predefinite supportate dal repository per l'attività iniziale e gli scenari QA
  di base.

L'attuale flusso operativo QA è un sito QA a due pannelli:

- Sinistra: dashboard del Gateway (Control UI) con l'agente.
- Destra: QA Lab, che mostra la trascrizione in stile Slack e il piano dello scenario.

Eseguilo con:

```bash
pnpm qa:lab:up
```

Questo compila il sito QA, avvia il percorso gateway supportato da Docker ed espone la
pagina QA Lab in cui un operatore o un ciclo di automazione può assegnare all'agente una
missione QA, osservare il comportamento reale del canale e registrare ciò che ha funzionato, fallito o
è rimasto bloccato.

Per un'iterazione più rapida dell'interfaccia utente di QA Lab senza ricompilare ogni volta l'immagine Docker,
avvia lo stack con un bundle QA Lab montato tramite bind:

```bash
pnpm openclaw qa docker-build-image
pnpm qa:lab:build
pnpm qa:lab:up:fast
pnpm qa:lab:watch
```

`qa:lab:up:fast` mantiene i servizi Docker su un'immagine precompilata e monta tramite bind
`extensions/qa-lab/web/dist` nel container `qa-lab`. `qa:lab:watch`
ricompila quel bundle a ogni modifica e il browser si ricarica automaticamente quando cambia l'hash
delle risorse di QA Lab.

## Risorse predefinite supportate dal repository

Le risorse predefinite si trovano in `qa/`:

- `qa/scenarios.md`

Queste sono intenzionalmente incluse in git in modo che il piano QA sia visibile sia agli esseri umani sia
all'agente. L'elenco di base dovrebbe rimanere abbastanza ampio da coprire:

- chat in DM e nei canali
- comportamento dei thread
- ciclo di vita delle azioni sui messaggi
- callback cron
- richiamo della memoria
- cambio di modello
- passaggio a subagent
- lettura del repository e della documentazione
- una piccola attività di build come Lobster Invaders

## Reportistica

`qa-lab` esporta un report di protocollo in Markdown dalla timeline del bus osservata.
Il report dovrebbe rispondere a:

- Cosa ha funzionato
- Cosa è fallito
- Cosa è rimasto bloccato
- Quali scenari di follow-up vale la pena aggiungere

## Documentazione correlata

- [Testing](/it/help/testing)
- [QA Channel](/it/channels/qa-channel)
- [Dashboard](/web/dashboard)
