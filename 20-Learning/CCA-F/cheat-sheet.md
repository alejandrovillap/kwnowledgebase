---
title: Cheat sheet
date: 2026-04-12
type: reference
technology: "gen-ai"
status: active
tags: ["cca-exam", "cheat-sheet", agentic, mcp, "claude-code", "structured-output", "context-window"]
keywords: [CCA exam, cheat sheet, D1, D2, D3, D4, D5, agentic, MCP, tools, structured output, context window]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# CCA Exam — Cheat Sheet

## D1 — Agentic Architecture & Orchestration (27%)

### Agentes vs Pipelines
```
Pipeline → el desarrollador decide el flujo antes de ejecutar
Agente   → Claude decide el siguiente paso durante la ejecución
```

### Orquestador vs Subagente
```
Orquestador → piensa, coordina, delega
Subagente   → actúa, ejecuta, reporta
Subagentes NO heredan contexto → se pasa explícitamente
```

### Patrones CPRE
```
Cadena       → pasos secuenciales, uno depende del anterior
Paralelo     → tareas independientes simultáneas
Router       → clasifica y manda al especialista correcto
Evaluador    → genera → revisa → itera hasta calidad suficiente
```

### stop_reason
```
"tool_use"  → Claude necesita una herramienta → el sistema ejecuta y devuelve resultado
"end_turn"  → Claude terminó → el sistema presenta respuesta final
Anti-patrón → parsear texto para detectar si terminó
```

### Task tool + allowedTools
```
allowedTools debe incluir "Task" para que el coordinador delegue
Paralelismo → múltiples Task calls en UNA SOLA respuesta
```

### Hooks
```
PostToolUse         → normaliza datos DESPUÉS de que la herramienta devuelve resultado
Interceptación      → bloquea ANTES de que la herramienta se ejecute
Hook                → determinístico, garantizado
Prompt              → probabilístico, puede fallar
```

### Programmatic enforcement
```
Prompt → tasa de fallo no cero
Hook/gate programático → 100% garantizado
"A veces se salta el paso" → siempre es problema de prompt → solución programática
```

### fork_session vs --resume
```
fork_session  → dos ramas independientes desde el mismo punto
--resume      → continúa sesión anterior específica
```

---

## D2 — Tool Design & MCP Integration (18%)

### Descripciones de herramientas
```
Descripción = mecanismo primario de selección
Descripción vaga → Claude selecciona herramienta incorrecta
Solución → descripción con: qué hace, inputs, ejemplos, cuándo NO usarla
```

### tool_choice
```
"auto"   → Claude decide si usa herramienta o responde con texto
"any"    → Claude DEBE usar alguna herramienta, elige cuál
forzado  → Claude DEBE usar herramienta específica
{"type": "tool", "name": "extract_metadata"}
```

### isError + tipos de error
```
transient  → timeout, servicio caído     → reintentable ✅
validation → input inválido              → no reintentable ❌
business   → regla de negocio            → no reintentable ❌
permission → sin autorización            → no reintentable ❌

Subagente resuelve transitorios localmente
Solo propaga lo que no puede resolver
```

### MCP Resources vs Tools
```
Tools     → acciones, Claude las invoca para hacer algo
Resources → catálogos, Claude los consulta para saber qué existe
Resources → eliminan tool calls exploratorios
```

### Máximo de herramientas
```
Máximo 4-5 herramientas por agente
Más herramientas → peor selección
Principio de menor privilegio → solo lo necesario para su rol
```

### Archivos de configuración MCP
```
.mcp.json        → proyecto, equipo, en Git, compartido
~/.claude.json   → personal, solo yo, nunca en Git
~ = personal     . sin ~ = proyecto
```

---

## D3 — Claude Code Configuration & Workflows (20%)

### Flags de CI/CD
```
-p / --print → modo no-interactivo, piloto automático
 sin esto → pipeline se congela
--output-format json → output parseable por máquinas
```

