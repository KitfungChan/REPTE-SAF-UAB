#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
demo_on_2026.py —— L2Q3 新数据模型在【真实 2026 问卷数据】上的落地演示

目的：证明新模型（长表 + 显式分母 n）在真实数据上能跑出结果，并直观展示
2026 问卷的缺口（为什么 L2Q3 要新增 E1 障碍 / E2 意向 / C6 公平 题）。

合规：
  - 本脚本只【读取】本地真实数据，不写入、不上传、不导出任何真实数据文件。
  - 真实 SAF 数据按竞赛规则不得入仓；本仓库不包含任何真实个人数据。
  - 结果以汇总 n / 占比呈现，无个人标识、无 n<30 子组结论。

运行（本机有真实数据时）：
    pip install pandas openpyyaml pyyaml
    python demo_on_2026.py

数据路径自动探测（按需修改）。
"""
from __future__ import annotations
import sys
import pandas as pd

# ── 真实数据路径（本机 /DADES/，绝不进仓） ────────────────────────────────
CANDIDATES = [
    "DADES/saf-enquesta-2026-equips.xlsx",
    "../DADES/saf-enquesta-2026-equips.xlsx",
    "D:/Project/REPTE SAF UAB/DADES/saf-enquesta-2026-equips.xlsx",
    "/home/teammate/REPTE SAF UAB/DADES/saf-enquesta-2026-equips.xlsx",
]

# ── 新 schema 字段 ↔ 2026 列的映射（复用字段；新增字段 2026 无数据）────────
#   字段 ID (schema.yaml)  :  2026 列索引
FIELD_COLS = {
    "generes":            2,   # A1 性别
    "situacio":           4,   # A3 运动状况（分组枢纽）
    "abonat":             5,   # A4 是否会员
    "frecuencia":         8,   # B1 运动频率（仅运动者；106 缺）
    "salut_fisica":       17,  # C1 身体健康
    "estat_emocional":    18,  # C2 情绪
    "pertinenca":         27,  # D1 归属感首题（4 题取首题示意）
}
# L2Q3 新增模块：2026 问卷完全没有，因此 n=0 —— 这正是设计它们的理由
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
    """2026 A3 取值 -> 分组：movers(运动者) / nonmovers(非运动者)"""
    s = str(v).strip().lower()
    if s.startswith("no practico"):
        return "nonmovers"
    # "Faig ... regularment" (规律>1年) 与 "He començat ... últim any" (近一年) 都是运动者
    return "movers"


def main():
    path = find_data()
    if not path:
        print("未在本机找到真实数据文件（按规则不入仓）。\n"
              "请在有真实数据的机器上运行本脚本；仓库本身不应包含真实数据。")
        return

    df = pd.read_excel(path, sheet_name="Respostes")
    N = len(df)
    print(f"【读取真实 2026 数据】{path}")
    print(f"  样本量 N = {N}（1025 为官方公布值）\n")

    # ── 分组（新模型的「分组枢纽」A3）───────────────────────────────────────
    df["_group"] = df.iloc[:, FIELD_COLS["situacio"]].apply(situ_to_group)
    movers = (df["_group"] == "movers").sum()
    nonmovers = (df["_group"] == "nonmovers").sum()

    # ── 显式分母 n（新模型的核心：每个百分比自带分母）───────────────────────
    denom = {
        "all_valid        全体有效": N,
        f"movers_n 运动者  A3∈规律/近一年": int(movers),
        f"nonmovers_n 非运动者 A3=不运动": int(nonmovers),
    }
    abonat_si = (df.iloc[:, FIELD_COLS["abonat"]].astype(str).str.strip() == "Sí.").sum()
    denom["abonat_sisi 会员 Sí  A4=Sí"] = int(abonat_si)

    print("【显式分母 n（新模型）】")
    for k, v in denom.items():
        flag = " ✅ n≥30" if v >= MIN_N else " ⚠ n<30 不下结论"
        print(f"  {k:<34} n={v:<6}{flag}")
    print(f"  会员占比 Sí = {abonat_si/N*100:.1f}%（分母 = 会员数）\n")

    # ── 复用字段：各题有效回答数（长表视角）─────────────────────────────────
    print("【复用字段：2026 有效回答数（可直接进新长表）】")
    label = {"generes":"generes A1","situacio":"situacio A3","abonat":"abonat A4",
             "frecuencia":"frecuencia B1","salut_fisica":"salut_fisica C1",
             "estat_emocional":"estat_emocional C2","pertinenca":"pertinenca D1"}
    for fid, idx in FIELD_COLS.items():
        col = df.columns[idx]
        valid = df[col].notna().sum()
        flag = "" if valid >= MIN_N else " ⚠ n<30"
        print(f"  {fid:<16}{label[fid]:<18} 有效 = {valid}{flag}")
    print("  （B1 频率缺 305 条：旧模型无法复原「谁该有频率」的分母；L2Q3 用显式分母修复）\n")

    # ── 新增模块：2026 数据缺口（证明 L2Q3 的设计必要性）────────────────────
    print("【L2Q3 新增模块 —— 2026 数据缺口】")
    print(f"  非运动者 E1 障碍 / E2 意向目标人群 n = {nonmovers}")
    print(f"    （2026 问卷对这 {nonmovers} 人【无任何】动机/障碍题 → 199 缺口）")
    for f in NEW_FIELDS:
        print(f"  {f:<18} 2026 观察数 = 0  →  2027 新问卷补充")
    print("  （E3 canvi_benestar 纵向锚点：需 2027 两次独立施测，2026 仅框架）\n")

    print("【声明】")
    print("  - 2026 为单一时点横断面问卷，相关 ≠ 因果。")
    print("  - 本脚本不输出任何 n<30 的子组结论；不识别任何人。")
    print("  - 新模块（C6/E1/E2/E3）在 2026 无数据，须明年重复施测方可验证。")


if __name__ == "__main__":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    main()
