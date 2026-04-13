---
read_when:
    - Rozszerzanie qa-lab lub qa-channel
    - Dodawanie scenariuszy QA opartych na repozytorium
    - Tworzenie bardziej realistycznej automatyzacji QA wokół panelu Gateway
summary: Prywatny kształt automatyzacji QA dla qa-lab, qa-channel, scenariuszy z ziarnem i raportów protokołu
title: Automatyzacja QA E2E
x-i18n:
    generated_at: "2026-04-13T08:50:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: a4a4f5c765163565c95c2a071f201775fd9d8d60cad4ff25d71e4710559c1570
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# Automatyzacja QA E2E

Prywatny stos QA ma na celu testowanie OpenClaw w sposób bardziej realistyczny,
uformowany wokół kanałów, niż jest to możliwe w pojedynczym teście jednostkowym.

Obecne elementy:

- `extensions/qa-channel`: syntetyczny kanał wiadomości z powierzchniami dla DM, kanału, wątku,
  reakcji, edycji i usuwania.
- `extensions/qa-lab`: interfejs debuggera i magistrala QA do obserwowania transkryptu,
  wstrzykiwania wiadomości przychodzących i eksportowania raportu Markdown.
- `qa/`: zasoby seed oparte na repozytorium dla zadania początkowego i bazowych
  scenariuszy QA.

Obecny przepływ pracy operatora QA to dwupanelowa strona QA:

- Po lewej: panel Gateway (Control UI) z agentem.
- Po prawej: QA Lab, pokazujący transkrypt w stylu Slacka i plan scenariusza.

Uruchom za pomocą:

```bash
pnpm qa:lab:up
```

To buduje stronę QA, uruchamia ścieżkę Gateway opartą na Dockerze i udostępnia
stronę QA Lab, na której operator lub pętla automatyzacji może zlecić agentowi
misję QA, obserwować rzeczywiste zachowanie kanału oraz zapisywać, co zadziałało,
co się nie udało lub co pozostało zablokowane.

Aby szybciej iterować nad interfejsem QA Lab bez przebudowywania obrazu Dockera za każdym razem,
uruchom stos z podmontowanym bundle QA Lab:

```bash
pnpm openclaw qa docker-build-image
pnpm qa:lab:build
pnpm qa:lab:up:fast
pnpm qa:lab:watch
```

`qa:lab:up:fast` utrzymuje usługi Dockera na wcześniej zbudowanym obrazie i bind-mountuje
`extensions/qa-lab/web/dist` do kontenera `qa-lab`. `qa:lab:watch`
przebudowuje ten bundle przy zmianach, a przeglądarka automatycznie przeładowuje się,
gdy zmienia się hash zasobów QA Lab.

Aby uruchomić ścieżkę smoke Matrix z rzeczywistym transportem, użyj:

```bash
pnpm openclaw qa matrix
```

Ta ścieżka udostępnia jednorazowy homeserver Tuwunel w Dockerze, rejestruje
tymczasowych użytkowników drivera, SUT i obserwatora, tworzy jeden prywatny pokój,
a następnie uruchamia rzeczywisty Plugin Matrix wewnątrz podrzędnego Gateway QA. Ścieżka z żywym transportem utrzymuje konfigurację
podrzędną ograniczoną do testowanego transportu, więc Matrix działa bez
`qa-channel` w konfiguracji podrzędnej.

Aby uruchomić ścieżkę smoke Telegram z rzeczywistym transportem, użyj:

```bash
pnpm openclaw qa telegram
```

Ta ścieżka jest kierowana do jednej rzeczywistej prywatnej grupy Telegram zamiast
udostępniać jednorazowy serwer. Wymaga `OPENCLAW_QA_TELEGRAM_GROUP_ID`,
`OPENCLAW_QA_TELEGRAM_DRIVER_BOT_TOKEN` oraz
`OPENCLAW_QA_TELEGRAM_SUT_BOT_TOKEN`, a także dwóch różnych botów w tej samej
prywatnej grupie. Bot SUT musi mieć nazwę użytkownika Telegram, a obserwacja
bot-bot działa najlepiej, gdy oba boty mają włączony tryb Bot-to-Bot Communication Mode
w `@BotFather`.

Ścieżki z żywym transportem współdzielą teraz jeden mniejszy kontrakt zamiast tego,
żeby każda definiowała własny kształt listy scenariuszy:

`qa-channel` pozostaje szerokim syntetycznym zestawem testów zachowania produktu i nie jest częścią
macierzy pokrycia dla żywego transportu.

