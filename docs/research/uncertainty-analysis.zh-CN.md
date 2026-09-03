[English](uncertainty-analysis.md) | [简体中文](uncertainty-analysis.zh-CN.md)

# 不确定性分析

## 衡量对象

研究闭环报告明确情景集合内的确定性敏感度。将一个具名干预与 reviewed baseline 对比后，归属发生变化的格网计为 affected cell。这些计数描述当前证据状态与后端的响应，不具有概率含义，也不能当作历史领土面积。

两个研究状态必须分开阅读：

- **Round 00**：定向取证之前的 epistemic state；诊断把成组情景拆成单项证据干预。
- **Round 01**：完成 Cairo、Edessa、Tripoli 搜索以及顺带进行的 Jaffa 复核之后的状态；诊断只报告相对于更新后基线仍未解决的反事实。

## Round 00：证据搜索优先级

Round-00 原子诊断在统一 10 km 格网上得到以下证据效应：

| 切片 | 决策干预 | 受影响格网数 |
|---|---|---:|
| 1130 | 加入 Ascalon | 1 |
| 1130 | 恢复 Edessa seed | 257 |
| 1130 | 加入 Tortosa | 0 |
| 1130 | 恢复 Tripoli seed | 220 |
| 1187 | 加入 Cairo | 1,162 |
| 1187 | 加入 Jaffa | 0 |

这些边际效应生成了第一轮搜索议程：Cairo、Edessa、Tripoli 的优先级高于 Ascalon；Tortosa 与 Jaffa 以零边际效应保留在诊断中。Cairo 的来源链提供了直接相关材料，因此 Jaffa 仍被顺带核查。

机器可读的依据是 [`rounds/00-initial/uncertainty-diagnosis.json`](../../cases/crusader_states/public/research/rounds/00-initial/uncertainty-diagnosis.json)。较早的 [`uncertainty-zones.png`](../../cases/crusader_states/public/figures/uncertainty-zones.png) 及配套 JSON 属于**冻结的 Round-00 v0.1 成组情景图**。其中 1130/1187 的百分比只用于复现该状态，不能表述为 Round-01 结果，也不能据此排列单项证据缺口。

## Round 01：更新后的基线与剩余不确定性

Round 01 先更新证据准入状态，再运行同一 XTENT 后端。基线之间的差异记录在 [`round-delta.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/round-delta.json)。

- **1130 年：**Rafaniyya 作为 Tripoli 的新增控制点获准进入模型后，改变 **0 个格网**；更新后的表面在声明格网上与 Round-00 基线完全相同。剩余证据干预为 Ascalon（**1 个格网**）与 Tortosa（**0 个格网**）。模型变体仍占主导：移除自然成本影响 196 个格网，normal reach 影响 3,412 个，expansive reach 影响 5,736 个。
- **1187 年：**Cairo 与 Jaffa 进入基线后改变 **1,162 个格网**，全部由未分配转为 Ayyubid Sultanate。Round-00 原子归因表明 1,162 个格网全部来自 Cairo，Jaffa 的边际效应为零。两项决策进入基线后，Round-01 证据轴没有剩余变体，因此影响 **0 个格网**。剩余诊断完全来自模型轴：移除自然成本影响 196 个格网，normal reach 影响 2,838 个，expansive reach 影响 5,182 个。

当前机器可读诊断为 [`uncertainty-diagnosis-1130.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/uncertainty-diagnosis-1130.json) 与 [`uncertainty-diagnosis-1187.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/uncertainty-diagnosis-1187.json)。项目没有声称生成 Round-01 分类不确定性 PNG；当前研究状态以这两份 JSON 为准。

## 解释边界

零边际效应不等于一项历史主张不重要，它只表示当前格网、后端、基线与干预次序没有产生归属变化。Cairo 带来的 1,162 格网扩张同样只记录新准入锚点触发的后端响应，不能用于验证 Ayyubid 边界或证明历史准确性。情景集合仍然有意保持有限，来源准入与 reach class 的合理性仍需历史学者判断。
