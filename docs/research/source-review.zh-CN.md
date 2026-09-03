[English](source-review.md) | [简体中文](source-review.zh-CN.md)

# 历史来源审查

## 审查方法

本案例面向研究型 Agent。Agent 检索目录、合法数字馆藏、出版社页面和可按页定位的版本，记录访问与权利状态，写出范围受限的释义，再决定该记录能否进入求解器。只有书目引用仍然不够；冲突或缺失必须继续留在谱系和情景登记中。

审查单位也受到限制。城市控制陈述可以支持地点种子；政治头衔可以识别政治中心，却不能证明每个城市或整片领土；事件与路线只作为观察记录。上述记录均不能单独证明领土边界。

仓库不保存来源扫描、地图集页面、长篇引文或受版权保护的书籍正文。

## 状态定义

- **已核实**：可访问页面或出版社记录直接支持现有的地点级释义。
- **部分核实**：记录只支持分组主张的一部分、相邻日期或较弱的政治角色。
- **未解决**：关键定位仍然过宽，或已查页面没有出现相关地点。

`KEEP`、`DOWNGRADE`、`REMOVE` 和 `DISPUTED` 是输入决策，不是另一套证据状态。完整决策见机器可读文件 [`historical-claim-decisions.json`](../../cases/crusader_states/public/historical-claim-decisions.json)。

## 主张级结果

| 恢复主张 | 审查结果 | 页级证据与限度 | 输入后果 |
|---|---|---|---|
| `CSB1130_001` 耶路撒冷 | 已核实 | William of Tyre，第 XIII 卷第 28 章，第二册 pp. 45–46 在继承叙事中明确耶路撒冷为王室居所。 | 保留城市点。 |
| `CSB1130_004` 大马士革 | 已核实 | Ibn al-Qalanisi/Gibb，AH 524–525，pp. 200–203 明确出现 Buri、大马士革、军队、城堡和宫殿。 | 保留政治中心点。 |
| `CSB1130_005` 阿斯卡隆 | 未解决 | 恢复出的现代研究定位仍然过宽，达不到公开谱系的页级标准。 | `DISPUTED`；基线省略，只进入 `inclusive`。 |
| `CSB1130_006` 的黎波里/托尔托萨 | 部分核实 | William of Tyre，第 XIII 卷第 26 章，第二册 pp. 40–42 称 Pons 为的黎波里伯爵；已查页面没有独立证明托尔托萨或连续的伯国范围。 | `DOWNGRADE`；保留的黎波里，托尔托萨延后至 `inclusive`。 |
| `CSB1130_008` 安条克 | 已核实 | William of Tyre，第 XIII 卷第 27 章，第二册 pp. 43–45 记载继承危机与安条克的管理。 | 保留城市点。 |
| `CSB1130_010` 埃德萨 | 部分核实 | William of Tyre，第 XIV 卷第 3 章，第二册 p. 51 在相邻的 1131 年叙事中称 Joscelin 为埃德萨伯爵。 | `DOWNGRADE`；降为 minor 权重，且不据此推断边界。 |
| `CSB1187_001` 开罗/大马士革 | 部分核实 | Painter，p. 45 称 Saladin 为埃及、大马士革和阿勒颇的苏丹。页面出现大马士革，没有出现开罗；头衔也不定义领土。 | `DOWNGRADE`；保留大马士革，开罗延后至 `inclusive`。 |
| `CSB1187_003` 耶路撒冷 | 已核实 | Ibn Shaddad，1897 年版，第 36 章 pp. 118–120 记载 1187 年 10 月 2 日投降并移交控制。 | 保留城市点。 |
| `CSB1187_004` 被占海岸城市 | 部分核实 | Ibn Shaddad，第 35 章 pp. 116–117 支持阿卡、西顿、贝鲁特、阿斯卡隆和加沙；已查页面没有 Jaffa。 | 保留有支持的城市；Jaffa 标为 `DISPUTED`，延后至 `inclusive`。 |
| `CSB1187_005` 提尔 | 已核实 | Ibn Shaddad，第 35 章 p. 117、第 36–38 章 pp. 120–122 记载据守以及持续到 12 月 30 日的围城。 | 年末切片保留城市点。 |
| `CSB1187_007` 的黎波里 | 城市级已核实 | Ibn Shaddad，第 35 章 p. 114 称的黎波里为哈丁战役后的避难地；Edbury 的出版社摘要说明的黎波里抵挡了 Saladin。 | `KEEP` 城市点，不推断伯国内陆界限。 |
| `CSB1187_008` 安条克 | 城市级已核实 | Edbury 的出版社摘要说明安条克抵挡了 Saladin。 | `KEEP` 城市点，周边领地仍未解决。 |

