---
read_when:
    - Gateway sürecini çalıştırırken veya hata ayıklarken
summary: Gateway hizmeti, yaşam döngüsü ve operasyonları için runbook
title: Gateway Runbook
x-i18n:
    generated_at: "2026-04-07T08:45:11Z"
    model: gpt-5.4
    provider: openai
    source_hash: fd2c21036e88612861ef2195b8ff7205aca31386bb11558614ade8d1a54fdebd
    source_path: gateway/index.md
    workflow: 15
---

# Gateway runbook

Gateway hizmetinin ilk gün başlatılması ve sonraki operasyonları için bu sayfayı kullanın.

<CardGroup cols={2}>
  <Card title="Derin sorun giderme" icon="siren" href="/tr/gateway/troubleshooting">
    Belirti odaklı tanılama; tam komut sıraları ve log imzalarıyla.
  </Card>
  <Card title="Yapılandırma" icon="sliders" href="/tr/gateway/configuration">
    Görev odaklı kurulum kılavuzu + tam yapılandırma referansı.
  </Card>
  <Card title="Secrets yönetimi" icon="key-round" href="/tr/gateway/secrets">
    SecretRef sözleşmesi, çalışma zamanı snapshot davranışı ve migrate/reload işlemleri.
  </Card>
  <Card title="Secrets plan sözleşmesi" icon="shield-check" href="/tr/gateway/secrets-plan-contract">
    Tam `secrets apply` hedef/yol kuralları ve yalnızca ref kullanan auth-profile davranışı.
  </Card>
</CardGroup>

## 5 dakikalık yerel başlangıç

<Steps>
  <Step title="Gateway'i başlat">

```bash
openclaw gateway --port 18789
# debug/trace stdio'ya yansıtılır
openclaw gateway --port 18789 --verbose
# seçilen porttaki dinleyiciyi zorla sonlandır, sonra başlat
openclaw gateway --force
```

  </Step>

  <Step title="Hizmet sağlığını doğrula">

```bash
openclaw gateway status
openclaw status
openclaw logs --follow
```

Sağlıklı temel durum: `Runtime: running` ve `RPC probe: ok`.

  </Step>

  <Step title="Kanal hazır oluşunu doğrula">

```bash
openclaw channels status --probe
```

Erişilebilir bir gateway ile bu, hesap başına canlı kanal problarını ve isteğe bağlı denetimleri çalıştırır.
Gateway'e ulaşılamazsa, CLI canlı prob çıktısı yerine yalnızca yapılandırma tabanlı kanal özetlerine geri düşer.

  </Step>
</Steps>

<Note>
Gateway config reload, etkin config dosyası yolunu izler (profil/durum varsayılanlarından çözülür veya ayarlanmışsa `OPENCLAW_CONFIG_PATH` kullanılır).
Varsayılan mod `gateway.reload.mode="hybrid"` şeklindedir.
İlk başarılı yüklemeden sonra çalışan süreç, etkin bellek içi config snapshot'unu sunar; başarılı bir reload bu snapshot'u atomik olarak değiştirir.
</Note>

## Çalışma zamanı modeli

- Yönlendirme, kontrol düzlemi ve kanal bağlantıları için sürekli çalışan tek bir süreç.
- Şunlar için tek, çoklamalı port:
  - WebSocket kontrol/RPC
  - HTTP API'leri, OpenAI uyumlu (`/v1/models`, `/v1/embeddings`, `/v1/chat/completions`, `/v1/responses`, `/tools/invoke`)
  - Control UI ve hook'lar
- Varsayılan bind modu: `loopback`.
- Varsayılan olarak auth gereklidir. Ortak gizli anahtar kullanan kurulumlar
  `gateway.auth.token` / `gateway.auth.password` (veya
  `OPENCLAW_GATEWAY_TOKEN` / `OPENCLAW_GATEWAY_PASSWORD`) kullanır; loopback olmayan
  reverse-proxy kurulumları ise `gateway.auth.mode: "trusted-proxy"` kullanabilir.

## OpenAI uyumlu uç noktalar

OpenClaw'un en yüksek etkili uyumluluk yüzeyi artık şudur:

- `GET /v1/models`
- `GET /v1/models/{id}`
- `POST /v1/embeddings`
- `POST /v1/chat/completions`
- `POST /v1/responses`

Bu kümenin önemli olma nedeni:

- Çoğu Open WebUI, LobeChat ve LibreChat entegrasyonu önce `/v1/models` yolunu prob eder.
- Birçok RAG ve bellek pipeline'ı `/v1/embeddings` bekler.
- Aracı odaklı istemciler giderek daha fazla `/v1/responses` tercih ediyor.

Planlama notu:

- `/v1/models` önce aracı yaklaşımını benimser: `openclaw`, `openclaw/default` ve `openclaw/<agentId>` döndürür.
- `openclaw/default`, yapılandırılmış varsayılan aracıya her zaman eşlenen kararlı takma addır.
- Bir backend sağlayıcı/model geçersiz kılması istediğinizde `x-openclaw-model` kullanın; aksi takdirde seçili aracının normal model ve embedding kurulumu kontrolü elinde tutar.

