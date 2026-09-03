[English](uncertainty-analysis.md) | [简体中文](uncertainty-analysis.zh-CN.md)

# 不确定性分析

## 问题

不确定性图衡量一组明确情景内部的归属一致性：当证据资格或模型选择改变时，哪些格网仍归于同一实体。它不是概率图，也不估计某实体在历史上控制一个格网的可能性。

## 情景集合

证据轴包含三个运行：

- `verified-only`：只使用页级核实的地点主张；
- `reviewed-baseline`：使用 KEEP 和已接受的 DOWNGRADE 决策；
- `inclusive`：在基线之外加入 1130 年有争议的阿斯卡隆与托尔托萨，以及 1187 年的开罗与 Jaffa。

模型轴固定 reviewed evidence，只改变求解器设置：

- `flat-natural` 移除黎巴嫩山和托罗斯山脉成本；
- `projection-normal` 与 `projection-expansive` 用另外两个允许等级对照 contracted 基线；
- `grid-5km` 与 `grid-20km` 在 10 km 基线两侧测试格网尺度。

八个具名情景全部定义在 `scenario-config.json`。写出图件前，流程会重新生成其有效输入和 run manifest。

## 分类规则

所有输出先栅格化到统一的 10 km 分析格网，再分为四类：

- **stable core**：证据情景组与模型情景组各自完全一致，且指向同一非零实体；
- **model-sensitive zone**：证据情景一致，至少一个模型变体改变归属；
- **evidence-sensitive zone**：模型情景一致，证据情景改变归属；
- **unresolved zone**：两组都变化、两组内部一致但彼此冲突，或只有一个轴产生归属。

所有情景都未分配的格网单独统计，在图中不着色。

## 结果

### 1130 年

在已评估表面中，stable core 占 13.65%，model-sensitive area 占 81.59%，evidence-sensitive area 占 1.31%，unresolved area 占 3.46%。证据情景组平均一致度为 0.9841，模型情景组为 0.7128。

较大的模型敏感区主要来自允许的 projection 等级，尤其是 expansive 运行，并非来自两个争议地点。证据敏感区主要集中在 Ascalon/Fatimid 与 Tortosa 新增点附近。埃德萨的降级通过降低种子权重影响基线范围，这仍属于需要人工接受的研究判断。

### 1187 年末

在已评估表面中，stable core 占 12.98%，model-sensitive area 占 75.44%，evidence-sensitive area 占 2.36%，unresolved area 占 9.22%。证据轴平均一致度为 0.9614，模型轴为 0.7191。

开罗在 inclusive 运行中增加了较大的西南影响场，Jaffa 改变较小的海岸区域。两者与 projection、格网变体相互作用，使 unresolved 比例高于 1130 年。stable core 靠近经过审查的地点锚点；这种稳定性只对当前情景设计成立，不具有概率含义。

## 图件读法

`uncertainty-zones.png` 使用分类颜色。绿色表示两个情景组中的所有运行都把该格网分给同一实体；橙色与紫色分别指出模型轴或证据轴造成的分歧；红色表示只按单一轴解释会产生误导。

面积值来自 10 km 分析格网，每个计数格对应 100 km²。它们是情景诊断量，不是中世纪领土实测面积。

## 局限与人工审查

当前情景集合刻意保持有限且结构化，没有抽样所有可能的历史解释、校准、自然要素或日期约定。历史学者仍需决定降级与争议输入是否可接受，以及 projection 范围是否构成合理的模型压力测试。
