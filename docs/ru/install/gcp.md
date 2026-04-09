---
summary: "Запустить OpenClaw Gateway круглосуточно на виртуальной машине GCP Compute Engine (Docker) с устойчивым состоянием"
read_when:
  - Вам нужно, чтобы OpenClaw работал круглосуточно на GCP
  - Вам нужен Gateway промышленного уровня, работающий постоянно, на вашей собственной виртуальной машине
  - Вам нужен полный контроль над сохранением состояния, бинарными файлами и поведением при перезапуске
title: "GCP"
---

# OpenClaw на GCP Compute Engine (Docker, руководство по развёртыванию на VPS)

## Цель

Запустить устойчивый OpenClaw Gateway на виртуальной машине GCP Compute Engine с использованием Docker, с устойчивым состоянием, встроенными бинарными файлами и безопасным поведением при перезапуске.

Если вам нужен "OpenClaw 24/7 примерно за 5–12 долларов в месяц", это надёжное решение на Google Cloud.
Стоимость зависит от типа машины и региона; выберите наименьшую виртуальную машину, подходящую для вашей рабочей нагрузки, и увеличьте её, если возникнет ошибка нехватки памяти (OOM).

## Что мы делаем (простыми словами)?

- Создать проект GCP и включить биллинг
- Создать виртуальную машину Compute Engine
- Установить Docker (изолированная среда выполнения приложений)
- Запустить OpenClaw Gateway в Docker
- Сохранить `~/.openclaw` + `~/.openclaw/workspace` на хосте (данные сохраняются при перезапусках/пересборах)
- Получить доступ к интерфейсу управления с ноутбука через SSH-туннель

Подключённое состояние `~/.openclaw` включает в себя `openclaw.json`, файлы `agents/<agentId>/agent/auth-profiles.json` для каждого агента и `.env`.

Доступ к Gateway можно получить следующими способами:

- Через переадресацию портов SSH с ноутбука
- Через прямой доступ к порту, если вы самостоятельно управляете настройками брандмауэра и токенами

В этом руководстве используется Debian на GCP Compute Engine.
Ubuntu также подойдёт; адаптируйте пакеты соответствующим образом.
Для общего процесса работы с Docker см. [Docker](/install/docker).

---

## Быстрый путь (для опытных операторов)

1. Создать проект GCP + включить API Compute Engine
2. Создать виртуальную машину Compute Engine (e2-small, Debian 12, 20 ГБ)
3. Подключиться к виртуальной машине по SSH
4. Установить Docker
5. Клонировать репозиторий OpenClaw
6. Создать постоянные каталоги на хосте
7. Настроить `.env` и `docker-compose.yml`
8. Встроить необходимые бинарные файлы, собрать и запустить

---

## Что вам понадобится

- Аккаунт GCP (для e2-micro доступен бесплатный тариф)
- Установленный gcloud CLI (или использование Cloud Console)
- Доступ по SSH с ноутбука
- Базовые навыки работы с SSH и копированием/вставкой
- Примерно 20–30 минут
- Docker и Docker Compose
- Учётные данные для аутентификации модели
- Дополнительные учётные данные провайдера (опционально):
  - QR-код WhatsApp
  - Токен бота Telegram
  - OAuth для Gmail

---

