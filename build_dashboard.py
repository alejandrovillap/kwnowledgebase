#!/usr/bin/env python3
"""
build_dashboard.py — Generate dashboard.html with all KnowledgeBase notes embedded.

The HTML is fully self-contained: data is embedded as JSON, no CDN dependencies.
Open dashboard.html in any browser to browse, filter, and search notes.

Usage:
    python build_dashboard.py
    python build_dashboard.py --out path/to/dashboard.html
"""

import json
import argparse
from datetime import date
from pathlib import Path
from collections import defaultdict

from build_index import load_notes, BASE

FOLDER_META = {
    "10-Work":                    {"label": "Work & Projects",       "color": "#5B6EF5"},
    "20-Learning":                {"label": "Learning",               "color": "#34C88A"},
    "20-Learning/CCA-F":          {"label": "CCA-F",                  "color": "#38BDF8"},
    "20-Learning/Certifications": {"label": "Certifications",         "color": "#A78BFA"},
    "20-Learning/Cognitive-PM-AI":{"label": "Cognitive PM AI",        "color": "#F472B6"},
    "40-Reference":               {"label": "Reference",              "color": "#FBBF24"},
    "50-Archive":                 {"label": "Archive",                "color": "#6B7280"},
    "Journal":                    {"label": "Journal",                "color": "#F87171"},
}

HTML_TEMPLATE = r"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>KnowledgeBase</title>
<style>
/* ── Tokens ──────────────────────────────────────────────────────────────── */
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

/* ── Reset ───────────────────────────────────────────────────────────────── */
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

/* ── Header ──────────────────────────────────────────────────────────────── */
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

/* ── Body layout ─────────────────────────────────────────────────────────── */
.layout {
  display: flex;
  flex: 1;
  min-height: 0;
}

/* ── Sidebar ─────────────────────────────────────────────────────────────── */
aside {
  width: var(--sidebar-w);
  flex-shrink: 0;
  background: var(--surface);
  border-right: 1px solid var(--border);
  overflow-y: auto;
  padding: 16px 0 32px;
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
  border-radius: 0;
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

/* ── Type filters ────────────────────────────────────────────────────────── */
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

/* ── Main feed ───────────────────────────────────────────────────────────── */
main {
  flex: 1;
  overflow-y: auto;
  padding: 20px 28px 40px;
}
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
  grid-template-columns: 88px 1fr auto;
  gap: 0 12px;
  align-items: center;
  padding: 7px 10px;
  border-radius: var(--radius);
  transition: background .1s;
  cursor: default;
}
.note-row:hover { background: var(--surface-2); }
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
.note-meta {
  display: flex;
  align-items: center;
  gap: 5px;
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
.badge-folder {
  border: 1px solid;
}
.badge-type {
  background: var(--surface-2);
  color: var(--text-2);
  border: 1px solid var(--border);
}

/* ── Scrollbar ───────────────────────────────────────────────────────────── */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border); border-radius: 99px; }
</style>
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
  <button class="theme-btn" onclick="toggleTheme()">◑</button>
</header>

<div class="layout">
  <aside>
    <div class="sidebar-section">
      <span class="sidebar-label">Carpetas</span>
      <div id="folder-nav"></div>
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

  <main id="main-feed"></main>
</div>

<script>
const DATA = __DATA__;
const FOLDER_META = __FOLDER_META__;

let activeFolder = null;
let activeTag    = null;
let activeType   = null;
let searchQuery  = '';

// ── Theme ──────────────────────────────────────────────────────────────────
function toggleTheme() {
  const root = document.documentElement;
  const cur  = root.getAttribute('data-theme');
  const next = cur === 'dark' ? 'light' : cur === 'light' ? 'dark' : 'light';
  root.setAttribute('data-theme', next);
}

// ── Filtering ──────────────────────────────────────────────────────────────
function filtered() {
  return DATA.notes.filter(n => {
    if (activeFolder && !n.folder.startsWith(activeFolder)) return false;
    if (activeTag    && !n.tags.includes(activeTag))         return false;
    if (activeType   && n.type !== activeType)               return false;
    if (searchQuery) {
      const q = searchQuery.toLowerCase();
      if (!n.title.toLowerCase().includes(q) &&
          !n.tags.join(' ').toLowerCase().includes(q) &&
          !n.folder.toLowerCase().includes(q)) return false;
    }
    return true;
  });
}

