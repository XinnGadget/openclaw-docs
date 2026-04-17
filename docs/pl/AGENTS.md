---
x-i18n:
    generated_at: "2026-04-12T09:33:22Z"
    model: gpt-5.4
    provider: openai
    source_hash: 6805814012caac6ff64f17f44f393975510c5af3421fae9651ed9033e5861784
    source_path: AGENTS.md
    workflow: 15
---

# Przewodnik po dokumentacji

Ten katalog odpowiada za tworzenie dokumentacji, reguły linków Mintlify i zasady internacjonalizacji dokumentacji.

## Reguły Mintlify

- Dokumentacja jest hostowana w Mintlify (`https://docs.openclaw.ai`).
- Wewnętrzne linki do dokumentów w `docs/**/*.md` muszą pozostać względne względem katalogu głównego i bez sufiksu `.md` lub `.mdx` (przykład: `[Config](/configuration)`).
- Odwołania do sekcji powinny używać kotwic w ścieżkach względnych względem katalogu głównego (przykład: `[Hooks](/configuration#hooks)`).
- Nagłówki dokumentów powinny unikać półpauz i apostrofów, ponieważ generowanie kotwic w Mintlify jest na to wrażliwe.
- README i inne dokumenty renderowane przez GitHub powinny zachować bezwzględne adresy URL dokumentacji, aby linki działały poza Mintlify.
- Treść dokumentacji musi pozostać ogólna: bez osobistych nazw urządzeń, nazw hostów ani lokalnych ścieżek; używaj symboli zastępczych, takich jak `user@gateway-host`.

## Zasady dotyczące treści dokumentacji

- W dokumentacji, tekstach UI i listach wyboru usługi/dostawców należy porządkować alfabetycznie, chyba że dana sekcja wyraźnie opisuje kolejność działania w czasie wykonywania lub kolejność automatycznego wykrywania.
- Zachowuj spójność nazewnictwa bundled Plugin z ogólnorepozytoryjnymi zasadami terminologii Plugin zawartymi w głównym `AGENTS.md`.

## Internacjonalizacja dokumentacji

- Dokumentacja w językach obcych nie jest utrzymywana w tym repozytorium. Wygenerowane dane wyjściowe do publikacji znajdują się w osobnym repozytorium `openclaw/docs` (często sklonowanym lokalnie jako `../openclaw-docs`).
- Nie dodawaj ani nie edytuj zlokalizowanej dokumentacji w `docs/<locale>/**` tutaj.
- Traktuj angielską dokumentację w tym repozytorium oraz pliki glosariusza jako źródło prawdy.
- Pipeline: zaktualizuj tutaj angielską dokumentację, w razie potrzeby zaktualizuj `docs/.i18n/glossary.<locale>.json`, a następnie pozwól, aby synchronizacja repozytorium publikacji i `scripts/docs-i18n` zostały uruchomione w `openclaw/docs`.
- Przed ponownym uruchomieniem `scripts/docs-i18n` dodaj wpisy do glosariusza dla wszelkich nowych terminów technicznych, tytułów stron lub krótkich etykiet nawigacyjnych, które muszą pozostać po angielsku lub mieć stałe tłumaczenie.
- `pnpm docs:check-i18n-glossary` jest mechanizmem kontrolnym dla zmienionych angielskich tytułów dokumentów i krótkich wewnętrznych etykiet dokumentów.
- Pamięć tłumaczeń znajduje się w wygenerowanych plikach `docs/.i18n/*.tm.jsonl` w repozytorium publikacji.
- Zobacz `docs/.i18n/README.md`.
