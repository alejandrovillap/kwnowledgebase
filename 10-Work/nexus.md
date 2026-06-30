---
title: Nexus
date: 2026-01-13
type: resume
technology: agile
status: active
tags: [nexus, "scaled-scrum", "nexus-integration-team", "scrum-scaling", dependencies, "integrated-increment"]
keywords: [Nexus, scaled Scrum, NIT, Nexus Integration Team, Product Backlog, integrated increment, dependencies, scaling, Scrum.org, Ken Schwaber]
source: "notion-migration"
project: ""
certification: ""
confidence: high
---

# Nexus

## What (Qué): Definición de Nexus

**Nexus** es un framework de escalado de Scrum desarrollado por Ken Schwaber y Scrum.org que permite integrar el trabajo de **3 a 9 equipos Scrum** (hasta 125 personas) trabajando en un mismo producto con un único Product Backlog. Su propósito es entregar un **Incremento Integrado** al final de cada Sprint, preservando los principios empíricos y valores de Scrum sin introducir complejidad innecesaria.

### Componentes Fundamentales

**Roles**:
- **Nexus Integration Team (NIT)**: Nuevo rol central que coordina, entrena y supervisa la integración
- **Equipos Scrum**: 3-9 equipos Scrum que mantienen sus roles (PO, SM, Dev Team)
- **Product Owner Único**: Un PO para todo el Nexus, responsable del Product Backlog

**Artefactos**:
- **Product Backlog Único**: Un backlog compartido para todo el Nexus
- **Nexus Sprint Backlog**: Unión de todos los Sprint Backlogs individuales que resalta dependencias
- **Integrated Increment**: Suma del trabajo integrado de todos los equipos, potencialmente liberable

**Eventos**:
- **Nexus Sprint Planning**: Planificación coordinada para todos los equipos
- **Nexus Daily Scrum**: Reunión diaria para gestionar dependencias antes de los Daily Scrums individuales
- **Nexus Sprint Review**: Única revisión para inspeccionar el incremento integrado
- **Nexus Sprint Retrospective**: Retrospectiva en 3 partes para mejora continua
- **Refinement**: Refinamiento del Product Backlog a nivel de Nexus para detectar dependencias

## Why (Por qué): Propósito e Importancia

Nexus surge de la necesidad de escalar Scrum **sin perder su esencia empírica y sin introducir burocracia**. Mientras que otros frameworks de escalado añaden roles y ceremonias complejas, Nexus mantiene la simplicidad de Scrum actuando como un **"exoesqueleto"** que coordina equipos existentes.

### Beneficios Cuantificables
- **40-60% reducción** en tiempo de resolución de dependencias cruzadas
- **30-50% mejora** en velocidad de entrega al eliminar bloqueos
- **70-80% reducción** en conflictos de integración al final del Sprint
- **Mejora de 25-35%** en satisfacción del equipo al reducir fricción

## Who (Quién): Roles y Responsabilidades

### Nexus Integration Team (NIT)

El NIT es el **rol distintivo de Nexus**, no un equipo separado sino un **equipo virtual formado por representantes de cada equipo Scrum**.

**Composición**:
- **Product Owner**: Responsable de maximizar valor del producto, gestiona el Product Backlog único
- **Scrum Master**: Facilita el proceso Nexus, elimina impedimentos de integración
- **Nexus Integration Team Members**: Representantes técnicos de cada equipo Scrum (generalmente 1-2 personas por equipo)

**Responsabilidades**:
- Asegurar que se produzca un incremento integrado al final de cada Sprint
- Coaching: guiar equipos en prácticas de integración continua, TDD, CI/CD
- Gestión de dependencias: identificar, visualizar y resolver dependencias cruzadas
- Garantizar que decisiones técnicas soporten integración (branching, versionado, calidad)

**Diferencia clave con Scrum of Scrums**: Mientras Scrum of Scrums es una reunión ad-hoc, el NIT es un **rol permanente con responsabilidad de integración**.

## When (Cuándo): Eventos de Nexus

1. **Refinement** — Continuamente, 1-2 horas por semana. Detectar y minimizar dependencias antes del Sprint Planning.
2. **Nexus Sprint Planning** — Inicio de cada Sprint (2-4 horas). Coordinar actividades, negociar Nexus Sprint Goal.
3. **Nexus Daily Scrum** — Diariamente **antes** de los Daily Scrums individuales (15-30 min). Gestionar dependencias.
4. **Nexus Sprint Review** — Final de cada Sprint (1-2 horas). **Solo un evento único** para todo el Nexus.
5. **Nexus Sprint Retrospective** — 3 partes: por equipo individual, NIT, y Nexus completo.

### Cuándo Usar Nexus

| Escenario | ¿Usar Nexus? |
|---|---|
| 3-9 equipos Scrum en un mismo producto | ✅ Ideal |
| Dependencias técnicas significativas entre equipos | ✅ Recomendado |
| Necesidad de incremento integrado por Sprint | ✅ Crítico |
| 1-2 equipos Scrum | ❌ No necesario (Scrum simple es suficiente) |
| 10+ equipos Scrum | ⚠️ Usar Nexus+ (hasta 9 Nexus coordinados) |
| Equipos completamente autónomos sin dependencias | ❌ Scrum individual es más eficiente |

## How (Cómo): Implementación

**Paso 1**: Confirmar que se tienen 3-9 equipos Scrum en un mismo producto; validar PO único; identificar dependencias críticas.

**Paso 2**: Formar el Nexus Integration Team — seleccionar representantes técnicos de cada equipo; capacitar al NIT.

**Paso 3**: Establecer infraestructura CI/CD que soporte integración continua de múltiples equipos.

**Paso 4**: Iniciar eventos Nexus — Nexus Sprint Planning, Nexus Daily Scrum, Nexus Sprint Review.

**Paso 5**: Medir y mejorar — % de Sprints con incremento integrado, tiempo de resolución de dependencias.

### Prácticas Clave de Éxito

- **Refinement de alto nivel**: Dedicar 10-15% de capacidad a refinamiento cross-team.
- **Integración continua**: Los equipos deben integrar su trabajo **diariamente**, no esperar al final del Sprint.
- **NIT como facilitador, no ejecutor**: El NIT no realiza la integración — asegura que ocurra.
- **Rotación en NIT**: Rotar cada 2-3 Sprints para distribuir conocimiento.

## How Much (Cuánto): Costos y ROI

| Componente | Rango de Inversión |
|---|---|
| Capacitación Nexus (SPS de Scrum.org) | $1,500 - $3,000/persona |
| Coaching inicial | $150 - $300/hora |
| Herramientas CI/CD | $0 - $500/mes |

**ROI**: 60-80% menos tiempo en integración al final del Sprint; 20-30% aumento en velocidad efectiva; 40-60% reducción en defectos de integración.
