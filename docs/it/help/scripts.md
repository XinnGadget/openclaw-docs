---
read_when:
    - Eseguire script dal repository
    - Aggiungere o modificare script in ./scripts
summary: 'Script del repository: scopo, ambito e note di sicurezza'
title: Script
x-i18n:
    generated_at: "2026-04-08T02:15:15Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3ecf1e9327929948fb75f80e306963af49b353c0aa8d3b6fa532ca964ff8b975
    source_path: help/scripts.md
    workflow: 15
---

# Script

La directory `scripts/` contiene script di supporto per flussi di lavoro locali e attività operative.
Usali quando un'attività è chiaramente legata a uno script; altrimenti preferisci la CLI.

## Convenzioni

- Gli script sono **facoltativi** a meno che non siano citati nella documentazione o nelle checklist di rilascio.
- Preferisci le superfici CLI quando esistono (esempio: il monitoraggio dell'autenticazione usa `openclaw models status --check`).
- Presumi che gli script siano specifici dell'host; leggili prima di eseguirli su una nuova macchina.

## Script di monitoraggio dell'autenticazione

Il monitoraggio dell'autenticazione è descritto in [Authentication](/it/gateway/authentication). Gli script in `scripts/` sono extra facoltativi per flussi di lavoro systemd/Termux su telefono.

## Helper di lettura GitHub

Usa `scripts/gh-read` quando vuoi che `gh` usi un token di installazione GitHub App per chiamate di lettura con ambito repository, lasciando il normale `gh` sul tuo accesso personale per le azioni di scrittura.

Variabili d'ambiente richieste:

- `OPENCLAW_GH_READ_APP_ID`
- `OPENCLAW_GH_READ_PRIVATE_KEY_FILE`

Variabili d'ambiente facoltative:

- `OPENCLAW_GH_READ_INSTALLATION_ID` quando vuoi saltare la ricerca dell'installazione basata sul repository
- `OPENCLAW_GH_READ_PERMISSIONS` come override separato da virgole per il sottoinsieme di autorizzazioni di lettura da richiedere

Ordine di risoluzione del repository:

- `gh ... -R owner/repo`
- `GH_REPO`
- `git remote origin`

Esempi:

- `scripts/gh-read pr view 123`
- `scripts/gh-read run list -R openclaw/openclaw`
- `scripts/gh-read api repos/openclaw/openclaw/pulls/123`

## Quando si aggiungono script

- Mantieni gli script mirati e documentati.
- Aggiungi una breve voce nella documentazione pertinente (o creane una se manca).
