---
title: "D5 - Context Management & Reliability"
date: 2026-03-25
type: resume
technology: "gen-ai"
status: active
tags: ["context-management", reliability, claude, "cca-exam", "handoff-patterns", observability]
keywords: [context window management, summarization, sliding window, context injection, external memory, handoff patterns, reliability, confidence calibration, graceful degradation, idempotency, observability, D5, CCA]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# D5 - Context Management & Reliability

Cuando un agente trabaja en tareas largas y complejas, enfrenta dos problemas que el examen evalúa:

**Problema 1 — El contexto se llena.** Claude tiene una ventana de contexto limitada. En conversaciones largas o agentes con muchas herramientas, el contexto se satura — Claude empieza a "olvidar" información importante del inicio.

**Problema 2 — El sistema falla.** En producción, los agentes fallan. La pregunta no es si va a pasar, sino cómo el sistema se recupera sin perder el trabajo hecho.

El Dominio 5 responde: **¿cómo mantienes a Claude efectivo en tareas largas y cómo construyes sistemas que se recuperan de fallos?**

Tiene 3 pilares:
- **Context Window Management** — cómo manejar el contexto cuando se llena
- **Handoff Patterns** — cómo pasar el estado entre agentes o sesiones
- **Reliability & Confidence Calibration** — cómo construir sistemas confiables

## Context Window Management

Imagina que Carlos (Claude) tiene un escritorio. Ese escritorio tiene un tamaño fijo — solo caben cierta cantidad de papeles. Al inicio de la conversación el escritorio está vacío y Carlos trabaja perfectamente. Pero conforme la conversación avanza, el escritorio se llena — mensajes anteriores, resultados de tools, documentos analizados.

Cuando el escritorio está completamente lleno pasan dos cosas malas:
- **Cosa mala 1** — Carlos ya no puede poner papeles nuevos. El sistema falla o trunca información.
- **Cosa mala 2** — Carlos tiene tanto papel en el escritorio que los documentos importantes del inicio quedaron enterrados. Carlos "olvida" el contexto crítico aunque técnicamente sigue ahí.

Context Window Management es el arte de **mantener el escritorio ordenado** — saber qué papeles son esenciales, cuáles se pueden archivar, y cómo resumir pilas de papeles en una sola hoja sin perder lo importante.

**Definición formal:** Context Window Management es el conjunto de estrategias para administrar eficientemente el espacio de contexto disponible en Claude, garantizando que la información más relevante esté siempre accesible sin saturar la ventana de contexto.

Las cuatro estrategias en detalle:

1. **Summarization** — cuando la conversación se está llenando, le pides a Claude que comprima los mensajes anteriores en un resumen conciso. Ese resumen reemplaza los mensajes originales en el contexto. Conservas lo esencial y liberas espacio para continuar. Es la estrategia más flexible porque preserva el significado aunque descarte los detalles.

2. **Sliding Window** — defines un número máximo de mensajes que siempre están en contexto — por ejemplo los últimos 20. Cuando llega el mensaje 21, el primero se descarta automáticamente. Simple y predecible. El examen te pregunta cuándo NO usarlo — cuando el mensaje del inicio tiene información crítica que siempre necesitas, como el objetivo original de la tarea.

3. **Context Injection selectiva** — en lugar de cargar todo el historial, solo inyectas la información relevante para la tarea actual. Si el agente está procesando el paso 7 de 20, no necesita los detalles del paso 1 en el contexto — solo el estado actual y el objetivo. Lo viste en el Dominio 2 como patrón de integración — aquí aplica dentro del manejo del contexto.

4. **External Memory** — para historiales muy largos que no caben en el contexto, guardas la información en una base de datos externa. Cuando Claude necesita algo específico, lo recupera con una tool. Claude no carga todo el historial — solo consulta lo que necesita en ese momento. Es la estrategia más escalable pero requiere más arquitectura.

### La trampa del examen en Context Window

El examen te da un agente que está fallando en tareas largas y te pregunta por qué. La respuesta casi siempre apunta a una de dos cosas:
- **Context leakage** — un subagente tiene acceso al contexto completo del orquestador cuando solo necesita el contexto de su tarea específica. Solución: aislar el contexto de cada subagente — darle solo lo que necesita para su tarea.
- **Sin estrategia de manejo** — el sistema no tiene ninguna de las cuatro estrategias implementadas y simplemente falla cuando el contexto se llena. Solución: implementar summarization o sliding window según el caso.

## Handoff Patterns

Sigues en Studio X. Carlos (Claude) está trabajando en un proyecto largo y complejo — analizar 200 contratos, extraer riesgos, y generar un reporte ejecutivo. Es demasiado trabajo para una sola sesión.

A mitad del trabajo pasan dos cosas:

**Escenario A** — la sesión se corta inesperadamente. Luz, internet, timeout. Carlos pierde todo lo que tenía en mente y cuando reinicia no sabe dónde estaba ni qué había hecho.

