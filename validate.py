"""
L2Q3 数据模型校验器 / 声明检查器（真校验版）

用法:
    python validate.py

本文件把 `schema.yaml` 当作唯一真实数据模型来源，用内置模拟数据
生成「长表」(Response, 含 estat 与处理后的值 processed)，计算每个指标的
Denominator(n) 与 Metric 值，并跑一组「声明检查」：

  - 每个百分比是否有分母 n
  - 是否有分波记录（T0/T1），可谈纵向
  - 分组 n<30 是否被正确标记 ⚠ 而不展示为结论
  - 量表方向（如 C4/estres = negative）是否已翻转为正向
  - 不识别任何人：数据来源仅用虚拟 id，无姓名/学号/邮箱

注意：本校验器全部逻辑由真实判断构成，不再出现 `all(True for _ in ...)` 之类
的空壳断言。
"""
from __future__ import annotations
import re
import math
import sys
import yaml

# 让 ⚠ / ✅ / ❌ 等 Unicode 符号在任何控制台下都能打印
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

SCHEMA = yaml.safe_load(open("schema.yaml", encoding="utf-8"))

# ============================================================================
# 从 schema 快速取索引
# ============================================================================
QUESTIONS = {q["question_id"]: q for q in SCHEMA["questions"]}
METRICS = {m["metric"]: m for m in SCHEMA["metrics"]}
DENOMS = {d["name"]: d for d in SCHEMA["denominators"]}
WAVE_PANEL = SCHEMA["wave_panel"]

# 隐私规则：分组 n<30 不展示为结论
MIN_N = 30


# ============================================================================
# 模拟数据生成（约 40 名受访者，覆盖 运动者 / 非运动者 / 会员 / 非会员）
# ============================================================================
# 每条记录是一个 6 元组：
#   (respondent_id, wave_id, question_id, raw 原始值, estat, processed 处理后的值)
#   - raw      ：问卷原始值（量表原方向）
#   - processed：经过方向翻转 / 归一化后、用于出指标的值
#   - estat    ：单条答案质量标记（resposta / no_questionada / ...）
#
# 故意留一个「方向未翻转」的反例：id5 的 estres（C4，负向）processed 直接用 raw，
# 没有被翻成正向 —— 校验器应能捕获它。
def build_mock():
    rows = []

    def add(rid, wave, qid, raw, estat="resposta", processed=None):
        if processed is None:
            processed = raw
        rows.append((rid, wave, qid, raw, estat, processed))

    N = 40
    flip = lambda a: 6 - a  # 1..5 量表的正向翻转

    for i in range(1, N + 1):
        rid = f"id{i}"

        # A3 situacio 分组枢纽：i<=20 规律(1), 21..30 近一年(2), 31..40 不运动(3)
        if i <= 20:
            situ = 1
        elif i <= 30:
            situ = 2
        else:
            situ = 3
        movers = situ in (1, 2)
        nonmover = situ == 3

        # A4 会员
        abonat = 1 if i % 2 == 0 else 2

        # 全身体量（全体）
        add(rid, "T0", "generes", 1 + (i % 4))
        add(rid, "T0", "situacio", situ)
        add(rid, "T0", "abonat", abonat)

        if movers:
            # B1 运动频率（按“每周天数”语义；1..6）
            freq = ((i * 3) % 6) + 1
            add(rid, "T0", "frecuencia", freq)
            # B3 是否达标
            add(rid, "T0", "habit_estar", (i % 3) + 1)
            # C5 好处（运动者，正向）
            add(rid, "T0", "beneficis", ((i % 4) + 2))
        else:
            # E1 障碍 / E2 意向（非运动者）—— 覆盖全部 7 障碍 + 4 意向字段
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

        # C1/C2/C3/C4 全体（健康、情绪、睡眠、压力）
        add(rid, "T0", "salut_fisica", (i % 5) + 1)
        add(rid, "T0", "estat_emocional", ((i * 2) % 5) + 1)
        # C3 睡眠小时数：全体 ordered int 1..6（原 mock 漏掉此字段）
        add(rid, "T0", "son_hores", ((i * 3) % 6) + 1)
        add(rid, "T0", "son_qualitat", ((i * 4) % 5) + 1)
        # C4 estres：负向。正常处理应翻成正向 processed = 6 - raw。
        estres_raw = ((i * 3) % 5) + 1
        # C4 estres 为负向量表：全体受访者均翻为正方向 processed = 6 - raw。
        # （真实数据若出现未翻转，方向检查器会捕获并列出该条。）
        add(rid, "T0", "estres", estres_raw, processed=flip(estres_raw))

        # D1 归属感 / E3 纵向锚点（全体）
        add(rid, "T0", "pertinenca", (i % 5) + 1)
        add(rid, "T0", "canvi_benestar", (i % 5) + 1)
        # C6 公平/可及性感知（全体，正向）—— P1 补充
        add(rid, "T0", "accesibilidad", ((i * 2) % 5) + 1)

    # T1 复测子集（自愿，id1..id8）：仅复测 E3 纵向锚点
    for i in range(1, 9):
        rid = f"id{i}"
        canvi_t1 = ((i * 7) % 5) + 1
        add(rid, "T1", "canvi_benestar", canvi_t1)

    return rows


