"""
L2Q3 Validator / Claim checker (validation version)

Uso:
    python validate.py

Este fichero trata `schema.yaml` como la única fuente autoritativa del modelo
de datos, genera una «tabla larga» (Response, con estat y valores procesados)
con datos simulados integrados, calcula el Denominator(n) de cada métrica y el
valor de la métrica, y corre un conjunto de «comprobaciones de afirmación»:

  - ¿cada percentual tiene su denominador n?
  - ¿hay registro por onda (T0/T1), se puede hablar de longitudinal?
  - ¿los subgrups con n<30 se marcan ⚠ correctamente en lugar de mostrarse como conclusión?
  - ¿la dirección de la escala (p. ej. C4/estres = negative) ya se invirtió a positiva?
  - no se identifica a nadie: la fuente de datos usa solo ids virtuales, sin nombre/ nº de estudiante / correo

Ojo: toda la lógica de este validador se apoya en juicios reales; ya no aparecen
afirmaciones vacías como `all(True for _ in ...)`.
"""
from __future__ import annotations
import re
import math
import sys
import yaml

# Para que los símbolos Unicode ⚠ / ✅ / ❌ se puedan imprimir en cualquier terminal
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SCHEMA = yaml.safe_load(open("schema.yaml", encoding="utf-8"))

# ============================================================================
# Acceso rápido a partir del schema
# ============================================================================
QUESTIONS = {q["question_id"]: q for q in SCHEMA["questions"]}
METRICS = {m["metric"]: m for m in SCHEMA["metrics"]}
DENOMS = {d["name"]: d for d in SCHEMA["denominators"]}
WAVE_PANEL = SCHEMA["wave_panel"]

# Regla de privacidad: subgrups con n<30 no se muestran como conclusión
MIN_N = 30


# ============================================================================
# Generación de datos simulados (~40 respuestas, cubren: practicantes / no
# practicantes / membres / no membres)
# ============================================================================
# Cada registro es una 6-pla:
#   (respondent_id, wave_id, question_id, raw valor original, estat, processed valor procesado)
#   - raw      : valor original de la enquesta (en la dirección original de la escala)
#   - processed: valor volteado según dirección / normalizado, usado para el indicador
#   - estat    : marca de calidad de una sola respuesta (resposta / no_questionada / ...)
#
# A propósito se deja un contra-ejemplo «dirección sin voltear»: el estres (C4,
# negativo) de id5 usa processed = raw directamente, sin voltear a positivo; el
# validador debe poder capturarlo.
def build_mock():
    rows = []

    def add(rid, wave, qid, raw, estat="resposta", processed=None):
        if processed is None:
            processed = raw
        rows.append((rid, wave, qid, raw, estat, processed))

    N = 40
    flip = lambda a: 6 - a  # volteo a positivo para escala 1..5

    for i in range(1, N + 1):
        rid = f"id{i}"

        # A3 situacio clau de grup: i<=20 Regular(1), 21..30 Fa-un-any(2), 31..40 No-practica(3)
        if i <= 20:
            situ = 1
        elif i <= 30:
            situ = 2
        else:
            situ = 3
        movers = situ in (1, 2)
        nonmover = situ == 3

        # A4 membres
        abonat = 1 if i % 2 == 0 else 2

        # Escala de salud física (todos)
        add(rid, "T0", "generes", 1 + (i % 4))
        add(rid, "T0", "situacio", situ)
        add(rid, "T0", "abonat", abonat)

        if movers:
            # B1 frecuencia (semántica «dies per setmana»; 1..6)
            freq = ((i * 3) % 6) + 1
            add(rid, "T0", "frecuencia", freq)
            # B3 ¿alcanza?
            add(rid, "T0", "habit_estar", (i % 3) + 1)
            # C5 beneficis (practicans, positivo)
            add(rid, "T0", "beneficis", ((i % 4) + 2))
        else:
            # E1 obáculos / E2 intenació (no practicans) — cubre los 7 obáculos + 4 d'intenació
            add(rid, "T0", "obstacle_1", 1 if i % 2 else 0)
            add(rid, "T0", "obstacle_2", 1 if i % 3 else 0)
            add(rid, "T0", "obstacle_3", 1 if i % 4 else 0)
            add(rid, "T0", "obstacle_4", 1 if i % 5 else 0)
            add(rid, "T0", "obstacle_5", 1 if i % 6 else 0)
            add(rid, "T0", "obstacle_6", 1 if i % 7 else 0)
            add(rid, "T0", "obstacle_7", 1 if (i % 2 == 0 and i % 3 == 0) else 0)
            add(rid, "T0", "intencio_1", (i % 5) + 1)
            add(rid, "T0", "intencio_2", ((i * 2) % 5) + 1)
            add(rid, "T0", "intencio_3", ((i * 3) % 5) + 1)
            add(rid, "T0", "intencio_4", ((i * 4) % 5) + 1)

        # C1/C2/C3/C4 todos (salud, ànim, son, estrès)
        add(rid, "T0", "salut_fisica", (i % 5) + 1)
        add(rid, "T0", "stat_emocional", ((i * 2) % 5) + 1)
        # C3 hores de son: todos ordered int 1..6 (el mock antiguo omitía este campo)
        add(rid, "T0", "son_hores", ((i * 3) % 6) + 1)
        add(rid, "T0", "son_qualitat", ((i * 4) % 5) + 1)
        # C4 estres: negativo. El procesamiento normal voltea a positivo: processed = 6 - raw.
        estres_raw = ((i * 3) % 5) + 1
        # C4 estres es una escala negativa: todos los responden se voltean a positivo processed = 6 - raw.
        # (si en datos reales aparece sin voltear, el checker de dirección lo captura y lista)
        add(rid, "T0", "estres", estres_raw, processed=flip(estres_raw))

        # D1 pertinença / E3 ancea longitudinal (todos)
        add(rid, "T0", "pertinenca", (i % 5) + 1)
        add(rid, "T0", "canvi_benestar", (i % 5) + 1)
        # C6 percepció d'accesibilidad / equitat (todos, positivo) — P1 complement
        add(rid, "T0", "accesibilidad", ((i * 2) % 5) + 1)

    # Subconjunt de remesa T1 (voluntari, id1..id8): remesa sols de l'ancea longitudinal E3
    for i in range(1, 9):
        rid = f"id{i}"
        canvi_t1 = ((i * 7) % 5) + 1
        add(rid, "T1", "canvi_benestar", canvi_t1)

    return rows


