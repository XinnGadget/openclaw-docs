---
read_when: You hit 'sandbox jail' or see a tool/elevated refusal and want the exact config key to change.
status: active
summary: 'Bir aracın neden engellendiği: sandbox çalışma zamanı, araç izin/engelleme ilkesi ve elevated exec kapıları'
title: Sandbox ve Araç İlkesi ve Elevated
x-i18n:
    generated_at: "2026-04-06T03:07:39Z"
    model: gpt-5.4
    provider: openai
    source_hash: 331f5b2f0d5effa1320125d9f29948e16d0deaffa59eb1e4f25a63481cbe22d6
    source_path: gateway/sandbox-vs-tool-policy-vs-elevated.md
    workflow: 15
---

# Sandbox ve Araç İlkesi ve Elevated

OpenClaw’un birbiriyle ilişkili olan (ama farklı) üç denetimi vardır:

1. **Sandbox** (`agents.defaults.sandbox.*` / `agents.list[].sandbox.*`), **araçların nerede çalıştığına** karar verir (Docker veya host).
2. **Araç ilkesi** (`tools.*`, `tools.sandbox.tools.*`, `agents.list[].tools.*`), **hangi araçların kullanılabilir/izinli olduğuna** karar verir.
3. **Elevated** (`tools.elevated.*`, `agents.list[].tools.elevated.*`), sandbox içindeyken (`gateway` varsayılan olarak veya exec hedefi `node` olarak yapılandırılmışsa `node`) sandbox dışında çalıştırmak için **yalnızca exec’e özel bir kaçış kapağıdır**.

## Hızlı hata ayıklama

OpenClaw’un _gerçekte_ ne yaptığını görmek için denetleyiciyi kullanın:

```bash
openclaw sandbox explain
openclaw sandbox explain --session agent:main:main
openclaw sandbox explain --agent work
openclaw sandbox explain --json
```

Şunları yazdırır:

- etkin sandbox modu/kapsamı/çalışma alanı erişimi
- oturumun şu anda sandbox içinde olup olmadığı (main ve non-main)
- etkin sandbox araç izin/engellemesi (ve bunun agent/global/default kaynağından gelip gelmediği)
- elevated kapıları ve düzeltme için anahtar yolları

## Sandbox: araçların nerede çalıştığı

Sandboxing, `agents.defaults.sandbox.mode` ile denetlenir:

- `"off"`: her şey host üzerinde çalışır.
- `"non-main"`: yalnızca non-main oturumlar sandbox içindedir (gruplar/kanallar için yaygın “sürpriz”).
- `"all"`: her şey sandbox içindedir.

Tam matris için bkz. [Sandboxing](/tr/gateway/sandboxing) (kapsam, çalışma alanı mount’ları, görseller).

### Bind mount’lar (hızlı güvenlik kontrolü)

- `docker.binds`, sandbox dosya sistemini _deler_: mount ettiğiniz her şey, belirlediğiniz kipte (`:ro` veya `:rw`) kapsayıcı içinde görünür olur.
- Kipi belirtmezseniz varsayılan okuma-yazmadır; kaynak kod/gizli veriler için `:ro` tercih edin.
- `scope: "shared"`, agent başına bind’ları yok sayar (yalnızca global bind’lar uygulanır).
- OpenClaw bind kaynaklarını iki kez doğrular: önce normalize edilmiş kaynak yolunda, sonra da en derin mevcut üst öğe üzerinden çözümledikten sonra yeniden. Symlink üst öğesi üzerinden kaçışlar, engellenmiş-yol veya izinli-kök denetimlerini atlatamaz.
- Var olmayan yaprak yollar yine de güvenli şekilde denetlenir. `/workspace/alias-out/new-file`, symlink’lenmiş bir üst öğe üzerinden engellenmiş bir yola veya yapılandırılmış izinli köklerin dışına çözülüyorsa bind reddedilir.
- `/var/run/docker.sock` bağlamak, fiilen host denetimini sandbox’a verir; bunu yalnızca bilinçli olarak yapın.
- Çalışma alanı erişimi (`workspaceAccess: "ro"`/`"rw"`), bind kiplerinden bağımsızdır.

## Araç ilkesi: hangi araçlar vardır/çağrılabilir

İki katman önemlidir:

- **Araç profili**: `tools.profile` ve `agents.list[].tools.profile` (temel izin listesi)
- **Sağlayıcı araç profili**: `tools.byProvider[provider].profile` ve `agents.list[].tools.byProvider[provider].profile`
- **Global/agent başına araç ilkesi**: `tools.allow`/`tools.deny` ve `agents.list[].tools.allow`/`agents.list[].tools.deny`
- **Sağlayıcı araç ilkesi**: `tools.byProvider[provider].allow/deny` ve `agents.list[].tools.byProvider[provider].allow/deny`
- **Sandbox araç ilkesi** (yalnızca sandbox içindeyken uygulanır): `tools.sandbox.tools.allow`/`tools.sandbox.tools.deny` ve `agents.list[].tools.sandbox.tools.*`