Bunların tümü ana Gateway portunda çalışır ve Gateway HTTP API'sinin geri kalanıyla aynı güvenilir operatör auth sınırını kullanır.

### Port ve bind önceliği

| Ayar         | Çözümleme sırası                                              |
| ------------ | ------------------------------------------------------------- |
| Gateway port | `--port` → `OPENCLAW_GATEWAY_PORT` → `gateway.port` → `18789` |
| Bind modu    | CLI/override → `gateway.bind` → `loopback`                    |

### Hot reload modları

| `gateway.reload.mode` | Davranış                                 |
| --------------------- | ---------------------------------------- |
| `off`                 | Config reload yok                        |
| `hot`                 | Yalnızca hot-safe değişiklikleri uygula  |
| `restart`             | Reload gerektiren değişikliklerde yeniden başlat |
| `hybrid` (varsayılan) | Güvenliyse hot-apply, gerekliyse yeniden başlat |

## Operatör komut kümesi

```bash
openclaw gateway status
openclaw gateway status --deep   # sistem düzeyinde hizmet taraması ekler
openclaw gateway status --json
openclaw gateway install
openclaw gateway restart
openclaw gateway stop
openclaw secrets reload
openclaw logs --follow
openclaw doctor
```

`gateway status --deep`, daha derin bir RPC sağlık probu için değil, ek hizmet keşfi (LaunchDaemons/systemd system
birimleri/schtasks) içindir.

## Birden fazla gateway (aynı host)

Çoğu kurulum makine başına tek bir gateway çalıştırmalıdır. Tek bir gateway birden çok
aracı ve kanalı barındırabilir.

Yalnızca özellikle yalıtım veya bir kurtarma botu istediğinizde birden fazla gateway gerekir.

Yararlı kontroller:

```bash
openclaw gateway status --deep
openclaw gateway probe
```

Beklenmesi gerekenler:

- `gateway status --deep`, `Other gateway-like services detected (best effort)`
  bildirebilir ve eski launchd/systemd/schtasks kurulumları hâlâ ortadaysa
  temizleme ipuçları yazdırabilir.
- `gateway probe`, birden fazla hedef yanıt verdiğinde `multiple reachable gateways`
  uyarısı verebilir.
- Bu kasıtlıysa, gateway başına portları, config/state alanlarını ve workspace köklerini ayırın.

Ayrıntılı kurulum: [/gateway/multiple-gateways](/tr/gateway/multiple-gateways).

## Uzak erişim

Tercih edilen: Tailscale/VPN.
Yedek: SSH tüneli.

```bash
ssh -N -L 18789:127.0.0.1:18789 user@host
```

Ardından istemcileri yerelde `ws://127.0.0.1:18789` adresine bağlayın.

<Warning>
SSH tünelleri gateway auth'ı atlatmaz. Ortak gizli anahtar auth'ı için istemciler,
tünel üzerinden bile olsa yine `token`/`password` göndermelidir. Kimlik taşıyan modlarda,
istek yine de o auth yolunu karşılamak zorundadır.
</Warning>

Bkz.: [Uzak Gateway](/tr/gateway/remote), [Kimlik Doğrulama](/tr/gateway/authentication), [Tailscale](/tr/gateway/tailscale).

## Denetim ve hizmet yaşam döngüsü

Üretime benzer güvenilirlik için denetimli çalıştırmalar kullanın.

<Tabs>
  <Tab title="macOS (launchd)">

```bash
openclaw gateway install
openclaw gateway status
openclaw gateway restart
openclaw gateway stop
```

LaunchAgent etiketleri `ai.openclaw.gateway` (varsayılan) veya `ai.openclaw.<profile>` (adlandırılmış profil) şeklindedir. `openclaw doctor`, hizmet config kaymasını denetler ve onarır.

  </Tab>

  <Tab title="Linux (systemd user)">

```bash
openclaw gateway install
systemctl --user enable --now openclaw-gateway[-<profile>].service
openclaw gateway status
```

Çıkış yaptıktan sonra kalıcılık için lingering'ı etkinleştirin:

```bash
sudo loginctl enable-linger <user>
```

Özel bir kurulum yolu gerektiğinde elle user-unit örneği:

```ini
[Unit]
Description=OpenClaw Gateway
After=network-online.target
Wants=network-online.target

[Service]
ExecStart=/usr/local/bin/openclaw gateway --port 18789
Restart=always
RestartSec=5
TimeoutStopSec=30
TimeoutStartSec=30
SuccessExitStatus=0 143
KillMode=control-group

[Install]
WantedBy=default.target
```

  </Tab>

  <Tab title="Windows (native)">

```powershell
openclaw gateway install
openclaw gateway status --json
openclaw gateway restart
openclaw gateway stop
```

