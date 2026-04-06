---
read_when:
    - Chcesz zrozumieć OAuth w OpenClaw od początku do końca
    - Napotkałeś problemy z unieważnianiem tokenów / wylogowywaniem
    - Chcesz używać przepływów uwierzytelniania Claude CLI lub OAuth
    - Chcesz używać wielu kont lub routingu profili
summary: 'OAuth w OpenClaw: wymiana tokenów, przechowywanie i wzorce dla wielu kont'
title: OAuth
x-i18n:
    generated_at: "2026-04-06T03:07:12Z"
    model: gpt-5.4
    provider: openai
    source_hash: 402e20dfeb6ae87a90cba5824a56a7ba3b964f3716508ea5cc48a47e5affdd73
    source_path: concepts/oauth.md
    workflow: 15
---

# OAuth

OpenClaw obsługuje „subscription auth” przez OAuth dla dostawców, którzy to oferują
(w szczególności **OpenAI Codex (ChatGPT OAuth)**). W przypadku Anthropic praktyczny podział
wygląda teraz następująco:

- **Klucz API Anthropic**: standardowe rozliczanie API Anthropic
- **Anthropic subscription auth w OpenClaw**: Anthropic powiadomił użytkowników OpenClaw
  **4 kwietnia 2026 o 12:00 PT / 20:00 BST**, że teraz
  wymaga to **Extra Usage**

OpenAI Codex OAuth jest oficjalnie obsługiwany do użycia w zewnętrznych narzędziach, takich jak
OpenClaw. Ta strona wyjaśnia:

W przypadku Anthropic w środowisku produkcyjnym bezpieczniejszą zalecaną ścieżką jest uwierzytelnianie kluczem API.

- jak działa **wymiana tokenów** OAuth (PKCE)
- gdzie tokeny są **przechowywane** (i dlaczego)
- jak obsługiwać **wiele kont** (profile + nadpisania dla poszczególnych sesji)

OpenClaw obsługuje też **pluginy dostawców**, które dostarczają własne przepływy OAuth lub API-key.
Uruchamiaj je za pomocą:

```bash
openclaw models auth login --provider <id>
```

## Ujście tokenów (dlaczego istnieje)

Dostawcy OAuth często tworzą **nowy token odświeżania** podczas logowania lub odświeżania. Niektórzy dostawcy (lub klienci OAuth) mogą unieważniać starsze tokeny odświeżania, gdy dla tego samego użytkownika/aplikacji zostanie wydany nowy.

Praktyczny objaw:

- logujesz się przez OpenClaw _i_ przez Claude Code / Codex CLI → jedno z nich później losowo zostaje „wylogowane”

Aby to ograniczyć, OpenClaw traktuje `auth-profiles.json` jako **ujście tokenów**:

- środowisko uruchomieniowe odczytuje poświadczenia z **jednego miejsca**
- możemy utrzymywać wiele profili i kierować je w sposób deterministyczny
- gdy poświadczenia są ponownie używane z zewnętrznego CLI, takiego jak Codex CLI, OpenClaw
  odzwierciedla je wraz z informacją o pochodzeniu i ponownie odczytuje to zewnętrzne źródło zamiast
  samodzielnie rotować token odświeżania

## Przechowywanie (gdzie znajdują się tokeny)

Sekrety są przechowywane **na agenta**:

- Profile auth (OAuth + klucze API + opcjonalne odwołania na poziomie wartości): `~/.openclaw/agents/<agentId>/agent/auth-profiles.json`
- Plik zgodności wstecznej: `~/.openclaw/agents/<agentId>/agent/auth.json`
  (statyczne wpisy `api_key` są usuwane po wykryciu)

Starszy plik tylko do importu (nadal obsługiwany, ale nie jest głównym magazynem):

- `~/.openclaw/credentials/oauth.json` (importowany do `auth-profiles.json` przy pierwszym użyciu)

