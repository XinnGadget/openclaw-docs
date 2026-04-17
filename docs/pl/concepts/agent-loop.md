---
read_when:
    - Potrzebujesz dokładnego omówienia pętli agenta lub zdarzeń cyklu życia
summary: Cykl życia pętli agenta, strumienie i semantyka oczekiwania
title: Pętla agenta
x-i18n:
    generated_at: "2026-04-12T23:28:03Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3c2986708b444055340e0c91b8fce7d32225fcccf3d197b797665fd36b1991a5
    source_path: concepts/agent-loop.md
    workflow: 15
---

# Pętla agenta (OpenClaw)

Pętla agentowa to pełny, „rzeczywisty” przebieg działania agenta: przyjęcie danych wejściowych → zbudowanie kontekstu → wnioskowanie modelu →
wykonanie narzędzi → strumieniowanie odpowiedzi → trwały zapis. To autorytatywna ścieżka, która przekształca wiadomość
w działania i końcową odpowiedź, zachowując przy tym spójność stanu sesji.

W OpenClaw pętla to pojedynczy, serializowany przebieg na sesję, który emituje zdarzenia cyklu życia i strumienia,
gdy model myśli, wywołuje narzędzia i strumieniuje dane wyjściowe. Ten dokument wyjaśnia, jak ta autentyczna pętla
jest połączona od początku do końca.

## Punkty wejścia

- Gateway RPC: `agent` i `agent.wait`.
- CLI: polecenie `agent`.

## Jak to działa (wysoki poziom)

1. RPC `agent` weryfikuje parametry, rozwiązuje sesję (`sessionKey`/`sessionId`), zapisuje metadane sesji i natychmiast zwraca `{ runId, acceptedAt }`.
2. `agentCommand` uruchamia agenta:
   - rozwiązuje domyślne wartości modelu + thinking/verbose/trace
   - wczytuje snapshot Skills
   - wywołuje `runEmbeddedPiAgent` (środowisko uruchomieniowe pi-agent-core)
   - emituje **lifecycle end/error**, jeśli osadzona pętla tego nie zrobi
3. `runEmbeddedPiAgent`:
   - serializuje przebiegi przez kolejki per sesja i globalne
   - rozwiązuje profil modelu + auth i buduje sesję pi
   - subskrybuje zdarzenia pi i strumieniuje delty asystenta/narzędzi
   - wymusza limit czasu -> przerywa przebieg po jego przekroczeniu
   - zwraca payloady + metadane użycia
4. `subscribeEmbeddedPiSession` mostkuje zdarzenia pi-agent-core do strumienia OpenClaw `agent`:
   - zdarzenia narzędzi => `stream: "tool"`
   - delty asystenta => `stream: "assistant"`
   - zdarzenia cyklu życia => `stream: "lifecycle"` (`phase: "start" | "end" | "error"`)
5. `agent.wait` używa `waitForAgentRun`:
   - czeka na **lifecycle end/error** dla `runId`
   - zwraca `{ status: ok|error|timeout, startedAt, endedAt, error? }`

## Kolejkowanie + współbieżność

- Przebiegi są serializowane per klucz sesji (pas sesji), a opcjonalnie także przez pas globalny.
- Zapobiega to wyścigom narzędzi/sesji i utrzymuje spójność historii sesji.
- Kanały wiadomości mogą wybierać tryby kolejki (collect/steer/followup), które zasilają ten system pasów.
  Zobacz [Kolejka poleceń](/pl/concepts/queue).

## Przygotowanie sesji + obszaru roboczego

- Obszar roboczy jest rozwiązywany i tworzony; przebiegi w sandbox mogą zostać przekierowane do katalogu głównego obszaru roboczego sandbox.
- Skills są wczytywane (lub ponownie używane ze snapshotu) i wstrzykiwane do środowiska oraz promptu.
- Pliki bootstrap/kontekstu są rozwiązywane i wstrzykiwane do raportu promptu systemowego.
- Uzyskiwana jest blokada zapisu sesji; przed rozpoczęciem strumieniowania `SessionManager` jest otwierany i przygotowywany.

## Składanie promptu + prompt systemowy

