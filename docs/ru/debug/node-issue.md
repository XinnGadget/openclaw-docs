---
summary: Заметки о сбое "__name is not a function" при работе с Node + tsx и способы обхода
read_when:
  - Отладка скриптов разработки только для Node или сбоев в режиме watch
  - Исследование сбоев загрузчика tsx/esbuild в OpenClaw
title: "Сбой Node + tsx"
---

# Сбой Node + tsx "\_\_name is not a function"

## Краткое описание

При запуске OpenClaw через Node с `tsx` происходит сбой при старте со следующей ошибкой:

```
[openclaw] Failed to start CLI: TypeError: __name is not a function
    at createSubsystemLogger (.../src/logging/subsystem.ts:203:25)
    at .../src/agents/auth-profiles/constants.ts:25:20
```

Проблема возникла после перехода от использования Bun к `tsx` в скриптах разработки (коммит `2871657e`, 06.01.2026). При использовании Bun тот же путь выполнения работал корректно.

## Окружение

- Node: v25.x (наблюдалось на v25.3.0)
- tsx: 4.21.0
- ОС: macOS (вероятность воспроизведения также на других платформах с Node 25)

## Воспроизведение (только для Node)

```bash
# в корне репозитория
node --version
pnpm install
node --import tsx src/entry.ts status
```

## Минимальное воспроизведение в репозитории

```bash
node --import tsx scripts/repro/tsx-name-repro.ts
```

## Проверка версий Node

- Node 25.3.0: сбой
- Node 22.22.0 (Homebrew `node@22`): сбой
- Node 24: пока не установлен; требуется проверка

## Заметки / гипотеза

- `tsx` использует esbuild для преобразования TS/ESM. Параметр `keepNames` в esbuild генерирует вспомогательную функцию `__name` и оборачивает определения функций в `__name(...)`.
- Сбой указывает на то, что `__name` существует, но не является функцией во время выполнения. Это означает, что вспомогательная функция отсутствует или перезаписана для данного модуля в пути загрузчика Node 25.
- Аналогичные проблемы с вспомогательной функцией `__name` сообщались в других проектах, использующих esbuild, когда функция отсутствовала или была переписана.

## История регрессии

- `2871657e` (06.01.2026): скрипты переведены с Bun на tsx, чтобы сделать Bun необязательным.
- До этого (при использовании Bun) команды `openclaw status` и `gateway:watch` работали корректно.

## Способы обхода

- Использовать Bun для скриптов разработки (временное возвращение к предыдущей конфигурации).
- Использовать Node + tsc watch, затем запускать скомпилированный вывод:

  ```bash
  pnpm exec tsc --watch --preserveWatchOutput
  node --watch openclaw.mjs status
  ```

- Локально подтверждено: `pnpm exec tsc -p tsconfig.json` + `node openclaw.mjs status` работает на Node 25.
- Отключить `keepNames` в esbuild в загрузчике TS, если это возможно (предотвратит вставку вспомогательной функции `__name`); в настоящее время tsx не предоставляет такой возможности.
- Протестировать LTS-версии Node (22/24) с `tsx`, чтобы выяснить, специфична ли проблема для Node 25.

## Ссылки

- [https://opennext.js.org/cloudflare/howtos/keep_names](https://opennext.js.org/cloudflare/howtos/keep_names)
- [https://esbuild.github.io/api/#keep-names](https://esbuild.github.io/api/#keep-names)
- [https://github.com/evanw/esbuild/issues/1031](https://github.com/evanw/esbuild/issues/1031)

## Следующие шаги

- Воспроизвести проблему на Node 22/24, чтобы подтвердить регрессию в Node 25.
- Протестировать ночную сборку `tsx` или зафиксировать более раннюю версию, если известна регрессия.
- Если проблема воспроизводится на LTS-версиях Node, отправить минимальное воспроизведение в вышестоящий проект вместе со стеком вызовов `__name`.