Wszystkie powyższe lokalizacje respektują też `$OPENCLAW_STATE_DIR` (nadpisanie katalogu stanu). Pełne informacje: [/gateway/configuration](/pl/gateway/configuration-reference#auth-storage)

Informacje o statycznych odwołaniach do sekretów i zachowaniu aktywacji migawek runtime znajdziesz w [Zarządzaniu sekretami](/pl/gateway/secrets).

## Zgodność ze starszymi tokenami Anthropic

<Warning>
Publiczna dokumentacja Claude Code od Anthropic mówi, że bezpośrednie użycie Claude Code pozostaje w ramach
limitów subskrypcji Claude. Osobno Anthropic poinformował użytkowników OpenClaw
**4 kwietnia 2026 o 12:00 PT / 20:00 BST**, że **OpenClaw jest traktowany jako
zewnętrzny harness**. Istniejące profile tokenów Anthropic nadal technicznie
mogą być używane w OpenClaw, ale Anthropic twierdzi, że ścieżka OpenClaw wymaga teraz **Extra
Usage** (pay-as-you-go, rozliczane oddzielnie od subskrypcji) dla tego ruchu.

Aktualną dokumentację planów Anthropic dla bezpośredniego Claude Code znajdziesz w [Using Claude Code
with your Pro or Max
plan](https://support.claude.com/en/articles/11145838-using-claude-code-with-your-pro-or-max-plan)
oraz [Using Claude Code with your Team or Enterprise
plan](https://support.anthropic.com/en/articles/11845131-using-claude-code-with-your-team-or-enterprise-plan/).

Jeśli chcesz używać innych opcji w stylu subskrypcyjnym w OpenClaw, zobacz [OpenAI
Codex](/pl/providers/openai), [Qwen Cloud Coding
Plan](/pl/providers/qwen), [MiniMax Coding Plan](/pl/providers/minimax)
oraz [Z.AI / GLM Coding Plan](/pl/providers/glm).
</Warning>

OpenClaw ponownie udostępnia Anthropic setup-token jako starszą/ręczną ścieżkę.
Powiadomienie Anthropic o rozliczaniu specyficznym dla OpenClaw nadal dotyczy tej ścieżki, więc
używaj jej z założeniem, że Anthropic wymaga **Extra Usage** dla
ruchu logowania do Claude inicjowanego przez OpenClaw.

## Migracja Anthropic Claude CLI

Anthropic nie ma już obsługiwanej lokalnej ścieżki migracji Claude CLI w
OpenClaw. Używaj kluczy API Anthropic do ruchu Anthropic albo zachowaj starsze
uwierzytelnianie oparte na tokenach tylko tam, gdzie jest już skonfigurowane, i z założeniem,
że Anthropic traktuje tę ścieżkę OpenClaw jako **Extra Usage**.

## Wymiana OAuth (jak działa logowanie)

Interaktywne przepływy logowania OpenClaw są zaimplementowane w `@mariozechner/pi-ai` i podłączone do kreatorów/poleceń.

### Anthropic setup-token

Kształt przepływu:

1. uruchom Anthropic setup-token lub wklej token z OpenClaw
2. OpenClaw zapisuje uzyskane poświadczenie Anthropic w profilu auth
3. wybór modelu pozostaje ustawiony na `anthropic/...`
4. istniejące profile auth Anthropic pozostają dostępne na potrzeby wycofania zmian/kontroli kolejności

### OpenAI Codex (ChatGPT OAuth)

OpenAI Codex OAuth jest oficjalnie obsługiwany do użycia poza Codex CLI, w tym w przepływach pracy OpenClaw.

Kształt przepływu (PKCE):

1. wygeneruj verifier/challenge PKCE oraz losowy `state`
2. otwórz `https://auth.openai.com/oauth/authorize?...`
3. spróbuj przechwycić callback na `http://127.0.0.1:1455/auth/callback`
4. jeśli nie można zbindować callbacku (lub działasz zdalnie/bez interfejsu), wklej URL przekierowania/kod
5. wykonaj wymianę pod adresem `https://auth.openai.com/oauth/token`
6. wyodrębnij `accountId` z tokenu dostępu i zapisz `{ access, refresh, expires, accountId }`

Ścieżka kreatora to `openclaw onboard` → wybór auth `openai-codex`.

## Odświeżanie i wygaśnięcie

Profile przechowują znacznik czasu `expires`.

W środowisku uruchomieniowym:

- jeśli `expires` wskazuje przyszłość → używany jest zapisany token dostępu
- jeśli wygasł → następuje odświeżenie (pod blokadą pliku) i nadpisanie zapisanych poświadczeń
- wyjątek: ponownie używane poświadczenia z zewnętrznego CLI pozostają zarządzane zewnętrznie; OpenClaw
  ponownie odczytuje magazyn auth CLI i nigdy sam nie wykorzystuje skopiowanego tokenu odświeżania

Przepływ odświeżania jest automatyczny; zwykle nie trzeba ręcznie zarządzać tokenami.

## Wiele kont (profile) i routing

Dwa wzorce:

### 1) Preferowane: osobni agenci

Jeśli chcesz, aby „osobiste” i „służbowe” nigdy się nie stykały, użyj izolowanych agentów (osobne sesje + poświadczenia + przestrzeń robocza):

```bash
openclaw agents add work
openclaw agents add personal
```

Następnie skonfiguruj auth dla każdego agenta osobno (kreator) i kieruj czaty do właściwego agenta.

### 2) Zaawansowane: wiele profili w jednym agencie

`auth-profiles.json` obsługuje wiele identyfikatorów profili dla tego samego dostawcy.

Wybór używanego profilu:

- globalnie przez kolejność w konfiguracji (`auth.order`)
- dla sesji przez `/model ...@<profileId>`

Przykład (nadpisanie dla sesji):

- `/model Opus@anthropic:work`

Jak sprawdzić, jakie identyfikatory profili istnieją:

- `openclaw channels list --json` (pokazuje `auth[]`)

Powiązana dokumentacja:

- [/concepts/model-failover](/pl/concepts/model-failover) (zasady rotacji i cooldown)
- [/tools/slash-commands](/pl/tools/slash-commands) (powierzchnia poleceń)

## Powiązane

- [Uwierzytelnianie](/pl/gateway/authentication) — przegląd uwierzytelniania dostawców modeli
- [Sekrety](/pl/gateway/secrets) — przechowywanie poświadczeń i SecretRef
- [Dokumentacja konfiguracji](/pl/gateway/configuration-reference#auth-storage) — klucze konfiguracji auth
