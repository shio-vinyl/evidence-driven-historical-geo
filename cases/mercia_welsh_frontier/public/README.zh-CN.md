[English](README.md) | [简体中文](README.zh-CN.md)

# Mercia–Welsh 边疆 prospective 案例

**阶段：completed_no_reconstruction · 重建门槛未通过 · held-out 材料继续封存**

该严格 prospective 案例覆盖 Rhuddlan—Dee/Llangollen—Chirk—Oswestry/Llanymynech—upper Severn 走廊的 **780-01-01 至 796-07-29**。区间以 Offa 去世为终点；只有年份的材料不会被解释为精确到日。

## 最终裁决

登记结果为 **`completed_no_reconstruction`**。冻结后的非地图检索没有为任何 modeled entity 找到两条相互独立、合法可访问、适用于目标区间的具名地点控制关系。九世纪的 Pillar of Eliseg 材料无法证明 Powys 在目标区间的连续性；798 年王号记录无法把 Gwynedd 接到 796 年 Rhuddlan 事件；Mercia 的王号、居住活动、战役与工程位置也无法证明连续的本地控制。

案例没有生成 polygon、territorial surface 或 reconstruction。Offa's Dyke 与 Wat's Dyke 继续排除出 allocation：宽泛或冲突的年代不能确定目标区间角色，工程位置也不能代替政治边界证据。

## 已审核证据轮次

`research/rounds/01-non-map-evidence/`记录了 23 条精确查询、17 次内容或馆藏记录检查和 7 项采纳来源。每项来源检查都保存查询、访问日期、URL、稳定 locator、内容访问范围、权利状态、原子 observation、采纳或拒绝理由、来源谱系与对应 gap。访问失败与被拒绝的转述来源仍保留在账本中。

六项 gap 的终态如下：

- `GAP_LOCAL_MERCIA_CONTROL`：**closed_unresolved**；没有发现合格的走廊地点控制关系。
- `GAP_POWYS_CONTINUITY`：**closed_unresolved**；可定位材料属于九世纪并具有回溯性。
- `GAP_GWYNEDD_CONTINUITY`：**closed_excluded**；798 年记录不能与 796 年事件合并。
- `GAP_RHUDDLAN_PARTIES`：**closed_unresolved**；参战方、结果、领土后果与确切战场位置均无充分支持。
- `GAP_DYKE_DATE_AND_ROLE`：**closed_excluded**；没有工程段同时满足年代与独立历史角色要求。
- `GAP_WATS_DYKE_RELATION`：**closed_excluded**；年代相互冲突或越出区间，功能仍未解决。

Gate 保留 12 个 distinct spatial candidates、至少三条独立来源谱系，以及明确的反证或排除。两项决定性标准未通过：至少两个 modeled entities，以及每个实体至少两条独立的区间地点关系。

## Append-only 生命周期

`lifecycle.json`把 commit `94f8ee75662bf909f34796040d917a347e228662` 的不可变预注册基线连接到已审核轮次清单。当前有效状态由该基线加审核后的增量推导。Validator 检查轮次哈希链、精确文件集合、source/observation/claim/decision 引用、预算算术、合法阶段迁移、有效 gap 状态、held-out 标识符隔离以及原九项冻结哈希。

## Prospective 封存

Held-out 登记表继续只保存书目元数据。没有查看或保存任何登记地图的主体、缩略图、PDF 页面、截图、OCR、矢量或边界几何。重建 gate 已失败，因此本案例没有第二次 pre-evaluation freeze，评估也不会打开。

自动验证只能审计仓库状态与记录声明，不能证明个人完整浏览历史。

## 文件

- [人类可读预注册](PREREGISTRATION.zh-CN.md)与[英文版](PREREGISTRATION.md)
- [可行性审计](feasibility-audit.zh-CN.md)与[英文版](feasibility-audit.md)
- `preregistration.json` 与 `preregistration-freeze.json`：不可变协议和九项材料 SHA-256 清单
- `research-bundle.json`：不可变的冻结前认知基线
- `lifecycle.json`：append-only 轮次链与有效终态
- `research/rounds/01-non-map-evidence/`：查询、来源、observation、claim、decision、gap、预算与 gate 增量
- `held-out-map-register.json`：只含封存的书目元数据

不执行重建的验证命令：

```bash
historical-geo validate cases/mercia_welsh_frontier/public
```
