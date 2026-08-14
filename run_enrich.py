#!/usr/bin/env python3
"""One-shot: enrich the 6 target notes."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from enrich_notes import enrich_file, BASE

targets = [
    BASE / "20-Learning" / "Gemini-Enterprise" / "2026-07-17_Gemini_Enterprise_Change_Management_Methodology_–_People,_Process,_Technology_&_.md",
    BASE / "20-Learning" / "Gemini-Enterprise" / "2026-07-17_Gemini_Enterprise_Platform_Overview_–_Deployment,_Adoption_&_Agentic_Architectur.md",
    BASE / "20-Learning" / "Gemini-Enterprise" / "2026-07-17_Módulo_1_—_Privacidad,_DLP_y_Cumplimiento_en_Gemini_Enterprise_(Google_Workspace.md",
    BASE / "20-Learning" / "Gemini-Enterprise" / "2026-07-17_Guía_del_Consultor_de_Soluciones_Gemini_Enterprise.md",
    BASE / "20-Learning" / "Antigravity" / "2025-01-01_Antigravity_Platform_-_Editor_and_Agentic_Flow_Design.md",
    BASE / "20-Learning" / "Antigravity" / "2026-07-15_Antigravity_Platform_Architecture_&_Engineering_Design.md",
]

ok = 0
for p in targets:
    if not p.exists():
        print(f"[MISSING] {p}")
        continue
    if enrich_file(p):
        ok += 1

print(f"\nEnriched {ok}/{len(targets)} notes.")

# Rebuild
from build_index import build_all
build_all()
from build_dashboard import build_dashboard
build_dashboard()
print("Index and dashboard updated.")