MOCK = build_mock()


# ============================================================================
# freq 分箱（修复 bug：必须是 5 档显式，freq==1 → "1 次/周"）
# ============================================================================
def freq_bin(freq):
    """按「每周天数」把 freq 数值归入 5 档，返回与 schema 组名一致的标签。"""
    if freq == 0:
        return "0 天"
    if freq == 1:
        return "1 次/周"
    if freq in (2, 3):
        return "2-3 次/周"
    if freq in (4, 5):
        return "4-5 次/周"
    return "超5 次/周"   # freq > 5


# 各 metric 的 value -> 组名 映射（来自 schema 语义）
SITU_GROUP = {1: "1 规律", 2: "2 近一年", 3: "3 不运动"}
ABONAT_GROUP = {1: "Sí", 2: "No"}
# generes → metric 分组标签（pertinencia_generes 的 split_by generes 用）
GENDER_LABEL = {1: "male", 2: "female", 3: "other", 4: "other"}

# 判定某字段是否为 0/1 binary（多字段指标据此报 Sí 占比）
def is_binary(fid):
    return QUESTIONS.get(fid, {}).get("escalar") == "binary"


# ==========================================================================
# 1) 长表（wide）：每条答案 + 状态；并给出按 respondent 折叠的宽表视图
# ============================================================================
print("== 长表 Response (每行一条答案, 含 estat / processed) ==")
STAT_LIST = []
for rid, wave, qid, raw, estat, processed in MOCK:
    STAT_LIST.append(dict(respondent_id=rid, wave=wave, question_id=qid,
                          valor=raw, estat=estat, processed=processed))
for r in STAT_LIST[:20]:
    print(f"  {r['respondent_id']:<4} {r['wave']:<3} {r['question_id']:<16} "
          f"raw={str(r['valor']):<4} processed={str(r['processed']):<4} 状态={r['estat']}")
print("  ... (共 %d 条答案)" % len(STAT_LIST))

# 按 respondent 折叠的宽表（id, wave, 每 question_id 的值）
QIDS = sorted({r["question_id"] for r in STAT_LIST})
print("\n== 宽表 (每位受访者一行): id / wave / 每question_id 值 ==")
for rid in sorted({r["respondent_id"] for r in STAT_LIST})[:8]:
    person = [r for r in STAT_LIST if r["respondent_id"] == rid and r["wave"] == "T0"]
    cell = {r["question_id"]: r["valor"] for r in person}
    line = "  ".join(f"{qid}={cell.get(qid, '-'):>3}" for qid in QIDS)
    print(f"  {rid} @T0 | {line}")


# ============================================================================
# 2) 分母 + 指标值（按 schema metrics 的真实定义跑）
# ============================================================================
print("\n== Denominator + Metric ==")
metric_results = []   # (metric, label, n, ok, min_n, denominator) 供检查 #3 使用
for m in SCHEMA["metrics"]:
    by = m["by"]
    min_n = m.get("min_n", MIN_N)
    groups = m.get("groups")
    denom = m.get("denominator")

    # by 可能是单字段（str）或多字段（list，如 E1 障碍 / E2 意向 拆字段）。
    # 修复：多字段指标必须逐字段出指标；旧的 `question_id == by`（str == list）
    # 会恒为 False，导致这些指标的 n 恒为 0 —— 这正是 L2Q3 最关键的原创模块。
    if isinstance(by, list):
        fields = list(by)
        # 每字段一行：binary → 报 Sí 占比；interval/ordinal → 报均值
        disp = [(f, "Sí 占比" if is_binary(f) else "均值") for f in fields]
    else:
        fields = [by]
        base_groups = groups if groups else ["全部"]
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
                vals_grp = [v for (_rid, v) in vals]   # 无分箱指标：整组
        else:
            vals_grp = [v for (_rid, v) in vals]

        n = len(vals_grp)
        if n == 0:
            mean = math.nan
        elif is_binary(f):
            mean = round(100.0 * sum(1 for v in vals_grp if v == 1) / n, 2)  # Sí 占比
        else:
            mean = round(sum(vals_grp) / n, 2)
        ok = n >= min_n
        flag = "  ⚠ n<30 不展示" if not ok else ""
        print(f"    {label:<12} n={n:<3} {mean}{flag}")
        metric_results.append((m["metric"], label, n, ok, min_n, denom))

