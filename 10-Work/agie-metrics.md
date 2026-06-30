---
title: Agile Metrics — Guía Completa
date: 2026-01-15
type: reference
technology: agile
status: active
tags: [metrics, burndown, "lead-time", throughput, velocity, kanban, scrum]
keywords: [agile metrics, burndown, burnup, cumulative flow diagram, CFD, lead time, cycle time, throughput, WIP, velocity, EVM, kanban, scrum, flow metrics, EBM]
source: "notion-migration"
project: ""
certification: ""
confidence: high
---

# Agile Metrics — Guía Completa

Las métricas ágiles son medidas cuantitativas que ayudan a ver si el equipo realmente entrega valor de forma predecible y sostenible, no solo si "hace muchas cosas". Se organizan en cuatro grandes bloques: flujo, valor, calidad y salud del equipo.

## Qué son las Agile Metrics

Son indicadores que describen el progreso, el flujo de trabajo, la calidad y los resultados del negocio en contextos ágiles como Scrum y Kanban. Su propósito es soportar decisiones empíricas: identificar cuellos de botella, mejorar la predictibilidad y conectar el trabajo del equipo con resultados para cliente y negocio.

## Métricas de Flujo

Métricas típicas: tiempo de ciclo, lead time, throughput (elementos completados por unidad de tiempo) y trabajo en progreso (WIP).

- **Lead time / Cycle time**: tiempo desde que se pide algo hasta que está terminado; fundamentales para medir rapidez y detectar cuellos de botella.
- **Throughput / rendimiento**: cantidad de elementos completados por unidad de tiempo, base para la predictibilidad.
- **WIP y edad del WIP**: cuántos ítems están abiertos y cuánto llevan abiertos; útil para controlar multitarea y bloqueos.

## Métricas de Valor y Outcomes

Enfoques como Evidence-Based Management (EBM) proponen medir: Current Value, Time to Market, Ability to Innovate y Unrealized Value.

- **Valor entregado**: historias de negocio cumplidas, objetivos cumplidos, indicadores económicos asociados a entregas.
- **Satisfacción del cliente (NPS)**: percepción del usuario sobre lo entregado.

## Métricas de Planificación (Scrum)

- **Velocidad del equipo**: trabajo completado por sprint, usada para pronosticar capacidad.
- **Sprint burndown / backlog burndown**: trabajo pendiente vs. tiempo, para ver si el sprint va en ruta.

## Métricas de Calidad

- **Defectos / tasa de fallos**: número de incidencias en producción y su tendencia.
- **Retrabajo / trabajo correctivo**: proporción de esfuerzo dedicado a corregir vs. crear nuevo valor.

## Métricas de Equipo y Cultura

- **Compromisos cumplidos vs. no cumplidos**: ratio de trabajo comprometido vs. terminado en un sprint.
- **Productividad del equipo**: relación entre unidades de trabajo y recursos/tiempo (usar con cuidado para evitar malos incentivos).

## Las 3 Gráficas Básicas

Burn down, burn up y cumulative flow son las tres gráficas básicas para "ver" el flujo y el progreso en Agile.

### Burndown Chart

Muestra **trabajo restante vs. tiempo**: eje X = días del sprint/proyecto, eje Y = esfuerzo pendiente (puntos, horas, historias).

- Incluye línea ideal y línea real.
- Si la real se aplana o se separa de la ideal: hay bloqueos, sobrecarga o cambios de alcance.
- Si sube: se añadió scope a mitad del sprint.

### Burnup Chart

Muestra **trabajo completado y alcance total**: eje X = tiempo, eje Y = unidades de trabajo; una línea sube con lo completado y otra marca el scope (que puede cambiar).

- Excelente para contextos con alcance dinámico.
- Hace visible el scope creep: se ve claramente cuando la línea de scope sube.

### Cumulative Flow Diagram (CFD)

Muestra, de forma acumulada, **cuántos ítems hay en cada estado** del flujo a lo largo del tiempo (bandas: To Do, In Progress, Done).

