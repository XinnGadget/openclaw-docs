---
summary: "Развёртывание OpenClaw Gateway в кластере Kubernetes с помощью Kustomize"
read_when:
  - Вы хотите запустить OpenClaw в кластере Kubernetes
  - Вы хотите протестировать OpenClaw в среде Kubernetes
title: "Kubernetes"
---

# OpenClaw в Kubernetes

Минимальная отправная точка для запуска OpenClaw в Kubernetes — не готовое к продакшену развёртывание. Охватывает основные ресурсы и предназначено для адаптации под вашу среду.

## Почему не Helm?

OpenClaw — это единый контейнер с несколькими конфигурационными файлами. Интересная настройка связана с содержимым агента (файлы Markdown, навыки, переопределения конфигурации), а не с шаблонизацией инфраструктуры. Kustomize обрабатывает оверлеи без накладных расходов, связанных с чартом Helm. Если ваше развёртывание станет более сложным, чарт Helm можно наложить поверх этих манифестов.

## Что вам понадобится

- Работающий кластер Kubernetes (AKS, EKS, GKE, k3s, kind, OpenShift и т. д.)
- `kubectl`, подключённый к вашему кластеру
- API-ключ как минимум для одного поставщика моделей

## Быстрый старт

```bash
# Замените на вашего поставщика: ANTHROPIC, GEMINI, OPENAI или OPENROUTER
export <PROVIDER>_API_KEY="..."
./scripts/k8s/deploy.sh

kubectl port-forward svc/openclaw 18789:18789 -n openclaw
open http://localhost:18789
```

Получите настроенный общий секрет для интерфейса управления (Control UI). Этот скрипт развёртывания по умолчанию создаёт аутентификацию по токену:

```bash
kubectl get secret openclaw-secrets -n openclaw -o jsonpath='{.data.OPENCLAW_GATEWAY_TOKEN}' | base64 -d
```

Для локальной отладки команда `./scripts/k8s/deploy.sh --show-token` выводит токен после развёртывания.

## Локальное тестирование с Kind

