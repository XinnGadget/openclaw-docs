---
read_when:
    - Procurando definições de canais de lançamento públicos
    - Procurando nomenclatura de versão e cadência
summary: Canais de lançamento públicos, nomenclatura de versão e cadência
title: Política de lançamento
x-i18n:
    generated_at: "2026-04-14T02:08:34Z"
    model: gpt-5.4
    provider: openai
    source_hash: fdc32839447205d74ba7a20a45fbac8e13b199174b442a1e260e3fce056c63da
    source_path: reference/RELEASING.md
    workflow: 15
---

# Política de lançamento

O OpenClaw tem três canais de lançamento públicos:

- stable: lançamentos com tag que publicam no npm `beta` por padrão, ou no npm `latest` quando solicitado explicitamente
- beta: tags de pré-lançamento que publicam no npm `beta`
- dev: a cabeça móvel de `main`

## Nomenclatura de versão

- Versão de lançamento stable: `YYYY.M.D`
  - Tag Git: `vYYYY.M.D`
- Versão de lançamento de correção stable: `YYYY.M.D-N`
  - Tag Git: `vYYYY.M.D-N`
- Versão de pré-lançamento beta: `YYYY.M.D-beta.N`
  - Tag Git: `vYYYY.M.D-beta.N`
- Não use preenchimento com zero para mês ou dia
- `latest` significa o lançamento npm stable promovido atual
- `beta` significa o alvo de instalação beta atual
- Lançamentos stable e lançamentos de correção stable publicam no npm `beta` por padrão; operadores de lançamento podem direcionar para `latest` explicitamente, ou promover depois uma build beta validada
- Todo lançamento do OpenClaw envia o pacote npm e o app macOS juntos

## Cadência de lançamento

- Os lançamentos passam primeiro por beta
- Stable só vem depois que o beta mais recente for validado
- Procedimento detalhado de lançamento, aprovações, credenciais e notas de recuperação são
  apenas para mantenedores

## Verificações prévias de lançamento

- Execute `pnpm build && pnpm ui:build` antes de `pnpm release:check` para que os
  artefatos de lançamento esperados em `dist/*` e o bundle da UI de Controle existam para a etapa
  de validação do pacote
- Execute `pnpm release:check` antes de todo lançamento com tag
- As verificações de lançamento agora são executadas em um workflow manual separado:
  `OpenClaw Release Checks`
- Essa separação é intencional: mantenha o caminho real de lançamento npm curto,
  determinístico e focado em artefatos, enquanto verificações live mais lentas ficam em sua
  própria trilha para não atrasarem nem bloquearem a publicação
- As verificações de lançamento devem ser disparadas a partir da ref de workflow `main` para que a
  lógica do workflow e os segredos permaneçam canônicos
- Esse workflow aceita uma tag de lançamento existente ou o SHA completo de 40 caracteres
  atual do commit `main`
- No modo commit-SHA, ele aceita apenas o HEAD atual de `origin/main`; use uma
  tag de lançamento para commits de lançamento mais antigos
- A verificação prévia somente de validação de `OpenClaw NPM Release` também aceita o
  SHA completo atual de 40 caracteres do commit `main` sem exigir uma tag enviada
- Esse caminho por SHA é somente para validação e não pode ser promovido a uma publicação real
- No modo SHA, o workflow sintetiza `v<package.json version>` apenas para a
  verificação de metadados do pacote; a publicação real ainda exige uma tag de lançamento real
- Ambos os workflows mantêm o caminho real de publicação e promoção em runners
  hospedados pelo GitHub, enquanto o caminho de validação não mutável pode usar os
  runners Linux Blacksmith maiores
- Esse workflow executa
  `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_CACHE_TEST=1 pnpm test:live:cache`
  usando os segredos de workflow `OPENAI_API_KEY` e `ANTHROPIC_API_KEY`
