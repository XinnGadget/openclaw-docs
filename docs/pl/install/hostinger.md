---
read_when:
    - Konfigurowanie OpenClaw na Hostinger
    - Szukasz zarządzanego VPS dla OpenClaw?
    - Korzystanie z 1-Click OpenClaw od Hostinger
summary: Hostuj OpenClaw na Hostinger
title: Hostinger
x-i18n:
    generated_at: "2026-04-14T02:08:50Z"
    model: gpt-5.4
    provider: openai
    source_hash: cf173cdcf6344f8ee22e839a27f4e063a3a102186f9acc07c4a33d4794e2c034
    source_path: install/hostinger.md
    workflow: 15
---

# Hostinger

Uruchom trwały Gateway OpenClaw na [Hostinger](https://www.hostinger.com/openclaw) za pomocą zarządzanego wdrożenia **1-Click** lub instalacji na **VPS**.

## Wymagania wstępne

- Konto Hostinger ([rejestracja](https://www.hostinger.com/openclaw))
- Około 5–10 minut

## Opcja A: OpenClaw 1-Click

Najszybszy sposób na rozpoczęcie. Hostinger zajmuje się infrastrukturą, Dockerem i automatycznymi aktualizacjami.

<Steps>
  <Step title="Zakup i uruchomienie">
    1. Na [stronie OpenClaw w Hostinger](https://www.hostinger.com/openclaw) wybierz plan Managed OpenClaw i sfinalizuj zakup.

    <Note>
    Podczas finalizacji zakupu możesz wybrać kredyty **Ready-to-Use AI**, które są kupowane z wyprzedzeniem i natychmiast integrowane w OpenClaw — bez potrzeby zakładania zewnętrznych kont ani używania kluczy API od innych dostawców. Możesz od razu rozpocząć czatowanie. Alternatywnie podczas konfiguracji możesz podać własny klucz od Anthropic, OpenAI, Google Gemini lub xAI.
    </Note>

  </Step>

  <Step title="Wybierz kanał wiadomości">
    Wybierz co najmniej jeden kanał do połączenia:

    - **WhatsApp** — zeskanuj kod QR wyświetlany w kreatorze konfiguracji.
    - **Telegram** — wklej token bota z [BotFather](https://t.me/BotFather).

  </Step>

  <Step title="Dokończ instalację">
    Kliknij **Finish**, aby wdrożyć instancję. Gdy wszystko będzie gotowe, uzyskaj dostęp do panelu OpenClaw z poziomu **OpenClaw Overview** w hPanel.
  </Step>

</Steps>

## Opcja B: OpenClaw na VPS

Większa kontrola nad serwerem. Hostinger wdraża OpenClaw przez Docker na Twoim VPS, a Ty zarządzasz nim przez **Docker Manager** w hPanel.

<Steps>
  <Step title="Kup VPS">
    1. Na [stronie OpenClaw w Hostinger](https://www.hostinger.com/openclaw) wybierz plan OpenClaw on VPS i sfinalizuj zakup.

    <Note>
    Podczas finalizacji zakupu możesz wybrać kredyty **Ready-to-Use AI** — są one kupowane z wyprzedzeniem i natychmiast integrowane w OpenClaw, dzięki czemu możesz rozpocząć czatowanie bez żadnych zewnętrznych kont ani kluczy API od innych dostawców.
    </Note>

  </Step>

  <Step title="Skonfiguruj OpenClaw">
    Gdy VPS zostanie udostępniony, wypełnij pola konfiguracji:

    - **Gateway token** — generowany automatycznie; zapisz go do późniejszego użycia.
    - **Numer WhatsApp** — Twój numer wraz z kodem kraju (opcjonalnie).
    - **Token bota Telegram** — z [BotFather](https://t.me/BotFather) (opcjonalnie).
    - **Klucze API** — potrzebne tylko wtedy, gdy podczas zakupu nie wybrano kredytów Ready-to-Use AI.

  </Step>

  <Step title="Uruchom OpenClaw">
    Kliknij **Deploy**. Po uruchomieniu otwórz panel OpenClaw z poziomu hPanel, klikając **Open**.
  </Step>

</Steps>

Logami, restartami i aktualizacjami zarządza się bezpośrednio z interfejsu Docker Manager w hPanel. Aby zaktualizować, kliknij **Update** w Docker Manager — spowoduje to pobranie najnowszego obrazu.

## Zweryfikuj konfigurację

Wyślij „Hi” do swojego asystenta na podłączonym kanale. OpenClaw odpowie i przeprowadzi Cię przez ustawienie początkowych preferencji.

## Rozwiązywanie problemów

**Panel się nie ładuje** — Poczekaj kilka minut, aż kontener zakończy provisioning. Sprawdź logi Docker Manager w hPanel.

**Kontener Docker ciągle się restartuje** — Otwórz logi Docker Manager i sprawdź, czy nie ma błędów konfiguracji (brakujące tokeny, nieprawidłowe klucze API).

**Bot Telegram nie odpowiada** — Wyślij wiadomość z kodem parowania bezpośrednio z Telegrama jako wiadomość w czacie OpenClaw, aby dokończyć połączenie.

## Kolejne kroki

- [Kanały](/pl/channels) — połącz Telegram, WhatsApp, Discord i inne
- [Konfiguracja Gateway](/pl/gateway/configuration) — wszystkie opcje konfiguracji
