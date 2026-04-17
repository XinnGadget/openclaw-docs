---
read_when:
    - OpenClaw’ı Ollama üzerinden bulut veya yerel modellerle çalıştırmak istiyorsunuz
    - Ollama kurulum ve yapılandırma rehberine ihtiyacınız var
summary: OpenClaw’ı Ollama ile çalıştırın (bulut ve yerel modeller)
title: Ollama
x-i18n:
    generated_at: "2026-04-15T14:40:56Z"
    model: gpt-5.4
    provider: openai
    source_hash: 098e083e0fc484bddb5270eb630c55d7832039b462d1710372b6afece5cefcdf
    source_path: providers/ollama.md
    workflow: 15
---

# Ollama

OpenClaw, barındırılan bulut modelleri ve yerel/kendi barındırdığınız Ollama sunucuları için Ollama’nın yerel API’si (`/api/chat`) ile entegre olur. Ollama’yı üç modda kullanabilirsiniz: erişilebilir bir Ollama ana makinesi üzerinden `Bulut + Yerel`, `https://ollama.com` karşısında `Yalnızca Bulut` veya erişilebilir bir Ollama ana makinesi karşısında `Yalnızca Yerel`.

<Warning>
**Uzak Ollama kullanıcıları**: OpenClaw ile `/v1` OpenAI uyumlu URL’yi (`http://host:11434/v1`) kullanmayın. Bu, araç çağırmayı bozar ve modeller ham araç JSON’unu düz metin olarak çıkarabilir. Bunun yerine yerel Ollama API URL’sini kullanın: `baseUrl: "http://host:11434"` (`/v1` olmadan).
</Warning>

## Başlarken

Tercih ettiğiniz kurulum yöntemini ve modu seçin.

