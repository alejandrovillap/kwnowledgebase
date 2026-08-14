---
certification: ''
confidence: high
date: 2026-01-13
keywords:
- disciplined agile
- DA
- DAD
- toolkit
- WoW
- way of working
- Scott Ambler
- PMI
- ciclo de vida
- DASM
- DASSM
- roles
- inception
- construction
- transition
project: ''
source: notion-migration
status: active
tags:
- disciplined-agile
- dad
- pmi
- way-of-working
- lifecycle
- dasm
target_folder: 20-Learning/PMI-ACP
technology: agile
title: Disciplined Agile
type: resume
updated: '2026-07-31'
---
# Disciplined Agile

## What: Definición de Disciplined Agile

**Disciplined Agile (DA)** es un **toolkit de toma de decisiones de procesos** que ayuda a personas, equipos y organizaciones a optimizar su forma de trabajar (Way of Working - WoW) de manera contextual y pragmática. Creado por Scott Ambler y Mark Lines, y adquirido por PMI en 2019, DA no es un framework prescriptivo sino un **kit de herramientas** que guía la selección de prácticas ágiles y lean según el contexto específico.

## Disciplined Agile Delivery (DAD)

DAD es el componente principal de DA enfocado en la entrega de soluciones de TI, con un **ciclo de vida de riesgo-valor** que abarca tres fases:

| Fase | Propósito | Duración | Actividades Clave |
|---|---|---|---|
| **Inception** | Arranque estructurado y alineación inicial | 1-4 semanas | Modelar solución, explorar pruebas de concepto, definir arquitectura común, crear roadmap de alto nivel |
| **Construction** | Desarrollo iterativo con calidad | 2-12+ iteraciones | Entrega continua, validación con cliente, pruebas integradas, refactorización |
| **Transition** | Liberación segura a producción | Días a semanas | Despliegue controlado, capacitación usuarios, documentación, soporte inicial |

## Los 4 Ciclos de Vida de DA

1. **Agile**: Basado en Scrum/XP, ideal para equipos con experiencia ágil
2. **Lean**: Basado en Kanban, para flujos continuos con baja variabilidad
3. **Continuous Delivery**: Para equipos maduros con CI/CD automatizado
4. **Exploratory**: Para proyectos de alta incertidumbre que requieren experimentación

## Componentes Clave

- **Metas de Proceso**: 21 metas que guían decisiones (ej: "Formar el equipo", "Explorar el alcance", "Mejorar calidad")
- **Prácticas**: Conjunto de técnicas para alcanzar metas (ej: User Stories, TDD, CI, Modelado Ágil)
- **Roles**: 5 roles primarios + roles secundarios contextuales
- **Principios**: 8 principios fundamentales que guían la toma de decisiones

## Why: Propósito e Importancia

DA surge para **completar los huecos** que dejan frameworks como Scrum, Kanban o XP, ofreciendo herramientas para decisiones pragmáticas según contexto. Su propósito es **evitar el "purismo ágil"** que ignora realidades empresariales y promover **disciplina sin rigidez**.

### Objetivos Estratégicos

**Flexibilidad contextual**: DA reconoce que "la elección es buena" (Choice is Good). No prescribe una sola forma de trabajar, sino que guía a equipos para elegir prácticas según su situación específica.

**Optimización del flujo completo**: DA fomenta optimizar desde concepción hasta retiro, no solo desarrollo. Incluye gobernanza, operaciones, seguridad, gestión de datos y atención al cliente.

**Mejora continua empoderada**: Los equipos autoorganizados usan el toolkit para evolucionar su WoW basado en retroalimentación continua, no en imposición top-down.

**Integración de prácticas probadas**: DA incorpora lo mejor de Scrum, Kanban, XP, Lean, SAFe, LeSS e incluso PMBOK®, creando un **híbrido pragmático**.

**Escalabilidad consciente**: DA es escalable pero no prescriptivo en cómo escalar, permitiendo organizaciones elegir entre Nexus, SAFe, LeSS o modelos híbridos según necesidad.

### Beneficios Cuantificables

- **30-50% reducción** en time-to-market al optimizar flujo completo
- **20-40% mejora** en eficiencia al eliminar prácticas que no aportan valor
- **Reducción de 25-35%** en costos de gobernanza innecesaria
- **Aumento de 40-60%** en satisfacción del equipo al empoderar decisiones locales

## Who: Roles y Responsabilidades

DA define **5 roles primarios** esenciales, más roles secundarios que se añaden según contexto.

### Roles Primarios

| Rol | Responsabilidades | Cuándo es Crítico |
|---|---|---|
| **Team Lead** | Facilita equipo, elimina impedimentos, guía mejora. Equivalente a Scrum Master pero más flexible | Siempre (rol fundamental) |
| **Product Owner** | Maximiza valor, gestiona backlog, prioriza según negocio | Siempre (rol fundamental) |
| **Architecture Owner** | Guía decisiones técnicas, asegura coherencia arquitectónica, mentor técnico | Proyectos con complejidad técnica significativa |
| **Team Member** | Entrega solución (dev, test, UX, ops). Equipo multifuncional | Siempre (rol fundamental) |
| **Stakeholder** | Representa intereses externos (usuarios, negocio, operaciones, seguridad) | Siempre (rol fundamental) |

