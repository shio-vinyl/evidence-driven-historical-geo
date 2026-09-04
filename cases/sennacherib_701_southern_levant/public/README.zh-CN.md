[English](README.md) | [简体中文](README.zh-CN.md)

# 辛那赫里布 701 年南黎凡特 Prospective 案例

**严格预注册 · completed_no_reconstruction · held-out 材料永久封存**

本 prospective 案例研究通常定年的**公元前 701 年第三次远征及其直接政治处置时段**中的 Joppa—Ekron—Lachish—Jerusalem 走廊。该时段不构成日级快照。时间使用明确的 BCE era/year 字段保存；天文纪年 `-700` 仅供计算。

## 终局裁决

有限审计给出**预注册与证据收集 GO**。随后严格运行冻结的 reconstruction gate，结论为 **NO-GO**，案例以无重建状态完结。冻结后 round 使用 24 次查询预算中的 16 次、全部 20 次正文/记录检查，以及 12 个来源准入预算中的 7 个。每个登记 gap 均执行了两轮允许的定向 follow-up。

五个候选实体具有文本路径：Judah、Ekron、Ashdod、Gaza、Ashkelon。冻结 12 个地点候选：Joppa、Ekron、Lachish、Jerusalem、Ashdod、Gaza、Ashkelon、Bīt-Daganna/Beth-Dagon、Banayabarqa/Bene-Baraq、Azuru、Eltekeh、Timnah。目前没有任何地点成为分配 seed。

Gate 失败原因明确：没有两个实体分别具备两条独立、合法可访问、适用于该时段的具名地点地方控制关系。Judah 与 Ekron 各自最多只有一个合格地点；Ashkelon 的多个具名关系只来自一条带立场的王室谱系；Ashdod 与 Gaza 得到的是未具名城镇。因此 modeled entity roster 为空。

## 证据边界

亚述征服、贡赋、宗主权、军事存在、地方王朝统治、转移、毁灭与地方行政保持分层。ORACC 的平行见证属于同一条带立场的王室谱系。Lachish 毁灭是事件观察，不是控制关系。《希伯来圣经》路径在完成文本层次、成书与依赖关系审查前，不进入独立确认计数。

Reviewed round 以明确约束关闭毁灭年代与《希伯来圣经》谱系 gap，以 exclusion 关闭 Ashdod 与 Gaza 的未具名转移 gap，并将 Judah、Ashkelon、Ekron 与地点识别 gap 关闭为 unresolved。没有获取坐标、land mask、DEM、路线、水系或考古点图层。没有运行场景求解器或敏感性分析，也不存在 polygon、territorial surface 或重建输出；由于模型未运行，model-dominated 判定不适用。

## Prospective 封存

*The Carta Bible Atlas* 仅按书目元数据登记。*Oxford Bible Atlas* 与 *The Bible Atlas* 因搜索结果暴露封面缩略图或地图标签摘要而被排除。没有打开或保存任何历史疆域地图主体、图版、PDF 地图页、截图、OCR、矢量或派生内容。

第一次 Git freeze 仍逐字节绑定原有 9 个机器可读材料。冻结后证据保存在 append-only reviewed round 及其 SHA-256 manifest 中。由于 reconstruction gate 失败，本案例不存在 `reconstructed_pre_evaluation` freeze，held-out 内容不得打开。

## 文件

- [可行性审计](feasibility-audit.zh-CN.md)与[英文版](feasibility-audit.md)
- [人类可读预注册](PREREGISTRATION.zh-CN.md)与[英文版](PREREGISTRATION.md)
- `preregistration.json`：冻结问题、范围、本体、预算、gate 与评价单元
- `research-bundle.json`：冻结前披露的 Source → Observation → Claim → Model Decision 状态
- `held-out-map-register.json`：仅含封存的书目元数据
- `spatial-input-contract.json`：12 个冻结地点候选及 no-input/no-polygon gate
- `preregistration-freeze.json`：SHA-256 manifest
- `research/rounds/01-non-map-evidence/`：精确查询、来源检查、观察、主张、决策、gap 结果、预算、gate 与 SHA-256 manifest
- `lifecycle.json`：终止于 `completed_no_reconstruction` 的 append-only 生命周期

仅验证、不重建：

```bash
historical-geo validate cases/sennacherib_701_southern_levant/public
```
