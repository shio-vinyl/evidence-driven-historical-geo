[English](README.md) | [简体中文](README.zh-CN.md)

# Mercia–Welsh 边疆 prospective 案例

**阶段：evidence collection · 有条件 GO · 禁止重建**

这是项目的第二个案例，也是首个严格 prospective held-out 检验。空间范围为 Rhuddlan—Dee/Llangollen—Chirk—Oswestry/Llanymynech—upper Severn 北中部走廊，时间范围为 **780-01-01 至 796-07-29**。区间以 Offa 去世为终点；只有年份的材料不会被解释为精确到日。

## 当前判断

可行性审计支持对预注册与证据收集作出有条件 **GO**。Mercia 在区间内有直接材料；Powys 与 Gwynedd 是可研究的具名候选，但区间内的本地控制关系仍未解决。因此该案例目前未达到重建门槛，也不包含领土 polygon。

已定位 12 个具名事件、路线、工程段、地形、年代反证或排除候选。它们的存在不使其自动成为控制点。Offa’s Dyke 尤其不得等同于政治边界：当前从 allocation 中排除；未来也只能在角色获得独立证据后进入单列的敏感性情景。

## Prospective 封存

Held-out 登记表只保存书目元数据。没有查看或保存任何登记地图的主体、缩略图、PDF 页面、截图、OCR、矢量或边界几何。首选比较对象在评估前固定。首次打开地图主体前，必须再以一个 `reconstructed_pre_evaluation` Git commit 冻结证据、情景、代码、校准、输出、固定坐标、评价规则与哈希。

自动验证会检查 metadata-only 标志，阻止 held-out ID 进入研究材料，拒绝地图主体文件与提前生成的重建输出，并核验预注册材料哈希。这些检查只能审计仓库状态与记录声明，不能证明个人完整浏览历史。

## 文件

- [人类可读预注册](PREREGISTRATION.zh-CN.md)与[英文版](PREREGISTRATION.md)
- [可行性审计](feasibility-audit.zh-CN.md)与[英文版](feasibility-audit.md)
- `preregistration.json`：冻结的机器可读协议
- `feasibility-audit.json`：机器可读 GO 判断与约束
- `research-bundle.json`：冻结前已披露的来源、观察、主张、决策与缺口
- `evidence-gap-register.json`：指向 bundle 权威记录的精简索引
- `held-out-map-register.json`：仅含封存的书目元数据
- `source-access-rights.json`：访问、定位与权利记录
- `research-scenarios.json`：无 allocation 基线及未来激活条件
- `spatial-input-contract.json`：允许的空间输入与禁止 polygon 的门槛
- `preregistration-freeze.json`：冻结材料的 SHA-256 清单

不执行重建的验证命令：

```bash
historical-geo validate cases/mercia_welsh_frontier/public
```
