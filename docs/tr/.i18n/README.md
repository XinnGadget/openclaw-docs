---
x-i18n:
    generated_at: "2026-04-06T03:05:54Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6e1cf417b0c04d001bc494fbe03ac2fcb66866f759e21646dbfd1a9c3a968bff
    source_path: .i18n/README.md
    workflow: 15
---

# OpenClaw belge i18n varlıkları

Bu klasör, kaynak belge deposu için çeviri yapılandırmasını depolar.

Oluşturulan yerel ayar sayfaları ve canlı yerel ayar çeviri belleği artık yayın deposunda bulunur (`openclaw/docs`, yerel kardeş checkout `~/Projects/openclaw-docs`).

## Dosyalar

- `glossary.<lang>.json` — tercih edilen terim eşlemeleri (istem yönlendirmesinde kullanılır).
- `<lang>.tm.jsonl` — iş akışı + model + metin karmasına göre anahtarlanan çeviri belleği (önbellek). Bu depoda, yerel ayar TM dosyaları gerektiğinde oluşturulur.

## Sözlük biçimi

`glossary.<lang>.json`, girişlerden oluşan bir dizidir:

```json
{
  "source": "troubleshooting",
  "target": "故障排除",
  "ignore_case": true,
  "whole_word": false
}
```

Alanlar:

- `source`: tercih edilecek İngilizce (veya kaynak) ifade.
- `target`: tercih edilen çeviri çıktısı.

## Notlar

- Sözlük girdileri modele **istem yönlendirmesi** olarak aktarılır (deterministik yeniden yazımlar yoktur).
- `scripts/docs-i18n` çeviri oluşturmayı hâlâ yönetir.
- Kaynak deposu İngilizce belgeleri yayın deposuna eşzamanlar; yerel ayar üretimi push, zamanlama ve sürüm dispatch başına ilgili depoda çalışır.
