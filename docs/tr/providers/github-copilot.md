---
read_when:
    - GitHub Copilot’u bir model sağlayıcısı olarak kullanmak istiyorsunuz
    - '`openclaw models auth login-github-copilot` akışına ihtiyacınız var'
summary: Cihaz akışını kullanarak OpenClaw içinden GitHub Copilot'ta oturum açın
title: GitHub Copilot
x-i18n:
    generated_at: "2026-04-15T14:40:31Z"
    model: gpt-5.4
    provider: openai
    source_hash: b8258fecff22fb73b057de878462941f6eb86d0c5f775c5eac4840e95ba5eccf
    source_path: providers/github-copilot.md
    workflow: 15
---

# GitHub Copilot

GitHub Copilot, GitHub'ın yapay zeka destekli kodlama yardımcısıdır. GitHub hesabınız ve planınız için Copilot modellerine erişim sağlar. OpenClaw, Copilot’u iki farklı şekilde bir model sağlayıcısı olarak kullanabilir.

## OpenClaw içinde Copilot kullanmanın iki yolu

<Tabs>
  <Tab title="Yerleşik sağlayıcı (github-copilot)">
    Bir GitHub token’ı almak için yerel cihaz oturum açma akışını kullanın, ardından OpenClaw çalıştığında bunu Copilot API token’larıyla değiştirin. Bu **varsayılan** ve en basit yoldur çünkü VS Code gerektirmez.

    <Steps>
      <Step title="Oturum açma komutunu çalıştırın">
        ```bash
        openclaw models auth login-github-copilot
        ```

        Bir URL’yi ziyaret etmeniz ve tek kullanımlık bir kod girmeniz istenir. İşlem tamamlanana kadar terminali açık tutun.
      </Step>
      <Step title="Varsayılan bir model ayarlayın">
        ```bash
        openclaw models set github-copilot/gpt-4o
        ```

        Veya yapılandırmada:

        ```json5
        {
          agents: { defaults: { model: { primary: "github-copilot/gpt-4o" } } },
        }
        ```
      </Step>
    </Steps>

  </Tab>

  <Tab title="Copilot Proxy Plugin (copilot-proxy)">
    Yerel bir köprü olarak **Copilot Proxy** VS Code uzantısını kullanın. OpenClaw, proxy’nin `/v1` uç noktasıyla konuşur ve orada yapılandırdığınız model listesini kullanır.

    <Note>
    Bunu, VS Code içinde zaten Copilot Proxy çalıştırıyorsanız veya trafiği onun üzerinden yönlendirmeniz gerekiyorsa seçin. Plugin’i etkinleştirmeniz ve VS Code uzantısını çalışır durumda tutmanız gerekir.
    </Note>

  </Tab>
</Tabs>

## İsteğe bağlı bayraklar

| Bayrak          | Açıklama                                          |
| --------------- | ------------------------------------------------- |
| `--yes`         | Onay istemini atla                                |
| `--set-default` | Sağlayıcının önerilen varsayılan modelini de uygula |

```bash
# Onayı atla
openclaw models auth login-github-copilot --yes

# Oturum aç ve varsayılan modeli tek adımda ayarla
openclaw models auth login --provider github-copilot --method device --set-default
```