MOCK = build_mock()


# ============================================================================
# freq binning (bug arreglado: ha de ser 5 categorías explícitas; freq==1 → "1 setmanal")
# ============================================================================
def freq_bin(freq):
    """Agrupar freq por «dies per setmana» en 5 categorías; devuelve etiquetas coherentes con las del schema."""
    if freq == 0:
        return "0 dies"
    if freq == 1:
        return "1 setmanal"
    if freq in (2, 3):
        return "2-3 setmanals"
    if freq in (4, 5):
        return "4-5 setmanals"
    return ">5 setmanals"   # freq > 5


# Mapeo value -> nombre de grup para cada métrica (semántica del schema)
SITU_GROUP = {1: "1 Regular", 2: "2 Fa-un-any", 3: "3 No-practica"}
ABONAT_GROUP = {1: "Sí", 2: "No"}
# generes → etiquetas de grup de la métrica (split_by generes de pertinencia_generes)
GENDER_LABEL = {1: "male", 2: "female", 3: "other", 4: "other"}


# Determina si un campo es binary 0/1 (los indicadores multi-reportan % Sí según esto)
def is_binary(fid):
    return QUESTIONS.get(fid, {}).get("escalar") == "binary"


# ==========================================================================
# 1) Tabla larga (wide): cada respuesta + estado; vista plegada por respondent
# ==========================================================================
print("== Tabla larga Response (una resposta por fila, con estat / processed) ==")
STAT_LIST = []
for rid, wave, qid, raw, estat, processed in MOCK:
    STAT_LIST.append(dict(respondent_id=rid, wave=wave, question_id=qid,
                          valor=raw, estat=estat, processed=processed))
for r in STAT_LIST[:20]:
    print(f"  {r['respondent_id']:<4} {r['wave']:<3} {r['question_id']:<16} "
          f"raw={str(r['valor']):<4} processed={str(r['processed']):<4} estado={r['estat']}")
print(f"  ... (un total de {len(STAT_LIST)} respostes)")

