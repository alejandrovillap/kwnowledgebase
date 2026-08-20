---
_trash_source: 20-Learning/CCA-F/Markdown_for_AI_Workflows_—_Presentation_&_Reference_Guide.md
certification: ''
confidence: high
date: '2026-08-20'
keywords:
- markdown
- markitdown
- token consumption
- file weight
- plain text
- docx
- PDF conversion
- MarkItDown CLI
- VS Code extension
- git version control
- LLM native format
- cheatsheet
project: ''
source: null
status: active
tags:
- markdown
- token-efficiency
- markitdown
- version-control
- plain-text
- vscode
- microsoft
- file-conversion
target_folder: 20-Learning/CCA-F
technology: gen-ai
title: Markdown for AI Workflows — Presentation & Reference Guide
type: lesson-learned
updated: '2026-08-20'
---
# Markdown

## Background

Two weeks ago, in this same room, we were talking about something that's been quietly draining us: token consumption. Every time we uploaded a heavy Word doc, a bloated PDF, a screenshot — we were paying an invisible cost for weight we never actually needed.

It's like driving a muscle car in the middle of an oil crisis. It looks incredible. It sounds incredible. But every time you start the engine, you're burning fuel you can't really afford to burn anymore. A .docx file is exactly that under the hood: it's not plain text — it's a compressed archive carrying styles, themes, fonts, and metadata you never see on screen, but that you still pay for every time that file gets opened and processed. In our own test, that hidden baggage was over thirty times heavier than the actual content.

**So we found the Prius: Markdown.**

Now — most people don't buy a Prius because it's beautiful. They buy it because it performs. It gets you where you need to go, burning a fraction of the fuel, without the dead weight. And to be fair, the latest generation is actually gorgeous — so even the *"not pretty"* argument is starting to lose ground.

But here's the part that matters for us today: switching to a hybrid means relearning how to drive. Regenerative braking behaves differently. The instrument cluster shows you things a gas engine never did. You don't just get in and drive exactly like before — there's a short learning curve before it becomes second nature.

That's exactly what's in front of us with Markdown. It's not just a new file extension — it's a small set of new habits: how we write headers, how we format a list, how we structure a table. Ten minutes from now, you'll have relearned how to drive.

## Alright — let's get you behind the wheel.

The dashboard display. In a gas car, you've got one gauge cluster, always the same size. In the Prius, the display resizes based on what matters most right now. That's your headers:

# Main Display → the big one, your document title
## Secondary Display → a section
### Small Readout → a sub-point

More # symbols, smaller the display. That's it — three levels, and you've covered 90% of what you'll ever need.

The hazard lights. You want something to stand out — an assumption, a risk, a deadline. You don't redesign the dashboard, you just flip the switch: **this matters** and it's bold. *this is a side note* and it's italic.

Cruise control checklist. Before you even start driving, you run through your pre-flight list. That's a bullet:
- check mirrors
- check fuel
One dash, one space, done. Need order instead of a checklist? Use numbers: 1. check mirrors.

