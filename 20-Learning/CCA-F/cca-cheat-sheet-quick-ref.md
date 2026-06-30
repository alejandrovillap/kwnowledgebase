---
title: CCA Cheat Sheet — Quick Reference
date: 2026-03-25
type: reference
technology: "gen-ai"
status: active
tags: ["cca-exam", "claude-agents", "tool-design", mcp, "prompt-engineering", orchestration]
keywords: [CCA cheat sheet, D1 D2 D3 D4 D5, fallback loop, tool schema, CLAUDE.md, prompt engineering, context management, retry loop, handoff patterns, confidence calibration, exam traps, decision tree]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# CCA Cheat Sheet — Quick Reference

Full quick reference across all 5 exam domains with decision trees and common traps.

---

## D1 — Agentic Architecture & Orchestration (27%)

**Concepto central: Claude orquesta, no ejecuta. El agente decide y delega — nunca hace el trabajo directamente.**

### Componentes clave

| Concepto | Definición |
|---|---|
| Orquestador | Claude que coordina subagentes y decide el flujo |
| Subagente | Claude especializado en una sola tarea |
| Hub-and-spoke | Un orquestador central + N subagentes especializados |
| Task decomposition | Dividir tarea compleja en subtareas atómicas para subagentes |
| Agentic loop | El ciclo: planear → actuar → observar → replantear |

### Fallback Loop — el patrón más importante del D1

| Paso | Qué ocurre |
|---|---|
| 1. Tool call | Claude invoca una tool y espera resultado |
| 2. Tool falla | is_error: true — Claude recibe el error como contexto |
| 3. Retry con backoff | Reintenta con espera: 1s, 2s, 4s |
| 4. max_retries agotado | Retorna tool_result con is_error: true controlado |
| 5. max_turns alcanzado | Escala a humano con Escalation Package |

> **TRAMPA:** Poner restricciones de seguridad en el system prompt del subagente no es suficiente. El código debe garantizar los límites — el prompt solo sugiere.

---

## D2 — Tool Design & MCP Integration (18%)

**Concepto central: Claude decide y arma instrucciones. Tu código ejecuta. MCP transporta. Nunca al revés.**

### Tool Schema — los 3 campos

| Campo | Regla crítica |
|---|---|
| name | snake_case, verbo+objeto, una sola acción. Malo: `orderTool`. Bueno: `cancel_order` |
| description | Dice CUÁNDO usarla, no qué hace. Fórmula: `Use when [cuando + sinónimos]. [Precondición]. Do NOT use when [cuando no].` |
| input_schema | Cada property con type y description con formato esperado. `required` solo lo imprescindible. |

> **TRAMPA:** Una tool con parámetro `action` que hace get/cancel/update es un error de arquitectura. Una tool = una acción atómica. Un schema malo produce fallos en cascada.

### MCP Protocol

| Elemento | Definición |
|---|---|
| Host | La aplicación que usa Claude (Claude.ai, tu app) |
| Client | Componente dentro del host que habla el protocolo |
| Server | Servicio externo que expone las tools |
| stdio | Misma máquina, proceso hijo, rápido, sin red |
| SSE | Red/remoto, HTTP, múltiples clients simultáneos |

**Ciclo de vida MCP:** Initialize → Operation (tools/list, tools/call, resources/read) → Shutdown limpio.

### Integration Patterns

| Patrón | Cuándo usarlo |
|---|---|
| Secuencial | Tool B necesita el resultado de Tool A |
| Paralelo | Tools independientes — tiempo = MAX, no suma |
| Context Injection | Datos estáticos que ya tienes — van en system prompt |
| Minimal Permissions | Solo las tools necesarias para esa tarea específica |

> **TRAMPA:** Usar llamadas secuenciales cuando podrían ser paralelas = arquitectura lenta innecesariamente. Pregunta: ¿Tool B necesita resultado de Tool A? Si no = paralelo.

---

## D3 — Claude Code Configuration & Workflows (20%)

**Concepto central: CLAUDE.md le dice cómo comportarse. Slash Commands automatizan procesos. CI/CD ejecuta sin intervención humana.**

### CLAUDE.md — jerarquía

| Nivel | Ubicación y alcance |
|---|---|
| Global (Estrategia) | `~/.claude/CLAUDE.md` — aplica a todos tus proyectos |
| Proyecto (Proyecto) | `./CLAUDE.md` — reglas del proyecto, se versiona con git |
| Local (Feature) | `./src/CLAUDE.md` — reglas del módulo o componente específico |

Regla de prioridad: Local sobreescribe Proyecto, Proyecto sobreescribe Global. Pero solo lo que contradice directamente — el resto sigue vigente.

5 secciones del CLAUDE.md: contexto del proyecto, estándares de código, restricciones, flujo de trabajo, comportamiento esperado.

> **TRAMPA:** No va en CLAUDE.md: secrets, API keys, instrucciones que cambian con cada tarea.

### Slash Commands

- Archivos `.md` en `.claude/commands/` que Claude ejecuta al invocar `/nombre`
- `$ARGUMENTS` captura lo que escribes después del comando
- Scope proyecto: `.claude/commands/` en el repo — se comparte con el equipo via git
- Scope global: `~/.claude/commands/` — solo para ti, funciona en cualquier proyecto
- Un Slash Command = una tarea atómica.

### CI/CD Integration

| Trigger | Caso de uso |
|---|---|
| pull_request | Code review automático — el más común |
| push | Generación de tests para código nuevo |
| schedule (cron) | Reporte nocturno de cambios del día |
| comentario en PR | `@claude review` — revisión bajo demanda |

> **TRAMPA:** GitHub Actions orquesta — Claude Code ejecuta. No son lo mismo. El modo headless = sin interfaz, sin humano presente.

