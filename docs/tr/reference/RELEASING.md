---
read_when:
    - Herkese açık sürüm kanalı tanımlarını arıyorum
    - Sürüm adlandırması ve yayın sıklığını arıyorum
summary: Herkese açık sürüm kanalları, sürüm adlandırması ve yayın sıklığı
title: Sürüm Politikası
x-i18n:
    generated_at: "2026-04-14T08:52:08Z"
    model: gpt-5.4
    provider: openai
    source_hash: 3eaf9f1786b8c9fd4f5a9c657b623cb69d1a485958e1a9b8f108511839b63587
    source_path: reference/RELEASING.md
    workflow: 15
---

# Sürüm Politikası

OpenClaw’ın herkese açık üç sürüm hattı vardır:

- stable: varsayılan olarak npm `beta`’ya yayımlanan etiketli sürümler veya açıkça istendiğinde npm `latest`’e
- beta: npm `beta`’ya yayımlanan ön sürüm etiketleri
- dev: `main` dalının hareketli başı

## Sürüm adlandırması

- Stable sürüm versiyonu: `YYYY.M.D`
  - Git etiketi: `vYYYY.M.D`
- Stable düzeltme sürümü versiyonu: `YYYY.M.D-N`
  - Git etiketi: `vYYYY.M.D-N`
- Beta ön sürüm versiyonu: `YYYY.M.D-beta.N`
  - Git etiketi: `vYYYY.M.D-beta.N`
- Ay veya günü sıfırla doldurmayın
- `latest`, şu anda öne çıkarılmış stable npm sürümü anlamına gelir
- `beta`, şu anda beta kurulum hedefi anlamına gelir
- Stable ve stable düzeltme sürümleri varsayılan olarak npm `beta`’ya yayımlanır; sürüm operatörleri açıkça `latest`’i hedefleyebilir veya daha sonra doğrulanmış bir beta derlemesini öne çıkarabilir
- Her OpenClaw sürümü, npm paketini ve macOS uygulamasını birlikte yayımlar

## Sürüm sıklığı

- Sürümler önce beta olarak ilerler
- Stable, yalnızca en son beta doğrulandıktan sonra gelir
- Ayrıntılı sürüm prosedürü, onaylar, kimlik bilgileri ve kurtarma notları
  yalnızca maintainers içindir

## Sürüm ön kontrolü

- Paket doğrulama adımı için beklenen `dist/*` sürüm artifaktları ve Control UI paketi mevcut olsun diye `pnpm release:check` öncesinde `pnpm build && pnpm ui:build` çalıştırın
- Her etiketli sürümden önce `pnpm release:check` çalıştırın
- Sürüm kontrolleri artık ayrı bir manuel iş akışında çalışır:
  `OpenClaw Release Checks`
- Bu ayrım bilinçlidir: gerçek npm sürüm yolunu kısa,
  deterministik ve artifakt odaklı tutarken, daha yavaş canlı kontrolleri kendi
  hattında tutar; böylece yayımlamayı geciktirmez veya engellemez
- Sürüm kontrolleri `main` iş akışı referansından tetiklenmelidir; böylece
  iş akışı mantığı ve gizli bilgiler kanonik kalır
- Bu iş akışı, mevcut bir sürüm etiketini veya geçerli tam
  40 karakterlik `main` commit SHA’sını kabul eder
- Commit-SHA modunda yalnızca geçerli `origin/main` HEAD kabul edilir; daha eski
  sürüm commit’leri için bir sürüm etiketi kullanın
- `OpenClaw NPM Release` yalnızca doğrulama amaçlı ön kontrolü de,
  itilmiş bir etiket gerektirmeden, geçerli tam 40 karakterlik `main` commit SHA’sını kabul eder
- Bu SHA yolu yalnızca doğrulama içindir ve gerçek bir yayıma yükseltilemez
- SHA modunda iş akışı, paket meta verisi kontrolü için yalnızca
  `v<package.json version>` üretir; gerçek yayımlama yine de gerçek bir sürüm etiketi gerektirir
- Her iki iş akışı da gerçek yayımlama ve öne çıkarma yolunu GitHub-hosted
  runner’larda tutarken, değişiklik yapmayan doğrulama yolu daha büyük
  Blacksmith Linux runner’larını kullanabilir
- Bu iş akışı
  `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_CACHE_TEST=1 pnpm test:live:cache`
  komutunu hem `OPENAI_API_KEY` hem de `ANTHROPIC_API_KEY` iş akışı gizli bilgilerini kullanarak çalıştırır
- npm sürüm ön kontrolü artık ayrı sürüm kontrolleri hattını beklemez
- Onaydan önce
  `RELEASE_TAG=vYYYY.M.D node --import tsx scripts/openclaw-npm-release-check.ts`
  komutunu (veya eşleşen beta/düzeltme etiketini) çalıştırın