补充审查后，十二组主张为 **7 组已核实、4 组部分核实、1 组未解决**。这个计数描述证据状态，不会取代下列七项输入决策。

## 承重证据决策

| 缺口 | 决策 | 基线处理 |
|---|---|---|
| 1187 年 captured-coast 分组中的 Jaffa | `DISPUTED` | 省略，只进入 `inclusive`。 |
| 1130 年阿斯卡隆 | `DISPUTED` | 连同 Fatimid 实体从基线省略，只进入 `inclusive`。 |
| 1187 年开罗/大马士革 | `DOWNGRADE` | 大马士革作为明确政治中心保留，开罗延后。 |
| 1187 年末安条克 | `KEEP` | 保留城市点。 |
| 使用相邻 1131 年材料的埃德萨 | `DOWNGRADE` | 保留地点，降为 minor 权重。 |
| 1130 年的黎波里/托尔托萨 | `DOWNGRADE` | 保留的黎波里，托尔托萨延后。 |
| 1187 年末的黎波里 | `KEEP` | 保留城市点。 |

求解器默认值没有替任何缺口作出历史判断。本轮也没有需要 `REMOVE` 的项目：缺乏支持的部分本来就能拆成独立种子，可以延后并保留审计轨迹。

## 版本与访问记录

- William of Tyre，*A History of Deeds Done Beyond the Sea*，Babcock/Krey 译本（1943），[Internet Archive：`williamoftyrehistory`](https://archive.org/details/williamoftyrehistory)，按页查阅；仓库只保留引用。
- Ibn al-Qalanisi，*The Damascus Chronicle of the Crusades*，Gibb 译本（1932），[Internet Archive：`the-damascus-chronicle-of-the-crusades`](https://archive.org/details/the-damascus-chronicle-of-the-crusades)；托管记录带 Public Domain Mark。
- Baha al-Din Ibn Shaddad，*The Life of Saladin; or, What Befell Sultan Yusuf*（1897），[Internet Archive：`libraryofpalesti13paleuoft`](https://archive.org/details/libraryofpalesti13paleuoft)，作为可按页定位的公有领域版本使用。
- Sidney Painter，“The Third Crusade”，载 *A History of the Crusades* 第二册（1962），p. 45，[JSTOR 开放书目记录](https://www.jstor.org/stable/j.ctv4s7mwv)；受版权保护，仓库只保留引用。
- Peter W. Edbury，“The Crusader States”，载 *The New Cambridge Medieval History* 第五册（1999），pp. 590–606，[Cambridge 出版社记录](https://www.cambridge.org/core/books/abs/new-cambridge-medieval-history/crusader-states/35E282BC04D01A0074105E8B1051F233)；核查出版社摘要，受版权保护，仓库只保留引用。
- Internet Archive 项目 `the-chronicle-of-ibn-al-athir-big-file` 被拒绝：上传者、版本元数据和权利状态不足以形成公开审计链。

本轮访问日期为 2026-09-01。参考地图的访问与权利记录另见 [`reference-map-register.json`](../../cases/crusader_states/public/reference-map-register.json)。

## 地理空间来源核验

陆地和自然要素来自 Natural Earth 1:10m physical vectors 5.1.2。与全新官方下载文件比较后，4,133 个海岸线要素的标准化几何多重集和约旦河 `NE_ID 1159114369` 均精确一致。黎巴嫩山 `NE_ID 1730071649` 与托罗斯山脉 `NE_ID 1159103077` 在 Polygon 提升为 MultiPolygon 后拓扑一致，对称差为零。

下载地址和 SHA-256 见 [`natural-earth-source-check.json`](../../cases/crusader_states/public/natural-earth-source-check.json)。近似地点坐标以 `geonameId` 引用 GeoNames，并遵循 CC BY 4.0。

## 人工审查边界

机器可读决策可以复现，其学术接受仍需人工完成。历史学者需要判断 1130 年阿斯卡隆与托尔托萨的状态、1131 年埃德萨材料能否桥接一年、年末口径下的 Jaffa、Painter 的政治头衔是否足以支持大马士革种子，以及幸存城市的黎波里和安条克能在多大程度上代表周边政体。当前项目只回答受限的地点级建模问题。
