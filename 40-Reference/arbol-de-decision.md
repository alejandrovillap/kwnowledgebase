---
title: Árbol de decisión
date: 2026-03-22
type: reference
technology: "gen-ai"
status: active
tags: ["model-selection", "decision-tree", openai, anthropic, google, "cost-optimization", "workload-mapping"]
keywords: [árbol de decisión, AI model selection, OpenAI, Anthropic, Google, Ligero, Sweet Spot, Avanzado, GPT, Claude, Gemini, model family, workload]
source: "notion-migration"
project: ""
certification: ""
confidence: high
---

# Árbol de decisión

## 1. Árbol de decisión (alto nivel)

### Paso 1 – ¿Qué pesa más?

1. **¿Costo ultra-bajo y alto volumen?**
   - Sí → ve a **Familia LIGERA** (barata, rápida).
   - No → sigue.
2. **¿Necesitas máximo razonamiento / tareas críticas?**
   - Sí → ve a **Familia AVANZADA** (flagship premium).
   - No → ve a **Familia SWEET SPOT** (caballo de batalla).

### Paso 2 – Tipo de workload

Dentro de cada familia:

1. **Workloads transaccionales / simples** (chatbot de soporte, formularios, clasificación, resúmenes cortos, orquestación / routing):
   - Prioriza: **latencia baja + costo bajo + JSON suficientemente fiable**.
   - Elige: modelo **ligero** (nano / Haiku / Flash / Lite).
2. **Uso general / copilots de negocio** (productividad, análisis moderado, RAG sobre varios documentos, coding estándar):
   - Prioriza: **equilibrio costo-calidad**, buen tool use y contextos medianos-grandes.
   - Elige: modelo **sweet spot** (mini / Sonnet / Pro "normal").
3. **Uso avanzado / crítico** (estrategia, legal complejo, ciencia, decisiones de alto impacto, RAG muy largo):
   - Prioriza: **razonamiento, robustez y structured outputs muy fiables**, aceptando costo.
   - Elige: modelo **avanzado** (GPT-5.4 / Claude Opus 4.6 / Gemini 3 Pro).

## Mapeo por proveedor (2026)

### OpenAI

| Tipo | Caso típico | Modelos sugeridos |
|---|---|---|
| **Ligero (barato)** | Chatbots simples, routing, transacciones, clasificación, resumen de tickets. | GPT-4.1-nano (legado pero barato) y GPT-5-nano / GPT-5.4-nano como evolución natural. |
| **Sweet spot** | Copilots de negocio, RAG normal, coding serio, asistentes internos. | GPT-4.1-mini (2025) y, para nuevos diseños, GPT-5-mini / GPT-5.4-mini como "modelo por defecto". |
| **Avanzado** | Estrategia, legal, RAG muy largo, agents complejos. | GPT-5.4 (short/long context) y GPT-5 core para casos donde necesitas máximo razonamiento. |

### Anthropic (Claude)

| Tipo | Caso típico | Modelos sugeridos |
|---|---|---|
| **Ligero (barato)** | Soporte, procesos transaccionales, clasificación, resúmenes de alto volumen. | Claude Haiku 4.5 (y posteriores Haiku 4.x): muy rápido, muy barato, buen JSON. |
| **Sweet spot** | Copilots generales, coding, RAG largo razonable. | Claude Sonnet 4.6 como caballo de batalla recomendado en 2026. |
| **Avanzado** | Investigación, análisis crítico, decisiones de alto impacto. | Claude Opus 4.6 como flagship de máximo razonamiento. |

### Google (Gemini)

| Tipo | Caso típico | Modelos sugeridos |
|---|---|---|
| **Ligero (barato)** | Chatbots simples, procesos transaccionales, interfaces rápidas. | Gemini 2.0 / 2.5 Flash y, mirando a futuro, Gemini 3 Flash. |
| **Sweet spot** | Copilots de Workspace, RAG largo, multimodal cotidiano. | Gemini 1.5 Pro-002 y 2.0 Flash para muchas cargas generales; en 3.x, Gemini 3 Flash. |
| **Avanzado** | Casos enterprise complejos, integraciones profundas, razonamiento pesado. | Gemini 3 Pro / 3.1 Pro como flagship premium dentro del ecosistema Google Cloud. |