<AccordionGroup>
  <Accordion title="Etkileşimli TTY gerekir">
    Cihazla oturum açma akışı etkileşimli bir TTY gerektirir. Bunu etkileşimsiz bir betikte veya CI işlem hattında değil, doğrudan bir terminalde çalıştırın.
  </Accordion>

  <Accordion title="Model kullanılabilirliği planınıza bağlıdır">
    Copilot model kullanılabilirliği GitHub planınıza bağlıdır. Bir model reddedilirse başka bir kimlik deneyin (örneğin `github-copilot/gpt-4.1`).
  </Accordion>

  <Accordion title="Taşıma seçimi">
    Claude model kimlikleri Anthropic Messages taşımasını otomatik olarak kullanır. GPT, o-series ve Gemini modelleri OpenAI Responses taşımasını kullanmaya devam eder. OpenClaw, model başvurusuna göre doğru taşıma türünü seçer.
  </Accordion>

  <Accordion title="Ortam değişkeni çözümleme sırası">
    OpenClaw, Copilot kimlik doğrulamasını aşağıdaki öncelik sırasına göre ortam değişkenlerinden çözümler:

    | Öncelik | Değişken              | Notlar                             |
    | -------- | --------------------- | ---------------------------------- |
    | 1        | `COPILOT_GITHUB_TOKEN` | En yüksek öncelik, Copilot’a özel |
    | 2        | `GH_TOKEN`            | GitHub CLI token’ı (yedek)         |
    | 3        | `GITHUB_TOKEN`        | Standart GitHub token’ı (en düşük) |

    Birden fazla değişken ayarlandığında OpenClaw en yüksek öncelikli olanı kullanır.
    Cihazla oturum açma akışı (`openclaw models auth login-github-copilot`), token’ını auth profil deposunda saklar ve tüm ortam değişkenlerinden önceliklidir.

  </Accordion>

  <Accordion title="Token depolama">
    Oturum açma işlemi bir GitHub token’ını auth profil deposunda saklar ve OpenClaw çalıştığında bunu bir Copilot API token’ı ile değiştirir. Token’ı elle yönetmeniz gerekmez.
  </Accordion>
</AccordionGroup>

<Warning>
Etkileşimli bir TTY gerekir. Oturum açma komutunu headless bir betik veya CI işi içinde değil, doğrudan bir terminalde çalıştırın.
</Warning>

## Bellek arama gömmeleri

GitHub Copilot, [bellek araması](/tr/concepts/memory-search) için bir gömme sağlayıcısı olarak da kullanılabilir. Bir Copilot aboneliğiniz varsa ve oturum açtıysanız OpenClaw, ayrı bir API anahtarı olmadan bunu gömmeler için kullanabilir.

### Otomatik algılama

`memorySearch.provider` değeri `"auto"` olduğunda (varsayılan), GitHub Copilot öncelik 15 ile denenir -- yerel gömmelerden sonra, ancak OpenAI ve diğer ücretli sağlayıcılardan önce. Bir GitHub token’ı mevcutsa OpenClaw, Copilot API’sinden kullanılabilir gömme modellerini keşfeder ve en iyisini otomatik olarak seçer.

### Açık yapılandırma

```json5
{
  agents: {
    defaults: {
      memorySearch: {
        provider: "github-copilot",
        // İsteğe bağlı: otomatik keşfedilen modeli geçersiz kıl
        model: "text-embedding-3-small",
      },
    },
  },
}
```

### Nasıl çalışır

1. OpenClaw GitHub token’ınızı çözümler (ortam değişkenlerinden veya auth profilinden).
2. Bunu kısa ömürlü bir Copilot API token’ı ile değiştirir.
3. Kullanılabilir gömme modellerini keşfetmek için Copilot `/models` uç noktasını sorgular.
4. En iyi modeli seçer (`text-embedding-3-small` tercih edilir).
5. Gömme isteklerini Copilot `/embeddings` uç noktasına gönderir.

Model kullanılabilirliği GitHub planınıza bağlıdır. Hiç gömme modeli yoksa OpenClaw, Copilot’u atlar ve bir sonraki sağlayıcıyı dener.

## İlgili

<CardGroup cols={2}>
  <Card title="Model seçimi" href="/tr/concepts/model-providers" icon="layers">
    Sağlayıcıları, model başvurularını ve yük devretme davranışını seçme.
  </Card>
  <Card title="OAuth ve kimlik doğrulama" href="/tr/gateway/authentication" icon="key">
    Kimlik doğrulama ayrıntıları ve kimlik bilgisi yeniden kullanım kuralları.
  </Card>
</CardGroup>
