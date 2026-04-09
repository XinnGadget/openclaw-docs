---
summary: "Поддерживаемые и неподдерживаемые учётные данные SecretRef"
read_when:
  - Проверка покрытия учётных данных SecretRef
  - Аудит того, подходят ли учётные данные для `secrets configure` или `secrets apply`
  - Проверка причин, по которым учётные данные находятся за пределами поддерживаемой области
title: "Область учётных данных SecretRef"
---

# Область учётных данных SecretRef

На этой странице определена каноническая область учётных данных SecretRef.

Цель определения области:

- В области: строго пользовательские учётные данные, которые OpenClaw не создаёт и не ротирует.
- За пределами области: учётные данные, создаваемые во время выполнения, ротируемые учётные данные, материалы для обновления OAuth и артефакты, похожие на сеансы.

## Поддерживаемые учётные данные

### Цели для `openclaw.json` (`secrets configure` + `secrets apply` + `secrets audit`)

[//]: # "secretref-supported-list-start"

- `models.providers.*.apiKey`
- `models.providers.*.headers.*`
- `models.providers.*.request.auth.token`
- `models.providers.*.request.auth.value`
- `models.providers.*.request.headers.*`
- `models.providers.*.request.proxy.tls.ca`
- `models.providers.*.request.proxy.tls.cert`
- `models.providers.*.request.proxy.tls.key`
- `models.providers.*.request.proxy.tls.passphrase`
- `models.providers.*.request.tls.ca`
- `models.providers.*.request.tls.cert`
- `models.providers.*.request.tls.key`
- `models.providers.*.request.tls.passphrase`
- `skills.entries.*.apiKey`
- `agents.defaults.memorySearch.remote.apiKey`
- `agents.list[].memorySearch.remote.apiKey`
- `talk.providers.*.apiKey`
- `messages.tts.providers.*.apiKey`
- `tools.web.fetch.firecrawl.apiKey`
- `plugins.entries.brave.config.webSearch.apiKey`
- `plugins.entries.google.config.webSearch.apiKey`
- `plugins.entries.xai.config.webSearch.apiKey`
- `plugins.entries.moonshot.config.webSearch.apiKey`
- `plugins.entries.perplexity.config.webSearch.apiKey`
- `plugins.entries.firecrawl.config.webSearch.apiKey`
- `plugins.entries.minimax.config.webSearch.apiKey`
- `plugins.entries.tavily.config.webSearch.apiKey`
- `tools.web.search.apiKey`
- `gateway.auth.password`
- `gateway.auth.token`
- `gateway.remote.token`
- `gateway.remote.password`
- `cron.webhookToken`
- `channels.telegram.botToken`
- `channels.telegram.webhookSecret`
- `channels.telegram.accounts.*.botToken`
- `channels.telegram.accounts.*.webhookSecret`
- `channels.slack.botToken`
- `channels.slack.appToken`
- `channels.slack.userToken`
- `channels.slack.signingSecret`
- `channels.slack.accounts.*.botToken`
- `channels.slack.accounts.*.appToken`
- `channels.slack.accounts.*.userToken`
- `channels.slack.accounts.*.signingSecret`
- `channels.discord.token`
- `channels.discord.pluralkit.token`
- `channels.discord.voice.tts.providers.*.apiKey`
- `channels.discord.accounts.*.token`
- `channels.discord.accounts.*.pluralkit.token`
- `channels.discord.accounts.*.voice.tts.providers.*.apiKey`
- `channels.irc.password`
- `channels.irc.nickserv.password`
- `channels.irc.accounts.*.password`
- `channels.irc.accounts.*.nickserv.password`
- `channels.bluebubbles.password`
- `channels.bluebubbles.accounts.*.password`
- `channels.feishu.appSecret`
- `channels.feishu.encryptKey`
- `channels.feishu.verificationToken`
- `channels.feishu.accounts.*.appSecret`
- `channels.feishu.accounts.*.encryptKey`
- `channels.feishu.accounts.*.verificationToken`
- `channels.msteams.appPassword`
- `channels.mattermost.botToken`
- `channels.mattermost.accounts.*.botToken`
- `channels.matrix.accessToken`
- `channels.matrix.password`
- `channels.matrix.accounts.*.accessToken`
- `channels.matrix.accounts.*.password`
- `channels.nextcloud-talk.botSecret`
- `channels.nextcloud-talk.apiPassword`
- `channels.nextcloud-talk.accounts.*.botSecret`
- `channels.nextcloud-talk.accounts.*.apiPassword`
- `channels.zalo.botToken`
- `channels.zalo.webhookSecret`
- `channels.zalo.accounts.*.botToken`
- `channels.zalo.accounts.*.webhookSecret`
- `channels.googlechat.serviceAccount` через sibling `serviceAccountRef` (исключение для совместимости)
- `channels.googlechat.accounts.*.serviceAccount` через sibling `serviceAccountRef` (исключение для совместимости)

### Цели для `auth-profiles.json` (`secrets configure` + `secrets apply` + `secrets audit`)

- `profiles.*.keyRef` (`type: "api_key"`; не поддерживается, когда `auth.profiles.<id>.mode = "oauth"`)
- `profiles.*.tokenRef` (`type: "token"`; не поддерживается, когда `auth.profiles.<id>.mode = "oauth"`)

[//]: # "secretref-supported-list-end"

Примечания:

- Для целей плана auth-profile требуется `agentId`.
- Записи плана нацелены на `profiles.*.key` / `profiles.*.token` и записывают sibling refs (`keyRef` / `tokenRef`).
- Ссылки auth-profile включены в разрешение во время выполнения и в охват аудита.
- Защита политики OAuth: `auth.profiles.<id>.mode = "oauth"` нельзя сочетать с входными данными SecretRef для этого профиля. При нарушении этой политики запуск/перезагрузка и разрешение auth-profile немедленно завершаются ошибкой.
- Для поставщиков моделей, управляемых через SecretRef, сгенерированные записи `agents/*/agent/models.json` сохраняют маркеры без секретных данных (а не разрешённые значения секретов) для поверхностей `apiKey`/headers.
- Сохранение маркеров определяется источником: OpenClaw записывает маркеры из активного снимка конфигурации источника (до разрешения), а не из разрешённых значений секретов во время выполнения.
- Для веб-поиска:
  - В режиме явного указания провайдера (`tools.web.search.provider` задан) активен только ключ выбранного провайдера.
  - В автоматическом режиме (`tools.web.search.provider` не задан) активен только первый ключ провайдера, который разрешается согласно приоритету.
  - В автоматическом режиме ссылки на не выбранные провайдеры считаются неактивными до момента их выбора.
  - Устаревшие пути провайдеров `tools.web.search.*` по-прежнему разрешаются в период совместимости, но каноническая область SecretRef — `plugins.entries.<plugin>.config.webSearch.*`.

## Неподдерживаемые учётные данные

Учётные данные за пределами области включают:

[//]: # "secretref-unsupported-list-start"

- `commands.ownerDisplaySecret`
- `hooks.token`
- `hooks.gmail.pushToken`
- `hooks.mappings[].sessionKey`
- `auth-profiles.oauth.*`
- `channels.discord.threadBindings.webhookToken`
- `channels.discord.accounts.*.threadBindings.webhookToken`
- `channels.whatsapp.creds.json`
- `channels.whatsapp.accounts.*.creds.json`

[//]: # "secretref-unsupported-list-end"

Обоснование:

- Эти учётные данные создаются, ротируются, связаны с сеансами или относятся к классам с длительным сроком действия OAuth, которые не подходят для разрешения внешних SecretRef только для чтения.