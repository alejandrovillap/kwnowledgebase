---
certification: ''
confidence: high
date: 2026-01-01
keywords:
- team productivity
- AI-assisted tasks
- Jira
- control chart
- cycle time
- JQL
- labels
- custom fields
- delivery stability
- AI measurement
- PERF
project: ''
source: notion-migration
status: active
tags:
- team-productivity
- ai-measurement
- jira
- cycle-time
- control-chart
- perf
target_folder: 20-Learning/Cognitive-PM-AI
technology: gen-ai
title: Measuring Team Productivity with AI
type: reference
updated: '2026-07-31'
---
# Measuring Team Productivity with AI

## Principles

1. **Frame productivity in business terms**: Use every bit of information to make a case that benefits the business (drives sales, headcount expansion, etc.). A strong productivity case improves client relationships and supports presales.

2. **Make output checkable with anecdotal evidence**: Customers should be able to verify productivity increases themselves in the task tracking system. Combine quantitative and qualitative analysis — back up every output with concrete examples. Metric tools like LinearB, DC PERF, and TaskTop are often black boxes for clients.

3. **Use AI on a percentage of tasks for valid comparison**: Don't use AI on 100% of tasks immediately — doing so eliminates the control group needed for comparison. Apply AI to a representative percentage of tasks to measure AI-assisted vs. non-AI-assisted performance cleanly. Prevent estimation drifting by estimating tasks as if done the old way; productivity improvement shows up in cycle time, not in inflated estimates.

## Setting Up Project Management Tools

In Jira, Rally, or Azure Boards: mark tasks as AI-assisted using **labels (tags)** or **custom fields** to enable later analysis and comparison.

### Labels Approach (simpler but error-prone)

Add labels directly to tasks: `ai-assisted-ba`, `ai-assisted-qa`, `ai-assisted-dev`.

- Pros: flexible, no configuration needed, works when PM/DM doesn't control field list.
- Cons: typos, inconsistencies, creative label names ("aiba" instead of "ai-assisted-ba").

### Custom Fields Approach (more structured)

In Jira: Settings → Issues → Custom Fields → Create Custom Field (Select List type). Name it "AI Assistance" with options: Business Analysis, Development, Quality Assurance.

JQL for custom field: `"AI Assistance" = "Development"` or `"AI Assistance" is not empty`.

## Basic Analysis with Jira Control Chart

The **Control Chart** in Jira tracks cycle time — time issues spend from In Progress to Done. Key features:
- **Rolling Average Line**: average cycle time over a period.
- **Standard Deviation Bands**: variability; outliers fall outside these bands.
- **Data Points**: each represents one issue.

### Steps for Comparative Analysis

1. **Ensure "Done" filters**: Only include completed tasks. Exclude Duplicate/Rejected resolutions.
2. **Create separate filters**: by issue type (Feature, Defect, Debt), size (Fibonacci intervals), and AI assistance label/field.
3. **Apply filters to Control Chart**: compare AI-assisted vs. non-AI-assisted for same issue types and sizes.
4. **Analyze**: Look at average cycle time, variability (standard deviation bands), and outliers.

### Comparative Analysis Table Structure

| Category | AI-Assisted | Non-AI-Assisted | Improvement in Time | Reduction in Variability |
|---|---|---|---|---|
| Feature - Small (0-1 SP) | X days | Y days | Z% faster | A% less variability |
| Feature - Medium (2-3 SP) | X days | Y days | Z% faster | A% less variability |
| Defect - Small | X days | Y days | Z% faster | A% less variability |
| Debt - Small | X days | Y days | Z% faster | A% less variability |

Use **Fibonacci sequence intervals** (0-1, 1-2, 2-3, 3-5, 5-8) to categorize tasks by estimation size for more precise analysis.

### Phase-Level Analysis

Configure Control Chart to track specific development phases:
- **Dev phase**: "Development Started" → "Development Completed" with `ai-assisted-dev` filter.
- **QA phase**: "QA Started" → "QA Completed" with `ai-assisted-qa` filter.
- **BA phase**: "Analysis Started" → "Analysis Completed" with `ai-assisted-ba` filter.

## Importance of Standard Deviation

A smaller standard deviation area indicates more predictable, consistent task completion. AI assistance can help standardize processes and reduce outliers — a key benefit beyond just average speed improvement.

## JQL Reference

```
-- Done filter (exclude cancelled/rejected)
status in ("Closed", "Resolved", "Completed") AND resolution in ("Fixed", "Implemented")

-- AI-assisted filter
labels in ("ai-assisted-ba", "ai-assisted-qa", "ai-assisted-dev")

-- Feature filter
issuetype = "Feature"

-- Story points range
"Story Points" > 1 AND "Story Points" <= 2
```

## Marking AI-Assisted Commits

Implement a consistent tagging/commenting system in version control to indicate AI-assisted code commits, enabling later analysis and performance comparison.

## PERF Tool (EPAM internal)

DC PERF and similar tools measure key performance indicators, configurable to differentiate AI-assisted from standard tasks. Available at delivery.epam.com → project → Metrics.