| Ścieżka  | Canary | Bramka wzmianek | Blokada allowlisty | Odpowiedź najwyższego poziomu | Wznowienie po restarcie | Dalszy ciąg w wątku | Izolacja wątku | Obserwacja reakcji | Polecenie help |
| -------- | ------ | --------------- | ------------------ | ----------------------------- | ----------------------- | ------------------- | -------------- | ------------------ | -------------- |
| Matrix   | x      | x               | x                  | x                             | x                       | x                   | x              | x                  |                |
| Telegram | x      |                 |                    |                               |                         |                     |                |                    | x              |

Dzięki temu `qa-channel` pozostaje szerokim zestawem testów zachowania produktu, podczas gdy Matrix,
Telegram i przyszłe żywe transporty współdzielą jedną jawną checklistę kontraktu transportowego.

Aby uruchomić ścieżkę z jednorazową maszyną wirtualną Linux bez włączania Dockera do ścieżki QA, użyj:

```bash
pnpm openclaw qa suite --runner multipass --scenario channel-chat-baseline
```

To uruchamia świeżego gościa Multipass, instaluje zależności, buduje OpenClaw
wewnątrz gościa, uruchamia `qa suite`, a następnie kopiuje zwykły raport QA i
podsumowanie z powrotem do `.artifacts/qa-e2e/...` na hoście.
Ponownie wykorzystuje to samo zachowanie wyboru scenariuszy co `qa suite` na hoście.
Uruchomienia hosta i pakietu Multipass domyślnie wykonują równolegle wiele wybranych scenariuszy
z izolowanymi workerami Gateway, maksymalnie do 64 workerów lub liczby wybranych
scenariuszy. Użyj `--concurrency <count>`, aby dostroić liczbę workerów, lub
`--concurrency 1` do wykonywania sekwencyjnego.
Uruchomienia live przekazują obsługiwane wejścia autoryzacji QA, które są praktyczne dla
gościa: klucze dostawcy oparte na env, ścieżkę konfiguracji dostawcy QA live oraz
`CODEX_HOME`, jeśli jest obecne. Utrzymuj `--output-dir` w katalogu głównym repozytorium, aby gość
mógł zapisywać dane z powrotem przez zamontowany workspace.

## Seedy oparte na repozytorium

Zasoby seed znajdują się w `qa/`:

- `qa/scenarios/index.md`
- `qa/scenarios/*.md`

Są one celowo przechowywane w git, aby plan QA był widoczny zarówno dla ludzi, jak i dla
agenta.

`qa-lab` powinien pozostać generycznym runnerem Markdown. Każdy plik scenariusza Markdown jest
źródłem prawdy dla jednego uruchomienia testu i powinien definiować:

- metadane scenariusza
- odwołania do dokumentacji i kodu
- opcjonalne wymagania Plugin
- opcjonalną poprawkę konfiguracji Gateway
- wykonywalny `qa-flow`

Powierzchnia wielokrotnego użytku środowiska wykonawczego, która wspiera `qa-flow`, może pozostać
generyczna i przekrojowa. Na przykład scenariusze Markdown mogą łączyć pomocniki po stronie
transportu z pomocnikami po stronie przeglądarki, które sterują osadzonym Control UI przez
powierzchnię Gateway `browser.request`, bez dodawania runnera specjalnego przypadku.

Lista bazowa powinna pozostać wystarczająco szeroka, aby obejmować:

- czat DM i kanałowy
- zachowanie wątków
- cykl życia akcji wiadomości
- wywołania zwrotne Cron
- przywoływanie pamięci
- przełączanie modeli
- przekazanie do subagenta
- czytanie repozytorium i dokumentacji
- jedno małe zadanie build, takie jak Lobster Invaders

## Adaptery transportowe

`qa-lab` jest właścicielem generycznej powierzchni transportu dla scenariuszy QA w Markdown.
`qa-channel` jest pierwszym adapterem tej powierzchni, ale docelowy projekt jest szerszy:
przyszłe rzeczywiste lub syntetyczne kanały powinny podłączać się do tego samego runnera pakietu
zamiast dodawać runner QA specyficzny dla transportu.

Na poziomie architektury podział wygląda następująco:

- `qa-lab` jest właścicielem generycznego wykonywania scenariuszy, współbieżności workerów, zapisu artefaktów i raportowania.
- adapter transportu jest właścicielem konfiguracji Gateway, gotowości, obserwacji wejścia i wyjścia, działań transportowych oraz znormalizowanego stanu transportu.
- pliki scenariuszy Markdown w `qa/scenarios/` definiują przebieg testu; `qa-lab` udostępnia powierzchnię środowiska wykonawczego wielokrotnego użytku, która je wykonuje.