<Tabs>
  <Tab title="İlk kurulum (önerilen)">
    **Şunun için en iyisi:** çalışan bir Ollama bulut veya yerel kurulumuna en hızlı yol.

    <Steps>
      <Step title="İlk kurulumu çalıştırın">
        ```bash
        openclaw onboard
        ```

        Sağlayıcı listesinden **Ollama** seçin.
      </Step>
      <Step title="Modunuzu seçin">
        - **Bulut + Yerel** — yerel Ollama ana makinesi artı bu ana makine üzerinden yönlendirilen bulut modelleri
        - **Yalnızca Bulut** — `https://ollama.com` üzerinden barındırılan Ollama modelleri
        - **Yalnızca Yerel** — yalnızca yerel modeller
      </Step>
      <Step title="Bir model seçin">
        `Yalnızca Bulut`, `OLLAMA_API_KEY` ister ve barındırılan bulut varsayılanlarını önerir. `Bulut + Yerel` ve `Yalnızca Yerel`, bir Ollama temel URL’si ister, kullanılabilir modelleri keşfeder ve seçilen yerel model henüz mevcut değilse bunu otomatik olarak çeker. `Bulut + Yerel`, ayrıca o Ollama ana makinesinin bulut erişimi için oturum açıp açmadığını da denetler.
      </Step>
      <Step title="Modelin kullanılabilir olduğunu doğrulayın">
        ```bash
        openclaw models list --provider ollama
        ```
      </Step>
    </Steps>

    ### Etkileşimsiz mod

    ```bash
    openclaw onboard --non-interactive \
      --auth-choice ollama \
      --accept-risk
    ```

    İsteğe bağlı olarak özel bir temel URL veya model belirtebilirsiniz:

    ```bash
    openclaw onboard --non-interactive \
      --auth-choice ollama \
      --custom-base-url "http://ollama-host:11434" \
      --custom-model-id "qwen3.5:27b" \
      --accept-risk
    ```

  </Tab>

  <Tab title="Elle kurulum">
    **Şunun için en iyisi:** bulut veya yerel kurulum üzerinde tam denetim.

    <Steps>
      <Step title="Bulut veya yereli seçin">
        - **Bulut + Yerel**: Ollama’yı kurun, `ollama signin` ile oturum açın ve bulut isteklerini bu ana makine üzerinden yönlendirin
        - **Yalnızca Bulut**: `https://ollama.com` adresini bir `OLLAMA_API_KEY` ile kullanın
        - **Yalnızca Yerel**: Ollama’yı [ollama.com/download](https://ollama.com/download) adresinden kurun
      </Step>
      <Step title="Yerel bir modeli çekin (yalnızca yerel)">
        ```bash
        ollama pull gemma4
        # veya
        ollama pull gpt-oss:20b
        # veya
        ollama pull llama3.3
        ```
      </Step>
      <Step title="OpenClaw için Ollama’yı etkinleştirin">
        `Yalnızca Bulut` için gerçek `OLLAMA_API_KEY` değerinizi kullanın. Ana makine destekli kurulumlarda herhangi bir yer tutucu değer işe yarar:

        ```bash
        # Bulut
        export OLLAMA_API_KEY="your-ollama-api-key"

        # Yalnızca yerel
        export OLLAMA_API_KEY="ollama-local"

        # Veya yapılandırma dosyanızda yapılandırın
        openclaw config set models.providers.ollama.apiKey "OLLAMA_API_KEY"
        ```
      </Step>
      <Step title="Modelinizi inceleyin ve ayarlayın">
        ```bash
        openclaw models list
        openclaw models set ollama/gemma4
        ```

        Veya varsayılanı yapılandırmada ayarlayın:

        ```json5
        {
          agents: {
            defaults: {
              model: { primary: "ollama/gemma4" },
            },
          },
        }
        ```
      </Step>
    </Steps>

  </Tab>
</Tabs>

## Bulut modelleri

<Tabs>
  <Tab title="Bulut + Yerel">
    `Bulut + Yerel`, hem yerel hem de bulut modelleri için denetim noktası olarak erişilebilir bir Ollama ana makinesi kullanır. Bu, Ollama’nın tercih ettiği hibrit akıştır.

    Kurulum sırasında **Bulut + Yerel** seçeneğini kullanın. OpenClaw, Ollama temel URL’sini ister, o ana makineden yerel modelleri keşfeder ve ana makinenin `ollama signin` ile bulut erişimi için oturum açıp açmadığını denetler. Ana makine oturum açmışsa OpenClaw ayrıca `kimi-k2.5:cloud`, `minimax-m2.7:cloud` ve `glm-5.1:cloud` gibi barındırılan bulut varsayılanlarını da önerir.

    Ana makine henüz oturum açmadıysa OpenClaw, siz `ollama signin` çalıştırana kadar kurulumu yalnızca yerel olarak tutar.

  </Tab>

  <Tab title="Yalnızca Bulut">
    `Yalnızca Bulut`, Ollama’nın `https://ollama.com` adresindeki barındırılan API’sine karşı çalışır.

    Kurulum sırasında **Yalnızca Bulut** seçeneğini kullanın. OpenClaw, `OLLAMA_API_KEY` ister, `baseUrl: "https://ollama.com"` ayarlar ve barındırılan bulut model listesini tohumlar. Bu yol, yerel bir Ollama sunucusu veya `ollama signin` gerektirmez.

  </Tab>

  <Tab title="Yalnızca Yerel">
    Yalnızca yerel modda OpenClaw, yapılandırılmış Ollama örneğinden modelleri keşfeder. Bu yol, yerel veya kendi barındırdığınız Ollama sunucuları içindir.

    OpenClaw şu anda yerel varsayılan olarak `gemma4` önerir.

  </Tab>
</Tabs>

## Model keşfi (örtük sağlayıcı)

`OLLAMA_API_KEY` (veya bir auth profili) ayarladığınızda ve `models.providers.ollama` tanımlamadığınızda, OpenClaw modelleri `http://127.0.0.1:11434` adresindeki yerel Ollama örneğinden keşfeder.

| Davranış             | Ayrıntı                                                                                                                                                             |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Katalog sorgusu      | `/api/tags` sorgulanır                                                                                                                                              |
| Yetenek algılama     | `contextWindow` değerini okumak ve yetenekleri (vision dahil) algılamak için en iyi çabayla `/api/show` aramaları kullanır                                        |
| Vision modelleri     | `/api/show` tarafından bildirilen `vision` yeteneğine sahip modeller görüntü destekli olarak işaretlenir (`input: ["text", "image"]`), böylece OpenClaw görüntüleri isteme otomatik ekler |
| Akıl yürütme algılama | Model adı kestirimiyle `reasoning` işaretlenir (`r1`, `reasoning`, `think`)                                                                                        |
| Token sınırları      | `maxTokens`, OpenClaw tarafından kullanılan varsayılan Ollama en yüksek token sınırına ayarlanır                                                                   |
| Maliyetler           | Tüm maliyetler `0` olarak ayarlanır                                                                                                                                 |

Bu, kataloğu yerel Ollama örneğiyle uyumlu tutarken elle model girişi yapmaktan kaçınır.

```bash
# Hangi modellerin kullanılabilir olduğunu görün
ollama list
openclaw models list
```

Yeni bir model eklemek için bunu Ollama ile çekmeniz yeterlidir:

```bash
ollama pull mistral
```

Yeni model otomatik olarak keşfedilir ve kullanıma sunulur.

<Note>
`models.providers.ollama` değerini açıkça ayarlarsanız otomatik keşif atlanır ve modelleri elle tanımlamanız gerekir. Aşağıdaki açık yapılandırma bölümüne bakın.
</Note>

## Yapılandırma

<Tabs>
  <Tab title="Temel (örtük keşif)">
    En basit yalnızca yerel etkinleştirme yolu ortam değişkeni kullanmaktır:

    ```bash
    export OLLAMA_API_KEY="ollama-local"
    ```

    <Tip>
    `OLLAMA_API_KEY` ayarlıysa, sağlayıcı girişinde `apiKey` değerini atlayabilirsiniz ve OpenClaw bunu kullanılabilirlik denetimleri için doldurur.
    </Tip>

  </Tab>

  <Tab title="Açık (elle modeller)">
    Barındırılan bulut kurulumu istediğinizde, Ollama başka bir ana makinede/bağlantı noktasında çalıştığında, belirli bağlam pencerelerini veya model listelerini zorlamak istediğinizde ya da tamamen elle model tanımları istediğinizde açık yapılandırmayı kullanın.

    ```json5
    {
      models: {
        providers: {
          ollama: {
            baseUrl: "https://ollama.com",
            apiKey: "OLLAMA_API_KEY",
            api: "ollama",
            models: [
              {
                id: "kimi-k2.5:cloud",
                name: "kimi-k2.5:cloud",
                reasoning: false,
                input: ["text", "image"],
                cost: { input: 0, output: 0, cacheRead: 0, cacheWrite: 0 },
                contextWindow: 128000,
                maxTokens: 8192
              }
            ]
          }
        }
      }
    }
    ```

  </Tab>

  <Tab title="Özel temel URL">
    Ollama farklı bir ana makinede veya bağlantı noktasında çalışıyorsa (açık yapılandırma otomatik keşfi devre dışı bırakır, bu yüzden modelleri elle tanımlayın):

    ```json5
    {
      models: {
        providers: {
          ollama: {
            apiKey: "ollama-local",
            baseUrl: "http://ollama-host:11434", // /v1 yok - yerel Ollama API URL’sini kullanın
            api: "ollama", // Yerel araç çağırma davranışını garanti etmek için açıkça ayarlayın
          },
        },
      },
    }
    ```

    <Warning>
    URL’ye `/v1` eklemeyin. `/v1` yolu, araç çağırmanın güvenilir olmadığı OpenAI uyumlu modu kullanır. Yol son eki olmadan temel Ollama URL’sini kullanın.
    </Warning>

  </Tab>
</Tabs>

### Model seçimi

Yapılandırıldıktan sonra tüm Ollama modelleriniz kullanılabilir olur:

```json5
{
  agents: {
    defaults: {
      model: {
        primary: "ollama/gpt-oss:20b",
        fallbacks: ["ollama/llama3.3", "ollama/qwen2.5-coder:32b"],
      },
    },
  },
}
```

## Ollama Web Search

OpenClaw, paketlenmiş bir `web_search` sağlayıcısı olarak **Ollama Web Search** destekler.

| Özellik    | Ayrıntı                                                                                                            |
| ----------- | ----------------------------------------------------------------------------------------------------------------- |
| Ana makine  | Yapılandırılmış Ollama ana makinenizi kullanır (`models.providers.ollama.baseUrl` ayarlıysa o, aksi takdirde `http://127.0.0.1:11434`) |
| Kimlik doğrulama | Anahtarsız                                                                                                  |
| Gereksinim | Ollama çalışıyor olmalı ve `ollama signin` ile oturum açılmış olmalı                                              |

`openclaw onboard` veya `openclaw configure --section web` sırasında **Ollama Web Search** seçin ya da şunu ayarlayın:

```json5
{
  tools: {
    web: {
      search: {
        provider: "ollama",
      },
    },
  },
}
```

<Note>
Tam kurulum ve davranış ayrıntıları için [Ollama Web Search](/tr/tools/ollama-search) bölümüne bakın.
</Note>

## Gelişmiş yapılandırma

<AccordionGroup>
  <Accordion title="Eski OpenAI uyumlu mod">
    <Warning>
    **Araç çağırma, OpenAI uyumlu modda güvenilir değildir.** Bu modu yalnızca bir proxy için OpenAI biçimine ihtiyaç duyuyorsanız ve yerel araç çağırma davranışına bağımlı değilseniz kullanın.
    </Warning>

    Bunun yerine OpenAI uyumlu uç noktayı kullanmanız gerekiyorsa (örneğin yalnızca OpenAI biçimini destekleyen bir proxy’nin arkasında), `api: "openai-completions"` değerini açıkça ayarlayın:

    ```json5
    {
      models: {
        providers: {
          ollama: {
            baseUrl: "http://ollama-host:11434/v1",
            api: "openai-completions",
            injectNumCtxForOpenAICompat: true, // varsayılan: true
            apiKey: "ollama-local",
            models: [...]
          }
        }
      }
    }
    ```

    Bu mod akış ve araç çağırmayı aynı anda desteklemeyebilir. Model yapılandırmasında `params: { streaming: false }` ile akışı devre dışı bırakmanız gerekebilir.

    `api: "openai-completions"` Ollama ile kullanıldığında OpenClaw, Ollama’nın sessizce 4096 bağlam penceresine geri dönmemesi için varsayılan olarak `options.num_ctx` ekler. Proxy’niz/yukarı akışınız bilinmeyen `options` alanlarını reddediyorsa bu davranışı devre dışı bırakın:

    ```json5
    {
      models: {
        providers: {
          ollama: {
            baseUrl: "http://ollama-host:11434/v1",
            api: "openai-completions",
            injectNumCtxForOpenAICompat: false,
            apiKey: "ollama-local",
            models: [...]
          }
        }
      }
    }
    ```

  </Accordion>

  <Accordion title="Bağlam pencereleri">
    Otomatik olarak keşfedilen modeller için OpenClaw, varsa Ollama tarafından bildirilen bağlam penceresini kullanır; aksi takdirde OpenClaw tarafından kullanılan varsayılan Ollama bağlam penceresine geri döner.

    `contextWindow` ve `maxTokens` değerlerini açık sağlayıcı yapılandırmasında geçersiz kılabilirsiniz:

    ```json5
    {
      models: {
        providers: {
          ollama: {
            models: [
              {
                id: "llama3.3",
                contextWindow: 131072,
                maxTokens: 65536,
              }
            ]
          }
        }
      }
    }
    ```

  </Accordion>

  <Accordion title="Akıl yürütme modelleri">
    OpenClaw, varsayılan olarak `deepseek-r1`, `reasoning` veya `think` gibi adlara sahip modelleri akıl yürütme yetenekli olarak kabul eder.

    ```bash
    ollama pull deepseek-r1:32b
    ```

    Ek yapılandırma gerekmez -- OpenClaw bunları otomatik olarak işaretler.

  </Accordion>

  <Accordion title="Model maliyetleri">
    Ollama ücretsizdir ve yerelde çalışır, bu nedenle tüm model maliyetleri $0 olarak ayarlanır. Bu, hem otomatik olarak keşfedilen hem de elle tanımlanan modeller için geçerlidir.
  </Accordion>

  <Accordion title="Bellek gömmeleri">
    Paketlenmiş Ollama Plugin, [bellek araması](/tr/concepts/memory) için bir bellek gömme sağlayıcısı kaydeder. Yapılandırılmış Ollama temel URL’sini ve API anahtarını kullanır.

    | Özellik       | Değer               |
    | ------------- | ------------------- |
    | Varsayılan model | `nomic-embed-text`  |
    | Otomatik çekme | Evet — gömme modeli yerelde mevcut değilse otomatik olarak çekilir |

    Ollama’yı bellek arama gömme sağlayıcısı olarak seçmek için:

    ```json5
    {
      agents: {
        defaults: {
          memorySearch: { provider: "ollama" },
        },
      },
    }
    ```

  </Accordion>

  <Accordion title="Akış yapılandırması">
    OpenClaw’ın Ollama entegrasyonu varsayılan olarak **yerel Ollama API’sini** (`/api/chat`) kullanır; bu, akış ve araç çağırmayı aynı anda tam olarak destekler. Özel bir yapılandırma gerekmez.

    <Tip>
    OpenAI uyumlu uç noktayı kullanmanız gerekiyorsa yukarıdaki "Eski OpenAI uyumlu mod" bölümüne bakın. Bu modda akış ve araç çağırma aynı anda çalışmayabilir.
    </Tip>

  </Accordion>
</AccordionGroup>

## Sorun giderme

<AccordionGroup>
  <Accordion title="Ollama algılanmadı">
    Ollama’nın çalıştığından, `OLLAMA_API_KEY` (veya bir auth profili) ayarladığınızdan ve açık bir `models.providers.ollama` girdisi tanımlamadığınızdan emin olun:

    ```bash
    ollama serve
    ```

    API’nin erişilebilir olduğunu doğrulayın:

    ```bash
    curl http://localhost:11434/api/tags
    ```

  </Accordion>

  <Accordion title="Kullanılabilir model yok">
    Modeliniz listelenmiyorsa modeli ya yerelde çekin ya da `models.providers.ollama` içinde açıkça tanımlayın.

    ```bash
    ollama list  # Kurulu olanları görün
    ollama pull gemma4
    ollama pull gpt-oss:20b
    ollama pull llama3.3     # Veya başka bir model
    ```

  </Accordion>

  <Accordion title="Bağlantı reddedildi">
    Ollama’nın doğru bağlantı noktasında çalıştığını denetleyin:

    ```bash
    # Ollama’nın çalışıp çalışmadığını denetleyin
    ps aux | grep ollama

    # Veya Ollama’yı yeniden başlatın
    ollama serve
    ```

  </Accordion>
</AccordionGroup>

<Note>
Daha fazla yardım: [Sorun giderme](/tr/help/troubleshooting) ve [SSS](/tr/help/faq).
</Note>

## İlgili

<CardGroup cols={2}>
  <Card title="Model sağlayıcıları" href="/tr/concepts/model-providers" icon="layers">
    Tüm sağlayıcılara, model başvurularına ve yük devretme davranışına genel bakış.
  </Card>
  <Card title="Model seçimi" href="/tr/concepts/models" icon="brain">
    Modellerin nasıl seçileceği ve yapılandırılacağı.
  </Card>
  <Card title="Ollama Web Search" href="/tr/tools/ollama-search" icon="magnifying-glass">
    Ollama destekli web araması için tam kurulum ve davranış ayrıntıları.
  </Card>
  <Card title="Yapılandırma" href="/tr/gateway/configuration" icon="gear">
    Tam yapılandırma başvurusu.
  </Card>
</CardGroup>
