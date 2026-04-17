---
read_when:
    - Widzisz klucz konfiguracyjny `.experimental` i chcesz wiedzieć, czy jest stabilny
    - Chcesz wypróbować funkcje środowiska uruchomieniowego w wersji zapoznawczej, nie myląc ich ze zwykłymi ustawieniami domyślnymi
    - Chcesz mieć jedno miejsce, w którym znajdziesz obecnie udokumentowane flagi eksperymentalne
summary: Co oznaczają flagi eksperymentalne w OpenClaw i które z nich są obecnie udokumentowane
title: Funkcje eksperymentalne
x-i18n:
    generated_at: "2026-04-15T14:40:33Z"
    model: gpt-5.4
    provider: openai
    source_hash: 2d1c7b3d4cd56ef8a0bdab1deb9918e9b2c9a33f956d63193246087f8633dcf3
    source_path: concepts/experimental-features.md
    workflow: 15
---

# Funkcje eksperymentalne

Funkcje eksperymentalne w OpenClaw to **opcjonalne powierzchnie podglądowe**. Są
ukryte za jawnymi flagami, ponieważ nadal potrzebują sprawdzenia w rzeczywistych
warunkach, zanim zasłużą na stabilne ustawienie domyślne lub długotrwały
publiczny kontrakt.

Traktuj je inaczej niż zwykłą konfigurację:

- Pozostaw je **wyłączone domyślnie**, chyba że powiązana dokumentacja zaleca wypróbowanie którejś z nich.
- Oczekuj, że ich **kształt i zachowanie będą się zmieniać** szybciej niż w przypadku stabilnej konfiguracji.
- Najpierw wybieraj ścieżkę stabilną, jeśli już istnieje.
- Jeśli wdrażasz OpenClaw szerzej, najpierw przetestuj flagi eksperymentalne w mniejszym
  środowisku, zanim uwzględnisz je we wspólnej bazie konfiguracji.

## Obecnie udokumentowane flagi

| Powierzchnia             | Klucz                                                     | Użyj jej, gdy                                                                                                  | Więcej                                                                                        |
| ------------------------ | --------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| Środowisko uruchomieniowe modeli lokalnych | `agents.defaults.experimental.localModelLean`             | Mniejszy lub bardziej rygorystyczny lokalny backend nie radzi sobie z pełną domyślną powierzchnią narzędzi OpenClaw | [Modele lokalne](/pl/gateway/local-models)                                                       |
| Wyszukiwanie pamięci     | `agents.defaults.memorySearch.experimental.sessionMemory` | Chcesz, aby `memory_search` indeksowało wcześniejsze transkrypcje sesji i akceptujesz dodatkowy koszt przechowywania oraz indeksowania | [Dokumentacja referencyjna konfiguracji pamięci](/pl/reference/memory-config#session-memory-search-experimental) |
| Narzędzie planowania strukturalnego | `tools.experimental.planTool`                             | Chcesz udostępnić strukturalne narzędzie `update_plan` do śledzenia pracy wieloetapowej w zgodnych środowiskach uruchomieniowych i interfejsach UI | [Dokumentacja referencyjna konfiguracji Gateway](/pl/gateway/configuration-reference#toolsexperimental)         |

## Tryb odchudzony modeli lokalnych

`agents.defaults.experimental.localModelLean: true` to zawór bezpieczeństwa dla
słabszych konfiguracji modeli lokalnych. Ogranicza cięższe domyślne narzędzia,
takie jak `browser`, `cron` i `message`, dzięki czemu kształt promptu jest
mniejszy i mniej podatny na problemy w backendach zgodnych z OpenAI, które mają
mały kontekst lub bardziej rygorystyczne wymagania.

To celowo **nie** jest normalna ścieżka. Jeśli Twój backend dobrze obsługuje
pełne środowisko uruchomieniowe, pozostaw tę opcję wyłączoną.

## Eksperymentalne nie znaczy ukryte

Jeśli funkcja jest eksperymentalna, OpenClaw powinien jasno to komunikować w dokumentacji oraz w samej
ścieżce konfiguracji. Tym, czego **nie** powinien robić, jest przemycanie zachowania podglądowego do
wyglądającego stabilnie domyślnego przełącznika i udawanie, że to coś normalnego. Właśnie w ten sposób
powierzchnie konfiguracji stają się chaotyczne.
