---
read_when:
    - Aktualizujesz OpenClaw
    - Coś przestało działać po aktualizacji
summary: Bezpieczne aktualizowanie OpenClaw (instalacja globalna lub ze źródeł) oraz strategia wycofania zmian
title: Aktualizowanie
x-i18n:
    generated_at: "2026-04-06T03:08:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: ca9fff0776b9f5977988b649e58a5d169e5fa3539261cb02779d724d4ca92877
    source_path: install/updating.md
    workflow: 15
---

# Aktualizowanie

Utrzymuj OpenClaw na bieżąco.

## Zalecane: `openclaw update`

Najszybszy sposób aktualizacji. Wykrywa typ instalacji (npm lub git), pobiera najnowszą wersję, uruchamia `openclaw doctor` i restartuje gateway.

```bash
openclaw update
```

Aby przełączyć kanał lub wskazać konkretną wersję:

```bash
openclaw update --channel beta
openclaw update --tag main
openclaw update --dry-run   # podgląd bez zastosowania
```

`--channel beta` preferuje kanał beta, ale runtime przechodzi awaryjnie do stable/latest, gdy
tag beta nie istnieje albo jest starszy niż najnowsze stabilne wydanie. Użyj `--tag beta`,
jeśli chcesz użyć surowego npm dist-tag beta do jednorazowej aktualizacji pakietu.

Informacje o semantyce kanałów znajdziesz w [Kanały deweloperskie](/pl/install/development-channels).

## Alternatywa: uruchom instalator ponownie

```bash
curl -fsSL https://openclaw.ai/install.sh | bash
```

Dodaj `--no-onboard`, aby pominąć wdrożenie. W przypadku instalacji ze źródeł podaj `--install-method git --no-onboard`.

## Alternatywa: ręcznie przez npm, pnpm lub bun

```bash
npm i -g openclaw@latest
```

```bash
pnpm add -g openclaw@latest
```

```bash
bun add -g openclaw@latest
```

## Auto-updater

Auto-updater jest domyślnie wyłączony. Włącz go w `~/.openclaw/openclaw.json`:

```json5
{
  update: {
    channel: "stable",
    auto: {
      enabled: true,
      stableDelayHours: 6,
      stableJitterHours: 12,
      betaCheckIntervalHours: 1,
    },
  },
}
```

| Channel  | Zachowanie                                                                                                    |
| -------- | ------------------------------------------------------------------------------------------------------------- |
| `stable` | Czeka `stableDelayHours`, a następnie stosuje aktualizację z deterministycznym jitterem rozłożonym na `stableJitterHours` (stopniowe wdrażanie). |
| `beta`   | Sprawdza co `betaCheckIntervalHours` (domyślnie: co godzinę) i stosuje aktualizację natychmiast.            |
| `dev`    | Brak automatycznego stosowania. Użyj `openclaw update` ręcznie.                                               |

Gateway zapisuje też przy uruchomieniu wskazówkę o aktualizacji w logach (wyłącz przez `update.checkOnStart: false`).

## Po aktualizacji

<Steps>

### Uruchom doctor

```bash
openclaw doctor
```

Migruje konfigurację, audytuje zasady DM i sprawdza kondycję gateway. Szczegóły: [Doctor](/pl/gateway/doctor)

### Zrestartuj gateway

```bash
openclaw gateway restart
```

### Zweryfikuj

```bash
openclaw health
```

</Steps>

## Wycofanie zmian

### Przypnij wersję (npm)

```bash
npm i -g openclaw@<version>
openclaw doctor
openclaw gateway restart
```

Wskazówka: `npm view openclaw version` pokazuje aktualnie opublikowaną wersję.

### Przypnij commit (źródła)

```bash
git fetch origin
git checkout "$(git rev-list -n 1 --before=\"2026-01-01\" origin/main)"
pnpm install && pnpm build
openclaw gateway restart
```

Aby wrócić do najnowszej wersji: `git checkout main && git pull`.

## Jeśli utkniesz

- Uruchom ponownie `openclaw doctor` i uważnie przeczytaj dane wyjściowe.
- W przypadku `openclaw update --channel dev` w checkoutach ze źródeł updater automatycznie bootstrapuje `pnpm`, gdy jest to potrzebne. Jeśli zobaczysz błąd bootstrapu pnpm/corepack, zainstaluj `pnpm` ręcznie (albo ponownie włącz `corepack`) i uruchom aktualizację jeszcze raz.
- Sprawdź: [Rozwiązywanie problemów](/pl/gateway/troubleshooting)
- Zapytaj na Discordzie: [https://discord.gg/clawd](https://discord.gg/clawd)

## Powiązane

- [Przegląd instalacji](/pl/install) — wszystkie metody instalacji
- [Doctor](/pl/gateway/doctor) — kontrole kondycji po aktualizacjach
- [Migracja](/pl/install/migrating) — przewodniki migracji między głównymi wersjami