<Steps>
  <Step title="Установить gcloud CLI (или использовать Console)">
    **Вариант A: gcloud CLI** (рекомендуется для автоматизации)

    Установите по ссылке [https://cloud.google.com/sdk/docs/install](https://cloud.google.com/sdk/docs/install)

    Инициализируйте и пройдите аутентификацию:

    ```bash
    gcloud init
    gcloud auth login
    ```

    **Вариант B: Cloud Console**

    Все шаги можно выполнить через веб-интерфейс по адресу [https://console.cloud.google.com](https://console.cloud.google.com)

  </Step>

  <Step title="Создать проект GCP">
    **CLI:**

    ```bash
    gcloud projects create my-openclaw-project --name="OpenClaw Gateway"
    gcloud config set project my-openclaw-project
    ```

    Включите биллинг по ссылке [https://console.cloud.google.com/billing](https://console.cloud.google.com/billing) (требуется для Compute Engine).

    Включите API Compute Engine:

    ```bash
    gcloud services enable compute.googleapis.com
    ```

    **Console:**

    1. Перейдите в IAM & Admin > Create Project
    2. Задайте имя и создайте проект
    3. Включите биллинг для проекта
    4. Перейдите в APIs & Services > Enable APIs > найдите "Compute Engine API" > Включите

  </Step>

  <Step title="Создать виртуальную машину">
    **Типы машин:**

    | Тип | Характеристики | Стоимость | Примечания |
    | --- | --- | --- | --- |
    | e2-medium | 2 vCPU, 4 ГБ ОЗУ | ~25 долларов в месяц | Наиболее надёжен для локальных сборок Docker |
    | e2-small | 2 vCPU, 2 ГБ ОЗУ | ~12 долларов в месяц | Минимально рекомендован для сборки Docker |
    | e2-micro | 2 vCPU (совместно используемые), 1 ГБ ОЗУ | Доступен по бесплатному тарифу | Часто завершается с ошибкой нехватки памяти при сборке Docker (exit 137) |

    **CLI:**

    ```bash
    gcloud compute instances create openclaw-gateway \
      --zone=us-central1-a \
      --machine-type=e2-small \
      --boot-disk-size=20GB \
      --image-family=debian-12 \
      --image-project=debian-cloud
    ```

    **Console:**

    1. Перейдите в Compute Engine > VM instances > Create instance
    2. Имя: `openclaw-gateway`
    3. Регион: `us-central1`, зона: `us-central1-a`
    4. Тип машины: `e2-small`
    5. Загрузочный диск: Debian 12, 20 ГБ
    6. Создать

  </Step>

  <Step title="Подключиться к виртуальной машине по SSH">
    **CLI:**

    ```bash
    gcloud compute ssh openclaw-gateway --zone=us-central1-a
    ```

    **Console:**

    Нажмите кнопку "SSH" рядом с вашей виртуальной машиной на панели управления Compute Engine.

    Примечание: распространение SSH-ключей может занять 1–2 минуты после создания виртуальной машины. Если подключение отклонено, подождите и повторите попытку.

  </Step>

  <Step title="Установить Docker (на виртуальной машине)">
    ```bash
    sudo apt-get update
    sudo apt-get install -y git curl ca-certificates
    curl -fsSL https://get.docker.com | sudo sh
    sudo usermod -aG docker $USER
    ```

    Выйдите из системы и войдите снова, чтобы изменения группы вступили в силу:

    ```bash
    exit
    ```

    Затем снова подключитесь по SSH:

    ```bash
    gcloud compute ssh openclaw-gateway --zone=us-central1-a
    ```

    Проверьте:

    ```bash
    docker --version
    docker compose version
    ```

  </Step>

  <Step title="Клонировать репозиторий OpenClaw">
    ```bash
    git clone https://github.com/openclaw/openclaw.git
    cd openclaw
    ```

    В этом руководстве предполагается, что вы соберёте собственный образ, чтобы гарантировать сохранение бинарных файлов.

  </Step>

  <Step title="Создать постоянные каталоги на хосте">
    Контейнеры Docker эфемерны.
    Все долговременные данные должны храниться на хосте.

    ```bash
    mkdir -p ~/.openclaw
    mkdir -p ~/.openclaw/workspace
    ```

  </Step>

  <Step title="Настроить переменные окружения">
    Создайте файл `.env` в корне репозитория.

    ```bash
    OPENCLAW_IMAGE=openclaw:latest
    OPENCLAW_GATEWAY_TOKEN=change-me-now
    OPENCLAW_GATEWAY_BIND=lan
    OPENCLAW_GATEWAY_PORT=18789

    OPENCLAW_CONFIG_DIR=/home/$USER/.openclaw
    OPENCLAW_WORKSPACE_DIR=/home/$USER/.openclaw/workspace

    GOG_KEYRING_PASSWORD=change-me-now
    XDG_CONFIG_HOME=/home/node/.openclaw
    ```

    Сгенерируйте надёжные секреты:

    ```bash
    openssl rand -hex 32
    ```

    **Не добавляйте этот файл в репозиторий.**

    Этот файл `.env` предназначен для переменных окружения контейнера/среды выполнения, таких как `OPENCLAW_GATEWAY_TOKEN`.
    Сохранённые учётные данные провайдера (OAuth/API-ключи) хранятся в подключённом каталоге `~/.openclaw/agents/<agentId