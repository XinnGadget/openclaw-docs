---
read_when: You hit 'sandbox jail' or see a tool/elevated refusal and want the exact config key to change.
status: active
summary: 'Dlaczego narzędzie jest blokowane: środowisko wykonawcze sandbox, zasady allow/deny dla narzędzi i bramki elevated exec'
title: Sandbox vs zasady narzędzi vs Elevated
x-i18n:
    generated_at: "2026-04-06T03:07:42Z"
    model: gpt-5.4
    provider: openai
    source_hash: 331f5b2f0d5effa1320125d9f29948e16d0deaffa59eb1e4f25a63481cbe22d6
    source_path: gateway/sandbox-vs-tool-policy-vs-elevated.md
    workflow: 15
---

# Sandbox vs zasady narzędzi vs Elevated

OpenClaw ma trzy powiązane ze sobą (ale różne) mechanizmy kontroli:

1. **Sandbox** (`agents.defaults.sandbox.*` / `agents.list[].sandbox.*`) decyduje, **gdzie uruchamiane są narzędzia** (Docker czy host).
2. **Zasady narzędzi** (`tools.*`, `tools.sandbox.tools.*`, `agents.list[].tools.*`) decydują, **które narzędzia są dostępne/dozwolone**.
3. **Elevated** (`tools.elevated.*`, `agents.list[].tools.elevated.*`) to **wyłącznie dla `exec` mechanizm obejścia**, który pozwala uruchamiać poza sandboxem, gdy jesteś w sandboxie (`gateway` domyślnie lub `node`, gdy cel `exec` jest skonfigurowany jako `node`).

## Szybkie debugowanie

Użyj inspektora, aby zobaczyć, co OpenClaw _faktycznie_ robi:

```bash
openclaw sandbox explain
openclaw sandbox explain --session agent:main:main
openclaw sandbox explain --agent work
openclaw sandbox explain --json
```

Wyświetla on:

- efektywny tryb/zakres sandboxa/dostęp do workspace
- czy sesja jest obecnie objęta sandboxem (main vs non-main)
- efektywne allow/deny narzędzi w sandboxie (oraz czy pochodzi z ustawień agenta/globalnych/domyślnych)
- bramki elevated i ścieżki kluczy naprawczych

## Sandbox: gdzie uruchamiane są narzędzia

Sandboxing jest kontrolowany przez `agents.defaults.sandbox.mode`:

- `"off"`: wszystko działa na hoście.
- `"non-main"`: tylko sesje non-main są objęte sandboxem (częsta „niespodzianka” w grupach/kanałach).
- `"all"`: wszystko jest objęte sandboxem.

Pełną matrycę (zakres, montowania workspace, obrazy) znajdziesz w [Sandboxing](/pl/gateway/sandboxing).

### Montowania bind (szybka kontrola bezpieczeństwa)

- `docker.binds` _przebija_ system plików sandboxa: wszystko, co zamontujesz, jest widoczne wewnątrz kontenera z ustawionym trybem (`:ro` lub `:rw`).
- Domyślnie używany jest tryb odczyt-zapis, jeśli pominiesz tryb; dla źródeł/sekretów preferuj `:ro`.
- `scope: "shared"` ignoruje montowania per-agent (stosowane są tylko globalne montowania).
- OpenClaw sprawdza źródła bind dwa razy: najpierw na znormalizowanej ścieżce źródłowej, a potem ponownie po rozwiązaniu przez najgłębszego istniejącego przodka. Ucieczki przez symlink-parent nie omijają kontroli ścieżek blokowanych ani dozwolonych katalogów głównych.
- Nieistniejące ścieżki liści również są sprawdzane bezpiecznie. Jeśli `/workspace/alias-out/new-file` po rozwiązaniu przez nadrzędny symlink prowadzi do zablokowanej ścieżki lub poza skonfigurowane dozwolone katalogi główne, bind zostanie odrzucony.
- Zamontowanie `/var/run/docker.sock` w praktyce przekazuje sandboxowi kontrolę nad hostem; rób to tylko świadomie.
- Dostęp do workspace (`workspaceAccess: "ro"`/`"rw"`) jest niezależny od trybów bind.

## Zasady narzędzi: które narzędzia istnieją i mogą być wywoływane

Znaczenie mają dwie warstwy:

- **Profil narzędzi**: `tools.profile` i `agents.list[].tools.profile` (bazowa allowlista)
- **Profil narzędzi dostawcy**: `tools.byProvider[provider].profile` i `agents.list[].tools.byProvider[provider].profile`
- **Globalne/per-agent zasady narzędzi**: `tools.allow`/`tools.deny` oraz `agents.list[].tools.allow`/`agents.list[].tools.deny`
- **Zasady narzędzi dostawcy**: `tools.byProvider[provider].allow/deny` oraz `agents.list[].tools.byProvider[provider].allow/deny`
- **Zasady narzędzi sandboxa** (obowiązują tylko w sandboxie): `tools.sandbox.tools.allow`/`tools.sandbox.tools.deny` oraz `agents.list[].tools.sandbox.tools.*`

