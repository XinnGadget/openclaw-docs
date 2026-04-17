---
read_when:
    - Chcesz uruchomić Gateway na serwerze Linux lub w chmurze VPS
    - Potrzebujesz szybkiego przeglądu przewodników hostingowych
    - Chcesz ogólnego dostrajania serwera Linux dla OpenClaw
sidebarTitle: Linux Server
summary: Uruchom OpenClaw na serwerze Linux lub w chmurze VPS — wybór dostawcy, architektura i dostrajanie
title: Serwer Linux
x-i18n:
    generated_at: "2026-04-14T02:08:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: e623f4c770132e01628d66bfb8cd273bbef6dad633b812496c90da5e3e0f1383
    source_path: vps.md
    workflow: 15
---

# Serwer Linux

Uruchom Gateway OpenClaw na dowolnym serwerze Linux lub w chmurze VPS. Ta strona pomaga
wybrać dostawcę, wyjaśnia, jak działają wdrożenia w chmurze, i omawia ogólne
dostrajanie Linuxa, które sprawdza się wszędzie.

## Wybierz dostawcę

<CardGroup cols={2}>
  <Card title="Railway" href="/pl/install/railway">Konfiguracja jednym kliknięciem w przeglądarce</Card>
  <Card title="Northflank" href="/pl/install/northflank">Konfiguracja jednym kliknięciem w przeglądarce</Card>
  <Card title="DigitalOcean" href="/pl/install/digitalocean">Prosty płatny VPS</Card>
  <Card title="Oracle Cloud" href="/pl/install/oracle">darmowa warstwa ARM Always Free</Card>
  <Card title="Fly.io" href="/pl/install/fly">Fly Machines</Card>
  <Card title="Hetzner" href="/pl/install/hetzner">Docker na VPS Hetzner</Card>
  <Card title="Hostinger" href="/pl/install/hostinger">VPS z konfiguracją jednym kliknięciem</Card>
  <Card title="GCP" href="/pl/install/gcp">Compute Engine</Card>
  <Card title="Azure" href="/pl/install/azure">Maszyna wirtualna z Linuxem</Card>
  <Card title="exe.dev" href="/pl/install/exe-dev">Maszyna wirtualna z proxy HTTPS</Card>
  <Card title="Raspberry Pi" href="/pl/install/raspberry-pi">Samodzielny hosting ARM</Card>
</CardGroup>

**AWS (EC2 / Lightsail / warstwa bezpłatna)** również sprawdza się bardzo dobrze.
Społecznościowy przewodnik wideo jest dostępny pod adresem
[x.com/techfrenAJ/status/2014934471095812547](https://x.com/techfrenAJ/status/2014934471095812547)
(zasób społecznościowy — może przestać być dostępny).

## Jak działają konfiguracje chmurowe

- **Gateway działa na VPS** i przechowuje stan oraz workspace.
- Łączysz się ze swojego laptopa lub telefonu przez **Control UI** albo **Tailscale/SSH**.
- Traktuj VPS jako źródło prawdy i regularnie twórz **kopie zapasowe** stanu oraz workspace.
- Bezpieczne ustawienie domyślne: utrzymuj Gateway na local loopback i uzyskuj do niego dostęp przez tunel SSH albo Tailscale Serve.
  Jeśli powiążesz go z `lan` lub `tailnet`, wymagaj `gateway.auth.token` albo `gateway.auth.password`.

Powiązane strony: [Zdalny dostęp do Gateway](/pl/gateway/remote), [Centrum platform](/pl/platforms).

## Wspólny agent firmowy na VPS

Uruchomienie jednego agenta dla zespołu to poprawna konfiguracja, jeśli każdy użytkownik znajduje się w tej samej granicy zaufania, a agent służy wyłącznie do celów biznesowych.

- Utrzymuj go w dedykowanym środowisku uruchomieniowym (VPS/VM/kontener + dedykowany użytkownik systemu/konta).
- Nie loguj tego środowiska do osobistych kont Apple/Google ani osobistych profili przeglądarki/menedżera haseł.
- Jeśli użytkownicy są wobec siebie potencjalnie wrodzy, rozdziel ich według gateway/hosta/użytkownika systemu.

Szczegóły modelu bezpieczeństwa: [Bezpieczeństwo](/pl/gateway/security).

## Korzystanie z Node na VPS

Możesz trzymać Gateway w chmurze i sparować **Node** na swoich lokalnych urządzeniach
(Mac/iOS/Android/headless). Node zapewniają lokalne możliwości ekranu/kamery/canvas oraz `system.run`,
podczas gdy Gateway pozostaje w chmurze.

Dokumentacja: [Node](/pl/nodes), [CLI Node](/cli/nodes).

## Dostrajanie uruchamiania dla małych VM i hostów ARM

Jeśli polecenia CLI działają wolno na słabszych VM (lub hostach ARM), włącz cache kompilacji modułów Node:

```bash
grep -q 'NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache' ~/.bashrc || cat >> ~/.bashrc <<'EOF'
export NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
mkdir -p /var/tmp/openclaw-compile-cache
export OPENCLAW_NO_RESPAWN=1
EOF
source ~/.bashrc
```

- `NODE_COMPILE_CACHE` przyspiesza uruchamianie powtarzanych poleceń.
- `OPENCLAW_NO_RESPAWN=1` pozwala uniknąć dodatkowego narzutu startowego związanego ze ścieżką samoczynnego ponownego uruchamiania.
- Pierwsze uruchomienie polecenia rozgrzewa cache; kolejne uruchomienia są szybsze.
- Szczegóły dotyczące Raspberry Pi znajdziesz w sekcji [Raspberry Pi](/pl/install/raspberry-pi).

### Lista kontrolna dostrajania systemd (opcjonalnie)

W przypadku hostów VM używających `systemd` rozważ:

- Dodanie zmiennych środowiskowych usługi dla stabilnej ścieżki uruchamiania:
  - `OPENCLAW_NO_RESPAWN=1`
  - `NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache`
- Jawne ustawienie zachowania przy ponownym uruchamianiu:
  - `Restart=always`
  - `RestartSec=2`
  - `TimeoutStartSec=90`
- Preferowanie dysków opartych na SSD dla ścieżek stanu/cache, aby ograniczyć kary zimnego startu wynikające z losowych operacji wejścia/wyjścia.

W przypadku standardowej ścieżki `openclaw onboard --install-daemon` edytuj jednostkę użytkownika:

```bash
systemctl --user edit openclaw-gateway.service
```

```ini
[Service]
Environment=OPENCLAW_NO_RESPAWN=1
Environment=NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache
Restart=always
RestartSec=2
TimeoutStartSec=90
```

Jeśli celowo zainstalowano zamiast tego jednostkę systemową, edytuj
`openclaw-gateway.service` za pomocą `sudo systemctl edit openclaw-gateway.service`.

Jak zasady `Restart=` pomagają w automatycznym odzyskiwaniu usług:
[systemd może automatyzować odzyskiwanie usług](https://www.redhat.com/en/blog/systemd-automate-recovery).
