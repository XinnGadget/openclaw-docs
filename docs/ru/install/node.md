---
title: "Node.js"
summary: "Установка и настройка Node.js для OpenClaw — требования к версии, варианты установки и устранение неполадок с PATH"
read_when:
  - "Вам нужно установить Node.js перед установкой OpenClaw"
  - "Вы установили OpenClaw, но команда `openclaw` не найдена"
  - "Команда `npm install -g` завершается с ошибками прав доступа или проблемами с PATH"
---

# Node.js

Для работы OpenClaw требуется **Node 22.14 или новее**. **Node 24 — среда выполнения по умолчанию, её рекомендуется использовать** при установке, в CI и в рабочих процессах выпуска. Node 22 по-прежнему поддерживается в рамках активной линии LTS. [Скрипт установки](/install#alternative-install-methods) обнаружит и установит Node автоматически — эта страница предназначена для тех, кто хочет настроить Node самостоятельно и убедиться, что всё настроено корректно (версии, PATH, глобальные установки).

## Проверьте свою версию

```bash
node -v
```

Если выводится `v24.x.x` или выше, вы используете рекомендуемую версию по умолчанию. Если выводится `v22.14.x` или выше, вы используете поддерживаемую версию Node 22 LTS, но мы всё равно рекомендуем при возможности обновиться до Node 24. Если Node не установлен или версия слишком старая, выберите один из способов установки ниже.

## Установка Node

<Tabs>
  <Tab title="macOS">
    **Homebrew** (рекомендуется):

    ```bash
    brew install node
    ```

    Или скачайте установщик для macOS с [nodejs.org](https://nodejs.org/).

  </Tab>
  <Tab title="Linux">
    **Ubuntu / Debian:**

    ```bash
    curl -fsSL https://deb.nodesource.com/setup_24.x | sudo -E bash -
    sudo apt-get install -y nodejs
    ```

    **Fedora / RHEL:**

    ```bash
    sudo dnf install nodejs
    ```

    Или используйте менеджер версий (см. ниже).

  </Tab>
  <Tab title="Windows">
    **winget** (рекомендуется):

    ```powershell
    winget install OpenJS.NodeJS.LTS
    ```

    **Chocolatey:**

    ```powershell
    choco install nodejs-lts
    ```

    Или скачайте установщик для Windows с [nodejs.org](https://nodejs.org/).

  </Tab>
</Tabs>

<Accordion title="Использование менеджера версий (nvm, fnm, mise, asdf)">
Менеджеры версий позволяют легко переключаться между версиями Node. Популярные варианты:

- [**fnm**](https://github.com/Schniz/fnm) — быстрый, кроссплатформенный;
- [**nvm**](https://github.com/nvm-sh/nvm) — широко используется на macOS/Linux;
- [**mise**](https://mise.jdx.dev/) — полиглотный (Node, Python, Ruby и т. д.).

Пример с fnm:

```bash
fnm install 24
fnm use 24
```

  <Warning>
  Убедитесь, что ваш менеджер версий инициализирован в файле запуска оболочки (`~/.zshrc` или `~/.bashrc`). Если это не так, команда `openclaw` может не находиться в новых сеансах терминала, поскольку PATH не будет включать каталог bin Node.
  </Warning>
</Accordion>

## Устранение неполадок

### `openclaw: command not found`

Это почти всегда означает, что глобальный каталог bin npm не включён в PATH.

<Steps>
  <Step title="Найдите глобальный префикс npm">
    ```bash
    npm prefix -g
    ```
  </Step>
  <Step title="Проверьте, включён ли он в PATH">
    ```bash
    echo "$PATH"
    ```

    Найдите в выводе `<npm-prefix>/bin` (macOS/Linux) или `<npm-prefix>` (Windows).

  </Step>
  <Step title="Добавьте его в файл запуска оболочки">
    <Tabs>
      <Tab title="macOS / Linux">
        Добавьте в `~/.zshrc` или `~/.bashrc`:

        ```bash
        export PATH="$(npm prefix -g)/bin:$PATH"
        ```

        Затем откройте новый терминал (или выполните `rehash` в zsh / `hash -r` в bash).
      </Tab>
      <Tab title="Windows">
        Добавьте вывод команды `npm prefix -g` в системный PATH через "Параметры" → "Система" → "Переменные среды".
      </Tab>
    </Tabs>

  </Step>
</Steps>

### Ошибки прав доступа при выполнении `npm install -g` (Linux)

Если вы видите ошибки `EACCES`, измените глобальный префикс npm на каталог, доступный для записи пользователю:

```bash
mkdir -p "$HOME/.npm-global"
npm config set prefix "$HOME/.npm-global"
export PATH="$HOME/.npm-global/bin:$PATH"
```

Добавьте строку `export PATH=...` в `~/.bashrc` или `~/.zshrc`, чтобы сохранить изменения.

## Связанные материалы

- [Обзор установки](/install) — все способы установки;
- [Обновление](/install/updating) — поддержание OpenClaw в актуальном состоянии;
- [Начало работы](/start/getting-started) — первые шаги после установки.