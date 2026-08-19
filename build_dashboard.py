#!/usr/bin/env python3
"""
build_dashboard.py — Generate dashboard.html with all KnowledgeBase notes embedded.

The HTML is fully self-contained: data is embedded as JSON, no CDN dependencies.
Open dashboard.html in any browser to browse, filter, and read notes.

Usage:
    python build_dashboard.py
    python build_dashboard.py --out path/to/dashboard.html
"""

import re
import json
import argparse
from datetime import date
from pathlib import Path
from collections import defaultdict

from build_index import load_notes, BASE, FRONTMATTER_RE

FOLDER_META = {
    "10-Work":                      {"label": "Work & Projects",   "color": "#5B6EF5"},
    "20-Learning/CCA-F":            {"label": "CCA-F",             "color": "#22d3ee"},
    "20-Learning/PMI-ACP":          {"label": "PMI-ACP",           "color": "#60a5fa"},
    "20-Learning/AI-SDLC":          {"label": "AI & SDLC",         "color": "#818cf8"},
    "20-Learning/Cognitive-PM-AI":  {"label": "Cognitive PM AI",   "color": "#fb923c"},
    "20-Learning/Gemini-Enterprise": {"label": "Gemini Enterprise", "color": "#34d399"},
    "20-Learning/Antigravity":      {"label": "Antigravity",       "color": "#fbbf24"},
    "20-Learning/Certifications":   {"label": "Certifications",    "color": "#a78bfa"},
    "20-Learning/Coaching":         {"label": "Coaching",          "color": "#f472b6"},
    "20-Learning/RPA":              {"label": "RPA",               "color": "#2dd4bf"},
    "20-Learning/Deep-Learning":    {"label": "Deep Learning",     "color": "#c084fc"},
    "20-Learning/English-Grammar":  {"label": "English",           "color": "#94a3b8"},
    "40-Reference":                 {"label": "Reference",         "color": "#FBBF24"},
    "50-Archive":                   {"label": "Archive",           "color": "#6B7280"},
    "Journal":                      {"label": "Journal",           "color": "#F87171"},
}

HTML_TEMPLATE = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>KnowledgeBase</title>
<style>
/* ── Tokens ───────────────────────────────────────────────────── */
:root {
  --bg:          #0F1117;
  --surface:     #1A1D27;
  --surface-2:   #222534;
  --border:      #2A2D42;
  --text-1:      #E4E6F0;
  --text-2:      #8B8FA8;
  --text-3:      #4E5270;
  --accent:      #5B6EF5;
  --accent-bg:   rgba(91,110,245,.12);
  --mono:        ui-monospace,"Cascadia Code","Fira Code","Consolas",monospace;
  --sans:        -apple-system,"Segoe UI",system-ui,sans-serif;
  --radius:      6px;
  --sidebar-w:   220px;
  --header-h:    52px;
}
@media (prefers-color-scheme: light) {
  :root {
    --bg:        #F2F3F7;
    --surface:   #FFFFFF;
    --surface-2: #F2F3F7;
    --border:    #DDE0EC;
    --text-1:    #1A1D2E;
    --text-2:    #5A5E78;
    --text-3:    #9599B3;
  }
}
:root[data-theme="light"] {
  --bg:        #F2F3F7;
  --surface:   #FFFFFF;
  --surface-2: #F2F3F7;
  --border:    #DDE0EC;
  --text-1:    #1A1D2E;
  --text-2:    #5A5E78;
  --text-3:    #9599B3;
}
:root[data-theme="dark"] {
  --bg:        #0F1117;
  --surface:   #1A1D27;
  --surface-2: #222534;
  --border:    #2A2D42;
  --text-1:    #E4E6F0;
  --text-2:    #8B8FA8;
  --text-3:    #4E5270;
}

/* ── Reset ────────────────────────────────────────────────────── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
body {
  background: var(--bg);
  color: var(--text-1);
  font-family: var(--sans);
  font-size: 14px;
  line-height: 1.5;
  height: 100vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}
a { color: inherit; text-decoration: none; }

/* ── Header ───────────────────────────────────────────────────── */
header {
  height: var(--header-h);
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 0 20px;
  flex-shrink: 0;
  position: sticky;
  top: 0;
  z-index: 10;
}
.logo {
  font-family: var(--mono);
  font-size: 13px;
  font-weight: 600;
  color: var(--accent);
  letter-spacing: .04em;
  white-space: nowrap;
}
.stat-pill {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text-3);
  background: var(--surface-2);
  border: 1px solid var(--border);
  padding: 2px 8px;
  border-radius: 99px;
  white-space: nowrap;
  font-variant-numeric: tabular-nums;
}
.search-wrap {
  flex: 1;
  max-width: 360px;
  margin-left: auto;
  position: relative;
}
.search-wrap svg {
  position: absolute;
  left: 10px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-3);
  pointer-events: none;
}
#search {
  width: 100%;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text-1);
  font-family: var(--sans);
  font-size: 13px;
  padding: 6px 10px 6px 32px;
  outline: none;
  transition: border-color .15s;
}
#search:focus { border-color: var(--accent); }
#search::placeholder { color: var(--text-3); }
.theme-btn {
  background: none;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text-2);
  cursor: pointer;
  padding: 5px 8px;
  font-size: 13px;
  line-height: 1;
  transition: border-color .15s, color .15s;
}
.theme-btn:hover { border-color: var(--accent); color: var(--text-1); }

/* ── Server status indicator ──────────────────────────────────── */
.server-status {
  display: flex; align-items: center; gap: 5px;
  font-size: 11px; color: var(--text-3);
  padding: 4px 8px; border: 1px solid var(--border);
  border-radius: var(--radius); cursor: default; user-select: none;
  transition: border-color .2s, color .2s;
}
.server-status:hover { border-color: var(--text-3); }
.server-dot {
  width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0;
  background: #6b7280; transition: background .3s;
}
.server-status.online  .server-dot { background: #34d399; }
.server-status.offline .server-dot { background: #f87171; }
.server-status.online  { color: var(--text-2); }
.server-status.offline { color: #f87171; border-color: rgba(248,113,113,.3); }

/* ── Properties editor ────────────────────────────────────────── */
.props-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,.55);
  z-index: 200; display: none; align-items: flex-start;
  justify-content: center; padding-top: 80px;
}
.props-overlay.open { display: flex; }
.props-panel {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 10px; width: 480px; max-width: 92vw;
  box-shadow: 0 24px 60px rgba(0,0,0,.5);
}
.props-header {
  display: flex; align-items: center; justify-content: space-between;
  padding: 14px 18px; border-bottom: 1px solid var(--border);
}
.props-title { font-size: 13px; font-weight: 600; color: var(--text-1); }
.props-close {
  background: none; border: 1px solid var(--border); border-radius: var(--radius);
  color: var(--text-3); cursor: pointer; padding: 3px 8px; font-size: 13px;
  transition: border-color .12s, color .12s;
}
.props-close:hover { border-color: var(--accent); color: var(--text-1); }
.props-body { padding: 18px; display: flex; flex-direction: column; gap: 16px; }
.props-field { display: flex; flex-direction: column; gap: 6px; }
.props-label { font-size: 11px; font-weight: 600; text-transform: uppercase; letter-spacing: .06em; color: var(--text-3); }
.props-select, .props-input {
  background: var(--surface-2); border: 1px solid var(--border);
  border-radius: var(--radius); color: var(--text-1);
  font-size: 13px; padding: 7px 10px; outline: none;
  font-family: var(--sans); transition: border-color .15s;
}
.props-select:focus, .props-input:focus { border-color: var(--accent); }
.props-tags-wrap {
  display: flex; flex-wrap: wrap; gap: 6px; align-items: center;
  background: var(--surface-2); border: 1px solid var(--border);
  border-radius: var(--radius); padding: 6px 8px; min-height: 36px;
  cursor: text; transition: border-color .15s;
}
.props-tags-wrap:focus-within { border-color: var(--accent); }
.props-tag {
  display: flex; align-items: center; gap: 4px;
  background: var(--accent-bg); color: var(--accent);
  border: 1px solid var(--accent); border-radius: 4px;
  font-size: 11px; padding: 2px 6px; white-space: nowrap;
}
.props-tag-rm {
  cursor: pointer; opacity: .7; font-size: 12px; line-height: 1;
  background: none; border: none; color: inherit; padding: 0;
}
.props-tag-rm:hover { opacity: 1; }
.props-tag-input {
  flex: 1; min-width: 80px; background: none; border: none;
  color: var(--text-1); font-size: 12px; outline: none; padding: 2px 4px;
}
.props-footer {
  display: flex; justify-content: flex-end; gap: 8px;
  padding: 12px 18px; border-top: 1px solid var(--border);
}
.props-save {
  background: var(--accent); color: #fff; border: none;
  border-radius: var(--radius); padding: 7px 18px; font-size: 13px;
  cursor: pointer; font-weight: 600; transition: opacity .15s;
}
.props-save:hover { opacity: .85; }
.props-save:disabled { opacity: .45; cursor: default; }
.props-status { font-size: 11px; color: var(--text-3); }
.props-status.ok { color: #34d399; }
.props-status.err { color: #f87171; }

/* ── Quick switcher (Ctrl+K) ──────────────────────────────────── */
.qs-overlay {
  position: fixed; inset: 0; background: rgba(0,0,0,.55);
  z-index: 300; display: none; align-items: flex-start;
  justify-content: center; padding-top: 80px;
}
.qs-overlay.open { display: flex; }
.qs-panel {
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 10px; width: 560px; max-width: 92vw;
  box-shadow: 0 24px 60px rgba(0,0,0,.5); overflow: hidden;
}
.qs-input {
  width: 100%; padding: 14px 16px; font-size: 15px;
  background: transparent; border: none; border-bottom: 1px solid var(--border);
  color: var(--text-1); outline: none; font-family: var(--sans);
}
.qs-input::placeholder { color: var(--text-3); }
.qs-list { max-height: 340px; overflow-y: auto; }
.qs-item {
  display: flex; align-items: center; gap: 10px;
  padding: 9px 16px; cursor: pointer; transition: background .1s;
}
.qs-item:hover, .qs-item.active { background: var(--accent-bg); }
.qs-item-title { flex: 1; font-size: 13px; color: var(--text-1); white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.qs-item-folder { font-size: 11px; color: var(--text-3); white-space: nowrap; }
.qs-item-dot { width: 7px; height: 7px; border-radius: 50%; flex-shrink: 0; }
.qs-empty { padding: 24px 16px; text-align: center; color: var(--text-3); font-size: 13px; }
.qs-hint { display: flex; justify-content: space-between; padding: 7px 16px; border-top: 1px solid var(--border); font-size: 11px; color: var(--text-3); }

/* ── Body layout ──────────────────────────────────────────────── */
.layout {
  display: flex;
  flex: 1;
  min-height: 0;
}

/* ── Panel collapse handles ───────────────────────────────────── */
.panel-handle {
  width: 14px;
  flex-shrink: 0;
  background: var(--surface);
  border-left: 1px solid var(--border);
  border-right: 1px solid var(--border);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-3);
  font-size: 9px;
  line-height: 1;
  user-select: none;
  transition: background .12s, color .12s;
  z-index: 2;
}
.panel-handle:hover { background: var(--surface-2); color: var(--accent); }

/* ── Sidebar ──────────────────────────────────────────────────── */
aside {
  width: var(--sidebar-w);
  flex-shrink: 0;
  background: var(--surface);
  border-right: 1px solid var(--border);
  overflow-y: auto;
  padding: 16px 0 32px;
  transition: width .22s ease;
}
.sidebar-section { margin-bottom: 24px; }
.sidebar-label {
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: .1em;
  text-transform: uppercase;
  color: var(--text-3);
  padding: 0 16px;
  margin-bottom: 6px;
  display: block;
}
.folder-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  width: 100%;
  padding: 5px 16px;
  background: none;
  border: none;
  color: var(--text-2);
  font-family: var(--sans);
  font-size: 13px;
  cursor: pointer;
  text-align: left;
  transition: background .12s, color .12s;
}
.folder-btn:hover { background: var(--surface-2); color: var(--text-1); }
.folder-btn.active { background: var(--accent-bg); color: var(--text-1); }
.folder-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  flex-shrink: 0;
}
.folder-count {
  margin-left: auto;
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text-3);
  font-variant-numeric: tabular-nums;
}
.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 0 12px;
}
.tag-chip {
  font-size: 11px;
  font-family: var(--mono);
  padding: 2px 7px;
  border-radius: 99px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  color: var(--text-2);
  cursor: pointer;
  transition: background .12s, color .12s, border-color .12s;
  white-space: nowrap;
}
.tag-chip:hover { border-color: var(--accent); color: var(--text-1); }
.tag-chip.active { background: var(--accent-bg); border-color: var(--accent); color: var(--accent); }

/* ── Type filters ─────────────────────────────────────────────── */
.type-filters {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
  padding: 0 12px;
}
.type-chip {
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 99px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  color: var(--text-2);
  cursor: pointer;
  transition: background .12s, color .12s, border-color .12s;
  white-space: nowrap;
}
.type-chip:hover { border-color: var(--accent); color: var(--text-1); }
.type-chip.active { background: var(--accent-bg); border-color: var(--accent); color: var(--accent); }


/* ── Main area (split) ────────────────────────────────────────── */
main {
  flex: 1;
  display: flex;
  min-height: 0;
  overflow: hidden;
}

.list-panel {
  width: 400px;
  flex-shrink: 0;
  overflow-y: auto;
  padding: 20px 16px 40px 24px;
  border-right: 1px solid var(--border);
  transition: width .22s ease;
}

/* ── Note feed ────────────────────────────────────────────────── */
.empty-state {
  color: var(--text-3);
  font-family: var(--mono);
  font-size: 13px;
  padding: 60px 0;
  text-align: center;
}
.month-group { margin-bottom: 32px; }
.month-header {
  font-family: var(--mono);
  font-size: 11px;
  font-weight: 600;
  letter-spacing: .08em;
  text-transform: uppercase;
  color: var(--text-3);
  padding-bottom: 8px;
  border-bottom: 1px solid var(--border);
  margin-bottom: 2px;
  font-variant-numeric: tabular-nums;
}
.note-row {
  display: grid;
  grid-template-columns: 76px 1fr auto;
  gap: 0 10px;
  align-items: center;
  padding: 7px 8px;
  border-radius: var(--radius);
  transition: background .1s;
  cursor: pointer;
  border-left: 3px solid transparent;
}
.note-row:hover { background: var(--surface-2); }
.note-row.kb-selected { outline: 2px solid var(--accent); outline-offset: -2px; }
.note-row.active {
  background: var(--accent-bg);
  border-left-color: var(--accent);
}
.note-date {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text-3);
  font-variant-numeric: tabular-nums;
  white-space: nowrap;
}
.note-title {
  font-size: 13px;
  color: var(--text-1);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.note-updated {
  font-family: var(--mono);
  font-size: 10px;
  color: var(--accent);
  margin-left: 6px;
}
.note-snippet {
  display: block;
  font-size: 11px;
  color: var(--text-3);
  margin-top: 2px;
  line-height: 1.4;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}
.note-snippet mark {
  background: var(--accent-bg);
  color: var(--accent);
  border-radius: 2px;
  padding: 0 2px;
  font-weight: 600;
}
.note-meta {
  display: flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}
.badge {
  font-size: 10px;
  font-family: var(--mono);
  padding: 1px 6px;
  border-radius: 4px;
  white-space: nowrap;
  opacity: .85;
}
.badge-folder { border: 1px solid; }
.badge-type {
  background: var(--surface-2);
  color: var(--text-2);
  border: 1px solid var(--border);
}

/* ── Timeline bar ─────────────────────────────────────────────── */
.timeline-bar {
  background: var(--surface);
  border-bottom: 1px solid var(--border);
  padding: 7px 20px;
  display: flex;
  align-items: center;
  gap: 5px;
  overflow-x: auto;
  flex-shrink: 0;
}
.timeline-bar::-webkit-scrollbar { height: 3px; }
.tl-label {
  font-family: var(--mono);
  font-size: 10px;
  font-weight: 600;
  letter-spacing: .1em;
  text-transform: uppercase;
  color: var(--text-3);
  white-space: nowrap;
  padding-right: 8px;
  border-right: 1px solid var(--border);
  margin-right: 4px;
}
.month-pill {
  font-family: var(--mono);
  font-size: 11px;
  padding: 2px 8px;
  border-radius: 4px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  color: var(--text-2);
  cursor: pointer;
  white-space: nowrap;
  transition: border-color .12s, color .12s;
  display: flex;
  align-items: center;
  gap: 5px;
}
.month-pill:hover { border-color: var(--accent); color: var(--text-1); }
.month-pill.active { border-color: var(--accent); color: var(--accent); background: var(--accent-bg); }
.mpill-count { color: var(--text-3); font-size: 10px; }

/* ── Detail panel ─────────────────────────────────────────────── */
.detail-panel {
  flex: 1;
  overflow-y: auto;
  background: var(--bg);
  display: flex;
  flex-direction: column;
}

.detail-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-3);
  font-family: var(--mono);
  font-size: 13px;
  gap: 8px;
}

