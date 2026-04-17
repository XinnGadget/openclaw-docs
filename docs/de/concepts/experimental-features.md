---
read_when:
    - Sie sehen einen Konfigurationsschlüssel `.experimental` und möchten wissen, ob er stabil ist
    - Sie möchten Vorschau-Laufzeitfunktionen ausprobieren, ohne sie mit normalen Standardeinstellungen zu verwechseln
    - Sie möchten eine zentrale Stelle finden, an der die derzeit dokumentierten experimentellen Flags aufgeführt sind
summary: Was experimentelle Flags in OpenClaw bedeuten und welche derzeit dokumentiert sind
title: Experimentelle Funktionen
x-i18n:
    generated_at: "2026-04-15T14:40:30Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2d1c7b3d4cd56ef8a0bdab1deb9918e9b2c9a33f956d63193246087f8633dcf3
    source_path: concepts/experimental-features.md
    workflow: 15
---

# Experimentelle Funktionen

Experimentelle Funktionen in OpenClaw sind **optionale Vorschau-Oberflächen**. Sie
stehen hinter expliziten Flags, weil sie noch Praxiserfahrung unter realen
Bedingungen brauchen, bevor sie eine stabile Standardeinstellung oder einen
langlebigen öffentlichen Vertrag verdienen.

Behandeln Sie sie anders als normale Konfiguration:

- Lassen Sie sie **standardmäßig deaktiviert**, sofern die zugehörige Dokumentation Sie nicht auffordert, eine auszuprobieren.
- Rechnen Sie damit, dass sich **Form und Verhalten** schneller ändern als bei stabiler Konfiguration.
- Bevorzugen Sie zuerst den stabilen Pfad, wenn bereits einer existiert.
- Wenn Sie OpenClaw breit ausrollen, testen Sie experimentelle Flags zunächst in einer kleineren Umgebung, bevor Sie sie in eine gemeinsame Baseline übernehmen.

## Derzeit dokumentierte Flags

| Oberfläche              | Schlüssel                                                  | Verwenden Sie ihn, wenn                                                                                         | Mehr                                                                                          |
| ----------------------- | ---------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Laufzeit für lokale Modelle | `agents.defaults.experimental.localModelLean`             | ein kleineres oder strengeres lokales Backend an der vollständigen Standard-Tool-Oberfläche von OpenClaw scheitert | [Lokale Modelle](/de/gateway/local-models)                                                       |
| Speichersuche           | `agents.defaults.memorySearch.experimental.sessionMemory`  | Sie möchten, dass `memory_search` frühere Sitzungsprotokolle indexiert und nehmen die zusätzlichen Speicher- und Indexierungskosten in Kauf | [Referenz zur Speicherkonfiguration](/de/reference/memory-config#session-memory-search-experimental) |
| Strukturiertes Planungstool | `tools.experimental.planTool`                             | Sie möchten das strukturierte Tool `update_plan` für die Nachverfolgung mehrstufiger Arbeiten in kompatiblen Laufzeiten und UIs verfügbar machen | [Referenz zur Gateway-Konfiguration](/de/gateway/configuration-reference#toolsexperimental)      |

## Lean-Modus für lokale Modelle

`agents.defaults.experimental.localModelLean: true` ist ein Entlastungsventil
für schwächere Setups mit lokalen Modellen. Es entfernt umfangreiche
Standard-Tools wie `browser`, `cron` und `message`, damit die Prompt-Struktur
kleiner und für Backends mit kleinem Kontext oder strengere
OpenAI-kompatible Backends weniger fragil ist.

Das ist absichtlich **nicht** der normale Pfad. Wenn Ihr Backend die vollständige
Laufzeit sauber verarbeiten kann, lassen Sie dies deaktiviert.

## Experimentell bedeutet nicht verborgen

Wenn eine Funktion experimentell ist, sollte OpenClaw das in der Dokumentation
und im Konfigurationspfad selbst klar sagen. Was es **nicht** tun sollte, ist,
Vorschauverhalten in einen stabil wirkenden Standard-Schalter hineinzuschmuggeln
und so zu tun, als wäre das normal. So werden Konfigurationsoberflächen
unübersichtlich.
