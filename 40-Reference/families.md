---
title: Families
date: 2026-03-22
type: reference
technology: "gen-ai"
status: active
tags: ["llm-families", "model-comparison", openai, anthropic, pricing, "context-window"]
keywords: [LLM families, OpenAI, Anthropic, Google Gemini, model comparison, GPT, Claude, Gemini, pricing, context window]
source: "notion-migration"
project: ""
certification: ""
confidence: high
---

# AI Model Families — Comparative Reference

## OpenAI Families

| Provider | Family | Model | Role | Launch Date | Retirement | Max Context | Knowledge Cutoff | Input USD/1M | Output USD/1M |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| OpenAI | GPT-4o | gpt-4o | Caballo de batalla multimodal 4.x | 13-05-2024 | ChatGPT: 13-02-2026 (API sigue activa) | 128k | ~oct-2023 | ~2.50 | ~10.00 |
| OpenAI | GPT-4.1 | gpt-4.1 | Caballo de batalla long-context | 13-04-2025 | ChatGPT: 13-02-2026 | ~1,000,000 | Jun-2024 | 2.00 (0.50 cached) | 8.00 |
| OpenAI | GPT-4.1 | gpt-4.1-mini | Caballo de batalla costo/beneficio | 14-05-2025 | ChatGPT: 13-02-2026 | 1M | Jun-2024 | ~0.40 | ~1.60 |
| OpenAI | GPT-4.1 | gpt-4.1-nano | Tier barato / router | 14-05-2025 | Sin fecha | 1M | Jun-2024 | ~0.10 | ~0.40 |
| OpenAI | GPT-5 | gpt-5 (core) | Caballo de batalla frontier | 07-08-2025 | API activa; variantes ChatGPT retiro 13-02-2026 | 200k–400k | 2025 | >4 | >16 |
| OpenAI | GPT-5 | gpt-5-mini | Caballo de batalla costo/beneficio 5.x | ~Q4-2025 | Sin retiro | 400k aprox | 2025 | Intermedio | Intermedio |
| OpenAI | GPT-5 | gpt-5-nano | Tier barato 5.x | ~Q4-2025 | Activo en 2026 | ~400k | 2025 | Muy bajo | Muy bajo |
| OpenAI | GPT-5.4 | gpt-5.4 | Caballo de batalla premium 5.x | ~Q1-2026 | Activo (default 2026) | Short: 100k+; Long: >272k | 2025 | Short: ~2.50; Long: ~5.00 | Short: ~15; Long: ~22.50 |
| OpenAI | GPT-5.4 | gpt-5.4-mini | Caballo de batalla costo/beneficio 5.4 | ~Q1-2026 | Activo | Intermedio | 2025 | <2.50 | <15 |
| OpenAI | GPT-5.4 | gpt-5.4-nano | Tier barato 5.4 | ~Q1-2026 | Activo | Amplio | 2025 | Muy bajo | Muy bajo |

## Anthropic Claude Families

