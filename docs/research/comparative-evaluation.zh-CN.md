[English](comparative-evaluation.md) | [简体中文](comparative-evaluation.zh-CN.md)

# 外部地图比较

## 范围与评估状态

登记的人工历史地图只用于评估，它们不构成 ground truth；下文分类计数也不代表历史准确率。仓库不保存地图集扫描页或沿参考图描出的边界。[`reference-map-register.json`](../../cases/crusader_states/public/reference-map-register.json) 记录书目信息、权利、时间匹配与人工摘录的分类观察；[`reference-comparison.png`](../../cases/crusader_states/public/figures/reference-comparison.png) 是项目原创汇总图。

当前入库的图件及配套 JSON 属于**通过 v0.1 兼容路径生成的冻结 Round-00 评估**，描述第一轮定向取证之前的 reviewed baseline。Round 01 搜索证据时没有查阅历史疆域地图；[`source-checks.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/source-checks.json) 明确记录了这一限制。项目没有声称得到 Round-01 的新版 held-out 比较计数。

## 登记的参考资料

冻结比较审查了四项资料。

- Andrew D. Buck，*The Principality of Antioch and its Frontiers in the Twelfth Century*（Boydell Press，2017），Map 2 “Northern Syria and Cilicia, 1130”，p. 23。出版社合法预览只确认图名与页码，没有开放地图正文，因此未提取断言或几何。
- William R. Shepherd，*Historical Atlas*（1926 年版），“Asia Minor and the States of the Crusaders in Syria, about 1140”，p. 68。该公有领域图覆盖区域格局，时间比目标切片晚十年。
- Shepherd，*Historical Atlas*（1911），“Europe and the Mediterranean Lands about 1190”，pp. 70–71。该公有领域图可用于区域尺度的实体存在检查，比例尺和年代均不支持 1187 年末边界评价。
- W. & A. K. Johnston / Reginald Lane Poole，“Syria Showing Saladin’s Conquests 1187–1190”，收录于 *Historical Atlas of Modern Europe*（1902）。该公有领域战役图区分 1187、1188、较晚失守的堡垒与 1192 年基督教边界。

Shepherd 与 Johnston 属于不同制图谱系。两者在公开项目组装前已被只读登记，因此比较并非盲评；该审计没有产生 seed、polygon、模型参数或历史 claim。Buck 同时出现在文字来源中，但无法访问的地图正文没有贡献任何提取断言。

## Round-00 分类结果

日期保持原样。1130 重建只把约 1140 年地图当作邻近年份代理；1187 年末与约 1190 年地图及 1187—1190 战役序列比较时，没有把第三次十字军期间的后续状态倒推回目标切片。城市控制、实体存在、邻接和海岸地点顺序分别记录；概化填色与战役分期颜色没有被转换为边界线。

**1130 年**的 Shepherd 图表达 17 项可比较的城市、实体与邻接断言，其中 12 项匹配 Round-00 reviewed baseline。5 项参考资料独有内容包括 Fatimid Egypt、Ascalon 与 Tortosa，以及两项涉及缺失 Fatimid 表面或 Jerusalem–Tripoli 接触关系的邻接。代理图存在时间错位与明显概化，因此没有计算线距离或重叠率。

**1187 年末**的约 1190 年 Shepherd 图表达 4 项可比较实体存在断言，全部匹配 Round-00 基线。Johnston 战役图表达 14 项可比较城市与实体断言，其中 13 项匹配，Jaffa 是唯一 reference-only 项。Round 00 当时已核查的文字材料尚不足以让 Jaffa 成为准入的点控制输入。

## Round-01 状态

Round 01 改变了冻结比较的适用范围。文字核查关闭 Jaffa 缺口，并准入 `D_1187_JAFFA_SEED`；它的单项空间效应仍为零格网。Cairo 同期获准进入基线并解释全部 1,162 个变化格网，Jaffa 没有贡献变化格网。因此，旧的“13/14，Jaffa 为 reference-only”只是一项 Round-00 历史结果，不能作为当前性能数字。

1130 基线新增 Rafaniyya；登记的参考断言未涉及该地点，且其加入改变零格网。“12/17”没有被重新计算，也没有被提升为 Round-01 分数。当前证据与空间状态应以 [`round-delta.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/round-delta.json) 和 Round-01 diagnosis 文件为准。

## 解释边界

register 只记录参考资料明确表达的内容与沉默处，不推断未绘出的边界，不把旧地图集填色转成直接观察，也不把多图平均成共识边界。冻结比较没有驱动模型调参。历史学者仍需判断 1140 代理对 1130 是否可接受、Johnston 战役分类应如何解释，以及能否合法查阅 Buck 的精确年份地图。