- Prompt systemowy jest budowany z bazowego promptu OpenClaw, promptu Skills, kontekstu bootstrap i nadpisań dla danego przebiegu.
- Wymuszane są limity specyficzne dla modelu oraz tokeny zarezerwowane dla Compaction.
- Zobacz [Prompt systemowy](/pl/concepts/system-prompt), aby sprawdzić, co widzi model.

## Punkty hooków (gdzie można przechwycić)

OpenClaw ma dwa systemy hooków:

- **Hooki wewnętrzne** (hooki Gateway): skrypty sterowane zdarzeniami dla poleceń i zdarzeń cyklu życia.
- **Hooki Pluginów**: punkty rozszerzeń wewnątrz cyklu życia agenta/narzędzi i potoku Gateway.

### Hooki wewnętrzne (hooki Gateway)

- **`agent:bootstrap`**: uruchamia się podczas budowania plików bootstrap, zanim prompt systemowy zostanie ostatecznie sfinalizowany.
  Użyj tego, aby dodawać/usuwać pliki kontekstu bootstrap.
- Hooki poleceń: `/new`, `/reset`, `/stop` i inne zdarzenia poleceń (zobacz dokumentację Hooków).

Zobacz [Hooki](/pl/automation/hooks), aby znaleźć konfigurację i przykłady.

### Hooki Pluginów (cykl życia agenta + Gateway)

Są one uruchamiane wewnątrz pętli agenta lub potoku Gateway:

- **`before_model_resolve`**: uruchamiany przed sesją (bez `messages`), aby deterministycznie nadpisać dostawcę/model przed rozstrzygnięciem modelu.
- **`before_prompt_build`**: uruchamiany po wczytaniu sesji (z `messages`), aby wstrzyknąć `prependContext`, `systemPrompt`, `prependSystemContext` lub `appendSystemContext` przed wysłaniem promptu. Używaj `prependContext` dla dynamicznego tekstu per tura, a pól kontekstu systemowego dla stabilnych wskazówek, które powinny znajdować się w przestrzeni promptu systemowego.
- **`before_agent_start`**: hook zgodności wstecznej; może działać w dowolnej z obu faz — preferuj powyższe hooki jawne.
- **`before_agent_reply`**: uruchamiany po działaniach inline i przed wywołaniem LLM, pozwalając Pluginowi przejąć turę i zwrócić odpowiedź syntetyczną lub całkowicie wyciszyć turę.
- **`agent_end`**: umożliwia inspekcję końcowej listy wiadomości i metadanych przebiegu po zakończeniu.
- **`before_compaction` / `after_compaction`**: obserwują lub adnotują cykle Compaction.
- **`before_tool_call` / `after_tool_call`**: przechwytują parametry/wyniki narzędzi.
- **`before_install`**: umożliwia inspekcję wyników wbudowanego skanowania i opcjonalne zablokowanie instalacji Skills lub Pluginów.
- **`tool_result_persist`**: synchronicznie przekształca wyniki narzędzi, zanim zostaną zapisane w transkrypcie sesji.
- **`message_received` / `message_sending` / `message_sent`**: hooki wiadomości przychodzących i wychodzących.
- **`session_start` / `session_end`**: granice cyklu życia sesji.
- **`gateway_start` / `gateway_stop`**: zdarzenia cyklu życia Gateway.

Zasady decyzyjne hooków dla zabezpieczeń wyjścia/narzędzi:

- `before_tool_call`: `{ block: true }` jest rozstrzygające i zatrzymuje handlery o niższym priorytecie.
- `before_tool_call`: `{ block: false }` nic nie robi i nie usuwa wcześniejszej blokady.
- `before_install`: `{ block: true }` jest rozstrzygające i zatrzymuje handlery o niższym priorytecie.
- `before_install`: `{ block: false }` nic nie robi i nie usuwa wcześniejszej blokady.
- `message_sending`: `{ cancel: true }` jest rozstrzygające i zatrzymuje handlery o niższym priorytecie.
- `message_sending`: `{ cancel: false }` nic nie robi i nie usuwa wcześniejszego anulowania.

