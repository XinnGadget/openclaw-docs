---
read_when:
    - Dodawanie automatyzacji przeglądarki sterowanej przez agenta
    - Debugowanie, dlaczego openclaw zakłóca działanie Twojej własnej przeglądarki Chrome
    - Implementowanie ustawień przeglądarki i cyklu życia w aplikacji macOS
summary: Zintegrowana usługa sterowania przeglądarką + polecenia akcji
title: Przeglądarka (zarządzana przez OpenClaw)
x-i18n:
    generated_at: "2026-04-14T09:50:55Z"
    model: gpt-5.4
    provider: openai
    source_hash: ae9ef725f544d4236d229f498c7187871c69bd18d31069b30a7e67fac53166a2
    source_path: tools/browser.md
    workflow: 15
---

# Przeglądarka (zarządzana przez openclaw)

OpenClaw może uruchamiać **dedykowany profil Chrome/Brave/Edge/Chromium**, którym steruje agent.
Jest on odizolowany od Twojej osobistej przeglądarki i zarządzany przez niewielką lokalną
usługę sterowania wewnątrz Gateway (tylko loopback).

Widok dla początkujących:

- Potraktuj to jako **oddzielną przeglądarkę tylko dla agenta**.
- Profil `openclaw` **nie** dotyka Twojego osobistego profilu przeglądarki.
- Agent może **otwierać karty, odczytywać strony, klikać i pisać** w bezpiecznym środowisku.
- Wbudowany profil `user` dołącza do Twojej prawdziwej zalogowanej sesji Chrome przez Chrome MCP.

## Co otrzymujesz

- Oddzielny profil przeglądarki o nazwie **openclaw** (domyślnie z pomarańczowym akcentem).
- Deterministyczne sterowanie kartami (lista/otwieranie/ustawianie fokusu/zamykanie).
- Działania agenta (kliknięcie/pisanie/przeciąganie/zaznaczanie), snapshoty, zrzuty ekranu, pliki PDF.
- Opcjonalna obsługa wielu profili (`openclaw`, `work`, `remote`, ...).

Ta przeglądarka **nie** jest Twoją codzienną przeglądarką. To bezpieczna, odizolowana powierzchnia do
automatyzacji i weryfikacji wykonywanych przez agenta.

## Szybki start

```bash
openclaw browser --browser-profile openclaw status
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw open https://example.com
openclaw browser --browser-profile openclaw snapshot
```

Jeśli pojawi się komunikat „Browser disabled”, włącz przeglądarkę w konfiguracji (patrz niżej) i uruchom ponownie
Gateway.