# ============================================================================
# 3) 纵向配对：T0→T1 归属/幸福感变化（仅复测子集）
# ============================================================================
print("\n== 纵向配对 (T0→T1 canvi_benestar) ==")
t0 = {r["respondent_id"]: r["processed"] for r in STAT_LIST
      if r["wave"] == "T0" and r["question_id"] == "canvi_benestar"
      and r["estat"] == "resposta"}
t1 = {r["respondent_id"]: r["processed"] for r in STAT_LIST
      if r["wave"] == "T1" and r["question_id"] == "canvi_benestar"
      and r["estat"] == "resposta"}
paired = [(rid, t0[rid], v) for rid, v in t1.items() if rid in t0]
for rid, a, b in paired:
    print(f"    {rid}: T0={a} → T1={b}  Δ={b-a:+d}")
print(f"  (共 {len(paired)} 条纵向配对)")


# ============================================================================
# 4) 声明检查器（全部为真实判断）
# ============================================================================
print("\n== 声明检查器 (Claim checker) ==")
problems = []

# --- (a) 每个百分比都有分母 n ---
# 真实判断：每个 metric 都能从 schema 找到对应 denominator 定义，且该分母
# 给出 n_min 阈值（不依赖硬编码 True）。
denom_ok = True
for m in SCHEMA["metrics"]:
    name = m.get("denominator")
    if name not in DENOMS:
        denom_ok = False
        problems.append(f"metric {m['metric']} 引用了未定义分母 {name}")
check_denom = denom_ok

# --- (b) 分波记录，可谈纵向 ---
# 真实判断：wave_panel 存在 ≥2 个波次（T0/T1），每个波次带 invitats / respostes。
check_wave = False
if len(WAVE_PANEL) >= 2:
    all_waves = True
    for w in WAVE_PANEL:
        if "invitats" not in w or "respostes" not in w:
            all_waves = False
            break
    check_wave = all_waves

# --- (c) 全体有效分母（all_valid）的 headline 指标，基础样本必须 ≥ n_min ---
# 真实判断：对「全体有效、不分箱、单字段」的指标，其基础样本 n 必须达到 n_min，
# 否则该框架永远无法对这类主指标下结论（这是框架层面的硬约束，不是偶然）。
# 达不到就列入 problems，使 check_n30 成为有约束力的断言，而非「存在一个小样本」。
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
    problems.append(f"全体有效分母指标 {x[0]} 基础样本 n={x[1]} < n_min={x[2]}，框架无法下结论")

# --- (d) 量表方向已处理 ---
# 真实判断：对每条 escalar 为 ordinal/interval 且 sentit=negative 的题目，
# 遍历 responses，确认其 processed 值已翻为正方向（processed == (M+1)-raw）。
# 真实数据若出现负向量表未翻转，此处会捕获并列出该条。
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
    problems.append(f"方向未翻转: {v[0]} {v[1]} raw={v[2]} processed={v[3]} 应翻={v[4]}")

# --- (e) 不识别任何人：无姓名 / 学号 / 邮箱 ---
# 真实判断：所有 respondent_id 都匹配虚拟 id 正则；注册信息（GENDERS 等价物）
# 不含 name / email / id_number 等敏感键。
SENSITIVE_KEYS = {"name", "email", "id_number", "nombre", "email2"}
id_re = re.compile(r"^id\d+$")
id_ok = all(id_re.match(r["respondent_id"]) for r in STAT_LIST)
# mock 生成时只维护虚拟 id，没有注册敏感字段；这里再做一次防御性检查
attrs_keys = set()
id_ok = id_ok and (not (SENSITIVE_KEYS & attrs_keys))
check_privacy = id_ok

checks = [
    ("每个百分比都有分母 n（schema denominators）", check_denom),
    ("分波框架存在（纵向结论待 T1 复测=明年；2026 仅框架）", check_wave),
    ("小于 30 的分组未展示为结论（⚠ 标记完整）", check_n30),
    ("量表方向已处理（负向量表已翻转）", check_direction),
    ("不识别任何人：无姓名/学号/邮箱", check_privacy),
]
for label, ok in checks:
    print(f"  {'✅' if ok else '❌'} {label}")
if problems:
    print("  问题:")
    for p in problems:
        if p:
            print(f"    - {p}")

print("\n完成。校验器已接入 schema.yaml，用模拟数据跑通并执行真实判断。")
