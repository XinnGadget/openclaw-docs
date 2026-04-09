---
summary: "Платформы обмена сообщениями, к которым может подключаться OpenClaw"
read_when:
  - Вы хотите выбрать чат-канал для OpenClaw
  - Вам нужен краткий обзор поддерживаемых платформ обмена сообщениями
title: "Чат-каналы"
---

# Чат-каналы

OpenClaw может общаться с вами в любом мессенджере, который вы уже используете. Каждый канал подключается через Gateway.
Текст поддерживается везде; поддержка медиафайлов и реакций зависит от канала.

## Поддерживаемые каналы

- [BlueBubbles](/channels/bluebubbles) — **Рекомендуется для iMessage**; использует REST API сервера BlueBubbles для macOS с полной поддержкой функций (встроенный плагин; редактирование, отмена отправки, эффекты, реакции, управление группами — редактирование в настоящее время не работает в macOS 26 Tahoe).
- [Discord](/channels/discord) — Discord Bot API + Gateway; поддерживает серверы, каналы и личные сообщения (DM).
- [Feishu](/channels/feishu) — бот Feishu/Lark через WebSocket (встроенный плагин).
- [Google Chat](/channels/googlechat) — приложение Google Chat API через HTTP-вебхук.
- [iMessage (устаревший)](/channels/imessage) — устаревшая интеграция с macOS через imsg CLI (не рекомендуется, для новых установок используйте BlueBubbles).
- [IRC](/channels/irc) — классические IRC-серверы; каналы и личные сообщения с управлением через списки парных подключений/разрешённых адресов.
- [LINE](/channels/line) — бот LINE Messaging API (встроенный плагин).
- [Matrix](/channels/matrix) — протокол Matrix (встроенный плагин).
- [Mattermost](/channels/mattermost) — Bot API + WebSocket; каналы, группы, личные сообщения (встроенный плагин).
- [Microsoft Teams](/channels/msteams) — Bot Framework; поддержка корпоративных решений (встроенный плагин).
- [Nextcloud Talk](/channels/nextcloud-talk) — саморазмещённый чат через Nextcloud Talk (встроенный плагин).
- [Nostr](/channels/nostr) — децентрализованные личные сообщения через NIP-04 (встроенный плагин).
- [QQ Bot](/channels/qqbot) — QQ Bot API; личные чаты, групповые чаты и мультимедийный контент (встроенный плагин).
- [Signal](/channels/signal) — signal-cli; ориентирован на конфиденциальность.
- [Slack](/channels/slack) — Bolt SDK; приложения для рабочих пространств.
- [Synology Chat](/channels/synology-chat) — чат Synology NAS через исходящие и входящие вебхуки (встроенный плагин).
- [Telegram](/channels/telegram) — Bot API через grammY; поддерживает группы.
- [Tlon](/channels/tlon) — мессенджер на базе Urbit (встроенный плагин).
- [Twitch](/channels/twitch) — чат Twitch через подключение по IRC (встроенный плагин).
- [Voice Call](/plugins/voice-call) — телефония через Plivo или Twilio (плагин, устанавливается отдельно).
- [WebChat](/web/webchat) — интерфейс WebChat Gateway через WebSocket.
- [WeChat](https://www.npmjs.com/package/@tencent-weixin/openclaw-weixin) — плагин Tencent iLink Bot через вход по QR-коду; только личные чаты.
- [WhatsApp](/channels/whatsapp) — самый популярный; использует Baileys и требует сопряжения по QR-коду.
- [Zalo](/channels/zalo) — Zalo Bot API; популярный мессенджер во Вьетнаме (встроенный плагин).
- [Zalo Personal](/channels/zalouser) — личная учётная запись Zalo через вход по QR-коду (встроенный плагин).

## Примечания

- Каналы могут работать одновременно; настройте несколько каналов, и OpenClaw будет маршрутизировать сообщения в зависимости от чата.
- Наиболее быстрая настройка обычно доступна для **Telegram** (простой токен бота). Для WhatsApp требуется сопряжение по QR-коду, и он сохраняет больше данных на диске.
- Поведение в группах зависит от канала; см. [Группы](/channels/groups).
- Для обеспечения безопасности применяются правила сопряжения личных сообщений и списки разрешённых адресов; см. [Безопасность](/gateway/security).
- Устранение неполадок: [Устранение неполадок с каналами](/channels/troubleshooting).
- Поставщики моделей описаны отдельно; см. [Поставщики моделей](/providers/models).