Wskazówki wdrożeniowe dla maintainerów dotyczące nowych adapterów kanałów znajdują się w
[Testing](/pl/help/testing#adding-a-channel-to-qa).

## Raportowanie

`qa-lab` eksportuje raport protokołu Markdown z obserwowanej osi czasu magistrali.
Raport powinien odpowiadać na pytania:

- Co zadziałało
- Co się nie udało
- Co pozostało zablokowane
- Jakie scenariusze follow-up warto dodać

Aby przeprowadzić kontrole charakteru i stylu, uruchom ten sam scenariusz dla wielu żywych referencji modeli
i zapisz oceniany raport Markdown:

```bash
pnpm openclaw qa character-eval \
  --model openai/gpt-5.4,thinking=xhigh \
  --model openai/gpt-5.2,thinking=xhigh \
  --model openai/gpt-5,thinking=xhigh \
  --model anthropic/claude-opus-4-6,thinking=high \
  --model anthropic/claude-sonnet-4-6,thinking=high \
  --model zai/glm-5.1,thinking=high \
  --model moonshot/kimi-k2.5,thinking=high \
  --model google/gemini-3.1-pro-preview,thinking=high \
  --judge-model openai/gpt-5.4,thinking=xhigh,fast \
  --judge-model anthropic/claude-opus-4-6,thinking=high \
  --blind-judge-models \
  --concurrency 16 \
  --judge-concurrency 16
```

Polecenie uruchamia lokalne podrzędne procesy Gateway QA, a nie Docker. Scenariusze
character eval powinny ustawiać personę przez `SOUL.md`, a następnie uruchamiać zwykłe tury użytkownika,
takie jak czat, pomoc dotycząca workspace i małe zadania plikowe. Kandydacki model
nie powinien być informowany, że jest oceniany. Polecenie zachowuje każdy pełny
transkrypt, zapisuje podstawowe statystyki uruchomienia, a następnie prosi modele sędziujące w trybie fast z
rozumowaniem `xhigh` o uszeregowanie uruchomień według naturalności, klimatu i humoru.
Użyj `--blind-judge-models` podczas porównywania dostawców: prompt sędziujący nadal otrzymuje
każdy transkrypt i status uruchomienia, ale referencje kandydatów są zastępowane neutralnymi
etykietami, takimi jak `candidate-01`; raport mapuje rankingi z powrotem na rzeczywiste referencje po
parsowaniu.
Uruchomienia kandydatów domyślnie używają poziomu myślenia `high`, a dla modeli OpenAI `xhigh`,
jeśli go obsługują. Zastąpienie dla konkretnego kandydata ustawiaj inline za pomocą
`--model provider/model,thinking=<level>`. `--thinking <level>` nadal ustawia
globalny fallback, a starsza forma `--model-thinking <provider/model=level>` jest
zachowana dla kompatybilności.
Referencje kandydatów OpenAI domyślnie używają trybu fast, tak aby priorytetowe przetwarzanie było używane tam,
gdzie dostawca to obsługuje. Dodaj inline `,fast`, `,no-fast` lub `,fast=false`, gdy
pojedynczy kandydat lub sędzia wymaga nadpisania. Przekaż `--fast` tylko wtedy, gdy chcesz
wymusić tryb fast dla każdego modelu kandydującego. Czasy trwania kandydatów i sędziów są
zapisywane w raporcie do analizy porównawczej, ale prompty sędziujące wyraźnie mówią,
aby nie tworzyć rankingu na podstawie szybkości.
Uruchomienia modeli kandydatów i sędziów domyślnie używają współbieżności 16. Obniż
`--concurrency` lub `--judge-concurrency`, gdy limity dostawcy lub obciążenie lokalnego Gateway
sprawiają, że uruchomienie staje się zbyt zaszumione.
Gdy nie zostanie przekazane żadne `--model` kandydata, character eval domyślnie używa
`openai/gpt-5.4`, `openai/gpt-5.2`, `openai/gpt-5`, `anthropic/claude-opus-4-6`,
`anthropic/claude-sonnet-4-6`, `zai/glm-5.1`,
`moonshot/kimi-k2.5` oraz
`google/gemini-3.1-pro-preview`, gdy nie zostanie przekazane `--model`.
Gdy nie zostanie przekazane żadne `--judge-model`, sędziowie domyślnie używają
`openai/gpt-5.4,thinking=xhigh,fast` oraz
`anthropic/claude-opus-4-6,thinking=high`.

## Powiązana dokumentacja

- [Testing](/pl/help/testing)
- [QA Channel](/pl/channels/qa-channel)
- [Dashboard](/web/dashboard)