The nav system. You type an address, it takes you somewhere else. That's a link:
[Governance Charter](http://www.epam.com) — the visible text is what you see on the dashboard, the URL is where it actually takes you.

The onboard diagnostics readout. Raw, exact, no interpretation — a part number, a command, a piece of code. You don't want that "translated" or styled, you want it exactly as-is:
`use_case_id_2026` — inline, for a short reference. Three backticks and a line break if you need a whole block of it.

The trip computer. Miles, average speed, fuel economy — data laid out in columns you can scan at a glance. That's a table:
| Column | Column | with a line of dashes underneath to separate the header row.

Six controls. That's the entire dashboard. Everything else in Markdown is a variation on these. You can refer to the **Cheatsheet** section for further details.

## So why now? Why is a 20-year-old idea suddenly the thing everyone's switching to?

Three things changed in the industry — and none of them are hype.

**First: every gas station started stocking a different fuel** The AI tools we use every day — the ones drafting, summarizing, reviewing our work — speak Markdown natively. It's the format they generate by default and read most cleanly. That's not a coincidence; it's plain text, so there's no complex structure to decode. When the infrastructure around you shifts to a new fuel type, driving the old muscle car doesn't stop working — it just stops being the smart choice.

**Second: the black box** Every hybrid logs exactly what happened, mile by mile — when you braked, when the engine kicked in, what changed between yesterday's drive and today's. That's version control. Because Markdown is plain text, tools like Git can show you precisely what changed in a document, line by line, between one version and the next. Try doing that with a .docx — you get "Proposal_v3_FINAL_REVISED_ALEJANDRO.docx" sitting next to five other files that all claim to be final.

**Third: the fuel itself never runs out** A proprietary format is a proprietary fuel — if the company that made it disappears, or changes the formula, your car stops running. A .md file is universal. It opens in any text editor, on any device, today or in fifteen years. No dependency on one company's software still existing.

That's the actual oil crisis. It's not that Word is broken — it's that the world we're operating in now runs on a different fuel, keeps a black box on everything, and rewards whoever isn't locked into someone else's tank.

## Let's make this real — not abstract. Who's actually driving this thing?

You already have, without knowing it. Every time someone typed ## in a Trello card to make a subtitle, or wrote **deadline** in a Slack message to make it bold — that was Markdown, running quietly in the background. No one announced it. It was just there.

- The engineers' garage: GitHub and GitLab. Every README file, every pull request description, every internal wiki page in software development is written in Markdown. If you've ever opened a project on GitHub and read the description on the main page — that's Markdown rendering in front of you.

- The note-takers: Notion, Obsidian, Bear. Entire products are built around it as the writing format — type # and it becomes a heading, no menu required.

- The messaging apps: Slack, Discord. Bold, italics, code blocks — all Markdown shorthand, built directly into the message box you use every day.

- The publishers: technical writers, documentation teams, blogs. Most software documentation today is written in Markdown first, then compiled into a website or a PDF at the end.

- And now: the AI layer. Every major AI assistant — including the one probably drafting half of this talk with you — generates and reads Markdown by default.

The point isn't *"here's a new tool to learn."* It's: you're already fluent in the accent, you just didn't know it had a name.

## It's not about winners and losers

Now, the honest part — because a good driving instructor doesn't tell you the muscle car is garbage. It's not. It's just the wrong car for daily commuting.

Where the Prius wins:

- Fuel efficiency, proven with data. We measured it earlier: same content, 31 times less file weight, because there's no hidden engine block of styles and themes running underneath.
- The black box. Clean, line-by-line version tracking — you always know exactly what changed and when.
- It starts anywhere. Any text editor, any device, no dealership required. A .md file from ten years ago opens exactly the same today.
- It speaks the new fuel. Native format for AI tools — no translation layer needed.

Where the muscle car still wins — and we should say this out loud:

- Design control. Branding, custom fonts, precise layout, a polished cover page for a client — Markdown wasn't built for that. Word (or PowerPoint, or Canva) still does that job better.
- The dealership experience. A client expects a client-facing deliverable to look a certain way. Handing them a .md file instead of a formatted proposal is the wrong call, not a bold one.
- Consistency isn't guaranteed. Different tools render Markdown slightly differently — what looks right in one app might shift slightly in another. That's why standards like CommonMark and GitHub Flavored Markdown exist: to make the rendering predictable.

So here's the actual rule for our team, not *"always use one or the other"*:

- Draft in the Prius. Deliver in whatever the client's garage expects.
- Internal notes, working documents, technical content, anything version-controlled or AI-assisted → Markdown.
- Final client-facing deliverables that need to look polished → export to Word or PDF at the end. You get the writing speed and the version history while you work, and the finished look when it actually matters.

| | Prius (Markdown) | Muscle car (Word) |
|---|---|---|
| Best for | Working docs, internal notes, AI workflows | Polished, client-facing deliverables |
| File weight | Light | Heavy |
| Version tracking | Clean, line-by-line | Messy |
| Design control | Minimal | Full |
| Opens without special software | Yes, always | Needs Word or equivalent |

*Hard to read, isnt it?*

|                                | Prius (Markdown)                           | Muscle car (Word) |
|---|---|---|
| Best for                       | Working docs, internal notes, AI workflows | Polished, client-facing deliverables |
| File weight                    | Light                                      | Heavy |
| Version tracking               | Clean, line-by-line                        | Messy |
| Design control                 | Minimal                                    | Full |
| Opens without special software | Yes, always                                | Needs Word or equivalent |

*What about, now? you only need to add spaces, but not mandatory*

So let's bring it back to where we started.

Last week, we noticed we'd been driving a muscle car through an oil crisis — burning fuel we couldn't afford, on files carrying thirty times more weight than the content actually needed. It looked impressive. It just wasn't the right car for where we're headed.

We found the Prius. Not because it's flashy — most people don't buy one for that. They buy it because it performs, it's efficient, and it gets you exactly where you need to go without the dead weight in the trunk.

And yes, we had to relearn how to drive. Six new controls: headers, bold, lists, links, code, tables. That's it. That's the whole dashboard. You just spent ten minutes learning it, and most of you were already driving it without knowing it, every ## in a Trello card, every **bold** in Slack.

Here's the only thing I'm asking today: we're not scrapping the muscle car. It still has its place: client-facing deliverables still need to look like client-facing deliverables. But for everything else, our working documents, our notes, anything we draft with AI, anything we want real version control on, let's drive the Prius.

Not because it's trendy. Because in a world where every token has a cost, we can't keep burning fuel we don't have to burn.

## MarkItDown — converting files to Markdown

### What it is

**MarkItDown** is an open-source Python library and command-line tool, built by Microsoft, that converts files and documents into Markdown. It gained over 25,000 GitHub stars within its first two weeks, a strong signal of real adoption, not a niche experiment. It can be used as a library (`import markitdown`) or directly from the terminal (`markitdown file.pdf > document.md`).

Its stated purpose is not to produce a beautifully formatted document for humans, it's to prepare content cleanly for consumption by an LLM or a text-analysis pipeline. Markdown is the target format specifically because most large language models understand it natively and it's token-efficient.

### How it works

MarkItDown routes each file to a converter built for that format:

| Format | How it's processed |
|---|---|
| Word, PowerPoint, Excel | Direct extraction of structure (text, tables, headings) |
| PDF | Text extraction via the `pdfminer` library — **no built-in OCR** |
| HTML, CSV, JSON, XML | Direct structural parsing |
| ZIP | Recursively walks and converts every file inside |
| Images | Extracts EXIF metadata; **describing visual content requires connecting a vision-capable LLM** |
| Audio | Extracts metadata; **transcribing speech requires a speech-recognition step** |

### Does it send data to a third party?

This is the question that matters most before feeding it project material, and the honest answer is: **it depends on the format, and on how you configure it.** It is not a uniform yes or no.

**Stays fully local (nothing leaves the machine):**
- Word (.docx), PowerPoint (.pptx), Excel (.xlsx)
- PDF (text only — `pdfminer` runs locally)
- HTML, CSV, JSON, XML, ZIP

For this group — likely the large majority of consulting project material — there is no external service call by design. It's local text processing with local Python libraries.

**Leaves the machine by default, if used:**
- **Audio transcription.** By default, MarkItDown sends audio to **Google's Speech Recognition API** to transcribe it. This requires an internet connection, and the audio is genuinely transmitted to a Google server. Meeting recordings with client information should not go through this path without a confidentiality review first.

**Leaves the machine only if explicitly configured:**
- **Image description.** By default, MarkItDown does *not* describe what's in an image — it only extracts metadata. Generating a description requires manually wiring in an LLM client (e.g., OpenAI) in code. Without that configuration, nothing is sent.
- **Azure Document Intelligence** (`az-doc-intel`, optional dependency). If installed and enabled, documents are sent to an Azure API for processing — a billable external call. It's opt-in only.
- **Third-party plugins.** Supported, but disabled by default. If one is enabled, its data handling depends entirely on the plugin author — no guarantee it stays local.

### Security note from the project itself

The maintainers state explicitly that MarkItDown performs I/O with the privileges of the process running it — similar to `open()` or `requests.get()` — so it will access whatever that process can access. They recommend sanitizing inputs in untrusted environments and using the narrowest conversion function available (`convert_local()`, `convert_stream()`) rather than the generic one.

### Practical takeaway for project use

1. Text-based project documents (Word, Excel, PowerPoint, PDF, HTML) can be processed with confidence — fully local, no third-party transfer.
2. **Avoid the audio module unless the content is non-confidential** — it calls Google's API by default.
3. **Don't configure an LLM client for images or install `az-doc-intel` unless you know exactly what's being sent and where** — both are opt-in, so leaving them untouched means nothing leaves the machine.
4. Install only what's needed. Instead of `pip install markitdown[all]` (which pulls in every optional dependency, including audio), install targeted extras such as `markitdown[docx,pptx,xlsx,pdf]` to minimize the dependency surface.

## How to make our own Markdown from a file

If you'd rather skip the terminal entirely — no venv activation, no PowerShell execution-policy errors — you can convert files with a point-and-click extension inside VS Code. It's a third-party wrapper (publisher bioinfo, not an official Microsoft extension) around the same MarkItDown engine, and it manages its own isolated Python environment automatically.

Requirement: Python 3.10+ must still be installed and reachable via python --version, but you never touch a venv or activation script yourself — the extension handles that internally.

### Step 1 — Visual Studio Code from Microsoft Store or webpage

[Visual Studio Code](https://code.visualstudio.com/download?_exp_download=fb315fc982)

### Step 2 — Install the extension

From the Extensions view (left bar):

Open VS Code.
Open Extensions (Ctrl+Shift+X on Windows/Linux, Cmd+Shift+X on macOS).
Search for **MarkItDown**.
Click Install on the extension by publisher bioinfo.
Or from the command line:

code --install-extension bioinfo.markitdown-vscode
The first conversion you run will set up an isolated Python environment in the background (a few seconds to a couple of minutes). Every conversion after that is instant.

### Step 3 — Convert a file (Explorer context menu)

In the VS Code Explorer sidebar, locate the file you want to convert (PDF, DOCX, PPTX, XLSX, image, audio, etc.).
Right-click the file.
Select Convert to Markdown.
You can multi-select several files first (Ctrl+Click / Cmd+Click) and convert them all in one action.

### Step 4 — Convert a file (Command Palette)

Press Ctrl+Shift+P (Cmd+Shift+P on macOS) to open the Command Palette.
Type and select MarkItDown: Convert File to Markdown.
Choose the file(s) to convert from the picker.

### Step 5 — Find the output

The generated .md file is written to the same folder as the source file and opens automatically by default.

Create new vs. replace, with the extension
This is the one place the extension behaves differently from the CLI: by default it does not overwrite. If report.md already exists, converting report.pdf again produces report-1.md, report-2.md, and so on, instead of touching the original.

To make it replace the existing file like the CLI does, open Settings and change the overwrite behavior:

Open Settings (Ctrl+, / Cmd+,).
Search for markitdown.
Toggle markitdown.overwriteExisting to true.
Available settings
Setting	Default	Effect
markitdown.openFileOnSuccess	true	Automatically opens the generated .md file after conversion.
markitdown.overwriteExisting	false	When true, replaces an existing .md file instead of creating a numbered variant.

### Full Options Reference

Flag	Long form	Takes a value?	Purpose
-v	--version	no	Show the installed MarkItDown version and exit.
-o	--output	yes	Output file name. Creates the file if new, overwrites it if it already exists. Omit to print to stdout.
-x	--extension	yes	Hint the file extension (useful when piping from stdin, since there's no filename to infer type from).
-m	--mime-type	yes	Hint the file's MIME type.
-c	--charset	yes	Hint the file's charset (e.g. UTF-8).
-d	--use-docintel	no	Use Azure Document Intelligence for extraction instead of offline conversion. Requires -e.
—	--use-cu	no	Use Azure Content Understanding for extraction. Requires --cu-endpoint.
-e	--endpoint	yes	Azure Document Intelligence endpoint URL. Required with -d.
—	--cu-endpoint	yes	Azure Content Understanding endpoint URL. Required with --use-cu.
—	--cu-analyzer	yes	Content Understanding analyzer ID. Auto-selected by file type if omitted.
—	--cu-file-types	yes	Comma-separated file types to route to Content Understanding.
-p	--use-plugins	no	Enable installed third-party MarkItDown plugins for this conversion.
—	--list-plugins	no	List all installed third-party plugins, then exit.
—	--keep-data-uris	no	Preserve embedded data URIs (e.g. base64 images) in the output instead of stripping them.

Example combinations

# Convert a PDF via Azure Document Intelligence, output to a new file
markitdown scan.pdf -d -e "https://<your-endpoint>.cognitiveservices.azure.com/" -o scan.md

# Convert a scanned image, keep embedded images as base64 data URIs
markitdown photo.png --keep-data-uris -o photo.md

# Convert piped stdin content, hinting it's a PDF
cat invoice.pdf | markitdown -x .pdf -o invoice.md

# Use a third-party plugin
markitdown data.custom --use-plugins -o data.md

# List available plugins before running one
markitdown --list-plugins

Quick Reference Summary

New file: markitdown input.ext -o output.md (file doesn't exist yet → created)
Replace file: markitdown input.ext -o output.md (file exists → overwritten, same syntax)
Append instead of replace: markitdown input.ext >> output.md
Print only: markitdown input.ext
Pipe input: cat input.ext | markitdown
No terminal at all: VS Code Extensions → install MarkItDown (bioinfo) → right-click file → Convert to Markdown

## Cheatsheet

# Header 1
## Header 2
### Header 3
#### Header 4
##### Header 5
###### Header 6

**Bold**
*Italic*

- item 1
- item 2
- item 3

[Google](http://google.com)

##in line code

`# --- Declaraciones ---`
`from datetime import date`
`year = date.today().year`

`# --- User ---`
`name = input("What is your name? ")`
`print()`

##code block

```# --- Declaraciones ---```
```from datetime import date```
```year = date.today().year```

```# --- User ---```
```name = input("What is your name? ")```
```print()```

## Table

| column 1 | column 2 | column 3 | column 4 |
|---|---|---|---! *Mandatory line for renders*
| data 1 | data 2 | data 3 | data 4 |
