[English](comparative-evaluation.md) | [简体中文](comparative-evaluation.zh-CN.md)

# 外部地图比较

## 目的

这次比较只回答一个问题：reviewed-baseline 与已出版人工地图在哪些地方一致、缺项或分歧。参考地图是外部解释，不是 ground truth；下文计数也不是历史准确率。

公开仓库不保存地图集扫描页，也不保存沿参考图描出的边界。`reference-map-register.json` 记录书目信息、权利、既往使用、时间匹配和人工摘录的分类观察；`reference-comparison.png` 是本项目原创汇总图。

## 参考地图登记

本轮审查了四项材料。

- Andrew D. Buck，*The Principality of Antioch and its Frontiers in the Twelfth Century*（Boydell Press，2017），Map 2 “Northern Syria and Cilicia, 1130”，p. 23。这是找到的唯一覆盖部分 1130 切片、年份完全一致的学术地图。出版社合法预览只显示图名和页码，没有开放地图正文，因此未提取分类断言或几何。
- William R. Shepherd，*Historical Atlas*（1926 年版），“Asia Minor and the States of the Crusaders in Syria, about 1140”，p. 68。该图属于公有领域，覆盖区域格局，但比目标年份晚十年。
- Shepherd，*Historical Atlas*（1911），“Europe and the Mediterranean Lands about 1190”，pp. 70–71。该图属于公有领域，适合检查实体是否仍被表达；比例尺过小、年代偏晚，不适合评价 1187 年末的城市和边界。
- W. & A. K. Johnston / Reginald Lane Poole，“Syria Showing Saladin’s Conquests 1187–1190”，收录于 *Historical Atlas of Modern Europe*（1902）。这幅公有领域战役图区分 1187、1188、较晚失守的堡垒和 1192 年基督教边界。

## 独立性与权利

Shepherd 与 Johnston 属于不同制图谱系。两者都曾在公开项目组装前的只读审计中登记，因此这次比较不是盲评。此前审计没有从地图生成种子、多边形、模型参数或历史主张，故可作为无参数循环的外部比较材料。

Buck 的 1130 地图与当前证据集部分独立，但 Buck 同时也是文字来源。出版社合法预览无法访问受版权保护的地图正文。register 直接记录这一权利与访问阻碍，没有从非授权副本恢复页面。

## 比较前统一规则

日期按原样保留。1130 模型与约 1140 年地图只能作邻近年份比较；1187 年末与约 1190 年地图、1187—1190 战役序列比较时，也没有把第三次十字军期间的后续状态倒推回 1187 年末。

实体只在等价关系明确时统一名称，例如将 “Empire of Saladin” 对应为 “Ayyubid Sultanate”。城市控制、实体存在、邻接和海岸地点顺序分别记录。概化填色、荒漠边缘和战役分期色块没有被转换为边界线。

## 分类比较结果

### 1130 年

Shepherd 地图表达了 17 项可比较的城市、实体和邻接断言，其中 12 项与 reviewed-baseline 一致。5 项参考资料独有内容包括：保留 Fatimid Egypt、阿斯卡隆与托尔托萨两个城市点，以及两项涉及已移除 Fatimid 表面或 Jerusalem–Tripoli 接触关系的邻接。

分歧位置很明确。耶路撒冷、大马士革、的黎波里、安条克和埃德萨构成共同核心；阿斯卡隆与托尔托萨只进入 inclusive 情景，可以查看它们的模型影响而不污染基线。由于约 1140 年填色存在时间错位和明显概化，本轮没有计算线距离或重叠率。

### 1187 年末

约 1190 年 Shepherd 地图表达 4 项可比较的实体存在断言，reviewed-baseline 全部保留。Johnston 战役图表达 14 项可比较的城市与实体断言，其中 13 项一致。唯一的参考资料独有城市是 Jaffa：Johnston 把它放入 1187 年征服序列，现有文字页级审查仍无法支持海岸分组中的 Jaffa 成员。

这项分歧表示证据张力，不是模型错误分数。Jaffa 不进入基线，只进入 inclusive 情景。提尔、的黎波里、安条克和阿尤布王朝的大尺度格局，是多图之间较稳定的共同点。

## 解释边界

register 只记录地图明确表达的内容和沉默处，不推断未绘出的边界，不把旧地图集填色当作直接观察，也不把多图平均成所谓共识边界。比较发生在基线证据决策之后，没有据此调整任何模型参数。

## 人工审查边界

仍需历史学者判断：用 1140 年地图比较 1130 年是否可接受，Johnston 的战役分类能否支持 Jaffa 点级解释，以及能否在合法访问条件下审查 Buck 的精确年份地图。这些问题会影响学术接受，当前代码无法自行裁决。
