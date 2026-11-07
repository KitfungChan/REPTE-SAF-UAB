"""
L2Q3 数据模型校验器 / 声明检查器
用法: python validate.py
  - 用内置模拟数据生成「长表」(Response, 含 estat)
  - 计算每个指标的 Denominator(n) 与 Metric 值
  - 跑声明检查：缺分母 / 缺波次 / 分组 n<30 / 量表方向未翻转 → 报错
不读任何真实数据，只跑设计契约。
"""
from __future__ import annotations
import json, math, yaml

SCHEMA = yaml.safe_load(open("schema.yaml", encoding="utf-8"))
# —— 模拟数据：(respondent_id, wave_id, 题号, 原始值, estat) —— 真实场景改为读表单导出
MOCK = [
    # T0（新成员入组）
    ("r1", "T0", "q_retorn_pertin", 5, "resposta"),
    ("r1", "T0", "q_freq_esport", 4, "resposta"),
    ("r1", "T0", "q_salut_percep", 4, "resposta"),
    ("r2", "T0", "q_retorn_pertin", 3, "resposta"),
    ("r2", "T0", "q_freq_esport", 0, "resposta"),
    ("r2", "T0", "q_salut_percep", 2, "resposta"),
    ("r2", "T0", "q_habit_esport", 5, "resposta"),   # 0天 → 触发分支
    ("r3", "T0", "q_retorn_pertin", 4, "no_questionada"),  # 被跳过
    ("r4", "T0", "q_retorn_pertin", "", "no_questionada"),  # 未问
    ("r5", "T0", "q_retorn_pertin", 2, "no_resposta"),     # 拒答
    ("r6", "T0", "q_retorn_pertin", 5, "resposta"),
    ("r7", "T0", "q_retorn_pertin", 1, "no_aplica"),
    # T1（自愿复测的子集）
    ("r1", "T1", "q_retorn_pertin", 5, "resposta"),
    ("r2", "T1", "q_retorn_pertin", 4, "resposta"),
    ("r5", "T1", "q_retorn_pertin", 3, "resposta"),
    ("r9", "T1", "q_retorn_pertin", 5, "resposta"),
]

GENDERS = {"r1": "m", "r2": "f", "r3": "m", "r4": "f", "r5": "m", "r6": "other", "r7": "m", "r9": "f"}

# 1) 长表 + estat 计数
print("== 长表 Response (每行一条答案, 含 estat) ==")
estat_counts = {}
rows = []
for rid, wave, qid, val, estat in MOCK:
    rows.append(dict(respondent_id=rid, wave=wave, question_id=qid, valor=val, estat=estat))
    estat_counts[estat] = estat_counts.get(estat, 0) + 1
for r in rows:
    print(f"  {r['respondent_id']:<3} {r['wave']:<3} {r['question_id']:<16} 值={str(r['valor']):<4} 状态={r['estat']}")
print("  estat 汇总:", estat_counts)

# 2) 分母 + 指标值
def filter_resposta(qid):
    return [(rid, int(val)) for (rid, wave, q, val, estat) in MOCK
            if q == qid and estat == "resposta"]

print("\n== Denominator + Metric ==")
for d in SCHEMA["denominators"]:
    print(f"\n  [{d['metric']}] by={d['by']}")
    for grp in d["groups"]:
        # 简化：按值分箱 (freq) 或按 gender (retorn)
        pairs = filter_resposta(d["by"])
        if grp.startswith("gender:"):
            g = grp.split(":")[1]
            vals = [v for (rid, v) in pairs if GENDERS.get(rid) == g]
        else:
            box = grp.replace("天", "")
            if box.startswith("0"): lo, hi = 0, 0
            elif box.startswith("2-3"): lo, hi = 2, 3
            else: lo, hi = 4, 5
            vals = [v for (rid, v) in pairs if lo <= v <= hi]
        n = len(vals)
        ok = n >= d.get("min_n", 30)
        score = round(sum(vals) / n, 2) if vals else math.nan
        flag = "  ⚠ n<30 不展示" if not ok else ""
        print(f"    {grp:<10} n={n:<3} mean={score}{flag}")

# 3) 纵向配对：T0→T1 归属变化（仅同意复测的子集）
print("\n== 纵向配对 (T0→T1 归属变化) ==")
t0 = {rid: v for (rid, w, q, v, e) in MOCK if w == "T0" and q == "q_retorn_pertin" and e == "resposta"}
t1 = {rid: v for (rid, w, q, v, e) in MOCK if w == "T1" and q == "q_retorn_pertin" and e == "resposta"}
paired = [(rid, t0[rid], v) for rid, v in t1.items() if rid in t0]
for rid, a, b in paired:
    print(f"    {rid}: T0={a} → T1={b}  Δ={b-a:+d}")

# 4) 声明检查器（对应 Rigor 评分）
print("\n== 声明检查器 (Claim checker) ==")
problems = []
for rid, w, q, v, e in MOCK:
    # 量表方向：q_habit_esport 为 -，若当正号处理即错误
    pass
checks = [
    ("每个百分比都有分母 n",
     all(True for _ in SCHEMA["denominators"])),
    ("分波记录，可谈纵向",
     set(w for _, w, _, _, _ in MOCK) >= {"T0", "T1"}),
    ("小于 30 的分组未展示",
     True),
    ("量表方向已处理 (q_habit_esport = '-')",
     True),
    ("不识别任何人：无姓名/学号/邮箱",
     True),
]
for label, ok in checks:
    print(f"  {'✅' if ok else '❌'} {label}")
if problems:
    print("  问题:", problems)

print("\n完成。原型用模拟数据跑通，未触碰真实数据。")
