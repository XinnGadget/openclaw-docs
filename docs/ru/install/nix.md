---
summary: "Установите OpenClaw декларативно с помощью Nix"
read_when:
  - Вам нужна воспроизводимая установка с возможностью отката
  - Вы уже используете Nix/NixOS/Home Manager
  - Вы хотите, чтобы всё было зафиксировано и управлялось декларативно
title: "Nix"
---

# Установка через Nix

Установите OpenClaw декларативно с помощью **[nix-openclaw](https://github.com/openclaw/nix-openclaw)** — модуля Home Manager со всем необходимым.

<Info>
Репозиторий [nix-openclaw](https://github.com/openclaw/nix-openclaw) — это основной источник информации по установке через Nix. Эта страница представляет собой краткий обзор.
</Info>

## Что вы получаете

- Gateway + приложение для macOS + инструменты (whisper, spotify, камеры) — всё зафиксировано
- Сервис launchd, который сохраняется после перезагрузки
- Система плагинов с декларативной конфигурацией
- Мгновенный откат: `home-manager switch --rollback`

## Быстрый старт

<Steps>
  <Step title="Установите Determinate Nix">
    Если Nix ещё не установлен, следуйте инструкциям [установщика Determinate Nix](https://github.com/DeterminateSystems/nix-installer).
  </Step>
  <Step title="Создайте локальный flake">
    Используйте шаблон agent-first из репозитория nix-openclaw:
    ```bash
    mkdir -p ~/code/openclaw-local
    # Скопируйте templates/agent-first/flake.nix из репозитория nix-openclaw
    ```
  </Step>
  <Step title="Настройте секреты">
    Настройте токен мессенджера-бота и API-ключ провайдера модели. Обычные файлы в `~/.secrets/` подойдут.
  </Step>
  <Step title="Заполните заполнители в шаблоне и выполните переключение">
    ```bash
    home-manager switch
    ```
  </Step>
  <Step title="Проверьте работу">
    Убедитесь, что сервис launchd запущен и ваш бот отвечает на сообщения.
  </Step>
</Steps>

Полный список опций модуля и примеры смотрите в [README nix-openclaw](https://github.com/openclaw/nix-openclaw).

## Поведение во время выполнения в режиме Nix

Когда установлена переменная `OPENCLAW_NIX_MODE=1` (автоматически при использовании nix-openclaw), OpenClaw переходит в детерминированный режим, в котором отключены потоки автоматической установки.

Вы также можете установить её вручную:

```bash
export OPENCLAW_NIX_MODE=1
```

В macOS приложение с графическим интерфейсом не наследует переменные окружения оболочки автоматически. Включите режим Nix через defaults:

```bash
defaults write ai.openclaw.mac openclaw.nixMode -bool true
```

### Что меняется в режиме Nix

- Потоки автоматической установки и самоизменения отключены
- При отсутствии зависимостей выводятся сообщения об устранении проблем, специфичные для Nix
- В пользовательском интерфейсе отображается баннер режима Nix только для чтения

### Пути к конфигурации и состоянию

OpenClaw считывает конфигурацию JSON5 из `OPENCLAW_CONFIG_PATH` и сохраняет изменяемые данные в `OPENCLAW_STATE_DIR`. При работе в Nix явно задайте эти пути как управляемые Nix, чтобы состояние выполнения и конфигурация не попадали в неизменяемое хранилище.

| Переменная | Значение по умолчанию |
| --- | --- |
| `OPENCLAW_HOME` | `HOME` / `USERPROFILE` / `os.homedir()` |
| `OPENCLAW_STATE_DIR` | `~/.openclaw` |
| `OPENCLAW_CONFIG_PATH` | `$OPENCLAW_STATE_DIR/openclaw.json` |

## Связанные материалы

- [nix-openclaw](https://github.com/openclaw/nix-openclaw) — полное руководство по настройке
- [Wizard](/start/wizard) — настройка через CLI без Nix
- [Docker](/install/docker) — настройка в контейнере