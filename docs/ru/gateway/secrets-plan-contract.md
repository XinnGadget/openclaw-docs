---
summary: "Контракт для планов `secrets apply`: проверка целевых объектов, сопоставление путей и область действия целевого объекта в `auth-profiles.json`"
read_when:
  - При генерации или проверке планов `openclaw secrets apply`
  - При отладке ошибок `Invalid plan target path`
  - При изучении поведения проверки типа и пути целевого объекта
title: "Контракт плана secrets apply"
---

# Контракт плана secrets apply

На этой странице определён строгий контракт, который соблюдается в `openclaw secrets apply`.

Если целевой объект не соответствует этим правилам, выполнение операции `apply` завершается ошибкой до внесения изменений в конфигурацию.

## Структура файла плана

Команда `openclaw secrets apply --from <plan.json>` ожидает массив `targets`, содержащий целевые объекты плана:

```json5
{
  version: 1,
  protocolVersion: 1,
  targets: [
    {
      type: "models.providers.apiKey",
      path: "models.providers.openai.apiKey",
      pathSegments: ["models", "providers", "openai", "apiKey"],
      providerId: "openai",
      ref: { source: "env", provider: "default", id: "OPENAI_API_KEY" },
    },
    {
      type: "auth-profiles.api_key.key",
      path: "profiles.openai:default.key",
      pathSegments: ["profiles", "openai:default", "key"],
      agentId: "main",
      ref: { source: "env", provider: "default", id: "OPENAI_API_KEY" },
    },
  ],
}
```

## Поддерживаемая область действия целевых объектов

Целевые объекты плана принимаются для поддерживаемых путей учётных данных в:

- [SecretRef Credential Surface](/reference/secretref-credential-surface)

## Поведение в зависимости от типа целевого объекта

Общее правило:

- `target.type` должен быть распознан и должен соответствовать нормализованной форме `target.path`.

Для существующих планов по-прежнему принимаются псевдонимы совместимости:

- `models.providers.apiKey`
- `skills.entries.apiKey`
- `channels.googlechat.serviceAccount`

## Правила проверки пути

Каждый целевой объект проверяется по всем следующим критериям:

- `type` должен быть распознанным типом целевого объекта.
- `path` должен быть непустым путём с разделителем в виде точки.
- `pathSegments` может быть опущен. Если указан, он должен нормализоваться до точно такого же пути, как `path`.
- Запрещённые сегменты отклоняются: `__proto__`, `prototype`, `constructor`.
- Нормализованный путь должен соответствовать зарегистрированной форме пути для типа целевого объекта.
- Если заданы `providerId` или `accountId`, они должны соответствовать идентификатору, закодированному в пути.
- Для целевых объектов `auth-profiles.json` требуется `agentId`.
- При создании нового сопоставления `auth-profiles.json` необходимо включить `authProfileProvider`.

## Поведение при ошибке

Если целевой объект не проходит проверку, выполнение `apply` завершается с ошибкой, например:

```text
Invalid plan target path for models.providers.apiKey: models.providers.openai.baseUrl
```

Для недопустимого плана никакие записи не фиксируются.

## Поведение согласия провайдера exec

- Параметр `--dry-run` по умолчанию пропускает проверку SecretRef для exec.
- Планы, содержащие exec SecretRefs/провайдеры, отклоняются в режиме записи, если не указан параметр `--allow-exec`.
- При проверке и применении планов, содержащих exec, необходимо указывать `--allow-exec` как в режиме пробного запуска, так и в режиме записи.

## Примечания о времени выполнения и области аудита

- Записи `auth-profiles.json`, содержащие только ссылки (`keyRef`/`tokenRef`), включаются в разрешение во время выполнения и в охват аудита.
- `secrets apply` записывает поддерживаемые целевые объекты `openclaw.json`, поддерживаемые целевые объекты `auth-profiles.json` и необязательные целевые объекты для очистки.

## Проверки оператора

```bash
# Проверить план без записи
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --dry-run

# Затем применить на самом деле
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json

# Для планов, содержащих exec, явно указать разрешение в обоих режимах
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --dry-run --allow-exec
openclaw secrets apply --from /tmp/openclaw-secrets-plan.json --allow-exec
```

Если выполнение `apply` завершается с сообщением о недопустимом пути целевого объекта, перегенерируйте план с помощью `openclaw secrets configure` или исправьте путь целевого объекта в соответствии с поддерживаемой формой, указанной выше.

## Связанные документы

- [Управление секретами](/gateway/secrets)
- [CLI `secrets`](/cli/secrets)
- [SecretRef Credential Surface](/reference/secretref-credential-surface)
- [Справочник по конфигурации](/gateway/configuration-reference)