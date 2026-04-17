---
read_when:
    - Configurare OpenClaw su Hostinger
    - Cerchi un VPS gestito per OpenClaw
    - Utilizzare OpenClaw 1-Click su Hostinger
summary: Ospita OpenClaw su Hostinger
title: Hostinger
x-i18n:
    generated_at: "2026-04-14T02:08:35Z"
    model: gpt-5.4
    provider: openai
    source_hash: cf173cdcf6344f8ee22e839a27f4e063a3a102186f9acc07c4a33d4794e2c034
    source_path: install/hostinger.md
    workflow: 15
---

# Hostinger

Esegui un Gateway OpenClaw persistente su [Hostinger](https://www.hostinger.com/openclaw) tramite un deployment gestito **1-Click** o un'installazione **VPS**.

## Prerequisiti

- Account Hostinger ([registrazione](https://www.hostinger.com/openclaw))
- Circa 5-10 minuti

## Opzione A: OpenClaw 1-Click

Il modo più rapido per iniziare. Hostinger gestisce l'infrastruttura, Docker e gli aggiornamenti automatici.

<Steps>
  <Step title="Acquista e avvia">
    1. Dalla [pagina OpenClaw di Hostinger](https://www.hostinger.com/openclaw), scegli un piano Managed OpenClaw e completa il checkout.

    <Note>
    Durante il checkout puoi selezionare crediti **Ready-to-Use AI** preacquistati e integrati immediatamente in OpenClaw: non servono account esterni né chiavi API di altri provider. Puoi iniziare a chattare subito. In alternativa, durante la configurazione puoi fornire la tua chiave di Anthropic, OpenAI, Google Gemini o xAI.
    </Note>

  </Step>

  <Step title="Seleziona un canale di messaggistica">
    Scegli uno o più canali da collegare:

    - **WhatsApp** -- scansiona il codice QR mostrato nella procedura guidata di configurazione.
    - **Telegram** -- incolla il token del bot da [BotFather](https://t.me/BotFather).

  </Step>

  <Step title="Completa l'installazione">
    Fai clic su **Finish** per distribuire l'istanza. Quando è pronta, accedi alla dashboard di OpenClaw da **OpenClaw Overview** in hPanel.
  </Step>

</Steps>

## Opzione B: OpenClaw su VPS

Più controllo sul tuo server. Hostinger distribuisce OpenClaw tramite Docker sul tuo VPS e tu lo gestisci tramite **Docker Manager** in hPanel.

<Steps>
  <Step title="Acquista un VPS">
    1. Dalla [pagina OpenClaw di Hostinger](https://www.hostinger.com/openclaw), scegli un piano OpenClaw su VPS e completa il checkout.

    <Note>
    Puoi selezionare crediti **Ready-to-Use AI** durante il checkout: sono preacquistati e integrati immediatamente in OpenClaw, così puoi iniziare a chattare senza account esterni né chiavi API di altri provider.
    </Note>

  </Step>

  <Step title="Configura OpenClaw">
    Una volta effettuato il provisioning del VPS, compila i campi di configurazione:

    - **Gateway token** -- generato automaticamente; salvalo per usarlo in seguito.
    - **Numero WhatsApp** -- il tuo numero con prefisso internazionale (facoltativo).
    - **Telegram bot token** -- da [BotFather](https://t.me/BotFather) (facoltativo).
    - **Chiavi API** -- necessarie solo se non hai selezionato i crediti Ready-to-Use AI durante il checkout.

  </Step>

  <Step title="Avvia OpenClaw">
    Fai clic su **Deploy**. Quando è in esecuzione, apri la dashboard di OpenClaw da hPanel facendo clic su **Open**.
  </Step>

</Steps>

Log, riavvii e aggiornamenti vengono gestiti direttamente dall'interfaccia Docker Manager in hPanel. Per aggiornare, premi **Update** in Docker Manager e verrà scaricata l'immagine più recente.

## Verifica la configurazione

Invia "Hi" al tuo assistente sul canale che hai collegato. OpenClaw risponderà e ti guiderà nella configurazione iniziale delle preferenze.

## Risoluzione dei problemi

**La dashboard non si carica** -- Attendi qualche minuto affinché il container completi il provisioning. Controlla i log di Docker Manager in hPanel.

**Il container Docker continua a riavviarsi** -- Apri i log di Docker Manager e cerca errori di configurazione (token mancanti, chiavi API non valide).

**Il bot Telegram non risponde** -- Invia il messaggio con il codice di abbinamento da Telegram direttamente come messaggio nella tua chat OpenClaw per completare la connessione.

## Passaggi successivi

- [Canali](/it/channels) -- collega Telegram, WhatsApp, Discord e altro
- [Configurazione del Gateway](/it/gateway/configuration) -- tutte le opzioni di configurazione