- npm yayımlamasından sonra, yayımlanan kayıt defteri kurulum yolunu yeni bir geçici önekte doğrulamak için
  `node --import tsx scripts/openclaw-npm-postpublish-verify.ts YYYY.M.D`
  komutunu (veya eşleşen beta/düzeltme sürümünü) çalıştırın
- Maintainer sürüm otomasyonu artık ön kontrol-sonra-öne çıkarma modelini kullanır:
  - gerçek npm yayımlaması başarılı bir npm `preflight_run_id` geçmelidir
  - stable npm sürümleri varsayılan olarak `beta`’ya gider
  - stable npm yayımlaması iş akışı girdisiyle açıkça `latest`’i hedefleyebilir
  - `beta`’dan `latest`’e stable npm öne çıkarma, güvenilen `OpenClaw NPM Release` iş akışında hâlâ açık bir manuel mod olarak kullanılabilir
  - doğrudan stable yayımlar ayrıca, `latest` ve `beta` etiketlerinin ikisini de zaten yayımlanmış stable sürüme işaret eden açık bir dist-tag eşitleme modunu çalıştırabilir
  - bu dist-tag modları, npm `dist-tag` yönetimi güvenilen yayımlamadan ayrı olduğu için `npm-release` ortamında yine de geçerli bir `NPM_TOKEN` gerektirir
  - herkese açık `macOS Release` yalnızca doğrulama içindir
  - gerçek özel mac yayımlaması başarılı özel mac
    `preflight_run_id` ve `validate_run_id` geçmelidir
  - gerçek yayımlama yolları, artifaktları yeniden derlemek yerine
    hazırlanmış artifaktları öne çıkarır
- `YYYY.M.D-N` gibi stable düzeltme sürümleri için, yayımlama sonrası doğrulayıcı
  ayrıca `YYYY.M.D`’den `YYYY.M.D-N`’ye aynı geçici önek yükseltme yolunu da kontrol eder;
  böylece sürüm düzeltmeleri, eski global kurulumları sessizce temel stable yükte bırakmaz
- npm sürüm ön kontrolü, tarball hem
  `dist/control-ui/index.html` hem de boş olmayan bir `dist/control-ui/assets/` yükü içermediği sürece kapalı başarısız olur;
  böylece tekrar boş bir tarayıcı panosu göndermeyiz
- `pnpm test:install:smoke`, aday güncelleme tarball’ında npm pack `unpackedSize` bütçesini de uygular;
  böylece kurucu e2e, sürüm yayımlama yolundan önce kazara paket şişmesini yakalar
- Sürüm çalışması CI planlamasına, eklenti zamanlama manifestolarına veya
  eklenti test matrislerine dokunduysa, onaydan önce `.github/workflows/ci.yml`
  içindeki planlayıcıya ait `checks-node-extensions` iş akışı matris çıktılarını yeniden üretin ve gözden geçirin;
  böylece sürüm notları eski bir CI düzenini açıklamaz
- Stable macOS sürüm hazırlığı, güncelleyici yüzeylerini de içerir:
  - GitHub sürümü sonunda paketlenmiş `.zip`, `.dmg` ve `.dSYM.zip` dosyalarını içermelidir
  - `main` üzerindeki `appcast.xml`, yayımdan sonra yeni stable zip’i işaret etmelidir
  - paketlenmiş uygulama, hata ayıklama dışı bir bundle id, boş olmayan bir Sparkle feed URL’si ve o sürüm versiyonu için kanonik Sparkle derleme tabanına eşit veya daha yüksek bir `CFBundleVersion` korumalıdır

## NPM iş akışı girdileri

`OpenClaw NPM Release` şu operatör kontrollü girdileri kabul eder:

- `tag`: `v2026.4.2`, `v2026.4.2-1` veya
  `v2026.4.2-beta.1` gibi gerekli sürüm etiketi; `preflight_only=true` olduğunda,
  yalnızca doğrulama amaçlı ön kontrol için geçerli tam 40 karakterlik
  `main` commit SHA’sı da olabilir
- `preflight_only`: yalnızca doğrulama/derleme/paketleme için `true`, gerçek yayımlama yolu için `false`
- `preflight_run_id`: gerçek yayımlama yolunda gereklidir; böylece iş akışı,
  başarılı ön kontrol çalışmasından hazırlanmış tarball’ı yeniden kullanır
- `npm_dist_tag`: yayımlama yolu için npm hedef etiketi; varsayılan `beta`
- `promote_beta_to_latest`: yayımlamayı atlayıp daha önce yayımlanmış bir
  stable `beta` derlemesini `latest`’e taşımak için `true`
