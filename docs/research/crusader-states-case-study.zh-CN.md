[English](crusader-states-case-study.md) | [简体中文](crusader-states-case-study.zh-CN.md)

# 十字军诸国案例研究

## 范围

本案例用 **1130 年**和 **1187 年末**两个受限切片测试由 Agent 主导的“证据—空间假说”闭环。证据获取阶段不向 Agent 提供现成历史疆域图；这些地图只登记为后续 held-out evaluation 材料。

当前写入仓库的 epistemic state 包含 23 个来源、63 条 observation、23 条 claim、33 项 model decision 和 9 个 evidence gap。任何地点要影响 XTENT backend，都必须依次经过 source、observation、claim 和显式 model decision。仓库保存引用、项目短释义、带出处的近似坐标、裁剪后的公有领域自然要素和机器可读审查记录，不再分发来源 PDF、地图集页面或沿受版权保护地图描出的几何。

## Round 01：第一次完成的研究闭环

Round 00 用单项 decision 反事实诊断候选证据缺口。其冻结的 before-state 保存为 [`research-bundle.snapshot.json`](../../cases/crusader_states/public/research/rounds/00-initial/research-bundle.snapshot.json) 与 [`research-scenarios.snapshot.json`](../../cases/crusader_states/public/research/rounds/00-initial/research-scenarios.snapshot.json)；这两个 snapshot 可复现经过审查的 v0.1 求解器输入，Round 01 则有意改变当前状态。Cairo 影响 1,162 个格网，Edessa 影响 257 个，Tripoli 影响 220 个，Ascalon 影响 1 个；Jaffa 与 Tortosa 的单项影响均为 0。Agent 据此定向检索 Cairo、Edessa 与 Tripoli，没有选择 Ascalon。Jaffa 来自 Cairo 检索路径中的附带核查，构成零边际影响对照。

Round 01 完成了四项范围受限的证据更新：

| 缺口 | 证据结果 | Epistemic state 变化 |
|---|---|---|
| 1187 年 Cairo | Lane-Poole p. 219 明确写到 al-Adil 从 Cairo 出发；Ibn Shaddad 补充埃及行政与动员背景。 | Cairo 从 unresolved/disputed 转为 supported，并作为 operational locality point 进入基线。 |
| 1130 年 Edessa | Asbridge pp. 125–126 的论述覆盖到该节 1130 年终点；William of Tyre 提供相邻年份旁证。 | 一年时间桥接缺口关闭；Edessa 继续以 minor 权重进入基线。 |
| 1130 年 Tripoli 内陆证据 | Lewis 将 Rafaniyya 由伯国持有的时段限定在 1126—1137 年；Syriaca.org 提供近似位置。 | 新增 supported 的 Rafaniyya minor control point 并纳入基线。 |
| 1187 年 Jaffa | Lane-Poole 记载其被攻取；另有同时代书信通过 Kauffeldt 的转录与引文得到核查。 | Jaffa 从 unresolved/disputed 转为 supported 并进入基线；其单项空间影响仍为 0 格网。 |

完整检索记录见 [`source-checks.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/source-checks.json)，全部对象级状态迁移见 [`state-changes.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/state-changes.json)。检索记录中的 held-out guard 明确说明本轮没有查阅历史疆域图。

## 当前切片定义

1130 年 reviewed baseline 包含 5 个建模实体：Kingdom of Jerusalem、Burid Damascus、County of Tripoli、Principality of Antioch 和 County of Edessa。Tripoli 现有 Tripoli 与 Rafaniyya 两个地点约束。Fatimid Egypt 仍未进入基线，因为 Ascalon 仍为 experimental；Tortosa 同样为 experimental。1130 年 `inclusive` 只额外加入 Ascalon 与 Tortosa。

1187 年末 reviewed baseline 包含 Ayyubid Sultanate，以及以 Tyre、Tripoli、Antioch 三个幸存拉丁中心表示的 Kingdom of Jerusalem、County of Tripoli 与 Principality of Antioch。Cairo 与 Jaffa 现已作为 Ayyubid 地点进入基线。因此，1187 年的 `verified-only`、`reviewed-baseline` 与 `inclusive` 当前重合。

地点只约束本地位置与求解器分配，不能单独证明政体边界、点之间的连续控制或周边区域归属。

## 证据更新后的空间响应

轮次间重建差异记录在 [`round-delta.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/round-delta.json)。在当前 XTENT ordinal backend 与既定 10 km 分析格网下：

- 1130 年新增 Rafaniyya 后，13,924 个分析格网中有 **0 个**改变分配。该地点完善了审计状态，但没有改变当前 backend 的表面。
- 1187 年纳入 Cairo 与 Jaffa 后，13,924 个分析格网中有 **1,162 个**改变分配，全部由 unassigned 转为 Ayyubid Sultanate。该响应来自 Cairo；Jaffa 的单项边际影响为 0。

这些数值只衡量 backend 对已审计状态变化的响应，不能衡量历史准确性，也不能验证边界。

[`cases/crusader_states/public/figures`](../../cases/crusader_states/public/figures/README.md) 中的重建、锚点、自然要素消融和 attractor 图已由当前 Round-01 v0.2 状态重新生成。外部地图比较与成组情景一致性图仍明确冻结在 Round 00，避免静默改写 held-out evaluation 记录。

## 当前不确定性诊断

更新后的 1130 年诊断把 1 个 evidence-sensitive 格网归因于仍为 experimental 的 Ascalon；Tortosa 的单项影响为 0。模型情景影响 5,823 个格网。该切片下一轮唯一证据检索目标是 Ascalon。

更新后的 1187 年诊断不含 evidence-axis intervention，因为所有已纳入的地点 decision 目前都达到项目的页级核查标准。模型情景影响 5,269 个格网，因此该切片归类为 model-sensitive，不生成下一轮证据检索目标。完整记录见 [`uncertainty-diagnosis-1130.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/uncertainty-diagnosis-1130.json) 与 [`uncertainty-diagnosis-1187.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/uncertainty-diagnosis-1187.json)。

黎巴嫩山与托罗斯山脉继续作为显式标注的摩擦假设。约旦河继续作为展示背景和被拒绝的边界吸引器候选。它们属于模型 decision，不构成历史边界证据。

## 开放问题与人工审查边界

目前还有 5 个开放缺口：1130 年 Ascalon、1130 年 Tortosa、1187 年末幸存拉丁据点的范围，以及两个切片各自的 reach-class 敏感性。前两项可触发受限证据检索；survival-extent 缺口需要更多地点或路线证据；两个 reach 缺口主要需要模型诊断。

工作流关闭缺口并不等于史学争议已经解决。历史学者仍需判断：二手文献的明确地点表述与一手材料的行政背景能否支持 Cairo operational point；转录的同时代书信与 Lane-Poole 能否在精确年末口径下支持 Jaffa；Asbridge 的论述能否充分解决 Edessa 的 1130 年时间问题；Rafaniyya 的占有时段与近似 gazetteer 坐标能否支持 minor solver seed。本项目主张的是可审计的地点级输入和显式 backend 后果，不宣称恢复出历史边界。