Zobacz [Hooki Pluginów](/pl/plugins/architecture#provider-runtime-hooks), aby znaleźć API hooków i szczegóły rejestracji.

## Strumieniowanie + częściowe odpowiedzi

- Delty asystenta są strumieniowane z pi-agent-core i emitowane jako zdarzenia `assistant`.
- Strumieniowanie blokowe może emitować częściowe odpowiedzi na `text_end` albo `message_end`.
- Strumieniowanie rozumowania może być emitowane jako osobny strumień albo jako odpowiedzi blokowe.
- Zobacz [Strumieniowanie](/pl/concepts/streaming), aby poznać zachowanie fragmentacji i odpowiedzi blokowych.

## Wykonywanie narzędzi + narzędzia wiadomości

- Zdarzenia rozpoczęcia/aktualizacji/zakończenia narzędzia są emitowane w strumieniu `tool`.
- Wyniki narzędzi są oczyszczane pod względem rozmiaru i payloadów obrazów przed logowaniem/emisją.
- Wysłania przez narzędzia wiadomości są śledzone, aby tłumić zduplikowane potwierdzenia asystenta.

## Kształtowanie odpowiedzi + tłumienie

- Końcowe payloady są składane z:
  - tekstu asystenta (i opcjonalnie rozumowania)
  - podsumowań narzędzi inline (gdy `verbose` jest włączone i dozwolone)
  - tekstu błędu asystenta, gdy model zwróci błąd
- Dokładny token wyciszający `NO_REPLY` / `no_reply` jest filtrowany z wychodzących
  payloadów.
- Duplikaty z narzędzi wiadomości są usuwane z końcowej listy payloadów.
- Jeśli nie pozostaną żadne renderowalne payloady, a narzędzie zwróciło błąd, emitowana jest awaryjna odpowiedź o błędzie narzędzia
  (chyba że narzędzie wiadomości już wysłało odpowiedź widoczną dla użytkownika).

## Compaction + ponowienia

- Auto-Compaction emituje zdarzenia strumienia `compaction` i może uruchomić ponowienie.
- Przy ponowieniu bufory w pamięci i podsumowania narzędzi są resetowane, aby uniknąć zduplikowanego wyjścia.
- Zobacz [Compaction](/pl/concepts/compaction), aby poznać potok Compaction.

## Strumienie zdarzeń (obecnie)

- `lifecycle`: emitowany przez `subscribeEmbeddedPiSession` (oraz awaryjnie przez `agentCommand`)
- `assistant`: strumieniowane delty z pi-agent-core
- `tool`: strumieniowane zdarzenia narzędzi z pi-agent-core

## Obsługa kanału czatu

- Delty asystenta są buforowane do wiadomości czatu `delta`.
- Końcowe `final` czatu jest emitowane przy **lifecycle end/error**.

## Limity czasu

- Domyślny `agent.wait`: 30 s (tylko oczekiwanie). Parametr `timeoutMs` go nadpisuje.
- Czas działania agenta: domyślne `agents.defaults.timeoutSeconds` to 172800 s (48 godzin); wymuszane przez timer przerwania w `runEmbeddedPiAgent`.
- Limit bezczynności LLM: `agents.defaults.llm.idleTimeoutSeconds` przerywa żądanie modelu, gdy w oknie bezczynności nie nadejdą żadne fragmenty odpowiedzi. Ustaw tę wartość jawnie dla wolnych modeli lokalnych albo dostawców rozumowania/wywołań narzędzi; ustaw na 0, aby wyłączyć. Jeśli nie jest ustawiona, OpenClaw używa `agents.defaults.timeoutSeconds`, jeśli jest skonfigurowane, w przeciwnym razie 120 s. Przebiegi wyzwalane przez Cron bez jawnego limitu czasu LLM lub agenta wyłączają watchdog bezczynności i polegają na zewnętrznym limicie czasu Cron.

## Gdzie wszystko może zakończyć się wcześniej

- Limit czasu agenta (przerwanie)
- AbortSignal (anulowanie)
- Rozłączenie Gateway lub limit czasu RPC
- Limit czasu `agent.wait` (dotyczy tylko oczekiwania, nie zatrzymuje agenta)

## Powiązane

- [Narzędzia](/pl/tools) — dostępne narzędzia agenta
- [Hooki](/pl/automation/hooks) — skrypty sterowane zdarzeniami, wyzwalane przez zdarzenia cyklu życia agenta
- [Compaction](/pl/concepts/compaction) — jak długie rozmowy są podsumowywane
- [Zgody na Exec](/pl/tools/exec-approvals) — bramki zatwierdzania poleceń powłoki
- [Thinking](/pl/tools/thinking) — konfiguracja poziomu thinking/rozumowania
