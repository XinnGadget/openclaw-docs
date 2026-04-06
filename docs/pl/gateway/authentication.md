---
read_when:
    - Debugowanie uwierzytelniania modelu lub wygaśnięcia OAuth
    - Dokumentowanie uwierzytelniania lub przechowywania poświadczeń
summary: 'Uwierzytelnianie modeli: OAuth, klucze API i starszy setup-token Anthropic'
title: Uwierzytelnianie
x-i18n:
    generated_at: "2026-04-06T03:07:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: f59ede3fcd7e692ad4132287782a850526acf35474b5bfcea29e0e23610636c2
    source_path: gateway/authentication.md
    workflow: 15
---

# Uwierzytelnianie (Providerzy modeli)

<Note>
Ta strona dotyczy uwierzytelniania **providera modeli** (klucze API, OAuth i starszy setup-token Anthropic). W przypadku uwierzytelniania **połączenia z gatewayem** (token, hasło, trusted-proxy) zobacz [Configuration](/pl/gateway/configuration) i [Trusted Proxy Auth](/pl/gateway/trusted-proxy-auth).
</Note>

OpenClaw obsługuje OAuth i klucze API dla providerów modeli. W przypadku stale
działających hostów gatewaya klucze API są zwykle najbardziej przewidywalną opcją. Przepływy
subskrypcyjne/OAuth są również obsługiwane, gdy pasują do modelu konta providera.

Zobacz [/concepts/oauth](/pl/concepts/oauth), aby poznać pełny przepływ OAuth i układ
przechowywania.
W przypadku uwierzytelniania opartego na SecretRef (providery `env`/`file`/`exec`) zobacz [Secrets Management](/pl/gateway/secrets).
Informacje o regułach kwalifikacji poświadczeń i kodów powodów używanych przez `models status --probe` znajdziesz w
[Auth Credential Semantics](/pl/auth-credential-semantics).

## Zalecana konfiguracja (klucz API, dowolny provider)

Jeśli uruchamiasz długowieczny gateway, zacznij od klucza API dla wybranego
providera.
W szczególności dla Anthropic uwierzytelnianie kluczem API jest bezpieczną ścieżką. Uwierzytelnianie
w stylu subskrypcyjnym Anthropic w OpenClaw to starsza ścieżka setup-token i
należy ją traktować jako ścieżkę **Extra Usage**, a nie ścieżkę limitów planu.

1. Utwórz klucz API w konsoli providera.
2. Umieść go na **hoście gatewaya** (maszynie uruchamiającej `openclaw gateway`).

```bash
export <PROVIDER>_API_KEY="..."
openclaw models status
```

3. Jeśli Gateway działa pod systemd/launchd, najlepiej umieścić klucz w
   `~/.openclaw/.env`, aby demon mógł go odczytać:

```bash
cat >> ~/.openclaw/.env <<'EOF'
<PROVIDER>_API_KEY=...
EOF
```

Następnie zrestartuj demona (lub zrestartuj proces Gateway) i sprawdź ponownie:

```bash
openclaw models status
openclaw doctor
```

Jeśli nie chcesz samodzielnie zarządzać zmiennymi env, onboarding może zapisać
klucze API do użycia przez demona: `openclaw onboard`.

Szczegóły dotyczące dziedziczenia env (`env.shellEnv`,
`~/.openclaw/.env`, systemd/launchd) znajdziesz w [Help](/pl/help).

## Anthropic: zgodność ze starszym tokenem

Uwierzytelnianie setup-token Anthropic jest nadal dostępne w OpenClaw jako
starsza/ręczna ścieżka. Publiczna dokumentacja Claude Code Anthropic nadal opisuje bezpośrednie
użycie Claude Code w terminalu w ramach planów Claude, ale Anthropic osobno poinformował użytkowników
OpenClaw, że ścieżka logowania Claude w **OpenClaw** jest traktowana jako użycie przez narzędzie zewnętrzne i
wymaga **Extra Usage** rozliczanego oddzielnie od
subskrypcji.

Aby uzyskać najczytelniejszą ścieżkę konfiguracji, użyj klucza API Anthropic. Jeśli musisz zachować
ścieżkę Anthropic w stylu subskrypcyjnym w OpenClaw, użyj starszej ścieżki setup-token
ze świadomością, że Anthropic traktuje ją jako **Extra Usage**.

Ręczne wprowadzenie tokenu (dowolny provider; zapisuje `auth-profiles.json` + aktualizuje config):

```bash
openclaw models auth paste-token --provider openrouter
```

Obsługiwane są również odwołania do profili auth dla statycznych poświadczeń:

- poświadczenia `api_key` mogą używać `keyRef: { source, provider, id }`
- poświadczenia `token` mogą używać `tokenRef: { source, provider, id }`
- Profile w trybie OAuth nie obsługują poświadczeń SecretRef; jeśli ustawiono `auth.profiles.<id>.mode` na `"oauth"`, wejście `keyRef`/`tokenRef` oparte na SecretRef dla tego profilu jest odrzucane.

Kontrola przyjazna automatyzacji (kod wyjścia `1`, gdy wygasło/brakuje, `2`, gdy wygasa):

```bash
openclaw models status --check
```

Aktywne sondy auth:

```bash
openclaw models status --probe
```

Uwagi:

