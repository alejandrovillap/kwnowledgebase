---
title: Fine grained tool calling
date: 2026-03-25
type: resume
technology: "gen-ai"
status: active
tags: ["fine-grained-streaming", "tool-calling", claude, latency, "json-streaming", "api-optimization"]
keywords: ["fine-grained tool calling", eager_input_streaming, streaming, tool use, latency, JSON truncation, CCA, D2]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Fine grained tool calling

## El problema que resuelve

En el flujo normal, Claude construye todos los parámetros de una tool en memoria, los valida como JSON completo, y *hasta entonces* los envía. Eso genera latencia, especialmente con outputs grandes.

**Fine-grained tool streaming** cambia eso: los parámetros se transmiten conforme llegan, sin esperar a que el JSON completo esté buffereado y validado.

**Diferencia clave:** sin fine-grained streaming hay un delay de ~15 segundos; con él se reduce a ~3 segundos — porque Claude no espera a tener el JSON completo para empezar a enviarlo.

## El tradeoff fundamental

Como fine-grained streaming envía los parámetros sin buffering ni validación JSON, **no hay garantía de que el stream resulte en un JSON válido**. En particular, si se alcanza el límite de `max_tokens`, el stream puede terminar a mitad de un parámetro.

## Cómo funciona internamente

La clave está en que antes de que llegue el primer chunk de parámetros, Claude ya emitió un `content_block_start` que declara el nombre de la tool y le asigna un **ID único** y un **index**. Todos los chunks que vienen después cargan ese mismo index — el sistema sabe sin ambigüedad a qué tool pertenecen.

**No hay riesgo de que los chunks vayan a una tool diferente.** El único riesgo real es que el JSON quede truncado si se agota `max_tokens` a mitad del stream.

## Activación por tool (decisión del desarrollador)

Se activa por herramienta individual, no de forma global. El desarrollador decide qué tools merece la velocidad del streaming:

```json
{
  "name": "make_file",
  "description": "Write text to a file",
  "eager_input_streaming": true,
  "input_schema": { ... }
}
```

Si `eager_input_streaming` es `true`, Claude streamea chunks. Si no está o es `false`, Claude espera y manda el JSON completo.

**Cuándo activarlo:**
- Tools que escriben archivos largos → streaming tiene sentido
- Tools de pago donde un JSON truncado causaría error crítico → JSON completo es más seguro

## Impacto en costos

Fine-grained streaming **no agrega tokens extra**. Los chunks son exactamente los mismos tokens que se mandarían de golpe en el JSON completo — solo cambia *cómo* viajan, no *cuántos* son.

En realidad puede **reducir costos** indirectamente:

| Escenario | Sin streaming | Con streaming |
|---|---|---|
| JSON truncado por `max_tokens` | Claude reintenta → pagas dos llamadas | Detectas el truncado al vuelo → evitas el reintento |

## Cuándo considerar fine-grained tool calling

- Necesitas mostrar progreso en tiempo real al usuario sobre la generación de argumentos de tool
- Quieres empezar a procesar resultados parciales lo antes posible
- Los delays de buffering impactan negativamente la experiencia de usuario
- Estás dispuesto a implementar manejo robusto de errores JSON
