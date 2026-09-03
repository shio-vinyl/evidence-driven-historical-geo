[English](crusader-states-case-study.md) | [简体中文](crusader-states-case-study.zh-CN.md)

# 十字军诸国案例研究

## 范围

本案例用 **1130 年**和 **1187 年末**两个受限切片测试由 Agent 主导的 evidence-to-XTENT 工作流。Agent 负责搜集并核查来源，区分城市点控制、政治中心和战役事件，处理 7 组承重缺口，并围绕无法关闭的争议构建情景。

Fixture 保存引用、项目短释义、GeoNames 近似点、裁剪后的公有领域自然要素和机器可读审查记录，不包含来源 PDF、地图集页面或沿受版权保护地图描出的几何。

## 切片定义

1130 切片表现多政体格局。reviewed-baseline 现包含 Jerusalem、Burid Damascus、Tripoli、Antioch 与 Edessa。Fatimid Egypt 没有进入基线，因为公开案例中唯一种子 Ascalon 仍属争议。inclusive 情景加入 Ascalon 与 Tortosa，用于敏感性测试。

1187 年末切片使用明确的年末约定。基线包含一个 Ayyubid 表面，以及 Tyre、Tripoli、Antioch 三个拉丁中心。Cairo 与 Jaffa 不进入基线，只在 inclusive 情景激活。

## 证据决策

原来处于部分核实或未解决状态的 7 组主张，现已分别处理。

| 组别 | 决策 | 对基线的影响 |
|---|---|---|
| 1187 海岸分组中的 Jaffa | DISPUTED | 移出基线，只进 inclusive。 |
| 1130 年 Ascalon | DISPUTED | Fatimid Egypt 不进入基线，只进 inclusive。 |
| 1187 年 Cairo/Damascus | DOWNGRADE | 保留 Damascus，Cairo 只进 inclusive。 |
| 1187 年 Antioch | KEEP | 保留城市点，不推断周边领地。 |
| 使用相邻 1131 材料的 Edessa | DOWNGRADE | 保留，但种子权重降为 minor。 |
| 1130 年 Tripoli/Tortosa | DOWNGRADE | 保留 Tripoli，Tortosa 只进 inclusive。 |
| 1187 年末 Tripoli | KEEP | 保留城市点，内陆伯国范围继续未解决。 |

机器可读表位于 `historical-claim-decisions.json`。Lineage 同步保存这些决定，已移出基线的输入不会通过 adapter 默认值返回。

## 重建结果

![1130 年与 1187 年末边界假说](../../cases/crusader_states/public/figures/reconstruction-slices.png)

reviewed-baseline 在 1130 年保留 5 个实体，1187 年保留 4 个实体。所有表面有效且无重叠。点位所有权规则只保证经过审查的地点在其栅格中可见，不授予更大领土。

生成边缘仍是格网推导的边界假说。1130 年缺失的 Fatimid 表面记录的是证据决策，不表示 Fatimid 政体在历史上不存在。

## 外部比较

![分类式外部比较](../../cases/crusader_states/public/figures/reference-comparison.png)

公有领域 Shepherd 约 1140 年地图表达 17 项城市、实体与邻接断言，其中 12 项与基线一致。主要参考资料独有项包括 Ascalon、Tortosa、Fatimid Egypt，以及两项受 Fatimid 表面缺失或模型几何影响的邻接。

在 1187 比较中，Shepherd 约 1190 年地图表达的 4 个实体全部一致。Johnston 1187—1190 战役图有 14 项城市与实体断言，其中 13 项一致；唯一参考资料独有城市是 Jaffa。Buck 精确 1130 地图已登记，但合法预览没有开放受版权保护的地图页，因此未作提取。

## 情景分析

![情景一致性区域](../../cases/crusader_states/public/figures/uncertainty-zones.png)

8 个情景覆盖 verified-only 证据、reviewed-baseline、争议输入、移除自然成本、两个更宽 projection 等级，以及 5/10/20 km 格网。1130 年 assessed cells 中 stable core 占 13.65%，model-sensitive 占 81.59%。1187 年 stable core 占 12.98%，model-sensitive 占 75.44%，evidence-sensitive 占 2.36%，unresolved 占 9.22%。

明显的 projection 响应本身就是结果：当前稀疏点集更容易支持稳定的局部核心，难以支持稳定的区域范围。

## 自然成本与边界吸引器

黎巴嫩山和托罗斯山脉继续作为明确标注的成本假设。`flat-natural` 移除两者；对称差只用于模型诊断。

约旦河仍是展示背景和被拒绝的真实吸引器候选。其方向相似度为 `0.0209`，低于 `0.8` 要求，因此源几何保持不变。现代线要素不会因为距离接近就成为历史边界证据。

## 核验

案例通过公开谱系验证、全部必要情景重建、实体保留、几何有效、无重叠、6 张图件 QA 与 fixture 哈希核验。完整命令和生成物见[复现指南](../operations/reproducibility.zh-CN.md)。

## 仍需历史学审查

代码无法决定相邻年份的 Edessa 材料是否可接受，“sultan of Egypt” 能否授权 Cairo 点，Jaffa 是否应在原始页级缺口存在时服从战役图，以及约 1140 或约 1190 代理图应获得多大时间权重。在历史学者接受或修订这些判断前，项目继续保持 research prototype 定位。
