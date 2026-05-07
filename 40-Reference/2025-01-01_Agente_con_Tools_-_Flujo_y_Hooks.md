---
certification: ''
confidence: medium
date: '2025-01-01'
keywords:
- agente
- tools
- get_customer
- lookup_order
- process_refund
- escalate_to_human
- post_tool_use_hook
- normalizar
- predefined_hook
project: ''
status: to-review
tags:
- agent
- tools
- hooks
- refund
- escalation
- pipeline
target_folder: 40-Reference
technology: gen-ai
title: Agente con Tools - Flujo y Hooks
type: idea
---

Cliente
↓
Agente    Capacidades
           Programadas
↓
Tools

1. Get Customer - Predefined Hook
   id_cliente
2. Lookup order
   Busca pedido
   order_id
3. Process_refund
   pipeline
   requires order_id
4. Escalate to human    - Claridades
                        - Algo ambiguo
                        - No pregues
↓
Post tool use Hook
Normalizar
↓
Respuesta usuario

![Agent Tools Flowchart](../assets/2026-05-06-diagram-01.png)
> **Auto description:** A vertical flowchart showing the flow from a stick figure labeled 'Cliente' (Client) down to an 'Agente' (Agent) node annotated with 'Capacidades Programadas' (Programmed Capabilities) in red, then down to 'Tools'. Inside a green-bordered rectangle, four numbered tools are listed: 1. Get Customer (with id_cliente in blue), 2. Lookup order (with Busca pedido and order_id in blue), 3. Process_refund (with pipeline and requires order_id in blue), and 4. Escalate to human (with red annotations: Claridades, Algo ambiguo, No pregues). An arrow exits the box downward to 'Post tool use Hook / Normalizar' and then to 'Respuesta usuario' (User Response).
