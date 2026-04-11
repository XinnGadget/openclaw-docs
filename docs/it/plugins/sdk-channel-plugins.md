---
read_when:
    - Stai creando un nuovo plugin di canale di messaggistica
    - Vuoi collegare OpenClaw a una piattaforma di messaggistica
    - Devi comprendere la superficie dell'adattatore ChannelPlugin
sidebarTitle: Channel Plugins
summary: Guida passo passo per creare un plugin di canale di messaggistica per OpenClaw
title: Creare plugin di canale
x-i18n:
    generated_at: "2026-04-11T02:46:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8a026e924f9ae8a3ddd46287674443bcfccb0247be504261522b078e1f440aef
    source_path: plugins/sdk-channel-plugins.md
    workflow: 15
---

# Creare plugin di canale

Questa guida illustra passo dopo passo la creazione di un plugin di canale che collega OpenClaw a una piattaforma di messaggistica. Alla fine avrai un canale funzionante con sicurezza DM, pairing, threading delle risposte e messaggistica in uscita.

<Info>
  Se non hai mai creato prima un plugin OpenClaw, leggi prima
  [Per iniziare](/it/plugins/building-plugins) per la struttura di base del
  pacchetto e la configurazione del manifest.
</Info>

## Come funzionano i plugin di canale

I plugin di canale non hanno bisogno dei propri strumenti send/edit/react. OpenClaw mantiene un unico strumento `message` condiviso nel core. Il tuo plugin gestisce:

- **Configurazione** — risoluzione dell'account e procedura guidata di configurazione
- **Sicurezza** — policy DM e allowlist
- **Pairing** — flusso di approvazione DM
- **Grammatica della sessione** — come gli id di conversazione specifici del provider vengono mappati a chat di base, id di thread e fallback parent
- **Messaggistica in uscita** — invio di testo, media e sondaggi alla piattaforma
- **Threading** — come vengono organizzate in thread le risposte

Il core gestisce lo strumento `message` condiviso, il wiring dei prompt, la forma esterna della session key, la gestione generica di `:thread:` e il dispatch.

Se la tua piattaforma memorizza scope aggiuntivo all'interno degli id di conversazione, mantieni quel parsing nel plugin con `messaging.resolveSessionConversation(...)`. Questo è l'hook canonico per mappare `rawId` all'id di conversazione di base, all'id di thread opzionale, a `baseConversationId` esplicito e a eventuali `parentConversationCandidates`.
Quando restituisci `parentConversationCandidates`, mantienili ordinati dal parent più specifico a quello più ampio/conversazione di base.

I plugin inclusi che necessitano dello stesso parsing prima che il registro dei canali venga avviato possono anche esporre un file `session-key-api.ts` di primo livello con un export `resolveSessionConversation(...)` corrispondente. Il core usa quella superficie sicura per il bootstrap solo quando il registro dei plugin runtime non è ancora disponibile.

`messaging.resolveParentConversationCandidates(...)` rimane disponibile come fallback legacy di compatibilità quando un plugin ha bisogno solo di fallback parent sopra l'id generico/raw. Se esistono entrambi gli hook, il core usa prima `resolveSessionConversation(...).parentConversationCandidates` e ricorre a `resolveParentConversationCandidates(...)` solo quando l'hook canonico li omette.

## Approvazioni e capacità del canale

La maggior parte dei plugin di canale non richiede codice specifico per le approvazioni.

