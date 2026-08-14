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

| CaracterÃ­stica | Modo 0: Fundamentos transversales | Modo 1: Desarrollo asistido | Modo 2: AutomatizaciÃ³n desatendida | Modo 3: Sistema agÃ©ntico en producciÃ³n | Modo 4: ExtracciÃ³n de documentos | Modo 5: IntegraciÃ³n con herramientas |
| --- | --- | --- | --- | --- | --- | --- |
| **Naturaleza** | Conocimiento base, no escenario | Escenario de uso | Escenario de uso | Escenario de uso | Escenario de uso | Capa transversal de capacidad |
| **Â¿Hay humano en el loop?** | N/A â€” aplica a todos | SÃ­, constante | No, corre solo | No, atiende usuarios finales | Depende del flujo | Transversal |
| **Escenario tÃ­pico** | Fundamentos que atraviesan todos los modos | Desarrollador en su IDE codificando | Pipeline nocturno, reporte semanal, cron job | App en producciÃ³n con usuarios reales | Procesar PDFs, correos, tickets a JSON | Claude necesita actuar sobre sistemas externos |
| **Producto/tecnologÃ­a principal** | API de Anthropic como base conceptual | Claude Code (interactivo) | Claude Code con `-p` **o** SDK en script | Agent SDK | API directa o SDK | MCP como protocolo |
| **Dominios del examen** | Atraviesa los 5 dominios | D2 (20%); D3 (18%) con MCP; D1 (27%) con subagentes | D2 (20%); D5 (15%); D4 (20%) si structured | D1 (27%); D5 (15%); D4 (20%) | D4 (20%); D5 (15%) | D3 (18%); cruza con todos |
| **Peso relativo en tu estudio** | ~25% del tiempo (base para todo) | ~15% (ya tienes terreno ganado) | ~15% | ~20% (el mÃ¡s pesado del examen) | ~15% | ~10% (ya tienes MCP bÃ¡sico funcionando) |
| **Anti-patrÃ³n comÃºn** | Confundir productos con casos de uso; pensar que SDK y Claude Code compiten | Usar Claude Code para job desatendido | Usar API sÃ­ncrona cuando Batch serÃ­a mÃ¡s barato | Usar Claude Code en producciÃ³n | Instrucciones vagas tipo "sÃ© conservador" | Tools con descripciones ambiguas o sin errores estructurados |
| **SeÃ±al en el enunciado del examen** | N/A â€” se presupone | "Un desarrollador estÃ¡ trabajando enâ€¦" | "Procesar cada nocheâ€¦", "pipeline CIâ€¦", "reporte semanalâ€¦" | "App que atiendeâ€¦", "usuarios finalesâ€¦", "en producciÃ³nâ€¦" | "Extraer campos deâ€¦", "convertir documentos aâ€¦" | "Integrar con [sistema]â€¦", "Claude necesita acceso aâ€¦" |

## Contenido principal por modo

**Modo 0 â€” Fundamentos:** AnatomÃ­a de request/response, stop_reasons, prompt engineering, JSON schema, Batch vs sync, CLAUDE.md, MCP base, subagentes, manejo de errores.

**Modo 1 â€” Desarrollo asistido:** Plan mode vs directo, CLAUDE.md local, subagentes en uso, conexiÃ³n de MCP servers. Corre en mÃ¡quina local del dev. SÃ­ncrono interactivo.

**Modo 2 â€” AutomatizaciÃ³n desatendida:** Flag `-p`, Batch API, idempotencia, logging, fallo controlado. Corre en GitHub Actions, GitLab CI, cron, servidor. SÃ­ncrono no-interactivo o Batch API.

**Modo 3 â€” Sistema agÃ©ntico en producciÃ³n:** DescomposiciÃ³n de tareas, hub-and-spoke, fallback loops, session resumption, escalaciÃ³n. Corre en servidor de producciÃ³n, contenedor. Streaming crÃ­tico â€” p95 latency importa.

**Modo 4 â€” ExtracciÃ³n de documentos:** Few-shot, schemas, criterios explÃ­citos, calibraciÃ³n de falsos positivos. Batch API para volumen, sync para urgencia. El modo en sÃ­ *es* el caso de uso.

**Modo 5 â€” IntegraciÃ³n con herramientas:** DiseÃ±o de tools, scoping de servers, estructura de errores, Grep vs Glob. Cada tool call suma latencia.
