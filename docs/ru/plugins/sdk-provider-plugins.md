---
title: "Создание плагинов провайдеров"
sidebarTitle: "Плагины провайдеров"
summary: "Пошаговое руководство по созданию плагина провайдера модели для OpenClaw"
read_when:
  - Вы создаёте новый плагин провайдера модели
  - Вы хотите добавить в OpenClaw прокси, совместимый с OpenAI, или собственную LLM
  - Вам нужно разобраться в аутентификации провайдера, каталогах и хуках времени выполнения
---

# Создание плагинов провайдеров

В этом руководстве описано, как создать плагин провайдера, который добавит провайдера модели (LLM) в OpenClaw. К концу работы у вас будет провайдер с каталогом моделей, аутентификацией по API-ключу и динамическим разрешением моделей.

<Info>
  Если вы ещё не создавали плагин для OpenClaw, сначала ознакомьтесь с разделом [Начало работы](/plugins/building-plugins), чтобы узнать об основной структуре пакета и настройке манифеста.
</Info>

## Пошаговое руководство

<Steps>
  <a id="step-1-package-and-manifest"></a>
  <Step title="Пакет и манифест">
    <CodeGroup>
    ```json package.json
    {
      "name": "@myorg/openclaw-acme-ai",
      "version": "1.0.0",
      "type": "module",
      "openclaw": {
        "extensions": ["./index.ts"],
        "providers": ["acme-ai"],
        "compat": {
          "pluginApi": ">=2026.3.24-beta.2",
          "minGatewayVersion": "2026.3.24-beta.2"
        },
        "build": {
          "openclawVersion": "2026.3.24-beta.2",
          "pluginSdkVersion": "2026.3.24-beta.2"
        }
      }
    }
    ```

    ```json openclaw.plugin.json
    {
      "id": "acme-ai",
      "name": "Acme AI",
      "description": "Провайдер моделей Acme AI",
      "providers": ["acme-ai"],
      "modelSupport": {
        "modelPrefixes": ["acme-"]
      },
      "providerAuthEnvVars": {
        "acme-ai": ["ACME_AI_API_KEY"]
      },
      "providerAuthAliases": {
        "acme-ai-coding": "acme-ai"
      },
      "providerAuthChoices": [
        {
          "provider": "acme-ai",
          "method": "api-key",
          "choiceId": "acme-ai-api-key",
          "choiceLabel": "API-ключ Acme AI",
          "groupId": "acme-ai",
          "groupLabel": "Acme AI",
          "cliFlag": "--acme-ai-api-key",
          "cliOption": "--acme-ai-api-key <key>",
          "cliDescription": "API-ключ Acme AI"
        }
      ],
      "configSchema": {
        "type": "object",
        "additionalProperties": false
      }
    }
    ```
    </CodeGroup>

    В манифесте указывается `providerAuthEnvVars`, чтобы OpenClaw мог обнаружить учётные данные без загрузки среды выполнения плагина. Добавьте `providerAuthAliases`, если вариант провайдера должен повторно использовать аутентификацию другого идентификатора провайдера. `modelSupport` — необязательный параметр, который позволяет OpenClaw автоматически загружать плагин провайдера по сокращённым идентификаторам моделей (например, `acme-large`) до появления хуков времени выполнения. Если вы публикуете провайдера в ClawHub, поля `openclaw.compat` и `openclaw.build` в `package.json` обязательны.

  </Step>

  <Step title="Регистрация провайдера">
    Для минимального провайдера требуются `id`, `label`, `auth` и `catalog`:

    ```typescript index.ts
    import { definePluginEntry } from "openclaw/plugin-sdk/plugin-entry";
    import { createProviderApiKeyAuthMethod } from "openclaw/plugin-sdk/provider-auth";

    export default definePluginEntry({
      id: "acme-ai",
      name: "Acme AI",
      description: "Провайдер моделей Acme AI",
      register(api) {
        api.registerProvider({
          id: "acme-ai",
          label: "Acme AI",
          docsPath: "/providers/acme-ai",
          envVars: ["ACME_AI_API_KEY"],

          auth: [
            createProviderApiKeyAuthMethod({
              providerId: "acme-ai",
              methodId: "api-key",
              label: "API-ключ Acme AI",
              hint: "API-ключ из панели управления Acme AI",
              optionKey: "acmeAiApiKey",
              flagName: "--acme-ai-api-key",
              envVar: "ACME_AI_API_KEY",
              promptMessage: "Введите API-ключ Acme AI",
              defaultModel: "acme-ai/acme-large",
            }),
          ],

          catalog: {
            order: "simple",
            run: async (ctx) => {
              const apiKey =
                ctx.resolveProviderApiKey("acme-ai").apiKey;
              if (!apiKey) return null;
              return {
                provider: {
                  baseUrl: "https://api.acme-ai.com/v1",
                  apiKey,
                  api: "openai-completions",
                  models: [
                    {
                      id: "acme-large",
                      name: "Acme Large",
                      reasoning: true,
                      input: ["text", "image"],
                      cost: { input: 3, output: 15, cacheRead: 0.3, cacheWrite: 3.75 },
                      contextWindow: 200000,
                      maxTokens: 32768,
                    },
                    {
                      id: "acme-small",
                      name: "Acme Small",
                      reasoning: false,
                      input: ["text"],
                      cost: { input: 1, output: 5, cacheRead: 0.1, cacheWrite: 1.25 },
                      contextWindow: 128000,
                      maxTokens: 8192,
                    },
                  ],
                },
              };
            },
          },
        });
      },
    });
    ```

    Это рабочий провайдер. Теперь пользователи могут выполнить команду `openclaw onboard --acme-ai-api-key <key>` и выбрать модель `acme-ai/acme-large`.

    Для встроенных провайдеров, которые регистрируют только один текстовый провайдер с аутентификацией по API-ключу и одним каталогом с поддержкой времени выполнения, предпочтительнее использовать более узкий помощник `defineSingleProviderPluginEntry(...)`:

    ```typescript
    import { defineSingleProviderPluginEntry } from "openclaw/plugin-sdk/provider-entry";

    export default defineSingleProviderPluginEntry({
      id: "acme-ai",
      name: "Acme AI",
      description: "Провайдер моделей Acme AI",
      provider: {
        label: "Acme AI",
        docsPath: "/providers/acme-ai",
        auth: [
          {
            methodId: "api-key",
            label: "API-ключ Acme AI",
            hint: "API-ключ из панели управления Acme AI",
            optionKey: "acmeAiApiKey",
            flagName: "--acme-ai-api-key",
            envVar: "ACME_AI_API_KEY",
            promptMessage: "Введите API-ключ Acme AI",
            defaultModel: "acme-ai/acme-large",
          },
        ],
        catalog: {
          buildProvider: () => ({
            api: "openai-completions",
            baseUrl: "https://api.acme-ai.com/v1",
            models: [{ id: "acme-large", name: "Acme Large" }],
          }),
        },
      },
    });
    ```

    Если ваш процесс аутентификации также должен изменять `models.providers.*`, псевдонимы и модель агента по умолчанию во время регистрации, используйте готовые помощники из `openclaw/plugin-sdk/provider-onboard`. Самые узкие помощники — `createDefaultModelPresetAppliers(...)`, `createDefaultModelsPresetAppliers(...)` и `createModelCatalogPresetAppliers(...)`.

    Если нативная конечная точка провайдера поддерживает