- Wiersze sond mogą pochodzić z profili auth, poświadczeń env lub `models.json`.
- Jeśli jawne `auth.order.<provider>` pomija zapisany profil, sonda zgłasza dla
  tego profilu `excluded_by_auth_order` zamiast próbować go użyć.
- Jeśli auth istnieje, ale OpenClaw nie może znaleźć kandydata modelu nadającego się do sondowania dla
  tego providera, sonda zgłasza `status: no_model`.
- Cooldowny limitu szybkości mogą być przypisane do konkretnego modelu. Profil będący w cooldownie dla jednego
  modelu może nadal nadawać się do użycia dla pokrewnego modelu u tego samego providera.

Opcjonalne skrypty operacyjne (systemd/Termux) są udokumentowane tutaj:
[Auth monitoring scripts](/pl/help/scripts#auth-monitoring-scripts)

## Uwaga dotycząca Anthropic

Backend Anthropic `claude-cli` został usunięty.

- Używaj kluczy API Anthropic dla ruchu Anthropic w OpenClaw.
- Setup-token Anthropic pozostaje starszą/ręczną ścieżką i powinien być używany z
  oczekiwaniem rozliczania Extra Usage, o którym Anthropic poinformował użytkowników OpenClaw.
- `openclaw doctor` wykrywa teraz przestarzały, usunięty stan Anthropic Claude CLI. Jeśli
  zapisane bajty poświadczeń nadal istnieją, doctor konwertuje je z powrotem do
  profili token/OAuth Anthropic. Jeśli nie, doctor usuwa przestarzałą konfigurację Claude CLI
  i kieruje do odzyskiwania przez klucz API lub setup-token.

## Sprawdzanie stanu uwierzytelniania modelu

```bash
openclaw models status
openclaw doctor
```

## Zachowanie rotacji kluczy API (gateway)

Niektórzy providerzy obsługują ponowienie żądania z alternatywnymi kluczami, gdy wywołanie API
napotka limit szybkości providera.

- Kolejność priorytetu:
  - `OPENCLAW_LIVE_<PROVIDER>_KEY` (pojedyncze nadpisanie)
  - `<PROVIDER>_API_KEYS`
  - `<PROVIDER>_API_KEY`
  - `<PROVIDER>_API_KEY_*`
- Providery Google uwzględniają również `GOOGLE_API_KEY` jako dodatkowy fallback.
- Ta sama lista kluczy jest deduplikowana przed użyciem.
- OpenClaw ponawia próbę z następnym kluczem tylko dla błędów limitu szybkości (na przykład
  `429`, `rate_limit`, `quota`, `resource exhausted`, `Too many concurrent
requests`, `ThrottlingException`, `concurrency limit reached` lub
  `workers_ai ... quota limit exceeded`).
- Błędy inne niż limity szybkości nie są ponawiane z alternatywnymi kluczami.
- Jeśli wszystkie klucze zawiodą, zwracany jest końcowy błąd z ostatniej próby.

## Kontrolowanie, które poświadczenie jest używane

### Dla sesji (polecenie czatu)

Użyj `/model <alias-or-id>@<profileId>`, aby przypiąć określone poświadczenie providera dla bieżącej sesji (przykładowe identyfikatory profili: `anthropic:default`, `anthropic:work`).

Użyj `/model` (lub `/model list`) dla zwartego selektora; użyj `/model status` dla pełnego widoku (kandydaci + następny profil auth, a także szczegóły endpointu providera, jeśli są skonfigurowane).

### Dla agenta (nadpisanie CLI)

Ustaw jawne nadpisanie kolejności profili auth dla agenta (zapisywane w `auth-profiles.json` tego agenta):

```bash
openclaw models auth order get --provider anthropic
openclaw models auth order set --provider anthropic anthropic:default
openclaw models auth order clear --provider anthropic
```

Użyj `--agent <id>`, aby wskazać konkretny agent; pomiń tę opcję, aby użyć skonfigurowanego agenta domyślnego.
Podczas debugowania problemów z kolejnością `openclaw models status --probe` pokazuje pominięte
zapisane profile jako `excluded_by_auth_order`, zamiast po cichu je omijać.
Podczas debugowania problemów z cooldownem pamiętaj, że cooldowny limitu szybkości mogą być powiązane
z jednym identyfikatorem modelu, a nie z całym profilem providera.

## Rozwiązywanie problemów

### "No credentials found"

Jeśli brakuje profilu Anthropic, skonfiguruj klucz API Anthropic na
**hoście gatewaya** lub ustaw starszą ścieżkę Anthropic setup-token, a następnie sprawdź ponownie:

```bash
openclaw models status
```

### Token wygasa/wygasł

Uruchom `openclaw models status`, aby potwierdzić, który profil wygasa. Jeśli starszy
profil tokenu Anthropic nie istnieje lub wygasł, odśwież tę konfigurację za pomocą
setup-token albo przejdź na klucz API Anthropic.

Jeśli maszyna nadal ma przestarzały, usunięty stan Anthropic Claude CLI ze starszych
buildów, uruchom:

```bash
openclaw doctor --yes
```

Doctor konwertuje `anthropic:claude-cli` z powrotem na Anthropic token/OAuth, jeśli
zapisane bajty poświadczeń nadal istnieją. W przeciwnym razie usuwa przestarzałe
odwołania do profilu/config/modelu Claude CLI i pozostawia wskazówki dotyczące kolejnych kroków.
