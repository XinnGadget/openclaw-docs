---
summary: "Автоматизированная защищённая установка OpenClaw с использованием Ansible, Tailscale VPN и изоляции с помощью брандмауэра"
read_when:
  - Вам нужна автоматизированная развёртывание сервера с усилением безопасности
  - Вам требуется настройка с изоляцией через брандмауэр и доступом через VPN
  - Вы развёртываете систему на удалённых серверах с Debian/Ubuntu
title: "Ansible"
---

# Установка Ansible

Разверните OpenClaw на рабочих серверах с помощью **[openclaw-ansible](https://github.com/openclaw/openclaw-ansible)** — автоматизированного установщика с архитектурой, ориентированной на безопасность.

<Info>
Репозиторий [openclaw-ansible](https://github.com/openclaw/openclaw-ansible) — это основной источник информации о развёртывании с Ansible. Эта страница представляет собой краткий обзор.
</Info>

## Предварительные требования

| Требование | Детали |
| ----------- | --------------------------------------------------------- |
| **ОС** | Debian 11+ или Ubuntu 20.04+ |
| **Доступ** | Права root или sudo |
| **Сеть** | Подключение к интернету для установки пакетов |
| **Ansible** | 2.14+ (устанавливается автоматически с помощью скрипта быстрого старта) |

## Что вы получаете

- **Безопасность с приоритетом на брандмауэр** — UFW + изоляция Docker (доступны только SSH и Tailscale)
- **Tailscale VPN** — безопасный удалённый доступ без публичного раскрытия сервисов
- **Docker** — изолированные контейнеры-песочницы, привязки только к localhost
- **Многоуровневая защита** — архитектура безопасности с 4 уровнями
- **Интеграция с Systemd** — автоматический запуск при загрузке с усилением безопасности
- **Настройка одной командой** — полное развёртывание за несколько минут

## Быстрый старт

Установка одной командой:

```bash
curl -fsSL https://raw.githubusercontent.com/openclaw/openclaw-ansible/main/install.sh | bash
```

## Что устанавливается

Плейбук Ansible устанавливает и настраивает:

1. **Tailscale** — mesh-VPN для безопасного удалённого доступа
2. **Брандмауэр UFW** — только порты SSH и Tailscale
3. **Docker CE + Compose V2** — для песочниц агентов
4. **Node.js 24 + pnpm** — зависимости среды выполнения (Node 22 LTS, на данный момент `22.14+`, поддерживается)
5. **OpenClaw** — на хосте, не в контейнере
6. **Сервис Systemd** — автоматический запуск с усилением безопасности

<Note>
Шлюз работает непосредственно на хосте (не в Docker), но песочницы агентов используют Docker для изоляции. Подробнее см. [Песочницы](/gateway/sandboxing).
</Note>

## Настройка после установки

<Steps>
  <Step title="Переключитесь на пользователя openclaw">
    ```bash
    sudo -i -u openclaw
    ```
  </Step>
  <Step title="Запустите мастер настройки">
    Скрипт после установки проведёт вас через процесс настройки параметров OpenClaw.
  </Step>
  <Step title="Подключите провайдеров сообщений">
    Войдите в WhatsApp, Telegram, Discord или Signal:
    ```bash
    openclaw channels login
    ```
  </Step>
  <Step title="Проверьте установку">
    ```bash
    sudo systemctl status openclaw
    sudo journalctl -u openclaw -f
    ```
  </Step>
  <Step title="Подключитесь к Tailscale">
    Присоединитесь к вашей VPN-сети для безопасного удалённого доступа.
  </Step>
</Steps>

### Быстрые команды

```bash
# Проверить статус сервиса
sudo systemctl status openclaw

# Просмотреть журналы в реальном времени
sudo journalctl -u openclaw -f

# Перезапустить шлюз
sudo systemctl restart openclaw

# Вход в провайдер (выполняется от имени пользователя openclaw)
sudo -i -u openclaw
openclaw channels login
```

## Архитектура безопасности

В развёртывании используется модель защиты с 4 уровнями:

1. **Брандмауэр (UFW)** — публично доступны только SSH (22) и Tailscale (41641/udp)
2. **VPN (Tailscale)** — шлюз доступен только через VPN-сеть
3. **Изоляция Docker** — цепочка DOCKER-USER в iptables предотвращает раскрытие внешних портов
4. **Усиление Systemd** — NoNewPrivileges, PrivateTmp, непривилегированный пользователь

Чтобы проверить внешнюю поверхность атаки:

```bash
nmap -p- YOUR_SERVER_IP
```

Должен быть открыт только порт 22 (SSH). Все остальные сервисы (шлюз, Docker) заблокированы.

Docker устанавливается для песочниц агентов (изолированное выполнение инструментов), а не для запуска самого шлюза. Подробнее о настройке песочниц см. [Многоагентные песочницы и инструменты](/tools/multi-agent-sandbox-tools).

## Ручная установка

Если вы предпочитаете ручной контроль над автоматизацией:

<Steps>
  <Step title="Установите предварительные требования">
    ```bash
    sudo apt update && sudo apt install -y ansible git
    ```
  </Step>
  <Step title="Клонируйте репозиторий">
    ```bash
    git clone https://github.com/openclaw/openclaw-ansible.git
    cd openclaw-ansible
    ```
  </Step>
  <Step title="Установите коллекции Ansible">
    ```bash
    ansible-galaxy collection install -r requirements.yml
    ```
  </Step>
  <Step title="Запустите плейбук">
    ```bash
    ./run-playbook.sh
    ```

    Альтернативно, запустите напрямую, а затем вручную выполните скрипт настройки:
    ```bash
    ansible-playbook playbook.yml --ask-become-pass
    # Затем выполните: /tmp/openclaw-setup.sh
    ```

  </Step>
</Steps>

## Обновление

Установщик Ansible настраивает OpenClaw для ручного обновления. Стандартный процесс обновления см. в разделе [Обновление](/install/updating).

Чтобы повторно запустить плейбук Ansible (например, для внесения изменений в конфигурацию):

```bash
cd openclaw-ansible
./run-playbook.sh
```

Это идемпотентная операция, её безопасно выполнять несколько раз.

## Устранение неполадок

<AccordionGroup>
  <Accordion title="Брандмауэр блокирует моё подключение">
    - Сначала убедитесь, что у вас есть доступ через Tailscale VPN
    - Доступ по SSH (порт 22) всегда разрешён
    - Шлюз доступен только через Tailscale — это предусмотрено дизайном
  </Accordion>
  <Accordion title="Сервис не запускается">
    ```bash
    # Проверьте журналы
    sudo journalctl -u openclaw -n 100

    # Проверьте права доступа
    sudo ls -la /opt/openclaw

    # Попробуйте запустить вручную
    sudo -i -u openclaw
    cd ~/openclaw
    openclaw gateway run
    ```

  </Accordion>
  <Accordion title="Проблемы с песочницей Docker">
    ```bash
    # Убедитесь, что Docker запущен
    sudo systemctl status docker

    # Проверьте образ песочницы
    sudo docker images | grep openclaw-sandbox

    # Соберите образ песочницы, если он отсутствует
    cd /opt/openclaw/openclaw
    sudo -u openclaw ./scripts/sandbox-setup.sh
    ```

  </Accordion>
  <Accordion title="Не удаётся войти в провайдер">
    Убедитесь, что вы выполняете команду от имени пользователя `openclaw`:
    ```bash
    sudo -i -u openclaw
    openclaw channels login
    ```
  </Accordion>
</AccordionGroup>

## Расширенная конфигурация

Для подробной информации об архитектуре безопасности и устранении неполадок см. репозиторий openclaw-ansible:

- [Архитектура безопасности](https://github.com/openclaw/openclaw-ansible/blob/main/docs/security.md)
- [Технические детали](https://github.com/openclaw/openclaw-ansible/blob/main/docs/architecture.md)
- [Руководство по устранению неполадок](https://github.com/openclaw/openclaw-ansible/blob/main/docs/troubleshooting.md)

## Связанные материалы

- [openclaw-ansible](https://github.com/openclaw/openclaw-ansible) — полное руководство по развёртыванию
- [Docker](/install/docker) — настройка шлюза в контейнере
- [Песочницы](/gateway/sandboxing) — настройка песочниц агентов
- [Многоагентные песочницы и инструменты](/tools/multi-agent-sandbox-tools) — изоляция для каждого агента