---
read_when:
    - Estensione di qa-lab o qa-channel
    - Aggiunta di scenari QA supportati dal repository
    - Creazione di un'automazione QA più realistica intorno alla dashboard del Gateway
summary: Struttura privata dell'automazione QA per qa-lab, qa-channel, scenari iniziali e report di protocollo
title: Automazione QA E2E
x-i18n:
    generated_at: "2026-04-08T06:00:44Z"
    model: gpt-5.4
    provider: openai
    source_hash: 57da147dc06abf9620290104e01a83b42182db1806514114fd9e8467492cda99
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# Automazione QA E2E

Lo stack QA privato è pensato per testare OpenClaw in un modo più realistico e
simile a un canale rispetto a quanto possa fare un singolo test unitario.

Componenti attuali:

- `extensions/qa-channel`: canale di messaggistica sintetico con superfici per messaggi diretti, canale, thread,
  reazioni, modifiche ed eliminazioni.
- `extensions/qa-lab`: interfaccia utente di debug e bus QA per osservare la trascrizione,
  inserire messaggi in ingresso ed esportare un report in Markdown.
- `qa/`: risorse iniziali supportate dal repository per il task iniziale e gli
  scenari QA di base.

L'attuale flusso operativo QA è un sito QA a due pannelli:

- Sinistra: dashboard del Gateway (Control UI) con l'agente.
- Destra: QA Lab, che mostra la trascrizione in stile Slack e il piano dello scenario.

Eseguilo con:

```bash
pnpm qa:lab:up
```

Questo comando compila il sito QA, avvia la corsia del gateway supportata da Docker ed espone la
pagina di QA Lab dove un operatore o un ciclo di automazione può assegnare all'agente una
missione QA, osservare il comportamento reale del canale e registrare cosa ha funzionato, cosa è fallito o
cosa è rimasto bloccato.

Per iterare più rapidamente sull'interfaccia utente di QA Lab senza ricompilare ogni volta l'immagine Docker,
avvia lo stack con un bundle di QA Lab montato tramite bind:

```bash
pnpm openclaw qa docker-build-image
pnpm qa:lab:build
pnpm qa:lab:up:fast
pnpm qa:lab:watch
```

`qa:lab:up:fast` mantiene i servizi Docker su un'immagine precompilata e monta tramite bind
`extensions/qa-lab/web/dist` nel container `qa-lab`. `qa:lab:watch`
ricompila quel bundle a ogni modifica e il browser si ricarica automaticamente quando l'hash
delle risorse di QA Lab cambia.

## Risorse iniziali supportate dal repository

Le risorse iniziali si trovano in `qa/`:

- `qa/scenarios/index.md`
- `qa/scenarios/*.md`

Questi file sono intenzionalmente in git in modo che il piano QA sia visibile sia agli esseri umani sia all'
agente. L'elenco di base dovrebbe rimanere sufficientemente ampio da coprire:

- chat in DM e nei canali
- comportamento dei thread
- ciclo di vita delle azioni sui messaggi
- callback cron
- richiamo della memoria
- cambio di modello
- passaggio a un subagente
- lettura del repository e della documentazione
- un piccolo task di build come Lobster Invaders

## Reportistica

`qa-lab` esporta un report di protocollo in Markdown dalla timeline del bus osservato.
Il report dovrebbe rispondere a:

- Cosa ha funzionato
- Cosa è fallito
- Cosa è rimasto bloccato
- Quali scenari di follow-up vale la pena aggiungere

## Documentazione correlata

- [Testing](/it/help/testing)
- [QA Channel](/it/channels/qa-channel)
- [Dashboard](/web/dashboard)
