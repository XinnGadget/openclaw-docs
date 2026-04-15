---
read_when:
    - Procurando definições de canais de lançamento públicos
    - Procurando nomenclatura de versões e cadência
summary: Canais de lançamento públicos, nomenclatura de versões e cadência
title: Política de lançamento
x-i18n:
    generated_at: "2026-04-15T05:33:47Z"
    model: gpt-5.4
    provider: openai
    source_hash: 88724307269ab783a9fbf8a0540fea198d8a3add68457f4e64d5707114fa518c
    source_path: reference/RELEASING.md
    workflow: 15
---

# Política de lançamento

O OpenClaw tem três faixas públicas de lançamento:

- stable: lançamentos com tag que publicam no npm `beta` por padrão, ou no npm `latest` quando solicitado explicitamente
- beta: tags de pré-lançamento que publicam no npm `beta`
- dev: a ponta móvel da `main`

## Nomenclatura de versões

- Versão de lançamento stable: `YYYY.M.D`
  - Tag Git: `vYYYY.M.D`
- Versão de lançamento de correção stable: `YYYY.M.D-N`
  - Tag Git: `vYYYY.M.D-N`
- Versão de pré-lançamento beta: `YYYY.M.D-beta.N`
  - Tag Git: `vYYYY.M.D-beta.N`
- Não preencha mês ou dia com zeros à esquerda
- `latest` significa o lançamento npm stable promovido atual
- `beta` significa o destino de instalação beta atual
- Lançamentos stable e correções stable publicam no npm `beta` por padrão; operadores de lançamento podem direcionar explicitamente para `latest` ou promover uma build beta validada depois
- Todo lançamento do OpenClaw entrega o pacote npm e o app macOS juntos

## Cadência de lançamentos

- Os lançamentos seguem primeiro para beta
- stable só vem depois que a beta mais recente é validada
- Procedimento detalhado de lançamento, aprovações, credenciais e notas de recuperação são exclusivos para maintainers

## Pré-verificação de lançamento

- Execute `pnpm build && pnpm ui:build` antes de `pnpm release:check` para que os artefatos de lançamento esperados em `dist/*` e o bundle da Control UI existam para a etapa de validação do pack
- Execute `pnpm release:check` antes de todo lançamento com tag
- As verificações de lançamento agora são executadas em um workflow manual separado:
  `OpenClaw Release Checks`
- A validação de runtime de instalação e upgrade entre sistemas operacionais é despachada a partir do workflow chamador privado
  `openclaw/releases-private/.github/workflows/openclaw-cross-os-release-checks.yml`,
  que invoca o workflow público reutilizável
  `.github/workflows/openclaw-cross-os-release-checks-reusable.yml`
- Essa divisão é intencional: mantém o caminho real de lançamento no npm curto,
  determinístico e focado em artefatos, enquanto as verificações ao vivo mais lentas ficam em sua própria faixa para não atrasarem nem bloquearem a publicação
- As verificações de lançamento devem ser despachadas a partir da referência de workflow `main` para que a lógica do workflow e os segredos permaneçam canônicos
- Esse workflow aceita uma tag de lançamento existente ou o SHA completo atual de 40 caracteres do commit da `main`
- No modo SHA de commit, ele aceita apenas o HEAD atual de `origin/main`; use uma tag de lançamento para commits de lançamento mais antigos
- A pré-verificação somente de validação de `OpenClaw NPM Release` também aceita o SHA completo atual de 40 caracteres do commit da `main` sem exigir uma tag enviada
- Esse caminho por SHA é apenas de validação e não pode ser promovido para uma publicação real
- No modo SHA, o workflow sintetiza `v<package.json version>` apenas para a verificação de metadados do pacote; a publicação real ainda exige uma tag de lançamento real
- Ambos os workflows mantêm o caminho real de publicação e promoção em runners hospedados pelo GitHub, enquanto o caminho de validação não mutável pode usar os runners Linux maiores da Blacksmith
- Esse workflow executa
  `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_CACHE_TEST=1 pnpm test:live:cache`
  usando os segredos de workflow `OPENAI_API_KEY` e `ANTHROPIC_API_KEY`
- A pré-verificação de lançamento npm não espera mais pela faixa separada de verificações de lançamento
- Execute `RELEASE_TAG=vYYYY.M.D node --import tsx scripts/openclaw-npm-release-check.ts`
  (ou a tag beta/correção correspondente) antes da aprovação
- Após a publicação no npm, execute
  `node --import tsx scripts/openclaw-npm-postpublish-verify.ts YYYY.M.D`
  (ou a versão beta/correção correspondente) para verificar o caminho de instalação publicado no registro em um prefixo temporário novo
- A automação de lançamento de maintainers agora usa pré-verificação seguida de promoção:
  - a publicação real no npm deve passar por um `preflight_run_id` bem-sucedido do npm
  - lançamentos npm stable usam `beta` por padrão
  - a publicação npm stable pode direcionar explicitamente para `latest` por entrada do workflow
  - a mutação de dist-tag do npm baseada em token agora fica em
    `openclaw/releases-private/.github/workflows/openclaw-npm-dist-tags.yml`
    por segurança, porque `npm dist-tag add` ainda precisa de `NPM_TOKEN`, enquanto o repositório público mantém publicação somente com OIDC
  - o `macOS Release` público é apenas de validação
  - a publicação real privada do mac deve passar por `preflight_run_id` e `validate_run_id` privados do mac bem-sucedidos
  - os caminhos de publicação reais promovem artefatos preparados em vez de reconstruí-los novamente
