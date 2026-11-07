# L2Q3 题号 ↔ 字段ID ↔ 量表方向 ↔ 分母 ↔ 统计表 映射表

> 覆盖问卷全部 15 题（含 E1/E2 拆分子字段），共 **17 类 question**（24 行字段）。
> 用途：任何分析脚本可按「一题一字段」对齐，列顺序为：
> **问卷题号 / 字段ID / 量表(escalar) / 方向(sentit) / 分母(denominators) / 对应 estat / 2026列 / 备注**

## 说明

- **量表 escalar**：`categorical`(类别/名义)·`binary`(0-1)·`ordinal`(有序)·`interval`(区间)·`ratio`(比率)。
- **方向 sentit**：`positive`(越大越好)/`negative`(越大越差)；binary/categorical 填 `-`。
- **preguntada_a**：`well_defined`(全体)/`well_defined_n_excluded`(仅某子群，剔除其他)。
- **track_pairing**：`true` 仅 `canvi_benestar`(纵向锚点)。
- **分母**：`all_valid`(全体有效)·`movers_n`(运动者 A3∈{1,2})·`abonat_sisi`(会员 Sí)·`nonmovers_n`(非运动者 A3=3，目标 ≥150)。
- **n 门槛**：结论 n_min_conclusion=30；n_min_privacy=30 为隐私阈值**建议**，≠隐私保证；分组 n<30 不展示。

## 映射表

| 问卷题号 | 字段ID | 量表(escalar) | 方向(sentit) | 分母(denominators) | 对应 estat | 2026列 | 备注 |
|---|---|---|---|---|---|---|---|
| A1 性别 | generes | categorical | - | all_valid | pertinencia_generes | col2 | 男/女/非二元/无意见；用于性别×归属跨表 |
| A3 运动情况 | situacio | categorical | - | all_valid | situacio_grups | col4 | **分组枢纽**：{1,2}→运动者 movers_n；{3}→非运动者 nonmovers_n；preguntada_a=well_defined_n_excluded |
| A4 是否会员 | abonat | binary | - | abonat_sisi | abonat_grups | col5 | Sí/No；分母为会员数 |
| B1 运动频率 | frecuencia | ordinal | positive | movers_n | freq_esport | col16(缺106) | 1=1次/周…4=超5次；4天阈值判定；仅运动者 |
| B3 是否达标 | habit_estar | ordinal | positive | movers_n | habit_arrel | — | 1=没达到,2=基本达到,3=达到；仅运动者 |
| C1 身体健康 | salut_fisica | interval | positive | all_valid | salut_fisica | col11-15 | int 1-5；全体正向 |
| C2 情绪 | stat_emocional | interval | positive | all_valid | stat_emocional | col16-19 | int 1-5；全体正向 |
| C3 睡眠小时数 | son_hores | ordinal | - | all_valid | son_hores | col20-23 | ordered int 区间 0-1…>9；非单调故 sentit=- |
| C3 睡眠质量 | son_qualitat | interval | positive | all_valid | son_qualitat | col24-27 | int 1-5；全体正向（与小时数拆分） |
| C4 压力 | estres | ordinal | negative | all_valid | estres_freq | col28-31 | 频率向 Mai…Molt sovint；反向计分 |
| C5 好处 | beneficis | interval | positive | movers_n | benefici_movers | col32-36 | int 1-5；仅运动者 |
| D1 联结/归属感 | pertinenca | interval | positive | all_valid | pertinencia | col37-40 | int 1-5；全体正向 |
| E1 障碍(1) | obstacle_1 | binary | - | nonmovers_n | obstacles_noesport | 新增 | 没时间/学习忙；0/1 |
| E1 障碍(2) | obstacle_2 | binary | - | nonmovers_n | obstacles_noesport | 新增 | 距离远/无交通；0/1 |
| E1 障碍(3) | obstacle_3 | binary | - | nonmovers_n | obstacles_noesport | 新增 | 费用高/无会员优惠；0/1 |
| E1 障碍(4) | obstacle_4 | binary | - | nonmovers_n | obstacles_noesport | 新增 | 不感兴趣/无偏好；0/1 |
| E1 障碍(5) | obstacle_5 | binary | - | nonmovers_n | obstacles_noesport | 新增 | 身体原因/伤病；0/1 |
| E1 障碍(6) | obstacle_6 | binary | - | nonmovers_n | obstacles_noesport | 新增 | 缺少伙伴；0/1 |
| E1 障碍(7) | obstacle_7 | binary | - | nonmovers_n | obstacles_noesport | 新增 | 缺乏更衣室/设施；0/1 |
| E2 意向(价格优惠) | intencio_1 | interval | positive | nonmovers_n | intencio_noesport | 新增 | 4 类激励拆字段；int 1-5 |
| E2 意向(时间灵活) | intencio_2 | interval | positive | nonmovers_n | intencio_noesport | 新增 | 时间/课程灵活性；int 1-5 |
| E2 意向(社交社群) | intencio_3 | interval | positive | nonmovers_n | intencio_noesport | 新增 | 社交/同伴/社群；int 1-5 |
| E2 意向(健康指导) | intencio_4 | interval | positive | nonmovers_n | intencio_noesport | 新增 | 健康收益/指导；int 1-5 |
| E3 纵向锚点 | canvi_benestar | ordinal | positive | all_valid | canvi_benestar_panel | 新增·纵向 | 一年前比较，负→正；track_pairing=true |

## 分母字典(denominators)

| name | 口径 | n_min_conclusion | n_min_privacy | 目标_n | 用途 |
|---|---|---|---|---|---|
| all_valid | 全体有效回收 | 30 | 30 | — | A1/A3/A4/C1/C2/C3/C4/D1/E3 |
| movers_n | 运动者 A3∈{1,2} | 30 | 30 | — | B1/B3/C5（缺106） |
| abonat_sisi | 会员 A4=Sí | 30 | 30 | — | A4 会员占比 |
| nonmovers_n | 非运动者 A3=3 | 30 | 30 | ≥150 | E1 障碍 / E2 意向 |

> 注：`n_min_privacy=30` 仅为**隐私阈值建议**，不等于隐私保证；真实数据不入仓，分组 n<30 不展示。

## 统计表(metrics)一览

| metric | by（字段） | denominator | table | 方向 |
|---|---|---|---|---|
| situacio_grups | situacio | all_valid | situacio_grups | — |
| abonat_grups | abonat | abonat_sisi | abonat_grups | — |
| freq_esport | frecuencia | movers_n | freq_esport | + |
| habit_arrel | habit_estar | movers_n | habit_arrel | + |
| salut_fisica | salut_fisica | all_valid | salut_fisica | + |
| stat_emocional | stat_emocional | all_valid | stat_emocional | + |
| son_hores | son_hores | all_valid | son_hores | - |
| son_qualitat | son_qualitat | all_valid | son_qualitat | + |
| estres_freq | estres | all_valid | estres_freq | - |
| benefici_movers | beneficis | movers_n | benefici_movers | + |
| pertinencia_generes | pertinenca × generes | all_valid | pertinencia_generes | + |
| pertinencia | pertinenca | all_valid | pertinencia | + |
| obstacles_noesport | obstacle_1..7 | nonmovers_n | obstacles_noesport | — |
| intencio_noesport | intencio_1..4 | nonmovers_n | intencio_noesport | + |
| canvi_benestar_panel | canvi_benestar | all_valid | canvi_benestar_panel | +（纵向配对） |
