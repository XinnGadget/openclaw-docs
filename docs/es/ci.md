---
read_when:
    - Necesitas entender por qué un trabajo de CI se ejecutó o no se ejecutó
    - Estás depurando verificaciones fallidas de GitHub Actions
summary: Gráfico de trabajos de CI, puertas de alcance y equivalentes de comandos locales
title: Canalización de CI
x-i18n:
    generated_at: "2026-04-11T02:44:16Z"
    model: gpt-5.4
    provider: openai
    source_hash: ca7e355b7f73bfe8ea8c6971e78164b8b2e68cbb27966964955e267fed89fce6
    source_path: ci.md
    workflow: 15
---

# Canalización de CI

La CI se ejecuta en cada push a `main` y en cada pull request. Usa un alcance inteligente para omitir trabajos costosos cuando solo cambiaron áreas no relacionadas.

## Resumen de trabajos

| Trabajo                  | Propósito                                                                               | Cuándo se ejecuta                    |
| ------------------------ | --------------------------------------------------------------------------------------- | ------------------------------------ |
| `preflight`              | Detectar cambios solo en docs, alcances modificados, extensiones modificadas y compilar el manifiesto de CI | Siempre en pushes y PR no borrador   |
| `security-fast`          | Detección de claves privadas, auditoría de workflows con `zizmor`, auditoría de dependencias de producción | Siempre en pushes y PR no borrador   |
| `build-artifacts`        | Compilar `dist/` y la UI de Control una vez, y subir artefactos reutilizables para trabajos posteriores | Cambios relevantes para Node         |
| `checks-fast-core`       | Carriles rápidos de corrección en Linux, como verificaciones de bundled/plugin-contract/protocol | Cambios relevantes para Node         |
| `checks-node-extensions` | Shards completos de pruebas de bundled-plugin en toda la suite de extensiones           | Cambios relevantes para Node         |
| `checks-node-core-test`  | Shards de pruebas principales de Node, excluyendo carriles de canal, bundled, contrato y extensión | Cambios relevantes para Node         |
| `extension-fast`         | Pruebas enfocadas solo en los plugins empaquetados modificados                          | Cuando se detectan cambios en extensiones |
| `check`                  | Puerta local principal en CI: `pnpm check` más `pnpm build:strict-smoke`               | Cambios relevantes para Node         |
| `check-additional`       | Guardas de arquitectura, límites e import-cycle, más el arnés de regresión de observación del gateway | Cambios relevantes para Node         |
| `build-smoke`            | Pruebas smoke de la CLI compilada y smoke de memoria al iniciar                         | Cambios relevantes para Node         |
| `checks`                 | Carriles restantes de Node en Linux: pruebas de canales y compatibilidad con Node 22 solo en push | Cambios relevantes para Node         |
| `check-docs`             | Formato de docs, lint y comprobaciones de enlaces rotos                                 | Cuando cambian las docs              |
| `skills-python`          | Ruff + pytest para Skills con backend en Python                                         | Cambios relevantes para Skills de Python |
| `checks-windows`         | Carriles de prueba específicos de Windows                                               | Cambios relevantes para Windows      |
| `macos-node`             | Carril de pruebas de TypeScript en macOS usando los artefactos compilados compartidos   | Cambios relevantes para macOS        |
| `macos-swift`            | Lint, compilación y pruebas de Swift para la app de macOS                               | Cambios relevantes para macOS        |
| `android`                | Matriz de compilación y pruebas de Android                                              | Cambios relevantes para Android      |

## Orden de fail-fast

Los trabajos se ordenan para que las verificaciones baratas fallen antes de que se ejecuten las costosas:

1. `preflight` decide qué carriles existen en primer lugar. La lógica de `docs-scope` y `changed-scope` son pasos dentro de este trabajo, no trabajos independientes.
2. `security-fast`, `check`, `check-additional`, `check-docs` y `skills-python` fallan rápido sin esperar a los trabajos más pesados de artefactos y matrices de plataforma.
3. `build-artifacts` se superpone con los carriles rápidos de Linux para que los consumidores posteriores puedan empezar en cuanto la compilación compartida esté lista.
4. Después se distribuyen los carriles más pesados de plataforma y tiempo de ejecución: `checks-fast-core`, `checks-node-extensions`, `checks-node-core-test`, `extension-fast`, `checks`, `checks-windows`, `macos-node`, `macos-swift` y `android`.

La lógica de alcance vive en `scripts/ci-changed-scope.mjs` y está cubierta por pruebas unitarias en `src/scripts/ci-changed-scope.test.ts`.
El workflow independiente `install-smoke` reutiliza el mismo script de alcance mediante su propio trabajo `preflight`. Calcula `run_install_smoke` a partir de la señal más acotada de cambios relevantes para smoke, por lo que el smoke de Docker/instalación solo se ejecuta para cambios relevantes para instalación, empaquetado y contenedores.

En los pushes, la matriz `checks` agrega el carril `compat-node22`, que solo se ejecuta en push. En los pull requests, ese carril se omite y la matriz se mantiene enfocada en los carriles normales de pruebas/canales.

## Runners

| Runner                           | Trabajos                                                                                             |
| -------------------------------- | ---------------------------------------------------------------------------------------------------- |
| `blacksmith-16vcpu-ubuntu-2404`  | `preflight`, `security-fast`, `build-artifacts`, verificaciones de Linux, comprobaciones de docs, Skills de Python, `android` |
| `blacksmith-32vcpu-windows-2025` | `checks-windows`                                                                                     |
| `macos-latest`                   | `macos-node`, `macos-swift`                                                                          |

## Equivalentes locales

```bash
pnpm check          # tipos + lint + formato
pnpm build:strict-smoke
pnpm check:import-cycles
pnpm test:gateway:watch-regression
pnpm test           # pruebas de vitest
pnpm test:channels
pnpm check:docs     # formato de docs + lint + enlaces rotos
pnpm build          # compila dist cuando importan los carriles de artefactos/ build-smoke de CI
```