- Il core gestisce `/approve` nella stessa chat, i payload condivisi dei pulsanti di approvazione e la consegna generica di fallback.
- Preferisci un singolo oggetto `approvalCapability` nel plugin di canale quando il canale richiede un comportamento specifico per l'approvazione.
- `ChannelPlugin.approvals` è stato rimosso. Inserisci in `approvalCapability` i dettagli relativi a consegna, rendering, auth e supporto nativo per le approvazioni.
- `plugin.auth` serve solo per login/logout; il core non legge più da quell'oggetto gli hook auth delle approvazioni.
- `approvalCapability.authorizeActorAction` e `approvalCapability.getActionAvailabilityState` sono la superficie canonica per l'auth delle approvazioni.
- Usa `approvalCapability.getActionAvailabilityState` per la disponibilità auth delle approvazioni nella stessa chat.
- Se il tuo canale espone approvazioni exec native, usa `approvalCapability.getExecInitiatingSurfaceState` per lo stato della superficie di avvio/client nativo quando differisce dall'auth di approvazione nella stessa chat. Il core usa questo hook specifico per exec per distinguere `enabled` da `disabled`, decidere se il canale di avvio supporta approvazioni exec native e includere il canale nelle indicazioni di fallback per client nativi. `createApproverRestrictedNativeApprovalCapability(...)` compila questa parte per il caso comune.
- Usa `outbound.shouldSuppressLocalPayloadPrompt` o `outbound.beforeDeliverPayload` per comportamenti specifici del canale nel ciclo di vita del payload, come nascondere prompt locali di approvazione duplicati o inviare indicatori di digitazione prima della consegna.
- Usa `approvalCapability.delivery` solo per instradamento di approvazioni native o soppressione del fallback.
- Usa `approvalCapability.nativeRuntime` per fatti di approvazione nativi posseduti dal canale. Mantienilo lazy negli entrypoint caldi del canale con `createLazyChannelApprovalNativeRuntimeAdapter(...)`, che può importare il tuo modulo runtime su richiesta consentendo comunque al core di assemblare il ciclo di vita dell'approvazione.
- Usa `approvalCapability.render` solo quando un canale ha davvero bisogno di payload di approvazione personalizzati invece del renderer condiviso.
- Usa `approvalCapability.describeExecApprovalSetup` quando il canale vuole che la risposta nel percorso disabilitato spieghi esattamente quali manopole di configurazione servono per abilitare le approvazioni exec native. L'hook riceve `{ channel, channelLabel, accountId }`; i canali con account nominati dovrebbero renderizzare percorsi con scope dell'account come `channels.<channel>.accounts.<id>.execApprovals.*` invece dei valori predefiniti di primo livello.
- Se un canale può dedurre identità DM stabili simili al proprietario dalla configurazione esistente, usa `createResolvedApproverActionAuthAdapter` da `openclaw/plugin-sdk/approval-runtime` per limitare `/approve` nella stessa chat senza aggiungere logica core specifica per le approvazioni.
- Se un canale necessita della consegna di approvazioni native, mantieni il codice del canale focalizzato su normalizzazione del target e dettagli di trasporto/presentazione. Usa `createChannelExecApprovalProfile`, `createChannelNativeOriginTargetResolver`, `createChannelApproverDmTargetResolver` e `createApproverRestrictedNativeApprovalCapability` da `openclaw/plugin-sdk/approval-runtime`. Metti i dettagli specifici del canale dietro `approvalCapability.nativeRuntime`, idealmente tramite `createChannelApprovalNativeRuntimeAdapter(...)` o `createLazyChannelApprovalNativeRuntimeAdapter(...)`, così il core può assemblare l'handler e gestire il filtraggio delle richieste, l'instradamento, la deduplicazione, la scadenza, la sottoscrizione al gateway e gli avvisi di instradamento alternativo. `nativeRuntime` è suddiviso in alcune superfici più piccole:
- `availability` — se l'account è configurato e se una richiesta deve essere gestita
- `presentation` — mappa il view model condiviso dell'approvazione in payload nativi pending/resolved/expired o azioni finali
- `transport` — prepara i target e invia/aggiorna/elimina messaggi di approvazione nativi
- `interactions` — hook opzionali bind/unbind/clear-action per pulsanti o reazioni native
- `observe` — hook diagnostici opzionali per la consegna
- Se il canale necessita di oggetti posseduti dal runtime come un client, token, app Bolt o ricevitore webhook, registrali tramite `openclaw/plugin-sdk/channel-runtime-context`. Il registro generico del runtime context consente al core di avviare handler guidati dalle capacità a partire dallo stato di avvio del canale senza aggiungere glue wrapper specifico per le approvazioni.
- Ricorri alle superfici di livello più basso `createChannelApprovalHandler` o `createChannelNativeApprovalRuntime` solo quando la superficie guidata dalle capacità non è ancora abbastanza espressiva.
- I canali di approvazione nativa devono instradare sia `accountId` sia `approvalKind` attraverso questi helper. `accountId` mantiene la policy di approvazione multi-account limitata all'account bot corretto, e `approvalKind` mantiene disponibile al canale il comportamento di approvazione exec vs plugin senza branch hardcoded nel core.
- Il core ora gestisce anche gli avvisi di reinstradamento delle approvazioni. I plugin di canale non dovrebbero inviare i propri messaggi di follow-up "l'approvazione è andata nei DM / in un altro canale" da `createChannelNativeApprovalRuntime`; invece, esponi un instradamento accurato origin + DM dell'approvatore tramite gli helper condivisi delle capacità di approvazione e lascia che il core aggreghi le consegne effettive prima di pubblicare eventuali avvisi nella chat di avvio.
- Preserva end-to-end il tipo di id di approvazione consegnato. I client nativi non devono indovinare
  o riscrivere l'instradamento delle approvazioni exec vs plugin a partire dallo stato locale del canale.