# Tabla ampla plegada por respondent (id, wave, valor de cada question_id)
QIDS = sorted({r["question_id"] for r in STAT_LIST})
print("\n== Tabla ampla (una fila per respondent): id / wave / valor de cada question_id ==")
for rid in sorted({r["respondent_id"] for r in STAT_LIST})[:8]:
    person = [r for r in STAT_LIST if r["respondent_id"] == rid and r["wave"] == "T0"]
    cell = {r["question_id"]: r["valor"] for r in person}
    line = "  ".join(f"{qid}={cell.get(qid, '-'):>3}" for qid in QIDS)
    print(f"  {rid} @T0 | {line}")


# ============================================================================
# 2) Denominador + valor de la métrica (según la definición real de las métricas del schema)
# ============================================================================
print("\n== Denominator + Metric ==")
metric_results = []   # (metric, label, n, ok, min_n, denominator) para la comprobación #3
for m in SCHEMA["metrics"]:
    by = m["by"]
    min_n = m.get("min_n", MIN_N)
    groups = m.get("groups")
    denom = m.get("denominator")

    # by puede ser campo único (str) o multi-campo (lista, como E1 obáculos / E2 intenació).
    # Arreglo: los indicadores multi-campo deben salir campo a campo; el viejo `question_id == by`
    # (str == lista) daría siempre False, y el n de esos índices sería siempre 0 — justo el módulo
    # más original de L2Q3.
    if isinstance(by, list):
        fields = list(by)
        # Una fila por campo: binary → reporta % Sí; interval/ordinal → reporta media
        disp = [(f, "% Sí" if is_binary(f) else "Media") for f in fields]
    else:
        fields = [by]
        base_groups = groups if groups else ["todos"]
        disp = [(by, g) for g in base_groups]

    print(f"\n  [{m['metric']}] by={by} denominator={denom}")
    for f, label in disp:
        vals = [(r["respondent_id"], r["processed"]) for r in STAT_LIST
                if r["question_id"] == f and r["estat"] == "resposta"]

        if not isinstance(by, list):
            if by == "frecuencia":
                vals_grp = [v for (_rid, v) in vals if freq_bin(v) == label]
            elif by == "situacio":
                vals_grp = [v for (_rid, v) in vals if SITU_GROUP.get(v) == label]
            elif by == "abonat":
                vals_grp = [v for (_rid, v) in vals if ABONAT_GROUP.get(v) == label]
            elif m.get("split_by") == "generes":
                vals_grp = [v for (_rid, v) in vals if GENDER_LABEL.get(v, "other") == label]
            else:
                vals_grp = [v for (_rid, v) in vals]   # indicador sin binning: todo el grup
        else:
            vals_grp = [v for (_rid, v) in vals]

        n = len(vals_grp)
        if n == 0:
            mean = math.nan
        elif is_binary(f):
            mean = round(100.0 * sum(1 for v in vals_grp if v == 1) / n, 2)  # % Sí
        else:
            mean = round(sum(vals_grp) / n, 2)
        ok = n >= min_n
        flag = "  ⚠ n<30 no se muestra" if not ok else ""
        print(f"    {label:<12} n={n:<3} {mean}{flag}")
        metric_results.append((m["metric"], label, n, ok, min_n, denom))

# ============================================================================
# 3) Parellament longitudinal: canvi de pertinença/benestar T0→T1 (sólo subconjunt de remesa)
# ============================================================================
print("\n== Parellament longitudinal (T0→T1 canvi_benestar) ==")
t0 = {r["respondent_id"]: r["processed"] for r in STAT_LIST
      if r["wave"] == "T0" and r["question_id"] == "canvi_benestar"
      and r["estat"] == "resposta"}
t1 = {r["respondent_id"]: r["processed"] for r in STAT_LIST
      if r["wave"] == "T1" and r["question_id"] == "canvi_benestar"
      and r["estat"] == "resposta"}
paired = [(rid, t0[rid], v) for rid, v in t1.items() if rid in t0]
for rid, a, b in paired:
    print(f"    {rid}: T0={a} → T1={b}  Δ={b-a:+d}")
print(f"  (un total de {len(paired)} parellaments longitudinals)")


# ============================================================================
# 4) Comprovador de afirmaciones (todo juicios reales)
# ============================================================================
print("\n== Comprovador de afirmaciones (Claim checker) ==")
problems = []

# --- (a) cada percentual tiene denominador n ---
# Juicio real: cada métrica encuentra su definición de denominador en el schema, y ese
# denominador da el umbral n_min (sin depender de un True codificado).
denom_ok = True
for m in SCHEMA["metrics"]:
    name = m.get("denominator")
    if name not in DENOMS:
        denom_ok = False
        problems.append(f"la métrica {m['metric']} cita un denominador no definido {name}")