Jeśli `openclaw browser` całkowicie zniknęło albo agent mówi, że narzędzie przeglądarki
jest niedostępne, przejdź do [Brak polecenia lub narzędzia przeglądarki](/pl/tools/browser#missing-browser-command-or-tool).

## Sterowanie Plugin

Domyślne narzędzie `browser` jest teraz dołączonym Plugin, który jest dostarczany jako włączony
domyślnie. Oznacza to, że możesz go wyłączyć lub zastąpić bez usuwania reszty
systemu Plugin OpenClaw:

```json5
{
  plugins: {
    entries: {
      browser: {
        enabled: false,
      },
    },
  },
}
```

Wyłącz dołączony Plugin przed zainstalowaniem innego Plugin, który udostępnia tę
samą nazwę narzędzia `browser`. Domyślne środowisko przeglądarki wymaga obu warunków:

- `plugins.entries.browser.enabled` nie może być wyłączone
- `browser.enabled=true`

Jeśli wyłączysz tylko Plugin, dołączone CLI przeglądarki (`openclaw browser`),
metoda gateway (`browser.request`), narzędzie agenta i domyślna usługa sterowania
przeglądarką znikną razem. Twoja konfiguracja `browser.*` pozostanie nienaruszona,
aby mogła zostać ponownie użyta przez zastępczy Plugin.

Dołączony Plugin przeglądarki jest teraz również właścicielem implementacji środowiska wykonawczego przeglądarki.
Rdzeń zachowuje tylko współdzielone pomocniki Plugin SDK oraz kompatybilnościowe re-exporty dla
starszych wewnętrznych ścieżek importu. W praktyce usunięcie lub zastąpienie pakietu Plugin przeglądarki
usuwa zestaw funkcji przeglądarki zamiast pozostawiać drugie środowisko wykonawcze należące do rdzenia.

Zmiany konfiguracji przeglądarki nadal wymagają ponownego uruchomienia Gateway, aby dołączony Plugin
mógł ponownie zarejestrować swoją usługę przeglądarki z nowymi ustawieniami.

## Brak polecenia lub narzędzia przeglądarki

Jeśli po aktualizacji `openclaw browser` nagle stanie się nieznanym poleceniem albo
agent zgłasza, że brakuje narzędzia przeglądarki, najczęstszą przyczyną jest
restrykcyjna lista `plugins.allow`, która nie zawiera `browser`.

Przykład błędnej konfiguracji:

```json5
{
  plugins: {
    allow: ["telegram"],
  },
}
```

Napraw to, dodając `browser` do listy dozwolonych Plugin:

```json5
{
  plugins: {
    allow: ["telegram", "browser"],
  },
}
```

Ważne uwagi:

- Samo `browser.enabled=true` nie wystarczy, gdy ustawione jest `plugins.allow`.
- Samo `plugins.entries.browser.enabled=true` również nie wystarczy, gdy ustawione jest `plugins.allow`.
- `tools.alsoAllow: ["browser"]` **nie** ładuje dołączonego Plugin przeglądarki. Tylko dostosowuje politykę narzędzi po tym, jak Plugin został już załadowany.
- Jeśli nie potrzebujesz restrykcyjnej listy dozwolonych Plugin, usunięcie `plugins.allow` również przywraca domyślne zachowanie dołączonej przeglądarki.

Typowe objawy:

- `openclaw browser` jest nieznanym poleceniem.
- Brakuje `browser.request`.
- Agent zgłasza, że narzędzie przeglądarki jest niedostępne lub go brakuje.

## Profile: `openclaw` vs `user`

- `openclaw`: zarządzana, odizolowana przeglądarka (nie wymaga rozszerzenia).
- `user`: wbudowany profil dołączania Chrome MCP do Twojej **prawdziwej zalogowanej sesji Chrome**.

Dla wywołań narzędzia przeglądarki przez agenta:

- Domyślnie: używaj odizolowanej przeglądarki `openclaw`.
- Preferuj `profile="user"`, gdy znaczenie mają istniejące zalogowane sesje i użytkownik
  jest przy komputerze, aby kliknąć/zatwierdzić ewentualny monit o dołączenie.
- `profile` jest jawnym nadpisaniem, gdy chcesz określonego trybu przeglądarki.

Ustaw `browser.defaultProfile: "openclaw"`, jeśli chcesz domyślnie używać trybu zarządzanego.

## Konfiguracja

Ustawienia przeglądarki znajdują się w `~/.openclaw/openclaw.json`.

```json5
{
  browser: {
    enabled: true, // domyślnie: true
    ssrfPolicy: {
      // dangerouslyAllowPrivateNetwork: true, // włącz tylko dla zaufanego dostępu do sieci prywatnej
      // allowPrivateNetwork: true, // starszy alias
      // hostnameAllowlist: ["*.example.com", "example.com"],
      // allowedHostnames: ["localhost"],
    },
    // cdpUrl: "http://127.0.0.1:18792", // starsze nadpisanie pojedynczego profilu
    remoteCdpTimeoutMs: 1500, // limit czasu HTTP zdalnego CDP (ms)
    remoteCdpHandshakeTimeoutMs: 3000, // limit czasu handshake WebSocket zdalnego CDP (ms)
    defaultProfile: "openclaw",
    color: "#FF4500",
    headless: false,
    noSandbox: false,
    attachOnly: false,
    executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser",
    profiles: {
      openclaw: { cdpPort: 18800, color: "#FF4500" },
      work: { cdpPort: 18801, color: "#0066CC" },
      user: {
        driver: "existing-session",
        attachOnly: true,
        color: "#00AA00",
      },
      brave: {
        driver: "existing-session",
        attachOnly: true,
        userDataDir: "~/Library/Application Support/BraveSoftware/Brave-Browser",
        color: "#FB542B",
      },
      remote: { cdpUrl: "http://10.0.0.42:9222", color: "#00AA00" },
    },
  },
}
```

Uwagi:

- Usługa sterowania przeglądarką wiąże się z loopback na porcie wyprowadzonym z `gateway.port`
  (domyślnie: `18791`, czyli gateway + 2).
- Jeśli nadpiszesz port Gateway (`gateway.port` lub `OPENCLAW_GATEWAY_PORT`),
  wyprowadzone porty przeglądarki przesuną się tak, aby pozostać w tej samej „rodzinie”.
- `cdpUrl` domyślnie wskazuje zarządzany lokalny port CDP, jeśli nie jest ustawiony.
- `remoteCdpTimeoutMs` ma zastosowanie do sprawdzania osiągalności zdalnego CDP (nie-loopback).
- `remoteCdpHandshakeTimeoutMs` ma zastosowanie do sprawdzania osiągalności handshake WebSocket zdalnego CDP.
- Nawigacja przeglądarki/otwieranie kart jest chronione przed SSRF przed nawigacją i ponownie sprawdzane metodą best-effort pod kątem końcowego adresu URL `http(s)` po nawigacji.
- W ścisłym trybie SSRF sprawdzane są także wykrywanie/sprawdzanie zdalnych punktów końcowych CDP (`cdpUrl`, w tym wyszukiwania `/json/version`).
- `browser.ssrfPolicy.dangerouslyAllowPrivateNetwork` jest domyślnie wyłączone. Ustaw `true` tylko wtedy, gdy świadomie ufasz dostępowi przeglądarki do sieci prywatnej.
- `browser.ssrfPolicy.allowPrivateNetwork` pozostaje obsługiwane jako starszy alias dla zgodności.
- `attachOnly: true` oznacza „nigdy nie uruchamiaj lokalnej przeglądarki; dołączaj tylko wtedy, gdy jest już uruchomiona”.
- `color` i per-profilowe `color` nadają odcień interfejsowi przeglądarki, aby było widać, który profil jest aktywny.
- Profilem domyślnym jest `openclaw` (samodzielna przeglądarka zarządzana przez OpenClaw). Użyj `defaultProfile: "user"`, aby wybrać przeglądarkę zalogowanego użytkownika.
- Kolejność automatycznego wykrywania: systemowa domyślna przeglądarka, jeśli jest oparta na Chromium; w przeciwnym razie Chrome → Brave → Edge → Chromium → Chrome Canary.
- Lokalne profile `openclaw` automatycznie przypisują `cdpPort`/`cdpUrl` — ustawiaj je tylko dla zdalnego CDP.
- `driver: "existing-session"` używa Chrome DevTools MCP zamiast surowego CDP. Nie
  ustawiaj `cdpUrl` dla tego sterownika.
- Ustaw `browser.profiles.<name>.userDataDir`, gdy profil existing-session
  ma dołączać do niestandardowego profilu użytkownika Chromium, takiego jak Brave lub Edge.

## Używanie Brave (lub innej przeglądarki opartej na Chromium)

Jeśli Twoja **systemowa domyślna** przeglądarka jest oparta na Chromium (Chrome/Brave/Edge itd.),
OpenClaw użyje jej automatycznie. Ustaw `browser.executablePath`, aby nadpisać
automatyczne wykrywanie:

Przykład CLI:

```bash
openclaw config set browser.executablePath "/usr/bin/google-chrome"
```

```json5
// macOS
{
  browser: {
    executablePath: "/Applications/Brave Browser.app/Contents/MacOS/Brave Browser"
  }
}

// Windows
{
  browser: {
    executablePath: "C:\\Program Files\\BraveSoftware\\Brave-Browser\\Application\\brave.exe"
  }
}

// Linux
{
  browser: {
    executablePath: "/usr/bin/brave-browser"
  }
}
```

## Sterowanie lokalne vs zdalne

- **Sterowanie lokalne (domyślne):** Gateway uruchamia usługę sterowania loopback i może uruchomić lokalną przeglądarkę.
- **Sterowanie zdalne (host Node):** uruchom hosta Node na komputerze, na którym jest przeglądarka; Gateway będzie przekazywać do niego działania przeglądarki.
- **Zdalny CDP:** ustaw `browser.profiles.<name>.cdpUrl` (lub `browser.cdpUrl`), aby
  dołączyć do zdalnej przeglądarki opartej na Chromium. W takim przypadku OpenClaw nie uruchomi lokalnej przeglądarki.

Zachowanie przy zatrzymywaniu różni się w zależności od trybu profilu:

- lokalne zarządzane profile: `openclaw browser stop` zatrzymuje proces przeglądarki,
  który uruchomił OpenClaw
- profile tylko-dołączane i zdalne profile CDP: `openclaw browser stop` zamyka aktywną
  sesję sterowania i zwalnia nadpisania emulacji Playwright/CDP (viewport,
  schemat kolorów, ustawienia regionalne, strefa czasowa, tryb offline i podobny stan),
  mimo że żaden proces przeglądarki nie został uruchomiony przez OpenClaw

Zdalne adresy URL CDP mogą zawierać uwierzytelnianie:

- Tokeny zapytania (np. `https://provider.example?token=<token>`)
- Uwierzytelnianie HTTP Basic (np. `https://user:pass@provider.example`)

OpenClaw zachowuje dane uwierzytelniające przy wywoływaniu punktów końcowych `/json/*` oraz podczas łączenia
z WebSocket CDP. Zamiast zatwierdzać tokeny w plikach konfiguracyjnych, preferuj zmienne środowiskowe lub menedżery sekretów.

## Proxy przeglądarki Node (domyślnie bez konfiguracji)

Jeśli uruchamiasz **hosta Node** na komputerze, na którym znajduje się Twoja przeglądarka, OpenClaw może
automatycznie kierować wywołania narzędzia przeglądarki do tego node bez dodatkowej konfiguracji przeglądarki.
To domyślna ścieżka dla zdalnych bram.

Uwagi:

- Host Node udostępnia swój lokalny serwer sterowania przeglądarką przez **polecenie proxy**.
- Profile pochodzą z własnej konfiguracji `browser.profiles` node (takiej samej jak lokalnie).
- `nodeHost.browserProxy.allowProfiles` jest opcjonalne. Pozostaw puste, aby zachować starsze/domyslne zachowanie: wszystkie skonfigurowane profile pozostają osiągalne przez proxy, w tym trasy tworzenia/usuwania profili.
- Jeśli ustawisz `nodeHost.browserProxy.allowProfiles`, OpenClaw traktuje to jako granicę minimalnych uprawnień: tylko profile z listy dozwolonych mogą być wskazywane, a trasy trwałego tworzenia/usuwania profili są blokowane na powierzchni proxy.
- Wyłącz tę funkcję, jeśli jej nie chcesz:
  - Na node: `nodeHost.browserProxy.enabled=false`
  - Na gateway: `gateway.nodes.browser.mode="off"`

## Browserless (hostowany zdalny CDP)

[Browserless](https://browserless.io) to hostowana usługa Chromium, która udostępnia
adresy URL połączeń CDP przez HTTPS i WebSocket. OpenClaw może używać obu form, ale
dla zdalnego profilu przeglądarki najprostszą opcją jest bezpośredni adres WebSocket
z dokumentacji połączeń Browserless.

Przykład:

```json5
{
  browser: {
    enabled: true,
    defaultProfile: "browserless",
    remoteCdpTimeoutMs: 2000,
    remoteCdpHandshakeTimeoutMs: 4000,
    profiles: {
      browserless: {
        cdpUrl: "wss://production-sfo.browserless.io?token=<BROWSERLESS_API_KEY>",
        color: "#00AA00",
      },
    },
  },
}
```

Uwagi:

- Zastąp `<BROWSERLESS_API_KEY>` swoim prawdziwym tokenem Browserless.
- Wybierz punkt końcowy regionu zgodny z Twoim kontem Browserless (zobacz ich dokumentację).
- Jeśli Browserless podaje bazowy adres URL HTTPS, możesz albo przekształcić go na
  `wss://` w celu bezpośredniego połączenia CDP, albo pozostawić adres HTTPS i pozwolić OpenClaw
  wykryć `/json/version`.

## Dostawcy bezpośredniego WebSocket CDP

Niektóre hostowane usługi przeglądarki udostępniają **bezpośredni punkt końcowy WebSocket** zamiast
standardowego wykrywania CDP opartego na HTTP (`/json/version`). OpenClaw obsługuje oba warianty:

- **Punkty końcowe HTTP(S)** — OpenClaw wywołuje `/json/version`, aby wykryć
  adres URL debuggera WebSocket, a następnie się łączy.
- **Punkty końcowe WebSocket** (`ws://` / `wss://`) — OpenClaw łączy się bezpośrednio,
  pomijając `/json/version`. Używaj tego w usługach takich jak
  [Browserless](https://browserless.io),
  [Browserbase](https://www.browserbase.com) lub u dowolnego dostawcy, który przekazuje Ci
  adres URL WebSocket.

### Browserbase

[Browserbase](https://www.browserbase.com) to platforma chmurowa do uruchamiania
przeglądarek headless z wbudowanym rozwiązywaniem CAPTCHA, trybem stealth i
proxy rezydencyjnymi.

```json5
{
  browser: {
    enabled: true,
    defaultProfile: "browserbase",
    remoteCdpTimeoutMs: 3000,
    remoteCdpHandshakeTimeoutMs: 5000,
    profiles: {
      browserbase: {
        cdpUrl: "wss://connect.browserbase.com?apiKey=<BROWSERBASE_API_KEY>",
        color: "#F97316",
      },
    },
  },
}
```

Uwagi:

- [Zarejestruj się](https://www.browserbase.com/sign-up) i skopiuj swój **API Key**
  z [panelu Overview](https://www.browserbase.com/overview).
- Zastąp `<BROWSERBASE_API_KEY>` swoim prawdziwym kluczem API Browserbase.
- Browserbase automatycznie tworzy sesję przeglądarki przy połączeniu WebSocket, więc
  nie jest potrzebny ręczny krok tworzenia sesji.
- Warstwa darmowa pozwala na jedną współbieżną sesję i jedną godzinę przeglądarki miesięcznie.
  Zobacz [cennik](https://www.browserbase.com/pricing), aby poznać limity planów płatnych.
- Zobacz [dokumentację Browserbase](https://docs.browserbase.com), aby uzyskać pełne
  informacje referencyjne o API, przewodniki po SDK i przykłady integracji.

## Bezpieczeństwo

Kluczowe założenia:

- Sterowanie przeglądarką jest dostępne tylko przez loopback; dostęp odbywa się przez uwierzytelnianie Gateway lub parowanie node.
- Samodzielne loopback API HTTP przeglądarki używa **wyłącznie uwierzytelniania wspólnym sekretem**:
  token bearer gateway, `x-openclaw-password` lub uwierzytelnianie HTTP Basic z
  skonfigurowanym hasłem gateway.
- Nagłówki tożsamości Tailscale Serve i `gateway.auth.mode: "trusted-proxy"` **nie**
  uwierzytelniają tego samodzielnego loopback API przeglądarki.
- Jeśli sterowanie przeglądarką jest włączone i nie skonfigurowano uwierzytelniania wspólnym sekretem, OpenClaw
  automatycznie generuje `gateway.auth.token` przy uruchomieniu i zapisuje go w konfiguracji.
- OpenClaw **nie** generuje tego tokenu automatycznie, gdy `gateway.auth.mode` jest
  już ustawione na `password`, `none` lub `trusted-proxy`.
- Utrzymuj Gateway i wszystkie hosty node w sieci prywatnej (Tailscale); unikaj publicznej ekspozycji.
- Traktuj zdalne adresy URL/tokeny CDP jako sekrety; preferuj zmienne środowiskowe lub menedżer sekretów.

Wskazówki dotyczące zdalnego CDP:

- Jeśli to możliwe, preferuj szyfrowane punkty końcowe (HTTPS lub WSS) i tokeny o krótkim czasie życia.
- Unikaj osadzania długowiecznych tokenów bezpośrednio w plikach konfiguracyjnych.

## Profile (wiele przeglądarek)

OpenClaw obsługuje wiele nazwanych profili (konfiguracji routingu). Profile mogą być:

- **zarządzane przez OpenClaw**: dedykowana instancja przeglądarki opartej na Chromium z własnym katalogiem danych użytkownika i portem CDP
- **zdalne**: jawny adres URL CDP (przeglądarka oparta na Chromium uruchomiona gdzie indziej)
- **istniejąca sesja**: Twój istniejący profil Chrome przez automatyczne połączenie Chrome DevTools MCP

Ustawienia domyślne:

- Profil `openclaw` jest tworzony automatycznie, jeśli go brakuje.
- Profil `user` jest wbudowany do dołączania istniejącej sesji Chrome MCP.
- Profile istniejącej sesji poza `user` są opcjonalne; utwórz je za pomocą `--driver existing-session`.
- Lokalne porty CDP są domyślnie przydzielane z zakresu **18800–18899**.
- Usunięcie profilu przenosi jego lokalny katalog danych do Kosza.

Wszystkie punkty końcowe sterowania akceptują `?profile=<name>`; CLI używa `--browser-profile`.

## Istniejąca sesja przez Chrome DevTools MCP

OpenClaw może także dołączyć do uruchomionego profilu przeglądarki opartej na Chromium przez
oficjalny serwer Chrome DevTools MCP. Pozwala to ponownie użyć kart i stanu logowania,
które są już otwarte w tym profilu przeglądarki.

Oficjalne materiały referencyjne i instrukcje konfiguracji:

- [Chrome for Developers: Use Chrome DevTools MCP with your browser session](https://developer.chrome.com/blog/chrome-devtools-mcp-debug-your-browser-session)
- [Chrome DevTools MCP README](https://github.com/ChromeDevTools/chrome-devtools-mcp)

Wbudowany profil:

- `user`

Opcjonalnie: utwórz własny niestandardowy profil istniejącej sesji, jeśli chcesz
innej nazwy, koloru lub katalogu danych przeglądarki.

Domyślne zachowanie:

- Wbudowany profil `user` używa automatycznego połączenia Chrome MCP, które jest kierowane na
  domyślny lokalny profil Google Chrome.

Użyj `userDataDir` dla Brave, Edge, Chromium lub niestandardowego profilu Chrome:

```json5
{
  browser: {
    profiles: {
      brave: {
        driver: "existing-session",
        attachOnly: true,
        userDataDir: "~/Library/Application Support/BraveSoftware/Brave-Browser",
        color: "#FB542B",
      },
    },
  },
}
```

Następnie w odpowiadającej przeglądarce:

1. Otwórz stronę inspect tej przeglądarki dla zdalnego debugowania.
2. Włącz zdalne debugowanie.
3. Pozostaw przeglądarkę uruchomioną i zatwierdź monit o połączenie, gdy OpenClaw będzie się dołączać.

Typowe strony inspect:

- Chrome: `chrome://inspect/#remote-debugging`
- Brave: `brave://inspect/#remote-debugging`
- Edge: `edge://inspect/#remote-debugging`

Test smoke dla aktywnego dołączania:

```bash
openclaw browser --browser-profile user start
openclaw browser --browser-profile user status
openclaw browser --browser-profile user tabs
openclaw browser --browser-profile user snapshot --format ai
```

Jak wygląda powodzenie:

- `status` pokazuje `driver: existing-session`
- `status` pokazuje `transport: chrome-mcp`
- `status` pokazuje `running: true`
- `tabs` wyświetla listę już otwartych kart przeglądarki
- `snapshot` zwraca refs z wybranej aktywnej karty

Co sprawdzić, jeśli dołączenie nie działa:

- docelowa przeglądarka oparta na Chromium ma wersję `144+`
- zdalne debugowanie jest włączone na stronie inspect tej przeglądarki
- przeglądarka wyświetliła monit o zgodę na dołączenie i został on zaakceptowany
- `openclaw doctor` migruje starą konfigurację przeglądarki opartą na rozszerzeniu i sprawdza,
  czy Chrome jest zainstalowane lokalnie dla domyślnych profili auto-connect, ale nie może
  włączyć za Ciebie zdalnego debugowania po stronie przeglądarki

Użycie przez agenta:

- Użyj `profile="user"`, gdy potrzebujesz zalogowanego stanu przeglądarki użytkownika.
- Jeśli używasz niestandardowego profilu istniejącej sesji, przekaż jawną nazwę tego profilu.
- Wybieraj ten tryb tylko wtedy, gdy użytkownik jest przy komputerze, aby zatwierdzić
  monit o dołączenie.
- Gateway lub host node może uruchomić `npx chrome-devtools-mcp@latest --autoConnect`

Uwagi:

- Ta ścieżka wiąże się z większym ryzykiem niż odizolowany profil `openclaw`, ponieważ może
  działać wewnątrz Twojej zalogowanej sesji przeglądarki.
- OpenClaw nie uruchamia przeglądarki dla tego sterownika; dołącza tylko do
  istniejącej sesji.
- OpenClaw używa tutaj oficjalnego przepływu Chrome DevTools MCP `--autoConnect`. Jeśli
  ustawiono `userDataDir`, OpenClaw przekazuje je dalej, aby wskazać jawnie ten
  katalog danych użytkownika Chromium.
- Zrzuty ekranu istniejącej sesji obsługują przechwycenia strony i przechwycenia elementów przez `--ref`
  ze snapshotów, ale nie selektory CSS `--element`.
- Zrzuty ekranu stron istniejącej sesji działają bez Playwright przez Chrome MCP.
  Oparte na ref zrzuty ekranu elementów (`--ref`) również tam działają, ale `--full-page`
  nie może być łączone z `--ref` ani `--element`.
- Działania istniejącej sesji są nadal bardziej ograniczone niż w ścieżce
  zarządzanej przeglądarki:
  - `click`, `type`, `hover`, `scrollIntoView`, `drag` i `select` wymagają
    refs ze snapshotów zamiast selektorów CSS
  - `click` obsługuje tylko lewy przycisk (bez nadpisywania przycisku i modyfikatorów)
  - `type` nie obsługuje `slowly=true`; użyj `fill` lub `press`
  - `press` nie obsługuje `delayMs`
  - `hover`, `scrollIntoView`, `drag`, `select`, `fill` i `evaluate` nie
    obsługują nadpisywania limitu czasu dla pojedynczego wywołania
  - `select` obecnie obsługuje tylko jedną wartość
- `wait --url` dla istniejącej sesji obsługuje dokładne, częściowe i globowe wzorce
  tak jak inne sterowniki przeglądarki. `wait --load networkidle` nie jest jeszcze obsługiwane.
- Hooki przesyłania plików dla istniejącej sesji wymagają `ref` lub `inputRef`, obsługują jeden plik naraz
  i nie obsługują wskazywania CSS `element`.
- Hooki dialogów istniejącej sesji nie obsługują nadpisywania limitu czasu.
- Niektóre funkcje nadal wymagają ścieżki zarządzanej przeglądarki, w tym działania wsadowe,
  eksport PDF, przechwytywanie pobrań i `responsebody`.
- Istniejąca sesja jest lokalna względem hosta. Jeśli Chrome znajduje się na innej maszynie lub
  w innej przestrzeni nazw sieci, użyj zamiast tego zdalnego CDP lub hosta node.

## Gwarancje izolacji

- **Dedykowany katalog danych użytkownika**: nigdy nie dotyka Twojego osobistego profilu przeglądarki.
- **Dedykowane porty**: unika `9222`, aby zapobiegać kolizjom z przepływami pracy deweloperskiej.
- **Deterministyczne sterowanie kartami**: kierowanie na karty według `targetId`, a nie „ostatnia karta”.

## Wybór przeglądarki

Przy lokalnym uruchamianiu OpenClaw wybiera pierwszą dostępną:

1. Chrome
2. Brave
3. Edge
4. Chromium
5. Chrome Canary

Możesz to nadpisać za pomocą `browser.executablePath`.

Platformy:

- macOS: sprawdza `/Applications` i `~/Applications`.
- Linux: szuka `google-chrome`, `brave`, `microsoft-edge`, `chromium` itd.
- Windows: sprawdza typowe lokalizacje instalacji.

## API sterowania (opcjonalnie)

Tylko dla integracji lokalnych Gateway udostępnia niewielkie loopback API HTTP:

- Status/start/stop: `GET /`, `POST /start`, `POST /stop`
- Karty: `GET /tabs`, `POST /tabs/open`, `POST /tabs/focus`, `DELETE /tabs/:targetId`
- Snapshot/zrzut ekranu: `GET /snapshot`, `POST /screenshot`
- Działania: `POST /navigate`, `POST /act`
- Hooki: `POST /hooks/file-chooser`, `POST /hooks/dialog`
- Pobrania: `POST /download`, `POST /wait/download`
- Debugowanie: `GET /console`, `POST /pdf`
- Debugowanie: `GET /errors`, `GET /requests`, `POST /trace/start`, `POST /trace/stop`, `POST /highlight`
- Sieć: `POST /response/body`
- Stan: `GET /cookies`, `POST /cookies/set`, `POST /cookies/clear`
- Stan: `GET /storage/:kind`, `POST /storage/:kind/set`, `POST /storage/:kind/clear`
- Ustawienia: `POST /set/offline`, `POST /set/headers`, `POST /set/credentials`, `POST /set/geolocation`, `POST /set/media`, `POST /set/timezone`, `POST /set/locale`, `POST /set/device`

Wszystkie punkty końcowe akceptują `?profile=<name>`.

Jeśli skonfigurowano uwierzytelnianie gateway wspólnym sekretem, trasy HTTP przeglądarki również wymagają uwierzytelniania:

- `Authorization: Bearer <gateway token>`
- `x-openclaw-password: <gateway password>` lub uwierzytelnianie HTTP Basic z tym hasłem

Uwagi:

- To samodzielne loopback API przeglądarki **nie** korzysta z trusted-proxy ani
  nagłówków tożsamości Tailscale Serve.
- Jeśli `gateway.auth.mode` ma wartość `none` lub `trusted-proxy`, te loopback trasy przeglądarki
  nie dziedziczą tych trybów opartych na tożsamości; utrzymuj je tylko na loopback.

### Kontrakt błędów `/act`

`POST /act` używa ustrukturyzowanej odpowiedzi błędu dla walidacji na poziomie trasy i
błędów polityki:

```json
{ "error": "<message>", "code": "ACT_*" }
```

Aktualne wartości `code`:

- `ACT_KIND_REQUIRED` (HTTP 400): brakuje `kind` lub nie jest rozpoznawane.
- `ACT_INVALID_REQUEST` (HTTP 400): payload działania nie przeszedł normalizacji lub walidacji.
- `ACT_SELECTOR_UNSUPPORTED` (HTTP 400): użyto `selector` z nieobsługiwanym rodzajem działania.
- `ACT_EVALUATE_DISABLED` (HTTP 403): `evaluate` (lub `wait --fn`) jest wyłączone w konfiguracji.
- `ACT_TARGET_ID_MISMATCH` (HTTP 403): najwyższego poziomu lub wsadowe `targetId` koliduje z celem żądania.
- `ACT_EXISTING_SESSION_UNSUPPORTED` (HTTP 501): działanie nie jest obsługiwane dla profili istniejącej sesji.

Inne błędy czasu działania mogą nadal zwracać `{ "error": "<message>" }` bez pola
`code`.

### Wymaganie Playwright

Niektóre funkcje (navigate/act/snapshot AI/snapshot roli, zrzuty ekranu elementów,
PDF) wymagają Playwright. Jeśli Playwright nie jest zainstalowany, te punkty końcowe zwracają
czytelny błąd 501.

Co nadal działa bez Playwright:

- Snapshoty ARIA
- Zrzuty ekranu stron dla zarządzanej przeglądarki `openclaw`, gdy dostępny jest
  WebSocket CDP dla danej karty
- Zrzuty ekranu stron dla profili `existing-session` / Chrome MCP
- Oparte na `ref` zrzuty ekranu istniejącej sesji (`--ref`) z danych wyjściowych snapshotu

Co nadal wymaga Playwright:

- `navigate`
- `act`
- Snapshoty AI / snapshoty roli
- Zrzuty ekranu elementów przez selektor CSS (`--element`)
- Eksport pełnego PDF przeglądarki

Zrzuty ekranu elementów odrzucają też `--full-page`; trasa zwraca `fullPage is
not supported for element screenshots`.

Jeśli widzisz `Playwright is not available in this gateway build`, zainstaluj pełny
pakiet Playwright (nie `playwright-core`) i uruchom gateway ponownie albo zainstaluj
OpenClaw ponownie z obsługą przeglądarki.

#### Instalacja Playwright w Docker

Jeśli Twój Gateway działa w Docker, unikaj `npx playwright` (konflikty nadpisań npm).
Użyj zamiast tego dołączonego CLI:

```bash
docker compose run --rm openclaw-cli \
  node /app/node_modules/playwright-core/cli.js install chromium
```

Aby zachować pobrane przeglądarki, ustaw `PLAYWRIGHT_BROWSERS_PATH` (na przykład
`/home/node/.cache/ms-playwright`) i upewnij się, że `/home/node` jest zachowywane przez
`OPENCLAW_HOME_VOLUME` lub bind mount. Zobacz [Docker](/pl/install/docker).

## Jak to działa (wewnętrznie)

Przepływ na wysokim poziomie:

- Niewielki **serwer sterowania** akceptuje żądania HTTP.
- Łączy się z przeglądarkami opartymi na Chromium (Chrome/Brave/Edge/Chromium) przez **CDP**.
- Do zaawansowanych działań (kliknięcie/pisanie/snapshot/PDF) używa **Playwright** na warstwie
  CDP.
- Gdy brakuje Playwright, dostępne są tylko operacje niewymagające Playwright.

Taka konstrukcja zapewnia agentowi stabilny, deterministyczny interfejs, a jednocześnie pozwala
Ci wymieniać lokalne/zdalne przeglądarki i profile.

## Szybkie odniesienie do CLI

Wszystkie polecenia akceptują `--browser-profile <name>`, aby wskazać konkretny profil.
Wszystkie polecenia akceptują też `--json` dla danych wyjściowych czytelnych maszynowo (stabilne payloady).

Podstawy:

- `openclaw browser status`
- `openclaw browser start`
- `openclaw browser stop`
- `openclaw browser tabs`
- `openclaw browser tab`
- `openclaw browser tab new`
- `openclaw browser tab select 2`
- `openclaw browser tab close 2`
- `openclaw browser open https://example.com`
- `openclaw browser focus abcd1234`
- `openclaw browser close abcd1234`

Inspekcja:

- `openclaw browser screenshot`
- `openclaw browser screenshot --full-page`
- `openclaw browser screenshot --ref 12`
- `openclaw browser screenshot --ref e12`
- `openclaw browser snapshot`
- `openclaw browser snapshot --format aria --limit 200`
- `openclaw browser snapshot --interactive --compact --depth 6`
- `openclaw browser snapshot --efficient`
- `openclaw browser snapshot --labels`
- `openclaw browser snapshot --selector "#main" --interactive`
- `openclaw browser snapshot --frame "iframe#main" --interactive`
- `openclaw browser console --level error`

Uwaga dotycząca cyklu życia:

- Dla profili tylko-dołączanych i zdalnych profili CDP `openclaw browser stop` nadal jest
  właściwym poleceniem czyszczenia po testach. Zamyka aktywną sesję sterowania i
  usuwa tymczasowe nadpisania emulacji zamiast zabijać bazową
  przeglądarkę.
- `openclaw browser errors --clear`
- `openclaw browser requests --filter api --clear`
- `openclaw browser pdf`
- `openclaw browser responsebody "**/api" --max-chars 5000`

Działania:

- `openclaw browser navigate https://example.com`
- `openclaw browser resize 1280 720`
- `openclaw browser click 12 --double`
- `openclaw browser click e12 --double`
- `openclaw browser type 23 "hello" --submit`
- `openclaw browser press Enter`
- `openclaw browser hover 44`
- `openclaw browser scrollintoview e12`
- `openclaw browser drag 10 11`
- `openclaw browser select 9 OptionA OptionB`
- `openclaw browser download e12 report.pdf`
- `openclaw browser waitfordownload report.pdf`
- `openclaw browser upload /tmp/openclaw/uploads/file.pdf`
- `openclaw browser fill --fields '[{"ref":"1","type":"text","value":"Ada"}]'`
- `openclaw browser dialog --accept`
- `openclaw browser wait --text "Done"`
- `openclaw browser wait "#main" --url "**/dash" --load networkidle --fn "window.ready===true"`
- `openclaw browser evaluate --fn '(el) => el.textContent' --ref 7`
- `openclaw browser highlight e12`
- `openclaw browser trace start`
- `openclaw browser trace stop`

Stan:

- `openclaw browser cookies`
- `openclaw browser cookies set session abc123 --url "https://example.com"`
- `openclaw browser cookies clear`
- `openclaw browser storage local get`
- `openclaw browser storage local set theme dark`
- `openclaw browser storage session clear`
- `openclaw browser set offline on`
- `openclaw browser set headers --headers-json '{"X-Debug":"1"}'`
- `openclaw browser set credentials user pass`
- `openclaw browser set credentials --clear`
- `openclaw browser set geo 37.7749 -122.4194 --origin "https://example.com"`
- `openclaw browser set geo --clear`
- `openclaw browser set media dark`
- `openclaw browser set timezone America/New_York`
- `openclaw browser set locale en-US`
- `openclaw browser set device "iPhone 14"`

Uwagi:

- `upload` i `dialog` to wywołania **uzbrajające**; uruchom je przed kliknięciem/naciśnięciem,
  które wywołuje selektor plików/okno dialogowe.
- Ścieżki wyjściowe pobrań i trace są ograniczone do tymczasowych katalogów głównych OpenClaw:
  - trace: `/tmp/openclaw` (zapasowo: `${os.tmpdir()}/openclaw`)
  - pobrania: `/tmp/openclaw/downloads` (zapasowo: `${os.tmpdir()}/openclaw/downloads`)
- Ścieżki przesyłania są ograniczone do tymczasowego katalogu głównego uploadów OpenClaw:
  - uploady: `/tmp/openclaw/uploads` (zapasowo: `${os.tmpdir()}/openclaw/uploads`)
- `upload` może również ustawiać wejścia plików bezpośrednio przez `--input-ref` lub `--element`.
- `snapshot`:
  - `--format ai` (domyślne, gdy Playwright jest zainstalowany): zwraca snapshot AI z numerycznymi refs (`aria-ref="<n>"`).
  - `--format aria`: zwraca drzewo dostępności (bez refs; tylko do inspekcji).
  - `--efficient` (lub `--mode efficient`): kompaktowe ustawienie wstępne snapshotu roli (interactive + compact + depth + niższe maxChars).
  - Domyślna konfiguracja (tylko narzędzie/CLI): ustaw `browser.snapshotDefaults.mode: "efficient"`, aby używać wydajnych snapshotów, gdy wywołujący nie przekaże trybu (zobacz [Konfiguracja Gateway](/pl/gateway/configuration-reference#browser)).
  - Opcje snapshotu roli (`--interactive`, `--compact`, `--depth`, `--selector`) wymuszają snapshot oparty na roli z refs takimi jak `ref=e12`.
  - `--frame "<iframe selector>"` zawęża snapshoty roli do iframe (w parze z refs roli takimi jak `e12`).
  - `--interactive` wypisuje płaską, łatwą do wybrania listę elementów interaktywnych (najlepszą do wykonywania działań).
  - `--labels` dodaje zrzut ekranu tylko viewportu z nałożonymi etykietami ref (wypisuje `MEDIA:<path>`).
- `click`/`type`/itd. wymagają `ref` ze `snapshot` (numerycznego `12` lub ref roli `e12`).
  Selektory CSS celowo nie są obsługiwane dla działań.

## Snapshoty i refs

OpenClaw obsługuje dwa style „snapshotów”:

- **Snapshot AI (numeryczne refs)**: `openclaw browser snapshot` (domyślnie; `--format ai`)
  - Wynik: tekstowy snapshot zawierający numeryczne refs.
  - Działania: `openclaw browser click 12`, `openclaw browser type 23 "hello"`.
  - Wewnętrznie ref jest rozwiązywany przez `aria-ref` z Playwright.

- **Snapshot roli (refs roli takie jak `e12`)**: `openclaw browser snapshot --interactive` (lub `--compact`, `--depth`, `--selector`, `--frame`)
  - Wynik: lista/drzewo oparte na roli z `[ref=e12]` (oraz opcjonalnie `[nth=1]`).
  - Działania: `openclaw browser click e12`, `openclaw browser highlight e12`.
  - Wewnętrznie ref jest rozwiązywany przez `getByRole(...)` (plus `nth()` dla duplikatów).
  - Dodaj `--labels`, aby dołączyć zrzut ekranu viewportu z nałożonymi etykietami `e12`.

Zachowanie refs:

- Refs **nie są stabilne między nawigacjami**; jeśli coś się nie powiedzie, uruchom ponownie `snapshot` i użyj świeżego ref.
- Jeśli snapshot roli został wykonany z `--frame`, refs roli są ograniczone do tego iframe aż do następnego snapshotu roli.

## Rozszerzone możliwości `wait`

Możesz czekać na więcej niż tylko czas/tekst:

- Czekanie na URL (globy obsługiwane przez Playwright):
  - `openclaw browser wait --url "**/dash"`
- Czekanie na stan ładowania:
  - `openclaw browser wait --load networkidle`
- Czekanie na predykat JS:
  - `openclaw browser wait --fn "window.ready===true"`
- Czekanie, aż selektor stanie się widoczny:
  - `openclaw browser wait "#main"`

Można je łączyć:

```bash
openclaw browser wait "#main" \
  --url "**/dash" \
  --load networkidle \
  --fn "window.ready===true" \
  --timeout-ms 15000
```

## Przepływy debugowania

Gdy działanie się nie powiedzie (np. „not visible”, „strict mode violation”, „covered”):

1. `openclaw browser snapshot --interactive`
2. Użyj `click <ref>` / `type <ref>` (preferuj refs roli w trybie interaktywnym)
3. Jeśli nadal się nie powiedzie: `openclaw browser highlight <ref>`, aby zobaczyć, na co wskazuje Playwright
4. Jeśli strona zachowuje się dziwnie:
   - `openclaw browser errors --clear`
   - `openclaw browser requests --filter api --clear`
5. Do głębokiego debugowania: nagraj trace:
   - `openclaw browser trace start`
   - odtwórz problem
   - `openclaw browser trace stop` (wypisuje `TRACE:<path>`)

## Wynik JSON

`--json` służy do skryptów i narzędzi strukturalnych.

Przykłady:

```bash
openclaw browser status --json
openclaw browser snapshot --interactive --json
openclaw browser requests --filter api --json
openclaw browser cookies --json
```

Snapshoty roli w JSON zawierają `refs` oraz mały blok `stats` (lines/chars/refs/interactive), aby narzędzia mogły wnioskować o rozmiarze i gęstości payloadu.

## Przełączniki stanu i środowiska

Są przydatne w przepływach typu „spraw, aby witryna zachowywała się jak X”:

- Cookies: `cookies`, `cookies set`, `cookies clear`
- Storage: `storage local|session get|set|clear`
- Offline: `set offline on|off`
- Headers: `set headers --headers-json '{"X-Debug":"1"}'` (starsze `set headers --json '{"X-Debug":"1"}'` nadal jest obsługiwane)
- Uwierzytelnianie HTTP Basic: `set credentials user pass` (lub `--clear`)
- Geolokalizacja: `set geo <lat> <lon> --origin "https://example.com"` (lub `--clear`)
- Media: `set media dark|light|no-preference|none`
- Strefa czasowa / ustawienia regionalne: `set timezone ...`, `set locale ...`
- Urządzenie / viewport:
  - `set device "iPhone 14"` (ustawienia wstępne urządzeń Playwright)
  - `set viewport 1280 720`

## Bezpieczeństwo i prywatność

- Profil przeglądarki openclaw może zawierać zalogowane sesje; traktuj go jako wrażliwy.
- `browser act kind=evaluate` / `openclaw browser evaluate` oraz `wait --fn`
  wykonują dowolny JavaScript w kontekście strony. Prompt injection może
  na to wpływać. Wyłącz to przez `browser.evaluateEnabled=false`, jeśli tego nie potrzebujesz.
- Informacje o logowaniach i uwagach dotyczących anti-bot (X/Twitter itd.) znajdziesz w [Logowanie przeglądarki + publikowanie na X/Twitter](/pl/tools/browser-login).
- Utrzymuj Gateway/host node jako prywatny (tylko loopback lub tailnet).
- Zdalne punkty końcowe CDP mają duże uprawnienia; tuneluj je i chroń.

Przykład trybu ścisłego (domyślnie blokowanie prywatnych/wewnętrznych miejsc docelowych):

```json5
{
  browser: {
    ssrfPolicy: {
      dangerouslyAllowPrivateNetwork: false,
      hostnameAllowlist: ["*.example.com", "example.com"],
      allowedHostnames: ["localhost"], // opcjonalne dokładne zezwolenie
    },
  },
}
```

## Rozwiązywanie problemów

W przypadku problemów specyficznych dla Linuxa (zwłaszcza snap Chromium) zobacz
[Rozwiązywanie problemów z przeglądarką](/pl/tools/browser-linux-troubleshooting).

W przypadku konfiguracji rozdzielonego hosta WSL2 Gateway + Windows Chrome zobacz
[Rozwiązywanie problemów WSL2 + Windows + zdalny Chrome CDP](/pl/tools/browser-wsl2-windows-remote-cdp-troubleshooting).

### Błąd uruchamiania CDP vs blokada SSRF nawigacji

To są różne klasy błędów i wskazują na różne ścieżki kodu.

- **Błąd uruchamiania lub gotowości CDP** oznacza, że OpenClaw nie może potwierdzić, że płaszczyzna sterowania przeglądarki jest sprawna.
- **Blokada SSRF nawigacji** oznacza, że płaszczyzna sterowania przeglądarki jest sprawna, ale docelowy adres nawigacji strony został odrzucony przez politykę.

Typowe przykłady:

- Błąd uruchamiania lub gotowości CDP:
  - `Chrome CDP websocket for profile "openclaw" is not reachable after start`
  - `Remote CDP for profile "<name>" is not reachable at <cdpUrl>`
- Blokada SSRF nawigacji:
  - `open`, `navigate`, snapshot lub przepływy otwierania kart kończą się błędem polityki przeglądarki/sieci, podczas gdy `start` i `tabs` nadal działają

Użyj tej minimalnej sekwencji, aby rozdzielić oba przypadki:

```bash
openclaw browser --browser-profile openclaw start
openclaw browser --browser-profile openclaw tabs
openclaw browser --browser-profile openclaw open https://example.com
```

Jak odczytywać wyniki:

- Jeśli `start` kończy się błędem `not reachable after start`, najpierw rozwiązuj problem gotowości CDP.
- Jeśli `start` się powiedzie, ale `tabs` zakończy się błędem, płaszczyzna sterowania nadal nie jest sprawna. Traktuj to jako problem osiągalności CDP, a nie problem nawigacji strony.
- Jeśli `start` i `tabs` się powiodą, ale `open` lub `navigate` zakończy się błędem, płaszczyzna sterowania przeglądarki działa, a błąd dotyczy polityki nawigacji lub strony docelowej.
- Jeśli `start`, `tabs` i `open` wszystkie się powiodą, podstawowa ścieżka sterowania zarządzaną przeglądarką jest sprawna.

Ważne szczegóły zachowania:

- Konfiguracja przeglądarki domyślnie używa obiektu polityki SSRF typu fail-closed nawet wtedy, gdy nie skonfigurujesz `browser.ssrfPolicy`.
- Dla lokalnego zarządzanego profilu loopback `openclaw` kontrole stanu CDP celowo pomijają wymuszanie osiągalności SSRF przeglądarki dla własnej lokalnej płaszczyzny sterowania OpenClaw.
- Ochrona nawigacji jest oddzielna. Pomyślny wynik `start` lub `tabs` nie oznacza, że późniejszy cel `open` lub `navigate` jest dozwolony.

Wskazówki dotyczące bezpieczeństwa:

- **Nie** rozluźniaj domyślnej polityki SSRF przeglądarki.
- Preferuj wąskie wyjątki hostów, takie jak `hostnameAllowlist` lub `allowedHostnames`, zamiast szerokiego dostępu do sieci prywatnej.
- Używaj `dangerouslyAllowPrivateNetwork: true` tylko w świadomie zaufanych środowiskach, w których dostęp przeglądarki do sieci prywatnej jest wymagany i sprawdzony.

Przykład: nawigacja zablokowana, płaszczyzna sterowania sprawna

- `start` się powiedzie
- `tabs` się powiedzie
- `open http://internal.example` zakończy się błędem

Zwykle oznacza to, że uruchamianie przeglądarki działa poprawnie, a cel nawigacji wymaga przeglądu polityki.

Przykład: uruchamianie zablokowane, zanim nawigacja zacznie mieć znaczenie

- `start` kończy się błędem `not reachable after start`
- `tabs` również kończy się błędem lub nie może zostać uruchomione

Wskazuje to na uruchamianie przeglądarki lub osiągalność CDP, a nie na problem z listą dozwolonych adresów URL stron.

## Narzędzia agenta + jak działa sterowanie

Agent otrzymuje **jedno narzędzie** do automatyzacji przeglądarki:

- `browser` — status/start/stop/tabs/open/focus/close/snapshot/screenshot/navigate/act

Mapowanie:

- `browser snapshot` zwraca stabilne drzewo interfejsu użytkownika (AI lub ARIA).
- `browser act` używa identyfikatorów `ref` ze snapshotu do klikania/pisania/przeciągania/zaznaczania.
- `browser screenshot` przechwytuje piksele (cała strona lub element).
- `browser` akceptuje:
  - `profile`, aby wybrać nazwany profil przeglądarki (openclaw, chrome lub zdalny CDP).
  - `target` (`sandbox` | `host` | `node`), aby wybrać miejsce, w którym znajduje się przeglądarka.
  - W sesjach sandbox `target: "host"` wymaga `agents.defaults.sandbox.browser.allowHostControl=true`.
  - Jeśli `target` zostanie pominięty: sesje sandbox domyślnie używają `sandbox`, a sesje bez sandbox domyślnie używają `host`.
  - Jeśli podłączony jest node z obsługą przeglądarki, narzędzie może automatycznie kierować do niego żądania, chyba że przypniesz `target="host"` lub `target="node"`.

Dzięki temu agent pozostaje deterministyczny i unika kruchych selektorów.

## Powiązane

- [Przegląd narzędzi](/pl/tools) — wszystkie dostępne narzędzia agenta
- [Sandboxing](/pl/gateway/sandboxing) — sterowanie przeglądarką w środowiskach sandbox
- [Bezpieczeństwo](/pl/gateway/security) — zagrożenia związane ze sterowaniem przeglądarką i utwardzanie