Temel kurallar:

- `deny` her zaman kazanır.
- `allow` boş değilse, diğer her şey engellenmiş kabul edilir.
- Araç ilkesi kesin durdurmadır: `/exec`, reddedilmiş bir `exec` aracını geçersiz kılamaz.
- `/exec`, yalnızca yetkili göndericiler için oturum varsayılanlarını değiştirir; araç erişimi vermez.
  Sağlayıcı araç anahtarları `provider` (ör. `google-antigravity`) veya `provider/model` (ör. `openai/gpt-5.4`) kabul eder.

### Araç grupları (kısa yollar)

Araç ilkeleri (global, agent, sandbox), birden fazla araca açılan `group:*` girdilerini destekler:

```json5
{
  tools: {
    sandbox: {
      tools: {
        allow: ["group:runtime", "group:fs", "group:sessions", "group:memory"],
      },
    },
  },
}
```

Kullanılabilir gruplar:

- `group:runtime`: `exec`, `process`, `code_execution` (`bash`, `exec` için bir takma ad olarak kabul edilir)
- `group:fs`: `read`, `write`, `edit`, `apply_patch`
- `group:sessions`: `sessions_list`, `sessions_history`, `sessions_send`, `sessions_spawn`, `sessions_yield`, `subagents`, `session_status`
- `group:memory`: `memory_search`, `memory_get`
- `group:web`: `web_search`, `x_search`, `web_fetch`
- `group:ui`: `browser`, `canvas`
- `group:automation`: `cron`, `gateway`
- `group:messaging`: `message`
- `group:nodes`: `nodes`
- `group:agents`: `agents_list`
- `group:media`: `image`, `image_generate`, `video_generate`, `tts`
- `group:openclaw`: tüm yerleşik OpenClaw araçları (sağlayıcı plugin’leri hariç)

## Elevated: yalnızca exec için "host üzerinde çalıştır"

Elevated, ek araçlar vermez; yalnızca `exec` üzerinde etkisi vardır.

- Sandbox içindeyseniz, `/elevated on` (veya `elevated: true` ile `exec`) sandbox dışında çalıştırır (onaylar yine de geçerli olabilir).
- Oturum için exec onaylarını atlamak üzere `/elevated full` kullanın.
- Zaten doğrudan çalışıyorsanız elevated fiilen etkisizdir (yine de kapılar uygulanır).
- Elevated, **skill kapsamlı değildir** ve araç izin/engellemesini geçersiz kılmaz.
- Elevated, `host=auto` içinden keyfi çapraz-host geçersiz kılmaları vermez; normal exec hedef kurallarını izler ve yalnızca yapılandırılmış/oturum hedefi zaten `node` ise `node`’u korur.
- `/exec`, elevated’dan ayrıdır. Yalnızca yetkili göndericiler için oturum başına exec varsayılanlarını ayarlar.

Kapılar:

- Etkinleştirme: `tools.elevated.enabled` (ve isteğe bağlı olarak `agents.list[].tools.elevated.enabled`)
- Gönderici izin listeleri: `tools.elevated.allowFrom.<provider>` (ve isteğe bağlı olarak `agents.list[].tools.elevated.allowFrom.<provider>`)

Bkz. [Elevated Mode](/tr/tools/elevated).

## Yaygın "sandbox jail" düzeltmeleri

### "Tool X blocked by sandbox tool policy"

Düzeltme anahtarları (birini seçin):

- Sandbox’ı devre dışı bırakın: `agents.defaults.sandbox.mode=off` (veya agent başına `agents.list[].sandbox.mode=off`)
- Araca sandbox içinde izin verin:
  - `tools.sandbox.tools.deny` içinden kaldırın (veya agent başına `agents.list[].tools.sandbox.tools.deny`)
  - veya `tools.sandbox.tools.allow` içine ekleyin (veya agent başına allow)

### "Bunun main olduğunu sanıyordum, neden sandbox içinde?"

`"non-main"` kipinde grup/kanal anahtarları _main_ değildir. Main oturum anahtarını kullanın (`sandbox explain` tarafından gösterilir) veya kipi `"off"` olarak değiştirin.

## Ayrıca bkz.

- [Sandboxing](/tr/gateway/sandboxing) -- tam sandbox başvurusu (kipler, kapsamlar, arka uçlar, görseller)
- [Multi-Agent Sandbox & Tools](/tr/tools/multi-agent-sandbox-tools) -- agent başına geçersiz kılmalar ve öncelik
- [Elevated Mode](/tr/tools/elevated)