- Bandas que se engrosan: acumulación/cuello de botella.
- Pendiente de la banda Done: refleja throughput.
- Distancias horizontales: permiten estimar lead time y cycle time.

### Cuándo Usar Cada Una

| Gráfica | Mejor para |
|---|---|
| **Burndown** | Sprints o proyectos de alcance fijo, seguimiento táctico |
| **Burnup** | Productos/proyectos con alcance cambiante, comunicación ejecutiva |
| **CFD** | Kanban, operaciones, multi-equipo donde importa la estabilidad del flujo |

## Agile Metrics vs EVM

| Dimensión | Burndown/Burnup | EVM (PV, EV, AC) |
|---|---|---|
| **Dimensión de costo** | No incluye costo, solo esfuerzo | Sí incluye costo (CPI, SPI, EAC, VAC) |
| **Cambio de alcance** | Burnup lo muestra visualmente | Requiere re-baseline formal |
| **Facilidad de lectura** | Muy intuitivo para cualquier equipo | Requiere formación en terminología PMP |
| **Control financiero** | Débil | Fuerte |
| **Uso típico** | Equipos Scrum/Kanban, sprint-level | Programas, contratos, gobierno, auditorías |

### Analogías Conceptuales EVM ↔ Burn Charts

- **PV (Planned Value)** ↔ Línea ideal del burndown o línea inicial de scope en burnup.
- **EV (Earned Value)** ↔ Línea de trabajo completado en burnup.
- **AC (Actual Cost)** ↔ No existe en burn charts (solo EVM incluye costo real).
- **SV (Schedule Variance)** ↔ Distancia vertical entre línea real e ideal en burndown.

### Cómo Combinarlos (Agile EVM)

- Usar burn up/burn down para gestión **táctica** del sprint y comunicación del equipo.
- **Calcular PV, EV y AC a nivel épica o release** para reporte ejecutivo, mapeando historias completadas a earned value.

## Por Qué Importan las Agile Metrics

1. **Conectar trabajo con resultados**: evalúan si el backlog se traduce en valor real.
2. **Gestionar flujo y predictibilidad**: permiten pronosticar mejor y simplificar la planificación.
3. **Mejorar calidad y reducir riesgo**: detectan tendencias de deuda técnica temprano.
4. **Habilitar decisiones basadas en evidencia**: desplazan la gestión de la opinión a los datos.
5. **Fomentar transparencia y mejora continua**: visibilidad objetiva para equipo, líderes y stakeholders.

## Dónde se Aplican

- **Nivel equipo**: Scrum/Kanban — burndown, velocidad, lead time, defectos.
- **Nivel programa/equipo de equipos**: features completadas, predictibilidad de PI, flujo inter-equipos.
- **Nivel portafolio**: progreso hacia OKR, time-to-market, capacidad de innovación.
- **Áreas no TI**: operaciones, CX, marketing — tableros Kanban con tiempos de respuesta y volumen procesado.

## Cuándo Revisar las Métricas

- **Día a día**: dailies y seguimiento de flujo continuo.
- **Cada sprint**: review y retrospectiva (velocidad, burndown, cycle time, defectos).
- **Mensual/trimestral**: patrones a largo plazo, PI Planning, comités de mejora.
- **Decisiones clave**: antes de iniciar/pausar/matar iniciativas, tras incidentes relevantes.

## Quién es Responsable de Cada Métrica

- **Product Owner**: métricas de valor y negocio (NPS, outcomes, revenue asociado a releases).
- **Scrum Master / Agile Coach**: métricas de flujo, salud del equipo, eficacia de eventos.
- **Developers / Equipo**: métricas de flujo y calidad técnica (lead time, defectos, deuda técnica).
- **Management / PMO**: métricas agregadas de portafolio y capacidades.
- **Stakeholders de negocio**: consumidores de vistas ejecutivas; ajustan estrategia con base en insights.
