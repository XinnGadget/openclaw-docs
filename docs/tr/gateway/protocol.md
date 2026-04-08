---
read_when:
    - Gateway WS istemcilerini uyguluyor veya güncelliyorsunuz
    - Protokol uyumsuzluklarında veya bağlantı hatalarında hata ayıklıyorsunuz
    - Protokol şemasını/modellerini yeniden oluşturuyorsunuz
summary: 'Gateway WebSocket protokolü: el sıkışma, çerçeveler, sürümleme'
title: Gateway Protokolü
x-i18n:
    generated_at: "2026-04-08T02:15:52Z"
    model: gpt-5.4
    provider: openai
    source_hash: 8635e3ac1dd311dbd3a770b088868aa1495a8d53b3ebc1eae0dfda3b2bf4694a
    source_path: gateway/protocol.md
    workflow: 15
---

# Gateway protokolü (WebSocket)

Gateway WS protokolü, OpenClaw için **tek denetim düzlemi + düğüm taşımasıdır**.
Tüm istemciler (CLI, web UI, macOS uygulaması, iOS/Android düğümleri, headless
düğümler) WebSocket üzerinden bağlanır ve el sıkışma sırasında
**rollerini** + **kapsamlarını** bildirir.

## Taşıma

- WebSocket, JSON yükleri içeren metin çerçeveleri.
- İlk çerçeve **zorunlu olarak** bir `connect` isteği olmalıdır.

## El sıkışma (`connect`)

Gateway → İstemci (bağlantı öncesi sınama):

```json
{
  "type": "event",
  "event": "connect.challenge",
  "payload": { "nonce": "…", "ts": 1737264000000 }
}
```

İstemci → Gateway:

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "cli",
      "version": "1.2.3",
      "platform": "macos",
      "mode": "operator"
    },
    "role": "operator",
    "scopes": ["operator.read", "operator.write"],
    "caps": [],
    "commands": [],
    "permissions": {},
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-cli/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

Gateway → İstemci:

```json
{
  "type": "res",
  "id": "…",
  "ok": true,
  "payload": { "type": "hello-ok", "protocol": 3, "policy": { "tickIntervalMs": 15000 } }
}
```

