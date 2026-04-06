---
read_when:
    - Yerel kurulumlar yerine container tabanlı bir gateway istiyorsunuz
    - Docker akışını doğruluyorsunuz
summary: OpenClaw için isteğe bağlı Docker tabanlı kurulum ve onboarding
title: Docker
x-i18n:
    generated_at: "2026-04-06T03:08:43Z"
    model: gpt-5.4
    provider: openai
    source_hash: d6aa0453340d7683b4954316274ba6dd1aa7c0ce2483e9bd8ae137ff4efd4c3c
    source_path: install/docker.md
    workflow: 15
---

# Docker (isteğe bağlı)

Docker **isteğe bağlıdır**. Yalnızca container tabanlı bir gateway istiyorsanız veya Docker akışını doğrulamak istiyorsanız kullanın.

## Docker benim için uygun mu?

- **Evet**: yalıtılmış, geçici bir gateway ortamı istiyorsunuz veya OpenClaw'ı yerel kurulum olmayan bir ana bilgisayarda çalıştırmak istiyorsunuz.
- **Hayır**: kendi makinenizde çalışıyorsunuz ve yalnızca en hızlı geliştirme döngüsünü istiyorsunuz. Bunun yerine normal kurulum akışını kullanın.
- **Sandbox notu**: ajan sandboxing de Docker kullanır, ancak bunun için tam gateway'in Docker içinde çalışması **gerekmez**. Bkz. [Sandboxing](/tr/gateway/sandboxing).

## Ön koşullar

- Docker Desktop (veya Docker Engine) + Docker Compose v2
- Görüntü oluşturma için en az 2 GB RAM (`pnpm install`, 1 GB ana bilgisayarlarda 137 çıkış koduyla OOM nedeniyle öldürülebilir)
- İmajlar ve günlükler için yeterli disk alanı
- VPS/genel ana bilgisayarda çalıştırıyorsanız
  [Ağ erişimi için güvenlik sağlamlaştırması](/tr/gateway/security) bölümünü,
  özellikle Docker `DOCKER-USER` güvenlik duvarı ilkesini inceleyin.

## Container tabanlı Gateway

