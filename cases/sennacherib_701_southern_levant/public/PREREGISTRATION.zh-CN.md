[English](PREREGISTRATION.md) | [简体中文](PREREGISTRATION.zh-CN.md)

# 预注册

## 冻结问题与范围

本案例考察：在辛那赫里布通常定年的**公元前 701 年第三次远征及其直接政治处置时段**，Joppa—Ekron—Lachish—Jerusalem 走廊中的哪些具名地点，可以被支持为 Judah、Ekron、Ashdod、Gaza、Ashkelon 的地方控制点、转移对象、争议地点或未解决地点。

时间保存为 `calendar=historical_bce_year_label`、`era=BCE`、`year_bce=701`、`temporal_resolution=campaign_horizon`。天文纪年 `-700` 按 `astronomical_year = 1 - year_bce` 计算，仅供机器运算；禁止负 ISO 日期。该时段不声称全部行动同时发生或达到日级精度。WGS84 范围为 `[34.0, 30.7, 35.5, 32.5]`。

## 证据与本体

允许逐行定位的楔形文字版本、发掘与定年报告、地方铭文、经过文本批判说明的希伯来文本见证、许可明确的 gazetteer、遗址坐标、地形、路线和水系。现有历史疆域地图及其主体、缩略图、图版、截图、OCR、矢量和派生内容，在评估 gate 前全部禁止。

本体严格区分地方王朝统治、权威争议、转移、亚述征服、贡赋、宗主权、军事存在、毁灭与地方行政。只有受支持、具名且适用于该时段的地方行政主张才能授权控制点。平行亚述铭文见证和现代译本默认属于同一条带立场的王室谱系，除非来源批判证明其独立。《希伯来圣经》材料必须保留文本层次、成书与依赖关系的不确定性。

每项纳入必须经过 `Source → Observation → Claim → Model Decision`。来源陈述不能跨层晋级，未具名的转移城镇不得获得虚构坐标。

## 搜索与重建 gate

冻结后的证据收集上限为 24 次查询、20 次正文记录检查、12 个来源纳入、每个 gap 两次 follow-up、4 次 held-out 元数据查询和 3 个 held-out 候选。gap 达到成功标准，或两次 follow-up 均无新增可采证据时即停止。

重建要求：至少两个实体各有两条相互独立、合法可访问、适用于时段且具名地点级的地方控制关系；至少 10 个可定位候选来自 4 条独立来源谱系；保留至少 2 项反证或排除；每个纳入来源均有稳定 locator 与权利记录。失败结果是 `NO_RECONSTRUCTION`，不能生成猜测性 polygon。

## Held-out 评估

候选顺序和 20 个分类评价单元冻结在 `preregistration.json`。每个单元必须记为 `aligned`、`not_aligned`、`not_expressed` 或 `not_comparable`，打开后不得缩减分母。可表达且可比较单元少于 8 个时，比较结论为 inconclusive。

地图主体继续封存，直至第二个 `reconstructed_pre_evaluation` Git commit 冻结有效证据状态、情景、代码、校准、输出、地点坐标、评分规则与哈希。held-out 内容永远不能回流到证据或调参。

## 修订与限制

冻结后的修订必须版本化，并在受影响分析开始前 commit。held-out 内容打开后，任何修改都属于 post hoc，不能替代预注册结果。

当前证据集中于带立场的亚述报告；Ashdod 与 Gaza 接收的是未具名地点；若干遗址对应仍待解决；圣经文本路径需要来源批判；atlas 也可能表达不足。仓库检查能建立材料隔离和声明一致性，不能证明人的完整浏览历史。