Praktyczne zasady:

- `deny` zawsze wygrywa.
- Jeśli `allow` nie jest puste, wszystko inne jest traktowane jako zablokowane.
- Zasady narzędzi to twarda blokada: `/exec` nie może nadpisać zablokowanego narzędzia `exec`.
- `/exec` zmienia tylko domyślne ustawienia sesji dla autoryzowanych nadawców; nie przyznaje dostępu do narzędzi.
  Klucze narzędzi dostawcy akceptują zarówno `provider` (np. `google-antigravity`), jak i `provider/model` (np. `openai/gpt-5.4`).

### Grupy narzędzi (skróty)

Zasady narzędzi (globalne, per-agent, sandbox) obsługują wpisy `group:*`, które rozwijają się do wielu narzędzi:

```json5
{
  tools: {
    sandbox: {
      tools: {
        allow: ["group:runtime", "group:fs", "group:sessions", "group:memory"],
      },
    },
  },
}
```

Dostępne grupy:

- `group:runtime`: `exec`, `process`, `code_execution` (`bash` jest akceptowane
  jako alias dla `exec`)
- `group:fs`: `read`, `write`, `edit`, `apply_patch`
- `group:sessions`: `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `sessions_yield`, `subagents`, `session_status`
- `group:memory`: `memory_search`, `memory_get`
- `group:web`: `web_search`, `x_search`, `web_fetch`
- `group:ui`: `browser`, `canvas`
- `group:automation`: `cron`, `gateway`
- `group:messaging`: `message`
- `group:nodes`: `nodes`
- `group:agents`: `agents_list`
- `group:media`: `image`, `image_generate`, `video_generate`, `tts`
- `group:openclaw`: wszystkie wbudowane narzędzia OpenClaw (z wyłączeniem pluginów dostawców)

## Elevated: tylko dla `exec` „uruchom na hoście”

Elevated **nie** przyznaje dodatkowych narzędzi; wpływa tylko na `exec`.

- Jeśli jesteś w sandboxie, `/elevated on` (lub `exec` z `elevated: true`) uruchamia poza sandboxem (nadal mogą obowiązywać zatwierdzenia).
- Użyj `/elevated full`, aby pominąć zatwierdzenia `exec` dla sesji.
- Jeśli już działasz bezpośrednio, elevated jest w praktyce no-op (nadal objęty bramkami).
- Elevated **nie** jest ograniczone do Skills i **nie** nadpisuje zasad allow/deny narzędzi.
- Elevated nie przyznaje dowolnych nadpisań między hostami z `host=auto`; podąża za zwykłymi zasadami celu `exec` i zachowuje `node` tylko wtedy, gdy skonfigurowany/czasowy cel sesji to już `node`.
- `/exec` jest odrębne od elevated. Zmienia tylko domyślne ustawienia `exec` dla sesji dla autoryzowanych nadawców.

Bramki:

- Włączenie: `tools.elevated.enabled` (oraz opcjonalnie `agents.list[].tools.elevated.enabled`)
- Allowlisty nadawców: `tools.elevated.allowFrom.<provider>` (oraz opcjonalnie `agents.list[].tools.elevated.allowFrom.<provider>`)

Zobacz [Tryb Elevated](/pl/tools/elevated).

## Typowe poprawki „więzienia sandboxa”

### „Narzędzie X zablokowane przez zasady narzędzi sandboxa”

Klucze naprawcze (wybierz jeden):

- Wyłącz sandbox: `agents.defaults.sandbox.mode=off` (lub per-agent `agents.list[].sandbox.mode=off`)
- Zezwól na narzędzie w sandboxie:
  - usuń je z `tools.sandbox.tools.deny` (lub per-agent `agents.list[].tools.sandbox.tools.deny`)
  - albo dodaj je do `tools.sandbox.tools.allow` (lub per-agent allow)

### „Myślałem, że to main, dlaczego jest w sandboxie?”

W trybie `"non-main"` klucze grup/kanałów _nie_ są main. Użyj klucza sesji main (pokazanego przez `sandbox explain`) albo przełącz tryb na `"off"`.

## Zobacz też

- [Sandboxing](/pl/gateway/sandboxing) -- pełna dokumentacja sandboxa (tryby, zakresy, backendy, obrazy)
- [Sandbox i narzędzia w środowisku Multi-Agent](/pl/tools/multi-agent-sandbox-tools) -- nadpisania per-agent i pierwszeństwo
- [Tryb Elevated](/pl/tools/elevated)
