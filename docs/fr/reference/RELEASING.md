---
read_when:
    - Recherche des définitions des canaux de publication publics
    - Recherche de la dénomination des versions et de la cadence
summary: Canaux de publication publics, dénomination des versions et cadence
title: Politique de publication
x-i18n:
    generated_at: "2026-04-14T02:08:38Z"
    model: gpt-5.4
    provider: openai
    source_hash: fdc32839447205d74ba7a20a45fbac8e13b199174b442a1e260e3fce056c63da
    source_path: reference/RELEASING.md
    workflow: 15
---

# Politique de publication

OpenClaw a trois canaux de publication publics :

- stable : des publications taguées qui publient vers npm `beta` par défaut, ou vers npm `latest` sur demande explicite
- beta : des tags de prépublication qui publient vers npm `beta`
- dev : la tête mobile de `main`

## Dénomination des versions

- Version de publication stable : `YYYY.M.D`
  - Tag Git : `vYYYY.M.D`
- Version de publication corrective stable : `YYYY.M.D-N`
  - Tag Git : `vYYYY.M.D-N`
- Version de prépublication beta : `YYYY.M.D-beta.N`
  - Tag Git : `vYYYY.M.D-beta.N`
- Ne remplissez pas le mois ou le jour avec des zéros
- `latest` signifie la publication npm stable promue actuelle
- `beta` signifie la cible d’installation beta actuelle
- Les publications stables et les publications correctives stables publient vers npm `beta` par défaut ; les opérateurs de publication peuvent cibler explicitement `latest`, ou promouvoir plus tard une build beta validée
- Chaque publication OpenClaw livre ensemble le package npm et l’app macOS

## Cadence de publication

- Les publications passent d’abord par beta
- Stable ne suit qu’après validation de la dernière beta
- La procédure de publication détaillée, les approbations, les identifiants et les notes de récupération sont réservés aux mainteneurs

## Vérifications préalables à la publication

- Exécutez `pnpm build && pnpm ui:build` avant `pnpm release:check` afin que les artefacts de publication `dist/*` attendus et le bundle de l’interface utilisateur de Control existent pour l’étape de validation du pack
- Exécutez `pnpm release:check` avant chaque publication taguée
- Les vérifications de publication s’exécutent désormais dans un workflow manuel séparé :
  `OpenClaw Release Checks`
- Cette séparation est intentionnelle : garder le vrai chemin de publication npm court, déterministe et centré sur les artefacts, tandis que les vérifications live plus lentes restent dans leur propre canal afin de ne pas ralentir ni bloquer la publication
- Les vérifications de publication doivent être déclenchées depuis la référence de workflow `main` afin que la logique du workflow et les secrets restent canoniques
- Ce workflow accepte soit un tag de publication existant, soit le SHA de commit `main` complet actuel sur 40 caractères
- En mode commit-SHA, il n’accepte que le HEAD actuel de `origin/main` ; utilisez un tag de publication pour des commits de publication plus anciens
- La vérification préalable en mode validation uniquement de `OpenClaw NPM Release` accepte aussi le SHA de commit `main` complet actuel sur 40 caractères sans exiger de tag poussé
- Ce chemin SHA est uniquement destiné à la validation et ne peut pas être promu en véritable publication
- En mode SHA, le workflow synthétise `v<package.json version>` uniquement pour la vérification des métadonnées du package ; la véritable publication exige toujours un vrai tag de publication
- Les deux workflows gardent le vrai chemin de publication et de promotion sur des runners hébergés par GitHub, tandis que le chemin de validation non mutatif peut utiliser les runners Linux Blacksmith plus grands
- Ce workflow exécute
  `OPENCLAW_LIVE_TEST=1 OPENCLAW_LIVE_CACHE_TEST=1 pnpm test:live:cache`
  en utilisant à la fois les secrets de workflow `OPENAI_API_KEY` et `ANTHROPIC_API_KEY`
- La vérification préalable de la publication npm n’attend plus le canal séparé des vérifications de publication
- Exécutez `RELEASE_TAG=vYYYY.M.D node --import tsx scripts/openclaw-npm-release-check.ts`
  (ou le tag beta/correctif correspondant) avant approbation