.detail-inner {
  padding: 28px 36px 60px;
  max-width: 960px;
  width: 100%;
}
.detail-body-wrap {
  display: flex;
  gap: 28px;
  align-items: flex-start;
}
.detail-body-wrap .note-body { flex: 1; min-width: 0; }
.outline-panel {
  width: 152px;
  flex-shrink: 0;
  position: sticky;
  top: 20px;
  font-size: 11px;
}
.outline-label {
  font-size: 10px;
  font-weight: 600;
  letter-spacing: .07em;
  text-transform: uppercase;
  color: var(--text-3);
  margin-bottom: 8px;
}
.outline-item {
  display: block;
  padding: 3px 0 3px 8px;
  color: var(--text-3);
  cursor: pointer;
  border-left: 2px solid var(--border);
  line-height: 1.4;
  transition: color .1s, border-color .1s;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.outline-item:hover { color: var(--text-1); border-left-color: var(--accent); }
.outline-item.h1 { padding-left: 8px; font-weight: 600; }
.outline-item.h2 { padding-left: 8px; }
.outline-item.h3 { padding-left: 18px; font-size: 10.5px; }
.outline-item.h4 { padding-left: 28px; font-size: 10px; color: var(--text-3); }

.detail-header {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 12px;
}
.detail-folder-select {
  font-size: 11px; font-family: var(--sans);
  background: var(--surface-2,var(--bg)); border: 1px solid var(--border);
  border-radius: 5px; color: var(--text-2); padding: 3px 6px;
  cursor: pointer; outline: none; max-width: 160px;
}
.detail-folder-select:hover { border-color: var(--accent); }
.detail-title {
  font-size: 22px;
  font-weight: 700;
  line-height: 1.3;
  color: var(--text-1);
  text-wrap: balance;
}
.detail-close {
  background: none;
  border: 1px solid var(--border);
  border-radius: var(--radius);
  color: var(--text-3);
  cursor: pointer;
  padding: 4px 8px;
  font-size: 13px;
  flex-shrink: 0;
  line-height: 1;
  transition: border-color .12s, color .12s;
}
.detail-close:hover { border-color: var(--accent); color: var(--text-1); }
.detail-star { color: var(--text-3); }
.detail-star.starred { color: #fbbf24; border-color: rgba(251,191,36,.4); }
.detail-star.starred:hover { border-color: #fbbf24; }

/* ── Starred sidebar section ──────────────────────────────────── */
#starred-section { display: none; }
#starred-section.has-items { display: block; }
.starred-item {
  display: flex; align-items: center; gap: 8px;
  padding: 5px 6px; border-radius: var(--radius);
  cursor: pointer; transition: background .1s;
  font-size: 12px; color: var(--text-2);
}
.starred-item:hover { background: var(--surface-2); color: var(--text-1); }
.starred-item-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.starred-item-title { flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }

.detail-chips {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  padding-bottom: 20px;
  margin-bottom: 24px;
  border-bottom: 1px solid var(--border);
}
.chip {
  font-size: 11px;
  font-family: var(--mono);
  padding: 2px 8px;
  border-radius: 4px;
  border: 1px solid var(--border);
  background: var(--surface-2);
  color: var(--text-2);
}
.chip-accent { border-color: var(--accent); background: var(--accent-bg); color: var(--accent); }
.chip-folder { border: 1px solid; }

/* ── Rendered markdown ────────────────────────────────────────── */
.note-body {
  color: var(--text-1);
  line-height: 1.7;
  font-size: 14px;
}

/* ── Link suggestions panel ─────────────────────────────────── */
.link-suggest-panel {
  background: var(--surface-2);
  border: 1px solid var(--accent);
  border-radius: 8px;
  margin-bottom: 20px;
  overflow: hidden;
}
.link-suggest-header {
  display: flex; align-items: center; gap: 8px;
  padding: 10px 14px;
  background: var(--surface-3);
  border-bottom: 1px solid var(--border);
}
.link-suggest-title {
  font-size: 12px; font-weight: 600; color: var(--accent);
  flex: 1; letter-spacing: .02em;
}
.link-suggest-close {
  background: none; border: none; color: var(--text-3);
  cursor: pointer; font-size: 14px; padding: 0 2px; line-height: 1;
}
.link-suggest-close:hover { color: var(--text-1); }
.link-suggest-list {
  padding: 8px 0;
  max-height: 220px;
  overflow-y: auto;
}
.link-suggest-item {
  display: flex; align-items: center; gap: 10px;
  padding: 7px 14px;
  cursor: pointer;
  transition: background .1s;
}
.link-suggest-item:hover { background: var(--surface-3); }
.link-suggest-item input[type=checkbox] { flex-shrink: 0; accent-color: var(--accent); cursor: pointer; }
.link-suggest-dot { width: 6px; height: 6px; border-radius: 50%; flex-shrink: 0; }
.link-suggest-name { font-size: 13px; color: var(--text-1); flex: 1;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.link-suggest-folder { font-size: 10px; color: var(--text-3); white-space: nowrap; }
.link-suggest-score {
  font-size: 10px; color: var(--text-3);
  background: var(--surface-1); border-radius: 4px; padding: 1px 5px;
  white-space: nowrap;
}
.link-suggest-footer {
  padding: 8px 14px;
  border-top: 1px solid var(--border);
  display: flex; align-items: center; gap: 8px;
}
.link-suggest-apply {
  background: var(--accent); border: none; border-radius: 6px;
  color: #fff; cursor: pointer; font-size: 12px; font-weight: 600;
  padding: 5px 12px; font-family: var(--sans);
  transition: opacity .15s;
}
.link-suggest-apply:hover { opacity: .85; }
.link-suggest-apply:disabled { opacity: .4; cursor: not-allowed; }
.link-suggest-hint { font-size: 11px; color: var(--text-3); }

/* ── Backlinks ──────────────────────────────────────────────── */
.backlinks-section {
  margin-top: 40px;
  padding-top: 18px;
  border-top: 1px solid var(--border);
}
.backlinks-label {
  font-size: 11px;
  font-weight: 600;
  color: var(--text-3);
  letter-spacing: .06em;
  text-transform: uppercase;
  margin-bottom: 10px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.backlinks-label::after {
  content: '';
  flex: 1;
  height: 1px;
  background: var(--border);
}
.backlinks-list {
  display: flex;
  flex-direction: column;
  gap: 5px;
}
.backlink-chip {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 6px 10px;
  cursor: pointer;
  text-align: left;
  width: 100%;
  transition: border-color .15s, background .15s;
  font-family: var(--sans);
}
.backlink-chip:hover {
  border-color: var(--accent);
  background: var(--surface-3);
}
.backlink-dot {
  width: 6px; height: 6px;
  border-radius: 50%;
  flex-shrink: 0;
}
.backlink-title {
  font-size: 13px;
  color: var(--text-1);
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.backlink-folder {
  font-size: 10px;
  color: var(--text-3);
  white-space: nowrap;
}
.backlinks-empty {
  font-size: 12px;
  color: var(--text-3);
  font-style: italic;
}
.related-loading {
  display: flex; align-items: center; gap: 7px;
  font-style: normal;
}
.note-body h1, .note-body h2 {
  font-size: 18px;
  font-weight: 700;
  margin: 28px 0 10px;
  color: var(--text-1);
  padding-bottom: 6px;
  border-bottom: 1px solid var(--border);
}
.note-body h3 {
  font-size: 15px;
  font-weight: 700;
  margin: 22px 0 8px;
  color: var(--text-1);
}
.note-body h4 {
  font-size: 13px;
  font-weight: 700;
  margin: 18px 0 6px;
  color: var(--text-2);
  text-transform: uppercase;
  letter-spacing: .06em;
}
.note-body p { margin: 0 0 14px; }
.note-body p:last-child { margin-bottom: 0; }
.note-body ul, .note-body ol {
  margin: 8px 0 14px 20px;
}
.note-body li { margin-bottom: 4px; }
.note-body li ul, .note-body li ol { margin-top: 4px; margin-bottom: 4px; }
.note-body blockquote {
  border-left: 3px solid var(--accent);
  padding: 8px 16px;
  margin: 14px 0;
  color: var(--text-2);
  background: var(--surface);
  border-radius: 0 4px 4px 0;
  font-style: italic;
}
.note-body code {
  font-family: var(--mono);
  font-size: 12px;
  background: var(--surface-2);
  border: 1px solid var(--border);
  padding: 1px 5px;
  border-radius: 3px;
  color: #7DD3FC;
}
.note-body pre {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 14px 16px;
  overflow-x: auto;
  margin: 14px 0;
}
.note-body pre code {
  background: none;
  border: none;
  padding: 0;
  color: var(--text-1);
  font-size: 12px;
  line-height: 1.6;
}
.note-body hr {
  border: none;
  border-top: 1px solid var(--border);
  margin: 24px 0;
}
.note-body table {
  width: 100%;
  border-collapse: collapse;
  margin: 14px 0;
  font-size: 13px;
  overflow-x: auto;
  display: block;
}
.note-body th {
  text-align: left;
  padding: 7px 12px;
  background: var(--surface);
  border: 1px solid var(--border);
  font-weight: 600;
  font-size: 12px;
  color: var(--text-2);
}
.note-body td {
  padding: 6px 12px;
  border: 1px solid var(--border);
  vertical-align: top;
}
.note-body tr:hover td { background: var(--surface-2); }
.note-body strong { font-weight: 700; color: var(--text-1); }
.note-body em { color: var(--text-2); font-style: italic; }
.note-body a { color: var(--accent); text-decoration: underline; text-underline-offset: 2px; }
.note-body a:hover { opacity: .8; }
.note-body img { max-width: 100%; border-radius: 4px; margin: 8px 0; display: block; }
.note-body .mermaid { background: var(--surface); border: 1px solid var(--border); border-radius: 6px; padding: 16px; margin: 14px 0; overflow-x: auto; text-align: center; }
.note-body .mermaid svg { max-width: 100%; height: auto; }

/* ── Wikilinks ────────────────────────────────────────────────── */
.wikilink {
  color: #34C88A;
  text-decoration: none;
  border-bottom: 1px dashed #34C88A66;
  padding-bottom: 1px;
  cursor: pointer;
}
.wikilink:hover { border-bottom-style: solid; opacity: .85; }
.wikilink-missing {
  color: var(--text-3);
  border-bottom: 1px dashed var(--text-3);
  padding-bottom: 1px;
  cursor: default;
}

/* ── Chat panel ───────────────────────────────────────────────── */
#chat-btn.active {
  background: #7C3AED22;
  border-color: #7C3AED;
  color: #A78BFA;
}
#chat-btn.offline { opacity: .4; cursor: not-allowed; }

.chat-overlay {
  position: fixed; inset: 0;
  z-index: 90;
  display: flex;
  pointer-events: none;
}
.chat-overlay.open { pointer-events: all; }
.chat-backdrop {
  flex: 1;
  background: rgba(0,0,0,.35);
  cursor: pointer;
  opacity: 0;
  transition: opacity .25s;
}
.chat-overlay.open .chat-backdrop { opacity: 1; }

.chat-panel {
  width: 480px;
  max-width: 95vw;
  background: var(--surface);
  border-left: 1px solid var(--border);
  display: flex;
  flex-direction: column;
  transform: translateX(100%);
  transition: transform .25s cubic-bezier(.4,0,.2,1);
  box-shadow: -12px 0 40px rgba(0,0,0,.4);
}
.chat-overlay.open .chat-panel { transform: translateX(0); }

.chat-header {
  display: flex; align-items: center; gap: 10px;
  padding: 14px 16px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.chat-title {
  font-size: 14px; font-weight: 700; color: var(--text-1); flex: 1;
}
.chat-subtitle {
  font-size: 11px; font-family: var(--mono); color: var(--text-3);
}
.chat-clear {
  background: none; border: 1px solid var(--border); border-radius: var(--radius);
  color: var(--text-3); cursor: pointer; font-size: 11px; font-family: var(--mono);
  padding: 3px 8px; transition: border-color .12s, color .12s;
}
.chat-clear:hover { border-color: var(--text-2); color: var(--text-2); }
.chat-close {
  background: none; border: 1px solid var(--border); border-radius: var(--radius);
  color: var(--text-3); cursor: pointer; font-size: 13px; padding: 4px 8px; line-height: 1;
  transition: border-color .12s, color .12s;
}
.chat-close:hover { border-color: var(--text-1); color: var(--text-1); }

.chat-messages {
  flex: 1; overflow-y: auto;
  padding: 16px 16px 8px;
  display: flex; flex-direction: column; gap: 20px;
}

.chat-empty {
  display: flex; flex-direction: column; align-items: center; justify-content: center;
  flex: 1; gap: 12px; padding: 32px 16px;
  color: var(--text-3); text-align: center;
}
.chat-empty-icon { font-size: 32px; line-height: 1; }
.chat-empty-title { font-size: 15px; font-weight: 700; color: var(--text-2); }
.chat-empty-hints { font-size: 12px; line-height: 1.8; }
.chat-hint-chip {
  display: inline-block; background: var(--surface-2); border: 1px solid var(--border);
  border-radius: 4px; padding: 2px 8px; margin: 2px; cursor: pointer;
  font-family: var(--mono); font-size: 11px; color: var(--text-2);
  transition: border-color .12s, color .12s;
}
.chat-hint-chip:hover { border-color: #A78BFA; color: #A78BFA; }

.chat-turn { display: flex; flex-direction: column; gap: 8px; }

.chat-user {
  align-self: flex-end;
  max-width: 85%;
  background: #7C3AED22;
  border: 1px solid #7C3AED44;
  border-radius: 12px 12px 3px 12px;
  padding: 10px 14px;
  font-size: 13px; color: var(--text-1); line-height: 1.55;
}

.chat-assistant {
  align-self: flex-start;
  max-width: 100%;
  font-size: 13px; color: var(--text-1); line-height: 1.7;
}
.chat-assistant-inner {
  background: var(--surface-2); border: 1px solid var(--border);
  border-radius: 3px 12px 12px 12px;
  padding: 12px 16px; margin-bottom: 8px;
}
.chat-assistant-inner p { margin: 0 0 10px; }
.chat-assistant-inner p:last-child { margin-bottom: 0; }
.chat-assistant-inner strong { color: var(--text-1); font-weight: 700; }
.chat-assistant-inner em { color: var(--text-2); font-style: italic; }
.chat-assistant-inner code {
  font-family: var(--mono); font-size: 11.5px;
  background: var(--surface); border: 1px solid var(--border);
  padding: 1px 4px; border-radius: 3px; color: #7DD3FC;
}
.chat-assistant-inner ul, .chat-assistant-inner ol {
  margin: 4px 0 10px 18px;
}
.chat-assistant-inner li { margin-bottom: 3px; }
.chat-cite {
  display: inline-block; font-family: var(--mono); font-size: 10px;
  background: rgba(167,139,250,.15); border: 1px solid rgba(167,139,250,.3);
  color: #A78BFA; border-radius: 3px; padding: 0 4px;
  cursor: pointer; margin: 0 1px;
  transition: background .12s;
}
.chat-cite:hover { background: rgba(167,139,250,.3); }

.chat-sources {
  display: flex; flex-wrap: wrap; gap: 5px;
}
.chat-source-chip {
  display: flex; align-items: center; gap: 5px;
  background: var(--surface); border: 1px solid var(--border);
  border-radius: 4px; padding: 4px 8px;
  font-size: 11px; font-family: var(--mono);
  color: var(--text-2); cursor: pointer;
  transition: border-color .12s, color .12s;
  max-width: 200px;
}
.chat-source-chip:hover { border-color: #A78BFA; color: #A78BFA; }
.chat-source-dot {
  width: 5px; height: 5px; border-radius: 50%;
  background: #A78BFA; flex-shrink: 0;
}
.chat-source-title {
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.chat-source-score {
  color: var(--text-3); font-size: 10px; flex-shrink: 0;
}

.chat-thinking {
  display: flex; gap: 5px; align-items: center; padding: 4px 0;
}
.chat-thinking span {
  width: 6px; height: 6px; border-radius: 50%;
  background: var(--text-3); display: inline-block;
  animation: thinking .9s ease-in-out infinite;
}
.chat-thinking span:nth-child(2) { animation-delay: .15s; }
.chat-thinking span:nth-child(3) { animation-delay: .30s; }
@keyframes thinking {
  0%, 60%, 100% { transform: translateY(0); opacity: .4; }
  30% { transform: translateY(-5px); opacity: 1; }
}

.chat-input-area {
  padding: 12px 14px 16px;
  border-top: 1px solid var(--border);
  flex-shrink: 0;
}
.chat-input-row {
  display: flex; gap: 8px; align-items: flex-end;
}
.chat-textarea {
  flex: 1; resize: none; border: 1px solid var(--border);
  border-radius: 8px; background: var(--bg); color: var(--text-1);
  font-family: var(--sans); font-size: 13px; line-height: 1.5;
  padding: 9px 12px; outline: none;
  transition: border-color .15s;
  min-height: 40px; max-height: 120px; overflow-y: auto;
}
.chat-textarea:focus { border-color: #7C3AED; }
.chat-textarea::placeholder { color: var(--text-3); }
.chat-send {
  background: #7C3AED; border: none; border-radius: 8px;
  color: #fff; cursor: pointer; font-size: 16px; line-height: 1;
  padding: 9px 14px; transition: opacity .15s; flex-shrink: 0;
  align-self: flex-end;
}
.chat-send:hover { opacity: .85; }
.chat-send:disabled { opacity: .4; cursor: default; }
.chat-hint-text {
  font-size: 10px; color: var(--text-3); font-family: var(--mono);
  margin-top: 6px; text-align: right;
}

/* ── Semantic search ──────────────────────────────────────────── */
#semantic-btn.active {
  background: var(--accent-bg);
  border-color: var(--accent);
  color: var(--accent);
}
#semantic-btn.offline { opacity: .4; cursor: not-allowed; }
.semantic-score {
  font-family: var(--mono);
  font-size: 10px;
  color: var(--text-3);
  margin-left: auto;
  flex-shrink: 0;
}
.semantic-bar {
  height: 2px;
  background: var(--accent);
  border-radius: 1px;
  margin-top: 2px;
  opacity: .5;
  transition: width .2s;
}
.semantic-notice {
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text-3);
  padding: 6px 8px 2px;
  display: flex;
  align-items: center;
  gap: 6px;
}
.semantic-spinner {
  display: inline-block;
  width: 10px; height: 10px;
  border: 2px solid var(--border);
  border-top-color: var(--accent);
  border-radius: 50%;
  animation: spin .6s linear infinite;
}
@keyframes spin { to { transform: rotate(360deg); } }

/* ── Capture button (header) ──────────────────────────────────── */
.capture-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--accent);
  border: none;
  border-radius: var(--radius);
  color: #fff;
  cursor: pointer;
  font-family: var(--sans);
  font-size: 12px;
  font-weight: 600;
  padding: 5px 12px;
  line-height: 1;
  transition: opacity .15s;
  white-space: nowrap;
}
.capture-btn:hover { opacity: .85; }
.capture-btn.offline { background: var(--surface-2); color: var(--text-3); border: 1px solid var(--border); cursor: not-allowed; }

/* ── Graph overlay ──────────────────────────────────────────────── */
.graph-overlay {
  position: fixed; inset: 0;
  background: #080810;
  z-index: 200;
  display: none;
  flex-direction: column;
  font-family: var(--sans);
}
.graph-overlay.open { display: flex; }
.graph-toolbar {
  display: flex; align-items: center; gap: 8px;
  padding: 8px 14px;
  background: rgba(0,0,0,.55);
  border-bottom: 1px solid rgba(255,255,255,.07);
  flex-shrink: 0;
}
.graph-title { font-size: 13px; font-weight: 600; color: #e5e7eb; letter-spacing: .02em; }
.graph-subtitle { font-size: 11px; color: #6b7280; margin-left: 8px; margin-right: auto; }
.graph-ctrl {
  background: rgba(255,255,255,.07);
  border: 1px solid rgba(255,255,255,.1);
  border-radius: 6px; color: #d1d5db;
  cursor: pointer; font-size: 12px; padding: 4px 10px;
  transition: background .15s; font-family: var(--sans);
}
.graph-ctrl:hover { background: rgba(255,255,255,.15); }
.graph-canvas-wrap { flex: 1; position: relative; overflow: hidden; }
#graph-canvas { display: block; width: 100%; height: 100%; cursor: grab; }
#graph-canvas.grabbing { cursor: grabbing; }
.graph-legend {
  position: absolute; top: 12px; left: 12px;
  background: rgba(8,8,20,.82);
  border: 1px solid rgba(255,255,255,.08);
  border-radius: 8px; padding: 8px 12px;
  display: flex; flex-direction: column; gap: 3px;
  user-select: none;
}
.graph-legend-item {
  display: flex; align-items: center; gap: 7px;
  font-size: 10px; color: #9ca3af; cursor: pointer;
  padding: 2px 3px; border-radius: 4px;
  transition: color .15s, opacity .15s;
}
.graph-legend-item:hover { color: #e5e7eb; }
.graph-legend-item.dimmed { opacity: .3; }
.graph-legend-dot { width: 8px; height: 8px; border-radius: 50%; flex-shrink: 0; }
.graph-hint {
  position: absolute; bottom: 12px; right: 14px;
  font-size: 10px; color: rgba(255,255,255,.2);
  pointer-events: none; line-height: 1.7; text-align: right;
}
.graph-tooltip {
  position: absolute;
  background: rgba(12,12,24,.96);
  border: 1px solid rgba(255,255,255,.12);
  border-radius: 6px; padding: 5px 10px;
  font-size: 11px; color: #e5e7eb;
  pointer-events: none; white-space: nowrap;
  max-width: 280px; overflow: hidden; text-overflow: ellipsis;
  display: none; box-shadow: 0 4px 14px rgba(0,0,0,.55);
}

/* ── Kanban overlay ─────────────────────────────────────────────── */
.kanban-overlay {
  position: fixed; inset: 0; z-index: 200;
  background: var(--bg); display: none; flex-direction: column;
}
.kanban-overlay.open { display: flex; }
.kanban-topbar {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 16px; border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.kanban-topbar-title { font-size: 14px; font-weight: 700; color: var(--text-1); margin-right: auto; }
.kanban-body { display: flex; flex: 1; overflow: hidden; }
.kanban-sidebar {
  width: 220px; flex-shrink: 0; border-right: 1px solid var(--border);
  overflow-y: auto; padding: 12px 8px; display: flex; flex-direction: column; gap: 4px;
}
.kanban-proj-item {
  padding: 8px 10px; border-radius: var(--radius); cursor: pointer;
  font-size: 13px; color: var(--text-2); transition: background .1s;
  border: 1px solid transparent;
}
.kanban-proj-item:hover { background: var(--surface-2); color: var(--text-1); }
.kanban-proj-item.active { background: var(--accent-bg); border-color: var(--accent); color: var(--text-1); font-weight: 600; }
.kanban-proj-status { font-size: 10px; color: var(--text-3); margin-top: 2px; }
.kanban-board {
  flex: 1; display: grid; grid-template-columns: repeat(3, 1fr);
  gap: 16px; padding: 16px; overflow-y: auto; align-items: start;
}
.kanban-col { background: var(--surface); border: 1px solid var(--border); border-radius: 8px; display: flex; flex-direction: column; }
.kanban-col-header {
  padding: 10px 14px; font-size: 12px; font-weight: 700; letter-spacing: .06em;
  text-transform: uppercase; color: var(--text-2); border-bottom: 1px solid var(--border);
  display: flex; align-items: center; justify-content: space-between;
}
.kanban-col-count { font-size: 11px; background: var(--surface-2); border-radius: 10px; padding: 1px 7px; font-weight: 600; }
.kanban-cards { padding: 8px; display: flex; flex-direction: column; gap: 6px; min-height: 80px; }
.kanban-card {
  background: var(--bg); border: 1px solid var(--border); border-radius: 6px;
  padding: 9px 11px; cursor: pointer; transition: border-color .15s, box-shadow .15s;
  font-size: 13px; color: var(--text-1); line-height: 1.4;
}
.kanban-card:hover { border-color: var(--accent); box-shadow: 0 2px 8px rgba(0,0,0,.15); }
.kanban-card.done-card { opacity: .6; text-decoration: line-through; color: var(--text-3); }
.kanban-card-note { font-size: 10px; color: var(--accent); margin-top: 4px; }
.kanban-add-task {
  margin: 6px 8px 8px; padding: 6px 10px; font-size: 12px; color: var(--text-3);
  background: none; border: 1px dashed var(--border); border-radius: 6px;
  cursor: pointer; text-align: left; transition: border-color .15s, color .15s;
}
.kanban-add-task:hover { border-color: var(--accent); color: var(--accent); }
.kanban-empty { padding: 20px; text-align: center; color: var(--text-3); font-size: 12px; }
.kanban-new-proj {
  margin: 8px; padding: 7px 10px; font-size: 12px; color: var(--accent);
  background: none; border: 1px dashed var(--border); border-radius: 6px; cursor: pointer;
}
.kanban-new-proj:hover { background: var(--accent-bg); }
/* move buttons on card hover */
.kanban-card-actions { display: none; gap: 4px; margin-top: 6px; }
.kanban-card:hover .kanban-card-actions { display: flex; }
.kanban-move-btn {
  font-size: 10px; padding: 2px 6px; border-radius: 4px; border: 1px solid var(--border);
  background: var(--surface); color: var(--text-2); cursor: pointer;
}
.kanban-move-btn:hover { background: var(--accent-bg); color: var(--accent); }

/* ── Quick capture modal ────────────────────────────────────────── */
.qc-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,.5);
  z-index: 150;
  display: none;
  align-items: center;
  justify-content: center;
  padding: 20px;
}
.qc-overlay.open { display: flex; }
.qc-panel {
  background: var(--surface-1);
  border: 1px solid var(--border);
  border-radius: 12px;
  width: 100%; max-width: 660px;
  display: flex; flex-direction: column;
  box-shadow: 0 20px 60px rgba(0,0,0,.35);
  max-height: 88vh;
  overflow: hidden;
}
.qc-header {
  display: flex; align-items: center; gap: 10px;
  padding: 14px 18px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.qc-label { font-size: 12px; font-weight: 600; color: var(--text-3); white-space: nowrap; }
.qc-title-input {
  flex: 1; background: none; border: none; outline: none;
  font-size: 15px; font-weight: 600;
  color: var(--text-1); font-family: var(--sans);
}
.qc-title-input::placeholder { color: var(--text-3); font-weight: 400; font-size: 14px; }
.qc-close { background: none; border: none; color: var(--text-3); cursor: pointer; font-size: 18px; line-height: 1; padding: 0 2px; }
.qc-close:hover { color: var(--text-1); }
.qc-body-wrap { flex: 1; overflow-y: auto; padding: 16px 18px; }
.qc-textarea {
  width: 100%; height: 300px;
  background: none; border: none; outline: none;
  font-size: 13px; line-height: 1.75;
  color: var(--text-1); font-family: var(--mono);
  resize: none; box-sizing: border-box;
}
.qc-textarea::placeholder { color: var(--text-3); font-family: var(--sans); font-size: 14px; line-height: 1.7; }
.qc-footer {
  display: flex; align-items: center; gap: 10px;
  padding: 10px 18px;
  border-top: 1px solid var(--border);
  flex-shrink: 0;
}
.qc-folder-row { display: flex; align-items: center; gap: 8px; padding: 8px 18px 0; flex-shrink: 0; }
.qc-folder-label { font-size: 11px; color: var(--text-3); white-space: nowrap; }
.qc-folder-select {
  flex: 1; background: var(--surface-2); border: 1px solid var(--border);
  border-radius: 6px; color: var(--text-1); font-size: 12px;
  font-family: var(--sans); padding: 4px 8px; cursor: pointer; outline: none;
}
.qc-tpl-row {
  display: flex; align-items: center; gap: 6px;
  padding: 8px 18px 0; flex-shrink: 0;
  overflow-x: auto;
}
.qc-tpl-row::-webkit-scrollbar { height: 0; }
.qc-tpl-label { font-size: 11px; color: var(--text-3); white-space: nowrap; flex-shrink: 0; }
.tpl-chip {
  display: flex; align-items: center; gap: 4px;
  font-size: 11px; white-space: nowrap;
  padding: 3px 9px; border-radius: 99px;
  background: var(--surface-2); border: 1px solid var(--border);
  color: var(--text-2); cursor: pointer; flex-shrink: 0;
  transition: border-color .12s, color .12s, background .12s;
}
.tpl-chip:hover { border-color: var(--accent); color: var(--text-1); }
.tpl-chip.active { background: var(--accent-bg); border-color: var(--accent); color: var(--accent); }
.qc-hint { font-size: 11px; color: var(--text-3); flex: 1; }
.qc-status { font-size: 12px; color: var(--text-3); }
.qc-status.ok  { color: #34d399; }
.qc-status.err { color: #f87171; }

/* ── Duplicate warning ─────────────────────────────────────────── */
.qc-dup-panel {
  margin: 8px 18px 0; flex-shrink: 0;
  border: 1px solid var(--border); border-radius: 8px;
  overflow: hidden; display: none;
  background: var(--surface-2);
}
.qc-dup-panel.show { display: block; }
.qc-dup-header {
  display: flex; align-items: center; gap: 7px;
  padding: 7px 12px;
  font-size: 12px; font-weight: 600;
  border-bottom: 1px solid var(--border);
}
.qc-dup-header.warn { color: #fbbf24; }
.qc-dup-header.info { color: var(--text-3); }
.qc-dup-item {
  display: flex; align-items: center; gap: 8px;
  padding: 7px 12px; border-bottom: 1px solid var(--border);
  font-size: 12px;
}
.qc-dup-item:last-child { border-bottom: none; }
.qc-dup-title { flex: 1; color: var(--text-1); overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.qc-dup-score { font-family: var(--mono); font-size: 10px; color: var(--text-3); flex-shrink: 0; }
.qc-dup-open {
  background: none; border: 1px solid var(--border); border-radius: 4px;
  color: var(--text-2); cursor: pointer; font-size: 11px;
  padding: 2px 8px; flex-shrink: 0; white-space: nowrap;
  transition: border-color .12s, color .12s; font-family: var(--sans);
}
.qc-dup-open:hover { border-color: var(--accent); color: var(--accent); }
.qc-save {
  background: var(--accent); border: none; border-radius: 6px;
  color: #fff; cursor: pointer; font-size: 13px; font-weight: 600;
  padding: 7px 16px; font-family: var(--sans); transition: opacity .15s;
}
.qc-save:hover { opacity: .85; }
.qc-save:disabled { opacity: .4; cursor: not-allowed; }

/* ── URL import modal ─────────────────────────────────────────── */
.url-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.5); z-index: 150; display: none; align-items: center; justify-content: center; padding: 20px; }
.url-overlay.open { display: flex; }
.url-panel { background: var(--surface-1,var(--surface)); border: 1px solid var(--border); border-radius: 12px; width: 100%; max-width: 560px; padding: 22px 24px; display: flex; flex-direction: column; gap: 14px; }
.url-header { display: flex; align-items: center; justify-content: space-between; }
.url-title { font-weight: 600; font-size: 15px; }
.url-close { background: none; border: none; color: var(--text-3); cursor: pointer; font-size: 18px; }
.url-close:hover { color: var(--text-1); }
.url-field { display: flex; flex-direction: column; gap: 5px; }
.url-label { font-size: 11px; color: var(--text-3); }
.url-input { background: var(--surface-2,var(--bg)); border: 1px solid var(--border); border-radius: 7px; color: var(--text-1); font-size: 13px; padding: 8px 12px; outline: none; font-family: var(--mono); }
.url-input:focus { border-color: var(--accent); }
.url-footer { display: flex; align-items: center; gap: 10px; }
.url-status { font-size: 12px; color: var(--text-3); flex: 1; }
.url-btn { background: var(--accent); border: none; border-radius: 6px; color: #fff; cursor: pointer; font-size: 13px; font-weight: 600; padding: 8px 18px; font-family: var(--sans); }
.url-btn:hover { opacity: .85; }
.url-btn:disabled { opacity: .4; cursor: not-allowed; }

/* ── Trash panel ──────────────────────────────────────────────── */
.trash-overlay { position: fixed; inset: 0; background: rgba(0,0,0,.5); z-index: 150; display: none; align-items: center; justify-content: center; padding: 20px; }
.trash-overlay.open { display: flex; }
.trash-panel { background: var(--surface-1,var(--surface)); border: 1px solid var(--border); border-radius: 12px; width: 100%; max-width: 600px; max-height: 80vh; display: flex; flex-direction: column; overflow: hidden; }
.trash-header { display: flex; align-items: center; gap: 10px; padding: 14px 18px; border-bottom: 1px solid var(--border); flex-shrink: 0; }
.trash-title { font-weight: 600; font-size: 15px; flex: 1; }
.trash-close { background: none; border: none; color: var(--text-3); cursor: pointer; font-size: 18px; padding: 0 2px; }
.trash-close:hover { color: var(--text-1); }
.trash-list { overflow-y: auto; flex: 1; }
.trash-empty { padding: 40px; text-align: center; color: var(--text-3); font-size: 13px; }
.trash-item { display: flex; align-items: center; gap: 10px; padding: 10px 18px; border-bottom: 1px solid var(--border); }
.trash-item:last-child { border-bottom: none; }
.trash-item-info { flex: 1; min-width: 0; }
.trash-item-title { font-size: 13px; font-weight: 500; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }
.trash-item-meta { font-size: 11px; color: var(--text-3); margin-top: 2px; }
.trash-btn { background: none; border: 1px solid var(--border); border-radius: 5px; cursor: pointer; font-size: 12px; padding: 3px 9px; color: var(--text-2); white-space: nowrap; }
.trash-btn:hover { background: var(--surface-2,var(--bg)); color: var(--text-1); }
.trash-btn.danger { color: #f87171; border-color: #f87171; }
.trash-btn.danger:hover { background: rgba(248,113,113,.1); }

/* ── Upload modal ─────────────────────────────────────────────── */
.modal-backdrop {
  position: fixed; inset: 0;
  background: rgba(0,0,0,.55);
  z-index: 100;
  display: flex; align-items: center; justify-content: center;
}
.modal {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 12px;
  padding: 28px 28px 24px;
  width: 420px;
  max-width: 95vw;
  box-shadow: 0 24px 64px rgba(0,0,0,.5);
}
.modal-title {
  font-size: 16px; font-weight: 700; color: var(--text-1); margin-bottom: 6px;
}
.modal-sub {
  font-size: 12px; color: var(--text-3); margin-bottom: 20px; font-family: var(--mono);
}
.drop-zone {
  border: 2px dashed var(--border);
  border-radius: 8px;
  padding: 28px 16px;
  text-align: center;
  cursor: pointer;
  transition: border-color .15s, background .15s;
  margin-bottom: 16px;
  position: relative;
}
.drop-zone:hover, .drop-zone.dragover {
  border-color: var(--accent);
  background: var(--accent-bg);
}
.drop-zone input[type=file] {
  position: absolute; inset: 0; opacity: 0; cursor: pointer; width: 100%; height: 100%;
}
.drop-icon { font-size: 28px; margin-bottom: 8px; }
.drop-label { font-size: 13px; color: var(--text-2); margin-bottom: 4px; }
.drop-hint  { font-size: 11px; color: var(--text-3); font-family: var(--mono); }
.camera-row {
  display: flex; gap: 8px; margin-bottom: 16px;
}
.camera-btn {
  flex: 1; display: flex; align-items: center; justify-content: center; gap: 6px;
  background: var(--surface-2); border: 1px solid var(--border); border-radius: var(--radius);
  color: var(--text-2); cursor: pointer; font-family: var(--sans); font-size: 12px; font-weight: 600;
  padding: 10px 12px; transition: border-color .12s, color .12s;
}
.camera-btn:hover { border-color: var(--accent); color: var(--text-1); }
.pipeline-log {
  background: var(--bg);
  border: 1px solid var(--border);
  border-radius: 6px;
  padding: 10px 12px;
  font-family: var(--mono);
  font-size: 11px;
  color: var(--text-2);
  max-height: 140px;
  overflow-y: auto;
  margin-bottom: 16px;
  display: none;
  line-height: 1.6;
}
.pipeline-log .log-done  { color: #4ADE80; }
.pipeline-log .log-error { color: #F87171; }
.modal-actions {
  display: flex; justify-content: flex-end; gap: 8px;
}
.btn-cancel {
  background: none; border: 1px solid var(--border); border-radius: var(--radius);
  color: var(--text-2); cursor: pointer; font-family: var(--sans); font-size: 13px;
  padding: 7px 16px; transition: border-color .12s, color .12s;
}
.btn-cancel:hover { border-color: var(--text-1); color: var(--text-1); }

/* ── Editor overlay ───────────────────────────────────────────── */
.editor-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,.6);
  z-index: 100;
  display: flex; align-items: stretch; justify-content: flex-end;
}
.editor-panel {
  width: 50vw; min-width: 480px; max-width: 820px;
  background: var(--surface);
  border-left: 1px solid var(--border);
  display: flex; flex-direction: column;
  box-shadow: -8px 0 32px rgba(0,0,0,.4);
}
.editor-header {
  display: flex; align-items: center; gap: 12px;
  padding: 12px 16px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.editor-title {
  font-size: 13px; font-weight: 600; color: var(--text-1);
  flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.editor-status {
  font-size: 11px; font-family: var(--mono); color: var(--text-3);
}
.editor-save {
  background: var(--accent); border: none; border-radius: var(--radius);
  color: #fff; cursor: pointer; font-family: var(--sans); font-size: 12px; font-weight: 600;
  padding: 5px 14px; transition: opacity .15s;
}
.editor-save:hover { opacity: .85; }
.editor-save:disabled { opacity: .45; cursor: default; }
.editor-close {
  background: none; border: 1px solid var(--border); border-radius: var(--radius);
  color: var(--text-3); cursor: pointer; font-size: 13px; padding: 4px 8px;
  transition: border-color .12s, color .12s; line-height: 1;
}
.editor-close:hover { border-color: var(--text-1); color: var(--text-1); }
.editor-textarea {
  flex: 1; resize: none; border: none; outline: none;
  background: var(--bg); color: var(--text-1);
  font-family: var(--mono); font-size: 12.5px; line-height: 1.7;
  padding: 20px 24px;
  overflow-y: auto;
}
.editor-textarea::placeholder { color: var(--text-3); }

/* ── Scrollbars ───────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }

@media (max-width: 800px) {
  .list-panel { width: 280px; }
  .detail-inner { padding: 20px 20px 40px; }
  .detail-title { font-size: 18px; }
}

/* ── Stats overlay ─────────────────────────────────────────────── */
.stats-overlay {
  position: fixed; inset: 0;
  background: rgba(0,0,0,.55);
  z-index: 150;
  display: none;
  align-items: flex-start;
  justify-content: center;
  padding: 36px 20px 60px;
  overflow-y: auto;
}
.stats-overlay.open { display: flex; }
.stats-panel {
  background: var(--surface);
  border: 1px solid var(--border);
  border-radius: 14px;
  width: 100%; max-width: 760px;
  display: flex; flex-direction: column;
  box-shadow: 0 24px 64px rgba(0,0,0,.45);
}
.stats-header {
  display: flex; align-items: center; gap: 10px;
  padding: 16px 22px;
  border-bottom: 1px solid var(--border);
  flex-shrink: 0;
}
.stats-title { font-size: 15px; font-weight: 700; flex: 1; }
.stats-close { background: none; border: none; color: var(--text-3); cursor: pointer; font-size: 18px; padding: 0 2px; }
.stats-close:hover { color: var(--text-1); }
.stats-body { padding: 22px; display: flex; flex-direction: column; gap: 26px; }
.stats-tiles { display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; }
.stats-tile {
  background: var(--surface-2); border: 1px solid var(--border);
  border-radius: 10px; padding: 14px 16px;
}
.stats-tile-val {
  font-size: 28px; font-weight: 800; color: var(--text-1);
  font-family: var(--mono); font-variant-numeric: tabular-nums; line-height: 1.1;
}
.stats-tile-lbl { font-size: 11px; color: var(--text-3); margin-top: 5px; }
.stats-tile.accent { border-color: var(--accent); background: var(--accent-bg); }
.stats-tile.accent .stats-tile-val { color: var(--accent); }
.stats-section-title {
  font-size: 10px; font-weight: 700; letter-spacing: .1em;
  text-transform: uppercase; color: var(--text-3);
  margin-bottom: 12px; font-family: var(--mono);
}
.stats-bar-row { display: flex; align-items: center; gap: 10px; margin-bottom: 8px; }
.stats-bar-label {
  font-size: 12px; color: var(--text-2);
  width: 140px; flex-shrink: 0;
  overflow: hidden; text-overflow: ellipsis; white-space: nowrap;
}
.stats-bar-track {
  flex: 1; height: 8px;
  background: var(--surface-2); border-radius: 4px; overflow: hidden;
}
.stats-bar-fill { height: 100%; border-radius: 4px; transition: width .4s ease; }
.stats-bar-count {
  font-size: 11px; font-family: var(--mono); color: var(--text-3);
  width: 30px; text-align: right; flex-shrink: 0;
  font-variant-numeric: tabular-nums;
}
.stats-activity { display: flex; align-items: flex-end; gap: 3px; height: 68px; }
.stats-act-col { display: flex; flex-direction: column; align-items: center; gap: 3px; flex: 1; min-width: 0; }
.stats-act-bar {
  width: 100%; border-radius: 2px 2px 0 0;
  background: var(--accent); opacity: .65;
  transition: opacity .15s;
}
.stats-act-bar:hover { opacity: 1; }
.stats-act-lbl {
  font-size: 7px; color: var(--text-3); font-family: var(--mono);
  white-space: nowrap; transform: rotate(-40deg) translateX(2px);
  transform-origin: top center; line-height: 1;
}
.stats-two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 28px; }
</style>
<script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script>
</head>
<body>

<header>
  <span class="logo">KB/</span>
  <span class="stat-pill" id="total-pill">── notes</span>
  <span class="stat-pill" id="date-pill">──</span>
  <div class="search-wrap">
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
      <circle cx="11" cy="11" r="8"/><path d="m21 21-4.35-4.35"/>
    </svg>
    <input id="search" type="search" placeholder="Buscar notas…" autocomplete="off">
  </div>
  <button class="theme-btn" onclick="openUrlImport()" title="Importar desde URL">🔗 URL</button>
  <button class="theme-btn" onclick="openTrash()" title="Papelera">🗑 Papelera</button>
  <button class="theme-btn" onclick="openQuickCapture()" title="Crear nota nueva rápido">✏️ Nueva</button>
  <button class="theme-btn" onclick="openStats()" title="Estadísticas del vault">📊 Stats</button>
  <button id="graph-btn" class="theme-btn" onclick="openGraph()" title="Grafo de conocimiento">⬡ Grafo</button>
  <button id="kanban-btn" class="theme-btn" onclick="openKanban()" title="Proyectos y tareas (Ctrl+P)">📋 Kanban</button>
  <button id="chat-btn" class="theme-btn" onclick="openChat()" title="Chat con tu vault (requiere servidor)">💬 Chat</button>
  <button id="semantic-btn" class="theme-btn" onclick="toggleSemantic()" title="Búsqueda semántica (requiere servidor)">⚡ Semántica</button>
  <button id="capture-btn" class="capture-btn offline" onclick="openCapture()" title="Capturar foto / subir archivo">
    ＋ Capturar
  </button>
  <div id="server-indicator" class="server-status offline" title="python kb_server.py">
    <span class="server-dot"></span><span id="server-label">offline</span>
  </div>
  <button class="theme-btn" onclick="toggleTheme()">◑</button>
</header>

<!-- Properties editor -->
<div id="props-overlay" class="props-overlay" onclick="if(event.target===this)closeProps()">
  <div class="props-panel">
    <div class="props-header">
      <span class="props-title">⚙️ Propiedades de la nota</span>
      <button class="props-close" onclick="closeProps()">✕</button>
    </div>
    <div class="props-body">
      <div class="props-field">
        <span class="props-label">Tipo</span>
        <select id="props-type" class="props-select"></select>
      </div>
      <div class="props-field">
        <span class="props-label">Tags</span>
        <div class="props-tags-wrap" id="props-tags-wrap" onclick="document.getElementById('props-tag-input').focus()">
          <input id="props-tag-input" class="props-tag-input" placeholder="Agregar tag…"
                 onkeydown="propsTagKeydown(event)">
        </div>
      </div>
      <div class="props-field">
        <span class="props-label">Status</span>
        <input id="props-status-input" class="props-input" type="text" placeholder="ej. draft, active, archived…">
      </div>
    </div>
    <div class="props-footer">
      <span id="props-status-msg" class="props-status"></span>
      <button class="props-save" id="props-save-btn" onclick="saveProps()">Guardar</button>
    </div>
  </div>
</div>

<!-- Quick switcher -->
<div id="qs-overlay" class="qs-overlay" onclick="if(event.target===this)closeQS()">
  <div class="qs-panel">
    <input id="qs-input" class="qs-input" placeholder="Buscar nota por título…" autocomplete="off"
           oninput="renderQS()" onkeydown="qsKeydown(event)">
    <div class="qs-list" id="qs-list"></div>
    <div class="qs-hint">
      <span>↑↓ navegar</span><span>Enter abrir</span><span>Esc cerrar</span>
    </div>
  </div>
</div>

<!-- Chat panel -->
<div id="chat-overlay" class="chat-overlay">
  <div class="chat-backdrop" onclick="closeChat()"></div>
  <div class="chat-panel">
    <div class="chat-header">
      <div>
        <div class="chat-title">💬 KB Chat</div>
        <div class="chat-subtitle" id="chat-subtitle">vault inteligente</div>
      </div>
      <button class="chat-clear" onclick="clearChat()">Limpiar</button>
      <button class="chat-close" onclick="closeChat()">✕</button>
    </div>

    <div class="chat-messages" id="chat-messages">
      <div class="chat-empty" id="chat-empty">
        <div class="chat-empty-icon">🧠</div>
        <div class="chat-empty-title">Pregúntale a tu vault</div>
        <div class="chat-empty-hints">
          Prueba con:<br>
          <span class="chat-hint-chip" onclick="sendHint(this)">¿Qué aprendí sobre agile?</span>
          <span class="chat-hint-chip" onclick="sendHint(this)">Resume mis notas de Gemini</span>
          <span class="chat-hint-chip" onclick="sendHint(this)">¿Qué técnicas de coaching conozco?</span>
          <span class="chat-hint-chip" onclick="sendHint(this)">Explícame el change management</span>
        </div>
      </div>
    </div>

    <div class="chat-input-area">
      <div class="chat-input-row">
        <textarea id="chat-input" class="chat-textarea" rows="1"
          placeholder="Pregunta algo sobre tus notas…"
          onkeydown="chatKeydown(event)"></textarea>
        <button id="chat-send" class="chat-send" onclick="sendChat()">↑</button>
      </div>
      <div class="chat-hint-text">Ctrl+Enter para enviar</div>
    </div>
  </div>
</div>

<!-- Upload modal -->
<div id="upload-modal" style="display:none" class="modal-backdrop" onclick="if(event.target===this)closeCapture()">
  <div class="modal">
    <div class="modal-title">Capturar nota</div>
    <div class="modal-sub">Sube una foto, imagen o PDF para procesarla con el pipeline.</div>
    <div class="camera-row">
      <button class="camera-btn" onclick="triggerCamera('capture')">📷 Cámara</button>
      <button class="camera-btn" onclick="triggerCamera('gallery')">🖼️ Galería / PDF</button>
    </div>
    <div class="drop-zone" id="drop-zone">
      <input type="file" id="file-input" accept="image/*,.pdf" onchange="handleFileSelect(event)">
      <div class="drop-icon">📂</div>
      <div class="drop-label">Arrastra un archivo aquí</div>
      <div class="drop-hint">PNG · JPG · HEIC · PDF</div>
    </div>
    <div class="pipeline-log" id="pipeline-log"></div>
    <div class="modal-actions">
      <button class="btn-cancel" onclick="closeCapture()">Cerrar</button>
    </div>
  </div>
</div>

<!-- Kanban overlay -->
<div id="kanban-overlay" class="kanban-overlay">
  <div class="kanban-topbar">
    <span class="kanban-topbar-title">📋 Proyectos</span>
    <button class="graph-ctrl" onclick="openKanbanNewProject()">+ Nuevo proyecto</button>
    <button class="graph-ctrl" onclick="closeKanban()">✕ Cerrar</button>
  </div>
  <div class="kanban-body">
    <div class="kanban-sidebar" id="kanban-sidebar"></div>
    <div class="kanban-board" id="kanban-board">
      <div class="kanban-empty" style="grid-column:1/-1">Selecciona un proyecto</div>
    </div>
  </div>
</div>

<!-- Graph overlay -->
<div id="graph-overlay" class="graph-overlay">
  <div class="graph-toolbar">
    <span class="graph-title">⬡ Grafo de conocimiento</span>
    <span class="graph-subtitle" id="graph-subtitle"></span>
    <button class="graph-ctrl" onclick="graphZoomBy(1.25)">＋</button>
    <button class="graph-ctrl" onclick="graphZoomBy(0.8)">－</button>
    <button class="graph-ctrl" onclick="resetGraphView()">⌂ Reset</button>
    <button class="graph-ctrl" onclick="closeGraph()">✕ Cerrar</button>
  </div>
  <div class="graph-canvas-wrap" id="graph-canvas-wrap">
    <canvas id="graph-canvas"></canvas>
    <div class="graph-legend" id="graph-legend"></div>
    <div class="graph-tooltip" id="graph-tooltip"></div>
    <div class="graph-hint">Scroll: zoom&nbsp;&nbsp;·&nbsp;&nbsp;Drag: mover&nbsp;&nbsp;·&nbsp;&nbsp;Click: abrir nota</div>
  </div>
</div>

<!-- URL import overlay -->
<div id="url-overlay" class="url-overlay" onclick="if(event.target===this)closeUrlImport()">
  <div class="url-panel">
    <div class="url-header">
      <span class="url-title">🔗 Importar desde URL</span>
      <button class="url-close" onclick="closeUrlImport()">✕</button>
    </div>
    <div class="url-field">
      <span class="url-label">URL</span>
      <input id="url-input" class="url-input" type="url" placeholder="https://…" onkeydown="if(event.key==='Enter')importFromUrl()">
    </div>
    <div class="url-field">
      <span class="url-label">Título (opcional — lo infiere del título de la página)</span>
      <input id="url-title-input" class="url-input" type="text" placeholder="Dejar vacío para usar el título de la página" style="font-family:var(--sans)">
    </div>
    <div class="url-footer">
      <span class="url-status" id="url-status"></span>
      <button type="button" class="url-btn" id="url-btn" onclick="importFromUrl()">Importar</button>
    </div>
  </div>
</div>

<!-- Stats overlay -->
<div id="stats-overlay" class="stats-overlay" onclick="if(event.target===this)closeStats()">
  <div class="stats-panel">
    <div class="stats-header">
      <span class="stats-title">📊 Estadísticas del vault</span>
      <button class="stats-close" onclick="closeStats()">✕</button>
    </div>
    <div class="stats-body" id="stats-body">
      <div style="color:var(--text-3);font-size:13px;text-align:center;padding:40px 0">Calculando…</div>
    </div>
  </div>
</div>

<!-- Trash overlay -->
<div id="trash-overlay" class="trash-overlay" onclick="if(event.target===this)closeTrash()">
  <div class="trash-panel">
    <div class="trash-header">
      <span class="trash-title">🗑 Papelera</span>
      <button class="trash-close" onclick="closeTrash()">✕</button>
    </div>
    <div class="trash-list" id="trash-list"></div>
  </div>
</div>

<!-- Quick capture overlay -->
<div id="qc-overlay" class="qc-overlay" onclick="if(event.target===this)closeQuickCapture()">
  <div class="qc-panel">
    <div class="qc-header">
      <span class="qc-label">✏️ Nueva nota</span>
      <input id="qc-title" class="qc-title-input" type="text" placeholder="Título (opcional — lo infiere la IA)">
      <button class="qc-close" onclick="closeQuickCapture()">✕</button>
    </div>
    <div class="qc-folder-row">
      <span class="qc-folder-label">📁 Carpeta</span>
      <select id="qc-folder" class="qc-folder-select">
        <option value="">Auto (IA)</option>
      </select>
    </div>
    <div id="qc-dup-panel" class="qc-dup-panel"></div>
    <div class="qc-tpl-row" id="qc-tpl-row">
      <span class="qc-tpl-label">Plantilla</span>
    </div>
    <div class="qc-body-wrap">
      <textarea id="qc-body" class="qc-textarea" placeholder="Escribe el contenido…&#10;&#10;La IA clasificará la carpeta, tipo y tags automáticamente." onkeydown="qcKeydown(event)"></textarea>
    </div>
    <div class="qc-footer">
      <span class="qc-hint">Ctrl+Enter para guardar</span>
      <span class="qc-status" id="qc-status"></span>
      <button type="button" class="qc-save" id="qc-save-btn" onclick="submitQuickCapture()">Guardar nota</button>
    </div>
  </div>
</div>

<!-- Editor overlay -->
<div id="editor-overlay" style="display:none" class="editor-overlay" onclick="if(event.target===this)closeEditor()">
  <div class="editor-panel">
    <div class="editor-header">
      <div class="editor-title" id="editor-note-title">—</div>
      <span class="editor-status" id="editor-status">listo</span>
      <button class="editor-save" id="editor-save-btn" onclick="saveNote()">Guardar</button>
      <button class="editor-close" onclick="closeEditor()">✕</button>
    </div>
    <textarea class="editor-textarea" id="editor-textarea" spellcheck="false" placeholder="Contenido de la nota…"></textarea>
  </div>
</div>

<div class="timeline-bar" id="timeline-bar">
  <span class="tl-label">Índice</span>
</div>

<div class="layout">
  <aside>
    <div class="sidebar-section" id="starred-section" style="margin-top:8px">
      <span class="sidebar-label">⭐ Favoritos</span>
      <div id="starred-nav"></div>
    </div>
    <div class="sidebar-section" style="margin-top:8px">
      <span class="sidebar-label">Carpetas</span>
      <div id="folder-nav"></div>
    </div>
    <div class="sidebar-section">
      <button id="orphan-btn" class="folder-btn" onclick="toggleOrphan()" style="width:100%;justify-content:space-between">
        <span>🔗 Sin conexiones</span><span id="orphan-count" class="folder-count"></span>
      </button>
    </div>
    <div class="sidebar-section">
      <span class="sidebar-label">Tipo</span>
      <div class="type-filters" id="type-filters"></div>
    </div>
    <div class="sidebar-section">
      <span class="sidebar-label">Tags</span>
      <div class="tag-cloud" id="tag-cloud"></div>
    </div>
  </aside>
  <div class="panel-handle" id="sidebar-handle" onclick="toggleSidebar()" title="Colapsar / expandir sidebar">
    <span id="sidebar-arrow">‹</span>
  </div>

  <main id="main-area">
    <!-- Left: note list -->
    <div class="list-panel">
      <div id="main-feed"></div>
    </div>
    <div class="panel-handle" id="list-handle" onclick="toggleList()" title="Colapsar / expandir lista">
      <span id="list-arrow">‹</span>
    </div>

    <!-- Right: note detail -->
    <div class="detail-panel" id="detail-panel">
      <div class="detail-empty" id="detail-empty">
        <span>← selecciona una nota para leerla</span>
      </div>
      <div class="detail-inner" id="detail-inner" style="display:none"></div>
    </div>
  </main>
</div>

<script>
const DATA        = __DATA__;
const FOLDER_META = __FOLDER_META__;

let activeFolder  = null;
let activeTag     = null;
let activeType    = null;
let activeOrphan  = false;
let searchQuery   = '';
let activeNoteId  = null;

// ── Theme ──────────────────────────────────────────────────────
function toggleTheme() {
  const root = document.documentElement;
  const cur  = root.getAttribute('data-theme');
  root.setAttribute('data-theme', cur === 'dark' ? 'light' : cur === 'light' ? 'dark' : 'light');
}

// ── HTML escape ────────────────────────────────────────────────
function esc(s) {
  return String(s)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

// ── Inline markdown (operates on already-escaped text) ─────────
function inlineMd(s) {
  return s
    // [[wikilinks]]
    .replace(/\[\[([^\]]+)\]\]/g, (_, title) => {
      const raw = title.replace(/&amp;/g,'&').replace(/&lt;/g,'<').replace(/&gt;/g,'>').replace(/&quot;/g,'"');
      const idx = DATA.notes.findIndex(n => n.title.toLowerCase() === raw.toLowerCase().trim());
      return idx >= 0
        ? `<a class="wikilink" onclick="openNoteById(${DATA.notes[idx].id});return false;">${title}</a>`
        : `<span class="wikilink-missing">[[${title}]]</span>`;
    })
    // **bold**
    .replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>')
    // *italic* (not preceded/followed by *)
    .replace(/(?<!\*)\*(?!\*)([^*\n]+)(?<!\*)\*(?!\*)/g, '<em>$1</em>')
    // `code`
    .replace(/`([^`\n]+)`/g, '<code>$1</code>')
    // [text](url)
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank" rel="noopener">$1</a>');
}

// ── Block markdown renderer ────────────────────────────────────
function renderMd(raw) {
  if (!raw || !raw.trim()) return '<p style="color:var(--text-3);font-family:var(--mono);font-size:12px;">Sin contenido.</p>';
  const lines = raw.split('\n');
  const out = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // Fenced code block
    if (line.startsWith('```')) {
      const lang = line.slice(3).trim();
      const codeLines = [];
      i++;
      while (i < lines.length && !lines[i].startsWith('```')) {
        codeLines.push(lines[i]);
        i++;
      }
      i++; // skip closing ```
      if (lang === 'mermaid') {
        // Raw content — Mermaid.js parses it; do not HTML-escape
        out.push(`<pre class="mermaid">${codeLines.join('\n')}</pre>`);
      } else {
        const escapedLang = esc(lang);
        out.push(`<pre><code${escapedLang ? ` class="lang-${escapedLang}"` : ''}>${codeLines.map(l => esc(l)).join('\n')}</code></pre>`);
      }
      continue;
    }

    // Horizontal rule
    if (/^(-{3,}|\*{3,}|_{3,})\s*$/.test(line)) {
      out.push('<hr>'); i++; continue;
    }

    // ATX headers
    const hm = line.match(/^(#{1,4})\s+(.*)/);
    if (hm) {
      const lv = hm[1].length;
      const slug = hm[2].toLowerCase().replace(/[^\w\s-]/g,'').trim().replace(/\s+/g,'-');
      out.push(`<h${lv} id="h-${slug}">${inlineMd(esc(hm[2]))}</h${lv}>`);
      i++; continue;
    }

    // Blockquote
    if (line.startsWith('> ')) {
      const qlines = [];
      while (i < lines.length && lines[i].startsWith('> ')) {
        qlines.push(lines[i].slice(2));
        i++;
      }
      out.push(`<blockquote>${inlineMd(esc(qlines.join('\n')))}</blockquote>`);
      continue;
    }

    // Unordered list
    if (/^\s*[-*+]\s/.test(line)) {
      const items = [];
      while (i < lines.length && /^\s*[-*+]\s/.test(lines[i])) {
        items.push(`<li>${inlineMd(esc(lines[i].replace(/^\s*[-*+]\s/, '')))}</li>`);
        i++;
      }
      out.push(`<ul>${items.join('')}</ul>`);
      continue;
    }

    // Ordered list
    if (/^\d+[.)]\s/.test(line)) {
      const items = [];
      while (i < lines.length && /^\d+[.)]\s/.test(lines[i])) {
        items.push(`<li>${inlineMd(esc(lines[i].replace(/^\d+[.)]\s/, '')))}</li>`);
        i++;
      }
      out.push(`<ol>${items.join('')}</ol>`);
      continue;
    }

    // Table (header row followed by separator row)
    if (line.trim().startsWith('|') && i + 1 < lines.length && /^[\s|:-]+$/.test(lines[i + 1])) {
      const parseCells = r => r.split('|').slice(1, -1).map(c => c.trim());
      const headers = parseCells(line);
      i += 2; // skip header + separator
      const bodyRows = [];
      while (i < lines.length && lines[i].trim().startsWith('|')) {
        bodyRows.push(parseCells(lines[i]));
        i++;
      }
      const thead = `<thead><tr>${headers.map(h => `<th>${inlineMd(esc(h))}</th>`).join('')}</tr></thead>`;
      const tbody = bodyRows.map(r => `<tr>${r.map(c => `<td>${inlineMd(esc(c))}</td>`).join('')}</tr>`).join('');
      out.push(`<table><${thead}<tbody>${tbody}</tbody></table>`);
      continue;
    }

    // Image (skip — can't load relative paths without a server)
    if (/^!\[/.test(line)) {
      const im = line.match(/^!\[([^\]]*)\]\(([^)]+)\)/);
      if (im) {
        out.push(`<p style="color:var(--text-3);font-size:11px;font-family:var(--mono);">[imagen: ${esc(im[1] || im[2])}]</p>`);
        i++; continue;
      }
    }

    // Empty line
    if (line.trim() === '') { i++; continue; }

    // Paragraph: collect consecutive non-empty, non-block lines
    const paraLines = [];
    while (i < lines.length) {
      const l = lines[i];
      if (l.trim() === '') break;
      if (/^#{1,4}\s/.test(l)) break;
      if (l.startsWith('```')) break;
      if (l.startsWith('> ')) break;
      if (/^\s*[-*+]\s/.test(l)) break;
      if (/^\d+[.)]\s/.test(l)) break;
      if (/^(-{3,}|\*{3,}|_{3,})\s*$/.test(l)) break;
      if (l.trim().startsWith('|') && i + 1 < lines.length && /^[\s|:-]+$/.test(lines[i + 1])) break;
      paraLines.push(l);
      i++;
    }
    if (paraLines.length) {
      out.push(`<p>${inlineMd(esc(paraLines.join(' ')))}</p>`);
    }
  }

  return out.join('\n');
}

// ── Note detail ────────────────────────────────────────────────
function openNoteById(id) {
  activeNoteId = id;
  const note = DATA.notes.find(n => n.id === id);
  if (!note) return;

  // Highlight active row
  document.querySelectorAll('.note-row').forEach(r => {
    r.classList.toggle('active', parseInt(r.dataset.noteId) === id);
  });

  const fm = FOLDER_META[note.folder];
  const chips = [
    `<span class="chip">${esc(note.date)}</span>`,
    note.type  ? `<span class="chip chip-accent">${esc(note.type)}</span>` : '',
    note.status ? `<span class="chip">${esc(note.status)}</span>` : '',
    fm ? `<span class="chip chip-folder" style="color:${fm.color};border-color:${fm.color}55;background:${fm.color}18">${esc(fm.label)}</span>` : '',
    ...note.tags.map(t => `<span class="chip">#${esc(t)}</span>`),
  ].filter(Boolean).join('');

  document.getElementById('detail-empty').style.display = 'none';
  const inner = document.getElementById('detail-inner');
  inner.style.display = '';
  inner.innerHTML = `
    <div class="detail-header">
      <div class="detail-title">${esc(note.title)}</div>
      <div style="display:flex;align-items:center;gap:6px;flex-shrink:0">
        <select class="detail-folder-select" data-edit onchange="moveNote(${id}, this.value, this)">
          ${Object.entries(FOLDER_META).map(([k,v]) =>
            `<option value="${k}"${k === note.folder ? ' selected' : ''}>${v.label}</option>`
          ).join('')}
        </select>
        <button id="star-btn" class="detail-close detail-star" onclick="toggleStar(${id})" title="Marcar como favorita">☆</button>
        <button class="detail-close" onclick="openProps(${id})" title="Editar propiedades" data-edit>⚙️</button>
        <button class="detail-close" onclick="openLinkSuggest(${id})" title="Sugerir wikilinks" data-edit>🔗</button>
        <button class="detail-close" onclick="openEditor(${id})" data-edit>✏️</button>
        <button class="detail-close" onclick="deleteNote(${id})" style="color:#f87171" data-edit title="Eliminar">🗑</button>
        <button class="detail-close" onclick="closeDetail()">✕</button>
      </div>
    </div>
    <div class="detail-chips">${chips}</div>
    <div class="detail-body-wrap">
      <div class="note-body">${renderMd(note.body || '')}</div>
      <div id="outline-panel" class="outline-panel"></div>
    </div>
    ${renderBacklinks(id)}
    ${semanticReady ? `<div id="related-section" class="backlinks-section">
      <div class="backlinks-label">relacionadas</div>
      <div class="backlinks-empty related-loading"><span class="semantic-spinner"></span> buscando similares…</div>
    </div>` : ''}`;

  // Apply server-online state to dynamically created data-edit buttons
  inner.querySelectorAll('[data-edit]').forEach(el => {
    el.style.display = serverOnline ? '' : 'none';
  });

  // Scroll detail panel to top
  document.getElementById('detail-panel').scrollTop = 0;

  // Update star button state
  _updateStarBtn(id);

  // Build outline from rendered headers
  buildOutline(note.body || '');

  // Render Mermaid diagrams inside the freshly injected HTML
  if (typeof mermaid !== 'undefined') {
    const mNodes = inner.querySelectorAll('.mermaid:not([data-processed])');
    if (mNodes.length) {
      const isDark = document.documentElement.dataset.theme === 'dark' ||
        (!document.documentElement.dataset.theme && window.matchMedia('(prefers-color-scheme: dark)').matches);
      mermaid.initialize({ startOnLoad: false, theme: isDark ? 'dark' : 'default', securityLevel: 'loose' });
      mermaid.run({ nodes: mNodes });
    }
  }

  // Async: populate related notes
  if (semanticReady) loadRelatedNotes(id);
}

function closeDetail() {
  activeNoteId = null;
  document.getElementById('detail-empty').style.display = '';
  document.getElementById('detail-inner').style.display = 'none';
  document.querySelectorAll('.note-row').forEach(r => r.classList.remove('active'));
}

// ── Filtering ──────────────────────────────────────────────────
function filtered() {
  return DATA.notes.filter(n => {
    if (activeFolder && !n.folder.startsWith(activeFolder)) return false;
    if (activeTag    && !n.tags.includes(activeTag))         return false;
    if (activeType   && n.type !== activeType)               return false;
    if (activeOrphan && !isOrphan(n))                        return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      if (!n.title.toLowerCase().includes(q) &&
          !n.tags.join(' ').toLowerCase().includes(q) &&
          !n.folder.toLowerCase().includes(q) &&
          !(n.body || '').toLowerCase().includes(q)) return false;
    }
    return true;
  });
}

// ── Sidebar ────────────────────────────────────────────────────
// ── Properties editor ────────────────────────────────────────────
let _propsNoteId = null;
let _propsTags   = [];
let _propsRaw    = '';   // full file content

async function openProps(id) {
  if (!serverOnline) { alert('El servidor no está corriendo.\nEjecuta: python kb_server.py'); return; }
  _propsNoteId = id;
  const note = DATA.notes.find(n => n.id === id);
  if (!note) return;

  // Load types for select
  const types = ['', ...new Set(DATA.notes.map(n => n.type).filter(Boolean)).values()].sort();
  const sel = document.getElementById('props-type');
  sel.innerHTML = types.map(t => `<option value="${t}"${t === (note.type||'') ? ' selected' : ''}>${t || '(sin tipo)'}</option>`).join('');

  // Load current tags
  _propsTags = [...(note.tags || [])];
  renderPropsTags();

  // Load status
  document.getElementById('props-status-input').value = note.status || '';
  document.getElementById('props-status-msg').textContent = '';
  document.getElementById('props-save-btn').disabled = false;

  // Fetch raw content so we can modify frontmatter precisely
  try {
    const r = await fetch(`${SERVER}/note/read?path=${encodeURIComponent(note.path)}`);
    const d = await r.json();
    _propsRaw = d.content || '';
  } catch { _propsRaw = ''; }

  document.getElementById('props-overlay').classList.add('open');
}

function closeProps() {
  document.getElementById('props-overlay').classList.remove('open');
  _propsNoteId = null;
}

function renderPropsTags() {
  const wrap = document.getElementById('props-tags-wrap');
  const inp  = document.getElementById('props-tag-input');
  wrap.innerHTML = '';
  _propsTags.forEach(tag => {
    const chip = document.createElement('span');
    chip.className = 'props-tag';
    chip.innerHTML = `#${esc(tag)}<button class="props-tag-rm" onclick="propsRemoveTag('${esc(tag)}')">×</button>`;
    wrap.appendChild(chip);
  });
  wrap.appendChild(inp);
  inp.value = '';
}

function propsRemoveTag(tag) {
  _propsTags = _propsTags.filter(t => t !== tag);
  renderPropsTags();
}

function propsTagKeydown(e) {
  if (e.key === 'Enter' || e.key === ',') {
    e.preventDefault();
    const val = e.target.value.trim().replace(/^#/, '').replace(/,/g, '').toLowerCase();
    if (val && !_propsTags.includes(val)) { _propsTags.push(val); renderPropsTags(); }
    else e.target.value = '';
  } else if (e.key === 'Backspace' && !e.target.value && _propsTags.length) {
    _propsTags.pop(); renderPropsTags();
  } else if (e.key === 'Escape') { closeProps(); }
}

async function saveProps() {
  if (!_propsNoteId) return;
  const note = DATA.notes.find(n => n.id === _propsNoteId);
  if (!note) return;

  const btn = document.getElementById('props-save-btn');
  const msg = document.getElementById('props-status-msg');
  btn.disabled = true;
  msg.textContent = 'Guardando…';
  msg.className = 'props-status';

  const newType   = document.getElementById('props-type').value;
  const newStatus = document.getElementById('props-status-input').value.trim();
  const newTags   = [..._propsTags];

  // Parse and patch frontmatter
  const fmRe = /^---\n([\s\S]*?)\n---\n?/;
  const m = _propsRaw.match(fmRe);
  let body = _propsRaw;
  let fm = {};
  if (m) {
    body = _propsRaw.slice(m[0].length);
    // Parse key: value lines manually (avoids needing js-yaml)
    m[1].split('\n').forEach(line => {
      const kv = line.match(/^(\w+):\s*(.*)/);
      if (kv) fm[kv[1]] = kv[2].trim().replace(/^['"]|['"]$/g, '');
    });
    // Parse tags array
    const tagBlock = m[1].match(/^tags:\n((?:\s*-\s*.+\n?)*)/m);
    if (tagBlock) fm._tagsArr = tagBlock[1].split('\n').map(l => l.replace(/^\s*-\s*/,'').trim()).filter(Boolean);
    else {
      const inline = m[1].match(/^tags:\s*\[([^\]]*)\]/m);
      if (inline) fm._tagsArr = inline[1].split(',').map(s => s.trim().replace(/^['"]|['"]$/g,'')).filter(Boolean);
      else fm._tagsArr = [];
    }
  }

  // Apply changes
  if (newType)   fm.type   = newType; else delete fm.type;
  if (newStatus) fm.status = newStatus; else delete fm.status;
  fm._tagsArr = newTags;

  // Reconstruct frontmatter
  const fmLines = [];
  const order = ['title','date','type','status','tags','folder'];
  const done  = new Set(['_tagsArr']);
  order.forEach(k => {
    if (k === 'tags') return; // handled below
    if (fm[k] !== undefined) { fmLines.push(`${k}: ${fm[k]}`); done.add(k); }
  });
  // remaining keys
  Object.keys(fm).forEach(k => { if (!done.has(k) && k !== 'tags') fmLines.push(`${k}: ${fm[k]}`); });
  // tags block
  if (newTags.length) fmLines.push(`tags:\n${newTags.map(t => `- ${t}`).join('\n')}`);
  else fmLines.push('tags: []');

  const newContent = `---\n${fmLines.join('\n')}\n---\n${body}`;

  try {
    const r = await fetch(`${SERVER}/note/save`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({ path: note.path, content: newContent }),
    });
    const d = await r.json();
    if (!r.ok) throw new Error(d.error || r.statusText);
    // Update DATA.notes in memory so UI reflects changes without reload
    note.type   = newType   || null;
    note.status = newStatus || null;
    note.tags   = newTags;
    msg.textContent = '✓ Guardado';
    msg.className = 'props-status ok';
    setTimeout(closeProps, 900);
    // Refresh open note chips
    if (activeNoteId === _propsNoteId) openNoteById(_propsNoteId);
  } catch(err) {
    msg.textContent = '✗ ' + err.message;
    msg.className = 'props-status err';
    btn.disabled = false;
  }
}

// ── Outline view ────────────────────────────────────────────────
function buildOutline(raw) {
  const panel = document.getElementById('outline-panel');
  if (!panel) return;
  const headers = [];
  for (const line of raw.split('\n')) {
    const m = line.match(/^(#{1,4})\s+(.*)/);
    if (m) headers.push({ level: m[1].length, text: m[2].replace(/[*_`]/g, '') });
  }
  if (headers.length < 2) { panel.innerHTML = ''; return; }
  const items = headers.map(h => {
    const slug = h.text.toLowerCase().replace(/[^\w\s-]/g,'').trim().replace(/\s+/g,'-');
    return `<span class="outline-item h${h.level}" onclick="
      const el=document.getElementById('h-${slug}');
      if(el)el.scrollIntoView({behavior:'smooth',block:'start'})
    " title="${esc(h.text)}">${esc(h.text)}</span>`;
  }).join('');
  panel.innerHTML = `<div class="outline-label">En esta nota</div>${items}`;
}

// ── Starred notes ────────────────────────────────────────────────
const _STAR_KEY = 'kb_starred_v1';
let _starred = new Set(JSON.parse(localStorage.getItem(_STAR_KEY) || '[]'));

function _saveStarred() {
  localStorage.setItem(_STAR_KEY, JSON.stringify([..._starred]));
}

function toggleStar(id) {
  if (_starred.has(id)) _starred.delete(id); else _starred.add(id);
  _saveStarred();
  _updateStarBtn(id);
  buildStarredNav();
}

function _updateStarBtn(id) {
  const btn = document.getElementById('star-btn');
  if (!btn) return;
  const on = _starred.has(id);
  btn.textContent = on ? '★' : '☆';
  btn.title = on ? 'Quitar de favoritos' : 'Marcar como favorita';
  btn.classList.toggle('starred', on);
}

function buildStarredNav() {
  const nav = document.getElementById('starred-nav');
  const sec = document.getElementById('starred-section');
  if (!nav || !sec) return;
  const items = [..._starred].map(id => DATA.notes.find(n => n.id === id)).filter(Boolean);
  sec.classList.toggle('has-items', items.length > 0);
  nav.innerHTML = items.map(n => {
    const color = Object.entries(FOLDER_META).find(([k]) => n.folder?.startsWith(k))?.[1]?.color || '#6b7280';
    return `<div class="starred-item" onclick="openNoteById(${n.id})">
      <span class="starred-item-dot" style="background:${color}"></span>
      <span class="starred-item-title">${esc(n.title)}</span>
    </div>`;
  }).join('');
}

function buildSidebar() {
  const nav   = document.getElementById('folder-nav');
  const total = DATA.notes.length;

  buildStarredNav();
  nav.appendChild(makeFolder('all', 'Todos', total, null));
  Object.entries(DATA.stats.by_folder)
    .sort((a, b) => b[1] - a[1])
    .forEach(([key, count]) => {
      nav.appendChild(makeFolder(key, FOLDER_META[key]?.label || key, count, FOLDER_META[key]?.color));
    });
}

function makeFolder(key, label, count, color) {
  const btn = document.createElement('button');
  btn.className = 'folder-btn' + (key === 'all' && !activeFolder ? ' active' : '');
  btn.dataset.key = key;

  const dot = document.createElement('span');
  dot.className = 'folder-dot';
  dot.style.background = color || 'var(--text-3)';
  if (key === 'all') dot.style.background = 'var(--accent)';

  const lbl = document.createElement('span');
  lbl.textContent = label;
  lbl.style.cssText = 'overflow:hidden;text-overflow:ellipsis;white-space:nowrap';

  const cnt = document.createElement('span');
  cnt.className = 'folder-count';
  cnt.textContent = count;

  btn.append(dot, lbl, cnt);
  btn.onclick = () => {
    activeFolder = key === 'all' ? null : key;
    activeTag = null; activeType = null; activeOrphan = false;
    document.getElementById('orphan-btn').classList.remove('active');
    document.getElementById('search').value = '';
    searchQuery = '';
    refreshAll();
  };
  return btn;
}

function buildTagCloud() {
  const freq = {};
  DATA.notes.forEach(n => n.tags.forEach(t => { freq[t] = (freq[t] || 0) + 1; }));
  const top  = Object.entries(freq).sort((a, b) => b[1] - a[1]).slice(0, 40);
  const cloud = document.getElementById('tag-cloud');
  cloud.innerHTML = '';
  top.forEach(([tag]) => {
    const chip = document.createElement('button');
    chip.className = 'tag-chip' + (activeTag === tag ? ' active' : '');
    chip.textContent = '#' + tag;
    chip.onclick = () => { activeTag = activeTag === tag ? null : tag; refreshAll(); };
    cloud.appendChild(chip);
  });
}

function buildTypeFilters() {
  const types = [...new Set(DATA.notes.map(n => n.type).filter(Boolean))].sort();
  const wrap  = document.getElementById('type-filters');
  wrap.innerHTML = '';
  types.forEach(t => {
    const chip = document.createElement('button');
    chip.className = 'type-chip' + (activeType === t ? ' active' : '');
    chip.textContent = t;
    chip.onclick = () => { activeType = activeType === t ? null : t; refreshAll(); };
    wrap.appendChild(chip);
  });
}

function setFolder(key) {
  activeFolder = key; activeTag = null; activeType = null;
  document.getElementById('search').value = ''; searchQuery = '';
  refreshAll();
}

function jumpMonth(key) {
  const anchor = document.getElementById('month-' + key);
  if (anchor) anchor.scrollIntoView({ behavior: 'smooth', block: 'start' });
}

// ── Feed ───────────────────────────────────────────────────────
function buildFeed(notes) {
  const feed = document.getElementById('main-feed');
  feed.innerHTML = '';

  if (!notes.length) {
    feed.innerHTML = '<p class="empty-state">Sin resultados.</p>';
    return;
  }

  const byMonth = {};
  notes.forEach(n => {
    const d     = new Date(n.date + 'T12:00:00');
    const key   = n.date.slice(0, 7);
    const label = d.toLocaleString('es', { month: 'long', year: 'numeric' });
    if (!byMonth[key]) byMonth[key] = { label, notes: [] };
    byMonth[key].notes.push(n);
  });

  Object.entries(byMonth)
    .sort((a, b) => b[0].localeCompare(a[0]))
    .forEach(([key, { label, notes: mnotes }]) => {
      const group = document.createElement('div');
      group.className = 'month-group';
      group.id = 'month-' + key;

      const hdr = document.createElement('div');
      hdr.className = 'month-header';
      hdr.textContent = key + ' — ' + label.charAt(0).toUpperCase() + label.slice(1);
      group.appendChild(hdr);

      mnotes.forEach(n => {
        const row = document.createElement('div');
        row.className = 'note-row' + (n.id === activeNoteId ? ' active' : '');
        row.dataset.noteId = n.id;
        row.onclick = () => openNoteById(n.id);

        const dateEl = document.createElement('span');
        dateEl.className = 'note-date';
        dateEl.textContent = n.date;

        const titleWrap = document.createElement('span');
        titleWrap.className = 'note-title';
        titleWrap.textContent = n.title;
        if (n.updated) {
          const upd = document.createElement('span');
          upd.className = 'note-updated';
          upd.textContent = '↑' + n.updated;
          titleWrap.appendChild(upd);
        }

        const meta = document.createElement('span');
        meta.className = 'note-meta';

        const fm = FOLDER_META[n.folder];
        if (fm) {
          const fb = document.createElement('span');
          fb.className = 'badge badge-folder';
          fb.textContent = fm.label;
          fb.style.color       = fm.color;
          fb.style.borderColor = fm.color + '55';
          fb.style.background  = fm.color + '18';
          meta.appendChild(fb);
        }
        if (n.type) {
          const tb = document.createElement('span');
          tb.className = 'badge badge-type';
          tb.textContent = n.type;
          meta.appendChild(tb);
        }

        // Body snippet when search matches body but not title
        if (searchQuery) {
          const q = searchQuery.toLowerCase();
          const inTitle = n.title.toLowerCase().includes(q);
          const body    = (n.body || '').replace(/^---[\s\S]*?---\n/,'');
          const bodyIdx = body.toLowerCase().indexOf(q);
          if (!inTitle && bodyIdx >= 0) {
            const start   = Math.max(0, bodyIdx - 40);
            const end     = Math.min(body.length, bodyIdx + q.length + 60);
            const excerpt = (start > 0 ? '…' : '') + body.slice(start, end).replace(/\n/g,' ') + (end < body.length ? '…' : '');
            const snip    = document.createElement('span');
            snip.className = 'note-snippet';
            snip.innerHTML = esc(excerpt).replace(
              new RegExp(esc(searchQuery).replace(/[.*+?^${}()|[\]\\]/g,'\\$&'), 'gi'),
              m => `<mark>${m}</mark>`
            );
            row.appendChild(snip);
          }
        }

        row.append(dateEl, titleWrap, meta);
        group.appendChild(row);
      });

      feed.appendChild(group);
    });
}

// ── Timeline bar ───────────────────────────────────────────────
function buildTimeline() {
  const bar = document.getElementById('timeline-bar');
  bar.innerHTML = '<span class="tl-label">Índice</span>';
  const byMonth = {};
  DATA.notes.forEach(n => {
    const key = n.date.slice(0, 7);
    if (!byMonth[key]) {
      const d = new Date(n.date + 'T12:00:00');
      byMonth[key] = { label: d.toLocaleString('es', { month: 'short', year: '2-digit' }), count: 0 };
    }
    byMonth[key].count++;
  });
  Object.entries(byMonth).sort((a, b) => b[0].localeCompare(a[0])).forEach(([key, { label, count }]) => {
    const pill = document.createElement('button');
    pill.className = 'month-pill';
    pill.dataset.month = key;
    pill.innerHTML = `<span>${label}</span><span class="mpill-count">${count}</span>`;
    pill.onclick = () => {
      document.querySelectorAll('.month-pill').forEach(p => p.classList.remove('active'));
      pill.classList.add('active');
      const anchor = document.getElementById('month-' + key);
      if (anchor) anchor.scrollIntoView({ behavior: 'smooth', block: 'start' });
    };
    bar.appendChild(pill);
  });
}

// ── Stats + active states ──────────────────────────────────────
function updateStats(notes) {
  document.getElementById('total-pill').textContent = notes.length + ' notas';
  document.getElementById('date-pill').textContent  = 'actualizado ' + DATA.stats.last_updated;
}

function updateActiveFolder() {
  document.querySelectorAll('.folder-btn').forEach(btn => {
    const key = btn.dataset.key;
    btn.classList.toggle('active', (!activeFolder && key === 'all') || activeFolder === key);
  });
}

// ── Refresh ────────────────────────────────────────────────────
function refreshAll() {
  const notes = filtered();
  buildFeed(notes);
  updateStats(notes);
  buildTagCloud();
  buildTypeFilters();
  updateActiveFolder();
}

// ── Search ─────────────────────────────────────────────────────
document.getElementById('search').addEventListener('input', e => {
  searchQuery = e.target.value.trim();
  if (semanticMode && searchQuery) {
    clearTimeout(semanticTimer);
    semanticTimer = setTimeout(() => runSemanticSearch(searchQuery), 400);
  } else {
    refreshAll();
  }
});

// ── Chat ────────────────────────────────────────────────────────
let chatHistory  = [];   // [{role, content}, ...]
let chatBusy     = false;

function openChat() {
  if (!serverOnline) { alert('El servidor no está corriendo.\nEjecuta: python kb_server.py'); return; }
  document.getElementById('chat-overlay').classList.add('open');
  document.getElementById('chat-btn').classList.add('active');
  setTimeout(() => document.getElementById('chat-input').focus(), 300);
}

function closeChat() {
  document.getElementById('chat-overlay').classList.remove('open');
  document.getElementById('chat-btn').classList.remove('active');
}

function clearChat() {
  chatHistory = [];
  const msgs = document.getElementById('chat-messages');
  msgs.innerHTML = '';
  msgs.appendChild(document.getElementById('chat-empty') || makeChatEmpty());
  document.getElementById('chat-empty').style.display = '';
}

function sendHint(el) {
  document.getElementById('chat-input').value = el.textContent;
  sendChat();
}

function chatKeydown(e) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') { e.preventDefault(); sendChat(); }
  // Auto-resize textarea
  e.target.style.height = 'auto';
  e.target.style.height = Math.min(e.target.scrollHeight, 120) + 'px';
}

async function sendChat() {
  if (chatBusy) return;
  const input = document.getElementById('chat-input');
  const query = input.value.trim();
  if (!query) return;

  chatBusy = true;
  input.value = '';
  input.style.height = 'auto';
  document.getElementById('chat-send').disabled = true;
  document.getElementById('chat-empty').style.display = 'none';

  // Add user turn to UI
  const msgs = document.getElementById('chat-messages');
  const userDiv = document.createElement('div');
  userDiv.className = 'chat-turn';
  userDiv.innerHTML = `<div class="chat-user">${esc(query)}</div>`;
  msgs.appendChild(userDiv);
  msgs.scrollTop = msgs.scrollHeight;

  // Add assistant turn (starts with thinking dots)
  const assistantTurn = document.createElement('div');
  assistantTurn.className = 'chat-turn';
  const thinkingEl = document.createElement('div');
  thinkingEl.className = 'chat-assistant';
  thinkingEl.innerHTML = '<div class="chat-assistant-inner"><div class="chat-thinking"><span></span><span></span><span></span></div></div>';
  assistantTurn.appendChild(thinkingEl);
  msgs.appendChild(assistantTurn);
  msgs.scrollTop = msgs.scrollHeight;

  let fullText = '';
  let sources  = [];

  try {
    const resp = await fetch(SERVER + '/chat', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query, history: chatHistory, k: 6 }),
    });

    if (!resp.ok) {
      const err = await resp.json();
      throw new Error(err.error || resp.statusText);
    }

    const reader  = resp.body.getReader();
    const decoder = new TextDecoder();
    let   buf     = '';

    // Replace thinking dots with empty response div
    const innerEl = document.createElement('div');
    innerEl.className = 'chat-assistant-inner';
    innerEl.textContent = '';
    thinkingEl.innerHTML = '';
    thinkingEl.appendChild(innerEl);

    while (true) {
      const { done, value } = await reader.read();
      if (done) break;

      buf += decoder.decode(value, { stream: true });
      const lines = buf.split('\n');
      buf = lines.pop();

      for (const line of lines) {
        if (!line.startsWith('data: ')) continue;
        const ev = JSON.parse(line.slice(6));

        if (ev.type === 'sources') {
          sources = ev.notes;
          // Show source chips above the response text
          const sourcesEl = document.createElement('div');
          sourcesEl.className = 'chat-sources';
          sources.forEach(n => {
            const chip = document.createElement('button');
            chip.className = 'chat-source-chip';
            chip.title = n.path;
            chip.innerHTML = `<span class="chat-source-dot"></span>
              <span class="chat-source-title">${esc(n.title)}</span>
              <span class="chat-source-score">${Math.round(n.score*100)}%</span>`;
            chip.onclick = () => { openNoteById(n.id); };
            sourcesEl.appendChild(chip);
          });
          assistantTurn.insertBefore(sourcesEl, thinkingEl);

        } else if (ev.type === 'text') {
          fullText += ev.content;
          innerEl.innerHTML = renderChatMd(fullText, sources);
          msgs.scrollTop = msgs.scrollHeight;

        } else if (ev.type === 'error') {
          innerEl.innerHTML = `<span style="color:#F87171">Error: ${esc(ev.content)}</span>`;

        } else if (ev.type === 'done') {
          break;
        }
      }
    }

    // Save to history
    chatHistory.push({ role: 'user',      content: query    });
    chatHistory.push({ role: 'assistant', content: fullText });
    // Keep last 10 turns (20 messages)
    if (chatHistory.length > 20) chatHistory = chatHistory.slice(-20);

    document.getElementById('chat-subtitle').textContent =
      `${chatHistory.length / 2} turnos · ${DATA.notes.length} notas`;

  } catch (err) {
    thinkingEl.innerHTML = `<div class="chat-assistant-inner"><span style="color:#F87171">Error: ${esc(err.message)}</span></div>`;
  }

  chatBusy = false;
  document.getElementById('chat-send').disabled = false;
  msgs.scrollTop = msgs.scrollHeight;
  document.getElementById('chat-input').focus();
}

function renderChatMd(text, sources) {
  // Lightweight inline renderer for chat responses
  const sourceMap = {};
  sources.forEach(n => { sourceMap[n.id] = n; });

  return esc(text)
    // [ID] citation links
    .replace(/\[(\d+)\]/g, (_, id) => {
      const n = sourceMap[parseInt(id)];
      if (!n) return `<span class="chat-cite">[${id}]</span>`;
      return `<button class="chat-cite" onclick="openNoteById(${n.id})" title="${esc(n.path)}">[${id}]</button>`;
    })
    // **bold**
    .replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>')
    // *italic*
    .replace(/(?<!\*)\*(?!\*)([^*\n]+)(?<!\*)\*(?!\*)/g, '<em>$1</em>')
    // `code`
    .replace(/`([^`\n]+)`/g, '<code>$1</code>')
    // Paragraph breaks
    .split('\n\n').map(para => {
      para = para.trim();
      if (!para) return '';
      // Unordered list
      if (/^[-*•]\s/.test(para)) {
        const items = para.split('\n').filter(l => /^[-*•]\s/.test(l));
        return `<ul>${items.map(l => `<li>${l.replace(/^[-*•]\s/, '')}</li>`).join('')}</ul>`;
      }
      // Ordered list
      if (/^\d+[.)]\s/.test(para)) {
        const items = para.split('\n').filter(l => /^\d+[.)]\s/.test(l));
        return `<ol>${items.map(l => `<li>${l.replace(/^\d+[.)]\s/, '')}</li>`).join('')}</ol>`;
      }
      return `<p>${para.replace(/\n/g, ' ')}</p>`;
    }).join('');
}

// ── Semantic search ─────────────────────────────────────────────
let semanticMode  = false;
let semanticReady = false;
let semanticTimer = null;

function toggleSemantic() {
  if (!serverOnline) return;
  semanticMode = !semanticMode;
  document.getElementById('semantic-btn').classList.toggle('active', semanticMode);
  if (semanticMode && searchQuery) runSemanticSearch(searchQuery);
  else refreshAll();
}

async function checkEmbeddings() {
  if (!serverOnline) return;
  try {
    const r = await fetch(SERVER + '/embed/status', { signal: AbortSignal.timeout(800) });
    const d = await r.json();
    semanticReady = d.ready;
    const btn = document.getElementById('semantic-btn');
    btn.classList.toggle('offline', !semanticReady);
    btn.title = semanticReady
      ? `Búsqueda semántica — ${d.count} notas indexadas`
      : 'Embeddings no generados. Corre: python build_embeddings.py';
  } catch { semanticReady = false; }
}

async function runSemanticSearch(query) {
  const feed = document.getElementById('main-feed');
  feed.innerHTML = `<div class="semantic-notice"><span class="semantic-spinner"></span> Buscando…</div>`;
  document.getElementById('index-panel').innerHTML = '';

  try {
    const r = await fetch(`${SERVER}/search?q=${encodeURIComponent(query)}&k=20`);
    const d = await r.json();
    if (!d.ready) {
      feed.innerHTML = `<p class="empty-state">${d.error}</p>`;
      return;
    }
    if (!d.results.length) {
      feed.innerHTML = '<p class="empty-state">Sin resultados semánticos.</p>';
      return;
    }
    renderSemanticResults(d.results, query);
  } catch (err) {
    feed.innerHTML = `<p class="empty-state">Error: ${err.message}</p>`;
  }
}

function renderSemanticResults(results, query) {
  const feed = document.getElementById('main-feed');
  feed.innerHTML = '';

  const header = document.createElement('div');
  header.className = 'month-header';
  header.textContent = `⚡ Resultados semánticos para "${query}" — ${results.length} notas`;
  feed.appendChild(header);

  results.forEach(({ id, score }) => {
    const note = DATA.notes.find(n => n.id === id);
    if (!note) return;

    const pct = Math.round(score * 100);
    const row = document.createElement('div');
    row.className = 'note-row' + (note.id === activeNoteId ? ' active' : '');
    row.dataset.noteId = note.id;
    row.onclick = () => openNoteById(note.id);
    row.style.display = 'block';
    row.style.padding = '8px 10px';

    const fm = FOLDER_META[note.folder];
    const folderBadge = fm
      ? `<span class="badge badge-folder" style="color:${fm.color};border-color:${fm.color}55;background:${fm.color}18">${fm.label}</span>`
      : '';

    row.innerHTML = `
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:3px">
        <span class="note-title" style="white-space:nowrap;overflow:hidden;text-overflow:ellipsis;flex:1">${esc(note.title)}</span>
        <span class="semantic-score">${pct}%</span>
        ${folderBadge}
      </div>
      <div class="semantic-bar" style="width:${pct}%"></div>`;

    feed.appendChild(row);
  });
}

// ── URL import ───────────────────────────────────────────────────
function openUrlImport() {
  document.getElementById('url-overlay').classList.add('open');
  document.getElementById('url-input').value = '';
  document.getElementById('url-title-input').value = '';
  document.getElementById('url-status').textContent = '';
  document.getElementById('url-btn').disabled = false;
  setTimeout(() => document.getElementById('url-input').focus(), 50);
}

function closeUrlImport() {
  document.getElementById('url-overlay').classList.remove('open');
}

async function importFromUrl() {
  const url   = document.getElementById('url-input').value.trim();
  const title = document.getElementById('url-title-input').value.trim();
  if (!url) { document.getElementById('url-status').textContent = '⚠️ Ingresa una URL'; return; }
  const btn = document.getElementById('url-btn');
  const st  = document.getElementById('url-status');
  btn.disabled = true;
  st.textContent = '⏳ Descargando y clasificando…';
  try {
    const r = await fetch(SERVER + '/note/from-url', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({url, title}),
    });
    const d = await r.json();
    if (!r.ok) throw new Error(d.error || r.statusText);
    st.textContent = `✓ Guardada en ${d.folder} — recargando…`;
    closeUrlImport();
    location.href = location.pathname + (d.path ? '#open=' + encodeURIComponent(d.path) : '');
  } catch(e) {
    st.textContent = '❌ ' + e.message;
    btn.disabled = false;
  }
}

// ── Trash ────────────────────────────────────────────────────────
async function openTrash() {
  document.getElementById('trash-overlay').classList.add('open');
  document.getElementById('trash-list').innerHTML = '<div class="trash-empty">Cargando…</div>';
  try {
    const r    = await fetch(SERVER + '/trash/list');
    const items = await r.json();
    const el   = document.getElementById('trash-list');
    if (!items.length) {
      el.innerHTML = '<div class="trash-empty">La papelera está vacía.</div>';
      return;
    }
    el.innerHTML = items.map(it => `
      <div class="trash-item" data-trash="${esc(it.trash_name)}">
        <div class="trash-item-info">
          <div class="trash-item-title">${esc(it.title)}</div>
          <div class="trash-item-meta">${esc(it.folder || '—')}</div>
        </div>
        <button class="trash-btn" onclick="restoreNote(this.closest('.trash-item').dataset.trash)">↩ Restaurar</button>
        <button class="trash-btn danger" onclick="purgeNote(this.closest('.trash-item').dataset.trash)">✕ Borrar</button>
      </div>`).join('');
  } catch(e) {
    document.getElementById('trash-list').innerHTML = '<div class="trash-empty">Error: ' + esc(e.message) + '</div>';
  }
}

function closeTrash() {
  document.getElementById('trash-overlay').classList.remove('open');
}

async function restoreNote(trashName) {
  const row = document.querySelector(`.trash-item[data-trash="${CSS.escape(trashName)}"]`);
  if (row) row.style.opacity = '.4';
  try {
    const r = await fetch(SERVER + '/trash/restore', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({trash_name: trashName}),
    });
    const d = await r.json();
    if (!r.ok) throw new Error(d.error);
    closeTrash();
    location.reload();
  } catch(e) {
    if (row) row.style.opacity = '';
    alert('Error al restaurar: ' + e.message);
  }
}

async function purgeNote(trashName) {
  if (!confirm('¿Eliminar permanentemente? Esta acción no se puede deshacer.')) return;
  const row = document.querySelector(`.trash-item[data-trash="${CSS.escape(trashName)}"]`);
  try {
    const r = await fetch(SERVER + '/trash/purge', {
      method: 'POST', headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({trash_name: trashName}),
    });
    if (!r.ok) throw new Error((await r.json()).error);
    if (row) row.remove();
    if (!document.querySelector('.trash-item')) {
      document.getElementById('trash-list').innerHTML = '<div class="trash-empty">La papelera está vacía.</div>';
    }
  } catch(e) {
    alert('Error: ' + e.message);
  }
}

// ── Duplicate detection ───────────────────────────────────────────
let _dupTimer = null;

function _scheduleDupCheck() {
  if (!semanticReady || !serverOnline) return;
  clearTimeout(_dupTimer);
  _dupTimer = setTimeout(_checkDuplicates, 700);
}

async function _checkDuplicates() {
  const title = document.getElementById('qc-title').value.trim();
  const body  = document.getElementById('qc-body').value.trim();
  const panel = document.getElementById('qc-dup-panel');
  if (!panel) return;

  const q = (title + ' ' + body).trim();
  if (q.length < 12) { panel.classList.remove('show'); return; }

  try {
    const r = await fetch(`${SERVER}/search?q=${encodeURIComponent(q.slice(0, 600))}&k=5`);
    const data = await r.json();
    if (!data.ready) return;

    const results = (data.results || []).filter(s => s.score >= 0.55).slice(0, 3);
    if (!results.length) { panel.classList.remove('show'); return; }

    const isDup     = results[0].score >= 0.80;
    const headerTxt = isDup ? '⚠️ Posible duplicado detectado' : '📎 Notas similares en el vault';
    const headerCls = isDup ? 'warn' : 'info';

    const items = results.map(s => {
      const n = DATA.notes.find(x => x.id === s.id);
      if (!n) return '';
      const fm  = FOLDER_META[n.folder];
      const col = fm?.color || 'var(--text-3)';
      const pct = Math.round(s.score * 100);
      return `<div class="qc-dup-item">
        <span class="backlink-dot" style="background:${col};flex-shrink:0"></span>
        <span class="qc-dup-title" title="${esc(n.title)}">${esc(n.title)}</span>
        <span class="qc-dup-score">${pct}%</span>
        <button class="qc-dup-open" onclick="closeQuickCapture();openNoteById(${n.id})">Abrir →</button>
      </div>`;
    }).join('');

    panel.innerHTML = `
      <div class="qc-dup-header ${headerCls}">${headerTxt}</div>
      ${items}`;
    panel.classList.add('show');

  } catch { panel.classList.remove('show'); }
}

// ── Plantillas ───────────────────────────────────────────────────
const TEMPLATES = [
  { label: 'Libre',     emoji: '📝', type: '',               body: '' },
  { label: 'Journal',   emoji: '📔', type: 'journal',
    body: '## Reflexión\n\n\n\n## Qué aprendí\n\n\n\n## Pendientes\n\n' },
  { label: 'Lección',   emoji: '💡', type: 'lesson-learned',
    body: '## Contexto\n\n\n\n## Qué pasó\n\n\n\n## Lección clave\n\n\n\n## Acción siguiente\n\n' },
  { label: 'Concepto',  emoji: '🧠', type: 'concept',
    body: '## Definición\n\n\n\n## Cómo funciona\n\n\n\n## Ejemplos\n\n\n\n## Ver también\n\n' },
  { label: 'Referencia',emoji: '📚', type: 'reference',
    body: '## Fuente\n\n\n\n## Puntos clave\n\n\n\n## Aplicaciones\n\n' },
  { label: 'Caso',      emoji: '🔍', type: 'case',
    body: '## Situación\n\n\n\n## Análisis\n\n\n\n## Conclusión\n\n' },
  { label: 'Reunión',   emoji: '🤝', type: 'capture',
    body: '## Participantes\n\n\n\n## Puntos tratados\n\n\n\n## Decisiones\n\n\n\n## Accionables\n\n' },
  { label: 'Pregunta',  emoji: '❓', type: 'question',
    body: '## Pregunta\n\n\n\n## Contexto\n\n\n\n## Hipótesis\n\n\n\n## Respuesta\n\n' },
];
let _activeTpl = 0;

function _buildTemplateRow() {
  const row = document.getElementById('qc-tpl-row');
  // Remove existing chips (keep the label)
  row.querySelectorAll('.tpl-chip').forEach(c => c.remove());
  TEMPLATES.forEach((t, i) => {
    const chip = document.createElement('button');
    chip.type = 'button';
    chip.className = 'tpl-chip' + (i === _activeTpl ? ' active' : '');
    chip.innerHTML = `${t.emoji} ${t.label}`;
    chip.onclick = () => _applyTemplate(i);
    row.appendChild(chip);
  });
}

function _applyTemplate(idx) {
  _activeTpl = idx;
  const t = TEMPLATES[idx];
  const bodyEl = document.getElementById('qc-body');
  // Only overwrite if empty or it was a template body (not user-typed)
  if (!bodyEl.value.trim() || bodyEl.dataset.fromTemplate === '1') {
    bodyEl.value = t.body;
    bodyEl.dataset.fromTemplate = t.body ? '1' : '0';
  }
  // Sync chip active state
  document.querySelectorAll('.tpl-chip').forEach((c, i) => {
    c.classList.toggle('active', i === idx);
  });
  bodyEl.focus();
  // Move cursor to first empty line inside template
  const firstBlank = t.body.indexOf('\n\n') + 2;
  if (firstBlank > 1) bodyEl.setSelectionRange(firstBlank, firstBlank);
}

// ── Quick capture ────────────────────────────────────────────────
function openQuickCapture() {
  document.getElementById('qc-overlay').classList.add('open');
  document.getElementById('qc-title').value = '';
  const bodyEl = document.getElementById('qc-body');
  bodyEl.value = '';
  bodyEl.dataset.fromTemplate = '0';
  document.getElementById('qc-status').textContent = '';
  document.getElementById('qc-save-btn').disabled = false;
  // Populate folder select from FOLDER_META
  const sel = document.getElementById('qc-folder');
  if (sel.options.length <= 1) {
    Object.entries(FOLDER_META).forEach(([key, meta]) => {
      const opt = document.createElement('option');
      opt.value = key;
      opt.textContent = meta.label + '  (' + key + ')';
      sel.appendChild(opt);
    });
  }
  sel.value = '';
  _activeTpl = 0;
  _buildTemplateRow();
  document.getElementById('qc-dup-panel').classList.remove('show');
  clearTimeout(_dupTimer);
  setTimeout(() => bodyEl.focus(), 50);
}

function closeQuickCapture() {
  document.getElementById('qc-overlay').classList.remove('open');
}

function qcKeydown(e) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
    e.preventDefault();
    submitQuickCapture();
    return;
  }
  // Mark body as user-typed so template switch won't overwrite it
  if (e.key.length === 1 || e.key === 'Backspace' || e.key === 'Delete') {
    e.target.dataset.fromTemplate = '0';
  }
}

async function submitQuickCapture() {
  const title = document.getElementById('qc-title').value.trim();
  const body  = document.getElementById('qc-body').value.trim();
  if (!body && !title) {
    document.getElementById('qc-status').textContent = '⚠️ Escribe algo primero.';
    return;
  }
  const btn = document.getElementById('qc-save-btn');
  const st  = document.getElementById('qc-status');
  btn.disabled = true;
  st.textContent = '⏳ Clasificando con IA…';
  try {
    const folder = document.getElementById('qc-folder').value || null;
    const res  = await fetch(SERVER + '/note/create', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({title, body, folder}),
    });
    const data = await res.json();
    if (!res.ok) throw new Error(data.error || res.statusText);
    st.textContent = `✓ Guardada en ${data.folder} — recargando…`;
    closeQuickCapture();
    location.href = location.pathname + (data.path ? '#open=' + encodeURIComponent(data.path) : '');
  } catch(err) {
    st.textContent = '❌ ' + err.message;
    btn.disabled = false;
  }
}

// ── Graph view ──────────────────────────────────────────────────
const FOLDER_COLORS = {
  '10-Work':                      '#5b6ef5',
  '20-Learning/CCA-F':            '#22d3ee',
  '20-Learning/PMI-ACP':          '#60a5fa',
  '20-Learning/AI-SDLC':          '#818cf8',
  '20-Learning/Cognitive-PM-AI':  '#fb923c',
  '20-Learning/Gemini-Enterprise': '#34d399',
  '20-Learning/Antigravity':      '#fbbf24',
  '20-Learning/Certifications':   '#a78bfa',
  '20-Learning/Coaching':         '#f472b6',
  '20-Learning/RPA':              '#2dd4bf',
  '20-Learning/Deep-Learning':    '#c084fc',
  '20-Learning/English-Grammar':  '#94a3b8',
  '40-Reference':                 '#fbbf24',
  '50-Archive':                   '#6b7280',
  'Journal':                      '#f87171',
};
const FOLDER_DISPLAY = {
  '10-Work':                      'Work & Projects',
  '20-Learning/CCA-F':            'CCA-F',
  '20-Learning/PMI-ACP':          'PMI-ACP',
  '20-Learning/AI-SDLC':          'AI & SDLC',
  '20-Learning/Cognitive-PM-AI':  'Cognitive PM AI',
  '20-Learning/Gemini-Enterprise': 'Gemini Enterprise',
  '20-Learning/Antigravity':      'Antigravity',
  '20-Learning/Certifications':   'Certifications',
  '20-Learning/Coaching':         'Coaching',
  '20-Learning/RPA':              'RPA',
  '20-Learning/Deep-Learning':    'Deep Learning',
  '20-Learning/English-Grammar':  'English',
  '40-Reference':                 'Reference',
  '50-Archive':                   'Archive',
  'Journal':                      'Journal',
};
const GRAPH_DEF_COLOR = '#94a3b8';

let _gNodes = null, _gEdges = null, _gClusters = {};
let _gAnimId = null, _gAlpha = 1;
let _gPan = {x:0,y:0}, _gZoom = 1;
let _gDrag = null, _gHovered = -1, _gFolderFilter = null;
let _gCanvas = null, _gCtx = null, _gW = 0, _gH = 0;

function _buildGraphData() {
  if (_gNodes) return;

  // Wikilink resolution: [[title]] → note id
  const titleMap = {};
  DATA.notes.forEach(n => { titleMap[n.title.trim().toLowerCase()] = n.id; });

  const wikiRe = /\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]/g;
  const edges = [], edgeSet = new Set();
  DATA.notes.forEach(note => {
    const body = note.body || '';
    let m; wikiRe.lastIndex = 0;
    while ((m = wikiRe.exec(body)) !== null) {
      const tid = titleMap[m[1].trim().toLowerCase()];
      if (tid !== undefined && tid !== note.id) {
        const ek = Math.min(note.id, tid) + '_' + Math.max(note.id, tid);
        if (!edgeSet.has(ek)) { edgeSet.add(ek); edges.push({s: note.id, t: tid}); }
      }
    }
  });

  const deg = {};
  DATA.notes.forEach(n => { deg[n.id] = 0; });
  edges.forEach(e => { deg[e.s]++; deg[e.t]++; });

  // Cluster centers in a circle
  const folders = [...new Set(DATA.notes.map(n => n.folder).filter(Boolean))].sort();
  const R = Math.max(200, folders.length * 33);
  _gClusters = {};
  folders.forEach((f, i) => {
    const ang = (2 * Math.PI * i / folders.length) - Math.PI / 2;
    _gClusters[f] = { x: Math.cos(ang) * R, y: Math.sin(ang) * R };
  });

  // Place nodes near their cluster center
  const idxMap = {};
  const nodes = DATA.notes.map((n, i) => {
    const c = _gClusters[n.folder] || {x:0,y:0};
    idxMap[n.id] = i;
    return {
      id: n.id, title: n.title, folder: n.folder || '',
      x: c.x + (Math.random()-.5)*40,
      y: c.y + (Math.random()-.5)*40,
      vx: 0, vy: 0, deg: deg[n.id]||0, r: 5,
    };
  });

  _gNodes = nodes;
  _gEdges = edges.map(e => ({si: idxMap[e.s], ti: idxMap[e.t]}));
}

// ── Kanban ────────────────────────────────────────────────────────

let _kProjects = (DATA.projects || []).map(p => JSON.parse(JSON.stringify(p)));
let _kActiveId = null;

function openKanban() {
  document.getElementById('kanban-overlay').classList.add('open');
  _renderKanbanSidebar();
  if (_kProjects.length) _kSelectProject(_kProjects[0].id);
}

function closeKanban() {
  document.getElementById('kanban-overlay').classList.remove('open');
}

function _renderKanbanSidebar() {
  const el = document.getElementById('kanban-sidebar');
  const statusLabel = { active: 'activo', in_progress: 'en progreso', done: 'completado', paused: 'pausado' };
  el.innerHTML = _kProjects.map(p => `
    <div class="kanban-proj-item${p.id === _kActiveId ? ' active' : ''}" onclick="_kSelectProject(${p.id})">
      ${esc(p.title)}
      <div class="kanban-proj-status">${statusLabel[p.status] || p.status} · ${_kTotalTasks(p)} tareas</div>
    </div>`).join('') +
    `<button class="kanban-new-proj" onclick="openKanbanNewProject()">+ Nuevo proyecto</button>`;
}

function _kTotalTasks(p) {
  return (p.tasks.backlog||[]).length + (p.tasks.in_progress||[]).length + (p.tasks.done||[]).length;
}

function _kSelectProject(id) {
  _kActiveId = id;
  _renderKanbanSidebar();
  _renderKanbanBoard();
}

function _renderKanbanBoard() {
  const p = _kProjects.find(x => x.id === _kActiveId);
  if (!p) return;
  const board = document.getElementById('kanban-board');
  const cols = [
    { key: 'backlog',     label: 'Backlog',      color: '#6b7280' },
    { key: 'in_progress', label: 'In Progress',  color: '#f59e0b' },
    { key: 'done',        label: 'Done',         color: '#34d399' },
  ];
  board.innerHTML = cols.map(col => {
    const tasks = p.tasks[col.key] || [];
    const cards = tasks.map((t, i) => {
      const moveLeft  = col.key !== 'backlog'     ? `<button class="kanban-move-btn" onclick="_kMoveTask(${p.id},'${col.key}',${i},'left')">← Atrás</button>` : '';
      const moveRight = col.key !== 'done'        ? `<button class="kanban-move-btn" onclick="_kMoveTask(${p.id},'${col.key}',${i},'right')">→ Adelante</button>` : '';
      const noteLink  = t.note ? `<div class="kanban-card-note" onclick="closeKanban();openNoteByPath('${esc(t.note)}')">📎 ${esc(t.note.split('/').pop())}</div>` : '';
      return `<div class="kanban-card${col.key==='done'?' done-card':''}">
        ${esc(t.text)}
        ${noteLink}
        <div class="kanban-card-actions">${moveLeft}${moveRight}
          <button class="kanban-move-btn" style="color:#f87171" onclick="_kDeleteTask(${p.id},'${col.key}',${i})">✕</button>
        </div>
      </div>`;
    }).join('');
    return `<div class="kanban-col">
      <div class="kanban-col-header" style="border-top:3px solid ${col.color}">
        ${col.label} <span class="kanban-col-count">${tasks.length}</span>
      </div>
      <div class="kanban-cards">${cards}</div>
      <button class="kanban-add-task" onclick="_kAddTask(${p.id},'${col.key}')">+ Agregar tarea</button>
    </div>`;
  }).join('');
}

const _COL_ORDER = ['backlog', 'in_progress', 'done'];

function _kMoveTask(projId, fromCol, taskIdx, dir) {
  const p = _kProjects.find(x => x.id === projId);
  if (!p) return;
  const fi = _COL_ORDER.indexOf(fromCol);
  const toCol = dir === 'right' ? _COL_ORDER[fi + 1] : _COL_ORDER[fi - 1];
  if (!toCol) return;
  const [task] = p.tasks[fromCol].splice(taskIdx, 1);
  task.done = toCol === 'done';
  p.tasks[toCol].push(task);
  _renderKanbanBoard();
  _kSaveProject(p);
}

function _kDeleteTask(projId, col, idx) {
  const p = _kProjects.find(x => x.id === projId);
  if (!p) return;
  p.tasks[col].splice(idx, 1);
  _renderKanbanBoard();
  _kSaveProject(p);
}

function _kAddTask(projId, col) {
  const text = prompt('Nueva tarea:');
  if (!text || !text.trim()) return;
  const p = _kProjects.find(x => x.id === projId);
  if (!p) return;
  p.tasks[col].push({ text: text.trim(), done: col === 'done', note: null });
  _renderKanbanBoard();
  _kSaveProject(p);
}

async function _kSaveProject(p) {
  if (!serverOnline) return;
  const cols = { backlog: '## Backlog', in_progress: '## In Progress', done: '## Done' };
  const fm = `---\ntitle: ${p.title}\ntype: project\nstatus: ${p.status}\ntags: [${p.tags.join(', ')}]\ncreated: ${p.created}\n---\n\n`;
  let body = '';
  for (const [key, header] of Object.entries(cols)) {
    body += header + '\n';
    for (const t of (p.tasks[key] || [])) {
      const check = t.done ? '[x]' : '[ ]';
      body += `- ${check} ${t.text}${t.note ? `\n  note: [[${t.note}]]` : ''}\n`;
    }
    body += '\n';
  }
  await fetch(`${SERVER}/note/save`, {
    method: 'POST', headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ path: p.path, content: fm + body })
  });
}

function openKanbanNewProject() {
  const title = prompt('Nombre del proyecto:');
  if (!title || !title.trim()) return;
  const slug = title.trim().toLowerCase().replace(/\s+/g, '-').replace(/[^a-z0-9-]/g, '');
  const newP = {
    id: _kProjects.length,
    title: title.trim(),
    status: 'active',
    tags: [],
    created: new Date().toISOString().slice(0, 10),
    path: `Kanban/${slug}.md`,
    tasks: { backlog: [], in_progress: [], done: [] }
  };
  _kProjects.push(newP);
  _kSaveProject(newP);
  _kSelectProject(newP.id);
}

function openNoteByPath(relPath) {
  const note = DATA.notes.find(n => n.path === relPath || n.path.endsWith(relPath));
  if (note) openNoteById(note.id);
}

function openGraph() {
  document.getElementById('graph-overlay').classList.add('open');
  _buildGraphData();
  _initGraphCanvas();
  _buildLegend();
}

function closeGraph() {
  document.getElementById('graph-overlay').classList.remove('open');
  if (_gAnimId) { cancelAnimationFrame(_gAnimId); _gAnimId = null; }
}

function _initGraphCanvas() {
  const wrap = document.getElementById('graph-canvas-wrap');
  const canvas = document.getElementById('graph-canvas');
  _gCanvas = canvas;
  _gW = wrap.clientWidth; _gH = wrap.clientHeight;
  const dpr = window.devicePixelRatio || 1;
  canvas.width  = _gW * dpr; canvas.height = _gH * dpr;
  canvas.style.width = _gW + 'px'; canvas.style.height = _gH + 'px';
  _gCtx = canvas.getContext('2d');
  _gCtx.scale(dpr, dpr);
  _gPan  = {x: _gW/2, y: _gH/2};
  _gZoom = Math.min(_gW, _gH) / 960;
  _gAlpha = 1; _gHovered = -1;

  document.getElementById('graph-subtitle').textContent =
    `${_gNodes.length} notas · ${_gEdges.length} conexiones de wikilinks`;

  _attachGraphEvents(canvas);
  _runGraphLoop();
}

function _runGraphLoop() {
  if (_gAnimId) cancelAnimationFrame(_gAnimId);
  const loop = () => {
    if (!document.getElementById('graph-overlay').classList.contains('open')) return;
    if (_gAlpha > 0.002) { _simStep(_gAlpha); _gAlpha *= 0.988; }
    _renderGraph();
    _gAnimId = requestAnimationFrame(loop);
  };
  _gAnimId = requestAnimationFrame(loop);
}

function _simStep(a) {
  const ns = _gNodes, es = _gEdges, N = ns.length;
  const REP=90, SPR=0.06, CLU=0.05, LEN=60, DAM=0.80;
  for (let i=0;i<N;i++){ns[i].fx=0;ns[i].fy=0;}

  // Repulsion O(n²) — 138 nodes is fine
  for (let i=0;i<N;i++) for (let j=i+1;j<N;j++) {
    const dx=ns[j].x-ns[i].x||.01, dy=ns[j].y-ns[i].y||.01;
    const d2=dx*dx+dy*dy||1, d=Math.sqrt(d2), f=REP/d2;
    const fx=dx/d*f, fy=dy/d*f;
    ns[i].fx-=fx; ns[i].fy-=fy; ns[j].fx+=fx; ns[j].fy+=fy;
  }

  // Wikilink springs
  for (const e of es) {
    const a2=ns[e.si], b=ns[e.ti];
    const dx=b.x-a2.x, dy=b.y-a2.y, d=Math.sqrt(dx*dx+dy*dy)||1;
    const f=(d-LEN)*SPR, fx=dx/d*f, fy=dy/d*f;
    a2.fx+=fx; a2.fy+=fy; b.fx-=fx; b.fy-=fy;
  }

  // Cluster gravity
  for (const n of ns) {
    const c=_gClusters[n.folder];
    if(c){n.fx+=(c.x-n.x)*CLU; n.fy+=(c.y-n.y)*CLU;}
  }

  // Integrate (skip pinned drag node)
  for (const n of ns) {
    if (_gDrag && n.id===_gDrag.id) continue;
    n.vx=(n.vx+n.fx*a)*DAM; n.vy=(n.vy+n.fy*a)*DAM;
    n.x+=n.vx; n.y+=n.vy;
  }
}

function _renderGraph() {
  const ctx=_gCtx, ns=_gNodes, es=_gEdges, W=_gW, H=_gH, z=_gZoom;
  ctx.clearRect(0,0,W,H);
  ctx.save();
  ctx.translate(_gPan.x,_gPan.y);
  ctx.scale(z,z);
  const fil=_gFolderFilter;

  // Wikilink edges
  for (const e of es) {
    const a=ns[e.si], b=ns[e.ti];
    const da=fil&&a.folder!==fil, db=fil&&b.folder!==fil;
    ctx.strokeStyle=`rgba(255,255,255,${da&&db?.03:da||db?.08:.30})`;
    ctx.lineWidth=1/z;
    ctx.beginPath(); ctx.moveTo(a.x,a.y); ctx.lineTo(b.x,b.y); ctx.stroke();
  }

  // Nodes
  for (let i=0;i<ns.length;i++) {
    const n=ns[i];
    const col=FOLDER_COLORS[n.folder]||GRAPH_DEF_COLOR;
    const dim=fil&&n.folder!==fil;
    const hov=i===_gHovered;
    const nr=hov?n.r*1.6:n.r;

    ctx.globalAlpha=dim?.2:1;
    ctx.beginPath(); ctx.arc(n.x,n.y,nr,0,Math.PI*2);
    ctx.fillStyle=dim?'#2a2a3a':col; ctx.fill();
    if(!dim){
      ctx.strokeStyle=hov?'rgba(255,255,255,.9)':'rgba(0,0,0,.35)';
      ctx.lineWidth=(hov?2:0.5)/z; ctx.stroke();
    }
    ctx.globalAlpha=1;

    // Labels: always at high zoom; always for hovered
    if (!dim && (hov || z>=0.85)) {
      const fs=Math.max(6,9/z);
      ctx.font=`${hov?600:400} ${fs}px system-ui,sans-serif`;
      ctx.fillStyle=hov?'#fff':'rgba(210,218,235,0.82)';
      ctx.textAlign='center'; ctx.textBaseline='top';
      const lab=n.title.length>24?n.title.slice(0,24)+'…':n.title;
      ctx.fillText(lab,n.x,n.y+nr+2/z);
    }
  }
  ctx.restore();
}

function _cToW(cx,cy){return{x:(cx-_gPan.x)/_gZoom,y:(cy-_gPan.y)/_gZoom};}

function _hitTest(wx,wy) {
  let best=-1, bestD=Infinity;
  const th=12/_gZoom;
  _gNodes.forEach((n,i)=>{
    const dx=n.x-wx,dy=n.y-wy,d=Math.sqrt(dx*dx+dy*dy);
    if(d<th&&d<bestD){best=i;bestD=d;}
  });
  return best;
}

function _attachGraphEvents(canvas) {
  const tooltip=document.getElementById('graph-tooltip');
  let panStart=null,dragInfo=null;

  const pos=e=>{const r=canvas.getBoundingClientRect();return{x:e.clientX-r.left,y:e.clientY-r.top};};

  canvas.addEventListener('mousedown',e=>{
    const p=pos(e),w=_cToW(p.x,p.y),hi=_hitTest(w.x,w.y);
    if(hi>=0){
      const n=_gNodes[hi];
      dragInfo={idx:hi,id:n.id,ox:w.x-n.x,oy:w.y-n.y,moved:false};
      _gDrag=n;
    } else {
      panStart={px:_gPan.x,py:_gPan.y,mx:p.x,my:p.y};
    }
  });

  canvas.addEventListener('mousemove',e=>{
    const p=pos(e),w=_cToW(p.x,p.y);
    if(dragInfo){
      dragInfo.moved=true;
      const n=_gNodes[dragInfo.idx];
      n.x=w.x-dragInfo.ox; n.y=w.y-dragInfo.oy; n.vx=0; n.vy=0;
      _gAlpha=Math.max(_gAlpha,0.3);
    } else if(panStart){
      _gPan.x=panStart.px+(p.x-panStart.mx);
      _gPan.y=panStart.py+(p.y-panStart.my);
    }
    const hi=_hitTest(w.x,w.y);
    _gHovered=hi;
    if(hi>=0){
      const n=_gNodes[hi];
      tooltip.style.cssText=`display:block;left:${p.x+16}px;top:${Math.max(4,p.y-10)}px`;
      tooltip.textContent=n.title+(n.folder?` · ${FOLDER_DISPLAY[n.folder]||n.folder}`:'');
    } else {
      tooltip.style.display='none';
    }
    canvas.style.cursor=hi>=0?'pointer':panStart?'grabbing':'grab';
  });

  canvas.addEventListener('mouseup',e=>{
    if(dragInfo&&!dragInfo.moved){
      const n=_gNodes[dragInfo.idx];
      closeGraph(); openNoteById(n.id);
    }
    dragInfo=null; _gDrag=null; panStart=null;
    canvas.style.cursor='grab';
  });

  canvas.addEventListener('mouseleave',()=>{
    dragInfo=null; _gDrag=null; panStart=null;
    _gHovered=-1; tooltip.style.display='none'; canvas.style.cursor='grab';
  });

  canvas.addEventListener('wheel',e=>{
    e.preventDefault();
    const p=pos(e),f=e.deltaY<0?1.12:0.89;
    _gPan.x=p.x+(_gPan.x-p.x)*f; _gPan.y=p.y+(_gPan.y-p.y)*f;
    _gZoom=Math.max(0.1,Math.min(6,_gZoom*f));
  },{passive:false});
}

function graphZoomBy(factor) {
  const cx=_gW/2,cy=_gH/2;
  _gPan.x=cx+(_gPan.x-cx)*factor; _gPan.y=cy+(_gPan.y-cy)*factor;
  _gZoom=Math.max(0.1,Math.min(6,_gZoom*factor));
}

function resetGraphView() {
  _gPan={x:_gW/2,y:_gH/2};
  _gZoom=Math.min(_gW,_gH)/960;
  _gFolderFilter=null;
  document.querySelectorAll('.graph-legend-item').forEach(el=>el.classList.remove('dimmed'));
  _gAlpha=0.5;
}

function _buildLegend() {
  const legend=document.getElementById('graph-legend');
  legend.innerHTML='';
  const folders=[...new Set(_gNodes.map(n=>n.folder).filter(Boolean))].sort();
  folders.forEach(f=>{
    const col=FOLDER_COLORS[f]||GRAPH_DEF_COLOR;
    const cnt=_gNodes.filter(n=>n.folder===f).length;
    const el=document.createElement('div');
    el.className='graph-legend-item'; el.dataset.folder=f;
    el.innerHTML=`<span class="graph-legend-dot" style="background:${col}"></span><span>${FOLDER_DISPLAY[f]||f}</span><span style="margin-left:auto;padding-left:8px;color:#4b5563">${cnt}</span>`;
    el.onclick=()=>{
      _gFolderFilter=_gFolderFilter===f?null:f;
      document.querySelectorAll('.graph-legend-item').forEach(li=>
        li.classList.toggle('dimmed',!!_gFolderFilter&&li.dataset.folder!==_gFolderFilter));
    };
    legend.appendChild(el);
  });
}

// ── Related notes ─────────────────────────────────────────────────
async function loadRelatedNotes(id) {
  const el = document.getElementById('related-section');
  if (!el) return;

  const note = DATA.notes.find(n => n.id === id);
  if (!note) { el.innerHTML = ''; return; }

  const q = (note.title + ' ' + (note.body || '')).slice(0, 800);

  try {
    const r = await fetch(`${SERVER}/search?q=${encodeURIComponent(q)}&k=10`);
    const data = await r.json();
    if (!data.ready) { el.innerHTML = ''; return; }

    const results = (data.results || [])
      .filter(s => s.id !== id && s.score > 0.28)
      .slice(0, 5);

    if (!results.length) { el.innerHTML = ''; return; }

    const chips = results.map(s => {
      const n   = DATA.notes.find(x => x.id === s.id);
      if (!n) return '';
      const fm  = FOLDER_META[n.folder];
      const col = fm?.color || 'var(--text-3)';
      const lbl = fm?.label || n.folder;
      const pct = Math.round(s.score * 100);
      return `<button class="backlink-chip" onclick="openNoteById(${n.id})">
        <span class="backlink-dot" style="background:${col}"></span>
        <span class="backlink-title">${esc(n.title)}</span>
        <span class="backlink-folder">${esc(lbl)}</span>
        <span style="font-size:10px;color:var(--text-3);font-family:var(--mono);flex-shrink:0;margin-left:4px">${pct}%</span>
      </button>`;
    }).join('');

    el.innerHTML = `
      <div class="backlinks-label">relacionadas · ${results.length} notas similares</div>
      <div class="backlinks-list">${chips}</div>`;

  } catch { el.innerHTML = ''; }
}

// ── Stats panel ──────────────────────────────────────────────────
function openStats() {
  document.getElementById('stats-overlay').classList.add('open');
  buildStats();
}

function closeStats() {
  document.getElementById('stats-overlay').classList.remove('open');
}

function buildStats() {
  const notes = DATA.notes;
  const total = notes.length;
  if (!total) {
    document.getElementById('stats-body').innerHTML =
      '<div style="color:var(--text-3);font-size:13px;text-align:center;padding:40px">Sin notas aún.</div>';
    return;
  }

  // Connection stats
  const connected = notes.filter(n => {
    const hasOut = /\[\[/.test(n.body || '');
    const hasIn  = (backlinksIndex[n.id] || []).length > 0;
    return hasOut || hasIn;
  }).length;
  const connPct = Math.round(connected / total * 100);
  const withTags = notes.filter(n => n.tags && n.tags.length > 0).length;
  const tagsPct  = Math.round(withTags / total * 100);
  const withType = notes.filter(n => n.type).length;
  const typePct  = Math.round(withType / total * 100);
  const healthScore = Math.round((connPct + tagsPct + typePct) / 3);
  const healthColor = healthScore >= 70 ? '#34d399' : healthScore >= 40 ? '#fbbf24' : '#f87171';

  // Total wikilinks count
  let totalLinks = 0;
  notes.forEach(n => {
    const m = (n.body || '').match(/\[\[/g);
    if (m) totalLinks += m.length;
  });
  const avgLinks = (totalLinks / total).toFixed(1);

  // By folder
  const byFolder = Object.entries(DATA.stats.by_folder).sort((a, b) => b[1] - a[1]);
  const maxF = byFolder[0]?.[1] || 1;

  // By month
  const byMonth = {};
  notes.forEach(n => {
    const key = n.date.slice(0, 7);
    byMonth[key] = (byMonth[key] || 0) + 1;
  });
  const months = Object.entries(byMonth).sort((a, b) => a[0].localeCompare(b[0])).slice(-18);
  const maxM = Math.max(...months.map(m => m[1]), 1);
  const mostActive = months.reduce((best, m) => m[1] > best[1] ? m : best, ['', 0]);
  const mostActiveLabel = mostActive[0]
    ? new Date(mostActive[0] + '-15').toLocaleString('es', { month: 'long', year: 'numeric' })
    : '—';

  // By type
  const byType = {};
  notes.forEach(n => { if (n.type) byType[n.type] = (byType[n.type] || 0) + 1; });
  const sortedTypes = Object.entries(byType).sort((a, b) => b[1] - a[1]);
  const maxT = sortedTypes[0]?.[1] || 1;

  // Tags
  const byTag = {};
  notes.forEach(n => (n.tags || []).forEach(t => { byTag[t] = (byTag[t] || 0) + 1; }));
  const topTags = Object.entries(byTag).sort((a, b) => b[1] - a[1]).slice(0, 10);
  const maxTag = topTags[0]?.[1] || 1;

  // ── Render ──
  const tiles = `<div class="stats-tiles">
    <div class="stats-tile accent">
      <div class="stats-tile-val">${total}</div>
      <div class="stats-tile-lbl">notas totales</div>
    </div>
    <div class="stats-tile">
      <div class="stats-tile-val">${connPct}%</div>
      <div class="stats-tile-lbl">conectadas</div>
    </div>
    <div class="stats-tile">
      <div class="stats-tile-val">${avgLinks}</div>
      <div class="stats-tile-lbl">links / nota (avg)</div>
    </div>
    <div class="stats-tile">
      <div class="stats-tile-val" style="color:${healthColor}">${healthScore}</div>
      <div class="stats-tile-lbl">health score</div>
    </div>
  </div>`;

  const actBars = months.map(([key, count]) => {
    const h   = Math.max(4, Math.round((count / maxM) * 56));
    const d   = new Date(key + '-15');
    const lbl = d.toLocaleString('es', { month: 'short' }).slice(0, 3) + "'" + String(d.getFullYear()).slice(2);
    return `<div class="stats-act-col">
      <div class="stats-act-bar" style="height:${h}px" title="${count} notas — ${key}"></div>
      <div class="stats-act-lbl">${lbl}</div>
    </div>`;
  }).join('');

  const folderBars = byFolder.map(([key, count]) => {
    const fm    = FOLDER_META[key];
    const color = fm?.color || 'var(--accent)';
    const label = fm?.label || key || '(raíz)';
    const pct   = Math.round(count / maxF * 100);
    return `<div class="stats-bar-row">
      <div class="stats-bar-label" title="${esc(key)}">${esc(label)}</div>
      <div class="stats-bar-track"><div class="stats-bar-fill" style="width:${pct}%;background:${color}"></div></div>
      <div class="stats-bar-count">${count}</div>
    </div>`;
  }).join('');

  const typeBars = sortedTypes.length
    ? sortedTypes.map(([type, count]) => {
        const pct = Math.round(count / maxT * 100);
        return `<div class="stats-bar-row">
          <div class="stats-bar-label">${esc(type)}</div>
          <div class="stats-bar-track"><div class="stats-bar-fill" style="width:${pct}%;background:var(--accent)"></div></div>
          <div class="stats-bar-count">${count}</div>
        </div>`;
      }).join('')
    : '<div style="color:var(--text-3);font-size:12px;font-style:italic">Sin tipos asignados.</div>';

  const tagBars = topTags.length
    ? topTags.map(([tag, count]) => {
        const pct = Math.round(count / maxTag * 100);
        return `<div class="stats-bar-row">
          <div class="stats-bar-label">#${esc(tag)}</div>
          <div class="stats-bar-track"><div class="stats-bar-fill" style="width:${pct}%;background:#818cf8"></div></div>
          <div class="stats-bar-count">${count}</div>
        </div>`;
      }).join('')
    : '<div style="color:var(--text-3);font-size:12px;font-style:italic">Sin tags.</div>';

  const healthRows = [
    { label: 'Notas enlazadas',  pct: connPct, color: '#34d399' },
    { label: 'Notas con tags',   pct: tagsPct, color: '#818cf8' },
    { label: 'Notas con tipo',   pct: typePct, color: '#fb923c' },
  ].map(r => `<div class="stats-bar-row">
    <div class="stats-bar-label">${r.label}</div>
    <div class="stats-bar-track"><div class="stats-bar-fill" style="width:${r.pct}%;background:${r.color}"></div></div>
    <div class="stats-bar-count">${r.pct}%</div>
  </div>`).join('');

  document.getElementById('stats-body').innerHTML = `
    ${tiles}
    <div>
      <div class="stats-section-title">Actividad — ${months.length} meses · pico: ${mostActiveLabel}</div>
      <div class="stats-activity">${actBars}</div>
    </div>
    <div>
      <div class="stats-section-title">Notas por carpeta</div>
      ${folderBars}
    </div>
    <div class="stats-two-col">
      <div>
        <div class="stats-section-title">Tipos</div>
        ${typeBars}
      </div>
      <div>
        <div class="stats-section-title">Top tags</div>
        ${tagBars}
      </div>
    </div>
    <div>
      <div class="stats-section-title">Salud del vault · score ${healthScore}/100</div>
      ${healthRows}
    </div>`;
}

// ── Server detection ───────────────────────────────────────────
const SERVER = (location.hostname === 'localhost' || location.hostname === '127.0.0.1')
  ? 'http://127.0.0.1:5000'
  : `${location.protocol}//${location.hostname}:5000`;
let serverOnline = false;

async function checkServer() {
  try {
    const r = await fetch(SERVER + '/embed/status', { method: 'GET', signal: AbortSignal.timeout(800) });
    serverOnline = r.ok || r.status < 500;
  } catch {
    serverOnline = false;
  }
  // Capture button
  const btn = document.getElementById('capture-btn');
  if (serverOnline) {
    btn.classList.remove('offline');
    btn.title = 'Capturar foto / subir archivo';
  } else {
    btn.classList.add('offline');
    btn.title = 'Servidor offline — corre: python kb_server.py';
  }
  // Show/hide edit buttons based on server availability
  document.querySelectorAll('[data-edit]').forEach(el => {
    el.style.display = serverOnline ? '' : 'none';
  });
  // Status indicator
  const ind = document.getElementById('server-indicator');
  const lbl = document.getElementById('server-label');
  if (ind && lbl) {
    ind.classList.toggle('online',  serverOnline);
    ind.classList.toggle('offline', !serverOnline);
    lbl.textContent = serverOnline ? 'online' : 'offline';
    ind.title = serverOnline
      ? 'Servidor corriendo en localhost:5000'
      : 'Servidor offline — ejecuta: python kb_server.py';
  }
}
// Poll every 10 seconds
setInterval(checkServer, 10_000);

// ── Quick switcher (Ctrl+K) ──────────────────────────────────────
let _qsIdx = 0;
let _qsResults = [];

function openQS() {
  document.getElementById('qs-overlay').classList.add('open');
  const inp = document.getElementById('qs-input');
  inp.value = '';
  _qsIdx = 0;
  renderQS();
  setTimeout(() => inp.focus(), 30);
}
function closeQS() {
  document.getElementById('qs-overlay').classList.remove('open');
}
function renderQS() {
  const q = document.getElementById('qs-input').value.trim().toLowerCase();
  _qsResults = q
    ? DATA.notes.filter(n => n.title.toLowerCase().includes(q) || (n.folder || '').toLowerCase().includes(q)).slice(0, 12)
    : DATA.notes.slice().sort((a, b) => (b.date || '').localeCompare(a.date || '')).slice(0, 12);
  _qsIdx = 0;
  const list = document.getElementById('qs-list');
  if (!_qsResults.length) {
    list.innerHTML = '<div class="qs-empty">Sin resultados</div>';
    return;
  }
  list.innerHTML = _qsResults.map((n, i) => {
    const meta = Object.values(FOLDER_META).find(m => n.folder && n.folder.startsWith(Object.keys(FOLDER_META).find(k => n.folder.startsWith(k)) || '')) || {};
    const color = meta.color || '#6b7280';
    return `<div class="qs-item${i === 0 ? ' active' : ''}" onclick="closeQS();openNoteById(${n.id})" data-qi="${i}">
      <span class="qs-item-dot" style="background:${color}"></span>
      <span class="qs-item-title">${esc(n.title)}</span>
      <span class="qs-item-folder">${esc((n.folder || '').split('/').pop())}</span>
    </div>`;
  }).join('');
}
function qsKeydown(e) {
  const items = document.querySelectorAll('.qs-item');
  if (e.key === 'ArrowDown') { e.preventDefault(); _qsIdx = Math.min(_qsIdx + 1, items.length - 1); }
  else if (e.key === 'ArrowUp') { e.preventDefault(); _qsIdx = Math.max(_qsIdx - 1, 0); }
  else if (e.key === 'Enter') { e.preventDefault(); if (_qsResults[_qsIdx]) { closeQS(); openNoteById(_qsResults[_qsIdx].id); } return; }
  else if (e.key === 'Escape') { closeQS(); return; }
  items.forEach((el, i) => el.classList.toggle('active', i === _qsIdx));
  if (items[_qsIdx]) items[_qsIdx].scrollIntoView({ block: 'nearest' });
}

// ── Feed keyboard navigation ─────────────────────────────────────
let _feedIdx = -1;
function _feedItems() { return [...document.querySelectorAll('.note-row')]; }
function _feedSelect(idx) {
  const items = _feedItems();
  if (!items.length) return;
  _feedIdx = Math.max(0, Math.min(idx, items.length - 1));
  items.forEach((el, i) => el.classList.toggle('kb-selected', i === _feedIdx));
  items[_feedIdx]?.scrollIntoView({ block: 'nearest' });
}

// ── Global keyboard shortcuts ────────────────────────────────────
function _anyModalOpen() {
  return ['qs-overlay','chat-overlay','stats-overlay','graph-overlay','editor-overlay']
    .some(id => document.getElementById(id)?.classList.contains('open'))
    || document.getElementById('upload-modal')?.style.display !== 'none'
    || document.getElementById('qc-overlay')?.style.display !== 'none'
    || document.getElementById('trash-overlay')?.style.display !== 'none';
}

document.addEventListener('keydown', e => {
  const tag = document.activeElement?.tagName;
  const inInput = tag === 'INPUT' || tag === 'TEXTAREA' || document.activeElement?.isContentEditable;

  // Ctrl/Cmd combos — fire even from inputs (except editor Ctrl+S already handled)
  if (e.ctrlKey || e.metaKey) {
    switch (e.key.toLowerCase()) {
      case 'k': e.preventDefault(); closeQS(); if (!document.getElementById('qs-overlay').classList.contains('open')) openQS(); return;
      case 'n': if (!inInput) { e.preventDefault(); openQuickCapture(); } return;
      case 'f': if (!inInput) { e.preventDefault(); document.getElementById('search')?.focus(); } return;
      case 'g': if (!inInput) { e.preventDefault(); openGraph(); } return;
      case 'p': if (!inInput) { e.preventDefault(); openKanban(); } return;
      case 'd': if (!inInput) { e.preventDefault(); _openDailyNote(); } return;
      case '\\': e.preventDefault(); toggleSidebar(); return;
      case 't': if (e.shiftKey) { e.preventDefault(); toggleTheme(); } return;
    }
    if (e.key === '|' || (e.shiftKey && e.key === '\\')) { e.preventDefault(); toggleList(); return; }
    if (e.shiftKey && e.key.toLowerCase() === 's') { e.preventDefault(); openStats(); return; }
  }

  // Single-key shortcuts — only when not typing and no modal open
  if (inInput || _anyModalOpen()) return;

  switch (e.key) {
    case 'e': case 'E':
      if (activeNoteId != null) { e.preventDefault(); openEditor(activeNoteId); }
      break;
    case 's': case 'S':
      if (activeNoteId != null) { e.preventDefault(); toggleStar(activeNoteId); }
      break;
    case 'Escape':
      closeDetail();
      break;
    case 'ArrowDown':
      e.preventDefault(); _feedSelect(_feedIdx + 1);
      break;
    case 'ArrowUp':
      e.preventDefault(); _feedSelect(_feedIdx - 1);
      break;
    case 'Enter':
      if (_feedIdx >= 0) {
        const items = _feedItems();
        if (items[_feedIdx]) items[_feedIdx].click();
      }
      break;
  }
});

// ── Daily note ───────────────────────────────────────────────────
function _openDailyNote() {
  const today = new Date().toISOString().slice(0, 10);
  const existing = DATA.notes.find(n => n.type === 'journal' && n.date === today);
  if (existing) { openNoteById(existing.id); return; }
  // Pre-fill Quick Capture as journal for today
  openQuickCapture();
  setTimeout(() => {
    const tpl = TEMPLATES.findIndex(t => t.label === 'Journal');
    if (tpl >= 0) _applyTemplate(tpl);
    const titleEl = document.getElementById('qc-title');
    if (titleEl) titleEl.value = `Journal ${today}`;
  }, 80);
}

// ── Capture modal ───────────────────────────────────────────────
function openCapture() {
  if (!serverOnline) {
    alert('El servidor no está corriendo.\nEjecuta:  python kb_server.py\nLuego abre http://localhost:5000');
    return;
  }
  document.getElementById('upload-modal').style.display = '';
  document.getElementById('pipeline-log').style.display = 'none';
  document.getElementById('pipeline-log').innerHTML = '';
}

function closeCapture() {
  document.getElementById('upload-modal').style.display = 'none';
}

function triggerCamera(mode) {
  const inp = document.getElementById('file-input');
  if (mode === 'capture') {
    inp.setAttribute('capture', 'environment');
  } else {
    inp.removeAttribute('capture');
  }
  inp.click();
}

function handleFileSelect(e) {
  const file = e.target.files[0];
  if (file) uploadFile(file);
}

// Drag & drop
const dz = document.getElementById('drop-zone');
dz.addEventListener('dragover', e => { e.preventDefault(); dz.classList.add('dragover'); });
dz.addEventListener('dragleave', () => dz.classList.remove('dragover'));
dz.addEventListener('drop', e => {
  e.preventDefault();
  dz.classList.remove('dragover');
  const file = e.dataTransfer.files[0];
  if (file) uploadFile(file);
});

async function uploadFile(file) {
  const log = document.getElementById('pipeline-log');
  log.style.display = '';
  log.innerHTML = `<div>Subiendo: <strong>${file.name}</strong> (${(file.size/1024).toFixed(1)} KB)…</div>`;

  const fd = new FormData();
  fd.append('file', file);

  try {
    const r = await fetch(SERVER + '/upload', { method: 'POST', body: fd });
    const data = await r.json();
    if (!r.ok) { log.innerHTML += `<div class="log-error">Error: ${data.error}</div>`; return; }
    log.innerHTML += `<div>Pipeline iniciado — ${data.file}</div>`;
    subscribeStatus(log);
  } catch (err) {
    log.innerHTML += `<div class="log-error">${err.message}</div>`;
  }
}

function subscribeStatus(log) {
  const es = new EventSource(SERVER + '/status');
  es.onmessage = e => {
    const ev = JSON.parse(e.data);
    const cls = ev.type === 'done' ? 'log-done' : ev.type === 'error' ? 'log-error' : '';
    log.innerHTML += `<div class="${cls}">${ev.msg}</div>`;
    log.scrollTop = log.scrollHeight;
    if (ev.type === 'done' || ev.type === 'error') {
      es.close();
      if (ev.type === 'done') {
        setTimeout(() => { closeCapture(); location.reload(); }, 2000);
      }
    }
  };
  es.onerror = () => es.close();
}

// ── Editor ──────────────────────────────────────────────────────
let editingNoteId = null;

async function openEditor(id) {
  if (!serverOnline) return;
  const note = DATA.notes.find(n => n.id === id);
  if (!note) return;
  editingNoteId = id;

  document.getElementById('editor-note-title').textContent = note.title;
  document.getElementById('editor-status').textContent = 'cargando…';
  document.getElementById('editor-save-btn').disabled = true;
  document.getElementById('editor-overlay').style.display = '';

  try {
    const r = await fetch(SERVER + '/note/read?path=' + encodeURIComponent(note.path));
    const data = await r.json();
    if (!r.ok) throw new Error(data.error);
    document.getElementById('editor-textarea').value = data.content;
    document.getElementById('editor-status').textContent = 'listo';
    document.getElementById('editor-save-btn').disabled = false;
  } catch (err) {
    document.getElementById('editor-status').textContent = 'Error: ' + err.message;
  }
}

function closeEditor() {
  document.getElementById('editor-overlay').style.display = 'none';
  editingNoteId = null;
}

async function saveNote() {
  if (editingNoteId === null) return;
  const note  = DATA.notes.find(n => n.id === editingNoteId);
  const content = document.getElementById('editor-textarea').value;
  const btn   = document.getElementById('editor-save-btn');
  const status = document.getElementById('editor-status');

  btn.disabled = true;
  status.textContent = 'guardando…';

  try {
    const r = await fetch(SERVER + '/note/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ path: note.path, content }),
    });
    const data = await r.json();
    if (!r.ok) throw new Error(data.error);
    status.textContent = '✓ guardado';
    btn.disabled = false;
    // Update the note body in memory so viewer reflects changes
    const m = content.match(/^---\s*\n[\s\S]*?\n---\s*\n([\s\S]*)$/);
    note.body = m ? m[1].trim() : content.trim();
    if (activeNoteId === editingNoteId) openNoteById(editingNoteId);
  } catch (err) {
    status.textContent = 'Error: ' + err.message;
    btn.disabled = false;
  }
}

// Ctrl+S in editor
document.getElementById('editor-textarea').addEventListener('keydown', e => {
  if ((e.ctrlKey || e.metaKey) && e.key === 's') { e.preventDefault(); saveNote(); }
});

// ── Move note ────────────────────────────────────────────────────
async function moveNote(id, newFolder, selectEl) {
  const note = DATA.notes.find(n => n.id === id);
  if (!note || newFolder === note.folder) return;
  const prev = note.folder;
  selectEl.disabled = true;
  try {
    const r = await fetch(SERVER + '/note/move', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({path: note.path, folder: newFolder}),
    });
    const d = await r.json();
    if (!r.ok) throw new Error(d.error || r.statusText);
    location.reload();
  } catch(e) {
    alert('Error al mover: ' + e.message);
    selectEl.value = prev;
    selectEl.disabled = false;
  }
}

// ── Delete note ─────────────────────────────────────────────────
async function deleteNote(id) {
  const note = DATA.notes.find(n => n.id === id);
  if (!note) return;
  if (!confirm(`¿Eliminar "${note.title}"?\n\nEsta acción no se puede deshacer.`)) return;
  try {
    const r = await fetch(SERVER + '/note/delete', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({path: note.path}),
    });
    const data = await r.json();
    if (!r.ok) throw new Error(data.error || r.statusText);
    closeDetail();
    location.reload();
  } catch(err) {
    alert('Error al borrar: ' + err.message);
  }
}

// ── Link suggestions ────────────────────────────────────────────
let _lsNoteId = null;

async function openLinkSuggest(id) {
  if (!serverOnline) { alert('El servidor no está corriendo.'); return; }
  if (!semanticReady) { alert('Los embeddings no están listos. Corre: python build_embeddings.py'); return; }

  _lsNoteId = id;
  const note = DATA.notes.find(n => n.id === id);
  if (!note) return;

  // Remove existing panel if open
  const existing = document.getElementById('link-suggest-panel');
  if (existing) existing.remove();

  // Build query from title + body
  const q = (note.title + ' ' + (note.body || '')).slice(0, 600);

  // Parse already-linked notes in this note's body
  const alreadyLinked = new Set();
  const wikiRe = /\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]/g;
  const titleMap = {};
  DATA.notes.forEach(n => { titleMap[n.title.trim().toLowerCase()] = n.id; });
  let m; wikiRe.lastIndex = 0;
  while ((m = wikiRe.exec(note.body || '')) !== null) {
    const tid = titleMap[m[1].trim().toLowerCase()];
    if (tid !== undefined) alreadyLinked.add(tid);
  }

  // Inject loading state panel
  const inner = document.getElementById('detail-inner');
  const bodyEl = inner.querySelector('.note-body');
  const panel = document.createElement('div');
  panel.id = 'link-suggest-panel';
  panel.className = 'link-suggest-panel';
  panel.innerHTML = `
    <div class="link-suggest-header">
      <span class="link-suggest-title">🔗 Buscando notas relacionadas…</span>
      <button class="link-suggest-close" onclick="closeLinkSuggest()">✕</button>
    </div>
    <div class="link-suggest-list" style="padding:12px 14px;color:var(--text-3);font-size:12px">Consultando embeddings…</div>`;
  inner.insertBefore(panel, bodyEl);

  try {
    const r = await fetch(`${SERVER}/search?q=${encodeURIComponent(q)}&k=12`);
    const data = await r.json();
    if (!r.ok) throw new Error(data.error);

    // Filter: remove self, already linked, low scores
    const suggestions = (data.results || [])
      .filter(s => s.id !== id && !alreadyLinked.has(s.id) && s.score > 0.2)
      .slice(0, 8);

    _renderLinkSuggestPanel(panel, suggestions);
  } catch (err) {
    panel.querySelector('.link-suggest-list').innerHTML =
      `<div style="padding:12px 14px;color:#f87171;font-size:12px">Error: ${esc(err.message)}</div>`;
  }
}

function _renderLinkSuggestPanel(panel, suggestions) {
  if (suggestions.length === 0) {
    panel.innerHTML = `
      <div class="link-suggest-header">
        <span class="link-suggest-title">🔗 Sugerencias de links</span>
        <button class="link-suggest-close" onclick="closeLinkSuggest()">✕</button>
      </div>
      <div class="link-suggest-list" style="padding:12px 14px;color:var(--text-3);font-size:12px;font-style:italic">
        No se encontraron notas nuevas para enlazar con suficiente similitud.
      </div>`;
    return;
  }

  const items = suggestions.map(s => {
    const n   = DATA.notes.find(x => x.id === s.id);
    if (!n) return '';
    const fm  = FOLDER_META[n.folder];
    const col = fm?.color || 'var(--text-3)';
    const lbl = fm?.label || n.folder;
    const pct = Math.round(s.score * 100);
    return `<label class="link-suggest-item">
      <input type="checkbox" data-note-id="${n.id}" data-note-title="${esc(n.title)}">
      <span class="link-suggest-dot" style="background:${col}"></span>
      <span class="link-suggest-name">${esc(n.title)}</span>
      <span class="link-suggest-folder">${esc(lbl)}</span>
      <span class="link-suggest-score">${pct}%</span>
    </label>`;
  }).join('');

  panel.innerHTML = `
    <div class="link-suggest-header">
      <span class="link-suggest-title">🔗 Sugerencias de links · ${suggestions.length} notas relacionadas</span>
      <button class="link-suggest-close" onclick="closeLinkSuggest()">✕</button>
    </div>
    <div class="link-suggest-list">${items}</div>
    <div class="link-suggest-footer">
      <button class="link-suggest-apply" id="ls-apply-btn" onclick="applyLinkSuggestions()" disabled>Insertar seleccionados</button>
      <span class="link-suggest-hint">Se agregan bajo ## Ver también al final de la nota</span>
    </div>`;

  // Enable apply button when at least 1 checkbox is checked
  panel.querySelectorAll('input[type=checkbox]').forEach(cb => {
    cb.addEventListener('change', () => {
      const anyChecked = panel.querySelectorAll('input[type=checkbox]:checked').length > 0;
      document.getElementById('ls-apply-btn').disabled = !anyChecked;
    });
  });
}

async function applyLinkSuggestions() {
  const id = _lsNoteId;
  if (id === null) return;
  const note = DATA.notes.find(n => n.id === id);
  if (!note) return;

  const panel = document.getElementById('link-suggest-panel');
  const checked = [...panel.querySelectorAll('input[type=checkbox]:checked')];
  if (!checked.length) return;

  const titles = checked.map(cb => cb.dataset.noteTitle);

  // Fetch raw note content
  const r = await fetch(SERVER + '/note/read?path=' + encodeURIComponent(note.path));
  const data = await r.json();
  if (!r.ok) { alert('Error leyendo nota: ' + data.error); return; }

  let content = data.content;

  // Check if "Ver también" section already exists
  const seeAlsoRe = /^##\s*Ver también\s*$/im;
  const newLinks  = titles.map(t => `- [[${t}]]`).join('\n');

  if (seeAlsoRe.test(content)) {
    // Append after existing section
    content = content.replace(seeAlsoRe, match => match + '\n' + newLinks);
  } else {
    // Add new section at the end
    content = content.trimEnd() + '\n\n## Ver también\n' + newLinks + '\n';
  }

  // Load into editor
  editingNoteId = id;
  document.getElementById('editor-note-title').textContent = note.title;
  document.getElementById('editor-status').textContent = 'listo';
  document.getElementById('editor-save-btn').disabled = false;
  document.getElementById('editor-textarea').value = content;
  document.getElementById('editor-overlay').style.display = '';

  // Scroll textarea to bottom so user sees inserted links
  const ta = document.getElementById('editor-textarea');
  ta.scrollTop = ta.scrollHeight;

  closeLinkSuggest();
}

function closeLinkSuggest() {
  const panel = document.getElementById('link-suggest-panel');
  if (panel) panel.remove();
  _lsNoteId = null;
}

// ── Backlinks index ─────────────────────────────────────────────
// backlinksIndex[noteId] = [{id, title, folder}, ...] of notes that link HERE
const backlinksIndex = {};

// ── Orphan notes ─────────────────────────────────────────────────
const wikiRe = /\[\[([^\]]+)\]\]/g;

function isOrphan(note) {
  const hasBacklinks = (backlinksIndex[note.id] || []).length > 0;
  const hasOutgoing  = wikiRe.test(note.body || '');
  wikiRe.lastIndex   = 0;
  return !hasBacklinks && !hasOutgoing;
}

function toggleOrphan() {
  activeOrphan = !activeOrphan;
  if (activeOrphan) { activeFolder = null; activeTag = null; activeType = null; }
  document.getElementById('orphan-btn').classList.toggle('active', activeOrphan);
  document.querySelectorAll('#folder-nav .folder-btn').forEach(b => b.classList.remove('active'));
  if (!activeOrphan) {
    const allBtn = document.querySelector('#folder-nav .folder-btn');
    if (allBtn) allBtn.classList.add('active');
  }
  refreshAll();
}

function updateOrphanCount() {
  const count = DATA.notes.filter(isOrphan).length;
  document.getElementById('orphan-count').textContent = count;
}

function buildBacklinksIndex() {
  const titleMap = {};
  DATA.notes.forEach(n => { titleMap[n.title.trim().toLowerCase()] = n.id; });

  const wikiRe = /\[\[([^\]|#]+)(?:[|#][^\]]+)?\]\]/g;
  DATA.notes.forEach(note => {
    const body = note.body || '';
    let m; wikiRe.lastIndex = 0;
    while ((m = wikiRe.exec(body)) !== null) {
      const tid = titleMap[m[1].trim().toLowerCase()];
      if (tid !== undefined && tid !== note.id) {
        if (!backlinksIndex[tid]) backlinksIndex[tid] = [];
        if (!backlinksIndex[tid].find(b => b.id === note.id)) {
          backlinksIndex[tid].push({ id: note.id, title: note.title, folder: note.folder });
        }
      }
    }
  });
}

function renderBacklinks(noteId) {
  const refs = backlinksIndex[noteId] || [];
  const count = refs.length;
  const label = count === 1 ? '1 referencia entrante' : `${count} referencias entrantes`;

  if (count === 0) {
    return `<div class="backlinks-section">
      <div class="backlinks-label">${label}</div>
      <div class="backlinks-empty">Ninguna nota enlaza aquí aún.</div>
    </div>`;
  }

  const chips = refs.map(r => {
    const fm  = FOLDER_META[r.folder];
    const col = fm?.color || 'var(--text-3)';
    const lbl = fm?.label || r.folder;
    return `<button class="backlink-chip" onclick="openNoteById(${r.id})">
      <span class="backlink-dot" style="background:${col}"></span>
      <span class="backlink-title">${esc(r.title)}</span>
      <span class="backlink-folder">${esc(lbl)}</span>
    </button>`;
  }).join('');

  return `<div class="backlinks-section">
    <div class="backlinks-label">${label}</div>
    <div class="backlinks-list">${chips}</div>
  </div>`;
}

// ── Panel collapse ────────────────────────────────────────────────
let _sidebarOpen = true;
let _listOpen    = true;

function toggleSidebar() {
  _sidebarOpen = !_sidebarOpen;
  const aside = document.querySelector('aside');
  if (_sidebarOpen) {
    aside.style.width   = '';
    aside.style.overflow = '';
    aside.style.padding  = '';
    aside.style.borderRight = '';
  } else {
    aside.style.width    = '0';
    aside.style.overflow = 'hidden';
    aside.style.padding  = '0';
    aside.style.borderRight = 'none';
  }
  document.getElementById('sidebar-arrow').textContent = _sidebarOpen ? '‹' : '›';
}

function toggleList() {
  _listOpen = !_listOpen;
  const lp = document.querySelector('.list-panel');
  if (_listOpen) {
    lp.style.width    = '';
    lp.style.overflow = '';
    lp.style.padding  = '';
    lp.style.borderRight = '';
  } else {
    lp.style.width    = '0';
    lp.style.overflow = 'hidden';
    lp.style.padding  = '0';
    lp.style.borderRight = 'none';
  }
  document.getElementById('list-arrow').textContent = _listOpen ? '‹' : '›';
}

// ── Duplicate check hooks ────────────────────────────────────────
document.getElementById('qc-title').addEventListener('input', _scheduleDupCheck);
document.getElementById('qc-body').addEventListener('input',  _scheduleDupCheck);

// ── Init ───────────────────────────────────────────────────────
buildBacklinksIndex();
updateOrphanCount();
buildSidebar();
buildTimeline();
refreshAll();
checkServer().then(() => {
  checkEmbeddings();
  // Auto-open note from #open= hash (set after quick capture)
  const hash = decodeURIComponent(location.hash);
  const m = hash.match(/^#open=(.+)$/);
  if (m) {
    const path = m[1];
    const note = DATA.notes.find(n => n.path === path);
    if (note) { openNoteById(note.id); history.replaceState(null, '', location.pathname); }
  }
});
</script>
</body>
</html>
"""


def _read_body(md_path: Path) -> str:
    """Read note body (content after YAML frontmatter)."""
    try:
        text = md_path.read_text(encoding="utf-8-sig")
        m = FRONTMATTER_RE.match(text)
        return text[m.end():].strip() if m else text.strip()
    except Exception:
        return ""


def load_projects() -> list[dict]:
    """Parse all .md files in Kanban/ folder into project dicts."""
    kanban_dir = BASE / "Kanban"
    if not kanban_dir.exists():
        return []

    projects = []
    for idx, path in enumerate(sorted(kanban_dir.glob("*.md"))):
        text = path.read_text(encoding="utf-8")
        m = FRONTMATTER_RE.match(text)
        fm = {}
        if m:
            try:
                import yaml
                fm = yaml.safe_load(m.group(1)) or {}
            except Exception:
                pass
        body = text[m.end():] if m else text

        tasks = {"backlog": [], "in_progress": [], "done": []}
        current = None
        SECTION_MAP = {
            "backlog": "backlog",
            "in progress": "in_progress",
            "in_progress": "in_progress",
            "done": "done",
            "hecho": "done",
            "en progreso": "in_progress",
        }
        for line in body.split("\n"):
            h = line.strip().lstrip("#").strip().lower()
            if line.startswith("##") and h in SECTION_MAP:
                current = SECTION_MAP[h]
                continue
            if current and line.strip().startswith("- ["):
                done = line.strip().startswith("- [x]")
                text_part = line.strip()[5:].strip()
                note_link = None
                if "\n  note:" in line or "  note:" in line:
                    pass  # handled below via next line
                # extract inline note: [[path]]
                import re as _re
                note_m = _re.search(r'note:\s*\[\[([^\]]+)\]\]', text_part)
                if note_m:
                    note_link = note_m.group(1)
                    text_part = text_part[:note_m.start()].strip()
                tasks[current].append({
                    "text": text_part,
                    "done": done,
                    "note": note_link,
                })

        projects.append({
            "id":     idx,
            "title":  fm.get("title", path.stem),
            "status": fm.get("status", "active"),
            "tags":   fm.get("tags", []) or [],
            "created": str(fm.get("created", "")),
            "path":   f"Kanban/{path.name}",
            "tasks":  tasks,
        })
    return projects


def build_dashboard(out_path: Path | None = None) -> Path:
    notes_raw = load_notes()

    notes_json = []
    for idx, n in enumerate(notes_raw):
        notes_json.append({
            "id":      idx,
            "title":   n["title"],
            "date":    n["date"].isoformat(),
            "updated": n["updated"].isoformat() if n["updated"] else None,
            "type":    n["type"],
            "status":  n["status"],
            "folder":  n["folder_key"],
            "tags":    n["tags"],
            "path":    str(n["rel"]).replace("\\", "/"),
            "body":    _read_body(n["path"]),
        })

    by_folder: dict[str, int] = defaultdict(int)
    for n in notes_json:
        by_folder[n["folder"]] += 1

    data = {
        "notes":    notes_json,
        "projects": load_projects(),
        "stats": {
            "total":        len(notes_json),
            "by_folder":    dict(by_folder),
            "last_updated": date.today().isoformat(),
        },
    }

    html = HTML_TEMPLATE \
        .replace("__DATA__",        json.dumps(data,        ensure_ascii=False)) \
        .replace("__FOLDER_META__", json.dumps(FOLDER_META, ensure_ascii=False))

    dest = out_path or BASE / "dashboard.html"
    dest.write_text(html, encoding="utf-8")
    return dest


def main():
    ap = argparse.ArgumentParser(description="Build KnowledgeBase dashboard HTML.")
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    dest = build_dashboard(args.out)
    print(f"[OK] Dashboard written to {dest}")


if __name__ == "__main__":
    main()
