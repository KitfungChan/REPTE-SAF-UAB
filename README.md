# REPTE SAF UAB 2026 — 竞赛项目仓库

本仓库是 **REPTE SAF UAB 2026**（SAF 40 周年，11/7–8）竞赛项目的**整体仓库**。
本仓库收录本次竞赛的交付物与材料；不同部分（各队选题成果）集中在同一目录下。

> ⚠️ 真实 SAF 数据**禁止入仓**（竞赛规则）。`.gitignore` 已排除 `DADES/` 与原始表格/PDF。

## 选题：L2Q3「明年该测什么」

设计第二次问卷 / 第二次测量体系，使 SAF 能谈「retorn de veritat（真实回报）」：
**回报限于学生自评的 benestar / hàbit / pertinença（幸福感、习惯、归属感），非钱、非成绩。**

## 交付物（L2Q3）

| 文件 | 说明 |
|---|---|
| `2026-11-07-L2Q3-问卷原文.docx` | 可重复问卷原文 |
| `2026-11-07-L2Q3-测量体系攻坚方案.docx` | 选题与攻坚方案 |
| `SAF_L2Q3_presentacio.pptx` | 3 分钟演示稿 |
| `2026-11-07-L2Q3-给SAF的一页纸.pdf` | 给 SAF 的一页纸（3 条讯息） |
| `2026-11-07-L2Q3-数据模型模板.xlsx` | 数据模型模板 |
| `saf_enquesta_analisi.ipynb` | 问卷分析 notebook |

### 数据模型（schema + ER 图 + 可运行校验器）

数据模型的工程交付物，与上面文档配套。**`schema.yaml` 是唯一权威的机读数据模型来源**（题目 / 量表 / 方向 / 跳题资格 / 分母 / 波次）；其余文件围绕它，互不重复定义同一模型：

| 文件 | 说明 | 与 schema.yaml 的关系 |
|---|---|---|
| `schema.yaml` | 题目元数据＋分母定义＋波次邀请数 | **唯一权威机读来源** |
| `question_field_map.md` | 题号 ↔ 字段 ↔ 量表方向 ↔ 分母 ↔ 统计表 映射 | 由 schema.yaml 导出的人类可读索引 |
| `validate.py` | 用内置模拟数据跑通：生成长表、算 Denominator/Metric、跑声明检查 | 消费 schema.yaml 的运行器 |
| `entitats.svg` | ER 关系图（长表 `Response` + 显式分母 `Denominator`） | 由 `entitats.svg` 脚本生成（`.svg` 实为画图脚本，运行后产出图） |
| `saf_model_er.html` | ER 图静态预览（浏览器可直接打开） | `entitats.svg` 的产物预览 |
| `Postgres DDL 镜像` / `可运行的关系型 Schema 原型` | 早期关系型原型（`saf_model.py`，Storage/Dimension/Presentation 三层） | **参考 / 历史镜像**，非权威来源，勿当作模型定义二次修改 |

数据模型核心思路：**用长表替代原始 33 列宽表，每个百分比自带分母 n**，
把 2026 问卷的缺陷（分母无法复原、跳题口径不一致）改成立论。详见 `schema.yaml`。

## 硬约束（每个数字必须写清）

- **出处、分母 n、与哪组比、单一时点**
- 真实数据只用于本次竞赛；不上传公开仓库、不传出团队、不识别任何人（分组 n<30 不展示）

## 提交规范

- 真实 SAF 数据不入仓（见 `.gitignore`）
- 提交信息用简短中英文说明改动

## 参考文献

Harvey S B, Øverland S, Hatch S L, et al. Exercise and the prevention of depression: results of the HUNT cohort study[J]. American journal of psychiatry, 2018, 175(1): 28-36.

Cornelissen V A, Smart N A. Exercise training for blood pressure: a systematic review and meta‐analysis[J]. Journal of the American heart association, 2013, 2(1): e004473.

Rhodes R E, Smith N E I. Personality correlates of physical activity: a review and meta-analysis[J]. British journal of sports medicine, 2006, 40(12): 958-965.

Sutin A R, Stephan Y, Luchetti M, et al. The five-factor model of personality and physical inactivity: A meta-analysis of 16 samples[J]. Journal of research in personality, 2016, 63: 22-28.

Caille P, Stephan Y, Sutin A R, et al. Personality and change in physical activity across 3–10 years[J]. Psychology & health, 2024, 39(5): 670-690.