**Escenario B** — Carlos termina su turno y le pasa el trabajo a otro agente especializado. Pero no le deja ninguna nota — el nuevo agente no sabe qué se hizo, qué falta, ni qué decisiones se tomaron.

En ambos casos el trabajo se pierde o se repite. Eso es exactamente lo que los Handoff Patterns resuelven — **cómo pasar el estado, el progreso, y el contexto de una sesión a otra, o de un agente a otro, sin perder información crítica.**

**Definición formal:** Los Handoff Patterns son estrategias de arquitectura que garantizan la continuidad del trabajo cuando hay una transferencia de control — entre sesiones, entre agentes, o entre Claude y un humano — preservando el estado, el progreso, y el contexto necesario para continuar sin interrupciones.

Los tres tipos de handoff y lo que el examen evalúa en cada uno:

1. **Sesión a Sesión** — cuando el trabajo se interrumpe. El agente genera un State Snapshot antes de terminar — un documento estructurado con el estado completo del trabajo. La siguiente sesión lee ese snapshot y continúa exactamente donde se quedó. El examen pregunta qué pasa si no hay snapshot — la nueva sesión empieza desde cero, duplicando trabajo.

2. **Agente a Agente** — cuando un agente especializado termina su parte y pasa el trabajo a otro. El Handoff Package contiene solo el contexto relevante para el agente receptor — no todo el historial del agente emisor. El agente receptor recibe solo lo que necesita para su tarea, no el contexto completo.

3. **Claude a Humano** — cuando Claude detecta que necesita intervención humana. El Escalation Package es crítico — no basta con decir "necesito ayuda". Claude debe entregar exactamente qué hizo, por qué está escalando, y qué opciones tiene el humano. Sin ese contexto el humano pierde tiempo reconstruyendo la situación.

## Reliability & Confidence Calibration

Carlos (Claude) está analizando contratos y encuentra una cláusula ambigua. Tiene dos opciones:

**Opción A** — responde con total confianza: *"Esta cláusula es un riesgo alto."* Pero internamente no está seguro — podría ser riesgo alto o medio dependiendo de la jurisdicción. El humano que lee el reporte toma una decisión crítica basada en una respuesta que Carlos dio con falsa confianza.

**Opción B** — responde calibrado: *"Esta cláusula probablemente es riesgo alto con 85% de confianza, pero depende de la jurisdicción aplicable. Recomiendo revisión humana antes de actuar."* El humano sabe exactamente cuánto confiar en esa respuesta.

La Opción B es **Confidence Calibration** — Claude comunica no solo su respuesta sino qué tan seguro está de ella. Eso le permite al sistema tomar decisiones inteligentes — actuar automáticamente cuando la confianza es alta, escalar cuando es baja.

**Definición formal:** Reliability & Confidence Calibration es el conjunto de patrones que garantizan que un sistema con Claude sea predecible y confiable — incluyendo que Claude comunique explícitamente su nivel de certeza para que el sistema pueda decidir cuándo actuar automáticamente y cuándo involucrar a un humano.

Los tres patrones de reliability en detalle:

- **Graceful Degradation** — cuando una parte del sistema falla, el resto sigue funcionando. Si la tool de `get_weather` falla, el agente de viajes no se cae completo — continúa con la reserva de vuelo y hotel, e informa al usuario que el clima no está disponible. El sistema degrada parcialmente en lugar de fallar totalmente.

- **Idempotency** — si la misma acción se ejecuta dos veces, el resultado es el mismo que ejecutarla una vez. Crítico en sistemas con retry loops — si Claude reintenta `cancel_order` porque no recibió confirmación, no debe cancelar la orden dos veces. El examen te pregunta cómo garantizar esto — la respuesta es verificar el estado antes de ejecutar.

- **Observability** — loggear cada decisión que Claude toma, qué tools llamó, con qué parámetros, y cuál fue el resultado. Sin observability no puedes auditar, depurar, ni mejorar el sistema. El examen lo pregunta así: *"El sistema está produciendo resultados inesperados pero no sabes por qué"* — la respuesta siempre es falta de observability.

---

## La conexión entre los tres pilares del Dominio 5

```
Context Window Management  →  mantiene a Claude efectivo
        ↓
Handoff Patterns           →  garantiza continuidad entre sesiones y agentes
        ↓
Reliability & Confidence   →  el sistema sabe cuándo confiar y cuándo escalar
```

Y la conexión con todos los dominios anteriores:

```
D1 — Cuándo escalar (max_turns, fallback)
D5 — Cómo escalar (Escalation Package con State Snapshot)

D2 — Minimal Permissions (solo las tools necesarias)
D5 — Context Isolation (solo el contexto necesario por agente)

D4 — Retry Loop (reintentar con contexto del error)
D5 — Idempotency (garantizar que el retry no duplica acciones)
```