- `sync_stable_dist_tags`: yayımlamayı atlayıp hem `latest` hem de
  `beta` etiketlerini daha önce yayımlanmış bir stable sürüme yönlendirmek için `true`

`OpenClaw Release Checks` şu operatör kontrollü girdileri kabul eder:

- `ref`: doğrulanacak mevcut sürüm etiketi veya geçerli tam 40 karakterlik `main` commit
  SHA’sı

Kurallar:

- Stable ve düzeltme etiketleri `beta` veya `latest`’e yayımlanabilir
- Beta ön sürüm etiketleri yalnızca `beta`’ya yayımlanabilir
- Tam commit SHA girdisine yalnızca `preflight_only=true` olduğunda izin verilir
- Sürüm kontrolleri commit-SHA modu ayrıca geçerli `origin/main` HEAD gerektirir
- Gerçek yayımlama yolu, ön kontrolde kullanılan aynı `npm_dist_tag`’i kullanmalıdır;
  iş akışı, yayımlama devam etmeden önce bu meta veriyi doğrular
- Öne çıkarma modu stable veya düzeltme etiketi, `preflight_only=false`,
  boş bir `preflight_run_id` ve `npm_dist_tag=beta` kullanmalıdır
- Dist-tag eşitleme modu stable veya düzeltme etiketi,
  `preflight_only=false`, boş bir `preflight_run_id`, `npm_dist_tag=latest`
  ve `promote_beta_to_latest=false` kullanmalıdır
- Öne çıkarma ve dist-tag eşitleme modları ayrıca geçerli bir `NPM_TOKEN` gerektirir;
  çünkü `npm dist-tag add` yine normal npm kimlik doğrulaması ister; güvenilen yayımlama
  yalnızca paket yayımlama yolunu kapsar

## Stable npm sürüm sırası

Bir stable npm sürümü keserken:

1. `preflight_only=true` ile `OpenClaw NPM Release` çalıştırın
   - Etiket henüz yokken, ön kontrol iş akışının yalnızca doğrulama amaçlı deneme çalıştırması için geçerli tam `main` commit SHA’sını kullanabilirsiniz
2. Normal beta-önce akışı için `npm_dist_tag=beta` seçin veya yalnızca
   doğrudan stable yayımlama yapmak istediğinizde `latest` seçin
3. Canlı prompt cache kapsamı istediğinizde,
   aynı etiket veya geçerli tam `main` commit SHA’sı ile `OpenClaw Release Checks` iş akışını ayrıca çalıştırın
   - Bu ayrım bilinçlidir; böylece canlı kapsam kullanılabilir kalır ve
     uzun süren veya kararsız kontroller yayımlama iş akışına yeniden bağlanmaz
4. Başarılı `preflight_run_id` değerini kaydedin
5. `preflight_only=false`, aynı
   `tag`, aynı `npm_dist_tag` ve kaydedilmiş `preflight_run_id` ile `OpenClaw NPM Release`’i yeniden çalıştırın
6. Sürüm `beta`’ya gittiyse, daha sonra aynı
   stable `tag`, `promote_beta_to_latest=true`, `preflight_only=false`,
   boş `preflight_run_id` ve `npm_dist_tag=beta` ile `OpenClaw NPM Release` çalıştırarak bu yayımlanmış
   derlemeyi `latest`’e taşıyabilirsiniz
7. Sürüm bilerek doğrudan `latest`’e yayımlandıysa ve `beta`
   aynı stable derlemeyi takip etmeliyse, aynı
   stable `tag`, `sync_stable_dist_tags=true`, `promote_beta_to_latest=false`,
   `preflight_only=false`, boş `preflight_run_id` ve `npm_dist_tag=latest` ile `OpenClaw NPM Release` çalıştırın

Öne çıkarma ve dist-tag eşitleme modları yine de `npm-release`
ortam onayı ve bu iş akışı çalışmasına erişebilen geçerli bir `NPM_TOKEN` gerektirir.

Bu, doğrudan yayımlama yolunu ve beta-önce öne çıkarma yolunu hem
belgelenmiş hem de operatör açısından görünür tutar.

## Herkese açık başvurular

- [`.github/workflows/openclaw-npm-release.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-npm-release.yml)
- [`.github/workflows/openclaw-release-checks.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-release-checks.yml)
- [`scripts/openclaw-npm-release-check.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/openclaw-npm-release-check.ts)
- [`scripts/package-mac-dist.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-dist.sh)
- [`scripts/make_appcast.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/make_appcast.sh)

Maintainers, gerçek çalışma kılavuzu için özel sürüm belgelerini
[`openclaw/maintainers/release/README.md`](https://github.com/openclaw/maintainers/blob/main/release/README.md)
içinde kullanır.
