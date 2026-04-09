---
summary: "Безопасное обновление OpenClaw (глобальная установка или из исходного кода), а также стратегия отката"
read_when:
  - Обновление OpenClaw
  - Что-то сломалось после обновления
title: "Обновление"
---

# Обновление

Поддерживайте OpenClaw в актуальном состоянии.

## Рекомендованный способ: `openclaw update`

Самый быстрый способ обновления. Он определяет тип вашей установки (npm или git), загружает последнюю версию, запускает `openclaw doctor` и перезапускает шлюз.

```bash
openclaw update
```

Чтобы переключиться на другой канал или указать конкретную версию:

```bash
openclaw update --channel beta
openclaw update --tag main
openclaw update --dry-run   # предварительный просмотр без применения
```

Параметр `--channel beta` отдаёт предпочтение бета-версии, но среда выполнения возвращается к стабильной/последней версии, если тег beta отсутствует или старше последней стабильной версии. Используйте `--tag beta`, если вам нужен необработанный npm-тег beta dist-tag для разового обновления пакета.

См. [Каналы разработки](/install/development-channels) для ознакомления с семантикой каналов.

## Альтернативный способ: повторный запуск установщика

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

Добавьте `--no-onboard`, чтобы пропустить ввод в эксплуатацию. Для установок из исходного кода передайте `--install-method git --no-onboard`.

## Альтернативный способ: ручная установка через npm, pnpm или bun

```bash
npm i -g openclaw@latest
```

```bash
pnpm add -g openclaw@latest
```

```bash
bun add -g openclaw@latest
```

## Автообновление

Автообновление по умолчанию отключено. Включите его в файле `~/.openclaw/openclaw.json`:

```json5
{
  update: {
    channel: "stable",
    auto: {
      enabled: true,
      stableDelayHours: 6,
      stableJitterHours: 12,
      betaCheckIntervalHours: 1,
    },
  },
}
```

| Канал | Поведение |
| -------- | ------------------------------------------------------------------------------------------------------------- |
| `stable` | Ожидает `stableDelayHours`, затем применяет обновление с детерминированным джиттером в пределах `stableJitterHours` (постепенное развёртывание). |
| `beta` | Проверяет наличие обновлений каждые `betaCheckIntervalHours` (по умолчанию — каждый час) и применяет их немедленно. |
| `dev` | Автоматическое применение отключено. Используйте `openclaw update` вручную. |

Шлюз также выводит подсказку об обновлении при запуске (отключите с помощью `update.checkOnStart: false`).

## После обновления

<Steps>

### Запустите doctor

```bash
openclaw doctor
```

Мигрирует конфигурацию, проверяет политики DM и оценивает работоспособность шлюза. Подробности: [Doctor](/gateway/doctor)

### Перезапустите шлюз

```bash
openclaw gateway restart
```

### Проверьте работоспособность

```bash
openclaw health
```

</Steps>

## Откат

### Закрепление версии (npm)

```bash
npm i -g openclaw@<version>
openclaw doctor
openclaw gateway restart
```

Совет: команда `npm view openclaw version` показывает текущую опубликованную версию.

### Закрепление коммита (исходный код)

```bash
git fetch origin
git checkout "$(git rev-list -n 1 --before=\"2026-01-01\" origin/main)"
pnpm install && pnpm build
openclaw gateway restart
```

Чтобы вернуться к последней версии: `git checkout main && git pull`.

## Если вы застряли

- Снова запустите `openclaw doctor` и внимательно прочитайте вывод.
- При выполнении `openclaw update --channel dev` для установок из исходного кода средство обновления автоматически загружает `pnpm` при необходимости. Если вы видите ошибку загрузки pnpm/corepack, установите `pnpm` вручную (или повторно включите `corepack`) и повторите обновление.
- Ознакомьтесь с разделом: [Устранение неполадок](/gateway/troubleshooting)
- Задайте вопрос в Discord: [https://discord.gg/clawd](https://discord.gg/clawd)

## Связанные материалы

- [Обзор установки](/install) — все способы установки
- [Doctor](/gateway/doctor) — проверка работоспособности после обновлений
- [Миграция](/install/migrating) — руководства по миграции между основными версиями