- Après la publication npm, exécutez
  `node --import tsx scripts/openclaw-npm-postpublish-verify.ts YYYY.M.D`
  (ou la version beta/corrective correspondante) pour vérifier le chemin d’installation du registre publié dans un préfixe temporaire vierge
- L’automatisation de publication des mainteneurs utilise désormais le modèle vérification-préalable-puis-promotion :
  - la véritable publication npm doit réussir un `preflight_run_id` npm valide
  - les publications npm stables ciblent `beta` par défaut
  - une publication npm stable peut cibler explicitement `latest` via une entrée de workflow
  - la promotion npm stable de `beta` vers `latest` reste disponible comme mode manuel explicite dans le workflow approuvé `OpenClaw NPM Release`
  - les publications stables directes peuvent aussi exécuter un mode explicite de synchronisation des dist-tags qui pointe à la fois `latest` et `beta` vers la version stable déjà publiée
  - ces modes de dist-tag nécessitent toujours un `NPM_TOKEN` valide dans l’environnement `npm-release`, car la gestion des `npm dist-tag` est séparée de la publication approuvée
  - `macOS Release` public est uniquement destiné à la validation
  - la véritable publication privée mac doit réussir des `preflight_run_id` et `validate_run_id` privés mac valides
  - les vrais chemins de publication promeuvent les artefacts préparés au lieu de les reconstruire à nouveau
- Pour les publications correctives stables comme `YYYY.M.D-N`, le vérificateur post-publication contrôle aussi le même chemin de mise à niveau en préfixe temporaire de `YYYY.M.D` vers `YYYY.M.D-N` afin que les correctifs de publication ne puissent pas laisser silencieusement d’anciennes installations globales sur la charge utile stable de base
- La vérification préalable de publication npm échoue en mode fermé à moins que le tarball inclue à la fois `dist/control-ui/index.html` et une charge utile non vide `dist/control-ui/assets/` afin d’éviter d’expédier à nouveau un tableau de bord navigateur vide
- Si le travail de publication a touché à la planification CI, aux manifestes de temporisation des extensions ou aux matrices de test des extensions, régénérez et examinez les sorties de matrice de workflow `checks-node-extensions` détenues par le planificateur depuis `.github/workflows/ci.yml` avant approbation afin que les notes de publication ne décrivent pas une disposition CI obsolète
- L’état de préparation d’une publication stable macOS inclut aussi les surfaces du programme de mise à jour :
  - la publication GitHub doit finalement contenir les fichiers empaquetés `.zip`, `.dmg` et `.dSYM.zip`
  - `appcast.xml` sur `main` doit pointer vers le nouveau zip stable après publication
  - l’app empaquetée doit conserver un bundle id non debug, une URL de flux Sparkle non vide, et un `CFBundleVersion` supérieur ou égal au seuil de build Sparkle canonique pour cette version de publication

## Entrées du workflow NPM

`OpenClaw NPM Release` accepte ces entrées contrôlées par l’opérateur :

- `tag` : tag de publication requis tel que `v2026.4.2`, `v2026.4.2-1`, ou `v2026.4.2-beta.1` ; lorsque `preflight_only=true`, il peut aussi s’agir du SHA de commit `main` complet actuel sur 40 caractères pour une vérification préalable en mode validation uniquement
- `preflight_only` : `true` pour validation/build/package uniquement, `false` pour le vrai chemin de publication
- `preflight_run_id` : requis sur le vrai chemin de publication afin que le workflow réutilise le tarball préparé à partir du run de vérification préalable réussi
- `npm_dist_tag` : dist-tag npm cible pour le chemin de publication ; vaut `beta` par défaut
- `promote_beta_to_latest` : `true` pour ignorer la publication et déplacer une build stable `beta` déjà publiée vers `latest`
- `sync_stable_dist_tags` : `true` pour ignorer la publication et pointer à la fois `latest` et `beta` vers une version stable déjà publiée

`OpenClaw Release Checks` accepte ces entrées contrôlées par l’opérateur :

