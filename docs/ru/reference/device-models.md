---
summary: "Как OpenClaw предоставляет сопоставление идентификаторов моделей устройств Apple с понятными именами в приложении для macOS".
read_when:
  - Обновление сопоставления идентификаторов моделей устройств или файлов NOTICE/license
  - Изменение способа отображения имён устройств в интерфейсе Instances
title: "База данных моделей устройств"
---

# База данных моделей устройств (понятные имена)

Приложение-компаньон для macOS отображает понятные имена моделей устройств Apple в интерфейсе **Instances**, сопоставляя идентификаторы моделей Apple (например, `iPad16,6`, `Mac16,6`) с читаемыми именами.

Сопоставление предоставляется в формате JSON по следующему пути:

- `apps/macos/Sources/OpenClaw/Resources/DeviceModels/`

## Источник данных

В настоящее время сопоставление берётся из репозитория с лицензией MIT:

- `kyle-seongwoo-jun/apple-device-identifiers`

Чтобы сборка оставалась детерминированной, файлы JSON привязаны к конкретным коммитам исходного репозитория (они указаны в `apps/macos/Sources/OpenClaw/Resources/DeviceModels/NOTICE.md`).

## Обновление базы данных

1. Выберите коммиты исходного репозитория, к которым хотите привязаться (один для iOS, один для macOS).
2. Обновите хэши коммитов в файле `apps/macos/Sources/OpenClaw/Resources/DeviceModels/NOTICE.md`.
3. Повторно загрузите файлы JSON, привязанные к этим коммитам:

```bash
IOS_COMMIT="<хеш коммита для ios-device-identifiers.json>"
MAC_COMMIT="<хеш коммита для mac-device-identifiers.json>"

curl -fsSL "https://raw.githubusercontent.com/kyle-seongwoo-jun/apple-device-identifiers/${IOS_COMMIT}/ios-device-identifiers.json" \
  -o apps/macos/Sources/OpenClaw/Resources/DeviceModels/ios-device-identifiers.json

curl -fsSL "https://raw.githubusercontent.com/kyle-seongwoo-jun/apple-device-identifiers/${MAC_COMMIT}/mac-device-identifiers.json" \
  -o apps/macos/Sources/OpenClaw/Resources/DeviceModels/mac-device-identifiers.json
```

4. Убедитесь, что файл `apps/macos/Sources/OpenClaw/Resources/DeviceModels/LICENSE.apple-device-identifiers.txt` по-прежнему соответствует исходному репозиторию (замените его, если лицензия в исходном репозитории изменилась).
5. Проверьте, что сборка приложения для macOS проходит без ошибок (без предупреждений):

```bash
swift build --package-path apps/macos
```