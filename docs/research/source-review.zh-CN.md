[English](source-review.md) | [简体中文](source-review.zh-CN.md)

# 历史来源审查

## 审查方法

研究型 Agent 检索目录、合法数字馆藏、出版社记录和可按页定位的版本，记录访问与权利状态，写出范围受限的释义，再判断所得 claim 能否约束求解器。只有书目信息、没有核查过的定位，达不到公开案例的证据门槛。冲突、缺失或被拒绝的材料继续保留在 lineage 中。

审查单位被严格限制在地点层级。控制陈述可以支持 locality seed；政治头衔或战役事件可以提供背景，但不能证明领土边界。Gazetteer 坐标只定位命名地点的现代近似位置，不复原中世纪聚落范围。

Round 01 按空间诊断结果选择检索目标，全程没有查阅 held-out 历史疆域图。目标选择、页码、结果和局限完整保存在 [`source-checks.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/source-checks.json)。

## 当前机器可读状态

当前 [`research-bundle.json`](../../cases/crusader_states/public/research-bundle.json) 包含 23 个来源、63 条 observation、23 条 claim、33 项 model decision 和 9 个 evidence gap。21 条 claim 为 `supported`，2 条为 `unresolved`。只统计地点类 claim 时，共有 18 条 supported 和 2 条 unresolved；后两条分别是 1130 年 Ascalon 与 Tortosa。

20 项 control-point decision 中，18 项为 `admitted`，2 项为 `experimental`。两项 experimental decision 正是 1130 年 Ascalon 与 Tortosa。9 个 evidence gap 中有 4 个已关闭、5 个仍开放。

冻结的 Round 00 [`research-bundle.snapshot.json`](../../cases/crusader_states/public/research/rounds/00-initial/research-bundle.snapshot.json) 与 [`research-scenarios.snapshot.json`](../../cases/crusader_states/public/research/rounds/00-initial/research-scenarios.snapshot.json) 可复现经过审查的 v0.1 输入。旧版 [`historical-claim-decisions.json`](../../cases/crusader_states/public/historical-claim-decisions.json) 记录该轮初始审查。Round 01 对 Cairo、Jaffa、Edessa 与 Tripoli 相关表述的更新明确记录在 [`state-changes.json`](../../cases/crusader_states/public/research/rounds/01-evidence-update/state-changes.json) 中。当前 epistemic state 以 research bundle 和 state-change record 为准。

## 主张级结果

| 地点或分组 | 当前结果 | 已核查依据与限制 | 当前求解器后果 |
|---|---|---|---|
| 1130 年 Jerusalem | supported | William of Tyre，第 XIII 卷第 28 章，第二册 pp. 45–46 在继承叙事中明确 Jerusalem 为王室居所。 | 城市点进入基线。 |
| 1130 年 Damascus | supported | Ibn al-Qalanisi/Gibb，AH 524–525，pp. 200–203 出现 Buri、Damascus、军队、城堡和宫殿。 | 政治中心点进入基线。 |
| 1130 年 Ascalon | unresolved | 已恢复的现代研究定位仍然过宽，达不到公开谱系的页级标准。 | 保持 experimental；不进入基线，只进入 `inclusive`。 |
| 1130 年 Tripoli 与 Tortosa | mixed | William of Tyre，第 XIII 卷第 26 章，第二册 pp. 40–42 支持 Tripoli 为伯国中心；已查材料仍未独立证明该切片中的 Tortosa。 | Tripoli 进入基线；Tortosa 保持 experimental，只进入 `inclusive`。 |
| 1130 年 Rafaniyya | supported | Lewis pp. 100–102、139 将伯国占有时段限定在 1126 年至 1137 年永久失守；Syriaca.org place 496 提供近似坐标。 | 新增 minor control point；不据此推断连续伯国范围。 |
| 1130 年 Antioch | supported | William of Tyre，第 XIII 卷第 27 章，第二册 pp. 43–45 记载继承危机与 Antioch 的管理。 | 城市点进入基线。 |
| 1130 年 Edessa | supported | Asbridge pp. 125–126 的论述覆盖到该节 1130 年终点；William of Tyre 第 XIV 卷第 3 章、第二册 p. 51 提供 1131 年旁证。 | 时间缺口关闭；地点继续以 minor 权重进入基线。 |
| 1187 年 Cairo | operational-locality 层级 supported | Lane-Poole p. 219 明确写到 al-Adil 从 Cairo 出发；Ibn Shaddad pp. 104–105、108 提供埃及行政和军事背景，但这些段落没有直接出现 Cairo。 | Cairo 作为 operational point 进入基线，不代表整个 Egypt。 |
| 1187 年 Damascus | political-center 层级 supported | Painter p. 45 称 Saladin 为 Egypt、Damascus 与 Aleppo 的苏丹。 | Damascus 点进入基线；头衔不定义空间范围。 |
| 1187 年 Jerusalem | supported | Ibn Shaddad 1897 年版，第 36 章 pp. 118–120 记载 1187 年 10 月 2 日投降并移交控制。 | 城市点进入基线。 |
| 1187 年 Acre、Sidon、Beirut、Ascalon 与 Gaza | supported | Ibn Shaddad 第 35 章 pp. 116–117 及相关已查 observation 支持这些地点被攻取或投降。 | 地点进入基线；不据此推断连续海岸 polygon。 |
| 1187 年 Jaffa | locality 层级 supported | Lane-Poole p. 219 记载 al-Adil 攻取 Jaffa；Kauffeldt p. 78 与 n. 225 通过 Edbury 2007 pp. 160–162 的引文转录一封同时代书信。 | Jaffa 进入基线；间接转录仍是显式限制，其单项格网影响为 0。 |
| 1187 年 Tyre | supported | Ibn Shaddad 第 35 章 p. 117、第 36–38 章 pp. 120–122 记载据守和持续到 12 月 30 日的围城。 | 年末切片保留城市点。 |
| 1187 年 Tripoli | 城市级 supported | Ibn Shaddad 第 35 章 p. 114 称 Tripoli 为 Hattin 战役后的避难地；Edbury 出版社摘要说明该城抵挡了 Saladin。 | 城市点进入基线，不推断内陆范围。 |
| 1187 年 Antioch | 城市级 supported | Edbury 出版社摘要说明 Antioch 抵挡了 Saladin。 | 城市点进入基线，周边领地不作为证据建模。 |

`Supported` 表示仓库中措辞受限的 claim 达到本项目审查门槛，不表示来源没有争议，也不表示历史学者已经接受对应的求解器 decision。

## Round 01 新增来源与核查

- Thomas S. Asbridge，*The Creation of the Principality of Antioch, 1098–1130*（2000），pp. 125–126，[Google Books 官方记录](https://books.google.com/books/about/The_Creation_of_the_Principality_of_Anti.html?id=DvUNedDOoFgC)。受版权保护，仓库只保留引用；不同地区的预览未必开放所引页面。
- Baha al-Din Ibn Shaddad，*The Life of Saladin; or, What Befell Sultan Yusuf*（1897），pp. 104–105、108，[Internet Archive 记录](https://archive.org/details/lifesaladin00condgoog)。可按页定位的公有领域版本；这些段落支持埃及背景，没有直接出现 Cairo。
- Stanley Lane-Poole，*Saladin and the Fall of the Kingdom of Jerusalem*（1898），p. 219，[公有领域扫描](https://upload.wikimedia.org/wikipedia/commons/3/3e/Saladin_and_the_fall_of_the_Kingdom_of_Jerusalem_%28IA_saladinfallofkin00lane%29.pdf)。该书为引用 Ibn al-Athir 的二手综合。
- Sebastian Fons Kauffeldt，Roskilde University 硕士论文（2019），p. 78、n. 225，[开放仓储 PDF](https://rucforsk.ruc.dk/ws/files/63773770/Speciale_Sebastian_Kauffeldt_Jerusalem_1099_1187.pdf)。同时代书信通过 Edbury 2007 间接转录；仓库只保留引用。
- Kevin James Lewis，*The Counts of Tripoli and Lebanon in the Twelfth Century*（2017），pp. 100–102、139，[数字副本](https://api.nla.am/server/api/core/bitstreams/bbc0405c-0d70-411b-ae3e-623e3457c101/content)。受版权保护，仓库只保留引用。
- Syriaca.org，*The Syriac Gazetteer*，[Rafaniyya，place 496](https://syriaca.org/place/496)。仅用于带出处的近似地点定位。

本轮访问日期为 2026-09-03。更早的版本和访问决策继续记录在 research bundle 的 source object 中。仓库不保存来源扫描、地图集页面、长篇引文或受版权保护的书籍正文。

## 当前缺口决策

| 问题 | 机器状态 | 仍需人工审查的判断 |
|---|---|---|
| 1130 年 Ascalon | open；seed 为 `experimental` | 判断可定位证据能否支持精确切片下的 Fatimid 控制。 |
| 1130 年 Tortosa | open；seed 为 `experimental` | 判断已查来源能否独立证明接近 1130 年的地点控制。 |
| 1130 年 Edessa | closed；seed 以 minor 权重 `admitted` | 接受或否定 Asbridge 的时间覆盖与相邻年份旁证。 |
| 1187 年 Cairo | closed；seed 为 `admitted` | 接受或否定由 Lane-Poole 加 Ibn Shaddad 背景形成的 operational-point 推断。 |
| 1187 年 Jaffa | closed；seed 为 `admitted` | 接受或否定二手叙述与间接转录的同时代书信形成的地点推断。 |
| 1130 年 Tripoli 内陆证据 | closed；Rafaniyya seed 以 minor 权重 `admitted` | 接受或否定占有时段解释与近似 gazetteer 位置；该点不生成伯国边界。 |
| 1187 年幸存拉丁据点范围 | open | 在 Tyre、Tripoli 与 Antioch 周边识别更多年末地点、路线或明确排除。 |
| 两个切片的 reach 假设 | 两个开放 model gap | 诊断或替换当前 backend 假设；单靠来源检索无法关闭。 |

## 地理空间来源核验

陆地和自然要素来自 Natural Earth 1:10m physical vectors 5.1.2。近似地点坐标均引用相应 gazetteer；GeoNames 数据按 CC BY 4.0 署名，新加入的 Rafaniyya 点直接引用 Syriaca.org。Natural Earth 输入的下载地址和 SHA-256 记录在 [`natural-earth-source-check.json`](../../cases/crusader_states/public/natural-earth-source-check.json)。

## 人工审查边界

机器记录可以复现每项输入为何纳入、保持 experimental 或被排除。学术接受仍由人完成。Cairo、Jaffa、Edessa 与 Rafaniyya 的 gap 关闭，只表示项目预先声明的 success criteria 已满足，不会把这些 decision 转化为定论；任何 locality claim 都不能单独授权一条被“恢复”的历史领土边界。
