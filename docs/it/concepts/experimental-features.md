---
read_when:
    - Vedi una chiave di configurazione `.experimental` e vuoi sapere se è stabile
    - Vuoi provare le funzionalità di runtime in anteprima senza confonderle con i valori predefiniti normali
    - Vuoi un unico posto in cui trovare i flag sperimentali attualmente documentati
summary: Cosa significano i flag sperimentali in OpenClaw e quali sono attualmente documentati
title: Funzionalità sperimentali
x-i18n:
    generated_at: "2026-04-15T14:40:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2d1c7b3d4cd56ef8a0bdab1deb9918e9b2c9a33f956d63193246087f8633dcf3
    source_path: concepts/experimental-features.md
    workflow: 15
---

# Funzionalità sperimentali

Le funzionalità sperimentali in OpenClaw sono **superfici di anteprima su base opt-in**. Sono
dietro flag espliciti perché hanno ancora bisogno di utilizzo nel mondo reale prima di
meritare un valore predefinito stabile o un contratto pubblico duraturo.

Trattale in modo diverso dalla configurazione normale:

- Tienile **disattivate per impostazione predefinita** a meno che la documentazione correlata non ti dica di provarne una.
- Aspettati che **struttura e comportamento cambino** più rapidamente rispetto alla configurazione stabile.
- Preferisci prima il percorso stabile quando ne esiste già uno.
- Se stai distribuendo OpenClaw su larga scala, testa i flag sperimentali in un ambiente
  più piccolo prima di integrarli in una baseline condivisa.

## Flag attualmente documentati

| Superficie               | Chiave                                                    | Usala quando                                                                                                   | Altro                                                                                         |
| ------------------------ | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Runtime del modello locale | `agents.defaults.experimental.localModelLean`           | Un backend locale più piccolo o più rigoroso va in difficoltà con la superficie completa degli strumenti predefiniti di OpenClaw | [Modelli locali](/it/gateway/local-models)                                                       |
| Ricerca nella memoria    | `agents.defaults.memorySearch.experimental.sessionMemory` | Vuoi che `memory_search` indicizzi le trascrizioni delle sessioni precedenti e accetti il costo aggiuntivo di archiviazione/indicizzazione | [Riferimento della configurazione della memoria](/it/reference/memory-config#session-memory-search-experimental) |
| Strumento di pianificazione strutturata | `tools.experimental.planTool`             | Vuoi che lo strumento strutturato `update_plan` sia esposto per il monitoraggio del lavoro in più fasi in runtime e interfacce compatibili | [Riferimento della configurazione del Gateway](/it/gateway/configuration-reference#toolsexperimental) |

## Modalità lean del modello locale

`agents.defaults.experimental.localModelLean: true` è una valvola di sfogo
per configurazioni di modelli locali più deboli. Riduce strumenti predefiniti pesanti come
`browser`, `cron` e `message` in modo che la struttura del prompt sia più piccola e meno fragile
per backend compatibili con OpenAI con contesto ridotto o più rigorosi.

Questa intenzionalmente **non** è la modalità normale. Se il tuo backend gestisce il
runtime completo senza problemi, lascia questa opzione disattivata.

## Sperimentale non significa nascosto

Se una funzionalità è sperimentale, OpenClaw dovrebbe dirlo chiaramente nella documentazione e nel
percorso di configurazione stesso. Quello che **non** dovrebbe fare è introdurre di nascosto un comportamento
di anteprima in una manopola predefinita dall'aspetto stabile e fingere che sia normale. È così che le
superfici di configurazione diventano disordinate.