- Tipi diversi di approvazione possono esporre intenzionalmente superfici native diverse.
  Esempi inclusi attuali:
  - Slack mantiene disponibile l'instradamento delle approvazioni native sia per id exec sia per id plugin.
  - Matrix mantiene lo stesso instradamento DM/canale nativo e la stessa UX a reazioni per approvazioni exec
    e plugin, pur consentendo che l'auth differisca per tipo di approvazione.
- `createApproverRestrictedNativeApprovalAdapter` esiste ancora come wrapper di compatibilità, ma il nuovo codice dovrebbe preferire il capability builder ed esporre `approvalCapability` nel plugin.

Per entrypoint caldi del canale, preferisci i sottopercorsi runtime più stretti quando ti serve solo una parte di questa famiglia:

- `openclaw/plugin-sdk/approval-auth-runtime`
- `openclaw/plugin-sdk/approval-client-runtime`
- `openclaw/plugin-sdk/approval-delivery-runtime`
- `openclaw/plugin-sdk/approval-gateway-runtime`
- `openclaw/plugin-sdk/approval-handler-adapter-runtime`
- `openclaw/plugin-sdk/approval-handler-runtime`
- `openclaw/plugin-sdk/approval-native-runtime`
- `openclaw/plugin-sdk/approval-reply-runtime`
- `openclaw/plugin-sdk/channel-runtime-context`

Allo stesso modo, preferisci `openclaw/plugin-sdk/setup-runtime`,
`openclaw/plugin-sdk/setup-adapter-runtime`,
`openclaw/plugin-sdk/reply-runtime`,
`openclaw/plugin-sdk/reply-dispatch-runtime`,
`openclaw/plugin-sdk/reply-reference` e
`openclaw/plugin-sdk/reply-chunking` quando non hai bisogno della superficie ombrello più ampia.

Per la configurazione iniziale in particolare:

- `openclaw/plugin-sdk/setup-runtime` copre gli helper di setup sicuri per il runtime:
  adapter di patch del setup sicuri per import (`createPatchedAccountSetupAdapter`,
  `createEnvPatchedAccountSetupAdapter`,
  `createSetupInputPresenceValidator`), output di lookup-note,
  `promptResolvedAllowFrom`, `splitSetupEntries` e i builder
  di setup-proxy delegati
- `openclaw/plugin-sdk/setup-adapter-runtime` è la superficie stretta dell'adapter
  sensibile all'ambiente per `createEnvPatchedAccountSetupAdapter`
- `openclaw/plugin-sdk/channel-setup` copre i builder di setup con installazione opzionale
  più alcune primitive sicure per il setup:
  `createOptionalChannelSetupSurface`, `createOptionalChannelSetupAdapter`,

Se il tuo canale supporta setup o auth guidati da env e i flussi generici di avvio/config
devono conoscere quei nomi env prima che il runtime venga caricato, dichiarali nel
manifest del plugin con `channelEnvVars`. Mantieni `envVars` del runtime del canale o costanti locali
solo per il testo rivolto all'operatore.
`createOptionalChannelSetupWizard`, `DEFAULT_ACCOUNT_ID`,
`createTopLevelChannelDmPolicy`, `setSetupChannelEnabled` e
`splitSetupEntries`

- usa la superficie più ampia `openclaw/plugin-sdk/setup` solo quando ti servono anche gli helper condivisi di setup/config più pesanti come
  `moveSingleAccountChannelSectionToDefaultAccount(...)`