Yerel Windows yönetilen başlangıcı, `OpenClaw Gateway`
(adlandırılmış profiller için `OpenClaw Gateway (<profile>)`) adlı bir Scheduled Task kullanır. Scheduled Task
oluşturulması reddedilirse, OpenClaw durum dizini içindeki `gateway.cmd` dosyasına işaret eden
kullanıcı başına Startup-folder başlatıcısına geri düşer.

  </Tab>

  <Tab title="Linux (system service)">

Çok kullanıcılı/sürekli açık host'lar için bir system unit kullanın.

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now openclaw-gateway[-<profile>].service
```

User unit ile aynı hizmet gövdesini kullanın, ancak bunu
`/etc/systemd/system/openclaw-gateway[-<profile>].service` altına kurun ve
`openclaw` binary'niz başka bir yerdeyse `ExecStart=` değerini ayarlayın.

  </Tab>
</Tabs>

## Tek host üzerinde birden fazla gateway

Çoğu kurulum **tek** Gateway çalıştırmalıdır.
Birden fazlasını yalnızca katı yalıtım/yedeklilik için kullanın (örneğin bir kurtarma profili).

Örnek başına kontrol listesi:

- Benzersiz `gateway.port`
- Benzersiz `OPENCLAW_CONFIG_PATH`
- Benzersiz `OPENCLAW_STATE_DIR`
- Benzersiz `agents.defaults.workspace`

Örnek:

```bash
OPENCLAW_CONFIG_PATH=~/.openclaw/a.json OPENCLAW_STATE_DIR=~/.openclaw-a openclaw gateway --port 19001
OPENCLAW_CONFIG_PATH=~/.openclaw/b.json OPENCLAW_STATE_DIR=~/.openclaw-b openclaw gateway --port 19002
```

Bkz.: [Birden fazla gateway](/tr/gateway/multiple-gateways).

### Geliştirme profili hızlı yol

```bash
openclaw --dev setup
openclaw --dev gateway --allow-unconfigured
openclaw --dev status
```

Varsayılanlar yalıtılmış state/config ve temel gateway portu `19001` içerir.

## Protokol hızlı başvuru (operatör görünümü)

- İlk istemci çerçevesi `connect` olmalıdır.
- Gateway `hello-ok` snapshot'u döndürür (`presence`, `health`, `stateVersion`, `uptimeMs`, limits/policy).
- `hello-ok.features.methods` / `events`, çağrılabilir her yardımcı rota için üretilmiş bir döküm değil,
  temkinli bir keşif listesidir.
- İstekler: `req(method, params)` → `res(ok/payload|error)`.
- Yaygın olaylar arasında `connect.challenge`, `agent`, `chat`,
  `session.message`, `session.tool`, `sessions.changed`, `presence`, `tick`,
  `health`, `heartbeat`, eşleştirme/onay yaşam döngüsü olayları ve `shutdown` bulunur.

Aracı çalıştırmaları iki aşamalıdır:

1. Anında kabul onayı (`status:"accepted"`)
2. Arada akış hâlindeki `agent` olaylarıyla son tamamlama yanıtı (`status:"ok"|"error"`).

Tam protokol belgeleri: [Gateway Protocol](/tr/gateway/protocol).

## Operasyonel kontroller

### Liveness

- WS açın ve `connect` gönderin.
- Snapshot içeren `hello-ok` yanıtını bekleyin.

### Readiness

```bash
openclaw gateway status
openclaw channels status --probe
openclaw health
```

### Gap recovery

Olaylar yeniden oynatılmaz. Sıra boşluklarında, devam etmeden önce durumu yenileyin (`health`, `system-presence`).

## Yaygın hata imzaları

| İmza                                                           | Olası sorun                                                                     |
| -------------------------------------------------------------- | ------------------------------------------------------------------------------- |
| `refusing to bind gateway ... without auth`                    | Geçerli bir gateway auth yolu olmadan loopback olmayan bind                     |
| `another gateway instance is already listening` / `EADDRINUSE` | Port çakışması                                                                  |
| `Gateway start blocked: set gateway.mode=local`                | Config uzak moda ayarlı veya hasarlı bir config içinde local-mode damgası eksik |
| `unauthorized` during connect                                  | İstemci ile gateway arasında auth uyumsuzluğu                                   |

Tam tanılama sıraları için [Gateway Troubleshooting](/tr/gateway/troubleshooting) kullanın.

## Güvenlik garantileri

- Gateway protokol istemcileri, Gateway kullanılamadığında hızlı başarısız olur (örtük doğrudan kanal yedeğine düşme yok).
- Geçersiz/`connect` olmayan ilk çerçeveler reddedilir ve bağlantı kapatılır.
- Zarif kapatma, soket kapanmadan önce `shutdown` olayı gönderir.

---

İlgili:

- [Sorun Giderme](/tr/gateway/troubleshooting)
- [Arka Plan Süreci](/tr/gateway/background-process)
- [Yapılandırma](/tr/gateway/configuration)
- [Health](/tr/gateway/health)
- [Doctor](/tr/gateway/doctor)
- [Kimlik Doğrulama](/tr/gateway/authentication)
