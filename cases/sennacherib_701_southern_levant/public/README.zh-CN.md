[English](README.md) | [简体中文](README.zh-CN.md)

# 辛那赫里布 701 年南黎凡特 Prospective 案例

**严格预注册 · evidence_collection · 禁止重建 · held-out 材料封存**

本 prospective 案例研究通常定年的**公元前 701 年第三次远征及其直接政治处置时段**中的 Joppa—Ekron—Lachish—Jerusalem 走廊。该时段不构成日级快照。时间使用明确的 BCE era/year 字段保存；天文纪年 `-700` 仅供计算。

## 可行性结论

有限审计给出：**预注册与证据收集 GO，现阶段重建 NO-GO**。审计准确记录 12 次查询、10 次正文/目录访问尝试、6 个初步来源和 1 个仅含元数据的 held-out 候选。

五个候选实体具有文本路径：Judah、Ekron、Ashdod、Gaza、Ashkelon。冻结 12 个地点候选：Joppa、Ekron、Lachish、Jerusalem、Ashdod、Gaza、Ashkelon、Bīt-Daganna/Beth-Dagon、Banayabarqa/Bene-Baraq、Azuru、Eltekeh、Timnah。目前没有任何地点成为分配 seed。

## 证据边界

亚述征服、贡赋、宗主权、军事存在、地方王朝统治、转移、毁灭与地方行政保持分层。ORACC 的平行见证属于同一条带立场的王室谱系。Lachish 毁灭是事件观察，不是控制关系。《希伯来圣经》路径在完成文本层次、成书与依赖关系审查前，不进入独立确认计数。

基线 bundle 只有 display 与 exclusion 决策。尚未取得坐标图层，也不存在 polygon、territorial surface 或重建输出。

## Prospective 封存

*The Carta Bible Atlas* 仅按书目元数据登记。*Oxford Bible Atlas* 与 *The Bible Atlas* 因搜索结果暴露封面缩略图或地图标签摘要而被排除。没有打开或保存任何历史疆域地图主体、图版、PDF 地图页、截图、OCR、矢量或派生内容。

第一次 Git freeze 绑定 9 个机器可读材料。打开任何 held-out 主体前，必须完成第二次 `reconstructed_pre_evaluation` freeze。重建 gate 若失败，案例必须以 `completed_no_reconstruction` 终止，并永久封存 atlas。

## 文件

- [可行性审计](feasibility-audit.zh-CN.md)与[英文版](feasibility-audit.md)
- [人类可读预注册](PREREGISTRATION.zh-CN.md)与[英文版](PREREGISTRATION.md)
- `preregistration.json`：冻结问题、范围、本体、预算、gate 与评价单元
- `research-bundle.json`：冻结前披露的 Source → Observation → Claim → Model Decision 状态
- `held-out-map-register.json`：仅含封存的书目元数据
- `spatial-input-contract.json`：12 个冻结地点候选及 no-input/no-polygon gate
- `preregistration-freeze.json`：SHA-256 manifest
- `lifecycle.json`：绑定预注册 commit 的 append-only 生命周期

仅验证、不重建：

```bash
historical-geo validate cases/sennacherib_701_southern_levant/public
```