Se il tuo canale vuole solo pubblicizzare "installa prima questo plugin" nelle superfici di setup,
preferisci `createOptionalChannelSetupSurface(...)`. L'adapter/la procedura guidata generati falliscono in modo chiuso su scritture di configurazione e finalizzazione, e riutilizzano lo stesso messaggio di installazione richiesta in validazione, finalizzazione e testo dei link alla documentazione.

Per altri percorsi caldi del canale, preferisci gli helper stretti invece delle superfici legacy più ampie:

- `openclaw/plugin-sdk/account-core`,
  `openclaw/plugin-sdk/account-id`,
  `openclaw/plugin-sdk/account-resolution` e
  `openclaw/plugin-sdk/account-helpers` per configurazione multi-account e
  fallback dell'account predefinito
- `openclaw/plugin-sdk/inbound-envelope` e
  `openclaw/plugin-sdk/inbound-reply-dispatch` per il wiring di route/envelope in ingresso e
  record-and-dispatch
- `openclaw/plugin-sdk/messaging-targets` per parsing/matching dei target
- `openclaw/plugin-sdk/outbound-media` e
  `openclaw/plugin-sdk/outbound-runtime` per caricamento dei media più delegate di identità/invio in uscita
- `openclaw/plugin-sdk/thread-bindings-runtime` per il ciclo di vita dei thread-binding
  e la registrazione degli adapter
- `openclaw/plugin-sdk/agent-media-payload` solo quando è ancora richiesto un layout legacy del campo payload agente/media
- `openclaw/plugin-sdk/telegram-command-config` per normalizzazione, validazione di duplicati/conflitti e contratto di configurazione stabile come fallback dei comandi personalizzati Telegram

I canali solo-auth di solito possono fermarsi al percorso predefinito: il core gestisce le approvazioni e il plugin espone solo capacità outbound/auth. I canali con approvazioni native come Matrix, Slack, Telegram e trasporti chat personalizzati dovrebbero usare gli helper nativi condivisi invece di implementare da soli l'intero ciclo di vita dell'approvazione.

## Policy delle menzioni in ingresso

Mantieni la gestione delle menzioni in ingresso divisa in due livelli:

- raccolta delle evidenze posseduta dal plugin
- valutazione della policy condivisa

Usa `openclaw/plugin-sdk/channel-inbound` per il livello condiviso.

Adatto alla logica locale del plugin:

- rilevamento delle risposte al bot
- rilevamento delle citazioni del bot
- controlli di partecipazione ai thread
- esclusioni di messaggi di servizio/sistema
- cache native della piattaforma necessarie per dimostrare la partecipazione del bot

Adatto all'helper condiviso:

- `requireMention`
- risultato di menzione esplicita
- allowlist di menzioni implicite
- bypass dei comandi
- decisione finale di salto

Flusso preferito:

1. Calcola i fatti locali sulle menzioni.
2. Passa questi fatti a `resolveInboundMentionDecision({ facts, policy })`.
3. Usa `decision.effectiveWasMentioned`, `decision.shouldBypassMention` e `decision.shouldSkip` nel tuo gate inbound.

```typescript
import {
  implicitMentionKindWhen,
  matchesMentionWithExplicit,
  resolveInboundMentionDecision,
} from "openclaw/plugin-sdk/channel-inbound";

const mentionMatch = matchesMentionWithExplicit(text, {
  mentionRegexes,
  mentionPatterns,
});

const facts = {
  canDetectMention: true,
  wasMentioned: mentionMatch.matched,
  hasAnyMention: mentionMatch.hasExplicitMention,
  implicitMentionKinds: [
    ...implicitMentionKindWhen("reply_to_bot", isReplyToBot),
    ...implicitMentionKindWhen("quoted_bot", isQuoteOfBot),
  ],
};

const decision = resolveInboundMentionDecision({
  facts,
  policy: {
    isGroup,
    requireMention,
    allowedImplicitMentionKinds: requireExplicitMention ? [] : ["reply_to_bot", "quoted_bot"],
    allowTextCommands,
    hasControlCommand,
    commandAuthorized,
  },
});

if (decision.shouldSkip) return;
```

`api.runtime.channel.mentions` espone gli stessi helper condivisi per le menzioni
per i plugin di canale inclusi che dipendono già dall'iniezione runtime:

