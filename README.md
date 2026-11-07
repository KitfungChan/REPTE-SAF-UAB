# L2Q3 数据模型

交付的「数据模型」= **schema.yaml + 可运行校验器 + ER 图**。

| 文件 | 说明 |
|---|---|
| `schema.yaml` | 题目定义（量表/方向/跳题资格）＋分母定义＋波次邀请数 |
| `validate.py` | 用内置模拟数据跑通：生成长表、算 Denominator/Metric、跑声明检查 |
| `entitats.svg` | ER 关系图（7 张表） |

## 三件套如何对应交付要求

- **可重复问卷** → `schema.yaml`（12 题预算里的题目元数据）
- **数据模型** → ER 图 + 长表 `Response`，每题自带 `Denominator.n`
- **原型** → `validate.py` 直接跑通，无依赖（纯 Python 标准库 + PyYAML）

## 跑起来
```powershell
cd model
$env:PYTHONIOENCODING="utf-8"; python validate.py
```

## 给 SAF 时记住的硬约束
- 每个数字必须写清：**出处、分母 n、和哪组比、单一时点**。
- 真实数据只用于本次竞赛，不上传公开仓库、不传出团队、不识别任何人（分组 n<30 不展示）。