Если у вас нет кластера, создайте его локально с помощью [Kind](https://kind.sigs.k8s.io/):

```bash
./scripts/k8s/create-kind.sh           # автоматически определяет docker или podman
./scripts/k8s/create-kind.sh --delete  # удалить кластер
```

Затем выполните развёртывание как обычно с помощью `./scripts/k8s/deploy.sh`.

## Пошаговая инструкция

### 1) Развёртывание

**Вариант A** — API-ключ в окружении (один шаг):

```bash
# Замените на вашего поставщика: ANTHROPIC, GEMINI, OPENAI или OPENROUTER
export <PROVIDER>_API_KEY="..."
./scripts/k8s/deploy.sh
```

Скрипт создаёт секрет Kubernetes с API-ключом и автоматически сгенерированным токеном шлюза, затем выполняет развёртывание. Если секрет уже существует, текущий токен шлюза и ключи поставщиков, которые не изменяются, сохраняются.

**Вариант B** — создание секрета отдельно:

```bash
export <PROVIDER>_API_KEY="..."
./scripts/k8s/deploy.sh --create-secret
./scripts/k8s/deploy.sh
```

Используйте параметр `--show-token` с любой из команд, если хотите, чтобы токен выводился в stdout для локального тестирования.

### 2) Доступ к шлюзу

```bash
kubectl port-forward svc/openclaw 18789:18789 -n openclaw
open http://localhost:18789
```

## Что развёртывается

```
Пространство имён: openclaw (настраивается через OPENCLAW_NAMESPACE)
├── Deployment/openclaw        # Один под, init-контейнер + шлюз
├── Service/openclaw           # ClusterIP на порту 18789
├── PersistentVolumeClaim      # 10 ГиБ для состояния агента и конфигурации
├── ConfigMap/openclaw-config  # openclaw.json + AGENTS.md
└── Secret/openclaw-secrets    # Токен шлюза + API-ключи
```

## Настройка

### Инструкции для агента

Отредактируйте `AGENTS.md` в `scripts/k8s/manifests/configmap.yaml` и выполните повторное развёртывание:

```bash
./scripts/k8s/deploy.sh
```

### Конфигурация шлюза

Отредактируйте `openclaw.json` в `scripts/k8s/manifests/configmap.yaml`. Полный справочник см. в разделе [Конфигурация шлюза](/gateway/configuration).

### Добавление поставщиков

Выполните повторное развёртывание с экспортированными дополнительными ключами:

```bash
export ANTHROPIC_API_KEY="..."
export OPENAI_API_KEY="..."
./scripts/k8s/deploy.sh --create-secret
./scripts/k8s/deploy.sh
```

Существующие ключи поставщиков остаются в секрете, если вы их не перезапишете.

Или внесите изменения в секрет напрямую:

```bash
kubectl patch secret openclaw-secrets -n openclaw \
  -p '{"stringData":{"<PROVIDER>_API_KEY":"..."}}'
kubectl rollout restart deployment/openclaw -n openclaw
```

### Пользовательское пространство имён

```bash
OPENCLAW_NAMESPACE=my-namespace ./scripts/k8s/deploy.sh
```

### Пользовательский образ

Отредактируйте поле `image` в `scripts/k8s/manifests/deployment.yaml`:

```yaml
image: ghcr.io/openclaw/openclaw:latest # или укажите конкретную версию из https://github.com/openclaw/openclaw/releases
```

### Предоставление доступа помимо port-forward

Стандартные манифесты привязывают шлюз к loopback внутри пода. Это работает с `kubectl port-forward`, но не работает с Kubernetes `Service` или путём Ingress, который должен обращаться к IP пода.

Если вы хотите предоставить доступ к шлюзу через Ingress или балансировщик нагрузки:

- Измените привязку шлюза в `scripts/k8s/manifests/configmap.yaml` с `loopback` на привязку, не являющуюся loopback, которая соответствует вашей модели развёртывания.
- Оставьте аутентификацию шлюза включённой и используйте надлежащую точку входа с завершением TLS.
- Настройте интерфейс управления (Control UI) для удалённого доступа с использованием поддерживаемой модели веб-безопасности (например, HTTPS/Tailscale Serve и явное указание разрешённых источников при необходимости).

## Повторное развёртывание

```bash
./scripts/k8s/deploy.sh
```

Это применяет все манифесты и перезапускает под, чтобы учесть любые изменения конфигурации или секрета.

## Удаление

```bash
./scripts/k8s/deploy.sh --delete
```

Это удаляет пространство имён и все ресурсы в нём, включая PVC.

## Примечания по архитектуре

- По умолчанию шлюз привязывается к loopback внутри пода, поэтому включённая настройка предназначена для `kubectl port-forward`.
- Нет ресурсов, охватывающих весь кластер — всё находится в одном пространстве имён.
- Безопасность: `readOnlyRootFilesystem`, `drop: ALL` возможности, пользователь без прав root (UID 1000).
- В конфигурации по умолчанию интерфейс управления (Control UI) находится на более безопасном пути локального доступа: привязка к loopback плюс `kubectl port-forward` к `http://127.0.0.1:18789`.
- Если вы выходите за рамки доступа через localhost, используйте поддерживаемую удалённую модель: HTTPS/Tailscale плюс соответствующая привязка шлюза и настройки источника для интерфейса управления (Control UI).
- Секреты генерируются во временном каталоге и применяются непосредственно к кластеру — никакие секретные данные не записываются в репозиторий.

## Структура файлов

```
scripts/k8s/
├── deploy.sh                   # Создаёт пространство имён + секрет, выполняет развёртывание через kustomize
├── create-kind.sh              # Локальный кластер Kind (автоматически определяет docker/podman)
└── manifests/
    ├── kustomization.yaml      # База Kustomize
    ├── configmap.yaml          # openclaw.json + AGENTS.md
    ├── deployment.yaml         # Спецификация пода с усилением безопасности
    ├── pvc.yaml                # Постоянное хранилище на 10 ГиБ
    └── service.yaml            # ClusterIP на 18789
```