### CLAUDE.md — 3 niveles
```
~/.claude/CLAUDE.md     → personal, solo yo, no en Git
CLAUDE.md raíz          → proyecto, todo el equipo, en Git
src/pagos/CLAUDE.md     → solo cuando trabajas en esa carpeta
```

### .claude/rules/ con glob patterns
```
.claude/rules/testing.md
---
paths: ["**/*.test.tsx"]   ← frontmatter YAML
---
→ Se activa cuando el archivo coincide con el patrón
→ Para archivos distribuidos por tipo en todo el repo

Subdirectorio CLAUDE.md → reglas para UNA CARPETA
.claude/rules/ + glob   → reglas para UN TIPO DE ARCHIVO
```

### @import
```
@import .claude/rules/security.md
→ Referencia archivo existente desde CLAUDE.md
→ Mantiene CLAUDE.md modular y limpio
```

### Skills vs Commands vs CLAUDE.md
```
CLAUDE.md         → siempre activo, estándares universales
Commands          → invocación manual, resultado en sesión principal
                    .claude/commands/     → equipo, en Git
                    ~/.claude/commands/   → personal, solo yo

Skills            → invocación manual, sesión aislada
                    .claude/skills/       → equipo, en Git
                    ~/.claude/skills/     → personal, solo yo
                    
Frontmatter de Skills:
context: fork     → sesión aislada, no contamina conversación principal
allowed-tools     → restringe herramientas disponibles
argument-hint     → pide parámetro cuando se invoca sin argumentos
```

### Plan Mode vs Direct Execution
```
Plan Mode         → múltiples archivos, decisiones arquitectónicas
Direct Execution  → cambio simple, un archivo, alcance claro
```

### Message Batches API
```
50% ahorro en costo
Hasta 24 horas de procesamiento
Sin SLA de latencia garantizado
Solo para workloads NO bloqueantes
Nunca para pre-merge checks o procesos que bloquean al usuario
```

---

## D4 — Prompt Engineering & Structured Output (20%)

### Few-shot prompting
```
Output inconsistente → few-shot examples
2-4 ejemplos concretos de input/output
Demuestran formato, casos ambiguos, qué reportar y qué NO
Más efectivo que instrucciones en prosa
```

### Criterios explícitos vs vagos
```
"Sé conservador"           → vago, no funciona
"Reporta SOLO cuando X"    → explícito, funciona
Vago = interpretación de Claude
Explícito = tu estándar
```

### tool_use + JSON schemas
```
Elimina:     errores de sintaxis JSON
Elimina:     campos faltantes obligatorios  
Elimina:     tipos de dato incorrectos
NO elimina:  errores semánticos
             (totales que no cuadran, valores en campos equivocados)
```

### Nullable — anti-alucinación
```
Campo requerido + información ausente → Claude inventa
Campo nullable + información ausente  → Claude devuelve null

"type": ["string", "null"]
```

### Multi-pass review
```
Pasada local       → cada archivo individualmente
Pasada integración → inconsistencias entre archivos
Sesión independiente → nunca la misma sesión que generó revisa
"El que hizo el examen no lo califica"
```

---

## D5 — Context Management & Reliability (15%)

### PRINCIPIOS TRANSVERSALES — Memorizar siempre
```
1. Programmatic enforcement > Prompt guidance
   Si DEBE garantizarse → código, no prompt

2. Sesión independiente para revisión
   Nunca el mismo Claude que generó → revisa

3. -p flag = piloto automático en CI/CD

4. Message Batches = 50% ahorro, sin urgencia

5. context:fork = subagente aislado, no contamina

6. ~ = personal, sin ~ = proyecto

7. Plan mode = multi-archivo, arquitectura
   Direct execution = cambio simple

8. stop_reason = "tool_use" → sigue
   stop_reason = "end_turn" → para

9. Nullable = anti-alucinación

10. Descripción de herramienta = mecanismo primario de selección
```
