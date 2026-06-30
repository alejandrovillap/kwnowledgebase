---
title: Extended thinking
date: 2026-04-01
type: resume
technology: "gen-ai"
status: active
tags: ["extended-thinking", reasoning, "token-budget", "prompt-caching", "context-management", transparency]
keywords: [extended thinking, thinking blocks, reasoning, budget tokens, prompt caching, interleaved thinking, CCA, D5, context management]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Extended thinking

**Important Note:** Extended Thinking is not compatible with some other features, notably message pre-filling and temperature. See the full list of restrictions at: https://docs.anthropic.com/en/docs/build-with-claude/extended-thinking#feature-compatibility

Extended thinking is Claude's advanced reasoning feature that gives the model time to work through complex problems before generating a final response. Think of it as Claude's "scratch paper" — you can see the reasoning process that leads to the answer, which helps with transparency and often results in better quality responses.

## How Extended Thinking Works

When extended thinking is enabled, Claude's response changes from a simple text block to a structured response containing two parts:

1. **Thinking content blocks** — the internal reasoning of Claude
2. **Text content blocks** — the final response for the user

Key benefits:
- Better reasoning capabilities for complex tasks
- Increased accuracy on difficult problems
- Transparency into Claude's thought process

Important trade-offs:
- Higher costs (you pay for thinking tokens)
- Increased latency (thinking takes time)
- More complex response handling in your code

## When to Use Extended Thinking

The decision is straightforward: use your prompt evaluations. Run your prompts without thinking first, and if the accuracy isn't meeting your requirements after you've already optimized your prompt, then consider enabling extended thinking. It's a tool for when standard prompting isn't quite getting you there.

## Response Structure and Security

Extended thinking responses include a special signature system for security. The signature is a cryptographic token that ensures you haven't modified the thinking text. This prevents developers from tampering with Claude's reasoning process, which could potentially lead the model in unsafe directions.

## Redacted Thinking

Sometimes you'll receive a redacted thinking block instead of readable reasoning text. This happens when Claude's thinking process gets flagged by internal safety systems. The redacted content contains the actual thinking in encrypted form, allowing you to pass the complete message back to Claude in future conversations without losing context.

## Implementation

To enable extended thinking, add two parameters to your chat function:

```python
def chat(
    messages,
    system=None,
    temperature=1.0,
    stop_sequences=[],
    tools=None,
    thinking=False,
    thinking_budget=1024
):
```

The thinking budget sets the maximum tokens Claude can use for reasoning. The minimum value is 1024 tokens, and your `max_tokens` parameter must be greater than your thinking budget.

```python
if thinking:
    params["thinking"] = {
        "type": "enabled",
        "budget": thinking_budget
    }
```

## Que es Extended Thinking (CCA-F)

Es un modo en el que Claude genera bloques de **razonamiento interno** (thinking blocks) antes de producir su respuesta final. En lugar de responder directamente, Claude "piensa en voz alta" paso a paso, y luego usa esas conclusiones para formular una respuesta más precisa y fundamentada.

### Como se activa

Se habilita mediante el parámetro `thinking` en la API, donde defines:
- **`enabled: true`** para activarlo
- **`budget_tokens`** — el máximo de tokens que Claude puede usar para su razonamiento interno (este presupuesto NO cuenta como parte de `max_tokens` de la respuesta)

### Para qué sirve

- Tareas de razonamiento complejo (matemáticas, lógica, análisis)
- Problemas que requieren descomposición paso a paso
- Análisis de código con múltiples dependencias
- Decisiones arquitectónicas con múltiples variables

### Comportamiento con Prompt Caching

Este punto es muy relevante para el examen:
- Los **thinking blocks de turnos anteriores se remueven del contexto** en peticiones subsecuentes — no consumen espacio en la ventana de contexto permanentemente
- **Excepción importante**: cuando continúas una conversación con tool use, los thinking blocks **sí se cachean** y cuentan como input tokens cuando se leen del cache
- Cambios en los **parámetros de thinking** (activar/desactivar, cambiar budget) **invalidan los cache breakpoints** de mensajes
- Los **system prompts y tools permanecen cacheados** aunque cambies parámetros de thinking

### Interleaved Thinking

En modelos más recientes (Claude Opus 4.5 en adelante), existe el modo "interleaved thinking" donde los bloques de pensamiento pueden ocurrir **entre múltiples tool calls** dentro de un mismo turno. Esto amplifica la invalidación de cache porque hay más puntos donde se insertan thinking blocks.

### Limitaciones clave

| Limitación | Detalle |
|---|---|
| No persistente | Los thinking blocks se eliminan del contexto en el siguiente turno (excepto durante tool use) |
| Cache sensible | Cambiar parámetros de thinking invalida breakpoints de cache de mensajes |
| Costo oculto | Aunque no consumen contexto visualmente, sí cuentan como input tokens cuando están cacheados |
| Budget obligatorio | Debes definir un budget máximo; tareas largas pueden necesitar la cache de 1 hora en lugar de la de 5 minutos |
| Toggle mid-conversation | Si desactivas thinking y pasas contenido de thinking en el turno actual de tool use, la petición puede fallar en modelos antiguos |

### Relevancia para el examen CCA-F

En el Dominio 5 (Gestión de Contexto y Confiabilidad), necesitas entender cómo extended thinking interactúa con:
- **Gestión de ventana de contexto** — los thinking blocks afectan el uso de tokens
- **Prompt caching** — las reglas de invalidación son un tema frecuente
- **Tool use flows** — el comportamiento especial de thinking blocks durante ciclos de herramientas

La clave para el examen es entender los **tradeoffs**: extended thinking mejora la calidad de razonamiento, pero introduce complejidad en caching y manejo de contexto que debes considerar al diseñar arquitecturas de producción.