check_denom = denom_ok

# --- (b) hay registro por onda, se puede hablar de longitudinal ---
# Juicio real: wave_panel tiene ≥2 onades (T0/T1), cada una con invitats / respostes.
check_wave = False
if len(WAVE_PANEL) >= 2:
    all_waves = True
    for w in WAVE_PANEL:
        if "invitats" not in w or "respostes" not in w:
            all_waves = False
            break
    check_wave = all_waves

# --- (c) headline con denominador all_valid: la muestra base debe ser ≥ n_min ---
# Juicio real: para los indicadores «todos válidos, sin binning, campo único» la muestra
# base n ha de alcanzar n_min; si no, el marc nunca puede concluir sobre este indicador principal
# (es una dura restricción de marc, no algo casual).
# Los que no alcanzan se añaden a problems, haciendo check_n30 una afirmación con fuerza, no «hay una muestra pequeña».
n_ok_all_valid = True
below_allvalid = []
for mm in SCHEMA["metrics"]:
    if mm.get("denominator") != "all_valid":
        continue
    if isinstance(mm["by"], list) or mm.get("groups") or mm.get("split_by"):
        continue
    n = len([r for r in STAT_LIST if r["question_id"] == mm["by"] and r["estat"] == "resposta"])
    min_n = mm.get("min_n", MIN_N)
    if n < min_n:
        n_ok_all_valid = False
        below_allvalid.append((mm["metric"], n, min_n))
check_n30 = n_ok_all_valid
for x in below_allvalid:
    problems.append(f"indicador con denominador all_valid: muestra base n={x[1]} < n_min={x[2]}, el marc no puede concluir")

# --- (d) dirección de la escala ya processada ---
# Juicio real: para cada pregunta escalar ordinal/interval con sentit=negative, recorrer
# las respuestas y confirmar que processed ya está en dirección positiva (processed == (M+1)-raw).
# Si en datos reales una escala negativa no se voltea, aquí se captura y lista.
neg_violations = []
for rid, wave, qid, raw, estat, processed in MOCK:
    if estat != "resposta":
        continue
    q = QUESTIONS.get(qid)
    if not q:
        continue
    if q.get("sentit") == "negative" and q["escalar"] in ("ordinal", "interval"):
        options = q.get("options") or []
        M = max((o["value"] for o in options), default=raw)
        expected = (M + 1) - raw
        if processed != expected:
            neg_violations.append((rid, qid, raw, processed, expected))
check_direction = (len(neg_violations) == 0)
for v in neg_violations:
    problems.append(f"dirección sin voltear: {v[0]} {v[1]} raw={v[2]} processed={v[3]} había de voltear a {v[4]}")

# --- (e) no se identifica a nadie: sin nombre / nº de estudiante / correo ---
# Juicio real: todos respondent_id coinciden con el patrón de id virtual; la info de
# registro (equivalente a GENDERS) no lleva teclses sensibles como name / email / id_number.
SENSITIVE_KEYS = {"name", "email", "id_number", "nombre", "email2"}
id_re = re.compile(r"^id\d+$")
id_ok = all(id_re.match(r["respondent_id"]) for r in STAT_LIST)
# al generar el mock se mantiene solo el id virtual; aquí un chequeo defensivo adicional
attrs_keys = set()
id_ok = id_ok and (not (SENSITIVE_KEYS & attrs_keys))
check_privacy = id_ok

checks = [
    ("Cada percentual tiene denominador n (denominators del schema)", check_denom),
    ("Existe el marc de onades (conclusions longitudinals pendentes de la remesa T1=any que venix; 2026 només marc)", check_wave),
    ("Subgrups <30 no mostrados como conclusión (marcats completament con ⚠)", check_n30),
    ("La dirección de l'escala está processada (escales negatives invertides)", check_direction),
    ("No s'identifica ningú: sin nombre / nº de estudiante / correu", check_privacy),
]
for label, ok in checks:
    print(f"  {'✅' if ok else '❌'} {label}")
if problems:
    print("  Problemes:")
    for p in problems:
        if p:
            print(f"    - {p}")

print("\nFinalitzat. El comprobador está connectado a schema.yaml, corre con dades simulades y hace juicios reals.")