Bir cihaz token'ı verildiğinde, `hello-ok` ayrıca şunları da içerir:

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "operator",
    "scopes": ["operator.read", "operator.write"]
  }
}
```

Güvenilir bootstrap devri sırasında `hello-ok.auth`, `deviceTokens` içinde
ek sınırlı rol girdileri de içerebilir:

```json
{
  "auth": {
    "deviceToken": "…",
    "role": "node",
    "scopes": [],
    "deviceTokens": [
      {
        "deviceToken": "…",
        "role": "operator",
        "scopes": ["operator.approvals", "operator.read", "operator.talk.secrets", "operator.write"]
      }
    ]
  }
}
```

Yerleşik node/operator bootstrap akışında birincil node token'ı
`scopes: []` olarak kalır ve devredilen tüm operator token'ları bootstrap
operator izin listesiyle (`operator.approvals`, `operator.read`,
`operator.talk.secrets`, `operator.write`) sınırlı kalır. Bootstrap kapsam
denetimleri rol önekli olmaya devam eder: operator girdileri yalnızca operator
isteklerini karşılar ve operator olmayan roller için yine kendi rol önekleri
altında kapsamlar gerekir.

### Node örneği

```json
{
  "type": "req",
  "id": "…",
  "method": "connect",
  "params": {
    "minProtocol": 3,
    "maxProtocol": 3,
    "client": {
      "id": "ios-node",
      "version": "1.2.3",
      "platform": "ios",
      "mode": "node"
    },
    "role": "node",
    "scopes": [],
    "caps": ["camera", "canvas", "screen", "location", "voice"],
    "commands": ["camera.snap", "canvas.navigate", "screen.record", "location.get"],
    "permissions": { "camera.capture": true, "screen.record": false },
    "auth": { "token": "…" },
    "locale": "en-US",
    "userAgent": "openclaw-ios/1.2.3",
    "device": {
      "id": "device_fingerprint",
      "publicKey": "…",
      "signature": "…",
      "signedAt": 1737264000000,
      "nonce": "…"
    }
  }
}
```

## Çerçeveleme

- **İstek**: `{type:"req", id, method, params}`
- **Yanıt**: `{type:"res", id, ok, payload|error}`
- **Olay**: `{type:"event", event, payload, seq?, stateVersion?}`

Yan etki oluşturan yöntemler için **idempotency key** gerekir (şemaya bakın).

## Roller + kapsamlar

### Roller

- `operator` = denetim düzlemi istemcisi (CLI/UI/otomasyon).
- `node` = yetenek ana makinesi (`camera`/`screen`/`canvas`/`system.run`).

### Kapsamlar (`operator`)

Yaygın kapsamlar:

- `operator.read`
- `operator.write`
- `operator.admin`
- `operator.approvals`
- `operator.pairing`
- `operator.talk.secrets`

`talk.config` içinde `includeSecrets: true`, `operator.talk.secrets`
(veya `operator.admin`) gerektirir.

Eklenti tarafından kaydedilen gateway RPC yöntemleri kendi operator kapsamlarını
isteyebilir, ancak ayrılmış çekirdek yönetici önekleri (`config.*`, `exec.approvals.*`, `wizard.*`,
`update.*`) her zaman `operator.admin` olarak çözülür.

Yöntem kapsamı yalnızca ilk geçittir. `chat.send` üzerinden ulaşılan bazı slash
komutları bunun üzerine daha sıkı komut düzeyi denetimler uygular. Örneğin kalıcı
`/config set` ve `/config unset` yazmaları `operator.admin` gerektirir.

`node.pair.approve`, temel yöntem kapsamının üzerine ek bir onay zamanı kapsam
denetimine de sahiptir:

- komutsuz istekler: `operator.pairing`
- exec olmayan node komutları içeren istekler: `operator.pairing` + `operator.write`
- `system.run`, `system.run.prepare` veya `system.which` içeren istekler:
  `operator.pairing` + `operator.admin`

### Yetenekler/komutlar/izinler (`node`)

Node'lar bağlantı sırasında yetenek beyanlarını bildirir:

- `caps`: üst düzey yetenek kategorileri.
- `commands`: invoke için komut izin listesi.
- `permissions`: ayrıntılı anahtarlar (`screen.record`, `camera.capture` gibi).

Gateway bunları **beyan** olarak ele alır ve sunucu tarafı izin listelerini uygular.

## Varlık durumu

- `system-presence`, cihaz kimliğine göre anahtarlanmış girdiler döndürür.
- Varlık girdileri `deviceId`, `roles` ve `scopes` içerir; böylece UI'ler aynı cihaz
  hem **operator** hem de **node** olarak bağlandığında tek bir satır gösterebilir.

## Yaygın RPC yöntem aileleri

Bu sayfa, oluşturulmuş tam bir döküm değildir; ancak genel WS yüzeyi yukarıdaki
el sıkışma/kimlik doğrulama örneklerinden daha geniştir. Bunlar Gateway'in bugün
sunduğu başlıca yöntem aileleridir.

`hello-ok.features.methods`, `src/gateway/server-methods-list.ts` ile yüklenmiş
eklenti/kanal yöntem dışa aktarımlarından oluşturulan muhafazakâr bir keşif listesidir.
Bunu özellik keşfi olarak değerlendirin; `src/gateway/server-methods/*.ts`
içinde uygulanan çağrılabilir her yardımcı işlevin oluşturulmuş dökümü olarak değil.

### Sistem ve kimlik

- `health`, önbelleğe alınmış veya yeni yoklanmış gateway sağlık anlık görüntüsünü döndürür.
- `status`, `/status` tarzı gateway özetini döndürür; hassas alanlar yalnızca
  yönetici kapsamlı operator istemcilerine dahil edilir.
- `gateway.identity.get`, relay ve eşleştirme akışlarında kullanılan gateway cihaz kimliğini döndürür.
- `system-presence`, bağlı operator/node cihazlar için geçerli varlık anlık görüntüsünü döndürür.
- `system-event`, bir sistem olayı ekler ve varlık bağlamını güncelleyip
  yayınlayabilir.
- `last-heartbeat`, kalıcı hale getirilmiş en son heartbeat olayını döndürür.
- `set-heartbeats`, gateway üzerinde heartbeat işlemeyi açıp kapatır.

### Modeller ve kullanım

- `models.list`, çalışma zamanında izin verilen model kataloğunu döndürür.
- `usage.status`, sağlayıcı kullanım pencerelerini/kalan kota özetlerini döndürür.
- `usage.cost`, bir tarih aralığı için toplu maliyet kullanım özetlerini döndürür.
- `doctor.memory.status`, etkin varsayılan agent çalışma alanı için
  vector-memory / embedding hazır olma durumunu döndürür.
- `sessions.usage`, oturum başına kullanım özetlerini döndürür.
- `sessions.usage.timeseries`, tek bir oturum için zaman serisi kullanımını döndürür.
- `sessions.usage.logs`, tek bir oturum için kullanım günlük girdilerini döndürür.

### Kanallar ve giriş yardımcıları

- `channels.status`, yerleşik + paketlenmiş kanal/eklenti durum özetlerini döndürür.
- `channels.logout`, kanal destekliyorsa belirli bir kanal/hesap oturumunu kapatır.
- `web.login.start`, geçerli QR destekli web kanalı sağlayıcısı için bir QR/web giriş akışı başlatır.
- `web.login.wait`, bu QR/web giriş akışının tamamlanmasını bekler ve başarı durumunda
  kanalı başlatır.
- `push.test`, kayıtlı bir iOS node'una test APNs bildirimi gönderir.
- `voicewake.get`, depolanan uyandırma sözcüğü tetikleyicilerini döndürür.
- `voicewake.set`, uyandırma sözcüğü tetikleyicilerini günceller ve değişikliği yayınlar.

### Mesajlaşma ve günlükler

- `send`, chat çalıştırıcısının dışında kanal/hesap/thread hedefli gönderimler için
  doğrudan giden teslim RPC'sidir.
- `logs.tail`, yapılandırılmış gateway dosya günlüğü kuyruğunu imleç/sınır ve
  en yüksek bayt denetimleriyle döndürür.

### Talk ve TTS

- `talk.config`, etkili Talk yapılandırma yükünü döndürür; `includeSecrets`
  için `operator.talk.secrets` (veya `operator.admin`) gerekir.
- `talk.mode`, WebChat/Control UI istemcileri için geçerli Talk modu durumunu ayarlar/yayınlar.
- `talk.speak`, etkin Talk konuşma sağlayıcısı üzerinden konuşma sentezler.
- `tts.status`, TTS etkin durumunu, etkin sağlayıcıyı, geri dönüş sağlayıcılarını
  ve sağlayıcı yapılandırma durumunu döndürür.
- `tts.providers`, görünür TTS sağlayıcı envanterini döndürür.
- `tts.enable` ve `tts.disable`, TTS tercih durumunu açıp kapatır.
- `tts.setProvider`, tercih edilen TTS sağlayıcısını günceller.
- `tts.convert`, tek seferlik metinden konuşmaya dönüştürme çalıştırır.

### Gizli bilgiler, yapılandırma, güncelleme ve sihirbaz

- `secrets.reload`, etkin SecretRef'leri yeniden çözümler ve çalışma zamanı gizli bilgi durumunu
  yalnızca tam başarıda değiştirir.
- `secrets.resolve`, belirli bir komut/hedef kümesi için komut hedefli gizli bilgi atamalarını çözümler.
- `config.get`, geçerli yapılandırma anlık görüntüsünü ve hash değerini döndürür.
- `config.set`, doğrulanmış bir yapılandırma yükü yazar.
- `config.patch`, kısmi bir yapılandırma güncellemesini birleştirir.
- `config.apply`, tam yapılandırma yükünü doğrular + değiştirir.
- `config.schema`, Control UI ve CLI araçlarının kullandığı canlı yapılandırma şeması yükünü
  döndürür: şema, `uiHints`, sürüm ve oluşturma meta verileri; buna çalışma zamanı
  bunları yükleyebildiğinde eklenti + kanal şema meta verileri de dahildir. Şema,
  eşleşen alan belgeleri mevcut olduğunda, UI'nin kullandığı aynı etiketler
  ve yardım metninden türetilen `title` / `description` meta verilerini içerir;
  buna iç içe nesne, joker karakter, dizi öğesi ve `anyOf` / `oneOf` / `allOf`
  bileşim dalları da dahildir.
- `config.schema.lookup`, tek bir yapılandırma yolu için yol kapsamlı bir lookup yükü döndürür:
  normalize edilmiş yol, sığ bir şema düğümü, eşleşen hint + `hintPath` ve
  UI/CLI ayrıntılı inceleme için doğrudan alt özetler.
  - Lookup şema düğümleri kullanıcıya dönük belgeleri ve yaygın doğrulama alanlarını korur:
    `title`, `description`, `type`, `enum`, `const`, `format`, `pattern`,
    sayısal/dize/dizi/nesne sınırları ve `additionalProperties`, `deprecated`,
    `readOnly`, `writeOnly` gibi boolean bayraklar.
  - Alt özetler `key`, normalize edilmiş `path`, `type`, `required`,
    `hasChildren` ile eşleşen `hint` / `hintPath` bilgilerini açığa çıkarır.
- `update.run`, gateway güncelleme akışını çalıştırır ve yalnızca güncellemenin
  kendisi başarılı olduğunda yeniden başlatma zamanlar.
- `wizard.start`, `wizard.next`, `wizard.status` ve `wizard.cancel`, onboarding
  sihirbazını WS RPC üzerinden sunar.

### Mevcut başlıca aileler

#### Agent ve çalışma alanı yardımcıları

- `agents.list`, yapılandırılmış agent girdilerini döndürür.
- `agents.create`, `agents.update` ve `agents.delete`, agent kayıtlarını ve
  çalışma alanı bağlantılarını yönetir.
- `agents.files.list`, `agents.files.get` ve `agents.files.set`, bir agent için açığa çıkarılan
  bootstrap çalışma alanı dosyalarını yönetir.
- `agent.identity.get`, bir agent veya oturum için etkili asistan kimliğini döndürür.
- `agent.wait`, bir çalışmanın tamamlanmasını bekler ve varsa son anlık görüntüyü döndürür.

#### Oturum denetimi

- `sessions.list`, geçerli oturum dizinini döndürür.
- `sessions.subscribe` ve `sessions.unsubscribe`, geçerli WS istemcisi için
  oturum değişikliği olay aboneliklerini açıp kapatır.
- `sessions.messages.subscribe` ve `sessions.messages.unsubscribe`, tek bir oturum için
  transkript/mesaj olay aboneliklerini açıp kapatır.
- `sessions.preview`, belirli oturum anahtarları için sınırlı transkript önizlemeleri döndürür.
- `sessions.resolve`, bir oturum hedefini çözümler veya kanonik hale getirir.
- `sessions.create`, yeni bir oturum girdisi oluşturur.
- `sessions.send`, mevcut bir oturuma mesaj gönderir.
- `sessions.steer`, etkin bir oturum için kesip yönlendirme varyantıdır.
- `sessions.abort`, bir oturum için etkin işleri iptal eder.
- `sessions.patch`, oturum meta verilerini/geçersiz kılmaları günceller.
- `sessions.reset`, `sessions.delete` ve `sessions.compact`, oturum bakımı gerçekleştirir.
- `sessions.get`, depolanan tam oturum satırını döndürür.
- chat yürütmesi hâlâ `chat.history`, `chat.send`, `chat.abort` ve
  `chat.inject` kullanır.
- `chat.history`, UI istemcileri için ekran-normalize edilmiştir: satır içi yönerge etiketleri
  görünür metinden çıkarılır; düz metin araç çağrısı XML yükleri (şunlar dahil:
  `<tool_call>...</tool_call>`, `<function_call>...</function_call>`,
  `<tool_calls>...</tool_calls>`, `<function_calls>...</function_calls>` ve
  kısaltılmış araç çağrısı blokları) ile sızmış ASCII/tam genişlikli model denetim token'ları
  çıkarılır; tam olarak `NO_REPLY` /
  `no_reply` olan saf sessiz token asistan satırları atlanır ve
  aşırı büyük satırlar yer tutucularla değiştirilebilir.

#### Cihaz eşleştirme ve cihaz token'ları

- `device.pair.list`, bekleyen ve onaylanmış eşleştirilmiş cihazları döndürür.
- `device.pair.approve`, `device.pair.reject` ve `device.pair.remove`,
  cihaz eşleştirme kayıtlarını yönetir.
- `device.token.rotate`, eşleştirilmiş bir cihaz token'ını onaylanmış rolü
  ve kapsam sınırları içinde döndürür.
- `device.token.revoke`, eşleştirilmiş bir cihaz token'ını iptal eder.

#### Node eşleştirme, invoke ve bekleyen işler

- `node.pair.request`, `node.pair.list`, `node.pair.approve`,
  `node.pair.reject` ve `node.pair.verify`, node eşleştirme ve bootstrap
  doğrulamasını kapsar.
- `node.list` ve `node.describe`, bilinen/bağlı node durumunu döndürür.
- `node.rename`, eşleştirilmiş bir node etiketini günceller.
- `node.invoke`, bir komutu bağlı bir node'a iletir.
- `node.invoke.result`, bir invoke isteğinin sonucunu döndürür.
- `node.event`, node kaynaklı olayları gateway'e geri taşır.
- `node.canvas.capability.refresh`, kapsamlı canvas yetenek token'larını yeniler.
- `node.pending.pull` ve `node.pending.ack`, bağlı node kuyruk API'leridir.
- `node.pending.enqueue` ve `node.pending.drain`, çevrim dışı/bağlı olmayan node'lar için
  kalıcı bekleyen işleri yönetir.

#### Onay aileleri

- `exec.approval.request`, `exec.approval.get`, `exec.approval.list` ve
  `exec.approval.resolve`, tek seferlik exec onay istekleri ile bekleyen
  onay arama/yeniden oynatmayı kapsar.
- `exec.approval.waitDecision`, tek bir bekleyen exec onayını bekler ve
  son kararı döndürür (veya zaman aşımında `null`).
- `exec.approvals.get` ve `exec.approvals.set`, gateway exec onay
  ilkesi anlık görüntülerini yönetir.
- `exec.approvals.node.get` ve `exec.approvals.node.set`, node relay komutları
  aracılığıyla node-yerel exec onay ilkesini yönetir.
- `plugin.approval.request`, `plugin.approval.list`,
  `plugin.approval.waitDecision` ve `plugin.approval.resolve`,
  eklenti tanımlı onay akışlarını kapsar.

#### Diğer başlıca aileler

- otomasyon:
  - `wake`, anında veya sonraki heartbeat'te bir uyandırma metni ekleme zamanlar
  - `cron.list`, `cron.status`, `cron.add`, `cron.update`, `cron.remove`,
    `cron.run`, `cron.runs`
- Skills/araçlar: `skills.*`, `tools.catalog`, `tools.effective`

### Yaygın olay aileleri

- `chat`: `chat.inject` ve diğer yalnızca transkript chat
  olayları gibi UI chat güncellemeleri.
- `session.message` ve `session.tool`: abone olunan bir oturum için transkript/olay akışı güncellemeleri.
- `sessions.changed`: oturum dizini veya meta verisi değişti.
- `presence`: sistem varlık anlık görüntüsü güncellemeleri.
- `tick`: periyodik keepalive / canlılık olayı.
- `health`: gateway sağlık anlık görüntüsü güncellemesi.
- `heartbeat`: heartbeat olay akışı güncellemesi.
- `cron`: cron çalışması/iş değişikliği olayı.
- `shutdown`: gateway kapanış bildirimi.
- `node.pair.requested` / `node.pair.resolved`: node eşleştirme yaşam döngüsü.
- `node.invoke.request`: node invoke isteği yayını.
- `device.pair.requested` / `device.pair.resolved`: eşleştirilmiş cihaz yaşam döngüsü.
- `voicewake.changed`: uyandırma sözcüğü tetikleyici yapılandırması değişti.
- `exec.approval.requested` / `exec.approval.resolved`: exec onay
  yaşam döngüsü.
- `plugin.approval.requested` / `plugin.approval.resolved`: eklenti onayı
  yaşam döngüsü.

### Node yardımcı yöntemleri

- Node'lar, otomatik izin denetimleri için geçerli skill yürütülebilir dosya
  listesini almak üzere `skills.bins` çağırabilir.

### Operator yardımcı yöntemleri

- Operator'lar, bir
  agent için çalışma zamanı araç kataloğunu almak üzere `tools.catalog` (`operator.read`) çağırabilir. Yanıt, gruplanmış araçları ve kaynak meta verilerini içerir:
  - `source`: `core` veya `plugin`
  - `pluginId`: `source="plugin"` olduğunda eklenti sahibi
  - `optional`: bir eklenti aracının isteğe bağlı olup olmadığı
- Operator'lar, bir oturum için çalışma zamanında etkili araç
  envanterini almak üzere `tools.effective` (`operator.read`) çağırabilir.
  - `sessionKey` zorunludur.
  - Gateway, çağıranın sağladığı auth veya teslim bağlamını kabul etmek yerine
    güvenilir çalışma zamanı bağlamını oturumdan sunucu tarafında türetir.
  - Yanıt oturum kapsamlıdır ve etkin konuşmanın şu anda kullanabileceği şeyleri
    yansıtır; buna çekirdek, eklenti ve kanal araçları dahildir.
- Operator'lar, bir
  agent için görünür skill envanterini almak üzere `skills.status` (`operator.read`) çağırabilir.
  - `agentId` isteğe bağlıdır; varsayılan agent çalışma alanını okumak için belirtmeyin.
  - Yanıt; uygunluk, eksik gereksinimler, yapılandırma denetimleri ve
    ham gizli değerleri açığa çıkarmadan temizlenmiş kurulum seçeneklerini içerir.
- Operator'lar, ClawHub keşif meta verileri için
  `skills.search` ve `skills.detail` (`operator.read`) çağırabilir.
- Operator'lar, iki modda `skills.install` (`operator.admin`) çağırabilir:
  - ClawHub modu: `{ source: "clawhub", slug, version?, force? }`, varsayılan
    agent çalışma alanı `skills/` dizinine bir skill klasörü kurar.
  - Gateway installer modu: `{ name, installId, dangerouslyForceUnsafeInstall?, timeoutMs? }`
    gateway ana makinesinde bildirilmiş bir `metadata.openclaw.install` eylemi çalıştırır.
- Operator'lar, iki modda `skills.update` (`operator.admin`) çağırabilir:
  - ClawHub modu, izlenen tek bir slug'ı veya varsayılan agent çalışma alanındaki
    tüm izlenen ClawHub kurulumlarını günceller.
  - Config modu, `enabled`,
    `apiKey` ve `env` gibi `skills.entries.<skillKey>` değerlerini yamalar.

## Exec onayları

- Bir exec isteği onay gerektirdiğinde gateway `exec.approval.requested` yayınlar.
- Operator istemcileri `exec.approval.resolve` çağırarak çözümler (`operator.approvals` kapsamı gerekir).
- `host=node` için `exec.approval.request`, `systemRunPlan`
  (kanonik `argv`/`cwd`/`rawCommand`/oturum meta verileri) içermelidir. `systemRunPlan` içermeyen istekler reddedilir.
- Onaydan sonra iletilen `node.invoke system.run` çağrıları, yetkili komut/cwd/oturum bağlamı olarak
  bu kanonik `systemRunPlan`'ı yeniden kullanır.
- Bir çağıran, hazırlık ile son onaylı `system.run` iletimi arasında
  `command`, `rawCommand`, `cwd`, `agentId` veya
  `sessionKey` değerlerini değiştirirse, gateway değiştirilen yüke güvenmek yerine
  çalıştırmayı reddeder.

## Agent teslim geri dönüşü

- `agent` istekleri, giden teslim istemek için `deliver=true` içerebilir.
- `bestEffortDeliver=false` katı davranışı korur: çözümlenmemiş veya yalnızca iç kullanım teslim hedefleri `INVALID_REQUEST` döndürür.
- `bestEffortDeliver=true`, harici teslim edilebilir bir rota çözümlenemediğinde
  yalnızca oturum yürütmesine geri dönüşe izin verir (örneğin iç/webchat oturumları veya belirsiz çok kanallı yapılandırmalar).

## Sürümleme

- `PROTOCOL_VERSION`, `src/gateway/protocol/schema.ts` içinde bulunur.
- İstemciler `minProtocol` + `maxProtocol` gönderir; sunucu uyumsuzlukları reddeder.
- Şemalar + modeller TypeBox tanımlarından oluşturulur:
  - `pnpm protocol:gen`
  - `pnpm protocol:gen:swift`
  - `pnpm protocol:check`

## Kimlik doğrulama

- Paylaşılan gizli gateway kimlik doğrulaması, yapılandırılmış auth moduna bağlı olarak
  `connect.params.auth.token` veya `connect.params.auth.password` kullanır.
- Tailscale Serve
  (`gateway.auth.allowTailscale: true`) veya loopback olmayan
  `gateway.auth.mode: "trusted-proxy"` gibi kimlik taşıyan modlar, connect auth denetimini
  `connect.params.auth.*` yerine istek başlıklarından karşılar.
- Özel giriş `gateway.auth.mode: "none"`, paylaşılan gizli connect auth denetimini
  tamamen atlar; bu modu genel/güvenilmeyen girişte açığa çıkarmayın.
- Eşleştirmeden sonra Gateway, bağlantı rolü + kapsamlarına göre sınırlı bir **device token**
  verir. Bu değer `hello-ok.auth.deviceToken` içinde döndürülür ve istemci tarafından
  gelecekteki bağlantılar için kalıcı hale getirilmelidir.
- İstemciler, başarılı her bağlantıdan sonra birincil `hello-ok.auth.deviceToken` değerini kalıcı hale getirmelidir.
- Bu **depolanmış** device token ile yeniden bağlanmak, o token için onaylanmış
  depolanmış kapsam kümesini de yeniden kullanmalıdır. Bu, zaten verilmiş olan
  read/probe/status erişimini korur ve yeniden bağlantıların sessizce
  daha dar örtük bir yalnızca yönetici kapsamına çökmesini önler.
- Normal connect auth önceliği sırasıyla açık paylaşılan token/parola, sonra
  açık `deviceToken`, sonra cihaz başına depolanmış token, sonra bootstrap token'dır.
- Ek `hello-ok.auth.deviceTokens` girdileri bootstrap devri token'larıdır.
  Bunları yalnızca bağlantı bootstrap auth ile güvenilir bir taşıma üzerinden
  yapıldıysa, örneğin `wss://` veya loopback/yerel eşleştirme, kalıcı hale getirin.
- Bir istemci açık bir `deviceToken` veya açık `scopes` sağlarsa, bu
  çağıran tarafından istenen kapsam kümesi yetkili olmaya devam eder; önbelleğe alınmış kapsamlar yalnızca
  istemci depolanmış cihaz başı token'ı yeniden kullandığında yeniden kullanılır.
- Device token'lar `device.token.rotate` ve
  `device.token.revoke` ile döndürülebilir/iptal edilebilir (`operator.pairing` kapsamı gerekir).
- Token verme/döndürme, o cihazın eşleştirme girdisinde kaydedilmiş onaylı rol kümesiyle
  sınırlı kalır; bir token'ı döndürmek, cihazı eşleştirme onayının hiç vermediği
  bir role genişletemez.
- Eşleştirilmiş cihaz token oturumlarında cihaz yönetimi, çağıran ayrıca
  `operator.admin` yetkisine sahip değilse kendine kapsamlıdır: yönetici olmayan çağıranlar
  yalnızca **kendi** cihaz girdilerini kaldırabilir/iptal edebilir/döndürebilir.
- `device.token.rotate`, istenen operator kapsam kümesini ayrıca çağıranın geçerli
  oturum kapsamlarıyla karşılaştırır. Yönetici olmayan çağıranlar, bir token'ı
  zaten sahip olduklarından daha geniş bir operator kapsam kümesine döndüremez.
- Kimlik doğrulama hataları `error.details.code` ile birlikte kurtarma ipuçları içerir:
  - `error.details.canRetryWithDeviceToken` (boolean)
  - `error.details.recommendedNextStep` (`retry_with_device_token`, `update_auth_configuration`, `update_auth_credentials`, `wait_then_retry`, `review_auth_configuration`)
- `AUTH_TOKEN_MISMATCH` için istemci davranışı:
  - Güvenilir istemciler, önbelleğe alınmış cihaz başı token ile bir sınırlı yeniden deneme yapabilir.
  - Bu yeniden deneme başarısız olursa istemciler otomatik yeniden bağlanma döngülerini durdurmalı ve operator eylem yönergelerini göstermelidir.

## Cihaz kimliği + eşleştirme

- Node'lar, bir anahtar çiftinin parmak izinden türetilmiş kararlı bir cihaz kimliği (`device.id`) içermelidir.
- Gateway'ler cihaz + rol başına token verir.
- Yerel otomatik onay etkin değilse yeni cihaz kimlikleri için eşleştirme onayı gerekir.
- Eşleştirme otomatik onayı, doğrudan yerel loopback bağlantıları etrafında merkezlenmiştir.
- OpenClaw ayrıca güvenilir paylaşılan gizli yardımcı akışları için dar bir
  arka uç/container-yerel self-connect yoluna da sahiptir.
- Aynı ana makinedeki tailnet veya LAN bağlantıları eşleştirme açısından hâlâ uzak kabul edilir
  ve onay gerektirir.
- Tüm WS istemcileri `connect` sırasında `device` kimliğini içermelidir (operator + node).
  Control UI bunu yalnızca şu modlarda atlayabilir:
  - yalnızca localhost için güvensiz HTTP uyumluluğu sağlayan `gateway.controlUi.allowInsecureAuth=true`.
  - başarılı `gateway.auth.mode: "trusted-proxy"` operator Control UI auth.
  - `gateway.controlUi.dangerouslyDisableDeviceAuth=true` (break-glass, ciddi güvenlik düşüşü).
- Tüm bağlantılar, sunucu tarafından sağlanan `connect.challenge` nonce değerini imzalamalıdır.

### Cihaz kimlik doğrulama geçiş tanılamaları

Hâlâ challenge öncesi imzalama davranışı kullanan eski istemciler için `connect`,
sabit bir `error.details.reason` ile birlikte artık `error.details.code` altında
`DEVICE_AUTH_*` ayrıntı kodları döndürür.

Yaygın geçiş hataları:

| Mesaj                       | details.code                     | details.reason           | Anlamı                                            |
| --------------------------- | -------------------------------- | ------------------------ | ------------------------------------------------- |
| `device nonce required`     | `DEVICE_AUTH_NONCE_REQUIRED`     | `device-nonce-missing`   | İstemci `device.nonce` alanını atladı (veya boş gönderdi). |
| `device nonce mismatch`     | `DEVICE_AUTH_NONCE_MISMATCH`     | `device-nonce-mismatch`  | İstemci eski/yanlış bir nonce ile imzaladı.       |
| `device signature invalid`  | `DEVICE_AUTH_SIGNATURE_INVALID`  | `device-signature`       | İmza yükü v2 yükü ile eşleşmiyor.                 |
| `device signature expired`  | `DEVICE_AUTH_SIGNATURE_EXPIRED`  | `device-signature-stale` | İmzalanan zaman damgası izin verilen kaymanın dışında. |
| `device identity mismatch`  | `DEVICE_AUTH_DEVICE_ID_MISMATCH` | `device-id-mismatch`     | `device.id`, açık anahtar parmak iziyle eşleşmiyor. |
| `device public key invalid` | `DEVICE_AUTH_PUBLIC_KEY_INVALID` | `device-public-key`      | Açık anahtar biçimi/kanonikleştirme başarısız oldu. |

Geçiş hedefi:

- Her zaman `connect.challenge` bekleyin.
- Sunucu nonce değerini içeren v2 yükünü imzalayın.
- Aynı nonce değerini `connect.params.device.nonce` içinde gönderin.
- Tercih edilen imza yükü `v3`'tür; bu, `platform` ve `deviceFamily` alanlarını,
  device/client/role/scopes/token/nonce alanlarına ek olarak bağlar.
- Eski `v2` imzaları uyumluluk için kabul edilmeye devam eder, ancak eşleştirilmiş cihaz
  meta veri sabitlemesi yeniden bağlantıda komut ilkesini kontrol etmeyi sürdürür.

## TLS + pinleme

- WS bağlantıları için TLS desteklenir.
- İstemciler isteğe bağlı olarak gateway sertifika parmak izini pinleyebilir
  (`gateway.tls` yapılandırması ile `gateway.remote.tlsFingerprint` veya CLI `--tls-fingerprint` değerlerine bakın).

## Kapsam

Bu protokol **tam gateway API'sini** açığa çıkarır (durum, kanallar, modeller, chat,
agent, oturumlar, node'lar, onaylar vb.). Tam yüzey,
`src/gateway/protocol/schema.ts` içindeki TypeBox şemalarıyla tanımlanır.