---

## D4 — Prompt Engineering & Structured Output (20%)

**Concepto central: Prompt Engineering controla qué hace Claude. Structured Output controla cómo lo entrega. Retry Loops garantizan que si falla, se corrige solo.**

### Los 5 elementos del prompt perfecto

| Elemento | Qué define |
|---|---|
| Rol | Quién es Claude en esta tarea |
| Contexto | Qué información necesita saber |
| Tarea | Qué debe hacer exactamente |
| Formato | Cómo debe entregar el resultado |
| Límites | Qué no debe hacer |

### 4 técnicas de Prompt Engineering

| Técnica | Cuándo usarla |
|---|---|
| System vs User Prompt | Restricciones críticas SIEMPRE en system prompt — el usuario controla el user prompt |
| Few-shot Examples | Mostrar 2-3 ejemplos input-output en lugar de describir el formato |
| Chain of Thought | Tareas con múltiples pasos lógicos — pide razonar antes de responder |
| Roles y Personas | Activa conocimiento y tono apropiado — no da capacidades nuevas |

### Structured Output

| Técnica | Cuándo usarla |
|---|---|
| JSON Schema | Output que tu código va a parsear — incluir instrucción explícita sin texto extra |
| XML Tags | Secciones con texto libre largo — más legible que JSON con strings escapados |
| Enum | Campo con valores predefinidos — sin enum Claude inventa valores distintos |

### Retry Loop — el patrón correcto

- Validar el output ANTES de usarlo — no asumir que Claude entregó lo correcto
- El error como input del retry — mostrar exactamente qué falló y qué debe corregir
- Max retries típicamente 3 — con fallback explícito al agotarse
- Nunca retornar None sin manejarlo

> **TRAMPA:** Retry malo: "Inténtalo de nuevo." Retry bueno: "Tu output fue X. Error: Y. Corrige exactamente eso." Sin contexto del error Claude falla igual en cada intento.

---

## D5 — Context Management & Reliability (15%)

**Concepto central: Un sistema confiable funciona bien cuando algo falla. Mantiene contexto efectivo, transfiere estado correctamente, y sabe cuándo confiar y cuándo escalar.**

### Context Window Management — 4 estrategias

| Estrategia | Cuándo usarla |
|---|---|
| Summarization | Conversación larga sin estructura — comprime lo procesado |
| Sliding Window | Solo importa lo reciente — descarta mensajes viejos automáticamente |
| Context Injection selectiva | Datos disponibles desde el inicio — inyecta solo lo relevante |
| External Memory | Historial muy largo — guarda en DB, recupera con tool |

> **TRAMPA:** `max_tokens` controla el largo de la RESPUESTA de Claude — no el tamaño de la ventana de contexto. Son parámetros diferentes. No resuelve `ContextWindowExceededError`.

### Handoff Patterns — los 5 elementos del State Snapshot

1. Objetivo original de la tarea
2. Qué se completó hasta ahora
3. Qué falta por hacer
4. Decisiones importantes tomadas y por qué
5. Próximo paso concreto

| Tipo de Handoff | Qué se transfiere |
|---|---|
| Sesión a Sesión | State Snapshot — continúa exactamente donde se quedó |
| Agente a Agente | Handoff Package — solo el contexto relevante para el receptor |
| Claude a Humano | Escalation Package — qué hizo + por qué escala + opciones disponibles |

### Reliability — 3 patrones

| Patrón | Definición |
|---|---|
| Graceful Degradation | Si una parte falla el sistema sigue funcionando parcialmente |
| Idempotency | Verificar en log si la acción ya se ejecutó ANTES de ejecutarla de nuevo |
| Observability | Loggear cada decisión de Claude para auditar y depurar |

### Confidence Calibration

| Nivel de confianza | Acción del sistema |
|---|---|
| 85% – 100% | Sistema actúa automáticamente |
| 60% – 84% | Notifica al humano para confirmar antes de ejecutar |
| 0% – 59% | Escala con Escalation Package completo |

---

## Conexiones entre dominios

| Conexión | Principio compartido |
|---|---|
| D1 cuándo escalar + D5 cómo escalar | Fallback loop define el trigger — Escalation Package define el contenido |
| D2 Minimal Permissions + D5 Context Isolation | Solo las tools necesarias / solo el contexto necesario por subagente |
| D4 Retry Loop + D5 Idempotency | Reintentar si falla / garantizar que el retry no duplica acciones |
| D2 Tool atómica + D3 Command atómico | Una tool = una acción / un Slash Command = una tarea |
| D2 Tool description + D4 Prompt Engineering | La description es el prompt que le dice a Claude cuándo y cómo usar la tool |

---

## Pregunta de decisión rápida para el examen

| Si el escenario describe... | Piensa en... |
|---|---|
| Claude llama la tool equivocada | **D2 — mejorar la description de la tool** |
| Claude falla en tareas largas | **D5 — Context Window Management** |
| Acción se ejecuta dos veces con retry | **D5 — Idempotency** |
| Agente receptor toma decisión incorrecta | **D5 — Handoff Package incompleto** |
| Output de Claude no es parseable | **D4 — Structured Output + Retry Loop** |
| Sistema lento sin razón aparente | **D2 — cambiar secuencial por paralelo** |
| Subagente tiene demasiado poder | **D2 — Minimal Permissions** |
| Claude ignora restricción crítica | **D4 — mover restricción a system prompt** |
| No sabes por qué el sistema falla | **D5 — falta Observability** |
| Tool con parámetro action múltiple | **D2 — separar en tools atómicas** |
| CI/CD review en cada push trivial | **D3 — cambiar trigger a pull_request** |
| CLAUDE.md local contradice proyecto | **D3 — el local tiene prioridad en lo que contradice** |