- A verificação prévia de lançamento npm não espera mais pela trilha separada de verificações de lançamento
- Execute `RELEASE_TAG=vYYYY.M.D node --import tsx scripts/openclaw-npm-release-check.ts`
  (ou a tag beta/correção correspondente) antes da aprovação
- Após a publicação no npm, execute
  `node --import tsx scripts/openclaw-npm-postpublish-verify.ts YYYY.M.D`
  (ou a versão beta/correção correspondente) para verificar o caminho de instalação
  publicado no registro em um prefixo temporário novo
- A automação de lançamento dos mantenedores agora usa preflight-then-promote:
  - a publicação npm real precisa passar por um `preflight_run_id` npm bem-sucedido
  - lançamentos npm stable usam `beta` por padrão
  - a publicação npm stable pode direcionar para `latest` explicitamente via entrada do workflow
  - a promoção npm stable de `beta` para `latest` continua disponível como um modo manual explícito no workflow confiável `OpenClaw NPM Release`
  - publicações stable diretas também podem executar um modo explícito de sincronização de dist-tag que
    faz `latest` e `beta` apontarem para a versão stable já publicada
  - esses modos de dist-tag ainda precisam de um `NPM_TOKEN` válido no ambiente `npm-release`, porque o gerenciamento de `npm dist-tag` é separado da publicação confiável
  - `macOS Release` público é somente para validação
  - a publicação privada real para mac deve passar por `preflight_run_id` e `validate_run_id`
    privados de mac bem-sucedidos
  - os caminhos de publicação reais promovem artefatos preparados em vez de reconstruí-los
    novamente
- Para lançamentos de correção stable como `YYYY.M.D-N`, o verificador pós-publicação
  também verifica o mesmo caminho de upgrade em prefixo temporário de `YYYY.M.D` para `YYYY.M.D-N`
  para que correções de lançamento não possam deixar silenciosamente instalações globais mais antigas na
  carga do stable base
- A verificação prévia de lançamento npm falha de forma fechada a menos que o tarball inclua
  tanto `dist/control-ui/index.html` quanto uma carga útil não vazia em `dist/control-ui/assets/`
  para que não enviemos novamente um painel do navegador vazio
- Se o trabalho de lançamento tocou no planejamento de CI, manifests de temporização de extensões ou
  matrizes de teste de extensões, regenere e revise as saídas de matriz do workflow
  `checks-node-extensions` de propriedade do planner a partir de `.github/workflows/ci.yml`
  antes da aprovação para que as notas de lançamento não descrevam um layout de CI desatualizado
- A prontidão para lançamento stable no macOS também inclui as superfícies do atualizador:
  - o lançamento no GitHub deve terminar com os arquivos empacotados `.zip`, `.dmg` e `.dSYM.zip`
  - `appcast.xml` em `main` deve apontar para o novo zip stable após a publicação
  - o app empacotado deve manter um bundle id não-debug, uma URL de feed Sparkle não vazia
    e um `CFBundleVersion` igual ou acima do piso de build Sparkle canônico
    para essa versão de lançamento

## Entradas do workflow NPM

`OpenClaw NPM Release` aceita estas entradas controladas pelo operador:

- `tag`: tag de lançamento obrigatória, como `v2026.4.2`, `v2026.4.2-1` ou
  `v2026.4.2-beta.1`; quando `preflight_only=true`, também pode ser o
  SHA completo atual de 40 caracteres do commit `main` para verificação prévia somente de validação
- `preflight_only`: `true` para somente validação/build/pacote, `false` para o
  caminho de publicação real
- `preflight_run_id`: obrigatório no caminho de publicação real para que o workflow reutilize
  o tarball preparado da execução de verificação prévia bem-sucedida
- `npm_dist_tag`: tag npm de destino para o caminho de publicação; o padrão é `beta`
- `promote_beta_to_latest`: `true` para pular a publicação e mover uma build stable `beta`
  já publicada para `latest`
- `sync_stable_dist_tags`: `true` para pular a publicação e fazer `latest` e
  `beta` apontarem para uma versão stable já publicada