| Provider | Family | Model | Role | Launch Date | Retirement | Max Context | Knowledge Cutoff | Input USD/1M | Output USD/1M |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Anthropic | Claude 3.5 | claude-3-5-sonnet-20240620 | Mid-tier 3.5 inicial | 20-06-2024 | Retirado 28-10-2025 | 200k | Abril 2024 | ~3 | ~15 |
| Anthropic | Claude 3.5 | claude-3-5-sonnet-20241022 (v2) | Mid-tier v2 | 22-10-2024 | Retirado 28-10-2025 | 200k | Abril 2024 | ~3 | ~15 |
| Anthropic | Claude 3.7 | claude-3-7-sonnet-20250224 | Experimental / transición a 4.x | 24-02-2025 | Superseded | 200k | Oct 2024 | ~3 | ~15 |
| Anthropic | Claude 4 | claude-sonnet-4-20250522 | Caballo de batalla 4.0 | 22-05-2025 | Activo (superseded por 4.5/4.6) | ≤200k | ~Marzo 2025 | ~3 | ~15 |
| Anthropic | Claude 4.1 | claude-opus-4-1-20250801 | Flagship reasoning 4.1 | Ago 2025 | Superseded por Opus 4.5/4.6 | ≥200k | ~Marzo 2025 | ~15 | ~75 |
| Anthropic | Claude 4.5 | claude-sonnet-4-5-20250929 | Caballo de batalla 4.5 | Sep 2025 | Superseded por Sonnet 4.6 | Hasta 1M beta / 200k estándar | ~Marzo 2025 | ≈3 | ≈15 |
| Anthropic | Claude 4.5 | claude-haiku-4-5-20251015 | Tier barato 4.5 | Oct 2025 | Activo 2026 | 200k | ~Marzo 2025 | ≈0.25–1 | ≈1–5 |
| Anthropic | Claude 4.5 | claude-opus-4-5-20251120 | Flagship reasoning 4.5 | Nov 2025 | Superseded por Opus 4.6 | Hasta 1M | ~Marzo 2025 | ≈15 | ≈75 |
| Anthropic | Claude 4.6 | claude-sonnet-4-6-20260217 | **Caballo de batalla recomendado 2026** | 17-02-2026 | Activo | Hasta 1M beta / 200k estándar | May 2025 | ≈3 | ≈15 |
| Anthropic | Claude 4.6 | claude-opus-4-6-20260205 | Flagship premium 2026 | 05-02-2026 | Activo | Hasta 1M | May 2025 | ≈15+ | ≈75+ |

## Google Gemini Families

| Provider | Family | Model | Role | Launch Date | Retirement | Max Context | Knowledge Cutoff | Input USD/1M | Output USD/1M |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Google | Gemini 1.5 Pro | gemini-1.5-pro-001 | Caballo de batalla 1.5 Pro (v1) | 23-05-2024 GA | Retirado en Vertex: 24-05-2025 | Hasta 2M | ~2023–2024 | ~3–5 | ~15–20 |
| Google | Gemini 1.5 Pro | gemini-1.5-pro-002 | Caballo de batalla 1.5 Pro (v2) | 24-09-2024 GA | Retirado: 24-09-2025 | Hasta 2M | ~2024 | ~1.25–2.5 | ~10–15 |
| Google | Gemini 1.5 Flash | gemini-1.5-flash-001 | Tier barato 1.5 (v1) | 23-05-2024 GA | Retirado: 24-05-2025 | 100k–1M | ~2024 | Muy bajo | Muy bajo |
| Google | Gemini 1.5 Flash | gemini-1.5-flash-002 | Tier barato 1.5 (v2) | 24-09-2024 GA | Deprecado 2025 | Hasta ~1M | ~2024 | Muy bajo | Muy bajo |
| Google | Gemini 2.0 Flash | gemini-2.0-flash-001 | Caballo de batalla 2.0 barato | 05-02-2025 GA | Shutdown: 17-06-2026 | 1M-class | ~late-2024 | Muy bajo | Bajo |
| Google | Gemini 2.0 Flash Lite | gemini-2.0-flash-lite-001 | Tier ultra-barato | 25-02-2025 | Shutdown: 01-06-2026 | Decenas de miles | ~late-2024 | Muy bajo | Muy bajo |
| Google | Gemini 2.5 Flash | gemini-2.5-flash-001 / flash-lite / image | Caballo barato multimodal 2.5 | 2025 | Deprecación planificada: 17-06-2026 | ~1M | ~early-2025 | Muy bajo | Bajo |
| Google | Gemini 3 Flash | gemini-3-flash-preview | Tier barato "inteligente" 3.x | 17-12-2025 (preview) | Sin fecha (preview) | 1M / 64k output | Enero 2025 | ≈0.5 in / 3 out | Bajo |
| Google | Gemini 3 Pro / 3.1 Pro | gemini-3-pro-preview → gemini-3.1-pro-preview | Caballo de batalla premium 3.x | Late 2025; 3.1 en 2026 | gemini-3-pro-preview deprecado 09-03-2026 | ~1M | 2025 | Alto | Alto |
