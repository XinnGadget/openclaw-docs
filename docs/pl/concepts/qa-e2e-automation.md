---
read_when:
    - Rozszerzanie qa-lab lub qa-channel
    - Dodawanie scenariuszy QA wspieranych przez repozytorium
    - Budowanie bardziej realistycznej automatyzacji QA wokół panelu Gateway
summary: Prywatna struktura automatyzacji QA dla qa-lab, qa-channel, scenariuszy seed i raportów protokołu
title: Automatyzacja QA E2E
x-i18n:
    generated_at: "2026-04-06T03:06:51Z"
    model: gpt-5.4
    provider: openai
    source_hash: df35f353d5ab0e0432e6a828c82772f9a88edb41c20ec5037315b7ba310b28e6
    source_path: concepts/qa-e2e-automation.md
    workflow: 15
---

# Automatyzacja QA E2E

Prywatny stos QA ma ćwiczyć OpenClaw w bardziej realistyczny,
ukierunkowany na kanały sposób, niż może to zrobić pojedynczy test jednostkowy.

Obecne elementy:

- `extensions/qa-channel`: syntetyczny kanał wiadomości z powierzchniami DM, kanału, wątku,
  reakcji, edycji i usuwania.
- `extensions/qa-lab`: interfejs debuggera i magistrala QA do obserwowania transkryptu,
  wstrzykiwania wiadomości przychodzących i eksportowania raportu Markdown.
- `qa/`: zasoby seed wspierane przez repozytorium dla zadania startowego i bazowych
  scenariuszy QA.

Długoterminowym celem jest dwupanelowa witryna QA:

- Lewy panel: panel Gateway (Control UI) z agentem.
- Prawy panel: QA Lab pokazujący transkrypt w stylu Slacka i plan scenariusza.

Dzięki temu operator lub pętla automatyzacji może przydzielić agentowi misję QA, obserwować
rzeczywiste zachowanie kanału i zapisywać, co działało, co nie działało lub co pozostało zablokowane.

## Seedy wspierane przez repozytorium

Zasoby seed znajdują się w `qa/`:

- `qa/QA_KICKOFF_TASK.md`
- `qa/seed-scenarios.json`

Są one celowo przechowywane w git, aby plan QA był widoczny zarówno dla ludzi, jak i dla
agenta. Lista bazowa powinna pozostać wystarczająco szeroka, aby obejmować:

- DM i czat kanałowy
- zachowanie wątków
- cykl życia działań na wiadomościach
- callbacki cron
- przywoływanie pamięci
- przełączanie modeli
- przekazanie do subagenta
- odczyt repozytorium i dokumentacji
- jedno małe zadanie build, takie jak Lobster Invaders

## Raportowanie

`qa-lab` eksportuje raport protokołu Markdown z obserwowanej osi czasu magistrali.
Raport powinien odpowiadać na pytania:

- Co działało
- Co nie działało
- Co pozostało zablokowane
- Jakie scenariusze uzupełniające warto dodać

## Powiązana dokumentacja

- [Testowanie](/pl/help/testing)
- [Kanał QA](/channels/qa-channel)
- [Panel](/web/dashboard)
