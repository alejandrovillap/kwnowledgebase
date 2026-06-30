---
title: Los 3 niveles de CLAUDE.md
date: 2026-04-10
type: resume
technology: "gen-ai"
status: active
tags: ["claude-md", "claude-code", "file-structure", configuration, hierarchy, "project-organization"]
keywords: [CLAUDE.md, niveles, usuario, proyecto, directorio, rules, glob, /memory, Claude Code, CCA, D3]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Los 3 niveles de CLAUDE.md

## La manzanita — Reglas de empresa internacional

- **Nivel usuario** `~/.claude/CLAUDE.md` = Tus preferencias personales en tu cajón. Tu idioma, tu estilo. Solo tú las ves. No van al repo.
- **Nivel proyecto** `.claude/CLAUDE.md` o `CLAUDE.md` en la raíz = El reglamento oficial del proyecto. Está en Git. Todos lo reciben al clonar.
- **Nivel directorio** = `CLAUDE.md` dentro de una subcarpeta específica = Las reglas especiales del departamento de finanzas que solo aplican cuando trabajas en esa área.

## Jerarquía formal

```
~/.claude/CLAUDE.md          ← Solo tú. No en Git.
│
REPOSITORIO/
├── CLAUDE.md                ← Todo el equipo. En Git.
├── .claude/
│   └── CLAUDE.md            ← Todo el equipo. En Git.
├── src/
│   └── api/
│       └── CLAUDE.md        ← Solo aplica en /api/
└── src/
    └── payments/
        └── CLAUDE.md        ← Solo aplica en /payments/
```

**Regla crítica:** Las instrucciones en `~/.claude/CLAUDE.md` a nivel usuario **no se comparten** con compañeros de equipo a través del control de versiones.

## Estructura estándar completa de Claude Code

```
REPOSITORIO/ (raíz del proyecto)
│
├── CLAUDE.md                    ← Nivel proyecto (opción 1)
│
├── .claude/                     ← Carpeta oficial de Claude
│   ├── CLAUDE.md                ← Nivel proyecto (opción 2)
│   ├── commands/                ← Commands del equipo
│   │   ├── review.md
│   │   └── deploy.md
│   ├── skills/                  ← Skills del equipo
│   │   └── analyze.md
│   └── rules/                   ← Reglas condicionales
│       ├── testing.md           ← paths: ["**/*.test.tsx"]
│       ├── api.md               ← paths: ["src/api/**/*"]
│       └── terraform.md         ← paths: ["terraform/**/*"]
│
├── src/
│   ├── api/
│   │   └── CLAUDE.md            ← Nivel directorio (solo aplica en /api/)
│   └── payments/
│       └── CLAUDE.md            ← Nivel directorio (solo aplica en /payments/)
│
~/.claude/                       ← Fuera del repo, en tu máquina
    ├── CLAUDE.md                ← Nivel usuario (solo tú)
    ├── commands/                ← Commands personales
    └── skills/                  ← Skills personales
```

## Regla de carga — cuándo se activa cada nivel

| Nivel | Se carga cuando... | Siempre activo |
|---|---|---|
| Usuario `~/.claude/CLAUDE.md` | Siempre, en cualquier proyecto | ✅ |
| Proyecto `CLAUDE.md` raíz | Siempre dentro del proyecto | ✅ |
| Directorio `src/api/CLAUDE.md` | Solo cuando editas archivos en `/api/` | ❌ Condicional |
| Rules `.claude/rules/testing.md` | Solo cuando el archivo coincide con el glob pattern | ❌ Condicional |

## Directorio CLAUDE.md vs `.claude/rules/` — la trampa del examen

**Directorio CLAUDE.md** → aplica a todo lo que está dentro de esa carpeta y sus subcarpetas. Útil cuando las reglas son *geográficas* — todo lo de `/payments/` sigue las mismas reglas.

**`.claude/rules/` con glob** → aplica por tipo de archivo sin importar dónde esté. Útil cuando las reglas siguen al *archivo*, no a la carpeta.

```
¿Las reglas aplican a UNA CARPETA específica?
→ Subdirectorio CLAUDE.md

¿Las reglas aplican a UN TIPO DE ARCHIVO distribuido por todo el repo?
→ .claude/rules/ con glob pattern
```

## Anti-patrones vs Patrones correctos

| ❌ Anti-patrón | ✅ Patrón correcto |
|---|---|
| Poner estándares del equipo en `~/.claude/CLAUDE.md` | Estándares del equipo van en `CLAUDE.md` a nivel proyecto en el repo |
| Un nuevo miembro del equipo no recibe las instrucciones | Diagnóstico: están en nivel usuario, no proyecto |
| Un `CLAUDE.md` enorme con todas las reglas mezcladas | Dividir en niveles + usar `@import` para modularizar |

## Cómo verificar cuáles están cargadas: `/memory`

```
/memory
→ Te muestra lista de archivos actualmente cargados:
  - ~/.claude/CLAUDE.md ✓
  - /proyecto/CLAUDE.md ✓
  - /proyecto/src/api/CLAUDE.md ✓ (porque estás editando en /api/)
  - /proyecto/.claude/rules/testing.md ✓ (porque el archivo abierto es .test.tsx)
```

## Tip de examen — la pregunta diagnóstica más común

> "Un nuevo desarrollador clonó el repo y Claude no sigue las instrucciones del equipo"

Proceso de eliminación:
1. ¿Están en `~/.claude/CLAUDE.md`? → **Problema** — eso es personal, no se comparte en Git
2. ¿Están en `CLAUDE.md` raíz? → **Correcto** — eso sí va en Git
3. ¿Usa `/memory` para verificar? → **Correcto** — así diagnosticas

**Tip rápido: "¿Quién lo ve?"**
- Solo yo → `~/.claude/CLAUDE.md`
- Todo el equipo → raíz del repo
- Solo ese directorio → subdirectorio
