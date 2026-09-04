[English](PREREGISTRATION.md) | [简体中文](PREREGISTRATION.zh-CN.md)

# 预注册

## 冻结的问题与范围

本案例研究 780-01-01 至 796-07-29 期间，Rhuddlan—upper Severn 走廊内哪些具名地点能由非疆域地图证据分类为 Mercian-controlled、named-Welsh-polity-controlled、contested 或 unresolved；若以后允许重建，则检验结果对 Offa’s Dyke 不同显式角色的敏感性。多数事件只能精确到年份，因此目标是区间，不能表述为 796 年 7 月 29 日精确政治快照。

WGS84 范围框为 `[-3.65, 52.05, -2.65, 53.40]`。Mercia、Powys 与 Gwynedd 是候选主体；在达到冻结准入门槛前必须保留 unresolved。“Britons”不得被编译成单一 Welsh state。

## 证据与谱系

允许的输入包括可定位文本、带真伪说明的宪章、考古与科学测年、历史环境记录、合法地名库、地形、水系、路线、聚落、地名研究及其他非疆域地图材料。禁止现成历史疆域地图及其主体或衍生物，也禁止把模型默认值写成证据。

所有获准路径必须保持 `Source → Observation → Claim → Model Decision`。一条 observation 只记录一个来源陈述或测量。事件、头衔、劫掠、贡赋、战役、工程位置与点控制都不能授权连续领土范围。只有得到支持且适用于目标区间的 claim 才能授权 admitted decision。

## Offa’s Dyke

Offa’s Dyke 是 `political_boundary_equivalence=false` 的争议对象。默认角色为 display context，当前情景把它排除出 allocation。指定工程段只有在独立证据支持其角色后，才能作为 traversal constraint、corridor、disputed clue 或 exclusion；禁止把它作为硬政治分割线。

## 搜索与停止规则

预注册 commit 后的预算为：24 次记录在案的 query、20 次内容或记录检查、12 个来源准入、每个缺口 2 次定向追查、6 次 held-out 元数据 query、3 个 held-out 候选。遇到以下首个适用条件即停止：达到重建门槛、预算耗尽、缺口达到成功条件，或两次定向追查没有增加合格证据。

重建要求至少两个主体分别具有两条独立、适用于区间的具名地点关系；至少 8 个空间候选来自 3 条独立来源谱系；至少保留 1 条反证或排除关系；每项准入都有稳定 locator 与明确权利。失败结果为 `NO_RECONSTRUCTION`，不得生成推测 polygon。

## Held-out 评估

候选优先级与 13 个分类评价单元已冻结在 `preregistration.json`。每项只能记为 `aligned`、`not_aligned`、`not_expressed` 或 `not_comparable`，打开后不得缩小分母。可表达且可比较单元少于 6 项时，比较结果必须判为 inconclusive。所报告的是在冻结规则下与一幅出版地图的一致程度，绝非历史准确率。

地图主体继续封存。首次打开前，必须再以一个 `reconstructed_pre_evaluation` commit 冻结 evidence bundle、情景、代码、校准、重建结果、地点坐标、评价规则与哈希。Held-out 材料永远不能回流到研究输入或调参。

## 冻结限制

Welsh 一侧的本地证据目前稀疏，且常为回顾性或略晚于目标区间。Rhuddlan 的参战方、结果与战场位置未解决。现存工程段的连续性与年代不一，政治功能没有成立。二元 allocation 可能抹去真实的未知区或边疆带。自动检查只能证明仓库材料隔离与声明一致，不能证明个人完整浏览历史。