`OpenClaw Release Checks` aceita estas entradas controladas pelo operador:

- `ref`: tag de lançamento existente ou o SHA completo de 40 caracteres do commit
  atual `main` para validar

Regras:

- Tags stable e de correção podem publicar em `beta` ou `latest`
- Tags de pré-lançamento beta podem publicar apenas em `beta`
- A entrada com SHA completo de commit é permitida apenas quando `preflight_only=true`
- O modo commit-SHA das verificações de lançamento também exige o HEAD atual de `origin/main`
- O caminho de publicação real deve usar o mesmo `npm_dist_tag` usado durante a verificação prévia;
  o workflow verifica esses metadados antes de a publicação continuar
- O modo de promoção deve usar uma tag stable ou de correção, `preflight_only=false`,
  `preflight_run_id` vazio e `npm_dist_tag=beta`
- O modo de sincronização de dist-tag deve usar uma tag stable ou de correção,
  `preflight_only=false`, `preflight_run_id` vazio, `npm_dist_tag=latest`
  e `promote_beta_to_latest=false`
- Os modos de promoção e sincronização de dist-tag também exigem um `NPM_TOKEN` válido porque
  `npm dist-tag add` ainda precisa de autenticação npm normal; a publicação confiável cobre
  apenas o caminho de publicação do pacote

## Sequência de lançamento npm stable

Ao fazer um lançamento npm stable:

1. Execute `OpenClaw NPM Release` com `preflight_only=true`
   - Antes de existir uma tag, você pode usar o SHA completo de `main` atual para uma
     execução seca somente de validação do workflow de verificação prévia
2. Escolha `npm_dist_tag=beta` para o fluxo normal beta-first, ou `latest` apenas
   quando você quiser intencionalmente uma publicação stable direta
3. Execute `OpenClaw Release Checks` separadamente com a mesma tag ou o
   SHA completo atual de `main` quando quiser cobertura live de cache de prompt
   - Isso é separado de propósito para que a cobertura live continue disponível sem
     reacoplar verificações demoradas ou instáveis ao workflow de publicação
4. Salve o `preflight_run_id` bem-sucedido
5. Execute `OpenClaw NPM Release` novamente com `preflight_only=false`, a mesma
   `tag`, o mesmo `npm_dist_tag` e o `preflight_run_id` salvo
6. Se o lançamento caiu em `beta`, execute `OpenClaw NPM Release` mais tarde com a
   mesma `tag` stable, `promote_beta_to_latest=true`, `preflight_only=false`,
   `preflight_run_id` vazio e `npm_dist_tag=beta` quando quiser mover essa
   build publicada para `latest`
7. Se o lançamento foi intencionalmente publicado diretamente em `latest` e `beta`
   deve seguir a mesma build stable, execute `OpenClaw NPM Release` com a mesma
   `tag` stable, `sync_stable_dist_tags=true`, `promote_beta_to_latest=false`,
   `preflight_only=false`, `preflight_run_id` vazio e `npm_dist_tag=latest`

Os modos de promoção e sincronização de dist-tag ainda exigem a aprovação do ambiente
`npm-release` e um `NPM_TOKEN` válido acessível a essa execução do workflow.

Isso mantém tanto o caminho de publicação direta quanto o caminho de promoção beta-first
documentados e visíveis para o operador.

## Referências públicas

- [`.github/workflows/openclaw-npm-release.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-npm-release.yml)
- [`.github/workflows/openclaw-release-checks.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-release-checks.yml)
- [`scripts/openclaw-npm-release-check.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/openclaw-npm-release-check.ts)
- [`scripts/package-mac-dist.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-dist.sh)
- [`scripts/make_appcast.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/make_appcast.sh)

Os mantenedores usam a documentação privada de lançamento em
[`openclaw/maintainers/release/README.md`](https://github.com/openclaw/maintainers/blob/main/release/README.md)
para o runbook real.
