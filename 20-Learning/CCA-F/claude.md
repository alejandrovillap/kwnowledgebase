---
title: Claude
date: 2026-03-21
type: resume
technology: "gen-ai"
status: active
tags: [claude, prompting, "4d-framework", delegation, artifacts, "ai-fluency"]
keywords: [prompting, 4D framework, delegation, description, discernment, diligence, artifacts, skills, projects, AI fluency]
source: "notion-migration"
project: ""
certification: CCA
confidence: high
---

# Claude

## What is a good prompt?

1. **Setting the stage:** What is your role and what are your objectives? Is there context about your work that Claude should know about?
2. **Defining the task:** What action do you want Claude to take? Do you want Claude to write, analyze, build, or something else?
3. **Specifying rules:** What's the style or tone you want Claude to use? Are there examples that you can attach to show Claude what you're looking for?
4. **Adding context:** Uploads, connectors, and custom preferences offer ways to give Claude even more context about your work. Supported file types include PDF, DOCX, CSV, TXT, and common image formats like PNG and JPEG.
5. **Iterating on Claude's responses:**
   - Ask follow-up questions: Build on Claude's response by asking for more detail, a different angle, or clarification.
   - Provide feedback: Tell Claude what you liked and didn't like about its response.
   - Redirect or restart: If Claude went in a different direction, steer it back. Worst case, restart your conversation in a new chat to fully refresh the context.

## Common problems

| Challenge | What's happening | Try this |
| --- | --- | --- |
| **Claude's response is too generic** | Your prompt didn't include enough context about your specific situation | Add details about your audience, role, or constraints. Instead of "Write an email about the project delay," try a detailed version with context about the client and situation. |
| **The response is too long (or too short)** | Claude is guessing at appropriate length | Be explicit: "Give me a two-paragraph summary" or "Keep this under 100 words" |
| **Claude didn't follow my format** | Claude understood *what* you want but not *how* you want it presented | Show, don't just tell. Provide an example of the format, or describe the structure explicitly. |
| **I got confident-sounding information that turned out to be wrong** | Claude occasionally generates plausible but incorrect information, especially with specific facts or niche topics | For high-stakes work, verify key facts independently. Ask Claude to cite sources or indicate confidence level. Enable web search to ground responses in current information. |
| **The tone isn't right** | Claude defaults to helpful and professional, which may not match your needs | Describe the tone in plain language: "Make this more conversational" or "This should sound authoritative and formal." |

## 4D Framework for AI Fluency

- **Delegation:** Deciding on what work should be done by humans, what work should be done by AI, and how to distribute tasks between them.
- **Description:** Effectively communicating with AI systems. Includes clearly defining outputs, guiding AI processes, and specifying desired AI behaviors.
- **Discernment:** Thoughtfully and critically evaluating AI outputs, processes, behaviors and interactions. Includes assessing quality, accuracy, appropriateness, and determining areas for improvement.
- **Diligence:** Using AI responsibly and ethically. Includes making thoughtful choices about AI systems and interactions, maintaining transparency, and taking accountability for AI-assisted work.

## Comparing the three modes

| | **Chat** | **Cowork** | **Code** |
| --- | --- | --- | --- |
| **Optimized for** | Quicker exchanges: exploring ideas, iterative drafting, quick answers, learning through dialogue | Complex or sustained work: research, analysis, file organization, producing finished documents and deliverables | Building software: writing, testing, running and deploying code |
| **Key features** | Quick entry, dictation | Work from local folders, plugins, subagents, scheduled tasks | Ask/Code/Plan modes, visual diffs, git integration, local and remote environments |
| **Tools and extensions** | Connectors, Skills, Claude in Chrome | Connectors (local and remote), Skills, Claude in Chrome, Plugins | Connectors, Skills, Claude in Chrome, Plugins, Hooks |

## Projects

**Key takeaways:**
- **Projects are self-contained workspaces** with their own memory, chat histories, knowledge bases, and customized instructions.
- **Project knowledge enhances Claude's understanding** by letting you upload relevant documents that Claude references across all chats within that project.
- **Project instructions guide Claude's behavior** — you can specify tone, expertise level, response style, and more.
- **Projects scale automatically**. When your knowledge base approaches context limits, Claude enables RAG mode to expand capacity by up to 10x.
- **For Claude for Work users, projects enable collaboration**. Share projects with teammates so everyone benefits from the same context.

**Best practices for projects:**
- Start focused, then expand.
- Keep your knowledge base current.
- Write clear instructions.
- Group related documents.
- Reference documents by name.

## What are Artifacts?

Artifacts are standalone, interactive outputs that Claude creates in a dedicated window alongside your conversation. Claude automatically creates an artifact when content:
- Is significant and self-contained, typically over 15 lines
- Is something you're likely to want to edit, iterate on, or reuse
- Represents complex content that stands on its own
- Is content you'll want to reference or use later

**Common artifact types:** Documents (markdown), Code snippets, HTML pages, SVG images, Mermaid diagrams, React components.

## What are Skills?

Skills are folders of instructions, scripts, and resources that Claude loads dynamically to improve performance on specialized tasks. Think of them as expertise packages.

- **Anthropic Skills** — created and maintained by Anthropic (Excel, Word, PowerPoint, PDF). Available to all paid users.
- **Custom Skills** — created by you or your organization for specialized workflows and domain-specific tasks.

## AI Fluency

- AI Fluency means engaging with AI systems effectively, efficiently, ethically, and safely.
- The AI Fluency Framework centers on the "4D" competencies: Delegation, Description, Discernment, and Diligence.
- Three ways people engage with AI: Automation, Augmentation, Agency.

### Delegation
- Problem Awareness: clearly understanding your goals and the nature of the work before involving AI.
- Platform Awareness: understanding the capabilities and limitations of different AI systems.
- Task Delegation: thoughtfully distributing work between humans and AI.

### Description
- Product Description: Clearly defining what you want the AI to create.
- Process Description: Guiding how the AI approaches your request.
- Performance Description: Defining how you want the AI to behave during your collaboration.

### Discernment
- Product Discernment: Evaluating the quality of AI outputs (accuracy, appropriateness, coherence, relevance).
- Process Discernment: Assessing how the AI arrived at its output.
- Performance Discernment: Evaluating how the AI behaves within the collaboration process itself.

### Diligence
- Creation Diligence: Being thoughtful about which AI systems you choose and how you work with them.
- Transparency Diligence: Being open about AI's role in your work.
- Deployment Diligence: Taking ownership for AI-assisted outputs you share with others.

### Effective Prompting Techniques
Six foundational prompting techniques:
1. Give context: Be specific about what you want, why you want it, and relevant background.
2. Show examples: Demonstrate the output style or format you're looking for.
3. Specify constraints: Clearly define format, length, and other output requirements.
4. Break complex tasks into steps: Guide the AI through multi-step reasoning.
5. Ask the AI to think first: Give space for the AI to work through its process.
6. Define the AI's role or tone: Specify how you want the AI to communicate.
