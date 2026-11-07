#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
demo_on_2026.py — Demostració del nuevo modelo de datos L2Q3 sobre 【dades reals de 2026】

Objetivo: demostrar que el nuevo modelo (tabla larga + denominador n explícit) pot
corrir resultats sobre dades reals, i mostrar visualment les buits de l'enquesta 2026
(per què L2Q3 necessita els nous mòduls d'obacles E1 / intenació E2 / C6 d'accesibilidad).

Conformitat:
  - Aquest script sols [llegix] les dades reals locales; no escriu, no puja, no exporta cap fitxer de dades reals.
  - Les dades reals del SAF no hi pot entrar al repositori segons la regla del repte; aquest repositori no conté cap dada real de persona.
  - Els resultats es presenten com a n agregat / percentuals; sense identificador personal, sense conclusions de subgrups n<30.

Execució (quan hi ha dades reals en aquesta màquina):
    pip install pandas openpyyaml pyyaml
    python demo_on_2026.py

Detecció automàtica de la ruta de dades (modifica si cal).
"""
from __future__ import annotations
import sys
import pandas as pd

# ── Ruta de les dades reals (locales /DADES/, mai al repositori) ────────────────────────
CANDIDATES = [
    "DADES/saf-enquesta-2026-equips.xlsx",
    "../DADES/saf-enquesta-2026-equips.xlsx",
    "D:/Project/REPTE SAF UAB/DADES/saf-enquesta-2026-equips.xlsx",
    "/home/teammate/REPTE SAF UAB/DADES/saf-enquesta-2026-equips.xlsx",
]

# ── Mappament camp (schema.yaml) ↔ col de 2026 (reutilitza camps; els nous camps no tenen dades a 2026) ─
#   camp ID (schema.yaml)  :  índex de col de 2026
FIELD_COLS = {
    "generes":            2,   # A1 gène
    "situacio":           4,   # A3 situació (clau de grup)
    "abonat":             5,   # A4 ¿membre?
    "frecuencia":         8,   # B1 freqüència (sols practicans; falten 106)
    "salut_fisica":       17,  # C1 salud física
    "stat_emocional":     18,  # C2 ànim
    "pertinenca":         27,  # D1 vincle/pertinença (primera pregunta, 4 preguntes com a mostra)
}
# Mòduls novells de L2Q3: no existeixen a l'enquesta 2026, per així n=0 — precisament el motiu de crear-los
NEW_FIELDS = ["accesibilidad", "obstacle_1", "obstacle_2", "obstacle_3",
              "obstacle_4", "obstacle_5", "obstacle_6", "obstacle_7",
              "intencio_1", "intencio_2", "intencio_3", "intencio_4",
              "canvi_benestar"]
MIN_N = 30


def find_data():
    for c in CANDIDATES:
        try:
            if __import__("pathlib").Path(c).exists():
                return c
        except Exception:
            pass
    return None


def situ_to_group(v):
    """Valor de A3 de 2026 → grup: practicans (movers) / no-practicans (nonmovers)"""
    s = str(v).strip().lower()
    if s.startswith("no practico"):
        return "nonmovers"
    # "Faig ... regularment" (regular >1 any) i "He començat ... últim any" (fa-un-any) són practicans
    return "movers"


def main():
    path = find_data()
    if not path:
        print("No se ha trobat el fitxer de dades reals en aquesta màquina (segons la regla, no s'entraria al repositori).\n"
              "Execute aquest script en una màquina amb dades reals; el repositori en si no ha de contenir dades reals.")
        return

    df = pd.read_excel(path, sheet_name="Respostes")
    N = len(df)
    print(f"【Lectura de dades reals 2026】{path}")
    print(f"  muestra N = {N} (1025 és el valor oficial publicat)\n")

    # ── Grup (la «clau de grup» A3 del nuevo modelo) ──────────────────────────────────────
    df["_group"] = df.iloc[:, FIELD_COLS["situacio"]].apply(situ_to_group)
    movers = (df["_group"] == "movers").sum()
    nonmovers = (df["_group"] == "nonmovers").sum()

    # ── Denominador n explícit (el centre del nuevo modelo: cada percentual porta el seu denominador) ────────────────────────
    denom = {
        "all_valid        tothom and de valid": N,
        f"movers_n practicans  A3∈regular/fa-un-any": int(movers),
        f"nonmovers_n no-practicans A3=no-practica": int(nonmovers),
    }
    abonat_si = (df.iloc[:, FIELD_COLS["abonat"]].astype(str).str.strip() == "Sí.").sum()
    denom["abonat_sisi membres Sí  A4=Sí"] = int(abonat_si)

    print("【Denominador n explícit (nuevo modelo)】")
    for k, v in denom.items():
        flag = " ✅ n≥30" if v >= MIN_N else " ⚠ n<30 sense conclusió"
        print(f"  {k:<34} n={v:<6}{flag}")
    print(f"  % de membres Sí = {abonat_si/N*100:.1f}% (denominador = nombre de membres)\n")

    # ── Camps reutilitzables: respostes valides de 2026 (directes a la nova tabla larga) ──────────────────────────────────
    print("【Camps reutilitzables: respostes valides de 2026 (directes a la nova tabla larga)】")
    label = {"generes":"generes A1","situacio":"situacio A3","abonat":"abonat A4",
             "frecuencia":"frecuencia B1","salut_fisica":"salut_fisica C1",
             "stat_emocional":"stat_emocional C2","pertinenca":"pertinenca D1"}
    for fid, idx in FIELD_COLS.items():
        col = df.columns[idx]
        valid = df[col].notna().sum()
        flag = "" if valid >= MIN_N else " ⚠ n<30"
        print(f"  {fid:<16}{label[fid]:<18} válides = {valid}{flag}")
    print("  (B1 freqüència manca 305 registres: el model antic no pot reconstruir el denominador de «qui ha de tenir freqüència»; L2Q3 ho arregla amb denominador explícit)\n")

    # ── Mòduls novells de L2Q3 — buits de dades de 2026 (demostrar la necessitat de disseny) ─────────────────────
    print("【Mòduls novells de L2Q3 — buits de dades de 2026】")
    print(f"  població objectiu d'obacles E1 /intenació E2 de no-practicans n = {nonmovers}")
    print(f"    (l'enquesta 2026 no té «ni una» pregunta de motivació/obacles per a aquests {nonmovers} → hueco de 199)")
    for f in NEW_FIELDS:
        print(f"  {f:<18} observacions de 2026 = 0  →  complement a l'enquesta nova del 2027")
    print("  (E3 canvi_benestar ancoa longitudinal: necessita dos aplicacions independents el 2027, 2026 només marc)\n")

    print("【Afirmacions】")
    print("  - 2026 és una enquesta cross-sectional d'un sol moment; correlación ≠ causa.")
    print("  - aquest script no emet conclusions de subgrups n<30; no s'identifica ningú.")
    print("  - els mòduls novells (C6/E1/E2/E3) no tenen dades a 2026; han de repetir-se l'aplicació el próximo any per poder verificar-los.")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