// ── Sidebar ────────────────────────────────────────────────────────────────
function buildSidebar() {
  const nav = document.getElementById('folder-nav');
  const total = DATA.notes.length;

  const allBtn = makeFolder('all', 'Todos', total, null);
  nav.appendChild(allBtn);

  Object.entries(DATA.stats.by_folder)
    .sort((a,b) => b[1] - a[1])
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
  lbl.style.overflow = 'hidden';
  lbl.style.textOverflow = 'ellipsis';
  lbl.style.whiteSpace = 'nowrap';

  const cnt = document.createElement('span');
  cnt.className = 'folder-count';
  cnt.textContent = count;

  btn.append(dot, lbl, cnt);
  btn.onclick = () => {
    activeFolder = key === 'all' ? null : key;
    activeTag = null;
    activeType = null;
    document.getElementById('search').value = '';
    searchQuery = '';
    refreshAll();
  };
  return btn;
}

function buildTagCloud() {
  const freq = {};
  DATA.notes.forEach(n => n.tags.forEach(t => { freq[t] = (freq[t]||0)+1; }));
  const top = Object.entries(freq).sort((a,b) => b[1]-a[1]).slice(0, 40);
  const cloud = document.getElementById('tag-cloud');
  cloud.innerHTML = '';
  top.forEach(([tag]) => {
    const chip = document.createElement('button');
    chip.className = 'tag-chip' + (activeTag === tag ? ' active' : '');
    chip.textContent = '#' + tag;
    chip.onclick = () => {
      activeTag = activeTag === tag ? null : tag;
      refreshAll();
    };
    cloud.appendChild(chip);
  });
}

function buildTypeFilters() {
  const types = [...new Set(DATA.notes.map(n => n.type).filter(Boolean))].sort();
  const wrap = document.getElementById('type-filters');
  wrap.innerHTML = '';
  types.forEach(t => {
    const chip = document.createElement('button');
    chip.className = 'type-chip' + (activeType === t ? ' active' : '');
    chip.textContent = t;
    chip.onclick = () => {
      activeType = activeType === t ? null : t;
      refreshAll();
    };
    wrap.appendChild(chip);
  });
}

// ── Feed ───────────────────────────────────────────────────────────────────
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
    const key   = n.date.slice(0,7);
    const label = d.toLocaleString('es', {month:'long', year:'numeric'});
    if (!byMonth[key]) byMonth[key] = { label, notes: [] };
    byMonth[key].notes.push(n);
  });

  Object.entries(byMonth)
    .sort((a,b) => b[0].localeCompare(a[0]))
    .forEach(([key, { label, notes: mnotes }]) => {
      const group = document.createElement('div');
      group.className = 'month-group';

      const hdr = document.createElement('div');
      hdr.className = 'month-header';
      hdr.textContent = key + ' — ' + label.charAt(0).toUpperCase() + label.slice(1);
      group.appendChild(hdr);

      mnotes.forEach(n => {
        const row = document.createElement('div');
        row.className = 'note-row';

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

        row.append(dateEl, titleWrap, meta);
        group.appendChild(row);
      });

      feed.appendChild(group);
    });
}

// ── Stats pill ─────────────────────────────────────────────────────────────
function updateStats(notes) {
  document.getElementById('total-pill').textContent = notes.length + ' notas';
  document.getElementById('date-pill').textContent  = 'actualizado ' + DATA.stats.last_updated;
}

// ── Active states ──────────────────────────────────────────────────────────
function updateActiveFolder() {
  document.querySelectorAll('.folder-btn').forEach(btn => {
    const key = btn.dataset.key;
    btn.classList.toggle('active',
      (!activeFolder && key === 'all') || activeFolder === key);
  });
}

// ── Refresh ────────────────────────────────────────────────────────────────
function refreshAll() {
  const notes = filtered();
  buildFeed(notes);
  updateStats(notes);
  buildTagCloud();
  buildTypeFilters();
  updateActiveFolder();
}

// ── Search ─────────────────────────────────────────────────────────────────
document.getElementById('search').addEventListener('input', e => {
  searchQuery = e.target.value.trim();
  refreshAll();
});

// ── Init ───────────────────────────────────────────────────────────────────
buildSidebar();
refreshAll();
</script>
</body>
</html>
"""


def build_dashboard(out_path: Path | None = None) -> Path:
    notes_raw = load_notes()

    notes_json = []
    for n in notes_raw:
        notes_json.append({
            "title":   n["title"],
            "date":    n["date"].isoformat(),
            "updated": n["updated"].isoformat() if n["updated"] else None,
            "type":    n["type"],
            "status":  n["status"],
            "folder":  n["folder_key"],
            "tags":    n["tags"],
            "path":    str(n["rel"]).replace("\\", "/"),
        })

    by_folder: dict[str, int] = defaultdict(int)
    for n in notes_json:
        by_folder[n["folder"]] += 1

    data = {
        "notes": notes_json,
        "stats": {
            "total":      len(notes_json),
            "by_folder":  dict(by_folder),
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
    ap.add_argument("--out", type=Path, default=None, help="Output path (default: dashboard.html)")
    args = ap.parse_args()
    dest = build_dashboard(args.out)
    print(f"[OK] Dashboard written to {dest}")


if __name__ == "__main__":
    main()
