---
title: LLMs capabilities and boundaries
date: 2026-03-23
type: reference
technology: "gen-ai"
status: active
tags: ["llm-capabilities", boundaries, evaluation, limitations, "ai-assessment"]
keywords: [LLM capabilities, communication, transactional, cognitive, grounding, robustness, calibration, observability, tool use, RAG, agentic, boundaries, evaluation]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# LLMs capabilities and boundaries

| Capacidad principal | Subcapacidad | Qué hace bien al 2026 | Límites técnicos | Riesgo típico | Cómo evaluarla / pregunta fina |
|---|---|---|---|---|---|
| **Comunicación** | Redacción | Produce borradores claros, estructurados y adaptados al tono y audiencia. | Puede sonar convincente aunque el contenido sea incorrecto o incompleto. | Texto persuasivo pero falso o impreciso. | ¿Mantiene coherencia, exactitud factual y tono adecuado sin inventar datos? |
| **Comunicación** | Resumen | Condensa documentos largos y extrae puntos clave con buena legibilidad. | Pierde matices, excepciones y dependencias entre partes distantes del texto. | Omitir condiciones críticas o excepciones. | ¿Conserva los hechos esenciales y las restricciones importantes? |
| **Comunicación** | Traducción / localización | Traduce con fluidez y adapta registro mejor que generaciones previas. | Puede fallar en terminología técnica, legal o cultural de alta precisión. | Traducción correcta en general, pero errónea en términos sensibles. | ¿Preserva significado, terminología y contexto cultural? |
| **Comunicación** | Extracción | Identifica entidades, campos, patrones y relaciones en texto no estructurado. | Se degrada con documentos ambiguos, tablas complejas o formatos sucios. | Falsos positivos o campos omitidos. | ¿Extrae datos con exactitud campo por campo? |
| **Comunicación** | Conversación | Mantiene diálogo natural, responde preguntas y ajusta el nivel de detalle. | La continuidad puede degradarse en conversaciones largas o muy ramificadas. | Contradicciones o pérdida de contexto. | ¿Sostiene consistencia entre turnos y recuerda restricciones clave? |
| **Comunicación** | Estilo / tono | Puede adoptar voz ejecutiva, técnica, comercial o pedagógica. | A veces sobreajusta el tono y sacrifica precisión o sencillez. | Respuestas "bonitas" pero poco útiles. | ¿Se adapta al público sin perder claridad ni precisión? |
| **Transaccional** | Tool use básico | Llama herramientas, consulta sistemas y combina fuentes externas. | Puede elegir mal la herramienta o usarla en el orden incorrecto. | Acciones fuera de secuencia o con datos desactualizados. | ¿Selecciona correctamente la herramienta y respeta el flujo? |
| **Transaccional** | Orquestación de flujos | Coordina pasos multi-etapa: recopilar, validar, decidir y ejecutar. | La robustez cae cuando hay estados intermedios, dependencias o excepciones. | Tareas incompletas o loops operativos. | ¿Completa el proceso end-to-end sin perder estado? |
| **Transaccional** | Grounding / RAG | Integra conocimiento externo para reducir errores y conectar con datos propietarios. | Si la recuperación es mala, puede seguir alucinando con mucha fluidez. | Respuesta "grounded" pero incorrecta por recuperación débil. | ¿La respuesta depende de evidencia recuperada y esta es relevante? |
| **Transaccional** | Automatización de negocio | Apoya triage, clasificación, resúmenes operativos, soporte y documentación. | No reemplaza controles, auditoría ni manejo fino de permisos y excepciones. | Ejecutar sobre datos erróneos o sin autorización. | ¿Acelera el proceso sin romper controles ni gobernanza? |
| **Transaccional** | Integración empresarial | Se incorpora en CRM, soporte, analítica y desarrollo con valor real. | La adopción productiva exige gobierno, observabilidad y evaluación continua. | Brecha entre demo y producción. | ¿Funciona de forma estable en operación real y con monitoreo? |
| **Transaccional** | Autonomía limitada | Puede ejecutar tareas cerradas con supervisión parcial. | Autonomía alta sigue siendo frágil sin guardrails fuertes. | Acción no deseada con impacto operativo o financiero. | ¿Puede actuar solo dentro de límites bien definidos? |
| **Cognitiva** | Razonamiento paso a paso | Mejora en problemas de lógica, matemáticas aplicadas y programación. | No garantiza consistencia interna en cadenas largas de inferencia. | Saltos lógicos o conclusiones inválidas. | ¿Resuelve el problema sin romper la lógica intermedia? |
| **Cognitiva** | Generalización | Funciona en tareas nuevas si se parecen a patrones vistos. | La transferencia fuerte a contextos raros o adversariales sigue siendo limitada. | Caída brusca fuera de distribución. | ¿Sostiene desempeño cuando cambian las condiciones del caso? |
| **Cognitiva** | Planificación | Puede proponer planes, descomponer tareas y secuenciar pasos. | Los planes pueden ser superficiales y poco robustos ante cambios de estado. | Plan correcto en papel, fallido en ejecución. | ¿El plan contempla dependencias, riesgos y puntos de control? |
| **Cognitiva** | Incertidumbre / calibración | Puede expresar dudas y matices mejor que antes. | Aun así puede responder con exceso de confianza ante información incierta. | Seguridad injustificada. | ¿Reconoce límites, supuestos y grado de confianza? |
| **Cognitiva** | Veracidad factual | Mejora con RAG, herramientas y verificación externa. | La alucinación sigue siendo un problema central. | Citas inventadas o hechos mezclados. | ¿Se puede verificar externamente cada afirmación importante? |
| **Cognitiva** | Memoria de trabajo efectiva | Maneja más contexto que antes e integra más información simultánea. | La atención es finita; parte del contexto se degrada o se ignora. | Pérdida de restricciones o contradicciones. | ¿Mantiene todas las restricciones relevantes a lo largo del intercambio? |
| **Variables transversales** | Grounding | Reduce dependencia del conocimiento paramétrico puro. | Si la recuperación falla, la respuesta también puede fallar. | Evidencia insuficiente o sesgada. | ¿La respuesta está anclada en fuentes o datos verificables? |
| **Variables transversales** | Robustez | Tolera variaciones de prompt, ruido y formato mejor que antes. | Sigue mostrando sensibilidad a formulaciones distintas. | Desempeño inconsistente. | ¿El resultado se mantiene estable en prompts equivalentes? |
| **Variables transversales** | Calibración | Mide si el modelo sabe cuándo sabe y cuándo no. | Puede sobreestimar su certeza. | Confianza falsa. | ¿La seguridad expresada coincide con la precisión real? |
| **Variables transversales** | Observabilidad | Permite auditar inputs, recuperación, herramientas y salidas. | Sin telemetría, el fallo es difícil de diagnosticar. | Errores opacos. | ¿Se puede rastrear por qué respondió o actuó así? |
| **Variables transversales** | Dependencia de contexto | Mide cuánto se degrada con casos largos o complejos. | El rendimiento cae al crecer la longitud o la complejidad. | Omisión de restricciones importantes. | ¿Sostiene calidad cuando el caso se hace más grande? |
| **Variables transversales** | Riesgo de acción | Clasifica el daño potencial de una respuesta incorrecta. | A mayor impacto, mayor necesidad de control humano. | Daño legal, financiero, operativo o reputacional. | ¿Qué pasa si se equivoca y cuánto costaría corregirlo? |