- `ref` : tag de publication existant ou SHA de commit `main` complet actuel sur 40 caractères à valider

Règles :

- Les tags stables et correctifs peuvent publier soit vers `beta`, soit vers `latest`
- Les tags de prépublication beta ne peuvent publier que vers `beta`
- Une entrée SHA de commit complet n’est autorisée que lorsque `preflight_only=true`
- Le mode commit-SHA des vérifications de publication exige aussi le HEAD actuel de `origin/main`
- Le vrai chemin de publication doit utiliser le même `npm_dist_tag` que celui utilisé pendant la vérification préalable ; le workflow vérifie ces métadonnées avant de poursuivre la publication
- Le mode promotion doit utiliser un tag stable ou correctif, `preflight_only=false`, un `preflight_run_id` vide, et `npm_dist_tag=beta`
- Le mode synchronisation des dist-tags doit utiliser un tag stable ou correctif, `preflight_only=false`, un `preflight_run_id` vide, `npm_dist_tag=latest`, et `promote_beta_to_latest=false`
- Les modes promotion et synchronisation des dist-tags exigent aussi un `NPM_TOKEN` valide, car `npm dist-tag add` nécessite toujours une authentification npm classique ; la publication approuvée ne couvre que le chemin de publication du package

## Séquence de publication npm stable

Lors de la création d’une publication npm stable :

1. Exécutez `OpenClaw NPM Release` avec `preflight_only=true`
   - Avant qu’un tag existe, vous pouvez utiliser le SHA complet du commit `main` actuel pour un essai à blanc en mode validation uniquement du workflow de vérification préalable
2. Choisissez `npm_dist_tag=beta` pour le flux normal beta-first, ou `latest` uniquement lorsque vous souhaitez intentionnellement une publication stable directe
3. Exécutez `OpenClaw Release Checks` séparément avec le même tag ou le SHA complet actuel de `main` lorsque vous souhaitez une couverture live du cache de prompt
   - Cela est volontairement séparé pour que la couverture live reste disponible sans recoupler des vérifications longues ou instables au workflow de publication
4. Enregistrez le `preflight_run_id` réussi
5. Exécutez à nouveau `OpenClaw NPM Release` avec `preflight_only=false`, le même `tag`, le même `npm_dist_tag`, et le `preflight_run_id` enregistré
6. Si la publication est arrivée sur `beta`, exécutez plus tard `OpenClaw NPM Release` avec le même `tag` stable, `promote_beta_to_latest=true`, `preflight_only=false`, `preflight_run_id` vide, et `npm_dist_tag=beta` lorsque vous souhaitez déplacer cette build publiée vers `latest`
7. Si la publication a été intentionnellement publiée directement vers `latest` et que `beta` doit suivre la même build stable, exécutez `OpenClaw NPM Release` avec le même `tag` stable, `sync_stable_dist_tags=true`, `promote_beta_to_latest=false`, `preflight_only=false`, `preflight_run_id` vide, et `npm_dist_tag=latest`

Les modes promotion et synchronisation des dist-tags exigent toujours l’approbation de l’environnement `npm-release` et un `NPM_TOKEN` valide accessible à l’exécution de ce workflow.

Cela permet de documenter et de rendre visibles pour les opérateurs à la fois le chemin de publication directe et le chemin de promotion beta-first.

## Références publiques

- [`.github/workflows/openclaw-npm-release.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-npm-release.yml)
- [`.github/workflows/openclaw-release-checks.yml`](https://github.com/openclaw/openclaw/blob/main/.github/workflows/openclaw-release-checks.yml)
- [`scripts/openclaw-npm-release-check.ts`](https://github.com/openclaw/openclaw/blob/main/scripts/openclaw-npm-release-check.ts)
- [`scripts/package-mac-dist.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/package-mac-dist.sh)
- [`scripts/make_appcast.sh`](https://github.com/openclaw/openclaw/blob/main/scripts/make_appcast.sh)

Les mainteneurs utilisent la documentation privée de publication dans
[`openclaw/maintainers/release/README.md`](https://github.com/openclaw/maintainers/blob/main/release/README.md)
pour la procédure réelle.