### Roles Secundarios (Contextuales)

Se añaden según necesidad sin crear burocracia permanente: Specialist, Domain Expert, Technical Specialist, Integrator, Independent Tester, DevOps.

### Diferencia Clave con SAFe

Mientras SAFe tiene **12+ roles definidos permanentemente** (RTE, Product Manager, System Architect, etc.), DA tiene **5 roles primarios fijos** y el resto es **situacional**. Esto reduce burocracia y permite estructuras más ligeras.

## When: Momentos de Aplicación y Decisiones

| Escenario | DA vs SAFe vs Nexus | Justificación |
|---|---|---|
| **Organización pequeña-mediana (<500 personas)** | ✅ DA ideal | Flexibilidad sin sobrecarga de roles |
| **Equipos con experiencia ágil que buscan optimizar** | ✅ DA ideal | Toolkit para refinamiento, no revolución |
| **Necesidad de integrar múltiples métodos (Scrum + Kanban + XP)** | ✅ DA ideal | Híbrido por diseño, no por workaround |
| **Cultura de empoderamiento y autoorganización** | ✅ DA ideal | Bottom-up, no top-down |
| **Organización grande (>1000 personas) con necesidad de gobernanza estricta** | ⚠️ SAFe mejor | DA puede usarse pero SAFe es más estructurado |
| **3-9 equipos en un solo producto con dependencias** | ⚠️ Nexus mejor | DA funciona pero Nexus es más específico |
| **Proyectos con alta incertidumbre y necesidad de experimentación** | ✅ DA ideal | Ciclo de vida Exploratory es nativo |

## Where: Contextos de Aplicación

**Organizaciones que buscan evolucionar, no revolucionar**: Equipos ágiles existentes que quieren optimizar su WoW sin cambiar todo. Compañías con prácticas híbridas que necesitan coherencia sin rigidez.

**Entornos con múltiples tipos de trabajo**: TI disciplinada, desarrollo de productos (Hardware + Software + Servicios), transformación empresarial.

**Niveles de aplicación**: Equipo → Programa → Portfolio → Empresa.

## How: Metodología de Implementación

**Paso 1: Evaluar Contexto (Semanas 1-2)** — Identificar restricciones, cultura, habilidades actuales. Mapear flujo de valor y cuellos de botella.

**Paso 2: Formar Equipo Inicial (Semanas 3-4)** — Identificar Team Lead, Product Owner, Architecture Owner. Seleccionar miembros multifuncionales.

**Paso 3: Inception Workshop (Semana 5)** — Definir visión y alcance. Modelar arquitectura de alto nivel. Identificar riesgos.

**Paso 4: Seleccionar WoW Inicial (Semana 6)** — Usar DA Toolkit para elegir prácticas. Definir Definition of Done y criterios de calidad.

**Paso 5: Ejecutar y Mejorar (Iteraciones 2-4 semanas)** — Entregar incrementos funcionales. Realizar retrospectivas para ajustar WoW.

### Los 8 Principios de DA

1. **Delight Customers**: Priorizar valor real para usuarios
2. **Be Awesome**: Excelencia técnica y profesional
3. **Context Counts**: No hay soluciones universales
4. **Pragmatism**: Lo que funciona en práctica es lo que importa
5. **Choice is Good**: Múltiples opciones empoderan equipos
6. **Optimize Flow**: Mejorar todo el flujo, no solo desarrollo
7. **Organize Around Products**: Estructuras orientadas a valor
8. **Enterprise Awareness**: Considerar impacto organizacional

## How Much: Inversión, ROI y Benchmarks

| Componente | Rango de Inversión | Detalle |
|---|---|---|
| **Certificación DASM** | $500 - $1,000/persona | Disciplined Agile Scrum Master (2 días) |
| **Certificación DASSM** | $800 - $1,500/persona | Senior Scrum Master (2 días) |
| **Certificación DAVSC** | $1,000 - $1,800/persona | Value Stream Consultant (3 días) |
| **Coaching DA** | $150 - $350/hora | Coach certificado durante 3-6 meses |
| **Tiempo de transición** | 5-10% productividad inicial | Curva suave, 1-3 meses |

**Nota**: DA es significativamente **menos costoso** que SAFe en capacitación y coaching.

### ROI y Beneficios

- **20-40% mejora** en eficiencia al eliminar prácticas innecesarias
- **15-30% reducción** en time-to-market al optimizar flujo
- **Reducción de 30-50%** en costos de gobernanza excesiva
- **Punto de equilibrio**: 6-12 meses
- **ROI a 2 años**: 200-350%
