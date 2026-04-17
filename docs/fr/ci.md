---
read_when:
    - Vous devez comprendre pourquoi une tâche CI s'est exécutée ou non
    - Vous déboguez des vérifications GitHub Actions en échec
summary: Graphe des tâches CI, portes de portée et équivalents des commandes locales
title: Pipeline CI
x-i18n:
    generated_at: "2026-04-11T02:44:19Z"
    model: gpt-5.4
    provider: openai
    source_hash: ca7e355b7f73bfe8ea8c6971e78164b8b2e68cbb27966964955e267fed89fce6
    source_path: ci.md
    workflow: 15
---

# Pipeline CI

La CI s'exécute à chaque push vers `main` et sur chaque pull request. Elle utilise une portée intelligente pour ignorer les tâches coûteuses lorsque seules des zones sans lien ont changé.

## Vue d'ensemble des tâches

| Tâche                    | Objectif                                                                                | Quand elle s'exécute                |
| ------------------------ | --------------------------------------------------------------------------------------- | ----------------------------------- |
| `preflight`              | Détecter les changements docs uniquement, les portées modifiées, les extensions modifiées, et construire le manifeste CI | Toujours sur les pushs et PR non-brouillons |
| `security-fast`          | Détection de clés privées, audit des workflows via `zizmor`, audit des dépendances de production | Toujours sur les pushs et PR non-brouillons |
| `build-artifacts`        | Construire `dist/` et la Control UI une seule fois, téléverser des artefacts réutilisables pour les tâches en aval | Changements pertinents pour Node    |
| `checks-fast-core`       | Voies rapides de validation Linux comme les vérifications bundled/plugin-contract/protocol | Changements pertinents pour Node    |
| `checks-node-extensions` | Fragmentation complète des tests de bundled-plugin sur toute la suite d'extensions      | Changements pertinents pour Node    |
| `checks-node-core-test`  | Fragmentation des tests Node du cœur, en excluant les voies channel, bundled, contract et extension | Changements pertinents pour Node    |
| `extension-fast`         | Tests ciblés uniquement pour les bundled plugins modifiés                               | Lorsque des changements d'extension sont détectés |
| `check`                  | Porte locale principale dans la CI : `pnpm check` plus `pnpm build:strict-smoke`        | Changements pertinents pour Node    |
| `check-additional`       | Garde-fous d'architecture, de limites et de cycles d'import, plus le harnais de régression gateway watch | Changements pertinents pour Node    |
| `build-smoke`            | Tests smoke de la CLI construite et smoke de mémoire au démarrage                       | Changements pertinents pour Node    |
| `checks`                 | Voies Linux Node restantes : tests de channel et compatibilité Node 22 uniquement sur push | Changements pertinents pour Node    |
| `check-docs`             | Vérifications de formatage, lint et liens cassés de la documentation                    | Documentation modifiée              |
| `skills-python`          | Ruff + pytest pour les Skills adossées à Python                                         | Changements pertinents pour les Skills Python |
| `checks-windows`         | Voies de test spécifiques à Windows                                                     | Changements pertinents pour Windows |
| `macos-node`             | Voie de test TypeScript sur macOS utilisant les artefacts partagés déjà construits      | Changements pertinents pour macOS   |
| `macos-swift`            | Lint, build et tests Swift pour l'app macOS                                             | Changements pertinents pour macOS   |
| `android`                | Matrice de build et de tests Android                                                    | Changements pertinents pour Android |

## Ordre fail-fast

Les tâches sont ordonnées de sorte que les vérifications peu coûteuses échouent avant le lancement des plus coûteuses :

1. `preflight` décide quelles voies existent réellement. La logique `docs-scope` et `changed-scope` correspond à des étapes à l'intérieur de cette tâche, pas à des tâches autonomes.
2. `security-fast`, `check`, `check-additional`, `check-docs` et `skills-python` échouent rapidement sans attendre les tâches plus lourdes d'artefacts et de matrice plateforme.
3. `build-artifacts` s'exécute en parallèle des voies Linux rapides afin que les consommateurs en aval puissent démarrer dès que le build partagé est prêt.
4. Les voies plus lourdes de plateforme et d'exécution se déploient ensuite : `checks-fast-core`, `checks-node-extensions`, `checks-node-core-test`, `extension-fast`, `checks`, `checks-windows`, `macos-node`, `macos-swift` et `android`.

La logique de portée se trouve dans `scripts/ci-changed-scope.mjs` et est couverte par des tests unitaires dans `src/scripts/ci-changed-scope.test.ts`.
Le workflow séparé `install-smoke` réutilise le même script de portée via sa propre tâche `preflight`. Il calcule `run_install_smoke` à partir du signal `changed-smoke` plus restreint, afin que le smoke Docker/install ne s'exécute que pour les changements pertinents pour l'installation, le packaging et les conteneurs.

Sur les pushs, la matrice `checks` ajoute la voie `compat-node22`, uniquement sur push. Sur les pull requests, cette voie est ignorée et la matrice reste concentrée sur les voies normales de test/channel.

## Exécuteurs

| Exécuteur                        | Tâches                                                                                              |
| -------------------------------- | --------------------------------------------------------------------------------------------------- |
| `blacksmith-16vcpu-ubuntu-2404`  | `preflight`, `security-fast`, `build-artifacts`, vérifications Linux, vérifications docs, Skills Python, `android` |
| `blacksmith-32vcpu-windows-2025` | `checks-windows`                                                                                    |
| `macos-latest`                   | `macos-node`, `macos-swift`                                                                         |

## Équivalents locaux

```bash
pnpm check          # types + lint + format
pnpm build:strict-smoke
pnpm check:import-cycles
pnpm test:gateway:watch-regression
pnpm test           # tests vitest
pnpm test:channels
pnpm check:docs     # format docs + lint + liens cassés
pnpm build          # construit dist/ lorsque les voies CI artifact/build-smoke sont concernées
```
