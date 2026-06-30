---
title: Cinco modos de Claude Code
date: 2026-04-16
type: resume
technology: "gen-ai"
status: active
tags: ["claude-code", agentic, sdk, mcp, "batch-api", extraction, "tool-design"]
keywords: [Claude Code, modos, agentic, SDK, MCP, batch API, extraction, tool design, CCA exam]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Cinco modos de Claude Code

| Característica | Modo 0: Fundamentos transversales | Modo 1: Desarrollo asistido | Modo 2: Automatización desatendida | Modo 3: Sistema agéntico en producción | Modo 4: Extracción de documentos | Modo 5: Integración con herramientas |
| --- | --- | --- | --- | --- | --- | --- |
| **Naturaleza** | Conocimiento base, no escenario | Escenario de uso | Escenario de uso | Escenario de uso | Escenario de uso | Capa transversal de capacidad |
| **¿Hay humano en el loop?** | N/A — aplica a todos | Sí, constante | No, corre solo | No, atiende usuarios finales | Depende del flujo | Transversal |
| **Escenario típico** | Fundamentos que atraviesan todos los modos | Desarrollador en su IDE codificando | Pipeline nocturno, reporte semanal, cron job | App en producción con usuarios reales | Procesar PDFs, correos, tickets a JSON | Claude necesita actuar sobre sistemas externos |
| **Producto/tecnología principal** | API de Anthropic como base conceptual | Claude Code (interactivo) | Claude Code con `-p` **o** SDK en script | Agent SDK | API directa o SDK | MCP como protocolo |
| **Dominios del examen** | Atraviesa los 5 dominios | D2 (20%); D3 (18%) con MCP; D1 (27%) con subagentes | D2 (20%); D5 (15%); D4 (20%) si structured | D1 (27%); D5 (15%); D4 (20%) | D4 (20%); D5 (15%) | D3 (18%); cruza con todos |
| **Peso relativo en tu estudio** | ~25% del tiempo (base para todo) | ~15% (ya tienes terreno ganado) | ~15% | ~20% (el más pesado del examen) | ~15% | ~10% (ya tienes MCP básico funcionando) |
| **Anti-patrón común** | Confundir productos con casos de uso; pensar que SDK y Claude Code compiten | Usar Claude Code para job desatendido | Usar API síncrona cuando Batch sería más barato | Usar Claude Code en producción | Instrucciones vagas tipo "sé conservador" | Tools con descripciones ambiguas o sin errores estructurados |
| **Señal en el enunciado del examen** | N/A — se presupone | "Un desarrollador está trabajando en…" | "Procesar cada noche…", "pipeline CI…", "reporte semanal…" | "App que atiende…", "usuarios finales…", "en producción…" | "Extraer campos de…", "convertir documentos a…" | "Integrar con [sistema]…", "Claude necesita acceso a…" |

## Contenido principal por modo

**Modo 0 — Fundamentos:** Anatomía de request/response, stop_reasons, prompt engineering, JSON schema, Batch vs sync, CLAUDE.md, MCP base, subagentes, manejo de errores.

**Modo 1 — Desarrollo asistido:** Plan mode vs directo, CLAUDE.md local, subagentes en uso, conexión de MCP servers. Corre en máquina local del dev. Síncrono interactivo.

**Modo 2 — Automatización desatendida:** Flag `-p`, Batch API, idempotencia, logging, fallo controlado. Corre en GitHub Actions, GitLab CI, cron, servidor. Síncrono no-interactivo o Batch API.

**Modo 3 — Sistema agéntico en producción:** Descomposición de tareas, hub-and-spoke, fallback loops, session resumption, escalación. Corre en servidor de producción, contenedor. Streaming crítico — p95 latency importa.

**Modo 4 — Extracción de documentos:** Few-shot, schemas, criterios explícitos, calibración de falsos positivos. Batch API para volumen, sync para urgencia. El modo en sí *es* el caso de uso.

**Modo 5 — Integración con herramientas:** Diseño de tools, scoping de servers, estructura de errores, Grep vs Glob. Cada tool call suma latencia.