- `buildMentionRegexes`
- `matchesMentionPatterns`
- `matchesMentionWithExplicit`
- `implicitMentionKindWhen`
- `resolveInboundMentionDecision`

I vecchi helper `resolveMentionGating*` restano in
`openclaw/plugin-sdk/channel-inbound` solo come export di compatibilità. Il nuovo codice
dovrebbe usare `resolveInboundMentionDecision({ facts, policy })`.

## Procedura guidata

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="Pacchetto e manifest">
    Crea i file standard del plugin. Il campo `channel` in `package.json` è
    ciò che rende questo un plugin di canale. Per la superficie completa dei metadati del pacchetto,
    vedi [Setup e configurazione del plugin](/it/plugins/sdk-setup#openclaw-channel):

    <CodeGroup>
    ```json package.json
    {
      "name": "@myorg/openclaw-acme-chat",
      "version": "1.0.0",
      "type": "module",
      "openclaw": {
        "extensions": ["./index.ts"],
        "setupEntry": "./setup-entry.ts",
        "channel": {
          "id": "acme-chat",
          "label": "Acme Chat",
          "blurb": "Collega OpenClaw ad Acme Chat."
        }
      }
    }
    ```

    ```json openclaw.plugin.json
    {
      "id": "acme-chat",
      "kind": "channel",
      "channels": ["acme-chat"],
      "name": "Acme Chat",
      "description": "Plugin di canale Acme Chat",
      "configSchema": {
        "type": "object",
        "additionalProperties": false,
        "properties": {
          "acme-chat": {
            "type": "object",
            "properties": {
              "token": { "type": "string" },
              "allowFrom": {
                "type": "array",
                "items": { "type": "string" }
              }
            }
          }
        }
      }
    }
    ```
    </CodeGroup>

  </Step>

  <Step title="Crea l'oggetto plugin di canale">
    L'interfaccia `ChannelPlugin` ha molte superfici adattatore opzionali. Inizia con
    il minimo — `id` e `setup` — e aggiungi adattatori secondo necessità.

    Crea `src/channel.ts`:

    ```typescript src/channel.ts
    import {
      createChatChannelPlugin,
      createChannelPluginBase,
    } from "openclaw/plugin-sdk/channel-core";
    import type { OpenClawConfig } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatApi } from "./client.js"; // client API della tua piattaforma

    type ResolvedAccount = {
      accountId: string | null;
      token: string;
      allowFrom: string[];
      dmPolicy: string | undefined;
    };

    function resolveAccount(
      cfg: OpenClawConfig,
      accountId?: string | null,
    ): ResolvedAccount {
      const section = (cfg.channels as Record<string, any>)?.["acme-chat"];
      const token = section?.token;
      if (!token) throw new Error("acme-chat: token is required");
      return {
        accountId: accountId ?? null,
        token,
        allowFrom: section?.allowFrom ?? [],
        dmPolicy: section?.dmSecurity,
      };
    }

    export const acmeChatPlugin = createChatChannelPlugin<ResolvedAccount>({
      base: createChannelPluginBase({
        id: "acme-chat",
        setup: {
          resolveAccount,
          inspectAccount(cfg, accountId) {
            const section =
              (cfg.channels as Record<string, any>)?.["acme-chat"];
            return {
              enabled: Boolean(section?.token),
              configured: Boolean(section?.token),
              tokenStatus: section?.token ? "available" : "missing",
            };
          },
        },
      }),

      // Sicurezza DM: chi può inviare messaggi al bot
      security: {
        dm: {
          channelKey: "acme-chat",
          resolvePolicy: (account) => account.dmPolicy,
          resolveAllowFrom: (account) => account.allowFrom,
          defaultPolicy: "allowlist",
        },
      },

      // Pairing: flusso di approvazione per nuovi contatti DM
      pairing: {
        text: {
          idLabel: "Nome utente Acme Chat",
          message: "Invia questo codice per verificare la tua identità:",
          notify: async ({ target, code }) => {
            await acmeChatApi.sendDm(target, `Pairing code: ${code}`);
          },
        },
      },

      // Threading: come vengono consegnate le risposte
      threading: { topLevelReplyToMode: "reply" },

      // Outbound: invia messaggi alla piattaforma
      outbound: {
        attachedResults: {
          sendText: async (params) => {
            const result = await acmeChatApi.sendMessage(
              params.to,
              params.text,
            );
            return { messageId: result.id };
          },
        },
        base: {
          sendMedia: async (params) => {
            await acmeChatApi.sendFile(params.to, params.filePath);
          },
        },
      },
    });
    ```

    <Accordion title="Cosa fa per te createChatChannelPlugin">
      Invece di implementare manualmente interfacce adattatore di basso livello, passi
      opzioni dichiarative e il builder le compone:

      | Opzione | Cosa collega |
      | --- | --- |
      | `security.dm` | Resolver di sicurezza DM con scope dai campi di configurazione |
      | `pairing.text` | Flusso di pairing DM basato su testo con scambio di codice |
      | `threading` | Resolver della modalità reply-to (fisso, con scope account o personalizzato) |
      | `outbound.attachedResults` | Funzioni di invio che restituiscono metadati del risultato (ID messaggio) |

      Puoi anche passare oggetti adattatore raw invece delle opzioni dichiarative
      se hai bisogno del pieno controllo.
    </Accordion>

  </Step>

  <Step title="Collega l'entry point">
    Crea `index.ts`:

    ```typescript index.ts
    import { defineChannelPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineChannelPluginEntry({
      id: "acme-chat",
      name: "Acme Chat",
      description: "Plugin di canale Acme Chat",
      plugin: acmeChatPlugin,
      registerCliMetadata(api) {
        api.registerCli(
          ({ program }) => {
            program
              .command("acme-chat")
              .description("Gestione Acme Chat");
          },
          {
            descriptors: [
              {
                name: "acme-chat",
                description: "Gestione Acme Chat",
                hasSubcommands: false,
              },
            ],
          },
        );
      },
      registerFull(api) {
        api.registerGatewayMethod(/* ... */);
      },
    });
    ```

    Inserisci i descrittori CLI posseduti dal canale in `registerCliMetadata(...)` così OpenClaw
    può mostrarli nell'help principale senza attivare l'intero runtime del canale,
    mentre i caricamenti completi normali continuano a rilevare gli stessi descrittori per la registrazione reale dei comandi.
    Mantieni `registerFull(...)` per il lavoro solo runtime.
    Se `registerFull(...)` registra metodi RPC del gateway, usa un prefisso
    specifico del plugin. I namespace admin del core (`config.*`,
    `exec.approvals.*`, `wizard.*`, `update.*`) restano riservati e vengono sempre
    risolti in `operator.admin`.
    `defineChannelPluginEntry` gestisce automaticamente la divisione tra modalità di registrazione. Vedi
    [Entry point](/it/plugins/sdk-entrypoints#definechannelpluginentry) per tutte
    le opzioni.

  </Step>

  <Step title="Aggiungi un setup entry">
    Crea `setup-entry.ts` per un caricamento leggero durante l'onboarding:

    ```typescript setup-entry.ts
    import { defineSetupPluginEntry } from "openclaw/plugin-sdk/channel-core";
    import { acmeChatPlugin } from "./src/channel.js";

    export default defineSetupPluginEntry(acmeChatPlugin);
    ```

    OpenClaw carica questo invece dell'entry completo quando il canale è disabilitato
    o non configurato. In questo modo evita di importare codice runtime pesante durante i flussi di setup.
    Vedi [Setup e configurazione](/it/plugins/sdk-setup#setup-entry) per i dettagli.

  </Step>

  <Step title="Gestisci i messaggi in ingresso">
    Il tuo plugin deve ricevere messaggi dalla piattaforma e inoltrarli a
    OpenClaw. Il pattern tipico è un webhook che verifica la richiesta e
    la inoltra tramite l'handler inbound del tuo canale:

    ```typescript
    registerFull(api) {
      api.registerHttpRoute({
        path: "/acme-chat/webhook",
        auth: "plugin", // auth gestita dal plugin (verifica tu stesso le firme)
        handler: async (req, res) => {
          const event = parseWebhookPayload(req);

          // Il tuo handler inbound inoltra il messaggio a OpenClaw.
          // Il wiring esatto dipende dal SDK della tua piattaforma —
          // vedi un esempio reale nel pacchetto plugin incluso Microsoft Teams o Google Chat.
          await handleAcmeChatInbound(api, event);

          res.statusCode = 200;
          res.end("ok");
          return true;
        },
      });
    }
    ```

    <Note>
      La gestione dei messaggi in ingresso è specifica del canale. Ogni plugin di canale gestisce
      la propria pipeline inbound. Guarda i plugin di canale inclusi
      (per esempio il pacchetto plugin Microsoft Teams o Google Chat) per pattern reali.
    </Note>

  </Step>

<a id="step-6-test"></a>
<Step title="Test">
Scrivi test colocati in `src/channel.test.ts`:

    ```typescript src/channel.test.ts
    import { describe, it, expect } from "vitest";
    import { acmeChatPlugin } from "./channel.js";

    describe("plugin acme-chat", () => {
      it("risolve l'account dalla configurazione", () => {
        const cfg = {
          channels: {
            "acme-chat": { token: "test-token", allowFrom: ["user1"] },
          },
        } as any;
        const account = acmeChatPlugin.setup!.resolveAccount(cfg, undefined);
        expect(account.token).toBe("test-token");
      });

      it("ispeziona l'account senza materializzare i segreti", () => {
        const cfg = {
          channels: { "acme-chat": { token: "test-token" } },
        } as any;
        const result = acmeChatPlugin.setup!.inspectAccount!(cfg, undefined);
        expect(result.configured).toBe(true);
        expect(result.tokenStatus).toBe("available");
      });

      it("segnala configurazione mancante", () => {
        const cfg = { channels: {} } as any;
        const result = acmeChatPlugin.setup!.inspectAccount!(cfg, undefined);
        expect(result.configured).toBe(false);
      });
    });
    ```

    ```bash
    pnpm test -- <bundled-plugin-root>/acme-chat/
    ```

    Per helper di test condivisi, vedi [Testing](/it/plugins/sdk-testing).

  </Step>
</Steps>

## Struttura dei file

```
<bundled-plugin-root>/acme-chat/
├── package.json              # metadati openclaw.channel
├── openclaw.plugin.json      # Manifest con schema di configurazione
├── index.ts                  # defineChannelPluginEntry
├── setup-entry.ts            # defineSetupPluginEntry
├── api.ts                    # Export pubblici (opzionale)
├── runtime-api.ts            # Export runtime interni (opzionale)
└── src/
    ├── channel.ts            # ChannelPlugin tramite createChatChannelPlugin
    ├── channel.test.ts       # Test
    ├── client.ts             # Client API della piattaforma
    └── runtime.ts            # Store runtime (se necessario)
```

## Argomenti avanzati

<CardGroup cols={2}>
  <Card title="Opzioni di threading" icon="git-branch" href="/it/plugins/sdk-entrypoints#registration-mode">
    Modalità di risposta fisse, con scope account o personalizzate
  </Card>
  <Card title="Integrazione dello strumento message" icon="puzzle" href="/it/plugins/architecture#channel-plugins-and-the-shared-message-tool">
    describeMessageTool e rilevamento delle azioni
  </Card>
  <Card title="Risoluzione del target" icon="crosshair" href="/it/plugins/architecture#channel-target-resolution">
    inferTargetChatType, looksLikeId, resolveTarget
  </Card>
  <Card title="Helper runtime" icon="settings" href="/it/plugins/sdk-runtime">
    TTS, STT, media, sottoagente tramite api.runtime
  </Card>
</CardGroup>

<Note>
Alcune superfici helper incluse esistono ancora per manutenzione e
compatibilità dei plugin inclusi. Non sono il pattern consigliato per i nuovi plugin di canale;
preferisci i sottopercorsi generici channel/setup/reply/runtime della superficie SDK
comune, a meno che tu non stia mantenendo direttamente quella famiglia di plugin inclusi.
</Note>

## Passaggi successivi

- [Plugin provider](/it/plugins/sdk-provider-plugins) — se il tuo plugin fornisce anche modelli
- [Panoramica SDK](/it/plugins/sdk-overview) — riferimento completo agli import dei sottopercorsi
- [Testing SDK](/it/plugins/sdk-testing) — utility di test e test di contratto
- [Manifest del plugin](/it/plugins/manifest) — schema completo del manifest