<Steps>
  <Step title="İmajı oluşturun">
    Depo kök dizininden kurulum betiğini çalıştırın:

    ```bash
    ./scripts/docker/setup.sh
    ```

    Bu, gateway imajını yerelde oluşturur. Bunun yerine önceden oluşturulmuş bir imaj kullanmak için:

    ```bash
    export OPENCLAW_IMAGE="ghcr.io/openclaw/openclaw:latest"
    ./scripts/docker/setup.sh
    ```

    Önceden oluşturulmuş imajlar
    [GitHub Container Registry](https://github.com/openclaw/openclaw/pkgs/container/openclaw) üzerinde yayımlanır.
    Yaygın etiketler: `main`, `latest`, `<version>` (ör. `2026.2.26`).

  </Step>

  <Step title="Onboarding'i tamamlayın">
    Kurulum betiği onboarding'i otomatik olarak çalıştırır. Şunları yapar:

    - sağlayıcı API anahtarlarını sorar
    - bir gateway token'ı oluşturur ve bunu `.env` dosyasına yazar
    - gateway'i Docker Compose üzerinden başlatır

    Kurulum sırasında, başlangıç öncesi onboarding ve yapılandırma yazmaları
    doğrudan `openclaw-gateway` üzerinden çalışır. `openclaw-cli`, yalnızca
    gateway container'ı zaten var olduktan sonra çalıştırdığınız komutlar içindir.

  </Step>

  <Step title="Control UI'ı açın">
    Tarayıcınızda `http://127.0.0.1:18789/` adresini açın ve yapılandırılmış
    paylaşılan gizli anahtarı Ayarlar'a yapıştırın. Kurulum betiği varsayılan
    olarak `.env` dosyasına bir token yazar; container yapılandırmasını parola
    kimlik doğrulamasına geçirirseniz bunun yerine o parolayı kullanın.

    URL'ye tekrar mı ihtiyacınız var?

    ```bash
    docker compose run --rm openclaw-cli dashboard --no-open
    ```

  </Step>

  <Step title="Kanalları yapılandırın (isteğe bağlı)">
    Mesajlaşma kanalları eklemek için CLI container'ını kullanın:

    ```bash
    # WhatsApp (QR)
    docker compose run --rm openclaw-cli channels login

    # Telegram
    docker compose run --rm openclaw-cli channels add --channel telegram --token "<token>"

    # Discord
    docker compose run --rm openclaw-cli channels add --channel discord --token "<token>"
    ```

    Belgeler: [WhatsApp](/tr/channels/whatsapp), [Telegram](/tr/channels/telegram), [Discord](/tr/channels/discord)

  </Step>
</Steps>

### El ile akış

Kurulum betiğini kullanmak yerine her adımı kendiniz çalıştırmayı tercih ederseniz:

```bash
docker build -t openclaw:local -f Dockerfile .
docker compose run --rm --no-deps --entrypoint node openclaw-gateway \
  dist/index.js onboard --mode local --no-install-daemon
docker compose run --rm --no-deps --entrypoint node openclaw-gateway \
  dist/index.js config set --batch-json '[{"path":"gateway.mode","value":"local"},{"path":"gateway.bind","value":"lan"},{"path":"gateway.controlUi.allowedOrigins","value":["http://localhost:18789","http://127.0.0.1:18789"]}]'
docker compose up -d openclaw-gateway
```

<Note>
`docker compose` komutunu depo kök dizininden çalıştırın. `OPENCLAW_EXTRA_MOUNTS`
veya `OPENCLAW_HOME_VOLUME` etkinleştirdiyseniz kurulum betiği `docker-compose.extra.yml`
dosyasını yazar; bunu `-f docker-compose.yml -f docker-compose.extra.yml` ile ekleyin.
</Note>

<Note>
`openclaw-cli`, `openclaw-gateway` ile aynı ağ ad alanını paylaştığı için
başlatma sonrası bir araçtır. `docker compose up -d openclaw-gateway` öncesinde onboarding
ve kurulum zamanı yapılandırma yazmalarını `openclaw-gateway` üzerinden
`--no-deps --entrypoint node` ile çalıştırın.
</Note>

### Ortam değişkenleri

Kurulum betiği şu isteğe bağlı ortam değişkenlerini kabul eder:

| Değişken                      | Amaç                                                             |
| ----------------------------- | ---------------------------------------------------------------- |
| `OPENCLAW_IMAGE`              | Yerelde oluşturmak yerine uzak bir imaj kullan                   |
| `OPENCLAW_DOCKER_APT_PACKAGES` | Derleme sırasında ek apt paketleri kur                           |
| `OPENCLAW_EXTENSIONS`         | Eklenti bağımlılıklarını derleme zamanında önceden kur (boşlukla ayrılmış adlar) |
| `OPENCLAW_EXTRA_MOUNTS`       | Ek ana bilgisayar bind mount'ları (virgülle ayrılmış `source:target[:opts]`) |
| `OPENCLAW_HOME_VOLUME`        | `/home/node` dizinini adlandırılmış bir Docker volume içinde kalıcı hale getir |
| `OPENCLAW_SANDBOX`            | Sandbox bootstrap kullanımını etkinleştir (`1`, `true`, `yes`, `on`) |
| `OPENCLAW_DOCKER_SOCKET`      | Docker socket yolunu geçersiz kıl                               |

### Sağlık denetimleri

Container probe uç noktaları (kimlik doğrulama gerekmez):

```bash
curl -fsS http://127.0.0.1:18789/healthz   # liveness
curl -fsS http://127.0.0.1:18789/readyz     # readiness
```

Docker imajı, `/healthz` uç noktasına ping atan yerleşik bir `HEALTHCHECK` içerir.
Denetimler sürekli başarısız olursa Docker container'ı `unhealthy` olarak işaretler ve
orkestrasyon sistemleri onu yeniden başlatabilir veya değiştirebilir.

Kimliği doğrulanmış ayrıntılı sağlık anlık görüntüsü:

```bash
docker compose exec openclaw-gateway node dist/index.js health --token "$OPENCLAW_GATEWAY_TOKEN"
```

### LAN ve loopback karşılaştırması

`scripts/docker/setup.sh`, Docker port yayımlama ile ana bilgisayardan
`http://127.0.0.1:18789` erişiminin çalışması için varsayılan olarak `OPENCLAW_GATEWAY_BIND=lan` kullanır.

- `lan` (varsayılan): ana bilgisayar tarayıcısı ve ana bilgisayar CLI, yayımlanan gateway portuna erişebilir.
- `loopback`: yalnızca container ağ ad alanı içindeki süreçler
  doğrudan gateway'e erişebilir.

<Note>
`gateway.bind` içinde bind modu değerlerini (`lan` / `loopback` / `custom` /
`tailnet` / `auto`) kullanın; `0.0.0.0` veya `127.0.0.1` gibi ana bilgisayar diğer adlarını kullanmayın.
</Note>

### Depolama ve kalıcılık

Docker Compose, `OPENCLAW_CONFIG_DIR` dizinini `/home/node/.openclaw` yoluna ve
`OPENCLAW_WORKSPACE_DIR` dizinini `/home/node/.openclaw/workspace` yoluna bind-mount eder; böylece bu yollar
container değiştirildiğinde korunur.

Bu bağlanan yapılandırma dizini, OpenClaw'ın şunları tuttuğu yerdir:

- davranış yapılandırması için `openclaw.json`
- depolanan sağlayıcı OAuth/API anahtarı kimlik doğrulaması için `agents/<agentId>/agent/auth-profiles.json`
- `OPENCLAW_GATEWAY_TOKEN` gibi ortam destekli çalışma zamanı gizli anahtarları için `.env`

VM dağıtımlarındaki tam kalıcılık ayrıntıları için bkz.
[Docker VM Runtime - Ne nerede kalıcı olur](/tr/install/docker-vm-runtime#what-persists-where).

**Disk büyüme sıcak noktaları:** `/tmp/openclaw/` altındaki `media/`, oturum JSONL dosyaları, `cron/runs/*.jsonl`
ve dönen dosya günlüklerini izleyin.

### Shell yardımcıları (isteğe bağlı)

Günlük Docker yönetimini kolaylaştırmak için `ClawDock` yükleyin:

```bash
mkdir -p ~/.clawdock && curl -sL https://raw.githubusercontent.com/openclaw/openclaw/main/scripts/clawdock/clawdock-helpers.sh -o ~/.clawdock/clawdock-helpers.sh
echo 'source ~/.clawdock/clawdock-helpers.sh' >> ~/.zshrc && source ~/.zshrc
```

ClawDock'ı eski `scripts/shell-helpers/clawdock-helpers.sh` ham yolundan yüklediyseniz, yerel yardımcı dosyanızın yeni konumu izlemesi için yukarıdaki yükleme komutunu yeniden çalıştırın.

Ardından `clawdock-start`, `clawdock-stop`, `clawdock-dashboard` vb. kullanın.
Tüm komutlar için `clawdock-help` çalıştırın.
Tam yardımcı kılavuzu için bkz. [ClawDock](/tr/install/clawdock).

<AccordionGroup>
  <Accordion title="Docker gateway için ajan sandbox'ı etkinleştir">
    ```bash
    export OPENCLAW_SANDBOX=1
    ./scripts/docker/setup.sh
    ```

    Özel socket yolu (ör. rootless Docker):

    ```bash
    export OPENCLAW_SANDBOX=1
    export OPENCLAW_DOCKER_SOCKET=/run/user/1000/docker.sock
    ./scripts/docker/setup.sh
    ```

    Betik, yalnızca sandbox ön koşulları geçtikten sonra `docker.sock` mount eder. Eğer
    sandbox kurulumu tamamlanamazsa betik `agents.defaults.sandbox.mode`
    değerini `off` olarak sıfırlar.

  </Accordion>

  <Accordion title="Otomasyon / CI (etkileşimsiz)">
    `-T` ile Compose pseudo-TTY tahsisini devre dışı bırakın:

    ```bash
    docker compose run -T --rm openclaw-cli gateway probe
    docker compose run -T --rm openclaw-cli devices list --json
    ```

  </Accordion>

  <Accordion title="Paylaşılan ağ güvenlik notu">
    `openclaw-cli`, CLI
    komutlarının gateway'e `127.0.0.1` üzerinden ulaşabilmesi için `network_mode: "service:openclaw-gateway"` kullanır. Bunu paylaşılan
    bir güven sınırı olarak değerlendirin. Compose yapılandırması `NET_RAW`/`NET_ADMIN` yetkilerini kaldırır ve
    `openclaw-cli` üzerinde `no-new-privileges` etkinleştirir.
  </Accordion>

  <Accordion title="İzinler ve EACCES">
    İmaj `node` (uid 1000) kullanıcısıyla çalışır. Eğer
    `/home/node/.openclaw` üzerinde izin hataları görüyorsanız, ana bilgisayar bind mount'larınızın uid 1000'e ait olduğundan emin olun:

    ```bash
    sudo chown -R 1000:1000 /path/to/openclaw-config /path/to/openclaw-workspace
    ```

  </Accordion>

  <Accordion title="Daha hızlı yeniden derlemeler">
    Dockerfile'ınızı bağımlılık katmanları önbelleğe alınacak şekilde sıralayın. Bu,
    lockfile'lar değişmediği sürece `pnpm install` komutunun yeniden çalıştırılmasını önler:

    ```dockerfile
    FROM node:24-bookworm
    RUN curl -fsSL https://bun.sh/install | bash
    ENV PATH="/root/.bun/bin:${PATH}"
    RUN corepack enable
    WORKDIR /app
    COPY package.json pnpm-lock.yaml pnpm-workspace.yaml .npmrc ./
    COPY ui/package.json ./ui/package.json
    COPY scripts ./scripts
    RUN pnpm install --frozen-lockfile
    COPY . .
    RUN pnpm build
    RUN pnpm ui:install
    RUN pnpm ui:build
    ENV NODE_ENV=production
    CMD ["node","dist/index.js"]
    ```

  </Accordion>

  <Accordion title="İleri düzey kullanıcılar için container seçenekleri">
    Varsayılan imaj güvenlik önceliklidir ve root olmayan `node` kullanıcısıyla çalışır. Daha
    tam özellikli bir container için:

    1. **`/home/node` dizinini kalıcı hale getirin**: `export OPENCLAW_HOME_VOLUME="openclaw_home"`
    2. **Sistem bağımlılıklarını imaja ekleyin**: `export OPENCLAW_DOCKER_APT_PACKAGES="git curl jq"`
    3. **Playwright tarayıcılarını yükleyin**:
       ```bash
       docker compose run --rm openclaw-cli \
         node /app/node_modules/playwright-core/cli.js install chromium
       ```
    4. **Tarayıcı indirmelerini kalıcı hale getirin**: şunu ayarlayın:
       `PLAYWRIGHT_BROWSERS_PATH=/home/node/.cache/ms-playwright` ve
       `OPENCLAW_HOME_VOLUME` veya `OPENCLAW_EXTRA_MOUNTS` kullanın.

  </Accordion>

  <Accordion title="OpenAI Codex OAuth (headless Docker)">
    Sihirbazda OpenAI Codex OAuth seçerseniz bir tarayıcı URL'si açılır. Docker
    veya headless kurulumlarda, ulaştığınız tam yönlendirme URL'sini kopyalayın ve
    kimlik doğrulamayı tamamlamak için bunu sihirbaza geri yapıştırın.
  </Accordion>

  <Accordion title="Temel imaj meta verileri">
    Ana Docker imajı `node:24-bookworm` kullanır ve
    `org.opencontainers.image.base.name`,
    `org.opencontainers.image.source` ve diğerleri dahil OCI temel imaj
    açıklamalarını yayımlar. Bkz.
    [OCI imaj açıklamaları](https://github.com/opencontainers/image-spec/blob/main/annotations.md).
  </Accordion>
</AccordionGroup>

### VPS üzerinde mi çalıştırıyorsunuz?

İkili dosya gömme, kalıcılık ve güncellemeler dahil
paylaşılan VM dağıtım adımları için bkz. [Hetzner (Docker VPS)](/tr/install/hetzner) ve
[Docker VM Runtime](/tr/install/docker-vm-runtime).

## Agent Sandbox

`agents.defaults.sandbox` etkin olduğunda, gateway ajan araç yürütmesini
(shell, dosya okuma/yazma vb.) yalıtılmış Docker container'ları içinde çalıştırır; gateway'in
kendisi ise ana bilgisayarda kalır. Bu, tüm gateway'i container içine almadan
güvenilmeyen veya çok kiracılı ajan oturumları etrafında sert bir sınır sağlar.

Sandbox kapsamı ajan başına (varsayılan), oturum başına veya paylaşımlı olabilir. Her kapsam
için `/workspace` adresine bağlanmış kendi çalışma alanı bulunur. Ayrıca
izinli/yasaklı araç ilkeleri, ağ yalıtımı, kaynak sınırları ve tarayıcı
container'ları da yapılandırabilirsiniz.

Tam yapılandırma, imajlar, güvenlik notları ve çok ajanlı profiller için bkz.:

- [Sandboxing](/tr/gateway/sandboxing) -- eksiksiz sandbox başvurusu
- [OpenShell](/tr/gateway/openshell) -- sandbox container'larına etkileşimli shell erişimi
- [Multi-Agent Sandbox and Tools](/tr/tools/multi-agent-sandbox-tools) -- ajan başına geçersiz kılmalar

### Hızlı etkinleştirme

```json5
{
  agents: {
    defaults: {
      sandbox: {
        mode: "non-main", // off | non-main | all
        scope: "agent", // session | agent | shared
      },
    },
  },
}
```

Varsayılan sandbox imajını oluşturun:

```bash
scripts/sandbox-setup.sh
```

## Sorun giderme

<AccordionGroup>
  <Accordion title="İmaj eksik veya sandbox container'ı başlamıyor">
    Sandbox imajını
    [`scripts/sandbox-setup.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/sandbox-setup.sh)
    ile oluşturun veya `agents.defaults.sandbox.docker.image` değerini kendi özel imajınıza ayarlayın.
    Container'lar gerektikçe oturum başına otomatik oluşturulur.
  </Accordion>

  <Accordion title="Sandbox içinde izin hataları">
    `docker.user` değerini bağlı çalışma alanı sahipliğiyle eşleşen bir UID:GID olarak ayarlayın
    veya çalışma alanı klasörünün sahibini değiştirin.
  </Accordion>

  <Accordion title="Özel araçlar sandbox içinde bulunamıyor">
    OpenClaw komutları `sh -lc` (login shell) ile çalıştırır; bu,
    `/etc/profile` dosyasını yükler ve PATH'i sıfırlayabilir. Özel
    araç yollarınızı öne eklemek için `docker.env.PATH` ayarlayın veya Dockerfile'ınıza `/etc/profile.d/`
    altında bir betik ekleyin.
  </Accordion>

  <Accordion title="İmaj derlemesi sırasında OOM nedeniyle öldürüldü (çıkış 137)">
    VM en az 2 GB RAM gerektirir. Daha büyük bir makine sınıfı kullanın ve yeniden deneyin.
  </Accordion>

  <Accordion title="Control UI'da yetkisiz veya eşleme gerekli">
    Yeni bir dashboard bağlantısı alın ve tarayıcı cihazını onaylayın:

    ```bash
    docker compose run --rm openclaw-cli dashboard --no-open
    docker compose run --rm openclaw-cli devices list
    docker compose run --rm openclaw-cli devices approve <requestId>
    ```

    Daha fazla ayrıntı: [Dashboard](/web/dashboard), [Devices](/cli/devices).

  </Accordion>

  <Accordion title="Gateway hedefi ws://172.x.x.x gösteriyor veya Docker CLI'dan eşleme hataları alınıyor">
    Gateway modunu ve bind ayarını sıfırlayın:

    ```bash
    docker compose run --rm openclaw-cli config set --batch-json '[{"path":"gateway.mode","value":"local"},{"path":"gateway.bind","value":"lan"}]'
    docker compose run --rm openclaw-cli devices list --url ws://127.0.0.1:18789
    ```

  </Accordion>
</AccordionGroup>

## İlgili

- [Kurulum Genel Bakış](/tr/install) — tüm kurulum yöntemleri
- [Podman](/tr/install/podman) — Docker'a Podman alternatifi
- [ClawDock](/tr/install/clawdock) — Docker Compose topluluk kurulumu
- [Güncelleme](/tr/install/updating) — OpenClaw'ı güncel tutma
- [Yapılandırma](/tr/gateway/configuration) — kurulum sonrası gateway yapılandırması