- Para lançamentos de correção stable como `YYYY.M.D-N`, o verificador pós-publicação
  também verifica o mesmo caminho de upgrade em prefixo temporário de `YYYY.M.D` para `YYYY.M.D-N`,
  para que correções de lançamento não deixem silenciosamente instalações globais mais antigas na carga stable base
- A pré-verificação de lançamento npm falha de forma fechada, a menos que o tarball inclua `dist/control-ui/index.html` e uma carga útil não vazia em `dist/control-ui/assets/`,
  para que não entreguemos novamente um dashboard de navegador vazio
- `pnpm test:install:smoke` também impõe o orçamento de `unpackedSize` do npm pack no tarball candidato de atualização,
  para que o e2e do instalador detecte aumento acidental do pack antes do caminho de publicação do lançamento
- Se o trabalho de lançamento tocou no planejamento de CI, manifestos de tempo de extensões ou matrizes de teste de extensões, regenere e revise as saídas da matriz de workflow `checks-node-extensions`, de propriedade do planner, em `.github/workflows/ci.yml`
  antes da aprovação, para que as notas de lançamento não descrevam um layout de CI desatualizado
- A prontidão de lançamento stable no macOS também inclui as superfícies do atualizador:
  - o lançamento no GitHub deve terminar com os arquivos empacotados `.zip`, `.dmg` e `.dSYM.zip`
  - `appcast.xml` na `main` deve apontar para o novo zip stable após a publicação
  - o app empacotado deve manter um bundle id não debug, uma URL de feed Sparkle não vazia
    e um `CFBundleVersion` igual ou acima do piso canônico de build do Sparkle
    para essa versão de lançamento

## Entradas do workflow de NPM

`OpenClaw NPM Release` aceita estas entradas controladas pelo operador:

- `tag`: tag de lançamento obrigatória como `v2026.4.2`, `v2026.4.2-1` ou
  `v2026.4.2-beta.1`; quando `preflight_only=true`, também pode ser o
  SHA completo atual de 40 caracteres do commit da `main` para pré-verificação apenas de validação
- `preflight_only`: `true` apenas para validação/build/package, `false` para o
  caminho de publicação real
- `preflight_run_id`: obrigatório no caminho de publicação real para que o workflow reutilize
  o tarball preparado da execução de pré-verificação bem-sucedida
- `npm_dist_tag`: tag de destino no npm para o caminho de publicação; o padrão é `beta`

`OpenClaw Release Checks` aceita estas entradas controladas pelo operador:

- `ref`: tag de lançamento existente ou o SHA completo atual de 40 caracteres do commit da `main`
  para validar

Regras:

- Tags stable e de correção podem publicar em `beta` ou `latest`
- Tags de pré-lançamento beta podem publicar apenas em `beta`
- A entrada de SHA completo de commit é permitida apenas quando `preflight_only=true`
- O modo SHA de commit das verificações de lançamento também exige o HEAD atual de `origin/main`
- O caminho de publicação real deve usar o mesmo `npm_dist_tag` usado durante a pré-verificação;
  o workflow verifica esses metadados antes de a publicação continuar

## Sequência de lançamento npm stable

Ao criar um lançamento npm stable:

1. Execute `OpenClaw NPM Release` com `preflight_only=true`
   - Antes de existir uma tag, você pode usar o SHA completo atual da `main` para uma execução de teste apenas de validação do workflow de pré-verificação
2. Escolha `npm_dist_tag=beta` para o fluxo normal beta-first, ou `latest` apenas
   quando você quiser intencionalmente uma publicação stable direta
3. Execute `OpenClaw Release Checks` separadamente com a mesma tag ou o
   SHA completo atual da `main` quando quiser cobertura ao vivo do cache de prompt
   - Isso é separado de propósito para que a cobertura ao vivo continue disponível sem
     reacoplar verificações longas ou instáveis ao workflow de publicação
4. Salve o `preflight_run_id` bem-sucedido
5. Execute `OpenClaw NPM Release` novamente com `preflight_only=false`, a mesma
   `tag`, o mesmo `npm_dist_tag` e o `preflight_run_id` salvo
6. Se o lançamento caiu em `beta`, use o workflow privado
   `openclaw/releases-private/.github/workflows/openclaw-npm-dist-tags.yml`
   para promover essa versão stable de `beta` para `latest`
7. Se o lançamento foi publicado intencionalmente diretamente em `latest` e `beta`
   deve seguir imediatamente a mesma build stable, use esse mesmo workflow privado
   para apontar ambas as dist-tags para a versão stable, ou deixe sua sincronização
   automática agendada mover `beta` depois

A mutação de dist-tag fica no repositório privado por segurança porque ainda
exige `NPM_TOKEN`, enquanto o repositório público mantém publicação somente com OIDC.

Isso mantém tanto o caminho de publicação direta quanto o caminho de promoção beta-first
documentados e visíveis para o operador.

## Referências públicas

- [`.github/workflows/openclaw-npm-release.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-npm-release.yml)
- [`.github/workflows/openclaw-release-checks.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-release-checks.yml)
- [`.github/workflows/openclaw-cross-os-release-checks-reusable.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-cross-os-release-checks-reusable.yml)
- [`scripts/openclaw-npm-release-check.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/openclaw-npm-release-check.ts)
- [`scripts/package-mac-dist.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-dist.sh)
- [`scripts/make_appcast.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/make_appcast.sh)

Maintainers usam a documentação privada de lançamento em
[`openclaw/maintainers/release/README.md`](https://github.com/openclaw/maintainers/blob/main/release/README.md)
para o runbook real.
