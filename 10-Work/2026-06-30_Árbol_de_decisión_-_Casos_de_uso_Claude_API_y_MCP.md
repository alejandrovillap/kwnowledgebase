---
certification: ''
confidence: medium
date: null
keywords:
- envío de dinero
- transformar documentos
- sistematización de contenidos
- CI/CD
- sistema agéntico
- DDA
- extracción API
- desarrollo asistido
- Claude Code
- MCP
- usuario final
- desarrollador
project: ''
status: to-review
tags:
- MCP
- API
- agentes
- Claude
- flujo-decision
- arquitectura
target_folder: 10-Work
technology: gen-ai
title: Árbol de decisión - Casos de uso Claude API y MCP
type: idea
---

Inicio

Envío de dinero → No → Propósito → Transformar documentos → No → Internalización
                                                                          ↓
                                                              2. Sistematización de contenidos
                                                                          ———————
                                                                          CI/CD
                                                                          ↓
                                                                          i.PI
                                                                          b. MCP

↓ sí

Es desarrollador → No → 3. Sistema agéntico
usuario final          ————————
                        DDA
                        ↓
                        i.PI
                        s. MCP

↓ sí

                    sí ↓

                    4 - Extracción
                    API
                    ————————
                    API
                    b. MCP

1. Desarrollo asistido
———————————
Claude
Code
↓
API
> MCP

![Decision Flowchart for Use Cases](../assets/2026-06-30-diagram-01.png)
> **Auto description:** A hand-drawn flowchart starting with an oval labeled 'Inicio' (Start). It branches into a diamond decision node 'Envío de dinero' (Money transfer) with a 'No' path leading to 'Propósito' (Purpose), which leads to another diamond 'Transformar documentos' (Transform documents). The 'No' branch leads to 'Internalización' (Internalization), which flows down to '2. Sistematización de contenidos' (Systematization of content), underlined in red, with 'CI/CD' noted, then arrows to 'i.PI' and 'b. MCP' in green. The 'Sí' (Yes) branch from 'Envío de dinero' leads to a diamond 'Es desarrollador / usuario final' (Is developer / end user). The 'No' path leads to '3. Sistema agéntico' (Agentic system), underlined in red with 'DDA', then green arrows to 'i.PI' and 's. MCP'. The 'Sí' path leads to '1. Desarrollo asistido' (Assisted development), underlined in blue, with 'Claude Code' noted, then green arrows to 'API' and '> MCP'. The 'Sí' branch from 'Transformar documentos' leads to '4 - Extracción API' (API Extraction), underlined in red, with green arrows to 'API' and 'b. MCP'.
